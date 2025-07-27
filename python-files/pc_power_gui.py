import tkinter as tk
from tkinter import messagebox, ttk
import subprocess
import sys
import os

class PowerControlGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("PC Power Control")
        self.root.geometry("350x200")
        self.root.resizable(False, False)
        
        # Center the window
        self.center_window()
        
        # Configure style
        style = ttk.Style()
        style.theme_use('clam')
        
        # Main frame
        main_frame = ttk.Frame(root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Title
        title_label = ttk.Label(main_frame, text="PC Power Control", 
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Buttons
        shutdown_btn = ttk.Button(main_frame, text="Shutdown", 
                                 command=self.shutdown_pc, width=15)
        shutdown_btn.grid(row=1, column=0, padx=5, pady=5)
        
        restart_btn = ttk.Button(main_frame, text="Restart", 
                                command=self.restart_pc, width=15)
        restart_btn.grid(row=1, column=1, padx=5, pady=5)
        
        sleep_btn = ttk.Button(main_frame, text="Sleep", 
                              command=self.sleep_pc, width=15)
        sleep_btn.grid(row=2, column=0, padx=5, pady=5)
        
        exit_btn = ttk.Button(main_frame, text="Exit", 
                             command=self.exit_app, width=15)
        exit_btn.grid(row=2, column=1, padx=5, pady=5)
        
        # Info label
        info_label = ttk.Label(main_frame, 
                              text="Click a button to perform the action",
                              font=('Arial', 9))
        info_label.grid(row=3, column=0, columnspan=2, pady=(20, 0))
        
        # Configure grid weights
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
    
    def center_window(self):
        # Get screen dimensions
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # Calculate position
        x = (screen_width // 2) - (350 // 2)
        y = (screen_height // 2) - (200 // 2)
        
        self.root.geometry(f"350x200+{x}+{y}")
    
    def confirm_action(self, action):
        """Show confirmation dialog before performing action"""
        result = messagebox.askyesno(
            "Confirm Action", 
            f"Are you sure you want to {action} your PC?",
            icon='warning'
        )
        return result
    
    def shutdown_pc(self):
        if self.confirm_action("shutdown"):
            try:
                if os.name == 'nt':  # Windows
                    subprocess.run(['shutdown', '/s', '/t', '1'], check=True)
                else:  # Linux/Mac
                    subprocess.run(['shutdown', '-h', 'now'], check=True)
            except subprocess.CalledProcessError as e:
                messagebox.showerror("Error", f"Failed to shutdown: {e}")
            except Exception as e:
                messagebox.showerror("Error", f"Unexpected error: {e}")
    
    def restart_pc(self):
        if self.confirm_action("restart"):
            try:
                if os.name == 'nt':  # Windows
                    subprocess.run(['shutdown', '/r', '/t', '1'], check=True)
                else:  # Linux/Mac
                    subprocess.run(['shutdown', '-r', 'now'], check=True)
            except subprocess.CalledProcessError as e:
                messagebox.showerror("Error", f"Failed to restart: {e}")
            except Exception as e:
                messagebox.showerror("Error", f"Unexpected error: {e}")
    
    def sleep_pc(self):
        if self.confirm_action("put to sleep"):
            try:
                if os.name == 'nt':  # Windows
                    subprocess.run(['rundll32.exe', 'powrprof.dll,SetSuspendState', '0,1,0'], check=True)
                else:  # Linux
                    subprocess.run(['systemctl', 'suspend'], check=True)
            except subprocess.CalledProcessError as e:
                messagebox.showerror("Error", f"Failed to sleep: {e}")
            except Exception as e:
                messagebox.showerror("Error", f"Unexpected error: {e}")
    
    def exit_app(self):
        self.root.quit()

def main():
    root = tk.Tk()
    app = PowerControlGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()