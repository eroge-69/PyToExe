import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess
import shlex

def browse_file():
    filename = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")])
    if filename:
        csv_file_var.set(filename)

def run_sldl():
    csv_file = csv_file_var.get()
    username = username_var.get()
    password = password_var.get()
    name_format = name_format_var.get()
    pref_format = pref_format_var.get()

    if extended_mix_var.get():
        # Append " (Extended Mix)" to {title} if not already present
        name_format = name_format.replace("{title}", "{title} (Extended Mix)")

    if not csv_file or not username or not password:
        messagebox.showerror("Error", "CSV file, username, and password are required.")
        return

    # Build command
    cmd = f'sldl "{csv_file}" --user {username} --pass {password} --name-format "{name_format}" --pref-format {pref_format}'
    try:
        subprocess.run(shlex.split(cmd), check=True)
        messagebox.showinfo("Success", "Download complete!")
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Error", f"Failed to run sldl:\n{e}")

# GUI Setup
root = tk.Tk()
root.title("MD's Soulseek Spotify Playlist Grabber")

csv_file_var = tk.StringVar()
username_var = tk.StringVar()
password_var = tk.StringVar()
name_format_var = tk.StringVar(value="{title} - {artist}")
pref_format_var = tk.StringVar(value="mp3")
extended_mix_var = tk.BooleanVar()

tk.Label(root, text="CSV File:").grid(row=0, column=0, sticky="e")
tk.Entry(root, textvariable=csv_file_var, width=40).grid(row=0, column=1)
tk.Button(root, text="Browse", command=browse_file).grid(row=0, column=2)

tk.Label(root, text="Username:").grid(row=1, column=0, sticky="e")
tk.Entry(root, textvariable=username_var).grid(row=1, column=1, columnspan=2, sticky="we")

tk.Label(root, text="Password:").grid(row=2, column=0, sticky="e")
tk.Entry(root, textvariable=password_var, show="*").grid(row=2, column=1, columnspan=2, sticky="we")

tk.Label(root, text="Name Format:").grid(row=3, column=0, sticky="e")
tk.Entry(root, textvariable=name_format_var).grid(row=3, column=1, columnspan=2, sticky="we")

tk.Checkbutton(root, text="Add 'Extended Mix' to Title", variable=extended_mix_var).grid(row=4, column=0, columnspan=3, sticky="w")

tk.Label(root, text="Preferred Format:").grid(row=5, column=0, sticky="e")
tk.OptionMenu(root, pref_format_var, "mp3", "flac", "wav").grid(row=5, column=1, columnspan=2, sticky="we")

tk.Button(root, text="Run SLDL", command=run_sldl).grid(row=6, column=0, columnspan=3, pady=10)

root.mainloop()
