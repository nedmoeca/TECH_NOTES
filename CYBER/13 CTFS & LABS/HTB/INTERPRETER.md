---
tags:
  - SN_10
link: https://app.hackthebox.com/machines/Interpreter
description: Medium·Linux
image: https://htb-mp-prod-public-storage.s3.eu-central-1.amazonaws.com/avatars/09ad7380d2a445fff16a31fadcd35ff6.png
date: 2026-02-22
---
## Summary

| SECTION/TASK     | FLAG |
| ---------------- | ---- |
| Submit User Flag |      |
| Submit Root Flag |      |

<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## 1. Reconnaissance & Discovery

### 1.1 Connecting to the HTB VPN

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
### 1.2. Verifying the Target is Reachable

Verify that the target machine is up and reachable by performing an ICMP ping test.

Command: `ping -c 4 TARGET_IP`

Breakdown:
- `-c 4` → sends 4 packets only (clean output, fast)

Output:

```shell
┌──(kali㉿kali)-[~]
└─$ ping -c 4 TARGET_IP
PING TARGET_IP (TARGET_IP) 56(84) bytes of data.
64 bytes from TARGET_IP: icmp_seq=1 ttl=63 time=190 ms
64 bytes from TARGET_IP: icmp_seq=2 ttl=63 time=190 ms
64 bytes from TARGET_IP: icmp_seq=3 ttl=63 time=191 ms
64 bytes from TARGET_IP: icmp_seq=4 ttl=63 time=194 ms

--- TARGET_IP ping statistics ---
4 packets transmitted, 4 received, 0% packet loss, time 3006ms
rtt min/avg/max/mdev = 189.991/191.283/193.771/1.479 ms
```

A successful response confirms that the machine is active and accessible on the HTB network, allowing us to proceed with the enumeration phase.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## 2. Enumeration

### 2.1. Port Scan with Nmap

Before we can attack a system, we need to find out what "doors" are open. Doors in this context are ports. We use a tool called **Nmap** (Network Mapper) to scan the target's IP address and see what services are running.

#### 2.1.1. The "Spearfishing" Scan (All Ports, High Speed)

Command: `nmap -p- --min-rate 5000 -Pn TARGET_IP`

Breakdown:
- **`nmap`**
    - **Description:** The utility itself.
- **`-p-`**
    - **Description:** All Ports Scan. 
    - **Purpose:** Scans all 65,535 ports. Slower but thorough.
- `--min-rate 5000`
	- **Description:** Minimum Packet Rate.
	- **Purpose:** Forces Nmap to send at least 5,000 packets per second. This drastically reduces scan time on stable networks like the HTB VPN.
- `-Pn`
    - **Description:** Skip Host Discovery.
    - **Purpose:** Treats the host as "online" even if it doesn't respond to pings (ICMP). Many HTB boxes have firewalls that block pings.
- **`TARGET_IP`**
    - **Description:** Target Specification.
    - **Purpose:** The IP address of the host being scanned.

Output:

```shell
┌──(kali㉿kali)-[~]
└─$ nmap -p- --min-rate 5000 -Pn TARGET_IP       
Starting Nmap 7.98 ( https://nmap.org ) at 2026-02-22 01:57 -0500
Warning: TARGET_IP giving up on port because retransmission cap hit (10).
Nmap scan report for TARGET_IP
Host is up (0.32s latency).
Not shown: 64926 closed tcp ports (reset), 605 filtered tcp ports (no-response)
PORT     STATE SERVICE
22/tcp   open  ssh
80/tcp   open  http
443/tcp  open  https
6661/tcp open  unknown

Nmap done: 1 IP address (1 host up) scanned in 46.08 s
```
<div align="center">
<br>
<br>
</div>

#### 2.1.2. The "Deep Dive" Scan (Targeted Aggression)

Command: `nmap -A -p p1,p2,p3,p4 TARGET_IP`

Breakdown:
- `-sC`
    - **Description:** Default Script Scan.
    - **Purpose:** Runs a collection built-in Nmap Scripting Engine (NSE) scripts to find common vulnerabilities, metadata, or hidden info.
- `-sV`
    - **Description:** Version Detection.
    - **Purpose:** Probes open ports to determine what software and version are actually running (e.g., identifying "Jetty" or "OpenSSH 9.2").
