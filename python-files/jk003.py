import os
import platform
import subprocess
import sys
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk, scrolledtext

class Py2ExeBuilder:
    def __init__(self, root):
        self.root = root
        self.root.title("Python to EXE Builder")
        self.root.geometry("750x550")

        self.py_file_path = tk.StringVar()
        self.exe_name = tk.StringVar()
        self.icon_path = tk.StringVar()
        self.onefile = tk.BooleanVar(value=True)
        self.console = tk.BooleanVar(value=False)
        self.upx_compress = tk.BooleanVar(value=True)

        self.create_widgets()

    def create_widgets(self):
        frame = ttk.Frame(self.root, padding=10)
        frame.grid(row=0, column=0, sticky="nsew")
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        ttk.Label(frame, text="Python File:").grid(row=0, column=0, sticky="w")
        ttk.Entry(frame, textvariable=self.py_file_path, width=60).grid(row=0, column=1, sticky="ew")
        ttk.Button(frame, text="Browse", command=self.browse_py_file).grid(row=0, column=2, padx=5)

        ttk.Label(frame, text="EXE Name:").grid(row=1, column=0, sticky="w", pady=5)
        ttk.Entry(frame, textvariable=self.exe_name, width=30).grid(row=1, column=1, sticky="w")

        ttk.Label(frame, text="Icon File (.ico):").grid(row=2, column=0, sticky="w")
        ttk.Entry(frame, textvariable=self.icon_path, width=60).grid(row=2, column=1, sticky="ew")
        ttk.Button(frame, text="Browse", command=self.browse_icon).grid(row=2, column=2, padx=5)

        ttk.Label(frame, text="Additional Files (comma separated):").grid(row=3, column=0, columnspan=3, sticky="w", pady=5)
        self.additional_files_entry = scrolledtext.ScrolledText(frame, height=2, width=80)
        self.additional_files_entry.grid(row=4, column=0, columnspan=3, sticky="ew")

        ttk.Label(frame, text="Hidden Imports (comma separated):").grid(row=5, column=0, columnspan=3, sticky="w", pady=5)
        self.hidden_imports_entry = scrolledtext.ScrolledText(frame, height=2, width=80)
        self.hidden_imports_entry.grid(row=6, column=0, columnspan=3, sticky="ew")

        ttk.Checkbutton(frame, text="One File", variable=self.onefile).grid(row=7, column=0, sticky="w", pady=3)
        ttk.Checkbutton(frame, text="Console Window", variable=self.console).grid(row=7, column=1, sticky="w", pady=3)
        ttk.Checkbutton(frame, text="UPX Compression", variable=self.upx_compress).grid(row=7, column=2, sticky="w", pady=3)

        self.progress = ttk.Progressbar(frame, mode="indeterminate")
        self.progress.grid(row=8, column=0, columnspan=3, sticky="ew", pady=10)

        ttk.Button(frame, text="Build EXE", command=self.start_build).grid(row=9, column=0, columnspan=3, pady=10)

        self.status_label = ttk.Label(frame, text="", foreground="blue")
        self.status_label.grid(row=10, column=0, columnspan=3, sticky="w")

        self.output_console = scrolledtext.ScrolledText(frame, height=10, width=80, state="disabled")
        self.output_console.grid(row=11, column=0, columnspan=3, pady=5, sticky="nsew")

    def log_output(self, text):
        self.output_console.configure(state="normal")
        self.output_console.insert(tk.END, text + "\n")
        self.output_console.configure(state="disabled")
        self.output_console.see(tk.END)

    def browse_py_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Python Files", "*.py")])
        if file_path:
            self.py_file_path.set(file_path)
            if not self.exe_name.get():
                self.exe_name.set(os.path.splitext(os.path.basename(file_path))[0])

    def browse_icon(self):
        file_path = filedialog.askopenfilename(filetypes=[("Icon Files", "*.ico")])
        if file_path:
            self.icon_path.set(file_path)

    def start_build(self):
        threading.Thread(target=self.build_exe).start()

    def install_pyinstaller(self):
        self.log_output("PyInstaller not found. Installing...")
        python_exec = sys.executable
        try:
            proc = subprocess.run([python_exec, "-m", "pip", "install", "pyinstaller"], capture_output=True, text=True)
            self.log_output(proc.stdout)
            if proc.returncode != 0:
                self.log_output(proc.stderr)
                messagebox.showerror("Installation Error", "Failed to install PyInstaller.\nSee output for details.")
                return False
            self.log_output("PyInstaller installed successfully.")
            return True
        except Exception as e:
            messagebox.showerror("Installation Error", str(e))
            return False

    def build_exe(self):
        if not self.py_file_path.get():
            messagebox.showerror("Error", "Please select a Python file.")
            return

        # Check PyInstaller
        try:
            import PyInstaller  # just test import
        except ImportError:
            if not self.install_pyinstaller():
                self.status_label.config(text="Build failed: PyInstaller not installed.")
                return

        def q(path):
            return f'"{path}"'

        py_file = q(self.py_file_path.get())
        exe_name = self.exe_name.get() or os.path.splitext(os.path.basename(self.py_file_path.get()))[0]
        icon = q(self.icon_path.get()) if self.icon_path.get() else ""

        add_files = self.additional_files_entry.get("1.0", tk.END).strip()
        sep = ";" if platform.system() == "Windows" else ":"
        add_files_str = " ".join([f'--add-data {q(path.strip() + sep + ".")}' for path in add_files.split(",") if path.strip()])

        hidden_imports = self.hidden_imports_entry.get("1.0", tk.END).strip()
        hidden_imports_str = " ".join([f'--hidden-import "{imp.strip()}"' for imp in hidden_imports.split(",") if imp.strip()])

        onefile = "--onefile" if self.onefile.get() else ""
        console = "--console" if self.console.get() else ""
        upx = "" if self.upx_compress.get() else "--upx-exclude"

        python_exec = q(sys.executable)

        cmd = f'{python_exec} -m PyInstaller {onefile} {console} {upx} --name "{exe_name}"'
        if icon:
            cmd += f' --icon {icon}'
        if add_files_str:
            cmd += f" {add_files_str}"
        if hidden_imports_str:
            cmd += f" {hidden_imports_str}"
        cmd += f" {py_file}"

        self.status_label.config(text="Building... Please wait.")
        self.progress.start(10)
        self.output_console.configure(state="normal")
        self.output_console.delete("1.0", tk.END)
        self.output_console.configure(state="disabled")

        try:
            process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            for line in process.stdout:
                self.log_output(line.strip())
            process.wait()

            self.progress.stop()
            if process.returncode == 0:
                self.status_label.config(text="✅ Build complete!")
                output_dir = os.path.join(os.getcwd(), "dist")
                if platform.system() == "Windows":
                    subprocess.Popen(f'explorer "{output_dir}"')
                else:
                    subprocess.Popen(["open", output_dir])
            else:
                self.status_label.config(text="❌ Build failed.")
        except Exception as e:
            self.progress.stop()
            messagebox.showerror("Error", str(e))
            self.status_label.config(text="Build failed.")

if __name__ == "__main__":
    root = tk.Tk()
    app = Py2ExeBuilder(root)
    root.mainloop()
