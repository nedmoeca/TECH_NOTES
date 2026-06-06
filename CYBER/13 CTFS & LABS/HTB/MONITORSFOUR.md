---
tags:
link: https://app.hackthebox.com/machines/MonitorsFour?sort_by=created_at&sort_type=desc
description: Easy·Windows
image: https://htb-mp-prod-public-storage.s3.eu-central-1.amazonaws.com/avatars/c7878dd8dba2eb248a89584ec958a5b8.png
date:
pawned: false
---
## Summary

| SECTION/TASK     | FLAG |
| ---------------- | ---- |
| Submit User Flag |      |
| Submit Root Flag |      |

<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

### 1.1 Connecting to the HTB VPN

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

Command: `ping -c 4 TARGET_IP`

Breakdown:
- `-c 4` → sends 4 packets only (clean output, fast)

Output:

```shell
┌──(kali㉿kali)-[~/PUEMAN/HTB]
└─$ ping -c 4 TARGET_IP  
PING TARGET_IP (TARGET_IP) 56(84) bytes of data.
64 bytes from TARGET_IP: icmp_seq=1 ttl=127 time=274 ms
64 bytes from TARGET_IP: icmp_seq=2 ttl=127 time=266 ms
64 bytes from TARGET_IP: icmp_seq=3 ttl=127 time=450 ms
64 bytes from TARGET_IP: icmp_seq=4 ttl=127 time=466 ms

--- TARGET_IP ping statistics ---
4 packets transmitted, 4 received, 0% packet loss, time 3009ms
rtt min/avg/max/mdev = 266.237/363.989/465.632/94.209 ms
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

Command: `nmap -p- --min-rate 5000 -Pn TARGET_IP`

Breakdown:
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

Output:

```shell
┌──(kali㉿kali)-[~/PUEMAN/HTB]
└─$ nmap -p- --min-rate 5000 -Pn 10.129.9.3
Starting Nmap 7.98 ( https://nmap.org ) at 2026-03-15 15:17 -0400
Nmap scan report for 10.129.9.3
Host is up (0.43s latency).
Not shown: 65533 filtered tcp ports (no-response)
PORT     STATE SERVICE
80/tcp   open  http
5985/tcp open  wsman

Nmap done: 1 IP address (1 host up) scanned in 30.78 seconds
```
<div align="center">
<br>
<br>
</div>

#### 2.1.2 The "Deep Dive" Scan (Targeted Aggression)

Command: `nmap -A -p p1,p2,p3,p4 TARGET_IP`

Breakdown:
- **`-A`**
    - **Description:** Aggressive Scan Mode.
    - **Purpose:** Enables OS detection, version detection, script scanning (`-sC`), and traceroute all at once.
- `-p`
    - **Description:** Targeted Port List.
    - **Purpose:** Restricts the heavy scanning to only the ports you confirmed are open, saving significant time and processing power.


Output:

```shell
┌──(kali㉿kali)-[~/PUEMAN/HTB]
└─$ nmap -A -p 80,5985 10.129.9.3          
Starting Nmap 7.98 ( https://nmap.org ) at 2026-03-15 15:19 -0400
Nmap scan report for 10.129.9.3
Host is up (0.26s latency).

PORT     STATE SERVICE VERSION
80/tcp   open  http    nginx
|_http-title: Did not follow redirect to http://monitorsfour.htb/
5985/tcp open  http    Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
|_http-title: Not Found
|_http-server-header: Microsoft-HTTPAPI/2.0
Warning: OSScan results may be unreliable because we could not find at least 1 open and 1 closed port
Device type: general purpose
Running (JUST GUESSING): Microsoft Windows 2022|2012|2016 (88%)
OS CPE: cpe:/o:microsoft:windows_server_2022 cpe:/o:microsoft:windows_server_2012:r2 cpe:/o:microsoft:windows_server_2016
Aggressive OS guesses: Microsoft Windows Server 2022 (88%), Microsoft Windows Server 2012 R2 (85%), Microsoft Windows Server 2016 (85%)
No exact OS matches for host (test conditions non-ideal).
Network Distance: 2 hops
Service Info: OS: Windows; CPE: cpe:/o:microsoft:windows

TRACEROUTE (using port 80/tcp)
HOP RTT       ADDRESS
1   263.57 ms 10.10.14.1
2   263.17 ms 10.129.9.3

OS and Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 30.71 seconds
```
<div align="center">
<br>
<br>
</div>

#### 2.1.3 Scan Results Analysis

| Port | **Service** | **Version**           | **Analysis**                                                                                                                              |
| ---- | ----------- | --------------------- | ----------------------------------------------------------------------------------------------------------------------------------------- |
| 80   | HTTP        | Nginx                 | The server attempts to redirect to `http://monitorsfour.htb/`. This suggests virtual hosting is in use and requires local DNS resolution. |
| 5985 | HTTP        | Microsoft HTTPAPI 2.0 | This port is commonly used for Windows Remote Management (WinRM). Its presence strongly indicates a Windows target.                       |

<div align="center">
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
</div>

### 2.2 Enumeration of Web Services

#### 2.2.1. Update Hosts File

Command: `sudo vi etc/hosts`

**Breakdown:**

- `sudo` 
	- Description: Elevated Privileges
	- Purpose: Required to modify system-level configuration files like the hosts database.
- `vi` 
	- Description: Terminal Text Editor
	- Purpose: Used to append the `TARGET_IP wingdata.htb` entry to the file.
- `/etc/hosts` 
	- Description: Static Host Lookup Table
	- Purpose: The local file that takes precedence over DNS servers, ensuring the domain resolves to the CTF machine.
<div align="center">
<br>
<br>
</div>

#### 2.2.2 Web Enumeration

Browse to `http://monitorsfour.htb/`.

![[Pasted image 20260315224808.png]]
<div align="center">
<br>
<br>
</div>

#### 2.2.3. Directory Fuzzing

Command: `ffuf -w /usr/share/wordlists/seclists/Discovery/DNS/subdomains-top1million-5000.txt -u http://monitorsfour.htb/ -H "Host: FUZZ.monitorsfour.htb" -ac`

Breakdown:

- **`-w .../subdomains-top1million-5000.txt`**
    - **Description:** Wordlist Path.
    - **Purpose:** Utilizes a more specialized DNS-focused wordlist for better hit rates on common subdomains.
- **`-u`**
    - **Description:** Target URL.
    - **Purpose:** Specifies the URL to be fuzzed. The keyword `FUZZ` tells the tool exactly where to inject the words from your wordlist.
- `-H "Host: FUZZ.monitorsfour.htb"`
	- **Description:** Specifically targets the VHost routing logic of the web server.
	- **Purpose:** This command automates the filtering process, allowing the tool to intelligently ignore "too many outputs" and only present results that differ from the server's standard behavior.

Output:
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

## 5. Conclusion & Remediation
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## References

