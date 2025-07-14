
import tkinter as tk
from tkinter import messagebox
import subprocess
import os

def run_fingerprint_tool():
    try:
        script_path = os.path.join(os.path.dirname(__file__), "Final_Fingerprint_Entropy_Tool.bat")
        subprocess.run(["cmd.exe", "/c", script_path], shell=True)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to run the script: {str(e)}")
    else:
        messagebox.showinfo("Done", "🟢 Fingerprint entropy updated successfully!")

app = tk.Tk()
app.title("Fingerprint Entropy Tool - 10 Day Cycle")
app.geometry("400x200")
app.resizable(False, False)

label = tk.Label(app, text="Run the tool every 10 days per device.\nClick below to rotate system entropy.", font=("Arial", 12))
label.pack(pady=20)

run_button = tk.Button(app, text="Run Fingerprint Tool", command=run_fingerprint_tool, font=("Arial", 12), bg="#4CAF50", fg="white")
run_button.pack(pady=10)

app.mainloop()
