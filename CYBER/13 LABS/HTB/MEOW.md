---
tags:
  - STARTING_POINT
link: https://app.hackthebox.com/machines/Meow
description: Very Easy·Linux
image: https://htb-mp-prod-public-storage.s3.eu-central-1.amazonaws.com/avatars/61b5837dfdfe1fb1ca3750cf2712da44.png
date: 2026-03-28
solved: true
---
## Connect to Hack The Box

![[Pasted image 20260328013715.png|1093]]
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## Task 1

What does the acronym VM stand for?
==Virtual Machine==
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## Task 2

What tool do we use to interact with the operating system in order to issue commands via the command line, such as the one to start our VPN connection? It's also known as a console or shell.
==terminal==
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## Task 3

What service do we use to form our VPN connection into HTB labs?
==openvpn==
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## Task 4

What tool do we use to test our connection to the target with an ICMP echo request?
==ping==
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## Task 5

What is the name of the most common tool for finding open ports on a target?
==nmap==
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->

## Task 6

What service do we identify on port 23/tcp during our scans?
==telnet==

**Output:**

```shell
┌──(kali㉿kali)-[~/PUEMAN/HTB]
└─$ nmap -A -p 23 10.129.60.19
Starting Nmap 7.98 ( https://nmap.org ) at 2026-03-27 18:39 -0400
Nmap scan report for 10.129.60.19
Host is up (0.28s latency).

PORT   STATE SERVICE VERSION
23/tcp open  telnet  Linux telnetd
Warning: OSScan results may be unreliable because we could not find at least 1 open and 1 closed port
Device type: general purpose|router
Running: Linux 4.X|5.X, MikroTik RouterOS 7.X
OS CPE: cpe:/o:linux:linux_kernel:4 cpe:/o:linux:linux_kernel:5 cpe:/o:mikrotik:routeros:7 cpe:/o:linux:linux_kernel:5.6.3
OS details: Linux 4.15 - 5.19, MikroTik RouterOS 7.2 - 7.5 (Linux 5.6.3)
Network Distance: 2 hops
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel

TRACEROUTE (using port 23/tcp)
HOP RTT       ADDRESS
1   279.47 ms 10.10.14.1
2   279.79 ms 10.129.60.19

OS and Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 31.43 seconds
```
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->

## Task 7

What username is able to log into the target over telnet with a blank password?
==root==

**Output:**

```shell
┌──(kali㉿kali)-[~/PUEMAN/HTB]
└─$ telnet 10.129.60.19
Trying 10.129.60.19...
Connected to 10.129.60.19.
Escape character is '^]'.

  █  █         ▐▌     ▄█▄ █          ▄▄▄▄
  █▄▄█ ▀▀█ █▀▀ ▐▌▄▀    █  █▀█ █▀█    █▌▄█ ▄▀▀▄ ▀▄▀
  █  █ █▄█ █▄▄ ▐█▀▄    █  █ █ █▄▄    █▌▄█ ▀▄▄▀ █▀█


Meow login: admin
Password: 

Login incorrect
Meow login: root
Welcome to Ubuntu 20.04.2 LTS (GNU/Linux 5.4.0-77-generic x86_64)

 * Documentation:  https://help.ubuntu.com
 * Management:     https://landscape.canonical.com
 * Support:        https://ubuntu.com/advantage

  System information as of Fri 27 Mar 2026 10:46:18 PM UTC

  System load:           0.0
  Usage of /:            41.7% of 7.75GB
  Memory usage:          4%
  Swap usage:            0%
  Processes:             138
  Users logged in:       0
  IPv4 address for eth0: 10.129.60.19
  IPv6 address for eth0: dead:beef::250:56ff:feb0:8b68

 * Super-optimized for small spaces - read how we shrank the memory
   footprint of MicroK8s to make it the smallest full K8s around.

   https://ubuntu.com/blog/microk8s-memory-optimisation

75 updates can be applied immediately.
31 of these updates are standard security updates.
To see these additional updates run: apt list --upgradable


The list of available updates is more than a week old.
To check for new updates run: sudo apt update
Ubuntu comes with ABSOLUTELY NO WARRANTY, to the extent permitted by
applicable law.


Last login: Mon Sep  6 15:15:23 UTC 2021 from 10.10.14.18 on pts/0
root@Meow:~# 
```

Telnet allows users to connect to a server without needing a specific identity by utilizing a `passwordless` login feature. This method is commonly employed for accessing or downloading public files.

```
telnet X.X.X.X#provide username#do not provide any password
```

If anonymous login is disabled on the Telnet server, trying common usernames and passwords like `admin`, `administrator` , `root` , `user`, or `test` can be a good initial step. This approach is less aggressive than attempting to guess passwords through brute force and is recommended to try first when accessing a server.

```
telnet X.X.X.X#provide a common username#provide a common password
```
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->

## Submit Flag

Submit root flag.
==b40abdfe23665f766f9c61ecba8a4c19==

**Output:**

```shell
root@Meow:~# cat flag.txt 
b40abdfe23665f766f9c61ecba8a4c19
```
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->

## Final Steps

Submit exploitation characteristics, rate this machine and leave your feedback.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->

## References

