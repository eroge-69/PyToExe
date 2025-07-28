import os, shutil, subprocess, tkinter as tk
from tkinter import messagebox, ttk

def force_delete(path):
    if os.path.exists(path):
        try:
            os.chmod(path, 0o777)
            if os.path.isdir(path):
                shutil.rmtree(path)
            else:
                os.remove(path)
            print(f"[+] Deleted: {path}")
        except Exception as e:
            print(f"[!] Could not delete {path}: {e}")

def kill_processes():
    for proc in ["FiveM.exe", "Steam.exe", "Discord.exe"]:
        subprocess.call(["taskkill","/F","/IM",proc],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL)

def clean_fivem():
    base = os.environ.get('USERPROFILE')
    paths = [
        os.path.join(base, "AppData", "Local", "FiveM", "cache"),
        os.path.join(base, "AppData", "Local", "D3DSCache"),
        os.path.join(base, "AppData", "Local", "Temp"),
        os.path.join(base, "Documents", "Rockstar Games", "GTA V", "logs")
    ]
    for p in paths:
        force_delete(p)

root = tk.Tk()
root.title("FiveM Cleaner")
root.geometry("640x400")
root.configure(bg="#0d0d0d")
style = ttk.Style()
style.theme_use('default')
style.configure("TButton", font=("Segoe UI", 13, "bold"),
                background="#1f1f1f", foreground="cyan")

tk.Label(root, text="Code Cleaner", font=("Segoe UI", 28, "bold"),
         fg="cyan", bg="#0d0d0d").pack(pady=20)

frame = tk.Frame(root, bg="#0d0d0d")
frame.pack(pady=10)
process_kill_var = tk.BooleanVar()
tk.Checkbutton(frame, text="Close Discord & Steam", variable=process_kill_var,
               font=("Segoe UI", 14), fg="white", bg="#0d0d0d",
               selectcolor="#0d0d0d").pack(anchor="w", pady=8)

def run_selected_actions():
    if process_kill_var.get():
        kill_processes()
    messagebox.showinfo("Done", "Selected actions completed.")

def run_clean_fivem():
    clean_fivem()
    messagebox.showinfo("Done", "Cache and temp files cleaned.")

tk.Button(root, text="Run Selected Actions", font=("Segoe UI", 15, "bold"),
          bg="cyan", fg="black", command=run_selected_actions)\
    .pack(pady=15, ipadx=10, ipady=5)

tk.Button(root, text="Clean FiveM", font=("Segoe UI", 15, "bold"),
          bg="cyan", fg="black", command=run_clean_fivem)\
    .pack(pady=15, ipadx=10, ipady=5)

root.mainloop()