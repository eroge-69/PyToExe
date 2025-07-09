import tkinter as tk
from tkinter import Canvas
import random
import winsound
import time
import keyboard
import threading
import math

# Configuration Area: Customize all settings here
CONFIG = {
    # Audio Settings
    "audio_enabled": True,  # Enable/disable audio (True/False)
    "use_beep": True,  # Use winsound.Beep (True) or winsound.PlaySound (False)
    "beep_base_freq": 1000,  # Base frequency for beeps (Hz, 37-32767)
    "beep_freq_range_min": -500,  # Min frequency offset (Hz)
    "beep_freq_range_max": 500,  # Max frequency offset (Hz)
    "beep_duration_ms": 80,  # Duration per beep (ms)
    "beep_count": 15,  # Number of beeps per call
    "beep_sleep_s": 0.02,  # Sleep time between beeps (seconds)
    "system_sound": "SystemExclamation",  # System sound for PlaySound (e.g., SystemExclamation, SystemAsterisk)

    # Termination Key Combination
    "terminate_keys": ["ctrl", "alt", "shift", "tab"],  # Keys to press simultaneously to terminate

    # Pop-up Window Settings
    "max_windows": 50,  # Maximum number of simultaneous pop-up windows (10-100 recommended)
    "popup_duration_ms": 3000,  # Duration each pop-up stays open (ms)
    "popup_size_min": 200,  # Minimum pop-up size (pixels)
    "popup_size_max": 400,  # Maximum pop-up size (pixels)
    "spawn_rate_initial": 10,  # Initial pop-ups to spawn
    "spawn_rate_per_sec": 5,  # Base pop-ups per second (increases with time)
    "spawn_rate_time_mult": 2,  # Additional pop-ups per 2 seconds elapsed

    # Color Settings
    "colors": ["red", "black", "yellow", "purple", "blue", "lime", "fuchsia", "cyan", "orange", "pink", "gray", "maroon"],  # Available colors
    "color_change_ms": 100,  # Interval for color changes (ms)

    # Window Movement
    "move_interval_min_ms": 20,  # Minimum interval for window movement (ms)
    "move_interval_max_ms": 80,  # Maximum interval for window movement (ms)

    # Illusion Settings
    "illusion_types": ["flip", "boxes", "normal"],  # Available illusions (remove to disable)
    "flip_rotation_ms": 50,  # Interval for text rotation in flip illusion (ms)
    "boxes_shuffle_ms": 200,  # Interval for box shuffling (ms)

    # Messages
    "main_messages": [
        "FATAL CRASH: SYSTEM ANNIHILATED! DIE NOW! 😈🔥💀👺",
        "VIRUS ARMAGEDDON: YOU’RE TOAST! 😱💣👾💥",
        "CRITICAL HACK: TARGET LOCKED! 😠💉⚡👹",
        "RANSOMWARE HELLFIRE: SURRENDER OR BURN! 👹🔪💀",
        "PC EXTERMINATION: HACKER OVERLORD! 😵💥🎉🔥"
    ],
    "virus_messages": [
        "ERASING ALL EXISTENCE... YOU’RE DONE! 😜💾☠️👽",
        "TROJAN APOCALYPSE: NO MERCY! 😈🔪💣💀",
        "INFECTING EVERY BYTE... TOTAL DESTRUCTION! 😎☠️🔥👹",
        "HACK DOMINATION: I OWN YOUR SOUL! ⚡👹💀🎃",
        "SYSTEM ERADICATION: CHAOS UNLEASHED! 😆💥👺🔪",
        "CRYPTO-DOOM: PAY OR PERISH NOW! 😈💰☠️",
        "WIPE APOCALYPSE... NO ESCAPE! 😏🗑️💉👾",
        "VIRUS ETERNITY: YOU’RE MINE FOREVER! 😈🔥👽💥"
    ],
    "taunt_messages": [
        "DENIAL DETECTED: YOU’RE MY SLAVE! 😈🔥👹",
        "CLICK AWAY, WEAKLING: YOU’RE FINISHED! 😜💀🎉",
        "NO HOPE LEFT: I’M UNSTOPPABLE! 😎👹🔪",
        "VIRUS ROARS: YOU’RE PATHETIC! 😈🔥💣👺"
    ]
}

