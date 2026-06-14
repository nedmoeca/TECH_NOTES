---
tags:
  - THM
  - BLUE_TEAM_INTRODUCTION
link: https://tryhackme.com/room/networkservices-aoc2025-jnsoqbxgky
description: Discover how to scan network ports and uncover what is hidden behind them.
image: https://tryhackme-images.s3.amazonaws.com/room-icons/678ecc92c80aa206339f0f23-1761778821176
---
## Summary

| SECTION/TASK                      | FLAG             |
| --------------------------------- | ---------------- |
| Task 1. Introduction              | No answer needed |
| Task 2. Discover Network Services |                  |
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## Task 1. Introduction
### The Story

![Task banner for day 7](https://tryhackme-images.s3.amazonaws.com/user-uploads/678ecc92c80aa206339f0f23/room-content/678ecc92c80aa206339f0f23-1763378850592.png)

Christmas preparations are delayed - HopSec has breached our QA environment and locked us out! Without it, the TBFC projects can't be tested, and our entire SOC-mas pipeline is frozen. To make things worse, the server is slowly transforming into a twisted EAST-mas node.

Can you uncover HopSec's trail, find a way back into **tbfc-devqa01**, and restore the server before the bunny's takeover is complete? For this task, you'll need to check every place to hide, every opened port that bunnies left unprotected. Good luck!

![Three bad bunnies with three hidden easter eggs occupy the breached server in a Christmas theme.](https://tryhackme-images.s3.amazonaws.com/user-uploads/678ecc92c80aa206339f0f23/room-content/678ecc92c80aa206339f0f23-1763379081488.png)
<div align="center">
<br>
<br>
</div>

### Learning Objectives

- Learn the basics of network service discovery with Nmap
- Learn core network protocols and concepts along the way
- Apply your knowledge to find a way back into the server
<div align="center">
<br>
<br>
</div>

### Connecting to the Machine

Before moving forward, review the questions in the connection card shown below:

![Connection card.](https://tryhackme-images.s3.amazonaws.com/user-uploads/678ecc92c80aa206339f0f23/room-content/678ecc92c80aa206339f0f23-1761779575024.png)

Start your target machine by clicking the **Start Machine** button below. The machine will need about 2 minutes to fully boot. Additionally, start your AttackBox by clicking the **Start AttackBox** button below. The AttackBox will start in split view. In case you can not see it, click the **Show Split View** button at the top of the page.
<div align="center">
<br>
</div>

#### Set up your virtual environment

To successfully complete this room, you'll need to set up your virtual environment. This involves starting both your AttackBox (if you're not using your VPN) and Target Machines, ensuring you're equipped with the necessary tools and access to tackle the challenges ahead.
<div>
<br>
<br>
</div>

### Questions

##### I have successfully launched the target machine and the AttackBox.
==No answer needed==
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## Task 2. Discover Network Services
### Discovering Exposed Services

Although we lost access to the QA server, at least it's still active, and we know its IP address. That's good news, since now we can counterattack and hopefully find our way back. Ensure you understand basic [Networking Concepts](https://tryhackme.com/room/networkingconcepts) like network ports, and let's plan the engagement!

1. Know your target. In our case, it is the `tbfc-devqa01` server with the `MACHINE_IP` IP address.
2. Scan the IP for open ports, especially common ones like 22 for SSH and 80 for HTTP.
3. Explore what's behind the open ports, maybe it's a vulnerable web server running on port 80.
4. Exploit the exposed service, find a way in, and kick out the bad bunnies from the QA server.

Along the practical of today's task you will find three keys.  
Keep note of them since you will later need them for the web app.  
The format will be `KEYNAME:KEY`.
<div align="center">
<br>
</div>

#### The Simplest Port Scan

There are many tools you can use to scan for open ports, from preinstalled Netcat on Linux and PowerShell on Windows, to specialized, powerful tools like Nmap and Naabu. Let's use Nmap for this task and perform a basic scan from the AttackBox or your own VPN-connected attacking machine. Open a new command line terminal and run the following command:

BasicNmapScan

```shell-session
root@attackbox:~# nmap MACHINE_IP
Nmap scan report for MACHINE_IP
Host is up (0.061s latency).
PORT     STATE SERVICE
22/tcp   open  ssh
80/tcp   open  http
```

The command scanned the top 1000 most commonly used ports and reported if any services were running there. The only results you received are an opened SSH port for remote machine access and a HTTP port for a website. This means you can now access the server via SSH (if you know the password), or open the website by visiting `http://MACHINE_IP` from within the AttackBox:

![A screenshot from the tbfc-qa server, where evil bunnies left the "pwned" message.](https://tryhackme-images.s3.amazonaws.com/user-uploads/678ecc92c80aa206339f0f23/room-content/678ecc92c80aa206339f0f23-1762976351953.png)
<div align="center">
<br>
</div>

#### Scanning Whole Range

It seems like the website is defaced by bad bunnies, and we don't know the key to enter the admin panel! But worry not. We scanned just 1000 ports, but there are actually 65535 ports where other services can hide! Now let's add the `-p-` argument to scan all ports, and `--script=banner` to see what's likely behind the port:

Specifying Port Range

```shell-session
root@attackbox:~# nmap -p- --script=banner MACHINE_IP
Nmap scan report for MACHINE_IP
Host is up (0.00036s latency).
Not shown: 65531 filtered ports
PORT      STATE SERVICE
22/tcp    open  ssh
|_banner: SSH-2.0-OpenSSH_9.6p1 Ubuntu-3ubuntu13.14
80/tcp    open  http
21212/tcp open  trinket-agent
|_banner: 220 (vsFTPd 3.0.5)
25251/tcp open  unknown
|_banner: TBFC maintd v0.2\x0AType HELP for commands.
```

Looks like you found a running FTP server and some custom TBFC application. Even though FTP runs on port 21 by default, it's possible to change the port to any other one, such as 21212. Let's try accessing the FTP in anonymous mode with the `ftp` command and see if we can find our way in! You can follow the commands from the terminal below:

UsingFTPClient

```shell-session
root@attackbox:~# ftp MACHINE_IP 21212
Connected to 10.10.239.62.
Name (10.10.239.62:root): anonymous
ftp> ls
-rw-r--r--  1  ftp  ftp  13 Oct 22 16:27 tbfc_qa_key1
ftp> get tbfc_qa_key1 -
[GET HIDDEN KEY 1 FROM HERE]
ftp> ! # Will exit the FTP shell
```
<div align="center">
<br>
</div>

#### Port Scan Modes

Good job finding the first flag part. There is nothing more we can see on the FTP server, so let's move on to the custom TBFC app on port 25251. Since it is not a well-known service like HTTP or FTP, your web browser or FTP client won't know how to access it. Luckily, you can always use Netcat (`nc`), a universal tool to interact with network services:

Using Netcat Client

```shell-session
root@attackbox:~# nc -v MACHINE_IP 25251
Connection to 10.10.239.62 25251 port [tcp/*] succeeded!
TBFC maintd v0.2
Type HELP for commands.
HELP                                   # Your input/request
Commands: HELP, STATUS, GET KEY, QUIT  # Server response
[RUN THE CORRECT COMMAND TO GET HIDDEN KEY 2]
```

Once you received the key, press `CTRL+C` to exit the Netcat client.
<div align="center">
<br>
</div>

#### TCP and UDP Ports

Congratulations on the second flag! But where to look for the third one? Till now, you have scanned only TCP ports, but there are also 65535 ports for UDP, another transport protocol. And there is a chance HopSec secrets are hiding there, too! You can switch to UDP scan by specifying the `-sU` flag:

ScanningUDPPorts

```shell-session
root@attackbox:~# nmap -sU MACHINE_IP
PORT   STATE SERVICE
53/udp open  domain
[...]
```

After a minute you should see an open port 53 associated with DNS - a protocol that drives the modern web by connecting domains to IPs, and many more! DNS is a complex topic and many secrets can hide there, but let's just ask the DNS server if it knows the key by using `dig` - a command to perform advanced DNS queries:

QueryingDNSServer

```shell-session
root@attackbox:~# dig @MACHINE_IP TXT key3.tbfc.local +short
[RUN THE CORRECT COMMAND TO GET HIDDEN KEY 3]
```
<div align="center">
<br>
<br>
</div>

### On-Host Service Discovery

Now that you know all three keys to the **tbfc-devqa01** QA server, it's time to call your TBFC teammates and kick out the bad bunnies. But first, log in to the server's admin panel by visiting `http://MACHINE_IP` from within the AttackBox and access the secret admin console by submitting the combined keys:

![The terminal window you will see after combining three key parts on the tbfc-qa website.](https://tryhackme-images.s3.amazonaws.com/user-uploads/678ecc92c80aa206339f0f23/room-content/678ecc92c80aa206339f0f23-1761256003855.png)
<div align="center">
<br>
</div>

#### Listing Listening Ports

Once you have access to the console, there is no need to scan the ports, as you can simply ask the OS to list its open ports, also called listening ports. You can do it by running `ss -tunlp` (or `netstat` on older systems) inside the Secret Admin Console of the web app. In the output, you may see exactly the same services you scanned before listening on `0.0.0.0`, but also some listening on `127.0.0.1` (available only from the host itself):

Listing Listening Ports

```shell-session
tbfcapp@tbfc-devqa01:~$ ss -tunlp
Netid  State   Recv-Q  Send-Q       Local Address:Port      Peer Address:Port  Process                   
udp    UNCONN  0       0                  0.0.0.0:53             0.0.0.0:*                               
udp    UNCONN  0       0        10.10.76.132%ens5:68             0.0.0.0:*                               
tcp    LISTEN  0       50                 0.0.0.0:25251          0.0.0.0:*                               
tcp    LISTEN  0       32                 0.0.0.0:21212          0.0.0.0:*                               
tcp    LISTEN  0       4096               0.0.0.0:22             0.0.0.0:*                               
tcp    LISTEN  0       32                 0.0.0.0:53             0.0.0.0:*                               
tcp    LISTEN  0       511                0.0.0.0:80             0.0.0.0:*                               
tcp    LISTEN  0       2048             127.0.0.1:8000           0.0.0.0:*
tcp    LISTEN  0       151              127.0.0.1:3306           0.0.0.0:*                               
tcp    LISTEN  0       4096             127.0.0.1:7681           0.0.0.0:*                               
tcp    LISTEN  0       4096                  [::]:22                [::]:*                                       
```

With root permissions, you can also view the process column. However, for now, let's focus on the `3306` port, which is the default MySQL database port. Usually databases require a password for remote clients, but allow unauthenticated logins from localhost. Since you are already inside the host, let's see the database content by using the `mysql` program:

Enumerating MySQL Tables

```shell-session
tbfcapp@tbfc-devqa01:~$ mysql -D tbfcqa01 -e "show tables;"            +--------------------+                                                 | Tables_in_tbfcqa01 |                                                 +--------------------+                                                 | flags              |                                                 +--------------------+                                                 tbfcapp@tbfc-devqa01:~$ mysql -D tbfcqa01 -e "select * from flags;"    [GET YOUR FLAG HERE]    
```

Great job on finding the flag! You have exposed all bunnies' secrets and regained full access to the QA server. Now it's time to secure all ports and restore the SOC-mas preparation pipeline. But for now, answer the questions below and finish the task!
<div>
<br>
<br>
</div>

### Questions

##### What evil message do you see on top of the website?
==Answer==

##### What is the first key part found on the FTP server?
==Answer==

##### What is the second key part found in the TBFC app?
==Answer==

##### What is the third key part found in the DNS records?
==Answer==

##### Which port was the MySQL database running on?
==Answer==

##### Finally, what's the flag you found in the database?
==Answer==

##### If you enjoyed today's room, feel free to check out the [Nmap: The Basics](https://tryhackme.com/room/nmap) room.
==No answer needed==
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## References

