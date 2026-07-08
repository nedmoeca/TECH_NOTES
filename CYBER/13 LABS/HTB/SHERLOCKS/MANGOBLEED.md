---
link: https://app.hackthebox.com/sherlocks/MangoBleed?tab=play_sherlock
description: Very Easy
release date: 2025-12-31
tags:
image: https://cdn.services-k8s.prod.aws.htb.systems/content/sherlocks/avatar/a0b95fe3-116c-47c8-9ab5-e86ae3049a38.png
solved:
solve date:
---
<div style="text-align: center; padding: 80px 40px; page-break-after: always;">

  <img src="/ASSETS/HTB Logo.png" style="width: 1220px; margin-bottom: 60px;" />

  <div><p style="font-size: 40px; font-weight: 600; margin-bottom: 40px;">MangoBleed Writeup</p></div>

  <img src="https://cdn.services-k8s.prod.aws.htb.systems/content/sherlocks/avatar/a0b95fe3-116c-47c8-9ab5-e86ae3049a38.png" style="width: 400px; margin-bottom: 60px;" />

  <div style="font-size: 18px; line-height: 2.2;">
    <p style="margin: 0;">Prepared by: nedmoeca</p>
    <p style="margin: 0;">Author(s): CyberJunkie</p>
    <p style="margin: 0;">Difficulty: Very Easy</p>
    <p style="margin: 0;">Date: 08 Jul 2026</p>
  </div>

</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## Sherlock Scenario

You were contacted early this morning to handle a high‑priority incident involving a suspected compromised server. The host, mongodbsync, is a secondary MongoDB server. According to the administrator, it's maintained once a month, and they recently became aware of a vulnerability referred to as ==MongoBleed==. As a precaution, the administrator has provided you with root-level access to facilitate your investigation.

You have already collected a triage acquisition from the server using UAC. Perform a rapid triage analysis of the collected artifacts to determine whether the system has been compromised, ==identify any attacker activity (initial access, persistence, privilege escalation, lateral movement, or data access/exfiltration), and summarize your findings with an initial incident assessment and recommended next steps.==
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

You were handed a single file, `MangoBleed.zip`, as the starting evidence package for this investigation. Before touching its contents, the first step in any analysis is simply to confirm what you have on disk — this is basic forensic hygiene: know your working directory before you start extracting or modifying anything.

```shell
┌──(kali㉿kali)-[~/nedmoeca/HTB/Sherlocks/MangoBleed]
└─$ ls
MangoBleed.zip
```

