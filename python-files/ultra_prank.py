import pyautogui, time, os, ctypes, random, threading, subprocess
from PIL import Image
from colorama import init, Fore

init()
pyautogui.FAILSAFE = False

# Runtime duration in seconds
runtime_duration = 120
start_time = time.time()

# Hacking messages
logs = [
    "[INFECTED] Injecting trojan into svchost.exe",
    "[STEALING] Transmitting webcam feed to 193.168.0.66",
    "[HACK] Accessing admin panel...",
    "[INSTALL] Rootkit installing on drive C:\\",
    "[LOCKED] Encrypting files...",
    "[DOWNLOADING] ransomware.exe... complete!",
    "[SPY] Keylogger active on port 8080",
    "[OVERWRITE] BIOS override initiated",
    "[DELETE] System32 scheduled for deletion",
    "[ACCESS GRANTED] Root access achieved",
    "[FIREWALL BREACHED] Port 445 open",
    "[WARNING] Unidentified script running in background",
]

def show_terminal_output():
    os.system("cls" if os.name == "nt" else "clear")
    print(Fore.GREEN + "Initializing remote access console...\n")
    time.sleep(2)
    for _ in range(60):
        print(Fore.RED + random.choice(logs))
        time.sleep(random.uniform(0.2, 0.4))
        if time.time() - start_time > runtime_duration:
            break

def open_notepad_logs():
    time.sleep(5)
    content = "\n".join(logs)
    path = "C:\\Windows\\Temp\\virus_log.txt"
    with open(path, "w") as f:
        f.write(content)
    subprocess.Popen(["notepad.exe", path])

def fake_popup():
    time.sleep(10)
    for _ in range(3):
        ctypes.windll.user32.MessageBoxW(0,
            "Virus download complete.\nSystem will restart soon.",
            "System Breach", 0x10)
        time.sleep(5)

def screen_flash():
    time.sleep(15)
    img = Image.new("RGB", (1920, 1080), (0, 0, 0))
    img_path = "black.jpg"
    img.save(img_path)
    for _ in range(3):
        os.startfile(img_path)
        time.sleep(2)

def final_fake_shutdown():
    ctypes.windll.user32.MessageBoxW(0,
        "Windows has encountered a critical error and must restart.",
        "CRITICAL SYSTEM FAILURE", 0x30)
    os.system("cls")
    print(Fore.BLUE + "Shutting down...")
    time.sleep(3)
    print(Fore.RED + "Shutdown failed. Recovery starting...")
    time.sleep(3)
    ctypes.windll.user32.MessageBoxW(0,
        "System recovery complete.\nNo damage detected.",
        "System Restored", 0x40)

# Launch all threads
def main():
    threads = [
        threading.Thread(target=show_terminal_output),
        threading.Thread(target=open_notepad_logs),
        threading.Thread(target=fake_popup),
        threading.Thread(target=screen_flash),
    ]
    for t in threads: t.start()
    for t in threads: t.join()

    final_fake_shutdown()

if __name__ == "__main__":
    print("🧠 Launching prank in 5 seconds...")
    time.sleep(5)
    main()
