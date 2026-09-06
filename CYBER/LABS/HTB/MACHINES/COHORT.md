---
link: https://app.hackthebox.com/machines/Cohort
difficulty: Easy
os: Linux
release date: 2026-08-01
tags:
  - SN_11
image: https://cdn.services-k8s.prod.aws.htb.systems/content/machines/avatar/a1fb351c-6269-49cd-8789-fc579a687c97-1781002999.png
solved:
solve date:
machine no.: 11
---

<div style="text-align: center; padding: 80px 40px; page-break-after: always;">

  <img src="/ASSETS/writeup_hack_the_box_logo.png" style="width: 1220px; margin-bottom: 60px;" />

  <div><p style="font-size: 40px; font-weight: 600; margin-bottom: 40px;">Cohort Writeup</p></div>

  <img src="https://cdn.services-k8s.prod.aws.htb.systems/content/machines/avatar/a1fb351c-6269-49cd-8789-fc579a687c97-1781002999.png" style="width: 400px; margin-bottom: 60px;" />

  <div style="font-size: 22px; line-height: 2.2;">
    <p style="margin: 0;">Prepared by: <a href="https://app.hackthebox.com/users/1809572">nedmoeca</a></p>
    <p style="margin: 0;">Author(s): <a href="https://app.hackthebox.com/users/114053">TheCyberGeek</a></p>
    <p style="margin: 0;">Difficulty: Easy/Medium/Hard/Insane</p>
    <p style="margin: 0;">Date: DD Month Year</p>
  </div>

</div>
<!-- PAGE BREAK -->

## Summary

Category: **Web**, with a secondary **Linux exploitation / CVE-chaining** component. Web comes first and is what gets you inside.

It fits Web because the entire foothold hinges on a server-side request forgery in the public portal: a user-supplied URL field that the application fetches on your behalf, with a blocklist filter that can be walked around. That SSRF is not just a proof-of-concept, it's the only way to see a service that is bound to loopback and invisible to any external port scan, and it's how you recover the hostname that makes the actual exploit reachable. Once you have a shell, the box shifts character entirely: the escalation is a known local privilege-escalation CVE against a system daemon, which is a different skill from the web work that got you there.
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
┌──(nedmoeca㉿kali)-[~/Labs/HTB/SN11/Cohort]
└─$ ping -c 4 $IP                           
PING 10.129.117.120 (10.129.117.120) 56(84) bytes of data.
64 bytes from 10.129.117.120: icmp_seq=1 ttl=63 time=589 ms
64 bytes from 10.129.117.120: icmp_seq=2 ttl=63 time=266 ms
64 bytes from 10.129.117.120: icmp_seq=3 ttl=63 time=364 ms
64 bytes from 10.129.117.120: icmp_seq=4 ttl=63 time=287 ms

