from colorama import Fore, Style, init
import os
import time
import shutil

# Initialize colorama
init(autoreset=True)

def cprint(text, color=Fore.WHITE, centered=True):
    """
    Prints text with color, centered in the terminal.
    """
    terminal_width = shutil.get_terminal_size().columns
    lines = text.splitlines()
    for line in lines:
        if centered:
            print(color + line.center(terminal_width))
        else:
            print(color + line) # For non-centered text within the border

def print_title():
    """
    Clears the screen and prints the stylish title banner.
    """
    os.system("cls" if os.name == "nt" else "clear")
    # A larger and more visible banner
    banner = """
  ╔══════════════════════════════════════════════════════════════════════════════════════════╗
  ║    ____  ____   _____   _____  ______ _____ ______ _____ _____ _______                   ║
  ║   / __ \\|  _ \\ / ____| |  __ \\|  ____/ ____| ____|  __ \\_   _|__   __|                  ║
  ║  | |  | | |_) | (___   | |__) | |__ | |  __| |__   | |  | || |    | |                   ║
  ║  | |  | |  _ < \\___ \\  |  _  /|  __|| | |_ |  __|  | |  | || |    | |                   ║
  ║  | |__| | |_) |____) | | | \\ \\| |___| |__| | |____ | |__| || |_   | |                   ║
  ║   \\____/|____/|_____/  |_|  \\_\\______\\_____|______||_____/_____|  |_|                   ║
  ╚══════════════════════════════════════════════════════════════════════════════════════════╝
    """
    cprint(banner, Fore.GREEN + Style.BRIGHT)
    cprint("--- Professional System Optimizer ---", Fore.YELLOW + Style.BRIGHT)
    cprint("Version 2.1 | Optimized for Low-End & High-End PCs", Fore.CYAN)
    print()

def main_menu():
    """
    Displays the main menu with a stylish border and handles user input.
    """
    while True:
        # Drawing a more prominent border for the menu
        cprint("╔═════════════════════════════════════════════════════════════════════════╗", Fore.CYAN)
        cprint("║                          MAIN MENU - Choose an option:                    ║", Fore.CYAN + Style.BRIGHT)
        cprint("╠═════════════════════════════════════════════════════════════════════════╣", Fore.CYAN)
        options = [
            "1.  Optimize CPU for Performance",
            "2.  Optimize RAM (Clear Standby)",
            "3.  Disk Cleanup",
            "4.  Defragment Drives (HDD only)",
            "5.  Flush DNS Cache",
            "6.  Reset Network",
            "7.  Disable Unused Services (Low-End)",
            "8.  Enable Recommended Services (High-End)",
            "9.  Check System Info",
            "10. Clean Temp & Junk Files",
            "11. Adjust Visual Effects (Low-End)",
            "12. Open Task Manager",
            "13. Open Device Manager",
            "14. Run SFC (System File Checker)",
            "15. Run DISM (System Repair)",
            "16. Exit"
        ]
        
        # Print each option inside the border
        for opt in options:
            print(Fore.YELLOW + f"║ {opt.ljust(70)} ║") # ljust pads the string to fit the border
        
        cprint("╚═════════════════════════════════════════════════════════════════════════╝", Fore.CYAN)
        print()
        
        choice = input(Fore.GREEN + "Enter your choice (1-16): ")
        actions = {
            "1": optimize_cpu,
            "2": optimize_ram,
            "3": disk_cleanup,
            "4": defrag_drives,
            "5": flush_dns,
            "6": reset_network,
            "7": disable_services_low_end,
            "8": enable_services_high_end,
            "9": show_system_info,
            "10": clean_temp_files,
            "11": adjust_visual_effects,
            "12": open_task_manager,
            "13": open_device_manager,
            "14": run_sfc,
            "15": run_dism,
            "16": exit_tool
        }
        action = actions.get(choice)
        if action:
            action()
        else:
            cprint("Invalid choice. Please try again.", Fore.RED)
            time.sleep(1)
            print_title()

# ---------- Function Implementations ----------
# The functions below remain the same as they were already functional.

def optimize_cpu():
    print_title()
    cprint("Optimizing CPU (Setting High Performance)...", Fore.YELLOW)
    os.system("powercfg /setactive SCHEME_MIN")  # High Performance Plan
    cprint("High Performance mode activated!", Fore.GREEN)
    input(Fore.CYAN + "\nPress Enter to return...")
    print_title()

