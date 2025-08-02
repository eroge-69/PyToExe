import customtkinter as ctk
import pygame
import subprocess
import threading
import time
import random
import hashlib
import uuid
from tkinter import messagebox  # ✅ popup standard

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class RectCheatLauncher(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("RECT CHEAT – Free Version")
        self.geometry("750x600")
        self.resizable(False, False)

        pygame.mixer.init()
        self.play_sound("assets/launch.wav")

        self.lang = "English"
        self.texts = self.load_translations()

        self.build_ui()

    def play_sound(self, path):
        try:
            pygame.mixer.music.load(path)
            pygame.mixer.music.play()
        except:
            print("Sound not found.")

    def build_ui(self):
        self.title_label = ctk.CTkLabel(self, text=self.texts[self.lang]["title"], font=("Segoe UI", 24, "bold"))
        self.title_label.pack(pady=(20, 2))

        self.subtitle_label = ctk.CTkLabel(self, text="(Developed by AKA)", font=("Segoe UI", 12, "italic"), text_color="gray")
        self.subtitle_label.pack(pady=(0, 20))

        self.tabview = ctk.CTkTabview(self, width=700, height=400)
        self.tabview.pack(pady=10)

        self.tabs = {
            "AIMBOT": self.tabview.add("AIMBOT"),
            "ESP TOOLS": self.tabview.add("ESP TOOLS"),
            "MISC": self.tabview.add("MISC"),
            "SETTINGS": self.tabview.add("SETTINGS"),
            "SPOOF": self.tabview.add("SPOOF")
        }

        self.build_tabs()

        self.launch_btn = ctk.CTkButton(self, text=self.texts[self.lang]["launch"], fg_color="blue", command=self.launch_game)
        self.launch_btn.pack(pady=15)

    def build_tabs(self):
        # AIMBOT
        a = self.tabs["AIMBOT"]
        ctk.CTkLabel(a, text="Distance Limit").pack(pady=5)
        ctk.CTkSlider(a, from_=0, to=500).pack()
        ctk.CTkLabel(a, text="Aimbot Smooth").pack(pady=5)
        ctk.CTkSlider(a, from_=1, to=10).pack()
        ctk.CTkLabel(a, text="FOV").pack(pady=5)
        ctk.CTkSlider(a, from_=10, to=180).pack()
        ctk.CTkSwitch(a, text="Silent Aim").pack(pady=10)

        # ESP TOOLS
        e = self.tabs["ESP TOOLS"]
        ctk.CTkCheckBox(e, text="ESP Boxes").pack()
        ctk.CTkCheckBox(e, text="Skeleton ESP").pack()
        ctk.CTkCheckBox(e, text="Distance ESP").pack()
        ctk.CTkCheckBox(e, text="Line ESP").pack()

        # MISC
        m = self.tabs["MISC"]
        ctk.CTkButton(m, text="Unlock 240 FPS", fg_color="green").pack(pady=5)
        ctk.CTkButton(m, text="Skin Changer (Visual)", fg_color="purple").pack(pady=5)
        ctk.CTkButton(m, text="Crosshair Overlay", fg_color="orange").pack(pady=5)
        self.streamer_button = ctk.CTkButton(m, text="Enable Streamer Mode", fg_color="gray", command=self.toggle_streamer_mode)
        self.streamer_button.pack(pady=10)

        # SETTINGS
        s = self.tabs["SETTINGS"]
        ctk.CTkLabel(s, text="Theme").pack(pady=5)
        self.theme_menu = ctk.CTkOptionMenu(s, values=["Dark", "Light", "System"], command=self.change_theme)
        self.theme_menu.pack(pady=5)

        ctk.CTkLabel(s, text="Language").pack(pady=5)
        self.lang_menu = ctk.CTkOptionMenu(s, values=["English", "Français", "Español"], command=self.change_language)
        self.lang_menu.pack(pady=5)

        # SPOOF
        f = self.tabs["SPOOF"]
        container = ctk.CTkFrame(f)
        container.pack(pady=10, fill="both", expand=True)

        fake_frame = ctk.CTkFrame(container)
        fake_frame.grid(row=0, column=0, padx=(20, 10), pady=10, sticky="nsew")
        real_frame = ctk.CTkFrame(container)
        real_frame.grid(row=0, column=1, padx=(10, 20), pady=10, sticky="nsew")

        container.columnconfigure(0, weight=1)
        container.columnconfigure(1, weight=1)

        # FAKE SYSTEM INFO
        ctk.CTkLabel(fake_frame, text="FAKE SYSTEM INFO", font=("Segoe UI", 14, "bold")).pack(pady=5)
        self.hwid_label = ctk.CTkLabel(fake_frame, text="")
        self.mac_label = ctk.CTkLabel(fake_frame, text="")
        self.ip_label = ctk.CTkLabel(fake_frame, text="")
        self.serial_label = ctk.CTkLabel(fake_frame, text="")
        for label in [self.hwid_label, self.mac_label, self.ip_label, self.serial_label]:
            label.pack(pady=2)

        self.spoof_progress = ctk.CTkProgressBar(fake_frame, width=250)
        self.spoof_progress.pack(pady=(20, 5))
        self.spoof_percent = ctk.CTkLabel(fake_frame, text="0%")
        self.spoof_percent.pack()
        self.spoof_button = ctk.CTkButton(fake_frame, text="SPOOF", fg_color="red", command=self.start_spoofing)
        self.spoof_button.pack(pady=10)

        # REAL SYSTEM INFO
        ctk.CTkLabel(real_frame, text="REAL SYSTEM INFO", font=("Segoe UI", 14, "bold")).pack(pady=5)
        self.real_hwid_label = ctk.CTkLabel(real_frame, text="Click to reveal...")
        self.real_hwid_label.pack(pady=(10, 5))
        self.toggle_real_hwid = False
        self.real_hwid_button = ctk.CTkButton(real_frame, text="Show real HWID", command=self.toggle_real_hwid_display)
        self.real_hwid_button.pack(pady=5)

        self.refresh_spoof_info(finish_now=True)

    def start_spoofing(self):
        self.hwid_label.configure(text="")
        self.mac_label.configure(text="")
        self.ip_label.configure(text="")
        self.serial_label.configure(text="")
        self.spoof_progress.set(0)
        self.spoof_percent.configure(text="0%")
        self.spoof_button.configure(text="SPOOFING...", state="disabled")
        threading.Thread(target=self.do_spoofing).start()

    def do_spoofing(self):
        duration = random.randint(10, 80)
        steps = duration * 2
        for i in range(steps + 1):
            progress = i / steps
            percent = int(progress * 100)
            self.spoof_progress.set(progress)
            self.spoof_percent.configure(text=f"{percent}%")
            time.sleep(0.5)

        self.refresh_spoof_info()
        self.spoof_button.configure(text="SPOOF", state="normal")
        messagebox.showinfo(
            title="Spoofing Complete",
            message="GOOD GAME BRO!"
        )

    def refresh_spoof_info(self, finish_now=False):
        if finish_now:
            self.spoof_progress.set(1)
            self.spoof_percent.configure(text="100%")
        self.hwid_label.configure(text=f"Fake HWID: {self.gen_hex(8)}-{self.gen_hex(4)}")
        self.mac_label.configure(text=f"Fake MAC: {':'.join(self.gen_hex(6, 2))}")
        self.ip_label.configure(text=f"Fake IP: {'.'.join(str(random.randint(1, 255)) for _ in range(4))}")
        self.serial_label.configure(text=f"Fake Serial: WD-{self.gen_hex(6)}")

    def toggle_real_hwid_display(self):
        if not self.toggle_real_hwid:
            hwid = self.get_real_hwid()
            self.real_hwid_label.configure(text=f"HWID: {hwid}")
            self.real_hwid_button.configure(text="Hide real HWID")
            self.toggle_real_hwid = True
        else:
            self.real_hwid_label.configure(text="Click to reveal...")
            self.real_hwid_button.configure(text="Show real HWID")
            self.toggle_real_hwid = False

    def get_real_hwid(self):
        try:
            node = uuid.getnode()
            hwid = hashlib.sha256(node.to_bytes(6, 'big')).hexdigest()
            return hwid[:16].upper()
        except:
            return "UNKNOWN"

    def toggle_streamer_mode(self):
        self.streamer_button.configure(text="Streamer Mode ENABLED", fg_color="green", state="disabled")
        messagebox.showinfo(
            title="Streamer Mode",
            message="Streamer Mode is now active.\nOverlay and UI visibility are simulated as hidden."
        )

    def gen_hex(self, length, group=1):
        return [f"{random.randint(0, 255):02X}" for _ in range(length // group)]

    def change_theme(self, value):
        ctk.set_appearance_mode(value.lower())

    def change_language(self, lang):
        self.lang = lang
        t = self.texts[lang]
        self.title_label.configure(text=t["title"])
        self.launch_btn.configure(text=t["launch"])

    def launch_game(self):
        path = ctk.filedialog.askopenfilename(title="Select Fortnite.exe", filetypes=[("Executable", "*.exe")])
        if path:
            try:
                subprocess.Popen([path])
            except Exception as e:
                messagebox.showinfo(title="Error", message=str(e))

    def load_translations(self):
        return {
            "English": {
                "title": "RECT CHEAT – free version",
                "launch": "Launch Fortnite"
            },
            "Français": {
                "title": "RECT CHEAT – version gratuite",
                "launch": "Lancer Fortnite"
            },
            "Español": {
                "title": "RECT CHEAT – versión gratuita",
                "launch": "Iniciar Fortnite"
            }
        }

if __name__ == "__main__":
    app = RectCheatLauncher()
    app.mainloop()
