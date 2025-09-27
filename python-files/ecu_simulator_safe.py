
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import shutil
import os
import time
from datetime import datetime

"""
ECU Simulator - Safe Batch Tool
This script is a simulation-only tool. It DOES NOT open serial ports or write to real ECU devices.
It operates on local files (bin/fash files) to create backups and "simulated" modified files
that are clearly labeled as SIMULATION. Use it to automate backups and to produce placeholder
"modified" files for testing workflows.

How to run:
1. Install Python 3.8+ from python.org (if not installed).
2. Save this file and run: python ecu_simulator_safe.py
3. Choose input files (your .bin/.bin files) and an output folder.
4. Click "Run Simulation" to create backups and simulated modified files.

This tool was prepared as a safe, non-destructive assistant for testing and organization.
"""

APP_TITLE = "ECU Batch Simulator - Safe (No ECU, No Changes)"

class ECUSimulatorSafe:
    def __init__(self, root):
        self.root = root
        self.root.title(APP_TITLE)
        self.root.geometry("820x540")
        self.files = []
        self.out_dir = ""
        self.setup_ui()

    def setup_ui(self):
        frm = ttk.Frame(self.root, padding=10)
        frm.pack(fill="both", expand=True)

        title = ttk.Label(frm, text=APP_TITLE, font=("Segoe UI", 14, "bold"))
        title.pack(pady=(0,10))

        btn_frame = ttk.Frame(frm)
        btn_frame.pack(fill="x", pady=5)

        ttk.Button(btn_frame, text="Import ECU files", command=self.import_files).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Choose output folder", command=self.choose_output_folder).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Run Simulation (Backup + Simulated Patch)", command=self.run_simulation).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Open output folder", command=self.open_output_folder).pack(side="left", padx=5)

        opts_frame = ttk.LabelFrame(frm, text="Options", padding=8)
        opts_frame.pack(fill="x", pady=8)

        self.add_timestamp = tk.BooleanVar(value=True)
        ttk.Checkbutton(opts_frame, text="Append timestamp to outputs", variable=self.add_timestamp).pack(side="left", padx=8)

        self.create_report = tk.BooleanVar(value=True)
        ttk.Checkbutton(opts_frame, text="Create a JSON report for the batch", variable=self.create_report).pack(side="left", padx=8)

        list_frame = ttk.LabelFrame(frm, text="Imported files", padding=8)
        list_frame.pack(fill="both", expand=True, pady=6)

        self.listbox = tk.Listbox(list_frame, height=12)
        self.listbox.pack(side="left", fill="both", expand=True)
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.listbox.yview)
        scrollbar.pack(side="right", fill="y")
        self.listbox.config(yscrollcommand=scrollbar.set)

        log_frame = ttk.LabelFrame(frm, text="Log", padding=8)
        log_frame.pack(fill="both", expand=True, pady=6)

        self.log_text = tk.Text(log_frame, height=8, font=("Consolas",10))
        self.log_text.pack(fill="both", expand=True)
        self.log("Ready. Import ECU files (BIN/HEX) and choose an output folder.")

    def import_files(self):
        paths = filedialog.askopenfilenames(
            title="Select ECU files to import",
            filetypes=[("BIN files","*.bin;*.BIN;*.hex;*.HEX;*.img"), ("All files","*.*")]
        )
        if not paths:
            return
        self.files = list(paths)
        self.listbox.delete(0, tk.END)
        for p in self.files:
            self.listbox.insert(tk.END, p)
        self.log(f"Imported {len(self.files)} files.")

    def choose_output_folder(self):
        d = filedialog.askdirectory(title="Choose output folder (will store backups and simulations)")
        if not d:
            return
        self.out_dir = d
        self.log(f"Output folder set: {self.out_dir}")

    def open_output_folder(self):
        if not self.out_dir:
            messagebox.showwarning("Warning", "Output folder not set.")
            return
        try:
            if os.name == 'nt':
                os.startfile(self.out_dir)
            else:
                # cross-platform fallback
                import subprocess, shlex
                subprocess.Popen(['xdg-open', self.out_dir])
        except Exception as e:
            messagebox.showerror("Error", f"Cannot open folder: {e}")

    def run_simulation(self):
        if not self.files:
            messagebox.showwarning("Warning", "No ECU files imported.")
            return
        if not self.out_dir:
            messagebox.showwarning("Warning", "Output folder not chosen.")
            return

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S") if self.add_timestamp.get() else ""
        report = {"timestamp": datetime.now().isoformat(), "files": []}

        for f in self.files:
            try:
                base = os.path.basename(f)
                name, ext = os.path.splitext(base)
                # backup
                backup_name = f"{name}_backup{('_'+timestamp) if timestamp else ''}{ext or '.bin'}"
                backup_path = os.path.join(self.out_dir, backup_name)
                shutil.copy2(f, backup_path)
                self.log(f"Backup created: {backup_name}")

                # simulated modified file
                sim_name = f"{name}_SIMULATED_noECU{('_'+timestamp) if timestamp else ''}{ext or '.bin'}"
                sim_path = os.path.join(self.out_dir, sim_name)
                with open(f, "rb") as src, open(sim_path, "wb") as dst:
                    # write a clear header so it's obvious this is a simulation
                    header = (f"SIMULATED_PATCH: EGR/LAMBDA_DISABLED - GENERATED {datetime.now().isoformat()}\n").encode('utf-8')
                    dst.write(header)
                    dst.write(src.read())
                self.log(f"Simulated file created: {sim_name}")

                report["files"].append({
                    "original": f,
                    "backup": backup_path,
                    "simulated": sim_path
                })

            except Exception as e:
                self.log(f"Error processing {f}: {e}")

        # create JSON report if requested
        if self.create_report.get():
            try:
                import json
                rep_name = f"simulation_report{('_'+timestamp) if timestamp else ''}.json"
                rep_path = os.path.join(self.out_dir, rep_name)
                with open(rep_path, "w", encoding='utf-8') as rf:
                    json.dump(report, rf, indent=2, ensure_ascii=False)
                self.log(f"Report saved: {rep_name}")
            except Exception as e:
                self.log(f"Failed to save report: {e}")

        messagebox.showinfo("Done", f"Simulation completed. Outputs saved to:\n{self.out_dir}")
        self.open_output_folder()

    def log(self, msg):
        ts = datetime.now().strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{ts}] {msg}\n")
        self.log_text.see(tk.END)


if __name__ == "__main__":
    root = tk.Tk()
    style = ttk.Style(root)
    try:
        style.theme_use('clam')
    except:
        pass
    app = ECUSimulatorSafe(root)
    root.mainloop()
