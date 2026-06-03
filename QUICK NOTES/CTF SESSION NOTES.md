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
