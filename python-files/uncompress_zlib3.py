
import zlib
import base64
import numpy as np
# import sys
# print(sys.version_info)

letter="123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`abcdefghijklmnopqrstuvwxyz"
z_list=list(letter)

fd = open('uncompress.txt','wt')
fh = open('compress.txt','rt')

while True:
    line = fh.readline() 
    if not line: 
        break 
    decompressed_data=zlib.decompress(base64.b64decode(line))
    data2=np.frombuffer(decompressed_data, dtype=np.uint8)

    d_list = list(data2)
    sz = len(d_list)
    i=1
    for k in range(0, sz-1):
        m=d_list[i]-1
        d_list[k+1] = z_list[ m ]
        i=i+1
    
    b= ''.join(map(str, d_list ))
    b= b.replace('z', '0')
    fd.write( b)
    fd.write('>\n') 

fd.close()
fh.close()


