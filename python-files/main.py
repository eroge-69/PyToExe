import tkinter as tk
from tkinter import messagebox
import os
import time
import winsound
import keyboard
import ctypes

# Disable Task Manager
def disable_task_manager():
    user32 = ctypes.windll.user32
    user32.SystemParametersInfoW(0x001F, 0, 0, 0)

# Enable Task Manager
def enable_task_manager():
    user32 = ctypes.windll.user32
    user32.SystemParametersInfoW(0x001F, 1, 0, 0)

def show_warning():
    messagebox.showwarning("Warning", "This simulation will disrupt your system. Proceed?")
    if messagebox.askyesno("Confirmation", "Are you sure you want to proceed?"):
        simulate_error()

def simulate_error():
    messagebox.showerror("Error", "An unexpected error has occurred.")
    winsound.Beep(1000, 500)  # Error sound effect
    time.sleep(1)
    show_blue_screen()

def show_blue_screen():
    root = tk.Tk()
    root.attributes("-fullscreen", True)
    root.config(bg="blue")

    label = tk.Label(root, text="A problem has been detected and Windows has been shut down to prevent damage to your computer.\n\nThe system has been halted.", font=("Helvetica", 20), fg="white", bg="blue")
    label.pack(pady=200)

    code_label = tk.Label(root, text="Enter the code to continue: ", font=("Helvetica", 15), fg="white", bg="blue")
    code_label.pack()

    code_entry = tk.Entry(root, font=("Helvetica", 15))
    code_entry.pack()

    def check_code():
        if code_entry.get() == "4414":
            root.destroy()
            enable_task_manager()
            keyboard.unblock_key('esc')
            keyboard.unblock_key('win')
        else:
            messagebox.showerror("Error", "Incorrect code. Please try again.")

    submit_button = tk.Button(root, text="Submit", font=("Helvetica", 15), command=check_code)
    submit_button.pack(pady=20)

    # Block Esc key, Windows key, and Ctrl+Alt+Del
    keyboard.block_key('esc')
    keyboard.block_key('win')
    keyboard.add_hotkey('ctrl+alt+del', lambda: None)

    root.mainloop()

if __name__ == "__main__":
    disable_task_manager()
    show_warning()
