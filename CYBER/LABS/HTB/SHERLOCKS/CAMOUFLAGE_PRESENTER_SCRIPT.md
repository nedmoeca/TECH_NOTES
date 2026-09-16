# CAMouflage — Presenter Script

**Session length:** 2 hours (110 min content + 10 min break)
**Audience:** beginners — assume they know what a file and a process are, and nothing else
**Companion doc:** `CAMOUFLAGE.md` (the full walkthrough — have it open in a second window)
**Evidence path used throughout:** `~/Labs/HTB/Sherlocks/CAMouflage/`

Everything marked **LIVE** is a command you type in front of them. Everything marked **SHOW** is output you paste on screen from `CAMOUFLAGE.md` — do not try to reproduce it live, it needs scripts and will eat your clock.

---

## PRE-FLIGHT — run this 10 minutes before you go on

Paste this whole block. Every line must print `OK`. If any line fails, that step becomes a **SHOW** instead of a **LIVE**.

```bash
cd ~/Labs/HTB/Sherlocks/CAMouflage

T="evidence/C/Users/Administrator/AppData/Local/Temp"
P="evidence/C/Windows/prefetch"

[ -d "$T" ] && echo "OK evidence tree" || echo "FAIL evidence tree"
which sccainfo >/dev/null && echo "OK sccainfo" || echo "FAIL sccainfo (sudo apt install -y libscca-utils)"
ls "$P/DOWNLOAD MASTERCAM X9 FULL CR-C7EFFD46.pf" >/dev/null 2>&1 && echo "OK installer prefetch" || echo "FAIL installer prefetch"
ls "$T/Mysql.wp5" "$T/Play.wp5" "$T/448887/Moscow.com" >/dev/null 2>&1 && echo "OK dropped files" || echo "FAIL dropped files"
python3 -c "import regipy" 2>/dev/null && echo "OK regipy" || echo "FAIL regipy (pip install regipy --break-system-packages) -- Task 2 becomes SHOW"
```

Then rehearse these three, which are the ones that can embarrass you live:

```bash
sccainfo "$P/DOWNLOAD MASTERCAM X9 FULL CR-C7EFFD46.pf" | head -14
file "$T"/*.wp5 "$T/448887/Moscow.com"
cd "$T" && cat Runner.wp5 Art.wp5 Gba.wp5 Romania.wp5 Refugees.wp5 Authorization.wp5 Lock.wp5 > /tmp/K && sha256sum /tmp/K && cd ~/Labs/HTB/Sherlocks/CAMouflage
```

The last one must print `2b3d1561b9ae7fa2bd3f09dee28a327b5647a908113945cd2a943134822d18d0`. If it prints anything else, your fragment order is wrong — check it against the batch line in Section 5.1.

**Terminal setup:** font size up to at least 18pt. Dark background. Clear your scrollback (`clear`) between sections so nobody is reading old output while you talk.

**Have ready in browser tabs:** the HTB task page (all 10 green), `CAMOUFLAGE.md`, and nothing else. Close Slack.

---

## RUNNING ORDER

| Time | Section | Task |
| --- | --- | --- |
| 0:00 | Open — the hook | — |
| 0:07 | What we were given | — |
| 0:17 | When did it run | 1 |
| 0:32 | When did it stop — the detour | 2 |
| 0:47 | What it dropped | 3, 4 |
| 1:00 | **BREAK** | — |
| 1:10 | The batch script | 5, 6 |
| 1:30 | Building a program out of nothing | 7, 8 |
| 1:45 | The payload | 9 |
| 1:55 | Who was on the other end | 10 |
| 2:05 | Close — 5 lessons | — |

If you are running late, cut in this order: the Amcache aside (0:40), the volume-serial aside (0:28), the ATT&CK table (2:05). Never cut Section 5 or 7 — they are the heart of it.

---

## 0:00 — OPEN (7 min)

Do not introduce yourself for three minutes. Start with the story.

> **SAY:** "On the 21st of June last year, someone sat down at their work laptop and searched Bing for a cracked copy of Mastercam. Mastercam is CAD software for machine tools — it costs thousands of pounds. They found a free one. They downloaded it, they double-clicked it, and forty seconds later their machine was running a credential stealer that was taking screenshots and reading their clipboard.
>
> No exploit. No phishing email. No zero-day. They just wanted free software.
>
> Over the next two hours I'm going to show you exactly how that happened, step by step, using only the files that were left behind on that laptop. And the reason this one is worth your time is this: **at no point did a complete piece of malware ever sit on that disk where an antivirus scanner could find it.** It built itself, at the moment it ran, out of pieces that were individually harmless."

Pause. Then:

