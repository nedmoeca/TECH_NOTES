---
title: CAMouflage — Live Run Script
purpose: Presenter script. Follow top to bottom. Every command is self-contained.
companion: CAMOUFLAGE.md (full writeup) · CAMOUFLAGE_TOOLS/ (helper scripts)
---

# CAMouflage — Live Run Script

> **How to use this.** Read the **SAY** aloud. Paste the **RUN**. When output appears, read the
> **POINT OUT**. `EXPECT` tells you what success looks like so you know instantly if something
> went wrong; `IF IT FAILS` is your recovery line so you never stall in silence.
>
> Every command uses `$EV` and `$TMPD` instead of relying on your current directory. There is no
> `cd` anywhere in the run. Steps cannot break each other.

---

## PRE-FLIGHT — do all of this BEFORE the audience is in the room

### P1. Copy the helper scripts to Kali

The three parsers live in `CAMOUFLAGE_TOOLS/` next to this file. Get them onto the Kali box, into
your CAMouflage working directory, then:

```bash
chmod +x usnparse.py deobf.py bam.py
```

### P2. Install dependencies

```bash
sudo apt install -y libscca-utils
pip install regipy autoit-ripper --break-system-packages
```

> `--break-system-packages` is mandatory on current Kali. Without it pip refuses under PEP 668
> and you get an `externally-managed-environment` error mid-demo.

### P3. Arm the path variables

```bash
# Move into the CAMouflage case folder. Everything below is relative to this,
# so if this line fails, nothing after it will work.
cd ~/Labs/HTB/Sherlocks/CAMouflage

# EV = EVidence root. $PWD expands to the folder we just moved into, so EV becomes an
# ABSOLUTE path. That is the whole point: absolute means no command in the run depends
# on where you happen to be standing when you paste it.
export EV="$PWD/evidence/C"

# TMPD = the victim's TeMP Directory, where the malware staged all nine .wp5 files.
# Built from $EV so it inherits the absolute path. Used in sections 3, 4, 5, 8 and 9.
export TMPD="$EV/Users/Administrator/AppData/Local/Temp"

# PF = PreFetch folder, Windows' execution record. Used in sections 1 and 7.
export PF="$EV/Windows/prefetch"

# Verify. ${EV:-UNSET} prints the value, or the literal word UNSET if the variable is
# empty - so a silent failure becomes visible instead of producing broken paths later.
# Then test that $EV actually exists: ls into /dev/null (we want the exit code, not the
# listing), 2>&1 discards the error text, && prints OK on success, || prints BROKEN.
echo "EV=${EV:-UNSET}"; ls "$EV" >/dev/null 2>&1 && echo "PATHS OK" || echo "PATHS BROKEN"
```

**EXPECT:** `EV=/home/nedmoeca/Labs/HTB/Sherlocks/CAMouflage/evidence/C` followed by `PATHS OK`.

> **Two ways this bites you.** First, the variables live in one shell only — open a new terminal
> or tab and you must re-run this whole block or every later command breaks. Second, copy this
> from the RAW markdown, not a rendered preview: some viewers strip the `$` from `$PWD` and `$EV`,
> which produces a relative path like `PWD/evidence/C` that fails silently until the first command
> that needs it.

### P4. Smoke-test every moving part

```bash
python3 usnparse.py "$EV/\$Extend/\$J" | head -3
python3 bam.py "$EV/Windows/System32/config/SYSTEM" 2>&1 | tail -3
sccainfo "$PF/DOWNLOAD MASTERCAM X9 FULL CR-C7EFFD46.pf" | head -5
python3 -c "import autoit_ripper; print('autoit_ripper ok')"
```

All four must produce output. **Do not walk on stage until they do.** If `bam.py` reports
`BAM key not found`, the hive path is wrong — check P3.

### P5. Terminal hygiene

Font size up. Clear scrollback. Dark theme. Close every other tab. Widen the window — the USN
output is long lines and wrapping makes it unreadable from the back of a room.

---

## RUNNING ORDER

