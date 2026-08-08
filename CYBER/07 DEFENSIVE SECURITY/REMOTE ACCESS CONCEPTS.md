Remote Access is accessing a computer over a network.

Some of the most common remote access technologies include but aren't limited to:
- Virtual Private Networks (VPN)
- Secure Shell (SSH)
- File Transfer Protocol (FTP)
- Virtual Network Computing (VNC)
- Windows Remote Management (or PowerShell Remoting) (WinRM)
- Remote Desktop Protocol (RDP)


---

## SSH
[Secure Shell (SSH)](https://en.wikipedia.org/wiki/SSH_\(Secure_Shell\)) is a cryptographic network protocol that runs on port `22` by default and is used to securely connect to remote systems over a network.
- It enables **secure communication** between a client and a server.
- Mostly used for **remote login** and **command execution** on servers.
- Encrypts the session to prevent eavesdropping, connection hijacking, etc.

| Term               | Description                                  |
| ------------------ | -------------------------------------------- |
| **Client**         | The system that initiates the SSH connection |
| **Server**         | The system that accepts SSH connections      |
| **Port 22**        | Default port SSH listens to                  |
| **Username**       | The user account on the remote machine       |
| **Authentication** | Can be done via **password** or **SSH keys** |
### How SSH Works
1. The client sends a connection request to the server.
2. The server responds with its public key.
3. The client and server negotiate encryption (e.g., using RSA, Ed25519).
4. The client authenticates (via password or key).
5. A secure channel is established.

### Basic SSH Command

```bash
ssh username@remote_host
```

Example:

```bash
ssh terrence@192.168.1.10
```

Or with a custom port:

```bash
ssh -p 2222 terrence@192.168.1.10
```


### Using SSH Keys (Instead of Passwords)

#### 1. Generate SSH Key Pair

```bash
ssh-keygen
```

- Saves public and private keys in `~/.ssh/id_rsa` (or similar)
- **Public key**: `id_rsa.pub` (can be shared)
- **Private key**: `id_rsa` (keep secure!)

#### 2. Copy Public Key to Remote Server

```bash
ssh-copy-id username@remote_host
```

Now, you can log in **without typing your password**.

### Common SSH Options

|Option|Purpose|
|---|---|
|`-p`|Specify port|
|`-i`|Use specific private key|
|`-L`|Local port forwarding|
|`-N`|No remote command, just forwarding|
|`-T`|Disable pseudo-terminal allocation|


---

## References
https://academy.hackthebox.com/module/77/section/847
https://academy.hackthebox.com/module/77/section/847

