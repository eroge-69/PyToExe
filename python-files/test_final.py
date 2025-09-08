import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import os
import signal
import random
import threading

# --- Dark Color Themes ---
COLOR_THEMES = {
    "Cyber Green": {
        "bg_color": "#0f111a",
        "fg_color": "#a2d729",
        "entry_bg": "#1c1f2a",
        "button_bg": "#2d742d",
        "button_hover": "#4caf50",
        "highlight_color": "#7acc31",
        "log_bg": "#121924",
        "progress_bg": "#213125"
    },
    "Neon Blue": {
        "bg_color": "#0a0f28",
        "fg_color": "#3fc9f0",
        "entry_bg": "#182945",
        "button_bg": "#215179",
        "button_hover": "#42a5ff",
        "highlight_color": "#60cff8",
        "log_bg": "#1a2a4d",
        "progress_bg": "#183354"
    },
    "Dark Slate": {
        "bg_color": "#12181b",
        "fg_color": "#7fc0c1",
        "entry_bg": "#1e2a2b",
        "button_bg": "#3c5c5d",
        "button_hover": "#5ea6a7",
        "highlight_color": "#95c8c9",
        "log_bg": "#182224",
        "progress_bg": "#243435"
    }
}

current_theme = "Cyber Green"

def apply_theme(root, style, theme_name):
    theme = COLOR_THEMES[theme_name]
    root.configure(bg=theme["bg_color"])
    style.configure('TLabel',
                    background=theme["bg_color"],
                    foreground=theme["fg_color"],
                    font=('Consolas', 13, 'bold'))
    style.configure('Header.TLabel',
                    background=theme["bg_color"],
                    foreground=theme["highlight_color"],
                    font=('Consolas', 20, 'bold'))
    style.configure('TButton',
                    font=('Consolas', 12, 'bold'),
                    foreground='#000000',
                    background=theme["button_bg"],
                    borderwidth=1,
                    focusthickness=3,
                    focuscolor=theme["highlight_color"],
                    padding=10)
    style.map('TButton',
              background=[('active', theme["button_hover"])],
              foreground=[('active', '#000000')])
    style.configure('TEntry',
                    fieldbackground=theme["entry_bg"],
                    foreground=theme["fg_color"],
                    insertcolor=theme["highlight_color"],
                    font=('Consolas', 12),
                    bordercolor=theme["highlight_color"],
                    borderwidth=2)
    style.configure('Horizontal.TProgressbar',
                    troughcolor=theme["progress_bg"],
                    bordercolor=theme["button_bg"],
                    background=theme["button_hover"],
                    thickness=22)

def update_colors_widgets(theme):
    process_listbox.config(bg=theme["entry_bg"], fg=theme["fg_color"],
                           selectbackground=theme["button_hover"],
                           selectforeground=theme["bg_color"],
                           font=('Consolas', 12))
    results_text.config(background=theme["log_bg"], fg=theme["fg_color"],
                        insertbackground=theme["highlight_color"], font=('Consolas', 12))
    scan_window.config(bg=theme["bg_color"])
    status_label.config(background=theme["bg_color"], font=('Consolas', 14, 'bold'))
    theme_selector.config(bg=theme["entry_bg"], fg=theme["fg_color"],
                          font=('Consolas', 12))

def change_theme(new_theme):
    global current_theme
    current_theme = new_theme
    apply_theme(scan_window, scan_style, current_theme)
    update_colors_widgets(COLOR_THEMES[current_theme])

def list_suspicious_processes():
    suspicious = []
    try:
        if os.name == 'nt':
            output = subprocess.check_output('tasklist', shell=True).decode()
            for line in output.splitlines():
                if 'keylog' in line.lower():
                    cols = line.split()
                    if len(cols) > 1 and cols[1].isdigit():
                        suspicious.append((int(cols[1]), cols[0]))
        else:
            output = subprocess.check_output(['ps', '-A'], shell=False).decode()
            for line in output.splitlines():
                if 'keylog' in line.lower():
                    cols = line.split()
                    if cols and cols[0].isdigit():
                        suspicious.append((int(cols[0]), cols[-1]))
    except Exception as e:
        print(f"Process scanning error: {e}")
    return suspicious

def kill_process(pid):
    try:
        if os.name == 'nt':
            subprocess.call(['taskkill', '/PID', str(pid), '/F'])
        else:
            os.kill(pid, signal.SIGTERM)
        return True
    except Exception as e:
        print(f"Process killing error: {e}")
        return False

scan_interval_ms = 4500
auto_kill_enabled = False
suspicious_processes = []

