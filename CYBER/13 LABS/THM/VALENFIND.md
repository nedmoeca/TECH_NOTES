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
    <p style="margin: 0;">Date: DD Month Year</p>
  </div>

</div>
<!-- PAGE BREAK -->

## Summary


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

Verify that the target machine is up and reachable by performing an ICMP ping test.

Command: `ping -c 4 TARGET_IP`

Breakdown:
- `-c 4` → sends 4 packets only (clean output, fast)

Output:

```shell
┌──(kali㉿kali)-[~/nedmoeca/THM/Valenfind]
└─$ ping -c 4 10.48.137.192
PING 10.48.137.192 (10.48.137.192) 56(84) bytes of data.
64 bytes from 10.48.137.192: icmp_seq=1 ttl=62 time=290 ms
64 bytes from 10.48.137.192: icmp_seq=2 ttl=62 time=288 ms
64 bytes from 10.48.137.192: icmp_seq=3 ttl=62 time=288 ms
64 bytes from 10.48.137.192: icmp_seq=4 ttl=62 time=292 ms

--- 10.48.137.192 ping statistics ---
4 packets transmitted, 4 received, 0% packet loss, time 3005ms
rtt min/avg/max/mdev = 288.175/289.584/292.173/1.621 ms
```

A successful response confirms that the machine is active and accessible on the THM network, allowing us to proceed with the enumeration phase.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
<br>
</div>

### 2. Enumeration of Web Services

Navigate to `http://10.48.131.246:5000`. Port 5000 is serving a live web app, **ValenFind**, a dating-site theme that matches the challenge story.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->

## References

