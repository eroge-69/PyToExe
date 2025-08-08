
#!/usr/bin/env python3
"""
baccarat_gui.py
A simple Tkinter GUI for the "Flexible Trend Reversal Strategy".
- Click "Banker" or "Player" to record results round-by-round.
- The app predicts the next round, displays history, and computes accuracy every 3 rounds.
- Optional Martingale calculator (base bet, max steps).
- Save / load history to CSV.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import csv
from datetime import datetime

# --- Strategy logic ---
def analyze_trend(history):
    """
    Flexible Trend Reversal Strategy (simple implementation):
    - Use up to last 10 rounds
    - If the last 3 are the same, predict continuation of that run
    - Else, if there was a recent run (>=2) at the end, follow it
    - Else, predict the last result
    History: list of 'B' or 'P' (strings)
    Returns: predicted 'B' or 'P'
    """
    if not history:
        return 'B'  # default starting prediction

    n = min(10, len(history))
    recent = history[-n:]
    # check last 3 same
    if len(recent) >= 3 and recent[-1] == recent[-2] == recent[-3]:
        return recent[-1]
    # check end run length
    run_val = recent[-1]
    run_len = 1
    for x in reversed(recent[:-1]):
        if x == run_val:
            run_len += 1
        else:
            break
    if run_len >= 2:
        return run_val
    # fallback: predict last
    return recent[-1]

# --- File helpers ---
def save_history_to_csv(path, history, predictions, results, timestamps):
    with open(path, 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(['index','timestamp','prediction','result'])
        for i, (t,p,res) in enumerate(zip(timestamps, predictions, results), start=1):
            w.writerow([i, t, p, res])

def load_history_from_csv(path):
    hist = []
    preds = []
    results = []
    times = []
    with open(path, newline='', encoding='utf-8') as f:
        r = csv.reader(f)
        header = next(r, None)
        for row in r:
            if len(row) >= 4:
                _, t, p, res = row[:4]
                preds.append(p)
                results.append(res)
                times.append(t)
                hist.append(res)
    return hist, preds, results, times

# --- GUI ---
class BaccaratGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Flexible Trend Reversal Strategy - Baccarat")
        self.geometry("760x520")
        self.resizable(False, False)

        # Data
        # Default history pre-filled from the conversation (26 rounds)
        self.history = list("BBBPBBPPBPPBPBBPBBPBBPBPPP".upper())  # default; editable by user
        self.predictions = []   # predictions made (for saved log)
        self.results = []       # actual results logged
        self.timestamps = []

        # Stats
        self.correct_count = 0
        self.total_checked = 0

        # Martingale settings
        self.base_bet = tk.DoubleVar(value=10.0)
        self.max_steps = tk.IntVar(value=6)
        self.bankroll = tk.DoubleVar(value=1000.0)

        self.create_widgets()
        self.redraw_all()

    def create_widgets(self):
        # Top frame: History + controls
        top = ttk.Frame(self, padding=8)
        top.pack(fill='x')

        # History display
        hist_frame = ttk.LabelFrame(top, text="History (most recent at right)", padding=8)
        hist_frame.pack(side='left', fill='x', expand=True)

        self.canvas = tk.Canvas(hist_frame, width=520, height=80, bg='white')
        self.canvas.pack(side='top', padx=4, pady=4)
        self.canvas_text = self.canvas.create_text(10, 40, anchor='w', text='', font=('Consolas', 14))

        # Controls
        ctrl_frame = ttk.Frame(top)
        ctrl_frame.pack(side='right', fill='y', padx=8)

        ttk.Label(ctrl_frame, text="Prediction:", font=('Arial', 12, 'bold')).pack(pady=(6,2))
        self.pred_label = ttk.Label(ctrl_frame, text='-', font=('Arial', 20))
        self.pred_label.pack(pady=(0,8))

        btn_frame = ttk.Frame(ctrl_frame)
        btn_frame.pack(pady=6)
        b_btn = ttk.Button(btn_frame, text="Banker (B)", command=lambda: self.record_result('B'), width=12)
        p_btn = ttk.Button(btn_frame, text="Player (P)", command=lambda: self.record_result('P'), width=12)
        b_btn.grid(row=0, column=0, padx=4, pady=4)
        p_btn.grid(row=0, column=1, padx=4, pady=4)

        misc_frame = ttk.Frame(ctrl_frame)
        misc_frame.pack(fill='x', pady=6)
        ttk.Button(misc_frame, text="Undo Last", command=self.undo_last).pack(fill='x', pady=2)
        ttk.Button(misc_frame, text="Reset History", command=self.reset_history).pack(fill='x', pady=2)
        ttk.Button(misc_frame, text="Save CSV", command=self.save_csv).pack(fill='x', pady=2)
        ttk.Button(misc_frame, text="Load CSV", command=self.load_csv).pack(fill='x', pady=2)

        # Middle frame: Stats & Martingale
        mid = ttk.Frame(self, padding=8)
        mid.pack(fill='x', pady=(10,0))

        stats = ttk.LabelFrame(mid, text="Stats", padding=8)
        stats.pack(side='left', fill='both', expand=True, padx=(0,8))
        self.stat_text = tk.Text(stats, width=40, height=8, state='disabled', wrap='word')
        self.stat_text.pack(fill='both', expand=True)

        mg = ttk.LabelFrame(mid, text="Martingale (optional)", padding=8)
        mg.pack(side='right', fill='y')
        ttk.Label(mg, text="Base bet:").pack(anchor='w')
        ttk.Entry(mg, textvariable=self.base_bet).pack(fill='x', pady=2)
        ttk.Label(mg, text="Max steps:").pack(anchor='w')
        ttk.Entry(mg, textvariable=self.max_steps).pack(fill='x', pady=2)
        ttk.Label(mg, text="Bankroll:").pack(anchor='w')
        ttk.Entry(mg, textvariable=self.bankroll).pack(fill='x', pady=2)
        ttk.Button(mg, text="Calc Martingale Sequence", command=self.calc_martingale).pack(fill='x', pady=(6,2))

        # Bottom: Log
        bot = ttk.Frame(self, padding=8)
        bot.pack(fill='both', expand=True)
        log_frame = ttk.LabelFrame(bot, text="Log (predictions & results)", padding=8)
        log_frame.pack(fill='both', expand=True)
        self.log_box = tk.Listbox(log_frame, height=8, font=('Consolas', 11))
        self.log_box.pack(side='left', fill='both', expand=True)
        sb = ttk.Scrollbar(log_frame, orient='vertical', command=self.log_box.yview)
        sb.pack(side='right', fill='y')
        self.log_box.config(yscrollcommand=sb.set)

    def redraw_all(self):
        # Update history canvas
        display = ' '.join(self.history)
        self.canvas.itemconfigure(self.canvas_text, text=display)
        # Colorize by drawing colored ovals above text for better readability
        self.canvas.delete('dot')
        x = 10
        y = 40
        for ch in self.history:
            color = '#d9534f' if ch == 'B' else '#0275d8'  # banker red, player blue
            self.canvas.create_oval(x, y-12, x+20, y+8, fill=color, outline='', tags='dot')
            self.canvas.create_text(x+10, y, text=ch, fill='white', font=('Consolas', 10, 'bold'), tags='dot')
            x += 26

        # Prediction
        pred = analyze_trend(self.history)
        self.pred_label.config(text=pred)
        # Update stats and log
        self.update_stats()

    def update_stats(self):
        # Compute accuracy every 3 rounds
        if len(self.results) >= 3:
            # compute last block of 3 (or sliding?) We'll compute cumulative accuracy per 3-record checkpoints
            correct = sum(1 for p, r in zip(self.predictions, self.results) if p == r)
            total = len(self.results)
            self.correct_count = correct
            self.total_checked = total

        # Update stat text
        txt = f"History length: {len(self.history)}\n"
        txt += f"Logged rounds: {len(self.results)}\n"
        txt += f"Correct predictions: {self.correct_count}\n"
        txt += f"Overall accuracy: { (self.correct_count/self.total_checked*100) if self.total_checked>0 else 0:.1f}%\n"
        # show last 10 entries in log
        last_preds = self.predictions[-10:]
        last_res = self.results[-10:]
        txt += "\nLast log entries (most recent last):\n"
        for i, (p, r) in enumerate(zip(last_preds, last_res), start=max(1, len(self.predictions)-len(last_preds)+1)):
            txt += f"{i:02d}. Pred:{p} -> Res:{r} {'✅' if p==r else '❌'}\n"

        self.stat_text.config(state='normal')
        self.stat_text.delete('1.0', 'end')
        self.stat_text.insert('1.0', txt)
        self.stat_text.config(state='disabled')

        # refresh log box
        self.log_box.delete(0, 'end')
        for i, (t, p, r) in enumerate(zip(self.timestamps, self.predictions, self.results), start=1):
            self.log_box.insert('end', f"{i:02d} {t} Pred:{p} Res:{r} {'OK' if p==r else 'NO'}")

    def record_result(self, result):
        # When user clicks Banker or Player
        # Make a prediction first (for recording purpose)
        pred = analyze_trend(self.history)
        # Log prediction and result
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.predictions.append(pred)
        self.results.append(result)
        self.timestamps.append(now)
        # Update counts
        if pred == result:
            self.correct_count += 1
        self.total_checked += 1
        # Append to history and redraw
        self.history.append(result)
        # keep history reasonably sized for display (but strategy uses up to last 10 anyway)
        if len(self.history) > 200:
            self.history = self.history[-200:]
        self.redraw_all()

    def undo_last(self):
        if not self.results:
            messagebox.showinfo("Undo", "ไม่มีผลให้ยกเลิก")
            return
        # remove last logged result and prediction, and remove last history entry
        self.results.pop()
        self.predictions.pop()
        self.timestamps.pop()
        # remove last history entry if it matches (to keep history consistent)
        if self.history:
            self.history.pop()
        # recompute correct_count and total_checked
        # simple recompute
        self.correct_count = sum(1 for p, r in zip(self.predictions, self.results) if p == r)
        self.total_checked = len(self.results)
        self.redraw_all()

    def reset_history(self):
        if not messagebox.askyesno("Reset", "ต้องการรีเซ็ตประวัติทั้งหมดใช่หรือไม่?"):
            return
        self.history = []
        self.predictions = []
        self.results = []
        self.timestamps = []
        self.correct_count = 0
        self.total_checked = 0
        self.redraw_all()

    def save_csv(self):
        path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files","*.csv")])
        if not path:
            return
        save_history_to_csv(path, self.history, self.predictions, self.results, self.timestamps)
        messagebox.showinfo("Saved", f"Saved to {path}")

    def load_csv(self):
        path = filedialog.askopenfilename(filetypes=[("CSV files","*.csv")])
        if not path:
            return
        hist, preds, results, times = load_history_from_csv(path)
        # replace internal data with loaded (simple behavior)
        if messagebox.askyesno("Load", "จะโหลดข้อมูลจากไฟล์และแทนที่ประวัติปัจจุบัน ใช่หรือไม่?"):
            self.history = hist
            self.predictions = preds
            self.results = results
            self.timestamps = times
            self.correct_count = sum(1 for p, r in zip(self.predictions, self.results) if p == r)
            self.total_checked = len(self.results)
            self.redraw_all()

    def calc_martingale(self):
        base = float(self.base_bet.get())
        steps = int(self.max_steps.get())
        seq = []
        stake = base
        for i in range(steps):
            seq.append(round(stake, 2))
            # simple martingale: next stake = (previous stake * 2) + small rounding
            stake = stake * 2
        # Show in a popup
        txt = "Martingale sequence (per step):\n"
        for i, s in enumerate(seq, start=1):
            txt += f"Step {i}: {s}\n"
        total_needed = sum(seq)
        txt += f"\nTotal money needed to cover {steps} steps: {total_needed:.2f}"
        messagebox.showinfo("Martingale", txt)

if __name__ == "__main__":
    app = BaccaratGUI()
    app.mainloop()
