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

