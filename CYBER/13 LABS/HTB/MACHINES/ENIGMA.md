---
link: https://app.hackthebox.com/machines/Enigma
description: Easy·Linux
release date: 2026-06-27
tags:
  - SN_11
image: https://htb-mp-prod-public-storage.s3.eu-central-1.amazonaws.com/avatars/131f520bad7d91e8bb5d3c11654467dd.png
solved:
solve date:
machine no.: 6
---
<div style="text-align: center; padding: 80px 40px; page-break-after: always;">

  <img src="/ASSETS/HTB Logo.png" style="width: 1220px; margin-bottom: 60px;" />

  <div><p style="font-size: 40px; font-weight: 600; margin-bottom: 40px;">Enigma Writeup</p></div>

  <img src="https://cdn.services-k8s.prod.aws.htb.systems/content/machines/avatar/a1e514a2-69e8-4e79-82ab-176c3b5a26b4-1780052657.png" style="width: 400px; margin-bottom: 60px;" />

  <div style="font-size: 18px; line-height: 2.2;">
    <p style="margin: 0;">Prepared by: nedmoeca</p>
    <p style="margin: 0;">Author(s): 7u9y</p>
    <p style="margin: 0;">Difficulty: Easy</p>
    <p style="margin: 0;">Date: 27th June, 2026</p>
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
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
</div>

### 1.2 Verify Target is Reachable

Verify that the target machine is up and reachable by performing an ICMP ping test.

**Command:** `ping -c 4 TARGET_IP`

**Breakdown:**

- `-c 4` → sends 4 packets only (clean output, fast)

**Result:**

```shell
┌──(kali㉿kali)-[~/…/HTB/Machines/SN11/Enigma]
└─$ ping -c 4 TARGET_IP 
PING TARGET_IP (TARGET_IP) 56(84) bytes of data.
64 bytes from TARGET_IP: icmp_seq=1 ttl=63 time=226 ms
64 bytes from TARGET_IP: icmp_seq=2 ttl=63 time=223 ms
64 bytes from TARGET_IP: icmp_seq=3 ttl=63 time=220 ms
64 bytes from TARGET_IP: icmp_seq=4 ttl=63 time=221 ms

--- TARGET_IP ping statistics ---
4 packets transmitted, 4 received, 0% packet loss, time 3005ms
rtt min/avg/max/mdev = 220.106/222.527/225.675/2.151 ms
```

A successful response confirms that the machine is active and accessible on the HTB network, allowing us to proceed with the enumeration phase.
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

#### 2.1.1 Full Port Sweep

Begin enumeration by discovering every open port on the target. Run a fast scan across all 65,535 ports to build a complete picture of the attack surface before committing to deeper inspection.

**Command:** `nmap -p- --min-rate 5000 -Pn TARGET_IP`

**Breakdown:**

- **`nmap`**
    - **Description:** The utility itself.
- **`-p-`**
    - **Description:** All Ports Scan. 
    - **Purpose:** Scans all 65,535 ports. Slower but thorough.
- `--min-rate 5000`
	- **Description:** Minimum Packet Rate.
	- **Purpose:** Forces Nmap to send at least 5,000 packets per second. This reduces scan time on stable networks like the HTB VPN.
- `-Pn`
    - **Description:** Skip Host Discovery.
    - **Purpose:** Treats the host as "online" even if it doesn't respond to pings (ICMP). Many HTB boxes have firewalls that block pings.
- **`TARGET_IP`**
    - **Description:** Target Specification.
    - **Purpose:** The IP address of the host being scanned.

**Result:**

```shell
┌──(kali㉿kali)-[~/…/HTB/Machines/SN11/Enigma]
└─$ nmap -p- --min-rate 5000 -Pn TARGET_IP 
Starting Nmap 7.98 ( https://nmap.org ) at 2026-06-28 06:48 +0000
Warning: TARGET_IP giving up on port because retransmission cap hit (10).
Nmap scan report for TARGET_IP
Host is up (0.37s latency).
Not shown: 65463 closed tcp ports (reset), 59 filtered tcp ports (no-response)
PORT      STATE SERVICE
22/tcp    open  ssh
80/tcp    open  http
110/tcp   open  pop3
111/tcp   open  rpcbind
143/tcp   open  imap
993/tcp   open  imaps
995/tcp   open  pop3s
2049/tcp  open  nfs
39345/tcp open  unknown
43875/tcp open  unknown
45607/tcp open  unknown
50355/tcp open  unknown
60309/tcp open  unknown

Nmap done: 1 IP address (1 host up) scanned in 39.08 seconds
```
<div align="center">
<br>
<br>
</div>

