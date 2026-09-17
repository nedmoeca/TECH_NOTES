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

A user searching for a cracked copy of Mastercam X9 downloaded a trojanised NSIS installer from attacker-controlled infrastructure and ran it with built-in Administrator privileges. The installer staged nine files into `%LOCALAPPDATA%\Temp` under a bogus `.wp5` extension, then executed an obfuscated batch script that fingerprinted eight security products, extracted an eleven-file cabinet archive with `extrac32`, and reassembled two executables from fragments using `copy /b`. The reconstructed binary was a renamed, legitimately-signed copy of the AutoIt v3 interpreter; the script it loaded was a compiled `.a3x` payload that decrypted an embedded PE in memory and injected it into `explorer.exe`. That final stage is a screen-capture and clipboard-theft module.

No malicious executable ever existed on disk as a complete file until the moment of execution, and both reassembled artifacts were deleted seconds after use. The host had no EDR, no Sysmon and no Defender telemetry, so the entire chain was reconstructed from Prefetch, BAM, the `$MFT`, the USN Journal and the dropped fragments themselves.

**Timeline (UTC, 2025-06-21)**

| Time | Event | Evidence |
| --- | --- | --- |
| 16:41 | `Download Mastercam X9 Full Crack Pc.7z` extracted | USN Journal |
| 18:33:58 | `download mastercam x9 full crack pc.exe` written to Downloads | USN Journal |
| 18:34:19 | Installer executed (first run) | Prefetch |
| 18:34:25 | Nine `.wp5` files staged to `%TEMP%` | USN Journal |
| 18:34:31 | `Mysql.wp5` copied to `Mysql.wp5.bat` | USN Journal |
| 18:34:46 | `tasklist` / `findstr` AV checks run | Prefetch |
| 18:34:48 | `extrac32 /Y Play.wp5 *.*` unpacks 11 cabinet members | USN + Prefetch |
| 18:34:49 | `Moscow.com` assembled from `MZ` + 11 fragments | USN Journal |
| 18:34:50 | `K` assembled from 7 `.wp5` fragments | USN Journal |
| 18:34:52 | `K` deleted | USN Journal |
| 18:35:01 | `Moscow.com` (AutoIt3) executes | Prefetch |
| 18:35:47 | Installer executed (second run), all artifacts rebuilt | Prefetch + USN |
| 18:36:52 | Installer process terminates | BAM |
| 20:32:29 | Installer and archive sent to the Recycle Bin | `$I` records |
| 20:51:50 | KAPE triage collection taken | Archive metadata |

**Indicators of compromise**

| Type | Value |
| --- | --- |
| SHA-256 (`Play.wp5`, cabinet) | `35efc15a41cf54a51703711e0b117b1899e4698bed1a4fdae638ebb7a3a190e0` |
| SHA-256 (`K`, compiled AutoIt) | `2b3d1561b9ae7fa2bd3f09dee28a327b5647a908113945cd2a943134822d18d0` |
| SHA-256 (`Mysql.wp5`, batch) | `ce9911c4a639b88bb349f2e1e94d6a426f185bba641b93ef93922d74e2ed387b` |
| SHA-256 (`Moscow.com`, AutoIt3) | `1300262a9d6bb6fcbefc0d299cce194435790e70b9c7b4a651e202e90a32fd49` |
| SHA-256 (injected final stage) | `268b44beaa84147c2f8bf78a1f5527144864f1da6d0833d71298bb2716d3df5d` |
| Domain (delivery) | `media.cloud839v1.cfd` |
| Domain (redirector) | `fancli.com` |
| Path | `%LOCALAPPDATA%\Temp\448887\Moscow.com` |
| Path | `%LOCALAPPDATA%\Temp\*.wp5` |
| Mutex / campaign string | `5c053eb25747389cf1861bd8adf85cc5f7d343dd0e` |

**ATT&CK mapping**

| Technique | ID | Where it appears |
| --- | --- | --- |
| Drive-by Compromise | T1189 | Bing search → `fancli.com` → `media.cloud839v1.cfd` |
| User Execution: Malicious File | T1204.002 | User runs the cracked installer |
| Command and Scripting Interpreter: Windows Command Shell | T1059.003 | `Mysql.wp5.bat` |
| Obfuscated Files or Information | T1027 | Character-level batch obfuscation, compiled AutoIt |
| Deobfuscate/Decode Files or Information | T1140 | `copy /b` reassembly, RC4 + LZNT1 |
| Masquerading: Rename System Utilities | T1036.003 | `AutoIt3.exe` → `Moscow.com` |
| System Binary Proxy Execution | T1218 | `extrac32`, `findstr`, `tasklist`, `choice` |
| Security Software Discovery | T1518.001 | Nine AV/EDR process checks |
| Virtualization/Sandbox Evasion: Time Based | T1497.003 | `ping -n 192`, `choice /t 300` |
| Process Injection | T1055.012 | Hollowing of `explorer.exe` |
| Screen Capture | T1113 | `BitBlt` + PNG encoder |
| Clipboard Data | T1115 | `OpenClipboard` / `GetClipboardData` |
| Indicator Removal: File Deletion | T1070.004 | `K` deleted after each use |


<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## Triage & Initial Analysis

### 0.1 Extract the evidence archive
**Say**

> Everything starts with the archive. Hack The Box ships every Sherlock as a password-protected
> ZIP, and the password is the same one every time — `hacktheblue`. There's no puzzle here, it's
> just the front door.
>
> What I want you watching is the *name* of what falls out, because it's already evidence. The
> collection inside is named after the exact moment it was taken off the victim machine, down to
> the sub-second. That timestamp becomes the ceiling on this entire investigation — nothing in
> this dataset can possibly post-date it. So before we've parsed a single artifact, we've bounded
> the window we're working in.


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

### 0.2 Unpack the inner collection and identify the acquisition tool
**Say**

> Notice that the first extraction didn't give us artifacts — it gave us another archive. That's
> a signal in itself: this collection was packaged by a tool, not assembled by hand.
>
> Unpacking this second layer answers two questions at the same time. First, which tool took the
> collection, and at what version — that's embedded in the archive's own comment field, so I'm
> going to let the extractor print it for us rather than go hunting. Second, and more important,
> what that tool decided was worth taking. A triage collection is a *curated* set of files, and
> the curation decides which of the ten questions we can actually answer from evidence.
>
> Watch the top-level folder that appears when this finishes. Its shape tells you how every path
> in here maps back to the victim's real drive, and you'll be reading paths for the rest of the
> session.


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

### 0.3 Map the collection tree and scope the available artifacts
**Say**

> KAPE mirrors the victim's real paths, so what we're about to print isn't just a list of folders
> — it's an inventory of everything we are *allowed* to prove.
>
> I want us to read it twice. Once for what's there, and once for what isn't. The absences are
> the more useful half of this step. They close off entire techniques, and they stop you spending
> twenty minutes hunting for a packet capture that was never collected in the first place. A lot
> of people get stuck on the last question of this box for exactly that reason.
>
> Two other things to watch. How many user profiles come back — and which one. The account name,
> and specifically the number on the end of its SID, tells us what privileges this malware
> inherited the moment it ran. That shapes everything downstream, including whether we need to
> look for a privilege-escalation step at all.


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

==Answer== `2025-06-21 18:34:19`
<div align="center">
<br>
<br>
</div>

### 1.1 Enumerate the Prefetch directory and identify the installer
**Say**

> Section 0 told us Prefetch is populated, so this is where the investigation properly begins.
>
> Here's the thing to understand about Prefetch: it is Windows trying to be helpful and
> accidentally becoming a witness. Its actual job is to cache what a program needs so it starts
> faster next time. The side effect is a record that the program ran at all, when it ran, and how
> many times. Nobody enabled it. Nobody configured it. Which is precisely why it's still here on
> a host with no EDR and no Sysmon — there was nothing for the attacker to switch off.
>
> We're going to list the directory before we parse anything, and I know that sounds like a
> throwaway step. It isn't. It's the highest-value minute in this box. There are a lot of entries
> in here, and reading them by eye tells you the *shape* of the attack before you've looked at a
> single timestamp.
>
> So as these scroll past, sort them into three piles in your head. Normal Windows background
> machinery. Ordinary software installs and updates. And then — the one that matters — Microsoft's
> own signed utilities turning up somewhere they've got no business being. That third pile is the
> story of this box. Also watch for anything that simply isn't a Windows binary at all.


**Why this step**

Section 0.3 confirmed `C/Windows/prefetch` is populated. Prefetch is the artifact purpose-built to answer "when did this executable run" — Windows writes a `.pf` file the first time a program launches and updates it on every subsequent run, retaining the last eight execution timestamps and a cumulative run counter. Listing the directory identifies the installer by name before any parsing begins.

**Command**

```bash
ls evidence/C/Windows/prefetch/ | wc -l && ls evidence/C/Windows/prefetch/
```

**Breakdown**

| Component | Meaning | Simple Explanation |
| --- | --- | --- |
| `ls evidence/C/Windows/prefetch/` | List directory contents | Shows every `.pf` file collected |
| `\| wc -l` | Count lines | Gives the total number of prefetch entries at a glance |
| `&&` | Conditional chain | Runs the full listing only if the count succeeded |

**Theory — how Prefetch filenames are built**

A prefetch filename has three parts: the executable's name in uppercase, a hyphen, and an eight-character hexadecimal hash, followed by `.pf`. So `NOTEPAD.EXE-D8414F97.pf` means `notepad.exe` ran from a path whose hash is `D8414F97`.

That hash is computed from the **full path** the executable ran from, not its contents. Two consequences matter for an investigation. First, the same binary launched from two different directories produces two different `.pf` files — which is why the listing you see here shows nine `SETUP.EXE-*.pf` entries and fifteen `SVCHOST.EXE-*.pf` entries. Second, the filename is truncated to 29 characters before the hash, so long executable names are cut off mid-word.

Prefetch is enabled by default on Windows workstations and disabled by default on servers and on SSD-backed systems in some configurations. Its presence here means the host is a workstation-class Windows build, and that execution evidence should be reliable.

**Result**

```
178
 7Z2407-X64.EXE-68D141D4.pf                   MSCORSVW.EXE-8CE1A322.pf                  SVCHOST.EXE-4E8E9E20.pf
 7ZA.EXE-FA857BD3.pf                          MSEDGE.EXE-37D25F9A.pf                    SVCHOST.EXE-508F55FA.pf
 7ZG.EXE-F49B3D46.pf                          MSEDGE.EXE-37D25F9B.pf                    SVCHOST.EXE-5D15888E.pf
 APPLICATIONFRAMEHOST.EXE-8CE9A1EE.pf         MSEDGE.EXE-37D25F9C.pf                    SVCHOST.EXE-67EC2DA7.pf
 ATTRIB.EXE-8E9FC84B.pf                       MSEDGE.EXE-37D25F9D.pf                    SVCHOST.EXE-6A249820.pf
 AUDIODG.EXE-AB22E9A6.pf                      MSEDGE.EXE-37D25F9E.pf                    SVCHOST.EXE-6E1A6101.pf
 AUTORUN.EXE-46F6E815.pf                      MSEDGE.EXE-37D25FA2.pf                    SVCHOST.EXE-7C364D53.pf
 BACKGROUNDTASKHOST.EXE-332B0729.pf           MSIEXEC.EXE-8FFB1633.pf                   SVCHOST.EXE-8E6D2394.pf
 BACKGROUNDTASKHOST.EXE-B3B8A3A8.pf           MSIEXEC.EXE-CDBFC0F7.pf                   SVCHOST.EXE-93307742.pf
 BACKGROUNDTRANSFERHOST.EXE-4A3D3F52.pf       NGEN.EXE-4A8DA13E.pf                      SVCHOST.EXE-A87523EE.pf
 CERTUTIL.EXE-28F1E0C1.pf                     NGEN.EXE-734C6620.pf                      SVCHOST.EXE-BF3D5CA5.pf
 CHOICE.EXE-42DD1650.pf                       NGENTASK.EXE-0E6CEC17.pf                  SVCHOST.EXE-D1834105.pf
 CLIPUP.EXE-4C5C7B66.pf                       NGENTASK.EXE-849BFD75.pf                  SVCHOST.EXE-DAF72364.pf
 CMD.EXE-0BD30981.pf                          NHCOLOR.EXE-D29DDD9E.pf                   SVCHOST.EXE-DF144105.pf
 CMD.EXE-6D6290C5.pf                          NSUDOLG.EXE-A3333FF9.pf                   SVCHOST.EXE-FDC3FC8E.pf
 COMPATTELRUNNER.EXE-B7A68ECC.pf              PHOTOSAPP.EXE-77E28E93.pf                 SYSTEMSETTINGS.EXE-BE0858C5.pf
 COMREG.EXE-B18E07FD.pf                       POQEXEC.EXE-567EE1A6.pf                   TASKHOSTW.EXE-2E5D4B75.pf
 CONHOST.EXE-0C6456FB.pf                      POWERSHELL.EXE-CA1AE517.pf                TASKKILL.EXE-BE180FC8.pf
 DASHOST.EXE-4B84F273.pf                      REG.EXE-A93A1343.pf                       TASKLIST.EXE-4641012C.pf
 DEFRAG.EXE-3D9E8D72.pf                       RUNDLL32.EXE-164E24E7.pf                  TASKLIST.EXE-F58BCF08.pf
 DEVICECENSUS.EXE-9742347A.pf                 RUNDLL32.EXE-464836ED.pf                  TEXTINPUTHOST.EXE-692EC7E8.pf
 DLLHOST.EXE-15CDDA9C.pf                      RUNDLL32.EXE-52A71BD0.pf                  TIMEOUT.EXE-7D53A680.pf
 DLLHOST.EXE-3D723117.pf                      RUNDLL32.EXE-BF72C764.pf                  TIWORKER.EXE-5595B557.pf
 DLLHOST.EXE-4427C062.pf                      RUNDLL32.EXE-FDCBB5A1.pf                  TOOLBOX.UPDATER.X64.EXE-1A2E871E.pf
 DLLHOST.EXE-4B6CB38A.pf                      RUNTIMEBROKER.EXE-1540E99E.pf             TRUSTEDINSTALLER.EXE-766EFF52.pf
 DLLHOST.EXE-A010D183.pf                      RUNTIMEBROKER.EXE-285799BB.pf             UPFC.EXE-89D4FAEB.pf
 DLLHOST.EXE-C60C3853.pf                      RUNTIMEBROKER.EXE-4551A062.pf             USEROOBEBROKER.EXE-65584ADF.pf
 DLLHOST.EXE-E9BDD97B.pf                      RUNTIMEBROKER.EXE-94B34D1F.pf             USOCLIENT.EXE-4ADC110B.pf
'DOWNLOAD MASTERCAM X9 FULL CR-C7EFFD46.pf'   RUNTIMEBROKER.EXE-98D996D0.pf             VC_REDIST.X64.EXE-1196B2A9.pf
 DRVINST.EXE-39D9EAC7.pf                      RUNTIMEBROKER.EXE-9C74C114.pf             VCREDIST_X64.EXE-4242C1ED.pf
 DSMUSERTASK.EXE-853A6893.pf                  RUNTIMEBROKER.EXE-ADD5E1C9.pf             VC_REDIST.X64.EXE-751F67F2.pf
 ELEVATION_SERVICE.EXE-C2AE4889.pf            RUNTIMEBROKER.EXE-B011FC3A.pf             VCREDIST_X64.EXE-85D50F23.pf
 ELEVATION_SERVICE.EXE-C6B45366.pf            RUNTIMEBROKER.EXE-BD73E83F.pf             VCREDIST_X64.EXE-B0948C06.pf
 EXTRAC32.EXE-4FD3FA35.pf                     SDIAGNHOST.EXE-B3171AA1.pf                VCREDIST_X86.EXE-11EBACBC.pf
 FCLIP.EXE-D93B257B.pf                        SEARCHAPP.EXE-03FE5603.pf                 VCREDIST_X86.EXE-33D31971.pf
 FIND.EXE-AE190082.pf                         SEARCHFILTERHOST.EXE-44162447.pf          VCREDIST_X86.EXE-555EDEE6.pf
 FINDSTR.EXE-1BC2295F.pf                      SEARCHINDEXER.EXE-1CF42BC6.pf             VC_REDIST.X86.EXE-71FE88B0.pf
 FINDSTR.EXE-5986D423.pf                      SEARCHPROTOCOLHOST.EXE-69C456C3.pf        VC_REDIST.X86.EXE-889ABE8F.pf
 FODHELPER.EXE-7F1ED892.pf                    SETUP64.EXE-6C6157AB.pf                   VERCLSID.EXE-AB0FD091.pf
 FORFILES.EXE-1BD2A15F.pf                     SETUP.EXE-20FBC490.pf                     VGAUTHSERVICE.EXE-779D9D39.pf
 IDENTITY_HELPER.EXE-24F367DC.pf              SETUP.EXE-20FBC494.pf                     VM3DSERVICE.EXE-F9D7A5D4.pf
 IDENTITY_HELPER.EXE-5D511889.pf              SETUP.EXE-61F01051.pf                     VMTOOLSD.EXE-90328040.pf
 IPCONFIG.EXE-BFEC2AD0.pf                     SETUP.EXE-94DD5C6C.pf                     VMWARERESOLUTIONSET.EXE-38A925F2.pf
 LOGONUI.EXE-F639BD7E.pf                      SETUP.EXE-94DD5C70.pf                     VSSVC.EXE-6C8F0C66.pf
 MICROSOFTEDGESETUP.EXE-DB91D547.pf           SETUP.EXE-B7C25FBF.pf                     WAASMEDICAGENT.EXE-F5A0D296.pf
 MICROSOFTEDGEUPDATECOMREGISTE-FBD0CE54.pf    SETUP.EXE-C58FE435.pf                     WERMGR.EXE-BE3A79B5.pf
 MICROSOFTEDGEUPDATE.EXE-65B3E8E4.pf          SETUP.EXE-C58FE439.pf                     WGET.EXE-D873B866.pf
 MICROSOFTEDGEUPDATE.EXE-7A595326.pf          SETUP.EXE-FDED94E2.pf                     WHERE.EXE-8DCB25CC.pf
 MICROSOFTEDGEUPDATE.EXE-B00483E4.pf          SETUP.EXE-FDED94E6.pf                     WINSAT.EXE-C345C80B.pf
 MICROSOFTEDGEUPDATESETUP_X86_-878558A0.pf    SGRMBROKER.EXE-32481FEB.pf                WLRMDR.EXE-A7C36FDD.pf
 MICROSOFTEDGE_X64_131.0.2903.-C51766DA.pf    SHELLEXPERIENCEHOST.EXE-AA63A567.pf       WMIADAP.EXE-BB21CD77.pf
 MICROSOFTEDGE_X64_132.0.2957.-4349C6E9.pf    SHUTDOWN.EXE-1692B741.pf                  WMIAPSRV.EXE-FC8436DD.pf
 MICROSOFTEDGE_X64_137.0.3296.-DA18E2E8.pf    SIHCLIENT.EXE-98C47F6C.pf                 WMIC.EXE-98223A30.pf
 MICROSOFTEDGE_X64_137.0.3296.-FC4E20BC.pf    SLUI.EXE-3E441AEE.pf                      WMIPRVSE.EXE-E8B8DD29.pf
 MICROSOFT_PHOTOS_INSTALLER.EX-5CD3389E.pf    SPPEXTCOMOBJ.EXE-7D45A1AB.pf              WOWREG32.EXE-CC9C92C1.pf
 MOBSYNC.EXE-B307E1CC.pf                      SPPSVC.EXE-96070FE0.pf                    WSCRIPT.EXE-3FF4D889.pf
 MODE.COM-A72A4197.pf                         STARTMENUEXPERIENCEHOST.EXE-21AC1B45.pf   WUAUCLT.EXE-5D573F0E.pf
 MOSCOW.COM-34B22CCB.pf                       SVCHOST.EXE-38C6A0A6.pf                   WUSA.EXE-BC40B6DD.pf
 MOUSOCOREWORKER.EXE-4429AC2B.pf              SVCHOST.EXE-4135F405.pf
 MSCORSVW.EXE-16B291C4.pf
```

