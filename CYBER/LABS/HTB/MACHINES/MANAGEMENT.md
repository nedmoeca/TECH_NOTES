---
link: https://app.hackthebox.com/machines/Management?sort_by=created_at&sort_type=desc
difficulty: Easy
os: Linux
pov: red
release date: 2026-09-12
tags:
  - HTB
  - MACHINE
image: https://cdn.services-k8s.prod.aws.htb.systems/content/machines/avatar/a261b8b2-9dd5-4958-aaac-ca53661ab002-1785405942.png
solved:
solve date:
machine no.:
---

<div style="text-align: center; padding: 80px 40px; page-break-after: always;">

  <img src="/ASSETS/writeup_hack_the_box_logo.png" style="width: 1220px; margin-bottom: 60px;" />

  <div><p style="font-size: 40px; font-weight: 600; margin-bottom: 40px;">Management Writeup</p></div>

  <img src="https://cdn.services-k8s.prod.aws.htb.systems/content/machines/avatar/a261b8b2-9dd5-4958-aaac-ca53661ab002-1785405942.png" style="width: 400px; margin-bottom: 60px;" />

  <div style="font-size: 22px; line-height: 2.2;">
    <p style="margin: 0;">Prepared by: <a href="https://app.hackthebox.com/users/1809572">nedmoeca</a></p>
    <p style="margin: 0;">Author: <a href="https://app.hackthebox.com/users/114053">TheCyberGeek</a></p>
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
|                   |                     |                                                                                                                                                                                                                                                    |

**Result:**

```shell
PORT      STATE SERVICE
22/tcp    open  ssh
80/tcp    open  http
443/tcp   open  https
1689/tcp  open  firefox
4444/tcp  open  krb524
37441/tcp open  unknown
50389/tcp open  unknown

Nmap done: 1 IP address (1 host up) scanned in 31.45 seconds
```
<div align="center">
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
</div>

#### 1.4.2 Fingerprint the seven services

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
22/tcp    open  ssh       OpenSSH 9.6p1 Ubuntu 3ubuntu13.19 (protocol 2.0)
80/tcp    open  http      nginx 1.24.0 (Ubuntu)  -> redirect to https://management.htb/
443/tcp   open  ssl/http  nginx 1.24.0 (Ubuntu)
|  ssl-cert: Subject: CN=management.htb / O=Management Managed Services Ltd
|  Subject Alternative Name: DNS:management.htb, DNS:*.management.htb
1689/tcp  open  java-rmi  Java RMI
|  rmi-dumpregistry: org.opends.server.protocols.jmx.client-unknown
|    javax.management.remote.rmi.RMIServerImpl_Stub  @127.0.1.1:38591
4444/tcp  open  ssl/krb524?  (OpenDJ Administration Connector)
|  ssl-cert: Subject: CN=sso.management.htb / O=Administration Connector RSA Self-Signed Certificate
|  fingerprint: LDAPSearchReq ... ds-root-dse ... ds-cfg-root-dse-backend   (LDAPS)
38591/tcp open  java-rmi  Java RMI
50389/tcp open  ldap      (Anonymous bind OK)
```
<div align="center">
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
</div>

#### 1.4.3 Scan Results Analysis

| Port  | Service  | Version                | Analysis                                                                          | Simple Explanation                                                                        |
| ----- | -------- | ---------------------- | --------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------- |
| 22    | SSH      | OpenSSH 9.6p1          | Modern, no public RCE. Credential-only entry point.                               | The front door. Useless until we find a username and password.                            |
| 80    | HTTP     | nginx 1.24.0           | 301 to `https://management.htb/`. Confirms name-based vhosting.                   | Plain web port that just bounces you to the secure one and reveals the real hostname.     |
| 443   | HTTPS    | nginx 1.24.0           | Main site. Cert SAN is wildcard `*.management.htb`.                               | The real website. Its ID card admits other subdomains exist but won’t name them.          |
| 1689  | Java RMI | OpenDJ JMX             | Registry dump names OpenDJ, points to the dynamic RMI port. Refuses unauth use.   | A management channel for the directory server. Locked, but it confirms what’s running.    |
| 4444  | LDAPS    | OpenDJ Admin Connector | Secure admin endpoint, refuses anonymous ops. Cert CN leaks `sso.management.htb`. | A locked admin line, but its certificate accidentally prints the hidden subdomain’s name. |
| 38591 | Java RMI | (dynamic)              | Secondary JMX endpoint tied to the JVM. Changes each reboot. Noise.               | A second locked management channel. Ignore it.                                            |
| 50389 | LDAP     | OpenDJ config store    | Anonymous bind accepted. Non-standard port. The reconnaissance jackpot.           | The directory database lets strangers connect without a password. Worth a closer look.    |
<div align="center">
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
</div>

