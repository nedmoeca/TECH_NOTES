---
link: https://app.hackthebox.com/machines/BlockSynergy
difficulty: Insane
os: Linux
release date: 2026-08-29
tags:
  - SN_11
image: https://cdn.services-k8s.prod.aws.htb.systems/content/machines/avatar/a29813ab-2643-4f77-80fd-65500f97bcd0-1787750589.png
solved:
solve date:
machine no.: 13
---

<div style="text-align: center; padding: 80px 40px; page-break-after: always;">

  <img src="/ASSETS/writeup_hack_the_box_logo.png" style="width: 1220px; margin-bottom: 60px;" />

  <div><p style="font-size: 40px; font-weight: 600; margin-bottom: 40px;">BlockSynergy Writeup</p></div>

  <img src="https://cdn.services-k8s.prod.aws.htb.systems/content/machines/avatar/a29813ab-2643-4f77-80fd-65500f97bcd0-1787750589.png" style="width: 400px; margin-bottom: 60px;" />

  <div style="font-size: 22px; line-height: 2.2;">
    <p style="margin: 0;">Prepared by: nedmoeca</p>
    <p style="margin: 0;">Author(s): R00cKet</p>
    <p style="margin: 0;">Difficulty: Insane</p>
    <p style="margin: 0;">Date: 29 Aug 2026</p>
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

### 1.3 Verify Target is Reachable

Verify that the target machine is up and reachable by performing an ICMP ping test.

**Command:** `ping -c 4 TARGET_IP`

**Breakdown:**

- `-c 4` → sends 4 packets only (clean output, fast)

**Result:**

```shell
┌──(nedmoeca㉿kali)-[~/Labs/HTB/SN11/BlockSynergy]
└─$ ping -c 4 $IP           
PING 10.129.115.174 (10.129.115.174) 56(84) bytes of data.
64 bytes from 10.129.115.174: icmp_seq=1 ttl=63 time=246 ms
64 bytes from 10.129.115.174: icmp_seq=2 ttl=63 time=344 ms
64 bytes from 10.129.115.174: icmp_seq=3 ttl=63 time=263 ms
64 bytes from 10.129.115.174: icmp_seq=4 ttl=63 time=203 ms

--- 10.129.115.174 ping statistics ---
4 packets transmitted, 4 received, 0% packet loss, time 3004ms
rtt min/avg/max/mdev = 202.548/264.052/344.111/51.246 ms
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
┌──(nedmoeca㉿kali)-[~/Labs/HTB/SN11/BlockSynergy]
└─$ nmap -p- --min-rate 5000 -Pn $IP | grapo
Starting Nmap 7.99 ( https://nmap.org ) at 2026-09-05 11:02 -0400
Nmap scan report for 10.129.115.174
Host is up (0.21s latency).
Not shown: 65533 closed tcp ports (reset)
PORT     STATE SERVICE
22/tcp   open  ssh
8080/tcp open  http-proxy

Nmap done: 1 IP address (1 host up) scanned in 21.75 seconds

22,8080
```

A two-port surface with SSH and a single web service rules out lateral entry through file shares, databases, or mail services. The web service on 8080 is the only realistic entry point, since SSH without credentials offers nothing to attack.
<div align="center">
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
</div>

#### 1.4.2 The "Deep Dive" Scan (Targeted Aggression)

**Command:** `nmap -A -p p1,p2,p3,p4 TARGET_IP`

**Breakdown:**

- **`-A`**
    - **Description:** Aggressive Scan Mode.
    - **Purpose:** Enables OS detection, version detection, script scanning (`-sC`), and traceroute all at once.
- `-p`
    - **Description:** Targeted Port List.
    - **Purpose:** Restricts the heavy scanning to only the ports you confirmed are open, saving significant time and processing power.

> Version detection is not passive observation. Nmap opens a real connection to each port and sends a sequence of probes designed to elicit identifying responses, then matches the replies against a database of known service signatures. Many services announce themselves unprompted. SSH sends its version string immediately on connect, and HTTP servers often include a `Server:` header which is why banners are frequently the highest-value output of a scan.
> 
> The default script set (`-sC`, included in `-A`) then runs safe, non-intrusive NSE scripts against whatever was identified. For HTTP that includes retrieving the page title and server header; for SSH it includes collecting host key fingerprints. These scripts do not attempt exploitation.

**Result:**

```shell
┌──(nedmoeca㉿kali)-[~/Labs/HTB/SN11/BlockSynergy]
└─$ nmap -A -p 22,8080 $IP   
Starting Nmap 7.99 ( https://nmap.org ) at 2026-09-05 11:03 -0400
Nmap scan report for 10.129.115.174
Host is up (0.22s latency).

PORT     STATE SERVICE VERSION
22/tcp   open  ssh     OpenSSH 9.6p1 Ubuntu 3ubuntu13.18 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   256 0b:93:57:66:c8:a4:f0:85:6a:d2:e1:a4:d5:f4:52:81 (ECDSA)
|_  256 aa:38:b7:38:85:1d:21:1e:db:0a:15:8b:c8:a4:03:92 (ED25519)
8080/tcp open  http    Werkzeug httpd 3.1.3 (Python 3.12.3)
|_http-server-header: Werkzeug/3.1.3 Python/3.12.3
|_http-title: BlockSynergy \xE2\x80\x93 Decentralized Future
Warning: OSScan results may be unreliable because we could not find at least 1 open and 1 closed port
Device type: general purpose|router
Running: Linux 4.X|5.X, MikroTik RouterOS 7.X
OS CPE: cpe:/o:linux:linux_kernel:4 cpe:/o:linux:linux_kernel:5 cpe:/o:mikrotik:routeros:7 cpe:/o:linux:linux_kernel:5.6.3
OS details: Linux 4.15 - 5.19, MikroTik RouterOS 7.2 - 7.5 (Linux 5.6.3)
Network Distance: 2 hops
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel

TRACEROUTE (using port 80/tcp)
HOP RTT       ADDRESS
1   246.52 ms 10.10.14.1
2   246.78 ms 10.129.115.174

OS and Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 19.60 seconds
```
<div align="center">
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
</div>