#### 2.1.2 The "Deep Dive" Scan (Targeted Aggression)

**Command:** `nmap -A -p p1,p2,p3,p4 TARGET_IP`

**Breakdown:**

- **`-A`**
    - **Description:** Aggressive Scan Mode.
    - **Purpose:** Enables OS detection, version detection, script scanning (`-sC`), and traceroute all at once.
- `-p`
    - **Description:** Targeted Port List.
    - **Purpose:** Restricts the heavy scanning to only the ports you confirmed are open, saving significant time and processing power.


**Result:**

```shell
┌──(kali㉿kali)-[~/…/HTB/Machines/SN11/Enigma]
└─$ nmap -A -p 22,80,110,111,143,993,995,2049 TARGET_IP
Starting Nmap 7.98 ( https://nmap.org ) at 2026-06-30 19:44 +0000
Nmap scan report for TARGET_IP
Host is up (0.27s latency).

PORT     STATE SERVICE  VERSION
22/tcp   open  ssh      OpenSSH 9.6p1 Ubuntu 3ubuntu13.16 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   256 0c:4b:d2:76:ab:10:06:92:05:dc:f7:55:94:7f:18:df (ECDSA)
|_  256 2d:6d:4a:4c:ee:2e:11:b6:c8:90:e6:83:e9:df:38:b0 (ED25519)
80/tcp   open  http     nginx 1.24.0 (Ubuntu)
|_http-title: Did not follow redirect to http://enigma.htb/
|_http-server-header: nginx/1.24.0 (Ubuntu)
110/tcp  open  pop3     Dovecot pop3d
|_ssl-date: TLS randomness does not represent time
|_pop3-capabilities: PIPELINING TOP CAPA UIDL STLS AUTH-RESP-CODE RESP-CODES SASL
| ssl-cert: Subject: commonName=enigma
| Subject Alternative Name: DNS:enigma
| Not valid before: 2026-02-18T20:33:33
|_Not valid after:  2036-02-16T20:33:33
111/tcp  open  rpcbind  2-4 (RPC #100000)
| rpcinfo: 
|   program version    port/proto  service
|   100000  2,3,4        111/tcp   rpcbind
|   100000  2,3,4        111/udp   rpcbind
|   100000  3,4          111/tcp6  rpcbind
|   100000  3,4          111/udp6  rpcbind
|   100003  3,4         2049/tcp   nfs
|   100003  3,4         2049/tcp6  nfs
|   100005  1,2,3      46369/tcp   mountd
|   100005  1,2,3      50731/tcp6  mountd
|   100005  1,2,3      54512/udp   mountd
|   100005  1,2,3      56950/udp6  mountd
|   100021  1,3,4      35861/tcp6  nlockmgr
|   100021  1,3,4      44461/tcp   nlockmgr
|   100021  1,3,4      44726/udp   nlockmgr
|   100021  1,3,4      60836/udp6  nlockmgr
|   100024  1          37332/udp   status
|   100024  1          49537/tcp6  status
|   100024  1          50233/tcp   status
|   100024  1          58327/udp6  status
|   100227  3           2049/tcp   nfs_acl
|_  100227  3           2049/tcp6  nfs_acl
143/tcp  open  imap     Dovecot imapd (Ubuntu)
|_ssl-date: TLS randomness does not represent time
|_imap-capabilities: have more STARTTLS LOGIN-REFERRALS SASL-IR ID IMAP4rev1 Pre-login OK post-login listed LITERAL+ ENABLE LOGINDISABLEDA0001 IDLE capabilities
| ssl-cert: Subject: commonName=enigma
| Subject Alternative Name: DNS:enigma
| Not valid before: 2026-02-18T20:33:33
|_Not valid after:  2036-02-16T20:33:33
993/tcp  open  ssl/imap Dovecot imapd (Ubuntu)
|_ssl-date: TLS randomness does not represent time
| ssl-cert: Subject: commonName=enigma
| Subject Alternative Name: DNS:enigma
| Not valid before: 2026-02-18T20:33:33
|_Not valid after:  2036-02-16T20:33:33
|_imap-capabilities: have more LOGIN-REFERRALS SASL-IR AUTH=PLAINA0001 IMAP4rev1 Pre-login OK post-login listed LITERAL+ ID ENABLE IDLE capabilities
995/tcp  open  ssl/pop3 Dovecot pop3d
|_pop3-capabilities: PIPELINING TOP CAPA UIDL USER AUTH-RESP-CODE RESP-CODES SASL(PLAIN)
|_ssl-date: TLS randomness does not represent time
| ssl-cert: Subject: commonName=enigma
| Subject Alternative Name: DNS:enigma
| Not valid before: 2026-02-18T20:33:33
|_Not valid after:  2036-02-16T20:33:33
2049/tcp open  nfs_acl  3 (RPC #100227)
Warning: OSScan results may be unreliable because we could not find at least 1 open and 1 closed port
Device type: general purpose
Running: Linux 4.X|5.X
OS CPE: cpe:/o:linux:linux_kernel:4 cpe:/o:linux:linux_kernel:5
OS details: Linux 4.15 - 5.19, Linux 5.0 - 5.14
Network Distance: 2 hops
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel

TRACEROUTE (using port 80/tcp)
HOP RTT       ADDRESS
1   254.25 ms 10.10.14.1
2   257.86 ms TARGET_IP

OS and Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 37.45 seconds
```