- `-p`
    - **Description:** Targeted Port List.
    - **Purpose:** Restricts the heavy scanning to only the ports you confirmed are open, saving significant time and processing power.


Output:

```shell
┌──(kali㉿kali)-[~]
└─$ nmap -A -p 22,80,443,6661 TARGET_IP         
Starting Nmap 7.98 ( https://nmap.org ) at 2026-02-22 02:04 -0500
Nmap scan report for TARGET_IP
Host is up (0.19s latency).

PORT     STATE SERVICE  VERSION
22/tcp   open  ssh      OpenSSH 9.2p1 Debian 2+deb12u7 (protocol 2.0)
| ssh-hostkey: 
|   256 07:eb:d1:b1:61:9a:6f:38:08:e0:1e:3e:5b:61:03:b9 (ECDSA)
|_  256 fc:d5:7a:ca:8c:4f:c1:bd:c7:2f:3a:ef:e1:5e:99:0f (ED25519)
80/tcp   open  http     Jetty
| http-methods: 
|_  Potentially risky methods: TRACE
|_http-title: Mirth Connect Administrator
443/tcp  open  ssl/http Jetty
| ssl-cert: Subject: commonName=mirth-connect
| Not valid before: 2025-09-19T12:50:05
|_Not valid after:  2075-09-19T12:50:05
|_http-title: Mirth Connect Administrator
| http-methods: 
|_  Potentially risky methods: TRACE
|_ssl-date: TLS randomness does not represent time
6661/tcp open  unknown
Warning: OSScan results may be unreliable because we could not find at least 1 open and 1 closed port
Device type: general purpose
Running: Linux 4.X|5.X
OS CPE: cpe:/o:linux:linux_kernel:4 cpe:/o:linux:linux_kernel:5
OS details: Linux 4.15 - 5.19, Linux 5.0 - 5.14
Network Distance: 2 hops
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel

TRACEROUTE (using port 22/tcp)
HOP RTT       ADDRESS
1   194.09 ms 10.10.14.1
2   194.91 ms TARGET_IP

OS and Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 197.90 seconds
```
<div align="center">
<br>
<br>
</div>

#### 2.1.3. Scan Results Analysis

| **Service**       | **Version**             | **Analysis**                                                                                                                                                                                    |
| ----------------- | ----------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **OpenSSH**       | `9.2p1`                 | **Low Priority.** This is a modern, patched version of SSH on Debian. Direct exploits are extremely rare. I will keep this as a potential "lateral movement" point if I find credentials later. |
| **Jetty**         | `(Web Server)`          | **Supporting Tech.** Jetty itself is usually secure, but it’s the "engine" for the real target (Mirth).                                                                                         |
| **Mirth Connect** | `Unknown` (* To Verify) | **HIGH PRIORITY.** This software has several high-severity RCE bugs (like CVE-2023-43208). <br>**Priority 1:** Find the specific version number.                                                |
<div align="center">
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
</div>

### 2.2. Enumeration of Web Services (Port 80)
#### 2.2.1. Web Enumeration

Browse to `TARGET_IP`.
<div align="center"><br><img width="" src="Pasted image 20260222104946.png" alt=""></div>

This also confirms Mirth Connect is running.
<div align="center">
<br>
<br>
</div>

#### 2.2.2. Fingerprinting (The "What")

I consulted the **Horizon3.ai** technical disclosure for **CVE-2023-43208**.

NextGen Mirth Connect Remote Code Execution Vulnerability (CVE-2023-43208)[^1]

![[horizon3-ai-attack-research-disclosures-nextgen-mirth-connect-remote-code-execution-2026-02-22-13_33_19.png]]
<div align="center">
<br>
<br>
</div>

#### 2.2.3. Detection

Command: `curl -Lk -H 'X-Requested-With: OpenAPI' https://TARGET_IP/api/server/version`

Breakdown: 

- `curl`
    - Description: Client URL Utility. 
    - Purpose: The tool used to interact with the web API.
- `-Lk`
    - Description: Follow Links (`L`) and Insecure (`k`).
    - Purpose: The Horizon3 post notes that Mirth often redirects to HTTPS. `-L` follows that redirect, and `-k` ignores the self-signed certificate warning common on HTB. 
