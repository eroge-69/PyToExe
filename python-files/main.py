
import tkinter as tk
from tkinter import messagebox
import time, random, sys, os
from datetime import datetime, timedelta

try:
    from minigame import DinoRunner
except Exception:
    DinoRunner = None

APP_NAME = "Countdown Clock"
VERSION = "0.4"

class Phase:
    NORMAL = 0
    QUIRKS = 1
    WRONG_TIME = 2
    UNSETTLING = 3
    BREAK_FOURTH_WALL = 4
    COUNTDOWN = 5
    FINALE = 6

class CountdownClockApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Clock")
        self.root.configure(bg="black")
        self.root.geometry("360x160")
        self.root.minsize(280, 120)
        self.root.attributes("-topmost", False)

        # UI
        self.time_label = tk.Label(root, font=("SF Pro Display", 36, "bold"), fg="#7CFC00", bg="black")
        self.time_label.pack(padx=16, pady=(18, 0), fill="x")

        self.sub_label = tk.Label(root, font=("SF Pro Text", 12), fg="#9ae29a", bg="black")
        self.sub_label.pack(padx=16, pady=(4, 12))

        # State
        self.phase = Phase.NORMAL
        self.phase_start = time.time()
        self.wrong_offset_seconds = 0
        self.is_wrong = False
        self.countdown_target = None
        self.flash_counter = 0
        self.tick_ms = 250  # smooth updates
        self.popup_timer = 0
        self.force_front_timer = 0
        self.end_variant = random.choice(["redscreen", "bsod", "loop"])

        # Context menu
        self.menu = tk.Menu(self.root, tearoff=0)
        self.menu.add_command(label="Fix Time", command=self.fix_time)
        self.menu.add_command(label="Toggle Always On Top", command=self.toggle_ontop)
        self.menu.add_separator()
        self.menu.add_command(label="About", command=self.show_about)
        self.menu.add_command(label="Quit", command=self.root.destroy)

        self.root.bind("<Button-3>", self.show_menu)  # right click
        self.root.bind("<Escape>", lambda e: self.root.destroy())
        self.root.bind("<Control-g>", self.open_minigame)  # hidden minigame
        self.root.bind("<space>", self.space_glitch)  # tiny secret

        # Subwindows tracking so we can clean up
        self.child_windows = []

        self.schedule_phase_progression()
        self.update_loop()

    # ---------------- UI / Events ----------------
    def show_menu(self, event):
        try:
            self.menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.menu.grab_release()

    def toggle_ontop(self):
        current = bool(self.root.attributes("-topmost"))
        self.root.attributes("-topmost", not current)

    def show_about(self):
        messagebox.showinfo("About", f"{APP_NAME} v{VERSION}\nA harmless spooky clock prototype.\nRight click → Fix Time\nCtrl+G → Mini‑game")

    def space_glitch(self, event=None):
        # One-frame glitch in early phases
        if self.phase in (Phase.QUIRKS, Phase.WRONG_TIME):
            self.sub_label.config(text="ARE YOU STILL THERE?")

    def open_miniggame_window(self):
        t = tk.Toplevel(self.root)
        t.configure(bg="black")
        t.title("Mini‑game")
        t.geometry("500x220")
        t.attributes("-topmost", True)
        self.child_windows.append(t)
        return t

    def open_minigame(self, event=None):
        if DinoRunner is None:
            messagebox.showinfo("Mini‑game", "Mini‑game module missing.")
            return
        t = self.open_miniggame_window()
        DinoRunner(t)

    # ---------------- Phases ----------------
    def schedule_phase_progression(self):
        # Time (in seconds) to move to next phase — tweak for pacing
        self.phase_durations = {
            Phase.NORMAL: 20,
            Phase.QUIRKS: 30,
            Phase.WRONG_TIME: 40,
            Phase.UNSETTLING: 45,
            Phase.BREAK_FOURTH_WALL: 45,
            Phase.COUNTDOWN: 60,
        }

    def advance_phase_if_ready(self):
        if self.phase == Phase.FINALE:
            return
        elapsed = time.time() - self.phase_start
        need = self.phase_durations.get(self.phase, 9999)
        if elapsed >= need:
            self.phase += 1
            self.phase_start = time.time()
            # Entering phase hooks
            if self.phase == Phase.WRONG_TIME:
                self.is_wrong = True
                self.wrong_offset_seconds = random.randint(-180, 300)
            elif self.phase == Phase.UNSETTLING:
                self.popup_timer = 0
            elif self.phase == Phase.BREAK_FOURTH_WALL:
                self.force_front_timer = 0
            elif self.phase == Phase.COUNTDOWN:
                self.countdown_target = datetime.now() + timedelta(seconds=60)
            elif self.phase == Phase.FINALE:
                self.trigger_finale()

    # ---------------- Clock Logic ----------------
    def get_display_time(self):
        now = datetime.now()
        # Apply wrong-time drift in certain phases
        if self.phase >= Phase.WRONG_TIME and self.is_wrong:
            now = now + timedelta(seconds=self.wrong_offset_seconds)

        # In countdown, show remaining
        if self.phase == Phase.COUNTDOWN and self.countdown_target:
            remain = self.countdown_target - datetime.now()
            if remain.total_seconds() <= 0:
                self.phase = Phase.FINALE
                self.trigger_finale()
                return "00:00:00"
            total = max(0, int(remain.total_seconds()))
            h = total // 3600
            m = (total % 3600) // 60
            s = total % 60
            return f"{h:02d}:{m:02d}:{s:02d}"

        return now.strftime("%H:%M:%S")

    def fix_time(self):
        self.is_wrong = False
        self.wrong_offset_seconds = 0
        self.sub_label.config(text="Time synchronized.")
        self.root.after(1500, lambda: self.sub_label.config(text=""))

    # ---------------- Effects & Popups ----------------
    def random_glitches(self):
        # Subtle flicker
        if self.phase >= Phase.QUIRKS and random.random() < 0.02:
            self.time_label.configure(fg="#a7ff7c" if random.random() < 0.5 else "#7CFC00")

        # Momentary ?????
        if self.phase >= Phase.QUIRKS and random.random() < 0.003:
            self.time_label.config(text="??:??:??")

        # Wrong time toggles
        if self.phase >= Phase.WRONG_TIME and random.random() < 0.005:
            self.is_wrong = not self.is_wrong
            if self.is_wrong:
                self.wrong_offset_seconds += random.randint(-120, 240)

        # UNSETTLING: faint messages
        if self.phase >= Phase.UNSETTLING and random.random() < 0.01:
            msg = random.choice(["ARE YOU THERE", "DON'T TURN AROUND", "IT'S ALMOST TIME", "KEEP WORKING"])
            self.sub_label.config(text=msg)
            self.root.after(1200, lambda: self.sub_label.config(text=""))

        # BREAK FOURTH WALL: fake notepad popups
        if self.phase >= Phase.BREAK_FOURTH_WALL:
            self.popup_timer += self.tick_ms
            if self.popup_timer > 4000 and random.random() < 0.2:
                self.popup_timer = 0
                self.spawn_fake_popup()

            # Force foreground occasionally
            self.force_front_timer += self.tick_ms
            if self.force_front_timer > 7000 and random.random() < 0.15:
                self.force_front_timer = 0
                try:
                    self.root.attributes("-topmost", True)
                    self.root.after(1500, lambda: self.root.attributes("-topmost", False))
                except Exception:
                    pass

        # COUNTDOWN: warnings
        if self.phase == Phase.COUNTDOWN and random.random() < 0.02:
            self.spawn_warning()

    def spawn_fake_popup(self):
        t = tk.Toplevel(self.root)
        t.title("Notes.txt - Notepad")
        t.configure(bg="white")
        t.geometry(f"420x220+{self.root.winfo_rootx()+random.randint(-40,60)}+{self.root.winfo_rooty()+random.randint(-40,60)}")
        self.child_windows.append(t)

        txt = tk.Text(t, wrap="word", bg="white", fg="black")
        txt.insert("1.0", random.choice([
            "the clock is counting down.\n\nyou should not have installed it.",
            "time drifts when you're not looking.",
            "are you sure your system time is correct?",
            "it only ends when you stop watching."
        ]))
        txt.configure(state="disabled")
        txt.pack(expand=True, fill="both")

        # Close itself after a while to avoid spam
        t.after(6000, t.destroy)

    def spawn_warning(self):
        t = tk.Toplevel(self.root)
        t.title("Clock Warning")
        t.configure(bg="black")
        t.attributes("-topmost", True)
        t.geometry("240x120")
        self.child_windows.append(t)

        lbl = tk.Label(t, text="INCOMING", fg="#ff3b30", bg="black", font=("SF Pro Display", 20, "bold"))
        lbl.pack(expand=True, fill="both")
        t.after(1000, t.destroy)

    # ---------------- Finale ----------------
    def trigger_finale(self):
        # Clean popups
        for w in list(self.child_windows):
            try: w.destroy()
            except Exception: pass
        self.child_windows.clear()

        if self.end_variant == "redscreen":
            self.redscreen_end()
        elif self.end_variant == "bsod":
            self.bsod_end()
        else:
            self.loop_end()

    def redscreen_end(self):
        t = tk.Toplevel(self.root)
        t.overrideredirect(True)
        t.attributes("-topmost", True)
        t.geometry(f"{self.root.winfo_screenwidth()}x{self.root.winfo_screenheight()}+0+0")
        t.configure(bg="#8b0000")
        lbl = tk.Label(t, text="00:00:00", font=("SF Pro Display", 120, "bold"), fg="white", bg="#8b0000")
        lbl.pack(expand=True, fill="both")
        t.after(1800, lambda: (t.destroy(), self.reset_to_normal()))

    def bsod_end(self):
        t = tk.Toplevel(self.root)
        t.overrideredirect(True)
        t.attributes("-topmost", True)
        t.geometry(f"{self.root.winfo_screenwidth()}x{self.root.winfo_screenheight()}+0+0")
        t.configure(bg="#0078D7")
        lbl = tk.Label(t, text=":(", font=("Consolas", 160, "bold"), fg="white", bg="#0078D7")
        lbl.pack(pady=40)
        msg = tk.Label(t, text="Your time ran into a problem and needs to restart.\nCollecting some info, and then we'll restart for you.",
                       font=("Consolas", 20), fg="white", bg="#0078D7")
        msg.pack()
        t.after(2800, lambda: (t.destroy(), self.reset_to_normal()))

    def loop_end(self):
        # Subtle: Just quietly reset
        self.reset_to_normal()

    def reset_to_normal(self):
        self.phase = Phase.NORMAL
        self.phase_start = time.time()
        self.is_wrong = False
        self.wrong_offset_seconds = 0
        self.countdown_target = None
        self.end_variant = random.choice(["redscreen", "bsod", "loop"])
        try:
            self.root.attributes("-topmost", False)
        except Exception:
            pass
        self.sub_label.config(text="")
        # Resize back
        self.root.geometry("360x160")

    # ---------------- Main Loop ----------------
    def update_loop(self):
        # Phase progression
        self.advance_phase_if_ready()

        # Time display
        display = self.get_display_time()
        # Occasional 'stutter' effect (repeat same text briefly)
        if random.random() < 0.005 and self.phase >= Phase.QUIRKS:
            pass  # keep last frame
        else:
            self.time_label.config(text=display)

        # Subtitle: show phase name briefly (for debugging, comment out if you want it hidden)
        # self.sub_label.config(text=f"Phase: {self.phase}")

        # Random glitches/effects
        self.random_glitches()

        self.root.after(self.tick_ms, self.update_loop)

def main():
    root = tk.Tk()
    app = CountdownClockApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
