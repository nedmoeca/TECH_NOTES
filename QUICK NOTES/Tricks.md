
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