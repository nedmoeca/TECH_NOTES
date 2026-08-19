---
link: https://tryhackme.com/room/c2carnage
difficulty: Medium
description: Apply your analytical skills to analyze the malicious network traffic using Wireshark.
tags:
image: https://tryhackme.com/_next/image?url=https%3A%2F%2Fcdn-images.tryhackme.com%2Froom-icons%2F6ba48271aa3457f8488e1029031ed058.png&w=96&q=75
solved:
solve date:
---

<div style="text-align: center; padding: 80px 40px; page-break-after: always;">

  <img src="/ASSETS/writeup_try_hack_me_logo.png" style="width: 1220px; margin-bottom: 60px;" />

  <div><p style="font-size: 40px; font-weight: 600; margin-bottom: 40px;">Carnage Writeup</p></div>

  <img src="https://tryhackme.com/_next/image?url=https%3A%2F%2Fcdn-images.tryhackme.com%2Froom-icons%2F6ba48271aa3457f8488e1029031ed058.png&w=96&q=75" style="width: 400px; margin-bottom: 60px;" />

  <div style="font-size: 18px; line-height: 2.2;">
    <p style="margin: 0;">Prepared by: nedmoeca</p>
    <p style="margin: 0;">Author: tryhackme</p>
    <p style="margin: 0;">Difficulty: Medium</p>
    <p style="margin: 0;">Date: 18 Aug 2026</p>
  </div>

</div>
<!-- PAGE BREAK -->

## Summary

Category: **Network Forensics / Traffic Analysis** first, **Malware Analysis** second. It fits the first because the entire engagement is reading a single packet capture; HTTP objects, TLS certificate metadata, DNS queries, and connection timing; to reconstruct what happened on a host you never touch. It fits the second because the traffic you're reconstructing is a malicious Word macro pulling a ZIP dropper and then beaconing to Cobalt Strike C2 infrastructure, so several steps are really about recognizing malware behavior patterns rather than about packets.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## Task 1 Scenario

Eric Fischer from the Purchasing Department at Bartell Ltd has received an email from a known contact with a Word document attachment.  Upon opening the document, he accidentally clicked on "Enable Content."  The SOC Department immediately received an alert from the endpoint agent that Eric's workstation was making suspicious connections outbound. The pcap was retrieved from the network sensor and handed to you for analysis. 

Task: Investigate the packet capture and uncover the malicious activities. 

Credit goes to Brad Duncan(opens in new tab) for capturing the traffic and sharing the pcap packet capture with InfoSec community. 

NOTE: DO NOT directly interact with any domains and IP addresses in this challenge. 

Deploy the machine attached to this task; it will be visible in the split-screen view once it is ready.

If you don't see a lab machine load, then click the Show Split View button.
<div align="center">
<br>
<br>
</div>

### Read the above.

==No Answer needed==
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## Task 2 Traffic Analysis

![](https://assets.tryhackme.com/additional/carnage/magnifier.png)  

Are you ready for the journey?

Please, load the pcap file in your Analysis folder on the Desktop into Wireshark to answer the questions below.
<div align="center">
<br>
<br>
</div>

### What was the date and time for the first HTTP connection to the malicious IP?

(**answer format**: yyyy-mm-dd hh:mm:ss)
==2021-09-24 16:44:38==
<div align="center">
<br>
</div>

By default it shows _seconds since beginning of capture_ — a float like `847.221934`. Several answers in this room want an absolute timestamp in `yyyy-mm-dd hh:mm:ss` format, and more importantly, when you correlate a DNS lookup against the TCP connection it produced, relative offsets make that painful. Absolute UTC makes ordering obvious at a glance.

The reason UTC specifically matters: a pcap stores each frame's arrival time as an epoch value. Wireshark renders that through whatever timezone the analysing machine is set to. Two analysts on the same file in different timezones will report different "answers" unless they both pin the display to UTC. This room's expected answers are in UTC, and the room VM may not be set to it locally.
<div align="center">
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
</div>

### What is the name of the zip file that was downloaded?

==documents.zip==
<div align="center">
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
</div>

### What was the domain hosting the malicious zip file?

==Answer==
<div align="center">
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
</div>

### Without downloading the file, what is the name of the file in the zip file?

==Answer==
<div align="center">
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
</div>

### What is the name of the webserver of the malicious IP from which the zip file was downloaded?

==Answer==
<div align="center">
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
</div>

### What is the version of the webserver from the previous question?

==Answer==
<div align="center">
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
</div>

### Malicious files were downloaded to the victim host from multiple domains. What were the three domains involved with this activity?

==Answer==
<div align="center">
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
</div>

### Which certificate authority issued the SSL certificate to the first domain from the previous question?

==Answer==
<div align="center">
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
</div>

### What are the two IP addresses of the Cobalt Strike servers? Use VirusTotal (the Community tab) to confirm if IPs are identified as Cobalt Strike C2 servers. (answer format: enter the IP addresses in sequential order)

==Answer==
<div align="center">
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
</div>

### What is the Host header for the first Cobalt Strike IP address from the previous question?

==Answer==
<div align="center">
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
</div>

### What is the domain name for the first IP address of the Cobalt Strike server? You may use VirusTotal to confirm if it's the Cobalt Strike server (check the Community tab).

==Answer==
<div align="center">
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
</div>

### What is the domain name of the second Cobalt Strike server IP?  You may use VirusTotal to confirm if it's the Cobalt Strike server (check the Community tab).

==Answer==
<div align="center">
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
</div>

### What is the domain name of the post-infection traffic?

==Answer==
<div align="center">
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
</div>

### What are the first eleven characters that the victim host sends out to the malicious domain involved in the post-infection traffic?

==Answer==
<div align="center">
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
</div>

### What was the length for the first packet sent out to the C2 server?

==Answer==
<div align="center">
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
</div>

### What was the Server header for the malicious domain from the previous question?

==Answer==
<div align="center">
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
</div>

### The malware used an API to check for the IP address of the victim’s machine. What was the date and time when the DNS query for the IP check domain occurred? (**answer format**: yyyy-mm-dd hh:mm:ss UTC)

==Answer==
<div align="center">
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
</div>

### What was the domain in the DNS query from the previous question?

==Answer==
<div align="center">
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
</div>

### Looks like there was some malicious spam (malspam) activity going on. What was the first MAIL FROM address observed in the traffic?

==Answer==
<div align="center">
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
</div>

### How many packets were observed for the SMTP traffic?

==Answer==
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## References