> **SAY:** "Two things before we start. First, everything I show you, you can do yourself with free tools on Linux — there's no expensive forensics suite here. Second, I want you to stop me. If I use a word you don't know, say so. Half the people in this room have never opened a prefetch file and that's completely fine — that's what this is for."

> **SAY:** "Here's the shape of the whole thing, so you always know where we are."

Draw or show this. Keep it on screen whenever you can.

```
User downloads crack  →  installer runs  →  drops 9 disguised files
                                                   ↓
                                          batch script runs
                                                   ↓
                               checks for antivirus  →  unpacks archive
                                                   ↓
                              glues 11 pieces into a program
                                                   ↓
                              glues 7 more into a script
                                                   ↓
                              runs the program, deletes the script
                                                   ↓
                                         steals, phones home
```

> **SAY:** "Ten questions. We'll answer them in order, and each one teaches a different artifact."

---

## 0:07 — WHAT WE WERE GIVEN (10 min)

> **SAY:** "We didn't get the laptop. We got a triage collection — a zip file. Let's open it."

**LIVE:**
```bash
cd ~/Labs/HTB/Sherlocks/CAMouflage
ls
```

> **SAY:** "One password-protected zip. HTB uses the same password for every one of these — `hacktheblue`. Watch the flag carefully, because I got this wrong the first time."

**LIVE:**
```bash
7z x CAMouflage.zip -phacktheblue
```

> **SAY:** "`-p` and the password glued together, no space. If you type `-hacktheblue` it thinks the password is a command and refuses. Small thing, but you'll hit it."

**LIVE:**
```bash
7z x 2025-06-21T205150_output.zip -oevidence
```

Point at the `Comment` line in the output.

> **SAY:** "There. *Created by KAPE version 1.3.0.2.* KAPE is a triage tool. Instead of copying the whole 500-gigabyte disk, it grabs a curated set of high-value files — the ones forensic analysts actually use — and it keeps them at the paths they came from. 663 files. That's our entire world for the next two hours."

**LIVE:**
```bash
find evidence/C -maxdepth 4 -type d | sort
```

> **SAY:** "Read this like a menu. Each folder is a capability."

Take these three slowly. Do not rush — this is the vocabulary for the whole session.

> **SAY:** "`Windows/prefetch` — Windows keeps a little cache file for every program you run, to make it start faster next time. It's a performance feature. It's also, completely by accident, a log of everything that has ever executed on this machine.
>
> `$Extend` — that's where the USN Journal lives. NTFS keeps a running diary of every file created, written, renamed or deleted, with timestamps down to the millisecond. Including files the attacker deleted afterwards.
>
> `System32/config` — the registry. We'll come back to this one, and it's going to save us."

> **SAY:** "But notice what that command did — I asked it for directories only. The single biggest piece of evidence in this collection isn't a folder at all. It's a file sitting at the root."

**LIVE:**
```bash
ls -la evidence/C/
```

> **SAY:** "There it is. **`$MFT`** — the Master File Table. 103 megabytes of it.
>
> This is the index card catalogue of the entire disk. One record per file, holding its name, its parent folder, and its timestamps — created, modified, accessed. Every NTFS volume has one, and it is the backbone of filesystem forensics.
>
> Underneath it, `$LogFile` at 64 megabytes — NTFS's transaction log, for crash recovery. And `$Extend`, the folder I just mentioned, which holds `$J` — the journal itself."

> **SAY:** "Worth saying plainly, because it catches everyone out: files whose names start with a dollar sign are NTFS's own internal metadata. They are invisible in Explorer, and you cannot even copy them while Windows is running — the operating system holds them locked. KAPE takes them with a low-level raw read. That is exactly why it is the tool for this job, and why you can't do this with copy and paste."

> **SAY:** "Keep these two straight, because we use both today and they answer different questions.
>
> The **`$MFT`** is a *snapshot* — which files exist right now, and what their timestamps are.
>
> The **USN Journal** is a *diary* — what happened to files, in what order, including files that no longer exist. That second one is how we are going to recover something the malware deleted."

> **SAY:** "Now — one detail that decides how the whole rest of the investigation goes."

**LIVE:**
```bash
ls evidence/C/Users/
```

> **SAY:** "One real user: `Administrator`. And if you look at the SID — the long number that identifies the account — it ends in `-500`. In Windows, `-500` means the built-in Administrator account. The one with full control of the machine.
>
> So this person was browsing the internet, as Administrator, on a machine where they install cracked software. The malware never had to escalate privileges. It never even triggered a UAC prompt. It had everything from the first second."

---

## 0:17 — TASK 1: WHEN DID IT RUN (15 min)

