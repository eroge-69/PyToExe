import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import subprocess
import threading
import sys


class PyToExeBuilder:
    def __init__(self, root):
        self.root = root
        root.title("Python → EXE Compiler")
        root.geometry("500x350")
        root.resizable(False, False)

        self.script = tk.StringVar()
        self.icon = tk.StringVar()
        self.threads = tk.IntVar(value=4)

        ttk.Button(
            root,
            text="Select Script (.py)",
            command=self.select_script).pack(
            pady=10)
        ttk.Label(root, textvariable=self.script).pack()

        ttk.Button(
            root,
            text="Browse Icon (.ico)",
            command=self.select_icon).pack(
            pady=10)
        ttk.Label(root, textvariable=self.icon).pack()

        thread_frame = ttk.LabelFrame(root, text="Build Threads")
        thread_frame.pack(pady=10)
        for n in [2, 4, 6, 8, 12]:
            ttk.Radiobutton(
                thread_frame,
                text=f"{n} Jobs",
                value=n,
                variable=self.threads).pack(
                side=tk.LEFT,
                padx=5)

        self.progress = ttk.Progressbar(
            root, orient="horizontal", length=400, mode="determinate")
        self.progress.pack(pady=20)

        ttk.Button(
            root,
            text="Start Building EXE",
            command=self.start_build).pack(
            pady=10)

    def select_script(self):
        f = filedialog.askopenfilename(filetypes=[("Python Files", "*.py")])
        if f:
            self.script.set(f)

    def select_icon(self):
        f = filedialog.askopenfilename(filetypes=[("Icon Files", "*.ico")])
        if f:
            self.icon.set(f)

    def start_build(self):
        if not self.script.get():
            messagebox.showwarning(
                "Missing Script",
                "Please select a .py script first.")
            return
        threading.Thread(target=self.run_pyinstaller, daemon=True).start()

    def run_pyinstaller(self):
        self.progress["value"] = 0
        cmd = [sys.executable,
               "-m",
               "PyInstaller",
               "--onefile",
               "--windowed",
               f"--icon={self.icon.get()}"] if self.icon.get() else [sys.executable,
                                                                     "-m",
                                                                     "PyInstaller",
                                                                     "--onefile",
                                                                     "--windowed"]
        cmd.append(self.script.get())
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True)
        for line in proc.stdout:
            if "Building EXE from" in line:
                self.progress["value"] = 50
            elif "completed successfully" in line.lower():
                self.progress["value"] = 100
        proc.wait()
        messagebox.showinfo("Done", "Build finished! Check the dist/ folder.")
        self.progress["value"] = 0


if __name__ == "__main__":
    root = tk.Tk()
    from tkinter import ttk
    PyToExeBuilder(root)
    root.mainloop()
