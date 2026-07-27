---
link: https://app.hackthebox.com/machines/DarkZeroReturns?sort_by=created_at&sort_type=desc
description: Hard·Windows
release date: 2026-07-25
tags:
  - SN_11
image: https://cdn.services-k8s.prod.aws.htb.systems/content/machines/avatar/a1fb32a5-8e1c-4d62-bf6e-d2041d6448ad-1781002585.png
solved:
solve date:
machine no.: 10
---

<div style="text-align: center; padding: 80px 40px; page-break-after: always;">

  <img src="/ASSETS/writeup_hack_the_box_logo.png" style="width: 1220px; margin-bottom: 60px;" />

  <div><p style="font-size: 40px; font-weight: 600; margin-bottom: 40px;">DarkZeroReturns Writeup</p></div>

  <img src="https://cdn.services-k8s.prod.aws.htb.systems/content/machines/avatar/a1fb32a5-8e1c-4d62-bf6e-d2041d6448ad-1781002585.png" style="width: 400px; margin-bottom: 60px;" />

  <div style="font-size: 18px; line-height: 2.2;">
    <p style="margin: 0;">Prepared by: nedmoeca</p>
    <p style="margin: 0;">Author(s): 0xEr3bus & Pho3o</p>
    <p style="margin: 0;">Difficulty: Hard</p>
    <p style="margin: 0;">Date: DD Month Year</p>
  </div>

</div>
<!-- PAGE BREAK -->

## Attack Chain Summary


<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
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

### 1.2 Verify Target is Reachable

VPN is established but unverified. Establish that the target answers before spending time on scans that would otherwise fail silently.

**Command:** `ping -c 4 TARGET_IP`

**Breakdown:**

| Component   | Purpose                  | Simple Explanation                                |
| ----------- | ------------------------ | ------------------------------------------------- |
| `ping`      | Sends ICMP echo requests | Asks "are you there?" and waits for a reply       |
| `-c 4`      | Stop after 4 packets     | Otherwise it runs forever until interrupted       |
| `TARGET_IP` | Destination host         | The HTB machine address assigned to your instance |

**Result:**

```shell
┌──(kali㉿kali)-[~]
└─$ ping -c 4 10.129.53.206
PING 10.129.53.206 (10.129.53.206) 56(84) bytes of data.
64 bytes from 10.129.53.206: icmp_seq=1 ttl=127 time=236 ms
64 bytes from 10.129.53.206: icmp_seq=2 ttl=127 time=234 ms
64 bytes from 10.129.53.206: icmp_seq=3 ttl=127 time=231 ms
64 bytes from 10.129.53.206: icmp_seq=4 ttl=127 time=242 ms

--- 10.129.53.206 ping statistics ---
4 packets transmitted, 4 received, 0% packet loss, time 3004ms
rtt min/avg/max/mdev = 231.415/235.706/241.509/3.743 ms
```

Zero packet loss confirms the VPN tunnel and target are both live.

**Key finding:** TTL 127 indicates an initial TTL of 128 decremented by a single hop. An initial TTL of 128 is the Windows default; Linux defaults to 64. Treat the host as Windows-family for now and revisit if service banners contradict it.

**Next:** With reachability confirmed, enumerate the full TCP port range to establish the exposed attack surface.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## 2. Enumeration

### 2.1 Port Scan with Nmap

#### 2.1.1 Full Port Sweep

Reachability is confirmed but the attack surface is unknown. Scan the full port range rather than nmap's default top 1000, since a service on a high port is a common way for boxes to hide their real entry point.

**Command:** `nmap -p- --min-rate 5000 -Pn TARGET_IP | grapo`

**Breakdown:**

| Component         | Purpose                        | Simple Explanation                                                                                                             |
| ----------------- | ------------------------------ | ------------------------------------------------------------------------------------------------------------------------------ |
| `nmap`            | Port scanner                   | Knocks on every door and notes which ones open                                                                                 |
| `-p-`             | Scan ports 1–65535             | The full range, not just the common ones                                                                                       |
| `--min-rate 5000` | Send at least 5000 packets/sec | Forces speed; a full-range scan at default rate takes many minutes                                                             |
| `-Pn`             | Skip host discovery            | Treat the host as up without pinging first — already verified manually                                                         |
| `TARGET_IP`       | Target                         | The HTB machine                                                                                                                |
| `\| grapo`        | Custom zsh function            | Prints full nmap output to the terminal while extracting open ports as a comma-joined list for copying into the follow-up scan |

**Result:**

