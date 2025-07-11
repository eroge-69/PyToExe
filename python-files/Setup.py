import tkinter as tk
from tkinter import ttk
import ctypes
import os
import random
import time
import sys

# GDI screen melt
def melt_screen():
    hdc = ctypes.windll.user32.GetDC(0)
    width = ctypes.windll.user32.GetSystemMetrics(0)
    height = ctypes.windll.user32.GetSystemMetrics(1)

    for _ in range(200):
        x = random.randint(0, width - 100)
        y = random.randint(0, height - 100)
        w = random.randint(50, 300)
        h = random.randint(1, 30)
        dx = x + random.randint(-20, 20)
        dy = y + random.randint(-20, 20)

        ctypes.windll.gdi32.BitBlt(
            hdc,
            x, y,
            w, h,
            hdc,
            dx, dy,
            0x00CC0020  # SRCCOPY
        )
        time.sleep(0.01)

    ctypes.windll.user32.ReleaseDC(0, hdc)

# MessageBox ask
def ask_permission():
    MB_YESNO = 0x04
    MB_ICONWARNING = 0x30
    IDYES = 6
    result = ctypes.windll.user32.MessageBoxW(
        0,
        "Run It?",
        "NOESCAPEV5.exe",
        MB_YESNO | MB_ICONWARNING
    )
    return result == IDYES

# Installer GUI
class FakeInstaller:
    def __init__(self, root):
        self.root = root
        self.root.title("NOESCAPEV5.exe Setup Wizard")
        self.root.geometry("720x400")
        self.root.configure(bg="#f0f0f0")
        self.root.resizable(False, False)

        self.step = 0
        self.progress_value = 0

        self.build_ui()

    def build_ui(self):
        self.left_panel = tk.Frame(self.root, bg="#2b2b2b", width=180)
        self.left_panel.pack(side="left", fill="y")

        self.logo_label = tk.Label(
            self.left_panel,
            text="NOESCAPE V5",
            bg="#2b2b2b",
            fg="white",
            font=("Segoe UI", 16, "bold")
        )
        self.logo_label.place(relx=0.5, rely=0.5, anchor="center")

        self.right_panel = tk.Frame(self.root, bg="#f0f0f0", padx=25, pady=25)
        self.right_panel.pack(side="right", expand=True, fill="both")

        self.header = tk.Label(
            self.right_panel,
            text="Welcome to the NOESCAPEV5.exe Setup Wizard",
            font=("Segoe UI", 14, "bold"),
            bg="#f0f0f0"
        )
        self.header.pack(anchor="w")

        self.description = tk.Label(
            self.right_panel,
            text="This wizard will guide you through the installation of NOESCAPEV5.exe.\n\nClick Next to continue.",
            font=("Segoe UI", 10),
            justify="left",
            bg="#f0f0f0"
        )
        self.description.pack(anchor="w", pady=(10, 20))

        self.button_frame = tk.Frame(self.right_panel, bg="#f0f0f0")
        self.button_frame.pack(side="bottom", anchor="e", pady=(0, 10))

        self.next_button = tk.Button(self.button_frame, text="Next", width=12, command=self.next_step)
        self.next_button.pack(side="right", padx=(5, 0))

    def next_step(self):
        if self.step == 0:
            self.header.config(text="Ready to Install")
            self.description.config(text="The installer is ready to install NOESCAPEV5.exe on your device.\n\nClick Install to continue.")
            self.next_button.config(text="Install")
            self.step += 1
        elif self.step == 1:
            self.header.pack_forget()
            self.description.pack_forget()
            self.next_button.pack_forget()
            self.show_progress_bar()

    def show_progress_bar(self):
        self.header = tk.Label(
            self.right_panel,
            text="Installing NOESCAPEV5.exe...",
            font=("Segoe UI", 14, "bold"),
            bg="#f0f0f0"
        )
        self.header.pack(anchor="w", pady=(0, 10))

        self.progress = ttk.Progressbar(
            self.right_panel,
            orient="horizontal",
            length=450,
            mode="determinate",
            maximum=100
        )
        self.progress.pack(pady=30)

        self.update_progress()

    def update_progress(self):
        if self.progress_value <= 100:
            self.progress["value"] = self.progress_value
            self.progress_value += 1
            self.root.after(100, self.update_progress)
        else:
            self.progress.pack_forget()
            self.header.pack_forget()
            self.create_installation_file()
            self.show_completion()
            melt_screen()  # Run melting screen after install finishes

    def create_installation_file(self):
        file_name = "installation_complete.txt"
        with open(file_name, "w") as f:
            f.write("NOESCAPEV5.exe has been successfully installed.\nThank you for using this installer.")

    def show_completion(self):
        self.header = tk.Label(
            self.right_panel,
            text="Installation Complete",
            font=("Segoe UI", 14, "bold"),
            bg="#f0f0f0"
        )
        self.header.pack(anchor="w")

        self.description = tk.Label(
            self.right_panel,
            text="The installation of NOESCAPEV5.exe is finished.\nThank you for using this setup wizard.",
            font=("Segoe UI", 10),
            justify="left",
            bg="#f0f0f0"
        )
        self.description.pack(anchor="w", pady=(10, 20))

        self.finish_button = tk.Button(self.button_frame, text="Finish", width=12, command=self.root.destroy)
        self.finish_button.pack(side="right", padx=(5, 0))


# MAIN ENTRY
if __name__ == "__main__":
    if not ctypes.windll.shell32.IsUserAnAdmin():
        ctypes.windll.user32.MessageBoxW(0, "Please run as Administrator.", "NOESCAPEV5.exe", 0x10)
        sys.exit()

    if ask_permission():
        root = tk.Tk()
        app = FakeInstaller(root)
        root.mainloop()
    else:
        sys.exit()
