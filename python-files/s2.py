import time
import random
import os
import threading
import keyboard
from datetime import datetime
import tkinter as tk
from tkinter import filedialog, messagebox
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from colorama import init, Fore, Style
import re

init(autoreset=True)


ansi_escape = re.compile(r'\x1B\[[0-?]*[ -/]*[@-~]')

def visible_len(text):
    return len(ansi_escape.sub('', text))

def clear_terminal():
    os.system('cls' if os.name == 'nt' else 'clear')

def human_typing(element, text):
    for char in text:
        element.send_keys(char)
        time.sleep(random.uniform(0.05, 0.25))

def random_mouse_move(driver):
    action = ActionChains(driver)
    for _ in range(random.randint(3, 10)):
        x = random.randint(0, 100)
        y = random.randint(0, 100)
        action.move_by_offset(x, y).perform()
        time.sleep(random.uniform(0.01, 0.1))
        action.move_by_offset(-x, -y).perform()

def draw_ui(change_count):
    if os.name == 'nt':
        os.system('chcp 65001 >nul')

    box_width = 50
    title = Fore.WHITE + "lynch.v3"
    subtitle = Fore.RED + "Former Username Remover v1.5"
    running = Fore.GREEN + "Running..."
    counter = Fore.MAGENTA + f"Changes [{change_count}]"

    def box_line(content):
        space = (box_width - 2 - visible_len(content)) // 2
        return "?" + " " * space + content + " " * (box_width - 2 - visible_len(content) - space) + "?"

    top = "?" + "?" * (box_width - 2) + "?"
    bottom = "?" + "?" * (box_width - 2) + "?"
    empty = "?" + " " * (box_width - 2) + "?"

    print(top)
    print(box_line(title))
    print(box_line(subtitle))
    print(empty)
    print(box_line(running))
    print(box_line(counter))
    print(bottom)


def log_change(image_path):
    with open("log.txt", "a") as log:
        log.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Changed to: {os.path.basename(image_path)}\n")

def run_bot(sessionid, image1, image2, total_changes):
    change_count = 0
    paused = False
    stop_flag = False

    options = Options()
    options.add_argument("--start-maximized")
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    driver = webdriver.Chrome(options=options)

    try:
        driver.get("https://www.instagram.com/")
        time.sleep(3)
        driver.add_cookie({
            'name': 'sessionid',
            'value': sessionid,
            'domain': '.instagram.com',
            'path': '/',
            'secure': True,
            'httpOnly': True
        })
        driver.get("https://www.instagram.com/accounts/edit/")
        time.sleep(5)

        

        upload_input = driver.find_element(By.XPATH, "//input[@type='file']")

        clear_terminal()
        draw_ui(change_count)

        def pause_listener():
            nonlocal paused
            while change_count < total_changes and not stop_flag:
                if keyboard.is_pressed('p'):
                    paused = not paused
                    state = "Paused" if paused else "Resumed"
                    print(f"\n[{state}] Press P to toggle.\n")
                    time.sleep(1)

        def exit_listener():
            nonlocal stop_flag, paused
            while change_count < total_changes and not stop_flag:
                if keyboard.is_pressed('esc'):
                    paused = True
                    print(Fore.YELLOW + "\n[EXIT] Are you sure you want to exit? (Y/N)")
                    while True:
                        if keyboard.is_pressed('y'):
                            stop_flag = True
                            with open("log.txt", "a") as log:
                                log.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Exit confirmed by user (ESC then Y)\n")
                            print(Fore.YELLOW + "Exiting...")
                            break
                        elif keyboard.is_pressed('n'):
                            paused = False
                            print(Fore.GREEN + "Resuming...")
                            time.sleep(0.5)
                            break
                        time.sleep(0.1)
                    if stop_flag:
                        break
                time.sleep(0.2)

        threading.Thread(target=pause_listener, daemon=True).start()
        threading.Thread(target=exit_listener, daemon=True).start()

        while change_count < total_changes and not stop_flag:
            if paused:
                time.sleep(0.5)
                continue

            for image in [image1, image2]:
                upload_input.send_keys(image)
                log_change(image)
                change_count += 1
                clear_terminal()
                draw_ui(change_count)
                time.sleep(random.uniform(0.5, 1.27))
                if change_count >= total_changes or stop_flag:
                    break

        with open("log.txt", "a") as log:
            log.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Total changes made: {change_count}\n")

        if stop_flag:
            messagebox.showinfo("Exit", "Bot exited by user request.")
        else:
            print("\nDone! Total changes:", change_count)
            messagebox.showinfo("Done", f"Completed {change_count} changes!")

    except Exception as e:
        print("Error:", e)
        messagebox.showerror("Error", str(e))
    finally:
        driver.quit()

