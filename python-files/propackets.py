
import customtkinter as ctk
from tkinter import StringVar
import threading
import time
import pydivert
import random

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class ProPacketsApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("ProPackets")
        self.geometry("500x350")
        self.resizable(False, False)

        self.mode_var = StringVar(value="Advanced")
        self.preset_var = StringVar(value="RoyAL")

        self.active_tab = "HitsDelayer"
        self.apply_settings = {
            "power": 15,
            "fast": 10,
            "slow": 20
        }

        # Title
        self.logo = ctk.CTkLabel(self, text="PRO\nPACKETS", font=("Arial Black", 20))
        self.logo.place(x=30, y=10)

        # Mode
        self.mode_label = ctk.CTkLabel(self, text="Mode")
        self.mode_label.place(x=200, y=10)
        self.mode_menu = ctk.CTkOptionMenu(self, values=["Basic", "Advanced"], variable=self.mode_var)
        self.mode_menu.place(x=200, y=35)

        # Preset
        self.preset_label = ctk.CTkLabel(self, text="Preset")
        self.preset_label.place(x=330, y=10)
        self.preset_menu = ctk.CTkOptionMenu(self, values=["RoyAL", "God", "Aggro"], variable=self.preset_var)
        self.preset_menu.place(x=330, y=35)

        # Sidebar
        self.sidebar = ctk.CTkFrame(self, width=120, height=240, corner_radius=0)
        self.sidebar.place(x=0, y=60)

        self.tabs = ["HitsDelayer", "Teleport", "Chaos"]
        for i, tab in enumerate(self.tabs):
            btn = ctk.CTkButton(self.sidebar, text=tab, width=100, command=lambda t=tab: self.switch_tab(t))
            btn.place(x=10, y=10 + i * 50)

        # Settings frame
        self.settings_frame = ctk.CTkFrame(self, width=360, height=270)
        self.settings_frame.place(x=130, y=60)

        self.power_slider = None
        self.fast_slider = None
        self.slow_slider = None
        self.apply_button = None

        self.running = True
        self.packet_thread = threading.Thread(target=self.packet_interceptor, daemon=True)
        self.packet_thread.start()

        self.switch_tab("HitsDelayer")

    def switch_tab(self, tab):
        self.active_tab = tab

        for widget in self.settings_frame.winfo_children():
            widget.destroy()

        if tab == "HitsDelayer":
            self.power_slider = ctk.CTkSlider(self.settings_frame, from_=0, to=30, number_of_steps=30)
            self.power_slider.set(self.apply_settings["power"])
            power_label = ctk.CTkLabel(self.settings_frame, text="Power")
            power_label.pack(pady=(10, 0))
            self.power_slider.pack(pady=(0, 10))

            self.fast_slider = ctk.CTkSlider(self.settings_frame, from_=0, to=30, number_of_steps=30)
            self.fast_slider.set(self.apply_settings["fast"])
            fast_label = ctk.CTkLabel(self.settings_frame, text="Fast")
            fast_label.pack()
            self.fast_slider.pack(pady=(0, 10))

            self.slow_slider = ctk.CTkSlider(self.settings_frame, from_=0, to=30, number_of_steps=30)
            self.slow_slider.set(self.apply_settings["slow"])
            slow_label = ctk.CTkLabel(self.settings_frame, text="Slow")
            slow_label.pack()
            self.slow_slider.pack(pady=(0, 10))

            self.apply_button = ctk.CTkButton(self.settings_frame, text="Apply", command=self.apply_hitsdelayer)
            self.apply_button.pack(pady=(10, 0))

        elif tab == "Teleport":
            lbl = ctk.CTkLabel(self.settings_frame, text="Random long delay injection (simulated teleport)")
            lbl.pack(pady=80)
            self.apply_button = ctk.CTkButton(self.settings_frame, text="Apply", command=self.apply_teleport)
            self.apply_button.pack()

        elif tab == "Chaos":
            lbl = ctk.CTkLabel(self.settings_frame, text="Random misplace + jitter")
            lbl.pack(pady=80)
            self.apply_button = ctk.CTkButton(self.settings_frame, text="Apply", command=self.apply_chaos)
            self.apply_button.pack()

    def apply_hitsdelayer(self):
        self.apply_settings["power"] = self.power_slider.get()
        self.apply_settings["fast"] = self.fast_slider.get()
        self.apply_settings["slow"] = self.slow_slider.get()
        print("[APPLY] HitsDelayer settings applied:", self.apply_settings)

    def apply_teleport(self):
        self.apply_settings["teleport"] = True
        print("[APPLY] Teleport mode activated")

    def apply_chaos(self):
        self.apply_settings["chaos"] = True
        print("[APPLY] Chaos mode activated")

    def packet_interceptor(self):
        try:
            with pydivert.WinDivert("outbound") as w:
                print("[INFO] Packet sniffer running...")
                while self.running:
                    packet = w.recv()
                    
                    # Only process Minecraft packets (port 25565) or modify as needed
                    if packet.dst_port == 25565:
                        print(f"[DEBUG] Minecraft packet: {packet.dst_addr}:{packet.dst_port}")
                        
                        # Apply packet manipulation based on active settings
                        if self.active_tab == "HitsDelayer":
                            self.apply_hits_delay(packet)
                        elif "teleport" in self.apply_settings:
                            self.apply_teleport_delay(packet)
                        elif "chaos" in self.apply_settings:
                            self.apply_chaos_delay(packet)
                    else:
                        # For non-Minecraft traffic, just pass through
                        print(f"[DEBUG] Other traffic: {packet.dst_addr}:{packet.dst_port}")
                    
                    w.send(packet)
        except Exception as e:
            print("[ERROR]", e)
    
    def apply_hits_delay(self, packet):
        """Apply HitsDelayer settings to packet"""
        power = self.apply_settings.get("power", 15)
        fast = self.apply_settings.get("fast", 10)
        slow = self.apply_settings.get("slow", 20)
        
        # Random delay based on settings
        delay_ms = random.uniform(fast, slow) * (power / 30.0)
        if delay_ms > 0:
            time.sleep(delay_ms / 1000.0)  # Convert to seconds
            print(f"[HITS] Applied {delay_ms:.2f}ms delay")
    
    def apply_teleport_delay(self, packet):
        """Apply teleport-like delay"""
        if random.random() < 0.1:  # 10% chance for teleport delay
            delay_ms = random.uniform(100, 500)  # 100-500ms delay
            time.sleep(delay_ms / 1000.0)
            print(f"[TELEPORT] Applied {delay_ms:.2f}ms teleport delay")
    
    def apply_chaos_delay(self, packet):
        """Apply chaos mode delays"""
        if random.random() < 0.3:  # 30% chance for chaos
            delay_ms = random.uniform(5, 100)  # 5-100ms jitter
            time.sleep(delay_ms / 1000.0)
            print(f"[CHAOS] Applied {delay_ms:.2f}ms chaos delay")

    def on_closing(self):
        self.running = False
        self.destroy()

if __name__ == "__main__":
    app = ProPacketsApp()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()