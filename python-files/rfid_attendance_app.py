import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import serial
import requests
import threading
import time
from datetime import datetime
import json
import os
from tkinter import font
import serial.tools.list_ports

class RFIDAttendanceApp:
    def __init__(self, root):
        self.root = root
        self.root.title("RFID Attendance Management System")
        self.root.geometry("1200x800")
        self.root.configure(bg='#f0f0f0')
        
        # Variables
        self.serial_connection = None
        self.is_listening = False
        self.config_file = "rfid_config.json"
        self.total_scans = 0
        self.successful_uploads = 0
        self.failed_uploads = 0
        
        # Load configuration
        self.load_config()
        
        # Setup UI
        self.setup_ui()
        self.setup_styles()
        
        # Auto-refresh port list
        self.refresh_ports()
        
    def load_config(self):
        """Load configuration from file"""
        default_config = {
            "serial_port": "COM12",
            "baudrate": 115200,
            "php_url": "http://localhost/phplogin/attendance.php",
            "timeout": 1
        }
        
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    self.config = json.load(f)
            else:
                self.config = default_config
                self.save_config()
        except:
            self.config = default_config
            
    def save_config(self):
        """Save configuration to file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=4)
        except Exception as e:
            self.log_message(f"Error saving config: {str(e)}", "ERROR")
            
    def setup_styles(self):
        """Setup custom styles"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure styles
        style.configure('Title.TLabel', font=('Segoe UI', 16, 'bold'), foreground='#2c3e50')
        style.configure('Header.TLabel', font=('Segoe UI', 12, 'bold'), foreground='#34495e')
        style.configure('Status.TLabel', font=('Segoe UI', 10), foreground='#7f8c8d')
        style.configure('Success.TLabel', font=('Segoe UI', 10, 'bold'), foreground='#27ae60')
        style.configure('Error.TLabel', font=('Segoe UI', 10, 'bold'), foreground='#e74c3c')
        style.configure('Warning.TLabel', font=('Segoe UI', 10, 'bold'), foreground='#f39c12')
        
    def setup_ui(self):
        """Setup the user interface"""
        # Main container
        main_frame = tk.Frame(self.root, bg="#f75f5f")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Title
        title_frame = tk.Frame(main_frame, bg='#f0f0f0')
        title_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(title_frame, text="Mehedi's IoT Academy RFID Attendance System", 
                 style='Title.TLabel').pack()
        ttk.Label(title_frame, text="Professional RFID attendance tracking solution", 
                 style='Status.TLabel').pack()
        
        # Create notebook for tabs
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # Configuration Tab
        self.setup_config_tab(notebook)
        
        # Monitoring Tab
        self.setup_monitoring_tab(notebook)
        
        # Statistics Tab
        self.setup_statistics_tab(notebook)
        
        # Logs Tab
        self.setup_logs_tab(notebook)
        
    def setup_config_tab(self, notebook):
        """Setup configuration tab"""
        config_frame = ttk.Frame(notebook)
        notebook.add(config_frame, text="⚙️ Configuration")
        
        # Configuration section
        config_section = ttk.LabelFrame(config_frame, text="Connection Settings", padding=20)
        config_section.pack(fill=tk.X, padx=20, pady=10)
        
        # Serial Port
        ttk.Label(config_section, text="Serial Port:", style='Header.TLabel').grid(row=0, column=0, sticky=tk.W, pady=5)
        self.port_var = tk.StringVar(value=self.config.get('serial_port', 'COM12'))
        self.port_combo = ttk.Combobox(config_section, textvariable=self.port_var, width=30)
        self.port_combo.grid(row=0, column=1, sticky=tk.W, padx=(10, 0), pady=5)
        
        refresh_btn = ttk.Button(config_section, text="🔄 Refresh Ports", command=self.refresh_ports)
        refresh_btn.grid(row=0, column=2, padx=(10, 0), pady=5)
        
        # Baudrate
        ttk.Label(config_section, text="Baudrate:", style='Header.TLabel').grid(row=1, column=0, sticky=tk.W, pady=5)
        self.baudrate_var = tk.StringVar(value=str(self.config.get('baudrate', 115200)))
        baudrate_combo = ttk.Combobox(config_section, textvariable=self.baudrate_var, 
                                     values=['9600', '19200', '38400', '57600', '115200'], width=30)
        baudrate_combo.grid(row=1, column=1, sticky=tk.W, padx=(10, 0), pady=5)
        
        # PHP URL
        ttk.Label(config_section, text="Server URL:", style='Header.TLabel').grid(row=2, column=0, sticky=tk.W, pady=5)
        self.url_var = tk.StringVar(value=self.config.get('php_url', 'http://localhost/phplogin/attendance.php'))
        url_entry = ttk.Entry(config_section, textvariable=self.url_var, width=50)
        url_entry.grid(row=2, column=1, columnspan=2, sticky=tk.W, padx=(10, 0), pady=5)
        
        # Buttons
        button_frame = tk.Frame(config_section, bg='white')
        button_frame.grid(row=3, column=0, columnspan=3, pady=20)
        
        save_btn = ttk.Button(button_frame, text="💾 Save Configuration", command=self.save_configuration)
        save_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        test_btn = ttk.Button(button_frame, text="🔗 Test Connection", command=self.test_connection)
        test_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        test_server_btn = ttk.Button(button_frame, text="🌐 Test Server", command=self.test_server)
        test_server_btn.pack(side=tk.LEFT)
        
    def setup_monitoring_tab(self, notebook):
        """Setup monitoring tab"""
        monitor_frame = ttk.Frame(notebook)
        notebook.add(monitor_frame, text="📡 Live Monitoring")
        
        # Control Panel
        control_panel = ttk.LabelFrame(monitor_frame, text="Control Panel", padding=20)
        control_panel.pack(fill=tk.X, padx=20, pady=10)
        
        # Status indicators
        status_frame = tk.Frame(control_panel, bg='white')
        status_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(status_frame, text="Connection Status:", style='Header.TLabel').pack(side=tk.LEFT)
        self.status_label = ttk.Label(status_frame, text="🔴 Disconnected", style='Error.TLabel')
        self.status_label.pack(side=tk.LEFT, padx=(10, 20))
        
        ttk.Label(status_frame, text="Listening:", style='Header.TLabel').pack(side=tk.LEFT)
        self.listening_label = ttk.Label(status_frame, text="⏸️ Stopped", style='Warning.TLabel')
        self.listening_label.pack(side=tk.LEFT, padx=(10, 0))
        
        # Control buttons
        button_frame = tk.Frame(control_panel, bg='white')
        button_frame.pack()
        
        self.start_btn = ttk.Button(button_frame, text="▶️ Start Listening", command=self.start_listening)
        self.start_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.stop_btn = ttk.Button(button_frame, text="⏹️ Stop Listening", command=self.stop_listening, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        clear_btn = ttk.Button(button_frame, text="🗑️ Clear Log", command=self.clear_monitoring_log)
        clear_btn.pack(side=tk.LEFT)
        
        # Real-time monitoring
        monitor_section = ttk.LabelFrame(monitor_frame, text="Real-time Activity", padding=20)
        monitor_section.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Create Treeview for better data display
        columns = ('Time', 'UID', 'Name', 'Status', 'Server Response')
        self.monitor_tree = ttk.Treeview(monitor_section, columns=columns, show='headings', height=15)
        
        for col in columns:
            self.monitor_tree.heading(col, text=col)
            self.monitor_tree.column(col, width=150 if col != 'Server Response' else 200)
        
        # Scrollbars for treeview
        tree_scroll_y = ttk.Scrollbar(monitor_section, orient=tk.VERTICAL, command=self.monitor_tree.yview)
        tree_scroll_x = ttk.Scrollbar(monitor_section, orient=tk.HORIZONTAL, command=self.monitor_tree.xview)
        self.monitor_tree.configure(yscrollcommand=tree_scroll_y.set, xscrollcommand=tree_scroll_x.set)
        
        self.monitor_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tree_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        tree_scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        
    def setup_statistics_tab(self, notebook):
        """Setup statistics tab"""
        stats_frame = ttk.Frame(notebook)
        notebook.add(stats_frame, text="📊 Statistics")
        
        # Statistics cards
        cards_frame = tk.Frame(stats_frame, bg='#f0f0f0')
        cards_frame.pack(fill=tk.X, padx=20, pady=20)
        
        # Total Scans Card
        self.create_stat_card(cards_frame, "📋 Total Scans", "0", "#3498db", 0)
        
        # Successful Uploads Card
        self.create_stat_card(cards_frame, "✅ Successful", "0", "#27ae60", 1)
        
        # Failed Uploads Card
        self.create_stat_card(cards_frame, "❌ Failed", "0", "#e74c3c", 2)
        
        # Success Rate Card
        self.create_stat_card(cards_frame, "📈 Success Rate", "0%", "#9b59b6", 3)
        
        # Recent activity chart placeholder
        chart_frame = ttk.LabelFrame(stats_frame, text="Recent Activity Overview", padding=20)
        chart_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        self.activity_text = scrolledtext.ScrolledText(chart_frame, height=15, width=80)
        self.activity_text.pack(fill=tk.BOTH, expand=True)
        
    def setup_logs_tab(self, notebook):
        """Setup logs tab"""
        logs_frame = ttk.Frame(notebook)
        notebook.add(logs_frame, text="📝 System Logs")
        
        # Log controls
        log_controls = tk.Frame(logs_frame, bg='#f0f0f0')
        log_controls.pack(fill=tk.X, padx=20, pady=10)
        
        ttk.Button(log_controls, text="🗑️ Clear Logs", command=self.clear_logs).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(log_controls, text="💾 Export Logs", command=self.export_logs).pack(side=tk.LEFT)
        
        # Log display
        log_frame = ttk.LabelFrame(logs_frame, text="System Logs", padding=20)
        log_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=25, width=100)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # Configure text tags for colored output
        self.log_text.tag_config("ERROR", foreground="#e74c3c", font=('Consolas', 9, 'bold'))
        self.log_text.tag_config("SUCCESS", foreground="#27ae60", font=('Consolas', 9, 'bold'))
        self.log_text.tag_config("WARNING", foreground="#f39c12", font=('Consolas', 9, 'bold'))
        self.log_text.tag_config("INFO", foreground="#3498db", font=('Consolas', 9))
        
    def create_stat_card(self, parent, title, value, color, column):
        """Create a statistics card"""
        card_frame = tk.Frame(parent, bg=color, relief=tk.RAISED, bd=2)
        card_frame.grid(row=0, column=column, padx=10, pady=10, sticky='ew')
        parent.grid_columnconfigure(column, weight=1)
        
        title_label = tk.Label(card_frame, text=title, bg=color, fg='white', 
                              font=('Segoe UI', 10, 'bold'))
        title_label.pack(pady=(15, 5))
        
        value_label = tk.Label(card_frame, text=value, bg=color, fg='white',
                              font=('Segoe UI', 24, 'bold'))
        value_label.pack(pady=(5, 15))
        
        # Store reference for updating
        if hasattr(self, 'stat_labels'):
            self.stat_labels.append(value_label)
        else:
            self.stat_labels = [value_label]
            
    def refresh_ports(self):
        """Refresh available serial ports"""
        ports = [port.device for port in serial.tools.list_ports.comports()]
        self.port_combo['values'] = ports
        if ports:
            if self.config.get('serial_port') not in ports:
                self.port_combo.set(ports[0])
        self.log_message(f"Found {len(ports)} serial ports", "INFO")
        
    def save_configuration(self):
        """Save current configuration"""
        self.config['serial_port'] = self.port_var.get()
        self.config['baudrate'] = int(self.baudrate_var.get())
        self.config['php_url'] = self.url_var.get()
        self.save_config()
        self.log_message("Configuration saved successfully", "SUCCESS")
        messagebox.showinfo("Success", "Configuration saved successfully!")
        
    def test_connection(self):
        """Test serial connection"""
        try:
            test_serial = serial.Serial(self.port_var.get(), int(self.baudrate_var.get()), timeout=1)
            test_serial.close()
            self.log_message(f"Serial connection test successful: {self.port_var.get()}", "SUCCESS")
            messagebox.showinfo("Success", "Serial connection test successful!")
        except Exception as e:
            self.log_message(f"Serial connection test failed: {str(e)}", "ERROR")
            messagebox.showerror("Error", f"Serial connection test failed:\n{str(e)}")
            
    def test_server(self):
        """Test server connection"""
        try:
            response = requests.get(self.url_var.get(), timeout=5)
            if response.status_code == 200:
                self.log_message(f"Server connection test successful: {self.url_var.get()}", "SUCCESS")
                messagebox.showinfo("Success", "Server connection test successful!")
            else:
                self.log_message(f"Server returned status {response.status_code}", "WARNING")
                messagebox.showwarning("Warning", f"Server returned status {response.status_code}")
        except Exception as e:
            self.log_message(f"Server connection test failed: {str(e)}", "ERROR")
            messagebox.showerror("Error", f"Server connection test failed:\n{str(e)}")
            
    def start_listening(self):
        """Start listening for RFID data"""
        try:
            self.serial_connection = serial.Serial(
                self.config['serial_port'], 
                self.config['baudrate'], 
                timeout=self.config.get('timeout', 1)
            )
            self.is_listening = True
            self.start_btn.config(state=tk.DISABLED)
            self.stop_btn.config(state=tk.NORMAL)
            self.status_label.config(text="🟢 Connected", style='Success.TLabel')
            self.listening_label.config(text="▶️ Listening", style='Success.TLabel')
            
            # Start listening thread
            self.listen_thread = threading.Thread(target=self.listen_for_rfid, daemon=True)
            self.listen_thread.start()
            
            self.log_message("Started listening for RFID data", "SUCCESS")
            
        except Exception as e:
            self.log_message(f"Failed to start listening: {str(e)}", "ERROR")
            messagebox.showerror("Error", f"Failed to start listening:\n{str(e)}")
            
    def stop_listening(self):
        """Stop listening for RFID data"""
        self.is_listening = False
        if self.serial_connection:
            self.serial_connection.close()
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.status_label.config(text="🔴 Disconnected", style='Error.TLabel')
        self.listening_label.config(text="⏸️ Stopped", style='Warning.TLabel')
        self.log_message("Stopped listening for RFID data", "WARNING")
        
    def listen_for_rfid(self):
        """Listen for RFID data in background thread"""
        while self.is_listening and self.serial_connection:
            try:
                line = self.serial_connection.readline().decode(errors='ignore').strip()
                if line.startswith("RFID:"):
                    self.process_rfid_data(line)
                time.sleep(0.1)  # Small delay to prevent excessive CPU usage
            except Exception as e:
                if self.is_listening:  # Only log if we're still supposed to be listening
                    self.log_message(f"Error reading serial data: {str(e)}", "ERROR")
                break
                
    def process_rfid_data(self, line):
        """Process received RFID data"""
        try:
            parts = line[5:].split(",")
            if len(parts) == 3:
                uid, name, status = parts
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                # Update statistics
                self.total_scans += 1
                self.update_statistics()
                
                # Send to server
                data = {
                    'serial_rfid': '1',
                    'uid': uid,
                    'name': name,
                    'status': status
                }
                
                response = requests.post(self.config['php_url'], data=data, timeout=5)
                
                if response.status_code == 200:
                    self.successful_uploads += 1
                    server_response = "Success"
                    log_type = "SUCCESS"
                else:
                    self.failed_uploads += 1
                    server_response = f"HTTP {response.status_code}"
                    log_type = "ERROR"
                
                # Update UI in main thread
                self.root.after(0, self.update_monitoring_display, timestamp, uid, name, status, server_response, log_type)
                self.root.after(0, self.update_statistics)
                
                self.log_message(f"Processed: {uid}, {name}, {status} | Server: {server_response}", log_type)
                
        except Exception as e:
            self.failed_uploads += 1
            self.root.after(0, self.update_statistics)
            self.log_message(f"Error processing RFID data: {str(e)}", "ERROR")
            
    def update_monitoring_display(self, timestamp, uid, name, status, response, log_type):
        """Update monitoring display"""
        # Insert into treeview
        tags = ('success',) if log_type == "SUCCESS" else ('error',)
        self.monitor_tree.insert('', 0, values=(timestamp, uid, name, status, response), tags=tags)
        
        # Configure tags
        self.monitor_tree.tag_configure('success', foreground='#27ae60')
        self.monitor_tree.tag_configure('error', foreground='#e74c3c')
        
        # Limit to last 100 entries
        items = self.monitor_tree.get_children()
        if len(items) > 100:
            for item in items[100:]:
                self.monitor_tree.delete(item)
                
    def update_statistics(self):
        """Update statistics display"""
        success_rate = (self.successful_uploads / self.total_scans * 100) if self.total_scans > 0 else 0
        
        if hasattr(self, 'stat_labels') and len(self.stat_labels) >= 4:
            self.stat_labels[0].config(text=str(self.total_scans))
            self.stat_labels[1].config(text=str(self.successful_uploads))
            self.stat_labels[2].config(text=str(self.failed_uploads))
            self.stat_labels[3].config(text=f"{success_rate:.1f}%")
            
    def log_message(self, message, log_type="INFO"):
        """Add message to log"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {log_type}: {message}\n"
        
        self.log_text.insert(tk.END, log_entry, log_type)
        self.log_text.see(tk.END)
        
        # Update activity text
        self.activity_text.insert(tk.END, log_entry)
        self.activity_text.see(tk.END)
        
    def clear_monitoring_log(self):
        """Clear monitoring display"""
        for item in self.monitor_tree.get_children():
            self.monitor_tree.delete(item)
        self.log_message("Monitoring display cleared", "INFO")
        
    def clear_logs(self):
        """Clear all logs"""
        self.log_text.delete(1.0, tk.END)
        self.activity_text.delete(1.0, tk.END)
        self.log_message("Logs cleared", "INFO")
        
    def export_logs(self):
        """Export logs to file"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"rfid_logs_{timestamp}.txt"
            
            with open(filename, 'w') as f:
                f.write(self.log_text.get(1.0, tk.END))
                
            self.log_message(f"Logs exported to {filename}", "SUCCESS")
            messagebox.showinfo("Success", f"Logs exported to {filename}")
            
        except Exception as e:
            self.log_message(f"Failed to export logs: {str(e)}", "ERROR")
            messagebox.showerror("Error", f"Failed to export logs:\n{str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = RFIDAttendanceApp(root)
    
    # Handle window closing
    def on_closing():
        if app.is_listening:
            app.stop_listening()
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()