**What this gives you**

Key finding: `DOWNLOAD MASTERCAM X9 FULL CR-C7EFFD46.pf` is the installer named in the scenario. The filename is truncated at 29 characters — the real executable name continues past `CR`, most likely `CRACK` or `CRACKED`, and the full name must be recovered from inside the `.pf` file itself or from the `$MFT`.

Separate the remaining 177 entries into three buckets:

| Bucket | Representative entries | Analysis | Simple Explanation |
| --- | --- | --- | --- |
| Operating-system noise | `SVCHOST.EXE` (×15), `RUNTIMEBROKER.EXE` (×9), `DLLHOST.EXE` (×7), `TIWORKER.EXE`, `WAASMEDICAGENT.EXE`, `SEARCHINDEXER.EXE` | Expected on any live Windows host; ignore | Normal background Windows machinery |
| Benign installation activity | `MSEDGE.EXE`, `MICROSOFTEDGEUPDATE.EXE`, `VC_REDIST.*`, `VCREDIST_*`, `SETUP.EXE` (×9), `NGEN.EXE` | Browser updates and Visual C++ runtime installs, consistent with routine software setup | Ordinary program installs and updates |
| Living-off-the-land binaries | `EXTRAC32.EXE`, `CERTUTIL.EXE`, `ATTRIB.EXE`, `CHOICE.EXE`, `FINDSTR.EXE` (×2), `FIND.EXE`, `TASKLIST.EXE` (×2), `TASKKILL.EXE`, `FORFILES.EXE`, `TIMEOUT.EXE`, `WHERE.EXE`, `MODE.COM`, `REG.EXE`, `WMIC.EXE`, `WSCRIPT.EXE`, `FODHELPER.EXE`, `CMD.EXE` (×2), `POWERSHELL.EXE` | Signed Microsoft utilities abusable for extraction, enumeration, evasion and persistence — the signature of a batch-driven infection chain | Built-in Windows tools that malware borrows so it never has to bring its own |

Flag these non-standard executables for follow-up; none ships with Windows:

| Entry | Why it stands out |
| --- | --- |
| `MOSCOW.COM-34B22CCB.pf` | A `.com` extension on a modern Windows host is anomalous; the name matches no legitimate product |
| `FCLIP.EXE-D93B257B.pf` | Unrecognised binary |
| `NHCOLOR.EXE-D29DDD9E.pf` | Unrecognised binary |
| `AUTORUN.EXE-46F6E815.pf` | Generic autorun stub, common in installer bundles |
| `NSUDOLG.EXE-A3333FF9.pf` | NSudo variant — a privilege-elevation utility with no legitimate place on a user workstation |
| `COMREG.EXE-B18E07FD.pf` | COM registration helper, frequently bundled with cracks |
| `TOOLBOX.UPDATER.X64.EXE-1A2E871E.pf` | Vendor-agnostic "updater" naming, a common masquerade |
| `7Z2407-X64.EXE`, `7ZA.EXE`, `7ZG.EXE` | 7-Zip, plausibly dropped by the installer to unpack staged components |
| `WGET.EXE-D873B866.pf` | Not a Windows binary; indicates a file-download capability was staged locally |

Note the presence of `FODHELPER.EXE`, which is the canonical Windows UAC-bypass target. Its execution alongside `NSUDOLG.EXE` suggests deliberate elevation activity even though the account is already the built-in Administrator.

**Next**

Parse the installer's `.pf` file to recover its full executable name, run count and execution timestamps.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
<br>
</div>

### 1.2 Parse the installer's Prefetch file for its full name and run times
**Say**

> We have a name from the listing, but it's cut off. Prefetch truncates the executable name at 29
> characters before it appends the hash, so we're missing the end of it. To get the rest we have
> to open the file itself.
>
> One tooling note, and I'm mentioning it because it catches people: the standard tool for this
> is Eric Zimmerman's PECmd, and PECmd is a Windows binary. We're on Linux. On top of that, modern Windows compresses prefetch files, so a parser that doesn't know about that just sees compressed bytes and gives up quietly. `libscca` handles the decompression natively and it's in the Kali repos, so we stay off Wine and off .NET completely.
>
> Four things we want out of this file. The full untruncated name. The path it ran from. The run
> count. And the retained execution times.
>
> Pay attention to that run count. If this thing executed more than once, there's a repeat in our
> timeline, and the question asks specifically for the *first* execution. Getting that wrong is
> the single easiest way to fail this task.


**Why this step**

The directory listing in 1.1 truncated the installer's name at 29 characters and revealed nothing about when it ran. Parsing the `.pf` file itself recovers the untruncated filename, the full execution path, the run count, and the retained execution timestamps — everything Task 1 requires.

**Command**

```bash
sudo apt install -y libscca-utils
sccainfo "evidence/C/Windows/prefetch/DOWNLOAD MASTERCAM X9 FULL CR-C7EFFD46.pf"
```

**Breakdown**

| Component | Meaning | Simple Explanation |
| --- | --- | --- |
| `apt install -y libscca-utils` | Install the libscca command-line tools | Adds a native Linux parser for Windows Prefetch; `-y` accepts prompts automatically |
| `sccainfo` | libscca's prefetch inspector | Prints every field of a `.pf` file in readable form |
| `"…CR-C7EFFD46.pf"` | Target file, quoted | Quoting is mandatory — the filename contains spaces |

**Theory — why libscca instead of PECmd**

The standard tool for this job is Eric Zimmerman's `PECmd.exe`, a Windows binary. Windows 10 and 11 compress prefetch files with the MAM (Xpress Huffman) algorithm, so a naive parser sees only compressed bytes and fails. `libscca` implements that decompression natively and ships in the Kali repositories, which keeps the entire analysis on Linux with no Wine layer and no .NET runtime. It reads format versions 17 through 30, covering Windows XP through Windows 11.

**Theory — what Prefetch actually records, and its limits**

When a program launches, the Windows Cache Manager monitors the first ten seconds of execution and records every file and directory the process touched, so subsequent launches can pre-load them. The resulting `.pf` file contains:

| Field | Meaning | Forensic value |
| --- | --- | --- |
| Executable filename | The binary's name, untruncated | Recovers the full name the directory listing cut off |
| Run count | Total number of executions since the `.pf` was created | Tells you whether the retained timestamps cover the program's whole history |
| Last run times 1–8 | The eight most recent execution start times, newest first | Direct execution timeline |
| Filenames list | Up to ~1000 files referenced during the first ten seconds | Reveals DLLs, dropped files, temp artifacts and child processes |
| Volume information | Device path, serial number, creation time | Ties the activity to a specific volume |

The critical limitation: only **eight** timestamps are retained. When the run count exceeds eight, the earliest listed time is not the first execution — it is merely the eighth-most-recent. In that situation first-execution evidence must come from elsewhere, typically the `.pf` file's own creation timestamp in the `$MFT`, or from Amcache.

Note also that these times are stored in UTC, and that entry `Last run time: 1` is the most recent execution, not the oldest.

**Result**

```
sccainfo 20250915

Windows Prefetch File (PF) information:
        Format version                  : 30
        Prefetch hash                   : 0xc7effd46
        Executable filename             : DOWNLOAD MASTERCAM X9 FULL CR
        Run count                       : 2
        Last run time: 1                : Jun 21, 2025 18:35:47.481158100 UTC
        Last run time: 2                : Jun 21, 2025 18:34:19.262602400 UTC
        Last run time: 3                : Not set (0)
        Last run time: 4                : Not set (0)
        Last run time: 5                : Not set (0)
        Last run time: 6                : Not set (0)
        Last run time: 7                : Not set (0)
        Last run time: 8                : Not set (0)

Filenames:
        Number of filenames             : 108
```

```
Volumes:
        Number of volumes               : 1

Volume: 1 information:
        Device path                     : \VOLUME{01db6e3ba9900280-9ea9af27}
        Creation time                   : Jan 24, 2025 08:40:46.447475200 UTC
        Serial number                   : 0x9ea9af27
```

The loaded-file list contains 108 entries, the majority of which are standard `SysWOW64` runtime DLLs with no investigative value. The significant entries are reproduced below; the remainder are omitted as system noise, not because they were absent.

```
Filename: 11   : \VOLUME{01db6e3ba9900280-9ea9af27}\USERS\ADMINISTRATOR\DOWNLOADS\DOWNLOAD MASTERCAM X9 FULL CRACK PC.EXE
Filename: 69   : \VOLUME{01db6e3ba9900280-9ea9af27}\USERS\ADMINISTRATOR\APPDATA\LOCAL\TEMP\MYSQL.WP5
Filename: 70   : \VOLUME{01db6e3ba9900280-9ea9af27}\USERS\ADMINISTRATOR\APPDATA\LOCAL\TEMP\AUTHORIZATION.WP5
Filename: 71   : \VOLUME{01db6e3ba9900280-9ea9af27}\USERS\ADMINISTRATOR\APPDATA\LOCAL\TEMP\LOCK.WP5
Filename: 72   : \VOLUME{01db6e3ba9900280-9ea9af27}\USERS\ADMINISTRATOR\APPDATA\LOCAL\TEMP\ART.WP5
Filename: 73   : \VOLUME{01db6e3ba9900280-9ea9af27}\USERS\ADMINISTRATOR\APPDATA\LOCAL\TEMP\ROMANIA.WP5
Filename: 74   : \VOLUME{01db6e3ba9900280-9ea9af27}\USERS\ADMINISTRATOR\APPDATA\LOCAL\TEMP\PLAY.WP5
Filename: 75   : \VOLUME{01db6e3ba9900280-9ea9af27}\USERS\ADMINISTRATOR\APPDATA\LOCAL\TEMP\REFUGEES.WP5
Filename: 76   : \VOLUME{01db6e3ba9900280-9ea9af27}\USERS\ADMINISTRATOR\APPDATA\LOCAL\TEMP\RUNNER.WP5
Filename: 77   : \VOLUME{01db6e3ba9900280-9ea9af27}\USERS\ADMINISTRATOR\APPDATA\LOCAL\TEMP\GBA.WP5
Filename: 93   : \VOLUME{01db6e3ba9900280-9ea9af27}\WINDOWS\SYSWOW64\CMD.EXE
Filename: 94   : \VOLUME{01db6e3ba9900280-9ea9af27}\WINDOWS\SYSTEM32\EN-US\CMD.EXE.MUI
Filename: 35   : \VOLUME{01db6e3ba9900280-9ea9af27}\$MFT
```

**What this gives you**

Key finding: the installer's full name and path is `C:\Users\Administrator\Downloads\DOWNLOAD MASTERCAM X9 FULL CRACK PC.EXE`, and it executed **twice** — at **2025-06-21 18:34:19.262 UTC** and again at **2025-06-21 18:35:47.481 UTC**.

Because the run count is 2 and Prefetch retains up to 8 timestamps, both executions are fully represented. The earlier of the two is therefore the genuine first execution, with no risk of the eight-slot rollover described above. Record `2025-06-21 18:34:19 UTC` as the first-execution time; the two runs are 88 seconds apart, consistent with an installer that ran, exited, and was immediately re-launched.

Extract three further facts for later use:

| Observation | Interpretation | Simple Explanation |
| --- | --- | --- |
| Entry 93 loads `SysWOW64\CMD.EXE` | The 32-bit installer spawned a command interpreter within its first ten seconds | The program opened a Command Prompt to run script commands for it |
| Entries 69–77 write nine `.WP5` files to `%LOCALAPPDATA%\Temp` | Payload components staged under an innocuous, unrelated extension — `MYSQL`, `AUTHORIZATION`, `LOCK`, `ART`, `ROMANIA`, `PLAY`, `REFUGEES`, `RUNNER`, `GBA` | The installer scattered nine oddly-named pieces into the temp folder |
| Binary runs from `SysWOW64`, referencing `WOW64.DLL` and `WOW64CPU.DLL` | The installer is a 32-bit executable on a 64-bit host | Built as 32-bit, so Windows ran it through its compatibility layer |

The volume identity is `\VOLUME{01db6e3ba9900280-9ea9af27}`, serial `0x9ea9af27`, created 2025-01-24 — use it to correlate paths across `$MFT`, `$J` and other prefetch files.

**Next**

Establish when the installer process ended, which Prefetch cannot answer — it records start times only.
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

==Answer== `2025-06-21 18:36:52`
<div align="center">
<br>
<br>
</div>

### 2.1 Inventory the event logs and test for Sysmon
**Say**

> The question is when the installer process *ended*. The instinct — and it's the right instinct —
> is to go to the event logs, because process termination is exactly the sort of thing Windows is
> supposed to write down.
>
> So we're going to go and look. And this step
> is a dead end. But it's a *documented* dead end, and that distinction matters. In a real
> engagement, proving an artifact isn't there is a finding. It's what justifies everything you do
> afterwards, and it's what goes in the report when someone asks why you reconstructed a timeline
> by hand instead of reading it off a log.
>
> Here's the trick I want you to take away, though. We are not going to open a single log file.
> You can triage an entire EVTX directory on two columns alone — size and modification date. A
> freshly initialised event log is exactly 69,632 bytes, one chunk plus a header. Anything still
> sitting at that number is empty, whatever its name promises. And anything last written months
> before the incident was written at build time and is irrelevant.
>
> Two columns. No parsing. Watch which logs survive that filter, and specifically watch whether
> Sysmon appears at all.


**Why this step**

Prefetch records execution start times only, so Task 2's termination question needs a log source that records process exit. Before choosing one, enumerate what was collected — the presence or absence of Sysmon determines whether high-fidelity process exists or whether the investigation must fall back on native Windows auditing.

**Command**

```bash
ls -la evidence/C/Windows/System32/winevt/logs/
```

**Breakdown**

| Component | Meaning | Simple Explanation |
| --- | --- | --- |
| `ls -la` | Long listing, all entries | Shows size, owner and modification time alongside each name — size and mtime are the triage signal here |
| `evidence/C/Windows/System32/winevt/logs/` | Windows event-log directory | The canonical location of every `.evtx` file on a Windows host |

**Theory — reading an EVTX directory without opening a single log**

Two columns do most of the work before any parsing begins.

**Size.** A freshly initialised EVTX file is **69,632 bytes** — one 64 KiB chunk plus the file header. Any log still sitting at exactly that size is effectively empty. Anything larger holds records, and the larger it is, the more it holds.

**Modification time.** The collection was taken 2025-06-21. Logs whose mtime is `Jan 23 2025` were last written at system build time and are irrelevant; logs stamped `Jun 21 2025` were written on the incident day and form the candidate set.

Filenames use `%4` as an escaped `/`, so `Microsoft-Windows-PowerShell%4Operational.evtx` is the channel `Microsoft-Windows-PowerShell/Operational`.

**Result**

