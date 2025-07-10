import os
import ctypes
import time
from datetime import datetime

def is_admin():
    """Check if the program is running as administrator"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def set_custom_date():
    """Set system date to August 10, 2023"""
    try:
        # Set date (mm-dd-yyyy)
        os.system('date 08-10-2023')
        # Set time (hh:mm)
        os.system('time 12:00')
        print("\nDate successfully set to August 10, 2023 12:00 PM")
    except Exception as e:
        print(f"\nError setting date: {e}")

def restore_auto_date():
    """Restore automatic date/time synchronization"""
    try:
        # Start Windows Time service
        os.system('net start w32time > nul')
        # Force time resync
        os.system('w32tm /resync > nul')
        print("\nAutomatic date/time synchronization restored")
    except Exception as e:
        print(f"\nError restoring automatic date: {e}")

def display_menu(current_time):
    """Display the application menu"""
    os.system('cls')
    print("╔══════════════════════════════════════╗")
    print("║      WINDOWS DATE CHANGER v1.0      ║")
    print("╠══════════════════════════════════════╣")
    print("║ Options:                            ║")
    print("║  1. Set date to August 10, 2023     ║")
    print("║  2. Restore automatic date/time     ║")
    print("║  0. Exit                            ║")
    print("╠══════════════════════════════════════╣")
    print(f"║ Current system date: {current_time} ║")
    print("╚══════════════════════════════════════╝")
    print("\nNote: This application requires administrator privileges")

def main():
    if not is_admin():
        print("\nERROR: This program must be run as Administrator!")
        print("Right-click on the file and select 'Run as administrator'")
        input("Press Enter to exit...")
        return

    while True:
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        display_menu(current_time)
        
        choice = input("\nSelect option (1/2/0): ").strip()
        
        if choice == "1":
            set_custom_date()
        elif choice == "2":
            restore_auto_date()
        elif choice == "0":
            print("\nExiting program...")
            break
        else:
            print("\nInvalid choice! Please select 1, 2 or 0")
        
        time.sleep(2)  # Pause to show result

if __name__ == "__main__":
    main()