#### 1.4.3 Scan Results Analysis

| Port | Service | Version                              | Analysis                                                                                                                                                                                                                                                                  | Simple Explanation                                                                                                                      |
| ---- | ------- | ------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------- |
| 22   | ssh     | OpenSSH 9.6p1 Ubuntu 3ubuntu13.18    | Current and patched. No known exploitable vulnerability at this version. The Ubuntu package suffix identifies the distribution as Ubuntu 24.04 LTS. Useful only once credentials or a private key are obtained.                                                           | Remote login service. Nothing to attack without a username and password or key, but it becomes a way in the moment either is recovered. |
| 8080 | http    | Werkzeug httpd 3.1.3 (Python 3.12.3) | Werkzeug is the WSGI library underlying Flask. A bare Werkzeug banner means the Flask development server is exposed directly rather than sitting behind gunicorn or nginx, which would normally mask it. Indicates hand-written application code, not a packaged product. | A Python web application running in its built-in development mode. There is no vendor product here to look up a public exploit for.     |

**Key findings:**

- Port 8080 serves a custom Python/Flask application titled **BlockSynergy – Decentralized Future**.
- The exposed Werkzeug development server confirms custom application logic; the attack path will consist of application logic flaws rather than a CVE against known software.
- The host is Ubuntu Linux, per the OpenSSH package string.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## 2. Web Enumeration

### 2.1 Review the application landing page

Port 8080 runs custom Flask code, so there is no vendor documentation to consult and no CVE to look up. Read the application's own public-facing content first. On a bespoke application the landing page frequently states the business rules and API contracts that define the attack surface.

**Command:**

```bash
firefox http://TARGET_IP:8080/ &
```

**Breakdown:**

| Component | Purpose                | Simple Explanation                                                                                                                                                  |
| --------- | ---------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `firefox` | Browser                | Renders JavaScript and CSS, which `curl` does not. Use a browser for reconnaissance of a human-facing interface; use `curl` once the requests to be made are known. |
| `http://` | Scheme                 | Plaintext, confirmed in the nmap scan. Reported no `ssl/` prefix and emitted no certificate or cipher output.                                                       |
| `:8080`   | Port                   | Non-default HTTP port identified in 1.3.                                                                                                                            |
| `&`       | Background the process | Returns the shell prompt immediately instead of blocking until the browser exits.                                                                                   |

**Result:**

![[blocksynergy_landing.png]]

Page content, transcribed:

|Section|Stated content|
|---|---|
|Header|BlockSynergy — "Illuminating the Future of Decentralization." Single navigation control: **Dashboard** (top right).|
|Key Features|Secure Wallet Management; Mining & Earning Rewards; VIP Access & Exclusive Features; Coin Purchasing & Secure Trading (described as early development, not live); API Integrations; Active Development.|
|VIP Access|"What You Get as VIP": Node Management Access; Smart Contract Deployment (Coming Soon); Early Access to New Features. "How to Become VIP": **"Have at least 10 Coins in your Wallet to automatically unlock VIP status."**|
|How Mining Works|Badge: "Currently the ONLY way to earn coins!" Mining tasks generated from pending network transactions. Mining data available at the public endpoint **`/mining_data`**.|
|Submitting Blocks|Blocks are submitted to **`/submit_block`** with the JSON structure `{'address': your_address, 'block': your_block}`. "Rewards are issued as transactions. You must mine a new block containing the reward transaction to actually receive your coins."|
|Call to action|Create Wallet; Get Data for Mining; Become VIP.|

**What this gives you:**

**Key finding: VIP status is granted by a numeric wallet-balance threshold of 10 coins, not by an administrative role assignment.** Any mechanism that inflates a wallet balance therefore grants VIP privileges. VIP privileges include node registration, which is the application's only stated capability involving server-initiated network requests.

Three further facts to carry into enumeration:

The coin lifecycle is two-stage. A transaction is created and held in a pending pool; the balance only updates once a block containing that transaction is mined and accepted. Validation may be absent at either stage, and both stages must be examined independently.

Two API endpoints are documented publicly, before authentication: `/mining_data` (returns data needed to construct a block) and `/submit_block` (accepts attacker-constructed blocks). Client-submitted blocks are normal for a blockchain — the protection is meant to come from proof-of-work being computationally expensive. Whether that protection holds here depends on the difficulty value and on how completely the server validates a submitted block.

The claim that mining is the only way to earn coins is a design assumption, not an enforced control. Treat it as a hypothesis to disprove: if coins can be obtained by any other route, the balance check guarding VIP is bypassed.

Note the application handles wallets and financial transactions over plaintext HTTP with no TLS, exposing session cookies and wallet data to network interception. Recorded for the remediation section; not part of the exploitation path.

**Next:**  
The landing page names an "API Integrations" feature but enumerates only two endpoints. Access the Dashboard to obtain the application's full endpoint list.
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




