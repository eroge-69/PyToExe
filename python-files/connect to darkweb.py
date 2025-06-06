import time
import random
import sys
import string
import webbrowser

def type_out(text, delay=0.05):
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
    print()

def matrix_effect(lines=20, width=80, duration=5):
    chars = string.ascii_letters + string.digits + string.punctuation
    end_time = time.time() + duration
    while time.time() < end_time:
        print(''.join(random.choice(chars) for _ in range(width)))
        time.sleep(0.1)

def brute_force_simulation(password="Join"):
    attempts = 0
    chars = string.ascii_letters + string.digits + string.punctuation
    found = ""
    type_out("[+] open darknet packages...", 0.02)
    while found != password:
        attempt = ''.join(random.choice(chars) for _ in range(len(password)))
        attempts += 1
        print(f"[Attempt {attempts:06d}] Trying: {attempt}", end='\r')
        if attempt == password:
            found = attempt
            break
    print(f"\n[+] Password cracked: {found} in {attempts} attempts!")

def main():
    type_out("\n[+] Connecting to the Darkbrowsing...")
    time.sleep(1)
    type_out("[+] Connect to Darkweb Network...")
    webbrowser.open("https://iplogger.com/2c1Zg4")  # Öffnet den Discord-Invite im Browser
    time.sleep(1)
    type_out("[+] Access granted!\n")
    time.sleep(0.5)
    matrix_effect()
    brute_force_simulation()
    type_out("[+] Downloading Darknet packages...")
    time.sleep(2)
    type_out("[+] your Darknet packages have been downloaded successfully!\n")
    type_out("[+] Disconnecting from the Darkweb Network...")
    time.sleep(1)
    type_out("[+] Disconnecting...\n")

if __name__ == "__main__":
    main()