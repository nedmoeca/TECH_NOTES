## Kali Terminal Setup — Install & Usage Reference

Reference for a Kali VM on VMware. Shell is zsh.


### 1. Full Install (from scratch)

Run these on a fresh Kali VM. If a package is already present, apt just says "already the newest version" — that's fine, move on.

```bash
# System update
sudo apt update && sudo apt full-upgrade -y

# VMware guest tools (clipboard, drag-drop, auto-resize)
sudo apt install -y open-vm-tools open-vm-tools-desktop

# Core CLI tools
sudo apt install -y fzf ripgrep fd-find bat eza zoxide tmux jq

# Zsh plugins (Kali usually ships these already)
sudo apt install -y zsh-autosuggestions zsh-syntax-highlighting
```

#### Make sure you're actually in zsh

Kali styles its bash prompt identically to zsh, so it's easy to think you're in zsh when you're not. Sourcing a `.zsh` file from bash throws a wall of `bad substitution` / `command not found` errors — that's the symptom.

```bash
echo $0          # should print /bin/zsh
chsh -s /bin/zsh # if not — then log out and back in
```

#### Verify

```bash
dpkg -l | grep open-vm-tools
systemctl status vmtoolsd
rg --version && fzf --version && eza --version && tmux -V
```


### 2. .zshrc Configuration

Kali's default `.zshrc` already sources the two zsh plugins inside `if [ -f ... ]` guards. Check before adding anything:

```bash
grep -n "zsh-autosuggestions\|zsh-syntax-highlighting" ~/.zshrc
```

Two lines each = already done, don't add more. Double-sourcing is harmless but slows startup and can make the autosuggestion widgets act oddly.

Then append the custom block:

```bash
cat >> ~/.zshrc << 'EOF'

# --- custom ---
alias fd='fdfind'
alias bat='batcat'
alias ll='eza -la --git --group-directories-first'
alias lt='eza --tree --level=2'
alias ports='ss -tulpn'
alias myip='curl -s ifconfig.me; echo'

eval "$(zoxide init zsh)"
source /usr/share/doc/fzf/examples/key-bindings.zsh
source /usr/share/doc/fzf/examples/completion.zsh
EOF

source ~/.zshrc
```

**Why `fd` and `bat` need aliases:** on Debian/Kali the binaries install as `fdfind` and `batcat` because of package name collisions with unrelated software.

**Why not alias `cat=bat`:** overriding `cat` globally breaks pipes and scripts in ways that are annoying to debug. Keep them separate.


### 3. Usage

#### fzf — fuzzy finder

The biggest daily win. Three keybindings:

|Key|Does|
|---|---|
|`Ctrl+R`|Fuzzy search command history|
|`Ctrl+T`|Fuzzy find a file, paste its path into current command|
|`Alt+C`|Fuzzy `cd` into a subdirectory|
|`Esc`|Back out of any fzf overlay|

`Ctrl+R` is the one to build a habit around. Instead of pressing ↑ forty times, type any fragment of an old command and it filters instantly. Recalling a 60-character nmap invocation from last week costs three keystrokes.

The status line (e.g. `26/26 (0)`) means: matches / total history / selected.

**Ctrl+T example:** type `cat` then hit `Ctrl+T` → pick a file → path is inserted. Good for when you half-remember where a wordlist lives.

#### zoxide — smart directory jumping

```bash
z htb          # jumps to ~/Labs/HTB from anywhere
z              # jumps home
zi             # interactive picker of known dirs
```

Learns from your actual `cd` history and ranks by frequency + recency. Needs a few days of normal use before it's useful — it can only jump to places you've already been.

#### ripgrep (rg) — fast recursive grep

```bash
rg password                      # search recursively from here
rg -i password /etc 2>/dev/null  # case-insensitive, hide permission errors
rg -n "api[_-]?key"              # show line numbers
rg -t php upload                 # only .php files
rg -l secret                     # list matching filenames only
rg -P '(?<=token=)\w+'           # PCRE2 lookbehind (needs +pcre2 build)
```

Skips binaries and respects `.gitignore` by default. Sweeping a web root for hardcoded creds takes seconds.

#### fd — fast file finding

```bash
fd config              # anything named *config*
fd -e conf /etc        # by extension
fd -H secret           # include hidden files
fd -t d wordlists      # directories only
fd -e log -x rm        # execute a command per result
```

Sane defaults, no `-type f -name '*...*'` ceremony.

