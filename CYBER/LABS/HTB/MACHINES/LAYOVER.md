---
link: https://app.hackthebox.com/machines/Layover
difficulty: Medium
os: Linux
pov: red
release date: 2026-09-26
tags:
  - SN_12
image: https://cdn.services-k8s.prod.aws.htb.systems/content/machines/avatar/a2cc2776-5507-42ae-b9d0-3346ff823ce7-1789977190.png
solved:
solve date:
machine no.: 1
---

<div style="text-align: center; padding: 80px 40px; page-break-after: always;">

  <img src="/ASSETS/writeup_hack_the_box_logo.png" style="width: 1220px; margin-bottom: 60px;" />

  <div><p style="font-size: 40px; font-weight: 600; margin-bottom: 40px;">Layover Writeup</p></div>

  <img src="https://cdn.services-k8s.prod.aws.htb.systems/content/machines/avatar/a2cc2776-5507-42ae-b9d0-3346ff823ce7-1789977190.png" style="width: 400px; margin-bottom: 60px;" />

  <div style="font-size: 22px; line-height: 2.2;">
    <p style="margin: 0;">Prepared by: <a href="https://app.hackthebox.com/users/1809572">nedmoeca</a></p>
    <p style="margin: 0;">Author(s): <a href="https://app.hackthebox.com/users/31190">TRX</a></p>
    <p style="margin: 0;">Difficulty: Medium</p>
    <p style="margin: 0;">Date: DD Month Year</p>
  </div>

</div>
<!-- PAGE BREAK -->

## Summary


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

### 1.3 Confirm target reachability

Before scanning, verify the host answers over the VPN and read the TTL for a first, free OS guess. A dead host wastes a long full-port scan; a live one with a tell-tale TTL saves you a question later.

**Command:** `ping -c 4 TARGET_IP`

**Breakdown:**

|Component|Reasoning|
|---|---|
|`ping`|Sends ICMP echo-request packets and waits for echo-replies to prove L3 reachability.|
|`-c 4`|Stop after 4 packets instead of running forever, so the command returns on its own.|
|`$IP`|Session variable holding the target address, resolved to TARGET_IP.|

**Result:**

```
PING TARGET_IP (TARGET_IP) 56(84) bytes of data.
64 bytes from TARGET_IP: icmp_seq=1 ttl=63 time=220 ms
64 bytes from TARGET_IP: icmp_seq=2 ttl=63 time=269 ms
64 bytes from TARGET_IP: icmp_seq=3 ttl=63 time=215 ms
64 bytes from TARGET_IP: icmp_seq=4 ttl=63 time=217 ms

--- TARGET_IP ping statistics ---
4 packets transmitted, 4 received, 0% packet loss, time 3007ms
rtt min/avg/max/mdev = 215.351/230.282/269.199/22.518 ms
```

Key findings:

- Host is up: 4/4 replies, 0% packet loss (evidence).
- `ttl=63` implies an original TTL of 64 decremented by one hop, which is the Linux default, so the target is likely Linux (inference, to be confirmed by the service banners).
- Average RTT ~230 ms is pure VPN latency, so expect sluggish interactive sessions and plan to drop to a reverse shell early (inference).

**Next:** With the host confirmed alive, enumerate every open TCP port to map the full attack surface.
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

**Command:**

```bash
# fast all-ports sweep, piped through the grapo helper to extract open ports
nmap -p- --min-rate 5000 -Pn TARGET_IP | grapo
```

**Breakdown:**

|Component|Reasoning|
|---|---|
|`nmap -p-`|Scan all 65,535 TCP ports, not just nmap's top 1,000 default, so no odd service is missed.|
|`--min-rate 5000`|Send at least 5,000 packets/sec; counters the ~230 ms VPN latency that would otherwise make a full sweep crawl.|
|`-Pn`|Skip host-discovery ping and treat the host as up; reachability was already proven in 1.1.|
|`\| grapo`|Custom zsh helper: tees nmap output to the terminal and emits the open ports as a comma-separated list for reuse in the next scan.|

**Result:**

```
Not shown: 65533 closed tcp ports (reset)
PORT     STATE SERVICE
22/tcp   open  ssh
3389/tcp open  ms-wbt-server

Nmap done: 1 IP address (1 host up) scanned in 39.75 seconds

22,3389
```

**What this gives you:**

Key findings:

- Only two TCP ports are open across the full range: 22 (ssh) and 3389 (ms-wbt-server).
- `grapo` emits `22,3389` as a ready-to-paste port list for the targeted scan.
- A very small external surface with no web port is an early sign the real targets sit on an internal segment (pivoting).

**Next:** Run a version and default-script scan against only the two open ports to fingerprint the services and lock down the OS.
<div align="center">
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
</div>

#### 1.4.2 Fingerprint services and OS on open ports

**Command:**

```bash
nmap -A -p 22,3389 TARGET_IP
```

**Breakdown:**

|Component|Reasoning|
|---|---|
|`nmap -A`|Aggressive scan: enables `-sV` version detection, `-sC` default scripts, OS detection, and traceroute in one flag.|
|`-p 22,3389`|Restrict the heavy scan to the two confirmed-open ports from 1.2, keeping it fast.|

**Result:**