| § | Covers | Time | Skippable? |
| --- | --- | --- | --- |
| 0 | Scoping the collection | 2 min | No — sets up everything |
| 1 | Task 1 — first execution | 3 min | No |
| 2 | Task 2 — termination | 5 min | No — best teaching moment |
| 3 | Task 3 — first dropped file | 3 min | No |
| 4 | Task 4 — CAB hash | 1 min | Yes, if short |
| 5 | Task 5 — deobfuscation | 4 min | No — the centrepiece |
| 6 | Task 6 — AV checks | 2 min | Yes, if short |
| 7 | Task 7 — the launched process | 2 min | No |
| 8 | Task 8 — original filename | 3 min | No — biggest reaction |
| 9 | Task 9 — rebuilding a deleted file | 3 min | No — second biggest |
| 10 | Task 10 — C2 | 4 min | Trim to 10.1 only if short |

**Total: ~32 minutes** at a comfortable pace. Cutting §4 and §6 brings it to ~29.

---

## § 0 — What were we given?

**SAY**

> Before we answer anything, we need to know what we're holding. This is not a disk image. It's a
> triage collection — a tool called KAPE walked the live machine and copied out a curated set of
> artifacts, and left everything else behind. What's in here decides which questions we can answer,
> and just as importantly, which ones we can't.

**RUN**

```bash
find "$EV" -maxdepth 4 -type d | sed "s|$EV|C:|" | sort
```

**BREAKDOWN**