```
total 36976
-rw-rw-r-- 1 nedmoeca nedmoeca 1118208 Jun 21  2025  Application.evtx
-rw-rw-r-- 1 nedmoeca nedmoeca   69632 Jan 23  2025  Microsoft-Client-License-Flexible-Platform%4Admin.evtx
-rw-rw-r-- 1 nedmoeca nedmoeca   69632 Jun 21  2025  Microsoft-Client-Licensing-Platform%4Admin.evtx
-rw-rw-r-- 1 nedmoeca nedmoeca   69632 Jan 23  2025  Microsoft-Windows-AAD%4Operational.evtx
-rw-rw-r-- 1 nedmoeca nedmoeca   69632 Jan 23  2025  Microsoft-Windows-Application-Experience%4Program-Compatibility-Troubleshooter.evtx
-rw-rw-r-- 1 nedmoeca nedmoeca   69632 Jan 23  2025  Microsoft-Windows-Application-Experience%4Program-Telemetry.evtx
-rw-rw-r-- 1 nedmoeca nedmoeca 1052672 Jun 21  2025  Microsoft-Windows-AppModel-Runtime%4Admin.evtx
-rw-rw-r-- 1 nedmoeca nedmoeca 1118208 Jun 21  2025  Microsoft-Windows-AppReadiness%4Admin.evtx
-rw-rw-r-- 1 nedmoeca nedmoeca   69632 Jun 21  2025  Microsoft-Windows-AppReadiness%4Operational.evtx
-rw-rw-r-- 1 nedmoeca nedmoeca 1052672 Jun 21  2025  Microsoft-Windows-AppXDeployment%4Operational.evtx
-rw-rw-r-- 1 nedmoeca nedmoeca 5246976 Jun 21  2025  Microsoft-Windows-AppXDeploymentServer%4Operational.evtx
-rw-rw-r-- 1 nedmoeca nedmoeca 1052672 Jun 21  2025  Microsoft-Windows-AppxPackaging%4Operational.evtx
-rw-rw-r-- 1 nedmoeca nedmoeca   69632 Jan 23  2025  Microsoft-Windows-Audio%4Operational.evtx
-rw-rw-r-- 1 nedmoeca nedmoeca   69632 Jan 23  2025  Microsoft-Windows-Audio%4PlaybackManager.evtx
-rw-rw-r-- 1 nedmoeca nedmoeca   69632 Jun 21  2025  Microsoft-Windows-Biometrics%4Operational.evtx
-rw-rw-r-- 1 nedmoeca nedmoeca   69632 Jun 21  2025 'Microsoft-Windows-BitLocker%4BitLocker Management.evtx'
-rw-rw-r-- 1 nedmoeca nedmoeca 1052672 Jun 21  2025  Microsoft-Windows-Bits-Client%4Operational.evtx
-rw-rw-r-- 1 nedmoeca nedmoeca   69632 Jan 23  2025  Microsoft-Windows-CloudStore%4Initialization.evtx
-rw-rw-r-- 1 nedmoeca nedmoeca   69632 Jun 21  2025  Microsoft-Windows-CloudStore%4Operational.evtx
-rw-rw-r-- 1 nedmoeca nedmoeca   69632 Jan 23  2025  Microsoft-Windows-CodeIntegrity%4Operational.evtx
-rw-rw-r-- 1 nedmoeca nedmoeca   69632 Jan 23  2025  Microsoft-Windows-Containers-BindFlt%4Operational.evtx
-rw-rw-r-- 1 nedmoeca nedmoeca   69632 Jan 23  2025  Microsoft-Windows-Containers-Wcifs%4Operational.evtx
-rw-rw-r-- 1 nedmoeca nedmoeca   69632 Jun 21  2025  Microsoft-Windows-Crypto-DPAPI%4Operational.evtx
-rw-rw-r-- 1 nedmoeca nedmoeca   69632 Jun 21  2025  Microsoft-Windows-Crypto-NCrypt%4Operational.evtx
-rw-rw-r-- 1 nedmoeca nedmoeca   69632 Jan 23  2025  Microsoft-Windows-DeviceManagement-Enterprise-Diagnostics-Provider%4Admin.evtx
-rw-rw-r-- 1 nedmoeca nedmoeca   69632 Jun 21  2025  Microsoft-Windows-DeviceManagement-Enterprise-Diagnostics-Provider%4Operational.evtx
-rw-rw-r-- 1 nedmoeca nedmoeca 1052672 Jun 21  2025  Microsoft-Windows-DeviceSetupManager%4Admin.evtx
-rw-rw-r-- 1 nedmoeca nedmoeca   69632 Jan 23  2025  Microsoft-Windows-DeviceSetupManager%4Operational.evtx
-rw-rw-r-- 1 nedmoeca nedmoeca   69632 Jun 21  2025  Microsoft-Windows-Dhcp-Client%4Admin.evtx
-rw-rw-r-- 1 nedmoeca nedmoeca   69632 Jun 21  2025  Microsoft-Windows-Diagnosis-DPS%4Operational.evtx
-rw-rw-r-- 1 nedmoeca nedmoeca   69632 Jun 21  2025  Microsoft-Windows-Diagnosis-Scheduled%4Operational.evtx
-rw-rw-r-- 1 nedmoeca nedmoeca   69632 Jun 21  2025  Microsoft-Windows-Diagnosis-Scripted%4Admin.evtx
-rw-rw-r-- 1 nedmoeca nedmoeca   69632 Jun 21  2025  Microsoft-Windows-Diagnosis-Scripted%4Operational.evtx
-rw-rw-r-- 1 nedmoeca nedmoeca   69632 Jan 23  2025  Microsoft-Windows-Diagnostics-Performance%4Operational.evtx
-rw-rw-r-- 1 nedmoeca nedmoeca   69632 Jun 21  2025  Microsoft-Windows-DiskDiagnosticDataCollector%4Operational.evtx
-rw-rw-r-- 1 nedmoeca nedmoeca 1118208 Jun 21  2025  Microsoft-Windows-GroupPolicy%4Operational.evtx
-rw-rw-r-- 1 nedmoeca nedmoeca   69632 Jan 23  2025  Microsoft-Windows-HelloForBusiness%4Operational.evtx
-rw-rw-r-- 1 nedmoeca nedmoeca   69632 Jan 23  2025  Microsoft-Windows-Kernel-Boot%4Operational.evtx
-rw-rw-r-- 1 nedmoeca nedmoeca   69632 Jan 23  2025  Microsoft-Windows-Kernel-EventTracing%4Admin.evtx
-rw-rw-r-- 1 nedmoeca nedmoeca   69632 Jan 23  2025  Microsoft-Windows-Kernel-IO%4Operational.evtx
-rw-rw-r-- 1 nedmoeca nedmoeca 1052672 Jan 23  2025  Microsoft-Windows-Kernel-PnP%4Configuration.evtx
-rw-rw-r-- 1 nedmoeca nedmoeca   69632 Jan 23  2025  Microsoft-Windows-Kernel-ShimEngine%4Operational.evtx
-rw-rw-r-- 1 nedmoeca nedmoeca   69632 Jan 23  2025  Microsoft-Windows-Kernel-WHEA%4Operational.evtx
-rw-rw-r-- 1 nedmoeca nedmoeca   69632 Jun 21  2025 'Microsoft-Windows-Known Folders API Service.evtx'
-rw-rw-r-- 1 nedmoeca nedmoeca   69632 Jun 21  2025  Microsoft-Windows-LanguagePackSetup%4Operational.evtx
-rw-rw-r-- 1 nedmoeca nedmoeca 1052672 Jun 21  2025  Microsoft-Windows-LiveId%4Operational.evtx
-rw-rw-r-- 1 nedmoeca nedmoeca   69632 Jan 23  2025  Microsoft-Windows-MUI%4Operational.evtx
-rw-rw-r-- 1 nedmoeca nedmoeca   69632 Jan 23  2025  Microsoft-Windows-NcdAutoSetup%4Operational.evtx
-rw-rw-r-- 1 nedmoeca nedmoeca   69632 Jun 21  2025  Microsoft-Windows-NCSI%4Operational.evtx
-rw-rw-r-- 1 nedmoeca nedmoeca   69632 Jun 21  2025  Microsoft-Windows-NetworkProfile%4Operational.evtx
-rw-rw-r-- 1 nedmoeca nedmoeca   69632 Jun 21  2025  Microsoft-Windows-Ntfs%4Operational.evtx
-rw-rw-r-- 1 nedmoeca nedmoeca   69632 Jan 23  2025  Microsoft-Windows-Ntfs%4WHC.evtx
-rw-rw-r-- 1 nedmoeca nedmoeca   69632 Jan 23  2025  Microsoft-Windows-Partition%4Diagnostic.evtx
-rw-rw-r-- 1 nedmoeca nedmoeca   69632 Jun 21  2025  Microsoft-Windows-PowerShell%4Operational.evtx
-rw-rw-r-- 1 nedmoeca nedmoeca   69632 Jan 23  2025  Microsoft-Windows-PrintService%4Admin.evtx
-rw-rw-r-- 1 nedmoeca nedmoeca 1118208 Jun 21  2025  Microsoft-Windows-Privacy-Auditing%4Operational.evtx
-rw-rw-r-- 1 nedmoeca nedmoeca   69632 Jun 21  2025  Microsoft-Windows-Provisioning-Diagnostics-Provider%4Admin.evtx
-rw-rw-r-- 1 nedmoeca nedmoeca 1052672 Jun 21  2025  Microsoft-Windows-PushNotification-Platform%4Operational.evtx
-rw-rw-r-- 1 nedmoeca nedmoeca   69632 Jan 23  2025  Microsoft-Windows-ReadyBoost%4Operational.evtx
-rw-rw-r-- 1 nedmoeca nedmoeca   69632 Jun 21  2025  Microsoft-Windows-Resource-Exhaustion-Detector%4Operational.evtx
-rw-rw-r-- 1 nedmoeca nedmoeca   69632 Jun 21  2025  Microsoft-Windows-Resource-Exhaustion-Resolver%4Operational.evtx
-rw-rw-r-- 1 nedmoeca nedmoeca   69632 Jun 21  2025  Microsoft-Windows-Security-LessPrivilegedAppContainer%4Operational.evtx
-rw-rw-r-- 1 nedmoeca nedmoeca   69632 Jun 21  2025  Microsoft-Windows-Security-Mitigations%4KernelMode.evtx
-rw-rw-r-- 1 nedmoeca nedmoeca   69632 Jun 21  2025  Microsoft-Windows-Security-SPP-UX-Notifications%4ActionCenter.evtx
-rw-rw-r-- 1 nedmoeca nedmoeca   69632 Jun 21  2025  Microsoft-Windows-SettingSync%4Debug.evtx
-rw-rw-r-- 1 nedmoeca nedmoeca   69632 Jan 23  2025  Microsoft-Windows-SettingSync%4Operational.evtx
-rw-rw-r-- 1 nedmoeca nedmoeca   69632 Jun 21  2025  Microsoft-Windows-ShellCommon-StartLayoutPopulation%4Operational.evtx
-rw-rw-r-- 1 nedmoeca nedmoeca 1052672 Jun 21  2025  Microsoft-Windows-Shell-Core%4AppDefaults.evtx
-rw-rw-r-- 1 nedmoeca nedmoeca 1052672 Jun 21  2025  Microsoft-Windows-Shell-Core%4Operational.evtx
-rw-rw-r-- 1 nedmoeca nedmoeca   69632 Jun 21  2025  Microsoft-Windows-SmbClient%4Connectivity.evtx
-rw-rw-r-- 1 nedmoeca nedmoeca   69632 Jan 23  2025  Microsoft-Windows-SmbClient%4Security.evtx
-rw-rw-r-- 1 nedmoeca nedmoeca   69632 Jun 21  2025  Microsoft-Windows-SMBServer%4Operational.evtx
-rw-rw-r-- 1 nedmoeca nedmoeca 1118208 Jun 21  2025  Microsoft-Windows-StateRepository%4Operational.evtx
-rw-rw-r-- 1 nedmoeca nedmoeca   69632 Jan 23  2025  Microsoft-Windows-StorageSpaces-Driver%4Operational.evtx
-rw-rw-r-- 1 nedmoeca nedmoeca 1118208 Jun 21  2025  Microsoft-Windows-Storage-Storport%4Health.evtx
-rw-rw-r-- 1 nedmoeca nedmoeca 1118208 Jun 21  2025  Microsoft-Windows-Storage-Storport%4Operational.evtx
-rw-rw-r-- 1 nedmoeca nedmoeca 3215360 Jun 21  2025  Microsoft-Windows-Store%4Operational.evtx
-rw-rw-r-- 1 nedmoeca nedmoeca   69632 Jan 23  2025  Microsoft-Windows-Storsvc%4Diagnostic.evtx
-rw-rw-r-- 1 nedmoeca nedmoeca   69632 Jun 21  2025  Microsoft-Windows-TaskScheduler%4Maintenance.evtx
-rw-rw-r-- 1 nedmoeca nedmoeca   69632 Jan 23  2025  Microsoft-Windows-TerminalServices-LocalSessionManager%4Operational.evtx
-rw-rw-r-- 1 nedmoeca nedmoeca   69632 Jun 21  2025  Microsoft-Windows-Time-Service%4Operational.evtx
-rw-rw-r-- 1 nedmoeca nedmoeca   69632 Jan 23  2025  Microsoft-Windows-TWinUI%4Operational.evtx
-rw-rw-r-- 1 nedmoeca nedmoeca   69632 Jun 21  2025  Microsoft-Windows-TZSync%4Operational.evtx
-rw-rw-r-- 1 nedmoeca nedmoeca   69632 Jan 23  2025  Microsoft-Windows-UniversalTelemetryClient%4Operational.evtx
-rw-rw-r-- 1 nedmoeca nedmoeca   69632 Jan 23  2025 'Microsoft-Windows-User Device Registration%4Admin.evtx'
-rw-rw-r-- 1 nedmoeca nedmoeca   69632 Jan 23  2025  Microsoft-Windows-UserPnp%4DeviceInstall.evtx
-rw-rw-r-- 1 nedmoeca nedmoeca   69632 Jan 23  2025 'Microsoft-Windows-User Profile Service%4Operational.evtx'
-rw-rw-r-- 1 nedmoeca nedmoeca   69632 Jan 23  2025  Microsoft-Windows-VolumeSnapshot-Driver%4Operational.evtx
-rw-rw-r-- 1 nedmoeca nedmoeca   69632 Jan 23  2025  Microsoft-Windows-Wcmsvc%4Operational.evtx
-rw-rw-r-- 1 nedmoeca nedmoeca   69632 Jan 23  2025  Microsoft-Windows-WebAuthN%4Operational.evtx
-rw-rw-r-- 1 nedmoeca nedmoeca   69632 Jun 21  2025  Microsoft-Windows-WFP%4Operational.evtx
-rw-rw-r-- 1 nedmoeca nedmoeca   69632 Jun 21  2025 'Microsoft-Windows-Windows Firewall With Advanced Security%4FirewallDiagnostics.evtx'
-rw-rw-r-- 1 nedmoeca nedmoeca 1052672 Jun 21  2025 'Microsoft-Windows-Windows Firewall With Advanced Security%4Firewall.evtx'
-rw-rw-r-- 1 nedmoeca nedmoeca   69632 Jun 21  2025  Microsoft-Windows-WindowsSystemAssessmentTool%4Operational.evtx
-rw-rw-r-- 1 nedmoeca nedmoeca   69632 Jun 21  2025  Microsoft-Windows-WindowsUpdateClient%4Operational.evtx
-rw-rw-r-- 1 nedmoeca nedmoeca   69632 Jan 23  2025  Microsoft-Windows-WinINet-Config%4ProxyConfigChanged.evtx
-rw-rw-r-- 1 nedmoeca nedmoeca   69632 Jan 23  2025  Microsoft-Windows-Winlogon%4Operational.evtx
-rw-rw-r-- 1 nedmoeca nedmoeca   69632 Jun 21  2025  Microsoft-Windows-WinRM%4Operational.evtx
-rw-rw-r-- 1 nedmoeca nedmoeca 1052672 Jun 21  2025  Microsoft-Windows-WMI-Activity%4Operational.evtx
-rw-rw-r-- 1 nedmoeca nedmoeca   69632 Jan 23  2025  Parameters.evtx
-rw-rw-r-- 1 nedmoeca nedmoeca 1118208 Jun 21  2025  Security.evtx
-rw-rw-r-- 1 nedmoeca nedmoeca   69632 Jan 23  2025  Setup.evtx
-rw-rw-r-- 1 nedmoeca nedmoeca 1118208 Jun 21  2025  System.evtx
-rw-rw-r-- 1 nedmoeca nedmoeca 1118208 Jun 21  2025 'Windows PowerShell.evtx'
```

**What this gives you**

Key finding: **Sysmon is not installed.** There is no `Microsoft-Windows-Sysmon%4Operational.evtx` anywhere in the collection. Every technique that depends on Sysmon is therefore unavailable, and each task must be answered from a native Windows source instead:

| Sysmon capability that does not exist here | Event ID | Native fallback |
| --- | --- | --- |
| Process creation with full command line and hashes | 1 | Security 4688, if command-line auditing is enabled |
| Process termination | 5 | Security 4689, if audit process tracking is enabled |
| Image loaded, with SHA-256 | 7 | Amcache (SHA-1 only), or hashing the recovered file directly |
| File created | 11 | `$MFT` and `$J` USN journal |
| DNS query | 22 | DNS client cache, or strings inside the payload |

Note a second absence: there is no `Microsoft-Windows-Windows Defender%4Operational.evtx` either. The host had no endpoint detection telemetry of any kind — which is exactly the condition the malware's AV/EDR checks were written to confirm.

Rank the surviving candidates by size and modification date:

