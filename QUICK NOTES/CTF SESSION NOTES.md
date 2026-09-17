
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
