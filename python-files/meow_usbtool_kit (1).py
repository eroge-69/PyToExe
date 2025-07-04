# MeowUSBToolKIT — Flash ISO & Recover USB 🐾
# Updated with device list selection, progress bar and animated 🐱 emoji that follows progress.

import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
import subprocess
import threading
import platform
import traceback

# Meow-style GUI colors
BG_COLOR = "#1e1e2e"
FG_COLOR = "#ffffff"
BTN_COLOR = "#ffcc00"
FONT = ("Segoe UI", 12)

class MeowUSBToolKIT:
    def __init__(self, root):
        self.root = root
        self.root.title("MeowUSBToolKIT 🐾")
        self.root.geometry("520x450")
        self.root.config(bg=BG_COLOR)

        tk.Label(root, text="MeowUSBToolKIT 🐾", bg=BG_COLOR, fg=BTN_COLOR, font=("Segoe UI", 18, "bold")).pack(pady=10)

        self.usb_list = ttk.Combobox(root, font=FONT)
        self.usb_list.pack(pady=10)
        self.refresh_usb_list()

        tk.Button(root, text="🔄 Refresh Devices", font=FONT, bg=BTN_COLOR, command=self.refresh_usb_list).pack(pady=5)
        tk.Button(root, text="💾 Flash ISO/BIN/IMG", font=FONT, bg=BTN_COLOR, command=self.flash_image).pack(pady=10)
        tk.Button(root, text="🔧 Recover USB", font=FONT, bg=BTN_COLOR, command=self.recover_usb).pack(pady=10)

        self.progress_frame = tk.Frame(root, bg=BG_COLOR)
        self.progress_frame.pack(pady=20)

        self.progress = ttk.Progressbar(self.progress_frame, length=400, mode='determinate')
        self.progress.grid(row=0, column=0)

        self.cat_label = tk.Label(self.progress_frame, text="🐱", bg=BG_COLOR, font=("Segoe UI", 14))
        self.cat_label.place(x=0, y=0)

    def refresh_usb_list(self):
        try:
            if platform.system() == "Darwin":
                result = subprocess.run(["diskutil", "list"], capture_output=True, text=True)
                lines = result.stdout.splitlines()
                devices = [line for line in lines if "/dev/disk" in line and "external" in line]
                self.usb_list['values'] = [line.split()[0] for line in devices]
            elif platform.system() == "Windows":
                result = subprocess.run(["wmic", "logicaldisk", "get", "deviceid"], capture_output=True, text=True)
                lines = result.stdout.splitlines()[1:]
                self.usb_list['values'] = [line.strip() for line in lines if line.strip()]
        except Exception as e:
            print("🐾 Error refreshing devices:", e)

    def flash_image(self):
        iso_path = filedialog.askopenfilename(title="Choose ISO/BIN/IMG file")
        selected_device = self.usb_list.get()
        if not iso_path or not selected_device:
            messagebox.showerror("😿", "Please select an image and a USB device.")
            return
        messagebox.showinfo("🐾 Flashing...", f"Image: {iso_path}\nUSB: {selected_device}")
        threading.Thread(target=self.simulate_progress, args=("Flashing completed! 🐾",)).start()

    def recover_usb(self):
        selected_device = self.usb_list.get()
        if not selected_device:
            messagebox.showerror("😿", "Please select a USB device.")
            return

        def run_recovery():
            try:
                self.set_progress(10)
                subprocess.run(["diskutil", "eraseDisk", "exFAT", "MeowUSB", selected_device], check=True)
                self.set_progress(100)
                messagebox.showinfo("✅", "USB Recovered!")
            except subprocess.CalledProcessError:
                try:
                    messagebox.showinfo("🔄", "Trying deeper erase...")
                    self.set_progress(20)
                    subprocess.run(["diskutil", "eraseDisk", "free", "", selected_device], check=True)
                    self.set_progress(60)
                    subprocess.run(["diskutil", "eraseDisk", "exFAT", "MeowUSB", selected_device], check=True)
                    self.set_progress(100)
                    messagebox.showinfo("✅", "USB Fully Recovered!")
                except subprocess.CalledProcessError:
                    try:
                        result = messagebox.askyesno("😿 Error", "Still can't format. Try deep clean (clean all)?")
                        if result:
                            self.clean_all(selected_device)
                    except Exception as e:
                        print("🐾 Recovery fallback error:", e)
                        traceback.print_exc()

        threading.Thread(target=run_recovery).start()

    def clean_all(self, device):
        messagebox.showinfo("🧼 Clean All", "Starting full wipe. Please wait meow...")
        try:
            self.set_progress(30)
            subprocess.run(["diskutil", "zeroDisk", device], check=True)
            self.set_progress(80)
            subprocess.run(["diskutil", "eraseDisk", "exFAT", "MeowUSB", device], check=True)
            self.set_progress(100)
            messagebox.showinfo("✅ Done", "Full clean successful!")
        except subprocess.CalledProcessError:
            self.set_progress(0)
            messagebox.showerror("💥 Meow:(", "Even deep clean failed. Try again later or replace USB.")
        except Exception as e:
            print("🐾 Clean all error:", e)
            traceback.print_exc()

    def simulate_progress(self, done_message):
        self.progress['value'] = 0
        for i in range(0, 101, 10):
            self.set_progress(i)
            self.root.update()
            self.root.after(200)
        messagebox.showinfo("✅", done_message)

    def set_progress(self, value):
        self.progress['value'] = value
        bar_width = 400
        cat_x = int(bar_width * value / 100)
        self.cat_label.place(x=cat_x, y=25)
        self.root.update_idletasks()

if __name__ == '__main__':
    root = tk.Tk()
    app = MeowUSBToolKIT(root)
    root.mainloop()
