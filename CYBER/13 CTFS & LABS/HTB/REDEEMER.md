---
tags:
  - STARTING_POINT
link: https://app.hackthebox.com/machines/Redeemer
description: Very Easy·Windows
image: https://htb-mp-prod-public-storage.s3.eu-central-1.amazonaws.com/avatars/cdf77651ab0a4eca65acd5cf388b4c66.png
date: 2026-06-04
pawned:
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

Which TCP port is open on the machine?
==6379==

```shell
┌──(kali㉿kali)-[~/nedmoeca/HTB/SP]
└─$ nmap -p- --min-rate 5000 -Pn 10.129.34.239
Starting Nmap 7.98 ( https://nmap.org ) at 2026-06-04 06:48 -0400
Warning: 10.129.34.239 giving up on port because retransmission cap hit (10).
Nmap scan report for 10.129.34.239
Host is up (0.28s latency).
Not shown: 62681 closed tcp ports (reset), 2853 filtered tcp ports (no-response)
PORT     STATE SERVICE
6379/tcp open  redis

Nmap done: 1 IP address (1 host up) scanned in 57.56 seconds
```
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## Task 2

Which service is running on the port that is open on the machine?
==redis====
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## Task 3

What type of database is Redis? Choose from the following options: (i) In-memory Database, (ii) Traditional Database
==In-memory Database==

> **Redis** is a high-performance data store that keeps its data primarily in memory (RAM), making it very fast for reading and writing data.
> 
> Redis is an **in-memory database** (often also called an in-memory key-value store). While it can save data to disk for persistence, its main characteristic is that data is stored and accessed from memory rather than being primarily disk-based like traditional databases.

<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## Task 4

Which command-line utility is used to interact with the Redis server? Enter the program name you would enter into the terminal without any arguments.
==redis-cli==
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## Task 5

Which flag is used with the Redis command-line utility to specify the hostname?
==-h==
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->

## Task 6

Once connected to a Redis server, which command is used to obtain the information and statistics about the Redis server?
==Answer==
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->

## Task 7

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