> **SAY:** "First question: *at what precise timestamp did the user first execute the cracked installer?* Precise. So we need an artifact that records execution to the second. That's Prefetch."

**LIVE:**
```bash
ls evidence/C/Windows/prefetch/ | wc -l
ls evidence/C/Windows/prefetch/ | head -40
```

> **SAY:** "178 files. Each one is named after a program, then a hyphen, then eight hex characters. That hex is a hash of the folder the program ran from — which is why you see fifteen different `SVCHOST.EXE` entries. Same program, different paths."

Now scroll to the M's and stop.

> **SAY:** "There it is. `DOWNLOAD MASTERCAM X9 FULL CR-C7EFFD46.pf`. Notice it's cut off after `CR` — Prefetch truncates the name at 29 characters. So we don't actually know the full filename yet. Let's open the file properly."

> **SAY:** "The standard tool for this is PECmd, which is a Windows program. We're on Linux, and modern Windows compresses these files, so a naive parser sees garbage. `libscca` handles the decompression natively and it's one apt command."

**LIVE:**
```bash
sccainfo "evidence/C/Windows/prefetch/DOWNLOAD MASTERCAM X9 FULL CR-C7EFFD46.pf" | head -14
```

Stop talking. Let them read it.

> **SAY:** "Three things matter here. **Run count: 2.** It ran twice. And two timestamps:
>
> `Last run time 1` — 18:35:47
> `Last run time 2` — 18:34:19
>
> Now — which one is the answer?"

**ASK the room. Wait for someone to say it. Let them get it wrong first if they do.**

> **SAY:** "Entry 1 is the *most recent*, not the oldest. Newest first. So the first execution is entry 2: **2025-06-21 18:34:19 UTC**. That's Task 1.
>
> But here's the part that matters more than the answer. Prefetch only keeps **eight** timestamps. If this program had run thirty times, the oldest one you can see is just the eighth-most-recent — and it would be completely wrong as an answer to 'when did it first run'. It's only safe here *because* the run count is 2. Always check the run count before you trust the oldest timestamp. That's a real mistake people make in real cases."

> **SAY:** "Now scroll down, because Prefetch tells us something else. Windows watches the first ten seconds of a program's life and records every file it touches."

**LIVE:**
```bash
sccainfo "evidence/C/Windows/prefetch/DOWNLOAD MASTERCAM X9 FULL CR-C7EFFD46.pf" | grep -iE "downloads|temp|cmd.exe" | head -15
```

> **SAY:** "Look at what this 'installer' touched in its first ten seconds.
>
> Its full name — `C:\Users\Administrator\Downloads\DOWNLOAD MASTERCAM X9 FULL CRACK PC.EXE`. That's the untruncated name we were missing.
>
> Then nine files in the Temp folder ending in `.wp5`. Called `MYSQL`, `AUTHORIZATION`, `LOCK`, `ART`, `ROMANIA`, `PLAY`, `REFUGEES`, `RUNNER`, `GBA`. Those names have nothing to do with each other and nothing to do with CAD software.
>
> And `cmd.exe`. A command prompt.
>
> An installer that opens a command prompt and scatters nine randomly-named files into your temp folder is not installing anything."

---

## 0:32 — TASK 2: WHEN DID IT STOP (15 min)

This is the best teaching moment in the session. Play the dead end honestly — do not skip to the answer.

> **SAY:** "Task 2: *when did the installer process terminate?* Sounds easy. It isn't, and the reason it isn't is the most useful thing I'll teach you today.
>
> Go back to that Prefetch output in your head. Was there a field anywhere that said when it *stopped*?"

**ASK. Wait.**

> **SAY:** "No. Prefetch records starts. Only starts. So we need something else. The obvious place is the Windows event logs."

**LIVE:**
```bash
ls -la evidence/C/Windows/System32/winevt/logs/ | head -25
```

> **SAY:** "Before we open anything — two columns tell you most of what you need.
>
> **Size.** An empty Windows event log is exactly 69,632 bytes. One 64K chunk plus a header. Anything sitting at exactly that number has nothing in it.
>
> **Date.** Our incident is 21 June. Anything last written in January was written when the machine was built and never touched again.
>
> Filter on those two and this list collapses from a hundred files to about a dozen."

> **SAY:** "Now, the thing I was hoping for was Sysmon. Sysmon is a free Microsoft tool that logs process creation, process *termination*, network connections, DNS queries, with hashes. It would answer half our questions by itself."

**LIVE:**
```bash
ls evidence/C/Windows/System32/winevt/logs/ | grep -i -E "sysmon|defender"
```

