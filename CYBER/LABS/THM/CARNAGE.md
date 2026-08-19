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

#### DEF-Wireshark

When two computers talk over a network, they don't send one big message. They chop it into small chunks and send them one at a time. Each chunk is called a **packet**. Everything you do online like loading a page, sending an email, downloading a file is thousands of these small chunks flying back and forth.

A **packet capture** is a recording of all of them. It's as if someone put a recorder on the network, and it wrote down every chunk that went past, along with the exact moment it arrived. That recording gets saved to a file, usually ending in `.pcap`.

Wireshark is the player for that recording. Opening a `.pcap` doesn't put you on the network or contact anybody — it just reads a file that's sitting on your disk. The traffic in this room was recorded back in 2021 and has been dead ever since. You're reading a transcript of an old conversation, not joining a new one. That's what makes it safe to look at malware traffic this way.

Now, the useful bit. On its own, a packet is a meaningless string of numbers. Wireshark's real job is turning those numbers into something a human can read.

Think of sending a letter. There's the message you wrote, folded inside an envelope with an address on it, dropped at posta with a destination label. Three layers, each wrapping the one inside it, each with its own labelling. A packet works the same way — a small piece of your actual data, wrapped in an address saying which computer it's going to, wrapped again in information about how it should physically travel across the wire.

Wireshark unwraps those layers one at a time. It reads the outermost wrapper, works out what's inside, unwraps that, and keeps going until it reaches the actual content — a web request, a chunk of a downloaded file, whatever it happens to be. Then it lays the whole thing out as a labelled list you can click through, instead of the raw numbers you started with.

That unwrapping is why the tool is worth learning. The answers you need in this room are almost never visible in the summary line. They're a couple of layers down — a filename, a web address, a timestamp — and Wireshark has already pulled them out and labelled them for you. You just have to know where to look.
<div align="center">
<br>
</div>

##### The three panes

The window splits into three horizontal sections, and you need to understand what each one is for.

The top pane is the **packet list** — one row per frame, with columns for number, time, source, destination, protocol, length, and a summary Info string. This is your index. You scroll it, sort it, and click a row to inspect it.

The middle pane is the **packet detail tree** for whichever row you clicked. It shows the layers stacked: Frame (metadata Wireshark itself added, including arrival time), Ethernet, IP, TCP, then the application protocol. Each has a triangle you expand. Most answers in this room live inside an expanded branch — the arrival time under Frame, the `Host:` header under Hypertext Transfer Protocol, the certificate subject under TLS.

The bottom pane is the **raw bytes**, hex on the left and ASCII on the right. Click any field in the middle pane and the corresponding bytes highlight below.
<div align="center">
<br>
</div>

##### Display filters — the thing you'll actually use

The bar at the top is a display filter. It hides rows that don't match; it never deletes anything, and clearing the bar brings everything back. Type `http` and press Enter and you see only frames Wireshark decoded as HTTP.

The syntax is worth learning properly because it's the difference between finding things and scrolling for an hour. A bare protocol name (`http`, `dns`, `tls`) means "frames containing this protocol." A field comparison narrows further: `ip.addr == 10.0.0.1`, `tcp.port == 443`, `http.request.method == "POST"`. Combine with `and` / `or` / `not`. Note the field naming convention — `protocol.field` — which means once you find a field in the detail tree, you can right-click it and choose _Apply as Filter_ to have Wireshark write the correct expression for you. That trick is how most people learn field names.

One gotcha that catches everyone: `==` matches exactly, and `ip.addr` matches source _or_ destination. If you want traffic _from_ a host specifically, that's `ip.src`. Another: the bar turns green for valid syntax, red for invalid, yellow for valid-but-probably-not-what-you-meant. Yellow usually means you wrote `!=` on a field that appears twice in a frame — use `not (field == value)` instead.
<div align="center">
<br>
</div>

##### Follow Stream

Right-click a packet → Follow → TCP Stream reassembles every packet in that conversation, in order, and shows the payload as readable text. Client data in one colour, server in another. For unencrypted HTTP this hands you the full request and response — headers, filenames, and often the beginning of the transferred file. You will use this repeatedly in engagements like this. It also auto-applies a filter like `tcp.stream eq 12`, which is how you isolate one conversation out of thousands.
<div align="center">
<br>
</div>

##### Statistics menu

`Statistics → Conversations` and `Statistics → Endpoints` give you aggregate views: who talked to whom, how many packets, how many bytes. Sort by packets or bytes and outliers surface immediately. In an infection capture, the host with an implausible number of connections to a single external address is usually your beacon. `Statistics → Protocol Hierarchy` shows the proportional breakdown of what's in the file — a quick sanity check on whether you're looking at mostly TLS, mostly HTTP, or something odd.

**One mental model to carry**

Filtering answers "which frames," Follow Stream answers "what was said," and Statistics answers "what's abnormal in aggregate." Nearly every question in Carnage is one of those three.
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

So after you deploy the machine:

```
Open Wireshark → File → Open → /home/ubuntu/Desktop/Analysis/carnage.pcap
View → Time Display Format → UTC Date and Time of Day
View → Time Display Format → Seconds
```

The second and third lines are separate toggles in the same menu — the first picks the _format_, the second picks the _precision_. Set precision to whole seconds so your timestamps match the answer format without trailing microseconds you'd have to trim by hand.

What to look for once it's loaded: the Time column should read something like `2021-09-24 16:xx:xx`. Also note the total packet count in the status bar at the bottom; it tells you the scale of what you're working through.

**Result:**

![[Pasted image 20260819125348.png]]

**Findings:**
-  Capture size: 70,873 packets, and the first frame lands on 24 September 2021 at 16:43:42 UTC.
- Frame 1 is a DHCP Request from `0.0.0.0` — that's a machine asking for an IP address, which means this capture starts at the moment a host joined the network. Capture opens at the moment the host requests a DHCP lease, so the recording covers the workstation's full session from the point it joined the network onward.
- The DHCP ACK on frame 2 comes from `10.9.23.5`.
- By frame 7 the host is announcing itself as `DESKTOP-IOJC6RB` at `10.9.23.102`
	Victim workstation: `10.9.23.102`, hostname `DESKTOP-IOJC6RB`
- Frames 16–19 show it doing an LDAP service lookup for `goingfortune.com` and finding the domain controller at `10.9.23.5`
	Domain controller / DNS server / DHCP server: `10.9.23.5`, `goingfortune-dc.goingfortune.com`
- Active Directory domain: `goingfortune.com`

Treat `10.9.23.5` as expected internal infrastructure. Any sustained conversation between `10.9.23.102` and an address that is neither `10.9.23.5` nor other local `10.9.23.x` hosts is a candidate for investigation.
<div align="center">
<br>
</div>

#### Isolate HTTP requests


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
