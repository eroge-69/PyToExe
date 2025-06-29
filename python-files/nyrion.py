import os
import sys
import time
import platform
import socket
import shutil
import random

import os
import sys
import time
import platform
import socket
import shutil
import random

# Block Windows 8.1 and older
import ctypes

def is_supported_windows():
    try:
        build_number = int(platform.version().split('.')[2])
        return build_number >= 10240  # Windows 10 = 10240+
    except (IndexError, ValueError):
        return False

def block_unsupported_os():
    if not is_supported_windows():
        ctypes.windll.user32.MessageBoxW(
            0,
            "❌ Nyrion no longer supports Windows 8.1 or older.\nSupport was dropped on October 10th, 2025.\nPlease upgrade to Windows 10 or later.",
            "Unsupported Operating System",
            0x10  # MB_ICONERROR
        )
        sys.exit()

block_unsupported_os()


# For colored output (Windows may need colorama installed)
try:
    from colorama import init, Fore, Style
    init()
except ImportError:
    class Fore:
        RED = ''
        GREEN = ''
        CYAN = ''
        YELLOW = ''
        RESET = ''
    class Style:
        BRIGHT = ''
        RESET_ALL = ''

NYRION_VERSION = "1.1"
command_history = []

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def loading_screen():
    clear_screen()
    print("Loading Nyrion " + NYRION_VERSION)
    for i in range(21):
        bar = '█' * i + '-' * (20 - i)
        print(f"[{bar}]", end='\r')
        time.sleep(0.05)
    print()

def show_help():
    print(Fore.CYAN + "Available lion commands:" + Fore.RESET)
    print(" lion help          - Show this help")
    print(" lion time          - Show current time")
    print(" lion date          - Show current date")
    print(" lion cls           - Clear screen")
    print(" lion dir           - List directory files")
    print(" lion cd <dir>      - Change directory")
    print(" lion type <file>   - Display file contents")
    print(" lion copy <src> <dst> - Copy file")
    print(" lion move <src> <dst> - Move file")
    print(" lion del <file>    - Delete file")
    print(" lion ren <old> <new>  - Rename file")
    print(" lion mkdir <dir>   - Make directory")
    print(" lion rmdir <dir>   - Remove directory")
    print(" lion echo <text>   - Print text")
    print(" lion pause         - Pause for keypress")
    print(" lion calc          - Calculator")
    print(" lion specs         - Show system specs")
    print(" lion nyrver        - Show Nyrion version")
    print(" lion base          - Show underlying OS")
    print(" lion script        - Simple script editor")
    print(" lion wmip          - Show IP address")
    print(" lion find <file>   - Find file")
    print(" lion edit <file>   - Edit a text file")
    print(" lion sysinfo       - Show system info")
    print(" lion history       - Last 5 commands")
    print(" lion joke          - Tell a joke")
    print(" lion crash         - Crash red screen")
    print(" lion reboot        - Restart shell")
    print(" lion exit          - Exit shell")

def show_time():
    print(time.strftime("%a %b %d %H:%M:%S %Y"))

def show_date():
    print(time.strftime("%Y-%m-%d"))

def list_dir():
    try:
        for f in os.listdir('.'):
            if os.path.isdir(f):
                print(Fore.CYAN + f + "\\" + Fore.RESET)
            else:
                print(f)
    except Exception as e:
        print(f"Error listing directory: {e}")

def change_dir(path):
    try:
        os.chdir(path)
    except Exception as e:
        print(f"Bad command or filename: {e}")

def type_file(filename):
    try:
        with open(filename, 'r') as f:
            print(f.read())
    except Exception as e:
        print(f"File not found: {e}")

def copy_file(src, dst):
    try:
        shutil.copy2(src, dst)
        print("1 file(s) copied.")
    except Exception as e:
        print(f"Cannot copy file: {e}")

