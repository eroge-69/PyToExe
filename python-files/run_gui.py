import subprocess
import tkinter as tk
from tkinter import messagebox
import webbrowser
import os
import signal

class DjangoServerController(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Django Server Controller")
        self.geometry("350x130")
        self.protocol("WM_DELETE_WINDOW", self.on_close)

        self.server_process = None
        self.fixed_host = "127.0.0.1"
        self.fixed_port = "8000"

        # Info label about fixed address
        info_text = f"Server will run at http://{self.fixed_host}:{self.fixed_port}/"
        tk.Label(self, text=info_text).pack(pady=10)

        # Buttons
        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=5)

        self.start_button = tk.Button(btn_frame, text="Start Server", command=self.start_server)
        self.start_button.grid(row=0, column=0, padx=10)

        self.stop_button = tk.Button(btn_frame, text="Stop Server", command=self.stop_server, state=tk.DISABLED)
        self.stop_button.grid(row=0, column=1, padx=10)

        # Status label
        self.status_label = tk.Label(self, text="Server not running", fg="red")
        self.status_label.pack(pady=10)

    def start_server(self):
        if self.server_process:
            messagebox.showinfo("Info", "Server is already running.")
            return

        base_dir = os.path.dirname(os.path.abspath(__file__))
        python_path = os.path.join(base_dir, "python.exe")
        manage_py_path = os.path.join(base_dir, "DPM", "Management", "manage.py")

        if not os.path.exists(python_path) or not os.path.exists(manage_py_path):
            messagebox.showerror("Error", "Required files not found.\nEnsure python.exe and manage.py exist.")
            return

        cmd = [python_path, manage_py_path, "runserver", f"{self.fixed_host}:{self.fixed_port}"]

        try:
            self.server_process = subprocess.Popen(
                cmd,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start server:\n{e}")
            return

        url = f"http://{self.fixed_host}:{self.fixed_port}/"
        webbrowser.open(url)
        self.status_label.config(text=f"Running at {url}", fg="green")
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)

    def stop_server(self):
        if not self.server_process:
            return
        try:
            self.server_process.send_signal(signal.CTRL_BREAK_EVENT)
            self.server_process.wait(timeout=5)
        except Exception:
            self.server_process.kill()
        self.server_process = None
        self.status_label.config(text="Server stopped", fg="red")
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)

    def on_close(self):
        if self.server_process:
            if messagebox.askyesno("Confirm", "Server is running. Stop and exit?"):
                self.stop_server()
            else:
                return
        self.destroy()

if __name__ == "__main__":
    app = DjangoServerController()
    app.mainloop()