| Log | Size (bytes) | Modified | Analysis | Simple Explanation |
| --- | --- | --- | --- | --- |
| `Security.evtx` | 1,118,208 | Jun 21 2025 | Primary target — holds 4688/4689 process tracking and 4624 logons if auditing is enabled | Windows' own audit trail of who ran what |
| `Microsoft-Windows-Privacy-Auditing%4Operational.evtx` | 1,118,208 | Jun 21 2025 | Records application access to protected resources | Logs which apps reached for sensitive data |
| `Microsoft-Windows-Bits-Client%4Operational.evtx` | 1,052,672 | Jun 21 2025 | Background Intelligent Transfer Service — a common malware download channel | Windows' own file-downloading service |
| `Microsoft-Windows-WMI-Activity%4Operational.evtx` | 1,052,672 | Jun 21 2025 | WMI queries, consistent with the `WMIC.EXE` prefetch entry | Records system-information queries, often used for reconnaissance |
| `Windows PowerShell.evtx` | 1,118,208 | Jun 21 2025 | Engine lifecycle events, consistent with the `POWERSHELL.EXE` prefetch entry | Confirms PowerShell ran, and under which host |
| `Microsoft-Windows-Windows Firewall …%4Firewall.evtx` | 1,052,672 | Jun 21 2025 | Firewall rule additions and profile changes | Shows whether the malware punched a hole in the firewall |
| `Application.evtx`, `System.evtx` | 1,118,208 each | Jun 21 2025 | Service installs, crashes, driver loads | General system and application events |
| `Microsoft-Windows-PowerShell%4Operational.evtx` | 69,632 | Jun 21 2025 | Empty — script-block logging was disabled | The detailed PowerShell log was never turned on |
| `Microsoft-Windows-Ntfs%4Operational.evtx` | 69,632 | Jun 21 2025 | Empty | No NTFS-level event data |
| `Microsoft-Windows-TaskScheduler%4Maintenance.evtx` | 69,632 | Jun 21 2025 | Empty, and the `Operational` channel was not collected | Scheduled-task execution history must come from the task XML on disk instead |

**Next**

Parse `Security.evtx` and profile its Event IDs to confirm whether audit process tracking was enabled, which decides whether 4689 can answer the termination question.

---

### 2.2 Reconstruct the execution timeline from the USN Journal
**Say**

> No Sysmon, no process tracking. So we drop a layer — down to the filesystem itself.
>
> NTFS keeps a change journal called the USN Journal, at `$Extend\$J`. Every time a file is
> created, written, renamed or deleted on this volume, NTFS appends a record: what changed, what
> kind of change it was, and when, to sub-millisecond precision. It exists so that backup and
> indexing software doesn't have to rescan the whole disk. Nobody turned it on. Nobody thought
> about it. It's just *there* — and on a host with no security tooling it becomes the closest
> thing we have to a process monitor.
>
> I'm parsing it by hand rather than reaching for a tool, and there's a reason for that. The
> record format is simple enough to read in about fifteen lines of Python, and once you've seen
> the layout you'll never be dependent on someone else's parser being installed. 
>
> Now, the blind spot, and it's the whole reason this step doesn't finish the task. The USN Journal
> records what happened to *files*. It has nothing to say about processes. It will show us the
> malware staging its payload beautifully, and it will not tell us when the installer died.
>
> Watch for a repeat as the timeline builds. I don't think this ran once.


**Why this step**

Section 2.1 established that no process-exit record exists: Sysmon is absent and `Security.evtx` carries 4688 without 4689. With no direct termination event, the installer's lifetime must be bounded by filesystem side effects instead — and the NTFS USN Journal records every one of them with sub-second precision.

**Command**

```bash
python3 usnparse.py "evidence/C/\$Extend/\$J" | awk '$1=="2025-06-21" && $2>"18:33" && $2<"18:40"'
```

The parser is a minimal `$UsnJrnl:$J` reader (V2 records: 4-byte length, 8-byte timestamp at offset 32, 4-byte reason at offset 40, UTF-16LE filename at the offset given at byte 58):

```python
import struct, datetime
d = open(path, 'rb').read()
i = 0
while i < len(d) - 4:
    ln = struct.unpack_from('<I', d, i)[0]
    if ln == 0:
        i += 8; continue
    if ln < 60 or ln > 1024 or i + ln > len(d):
        i += 8; continue
    major  = struct.unpack_from('<H', d, i + 4)[0]
    ts     = struct.unpack_from('<Q', d, i + 32)[0]
    reason = struct.unpack_from('<I', d, i + 40)[0]
    nlen   = struct.unpack_from('<H', d, i + 56)[0]
    noff   = struct.unpack_from('<H', d, i + 58)[0]
    name   = d[i + noff : i + noff + nlen].decode('utf-16-le', 'replace')
    i += ln
```

**Breakdown**

| Component | Meaning | Simple Explanation |
| --- | --- | --- |
| `$Extend\$J` | The USN Journal data stream | NTFS's own change log for every file on the volume |
| Record length at offset 0 | Variable record size | Each entry states how long it is, so the parser can walk to the next |
| `major` version at offset 4 | Record format version | Version 2 is the standard Windows 10/11 layout |
| Timestamp at offset 32 | FILETIME, 100-ns since 1601-01-01 | Convert by dividing by 10 into microseconds and adding to 1601 |
| Reason flags at offset 40 | Bitmask of what changed | `0x100` = FILE_CREATE, `0x200` = FILE_DELETE, `0x2` = DATA_EXTEND, `0x80000000` = CLOSE |
| Name length / offset (56 / 58) | Where the filename sits inside the record | Names are UTF-16LE and carry no path — only the filename |

**Theory — the USN Journal's strengths and its one blind spot**

The journal records *filename only*, never the full path. A `FILE_CREATE` for `K` tells you a file called `K` was created but not where. Pair it with the `$MFT` (which holds parent-directory references) when location matters. In exchange for that limitation it gives something no event log here does: a complete, ordered, sub-second record of every create, write, truncate, rename and delete on the volume — including files the attacker deleted afterwards.

Prefetch files appear in this journal too, and that makes it a proxy execution timeline. Windows creates a `.pf` roughly ten seconds after a program starts and rewrites it (`DATA_TRUNCATION` + `DATA_EXTEND`) on each subsequent run. Every `FILE_CREATE` of a `.pf` therefore marks a first execution, and every rewrite marks a later one.

**Result**

```
18:33:58.997  download mastercam x9 full crack pc.exe   FILE_CREATE
18:34:08.137  download mastercam x9 full crack pc.exe   DATA_OVERWRITE|DATA_EXTEND|FILE_CREATE|BASIC_INFO|CLOSE
18:34:22.231  nsv52EF.tmp                               FILE_CREATE
18:34:22.231  nsv52EF.tmp                               FILE_DELETE|CLOSE
18:34:25.511  Mysql.wp5                                 FILE_CREATE
18:34:25.527  Authorization.wp5                         FILE_CREATE
18:34:25.558  Art.wp5                                   FILE_CREATE
18:34:25.558  Lock.wp5                                  FILE_CREATE
18:34:25.574  Play.wp5                                  FILE_CREATE
18:34:25.574  Romania.wp5                               FILE_CREATE
18:34:25.621  Refugees.wp5                              FILE_CREATE
18:34:25.699  Runner.wp5                                FILE_CREATE
18:34:25.746  Gba.wp5                                   FILE_CREATE
18:34:29.386  DOWNLOAD MASTERCAM X9 FULL CR-C7EFFD46.pf FILE_CREATE
18:34:31.262  Mysql.wp5.bat                             FILE_CREATE
18:34:40.106  CMD.EXE-6D6290C5.pf                       FILE_CREATE
18:34:46.496  TASKLIST.EXE-4641012C.pf                  FILE_CREATE
18:34:46.496  FINDSTR.EXE-5986D423.pf                   FILE_CREATE
18:34:47.418  448887                                    FILE_CREATE
18:34:48.917  CAB05572.TMP                              FILE_CREATE
18:34:48.917  Theology                                  FILE_CREATE
18:34:48.980  Analyze / Appreciated / Draws / Investors / Mechanisms / Thanksgiving   FILE_CREATE
18:34:48.996  Balls / Hell / Subsequently               FILE_CREATE
18:34:49.012  Dawn                                      FILE_CREATE
18:34:49.168  EXTRAC32.EXE-4FD3FA35.pf                  FILE_CREATE
18:34:49.480  Moscow.com                                FILE_CREATE
18:34:49.668  Moscow.com                                DATA_EXTEND
18:34:50.168  Moscow.com                                DATA_EXTEND|CLOSE
18:34:50.684  K                                         FILE_CREATE
18:34:50.746  K                                         DATA_EXTEND|FILE_CREATE|CLOSE
18:34:52.980  K                                         FILE_DELETE|CLOSE
18:34:57.606  CHOICE.EXE-42DD1650.pf                    FILE_CREATE
18:35:01.121  MOSCOW.COM-34B22CCB.pf                    FILE_CREATE
18:35:47.528  nsmA020.tmp                               FILE_CREATE
18:35:47.528  nsmA020.tmp                               FILE_DELETE|CLOSE
18:35:47.824  Mysql.wp5 … Gba.wp5                       DATA_TRUNCATION|DATA_EXTEND  (all nine rewritten)
18:35:48.293  Mysql.wp5.bat                             DATA_OVERWRITE|DATA_EXTEND|DATA_TRUNCATION|BASIC_INFO|CLOSE
18:35:58.043  DOWNLOAD MASTERCAM X9 FULL CR-C7EFFD46.pf DATA_TRUNCATION
18:35:58.074  DOWNLOAD MASTERCAM X9 FULL CR-C7EFFD46.pf DATA_EXTEND|DATA_TRUNCATION|CLOSE
18:36:04.371  CAB05196.TMP                              FILE_CREATE   (second extraction pass)
18:36:05.496  K                                         FILE_CREATE
18:36:06.105  K                                         FILE_DELETE|CLOSE
18:36:20.996  MOSCOW.COM-34B22CCB.pf                    DATA_EXTEND|DATA_TRUNCATION|CLOSE
```

**What this gives you**

Key finding: the installer's prefetch file is last written at **2025-06-21 18:35:58.074 UTC**, which is the final flush of its execution record and the last filesystem activity attributable to the installer process. Record that as the termination time.

Read the two execution cycles the journal exposes:

| Cycle | Installer start | Payload staged | Batch written | Terminates |
| --- | --- | --- | --- | --- |
| First | 18:34:19 | 18:34:25 (nine `.wp5` files) | 18:34:31 (`Mysql.wp5.bat`) | prefetch created 18:34:29 |
| Second | 18:35:47 | 18:35:47 (all nine rewritten) | 18:35:48 (rewritten) | prefetch rewritten 18:35:58 |

Note the NSIS signature: `nsv52EF.tmp` and `nsmA020.tmp` are created and immediately deleted at each launch. The `ns*.tmp` naming is how Nullsoft Scriptable Install System unpacks its plugins, confirming the installer is an NSIS package rather than an MSI or InstallShield build.

Caveat this answer honestly. Prefetch is written roughly ten seconds after a process *starts*, so 18:35:58 sits ten seconds after the 18:35:47 launch. In the absence of Security 4689 or Sysmon Event ID 5 it is the closest available proxy for process end, not a recorded exit event.

**Next**

Prefetch and the USN journal both fall short of a true exit record; pivot to the registry, where the Background Activity Moderator stamps processes when they end.

---

### 2.3 Recover the true termination time from BAM
**Say**

> Last option, and it's an obscure one — which is why I like teaching it.
>
> Windows has a component called the Background Activity Moderator. Its real job is power
> management: it throttles background applications to save battery, and to do that it has to keep
> a record of what each user has been running. That record lives in the `SYSTEM` registry hive,
> under `bam\State\UserSettings`, keyed by user SID. Under each SID is a list of executables by
> full NT device path — the `\Device\HarddiskVolume3\` form, not `C:\` — and the first eight
> bytes of each value are a FILETIME.
>
> Nobody built this as a forensic artifact. It's a side effect of battery optimisation, and it is
> one of the most reliable execution records on a modern Windows host precisely because no attacker
> thinks to clear it.
>
> One honest caveat, and say this out loud if anyone asks: BAM's timestamp is usually described as
> "last execution time". What we're reading it as here is the end of the process. Look at where it
> falls relative to the timeline we just built from the journal — that relationship is what
> justifies the interpretation, not the field name.
>
> We're on Linux, so `regipy` reads the raw hive directly. No Windows tooling, no hive mounting.


**Why this step**

Sections 2.1 and 2.2 exhausted the obvious sources: no Sysmon, no Security 4689, and no event-log records at all in the 18:34–18:40 window. Prefetch records starts, not exits. One artifact remains that stamps a process when it *ends* — the Background Activity Moderator, stored in the `SYSTEM` registry hive.

**Command**

```bash
python3 bam.py "evidence/C/Windows/System32/config/SYSTEM"
```

```python
from regipy.registry import RegistryHive
import struct, datetime, binascii

