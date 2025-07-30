import subprocess
import time

comando = 'start cmd'

for i in range(20000):
    subprocess.Popen(f'start cmd /k "{comando}"', shell=True)
    time.sleep(0.1)
