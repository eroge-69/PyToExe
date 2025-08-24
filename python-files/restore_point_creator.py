import tkinter as tk
from tkinter import messagebox, ttk
import subprocess
import sys
import os
from datetime import datetime

class RestorePointCreator:
    def __init__(self, root):
        self.root = root
        self.root.title("System Restore Point Creator")
        self.root.geometry("350x180")
        self.root.resizable(False, False)
        
        # Center the window
        self.center_window()
        
        # Create GUI elements
        self.setup_gui()
        
    def center_window(self):
        """Center the window on screen"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")
    
    def setup_gui(self):
        """Setup the GUI elements"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="30")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Title label
        title_label = ttk.Label(main_frame, text="System Restore Point Creator", 
                               font=("Arial", 14, "bold"))
        title_label.grid(row=0, column=0, pady=(0, 30))
        
        # Create button (large and centered)
        self.create_button = ttk.Button(main_frame, text="Create Restore Point\n(mhadabi,before tweak)", 
                                       command=self.create_restore_point,
                                       style="Accent.TButton")
        self.create_button.grid(row=1, column=0, pady=20, ipadx=20, ipady=10)
        
        # Progress bar (initially hidden)
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        
        # Status label
        self.status_label = ttk.Label(main_frame, text="Ready to create restore point")
        self.status_label.grid(row=3, column=0, pady=(20, 0))
        
        # Configure grid weights
        main_frame.columnconfigure(0, weight=1)
        
    def check_admin_privileges(self):
        """Check if the script is running with administrator privileges"""
        try:
            return os.getuid() == 0
        except AttributeError:
            # Windows
            try:
                import ctypes
                return ctypes.windll.shell32.IsUserAnAdmin() != 0
            except:
                return False
    
    def create_restore_point(self):
        """Create a system restore point"""
        if not self.check_admin_privileges():
            messagebox.showerror("Administrator Required", 
                               "This script must be run as Administrator to create restore points.\n\n"
                               "Please right-click on the Python file and select 'Run as Administrator'")
            return
        
        restore_name = "mhadabi,before tweak"
        
        # Show progress
        self.create_button.config(state="disabled")
        self.progress.grid(row=2, column=0, pady=15, sticky=(tk.W, tk.E))
        self.progress.start()
        self.status_label.config(text="Creating restore point...")
        self.root.update()
        
        try:
            # PowerShell command to create restore point
            powershell_cmd = [
                "powershell", "-Command",
                f"Checkpoint-Computer -Description '{restore_name}' -RestorePointType 'MODIFY_SETTINGS'"
            ]
            
            # Alternative method using wmic (Windows Management Instrumentation)
            wmic_cmd = [
                "wmic.exe", "/Namespace:\\\\root\\default", "Path", "SystemRestore", 
                "Call", "CreateRestorePoint", f'"{restore_name}"', "100", "7"
            ]
            
            # Try PowerShell method first
            try:
                result = subprocess.run(powershell_cmd, capture_output=True, text=True, timeout=60)
                if result.returncode == 0:
                    self.show_success(restore_name)
                else:
                    # Try wmic method as fallback
                    result2 = subprocess.run(wmic_cmd, capture_output=True, text=True, timeout=60)
                    if result2.returncode == 0:
                        self.show_success(restore_name)
                    else:
                        self.show_error(f"Failed to create restore point.\nPowerShell error: {result.stderr}\nWMIC error: {result2.stderr}")
            
            except subprocess.TimeoutExpired:
                self.show_error("Operation timed out. Creating restore points can take time.")
            except Exception as e:
                self.show_error(f"Error creating restore point: {str(e)}")
                
        except Exception as e:
            self.show_error(f"Unexpected error: {str(e)}")
        
        finally:
            # Hide progress and re-enable button
            self.progress.stop()
            self.progress.grid_remove()
            self.create_button.config(state="normal")
    
    def show_success(self, restore_name):
        """Show success message"""
        self.status_label.config(text="Restore point created successfully!")
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        messagebox.showinfo("Success", 
                          f"System restore point created successfully!\n\n"
                          f"Name: {restore_name}\n"
                          f"Time: {timestamp}\n\n"
                          f"You can now safely proceed with your system tweaks.")
    
    def show_error(self, error_msg):
        """Show error message"""
        self.status_label.config(text="Failed to create restore point")
        messagebox.showerror("Error", error_msg)

def main():
    """Main function"""
    # Check if running on Windows
    if sys.platform != "win32":
        messagebox.showerror("Platform Error", "This tool is designed for Windows systems only.")
        return
    
    # Create and run the GUI
    root = tk.Tk()
    app = RestorePointCreator(root)
    root.mainloop()

if __name__ == "__main__":
    main()
