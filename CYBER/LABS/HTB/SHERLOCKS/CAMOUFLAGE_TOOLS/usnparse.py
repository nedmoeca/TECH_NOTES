#!/usr/bin/env python3
"""Minimal USN Journal ($J) v2 record parser.  Usage: usnparse.py <path-to-$J>"""
import sys, struct, datetime
import signal
signal.signal(signal.SIGPIPE, signal.SIG_DFL)

REASONS = [
    (0x00000001, 'DATA_OVERWRITE'),     (0x00000002, 'DATA_EXTEND'),
    (0x00000004, 'DATA_TRUNCATION'),    (0x00000100, 'FILE_CREATE'),
    (0x00000200, 'FILE_DELETE'),        (0x00000800, 'SECURITY_CHANGE'),
    (0x00001000, 'RENAME_OLD_NAME'),    (0x00002000, 'RENAME_NEW_NAME'),
    (0x00004000, 'INDEXABLE_CHANGE'),   (0x00008000, 'BASIC_INFO_CHANGE'),
    (0x00020000, 'COMPRESSION_CHANGE'), (0x00200000, 'STREAM_CHANGE'),
    (0x80000000, 'CLOSE'),
]
EPOCH = datetime.datetime(1601, 1, 1)

def main():
    if len(sys.argv) < 2:
        sys.exit("usage: usnparse.py <path-to-$J>")
    data = open(sys.argv[1], 'rb').read()
    i, emitted = 0, 0
    while i < len(data) - 4:
        ln = struct.unpack_from('<I', data, i)[0]
        if ln == 0 or ln < 60 or ln > 1024 or i + ln > len(data):
            i += 8
            continue
        major = struct.unpack_from('<H', data, i + 4)[0]
        ts    = struct.unpack_from('<Q', data, i + 32)[0]
        rsn   = struct.unpack_from('<I', data, i + 40)[0]
        nlen  = struct.unpack_from('<H', data, i + 56)[0]
        noff  = struct.unpack_from('<H', data, i + 58)[0]
        if major == 2 and nlen and ts and noff + nlen <= ln:
            name  = data[i+noff : i+noff+nlen].decode('utf-16-le', 'replace')
            when  = EPOCH + datetime.timedelta(microseconds=ts // 10)
            flags = ' | '.join(n for b, n in REASONS if rsn & b) or hex(rsn)
            print('%s %s | %s | %s' % (when.strftime('%Y-%m-%d'),
                                       when.strftime('%H:%M:%S.%f'), name, flags))
            emitted += 1
        i += ln
    print('# %d records' % emitted, file=sys.stderr)

if __name__ == '__main__':
    main()