```shell
┌──(kali㉿kali)-[~]
└─$ nmap -p- --min-rate 5000 -Pn 10.129.53.206 | grapo              
Starting Nmap 7.98 ( https://nmap.org ) at 2026-07-27 06:59 +0000
Nmap scan report for 10.129.53.206
Host is up (0.46s latency).
Not shown: 65533 filtered tcp ports (no-response)
PORT   STATE SERVICE
22/tcp open  ssh
80/tcp open  http

Nmap done: 1 IP address (1 host up) scanned in 29.33 seconds

22,80
```

Only 22/tcp (SSH) and 80/tcp (HTTP) are exposed. No SMB (445), no LDAP (389), no Kerberos (88) — none of the ports that normally advertise a Windows domain controller.

**Next:** Fingerprint both services to identify software and versions before probing the web application.
<div align="center">
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
</div>

#### 2.1.2 The "Deep Dive" Scan (Targeted Aggression)

Two ports are confirmed open but the software behind them is unknown. Run service and version detection against only those ports to identify software, versions, and any immediate script findings.

**Command:** `nmap -A -p p1,p2,p3,p4 TARGET_IP`

**Breakdown:**

| Component   | Purpose                 | Simple Explanation                                                                                                   |
| ----------- | ----------------------- | -------------------------------------------------------------------------------------------------------------------- |
| `nmap`      | Port scanner            | The scanning tool                                                                                                    |
| `-A`        | Aggressive mode         | That's a superset; Bundles four things at once: version detection, default NSE scripts, OS detection, and traceroute |
| `-p 22,80`  | Restrict to these ports | Only the ports the full scan found open — no wasted time                                                             |
| `TARGET_IP` | Target                  | The HTB machine                                                                                                      |
(`-A` is equivalent to `-sC -sV -O --traceroute` combined.)

**Result:**

```shell
┌──(kali㉿kali)-[~]
└─$ nmap -A -p 22,80 10.129.53.206                                                                                                    
Starting Nmap 7.98 ( https://nmap.org ) at 2026-07-27 07:05 +0000
Nmap scan report for 10.129.53.206
Host is up (0.23s latency).

PORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH 9.6p1 Ubuntu 3ubuntu13.18 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   256 0c:4b:d2:76:ab:10:06:92:05:dc:f7:55:94:7f:18:df (ECDSA)
|_  256 2d:6d:4a:4c:ee:2e:11:b6:c8:90:e6:83:e9:df:38:b0 (ED25519)
80/tcp open  http    nginx 1.24.0 (Ubuntu)
|_http-server-header: nginx/1.24.0 (Ubuntu)
|_http-title: Did not follow redirect to http://dzcampaigns.htb/
Warning: OSScan results may be unreliable because we could not find at least 1 open and 1 closed port
Device type: general purpose
Running (JUST GUESSING): Microsoft Windows 2022|2012|2016 (88%)
OS CPE: cpe:/o:microsoft:windows_server_2022 cpe:/o:microsoft:windows_server_2012:r2 cpe:/o:microsoft:windows_server_2016
Aggressive OS guesses: Microsoft Windows Server 2022 (88%), Microsoft Windows Server 2012 R2 (85%), Microsoft Windows Server 2016 (85%)
No exact OS matches for host (test conditions non-ideal).
Network Distance: 2 hops
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel

TRACEROUTE (using port 80/tcp)
HOP RTT       ADDRESS
1   244.38 ms 10.10.14.1
2   244.41 ms 10.129.53.206

OS and Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 26.90 seconds
```
<div align="center">
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
</div>

#### 2.1.3 Scan Results Analysis

| Port   | Service | Version                           | Analysis                                                                                 | Simple Explanation                                                        |
| ------ | ------- | --------------------------------- | ---------------------------------------------------------------------------------------- | ------------------------------------------------------------------------- |
| 22/tcp | SSH     | OpenSSH 9.6p1 Ubuntu 3ubuntu13.18 | Current release, no known exploitable CVEs. No entry point without credentials.          | Remote login for Linux. Useless until a username and password turn up.    |
| 80/tcp | HTTP    | nginx 1.24.0 (Ubuntu)             | Reverse proxy. Redirects to a named vhost, so the real app is not served on the bare IP. | The web server. It won't show the real site until you ask for it by name. |
**Key findings:** 

- The host serving both ports is Ubuntu Linux, contradicting nmap's Windows OS guess. The OS fingerprint carries an explicit reliability warning — with 65533 ports filtered, nmap lacked the open/closed port pair it needs for accurate stack fingerprinting. Trust the service banners over the guess: the edge host is Linux, and the Windows signals belong to infrastructure behind it.

- nginx redirects to the virtual host `dzcampaigns.htb`. Resolve this name locally before any web enumeration, or every request returns the redirect instead of the application.