def auto_detect_keyloggers():
    global suspicious_processes
    suspicious_processes = list_suspicious_processes()
    if auto_kill_enabled:
        for pid, _ in suspicious_processes:
            kill_process(pid)
    update_results_text()
    listbox_update()
    if scan_window.winfo_exists():
        scan_window.after(scan_interval_ms, auto_detect_keyloggers)

def update_results_text():
    results_text.config(state=tk.NORMAL)
    results_text.delete('1.0', tk.END)
    if suspicious_processes:
        results_text.insert(tk.END, "Potential Keyloggers Detected:\n\n")
        for pid, name in suspicious_processes:
            results_text.insert(tk.END, f"PID {pid} - {name}\n")
    else:
        results_text.insert(tk.END, "No suspicious keylogger processes found.\n")
    results_text.config(state=tk.DISABLED)

def manual_kill_selected():
    if not suspicious_processes:
        messagebox.showinfo("Info", "No suspicious processes detected.", parent=scan_window)
        return
    selection = process_listbox.curselection()
    if not selection:
        messagebox.showwarning("Warning", "Please select a process first.", parent=scan_window)
        return
    idx = selection[0]
    pid, name = suspicious_processes[idx]
    if kill_process(pid):
        messagebox.showinfo("Success", f"Killed process: {name} (PID {pid})", parent=scan_window)
    else:
        messagebox.showerror("Error", f"Failed to kill process: {name} (PID {pid})", parent=scan_window)
    auto_detect_keyloggers()

def toggle_autokill():
    global auto_kill_enabled
    auto_kill_enabled = not auto_kill_enabled
    auto_button.config(text=f"Auto Kill: {'ON' if auto_kill_enabled else 'OFF'}")

def listbox_update():
    process_listbox.delete(0, tk.END)
    for pid, name in suspicious_processes:
        process_listbox.insert(tk.END, f"{name} (PID {pid})")

def on_refresh():
    auto_detect_keyloggers()

quick_scan_files = [
    "config.sys", "login.keylogger", "log_monitor.dll", "random_file.log", "keylogger_tool.exe"
]

full_scan_files = [
    "system32.dll", "kernel.sys", "user.profile", "firewall.exe",
    "passwords.txt", "log_creator.exe", "notes.docx", "backup.bak",
    "temp.tmp", "login.cfg", "chrome.exe", "notepad.exe", "random.log",
    "malware.exe", "key_creator.exe", "document.pdf", "image.jpg"
]

def scan_files_simulation(scan_button, scan_type):
    files = quick_scan_files if scan_type == "quick" else full_scan_files
    scan_button.config(state=tk.DISABLED)
    results_text.config(state=tk.NORMAL)
    results_text.delete('1.0', tk.END)
    results_text.insert(tk.END, f"{scan_type.capitalize()} Scan Started...\n\n")
    total = len(files)
    delay = 350

    def step(i=0):
        if i < total:
            results_text.insert(tk.END, f"Scanning: {files[i]}\n")
            results_text.see(tk.END)
            scan_button.after(delay, step, i+1)
        else:
            results_text.insert(tk.END, f"\n{scan_type.capitalize()} Scan Completed.\n")
            results_text.config(state=tk.DISABLED)
            scan_button.config(state=tk.NORMAL)

    step()

def full_real_scan(scan_button, start_path=None):
    if scan_button['state'] == tk.DISABLED:
        return
    scan_button.config(state=tk.DISABLED)
    results_text.config(state=tk.NORMAL)
    results_text.delete('1.0', tk.END)
    if start_path is None:
        start_path = "C:\\" if os.name == 'nt' else "/"
    results_text.insert(tk.END, f"Starting full system scan from: {start_path}\n\n")
    results_text.see(tk.END)

    def scan_worker():
        found = []
        try:
            for root, dirs, files in os.walk(start_path):
                for file in files:
                    if "keylog" in file.lower():
                        path = os.path.join(root, file)
                        found.append(path)
                        results_text.insert(tk.END, f"Suspicious file: {path}\n")
                        results_text.see(tk.END)
        except Exception as e:
            results_text.insert(tk.END, f"\nError during scan: {e}\n")
        if not found:
            results_text.insert(tk.END, "\nNo suspicious files found.\n")
        else:
            results_text.insert(tk.END, f"\nScan complete: {len(found)} suspicious files found.\n")
        results_text.config(state=tk.DISABLED)
        scan_button.config(state=tk.NORMAL)

    threading.Thread(target=scan_worker, daemon=True).start()

