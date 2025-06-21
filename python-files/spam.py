import tkinter as tk
import pyautogui
import keyboard
import threading
import time

spamming = False

def spam_loop(message):
    global spamming
    spamming = True
    print("Waiting 5 seconds to focus target window...")
    time.sleep(5)

    print("Spamming started! Press ESC to stop.")
    while spamming:
        if keyboard.is_pressed('esc'):
            spamming = False
            print("Stopped by ESC.")
            break
        pyautogui.typewrite(message)
        pyautogui.press('enter')
        time.sleep(1)

def wait_for_f8(message):
    print("Press F8 to start spamming.")
    keyboard.wait('f8')
    spam_loop(message)

def on_start_click():
    message = entry.get()
    if not message.strip():
        status_label.config(text="Please enter a message to spam.", fg="red")
        return
    status_label.config(text="Waiting for F8 to start...", fg="blue")
    threading.Thread(target=wait_for_f8, args=(message,), daemon=True).start()

# GUI setup
root = tk.Tk()
root.title("Spam Automation with F8 to start, ESC to stop")
root.geometry("400x250")
root.resizable(False, False)

label = tk.Label(root, text="Type your spam message below:")
label.pack(pady=(20, 5))

entry = tk.Entry(root, width=50)
entry.pack(pady=5)
entry.focus()

instructions = tk.Label(root, text="Instructions:\n1. Type message.\n2. Click Start.\n3. Press F8 to start spamming.\n4. Click into chat box.\n5. Press ESC to stop.", justify="left")
instructions.pack(pady=10)

start_button = tk.Button(root, text="Start", command=on_start_click)
start_button.pack(pady=10)

status_label = tk.Label(root, text="", fg="green")
status_label.pack(pady=5)

root.mainloop()