One web server can host many different websites on a single IP address. The way it decides which site to serve is the `Host` header — a line your browser sends with every request saying which name you typed. Request `dzcampaigns.htb` and nginx serves the campaign application; request the bare IP address and nginx has no matching site configuration, so it redirects you to the name it expects.

The problem is that `dzcampaigns.htb` isn't a real registered domain. Public DNS has never heard of it, so your machine can't resolve it to an address and the redirect goes nowhere.

The fix is `/etc/hosts`, a plain text file your system consults _before_ asking DNS. Adding a line there that maps `dzcampaigns.htb` to the target IP means your browser resolves the name locally, sends the correct `Host` header, and nginx serves the real application. This is a routine first move on almost every HTB web box — whenever a scan mentions a `.htb` domain, that domain goes in `/etc/hosts` immediately.

**Next:** Map the virtual host name to the target IP locally so the application becomes reachable.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
<br>
</div>

### 2.2 Resolve the virtual host locally

Nginx redirects requests for the bare IP to `dzcampaigns.htb`, a name public DNS cannot resolve. Map the name to the target address in the local hosts file so requests carry the correct `Host` header and reach the application.

**Command**

```bash
sudo vi /etc/hosts
```

Append the following line:

```
TARGET_IP    dzcampaigns.htb
```

**Breakdown**

|Component|Purpose|Simple Explanation|
|---|---|---|
|`sudo`|Elevate privileges|`/etc/hosts` is system-owned and not writable by a normal user|
|`vi`|Text editor|Opens the file for editing|
|`/etc/hosts`|Local resolution table|Consulted before DNS; maps IP addresses to hostnames|
|`TARGET_IP dzcampaigns.htb`|The mapping entry|Sends any request for that name to the target machine|

Note the format: address first, then one or more names separated by whitespace. No protocol scheme, no port, no path — the file resolves names to addresses and nothing more.

**Verify**

```bash
curl -I http://dzcampaigns.htb/
```

| Component | Purpose                  | Simple Explanation                                                                                 |
| --------- | ------------------------ | -------------------------------------------------------------------------------------------------- |
| `curl`    | Command-line HTTP client | Fetches a URL without a browser                                                                    |
| `-I`      | HEAD request only        | Returns response headers and skips the page body — fast confirmation the host resolves and answers |

**Result**

```shell
┌──(kali㉿kali)-[~]
└─$ curl -I http://dzcampaigns.htb/                                                                                                   
HTTP/1.1 200 OK
Server: nginx/1.24.0 (Ubuntu)
Date: Mon, 27 Jul 2026 15:04:02 GMT
Content-Type: text/html; charset=utf-8
Content-Length: 2344
Connection: keep-alive
ETag: W/"928-OsnbcztKl7ijbe9shRmPWv/KaWM"
Set-Cookie: dz.sid=s%3A3Ku4I0ZOarjEdq2eSHLVXwAC8bL_ukEw.VdbqE3O8Q%2BoZvw0c8lnMtVDzvxpwOzYf16Ysxi8cV24; Path=/; Expires=Tue, 28 Jul 2026 15:04:02 GMT; HttpOnly; SameSite=Lax
```

HTTP 200 replaces the earlier redirect — the virtual host now resolves and the application responds.

**Next:** Browse the application to identify functionality, authentication endpoints, and user-controllable input.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
<br>
</div>

### 2.3 Web Enumeration
#### 2.3.1 Enumerate application functionality as an unauthenticated user

The application responds on the resolved vhost but its purpose and input surface are unknown. Browse every page reachable without credentials to map functionality before attempting authentication.

**Action**

Open the following in a browser:

- http://dzcampaigns.htb/
- http://dzcampaigns.htb/essentials
- http://dzcampaigns.htb/dice
- http://dzcampaigns.htb/login


**Result:**

`/` — "DarkZero Campaigns", a tabletop RPG campaign tracker. Displays ACTIVE CAMPAIGNS with a single entry, "The Clockwork Moon and the Thieves of Dawn", plus its narrative description, and a RECENT HEROES section listing one character: `Thomas — Goblin Guardian`.

![[dzcampaigns_home.png]]

`/essentials` — Documentation covering campaigns, character creation, inventory, dice, and a Coming Soon list.

![[dzcampaigns_essentials.png]]

`/dice` — Dice roller: DIE selector (default "6 sided"), COUNT field (default 1), ROLL button.

![[dzcampaigns_dice.png]]

http://dzcampaigns.htb/login

![[dzcampaigns_login.png]]

