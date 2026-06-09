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
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## 3. Exploitation
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

