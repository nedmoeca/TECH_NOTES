---
link: https://tryhackme.com/room/vulnversity
difficulty: Easy
team: red
description: Learn about active recon, web app attacks and privilege escalation.
tags:
image: https://cdn-images.tryhackme.com/room-icons/85dee7ce633f5668b104d329da2769c3.png
solved:
solve date:
---

<div style="text-align: center; padding: 80px 40px; page-break-after: always;">

  <img src="/ASSETS/writeup_try_hack_me_logo.png" style="width: 1220px; margin-bottom: 60px;" />

  <div><p style="font-size: 40px; font-weight: 600; margin-bottom: 40px;">Vulnversity Writeup</p></div>

  <img src="https://cdn-images.tryhackme.com/room-icons/85dee7ce633f5668b104d329da2769c3.png" style="width: 400px; margin-bottom: 60px;" />

  <div style="font-size: 22px; line-height: 2.2;">
    <p style="margin: 0;">Prepared by: <a href="https://tryhackme.com/p/nedmoeca">nedmoeca</a></p>
    <p style="margin: 0;">Author(s): <a href="https://tryhackme.com/p/1337rce">1337rce</a></p>
    <p style="margin: 0;">Difficulty: Easy</p>
    <p style="margin: 0;">Date: DD Month Year</p>
  </div>

</div>
<!-- PAGE BREAK -->

## Summary


<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## Task 1 Deploy the machine
### Q1 Deploy the machine.

==Answer== No answer needed
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## Task 2 Reconnaissance