**Key finding:** The navigation bar exposes only four destinations and no registration link, yet the Essentials workflow lists "Register or log in" as step 1. Account creation exists but is unlinked from the UI.

**Endpoint map (unauthenticated)**

| Path          | Nav label  | Function                                 | Input surface                      | Simple Explanation                            |
| ------------- | ---------- | ---------------------------------------- | ---------------------------------- | --------------------------------------------- |
| `/`           | HOME       | Lists active campaigns and recent heroes | None                               | The front page — shows what's going on        |
| `/essentials` | ESSENTIALS | Application documentation                | None                               | A help page explaining the app's own features |
| `/dice`       | ROLL DICE  | Server-side dice roller                  | Die type (select), count (numeric) | Rolls dice for you; only accepts numbers      |
| `/login`      | LOGIN      | Authentication form                      | Email, password                    | Where you sign in                             |

**Next:** Locate the unlinked registration endpoint and create an account to reach the authenticated character-creation flow.
<div align="center">
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
</div>

#### 2.3.2 Register an account and authenticate

Navigate to the login page and follow the registration link in the body text beneath the form:

![[dzcampaigns_login_register_here.png]]

Submit the registration form by clicking on 'Create Account' after entering the required details.

![[dzcampaigns_register.png]]

Registration redirects to `/login`. Authenticate with the same email and password.

**Result:**

Login succeeds and redirects to `/dashboard`:

![[dzcampaigns_dashboard.png]]

Registration is open, unverified, and requires no invitation or approval. Any unauthenticated attacker can self-provision an account.

**Next:** Open the character-creation form and enumerate its fields, paying particular attention to any field whose contents are rendered into campaign output.
<div align="center">
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
</div>

#### 2.3.3 Enumerate the character creation form

Authentication is established and the dashboard exposes a CREATE CHARACTER action. Inspect every field on the form before submitting anything, to identify which inputs are treated as data and which are treated as instructions.

![[dzcampaigns_character_new.png]]

**Key findings:**

- The CUSTOM CAMPAIGN MESSAGE field accepts a **template**, not a value. Its own placeholder text demonstrates the syntax — `{{race}}`, `{{class}}`, `{{name}}` — which is Mustache-family templating. In a Node.js/Express application, the dominant implementation of that syntax is Handlebars.js. The application permits a user to supply the template that the server will compile and render. This inverts the safe arrangement described in 1.5.1 and makes server-side template injection the primary attack path.

- The message field is visually disabled with the annotation "available once a campaign is chosen". Field disabling is enforced in the browser via the HTML disabled attribute. It prevents interaction in the UI but does not prevent the parameter from being included in a crafted HTTP request. Treat the gate as advisory only.

**Note:** The default template references `{{race}}`, `{{class}}`, and `{{name}}` — the same three fields present above it. This confirms the four data fields are passed into the rendering context, meaning the template executes with access to a context object populated from user input.
<div align="center">
<br>
<br>
</div>

##### Theory — Handlebars, and what "compiling a template" means

Handlebars is a templating engine for JavaScript. You hand it a template string and a context object, and it hands you back finished text.

```
Template:  "Hello {{name}}, welcome to {{place}}."
Context:   { name: "Ned", place: "Virelia" }
Output:    "Hello Ned, welcome to Virelia."
```

The important part is _how_ it does this. Handlebars does not perform a simple find-and-replace. It runs the template through two stages:

1. **Parse.** The template string is read and converted into an **AST** — an Abstract Syntax Tree. This is a structured object describing what the template means: "here is literal text", "here is a mustache statement that looks up the variable `name`", "here is a block helper". The braces are gone by this point; what remains is a tree of typed nodes.
2. **Compile and execute.** The AST is walked and turned into an actual JavaScript function, which is then called with the context object to produce output.

Stage 2 is the dangerous one, because "turned into an actual JavaScript function" means the contents of the AST end up as executable code inside the Node.js process. Handlebars normally guards this carefully — the parser only ever produces well-formed nodes, so nothing unexpected can reach the code generator.

That guarantee holds only as long as the AST comes from the parser. If an attacker can supply the AST **directly**, skipping the parse stage, they can construct nodes the parser would never emit — nodes containing arbitrary JavaScript in fields the compiler expects to hold simple values. That is the shape of the vulnerability on this box, and it is why the next few steps focus on how the message field is transmitted rather than just what text it accepts.

**Next:** Submit a character joining the campaign with the default message intact, to establish baseline rendering behaviour and locate where the output appears.
<div align="center">
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
</div>

####
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## 3. Exploitation
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## 4. Post-Exploitation
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## 5. PrivEsc
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## 6. Lessons Learned
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->

## 7. Remediation Recommendations
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## References

