
import customtkinter as ctk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import subprocess
import threading
import base64
import re
import os
import shutil
import time

root = None
save_location = "Not set"

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

WALLPAPER_PATH = r"C:\Program Files (x86)\Steam\steamapps\common\wallpaper_engine\projects\myprojects"

accounts = {
    'ruiiixx': 'UzY3R0JUQjgzRDNZ',
    'premexilmenledgconis': 'M3BYYkhaSmxEYg==',
    'vAbuDy': 'Qm9vbHE4dmlw',
    'adgjl1182': 'UUVUVU85OTk5OQ==',
    'gobjj16182': 'enVvYmlhbzgyMjI=',
    '787109690': 'SHVjVXhZTVFpZzE1'
}
passwords = {account: base64.b64decode(accounts[account]).decode('utf-8') for account in accounts}

def load_save_location():
    global save_location
    try:
        with open('lastsavelocation.cfg', 'r') as file:
            target_directory = file.read().strip()
            if os.path.isdir(target_directory):
                save_location = target_directory
            else:
                save_location = "Not set"
    except FileNotFoundError:
        save_location = "Not set"

def printlog(log):
    console.configure(state="normal")
    console.insert("end", log)
    console.yview("end")
    console.configure(state="disabled")

def run_command(pubfileid):
    printlog(f"----------Downloading {pubfileid}--------\n")
    if not os.path.isdir(save_location):
        printlog("Error: Save location is not set correctly or doesn't exist.\n")
        return
    target_directory = os.path.join(save_location, "projects", "myprojects")
    if not os.path.isdir(target_directory):
        printlog("Invalid save location: \projects\myprojects not found.\n")
        return
    dir_option = f"-dir \"{target_directory}\\{pubfileid}\""
    command = f".\\DepotdownloaderMod\\DepotDownloadermod.exe -app 431960 -pubfile {pubfileid} -verify-all -username {username.get()} -password {passwords[username.get()]} {dir_option}"
    printlog(f"Running command: {command}\n")
    try:
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=True)
        stdout, stderr = process.communicate()
        printlog(stdout)
        if stderr:
            printlog(f"[DepotDownloaderMod STDERR]:\n{stderr}\n")
    except Exception as e:
        printlog(f"Error running DepotDownloaderMod: {e}\n")
    printlog("-------------Download finished-----------\n")

def run_commands():
    run_button.configure(state="disabled")
    links = link_text.get("1.0", "end").splitlines()
    for link in links:
        link = link.strip()
        if not link:
            continue
        match = re.search(r'(\d{8,10})', link)
        if match:
            run_command(match.group(1))
        else:
            printlog(f"Invalid link: {link}\n")
    run_button.configure(state="normal")

def start_thread():
    threading.Thread(target=run_commands).start()

def on_closing():
    subprocess.Popen("taskkill /f /im DepotDownloadermod.exe", creationflags=subprocess.CREATE_NO_WINDOW)
    os._exit(0)

def select_save_location():
    global save_location
    selected_directory = filedialog.askdirectory()
    target_directory = os.path.join(selected_directory, "projects", "myprojects")
    if not os.path.isdir(target_directory):
        printlog("Invalid save location: \projects\myprojects not found.\n")
    else:
        save_location = selected_directory
        save_location_label.configure(text=f"Save Location: {selected_directory}")
        with open('lastsavelocation.cfg', 'w') as file:
            file.write(selected_directory)

def show_wallpaper_previews():
    if not os.path.isdir(WALLPAPER_PATH):
        messagebox.showerror("Error", f"Path not found:\n{WALLPAPER_PATH}")
        return
    preview_window = ctk.CTkToplevel(root)
    preview_window.title("Delete Wallpapers")
    preview_window.geometry("900x700")
    scroll_frame = ctk.CTkScrollableFrame(preview_window, width=880, height=680)
    scroll_frame.pack(padx=10, pady=10, fill="both", expand=True)
    row, col = 0, 0
    for folder in os.listdir(WALLPAPER_PATH):
        full_path = os.path.join(WALLPAPER_PATH, folder)
        if os.path.isdir(full_path):
            preview_image = None
            for file in os.listdir(full_path):
                if file.lower().endswith(('.jpg', '.png', '.jpeg')):
                    preview_image = os.path.join(full_path, file)
                    break
            if preview_image:
                try:
                    img = Image.open(preview_image)
                    img_tk = ctk.CTkImage(light_image=img, dark_image=img, size=(150, 150))
                    frame = ctk.CTkFrame(scroll_frame, corner_radius=10)
                    ctk.CTkLabel(frame, text=folder).pack()
                    ctk.CTkLabel(frame, image=img_tk, text="").pack()

                    def delete_folder(p=full_path, f=frame):
                        if messagebox.askyesno("Confirm Delete", f"Delete wallpaper: {folder}?"):
                            shutil.rmtree(p)
                            f.destroy()
                            printlog(f"Deleted: {p}\n")
                            try:
                                subprocess.Popen("taskkill /f /im wallpaper32.exe", creationflags=subprocess.CREATE_NO_WINDOW)
                                subprocess.Popen("start steam://rungameid/431960", shell=True)
                                printlog("Wallpaper Engine restarted.\n")
                            except Exception as e:
                                printlog(f"Failed to restart Wallpaper Engine: {e}\n")

                    ctk.CTkButton(frame, text="Delete", command=delete_folder, fg_color="red").pack(pady=5)
                    frame.grid(row=row, column=col, padx=10, pady=10)
                    col += 1
                    if col >= 3:
                        col = 0
                        row += 1
                except Exception as e:
                    printlog(f"Failed to load preview for {folder}: {e}\n")

