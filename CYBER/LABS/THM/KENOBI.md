---
tags:
  - THM
link: https://tryhackme.com/room/kenobi
description: Walkthrough on exploiting a Linux machine. Enumerate Samba for shares, manipulate a vulnerable version of proftpd and escalate your privileges with path variable manipulation.
image: https://tryhackme-images.s3.amazonaws.com/room-icons/46f437a95b1de43238c290a9c416c8d4.png
---
## Summary

| SECTION/TASK                                                 | FLAG                                           |
| ------------------------------------------------------------ | ---------------------------------------------- |
| Task 1. Deploy the vulnerable machine                        | 7                                              |
| Task 2. Enumerating Samba for shares                         | 3<br>log.txt<br>21<br>/var                     |
| Task 3. Gain initial access with ProFtpd                     | 1.3.5<br>4<br>d0b0f3f53b6caa532a83915e19224899 |
| Task 4. Privilege Escalation with Path Variable Manipulation | /usr/bin/menu<br>3<br>                         |

<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## Task 1. Deploy the vulnerable machine

This room will cover accessing a Samba share, manipulating a vulnerable version of proftpd to gain initial access and escalate your privileges to root via an SUID binary.

> **ProFTPD** is an open-source **FTP server** for Unix/Linux systems. Think of it as the software that lets other computers upload/download files from your machine using the FTP protocol.
<div>
<br>
<br>
</div>

### Questions

#### Make sure you're connected to our network and deploy the machine
==No answer needed==

###### 1.1 Connecting to the TryHackMe VPN

Before interacting with the target machine, connect to the TryHackMe VPN using my `.ovpn` configuration file. This establishes a secure tunnel that allows access to the target machine’s internal network.

Command:

`sudo openvpn <myprofile>.ovpn`

Once the VPN initialized successfully, confirm the connection by checking for the `Initialization Sequence Completed` message in the terminal.
<div align="center">
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
</div>
###### 1.2. Verifying the Target is Reachable

After connecting to the VPN, verify that the target machine is up and reachable by performing an ICMP ping test.

Command: `ping -c 4 <TARGET_IP>`

Breakdown:
- `-c 4` → sends 4 packets only (clean output, fast)

Output:

```shell
┌──(kali㉿kali)-[~]
└─$ ping -c 4 10.65.147.145
PING 10.65.147.145 (10.65.147.145) 56(84) bytes of data.
64 bytes from 10.65.147.145: icmp_seq=1 ttl=62 time=212 ms
64 bytes from 10.65.147.145: icmp_seq=2 ttl=62 time=211 ms
64 bytes from 10.65.147.145: icmp_seq=3 ttl=62 time=210 ms
64 bytes from 10.65.147.145: icmp_seq=4 ttl=62 time=209 ms

--- 10.65.147.145 ping statistics ---
4 packets transmitted, 4 received, 0% packet loss, time 3007ms
rtt min/avg/max/mdev = 208.865/210.433/212.204/1.198 ms
```

A successful response confirms that the machine is active and accessible on the TryHackMe network, allowing us to proceed with the enumeration phase.
<div align="center">
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
</div>

#### Scan the machine with nmap, how many ports are open?
==7==

Before we can attack a system, we need to find out what "doors" are open. Doors in this context are ports. We use a tool called **Nmap** (Network Mapper) to scan the target's IP address and see what services are running.

Command: `nmap 10.65.147.145`

Breakdown:
- **`nmap`**
    - **Description:** The utility itself.
    - **Purpose:** Starts the network scanning application.
- **`10.65.147.145`**
    - **Description:** Target Specification.
    - **Purpose:** The IP address of the host being scanned.

Output:

```shell
┌──(kali㉿kali)-[~]
└─$ nmap 10.65.147.145                  
Starting Nmap 7.95 ( https://nmap.org ) at 2026-02-03 09:05 EST
Nmap scan report for 10.65.147.145
Host is up (0.21s latency).
Not shown: 993 closed tcp ports (reset)
PORT     STATE SERVICE
21/tcp   open  ftp
22/tcp   open  ssh
80/tcp   open  http
111/tcp  open  rpcbind
139/tcp  open  netbios-ssn
445/tcp  open  microsoft-ds
2049/tcp open  nfs

Nmap done: 1 IP address (1 host up) scanned in 4.27 seconds
```

Based on my output, Nmap found **7 open ports**.

| **Port** | **Service** | **What it usually does**                                                                 |
| -------- | ----------- | ---------------------------------------------------------------------------------------- |
| **21**   | **FTP**     | File Transfer Protocol: Used for sending files between computers.                        |
| **22**   | **SSH**     | Secure Shell: Used for remote terminal access (logging into the command line).           |
| **80**   | **HTTP**    | Web Server: This means the machine is likely hosting a website.                          |
| **111**  | **RPCBind** | Converts RPC program numbers into universal addresses (often used with NFS).             |
| **139**  | **NetBIOS** | Used for file sharing and communication on older Windows-based networks.                 |
| **445**  | **SMB**     | Server Message Block: A modern way to share files and printers over a network.           |
| **2049** | **NFS**     | Network File System: Allows a user to access files over a network as if they were local. |
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## Task 2. Enumerating Samba for shares

