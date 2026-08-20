
<div style="text-align: center; padding: 80px 40px; page-break-after: always;">

  <img src="/ASSETS/writeup_try_hack_me_logo.png" style="width: 1220px; margin-bottom: 60px;" />

  <div><p style="font-size: 40px; font-weight: 600; margin-bottom: 40px;">Carnage Writeup</p></div>

  <img src="https://tryhackme.com/_next/image?url=https%3A%2F%2Fcdn-images.tryhackme.com%2Froom-icons%2F6ba48271aa3457f8488e1029031ed058.png&w=96&q=75" style="width: 400px; margin-bottom: 60px;" />

  <div style="font-size: 22px; line-height: 2.2;">
    <p style="margin: 0;">Prepared by: nedmoeca</p>
    <p style="margin: 0;">Author: tryhackme</p>
    <p style="margin: 0;">Difficulty: Medium</p>
    <p style="margin: 0;">Date: 18 Aug 2026</p>
  </div>

</div>
<!-- PAGE BREAK -->

## Summary

Category: **Network Forensics**

Traffic Analysis first, **Malware Analysis** second. It fits the first because the entire engagement is reading a single packet capture; HTTP objects, TLS certificate metadata, DNS queries, and connection timing; to reconstruct what happened on this host. It fits the second because the traffic you're reconstructing is a malicious Word macro pulling a ZIP dropper and then beaconing to Cobalt Strike C2 infrastructure, so several steps are really about recognizing malware behavior patterns rather than about packets.

---

## Placeholder legend

| Token | Where to get it |
| --- | --- |
| `<ANALYST_HANDLE>` | Your own name/handle on the writeup |
| `<PCAP_PATH>` | Path to the capture on the deployed lab machine (Analysis folder on the Desktop) — ⚠ verify per spawn |
| `<STREAM_ZIP>` | TCP stream index Wireshark auto-applies when you Follow the `documents.zip` download — ⚠ regenerates per spawn |
| `<STREAM_C2>` | TCP stream index Wireshark auto-applies when you Follow the post-infection POST conversation — ⚠ regenerates per spawn |
| `<ZIP_HOST_IP>` | Destination IP of the first HTTP `GET` for the ZIP |
| `<TLS_DOMAIN_IP>` | Source IP of the first HTTPS malicious-download domain (from the SNI column) |
| `<CS_IP_1>`, `<CS_IP_2>` | The two Cobalt Strike server IPs, confirmed on VirusTotal Community tab |
| `<POSTINFECT_IP>` | IP of the plaintext-HTTP post-infection C2 |

> Frame numbers, stream indices, and displayed-packet counts vary by spawn and by Wireshark version. Anything in `< >` must be substituted.

---

## Task 1 Scenario

No commands. Deploy the attached machine (split-screen view; click **Show Split View** if it does not load).

> Do not directly interact with any domain or IP address in this room.

---

## Task 2 Traffic Analysis

### Setup — load the capture and fix the time format

```
Open Wireshark → File → Open → <PCAP_PATH>
View → Time Display Format → UTC Date and Time of Day
View → Time Display Format → Seconds
```

> The last two lines are separate toggles in the same menu — the first sets the format, the second the precision. Set precision to whole seconds or your timestamps will carry microseconds the answer format rejects.

---

### Q1 First HTTP connection to the malicious IP (date/time)

Display filter:

```
http
```

Read the **Time** column of the first request frame.

---

### Q2 Name of the downloaded zip file

Same `http` filter — read the request URI of that first `GET`.

---

### Q3 Domain hosting the malicious zip

Expand **Hypertext Transfer Protocol** on that frame and read the `Host:` header (also visible in the ASCII byte pane).

---

### Q4 Name of the file inside the zip (without downloading it)

```
Right-click the GET frame → Follow → HTTP Stream
```

Auto-applied filter:

```
tcp.stream eq <STREAM_ZIP>
```

Scroll past the response headers to the body. It begins with `PK`; the stored filename follows the local file header as plain uncompressed text.

> Everything after the filename is compressed binary and renders as noise in the ASCII pane — expected, not an error.

---

### Q5 Webserver name of the malicious IP

In the same Follow HTTP Stream window, read the server response header:

```
server:
```

---

### Q6 Version from the previous question

Same response block:

```
x-powered-by:
```

> The `server:` line carries no version — the room's expected value comes from `x-powered-by`, which identifies the scripting engine, not the server.

---

### Q7 Three domains involved in malicious downloads

```
tls.handshake.type == 1
```

Add the SNI column:

```
Click any Client Hello frame → detail pane → expand:
  Transport Layer Security
    → TLSv1.2 Record Layer: Handshake Protocol: Client Hello
      → Handshake Protocol: Client Hello
        → Extension: server_name
          → Server Name Indication extension
            → Server Name
Right-click "Server Name" → Apply as Column
```

