import time
import os
import sys
import random

def clear_screen():
    """Clears the console screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def typewriter_print(text, delay=0.015):
    """Prints text with a typewriter effect, faster for system messages."""
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
    print()

def progress_bar(duration, description, length=40):
    """Displays a detailed progress bar."""
    start_time = time.time()
    sys.stdout.write(f"{description} [ {' ' * length} ] 0% \r")
    sys.stdout.flush()
    while time.time() - start_time < duration:
        progress = int(((time.time() - start_time) / duration) * length)
        percent = int(((time.time() - start_time) / duration) * 100)
        sys.stdout.write(f"{description} [ {'#' * progress}{' ' * (length - progress)} ] {percent}% \r")
        sys.stdout.flush()
        time.sleep(0.1)
    sys.stdout.write(f"{description} [ {'#' * length} ] 100% COMPLETE\n")
    sys.stdout.flush()
    time.sleep(0.5)

def run_anti_piracy_sequence():
    """Contains the main anti-piracy check and lockdown sequence."""
    clear_screen()
    print("\033[94m===================================================\033[0m")
    print("\033[94m|                                                 |\033[0m")
    print("\033[94m|           GLOBAL LICENSE AUTHENTICATION         |\033[0m")
    print("\033[94m|           SYSTEM V4.7.1 - SECURE BOOT           |\033[0m")
    print("\033[94m|                                                 |\033[0m")
    print("\033[94m===================================================\033[0m\n")
    
    typewriter_print(f"[{time.strftime('%H:%M:%S')}] Initializing secure boot environment...", delay=0.01)
    time.sleep(0.5)
    progress_bar(1.5, f"[{time.strftime('%H:%M:%S')}] Validating system checksums", 30)
    progress_bar(2.0, f"[{time.strftime('%H:%M:%S')}] Establishing encrypted tunnel (AES-256)", 30)
    typewriter_print(f"[{time.strftime('%H:%M:%S')}] Connecting to GLAS Mainframe (GEO-SYNC: {random.randint(10,99)}.X.X.X)...", delay=0.01)
    time.sleep(1.5)
    print("\n")

    typewriter_print(f"[{time.strftime('%H:%M:%S')}] Scanning localized license repository for anomalies...", delay=0.01)
    time.sleep(1)
    for i in range(5):
        status = random.choice(["OK", "VERIFIED", "SYNCING", "PENDING"])
        typewriter_print(f"[{time.strftime('%H:%M:%S')}]   -> Checking Module {i+1}: PID_HASH_{random.randint(10000, 99999)} [{status}]", delay=0.005)
        time.sleep(random.uniform(0.1, 0.4))
    print("\n")
    
    typewriter_print(f"[{time.strftime('%H:%M:%S')}] Cross-referencing against global unauthorized access logs...", delay=0.01)
    time.sleep(2)
    progress_bar(3.0, f"[{time.strftime('%H:%M:%S')}] Performing deep integrity scan (Level 5)", 40)
    typewriter_print(f"[{time.strftime('%H:%M:%S')}] Access Violation Signature Detected! Processing...", delay=0.005)
    time.sleep(1)

    clear_screen()
    print("\033[91m===================================================\033[0m") # Red color
    print("\033[91m|                                                 |\033[0m")
    print("\033[91m|             AUTHENTICATION FAILED               |\033[0m")
    print("\033[91m|           SEVERE LICENSE VIOLATION              |\033[0m")
    print("\033[91m|                                                 |\033[0m")
    print("\033[91m===================================================\033[0m\n")

    typewriter_print(f"\033[91m[{time.strftime('%H:%M:%S')}] [CRITICAL_ERROR_LVA-0x00FF]\033[0m", delay=0.01)
    typewriter_print("\033[91mUnauthorized access attempt detected: Digital Signature Mismatch.\033[0m", delay=0.02)
    time.sleep(1)
    typewriter_print("\033[91mThis instance of software is operating outside authorized parameters.\033[0m", delay=0.02)
    time.sleep(1.5)
    typewriter_print("\033[91mAs per Section 7.b of the EULA, illicit usage detected. Initiating countermeasures.\033[0m", delay=0.02)
    time.sleep(2)

    print("\n")
    typewriter_print(f"\033[91m[{time.strftime('%H:%M:%S')}] Commencing System Lockdown Protocol (SLP-7)...\033[0m", delay=0.02)
    time.sleep(1)
    typewriter_print(f"\033[91m[{time.strftime('%H:%M:%S')}] Disconnecting network interfaces...\033[0m", delay=0.01)
    progress_bar(1.0, f"\033[91m[{time.strftime('%H:%M:%S')}] Shutting down non-essential processes\033[0m", 25)
    typewriter_print(f"\033[91m[{time.strftime('%H:%M:%S')}] Initiating forced application termination...\033[0m", delay=0.01)
    time.sleep(1)

    clear_screen()
    print("\033[91m===================================================\033[0m")
    print("\033[91m|                                                 |\033[0m")
    print("\033[91m|             SYSTEM LOCKDOWN ACTIVE              |\033[0m")
    print("\033[91m|                                                 |\033[0m")
    print("\033[91m===================================================\033[0m\n")
    
    typewriter_print("\033[91mAccess to this system has been permanently restricted due to EULA violation.\033[0m", delay=0.03)
    typewriter_print("\033[91mAll user processes have been suspended. Further unauthorized access attempts will escalate protocols.\033[0m", delay=0.03)
    print("\n")
    typewriter_print("\033[91mThis application will now cease all operations.\033[0m", delay=0.04)
    typewriter_print("\033[91mPlease refer to official documentation for legal implications.\033[0m", delay=0.04)
    time.sleep(5)
    # The script will effectively end here, by looping back to the welcome screen.

def main():
    while True: # Loop to "reopen" if interrupted
        clear_screen()
        print("\033[92m===================================================\033[0m")
        print("\033[92m|                                                 |\033[0m")
        print("\033[92m|        Welcome to the Chrome Anti-Piracy        |\033[0m")
        print("\033[92m|                  Program                        |\033[0m")
        print("\033[92m|                                                 |\033[0m")
        print("\033[92m===================================================\033[0m\n")
        print("\033[92m      Click ENTER to begin license verification.\033[0m")
        print("\033[92m      (Attempting to exit will restart program)\033[0m\n")

        try:
            input() # Wait for user to press Enter
            run_anti_piracy_sequence() # Run the main hoax sequence
            # No 'break' here. After the sequence, it just loops back to the welcome screen.
            # This makes the "lockdown" feel more permanent/inescapable if they don't manually close the terminal.
        except KeyboardInterrupt:
            # If Ctrl+C is pressed, catch it and loop again, effectively "reopening"
            clear_screen()
            print("\033[91m\n[WARNING]: Unauthorized program termination attempt detected.\033[0m")
            print("\033[91m[WARNING]: Anti-Piracy protocols are self-healing. Re-initializing...\033[0m")
            time.sleep(3)
            # The loop continues, showing the welcome screen again

if __name__ == "__main__":
    main()