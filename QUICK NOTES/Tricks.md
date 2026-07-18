how do I add it ~/.zshrc then source? what does that even mean?

`~/.zshrc` is a plain text config file in your home directory that zsh reads every time it starts a new shell. Anything you put in it — aliases, functions, environment variables — becomes available automatically in every terminal you open. Right now `grapo` doesn't exist because you haven't defined it anywhere; putting it in `.zshrc` makes it a permanent command you can use forever.

"Source" means telling your _current_ shell to re-read that file right now, instead of waiting until you open a new terminal. When you edit `.zshrc`, the shell you already have open doesn't know about the change yet — `source ~/.zshrc` reloads it so `grapo` works immediately without closing your terminal.

Here's the whole thing start to finish. First, append the function to the file:

```
cat >> ~/.zshrc << 'EOF'

grapo() {
  grep -oP '^\d+(?=/tcp\s+open)' | paste -sd, | sed 's/^/\n/'
}
EOF
```

That `cat >> file << 'EOF'` pattern writes everything between the two `EOF` markers onto the end of `~/.zshrc` (the `>>` means append, not overwrite — important, you don't want to wipe your config). The quotes around `'EOF'` stop the shell from mangling the `$` in the regex.

Then reload it:

```
source ~/.zshrc
```