![](https://assets.tryhackme.com/additional/imgur/O8S93Kr.png)

Samba is the standard Windows interoperability suite of programs for Linux and Unix. It allows end users to access and use files, printers and other commonly shared resources on a companies intranet or internet. Its often referred to as a network file system.

Samba is based on the common client/server protocol of Server Message Block (SMB). SMB is developed only for Windows, without Samba, other computer platforms would be isolated from Windows machines, even if they were part of the same network.
<div align="center">
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
</div>
### Understanding Samba & SMB

To understand how we are going to get into this machine, we need to understand how it shares files.

#### What is SMB?

**SMB (Server Message Block)** is a protocol used by Windows computers to share things like files and printers. Imagine it as a "delivery service" for data within a network.

#### What is Samba?

Since our target machine (Kenobi) is running Linux, it shouldn't naturally be able to talk to Windows machines using SMB. **Samba** is the software that allows Linux to "speak" the Windows language.

> **Analogy:** If SMB is the "English language," Windows is a native speaker. Linux is a native "French speaker." **Samba** is the translator that allows the Linux machine to speak English so it can share files with everyone else on the network.

#### Why is this a target?

In many environments, Samba is used to host "Shares"—folders that multiple people can access. If these shares are misconfigured (for example, if they allow "Anonymous" access), a hacker can look inside those folders and find sensitive information like passwords, keys, or private documents.

<div>
<br>
<br>
</div>

### Questions

Using nmap we can enumerate a machine for SMB shares.

Nmap has the ability to run to automate a wide variety of networking tasks. There is a script to enumerate shares!

`nmap -p 445 --script=smb-enum-shares.nse,smb-enum-users.nse MACHINE_IP`

SMB has two ports, 445 and 139.

![](https://assets.tryhackme.com/additional/imgur/bkgVNy3.png)

#### Using the nmap command above, how many shares have been found?
==3==

Now that we know the "door" for file sharing (Port 445) is open, we need to see what "folders" are inside.

Nmap isn't just for finding open ports; it has built-in "mini-programs" called **Scripts**. These scripts can automatically try to log in, check for common bugs, or, in our case, ask the server: _"Hey, what folders are you sharing?"_

Command: `nmap -p 445 --script=smb-enum-shares.nse,smb-enum-users.nse 10.65.147.145`

Breakdown:
- **`-p 445`**: Tells Nmap to only look at the SMB port.
- **`--script=...`**: Tells Nmap to run two specific scripts:
    1. `smb-enum-shares.nse`: Lists all the shared folders.
    2. `smb-enum-users.nse`: Lists any users the system recognizes.

Output:

```shell
┌──(kali㉿kali)-[~]
└─$ nmap -p 445 --script=smb-enum-shares.nse,smb-enum-users.nse 10.65.147.145


Starting Nmap 7.95 ( https://nmap.org ) at 2026-02-03 09:21 EST
Nmap scan report for 10.65.147.145
Host is up (0.21s latency).

PORT    STATE SERVICE
445/tcp open  microsoft-ds

Nmap done: 1 IP address (1 host up) scanned in 2.40 seconds

```

When this command runs successfully, it should identify shares. If your scan results look empty like mine try this using `smbclient`

Sometimes, a general scanner like Nmap doesn't get the information we need. This is common in real-world scenarios. When that happens, we use a tool specifically designed for that service. For SMB, that tool is **smbclient**.

Command: `smbclient -L //10.65.147.145/`

(When it asks for a password, just press **Enter**—we are trying to log in as a "Guest" with no password.)

Output:

```shell
┌──(kali㉿kali)-[~]
└─$ smbclient -L //10.65.147.145/
Password for [WORKGROUP\kali]:

        Sharename       Type      Comment
        ---------       ----      -------
        print$          Disk      Printer Drivers
        anonymous       Disk      
        IPC$            IPC       IPC Service (kenobi server (Samba, Ubuntu))
Reconnecting with SMB1 for workgroup listing.
smbXcli_negprot_smb1_done: No compatible protocol selected by server.
Protocol negotiation to server 10.65.147.145 (for a protocol between LANMAN1 and NT1) failed: NT_STATUS_INVALID_NETWORK_RESPONSE
Unable to connect with SMB1 -- no workgroup available
```

Breakdown:

- **`smbclient`**: The tool used to talk to SMB shares.
- **`-L`**: Stands for "List." It asks the server to show us all available shares.
- **`//IP/`**: The address of the machine we are looking at.

Total Shares Found: 3
<div align="center">
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
</div>
On most distributions of Linux smbclient is already installed. Lets inspect one of the shares.

`smbclient //10.65.147.145/anonymous`

Using your machine, connect to the machines network share.

![](https://assets.tryhackme.com/additional/imgur/B1FXBt8.png)
#### Once you're connected, list the files on the share. What is the file can you see?
==log.txt==

Now that we know a share called `anonymous` exists, we want to see what is inside it.
When prompted for a password, we simply press **Enter**. This works because "Anonymous" shares are designed to let people in without credentials.
Once successful, your terminal changes to `smb: \>`. You are now interacting directly with the remote computer's folder.

Output:

```shell
┌──(kali㉿kali)-[~]
└─$ smbclient //10.65.147.145/anonymous


Password for [WORKGROUP\kali]:
Try "help" to get a list of possible commands.
smb: \> ls
  .                                   D        0  Wed Sep  4 06:49:09 2019
  ..                                  D        0  Sat Aug  9 09:03:22 2025
  log.txt                             N    12237  Wed Sep  4 06:49:09 2019

                9183416 blocks of size 1024. 2993084 blocks available
smb: \> 
```

Inside the SMB prompt, we use the `ls` (list) command: `smb: \> ls`
<div align="center">
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
</div>
You can recursively download the SMB share too. Submit the username and password as nothing.

smbget -R smb://10.65.147.145/anonymous

Open the file on the share. There is a few interesting things found.

- Information generated for Kenobi when generating an SSH key for the user
- Information about the ProFTPD server.
#### What port is FTP running on?
==21==

<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## Task 3. Gain initial access with ProFtpd
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## Task 4. Privilege Escalation with Path Variable Manipulation
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## References

