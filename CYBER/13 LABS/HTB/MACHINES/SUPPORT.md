---
link:
description:
release date:
tags:
image:
solved:
solve date:
machine no.:
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
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
<br>
</div>

### 1.2 Verify Target is Reachable

Why this step: Before enumerating, confirm the VPN tunnel actually routes to the target and note any OS fingerprint the response leaks.

**Command:** `ping -c 4 TARGET_IP`

**Breakdown:**

- `ping`
    - **Description:** Sends ICMP echo requests to a host and reports replies and round-trip time.
    - **Purpose:** Confirms the target is live and reachable over the HTB VPN before spending time on port scans.
- `-c 4`
    - **Description:** Count — stop after sending 4 packets.
    - **Purpose:** Bounds the check to a quick, finite sample instead of pinging forever.

**Result:**

```shell
┌──(kali㉿kali)-[~/…/HTB/Machines/Retired/Support]
└─$ ping -c 4 10.129.230.181  
PING 10.129.230.181 (10.129.230.181) 56(84) bytes of data.
64 bytes from 10.129.230.181: icmp_seq=1 ttl=127 time=224 ms
64 bytes from 10.129.230.181: icmp_seq=2 ttl=127 time=224 ms
64 bytes from 10.129.230.181: icmp_seq=3 ttl=127 time=228 ms
64 bytes from 10.129.230.181: icmp_seq=4 ttl=127 time=228 ms

--- 10.129.230.181 ping statistics ---
4 packets transmitted, 4 received, 0% packet loss, time 3007ms
rtt min/avg/max/mdev = 224.416/226.332/228.333/1.905 ms
```

**Key finding:** the host is reachable with 0% packet loss, and `ttl=127` indicates a Windows target (initial TTL of 128, decremented by one hop) — this frames every enumeration choice that follows toward Windows/AD services.

**Next:** With reachability and a likely-Windows OS confirmed, map the attack surface by scanning ports and fingerprinting services.

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

#### 2.1.1 Scan All Ports

A quick full-range sweep establishes the complete attack surface before committing time to version detection, so no listening service is missed.

**Command:** `nmap -p- --min-rate 5000 -Pn TARGET_IP`

**Breakdown:**

- `nmap`
    - **Description:** Network mapper — probes hosts for open ports and running services.
    - **Purpose:** Enumerates every reachable TCP port on the target.
- `-p-`
    - **Description:** Scan all 65,535 TCP ports rather than the default top 1,000.
    - **Purpose:** Ensures high ephemeral RPC ports and any non-standard service are captured.
- `--min-rate 5000`
    - **Description:** Send packets at a minimum of 5,000 per second.
    - **Purpose:** Keeps a full-range scan fast enough to be practical against a high-latency VPN target.
- `-Pn`
    - **Description:** Skip host discovery and treat the host as up.
    - **Purpose:** Avoids missing the target if it filters ICMP, and reachability was already confirmed by ping.

**Result:**

```shell
┌──(kali㉿kali)-[~/…/HTB/Machines/Retired/Support]
└─$ nmap -p- --min-rate 5000 -Pn 10.129.230.181 | grapo
Starting Nmap 7.98 ( https://nmap.org ) at 2026-07-22 05:59 +0000
Nmap scan report for 10.129.230.181
Host is up (0.43s latency).
Not shown: 65518 filtered tcp ports (no-response)
PORT      STATE SERVICE
53/tcp    open  domain
88/tcp    open  kerberos-sec
135/tcp   open  msrpc
139/tcp   open  netbios-ssn
389/tcp   open  ldap
445/tcp   open  microsoft-ds
464/tcp   open  kpasswd5
593/tcp   open  http-rpc-epmap
636/tcp   open  ldapssl
3269/tcp  open  globalcatLDAPssl
5985/tcp  open  wsman
49664/tcp open  unknown
49667/tcp open  unknown
49678/tcp open  unknown
49690/tcp open  unknown
49703/tcp open  unknown
49741/tcp open  unknown

Nmap done: 1 IP address (1 host up) scanned in 41.67 seconds

53,88,135,139,389,445,464,593,636,3269,5985,49664,49667,49678,49690,49703,49741
```