def show_scan():
    global scan_window, scan_style, theme_selector, process_listbox, results_text, auto_button, quick_button, full_button, real_button

    scan_window = tk.Tk()
    scan_window.title("Keylogger Scanner")
    scan_window.geometry("980x700")
    scan_window.resizable(False, False)

    scan_style = ttk.Style(scan_window)
    apply_theme(scan_window, scan_style, current_theme)

    header = ttk.Frame(scan_window)
    header.pack(fill=tk.X, padx=20, pady=12)
    ttk.Label(header, text="Keylogger Scanner", style="Header.TLabel").pack(side=tk.LEFT)

    ttk.Label(header, text="Theme:", font=("Consolas", 12, "bold")).pack(side=tk.LEFT, padx=(40,8))
    theme_selector = ttk.Combobox(header, values=list(COLOR_THEMES.keys()), state="readonly",
                                  width=18, font=("Consolas", 12))
    theme_selector.pack(side=tk.LEFT)
    theme_selector.set(current_theme)
    theme_selector.bind("<<ComboboxSelected>>", lambda e: change_theme(theme_selector.get()))

    controls = ttk.Frame(scan_window)
    controls.pack(fill=tk.X, padx=20, pady=15)
    for i in range(5):
        controls.columnconfigure(i, weight=1)

    quick_button = ttk.Button(controls, text="Quick Scan",
                              command=lambda: scan_files_simulation(quick_button, "quick"))
    quick_button.grid(row=0, column=0, sticky="ew", padx=6)

    full_button = ttk.Button(controls, text="Full Scan",
                             command=lambda: scan_files_simulation(full_button, "full"))
    full_button.grid(row=0, column=1, sticky="ew", padx=6)

    real_button = ttk.Button(controls, text="Full System Scan",
                             command=lambda: full_real_scan(real_button))
    real_button.grid(row=0, column=2, sticky="ew", padx=6)

    auto_button = ttk.Button(controls, text="Auto Kill: OFF", command=lambda: toggle_autokill())
    auto_button.grid(row=0, column=3, sticky="ew", padx=6)

    refresh_button = ttk.Button(controls, text="Refresh Processes", command=lambda: on_refresh())
    refresh_button.grid(row=0, column=4, sticky="ew", padx=6)

    ttk.Label(scan_window, text="Detected Suspicious Processes:", font=("Consolas", 14, "bold")).pack(anchor=tk.W, padx=20)

    process_listbox = tk.Listbox(scan_window, height=10, font=("Consolas", 12),
                                 bg=COLOR_THEMES[current_theme]["entry_bg"],
                                 fg=COLOR_THEMES[current_theme]["fg_color"],
                                 selectbackground=COLOR_THEMES[current_theme]["button_hover"],
                                 selectforeground=COLOR_THEMES[current_theme]["bg_color"],
                                 relief=tk.FLAT, borderwidth=0)
    process_listbox.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

    ttk.Button(scan_window, text="Kill Selected Process", command=lambda: manual_kill_selected(), width=25).pack(pady=10)

    results_text = tk.Text(scan_window, height=15, font=("Consolas", 12),
                           bg=COLOR_THEMES[current_theme]["log_bg"],
                           fg=COLOR_THEMES[current_theme]["fg_color"],
                           insertbackground=COLOR_THEMES[current_theme]["highlight_color"],
                           relief=tk.FLAT, borderwidth=0)
    results_text.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0,20))

    update_colors_widgets(COLOR_THEMES[current_theme])

    scan_window.after(1000, auto_detect_keyloggers)
    scan_window.mainloop()

def validate_login():
    user = username_entry.get()
    pwd = password_entry.get()
    if user == "admin" and pwd == "password":
        login_window.destroy()
        show_scan()
    else:
        messagebox.showerror("Login Failed", "Invalid username or password")

login_window = tk.Tk()
login_window.title("Secure Login")
login_window.geometry("400x320")
login_window.resizable(False, False)

style = ttk.Style(login_window)
apply_theme(login_window, style, current_theme)

frame = ttk.Frame(login_window, padding=30)
frame.pack(expand=True, fill=tk.BOTH)

ttk.Label(frame, text="Secure Login", style="Header.TLabel").pack(pady=(0, 25))

ttk.Label(frame, text="Username:", font=("Consolas", 12)).pack(anchor=tk.W)
username_entry = ttk.Entry(frame, font=("Consolas", 12))
username_entry.pack(fill=tk.X, pady=5)

ttk.Label(frame, text="Password:", font=("Consolas", 12)).pack(anchor=tk.W)
password_entry = ttk.Entry(frame, show="*", font=("Consolas", 12))
password_entry.pack(fill=tk.X, pady=5)

login_btn = ttk.Button(frame, text="Login", width=30, command=validate_login)
login_btn.pack(pady=20)

username_entry.focus()

login_window.mainloop()
