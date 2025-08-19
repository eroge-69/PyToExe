# FiveM GUI Launcher
# Requirements: pip install pillow psutil
# Place your FiveM logo as 'assets/fivem_logo.png'

import os
import sys
import subprocess
import importlib.util
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import webbrowser
import psutil

FIVEM_URL = "https://cfx.re/join/d44jmd"
LOGO_PATH = os.path.join("assets", "fivem_logo.png")
TITLE = "Tilslut dig Direction 16+"
SETUP_FLAG = ".setup_complete"
ERROR_LOG = "setup_error.log"

def install_package(package_name):
    """Silently install a package using pip."""
    try:
        # Hide CMD window on Windows and suppress output
        creationflags = 0x08000000 if sys.platform == "win32" else 0  # CREATE_NO_WINDOW on Windows
        subprocess.run(
            [sys.executable, "-m", "pip", "install", package_name],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True,
            creationflags=creationflags
        )
    except subprocess.CalledProcessError as e:
        # Log error to file instead of showing pop-up
        with open(ERROR_LOG, "a") as f:
            f.write(f"Failed to install {package_name}: {e}\n")
        sys.exit(1)

def check_and_install_dependencies():
    """Check and silently install required packages if not present."""
    # Skip if setup has already been done
    if os.path.exists(SETUP_FLAG):
        return

    # Check and install required packages
    required_packages = ["pillow", "psutil"]
    for package in required_packages:
        if importlib.util.find_spec(package) is None:
            install_package(package)

    # Mark setup as complete
    try:
        with open(SETUP_FLAG, "w") as f:
            f.write("Setup complete")
    except Exception as e:
        with open(ERROR_LOG, "a") as f:
            f.write(f"Failed to create setup flag: {e}\n")
        sys.exit(1)

class FiveMLauncher(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("FiveM Launcher")
        self.geometry("500x350")
        self.resizable(False, False)
        self.configure(bg="#000000")  # Solid black background

        # Background canvas (black)
        self.bg_canvas = tk.Canvas(self, width=500, height=350, bg="#000000", highlightthickness=0)
        self.bg_canvas.place(x=0, y=0)

        # Load logo
        if os.path.exists(LOGO_PATH):
            logo_img = Image.open(LOGO_PATH).resize((500, 350))
            self.logo = ImageTk.PhotoImage(logo_img)
            self.logo_label = tk.Label(self, image=self.logo, bg="#000000")  # Match black background
            self.logo_label.place(x=0, y=0, relwidth=1, relheight=1)
        else:
            self.logo_label = tk.Label(self, bg="#000000")  # Fallback to black
            self.logo_label.place(x=0, y=0, relwidth=1, relheight=1)

        # Subtle shadow effect (canvas)
        self.shadow_canvas = tk.Canvas(self, width=500, height=350, bg="#000000", highlightthickness=0)
        self.shadow_canvas.place(x=0, y=0)
        self.shadow_canvas.create_oval(50, 50, 450, 330, fill="#1ed760", outline="", stipple="gray50", tags="shadow")

        # Title with drop shadow
        self.title_shadow = tk.Label(self, text=TITLE, font=("Helvetica", 24, "bold"), fg="#111111", bg="#000000")
        self.title_shadow.place(relx=0.5, rely=0.18, anchor="center", x=3, y=3)
        self.title_label = tk.Label(self, text=TITLE, font=("Helvetica", 24, "bold"), fg="#1ed760", bg="#000000")
        self.title_label.place(relx=0.5, rely=0.18, anchor="center")

        # Subtitle
        self.subtitle_label = tk.Label(self, text="FiveM Direction 16+ Launcher", font=("Helvetica", 14), fg="#ffffff", bg="#000000")
        self.subtitle_label.place(relx=0.5, rely=0.28, anchor="center")

        # Join button with modern hover effect
        self.join_btn = tk.Button(self, text="Join Server", font=("Helvetica", 16, "bold"), command=self.join_server,
                                  bg="#1ed760", fg="#ffffff", activebackground="#23e06d", bd=0, relief="flat")
        self.join_btn.place(relx=0.5, rely=0.7, anchor="center", width=240, height=60)

        # Gradient-like button border (using nested frames for glow effect)
        self.button_border_outer = tk.Frame(self, bg="#000000", highlightbackground="#23e06d", highlightthickness=2)
        self.button_border_outer.place(relx=0.5, rely=0.7, anchor="center", width=248, height=68)
        self.button_border_inner = tk.Frame(self, bg="#000000", highlightbackground="#1ed760", highlightthickness=2)
        self.button_border_inner.place(relx=0.5, rely=0.7, anchor="center", width=244, height=64)
        self.join_btn.lift()

        # Button hover effect (color and slight scale)
        self.join_btn.bind("<Enter>", self.on_button_enter)
        self.join_btn.bind("<Leave>", self.on_button_leave)

    def on_button_enter(self, event):
        self.join_btn.config(bg="#23e06d")
        self.join_btn.place_configure(width=245, height=62)  # Slight scale up
        self.button_border_inner.config(highlightbackground="#25e570")
        self.button_border_outer.config(highlightbackground="#25e570")

    def on_button_leave(self, event):
        self.join_btn.config(bg="#1ed760")
        self.join_btn.place_configure(width=240, height=60)  # Reset size
        self.button_border_inner.config(highlightbackground="#1ed760")
        self.button_border_outer.config(highlightbackground="#23e06d")

    def join_server(self):
        # Check if FiveM is running
        fivem_running = False
        for proc in psutil.process_iter(['name']):
            if proc.info['name'].lower() == 'fivem.exe':
                fivem_running = True
                break

        if not fivem_running:
            messagebox.showwarning("Advarsel", "Åben FiveM Først")
            return

        try:
            webbrowser.open(FIVEM_URL)
        except Exception as e:
            messagebox.showerror("Error", f"Could not open FiveM link: {e}")

if __name__ == "__main__":
    # Check and install dependencies silently on first run
    check_and_install_dependencies()
    app = FiveMLauncher()
    app.mainloop()