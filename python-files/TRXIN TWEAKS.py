import os
import sys
import ctypes
import subprocess
import time
from colorama import init, Fore

# Initialize colorama
init()

# Constants for colors
W = Fore.WHITE
P = Fore.MAGENTA
R = Fore.RESET


# Define Windows types structure
class RECT(ctypes.Structure):
    _fields_ = [
        ('left', ctypes.c_long),
        ('top', ctypes.c_long),
        ('right', ctypes.c_long),
        ('bottom', ctypes.c_long)
    ]


# Window management functions
def set_window_properties():
    try:
        # Get console window handle
        hwnd = ctypes.windll.kernel32.GetConsoleWindow()

        # Set window transparency
        WS_EX_LAYERED = 0x00080000
        LWA_ALPHA = 0x00000002
        ctypes.windll.user32.SetWindowLongA(hwnd, -20, WS_EX_LAYERED)
        ctypes.windll.user32.SetLayeredWindowAttributes(hwnd, 0, 200, LWA_ALPHA)

        # Center window
        rect = RECT()
        ctypes.windll.user32.GetWindowRect(hwnd, ctypes.byref(rect))
        width = rect.right - rect.left
        height = rect.bottom - rect.top

        screen_width = ctypes.windll.user32.GetSystemMetrics(0)
        screen_height = ctypes.windll.user32.GetSystemMetrics(1)

        x = (screen_width - width) // 2
        y = (screen_height - height) // 2

        SWP_NOSIZE = 0x0001
        ctypes.windll.user32.SetWindowPos(hwnd, 0, x, y, 0, 0, SWP_NOSIZE)

        # Set window title
        ctypes.windll.kernel32.SetConsoleTitleW("Performance Tweaker")
    except Exception as e:
        print(f"Window adjustment error: {str(e)}")


# Admin check
def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


if not is_admin():
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
    sys.exit()


def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')


def print_header(title):
    clear_screen()
    print(f"\n{P}╔{'═' * (len(title) + 2)}╗")
    print(f"║ {W}{title}{P} ║")
    print(f"╚{'═' * (len(title) + 2)}╝{R}\n")


def print_menu(options):
    for i, option in enumerate(options, 1):
        print(f" {W}[{P}{i}{W}] {option}")
    print()


def press_enter():
    input(f"\n{W}Press Enter to continue...{R}")


def create_restore_point(description):
    try:
        print(f"\n{W}Creating restore point...{R}")
        animation = "|/-\\"
        for i in range(15):
            time.sleep(0.1)
            sys.stdout.write(f"\r{animation[i % len(animation)]}")
            sys.stdout.flush()

        result = subprocess.run(
            f'powershell Checkpoint-Computer -Description "{description}" -RestorePointType "MODIFY_SETTINGS"',
            shell=True,
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            print(f"\r{W}✓ Restore point created{R}")
        else:
            print(f"\r{W}⚠ Failed to create restore point{R}")
    except Exception as e:
        print(f"\r{W}⚠ Error creating restore point: {str(e)}{R}")


def system_optimizations():
    print_header("SYSTEM OPTIMIZATIONS")

    options = [
        "Optimize Visual Effects",
        "Disable Search Indexing",
        "Optimize Memory",
        "Disable Telemetry",
        "Back to Main Menu"
    ]

    print_menu(options)

    choice = input(f"{W}Select optimization: {R}")

    if choice == '1':
        create_restore_point("Visual Effects Optimization")
        subprocess.run(
            'reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\VisualEffects" /v "VisualFXSetting" /t REG_DWORD /d "2" /f',
            shell=True)
        print(f"\n{W}Visual effects optimized{R}")
        press_enter()
    elif choice == '2':
        create_restore_point("Disable Search Indexing")
        subprocess.run('sc config "WSearch" start= disabled', shell=True)
        print(f"\n{W}Search indexing disabled{R}")
        press_enter()
    elif choice == '3':
        create_restore_point("Memory Optimization")
        subprocess.run(
            'reg add "HKLM\\SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Memory Management" /v "DisablePagingExecutive" /t REG_DWORD /d "1" /f',
            shell=True)
        print(f"\n{W}Memory management optimized{R}")
        press_enter()
    elif choice == '4':
        create_restore_point("Disable Telemetry")
        subprocess.run('sc config "DiagTrack" start= disabled', shell=True)
        print(f"\n{W}Telemetry services disabled{R}")
        press_enter()


def complete_optimization():
    print_header("COMPLETE OPTIMIZATION")

    print(f"{W}This will apply all optimizations{R}")
    if input(f"\n{W}Continue? (y/n): {R}").lower() != 'y':
        return

    create_restore_point("Complete Optimization")

    optimizations = [
        ("Visual Effects",
         'reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\VisualEffects" /v "VisualFXSetting" /t REG_DWORD /d "2" /f'),
        ("Power Plan", 'powercfg /setactive 8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c'),
        ("Memory",
         'reg add "HKLM\\SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Memory Management" /v "DisablePagingExecutive" /t REG_DWORD /d "1" /f'),
        ("Telemetry", 'sc config "DiagTrack" start= disabled')
    ]

    for name, cmd in optimizations:
        print(f"{W}Applying {name}...{R}", end='\r')
        subprocess.run(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(f"{W}✓ {name} applied{R}")

    print(f"\n{W}All optimizations completed{R}")
    if input(f"{W}Reboot now? (y/n): {R}").lower() == 'y':
        subprocess.run('shutdown /r /t 5', shell=True)


def system_info():
    print_header("SYSTEM INFORMATION")

    print(f"{W}Operating System:{R}")
    subprocess.run('systeminfo | findstr /C:"OS Name" /C:"OS Version"', shell=True)

    print(f"\n{W}Processor:{R}")
    subprocess.run('wmic cpu get Name /format:list | findstr Name=', shell=True)

    print(f"\n{W}Memory:{R}")
    subprocess.run('systeminfo | findstr /C:"Total Physical Memory"', shell=True)

    press_enter()


def power_settings():
    print_header("POWER SETTINGS")
    print("Power settings options would be here")
    press_enter()


def mouse_keyboard_tweaks():
    print_header("MOUSE/KEYBOARD TWEAKS")
    print("Mouse/keyboard options would be here")
    press_enter()


def gpu_optimizations():
    print_header("GPU OPTIMIZATIONS")
    print("GPU optimization options would be here")
    press_enter()


def main_menu():
    set_window_properties()

    while True:
        print_header("PERFORMANCE TWEAKER")

        options = [
            "System Optimizations",
            "Power Settings",
            "Mouse/Keyboard Tweaks",
            "GPU Optimizations",
            "Create Restore Point",
            "Complete Optimization",
            "System Information",
            "Exit"
        ]

        print_menu(options)

        choice = input(f"{W}Select an option: {R}")

        if choice == '1':
            system_optimizations()
        elif choice == '2':
            power_settings()
        elif choice == '3':
            mouse_keyboard_tweaks()
        elif choice == '4':
            gpu_optimizations()
        elif choice == '5':
            create_restore_point("Manual Restore Point")
            press_enter()
        elif choice == '6':
            complete_optimization()
        elif choice == '7':
            system_info()
        elif choice == '8':
            sys.exit()


if __name__ == "__main__":
    main_menu()