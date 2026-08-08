---
tags:
  - JR_PENETRATION_TESTER
  - INTRODUCTION_TO_WEB_HACKING
  - THM
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

## 1. What Is Content Discovery?

Firstly, we should ask, in the context of web application security, what is content? Content can be many things, a file, video, picture, backup, a website feature. When we talk about content discovery, we're not talking about the obvious things we can see on a website; it's the things that aren't immediately presented to us and that weren't always intended for public access.  
  
This content could be, for example, pages or portals intended for staff usage, older versions of the website, backup files, configuration files, administration panels, etc.  
  
There are three main ways of discovering content on a website which we'll cover. Manually, Automated and OSINT (Open-Source Intelligence).  
  
Start the AttackBox (by clicking the blue "Start AttackBox" button), and the machine on this task.
<div>
<br>
<br>
</div>

### Questions

##### What is the Content Discovery method that begins with M?
Manually
<div>
<br>
</div>

##### What is the Content Discovery method that begins with A?
Automated
<div>
<br>
</div>

##### What is the Content Discovery method that begins with O?
OSINT
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## 2. Manual Discovery - Robots.txt

There are multiple places we can manually check on a website to start discovering more content. 

### Robots.txt

==**`robots.txt`** is a simple text file that websites use to give instructions to web crawlers (like Googlebot, Bingbot, or other search engine bots) about which pages or files they’re allowed or not allowed to crawl and index.==

It’s part of the **Robots Exclusion Protocol (REP)** — a standard for managing crawler access to your site.

**Key points about `robots.txt`:**
- 📍 **Location:** It must be placed in the root directory of your website. For example, `https://example.com/robots.txt`.
- ⚙️ **Syntax:** It uses simple rules like `User-agent` to specify which bot the rule applies to, and `Disallow` or `Allow` to tell bots what they can or can’t crawl.
- 🚫 **Purpose:** Common uses include blocking private areas (like `/admin/`), preventing indexing of duplicate content, or managing crawl budgets for large sites.
- ❗ **Limitations:** It’s not a security feature — it only _requests_ bots to stay away; it doesn’t prevent them from accessing the content if they choose to ignore the rules.


**Example `robots.txt`:**

```txt
User-agent: *
Disallow: /private/
Allow: /public/
```

This means:
- `User-agent: *` → applies to all bots.
- `Disallow: /private/` → bots should not crawl anything under `/private/`.
- `Allow: /public/` → bots can crawl `/public/`.


This file gives us a great list of locations on the website that the owners don't want us to discover as penetration testers.

Take a look at the robots.txt file on the Acme IT Support website to see if they have anything they don't want to list - To do this open Firefox on the AttackBox, and enter the url: [http://MACHINE_IP/robots.txt](http://machine_ip/robots.txt)[](https://lab_web_url.p.thmlabs.com/robots.txt) (_this URL will update 2 minutes from when you start the machine in task 1_)
<div>
<br>
<br>
</div>

### Questions

##### What is the directory in the robots.txt that isn't allowed to be viewed by web crawlers?
/staff-portal

![[Pasted image 20250703122229.png]]
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## 3. Manual Discovery - Favicon

### Favicon

The favicon is a small icon displayed in the browser's address bar or tab used for branding a website.
 
