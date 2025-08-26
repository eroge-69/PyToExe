#!/usr/bin/env python3
"""
Warp CLI GUI Control Application
A simple GUI application to control and monitor Cloudflare Warp CLI on Linux
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import subprocess
import json
import threading
import time
import re
from datetime import datetime
import requests
import os

class WarpControlApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Warp CLI Control")
        self.root.geometry("600x700")
        self.root.resizable(True, True)
        
        # Theme variables
        self.current_theme = "auto"  # auto, light, dark
        self.themes = {
            "light": {
                "bg": "#ffffff",
                "fg": "#000000",
                "select_bg": "#0078d4",
                "select_fg": "#ffffff",
                "button_bg": "#f0f0f0",
                "entry_bg": "#ffffff",
                "frame_bg": "#f5f5f5"
            },
            "dark": {
                "bg": "#2d2d2d",
                "fg": "#ffffff",
                "select_bg": "#404040",
                "select_fg": "#ffffff",
                "button_bg": "#404040",
                "entry_bg": "#3d3d3d",
                "frame_bg": "#353535"
            }
        }
        
        # Application state
        self.warp_status = {}
        self.current_ip = "Unknown"
        self.warp_ip = "Unknown"
        self.update_running = True
        
        # Create GUI
        self.create_widgets()
        self.apply_theme()
        self.start_status_updates()
        
        # Handle window close
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def create_widgets(self):
        # Main container
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Top frame for settings button and title
        top_frame = ttk.Frame(main_frame)
        top_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Settings button
        self.settings_btn = ttk.Button(top_frame, text="⚙", width=3, command=self.open_settings)
        self.settings_btn.pack(side=tk.LEFT)
        
        # Theme toggle button
        self.theme_btn = ttk.Button(top_frame, text="🌓", width=3, command=self.toggle_theme)
        self.theme_btn.pack(side=tk.LEFT, padx=(5, 0))
        
        # Title
        title_label = ttk.Label(top_frame, text="Warp CLI Control Center", font=("Arial", 16, "bold"))
        title_label.pack(side=tk.LEFT, padx=(20, 0))
        
        # Status frame
        status_frame = ttk.LabelFrame(main_frame, text="Connection Status", padding=10)
        status_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.status_label = ttk.Label(status_frame, text="Checking status...", font=("Arial", 12))
        self.status_label.pack()
        
        # Control buttons frame
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.connect_btn = ttk.Button(control_frame, text="Connect", command=self.connect_warp, width=15)
        self.connect_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.disconnect_btn = ttk.Button(control_frame, text="Disconnect", command=self.disconnect_warp, width=15)
        self.disconnect_btn.pack(side=tk.LEFT)
        
        # Server location frame
        location_frame = ttk.LabelFrame(main_frame, text="Server Location", padding=10)
        location_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.location_label = ttk.Label(location_frame, text="Location: Unknown", font=("Arial", 10))
        self.location_label.pack()
        
        # IP Information frame
        ip_frame = ttk.LabelFrame(main_frame, text="IP Information", padding=10)
        ip_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.current_ip_label = ttk.Label(ip_frame, text="Current IP: Checking...", font=("Arial", 10))
        self.current_ip_label.pack(anchor=tk.W)
        
        self.warp_ip_label = ttk.Label(ip_frame, text="Warp IP: Unknown", font=("Arial", 10))
        self.warp_ip_label.pack(anchor=tk.W)
        
        # Additional information frame
        info_frame = ttk.LabelFrame(main_frame, text="Connection Details", padding=10)
        info_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        self.info_text = scrolledtext.ScrolledText(info_frame, height=10, width=50)
        self.info_text.pack(fill=tk.BOTH, expand=True)
        
        # Status bar
        self.status_bar = ttk.Label(main_frame, text="Ready", relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM)
    
    def apply_theme(self):
        """Apply the current theme to the application"""
        if self.current_theme == "auto":
            # Try to detect system theme (simplified approach)
            theme_name = self.detect_system_theme()
        else:
            theme_name = self.current_theme
            
        theme = self.themes[theme_name]
        
        # Configure ttk style
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure colors
        style.configure('TFrame', background=theme['bg'])
        style.configure('TLabel', background=theme['bg'], foreground=theme['fg'])
        style.configure('TButton', background=theme['button_bg'], foreground=theme['fg'])
        style.configure('TLabelFrame', background=theme['bg'], foreground=theme['fg'])
        style.configure('TLabelFrame.Label', background=theme['bg'], foreground=theme['fg'])
        
        self.root.configure(bg=theme['bg'])
        self.info_text.configure(bg=theme['entry_bg'], fg=theme['fg'], insertbackground=theme['fg'])
    
    def detect_system_theme(self):
        """Detect system theme (simplified method for Linux)"""
        try:
            # Try to detect GNOME theme
            result = subprocess.run(['gsettings', 'get', 'org.gnome.desktop.interface', 'gtk-theme'], 
                                  capture_output=True, text=True, timeout=5)
            if 'dark' in result.stdout.lower():
                return "dark"
        except:
            pass
        
        # Default to light theme
        return "light"
    
    def toggle_theme(self):
        """Toggle between light, dark, and auto themes"""
        themes = ["auto", "light", "dark"]
        current_index = themes.index(self.current_theme)
        self.current_theme = themes[(current_index + 1) % len(themes)]
        self.apply_theme()
        self.update_status_bar(f"Theme: {self.current_theme}")
    
    def get_warp_status(self):
        """Get Warp CLI status"""
        try:
            result = subprocess.run(['warp-cli', 'status'], capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                return self.parse_warp_status(result.stdout)
            else:
                return {"error": result.stderr or "Unknown error"}
        except subprocess.TimeoutExpired:
            return {"error": "Command timeout"}
        except FileNotFoundError:
            return {"error": "warp-cli not found. Please install Cloudflare Warp."}
        except Exception as e:
            return {"error": str(e)}
    
    def parse_warp_status(self, status_output):
        """Parse warp-cli status output"""
        status = {}
        lines = status_output.strip().split('\n')
        
        for line in lines:
            if ':' in line:
                key, value = line.split(':', 1)
                status[key.strip()] = value.strip()
        
        return status
    
    def get_current_ip(self):
        """Get current public IP address"""
        try:
            response = requests.get('https://api.ipify.org', timeout=5)
            return response.text.strip()
        except:
            try:
                response = requests.get('https://httpbin.org/ip', timeout=5)
                data = response.json()
                return data.get('origin', 'Unknown')
            except:
                return "Unable to fetch"
    
    def get_ip_info(self, ip):
        """Get IP geolocation information"""
        try:
            response = requests.get(f'http://ip-api.com/json/{ip}', timeout=5)
            if response.status_code == 200:
                return response.json()
        except:
            pass
        return None
    
    def update_status(self):
        """Update application status"""
        self.warp_status = self.get_warp_status()
        
        if "error" in self.warp_status:
            self.status_label.config(text=f"Error: {self.warp_status['error']}", foreground="red")
            self.connect_btn.config(state=tk.DISABLED)
            self.disconnect_btn.config(state=tk.DISABLED)
            self.location_label.config(text="Location: Unknown")
            self.info_text.delete(1.0, tk.END)
            self.info_text.insert(tk.END, f"Error: {self.warp_status['error']}")
            return
        
        # Update status label
        status_text = self.warp_status.get('Status', 'Unknown')
        if 'Connected' in status_text:
            self.status_label.config(text="🟢 Connected", foreground="green")
            self.connect_btn.config(state=tk.DISABLED)
            self.disconnect_btn.config(state=tk.NORMAL)
        elif 'Disconnected' in status_text:
            self.status_label.config(text="🔴 Disconnected", foreground="red")
            self.connect_btn.config(state=tk.NORMAL)
            self.disconnect_btn.config(state=tk.DISABLED)
        else:
            self.status_label.config(text=f"⚪ {status_text}", foreground="orange")
            self.connect_btn.config(state=tk.NORMAL)
            self.disconnect_btn.config(state=tk.NORMAL)
        
        # Update server location
        location = "Unknown"
        if 'Connected' in status_text:
            # Try to get location from various possible fields
            for key in ['WarpPlus', 'Endpoint', 'Location']:
                if key in self.warp_status:
                    location = self.warp_status[key]
                    break
        
        self.location_label.config(text=f"Location: {location}")
        
        # Update IP information
        current_ip = self.get_current_ip()
        self.current_ip = current_ip
        self.current_ip_label.config(text=f"Current IP: {current_ip}")
        
        if 'Connected' in status_text and current_ip != "Unable to fetch":
            self.warp_ip = current_ip
            self.warp_ip_label.config(text=f"Warp IP: {current_ip}")
        else:
            self.warp_ip_label.config(text="Warp IP: Not connected")
        
        # Update detailed information
        self.update_info_text()
    
    def update_info_text(self):
        """Update the detailed information text area"""
        self.info_text.delete(1.0, tk.END)
        
        info_text = f"Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        if "error" not in self.warp_status:
            info_text += "=== Warp CLI Status ===\n"
            for key, value in self.warp_status.items():
                info_text += f"{key}: {value}\n"
            
            # Add IP geolocation info
            if self.current_ip != "Unable to fetch":
                ip_info = self.get_ip_info(self.current_ip)
                if ip_info:
                    info_text += "\n=== IP Geolocation ===\n"
                    for key in ['country', 'regionName', 'city', 'isp', 'org']:
                        if key in ip_info:
                            info_text += f"{key.title()}: {ip_info[key]}\n"
        else:
            info_text += f"Error: {self.warp_status['error']}"
        
        self.info_text.insert(tk.END, info_text)
    
    def connect_warp(self):
        """Connect to Warp"""
        self.update_status_bar("Connecting...")
        threading.Thread(target=self._connect_warp, daemon=True).start()
    
    def _connect_warp(self):
        """Connect to Warp (threaded)"""
        try:
            result = subprocess.run(['warp-cli', 'connect'], capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                self.root.after(0, lambda: self.update_status_bar("Connected successfully"))
            else:
                error_msg = result.stderr or "Connection failed"
                self.root.after(0, lambda: messagebox.showerror("Connection Error", error_msg))
                self.root.after(0, lambda: self.update_status_bar("Connection failed"))
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", str(e)))
            self.root.after(0, lambda: self.update_status_bar("Connection error"))
        
        # Update status after connection attempt
        self.root.after(2000, self.update_status)
    
    def disconnect_warp(self):
        """Disconnect from Warp"""
        self.update_status_bar("Disconnecting...")
        threading.Thread(target=self._disconnect_warp, daemon=True).start()
    
    def _disconnect_warp(self):
        """Disconnect from Warp (threaded)"""
        try:
            result = subprocess.run(['warp-cli', 'disconnect'], capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                self.root.after(0, lambda: self.update_status_bar("Disconnected successfully"))
            else:
                error_msg = result.stderr or "Disconnection failed"
                self.root.after(0, lambda: messagebox.showerror("Disconnection Error", error_msg))
                self.root.after(0, lambda: self.update_status_bar("Disconnection failed"))
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", str(e)))
            self.root.after(0, lambda: self.update_status_bar("Disconnection error"))
        
        # Update status after disconnection attempt
        self.root.after(2000, self.update_status)
    
    def open_settings(self):
        """Open settings window"""
        settings_window = SettingsWindow(self.root, self)
    
    def start_status_updates(self):
        """Start periodic status updates"""
        self.update_status()
        if self.update_running:
            self.root.after(10000, self.start_status_updates)  # Update every 10 seconds
    
    def update_status_bar(self, message):
        """Update status bar message"""
        self.status_bar.config(text=message)
    
    def on_closing(self):
        """Handle application closing"""
        self.update_running = False
        self.root.destroy()


class SettingsWindow:
    def __init__(self, parent, main_app):
        self.parent = parent
        self.main_app = main_app
        
        self.window = tk.Toplevel(parent)
        self.window.title("Warp CLI Settings")
        self.window.geometry("500x600")
        self.window.transient(parent)
        self.window.grab_set()
        
        self.create_widgets()
        self.load_current_settings()
    
    def create_widgets(self):
        # Main frame
        main_frame = ttk.Frame(self.window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Title
        title_label = ttk.Label(main_frame, text="Warp CLI Settings", font=("Arial", 14, "bold"))
        title_label.pack(pady=(0, 10))
        
        # Mode settings
        mode_frame = ttk.LabelFrame(main_frame, text="Connection Mode", padding=10)
        mode_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.mode_var = tk.StringVar()
        modes = [("Warp", "warp"), ("Warp+", "warp+"), ("Proxy", "proxy"), ("DNS Only", "doh")]
        
        for text, value in modes:
            ttk.Radiobutton(mode_frame, text=text, variable=self.mode_var, value=value).pack(anchor=tk.W)
        
        # Registration settings
        reg_frame = ttk.LabelFrame(main_frame, text="Registration", padding=10)
        reg_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(reg_frame, text="Register Device", command=self.register_device).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(reg_frame, text="Reset Registration", command=self.reset_registration).pack(side=tk.LEFT)
        
        # Proxy settings
        proxy_frame = ttk.LabelFrame(main_frame, text="Proxy Settings", padding=10)
        proxy_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(proxy_frame, text="Proxy Port:").pack(anchor=tk.W)
        self.proxy_port_var = tk.StringVar(value="40000")
        ttk.Entry(proxy_frame, textvariable=self.proxy_port_var, width=20).pack(anchor=tk.W, pady=(0, 5))
        
        # DNS settings
        dns_frame = ttk.LabelFrame(main_frame, text="DNS Settings", padding=10)
        dns_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.families_var = tk.BooleanVar()
        ttk.Checkbutton(dns_frame, text="Enable Families Mode", variable=self.families_var).pack(anchor=tk.W)
        
        # Account settings
        account_frame = ttk.LabelFrame(main_frame, text="Account", padding=10)
        account_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(account_frame, text="Team Name:").pack(anchor=tk.W)
        self.team_var = tk.StringVar()
        ttk.Entry(account_frame, textvariable=self.team_var, width=30).pack(anchor=tk.W, pady=(0, 5))
        
        # Current settings display
        current_frame = ttk.LabelFrame(main_frame, text="Current Settings", padding=10)
        current_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        self.settings_text = scrolledtext.ScrolledText(current_frame, height=8, width=50)
        self.settings_text.pack(fill=tk.BOTH, expand=True)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        ttk.Button(button_frame, text="Apply Settings", command=self.apply_settings).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="Refresh", command=self.load_current_settings).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="Close", command=self.window.destroy).pack(side=tk.RIGHT)
    
    def load_current_settings(self):
        """Load current warp-cli settings"""
        try:
            # Get current settings
            result = subprocess.run(['warp-cli', 'settings'], capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                self.settings_text.delete(1.0, tk.END)
                self.settings_text.insert(tk.END, result.stdout)
            
            # Get account info
            account_result = subprocess.run(['warp-cli', 'account'], capture_output=True, text=True, timeout=10)
            if account_result.returncode == 0:
                self.settings_text.insert(tk.END, "\n=== Account Information ===\n")
                self.settings_text.insert(tk.END, account_result.stdout)
                
        except Exception as e:
            self.settings_text.delete(1.0, tk.END)
            self.settings_text.insert(tk.END, f"Error loading settings: {str(e)}")
    
    def apply_settings(self):
        """Apply selected settings"""
        try:
            # Apply mode
            mode = self.mode_var.get()
            if mode:
                subprocess.run(['warp-cli', 'set-mode', mode], check=True, timeout=10)
            
            # Apply proxy port
            port = self.proxy_port_var.get()
            if port and port.isdigit():
                subprocess.run(['warp-cli', 'set-proxy-port', port], check=True, timeout=10)
            
            # Apply families mode
            if self.families_var.get():
                subprocess.run(['warp-cli', 'set-families-mode', 'on'], check=True, timeout=10)
            else:
                subprocess.run(['warp-cli', 'set-families-mode', 'off'], check=True, timeout=10)
            
            messagebox.showinfo("Success", "Settings applied successfully!")
            self.load_current_settings()
            
        except subprocess.CalledProcessError as e:
            messagebox.showerror("Error", f"Failed to apply settings: {e}")
        except Exception as e:
            messagebox.showerror("Error", f"Error: {str(e)}")
    
    def register_device(self):
        """Register device with Warp"""
        try:
            result = subprocess.run(['warp-cli', 'register'], capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                messagebox.showinfo("Success", "Device registered successfully!")
            else:
                messagebox.showerror("Error", f"Registration failed: {result.stderr}")
        except Exception as e:
            messagebox.showerror("Error", f"Registration error: {str(e)}")
    
    def reset_registration(self):
        """Reset device registration"""
        if messagebox.askyesno("Confirm", "Are you sure you want to reset registration? This will disconnect and require re-registration."):
            try:
                result = subprocess.run(['warp-cli', 'delete'], capture_output=True, text=True, timeout=30)
                if result.returncode == 0:
                    messagebox.showinfo("Success", "Registration reset successfully!")
                else:
                    messagebox.showerror("Error", f"Reset failed: {result.stderr}")
            except Exception as e:
                messagebox.showerror("Error", f"Reset error: {str(e)}")


def main():
    root = tk.Tk()
    app = WarpControlApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
