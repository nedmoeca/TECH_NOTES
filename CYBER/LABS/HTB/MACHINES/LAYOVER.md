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

```
<div align="center">
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
</div>

#### 1.4.3 Scan Results Analysis

| Port | **Service** | **Version** | **Analysis** | **Simple Explanation** |
| ---- | ----------- | ----------- | ------------ | ---------------------- |
|      |             |             |              |                        |
|      |             |             |              |                        |
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## 2. Enumeration
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## 3. Exploitation
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

