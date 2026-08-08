## What is `dirb`?

**`dirb`** is a command-line web content scanner used to brute-force directories and files on a web server.  
It tries to find hidden or unlinked web resources by making HTTP requests using a wordlist.

---

## Installation

On **Kali Linux**, it’s usually pre-installed.  
If not, you can install it with:

```bash
sudo apt update
sudo apt install dirb
```

---

## Basic syntax

```bash
dirb [URL] [wordlist]
```

**Example:**

```bash
dirb http://example.com /usr/share/wordlists/dirb/common.txt
```

---

## How it works

- `URL` — The base URL to scan.
- `wordlist` — A file with potential directory and file names.

If you omit the wordlist, `dirb` uses its default: `/usr/share/dirb/wordlists/common.txt`.

---

## Example scan

```bash
dirb http://target.com
```

This runs with the default wordlist.
**Common locations for wordlists:**
- `/usr/share/wordlists/dirb/`
- `/usr/share/wordlists/` (look for `rockyou.txt` for passwords, `common.txt` for directories)

---

## Useful options

|Option|What it does|
|---|---|
|`-o output.txt`|Save output to a file|
|`-r`|Don’t send the “Referer” header|
|`-S`|Silent mode (only shows found results)|
|`-X .php,.html`|Add file extensions to try|
|`-i`|Ignore case sensitivity|
|`-t 20`|Number of concurrent threads|

**Example with extensions:**

```bash
dirb http://target.com /usr/share/wordlists/dirb/common.txt -X .php,.bak,.txt
```

This tries each word with `.php`, `.bak`, `.txt`.

---

## Alternative tools

`dirb` is good but older — alternatives like `gobuster` or `feroxbuster` are faster and support multi-threading better.