> **SAY:** "Nothing. No Sysmon. No Windows Defender log either.
>
> That absence *is* a finding. This machine had no endpoint detection of any kind. Which — remember this — is exactly the state the malware was about to check for.
>
> OK, fall back to the built-in Security log. Windows can audit process creation and termination itself."

**SHOW** (from `CAMOUFLAGE.md` §2.1 — running the parser live takes too long):

```
     84 5379      45 4688      20 4798
     70 4624      27 4799      20 4781
     60 4672      49 4735      19 5061
```

> **SAY:** "Event ID **4688** is process creation — 45 of them. Good. Event ID **4689** is process *termination* — and it isn't in the list at all. Auditing was half-enabled.
>
> And it gets worse. All 45 of those 4688 events are from January, at boot. There is not a single event in *any* log on this machine between 18:34 and 18:40 on the day of the incident.
>
> So: no Sysmon, no 4689, no event logs at all in our window. The obvious sources are gone. This is what real cases feel like."

Pause here. Let it land.

> **SAY:** "So where do you go? You go somewhere nobody thinks about: **BAM**. The Background Activity Moderator.
>
> BAM is a *power management* feature. It arrived in Windows 10 to throttle background apps and save battery. To do that, it keeps a list in the registry of every program each user has run, with one timestamp each.
>
> And here's why that matters — BAM writes its timestamp when the process **ends**. Prefetch stamps the start; BAM stamps the finish. A battery-saving feature is the only thing on this machine that recorded a process exit."

**LIVE** (if regipy passed pre-flight — otherwise **SHOW** from §2.3):
```bash
python3 - <<'EOF'
from regipy.registry import RegistryHive
import struct, datetime, binascii
h = RegistryHive('evidence/C/Windows/System32/config/SYSTEM')
k = h.get_key('\\ControlSet001\\Services\\bam\\State\\UserSettings')
for sk in k.iter_subkeys():
    for v in sk.get_values():
        try:
            b = binascii.unhexlify(v.value.replace(' ',''))
            ts = struct.unpack_from('<Q', b, 0)[0]
            t = datetime.datetime(1601,1,1) + datetime.timedelta(microseconds=ts//10)
            if t.year == 2025 and t.month == 6:
                print(t, v.name)
        except Exception: pass
EOF
```

> **SAY:** "And there it is:
>
> `2025-06-21 18:36:52` — `...\Downloads\download mastercam x9 full crack pc.exe`
>
> That's Task 2.
>
> Now compare it to what Prefetch told us. It *started* at 18:34:19. It *ended* at 18:36:52. Two and a half minutes. It was sitting there the whole time, alive, while its child processes did the work. Prefetch would never have told you that."

*(Cut if short on time:)* Also visible in that output: `Ghost Toolbox\toolbox.updater.x64.exe` from January. This machine was already running an unofficial Windows-debloating toolkit five months before the incident. The risk posture was bad long before this.

---

## 0:47 — TASKS 3 & 4: WHAT IT DROPPED (13 min)

> **SAY:** "Task 3: *what was the first file dropped by the malware?* We saw the names in Prefetch. Now let's look at the actual files."

**LIVE:**
```bash
cd evidence/C/Users/Administrator/AppData/Local/Temp
ls -la
```

> **SAY:** "Nine `.wp5` files. Plus a folder called `448887`. And a pile of other odd names — `Hell`, `Balls`, `Theology`, `Thanksgiving`, `Subsequently`. Hold that thought.
>
> `.wp5` is the WordPerfect 5 file extension. Nobody has used WordPerfect 5 since about 1992. That's *deliberate* — an extension nothing on Windows will preview, nothing will open, and a lot of scanning policies skip.
>
> So let's ignore the extension entirely and ask what these files actually *are*."

**LIVE:**
```bash
file *.wp5 448887/*
```

> **SAY:** "This is the single most important habit I can give you today. **The extension is a claim. The first few bytes are evidence.** The `file` command reads the content.
>
> `Mysql.wp5` — ASCII text. It's a script.
> `Play.wp5` — a **Microsoft Cabinet archive**. Eleven files inside it. That's a zip file wearing a WordPerfect costume.
> The other seven — just `data`. Unrecognisable. Hold that thought too.
> And `448887/Moscow.com` — a Windows executable."

> **SAY:** "For the exact ordering of the drop we go to the USN Journal — the filesystem's diary. Millisecond precision."

**SHOW** (from §2.2):
```
18:34:25.511  Mysql.wp5          FILE_CREATE   <-- first
18:34:25.527  Authorization.wp5  FILE_CREATE
18:34:25.558  Art.wp5 / Lock.wp5 FILE_CREATE
18:34:25.574  Play.wp5 / Romania.wp5
18:34:25.621  Refugees.wp5
18:34:25.699  Runner.wp5
18:34:25.746  Gba.wp5
```

