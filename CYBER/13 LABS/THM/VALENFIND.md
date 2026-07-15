---
link: https://tryhackme.com/room/lafb2026e10
description:
tags:
image: https://cdn-images.tryhackme.com/room-icons/5ed5961c6276df568891c3ea-1770943483211
solved:
solve date:
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
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->

## References

