import os
import sys
import subprocess


def clear_screen():
    """Clears the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_section_header(title):
    """Prints a formatted header for a section."""
    print(f"\n\033[33m{title}\033[0m")

########################################################
def dxdiag():
    try:
        subprocess.run(["dxdiag"], check=True, shell=True)
        print("Successfully executed 'dxdiag'.")
    except subprocess.CalledProcessError as e:
        print(f"Error executing 'dxdiag': {e}")
    except FileNotFoundError:
        print("Error: 'dxdiag' command not found.")
        
def device_manager():
    try:
        subprocess.run(["devmgmt.msc"], check=True, shell=True)
        print("Successfully executed 'sdevmgmt.msc'.")
    except subprocess.CalledProcessError as e:
        print(f"Error executing 'devmgmt.msc': {e}")
    except FileNotFoundError:
        print("Error: 'devmgmt.msc' command not found.")
        
def services():
    try:
        subprocess.run(["services.msc"], check=True, shell=True)
        print("Successfully executed 'services.msc'.")
    except subprocess.CalledProcessError as e:
        print(f"Error executing 'services.msc': {e}")
    except FileNotFoundError:
        print("Error: 'services.msc' command not found.")

def system_configuration():
    try:
        subprocess.run(["msconfig"], check=True, shell=True)
        print("Successfully executed 'msconfig'.")
    except subprocess.CalledProcessError as e:
        print(f"Error executing 'msconfig': {e}")
    except FileNotFoundError:
        print("Error: 'msconfig' command not found.")

def windows_tools():
    while True:
        clear_screen()
        print_section_header("--- System Utilities & Settings ---")
        print("[1] System Configuration")
        print("[2] Services")
        print("[3] Device Manager")
        print("[4] DirectX Diagnostic Tool")
        print("[5] Back to Main")

        choice = input("Enter choice 1|2|3|4|5: ").strip()

        if choice == '1':
            system_configuration()
        elif choice == '2':
            services()
        elif choice == '3':
            device_manager()
        elif choice == '4':
            dxdiag()
        elif choice == '5':
            break
        else:
            input("\033[91mInvalid input, Press Enter to try again...\033[0m")

########################################################


def task_manager():
    try:
        subprocess.run(["taskmgr"], check=True, shell=True)
        print("Successfully executed 'taskmgr'")
    except subprocess.CalledProcessError as e:
        print(f"Error executing 'taskmgr': {e}")
    except FileNotFoundError:
        print("Error: 'taskmgr' command not found.")

def msinfo32():
    try:
        subprocess.run(["msinfo32"], check=True, shell=True)
        print("Successfully executed 'msinfo32'.")
    except subprocess.CalledProcessError as e:
        print(f"Error executing 'msinfo32': {e}")
    except FileNotFoundError:
        print("Error: 'msinfo32' command not found.")

def winver():
    """
    Executes 'winver' command using the 'windows + r' equivalent in Python.
    """
    try:
        subprocess.run(["winver"], check=True, shell=True)
        print("Successfully executed 'winver'.")
    except subprocess.CalledProcessError as e:
        print(f"Error executing 'winver': {e}")
    except FileNotFoundError:
        print("Error: 'winver' command not found.")

def windows_information():
    while True:
        clear_screen()
        print_section_header("-- Windows Information --")
        print("[1] About Windows")
        print("[2] System Information")
        print("[3] Task Manager")
        print("[4] Back to Main")

        choice = input("Enter choice 1|2|3|4: ").strip()

        if choice == '1':
            winver()
        elif choice == '2':
            msinfo32()
        elif choice == '3':
            task_manager()
        elif choice == '4':
            break
        else:
            input("\033[91mInvalid input, Press Enter to try again...\033[0m")

########################################################       
def main():
    while True:
        clear_screen()
        print_section_header("[BASIC WINDOWS COMMAND by PH-Z]")
        print("[1] Windows Information")
        print("[2] Windows Tools")
        print("[3] Exit")

        choice = input("Enter choice 1|2|3: ").strip()

        if choice == '1':
            windows_information()
        elif choice == '2':
            windows_tools()
        elif choice == '3':
            clear_screen()
            print("[PH-Z] Exiting the program. Goodbye!")
            sys.exit()
        else:
            input("\033[91mInvalid input, Press Enter to try again...\033[0m")
            
if __name__ == "__main__":
    main()

