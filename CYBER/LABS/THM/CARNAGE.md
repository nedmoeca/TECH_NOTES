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

### Q1 What was the date and time for the first HTTP connection to the malicious IP?

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

```
http
```

Type that in the display filter bar and press Enter.

That's the entire filter. A bare protocol name matches any frame Wireshark dissected as that protocol — no field, no comparison operator. The bar should turn green. If it turns red you've typo'd it; if it's yellow something else is wrong with the expression.

**Results:**

![[Pasted image 20260819131337.png]]

Frame 1735 is your answer to Q1, Q2 and Q3 all at once.

- `2021-09-24 16:44:38`, a `GET` for `/incidunt-consequatur/documents.zip`, going to `85.187.128.24`. The `Host:` header is visible in the ASCII pane at the bottom even without expanding the tree — `Host: attirenepal.com`. That's the domain, and it's a legitimate-looking Nepalese clothing site, almost certainly a compromised WordPress install rather than attacker-registered infrastructure.

- Also worth noting before we move on: the filter reduced 70,873 packets to 394, and look at what dominates the list. From 16:46 onward it's a steady drumbeat of `POST` requests to `208.91.128.6` with long random-looking URL paths, one every ~15 seconds, each answered with a `200 OK (text/html)`. Regular interval, tiny payloads, encoded-looking paths — that's beaconing, and it's already visible before we've done any dedicated hunting. Park that somewhere in the back of your head or in you rough notes.
<div align="center">
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
</div>

### Q2 What is the name of the zip file that was downloaded?

==documents.zip==
<div align="center">
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
</div>

### Q3 What was the domain hosting the malicious zip file?

==attirenepal.com==
<div align="center">
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
</div>

### Q4 Without downloading the file, what is the name of the file in the zip file?

==chart-1530076591.xls==
<div align="center">
<br>
<br>
</div>

#### Reassemble the download conversation with Follow HTTP Stream

Then, for Q4, Q5 and Q6 — all three come from the server's _response_, not the request. Right-click frame 1735 and choose **Follow → HTTP Stream**.

Applied filter: `tcp.stream eq 73`

| Component               | Purpose                                                                                     | Simple Explanation                                                                      |
| ----------------------- | ------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------- |
| `Follow → HTTP Stream`  | Reassembles all packets in the TCP conversation in sequence and renders the payload as text | Stitches the scattered chunks back into the full request-and-reply, readable end to end |
| `tcp.stream eq 73`      | Auto-applied display filter isolating this one conversation                                 | Wireshark numbers each conversation; this pins the view to conversation 73              |
| Client/server colouring | Distinguishes direction                                                                     | Victim's outbound data in one colour, server's reply in another                         |

**Results:**

![[Pasted image 20260819133319.png]]

```
GET /incidunt-consequatur/documents.zip HTTP/1.1
Host: attirenepal.com
Connection: keep-alive
Upgrade-Insecure-Requests: 1
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36 Edg/93.0.961.52
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9
Accept-Encoding: gzip, deflate
Accept-Language: en

HTTP/1.1 200 OK
Connection: Keep-Alive
Keep-Alive: timeout=5, max=100
x-powered-by: PHP/7.2.34
set-cookie: PHPSESSID=3de638a4b99bd63f8f7b0ca7e3b6f14c; path=/
content-description: File Transfer
content-type: application/octet-stream
content-disposition: attachment; filename=documents.zip
content-transfer-encoding: binary
expires: 0
cache-control: must-revalidate, post-check=0, pre-check=0
pragma: public
transfer-encoding: chunked
date: Fri, 24 Sep 2021 16:44:06 GMT
server: LiteSpeed
strict-transport-security: max-age=63072000; includeSubDomains
x-frame-options: SAMEORIGIN
x-content-type-options: nosniff

10000
PK.........d8S.a../...........chart-1530076591.xlsUT	....Ma..Maux..............[w\...>..[.U@.X@,..K.&.
[remainder: 199kB of compressed binary data, not human-readable] 

Stream metadata: 1 client pkt, 148 server pkts, 1 turn
```

