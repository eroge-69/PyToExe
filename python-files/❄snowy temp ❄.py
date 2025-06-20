import ctypes
import os
import sys
import time
from colorama import init, Fore, Style

init(autoreset=True)

def make_console_transparent(alpha=200):
    hwnd = ctypes.windll.kernel32.GetConsoleWindow()
    if hwnd:
        GWL_EXSTYLE = -20
        WS_EX_LAYERED = 0x80000
        LWA_ALPHA = 0x2
        ctypes.windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE,
            ctypes.windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE) | WS_EX_LAYERED)
        ctypes.windll.user32.SetLayeredWindowAttributes(hwnd, 0, alpha, LWA_ALPHA)

def disable_resize():
    hwnd = ctypes.windll.kernel32.GetConsoleWindow()
    if hwnd:
        GWL_STYLE = -16
        WS_SIZEBOX = 0x00040000
        WS_MAXIMIZEBOX = 0x00010000
        style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_STYLE)
        style = style & ~WS_SIZEBOX & ~WS_MAXIMIZEBOX
        ctypes.windll.user32.SetWindowLongW(hwnd, GWL_STYLE, style)

def print_banner():
    banner_lines = [
        "  ███████╗███╗   ██╗ ██████╗ ██╗    ██╗██╗   ██╗",
        "  ██╔════╝████╗  ██║██╔═══██╗██║    ██║╚██╗ ██╔╝",
        " ███████╗██╔██╗ ██║██║   ██║██║ █╗ ██║ ╚████╔╝",
        "╚════██║██║╚██╗██║██║   ██║██║███╗██║  ╚██╔╝",
        "███████║██║ ╚████║╚██████╔╝╚███╔███╔╝   ██║",
        "╚══════╝╚═╝  ╚═══╝ ╚═════╝  ╚══╝╚══╝    ╚═╝"
    ]
    try:
        width = os.get_terminal_size().columns
    except OSError:
        width = 80

    print()
    for line in banner_lines:
        padding = (width - len(line)) // 2
        print(Fore.BLUE + " " * padding + line)
    print()

def slow_print_inline(text, delay=0.05, color=Fore.BLUE):
    for char in text:
        sys.stdout.write(color + char)
        sys.stdout.flush()
        time.sleep(delay)
    sys.stdout.write(Style.RESET_ALL)

def slow_print(text, delay=0.05, color=Fore.BLUE):
    for char in text:
        sys.stdout.write(color + char)
        sys.stdout.flush()
        time.sleep(delay)
    sys.stdout.write(Style.RESET_ALL + "\n")

def countdown(seconds):
    for i in range(seconds, 0, -1):
        sys.stdout.write(Fore.RED + f"\rProgram will close in {i} seconds...   ")
        sys.stdout.flush()
        time.sleep(1)
    print()

def chaos_print(duration=3):
    import random
    chars = "abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*()-_=+[]{}<>?"
    end_time = time.time() + duration
    while time.time() < end_time:
        line = ''.join(random.choice(chars) for _ in range(60))
        color = Fore.RED if random.random() < 0.5 else Fore.GREEN
        print(color + line)
        time.sleep(0.03)
    time.sleep(0.3)
    os.system("cls")

def spoof_level_loop():
    while True:
        slow_print_inline("[i] Do you want to spoof? (y/n) ", delay=0.05, color=Fore.BLUE)
        choice = input().strip().lower()

        if choice == "y":
            chaos_print()
            os.system("cls")
            try:
                width = os.get_terminal_size().columns
            except OSError:
                width = 80

            # 2. Zeile grün
            line2 = "[i] Successfully Spoofed"
            padding2 = (width - len(line2)) // 2
            print("\n" + " " * padding2 + Fore.GREEN + line2)

            # 3. Zeile weiß
            line3 = "please close manually"
            padding3 = (width - len(line3)) // 2
            print(" " * padding3 + Style.RESET_ALL + line3)

            # 4. Zeile leer
            print()

            # Kein input mehr, einfach stehen lassen
            while True:
                time.sleep(1)

        elif choice == "n":
            slow_print_inline("[-] Do you wanna close Snowy Temp? (y/n) ", delay=0.05, color=Fore.RED)
            close_choice = input().strip().lower()

            if close_choice == "y":
                sys.exit()
            else:
                continue
        else:
            continue

def main():
    os.system("chcp 65001 >nul")  # UTF-8 Codepage
    os.system("cls")
    make_console_transparent(alpha=200)
    disable_resize()

    print_banner()

    prompt = "[*] Enter a Licence Key: "
    slow_print_inline(prompt, delay=0.05, color=Fore.BLUE)
    key = input()

    if key.strip().lower() == "ds4y-02904":
        slow_print("[+] Licence Key valid", delay=0.05, color=Fore.GREEN)
        spoof_level_loop()
    else:
        slow_print("[-] Invalid Licence Key", delay=0.05, color=Fore.RED)
        countdown(5)
        sys.exit()

if __name__ == "__main__":
    main()
