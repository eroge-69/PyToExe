import os
import sys

# source and destination paths
src = sys.argv[1]
dst = sys.argv[2]

#print(src)
#print(dst)

# create symbolic link
os.symlink(src, dst)
#print("Link created")