**Findings:**

Key finding: the ZIP is a container delivering an Office document, not the final payload.
<div align="center">
<br>
</div>

###### Reading a filename out of a ZIP without extracting it:

In the HTTP Stream window, just past the response headers to where the file body begins. The body starts with `PK`.

A ZIP archive begins each stored file with a _local file header_. Its first two bytes are always `50 4B` — ASCII `PK`, the initials of Phil Katz, who created the format. That signature is how tools recognise a ZIP regardless of its extension. A short run of version, flag, compression, and timestamp fields follows, and then the filename appears as plain uncompressed text.

The filename is deliberately left unencoded so that archive tools can list contents without decompressing anything. That property is what makes this step safe: reading `chart-1530076591.xlsx` off the wire requires no extraction, no execution, and no contact with the host. Everything after the filename is compressed data and renders as noise in the ASCII view, which is expected and not an error.

<div align="center">
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
</div>

### Q5 What is the name of the webserver of the malicious IP from which the zip file was downloaded?

==LiteSpeed==
<div align="center">
<br>
</div>

In the Follow HTTP Stream window, read the `server:` header within the server's response block.

```
HTTP/1.1 200 OK
...
server: LiteSpeed
```

**Notes:**  
The `server:` header is voluntary self-identification by the webserver software. It can be suppressed or falsified, so it is an indicator rather than proof — but it is rarely tampered with on a compromised legitimate host, since the attacker's goal there is to leave the site looking normal.

LiteSpeed is a commercial drop-in replacement for Apache, common on shared hosting because it reads Apache configuration files directly. Seeing it on a small retail site is unremarkable.
<div align="center">
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
</div>

### Q6 What is the version of the webserver from the previous question?

==PHP/7.2.34==
<div align="center">
<br>
</div>

Read the `x-powered-by` header in the same response block.

```
x-powered-by: PHP/7.2.34
...
server: LiteSpeed
```

**Notes:**  
The `server: LiteSpeed` line carries **no version number**. LiteSpeed is configured here to suppress its own version, which is standard hardening. The value the room expects comes from `x-powered-by`, which identifies the _scripting engine_ behind the server, not the server itself.

The question is kinda sloppy. Answer `PHP/7.2.34` to satisfy the room, but I'd record it accurately in any real report as: _"LiteSpeed; version undisclosed. PHP 7.2.34 disclosed via `x-powered-by`."_

The version is still a genuine finding. PHP 7.2 reached end of security support in November 2020, ten months before this capture. An unpatched, end-of-life PHP branch on a public-facing WordPress site is a plausible explanation for how the host came to be serving attacker files in the first place.
<div align="center">
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
</div>

### Q7 Malicious files were downloaded to the victim host from multiple domains. What were the three domains involved with this activity?

==finejewels.com.au, thietbiagt.com, new.americold.com==
<div align="center">
<br>
</div>

These transfers occurred over HTTPS, so they are invisible to the `http` filter used for Q1–Q6. The file contents are encrypted and unrecoverable, but the requested domain name is transmitted in cleartext inside each TLS Client Hello.

Every encrypted connection starts with an unencrypted negotiation. The two sides have to agree on how they'll encrypt before they can encrypt anything — you can't use a shared secret you haven't established yet. That negotiation is the TLS handshake, and the Client Hello is its opening message.

Because the Client Hello arrives before any keys exist, it is necessarily plaintext. That makes it one of the highest-value frames in any capture involving HTTPS.

There is exactly one Client Hello per connection attempt. Filtering for them gives you a clean one-row-per-connection list of everywhere a host tried to go.

```
Display filter:  tls.handshake.type == 1
```

Add a column exposing the requested hostname:

