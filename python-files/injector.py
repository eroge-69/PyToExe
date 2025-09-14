import customtkinter as ctk
from tkinter import messagebox, simpledialog, filedialog
import random
import string
import time
import threading

# Constants
VALID_KEYS = ["pro", "admin", "key"]
current_hwid = ''.join(random.choices(string.ascii_uppercase + string.digits, k=14))

# Set app theme
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# Main app
app = ctk.CTk()
app.title("RIOT Injector Prank")
app.geometry("500x400")
app.resizable(False, False)

# ASCII Art Title
title_label = ctk.CTkLabel(app, text="""
 _____  _____  _____ _______ 
|  __ \|  __ \|_   _|__   __|
| |__) | |__) | | |    | |   
|  _  /|  ___/  | |    | |   
| | \ \| |     _| |_   | |   
|_|  \_\_|    |_____|  |_|   
""", font=("Courier", 14), text_color="white", justify="center")
title_label.pack(pady=10)

# Functions
def inject_popup():
    key = simpledialog.askstring("Enter Key", "Please insert your key:")
    if key in VALID_KEYS:
        loading_popup = ctk.CTkToplevel(app)
        loading_popup.title("Injecting...")
        loading_popup.geometry("300x150")
        loading_popup.resizable(False, False)

        label = ctk.CTkLabel(loading_popup, text="Injecting...")
        label.pack(pady=10)

        progress_var = ctk.DoubleVar()
        progress_bar = ctk.CTkProgressBar(loading_popup, variable=progress_var, width=200)
        progress_bar.pack(pady=10)
        progress_bar.set(0)

        def simulate_loading():
            progress = 0.0
            while progress < 1.0:
                time.sleep(random.uniform(0.1, 0.3))
                progress += random.uniform(0.05, 0.15)
                progress_var.set(min(progress, 1.0))
                loading_popup.update()
            messagebox.showinfo("Injected!", "Successfully injected!")
            loading_popup.destroy()
            app.destroy()

        threading.Thread(target=simulate_loading).start()
    else:
        messagebox.showerror("Invalid Key", "That key isn't valid.")

def edit_config():
    config_popup = ctk.CTkToplevel(app)
    config_popup.title("Edit Config")
    config_popup.geometry("400x300")

    text_area = ctk.CTkTextbox(config_popup, width=380, height=200)
    text_area.pack(pady=10, padx=10)

    def save_config():
        file_path = filedialog.asksaveasfilename(defaultextension=".txt",
                                                 filetypes=[("Text Files", "*.txt")])
        if file_path:
            with open(file_path, "w") as file:
                file.write(text_area.get("1.0", "end"))
            messagebox.showinfo("Saved", "Configuration saved successfully.")

    save_button = ctk.CTkButton(config_popup, text="Save", command=save_config)
    save_button.pack(pady=5)

def reset_hwid():
    global current_hwid
    key = simpledialog.askstring("Enter Key", "Please enter your key:")
    if key in VALID_KEYS:
        hwid_popup = ctk.CTkToplevel(app)
        hwid_popup.title("Reset HWID")
        hwid_popup.geometry("400x150")

        hwid_label = ctk.CTkLabel(hwid_popup, text=f"Current HWID: {current_hwid}")
        hwid_label.pack(pady=10)

        def reset():
            global current_hwid
            current_hwid = ''.join(random.choices(string.ascii_uppercase + string.digits, k=14))
            hwid_label.configure(text=f"Current HWID: {current_hwid}")
            messagebox.showinfo("Reset", "Successfully reset HWID!")

        reset_btn = ctk.CTkButton(hwid_popup, text="Reset HWID", command=reset)
        reset_btn.pack(pady=10)
    else:
        messagebox.showerror("Invalid Key", "Invalid key provided.")

def exit_app():
    confirm = messagebox.askyesno("Exit", "Are you sure you want to exit?")
    if confirm:
        app.destroy()

# Buttons
btn_frame = ctk.CTkFrame(app)
btn_frame.pack(pady=20)

btn1 = ctk.CTkButton(btn_frame, text="1. Inject", width=200, command=inject_popup)
btn1.pack(pady=5)

btn2 = ctk.CTkButton(btn_frame, text="2. Edit Config", width=200, command=edit_config)
btn2.pack(pady=5)

btn3 = ctk.CTkButton(btn_frame, text="3. Reset HWID", width=200, command=reset_hwid)
btn3.pack(pady=5)

btn4 = ctk.CTkButton(btn_frame, text="4. Exit", width=200, command=exit_app)
btn4.pack(pady=5)

# Run
app.mainloop()
