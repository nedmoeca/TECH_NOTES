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

