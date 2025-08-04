import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import subprocess
import threading
import sys
import ctypes
import os
import time

class WiFiResetApp:
    def __init__(self, root):
        self.root = root
        self.root.title("WiFi Reset Tool")
        self.root.geometry("500x400")
        self.root.resizable(True, True)
        
        # Threading event for stopping the fix process
        self.stop_event = threading.Event()
        
        # Configure style
        style = ttk.Style()
        style.theme_use('clam')
        
        self.create_widgets()
        self.check_admin_privileges()
        
    def create_widgets(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="WiFi Reset Tool", font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 10))
        
        # WiFi adapter info
        info_frame = ttk.LabelFrame(main_frame, text="WiFi Adapter Information", padding="5")
        info_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        info_frame.columnconfigure(1, weight=1)
        
        ttk.Label(info_frame, text="Target Adapter:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.adapter_var = tk.StringVar(value="Intel(R) Wi-Fi 6 AX201 160MHz")
        adapter_entry = ttk.Entry(info_frame, textvariable=self.adapter_var, width=40)
        adapter_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(5, 0))
        
        # Buttons frame
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        button_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(1, weight=1)
        button_frame.columnconfigure(2, weight=1)
        button_frame.columnconfigure(3, weight=1)
        
        # Buttons
        self.fix_button = ttk.Button(button_frame, text="Fix WiFi Until Works", 
                                    command=self.fix_wifi_until_works, style="Accent.TButton")
        self.fix_button.grid(row=0, column=0, padx=2, sticky=(tk.W, tk.E))
        
        self.stop_button = ttk.Button(button_frame, text="Stop Fix", 
                                     command=self.stop_fix_wifi, state='disabled')
        self.stop_button.grid(row=0, column=1, padx=2, sticky=(tk.W, tk.E))
        
        self.list_button = ttk.Button(button_frame, text="List Adapters", 
                                     command=self.list_adapters_threaded)
        self.list_button.grid(row=0, column=2, padx=2, sticky=(tk.W, tk.E))
        
        self.clear_button = ttk.Button(button_frame, text="Clear Log", 
                                      command=self.clear_log)
        self.clear_button.grid(row=0, column=3, padx=2, sticky=(tk.W, tk.E))
        
        # Log frame
        log_frame = ttk.LabelFrame(main_frame, text="Log Output", padding="5")
        log_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        # Log text area
        self.log_text = scrolledtext.ScrolledText(log_frame, height=15, width=60)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
    
    def check_admin_privileges(self):
        """Check if the application is running with administrator privileges"""
        try:
            is_admin = ctypes.windll.shell32.IsUserAnAdmin()
            if not is_admin:
                self.log_message("⚠️ WARNING: This application requires administrator privileges for full functionality.")
                self.log_message("Some operations may fail without proper permissions.")
                self.status_var.set("Running without admin privileges")
            else:
                self.log_message("✅ Running with administrator privileges.")
                self.status_var.set("Ready (Admin)")
        except:
            self.log_message("⚠️ Could not determine privilege level.")
    
    def log_message(self, message):
        """Add a message to the log"""
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()
    
    def clear_log(self):
        """Clear the log text area"""
        self.log_text.delete(1.0, tk.END)
    
    def run_powershell_command(self, command):
        """Execute a PowerShell command and return the result"""
        try:
            # Create startup info to hide the window
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = subprocess.SW_HIDE
            
            result = subprocess.run(
                ["powershell", "-Command", command],
                capture_output=True,
                text=True,
                timeout=30,
                startupinfo=startupinfo
            )
            return result.stdout, result.stderr, result.returncode
        except subprocess.TimeoutExpired:
            return "", "Command timed out", 1
        except Exception as e:
            return "", f"Error executing command: {str(e)}", 1
    
    def list_adapters_threaded(self):
        """List network adapters in a separate thread"""
        threading.Thread(target=self.list_adapters, daemon=True).start()
    
    def list_adapters(self):
        """List all network adapters"""
        self.status_var.set("Listing network adapters...")
        self.list_button.config(state='disabled')
        
        try:
            self.log_message("📡 Listing all network adapters...")
            
            command = "Get-NetAdapter | Select-Object Name, InterfaceDescription, Status | Format-Table -AutoSize"
            stdout, stderr, returncode = self.run_powershell_command(command)
            
            if returncode == 0:
                self.log_message("Available network adapters:")
                self.log_message(stdout)
            else:
                self.log_message(f"❌ Error listing adapters: {stderr}")
                
        except Exception as e:
            self.log_message(f"❌ Exception occurred: {str(e)}")
        finally:
            self.list_button.config(state='normal')
            self.status_var.set("Ready")
    
    def stop_fix_wifi(self):
        """Stop the WiFi fix process"""
        self.stop_event.set()
        self.log_message("🛑 Stop requested by user...")
        self.status_var.set("Stopping...")
    
    def fix_wifi_until_works(self):
        """Fix WiFi adapter until it works - using the proven logic"""
        # Check admin privileges first
        if not ctypes.windll.shell32.IsUserAnAdmin():
            try:
                # Try to restart with admin privileges
                ctypes.windll.shell32.ShellExecuteW(
                    None, "runas", sys.executable, " ".join(sys.argv), None, 1
                )
                return
            except:
                self.log_message("⚠️ Admin privileges required but elevation failed.")
                self.log_message("Some operations may fail. Try running as administrator.")
        
        # Clear the stop event
        self.stop_event.clear()
        
        # Update button states
        self.fix_button.config(state='disabled')
        self.stop_button.config(state='normal')
        self.status_var.set("Fixing WiFi...")
        
        # Clear log and start
        self.clear_log()
        
        # Start in separate thread
        threading.Thread(target=self.fix_wifi_loop, daemon=True).start()
    
    def fix_wifi_loop(self):
        """Main fix loop using the exact working logic from wifi_fix_until_works.ps1"""
        try:
            self.log_message("WiFi Fix - Keep trying until it works")
            self.log_message("=====================================")
            self.log_message("Click 'Stop Fix' button to cancel at any time")
            self.log_message("")
            
            # Find Intel WiFi adapter
            self.log_message("Looking for Intel WiFi adapter...")
            find_command = '''
            $wifiDevice = Get-PnpDevice | Where-Object { 
                $_.Class -eq "Net" -and $_.FriendlyName -like "*Intel*Wi-Fi*"
            } | Select-Object -First 1
            
            if ($wifiDevice) {
                Write-Output $wifiDevice.FriendlyName
            } else {
                Write-Output "NOT_FOUND"
            }
            '''
            
            stdout, stderr, returncode = self.run_powershell_command(find_command)
            
            if returncode != 0 or "NOT_FOUND" in stdout:
                self.log_message("No Intel WiFi adapter found!")
                self.status_var.set("Ready")
                self.fix_button.config(state='normal')
                self.stop_button.config(state='disabled')
                return
            
            adapter_name = stdout.strip()
            self.log_message(f"Found: {adapter_name}")
            self.log_message("")
            
            attempt = 1
            
            # Keep trying until it works or user stops
            while not self.stop_event.is_set():
                self.log_message(f"Attempt {attempt}")
                self.log_message("-----------")
                
                # Check if device has any problems
                check_command = '''
                $wifiDevice = Get-PnpDevice | Where-Object { 
                    $_.Class -eq "Net" -and $_.FriendlyName -like "*Intel*Wi-Fi*"
                } | Select-Object -First 1
                
                if ($wifiDevice) {
                    $device = Get-WmiObject -Class Win32_PnPEntity | Where-Object { $_.DeviceID -eq $wifiDevice.InstanceId }
                    Write-Output $device.ConfigManagerErrorCode
                } else {
                    Write-Output "999"
                }
                '''
                
                stdout, stderr, returncode = self.run_powershell_command(check_command)
                
                if returncode == 0:
                    error_code = int(stdout.strip())
                else:
                    error_code = 999
                
                if error_code == 0:
                    self.log_message("✅ WiFi adapter is working! (No errors)")
                    self.log_message("Check Device Manager - yellow warning should be gone.")
                    self.log_message("")
                    self.log_message("🎉 SUCCESS! WiFi adapter is now working properly!")
                    self.log_message("The yellow warning icon should be gone from Device Manager.")
                    self.status_var.set("WiFi Fixed!")
                    break
                else:
                    if self.stop_event.is_set():
                        break
                        
                    self.log_message(f"❌ WiFi has problems (Error Code: {error_code})")
                    self.log_message("Disabling...")
                    
                    # Disable using PnP
                    disable_command = '''
                    $wifiDevice = Get-PnpDevice | Where-Object { 
                        $_.Class -eq "Net" -and $_.FriendlyName -like "*Intel*Wi-Fi*"
                    } | Select-Object -First 1
                    
                    if ($wifiDevice) {
                        Disable-PnpDevice -InstanceId $wifiDevice.InstanceId -Confirm:$false -ErrorAction SilentlyContinue
                    }
                    '''
                    
                    self.run_powershell_command(disable_command)
                    
                    # Check for stop during sleep
                    for i in range(20):  # 2 seconds total, check every 0.1 seconds
                        if self.stop_event.is_set():
                            break
                        time.sleep(0.1)
                    
                    if self.stop_event.is_set():
                        break
                    
                    self.log_message("Enabling...")
                    
                    # Enable using PnP
                    enable_command = '''
                    $wifiDevice = Get-PnpDevice | Where-Object { 
                        $_.Class -eq "Net" -and $_.FriendlyName -like "*Intel*Wi-Fi*"
                    } | Select-Object -First 1
                    
                    if ($wifiDevice) {
                        Enable-PnpDevice -InstanceId $wifiDevice.InstanceId -Confirm:$false -ErrorAction SilentlyContinue
                    }
                    '''
                    
                    self.run_powershell_command(enable_command)
                    
                    # Check for stop during sleep
                    for i in range(30):  # 3 seconds total, check every 0.1 seconds
                        if self.stop_event.is_set():
                            break
                        time.sleep(0.1)
                    
                    if self.stop_event.is_set():
                        break
                    
                    self.log_message("Checking...")
                    
                    # Check for stop during sleep
                    for i in range(20):  # 2 seconds total, check every 0.1 seconds
                        if self.stop_event.is_set():
                            break
                        time.sleep(0.1)
                
                attempt += 1
                self.log_message("")
            
            # Check if stopped by user
            if self.stop_event.is_set():
                self.log_message("🛑 WiFi fix stopped by user.")
                self.status_var.set("Stopped")
                
        except Exception as e:
            self.log_message(f"❌ Exception occurred: {str(e)}")
        finally:
            self.fix_button.config(state='normal')
            self.stop_button.config(state='disabled')
            if not self.stop_event.is_set():
                self.status_var.set("Ready")

def main():
    # Try to run as administrator if not already
    if not ctypes.windll.shell32.IsUserAnAdmin():
        try:
            # Re-run the program with admin rights
            ctypes.windll.shell32.ShellExecuteW(
                None, "runas", sys.executable, " ".join(sys.argv), None, 1
            )
            return
        except:
            pass  # Continue without admin rights
    
    root = tk.Tk()
    app = WiFiResetApp(root)
    
    # Center the window
    root.update_idletasks()
    x = (root.winfo_screenwidth() // 2) - (root.winfo_width() // 2)
    y = (root.winfo_screenheight() // 2) - (root.winfo_height() // 2)
    root.geometry(f"+{x}+{y}")
    
    root.mainloop()

if __name__ == "__main__":
    main() 