# nixware_cli.py
# Console demo menu for Windows CMD. Safe demonstration only — does NOT perform injections.

import sys, time, shutil

ASCII_ART = r"""
   
███╗░░██╗██╗██╗░░██╗  ░██╗░░░░░░░██╗░█████╗░██████╗░███████╗  ░█████╗░██████╗░░█████╗░░█████╗░██╗░░██╗
████╗░██║██║╚██╗██╔╝  ░██║░░██╗░░██║██╔══██╗██╔══██╗██╔════╝  ██╔══██╗██╔══██╗██╔══██╗██╔══██╗██║░██╔╝
██╔██╗██║██║░╚███╔╝░  ░╚██╗████╗██╔╝███████║██████╔╝█████╗░░  ██║░░╚═╝██████╔╝███████║██║░░╚═╝█████═╝░
██║╚████║██║░██╔██╗░  ░░████╔═████║░██╔══██║██╔══██╗██╔══╝░░  ██║░░██╗██╔══██╗██╔══██║██║░░██╗██╔═██╗░
██║░╚███║██║██╔╝╚██╗  ░░╚██╔╝░╚██╔╝░██║░░██║██║░░██║███████╗  ╚█████╔╝██║░░██║██║░░██║╚█████╔╝██║░╚██╗
╚═╝░░╚══╝╚═╝╚═╝░░╚═╝  ░░░╚═╝░░░╚═╝░░╚═╝░░╚═╝╚═╝░░╚═╝╚══════╝  ░╚════╝░╚═╝░░╚═╝╚═╝░░╚═╝░╚════╝░╚═╝░░╚═╝         

                                            
    N I X W A R E   - BY @cheatssoldout
"""

TELEGRAM_LINK = "https://t.me/cheatssoldout"

def cls():
    # cross-platform clear for convenience; on Windows this will clear CMD
    os_name = sys.platform
    if os_name.startswith("win"):
        import os; os.system('cls')
    else:
        import os; os.system('clear')

def print_menu():
    cols = shutil.get_terminal_size((80,20)).columns
    print(ASCII_ART)
    print("-" * min(cols, 80))
    print("1) Start injecting NixWare")
    print("2) Close Menu")
    print("3) Restart NixWare")
    print("-" * min(cols, 80))
    print("Channel Creators:", TELEGRAM_LINK)
    print()

def simulate_progress(label="Processing", duration=3.0):
    # simple textual progress bar lasting approximately 'duration' seconds
    steps = 40
    delay = duration / steps
    for i in range(steps + 1):
        bar = "#" * i + "-" * (steps - i)
        pct = int(i / steps * 100)
        print(f"\r{label}: [{bar}] {pct}%", end="", flush=True)
        time.sleep(delay)
    print()  # newline at end

def main():
    while True:
        cls()
        print_menu()
        try:
            choice = input("Select option (1-3): ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting...")
            break

        if choice == "1":
            print("\n[!] Succesfull. Внимание наши разработчики не несут ответсвенноти за VAC-БАН НА ВАШЕМ АККАУНТЕ!.")
            simulate_progress("Starting (demo)", duration=4.0)
            print("Starting завершена. Нажмите Enter, чтобы продолжить...")
            input()
        elif choice == "2":
            print("\nClosing menu...")
            time.sleep(0.6)
            break
        elif choice == "3":
            print("\nRestarting (demo)...")
            simulate_progress("Restarting", duration=2.5)
            print("Перезапуск завершён. Нажмите Enter, чтобы вернуться в меню...")
            input()
        else:
            print("\nНеверный ввод. Нажмите Enter и попробуйте снова...")
            input()

if __name__ == "__main__":
    main()
