import os
import shutil
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import psutil

class DiskBlasterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("DiskBlaster - Advanced System Cleaner")
        self.root.geometry("800x700")
        self.root.resizable(False, False)
        
        # Application icon (if available)
        try:
            self.root.iconbitmap("diskblaster.ico")
        except:
            pass
        
        # Style configurations
        self.style = ttk.Style()
        self.style.configure('TFrame', background='#f0f0f0')
        self.style.configure('TLabel', background='#f0f0f0', font=('Arial', 10))
        self.style.configure('Title.TLabel', background='#f0f0f0', font=('Arial', 18, 'bold'), foreground='#c10000')
        self.style.configure('TButton', font=('Arial', 10))
        self.style.configure('RunAll.TButton', font=('Arial', 12, 'bold'), foreground='white', background='#c10000')
        self.style.configure('TCheckbutton', background='#f0f0f0', font=('Arial', 10))
        
        # Create main frame
        self.main_frame = ttk.Frame(root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Title
        title_label = ttk.Label(self.main_frame, text="DiskBlaster - Advanced System Cleaner", style='Title.TLabel')
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 15))
        
        # Description
        desc_label = ttk.Label(self.main_frame, 
                              text="Select the cleaning options you want to perform and click 'Run Selected' or 'Run All' for a complete cleanup.")
        desc_label.grid(row=1, column=0, columnspan=2, pady=(0, 15))
        
        # Options frame
        options_frame = ttk.LabelFrame(self.main_frame, text="Cleaning Options", padding="10")
        options_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 15))
        
        # Checkboxes for options
        self.temp_var = tk.BooleanVar(value=True)
        self.update_var = tk.BooleanVar(value=True)
        self.recycle_var = tk.BooleanVar(value=True)
        self.logs_var = tk.BooleanVar(value=True)
        self.browser_var = tk.BooleanVar(value=True)
        self.prefetch_var = tk.BooleanVar(value=True)
        self.wer_var = tk.BooleanVar(value=True)
        
        ttk.Checkbutton(options_frame, text="Clear TEMP files", variable=self.temp_var).grid(row=0, column=0, sticky=tk.W, pady=2)
        ttk.Checkbutton(options_frame, text="Clear Windows Update cache", variable=self.update_var).grid(row=1, column=0, sticky=tk.W, pady=2)
        ttk.Checkbutton(options_frame, text="Empty Recycle Bin", variable=self.recycle_var).grid(row=2, column=0, sticky=tk.W, pady=2)
        ttk.Checkbutton(options_frame, text="Delete Log files", variable=self.logs_var).grid(row=3, column=0, sticky=tk.W, pady=2)
        ttk.Checkbutton(options_frame, text="Clear Browser cache (Chrome/Edge/Firefox)", variable=self.browser_var).grid(row=0, column=1, sticky=tk.W, pady=2)
        ttk.Checkbutton(options_frame, text="Clear Prefetch folder", variable=self.prefetch_var).grid(row=1, column=1, sticky=tk.W, pady=2)
        ttk.Checkbutton(options_frame, text="Delete Windows Error Reports", variable=self.wer_var).grid(row=2, column=1, sticky=tk.W, pady=2)
        
        # Buttons frame
        buttons_frame = ttk.Frame(self.main_frame)
        buttons_frame.grid(row=3, column=0, columnspan=2, pady=(0, 15))
        
        ttk.Button(buttons_frame, text="Run Selected", command=self.run_selected).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Run All", command=self.run_all, style='RunAll.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Show Disk Space", command=self.show_disk_space).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Exit", command=self.root.destroy).pack(side=tk.LEFT, padx=5)
        
        # Output area
        output_label = ttk.Label(self.main_frame, text="Operation Output:")
        output_label.grid(row=4, column=0, sticky=tk.W, pady=(5, 0))
        
        self.output_area = scrolledtext.ScrolledText(self.main_frame, width=90, height=20, state='disabled')
        self.output_area.grid(row=5, column=0, columnspan=2, pady=(5, 0))
        
        # Progress bar
        self.progress = ttk.Progressbar(self.main_frame, mode='indeterminate')
        self.progress.grid(row=6, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        
        # Status label
        self.status_label = ttk.Label(self.main_frame, text="Ready")
        self.status_label.grid(row=7, column=0, columnspan=2, sticky=tk.W)
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.columnconfigure(1, weight=1)
        
    def log_message(self, message):
        """Add message to output area"""
        self.output_area.config(state='normal')
        self.output_area.insert(tk.END, message + "\n")
        self.output_area.see(tk.END)
        self.output_area.config(state='disabled')
        self.status_label.config(text=message)
        
    def run_command(self, func, *args):
        """Run a command in a separate thread"""
        self.progress.start()
        thread = threading.Thread(target=func, args=args)
        thread.daemon = True
        thread.start()
        self.check_thread(thread)
        
    def check_thread(self, thread):
        """Check if thread is still running"""
        if thread.is_alive():
            self.root.after(100, lambda: self.check_thread(thread))
        else:
            self.progress.stop()
            self.log_message("Operation completed!")
            
    def clear_temp_files(self):
        """Clear TEMP files"""
        self.log_message("Clearing TEMP files...")
        try:
            temp_dir = os.environ.get('TEMP', '')
            if temp_dir and os.path.exists(temp_dir):
                for root, dirs, files in os.walk(temp_dir):
                    for file in files:
                        try:
                            os.remove(os.path.join(root, file))
                        except:
                            pass
            
            windows_temp = "C:\\Windows\\Temp"
            if os.path.exists(windows_temp):
                for root, dirs, files in os.walk(windows_temp):
                    for file in files:
                        try:
                            os.remove(os.path.join(root, file))
                        except:
                            pass
            
            self.log_message("TEMP files cleared successfully!")
        except Exception as e:
            self.log_message(f"Error clearing TEMP files: {str(e)}")
            
    def clear_update_cache(self):
        """Clear Windows Update cache"""
        self.log_message("Clearing Windows Update cache...")
        try:
            # Stop Windows Update service
            subprocess.run(['net', 'stop', 'wuauserv'], capture_output=True, text=True)
            
            # Delete update cache
            update_path = "C:\\Windows\\SoftwareDistribution\\Download"
            if os.path.exists(update_path):
                shutil.rmtree(update_path)
                os.makedirs(update_path)
            
            # Start Windows Update service
            subprocess.run(['net', 'start', 'wuauserv'], capture_output=True, text=True)
            
            self.log_message("Windows Update cache cleared successfully!")
        except Exception as e:
            self.log_message(f"Error clearing update cache: {str(e)}")
            
    def empty_recycle_bin(self):
        """Empty Recycle Bin"""
        self.log_message("Emptying Recycle Bin...")
        try:
            # Empty recycle bin using PowerShell
            subprocess.run([
                'powershell', 
                '-Command', 
                'Clear-RecycleBin -Force'
            ], capture_output=True, text=True)
            
            self.log_message("Recycle Bin emptied successfully!")
        except Exception as e:
            self.log_message(f"Error emptying Recycle Bin: {str(e)}")
            
    def delete_log_files(self):
        """Delete Log files"""
        self.log_message("Deleting Windows log files...")
        try:
            logs_path = "C:\\Windows\\Logs"
            if os.path.exists(logs_path):
                for root, dirs, files in os.walk(logs_path):
                    for file in files:
                        try:
                            os.remove(os.path.join(root, file))
                        except:
                            pass
            
            self.log_message("Log files deleted successfully!")
        except Exception as e:
            self.log_message(f"Error deleting log files: {str(e)}")
            
    def clear_browser_cache(self):
        """Clear Browser cache"""
        self.log_message("Clearing browser cache...")
        try:
            # Chrome
            chrome_path = os.path.expanduser('~') + "\\AppData\\Local\\Google\\Chrome\\User Data\\Default\\Cache"
            if os.path.exists(chrome_path):
                shutil.rmtree(chrome_path)
                self.log_message("Chrome cache cleared!")
            
            # Edge
            edge_path = os.path.expanduser('~') + "\\AppData\\Local\\Microsoft\\Edge\\User Data\\Default\\Cache"
            if os.path.exists(edge_path):
                shutil.rmtree(edge_path)
                self.log_message("Edge cache cleared!")
            
            # Firefox
            firefox_profiles = os.path.expanduser('~') + "\\AppData\\Roaming\\Mozilla\\Firefox\\Profiles"
            if os.path.exists(firefox_profiles):
                for profile in os.listdir(firefox_profiles):
                    cache_path = os.path.join(firefox_profiles, profile, "cache2")
                    if os.path.exists(cache_path):
                        shutil.rmtree(cache_path)
                self.log_message("Firefox cache cleared!")
            
            self.log_message("Browser cache cleared successfully!")
        except Exception as e:
            self.log_message(f"Error clearing browser cache: {str(e)}")
            
    def clear_prefetch(self):
        """Clear Prefetch folder"""
        self.log_message("Clearing Prefetch folder...")
        try:
            prefetch_path = "C:\\Windows\\Prefetch"
            if os.path.exists(prefetch_path):
                for file in os.listdir(prefetch_path):
                    try:
                        os.remove(os.path.join(prefetch_path, file))
                    except:
                        pass
            
            self.log_message("Prefetch folder cleared successfully!")
        except Exception as e:
            self.log_message(f"Error clearing Prefetch folder: {str(e)}")
            
    def clear_wer(self):
        """Delete Windows Error Reports"""
        self.log_message("Deleting Windows Error Reports...")
        try:
            wer_queue = "C:\\ProgramData\\Microsoft\\Windows\\WER\\ReportQueue"
            if os.path.exists(wer_queue):
                shutil.rmtree(wer_queue)
                os.makedirs(wer_queue)
            
            wer_archive = "C:\\ProgramData\\Microsoft\\Windows\\WER\\ReportArchive"
            if os.path.exists(wer_archive):
                shutil.rmtree(wer_archive)
                os.makedirs(wer_archive)
            
            self.log_message("Windows Error Reports deleted successfully!")
        except Exception as e:
            self.log_message(f"Error deleting Windows Error Reports: {str(e)}")
            
    def show_disk_space(self):
        """Show free disk space"""
        self.log_message("Checking disk space...")
        try:
            disk_info = ""
            for partition in psutil.disk_partitions():
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    total_gb = usage.total / (1024**3)
                    used_gb = usage.used / (1024**3)
                    free_gb = usage.free / (1024**3)
                    free_percent = (usage.free / usage.total) * 100
                    
                    disk_info += f"{partition.device} - {free_gb:.2f}GB free of {total_gb:.2f}GB ({free_percent:.1f}% free)\n"
                except:
                    continue
            
            self.log_message(disk_info)
            self.log_message("Disk space information retrieved successfully!")
        except Exception as e:
            self.log_message(f"Error retrieving disk space: {str(e)}")
            
    def run_selected(self):
        """Run selected cleaning operations"""
        self.output_area.config(state='normal')
        self.output_area.delete(1.0, tk.END)
        self.output_area.config(state='disabled')
        
        def run_operations():
            if self.temp_var.get():
                self.clear_temp_files()
            if self.update_var.get():
                self.clear_update_cache()
            if self.recycle_var.get():
                self.empty_recycle_bin()
            if self.logs_var.get():
                self.delete_log_files()
            if self.browser_var.get():
                self.clear_browser_cache()
            if self.prefetch_var.get():
                self.clear_prefetch()
            if self.wer_var.get():
                self.clear_wer()
            
            self.log_message("Selected operations completed!")
            messagebox.showinfo("DiskBlaster", "Selected cleaning operations completed!")
        
        self.run_command(run_operations)
        
    def run_all(self):
        """Run all cleaning operations"""
        self.output_area.config(state='normal')
        self.output_area.delete(1.0, tk.END)
        self.output_area.config(state='disabled')
        
        # Select all options
        self.temp_var.set(True)
        self.update_var.set(True)
        self.recycle_var.set(True)
        self.logs_var.set(True)
        self.browser_var.set(True)
        self.prefetch_var.set(True)
        self.wer_var.set(True)
        
        def run_all_operations():
            self.clear_temp_files()
            self.clear_update_cache()
            self.empty_recycle_bin()
            self.delete_log_files()
            self.clear_browser_cache()
            self.clear_prefetch()
            self.clear_wer()
            
            self.log_message("✅ ALL CLEANING OPERATIONS COMPLETED!")
            messagebox.showinfo("DiskBlaster", "All cleaning operations completed successfully!")
        
        self.run_command(run_all_operations)

if __name__ == "__main__":
    root = tk.Tk()
    app = DiskBlasterApp(root)
    root.mainloop()