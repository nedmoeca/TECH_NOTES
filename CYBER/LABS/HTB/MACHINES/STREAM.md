---
tags:
  - HTB
  - MACHINE
link: https://app.hackthebox.com/machines/Stream
difficulty: Medium
os: Linux
pov: red
description:
image: https://cdn.services-k8s.prod.aws.htb.systems/content/machines/avatar/a2cc2e41-9160-4e35-9d3f-8eb1e98cdf77-1789978330.png
solved:
solve date:
machine no.: 3
release date: 2026-10-10
---

<div style="text-align: center; padding: 80px 40px; page-break-after: always;">

  <img src="/ASSETS/writeup_hack_the_box_logo.png" style="width: 1220px; margin-bottom: 60px;" />

  <div><p style="font-size: 40px; font-weight: 600; margin-bottom: 40px;">Stream Writeup</p></div>

  <img src="https://cdn.services-k8s.prod.aws.htb.systems/content/machines/avatar/a2cc2e41-9160-4e35-9d3f-8eb1e98cdf77-1789978330.png" style="width: 400px; margin-bottom: 60px;" />

  <div style="font-size: 22px; line-height: 2.2;">
    <p style="margin: 0;">Prepared by: <a href="https://app.hackthebox.com/users/1809572">nedmoeca</a></p>
    <p style="margin: 0;">Created by: <a href="https://app.hackthebox.com/users/260996">7u9y</a></p>
    <p style="margin: 0;">Difficulty: Easy</p>
    <p style="margin: 0;">Date: DD Month Year</p>
  </div>

</div>
<!-- PAGE BREAK -->

## Debrief


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
64 bytes from TARGET_IP: icmp_seq=1 ttl=63 time=242 ms
64 bytes from TARGET_IP: icmp_seq=2 ttl=63 time=229 ms
64 bytes from TARGET_IP: icmp_seq=3 ttl=63 time=578 ms
64 bytes from TARGET_IP: icmp_seq=4 ttl=63 time=295 ms

--- TARGET_IP ping statistics ---
4 packets transmitted, 4 received, 0% packet loss
rtt min/avg/max/mdev = 229.009/335.850/577.967/141.961 ms
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
PORT      STATE SERVICE
22/tcp    open  ssh
80/tcp    open  http
8081/tcp  open  blackice-icecap
40899/tcp open  unknown
```
<div align="center">
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
</div>

#### 1.4.2 Fingerprint the open services

**Command:** `nmap -A -p p1,p2,p3,p4 TARGET_IP`

**Breakdown:**

| Component             | Purpose         | Simple Explanation                                                                                                                                                     |
| --------------------- | --------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `nmap`                | Port scanner    | Reconnects to the given ports, this time to interrogate each service rather than just confirm it’s open.                                                               |
| `-A`                  | Aggressive scan | Bundles four things at once: service/version detection, default NSE scripts, OS fingerprinting, and traceroute. Turns “port 8081 is open” into “Uvicorn serving JSON.” |
| `-p 22,80,8081,40899` | Port list       | Restricts the scan to the ports the full sweep already found open, so the slow `-A` probes run against four ports instead of all 65535.                                |


**Result:**

```shell
Starting Nmap 7.99 ( https://nmap.org ) at 2026-10-17 09:27 -0400
Nmap scan report for TARGET_IP
Host is up (0.28s latency).

PORT      STATE SERVICE    VERSION
22/tcp    open  ssh        OpenSSH 9.6p1 Ubuntu 3ubuntu13.19 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   256 0c:4b:d2:76:ab:10:06:92:05:dc:f7:55:94:7f:18:df (ECDSA)
|_  256 2d:6d:4a:4c:ee:2e:11:b6:c8:90:e6:83:e9:df:38:b0 (ED25519)
80/tcp    open  http       nginx 1.24.0 (Ubuntu)
|_http-server-header: nginx/1.24.0 (Ubuntu)
|_http-title: Did not follow redirect to http://api.htb-airport.htb/
8081/tcp  open  http       Uvicorn
|_http-title: Site doesn't have a title (application/json).
|_http-server-header: uvicorn
40899/tcp open  tcpwrapped
Warning: OSScan results may be unreliable because we could not find at least 1 open and 1 closed port
Device type: general purpose|router
Running: Linux 4.X|5.X, MikroTik RouterOS 7.X
OS CPE: cpe:/o:linux:linux_kernel:4 cpe:/o:linux:linux_kernel:5 cpe:/o:mikrotik:routeros:7 cpe:/o:linux:linux_kernel:5.6.3
OS details: Linux 4.15 - 5.19, MikroTik RouterOS 7.2 - 7.5 (Linux 5.6.3)
Network Distance: 2 hops
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel

TRACEROUTE (using port 443/tcp)
HOP RTT       ADDRESS
1   230.30 ms 10.10.14.1
2   230.05 ms TARGET_IP

OS and Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 21.96 seconds
```
<div align="center">
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
</div>

#### 1.4.3 Scan Results Analysis

| Port      | Service    | Version                           | Analysis                                                                                                                                                                                                       | Simple Explanation                                                                                                                                                           |
| --------- | ---------- | --------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 22/tcp    | SSH        | OpenSSH 9.6p1 Ubuntu 3ubuntu13.19 | Current, fully patched OpenSSH. No pre-auth attack surface here; it only becomes useful once credentials turn up elsewhere in the chain. Park it.                                                              | The remote-login door. Solid lock, so there is no point attacking it directly. We come back once we have found a username and password.                                      |
| 80/tcp    | HTTP       | nginx 1.24.0 (Ubuntu)             | Does not serve on the raw IP; responds with a redirect toward `api.htb-airport.htb`. Confirms name-based virtual hosting, so the real site only appears when the correct Host header is sent. First real lead. | The web server refuses to show its site unless you knock using the right domain name instead of the bare IP address. That name is our way in.                                |
| 8081/tcp  | HTTP       | Uvicorn                           | Python ASGI server returning `application/json` with no HTML title. A machine-facing API rather than a human website; worth reading directly to learn what it ingests and how.                                 | A second web service that talks in raw data, not web pages. It is built for programs to call, which usually means it will tell us exactly what it expects if we just ask it. |
| 40899/tcp | tcpwrapped | Unknown                           | Handshake completes then the service drops it, so nmap cannot fingerprint it. Port number is randomized per spawn. No actionable surface; set aside.                                                           | A door that opens a crack then slams shut before saying anything. Nothing to work with, and the number changes each time the box restarts, so ignore it.                     |
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## 2. Enumeration
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## 3. Exploitation
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## 4. Post-Exploitation
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

