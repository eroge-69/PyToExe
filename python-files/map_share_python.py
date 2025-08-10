#!/usr/bin/env python3
# Prosty GUI w Tkinter do mapowania udziałów Samba (używa 'net use' pod spodem)
import tkinter as tk
from tkinter import messagebox
import subprocess
import shlex

def map_drive():
    server = entry_server.get().strip()
    share = var_class.get().strip()
    user = entry_user.get().strip()
    pwd = entry_pwd.get().strip()
    drive = entry_drive.get().strip().upper()
    if not server or not user or not pwd:
        messagebox.showwarning("Błąd", "Uzupełnij server, login i hasło")
        return
    root = f"\\\\{server}\\{share}\\{user}"
    cmd = f'net use {drive}: "{root}" "{pwd}" /user:{user} /persistent:no'
    try:
        subprocess.check_call(cmd, shell=True)
        messagebox.showinfo("OK", f"Podłączono {drive}: -> {root}")
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Błąd", f"Błąd mapowania: {e}")

def unmap_drive():
    drive = entry_drive.get().strip().upper()
    cmd = f'net use {drive}: /delete /y'
    try:
        subprocess.check_call(cmd, shell=True)
        messagebox.showinfo("OK", f"Odłączono {drive}:")
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Błąd", f"Błąd odłączania: {e}")

root = tk.Tk()
root.title("Mapuj udział ucznia - Samba")
tk.Label(root, text="Server (IP/NB):").grid(row=0,column=0,sticky="e")
entry_server = tk.Entry(root, width=30)
entry_server.grid(row=0,column=1)
entry_server.insert(0,"SERVER_IP_OR_NAME")

tk.Label(root, text="Klasa:").grid(row=1,column=0,sticky="e")
var_class = tk.StringVar(value="klasa-4")
tk.OptionMenu(root, var_class, "klasa-4","klasa-5","klasa-6","klasa-7","klasa-8").grid(row=1,column=1,sticky="w")

tk.Label(root, text="Login:").grid(row=2,column=0,sticky="e")
entry_user = tk.Entry(root, width=30)
entry_user.grid(row=2,column=1)

tk.Label(root, text="Hasło:").grid(row=3,column=0,sticky="e")
entry_pwd = tk.Entry(root, width=30, show="*")
entry_pwd.grid(row=3,column=1)

tk.Label(root, text="Litera dysku:").grid(row=4,column=0,sticky="e")
entry_drive = tk.Entry(root, width=5)
entry_drive.grid(row=4,column=1,sticky="w")
entry_drive.insert(0,"Z")

tk.Button(root, text="Mapuj", command=map_drive).grid(row=5,column=0,pady=10)
tk.Button(root, text="Odłącz", command=unmap_drive).grid(row=5,column=1,pady=10)

root.mainloop()
