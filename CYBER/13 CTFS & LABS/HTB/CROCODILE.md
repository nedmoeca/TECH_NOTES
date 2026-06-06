---
tags:
  - STARTING_POINT
link: https://app.hackthebox.com/machines/Crocodile
description: Very Easy·Linux
image: https://htb-mp-prod-public-storage.s3.eu-central-1.amazonaws.com/avatars/00935a242722b9a2c700bdb6b65195f6.png
date: 2026-06-06
pawned: true
machine no.:
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

What Nmap scanning switch employs the use of default scripts during a scan?
==-sC==
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## Task 2

What service version is found to be running on port 21?
==vsftpd 3.0.3==

```shell
┌──(kali㉿kali)-[~]
└─$ nmap -A -p 21 10.129.1.15                 
Starting Nmap 7.98 ( https://nmap.org ) at 2026-06-06 09:58 -0400
Nmap scan report for 10.129.1.15
Host is up (0.21s latency).

PORT   STATE SERVICE VERSION
21/tcp open  ftp     vsftpd 3.0.3
| ftp-anon: Anonymous FTP login allowed (FTP code 230)
| -rw-r--r--    1 ftp      ftp            33 Jun 08  2021 allowed.userlist
|_-rw-r--r--    1 ftp      ftp            62 Apr 20  2021 allowed.userlist.passwd
| ftp-syst: 
|   STAT: 
| FTP server status:
|      Connected to ::ffff:10.10.15.101
|      Logged in as ftp
|      TYPE: ASCII
|      No session bandwidth limit
|      Session timeout in seconds is 300
|      Control connection is plain text
|      Data connections will be plain text
|      At session startup, client count was 4
|      vsFTPd 3.0.3 - secure, fast, stable
|_End of status
Warning: OSScan results may be unreliable because we could not find at least 1 open and 1 closed port
Device type: general purpose
Running: Linux 4.X|5.X
OS CPE: cpe:/o:linux:linux_kernel:4 cpe:/o:linux:linux_kernel:5
OS details: Linux 4.15 - 5.19
Network Distance: 2 hops
Service Info: OS: Unix

TRACEROUTE (using port 443/tcp)
HOP RTT       ADDRESS
1   215.21 ms 10.10.14.1
2   215.67 ms 10.129.1.15

OS and Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 12.47 seconds
```
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## Task 3

What FTP code is returned to us for the "Anonymous FTP login allowed" message?
==230==
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## Task 4

After connecting to the FTP server using the ftp client, what username do we provide when prompted to log in anonymously?
==anonymous==

```shell
┌──(kali㉿kali)-[~]
└─$ ftp 10.129.1.15
Connected to 10.129.1.15.
220 (vsFTPd 3.0.3)
Name (10.129.1.15:kali): anonymous
230 Login successful.
Remote system type is UNIX.
Using binary mode to transfer files.
ftp> 
```
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## Task 5

After connecting to the FTP server anonymously, what command can we use to download the files we find on the FTP server?
==get==

```shell
ftp> get allowed.userlist
local: allowed.userlist remote: allowed.userlist
229 Entering Extended Passive Mode (|||41546|)
150 Opening BINARY mode data connection for allowed.userlist (33 bytes).
100% |*********************************************|    33        2.56 KiB/s    00:00 ETA
226 Transfer complete.
33 bytes received in 00:00 (0.13 KiB/s)
ftp> get allowed.userlist.passwd
local: allowed.userlist.passwd remote: allowed.userlist.passwd
229 Entering Extended Passive Mode (|||43756|)
150 Opening BINARY mode data connection for allowed.userlist.passwd (62 bytes).
100% |*********************************************|    62      163.63 KiB/s    00:00 ETA
226 Transfer complete.
62 bytes received in 00:00 (0.28 KiB/s)
ftp>
```
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->

## Task 6

What is one of the higher-privilege sounding usernames in 'allowed.userlist' that we download from the FTP server?
==admin==

```
┌──(kali㉿kali)-[~]
└─$ cat allowed.userlist                        
aron
pwnmeow
egotisticalsw
admin
```
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->

## Task 7

What version of Apache HTTP Server is running on the target host?
==Apache httpd 2.4.41==
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->

## Task 8

What switch can we use with Gobuster to specify we are looking for specific filetypes?
==Answer==
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->

## Task 9

Question
==Answer==
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->

## Submit Flag

Question
==Answer==
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->

## References