Your shouldn't scan those "unknown" high ports (39345, 43875, 45607, etc.). They are dynamically assigned NFS/RPC helper ports (`mountd`, `nlockmgr`, `status`) that change on every reboot. Scanning them deeply in `-A` mode adds noise and scan time with zero extra value, since:

1. They're not independently exploitable — they only exist to support the NFS service already on 2049.
2. Their port numbers will be different next time the box restarts anyway.
3. `-A` on them just returns more RPC version info you already have from the `rpcinfo` block on port 111.

They're commonly called **"high ports"** (or "ephemeral ports"), referring to any port number in the upper range, typically **above 1023** (and often more specifically **above 49152** for the formally reserved "dynamic/private" range per IANA). In practice, the term "high port" is used loosely by pentesters to mean "anything way above the well-known 0-1023 range that looks randomly assigned rather than tied to a standard service."

In your case, ports like `39345`, `43875`, `45607` etc. fall into this category for a specific reason: they're **ephemeral RPC ports**, dynamically allocated by `rpcbind` each time an RPC-based service (like NFS's `mountd`, `nlockmgr`, `status`) starts up. They aren't "well-known" or fixed — that's exactly why they show up as `unknown` in a plain `nmap -sV` scan and need `rpcinfo` (which `-A` includes) to identify what they actually belong to.
<div align="center">
<br>
<br>
</div>

#### 2.1.3 Scan Results Analysis

