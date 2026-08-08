**Nmap** (short for **Network Mapper**) is an open-source tool used for **network discovery** and **security auditing**. It’s widely used by system administrators, network engineers, and cybersecurity professionals to:

- **Scan networks** to see which devices are connected.
- **Detect open ports** on a system.
- **Identify services** running on those ports (e.g., web servers, SSH).
- **Guess the operating system** of a host (OS fingerprinting).
- **Audit network security** by detecting vulnerabilities.


## How It Works

Nmap sends specially crafted packets to target hosts and analyzes the responses. Based on these, it determines:
- Host availability (is the host online?).
- What ports are open.
- What services/versions are running.
- Operating system and hardware characteristics.


---

## Common Command Examples

**Scan a single IP**:
```
nmap 192.168.1.1
```

**Scan a range of IPs**:
```
nmap 192.168.1.1-50
```

**Scan a subnet**:
```
nmap 192.168.1.0/24
```

**Service version detection**:
```
nmap -sV 192.168.1.1
```

**OS detection**:
```
nmap -O 192.168.1.1
```

**Aggressive scan (includes version detection, OS detection, script scanning, traceroute)**:
```
nmap -A 192.168.1.1
```


---

### Advanced Features

- **NSE (Nmap Scripting Engine)**: Automates tasks like brute-force attacks, vulnerability detection, or backdoor detection.
- **Zenmap**: GUI version of Nmap for easier use.


---

## References

