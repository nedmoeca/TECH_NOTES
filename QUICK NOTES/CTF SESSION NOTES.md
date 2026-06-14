https://thecybersecguru.com/ctf-walkthroughs/mastering-checkpoint-beginners-guide-from-hackthebox/

## **Introduction**

If you want a practical HackTheBox walkthrough that feels approachable, this guide maps the full path in simple steps. It covers the flow you would expect in ethical hacking and penetration testing: scan first, inspect web apps, verify versions, test likely weaknesses, and move carefully toward access. The provided material gives you a realistic lab for building methodical habits instead of guessing your way through the target.

![Checkpoint Hack The Box](https://i0.wp.com/thecybersecguru.com/wp-content/uploads/2026/06/image-11.png?resize=571%2C226&ssl=1)

Checkpoint Hack The Box

## **Preparing for the Checkpoint HTB Writeup**

Before you start, treat this as a structured penetration exercise rather than a race. Good preparation helps you track services, credentials, app behavior, and each change in the environment. That matters when one clue leads to the next stage.

If you are asking for a detailed writeup for the Checkpoint machine on HackTheBox, the best approach is to organize your tools, notes, and browser setup first. You will move from scans to web review, then to exploitation and privilege work, so preparation saves time and avoids confusion.

**ALSO READ: [Mastering Connected: Beginner’s Guide from Hack The Box](https://thecybersecguru.com/ctf-walkthroughs/mastering-connected-beginners-guide-from-hackthebox/)**

## **Initial Foothold**

Provided Credentials: alex.turner / Checkpoint2024!

![Checkpoint HTB Pwnd](https://i0.wp.com/thecybersecguru.com/wp-content/uploads/2026/06/1781414218982.jpg?resize=700%2C360&ssl=1)

Checkpoint HTB Pwnd

### Reconnaissance & Enumeration

#### Port Scanning (Nmap)

We initiate our scanning with a fast scan followed by service version detection:

```
nmap -p- --min-rate 5000 10.129.16.196 -oN init.nmap
```

Based on the open ports, we run a targeted TCP script and service scan:

```
nmap -p 53,88,135,139,389,445,464,593,636,3268,3269,5985,9389 -sCV 10.129.16.196 -oN services.nmap
```

#### Scan Results Analysis

- **Port 53 (DNS):** Running _Simple DNS Plus_.
- **Port 88 (Kerberos):** Active Directory Kerberos v5 authentications.
- **Ports 135/139/445 (MSRPC/SMB):** File sharing and RPC interfaces active.
- **Ports 389/636/3268/3269 (LDAP/S):** Active Directory Lightweight Directory Access Protocol.
- **Port 5985 (WinRM):** Windows Remote Management is active over HTTP.

#### Active Directory User Enumeration

We extract a list of valid active domain users.

We save these names to a local wordlist called `users.txt` for further Active Directory attacks.

#### SMB Share Enumeration

We perform an unauthenticated/guest SMB check using `NetExec` or `smbclient`.

We locate an unusual share.

Connecting to the share using `smbclient`:

```
smbclient //10.129.16.196/UnusualShare -N
```

On the share, we can see existing files and a configuration file indicating an automated backend mechanism. This service regularly scans for new or updated packages, extracts them, and installs them.

****************************To Access the Complete non-public writeup, Please [CLICK HERE](https://buymeacoffee.com/thecybersecguru/checkpoint-htb-complete-writeup)****************************

******************************To Access Every Script Used in this Writeup******************************, ******************************Please** [CLICK HERE](https://buymeacoffee.com/thecybersecguru/checkpoint-htb-all-scripts)****************************

### Gaining Initial Access (Foothold)

#### Identifying the Vulnerability

While we have `READ` permissions to inspect the share, to deploy our own malicious extension we need `WRITE` permissions.

To obtain valid credentials for a developer or service account capable of writing to `DevDrop`, we check for users with the setting _“Do not require Kerberos preauthentication”_ enabled can have their TGT requested without a password, allowing us to crack their password offline.

#### Password Cracking

We use `hashcat` with to crack the hash

This successfully yields the plain-text password.

#### Exploiting the Extension Share

With credentials, we authenticate to the SMB share and confirm we now have `WRITE` permissions.

#### How Extensions Execute Code

An extension file is simply a renamed ZIP archive containing the extension assets and metadata. The extensions run within Node.js, giving them full access to the local operating system APIs.

Furthermore, we can leverage npm package lifecycle hooks inside `package.json` such as `"postinstall"`, which trigger script execution automatically when the package is extracted and processed.

#### Constructing the Malicious Extension

We will build a simple, lightweight extension from scratch:

1. Create a clean project directory.
2. Create a `package.json` file. We include a script block containing a PowerShell one-liner that connects back to our machine.
3. Package the extension.

#### Deploying and Triggering the Exploit

1. Start a listener on your attacking machine.
2. Authenticate to SMB and upload the malicious package to the root.
3. The automated task running on `DC01` discovers the new package, parses it, and triggers the script block. Grab user.txt.

#### Privilege Escalation

With initial access established, we run an active directory checkup using `BloodHound` or `SharpHound` and examine local system objects.

#### AD Privilege Inspection

We run standard Powerview or WinRM privilege checks.

We notice that an user belongs to a group with specific delegation or write permissions over critical system templates, or they may have direct path access to local active directory objects.

Let’s inspect the Domain Controller’s **AD CS** setup. This is a common attack path in modern AD environments.

Using our Linux attacker system to scan the environment.

#### Identifying Vulnerable Certificate Templates

The scan output reveals a template with the misconfiguration.

This permits to request a certificate for any user on the domain by specifying their Subject Alternative Name (SAN) in the request.

#### Escalating to Domain Administrator (System Compromise)

We request a certificate for the domain `Administrator` account using the vulnerable template.

#### Output

This generates a private key and certificate file on our system:

#### Authenticating as Administrator

We use the newly generated certificate to authenticate to the Domain Controller and perform a Kerberos exchange to recover the NT hash of the Administrator account.

This returns the NT hash for the Domain Administrator.

#### Final Flag Retrieval (Pass-the-Hash)

Using the retrieved NT hash, we authenticate directly to the Domain Controller.

Alternatively, dump the Active Directory database secrets using `secretsdump.py`.

You are now logged in with full Domain Admin privileges. Grab root.txt

You have successfully compromised the **Checkpoint** machine!