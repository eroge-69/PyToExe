import tkinter as tk
import subprocess

# Admin: Update these paths and display names as needed
bat_files = [
    r"C:\Path\To\nx_version1.bat",
    r"C:\Path\To\nx_version2.bat",
    r"C:\Path\To\nx_version3.bat"
]

# Admin: Change the display names here
display_names = [
    "NX 2007",
    "NX 2206",
    "NX 2306"
]

# Function to run the .bat files
def run_bat(index):
    subprocess.Popen(bat_files[index], shell=True)

# GUI setup
root = tk.Tk()
root.title("NX Launcher")

for i in range(3):
    btn = tk.Button(root, text=display_names[i], width=25, command=lambda i=i: run_bat(i))
    btn.pack(pady=10)

root.mainloop()