def move_file(src, dst):
    try:
        shutil.move(src, dst)
        print("1 file(s) moved.")
    except Exception as e:
        print(f"Cannot move file: {e}")

def delete_file(filename):
    try:
        os.remove(filename)
        print(f"{filename} deleted.")
    except Exception as e:
        print(f"Cannot delete file: {e}")

def rename_file(old, new):
    try:
        os.rename(old, new)
        print(f"Renamed from {old} to {new}.")
    except Exception as e:
        print(f"Cannot rename file: {e}")

def mkdir(dirname):
    try:
        os.mkdir(dirname)
        print(f"Directory created: {dirname}")
    except Exception as e:
        print(f"Cannot create directory: {e}")

def rmdir(dirname):
    try:
        os.rmdir(dirname)
        print(f"Directory removed: {dirname}")
    except Exception as e:
        print(f"Cannot remove directory: {e}")

def echo_command(args):
    print(' '.join(args))

def pause():
    input("Press Enter to continue...")

def calculator():
    print("Calculator started. Type 'exit' to quit.")
    while True:
        expr = input("calc> ")
        if expr.lower() in ('exit', 'quit'):
            break
        try:
            # Safe eval: allow digits and operators only
            allowed = "0123456789+-*/(). "
            if all(c in allowed for c in expr):
                print(eval(expr))
            else:
                print("Invalid characters in expression.")
        except Exception as e:
            print(f"Error: {e}")

def lion_specs():
    print("System Specs:")
    print(f" System: {platform.system()}")
    print(f" Node Name: {platform.node()}")
    print(f" Release: {platform.release()}")
    print(f" Version: {platform.version()}")
    print(f" Machine: {platform.machine()}")
    print(f" Processor: {platform.processor()}")

def lion_nyrver():
    print(f"Nyrion Version {NYRION_VERSION}")

def lion_base():
    print(f"Underlying OS: {platform.system()} {platform.release()}")

def lion_script():
    print("Script editor (type 'run' to execute, 'exit' to quit)")
    script_lines = []
    while True:
        line = input("script> ")
        if line.lower() == 'exit':
            break
        elif line.lower() == 'run':
            for cmd in script_lines:
                execute_command("lion " + cmd, echo=False)
            script_lines.clear()
        else:
            script_lines.append(line)

def lion_wmip():
    try:
        hostname = socket.gethostname()
        ip = socket.gethostbyname(hostname)
        print(f"IP Address: {ip}")
    except Exception as e:
        print(f"Cannot get IP address: {e}")

def lion_find(filename):
    found = []
    for root, dirs, files in os.walk('.'):
        if filename in files:
            found.append(os.path.join(root, filename))
    if found:
        print(f"Found {len(found)} file(s):")
        for f in found:
            print(f)
    else:
        print("File not found.")

def lion_edit(filename):
    print(f"Editing {filename}. Type 'SAVE' alone on a line to save and exit.")
    lines = []
    if os.path.exists(filename):
        with open(filename) as f:
            lines = f.read().splitlines()
        print("\n".join(lines))
    else:
        print("New file.")

    new_lines = []
    while True:
        line = input()
        if line.strip().upper() == "SAVE":
            break
        new_lines.append(line)
    try:
        with open(filename, 'w') as f:
            f.write('\n'.join(new_lines))
        print(f"{filename} saved.")
    except Exception as e:
        print(f"Failed to save file: {e}")

def lion_sysinfo():
    print("System Info:")
    print(f" System: {platform.system()} {platform.release()} ({platform.version()})")
    print(f" Machine: {platform.machine()}")
    print(f" Processor: {platform.processor()}")
    print(f" Python Version: {platform.python_version()}")

def lion_history():
    print("Last 5 Commands:")
    for cmd in command_history[-5:]:
        print(cmd)