### 1.5 Resolve the virtual hosts and identify the web front-ends

**Why this step:** The port scan proved name-based virtual hosting (port 80 redirects to a hostname, the 443 cert carries a wildcard SAN, and the 4444 cert disclosed `sso.management.htb`). Before any hostname-based request will work, those names must resolve to the target locally.

**Command:**

```shell
echo "TARGET_IP management.htb sso.management.htb" | sudo tee -a /etc/hosts
```

**Breakdown:**

- `echo "TARGET_IP management.htb sso.management.htb"` builds one hosts-file line mapping both names to the target.
- `| sudo tee -a /etc/hosts` appends that line to `/etc/hosts` with root privileges (`-a` = append, so existing entries are preserved).

**Result (IP scrubbed):**

```
TARGET_IP management.htb sso.management.htb
```

Both hostnames now resolve, and both load in the browser after accepting the self-signed certificate warning:

- `https://management.htb/` serves a corporate marketing site for “Management Managed Services Ltd.” Its copy advertises managed “identity, service desk, monitoring and backup.” 

![[management-landing.png]]

- `https://sso.management.htb/` issues a redirect into `/openam/XUI/` and presents an **OpenAM Community Edition** sign-in page. 

![[openam-login.png]]

**What this gives you:** Two distinct web applications on one IP. **Key finding:** the real application surface is the OpenAM identity platform at `https://sso.management.htb/openam`; the main site is a separate, static-looking marketing front-end whose copy foreshadows the service stack (identity, service desk, backup).

**Next:** Fingerprint and content-enumerate the main site first, confirming whether it holds anything actionable or is purely a front, before pivoting to OpenAM.
<div align="center">
<br>
<br>
</div>

#### OpenAM (OH-pen-ay-em)

**OpenAM** is an open-source Identity and Access Management (IAM) platform. Think of it as the head of security for an organization’s web applications: instead of every app handling its own logins, they all delegate to OpenAM, which decides who you are and what you’re allowed to touch.

What it actually does, in plain terms:

- **Authentication** - it verifies identity (checks your username/password, MFA, etc.), often against a directory like LDAP. That directory on this box is the OpenDJ store you already found on port 50389.
- **Single Sign-On (SSO)** - log in once, and you get access to every connected app without logging in again. That’s why the subdomain here is literally named `sso`.
- **Authorization and policy** - it enforces rules about which users can reach which resources.
- **Federation** - it lets separate organizations trust each other’s logins (SAML, OAuth/OpenID Connect), so a user from company A can access company B’s app.

A bit of lineage, because it explains why it matters for us: OpenAM started at Sun Microsystems, passed to Oracle, then ForgeRock, and the version here is the community fork maintained by the OpenIdentityPlatform project. It’s a large, old, Java web application that runs on Tomcat. That combination (big Java codebase, long history, lots of legacy endpoints) is exactly why experienced players perk up when they see OpenAM on a box: it has a rich history of Java-specific vulnerabilities. We’ll get to its version and what that unlocks once we’ve closed out the main-site decoy.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## 2. Enumeration

### 2.1 Fingerprint and content-enumerate the main site

**Why this step:** With the main site identified as a separate front-end from OpenAM, enumerate it on its own terms (technology, hidden content, page construction) before deciding whether it is in-scope for the attack chain or a decoy.

**Commands/Actions:**

```shell
whatweb -a3 https://management.htb
feroxbuster -u https://management.htb -k -w /usr/share/seclists/Discovery/Web-Content/raft-medium-directories.txt -t 50 -o loot/ferox-management.txt
curl -k https://management.htb
```

- Wappalyzer: 

