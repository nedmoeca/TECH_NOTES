---
link: https://app.hackthebox.com/machines/Nimbus
description: Hard·Linux
release date:
tags:
  - SN_11
image: https://cdn.services-k8s.prod.aws.htb.systems/content/machines/avatar/a1e513f0-690d-4dc2-bd2c-946d3983d026-1780052541.png
solved:
solve date: 2026-06-20
machine no.: 5
---

<div style="text-align: center; padding: 80px 40px; page-break-after: always;">

  <img src="/ASSETS/HTB Logo.png" style="width: 1220px; margin-bottom: 60px;" />

  <div><p style="font-size: 40px; font-weight: 600; margin-bottom: 40px;">Nimbus Writeup</p></div>

  <img src="https://cdn.services-k8s.prod.aws.htb.systems/content/machines/avatar/a1e513f0-690d-4dc2-bd2c-946d3983d026-1780052541.png" style="width: 400px; margin-bottom: 60px;" />

  <div style="font-size: 18px; line-height: 2.2;">
    <p style="margin: 0;">Prepared by: nedmoeca</p>
    <p style="margin: 0;">Author(s): dotguy & TheCyberGeek</p>
    <p style="margin: 0;">Difficulty: Hard</p>
    <p style="margin: 0;">Date: 20th June, 2026</p>
  </div>

</div>
<!-- PAGE BREAK -->

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
┌──(kali㉿kali)-[~]
└─$ ping -c 4 10.129.40.68
PING 10.129.40.68 (10.129.40.68) 56(84) bytes of data.
64 bytes from 10.129.40.68: icmp_seq=1 ttl=63 time=222 ms
64 bytes from 10.129.40.68: icmp_seq=2 ttl=63 time=220 ms
64 bytes from 10.129.40.68: icmp_seq=3 ttl=63 time=219 ms
64 bytes from 10.129.40.68: icmp_seq=4 ttl=63 time=221 ms

--- 10.129.40.68 ping statistics ---
4 packets transmitted, 4 received, 0% packet loss, time 3007ms
rtt min/avg/max/mdev = 218.570/220.330/221.677/1.187 ms
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

#### 2.1.1 Full Port Sweep

Begin enumeration by discovering every open port on the target. Run a fast scan across all 65,535 ports to build a complete picture of the attack surface before committing to deeper inspection.

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
└─$ nmap -p- --min-rate 5000 -Pn 10.129.40.68 
Starting Nmap 7.98 ( https://nmap.org ) at 2026-06-27 09:36 +0000
Warning: 10.129.40.68 giving up on port because retransmission cap hit (10).
Nmap scan report for 10.129.40.68
Host is up (0.36s latency).
Not shown: 61988 closed tcp ports (reset), 3545 filtered tcp ports (no-response)
PORT   STATE SERVICE
22/tcp open  ssh
80/tcp open  http

Nmap done: 1 IP address (1 host up) scanned in 63.74 seconds
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
└─$ nmap -A -p 22,80 10.129.40.68            
Starting Nmap 7.98 ( https://nmap.org ) at 2026-06-27 09:37 +0000
Nmap scan report for 10.129.40.68
Host is up (0.22s latency).

PORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH 9.6p1 Ubuntu 3ubuntu13.16 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   256 eb:ab:8f:be:99:02:0b:3e:c4:1c:83:b2:66:2f:17:13 (ECDSA)
|_  256 c1:69:ab:84:f3:88:8b:b3:8a:ae:e2:28:35:54:35:0b (ED25519)
80/tcp open  http    nginx 1.24.0 (Ubuntu)
|_http-title: Did not follow redirect to http://nimbus.htb/
|_http-server-header: nginx/1.24.0 (Ubuntu)
Warning: OSScan results may be unreliable because we could not find at least 1 open and 1 closed port
Device type: general purpose|router
Running: Linux 4.X|5.X, MikroTik RouterOS 7.X
OS CPE: cpe:/o:linux:linux_kernel:4 cpe:/o:linux:linux_kernel:5 cpe:/o:mikrotik:routeros:7 cpe:/o:linux:linux_kernel:5.6.3
OS details: Linux 4.15 - 5.19, MikroTik RouterOS 7.2 - 7.5 (Linux 5.6.3)
Network Distance: 2 hops
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel

TRACEROUTE (using port 80/tcp)
HOP RTT       ADDRESS
1   258.61 ms 10.10.14.1
2   218.68 ms 10.129.40.68

OS and Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 24.99 seconds
```
<div align="center">
<br>
<br>
</div>

#### 2.1.3 Scan Results Analysis

| Port | **Service** | **Version**                       | **Analysis**                                                                                                                                                                                                                                                                                                                                                                                               |
| ---- | ----------- | --------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 22   | ssh         | OpenSSH 9.6p1 Ubuntu 3ubuntu13.16 | Standard SSH. Unlikely to be the initial entry point without valid credentials — no anonymous auth, no known unauthenticated RCE for this version. Worth revisiting later only if creds/keys are found during the web-app phase.                                                                                                                                                                           |
| 80   | http        | nginx 1.24.0 (Ubuntu)             | Primary attack surface. The scan shows nginx issuing a redirect to `http://nimbus.htb/`, confirming **name-based virtual hosting** — the server only renders the correct site when the `Host` header matches a configured vhost. This means `/etc/hosts` must be updated to map `nimbus.htb` (and likely other subdomains) to the target IP before any further enumeration will return meaningful content. |
With only two ports open and SSH requiring credentials we don't have, the entire compromise path runs through the nginx-hosted web application at `nimbus.htb`. The redirect behavior is the first concrete clue that vhost-based routing is in play.
<div align="center">
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
</div>

### 2.2 Web Service Enumeration

#### 2.2.1 Update Hosts File

With virtual hosting confirmed, mapping `nimbus.htb` to the target IP and re-requesting the web root revealed the actual application: **Nimbus**, an internal job scheduler built by "Nimbus Labs Engineering" (v1.4.2). The page exposes three navigation points worth tracking — `/jobs` (job submission), `/login` (authentication), and `/api/v1/health` (a healthcheck endpoint, often a goldmine for fingerprinting backend services).

Two panels are particularly significant from an attacker's perspective. First, the "How do I submit a job?" panel states that jobs are submitted by pointing the job submitter at a **raw URL** — any feature that fetches a user-supplied URL server-side is a textbook **SSRF (Server-Side Request Forgery)** candidate, since the server itself becomes a proxy for our requests into its internal network. Second, the "Need shell access" panel confirms SSH access requires manual key approval from a DevOps lead ("marcus"), ruling out SSH as a direct, unauthenticated entry point and reinforcing that the web app is the only viable attack surface.

**Command:** `echo "10.129.40.68 nimbus.htb" | sudo tee -a /etc/hosts`  
**Breakdown:**

- **`echo "10.129.40.68 nimbus.htb"`**
    - **Description:** Prints a string mapping the target IP to the hostname `nimbus.htb`.
    - **Purpose:** Nginx routes by Host header (vhost), so without this local DNS override, requests to `nimbus.htb` would never resolve to the target.
- **`sudo tee -a /etc/hosts`**
    - **Description:** `tee` writes input to a file while also passing it through to stdout; `-a` appends rather than overwrites; `sudo` is required since `/etc/hosts` is owned by root.
    - **Purpose:** Persists the hostname mapping system-wide so any tool (curl, browser, nmap) resolves `nimbus.htb` correctly going forward.
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

