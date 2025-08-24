import os
import time
import sys
import platform
import random

# Fake hacker-style logs
logs = [
    "[+] Establishing secure connection...",
    "[+] Accessing system kernel...",
    "[+] Injecting payload...",
    "[+] Uploading malicious files...",
    "[+] Disabling firewalls...",
    "[+] Bypassing authentication...",
    "[+] Root access granted!"
]

for log in logs:
    print("\033[92m" + log + "\033[0m")  # green text
    time.sleep(random.uniform(0.5, 1.5))

print("\n[!] System will sleep in 3 seconds...")

# Sleep computer safely
time.sleep(2)
if platform.system() == "Windows":
    os.system("rundll32.exe powrprof.dll,SetSuspendState Sleep")
elif platform.system() == "Darwin":  # macOS
    os.system("pmset sleepnow")
else:
    print("Sleep command not supported.")

time.sleep(3)

print("\n[+] System reboot complete. Access terminated.")