![](https://tryhackme-images.s3.amazonaws.com/user-uploads/5efe36fb68daf465530ca761/room-content/42a556740d021fc3e7111a689dcadb28.png)

Sometimes when frameworks are used to build a website, a favicon that is part of the installation gets leftover, and if the website developer doesn't replace this with a custom one, this can give us a clue on what framework is in use. OWASP host a database of common framework icons that you can use to check against the targets favicon [https://wiki.owasp.org/index.php/OWASP_favicon_database](https://wiki.owasp.org/index.php/OWASP_favicon_database). Once we know the framework stack, we can use external resources to discover more about it (see next section).

#### Practical Exercise

On the AttackBox, open firefox and enter the url [https://static-labs.tryhackme.cloud/sites/favicon/](https://static-labs.tryhackme.cloud/sites/favicon/) here you'll see a basic website with a note saying "Website coming soon...", if you look at your tabs you'll notice an icon that confirms this site is using a favicon.

Viewing the page source you'll see line six contains a link to the images/favicon.ico file. 

![](https://tryhackme-images.s3.amazonaws.com/user-uploads/5efe36fb68daf465530ca761/room-content/1f1217249bf0edf74c8e6d0ba58bbc58.png)  

If you run the following command on the AttackBox, it will download the favicon and get its md5 hash value which you can then lookup on the  
[https://wiki.owasp.org/index.php/OWASP_favicon_database](https://wiki.owasp.org/index.php/OWASP_favicon_database).

```shell-session
user@machine$ curl https://static-labs.tryhackme.cloud/sites/favicon/images/favicon.ico | md5sum
```

Note: This curl will fail on the AttackBox if you are a free user, in which case you should use a VM for this. If your hash ends with 427e then your curl failed, and you may need to try it again. You could also run this on Windows in PowerShell as shown below.  

```markup
PS C:\> curl https://static-labs.tryhackme.cloud/sites/favicon/images/favicon.ico -UseBasicParsing -o favicon.ico
PS C:\> Get-FileHash .\favicon.ico -Algorithm MD5 
```

<div>
<br>
<br>
</div>

### Questions

##### What framework did the favicon belong to?
cgiirc

```shell
root@ip-10-10-86-179:~# curl https://static-labs.tryhackme.cloud/sites/favicon/images/favicon.ico | md5sum
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
100  1406  100  1406    0     0  28120      0 --:--:-- --:--:-- --:--:-- 28120
f276b19aabcb4ae8cda4d22625c6735f  -
```

![[Pasted image 20250831104154.png]]
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## 4. Manual Discovery - Sitemap.xml

### Sitemap.xml

Unlike the robots.txt file, which restricts what search engine crawlers can look at, the sitemap.xml file gives a list of every file the website owner wishes to be listed on a search engine. These can sometimes contain areas of the website that are a bit more difficult to navigate to or even list some old webpages that the current site no longer uses but are still working behind the scenes.
 
Take a look at the sitemap.xml file on the Acme IT Support website to see if there's any new content we haven't yet discovered: [http://10.10.127.158/sitemap.xml](http://10.10.127.158/sitemap.xml)[](http://10.10.127.158/sitemap.xml) (open this in the FireFox browser on the AttackBox).
<div>
<br>
<br>
</div>

### Questions

##### What is the path of the secret area that can be found in the sitemap.xml file?
/s3cr3t-area

![[Pasted image 20250831111227.png]]
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## 5. Manual Discovery - HTTP Headers

When we make requests to the web server, the server returns various HTTP headers. These headers can sometimes contain useful information such as the webserver software and possibly the programming/scripting language in use. In the below example, we can see the webserver is NGINX version 1.18.0 and runs PHP version 7.4.3. Using this information, we could find vulnerable versions of software being used. Try running the below curl command against the web server, where the **-v** switch enables verbose mode, which will output the headers (there might be something interesting!).

```shell-session
user@machine$ curl http://10.10.127.158 -v
*   Trying 10.10.127.158:80...
* TCP_NODELAY set
* Connected to 10.10.127.158 (10.10.127.158) port 80 (#0)
> GET / HTTP/1.1
> Host: 10.10.127.158
> User-Agent: curl/7.68.0
> Accept: */*
> 
* Mark bundle as not supporting multiuse
< HTTP/1.1 200 OK
< Server: nginx/1.18.0 (Ubuntu)
< X-Powered-By: PHP/7.4.3
< Date: Mon, 19 Jul 2021 14:39:09 GMT
< Content-Type: text/html; charset=UTF-8
< Transfer-Encoding: chunked
< Connection: keep-alive
```
<div>
<br>
<br>
</div>

### Questions

##### What is the flag value from the X-FLAG header?
THM{HEADER_FLAG}

```shell
root@ip-10-10-86-179:~# curl http://10.10.204.3 -v
*   Trying 10.10.204.3:80...
* TCP_NODELAY set
* Connected to 10.10.204.3 (10.10.204.3) port 80 (#0)
> GET / HTTP/1.1
> Host: 10.10.204.3
> User-Agent: curl/7.68.0
> Accept: */*
> 
* Mark bundle as not supporting multiuse
< HTTP/1.1 200 OK
< Server: nginx/1.18.0 (Ubuntu)
< Date: Sun, 31 Aug 2025 08:45:15 GMT
< Content-Type: text/html; charset=UTF-8
< Transfer-Encoding: chunked
< Connection: keep-alive
< X-FLAG: THM{HEADER_FLAG}
< 
<!--
This page is temporary while we work on the new homepage @ /new-home-beta
-->
<!DOCTYPE html>
<html lang="en">
<head>
    <title>Acme IT Support - Home</title>
    <meta charset="utf-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1">
        <link rel="stylesheet" href="https://pro.fontawesome.com/releases/v5.12.0/css/all.css" integrity="sha384-ekOryaXPbeCpWQNxMwSWVvQ0+1VrStoPJq54shlYhR8HzQgig1v5fas6YgOqLoKz" crossorigin="anonymous">
        <link rel="stylesheet" href="/assets/bootstrap.min.css">
    <link rel="stylesheet" href="/assets/style.css">
</head>
<body>
    <nav class="navbar navbar-inverse navbar-fixed-top">
        <div class="container">
            <div class="navbar-header">
                <button type="button" class="navbar-toggle collapsed" data-toggle="collapse" data-target="#navbar" aria-expanded="false" aria-controls="navbar">
                    <span class="sr-only">Toggle navigation</span>
                    <span class="icon-bar"></span>
                    <span class="icon-bar"></span>
                    <span class="icon-bar"></span>
                </button>
                <a class="navbar-brand" href="#">Acme IT Support</a>
            </div>
            <div id="navbar" class="collapse navbar-collapse">
                <ul class="nav navbar-nav">
                    <li class="active"><a href="/">Home</a></li>
                    <li><a href="/news">News</a></li>
                    <li><a href="/contact">Contact</a></li>
                    <li><a href="/customers">Customers</a></li>
                </ul>
            </div><!--/.nav-collapse -->
        </div>
    </nav><div class="container" style="padding-top:60px">
    <h1 class="text-center">Acme IT Support</h1>
    <div class="row">
        <div class="col-md-8 col-md-offset-2 text-center">
            <img src="/assets/staff.png">
            <p class="welcome-msg">Our dedicated staff are ready <a href="/secret-page">to</a> assist you with your IT problems.</p>
        </div>
    </div>
</div>
<script src="/assets/jquery.min.js"></script>
<script src="/assets/bootstrap.min.js"></script>
<script src="/assets/site.js"></script>
</body>
</html>
<!--
Page Generated in 0.03477 Seconds using the THM Framework v1.2 ( https://static-labs.tryhackme.cloud/sites/thm-web-framework )
* Connection #0 to host 10.10.204.3 left intact
```
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## 6. Manual Discovery - Framework Stack

### Framework Stack

Once you've established the framework of a website, either from the above favicon example or by looking for clues in the page source such as comments, copyright notices or credits, you can then locate the framework's website. From there, we can learn more about the software and other information, possibly leading to more content we can discover.

Looking at the page source of our Acme IT Support website ([http://MACHINE_IP](http://machine_ip/)), you'll see a comment at the end of every page with a page load time and also a link to the framework's website, which is [https://static-labs.tryhackme.cloud/sites/thm-web-framework](https://static-labs.tryhackme.cloud/sites/thm-web-framework). Let's take a look at that website. Viewing the documentation page gives us the path of the framework's administration portal, which gives us a flag if viewed on the Acme IT Support website.
<div>
<br>
<br>
</div>

### Questions

##### What is the flag from the framework's administration portal?
THM{CHANGE_DEFAULT_CREDENTIALS}

![[Pasted image 20250703153911.png]]
![[Pasted image 20250703154009.png]]
![[Pasted image 20250703154100.png]]
![[Pasted image 20250703154142.png]]
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## 7. OSINT - Google Hacking / Dorking

==**DEF-Google Dorking** (also called **Google Hacking**) is the practice of using advanced Google search operators to find information that is not easily accessible through normal search queries.==
You can, for instance, pick out results from a certain domain name using the **site:** filter, for example (site:[tryhackme.com](http://tryhackme.com/)) you can then match this up with certain search terms, say, for example, the word admin (site:tryhackme.com admin) this then would only return results from the [tryhackme.com](http://tryhackme.com/) website which contain the word admin in its content. You can combine multiple filters as well. Here is an example of more filters you can use:

| Operator             | Use                                                                                   | Example              |
| -------------------- | ------------------------------------------------------------------------------------- | -------------------- |
| `site:`              | Limit search to a domain                                                              | `site:example.com`   |
| `filetype:` / `ext:` | Find specific file types (returns results which are a particular file extension)      | `filetype:pdf`       |
| `intitle:`           | Keywords in page title (returns results that contain the specified word in the title) | `intitle:"index of"` |
| `inurl:`             | Keywords in URL (returns results that have the specified word in the URL)             | `inurl:admin`        |
| `allintext:`         | Keywords in page body                                                                 | `allintext:password` |
| `cache:`             | Google’s cached version                                                               | `cache:example.com`  |
| `OR`                 | Combine terms                                                                         | `"login" OR "admin"` |
<div>
<br>
<br>
</div>

### Google Dorking & Search Operators — Quick Reference

#### Official Google Search Operator Resources

- **Google Advanced Search Page:**  
    [https://www.google.com/advanced_search](https://www.google.com/advanced_search)
 
- **Google Search Help — Refine Web Searches:**  
    [https://support.google.com/websearch/answer/2466433?hl=en](https://support.google.com/websearch/answer/2466433?hl=en)
   
#### Comprehensive Google Dork Database

- **Exploit-DB Google Hacking Database (GHDB):**  
    [https://www.exploit-db.com/google-hacking-database](https://www.exploit-db.com/google-hacking-database)

#### Community Cheat Sheets & Collections

- **GitHub:** Search _“Google Dork Cheat Sheet GitHub”_ for user-maintained lists.  
    Example:  
    [https://github.com](https://github.com/) → search for **Google Dork Cheat Sheet**.

- **HackTricks (by Carlos Polop):** Practical OSINT & Dorking tricks.  
    [https://book.hacktricks.xyz](https://book.hacktricks.xyz/)

- **Offensive Security:** Resources often mention advanced dorking for pentesting.
<div>
<br>
<br>
</div>

### Questions

##### What Google dork operator can be used to only show results from a particular site?
site:
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## 8. OSINT - #Wappalyzer

**Wappalyzer** is a popular tool (and browser extension) used to **identify the technologies** used by websites. It tells you what frameworks, programming languages, CMSs, eCommerce platforms, analytics tools, JavaScript libraries, server software, and more a website is using — just by scanning its public-facing code.
<div>
<br>
<br>
</div>

### What Wappalyzer Does

When you visit a website with Wappalyzer:

- It inspects the HTML, HTTP headers, JavaScript, cookies, and other hints.
- Then it matches these fingerprints to known patterns.
- You see a list of technologies like:
    - CMS: WordPress, Joomla, Drupal
    - Web Server: Apache, Nginx, LiteSpeed
    - Programming Languages: PHP, Python, Ruby
    - Frameworks: React, Angular, Laravel
    - E-commerce: Shopify, WooCommerce
    - Analytics: Google Analytics, Hotjar, Facebook Pixel

### How to Use Wappalyzer

1. **Browser Extension**
    - Available for Chrome, Firefox, Edge, Safari.
    - After installing, click the icon when you visit any site — it instantly shows detected tech.

2. **Online Lookup**
    - You can check a website manually on [wappalyzer.com](https://www.wappalyzer.com/) → Enter the URL → Get the report.

3. **APIs & Integrations**
    - Wappalyzer also has a paid API and command-line tools.
    - Useful for automated tech reconnaissance and competitive research.

### Alternatives

If you’re interested in other tools like Wappalyzer, here are some:

- #BuiltWith: [builtwith.com](https://www.builtwith.com/) — more detailed reports.
- #WhatRuns: Another lightweight browser extension.
- #Netcraft: For deep server info and hosting history.
<div>
<br>
<br>
</div>

### Questions

##### What online tool can be used to identify what technologies a website is running?
Wappalyzer
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## 9. OSINT - #Wayback_Machine

The **Wayback Machine** is an incredibly useful tool for exploring the history of websites — it’s basically an internet time machine!

- It is a digital archive of the World Wide Web, run by the **Internet Archive** (a non-profit).
- URL: https://archive.org/web/
- It lets you **view snapshots of websites as they looked at different points in time** — sometimes going back to the 1990s.
<div>
<br>
<br>
</div>

### Questions

##### What is the website address for the Wayback Machine?
https://archive.org/web/
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## 10. OSINT - GitHub

To understand GitHub, you first need to understand Git. 

==DEF-Git is a **version control system** that tracks changes to files in a project.== Working in a team is easier because you can see what each team member is editing and what changes they made to files. When users have finished making their changes, they commit them with a message and then push them back to a central location (repository) for the other users to then pull those changes to their local machines. 

====DEF-GitHub is a hosted version of Git on the internet==. Repositories can either be set to public or private and have various access controls. You can use GitHub's search feature to look for company names or website names to try and locate repositories belonging to your target. Once discovered, you may have access to source code, passwords or other content that you hadn't yet found.
<div>
<br>
<br>
</div>

### Questions

##### What is Git?
version control system
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## 11. OSINT - S3 Buckets

S3 Buckets are a storage service provided by Amazon AWS, allowing people to save files and even static website content in the cloud accessible over HTTP and HTTPS. The owner of the files can set access permissions to either make files public, private and even writable. Sometimes these access permissions are incorrectly set and inadvertently allow access to files that shouldn't be available to the public. The format of the S3 buckets is http(s)://**{name}.**[**s3.amazonaws.com**](http://s3.amazonaws.com/) where {name} is decided by the owner, such as [tryhackme-assets.s3.amazonaws.com](http://tryhackme-assets.s3.amazonaws.com/). S3 buckets can be discovered in many ways, such as finding the URLs in the website's page source, GitHub repositories, or even automating the process. One common automation method is by using the company name followed by common terms such as **{name}**-assets, **{name}**-www, **{name}**-public, **{name}**-private, etc.
<div>
<br>
<br>
</div>

### Questions

##### What URL format do Amazon S3 buckets end in?
.s3.amazonaws.com
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## 12. Automated Discovery

## What is Automated Discovery?

Automated discovery is the process of using tools to discover content rather than doing it manually. This process is automated as it usually contains hundreds, thousands or even millions of requests to a web server. These requests check whether a file or directory exists on a website, giving us access to resources we didn't previously know existed. This process is made possible by using a resource called wordlists.
<div>
<br>
<br>
</div>

### What are wordlists?

==DEF-Wordlists are text files that contain long lists of commonly used words based on use cases.== For example, a password wordlist would include the most frequently used passwords, whereas we're looking for content in our case, so we'd require a list containing the most commonly used directory and file names. An excellent resource for wordlists that is preinstalled on the THM AttackBox is [https://github.com/danielmiessler/SecLists](https://github.com/danielmiessler/SecLists) which Daniel Miessler curates.
<div>
<br>
<br>
</div>

### Automation Tools

Although there are many different content discovery tools available, all with their features and flaws, we're going to cover three which are preinstalled on our attack box, ffuf, dirb and gobuster. 

On the AttackBox execute the following three commands, targeting the Acme IT Support website and see what results you get. 

#### Using [[FFUF|ffuf]]

```shell-session
user@machine$ ffuf -w /usr/share/wordlists/SecLists/Discovery/Web-Content/common.txt -u http://MACHINE_IP/FUZZ
```

#### Using [[DIRB|dirb]]

```shell-session
user@machine$ dirb http://MACHINE_IP/ /usr/share/wordlists/SecLists/Discovery/Web-Content/common.txt
```

#### Using [[GOBUSTER|Gobuster]]

```shell-session
user@machine$ gobuster dir --url http://MACHINE_IP/ -w /usr/share/wordlists/SecLists/Discovery/Web-Content/common.txt
```

Using the results from the commands above, please answer the below questions:  
<div>
<br>
<br>
</div>

### Questions

##### What is the name of the directory beginning "/mo...." that was discovered?
/monthly

```shell
root@ip-10-10-149-158:~# ffuf -s -w /usr/share/wordlists/SecLists/Discovery/Web-Content/common.txt -u http://10.10.204.3/FUZZ
assets
contact
customers
development.log
monthly
news
private
robots.txt
sitemap.xml
```
<div>
<br>
</div>

##### What is the name of the log file that was discovered?
/development.log
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## References

https://tryhackme.com/room/contentdiscovery