```
Click any Client Hello frame → in the detail pane expand:
  Transport Layer Security
    → TLSv1.2 Record Layer: Handshake Protocol: Client Hello
      → Handshake Protocol: Client Hello
        → Extension: server_name (len=22)
          → Server Name Indication extension
            → Server Name: <value>
Right-click "Server Name" → Apply as Column
```

The column pulls one specific field out of every packet and prints it as a table cell.

So when you right-clicked `Server Name` and chose **Apply as Column**, Wireshark noted the field name behind that line and added a column configured to display it. Now, for every row in the packet list, it asks: does this packet contain a field called `tls.handshake.extensions_server_name`? If yes, print the value. If no, leave the cell blank.

Then scroll to the window 16:45:11–16:45:30.

**Results:**

![[Pasted image 20260819143253.png]]

`finejewels.com.au` (`148.72.192.206`) and `new.americold.com` (`148.72.53.144`) fall within the same `148.72.0.0/16` GoDaddy shared-hosting range. Two compromised sites on one hosting provider suggests a shared root cause — reused credentials or a common unpatched CMS component — rather than three independent intrusions.

The claim happens to be right — GoDaddy operates that block for shared hosting — but you shouldn't take it on my word and neither should a report. Verify it properly:

```
whois 148.72.192.206
```
<div align="center">
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
</div>

### Q8 Which certificate authority issued the SSL certificate to the first domain from the previous question?

==GoDaddy==
<div align="center">
<br>
<br>
</div>

The Client Hello from Q7 carries the request but the certificate is in the server's reply, so switch to the Certificate handshake message and locate the response from `finejewels.com.au`'s address.

```
Display filter:  tls.handshake.type == 11
```

Find the row where the **Source** is `148.72.192.206` — that's `finejewels.com.au` replying. Should be a second or two after 16:45:11, then expand:

![[Pasted image 20260819145214.png]]

Single-frame alternative:

```
ip.addr == 148.72.192.206 && tls.handshake.type == 11
```

**Breakdown:**

| Component                   | Purpose                                           | Simple Explanation                                                              |
| --------------------------- | ------------------------------------------------- | ------------------------------------------------------------------------------- |
| `tls.handshake.type == 11`  | Certificate message only                          | One row per server presenting its identity, rather than per connection attempt  |
| `ip.addr == 148.72.192.206` | Restricts to the `finejewels.com.au` conversation | Skips scrolling — `ip.addr` matches source or destination                       |
| `Certificates` subtree      | Container holding the presented chain             | Servers send their own certificate plus the intermediates needed to validate it |
<div align="center">
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
</div>

### Q9 What are the two IP addresses of the Cobalt Strike servers? Use VirusTotal (the Community tab) to confirm if IPs are identified as Cobalt Strike C2 servers. (answer format: enter the IP addresses in sequential order)

==185.106.96.158, 185.125.204.174==
<div align="center">
<br>
</div>

![[Pasted image 20260819151642.png]]

![[Pasted image 20260819151557.png]]


<div align="center">
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
</div>

### Q10 What is the Host header for the first Cobalt Strike IP address from the previous question?

==ocsp.verisign.com==
<div align="center">
<br>
</div>

```
Display filter:  ip.addr == 185.106.96.158 && http
```

Click the first returned frame, then expand **Hypertext Transfer Protocol** in the detail pane.

**Breakdown:**

|Component|Purpose|Simple Explanation|
|---|---|---|
|`ip.addr == 185.106.96.158`|Matches the C2 address as either source or destination|Captures both the beacon's requests and the server's replies|
|`&& http`|Restricts to frames the HTTP dissector claimed|Filters out the TLS sessions on 443/8888, leaving readable plaintext|
|Expand `Hypertext Transfer Protocol`|Exposes individual header fields|The Host header is not shown in the packet list summary|

**Result:**

![[Pasted image 20260819152607.png]]
<div align="center">
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
</div>

### Q11 What is the domain name for the first IP address of the Cobalt Strike server? You may use VirusTotal to confirm if it's the Cobalt Strike server (check the Community tab).

