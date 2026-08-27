---
link: https://tryhackme.com/room/investigatingwindows
difficulty: Easy
description: Command-only reference for the Investigating Windows room (DFIR on a compromised Server 2016 host).
tags:
---

<div style="text-align: center; padding: 80px 40px; page-break-after: always;">

  <img src="/ASSETS/writeup_try_hack_me_logo.png" style="width: 1220px; margin-bottom: 60px;" />

  <div><p style="font-size: 40px; font-weight: 600; margin-bottom: 40px;">Investigating Windows Writeup</p></div>

  <img src="https://cdn-images.tryhackme.com/room-icons/ca912860a1629510138df1b796ae687f.png" style="width: 400px; margin-bottom: 60px;" />

  <div style="font-size: 22px; line-height: 2.2;">
    <p style="margin: 0;">Prepared by: nedmoeca</p>
    <p style="margin: 0;">Author(s): tryhackme, Aashir.Masood</p>
    <p style="margin: 0;">Difficulty: Easy</p>
    <p style="margin: 0;">Date: 26 Aug 2026</p>
  </div>

</div>
<!-- PAGE BREAK -->

## Summary

Category: **Blue Team: Digital Forensics & Incident Response**

**Prerequisites:** openvpn, xfreerdp (or `xfreerdp3`) — everything else runs natively on the target (`net`, `taskschd.msc`, `wf.msc`, `winver`, Explorer, Event Viewer, Notepad).

**Access:** RDP as `Administrator`. No exploitation — every step is read-only enumeration on the target.

---

## Placeholder legend

| Token | Where to get it |
| --- | --- |
| `<VPN_CONFIG>` | Your `.ovpn` file, downloaded from the THM access page (`~/Downloads/<file>.ovpn`) |
| `TARGET_IP` | ⚠ The target's IP, shown on the room page after you start the machine. Regenerates per spawn. |
| `<RDP_PASSWORD>` | ⚠ The Administrator password published on the room page. Confirm it per spawn before assuming the old one. |
| `<TARGET_HOSTNAME>` | The machine name printed by `hostname` / shown in `net user` output. Regenerates per spawn. |

> ⚠ = per-spawn value, swap before running.

---

## 0. Access

Run in a terminal you can leave open — OpenVPN holds the terminal and does not return to a prompt.

```
sudo openvpn ~/Downloads/<VPN_CONFIG>.ovpn
```

Prompts for your sudo password. Wait for `Initialization Sequence Completed` before continuing, and confirm "Connected" on the THM access page.

Start the machine on the room page and wait for the IP to appear. The box does not answer ICMP and takes a few minutes to boot — do not treat silence as failure.

```
xfreerdp /v:TARGET_IP /u:Administrator /p:'<RDP_PASSWORD>' /dynamic-resolution +clipboard /cert:ignore
```

Single-quote the password so the shell does not interpret `!`. On current Kali the binary may be `xfreerdp3`. Accept nothing at a prompt — `/cert:ignore` suppresses the certificate warning.

Everything below runs **on the target**, inside the RDP session.

---

## Task 1

### Q1 — Windows version and year

```
Win+R  →  winver
```

### Q2 — Which user logged in last

```
net user
net user Jenny
net user John
net user Administrator
```

Read the `Last logon`, `Password last set`, and `Local Group Memberships` fields.

### Q3 — When John last logged on

```
net user John
```

### Q4 — IP the system connects to at startup

```
Win+R  →  regedit  →  HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\Run
```

Read the autostart command's arguments (PsExec-style invocation) for the destination IP.

### Q5 — Accounts with administrative privileges

```
net localgroup administrators
```

### Q6 — Name of the malicious scheduled task

```
Win+R  →  taskschd.msc  →  Task Scheduler Library
```

Inspect each non-platform task, then read its configured command:

```
Task Scheduler → select the task → Actions tab
```

Candidates to inspect: `check logged in`, `Clean file system`, `falshupdate22`, `update windows`. Ignore the two `Amazon Ec2 Launch` entries, `npcapwatchdog`, `BADR`, and `BadrClient` (platform / lab agents).

A task reporting `Last Run Result: 0x800710E0` failed to run — that does not make it benign.

### Q7 — File the task ran daily

Read the `Start a program` action of `Clean file system`. Optionally open the script to identify it:

```
notepad C:\TMP\nc.ps1
```

`.ps1` files are associated with Notepad by default, so running the task opens the script rather than executing it. The script is a copy of **powercat** (https://github.com/besimorhino/powercat) — identify it by its `function powercat` first line and embedded help text.

### Q8 — Port the file listened on

Read the argument after `-l` in the task's action line. In powercat's parameter block `-l` is the `Listen` switch and the bare number binds positionally to `-p` / `Port`.

### Q9 — When Jenny last logged on

```
net user Jenny
```

### Q10 — Date of the compromise

```
Explorer → This PC → Local Disk (C:)
Explorer → This PC → Local Disk (C:) → TMP
```

Sort by **Date modified**. `C:\TMP` is not a standard Windows directory — the baseline at root is `PerfLogs`, `Program Files`, `Program Files (x86)`, `Users`, `Windows`.

### Q11 — First time Windows assigned special privileges to a new logon

```
Win+R  →  eventvwr.msc  →  Windows Logs → Security
```

Filter to **Event ID 4672** (`Special Logon`) and take the earliest entry inside the compromise window.

### Q12 — Tool used to get Windows passwords

```
Explorer → C:\TMP
notepad C:\TMP\mim-out.txt
```

Identify by the binary name and the format of its paired output file.

### Q13 — Attacker's external C2 IP

```
notepad C:\Windows\System32\drivers\etc\hosts
```

A clean Server 2016 hosts file is comments only — every uncommented line is a modification. Look for the entry pointing a well-known public hostname at routable (non-RFC1918) space.

### Q14 — Extension of the shell uploaded via the website

```
Explorer → C:\inetpub\wwwroot
```

Sort by Date modified and look for the file dropped inside the compromise window.

### Q15 — Last port the attacker opened

```
Win+R  →  wf.msc  →  Inbound Rules
```

Sort by name/creation and look for rules with an **empty Group** field, a prose justification-style name, and `Program: Any` + `Remote Address: Any`.

### Q16 — DNS poisoning target

```
notepad C:\Windows\System32\drivers\etc\hosts
```

Same file as Q13 — read the hostname on the poisoned line, not the IP.

---

## Fill-in table (per-spawn values)

| Token | Value | Source |
| --- | --- | --- |
| `TARGET_IP` | | Room page, after starting the machine |
| `<RDP_PASSWORD>` | | Room page (Task 1 access details) |
| `<VPN_CONFIG>` | | THM access page → OpenVPN config download |
| `<TARGET_HOSTNAME>` | | `hostname` on the target, or the header of `net user` output |

---

## Host map

| Host | Role | How you reach it |
| --- | --- | --- |
| Attack box (your Kali, or the THM AttackBox) | Runs the VPN and the RDP client only | Local terminal |
| `TARGET_IP` — Windows Server 2016 | The compromised host; all enumeration happens here | `xfreerdp` over the THM VPN, TCP 3389 |

No pivoting is required — there is a single target and every command above is run inside the RDP session.

## References

- Room: https://tryhackme.com/room/investigatingwindows
- powercat: https://github.com/besimorhino/powercat