#### bat — cat with syntax highlighting

```bash
bat script.py             # highlighted + line numbers
bat -n file.txt           # numbers only, no decorations
bat --paging=never f.txt  # don't open a pager
rg -n foo | bat           # highlight grep output
```

Line numbers matter more than they sound — when a writeup says "line 47 of the config," you can see it directly.

#### eza — modern ls

```bash
ll             # alias: long, all, git status
lt             # alias: tree, 2 levels deep
eza --tree --level=3 --long
eza -la --sort=modified
```

`lt` is the fast way to orient yourself in an unfamiliar directory structure.

#### jq — JSON processor

```bash
curl -s ifconfig.me/all.json | jq          # pretty-print
cat data.json | jq '.users[].name'         # extract a field
cat data.json | jq '.[] | select(.admin)'  # filter
cat data.json | jq -r '.token'             # raw output, no quotes
```

`-r` matters when piping a value into another command — without it you get quotes wrapped around the string.

#### zsh plugins

- **Autosuggestions** — greyed-out completion from history appears as you type. Press `→` (right arrow) to accept. Needs history to work, so it's quiet on a fresh install.
- **Syntax highlighting** — commands turn green when they exist on your PATH, red when they don't. Catches typo'd binary names _before_ you hit enter. Colour appears live as you type; it does not survive copy-paste, so test it by watching the live terminal, not the scrollback.


### 4. VMware Notes

- Clipboard needs both `open-vm-tools-desktop` **and** VM → Settings → Options → Guest Isolation → "Enable copy and paste" ticked.
- Paste into a terminal is `Ctrl+Shift+V`, not `Ctrl+V`.
- Resize test: drag the VMware window. If the desktop resolution follows, guest tools are working.
- **Take a snapshot once your terminal is configured.** Kali installs accumulate cruft fast, and rolling back to a clean-but-configured state saves hours.


### 5. Still To Do

- **tmux** — persistent sessions so a dropped shell doesn't kill a long scan, plus split panes. Real learning curve, worth it.
- **Nerd Font** (e.g. JetBrainsMono Nerd Font) — so prompt glyphs and eza icons render instead of boxes.
- **Terminal scrollback** — raise to ~50,000 lines in the terminal profile. The default is small and you'll lose scan output.
<div align="center">
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
</div>

## Grapo

`~/.zshrc` is a plain text config file in your home directory that zsh reads every time it starts a new shell. Anything you put in it — aliases, functions, environment variables — becomes available automatically in every terminal you open. Right now `grapo` doesn't exist because you haven't defined it anywhere; putting it in `.zshrc` makes it a permanent command you can use forever.

"Source" means telling your current shell to re-read that file right now, instead of waiting until you open a new terminal. When you edit `.zshrc`, the shell you already have open doesn't know about the change yet — `source ~/.zshrc` reloads it so `grapo` works immediately without closing your terminal.

`grapo` reads Nmap's output from stdin, echoes the full scan back to your terminal via `tee /dev/tty` so you can watch it run, then extracts just the open-port numbers and prints them as a comma-joined list on their own line. Use it by piping Nmap straight into it: `nmap -p- --min-rate 5000 -Pn TARGET | grapo`.

Here's the whole thing start to finish. First, append the function to the file:

```
cat >> ~/.zshrc << 'EOF'

grapo() {
  tee /dev/tty | grep -oP '^\d+(?=/tcp\s+open)' | paste -sd, | sed 's/^/\n/'
}
EOF
```

That `cat >> file << 'EOF'` pattern writes everything between the two `EOF` markers onto the end of `~/.zshrc` (the `>>` means append, not overwrite — important, you don't want to wipe your config). The quotes around `'EOF'` stop the shell from mangling the `$` in the regex.

Then reload it so your current shell picks it up:

```
source ~/.zshrc
```

Quick component breakdown for reference:

- `tee /dev/tty` — splits the piped input: one copy goes to your terminal so you see the live scan, the other continues down the pipe for parsing.
- `grep -oP '^\d+(?=/tcp\s+open)'` — `-o` prints only the matched text, `-P` enables Perl regex. The pattern grabs a leading number only when it's immediately followed by `/tcp open`, so you get the port number and nothing else.
- `paste -sd,` — `-s` joins all lines into one, `-d,` sets the delimiter to a comma. Turns the column of ports into `22,80,1515`.
- `sed 's/^/\n/'` — prepends a newline so the port list sits on its own line, cleanly separated from Nmap's report above it.