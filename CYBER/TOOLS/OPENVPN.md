## What is OpenVPN?

OpenVPN is an open-source Virtual Private Network (VPN) solution that uses custom security protocols to create secure point-to-point or site-to-site connections.

It allows:
- Secure remote access to networks
- Encrypted tunnels for traffic
- Safe connections on public Wi-Fi
- ==Connecting virtual labs (e.g., TryHackMe or Hack The Box)==

## Key Components

- **Client Config (`.ovpn`) file**: Contains settings, keys, and server info.
- **Server**: Remote machine you're connecting to.
- **Client**: Your local machine.

## Common Files in OpenVPN Setup

- `.ovpn` file: Config file to connect to VPN
- `ca.crt`: Certificate authority file (validates server cert)
- `client.crt`: Your client certificate
- `client.key`: Your private key
- `ta.key`: TLS auth key (for additional security, optional)

## How to Connect Using OpenVPN (Linux)

**Install OpenVPN**

```bash
sudo apt update
sudo apt install openvpn
```

Navigate to the `.ovpn` file

```bash
cd ~/Downloads
```

Connect

```bash
sudo openvpn <filename>.ovpn
```

Verify connection
- Check your IP
- Use `ifconfig` or `ip a` to view tunnel interface (usually `tun0`)


---

## References