**Key finding:** the open-port profile — Kerberos (88), LDAP (389/636/3269), SMB (445), DNS (53), WinRM (5985) — is the classic fingerprint of a Windows Active Directory Domain Controller, with no web service present.

**Next:** Run version and script detection against the named service ports to confirm the domain and identify the host role.
<div align="center">
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
</div>

#### 2.1.2 Run a Targeted Deep Scan

The full sweep found the ports; a scripted version scan on the meaningful service ports is needed to confirm the domain name and DC hostname required for host-file entries and later LDAP/SMB work.

**Command:** `nmap -A -p 53,88,135,139,389,445,464,593,636,3269,5985 TARGET_IP`

**Breakdown:**

- `-A`
    - **Description:** Aggressive scan — enables version detection (`-sV`), default scripts (`-sC`), OS detection, and traceroute in one flag.
    - **Purpose:** Pulls service versions and LDAP/SMB script data that reveal the domain and host role.
- `-p 53,88,135,139,389,445,464,593,636,3269,5985`
    - **Description:** Restrict the scan to this explicit port list.
    - **Purpose:** Targets only the named AD service ports, deliberately excluding the dynamic high RPC ports (49664+) that add scan time without actionable results.

**Result:**

```shell
┌──(kali㉿kali)-[~/…/HTB/Machines/Retired/Support]
└─$ nmap -A -p 53,88,135,139,389,445,464,593,636,3269,5985 10.129.230.181
Starting Nmap 7.98 ( https://nmap.org ) at 2026-07-22 06:04 +0000
Nmap scan report for 10.129.230.181
Host is up (0.23s latency).

PORT     STATE SERVICE       VERSION
53/tcp   open  domain        Simple DNS Plus
88/tcp   open  kerberos-sec  Microsoft Windows Kerberos (server time: 2026-07-22 06:04:33Z)
135/tcp  open  msrpc         Microsoft Windows RPC
139/tcp  open  netbios-ssn   Microsoft Windows netbios-ssn
389/tcp  open  ldap          Microsoft Windows Active Directory LDAP (Domain: support.htb, Site: Default-First-Site-Name)
445/tcp  open  microsoft-ds?
464/tcp  open  kpasswd5?
593/tcp  open  ncacn_http    Microsoft Windows RPC over HTTP 1.0
636/tcp  open  tcpwrapped
3269/tcp open  tcpwrapped
5985/tcp open  http          Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
|_http-server-header: Microsoft-HTTPAPI/2.0
|_http-title: Not Found
Warning: OSScan results may be unreliable because we could not find at least 1 open and 1 closed port
Device type: general purpose
Running (JUST GUESSING): Microsoft Windows 2022|2012|2016 (89%)
OS CPE: cpe:/o:microsoft:windows_server_2022 cpe:/o:microsoft:windows_server_2012:r2 cpe:/o:microsoft:windows_server_2016
Aggressive OS guesses: Microsoft Windows Server 2022 (89%), Microsoft Windows Server 2012 R2 (85%), Microsoft Windows Server 2016 (85%)
No exact OS matches for host (test conditions non-ideal).
Network Distance: 2 hops
Service Info: Host: DC; OS: Windows; CPE: cpe:/o:microsoft:windows

Host script results:
| smb2-security-mode: 
|   3.1.1: 
|_    Message signing enabled and required
| smb2-time: 
|   date: 2026-07-22T06:04:57
|_  start_date: N/A
|_clock-skew: -19s

TRACEROUTE (using port 445/tcp)
HOP RTT       ADDRESS
1   231.72 ms 10.10.14.1
2   232.39 ms 10.129.230.181

OS and Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 79.01 seconds
```

**Key finding:** the domain is `support.htb` and the host role is `DC`, confirming the target is the domain controller `dc.support.htb`; SMB 3.1.1 requires message signing.

_Next:_ Map the identified ports to their attack implications, then begin service enumeration against SMB — the only anonymous-friendly entry point exposed.

<div align="center">
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
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
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
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

