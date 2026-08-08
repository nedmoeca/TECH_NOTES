## What is `ffuf`?

**`ffuf`** (pronounced “fuff”) stands for **Fuzz Faster U Fool**. It’s a super-fast web fuzzer used for:
- **Content discovery** (hidden files/directories)
- **Parameter fuzzing**
- **Subdomain enumeration**
- Basically, brute-forcing any part of an HTTP request.

---

## Installing `ffuf`

If you haven’t already:

```bash
# On Kali Linux
sudo apt install ffuf

# Or using Go (most common way)
go install github.com/ffuf/ffuf/v2@latest
```

---

## Basic usage

**The basic syntax:**

```bash
ffuf -u https://example.com/FUZZ -w wordlist.txt
```

**What this means:**

- `-u` specifies the **URL** — `FUZZ` is the placeholder.
- `-w` specifies the **wordlist**.

Example: Discover hidden directories:

```bash
ffuf -u https://example.com/FUZZ -w /usr/share/wordlists/dirb/common.txt
```

---

## Common examples

### Directory brute-forcing

```bash
ffuf -u https://target.com/FUZZ -w /usr/share/wordlists/dirb/common.txt
```

### File extension fuzzing

```bash
ffuf -u https://target.com/FUZZ.php -w wordlist.txt
```

Or try multiple extensions:

```bash
ffuf -u https://target.com/FUZZ -w wordlist.txt -e .php,.bak,.txt
```

### Virtual host fuzzing

```bash
ffuf -u https://FUZZ.target.com/ -w subdomains.txt -H "Host: FUZZ.target.com"
```

---

## Useful options

|Option|What it does|
|---|---|
|`-mc`|Match HTTP status code. E.g. `-mc 200`|
|`-fs`|Filter by response size. E.g. `-fs 4242`|
|`-fw`|Filter by word count. E.g. `-fw 10`|
|`-H`|Add a header. E.g. `-H "Cookie: auth=true"`|
|`-X`|Change HTTP method. E.g. `-X POST`|
|`-d`|Send POST data. E.g. `-d "username=FUZZ"`|
|`-recursion`|Recursively fuzz found directories.|

---

## Example: Fuzzing POST data

```bash
ffuf -u https://example.com/login -X POST -d "username=admin&password=FUZZ" -w passwords.txt
```

---

## Filtering junk

Sometimes results are noisy. For example:

If the valid page returns 200 and so do the 404s — filter by size or words:

```bash
ffuf -u https://site.com/FUZZ -w words.txt -fs 1234
```

This filters out responses with size `1234`.


---

## Pro Tips

✅ Use good wordlists: e.g. `SecLists` (`/usr/share/seclists/`).  
✅ Always check the response codes/sizes manually.  
✅ Combine `ffuf` with Burp or `proxychains` to inspect traffic.  
✅ Respect scope & always have permission!