Gather information about this machine using a network scanning tool called `Nmap`. Check out the [Nmap](https://tryhackme.com/room/furthernmap) room for more on this!

**Connecting to the machine**

This room recommends using the AttackBox, which can be launched by clicking the blue button on the top-right.

**Scan the box**

`nmap -sV 10.48.143.150`.

![](https://cdn-images.tryhackme.com/user-uploads/5e86dbbd98fde62929a7e03b/room-content/5e86dbbd98fde62929a7e03b-1759493375506.png)

Nmap is a free, open-source and powerful tool used to discover hosts and services on a computer network. In our example, we use Nmap to scan this machine to identify all services running on a particular port. Nmap has many capabilities; a table summarizes some of its functionality below.

| Nmap flag     | Description                                                                         |
| ------------- | ----------------------------------------------------------------------------------- |
| -sV           | Attempts to determine the version of the services running                           |
| -p <x> or -p- | Port scan for port <x> or scan all ports                                            |
| -Pn           | Disable host discovery and scan for open ports                                      |
| -A            | Enables OS and version detection, executes in-build scripts for further enumeration |
| -sC           | Scan with the default Nmap scripts                                                  |
| -v            | Verbose mode                                                                        |
| -sU           | UDP port scan                                                                       |
| -sS           | TCP SYN port scan                                                                   |
<div align="center">
<br>
<br>
</div>

### Q2 There are many Nmap "cheatsheets" online that you can use too.

==Answer== No answer needed
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
<br>
</div>

### Q3 Scan the box; how many ports are open?

==Answer== 6
<div align="center">
<br>
<br>
</div>

**Why this step:** Begin every engagement by learning which ports the target actually exposes. A default nmap scan only checks the top 1,000 ports; this box runs services on non-standard high ports, so a full sweep is mandatory before any assumptions.

**Command:**

```
nmap -p- --min-rate 5000 -Pn TARGET_IP
```

**Breakdown:**

|Component|Purpose|
|---|---|
|`nmap`|The network scanner.|
|`-p-`|Scan all 65,535 TCP ports, not just the default top 1,000.|
|`--min-rate 5000`|Send at least 5,000 packets/sec — trades stealth for speed on a lab box.|
|`-Pn`|Skip the initial ping/host-discovery probe; treat the host as up and scan directly.|
|`TARGET_IP`|The machine's IP (set to a shell variable during the engagement).|

**Result:**

```
Not shown: 65529 closed tcp ports (reset)
PORT     STATE SERVICE
21/tcp   open  ftp
22/tcp   open  ssh
139/tcp  open  netbios-ssn
445/tcp  open  microsoft-ds
3128/tcp open  squid-http
3333/tcp open  dec-notes

Nmap done: 1 IP address (1 host up) scanned in 19.09 seconds
```

|Port|Service (nmap guess)|Version|Analysis|Simple Explanation|
|---|---|---|---|---|
|21|ftp|_not yet enumerated_|File transfer; check for anonymous access.|A way to upload/download files — sometimes open to anyone.|
|22|ssh|_not yet enumerated_|Remote login; needs credentials, low priority now.|Remote control of the box — but you need a username/password.|
|139|netbios-ssn|_not yet enumerated_|SMB (older NetBIOS transport).|Windows-style file sharing.|
|445|microsoft-ds|_not yet enumerated_|SMB (modern transport); enumerate shares.|The main file-sharing service — worth poking at.|
|3128|squid-http|_not yet enumerated_|Squid web proxy.|A middle-man for web traffic.|
|3333|dec-notes|_not yet enumerated_|**Mislabelled** — 3333 is a non-standard port; the "dec-notes" name is just nmap's default guess. Almost certainly the web server.|The label is a guess based on the port number, not what's really running.|

**What this gives you:** Key finding - six open TCP ports, with a likely web application on the non-standard port **3333**. The `SERVICE` column here is inferred from port numbers only (no `-sV`), so the "dec-notes" label on 3333 must be verified, not trusted.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
<br>
</div>

### Q4 What version of the squid proxy is running on the machine?

==Answer== 4.10
<div align="center">
<br>
<br>
</div>

**Why this step:** The port sweep in 1.1 revealed _which_ ports are open but labelled them by guesswork. Fingerprint each one to learn the real software and version and to confirm what's actually running on the non-standard port 3333.

**Command:**

```
nmap -A -p 21,22,139,445,3128,3333 TARGET_IP
```

**Breakdown:**

|Component|Purpose|
|---|---|
|`nmap`|The network scanner.|
|`-A`|Aggressive mode — bundles version detection (`-sV`), default scripts (`-sC`), OS detection (`-O`), and traceroute in one pass.|
|`-p 21,22,139,445,3128,3333`|Limit the scan to the six ports found open in 1.1, so the deeper probes finish quickly.|
|`TARGET_IP`|The target machine.|

**Result:**

```
PORT     STATE SERVICE     VERSION
21/tcp   open  ftp         vsftpd 3.0.5
22/tcp   open  ssh         OpenSSH 8.2p1 Ubuntu 4ubuntu0.13 (Ubuntu Linux; protocol 2.0)
139/tcp  open  netbios-ssn Samba smbd 4
445/tcp  open  netbios-ssn Samba smbd 4
3128/tcp open  http-proxy  Squid http proxy 4.10
3333/tcp open  http        Apache httpd 2.4.41 ((Ubuntu))
|_http-title: Vuln University

Aggressive OS guesses: Linux 5.14 - 6.8 (96%) ...
Service Info: OSs: Unix, Linux
```

|Port|Service|Version|Analysis|Simple Explanation|
|---|---|---|---|---|
|21|ftp|vsftpd 3.0.5|Current release — **not** the backdoored 2.3.4. No known easy exploit.|The file-transfer service is up to date; no free way in.|
|22|ssh|OpenSSH 8.2p1 (Ubuntu)|Patched; needs valid credentials. Park it.|Remote login — useless without a username and password.|
|139/445|netbios-ssn|Samba smbd 4|SMB file sharing. Valid enumeration side-path (shares/users), not the intended route.|File sharing — worth a look, but not the main door here.|
|3128|http-proxy|Squid http proxy 4.10|A web proxy; no obvious foothold.|A traffic middle-man; nothing to exploit directly.|
|3333|http|Apache httpd 2.4.41 (Ubuntu)|**The target.** Confirmed web app, page title "Vuln University".|This is the website we attack.|

**What this gives you:** Key finding - the non-standard port **3333 runs an Apache web application** ("Vuln University"); the FTP and SSH versions are patched, ruling out quick service exploits. The web app is the primary attack surface.

**Next:** Brute-force the web app's directory structure on port 3333 to find non-linked pages; application entry points that aren't visible from the homepage.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
<br>
</div>

### Q5 How many ports will Nmap scan if the flag -p-400 was used?

==Answer== 400
<div align="center">
<br>
<br>
</div>

Think of it as `-p [start]-[end]`:

- `-p-400` has nothing before the dash, so start defaults to port 1. It reads as `-p 1-400` = **400 ports.**
- `-p-` has nothing on _either_ side, so it's `1-65535` = all ports.
- `-p 400-` has nothing after the dash, so it's `400-65535`.
- `-p 400` with no dash at all is the "just one port".
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
<br>
</div>

### Q6 What is the most likely operating system this machine is running?

==Answer== Ubuntu
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
<br>
</div>

### Q7 What port is the web server running on?

==Answer==
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
<br>
</div>

### Q8 It's essential to ensure you are always doing your reconnaissance thoroughly before progressing. Knowing all open services (which can all be points of exploitation) is very important, don't forget that ports on a higher range might be open, so constantly scan ports after 1000 (even if you leave checking in the background).

==Answer== No answer needed
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
<br>
</div>

### Q9 What is the flag for enabling verbose mode using Nmap?

==Answer==
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## Task 3 Locating directories using Gobuster
### Q10 I have successfully configured Gobuster.

==Answer== No answer needed
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
<br>
</div>

### Q11 What is the directory that has an upload form page?

==Answer==
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## Task 4 Compromise the Webserver
### Q12 What common file type you'd want to upload to exploit the server is blocked? Try a couple to find out.

==Answer==
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
<br>
</div>

### Q13 I understand the Burpsuite tool and its purpose during pentesting.

==Answer== No answer needed
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
<br>
</div>

### Q14 What extension is allowed after running the above exercise?

==Answer==
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
<br>
</div>

### Q15 While completing the above exercise, I have successfully downloaded the PHP reverse shell.

==Answer== No answer needed
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
<br>
</div>

### Q16 What is the name of the user who manages the webserver?

==Answer==
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
<br>
</div>

### Q17 What is the user flag?

==Answer==
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## Task 5 Privilege Escalation
### Q18 On the system, search for all SUID files. Which file stands out?

==Answer==
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
<br>
</div>

### Q19 What is the root flag value?

==Answer==
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## References
