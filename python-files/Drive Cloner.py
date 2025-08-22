import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess
import os

def run_disk2vhd(disk2vhd_path, volumes, output_path, log_callback):
    if not os.path.isfile(disk2vhd_path):
        log_callback(f"Disk2vhd.exe not found at: {disk2vhd_path}")
        return

    if not output_path.lower().endswith(".vhdx"):
        log_callback("Output file must have a .vhdx extension.")
        return

    command = [
        disk2vhd_path,
        volumes,
        output_path,
        "/vhdx"
    ]

    log_callback(f"Running: {' '.join(command)}")

    try:
        subprocess.run(command, check=True)
        log_callback(f"✅ Drive successfully cloned to: {output_path}")
    except subprocess.CalledProcessError as e:
        log_callback(f"❌ Error running Disk2vhd: {e}")
    except Exception as ex:
        log_callback(f"❌ Unexpected error: {ex}")


class Disk2VHDGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Clone Drive to .VHDX")

        self.disk2vhd_path = tk.StringVar()
        self.volumes = tk.StringVar(value="*")
        self.output_path = tk.StringVar()

        self.create_widgets()

    def create_widgets(self):
        padding = {'padx': 10, 'pady': 5}

        tk.Label(self.root, text="Disk2vhd.exe Path:").grid(row=0, column=0, sticky='e', **padding)
        tk.Entry(self.root, textvariable=self.disk2vhd_path, width=50).grid(row=0, column=1, **padding)
        tk.Button(self.root, text="Browse", command=self.browse_disk2vhd).grid(row=0, column=2, **padding)

        tk.Label(self.root, text="Volumes to Clone (e.g., C: or *):").grid(row=1, column=0, sticky='e', **padding)
        tk.Entry(self.root, textvariable=self.volumes, width=20).grid(row=1, column=1, **padding)

        tk.Label(self.root, text="Output VHDX Path:").grid(row=2, column=0, sticky='e', **padding)
        tk.Entry(self.root, textvariable=self.output_path, width=50).grid(row=2, column=1, **padding)
        tk.Button(self.root, text="Browse", command=self.browse_output_path).grid(row=2, column=2, **padding)

        tk.Button(self.root, text="Start Clone", command=self.start_clone, bg="green", fg="white").grid(row=3, column=1, pady=10)

        self.log_box = tk.Text(self.root, height=10, width=80, state='disabled', bg="#f5f5f5")
        self.log_box.grid(row=4, column=0, columnspan=3, padx=10, pady=10)

    def browse_disk2vhd(self):
        path = filedialog.askopenfilename(title="Select Disk2vhd.exe", filetypes=[("Executable", "*.exe")])
        if path:
            self.disk2vhd_path.set(path)

    def browse_output_path(self):
        path = filedialog.asksaveasfilename(defaultextension=".vhdx", filetypes=[("VHDX file", "*.vhdx")])
        if path:
            self.output_path.set(path)

    def log(self, message):
        self.log_box.config(state='normal')
        self.log_box.insert(tk.END, message + '\n')
        self.log_box.see(tk.END)
        self.log_box.config(state='disabled')

    def start_clone(self):
        disk2vhd_path = self.disk2vhd_path.get().strip()
        volumes = self.volumes.get().strip()
        output_path = self.output_path.get().strip()

        if not disk2vhd_path or not volumes or not output_path:
            messagebox.showerror("Missing Input", "Please provide all fields.")
            return

        self.log("🔄 Starting clone operation...")
        self.root.after(100, run_disk2vhd, disk2vhd_path, volumes, output_path, self.log)


if __name__ == "__main__":
    root = tk.Tk()
    app = Disk2VHDGUI(root)
    root.mainloop()
