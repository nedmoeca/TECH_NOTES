---
link: https://app.hackthebox.com/machines/Paperwork?sort_by=created_at&sort_type=desc
description: Easy·Linux
release date: 2026-07-11
tags:
  - SN_11
image: https://cdn.services-k8s.prod.aws.htb.systems/content/machines/avatar/a1ee24ec-e2f1-4c61-88ca-9d7d4d296251-1780441937.png
solved:
solve date:
machine no.: 8
---

<div style="text-align: center; padding: 80px 40px; page-break-after: always;">

  <img src="/ASSETS/writeup_hack_the_box_logo.png" style="width: 1220px; margin-bottom: 60px;" />

  <div><p style="font-size: 40px; font-weight: 600; margin-bottom: 40px;">"Machine Name" Writeup</p></div>

  <img src="badge link" style="width: 400px; margin-bottom: 60px;" />

  <div style="font-size: 18px; line-height: 2.2;">
    <p style="margin: 0;">Prepared by: nedmoeca</p>
    <p style="margin: 0;">Author(s): "htb username"</p>
    <p style="margin: 0;">Difficulty: Easy/Medium/Hard/Insane</p>
    <p style="margin: 0;">Date: DD Month Year</p>
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

- `ping`
    - **Description:** Sends ICMP echo-request packets and reports replies and round-trip times.
    - **Purpose:** Confirm the target host is alive and routable over the VPN tunnel before committing to a full port scan.
- `-c 4`
    - **Description:** Count — stop after sending four packets rather than pinging indefinitely.
    - **Purpose:** A quick liveness check; four packets is enough to confirm reachability and see a stable round-trip time.

**Result:**

```shell
┌──(kali㉿kali)-[~/…/HTB/Machines/SN11/Paperwork]
└─$ ping -c 4 10.129.35.97                                          
PING 10.129.35.97 (10.129.35.97) 56(84) bytes of data.
64 bytes from 10.129.35.97: icmp_seq=1 ttl=63 time=215 ms
64 bytes from 10.129.35.97: icmp_seq=2 ttl=63 time=489 ms
64 bytes from 10.129.35.97: icmp_seq=3 ttl=63 time=215 ms
64 bytes from 10.129.35.97: icmp_seq=4 ttl=63 time=215 ms

--- 10.129.35.97 ping statistics ---
4 packets transmitted, 4 received, 0% packet loss, time 3006ms
rtt min/avg/max/mdev = 214.660/283.254/488.550/118.527 ms
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

**Command:** `nmap -p- --min-rate 5000 -Pn TARGET_IP | grapo`

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
- `| grapo`
	- **Description:** Custom shell function (defined in `~/.zshrc`) that echoes the full scan to the terminal via `tee /dev/tty`, then extracts open-port numbers and prints them as a comma-joined list.
	- **Purpose:** Produces a ready-to-copy port string (`22,80,1515`) to feed straight into the targeted deep scan, without hand-copying from the report.

**Result:**

```shell
┌──(kali㉿kali)-[~/…/HTB/Machines/SN11/Paperwork]
└─$ nmap -p- --min-rate 5000 -Pn 10.129.35.97 | grapo
Starting Nmap 7.98 ( https://nmap.org ) at 2026-07-18 14:15 +0000
Warning: 10.129.35.97 giving up on port because retransmission cap hit (10).
Nmap scan report for 10.129.35.97
Host is up (0.24s latency).
Not shown: 65306 closed tcp ports (reset), 226 filtered tcp ports (no-response)
PORT     STATE SERVICE
22/tcp   open  ssh
80/tcp   open  http
1515/tcp open  ifor-protocol

Nmap done: 1 IP address (1 host up) scanned in 49.20 seconds

22,80,1515
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
┌──(kali㉿kali)-[~/…/HTB/Machines/SN11/Paperwork]
└─$ nmap -A -p 22,80,1515 10.129.35.97               
Starting Nmap 7.98 ( https://nmap.org ) at 2026-07-18 14:29 +0000
Nmap scan report for 10.129.35.97
Host is up (0.23s latency).

PORT     STATE SERVICE        VERSION
22/tcp   open  ssh            OpenSSH 10.0p2 Ubuntu 5ubuntu5.4 (Ubuntu Linux; protocol 2.0)
80/tcp   open  http           nginx 1.28.0 (Ubuntu)
|_http-title: Did not follow redirect to http://paperwork.htb/
|_http-server-header: nginx/1.28.0 (Ubuntu)
1515/tcp open  ifor-protocol?
| fingerprint-strings: 
|   TerminalServer, TerminalServerCookie: 
|_    Archive_Printer is ready and printing.
1 service unrecognized despite returning data. If you know the service/version, please submit the following fingerprint at https://nmap.org/cgi-bin/submit.cgi?new-service :
SF-Port1515-TCP:V=7.98%I=7%D=7/18%Time=6A5B8DDB%P=x86_64-pc-linux-gnu%r(Te
SF:rminalServerCookie,27,"Archive_Printer\x20is\x20ready\x20and\x20printin
SF:g\.\n")%r(TerminalServer,27,"Archive_Printer\x20is\x20ready\x20and\x20p
SF:rinting\.\n");
Warning: OSScan results may be unreliable because we could not find at least 1 open and 1 closed port
Device type: general purpose
Running: Linux 4.X|5.X
OS CPE: cpe:/o:linux:linux_kernel:4 cpe:/o:linux:linux_kernel:5
OS details: Linux 4.15 - 5.19
Network Distance: 2 hops
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel

TRACEROUTE (using port 443/tcp)
HOP RTT       ADDRESS
1   237.45 ms 10.10.14.1
2   237.82 ms 10.129.35.97

OS and Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 34.47 seconds
```
<div align="center">
<br>
<br>
</div>

#### 2.1.3 Scan Results Analysis

| Port | **Service** | **Version** | **Analysis** | **Simple Explanation** |
| ---- | ----------- | ----------- | ------------ | ---------------------- |
|      |             |             |              |                        |
|      |             |             |              |                        |

<div align="center">
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
</div>

### 2.2 
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

