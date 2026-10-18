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

