import os
import shutil
import sys
import getpass

# --- Simple User Database ---
USERS = {
    "admin": "admin123",
    "user": "password"
}

# --- Login System ---
def login():
    print("=== PyOS Login ===")
    for _ in range(3):
        username = input("Username: ")
        password = getpass.getpass("Password: ")
        if USERS.get(username) == password:
            print(f"Welcome, {username}!\n")
            return True
        else:
            print("Invalid credentials.\n")
    print("Too many failed attempts. Exiting.")
    return False

# --- Shell Commands ---
def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def list_dir(path='.'):
    for item in os.listdir(path):
        print(item)

def change_dir(path):
    try:
        os.chdir(path)
    except Exception as e:
        print(f"cd error: {e}")

def echo(text):
    print(text)

def make_dir(dirname):
    try:
        os.mkdir(dirname)
    except Exception as e:
        print(f"mkdir error: {e}")

def remove(path):
    try:
        if os.path.isdir(path):
            shutil.rmtree(path)
        else:
            os.remove(path)
    except Exception as e:
        print(f"rm error: {e}")

def show_help():
    print("""
Commands:
  ls                - list files
  cd <dir>          - change directory
  echo <text>       - print text
  mkdir <name>      - create folder
  rm <file|folder>  - remove file or folder
  rm /a             - delete system (/a directory)
  clear             - clear screen
  help              - show this message
  exit              - exit the shell
""")

# --- Fake Crash Function ---
def fake_crash():
    clear()
    print("CRITICAL ERROR: System file '/a' deleted!")
    print("PyOS has crashed. Kernel panic.\n")
    print("[ERROR CODE: 0xDEADDEAD]")
    print("Shutting down...")
    while True:
        pass  # infinite freeze to simulate crash

# --- Shell Loop ---
def shell():
    clear()
    print("Welcome to MyPyOS Shell! Type 'help' for commands.\n")
    while True:
        try:
            cmd = input(f"{os.getcwd()} myos> ").strip()
            if not cmd:
                continue
            parts = cmd.split()
            command = parts[0]
            args = parts[1:]

            # Fake crash trigger
            if command == "rm" and args and args[0] == "/a":
                fake_crash()
                return

            if command == "ls":
                list_dir()
            elif command == "cd":
                if args:
                    change_dir(args[0])
                else:
                    print("cd: missing argument")
            elif command == "echo":
                echo(" ".join(args))
            elif command == "mkdir":
                if args:
                    make_dir(args[0])
                else:
                    print("mkdir: missing name")
            elif command == "rm":
                if args:
                    remove(args[0])
                else:
                    print("rm: missing target")
            elif command == "clear":
                clear()
            elif command == "help":
                show_help()
            elif command == "exit":
                print("Exiting MyPyOS...")
                break
            else:
                print(f"Unknown command: {command}")
        except KeyboardInterrupt:
            print("\nUse 'exit' to quit.")
        except Exception as e:
            print(f"Error: {e}")

# --- Entry Point ---
def main():
    if login():
        shell()

if __name__ == "__main__":
    main()
