#!/usr/bin/env python3
\"\"\"SlotReelCapture GUI (tkinter)
Simple GUI wrapper for the console capture script. Allows selecting ROI, templates folder,
screenshot file, and starting capture. Designed to be compiled with PyInstaller.
\"\"\"
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
from pathlib import Path
import threading, subprocess, sys, os, json

THIS_DIR = Path(__file__).resolve().parent

DEFAULT_OUT = "spins_log.csv"
DEFAULT_KEYMAP = "symbol_keymap.json"

def run_capture(args_list, log_widget, on_done=None):
    try:
        # Run the console capture script (bundled alongside)
        script = THIS_DIR / "SlotReelCapture" / "slot_reel_capture.py"
        if not script.exists():
            log_widget.insert(tk.END, "Error: backend script not found.\n")
            return
        cmd = [sys.executable, str(script)] + args_list
        log_widget.insert(tk.END, "Running: " + " ".join(cmd) + "\n")
        log_widget.see(tk.END)
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
        for line in p.stdout:
            log_widget.insert(tk.END, line)
            log_widget.see(tk.END)
        p.wait()
        if on_done:
            on_done(p.returncode)
    except Exception as e:
        log_widget.insert(tk.END, f"Exception: {e}\\n")
        log_widget.see(tk.END)

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("SlotReelCapture GUI")
        self.geometry("700x560")
        self.resizable(False, False)
        self.create_widgets()

    def create_widgets(self):
        frm = tk.Frame(self); frm.pack(fill=tk.X, padx=10, pady=6)

        tk.Label(frm, text="Reels:").grid(row=0, column=0, sticky="w")
        self.reels_var = tk.IntVar(value=5)
        tk.Entry(frm, textvariable=self.reels_var, width=6).grid(row=0, column=1, sticky="w")

        tk.Label(frm, text="ROI (X,Y,W,H):").grid(row=0, column=2, sticky="w", padx=(10,0))
        self.roi_entry = tk.Entry(frm, width=20)
        self.roi_entry.insert(0, "100,100,800,300")
        self.roi_entry.grid(row=0, column=3, sticky="w")

        tk.Label(frm, text="Templates folder:").grid(row=1, column=0, sticky="w", pady=(8,0))
        self.templates_entry = tk.Entry(frm, width=50)
        self.templates_entry.grid(row=1, column=1, columnspan=3, sticky="w", padx=(0,6), pady=(8,0))
        tk.Button(frm, text="Browse", command=self.browse_templates).grid(row=1, column=4, padx=4, pady=(8,0))

        tk.Label(frm, text="From image (optional):").grid(row=2, column=0, sticky="w", pady=(8,0))
        self.image_entry = tk.Entry(frm, width=50)
        self.image_entry.grid(row=2, column=1, columnspan=3, sticky="w", padx=(0,6), pady=(8,0))
        tk.Button(frm, text="Browse", command=self.browse_image).grid(row=2, column=4, padx=4, pady=(8,0))

        tk.Label(frm, text="Spin count:").grid(row=3, column=0, sticky="w", pady=(8,0))
        self.spin_count = tk.IntVar(value=10)
        tk.Entry(frm, textvariable=self.spin_count, width=8).grid(row=3, column=1, sticky="w", pady=(8,0))

        tk.Label(frm, text="Out CSV:").grid(row=3, column=2, sticky="w", padx=(10,0))
        self.out_entry = tk.Entry(frm, width=20)
        self.out_entry.insert(0, DEFAULT_OUT)
        self.out_entry.grid(row=3, column=3, sticky="w", pady=(8,0))

        tk.Button(frm, text="Start Capture", command=self.start_capture, bg="#4CAF50", fg="white").grid(row=4, column=0, pady=(12,0))
        tk.Button(frm, text="Stop (not implemented)", command=lambda: messagebox.showinfo("Stop","Stop not implemented in GUI wrapper")).grid(row=4, column=1, pady=(12,0))

        # Log text area
        self.log = scrolledtext.ScrolledText(self, height=20)
        self.log.pack(fill=tk.BOTH, padx=10, pady=10)
        self.log.insert(tk.END, "Ready. Provide ROI and templates, or a single image, then click Start Capture.\\n")

    def browse_templates(self):
        d = filedialog.askdirectory(title="Select templates folder")
        if d:
            self.templates_entry.delete(0, tk.END)
            self.templates_entry.insert(0, d)

    def browse_image(self):
        f = filedialog.askopenfilename(title="Select screenshot image", filetypes=[("PNG","*.png"),("JPG","*.jpg;*.jpeg"),("All","*.*")])
        if f:
            self.image_entry.delete(0, tk.END)
            self.image_entry.insert(0, f)

    def start_capture(self):
        try:
            reels = int(self.reels_var.get())
            spin_count = int(self.spin_count.get())
        except Exception as e:
            messagebox.showerror("Input error", "Reels and spin count must be integers.")
            return
        args = ["--reels", str(reels), "--spin-count", str(spin_count), "--out-csv", self.out_entry.get(), "--keymap-json", THIS_DIR+"/symbol_keymap.json"]
        roi = self.roi_entry.get().strip()
        if roi:
            try:
                parts = [int(x.strip()) for x in roi.split(",")]
                if len(parts) == 4:
                    args += ["--roi"] + [str(x) for x in parts]
            except:
                messagebox.showerror("ROI error", "ROI must be four integers: X,Y,W,H")
                return
        if self.templates_entry.get().strip():
            args += ["--templates", self.templates_entry.get().strip()]
        if self.image_entry.get().strip():
            args += ["--from-image", self.image_entry.get().strip()]

        # run in thread so GUI doesn't block
        t = threading.Thread(target=run_capture, args=(args, self.log, self.on_done))
        t.daemon = True
        t.start()

    def on_done(self, rc):
        self.log.insert(tk.END, f"Capture finished (return code {rc}).\\n")
        self.log.see(tk.END)

if __name__ == '__main__':
    App().mainloop()