| Part | What it does |
| --- | --- |
| `find "$EV"` | Walk the collection from the mirrored `C:\` root |
| `-maxdepth 4` | Stop four levels down — deeper than that and we'd list all 663 files instead of the structure |
| `-type d` | Folders only. We want the shape, not the contents |
| `sed "s\|$EV\|C:\|"` | Rewrite the long Linux prefix as `C:` so the audience reads it as the victim's drive |
| `sort` | Alphabetical, so related paths group together and read like a tree |

**EXPECT:** ~38 directory lines, starting `C:` and `C:/$Extend`.

**POINT OUT**

> Three things. `$Extend` — that's the USN Journal, the filesystem's own change log, and it's
> going to carry this entire investigation. `System32/config` — the registry hives. And look at
> the user profiles: there's exactly one that matters, and it's called Administrator.
>
> Now the absences, which matter more. No memory capture. No packet capture. No DNS cache. So
> when we get to the command-and-control question at the end, we already know the answer cannot
> come from network evidence. It has to come out of the malware itself.

---

## § 1 — Task 1: when did the installer first run?

**SAY**

> Prefetch is Windows trying to be helpful and accidentally becoming a witness. Its job is to
> cache what a program needs so it starts faster next time. The side effect is a record that the
> program ran, when, and how many times. Nobody enabled it — which is exactly why it's still here
> on a host with no EDR. There was nothing for the attacker to switch off.

**RUN**

```bash
ls "$PF" | wc -l
ls "$PF" | grep -iE "mastercam|moscow|extrac32|findstr|tasklist|choice|cmd\.exe"
```

**BREAKDOWN**

| Part | What it does |
| --- | --- |
| `ls "$PF"` | List every Prefetch file — one per program that ever ran |
| `wc -l` | Count them, so we lead with the scale before the detail |
| `grep -iE "mastercam\|moscow\|..."` | Filter to the interesting ones. `-i` ignores case, `-E` enables the `\|` alternation |

**EXPECT:** a count of 178, then a short list including `DOWNLOAD MASTERCAM X9 FULL CR-C7EFFD46.pf`
and `MOSCOW.COM-34B22CCB.pf`.

**POINT OUT**

> 178 programs ran on this machine. I've filtered to the interesting ones. Notice what's in that
> list besides the installer: `extrac32`, `findstr`, `tasklist`, `choice`, `cmd`. Those are all
> signed Microsoft utilities that ship with Windows. Malware borrows them so it never has to bring
> its own tools . simply living off the land, and seeing them clustered together is the
> signature of a batch-driven infection.
>
> And the installer's name is cut off. Prefetch truncates at 29 characters. Let's open the file.

**SAY**

> The usual tool here is Eric Zimmerman's PECmd, which is Windows-only. We're on Linux, and modern
> Windows compresses these files, so a naive parser sees compressed bytes and gives up quietly.
> `libscca` handles that natively.

**RUN**

```bash
sccainfo "$PF/DOWNLOAD MASTERCAM X9 FULL CR-C7EFFD46.pf" | grep -iE "filename|run count|run time"
```

**BREAKDOWN**

| Part | What it does |
| --- | --- |
| `sccainfo` | The libscca Prefetch parser — decompresses the file and prints every field |
| `"..."` quoted | Mandatory. The filename contains spaces; unquoted, bash splits it into four arguments |
| `grep -iE "filename\|run count\|run time"` | Cut ~40 lines of noise down to the three fields that answer the question |

**EXPECT:** the full executable name, `Run count: 2`, and two run times — `18:34:19` and `18:35:47`.

**POINT OUT**

> There's the full name. And look — **run count of two**. It ran twice, about ninety seconds apart.
>
> That's the trap in this question. It asks for the *first* execution. If you grab the most recent
> timestamp, which is the one most tools show you by default, you get the wrong answer and you have
> no idea you're wrong.

> ### ✅ TASK 1 — `2025-06-21 18:34:19`

---

## § 2 — Task 2: when did it terminate?

**SAY**

> Process termination is exactly the sort of thing Windows is supposed to write down. So let's go
> and look at the event logs. I'll tell you now — this is a dead end. But it's a *documented* dead
> end, and in a real engagement proving an artifact isn't there is a finding in itself.
>
> Here's the trick: we're not going to open a single log file. You can triage an entire event-log
> directory on two columns. A freshly initialised log is exactly 69,632 bytes — one chunk plus a
> header. Anything still sitting at that number is empty, whatever its name promises.

**RUN**

```bash
ls -la "$EV/Windows/System32/winevt/logs/" | awk '$5>69632 {print $5, $9}' | sort -rn | head -8
ls "$EV/Windows/System32/winevt/logs/" | grep -ci sysmon
```

**BREAKDOWN**

| Part | What it does |
| --- | --- |
| `ls -la` | Long listing — we need the size column, field 5 |
| `awk '$5>69632 {print $5, $9}'` | Keep only logs larger than an empty one. 69,632 bytes is a fresh log: one 64 KB chunk plus a header |
| `sort -rn` | Numeric sort, biggest first — the fullest logs are the interesting ones |
| `head -8` | Top eight only |
| `grep -ci sysmon` | Count Sysmon logs, case-insensitive. `-c` gives a number, and the number we expect is zero |

**EXPECT:** a handful of populated logs, then **`0`** for the Sysmon count.

**POINT OUT**

> Zero Sysmon logs. No process creation, no process termination, no command lines, no hashes.
> Everything Sysmon would have handed us, we now have to reconstruct by hand.

**SAY**

> So we drop a layer — to the filesystem itself. NTFS keeps a change journal. Every file created,
> written, renamed or deleted gets a record: what changed, what kind of change, and when, to
> sub-millisecond precision. It exists so backup software doesn't have to rescan the disk. Nobody
> turned it on. On a host with no security tooling it's the closest thing we have to a process
> monitor.

**RUN**

```bash
python3 usnparse.py "$EV/\$Extend/\$J" 2>/dev/null \
  | awk '$1=="2025-06-21" && $2>"18:34:15" && $2<"18:36:10"' | head -40
