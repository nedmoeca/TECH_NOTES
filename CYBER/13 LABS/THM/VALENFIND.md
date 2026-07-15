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

**Output**:

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

The challenge is filed under the **Web** category and the task card hands us a direct entry point: `http://10.48.131.246:5000`. Because the port is already known, a slow full-port scan is unnecessary. Instead, we simply open the address in a browser to confirm a web application is being served there.

Navigate to `http://10.48.131.246:5000`. Port 5000 is serving a live web app, **ValenFind**, a dating-site theme that matches the challenge story.

![[Pasted image 20260714194059.png]]

Before touching anything, we walk the app as a legitimate user.

**The important observation:** the `/complete_profile` form collects genuinely **sensitive personal data** — phone number and home address — and the page even winks at us with _"(Your secrets are safe with us… mostly.)"_

The dashboard confirms there are **other users** (`romeo_montague`, `casanova_official`, `cleopatra_queen`, `sherlock_h`, `gatsby_great`, `jane_eyre`, `count_dracula`, `cupid`), each with a **"Profile"** button. That's our next lead.

The logical next move is to see **how the app identifies a single user's profile in the URL**. This tells us whether we can tamper with that identifier to reach data that isn't ours — a class of flaw called **IDOR** (Insecure Direct Object Reference), which we'll define properly if the URL structure supports it.


<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->

## References