![[management-landing-wappalyzer.png]]

You could also open the page source in the browser (Ctrl+U) and skim for anything interesting: HTML comments, linked JS bundles, hidden paths, or credentials a developer left behind.

**Breakdown:**

- `whatweb -a3` fingerprints the stack at aggression level 3 (a few extra probes for version/plugin detail).
- `feroxbuster ... -k ... -t 50` brute-forces directories over the self-signed TLS endpoint with 50 threads, output saved for the notes.
- `curl -k https://management.htb` pulls the raw HTML so the page construction is visible without a browser rendering it. 

**Result (IP scrubbed):**

```
# whatweb
https://management.htb [200 OK] HTML5, HTTPServer[Ubuntu Linux][nginx/1.24.0 (Ubuntu)],
IP[TARGET_IP], Script, Title[Management — Managed IT & Infrastructure], nginx[1.24.0]

# feroxbuster
301   GET   https://management.htb/assets => https://management.htb/assets/
(only /assets discovered across 60k requests)

# curl: key excerpt from the inline loader script
var KEY="C+XDTUB0EuPY7BE+xzRcMP6dNjWd0h0GPxdt8tWSTVY=", FILE="assets/app.enc";
...
crypto.subtle.importKey("raw", b64(KEY), {name:"AES-GCM"}, false, ["decrypt"])
  .then(k => crypto.subtle.decrypt({name:"AES-GCM", iv: raw.slice(0,12)}, k, raw.slice(12)))
  .then(buf => (0,eval)(new TextDecoder().decode(buf)));
```

The page also sets `<meta name="robots" content="noindex,nofollow">` and loads only `assets/styles.css` plus the inline loader.

**What this gives you:** A static Nginx-served marketing site whose entire application is an AES-GCM-encrypted JavaScript bundle (`assets/app.enc`) decrypted in the browser using a **hardcoded key present in the page source**. **Key finding:** client-side encryption with an exposed key offers zero real protection, so the bundle is fully recoverable offline. This is a strong rabbit-hole indicator, but it must be decrypted and inspected to rule it out.

**Next:** Recover and decrypt `app.enc` with the leaked key, then grep the plaintext for endpoints, credentials, or paths before judging the site a dead end.
<div align="center">
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
</div>

### 2.2 Decrypt the client-side bundle and rule out the decoy (Section 2: Enumeration)

**Why this step:** The main site’s logic is an AES-GCM-encrypted bundle (`assets/app.enc`) with the decryption key hardcoded in the page source. Because the key is client-side, the bundle is fully recoverable and must be inspected before the site can be dismissed.

**Command:**

```shell
curl -sk https://management.htb/assets/app.enc | python3 -c '
import sys, base64
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
raw = base64.b64decode(sys.stdin.read().strip())
key = base64.b64decode("C+XDTUB0EuPY7BE+xzRcMP6dNjWd0h0GPxdt8tWSTVY=")
sys.stdout.write(AESGCM(key).decrypt(raw[:12], raw[12:], None).decode(errors="replace"))
' | grep -ioE '(https?://[^"]+|/[a-z0-9_/.-]+|user|pass|secret|token|api|key)' | sort -u
```

**Breakdown:**

- `curl -sk .../app.enc` fetches the encrypted bundle (`-s` silent, `-k` ignore self-signed cert).
- The Python one-liner base64-decodes the blob, splits off the 12-byte IV prefix from the ciphertext, and AES-GCM-decrypts it with the base64-decoded key taken from the page source, writing plaintext to stdout.
- `grep ... | sort -u` extracts any URLs, paths, or credential-like tokens from the decrypted JavaScript.

**Result:**

```
(no matches)
```

Byte count of the decrypted output, confirming the decrypt itself succeeded:

```
63863
```

**What this gives you:** 62 KB of decrypted front-end JavaScript containing no endpoints, credentials, or paths. **Key finding (dead end):** the main site is a deliberate rabbit hole. Its client-side encryption is cosmetic and its contents are purely cosmetic UI. Nothing here advances the engagement; the real target is the OpenAM application on the `sso` vhost.

**Next:** Pivot to `https://sso.management.htb/openam` and read the login page source to fingerprint the exact OpenAM version, which drives CVE selection.
<div align="center">
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
</div>