--- 10.129.117.120 ping statistics ---
4 packets transmitted, 4 received, 0% packet loss, time 3008ms
rtt min/avg/max/mdev = 265.548/376.256/588.904/128.079 ms
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
┌──(nedmoeca㉿kali)-[~/Labs/HTB/SN11/Cohort]
└─$ nmap -p- --min-rate 5000 -Pn $IP | grapo
Starting Nmap 7.99 ( https://nmap.org ) at 2026-09-06 11:31 -0400
Warning: 10.129.117.120 giving up on port because retransmission cap hit (10).
Nmap scan report for 10.129.117.120
Host is up (0.24s latency).
Not shown: 65508 closed tcp ports (reset)
PORT      STATE    SERVICE
22/tcp    open     ssh
80/tcp    open     http
443/tcp   open     https
1371/tcp  filtered fc-cli
1559/tcp  filtered web2host
10729/tcp filtered unknown
15193/tcp filtered unknown
23535/tcp filtered unknown
23757/tcp filtered unknown
25502/tcp filtered unknown
27021/tcp filtered unknown
28705/tcp filtered unknown
35715/tcp filtered unknown
38633/tcp filtered unknown
38652/tcp filtered unknown
41135/tcp filtered unknown
42457/tcp filtered unknown
42735/tcp filtered unknown
44233/tcp filtered unknown
45064/tcp filtered unknown
46228/tcp filtered unknown
47030/tcp filtered unknown
51555/tcp filtered unknown
52656/tcp filtered unknown
56880/tcp filtered unknown
58394/tcp filtered unknown
63392/tcp filtered unknown

Nmap done: 1 IP address (1 host up) scanned in 36.75 seconds

22,80,443
```
<div align="center">
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
</div>

#### 1.4.2 The "Deep Dive" Scan (Targeted Aggression)

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
┌──(nedmoeca㉿kali)-[~/Labs/HTB/SN11/Cohort]
└─$ nmap -A -p 22,80,443 $IP                
Starting Nmap 7.99 ( https://nmap.org ) at 2026-09-06 11:32 -0400
Nmap scan report for 10.129.117.120
Host is up (0.23s latency).

PORT    STATE SERVICE  VERSION
22/tcp  open  ssh      OpenSSH 9.6p1 Ubuntu 3ubuntu13.18 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   256 0c:4b:d2:76:ab:10:06:92:05:dc:f7:55:94:7f:18:df (ECDSA)
|_  256 2d:6d:4a:4c:ee:2e:11:b6:c8:90:e6:83:e9:df:38:b0 (ED25519)
80/tcp  open  http     nginx 1.24.0 (Ubuntu)
|_http-server-header: nginx/1.24.0 (Ubuntu)
|_http-title: Did not follow redirect to https://cohort.htb/
443/tcp open  ssl/http nginx 1.24.0 (Ubuntu)
|_ssl-date: TLS randomness does not represent time
| tls-alpn: 
|   http/1.1
|   http/1.0
|_  http/0.9
|_http-server-header: nginx/1.24.0 (Ubuntu)
| ssl-cert: Subject: commonName=cohort.htb/organizationName=Cohort Analytics
| Subject Alternative Name: DNS:cohort.htb, DNS:*.cohort.htb
| Not valid before: 2026-06-01T18:47:07
|_Not valid after:  2126-05-08T18:47:07
|_http-title: Did not follow redirect to https://cohort.htb/
Warning: OSScan results may be unreliable because we could not find at least 1 open and 1 closed port
Device type: general purpose
Running: Linux 4.X|5.X
OS CPE: cpe:/o:linux:linux_kernel:4 cpe:/o:linux:linux_kernel:5
OS details: Linux 4.15 - 5.19
Network Distance: 2 hops
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel

TRACEROUTE (using port 80/tcp)
HOP RTT       ADDRESS
1   228.56 ms 10.10.14.1
2   228.82 ms 10.129.117.120

OS and Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 29.82 seconds
```
<div align="center">
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
</div>

#### 1.4.3 Scan Results Analysis

| Port | Service | Version                           | Analysis                                                                                                                                       | Simple Explanation                                                                                                                      |
| ---- | ------- | --------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------- |
| 22   | SSH     | OpenSSH 9.6p1 Ubuntu 3ubuntu13.18 | Current release shipped with Ubuntu 24.04. No known pre-auth RCE. Only useful with harvested credentials or keys.                              | Remote login service. Nothing to attack without a username and password or key, but it becomes a way in the moment either is recovered. |
| 80   | HTTP    | nginx 1.24.0 (Ubuntu)             | Redirects to `https://cohort.htb/`. Serves no content of its own; exists to push clients to TLS.                                               | The plain web port just forwards you to the secure one. Nothing to attack here directly.                                                |
| 443  | HTTPS   | nginx 1.24.0 (Ubuntu)             | Primary application entry point. Certificate names `cohort.htb` with a wildcard SAN. nginx is acting as a reverse proxy, not an origin server. | The real website. The certificate hints there are other sites hiding behind this same door, reachable by name.                          |
**Next:**  
The application answers to a hostname rather than an IP. Add local name resolution for `cohort.htb` and confirm the web application responds before enumerating its content.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
<br>
</div>

### 1.5 Resolve the application hostname locally

**Why this step:**  
We've established that nginx routes by `Host` header and that port 80 redirects to `https://cohort.htb/`. Requests sent to the bare IP reach only the default site. Local name resolution is a prerequisite for reaching the application at all.

**Command:**

```bash
sudo vi /etc/hosts
# Append the following line:
# TARGET_IP  cohort.htb

cat /etc/hosts
```

**Breakdown:**

|Component|Purpose|
|---|---|
|`/etc/hosts`|Static hostname-to-IP mapping file, consulted by the resolver **before** DNS on a default Linux configuration. Entries here override any DNS answer.|
|`sudo`|The file is root-owned; editing requires elevation.|
|`vi`|Text editor. Any editor works; `echo "TARGET_IP cohort.htb" \| sudo tee -a /etc/hosts` achieves the same result non-interactively.|
|`cat /etc/hosts`|Verification step. Confirms the entry was written and no existing line was overwritten.|

###### Why a hosts entry is required rather than optional:

HTB target hostnames such as `cohort.htb` do not exist in public DNS. A browser or `curl` given that hostname will attempt resolution, fail, and never send a packet.

The mapping matters for a second, less obvious reason. When nginx serves multiple virtual hosts on one IP, it selects the backend using the `Host` header of the HTTP request (and the SNI field of the TLS handshake). Both are populated from the hostname the client was given not from the IP it connected to. Browsing `https://TARGET_IP/` therefore sends `Host: TARGET_IP`, matching no configured vhost, and nginx falls through to its default server block.

Adding the hosts entry lets the client send `Host: cohort.htb`, which nginx routes to the intended application. 

**Result:**

```
┌──(nedmoeca㉿kali)-[~/Labs/HTB/SN11/Cohort]
└─$ cat /etc/hosts
127.0.0.1       localhost
127.0.1.1       kali
::1             localhost ip6-localhost ip6-loopback
ff02::1         ip6-allnodes
ff02::2         ip6-allrouters
10.129.117.120  cohort.htb
```

**Next:**  
Name resolution is in place. Load the application in a browser and read its content for descriptions of functionality that indicate attack surface.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## 2. Enumeration

### 2.1 Review the public landing page for described functionality

**Command:**

```bash
# Browse to the application:
firefox https://cohort.htb/
```

Accept the self-signed certificate warning — the certificate observed in 1.3 is issued for `cohort.htb` by an untrusted authority, which is expected on this target.

**Result:**

![[cohort_landing_page.png]]

Site branding: **Cohort Analytics**, a subscription-retention analytics consultancy. Page sections: Services, Approach, Results, Team.

Navigation and calls to action:

|Element|Location|Destination|
|---|---|---|
|Services / Approach / Results / Team|Header nav|In-page anchors on the landing page|
|Client Insights|Header, top right|Separate application (repeated as a CTA)|
|Open Client Insights|Hero section, and footer CTA block|Same destination as above|
|How we work|Hero section|In-page anchor|

Service descriptions listed under "What we do":

|No.|Service|Description as published|Relevance|
|---|---|---|---|
|01|Cohort and retention modelling|Rebuilds retention curves from raw events|Data processing; no user-supplied endpoint implied|
|02|Churn forecasting|Survival models scored against revenue|No external input implied|
|03|Activation analytics|Traces first-30-day paths|No external input implied|
|04|Reporting that gets read|Dashboards refreshed on a schedule|Implies scheduled server-side jobs|
|05|**Source review**|**Validates every feed the client points them at**|**Server fetches a client-nominated remote resource**|

Process steps published under "We work in the open":

- **A** — Connect a warehouse or a read-only export, and agree what a retained account means.
- **B** — Reconcile the raw feed against billing.
- **C** — Model, review together, and hand back the notebook.

**What this gives you:**

**Key finding: service 05 and process step A both describe the server retrieving a resource at a URL the client supplies.** Phrases such as "every feed you point us at" and "connect your warehouse" describe outbound server-initiated requests driven by user-controlled input. Where an application fetches an address chosen by an untrusted party, the address may be redirected toward the server's own internal network rather than an external data source — the precondition for Server-Side Request Forgery.

Supporting observations:

- The "Client Insights" call to action appears three times (header, hero, footer) and is the only element linking away from the landing page. This is the application proper; the landing page is static content.
- Process step C mentions handing back "the notebook," implying a notebook application exists somewhere in the environment.
- Named personnel: Mara Quinteros (Founder) and Devin Oyelaran (Analytics engineering). Retain as potential usernames.

**Ruled out:** The landing page itself as an attack surface. It exposes no input fields, no authentication, and no dynamic content.

**Next:**  
The copy identifies a URL-fetching feature but not its location. Extract every link and form target referenced in the page source to map available paths before following the visible call to action.
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

