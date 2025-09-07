"""
stego_launcher.py

Simple GUI that extracts an appended hidden file from a PNG (marker: b"STEGOFILE")
and optionally runs it locally (ONLY if you choose to).

Usage:
    python stego_launcher.py

Dependencies:
    - Python 3.x
    - (No external packages required; uses tkinter and subprocess included in stdlib)
"""

import os
import sys
import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess

MARKER = b"STEGOFILE"

def find_hidden_file(data):
    """Return (ext, hidden_bytes) or (None, None) if not found."""
    idx = data.find(MARKER)
    if idx == -1:
        return None, None
    start = idx + len(MARKER)
    # extension is stored as bytes up to a null byte
    end = data.find(b"\0", start)
    if end == -1:
        return None, None
    ext = data[start:end].decode(errors="ignore")
    hidden = data[end + 1:]
    return ext, hidden

def extract_to_folder(stego_path, out_folder):
    with open(stego_path, "rb") as f:
        data = f.read()

    ext, hidden = find_hidden_file(data)
    if ext is None:
        raise ValueError("No hidden file found (marker missing or malformed).")

    # make a safe filename
    base_name = os.path.splitext(os.path.basename(stego_path))[0]
    out_name = f"{base_name}_extracted{ext}"
    out_path = os.path.join(out_folder, out_name)

    # if exists, add numeric suffix
    if os.path.exists(out_path):
        i = 1
        while True:
            candidate = os.path.join(out_folder, f"{base_name}_extracted_{i}{ext}")
            if not os.path.exists(candidate):
                out_path = candidate
                break
            i += 1

    with open(out_path, "wb") as out_f:
        out_f.write(hidden)

    return out_path

# ----------------- GUI -----------------

class StegoLauncher(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Stego Launcher - Extract & (optionally) Run hidden file")
        self.geometry("600x260")
        self.resizable(False, False)

        self.stego_path = None
        self.extracted_path = None

        # Widgets
        tk.Label(self, text="Hidden-file extractor for PNG (marker: STEGOFILE)", font=("Segoe UI", 11)).pack(pady=(10,6))

        frame = tk.Frame(self)
        frame.pack(fill="x", padx=12)

        self.path_var = tk.StringVar(value="No file selected")
        tk.Entry(frame, textvariable=self.path_var, state="readonly", width=70).pack(side="left", padx=(0,6))
        tk.Button(frame, text="Select PNG...", command=self.select_file).pack(side="left")

        btn_frame = tk.Frame(self)
        btn_frame.pack(fill="x", padx=12, pady=(12,0))

        tk.Button(btn_frame, text="Extract to folder...", command=self.extract_file, width=18).pack(side="left")
        self.run_var = tk.BooleanVar(value=False)
        tk.Checkbutton(btn_frame, text="Run after extract (unsafe)", variable=self.run_var).pack(side="left", padx=(12,0))

        tk.Button(btn_frame, text="Select output folder", command=self.choose_output_folder).pack(side="right")

        self.output_folder = os.path.expanduser("~")
        tk.Label(self, text=f"Output folder: {self.output_folder}", anchor="w", fg="gray50").pack(fill="x", padx=12, pady=(8,0))

        self.info_text = tk.Text(self, height=6, wrap="word")
        self.info_text.pack(fill="both", padx=12, pady=8)
        self.info_text.insert("1.0", "Instructions:\n1) Click 'Select PNG...' and choose a PNG that contains a hidden file (appended marker).\n2) Click 'Extract to folder...' to extract the hidden file to the output folder.\n3) Optionally check 'Run after extract' to execute the extracted file (only run files you trust).\n\nWarning: Running unknown executables is dangerous. The program will ask for confirmation before running anything.\n")
        self.info_text.config(state="disabled")

    def select_file(self):
        p = filedialog.askopenfilename(title="Select PNG with hidden file", filetypes=[("PNG images", "*.png"), ("All files", "*.*")])
        if p:
            self.stego_path = p
            self.path_var.set(p)
            self.info(f"Selected: {p}")

    def choose_output_folder(self):
        p = filedialog.askdirectory(title="Choose output folder", initialdir=self.output_folder)
        if p:
            self.output_folder = p
            # update label
            for w in self.winfo_children():
                pass
            # crude update: recreate small label by destroying and re-adding; simpler to just update the label text if we saved it earlier.
            # Instead, find the label and update:
            for child in self.pack_slaves():
                pass
            # set window label by searching for it
            # easier: set by destroying and re-adding bottom label — but to keep code short, simply update text widget too:
            self.info(f"Output folder set to: {p}")

    def info(self, text):
        # append to info box
        self.info_text.config(state="normal")
        self.info_text.insert("end", "\n" + text)
        self.info_text.see("end")
        self.info_text.config(state="disabled")

    def extract_file(self):
        if not self.stego_path:
            messagebox.showwarning("No file", "Please select a PNG file first.")
            return

        try:
            with open(self.stego_path, "rb") as f:
                data = f.read()
        except Exception as e:
            messagebox.showerror("Error", f"Failed reading file:\n{e}")
            return

        ext, hidden = find_hidden_file(data)
        if ext is None:
            messagebox.showinfo("No hidden file", "No embedded file found (marker missing or malformed).")
            return

        # confirm extraction
        resp = messagebox.askyesno("Confirm extraction", f"Hidden file type detected: {ext}\nExtract to folder:\n{self.output_folder}\n\nProceed?")
        if not resp:
            return

        try:
            out_path = extract_to_folder(self.stego_path, self.output_folder)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to extract:\n{e}")
            return

        self.extracted_path = out_path
        self.info(f"Extracted to: {out_path}")
        messagebox.showinfo("Done", f"Hidden file extracted:\n{out_path}")

        # optionally run
        if self.run_var.get():
            # double confirm
            run_confirm = messagebox.askyesno("Run file?", f"Do you really want to RUN the extracted file?\n\n{out_path}\n\nOnly run files you trust.")
            if run_confirm:
                try:
                    # On Windows, use 'start' via shell to open an associated program or run directly.
                    if sys.platform.startswith("win"):
                        # Use subprocess.Popen without shell for direct execution
                        subprocess.Popen([out_path], shell=False)
                    else:
                        # Unix-like: try to make it executable & run
                        os.chmod(out_path, 0o755)
                        subprocess.Popen([out_path])
                    self.info(f"Process started: {out_path}")
                except Exception as e:
                    messagebox.showerror("Run failed", f"Failed to run the extracted file:\n{e}")
            else:
                self.info("Run cancelled by user.")

if __name__ == "__main__":
    app = StegoLauncher()
    app.mainloop()
