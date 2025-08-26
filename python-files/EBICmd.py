import tkinter as tk
from tkinter import scrolledtext
import subprocess
import threading

# --- Function to run commands and display output ---
def run_command(cmd):
    output_box.delete(1.0, tk.END)  # Clear previous output
    output_box.insert(tk.END, f"Running: {cmd}\n\n")
    output_box.see(tk.END)

    def task():
        process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        for line in process.stdout:
            output_box.insert(tk.END, line)
            output_box.see(tk.END)
        process.wait()
        output_box.insert(tk.END, f"\nCommand finished with exit code {process.returncode}\n")
        output_box.see(tk.END)

    threading.Thread(target=task).start()

# --- Command functions ---
def run_cmd1():
    run_command("bckbld -out bckbld.txt")

def run_cmd2():
    run_command("fildmp -dump -file dmp231_int_'xx'.txt -filenum 231 -records 1,2000 -format INT")

def run_cmd3():
    run_command("fildmp -dump -file dmp171_hex_'xx'.txt -filenum 171 -records 1,2000 -format HEX")

def run_cmd4():
    run_command("fildmp -dump -file dmp11_hex_'xx'.txt -filenum 11 -records 1,2000 -format HEX")

# --- GUI setup ---
root = tk.Tk()
root.title("EBI Datacollector")
root.geometry("600x400")

# Buttons frame
button_frame = tk.Frame(root)
button_frame.pack(pady=10)

tk.Button(button_frame, text="Backbuild", width=25, command=run_cmd1).grid(row=0, column=0, padx=5, pady=5)
tk.Button(button_frame, text="Specific Pager Alarms", width=25, command=run_cmd2).grid(row=0, column=1, padx=5, pady=5)
tk.Button(button_frame, text="Alarm Pager Destinations", width=25, command=run_cmd3).grid(row=1, column=0, padx=5, pady=5)
tk.Button(button_frame, text="Trend List", width=25, command=run_cmd4).grid(row=1, column=1, padx=5, pady=5)

# Output box
output_box = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=70, height=15, font=("Consolas", 10))
output_box.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

root.mainloop()
