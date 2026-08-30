---
link: https://tryhackme.com/room/blue
difficulty: Easy
description: Deploy & hack into a Windows machine, leveraging common misconfigurations issues.
tags:
image: https://cdn-images.tryhackme.com/room-icons/blue-1785241443587.png
solved:
solve date:
---

<div style="text-align: center; padding: 80px 40px; page-break-after: always;">

  <img src="/ASSETS/writeup_try_hack_me_logo.png" style="width: 1220px; margin-bottom: 60px;" />

  <div><p style="font-size: 40px; font-weight: 600; margin-bottom: 40px;">Blue Writeup</p></div>

  <img src="https://cdn-images.tryhackme.com/room-icons/blue-1785241443587.png" style="width: 400px; margin-bottom: 60px;" />

  <div style="font-size: 22px; line-height: 2.2;">
    <p style="margin: 0;">Prepared by: nedmoeca</p>
    <p style="margin: 0;">Author(s): ben, DarkStar7471</p>
    <p style="margin: 0;">Difficulty: Easy</p>
    <p style="margin: 0;">Date: 30 Aug 2026</p>
  </div>

</div>
<!-- PAGE BREAK -->

## Summary

Category: **Exploitation**, with a secondary phase of **Post-Exploitation / Credential Attacks**. Exploitation comes first and dominates the box: a Windows 7-era host exposes SMBv1 on 445, and the vulnerability is a memory-corruption bug in the SMBv1 transaction handling that yields remote code execution as SYSTEM without any credentials. The second half is genuinely a different skill. You take a raw shell, upgrade it to a full post-exploitation session, dump the local password database, and crack a hash offline. There's no lateral movement here; the initial exploit already lands you at the highest privilege level on a standalone host, so "escalation" in this room is really session upgrading rather than true privilege escalation.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## Task 1 Recon

Press the **Start Lab Machine** button.

Start the AttackBox by pressing the **Start AttackBox** button at the top of this page. The AttackBox machine will start in Split-Screen view. If it is not visible, use the blue **Show Split View** button at the top of the page.

Scan and learn what exploit this machine is vulnerable to. Please note that this machine does not respond to ping (ICMP) and may take a few minutes to boot up. **This room is not meant to be a boot2root CTF, rather, this is an educational series for complete beginners. Professionals will likely get very little out of this room beyond basic practice as the process here is meant to be beginner-focused.** 

