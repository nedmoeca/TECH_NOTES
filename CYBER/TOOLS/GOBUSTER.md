## What is Gobuster?

Gobuster is a command‑line tool written in Go, used mainly to brute‑force:
- **Directories / files** on web servers
- **DNS subdomains**
- Sometimes **virtual hostnames** or **Amazon S3 buckets**

It’s valued for its speed and low memory footprint.

---

## Installation

If you’re on Kali, Parrot, or most pentest distros:

```bash
sudo apt install gobuster
```

Or, install from source:

```bash
go install github.com/OJ/gobuster/v3@latest
```

---

## Basic Usage: Directory brute‑forcing

Suppose you want to find hidden directories on:

```
http://example.com
```

You’ll need:
- The target URL
- A wordlist (e.g., `/usr/share/wordlists/dirb/common.txt`)

**Command:**

```bash
gobuster dir -u http://example.com -w /usr/share/wordlists/dirb/common.txt
```

Let’s break it down:
- `dir` → use the directory brute‑forcing mode
- `-u` → target URL
- `-w` → path to the wordlist

---

## Common useful options

|Option|Purpose|
|---|---|
|`-x php,txt,html`|Append extensions to words (e.g., index.php)|
|`-t 50`|Number of concurrent threads (default: 10)|
|`-o result.txt`|Output to file|
|`-s 200,204,301,302,307,403`|Only show these HTTP status codes|
|`-b 404`|Blacklist 404s (useful if the server returns a custom page for not found)|
|`-q`|Quiet mode (only shows found URLs)|

---

## Example: look for common PHP files

```bash
gobuster dir -u http://example.com -w /usr/share/wordlists/dirb/common.txt -x php,txt,html -t 50 -o gobuster_results.txt
```

---

## DNS subdomain brute‑forci

If you have a domain (e.g., `example.com`) and a subdomain wordlist (e.g., `subdomains-top1million-5000.txt`):

```bash
gobuster dns -d example.com -w subdomains-top1million-5000.txt
```

**Options:**
- `dns` → DNS brute‑forcing mode
- `-d` → domain
- `-w` → wordlist

---

## VHost brute‑forcing (virtual hosts)

Useful if the server might respond differently based on the `Host` header.

```bash
gobuster vhost -u http://example.com -w /usr/share/wordlists/seclists/Discovery/DNS/subdomains-top1million-5000.txt
```

---

## Summary of modes:

|Mode|Use for|
|---|---|
|`dir`|Discover directories & files|
|`dns`|Find subdomains|
|`vhost`|Discover virtual hosts by brute‑forcing Host header|
