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

**Command:**

bash

```bash
echo "TARGET_IP paperwork.htb" | sudo tee -a /etc/hosts
curl -s http://paperwork.htb/
```

**Breakdown:**

- `echo "TARGET_IP paperwork.htb" | sudo tee -a /etc/hosts` — map the vhost name to the target so nginx serves the app instead of redirecting.
- `curl -s http://paperwork.htb/` — fetch the page body quietly (`-s` suppresses the progress meter).

**Result (rendered content):**

```
Department of Records & Archives — Intake Portal

Maintenance Advisory: Backend spooler PRN-ARCHIVE-01 management console is
currently offline. Manual ingestion remains active via the legacy gateway.

System Configuration
  Protocol:           Compliance Level: RFC 1179
  Target Queue:       archive_intake
  Internal Processor: paperwork-archive-v1.02   (rendered as a hyperlink)

Usage Notice: Remote job submission must conform to business requirements for
archival indexing. Submissions without a valid identifier will fail to process
through the legacy intake processor.

Internal Use Only © 2026 Corporate Digital Archiving Solutions v1.02
```

**What this gives you:** **Key finding:** the service on 1515 speaks **RFC 1179 (LPD)**, expects queue **`archive_intake`**, and demands a "valid identifier" on each job — a nudge toward the control-file job-name field. The "Internal Processor" is a live hyperlink, a likely pointer to the service's source.

**Next:** Inspect the page's links to locate the processor source referenced by the portal.
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

