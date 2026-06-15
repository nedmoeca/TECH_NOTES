---
tags:
  - STARTING_POINT
link: https://app.hackthebox.com/machines/Dancing
description: Very Easy·Windows
image: https://htb-mp-prod-public-storage.s3.eu-central-1.amazonaws.com/avatars/ce52eadd09ff5a28a1eea8c65d6683a9.png
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

What does the 3-letter acronym SMB stand for?
==Server Message Block==
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## Task 2

What port does SMB use to operate at?
==445==
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## Task 3

What is the service name for port 445 that came up in our Nmap scan?
==microsoft-ds==

**Output:**

```shell
┌──(kali㉿kali)-[~/PUEMAN/HTB]
└─$ nmap -sV -p 445 10.129.18.40
Starting Nmap 7.98 ( https://nmap.org ) at 2026-03-28 11:08 -0400
Nmap scan report for 10.129.18.40
Host is up (0.57s latency).

PORT    STATE SERVICE       VERSION
445/tcp open  microsoft-ds?

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 48.10 seconds
```
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## Task 4

What is the 'flag' or 'switch' that we can use with the smbclient utility to 'list' the available shares on Dancing?
==-L==
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## Task 5

How many shares are there on Dancing?
==4==

**Output:**

```shell
┌──(kali㉿kali)-[~/PUEMAN/HTB]
└─$ smbclient -L 10.129.18.40              
Password for [WORKGROUP\kali]:

        Sharename       Type      Comment
        ---------       ----      -------
        ADMIN$          Disk      Remote Admin
        C$              Disk      Default share
        IPC$            IPC       Remote IPC
        WorkShares      Disk      
Reconnecting with SMB1 for workgroup listing.
do_connect: Connection to 10.129.18.40 failed (Error NT_STATUS_RESOURCE_NAME_NOT_FOUND)
Unable to connect with SMB1 -- no workgroup available
```
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->

## Task 6

What is the name of the share we are able to access in the end with a blank password?
==WorkShares==

**Output:**

```
┌──(kali㉿kali)-[~/PUEMAN/HTB]
└─$ smbclient //10.129.18.40/WorkShares -N
Try "help" to get a list of possible commands.
smb: \> ls
  .                                   D        0  Mon Mar 29 04:22:01 2021
  ..                                  D        0  Mon Mar 29 04:22:01 2021
  Amy.J                               D        0  Mon Mar 29 05:08:24 2021
  James.P                             D        0  Thu Jun  3 04:38:03 2021

                5114111 blocks of size 4096. 1753004 blocks available
smb: \> 
```
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->

## Task 7

What is the command we can use within the SMB shell to download the files we find?
==get==
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->

## Submit Flag

Submit root flag
==5f61c10dffbc77a704d76016a22f1664==
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->

## References

