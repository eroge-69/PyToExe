Python 3.13.7 (tags/v3.13.7:bcee1c3, Aug 14 2025, 14:15:11) [MSC v.1944 64 bit (AMD64)] on win32
Enter "help" below or click "Help" above for more information.
"""
Lantern Test Simulator — Professional Edition
- Full-screen Tkinter application for practicing aviation lantern color signals.
- Supports: Red (R), Green (G), White (W), Yellow (Y).
- Modes: Practice / Test (timed). Instructor Mode: optionally show correct answer after each trial.
- Records responses, correctness, reaction times; save to CSV.
- Smooth fade-in/out, polished UI, keyboard hotkeys and on-screen buttons.

Run:
    python lantern_test_pro.py

Author: Assistant (generated)
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import random
import time
import csv
from dataclasses import dataclass
from typing import List, Optional, Tuple

# ----------------------------
# Configuration / Constants
# ----------------------------
APP_TITLE = "Lantern Test Simulator — Professional"
BACKGROUND_COLOR = "#0b0b0b"
PANEL_BG = "#0f0f10"
TEXT_FG = "#eaeaea"
MUTED_FG = "#9aa0a6"
ACCENT = "#2a9df4"
BUTTON_BG = "#1f1f1f"
BUTTON_FG = "#ffffff"

FONT_UI = ("Segoe UI", 11)
FONT_LARGE = ("Segoe UI", 16, "bold")
FONT_SMALL = ("Segoe UI", 10)

DEFAULT_TRIALS = 30
DEFAULT_RESPONSE_TIME = 2.0  # seconds for Test mode
CIRCLE_DIAMETER = 10  # requested 9-10 px -> chosen 10
CIRCLE_RADIUS = CIRCLE_DIAMETER // 2
FADE_STEPS = 10
FADE_STEP_MS = 18  # total ~180ms fade-in/out

# Colors available (add yellow here)
# Values are base RGB tuples (0-255)
COLOR_MAP = {
    "R": (220, 45, 45),    # Red (slightly softer than pure 255 to look nicer)
    "G": (50, 210, 80),    # Green
    "W": (255, 255, 255),  # White
    "Y": (255, 215, 30),   # Yellow (warm)
}

COLOR_NAME = {
    "R": "Red",
    "G": "Green",
    "W": "White",
    "Y": "Yellow",
}

HOTKEYS = {k: k for k in COLOR_MAP.keys()}  # R, G, W, Y

# ----------------------------
# Data Classes
# ----------------------------
@dataclass
class TrialRecord:
    trial_index: int
    presented: List[str]
    response: List[Optional[str]]
    correct: List[bool]
    reaction_times: List[Optional[float]]
    timed_out: bool

# ----------------------------
# Utility Functions
# ----------------------------
def rgb_to_hex(rgb: Tuple[int, int, int]) -> str:
    return "#{:02x}{:02x}{:02x}".format(*rgb)

def scale_color(rgb: Tuple[int, int, int], factor: float) -> Tuple[int, int, int]:
    return tuple(max(0, min(255, int(c * factor))) for c in rgb)

# ----------------------------
# Test Sequence Generator
# ----------------------------
class LanternTest:
    def __init__(self,
                 num_trials: int = DEFAULT_TRIALS,
                 mode: str = "Practice",
                 response_time: float = DEFAULT_RESPONSE_TIME,
                 allow_pairs: bool = True,
                 colors: List[str] = None,
                 brightness_variation: bool = False,
                 pair_probability: float = 0.5):
        self.num_trials = max(1, int(num_trials))
        self.mode = mode
        self.response_time = float(response_time)
        self.allow_pairs = allow_pairs
        self.colors = colors or list(COLOR_MAP.keys())
        self.brightness_variation = brightness_variation
        self.pair_probability = pair_probability
        self.sequence = self._generate_sequence()
        self.index = 0

    def _generate_sequence(self) -> List[List[str]]:
        seq = []
        for _ in range(self.num_trials):
            if self.allow_pairs and random.random() < self.pair_probability:
                # choose two (could be same occasionally)
                if random.random() < 0.85:
                    left, right = random.sample(self.colors, 2)
                else:
                    left = random.choice(self.colors)
                    right = random.choice(self.colors)
                seq.append([left, right])
            else:
                seq.append([random.choice(self.colors)])
        random.shuffle(seq)  # shuffle whole set for better mixing
        return seq

    def next_trial(self) -> Optional[List[str]]:
        if self.index >= len(self.sequence):
            return None
        t = self.sequence[self.index]
        self.index += 1
        return t

    def reset(self):
        self.sequence = self._generate_sequence()
        self.index = 0

# ----------------------------
# Main Application
# ----------------------------
class LanternApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.configure(bg=BACKGROUND_COLOR)
        self.attributes("-fullscreen", True)

        # Screen metrics
        self.screen_w = self.winfo_screenwidth()
        self.screen_h = self.winfo_screenheight()

        # Variables (UI-bindable)
        self.num_trials_var = tk.IntVar(value=DEFAULT_TRIALS)
        self.mode_var = tk.StringVar(value="Practice")
        self.response_time_var = tk.DoubleVar(value=DEFAULT_RESPONSE_TIME)
        self.brightness_var = tk.BooleanVar(value=False)
        self.instructor_var = tk.BooleanVar(value=False)
        self.pair_prob_var = tk.DoubleVar(value=0.5)

        # Runtime state
        self.test: Optional[LanternTest] = None
        self.results: List[TrialRecord] = []
        self.current_presented: List[str] = []
        self.current_brightness: List[float] = []
        self.current_response: List[Optional[str]] = []
        self.current_rts: List[Optional[float]] = []
        self.timed_out = False
        self.trial_start_time = 0.0
        self.timeout_id = None
        self.anim_ids: List[str] = []
        self.canvas_items = []
        self.waiting = 0

        # Build UI
        self._build_ui()

        # Key bindings
        self.bind_all("<Key>", self._on_key)

    # ----------------------------
    # UI Building
    # ----------------------------
    def _build_ui(self):
        # Top bar
        top = tk.Frame(self, bg=BACKGROUND_COLOR)
        top.pack(side=tk.TOP, fill=tk.X, padx=18, pady=10)

        title = tk.Label(top, text=APP_TITLE, fg=TEXT_FG, bg=BACKGROUND_COLOR, font=FONT_LARGE)
        title.pack(side=tk.LEFT)

        controls = tk.Frame(top, bg=BACKGROUND_COLOR)
        controls.pack(side=tk.RIGHT)

        # Mode & settings group
        settings = tk.Frame(controls, bg=BACKGROUND_COLOR)
        settings.pack(side=tk.LEFT, padx=8)

        tk.Label(settings, text="Mode:", fg=MUTED_FG, bg=BACKGROUND_COLOR, font=FONT_UI).grid(row=0, column=0, sticky="w")
        mode_combo = ttk.Combobox(settings, textvariable=self.mode_var, values=["Practice", "Test"], width=10, state="readonly")
        mode_combo.grid(row=0, column=1, padx=6)
        tk.Label(settings, text="Trials:", fg=MUTED_FG, bg=BACKGROUND_COLOR, font=FONT_UI).grid(row=0, column=2, padx=(12,0))
        tk.Entry(settings, textvariable=self.num_trials_var, width=5, font=FONT_UI).grid(row=0, column=3, padx=6)
        tk.Label(settings, text="Response (s):", fg=MUTED_FG, bg=BACKGROUND_COLOR, font=FONT_UI).grid(row=0, column=4, padx=(12,0))
        tk.Entry(settings, textvariable=self.response_time_var, width=6, font=FONT_UI).grid(row=0, column=5, padx=6)

        cb_bright = tk.Checkbutton(settings, text="Brightness variation", fg=MUTED_FG, bg=BACKGROUND_COLOR,
                                   variable=self.brightness_var, activebackground=BACKGROUND_COLOR, selectcolor=BACKGROUND_COLOR,
                                   font=FONT_SMALL)
        cb_bright.grid(row=0, column=6, padx=(12,0))

        # Instructor toggle
        instr_frame = tk.Frame(controls, bg=BACKGROUND_COLOR)
        instr_frame.pack(side=tk.LEFT, padx=12)
        cb_instr = tk.Checkbutton(instr_frame, text="Instructor Mode", fg=TEXT_FG, bg=BACKGROUND_COLOR,
                                  variable=self.instructor_var, font=FONT_UI,
                                  selectcolor=BACKGROUND_COLOR, activebackground=BACKGROUND_COLOR)
        cb_instr.pack(anchor="e")

        # Start / Exit
        action_frame = tk.Frame(controls, bg=BACKGROUND_COLOR)
        action_frame.pack(side=tk.LEFT, padx=12)
        start_btn = ttk.Button(action_frame, text="Start Test (Fullscreen)", command=self.start_test)
        start_btn.pack(pady=(0,6), fill=tk.X)
        exit_btn = ttk.Button(action_frame, text="Exit Fullscreen / Quit", command=self.on_exit)
        exit_btn.pack(fill=tk.X)

        # Separator
        sep = tk.Frame(self, height=1, bg="#141414")
        sep.pack(fill=tk.X, padx=18, pady=(6,12))

        # Canvas area for lights
        self.canvas = tk.Canvas(self, bg=BACKGROUND_COLOR, highlightthickness=0)
        self.canvas.pack(expand=True, fill=tk.BOTH)

        # Bottom panel: buttons + progress + save
        bottom = tk.Frame(self, bg=BACKGROUND_COLOR)
        bottom.pack(side=tk.BOTTOM, fill=tk.X, padx=18, pady=12)

        # Generate response buttons dynamically from COLORS
        btn_frame = tk.Frame(bottom, bg=BACKGROUND_COLOR)
        btn_frame.pack(side=tk.LEFT)
        self.color_buttons = {}
        for idx, code in enumerate(COLOR_MAP.keys()):
            name = f"{COLOR_NAME[code]} ({code})"
            btn = ttk.Button(btn_frame, text=name, command=lambda c=code: self.register_response(c))
            btn.grid(row=0, column=idx, padx=6)
            self.color_buttons[code] = btn

        # Right side: progress, summary, save
        right_frame = tk.Frame(bottom, bg=BACKGROUND_COLOR)
        right_frame.pack(side=tk.RIGHT)

        self.status_label = tk.Label(right_frame, text="Ready", fg=MUTED_FG, bg=BACKGROUND_COLOR, font=FONT_UI)
        self.status_label.pack(anchor="e")

        self.progress_label = tk.Label(right_frame, text="Trial 0 / 0", fg=TEXT_FG, bg=BACKGROUND_COLOR, font=FONT_UI)
        self.progress_label.pack(anchor="e", pady=(6,0))

        summary_btn = ttk.Button(right_frame, text="Show Summary", command=self.show_summary)
        summary_btn.pack(anchor="e", pady=(6,0))
        save_btn = ttk.Button(right_frame, text="Save CSV", command=self.save_results)
        save_btn.pack(anchor="e", pady=(6,0))

    # ----------------------------
    # Controls
    # ----------------------------
    def on_exit(self):
        if self.attributes("-fullscreen"):
            self.attributes("-fullscreen", False)
        else:
            self.quit()

    def start_test(self):
        # Validate inputs
        try:
            n = int(self.num_trials_var.get())
            if n <= 0:
                raise ValueError()
        except Exception:
            messagebox.showerror("Invalid Trials", "Trials must be a positive integer.")
            return

        try:
            response_time = float(self.response_time_var.get())
            if response_time <= 0:
                raise ValueError()
        except Exception:
            messagebox.showerror("Invalid Response Time", "Response time must be a positive number.")
            return

        # Fullscreen immediately
        self.attributes("-fullscreen", True)

        # Create LanternTest
        self.test = LanternTest(num_trials=n,
                                mode=self.mode_var.get(),
                                response_time=response_time,
                                allow_pairs=True,
                                colors=list(COLOR_MAP.keys()),
                                brightness_variation=self.brightness_var.get(),
                                pair_probability=self.pair_prob_var.get())

        self.results.clear()
        self.status_label.config(text=f"Mode: {self.test.mode}  |  Instructor: {'On' if self.instructor_var.get() else 'Off'}")
        self.progress_label.config(text=f"Trial 0 / {self.test.num_trials}")

        # Start first trial quickly
        self.after(160, self._next_trial)

    # ----------------------------
    # Trial Flow
    # ----------------------------
    def _next_trial(self):
        # Cancel pending animations/timeouts
        self._cancel_pending()
        if self.test is None:
            return

        trial = self.test.next_trial()
        if trial is None:
            self._end_test()
            return

        self.current_presented = trial
        self.current_response = [None] * len(trial)
        self.current_rts = [None] * len(trial)
        self.timed_out = False
        self.waiting = len(trial)

        # brightness factors
        if self.test.brightness_variation:
            self.current_brightness = [random.uniform(0.28, 1.0) for _ in trial]
        else:
            self.current_brightness = [1.0 for _ in trial]

        # draw with fade-in
        self._draw_presented(self.current_presented, self.current_brightness, fade_in=True)

        # start timing
        self.trial_start_time = time.perf_counter()

        # setup timeout in Test mode
        if self.test.mode == "Test":
            ms = int(self.test.response_time * 1000)
            self.timeout_id = self.after(ms, self._on_timeout)
        else:
            self.timeout_id = None

        # update progress
        done = len(self.results)
        total = self.test.num_trials
        self.progress_label.config(text=f"Trial {done}/{total}")

    def _on_timeout(self):
        # Mark any unanswered as missed and finalize
        self.timed_out = True
        for i in range(len(self.current_response)):
            if self.current_response[i] is None:
                self.current_response[i] = None
                self.current_rts[i] = None
        self._finalize_trial()
        # small pause then continue
        self.after(320, self._next_trial)

    def _finalize_trial(self):
        # Determine correctness per slot
        correct = []
        for j, pres in enumerate(self.current_presented):
            resp = self.current_response[j]
            correct.append(resp == pres)

        rec = TrialRecord(
            trial_index=len(self.results) + 1,
            presented=self.current_presented.copy(),
            response=self.current_response.copy(),
            correct=correct,
            reaction_times=self.current_rts.copy(),
            timed_out=self.timed_out
        )
        self.results.append(rec)

        # Update status
        last_ok = all(correct)
        self.status_label.config(text=f"Trial {rec.trial_index}/{self.test.num_trials}  —  {'Correct' if last_ok else 'Incorrect'}  |  Instructor: {'On' if self.instructor_var.get() else 'Off'}")

        # Instructor Mode: show correct color(s) for a short moment before continuing
        if self.instructor_var.get():
            self._show_correct_then_continue()
        else:
            # fade out and continue quickly
            self._draw_presented(self.current_presented, self.current_brightness, fade_in=False)
            self.after(220, self._next_trial)

    def _show_correct_then_continue(self):
        # Highlight correct positions by drawing an outline or label, then continue
        self._draw_correct_overlay()
        # Keep overlay visible for 600-900ms (short teaching pause), then fade out and next trial
        self.after(750, lambda: (self._draw_presented(self.current_presented, self.current_brightness, fade_in=False), self.after(220, self._next_trial)))

    def _end_test(self):
        self.status_label.config(text="Test complete")
        self.progress_label.config(text=f"Trial {len(self.results)}/{self.test.num_trials}")
        self.show_summary()

    # ----------------------------
    # Drawing: present and fade
    # ----------------------------
    def _center_positions(self, count: int) -> List[Tuple[int, int]]:
        w = self.canvas.winfo_width() or self.screen_w
        h = self.canvas.winfo_height() or self.screen_h
        cx = w // 2
        cy = h // 2
        if count == 1:
            return [(cx, cy)]
        # two positions: left and right
        spacing = max(90, CIRCLE_DIAMETER * 10)  # ensure visually separated
        return [(cx - spacing // 2, cy), (cx + spacing // 2, cy)]

    def _draw_presented(self, colors: List[str], brightness: List[float], fade_in: bool):
        """Draw the current lights; fade_in True = fade up, else fade out (fade to black)."""
        # cancel previous animations
        self._cancel_pending()
        self.canvas.delete("all")
        self.canvas_items.clear()

        positions = self._center_positions(len(colors))
        self.canvas.create_text(self.screen_w//2, positions[0][1] + 60, text=("Identify color(s) — Left → Right" if len(colors) == 2 else "Identify the color"),
                                fill=MUTED_FG, font=FONT_UI, tag="prompt")

        if fade_in:
            for step in range(1, FADE_STEPS + 1):
                factor = step / FADE_STEPS
                aid = self.after(FADE_STEP_MS * step, lambda f=factor, pos=positions, cols=colors, br=brightness: self._draw_step(pos, cols, br, f))
                self.anim_ids.append(aid)
        else:
            # fade out: reduce from 1.0 to near 0 across steps
            for step in range(1, FADE_STEPS + 1):
                factor = 1.0 - (step / FADE_STEPS)
                aid = self.after(FADE_STEP_MS * step, lambda f=factor, pos=positions, cols=colors, br=brightness: self._draw_step(pos, cols, br, f))
                self.anim_ids.append(aid)

    def _draw_step(self, positions, colors, brightness, factor):
        # Remove previous lamps, keep prompt
        self.canvas.delete("lamp")
        for i, pos in enumerate(positions):
            tx, ty = pos
            base_rgb = COLOR_MAP[colors[i]]
            bfactor = brightness[i]
            rgb = scale_color(base_rgb, bfactor * factor)
            hexcol = rgb_to_hex(rgb)
            x0 = tx - CIRCLE_RADIUS
            y0 = ty - CIRCLE_RADIUS
            x1 = tx + CIRCLE_RADIUS
            y1 = ty + CIRCLE_RADIUS
            self.canvas.create_oval(x0, y0, x1, y1, fill=hexcol, outline=hexcol, tag="lamp")

    def _draw_correct_overlay(self):
        """Draw ring or label showing correct colors over the displayed lamps."""
        positions = self._center_positions(len(self.current_presented))
        for i, pos in enumerate(positions):
            tx, ty = pos
            # ring outline in a warm accent color (green for correct, red for wrong per slot)
            is_correct = (self.current_response[i] == self.current_presented[i])
            ring_color = "#2ecc71" if is_correct else "#e74c3c"
            # ring (slightly larger than lamp)
            r = CIRCLE_RADIUS + 6
            self.canvas.create_oval(tx - r, ty - r, tx + r, ty + r, outline=ring_color, width=2, tag="overlay")
            # also label expected color beneath
            expected_text = f"Expected: {COLOR_NAME[self.current_presented[i]]}"
            self.canvas.create_text(tx, ty + 18, text=expected_text, fill=MUTED_FG, font=FONT_SMALL, tag="overlay")

    # ----------------------------
    # Input Handling
    # ----------------------------
    def _on_key(self, event):
        ch = (event.char or "").upper()
        if ch in HOTKEYS:
            self.register_response(ch)
        elif ch == "\x1b":  # ESC
            self.attributes("-fullscreen", False)

    def register_response(self, code: str):
        if not self.current_presented:
            return
        # find first unanswered slot
        try:
            idx = self.current_response.index(None)
        except ValueError:
            # all answered
            return
        self.current_response[idx] = code
        now = time.perf_counter()
        self.current_rts[idx] = now - self.trial_start_time

        # small feedback text
        self._flash_response_feedback(idx, code)

        # if all answered, finalize
        if all(r is not None for r in self.current_response):
            if self.timeout_id:
                try:
                    self.after_cancel(self.timeout_id)
                except Exception:
                    pass
                self.timeout_id = None
            self._finalize_trial()

    def _flash_response_feedback(self, slot: int, code: str):
        positions = self._center_positions(len(self.current_presented))
        tx, ty = positions[slot]
        text = f"{'Left' if (slot == 0 and len(self.current_presented) == 2) else ('Right' if (slot == 1 and len(self.current_presented) == 2) else '')} {COLOR_NAME[code]}"
        tid = self.canvas.create_text(tx, ty - 22, text=text, fill=ACCENT, font=FONT_SMALL, tag="feedback")
        self.after(420, lambda: self.canvas.delete(tid))

    # ----------------------------
    # Utilities: cancel scheduled callbacks
    # ----------------------------
    def _cancel_pending(self):
        for aid in self.anim_ids:
            try:
                self.after_cancel(aid)
            except Exception:
                pass
        self.anim_ids.clear()
        if self.timeout_id:
            try:
                self.after_cancel(self.timeout_id)
            except Exception:
                pass
            self.timeout_id = None

    # ----------------------------
    # Summary & Save
    # ----------------------------
    def _compute_summary(self):
        total_trials = len(self.results)
        total_signals = 0
        correct_signals = 0
        rt_sum = 0.0
        rt_count = 0
        for rec in self.results:
            total_signals += len(rec.presented)
            for ok, rt in zip(rec.correct, rec.reaction_times):
                if ok:
                    correct_signals += 1
                if rt is not None:
                    rt_sum += rt
                    rt_count += 1
        accuracy = (correct_signals / total_signals * 100) if total_signals else 0.0
        avg_rt = (rt_sum / rt_count) if rt_count else None
        return {
            "total_trials": total_trials,
            "total_signals": total_signals,
            "correct_signals": correct_signals,
            "accuracy": accuracy,
            "avg_rt": avg_rt
        }

    def show_summary(self):
        s = self._compute_summary()
        avg_rt_str = f"{s['avg_rt']:.3f} s" if s['avg_rt'] is not None else "N/A"
        msg = (
            f"Trials completed: {s['total_trials']}\n"
            f"Signals shown: {s['total_signals']}\n"
            f"Correct signals: {s['correct_signals']}\n"
            f"Accuracy: {s['accuracy']:.1f}%\n"
            f"Average reaction time: {avg_rt_str}\n\n"
            "Save results to CSV?"
        )
        if messagebox.askyesno("Test Summary", msg):
            self.save_results()

    def save_results(self):
        if not self.results:
            messagebox.showinfo("No data", "No results to save.")
            return
        path = filedialog.asksaveasfilename(defaultextension=".csv",
                                            filetypes=[("CSV files", "*.csv")],
                                            title="Save results")
        if not path:
            return
...         try:
...             with open(path, "w", newline="", encoding="utf-8") as f:
...                 w = csv.writer(f)
...                 w.writerow([
...                     "trial_index",
...                     "presented",
...                     "presented_count",
...                     "response",
...                     "correct_each",
...                     "reaction_times",
...                     "timed_out",
...                     "instructor_mode_at_trial"
...                 ])
...                 for idx, rec in enumerate(self.results):
...                     # We record whether Instructor Mode was on at file save time (convenient). If you prefer per-trial recording, extend TrialRecord.
...                     presented = " ".join(rec.presented)
...                     response = " ".join([r if r is not None else "" for r in rec.response])
...                     correct = " ".join(["1" if c else "0" for c in rec.correct])
...                     rts = " ".join([f"{rt:.3f}" if rt is not None else "" for rt in rec.reaction_times])
...                     w.writerow([rec.trial_index, presented, len(rec.presented), response, correct, rts, rec.timed_out, self.instructor_var.get()])
...             messagebox.showinfo("Saved", f"Results saved to:\n{path}")
...         except Exception as e:
...             messagebox.showerror("Save error", f"Failed to save results:\n{e}")
... 
... # ----------------------------
... # Run the application
... # ----------------------------
... def main():
...     app = LanternApp()
...     app.mainloop()
... 
... if __name__ == "__main__":
...     main()
... 
SyntaxError: multiple statements found while compiling a single statement
