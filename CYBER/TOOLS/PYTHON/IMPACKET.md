
**Impacket** is a popular open-source collection of Python classes focused on working with network protocols. It's widely used by cybersecurity professionals for **penetration testing**, **network reconnaissance**, **credential dumping**, and **lateral movement** in Windows environments.

## Key Features of Impacket:

1. **Low-level protocol interaction:**
    - Provides access to raw packets and lets you craft custom network protocol messages.
    - Supports many protocols: **SMB, NTLM, DNS, RDP, LDAP, Kerberos, MSRPC**, and more.
    
2. **High-level scripting:**
    - Comes with a set of **ready-to-use tools** for common offensive security tasks.
        
3. **Python-based:**
    - Written in Python, making it easily modifiable and scriptable.


### Common Impacket Tools:

Some useful tools included in Impacket (located in the `examples/` directory):

| Tool             | Description                                                                 |
| ---------------- | --------------------------------------------------------------------------- |
| `smbclient.py`   | SMB command-line client (like `smbclient` in Linux).                        |
| `secretsdump.py` | Dumps NTLM hashes and secrets from remote Windows systems.                  |
| `wmiexec.py`     | Executes commands on a remote host using WMI.                               |
| `psexec.py`      | Runs commands remotely using the SMB protocol (like Sysinternals PsExec).   |
| `mimikatz.py`    | Wrapper for invoking Mimikatz remotely.                                     |
| `ticketer.py`    | Creates Kerberos tickets for impersonation (Golden/Silver tickets).         |
| `ntlmrelayx.py`  | Relays NTLM authentication to hijack sessions and authenticate to services. |

### Use Cases:

- **Red teaming / offensive security:**
    - Credential theft, lateral movement, remote code execution.
- **Blue teaming / defense:**
    - Emulating attacker behavior for detection testing.
- **Protocol testing:**
    - Debug or reverse engineer Windows protocols.


---

## 1. Installing Impacket

### Requirements:

- **Python 3.7+**

### Installation:

```bash
# Clone the repository
git clone https://github.com/fortra/impacket.git
cd impacket

# Install dependencies and setup
pip install -r requirements.txt
python3 setup.py install
```


## 2. Basic Tools and Examples

Impacket comes with many tools located in the `examples/` directory.

### `smbclient.py` – SMB File Access

```bash
python3 examples/smbclient.py user:pass@target_ip
```

Like a Windows share browser. Use it to list and interact with SMB shares.

### `secretsdump.py` – Dump Password Hashes

```bash
python3 examples/secretsdump.py user:pass@target_ip
```

Extracts:
- NTLM hashes
- Cached credentials
- LSA secrets

### `psexec.py` – Remote Code Execution via SMB

```bash
python3 examples/psexec.py user:pass@target_ip
```

Launches a shell on the remote system, mimicking Sysinternals PsExec.

### `wmiexec.py` – Command Execution via WMI

```bash
python3 examples/wmiexec.py user:pass@target_ip
```

Executes commands without writing to disk (fileless execution).

### `ntlmrelayx.py` – NTLM Relay Attacks

Used in **man-in-the-middle attacks** when capturing and relaying NTLM authentication.

```bash
python3 examples/ntlmrelayx.py -tf targets.txt
```


## 3. Authentication Formats

Impacket accepts many formats for credentials:

|Format|Example|
|---|---|
|Username & Password|`domain/user:password@target`|
|NTLM Hash|`domain/user@target -hashes :<NTLM_HASH>`|
|Kerberos Ticket|`-k -no-pass` (uses TGT from system)|


## 4. Use Case Scenarios

|Goal|Tool|
|---|---|
|Browse SMB shares|`smbclient.py`|
|Dump user credentials|`secretsdump.py`|
|Remote command exec|`psexec.py` / `wmiexec.py`|
|Relay NTLM auth|`ntlmrelayx.py`|
|Create forged tickets|`ticketer.py`|


## 5. Best Practices

- Use **VPN or lab environments** for testing.
- Pair with tools like **CrackMapExec**, **Responder**, and **BloodHound**.
- Consider setting up a **Windows test lab** with AD for hands-on learning.


---

## References

https://tryhackme.com/room/attacktivedirectory