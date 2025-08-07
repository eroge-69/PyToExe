import time
import random
import os
import sys

fake_files = [
    "user_data.db", "config.sys", "backup_01.tar.gz", "logfile.log",
    "system32.dll", "hidden.img", "credentials.txt", "email_backup.zip",
    "chat_logs.json", "metadata.xml"
]

fake_status = [
    "Uploading", "Encrypting", "Verifying", "Transferring", "Processing",
    "Scanning", "Injecting", "Packaging"
]

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def generate_fake_upload_line():
    file = random.choice(fake_files)
    status = random.choice(fake_status)
    percent = random.randint(1, 100)
    speed = round(random.uniform(1.0, 10.0), 2)
    return f"[{status}] {file} ... {percent}% complete at {speed} MB/s"

def main():
    clear_screen()
    print("Initializing secure data transfer...\n")
    time.sleep(1)
    try:
        while True:
            print(generate_fake_upload_line())
            time.sleep(random.uniform(0.1, 0.5))
    except KeyboardInterrupt:
        print("\n\n[Process Interrupted] Secure session terminated.")
        sys.exit(0)

if __name__ == "__main__":
    main()