| Port     | **Service** | **Version**            | **Analysis**                                                                                                                                                                      | **Simple Explanation**                                                                                                                                                   |
| -------- | ----------- | ---------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| 22/tcp   | SSH         | OpenSSH 9.6p1 (Ubuntu) | Standard SSH access; no credentials known yet at this stage. Not the initial attack vector.                                                                                       | A back door with a key lock — lets administrators control the machine remotely. We can see it exists but don't have a key yet.                                           |
| 80/tcp   | HTTP        | nginx 1.24.0 (Ubuntu)  | Redirects to `http://enigma.htb` — requires hostname resolution via `/etc/hosts` to access.                                                                                       | The main front door — a public-facing website. When nmap knocked, it redirected us to a specific address, like a receptionist saying _"you need to ask for us by name."_ |
| 110/tcp  | POP3        | Dovecot pop3d          | Mail retrieval service; TLS cert `CN=enigma` confirms the box's internal hostname. Key pivot point for credential reuse.                                                          | A post office window — lets users collect their email. This is the unencrypted version.                                                                                  |
| 111/tcp  | RPCbind     | 2-4 (RPC #100000)      | Exposes the full RPC service map, revealing NFS (2049), `mountd`, `nlockmgr`, and `status` on dynamically assigned high ports — not independently exploitable, just NFS plumbing. | A map in a hallway — it doesn't do anything itself, but tells us what other rooms exist and where to find them.                                                          |
| 143/tcp  | IMAP        | Dovecot imapd (Ubuntu) | Plaintext IMAP; same mail backend as POP3/IMAPS, supports `STARTTLS`.                                                                                                             | Another post office window — instead of collecting mail and taking it home, this one lets you browse your inbox in place.                                                |
| 993/tcp  | SSL/IMAP    | Dovecot imapd (Ubuntu) | TLS-wrapped IMAP; same cert/hostname as other mail services.                                                                                                                      | The same in-place mail browsing window as port 143, but with a privacy screen (encrypted).                                                                               |
| 995/tcp  | SSL/POP3    | Dovecot pop3d          | TLS-wrapped POP3; `SASL(PLAIN)` auth confirmed available over TLS.                                                                                                                | The same mail collection window as port 110, but with a privacy screen (encrypted).                                                                                      |
| 2049/tcp | NFS         | 3 (RPC #100227)        | Core NFS service; export enumeration via `showmount -e` reveals available network shares worth investigating.                                                                     | A shared file storage room — like a filing cabinet on the network that other machines can access. Worth checking whether it's locked or open to anyone.                  |
<div align="center">
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
</div>

### 2.2 Web Service Enumeration

#### 2.2.1. Hostname Resolution

Before the web service can be accessed properly, the target's hostname needs to be mapped to its IP address locally. Without this, any attempt to browse to `enigma.htb` will fail to resolve — even though we already know the IP from our scan.

Add the mapping to your local hosts file:

**Command:** `echo "10.129.32.201 enigma.htb" | sudo tee -a /etc/hosts`

**Breakdown:**

- `echo "10.129.32.201 enigma.htb"`
    - **Description:** Prints the hostname mapping string to stdout.
    - **Purpose:** Prepares the entry to be written into `/etc/hosts`.
- `sudo tee -a /etc/hosts`
    - **Description:** Appends stdin to `/etc/hosts` with elevated privileges while also printing it to the terminal.
    - **Purpose:** `/etc/hosts` is root-owned, so a standard redirect would fail. Piping into `sudo tee -a` correctly elevates only the write operation without opening a full root shell.

**Result:**

```shell
┌──(kali㉿kali)-[~/…/HTB/Machines/SN11/Enigma]
└─$ echo "10.129.32.201 enigma.htb" | sudo tee -a /etc/hosts
10.129.32.201 enigma.htb

┌──(kali㉿kali)-[~/…/HTB/Machines/SN11/Enigma]
└─$ cat /etc/hosts                        
127.0.0.1       localhost
127.0.1.1       kali
::1             localhost ip6-localhost ip6-loopback
ff02::1         ip6-allnodes
ff02::2         ip6-allrouters
10.129.32.201 enigma.htb
```

The system should now now resolve `enigma.htb` to `10.129.32.201` locally, allowing the web service to be accessed by hostname as intended. With that in place, the next step is to browse to the web service and inspect what's running on port 80.
<div align="center">
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
</div>

#### 2.2.2. Initial Web Recon

With the hostname now resolving correctly, browse to `http://enigma.htb` in your browser to inspect what the web service is presenting.

![[enigma.htb.png]]


**Result:**

The page loads a polished corporate marketing site for **Enigma Corp**, presenting itself as a managed IT services company. Scrolling through the page reveals the following:

- A hero section advertising "Enterprise IT. Without the stress."
- A stats bar showing company metrics (3,800+ infrastructures managed, 12,000+ systems monitored)
- A services section listing: Managed IT Support, Hardware & Software Maintenance, On-Site Technical Assistance, Security & Compliance, Cloud Infrastructure, and Analytics & Reporting
- A contact section disclosing a support email address: **[support@enigma.htb](mailto:support@enigma.htb)**
- A footer with standard company links (About, Careers, Blog, Contact)

From an attacker's perspective, this page is mostly decorative — there are no visible login forms, file upload fields, or dynamic parameters in the URL. The page is entirely static HTML and client-side JavaScript with no obvious interactive backend to probe directly.

The one piece of actionable intelligence is the email address `support@enigma.htb`, which confirms the domain being used for internal mail. Combined with the open POP3/IMAP ports discovered during the Nmap scan, this reinforces that the mail services are the more promising avenue to explore next rather than the web surface itself.

At this stage we have two open threads worth pursuing: the mail services (POP3/IMAP on ports 110, 143, 993, 995) and the NFS share (port 2049). **POP3 and IMAP are email protocols** — they're the mechanism that allows a mail client (like Outlook) to connect to a mail server and retrieve messages from a mailbox. **NFS (Network File System) is a file-sharing protocol** — it allows a server to expose folders on its filesystem to other machines on the network, similar to a shared drive in an office environment.

The email address `support@enigma.htb` tells us that the mail infrastructure is active and in use — someone is sending and receiving mail on this domain. However, to interact with a mailbox we need credentials first. We don't have any yet.

This is where the NFS share becomes the priority. NFS shares — particularly ones named something like "onboarding" — are commonly used inside corporate environments to distribute files to new employees before they have full system access. If this share is world-readable (i.e. accessible without authentication, which the `*` wildcard in a `showmount` export list would confirm), it could contain exactly the kind of internal documentation that gets handed to a new hire on their first day — things like welcome letters, system access guides, or initial login credentials.

In other words, the NFS share is the likely source of the credentials we need to get into the mail service. That's why we will pivot there first — not because the mail service isn't interesting, but because we need a key before we can open that door.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
<br>
</div>

### 2.3 NFS Share Enumeration

`showmount` is a command-line utility that queries an NFS server and asks it **"what are you sharing, and with whom?"** It communicates with the `rpcbind` service (port 111) on the target to retrieve the server's export list — the list of directories it has made available to other machines on the network.

Think of it like walking up to a shared filing cabinet in an office and checking the label on the outside before opening it — you're not accessing anything yet, just finding out what's there and whether it's locked.

It's typically one of the first commands you run when you spot NFS (port 2049) open on a target, since there's no point attempting a mount until you know:

1. **What** directories are being shared
2. **Who** is allowed to access them (the `*` wildcard meaning anyone, a specific IP, or a subnet)

**Command:** `showmount -e 10.129.32.201`

**Breakdown:**

- `-e`
    - **Description:** Displays the NFS server's export list — the directories it is making available to other machines on the network.
    - **Purpose:** Before attempting to mount anything, we need to know what the server is actually sharing and whether any access restrictions are in place. This is the standard first step when NFS is identified on a target.
- `10.129.32.201`
    - **Description:** The target IP address.
    - **Purpose:** Directs the query at the Enigma host's NFS service identified on port 2049 during the Nmap scan.

**Result:**

```shell
┌──(kali㉿kali)-[~/…/HTB/Machines/SN11/Enigma]
└─$ showmount -e 10.129.32.201
Export list for 10.129.32.201:
/srv/nfs/onboarding *
```

The server is exporting a single directory: `/srv/nfs/onboarding`. The `*` alongside it is significant — in NFS, this wildcard means the share is available to **any host** with no IP-based restrictions whatsoever. No authentication, no allowlist, no restrictions. Anyone on the network can mount it.

The name "onboarding" is also immediately interesting. In a corporate environment, an onboarding share is exactly the kind of place an IT department would drop welcome documents, system access guides, and initial credentials for new employees. This lines up directly with our earlier reasoning — this share is almost certainly the source of the credentials we need to access the mail service.
<div align="center">
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
</div>

With the export path and access policy confirmed, the next step is to create a local mount point and attach the remote share to it so its contents can be inspected directly from our machine.

**Command:** `mkdir -p /tmp/nfs_mount`

**Breakdown:**

- `mkdir`
    - **Description:** Creates a new directory.
    - **Purpose:** Creates the local folder that the remote NFS share will be attached to.
- `-p`
    - **Description:** Creates parent directories as needed and suppresses errors if the directory already exists.
    - **Purpose:** Ensures the command succeeds cleanly regardless of whether `/tmp/nfs_mount` already exists on the system.
tl
With the mount point ready, attach the remote share:

**Command:** `sudo mount -t nfs 10.129.32.201:/srv/nfs/onboarding /tmp/nfs_mount -o nolock`

**Breakdown:**

- `-t nfs`
    - **Description:** Specifies the filesystem type as NFS.
    - **Purpose:** Tells the mount command exactly which protocol driver to use rather than attempting to guess from the source path.
- `10.129.32.201:/srv/nfs/onboarding`
    - **Description:** The remote export path in `HOST:PATH` format.
    - **Purpose:** Targets the specific share confirmed available in the previous `showmount` query.
- `/tmp/nfs_mount`
    - **Description:** The local directory to mount the share into.
    - **Purpose:** The local access point through which the share's contents will be readable.
- `-o nolock`
    - **Description:** Disables NFS file locking.
    - **Purpose:** Prevents the mount from hanging or failing due to the NFS lock manager not being reachable — a common issue on CTF infrastructure where file locking isn't needed anyway.

**Result:**

```shell
┌──(kali㉿kali)-[~/…/HTB/Machines/SN11/Enigma]
└─$ sudo mount -t nfs 10.129.32.201:/srv/nfs/onboarding /tmp/nfs_mount -o nolock
[sudo] password for kali: 
```

Now list the contents of the mounted share:

**Command:** `ls -la /tmp/nfs_mount`

**Result:**

```shell
┌──(kali㉿kali)-[~/…/HTB/Machines/SN11/Enigma]
└─$ ls -la /tmp/nfs_mount 
total 8
drwxr-xr-x  2 root root 4096 Feb 19 19:54 .
drwxrwxrwt 18 root root  440 Jun 30 23:16 ..
-rw-r--r--  1 root root 1751 Feb 19 19:53 New_Employee_Access.pdf
```

The share contains a single file: `New_Employee_Access.pdf`. The permissions (`-rw-r--r--`) confirm it is world-readable — any user can open it without needing root access. The filename itself is immediately telling: this is exactly the kind of document an IT department would generate for a new employee, and it very likely contains the initial system credentials we've been looking for.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
<br>
</div>

### 2.4 Extracting Credentials from the Onboarding Document

The PDF can be viewed directly in the browser by navigating to `file:///tmp/nfs_mount/New_Employee_Access.pdf` since the share is mounted locally. This gives a clean, readable view of the document exactly as it would appear to the intended recipient. 

![[New_Employee_Access.pdf.png]]

For documentation purposes however, the contents are also extracted to the terminal using `pdftotext`.

**Command:** `pdftotext /tmp/nfs_mount/New_Employee_Access.pdf -`

**Breakdown:**

- `pdftotext`
    - **Description:** A command-line utility that extracts text content from a PDF file.
    - **Purpose:** Allows the PDF contents to be read and documented directly in the terminal without needing a GUI application.
- `/tmp/nfs_mount/New_Employee_Access.pdf`
    - **Description:** The path to the PDF file on the locally mounted NFS share.
    - **Purpose:** Targets the onboarding document discovered in the previous step.
- `-`
    - **Description:** Instructs `pdftotext` to write its output to stdout (the terminal) instead of saving it to a file.
    - **Purpose:** Keeps the output inline and immediately visible rather than creating an intermediate file on disk.

**Result:**

```shell
┌──(kali㉿kali)-[~/…/HTB/Machines/SN11/Enigma]
└─$ pdftotext /tmp/nfs_mount/New_Employee_Access.pdf -
Enigma Corp
IT Department - New Employee System Access

Employee:

Kevin Mitchell

Department:

Operations

Provisioned by:

IT Department

Date:

2024-03-01

Webmail Access
URL:

http://mail001.enigma.htb

Username:

kevin

Password:

Enigma2024!

Please change your password upon first login.
For support contact: it@enigma.htb
This document contains confidential internal information intended solely for the recipient.
Unauthorized access, disclosure, or distribution is strictly prohibited.
Generated automatically by Enigma Corp Identity Management System.
```

The document is an automatically generated IT provisioning notice for a new employee — **Kevin Mitchell** from the Operations department. It contains his initial webmail credentials:

|Field|Value|
|---|---|
|URL|`http://mail001.enigma.htb`|
|Username|`kevin`|
|Password|`Enigma2024!`|

Two additional details are worth noting. First, the support contact (`it@enigma.htb`) confirms an internal IT team is actively managing this environment. Second, the document was generated by an **"Identity Management System"** — suggesting credentials across the organisation may follow a similar pattern or provisioning process, which could be relevant if password reuse is in play.
<div align="center">
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
</div>

Before proceeding, `mail001.enigma.htb` is a new hostname that needs to be added to `/etc/hosts`, otherwise the webmail URL won't resolve:

**Command:** `echo "10.129.32.201 mail001.enigma.htb" | sudo tee -a /etc/hosts`

The hostname is now resolvable. `mail001.enigma.htb` will correctly direct to the target IP, allowing us to interact with the mail service using the hostname rather than the raw IP — which matters here since the webmail URL in the onboarding document explicitly uses this hostname.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
<br>
</div>

### 2.5 Accessing Kevin's Mailbox

Browsing to `http://mail001.enigma.htb` reveals a **Roundcube Webmail** login page — confirming this is the webmail interface referenced in the onboarding document. 

![[Pasted image 20260701024642.png]]

Logging in with Kevin's credentials (`kevin` / `Enigma2024!`) lands us in his inbox, which shows a single email from `sarah@enigma.htb` with the subject "Welcome to Enigma Corp, Kevin!".

![[Pasted image 20260701025234.png]]

![[Pasted image 20260701030156.png]]

While the browser gives us a clean visual view of the inbox, the same mailbox is also accessed directly via the terminal using `openssl s_client` against the POP3S service. This approach is more useful for documentation and automation purposes.

**Command:** `openssl s_client -connect mail001.enigma.htb:995 -quiet << 'EOF'`

**Breakdown:**

- `openssl s_client`
    - **Description:** OpenSSL's built-in generic SSL/TLS client — essentially a raw TCP client that wraps the connection in TLS.
    - **Purpose:** Port 995 (POP3S) requires TLS from the moment the connection opens, so a plain terminal tool like `nc` won't work here. `openssl s_client` handles the TLS handshake transparently and then lets us type raw POP3 commands as if it were a regular text connection.
- `-connect mail001.enigma.htb:995`
    - **Description:** Specifies the target host and port to connect to.
    - **Purpose:** Directs the connection to the POP3S service on the mail server.
- `-quiet`
    - **Description:** Suppresses the verbose TLS handshake and certificate output.
    - **Purpose:** Keeps the terminal output focused on the actual POP3 dialogue rather than pages of TLS negotiation details — though note the self-signed certificate warning still surfaces since `-quiet` doesn't fully suppress verification errors.
- `<< 'EOF' ... EOF`
    - **Description:** A bash heredoc — a way of feeding multiple lines of input into a command all at once.
    - **Purpose:** Allows the full POP3 conversation (`USER`, `PASS`, `LIST`, `RETR`, `QUIT`) to be scripted in one go rather than typed interactively line by line.
- `USER kevin` / `PASS Enigma2024!`
    - **Description:** Standard POP3 authentication commands.
    - **Purpose:** Authenticates to the mail server using the credentials recovered from the onboarding PDF.
- `LIST`
    - **Description:** Requests a list of all messages in the mailbox along with their sizes.
    - **Purpose:** Confirms how many emails are present before retrieving any.
- `RETR 1`
    - **Description:** Retrieves the full content of message number 1.
    - **Purpose:** Reads the only email present in Kevin's inbox.
- `QUIT`
    - **Description:** Closes the POP3 session cleanly.
    - **Purpose:** Terminates the connection properly rather than leaving it hanging.

**Result:**

```shell
┌──(kali㉿kali)-[~/…/HTB/Machines/SN11/Enigma]
└─$ openssl s_client -connect mail001.enigma.htb:995 -quiet << 'EOF'
USER kevin
PASS Enigma2024!
LIST
RETR 1
QUIT
EOF
Connecting to 10.129.32.201
depth=0 CN=enigma
verify error:num=18:self-signed certificate
verify return:1
depth=0 CN=enigma
verify return:1
+OK Dovecot (Ubuntu) ready.
+OK
+OK Logged in.
+OK 1 messages:
1 1473
.
+OK 1473 octets
Return-Path: <sarah@enigma.htb>
X-Original-To: kevin@localhost
Delivered-To: kevin@localhost
Received: from enigma (localhost [127.0.0.1])
        by enigma (Postfix) with ESMTP id 673F7211B9
        for <kevin@localhost>; Wed, 18 Feb 2026 21:29:13 +0000 (UTC)
Date: Wed, 18 Feb 2026 21:29:13 +0000
To: kevin@localhost
From: sarah@enigma.htb
Subject: Welcome to Enigma Corp, Kevin!
Message-Id: <20260218212913.010896@enigma>
X-Mailer: swaks v20240103.0 jetmore.org/john/code/swaks/

Hi Kevin,

Welcome to the team! We're thrilled to have you on board at Enigma Corp.

A little about us — Enigma Corp is a mid-sized technology and operations firm specializing in infrastructure management and enterprise solutions. We've been growing rapidly over the past few years and we're excited to have fresh talent joining us.

I'm Sarah from the Accounts department. I'll be your point of contact for any finance-related queries during your onboarding period.

We're still finalizing a few of your onboarding details — your system access, equipment setup, and department introductions are all being arranged by the IT team. You should be receiving your access credentials shortly via the company shared drive.

In the meantime, don't hesitate to reach out if you have any questions. We want to make sure your first few days are as smooth as possible.

Looking forward to working with you!

Best regards,
Sarah
Accounts Department
Enigma Corp
sarah@enigma.htb

.
+OK Logging out.
```

Kevin's inbox contains a single email — a welcome message sent by **Sarah** from the Accounts department (`sarah@enigma.htb`). The email itself doesn't contain any credentials, but it does introduce a new person of interest. Sarah mentions that Kevin's access credentials will be arriving "via the company shared drive" — which we've already accessed via the NFS share, confirming that chain was the intended path.

More importantly, we now have a second internal username: `sarah`. Given that Kevin's password (`Enigma2024!`) appears to have been auto-generated by the Identity Management System referenced in the onboarding PDF, it's reasonable to ask: was the same password provisioned for other accounts? This is a classic **password reuse** scenario — and the next logical step is to test whether Sarah's account uses the same credential.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
<br>
</div>

### 2.6 Password Reuse Confirmed — Accessing Sarah's Mailbox

The same credential used for Kevin's account can now be tested against Sarah's mailbox. Since both accounts were provisioned by the same IT Identity Management System — and the onboarding document explicitly warned _"Please change your password upon first login"_ — it's worth checking whether Sarah followed that instruction. Run the following command to attempt authentication as Sarah using Kevin's password:

**Command:** `openssl s_client -connect mail001.enigma.htb:995 -quiet << 'EOF'`

**Breakdown:**

- `USER sarah` / `PASS Enigma2024!`
    - **Description:** POP3 authentication commands using Sarah's username with Kevin's provisioned password.
    - **Purpose:** Tests whether the same default password was reused across multiple accounts — a common misconfiguration in environments where passwords are auto-generated and never changed.
- All other flags and commands are identical to the previous step — refer to Section 2.6 for their full breakdown.

**Result:**

```shell
┌──(kali㉿kali)-[~/…/HTB/Machines/SN11/Enigma]
└─$ openssl s_client -connect mail001.enigma.htb:995 -quiet << 'EOF'
USER sarah
PASS Enigma2024!
LIST
RETR 1
QUIT
EOF
Connecting to 10.129.32.201
depth=0 CN=enigma
verify error:num=18:self-signed certificate
verify return:1
depth=0 CN=enigma
verify return:1
+OK Dovecot (Ubuntu) ready.
+OK
+OK Logged in.
+OK 1 messages:
1 838
.
+OK 838 octets
Return-Path: <it@enigma.htb>
X-Original-To: sarah@localhost
Delivered-To: sarah@localhost
Received: from enigma (localhost [127.0.0.1])
        by enigma (Postfix) with ESMTP id C123C211B9
        for <sarah@localhost>; Wed, 18 Feb 2026 21:42:51 +0000 (UTC)
Date: Thu, 19 Feb 2026 10:22:00 +0000
Subject: Re: OpenSTAManager Access Request
From: it@enigma.htb
To: sarah@enigma.htb
Message-Id: <osm-reply-001@enigma.htb>
In-Reply-To: <osm-request-001@enigma.htb>
References: <osm-request-001@enigma.htb>

Hi Sarah,

Apologies for the delay. I have provisioned your access. Please find the details below:

URL: http://support_001.enigma.htb
Username: admin
Password: Ne3s4rtars78s

Note: I will create a dedicated account for you shortly, for now you can use the admin account to get started.

Regards,
IT Support
Enigma Corp

.
+OK Logging out.
```
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