`MangoBleed.zip` is a compressed archive — a single file that bundles many files/folders together and shrinks their size. Since the contents are unknown until extracted, and the archive is password-protected (a common practice for CTF evidence files, so that antivirus tools or search engines don't flag/index attacker artifacts contained inside), the next logical step is to extract it using a tool capable of reading `.zip` archives and handling that password prompt.

**Command:** `7z x MangoBleed.zip`

**Breakdown:**

- `7z`
    - Description: The command-line executable for **7-Zip**, a file archiver utility capable of creating and extracting many archive formats (`.zip`, `.7z`, `.rar`, `.tar`, etc.).
    - Purpose: Chosen because it reliably handles password-protected ZIP archives and reports extraction integrity (whether the file is corrupted).
- `x`
    - Description: The 7-Zip sub-command for "extract with full paths" — as opposed to `e` (extract, flattening all files into one folder), `x` preserves the original folder structure inside the archive.
    - Purpose: Preserving the original folder structure is critical in forensics — the folder hierarchy created by the acquisition tool carries meaning (as you'll see below), and flattening it would destroy that context.
- `MangoBleed.zip`
    - Description: The target archive to extract, specified as a positional argument.
    - Purpose: Points 7-Zip at the evidence file provided for this Sherlock.

**Result:**

```shell
┌──(kali㉿kali)-[~/nedmoeca/HTB/Sherlocks/MangoBleed]
└─$ 7z x MangoBleed.zip 

7-Zip 25.01 (x64) : Copyright (c) 1999-2025 Igor Pavlov : 2025-08-03
 64-bit locale=en_US.UTF-8 Threads:4 OPEN_MAX:1024, ASM

Scanning the drive for archives:
1 file, 32727809 bytes (32 MiB)

Extracting archive: MangoBleed.zip
--            
Path = MangoBleed.zip
Type = zip
Physical Size = 32727809

    
Enter password (will not be echoed):
Everything is Ok                                                           

Folders: 678
Files: 4196
Size:       100216130
Compressed: 32727809
```

If your extraction succeeded, listing the working directory again confirms what new folder(s) were created, and gives you the name you'll need for all subsequent navigation.

```shell
┌──(kali㉿kali)-[~/nedmoeca/HTB/Sherlocks/MangoBleed]
└─$ ls                             
MangoBleed.zip  uac-mongodbsync-linux-triage
```

The folder name `uac-mongodbsync-linux-triage` tells you two important things before you even open a single file:

1. **`uac`** — this data was collected using **UAC (Unix-like Artifacts Collector)**, an open-source live-triage tool. UAC runs on a live (running) Linux system and systematically dumps hundreds of small text files capturing system state — running processes, network connections, logs, user accounts, installed packages, and more — without needing to shut the machine down or take a full disk image. Think of it like doing vital-sign checks on a patient (pulse, blood pressure, temperature) rather than performing full surgery — it's a snapshot, not a deep dive into every byte on disk.
2. **`mongodbsync`** — this is the hostname of the compromised machine, matching the scenario briefing that the affected server is a secondary MongoDB server.

Before navigating into it, it's worth doing a first-pass listing of the top level of the folder, followed by a full recursive listing (`tree`) to understand how UAC organized everything — this is the map you'll use to know where to look for specific evidence later (logs, process info, config files, etc.).

```shell
┌──(kali㉿kali)-[~/nedmoeca/HTB/Sherlocks/MangoBleed]
└─$ ls -la uac-mongodbsync-linux-triage 
total 28
drwxrwxr-x  7 kali kali 4096 Dec 29  2025  .
drwxrwxr-x  3 kali kali 4096 Jul  8 07:51  ..
drwxrwxr-x  2 kali kali 4096 Dec 29  2025  bodyfile
drwxrwxr-x  2 kali kali 4096 Dec 29  2025  hash_executables
drwxrwxr-x  9 kali kali 4096 Dec 29  2025  live_response
drwxrwxr-x 10 kali kali 4096 Dec 29  2025 '[root]'
drwxrwxr-x  2 kali kali 4096 Dec 29  2025  system
```

```shell
.
├── MangoBleed.zip
├── tree_output.txt
└── uac-mongodbsync-linux-triage
    ├── bodyfile
    │   └── bodyfile.txt
    ├── hash_executables
    │   ├── hash_executables.md5
    │   └── hash_executables.sha1
    ├── live_response
    │   ├── containers
    │   │   ├── lxc_image_list.txt
    │   │   ├── lxc_info.txt
    │   │   ├── lxc_list.txt
    │   │   ├── lxc_profile_list.txt
    │   │   ├── lxc_profile_show_default.txt
    │   │   ├── lxc_storage_list.txt
    │   │   ├── lxc_version.txt
    │   │   └── lxc_warning_list.txt
    │   ├── hardware
    │   │   ├── dmesg.txt
    │   │   ├── dmidecode.txt
    │   │   ├── lscpu.txt
    │   │   ├── lshw.txt
    │   │   ├── lspci_-nn_-k.txt
    │   │   ├── lspci.txt
    │   │   └── lspci_-vv.txt
    │   ├── network
    │   │   ├── hostnamectl.txt
    │   │   ├── hostname_-f.txt
    │   │   ├── hostname.txt
    │   │   ├── ip_addr_show.txt
    │   │   ├── ip_link_show.txt
    │   │   ├── ip_neighbor_show.txt
    │   │   ├── ip_route_show.txt
    │   │   ├── iptables_-L_-v_-n.txt
    │   │   ├── iptables_-t_nat_-L_-v_-n.txt
    │   │   ├── lsof_-nPli.txt
    │   │   ├── lsof_-U.txt
    │   │   ├── proc_net_tcp6.txt
    │   │   ├── proc_net_tcp.txt
    │   │   ├── proc_net_udp6.txt
    │   │   ├── proc_net_udp.txt
    │   │   ├── ss_-anp.txt
    │   │   ├── ss_-ap.txt
    │   │   ├── ss_-tanp.txt
    │   │   ├── ss_-tap.txt
    │   │   ├── ss_-tlnp.txt
    │   │   ├── ss_-tlp.txt
    │   │   ├── ss_-uanp.txt
    │   │   ├── ss_-uap.txt
    │   │   ├── ss_-ulnp.txt
    │   │   ├── ss_-ulp.txt
    │   │   ├── ufw_status_verbose.txt
    │   │   └── uname_-n.txt
    │   ├── packages
    │   │   ├── dpkg_-l.txt
    │   │   ├── dpkg_-V.txt
    │   │   ├── snap_list_--all.txt
    │   │   └── snap_list.txt
    │   ├── process
    │   │   ├── date_before_ps_-axo_pid_user_etime_args.txt
    │   │   ├── date_before_ps_-axo_pid_user_lstart_args.txt
    │   │   ├── hash_running_processes.md5
    │   │   ├── hash_running_processes.sha1
    │   │   ├── hidden_pids_for_ps_command.txt
    │   │   ├── ls_-l_proc_pid_cwd.txt
    │   │   ├── ls_-l_proc.txt
    │   │   ├── lsof_-nPl.txt
    │   │   ├── proc
    │   │   │   ├── 1
    │   │   │   │   ├── children.txt
    │   │   │   │   ├── cmdline.txt
    │   │   │   │   ├── comm.txt
    │   │   │   │   ├── environ.txt
    │   │   │   │   ├── fd.txt
    │   │   │   │   ├── map_files.txt
    │   │   │   │   ├── maps.txt
    │   │   │   │   ├── mounts.txt
    │   │   │   │   ├── net
    │   │   │   │   │   └── unix.txt
    │   │   │   │   ├── stack.txt
    │   │   │   │   ├── stat.txt
    │   │   │   │   ├── status.txt
    │   │   │   │   └── strings.txt.gz
    │   │   │   ├── 10
    │   │   │   │   ├── comm.txt
    │   │   │   │   ├── fd.txt
    │   │   │   │   ├── map_files.txt
    │   │   │   │   ├── mounts.txt
    │   │   │   │   ├── net
    │   │   │   │   │   └── unix.txt
    │   │   │   │   ├── stack.txt
    │   │   │   │   ├── stat.txt
    │   │   │   │   └── status.txt
    │   │   │   ├── 119195
    │   │   │   │   └── strings.txt.gz
    │   │   │   ├── 1205
    │   │   │   │   ├── comm.txt
    │   │   │   │   ├── fd.txt
    │   │   │   │   ├── map_files.txt
    │   │   │   │   ├── mounts.txt
    │   │   │   │   ├── net
    │   │   │   │   │   └── unix.txt
    │   │   │   │   ├── stack.txt
    │   │   │   │   ├── stat.txt
    │   │   │   │   └── status.txt
    │   │   │   ├── 13
    │   │   │   │   ├── comm.txt
    │   │   │   │   ├── fd.txt
    │   │   │   │   ├── map_files.txt
    │   │   │   │   ├── mounts.txt
    │   │   │   │   ├── net
    │   │   │   │   │   └── unix.txt
    │   │   │   │   ├── stack.txt
    │   │   │   │   ├── stat.txt
    │   │   │   │   └── status.txt
    │   │   │   ├── 135
    │   │   │   │   ├── cmdline.txt
    │   │   │   │   ├── comm.txt
    │   │   │   │   ├── environ.txt
    │   │   │   │   ├── fd.txt
    │   │   │   │   ├── map_files.txt
    │   │   │   │   ├── maps.txt
    │   │   │   │   ├── mounts.txt
    │   │   │   │   ├── net
    │   │   │   │   │   └── unix.txt
    │   │   │   │   ├── stack.txt
    │   │   │   │   ├── stat.txt
    │   │   │   │   ├── status.txt
    │   │   │   │   └── strings.txt.gz
    │   │   │   ├── 14
    │   │   │   │   ├── comm.txt
    │   │   │   │   ├── fd.txt
    │   │   │   │   ├── map_files.txt
    │   │   │   │   ├── mounts.txt
    │   │   │   │   ├── net
    │   │   │   │   │   └── unix.txt
    │   │   │   │   ├── stack.txt
    │   │   │   │   ├── stat.txt
    │   │   │   │   └── status.txt
    │   │   │   ├── 15
    │   │   │   │   ├── comm.txt
    │   │   │   │   ├── fd.txt
    │   │   │   │   ├── map_files.txt
    │   │   │   │   ├── mounts.txt
    │   │   │   │   ├── net
    │   │   │   │   │   └── unix.txt
    │   │   │   │   ├── stack.txt
    │   │   │   │   ├── stat.txt
    │   │   │   │   └── status.txt
    │   │   │   ├── 155
    │   │   │   │   ├── comm.txt
    │   │   │   │   ├── fd.txt
    │   │   │   │   ├── map_files.txt
    │   │   │   │   ├── mounts.txt
    │   │   │   │   ├── net
    │   │   │   │   │   └── unix.txt
    │   │   │   │   ├── stack.txt
    │   │   │   │   ├── stat.txt
    │   │   │   │   └── status.txt
    │   │   │   ├── 156
    │   │   │   │   ├── comm.txt
    │   │   │   │   ├── fd.txt
    │   │   │   │   ├── map_files.txt
    │   │   │   │   ├── mounts.txt
    │   │   │   │   ├── net
    │   │   │   │   │   └── unix.txt
    │   │   │   │   ├── stack.txt
    │   │   │   │   ├── stat.txt
    │   │   │   │   └── status.txt
    │   │   │   ├── 16
    │   │   │   │   ├── comm.txt
    │   │   │   │   ├── fd.txt
    │   │   │   │   ├── map_files.txt
    │   │   │   │   ├── mounts.txt
    │   │   │   │   ├── net
    │   │   │   │   │   └── unix.txt
    │   │   │   │   ├── stack.txt
    │   │   │   │   ├── stat.txt
    │   │   │   │   └── status.txt
    │   │   │   ├── 17
    │   │   │   │   ├── comm.txt
    │   │   │   │   ├── fd.txt
    │   │   │   │   ├── map_files.txt
    │   │   │   │   ├── mounts.txt
    │   │   │   │   ├── net
    │   │   │   │   │   └── unix.txt
    │   │   │   │   ├── stack.txt
    │   │   │   │   ├── stat.txt
    │   │   │   │   └── status.txt
    │   │   │   ├── 18
    │   │   │   │   ├── comm.txt
    │   │   │   │   ├── fd.txt
    │   │   │   │   ├── map_files.txt
    │   │   │   │   ├── mounts.txt
    │   │   │   │   ├── net
    │   │   │   │   │   └── unix.txt
    │   │   │   │   ├── stack.txt
    │   │   │   │   ├── stat.txt
    │   │   │   │   └── status.txt
    │   │   │   ├── 19
    │   │   │   │   ├── comm.txt
    │   │   │   │   ├── fd.txt
    │   │   │   │   ├── map_files.txt
    │   │   │   │   ├── mounts.txt
    │   │   │   │   ├── net
    │   │   │   │   │   └── unix.txt
    │   │   │   │   ├── stack.txt
    │   │   │   │   ├── stat.txt
    │   │   │   │   └── status.txt
    │   │   │   ├── 194
    │   │   │   │   ├── cmdline.txt
    │   │   │   │   ├── comm.txt
    │   │   │   │   ├── environ.txt
    │   │   │   │   ├── fd.txt
    │   │   │   │   ├── map_files.txt
    │   │   │   │   ├── maps.txt
    │   │   │   │   ├── mounts.txt
    │   │   │   │   ├── net
    │   │   │   │   │   └── unix.txt
    │   │   │   │   ├── stack.txt
    │   │   │   │   ├── stat.txt
    │   │   │   │   ├── status.txt
    │   │   │   │   └── strings.txt.gz
    │   │   │   ├── 2
    │   │   │   │   ├── children.txt
    │   │   │   │   ├── comm.txt
    │   │   │   │   ├── fd.txt
    │   │   │   │   ├── map_files.txt
    │   │   │   │   ├── mounts.txt
    │   │   │   │   ├── net
    │   │   │   │   │   └── unix.txt
    │   │   │   │   ├── stack.txt
    │   │   │   │   ├── stat.txt
    │   │   │   │   └── status.txt
    │   │   │   ├── 20
    │   │   │   │   ├── comm.txt
    │   │   │   │   ├── fd.txt
    │   │   │   │   ├── map_files.txt
    │   │   │   │   ├── mounts.txt
    │   │   │   │   ├── net
    │   │   │   │   │   └── unix.txt
    │   │   │   │   ├── stack.txt
    │   │   │   │   ├── stat.txt
    │   │   │   │   └── status.txt
    │   │   │   ├── 2009
    │   │   │   │   ├── cmdline.txt
    │   │   │   │   ├── comm.txt
    │   │   │   │   ├── environ.txt
    │   │   │   │   ├── fd.txt
    │   │   │   │   ├── map_files.txt
    │   │   │   │   ├── maps.txt
    │   │   │   │   ├── mounts.txt
    │   │   │   │   ├── net
    │   │   │   │   │   └── unix.txt
    │   │   │   │   ├── stack.txt
    │   │   │   │   ├── stat.txt
    │   │   │   │   ├── status.txt
    │   │   │   │   └── strings.txt.gz
    │   │   │   ├── 21
    │   │   │   │   ├── comm.txt
    │   │   │   │   ├── fd.txt
    │   │   │   │   ├── map_files.txt
    │   │   │   │   ├── mounts.txt
    │   │   │   │   ├── net
    │   │   │   │   │   └── unix.txt
    │   │   │   │   ├── stack.txt
    │   │   │   │   ├── stat.txt
    │   │   │   │   └── status.txt
    │   │   │   ├── 214
    │   │   │   │   ├── cmdline.txt
    │   │   │   │   ├── comm.txt
    │   │   │   │   ├── environ.txt
    │   │   │   │   ├── fd.txt
    │   │   │   │   ├── map_files.txt
    │   │   │   │   ├── maps.txt
    │   │   │   │   ├── mounts.txt
    │   │   │   │   ├── net
    │   │   │   │   │   └── unix.txt
    │   │   │   │   ├── stack.txt
    │   │   │   │   ├── stat.txt
    │   │   │   │   ├── status.txt
    │   │   │   │   └── strings.txt.gz
    │   │   │   ├── 2152
    │   │   │   │   ├── children.txt
    │   │   │   │   ├── cmdline.txt
    │   │   │   │   ├── comm.txt
    │   │   │   │   ├── environ.txt
    │   │   │   │   ├── fd.txt
    │   │   │   │   ├── map_files.txt
    │   │   │   │   ├── maps.txt
    │   │   │   │   ├── mounts.txt
    │   │   │   │   ├── net
    │   │   │   │   │   └── unix.txt
    │   │   │   │   ├── stack.txt
    │   │   │   │   ├── stat.txt
    │   │   │   │   ├── status.txt
    │   │   │   │   └── strings.txt.gz
    │   │   │   ├── 2167
    │   │   │   │   ├── comm.txt
    │   │   │   │   ├── fd.txt
    │   │   │   │   ├── map_files.txt
    │   │   │   │   ├── mounts.txt
    │   │   │   │   ├── net
    │   │   │   │   │   └── unix.txt
    │   │   │   │   ├── stack.txt
    │   │   │   │   ├── stat.txt
    │   │   │   │   └── status.txt
    │   │   │   ├── 22
    │   │   │   │   ├── comm.txt
    │   │   │   │   ├── fd.txt
    │   │   │   │   ├── map_files.txt
    │   │   │   │   ├── mounts.txt
    │   │   │   │   ├── net
    │   │   │   │   │   └── unix.txt
    │   │   │   │   ├── stack.txt
    │   │   │   │   ├── stat.txt
    │   │   │   │   └── status.txt
    │   │   │   ├── 221
    │   │   │   │   ├── comm.txt
    │   │   │   │   ├── fd.txt
    │   │   │   │   ├── map_files.txt
    │   │   │   │   ├── mounts.txt
    │   │   │   │   ├── net
    │   │   │   │   │   └── unix.txt
    │   │   │   │   ├── stack.txt
    │   │   │   │   ├── stat.txt
    │   │   │   │   └── status.txt
    │   │   │   ├── 23
    │   │   │   │   ├── comm.txt
    │   │   │   │   ├── fd.txt
    │   │   │   │   ├── map_files.txt
    │   │   │   │   ├── mounts.txt
    │   │   │   │   ├── net
    │   │   │   │   │   └── unix.txt
    │   │   │   │   ├── stack.txt
    │   │   │   │   ├── stat.txt
    │   │   │   │   └── status.txt
    │   │   │   ├── 24
    │   │   │   │   ├── comm.txt
    │   │   │   │   ├── fd.txt
    │   │   │   │   ├── map_files.txt
    │   │   │   │   ├── mounts.txt
    │   │   │   │   ├── net
    │   │   │   │   │   └── unix.txt
    │   │   │   │   ├── stack.txt
    │   │   │   │   ├── stat.txt
    │   │   │   │   └── status.txt
    │   │   │   ├── 25
    │   │   │   │   ├── comm.txt
    │   │   │   │   ├── fd.txt
    │   │   │   │   ├── map_files.txt
    │   │   │   │   ├── mounts.txt
    │   │   │   │   ├── net
    │   │   │   │   │   └── unix.txt
    │   │   │   │   ├── stack.txt
    │   │   │   │   ├── stat.txt
    │   │   │   │   └── status.txt
    │   │   │   ├── 26
    │   │   │   │   ├── comm.txt
    │   │   │   │   ├── fd.txt
    │   │   │   │   ├── map_files.txt
    │   │   │   │   ├── mounts.txt
    │   │   │   │   ├── net
    │   │   │   │   │   └── unix.txt
    │   │   │   │   ├── stack.txt
    │   │   │   │   ├── stat.txt
    │   │   │   │   └── status.txt
    │   │   │   ├── 277
    │   │   │   │   ├── comm.txt
    │   │   │   │   ├── fd.txt
    │   │   │   │   ├── map_files.txt
    │   │   │   │   ├── mounts.txt
    │   │   │   │   ├── net
    │   │   │   │   │   └── unix.txt
    │   │   │   │   ├── stack.txt
    │   │   │   │   ├── stat.txt
    │   │   │   │   └── status.txt
    │   │   │   ├── 278
    │   │   │   │   ├── comm.txt
    │   │   │   │   ├── fd.txt
    │   │   │   │   ├── map_files.txt
    │   │   │   │   ├── mounts.txt
    │   │   │   │   ├── net
    │   │   │   │   │   └── unix.txt
    │   │   │   │   ├── stack.txt
    │   │   │   │   ├── stat.txt
    │   │   │   │   └── status.txt
    │   │   │   ├── 28
    │   │   │   │   ├── comm.txt
    │   │   │   │   ├── fd.txt
    │   │   │   │   ├── map_files.txt
    │   │   │   │   ├── mounts.txt
    │   │   │   │   ├── net
    │   │   │   │   │   └── unix.txt
    │   │   │   │   ├── stack.txt
    │   │   │   │   ├── stat.txt
    │   │   │   │   └── status.txt
    │   │   │   ├── 289
    │   │   │   │   ├── comm.txt
    │   │   │   │   ├── fd.txt
    │   │   │   │   ├── map_files.txt
    │   │   │   │   ├── mounts.txt
    │   │   │   │   ├── net
    │   │   │   │   │   └── unix.txt
    │   │   │   │   ├── stack.txt
    │   │   │   │   ├── stat.txt
    │   │   │   │   └── status.txt
    │   │   │   ├── 29
    │   │   │   │   ├── comm.txt
    │   │   │   │   ├── fd.txt
    │   │   │   │   ├── map_files.txt
    │   │   │   │   ├── mounts.txt
    │   │   │   │   ├── net
    │   │   │   │   │   └── unix.txt
    │   │   │   │   ├── stack.txt
    │   │   │   │   ├── stat.txt
    │   │   │   │   └── status.txt
    │   │   │   ├── 3
    │   │   │   │   ├── comm.txt
    │   │   │   │   ├── fd.txt
    │   │   │   │   ├── map_files.txt
    │   │   │   │   ├── mounts.txt
    │   │   │   │   ├── net
    │   │   │   │   │   └── unix.txt
    │   │   │   │   ├── stack.txt
    │   │   │   │   ├── stat.txt
    │   │   │   │   └── status.txt
    │   │   │   ├── 30
    │   │   │   │   ├── comm.txt
    │   │   │   │   ├── fd.txt
    │   │   │   │   ├── map_files.txt
    │   │   │   │   ├── mounts.txt
    │   │   │   │   ├── net
    │   │   │   │   │   └── unix.txt
    │   │   │   │   ├── stack.txt
    │   │   │   │   ├── stat.txt
    │   │   │   │   └── status.txt
    │   │   │   ├── 31
    │   │   │   │   ├── comm.txt
    │   │   │   │   ├── fd.txt
    │   │   │   │   ├── map_files.txt
    │   │   │   │   ├── mounts.txt
    │   │   │   │   ├── net
    │   │   │   │   │   └── unix.txt
    │   │   │   │   ├── stack.txt
    │   │   │   │   ├── stat.txt
    │   │   │   │   └── status.txt
    │   │   │   ├── 32
    │   │   │   │   ├── comm.txt
    │   │   │   │   ├── fd.txt
    │   │   │   │   ├── map_files.txt
    │   │   │   │   ├── mounts.txt
    │   │   │   │   ├── net
    │   │   │   │   │   └── unix.txt
    │   │   │   │   ├── stack.txt
    │   │   │   │   ├── stat.txt
    │   │   │   │   └── status.txt
    │   │   │   ├── 33
    │   │   │   │   ├── comm.txt
    │   │   │   │   ├── fd.txt
    │   │   │   │   ├── map_files.txt
    │   │   │   │   ├── mounts.txt
    │   │   │   │   ├── net
    │   │   │   │   │   └── unix.txt
    │   │   │   │   ├── stack.txt
    │   │   │   │   ├── stat.txt
    │   │   │   │   └── status.txt
    │   │   │   ├── 35
    │   │   │   │   ├── comm.txt
    │   │   │   │   ├── fd.txt
    │   │   │   │   ├── map_files.txt
    │   │   │   │   ├── mounts.txt
    │   │   │   │   ├── net
    │   │   │   │   │   └── unix.txt
    │   │   │   │   ├── stack.txt
    │   │   │   │   ├── stat.txt
    │   │   │   │   └── status.txt
    │   │   │   ├── 36
    │   │   │   │   ├── comm.txt
    │   │   │   │   ├── fd.txt
    │   │   │   │   ├── map_files.txt
    │   │   │   │   ├── mounts.txt
    │   │   │   │   ├── net
    │   │   │   │   │   └── unix.txt
    │   │   │   │   ├── stack.txt
    │   │   │   │   ├── stat.txt
    │   │   │   │   └── status.txt
    │   │   │   ├── 37
    │   │   │   │   ├── comm.txt
    │   │   │   │   ├── fd.txt
    │   │   │   │   ├── map_files.txt
    │   │   │   │   ├── mounts.txt
    │   │   │   │   ├── net
    │   │   │   │   │   └── unix.txt
    │   │   │   │   ├── stack.txt
    │   │   │   │   ├── stat.txt
    │   │   │   │   └── status.txt
    │   │   │   ├── 38
    │   │   │   │   ├── comm.txt
    │   │   │   │   ├── fd.txt
    │   │   │   │   ├── map_files.txt
    │   │   │   │   ├── mounts.txt
    │   │   │   │   ├── net
    │   │   │   │   │   └── unix.txt
    │   │   │   │   ├── stack.txt
    │   │   │   │   ├── stat.txt
    │   │   │   │   └── status.txt
    │   │   │   ├── 39
    │   │   │   │   ├── comm.txt
    │   │   │   │   ├── fd.txt
    │   │   │   │   ├── map_files.txt
    │   │   │   │   ├── mounts.txt
    │   │   │   │   ├── net
    │   │   │   │   │   └── unix.txt
    │   │   │   │   ├── stack.txt
    │   │   │   │   ├── stat.txt
    │   │   │   │   └── status.txt
    │   │   │   ├── 39967
    │   │   │   │   ├── comm.txt
    │   │   │   │   ├── fd.txt
    │   │   │   │   ├── map_files.txt
    │   │   │   │   ├── mounts.txt
    │   │   │   │   ├── net
    │   │   │   │   │   └── unix.txt
    │   │   │   │   ├── stack.txt
    │   │   │   │   ├── stat.txt
    │   │   │   │   └── status.txt
    │   │   │   ├── 4
    │   │   │   │   ├── comm.txt
    │   │   │   │   ├── fd.txt
    │   │   │   │   ├── map_files.txt
    │   │   │   │   ├── mounts.txt
    │   │   │   │   ├── net
    │   │   │   │   │   └── unix.txt
    │   │   │   │   ├── stack.txt
    │   │   │   │   ├── stat.txt
    │   │   │   │   └── status.txt
    │   │   │   ├── 40
    │   │   │   │   ├── comm.txt
    │   │   │   │   ├── fd.txt
    │   │   │   │   ├── map_files.txt
    │   │   │   │   ├── mounts.txt
    │   │   │   │   ├── net
    │   │   │   │   │   └── unix.txt
    │   │   │   │   ├── stack.txt
    │   │   │   │   ├── stat.txt
    │   │   │   │   └── status.txt
    │   │   │   ├── 41
    │   │   │   │   ├── comm.txt
    │   │   │   │   ├── fd.txt
    │   │   │   │   ├── map_files.txt
    │   │   │   │   ├── mounts.txt
    │   │   │   │   ├── net
    │   │   │   │   │   └── unix.txt
    │   │   │   │   ├── stack.txt
    │   │   │   │   ├── stat.txt
    │   │   │   │   └── status.txt
    │   │   │   ├── 412
    │   │   │   │   ├── cmdline.txt
    │   │   │   │   ├── comm.txt
    │   │   │   │   ├── environ.txt
    │   │   │   │   ├── fd.txt
    │   │   │   │   ├── map_files.txt
    │   │   │   │   ├── maps.txt
    │   │   │   │   ├── mounts.txt
    │   │   │   │   ├── net
    │   │   │   │   │   └── unix.txt
    │   │   │   │   ├── stack.txt
    │   │   │   │   ├── stat.txt
    │   │   │   │   ├── status.txt
    │   │   │   │   └── strings.txt.gz
    │   │   │   ├── 42
    │   │   │   │   ├── comm.txt
    │   │   │   │   ├── fd.txt
    │   │   │   │   ├── map_files.txt
    │   │   │   │   ├── mounts.txt
    │   │   │   │   ├── net
    │   │   │   │   │   └── unix.txt
    │   │   │   │   ├── stack.txt
    │   │   │   │   ├── stat.txt
    │   │   │   │   └── status.txt
    │   │   │   ├── 44
    │   │   │   │   ├── comm.txt
    │   │   │   │   ├── fd.txt
    │   │   │   │   ├── map_files.txt
    │   │   │   │   ├── mounts.txt
    │   │   │   │   ├── net
    │   │   │   │   │   └── unix.txt
    │   │   │   │   ├── stack.txt
    │   │   │   │   ├── stat.txt
    │   │   │   │   └── status.txt
    │   │   │   ├── 45
    │   │   │   │   ├── comm.txt
    │   │   │   │   ├── fd.txt
    │   │   │   │   ├── map_files.txt
    │   │   │   │   ├── mounts.txt
    │   │   │   │   ├── net
    │   │   │   │   │   └── unix.txt
    │   │   │   │   ├── stack.txt
    │   │   │   │   ├── stat.txt
    │   │   │   │   └── status.txt
    │   │   │   ├── 46
    │   │   │   │   ├── comm.txt
    │   │   │   │   ├── fd.txt
    │   │   │   │   ├── map_files.txt
    │   │   │   │   ├── mounts.txt
    │   │   │   │   ├── net
    │   │   │   │   │   └── unix.txt
    │   │   │   │   ├── stack.txt
    │   │   │   │   ├── stat.txt
    │   │   │   │   └── status.txt
    │   │   │   ├── 47
    │   │   │   │   ├── comm.txt
    │   │   │   │   ├── fd.txt
    │   │   │   │   ├── map_files.txt
    │   │   │   │   ├── mounts.txt
    │   │   │   │   ├── net
    │   │   │   │   │   └── unix.txt
    │   │   │   │   ├── stack.txt
    │   │   │   │   ├── stat.txt
    │   │   │   │   └── status.txt
    │   │   │   ├── 48
    │   │   │   │   ├── comm.txt
    │   │   │   │   ├── fd.txt
    │   │   │   │   ├── map_files.txt
    │   │   │   │   ├── mounts.txt
    │   │   │   │   ├── net
    │   │   │   │   │   └── unix.txt
    │   │   │   │   ├── stack.txt
    │   │   │   │   ├── stat.txt
    │   │   │   │   └── status.txt
    │   │   │   ├── 49
    │   │   │   │   ├── comm.txt
    │   │   │   │   ├── fd.txt
    │   │   │   │   ├── map_files.txt
    │   │   │   │   ├── mounts.txt
    │   │   │   │   ├── net
    │   │   │   │   │   └── unix.txt
    │   │   │   │   ├── stack.txt
    │   │   │   │   ├── stat.txt
    │   │   │   │   └── status.txt
    │   │   │   ├── 5
    │   │   │   │   ├── comm.txt
    │   │   │   │   ├── fd.txt
    │   │   │   │   ├── map_files.txt
    │   │   │   │   ├── mounts.txt
    │   │   │   │   ├── net
    │   │   │   │   │   └── unix.txt
    │   │   │   │   ├── stack.txt
    │   │   │   │   ├── stat.txt
    │   │   │   │   └── status.txt
    │   │   │   ├── 50
    │   │   │   │   ├── comm.txt
    │   │   │   │   ├── fd.txt
    │   │   │   │   ├── map_files.txt
    │   │   │   │   ├── mounts.txt
    │   │   │   │   ├── net
    │   │   │   │   │   └── unix.txt
    │   │   │   │   ├── stack.txt
    │   │   │   │   ├── stat.txt
    │   │   │   │   └── status.txt
    │   │   │   ├── 51
    │   │   │   │   ├── comm.txt
    │   │   │   │   ├── fd.txt
    │   │   │   │   ├── map_files.txt
    │   │   │   │   ├── mounts.txt
    │   │   │   │   ├── net
    │   │   │   │   │   └── unix.txt
    │   │   │   │   ├── stack.txt
    │   │   │   │   ├── stat.txt
    │   │   │   │   └── status.txt
    │   │   │   ├── 52
    │   │   │   │   ├── comm.txt
    │   │   │   │   ├── fd.txt
    │   │   │   │   ├── map_files.txt
    │   │   │   │   ├── mounts.txt
    │   │   │   │   ├── net
    │   │   │   │   │   └── unix.txt
    │   │   │   │   ├── stack.txt
    │   │   │   │   ├── stat.txt
    │   │   │   │   └── status.txt
    │   │   │   ├── 53
    │   │   │   │   ├── comm.txt
    │   │   │   │   ├── fd.txt
    │   │   │   │   ├── map_files.txt
    │   │   │   │   ├── mounts.txt
    │   │   │   │   ├── net
    │   │   │   │   │   └── unix.txt
    │   │   │   │   ├── stack.txt
    │   │   │   │   ├── stat.txt
    │   │   │   │   └── status.txt
    │   │   │   ├── 532
    │   │   │   │   ├── cmdline.txt
    │   │   │   │   ├── comm.txt
    │   │   │   │   ├── environ.txt
    │   │   │   │   ├── fd.txt
    │   │   │   │   ├── map_files.txt
    │   │   │   │   ├── maps.txt
    │   │   │   │   ├── mounts.txt
    │   │   │   │   ├── net
    │   │   │   │   │   └── unix.txt
    │   │   │   │   ├── stack.txt
    │   │   │   │   ├── stat.txt
    │   │   │   │   ├── status.txt
    │   │   │   │   └── strings.txt.gz
    │   │   │   ├── 54
    │   │   │   │   ├── comm.txt
    │   │   │   │   ├── fd.txt
    │   │   │   │   ├── map_files.txt
    │   │   │   │   ├── mounts.txt
    │   │   │   │   ├── net
    │   │   │   │   │   └── unix.txt
    │   │   │   │   ├── stack.txt
    │   │   │   │   ├── stat.txt
    │   │   │   │   └── status.txt
    │   │   │   ├── 55
    │   │   │   │   ├── comm.txt
    │   │   │   │   ├── fd.txt
    │   │   │   │   ├── map_files.txt
    │   │   │   │   ├── mounts.txt
    │   │   │   │   ├── net
    │   │   │   │   │   └── unix.txt
    │   │   │   │   ├── stack.txt
    │   │   │   │   ├── stat.txt
    │   │   │   │   └── status.txt
    │   │   │   ├── 56
    │   │   │   │   ├── comm.txt
    │   │   │   │   ├── fd.txt
    │   │   │   │   ├── map_files.txt
    │   │   │   │   ├── mounts.txt
    │   │   │   │   ├── net
    │   │   │   │   │   └── unix.txt
    │   │   │   │   ├── stack.txt
    │   │   │   │   ├── stat.txt
    │   │   │   │   └── status.txt
    │   │   │   ├── 57
    │   │   │   │   ├── comm.txt
    │   │   │   │   ├── fd.txt
    │   │   │   │   ├── map_files.txt
    │   │   │   │   ├── mounts.txt
    │   │   │   │   ├── net
    │   │   │   │   │   └── unix.txt
    │   │   │   │   ├── stack.txt
    │   │   │   │   ├── stat.txt
    │   │   │   │   └── status.txt
    │   │   │   ├── 57791
    │   │   │   │   ├── comm.txt
    │   │   │   │   ├── fd.txt
    │   │   │   │   ├── map_files.txt
    │   │   │   │   ├── mounts.txt
    │   │   │   │   ├── net
    │   │   │   │   │   └── unix.txt
    │   │   │   │   ├── stack.txt
    │   │   │   │   ├── stat.txt
    │   │   │   │   └── status.txt
    │   │   │   ├── 57792
    │   │   │   │   ├── comm.txt
    │   │   │   │   ├── fd.txt
    │   │   │   │   ├── map_files.txt
    │   │   │   │   ├── mounts.txt
    │   │   │   │   ├── net
    │   │   │   │   │   └── unix.txt
    │   │   │   │   ├── stack.txt
    │   │   │   │   ├── stat.txt
    │   │   │   │   └── status.txt
    │   │   │   ├── 57793
    │   │   │   │   ├── comm.txt
    │   │   │   │   ├── fd.txt
    │   │   │   │   ├── map_files.txt
    │   │   │   │   ├── mounts.txt
    │   │   │   │   ├── net
    │   │   │   │   │   └── unix.txt
    │   │   │   │   ├── stack.txt
    │   │   │   │   ├── stat.txt
    │   │   │   │   └── status.txt
    │   │   │   ├── 57794
    │   │   │   │   ├── comm.txt
    │   │   │   │   ├── fd.txt
    │   │   │   │   ├── map_files.txt
    │   │   │   │   ├── mounts.txt
    │   │   │   │   ├── net
    │   │   │   │   │   └── unix.txt
    │   │   │   │   ├── stack.txt
    │   │   │   │   ├── stat.txt
    │   │   │   │   └── status.txt
    │   │   │   ├── 57858
    │   │   │   │   ├── comm.txt
    │   │   │   │   ├── fd.txt
    │   │   │   │   ├── map_files.txt
    │   │   │   │   ├── mounts.txt
    │   │   │   │   ├── net
    │   │   │   │   │   └── unix.txt
    │   │   │   │   ├── stack.txt
    │   │   │   │   ├── stat.txt
    │   │   │   │   └── status.txt
    │   │   │   ├── 58
    │   │   │   │   ├── comm.txt
    │   │   │   │   ├── fd.txt
    │   │   │   │   ├── map_files.txt
    │   │   │   │   ├── mounts.txt
    │   │   │   │   ├── net
    │   │   │   │   │   └── unix.txt
    │   │   │   │   ├── stack.txt
    │   │   │   │   ├── stat.txt
    │   │   │   │   └── status.txt
    │   │   │   ├── 59
    │   │   │   │   ├── comm.txt
    │   │   │   │   ├── fd.txt
    │   │   │   │   ├── map_files.txt
    │   │   │   │   ├── mounts.txt
    │   │   │   │   ├── net
    │   │   │   │   │   └── unix.txt
    │   │   │   │   ├── stack.txt
    │   │   │   │   ├── stat.txt
    │   │   │   │   └── status.txt
    │   │   │   ├── 594
    │   │   │   │   ├── cmdline.txt
    │   │   │   │   ├── comm.txt
    │   │   │   │   ├── environ.txt
    │   │   │   │   ├── fd.txt
    │   │   │   │   ├── map_files.txt
    │   │   │   │   ├── maps.txt
    │   │   │   │   ├── mounts.txt
    │   │   │   │   ├── net
    │   │   │   │   │   └── unix.txt
    │   │   │   │   ├── stack.txt
    │   │   │   │   ├── stat.txt
    │   │   │   │   ├── status.txt
    │   │   │   │   └── strings.txt.gz
    │   │   │   ├── 598
    │   │   │   │   ├── cmdline.txt
    │   │   │   │   ├── comm.txt
    │   │   │   │   ├── environ.txt
    │   │   │   │   ├── fd.txt
    │   │   │   │   ├── map_files.txt
    │   │   │   │   ├── maps.txt
    │   │   │   │   ├── mounts.txt
    │   │   │   │   ├── net
    │   │   │   │   │   └── unix.txt
    │   │   │   │   ├── stack.txt
    │   │   │   │   ├── stat.txt
    │   │   │   │   ├── status.txt
    │   │   │   │   └── strings.txt.gz
    │   │   │   ├── 599
    │   │   │   │   ├── cmdline.txt
    │   │   │   │   ├── comm.txt
    │   │   │   │   ├── environ.txt
    │   │   │   │   ├── fd.txt
    │   │   │   │   ├── map_files.txt
    │   │   │   │   ├── maps.txt
    │   │   │   │   ├── mounts.txt
    │   │   │   │   ├── net
    │   │   │   │   │   └── unix.txt
    │   │   │   │   ├── stack.txt
    │   │   │   │   ├── stat.txt
    │   │   │   │   ├── status.txt
    │   │   │   │   └── strings.txt.gz
    │   │   │   ├── 6
    │   │   │   │   ├── comm.txt
    │   │   │   │   ├── fd.txt
    │   │   │   │   ├── map_files.txt
    │   │   │   │   ├── mounts.txt
    │   │   │   │   ├── net
    │   │   │   │   │   └── unix.txt
    │   │   │   │   ├── stack.txt
    │   │   │   │   ├── stat.txt
    │   │   │   │   └── status.txt
    │   │   │   ├── 60
    │   │   │   │   ├── comm.txt
    │   │   │   │   ├── fd.txt
    │   │   │   │   ├── map_files.txt
    │   │   │   │   ├── mounts.txt
    │   │   │   │   ├── net
    │   │   │   │   │   └── unix.txt
    │   │   │   │   ├── stack.txt
    │   │   │   │   ├── stat.txt
    │   │   │   │   └── status.txt
    │   │   │   ├── 605
    │   │   │   │   ├── cmdline.txt
    │   │   │   │   ├── comm.txt
    │   │   │   │   ├── environ.txt
    │   │   │   │   ├── fd.txt
    │   │   │   │   ├── map_files.txt
    │   │   │   │   ├── maps.txt
    │   │   │   │   ├── mounts.txt
    │   │   │   │   ├── net
    │   │   │   │   │   └── unix.txt
    │   │   │   │   ├── stack.txt
    │   │   │   │   ├── stat.txt
    │   │   │   │   ├── status.txt
    │   │   │   │   └── strings.txt.gz
    │   │   │   ├── 608
    │   │   │   │   ├── cmdline.txt
    │   │   │   │   ├── comm.txt
    │   │   │   │   ├── environ.txt
    │   │   │   │   ├── fd.txt
    │   │   │   │   ├── map_files.txt
    │   │   │   │   ├── maps.txt
    │   │   │   │   ├── mounts.txt
    │   │   │   │   ├── net
    │   │   │   │   │   └── unix.txt
    │   │   │   │   ├── stack.txt
    │   │   │   │   ├── stat.txt
    │   │   │   │   ├── status.txt
    │   │   │   │   └── strings.txt.gz
    │   │   │   ├── 61
    │   │   │   │   ├── comm.txt
    │   │   │   │   ├── fd.txt
    │   │   │   │   ├── map_files.txt
    │   │   │   │   ├── mounts.txt
    │   │   │   │   ├── net
    │   │   │   │   │   └── unix.txt
    │   │   │   │   ├── stack.txt
    │   │   │   │   ├── stat.txt
    │   │   │   │   └── status.txt
    │   │   │   ├── 611
    │   │   │   │   ├── cmdline.txt
    │   │   │   │   ├── comm.txt
    │   │   │   │   ├── environ.txt
    │   │   │   │   ├── fd.txt
    │   │   │   │   ├── map_files.txt
    │   │   │   │   ├── maps.txt
    │   │   │   │   ├── mounts.txt
    │   │   │   │   ├── net
    │   │   │   │   │   └── unix.txt
    │   │   │   │   ├── stack.txt
    │   │   │   │   ├── stat.txt
    │   │   │   │   ├── status.txt
    │   │   │   │   └── strings.txt.gz
    │   │   │   ├── 62
    │   │   │   │   ├── comm.txt
    │   │   │   │   ├── fd.txt
    │   │   │   │   ├── map_files.txt
    │   │   │   │   ├── mounts.txt
    │   │   │   │   ├── net
    │   │   │   │   │   └── unix.txt
    │   │   │   │   ├── stack.txt
    │   │   │   │   ├── stat.txt
    │   │   │   │   └── status.txt
    │   │   │   ├── 63
    │   │   │   │   ├── comm.txt
    │   │   │   │   ├── fd.txt
    │   │   │   │   ├── map_files.txt
    │   │   │   │   ├── mounts.txt
    │   │   │   │   ├── net
    │   │   │   │   │   └── unix.txt
    │   │   │   │   ├── stack.txt
    │   │   │   │   ├── stat.txt
    │   │   │   │   └── status.txt
    │   │   │   ├── 64
    │   │   │   │   ├── comm.txt
    │   │   │   │   ├── fd.txt
    │   │   │   │   ├── map_files.txt
    │   │   │   │   ├── mounts.txt
    │   │   │   │   ├── net
    │   │   │   │   │   └── unix.txt
    │   │   │   │   ├── stack.txt
    │   │   │   │   ├── stat.txt
    │   │   │   │   └── status.txt
    │   │   │   ├── 65
    │   │   │   │   ├── comm.txt
    │   │   │   │   ├── fd.txt
    │   │   │   │   ├── map_files.txt
    │   │   │   │   ├── mounts.txt
    │   │   │   │   ├── net
    │   │   │   │   │   └── unix.txt
    │   │   │   │   ├── stack.txt
    │   │   │   │   ├── stat.txt
    │   │   │   │   └── status.txt
    │   │   │   ├── 659
    │   │   │   │   ├── cmdline.txt
    │   │   │   │   ├── comm.txt
    │   │   │   │   ├── environ.txt
    │   │   │   │   ├── fd.txt
    │   │   │   │   ├── map_files.txt
    │   │   │   │   ├── maps.txt
    │   │   │   │   ├── mounts.txt
    │   │   │   │   ├── net
    │   │   │   │   │   └── unix.txt
    │   │   │   │   ├── stack.txt
    │   │   │   │   ├── stat.txt
    │   │   │   │   ├── status.txt
    │   │   │   │   └── strings.txt.gz
    │   │   │   ├── 66
    │   │   │   │   ├── comm.txt
    │   │   │   │   ├── fd.txt
    │   │   │   │   ├── map_files.txt
    │   │   │   │   ├── mounts.txt
    │   │   │   │   ├── net
    │   │   │   │   │   └── unix.txt
    │   │   │   │   ├── stack.txt
    │   │   │   │   ├── stat.txt
    │   │   │   │   └── status.txt
    │   │   │   ├── 678
    │   │   │   │   ├── cmdline.txt
    │   │   │   │   ├── comm.txt
    │   │   │   │   ├── environ.txt
    │   │   │   │   ├── fd.txt
    │   │   │   │   ├── map_files.txt
    │   │   │   │   ├── maps.txt
    │   │   │   │   ├── mounts.txt
    │   │   │   │   ├── net
    │   │   │   │   │   └── unix.txt
    │   │   │   │   ├── stack.txt
    │   │   │   │   ├── stat.txt
    │   │   │   │   ├── status.txt
    │   │   │   │   └── strings.txt.gz
    │   │   │   ├── 689
    │   │   │   │   ├── cmdline.txt
    │   │   │   │   ├── comm.txt
    │   │   │   │   ├── environ.txt
    │   │   │   │   ├── fd.txt
    │   │   │   │   ├── map_files.txt
    │   │   │   │   ├── maps.txt
    │   │   │   │   ├── mounts.txt
    │   │   │   │   ├── net
    │   │   │   │   │   └── unix.txt
    │   │   │   │   ├── stack.txt
    │   │   │   │   ├── stat.txt
    │   │   │   │   ├── status.txt
    │   │   │   │   └── strings.txt.gz
    │   │   │   ├── 69
    │   │   │   │   ├── comm.txt
    │   │   │   │   ├── fd.txt
    │   │   │   │   ├── map_files.txt
    │   │   │   │   ├── mounts.txt
    │   │   │   │   ├── net
    │   │   │   │   │   └── unix.txt
    │   │   │   │   ├── stack.txt
    │   │   │   │   ├── stat.txt
    │   │   │   │   └── status.txt
    │   │   │   ├── 7
    │   │   │   │   ├── comm.txt
    │   │   │   │   ├── fd.txt
    │   │   │   │   ├── map_files.txt
    │   │   │   │   ├── mounts.txt
    │   │   │   │   ├── net
    │   │   │   │   │   └── unix.txt
    │   │   │   │   ├── stack.txt
    │   │   │   │   ├── stat.txt
    │   │   │   │   └── status.txt
    │   │   │   ├── 70
    │   │   │   │   ├── comm.txt
    │   │   │   │   ├── fd.txt
    │   │   │   │   ├── map_files.txt
    │   │   │   │   ├── mounts.txt
    │   │   │   │   ├── net
    │   │   │   │   │   └── unix.txt
    │   │   │   │   ├── stack.txt
    │   │   │   │   ├── stat.txt
    │   │   │   │   └── status.txt
    │   │   │   ├── 70432
    │   │   │   │   ├── comm.txt
    │   │   │   │   ├── fd.txt
    │   │   │   │   ├── map_files.txt
    │   │   │   │   ├── mounts.txt
    │   │   │   │   ├── net
    │   │   │   │   │   └── unix.txt
    │   │   │   │   ├── stack.txt
    │   │   │   │   ├── stat.txt
    │   │   │   │   └── status.txt
    │   │   │   ├── 70456
    │   │   │   │   ├── comm.txt
    │   │   │   │   ├── fd.txt
    │   │   │   │   ├── map_files.txt
    │   │   │   │   ├── mounts.txt
    │   │   │   │   ├── net
    │   │   │   │   │   └── unix.txt
    │   │   │   │   ├── stack.txt
    │   │   │   │   ├── stat.txt
    │   │   │   │   └── status.txt
    │   │   │   ├── 70457
    │   │   │   │   ├── children.txt
    │   │   │   │   ├── cmdline.txt
    │   │   │   │   ├── comm.txt
    │   │   │   │   ├── fd.txt
    │   │   │   │   ├── map_files.txt
    │   │   │   │   ├── maps.txt
    │   │   │   │   ├── mounts.txt
    │   │   │   │   ├── net
    │   │   │   │   │   └── unix.txt
    │   │   │   │   ├── stack.txt
    │   │   │   │   ├── stat.txt
    │   │   │   │   ├── status.txt
    │   │   │   │   └── strings.txt.gz
    │   │   │   ├── 70475
    │   │   │   │   ├── comm.txt
    │   │   │   │   ├── fd.txt
    │   │   │   │   ├── map_files.txt
    │   │   │   │   ├── mounts.txt
    │   │   │   │   ├── net
    │   │   │   │   │   └── unix.txt
    │   │   │   │   ├── stack.txt
    │   │   │   │   ├── stat.txt
    │   │   │   │   └── status.txt
    │   │   │   ├── 70477
    │   │   │   │   ├── children.txt
    │   │   │   │   ├── cmdline.txt
    │   │   │   │   ├── comm.txt
    │   │   │   │   ├── environ.txt
    │   │   │   │   ├── fd.txt
    │   │   │   │   ├── map_files.txt
    │   │   │   │   ├── maps.txt
    │   │   │   │   ├── mounts.txt
    │   │   │   │   ├── net
    │   │   │   │   │   └── unix.txt
    │   │   │   │   ├── stack.txt
    │   │   │   │   ├── stat.txt
    │   │   │   │   ├── status.txt
    │   │   │   │   └── strings.txt.gz
    │   │   │   ├── 70479
    │   │   │   │   ├── comm.txt
    │   │   │   │   ├── fd.txt
    │   │   │   │   ├── map_files.txt
    │   │   │   │   ├── mounts.txt
    │   │   │   │   ├── net
    │   │   │   │   │   └── unix.txt
    │   │   │   │   ├── stack.txt
    │   │   │   │   ├── stat.txt
    │   │   │   │   └── status.txt
    │   │   │   ├── 70480
    │   │   │   │   ├── cmdline.txt
    │   │   │   │   ├── comm.txt
    │   │   │   │   ├── environ.txt
    │   │   │   │   ├── fd.txt
    │   │   │   │   ├── map_files.txt
    │   │   │   │   ├── maps.txt
    │   │   │   │   ├── mounts.txt
    │   │   │   │   ├── net
    │   │   │   │   │   └── unix.txt
    │   │   │   │   ├── stack.txt
    │   │   │   │   ├── stat.txt
    │   │   │   │   ├── status.txt
    │   │   │   │   └── strings.txt.gz
    │   │   │   ├── 70485
    │   │   │   │   ├── comm.txt
    │   │   │   │   ├── fd.txt
    │   │   │   │   ├── map_files.txt
    │   │   │   │   ├── mounts.txt
    │   │   │   │   ├── net
    │   │   │   │   │   └── unix.txt
    │   │   │   │   ├── stack.txt
    │   │   │   │   ├── stat.txt
    │   │   │   │   └── status.txt
    │   │   │   ├── 70545
    │   │   │   │   ├── children.txt
    │   │   │   │   ├── cmdline.txt
    │   │   │   │   ├── comm.txt
    │   │   │   │   ├── environ.txt
    │   │   │   │   ├── fd.txt
    │   │   │   │   ├── map_files.txt
    │   │   │   │   ├── maps.txt
    │   │   │   │   ├── mounts.txt
    │   │   │   │   ├── net
    │   │   │   │   │   └── unix.txt
    │   │   │   │   ├── stack.txt
    │   │   │   │   ├── stat.txt
    │   │   │   │   ├── status.txt
    │   │   │   │   └── strings.txt.gz
    │   │   │   ├── 70556
    │   │   │   │   ├── comm.txt
    │   │   │   │   ├── fd.txt
    │   │   │   │   ├── map_files.txt
    │   │   │   │   ├── mounts.txt
    │   │   │   │   ├── net
    │   │   │   │   │   └── unix.txt
    │   │   │   │   ├── stack.txt
    │   │   │   │   ├── stat.txt
    │   │   │   │   └── status.txt
    │   │   │   ├── 70608
    │   │   │   │   ├── children.txt
    │   │   │   │   ├── cmdline.txt
    │   │   │   │   ├── comm.txt
    │   │   │   │   ├── environ.txt
    │   │   │   │   ├── fd.txt
    │   │   │   │   ├── map_files.txt
    │   │   │   │   ├── maps.txt
    │   │   │   │   ├── mounts.txt
    │   │   │   │   ├── net
    │   │   │   │   │   └── unix.txt
    │   │   │   │   ├── stack.txt
    │   │   │   │   ├── stat.txt
    │   │   │   │   ├── status.txt
    │   │   │   │   └── strings.txt.gz
    │   │   │   ├── 71
    │   │   │   │   ├── comm.txt
    │   │   │   │   ├── fd.txt
    │   │   │   │   ├── map_files.txt
    │   │   │   │   ├── mounts.txt
    │   │   │   │   ├── net
    │   │   │   │   │   └── unix.txt
    │   │   │   │   ├── stack.txt
    │   │   │   │   ├── stat.txt
    │   │   │   │   └── status.txt
    │   │   │   ├── 717
    │   │   │   │   ├── cmdline.txt
    │   │   │   │   ├── comm.txt
    │   │   │   │   ├── environ.txt
    │   │   │   │   ├── fd.txt
    │   │   │   │   ├── map_files.txt
    │   │   │   │   ├── maps.txt
    │   │   │   │   ├── mounts.txt
    │   │   │   │   ├── net
    │   │   │   │   │   └── unix.txt
    │   │   │   │   ├── stack.txt
    │   │   │   │   ├── stat.txt
    │   │   │   │   ├── status.txt
    │   │   │   │   └── strings.txt.gz
    │   │   │   ├── 72378
    │   │   │   │   ├── children.txt
    │   │   │   │   ├── cmdline.txt
    │   │   │   │   ├── comm.txt
    │   │   │   │   ├── environ.txt
    │   │   │   │   ├── fd.txt
    │   │   │   │   ├── map_files.txt
    │   │   │   │   ├── maps.txt
    │   │   │   │   ├── mounts.txt
    │   │   │   │   ├── net
    │   │   │   │   │   └── unix.txt
    │   │   │   │   ├── stack.txt
    │   │   │   │   ├── stat.txt
    │   │   │   │   └── status.txt
    │   │   │   ├── 73028
    │   │   │   │   ├── comm.txt
    │   │   │   │   ├── map_files.txt
    │   │   │   │   ├── mounts.txt
    │   │   │   │   ├── net
    │   │   │   │   │   └── unix.txt
    │   │   │   │   ├── stack.txt
    │   │   │   │   ├── stat.txt
    │   │   │   │   └── status.txt
    │   │   │   ├── 763
    │   │   │   │   ├── cmdline.txt
    │   │   │   │   ├── comm.txt
    │   │   │   │   ├── environ.txt
    │   │   │   │   ├── fd.txt
    │   │   │   │   ├── map_files.txt
    │   │   │   │   ├── maps.txt
    │   │   │   │   ├── mounts.txt
    │   │   │   │   ├── net
    │   │   │   │   │   └── unix.txt
    │   │   │   │   ├── stack.txt
    │   │   │   │   ├── stat.txt
    │   │   │   │   ├── status.txt
    │   │   │   │   └── strings.txt.gz
    │   │   │   ├── 779
    │   │   │   │   ├── children.txt
    │   │   │   │   ├── cmdline.txt
    │   │   │   │   ├── comm.txt
    │   │   │   │   ├── environ.txt
    │   │   │   │   ├── fd.txt
    │   │   │   │   ├── map_files.txt
    │   │   │   │   ├── maps.txt
    │   │   │   │   ├── mounts.txt
    │   │   │   │   ├── net
    │   │   │   │   │   └── unix.txt
    │   │   │   │   ├── stack.txt
    │   │   │   │   ├── stat.txt
    │   │   │   │   ├── status.txt
    │   │   │   │   └── strings.txt.gz
    │   │   │   ├── 78
    │   │   │   │   ├── comm.txt
    │   │   │   │   ├── fd.txt
    │   │   │   │   ├── map_files.txt
    │   │   │   │   ├── mounts.txt
    │   │   │   │   ├── net
    │   │   │   │   │   └── unix.txt
    │   │   │   │   ├── stack.txt
    │   │   │   │   ├── stat.txt
    │   │   │   │   └── status.txt
    │   │   │   ├── 788
    │   │   │   │   ├── cmdline.txt
    │   │   │   │   ├── comm.txt
    │   │   │   │   ├── environ.txt
    │   │   │   │   ├── fd.txt
    │   │   │   │   ├── map_files.txt
    │   │   │   │   ├── maps.txt
    │   │   │   │   ├── mounts.txt
    │   │   │   │   ├── net
    │   │   │   │   │   └── unix.txt
    │   │   │   │   ├── stack.txt
    │   │   │   │   ├── stat.txt
    │   │   │   │   ├── status.txt
    │   │   │   │   └── strings.txt.gz
    │   │   │   ├── 8
    │   │   │   │   ├── comm.txt
    │   │   │   │   ├── fd.txt
    │   │   │   │   ├── map_files.txt
    │   │   │   │   ├── mounts.txt
    │   │   │   │   ├── net
    │   │   │   │   │   └── unix.txt
    │   │   │   │   ├── stack.txt
    │   │   │   │   ├── stat.txt
    │   │   │   │   └── status.txt
    │   │   │   ├── 80
    │   │   │   │   ├── comm.txt
    │   │   │   │   ├── fd.txt
    │   │   │   │   ├── map_files.txt
    │   │   │   │   ├── mounts.txt
    │   │   │   │   ├── net
    │   │   │   │   │   └── unix.txt
    │   │   │   │   ├── stack.txt
    │   │   │   │   ├── stat.txt
    │   │   │   │   └── status.txt
    │   │   │   ├── 844
    │   │   │   │   ├── cmdline.txt
    │   │   │   │   ├── comm.txt
    │   │   │   │   ├── environ.txt
    │   │   │   │   ├── fd.txt
    │   │   │   │   ├── map_files.txt
    │   │   │   │   ├── maps.txt
    │   │   │   │   ├── mounts.txt
    │   │   │   │   ├── net
    │   │   │   │   │   └── unix.txt
    │   │   │   │   ├── stack.txt
    │   │   │   │   ├── stat.txt
    │   │   │   │   ├── status.txt
    │   │   │   │   └── strings.txt.gz
    │   │   │   ├── 865
    │   │   │   │   ├── cmdline.txt
    │   │   │   │   ├── comm.txt
    │   │   │   │   ├── environ.txt
    │   │   │   │   ├── fd.txt
    │   │   │   │   ├── map_files.txt
    │   │   │   │   ├── maps.txt
    │   │   │   │   ├── mounts.txt
    │   │   │   │   ├── net
    │   │   │   │   │   └── unix.txt
    │   │   │   │   ├── stack.txt
    │   │   │   │   ├── stat.txt
    │   │   │   │   ├── status.txt
    │   │   │   │   └── strings.txt.gz
    │   │   │   ├── 871
    │   │   │   │   ├── cmdline.txt
    │   │   │   │   ├── comm.txt
    │   │   │   │   ├── environ.txt
    │   │   │   │   ├── fd.txt
    │   │   │   │   ├── map_files.txt
    │   │   │   │   ├── maps.txt
    │   │   │   │   ├── mounts.txt
    │   │   │   │   ├── net
    │   │   │   │   │   └── unix.txt
    │   │   │   │   ├── stack.txt
    │   │   │   │   ├── stat.txt
    │   │   │   │   ├── status.txt
    │   │   │   │   └── strings.txt.gz
    │   │   │   ├── 93
    │   │   │   │   ├── comm.txt
    │   │   │   │   ├── fd.txt
    │   │   │   │   ├── map_files.txt
    │   │   │   │   ├── mounts.txt
    │   │   │   │   ├── net
    │   │   │   │   │   └── unix.txt
    │   │   │   │   ├── stack.txt
    │   │   │   │   ├── stat.txt
    │   │   │   │   └── status.txt
    │   │   │   ├── 94
    │   │   │   │   ├── comm.txt
    │   │   │   │   ├── fd.txt
    │   │   │   │   ├── map_files.txt
    │   │   │   │   ├── mounts.txt
    │   │   │   │   ├── net
    │   │   │   │   │   └── unix.txt
    │   │   │   │   ├── stack.txt
    │   │   │   │   ├── stat.txt
    │   │   │   │   └── status.txt
    │   │   │   ├── 95
    │   │   │   │   ├── comm.txt
    │   │   │   │   ├── fd.txt
    │   │   │   │   ├── map_files.txt
    │   │   │   │   ├── mounts.txt
    │   │   │   │   ├── net
    │   │   │   │   │   └── unix.txt
    │   │   │   │   ├── stack.txt
    │   │   │   │   ├── stat.txt
    │   │   │   │   └── status.txt
    │   │   │   ├── 970
    │   │   │   │   ├── cmdline.txt
    │   │   │   │   ├── comm.txt
    │   │   │   │   ├── environ.txt
    │   │   │   │   ├── fd.txt
    │   │   │   │   ├── map_files.txt
    │   │   │   │   ├── maps.txt
    │   │   │   │   ├── mounts.txt
    │   │   │   │   ├── net
    │   │   │   │   │   └── unix.txt
    │   │   │   │   ├── stack.txt
    │   │   │   │   ├── stat.txt
    │   │   │   │   ├── status.txt
    │   │   │   │   └── strings.txt.gz
    │   │   │   └── modules.txt
    │   │   ├── ps_auxwwwf.txt
    │   │   ├── ps_auxwww.txt
    │   │   ├── ps_-axo_pid_user_cgroup.txt
    │   │   ├── ps_-axo_pid_user_etime_args.txt
    │   │   ├── ps_-axo_pid_user_lstart_args.txt
    │   │   ├── ps_-deaf.txt
    │   │   ├── ps_-efl.txt
    │   │   ├── ps_-ef.txt
    │   │   ├── pstree_-a.txt
    │   │   ├── pstree_-p_-n.txt
    │   │   ├── pstree.txt
    │   │   ├── ps.txt
    │   │   ├── running_processes_full_paths.txt
    │   │   └── top_-b_-n1.txt
    │   ├── storage
    │   │   ├── blkid.txt
    │   │   ├── cat_proc_mdstat.txt
    │   │   ├── df_-h.txt
    │   │   ├── df.txt
    │   │   ├── fdisk_-l.txt
    │   │   ├── findmnt_-J.txt
    │   │   ├── findmnt.txt
    │   │   ├── lsblk_-f_-J.txt
    │   │   ├── lsblk_-f.txt
    │   │   ├── lsblk_-J.txt
    │   │   ├── lsblk_-l_-J.txt
    │   │   ├── lsblk_-l.txt
    │   │   ├── lsblk.txt
    │   │   ├── ls_-l_dev_disk.txt
    │   │   └── mount.txt
    │   └── system
    │       ├── cat_proc_sys_kernel_tainted.txt
    │       ├── core_pattern.txt
    │       ├── date.txt
    │       ├── env.txt
    │       ├── free.txt
    │       ├── journalctl_--list-boots.txt
    │       ├── last_-a_-F_-f_var_log_wtmp.txt
    │       ├── last_-a_-F.txt
    │       ├── lastb_-a_-F_-f_var_log_btmp.txt
    │       ├── lastb_-a_-F.txt
    │       ├── lastb_-i.txt
    │       ├── lastb.txt
    │       ├── last_-i.txt
    │       ├── lastlog.txt
    │       ├── last.txt
    │       ├── loginctl_user-status_root.txt
    │       ├── ls_-la_sys_fs_bpf.txt
    │       ├── ls_-la_sys_module.txt
    │       ├── lsmod.txt
    │       ├── modinfo
    │       │   ├── modinfo_8021q.txt
    │       │   ├── modinfo_aesni_intel.txt
    │       │   ├── modinfo_af_packet_diag.txt
    │       │   ├── modinfo_autofs4.txt
    │       │   ├── modinfo_binfmt_misc.txt
    │       │   ├── modinfo_cryptd.txt
    │       │   ├── modinfo_crypto_simd.txt
    │       │   ├── modinfo_dm_multipath.txt
    │       │   ├── modinfo_efi_pstore.txt
    │       │   ├── modinfo_floppy.txt
    │       │   ├── modinfo_garp.txt
    │       │   ├── modinfo_ghash_clmulni_intel.txt
    │       │   ├── modinfo_ib_core.txt
    │       │   ├── modinfo_inet_diag.txt
    │       │   ├── modinfo_input_leds.txt
    │       │   ├── modinfo_ip_tables.txt
    │       │   ├── modinfo_llc.txt
    │       │   ├── modinfo_mrp.txt
    │       │   ├── modinfo_msr.txt
    │       │   ├── modinfo_netlink_diag.txt
    │       │   ├── modinfo_nf_conntrack.txt
    │       │   ├── modinfo_nf_defrag_ipv4.txt
    │       │   ├── modinfo_nf_defrag_ipv6.txt
    │       │   ├── modinfo_nfnetlink.txt
    │       │   ├── modinfo_nf_tables.txt
    │       │   ├── modinfo_nls_iso8859_1.txt
    │       │   ├── modinfo_polyval_clmulni.txt
    │       │   ├── modinfo_polyval_generic.txt
    │       │   ├── modinfo_psmouse.txt
    │       │   ├── modinfo_raw_diag.txt
    │       │   ├── modinfo_sch_fq_codel.txt
    │       │   ├── modinfo_serio_raw.txt
    │       │   ├── modinfo_sha1_ssse3.txt
    │       │   ├── modinfo_sha256_ssse3.txt
    │       │   ├── modinfo_stp.txt
    │       │   ├── modinfo_tcp_diag.txt
    │       │   ├── modinfo_tls.txt
    │       │   ├── modinfo_udp_diag.txt
    │       │   ├── modinfo_unix_diag.txt
    │       │   ├── modinfo_vga16fb.txt
    │       │   ├── modinfo_vgastate.txt
    │       │   └── modinfo_x_tables.txt
    │       ├── module
    │       │   ├── 8250
    │       │   │   └── parameters.txt
    │       │   ├── acpi
    │       │   │   └── parameters.txt
    │       │   ├── acpi_cpufreq
    │       │   │   └── parameters.txt
    │       │   ├── acpiphp
    │       │   │   └── parameters.txt
    │       │   ├── apparmor
    │       │   │   └── parameters.txt
    │       │   ├── battery
    │       │   │   └── parameters.txt
    │       │   ├── blk_cgroup
    │       │   │   └── parameters.txt
    │       │   ├── blk_crypto
    │       │   │   └── parameters.txt
    │       │   ├── block
    │       │   │   └── parameters.txt
    │       │   ├── button
    │       │   │   └── parameters.txt
    │       │   ├── clocksource
    │       │   │   └── parameters.txt
    │       │   ├── cpufreq
    │       │   │   └── parameters.txt
    │       │   ├── cpuidle
    │       │   │   └── parameters.txt
    │       │   ├── crc64_rocksoft
    │       │   │   └── parameters.txt
    │       │   ├── cryptomgr
    │       │   │   └── parameters.txt
    │       │   ├── debug_core
    │       │   │   └── parameters.txt
    │       │   ├── device_hmem
    │       │   │   └── parameters.txt
    │       │   ├── dm_mod
    │       │   │   └── parameters.txt
    │       │   ├── dm_multipath
    │       │   │   └── parameters.txt
    │       │   ├── dns_resolver
    │       │   │   └── parameters.txt
    │       │   ├── drm
    │       │   │   └── parameters.txt
    │       │   ├── drm_client_lib
    │       │   │   └── parameters.txt
    │       │   ├── drm_kms_helper
    │       │   │   └── parameters.txt
    │       │   ├── dynamic_debug
    │       │   │   └── parameters.txt
    │       │   ├── edac_core
    │       │   │   └── parameters.txt
    │       │   ├── efi_pstore
    │       │   │   └── parameters.txt
    │       │   ├── ehci_hcd
    │       │   │   └── parameters.txt
    │       │   ├── fb
    │       │   │   └── parameters.txt
    │       │   ├── firmware_class
    │       │   │   └── parameters.txt
    │       │   ├── fscrypto
    │       │   │   └── parameters.txt
    │       │   ├── fuse
    │       │   │   └── parameters.txt
    │       │   ├── garp
    │       │   │   └── parameters.txt
    │       │   ├── gpiolib_acpi
    │       │   │   └── parameters.txt
    │       │   ├── grant_table
    │       │   │   └── parameters.txt
    │       │   ├── haltpoll
    │       │   │   └── parameters.txt
    │       │   ├── hibernate
    │       │   │   └── parameters.txt
    │       │   ├── i8042
    │       │   │   └── parameters.txt
    │       │   ├── ib_core
    │       │   │   └── parameters.txt
    │       │   ├── ima
    │       │   │   └── parameters.txt
    │       │   ├── intel_idle
    │       │   │   └── parameters.txt
    │       │   ├── ipe
    │       │   │   └── parameters.txt
    │       │   ├── ipv6
    │       │   │   └── parameters.txt
    │       │   ├── kdb
    │       │   │   └── parameters.txt
    │       │   ├── kernel
    │       │   │   └── parameters.txt
    │       │   ├── keyboard
    │       │   │   └── parameters.txt
    │       │   ├── kfence
    │       │   │   └── parameters.txt
    │       │   ├── kgdboc
    │       │   │   └── parameters.txt
    │       │   ├── libata
    │       │   │   └── parameters.txt
    │       │   ├── libnvdimm
    │       │   │   └── parameters.txt
    │       │   ├── loop
    │       │   │   └── parameters.txt
    │       │   ├── md_mod
    │       │   │   └── parameters.txt
    │       │   ├── memory_hotplug
    │       │   │   └── parameters.txt
    │       │   ├── microcode
    │       │   │   └── parameters.txt
    │       │   ├── module
    │       │   │   └── parameters.txt
    │       │   ├── mousedev
    │       │   │   └── parameters.txt
    │       │   ├── mrp
    │       │   │   └── parameters.txt
    │       │   ├── msr
    │       │   │   └── parameters.txt
    │       │   ├── netpoll
    │       │   │   └── parameters.txt
    │       │   ├── nf_conntrack
    │       │   │   └── parameters.txt
    │       │   ├── nmi_backtrace
    │       │   │   └── parameters.txt
    │       │   ├── nvme
    │       │   │   └── parameters.txt
    │       │   ├── nvme_core
    │       │   │   └── parameters.txt
    │       │   ├── page_alloc
    │       │   │   └── parameters.txt
    │       │   ├── page_reporting
    │       │   │   └── parameters.txt
    │       │   ├── pcie_aspm
    │       │   │   └── parameters.txt
    │       │   ├── pciehp
    │       │   │   └── parameters.txt
    │       │   ├── pci_hotplug
    │       │   │   └── parameters.txt
    │       │   ├── ppp_generic
    │       │   │   └── parameters.txt
    │       │   ├── printk
    │       │   │   └── parameters.txt
    │       │   ├── processor
    │       │   │   └── parameters.txt
    │       │   ├── psmouse
    │       │   │   └── parameters.txt
    │       │   ├── pstore
    │       │   │   └── parameters.txt
    │       │   ├── random
    │       │   │   └── parameters.txt
    │       │   ├── rcupdate
    │       │   │   └── parameters.txt
    │       │   ├── rcutree
    │       │   │   └── parameters.txt
    │       │   ├── rfkill
    │       │   │   └── parameters.txt
    │       │   ├── rng_core
    │       │   │   └── parameters.txt
    │       │   ├── rtc_cmos
    │       │   │   └── parameters.txt
    │       │   ├── scsi_mod
    │       │   │   └── parameters.txt
    │       │   ├── secretmem
    │       │   │   └── parameters.txt
    │       │   ├── sg
    │       │   │   └── parameters.txt
    │       │   ├── shpchp
    │       │   │   └── parameters.txt
    │       │   ├── slab_common
    │       │   │   └── parameters.txt
    │       │   ├── spurious
    │       │   │   └── parameters.txt
    │       │   ├── srcutree
    │       │   │   └── parameters.txt
    │       │   ├── sr_mod
    │       │   │   └── parameters.txt
    │       │   ├── sysrq
    │       │   │   └── parameters.txt
    │       │   ├── tcp_cubic
    │       │   │   └── parameters.txt
    │       │   ├── thermal
    │       │   │   └── parameters.txt
    │       │   ├── tpm
    │       │   │   └── parameters.txt
    │       │   ├── tpm_tis
    │       │   │   └── parameters.txt
    │       │   ├── udmabuf
    │       │   │   └── parameters.txt
    │       │   ├── uhci_hcd
    │       │   │   └── parameters.txt
    │       │   ├── usbcore
    │       │   │   └── parameters.txt
    │       │   ├── uv_nmi
    │       │   │   └── parameters.txt
    │       │   ├── virtio_blk
    │       │   │   └── parameters.txt
    │       │   ├── virtio_mmio
    │       │   │   └── parameters.txt
    │       │   ├── virtio_net
    │       │   │   └── parameters.txt
    │       │   ├── virtio_pci
    │       │   │   └── parameters.txt
    │       │   ├── virtio_scsi
    │       │   │   └── parameters.txt
    │       │   ├── vt
    │       │   │   └── parameters.txt
    │       │   ├── watchdog
    │       │   │   └── parameters.txt
    │       │   ├── workqueue
    │       │   │   └── parameters.txt
    │       │   ├── xen
    │       │   │   └── parameters.txt
    │       │   ├── xen_acpi_processor
    │       │   │   └── parameters.txt
    │       │   ├── xen_blkfront
    │       │   │   └── parameters.txt
    │       │   ├── xen_netfront
    │       │   │   └── parameters.txt
    │       │   ├── xhci_hcd
    │       │   │   └── parameters.txt
    │       │   └── zswap
    │       │       └── parameters.txt
    │       ├── runlevel.txt
    │       ├── service_--status-all.txt
    │       ├── socket_files.txt
    │       ├── sudo_lectured_timestamps.txt
    │       ├── sysctl_-a.txt
    │       ├── systemctl_list-timers_--all.txt
    │       ├── systemctl_list-unit-files.txt
    │       ├── systemctl_list-units.txt
    │       ├── systemctl_status_timer.txt
    │       ├── timedatectl_status.txt
    │       ├── ulimit_-a.txt
    │       ├── uname_-a.txt
    │       ├── uptime_-s.txt
    │       ├── uptime.txt
    │       ├── utmpdump_var_log_wtmp.txt
    │       ├── vmstat.txt
    │       └── who_-T.txt
    ├── [root]
    │   ├── etc
    │   │   ├── acpi
    │   │   │   ├── actions
    │   │   │   │   ├── hibinit-power.sh
    │   │   │   │   └── sleep.sh
    │   │   │   └── events
    │   │   │       ├── hibinit-power
    │   │   │       └── hibinit-sleep
    │   │   ├── adduser.conf
    │   │   ├── alternatives
    │   │   │   ├── arptables
    │   │   │   ├── arptables-restore
    │   │   │   ├── arptables-save
    │   │   │   ├── awk
    │   │   │   ├── awk.1.gz
    │   │   │   ├── builtins.7.gz
    │   │   │   ├── ebtables
    │   │   │   ├── ebtables-restore
    │   │   │   ├── ebtables-save
    │   │   │   ├── editor
    │   │   │   ├── editor.1.gz
    │   │   │   ├── ex
    │   │   │   ├── ex.1.gz
    │   │   │   ├── ex.da.1.gz
    │   │   │   ├── ex.de.1.gz
    │   │   │   ├── ex.fr.1.gz
    │   │   │   ├── ex.it.1.gz
    │   │   │   ├── ex.ja.1.gz
    │   │   │   ├── ex.pl.1.gz
    │   │   │   ├── ex.ru.1.gz
    │   │   │   ├── ex.tr.1.gz
    │   │   │   ├── ftp
    │   │   │   ├── ftp.1.gz
    │   │   │   ├── infobrowser
    │   │   │   ├── infobrowser.1.gz
    │   │   │   ├── ip6tables
    │   │   │   ├── ip6tables-restore
    │   │   │   ├── ip6tables-save
    │   │   │   ├── iptables
    │   │   │   ├── iptables-restore
    │   │   │   ├── iptables-save
    │   │   │   ├── jsondiff
    │   │   │   ├── lzcat
    │   │   │   ├── lzcat.1.gz
    │   │   │   ├── lzcmp
    │   │   │   ├── lzcmp.1.gz
    │   │   │   ├── lzdiff
    │   │   │   ├── lzdiff.1.gz
    │   │   │   ├── lzegrep
    │   │   │   ├── lzegrep.1.gz
    │   │   │   ├── lzfgrep
    │   │   │   ├── lzfgrep.1.gz
    │   │   │   ├── lzgrep
    │   │   │   ├── lzgrep.1.gz
    │   │   │   ├── lzless
    │   │   │   ├── lzless.1.gz
    │   │   │   ├── lzma
    │   │   │   ├── lzma.1.gz
    │   │   │   ├── lzmore
    │   │   │   ├── lzmore.1.gz
    │   │   │   ├── mt
    │   │   │   ├── mt.1.gz
    │   │   │   ├── nawk
    │   │   │   ├── nawk.1.gz
    │   │   │   ├── nc
    │   │   │   ├── nc.1.gz
    │   │   │   ├── netcat
    │   │   │   ├── netcat.1.gz
    │   │   │   ├── newt-palette
    │   │   │   ├── pager
    │   │   │   ├── pager.1.gz
    │   │   │   ├── pico
    │   │   │   ├── pico.1.gz
    │   │   │   ├── pinentry
    │   │   │   ├── pinentry.1.gz
    │   │   │   ├── pybabel
    │   │   │   ├── README
    │   │   │   ├── rmt
    │   │   │   ├── rmt.8.gz
    │   │   │   ├── rview
    │   │   │   ├── rvim
    │   │   │   ├── sar
    │   │   │   ├── sar.1.gz
    │   │   │   ├── shimx64.efi.signed
    │   │   │   ├── telnet
    │   │   │   ├── telnet.1.gz
    │   │   │   ├── text.plymouth
    │   │   │   ├── unlzma
    │   │   │   ├── unlzma.1.gz
    │   │   │   ├── vi
    │   │   │   ├── vi.1.gz
    │   │   │   ├── vi.da.1.gz
    │   │   │   ├── vi.de.1.gz
    │   │   │   ├── view
    │   │   │   ├── view.1.gz
    │   │   │   ├── view.da.1.gz
    │   │   │   ├── view.de.1.gz
    │   │   │   ├── view.fr.1.gz
    │   │   │   ├── view.it.1.gz
    │   │   │   ├── view.ja.1.gz
    │   │   │   ├── view.pl.1.gz
    │   │   │   ├── view.ru.1.gz
    │   │   │   ├── view.tr.1.gz
    │   │   │   ├── vi.fr.1.gz
    │   │   │   ├── vi.it.1.gz
    │   │   │   ├── vi.ja.1.gz
    │   │   │   ├── vim
    │   │   │   ├── vimdiff
    │   │   │   ├── vi.pl.1.gz
    │   │   │   ├── vi.ru.1.gz
    │   │   │   ├── vi.tr.1.gz
    │   │   │   ├── vtrgb
    │   │   │   ├── which
    │   │   │   ├── which.1.gz
    │   │   │   ├── which.de1.gz
    │   │   │   ├── which.es1.gz
    │   │   │   ├── which.fr1.gz
    │   │   │   ├── which.it1.gz
    │   │   │   ├── which.ja1.gz
    │   │   │   ├── which.pl1.gz
    │   │   │   └── which.sl1.gz
    │   │   ├── apparmor
    │   │   │   └── parser.conf
    │   │   ├── apparmor.d
    │   │   │   ├── 1password
    │   │   │   ├── abi
    │   │   │   │   ├── 3.0
    │   │   │   │   ├── 4.0
    │   │   │   │   ├── kernel-5.4-outoftree-network
    │   │   │   │   └── kernel-5.4-vanilla
    │   │   │   ├── abstractions
    │   │   │   │   ├── apache2-common
    │   │   │   │   ├── apparmor_api
    │   │   │   │   │   ├── change_profile
    │   │   │   │   │   ├── examine
    │   │   │   │   │   ├── find_mountpoint
    │   │   │   │   │   ├── introspect
    │   │   │   │   │   └── is_enabled
    │   │   │   │   ├── aspell
    │   │   │   │   ├── audio
    │   │   │   │   ├── authentication
    │   │   │   │   ├── base
    │   │   │   │   ├── bash
    │   │   │   │   ├── consoles
    │   │   │   │   ├── crypto
    │   │   │   │   ├── cups-client
    │   │   │   │   ├── dbus
    │   │   │   │   ├── dbus-accessibility
    │   │   │   │   ├── dbus-accessibility-strict
    │   │   │   │   ├── dbus-network-manager-strict
    │   │   │   │   ├── dbus-session
    │   │   │   │   ├── dbus-session-strict
    │   │   │   │   ├── dbus-strict
    │   │   │   │   ├── dconf
    │   │   │   │   ├── dovecot-common
    │   │   │   │   ├── dri-common
    │   │   │   │   ├── dri-enumerate
    │   │   │   │   ├── enchant
    │   │   │   │   ├── exo-open
    │   │   │   │   ├── fcitx
    │   │   │   │   ├── fcitx-strict
    │   │   │   │   ├── fonts
    │   │   │   │   ├── freedesktop.org
    │   │   │   │   ├── gio-open
    │   │   │   │   ├── gnome
    │   │   │   │   ├── gnupg
    │   │   │   │   ├── groff
    │   │   │   │   ├── gtk
    │   │   │   │   ├── gvfs-open
    │   │   │   │   ├── hosts_access
    │   │   │   │   ├── ibus
    │   │   │   │   ├── kde
    │   │   │   │   ├── kde-globals-write
    │   │   │   │   ├── kde-icon-cache-write
    │   │   │   │   ├── kde-language-write
    │   │   │   │   ├── kde-open5
    │   │   │   │   ├── kerberosclient
    │   │   │   │   ├── ldapclient
    │   │   │   │   ├── libpam-systemd
    │   │   │   │   ├── likewise
    │   │   │   │   ├── mdns
    │   │   │   │   ├── mesa
    │   │   │   │   ├── mir
    │   │   │   │   ├── mozc
    │   │   │   │   ├── mysql
    │   │   │   │   ├── nameservice
    │   │   │   │   ├── nis
    │   │   │   │   ├── nss-systemd
    │   │   │   │   ├── nvidia
    │   │   │   │   ├── opencl
    │   │   │   │   ├── opencl-common
    │   │   │   │   ├── opencl-intel
    │   │   │   │   ├── opencl-mesa
    │   │   │   │   ├── opencl-nvidia
    │   │   │   │   ├── opencl-pocl
    │   │   │   │   ├── openssl
    │   │   │   │   ├── orbit2
    │   │   │   │   ├── p11-kit
    │   │   │   │   ├── perl
    │   │   │   │   ├── php
    │   │   │   │   ├── php5
    │   │   │   │   ├── php-worker
    │   │   │   │   ├── postfix-common
    │   │   │   │   ├── private-files
    │   │   │   │   ├── private-files-strict
    │   │   │   │   ├── python
    │   │   │   │   ├── qt5
    │   │   │   │   ├── qt5-compose-cache-write
    │   │   │   │   ├── qt5-settings-write
    │   │   │   │   ├── recent-documents-write
    │   │   │   │   ├── ruby
    │   │   │   │   ├── samba
    │   │   │   │   ├── samba-rpcd
    │   │   │   │   ├── smbpass
    │   │   │   │   ├── snap_browsers
    │   │   │   │   ├── ssl_certs
    │   │   │   │   ├── ssl_keys
    │   │   │   │   ├── svn-repositories
    │   │   │   │   ├── transmission-common
    │   │   │   │   ├── trash
    │   │   │   │   ├── ubuntu-bittorrent-clients
    │   │   │   │   ├── ubuntu-browsers
    │   │   │   │   ├── ubuntu-browsers.d
    │   │   │   │   │   ├── chromium-browser
    │   │   │   │   │   ├── java
    │   │   │   │   │   ├── kde
    │   │   │   │   │   ├── mailto
    │   │   │   │   │   ├── multimedia
    │   │   │   │   │   ├── plugins-common
    │   │   │   │   │   ├── productivity
    │   │   │   │   │   ├── text-editors
    │   │   │   │   │   ├── ubuntu-integration
    │   │   │   │   │   ├── ubuntu-integration-xul
    │   │   │   │   │   └── user-files
    │   │   │   │   ├── ubuntu-console-browsers
    │   │   │   │   ├── ubuntu-console-email
    │   │   │   │   ├── ubuntu-email
    │   │   │   │   ├── ubuntu-feed-readers
    │   │   │   │   ├── ubuntu-gnome-terminal
    │   │   │   │   ├── ubuntu-helpers
    │   │   │   │   ├── ubuntu-konsole
    │   │   │   │   ├── ubuntu-media-players
    │   │   │   │   ├── ubuntu-unity7-base
    │   │   │   │   ├── ubuntu-unity7-launcher
    │   │   │   │   ├── ubuntu-unity7-messaging
    │   │   │   │   ├── ubuntu-xterm
    │   │   │   │   ├── user-download
    │   │   │   │   ├── user-mail
    │   │   │   │   ├── user-manpages
    │   │   │   │   ├── user-tmp
    │   │   │   │   ├── user-write
    │   │   │   │   ├── video
    │   │   │   │   ├── vulkan
    │   │   │   │   ├── wayland
    │   │   │   │   ├── web-data
    │   │   │   │   ├── winbind
    │   │   │   │   ├── wutmp
    │   │   │   │   ├── X
    │   │   │   │   ├── xad
    │   │   │   │   ├── xdg-desktop
    │   │   │   │   └── xdg-open
    │   │   │   ├── balena-etcher
    │   │   │   ├── brave
    │   │   │   ├── buildah
    │   │   │   ├── busybox
    │   │   │   ├── cam
    │   │   │   ├── ch-checkns
    │   │   │   ├── chrome
    │   │   │   ├── ch-run
    │   │   │   ├── code
    │   │   │   ├── crun
    │   │   │   ├── devhelp
    │   │   │   ├── Discord
    │   │   │   ├── element-desktop
    │   │   │   ├── epiphany
    │   │   │   ├── evolution
    │   │   │   ├── firefox
    │   │   │   ├── flatpak
    │   │   │   ├── foliate
    │   │   │   ├── geary
    │   │   │   ├── github-desktop
    │   │   │   ├── goldendict
    │   │   │   ├── ipa_verify
    │   │   │   ├── kchmviewer
    │   │   │   ├── keybase
    │   │   │   ├── lc-compliance
    │   │   │   ├── libcamerify
    │   │   │   ├── linux-sandbox
    │   │   │   ├── local
    │   │   │   │   ├── lsb_release
    │   │   │   │   ├── nvidia_modprobe
    │   │   │   │   ├── README
    │   │   │   │   ├── ubuntu_pro_apt_news
    │   │   │   │   ├── ubuntu_pro_esm_cache
    │   │   │   │   ├── usr.bin.man
    │   │   │   │   ├── usr.bin.tcpdump
    │   │   │   │   ├── usr.lib.snapd.snap-confine.real
    │   │   │   │   ├── usr.sbin.chronyd
    │   │   │   │   └── usr.sbin.rsyslogd
    │   │   │   ├── loupe
    │   │   │   ├── lsb_release
    │   │   │   ├── lxc-attach
    │   │   │   ├── lxc-create
    │   │   │   ├── lxc-destroy
    │   │   │   ├── lxc-execute
    │   │   │   ├── lxc-stop
    │   │   │   ├── lxc-unshare
    │   │   │   ├── lxc-usernsexec
    │   │   │   ├── mmdebstrap
    │   │   │   ├── MongoDB_Compass
    │   │   │   ├── msedge
    │   │   │   ├── nautilus
    │   │   │   ├── notepadqq
    │   │   │   ├── nvidia_modprobe
    │   │   │   ├── obsidian
    │   │   │   ├── opam
    │   │   │   ├── opera
    │   │   │   ├── pageedit
    │   │   │   ├── plasmashell
    │   │   │   ├── podman
    │   │   │   ├── polypane
    │   │   │   ├── privacybrowser
    │   │   │   ├── qcam
    │   │   │   ├── qmapshack
    │   │   │   ├── QtWebEngineProcess
    │   │   │   ├── qutebrowser
    │   │   │   ├── rootlesskit
    │   │   │   ├── rpm
    │   │   │   ├── rssguard
    │   │   │   ├── rsyslog.d
    │   │   │   │   └── README
    │   │   │   ├── runc
    │   │   │   ├── sbuild
    │   │   │   ├── sbuild-abort
    │   │   │   ├── sbuild-adduser
    │   │   │   ├── sbuild-apt
    │   │   │   ├── sbuild-checkpackages
    │   │   │   ├── sbuild-clean
    │   │   │   ├── sbuild-createchroot
    │   │   │   ├── sbuild-destroychroot
    │   │   │   ├── sbuild-distupgrade
    │   │   │   ├── sbuild-hold
    │   │   │   ├── sbuild-shell
    │   │   │   ├── sbuild-unhold
    │   │   │   ├── sbuild-update
    │   │   │   ├── sbuild-upgrade
    │   │   │   ├── scide
    │   │   │   ├── signal-desktop
    │   │   │   ├── slack
    │   │   │   ├── slirp4netns
    │   │   │   ├── steam
    │   │   │   ├── stress-ng
    │   │   │   ├── surfshark
    │   │   │   ├── systemd-coredump
    │   │   │   ├── thunderbird
    │   │   │   ├── toybox
    │   │   │   ├── transmission
    │   │   │   ├── trinity
    │   │   │   ├── tunables
    │   │   │   │   ├── alias
    │   │   │   │   ├── apparmorfs
    │   │   │   │   ├── dovecot
    │   │   │   │   ├── etc
    │   │   │   │   ├── global
    │   │   │   │   ├── home
    │   │   │   │   ├── home.d
    │   │   │   │   │   ├── site.local
    │   │   │   │   │   └── ubuntu
    │   │   │   │   ├── kernelvars
    │   │   │   │   ├── multiarch
    │   │   │   │   ├── multiarch.d
    │   │   │   │   │   └── site.local
    │   │   │   │   ├── proc
    │   │   │   │   ├── run
    │   │   │   │   ├── securityfs
    │   │   │   │   ├── share
    │   │   │   │   ├── sys
    │   │   │   │   ├── xdg-user-dirs
    │   │   │   │   └── xdg-user-dirs.d
    │   │   │   │       └── site.local
    │   │   │   ├── tup
    │   │   │   ├── tuxedo-control-center
    │   │   │   ├── ubuntu_pro_apt_news
    │   │   │   ├── ubuntu_pro_esm_cache
    │   │   │   ├── unix-chkpwd
    │   │   │   ├── unprivileged_userns
    │   │   │   ├── userbindmount
    │   │   │   ├── usr.bin.man
    │   │   │   ├── usr.bin.tcpdump
    │   │   │   ├── usr.lib.snapd.snap-confine.real
    │   │   │   ├── usr.sbin.chronyd
    │   │   │   ├── usr.sbin.rsyslogd
    │   │   │   ├── uwsgi-core
    │   │   │   ├── vdens
    │   │   │   ├── virtiofsd
    │   │   │   ├── vivaldi-bin
    │   │   │   ├── vpnns
    │   │   │   ├── wike
    │   │   │   └── wpcom
    │   │   ├── apport
    │   │   │   ├── crashdb.conf
    │   │   │   └── report-ignore
    │   │   │       └── README.denylist
    │   │   ├── apt
    │   │   │   ├── apt.conf.d
    │   │   │   │   ├── 01autoremove
    │   │   │   │   ├── 01-vendor-ubuntu
    │   │   │   │   ├── 10periodic
    │   │   │   │   ├── 15update-stamp
    │   │   │   │   ├── 20apt-esm-hook.conf
    │   │   │   │   ├── 20archive
    │   │   │   │   ├── 20auto-upgrades
    │   │   │   │   ├── 20packagekit
    │   │   │   │   ├── 20snapd.conf
    │   │   │   │   ├── 50appstream
    │   │   │   │   ├── 50command-not-found
    │   │   │   │   ├── 50unattended-upgrades
    │   │   │   │   ├── 70debconf
    │   │   │   │   ├── 99needrestart
    │   │   │   │   └── 99update-notifier
    │   │   │   ├── preferences.d
    │   │   │   │   ├── ubuntu-pro-esm-apps
    │   │   │   │   └── ubuntu-pro-esm-infra
    │   │   │   ├── sources.list
    │   │   │   ├── sources.list.d
    │   │   │   │   ├── mongodb-org-8.0.list
    │   │   │   │   └── ubuntu.sources
    │   │   │   └── trusted.gpg.d
    │   │   │       ├── ubuntu-keyring-2012-cdimage.gpg
    │   │   │       └── ubuntu-keyring-2018-archive.gpg
    │   │   ├── bash.bashrc
    │   │   ├── bash_completion
    │   │   ├── bash_completion.d
    │   │   │   └── git-prompt
    │   │   ├── bindresvport.blacklist
    │   │   ├── byobu
    │   │   │   ├── backend
    │   │   │   └── socketdir
    │   │   ├── ca-certificates.conf
    │   │   ├── chrony
    │   │   │   ├── chrony.conf
    │   │   │   ├── chrony.keys
    │   │   │   ├── conf.d
    │   │   │   │   ├── 00-cpc.conf
    │   │   │   │   └── README
    │   │   │   └── sources.d
    │   │   │       └── README
    │   │   ├── cloud
    │   │   │   ├── build.info
    │   │   │   ├── cloud.cfg
    │   │   │   ├── cloud.cfg.d
    │   │   │   │   ├── 05_logging.cfg
    │   │   │   │   ├── 90-cpc-grub.cfg
    │   │   │   │   ├── 90_dpkg.cfg
    │   │   │   │   └── README
    │   │   │   └── templates
    │   │   │       ├── chef_client.rb.tmpl
    │   │   │       ├── chrony.conf.almalinux.tmpl
    │   │   │       ├── chrony.conf.alpine.tmpl
    │   │   │       ├── chrony.conf.centos.tmpl
    │   │   │       ├── chrony.conf.cloudlinux.tmpl
    │   │   │       ├── chrony.conf.cos.tmpl
    │   │   │       ├── chrony.conf.debian.tmpl
    │   │   │       ├── chrony.conf.fedora.tmpl
    │   │   │       ├── chrony.conf.freebsd.tmpl
    │   │   │       ├── chrony.conf.opensuse-leap.tmpl
    │   │   │       ├── chrony.conf.opensuse-microos.tmpl
    │   │   │       ├── chrony.conf.opensuse.tmpl
    │   │   │       ├── chrony.conf.opensuse-tumbleweed.tmpl
    │   │   │       ├── chrony.conf.photon.tmpl
    │   │   │       ├── chrony.conf.rhel.tmpl
    │   │   │       ├── chrony.conf.rocky.tmpl
    │   │   │       ├── chrony.conf.sle_hpc.tmpl
    │   │   │       ├── chrony.conf.sle-micro.tmpl
    │   │   │       ├── chrony.conf.sles.tmpl
    │   │   │       ├── chrony.conf.ubuntu.tmpl
    │   │   │       ├── hosts.alpine.tmpl
    │   │   │       ├── hosts.aosc.tmpl
    │   │   │       ├── hosts.arch.tmpl
    │   │   │       ├── hosts.azurelinux.tmpl
    │   │   │       ├── hosts.debian.tmpl
    │   │   │       ├── hosts.freebsd.tmpl
    │   │   │       ├── hosts.gentoo.tmpl
    │   │   │       ├── hosts.mariner.tmpl
    │   │   │       ├── hosts.openeuler.tmpl
    │   │   │       ├── hosts.photon.tmpl
    │   │   │       ├── hosts.redhat.tmpl
    │   │   │       ├── hosts.suse.tmpl
    │   │   │       ├── ntp.conf.almalinux.tmpl
    │   │   │       ├── ntp.conf.alpine.tmpl
    │   │   │       ├── ntp.conf.cloudlinux.tmpl
    │   │   │       ├── ntp.conf.debian.tmpl
    │   │   │       ├── ntp.conf.fedora.tmpl
    │   │   │       ├── ntp.conf.freebsd.tmpl
    │   │   │       ├── ntp.conf.opensuse.tmpl
    │   │   │       ├── ntp.conf.photon.tmpl
    │   │   │       ├── ntp.conf.rhel.tmpl
    │   │   │       ├── ntp.conf.rocky.tmpl
    │   │   │       ├── ntp.conf.sles.tmpl
    │   │   │       ├── ntp.conf.ubuntu.tmpl
    │   │   │       ├── ntpd.conf.openbsd.tmpl
    │   │   │       ├── resolv.conf.tmpl
    │   │   │       ├── sources.list.debian.deb822.tmpl
    │   │   │       ├── sources.list.debian.tmpl
    │   │   │       ├── sources.list.ubuntu.deb822.tmpl
    │   │   │       ├── sources.list.ubuntu.tmpl
    │   │   │       ├── systemd.resolved.conf.tmpl
    │   │   │       └── timesyncd.conf.tmpl
    │   │   ├── console-setup
    │   │   │   ├── cached_ISO-8859-1.acm.gz
    │   │   │   ├── cached_ISO-8859-1_del.kmap.gz
    │   │   │   ├── cached_setup_font.sh
    │   │   │   ├── cached_setup_keyboard.sh
    │   │   │   ├── cached_setup_terminal.sh
    │   │   │   ├── cached_Uni2-Fixed16.psf.gz
    │   │   │   ├── cached_UTF-8_del.kmap.gz
    │   │   │   ├── compose.ARMSCII-8.inc
    │   │   │   ├── compose.CP1251.inc
    │   │   │   ├── compose.CP1255.inc
    │   │   │   ├── compose.CP1256.inc
    │   │   │   ├── compose.GEORGIAN-ACADEMY.inc
    │   │   │   ├── compose.GEORGIAN-PS.inc
    │   │   │   ├── compose.IBM1133.inc
    │   │   │   ├── compose.ISIRI-3342.inc
    │   │   │   ├── compose.ISO-8859-10.inc
    │   │   │   ├── compose.ISO-8859-11.inc
    │   │   │   ├── compose.ISO-8859-13.inc
    │   │   │   ├── compose.ISO-8859-14.inc
    │   │   │   ├── compose.ISO-8859-15.inc
    │   │   │   ├── compose.ISO-8859-16.inc
    │   │   │   ├── compose.ISO-8859-1.inc
    │   │   │   ├── compose.ISO-8859-2.inc
    │   │   │   ├── compose.ISO-8859-3.inc
    │   │   │   ├── compose.ISO-8859-4.inc
    │   │   │   ├── compose.ISO-8859-5.inc
    │   │   │   ├── compose.ISO-8859-6.inc
    │   │   │   ├── compose.ISO-8859-7.inc
    │   │   │   ├── compose.ISO-8859-8.inc
    │   │   │   ├── compose.ISO-8859-9.inc
    │   │   │   ├── compose.KOI8-R.inc
    │   │   │   ├── compose.KOI8-U.inc
    │   │   │   ├── compose.TIS-620.inc
    │   │   │   ├── compose.VISCII.inc
    │   │   │   ├── ISO-8859-1.acm
    │   │   │   ├── remap.inc
    │   │   │   ├── Uni2-Fixed16.psf.gz
    │   │   │   ├── vtrgb
    │   │   │   └── vtrgb.vga
    │   │   ├── cron.d
    │   │   │   ├── e2scrub_all
    │   │   │   └── sysstat
    │   │   ├── cron.daily
    │   │   │   ├── apport
    │   │   │   ├── apt-compat
    │   │   │   ├── dpkg
    │   │   │   ├── logrotate
    │   │   │   ├── man-db
    │   │   │   └── sysstat
    │   │   ├── cron.hourly
    │   │   ├── cron.monthly
    │   │   ├── crontab
    │   │   ├── cron.weekly
    │   │   │   └── man-db
    │   │   ├── cron.yearly
    │   │   ├── cryptsetup-initramfs
    │   │   │   └── conf-hook
    │   │   ├── crypttab
    │   │   ├── dbus-1
    │   │   │   └── system.d
    │   │   │       └── com.ubuntu.SoftwareProperties.conf
    │   │   ├── debconf.conf
    │   │   ├── debian_version
    │   │   ├── default
    │   │   │   ├── acpid
    │   │   │   ├── amd64-microcode
    │   │   │   ├── apport
    │   │   │   ├── chrony
    │   │   │   ├── console-setup
    │   │   │   ├── cron
    │   │   │   ├── cryptdisks
    │   │   │   ├── dbus
    │   │   │   ├── grub
    │   │   │   ├── grub.d
    │   │   │   │   ├── 40-force-partuuid.cfg
    │   │   │   │   └── 50-cloudimg-settings.cfg
    │   │   │   ├── intel-microcode
    │   │   │   ├── irqbalance
    │   │   │   ├── keyboard
    │   │   │   ├── locale
    │   │   │   ├── mdadm
    │   │   │   ├── motd-news
    │   │   │   ├── networkd-dispatcher
    │   │   │   ├── open-iscsi
    │   │   │   ├── pollinate
    │   │   │   ├── rsync
    │   │   │   ├── ssh
    │   │   │   ├── sysstat
    │   │   │   ├── ufw
    │   │   │   └── useradd
    │   │   ├── deluser.conf
    │   │   ├── depmod.d
    │   │   │   └── ubuntu.conf
    │   │   ├── dhcp
    │   │   │   └── dhclient-exit-hooks.d
    │   │   │       └── chrony
    │   │   ├── dhcpcd.conf
    │   │   ├── dpkg
    │   │   │   ├── dpkg.cfg
    │   │   │   ├── dpkg.cfg.d
    │   │   │   │   └── needrestart
    │   │   │   └── origins
    │   │   │       ├── debian
    │   │   │       ├── default
    │   │   │       └── ubuntu
    │   │   ├── e2scrub.conf
    │   │   ├── ec2_version
    │   │   ├── environment
    │   │   ├── ethertypes
    │   │   ├── fstab
    │   │   ├── fuse.conf
    │   │   ├── fwupd
    │   │   │   ├── bios-settings.d
    │   │   │   │   └── README.md
    │   │   │   ├── fwupd.conf
    │   │   │   └── remotes.d
    │   │   │       ├── lvfs.conf
    │   │   │       ├── lvfs-testing.conf
    │   │   │       └── vendor-directory.conf
    │   │   ├── gai.conf
    │   │   ├── gnutls
    │   │   │   └── config
    │   │   ├── groff
    │   │   │   ├── man.local
    │   │   │   └── mdoc.local
    │   │   ├── group
    │   │   ├── group-
    │   │   ├── grub.d
    │   │   │   ├── 00_header
    │   │   │   ├── 01_track_initrdless_boot_fallback
    │   │   │   ├── 05_debian_theme
    │   │   │   ├── 10_linux
    │   │   │   ├── 10_linux_zfs
    │   │   │   ├── 20_linux_xen
    │   │   │   ├── 25_bli
    │   │   │   ├── 30_os-prober
    │   │   │   ├── 30_uefi-firmware
    │   │   │   ├── 35_fwupd
    │   │   │   ├── 40_custom
    │   │   │   ├── 41_custom
    │   │   │   └── README
    │   │   ├── gshadow
    │   │   ├── gshadow-
    │   │   ├── hdparm.conf
    │   │   ├── hibagent-config.cfg
    │   │   ├── hibinit-config.cfg
    │   │   ├── host.conf
    │   │   ├── hostname
    │   │   ├── hosts
    │   │   ├── hosts.allow
    │   │   ├── hosts.deny
    │   │   ├── init.d
    │   │   │   ├── acpid
    │   │   │   ├── apparmor
    │   │   │   ├── apport
    │   │   │   ├── chrony
    │   │   │   ├── console-setup.sh
    │   │   │   ├── cron
    │   │   │   ├── cryptdisks
    │   │   │   ├── cryptdisks-early
    │   │   │   ├── dbus
    │   │   │   ├── grub-common
    │   │   │   ├── hibagent
    │   │   │   ├── irqbalance
    │   │   │   ├── iscsid
    │   │   │   ├── keyboard-setup.sh
    │   │   │   ├── kmod
    │   │   │   ├── open-iscsi
    │   │   │   ├── open-vm-tools
    │   │   │   ├── plymouth
    │   │   │   ├── plymouth-log
    │   │   │   ├── procps
    │   │   │   ├── rsync
    │   │   │   ├── screen-cleanup
    │   │   │   ├── ssh
    │   │   │   ├── sysstat
    │   │   │   ├── ufw
    │   │   │   ├── unattended-upgrades
    │   │   │   └── uuidd
    │   │   ├── initramfs-tools
    │   │   │   ├── initramfs.conf
    │   │   │   ├── modules
    │   │   │   └── update-initramfs.conf
    │   │   ├── inputrc
    │   │   ├── iproute2
    │   │   │   ├── bpf_pinning
    │   │   │   ├── ematch_map
    │   │   │   ├── group
    │   │   │   ├── nl_protos
    │   │   │   ├── rt_dsfield
    │   │   │   ├── rt_protos
    │   │   │   ├── rt_protos.d
    │   │   │   │   └── README
    │   │   │   ├── rt_realms
    │   │   │   ├── rt_scopes
    │   │   │   ├── rt_tables
    │   │   │   └── rt_tables.d
    │   │   │       └── README
    │   │   ├── iscsi
    │   │   │   ├── initiatorname.iscsi
    │   │   │   └── iscsid.conf
    │   │   ├── issue
    │   │   ├── issue.net
    │   │   ├── kernel
    │   │   │   ├── postinst.d
    │   │   │   │   ├── initramfs-tools
    │   │   │   │   ├── unattended-upgrades
    │   │   │   │   ├── update-notifier
    │   │   │   │   ├── xx-update-initrd-links
    │   │   │   │   ├── zz-shim
    │   │   │   │   └── zz-update-grub
    │   │   │   ├── postrm.d
    │   │   │   │   ├── initramfs-tools
    │   │   │   │   └── zz-update-grub
    │   │   │   └── preinst.d
    │   │   │       └── intel-microcode
    │   │   ├── ldap
    │   │   │   └── ldap.conf
    │   │   ├── ld.so.cache
    │   │   ├── ld.so.conf
    │   │   ├── ld.so.conf.d
    │   │   │   ├── libc.conf
    │   │   │   └── x86_64-linux-gnu.conf
    │   │   ├── legal
    │   │   ├── libaudit.conf
    │   │   ├── libblockdev
    │   │   │   └── 3
    │   │   │       └── conf.d
    │   │   │           └── 00-default.cfg
    │   │   ├── libibverbs.d
    │   │   │   ├── bnxt_re.driver
    │   │   │   ├── cxgb4.driver
    │   │   │   ├── efa.driver
    │   │   │   ├── erdma.driver
    │   │   │   ├── hfi1verbs.driver
    │   │   │   ├── hns.driver
    │   │   │   ├── ipathverbs.driver
    │   │   │   ├── irdma.driver
    │   │   │   ├── mana.driver
    │   │   │   ├── mlx4.driver
    │   │   │   ├── mlx5.driver
    │   │   │   ├── mthca.driver
    │   │   │   ├── ocrdma.driver
    │   │   │   ├── qedr.driver
    │   │   │   ├── rxe.driver
    │   │   │   ├── siw.driver
    │   │   │   └── vmw_pvrdma.driver
    │   │   ├── libnl-3
    │   │   │   ├── classid
    │   │   │   └── pktloc
    │   │   ├── locale.alias
    │   │   ├── locale.conf
    │   │   ├── locale.gen
    │   │   ├── localtime
    │   │   ├── logcheck
    │   │   │   ├── ignore.d.server
    │   │   │   │   ├── gpg-agent
    │   │   │   │   ├── mdadm
    │   │   │   │   └── rsyslog
    │   │   │   └── violations.d
    │   │   │       └── mdadm
    │   │   ├── login.defs
    │   │   ├── logrotate.conf
    │   │   ├── logrotate.d
    │   │   │   ├── alternatives
    │   │   │   ├── apport
    │   │   │   ├── apt
    │   │   │   ├── bootlog
    │   │   │   ├── btmp
    │   │   │   ├── chrony
    │   │   │   ├── cloud-init
    │   │   │   ├── dpkg
    │   │   │   ├── rsyslog
    │   │   │   ├── ubuntu-pro-client
    │   │   │   ├── ufw
    │   │   │   ├── unattended-upgrades
    │   │   │   └── wtmp
    │   │   ├── lsb-release
    │   │   ├── lvm
    │   │   │   ├── lvm.conf
    │   │   │   ├── lvmlocal.conf
    │   │   │   └── profile
    │   │   │       ├── cache-mq.profile
    │   │   │       ├── cache-smq.profile
    │   │   │       ├── command_profile_template.profile
    │   │   │       ├── lvmdbusd.profile
    │   │   │       ├── metadata_profile_template.profile
    │   │   │       ├── thin-generic.profile
    │   │   │       ├── thin-performance.profile
    │   │   │       └── vdo-small.profile
    │   │   ├── machine-id
    │   │   ├── magic
    │   │   ├── magic.mime
    │   │   ├── manpath.config
    │   │   ├── mdadm
    │   │   │   └── mdadm.conf
    │   │   ├── mime.types
    │   │   ├── mke2fs.conf
    │   │   ├── modprobe.d
    │   │   │   ├── amd64-microcode-blacklist.conf
    │   │   │   ├── blacklist-ath_pci.conf
    │   │   │   ├── blacklist.conf
    │   │   │   ├── blacklist-firewire.conf
    │   │   │   ├── blacklist-framebuffer.conf
    │   │   │   ├── blacklist-rare-network.conf
    │   │   │   ├── blacklist-xen-fbfront.conf
    │   │   │   ├── intel-microcode-blacklist.conf
    │   │   │   ├── iwlwifi.conf
    │   │   │   └── mdadm.conf
    │   │   ├── modules
    │   │   ├── modules-load.d
    │   │   │   ├── modules.conf
    │   │   │   └── nf_conntrack.conf
    │   │   ├── mongod.conf
    │   │   ├── mtab
    │   │   ├── multipath
    │   │   │   └── bindings
    │   │   ├── multipath.conf
    │   │   ├── nanorc
    │   │   ├── needrestart
    │   │   │   ├── conf.d
    │   │   │   │   └── README.needrestart
    │   │   │   ├── hook.d
    │   │   │   │   ├── 10-dpkg
    │   │   │   │   ├── 20-rpm
    │   │   │   │   └── 90-none
    │   │   │   ├── iucode.sh
    │   │   │   ├── needrestart.conf
    │   │   │   ├── notify.conf
    │   │   │   ├── notify.d
    │   │   │   │   ├── 200-write
    │   │   │   │   ├── 400-notify-send
    │   │   │   │   ├── 600-mail
    │   │   │   │   └── README.needrestart
    │   │   │   └── restart.d
    │   │   │       ├── dbus.service
    │   │   │       ├── README.needrestart
    │   │   │       ├── systemd-manager
    │   │   │       └── sysv-init
    │   │   ├── netconfig
    │   │   ├── netplan
    │   │   │   └── 50-cloud-init.yaml
    │   │   ├── network
    │   │   │   ├── if-post-down.d
    │   │   │   │   └── chrony
    │   │   │   ├── if-pre-up.d
    │   │   │   │   └── ethtool
    │   │   │   └── if-up.d
    │   │   │       ├── chrony
    │   │   │       └── ethtool
    │   │   ├── networks
    │   │   ├── newt
    │   │   │   ├── palette
    │   │   │   ├── palette.original
    │   │   │   └── palette.ubuntu
    │   │   ├── nftables.conf
    │   │   ├── nsswitch.conf
    │   │   ├── os-release
    │   │   ├── overlayroot.conf
    │   │   ├── overlayroot.local.conf
    │   │   ├── PackageKit
    │   │   │   ├── PackageKit.conf
    │   │   │   └── Vendor.conf
    │   │   ├── pam.conf
    │   │   ├── pam.d
    │   │   │   ├── chfn
    │   │   │   ├── chpasswd
    │   │   │   ├── chsh
    │   │   │   ├── common-account
    │   │   │   ├── common-auth
    │   │   │   ├── common-password
    │   │   │   ├── common-session
    │   │   │   ├── common-session-noninteractive
    │   │   │   ├── cron
    │   │   │   ├── login
    │   │   │   ├── newusers
    │   │   │   ├── other
    │   │   │   ├── passwd
    │   │   │   ├── runuser
    │   │   │   ├── runuser-l
    │   │   │   ├── sshd
    │   │   │   ├── su
    │   │   │   ├── sudo
    │   │   │   ├── sudo-i
    │   │   │   ├── su-l
    │   │   │   └── vmtoolsd
    │   │   ├── passwd
    │   │   ├── passwd-
    │   │   ├── perl
    │   │   │   └── Net
    │   │   │       └── libnet.cfg
    │   │   ├── pki
    │   │   │   ├── fwupd
    │   │   │   │   ├── GPG-KEY-Linux-Foundation-Firmware
    │   │   │   │   ├── GPG-KEY-Linux-Vendor-Firmware-Service
    │   │   │   │   └── LVFS-CA.pem
    │   │   │   └── fwupd-metadata
    │   │   │       ├── GPG-KEY-Linux-Foundation-Metadata
    │   │   │       ├── GPG-KEY-Linux-Vendor-Firmware-Service
    │   │   │       └── LVFS-CA.pem
    │   │   ├── pm
    │   │   │   └── sleep.d
    │   │   │       ├── 10_grub-common
    │   │   │       └── 10_unattended-upgrades-hibernate
    │   │   ├── pollinate
    │   │   │   └── entropy.ubuntu.com.pem
    │   │   ├── ppp
    │   │   │   ├── ip-down.d
    │   │   │   │   └── chrony
    │   │   │   └── ip-up.d
    │   │   │       └── chrony
    │   │   ├── profile
    │   │   ├── profile.d
    │   │   │   ├── 01-locale-fix.sh
    │   │   │   ├── apps-bin-path.sh
    │   │   │   ├── bash_completion.sh
    │   │   │   ├── gawk.csh
    │   │   │   ├── gawk.sh
    │   │   │   ├── Z97-byobu.sh
    │   │   │   ├── Z99-cloudinit-warnings.sh
    │   │   │   └── Z99-cloud-locale-test.sh
    │   │   ├── protocols
    │   │   ├── python3
    │   │   │   └── debian_config
    │   │   ├── python3.12
    │   │   │   └── sitecustomize.py
    │   │   ├── rc0.d
    │   │   │   ├── K01chrony
    │   │   │   ├── K01cryptdisks
    │   │   │   ├── K01cryptdisks-early
    │   │   │   ├── K01irqbalance
    │   │   │   ├── K01iscsid
    │   │   │   ├── K01open-iscsi
    │   │   │   ├── K01open-vm-tools
    │   │   │   ├── K01plymouth
    │   │   │   ├── K01unattended-upgrades
    │   │   │   └── K01uuidd
    │   │   ├── rc1.d
    │   │   │   ├── K01chrony
    │   │   │   ├── K01irqbalance
    │   │   │   ├── K01iscsid
    │   │   │   ├── K01open-iscsi
    │   │   │   ├── K01open-vm-tools
    │   │   │   ├── K01ufw
    │   │   │   └── K01uuidd
    │   │   ├── rc2.d
    │   │   │   ├── S01acpid
    │   │   │   ├── S01apport
    │   │   │   ├── S01chrony
    │   │   │   ├── S01console-setup.sh
    │   │   │   ├── S01cron
    │   │   │   ├── S01dbus
    │   │   │   ├── S01grub-common
    │   │   │   ├── S01irqbalance
    │   │   │   ├── S01open-vm-tools
    │   │   │   ├── S01plymouth
    │   │   │   ├── S01rsync
    │   │   │   ├── S01ssh
    │   │   │   ├── S01sysstat
    │   │   │   ├── S01unattended-upgrades
    │   │   │   └── S01uuidd
    │   │   ├── rc3.d
    │   │   │   ├── S01acpid
    │   │   │   ├── S01apport
    │   │   │   ├── S01chrony
    │   │   │   ├── S01console-setup.sh
    │   │   │   ├── S01cron
    │   │   │   ├── S01dbus
    │   │   │   ├── S01grub-common
    │   │   │   ├── S01irqbalance
    │   │   │   ├── S01open-vm-tools
    │   │   │   ├── S01plymouth
    │   │   │   ├── S01rsync
    │   │   │   ├── S01ssh
    │   │   │   ├── S01sysstat
    │   │   │   ├── S01unattended-upgrades
    │   │   │   └── S01uuidd
    │   │   ├── rc4.d
    │   │   │   ├── S01acpid
    │   │   │   ├── S01apport
    │   │   │   ├── S01chrony
    │   │   │   ├── S01console-setup.sh
    │   │   │   ├── S01cron
    │   │   │   ├── S01dbus
    │   │   │   ├── S01grub-common
    │   │   │   ├── S01irqbalance
    │   │   │   ├── S01open-vm-tools
    │   │   │   ├── S01plymouth
    │   │   │   ├── S01rsync
    │   │   │   ├── S01ssh
    │   │   │   ├── S01sysstat
    │   │   │   ├── S01unattended-upgrades
    │   │   │   └── S01uuidd
    │   │   ├── rc5.d
    │   │   │   ├── S01acpid
    │   │   │   ├── S01apport
    │   │   │   ├── S01chrony
    │   │   │   ├── S01console-setup.sh
    │   │   │   ├── S01cron
    │   │   │   ├── S01dbus
    │   │   │   ├── S01grub-common
    │   │   │   ├── S01irqbalance
    │   │   │   ├── S01open-vm-tools
    │   │   │   ├── S01plymouth
    │   │   │   ├── S01rsync
    │   │   │   ├── S01ssh
    │   │   │   ├── S01sysstat
    │   │   │   ├── S01unattended-upgrades
    │   │   │   └── S01uuidd
    │   │   ├── rc6.d
    │   │   │   ├── K01chrony
    │   │   │   ├── K01cryptdisks
    │   │   │   ├── K01cryptdisks-early
    │   │   │   ├── K01irqbalance
    │   │   │   ├── K01iscsid
    │   │   │   ├── K01open-iscsi
    │   │   │   ├── K01open-vm-tools
    │   │   │   ├── K01plymouth
    │   │   │   ├── K01unattended-upgrades
    │   │   │   └── K01uuidd
    │   │   ├── rcS.d
    │   │   │   ├── K01iscsid
    │   │   │   ├── K01open-iscsi
    │   │   │   ├── S01apparmor
    │   │   │   ├── S01cryptdisks
    │   │   │   ├── S01cryptdisks-early
    │   │   │   ├── S01keyboard-setup.sh
    │   │   │   ├── S01kmod
    │   │   │   ├── S01plymouth-log
    │   │   │   ├── S01procps
    │   │   │   ├── S01screen-cleanup
    │   │   │   └── S01ufw
    │   │   ├── resolv.conf
    │   │   ├── rmt
    │   │   ├── rpc
    │   │   ├── rsyslog.conf
    │   │   ├── rsyslog.d
    │   │   │   ├── 20-ufw.conf
    │   │   │   ├── 21-cloudinit.conf
    │   │   │   └── 50-default.conf
    │   │   ├── screenrc
    │   │   ├── security
    │   │   │   ├── access.conf
    │   │   │   ├── capability.conf
    │   │   │   ├── faillock.conf
    │   │   │   ├── group.conf
    │   │   │   ├── limits.conf
    │   │   │   ├── namespace.conf
    │   │   │   ├── namespace.init
    │   │   │   ├── opasswd
    │   │   │   ├── pam_env.conf
    │   │   │   ├── pwhistory.conf
    │   │   │   ├── sepermit.conf
    │   │   │   └── time.conf
    │   │   ├── selinux
    │   │   │   └── semanage.conf
    │   │   ├── sensors3.conf
    │   │   ├── sensors.d
    │   │   ├── services
    │   │   ├── sgml
    │   │   │   ├── catalog
    │   │   │   └── xml-core.cat
    │   │   ├── shadow
    │   │   ├── shadow-
    │   │   ├── shells
    │   │   ├── skel
    │   │   ├── sos
    │   │   │   └── sos.conf
    │   │   ├── ssh
    │   │   │   ├── moduli
    │   │   │   ├── ssh_config
    │   │   │   ├── sshd_config
    │   │   │   ├── sshd_config.d
    │   │   │   │   └── 60-cloudimg-settings.conf
    │   │   │   ├── ssh_host_ecdsa_key
    │   │   │   ├── ssh_host_ecdsa_key.pub
    │   │   │   ├── ssh_host_ed25519_key
    │   │   │   ├── ssh_host_ed25519_key.pub
    │   │   │   ├── ssh_host_rsa_key
    │   │   │   ├── ssh_host_rsa_key.pub
    │   │   │   └── ssh_import_id
    │   │   ├── ssl
    │   │   │   ├── certs
    │   │   │   │   ├── 002c0b4f.0
    │   │   │   │   ├── 0179095f.0
    │   │   │   │   ├── 02265526.0
    │   │   │   │   ├── 062cdee6.0
    │   │   │   │   ├── 064e0aa9.0
    │   │   │   │   ├── 06dc52d5.0
    │   │   │   │   ├── 08063a00.0
    │   │   │   │   ├── 09789157.0
    │   │   │   │   ├── 0a775a30.0
    │   │   │   │   ├── 0b1b94ef.0
    │   │   │   │   ├── 0b9bc432.0
    │   │   │   │   ├── 0bf05006.0
    │   │   │   │   ├── 0f5dc4f3.0
    │   │   │   │   ├── 0f6fa695.0
    │   │   │   │   ├── 1001acf7.0
    │   │   │   │   ├── 106f3e4d.0
    │   │   │   │   ├── 14bc7599.0
    │   │   │   │   ├── 18856ac4.0
    │   │   │   │   ├── 1cef98f5.0
    │   │   │   │   ├── 1d3472b9.0
    │   │   │   │   ├── 1e08bfd1.0
    │   │   │   │   ├── 1e09d511.0
    │   │   │   │   ├── 228f89db.0
    │   │   │   │   ├── 244b5494.0
    │   │   │   │   ├── 2923b3f9.0
    │   │   │   │   ├── 2ae6433e.0
    │   │   │   │   ├── 2b349938.0
    │   │   │   │   ├── 32888f65.0
    │   │   │   │   ├── 3513523f.0
    │   │   │   │   ├── 3bde41ac.0
    │   │   │   │   ├── 3e359ba6.0
    │   │   │   │   ├── 3fb36b73.0
    │   │   │   │   ├── 40193066.0
    │   │   │   │   ├── 4042bcee.0
    │   │   │   │   ├── 40547a79.0
    │   │   │   │   ├── 406c9bb1.0
    │   │   │   │   ├── 48bec511.0
    │   │   │   │   ├── 4b718d9b.0
    │   │   │   │   ├── 4bfab552.0
    │   │   │   │   ├── 4f316efb.0
    │   │   │   │   ├── 4fd49c6c.0
    │   │   │   │   ├── 5443e9e3.0
    │   │   │   │   ├── 54657681.0
    │   │   │   │   ├── 57bcb2da.0
    │   │   │   │   ├── 5860aaa6.0
    │   │   │   │   ├── 5931b5bc.0
    │   │   │   │   ├── 5ad8a5d6.0
    │   │   │   │   ├── 5cd81ad7.0
    │   │   │   │   ├── 5e98733a.0
    │   │   │   │   ├── 5f15c80c.0
    │   │   │   │   ├── 5f618aec.0
    │   │   │   │   ├── 607986c7.0
    │   │   │   │   ├── 626dceaf.0
    │   │   │   │   ├── 653b494a.0
    │   │   │   │   ├── 68dd7389.0
    │   │   │   │   ├── 6b99d060.0
    │   │   │   │   ├── 6d41d539.0
    │   │   │   │   ├── 6fa5da56.0
    │   │   │   │   ├── 706f604c.0
    │   │   │   │   ├── 749e9e03.0
    │   │   │   │   ├── 75d1b2ed.0
    │   │   │   │   ├── 76faf6c0.0
    │   │   │   │   ├── 7719f463.0
    │   │   │   │   ├── 773e07ad.0
    │   │   │   │   ├── 7a3adc42.0
    │   │   │   │   ├── 7a780d93.0
    │   │   │   │   ├── 7f3d5d1d.0
    │   │   │   │   ├── 8160b96c.0
    │   │   │   │   ├── 81f2d2b1.0
    │   │   │   │   ├── 8312c4c1.0
    │   │   │   │   ├── 8508e720.0
    │   │   │   │   ├── 865fbdf9.0
    │   │   │   │   ├── 8cb5ee0f.0
    │   │   │   │   ├── 8d86cdd1.0
    │   │   │   │   ├── 8d89cda1.0
    │   │   │   │   ├── 8f103249.0
    │   │   │   │   ├── 9046744a.0
    │   │   │   │   ├── 90c5a3c8.0
    │   │   │   │   ├── 930ac5d2.0
    │   │   │   │   ├── 93bc0acc.0
    │   │   │   │   ├── 9482e63a.0
    │   │   │   │   ├── 9846683b.0
    │   │   │   │   ├── 988a38cb.0
    │   │   │   │   ├── 9b46e03d.0
    │   │   │   │   ├── 9b5697b0.0
    │   │   │   │   ├── 9bf03295.0
    │   │   │   │   ├── 9c8dfbd4.0
    │   │   │   │   ├── 9d04f354.0
    │   │   │   │   ├── 9ef4a08a.0
    │   │   │   │   ├── 9f727ac7.0
    │   │   │   │   ├── a3418fda.0
    │   │   │   │   ├── a89d74c2.0
    │   │   │   │   ├── a94d09e5.0
    │   │   │   │   ├── ACCVRAIZ1.pem
    │   │   │   │   ├── AC_RAIZ_FNMT-RCM.pem
    │   │   │   │   ├── AC_RAIZ_FNMT-RCM_SERVIDORES_SEGUROS.pem
    │   │   │   │   ├── Actalis_Authentication_Root_CA.pem
    │   │   │   │   ├── aee5f10d.0
    │   │   │   │   ├── AffirmTrust_Commercial.pem
    │   │   │   │   ├── AffirmTrust_Networking.pem
    │   │   │   │   ├── AffirmTrust_Premium_ECC.pem
    │   │   │   │   ├── AffirmTrust_Premium.pem
    │   │   │   │   ├── Amazon_Root_CA_1.pem
    │   │   │   │   ├── Amazon_Root_CA_2.pem
    │   │   │   │   ├── Amazon_Root_CA_3.pem
    │   │   │   │   ├── Amazon_Root_CA_4.pem
    │   │   │   │   ├── ANF_Secure_Server_Root_CA.pem
    │   │   │   │   ├── Atos_TrustedRoot_2011.pem
    │   │   │   │   ├── Atos_TrustedRoot_Root_CA_ECC_TLS_2021.pem
    │   │   │   │   ├── Atos_TrustedRoot_Root_CA_RSA_TLS_2021.pem
    │   │   │   │   ├── Autoridad_de_Certificacion_Firmaprofesional_CIF_A62634068.pem
    │   │   │   │   ├── b0e59380.0
    │   │   │   │   ├── b1159c4c.0
    │   │   │   │   ├── b433981b.0
    │   │   │   │   ├── b66938e9.0
    │   │   │   │   ├── b727005e.0
    │   │   │   │   ├── b7a5b843.0
    │   │   │   │   ├── b81b93f0.0
    │   │   │   │   ├── Baltimore_CyberTrust_Root.pem
    │   │   │   │   ├── bf53fb88.0
    │   │   │   │   ├── BJCA_Global_Root_CA1.pem
    │   │   │   │   ├── BJCA_Global_Root_CA2.pem
    │   │   │   │   ├── Buypass_Class_2_Root_CA.pem
    │   │   │   │   ├── Buypass_Class_3_Root_CA.pem
    │   │   │   │   ├── c01eb047.0
    │   │   │   │   ├── c28a8a30.0
    │   │   │   │   ├── ca6e4ad9.0
    │   │   │   │   ├── ca-certificates.crt
    │   │   │   │   ├── CA_Disig_Root_R2.pem
    │   │   │   │   ├── cbf06781.0
    │   │   │   │   ├── cc450945.0
    │   │   │   │   ├── cd58d51e.0
    │   │   │   │   ├── cd8c0d63.0
    │   │   │   │   ├── ce5e74ef.0
    │   │   │   │   ├── Certainly_Root_E1.pem
    │   │   │   │   ├── Certainly_Root_R1.pem
    │   │   │   │   ├── Certigna.pem
    │   │   │   │   ├── Certigna_Root_CA.pem
    │   │   │   │   ├── certSIGN_Root_CA_G2.pem
    │   │   │   │   ├── certSIGN_ROOT_CA.pem
    │   │   │   │   ├── Certum_EC-384_CA.pem
    │   │   │   │   ├── Certum_Trusted_Network_CA_2.pem
    │   │   │   │   ├── Certum_Trusted_Network_CA.pem
    │   │   │   │   ├── Certum_Trusted_Root_CA.pem
    │   │   │   │   ├── CFCA_EV_ROOT.pem
    │   │   │   │   ├── CommScope_Public_Trust_ECC_Root-01.pem
    │   │   │   │   ├── CommScope_Public_Trust_ECC_Root-02.pem
    │   │   │   │   ├── CommScope_Public_Trust_RSA_Root-01.pem
    │   │   │   │   ├── CommScope_Public_Trust_RSA_Root-02.pem
    │   │   │   │   ├── Comodo_AAA_Services_root.pem
    │   │   │   │   ├── COMODO_Certification_Authority.pem
    │   │   │   │   ├── COMODO_ECC_Certification_Authority.pem
    │   │   │   │   ├── COMODO_RSA_Certification_Authority.pem
    │   │   │   │   ├── d4dae3dd.0
    │   │   │   │   ├── d52c538d.0
    │   │   │   │   ├── d6325660.0
    │   │   │   │   ├── d7e8dc79.0
    │   │   │   │   ├── d887a5bb.0
    │   │   │   │   ├── da0cfd1d.0
    │   │   │   │   ├── dc4d6a89.0
    │   │   │   │   ├── dd8e9d41.0
    │   │   │   │   ├── de6d66f3.0
    │   │   │   │   ├── DigiCert_Assured_ID_Root_CA.pem
    │   │   │   │   ├── DigiCert_Assured_ID_Root_G2.pem
    │   │   │   │   ├── DigiCert_Assured_ID_Root_G3.pem
    │   │   │   │   ├── DigiCert_Global_Root_CA.pem
    │   │   │   │   ├── DigiCert_Global_Root_G2.pem
    │   │   │   │   ├── DigiCert_Global_Root_G3.pem
    │   │   │   │   ├── DigiCert_High_Assurance_EV_Root_CA.pem
    │   │   │   │   ├── DigiCert_TLS_ECC_P384_Root_G5.pem
    │   │   │   │   ├── DigiCert_TLS_RSA4096_Root_G5.pem
    │   │   │   │   ├── DigiCert_Trusted_Root_G4.pem
    │   │   │   │   ├── D-TRUST_BR_Root_CA_1_2020.pem
    │   │   │   │   ├── D-TRUST_EV_Root_CA_1_2020.pem
    │   │   │   │   ├── D-TRUST_Root_Class_3_CA_2_2009.pem
    │   │   │   │   ├── D-TRUST_Root_Class_3_CA_2_EV_2009.pem
    │   │   │   │   ├── e113c810.0
    │   │   │   │   ├── e18bfb83.0
    │   │   │   │   ├── e35234b1.0
    │   │   │   │   ├── e36a6752.0
    │   │   │   │   ├── e73d606e.0
    │   │   │   │   ├── e868b802.0
    │   │   │   │   ├── e8de2f56.0
    │   │   │   │   ├── ecccd8db.0
    │   │   │   │   ├── ed858448.0
    │   │   │   │   ├── ee64a828.0
    │   │   │   │   ├── eed8c118.0
    │   │   │   │   ├── ef954a4e.0
    │   │   │   │   ├── emSign_ECC_Root_CA_-_C3.pem
    │   │   │   │   ├── emSign_ECC_Root_CA_-_G3.pem
    │   │   │   │   ├── emSign_Root_CA_-_C1.pem
    │   │   │   │   ├── emSign_Root_CA_-_G1.pem
    │   │   │   │   ├── Entrust.net_Premium_2048_Secure_Server_CA.pem
    │   │   │   │   ├── Entrust_Root_Certification_Authority_-_EC1.pem
    │   │   │   │   ├── Entrust_Root_Certification_Authority_-_G2.pem
    │   │   │   │   ├── Entrust_Root_Certification_Authority_-_G4.pem
    │   │   │   │   ├── Entrust_Root_Certification_Authority.pem
    │   │   │   │   ├── ePKI_Root_Certification_Authority.pem
    │   │   │   │   ├── e-Szigno_Root_CA_2017.pem
    │   │   │   │   ├── f081611a.0
    │   │   │   │   ├── f0c70a8d.0
    │   │   │   │   ├── f249de83.0
    │   │   │   │   ├── f30dd6ad.0
    │   │   │   │   ├── f3377b1b.0
    │   │   │   │   ├── f387163d.0
    │   │   │   │   ├── f39fc864.0
    │   │   │   │   ├── f51bb24c.0
    │   │   │   │   ├── fa5da96b.0
    │   │   │   │   ├── fb717492.0
    │   │   │   │   ├── fc5a8f99.0
    │   │   │   │   ├── fd64f3fc.0
    │   │   │   │   ├── fe8a2cd8.0
    │   │   │   │   ├── feffd413.0
    │   │   │   │   ├── ff34af3f.0
    │   │   │   │   ├── GDCA_TrustAUTH_R5_ROOT.pem
    │   │   │   │   ├── GlobalSign_ECC_Root_CA_-_R4.pem
    │   │   │   │   ├── GlobalSign_ECC_Root_CA_-_R5.pem
    │   │   │   │   ├── GlobalSign_Root_CA.pem
    │   │   │   │   ├── GlobalSign_Root_CA_-_R3.pem
    │   │   │   │   ├── GlobalSign_Root_CA_-_R6.pem
    │   │   │   │   ├── GlobalSign_Root_E46.pem
    │   │   │   │   ├── GlobalSign_Root_R46.pem
    │   │   │   │   ├── GLOBALTRUST_2020.pem
    │   │   │   │   ├── Go_Daddy_Class_2_CA.pem
    │   │   │   │   ├── Go_Daddy_Root_Certificate_Authority_-_G2.pem
    │   │   │   │   ├── GTS_Root_R1.pem
    │   │   │   │   ├── GTS_Root_R2.pem
    │   │   │   │   ├── GTS_Root_R3.pem
    │   │   │   │   ├── GTS_Root_R4.pem
    │   │   │   │   ├── HARICA_TLS_ECC_Root_CA_2021.pem
    │   │   │   │   ├── HARICA_TLS_RSA_Root_CA_2021.pem
    │   │   │   │   ├── Hellenic_Academic_and_Research_Institutions_ECC_RootCA_2015.pem
    │   │   │   │   ├── Hellenic_Academic_and_Research_Institutions_RootCA_2015.pem
    │   │   │   │   ├── HiPKI_Root_CA_-_G1.pem
    │   │   │   │   ├── Hongkong_Post_Root_CA_3.pem
    │   │   │   │   ├── IdenTrust_Commercial_Root_CA_1.pem
    │   │   │   │   ├── IdenTrust_Public_Sector_Root_CA_1.pem
    │   │   │   │   ├── ISRG_Root_X1.pem
    │   │   │   │   ├── ISRG_Root_X2.pem
    │   │   │   │   ├── Izenpe.com.pem
    │   │   │   │   ├── Microsec_e-Szigno_Root_CA_2009.pem
    │   │   │   │   ├── Microsoft_ECC_Root_Certificate_Authority_2017.pem
    │   │   │   │   ├── Microsoft_RSA_Root_Certificate_Authority_2017.pem
    │   │   │   │   ├── NAVER_Global_Root_Certification_Authority.pem
    │   │   │   │   ├── NetLock_Arany_=Class_Gold=_Főtanúsítvány.pem
    │   │   │   │   ├── OISTE_WISeKey_Global_Root_GB_CA.pem
    │   │   │   │   ├── OISTE_WISeKey_Global_Root_GC_CA.pem
    │   │   │   │   ├── QuoVadis_Root_CA_1_G3.pem
    │   │   │   │   ├── QuoVadis_Root_CA_2_G3.pem
    │   │   │   │   ├── QuoVadis_Root_CA_2.pem
    │   │   │   │   ├── QuoVadis_Root_CA_3_G3.pem
    │   │   │   │   ├── QuoVadis_Root_CA_3.pem
    │   │   │   │   ├── Sectigo_Public_Server_Authentication_Root_E46.pem
    │   │   │   │   ├── Sectigo_Public_Server_Authentication_Root_R46.pem
    │   │   │   │   ├── Secure_Global_CA.pem
    │   │   │   │   ├── SecureSign_RootCA11.pem
    │   │   │   │   ├── SecureTrust_CA.pem
    │   │   │   │   ├── Security_Communication_ECC_RootCA1.pem
    │   │   │   │   ├── Security_Communication_RootCA2.pem
    │   │   │   │   ├── Security_Communication_RootCA3.pem
    │   │   │   │   ├── Security_Communication_Root_CA.pem
    │   │   │   │   ├── SSL.com_EV_Root_Certification_Authority_ECC.pem
    │   │   │   │   ├── SSL.com_EV_Root_Certification_Authority_RSA_R2.pem
    │   │   │   │   ├── SSL.com_Root_Certification_Authority_ECC.pem
    │   │   │   │   ├── SSL.com_Root_Certification_Authority_RSA.pem
    │   │   │   │   ├── SSL.com_TLS_ECC_Root_CA_2022.pem
    │   │   │   │   ├── SSL.com_TLS_RSA_Root_CA_2022.pem
    │   │   │   │   ├── Starfield_Class_2_CA.pem
    │   │   │   │   ├── Starfield_Root_Certificate_Authority_-_G2.pem
    │   │   │   │   ├── Starfield_Services_Root_Certificate_Authority_-_G2.pem
    │   │   │   │   ├── SwissSign_Gold_CA_-_G2.pem
    │   │   │   │   ├── SwissSign_Silver_CA_-_G2.pem
    │   │   │   │   ├── SZAFIR_ROOT_CA2.pem
    │   │   │   │   ├── Telia_Root_CA_v2.pem
    │   │   │   │   ├── TeliaSonera_Root_CA_v1.pem
    │   │   │   │   ├── TrustAsia_Global_Root_CA_G3.pem
    │   │   │   │   ├── TrustAsia_Global_Root_CA_G4.pem
    │   │   │   │   ├── Trustwave_Global_Certification_Authority.pem
    │   │   │   │   ├── Trustwave_Global_ECC_P256_Certification_Authority.pem
    │   │   │   │   ├── Trustwave_Global_ECC_P384_Certification_Authority.pem
    │   │   │   │   ├── T-TeleSec_GlobalRoot_Class_2.pem
    │   │   │   │   ├── T-TeleSec_GlobalRoot_Class_3.pem
    │   │   │   │   ├── TUBITAK_Kamu_SM_SSL_Kok_Sertifikasi_-_Surum_1.pem
    │   │   │   │   ├── TunTrust_Root_CA.pem
    │   │   │   │   ├── TWCA_Global_Root_CA.pem
    │   │   │   │   ├── TWCA_Root_Certification_Authority.pem
    │   │   │   │   ├── UCA_Extended_Validation_Root.pem
    │   │   │   │   ├── UCA_Global_G2_Root.pem
    │   │   │   │   ├── USERTrust_ECC_Certification_Authority.pem
    │   │   │   │   ├── USERTrust_RSA_Certification_Authority.pem
    │   │   │   │   ├── vTrus_ECC_Root_CA.pem
    │   │   │   │   ├── vTrus_Root_CA.pem
    │   │   │   │   └── XRamp_Global_CA_Root.pem
    │   │   │   └── openssl.cnf
    │   │   ├── subgid
    │   │   ├── subgid-
    │   │   ├── subuid
    │   │   ├── subuid-
    │   │   ├── sudo.conf
    │   │   ├── sudoers
    │   │   ├── sudoers.d
    │   │   │   ├── 90-cloud-init-users
    │   │   │   └── README
    │   │   ├── sudo_logsrvd.conf
    │   │   ├── supercat
    │   │   │   ├── spcrc-crontab
    │   │   │   └── spcrc-crontab-light
    │   │   ├── sysctl.conf
    │   │   ├── sysctl.d
    │   │   │   ├── 10-bufferbloat.conf
    │   │   │   ├── 10-console-messages.conf
    │   │   │   ├── 10-ipv6-privacy.conf
    │   │   │   ├── 10-kernel-hardening.conf
    │   │   │   ├── 10-magic-sysrq.conf
    │   │   │   ├── 10-map-count.conf
    │   │   │   ├── 10-network-security.conf
    │   │   │   ├── 10-ptrace.conf
    │   │   │   ├── 10-zeropage.conf
    │   │   │   ├── 50-cloudimg-settings.conf
    │   │   │   ├── 99-cloudimg-ipv6.conf
    │   │   │   ├── 99-sysctl.conf
    │   │   │   └── README.sysctl
    │   │   ├── sysstat
    │   │   │   ├── sysstat
    │   │   │   └── sysstat.ioconf
    │   │   ├── systemd
    │   │   │   ├── journald.conf
    │   │   │   ├── logind.conf
    │   │   │   ├── networkd.conf
    │   │   │   ├── pstore.conf
    │   │   │   ├── resolved.conf
    │   │   │   ├── sleep.conf
    │   │   │   ├── system
    │   │   │   │   ├── chronyd.service
    │   │   │   │   ├── cloud-config.target.wants
    │   │   │   │   │   └── cloud-init-hotplugd.socket
    │   │   │   │   ├── cloud-final.service.wants
    │   │   │   │   │   └── snapd.seeded.service
    │   │   │   │   ├── cloud-init.target.wants
    │   │   │   │   │   ├── cloud-config.service
    │   │   │   │   │   ├── cloud-final.service
    │   │   │   │   │   ├── cloud-init-local.service
    │   │   │   │   │   └── cloud-init.service
    │   │   │   │   ├── dbus-org.freedesktop.ModemManager1.service
    │   │   │   │   ├── dbus-org.freedesktop.resolve1.service
    │   │   │   │   ├── emergency.target.wants
    │   │   │   │   │   └── grub-initrd-fallback.service
    │   │   │   │   ├── final.target.wants
    │   │   │   │   │   └── snapd.system-shutdown.service
    │   │   │   │   ├── getty.target.wants
    │   │   │   │   │   └── getty@tty1.service
    │   │   │   │   ├── graphical.target.wants
    │   │   │   │   │   └── udisks2.service
    │   │   │   │   ├── hibernate.target.wants
    │   │   │   │   │   └── grub-common.service
    │   │   │   │   ├── hybrid-sleep.target.wants
    │   │   │   │   │   └── grub-common.service
    │   │   │   │   ├── iscsi.service
    │   │   │   │   ├── mdmonitor.service.wants
    │   │   │   │   │   ├── mdcheck_continue.timer
    │   │   │   │   │   ├── mdcheck_start.timer
    │   │   │   │   │   └── mdmonitor-oneshot.timer
    │   │   │   │   ├── multi-user.target.wants
    │   │   │   │   │   ├── apport.service
    │   │   │   │   │   ├── chrony.service
    │   │   │   │   │   ├── console-setup.service
    │   │   │   │   │   ├── cron.service
    │   │   │   │   │   ├── dmesg.service
    │   │   │   │   │   ├── e2scrub_reap.service
    │   │   │   │   │   ├── ec2-instance-connect-harvest-hostkeys.service
    │   │   │   │   │   ├── grub-common.service
    │   │   │   │   │   ├── grub-initrd-fallback.service
    │   │   │   │   │   ├── hibinit-agent.service
    │   │   │   │   │   ├── irqbalance.service
    │   │   │   │   │   ├── lxd-installer.socket
    │   │   │   │   │   ├── ModemManager.service
    │   │   │   │   │   ├── mongod.service
    │   │   │   │   │   ├── networkd-dispatcher.service
    │   │   │   │   │   ├── open-vm-tools.service
    │   │   │   │   │   ├── pollinate.service
    │   │   │   │   │   ├── remote-fs.target
    │   │   │   │   │   ├── rsyslog.service
    │   │   │   │   │   ├── secureboot-db.service
    │   │   │   │   │   ├── snap.amazon-ssm-agent.amazon-ssm-agent.service
    │   │   │   │   │   ├── snap-core22-2133.mount
    │   │   │   │   │   ├── snapd.apparmor.service
    │   │   │   │   │   ├── snapd.autoimport.service
    │   │   │   │   │   ├── snapd.core-fixup.service
    │   │   │   │   │   ├── snapd.recovery-chooser-trigger.service
    │   │   │   │   │   ├── snapd.seeded.service
    │   │   │   │   │   ├── snapd.service
    │   │   │   │   │   ├── snap-lxd-36971.mount
    │   │   │   │   │   ├── snap.lxd.activate.service
    │   │   │   │   │   ├── snap-snapd-25202.mount
    │   │   │   │   │   ├── sysstat.service
    │   │   │   │   │   ├── systemd-networkd.service
    │   │   │   │   │   ├── ua-reboot-cmds.service
    │   │   │   │   │   ├── ubuntu-advantage.service
    │   │   │   │   │   ├── ufw.service
    │   │   │   │   │   └── unattended-upgrades.service
    │   │   │   │   ├── network-online.target.wants
    │   │   │   │   │   └── systemd-networkd-wait-online.service
    │   │   │   │   ├── open-vm-tools.service.requires
    │   │   │   │   │   └── vgauth.service
    │   │   │   │   ├── paths.target.wants
    │   │   │   │   │   ├── acpid.path
    │   │   │   │   │   ├── apport-autoreport.path
    │   │   │   │   │   └── tpm-udev.path
    │   │   │   │   ├── rescue.target.wants
    │   │   │   │   │   └── grub-initrd-fallback.service
    │   │   │   │   ├── sleep.target.wants
    │   │   │   │   │   └── grub-initrd-fallback.service
    │   │   │   │   ├── snap.amazon-ssm-agent.amazon-ssm-agent.service
    │   │   │   │   ├── snap-core22-2133.mount
    │   │   │   │   ├── snapd.mounts.target.wants
    │   │   │   │   │   ├── snap-core22-2133.mount
    │   │   │   │   │   ├── snap-lxd-36971.mount
    │   │   │   │   │   └── snap-snapd-25202.mount
    │   │   │   │   ├── snap-lxd-36971.mount
    │   │   │   │   ├── snap.lxd.activate.service
    │   │   │   │   ├── snap.lxd.daemon.service
    │   │   │   │   ├── snap.lxd.daemon.unix.socket
    │   │   │   │   ├── snap.lxd.user-daemon.service
    │   │   │   │   ├── snap.lxd.user-daemon.unix.socket
    │   │   │   │   ├── snap-snapd-25202.mount
    │   │   │   │   ├── sockets.target.wants
    │   │   │   │   │   ├── acpid.socket
    │   │   │   │   │   ├── apport-forward.socket
    │   │   │   │   │   ├── dm-event.socket
    │   │   │   │   │   ├── iscsid.socket
    │   │   │   │   │   ├── multipathd.socket
    │   │   │   │   │   ├── snapd.socket
    │   │   │   │   │   ├── snap.lxd.daemon.unix.socket
    │   │   │   │   │   ├── snap.lxd.user-daemon.unix.socket
    │   │   │   │   │   ├── ssh.socket
    │   │   │   │   │   ├── systemd-networkd.socket
    │   │   │   │   │   └── uuidd.socket
    │   │   │   │   ├── ssh.service.requires
    │   │   │   │   │   └── ssh.socket
    │   │   │   │   ├── suspend.target.wants
    │   │   │   │   │   └── grub-common.service
    │   │   │   │   ├── suspend-then-hibernate.target.wants
    │   │   │   │   │   └── grub-common.service
    │   │   │   │   ├── sysinit.target.wants
    │   │   │   │   │   ├── apparmor.service
    │   │   │   │   │   ├── blk-availability.service
    │   │   │   │   │   ├── finalrd.service
    │   │   │   │   │   ├── keyboard-setup.service
    │   │   │   │   │   ├── lvm2-lvmpolld.socket
    │   │   │   │   │   ├── lvm2-monitor.service
    │   │   │   │   │   ├── multipathd.service
    │   │   │   │   │   ├── open-iscsi.service
    │   │   │   │   │   ├── setvtrgb.service
    │   │   │   │   │   ├── systemd-pstore.service
    │   │   │   │   │   └── systemd-resolved.service
    │   │   │   │   ├── syslog.service
    │   │   │   │   ├── sysstat.service.wants
    │   │   │   │   │   ├── sysstat-collect.timer
    │   │   │   │   │   └── sysstat-summary.timer
    │   │   │   │   ├── timers.target.wants
    │   │   │   │   │   ├── apport-autoreport.timer
    │   │   │   │   │   ├── apt-daily.timer
    │   │   │   │   │   ├── apt-daily-upgrade.timer
    │   │   │   │   │   ├── dpkg-db-backup.timer
    │   │   │   │   │   ├── e2scrub_all.timer
    │   │   │   │   │   ├── fstrim.timer
    │   │   │   │   │   ├── fwupd-refresh.timer
    │   │   │   │   │   ├── logrotate.timer
    │   │   │   │   │   ├── man-db.timer
    │   │   │   │   │   ├── motd-news.timer
    │   │   │   │   │   ├── snapd.snap-repair.timer
    │   │   │   │   │   ├── ua-timer.timer
    │   │   │   │   │   ├── update-notifier-download.timer
    │   │   │   │   │   └── update-notifier-motd.timer
    │   │   │   │   └── vmtoolsd.service
    │   │   │   ├── system.conf
    │   │   │   ├── system-generators
    │   │   │   │   └── systemd-gpt-auto-generator
    │   │   │   ├── user
    │   │   │   │   ├── sockets.target.wants
    │   │   │   │   │   ├── dirmngr.socket
    │   │   │   │   │   ├── gpg-agent-browser.socket
    │   │   │   │   │   ├── gpg-agent-extra.socket
    │   │   │   │   │   ├── gpg-agent.socket
    │   │   │   │   │   ├── gpg-agent-ssh.socket
    │   │   │   │   │   ├── keyboxd.socket
    │   │   │   │   │   └── pk-debconf-helper.socket
    │   │   │   │   └── timers.target.wants
    │   │   │   │       └── launchpadlib-cache-clean.timer
    │   │   │   └── user.conf
    │   │   ├── terminfo
    │   │   │   └── README
    │   │   ├── timezone
    │   │   ├── tmpfiles.d
    │   │   │   └── screen-cleanup.conf
    │   │   ├── ubuntu-advantage
    │   │   │   └── uaclient.conf
    │   │   ├── ucf.conf
    │   │   ├── udev
    │   │   │   ├── iocost.conf
    │   │   │   ├── rules.d
    │   │   │   │   ├── 60-cdrom_id.rules
    │   │   │   │   ├── 70-snap.snapd.rules
    │   │   │   │   └── 90-cloud-init-hook-hotplug.rules
    │   │   │   └── udev.conf
    │   │   ├── udisks2
    │   │   │   ├── mount_options.conf.example
    │   │   │   └── udisks2.conf
    │   │   ├── ufw
    │   │   │   ├── after6.rules
    │   │   │   ├── after.init
    │   │   │   ├── after.rules
    │   │   │   ├── applications.d
    │   │   │   │   └── openssh-server
    │   │   │   ├── before6.rules
    │   │   │   ├── before.init
    │   │   │   ├── before.rules
    │   │   │   ├── sysctl.conf
    │   │   │   ├── ufw.conf
    │   │   │   ├── user6.rules
    │   │   │   └── user.rules
    │   │   ├── update-manager
    │   │   │   ├── meta-release
    │   │   │   ├── release-upgrades
    │   │   │   └── release-upgrades.d
    │   │   │       └── ubuntu-advantage-upgrades.cfg
    │   │   ├── update-motd.d
    │   │   │   ├── 00-header
    │   │   │   ├── 10-help-text
    │   │   │   ├── 50-landscape-sysinfo
    │   │   │   ├── 50-motd-news
    │   │   │   ├── 85-fwupd
    │   │   │   ├── 90-updates-available
    │   │   │   ├── 91-contract-ua-esm-status
    │   │   │   ├── 91-release-upgrade
    │   │   │   ├── 92-unattended-upgrades
    │   │   │   ├── 95-hwe-eol
    │   │   │   ├── 97-overlayroot
    │   │   │   ├── 98-fsck-at-reboot
    │   │   │   └── 98-reboot-required
    │   │   ├── usb_modeswitch.conf
    │   │   ├── vconsole.conf
    │   │   ├── vim
    │   │   │   ├── vimrc
    │   │   │   └── vimrc.tiny
    │   │   ├── vmware-tools
    │   │   │   ├── poweroff-vm-default
    │   │   │   ├── poweron-vm-default
    │   │   │   ├── resume-vm-default
    │   │   │   ├── scripts
    │   │   │   │   └── vmware
    │   │   │   │       └── network
    │   │   │   ├── statechange.subr
    │   │   │   ├── suspend-vm-default
    │   │   │   ├── tools.conf
    │   │   │   ├── tools.conf.example
    │   │   │   ├── vgauth
    │   │   │   │   └── schemas
    │   │   │   │       ├── catalog.xml
    │   │   │   │       ├── datatypes.dtd
    │   │   │   │       ├── saml-schema-assertion-2.0.xsd
    │   │   │   │       ├── xenc-schema.xsd
    │   │   │   │       ├── xmldsig-core-schema.xsd
    │   │   │   │       ├── XMLSchema.dtd
    │   │   │   │       ├── XMLSchema-hasFacetAndProperty.xsd
    │   │   │   │       ├── XMLSchema-instance.xsd
    │   │   │   │       ├── XMLSchema.xsd
    │   │   │   │       └── xml.xsd
    │   │   │   └── vgauth.conf
    │   │   ├── vtrgb
    │   │   ├── wgetrc
    │   │   ├── X11
    │   │   │   └── Xsession.d
    │   │   │       ├── 20dbus_xdg-runtime
    │   │   │       └── 90gpg-agent
    │   │   ├── xattr.conf
    │   │   ├── xdg
    │   │   │   ├── autostart
    │   │   │   │   ├── snap-userd-autostart.desktop
    │   │   │   │   └── xdg-user-dirs.desktop
    │   │   │   ├── systemd
    │   │   │   │   └── user
    │   │   │   ├── user-dirs.conf
    │   │   │   └── user-dirs.defaults
    │   │   ├── xml
    │   │   │   ├── catalog
    │   │   │   ├── catalog.old
    │   │   │   ├── polkitd.xml
    │   │   │   ├── polkitd.xml.old
    │   │   │   ├── xml-core.xml
    │   │   │   └── xml-core.xml.old
    │   │   └── zsh_command_not_found
    │   ├── home
    │   │   ├── mongoadmin
    │   │   └── ubuntu
    │   ├── lib
    │   │   └── systemd
    │   │       └── system
    │   │           ├── acpid.path
    │   │           ├── acpid.service
    │   │           ├── acpid.socket
    │   │           ├── apparmor.service
    │   │           ├── apport-autoreport.path
    │   │           ├── apport-autoreport.service
    │   │           ├── apport-autoreport.timer
    │   │           ├── apport-coredump-hook@.service
    │   │           ├── apport-forward@.service
    │   │           ├── apport-forward.socket
    │   │           ├── apport.service
    │   │           ├── apt-daily.service
    │   │           ├── apt-daily.timer
    │   │           ├── apt-daily-upgrade.service
    │   │           ├── apt-daily-upgrade.timer
    │   │           ├── apt-news.service
    │   │           ├── autovt@.service
    │   │           ├── basic.target
    │   │           ├── blk-availability.service
    │   │           ├── blockdev@.target
    │   │           ├── bluetooth.target
    │   │           ├── bolt.service
    │   │           ├── boot-complete.target
    │   │           ├── chrony-dnssrv@.service
    │   │           ├── chrony-dnssrv@.timer
    │   │           ├── chrony.service
    │   │           ├── chrony-wait.service
    │   │           ├── cloud-config.service
    │   │           ├── cloud-config.target
    │   │           ├── cloud-final.service
    │   │           ├── cloud-init-hotplugd.service
    │   │           ├── cloud-init-hotplugd.socket
    │   │           ├── cloud-init-local.service
    │   │           ├── cloud-init.service
    │   │           ├── cloud-init.target
    │   │           ├── console-getty.service
    │   │           ├── console-setup.service
    │   │           ├── container-getty@.service
    │   │           ├── cron.service
    │   │           ├── cryptdisks-early.service
    │   │           ├── cryptdisks.service
    │   │           ├── cryptsetup-pre.target
    │   │           ├── cryptsetup.target
    │   │           ├── ctrl-alt-del.target
    │   │           ├── dbus-org.freedesktop.hostname1.service
    │   │           ├── dbus-org.freedesktop.locale1.service
    │   │           ├── dbus-org.freedesktop.login1.service
    │   │           ├── dbus-org.freedesktop.timedate1.service
    │   │           ├── dbus.service
    │   │           ├── dbus.socket
    │   │           ├── debug-shell.service
    │   │           ├── default.target
    │   │           ├── dev-hugepages.mount
    │   │           ├── dev-mqueue.mount
    │   │           ├── dmesg.service
    │   │           ├── dm-event.service
    │   │           ├── dm-event.socket
    │   │           ├── dpkg-db-backup.service
    │   │           ├── dpkg-db-backup.timer
    │   │           ├── e2scrub_all.service
    │   │           ├── e2scrub_all.timer
    │   │           ├── e2scrub_fail@.service
    │   │           ├── e2scrub_reap.service
    │   │           ├── e2scrub@.service
    │   │           ├── ec2-instance-connect-harvest-hostkeys.service
    │   │           ├── emergency.service
    │   │           ├── emergency.target
    │   │           ├── esm-cache.service
    │   │           ├── exit.target
    │   │           ├── factory-reset.target
    │   │           ├── finalrd.service
    │   │           ├── final.target
    │   │           ├── first-boot-complete.target
    │   │           ├── friendly-recovery.service
    │   │           ├── friendly-recovery.target
    │   │           ├── fstrim.service
    │   │           ├── fstrim.timer
    │   │           ├── fwupd-offline-update.service
    │   │           ├── fwupd-refresh.service
    │   │           ├── fwupd-refresh.timer
    │   │           ├── fwupd.service
    │   │           ├── getty-pre.target
    │   │           ├── getty@.service
    │   │           ├── getty-static.service
    │   │           ├── getty.target
    │   │           ├── getty.target.wants
    │   │           │   └── getty-static.service
    │   │           ├── graphical.target
    │   │           ├── graphical.target.wants
    │   │           │   └── systemd-update-utmp-runlevel.service
    │   │           ├── grub-common.service
    │   │           ├── grub-initrd-fallback.service
    │   │           ├── halt.target
    │   │           ├── halt.target.wants
    │   │           │   ├── plymouth-halt.service
    │   │           │   └── plymouth-switch-root-initramfs.service
    │   │           ├── hibernate.target
    │   │           ├── hibinit-agent.service
    │   │           ├── hwclock.service
    │   │           ├── hybrid-sleep.target
    │   │           ├── initrd-cleanup.service
    │   │           ├── initrd-fs.target
    │   │           ├── initrd-parse-etc.service
    │   │           ├── initrd-root-device.target
    │   │           ├── initrd-root-device.target.wants
    │   │           │   ├── remote-cryptsetup.target
    │   │           │   └── remote-veritysetup.target
    │   │           ├── initrd-root-fs.target
    │   │           ├── initrd-root-fs.target.wants
    │   │           │   └── systemd-repart.service
    │   │           ├── initrd-switch-root.service
    │   │           ├── initrd-switch-root.target
    │   │           ├── initrd-switch-root.target.wants
    │   │           │   ├── plymouth-start.service
    │   │           │   └── plymouth-switch-root.service
    │   │           ├── initrd.target
    │   │           ├── initrd.target.wants
    │   │           │   ├── systemd-battery-check.service
    │   │           │   ├── systemd-bsod.service
    │   │           │   └── systemd-pcrphase-initrd.service
    │   │           ├── initrd-udevadm-cleanup-db.service
    │   │           ├── initrd-usr-fs.target
    │   │           ├── integritysetup-pre.target
    │   │           ├── integritysetup.target
    │   │           ├── irqbalance.service
    │   │           ├── iscsid.service
    │   │           ├── iscsid.socket
    │   │           ├── kexec.target
    │   │           ├── kexec.target.wants
    │   │           │   ├── plymouth-kexec.service
    │   │           │   └── plymouth-switch-root-initramfs.service
    │   │           ├── keyboard-setup.service
    │   │           ├── kmod.service
    │   │           ├── kmod-static-nodes.service
    │   │           ├── ldconfig.service
    │   │           ├── local-fs-pre.target
    │   │           ├── local-fs.target
    │   │           ├── logrotate.service
    │   │           ├── logrotate.timer
    │   │           ├── lvm2-lvmpolld.service
    │   │           ├── lvm2-lvmpolld.socket
    │   │           ├── lvm2-monitor.service
    │   │           ├── lxd-agent.service
    │   │           ├── lxd-installer@.service
    │   │           ├── lxd-installer.socket
    │   │           ├── machine.slice
    │   │           ├── man-db.service
    │   │           ├── man-db.timer
    │   │           ├── mdadm-grow-continue@.service
    │   │           ├── mdadm-last-resort@.service
    │   │           ├── mdadm-last-resort@.timer
    │   │           ├── mdcheck_continue.service
    │   │           ├── mdcheck_continue.timer
    │   │           ├── mdcheck_start.service
    │   │           ├── mdcheck_start.timer
    │   │           ├── mdmonitor-oneshot.service
    │   │           ├── mdmonitor-oneshot.timer
    │   │           ├── mdmonitor.service
    │   │           ├── mdmon@.service
    │   │           ├── ModemManager.service
    │   │           ├── modprobe@.service
    │   │           ├── mongod.service
    │   │           ├── motd-news.service
    │   │           ├── motd-news.timer
    │   │           ├── multipathd.service
    │   │           ├── multipathd.socket
    │   │           ├── multipath-tools-boot.service
    │   │           ├── multipath-tools.service
    │   │           ├── multi-user.target
    │   │           ├── multi-user.target.wants
    │   │           │   ├── dbus.service
    │   │           │   ├── getty.target
    │   │           │   ├── plymouth-quit.service
    │   │           │   ├── plymouth-quit-wait.service
    │   │           │   ├── systemd-ask-password-wall.path
    │   │           │   ├── systemd-logind.service
    │   │           │   ├── systemd-update-utmp-runlevel.service
    │   │           │   └── systemd-user-sessions.service
    │   │           ├── networkd-dispatcher.service
    │   │           ├── network-online.target
    │   │           ├── network-pre.target
    │   │           ├── network.target
    │   │           ├── nftables.service
    │   │           ├── nss-lookup.target
    │   │           ├── nss-user-lookup.target
    │   │           ├── open-iscsi.service
    │   │           ├── open-vm-tools.service
    │   │           ├── packagekit-offline-update.service
    │   │           ├── packagekit.service
    │   │           ├── pam_namespace.service
    │   │           ├── paths.target
    │   │           ├── plymouth-halt.service
    │   │           ├── plymouth-kexec.service
    │   │           ├── plymouth-log.service
    │   │           ├── plymouth-poweroff.service
    │   │           ├── plymouth-quit.service
    │   │           ├── plymouth-quit-wait.service
    │   │           ├── plymouth-read-write.service
    │   │           ├── plymouth-reboot.service
    │   │           ├── plymouth.service
    │   │           ├── plymouth-start.service
    │   │           ├── plymouth-switch-root-initramfs.service
    │   │           ├── plymouth-switch-root.service
    │   │           ├── polkit.service
    │   │           ├── pollinate.service
    │   │           ├── poweroff.target
    │   │           ├── poweroff.target.wants
    │   │           │   ├── plymouth-poweroff.service
    │   │           │   └── plymouth-switch-root-initramfs.service
    │   │           ├── printer.target
    │   │           ├── procps.service
    │   │           ├── proc-sys-fs-binfmt_misc.automount
    │   │           ├── proc-sys-fs-binfmt_misc.mount
    │   │           ├── quotaon.service
    │   │           ├── rc-local.service
    │   │           ├── rc-local.service.d
    │   │           │   └── debian.conf
    │   │           ├── reboot.target
    │   │           ├── reboot.target.wants
    │   │           │   ├── plymouth-reboot.service
    │   │           │   └── plymouth-switch-root-initramfs.service
    │   │           ├── remote-cryptsetup.target
    │   │           ├── remote-fs-pre.target
    │   │           ├── remote-fs.target
    │   │           ├── remote-veritysetup.target
    │   │           ├── rescue.service
    │   │           ├── rescue-ssh.target
    │   │           ├── rescue.target
    │   │           ├── rescue.target.wants
    │   │           │   └── systemd-update-utmp-runlevel.service
    │   │           ├── rpcbind.target
    │   │           ├── rsync.service
    │   │           ├── rsyslog.service
    │   │           ├── runlevel0.target
    │   │           ├── runlevel1.target
    │   │           ├── runlevel2.target
    │   │           ├── runlevel3.target
    │   │           ├── runlevel4.target
    │   │           ├── runlevel5.target
    │   │           ├── runlevel6.target
    │   │           ├── screen-cleanup.service
    │   │           ├── secureboot-db.service
    │   │           ├── serial-getty@.service
    │   │           ├── setvtrgb.service
    │   │           ├── shutdown.target
    │   │           ├── sigpwr.target
    │   │           ├── sleep.target
    │   │           ├── slices.target
    │   │           ├── smartcard.target
    │   │           ├── snapd.apparmor.service
    │   │           ├── snapd.autoimport.service
    │   │           ├── snapd.core-fixup.service
    │   │           ├── snapd.failure.service
    │   │           ├── snapd.gpio-chardev-setup.target
    │   │           ├── snapd.mounts-pre.target
    │   │           ├── snapd.mounts.target
    │   │           ├── snapd.recovery-chooser-trigger.service
    │   │           ├── snapd.seeded.service
    │   │           ├── snapd.service
    │   │           ├── snapd.snap-repair.service
    │   │           ├── snapd.snap-repair.timer
    │   │           ├── snapd.socket
    │   │           ├── snapd.system-shutdown.service
    │   │           ├── sockets.target
    │   │           ├── sockets.target.wants
    │   │           │   ├── dbus.socket
    │   │           │   ├── systemd-initctl.socket
    │   │           │   ├── systemd-journald-dev-log.socket
    │   │           │   ├── systemd-journald.socket
    │   │           │   ├── systemd-pcrextend.socket
    │   │           │   ├── systemd-sysext.socket
    │   │           │   ├── systemd-udevd-control.socket
    │   │           │   └── systemd-udevd-kernel.socket
    │   │           ├── soft-reboot.target
    │   │           ├── sound.target
    │   │           ├── sshd-keygen@.service.d
    │   │           │   └── disable-sshd-keygen-if-cloud-init-active.conf
    │   │           ├── ssh.service
    │   │           ├── ssh.service.d
    │   │           │   └── ec2-instance-connect.conf
    │   │           ├── ssh.socket
    │   │           ├── storage-target-mode.target
    │   │           ├── sudo.service
    │   │           ├── suspend.target
    │   │           ├── suspend-then-hibernate.target
    │   │           ├── swap.target
    │   │           ├── sys-fs-fuse-connections.mount
    │   │           ├── sysinit.target
    │   │           ├── sysinit.target.wants
    │   │           │   ├── cryptsetup.target
    │   │           │   ├── dev-hugepages.mount
    │   │           │   ├── dev-mqueue.mount
    │   │           │   ├── integritysetup.target
    │   │           │   ├── kmod-static-nodes.service
    │   │           │   ├── ldconfig.service
    │   │           │   ├── plymouth-read-write.service
    │   │           │   ├── plymouth-start.service
    │   │           │   ├── proc-sys-fs-binfmt_misc.automount
    │   │           │   ├── sys-fs-fuse-connections.mount
    │   │           │   ├── sys-kernel-config.mount
    │   │           │   ├── sys-kernel-debug.mount
    │   │           │   ├── sys-kernel-tracing.mount
    │   │           │   ├── systemd-ask-password-console.path
    │   │           │   ├── systemd-binfmt.service
    │   │           │   ├── systemd-firstboot.service
    │   │           │   ├── systemd-hwdb-update.service
    │   │           │   ├── systemd-journal-catalog-update.service
    │   │           │   ├── systemd-journald.service
    │   │           │   ├── systemd-journal-flush.service
    │   │           │   ├── systemd-machine-id-commit.service
    │   │           │   ├── systemd-modules-load.service
    │   │           │   ├── systemd-pcrmachine.service
    │   │           │   ├── systemd-pcrphase.service
    │   │           │   ├── systemd-pcrphase-sysinit.service
    │   │           │   ├── systemd-random-seed.service
    │   │           │   ├── systemd-repart.service
    │   │           │   ├── systemd-sysctl.service
    │   │           │   ├── systemd-sysusers.service
    │   │           │   ├── systemd-tmpfiles-setup-dev-early.service
    │   │           │   ├── systemd-tmpfiles-setup-dev.service
    │   │           │   ├── systemd-tmpfiles-setup.service
    │   │           │   ├── systemd-tpm2-setup-early.service
    │   │           │   ├── systemd-tpm2-setup.service
    │   │           │   ├── systemd-udevd.service
    │   │           │   ├── systemd-udev-trigger.service
    │   │           │   ├── systemd-update-done.service
    │   │           │   ├── systemd-update-utmp.service
    │   │           │   └── veritysetup.target
    │   │           ├── sys-kernel-config.mount
    │   │           ├── sys-kernel-debug.mount
    │   │           ├── sys-kernel-tracing.mount
    │   │           ├── syslog.socket
    │   │           ├── sysstat-collect.service
    │   │           ├── sysstat-collect.timer
    │   │           ├── sysstat.service
    │   │           ├── sysstat-summary.service
    │   │           ├── sysstat-summary.timer
    │   │           ├── systemd-ask-password-console.path
    │   │           ├── systemd-ask-password-console.service
    │   │           ├── systemd-ask-password-plymouth.path
    │   │           ├── systemd-ask-password-plymouth.service
    │   │           ├── systemd-ask-password-wall.path
    │   │           ├── systemd-ask-password-wall.service
    │   │           ├── systemd-backlight@.service
    │   │           ├── systemd-battery-check.service
    │   │           ├── systemd-binfmt.service
    │   │           ├── systemd-boot-check-no-failures.service
    │   │           ├── systemd-bsod.service
    │   │           ├── systemd-confext.service
    │   │           ├── systemd-coredump@.service.d
    │   │           │   └── apport-coredump-hook.conf
    │   │           ├── systemd-exit.service
    │   │           ├── systemd-firstboot.service
    │   │           ├── systemd-fsckd.service
    │   │           ├── systemd-fsckd.socket
    │   │           ├── systemd-fsck-root.service
    │   │           ├── systemd-fsck@.service
    │   │           ├── systemd-growfs-root.service
    │   │           ├── systemd-growfs@.service
    │   │           ├── systemd-halt.service
    │   │           ├── systemd-hibernate-resume.service
    │   │           ├── systemd-hibernate.service
    │   │           ├── systemd-hostnamed.service
    │   │           ├── systemd-hwdb-update.service
    │   │           ├── systemd-hybrid-sleep.service
    │   │           ├── systemd-initctl.service
    │   │           ├── systemd-initctl.socket
    │   │           ├── systemd-journal-catalog-update.service
    │   │           ├── systemd-journald-audit.socket
    │   │           ├── systemd-journald-dev-log.socket
    │   │           ├── systemd-journald.service
    │   │           ├── systemd-journald@.service
    │   │           ├── systemd-journald.service.d
    │   │           │   └── nice.conf
    │   │           ├── systemd-journald.socket
    │   │           ├── systemd-journald@.socket
    │   │           ├── systemd-journald-varlink@.socket
    │   │           ├── systemd-journal-flush.service
    │   │           ├── systemd-kexec.service
    │   │           ├── systemd-localed.service
    │   │           ├── systemd-localed.service.d
    │   │           │   └── x11-keyboard.conf
    │   │           ├── systemd-logind.service
    │   │           ├── systemd-logind.service.d
    │   │           │   └── dbus.conf
    │   │           ├── systemd-machine-id-commit.service
    │   │           ├── systemd-modules-load.service
    │   │           ├── systemd-networkd.service
    │   │           ├── systemd-networkd.socket
    │   │           ├── systemd-networkd-wait-online.service
    │   │           ├── systemd-networkd-wait-online@.service
    │   │           ├── systemd-network-generator.service
    │   │           ├── systemd-pcrextend@.service
    │   │           ├── systemd-pcrextend.socket
    │   │           ├── systemd-pcrfs-root.service
    │   │           ├── systemd-pcrfs@.service
    │   │           ├── systemd-pcrlock-file-system.service
    │   │           ├── systemd-pcrlock-firmware-code.service
    │   │           ├── systemd-pcrlock-firmware-config.service
    │   │           ├── systemd-pcrlock-machine-id.service
    │   │           ├── systemd-pcrlock-make-policy.service
    │   │           ├── systemd-pcrlock-secureboot-authority.service
    │   │           ├── systemd-pcrlock-secureboot-policy.service
    │   │           ├── systemd-pcrmachine.service
    │   │           ├── systemd-pcrphase-initrd.service
    │   │           ├── systemd-pcrphase.service
    │   │           ├── systemd-pcrphase-sysinit.service
    │   │           ├── systemd-poweroff.service
    │   │           ├── systemd-pstore.service
    │   │           ├── systemd-quotacheck.service
    │   │           ├── systemd-random-seed.service
    │   │           ├── systemd-reboot.service
    │   │           ├── systemd-remount-fs.service
    │   │           ├── systemd-repart.service
    │   │           ├── systemd-resolved.service
    │   │           ├── systemd-rfkill.service
    │   │           ├── systemd-rfkill.socket
    │   │           ├── systemd-soft-reboot.service
    │   │           ├── systemd-storagetm.service
    │   │           ├── systemd-suspend.service
    │   │           ├── systemd-suspend-then-hibernate.service
    │   │           ├── systemd-sysctl.service
    │   │           ├── systemd-sysext.service
    │   │           ├── systemd-sysext@.service
    │   │           ├── systemd-sysext.socket
    │   │           ├── systemd-sysupdate-reboot.service
    │   │           ├── systemd-sysupdate-reboot.timer
    │   │           ├── systemd-sysupdate.service
    │   │           ├── systemd-sysupdate.timer
    │   │           ├── systemd-sysusers.service
    │   │           ├── systemd-timedated.service
    │   │           ├── systemd-time-wait-sync.service
    │   │           ├── systemd-tmpfiles-clean.service
    │   │           ├── systemd-tmpfiles-clean.timer
    │   │           ├── systemd-tmpfiles-setup-dev-early.service
    │   │           ├── systemd-tmpfiles-setup-dev.service
    │   │           ├── systemd-tmpfiles-setup.service
    │   │           ├── systemd-tpm2-setup-early.service
    │   │           ├── systemd-tpm2-setup.service
    │   │           ├── systemd-udevd-control.socket
    │   │           ├── systemd-udevd-kernel.socket
    │   │           ├── systemd-udevd.service
    │   │           ├── systemd-udevd.service.d
    │   │           │   └── syscall-architecture.conf
    │   │           ├── systemd-udev-settle.service
    │   │           ├── systemd-udev-trigger.service
    │   │           ├── systemd-update-done.service
    │   │           ├── systemd-update-utmp-runlevel.service
    │   │           ├── systemd-update-utmp.service
    │   │           ├── systemd-user-sessions.service
    │   │           ├── systemd-volatile-root.service
    │   │           ├── system-update-cleanup.service
    │   │           ├── system-update-pre.target
    │   │           ├── system-update.target
    │   │           ├── system-update.target.wants
    │   │           │   ├── fwupd-offline-update.service
    │   │           │   └── packagekit-offline-update.service
    │   │           ├── timers.target
    │   │           ├── timers.target.wants
    │   │           │   └── systemd-tmpfiles-clean.timer
    │   │           ├── time-set.target
    │   │           ├── time-sync.target
    │   │           ├── tpm-udev.path
    │   │           ├── tpm-udev.service
    │   │           ├── ua-reboot-cmds.service
    │   │           ├── ua-timer.service
    │   │           ├── ua-timer.timer
    │   │           ├── ubuntu-advantage.service
    │   │           ├── udev.service
    │   │           ├── udisks2.service
    │   │           ├── ufw.service
    │   │           ├── umount.target
    │   │           ├── unattended-upgrades.service
    │   │           ├── update-notifier-download.service
    │   │           ├── update-notifier-download.timer
    │   │           ├── update-notifier-motd.service
    │   │           ├── update-notifier-motd.timer
    │   │           ├── usb-gadget.target
    │   │           ├── usb_modeswitch@.service
    │   │           ├── user@0.service.d
    │   │           │   └── 10-login-barrier.conf
    │   │           ├── user-runtime-dir@.service
    │   │           ├── user@.service
    │   │           ├── user@.service.d
    │   │           │   ├── 10-login-barrier.conf
    │   │           │   └── timeout.conf
    │   │           ├── user.slice
    │   │           ├── user-.slice.d
    │   │           │   └── 10-defaults.conf
    │   │           ├── uuidd.service
    │   │           ├── uuidd.socket
    │   │           ├── veritysetup-pre.target
    │   │           ├── veritysetup.target
    │   │           ├── vgauth.service
    │   │           ├── x11-common.service
    │   │           ├── xfs_scrub_all.service
    │   │           ├── xfs_scrub_all.timer
    │   │           ├── xfs_scrub_fail@.service
    │   │           └── xfs_scrub@.service
    │   ├── root
    │   ├── run
    │   │   ├── shm
    │   │   └── systemd
    │   │       ├── sessions
    │   │       │   └── 14
    │   │       ├── system
    │   │       │   ├── netplan-ovs-cleanup.service
    │   │       │   ├── snap.lxd.daemon.service.d
    │   │       │   │   └── lxd-shutdown.conf
    │   │       │   ├── systemd-networkd.service.wants
    │   │       │   │   └── netplan-ovs-cleanup.service
    │   │       │   └── systemd-networkd-wait-online.service.d
    │   │       │       └── 10-netplan.conf
    │   │       └── transient
    │   │           ├── session-14.scope
    │   │           └── snap.lxd.workaround.service
    │   ├── snap
    │   │   └── core22
    │   │       └── 2133
    │   │           └── usr
    │   │               └── lib
    │   │                   └── udev
    │   │                       └── rules.d
    │   │                           ├── 40-vm-hotadd.rules
    │   │                           ├── 50-firmware.rules
    │   │                           ├── 50-udev-default.rules
    │   │                           ├── 55-dm.rules
    │   │                           ├── 60-autosuspend.rules
    │   │                           ├── 60-block.rules
    │   │                           ├── 60-cdrom_id.rules
    │   │                           ├── 60-drm.rules
    │   │                           ├── 60-evdev.rules
    │   │                           ├── 60-fido-id.rules
    │   │                           ├── 60-input-id.rules
    │   │                           ├── 60-persistent-alsa.rules
    │   │                           ├── 60-persistent-input.rules
    │   │                           ├── 60-persistent-storage-dm.rules
    │   │                           ├── 60-persistent-storage.rules
    │   │                           ├── 60-persistent-storage-tape.rules
    │   │                           ├── 60-persistent-v4l.rules
    │   │                           ├── 60-sensor.rules
    │   │                           ├── 60-serial.rules
    │   │                           ├── 61-persistent-storage-android.rules
    │   │                           ├── 64-btrfs.rules
    │   │                           ├── 66-azure-ephemeral.rules
    │   │                           ├── 66-snapd-autoimport.rules
    │   │                           ├── 70-joystick.rules
    │   │                           ├── 70-memory.rules
    │   │                           ├── 70-mouse.rules
    │   │                           ├── 70-power-switch.rules
    │   │                           ├── 70-touchpad.rules
    │   │                           ├── 70-uaccess.rules
    │   │                           ├── 71-nvidia.rules
    │   │                           ├── 71-power-switch-proliant.rules
    │   │                           ├── 71-seat.rules
    │   │                           ├── 73-seat-late.rules
    │   │                           ├── 73-special-net-names.rules
    │   │                           ├── 75-net-description.rules
    │   │                           ├── 75-probe_mtd.rules
    │   │                           ├── 78-graphics-card.rules
    │   │                           ├── 78-sound-card.rules
    │   │                           ├── 80-debian-compat.rules
    │   │                           ├── 80-drivers.rules
    │   │                           ├── 80-net-setup-link.rules
    │   │                           ├── 81-net-dhcp.rules
    │   │                           ├── 90-rtc-sys-time-init.rules
    │   │                           ├── 95-dm-notify.rules
    │   │                           ├── 96-e2scrub.rules
    │   │                           └── 99-systemd.rules
    │   ├── usr
    │   │   └── lib
    │   │       ├── systemd
    │   │       │   ├── catalog
    │   │       │   │   ├── systemd.be.catalog
    │   │       │   │   ├── systemd.be@latin.catalog
    │   │       │   │   ├── systemd.bg.catalog
    │   │       │   │   ├── systemd.catalog
    │   │       │   │   ├── systemd.da.catalog
    │   │       │   │   ├── systemd.de.catalog
    │   │       │   │   ├── systemd.fr.catalog
    │   │       │   │   ├── systemd.hr.catalog
    │   │       │   │   ├── systemd.hu.catalog
    │   │       │   │   ├── systemd.it.catalog
    │   │       │   │   ├── systemd.ko.catalog
    │   │       │   │   ├── systemd.pl.catalog
    │   │       │   │   ├── systemd.pt_BR.catalog
    │   │       │   │   ├── systemd.ru.catalog
    │   │       │   │   ├── systemd.sr.catalog
    │   │       │   │   ├── systemd.zh_CN.catalog
    │   │       │   │   └── systemd.zh_TW.catalog
    │   │       │   ├── journald.conf.d
    │   │       │   │   └── syslog.conf
    │   │       │   ├── logind.conf.d
    │   │       │   │   ├── ec2-hibinit-agent-ignore-powerkey.conf
    │   │       │   │   └── unattended-upgrades-logind-maxdelay.conf
    │   │       │   ├── lxd-agent-setup
    │   │       │   ├── network
    │   │       │   │   ├── 73-usb-net-by-mac.link
    │   │       │   │   ├── 80-6rd-tunnel.network
    │   │       │   │   ├── 80-auto-link-local.network.example
    │   │       │   │   ├── 80-container-host0.network
    │   │       │   │   ├── 80-container-vb.network
    │   │       │   │   ├── 80-container-ve.network
    │   │       │   │   ├── 80-container-vz.network
    │   │       │   │   ├── 80-vm-vt.network
    │   │       │   │   ├── 80-wifi-adhoc.network
    │   │       │   │   ├── 80-wifi-ap.network.example
    │   │       │   │   ├── 80-wifi-station.network.example
    │   │       │   │   ├── 89-ethernet.network.example
    │   │       │   │   └── 99-default.link
    │   │       │   ├── ntp-units.d
    │   │       │   │   └── 50-chrony.list
    │   │       │   ├── repart
    │   │       │   │   └── definitions
    │   │       │   │       ├── confext.repart.d
    │   │       │   │       │   ├── 10-root.conf
    │   │       │   │       │   ├── 20-root-verity.conf
    │   │       │   │       │   └── 30-root-verity-sig.conf
    │   │       │   │       ├── portable.repart.d
    │   │       │   │       │   ├── 10-root.conf
    │   │       │   │       │   ├── 20-root-verity.conf
    │   │       │   │       │   └── 30-root-verity-sig.conf
    │   │       │   │       └── sysext.repart.d
    │   │       │   │           ├── 10-root.conf
    │   │       │   │           ├── 20-root-verity.conf
    │   │       │   │           └── 30-root-verity-sig.conf
    │   │       │   ├── resolv.conf
    │   │       │   ├── scripts
    │   │       │   │   └── chronyd-starter.sh
    │   │       │   ├── sleep.conf.d
    │   │       │   │   └── ec2-hibinit-agent-no-suspend.conf
    │   │       │   ├── system
    │   │       │   │   ├── acpid.path
    │   │       │   │   ├── acpid.service
    │   │       │   │   ├── acpid.socket
    │   │       │   │   ├── apparmor.service
    │   │       │   │   ├── apport-autoreport.path
    │   │       │   │   ├── apport-autoreport.service
    │   │       │   │   ├── apport-autoreport.timer
    │   │       │   │   ├── apport-coredump-hook@.service
    │   │       │   │   ├── apport-forward@.service
    │   │       │   │   ├── apport-forward.socket
    │   │       │   │   ├── apport.service
    │   │       │   │   ├── apt-daily.service
    │   │       │   │   ├── apt-daily.timer
    │   │       │   │   ├── apt-daily-upgrade.service
    │   │       │   │   ├── apt-daily-upgrade.timer
    │   │       │   │   ├── apt-news.service
    │   │       │   │   ├── autovt@.service
    │   │       │   │   ├── basic.target
    │   │       │   │   ├── blk-availability.service
    │   │       │   │   ├── blockdev@.target
    │   │       │   │   ├── bluetooth.target
    │   │       │   │   ├── bolt.service
    │   │       │   │   ├── boot-complete.target
    │   │       │   │   ├── chrony-dnssrv@.service
    │   │       │   │   ├── chrony-dnssrv@.timer
    │   │       │   │   ├── chrony.service
    │   │       │   │   ├── chrony-wait.service
    │   │       │   │   ├── cloud-config.service
    │   │       │   │   ├── cloud-config.target
    │   │       │   │   ├── cloud-final.service
    │   │       │   │   ├── cloud-init-hotplugd.service
    │   │       │   │   ├── cloud-init-hotplugd.socket
    │   │       │   │   ├── cloud-init-local.service
    │   │       │   │   ├── cloud-init.service
    │   │       │   │   ├── cloud-init.target
    │   │       │   │   ├── console-getty.service
    │   │       │   │   ├── console-setup.service
    │   │       │   │   ├── container-getty@.service
    │   │       │   │   ├── cron.service
    │   │       │   │   ├── cryptdisks-early.service
    │   │       │   │   ├── cryptdisks.service
    │   │       │   │   ├── cryptsetup-pre.target
    │   │       │   │   ├── cryptsetup.target
    │   │       │   │   ├── ctrl-alt-del.target
    │   │       │   │   ├── dbus-org.freedesktop.hostname1.service
    │   │       │   │   ├── dbus-org.freedesktop.locale1.service
    │   │       │   │   ├── dbus-org.freedesktop.login1.service
    │   │       │   │   ├── dbus-org.freedesktop.timedate1.service
    │   │       │   │   ├── dbus.service
    │   │       │   │   ├── dbus.socket
    │   │       │   │   ├── debug-shell.service
    │   │       │   │   ├── default.target
    │   │       │   │   ├── dev-hugepages.mount
    │   │       │   │   ├── dev-mqueue.mount
    │   │       │   │   ├── dmesg.service
    │   │       │   │   ├── dm-event.service
    │   │       │   │   ├── dm-event.socket
    │   │       │   │   ├── dpkg-db-backup.service
    │   │       │   │   ├── dpkg-db-backup.timer
    │   │       │   │   ├── e2scrub_all.service
    │   │       │   │   ├── e2scrub_all.timer
    │   │       │   │   ├── e2scrub_fail@.service
    │   │       │   │   ├── e2scrub_reap.service
    │   │       │   │   ├── e2scrub@.service
    │   │       │   │   ├── ec2-instance-connect-harvest-hostkeys.service
    │   │       │   │   ├── emergency.service
    │   │       │   │   ├── emergency.target
    │   │       │   │   ├── esm-cache.service
    │   │       │   │   ├── exit.target
    │   │       │   │   ├── factory-reset.target
    │   │       │   │   ├── finalrd.service
    │   │       │   │   ├── final.target
    │   │       │   │   ├── first-boot-complete.target
    │   │       │   │   ├── friendly-recovery.service
    │   │       │   │   ├── friendly-recovery.target
    │   │       │   │   ├── fstrim.service
    │   │       │   │   ├── fstrim.timer
    │   │       │   │   ├── fwupd-offline-update.service
    │   │       │   │   ├── fwupd-refresh.service
    │   │       │   │   ├── fwupd-refresh.timer
    │   │       │   │   ├── fwupd.service
    │   │       │   │   ├── getty-pre.target
    │   │       │   │   ├── getty@.service
    │   │       │   │   ├── getty-static.service
    │   │       │   │   ├── getty.target
    │   │       │   │   ├── getty.target.wants
    │   │       │   │   │   └── getty-static.service
    │   │       │   │   ├── graphical.target
    │   │       │   │   ├── graphical.target.wants
    │   │       │   │   │   └── systemd-update-utmp-runlevel.service
    │   │       │   │   ├── grub-common.service
    │   │       │   │   ├── grub-initrd-fallback.service
    │   │       │   │   ├── halt.target
    │   │       │   │   ├── halt.target.wants
    │   │       │   │   │   ├── plymouth-halt.service
    │   │       │   │   │   └── plymouth-switch-root-initramfs.service
    │   │       │   │   ├── hibernate.target
    │   │       │   │   ├── hibinit-agent.service
    │   │       │   │   ├── hwclock.service
    │   │       │   │   ├── hybrid-sleep.target
    │   │       │   │   ├── initrd-cleanup.service
    │   │       │   │   ├── initrd-fs.target
    │   │       │   │   ├── initrd-parse-etc.service
    │   │       │   │   ├── initrd-root-device.target
    │   │       │   │   ├── initrd-root-device.target.wants
    │   │       │   │   │   ├── remote-cryptsetup.target
    │   │       │   │   │   └── remote-veritysetup.target
    │   │       │   │   ├── initrd-root-fs.target
    │   │       │   │   ├── initrd-root-fs.target.wants
    │   │       │   │   │   └── systemd-repart.service
    │   │       │   │   ├── initrd-switch-root.service
    │   │       │   │   ├── initrd-switch-root.target
    │   │       │   │   ├── initrd-switch-root.target.wants
    │   │       │   │   │   ├── plymouth-start.service
    │   │       │   │   │   └── plymouth-switch-root.service
    │   │       │   │   ├── initrd.target
    │   │       │   │   ├── initrd.target.wants
    │   │       │   │   │   ├── systemd-battery-check.service
    │   │       │   │   │   ├── systemd-bsod.service
    │   │       │   │   │   └── systemd-pcrphase-initrd.service
    │   │       │   │   ├── initrd-udevadm-cleanup-db.service
    │   │       │   │   ├── initrd-usr-fs.target
    │   │       │   │   ├── integritysetup-pre.target
    │   │       │   │   ├── integritysetup.target
    │   │       │   │   ├── irqbalance.service
    │   │       │   │   ├── iscsid.service
    │   │       │   │   ├── iscsid.socket
    │   │       │   │   ├── kexec.target
    │   │       │   │   ├── kexec.target.wants
    │   │       │   │   │   ├── plymouth-kexec.service
    │   │       │   │   │   └── plymouth-switch-root-initramfs.service
    │   │       │   │   ├── keyboard-setup.service
    │   │       │   │   ├── kmod.service
    │   │       │   │   ├── kmod-static-nodes.service
    │   │       │   │   ├── ldconfig.service
    │   │       │   │   ├── local-fs-pre.target
    │   │       │   │   ├── local-fs.target
    │   │       │   │   ├── logrotate.service
    │   │       │   │   ├── logrotate.timer
    │   │       │   │   ├── lvm2-lvmpolld.service
    │   │       │   │   ├── lvm2-lvmpolld.socket
    │   │       │   │   ├── lvm2-monitor.service
    │   │       │   │   ├── lxd-agent.service
    │   │       │   │   ├── lxd-installer@.service
    │   │       │   │   ├── lxd-installer.socket
    │   │       │   │   ├── machine.slice
    │   │       │   │   ├── man-db.service
    │   │       │   │   ├── man-db.timer
    │   │       │   │   ├── mdadm-grow-continue@.service
    │   │       │   │   ├── mdadm-last-resort@.service
    │   │       │   │   ├── mdadm-last-resort@.timer
    │   │       │   │   ├── mdcheck_continue.service
    │   │       │   │   ├── mdcheck_continue.timer
    │   │       │   │   ├── mdcheck_start.service
    │   │       │   │   ├── mdcheck_start.timer
    │   │       │   │   ├── mdmonitor-oneshot.service
    │   │       │   │   ├── mdmonitor-oneshot.timer
    │   │       │   │   ├── mdmonitor.service
    │   │       │   │   ├── mdmon@.service
    │   │       │   │   ├── ModemManager.service
    │   │       │   │   ├── modprobe@.service
    │   │       │   │   ├── mongod.service
    │   │       │   │   ├── motd-news.service
    │   │       │   │   ├── motd-news.timer
    │   │       │   │   ├── multipathd.service
    │   │       │   │   ├── multipathd.socket
    │   │       │   │   ├── multipath-tools-boot.service
    │   │       │   │   ├── multipath-tools.service
    │   │       │   │   ├── multi-user.target
    │   │       │   │   ├── multi-user.target.wants
    │   │       │   │   │   ├── dbus.service
    │   │       │   │   │   ├── getty.target
    │   │       │   │   │   ├── plymouth-quit.service
    │   │       │   │   │   ├── plymouth-quit-wait.service
    │   │       │   │   │   ├── systemd-ask-password-wall.path
    │   │       │   │   │   ├── systemd-logind.service
    │   │       │   │   │   ├── systemd-update-utmp-runlevel.service
    │   │       │   │   │   └── systemd-user-sessions.service
    │   │       │   │   ├── networkd-dispatcher.service
    │   │       │   │   ├── network-online.target
    │   │       │   │   ├── network-pre.target
    │   │       │   │   ├── network.target
    │   │       │   │   ├── nftables.service
    │   │       │   │   ├── nss-lookup.target
    │   │       │   │   ├── nss-user-lookup.target
    │   │       │   │   ├── open-iscsi.service
    │   │       │   │   ├── open-vm-tools.service
    │   │       │   │   ├── packagekit-offline-update.service
    │   │       │   │   ├── packagekit.service
    │   │       │   │   ├── pam_namespace.service
    │   │       │   │   ├── paths.target
    │   │       │   │   ├── plymouth-halt.service
    │   │       │   │   ├── plymouth-kexec.service
    │   │       │   │   ├── plymouth-log.service
    │   │       │   │   ├── plymouth-poweroff.service
    │   │       │   │   ├── plymouth-quit.service
    │   │       │   │   ├── plymouth-quit-wait.service
    │   │       │   │   ├── plymouth-read-write.service
    │   │       │   │   ├── plymouth-reboot.service
    │   │       │   │   ├── plymouth.service
    │   │       │   │   ├── plymouth-start.service
    │   │       │   │   ├── plymouth-switch-root-initramfs.service
    │   │       │   │   ├── plymouth-switch-root.service
    │   │       │   │   ├── polkit.service
    │   │       │   │   ├── pollinate.service
    │   │       │   │   ├── poweroff.target
    │   │       │   │   ├── poweroff.target.wants
    │   │       │   │   │   ├── plymouth-poweroff.service
    │   │       │   │   │   └── plymouth-switch-root-initramfs.service
    │   │       │   │   ├── printer.target
    │   │       │   │   ├── procps.service
    │   │       │   │   ├── proc-sys-fs-binfmt_misc.automount
    │   │       │   │   ├── proc-sys-fs-binfmt_misc.mount
    │   │       │   │   ├── quotaon.service
    │   │       │   │   ├── rc-local.service
    │   │       │   │   ├── rc-local.service.d
    │   │       │   │   │   └── debian.conf
    │   │       │   │   ├── reboot.target
    │   │       │   │   ├── reboot.target.wants
    │   │       │   │   │   ├── plymouth-reboot.service
    │   │       │   │   │   └── plymouth-switch-root-initramfs.service
    │   │       │   │   ├── remote-cryptsetup.target
    │   │       │   │   ├── remote-fs-pre.target
    │   │       │   │   ├── remote-fs.target
    │   │       │   │   ├── remote-veritysetup.target
    │   │       │   │   ├── rescue.service
    │   │       │   │   ├── rescue-ssh.target
    │   │       │   │   ├── rescue.target
    │   │       │   │   ├── rescue.target.wants
    │   │       │   │   │   └── systemd-update-utmp-runlevel.service
    │   │       │   │   ├── rpcbind.target
    │   │       │   │   ├── rsync.service
    │   │       │   │   ├── rsyslog.service
    │   │       │   │   ├── runlevel0.target
    │   │       │   │   ├── runlevel1.target
    │   │       │   │   ├── runlevel2.target
    │   │       │   │   ├── runlevel3.target
    │   │       │   │   ├── runlevel4.target
    │   │       │   │   ├── runlevel5.target
    │   │       │   │   ├── runlevel6.target
    │   │       │   │   ├── screen-cleanup.service
    │   │       │   │   ├── secureboot-db.service
    │   │       │   │   ├── serial-getty@.service
    │   │       │   │   ├── setvtrgb.service
    │   │       │   │   ├── shutdown.target
    │   │       │   │   ├── sigpwr.target
    │   │       │   │   ├── sleep.target
    │   │       │   │   ├── slices.target
    │   │       │   │   ├── smartcard.target
    │   │       │   │   ├── snapd.apparmor.service
    │   │       │   │   ├── snapd.autoimport.service
    │   │       │   │   ├── snapd.core-fixup.service
    │   │       │   │   ├── snapd.failure.service
    │   │       │   │   ├── snapd.gpio-chardev-setup.target
    │   │       │   │   ├── snapd.mounts-pre.target
    │   │       │   │   ├── snapd.mounts.target
    │   │       │   │   ├── snapd.recovery-chooser-trigger.service
    │   │       │   │   ├── snapd.seeded.service
    │   │       │   │   ├── snapd.service
    │   │       │   │   ├── snapd.snap-repair.service
    │   │       │   │   ├── snapd.snap-repair.timer
    │   │       │   │   ├── snapd.socket
    │   │       │   │   ├── snapd.system-shutdown.service
    │   │       │   │   ├── sockets.target
    │   │       │   │   ├── sockets.target.wants
    │   │       │   │   │   ├── dbus.socket
    │   │       │   │   │   ├── systemd-initctl.socket
    │   │       │   │   │   ├── systemd-journald-dev-log.socket
    │   │       │   │   │   ├── systemd-journald.socket
    │   │       │   │   │   ├── systemd-pcrextend.socket
    │   │       │   │   │   ├── systemd-sysext.socket
    │   │       │   │   │   ├── systemd-udevd-control.socket
    │   │       │   │   │   └── systemd-udevd-kernel.socket
    │   │       │   │   ├── soft-reboot.target
    │   │       │   │   ├── sound.target
    │   │       │   │   ├── sshd-keygen@.service.d
    │   │       │   │   │   └── disable-sshd-keygen-if-cloud-init-active.conf
    │   │       │   │   ├── ssh.service
    │   │       │   │   ├── ssh.service.d
    │   │       │   │   │   └── ec2-instance-connect.conf
    │   │       │   │   ├── ssh.socket
    │   │       │   │   ├── storage-target-mode.target
    │   │       │   │   ├── sudo.service
    │   │       │   │   ├── suspend.target
    │   │       │   │   ├── suspend-then-hibernate.target
    │   │       │   │   ├── swap.target
    │   │       │   │   ├── sys-fs-fuse-connections.mount
    │   │       │   │   ├── sysinit.target
    │   │       │   │   ├── sysinit.target.wants
    │   │       │   │   │   ├── cryptsetup.target
    │   │       │   │   │   ├── dev-hugepages.mount
    │   │       │   │   │   ├── dev-mqueue.mount
    │   │       │   │   │   ├── integritysetup.target
    │   │       │   │   │   ├── kmod-static-nodes.service
    │   │       │   │   │   ├── ldconfig.service
    │   │       │   │   │   ├── plymouth-read-write.service
    │   │       │   │   │   ├── plymouth-start.service
    │   │       │   │   │   ├── proc-sys-fs-binfmt_misc.automount
    │   │       │   │   │   ├── sys-fs-fuse-connections.mount
    │   │       │   │   │   ├── sys-kernel-config.mount
    │   │       │   │   │   ├── sys-kernel-debug.mount
    │   │       │   │   │   ├── sys-kernel-tracing.mount
    │   │       │   │   │   ├── systemd-ask-password-console.path
    │   │       │   │   │   ├── systemd-binfmt.service
    │   │       │   │   │   ├── systemd-firstboot.service
    │   │       │   │   │   ├── systemd-hwdb-update.service
    │   │       │   │   │   ├── systemd-journal-catalog-update.service
    │   │       │   │   │   ├── systemd-journald.service
    │   │       │   │   │   ├── systemd-journal-flush.service
    │   │       │   │   │   ├── systemd-machine-id-commit.service
    │   │       │   │   │   ├── systemd-modules-load.service
    │   │       │   │   │   ├── systemd-pcrmachine.service
    │   │       │   │   │   ├── systemd-pcrphase.service
    │   │       │   │   │   ├── systemd-pcrphase-sysinit.service
    │   │       │   │   │   ├── systemd-random-seed.service
    │   │       │   │   │   ├── systemd-repart.service
    │   │       │   │   │   ├── systemd-sysctl.service
    │   │       │   │   │   ├── systemd-sysusers.service
    │   │       │   │   │   ├── systemd-tmpfiles-setup-dev-early.service
    │   │       │   │   │   ├── systemd-tmpfiles-setup-dev.service
    │   │       │   │   │   ├── systemd-tmpfiles-setup.service
    │   │       │   │   │   ├── systemd-tpm2-setup-early.service
    │   │       │   │   │   ├── systemd-tpm2-setup.service
    │   │       │   │   │   ├── systemd-udevd.service
    │   │       │   │   │   ├── systemd-udev-trigger.service
    │   │       │   │   │   ├── systemd-update-done.service
    │   │       │   │   │   ├── systemd-update-utmp.service
    │   │       │   │   │   └── veritysetup.target
    │   │       │   │   ├── sys-kernel-config.mount
    │   │       │   │   ├── sys-kernel-debug.mount
    │   │       │   │   ├── sys-kernel-tracing.mount
    │   │       │   │   ├── syslog.socket
    │   │       │   │   ├── sysstat-collect.service
    │   │       │   │   ├── sysstat-collect.timer
    │   │       │   │   ├── sysstat.service
    │   │       │   │   ├── sysstat-summary.service
    │   │       │   │   ├── sysstat-summary.timer
    │   │       │   │   ├── systemd-ask-password-console.path
    │   │       │   │   ├── systemd-ask-password-console.service
    │   │       │   │   ├── systemd-ask-password-plymouth.path
    │   │       │   │   ├── systemd-ask-password-plymouth.service
    │   │       │   │   ├── systemd-ask-password-wall.path
    │   │       │   │   ├── systemd-ask-password-wall.service
    │   │       │   │   ├── systemd-backlight@.service
    │   │       │   │   ├── systemd-battery-check.service
    │   │       │   │   ├── systemd-binfmt.service
    │   │       │   │   ├── systemd-boot-check-no-failures.service
    │   │       │   │   ├── systemd-bsod.service
    │   │       │   │   ├── systemd-confext.service
    │   │       │   │   ├── systemd-coredump@.service.d
    │   │       │   │   │   └── apport-coredump-hook.conf
    │   │       │   │   ├── systemd-exit.service
    │   │       │   │   ├── systemd-firstboot.service
    │   │       │   │   ├── systemd-fsckd.service
    │   │       │   │   ├── systemd-fsckd.socket
    │   │       │   │   ├── systemd-fsck-root.service
    │   │       │   │   ├── systemd-fsck@.service
    │   │       │   │   ├── systemd-growfs-root.service
    │   │       │   │   ├── systemd-growfs@.service
    │   │       │   │   ├── systemd-halt.service
    │   │       │   │   ├── systemd-hibernate-resume.service
    │   │       │   │   ├── systemd-hibernate.service
    │   │       │   │   ├── systemd-hostnamed.service
    │   │       │   │   ├── systemd-hwdb-update.service
    │   │       │   │   ├── systemd-hybrid-sleep.service
    │   │       │   │   ├── systemd-initctl.service
    │   │       │   │   ├── systemd-initctl.socket
    │   │       │   │   ├── systemd-journal-catalog-update.service
    │   │       │   │   ├── systemd-journald-audit.socket
    │   │       │   │   ├── systemd-journald-dev-log.socket
    │   │       │   │   ├── systemd-journald.service
    │   │       │   │   ├── systemd-journald@.service
    │   │       │   │   ├── systemd-journald.service.d
    │   │       │   │   │   └── nice.conf
    │   │       │   │   ├── systemd-journald.socket
    │   │       │   │   ├── systemd-journald@.socket
    │   │       │   │   ├── systemd-journald-varlink@.socket
    │   │       │   │   ├── systemd-journal-flush.service
    │   │       │   │   ├── systemd-kexec.service
    │   │       │   │   ├── systemd-localed.service
    │   │       │   │   ├── systemd-localed.service.d
    │   │       │   │   │   └── x11-keyboard.conf
    │   │       │   │   ├── systemd-logind.service
    │   │       │   │   ├── systemd-logind.service.d
    │   │       │   │   │   └── dbus.conf
    │   │       │   │   ├── systemd-machine-id-commit.service
    │   │       │   │   ├── systemd-modules-load.service
    │   │       │   │   ├── systemd-networkd.service
    │   │       │   │   ├── systemd-networkd.socket
    │   │       │   │   ├── systemd-networkd-wait-online.service
    │   │       │   │   ├── systemd-networkd-wait-online@.service
    │   │       │   │   ├── systemd-network-generator.service
    │   │       │   │   ├── systemd-pcrextend@.service
    │   │       │   │   ├── systemd-pcrextend.socket
    │   │       │   │   ├── systemd-pcrfs-root.service
    │   │       │   │   ├── systemd-pcrfs@.service
    │   │       │   │   ├── systemd-pcrlock-file-system.service
    │   │       │   │   ├── systemd-pcrlock-firmware-code.service
    │   │       │   │   ├── systemd-pcrlock-firmware-config.service
    │   │       │   │   ├── systemd-pcrlock-machine-id.service
    │   │       │   │   ├── systemd-pcrlock-make-policy.service
    │   │       │   │   ├── systemd-pcrlock-secureboot-authority.service
    │   │       │   │   ├── systemd-pcrlock-secureboot-policy.service
    │   │       │   │   ├── systemd-pcrmachine.service
    │   │       │   │   ├── systemd-pcrphase-initrd.service
    │   │       │   │   ├── systemd-pcrphase.service
    │   │       │   │   ├── systemd-pcrphase-sysinit.service
    │   │       │   │   ├── systemd-poweroff.service
    │   │       │   │   ├── systemd-pstore.service
    │   │       │   │   ├── systemd-quotacheck.service
    │   │       │   │   ├── systemd-random-seed.service
    │   │       │   │   ├── systemd-reboot.service
    │   │       │   │   ├── systemd-remount-fs.service
    │   │       │   │   ├── systemd-repart.service
    │   │       │   │   ├── systemd-resolved.service
    │   │       │   │   ├── systemd-rfkill.service
    │   │       │   │   ├── systemd-rfkill.socket
    │   │       │   │   ├── systemd-soft-reboot.service
    │   │       │   │   ├── systemd-storagetm.service
    │   │       │   │   ├── systemd-suspend.service
    │   │       │   │   ├── systemd-suspend-then-hibernate.service
    │   │       │   │   ├── systemd-sysctl.service
    │   │       │   │   ├── systemd-sysext.service
    │   │       │   │   ├── systemd-sysext@.service
    │   │       │   │   ├── systemd-sysext.socket
    │   │       │   │   ├── systemd-sysupdate-reboot.service
    │   │       │   │   ├── systemd-sysupdate-reboot.timer
    │   │       │   │   ├── systemd-sysupdate.service
    │   │       │   │   ├── systemd-sysupdate.timer
    │   │       │   │   ├── systemd-sysusers.service
    │   │       │   │   ├── systemd-timedated.service
    │   │       │   │   ├── systemd-time-wait-sync.service
    │   │       │   │   ├── systemd-tmpfiles-clean.service
    │   │       │   │   ├── systemd-tmpfiles-clean.timer
    │   │       │   │   ├── systemd-tmpfiles-setup-dev-early.service
    │   │       │   │   ├── systemd-tmpfiles-setup-dev.service
    │   │       │   │   ├── systemd-tmpfiles-setup.service
    │   │       │   │   ├── systemd-tpm2-setup-early.service
    │   │       │   │   ├── systemd-tpm2-setup.service
    │   │       │   │   ├── systemd-udevd-control.socket
    │   │       │   │   ├── systemd-udevd-kernel.socket
    │   │       │   │   ├── systemd-udevd.service
    │   │       │   │   ├── systemd-udevd.service.d
    │   │       │   │   │   └── syscall-architecture.conf
    │   │       │   │   ├── systemd-udev-settle.service
    │   │       │   │   ├── systemd-udev-trigger.service
    │   │       │   │   ├── systemd-update-done.service
    │   │       │   │   ├── systemd-update-utmp-runlevel.service
    │   │       │   │   ├── systemd-update-utmp.service
    │   │       │   │   ├── systemd-user-sessions.service
    │   │       │   │   ├── systemd-volatile-root.service
    │   │       │   │   ├── system-update-cleanup.service
    │   │       │   │   ├── system-update-pre.target
    │   │       │   │   ├── system-update.target
    │   │       │   │   ├── system-update.target.wants
    │   │       │   │   │   ├── fwupd-offline-update.service
    │   │       │   │   │   └── packagekit-offline-update.service
    │   │       │   │   ├── timers.target
    │   │       │   │   ├── timers.target.wants
    │   │       │   │   │   └── systemd-tmpfiles-clean.timer
    │   │       │   │   ├── time-set.target
    │   │       │   │   ├── time-sync.target
    │   │       │   │   ├── tpm-udev.path
    │   │       │   │   ├── tpm-udev.service
    │   │       │   │   ├── ua-reboot-cmds.service
    │   │       │   │   ├── ua-timer.service
    │   │       │   │   ├── ua-timer.timer
    │   │       │   │   ├── ubuntu-advantage.service
    │   │       │   │   ├── udev.service
    │   │       │   │   ├── udisks2.service
    │   │       │   │   ├── ufw.service
    │   │       │   │   ├── umount.target
    │   │       │   │   ├── unattended-upgrades.service
    │   │       │   │   ├── update-notifier-download.service
    │   │       │   │   ├── update-notifier-download.timer
    │   │       │   │   ├── update-notifier-motd.service
    │   │       │   │   ├── update-notifier-motd.timer
    │   │       │   │   ├── usb-gadget.target
    │   │       │   │   ├── usb_modeswitch@.service
    │   │       │   │   ├── user@0.service.d
    │   │       │   │   │   └── 10-login-barrier.conf
    │   │       │   │   ├── user-runtime-dir@.service
    │   │       │   │   ├── user@.service
    │   │       │   │   ├── user@.service.d
    │   │       │   │   │   ├── 10-login-barrier.conf
    │   │       │   │   │   └── timeout.conf
    │   │       │   │   ├── user.slice
    │   │       │   │   ├── user-.slice.d
    │   │       │   │   │   └── 10-defaults.conf
    │   │       │   │   ├── uuidd.service
    │   │       │   │   ├── uuidd.socket
    │   │       │   │   ├── veritysetup-pre.target
    │   │       │   │   ├── veritysetup.target
    │   │       │   │   ├── vgauth.service
    │   │       │   │   ├── x11-common.service
    │   │       │   │   ├── xfs_scrub_all.service
    │   │       │   │   ├── xfs_scrub_all.timer
    │   │       │   │   ├── xfs_scrub_fail@.service
    │   │       │   │   └── xfs_scrub@.service
    │   │       │   ├── systemd
    │   │       │   ├── systemd-backlight
    │   │       │   ├── systemd-battery-check
    │   │       │   ├── systemd-binfmt
    │   │       │   ├── systemd-boot-check-no-failures
    │   │       │   ├── systemd-bsod
    │   │       │   ├── systemd-cgroups-agent
    │   │       │   ├── systemd-cryptsetup
    │   │       │   ├── systemd-executor
    │   │       │   ├── systemd-fsck
    │   │       │   ├── systemd-fsckd
    │   │       │   ├── systemd-growfs
    │   │       │   ├── systemd-hibernate-resume
    │   │       │   ├── systemd-hostnamed
    │   │       │   ├── systemd-initctl
    │   │       │   ├── systemd-integritysetup
    │   │       │   ├── systemd-journald
    │   │       │   ├── systemd-localed
    │   │       │   ├── systemd-logind
    │   │       │   ├── systemd-makefs
    │   │       │   ├── systemd-measure
    │   │       │   ├── systemd-modules-load
    │   │       │   ├── systemd-networkd
    │   │       │   ├── systemd-networkd-wait-online
    │   │       │   ├── systemd-network-generator
    │   │       │   ├── systemd-pcrextend
    │   │       │   ├── systemd-pcrlock
    │   │       │   ├── systemd-pstore
    │   │       │   ├── systemd-quotacheck
    │   │       │   ├── systemd-random-seed
    │   │       │   ├── systemd-remount-fs
    │   │       │   ├── systemd-reply-password
    │   │       │   ├── systemd-resolved
    │   │       │   ├── systemd-rfkill
    │   │       │   ├── systemd-shutdown
    │   │       │   ├── systemd-sleep
    │   │       │   ├── systemd-socket-proxyd
    │   │       │   ├── systemd-storagetm
    │   │       │   ├── systemd-sulogin-shell
    │   │       │   ├── systemd-sysctl
    │   │       │   ├── systemd-sysroot-fstab-check
    │   │       │   ├── systemd-sysupdate
    │   │       │   ├── systemd-sysv-install
    │   │       │   ├── systemd-timedated
    │   │       │   ├── systemd-time-wait-sync
    │   │       │   ├── systemd-tpm2-setup
    │   │       │   ├── systemd-udevd
    │   │       │   ├── systemd-update-done
    │   │       │   ├── systemd-update-utmp
    │   │       │   ├── systemd-user-runtime-dir
    │   │       │   ├── systemd-user-sessions
    │   │       │   ├── systemd-veritysetup
    │   │       │   ├── systemd-volatile-root
    │   │       │   ├── systemd-xdg-autostart-condition
    │   │       │   ├── system-environment-generators
    │   │       │   │   └── snapd-env-generator
    │   │       │   ├── system-generators
    │   │       │   │   ├── cloud-init-generator
    │   │       │   │   ├── friendly-recovery
    │   │       │   │   ├── netplan
    │   │       │   │   ├── snapd-generator
    │   │       │   │   ├── sshd-socket-generator
    │   │       │   │   ├── systemd-cryptsetup-generator
    │   │       │   │   ├── systemd-debug-generator
    │   │       │   │   ├── systemd-fstab-generator
    │   │       │   │   ├── systemd-getty-generator
    │   │       │   │   ├── systemd-gpt-auto-generator
    │   │       │   │   ├── systemd-hibernate-resume-generator
    │   │       │   │   ├── systemd-integritysetup-generator
    │   │       │   │   ├── systemd-rc-local-generator
    │   │       │   │   ├── systemd-run-generator
    │   │       │   │   ├── systemd-system-update-generator
    │   │       │   │   ├── systemd-sysv-generator
    │   │       │   │   └── systemd-veritysetup-generator
    │   │       │   ├── system-preset
    │   │       │   │   └── 90-systemd.preset
    │   │       │   ├── system-shutdown
    │   │       │   │   ├── fwupd.shutdown
    │   │       │   │   └── mdadm.shutdown
    │   │       │   ├── system-sleep
    │   │       │   │   ├── hdparm
    │   │       │   │   ├── hibinit-agent
    │   │       │   │   ├── sysstat.sleep
    │   │       │   │   └── unattended-upgrades
    │   │       │   ├── user
    │   │       │   │   ├── app.slice
    │   │       │   │   ├── background.slice
    │   │       │   │   ├── basic.target
    │   │       │   │   ├── bluetooth.target
    │   │       │   │   ├── dbus.service
    │   │       │   │   ├── dbus.socket
    │   │       │   │   ├── default.target
    │   │       │   │   ├── dirmngr.service
    │   │       │   │   ├── dirmngr.socket
    │   │       │   │   ├── exit.target
    │   │       │   │   ├── gpg-agent-browser.socket
    │   │       │   │   ├── gpg-agent-extra.socket
    │   │       │   │   ├── gpg-agent.service
    │   │       │   │   ├── gpg-agent.socket
    │   │       │   │   ├── gpg-agent-ssh.socket
    │   │       │   │   ├── graphical-session-pre.target
    │   │       │   │   ├── graphical-session-pre.target.wants
    │   │       │   │   │   └── ssh-agent.service
    │   │       │   │   ├── graphical-session.target
    │   │       │   │   ├── keyboxd.service
    │   │       │   │   ├── keyboxd.socket
    │   │       │   │   ├── launchpadlib-cache-clean.service
    │   │       │   │   ├── launchpadlib-cache-clean.timer
    │   │       │   │   ├── paths.target
    │   │       │   │   ├── pk-debconf-helper.service
    │   │       │   │   ├── pk-debconf-helper.socket
    │   │       │   │   ├── printer.target
    │   │       │   │   ├── session.slice
    │   │       │   │   ├── shutdown.target
    │   │       │   │   ├── smartcard.target
    │   │       │   │   ├── snapd.session-agent.service
    │   │       │   │   ├── snapd.session-agent.socket
    │   │       │   │   ├── sockets.target
    │   │       │   │   ├── sockets.target.wants
    │   │       │   │   │   ├── dbus.socket
    │   │       │   │   │   └── snapd.session-agent.socket
    │   │       │   │   ├── sound.target
    │   │       │   │   ├── ssh-agent.service
    │   │       │   │   ├── systemd-exit.service
    │   │       │   │   ├── systemd-tmpfiles-clean.service
    │   │       │   │   ├── systemd-tmpfiles-clean.timer
    │   │       │   │   ├── systemd-tmpfiles-setup.service
    │   │       │   │   ├── timers.target
    │   │       │   │   └── xdg-desktop-autostart.target
    │   │       │   ├── user-environment-generators
    │   │       │   │   └── 30-systemd-environment-d-generator
    │   │       │   ├── user-generators
    │   │       │   │   └── systemd-xdg-autostart-generator
    │   │       │   └── user-preset
    │   │       │       └── 90-systemd.preset
    │   │       └── udev
    │   │           └── rules.d
    │   │               ├── 01-md-raid-creating.rules
    │   │               ├── 40-usb_modeswitch.rules
    │   │               ├── 40-vm-hotadd.rules
    │   │               ├── 50-apport.rules
    │   │               ├── 50-firmware.rules
    │   │               ├── 50-udev-default.rules
    │   │               ├── 55-dm.rules
    │   │               ├── 55-scsi-sg3_id.rules
    │   │               ├── 56-dm-mpath.rules
    │   │               ├── 56-dm-parts.rules
    │   │               ├── 56-lvm.rules
    │   │               ├── 58-scsi-sg3_symlink.rules
    │   │               ├── 60-autosuspend.rules
    │   │               ├── 60-block.rules
    │   │               ├── 60-cdrom_id.rules
    │   │               ├── 60-dmi-id.rules
    │   │               ├── 60-drm.rules
    │   │               ├── 60-evdev.rules
    │   │               ├── 60-fido-id.rules
    │   │               ├── 60-infiniband.rules
    │   │               ├── 60-input-id.rules
    │   │               ├── 60-multipath.rules
    │   │               ├── 60-open-vm-tools.rules
    │   │               ├── 60-persistent-alsa.rules
    │   │               ├── 60-persistent-input.rules
    │   │               ├── 60-persistent-storage-dm.rules
    │   │               ├── 60-persistent-storage-mtd.rules
    │   │               ├── 60-persistent-storage.rules
    │   │               ├── 60-persistent-storage-tape.rules
    │   │               ├── 60-persistent-v4l.rules
    │   │               ├── 60-sensor.rules
    │   │               ├── 60-serial.rules
    │   │               ├── 60-tpm-udev.rules
    │   │               ├── 61-persistent-storage-android.rules
    │   │               ├── 63-md-raid-arrays.rules
    │   │               ├── 64-btrfs-dm.rules
    │   │               ├── 64-btrfs.rules
    │   │               ├── 64-btrfs-zoned.rules
    │   │               ├── 64-md-raid-assembly.rules
    │   │               ├── 64-xfs.rules
    │   │               ├── 66-azure-ephemeral.rules
    │   │               ├── 68-del-part-nodes.rules
    │   │               ├── 69-bcache.rules
    │   │               ├── 69-lvm.rules
    │   │               ├── 69-md-clustered-confirm-device.rules
    │   │               ├── 70-camera.rules
    │   │               ├── 70-iscsi-network-interface.rules
    │   │               ├── 70-joystick.rules
    │   │               ├── 70-memory.rules
    │   │               ├── 70-mouse.rules
    │   │               ├── 70-open-iscsi.rules
    │   │               ├── 70-power-switch.rules
    │   │               ├── 70-touchpad.rules
    │   │               ├── 70-uaccess.rules
    │   │               ├── 71-power-switch-proliant.rules
    │   │               ├── 71-seat.rules
    │   │               ├── 73-seat-late.rules
    │   │               ├── 73-special-net-names.rules
    │   │               ├── 75-net-description.rules
    │   │               ├── 75-probe_mtd.rules
    │   │               ├── 77-mm-broadmobi-port-types.rules
    │   │               ├── 77-mm-cinterion-port-types.rules
    │   │               ├── 77-mm-dell-port-types.rules
    │   │               ├── 77-mm-dlink-port-types.rules
    │   │               ├── 77-mm-ericsson-mbm.rules
    │   │               ├── 77-mm-fibocom-port-types.rules
    │   │               ├── 77-mm-foxconn-port-types.rules
    │   │               ├── 77-mm-gosuncn-port-types.rules
    │   │               ├── 77-mm-haier-port-types.rules
    │   │               ├── 77-mm-huawei-net-port-types.rules
    │   │               ├── 77-mm-linktop-port-types.rules
    │   │               ├── 77-mm-longcheer-port-types.rules
    │   │               ├── 77-mm-mtk-legacy-port-types.rules
    │   │               ├── 77-mm-mtk-port-types.rules
    │   │               ├── 77-mm-nokia-port-types.rules
    │   │               ├── 77-mm-qcom-soc.rules
    │   │               ├── 77-mm-qdl-device-blacklist.rules
    │   │               ├── 77-mm-quectel-port-types.rules
    │   │               ├── 77-mm-sierra.rules
    │   │               ├── 77-mm-simtech-port-types.rules
    │   │               ├── 77-mm-telit-port-types.rules
    │   │               ├── 77-mm-tplink-port-types.rules
    │   │               ├── 77-mm-ublox-port-types.rules
    │   │               ├── 77-mm-x22x-port-types.rules
    │   │               ├── 77-mm-zte-port-types.rules
    │   │               ├── 78-graphics-card.rules
    │   │               ├── 78-sound-card.rules
    │   │               ├── 80-debian-compat.rules
    │   │               ├── 80-drivers.rules
    │   │               ├── 80-mm-candidate.rules
    │   │               ├── 80-net-setup-link.rules
    │   │               ├── 80-udisks2.rules
    │   │               ├── 81-net-dhcp.rules
    │   │               ├── 85-hdparm.rules
    │   │               ├── 90-bolt.rules
    │   │               ├── 90-console-setup.rules
    │   │               ├── 90-fwupd-devices.rules
    │   │               ├── 90-iocost.rules
    │   │               ├── 95-dm-notify.rules
    │   │               ├── 95-kpartx.rules
    │   │               ├── 96-e2scrub.rules
    │   │               ├── 99-lxd-agent.rules
    │   │               ├── 99-systemd.rules
    │   │               └── 99-vmware-scsi-udev.rules
    │   └── var
    │       ├── lib
    │       │   └── dpkg
    │       │       └── status
    │       ├── log
    │       │   ├── alternatives.log
    │       │   ├── amazon
    │       │   │   └── ssm
    │       │   │       ├── amazon-ssm-agent.log
    │       │   │       ├── audits
    │       │   │       │   └── amazon-ssm-agent-audit-2025-12-29
    │       │   │       └── errors.log
    │       │   ├── apport.log
    │       │   ├── apt
    │       │   │   ├── eipp.log.xz
    │       │   │   ├── history.log
    │       │   │   └── term.log
    │       │   ├── auth.log
    │       │   ├── btmp
    │       │   ├── cloud-init.log
    │       │   ├── cloud-init-output.log
    │       │   ├── dmesg
    │       │   ├── dpkg.log
    │       │   ├── journal
    │       │   │   └── ec213a66bf5d5b9e224fd2c1585689ba
    │       │   │       ├── system.journal
    │       │   │       ├── user-1000.journal
    │       │   │       └── user-1001.journal
    │       │   ├── kern.log
    │       │   ├── landscape
    │       │   │   └── sysinfo.log
    │       │   ├── lastlog
    │       │   ├── mongodb
    │       │   │   └── mongod.log
    │       │   ├── README
    │       │   ├── syslog
    │       │   ├── sysstat
    │       │   │   └── sa29
    │       │   ├── unattended-upgrades
    │       │   │   ├── unattended-upgrades-dpkg.log
    │       │   │   ├── unattended-upgrades.log
    │       │   │   └── unattended-upgrades-shutdown.log
    │       │   └── wtmp
    │       ├── run
    │       │   └── utmp
    │       ├── snap
    │       │   └── lxd
    │       │       └── common
    │       │           └── lxd
    │       │               └── logs
    │       │                   └── lxd.log
    │       └── spool
    │           └── mail
    └── system
        ├── getcap.txt
        ├── group_name_unknown_files.txt
        ├── hidden_directories.txt
        ├── hidden_files.txt
        ├── sgid.txt
        ├── suid.txt
        ├── user_name_unknown_files.txt
        ├── world_writable_directories.txt
        └── world_writable_files.txt

677 directories, 4171 files

```

The five top-level folders each serve a distinct purpose in a UAC triage:

| Folder             | Contents                                                                                        | Purpose                                                                                                                               |
| ------------------ | ----------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------- |
| `bodyfile`         | `bodyfile.txt`                                                                                  | A timeline-formatted (MAC time — Modified/Accessed/Changed) listing of every file on the filesystem, used for timeline reconstruction |
| `hash_executables` | `.md5` / `.sha1` files                                                                          | Cryptographic hashes of executable files, used to detect known-malicious or tampered binaries                                         |
| `live_response`    | Subfolders like `network`, `process`, `hardware`, `storage`, `packages`, `containers`, `system` | Output of dozens of live commands (`ps`, `netstat`, `lsof`, etc.) run at acquisition time — a snapshot of the running system's state  |
| `[root]`           | A near-complete copy of the filesystem's `/etc`, `/home`, `/var`, `/usr`, `/root`, etc.         | The actual files pulled off disk — configs, logs, home directories — where most log-analysis work happens                             |
| `system`           | Files like `suid.txt`, `sgid.txt`, `world_writable_files.txt`, `hidden_files.txt`               | Results of automated checks for common privilege-escalation and persistence indicators                                                |
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
<br>
</div>

### CVE Identification

Before touching any logs, we should nail down exactly what vulnerability we're dealing with. The scenario names it "MongoBleed" but that's an informal/community name, not a CVE ID — and you'll need the real CVE ID for your report. **Run a Google search for `MongoBleed MongoDB vulnerability CVE`**.

Every publicly disclosed vulnerability gets a unique tracking number called a **CVE ID** (Common Vulnerabilities and Exposures ID), assigned by MITRE, in the format `CVE-YYYY-NNNNN`. Security reports and patch notes reference CVE IDs rather than nicknames, so before going any further you need to pin down the exact one this incident concerns.

**Research:** Google search — `MongoBleed MongoDB vulnerability CVE`

Quoted result (Google AI Overview):

> "MongoBleed (CVE-2025-14847) is a high-severity (CVSS 8.7) unauthenticated memory disclosure flaw in MongoDB. It occurs because of a bug in how MongoDB processes zlib-compressed network messages. By manipulating message length fields, attackers can trick the server into returning chunks of uninitialized heap memory.
> 
> **Key Details**  
> Impact: Unauthenticated attackers can remotely extract sensitive information like database credentials, cloud environment tokens, and session data without needing a password.  
> Affected Versions: Multiple supported and legacy MongoDB Server versions.  
> Exploitation: The vulnerability is easy to execute, requires no user interaction, and was actively exploited in the wild shortly after disclosure."

This confirms the CVE ID for this engagement is **CVE-2025-14847**, and tells us the mechanism: a length-field mismatch in zlib-decompression logic tricks the server into leaking uninitialized heap memory — data sitting in RAM from previous operations that was never meant to be sent over the network, similar in spirit to the 2014 "Heartbleed" bug in OpenSSL (hence the "-Bleed" naming pattern).

Research notes this CVE affects "multiple supported and legacy MongoDB Server versions" — not every version. Before you can assess whether this server was actually exploitable, you need to confirm the exact MongoDB version it was running at the time of the incident. MongoDB writes its own version number to its log file every time the service starts, in a log entry containing the field `buildInfo`. That log file lives at `/var/log/mongodb/mongod.log` — a path you already confirmed exists under `[root]/var/log/` in the tree structure.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
<br>
</div>

### MongoDB Version Identification

**Command:** `cat mongod.log | grep -i "buildinfo"`

**Breakdown:**

- `cat`
    - Description: Short for "concatenate" — prints the full contents of a file to the terminal.
    - Purpose: Feeds the entire contents of `mongod.log` into the next command via a pipe, rather than manually scrolling through a 512KB file.
- `|` (pipe)
    - Description: A shell operator that takes the output of the command on its left and passes it as input to the command on its right, instead of printing it to screen.
    - Purpose: Chains `cat`'s output directly into `grep` so the log can be searched in a single line.
- `grep`
    - Description: A text-search utility that reads input line by line and prints only the lines matching a given pattern.
    - Purpose: Filters thousands of log lines down to only the ones mentioning build/version information.
- `-i`
    - Description: Makes the pattern match case-insensitive.
    - Purpose: MongoDB logs the field as `buildInfo` (mixed case) — case-insensitivity avoids a miss due to capitalization.
- `"buildinfo"`
    - Description: The search keyword, quoted so the shell treats it as one literal argument.
    - Purpose: This is the specific JSON field MongoDB logs its version number under.

**Result:**

```shell
┌──(kali㉿kali)-[~/…/[root]/var/log/mongodb]
└─$ cat mongod.log | grep -i "buildinfo"
{"t":{"$date":"2025-12-29T05:11:47.713+00:00"},"s":"I",  "c":"CONTROL",  "id":23403,   "ctx":"initandlisten","msg":"Build Info","attr":{"buildInfo":{"version":"8.0.16","gitVersion":"ba70b6a13fda907977110bf46e6c8137f5de48f6","openSSLVersion":"OpenSSL 3.0.13 30 Jan 2024","modules":[],"allocator":"tcmalloc-google","environment":{"distmod":"debian12","distarch":"x86_64","target_arch":"x86_64"}}}}
{"t":{"$date":"2025-12-29T05:16:58.104+00:00"},"s":"I",  "c":"CONTROL",  "id":23403,   "ctx":"initandlisten","msg":"Build Info","attr":{"buildInfo":{"version":"8.0.16","gitVersion":"ba70b6a13fda907977110bf46e6c8137f5de48f6","openSSLVersion":"OpenSSL 3.0.13 30 Jan 2024","modules":[],"allocator":"tcmalloc-google","environment":{"distmod":"debian12","distarch":"x86_64","target_arch":"x86_64"}}}}
{"t":{"$date":"2025-12-29T06:09:34.806+00:00"},"s":"I",  "c":"CONTROL",  "id":23403,   "ctx":"initandlisten","msg":"Build Info","attr":{"buildInfo":{"version":"8.0.16","gitVersion":"ba70b6a13fda907977110bf46e6c8137f5de48f6","openSSLVersion":"OpenSSL 3.0.13 30 Jan 2024","modules":[],"allocator":"tcmalloc-google","environment":{"distmod":"debian12","distarch":"x86_64","target_arch":"x86_64"}}}}
```

MongoDB logs in structured JSON rather than plain text, so each field is worth decoding once:

|Field|Meaning|
|---|---|
|`"t":{"$date":...}`|Timestamp of the log event, in UTC|
|`"s":"I"`|Severity — `I` stands for Informational (not a warning or error)|
|`"c":"CONTROL"`|Component — which internal subsystem generated the log|
|`"id":23403`|A unique numeric ID MongoDB assigns to this specific type of log message|
|`"ctx":"initandlisten"`|Context/thread name — `initandlisten` is the thread that runs during server startup|
|`"attr":{"buildInfo":{"version":"8.0.16",...}}`|The actual data attached to the message — here, the version string|

Three matching entries means `mongod` started up three separate times during the period covered by this log, and all three report the identical version: **8.0.16**.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
<br>
</div>

### Identifying the Attacker's IP

With the CVE and the exact vulnerable version (8.0.16) confirmed, the next question in any incident response is: **who did this?** The scenario briefing already told you a MongoDB vulnerability was involved, and the CVE research described the exploitation pattern precisely — a flood of connections that get accepted and immediately disconnected, at a volume and speed no normal client would ever produce. Grepping for this manually is possible, but a community-maintained detector tool exists specifically to automate this pattern-matching and score the confidence of exploitation, so that's the more efficient path.

Research: Google search — `MongoBleed CVE-2025-14847 log indicators`

Quoted result (Google AI Overview):

> "A common indicator of exploitation is a high volume of rapid, short-lived connections (Event ID 22943 followed immediately by 22944) that completely lack client metadata, which standard MongoDB drivers typically provide."
> 
> "Rapid Pre-Authentication Failure Bursts: High volumes of pre-authentication errors or bursty, repeated connection attempts from unfamiliar or external IP addresses targeting port 27017."
> 
> "Abnormal Inbound Traffic: Sudden increases in inbound, short-lived TCP connections, particularly those attempting to initiate zlib compressed sessions against the default MongoDB port."

This tells us exactly what fingerprint to hunt for: event ID `22943` ("connection accepted") immediately followed by event ID `22944` ("connection ended"), repeated at high volume, with the connections missing the client metadata a legitimate driver would normally send.


Grepping for this pattern manually across tens of thousands of log lines is possible, but a community-maintained tool exists specifically to automate this kind of pattern-matching and score the confidence of exploitation, so that was used instead.

**GitHub repository:** — [Neo23x0/mongobleed-detector](https://github.com/Neo23x0/mongobleed-detector)

Quoted from the tool's own documentation:

> "A standalone Linux command-line tool that analyzes MongoDB data to identify likely exploitation of CVE-2025-14847 using multiple detection modules."
> 
> "Offline MongoDB Analysis Tool for CVE-2025-14847 (MongoBleed) that analyzes data to identify potential exploitation using multiple detection modules including log correlation, assert counts analysis, and FTDC spike detection."

**Relevant flags from its documented options:**

| Flag                   | Purpose                                                                                                                                                                             |
| ---------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `-p, --path <glob>`    | Points the tool at a specific log file to scan                                                                                                                                      |
| `--no-default-paths`   | Skips the tool's built-in default log locations — necessary here since we're scanning an offline, extracted copy of evidence, not a live system where logs sit in their normal spot |
| `-t, --time <minutes>` | Sets how far back (in minutes) the tool looks for events, relative to the current system clock (default: 4320 minutes / 3 days)                                                     |

**Two details needed to be handled before running this tool, based on the nature of the evidence:**

1. The extracted evidence folder is named `[root]` — a literal folder name containing square brackets, which are special "glob" pattern-matching characters in Linux (used to match a single character from a set, e.g. `[abc]`). Tools that accept a "path or glob" argument often do their own internal pattern-matching on the string they're given, separate from the shell. To avoid the detector misinterpreting `[root]` as a glob pattern instead of a literal folder name. Copy the log file into a clean scratch folder with no special characters in its path, leaving the original evidence untouched.
2. The tool's default lookback window is only 3 days, measured backward from the analysis machine's current system clock — which does not match the date the incident occurred. Setting `-t` to a large value up front guarantees the whole log is captured regardless of today's date.

**Command:**

```shell
mkdir -p ~/nedmoeca/HTB/Sherlocks/MangoBleed/analysis
cp ~/nedmoeca/HTB/Sherlocks/MangoBleed/uac-mongodbsync-linux-triage/\[root\]/var/log/mongodb/mongod.log ~/nedmoeca/HTB/Sherlocks/MangoBleed/analysis/
```

With a clean, bracket-free copy of the log in place and a wide enough time window set from the start, run the detector. 

**Command:** `bash mongobleed-detector.sh --no-default-paths -p ~/nedmoeca/HTB/Sherlocks/MangoBleed/analysis/mongod.log -t 500000`

**Breakdown:**

- `bash mongobleed-detector.sh`
    - Description: Hands the script file to the Bash interpreter as an argument, rather than executing it directly.
    - Purpose: Runs the tool without needing to separately mark the script file as executable (`chmod +x`) — passing a script to `bash` this way only requires that `bash` itself can read the file.
- `--no-default-paths`
    - Description: Skips the tool's built-in default MongoDB log locations.
    - Purpose: We're scanning an offline copy sitting at a custom path, not a live system's log directory.
- `-p <path>`
    - Description: Specifies the exact log file to analyze.
    - Purpose: Points the tool at the clean copy of `mongod.log`.
- `-t 500000`
    - Description: Sets the lookback window to 500,000 minutes (~347 days).
    - Purpose: Guarantees the tool's analysis window reaches back far enough to include the incident, regardless of the current date on the analysis machine.

**Result:**

```shell
┌──(kali㉿kali)-[~/…/HTB/Sherlocks/MangoBleed/mongobleed-detector]
└─$ bash mongobleed-detector.sh --no-default-paths -p ~/nedmoeca/HTB/Sherlocks/MangoBleed/analysis/mongod.log -t 500000
INFO: Analyzing 1 log file(s)...
INFO: Time window: 2025-07-26T06:54:00Z to now

╔══════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
║                              MongoBleed (CVE-2025-14847) Detection Results                                       ║
╚══════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝

Analysis Parameters:
  Time Window:        500000 minutes
  Connection Thresh:  100
  Burst Rate Thresh:  400/min
  Metadata Rate:      0.10

Risk     SourceIP                                  ConnCount  MetaCount  DiscCount    MetaRate%    BurstRate/m FirstSeen (UTC)        LastSeen (UTC)        
-------- ---------------------------------------- ---------- ---------- ---------- ------------ -------------- ---------------------- ----------------------
HIGH     65.0.76.43                                    37630          0      37630        0.00%       30104.00 2025-12-29T05:25:52Z   2025-12-29T05:27:07Z  

═══════════════════════════════════════════════════════════════════════════════════════════════════════════════════
Summary:
  HIGH:   1 source(s) - Likely exploitation detected

⚠ IMPORTANT: If exploitation is confirmed, patching alone is insufficient.
  - Rotate all credentials that may have been exposed
  - Review accessed data for sensitive information disclosure
  - Check for lateral movement from affected systems
  - Preserve logs for forensic analysis
```

Breaking down what each column in the results table means:

| Column                     | Meaning                                                                                                                                                                                                                                    |
| -------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Risk                       | The tool's overall confidence that this source IP represents real exploitation, not a false positive                                                                                                                                       |
| SourceIP                   | The remote IP address generating the flagged traffic                                                                                                                                                                                       |
| ConnCount                  | Total "connection accepted" events logged from this IP                                                                                                                                                                                     |
| MetaCount                  | Of those connections, how many included normal client metadata (application name, driver version, OS) — legitimate MongoDB clients almost always send this during a proper handshake                                                       |
| DiscCount                  | Total "connection ended" (disconnect) events from this IP                                                                                                                                                                                  |
| MetaRate%                  | `MetaCount ÷ ConnCount` — the percentage of connections that behaved like a normal client. A malformed/exploit packet skips the parts of the handshake that carry this metadata, so an exploit tool would show a near-zero percentage here |
| BurstRate/m                | The peak rate of connections-per-minute observed — used to detect sudden floods                                                                                                                                                            |
| FirstSeen / LastSeen (UTC) | Timestamps bounding the first and last event attributed to this source                                                                                                                                                                     |

**What this tells us:** `65.0.76.43` opened 37,630 connections in roughly 75 seconds (`05:25:52` to `05:27:07`), with a peak rate over 30,000 connections/minute, and **0.00%** of those connections carried normal client metadata. That combination — massive volume, extreme speed, and a complete absence of the handshake data a real client would send — matches exactly the log indicators identified in the research. This identifies `**65.0.76.43**` as the attacker's IP address, with exploitation activity spanning `2025-12-29T05:25:52Z` to `2025-12-29T05:27:07Z` UTC.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## Task 1

### What is the CVE ID designated to the MongoDB vulnerability explained in the scenario?

**==CVE-2025-14847==**
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## Task 2

### What is the version of MongoDB installed on the server that the CVE exploited?

**==8.0.16==**
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## Task 3

### Analyze the MongoDB logs to identify the attacker's remote IP address used to exploit the CVE.

**==65.0.76.43==**
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## Task 4

### Based on the MongoDB logs, determine the exact date and time the attacker’s exploitation activity began (the earliest confirmed malicious event)

**==2025-12-29 05:25:52==**
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## Task 5

### Using the MongoDB logs, calculate the total number of malicious connections initiated by the attacker.

**==75260==**

**Command:**

```shell
┌──(kali㉿kali)-[~/…/[root]/var/log/mongodb]
└─$ grep -i "65.0.76.43" mongod.log | wc -l
75260
```
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## Task 6

### The attacker gained remote access after a series of brute‑force attempts. The attack likely exposed sensitive information, which enabled them to gain remote access. Based on the logs, when did the attacker successfully gain interactive hands-on remote access?

**==2025-12-29 05:40:03==**
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
<br>
</div>

MongoBleed leaks uninitialized heap memory — and heap memory on a database server can easily contain recently-processed data like authentication credentials, session tokens, or connection strings. Given that, the logical next question is whether the attacker took whatever they scraped from memory and used it to log into the server directly, rather than just reading data through the database protocol.

SSH (Secure Shell) is the standard way to get an interactive command-line session on a remote Linux server, and every login attempt against it — successful or failed — gets recorded by Linux's authentication system (PAM, the Pluggable Authentication Modules framework) into `/var/log/auth.log`. You already confirmed this file exists under `[root]/var/log/` in the tree structure. Since we now have the attacker's IP address (`65.0.76.43`) pinned down from the MongoDB logs, the next step is to check whether that same IP shows up in the authentication log.

Navigate to `[root]/var/log/` and search `auth.log` for the attacker's IP address. Run:

**Command:** `grep -i "65.0.76.43" auth.log`

**Result:**

```shell
┌──(kali㉿kali)-[~/…/uac-mongodbsync-linux-triage/[root]/var/log]
└─$ grep -i "65.0.76.43" auth.log                     
2025-12-29T05:39:18.864074+00:00 ip-172-31-38-170 sshd[39814]: Received disconnect from 65.0.76.43 port 54962:11: Bye Bye [preauth]
2025-12-29T05:39:18.866641+00:00 ip-172-31-38-170 sshd[39814]: Disconnected from authenticating user mongoadmin 65.0.76.43 port 54962 [preauth]
2025-12-29T05:39:19.113009+00:00 ip-172-31-38-170 sshd[2152]: drop connection #10 from [65.0.76.43]:55068 on [172.31.38.170]:22 past MaxStartups
2025-12-29T05:39:19.381375+00:00 ip-172-31-38-170 sshd[39844]: pam_unix(sshd:auth): authentication failure; logname= uid=0 euid=0 tty=ssh ruser= rhost=65.0.76.43  user=mongoadmin
2025-12-29T05:39:19.478221+00:00 ip-172-31-38-170 sshd[39845]: pam_unix(sshd:auth): authentication failure; logname= uid=0 euid=0 tty=ssh ruser= rhost=65.0.76.43  user=mongoadmin
2025-12-29T05:39:19.545976+00:00 ip-172-31-38-170 sshd[39846]: pam_unix(sshd:auth): authentication failure; logname= uid=0 euid=0 tty=ssh ruser= rhost=65.0.76.43  user=mongoadmin
2025-12-29T05:39:19.554759+00:00 ip-172-31-38-170 sshd[39847]: pam_unix(sshd:auth): authentication failure; logname= uid=0 euid=0 tty=ssh ruser= rhost=65.0.76.43  user=mongoadmin
2025-12-29T05:39:19.554993+00:00 ip-172-31-38-170 sshd[39848]: pam_unix(sshd:auth): authentication failure; logname= uid=0 euid=0 tty=ssh ruser= rhost=65.0.76.43  user=mongoadmin
2025-12-29T05:39:19.555198+00:00 ip-172-31-38-170 sshd[39851]: pam_unix(sshd:auth): authentication failure; logname= uid=0 euid=0 tty=ssh ruser= rhost=65.0.76.43  user=mongoadmin
2025-12-29T05:39:19.558909+00:00 ip-172-31-38-170 sshd[39854]: pam_unix(sshd:auth): authentication failure; logname= uid=0 euid=0 tty=ssh ruser= rhost=65.0.76.43  user=mongoadmin
2025-12-29T05:39:19.564686+00:00 ip-172-31-38-170 sshd[39853]: pam_unix(sshd:auth): authentication failure; logname= uid=0 euid=0 tty=ssh ruser= rhost=65.0.76.43  user=mongoadmin
2025-12-29T05:39:19.564934+00:00 ip-172-31-38-170 sshd[39855]: pam_unix(sshd:auth): authentication failure; logname= uid=0 euid=0 tty=ssh ruser= rhost=65.0.76.43  user=mongoadmin
2025-12-29T05:39:19.565129+00:00 ip-172-31-38-170 sshd[39850]: pam_unix(sshd:auth): authentication failure; logname= uid=0 euid=0 tty=ssh ruser= rhost=65.0.76.43  user=mongoadmin
2025-12-29T05:39:19.566958+00:00 ip-172-31-38-170 sshd[39856]: pam_unix(sshd:auth): authentication failure; logname= uid=0 euid=0 tty=ssh ruser= rhost=65.0.76.43  user=mongoadmin
2025-12-29T05:39:19.567215+00:00 ip-172-31-38-170 sshd[39852]: pam_unix(sshd:auth): authentication failure; logname= uid=0 euid=0 tty=ssh ruser= rhost=65.0.76.43  user=mongoadmin
2025-12-29T05:39:19.567871+00:00 ip-172-31-38-170 sshd[39849]: pam_unix(sshd:auth): authentication failure; logname= uid=0 euid=0 tty=ssh ruser= rhost=65.0.76.43  user=mongoadmin
2025-12-29T05:39:19.572079+00:00 ip-172-31-38-170 sshd[39857]: pam_unix(sshd:auth): authentication failure; logname= uid=0 euid=0 tty=ssh ruser= rhost=65.0.76.43  user=mongoadmin
2025-12-29T05:39:21.697983+00:00 ip-172-31-38-170 sshd[39816]: error: PAM: Authentication failure for mongoadmin from 65.0.76.43
2025-12-29T05:39:21.752018+00:00 ip-172-31-38-170 sshd[39858]: pam_unix(sshd:auth): authentication failure; logname= uid=0 euid=0 tty=ssh ruser= rhost=65.0.76.43  user=mongoadmin
2025-12-29T05:39:21.797661+00:00 ip-172-31-38-170 sshd[39818]: error: PAM: Authentication failure for mongoadmin from 65.0.76.43
2025-12-29T05:39:21.851009+00:00 ip-172-31-38-170 sshd[39859]: pam_unix(sshd:auth): authentication failure; logname= uid=0 euid=0 tty=ssh ruser= rhost=65.0.76.43  user=mongoadmin
2025-12-29T05:39:21.856191+00:00 ip-172-31-38-170 sshd[39819]: error: PAM: Authentication failure for mongoadmin from 65.0.76.43
2025-12-29T05:39:21.870123+00:00 ip-172-31-38-170 sshd[39820]: error: PAM: Authentication failure for mongoadmin from 65.0.76.43
2025-12-29T05:39:21.871087+00:00 ip-172-31-38-170 sshd[39824]: error: PAM: Authentication failure for mongoadmin from 65.0.76.43
2025-12-29T05:39:21.871332+00:00 ip-172-31-38-170 sshd[39821]: error: PAM: Authentication failure for mongoadmin from 65.0.76.43
2025-12-29T05:39:21.878545+00:00 ip-172-31-38-170 sshd[39823]: error: PAM: Authentication failure for mongoadmin from 65.0.76.43
2025-12-29T05:39:21.879041+00:00 ip-172-31-38-170 sshd[39825]: error: PAM: Authentication failure for mongoadmin from 65.0.76.43
2025-12-29T05:39:21.880199+00:00 ip-172-31-38-170 sshd[39827]: error: PAM: Authentication failure for mongoadmin from 65.0.76.43
2025-12-29T05:39:21.880996+00:00 ip-172-31-38-170 sshd[39817]: error: PAM: Authentication failure for mongoadmin from 65.0.76.43
2025-12-29T05:39:21.883517+00:00 ip-172-31-38-170 sshd[39830]: error: PAM: Authentication failure for mongoadmin from 65.0.76.43
2025-12-29T05:39:21.883794+00:00 ip-172-31-38-170 sshd[39826]: error: PAM: Authentication failure for mongoadmin from 65.0.76.43
2025-12-29T05:39:21.884016+00:00 ip-172-31-38-170 sshd[39822]: error: PAM: Authentication failure for mongoadmin from 65.0.76.43
2025-12-29T05:39:21.890635+00:00 ip-172-31-38-170 sshd[39829]: error: PAM: Authentication failure for mongoadmin from 65.0.76.43
2025-12-29T05:39:22.030041+00:00 ip-172-31-38-170 sshd[39860]: pam_unix(sshd:auth): authentication failure; logname= uid=0 euid=0 tty=ssh ruser= rhost=65.0.76.43  user=mongoadmin
2025-12-29T05:39:22.146020+00:00 ip-172-31-38-170 sshd[39861]: pam_unix(sshd:auth): authentication failure; logname= uid=0 euid=0 tty=ssh ruser= rhost=65.0.76.43  user=mongoadmin
2025-12-29T05:39:22.158046+00:00 ip-172-31-38-170 sshd[39871]: pam_unix(sshd:auth): authentication failure; logname= uid=0 euid=0 tty=ssh ruser= rhost=65.0.76.43  user=mongoadmin
2025-12-29T05:39:22.161929+00:00 ip-172-31-38-170 sshd[39862]: pam_unix(sshd:auth): authentication failure; logname= uid=0 euid=0 tty=ssh ruser= rhost=65.0.76.43  user=mongoadmin
2025-12-29T05:39:22.162153+00:00 ip-172-31-38-170 sshd[39869]: pam_unix(sshd:auth): authentication failure; logname= uid=0 euid=0 tty=ssh ruser= rhost=65.0.76.43  user=mongoadmin
2025-12-29T05:39:22.162355+00:00 ip-172-31-38-170 sshd[39863]: pam_unix(sshd:auth): authentication failure; logname= uid=0 euid=0 tty=ssh ruser= rhost=65.0.76.43  user=mongoadmin
2025-12-29T05:39:22.166407+00:00 ip-172-31-38-170 sshd[39865]: pam_unix(sshd:auth): authentication failure; logname= uid=0 euid=0 tty=ssh ruser= rhost=65.0.76.43  user=mongoadmin
2025-12-29T05:39:22.166627+00:00 ip-172-31-38-170 sshd[39867]: pam_unix(sshd:auth): authentication failure; logname= uid=0 euid=0 tty=ssh ruser= rhost=65.0.76.43  user=mongoadmin
2025-12-29T05:39:22.166873+00:00 ip-172-31-38-170 sshd[39866]: pam_unix(sshd:auth): authentication failure; logname= uid=0 euid=0 tty=ssh ruser= rhost=65.0.76.43  user=mongoadmin
2025-12-29T05:39:22.167075+00:00 ip-172-31-38-170 sshd[39864]: pam_unix(sshd:auth): authentication failure; logname= uid=0 euid=0 tty=ssh ruser= rhost=65.0.76.43  user=mongoadmin
2025-12-29T05:39:22.167285+00:00 ip-172-31-38-170 sshd[39868]: pam_unix(sshd:auth): authentication failure; logname= uid=0 euid=0 tty=ssh ruser= rhost=65.0.76.43  user=mongoadmin
2025-12-29T05:39:22.173507+00:00 ip-172-31-38-170 sshd[39870]: pam_unix(sshd:auth): authentication failure; logname= uid=0 euid=0 tty=ssh ruser= rhost=65.0.76.43  user=mongoadmin
2025-12-29T05:39:23.676920+00:00 ip-172-31-38-170 sshd[39816]: error: PAM: Authentication failure for mongoadmin from 65.0.76.43
2025-12-29T05:39:23.731304+00:00 ip-172-31-38-170 sshd[39872]: pam_unix(sshd:auth): authentication failure; logname= uid=0 euid=0 tty=ssh ruser= rhost=65.0.76.43  user=mongoadmin
2025-12-29T05:39:23.776120+00:00 ip-172-31-38-170 sshd[39818]: error: PAM: Authentication failure for mongoadmin from 65.0.76.43
2025-12-29T05:39:23.829259+00:00 ip-172-31-38-170 sshd[39873]: pam_unix(sshd:auth): authentication failure; logname= uid=0 euid=0 tty=ssh ruser= rhost=65.0.76.43  user=mongoadmin
2025-12-29T05:39:23.951868+00:00 ip-172-31-38-170 sshd[39819]: error: PAM: Authentication failure for mongoadmin from 65.0.76.43
2025-12-29T05:39:24.005606+00:00 ip-172-31-38-170 sshd[39874]: pam_unix(sshd:auth): authentication failure; logname= uid=0 euid=0 tty=ssh ruser= rhost=65.0.76.43  user=mongoadmin
2025-12-29T05:39:24.067192+00:00 ip-172-31-38-170 sshd[39824]: error: PAM: Authentication failure for mongoadmin from 65.0.76.43
2025-12-29T05:39:24.081971+00:00 ip-172-31-38-170 sshd[39822]: error: PAM: Authentication failure for mongoadmin from 65.0.76.43
2025-12-29T05:39:24.085379+00:00 ip-172-31-38-170 sshd[39821]: error: PAM: Authentication failure for mongoadmin from 65.0.76.43
2025-12-29T05:39:24.086370+00:00 ip-172-31-38-170 sshd[39820]: error: PAM: Authentication failure for mongoadmin from 65.0.76.43
2025-12-29T05:39:24.088632+00:00 ip-172-31-38-170 sshd[39817]: error: PAM: Authentication failure for mongoadmin from 65.0.76.43
2025-12-29T05:39:24.088863+00:00 ip-172-31-38-170 sshd[39825]: error: PAM: Authentication failure for mongoadmin from 65.0.76.43
2025-12-29T05:39:24.091298+00:00 ip-172-31-38-170 sshd[39829]: error: PAM: Authentication failure for mongoadmin from 65.0.76.43
2025-12-29T05:39:24.092043+00:00 ip-172-31-38-170 sshd[39826]: error: PAM: Authentication failure for mongoadmin from 65.0.76.43
2025-12-29T05:39:24.092755+00:00 ip-172-31-38-170 sshd[39823]: error: PAM: Authentication failure for mongoadmin from 65.0.76.43
2025-12-29T05:39:24.097350+00:00 ip-172-31-38-170 sshd[39830]: error: PAM: Authentication failure for mongoadmin from 65.0.76.43
2025-12-29T05:39:24.099331+00:00 ip-172-31-38-170 sshd[39827]: error: PAM: Authentication failure for mongoadmin from 65.0.76.43
2025-12-29T05:39:24.108758+00:00 ip-172-31-38-170 sshd[39830]: Connection closed by authenticating user mongoadmin 65.0.76.43 port 55126 [preauth]
2025-12-29T05:39:24.108846+00:00 ip-172-31-38-170 sshd[39827]: Connection closed by authenticating user mongoadmin 65.0.76.43 port 55096 [preauth]
2025-12-29T05:39:24.108889+00:00 ip-172-31-38-170 sshd[39826]: Connection closed by authenticating user mongoadmin 65.0.76.43 port 55090 [preauth]
2025-12-29T05:39:24.210906+00:00 ip-172-31-38-170 sshd[39875]: pam_unix(sshd:auth): authentication failure; logname= uid=0 euid=0 tty=ssh ruser= rhost=65.0.76.43  user=mongoadmin
2025-12-29T05:39:24.269457+00:00 ip-172-31-38-170 sshd[39878]: pam_unix(sshd:auth): authentication failure; logname= uid=0 euid=0 tty=ssh ruser= rhost=65.0.76.43  user=mongoadmin
2025-12-29T05:39:24.273306+00:00 ip-172-31-38-170 sshd[39876]: pam_unix(sshd:auth): authentication failure; logname= uid=0 euid=0 tty=ssh ruser= rhost=65.0.76.43  user=mongoadmin
2025-12-29T05:39:24.276756+00:00 ip-172-31-38-170 sshd[39825]: Accepted keyboard-interactive/pam for mongoadmin from 65.0.76.43 port 55056 ssh2
2025-12-29T05:39:24.279681+00:00 ip-172-31-38-170 sshd[39882]: pam_unix(sshd:auth): authentication failure; logname= uid=0 euid=0 tty=ssh ruser= rhost=65.0.76.43  user=mongoadmin
2025-12-29T05:39:24.286885+00:00 ip-172-31-38-170 sshd[39879]: pam_unix(sshd:auth): authentication failure; logname= uid=0 euid=0 tty=ssh ruser= rhost=65.0.76.43  user=mongoadmin
2025-12-29T05:39:24.289290+00:00 ip-172-31-38-170 sshd[39881]: pam_unix(sshd:auth): authentication failure; logname= uid=0 euid=0 tty=ssh ruser= rhost=65.0.76.43  user=mongoadmin
2025-12-29T05:39:24.289574+00:00 ip-172-31-38-170 sshd[39880]: pam_unix(sshd:auth): authentication failure; logname= uid=0 euid=0 tty=ssh ruser= rhost=65.0.76.43  user=mongoadmin
2025-12-29T05:39:25.596404+00:00 ip-172-31-38-170 sshd[39816]: error: PAM: Authentication failure for mongoadmin from 65.0.76.43
2025-12-29T05:39:25.598101+00:00 ip-172-31-38-170 sshd[39816]: Connection closed by authenticating user mongoadmin 65.0.76.43 port 54976 [preauth]
2025-12-29T05:39:25.694370+00:00 ip-172-31-38-170 sshd[39818]: error: PAM: Authentication failure for mongoadmin from 65.0.76.43
2025-12-29T05:39:25.695961+00:00 ip-172-31-38-170 sshd[39818]: Connection closed by authenticating user mongoadmin 65.0.76.43 port 54988 [preauth]
2025-12-29T05:39:25.870560+00:00 ip-172-31-38-170 sshd[39819]: error: PAM: Authentication failure for mongoadmin from 65.0.76.43
2025-12-29T05:39:25.872303+00:00 ip-172-31-38-170 sshd[39819]: Connection closed by authenticating user mongoadmin 65.0.76.43 port 55002 [preauth]
2025-12-29T05:39:25.880047+00:00 ip-172-31-38-170 sshd[39824]: error: PAM: Authentication failure for mongoadmin from 65.0.76.43
2025-12-29T05:39:25.881891+00:00 ip-172-31-38-170 sshd[39824]: Connection closed by authenticating user mongoadmin 65.0.76.43 port 55040 [preauth]
2025-12-29T05:39:25.938496+00:00 ip-172-31-38-170 sshd[39829]: error: PAM: Authentication failure for mongoadmin from 65.0.76.43
2025-12-29T05:39:25.940446+00:00 ip-172-31-38-170 sshd[39829]: Connection closed by authenticating user mongoadmin 65.0.76.43 port 55112 [preauth]
2025-12-29T05:39:25.941340+00:00 ip-172-31-38-170 sshd[39822]: error: PAM: Authentication failure for mongoadmin from 65.0.76.43
2025-12-29T05:39:25.943193+00:00 ip-172-31-38-170 sshd[39822]: Connection closed by authenticating user mongoadmin 65.0.76.43 port 55018 [preauth]
2025-12-29T05:39:25.949031+00:00 ip-172-31-38-170 sshd[39823]: error: PAM: Authentication failure for mongoadmin from 65.0.76.43
2025-12-29T05:39:25.950631+00:00 ip-172-31-38-170 sshd[39823]: Connection closed by authenticating user mongoadmin 65.0.76.43 port 55034 [preauth]
2025-12-29T05:39:25.955047+00:00 ip-172-31-38-170 sshd[39817]: error: PAM: Authentication failure for mongoadmin from 65.0.76.43
2025-12-29T05:39:25.958028+00:00 ip-172-31-38-170 sshd[39820]: error: PAM: Authentication failure for mongoadmin from 65.0.76.43
2025-12-29T05:39:25.959241+00:00 ip-172-31-38-170 sshd[39821]: error: PAM: Authentication failure for mongoadmin from 65.0.76.43
2025-12-29T05:39:25.959329+00:00 ip-172-31-38-170 sshd[39817]: Connection closed by authenticating user mongoadmin 65.0.76.43 port 54978 [preauth]
2025-12-29T05:39:25.959975+00:00 ip-172-31-38-170 sshd[39820]: Connection closed by authenticating user mongoadmin 65.0.76.43 port 55006 [preauth]
2025-12-29T05:39:25.960736+00:00 ip-172-31-38-170 sshd[39821]: Connection closed by authenticating user mongoadmin 65.0.76.43 port 55014 [preauth]
2025-12-29T05:40:03.475659+00:00 ip-172-31-38-170 sshd[39962]: Accepted keyboard-interactive/pam for mongoadmin from 65.0.76.43 port 46062 ssh2
2025-12-29T05:48:28.249844+00:00 ip-172-31-38-170 sshd[40027]: Received disconnect from 65.0.76.43 port 46062:11: disconnected by user
2025-12-29T05:48:28.250045+00:00 ip-172-31-38-170 sshd[40027]: Disconnected from user mongoadmin 65.0.76.43 port 46062
```

Two things stand out here. First, between roughly `05:39:19` and `05:39:26` — a window of about **7 seconds** — there are well over a hundred `authentication failure` events for the same user, `mongoadmin`, all from `65.0.76.43`, each one running under a _different_ SSH process ID (`sshd[39844]`, `sshd[39845]`, `sshd[39846]`, and so on). 

A human typing a password wrong repeatedly would generate failures one at a time, sequentially, under a single connection. Dozens of simultaneous connection attempts, each with its own process ID, all within a few seconds, is the signature of an automated brute-force tool — a script that opens many parallel SSH connections at once and rapidly tries different passwords across all of them.

Second, buried inside the auth failures are two lines that don't say `authentication failure` — they say `Accepted keyboard-interactive/pam`, meaning a correct password was eventually supplied and SSH let the connection through:

- `sshd[39825]` — accepted at `05:39:24.276756`, right in the middle of the brute-force burst.
- `sshd[39962]` — accepted at `05:40:03.475659`, about 39 seconds after the burst died down.

The first accepted session (`39825`) doesn't show a matching disconnect line in this IP-filtered view — which makes sense, since a session's closing message doesn't always repeat the remote IP address, so a plain IP search can miss it. To see that session's complete lifecycle in isolation from all the surrounding noise, the next step is to filter `auth.log` by its specific process ID instead of the IP.
<div align="center">
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
</div>

**Command:** `grep "39825" auth.log`

**Result:**

```shell
┌──(kali㉿kali)-[~/…/uac-mongodbsync-linux-triage/[root]/var/log]
└─$ grep "39825" auth.log                             
2025-12-29T05:39:21.879041+00:00 ip-172-31-38-170 sshd[39825]: error: PAM: Authentication failure for mongoadmin from 65.0.76.43
2025-12-29T05:39:24.088863+00:00 ip-172-31-38-170 sshd[39825]: error: PAM: Authentication failure for mongoadmin from 65.0.76.43
2025-12-29T05:39:24.276756+00:00 ip-172-31-38-170 sshd[39825]: Accepted keyboard-interactive/pam for mongoadmin from 65.0.76.43 port 55056 ssh2
2025-12-29T05:39:24.280444+00:00 ip-172-31-38-170 sshd[39825]: pam_unix(sshd:session): session opened for user mongoadmin(uid=1001) by mongoadmin(uid=0)
2025-12-29T05:39:24.861336+00:00 ip-172-31-38-170 sshd[39825]: pam_unix(sshd:session): session closed for user mongoadmin
```

This gives us the complete lifecycle of session `39825`: two failed password guesses, then a correct one accepted at `05:39:24.276756`, a session opened four milliseconds later at `.280444`, and — critically — that same session closed at `05:39:24.861336`. From accepted to closed is under **six-tenths of a second**. No human logs in, does something, and logs out again in half a second — that's consistent with an automated tool confirming a cracked credential works and then dropping the connection, not someone sitting at a keyboard actually using the access.

That rules out `39825` as the hands-on session. The remaining candidate is `39962`, accepted at `05:40:03`. The same technique — filtering by its PID — will show whether that session behaves differently.
<div align="center">
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
</div>

**Command:** `grep "39962" auth.log`

**Result:**

```shell
┌──(kali㉿kali)-[~/…/uac-mongodbsync-linux-triage/[root]/var/log]
└─$ grep "39962" auth.log 
2025-12-29T05:40:03.475659+00:00 ip-172-31-38-170 sshd[39962]: Accepted keyboard-interactive/pam for mongoadmin from 65.0.76.43 port 46062 ssh2
2025-12-29T05:40:03.477802+00:00 ip-172-31-38-170 sshd[39962]: pam_unix(sshd:session): session opened for user mongoadmin(uid=1001) by mongoadmin(uid=0)
2025-12-29T05:48:28.250833+00:00 ip-172-31-38-170 sshd[39962]: pam_unix(sshd:session): session closed for user mongoadmin
```

This is a completely different pattern from `39825`. Here, the session was accepted at `05:40:03.475659`, opened two milliseconds later, and stayed open until it finally closed at `05:48:28.250833` — a gap of roughly **8 minutes and 25 seconds**. A session held open for that long is consistent with a real, hands-on interactive use of the terminal: someone typing commands, looking around the system, waiting between actions — not a script that authenticates and immediately exits.

Combined with what was ruled out in `39825` (accepted-and-closed in under a second, indicating automated credential validation rather than actual use), this identifies `39962` as the session where the attacker actually sat down and used their access.

The attacker gained interactive hands-on remote access at **2025-12-29 05:40:03 UTC** (the moment session `39962` was accepted and opened), and remained connected until `05:48:28 UTC`, roughly 8 minutes and 25 seconds later.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## Task 7

### Identify the exact command line the attacker used to execute an in‑memory script as part of their privilege‑escalation attempt.

**==Answer==**
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
<br>
</div>


<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## Task 8

### The attacker was interested in a specific directory and also opened a Python web server, likely for exfiltration purposes. Which directory was the target?

**==Answer==**
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

