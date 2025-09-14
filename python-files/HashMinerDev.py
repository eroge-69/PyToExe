import tkinter as tk
from tkinter import ttk, messagebox
import random
import time
import threading
import uuid

APP_TITLE = "Hash Miner"
BTC_PER_BLOCK = 0.0005
BTC_TO_USD = 115500.44  # fixed latest price snapshot

class MinerSimulator:
    def __init__(self, root):
        self.root = root
        root.title(APP_TITLE)
        root.geometry("700x560")
        root.configure(bg="#1e1e1e")

        # Mining state
        self.running = False
        self.update_ms = 500
        self.production_scale = 0.001 * 10  # 10x speed
        self.base_success_chance = 0.001
        self.success_chance = self.base_success_chance * self.production_scale
        self.total_btc = 0.0
        self.blocks_found = 0
        self.hashrate = 0.0
        self.start_time = None
        self.elapsed_ms = 0
        self.dev_override = None  # Developer-controlled hashrate

        self._build_ui()
        self._elapsed_updater()

    # --- UI ---
    def _build_ui(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TFrame", background="#1e1e1e")
        style.configure("TLabel", background="#1e1e1e", foreground="white", font=("Segoe UI", 11))
        style.configure("Title.TLabel", font=("Segoe UI", 18, "bold"), foreground="#ffcc00")
        style.configure("Stat.TLabel", font=("Segoe UI", 12, "bold"), foreground="#ffcc00")
        style.configure("Note.TLabel", font=("Segoe UI", 8), foreground="#aaaaaa")
        style.configure("TButton", font=("Segoe UI", 10, "bold"), padding=6, background="#333333", foreground="white")
        style.map("TButton", background=[("active", "#ffcc00")], foreground=[("active", "black")])
        style.configure("TProgressbar", troughcolor="#333333", background="#ffcc00", thickness=18)

        main = ttk.Frame(self.root, padding=16)
        main.pack(fill="both", expand=True)

        ttk.Label(main, text=APP_TITLE, style="Title.TLabel").pack(pady=(0, 15))

        stats_frame = ttk.Frame(main)
        stats_frame.pack(fill="x", pady=8)

        self.hash_lbl = ttk.Label(stats_frame, text="Hashrate: -- TH/s", style="Stat.TLabel")
        self.hash_lbl.grid(row=0, column=0, sticky="w", padx=8, pady=6)

        self.btc_lbl = ttk.Label(stats_frame, text="Total BTC: 0.00000000", style="Stat.TLabel")
        self.btc_lbl.grid(row=0, column=1, sticky="w", padx=8, pady=6)

        self.blocks_lbl = ttk.Label(stats_frame, text="Blocks found: 0", style="Stat.TLabel")
        self.blocks_lbl.grid(row=0, column=2, sticky="w", padx=8, pady=6)

        self.usd_var = tk.StringVar(value="≈ $0.00 USD")
        self.usd_lbl = ttk.Label(main, textvariable=self.usd_var, foreground="#ffcc00")
        self.usd_lbl.pack(pady=(0, 6))

        self.elapsed_var = tk.StringVar(value="Elapsed: 00:00:00")
        ttk.Label(main, textvariable=self.elapsed_var, font=("Segoe UI", 10, "italic"), foreground="#ffcc00").pack(pady=(0, 6))

        self.status_var = tk.StringVar(value="Press Start to mining BTC.")
        self.status_label = ttk.Label(main, textvariable=self.status_var, relief="sunken", anchor="center", foreground="#ffcc00")
        self.status_label.pack(fill="x", pady=(6, 10))

        # Hash stream
        ttk.Label(main, text="Hash Stream:", style="Stat.TLabel").pack(anchor="w", pady=(4, 2))
        self.hash_stream_text = tk.Text(main, height=10, width=80, bg="black", fg="#ffcc00",
                                        font=("Consolas", 10), wrap="none")
        self.hash_stream_text.pack(fill="x", pady=(0, 10))
        self.hash_stream_text.insert("end", "(no activity yet)\n")
        self.hash_stream_text.config(state="disabled")

        # Controls
        ctrl = ttk.Frame(main)
        ctrl.pack(fill="x", pady=6)

        self.toggle_btn = ttk.Button(ctrl, text="▶ Start", command=self.toggle)
        self.toggle_btn.pack(side="left", padx=5)

        dev_btn = ttk.Button(ctrl, text="👨‍💻 Developer Panel", command=self.open_dev_panel)
        dev_btn.pack(side="left", padx=5)

        withdraw_btn = ttk.Button(ctrl, text="💰 Withdraw", command=self.open_withdraw_window)
        withdraw_btn.pack(side="right", padx=5)

        about_btn = ttk.Button(ctrl, text="ℹ About", command=self.open_about_window)
        about_btn.pack(side="right", padx=5)

        ttk.Label(main, text="Made By Aiven Drewry - To Simplify His Life", style="Note.TLabel").pack(side="bottom", pady=8)

    # --- Developer Panel Overlay ---
    def open_dev_panel(self):
        dev_win = tk.Toplevel(self.root)
        dev_win.title("Developer Panel")
        dev_win.geometry("400x300")
        dev_win.configure(bg="#1e1e1e")
        frm = ttk.Frame(dev_win, padding=10)
        frm.pack(fill="both", expand=True)

        ttk.Label(frm, text="Developer Tricks", style="Title.TLabel").pack(pady=(0, 10))

        # Override hashrate
        ttk.Label(frm, text="Override Hashrate (TH/s):", foreground="#ffcc00").pack(anchor="w", pady=(2,2))
        self.dev_hashrate_var = tk.DoubleVar(value=0.0)
        ttk.Scale(frm, from_=0.0, to=500.0, variable=self.dev_hashrate_var, orient="horizontal").pack(fill="x", pady=(0,5))
        ttk.Button(frm, text="Set Hashrate", command=self.set_dev_hashrate).pack(pady=(0,5))

        # Multiply earnings
        ttk.Label(frm, text="Multiply next tick earnings:", foreground="#ffcc00").pack(anchor="w", pady=(2,2))
        self.multiplier_var = tk.DoubleVar(value=1.0)
        ttk.Entry(frm, textvariable=self.multiplier_var).pack(pady=(0,5))
        ttk.Button(frm, text="Apply Multiplier", command=self.apply_multiplier).pack(pady=(0,5))

        # Add BTC instantly
        ttk.Label(frm, text="Add BTC instantly:", foreground="#ffcc00").pack(anchor="w", pady=(2,2))
        self.add_btc_var = tk.DoubleVar(value=0.0)
        ttk.Entry(frm, textvariable=self.add_btc_var).pack(pady=(0,5))
        ttk.Button(frm, text="Add BTC", command=self.add_btc).pack(pady=(0,5))

        # Force block find
        ttk.Button(frm, text="Force Block Find", command=self.force_block).pack(pady=(5,5))

        # Reset stats
        ttk.Button(frm, text="Reset Stats", command=self.reset_stats).pack(pady=(5,5))

    # --- Developer Methods ---
    def set_dev_hashrate(self):
        val = self.dev_hashrate_var.get()
        self.dev_override = val if val > 0 else None
        self.status_var.set(f"Developer hashrate set to {val:.2f} TH/s" if val > 0 else "Developer override cleared")

    def apply_multiplier(self):
        self.production_scale *= self.multiplier_var.get()
        self.status_var.set(f"Earnings multiplied by {self.multiplier_var.get():.2f}")

    def add_btc(self):
        self.total_btc += self.add_btc_var.get()
        self.update_ui()
        self.status_var.set(f"Added {self.add_btc_var.get():.8f} BTC")

    def force_block(self):
        self.blocks_found += 1
        self.total_btc += BTC_PER_BLOCK * self.production_scale
        self.update_ui()
        self.status_var.set("Forced a block find!")

    def reset_stats(self):
        self.total_btc = 0.0
        self.blocks_found = 0
        self.hashrate = 0.0
        self.production_scale = 0.001 * 10
        self.dev_override = None
        self.update_ui()
        self.status_var.set("Stats reset")

    # --- Core Controls ---
    def toggle(self):
        if self.running:
            self.stop()
        else:
            self.start()

    def start(self):
        if self.running: return
        self.running = True
        self.toggle_btn.config(text="■ Stop")
        if self.start_time is None:
            self.start_time = time.time() - (self.elapsed_ms / 1000.0)
        self.status_var.set("Mining started... good luck!")
        self._schedule_tick()
        self._schedule_hash_stream()

    def stop(self):
        if not self.running: return
        self.running = False
        if self.start_time is not None:
            self.elapsed_ms = int((time.time() - self.start_time) * 1000)
            self.start_time = None
        self.toggle_btn.config(text="▶ Start")
        self.status_var.set("Paused.")

    def _schedule_tick(self):
        if not self.running: return
        self.root.after(self.update_ms, self._tick)

    def _tick(self):
        if not self.running: return
        base_hr = 50.0
        jitter = random.uniform(-5.0, 5.0)
        self.hashrate = self.dev_override if self.dev_override else max(0.1, base_hr + jitter)
        produced = (self.hashrate / 1000.0) * (self.update_ms / 1000.0) * 0.0001 * self.production_scale
        self.total_btc += produced
        if random.random() < self.success_chance:
            self.blocks_found += 1
            reward = BTC_PER_BLOCK * self.production_scale
            self.total_btc += reward
            self._flash_message(f"🎉 Block found! +{reward:.8f} BTC")
        else:
            self.status_var.set(f"Mined {produced:.8f} BTC this tick")
        self.update_ui()
        self._schedule_tick()

    def _flash_message(self, text, duration_ms=1600):
        self.status_var.set(text)
        def restore():
            if self.running: self.status_var.set("Mining...")
            else: self.status_var.set("Paused.")
        self.root.after(duration_ms, restore)

    def _elapsed_updater(self):
        elapsed = int((time.time() - self.start_time) * 1000) + self.elapsed_ms if self.running and self.start_time else self.elapsed_ms
        total_seconds = elapsed // 1000
        hrs, mins, secs = total_seconds // 3600, (total_seconds % 3600) // 60, total_seconds % 60
        self.elapsed_var.set(f"Elapsed: {hrs:02d}:{mins:02d}:{secs:02d}")
        self.root.after(250, self._elapsed_updater)

    def _schedule_hash_stream(self):
        if not self.running: return
        fake_hash = uuid.uuid4().hex * 2
        display_hash = "0x" + fake_hash[:62]
        self.hash_stream_text.config(state="normal")
        self.hash_stream_text.insert("end", display_hash + "\n")
        lines = self.hash_stream_text.get("1.0", "end-1c").split("\n")
        if len(lines) > 10:
            self.hash_stream_text.delete("1.0", f"{len(lines)-10}.0")
        self.hash_stream_text.see("end")
        self.hash_stream_text.config(state="disabled")
        self.root.after(20, self._schedule_hash_stream)

    # --- Withdraw ---
    def open_withdraw_window(self):
        win = tk.Toplevel(self.root)
        win.title("Withdraw BTC")
        win.geometry("520x300")
        win.configure(bg="#1e1e1e")
        frm = ttk.Frame(win, padding=12)
        frm.pack(fill="both", expand=True)

        ttk.Label(frm, text="Withdraw BTC Here", style="Title.TLabel").pack(pady=(0, 8))
        bal_var = tk.StringVar(value=f"Available balance: {self.total_btc:.8f} BTC")
        ttk.Label(frm, textvariable=bal_var, foreground="#ffcc00").pack(pady=(6,6))

        ttk.Label(frm, text="Amount to withdraw (BTC):", foreground="#ffcc00").pack(anchor="w")
        amount_entry = ttk.Entry(frm)
        amount_entry.pack(fill="x", pady=(0,6))

        ttk.Label(frm, text="Destination address:", foreground="#ffcc00").pack(anchor="w")
        addr_entry = ttk.Entry(frm)
        addr_entry.pack(fill="x", pady=(0,6))

        btn_frame = ttk.Frame(frm)
        btn_frame.pack(fill="x", pady=10)
        send_btn = ttk.Button(btn_frame, text="Send", command=lambda: self._do_fake_withdraw(win, bal_var, amount_entry, addr_entry, send_btn))
        send_btn.pack(side="right", padx=5)
        ttk.Button(btn_frame, text="Cancel", command=win.destroy).pack(side="right", padx=5)

    def _do_fake_withdraw(self, win, bal_var, amount_entry, addr_entry, send_btn):
        try: amt = float(amount_entry.get().strip())
        except: return messagebox.showerror("Invalid", "Please enter a correct BTC amount")
        if amt <= 0 or amt > self.total_btc: return messagebox.showerror("Error", "Invalid or insufficient amount")
        addr = addr_entry.get().strip()
        if not addr: return messagebox.showerror("Error", "Please enter a BTC address")

        send_btn.config(state="disabled")
        proc = tk.Toplevel(self.root)
        proc.title("Sending (simulated)")
        proc.geometry("420x120")
        pf = ttk.Frame(proc, padding=12)
        pf.pack(fill="both", expand=True)
        ttk.Label(pf, text="Sending transaction...", font=("Segoe UI", 10), foreground="#ffcc00").pack(pady=(0,8))
        prog = ttk.Progressbar(pf, mode="determinate", maximum=100)
        prog.pack(fill="x", pady=(0,8))

        def run_simulation():
            for i in range(31):
                time.sleep(0.05)
                self.root.after(0, prog.configure, {"value": int(i/30*100)})
            txid = "0x" + uuid.uuid4().hex + uuid.uuid4().hex[:28]
            self.total_btc -= amt
            self.root.after(0, self._finish_withdraw, proc, win, bal_var, amt, addr, txid, send_btn)
        threading.Thread(target=run_simulation, daemon=True).start()

    def _finish_withdraw(self, proc, win, bal_var, amount, addr, txid, send_btn):
        proc.destroy()
        bal_var.set(f"Available balance: {self.total_btc:.8f} BTC")
        self.update_ui()
        messagebox.showinfo("Send Complete", f"Transaction sent!\n\nTxID: {txid}\nAmount: {amount:.8f} BTC\nTo: {addr}")
        send_btn.config(state="normal")
        win.destroy()

    # --- About ---
    def open_about_window(self):
        about = tk.Toplevel(self.root)
        about.title("About Developer")
        about.geometry("320x160")
        about.configure(bg="#1e1e1e")
        frm = ttk.Frame(about, padding=20)
        frm.pack(fill="both", expand=True)
        ttk.Label(frm, text="About Developer", style="Title.TLabel").pack(pady=(0,10))
        ttk.Label(frm, text="Aiven's the best!", font=("Segoe UI", 11), foreground="#ffcc00").pack(pady=(0,10))
        ttk.Button(frm, text="Close", command=about.destroy).pack(pady=10)

    # --- UI Update ---
    def update_ui(self):
        self.btc_lbl.config(text=f"Total BTC: {self.total_btc:.8f}")
        self.blocks_lbl.config(text=f"Blocks found: {self.blocks_found}")
        self.hash_lbl.config(text=f"Hashrate: {self.hashrate:.2f} TH/s")
        self.usd_var.set(f"≈ ${self.total_btc * BTC_TO_USD:,.2f} USD")


def main():
    root = tk.Tk()
    app = MinerSimulator(root)
    root.mainloop()


if __name__ == "__main__":
    main()
