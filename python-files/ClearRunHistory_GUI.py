
import tkinter as tk
from tkinter import messagebox
import subprocess

def clear_run_history():
    try:
        subprocess.run(["REG", "DELETE", "HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Explorer\RunMRU", "/f"], check=True)
        messagebox.showinfo("Success", "Run history cleared successfully.")
    except subprocess.CalledProcessError:
        messagebox.showerror("Error", "Failed to clear Run history.")

root = tk.Tk()
root.title("Clear Run History")
root.geometry("300x150")
root.resizable(False, False)

label = tk.Label(root, text="Click the button below to clear
Run command history.", font=("Arial", 10), pady=20)
label.pack()

btn = tk.Button(root, text="Clear Run History", command=clear_run_history, bg="#0078D7", fg="white", font=("Arial", 10, "bold"))
btn.pack(pady=10)

root.mainloop()