> **SAY:** "All nine inside a quarter of a second. First one out: **`Mysql.wp5`** — the script. Task 3. It drops the instructions first, then everything the instructions will need."

> **SAY:** "Task 4 wants a fingerprint of the Cabinet archive."

**LIVE:**
```bash
sha256sum Play.wp5
```

> **SAY:** "`35efc15a...`. Task 4.
>
> A SHA-256 is a fingerprint — change one byte of the file and the whole thing changes completely. It's what you hand to your SOC to block this thing everywhere, and what you paste into threat intelligence to see if anyone else has met it.
>
> And one detail from the `file` output worth catching: the archive was **built on 20 June** — the day before it landed here. This wasn't generated for this victim. It was packaged in advance and sprayed."

---

## 1:00 — BREAK (10 min)

> **SAY:** "Ten minutes. When we come back we open the script, and that's where it gets fun."

Use the break to: `clear`, `cd ~/Labs/HTB/Sherlocks/CAMouflage`, and open §5.1 of `CAMOUFLAGE.md` ready to paste.

---

## 1:10 — TASKS 5 & 6: THE SCRIPT (20 min)

> **SAY:** "This is the brain of the whole operation. Let's look at it."

**LIVE:**
```bash
cd evidence/C/Users/Administrator/AppData/Local/Temp
head -20 Mysql.wp5
```

> **SAY:** "Right. That's what obfuscation looks like.
>
> 422 lines of this. Lines like `mvwSphere(Arising(` — that's not a command, that's garbage. When `cmd.exe` hits a line it can't parse, it prints an error and carries on to the next line. So the attacker padded the file with hundreds of junk lines that do nothing, to bury about forty real ones.
>
> But look at the lines that *do* make sense."

**LIVE:**
```bash
grep -E "^Set [A-Za-z]+=" Mysql.wp5 | head -12
```

> **SAY:** "`Set Ten=5`. `Set Ballet=X`. `Set Adventures=n`. Every variable holds **one single character**, and it's named after a random English word.
>
> So when the script wants to run `findstr`, it doesn't write `findstr`. It writes:
>
> `%Washington%i%Adventures%%Climate%str`
>
> Washington is `f`, Adventures is `n`, Climate is `d`. f-i-n-d-str. The word `findstr` never appears in the file. Any antivirus looking for suspicious command names sees nothing."

> **SAY:** "To undo it, we build a dictionary of every variable and substitute them back. About fifteen lines of Python."

**SHOW** the deobfuscated result (from §5.1). Put this on screen and leave it up — you'll refer to it for the next twenty minutes.

```
327: tasklist | findstr /I "opssvc wrsa" & if not errorlevel 1 ping -n 192 127.0.0.1
338: tasklist | findstr "bdservicehost SophosHealth AvastUI AVGUI nsWscSvc ekrn"
       & if not errorlevel 1 Set ...=AutoIt3.exe & Set ...=.a3x & Set ...=300
344: md 448887
354: extrac32 /Y Play.wp5 *.*
360: set /p ="MZ" > 448887\Moscow.com <nul
363: findstr /V "Surplus" Balls >> 448887\Moscow.com
367: copy /b 448887\Moscow.com + Hell + Analyze + Theology + Thanksgiving
       + Subsequently + Mechanisms + Dawn + Draws + Appreciated + Investors
       448887\Moscow.com
374: cd 448887
384: copy /b ..\Runner.wp5 + ..\Art.wp5 + ..\Gba.wp5 + ..\Romania.wp5
       + ..\Refugees.wp5 + ..\Authorization.wp5 + ..\Lock.wp5 K
387: start Moscow.com K
413: choice /d n /t 5
```

> **SAY:** "Forty lines. That's the entire attack.
>
> Task 5 asks how it unpacked the Cabinet. Line 354: **`extrac32 /Y Play.wp5 *.*`**.
>
> `extrac32` is a Microsoft program. It's been in `System32` since Windows 95. It's digitally signed by Microsoft, it's trusted, it's on every machine on the planet. `/Y` means don't ask me any questions, `*.*` means extract everything.
>
> This is what we call a **living-off-the-land binary**. The attacker didn't bring an unzip tool — that would be a suspicious file on disk. They used Microsoft's own."

> **SAY:** "Now Task 6 — the antivirus checks. Lines 327 and 338."

Point at line 327.

> **SAY:** "`tasklist` lists every running process. The pipe sends that list to `findstr`, which searches it. It's searching for `opssvc` and `wrsa` — those are Quick Heal and Webroot.
>
> And if it finds one? `ping -n 192 127.0.0.1`. It pings itself 192 times. That's about three minutes of doing nothing.
>
> Why?"