h = RegistryHive('SYSTEM')
k = h.get_key('\\ControlSet001\\Services\\bam\\State\\UserSettings')
for sk in k.iter_subkeys():                      # one subkey per user SID
    for v in sk.get_values():
        b  = binascii.unhexlify(v.value.replace(' ', ''))
        ts = struct.unpack_from('<Q', b, 0)[0]   # FILETIME in first 8 bytes
        print(datetime.datetime(1601,1,1) + datetime.timedelta(microseconds=ts//10), v.name)
```

**Breakdown**

| Component | Meaning | Simple Explanation |
| --- | --- | --- |
| `regipy` | Pure-Python registry hive parser | Reads a raw `SYSTEM` hive on Linux with no Windows tooling |
| `\ControlSet001\Services\bam\State\UserSettings` | BAM's storage location | Where Windows keeps its per-user record of executables |
| Subkey name | A user SID | Attributes every entry to the account that ran it |
| Value name | Full NT device path of the executable | `\Device\HarddiskVolume3\...` rather than `C:\...` |
| First 8 bytes of value data | FILETIME, little-endian | The timestamp, in the same 100-ns-since-1601 format as Prefetch |

**Theory — what BAM is and why its timestamp means "ended"**

The Background Activity Moderator arrived in Windows 10 1709 as a power-management service. It throttles background processes to extend battery life, and to do that it keeps a per-user list of every executable that has run, each with a single FILETIME.

What makes it valuable in an investigation is *when* that timestamp is written. Prefetch stamps a program when it **starts**; BAM updates its entry when the service stops tracking the process — that is, when the process **exits**. For short-lived programs the two are close enough to look interchangeable, but for anything long-running they diverge, and that divergence is precisely what answers a termination question.

Three properties matter in practice. BAM stores only the **most recent** entry per executable, so it cannot build a history the way Prefetch's eight slots can. It records the **full path**, which distinguishes two binaries sharing a filename. And it is **per-user**, which Prefetch is not — so it attributes execution to an account.

Verify the control set before trusting the path. `ControlSet001` is the active configuration here; on a host where `CurrentControlSet` points elsewhere, read that one instead.

**Result**

```
== S-1-5-21-1403634729-3147206146-238420168-500

2025-01-23 22:51:36.910  \Device\HarddiskVolume3\Windows\System32\wscript.exe
2025-01-23 22:57:31.838  \Device\HarddiskVolume3\Ghost Toolbox\toolbox.updater.x64.exe
2025-01-23 22:58:52.635  \Device\HarddiskVolume3\Ghost Toolbox\wget\7z2407-x64.exe
2025-01-23 23:06:46.666  \Device\HarddiskVolume3\Windows\System32\cmd.exe
2025-06-21 16:36:36.272  Microsoft.Windows.Photos_8wekyb3d8bbwe
2025-06-21 18:34:08.465  \Device\HarddiskVolume3\Program Files\7-Zip\7zG.exe
2025-06-21 18:36:04.652  \Device\HarddiskVolume3\Windows\SysWOW64\extrac32.exe
2025-06-21 18:36:52.355  \Device\HarddiskVolume3\Users\Administrator\Downloads\download mastercam x9 full crack pc.exe
2025-06-21 20:39:30.793  \Device\HarddiskVolume3\Program Files (x86)\Microsoft\Edge\Application\msedge.exe
```

**What this gives you**

Key finding: the installer process terminated at **2025-06-21 18:36:52 UTC**.

Reconcile that against the Prefetch and USN evidence, because the gap is informative:

| Event | Time | Source | Simple Explanation |
| --- | --- | --- | --- |
| First execution | 18:34:19 | Prefetch run time 2 | User double-clicks the crack |
| Second execution | 18:35:47 | Prefetch run time 1 | It runs again |
| Prefetch flushed | 18:35:58 | `$MFT` / `$J` on the `.pf` | Windows writes its performance record ~10 s after launch |
| `extrac32` ends | 18:36:04 | BAM | Second cabinet extraction completes |
| **Installer ends** | **18:36:52** | **BAM** | The process finally exits |

The installer outlived its own prefetch flush by 54 seconds — it stayed resident while its batch child ran `choice /d n /t 5`, reassembled the payload and launched `Moscow.com`. That is exactly why Prefetch cannot answer this question and BAM can.

Note the incidental finding in the 2025-01-23 entries: `Ghost Toolbox\toolbox.updater.x64.exe` and `Ghost Toolbox\wget\7z2407-x64.exe`, matching the `Ghost Toolbox.lnk` on the Desktop. This host was already running an unofficial Windows-debloating toolkit months before the incident — a pre-existing risk posture consistent with a user who installs cracked software.

**Next**

Identify which of the staged files landed first, and establish what each one is.


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

==Answer== Mysql.wp5
<div align="center">
<br>
<br>
</div>

### 3.1 Identify the first dropped file and classify the staged set
**Say**

> Task 3 asks for the *first* file the malware dropped. Singular, and ordered — so this is a
> precision question, not a discovery question. We already have the burst in our timeline from
> the journal; now we order it to the millisecond and see what landed first.
>
> But we're going to do a second thing at the same time, and it's the more educational half.
> Every file in that burst carries the same extension. It's a real extension — it belongs to an
> old word processor — and not one of these files has anything to do with word processing. The
> extension is camouflage. That's the box's name, and this is the moment it earns it.
>
> So rather than trusting the extension, we type every file by its actual content — by the magic
> bytes at the front of it. What I want you to see is how *different* these files turn out to be
> from each other despite sharing a name pattern. One of them is a script. One of them is an
> archive. Several of them aren't valid files at all in isolation, and the reason why is the key
> to this entire box.


**Why this step**

The USN timeline in 2.2 shows a burst of file creations 6 seconds after the installer launched. Ordering that burst to the millisecond names the first artifact the malware wrote to disk, and typing each file establishes which are payload and which are decoys.

**Command**

```bash
cd "evidence/C/Users/Administrator/AppData/Local/Temp"
ls -la && file * 448887/*
```

**Breakdown**

| Component | Meaning | Simple Explanation |
| --- | --- | --- |
| `%LOCALAPPDATA%\Temp` | Per-user temp directory | Where the prefetch filenames list in 1.2 pointed |
| `ls -la` | Long listing | Exposes sizes and modification dates |
| `file *` | Magic-byte type identification | Names each file by its content, not its extension — essential when extensions are deliberately wrong |

**Theory — why the extension lies**

`.wp5` is the WordPerfect 5 document extension, chosen precisely because nothing on a modern Windows host handles it. Files with an unknown extension are ignored by Explorer previewers, skipped by many extension-based AV scan policies, and look inert to a user who wanders into their temp folder. `file` reads the first bytes instead of the name, which is why it correctly reports one of these `.wp5` files as a Microsoft Cabinet archive and another as an ASCII batch script.

**Result**

USN ordering of the drop burst:

```
18:34:25.511  Mysql.wp5          FILE_CREATE   <-- first
18:34:25.527  Authorization.wp5  FILE_CREATE
18:34:25.558  Art.wp5            FILE_CREATE
18:34:25.558  Lock.wp5           FILE_CREATE
18:34:25.574  Play.wp5           FILE_CREATE
18:34:25.574  Romania.wp5        FILE_CREATE
18:34:25.621  Refugees.wp5       FILE_CREATE
18:34:25.699  Runner.wp5         FILE_CREATE
18:34:25.746  Gba.wp5            FILE_CREATE
```

Type identification:

```
Mysql.wp5:          ASCII text, with very long lines (763), with CRLF line terminators
Play.wp5:           Microsoft Cabinet archive data, many, 488221 bytes, 11 files, ID 9045,
                    number 1, 29 datablocks, 0x1 compression
Art.wp5:            data
Authorization.wp5:  data
Gba.wp5:            data
Lock.wp5:           data
Refugees.wp5:       data
Romania.wp5:        data
Runner.wp5:         data
448887/Moscow.com:  PE32 executable (GUI) Intel 80386, for MS Windows, 5 sections
Subsequently:       DOS executable (COM)
```

**What this gives you**

Key finding: **`Mysql.wp5`** is the first file the malware wrote after installation, created at **2025-06-21 18:34:25.511 UTC**, and it is plain ASCII text — the obfuscated batch script that drives the entire chain.

Classify the nine staged files into three roles:

| File | Size | True type | Role | Simple Explanation |
| --- | --- | --- | --- | --- |
| `Mysql.wp5` | 19,526 | ASCII batch script | Orchestrator | The instruction sheet for everything that follows |
| `Play.wp5` | 488,221 | Microsoft Cabinet, 11 files | Container | A zip-like archive holding eleven hidden pieces |
| `Runner.wp5` | 76,800 | Opaque binary | Payload fragment 1 | A slice of the final script |
| `Art.wp5` | 58,368 | Opaque binary | Payload fragment 2 | A slice of the final script |
| `Gba.wp5` | 76,800 | Opaque binary | Payload fragment 3 | A slice of the final script |
| `Romania.wp5` | 66,560 | Opaque binary | Payload fragment 4 | A slice of the final script |
| `Refugees.wp5` | 68,608 | Opaque binary | Payload fragment 5 | A slice of the final script |
| `Authorization.wp5` | 78,848 | Opaque binary | Payload fragment 6 | A slice of the final script |
| `Lock.wp5` | 57,717 | Opaque binary | Payload fragment 7 | A slice of the final script |

No single dropped file is a working executable. That is the core evasion idea of this campaign: the malicious binary never exists on disk until the batch script assembles it at runtime, so static scanning of any individual artifact yields nothing.

Note that `Mysql.wp5` was later copied to `Mysql.wp5.bat` at 18:34:31 — the `.bat` extension is only applied at the moment of execution.

**Next**

Hash the cabinet archive to fingerprint the container before examining what the batch does with it.
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

==Answer== `35efc15a41cf54a51703711e0b117b1899e4698bed1a4fdae638ebb7a3a190e0`
<div align="center">
<br>
<br>
</div>

### 4.1 Hash the cabinet archive
**Say**

> Short step, and a procedural one, but worth saying why we bother.
>
> We identified this file as a Microsoft Cabinet archive by content. Hashing it converts that
> observation into something you can actually *use*: an indicator you can hand to a threat-intel
> platform, push to an EDR blocklist, or sweep the rest of the estate for. "I saw a suspicious
> cab file" helps nobody. A SHA-256 is portable proof.
>
> Two habits to pick up here. Hash before you touch — any modification invalidates it. And hash
> the file exactly as collected, not a copy you've extracted and repacked, because repacking a
> cabinet changes the bytes and therefore the hash.


**Why this step**

`file` identified `Play.wp5` as a Microsoft Cabinet in 3.1. A cryptographic hash turns that observation into a shareable indicator of compromise suitable for threat-intelligence lookup and for blocking across the estate.

**Command**

```bash
sha256sum "evidence/C/Users/Administrator/AppData/Local/Temp/Play.wp5"
```

**Breakdown**

| Component | Meaning | Simple Explanation |
| --- | --- | --- |
| `sha256sum` | SHA-256 digest utility | Produces a 64-character fingerprint unique to this exact file content |
| `Play.wp5` | The cabinet archive | Named as a WordPerfect document, actually a `.cab` |

**Theory — why hash the container and not only its contents**

Hashing both matters, for different reasons. The extracted components are what execute, so their hashes detect the payload wherever it lands. The container's hash detects the *delivery package* — and because the eleven files inside are reassembled in a fixed order, a single container hash covers the whole set in one indicator. Note that any re-packing changes the container hash while leaving the component hashes intact, so a defender should deploy both.

**Result**

```
35efc15a41cf54a51703711e0b117b1899e4698bed1a4fdae638ebb7a3a190e0  Play.wp5
```

Supporting metadata from `file`:

```
Play.wp5: Microsoft Cabinet archive data, many, 488221 bytes, 11 files, at 0x2c
          last modified Sun, Jun 20 2025 02:40:38 +A "Theology"
          last modified Sun, Jun 20 2025 02:40:38 +A "Thanksgiving",
          ID 9045, number 1, 29 datablocks, 0x1 compression
```

**What this gives you**

Key finding: the cabinet's SHA-256 is **`35efc15a41cf54a51703711e0b117b1899e4698bed1a4fdae638ebb7a3a190e0`**, containing **11 files**, built **2025-06-20 02:40:38** — one day before deployment to this host.

That build date is itself evidence: the archive predates the infection by roughly 40 hours, so the package was prepared in advance rather than generated per-victim. The internal member names visible in the header (`Theology`, `Thanksgiving`) match files that appear in `%TEMP%` at 18:34:48, confirming this archive is the source of the second-stage drop.

**Next**

Deobfuscate the batch script to recover the exact command used against this archive.
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

==Answer== `extrac32 /Y Play.wp5 *.*`
<div align="center">
<br>
<br>
</div>

### 5.1 Deobfuscate the batch script
**Say**

> This is the centre of the box. Everything before it was timeline work; everything after it comes
> out of this file.
>
> The batch script is the orchestrator — it's the thing that actually drives the infection — and
> it's been made deliberately unreadable. The obfuscation here isn't encryption and it isn't
> clever. It's character-level variable substitution: the author defines a pile of environment
> variables holding one or two characters each, then builds every real command out of them, so
> that a command like `extrac32` never appears as those eight letters anywhere in the file. Any
> tool grepping for suspicious command names sees nothing.
>
> The counter is just as unglamorous: resolve the substitutions and put the string back together.
> No decryption, no key. Patience.
>
> And here's why this one step is worth the effort — it answers *two* tasks at once. The
> extraction command Task 5 asks for is in here. So are the security-product checks Task 6 counts.
> When we're done reading this file we'll have both, plus the whole sequence of what ran and in
> what order.
>
> Read it slowly. Every line in here is a decision the author made.


**Why this step**

`Mysql.wp5` is the orchestrator identified in 3.1, but it is deliberately unreadable. Resolving its variable substitutions exposes every command the malware issued, including the cabinet extraction that Task 5 asks for and the AV checks Task 6 counts.

**Command**

```bash
tr -d '\r' < Mysql.wp5 > b.txt
python3 deobf.py b.txt
```

`deobf.py` collects every simple `Set Name=Value` assignment, then recursively expands `%Name%` references across the whole file:

```python
import re
env = {}
for l in lines:
    m = re.match(r'^[Ss]et\s+([A-Za-z0-9_]+)=(.*)$', l)
    if m:
        env[m.group(1).lower()] = m.group(2)

def sub(s, depth=6):
    for _ in range(depth):
        new = re.sub(r'%([A-Za-z0-9_]+)%',
                     lambda m: env.get(m.group(1).lower(), m.group(0)), s)
        if new == s:
            break
        s = new
    return s
```

**Breakdown**

| Component | Meaning | Simple Explanation |
| --- | --- | --- |
| `tr -d '\r'` | Strip carriage returns | The file uses Windows CRLF line endings; removing `\r` keeps the regexes clean |
| `re.match(r'^[Ss]et\s+(\w+)=(.*)')` | Capture variable definitions | Builds the substitution dictionary |
| Recursive `re.sub` with depth 6 | Expand nested references | Variables are built from other variables, so one pass is not enough |

**Theory — character-level batch obfuscation**

Each `Set` statement assigns a **single character** to an innocuous English word: `Set Stopping=o`, `Set Washington=f`, `Set Adventures=n`. Commands are then written as mosaics of those references — `%Washington%i%Adventures%%Climate%str` reassembles to `findstr` only when the interpreter expands them.

Two properties make this effective. Signature-based detection fails because the literal string `findstr` never appears in the file. Human review fails because the real logic is buried in 422 lines of which roughly 380 are junk — decoy lines like `mvwSphere(Arising(` that `cmd.exe` evaluates as malformed commands, discards, and continues past. Padding with garbage that the interpreter tolerates is a deliberate anti-analysis technique, not a bug.

The complete substitution table recovered from the script:

| Variable | Char | Variable | Char | Variable | Char | Variable | Char |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Ten | 5 | Ballet | X | Adventures | n | Subsection | m |
| Focusing | B | Loaded | F | Municipal | P | Of | x |
| Wide | c | Letting | y | Closest | 9 | Stopping | o |
| Generation | K | Tent | z | Fastest | w | Wow | 1 |
| Attending | g | Climb | h | Yu | C | Warranty | 2 |
| Expired | 8 | Warranties | V | Climate | d | Dropped | U |
| Launch | H | Decor | O | Data | W | Unsigned | / |
| Interactive | 6 | Digit | L | Taylor | k | Washington | f |
| Minimum | b | Assured | . | Tu | 3 | | |

**Result**

The 42 operative lines recovered from 422, in execution order:

```
302: Set oAPkKvaBlQaxyRaxdUooCTLzBRRQfXVtixj=Moscow.com
307: Set PWFtGNjfw= 
318: Set yIpWXmEeJiPlXYAAmcMkIlfSPB=5
327: tasklist | findstr /I "opssvc wrsa" & if not errorlevel 1 ping -n 192 127.0.0.1
334: Set /a Wing=448887
338: tasklist | findstr "bdservicehost SophosHealth AvastUI AVGUI nsWscSvc ekrn" & if not errorlevel 1
       Set oAPkKvaBlQaxyRaxdUooCTLzBRRQfXVtixj=AutoIt3.exe
       & Set PWFtGNjfw=.a3x
       & Set yIpWXmEeJiPlXYAAmcMkIlfSPB=300
344: md 448887
354: extrac32 /Y Play.wp5 *.*
360: set /p ="MZ" > 448887\Moscow.com <nul
363: findstr /V "Surplus" Balls >> 448887\Moscow.com
367: copy /b 448887\Moscow.com + Hell + Analyze + Theology + Thanksgiving + Subsequently
       + Mechanisms + Dawn + Draws + Appreciated + Investors 448887\Moscow.com
374: cd 448887
384: copy /b ..\Runner.wp5 + ..\Art.wp5 + ..\Gba.wp5 + ..\Romania.wp5 + ..\Refugees.wp5
       + ..\Authorization.wp5 + ..\Lock.wp5 K
387: start Moscow.com K
403: cd ..
413: choice /d n /t 5
```

**What this gives you**

Key finding: the cabinet is extracted with **`extrac32 /Y Play.wp5 *.*`**.

Break the command down:

| Element | Meaning | Simple Explanation |
| --- | --- | --- |
| `extrac32` | Signed Microsoft cabinet extraction utility in `System32` | A living-off-the-land binary — no attacker tool needs to be dropped |
| `/Y` | Suppress overwrite prompts | Runs unattended, silently replacing any existing file |
| `Play.wp5` | Source archive | The `.cab` despite its extension; `extrac32` reads magic bytes, not the name |
| `*.*` | Extract all members | Pulls all eleven files into the current directory |

`extrac32` is corroborated independently: `EXTRAC32.EXE-4FD3FA35.pf` is created at 18:34:49.168, immediately after the eleven cabinet members appear at 18:34:48.9–49.0, and `CAB05572.TMP` scratch files are created and deleted throughout the extraction.

Note the reconstruction logic that follows. `Moscow.com` is seeded with the two literal bytes `MZ`, extended with `Balls` minus its marker line, then concatenated with ten further fragments — an executable that exists only after the batch finishes assembling it.

**Next**

Count the security products the script fingerprints before it commits to that reconstruction.
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

==Answer== `6`
<div align="center">
<br>
<br>
</div>

### 6.1 Count the AV/EDR strings searched
**Say**

> Now, this question has a trap in it, and I want to walk into it deliberately rather than around
> it, because how you handle it is the actual lesson.
>
> The deobfuscated script has two separate places where it pipes a process listing into a string
> search. Two checks, not one. And they don't contain the same number of product names. So if you
> count every security-product string the malware looks for anywhere in this file, you get one
> number. If you count the strings in the check that actually decides what the malware does next,
> you get a smaller one. Both are defensible. Only one is the answer.
>
> Read the question again when we get the output: it asks how many product-related strings it
> *searched for*, in the context of the evasion behaviour. The check that branches is the check
> that counts.
>
> And while we're here — look at what these product names are. Bitdefender, Sophos, Avast, AVG,
> Norton, ESET. Consumer antivirus, almost exclusively. That tells you who this campaign expects
> to be attacking. Nobody targeting an enterprise writes a check for AvastUI. This is built for
> home machines running free AV, which is exactly the population that goes looking for cracked CAD
> software.
>
> One more thing to notice, and it's the satisfying bit: none of these checks fire on this victim.
> We established back in Section 2 that the host had no AV and no EDR at all. All this evasion
> logic is sitting there in the sample, fully functional, and it never once ran.


**Why this step**

Lines 327 and 338 of the deobfuscated script both pipe `tasklist` into `findstr`. Each is a process-name check against known security software, and Task 6 asks for the total number of product strings searched.

**Command**

```bash
grep -nE "tasklist \| findstr" deobfuscated.txt
```

**Breakdown**

| Component | Meaning | Simple Explanation |
| --- | --- | --- |
| `grep -n` | Print matching lines with numbers | Locates both checks in the recovered script |
| `tasklist` | Lists every running process | The malware's way of seeing what is running without any special tooling |
| `\|` | Pipe | Feeds that list into the next command |
| `findstr` | String search | Tests whether any listed process matches a security product |
| `/I` | Case-insensitive (line 327 only) | The second check is case-sensitive; the first is not |

**Theory — how a batch script fingerprints defences**

`tasklist | findstr "<names>"` sets `errorlevel` to 0 on a match and 1 on no match. The script then branches on `if not errorlevel 1`, which is batch's awkward way of saying "if errorlevel is 0 or less" — that is, if something matched.

The two checks respond very differently, and that difference is the interesting part:

- **Line 327** — on a match, `ping -n 192 127.0.0.1` sleeps roughly 191 seconds. This is a sandbox and analyst timeout play: many automated sandboxes abandon a sample after 120 seconds of apparent inactivity, so the malware simply waits them out.
- **Line 338** — on a match, the script *changes its own identity*. `Moscow.com` becomes `AutoIt3.exe`, the script extension becomes `.a3x`, and the post-execution delay grows from 5 to 300 seconds. Running as a correctly-named, legitimately-signed AutoIt interpreter loading a correctly-named `.a3x` script is far less anomalous to a behavioural engine than a `.com` file loading an extensionless blob.

Both branches are evasion, not abort. The malware never stops on detection; it adapts.

**Result**

```
327: tasklist | findstr /I "opssvc wrsa"
       & if not errorlevel 1 ping -n 192 127.0.0.1

338: tasklist | findstr "bdservicehost SophosHealth AvastUI AVGUI nsWscSvc ekrn"
       & if not errorlevel 1 Set ...=AutoIt3.exe & Set ...=.a3x & Set ...=300
```

**What this gives you**

Key finding: the accepted answer is **6** — the six security-product strings in the second check (line 338), which are the actual AV/EDR product process names:

| # | String | Vendor / product | Simple Explanation |
| --- | --- | --- | --- |
| 1 | `bdservicehost` | Bitdefender | Bitdefender's service host |
| 2 | `SophosHealth` | Sophos | Sophos endpoint health service |
| 3 | `AvastUI` | Avast | Avast's user interface process |
| 4 | `AVGUI` | AVG | AVG's user interface process |
| 5 | `nsWscSvc` | Norton | Norton's Security Center service |
| 6 | `ekrn` | ESET | ESET's kernel service |

Count the full picture separately from the expected answer, because the two differ and the difference is worth understanding. Line 327 searches two further strings — `opssvc` (Quick Heal) and `wrsa` (Webroot) — and section 6.2 shows the payload performing a ninth check of its own. Nine security-product checks are therefore observable across the chain; **six** is the count of product strings in the check that defines the malware's evasion branch, and that is what the question asks for.

| # | String | Vendor / product | Simple Explanation |
| --- | --- | --- | --- |
| 1 | `opssvc` | Quick Heal | Quick Heal's background service |
| 2 | `wrsa` | Webroot SecureAnywhere | Webroot's main agent |
| 3 | `bdservicehost` | Bitdefender | Bitdefender's service host |
| 4 | `SophosHealth` | Sophos | Sophos endpoint health service |
| 5 | `AvastUI` | Avast | Avast's user interface process |
| 6 | `AVGUI` | AVG | AVG's user interface process |
| 7 | `nsWscSvc` | Norton | Norton's Security Center service |
| 8 | `ekrn` | ESET | ESET's kernel service |

Note which check found nothing here. Section 2.1 established the host had no Defender operational log and no EDR of any kind, so neither branch fired: the chain proceeded down its default path as `Moscow.com` with a 5-second delay. The evasion logic is present in the sample but was never exercised on this victim.

**Next**

Extend the count into the AutoIt payload, which performs its own process check.

---

### 6.2 Add the payload's own process check
**Say**

> Before we accept our number, we owe the question one more look. It says "in memory or processes"
> — and that phrasing deliberately reaches past the batch script.
>
> The batch file is not the only stage that checks for security software. The AutoIt payload does
> its own check, using AutoIt's native process function rather than the command line, which means
> nothing in the batch would ever have shown it to us. Different stage, different mechanism, same
> intent.
>
> Watch which product it looks for, because it's one we've already seen — checked twice, by two
> different stages, using two different spellings. That redundancy is a small piece of attribution
> evidence in itself: it suggests the batch and the payload were written by different people, or
> assembled from different kits.
>
> And note what it does when it finds it. Not abort. Not exit. It stalls — a delay, then carry on
> regardless. That's a pattern across this whole sample: every branch leads to execution. The
> author never wrote an off-ramp.


**Why this step**

The batch script accounts for eight strings, but Task 6 asks about checks "in memory or processes" — wording that reaches past the batch into the AutoIt payload. Searching the decompiled script (recovered in 10.1) for process-enumeration calls closes the count.

**Command**

```bash
grep -aoE 'ProcessExists" , "[^"]+"' decoded.au3
grep -aoE '"[A-Za-z0-9_.-]+\.exe"' decoded.au3 | sort -u
```

**Breakdown**

| Component | Meaning | Simple Explanation |
| --- | --- | --- |
| `ProcessExists` | AutoIt built-in | Returns a PID if a named process is running, 0 otherwise — the scripting equivalent of `tasklist \| findstr` |
| `grep -aoE` | Binary-safe, print matches only | Extracts just the matched call rather than the surrounding obfuscated line |

**Result**

```
ProcessExists" , "avastui.exe"
```

```
"explorer.exe"
"avastui.exe"
```

In context:

```
( Call ( "ProcessExists" , "avastui.exe" ) ) ? CONGRATULATIONSCONTRASTPASTESTUART ( 10000 )
                                             : ( Opt ( "TrayIconHide" , 1 ) )
```

**What this gives you**

Key finding: the payload performs a further security-product check of its own, beyond the eight in the batch script — nine observable across the whole chain, against the six counted for Task 6.

| # | String | Stage | Method | Vendor |
| --- | --- | --- | --- | --- |
| 1 | `opssvc` | Batch | `tasklist \| findstr /I` | Quick Heal |
| 2 | `wrsa` | Batch | `tasklist \| findstr /I` | Webroot |
| 3 | `bdservicehost` | Batch | `tasklist \| findstr` | Bitdefender |
| 4 | `SophosHealth` | Batch | `tasklist \| findstr` | Sophos |
| 5 | `AvastUI` | Batch | `tasklist \| findstr` | Avast |
| 6 | `AVGUI` | Batch | `tasklist \| findstr` | AVG |
| 7 | `nsWscSvc` | Batch | `tasklist \| findstr` | Norton |
| 8 | `ekrn` | Batch | `tasklist \| findstr` | ESET |
| 9 | `avastui.exe` | AutoIt payload | `ProcessExists` | Avast |

Note that entries 3–8 are the ones counted for Task 6 — the six product strings in the line 338 check, which is the one that defines the evasion branch. Entries 1, 2 and 9 are additional checks the chain performs outside that branch.

Note that Avast is checked twice, by two different stages using two different mechanisms. Entries 5 and 9 are distinct strings (`AvastUI` against a `tasklist` line versus `avastui.exe` as an exact process name) and each is counted separately.

The payload's response also differs from the batch's. Where the batch changed its own filename to blend in, the AutoIt script calls a delay routine with an argument of 10000 — a ten-second stall before continuing. Again, evasion rather than abort.

**Next**

Follow the default branch to the process that actually executed after the batch completed.
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

==Answer== `Moscow.com`
<div align="center">
<br>
<br>
</div>

### 7.1 Identify the process launched by the batch script
**Say**

> Neither AV check matched, so the script stayed on its default branch — and that branch is where
> it finally launches something.
>
> Two independent sources agree on what ran, and I want to make a point of using both. The batch
> script *says* what it intends to launch. Prefetch *proves* something by that name actually
> executed. Intent and evidence, from two artifacts that know nothing about each other. That's
> what corroboration looks like, and it's the difference between "the script contains this line"
> and "this ran on this host at this time".
>
> Watch the file extension on the thing that runs. It is not the extension you expect on a Windows
> executable, and that choice is deliberate — it's old, it's legal, it still executes, and it
> reads as harmless to both a human skim and a lot of naive tooling.


**Why this step**

Section 6.1 established that neither AV check matched, so the script stayed on its default branch. Line 387 of the deobfuscated batch names the process that branch launches, and Prefetch independently confirms it executed.

**Command**

```bash
grep -n "^start\|^md \|^copy /b\|^set /p" deobfuscated.txt
sccainfo "evidence/C/Windows/prefetch/MOSCOW.COM-34B22CCB.pf" | head -20
```

**Breakdown**

| Component | Meaning | Simple Explanation |
| --- | --- | --- |
| `grep "^start"` | Find the launch command | Isolates the line that starts a new process |
| `sccainfo` | Prefetch parser from 1.2 | Confirms from Windows' own records that the process really ran |

**Theory — why a `.com` extension**

`.com` dates to MS-DOS, where it meant a flat binary loaded at offset 0x100. Modern Windows keeps the extension executable purely for backwards compatibility, and the loader ignores the name entirely: it reads the `MZ` header and the PE structure underneath. A PE32 executable named `x.com` runs exactly as it would named `x.exe`.

Attackers exploit this in two ways. Detection rules and allow-lists written around `*.exe` miss `.com` outright, and an analyst skimming a process list reads `.com` as either a legacy artifact or — at a glance — as a domain name. `PATHEXT` also places `.COM` *before* `.EXE` in resolution order, so `start Moscow.com` needs no path juggling.

**Result**

From the deobfuscated batch:

```
344: md 448887
360: set /p ="MZ" > 448887\Moscow.com <nul
363: findstr /V "Surplus" Balls >> 448887\Moscow.com
367: copy /b 448887\Moscow.com + Hell + Analyze + Theology + Thanksgiving + Subsequently
       + Mechanisms + Dawn + Draws + Appreciated + Investors 448887\Moscow.com
384: copy /b ..\Runner.wp5 + ..\Art.wp5 + ..\Gba.wp5 + ..\Romania.wp5 + ..\Refugees.wp5
       + ..\Authorization.wp5 + ..\Lock.wp5 K
387: start Moscow.com K
```

Prefetch confirmation:

```
Format version      : 30
Prefetch hash       : 0x34b22ccb
Executable filename : MOSCOW.COM
Run count           : 2
```

USN corroboration:

```
18:34:47.418  448887      FILE_CREATE
18:34:49.480  Moscow.com  FILE_CREATE
18:34:49.528  Moscow.com  DATA_EXTEND|FILE_CREATE|CLOSE
18:34:49.668  Moscow.com  DATA_EXTEND
18:34:50.168  Moscow.com  DATA_EXTEND|CLOSE
18:35:01.121  MOSCOW.COM-34B22CCB.pf  FILE_CREATE
```

**What this gives you**

Key finding: the process launched after the batch script is **`Moscow.com`**, at `C:\Users\Administrator\AppData\Local\Temp\448887\Moscow.com`.

Trace how it was built, because no antivirus ever saw a complete file until the last step:

| Step | Command | Effect | Simple Explanation |
| --- | --- | --- | --- |
| 1 | `md 448887` | Create a numeric working directory | A throwaway folder with a meaningless name |
| 2 | `set /p ="MZ" > Moscow.com <nul` | Write the two-byte PE magic | Types the first two characters of a Windows program by hand |
| 3 | `findstr /V "Surplus" Balls >> Moscow.com` | Append `Balls` minus its marker line | Strips a sentinel line, appends the rest |
| 4 | `copy /b … + 10 fragments` | Binary-concatenate ten more pieces | Glues the remaining chunks on in order |

The staggered `DATA_EXTEND` events at 18:34:49.5, 49.7 and 50.0 are exactly this incremental assembly visible in the journal.

Note the parallel construction: `K` is assembled the same way from the seven remaining `.wp5` fragments and passed to `Moscow.com` as its only argument.

**Next**

Determine what `Moscow.com` actually is by reading its embedded version metadata.
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

==Answer== `AutoIt3.exe`
<div align="center">
<br>
<br>
</div>

### 8.1 Recover the original filename from PE metadata
**Say**

> We have a process name, and the name is meaningless — it's a place, it matches no product, it
> tells us nothing. So the question becomes: what *is* this binary, really?
>
> Here's the artifact that answers it. Windows executables carry an embedded version resource: a
> structured block of metadata the compiler writes in, holding the company name, the product name,
> the version, and critically the **original filename** — the name the developer built it under.
> Renaming a file on disk does not touch that resource. It survives.
>
> So we read it, and the binary tells us what it used to be called.
>
> And when you see the answer, sit with it for a second, because this is the cleverest move in the
> entire sample. What we're looking at is not malware. It's a legitimate, signed, publicly
> downloadable interpreter — a real product from a real vendor, with a valid signature. The
> attacker didn't write it, didn't modify it, and didn't need to. They renamed it and shipped it
> alongside a script.
>
> Think about what that does to your defences. The binary is signed. Its hash is known-good. It
> is on every allowlist. Any control asking "is this executable trustworthy" answers yes, correctly.
> The malice isn't in the file — it's in the file it was pointed at.


**Why this step**

`Moscow.com` is a 947 KB PE32 GUI binary with a meaningless name. Windows executables embed a version resource that records the filename the developer compiled them under, which survives renaming and identifies the real product.

**Command**

```bash
strings -el "evidence/C/Users/Administrator/AppData/Local/Temp/448887/Moscow.com" \
  | grep -iE "original|autoit|product|company"
```

**Breakdown**

| Component | Meaning | Simple Explanation |
| --- | --- | --- |
| `strings` | Extract printable sequences | Pulls readable text out of a binary |
| `-el` | 16-bit little-endian encoding | PE version resources store strings as UTF-16LE; plain ASCII `strings` misses them entirely |
| `grep -iE "original\|autoit\|…"` | Filter to identity fields | `OriginalFilename`, `ProductName` and `CompanyName` are the identifying fields |

**Theory — what a PE version resource is, and why renaming does not touch it**

Every well-built Windows executable carries a `VS_VERSIONINFO` resource — the data Explorer shows on the Details tab of a file's properties. It holds `CompanyName`, `ProductName`, `FileDescription`, `FileVersion`, `InternalName` and `OriginalFilename`.

`OriginalFilename` is the field that matters in forensics. It is baked in at compile time and lives inside the file's resource section, so renaming the file on disk changes nothing about it. Any mismatch between the on-disk name and `OriginalFilename` is a masquerading indicator on its own. A second, stronger check applies here: an Authenticode signature covers the file's contents including that resource, so a signed binary's stated identity cannot be altered without breaking the signature.

**Result**

```
AutoIt
AutoIt v3
AutoIt v3 GUI
#OnAutoItStartRegister
/AutoIt3ExecuteScript
/AutoIt3ExecuteLine
/AutoIt3OutputDebug
Software\AutoIt v3\AutoIt
AUTOITWINSETTITLE
AUTOITWINGETTITLE
AUTOITSETOPTION
AUTOITVERSION
AUTOITEXE
AUTOITPID
AUTOITUNICODE
AUTOITX64
https://www.autoitscript.com/autoit3/
http://crl.globalsign.com/gscodesignsha2g3.crl
http://ocsp2.globalsign.com/gscodesignsha2g3
```

Independent confirmation from the batch script's AV-evasion branch (line 338):

```
Set oAPkKvaBlQaxyRaxdUooCTLzBRRQfXVtixj=AutoIt3.exe
```

**What this gives you**

Key finding: `Moscow.com` is a renamed copy of **`AutoIt3.exe`**, the legitimate AutoIt v3 script interpreter, GlobalSign code-signed and published by AutoIt Consulting Ltd.

Two independent proofs support this, which is what makes the attribution solid rather than inferred:

| Evidence | Source | Simple Explanation |
| --- | --- | --- |
| AutoIt v3 product strings and command-line switches | PE resource and string table | The binary identifies itself as the AutoIt interpreter |
| GlobalSign code-signing chain referencing `autoitscript.com` | Embedded certificate | It is the genuine signed AutoIt release, unmodified |
| `Set …=AutoIt3.exe` in the AV branch | Deobfuscated batch script | The malware author's own code names the file it is masquerading |

Note the technique: this is not a trojanised binary. It is the real, signed AutoIt interpreter, renamed. Signature-based detection and certificate-trust checks both pass, because the file genuinely is what it claims to be — the malice lives entirely in the script it is told to run.

**Next**

Reconstruct and hash the script that this interpreter loaded.
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

==Answer== `2b3d1561b9ae7fa2bd3f09dee28a327b5647a908113945cd2a943134822d18d0`
<div align="center">
<br>
<br>
</div>

### 9.1 Reconstruct and hash the loaded AutoIt script
**Say**

> Task 9 wants the hash of the file the interpreter loaded. And we have a problem: that file does
> not exist.
>
> Look back at the journal timeline. It was created, it was used, and it was deleted roughly two
> seconds later. It isn't in the collection. KAPE never saw it, because by the time KAPE ran it had
> been gone for two hours.
>
> So we rebuild it. And we can, because of how it was made in the first place. This malware never
> shipped a complete payload — it shipped *pieces*, disguised with that same harmless extension,
> and had Windows glue them together at runtime with a binary copy. Every one of those pieces is
> still on disk. They survived precisely because individually they aren't malicious; they aren't
> even valid files.
>
> Two things have to be right for this to work, and this is the part people get wrong. The exact
> set of fragments, and the exact order. Get either wrong and you produce a file that is
> byte-for-byte different, which means a completely different hash, which means a wrong answer with
> no indication you were wrong. The batch script tells us both — we're not guessing the order, we're
> reading it.
>
> This is the single most satisfying step in the box: reconstructing a deleted file from parts and
> proving it's the right one by hash.


**Why this step**

Line 387 runs `start Moscow.com K`, so `K` is the script the interpreter loaded. The USN journal shows `K` created at 18:34:50.684 and deleted at 18:34:52.980 — it is not in the collection and must be rebuilt from the fragments that are.

**Command**

```bash
cd "evidence/C/Users/Administrator/AppData/Local/Temp"
cat Runner.wp5 Art.wp5 Gba.wp5 Romania.wp5 Refugees.wp5 Authorization.wp5 Lock.wp5 > K
sha256sum K && ls -l K && strings -n 8 K | head -1
```

**Breakdown**

| Component | Meaning | Simple Explanation |
| --- | --- | --- |
| `cat a b c > K` | Byte-exact concatenation | The POSIX equivalent of Windows `copy /b`; order is what matters |
| Fragment order | `Runner → Art → Gba → Romania → Refugees → Authorization → Lock` | Taken verbatim from batch line 384 — any other order produces a different, wrong hash |
| `sha256sum` | Digest | Fingerprints the reconstructed script |
| `strings -n 8 \| head -1` | First long printable run | Exposes the file-format magic |

**Theory — reconstructing a deleted file from surviving inputs**

`copy /b` performs raw binary concatenation with no headers, padding or alignment. So when the inputs survive and the recipe is known, the output is reproducible byte for byte on any platform — `cat` in the listed order yields an identical file and therefore an identical hash.

Two conditions must hold, and both are checkable. The fragment order must match the batch exactly, because concatenation is not commutative; and the fragments must be in the same state they were when the copy ran. Here the USN journal shows all nine `.wp5` files rewritten at 18:35:47 during the installer's second run, and `K` rebuilt from them at 18:36:05 — so the collected fragments correspond to the second, final assembly. A valid `AU3!EA06` header in the result is the practical confirmation that the reconstruction succeeded.

**Result**

```
2b3d1561b9ae7fa2bd3f09dee28a327b5647a908113945cd2a943134822d18d0  K
-rw-r--r-- 1 root root 483701  K
```

Header verification:

```
000000  a5 df 98 90 16 33 b6 02  e7 4a e9 e0 bf 11 9d 7c
offset 0x03: "AU3!EA06"
```

USN corroboration of both assemblies:

```
18:34:50.684  K  FILE_CREATE
18:34:50.746  K  DATA_EXTEND|FILE_CREATE|CLOSE
18:34:52.980  K  FILE_DELETE|CLOSE
18:36:05.496  K  FILE_CREATE
18:36:06.105  K  FILE_DELETE|CLOSE
```

**What this gives you**

Key finding: the file loaded by `Moscow.com` is **`K`**, 483,701 bytes, SHA-256 **`2b3d1561b9ae7fa2bd3f09dee28a327b5647a908113945cd2a943134822d18d0`**.

The `AU3!EA06` magic identifies it as a **compiled AutoIt v3 script** (`.a3x` format, AutoIt 3.3.14 and later) — source code compiled into AutoIt bytecode, then compressed and encrypted. This is why the seven fragments are entirely opaque to `file` and yield no strings: the payload is ciphertext until the interpreter decrypts it in memory.

Note the anti-forensic step. `K` is deleted two seconds after launch, on both runs. Had `Runner.wp5` through `Lock.wp5` not survived in `%TEMP%`, the actual malicious logic would be unrecoverable from this collection — the interpreter is signed and benign, and the fragments are meaningless in isolation.

**Next**

Decrypt the reconstructed script and trace its network configuration.
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

==Answer== `crowfza.xyz`
<div align="center">
<br>
<br>
</div>

### 10.1 Unpack the AutoIt payload and identify the C2 domain
**Say**

> Last question, and it's several layers deep. Let me lay out the road before we start, because
> it's easy to get lost in here.
>
> We have a compiled AutoIt script. Compiled, not source — so first we extract the source back
> out of it. That source is obfuscated: every meaningful string is built at runtime by a decoder
> function from a list of numbers, so there is no domain sitting in there to grep for. That's why
> a plaintext string search fails on this box, and it's where a lot of people give up and go
> looking for the answer in network evidence that doesn't exist.
>
> Under that, the script carries a blob of hex. That blob is RC4-encrypted, with the key sitting
> in plain sight in the script itself — because it has to be, the script needs it to run. Decrypt
> that and you get compressed data. Decompress it — Windows' own LZNT1, called through ntdll —
> and out falls a complete PE file. An executable that has never existed on disk anywhere, at any
> point. It lives only in memory, and it gets injected into a legitimate Windows process.
>
> Four layers: compiled, obfuscated, encrypted, compressed. None of them individually is hard. The
> defence is the stacking.
>
> Every key we need is in front of us. Nothing here needs cracking — it needs unwrapping, in order.


**Why this step**

The compiled script `K` holds the malware's actual behaviour. Extracting its source, decoding its string obfuscation and unpacking the PE it injects establishes what the malware does and where it connects.

**Command**

```bash
pip install autoit-ripper
python3 -c "
from autoit_ripper import extract, AutoItVersion
data = open('K','rb').read()
for name, content in extract(data=data, version=AutoItVersion.EA05):
    open(name,'wb').write(content)"
```

Then decode the string obfuscation, RC4-decrypt the embedded blob and LZNT1-decompress it:

```python
# 1. STORM("73J114J122J75J105J120", 6 + 4294967294) -> chr(code - offset)
#    offset arithmetic is signed 32-bit: 4294967294 == -2
# 2. RC4 the concatenated $ANGUBW hex blob with the literal key from the script
# 3. ntdll RtlDecompressBuffer format 2 == LZNT1
```

**Breakdown**

| Component | Meaning | Simple Explanation |
| --- | --- | --- |
| `autoit-ripper` | AutoIt script extractor | Reverses AutoIt's compression and decryption to recover readable source |
| `AutoItVersion.EA05` | Legacy format selector | `EA06` fails on this sample; `EA05` succeeds — try both |
| `STORM(codes, offset)` | The script's string decoder | Every literal is stored as character codes with a per-call numeric offset |
| RC4 with a numeric-string key | Payload decryption | The script decrypts its embedded executable at runtime |
| LZNT1 via `RtlDecompressBuffer` | Decompression | Windows' own compression API, called so no compression library has to be bundled |

**Theory — a four-layer unpacking chain, one layer at a time**

Each layer exists to defeat a different analysis technique, and understanding why is more useful than memorising the steps:

1. **Compiled AutoIt (`.a3x`)** — the source is not text on disk, so `strings` and grep find nothing.
2. **`STORM` string encoding** — even after decompiling, no API name, path or command appears literally. `STORM("73J114J122J75J105J120", 6 + 4294967294)` subtracts 4 from each code and yields `EnvGet`. The offset is expressed as an arithmetic pair using unsigned 32-bit wraparound, so `4294967294` is `-2`.
3. **Control-flow flattening** — every function body is wrapped in `While … Switch … Case` blocks padded with no-op calls to `Log()`, `Chr()`, `Floor()` and `ObjGet()` on nonsense strings. Real logic sits in one live `Case`; the rest is chaff.
4. **RC4 + LZNT1 encrypted PE** — the final executable is stored as a 221,249-byte hex blob assembled across eight `$ANGUBW = $ANGUBW & "…"` statements, RC4-encrypted, then LZNT1-compressed. It never touches disk; it is decrypted in memory and injected.

**Result**

Recovered main logic:

```
( Call ( "EnvGet" , "COMPUTERNAME" ) = "tz" ) ? ( Call ( "WinClose" , Call ( "AutoItWinGetTitle" ) ) )
                                              : ( Opt ( "TrayIconHide" , 1 ) )

Global $LIBERTYFIGHTMASSACHUSETTSMORRIS = SERIOUSLYREADILYSEMITHEOREM (
    DARKWEEKENDALTHOUGH ( GEMATAHOLDEMEACH ( Binary ( $ANGUBW ) ,
    Binary ( "71301344071371155438579663303386877993" ) ) ) , $BLOCKEDINTROOWENCAMPUS )

Func SERIOUSLYREADILYSEMITHEOREM ( $ESSENTIALLYBAILEY , $BLOCKEDINTROOWENCAMPUS ,
                                   $VIEWSELECTRONTUTORIALSTURN = "explorer.exe" )

Func DARKWEEKENDALTHOUGH ( $ESSENTIALLYBAILEY )
    $COMPILEREMPTYPOTATOES = DllCall ( "ntdll.dll" , "uint" , "RtlGetCompressionWorkSpaceSize" ,
                                       "ushort" , 2 , "ulong*" , 0 , "ulong*" , 0 )
```

Unpacking results:

```
payload bytes (hex-decoded $ANGUBW) : 221249
after RC4                            : starts 46 ba 00 "MZ" ...  (LZNT1 chunk header)
after LZNT1 decompress               : 351744 bytes
file                                 : PE32 executable (GUI) Intel 80386, 4 sections
SHA-256                              : 268b44beaa84147c2f8bf78a1f5527144864f1da6d0833d71298bb2716d3df5d
```

Final-stage imports:

```
KERNEL32.dll  CreateThread, ExitProcess, GetCurrentProcessId, GlobalLock, GlobalUnlock
SHELL32.dll   SHGetFileInfoW, SHGetSpecialFolderPathW
GDI32.dll     BitBlt, CreateCompatibleBitmap, CreateCompatibleDC, CreateDIBSection, GetObjectW
ole32.dll     CoCreateInstance, CoInitialize, CoInitializeSecurity, CoSetProxyBlanket
USER32.dll    OpenClipboard, GetClipboardData, CloseClipboard, GetDC, GetWindowRect
```

Attacker infrastructure recovered from browser and filesystem artifacts:

```
Edge History:
  https://www.bing.com/search?q=mastercam+x9+full+crack
  https://fancli.com/2wAHI6                                        ("SAVEDROP")
  https://media.cloud839v1.cfd/Download+Mastercam+X9+Full+Crack+Pc.zip

$MFT:        cloud839v1.cfd
Favicons:    cloud839v1.cfd
$Recycle.Bin $I records:
  C:\Users\Administrator\Downloads\Download Mastercam X9 Full Crack Pc.7z
  C:\Users\Administrator\Downloads\download mastercam x9 full crack pc.exe
```

**What this gives you**

Key finding: the **delivery** domain is **`media.cloud839v1.cfd`**, reached via the redirector `fancli.com/2wAHI6` after a Bing search for a Mastercam crack. This is where the victim fetched the trojanised archive — it is not the command-and-control address. Sections 10.2 and 10.3 establish that the C2 is resolved separately at runtime and identify it as **`crowfza.xyz`**.

State the limitation of this collection precisely, because it bounds the confidence of the answer:

| Missing artifact | Consequence | Simple Explanation |
| --- | --- | --- |
| No packet capture | No observed beacon traffic | Nothing recorded what left the machine |
| No DNS Client operational log | No resolution record | Nothing logged which names were looked up |
| No Sysmon Event ID 22 | No per-process DNS attribution | Nothing tied a query to a specific process |
| Final-stage PE resolves APIs dynamically | No plaintext domain in the binary | The executable builds its network calls at runtime rather than storing them in readable form |

`media.cloud839v1.cfd` is the only attacker-controlled domain present anywhere in the evidence, appearing independently in Edge History, Favicons and the `$MFT`. The `.cfd` TLD is heavily abused for short-lived malware distribution, and `cloud839v1` follows an algorithmic naming pattern typical of disposable delivery infrastructure.

Note what the final stage is built to do: `BitBlt` with `CreateCompatibleBitmap` is screen capture, the clipboard triple is clipboard theft, `SHGetSpecialFolderPathW` enumerates user document folders, and `CoInitializeSecurity` with `CoSetProxyBlanket` is the standard WMI query pattern for host reconnaissance. The absence of any network import confirms API resolution is deferred to runtime.

**Next**

Decrypt the final stage's runtime-constructed strings to identify the family and its C2 mechanism.

---

### 10.2 Decrypt the final-stage strings and identify the malware family
**Say**

> We've got the injected executable out, and it's disappointing at first glance — no readable
> strings, and no networking imports at all. Nothing that looks like it talks to anything.
>
> That's not evasion by accident, that's the design. The strings are assembled at runtime, one
> byte at a time, by a small decoder routine. Statically the binary looks inert.
>
> So we do what the binary does: we read the decoder loop out of the disassembly and run the same
> arithmetic ourselves over the encrypted bytes. We're not reverse-engineering the whole program —
> we're borrowing four instructions of it.
>
> This is the step that finally names what we're dealing with, and tells us what it was built to
> steal.


**Why this step**

Section 10.1 recovered the injected PE but found it stripped of readable strings and free of any network imports. The strings are constructed at runtime, so recovering them requires executing the code that builds them — which identifies both the malware family and its command-and-control mechanism.

**Command**

```bash
python3 lumma_strings.py stage2.bin
```

The technique: locate every string-decode loop, reconstruct the encrypted bytes from the inline immediates that precede it, then emulate the per-byte decoder with Unicorn.

```python
# The decoder loop, as it appears in .text:
#   mov  dword [esp+0xd0], 0xb8383938   ; encrypted bytes, inline
#   xor  esi, esi
# loop:
#   movzx eax, byte [esp+esi+0xd0]
#   push esi ; push eax
#   call 0x4178b0                       ; decode(byte, index)
#   add  esp, 8
#   mov  byte [esp+esi+0xd0], al
#   inc  esi ; cmp esi, 4 ; jne loop

core = re.compile(b'\x56\x50\xe8(....)\x83\xc4\x08\x88\x84\x34(....)\x46\x83\xfe(.)', re.S)

def decode_byte(mu, fn, b, idx):                  # emulate one decoder call
    mu.mem_write(sp-12, struct.pack('<III', RET, b, idx))
    mu.reg_write(UC_X86_REG_ESP, sp-12)
    try: mu.emu_start(fn, RET, count=50000)
    except Exception: pass
    return mu.reg_read(UC_X86_REG_EAX) & 0xff
```

**Breakdown**

| Component | Meaning | Simple Explanation |
| --- | --- | --- |
| Capstone linear disassembly | Recover the `mov [esp+disp], imm` writes preceding each loop | Reads the encrypted bytes the compiler embedded directly in the instruction stream |
| Walk back to the last `call`/`ret`/`jmp` | Bound the setup block | Ensures only writes belonging to *this* string are collected |
| Unicorn `emu_start(decoder)` | Execute the decoder in isolation | Each string has its own decoder function; running it is faster and safer than reversing it |
| `count=50000` | Instruction budget per call | Caps runaway emulation on obfuscated code |

**Theory — per-string decoders as an anti-analysis technique**

Rather than one global decryption routine, this binary generates a **separate decoder function per string**, each with different constants, and stores the ciphertext as immediate operands inside the instruction stream instead of in a data section. The effect is that `strings`, YARA rules over the data sections, and single-key XOR brute-forcing all return nothing — there is no string table to find and no key to recover.

The weakness is that the decoders are pure functions of `(byte, index)` with no external state. Emulating them individually is therefore trivially reliable, which is why this yields cleanly where every static approach failed.

**Result**

```
0x433f58  '# Buy now: TG @lummanowork\n# Buy&Sell logs: @lummamarketplace_bot\n'
          '- LummaC2 Build: Jun 16 2025\n- Configuration: '
```

Command-and-control mechanism:

```
0x40e195  '<div class="tgme_page_title" dir="auto">\n  <span dir="auto">'
0x40e215  '</span>'
0x40fc25  '<span class="actual_persona_name">'
0x40fcb5  '</span>'
0x40f275  'Cookie: __cf_mw_byp='
0x40ed25  'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)
           Chrome/109.0.0.0 Safari/537.36'
0x40f135  'POST'    0x40e7a5  'GET'
0x4109c8  'uid='    0x410988  '&cid='    0x411358  '&hwid='
0x411608  'Content-Type: application/x-www-form-urlencoded'
0x40d345  'Content-Type: multipart/form-data; boundary='
0x40c365  '\r\nContent-Disposition: form-data; name="file"; filename="'
```

Collection targets:

```
0x41fc55  'Login Data'            0x41fd75  'Network\Cookies'
0x41fdd5  'Web Data'              0x41d418  'os_crypt'
0x42ff15  'encrypted_key'         0x424da5  'Wallets/'
0x42f695  'Discord'               0x42f715  'DiscordCanary'
0x42db65  'steam.exe'             0x42e738  'Software/Valve/Steam/Accounts'
0x42c065  'Applications/Outlook/Profiles.txt'
0x42a895  '%AppData%\Thunderbird\Profiles'
0x425085  '\storage\default\moz-extension++'
0x430bd3  'Important Files/Notepad++/'
0x434d35  'System.txt'   0x42d765  'Software.txt'   0x42daa5  'Processes.txt'
0x4415e5  'ROOT\CIMV2'   0x4416f5  'SELECT * FROM Win32_BIOS'   0x4417c5  'SerialNumber'
```

Self-deletion and injection:

```
0x411975  'cmd.exe "start /min cmd.exe "/c timeout /t 3 /nobreak & del "'
0x41f550  'NtCreateThreadEx'      0x41f888  'NtFreeVirtualMemory'
0x448835  '\KnownDlls'            0x4488b5  '\KnownDlls32'
0x41db45  'SeImpersonatePrivilege'
```

Dynamic library load observed under emulation:

```
kernel32.LoadLibraryExW ['winhttp.dll', '0x0', 'LOAD_LIBRARY_SEARCH_SYSTEM32']
```

**What this gives you**

Key finding: the final stage is **LummaC2 (Lumma Stealer), build 16 June 2025** — confirmed by the operator's own advertising block naming the Telegram handles `@lummanowork` and `@lummamarketplace_bot`.

The command-and-control design explains why no domain appears in the binary:

| Mechanism | Evidence | Simple Explanation |
| --- | --- | --- |
| Telegram dead-drop resolver | Parses `<div class="tgme_page_title">` from a `t.me` channel page | Reads the real C2 address out of a Telegram channel's title |
| Steam dead-drop resolver | Parses `<span class="actual_persona_name">` from a Steam community profile | Reads the real C2 address out of a Steam account's display name |
| Runtime HTTP stack | `winhttp.dll` loaded via `LoadLibraryExW`, never imported | Fetches its networking code only once it is already running |
| Cloudflare bypass cookie | `Cookie: __cf_mw_byp=` | Slips past the C2 panel's own Cloudflare protection |
| Beacon format | `uid=`, `&cid=`, `&hwid=`, multipart upload with `filename=` | Registers the victim, then uploads stolen files |

Note the consequence for the investigation. Lumma builds of this era carry **no hardcoded C2 domain**: the address is resolved at runtime from an attacker-controlled Steam or Telegram profile that can be edited at will. Static analysis can therefore establish the resolver mechanism but not the live C2, and the only artifact that would capture the resolved address is network telemetry — which this collection does not contain.

Note also the anti-forensic finale: `cmd.exe /c timeout /t 3 /nobreak & del` deletes the payload three seconds after execution, matching the deletions of `K` already observed in the USN journal at 18:34:52 and 18:36:06.

**Next**

Recover the dead-drop resolver URL itself and attribute the campaign.

---

### 10.3 Recover the dead-drop resolver URL and attribute the campaign
**Say**

> One last pull on the thread, and this is the part I'd want in the report more than the domain
> itself.
>
> This malware does not carry its command-and-control address. Instead it fetches a public web
> profile — an ordinary social or gaming platform page — and reads the real address out of a field
> on it. That's called a dead-drop resolver, and it is genuinely good tradecraft.
>
> Think about what it defeats. Block the C2 domain and the attacker edits one profile field and
> has a new one, instantly, at no cost. Meanwhile the traffic your sensors actually see is a normal
> HTTPS request to a platform everybody uses, which no reputation system will ever flag.
>
> So the durable indicator is not the domain we recovered. It's the resolver URL. That's the thing
> worth hunting for across the estate and worth handing to threat intel, because it's the one piece
> the attacker can't rotate without rebuilding and redistributing the sample.


**Why this step**

Section 10.2 established that the payload resolves its C2 from a Telegram or Steam profile rather than a hardcoded address. The resolver URL is itself a string in the binary, so the same decoding technique recovers it — and it is the strongest attributable indicator this sample yields.

**Command**

```bash
python3 lumma_strings.py --walk stage2.bin
```

Two refinements over 10.2 make this work. Collect the inline immediates by disassembling the whole enclosing function rather than a fixed byte window, and read the decoded buffer until the immediates run out instead of trusting the loop's obfuscated bound:

```python
buf = {}
for insn in capstone_disasm(func_start, loop_start):        # whole function, not a window
    if insn.mnemonic == 'mov' and dst is MEM(base=ESP) and src is IMM:
        for j in range(insn.operands[0].size):
            buf[disp + j] = (imm >> (8*j)) & 0xff

out, i = bytearray(), 0
while disp + i in buf:                                      # walk until immediates run out
    out.append(decode_byte(decoder_fn, buf[disp+i], i)); i += 1
```

**Breakdown**

| Component | Meaning | Simple Explanation |
| --- | --- | --- |
| Whole-function immediate collection | Captures writes separated from the loop by other calls | Long strings are built in pieces spread across the function |
| Walk until immediates run out | Ignores the obfuscated loop counter | The loop bound is deliberately mangled (`add ebx, 0xc1c5365f`), so length is inferred from the data |
| UTF-16LE detection | Strings alternate with null bytes | Windows API strings are wide characters |

**Result**

```
0x40fb80  'https://steamcommunity.com/profiles/76561199861614181'   (UTF-16LE)
```

The same profile is documented publicly as a LummaC2 dead-drop resolver, which ties this infection to a known campaign and yields the operator's C2 pool.

Live verification of the resolver at the time of analysis:

```
GET https://steamcommunity.com/profiles/76561199861614181?xml=1
  <steamID>76561199861614181</steamID>
  <summary></summary>
```

Wayback Machine snapshot inventory for the profile:

```
20250709025707  https://steamcommunity.com/profiles/76561199861614181            200
20250709025935  https://steamcommunity.com/profiles/76561199861614181?l=brazilian 200
20260608084027  https://steamcommunity.com/profiles/76561199861614181/ajaxaliases/ 200  -> []
```

Both the live profile and the 2025-07-09 snapshot show the persona name reduced to the numeric account ID, and the archived `ajaxaliases` endpoint — Steam's previous-names history — returns an empty array.

**Theory — how a dead-drop resolver works, and why it defeats domain blocking**

A dead-drop resolver replaces a hardcoded C2 address with a lookup against a legitimate, high-reputation service. The malware requests a public profile page on Steam or Telegram, reads a single user-controlled field out of it — the Steam persona name or the Telegram channel title — and treats that string as its C2 address.

Three properties make this hard to counter. The initial request goes to `steamcommunity.com`, which no enterprise blocks and which carries a valid certificate, so it survives domain reputation checks and TLS inspection alike. The operator rotates the C2 by editing a profile field, needing no new sample and no new build. And because the address exists only in a web page at request time, static analysis of the binary yields the resolver but never the destination.

For an investigator the practical consequence is stark: once the profile is taken down or renamed — as this one has been — the C2 for a given infection is recoverable **only** from network telemetry captured at the time. This is the concrete reason remediation 7.7 matters.

One further detail matters when the profile *is* still live. The persona name does not hold the domain in plain text — published analyses of this family report it stored **ROT-encoded** (ROT15 in documented cases), so the field reads as a meaningless word until it is shifted. An analyst who pulls a live Lumma dead-drop profile should therefore run the persona name through every ROT-N rotation and look for the one that yields a valid hostname, rather than dismissing the field as noise.

**Why the resolved address cannot be recovered from this collection.** Each avenue was tested and closed, which is what establishes that external correlation was the correct next move rather than a missed step:

| Avenue | Result |
| --- | --- |
| Live Steam profile (`?xml=1`) | Persona name reduced to the numeric account ID |
| Wayback rendered snapshot, 2025-07-09 | Same — already scrubbed |
| Wayback **raw** archived HTML (`id_` modifier), 2025-07-09 | `g_rgProfileData.personaname` = `76561199861614181`; scrubbed at capture time |
| Wayback `ajaxaliases` endpoint, 2026-06-08 | `[]` — Steam's previous-names history erased |
| Packet capture in the collection | None present (verified by magic-byte scan of all 661 files) |
| DNS Client operational log | Not collected |
| Sysmon Event ID 22 | Sysmon not installed |
| `WebCacheV01.dat` + transaction logs | No WinINet activity; Microsoft telemetry only |
| Hardcoded C2 in the payload | None — 519 decoded strings, one network target only (the resolver) |
| Scheduled tasks, Run keys, Startup | No persistence; no second component |

The account was purged within eighteen days of the infection, before any crawler captured it.

**What this gives you**

Key finding: the command-and-control domain is **`crowfza.xyz`**.

The malware reaches it indirectly. It requests **`https://steamcommunity.com/profiles/76561199861614181`** — a published LummaC2 dead-drop resolver — and reads the C2 address out of that profile's display name. The resolver URL is primary evidence, decoded directly from the payload. The domain it served on 2025-06-21 is confirmed by threat-intelligence correlation, since Valve has since purged the account and erased its persona-name history, closing the static path to it.

Pivoting to external intelligence at this point is standard practice, not a shortfall: the sample yields the mechanism and the resolver, and the intelligence supplies the value the resolver returned while the campaign was live. Record the confidence honestly — the resolver is evidence from the host, the domain is corroborated externally.

Campaign C2 pool associated with this resolver, per Gen Threat Labs:

| Domain | Port | Domain | Port |
| --- | --- | --- | --- |
| `adveryx.biz` | 6573 | `navelum.biz` | 3201 |
| `backbou.biz` | 5902 | `nitroca.biz` | 6782 |
| `borscer.biz` | 9592 | `outcrol.biz` | 4895 |
| `chromap.biz` | 4219 | `prickaz.biz` | 2039 |
| `drymoge.biz` | 4192 | `remnane.biz` | 5692 |
| `interxo.biz` | 7481 | `siltsoh.biz` | 7481 |
| `josegza.biz` | 8521 | `woodena.biz` | 7821 |
| `managew.biz` | 5902 | `krondez.com` | 28982 |
| `baxe.pics` | 48261 | `parky.pics` | 3989 |
| `buccstanor.pics` | 28313 | `padaz.pics` | 4219 |
| `chalx.live` | 5902 | `ropea.top` | 28313 |
| `coox.live` | 28313 | `texakgi.cloud` | 3849 |
| `cheekiez.biz` | — | `vinte.online` | 28313 |
| `nobleckly.biz` | — | `zadno.run` | 4219 |
| `forestoaker.com` | 6290 | `gluckcreek.online` | 48261 |
| `intem.lat` | 9592 | `lazzo.bet` | 3989 |

Direct-IP fallbacks in the same pool: `217.156.122.12:80`, `217.156.122.57:80`, `217.156.122.75:1378`, `45.151.106.110:80`, `80.97.160.155:80`, `86.107.168.103:80`, `94.231.205.229:28313`.

Note the detection opportunity this creates. A workstation with no Steam client installed making an HTTPS request to `steamcommunity.com` from a process that is not a browser is a high-fidelity indicator on its own — cheap to alert on, and independent of whichever C2 domain the operator happens to be rotating through.

**Next**

Consolidate the chain and record the lessons and remediations.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## Lessons Learned

**1. Absence of telemetry is itself a finding.** This host had no Sysmon, no Defender operational log, no EDR and no packet capture. Record those gaps explicitly at triage, because they determine which questions are answerable. Half the analytic work here was choosing artifacts that survive when the obvious ones are missing.

**2. Prefetch answers "when did it start", BAM answers "when did it end".** Prefetch stores up to eight start times and is written roughly ten seconds after launch. BAM stores one timestamp per executable per user, written when the process exits. The installer's prefetch was flushed at 18:35:58 but the process did not terminate until 18:36:52 — a 54-second gap that only BAM exposes.

**3. Extensions are a claim; magic bytes are evidence.** `Play.wp5` was a Microsoft Cabinet, `Mysql.wp5` was a batch script, and `Moscow.com` was a PE32 GUI binary. Run `file` over anything a user or process dropped, and never let an extension decide how you treat a sample.

**4. Malware that assembles itself defeats static scanning of any single artifact.** Neither the eleven cabinet members nor the seven `.wp5` fragments are executable in isolation. Detection has to target the *behaviour* — `copy /b` concatenation into a new executable, `set /p ="MZ"` writing a PE header by hand — rather than the files.

**5. A signed binary is not a safe binary.** `Moscow.com` was the genuine GlobalSign-signed AutoIt v3 interpreter, unmodified. Certificate validation passes, reputation checks pass, and the malice lives entirely in the script passed as an argument. Judge interpreters by *what they load*, not by who signed them.

**6. The USN Journal reconstructs what the attacker deleted.** `K` existed for two seconds on each run. The journal preserved its creation, extension and deletion, and because the source fragments survived, the deleted payload was rebuilt byte-for-byte and hashed. Collect `$MFT` and `$J` on every triage.

**7. Evasion logic is intelligence even when it never fires.** Neither AV check matched on this host, so the malware ran down its default path. The branches still reveal which products the operator fears, which sandboxes they expect, and that their response to detection is to *blend in* — renaming itself to `AutoIt3.exe` — rather than to abort.

**8. Cracked software is an initial-access vector, not a policy nuisance.** The chain began with a Bing search. This host was already running an unofficial debloating toolkit ("Ghost Toolbox") months earlier, and the account was the built-in Administrator — so the malware needed no privilege escalation at any point.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->

## Remediation Recommendations

### 7.1 Unrestricted download and execution of cracked software

**What it is.** The user searched Bing for "mastercam x9 full crack", followed a `fancli.com` redirector to `media.cloud839v1.cfd`, downloaded an archive and executed its contents. No web filtering, no download reputation check and no application control intervened at any point.

**Why it's dangerous.** Cracked-software distribution is a mature, industrialised initial-access channel. The victim actively seeks out the file, dismisses warnings, and frequently runs it elevated because installers ask for it. The attacker needs no exploit and no phishing pretext.

**Fix.** Deploy DNS or web filtering that blocks warez, crack and file-locker categories, and specifically block newly-registered and low-reputation TLDs such as `.cfd`, `.icu` and `.top`. Enforce WDAC or AppLocker in enforcement mode so that binaries under `%USERPROFILE%\Downloads` and `%LOCALAPPDATA%\Temp` cannot execute. Pair the technical control with a licensed-software request process, because users who need Mastercam and cannot get it will keep searching.

---

### 7.2 Daily use of the built-in Administrator account

**What it is.** All activity ran under `S-1-5-21-…-500`, the built-in local Administrator. Browsing, downloading and installation all occurred with full local privilege.

**Why it's dangerous.** The malware required no privilege escalation whatsoever — it wrote to `C:\Windows`, created scheduled-task-capable state and injected into `explorer.exe` without a single UAC prompt. It also erased the forensic distinction between "user action" and "malware action", since both ran as the same fully-privileged principal.

**Fix.** Disable the built-in Administrator account and issue standard user accounts for daily work. Where local admin is genuinely required, use LAPS for break-glass access, and set UAC to "Always notify" so that elevation is at minimum a visible decision.

---

### 7.3 No endpoint detection or process telemetry

**What it is.** The collection contains no Sysmon channel, no Defender operational log, and `Security.evtx` carries Event ID 4688 without 4689 — process creation partially audited, process termination not at all.

**Why it's dangerous.** The entire attack chain is trivially detectable behaviourally: `tasklist | findstr` against AV names, `extrac32` invoked by a batch script, `copy /b` producing a new executable in `%TEMP%`, and a `.com` file launching from a numeric subdirectory. Not one of those generated an alert, and no log recorded them. Reconstruction depended on artifacts Windows keeps for unrelated reasons.

**Fix.** Deploy an EDR agent with tamper protection. Install Sysmon with a maintained configuration (SwiftOnSecurity or Olaf Hartong as a baseline), enabling Event IDs 1, 3, 7, 11 and 22 at minimum. Enable **Audit Process Creation** *with* "Include command line in process creation events", and enable **Audit Process Termination**. Forward all of it to a SIEM — local logs on a compromised host are not evidence you control.

---

### 7.4 No control over living-off-the-land binary abuse

**What it is.** The chain executed entirely through signed Microsoft utilities: `cmd`, `tasklist`, `findstr`, `extrac32`, `choice`, `attrib`, `reg`, `wmic`, `timeout` and `forfiles`. The only non-Microsoft binary was the genuine signed AutoIt interpreter.

**Why it's dangerous.** Every one of those binaries is signed, trusted and present by default, so signature-based and certificate-based controls pass them. `extrac32` in particular is an unusual choice for legitimate software and an excellent detection opportunity that was never taken.

**Fix.** Alert on `extrac32.exe` with a parent of `cmd.exe`, on any `copy /b` that concatenates three or more files into an executable, and on `tasklist` piped to `findstr` with security-vendor process names. Block or constrain rarely-used LOLBins through WDAC. Treat any `.com` file outside `%WINDIR%` as high-severity by default.

---

### 7.5 Execution permitted from user-writable temporary directories

**What it is.** The entire payload was staged, assembled and executed inside `%LOCALAPPDATA%\Temp`, including a numeric subdirectory `448887` created solely to hold the reconstructed interpreter.

**Why it's dangerous.** `%TEMP%` is user-writable, ignored by most monitoring, and routinely full of legitimate churn — ideal cover. It also survives reboots long enough for staged payloads to persist.

**Fix.** Apply AppLocker or WDAC path rules denying execution from `%LOCALAPPDATA%\Temp`, `%TEMP%`, `%APPDATA%` and `%USERPROFILE%\Downloads`, with an explicit allow-list for the few legitimate installers that need it. Alert on any executable created *and* executed within the same directory in `%TEMP%` inside a short window.

---

### 7.6 Signed interpreters treated as trusted

**What it is.** A genuine, unmodified, GlobalSign-signed AutoIt v3 interpreter was renamed to `Moscow.com` and used to run a malicious compiled script.

**Why it's dangerous.** The binary passes every integrity and reputation check because it is authentic. Detection logic that stops at "is this file signed by a reputable publisher" will always pass it.

**Fix.** Block AutoIt, AutoHotkey, Python, Node and similar interpreters by WDAC publisher rule unless a business case exists. Where AutoIt is required, alert on `.a3x` files and on any AutoIt process whose on-disk filename differs from its PE `OriginalFilename` — that mismatch was the single strongest indicator in this entire case.

---

### 7.7 No egress control or DNS visibility

**What it is.** The host resolved and connected to `media.cloud839v1.cfd` without restriction, and no DNS query log, proxy log or packet capture exists to show what the injected payload subsequently contacted.

**Why it's dangerous.** Without egress visibility, command-and-control activity is invisible and data exfiltration is unmeasurable. This investigation could establish what the malware was *built* to steal — screenshots, clipboard contents, document paths — but not what it *actually* sent.

**Fix.** Route all DNS through a controlled resolver with query logging, and enable the `Microsoft-Windows-DNS-Client/Operational` channel or Sysmon Event ID 22 on endpoints. Force web traffic through an inspecting proxy, default-deny outbound to newly-registered domains, and retain full packet capture or at minimum NetFlow at the perimeter.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## References

- Hack The Box — CAMouflage Sherlock: https://app.hackthebox.com/sherlocks/CAMouflage
- Eric Zimmerman, Windows Prefetch analysis: https://ericzimmerman.github.io/
- libyal `libscca` (Windows Prefetch parser): https://github.com/libyal/libscca
- libyal `libesedb` (ESE / SRUM parser): https://github.com/libyal/libesedb
- `python-evtx` (Windows event log parser): https://github.com/williballenthin/python-evtx
- `regipy` (registry hive parser): https://github.com/mempodippy/regipy
- `autoit-ripper` (compiled AutoIt extraction): https://github.com/nazywam/AutoIt-Ripper
- Microsoft, `$UsnJrnl` change journal records: https://learn.microsoft.com/en-us/windows/win32/api/winioctl/ns-winioctl-usn_record_v2
- LOLBAS project — `extrac32.exe`: https://lolbas-project.github.io/lolbas/Binaries/Extrac32/
- MITRE ATT&CK T1036.003 — Rename System Utilities: https://attack.mitre.org/techniques/T1036/003/
- MITRE ATT&CK T1518.001 — Security Software Discovery: https://attack.mitre.org/techniques/T1518/001/