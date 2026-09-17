#!/usr/bin/env python3
"""Resolve character-level %VAR% substitution in an obfuscated batch script.
Usage: deobf.py <batch-file>   (prints resolved script to stdout)"""
import sys, re

SET_RE = re.compile(r'^\s*set\s+(?:"(?P<qn>[^"=]+)=(?P<qv>[^"]*)"|(?P<n>[A-Za-z0-9_#@$-]+)=(?P<v>.*))\s*$',
                    re.IGNORECASE)
VAR_RE = re.compile(r'%([A-Za-z0-9_#@$-]+)%')

def resolve(text, env, depth=12):
    for _ in range(depth):
        new = VAR_RE.sub(lambda m: env.get(m.group(1).lower(), m.group(0)), text)
        if new == text:
            break
        text = new
    return text

def main():
    if len(sys.argv) < 2:
        sys.exit("usage: deobf.py <batch-file>")
    raw = open(sys.argv[1], 'rb').read().decode('utf-8', 'replace')
    lines = raw.replace('\r\n', '\n').replace('\r', '\n').split('\n')

    env = {}
    for line in lines:
        m = SET_RE.match(line)
        if m:
            name = m.group('qn') or m.group('n')
            val  = m.group('qv') if m.group('qn') is not None else m.group('v')
            env[name.strip().lower()] = val

    for k in list(env):
        env[k] = resolve(env[k], env)

    for n, line in enumerate(lines, 1):
        out = resolve(line, env)
        if out.strip():
            print('%4d  %s' % (n, out))

if __name__ == '__main__':
    main()
