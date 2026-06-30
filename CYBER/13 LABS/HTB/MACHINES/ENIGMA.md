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

