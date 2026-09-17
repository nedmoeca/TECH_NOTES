#!/usr/bin/env python3
# bam.py 
"""Read Background Activity Moderator (BAM) execution records from a SYSTEM hive.
Usage: bam.py <path-to-SYSTEM> [substring-filter]"""
import sys, struct, binascii, datetime
from regipy.registry import RegistryHive

EPOCH = datetime.datetime(1601, 1, 1)
PATHS = [
    r'\ControlSet001\Services\bam\State\UserSettings',
    r'\ControlSet001\Services\bam\UserSettings',
    r'\ControlSet002\Services\bam\State\UserSettings',
]

def to_bytes(v):
    if isinstance(v, (bytes, bytearray)):
        return bytes(v)
    if isinstance(v, str):
        return binascii.unhexlify(v.replace(' ', '').replace('\n', ''))
    if isinstance(v, (list, tuple)):
        return bytes(v)
    raise TypeError('unhandled value type: %r' % type(v))

def main():
    if len(sys.argv) < 2:
        sys.exit("usage: bam.py <path-to-SYSTEM> [substring-filter]")
    needle = sys.argv[2].lower() if len(sys.argv) > 2 else None
    hive = RegistryHive(sys.argv[1])

    key = None
    for p in PATHS:
        try:
            key = hive.get_key(p)
            print('# BAM key: %s' % p, file=sys.stderr)
            break
        except Exception:
            continue
    if key is None:
        sys.exit('BAM key not found under any known path')

    rows = []
    for sid_key in key.iter_subkeys():
        sid = sid_key.name
        for val in (sid_key.get_values() or []):
            if val.name in ('Version', 'SequenceNumber'):
                continue
            try:
                blob = to_bytes(val.value)
                if len(blob) < 8:
                    continue
                ft = struct.unpack_from('<Q', blob, 0)[0]
                if not ft:
                    continue
                when = EPOCH + datetime.timedelta(microseconds=ft // 10)
            except Exception:
                continue
            if needle and needle not in val.name.lower():
                continue
            rows.append((when, sid, val.name))

    for when, sid, name in sorted(rows):
        print('%s | %s | %s' % (when.strftime('%Y-%m-%d %H:%M:%S'), sid, name))
    print('# %d entries' % len(rows), file=sys.stderr)

if __name__ == '__main__':
    main()