![](https://assets.tryhackme.com/additional/imgur/NhZIt9S.png)

_Art by one of our members, Varg - [THM Profile](https://tryhackme.com/p/Varg) - [Instagram](https://www.instagram.com/varghalladesign/) - [Blue Merch](https://www.redbubble.com/shop/ap/53637482) - [Twitter](https://twitter.com/Vargnaar)_

_Link to Ice, the sequel to Blue: [Link](https://tryhackme.com/room/ice)_

_You can check out the third box in this series, Blaster, here: [Link](https://tryhackme.com/room/blaster)_

-----------------------------------------

The lab machine used in this room (Blue) can be downloaded for offline usage from [https://darkstar7471.com/resources.html(opens in new tab)](https://darkstar7471.com/resources.html)[(opens in new tab)](https://darkstar7471.com/resources.html)

_Enjoy the room! For future rooms and write-ups, follow [@darkstar7471](https://twitter.com/darkstar7471) on Twitter._
<div align="center">
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
</div>

### Q1 Scan the machine. (If you are unsure how to tackle this, I recommend checking out the [Nmap](https://tryhackme.com/room/furthernmap) room)

==No answer needed==
<div align="center">
<br>
<br>
</div>

```shell
┌──(nedmoeca㉿kali)-[~/Labs/THM/Blue]
└─$ nmap -p- --min-rate 5000 -Pn 10.49.188.213 | grapo
Starting Nmap 7.99 ( https://nmap.org ) at 2026-08-30 10:38 -0400
Nmap scan report for 10.49.188.213
Host is up (0.31s latency).
Not shown: 65521 closed tcp ports (reset)
PORT      STATE    SERVICE
135/tcp   open     msrpc
139/tcp   open     netbios-ssn
445/tcp   open     microsoft-ds
3389/tcp  open     ms-wbt-server
4290/tcp  filtered vrml-multi-use
5985/tcp  open     wsman
47001/tcp open     winrm
49152/tcp open     unknown
49153/tcp open     unknown
49154/tcp open     unknown
49155/tcp open     unknown
49171/tcp open     unknown
49172/tcp open     unknown
49200/tcp open     unknown

Nmap done: 1 IP address (1 host up) scanned in 21.39 seconds

135,139,445,3389,5985,47001,49152,49153,49154,49155,49171,49172,49200

┌──(nedmoeca㉿kali)-[~/Labs/THM/Blue]
└─$ nmap -A -p 135,139,445,3389,5985,47001,49152,49153,49154,49155,49171,49172,49200 10.49.188.213 
Starting Nmap 7.99 ( https://nmap.org ) at 2026-08-30 10:48 -0400
Nmap scan report for 10.49.188.213
Host is up (0.32s latency).

PORT      STATE SERVICE       VERSION
135/tcp   open  msrpc         Microsoft Windows RPC
139/tcp   open  netbios-ssn   Microsoft Windows netbios-ssn
445/tcp   open  microsoft-ds  Windows Server 2012 R2 Datacenter 9600 microsoft-ds
3389/tcp  open  ms-wbt-server Microsoft Terminal Service
5985/tcp  open  http          Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
|_http-title: Not Found
|_http-server-header: Microsoft-HTTPAPI/2.0
47001/tcp open  http          Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
|_http-server-header: Microsoft-HTTPAPI/2.0
|_http-title: Not Found
49152/tcp open  msrpc         Microsoft Windows RPC
49153/tcp open  msrpc         Microsoft Windows RPC
49154/tcp open  msrpc         Microsoft Windows RPC
49155/tcp open  msrpc         Microsoft Windows RPC
49171/tcp open  msrpc         Microsoft Windows RPC
49172/tcp open  msrpc         Microsoft Windows RPC
49200/tcp open  msrpc         Microsoft Windows RPC
Warning: OSScan results may be unreliable because we could not find at least 1 open and 1 closed port
Device type: general purpose
Running: Microsoft Windows 2012
OS CPE: cpe:/o:microsoft:windows_server_2012:r2
OS details: Microsoft Windows Server 2012 or 2012 R2
Network Distance: 3 hops
Service Info: OSs: Windows, Windows Server 2008 R2 - 2012; CPE: cpe:/o:microsoft:windows

Host script results:
| smb-os-discovery: 
|   OS: Windows Server 2012 R2 Datacenter 9600 (Windows Server 2012 R2 Datacenter 6.3)
|   OS CPE: cpe:/o:microsoft:windows_server_2012::-
|   Computer name: WIN-JO6REVNMMMP
|   NetBIOS computer name: WIN-JO6REVNMMMP\x00
|   Workgroup: WORKGROUP\x00
|_  System time: 2026-08-30T07:49:48-07:00
| smb2-security-mode: 
|   3.0.2: 
|_    Message signing enabled but not required
| smb-security-mode: 
|   account_used: <blank>
|   authentication_level: user
|   challenge_response: supported
|_  message_signing: disabled (dangerous, but default)
|_clock-skew: mean: 2h19m58s, deviation: 4h02m30s, median: -2s
|_nbstat: NetBIOS name: WIN-JO6REVNMMMP, NetBIOS user: <unknown>, NetBIOS MAC: 0a:99:14:ab:b2:13 (unknown)
| smb2-time: 
|   date: 2026-08-30T14:49:49
|_  start_date: 2026-08-30T14:18:43

TRACEROUTE (using port 443/tcp)
HOP RTT       ADDRESS
1   304.12 ms 192.168.128.1
2   ...
3   323.50 ms 10.49.188.213

OS and Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 145.28 seconds
```

**Analysis**

| Port        | Service       | Version                                 | Analysis                                                                                                       | Simple Explanation                                                                |
| ----------- | ------------- | --------------------------------------- | -------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------- |
| 135         | msrpc         | Microsoft Windows Remote Procedure Call | RPC endpoint mapper. Directs clients to the dynamic high ports. Rarely exploitable directly on a patched host. | The switchboard operator. Tells callers which extension to dial.                  |
| 139         | netbios-ssn   | Microsoft Windows netbios-ssn           | Legacy NetBIOS session service. Its presence alongside 445 indicates backward compatibility is enabled.        | The old-fashioned way Windows machines find and talk to each other.               |
| 445         | microsoft-ds  | Windows Server 2012 R2 Datacenter 9600  | SMB file sharing. Signing disabled, blank account accepted for enumeration. **Primary target.**                | File sharing: how Windows machines hand files back and forth. This is the way in. |
| 3389        | ms-wbt-server | Microsoft Terminal Service              | RDP. Useful post-compromise for a graphical session; no credentials available yet, so not an entry point.      | Remote desktop. Useless until you have a username and password.                   |
| 5985        | http          | Microsoft HTTPAPI httpd 2.0             | WinRM over HTTP. Remote PowerShell management. Requires valid credentials.                                     | Remote command line for admins. Also needs credentials first.                     |
| 47001       | http          | Microsoft HTTPAPI httpd 2.0             | WinRM listener companion port. Same credential requirement.                                                    | Same as above, second door onto the same service.                                 |
| 49152–49200 | msrpc         | Microsoft Windows RPC                   | Dynamic RPC endpoints allocated by the port 135 mapper. Not independently exploitable.                         | The actual extensions the switchboard connects you to.                            |

**What this gives you:**

**Key finding: the target is Windows Server 2012 R2 Datacenter build 9600, hostname `WIN-JO6REVNMMMP`, in `WORKGROUP` — a standalone host, not domain-joined.** Workgroup membership rules out Active Directory attack paths entirely; there is no domain controller, no Kerberos, no domain accounts.

Note that published writeups for this room commonly show a Windows 7 target. The room's machine has since been rebuilt on Server 2012 R2. Expect banner and high-port differences from any reference material; the vulnerability class is unchanged.

Focus on 445. Two lines mark it as the weak point: `message_signing: disabled` means SMB messages carry no integrity protection, and `account_used: <blank>` means the server answered a null session — it disclosed its OS, hostname, and workgroup to an unauthenticated stranger. Every other open port either brokers connections or demands credentials that are not yet available.
<div align="center">
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
</div>

### Q2 How many ports are open with a port number under 1000?

==3==

```
135,139,445,
```
<div align="center">
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
</div>

### Q3  What is this machine vulnerable to? (Answer in the form of: ms??-???, ex: ms08-067)

==Answer==
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## Task 2
### Question

==Answer==
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## Task 3
### Question

==Answer==
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## Task 4
### Question

==Answer==
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## Task 5
### Question

==Answer==
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->

## Task 6
### Question

==Answer==
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->

## Task 7
### Question

==Answer==
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->

## Task 8
### Question

==Answer==
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->

## Task 9
### Question

==Answer==
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->

## Task 10
### Question

==Answer==
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->

## References
