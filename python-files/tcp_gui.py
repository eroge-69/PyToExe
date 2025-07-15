
import tkinter as tk
from tkinter import messagebox
import subprocess

def run_netsh(value):
    try:
        cmd = f'netsh int tcp set global autotuning={value}'
        subprocess.run(['powershell', '-Command',
                        f'Start-Process cmd -ArgumentList "/c {cmd}" -Verb RunAs'],
                       shell=True)
        messagebox.showinfo("Done", f"Set to: {value.upper()}")
    except Exception as e:
        messagebox.showerror("Error", str(e))

root = tk.Tk()
root.title("TCP Autotuning Switcher")
root.geometry("300x230")
root.resizable(False, False)

tk.Label(root, text="Choose TCP Autotuning Mode:", font=("Segoe UI", 12)).pack(pady=10)

btn_normal = tk.Button(root, text="Set to NORMAL", width=25, command=lambda: run_netsh("normal"))
btn_normal.pack(pady=5)

btn_disabled = tk.Button(root, text="Set to DISABLED", width=25, command=lambda: run_netsh("disabled"))
btn_disabled.pack(pady=5)

btn_restricted = tk.Button(root, text="Set to HIGHLYRESTRICTED", width=25, command=lambda: run_netsh("highlyrestricted"))
btn_restricted.pack(pady=5)

btn_exit = tk.Button(root, text="Exit", width=25, command=root.destroy)
btn_exit.pack(pady=15)

root.mainloop()