**ASK. Wait for it.**

> **SAY:** "Because automated malware sandboxes give a sample about two minutes before they give up and call it clean. It's literally waiting them out."

Point at line 338.

> **SAY:** "Second check. Six more: Bitdefender, Sophos, Avast, AVG, Norton, ESET.
>
> And if it finds one of *those*, look what it does. It doesn't quit. It changes its own name. `Moscow.com` becomes `AutoIt3.exe`, and the file extension becomes `.a3x`, and the wait goes from 5 seconds to 300.
>
> It disguises itself *better* when it detects that someone is watching. That's not a bug, that's design."

> **SAY:** "Count the second check. `bdservicehost`, `SophosHealth`, `AvastUI`, `AVGUI`, `nsWscSvc`, `ekrn`. **Six.** That's Task 6.
>
> Be precise about what we're counting, because someone will ask. The first check adds two more — Quick Heal and Webroot — and the payload itself checks for Avast a second time, so there are nine security-product checks across the whole chain. But the question asks about the AV/EDR product strings, and that's the six in the check that actually decides the malware's behaviour. Six is the answer."

> **SAY:** "And here's the punchline: on this machine, neither check matched. No antivirus was running. It sailed straight down the default path. All that evasion logic was never needed."

---

## 1:30 — TASKS 7 & 8: BUILDING A PROGRAM FROM NOTHING (15 min)

This is the showstopper. Slow down.

> **SAY:** "I want you to look at lines 360 to 367 and tell me what's happening."

Read them out loud, one at a time.

> **SAY:** "`set /p ="MZ" > 448887\Moscow.com`
>
> That writes two letters — M and Z — into a new file. Nothing else.
>
> Why M and Z? Because every Windows executable starts with those two bytes. It's the signature Windows looks for. `MZ` are the initials of Mark Zbikowski, the Microsoft engineer who designed the format in 1981. It's been there for forty years.
>
> So the attacker just **typed the first two bytes of a Windows program by hand.**"

> **SAY:** "Next line — `findstr /V "Surplus" Balls >> Moscow.com`. Remember `Balls` from the temp folder? `/V` means *exclude*. So: take the file `Balls`, throw away the line containing the word `Surplus`, and append everything else. That marker line was there to stop the file being a valid program on its own.
>
> Then — `copy /b` with ten more files chained together with plus signs. `/b` means binary mode. Glue them all onto the end."

Pause.

> **SAY:** "Do you see what that means?
>
> Every antivirus in the world works, at some level, by looking at files. But until that last `copy` command finishes, **the malicious program does not exist**. There are eleven meaningless fragments and a two-byte file. Scan any one of them and you get nothing, because there's nothing there to find.
>
> This is the single idea the whole box is built around."

> **SAY:** "Then line 387: `start Moscow.com K`. It runs the thing it just assembled. That's Task 7 — **`Moscow.com`**."

> **SAY:** "Now — why `.com`?"

**ASK.**

> **SAY:** "`.com` is a leftover from MS-DOS. Windows still treats it as executable for compatibility, but the loader doesn't care about the extension at all — it reads the file header. So a normal Windows program called `x.com` runs exactly as it would called `x.exe`.
>
> Two things that buys you. Detection rules written around `*.exe` miss it completely. And an analyst scanning a process list reads `.com` and thinks 'legacy' — or worse, thinks it's a web address."

> **SAY:** "Task 8 asks what this program really is. Windows executables carry a version resource — the data you see on the Details tab when you right-click a file. It's baked in at compile time and *renaming the file doesn't change it*."

**LIVE:**
```bash
strings -el 448887/Moscow.com | grep -iE "autoit" | head -8
```

> **SAY:** "Note the `-el` flag — that's for 16-bit text. Windows stores these strings as wide characters, so a plain `strings` misses them entirely. That trips people up constantly.
>
> And there's the answer: **`AutoIt3.exe`**. AutoIt is a legitimate scripting tool for Windows automation — IT departments use it. This is the real, genuine, Microsoft-compatible AutoIt interpreter."

**LIVE:**
```bash
strings 448887/Moscow.com | grep -i "globalsign\|autoitscript" | head -4
```

> **SAY:** "And look — it's digitally signed by GlobalSign, and it references autoitscript.com. This file is **not** trojanised. It has not been modified. It is the authentic signed AutoIt interpreter, renamed to `Moscow.com`.
>
> So every check passes. Signature? Valid. Publisher? Reputable. File hash against known-good? Matches. It is exactly what it claims to be.
>
> The malice isn't in the program. It's in the *script you hand it*."