class HellTrollVirus:
    def __init__(self):
        self.windows = []
        self.running = True
        self.start_time = time.time()
        self.no_count = 0
        print("Initializing HellTrollVirus")
        print(f"Loaded CONFIG: {CONFIG}")
        try:
            # Test audio
            if CONFIG["audio_enabled"]:
                print("Playing test audio")
                if CONFIG["use_beep"]:
                    winsound.Beep(1000, 500)
                else:
                    winsound.PlaySound(CONFIG["system_sound"], winsound.SND_ALIAS)
        except Exception as e:
            print(f"Test audio failed: {e}")
        root = tk.Tk()
        self.screen_width = root.winfo_screenwidth()
        self.screen_height = root.winfo_screenheight()
        root.destroy()
        self.main_window = tk.Tk()
        self.windows.append(self.main_window)
        threading.Thread(target=self.check_force_close, daemon=True).start()
        self.spawn_initial_windows()
        self.play_beeps(
            CONFIG["beep_base_freq"], CONFIG["beep_freq_range_min"], CONFIG["beep_freq_range_max"],
            CONFIG["beep_duration_ms"], CONFIG["beep_count"], CONFIG["beep_sleep_s"]
        )
        self.setup_main_window()
        self.main_window.after(1000, self.auto_spawn_windows)
        print("Starting Tkinter main loop")
        try:
            self.main_window.mainloop()
        except Exception as e:
            print(f"Main loop error: {e}")

    def play_beeps(self, base_freq, freq_range_min, freq_range_max, duration, count, sleep_time):
        if not CONFIG["audio_enabled"]:
            print("Audio disabled in CONFIG")
            return
        print(f"Playing {count} beeps with base freq {base_freq}, range [{freq_range_min}, {freq_range_max}], duration {duration} ms")
        for _ in range(count):
            freq = base_freq + random.randint(freq_range_min, freq_range_max)
            try:
                print(f"Playing: freq {freq} Hz, duration {duration} ms")
                if CONFIG["use_beep"]:
                    winsound.Beep(freq, duration)
                else:
                    winsound.PlaySound(CONFIG["system_sound"], winsound.SND_ALIAS)
                time.sleep(sleep_time)
            except Exception as e:
                print(f"Error playing audio: {e}")

    def spawn_initial_windows(self):
        if len(self.windows) < CONFIG["max_windows"]:
            print("Spawning initial windows")
            for _ in range(CONFIG["spawn_rate_initial"]):
                self.create_popup_window(initial=True)

    def create_popup_window(self, initial=False):
        try:
            print("Creating popup window")
            size = random.randint(CONFIG["popup_size_min"], CONFIG["popup_size_max"])
            new_window = tk.Toplevel()
            new_window.title(f"INFECTED! #{random.randint(1, 9999)}")
            new_window.geometry(f"{size}x{size}")
            new_window.geometry(f"+{random.randint(0, self.screen_width-size)}+{random.randint(0, self.screen_height-size)}")
            new_window.attributes('-topmost', True)
            new_window.protocol("WM_DELETE_WINDOW", lambda w=new_window: self.prevent_minimize(w))
            new_window.protocol("WM_TAKE_FOCUS", lambda w=new_window: self.prevent_minimize(w))
            self.windows.append(new_window)

            illusion_type = random.choice(CONFIG["illusion_types"])
            print(f"Selected illusion type: {illusion_type}")
            if illusion_type == "flip":
                self.create_flipping_content(new_window, size)
            elif illusion_type == "boxes":
                self.create_box_content(new_window, size)
            else:
                self.create_normal_content(new_window, size)

            self.change_colors(new_window, size)
            if initial:
                self.play_beeps(1200, -500, 500, 100, 1, 0)
                self.play_beeps(800, -600, 600, 50, 10, 0.01)
            new_window.after(100, lambda w=new_window: self.spaz_window(w))
            new_window.after(CONFIG["popup_duration_ms"], lambda w=new_window: self.destroy_popup(w))
        except Exception as e:
            print(f"Error spawning popup window: {e}")

    def create_flipping_content(self, window, size):
        try:
            print("Creating flipping content")
            canvas = Canvas(window, width=size, height=size, bg="black")
            canvas.pack()
            msg = random.choice(CONFIG["virus_messages"])
            text_id = canvas.create_text(size/2, size/2, text=msg, font=("Arial", 12, "bold"), fill="white", width=size-20)
            self.rotate_content(canvas, text_id, 0)
        except Exception as e:
            print(f"Error in flipping content: {e}")

    def rotate_content(self, canvas, text_id, angle):
        if not self.running:
            return
        try:
            canvas.itemconfig(text_id, angle=angle % 360)
            canvas.after(CONFIG["flip_rotation_ms"], lambda: self.rotate_content(canvas, text_id, angle + 10))
        except:
            pass

    def create_box_content(self, window, size):
        try:
            print("Creating box content")
            frame = tk.Frame(window, width=size, height=size, bg="black")
            frame.pack()
            box_size = size // 3
            boxes = []
            for i in range(3):
                for j in range(3):
                    subframe = tk.Frame(frame, width=box_size, height=box_size, bg=random.choice(CONFIG["colors"]))
                    subframe.place(x=j*box_size, y=i*box_size)
                    tk.Label(subframe, text="VIRUS", font=("Arial", 8), fg="white").pack()
                    boxes.append(subframe)
            self.shuffle_boxes(frame, boxes, box_size)
        except Exception as e:
            print(f"Error in box content: {e}")

    def shuffle_boxes(self, frame, boxes, box_size):
        if not self.running:
            return
        try:
            positions = [(i % 3 * box_size, i // 3 * box_size) for i in range(9)]
            random.shuffle(positions)
            for box, (x, y) in zip(boxes, positions):
                box.place(x=x, y=y)
            frame.after(CONFIG["boxes_shuffle_ms"], lambda: self.shuffle_boxes(frame, boxes, box_size))
        except:
            pass

    def create_normal_content(self, window, size):
        try:
            print("Creating normal content")
            msg = random.choice(CONFIG["virus_messages"])
            tk.Label(window, text=msg, font=("Arial", 12, "bold"), fg="white", bg="red", wraplength=size-20).pack(pady=10)
            self.add_random_text(window)
        except Exception as e:
            print(f"Error in normal content: {e}")

    def destroy_popup(self, window):
        try:
            if window.winfo_exists() and window in self.windows:
                print(f"Destroying popup window: {window}")
                self.windows.remove(window)
                window.destroy()
        except Exception as e:
            print(f"Error destroying popup: {e}")

    def prevent_minimize(self, window):
        if self.running:
            try:
                size = window.winfo_width()
                window.geometry(f"+{random.randint(0, self.screen_width-size)}+{random.randint(0, self.screen_height-size)}")
                window.deiconify()
                window.attributes('-topmost', True)
            except Exception as e:
                print(f"Error preventing minimize: {e}")

    def spaz_window(self, window):
        if self.running and window in self.windows:
            try:
                size = window.winfo_width()
                x = random.randint(0, self.screen_width - size)
                y = random.randint(0, self.screen_height - size)
                window.geometry(f"+{x}+{y}")
                window.after(random.randint(CONFIG["move_interval_min_ms"], CONFIG["move_interval_max_ms"]), lambda w=window: self.spaz_window(w))
            except Exception as e:
                print(f"Error spazzing window: {e}")

    def change_colors(self, window, size):
        if self.running and window in self.windows:
            try:
                bg_color = random.choice(CONFIG["colors"])
                window.configure(bg=bg_color)
                for widget in window.winfo_children():
                    try:
                        widget.configure(bg=bg_color)
                    except:
                        pass
                window.after(CONFIG["color_change_ms"], lambda: self.change_colors(window, size))
            except Exception as e:
                print(f"Error changing colors: {e}")

    def check_force_close(self):
        print("Starting key detection thread")
        while self.running:
            try:
                if all(keyboard.is_pressed(key) for key in CONFIG["terminate_keys"]):
                    print(f"Termination keys {CONFIG['terminate_keys']} detected!")
                    self.running = False
                    for w in self.windows[:]:
                        try:
                            if w.winfo_exists():
                                w.destroy()
                        except Exception as e:
                            print(f"Error destroying window: {e}")
                    self.windows = []
                    exit_window = tk.Tk()
                    exit_window.title("PRANK TERMINATED")
                    exit_window.geometry("600x400")
                    exit_window.configure(bg="blue")
                    tk.Label(exit_window, text="SYSTEM PURGED! Prank OVER! 😎�fire💥", font=("Arial", 20, "bold"), fg="white", bg="blue", wraplength=580).pack(pady=30)
                    self.play_beeps(500, -300, 300, 150, 10, 0.04)
                    exit_window.after(3000, exit_window.destroy)
                    break
            except Exception as e:
                print(f"Error in key detection: {e}")
            time.sleep(0.1)

    def auto_spawn_windows(self):
        if self.running and len(self.windows) < CONFIG["max_windows"]:
            elapsed_time = time.time() - self.start_time
            windows_to_spawn = min(
                CONFIG["spawn_rate_per_sec"] + CONFIG["spawn_rate_time_mult"] * (elapsed_time // 2),
                CONFIG["max_windows"] - len(self.windows)
            )
            print(f"Spawning {windows_to_spawn} windows")
            for _ in range(int(windows_to_spawn)):
                self.create_popup_window()
        if self.running:
            self.main_window.after(1000, self.auto_spawn_windows)

    def add_random_text(self, window):
        if random.random() > 0.3:
            try:
                noise = tk.Label(window, text="ERROR! HACK! VIRUS! 💥" * random.randint(1, 3), font=("Courier", 10), fg=random.choice(["yellow", "white", "red"]), bg=random.choice(CONFIG["colors"]))
                noise.place(x=random.randint(0, 300), y=random.randint(0, 300))
            except Exception as e:
                print(f"Error adding random text: {e}")

    def setup_main_window(self):
        if not self.running:
            return
        print("Setting up main window")
        window = self.main_window
        try:
            print("Configuring window title and geometry")
            window.title(f"VIRUS HELL! #{random.randint(1000, 9999)}")
            window.geometry("600x450")
            window.resizable(False, False)
            window.attributes('-topmost', True)
            window.protocol("WM_DELETE_WINDOW", lambda w=window: self.prevent_minimize(w))
            window.protocol("WM_TAKE_FOCUS", lambda w=window: self.prevent_minimize(w))
            window.geometry(f"+{random.randint(0, self.screen_width-600)}+{random.randint(0, self.screen_height-450)}")

            print("Creating main window widgets")
            msg = random.choice(CONFIG["main_messages"])
            label = tk.Label(window, text=msg, font=("Arial", 18, "bold"), fg="white", wraplength=580)
            label.pack(pady=15)
            progress = tk.Label(window, text="Infection Progress: [██████████ 100%]", font=("Arial", 14), fg="red", bg="black")
            progress.pack(pady=15)
            yes_btn = tk.Button(window, text="Yes, I surrender!", font=("Arial", 14), bg="green", fg="white", command=lambda: self.on_yes(window))
            yes_btn.pack(pady=15)
            no_btn = tk.Button(window, text="No, fight me!", font=("Arial", 14), bg="red", fg="white", command=lambda: self.on_no(window))
            no_btn.pack(pady=15)

            print("Scheduling background flash and window movement")
            self.flash_background(window, label, progress)
            window.after(100, lambda: self.move_window(window))
        except Exception as e:
            print(f"Error in setup_main_window: {e}")

    def flash_background(self, window, label, progress):
        if not self.running:
            return
        try:
            current_color = random.choice(CONFIG["colors"])
            window.configure(bg=current_color)
            label.configure(bg=current_color)
            progress.configure(bg=current_color)
            window.after(CONFIG["color_change_ms"], lambda: self.flash_background(window, label, progress))
        except Exception as e:
            print(f"Error flashing background: {e}")

    def move_window(self, window):
        if not self.running:
            return
        try:
            window.geometry(f"+{random.randint(0, self.screen_width-600)}+{random.randint(0, self.screen_height-450)}")
            window.after(100, lambda: self.move_window(window))
        except Exception as e:
            print(f"Error moving window: {e}")

    def on_yes(self, window):
        self.running = False
        print("User surrendered")
        for w in self.windows[:]:
            try:
                if w.winfo_exists():
                    w.destroy()
            except Exception as e:
                print(f"Error destroying window: {e}")
        self.windows = []
        final_window = tk.Tk()
        final_window.title("TROLL HELL ENDED!")
        final_window.geometry("600x450")
        final_window.configure(bg="green")
        tk.Label(final_window, text="YOU’RE OBLITERATED! TROLLED TO DEATH! 😎🔥💥", font=("Arial", 20, "bold"), fg="white", bg="green", wraplength=580).pack(pady=30)
        self.play_beeps(800, -500, 500, 80, 15, 0.02)
        final_window.after(3000, final_window.destroy)

    def on_no(self, window):
        if not self.running:
            return
        self.no_count += 1
        print(f"User clicked 'No', spawning taunt windows, no_count: {self.no_count}")
        temp_window_count = min(10 + (self.no_count - 1) * 3, CONFIG["max_windows"] - len(self.windows))
        for _ in range(temp_window_count):
            self.create_popup_window()
        for _ in range(5):
            try:
                size = random.randint(CONFIG["popup_size_min"], CONFIG["popup_size_max"])
                taunt_window = tk.Toplevel()
                taunt_window.title(random.choice(["NO ESCAPE!", "VIRUS HELL!", "YOU’RE DOOMED!"]))
                taunt_window.geometry(f"{size}x{size}")
                taunt_window.geometry(f"+{random.randint(0, self.screen_width-size)}+{random.randint(0, self.screen_height-size)}")
                taunt_window.attributes('-topmost', True)
                taunt_window.protocol("WM_DELETE_WINDOW", lambda w=taunt_window: self.prevent_minimize(w))
                taunt_window.protocol("WM_TAKE_FOCUS", lambda w=taunt_window: self.prevent_minimize(w))
                tk.Label(taunt_window, text=random.choice(CONFIG["taunt_messages"]), font=("Arial", 12, "bold"), fg="white", bg="black", wraplength=size-20).pack(pady=10)
                self.add_random_text(taunt_window)
                self.windows.append(taunt_window)
                self.change_colors(taunt_window, size)
                taunt_window.after(CONFIG["popup_duration_ms"], lambda w=taunt_window: self.destroy_popup(w))
                self.play_beeps(1000, -700, 700, 60, 12, 0.01)
            except Exception as e:
                print(f"Error spawning taunt window: {e}")

if __name__ == "__main__":
    HellTrollVirus()