==survmeter.live==
<div align="center">
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
</div>

### Q12 What is the domain name of the second Cobalt Strike server IP?  You may use VirusTotal to confirm if it's the Cobalt Strike server (check the Community tab).

==securitybusinpuff.com==
<div align="center">
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
</div>

### Q13 What is the domain name of the post-infection traffic?

==maldivehost.net==
<div align="center">
<br>
</div>
**How to find it:**

```
Display filter:  ip.addr == 208.91.128.6 && http
or
http.request.method == POST
```

Click any POST frame, expand **Hypertext Transfer Protocol**, read the `Host:` line.

**Result:**

![[Pasted image 20260819153237.png]]

Key finding: a second, independent malware channel runs alongside the Cobalt Strike beacons.

- Post-infection C2 domain: `maldivehost.net` at `208.91.128.6`, plaintext HTTP on port 80
- Activity begins 16:46:16 — approximately seven minutes before the first Cobalt Strike connection (16:53:23) and nine before the second (16:55:08)

<div align="center">
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
</div>

### Q14 What are the first eleven characters that the victim host sends out to the malicious domain involved in the post-infection traffic?

==zLIisQRWZI9==
<div align="center">
<br>
</div>

**How to find it:**

```
Right-click the first frame in the maldivehost.net conversation → Follow → TCP Stream
Auto-applied filter:  tcp.stream eq 104
```

Read the opening bytes of the client half of the stream.

**Result:**

![[Pasted image 20260819154337.png]]

```
POST /zLIisQRWZI9/OQsaDixzHTgtfjMcGypGenpldWF5eWV9f3k= HTTP/1.1
Host: maldivehost.net
Content-Length: 112

Dw8YBxsEGmYFAAEJfR4NQkMmLTYqZDk5KyQmORGQg1xEBo4Lzk/EyYrMi1hOT8vIyM7IhcNPzsOKjguFxgkLSIiJCxFRgwFAgIIDQUZGBoFD0JF
```

Character-by-character from the start of the client's transmission:

```
P  O  S  T  /  z  L  I  i  s  Q  R  W  Z  I  9
               └─────────────────────────────┘
                  first 11 after "POST /"
```
<div align="center">
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
</div>

### Q15 What was the length for the first packet sent out to the C2 server?

==281==
<div align="center">
<br>
</div>

**How to find it:**

```
Display filter:  ip.addr == 208.91.128.6 && http
```

Scroll to the earliest frame in the conversation (16:46:16), select it, and read the frame length from the detail pane's Frame branch or the packet list's Length column.

**Result:**

![[Pasted image 20260819154747.png]]

```
3822  2021-09-24 16:46:16  10.9.23.102 → 208.91.128.6  HTTP  281  POST /zLIisQRWZI9/OQsaDixzHTgtfjMcGypGenpldWF5eWV9f3k=
```
<div align="center">
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
</div>

### Q16 What was the Server header for the malicious domain from the previous question?

==Apache/2.4.49 (cPanel) OpenSSL/1.1.1l mod_bwlimited/1.4==
<div align="center">
<br>
</div>

**How to find it:**

In the same Follow TCP Stream window (`tcp.stream eq 104`), read the `Server:` line in the server's response block.

**Result:**

![[Pasted image 20260819155737.png]]