### 2.3 Fingerprint the OpenAM version from the login page

**Why this step:** With the decoy site ruled out, the OpenAM instance on the `sso` vhost is the real target. Its exact version determines which published vulnerabilities apply, and the XUI single-page app discloses that version in its page source.

**Command:**

```shell
curl -sk 'https://sso.management.htb/openam/XUI/' | grep -ioE 'urlArgs[^,]*|version[^,<]*' | head
```

**Breakdown:**

- `curl -sk 'https://sso.management.htb/openam/XUI/'` fetches the login SPA’s HTML over the self-signed TLS endpoint.
- `grep -ioE 'urlArgs[^,]*|version[^,<]*'` extracts the RequireJS `urlArgs` line (and any `version` strings), case-insensitively.

**Result:**

```
urlArgs : "v=16.0.5"
```

> There it is: **OpenAM 16.0.5**. That one string is the pivot point of the whole box. A precise product and version means we can stop guessing and start researching known vulnerabilities.
> 
> A quick note on why this leaks, because it’s a nice lesson: `urlArgs` is a RequireJS cache-busting parameter. The XUI app appends `?v=16.0.5` to every JavaScript module it loads so browsers don’t serve a stale cached copy after an admin upgrades. Completely harmless as a feature, but it hands an attacker the exact build number for free. Version disclosure through a cache-buster is a classic accidental leak.

**What this gives you:** The exact product build. **Key finding:** this is **OpenAM 16.0.5** (the OpenIdentityPlatform community fork). The version is disclosed via a RequireJS cache-busting parameter, a harmless front-end feature that accidentally exposes the build number.

**Next:** Research known vulnerabilities affecting OpenAM 16.0.5 to select a viable exploitation path.
<div align="center">
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
</div>

### 2.4 Research and select a viable CVE

![[Google OpenAM 16.0.5 CVE.png]]

**Why this step:** OpenAM 16.0.5 has a colorful vulnerability history. Multiple pre-auth RCE advisories exist for this version, so they must be triaged by reachability on this specific deployment rather than by severity score.

**Research method:** Search the version against GitHub Advisory Database (GHSA), NVD, GitLab/Snyk advisory mirrors, and the OpenIdentityPlatform release notes. Query terms: `OpenAM 16.0.5 CVE`, `OpenAM pre-auth RCE deserialization`.

**Candidate triage:**

|CVE|Vulnerability|Reachability on this box|Verdict|
|---|---|---|---|
|CVE-2026-33439|Unsafe Java deserialization of the `jato.clientSession` HTTP parameter on legacy JATO ViewBean endpoints (login, password reset)|High. These endpoints ship enabled by default and need no configuration.|**Selected**|
|CVE-2026-45051|Deserialization-of-untrusted-data in the WebAuthn authentication module|Low. Requires WebAuthn to be configured into an auth chain, which this box shows no sign of.|Deferred|
|CVE-2026-46498|Authentication bypass (not RCE)|Uncertain. Advisory does not clearly list 16.0.5; wrong bug class for a shell.|Rejected|
|CVE-2025-67735 / 15284 / 13465|Dependency issues (Netty CRLF, `qs` DoS, Lodash prototype pollution)|N/A. DoS/low impact, fixed in the 16.0.5 release.|Rejected|

**Plain-language summary:** Three “critical RCE” headlines appear for this version, but only one attacks a feature that is turned on by default and reachable without logging in. The deserialization bug in the `jato.clientSession` parameter (CVE-2026-33439) is that one; the others need optional features or are the wrong type of flaw.

**Key finding:** CVE-2026-33439 is the selected path: pre-authentication RCE via Java deserialization of the `jato.clientSession` parameter against legacy JATO endpoints.

**Next:** Confirm those legacy JATO endpoints are actually live and unauthenticated on this deployment before investing in payload construction.
<div align="center">
<br>
<br>
</div>

#### CVE Breakdown
<div align="center">
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
</div>

### 2.5 Confirm the legacy JATO endpoints are live

**Why this step:** CVE-2026-33439 delivers its payload through legacy JATO ViewBean endpoints. Before building a deserialization payload, verify those endpoints respond without authentication on this deployment.

**Command:**

