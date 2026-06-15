---
tags:
  - STARTING_POINT
link: https://app.hackthebox.com/machines/Fawn
description: Very Easy·Linux
image: https://htb-mp-prod-public-storage.s3.eu-central-1.amazonaws.com/avatars/b64f85071e626e4cc2272d54332e4131.png
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

What does the 3-letter acronym FTP stand for?
==File Transfer Protocol==
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## Task 2

Which port does the FTP service listen on usually?
==21==
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## Task 3

FTP sends data in the clear, without any encryption. What acronym is used for a later protocol designed to provide similar functionality to FTP but securely, as an extension of the SSH protocol?
==SFTP==
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## Task 4

What is the command we can use to send an ICMP echo request to test our connection to the target?
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

From your scans, what version is FTP running on the target?
==vsftpd 3.0.3==

**Output:**

```shell
┌──(kali㉿kali)-[~/PUEMAN/HTB]
└─$ nmap -sV -p 21 10.129.61.67
Starting Nmap 7.98 ( https://nmap.org ) at 2026-03-28 10:06 -0400
Nmap scan report for 10.129.61.67
Host is up (0.57s latency).

PORT   STATE SERVICE VERSION
21/tcp open  ftp     vsftpd 3.0.3
Service Info: OS: Unix

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 5.77 seconds
```
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->

## Task 6

From your scans, what OS type is running on the target?
==Unix==
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->

## Task 7

What is the command we need to run in order to display the 'ftp' client help menu?
`ftp -?`
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->

## Task 8

What is username that is used over FTP when you want to log in without having an account?
==anonymous==

FTP allows users to connect to a server without needing a specific identity by using an `anonymous` login feature. This method is widely used for accessing or downloading public files.

```
ftp X.X.X.X
#provide anonymous as username
#provide any password
```

**Output:**

```shell
┌──(kali㉿kali)-[~/PUEMAN/HTB]
└─$ ftp 10.129.61.67
Connected to 10.129.61.67.
220 (vsFTPd 3.0.3)
Name (10.129.61.67:kali): anonymous
331 Please specify the password.
Password: 
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

## Task 9

What is the response code we get for the FTP message 'Login successful'?
==230==
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->

## Task 10

There are a couple of commands we can use to list the files and directories available on the FTP server. One is dir. What is the other that is a common way to list files on a Linux system.
==ls==

**Output:**

```shell
ftp> ls
229 Entering Extended Passive Mode (|||49134|)
150 Here comes the directory listing.
-rw-r--r--    1 0        0              32 Jun 04  2021 flag.txt
226 Directory send OK.
ftp> dir
229 Entering Extended Passive Mode (|||20937|)
150 Here comes the directory listing.
-rw-r--r--    1 0        0              32 Jun 04  2021 flag.txt
226 Directory send OK.
```
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->

## Task 11

What is the command used to download the file we found on the FTP server?
==get==

**Output:**

```shell
ftp> get flag.txt
local: flag.txt remote: flag.txt
229 Entering Extended Passive Mode (|||46866|)
150 Opening BINARY mode data connection for flag.txt (32 bytes).
100% |*********************************************|    32       18.46 KiB/s    00:00 ETA
226 Transfer complete.
32 bytes received in 00:00 (0.05 KiB/s)                                                                                       
```
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->

## Submit Flag

**Output:**

```shell
┌──(kali㉿kali)-[~/PUEMAN/HTB]
└─$ cat  flag.txt             
035db21c881520061c53e0536e44f815                                                                                          
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