Scroll the 16:45:11–16:45:30 window and read the three hostnames.

Verify hosting-provider attribution rather than asserting it:

```
whois <TLS_DOMAIN_IP>
```

---

### Q8 Certificate authority for the first domain

```
tls.handshake.type == 11
```

Find the row whose **Source** is that domain's IP, then expand the `Certificates` subtree.

Single-frame alternative:

```
ip.addr == <TLS_DOMAIN_IP> && tls.handshake.type == 11
```

---

### Q9 The two Cobalt Strike server IPs

Identify the candidate external addresses, then confirm each on VirusTotal → **Community** tab. Answer format: sequential order.

```
Statistics → Conversations → IPv4 tab → sort by Bytes/Packets
```

---

### Q10 Host header for the first Cobalt Strike IP

```
ip.addr == <CS_IP_1> && http
```

Click the first returned frame → expand **Hypertext Transfer Protocol** → read `Host:`.

> `&& http` is what strips the TLS sessions on 443/8888 and leaves the readable plaintext request.

---

### Q11 Domain name for the first Cobalt Strike IP

VirusTotal lookup on `<CS_IP_1>` (Community tab / Relations).

---

### Q12 Domain name for the second Cobalt Strike IP

VirusTotal lookup on `<CS_IP_2>` (Community tab / Relations).

---

### Q13 Domain of the post-infection traffic

```
ip.addr == <POSTINFECT_IP> && http
```

or

```
http.request.method == POST
```

Click any POST frame → expand **Hypertext Transfer Protocol** → read `Host:`.

---

### Q14 First eleven characters the victim sends to that domain

```
Right-click the first frame in that conversation → Follow → TCP Stream
```

Auto-applied filter:

```
tcp.stream eq <STREAM_C2>
```

Read the opening bytes of the client half — the eleven characters immediately after `POST /`.

---

### Q15 Length of the first packet sent to the C2 server

```
ip.addr == <POSTINFECT_IP> && http
```

Select the earliest frame in the conversation and read the **Length** column (or the Frame branch in the detail pane).

---

### Q16 Server header for that malicious domain

In the same Follow TCP Stream window (`tcp.stream eq <STREAM_C2>`), read the server response header:

```
Server:
```

---

### Q17 Date/time of the DNS query for the IP-check domain

```
frame contains "api"
```

Then confirm no earlier query exists by targeting the field directly:

```
dns.qry.name contains "ipify"
```

Read the earliest timestamp in the **Time** column. Answer format: `yyyy-mm-dd hh:mm:ss UTC`.

> The broad `frame contains` search truncates in the window. Always re-run against the specific field when the answer depends on a value being earliest or unique.

---

### Q18 Domain in that DNS query

Read the query name from the **Info** column, or expand **Domain Name System (query) → Queries** in the detail pane.

---

### Q19 First `MAIL FROM` address observed

```
smtp.req.command == "MAIL"
```

Sort by the **No.** column to restore capture order, then read the earliest frame.

> Filter on the verb only — the `FROM:` portion is a parameter held in `smtp.req.parameter`, not part of the command value. Sorting by any other column interleaves the phases and hides which command came first.

---

### Q20 How many packets were observed for the SMTP traffic

```
smtp
```

Read **Displayed** in the status bar at the bottom of the window.

---

## Fill-in table (per-spawn values)

| Token | Value | Source |
| --- | --- | --- |
| `<PCAP_PATH>` | | Analysis folder on the lab machine Desktop |
| `<STREAM_ZIP>` | | Auto-applied by Follow → HTTP Stream (Q4) |
| `<STREAM_C2>` | | Auto-applied by Follow → TCP Stream (Q14) |
| `<ZIP_HOST_IP>` | | Destination of the first HTTP GET (Q1) |
| `<TLS_DOMAIN_IP>` | | Source of the first HTTPS download domain (Q7) |
| `<CS_IP_1>` | | VirusTotal-confirmed Cobalt Strike server (Q9) |
| `<CS_IP_2>` | | VirusTotal-confirmed Cobalt Strike server (Q9) |
| `<POSTINFECT_IP>` | | Destination of the repeating POSTs (Q13) |

---

## Host map

| Host | Role |
| --- | --- |
| Victim workstation (`10.9.23.x`) | Source of all outbound activity in the capture |
| Domain controller / DNS / DHCP (`10.9.23.5`) | Expected internal infrastructure — baseline, not a finding |
| Compromised web hosts (external) | Serve the ZIP dropper and follow-on files |
| Cobalt Strike servers (external) | Beacon C2 |
| Post-infection C2 (external) | Plaintext HTTP POST channel on port 80 |
| External mail servers (external, port 25) | Malspam relay targets |

> Everything in this room is read out of one offline capture — no traffic is generated toward any of the hosts above.

---

## References