#gui

def browse_file(entry_field):
    filepath = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.jpeg *.png")])
    if filepath:
        entry_field.delete(0, tk.END)
        entry_field.insert(0, filepath)

def open_log():
    os.system("notepad log.txt" if os.name == 'nt' else "xdg-open log.txt")

def toggle_dark_mode():
    bg_color = '#1e1e1e' if root['bg'] == 'SystemButtonFace' else 'SystemButtonFace'
    fg_color = 'white' if bg_color == '#1e1e1e' else 'black'

    root.config(bg=bg_color)
    for widget in root.winfo_children():
        try:
            widget.config(bg=bg_color, fg=fg_color)
        except:
            pass

def toggle_session_visibility():
    current = sessionid_entry.cget('show')
    sessionid_entry.config(show='' if current == '*' else '*')
    toggle_button.config(text='Hide' if current == '*' else 'Show')

def start_bot():
    sessionid = sessionid_entry.get()
    image1 = image1_entry.get()
    image2 = image2_entry.get()
    try:
        total_changes = int(changes_entry.get())
    except:
        messagebox.showerror("Error", "Change count must be a number.")
        return

    if not all([sessionid, image1, image2]):
        messagebox.showerror("Error", "Please fill in all fields.")
        return

    image1 = os.path.abspath(image1)
    image2 = os.path.abspath(image2)

    root.destroy()
    run_bot(sessionid, image1, image2, total_changes)

#window

root = tk.Tk()
root.title("lynch.v3 | Former Username Remover v1.5")
root.iconbitmap('user.ico')

sessionid_label = tk.Label(root, text="Session id")
sessionid_label.grid(row=0, column=0, sticky="e", padx=10, pady=5)
sessionid_entry = tk.Entry(root, show="*", width=40)
sessionid_entry.grid(row=0, column=1, padx=10, pady=5)
toggle_button = tk.Button(root, text="Show", command=toggle_session_visibility)
toggle_button.grid(row=0, column=2, padx=5)

tip_label = tk.Label(root, text="(Copy from browser cookies)", fg="gray")
tip_label.grid(row=1, column=1, sticky="w", padx=10)

image1_label = tk.Label(root, text="Image 1")
image1_label.grid(row=2, column=0, sticky="e", padx=10, pady=5)
image1_entry = tk.Entry(root, width=40)
image1_entry.grid(row=2, column=1, padx=10, pady=5)
tk.Button(root, text="Browse", command=lambda: browse_file(image1_entry)).grid(row=2, column=2, padx=5)

image2_label = tk.Label(root, text="Image 2")
image2_label.grid(row=3, column=0, sticky="e", padx=10, pady=5)
image2_entry = tk.Entry(root, width=40)
image2_entry.grid(row=3, column=1, padx=10, pady=5)
tk.Button(root, text="Browse", command=lambda: browse_file(image2_entry)).grid(row=3, column=2, padx=5)

tk.Label(root, text="Total Changes").grid(row=4, column=0, sticky="e", padx=10, pady=5)
changes_entry = tk.Entry(root, width=40)
changes_entry.grid(row=4, column=1, padx=10, pady=5)

tk.Button(root, text="Start", command=start_bot, width=20).grid(row=5, column=1, pady=10)
tk.Button(root, text="View Logs", command=open_log).grid(row=6, column=1, pady=5)
tk.Button(root, text="Dark Mode", command=toggle_dark_mode).grid(row=7, column=1, pady=5)

root.mainloop()