---

## 1:45 — TASK 9: THE PAYLOAD (10 min)

> **SAY:** "Which brings us to that script. Line 387 again — `start Moscow.com K`. `K` is the argument. `K` is what the interpreter runs. So what is `K`?"

**LIVE:**
```bash
ls 448887/
```

> **SAY:** "It's not there. Because of this, from the USN Journal:
>
> `18:34:50.684  K  FILE_CREATE`
> `18:34:52.980  K  FILE_DELETE`
>
> It existed for **two point three seconds**, then deleted itself.
>
> So how do we get it back?"

**ASK. Let someone work it out — the answer is on screen in front of them, line 384.**

> **SAY:** "Line 384. `copy /b` of seven `.wp5` files. Those seven files are still sitting in the temp folder. `copy /b` is just concatenation — no headers, no padding. So if we glue them together in the same order, on any operating system, we get a byte-for-byte identical file."

**LIVE:**
```bash
cat Runner.wp5 Art.wp5 Gba.wp5 Romania.wp5 Refugees.wp5 Authorization.wp5 Lock.wp5 > /tmp/K
ls -l /tmp/K
sha256sum /tmp/K
```

> **SAY:** "**`2b3d1561b9ae...`** — Task 9. We just reconstructed a file the malware deleted, from the pieces it forgot to clean up. That's forensics."

> **SAY:** "Order matters, by the way. Swap any two of those and you get a different file and a wrong hash. We got the order from the batch script — which is why deobfuscating it first was worth the effort."

**LIVE:**
```bash
strings -n 8 /tmp/K | head -1
```

> **SAY:** "`AU3!EA06`. That's the magic marker for a **compiled** AutoIt script. The source has been converted to bytecode, compressed and encrypted. That's why those seven fragments looked like meaningless `data` to the `file` command — they *are* meaningless. It's ciphertext until the interpreter decrypts it in memory."

---

## 1:55 — TASK 10: WHO WAS ON THE OTHER END (10 min)

> **SAY:** "Last question. What did it talk to?
>
> The answer is **`crowfza.xyz`**. But the answer is the least interesting part of this section — *how it gets there* is one of the cleverest things in modern malware, and it's the bit I actually want you to remember."

> **SAY:** "First, what are we even dealing with? I unpacked that compiled AutoIt script. Inside it was an encrypted Windows program, which it decrypts in memory and injects into `explorer.exe` — so it never appears as a process of its own in Task Manager.
>
> That program had no readable text in it at all. Every string is assembled at runtime by its own little decoder routine. I had to emulate those decoders to read anything. When I did, the very first thing that came out was this."

**SHOW:**
```
# Buy now: TG @lummanowork
# Buy&Sell logs: @lummamarketplace_bot
- LummaC2 Build: Jun 16 2025
```

> **SAY:** "That's the malware advertising itself — the authors left their own sales pitch in the binary.
>
> This is **LummaC2**, Lumma Stealer. One of the largest credential stealers in the world. The FBI and Europol ran a takedown against it in May 2025. This build is dated the 16th of June — three weeks after the takedown. They rebuilt and carried on. And our victim ran it five days later."

> **SAY:** "Here's what it's built to take."

**SHOW:**
```
Login Data      Network\Cookies     Web Data      os_crypt / encrypted_key
Wallets/        Discord             steam.exe     Outlook / Thunderbird profiles
BitBlt          OpenClipboard       GetClipboardData
```

> **SAY:** "Browser passwords and cookies, and the key that decrypts them. Crypto wallets. Discord tokens. Steam sessions. Email profiles. Plus screen capture and clipboard reading.
>
> Then it removes itself — `cmd.exe /c timeout /t 3 /nobreak & del`. Three seconds after it's done, gone. That's the same deletion the USN Journal caught at 18:34:52."

> **SAY:** "Now — the clever bit. There is no C2 domain anywhere in that binary. Not stored, not encrypted, not hidden. It genuinely isn't there. What *is* there is this, and I decoded it straight out of the payload."

**SHOW:**
```
https://steamcommunity.com/profiles/76561199861614181
```

> **SAY:** "A Steam profile.
>
> This is called a **dead-drop resolver**. The malware doesn't carry its C2 address — it goes and *looks it up*. It fetches that public Steam profile page, reads the account's **display name**, and that display name is the C2 address, scrambled with a simple letter shift so it reads as a nonsense word to anyone glancing at it."

Pause. Let that sink in before you explain why it matters.

