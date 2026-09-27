---
tags:
  - JR_PENETRATION_TESTER
  - INTRODUCTION_TO_WEB_HACKING
  - THM
  - ROOM
link:
description:
---
## Summary

| SECTION/TASK | FLAG |
| ------------ | ---- |
|              |      |

<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## 1. Brief

==DEF-Subdomain enumeration is the process of finding valid subdomains for a domain, but why do we do this? We do this to expand our attack surface to try and discover more potential points of vulnerability.==
  
We will explore three different subdomain enumeration methods: Brute Force, OSINT (Open-Source Intelligence) and Virtual Host.  
  
Start the machine and then move onto the next task.
<div>
<br>
<br>
</div>

### Questions

##### What is a subdomain enumeration method beginning with B?
Brute Force
<div>
<br>
</div>

##### What is a subdomain enumeration method beginning with O?
OSINT
<div>
<br>
</div>

##### What is a subdomain enumeration method beginning with V?
Virtual Host
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## 2. OSINT - SSL/TLS Certificates

When an SSL/TLS (Secure Sockets Layer/Transport Layer Security) certificate is created for a domain by a CA (Certificate Authority), CA's take part in what's called "Certificate Transparency (CT) logs". These are publicly accessible logs of every SSL/TLS certificate created for a domain name. The purpose of Certificate Transparency logs is to stop malicious and accidentally made certificates from being used. We can use this service to our advantage to discover subdomains belonging to a domain, sites like [https://crt.sh](https://crt.sh/) offer a searchable database of certificates that shows current and historical results.

Go to [crt.sh](https://crt.sh/) and search for the domain name **tryhackme.com**, find the entry that was logged at **2020-12-26** and enter the domain below to answer the question.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※ ADDED NOTES ※※※※※※※※※※※※※※※※※※※※
<br>
<br>
</div>

### What are SSL/TLS certificates?

**SSL** (Secure Sockets Layer) and its successor **TLS** (Transport Layer Security) are cryptographic protocols that secure communication over a network (mainly the internet).

- ==**DEF-SSL/TLS certificates** are digital certificates issued by a Certificate Authority (CA) to verify that a website (or server) is who it claims to be and enable **HTTPS**, which encrypts data between your browser and the server.==
- Technically, the certificate contains the website’s public key, the domain name it’s issued for, the CA’s signature, and metadata like expiry dates.

When you see `https://` and the 🔒 lock icon in your browser — that’s SSL/TLS at work.

When an SSL/TLS certificate is issued for a website by a Certificate Authority (CA), it gets recorded in something called a ==**DEF-Certificate Transparency (CT) log**.==

==These logs are public lists of all SSL/TLS certificates created for websites. The main reason for CT logs is to help catch fake or mistakenly issued certificates before they can be used for bad purposes.==
<div>
<br>
<br>
</div>

### How are SSL/TLS certificates used in OSINT (Open Source Intelligence)?

In OSINT investigations, SSL/TLS certificates can reveal valuable information. Here’s how:

#### 1. Identify related domains

- Many websites share the same certificate (like subdomains: `mail.example.com`, `api.example.com`).
- Certificate fields (like the **Subject Alternative Name** or SAN) often list multiple domains — so you can discover infrastructure connections.

#### 2. Reveal ownership clues

- Certificates sometimes include organization names, email addresses, or locations in the subject or issuer fields.
- This can help attribute a site to a company or person.

#### 3. Track infrastructure

- Some attackers reuse certificates across multiple servers.
- Investigators can search **certificate transparency logs** (public records of all certificates issued) to spot suspicious patterns or find related malicious domains.

#### 4. Timeline and history

- Certificates have issue/expiry dates — this helps track when a domain was likely active or changed hands.
- You can correlate this with other events (like domain registration dates).

#### 5. Bypass privacy shields

- Even if WHOIS data is hidden with privacy services, certificates might still expose real organizational info.
<div>
<br>
<br>
</div>

### Common tools and sites for SSL/TLS OSINT

- **Censys**, **Shodan** — search engines for internet-connected devices & their certificates.
- **crt.sh** — searches Certificate Transparency logs.
- **Google Certificate Transparency** — logs issued certs.
- **OpenSSL** — to manually inspect certs.
<div>
<br>
</div>

### Example scenario

**Imagine you find a suspicious phishing domain:**

1. Look up its certificate on `crt.sh`.
2. Find all other domains using the same cert → more phishing domains.
3. Check the organization field → link to the attacker or company.
4. Check logs for older certs → see if they reused info elsewhere.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※ ADDED NOTES ※※※※※※※※※※※※※※※※※※※※
<br>
<br>
</div>

### Questions

##### What domain was logged on crt.sh at 2020-12-26?
store.tryhackme.com

![[Pasted image 20250704111225.png]]
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## 3. OSINT - Search Engines

Search engines contain trillions of links to more than a billion websites, which can be an excellent resource for finding new subdomains. Using advanced search methods on websites like Google, such as the `site: filter`, can narrow the search results. For example, `site:*.domain.com -site:www.domain.com` would only contain results leading to the domain name domain.com but exclude any links to www.domain.com; therefore, it shows us only subdomain names belonging to domain.com.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※ ADDED NOTES ※※※※※※※※※※※※※※※※※※※※
<br>
<br>
</div>

Here’s how it works:
- **`site:*.domain.com`** — This tells Google: _“Show me pages from any subdomain of `domain.com`.”_
    - For example: `blog.domain.com`, `shop.domain.com`, `mail.domain.com`, etc.
    - The `*` is a wildcard that matches any subdomain.
- **`-site:www.domain.com`** — The minus sign means _“Exclude this.”_
    - So, this part tells Google: _“Do not show pages from `www.domain.com`.”_

**Putting it all together:**  
This search will show **only pages from subdomains of `domain.com`**, but it will leave out the main site at `www.domain.com`.

So instead of getting links like `www.domain.com/home`, you might find:
- `store.domain.com/products`
- `support.domain.com/help`
- `beta.domain.com/login`
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※ ADDED NOTES ※※※※※※※※※※※※※※※※※※※※
<br>
<br>
</div>

Go to [Google](https://tryhackme.com/room/google.com) and use the search term `site:*.tryhackme.com -site:www.tryhackme.com`, which should reveal a subdomain for tryhackme.com; use that subdomain to answer the question below.
<div>
<br>
<br>
</div>

### Questions

##### What is the TryHackMe subdomain beginning with **S** discovered using the above Google search?
store.tryhackme.com

![[Pasted image 20250704112339.png]]
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## 4. DNS Bruteforce

==**DEF-Bruteforce DNS Enumeration** is the process of automatically generating and testing large numbers of possible subdomain names for a given domain to identify which ones resolve to valid IP addresses.== Bruteforce DNS is an **active enumeration** method.

Because this method requires many requests, we automate it with tools to make the process quicker. In this instance, we are using a tool called dnsrecon to perform this. Click the "View Site" button to open the static site, press the "Run DNSrecon Request" button to start the simulation, and then answer the question below.
<div>
<br>
<br>
</div>

### Questions

##### What is the first subdomain found with the dnsrecon tool?
api.acmeitsupport.thm

![[Pasted image 20250704114254.png]]
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## 5. OSINT - #Sublist3r

To speed up the process of OSINT subdomain discovery, we can automate the above methods with the help of tools like [Sublist3r](https://www.kali.org/tools/sublist3r/), click the "View Site" button to open up the static site and run the sublist3r simulation to discover a new subdomain that will help answer the question below.
<div>
<br>
<br>
</div>

### Questions

##### What is the first subdomain discovered by sublist3r?
web55.acmeitsupport.thm

```shell
user@thm:~$ ./sublist3r.py -d acmeitsupport.thm  
  
          ____        _     _ _     _   _____  
         / ___| _   _| |__ | (_)___| |_|___ / _ __  
         \___ \| | | | '_ \| | / __| __| |_ \| '__|  
          ___) | |_| | |_) | | \__ \ |_ ___) | |  
         |____/ \__,_|_.__/|_|_|___/\__|____/|_|  
  
         # Coded By Ahmed Aboul-Ela - @aboul3la  
  
[-] Enumerating subdomains now for acmeitsupport.thm  
[-] Searching now in Baidu..  
[-] Searching now in Yahoo..  
[-] Searching now in Google..  
[-] Searching now in Bing..  
[-] Searching now in Ask..  
[-] Searching now in Netcraft..  
[-] Searching now in Virustotal..  
[-] Searching now in ThreatCrowd..  
[-] Searching now in SSL Certificates..  
[-] Searching now in PassiveDNS..  
[-] Searching now in Virustotal..  
[-] Total Unique Subdomains Found: 2  
web55.acmeitsupport.thm  
www.acmeitsupport.thm
```
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## 6. Virtual Hosts

Some subdomains aren't always hosted in publicly accessible DNS results, such as development versions of a web application or administration portals. Instead, the DNS record could be kept on a private DNS server or recorded on the developer's machines in their **`/etc/hosts`** file (or **`c:\windows\system32\drivers\etc\hosts`** file for Windows users), which maps domain names to IP addresses. 

Because web servers can host multiple websites from one server when a website is requested from a client, the server knows which website the client wants from the Host header. We can utilize this host header by making changes to it and monitoring the response to see if we've discovered a new website.

Like with DNS Bruteforce, we can automate this process by using a wordlist of commonly used subdomains.

Start the AttackBox and then try the following command against the Acme IT Support machine to discover a new subdomain.

```shell-session
user@machine$ ffuf -w /usr/share/wordlists/SecLists/Discovery/DNS/namelist.txt -H "Host: FUZZ.acmeitsupport.thm" -u http://MACHINE_IP
```

The above command uses the -w switch to specify the wordlist we are going to use. The **-H** switch adds/edits a header (in this instance, the Host header), we have the **FUZZ** keyword in the space where a subdomain would normally go, and this is where we will try all the options from the wordlist.

Because the above command will always produce a valid result, we need to filter the output. We can do this by using the page size result with the **-fs** switch. Edit the below command replacing **{size}** with the most occurring size value from the previous result and try it on the AttackBox.

```shell-session
user@machine$ ffuf -w /usr/share/wordlists/SecLists/Discovery/DNS/namelist.txt -H "Host: FUZZ.acmeitsupport.thm" -u http://MACHINE_IP -fs {size}
```

This command has a similar syntax to the first apart from the **-fs** switch, which tells **ffuf** to ignore any results that are of the specified size.

The above command should have revealed two positive results that we haven't come across before.
<div>
<br>
<br>
</div>

### Questions

##### What is the first subdomain discovered?
delta

```shell
┌──(mopsy㉿APHP)-[~]
└─$ ffuf -w /usr/share/wordlists/seclists/Discovery/DNS/namelist.txt -H "Host: FUZZ.acmeitsupport.thm" -u http://10.10.159.142 -fs 2395

        /'___\  /'___\           /'___\
       /\ \__/ /\ \__/  __  __  /\ \__/
       \ \ ,__\\ \ ,__\/\ \/\ \ \ \ ,__\
        \ \ \_/ \ \ \_/\ \ \_\ \ \ \ \_/
         \ \_\   \ \_\  \ \____/  \ \_\
          \/_/    \/_/   \/___/    \/_/

       v2.1.0-dev
________________________________________________

 :: Method           : GET
 :: URL              : http://10.10.159.142
 :: Wordlist         : FUZZ: /usr/share/wordlists/seclists/Discovery/DNS/namelist.txt
 :: Header           : Host: FUZZ.acmeitsupport.thm
 :: Follow redirects : false
 :: Calibration      : false
 :: Timeout          : 10
 :: Threads          : 40
 :: Matcher          : Response status: 200-299,301,302,307,401,403,405,500
 :: Filter           : Response size: 2395
________________________________________________

api                     [Status: 200, Size: 31, Words: 4, Lines: 1, Duration: 158ms]
delta                   [Status: 200, Size: 51, Words: 7, Lines: 1, Duration: 194ms]
yellow                  [Status: 200, Size: 56, Words: 8, Lines: 1, Duration: 158ms]
:: Progress: [151265/151265] :: Job [1/1] :: 137 req/sec :: Duration: [0:14:00] :: Errors: 0 ::
```
<div>
<br>
</div>

##### What is the second subdomain discovered?
yellow
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## References

https://tryhackme.com/room/subdomainenumeration