import os
import time
import socket
import uuid
import platform
import subprocess
from colorama import init, Fore
import requests

init(autoreset=True)

# --- ASCII Art ---
def print_ascii():
    print(Fore.MAGENTA + "       _____ __             _________            __")
    print(Fore.MAGENTA + "      / ___// /_____ ______/ ____/ (_)__  ____  / /_")
    print(Fore.MAGENTA + "      \\__ \\/ __/ __ `/ ___/ /   / / / _ \\/ __ \\/ __/")
    print(Fore.MAGENTA + "     ___/ / /_/ /_/ / /  / /___/ / /  __/ / / / /_  ")
    print(Fore.MAGENTA + "    /____/\\__\\/\\__,_/_/   \\____/_/_/\\___/_/ /_/\\__/  ")
    print()

# --- Typing effect ---
def type_output(text, delay=0.03):
    for char in text:
        print(char, end='', flush=True)
        time.sleep(delay)
    print()

# --- Device Info Functions ---
def get_device_name():
    return socket.gethostname()

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "Unavailable"

def get_public_ip():
    try:
        response = requests.get('https://api.ipify.org/?format=text', timeout=5)
        if response.status_code == 200:
            return response.text.strip()
        else:
            return "Unavailable"
    except:
        return "Unavailable"

def get_ipv6():
    try:
        for info in socket.getaddrinfo(socket.gethostname(), None):
            if info[0] == socket.AF_INET6:
                return info[4][0]
    except:
        return "Unavailable"
    return "Unavailable"

def get_hwid():
    try:
        if platform.system() == "Windows":
            output = subprocess.check_output("wmic csproduct get uuid", shell=True)
            return output.decode().splitlines()[1].strip()
        else:
            return hex(uuid.getnode())
    except Exception as e:
        return "Error retrieving HWID: " + str(e)

def get_os():
    return f"{platform.system()} {platform.release()} ({platform.version()})"

def get_cpu():
    try:
        if platform.system() == "Windows":
            output = subprocess.check_output("wmic cpu get name", shell=True)
            return output.decode().splitlines()[1].strip()
        else:
            return platform.processor()
    except Exception as e:
        return "Error retrieving CPU: " + str(e)

def get_gpu():
    try:
        if platform.system() == "Windows":
            output = subprocess.check_output("wmic path win32_VideoController get name", shell=True)
            lines = output.decode().splitlines()
            gpus = [line.strip() for line in lines if line.strip() and "Name" not in line]
            return ', '.join(gpus)
        else:
            return "GPU detection not supported on this OS"
    except:
        return "Unavailable"

# --- Script 1: Grab Device Info ---
def script_1():
    clear_screen()
    print_ascii()
    print(Fore.CYAN + "Grabbing device info:\n")
    type_output("Device Name: " + get_device_name())
    type_output("Local IP: " + get_local_ip())
    type_output("Public IP: " + get_public_ip())
    type_output("IPv6: " + get_ipv6())
    type_output("HWID: " + get_hwid())
    type_output("OS: " + get_os())
    type_output("CPU: " + get_cpu())
    type_output("GPU: " + get_gpu())
    input("\nPress Enter to return to the menu...")

# --- Helper to clear screen ---
def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

# --- Menu ---
def main():
    while True:
        clear_screen()
        print_ascii()
        type_output("\nChoose an option:")
        type_output("1. Grab Device Info")
        type_output("2. Keylogger")
        type_output("3. Password Grabber")
        type_output("4. PC Traffic")
        type_output("5. Execute Script 5")
        print(Fore.GREEN + "Type 'exit' to quit the program.")

        choice = input("Enter a number (1-5) or 'exit': ").strip()

        if choice == "1":
            script_1()
        elif choice in ["2", "3", "4", "5"]:
            clear_screen()
            print_ascii()
            type_output(Fore.CYAN + f"Executing script {choice} (Demo)...")
            input("\nPress Enter to return to the menu...")
        elif choice.lower() == "exit":
            clear_screen()
            type_output(Fore.RED + "Exiting StarClient Demo...")
            break
        else:
            print(Fore.LIGHTBLACK_EX + "Invalid choice. Please select 1-5 or 'exit'.")
            time.sleep(1.5)

if __name__ == "__main__":
    main()