def optimize_ram():
    print_title()
    cprint("Clearing Standby Memory (requires EmptyStandbyList.exe)...", Fore.YELLOW)
    if os.path.exists("EmptyStandbyList.exe"):
        os.system("EmptyStandbyList.exe workingsets")
        cprint("RAM Optimization Complete!", Fore.GREEN)
    else:
        cprint("Tool not found. Please place EmptyStandbyList.exe in this folder.", Fore.RED)
    input(Fore.CYAN + "\nPress Enter to return...")
    print_title()

def disk_cleanup():
    print_title()
    cprint("Running Disk Cleanup...", Fore.YELLOW)
    os.system("cleanmgr")
    input(Fore.CYAN + "\nPress Enter to return...")
    print_title()

def defrag_drives():
    print_title()
    cprint("Opening Defragmenter (Only for HDD)...", Fore.YELLOW)
    os.system("dfrgui")
    input(Fore.CYAN + "\nPress Enter to return...")
    print_title()

def flush_dns():
    print_title()
    cprint("Flushing DNS Cache...", Fore.YELLOW)
    os.system("ipconfig /flushdns")
    cprint("DNS cache flushed.", Fore.GREEN)
    input(Fore.CYAN + "\nPress Enter to return...")
    print_title()

def reset_network():
    print_title()
    cprint("Releasing and Renewing IP...", Fore.YELLOW)
    os.system("ipconfig /release && ipconfig /renew")
    cprint("Network Reset Complete.", Fore.GREEN)
    input(Fore.CYAN + "\nPress Enter to return...")
    print_title()

def disable_services_low_end():
    print_title()
    cprint("Disabling unnecessary services for low-end PCs...", Fore.YELLOW)
    services = ["SysMain", "Fax", "XblGameSave"]
    for service in services:
        os.system(f"sc stop {service} && sc config {service} start= disabled")
    cprint("Selected services disabled.", Fore.GREEN)
    input(Fore.CYAN + "\nPress Enter to return...")
    print_title()

def enable_services_high_end():
    print_title()
    cprint("Enabling recommended services for high-end PCs...", Fore.YELLOW)
    services = ["SysMain", "wuauserv"]
    for service in services:
        os.system(f"sc config {service} start= auto && sc start {service}")
    cprint("Services enabled.", Fore.GREEN)
    input(Fore.CYAN + "\nPress Enter to return...")
    print_title()

def show_system_info():
    print_title()
    os.system("systeminfo | more")
    input(Fore.CYAN + "\nPress Enter to return...")
    print_title()

def clean_temp_files():
    print_title()
    cprint("Cleaning Temp Files...", Fore.YELLOW)
    os.system('del /q /f /s "%TEMP%\\*" >nul 2>&1')
    os.system('del /q /f /s "C:\\Windows\\Temp\\*" >nul 2>&1')
    cprint("Temporary files cleaned!", Fore.GREEN)
    input(Fore.CYAN + "\nPress Enter to return...")
    print_title()

def adjust_visual_effects():
    print_title()
    cprint("Setting visual effects for best performance (Low-End)...", Fore.YELLOW)
    reg = 'reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\VisualEffects" /v VisualFXSetting /t REG_DWORD /d 2 /f'
    os.system(reg)
    cprint("Visual settings adjusted!", Fore.GREEN)
    input(Fore.CYAN + "\nPress Enter to return...")
    print_title()

def open_task_manager():
    print_title()
    os.system("start taskmgr")
    input(Fore.CYAN + "\nPress Enter to return...")
    print_title()

def open_device_manager():
    print_title()
    os.system("start devmgmt.msc")
    input(Fore.CYAN + "\nPress Enter to return...")
    print_title()

def run_sfc():
    print_title()
    cprint("Running System File Checker...", Fore.YELLOW)
    os.system("sfc /scannow")
    input(Fore.CYAN + "\nPress Enter to return...")
    print_title()

def run_dism():
    print_title()
    cprint("Running DISM Scan...", Fore.YELLOW)
    os.system("DISM /Online /Cleanup-Image /RestoreHealth")
    input(Fore.CYAN + "\nPress Enter to return...")
    print_title()

def exit_tool():
    print_title()
    cprint("Exiting System Optimizer. Goodbye!", Fore.RED)
    time.sleep(1)
    exit()

# Run the app
if __name__ == "__main__":
    print_title()
    main_menu()