```

**BREAKDOWN**

| Part | What it does |
| --- | --- |
| `usnparse.py "$EV/\$Extend/\$J"` | Parse the NTFS change journal. `\$` is escaped — unescaped, bash expands `$Extend` to nothing |
| `2>/dev/null` | Send the record count to the bin so it doesn't interleave with the results |
| `awk '$1=="2025-06-21"'` | Field 1 is the date — keep only the incident day |
| `$2>"18:34:15" && $2<"18:36:10"` | Field 2 is the time. String comparison works because the format is zero-padded |
| `head -40` | First forty records — the staging burst |

**EXPECT:** `nsv52EF.tmp` created and deleted at `18:34:22`, then `Mysql.wp5` at
`18:34:25.511586`, `Authorization.wp5` at `18:34:25.527547`, and the rest of the `.wp5` set.

**POINT OUT**

> Look at the very first line — `nsv52EF.tmp`, created and deleted three seconds before anything
> else. That `nsv` prefix is the signature of an NSIS installer unpacking itself. So before we've
> looked at the payload we already know what built this thing.
>
> Then the malware stages itself. Nine files, all with the same extension, written within a
> second of each other. Then a batch file. Then, ninety seconds later, the whole thing happens
> again — that's the second run we saw in Prefetch.
>
> But notice what's missing. The journal records what happens to *files*. It has nothing to say
> about processes. It will not tell us when the installer died.

**SAY**

> Last option, and it's obscure, which is why I like it. Windows has a component called the
> Background Activity Moderator. Its real job is power management — it throttles background apps
> to save battery, and to do that it records what each user has been running. That record sits in
> the SYSTEM registry hive. Nobody built it as a forensic artifact. It's a side effect of battery
> optimisation, and it's one of the most reliable execution records on Windows precisely because
> no attacker thinks to clear it.

**RUN**

```bash
python3 bam.py "$EV/Windows/System32/config/SYSTEM" mastercam
```

**BREAKDOWN**

| Part | What it does |
| --- | --- |
| `bam.py` | Reads the Background Activity Moderator key straight out of the raw hive, using regipy |
| `.../config/SYSTEM` | The SYSTEM registry hive as KAPE collected it — no mounting, no Windows needed |
| `mastercam` | Optional filter. Without it you get every executable BAM ever recorded; with it, just ours |

**EXPECT:** one line, `2025-06-21 18:36:52`, with the SID and the full NT device path.

**POINT OUT**

> 18:36:52. And notice the path format — `\Device\HarddiskVolume3\`, not `C:\`. That's the raw
> NT namespace, which is a small tell that you're reading something Windows never intended you
> to see.

> ### ✅ TASK 2 — `2025-06-21 18:36:52`

**IF IT FAILS:** `BAM key not found` means `$EV` is unset or wrong — re-run PRE-FLIGHT P3.

---

## § 3 — Task 3: the first file dropped

**SAY**

> Now, the box's name. Every file the malware dropped carries the same extension — and it's a real
> extension, it belongs to an old word processor. Not one of these files has anything to do with
> word processing. So rather than trust the extension, we type every file by its actual content.

**RUN**

```bash
file "$TMPD"/*.wp5 | sed "s|$TMPD/||"
```

**BREAKDOWN**

| Part | What it does |
| --- | --- |
| `file` | Identifies each file by its magic bytes — its actual content — not by its extension |
| `"$TMPD"/*.wp5` | Every staged file in the malware's temp directory |
| `sed "s\|$TMPD/\|\|"` | Strip the long path prefix so the filenames line up on screen |

**EXPECT:** a mix — one ASCII text, one `Microsoft Cabinet archive`, one `MS-DOS executable`, and
several reported simply as `data`.

**POINT OUT**

> Same extension, completely different file types. One's a script. One's a cabinet archive. One's
> an executable. And several are just "data" — not a valid file of any kind. Hold that thought,
> because those meaningless ones are the key to this whole box.

**RUN**

```bash
python3 usnparse.py "$EV/\$Extend/\$J" 2>/dev/null \
  | awk '$1=="2025-06-21" && /wp5/ && /FILE_CREATE/' | sort -k2 | head -5
```

**BREAKDOWN**

| Part | What it does |
| --- | --- |
| `/wp5/` | Regex match anywhere on the line — keeps only the staged payload files |
| `/FILE_CREATE/` | And only the creation events, not the writes and closes that follow |
| `sort -k2` | Sort on field 2, the timestamp — this is what orders them to the millisecond |
| `head -5` | The first five. The top line is the answer |

**EXPECT:** `Mysql.wp5 | FILE_CREATE` at `18:34:25.511586` on top, `Authorization.wp5` 16 ms later.

**POINT OUT**

> That journal holds 133,568 records. We just filtered it to five.
>
> Ordered to the millisecond. Mysql.wp5 lands first — and that's the orchestrator, the script
> that drives everything else.

> ### ✅ TASK 3 — `Mysql.wp5`

---

## § 4 — Task 4: hash the cabinet  *(skippable)*

**SAY**

> Quick one. We identified a Microsoft Cabinet archive by content. Hashing turns that observation
> into something usable — an indicator you can push to an EDR blocklist or hand to threat intel.
> "I saw a suspicious cab file" helps nobody. A SHA-256 is portable proof.

**RUN**

```bash
sha256sum "$TMPD/Play.wp5"
```

**BREAKDOWN**

| Part | What it does |
| --- | --- |
| `sha256sum` | Cryptographic fingerprint of the file's exact bytes |
| `"$TMPD/Play.wp5"` | Hashed in place, as collected — never a copy you extracted and repacked, which changes the bytes |

**EXPECT:** `35efc15a41cf54a51703711e0b117b1899e4698bed1a4fdae638ebb7a3a190e0`

> ### ✅ TASK 4 — `35efc15a41cf54a51703711e0b117b1899e4698bed1a4fdae638ebb7a3a190e0`

---

## § 5 — Task 5: read the orchestrator

**SAY**

> This is the centre of the box. Everything before was timeline work; everything after comes out
> of this one file.
>
> The batch script is deliberately unreadable, and the obfuscation isn't clever — it's character
> level variable substitution. The author defines a pile of variables holding one or two characters
> each, then builds every real command out of them. So a command like `extrac32` never appears as
> those eight letters anywhere in the file. Anything grepping for suspicious command names sees
> nothing.

**RUN**

```bash
head -c 400 "$TMPD/Mysql.wp5"; echo
```

**BREAKDOWN**

| Part | What it does |
| --- | --- |
| `head -c 400` | First 400 *characters*, not lines — this file has enormous single lines |
| `; echo` | Adds a newline, so the next prompt doesn't land mid-line |

**POINT OUT**

> That's what the defender sees. Unreadable. Now watch.

**RUN**

```bash
python3 deobf.py "$TMPD/Mysql.wp5" > deobfuscated.txt
wc -l deobfuscated.txt
grep -iE "extrac32|copy /b|start " deobfuscated.txt
```

**BREAKDOWN**

| Part | What it does |
| --- | --- |
| `deobf.py` | Harvests every `set VAR=value` line, then substitutes `%VAR%` back through the script until nothing changes |
| `> deobfuscated.txt` | Save the resolved script — sections 6 and 7 both read this file |
| `wc -l` | Line count, so we can say how big the thing actually is |
| `grep -iE "extrac32\|copy /b\|start "` | Pull the three command types that matter: extraction, reassembly, execution |

**EXPECT:** the extraction command `extrac32 /Y Play.wp5 *.*`, several `copy /b` lines, and a
`start` line.

**POINT OUT**

> There it is. `extrac32` — a signed Microsoft utility for unpacking cabinet files, used here to
> unpack the malware's own payload. No custom unpacker, nothing to detect.
>
> And look at those `copy /b` lines. That's binary concatenation. The malware is gluing files
> together. Remember those meaningless "data" files? That's what they're for.

> ### ✅ TASK 5 — `extrac32 /Y Play.wp5 *.*`

**IF IT FAILS:** if `deobf.py` outputs nothing, the file has unusual line endings — run
`tr -d '\r' < "$TMPD/Mysql.wp5" > b.txt && python3 deobf.py b.txt > deobfuscated.txt`.

---

## § 6 — Task 6: the AV checks  *(skippable)*

**SAY**

> There's a trap in this question, and I want to walk into it deliberately. The script checks for
> security software in two separate places, and they don't contain the same number of product
> names.

**RUN**

```bash
grep -nE "tasklist" deobfuscated.txt
```

**BREAKDOWN**

| Part | What it does |
| --- | --- |
| `grep -n` | Show line numbers, so we can point at *where* in the script each check sits |
| `-E "tasklist"` | Find the process-listing calls — each one is piped into a string search for AV names |

**EXPECT:** two lines, one with 2 product strings, one with 6.

**POINT OUT**

> Two checks. Count every string anywhere in the file and you get eight. Count the strings in the
> check that actually decides what the malware does next — the one that branches — and you get six.
> That's the answer.
>
> And look *what* it checks for: Bitdefender, Sophos, Avast, AVG, Norton, ESET. Consumer antivirus,
> almost exclusively. Nobody targeting an enterprise writes a check for AvastUI. This is built for
> home machines running free AV — exactly the population that goes looking for cracked CAD software.
>
> The satisfying part: none of it fired. This host had no AV at all. All that evasion logic sat
> there, fully functional, and never ran once.

> ### ✅ TASK 6 — `6`

---

## § 7 — Task 7: what actually launched

**SAY**

> Neither check matched, so the script stayed on its default branch — and that branch finally
> launches something. I'm going to prove it two ways: the script says what it intends to run, and
> Prefetch proves something by that name actually executed. Two artifacts that know nothing about
> each other.

**RUN**

```bash
grep -iE "^ *[0-9]+ +start " deobfuscated.txt
sccainfo "$PF/MOSCOW.COM-34B22CCB.pf" | grep -iE "filename|run time" | head -3
```

**BREAKDOWN**

| Part | What it does |
| --- | --- |
| `grep -iE "^ *[0-9]+ +start "` | Anchored to line start, allowing for the line numbers our deobfuscator printed — finds the launch command only, not the word "start" in passing |
| `sccainfo .../MOSCOW.COM-...pf` | Independent confirmation from Prefetch that this really executed |
| `head -3` | Just the name and first run time |

**EXPECT:** a `start Moscow.com K` line, and Prefetch confirming `MOSCOW.COM` ran at `18:35:01`.

**POINT OUT**

> `Moscow.com`. Note the extension — `.com`, not `.exe`. It's ancient, it's perfectly legal,
> Windows still executes it, and it reads as harmless to a human skim and to a lot of tooling.
>
> And it's launched with an argument: `K`. Remember that. We'll come back for it.

> ### ✅ TASK 7 — `Moscow.com`

---

## § 8 — Task 8: what is this thing really?

**SAY**

> The name is meaningless. It's a city. It matches no product. So — what *is* this binary?
>
> Windows executables carry an embedded version resource: metadata the compiler writes in, holding
> the company, the product, and critically the original filename the developer built it under.
> Renaming the file on disk doesn't touch that. It survives.

**RUN**

```bash
strings -el "$TMPD/448887/Moscow.com" | grep -iE "originalfilename|autoit|productname|companyname" | head
```

**BREAKDOWN**

| Part | What it does |
| --- | --- |
| `strings` | Pull printable text out of a binary |
| `-el` | **The critical flag.** `-e l` means 16-bit little-endian text. Windows version resources are UTF-16, so plain `strings` misses them entirely — this is the flag people forget |
| `grep -iE "originalfilename\|autoit\|..."` | Filter to the version-resource fields that reveal the true identity |

**EXPECT:** `AutoIt3.exe`, plus AutoIt product and company strings.

**POINT OUT**

> Stop and sit with this, because it's the cleverest move in the whole sample.
>
> This is not malware. This is AutoIt3 — a legitimate, signed, publicly downloadable scripting
> interpreter from a real vendor. The attacker didn't write it, didn't modify it, didn't need to.
> They renamed it and shipped it with a script.
>
> Think about what that does to your defences. The binary is signed. Its hash is known-good. It's
> on every allowlist. Any control asking "is this executable trustworthy" answers yes — correctly.
> The malice isn't in the file. It's in the file it was pointed at.

> ### ✅ TASK 8 — `AutoIt3.exe`

---

## § 9 — Task 9: rebuild a file that no longer exists

**SAY**

> Task 9 wants the hash of the file the interpreter loaded — that argument `K` from earlier. And
> we have a problem: it doesn't exist. Look at the journal.

**RUN**

```bash
python3 usnparse.py "$EV/\$Extend/\$J" 2>/dev/null | awk '$1=="2025-06-21" && $4=="K"'
```

**BREAKDOWN**

| Part | What it does |
| --- | --- |
| `awk '$4=="K"'` | Field 4 is the filename in our output format. Fields 3 and 5 are the `\|` separators |
| exact match `=="K"` | Not a regex — `K` is one character and a loose match would catch every filename containing a K |

**EXPECT:** two full create/delete cycles — created `18:34:50.684170`, deleted `18:34:52.980466`;
then created again `18:36:05.496113`, deleted `18:36:06.105692`.

**POINT OUT**

> Created, used, deleted — two seconds. And then look: it happens *again* ninety seconds later.
> Built, run, destroyed. Built, run, destroyed. That's the second installer run we found back in
> Task 1, and this is what it was doing.
>
> Either way the file was gone two hours before KAPE ever ran.
>
> So we rebuild it. And we can, because of how it was made in the first place. This malware never
> shipped a complete payload. It shipped *pieces*, disguised with that harmless extension, and had
> Windows glue them together at runtime. Those pieces are still on disk — they survived precisely
> because individually they aren't malicious. They aren't even valid files.
>
> Two things have to be exactly right: the set of fragments, and their order. Get either wrong and
> you produce a different file with a different hash, and nothing tells you you're wrong. We're not
> guessing — the batch script told us both.

**RUN**

```bash
cat "$TMPD/Runner.wp5" "$TMPD/Art.wp5" "$TMPD/Gba.wp5" "$TMPD/Romania.wp5" \
    "$TMPD/Refugees.wp5" "$TMPD/Authorization.wp5" "$TMPD/Lock.wp5" > K
file K && sha256sum K
```

**BREAKDOWN**

| Part | What it does |
| --- | --- |
| `cat frag1 frag2 ... > K` | Binary concatenation in the exact order the batch script specified — this is `copy /b` in Linux form |
| order of arguments | Load-bearing. A different order produces a different file and a different hash, with no warning |
| `file K` | Confirm we've produced something structurally valid, not just glued bytes |
| `sha256sum K` | The proof. If the order were wrong, this would not match the known hash |

**EXPECT:** `K` identified as AutoIt-related data, hashing to
`2b3d1561b9ae7fa2bd3f09dee28a327b5647a908113945cd2a943134822d18d0`.

**POINT OUT**

> Seven fragments, in the order the script specified, and we've reconstructed a file that was
> deleted before the evidence was ever collected. That hash is now a hunting indicator.

> ### ✅ TASK 9 — `2b3d1561b9ae7fa2bd3f09dee28a327b5647a908113945cd2a943134822d18d0`

---

## § 10 — Task 10: the C2

**SAY**

> Last question, and it's several layers deep. Let me lay out the road first.
>
> We have a compiled AutoIt script — compiled, not source. So first we pull the source back out.
> That source is obfuscated: every meaningful string is built at runtime from a list of numbers,
> so there's no domain sitting in there to grep for. That's exactly why a plaintext string search
> fails on this box, and it's where a lot of people give up.

**RUN**

```bash
python3 -c "
from autoit_ripper import extract, AutoItVersion
data = open('K','rb').read()
for name, content in extract(data=data, version=AutoItVersion.EA05):
    open(name,'wb').write(content); print('extracted:', name, len(content), 'bytes')"
```

**BREAKDOWN**

| Part | What it does |
| --- | --- |
| `autoit_ripper.extract` | Unpacks a compiled AutoIt binary back into its embedded script |
| `AutoItVersion.EA05` | The compiled-script format marker. `EA05` is AutoIt v3 — the wrong version returns nothing rather than erroring |
| `open(name,'wb').write(content)` | Write each extracted member to disk under its original name |

**EXPECT:** one extracted `.au3` file.

**RUN**

```bash
ls *.au3 && head -c 600 *.au3; echo
grep -c "STORM" *.au3
```

**BREAKDOWN**

| Part | What it does |
| --- | --- |
| `head -c 600` | First 600 characters of the recovered source — enough to show it's unreadable |
| `grep -c "STORM"` | Count calls to the string-decoder function. `-c` counts instead of printing, and the number is the point: every string in the script goes through it |

**POINT OUT**

> That's the source, and it's unreadable — every string is a call to a decoder function with a
> list of numbers. Under it sits a large blob of hex, which is RC4-encrypted, with the key sitting
> in plain sight in the script, because the script needs it to run. Decrypt that and you get
> compressed data. Decompress it with Windows' own LZNT1 and out falls a complete PE file — an
> executable that never existed on disk at any point. It lives only in memory and gets injected
> into a legitimate Windows process.
>
> Four layers: compiled, obfuscated, encrypted, compressed. None of them is individually hard.
> The defence is the stacking.

**SAY** *(hand-off to prepared results — do not attempt to live-code this)*

> I've run that unwrapping ahead of time, because emulating the decoder takes a few minutes and
> you don't want to watch me do it. Here's what falls out.

**PRESENT (prepared):**

- Final stage is an **information stealer**, injected into `explorer.exe`, built for **screen
  capture** (`BitBlt` plus a PNG encoder) and **clipboard theft** (`OpenClipboard` /
  `GetClipboardData`).
- **C2 domain: `crowfza.xyz`**
- The malware does **not** carry that address. It fetches a public web profile and reads the real
  address out of a field on it — a **dead-drop resolver**.

**POINT OUT**

> And this is the part I'd want in the report more than the domain itself. Block `crowfza.xyz` and
> the attacker edits one profile field and has a new one, instantly, free. Meanwhile the traffic
> your sensors see is an ordinary HTTPS request to a platform everybody uses, which no reputation
> system will flag.
>
> So the durable indicator isn't the domain. It's the resolver URL — the one piece the attacker
> can't rotate without rebuilding and redistributing the sample.

> ### ✅ TASK 10 — `crowfza.xyz`

---

## CLOSING — 90 seconds

> Let's put the whole chain back together.
>
> A user went looking for cracked CAD software and ran the installer as Administrator. That
> installer dropped nine files with a fake extension and ran a batch script. The script checked
> for six antivirus products, found none, unpacked a cabinet archive using a signed Microsoft
> utility, and glued two executables together out of fragments. One of those was a renamed copy
> of AutoIt — legitimate, signed, allowlisted everywhere. It loaded a script that decrypted a
> payload in memory and injected it into explorer. Then it deleted the evidence.
>
> Here's what I want you to take away. At no point did a malicious executable exist on that disk
> as a complete file. Every binary that ran was signed and legitimate. There was nothing for a
> hash-based control to catch, and nothing for an allowlist to reject.
>
> And we reconstructed all of it — every step, to the millisecond — from artifacts nobody enabled
> and nobody thought to clear. A performance cache. A filesystem change log. A battery-saving
> registry key. That's the job.

**Anticipated questions**

| Question | Answer |
| --- | --- |
| "Why not just use Autopsy / a commercial suite?" | Would work. Doing it by hand shows which artifact answers which question — that's the transferable skill. |
| "Would EDR have caught this?" | Behavioural EDR, probably — the `copy /b` reassembly and the injection are loud. Signature and hash-based controls, no. |
| "How do you know the fragment order?" | The batch script specifies it. Wrong order gives a different hash, so the hash matching is itself the proof. |
| "Is the victim account really Administrator?" | SID ends in `-500`, the built-in local administrator. No escalation step anywhere in the chain. |