```
PORT     STATE SERVICE       VERSION
22/tcp   open  ssh           OpenSSH 9.6p1 Ubuntu 3ubuntu13.19 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey:
|   256 0c:4b:d2:76:ab:10:06:92:05:dc:f7:55:94:7f:18:df (ECDSA)
|_  256 2d:6d:4a:4c:ee:2e:11:b6:c8:90:e6:83:e9:df:38:b0 (ED25519)
3389/tcp open  ms-wbt-server Microsoft Terminal Service
Warning: OSScan results may be unreliable because we could not find at least 1 open and 1 closed port
Running: Linux 4.X|5.X, MikroTik RouterOS 7.X
OS details: Linux 4.15 - 5.19, MikroTik RouterOS 7.2 - 7.5 (Linux 5.6.3)
Network Distance: 2 hops
Service Info: OSs: Linux, Windows; CPE: cpe:/o:linux:linux_kernel, cpe:/o:microsoft:windows
```
<div align="center">
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
</div>

#### 1.4.3 Scan Results Analysis

|Port|Service|Version|Analysis|Simple Explanation|
|---|---|---|---|---|
|22/tcp|ssh|OpenSSH 9.6p1 Ubuntu 3ubuntu13.19|Ubuntu banner confirms Linux; SSH is restricted on this box, so not the intended entry despite having creds.|The normal remote-login door. It's locked to us here, so we don't use it to get in.|
|3389/tcp|ms-wbt-server|Microsoft Terminal Service (xrdp)|RDP on Linux = xrdp; PAM-backed graphical desktop. Supplied creds `contractor / Contractor2026!` target this.|A "remote screen" door. On Linux this is xrdp, giving a full graphical desktop instead of a text shell. This is our way in.|

**What this gives you:**

Key findings:

- Target OS is Ubuntu Linux, confirmed by the OpenSSH banner. The conflicting "MikroTik RouterOS" OS-detection guess is flagged unreliable by nmap's own warning (no open+closed port pair for the fingerprint) and is discarded.
- RDP on a Linux host indicates xrdp; because xrdp authenticates against local PAM, the handed-out RDP credentials are also local user credentials.
- Absence of any external web service (no 80/443) confirms the target web application lives on an unreachable internal segment, consistent with a pivoting engagement.

**Next:** Use the supplied `contractor / Contractor2026!` credentials against xrdp on 3389 to land a graphical foothold on the workstation; SSH is restricted, so RDP is the intended entry.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## 2. Initial Access: Foothold via RDP (xrdp)

### Connect to the Linux desktop as contractor:

**Why this step:** Recon showed xrdp on 3389 and supplied `contractor / Contractor2026!`, with SSH not accepting this account. RDP is the intended door, so use it to land a graphical session on the workstation.

**Command:**

bash

```bash
xfreerdp3 /v:TARGET_IP /u:contractor /p:'Contractor2026!' /cert:ignore /dynamic-resolution /sec:tls
```

**Breakdown:**

|Component|Reasoning|
|---|---|
|`xfreerdp3`|FreeRDP 3 command-line RDP client. Every option is a single unbroken `/flag:value` token; a space after the colon splits the argument and aborts with "Unsupported command line syntax."|
|`/v:TARGET_IP`|The victim host to connect to.|
|`/u:contractor`|Username supplied by HTB.|
|`/p:'Contractor2026!'`|Password, single-quoted so Bash treats `!` literally instead of triggering history expansion. No space between `/p:` and the value.|
|`/cert:ignore`|xrdp presents a self-signed certificate Kali does not trust; connect anyway rather than aborting on validation.|
|`/dynamic-resolution`|Allow the RDP window to resize dynamically, keeping the laggy desktop workable.|
|`/sec:tls`|Force TLS security negotiation, which modern xrdp expects.|

**Result:** Session established. Title bar shows `FreeRDP: TARGET_IP`; desktop is XFCE logged in as `contractor`. Log output confirms a successful connect (framebuffer init, dynamic virtual channels `ainput` / `rdpgfx` / `disp` / `rdpsnd` loaded); the `/p is insecure`, `/cert:ignore` DANGER, and `BB_ERROR_BLOB` license warnings are benign and expected against xrdp.

![[layover_rdp_desktop.png]]

**What this gives you:**

Key findings:

- Graphical foothold as the `contractor` user on the workstation (host `airside-ws01`, to be confirmed at a terminal prompt).
- The desktop is Linux XFCE served by xrdp, giving GUI access (useful later for the Wi-Fi network applet) but not a fast shell.

**Next:** Open a terminal in the Xfce session and check `sudo -l` to assess local privilege on the workstation before doing any heavier work.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## 3. Privilege Escalation (Workstation): sudo misconfiguration → root

### 3.1 Enumerate sudo rights for contractor:

**Why this step:** With a shell as `contractor` on airside-ws01 (2.1), the fastest local-privilege check is the sudo policy. A permissive entry is the most common instant-win on Linux.

**Command:**

```bash
sudo -l
```

**Breakdown:**

|Component|Reasoning|
|---|---|
|`sudo -l`|List the sudo privileges granted to the current user, as defined in `/etc/sudoers`, without running anything. Prompts for the user's own password on first use.|

**Result:**

```
Matching Defaults entries for contractor on airside-ws01:
    env_reset, mail_badpass, secure_path=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/snap/bin, use_pty

User contractor may run the following commands on airside-ws01:
    (ALL : ALL) ALL
```

**What this gives you:**

Key findings:

- `contractor` may run `(ALL : ALL) ALL`: any command, as any user, as any group, on this host. This is full administrative control.
- Escalation requires only contractor's own password (already known), with no restriction on the command.

###### Reading the sudoers grant:

The entry `(ALL : ALL) ALL` has three fields. The first `ALL` is the set of users the command may be run as (any user, root included). The `ALL` inside the parentheses is the set of groups it may be run as. The final `ALL` is the set of permitted commands. All three being `ALL` means the user can execute any command as anyone, which is equivalent to unrestricted root.

**Next:** Invoke a root shell with `sudo su` to take full control of the workstation, then use that access to enumerate network interfaces for the pivot.
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

