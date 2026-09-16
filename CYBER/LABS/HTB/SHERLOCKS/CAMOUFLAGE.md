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
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
<br>
</div>

### 1.3 Map the collection tree and scope the available artifacts

**Why this step**

KAPE mirrors original Windows paths, so the directory tree is itself an artifact inventory. Knowing which categories exist — and which do not — determines every technique available for the ten tasks and rules out approaches that have no supporting evidence.

**Command**

```bash
find evidence/C -maxdepth 4 -type d | sort
```

**Breakdown**

| Component | Meaning | Simple Explanation |
| --- | --- | --- |
| `find` | Recursive filesystem walker | Walks the tree and prints what matches |
| `evidence/C` | Search root | The mirrored `C:\` drive of the victim host |
| `-maxdepth 4` | Depth limit | Stops four levels down so the output stays readable instead of listing all 663 files |
| `-type d` | Directories only | Shows structure, not contents |
| `\| sort` | Alphabetical ordering | Groups related paths together so categories are obvious |

**Result**

```
evidence/C
evidence/C/$Extend
evidence/C/$Extend/$RmMetadata
evidence/C/$Extend/$RmMetadata/$TxfLog
evidence/C/$Recycle.Bin
evidence/C/$Recycle.Bin/S-1-5-21-1403634729-3147206146-238420168-500
evidence/C/ProgramData
evidence/C/ProgramData/Microsoft
evidence/C/ProgramData/Microsoft/Windows
evidence/C/ProgramData/Microsoft/Windows/Start Menu
evidence/C/Users
evidence/C/Users/Administrator
evidence/C/Users/Administrator/AppData
evidence/C/Users/Administrator/AppData/Local
evidence/C/Users/Administrator/AppData/LocalLow
evidence/C/Users/Administrator/AppData/Roaming
evidence/C/Users/Administrator/Desktop
evidence/C/Users/Default
evidence/C/Users/Default/AppData
evidence/C/Users/Default/AppData/Roaming
evidence/C/Users/Public
evidence/C/Users/Public/Desktop
evidence/C/Windows
evidence/C/Windows/AppCompat
evidence/C/Windows/AppCompat/Programs
evidence/C/Windows/prefetch
evidence/C/Windows/ServiceProfiles
evidence/C/Windows/ServiceProfiles/LocalService
evidence/C/Windows/ServiceProfiles/NetworkService
evidence/C/Windows/System32
evidence/C/Windows/System32/config
evidence/C/Windows/System32/config/systemprofile
evidence/C/Windows/System32/SRU
evidence/C/Windows/System32/Tasks
evidence/C/Windows/System32/Tasks/Microsoft
evidence/C/Windows/System32/winevt
evidence/C/Windows/System32/winevt/logs
```

**Theory — reading a KAPE tree as an artifact inventory**

Each directory in a KAPE collection is shorthand for a specific forensic capability. Learn to translate the tree on sight:

| Path | Artifact | What it answers | Simple Explanation |
| --- | --- | --- | --- |
| `C/$Extend` | `$J` USN Journal | Every file create, rename, write and delete, with timestamps | A change log the filesystem keeps of everything that happened to every file |
| `C/` (root) | `$MFT` | Metadata for every file on the volume, including deleted entries | The master index card catalogue of the disk |
| `C/Windows/prefetch` | `.pf` files | Which executables ran, when, how often, and what they loaded | Windows' own performance cache that accidentally doubles as an execution log |
| `C/Windows/AppCompat/Programs` | `Amcache.hve` | Executable paths, SHA-1 hashes, first-seen times | A registry hive recording binaries the system has encountered |
| `C/Windows/System32/SRU` | `SRUDB.dat` | Per-process network bytes sent/received, per user | The System Resource Usage Monitor — proves a process talked to the network |
| `C/Windows/System32/config` | `SYSTEM`, `SOFTWARE`, `SAM` hives | Services, BAM/DAM execution records, installed software | Core registry — BAM lives in `SYSTEM` and records last execution per user |
| `C/Windows/System32/Tasks` | Scheduled task XML | Persistence via the task scheduler | Jobs Windows was told to run automatically |
| `C/Windows/System32/winevt/logs` | `.evtx` event logs | Process creation, PowerShell, service installs, DNS queries | Windows' built-in audit trail |
| `C/Users/Administrator/AppData` | `NTUSER.DAT`, browser data, roaming payloads | User-scoped activity, download history, dropped files | Where per-user settings and most malware staging lives |
| `C/$Recycle.Bin/S-1-5-21-…-500` | `$I`/`$R` pairs | Files deleted by that user | Deleted-file recovery, with original path and delete time |

**What this gives you**

Key finding: the collection covers **execution artifacts** (Prefetch, Amcache, BAM via `SYSTEM`, SRUM), **filesystem history** (`$MFT`, `$J`), **registry**, **scheduled tasks**, **event logs** and the **Recycle Bin** — the complete standard triage set for reconstructing a malware execution timeline.

Note the single meaningful user profile: `Administrator`, SID `S-1-5-21-1403634729-3147206146-238420168-500`. The `-500` relative identifier marks the built-in local administrator account, so the malware executed with full local privileges and no escalation step is required anywhere in this chain.

Record the negative findings explicitly, since they close off techniques:

| Absent artifact | Consequence |
| --- | --- |
| No memory image (`.raw`, `.mem`, `.dmp`) | Questions worded around "in memory" must be answered from strings inside files recovered on disk |
| No packet capture (`.pcap`, `.pcapng`) | The C2 domain must come from DNS-related event logs, the DNS cache, or the payload's own configuration — not from traffic analysis |
| No full disk image | Only files KAPE targeted exist; anything outside its targets is recoverable as metadata only, via `$MFT` and `$J` |

**Next**

Pivot to execution artifacts to establish the installer's identity and first-run time, starting with Prefetch — the artifact that records executable launches with the precision Task 1 demands.

---

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