def lion_joke():
    jokes = [
        "Why do programmers prefer dark mode? Because light attracts bugs!",
        "Why do Java developers wear glasses? Because they don't C#!",
        "A SQL query walks into a bar, walks up to two tables and asks, 'Can I join you?'",
        "There are only 10 types of people in the world: those who understand binary, and those who don't.",
        "Debugging: Being the detective in a crime movie where you are also the murderer."
    ]
    print(random.choice(jokes))

def lion_crash():
    clear_screen()
    print(Fore.RED + Style.BRIGHT)
    print("\n\nNYRION RED SCREEN OF DEATH\n\n")
    print("A fatal error occurred. The system will restart shortly.")
    print(Style.RESET_ALL + Fore.RESET)
    time.sleep(3)
    main()

def lion_reboot():
    print("Rebooting Nyrion...")
    time.sleep(1)
    main()

def execute_command(cmd, echo=True):
    global command_history
    if echo:
        print(cmd)

    command_history.append(cmd)
    if len(command_history) > 100:
        command_history.pop(0)

    parts = cmd.strip().split()
    if len(parts) < 2:
        print("Command must start with 'lion' and have a subcommand.")
        return
    if parts[0].lower() != 'lion':
        print("Commands must start with 'lion'")
        return

    command = parts[1].lower()
    args = parts[2:]

    try:
        if command == 'help':
            show_help()
        elif command == 'time':
            show_time()
        elif command == 'date':
            show_date()
        elif command == 'cls':
            clear_screen()
        elif command == 'dir':
            list_dir()
        elif command == 'cd':
            if args:
                change_dir(args[0])
            else:
                print("Missing directory.")
        elif command == 'type':
            if args:
                type_file(args[0])
            else:
                print("Missing filename.")
        elif command == 'copy':
            if len(args) == 2:
                copy_file(args[0], args[1])
            else:
                print("Syntax: lion copy <src> <dst>")
        elif command == 'move':
            if len(args) == 2:
                move_file(args[0], args[1])
            else:
                print("Syntax: lion move <src> <dst>")
        elif command == 'del':
            if args:
                delete_file(args[0])
            else:
                print("Missing filename.")
        elif command == 'ren':
            if len(args) == 2:
                rename_file(args[0], args[1])
            else:
                print("Syntax: lion ren <old> <new>")
        elif command == 'mkdir':
            if args:
                mkdir(args[0])
            else:
                print("Missing directory name.")
        elif command == 'rmdir':
            if args:
                rmdir(args[0])
            else:
                print("Missing directory name.")
        elif command == 'echo':
            echo_command(args)
        elif command == 'pause':
            pause()
        elif command == 'calc':
            calculator()
        elif command == 'specs':
            lion_specs()
        elif command == 'nyrver':
            lion_nyrver()
        elif command == 'base':
            lion_base()
        elif command == 'script':
            lion_script()
        elif command == 'wmip':
            lion_wmip()
        elif command == 'find':
            if args:
                lion_find(args[0])
            else:
                print("Missing filename.")
        elif command == 'edit':
            if args:
                lion_edit(args[0])
            else:
                print("Missing filename.")
        elif command == 'sysinfo':
            lion_sysinfo()
        elif command == 'history':
            lion_history()
        elif command == 'joke':
            lion_joke()
        elif command == 'crash':
            lion_crash()
        elif command == 'reboot':
            lion_reboot()
        elif command == 'exit':
            print("Exiting Nyrion shell...")
            sys.exit(0)
        else:
            print(f"'{command}' is not recognized as a lion command.")
    except Exception as e:
        print(f"Error executing command: {e}")

def main():
    loading_screen()
    while True:
        try:
            cwd = os.getcwd()
            inp = input(f"{Fore.GREEN}Nyrion:{cwd}> {Fore.RESET}").strip()
            if not inp:
                continue
            execute_command(inp)
        except KeyboardInterrupt:
            print("\nUse 'lion exit' to quit.")
        except Exception as e:
            print(f"Unexpected error: {e}")

if __name__ == "__main__":
    main()
