import subprocess
import os
import shutil
from colorama import Fore
import keyboard
import sys

try:
    os.system("clear")
except:
    os.system("cls")


def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")


keyboard.add_hotkey("ctrl+l", clear_screen)


def list_show(command):
    commands = {
        "ls": "dir",
        "ls -ltrh": "dir",
        "ls -a": ["dir", "/A"],
        "ls -R": ["dir", "/S"],
        "ls -u": ["dir", "/D"],
        "ls -l": ["dir", "/Q"],
        "ls -lh": ["dir", "/C"],
        "dir": "ls",
    }

    try:
        cmd = commands.get(command.strip())
        if cmd:
            subprocess.run(cmd, shell=True) if isinstance(cmd, str) else subprocess.run(cmd, shell=True)
        elif command in ["clear", "cls"]:
            clear_screen()
        else:
            print(Fore.RED + f"The command '{command}' is not supported.")
    except Exception as e:
        print(Fore.RED + f"An error occurred: {e}")


def change_directory(command):
    try:
        path = command.strip().split("cd ")[1] if command.startswith("cd ") else None
        os.chdir(path) if path else os.chdir("..")
    except Exception as e:
        print(Fore.RED + f"An error occurred: {e}")


def make_directory(command):
    try:
        folder_name = command.strip().split("mkdir ")[1]
        os.makedirs(folder_name, exist_ok=True)
        print(Fore.GREEN + f"Directory '{folder_name}' created successfully.")
    except Exception as e:
        print(Fore.RED + f"An error occurred: {e}")


def move(command):
    try:
        source, destination = command.strip().split()
        shutil.move(source, destination)
        print(Fore.GREEN + f"'{source}' moved to '{destination}' successfully.")
    except Exception as e:
        print(Fore.RED + f"An error occurred: {e}")


def copy(command):
    try:
        src, dest = command.strip().split()
        if os.path.isdir(src):
            shutil.copytree(src, dest, dirs_exist_ok=True)
        else:
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            shutil.copy(src, dest)
        print(Fore.GREEN + f"'{src}' copied to '{dest}' successfully.")
    except Exception as e:
        print(Fore.RED + f"An error occurred: {e}")


def remove(command):
    try:
        path = command.strip().split()
        if os.path.isdir(path):
            shutil.rmtree(path)
        else:
            os.remove(path)
        print(Fore.GREEN + f"'{path}' removed successfully.")
    except Exception as e:
        print(Fore.RED + f"An error occurred: {e}")


def whoami(command):
    try:
        if command in ["whoami", "uname", "uname -a"]:
            result = subprocess.run("whoami", shell=True, text=True, capture_output=True)
            print(Fore.GREEN + result.stdout.strip())
        else:
            print(Fore.RED + f"Invalid command '{command}'.")
    except Exception as e:
        print(Fore.RED + f"An error occurred: {e}")


def other(command):
    if command == "exit":
        print(Fore.RED + "EXIT")
        sys.exit()
    else:
        print(Fore.RED + f"Unknown command: {command}")


while True:
    username = os.getlogin() if hasattr(os, 'getlogin') else "USER"
    current_dir = os.getcwd()
    prompt = f"{Fore.LIGHTYELLOW_EX}{username}{Fore.LIGHTBLUE_EX} ┌─[{Fore.LIGHTRED_EX}{current_dir}{Fore.LIGHTBLUE_EX}] \n└──╼ {Fore.LIGHTRED_EX}# {Fore.WHITE}"

    link = input(prompt).strip()

    if link.startswith("cd "):
        change_directory(link)
    elif link.startswith("mkdir "):
        make_directory(link)
    elif link.startswith("mv "):
        move(link)
    elif link.startswith("cp "):
        copy(link)
    elif link.startswith("rm "):
        remove(link)
    elif link in ["ls", "ls -a", "ls -R", "ls -u", "ls -l", "ls -lh", "dir", "clear", "cls"]:
        list_show(link)
    elif link in ["whoami", "uname", "uname -a"]:
        whoami(link)
    else:
        other(link)
