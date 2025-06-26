import tkinter as tk
from tkinter import scrolledtext, filedialog
import subprocess
import threading
import base64
import re
import os

# Function to run the DepotDownloader command
def run_command(pubfileid):
    printlog(f"----------Downloading {pubfileid}--------\n")
    if 'save_location' not in globals():
        printlog("Error: Save location is not set correctly.\n")
        return
    if not os.path.isdir(save_location):
        printlog("Error: Save location is not exist.\n")
        return
    target_directory = os.path.join(save_location, "projects", "myprojects")
    if not os.path.isdir(target_directory):
        printlog("Invaild save location: Selected directory does not contain \projects\myprojects\n")
        return
    dir_option = f"-dir \"{save_location}\\projects\\myprojects\\{pubfileid}\""  # Ensure the directory path is correctly formatted for Windows
    command = f"DepotdownloaderMod\\DepotDownloadermod.exe -app 431960 -pubfile {pubfileid} -verify-all -username {username.get()} -password {passwords[username.get()]} {dir_option}"
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,creationflags=subprocess.CREATE_NO_WINDOW)
    for line in process.stdout:
        printlog(line)
    process.stdout.close()
    process.wait()
    printlog(f"-------------Download finished-----------\n")

def printlog(log):
    console.config(state=tk.NORMAL)
    console.insert(tk.END, log)
    console.yview(tk.END)
    console.config(state=tk.DISABLED)

# Function to handle running commands in sequence
def run_commands():
    run_button.config(state=tk.DISABLED)
    links = link_text.get("1.0", tk.END).splitlines()
    for link in links:
        if link:
            match = re.search(r'\b\d{8,10}\b', link.strip())
            if match:
                run_command(match.group(0))
            else:
                printlog(f"Invalid link: {link}\n")
    run_button.config(state=tk.NORMAL)
            
# Function to run commands in a separate thread
def start_thread():
    threading.Thread(target=run_commands).start()

def on_closing():
    subprocess.Popen("taskkill /f /im DepotDownloadermod.exe", creationflags=subprocess.CREATE_NO_WINDOW)
    os._exit(0)

# Function to select save location
def select_save_location():
    selected_directory = filedialog.askdirectory()
    target_directory = os.path.join(selected_directory, "projects", "myprojects")
    if not os.path.isdir(target_directory):
        printlog("Invaild save location: Selected directory does not contain \projects\myprojects\n")
    else:
        printlog(f"Path set to {selected_directory}\n")
        global save_location
        save_location = selected_directory
        save_location_label.config(text=f"Save Location: {selected_directory}")
        with open('lastsavelocation.cfg', 'w') as file:
            file.write(selected_directory)

# Accounts and passwords
accounts = {'ruiiixx': 'UzY3R0JUQjgzRDNZ',
    'premexilmenledgconis': 'M3BYYkhaSmxEYg==',
    'vAbuDy': 'Qm9vbHE4dmlw',
    'adgjl1182': 'UUVUVU85OTk5OQ==',
    'gobjj16182': 'enVvYmlhbzgyMjI=',
    '787109690': 'SHVjVXhZTVFpZzE1'
    }
passwords = {account: base64.b64decode(accounts[account]).decode('utf-8') for account in accounts}

def load_save_location():
    try:
        with open('lastsavelocation.cfg', 'r') as file:
            target_directory = file.read().strip()
            if os.path.isdir(target_directory):
                global save_location
                save_location = target_directory
            else:
                save_location = "Not set"
    except FileNotFoundError:
        save_location = "Not set"

load_save_location()

# GUI setup
root = tk.Tk()
root.title("Wallpaper Engine Workshop Downloader")

title_label = tk.Label(root, text="Wallpaper Engine Workshop Downloader", font=("Arial", 21))
title_label.grid(row=0, column=0)

# Username selection
username_label = tk.Label(root, text="Select Account:")
username_label.grid(row=1, column=0, sticky='w', padx=(130, 0))
username = tk.StringVar(root)
username.set(list(accounts.keys())[0]) 
username_menu = tk.OptionMenu(root, username, *accounts.keys())
username_menu.grid(row=1, column=0)

# Save location button
save_location_button = tk.Button(root, text="Select wallpaper engine path", command=select_save_location)
save_location_button.grid(row=2, column=0)

save_location_label = tk.Label(root, text=f"Wallpaper engine path: {save_location}")
save_location_label.grid(row=3, column=0)

# Link input
link_label = tk.Label(root, text="Enter workshop items (one per line, support link and file id):")
link_text = scrolledtext.ScrolledText(root, height=10)
link_label.grid(row=4, column=0)
link_text.grid(row=5, column=0)

# Console output
console_label = tk.Label(root, text="Console Output:")
console = scrolledtext.ScrolledText(root, height=10)
console_label.grid(row=6, column=0)
console.grid(row=7, column=0)
console.config(state=tk.DISABLED)

# Run button
run_button = tk.Button(root, text="Download", command=start_thread)
run_button.grid(row=8, column=0)

root.protocol("WM_DELETE_WINDOW", on_closing)

root.mainloop()