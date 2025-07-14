import time
import os
import random
import sys

messages = [
    "[*] Accessing system files...",
    "[*] Bypassing firewall...",
    "[*] Injecting malware...",
    "[*] Downloading payload...",
    "[*] Deleting system32...",
    "[!] SYSTEM BREACH DETECTED!",
    "[!] Encrypting files...",
    "[!] Sending data to hacker server...",
    "[✔] HACK COMPLETE!"
]

def type_effect(text, delay=0.05):
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
    print()

os.system('cls' if os.name == 'nt' else 'clear')
type_effect("Initializing hack tool v3.0...")
time.sleep(1)

for msg in messages:
    type_effect(msg, delay=random.uniform(0.03, 0.08))
    time.sleep(random.uniform(0.5, 1.5))

# Fake system crash screen
os.system('cls' if os.name == 'nt' else 'clear')
type_effect("💀 Your system has been hacked 💀", 0.1)
type_effect("All files encrypted. Contact 0xH4ck3r for decryption key.", 0.05)
type_effect("😈 Good luck, human.", 0.1)

# Looping blinking cursor
while True:
    sys.stdout.write("\rPress any key to exit...")
    sys.stdout.flush()
    time.sleep(0.5)
    sys.stdout.write("\r                       ")
    sys.stdout.flush()
    time.sleep(0.5)