```
HTTP/1.1 200 OK
Date: Fri, 24 Sep 2021 16:46:15 GMT
Server: Apache/2.4.49 (cPanel) OpenSSL/1.1.1l mod_bwlimited/1.4
X-Powered-By: PHP/5.6.40
Content-Length: 302
Strict-Transport-Security: ...max-age=15552000...
Connection: close
Content-Type: text/html; charset=UTF-8

eXp7QUVCQ0FBfn15eXl/
enN8ekJBQ0JGQnpzeWJ+eXtleHllf3xBRUJDQUELDhkAGAAbZwIDBQh8GQ5GQicqNS51OD4oICc6I0VGCHAXGTwuODgQIiozKmI9Pi4kID8jFgo8Pw8rPy0TGSUqISY1LUJFCAQDBQsJBBgfGQEOQ0JBRUJDQUEBBAQQQUVCQ0FBAQQEDkFFQkNBQQEEBA5BRUJDQUFCQUNCRkJGQEJFRUZHQUVGQUdGRkZCRUZBRUJDQUFCQUNCRkJGQEJFRUZHQUVGQUdGRkZBRUJDQUFCQUNCRkJGQEJFRUZHQUVGQUdGQUVCQ0FBQUNCRkJGQEJFRUZHQVVGQVc=
```
<div align="center">
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
</div>

### Q17 The malware used an API to check for the IP address of the victim’s machine. What was the date and time when the DNS query for the IP check domain occurred? (answer format: yyyy-mm-dd hh:mm:ss UTC)

==2021-09-24 17:00:04==
<div align="center">
<br>
</div>

**How to find it:**

```
Display filter:  frame contains "api"
```

Locate `api.ipify.org` among the results, then confirm no earlier query exists:

```
Display filter:  dns.qry.name contains "ipify"
```

Read the earliest timestamp in the Time column.

**Breakdown:**

|Component|Purpose|Simple Explanation|
|---|---|---|
|`frame contains "api"`|Raw byte-string search across the entire frame|Finds the text anywhere in the packet without knowing which field holds it|
|`dns.qry.name`|The queried name inside a DNS request|Targets the specific field rather than searching blindly|
|`contains "ipify"`|Substring match on that field|Catches the name regardless of subdomain or trailing components|

**Result:**

```
Packets: 70873 · Displayed: 8 (0.0%)

27836  2021-09-24 17:02:35  10.9.23.102 → 10.9.23.5  DNS  73  Standard query 0x5250 A api.ipify.org
26756  2021-09-24 17:02:17  10.9.23.102 → 10.9.23.5  DNS  73  Standard query 0x8d97 A api.ipify.org
25279  2021-09-24 17:00:59  10.9.23.102 → 10.9.23.5  DNS  73  Standard query 0x8eed A api.ipify.org
24147  2021-09-24 17:00:04  10.9.23.102 → 10.9.23.5  DNS  73  Standard query 0xc92c A api.ipify.org

24149  2021-09-24 17:00:04  10.9.23.5 → 10.9.23.102  DNS  299  Standard query response 0xc92c A api.ipify.org
       CNAME nagano-19599.herokussl.com
       CNAME elb097307-934924932.us-east-1.elb.amazonaws.com
       A 54.243.45.255  A 50.16.216.118 …
```

**What this gives you:**

Key finding: the malware polls for the victim's public IP four times in under three minutes.

- First query: `2021-09-24 17:00:04 UTC` (frame 24147, transaction ID `0xc92c`)
- Subsequent queries at 17:00:59, 17:02:17, 17:02:35 — intervals of roughly 55, 78, and 18 seconds
- All queries directed to the internal DNS server `10.9.23.5`, the domain controller established as baseline in 1.1
- Only eight frames match, confirming no earlier lookup exists

**Verification note:** the initial `frame contains "api"` filter is a broad byte search and its output was truncated by the window. Re-running against the specific `dns.qry.name` field returns the complete set and confirms 17:00:04 is genuinely first. Confirm completeness whenever an answer depends on a value being earliest or unique.

**Repeat-query pattern:** a single public-IP check is ordinary software behaviour. Four within three minutes is not. The malware is re-confirming its network position, and the polling cadence is itself an indicator worth building detection around.
<div align="center">
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
</div>

### Q18 What was the domain in the DNS query from the previous question?

==api.ipify.org==
<div align="center">
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
</div>

### Q19 Looks like there was some malicious spam (malspam) activity going on. What was the first MAIL FROM address observed in the traffic?

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
