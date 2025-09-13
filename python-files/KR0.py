import subprocess
import time
import random
import sys
import signal
import os

secret_code = "403"

# Fake “encrypted” file messages
fake_files = [
    "C:\\Users\\User\\Documents\\importantdocs.locked",
    "C:\\Users\\User\\Pictures\\selfie.png.locked",
    "C:\\Users\\User\\Desktop\\personalfiles.exe.locked",
    "C:\\Users\\User\\Downloads\\main.mp4.locked"
]

scary_messages = [
    "!!! WARNING: FILES ENCRYPTED !!!",
    "!!! CRITICAL ERROR: DATA COMPROMISED !!!",
    "!!! RANSOM DETECTED: PAY IN BITCOIN ??? !!!",
    f"!!!  000000000000000000040300000000",
    "SYSTEM LOCKDOWN: ALL FILES MARKED AS .LOCKED",
    "!!! URGENT !!! Your system is encrypted!"
]

def block_ctrl_c(sig, frame):
    print("\n Ctrl+C won’t save you Find the code in the encrypted files.")
signal.signal(signal.SIGINT, block_ctrl_c)

print("KR0.exe")
print("Your 'files' are encrypted...find the code or pay us in bitcoin\n")

opened_notes = []

while True:
    # Pick random scary message or fake encrypted file
    msg = random.choice(scary_messages + [f"Encrypted file: {random.choice(fake_files)}"])
    file_name = f"prank_note_{random.randint(1000,9999)}.txt"
    
    with open(file_name, "w", encoding="utf-8") as f:
        f.write(msg)
    
    # Open Notepad
    proc = subprocess.Popen(["notepad.exe", file_name])
    opened_notes.append(proc)
    
    # Console fake progress bar
    bar = ""
    for i in range(20):
        bar += "#"
        sys.stdout.write(f"\r[ {bar:<20} ] Encrypting files...")
        sys.stdout.flush()
        time.sleep(0.05)
    print("\n")

    # Ask for the secret code
    code = input("Enter secret code to stop the software: ").strip()
    if code == secret_code:
        print("\n correct closing all locked files...")
        for p in opened_notes:
            try:
                p.kill()
            except:
                pass
        break
    else:
        print("last warning. More files encryption in progress...\n")
        time.sleep(1)
