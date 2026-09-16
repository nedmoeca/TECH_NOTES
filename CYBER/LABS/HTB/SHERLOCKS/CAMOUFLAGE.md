---
link: https://app.hackthebox.com/sherlocks/CAMouflage
difficulty: Easy
team: blue
release date: 2026-05-28
tags:
image: https://cdn.services-k8s.prod.aws.htb.systems/content/sherlocks/avatar/a1c56189-c2c1-418c-877c-453904ced993-1778691170.png
solved: true
solve date: 2026-09-16
---

<div style="text-align: center; padding: 80px 40px; page-break-after: always;">

  <img src="/ASSETS/writeup_hack_the_box_logo.png" style="width: 1220px; margin-bottom: 60px;" />

  <div><p style="font-size: 40px; font-weight: 600; margin-bottom: 40px;">CAMouflage Writeup</p></div>

  <img src="https://cdn.services-k8s.prod.aws.htb.systems/content/sherlocks/avatar/a1c56189-c2c1-418c-877c-453904ced993-1778691170.png" style="width: 400px; margin-bottom: 60px;" />

  <div style="font-size: 22px; line-height: 2.2;">
    <p style="margin: 0;">Prepared by: <a href="https://app.hackthebox.com/users/1809572">nedmoeca</a></p>
    <p style="margin: 0;">Author(s): <a href="https://app.hackthebox.com/users/1396367">M4shl3</a></p>
    <p style="margin: 0;">Difficulty: Easy</p>
    <p style="margin: 0;">Date: 16 Sep 2026</p>
  </div>

</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## Sherlock Scenario

A newly launched campaign has been detected targeting multiple users utilizing cracked applications. We received an alert indicating unusual behavior from one of our user’s laptops and performed an initial triage. Your task is to conduct a deep dive investigation to determine the root cause and extent of the incident.
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

### 1.1 Extract the evidence archive

**Why this step**

The Sherlock ships as a single password-protected ZIP. Nothing can be parsed until both layers are unpacked, and the inner archive name carries a collection timestamp that bounds the whole investigation.

**Command**

```bash
7z x CAMouflage.zip -phacktheblue
```

**Breakdown**

| Component | Meaning | Simple Explanation |
| --- | --- | --- |
| `7z` | 7-Zip command-line binary | The archive tool that handles ZIP, 7z, CAB and more |
| `x` | Extract with full paths | Unpacks while preserving the folder structure inside |
| `CAMouflage.zip` | Target archive | The file downloaded from HTB |
| `-phacktheblue` | Password switch | `-p` with the password glued directly to it — HTB uses `hacktheblue` for every Sherlock |

**Result**

```
Everything is Ok

Size:       50191925
Compressed: 50192159
```

Directory contents after extraction:

```
2025-06-21T205150_output.zip  CAMouflage.zip
```

**What this gives you**

Key finding: the inner archive is named `2025-06-21T205150_output.zip`, a collection timestamp of **2025-06-21 20:51:50**. Treat that as the upper bound of the investigation window. No artifact in this dataset post-dates it.

**Next**

Unpack the inner archive to establish which forensic artifact categories the collection contains.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
<br>
</div>

### 1.2 Unpack the inner collection and identify the acquisition tool

**Why this step**

The outer archive yielded a second ZIP rather than artifacts. Extracting it reveals both the acquisition tooling used and the artifact scope available for the rest of the investigation.

**Command**

```bash
7z x 2025-06-21T205150_output.zip -oevidence && ls -la evidence
```

**Breakdown**

| Component | Meaning | Simple Explanation |
| --- | --- | --- |
| `7z x` | Extract with full paths | Preserves the collection's original directory tree |
| `2025-06-21T205150_output.zip` | Target archive | The inner archive produced by step 1.1 |
| `-oevidence` | Output directory switch | `-o` glued to the destination name — sends output into `evidence/` instead of the current directory |
| `&&` | Conditional chain | Runs the listing only if extraction succeeded |
| `ls -la evidence` | Long listing, including hidden entries | Shows what landed at the top level of the collection |

**Result**

```
Comment = Created by KAPE version 1.3.0.2 on 2025-06-21T20:51:50.9968970Z

Everything is Ok

Folders: 46
Files: 663
Size:       395529820
Compressed: 50191925
```

```
total 260
drwxrwxr-x 3 nedmoeca nedmoeca   4096 Sep 16 06:39 .
drwxrwxr-x 3 nedmoeca nedmoeca   4096 Sep 16 06:39 ..
-rw-rw-r-- 1 nedmoeca nedmoeca 240679 Jun 21  2025 2025-06-21T20_51_50_9968970_CopyLog.csv
-rw-rw-r-- 1 nedmoeca nedmoeca  11328 Jun 21  2025 2025-06-21T20_51_50_9968970_SkipLog.csv.csv
drwxrwxr-x 7 nedmoeca nedmoeca   4096 Sep 16 06:39 C
```

**Theory — what a KAPE collection is**

KAPE (Kroll Artifact Parser and Extractor) is a triage tool. Rather than imaging an entire disk, it copies a curated set of high-value forensic files off a live Windows host — registry hives, Prefetch, event logs, the `$MFT` and `$J` USN journal, browser history, SRUM and BAM databases — and writes them into a folder tree that mirrors their original paths. That mirroring is why the top level here is a bare `C` directory: every file underneath sits at the same path it occupied on the victim's `C:\` drive.

Two logs accompany every collection. `CopyLog.csv` records each file KAPE successfully copied, with its source path, size and timestamps. `SkipLog.csv` records files KAPE deliberately skipped, usually zero-byte files or ones already collected. Both are investigative assets in their own right — the CopyLog is a searchable inventory of the entire collection, which makes it a faster way to locate a filename than walking the tree.

**What this gives you**

Key finding: the evidence is a **KAPE 1.3.0.2 triage collection** taken **2025-06-21T20:51:50.9968970Z**, containing **663 files across 46 folders** totalling roughly **395 MB uncompressed**.

Note what this is *not*: there is no memory image and no disk image. Every answer must come from on-disk artifacts — execution evidence (Prefetch, SRUM, BAM, Amcache), filesystem metadata (`$MFT`, `$J`), registry hives, and event logs. Questions phrased around "in memory" therefore resolve to strings recoverable from dropped files on disk, not from a RAM capture.

**Next**

Map the collection's directory tree to confirm which artifact categories are present before targeting any single one.

<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## Task 1
### Based on forensic artifacts, at what precise timestamp did the user first execute the Cracked App installer?

==Answer==
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## Task 2
### When did the installer process terminate?

==Answer==
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## Task 3
### What was the first file dropped by the malware post-installation?

==Answer==
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## Task 4
### What is the SHA-256 hash of the .cab archive extracted during execution?

==Answer==
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## Task 5
### What command did the malware use to extract content files from that .cab file?

==Answer==
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## Task 6
### During execution, the malware performed AV/EDR checks. How many security product-related strings did it search for in memory or processes?

==Answer==
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## Task 7
### After the batch file was executed, what was the name of the process that ran?

==Answer==
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## Task 8
### What is the original name for that process?

==Answer==
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## Task 9
### What is the SHA-256 hash of the file loaded by the above identified process?

==Answer==
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## Task 10
### What is the C2 Domain name address contacted by the malware?

==Answer==
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