- `-H 'X-Requested-With: OpenAPI'`
    - Description: Custom HTTP Header.
    - Purpose: The Horizon3 research explains that Mirth’s Java servlet filter checks for this specific header to prevent CSRF. Without this header, the server would reject your request even if the path is correct.
- `/api/server/version`
    - Description: Target API Endpoint. 
    - Purpose: As documented in the research, this is the specific URI that returns the software version string without requiring a login.

Output:

```shell
┌──(kali㉿kali)-[~]
└─$ curl -Lk -H 'X-Requested-With: OpenAPI' https://10.129.1.153/api/server/version
4.4.0    
```

This **`4.4.0`** result is exactly what we were looking for. Any Mirth Connect version **less than 4.4.1** is confirmed vulnerable to **CVE-2023-43208**, which is a critical, **unauthenticated** Remote Code Execution (RCE) vulnerability.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## 3. Exploitation

Once you've confirmed the version as 4.4.0, conduct a targeted search for a functional Proof-of-Concept (PoC).

Search Query: `CVE-2023-43208`

Repository found: https://github.com/K3ysTr0K3R/CVE-2023-43208-EXPLOIT [^2]
<div align="center">
<br>
<br>
</div>

### 3.1. Clone and Prepare the Workspace

```shell
┌──(kali㉿kali)-[~/CS/HTB/Interpreter]
└─$ git clone https://github.com/K3ysTr0K3R/CVE-2023-43208-EXPLOIT                                             
Cloning into 'CVE-2023-43208-EXPLOIT'...
remote: Enumerating objects: 36, done.
remote: Counting objects: 100% (36/36), done.
remote: Compressing objects: 100% (28/28), done.
remote: Total 36 (delta 6), reused 21 (delta 4), pack-reused 0 (from 0)
Receiving objects: 100% (36/36), 15.28 KiB | 237.00 KiB/s, done.
Resolving deltas: 100% (6/6), done.

┌──(kali㉿kali)-[~/CS/HTB/Interpreter]
└─$ cd CVE-2023-43208-EXPLOIT 

┌──(kali㉿kali)-[~/CS/HTB/Interpreter/CVE-2023-43208-EXPLOIT]
└─$ pip install -r requirements.txt
error: externally-managed-environment

× This environment is externally managed
╰─> To install Python packages system-wide, try apt install
    python3-xyz, where xyz is the package you are trying to
    install.
    
    If you wish to install a non-Kali-packaged Python package,
    create a virtual environment using python3 -m venv path/to/venv.
    Then use path/to/venv/bin/python and path/to/venv/bin/pip. Make
    sure you have pypy3-venv installed.
    
    If you wish to install a non-Kali-packaged Python application,
    it may be easiest to use pipx install xyz, which will manage a
    virtual environment for you. Make sure you have pipx installed.
    
    For more information, refer to the following:
    * https://www.kali.org/docs/general-use/python3-external-packages/
    * /usr/share/doc/python3.13/README.venv

note: If you believe this is a mistake, please contact your Python installation or OS distribution provider. You can override this, at the risk of breaking your Python installation or OS, by passing --break-system-packages.
hint: See PEP 668 for the detailed specification.

┌──(kali㉿kali)-[~/CS/HTB/Interpreter/CVE-2023-43208-EXPLOIT]
└─$ python3 -m venv venv                                                                      

┌──(kali㉿kali)-[~/CS/HTB/Interpreter/CVE-2023-43208-EXPLOIT]
└─$ source venv/bin/activate  

┌──(venv)─(kali㉿kali)-[~/CS/HTB/Interpreter/CVE-2023-43208-EXPLOIT]
└─$ pip install -r requirements.txt
Collecting alive_progress==3.1.4 (from -r requirements.txt (line 1))
  Downloading alive_progress-3.1.4-py3-none-any.whl.metadata (68 kB)
Collecting packaging==24.0 (from -r requirements.txt (line 2))
  Downloading packaging-24.0-py3-none-any.whl.metadata (3.2 kB)
Collecting pwncat-cs==0.5.4 (from -r requirements.txt (line 3))
  Downloading pwncat_cs-0.5.4-py3-none-any.whl.metadata (12 kB)
Collecting requests==2.31.0 (from -r requirements.txt (line 4))
  Downloading requests-2.31.0-py3-none-any.whl.metadata (4.6 kB)
Collecting rich==13.7.1 (from -r requirements.txt (line 5))
  Downloading rich-13.7.1-py3-none-any.whl.metadata (18 kB)
Collecting about-time==4.2.1 (from alive_progress==3.1.4->-r requirements.txt (line 1))
  Downloading about_time-4.2.1-py3-none-any.whl.metadata (13 kB)
Collecting grapheme==0.6.0 (from alive_progress==3.1.4->-r requirements.txt (line 1))
  Downloading grapheme-0.6.0.tar.gz (207 kB)
  Installing build dependencies ... done
  Getting requirements to build wheel ... done
  Preparing metadata (pyproject.toml) ... done
Collecting Jinja2<4.0.0,>=3.0.1 (from pwncat-cs==0.5.4->-r requirements.txt (line 3))
  Downloading jinja2-3.1.6-py3-none-any.whl.metadata (2.9 kB)
Collecting PyNaCl<2.0.0,>=1.4.0 (from pwncat-cs==0.5.4->-r requirements.txt (line 3))
  Downloading pynacl-1.6.2-cp38-abi3-manylinux_2_34_x86_64.whl.metadata (10.0 kB)
Collecting ZODB3<4.0.0,>=3.11.0 (from pwncat-cs==0.5.4->-r requirements.txt (line 3))
  Downloading ZODB3-3.11.0.tar.gz (55 kB)
  Installing build dependencies ... done
  Getting requirements to build wheel ... done
  Preparing metadata (pyproject.toml) ... done
Collecting netifaces<0.12.0,>=0.11.0 (from pwncat-cs==0.5.4->-r requirements.txt (line 3))
  Downloading netifaces-0.11.0.tar.gz (30 kB)
  Installing build dependencies ... done
  Getting requirements to build wheel ... done
  Preparing metadata (pyproject.toml) ... done
INFO: pip is looking at multiple versions of pwncat-cs to determine which version is compatible with other requirements. This could take a while.
ERROR: Cannot install -r requirements.txt (line 3) and packaging==24.0 because these package versions have conflicting dependencies.                                                                                                    

The conflict is caused by:
    The user requested packaging==24.0
    pwncat-cs 0.5.4 depends on packaging<21.0 and >=20.9

Additionally, some packages in these conflicts have no matching distributions available for your environment:
    packaging

To fix this you could try to:
1. loosen the range of package versions you've specified
2. remove package versions to allow pip to attempt to solve the dependency conflict

ERROR: ResolutionImpossible: for help visit https://pip.pypa.io/en/latest/topics/dependency-resolution/#dealing-with-dependency-conflicts
```

