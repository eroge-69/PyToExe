import customtkinter as ctk
import threading
import keyboard
import time
import random
import psutil
import os
import platform
import atexit

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

def set_system_mode(mode):
    if platform.system() != "Windows":
        return
    p = psutil.Process(os.getpid())
    try:
        if mode == "busted":
            p.nice(psutil.REALTIME_PRIORITY_CLASS)
            os.system("powercfg /setactive SCHEME_MIN")
            os.system("powercfg /change monitor-timeout-ac 0")
            os.system("powercfg /change standby-timeout-ac 0")
            p.cpu_affinity(list(range(psutil.cpu_count())))
        elif mode == "moon":
            p.nice(psutil.NORMAL_PRIORITY_CLASS)
            os.system("powercfg /setactive SCHEME_BALANCED")
            os.system("powercfg /change monitor-timeout-ac 10")
            os.system("powercfg /change standby-timeout-ac 15")
            p.cpu_affinity(list(range(psutil.cpu_count())))
        elif mode == "delax":
            p.nice(psutil.IDLE_PRIORITY_CLASS)
            os.system("powercfg /setactive SCHEME_MAX")
            os.system("powercfg /change monitor-timeout-ac 5")
            os.system("powercfg /change standby-timeout-ac 7")
            p.cpu_affinity([0])
        elif mode == "reset":
            # VERY DANGEROUS RESET
            p.nice(psutil.NORMAL_PRIORITY_CLASS)
            os.system("powercfg /setactive SCHEME_BALANCED")
            os.system("powercfg /deletescheme SCHEME_MIN")  # try delete max perf plan - might require admin, ignore error
            os.system("powercfg /deletescheme SCHEME_MAX")  # try delete power saver plan
            os.system("powercfg /change monitor-timeout-ac 10")
            os.system("powercfg /change standby-timeout-ac 15")
            p.cpu_affinity(list(range(psutil.cpu_count())))
    except Exception as e:
        print(f"Error setting system mode {mode}: {e}")

def cleanup():
    try:
        keyboard.unhook_all()
        keyboard.release("a")
        keyboard.release("d")
        keyboard.clear_all_hotkeys()
        print("Cleaned up keyboard hooks and keys.")
    except Exception as e:
        print("Cleanup error:", e)

class QuasqasMac(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Quasqas Mac - Ultra Keyboard Delay Optimizer")
        self.geometry("520x460")
        self.resizable(False, False)

        self.running = False
        self.mode = None
        self.delay_min = 5
        self.delay_max = 40

        self.create_ui()
        self.animate_title()

        keyboard.add_hotkey("F6", self.toggle_macro)

        self.protocol("WM_DELETE_WINDOW", self.on_close)

        atexit.register(cleanup)

    def create_ui(self):
        self.title_label = ctk.CTkLabel(self, text="Quasqas Mac", font=("Segoe UI Black", 32), text_color="#00FFFF")
        self.title_label.pack(pady=20)

        self.subtitle_label = ctk.CTkLabel(self, text="Extreme Keyboard Delay Reduction", font=("Segoe UI", 14), text_color="#00CCFF")
        self.subtitle_label.pack(pady=(0, 20))

        self.btn_frame = ctk.CTkFrame(self)
        self.btn_frame.pack(pady=10)

        self.busted_btn = ctk.CTkButton(self.btn_frame, text="🚀 BUSTED MODE (DANGEROUS)", width=320,
                                       command=lambda: self.select_mode("busted"), fg_color="#FF4444")
        self.busted_btn.pack(pady=10)

        self.moon_btn = ctk.CTkButton(self.btn_frame, text="🌙 MOON MODE (BALANCED)", width=320,
                                     command=lambda: self.select_mode("moon"), fg_color="#4466FF")
        self.moon_btn.pack(pady=10)

        self.delax_btn = ctk.CTkButton(self.btn_frame, text="🛌 DELAX MODE (STABLE)", width=320,
                                      command=lambda: self.select_mode("delax"), fg_color="#22CC88")
        self.delax_btn.pack(pady=10)

        self.reset_btn = ctk.CTkButton(self.btn_frame, text="⚠️ RESET MODE (VERY DANGEROUS)", width=320,
                                      command=lambda: self.select_mode("reset"), fg_color="#FFAA00")
        self.reset_btn.pack(pady=10)

        self.delay_slider = ctk.CTkSlider(self, from_=1, to=100, number_of_steps=99,
                                          command=self.on_delay_change)
        self.delay_slider.set(self.delay_max)
        self.delay_slider.pack(pady=(20, 5), padx=50)

        self.delay_label = ctk.CTkLabel(self, text=f"Max Delay: {self.delay_max} ms", font=("Segoe UI", 12), text_color="#00CCFF")
        self.delay_label.pack()

        self.status_label = ctk.CTkLabel(self, text="Mode not selected", font=("Consolas", 14), text_color="orange")
        self.status_label.pack(pady=15)

        self.toggle_btn = ctk.CTkButton(self, text="START / STOP (F6)", width=280, command=self.toggle_macro)
        self.toggle_btn.pack(pady=10)

        self.info_label = ctk.CTkLabel(self, text="Press F6 to toggle macro\nSends extremely fast keystrokes\nDangerous modes can affect system stability", font=("Segoe UI", 10), text_color="#00CCFF")
        self.info_label.pack(pady=10)

    def animate_title(self):
        def pulse():
            colors = ["#00FFFF", "#00CCFF", "#0099CC", "#006688"]
            i = 0
            while True:
                self.title_label.configure(text_color=colors[i % len(colors)])
                i += 1
                time.sleep(0.3)
        threading.Thread(target=pulse, daemon=True).start()

    def select_mode(self, mode):
        self.mode = mode
        set_system_mode(mode)
        self.status_label.configure(text=f"Active Mode: {mode.upper()}", text_color="#FFD700")

    def on_delay_change(self, value):
        self.delay_max = int(value)
        self.delay_label.configure(text=f"Max Delay: {self.delay_max} ms")

    def toggle_macro(self):
        if self.mode is None:
            self.status_label.configure(text="Please select a mode first!", text_color="red")
            return

        if self.running:
            self.running = False
            cleanup()
            self.status_label.configure(text=f"Macro stopped ({self.mode.upper()})", text_color="red")
        else:
            self.running = True
            self.status_label.configure(text=f"Macro started ({self.mode.upper()})", text_color="lime")
            threading.Thread(target=self.run_macro_loop, daemon=True).start()

    def run_macro_loop(self):
        keys = ["a", "d"]
        while self.running:
            for key in keys:
                keyboard.press_and_release(key)
                delay = random.uniform(1, self.delay_max) / 1000
                time.sleep(delay)
                if not self.running:
                    break

    def on_close(self):
        self.running = False
        cleanup()
        self.destroy()

if __name__ == "__main__":
    app = QuasqasMac()
    app.mainloop()
