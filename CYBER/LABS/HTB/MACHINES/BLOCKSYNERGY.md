---
link: https://app.hackthebox.com/machines/BlockSynergy
difficulty: Insane
os: Linux
release date: 2026-08-29
tags:
  - SN_11
image: https://cdn.services-k8s.prod.aws.htb.systems/content/machines/avatar/a29813ab-2643-4f77-80fd-65500f97bcd0-1787750589.png
solved:
solve date:
machine no.: 13
---

<div style="text-align: center; padding: 80px 40px; page-break-after: always;">

  <img src="/ASSETS/writeup_hack_the_box_logo.png" style="width: 1220px; margin-bottom: 60px;" />

  <div><p style="font-size: 40px; font-weight: 600; margin-bottom: 40px;">BlockSynergy Writeup</p></div>

  <img src="https://cdn.services-k8s.prod.aws.htb.systems/content/machines/avatar/a29813ab-2643-4f77-80fd-65500f97bcd0-1787750589.png" style="width: 400px; margin-bottom: 60px;" />

  <div style="font-size: 22px; line-height: 2.2;">
    <p style="margin: 0;">Prepared by: nedmoeca</p>
    <p style="margin: 0;">Author(s): R00cKet</p>
    <p style="margin: 0;">Difficulty: Insane</p>
    <p style="margin: 0;">Date: 29 Aug 2026</p>
  </div>

</div>
<!-- PAGE BREAK -->

## Summary

**Category: Web Exploitation**, with **Linux Privilege Escalation** as a strong secondary phase.

It's primarily web because everything from first packet to user shell happens through a single custom Python web application on port 8080. A homemade blockchain whose transaction endpoint never verifies signatures, whose proof-of-work you can reproduce yourself, and whose admin panel builds a shell command out of a URL you control. The privesc half is a different skill entirely: a race condition against a root-owned restore daemon that checks a file's hash and then re-opens it, giving you a window to swap the file.

A few things worth knowing before we touch anything. The box has no lateral-movement-across-hosts phase in the classic sense, but there _is_ a user-to-user pivot (walter → hank) through a second Flask app bound to localhost. You'll be writing two small Python scripts of your own — one to mine a block, one to win a race — so have an editor ready. And several stages here fail silently if a single field name or a single character is wrong, so I'll flag those gotchas before you hit them rather than after.
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

### 1.2 Verify Target is Reachable

Verify that the target machine is up and reachable by performing an ICMP ping test.

**Command:** `ping -c 4 TARGET_IP`

**Breakdown:**

- `-c 4` → sends 4 packets only (clean output, fast)

**Result:**

```shell
┌──(nedmoeca㉿kali)-[~/Labs/HTB/SN11/BlockSynergy]
└─$ ping -c 4 10.129.115.174
PING 10.129.115.174 (10.129.115.174) 56(84) bytes of data.
64 bytes from 10.129.115.174: icmp_seq=1 ttl=63 time=201 ms
64 bytes from 10.129.115.174: icmp_seq=2 ttl=63 time=232 ms
64 bytes from 10.129.115.174: icmp_seq=3 ttl=63 time=262 ms
64 bytes from 10.129.115.174: icmp_seq=4 ttl=63 time=291 ms

--- 10.129.115.174 ping statistics ---
4 packets transmitted, 4 received, 0% packet loss, time 3004ms
rtt min/avg/max/mdev = 200.902/246.514/291.001/33.608 ms
```

A successful response confirms that the machine is active and accessible on the HTB network, allowing us to proceed with the enumeration phase.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## 2. Enumeration

### 2.1 Port Scan with Nmap

Before we can attack a system, we need to find out what "doors" are open. Doors in this context are ports. We use a tool called **Nmap** (Network Mapper) to scan the target's IP address and see what services are running.

#### 2.1.1 Full Port Sweep

Begin enumeration by discovering every open port on the target. Run a fast scan across all 65,535 ports to build a complete picture of the attack surface before committing to deeper inspection.

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