The script I cloned has a very strict `requirements.txt` that forces `packaging==24.0`, but `pwncat-cs` is an older tool that specifically demands an older version of that same library (`<21.0`). They are fighting, and `pip` is giving up.

**The good news:** You don't actually need the complex `pwncat-cs` or the "fancy" progress bars to run this exploit. You just need `requests` to send the payload and `rich` to see the script's output.

The Fix: 
1. Install the core essentials (ignoring the conflict): `pip install requests rich alive-progress`
2. Forget `pwncat-cs` for now: The script wants to use `pwncat` as a listener, but you can use the standard **Netcat** (`nc`) which is already installed on your Kali system and never has dependency issues.
<div align="center">
<br>
<br>
</div>

### 3.2. Start your Listener (The "Catcher")

Open a **new terminal tab** on your Kali machine. This needs to be running _before_ you launch the exploit so it's ready to catch the incoming connection.

Command: `nc -lvnp 4444`

Output:

```shell
┌──(kali㉿kali)-[~/CS/HTB/Interpreter]
└─$ nc -lvnp 4444                
listening on [any] 4444 ...
```

<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## 4. Post-Exploitation
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## 5. Conclusion & Remediation
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## References


[^1]: [NextGen Mirth Connect Remote Code Execution Vulnerability (CVE-2023-43208)](https://horizon3.ai/attack-research/disclosures/nextgen-mirth-connect-remote-code-execution/)
[^2]: [CVE-2023-43208 - Mirth Connect Remote Code Execution (RCE) Exploit 🚨](https://github.com/K3ysTr0K3)