def launch_main_app():
    global root, username, link_text, console, run_button, save_location_label

    root.deiconify()
    root.title("Wallpaper Engine Workshop Downloader")
    root.geometry("1000x800")

    ctk.CTkLabel(root, text="Wallpaper Engine Workshop Downloader", font=ctk.CTkFont(size=24, weight="bold")).pack(pady=10)
    account_frame = ctk.CTkFrame(root)
    account_frame.pack(pady=5)
    ctk.CTkLabel(account_frame, text="Select Account:").pack(side="left", padx=5)
    username = ctk.StringVar(value=list(accounts.keys())[0])
    ctk.CTkOptionMenu(account_frame, variable=username, values=list(accounts.keys())).pack(side="left")

    ctk.CTkButton(root, text="Select Wallpaper Engine Path", command=select_save_location).pack(pady=5)
    save_location_label = ctk.CTkLabel(root, text=f"Wallpaper engine path: {save_location}")
    save_location_label.pack()

    ctk.CTkLabel(root, text="Workshop Items:").pack(pady=(10, 0))
    link_text = ctk.CTkTextbox(root, height=120)
    link_text.pack(padx=10, fill="both")

    ctk.CTkLabel(root, text="Console Output:").pack(pady=(10, 0))
    console = ctk.CTkTextbox(root, height=120)
    console.pack(padx=10, fill="both")
    console.configure(state="disabled")

    button_frame = ctk.CTkFrame(root)
    button_frame.pack(pady=10)

    run_button = ctk.CTkButton(button_frame, text="Download", command=start_thread)
    run_button.pack(side="left", padx=10)

    ctk.CTkButton(button_frame, text="Delete Wallpapers", command=show_wallpaper_previews, fg_color="red", hover_color="#aa0000").pack(side="left", padx=10)
    root.protocol("WM_DELETE_WINDOW", on_closing)

def show_splash_screen():
    global root
    root = ctk.CTk()
    root.withdraw()

    splash = ctk.CTkToplevel()
    splash.geometry("400x320")
    splash.overrideredirect(True)

    x = (splash.winfo_screenwidth() // 2) - 200
    y = (splash.winfo_screenheight() // 2) - 160
    splash.geometry(f"+{x}+{y}")

    try:
        img = Image.open("db84b740-1641-4496-9d7e-c978e88983c6.png")
        logo = ctk.CTkImage(light_image=img, dark_image=img, size=(100, 100))
        ctk.CTkLabel(splash, image=logo, text="").pack(pady=(40, 10))
    except:
        pass

    ctk.CTkLabel(splash, text="Made by Guest", font=ctk.CTkFont(size=20, weight="bold")).pack()
    status_label = ctk.CTkLabel(splash, text="Loading...", font=ctk.CTkFont(size=16))
    status_label.pack(pady=(5, 0))

    progress = ctk.CTkProgressBar(splash, width=250)
    progress.set(0)
    progress.pack(pady=15)
    percent = ctk.CTkLabel(splash, text="0%", font=ctk.CTkFont(size=14))
    percent.pack()

    def animate(i=0):
        if i <= 100:
            progress.set(i / 100)
            percent.configure(text=f"{i}%")
            status_label.configure(text="Loading" + "." * ((i // 10) % 4))
            splash.after(25, animate, i + 1)
        else:
            splash.destroy()
            load_save_location()
            launch_main_app()

    animate()
    splash.mainloop()

# Start the splash first
show_splash_screen()
