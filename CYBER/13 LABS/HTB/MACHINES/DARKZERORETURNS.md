---
link: https://app.hackthebox.com/machines/DarkZeroReturns?sort_by=created_at&sort_type=desc
description: Hard·Windows
release date: 2026-07-25
tags:
  - SN_11
image: https://cdn.services-k8s.prod.aws.htb.systems/content/machines/avatar/a1fb32a5-8e1c-4d62-bf6e-d2041d6448ad-1781002585.png
solved:
solve date:
machine no.: 10
---

<div style="text-align: center; padding: 80px 40px; page-break-after: always;">

  <img src="/ASSETS/writeup_hack_the_box_logo.png" style="width: 1220px; margin-bottom: 60px;" />

  <div><p style="font-size: 40px; font-weight: 600; margin-bottom: 40px;">DarkZeroReturns Writeup</p></div>

  <img src="https://cdn.services-k8s.prod.aws.htb.systems/content/machines/avatar/a1fb32a5-8e1c-4d62-bf6e-d2041d6448ad-1781002585.png" style="width: 400px; margin-bottom: 60px;" />

  <div style="font-size: 18px; line-height: 2.2;">
    <p style="margin: 0;">Prepared by: nedmoeca</p>
    <p style="margin: 0;">Author(s): 0xEr3bus & Pho3o</p>
    <p style="margin: 0;">Difficulty: Hard</p>
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

VPN is established but unverified. Establish that the target answers before spending time on scans that would otherwise fail silently.

**Command:** `ping -c 4 TARGET_IP`

**Breakdown:**

| Component   | Purpose                  | Simple Explanation                                |
| ----------- | ------------------------ | ------------------------------------------------- |
| `ping`      | Sends ICMP echo requests | Asks "are you there?" and waits for a reply       |
| `-c 4`      | Stop after 4 packets     | Otherwise it runs forever until interrupted       |
| `TARGET_IP` | Destination host         | The HTB machine address assigned to your instance |

**Result:**

```shell
┌──(kali㉿kali)-[~]
└─$ ping -c 4 10.129.53.206
PING 10.129.53.206 (10.129.53.206) 56(84) bytes of data.
64 bytes from 10.129.53.206: icmp_seq=1 ttl=127 time=236 ms
64 bytes from 10.129.53.206: icmp_seq=2 ttl=127 time=234 ms
64 bytes from 10.129.53.206: icmp_seq=3 ttl=127 time=231 ms
64 bytes from 10.129.53.206: icmp_seq=4 ttl=127 time=242 ms

--- 10.129.53.206 ping statistics ---
4 packets transmitted, 4 received, 0% packet loss, time 3004ms
rtt min/avg/max/mdev = 231.415/235.706/241.509/3.743 ms
```

Zero packet loss confirms the VPN tunnel and target are both live.

**Key finding:** TTL 127 indicates an initial TTL of 128 decremented by a single hop. An initial TTL of 128 is the Windows default; Linux defaults to 64. Treat the host as Windows-family for now and revisit if service banners contradict it.

**Next:** With reachability confirmed, enumerate the full TCP port range to establish the exposed attack surface.
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

#### 2.1.1 Full Port Sweep

Reachability is confirmed but the attack surface is unknown. Scan the full port range rather than nmap's default top 1000, since a service on a high port is a common way for boxes to hide their real entry point.

**Command:** `nmap -p- --min-rate 5000 -Pn TARGET_IP | grapo`

**Breakdown:**

| Component         | Purpose                        | Simple Explanation                                                                                                             |
| ----------------- | ------------------------------ | ------------------------------------------------------------------------------------------------------------------------------ |
| `nmap`            | Port scanner                   | Knocks on every door and notes which ones open                                                                                 |
| `-p-`             | Scan ports 1–65535             | The full range, not just the common ones                                                                                       |
| `--min-rate 5000` | Send at least 5000 packets/sec | Forces speed; a full-range scan at default rate takes many minutes                                                             |
| `-Pn`             | Skip host discovery            | Treat the host as up without pinging first — already verified manually                                                         |
| `TARGET_IP`       | Target                         | The HTB machine                                                                                                                |
| `\| grapo`        | Custom zsh function            | Prints full nmap output to the terminal while extracting open ports as a comma-joined list for copying into the follow-up scan |

**Result:**

```shell
┌──(kali㉿kali)-[~]
└─$ nmap -p- --min-rate 5000 -Pn 10.129.53.206 | grapo              
Starting Nmap 7.98 ( https://nmap.org ) at 2026-07-27 06:59 +0000
Nmap scan report for 10.129.53.206
Host is up (0.46s latency).
Not shown: 65533 filtered tcp ports (no-response)
PORT   STATE SERVICE
22/tcp open  ssh
80/tcp open  http

Nmap done: 1 IP address (1 host up) scanned in 29.33 seconds

22,80
```
<div align="center">
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
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

```
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