```shell
for ep in /openam/ui/Login /openam/ui/PWResetUserValidation /openam/ui/PWResetQuestion; do
  echo -n "$ep -> "
  curl -sk -o /dev/null -w '%{http_code}\n' "https://sso.management.htb$ep"
done
```

**Breakdown:**

- The loop walks the three candidate JATO endpoints.
- `curl -sk` fetches each over TLS, ignoring the self-signed cert; `-o /dev/null` discards the body; `-w '%{http_code}\n'` prints only the HTTP status.

**Result:**

```
/openam/ui/Login -> 200
/openam/ui/PWResetUserValidation -> 200
/openam/ui/PWResetQuestion -> 200
```

**What this gives you:** All three legacy ViewBean endpoints answer with HTTP 200 and no authentication. **Key finding:** the deserialization sink is reachable pre-auth. These three paths are the delivery points for the `jato.clientSession` payload.

**Next:** Enter exploitation: understand the deserialization mechanism, then obtain and prepare a working proof-of-concept.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## 3. Exploitation & Initial Access

### 3.1 Prepare the attack environment: JDK 21

**Why this step:** The exploit compiles a malicious Java class locally that is then loaded and executed by the target’s JVM (Java Virtual Machine). Compiled bytecode carries a class-file version tied to the compiling JDK; a newer JDK produces bytecode the target’s older JVM rejects with `UnsupportedClassVersionError`, causing a silent failure. JDK 21 produces compatible bytecode for this target.

**Commands:**

```shell
java -version          # initial check
sudo apt install -y openjdk-21-jdk
sudo update-alternatives --config java    # select the java-21 line
sudo update-alternatives --config javac   # select/confirm java-21
java -version 2>&1; javac -version 2>&1    # verify
```

**Breakdown:**

- The first `java -version` reveals the current JDK so you know whether a change is needed.
- `apt install openjdk-21-jdk` installs the full JDK 21 (compiler included, not just a runtime).
- `update-alternatives --config java` / `javac` switch the system default from any newer JDK to 21.
- The final version checks confirm both the runtime and compiler are 21.

**Result:**

```
# before
openjdk version "25.0.4"          # runtime only, javac not installed

# after selecting JDK 21
openjdk version "21.0.12.1" 2026-08-18
javac 21.0.12.1
```

**What this gives you:** A compiler and runtime pinned to JDK 21. **Key finding:** the attack box shipped with JDK 25 (and no compiler). Building the payload under 25 would have produced bytecode the target JVM refuses, so pinning to 21 is mandatory before any payload work.

**Next:** Obtain a public proof-of-concept for CVE-2026-33439 and review its structure before execution.
<div align="center">
<br>
<br>
</div>

#### Why do we need JDK 21 & how did we figure that we need it?
<div align="center">
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
</div>

### 3.2 Acquire and inspect the CVE-2026-33439 PoC

**Why this step:** With JDK 21 in place, obtain a reference exploit and confirm it ships the correct OpenAM/Click/Xalan JARs needed to build a gadget chain matching the server’s classpath.

**Command:**

```shell
git clone https://github.com/TheMalwareGuardian/CVE-2026-33439.git
cd CVE-2026-33439
ls -R
```

**Result (structure):**

```
01 Vulnerable/   docker-compose.yml          # local test lab
02 Exploit/      Exploit_CVE_2026_33439.py   # payload builder + sender
                 Jars/                        # classpath for the gadget chain
Jars/: click-extras-2.3.0.jar  click-nodeps-2.3.0.jar  jato-shaded-16.0.5.jar
       openam-core-16.0.5.jar  serializer-2.7.3.jar  servlet-api.jar  xalan-2.7.3.jar
```

**What this gives you:** A working PoC bundled with the exact JAR versions matching OpenAM 16.0.5. **Key finding:** the `Jars/` directory supplies the real server-side classes (OpenAM core, the shaded JATO library, and OpenAM’s bundled Apache Click fork), so the gadget chain is built against classes guaranteed to exist on the target. No JAR download is required.

**Next:** Understand the deserialization gadget chain, then review the script’s invocation before firing.
<div align="center">
<br>
<br>
</div>

#### PoC Breakdown
<div align="center">
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
</div>


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

