---
link: https://app.hackthebox.com/sherlocks/MangoBleed?tab=play_sherlock
description: Very Easy
release date: 2025-12-31
tags:
image: https://cdn.services-k8s.prod.aws.htb.systems/content/sherlocks/avatar/a0b95fe3-116c-47c8-9ab5-e86ae3049a38.png
solved:
solve date:
---
<div style="text-align: center; padding: 80px 40px; page-break-after: always;">

  <img src="/ASSETS/HTB Logo.png" style="width: 1220px; margin-bottom: 60px;" />

  <div><p style="font-size: 40px; font-weight: 600; margin-bottom: 40px;">MangoBleed Writeup</p></div>

  <img src="https://cdn.services-k8s.prod.aws.htb.systems/content/sherlocks/avatar/a0b95fe3-116c-47c8-9ab5-e86ae3049a38.png" style="width: 400px; margin-bottom: 60px;" />

  <div style="font-size: 18px; line-height: 2.2;">
    <p style="margin: 0;">Prepared by: nedmoeca</p>
    <p style="margin: 0;">Author(s): CyberJunkie</p>
    <p style="margin: 0;">Difficulty: Very Easy</p>
    <p style="margin: 0;">Date: 08 Jul 2026</p>
  </div>

</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## Sherlock Scenario

You were contacted early this morning to handle a high‑priority incident involving a suspected compromised server. The host, mongodbsync, is a secondary MongoDB server. According to the administrator, it's maintained once a month, and they recently became aware of a vulnerability referred to as MongoBleed. As a precaution, the administrator has provided you with root-level access to facilitate your investigation.

You have already collected a triage acquisition from the server using UAC. Perform a rapid triage analysis of the collected artifacts to determine whether the system has been compromised, ==identify any attacker activity (initial access, persistence, privilege escalation, lateral movement, or data access/exfiltration), and summarize your findings with an initial incident assessment and recommended next steps.==
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->

## Summary


<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## Triage & Initial Analysis

You were handed a single file, `MangoBleed.zip`, as the starting evidence package for this investigation. Before touching its contents, the first step in any analysis is simply to confirm what you have on disk — this is basic forensic hygiene: know your working directory before you start extracting or modifying anything.

```shell
┌──(kali㉿kali)-[~/nedmoeca/HTB/Sherlocks/MangoBleed]
└─$ ls
MangoBleed.zip
```

