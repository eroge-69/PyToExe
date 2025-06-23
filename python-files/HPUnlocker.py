#!/usr/bin/python3
# Python 3.7.0 (v3.7.0:1bf9cc5093, Jun 27 2018, 04:59:51) [MSC v.1914 64 bit (AMD64)]

import mmap, shutil, sys

if len(sys.argv) != 2:
    print('Please provide a HP BIOS image .bin file as first parameter!')
    sys.exit(1)

path = sys.argv[1]
splitpath = path.split('.')
newpath = splitpath[0] + '_unlocked.' + splitpath[1]
shutil.copyfile(path, newpath)
loc_old = 0
word = b'U\x00s\x00e\x00r\x00C\x00r\x00e\x00d'
oldword = b'$VSS'
oldword_key = b'B\x00i\x00o\x00s\x00U\x00s\x00e\x00r'
oldword_end = b'\xaaU'

with open(newpath, 'r+') as (f):
    with mmap.mmap(f.fileno(), 0) as (m):
        m.seek(0)
        loc = m.find(oldword)
        if loc == -1:
            m.seek(0)
            loc = m.find(word)
            if loc == -1:
                print('ERROR: Unable to find HP BIOS password - is this a correct HP BIOS image?')
                sys.exit(1)

            print('New BIOS detected')
            for j in range(0, 100):
                if j > 9 and j < 14:
                    m[loc + 16 + j:loc + 17 + j] = b'\xff'
                else:
                    m[loc + 16 + j:loc + 17 + j] = b'\x00'

        else:
            print('Old BIOS detected')
            while True:
                loc_start = m.find(oldword_key, loc_old + 2)
                loc_len = m.find(oldword_end, loc_start) - loc_start - 22
                print(loc_start)
                if loc_start == -1:
                    break
                for i in range(0, loc_len):
                    m[loc_start + 22 + i:loc_start + 23 + i] = b'\xff'

                loc_old = loc_start

            m.flush()
            m.seek(0)
            f.seek(0)

        print('OK')
