import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import sys
import ctypes
import tempfile
import threading

class HiddenNetworkConnector:
    def __init__(self, root):
        self.root = root
        self.root.title("Hidden Network Connector")
        self.root.geometry("300x200")
        self.root.resizable(False, False)
        
        # Custom colors
        self.bg_color = "#f5f5f5"  # Light gray background
        self.button_color = "#0078d7"  # Windows 11 blue
        self.button_hover = "#106ebe"  # Slightly darker blue
        self.button_text = "#ffffff"  # White text
        self.success_color = "#4CAF50"  # Green for success
        self.error_color = "#f44336"  # Red for errors
        
        # Configure main window
        self.root.configure(bg=self.bg_color)
        
        # Main frame
        self.main_frame = tk.Frame(self.root, bg=self.bg_color)
        self.main_frame.pack(expand=True, fill='both', padx=20, pady=20)
        
        # Title
        self.title_label = tk.Label(
            self.main_frame,
            text="TN-MM6210 Connector",
            bg=self.bg_color,
            fg="#333333",
            font=('Segoe UI', 12, 'bold')
        )
        self.title_label.pack(pady=(0, 20))
        
        # Connect button - Using tk.Button for better color control
        self.connect_btn = tk.Button(
            self.main_frame,
            text="Connect Now",
            command=self.start_connection,
            bg=self.button_color,
            fg=self.button_text,
            activebackground=self.button_hover,
            activeforeground=self.button_text,
            relief="flat",
            font=('Segoe UI', 10, 'bold'),
            padx=20,
            pady=8,
            borderwidth=0,
            highlightthickness=0
        )
        self.connect_btn.pack(pady=10)
        
        # Add hover effect - FIXED THE EXTRA PARENTHESIS HERE
        self.connect_btn.bind("<Enter>", lambda e: self.connect_btn.config(bg=self.button_hover))
        self.connect_btn.bind("<Leave>", lambda e: self.connect_btn.config(bg=self.button_color))
        
        # Status label
        self.status_label = tk.Label(
            self.main_frame,
            text="Ready to connect",
            bg=self.bg_color,
            fg="#666666",
            font=('Segoe UI', 9)
        )
        self.status_label.pack(pady=10)
        
        # Progress bar
        self.progress = ttk.Progressbar(
            self.main_frame,
            orient='horizontal',
            mode='determinate',
            length=200
        )
    
    def start_connection(self):
        """Start the connection process in a separate thread"""
        self.connect_btn.config(state='disabled')
        self.status_label.config(text="Connecting...", fg="#333333")
        self.progress.pack(pady=10)
        self.progress.start(10)
        
        # Run connection in separate thread to prevent UI freezing
        threading.Thread(target=self.connect_to_network, daemon=True).start()
    
    def connect_to_network(self):
        """Connect to the hidden network"""
        try:
            # Create XML profile
            xml_profile = """<?xml version="1.0"?>
<WLANProfile xmlns="http://www.microsoft.com/networking/WLAN/profile/v1">
  <name>TN-MM6210</name>
  <SSIDConfig>
    <SSID>
      <hex>544e2d4d4d36323130</hex>
      <name>TN-MM6210</name>
    </SSID>
    <nonBroadcast>true</nonBroadcast>
  </SSIDConfig>
  <connectionType>ESS</connectionType>
  <connectionMode>manual</connectionMode>
  <MSM>
    <security>
      <authEncryption>
        <authentication>WPA2PSK</authentication>
        <encryption>AES</encryption>
        <useOneX>false</useOneX>
      </authEncryption>
      <sharedKey>
        <keyType>passPhrase</keyType>
        <protected>false</protected>
        <keyMaterial>RFDyz2q3SOkA0ZxWlSqbmUevMrVhSschXI21EtgVmozni7c78G</keyMaterial>
      </sharedKey>
    </security>
  </MSM>
</WLANProfile>"""
            
            # Save to temp file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as f:
                profile_path = f.name
                f.write(xml_profile)
            
            # Execute commands
            commands = [
                f'netsh wlan delete profile name="TN-MM6210"',
                f'netsh wlan add profile filename="{profile_path}"',
                'netsh wlan connect name="TN-MM6210"'
            ]
            
            for cmd in commands:
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                if result.returncode != 0 and "not found" not in result.stderr:
                    raise subprocess.CalledProcessError(
                        result.returncode, cmd, result.stderr
                    )
            
            # Clean up
            try:
                import os
                os.remove(profile_path)
            except:
                pass
            
            # Update UI on success
            self.root.after(0, self.connection_success)
            
        except Exception as e:
            self.root.after(0, self.connection_failed, str(e))
    
    def connection_success(self):
        """Handle successful connection"""
        self.progress.stop()
        self.progress.pack_forget()
        self.status_label.config(text="Successfully connected!", fg=self.success_color)
        self.connect_btn.config(state='normal')
        
    def connection_failed(self, error):
        """Handle failed connection"""
        self.progress.stop()
        self.progress.pack_forget()
        self.status_label.config(text="Connection failed", fg=self.error_color)
        self.connect_btn.config(state='normal')
        messagebox.showerror(
            "Connection Error",
            f"Failed to connect to TN-MM6210:\n\n{error}\n\n"
            "Please ensure:\n"
            "1. WiFi is enabled\n"
            "2. You're in range\n"
            "3. The password is correct"
        )

def is_admin():
    """Check if running as admin"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def main():
    if not is_admin():
        # Re-run as admin
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, " ".join(sys.argv), None, 1
        )
        sys.exit()
    
    root = tk.Tk()
    app = HiddenNetworkConnector(root)
    root.mainloop()

if __name__ == "__main__":
    main()