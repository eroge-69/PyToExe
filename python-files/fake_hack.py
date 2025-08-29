import time
import random
import os
import sys

# تغيير لون الكتابة للأخضر (لو Windows CMD)
if os.name == "nt":
    os.system("color a")

fake_cmds = [
    "Connecting to server 192.168.1.1 ...",
    "Bypassing firewall...",
    "Access granted.",
    "Downloading passwords.txt...",
    "Encrypting data...",
    "Uploading backdoor...",
    "Connection established.",
    "Scanning system files...",
    "Injection successful.",
    "Mission accomplished."
]

def fake_hack():
    for cmd in fake_cmds:
        for ch in cmd:
            sys.stdout.write(ch)
            sys.stdout.flush()
            time.sleep(random.uniform(0.02, 0.07))
        print()
        time.sleep(random.uniform(0.3, 1))

    print("\n>>> HACKING COMPLETE ✅")

if __name__ == "__main__":
    fake_hack()
    input("\nPress Enter to exit...")
