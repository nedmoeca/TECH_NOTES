---
link: https://app.hackthebox.com/sherlocks/CAMouflage
difficulty: Easy
team: blue
category: Windows DFIR / Malware Analysis
tags:
  - sherlock
  - dfir
  - prefetch
  - usn
  - bam
  - autoit
  - presenter-notes
release date: 2026-05-28
solved:
rebuilt: 2026-09-17
---

<div style="text-align: center; padding: 80px 40px; page-break-after: always;">

  <img src="/ASSETS/writeup_hack_the_box_logo.png" style="width: 1220px; margin-bottom: 60px;" />

  <div><p style="font-size: 40px; font-weight: 600; margin-bottom: 40px;">CAMouflage — Presenter Notes</p></div>

  <img src="https://cdn.services-k8s.prod.aws.htb.systems/content/sherlocks/avatar/a1c56189-c2c1-418c-877c-453904ced993-1778691170.png" style="width: 400px; margin-bottom: 60px;" />

  <div style="font-size: 22px; line-height: 2.2;">
    <p style="margin: 0;">Presented by: <a href="https://app.hackthebox.com/users/1809572">nedmoeca</a></p>
    <p style="margin: 0;">Author(s): <a href="https://app.hackthebox.com/users/1396367">M4shl3</a></p>
    <p style="margin: 0;">Difficulty: Easy &nbsp;|&nbsp; Category: Windows DFIR</p>
  </div>

</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## How to use these notes:

This document is a **live walkthrough script**, not a report. It is ordered exactly as the
investigation is performed, and each step carries four parts:

| Part | What it is | When you use it |
| --- | --- | --- |
| **SAY** | Spoken framing — the sentences delivered to the room *before* the command runs. Explains the action and the reasoning, and never reveals the result. | Read aloud, then run |
| **RUN** | The exact copy-pasteable command | Paste into the terminal on screen |
| **BREAKDOWN** | Flag-by-flag reasoning table, for when someone asks mid-demo | Reference only — do not read aloud in full |
| **POINT OUT** | What to draw the audience's attention to *after* the output appears, and the finding it establishes | Read aloud once output is on screen |

Sections are numbered to match the HTB task they answer. Section 0 belongs to no task —
it is the scoping work that makes every later answer defensible.

<div align="center">
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## Sherlock Scenario:

A newly launched campaign has been detected targeting multiple users utilizing cracked
applications. We received an alert indicating unusual behavior from one of our user's laptops
and performed an initial triage. Your task is to conduct a deep dive investigation to determine
the root cause and extent of the incident.

### Opening framing — SAY:

> This is a Windows DFIR box with a malware-analysis tail on it. The whole design of the machine
> is an *absence*: the victim host had no EDR, no Sysmon, and no Defender telemetry. There is no
> process-creation log anywhere in this collection. So every single thing we're about to prove —
> what ran, when it ran, what it dropped, when it died — has to be rebuilt from artifacts Windows
> writes *incidentally*, as a side effect of doing its job. That's Prefetch, the USN Journal, the
> Master File Table, and a registry key called BAM.
>
> The second thing to flag up front: no complete malicious executable ever exists on this disk.
> The malware ships itself in fragments, assembles them at runtime with `copy /b`, runs the
> result, and deletes it seconds later. If you went looking for "the malware file", you would
> find nothing and conclude the host was clean.

### Known open questions carried into this run:

Two answers are disputed between the reference material and the previous attempt at this box.
They are flagged here so they are resolved from evidence rather than assumed:

| Task | Value A | Value B | Resolution |
| --- | --- | --- | --- |
| 6 — AV/EDR strings searched | `6` (both peer reports, accepted by HTB) | 8–9 (previous attempt) | *pending — Section 6* |
| 10 — C2 domain | `crowfza.xyz` (both peer reports) | `media.cloud839v1.cfd` (previous attempt) | *pending — Section 10* |

<div align="center">
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## 0. Triage & Scoping:

### 0.1 Locate the collection root and map the artifact tree:

#### SAY:

> Before we answer anything, we need to know what we were actually given. This is not a disk
> image — it's a *triage collection*. A tool called KAPE walked the live machine and copied out
> a pre-chosen list of high-value artifacts: Prefetch, the registry hives, the event logs, the
> Master File Table, the USN Journal, browser data. Everything else on that disk was left behind.
>
> That matters more than it sounds. The shape of this collection decides which questions are
> answerable and, just as importantly, which ones are *not*. There is no packet capture in here.
> There is no DNS cache. So when we get to the command-and-control question at the end, we
> already know the answer cannot come from network evidence — it has to come out of the malware
> itself. Knowing that now saves us from taking a domain off the wrong layer of the attack chain.
>
> Two things I specifically want to confirm exist before we go any further: the USN Journal, at
> `$Extend\$J`, and the SYSTEM registry hive. Task 2 and Task 3 are unanswerable without them.
> So — let's find the root of the extraction and print its skeleton.

#### RUN:

```bash
ROOT=$(find ~ -maxdepth 7 -type d -iname '*205150_output*' 2>/dev/null | head -1); echo "ROOT=${ROOT:-UNSET}"; echo '---'; find "$ROOT" -maxdepth 4 -type d 2>/dev/null | sed "s|$ROOT|.|" | sort
```

#### BREAKDOWN:

| Component | Technical reason | Simple Explanation |
| --- | --- | --- |
| `find ~ -maxdepth 7` | Restricts the search to the home tree and caps recursion depth. The KAPE output directory sits roughly four levels inside `Downloads`. | Only look in my own folders, and don't dig deeper than seven levels — otherwise it takes forever. |
| `-type d` | Matches directories only. The acquisition timestamp also appears inside filenames within the collection. | I want the *folder*, not files that happen to have the same name in them. |
| `-iname '*205150_output*'` | Case-insensitive glob on the KAPE output folder, which is named after the acquisition time. | Find the folder whose name contains this time, ignoring capital letters. |
| `2>/dev/null` | Discards permission-denied messages on stderr. | Throw away the error noise so the screen stays readable. |
| `head -1` | Returns only the first match. | If there's more than one copy lying around, just take the first. |
| `echo "ROOT=${ROOT:-UNSET}"` | Prints the captured variable, substituting `UNSET` when empty — a guard against silently operating on an empty path. | Show me what I found. If it says UNSET, the search failed and nothing below is real. |
| `find "$ROOT" -maxdepth 4 -type d` | Walks four levels of directories from the root. | Draw me the folder skeleton, four levels deep. |
| `sed "s\|$ROOT\|.\|"` | Rewrites the long absolute prefix to `.` for legibility. | Chop the long path off the front of every line. |
| `sort` | Deterministic ordering, so the tree reads top-down. | Put it in alphabetical order so it reads like a tree. |

#### POINT OUT:

*Pending — awaiting terminal output.*

Expected landmarks: `./C/Windows/prefetch`, `./C/Windows/System32/config` (SYSTEM hive → BAM),
`./C/$Extend` (USN Journal), `./C/Users/Administrator/AppData/Local/Temp` (staged payload set),
`./C/Windows/System32/winevt/logs`.

#### EVIDENCE:

*Pending — awaiting terminal output.*

---
