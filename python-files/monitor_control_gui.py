import tkinter as tk
import subprocess
from tkinter import messagebox

class MonitorControlGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Monitor Control")
        self.root.geometry("300x250")
        
        # Create main frame
        self.main_frame = tk.Frame(self.root, padx=10, pady=10)
        self.main_frame.pack(expand=True, fill="both")
        
        # Create and place buttons
        tk.Button(
            self.main_frame,
            text="Set Brightness to 0",
            command=lambda: self.execute_command('10', '0'),
            width=20
        ).pack(pady=5)
        
        tk.Button(
            self.main_frame,
            text="Set Brightness to 10",
            command=lambda: self.execute_command('10', '10'),
            width=20
        ).pack(pady=5)
        
        tk.Button(
            self.main_frame,
            text="Set Brightness to 25",
            command=lambda: self.execute_command('10', '25'),
            width=20
        ).pack(pady=5)
        
        tk.Button(
            self.main_frame,
            text="Set Power Mode to 5",
            command=lambda: self.execute_command('D6', '5'),
            width=20
        ).pack(pady=5)
        
        # Status label
        self.status_label = tk.Label(self.main_frame, text="")
        self.status_label.pack(pady=10)
    
    def execute_command(self, code, value):
        try:
            command = f'ControlMyMonitor.exe /SetValue "Primary" {code} {value}'
            result = subprocess.run(command, capture_output=True, text=True, shell=True)
            if result.returncode == 0:
                self.status_label.config(text=f"Success: Set {code} to {value}")
            else:
                self.status_label.config(text="Error: Command failed")
                messagebox.showerror("Error", f"Command failed: {result.stderr}")
        except Exception as e:
            self.status_label.config(text="Error occurred")
            messagebox.showerror("Error", f"Error: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = MonitorControlGUI(root)
    root.mainloop()