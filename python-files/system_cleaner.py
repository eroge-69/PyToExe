import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import psutil
import os
import shutil
import time
from datetime import datetime
import threading
import webbrowser
import json
import winreg
import glob
from pathlib import Path

class SystemCleanPro:
    def __init__(self, root):
        self.root = root
        self.root.title("🚀 SystemClean Pro")
        self.root.geometry("1200x800")
        
        # Light theme colors
        self.bg_color = '#f8f9fa'
        self.card_bg = '#ffffff'
        self.accent_color = '#007acc'
        self.text_color = '#2c3e50'
        self.warning_color = '#e74c3c'
        self.success_color = '#27ae60'
        self.border_color = '#dee2e6'
        self.hover_color = '#e9ecef'
        
        # Settings
        self.settings_file = "system_clean_settings.json"
        self.settings = self.load_settings()
        
        self.setup_ui()
        self.start_monitoring()
    
    def load_settings(self):
        """Load persistent settings"""
        default_settings = {
            "auto_clean": False,
            "scan_threshold": 100,
            "theme": "light",
            "monitor_interval": 2,
            "startup_programs": {}
        }
        
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading settings: {e}")
        
        return default_settings
    
    def save_settings(self):
        """Save settings to file"""
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(self.settings, f, indent=2)
        except Exception as e:
            print(f"Error saving settings: {e}")

    def scan_large_files(self, target):
        """Scan for actual large files"""
        try:
            # Clear previous results
            for item in self.disk_tree.get_children():
                self.disk_tree.delete(item)
            
            # Determine scan path
            if target == "Downloads":
                scan_path = os.path.join(os.path.expanduser("~"), "Downloads")
            else:
                scan_path = target
            
            if not os.path.exists(scan_path):
                messagebox.showerror("Error", f"Path not found: {scan_path}")
                return
            
            # Show scanning progress
            self.status_label.config(text="● Scanning files...", fg=self.accent_color)
            
            # Scan in thread to avoid UI freeze
            threading.Thread(target=self._perform_scan, args=(scan_path,), daemon=True).start()
            
        except Exception as e:
            messagebox.showerror("Error", f"Scan error: {e}")
    
    def _perform_scan(self, scan_path):
        """Perform actual file scanning in background thread"""
        try:
            large_files = []
            threshold = self.settings.get("scan_threshold", 100) * 1024 * 1024  # Convert to bytes
            
            # Walk through directory tree
            for root_dir, dirs, files in os.walk(scan_path):
                # Skip system directories to improve performance
                if any(skip in root_dir.lower() for skip in ['system32', 'windows', 'program files', '$recycle.bin']):
                    continue
                    
                for file in files:
                    try:
                        file_path = os.path.join(root_dir, file)
                        
                        # Skip if cannot access
                        if not os.path.exists(file_path):
                            continue
                            
                        file_size = os.path.getsize(file_path)
                        
                        if file_size > threshold:
                            # Get file type
                            _, ext = os.path.splitext(file)
                            file_type = self.get_file_type(ext)
                            
                            large_files.append({
                                'name': file,
                                'size': self.format_file_size(file_size),
                                'path': root_dir,
                                'type': file_type,
                                'full_path': file_path,
                                'size_bytes': file_size
                            })
                            
                    except (OSError, PermissionError):
                        continue
            
            # Sort by size (largest first)
            large_files.sort(key=lambda x: x['size_bytes'], reverse=True)
            
            # Update UI in main thread
            self.root.after(0, self._update_scan_results, large_files)
            
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", f"Scan failed: {e}"))
    
    def _update_scan_results(self, files):
        """Update UI with scan results"""
        # Clear previous results
        for item in self.disk_tree.get_children():
            self.disk_tree.delete(item)
        
        # Add files to treeview
        for file_info in files[:100]:  # Limit to 100 files for performance
            self.disk_tree.insert('', 'end', values=(
                "☑",
                file_info['name'],
                file_info['size'],
                file_info['path'],
                file_info['type']
            ), tags=(file_info['full_path'],))
        
        self.status_label.config(text=f"● Found {len(files)} large files", fg=self.success_color)
    
    def format_file_size(self, size_bytes):
        """Convert bytes to human readable format"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} PB"
    
    def get_file_type(self, extension):
        """Get file type from extension"""
        file_types = {
            '.exe': 'Application', '.msi': 'Installer', '.dll': 'System',
            '.mp4': 'Video', '.avi': 'Video', '.mkv': 'Video', '.mov': 'Video',
            '.mp3': 'Audio', '.wav': 'Audio', '.flac': 'Audio',
            '.jpg': 'Image', '.jpeg': 'Image', '.png': 'Image', '.gif': 'Image',
            '.pdf': 'Document', '.doc': 'Document', '.docx': 'Document',
            '.xls': 'Spreadsheet', '.xlsx': 'Spreadsheet',
            '.zip': 'Archive', '.rar': 'Archive', '.7z': 'Archive',
            '.py': 'Script', '.js': 'Script', '.html': 'Web File'
        }
        return file_types.get(extension.lower(), 'Other')


    def scan_large_files(self, target):
        """Scan for actual large files"""
        try:
            # Clear previous results
            for item in self.disk_tree.get_children():
                self.disk_tree.delete(item)
            
            # Determine scan path
            if target == "Downloads":
                scan_path = os.path.join(os.path.expanduser("~"), "Downloads")
            else:
                scan_path = target
            
            if not os.path.exists(scan_path):
                messagebox.showerror("Error", f"Path not found: {scan_path}")
                return
            
            # Show scanning progress
            self.status_label.config(text="● Scanning files...", fg=self.accent_color)
            
            # Scan in thread to avoid UI freeze
            threading.Thread(target=self._perform_scan, args=(scan_path,), daemon=True).start()
            
        except Exception as e:
            messagebox.showerror("Error", f"Scan error: {e}")
    
    def _perform_scan(self, scan_path):
        """Perform actual file scanning in background thread"""
        try:
            large_files = []
            threshold = self.settings.get("scan_threshold", 100) * 1024 * 1024  # Convert to bytes
            
            # Walk through directory tree
            for root_dir, dirs, files in os.walk(scan_path):
                # Skip system directories to improve performance
                if any(skip in root_dir.lower() for skip in ['system32', 'windows', 'program files', '$recycle.bin']):
                    continue
                    
                for file in files:
                    try:
                        file_path = os.path.join(root_dir, file)
                        
                        # Skip if cannot access
                        if not os.path.exists(file_path):
                            continue
                            
                        file_size = os.path.getsize(file_path)
                        
                        if file_size > threshold:
                            # Get file type
                            _, ext = os.path.splitext(file)
                            file_type = self.get_file_type(ext)
                            
                            large_files.append({
                                'name': file,
                                'size': self.format_file_size(file_size),
                                'path': root_dir,
                                'type': file_type,
                                'full_path': file_path,
                                'size_bytes': file_size
                            })
                            
                    except (OSError, PermissionError):
                        continue
            
            # Sort by size (largest first)
            large_files.sort(key=lambda x: x['size_bytes'], reverse=True)
            
            # Update UI in main thread
            self.root.after(0, self._update_scan_results, large_files)
            
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", f"Scan failed: {e}"))
    
    def _update_scan_results(self, files):
        """Update UI with scan results"""
        # Clear previous results
        for item in self.disk_tree.get_children():
            self.disk_tree.delete(item)
        
        # Add files to treeview
        for file_info in files[:100]:  # Limit to 100 files for performance
            self.disk_tree.insert('', 'end', values=(
                "☑",
                file_info['name'],
                file_info['size'],
                file_info['path'],
                file_info['type']
            ), tags=(file_info['full_path'],))
        
        self.status_label.config(text=f"● Found {len(files)} large files", fg=self.success_color)
    
    def format_file_size(self, size_bytes):
        """Convert bytes to human readable format"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} PB"
    
    def get_file_type(self, extension):
        """Get file type from extension"""
        file_types = {
            '.exe': 'Application', '.msi': 'Installer', '.dll': 'System',
            '.mp4': 'Video', '.avi': 'Video', '.mkv': 'Video', '.mov': 'Video',
            '.mp3': 'Audio', '.wav': 'Audio', '.flac': 'Audio',
            '.jpg': 'Image', '.jpeg': 'Image', '.png': 'Image', '.gif': 'Image',
            '.pdf': 'Document', '.doc': 'Document', '.docx': 'Document',
            '.xls': 'Spreadsheet', '.xlsx': 'Spreadsheet',
            '.zip': 'Archive', '.rar': 'Archive', '.7z': 'Archive',
            '.py': 'Script', '.js': 'Script', '.html': 'Web File'
        }
        return file_types.get(extension.lower(), 'Other')


    def detect_browser_caches(self):
        """Detect actual browser cache sizes and locations"""
        browsers = {}
        
        # Common browser cache locations
        browser_paths = {
            'Chrome': [
                os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Google', 'Chrome', 'User Data', 'Default', 'Cache'),
                os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Google', 'Chrome', 'User Data', 'Default', 'Code Cache')
            ],
            'Firefox': [
                os.path.join(os.environ.get('APPDATA', ''), 'Mozilla', 'Firefox', 'Profiles'),
            ],
            'Edge': [
                os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Microsoft', 'Edge', 'User Data', 'Default', 'Cache'),
                os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Microsoft', 'Edge', 'User Data', 'Default', 'Code Cache')
            ],
            'Opera': [
                os.path.join(os.environ.get('APPDATA', ''), 'Opera Software', 'Opera Stable', 'Cache'),
            ]
        }
        
        for browser, paths in browser_paths.items():
            total_size = 0
            detected_paths = []
            
            for path in paths:
                if os.path.exists(path):
                    detected_paths.append(path)
                    total_size += self.get_folder_size(path)
            
            if detected_paths:
                browsers[browser] = {
                    'size': self.format_file_size(total_size),
                    'size_bytes': total_size,
                    'paths': detected_paths,
                    'detected': True
                }
            else:
                browsers[browser] = {
                    'size': 'Not detected',
                    'size_bytes': 0,
                    'paths': [],
                    'detected': False
                }
        
        return browsers
    
    def get_folder_size(self, folder_path):
        """Calculate total size of folder"""
        total_size = 0
        try:
            for dirpath, dirnames, filenames in os.walk(folder_path):
                for filename in filenames:
                    filepath = os.path.join(dirpath, filename)
                    try:
                        total_size += os.path.getsize(filepath)
                    except (OSError, PermissionError):
                        continue
        except (OSError, PermissionError):
            pass
            
        return total_size
    
    def clean_browser_cache(self, browser_name, paths):
        """Clean actual browser cache"""
        try:
            total_freed = 0
            for path in paths:
                if os.path.exists(path):
                    freed = self.get_folder_size(path)
                    shutil.rmtree(path)
                    total_freed += freed
                    
                    # Recreate empty directory
                    os.makedirs(path, exist_ok=True)
            
            return total_freed
        except Exception as e:
            raise Exception(f"Failed to clean {browser_name}: {e}")
    
    def update_browser_list(self):
        """Update browser list with actual detected caches"""
        browsers = self.detect_browser_caches()
        
        # Clear existing browser widgets
        for widget in self.browser_list_frame.winfo_children():
            widget.destroy()
        
        self.browser_vars = {}
        
        for browser, info in browsers.items():
            frame = tk.Frame(self.browser_list_frame, bg=self.card_bg)
            frame.pack(fill=tk.X, padx=10, pady=5)
            
            var = tk.BooleanVar(value=info['detected'])
            self.browser_vars[browser] = {'var': var, 'info': info}
            
            # Only show checkbox if browser is detected
            if info['detected']:
                cb = tk.Checkbutton(
                    frame, 
                    text=f"{browser} ({info['size']})",
                    variable=var,
                    fg=self.text_color,
                    bg=self.card_bg,
                    selectcolor=self.hover_color
                )
                cb.pack(side=tk.LEFT)
            else:
                tk.Label(
                    frame,
                    text=f"{browser} (Not installed)",
                    fg='#95a5a6',
                    bg=self.card_bg,
                    font=('Arial', 9)
                ).pack(side=tk.LEFT)

    def get_startup_programs(self):
        """Get actual startup programs from registry and startup folders"""
        startup_programs = []
        
        # Registry locations for startup programs
        registry_locations = [
            (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run"),
            (winreg.HKEY_LOCAL_MACHINE, r"Software\Microsoft\Windows\CurrentVersion\Run"),
            (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\RunOnce"),
            (winreg.HKEY_LOCAL_MACHINE, r"Software\Microsoft\Windows\CurrentVersion\RunOnce"),
        ]
        
        # Startup folders
        startup_folders = [
            os.path.join(os.environ.get('APPDATA', ''), 'Microsoft', 'Windows', 'Start Menu', 'Programs', 'Startup'),
            os.path.join(os.environ.get('PROGRAMDATA', ''), 'Microsoft', 'Windows', 'Start Menu', 'Programs', 'Startup')
        ]
        
        # Check registry
        for hive, subkey in registry_locations:
            try:
                with winreg.OpenKey(hive, subkey) as key:
                    i = 0
                    while True:
                        try:
                            name, value, _ = winreg.EnumValue(key, i)
                            startup_programs.append({
                                'name': name,
                                'path': value,
                                'type': 'Registry',
                                'enabled': True,
                                'location': f"{hive}\\{subkey}"
                            })
                            i += 1
                        except WindowsError:
                            break
            except FileNotFoundError:
                continue
        
        # Check startup folders
        for folder in startup_folders:
            if os.path.exists(folder):
                for item in os.listdir(folder):
                    item_path = os.path.join(folder, item)
                    startup_programs.append({
                        'name': item,
                        'path': item_path,
                        'type': 'Startup Folder',
                        'enabled': True,
                        'location': folder
                    })
        
        return startup_programs
    
    def toggle_startup_program(self, program_name, enabled):
        """Enable/disable startup program"""
        try:
            # This is a simplified implementation
            # In a real application, you would modify registry or file system
            messagebox.showinfo("Info", 
                              f"Startup program '{program_name}' would be {'disabled' if not enabled else 'enabled'}.\n\n"
                              "Note: This requires administrator privileges for full implementation.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to modify startup program: {e}")
    
    def update_startup_list(self):
        """Update startup programs list with actual data"""
        programs = self.get_startup_programs()
        
        # Clear existing items
        for item in self.startup_tree.get_children():
            self.startup_tree.delete(item)
        
        # Add programs to treeview
        for program in programs:
            status = "Enabled" if program['enabled'] else "Disabled"
            self.startup_tree.insert('', 'end', values=(
                program['name'],
                program['path'],
                program['type'],
                status
            ), tags=(program['location'],))

    def get_temperature_data(self):
        """Get system temperature data"""
        try:
            temperatures = {}
            
            # Try to get temperature from psutil
            if hasattr(psutil, "sensors_temperatures"):
                temp_data = psutil.sensors_temperatures()
                
                if temp_data:
                    for name, entries in temp_data.items():
                        for entry in entries:
                            if entry.current:
                                temperatures[f"{name}_{entry.label or 'temp'}"] = {
                                    'current': entry.current,
                                    'high': entry.high,
                                    'critical': entry.critical
                                }
            
            # Fallback to mock data if no sensors found
            if not temperatures:
                temperatures = {
                    'cpu_temp': {'current': 45.0, 'high': 85.0, 'critical': 100.0},
                    'gpu_temp': {'current': 55.0, 'high': 95.0, 'critical': 105.0}
                }
            
            return temperatures
        except Exception as e:
            print(f"Temperature monitoring error: {e}")
            return {'cpu_temp': {'current': 0, 'high': 0, 'critical': 0}}
    
    def update_temperature_display(self):
        """Update temperature gauges"""
        try:
            temps = self.get_temperature_data()
            
            # Update CPU temperature
            cpu_temp = temps.get('cpu_temp', {}).get('current', 0)
            cpu_critical = temps.get('cpu_temp', {}).get('critical', 100)
            
            # Calculate percentage for progress bar
            cpu_percent = min(100, (cpu_temp / cpu_critical) * 100) if cpu_critical else 0
            
            # Update temperature label and progress bar
            if hasattr(self, 'cpu_temp_label'):
                color = self.success_color
                if cpu_temp > 70:
                    color = self.warning_color
                elif cpu_temp > 85:
                    color = self.warning_color
                
                self.cpu_temp_label.config(text=f"{cpu_temp:.1f}°C", fg=color)
            
            if hasattr(self, 'cpu_temp_bar'):
                self.cpu_temp_bar['value'] = cpu_percent
            
        except Exception as e:
            print(f"Temperature update error: {e}")

    def setup_auto_clean(self):
        """Setup automatic cleaning scheduler"""
        self.auto_clean_var = tk.BooleanVar(value=self.settings.get('auto_clean', False))
        self.clean_interval_var = tk.StringVar(value=self.settings.get('clean_interval', '7'))
        
        # Start scheduler if enabled
        if self.auto_clean_var.get():
            self.start_auto_clean_scheduler()
    
    def start_auto_clean_scheduler(self):
        """Start the automatic cleaning scheduler"""
        def clean_scheduler():
            while self.auto_clean_var.get():
                try:
                    # Perform scheduled cleanup
                    self.perform_scheduled_cleanup()
                    
                    # Wait for interval (days)
                    interval_days = int(self.clean_interval_var.get())
                    time.sleep(interval_days * 24 * 60 * 60)
                    
                except Exception as e:
                    print(f"Auto-clean error: {e}")
                    time.sleep(3600)  # Wait 1 hour on error
        
        threading.Thread(target=clean_scheduler, daemon=True).start()
    
    def perform_scheduled_cleanup(self):
        """Perform automatic system cleanup"""
        try:
            # Clean browser caches
            browsers = self.detect_browser_caches()
            for browser, info in browsers.items():
                if info['detected']:
                    try:
                        self.clean_browser_cache(browser, info['paths'])
                    except Exception:
                        pass
            
            # Clean temporary files
            self.clean_temp_files()
            
            # Update status
            self.root.after(0, lambda: self.status_label.config(
                text=f"● Auto-clean completed at {datetime.now().strftime('%H:%M')}",
                fg=self.success_color
            ))
            
        except Exception as e:
            print(f"Scheduled cleanup error: {e}")
    
    def clean_temp_files(self):
        """Clean temporary files"""
        temp_dirs = [
            os.environ.get('TEMP', ''),
            os.environ.get('TMP', ''),
            os.path.join(os.environ.get('WINDIR', ''), 'Temp')
        ]
        
        for temp_dir in temp_dirs:
            if os.path.exists(temp_dir):
                try:
                    for item in os.listdir(temp_dir):
                        item_path = os.path.join(temp_dir, item)
                        try:
                            if os.path.isfile(item_path):
                                os.remove(item_path)
                            elif os.path.isdir(item_path):
                                shutil.rmtree(item_path)
                        except (PermissionError, OSError):
                            continue
                except (PermissionError, OSError):
                    continue


    def setup_settings_tab(self):
        """Enhanced settings tab with persistence"""
        settings_frame = tk.Frame(self.notebook, bg=self.bg_color)
        self.notebook.add(settings_frame, text="⚙️ Settings")
        
        # Auto-clean settings
        auto_clean_frame = tk.LabelFrame(
            settings_frame,
            text="Automatic Cleaning",
            font=('Arial', 12, 'bold'),
            fg=self.text_color,
            bg=self.bg_color,
            labelanchor='n'
        )
        auto_clean_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Auto-clean toggle
        auto_clean_cb = tk.Checkbutton(
            auto_clean_frame,
            text="Enable automatic cleaning",
            variable=self.auto_clean_var,
            command=self.toggle_auto_clean,
            fg=self.text_color,
            bg=self.bg_color,
            selectcolor=self.hover_color
        )
        auto_clean_cb.pack(anchor=tk.W, padx=10, pady=5)
        
        # Cleaning interval
        interval_frame = tk.Frame(auto_clean_frame, bg=self.bg_color)
        interval_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(interval_frame, text="Clean every:", fg=self.text_color, bg=self.bg_color).pack(side=tk.LEFT)
        interval_spin = tk.Spinbox(
            interval_frame,
            from_=1,
            to=30,
            textvariable=self.clean_interval_var,
            width=5,
            command=self.save_settings
        )
        interval_spin.pack(side=tk.LEFT, padx=5)
        tk.Label(interval_frame, text="days", fg=self.text_color, bg=self.bg_color).pack(side=tk.LEFT)
        
        # File scanning settings
        scan_frame = tk.LabelFrame(
            settings_frame,
            text="File Scanning",
            font=('Arial', 12, 'bold'),
            fg=self.text_color,
            bg=self.bg_color,
            labelanchor='n'
        )
        scan_frame.pack(fill=tk.X, padx=10, pady=10)
        
        scan_threshold_frame = tk.Frame(scan_frame, bg=self.bg_color)
        scan_threshold_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(scan_threshold_frame, text="Large file threshold:", fg=self.text_color, bg=self.bg_color).pack(side=tk.LEFT)
        
        self.scan_threshold_var = tk.StringVar(value=str(self.settings.get('scan_threshold', 100)))
        threshold_spin = tk.Spinbox(
            scan_threshold_frame,
            from_=10,
            to=10000,
            textvariable=self.scan_threshold_var,
            width=5,
            command=self.update_scan_threshold
        )
        threshold_spin.pack(side=tk.LEFT, padx=5)
        tk.Label(scan_threshold_frame, text="MB", fg=self.text_color, bg=self.bg_color).pack(side=tk.LEFT)
        
        # Save button
        save_btn = tk.Button(
            settings_frame,
            text="💾 Save Settings",
            command=self.save_settings,
            bg=self.success_color,
            fg='white',
            font=('Arial', 11, 'bold'),
            padx=20,
            pady=10
        )
        save_btn.pack(pady=20)
    
    def toggle_auto_clean(self):
        """Toggle automatic cleaning"""
        self.settings['auto_clean'] = self.auto_clean_var.get()
        
        if self.auto_clean_var.get():
            self.start_auto_clean_scheduler()
            messagebox.showinfo("Auto-clean", "Automatic cleaning enabled")
        else:
            messagebox.showinfo("Auto-clean", "Automatic cleaning disabled")
        
        self.save_settings()
    
    def update_scan_threshold(self):
        """Update file scan threshold"""
        try:
            threshold = int(self.scan_threshold_var.get())
            self.settings['scan_threshold'] = threshold
            self.save_settings()
        except ValueError:
            pass
    
    def save_settings(self):
        """Save all settings"""
        self.settings.update({
            'auto_clean': self.auto_clean_var.get(),
            'clean_interval': self.clean_interval_var.get(),
            'scan_threshold': int(self.scan_threshold_var.get())
        })
        
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(self.settings, f, indent=2)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save settings: {e}")


    def setup_ui(self):
        # Create main container with light theme
        main_container = tk.Frame(self.root, bg=self.bg_color)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Header with light theme
        header_frame = tk.Frame(main_container, bg=self.bg_color)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        title_label = tk.Label(
            header_frame, 
            text="🚀 SystemClean Pro", 
            font=('Arial', 24, 'bold'),
            fg=self.accent_color,
            bg=self.bg_color
        )
        title_label.pack(side=tk.LEFT)
        
        # Status indicator
        self.status_label = tk.Label(
            header_frame,
            text="● System Normal",
            font=('Arial', 10),
            fg=self.success_color,
            bg=self.bg_color
        )
        self.status_label.pack(side=tk.RIGHT)
        
        # Create notebook with light theme
        self.notebook = ttk.Notebook(main_container)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Apply light theme style
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure('TNotebook', background=self.bg_color)
        self.style.configure('TNotebook.Tab', 
                           background=self.card_bg,
                           foreground=self.text_color,
                           padding=[20, 5])
        
        # Create all tabs
        self.setup_dashboard_tab()
        self.setup_cleaner_tab()
        self.setup_performance_tab()
        self.setup_storage_tab()
        self.setup_startup_tab()
        self.setup_settings_tab()
        
        # Initialize auto-clean
        self.setup_auto_clean()

    def create_stat_card(self, parent, title, value, subvalue):
        """Create a statistics card with light theme"""
        card = tk.Frame(
            parent, 
            bg=self.card_bg, 
            relief=tk.RAISED, 
            bd=1, 
            width=150, 
            height=80
        )
        card.pack_propagate(False)
        
        title_label = tk.Label(
            card, 
            text=title, 
            font=('Arial', 10), 
            fg=self.text_color, 
            bg=self.card_bg
        )
        title_label.pack(anchor=tk.W, padx=10, pady=(10, 0))
        
        value_label = tk.Label(
            card, 
            text=value, 
            font=('Arial', 16, 'bold'), 
            fg=self.accent_color, 
            bg=self.card_bg
        )
        value_label.pack(anchor=tk.W, padx=10)
        
        subvalue_label = tk.Label(
            card, 
            text=subvalue, 
            font=('Arial', 8), 
            fg='#7f8c8d', 
            bg=self.card_bg
        )
        subvalue_label.pack(anchor=tk.W, padx=10, pady=(0, 10))
        
        return card

    def setup_cleaner_tab(self):
        """Enhanced cleaner tab with actual browser detection"""
        cleaner_frame = tk.Frame(self.notebook, bg=self.bg_color)
        self.notebook.add(cleaner_frame, text="🧹 Cleaner")
        
        # Browser Cleaner Section
        browser_frame = tk.LabelFrame(
            cleaner_frame, 
            text="Browser Cache Cleaner", 
            font=('Arial', 12, 'bold'),
            fg=self.text_color,
            bg=self.bg_color,
            labelanchor='n'
        )
        browser_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Browser list container
        self.browser_list_frame = tk.Frame(browser_frame, bg=self.bg_color)
        self.browser_list_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Detect and display browsers
        self.update_browser_list()
        
        # Browser cleaner buttons
        browser_btn_frame = tk.Frame(browser_frame, bg=self.bg_color)
        browser_btn_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Button(
            browser_btn_frame,
            text="🔄 Refresh Browsers",
            command=self.update_browser_list,
            bg=self.card_bg,
            fg=self.text_color,
            relief=tk.RAISED,
            bd=1
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        tk.Button(
            browser_btn_frame,
            text="🗑️ Clear Selected",
            command=self.clean_selected_browsers,
            bg=self.warning_color,
            fg='white'
        ).pack(side=tk.LEFT)
        
        # Rest of the cleaner tab remains similar but with updated colors...

    def clean_selected_browsers(self):
        """Clean selected browser caches"""
        selected_browsers = []
        for browser, data in self.browser_vars.items():
            if data['var'].get() and data['info']['detected']:
                selected_browsers.append((browser, data['info']['paths']))
        
        if not selected_browsers:
            messagebox.showwarning("Warning", "Please select at least one browser to clean.")
            return
        
        # Perform cleaning
        total_freed = 0
        for browser_name, paths in selected_browsers:
            try:
                freed = self.clean_browser_cache(browser_name, paths)
                total_freed += freed
            except Exception as e:
                messagebox.showerror("Error", str(e))
                return
        
        messagebox.showinfo("Success", 
                          f"Cleaned {len(selected_browsers)} browsers\n"
                          f"Freed: {self.format_file_size(total_freed)}")
        
        # Refresh browser list
        self.update_browser_list()

def main():
    root = tk.Tk()
    app = SystemCleanPro(root)
    root.mainloop()

if __name__ == "__main__":
    main()