import tkinter as tk
import threading
import os
import socket
import winSecurity  # Your Flask app
import esp
import requests
import aob 
import keyauth
CONFIG_FILE = os.path.join(os.environ.get("ProgramFiles", "C:\\Program Files"), "Common Files", "config.txt")

def check_port_free(port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.bind(('0.0.0.0', port))
        s.close()
        return True
    except OSError:
        return False

def start_flask(port):
    try:
        winSecurity.run_flask(port)
    except Exception:
        pass  # Silently ignore errors or add UI error if you want

def save_port_and_start():
    port_input = port_entry.get()
    if not port_input.isdigit():
        return
    port = int(port_input)
    if not (1024 <= port <= 65535):
        return
    if not check_port_free(port):
        return
    with open(CONFIG_FILE, "w") as f:
        f.write(str(port))
    flask_thread = threading.Thread(target=start_flask, args=(port,))
    flask_thread.start()
    root.destroy()

def first_time_gui():
    global port_entry, root
    root = tk.Tk()
    root.title("LITEX X CHEATS")
    root.geometry("400x200")
    root.configure(bg="#1e1e1e")
    root.resizable(False, False)

    label_style = {'font': ('Segoe UI', 14, 'bold'), 'fg': '#ffffff', 'bg': '#1e1e1e'}
    entry_style = {'font': ('Segoe UI', 12), 'bg': '#2d2d2d', 'fg': '#ffffff', 'insertbackground': 'white'}
    button_style = {'font': ('Segoe UI', 12), 'bg': '#007acc', 'fg': 'white', 'activebackground': '#005a9e'}

    tk.Label(root, text="🔥LITEX CHEATS", **label_style).pack(pady=15)
    tk.Label(root, text="Enter Secret Number:", **label_style).pack()
    port_entry = tk.Entry(root, justify='center', **entry_style)
    port_entry.pack(ipady=4, pady=10, ipadx=10)

    start_button = tk.Button(root, text="🚀 Start", command=save_port_and_start, **button_style)
    start_button.pack(pady=10, ipadx=5, ipady=2)

    root.mainloop()

def main():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            try:
                port = int(f.read().strip())
            except Exception:
                port = None

        if port and check_port_free(port):
            start_flask(port)
        else:
            first_time_gui()
    else:
        first_time_gui()

if __name__ == '__main__':
    main()
