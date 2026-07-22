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
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
</div>

#### 2.3.3 Unzip and Identify the Binary

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

_What this gives you:_ **Key finding:** `UserInfo.exe` is a .NET assembly, which compiles to intermediate language and decompiles back to near-original C# source — its logic, including any hardcoded credentials, can be read directly.

_Next:_ Decompile the assembly and inspect its authentication routine to recover how it binds to the LDAP server.

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

