---
link: https://app.hackthebox.com/machines/Management?sort_by=created_at&sort_type=desc
difficulty: Easy
os: Linux
pov: red
release date: 2026-09-12
tags:
  - HTB
  - MACHINE
image: https://cdn.services-k8s.prod.aws.htb.systems/content/machines/avatar/a261b8b2-9dd5-4958-aaac-ca53661ab002-1785405942.png
solved:
solve date:
machine no.:
---

<div style="text-align: center; padding: 80px 40px; page-break-after: always;">

  <img src="/ASSETS/writeup_hack_the_box_logo.png" style="width: 1220px; margin-bottom: 60px;" />

  <div><p style="font-size: 40px; font-weight: 600; margin-bottom: 40px;">Management Writeup</p></div>

  <img src="https://cdn.services-k8s.prod.aws.htb.systems/content/machines/avatar/a261b8b2-9dd5-4958-aaac-ca53661ab002-1785405942.png" style="width: 400px; margin-bottom: 60px;" />

  <div style="font-size: 22px; line-height: 2.2;">
    <p style="margin: 0;">Prepared by: <a href="https://app.hackthebox.com/users/1809572">nedmoeca</a></p>
    <p style="margin: 0;">Author: <a href="https://app.hackthebox.com/users/114053">TheCyberGeek</a></p>
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
|                   |                     |                                                                                                                                                                                                                                                    |

**Result:**

```shell
PORT      STATE SERVICE
22/tcp    open  ssh
80/tcp    open  http
443/tcp   open  https
1689/tcp  open  firefox
4444/tcp  open  krb524
37441/tcp open  unknown
50389/tcp open  unknown

Nmap done: 1 IP address (1 host up) scanned in 31.45 seconds
```
<div align="center">
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
</div>

#### 1.4.2 Fingerprint the seven services

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
22/tcp    open  ssh       OpenSSH 9.6p1 Ubuntu 3ubuntu13.19 (protocol 2.0)
80/tcp    open  http      nginx 1.24.0 (Ubuntu)  -> redirect to https://management.htb/
443/tcp   open  ssl/http  nginx 1.24.0 (Ubuntu)
|  ssl-cert: Subject: CN=management.htb / O=Management Managed Services Ltd
|  Subject Alternative Name: DNS:management.htb, DNS:*.management.htb
1689/tcp  open  java-rmi  Java RMI
|  rmi-dumpregistry: org.opends.server.protocols.jmx.client-unknown
|    javax.management.remote.rmi.RMIServerImpl_Stub  @127.0.1.1:38591
4444/tcp  open  ssl/krb524?  (OpenDJ Administration Connector)
|  ssl-cert: Subject: CN=sso.management.htb / O=Administration Connector RSA Self-Signed Certificate
|  fingerprint: LDAPSearchReq ... ds-root-dse ... ds-cfg-root-dse-backend   (LDAPS)
38591/tcp open  java-rmi  Java RMI
50389/tcp open  ldap      (Anonymous bind OK)
```
<div align="center">
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
</div>

#### 1.4.3 Scan Results Analysis

| Port  | Service  | Version                | Analysis                                                                          | Simple Explanation                                                                        |
| ----- | -------- | ---------------------- | --------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------- |
| 22    | SSH      | OpenSSH 9.6p1          | Modern, no public RCE. Credential-only entry point.                               | The front door. Useless until we find a username and password.                            |
| 80    | HTTP     | nginx 1.24.0           | 301 to `https://management.htb/`. Confirms name-based vhosting.                   | Plain web port that just bounces you to the secure one and reveals the real hostname.     |
| 443   | HTTPS    | nginx 1.24.0           | Main site. Cert SAN is wildcard `*.management.htb`.                               | The real website. Its ID card admits other subdomains exist but won’t name them.          |
| 1689  | Java RMI | OpenDJ JMX             | Registry dump names OpenDJ, points to the dynamic RMI port. Refuses unauth use.   | A management channel for the directory server. Locked, but it confirms what’s running.    |
| 4444  | LDAPS    | OpenDJ Admin Connector | Secure admin endpoint, refuses anonymous ops. Cert CN leaks `sso.management.htb`. | A locked admin line, but its certificate accidentally prints the hidden subdomain’s name. |
| 38591 | Java RMI | (dynamic)              | Secondary JMX endpoint tied to the JVM. Changes each reboot. Noise.               | A second locked management channel. Ignore it.                                            |
| 50389 | LDAP     | OpenDJ config store    | Anonymous bind accepted. Non-standard port. The reconnaissance jackpot.           | The directory database lets strangers connect without a password. Worth a closer look.    |
<div align="center">
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
</div>

###
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