> **SAY:** "Think about what that buys the attacker. Three things.
>
> One — the first connection goes to `steamcommunity.com`. Nobody blocks Steam. Valid certificate, huge reputation, looks like a gamer's laptop.
>
> Two — when a C2 domain gets burned, the attacker edits a Steam profile. No new malware. No new build. Every existing infection on every victim machine follows them to the new address within minutes.
>
> Three — because the address only exists in a web page at the moment of the request, you cannot get it by analysing the file. You can only get it by watching the traffic, or by catching the profile while it's live."

> **SAY:** "So we know the mechanism with certainty — that URL is primary evidence, decoded from the sample. For the value it returned, we pivot to threat intelligence, which is completely normal practice: this Steam profile is publicly documented as a LummaC2 dead drop, and the domain it was serving in this campaign is **`crowfza.xyz`**.
>
> I did go and check the profile myself. Valve has purged the account — the display name now just shows the account number. The archived copy from three weeks after our infection already shows it wiped, and Steam's own name-history endpoint comes back empty. So that address is confirmed from intelligence rather than pulled from the disk, and in a real report you write that distinction down. Mechanism: host evidence. Domain: corroborated externally. Both go in, with their confidence labelled."

> **SAY:** "And this is where the investigation hands you your most important recommendation. We can prove exactly what this malware was **built** to steal. We cannot prove from this laptop what it actually **sent**, because nothing on that machine was recording DNS queries or network traffic.
>
> That's not a limitation of forensics. That's a gap in their monitoring — and it's the first thing on my remediation list."

## 2:05 — CLOSE (7 min)

> **SAY:** "Five things to take away."

Say these slowly, one at a time. This is the bit they'll remember.

> **1. Absence of evidence is evidence.** No Sysmon, no Defender, no packet capture. Those absences shaped the entire investigation, and they are a finding to report in their own right — not a footnote.
>
> **2. Prefetch tells you when something started. BAM tells you when it stopped.** Two and a half minutes apart in this case. Know both.
>
> **3. The extension is a claim; the magic bytes are evidence.** A WordPerfect document that's actually a Cabinet archive. Run `file` on everything.
>
> **4. A signed binary is not a safe binary.** That AutoIt interpreter was genuine, unmodified and correctly signed. Judge an interpreter by what you hand it, not by who signed it.
>
> **5. Malware that assembles itself at runtime defeats file scanning by design.** You can't catch this with hashes. You catch it with behaviour — a batch script that runs `extrac32`, a `copy /b` that builds an executable in the temp folder, a `.com` file launching from a numeric directory.

> **SAY:** "And if you take one single detection rule away from this: **a machine with no Steam client installed, making an HTTPS request to steamcommunity.com from something that isn't a browser.** That catches this whole family, and it keeps working no matter how many times they rotate the domain."

> **SAY:** "Full writeup with every command and every output is in the document. Questions."

---

## Q&A — PREPARED ANSWERS

**"Why couldn't antivirus catch this?"**
Because for most of the chain there was nothing to catch. The pieces are meaningless fragments; the only complete executable is a legitimately signed Microsoft-compatible interpreter. The malicious thing exists for two seconds in a file that deletes itself. Behavioural detection catches this; file scanning doesn't.

**"Would it have worked on a standard user account?"**
Mostly yes — everything happened in the user's own temp folder, which any user can write to. Being Administrator meant no UAC prompt and no friction, but it wasn't required.

**"How do I know the reconstruction is right?"**
Two independent checks. The reassembled file starts with `AU3!EA06`, the correct magic for a compiled AutoIt script — random bytes wouldn't produce that. And HTB accepted the hash.

**"What's the difference between `$MFT` and the USN Journal?"**
The `$MFT` is a snapshot: what files exist right now, and their timestamps. The USN Journal is a diary: what *happened* to files, in order, including ones that no longer exist. You want both — the journal for sequence, the MFT for detail.

**"Could you get the C2 if you had the machine?"**
If you had memory, yes — the domain is in RAM once the payload resolves it. If you had DNS logs or a packet capture, trivially. From disk alone, no.

**"What's ROT / a letter shift?"**
Shift every letter forward by a fixed number. ROT15 turns A into P. It's not encryption, it's a disguise — enough that the Steam display name looks like a nonsense word instead of a web address.

**"Why does an installer ship a WordPerfect file?"**
It doesn't. That's the whole point — the extension is chosen precisely because nothing on Windows handles it, so nothing opens it, previews it or looks inside.

---

## IF YOU LOSE YOUR PLACE

The one-line version of the chain, in order:

**crack → installer → 9 disguised files → batch script → AV check → extrac32 unpacks 11 more → copy /b builds AutoIt3.exe renamed Moscow.com → copy /b builds the script K → runs it → K deletes itself → Lumma injects into explorer.exe → reads its C2 off a Steam profile.**

