import subprocess
import time

while True:
    subprocess.Popen(['notepad.exe'])
    time.sleep(0.01)  # 10 миллисекунд = 0.01 секунды