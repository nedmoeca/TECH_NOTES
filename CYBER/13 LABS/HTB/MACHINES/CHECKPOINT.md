---
link: https://app.hackthebox.com/machines/Checkpoint
description: Medium·Windows
release date: 2026-06-13
tags:
  - SN_11
image: https://htb-mp-prod-public-storage.s3.eu-central-1.amazonaws.com/avatars/d90d9ba3228fb458485c03a1b4c2f6e5.png
solved:
solve date:
machine no.: 4
---
<div style="text-align: center; padding: 80px 40px; page-break-after: always;">

  <img src="/ASSETS/HTB Logo.png" style="width: 1220px; margin-bottom: 60px;" />

  <div><p style="font-size: 40px; font-weight: 600; margin-bottom: 40px;">Checkpoint Writeup</p></div>

  <img src="https://htb-mp-prod-public-storage.s3.eu-central-1.amazonaws.com/avatars/d90d9ba3228fb458485c03a1b4c2f6e5.png" style="width: 400px; margin-bottom: 60px;" />

  <div style="font-size: 18px; line-height: 2.2;">
    <p style="margin: 0;">Prepared by: nedmoeca</p>
    <p style="margin: 0;">Machine Author(s): AnuragTaparia</p>
    <p style="margin: 0;">Difficulty: Medium</p>
    <p style="margin: 0;">Date: 20 June 2026</p>
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
└─$ ping -c 4 10.129.32.103
PING 10.129.32.103 (10.129.32.103) 56(84) bytes of data.
64 bytes from 10.129.32.103: icmp_seq=1 ttl=127 time=221 ms
64 bytes from 10.129.32.103: icmp_seq=2 ttl=127 time=223 ms
64 bytes from 10.129.32.103: icmp_seq=3 ttl=127 time=220 ms
64 bytes from 10.129.32.103: icmp_seq=4 ttl=127 time=223 ms

--- 10.129.32.103 ping statistics ---
4 packets transmitted, 4 received, 0% packet loss, time 3008ms
rtt min/avg/max/mdev = 220.158/221.730/222.947/1.204 ms
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
└─$ nmap -p- --min-rate 5000 -Pn 10.129.32.103
Starting Nmap 7.98 ( https://nmap.org ) at 2026-06-19 17:06 -0400
Nmap scan report for 10.129.32.103
Host is up (0.47s latency).
Not shown: 65518 filtered tcp ports (no-response)
PORT      STATE SERVICE
53/tcp    open  domain
135/tcp   open  msrpc
139/tcp   open  netbios-ssn
389/tcp   open  ldap
445/tcp   open  microsoft-ds
464/tcp   open  kpasswd5
593/tcp   open  http-rpc-epmap
636/tcp   open  ldapssl
3269/tcp  open  globalcatLDAPssl
5985/tcp  open  wsman
49670/tcp open  unknown
49671/tcp open  unknown
49673/tcp open  unknown
49674/tcp open  unknown
49683/tcp open  unknown
49704/tcp open  unknown
49712/tcp open  unknown

Nmap done: 1 IP address (1 host up) scanned in 54.20 seconds
```
<div align="center">
<br>
<br>
</div>

#### 2.1.2 The "Deep Dive" Scan (Targeted Aggression)

With the open ports identified, run an aggressive scan against only those ports to extract service versions, the operating system, and Active Directory metadata.

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
└─$ nmap -A -p 53,135,139,389,445,464,593,636,3269,5985 10.129.32.103     
Starting Nmap 7.98 ( https://nmap.org ) at 2026-06-19 17:22 -0400
Nmap scan report for 10.129.32.103
Host is up (0.22s latency).

PORT     STATE SERVICE           VERSION
53/tcp   open  domain            Simple DNS Plus
135/tcp  open  msrpc             Microsoft Windows RPC
139/tcp  open  netbios-ssn       Microsoft Windows netbios-ssn
389/tcp  open  ldap              Microsoft Windows Active Directory LDAP (Domain: checkpoint.htb, Site: Default-First-Site-Name)
445/tcp  open  microsoft-ds?
464/tcp  open  kpasswd5?
593/tcp  open  ncacn_http        Microsoft Windows RPC over HTTP 1.0
636/tcp  open  ldapssl?
3269/tcp open  globalcatLDAPssl?
5985/tcp open  http              Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
|_http-server-header: Microsoft-HTTPAPI/2.0
|_http-title: Not Found
Warning: OSScan results may be unreliable because we could not find at least 1 open and 1 closed port
Device type: general purpose
Running (JUST GUESSING): Microsoft Windows 2022|2012|2016 (88%)
OS CPE: cpe:/o:microsoft:windows_server_2022 cpe:/o:microsoft:windows_server_2012:r2 cpe:/o:microsoft:windows_server_2016
Aggressive OS guesses: Microsoft Windows Server 2022 (88%), Microsoft Windows Server 2012 R2 (85%), Microsoft Windows Server 2016 (85%)
No exact OS matches for host (test conditions non-ideal).
Network Distance: 2 hops
Service Info: Host: DC01; OS: Windows; CPE: cpe:/o:microsoft:windows

Host script results:
|_clock-skew: 6h59m58s
| smb2-security-mode: 
|   3.1.1: 
|_    Message signing enabled and required
| smb2-time: 
|   date: 2026-06-20T04:23:15
|_  start_date: N/A

TRACEROUTE (using port 135/tcp)
HOP RTT       ADDRESS
1   217.07 ms 10.10.14.1
2   217.40 ms 10.129.32.103

OS and Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 82.09 seconds
```


Reasons high ports (49670, 49671, etc.) are left out of the `-A` pass:

- **They're not stable.** The OS reassigns them from the 49152–65535 pool, often on every reboot. If you document "service X on 49670" today, that port may belong to something else after the box resets — so version-scanning them produces results that age out immediately and aren't worth putting in a report.
- **`-A` on them is slow and yields little.** Version detection plus NSE scripts against a dozen dynamic RPC ports adds real time, and nmap almost always just comes back with `msrpc` again — no clean fingerprint. High cost, near-zero new information.
- **They're the same RPC subsystem you already see on 135/593.** They don't represent a _new_ attack surface; they're the dynamically-allocated tail end of the RPC service the endpoint mapper already advertises. Scanning 135 covers the front door.

So for the deep scan, focusing on the named service ports (53, 389, 445, 464, 636, 3269, 5985…) gives you everything actionable — the domain, hostname, and service versions.
<div align="center">
<br>
<br>
</div>

#### 2.1.3 Scan Results Analysis

| Port | **Service** | **Version** | **Analysis** |
| ---- | ----------- | ----------- | ------------ |
|      |             |             |              |
|      |             |             |              |

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

