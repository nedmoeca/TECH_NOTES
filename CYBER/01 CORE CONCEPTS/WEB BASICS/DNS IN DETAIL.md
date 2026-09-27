---
tags:
  - THM
  - THM-PRE_SECURITY
  - HOW_THE_WEB_WORKS
  - CYBER_SHUJAA_CNS
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

## 1. What is DNS?

DNS (Domain Name System) provides a simple way for us to communicate with devices on the internet without remembering complex numbers. Much like every house has a unique address for sending mail directly to it, every computer on the internet has its own unique address to communicate with it called an IP address. An IP address looks like the following 104.26.10.229, 4 sets of digits ranging from 0 - 255 separated by a period. When you want to visit a website, it's not exactly convenient to remember this complicated set of numbers, and that's where DNS can help. So instead of remembering 104.26.10.229, you can remember [tryhackme.com](http://tryhackme.com/) instead.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※ ADDED NOTES ※※※※※※※※※※※※※※※※※※※※
<br>
<br>
</div>

==**DEF-DNS** stands for **Domain Name System**. It's like the internet's phonebook. DNS translates **domain names** (like `www.google.com`) into **IP addresses** (like `142.250.190.68`) that computers use to identify each other on the network.
Humans remember names like `example.com`, but computers talk using numbers (IP addresses). DNS makes it easier for us to browse the web without needing to memorize those numbers.==

**How DNS works (basic steps):**
1. **You type a website URL** in your browser (`www.example.com`).
2. **Your computer asks a DNS server** to find the IP address of that domain.
3. **The DNS server responds** with the IP address.
4. **Your browser connects** to that IP address and loads the website.

Think of DNS like your phone's contacts list:
- You search for “Mom” (domain name).
- Your phone finds her number (IP address) and calls her.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※ ADDED NOTES ※※※※※※※※※※※※※※※※※※※※
<br>
<br>
</div>

### Questions

##### What does DNS stand for?
Domain Name System
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## 2. Domain Hierarchy
<div align="center"><br><img width="600" src="https://tryhackme-images.s3.amazonaws.com/user-uploads/5c549500924ec576f953d9fc/room-content/a168c8511887fff98a6944619c4b5259.png"></div>
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※ ADDED NOTES ※※※※※※※※※※※※※※※※※※※※
<br>
<br>
</div>

|                        |                                                                                            |                                  |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    |
| ---------------------- | ------------------------------------------------------------------------------------------ | -------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| TLD (Top-Level Domain) | The last part of a domain name (e.g., .com).                                               | `.com`, `.org`, `.ca`, `.uk`     | There are two types of TLD, gTLD (Generic Top Level) and ccTLD (Country Code Top Level Domain). Historically a gTLD was meant to tell the user the domain name's purpose; for example, a .com would be for commercial purposes, .org for an organisation, .edu for education and .gov for government. And a ccTLD was used for geographical purposes, for example, .ca for sites based in Canada, .co.uk for sites based in the United Kingdom and so on. Due to such demand, there is an influx of new gTLDs ranging from .online , .club , .website , .biz and so many more. For a full list of over 2000 TLDs [click here](https://data.iana.org/TLD/tlds-alpha-by-domain.txt). |
| Second-Level Domain    | The part directly left of the TLD. Represents the main name chosen during registration.    | `tryhackme` in `tryhackme.com`   | Up to 63 characters. Only a-z, 0-9, and hyphens (-). Cannot start/end with hyphens or use consecutive hyphens.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     |
| Subdomain              | Sits to the left of the Second-Level Domain. Can be used to create subdivisions of a site. | `admin` in `admin.tryhackme.com` | A subdomain name has the same creation restrictions as a Second-Level Domain, being limited to 63 characters and can only use a-z 0-9 and hyphens (cannot start or end with hyphens or have consecutive hyphens). You can use multiple subdomains split with periods to create longer names, such as jupiter.servers.tryhackme.com. But the length must be kept to 253 characters or less.                                                                                                                                                                                                                                                                                         |
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※ ADDED NOTES ※※※※※※※※※※※※※※※※※※※※
<br>
<br>
</div>

### Questions

##### What is the maximum length of a subdomain?
63

##### Which of the following characters cannot be used in a subdomain ( 3 b _ - )?
_

##### What is the maximum length of a domain name?
253

##### What type of TLD is .co.uk?
ccTLD
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## 3. Record Types

DNS isn't just for websites though, and multiple types of DNS record exist. We'll go over some of the most common ones that you're likely to come across.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※ ADDED NOTES ※※※※※※※※※※※※※※※※※※※※
<br>
<br>
</div>

==DEF-DNS records are entries in the **Domain Name System (DNS)** that tell the internet how to handle requests for a domain.==

### Scenario: You type **`www.example.com`** into your browser

1. **Your browser asks the DNS system: “Where is `www.example.com`?”**
    - It starts by checking DNS records.

2. **DNS checks the domain’s records (in the authoritative name server):**
    - `NS record`: Says “These servers know everything about `example.com`.”
    - `A record`: Says “`example.com` = 93.184.216.34 (the server’s IP address).”
    - `CNAME record` (if used): Might say “`www.example.com` is really just `example.com`.”

3. **The browser gets an answer:**
    - “`www.example.com` → 93.184.216.34”

4. **Browser connects to that IP address**
    - Now it knows which server to contact to load the website.

### Same domain, different request: sending an email to `user@example.com`

1. **Your email server asks DNS: “Where should I send mail for `example.com`?”**
    
2. **DNS checks for `MX records`:**
    - Example: “Mail for `example.com` should go to `mail.example.com`.”
    - And the `A record` of `mail.example.com` gives the IP.

3. **Your email server delivers the message** to the correct mail server.

|Record Type|Full Name|Purpose / What It Does|
|---|---|---|
|**A**|Address Record|Maps a domain to an **IPv4 address**.|
|**AAAA**|IPv6 Address Record|Maps a domain to an **IPv6 address**.|
|**CNAME**|Canonical Name Record|Points one domain/subdomain to another domain (alias).|
|**MX**|Mail Exchange|Defines the **mail server(s)** responsible for handling email.|
|**TXT**|Text Record|Stores arbitrary text; often used for **email security (SPF, DKIM, DMARC)** and domain verification.|
|**NS**|Name Server Record|Lists the **authoritative name servers** for the domain.|
|**SOA**|Start of Authority|Contains key domain information (primary name server, admin email, refresh times).|
|**SRV**|Service Record|Specifies location of services (e.g., VoIP, IM, SIP).|
|**PTR**|Pointer Record|Maps an **IP address back to a domain name** (reverse DNS).|
|**CAA**|Certification Authority Authorization|Specifies which **certificate authorities** can issue SSL/TLS certificates for the domain.|
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※ ADDED NOTES ※※※※※※※※※※※※※※※※※※※※
<br>
<br>
</div>
<div>
<br>
<br>
</div>

### Questions

##### What type of record would be used to advise where to send email?
MX

##### What type of record handles IPv6 addresses?
AAAA
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## 4. Making A Request
<div align="center"><br><img width="500" src="https://tryhackme-images.s3.amazonaws.com/user-uploads/5f04259cf9bf5b57aed2c476/room-content/5f04259cf9bf5b57aed2c476-1724075620083.png"></div>
1. When you request a domain name, your computer first checks its local cache to see if you've previously looked up the address recently; if not, a request to your Recursive DNS Server will be made.

2. A Recursive DNS Server is usually provided by your ISP, but you can also choose your own. This server also has a local cache of recently looked up domain names. If a result is found locally, this is sent back to your computer, and your request ends here (this is common for popular and heavily requested services such as Google, Facebook, Twitter). If the request cannot be found locally, a journey begins to find the correct answer, starting with the internet's root DNS servers.

3. The root servers act as the DNS backbone of the internet; their job is to redirect you to the correct Top Level Domain Server, depending on your request. If, for example, you request [www.tryhackme.com](http://www.tryhackme.com/), the root server will recognise the Top Level Domain of .com and refer you to the correct TLD server that deals with .com addresses.

4. The TLD server holds records for where to find the authoritative server to answer the DNS request. The authoritative server is often also known as the nameserver for the domain. For example, the name server for [tryhackme.com](http://tryhackme.com/) is [kip.ns.cloudflare.com](http://kip.ns.cloudflare.com/) and [uma.ns.cloudflare.com](http://uma.ns.cloudflare.com/). You'll often find multiple nameservers for a domain name to act as a backup in case one goes down.

5. An authoritative DNS server is the server that is responsible for storing the DNS records for a particular domain name and where any updates to your domain name DNS records would be made. Depending on the record type, the DNS record is then sent back to the Recursive DNS Server, where a local copy will be cached for future requests and then relayed back to the original client that made the request. DNS records all come with a TTL (Time To Live) value. This value is a number represented in seconds that the response should be saved for locally until you have to look it up again. Caching saves on having to make a DNS request every time you communicate with a server.
<div>
<br>
<br>
</div>

### Questions

##### What field specifies how long a DNS record should be cached for?
TTL

##### What type of DNS Server is usually provided by your ISP?
recursive

##### What type of server holds all the records for a domain?
authoritative
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## 5. Practical

Using the website on the right, we can build requests to make DNS queries and view the results. The website will also show you the command you'd need to run on your own computer if you wished to make the requests yourself.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※ ADDED NOTES ※※※※※※※※※※※※※※※※※※※※
<br>
<br>
</div>

### #nslookup

##### Run a basic lookup

```
nslookup example.com
```

This shows the **IP address** of the domain (`A` record).  
You’ll see output like:

```shell
Server:  dns.google 
Address: 8.8.8.8  

Non-authoritative answer: 
Name:    example.com 
Address: 3.184.216.34
```

- `Server` → The DNS server you’re asking.
- `Address` → Its IP.
- `Non-authoritative answer` → Means it’s from cache, not the official owner’s server.
- `Name / Address` → The actual mapping for the domain.
<div>
<br>
</div>

##### Query specific record types

You can tell `nslookup` what kind of record you want:
```
nslookup -type=A example.com     # IPv4 address 
nslookup -type=AAAA example.com  # IPv6 address 
nslookup -type=MX example.com    # Mail servers 
nslookup -type=NS example.com    # Name servers 
nslookup -type=TXT example.com   # Text records (SPF, DKIM, etc.)
```
<div>
<br>
</div>

##### Interactive mode (optional)

You can run `nslookup` by itself:

```bash
nslookup
```

Then you’ll get a prompt like:

```shell
>
```

Now you can type commands inside it:

```shell
> set type=MX 
> example.com
```

To exit, just type:

```shell
> exit
```
<div>
<br>
</div>

⚡ Pro tip: If you want to use a **different DNS server** (instead of your computer’s default), you can specify it:

```
nslookup example.com 8.8.8.8
```

Here, `8.8.8.8` is Google’s public DNS.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※ ADDED NOTES ※※※※※※※※※※※※※※※※※※※※
<br>
<br>
</div>

### Questions

##### What is the CNAME of shop.website.thm?
shops.myshopify.com

##### What is the value of the TXT record of website.thm?
THM{7012BBA60997F35A9516C2E16D2944FF}

##### What is the numerical priority value for the MX record?
30

##### What is the IP address for the A record of www.website.thm?
10.10.10.10
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## References

https://tryhackme.com/room/dnsindetail