import os
import platform
import time
import tkinter as tk
from tkinter import messagebox
import webbrowser

VERSION = "Nyrion v1.2.2"
LION_VERSION = "Lion Shell v0.1.6"

command_history = []

# ────── LOGO ────── #
def show_logo():
    logo = [
        "██        ██",
        "████      ██",    
        "██  ██    ██",
        "██    ██  ██",
        "██      ████",
        "██        ██",
        "██        ██"
    ]
    for line in logo:
        print(line)
    print(f"\nWelcome to {VERSION} - {LION_VERSION}")
    print("Type 'lion help' to begin.\n")

# ────── GUI LAUNCH ────── #
def launch_gui():
    os.system('cls' if os.name == 'nt' else 'clear')
    print("Launching Nyrion GUI...")
    time.sleep(1)

    gui_root = tk.Tk()
    gui_root.title("Nyrion Desktop")
    gui_root.geometry("1920x1080")
    gui_root.configure(bg="#1e1e1e")

    title = tk.Label(gui_root, text="Nyrion v1.2", font=("Consolas", 20), fg="white", bg="#1e1e1e")
    title.pack(pady=20)

    load_label = tk.Label(gui_root, text="Loading Nyrion...\n", font=("Consolas", 12), fg="white", bg="#1e1e1e")
    load_label.pack()

    n_logo = [
        "██        ██",
        "████      ██",    
        "██  ██    ██",
        "██    ██  ██",
        "██      ████",
        "██        ██",
        "██        ██"
    ]
    for line in n_logo:
        tk.Label(gui_root, text=line, fg="white", bg="#1e1e1e", font=("Courier", 10)).pack()

    # Button Panel
    frame = tk.Frame(gui_root, bg="#1e1e1e")
    frame.pack(pady=30)

    def show_specs():
        specs = f"""OS: {platform.system()} {platform.release()}
Processor: {platform.processor()}
Python: {platform.python_version()}"""
        messagebox.showinfo("Specs", specs)

    def open_web():
        webbrowser.open("https://www.google.com")

    def open_editor():
        editor = tk.Toplevel(gui_root)
        editor.title("Nyrion Script Editor")
        editor.geometry("600x400")
        text = tk.Text(editor, bg="black", fg="white", insertbackground='white')
        text.pack(expand=True, fill='both')

    tk.Button(frame, text="Specs", command=show_specs, width=12).grid(row=0, column=0, padx=10)
    tk.Button(frame, text="Web", command=open_web, width=12).grid(row=0, column=1, padx=10)
    tk.Button(frame, text="Editor", command=open_editor, width=12).grid(row=0, column=2, padx=10)
    tk.Button(frame, text="Exit", command=gui_root.destroy, width=12).grid(row=0, column=3, padx=10)

    gui_root.mainloop()

# ────── SHELL COMMANDS ────── #
def show_help():
    print("Available commands:\n")
    print("lion specs     - Show system specs")
    print("lion nyrver    - Show Nyrion version")
    print("lion base      - Show underlying OS")
    print("lion web       - Open the browser installed on base OS")
    print("lion gui       - Launch desktop GUI")
    print("lion script    - Open script editor")
    print("lion clear     - Clear the screen")
    print("lion history   - Show last 5 commands")
    print("lion exit      - Exit Nyrion")

def show_specs():
    print(f"System: {platform.system()} {platform.release()}")
    print(f"Processor: {platform.processor()}")
    print(f"Python Version: {platform.python_version()}")

def show_version():
    print(f"{VERSION}\n{LION_VERSION}")

def show_base():
    print(f"Underlying OS: {os.name} ({platform.system()})")

def launch_editor():
    print("Launching script editor...")
    time.sleep(1)
    try:
        os.system("notepad" if os.name == "nt" else "nano")
    except:
        print("Editor could not be opened.")

def open_web():
    print("Launching web browser...")
    webbrowser.open("https://www.google.com")

def show_history():
    print("Last 5 commands:")
    for cmd in command_history[-5:]:
        print("-", cmd)

# ────── MAIN LOOP ────── #
def main():
    show_logo()
    while True:
        try:
            command = input(">> ").strip().lower()
            if not command:
                continue

            command_history.append(command)

            if command == "lion help":
                show_help()
            elif command == "lion specs":
                show_specs()
            elif command == "lion nyrver":
                show_version()
            elif command == "lion base":
                show_base()
            elif command == "lion script":
                launch_editor()
            elif command == "lion web":
                open_web()
            elif command == "lion gui":
                launch_gui()
            elif command == "lion history":
                show_history()
            elif command == "lion clear":
                os.system("cls" if os.name == "nt" else "clear")
            elif command == "lion exit":
                print("Exiting Nyrion...")
                break
            else:
                print("Unknown command. Type 'lion help' for a list.")
        except KeyboardInterrupt:
            print("\nUse 'lion exit' to quit.")
        except Exception as e:
            print(f"Error: {e}")

# ────── RUN ────── #
if __name__ == "__main__":
    main()