`MangoBleed.zip` is a compressed archive — a single file that bundles many files/folders together and shrinks their size. Since the contents are unknown until extracted, and the archive is password-protected (a common practice for CTF evidence files, so that antivirus tools or search engines don't flag/index attacker artifacts contained inside), the next logical step is to extract it using a tool capable of reading `.zip` archives and handling that password prompt.

**Command:** `7z x MangoBleed.zip`

**Breakdown:**

- `7z`
    - Description: The command-line executable for **7-Zip**, a file archiver utility capable of creating and extracting many archive formats (`.zip`, `.7z`, `.rar`, `.tar`, etc.).
    - Purpose: Chosen because it reliably handles password-protected ZIP archives and reports extraction integrity (whether the file is corrupted).
- `x`
    - Description: The 7-Zip sub-command for "extract with full paths" — as opposed to `e` (extract, flattening all files into one folder), `x` preserves the original folder structure inside the archive.
    - Purpose: Preserving the original folder structure is critical in forensics — the folder hierarchy created by the acquisition tool carries meaning (as you'll see below), and flattening it would destroy that context.
- `MangoBleed.zip`
    - Description: The target archive to extract, specified as a positional argument.
    - Purpose: Points 7-Zip at the evidence file provided for this Sherlock.

**Result:**

```shell
┌──(kali㉿kali)-[~/nedmoeca/HTB/Sherlocks/MangoBleed]
└─$ 7z x MangoBleed.zip 

7-Zip 25.01 (x64) : Copyright (c) 1999-2025 Igor Pavlov : 2025-08-03
 64-bit locale=en_US.UTF-8 Threads:4 OPEN_MAX:1024, ASM

Scanning the drive for archives:
1 file, 32727809 bytes (32 MiB)

Extracting archive: MangoBleed.zip
--            
Path = MangoBleed.zip
Type = zip
Physical Size = 32727809

    
Enter password (will not be echoed):
Everything is Ok                                                           

Folders: 678
Files: 4196
Size:       100216130
Compressed: 32727809
```

If your extraction succeeded, listing the working directory again confirms what new folder(s) were created, and gives you the name you'll need for all subsequent navigation.

```shell
┌──(kali㉿kali)-[~/nedmoeca/HTB/Sherlocks/MangoBleed]
└─$ ls                             
MangoBleed.zip  uac-mongodbsync-linux-triage
```

The folder name `uac-mongodbsync-linux-triage` tells you two important things before you even open a single file:

1. **`uac`** — this data was collected using **UAC (Unix-like Artifacts Collector)**, an open-source live-triage tool. UAC runs on a live (running) Linux system and systematically dumps hundreds of small text files capturing system state — running processes, network connections, logs, user accounts, installed packages, and more — without needing to shut the machine down or take a full disk image. Think of it like doing vital-sign checks on a patient (pulse, blood pressure, temperature) rather than performing full surgery — it's a snapshot, not a deep dive into every byte on disk.
2. **`mongodbsync`** — this is the hostname of the compromised machine, matching the scenario briefing that the affected server is a secondary MongoDB server.

Before navigating into it, it's worth doing a first-pass listing of the top level of the folder, followed by a full recursive listing (`tree`) to understand how UAC organized everything — this is the map you'll use to know where to look for specific evidence later (logs, process info, config files, etc.).

```shell
┌──(kali㉿kali)-[~/nedmoeca/HTB/Sherlocks/MangoBleed]
└─$ ls -la uac-mongodbsync-linux-triage 
total 28
drwxrwxr-x  7 kali kali 4096 Dec 29  2025  .
drwxrwxr-x  3 kali kali 4096 Jul  8 07:51  ..
drwxrwxr-x  2 kali kali 4096 Dec 29  2025  bodyfile
drwxrwxr-x  2 kali kali 4096 Dec 29  2025  hash_executables
drwxrwxr-x  9 kali kali 4096 Dec 29  2025  live_response
drwxrwxr-x 10 kali kali 4096 Dec 29  2025 '[root]'
drwxrwxr-x  2 kali kali 4096 Dec 29  2025  system
```

The five top-level folders each serve a distinct purpose in a UAC triage:

| Folder             | Contents                                                                                        | Purpose                                                                                                                               |
| ------------------ | ----------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------- |
| `bodyfile`         | `bodyfile.txt`                                                                                  | A timeline-formatted (MAC time — Modified/Accessed/Changed) listing of every file on the filesystem, used for timeline reconstruction |
| `hash_executables` | `.md5` / `.sha1` files                                                                          | Cryptographic hashes of executable files, used to detect known-malicious or tampered binaries                                         |
| `live_response`    | Subfolders like `network`, `process`, `hardware`, `storage`, `packages`, `containers`, `system` | Output of dozens of live commands (`ps`, `netstat`, `lsof`, etc.) run at acquisition time — a snapshot of the running system's state  |
| `[root]`           | A near-complete copy of the filesystem's `/etc`, `/home`, `/var`, `/usr`, `/root`, etc.         | The actual files pulled off disk — configs, logs, home directories — where most log-analysis work happens                             |
| `system`           | Files like `suid.txt`, `sgid.txt`, `world_writable_files.txt`, `hidden_files.txt`               | Results of automated checks for common privilege-escalation and persistence indicators                                                |
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## Task 1
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## Task 2
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## Task 3
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## Task 4
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## Task 5
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## Task 6
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## Task 7
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## Task 8
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## Task 9
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## Task 10
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## Lessons Learned
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->

## Remediation Recommendations
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## References

