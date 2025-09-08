import tkinter as tk
from tkinter import messagebox, simpledialog
import json
import socket
import threading
from datetime import datetime
import cv2
from PIL import Image, ImageTk
import os
import platform
import glob

class BeveledFrame:
    """Custom frame class with 5% beveled corners"""
    def __init__(self, parent, **kwargs):
        # Extract bevel-specific parameters
        bevel_radius = kwargs.pop('bevel_radius', 5)  # 5% bevel
        bg_color = kwargs.pop('bg', '#f5f5f7')
        
        # Create outer frame for bevel effect
        self.outer_frame = tk.Frame(parent, bg='#d1d1d6', relief=tk.FLAT, bd=0)
        
        # Create inner frame with beveled appearance
        self.inner_frame = tk.Frame(self.outer_frame, bg=bg_color, relief=tk.FLAT, bd=0)
        self.inner_frame.pack(expand=True, fill=tk.BOTH, padx=bevel_radius, pady=bevel_radius)
        
        # Store reference to inner frame for widget placement
        self.frame = self.inner_frame
        
        # Apply bevel effect by adjusting colors
        self._apply_bevel_effect(bevel_radius, bg_color)
    
    def _apply_bevel_effect(self, radius, bg_color):
        """Apply bevel effect using color variations"""
        # Create subtle bevel effect with color variations
        if bg_color == '#f5f5f7':  # Light gray
            self.outer_frame.configure(bg='#e5e5ea')  # Slightly darker for bevel
        elif bg_color == '#ffffff':  # White
            self.outer_frame.configure(bg='#f2f2f7')  # Very light gray for bevel
    
    def pack(self, **kwargs):
        return self.outer_frame.pack(**kwargs)
    
    def grid(self, **kwargs):
        return self.outer_frame.grid(**kwargs)
    
    def place(self, **kwargs):
        return self.outer_frame.place(**kwargs)
    
    def configure(self, **kwargs):
        return self.inner_frame.configure(**kwargs)
    
    def winfo_children(self):
        return self.inner_frame.winfo_children()
    
    def bind(self, event, callback):
        self.outer_frame.bind(event, callback)
        self.inner_frame.bind(event, callback)

class ClockInOutClient:
    def __init__(self, root):
        self.root = root
        self.root.title("Employee Clock In/Out System")
        self.root.geometry("1000x600")
        self.root.configure(bg='#f0f0f0')
        
        # Set font to San Francisco-like (system default)
        if platform.system() == "Darwin":  # macOS
            self.default_font = ('SF Pro Display', 10)
            self.title_font = ('SF Pro Display', 16, 'bold')
        else:  # Windows/Linux
            self.default_font = ('Arial', 10)
            self.title_font = ('Arial', 16, 'bold')
        
        # Camera setup
        self.camera = None
        self.camera_active = False
        
        # Employee data
        self.employees = self.load_employees()
        self.current_employee = None
        
        # Server connection - configurable for cross-platform
        self.server_host = 'localhost'  # Default, can be changed
        self.server_port = 5000
        self.connected = False
        
        # Connection management
        self.server_socket = None
        self.connection_thread = None
        self.should_listen = False
        
        self.setup_ui()
        self.update_time()
        
        # Show connection dialog
        self.show_connection_dialog()
        
    def show_connection_dialog(self):
        """Show dialog to configure server connection"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Server Connection")
        dialog.geometry("400x300")
        dialog.configure(bg='#f0f0f0')
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Center the dialog
        dialog.geometry("+%d+%d" % (self.root.winfo_rootx() + 50, self.root.winfo_rooty() + 50))
        
        # Title
        title_label = tk.Label(dialog, text="Connect to Admin Server", 
                              font=self.title_font, bg='#f0f0f0', fg='#333333')
        title_label.pack(pady=20)
        
        # Instructions
        instructions = tk.Label(dialog, 
                              text="Enter the IP address of the computer\nrunning the admin application:", 
                              font=self.default_font, bg='#f0f0f0', fg='#666666')
        instructions.pack(pady=(0, 20))
        
        # IP input frame
        ip_frame = tk.Frame(dialog, bg='#f0f0f0')
        ip_frame.pack(pady=(0, 20))
        
        ip_label = tk.Label(ip_frame, text="Server IP:", font=self.default_font, bg='#f0f0f0')
        ip_label.pack(side=tk.LEFT, padx=(0, 10))
        
        self.ip_entry = tk.Entry(ip_frame, font=self.default_font, width=15)
        self.ip_entry.pack(side=tk.LEFT)
        self.ip_entry.insert(0, self.server_host)
        
        # Port input frame
        port_frame = tk.Frame(dialog, bg='#f0f0f0')
        port_frame.pack(pady=(0, 20))
        
        port_label = tk.Label(port_frame, text="Port:", font=self.default_font, bg='#f0f0f0')
        port_label.pack(side=tk.LEFT, padx=(0, 10))
        
        self.port_entry = tk.Entry(port_frame, font=self.default_font, width=10)
        self.port_entry.pack(side=tk.LEFT)
        self.port_entry.insert(0, str(self.server_port))
        
        # Buttons
        button_frame = tk.Frame(dialog, bg='#f0f0f0')
        button_frame.pack(pady=20)
        
        connect_btn = tk.Button(button_frame, text="Connect", 
                               command=self.connect_to_server, font=self.default_font,
                               bg='#4CAF50', fg='black', relief=tk.FLAT)
        connect_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        test_btn = tk.Button(button_frame, text="Test Connection", 
                            command=self.test_connection, font=self.default_font,
                            bg='#2196F3', fg='black', relief=tk.FLAT)
        test_btn.pack(side=tk.LEFT)
        
        # Help text
        help_text = tk.Label(dialog, 
                            text="💡 Tip: Use 'localhost' if admin app is on this computer\nUse IP address (e.g., 192.168.1.100) if on different computer", 
                            font=('Arial', 9), bg='#f0f0f0', fg='#666666', justify=tk.LEFT)
        help_text.pack(pady=20)
        
        # Store reference to dialog for later closing
        self.connection_dialog = dialog
        
        # Make dialog modal
        dialog.wait_window()
        
    def connect_to_server(self):
        """Connect to the specified server"""
        try:
            self.server_host = self.ip_entry.get().strip()
            self.server_port = int(self.port_entry.get().strip())
            
                        # Test connection
            if self.test_connection():
                self.connected = True
                self.root.focus_force()  # Bring main window to front
                self.update_connection_status()
                messagebox.showinfo("Success", f"Connected to server at {self.server_host}:{self.server_port}")
                
                # Close the connection dialog
                if hasattr(self, 'connection_dialog') and self.connection_dialog:
                    self.connection_dialog.destroy()
                    self.connection_dialog = None
                
                # Establish persistent connection
                self.establish_persistent_connection()
            else:
                self.connected = False
                self.update_connection_status()
                messagebox.showerror("Connection Failed", "Could not connect to server. Please check the IP address and port.")
                
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid port number.")
        except Exception as e:
            messagebox.showerror("Error", f"Connection error: {str(e)}")
    
    def establish_persistent_connection(self):
        """Establish a persistent connection to the server"""
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.settimeout(10)
            self.server_socket.connect((self.server_host, self.server_port))
            
            # Start listening thread
            self.should_listen = True
            self.connection_thread = threading.Thread(target=self.listen_for_server_updates, daemon=True)
            self.connection_thread.start()
            
            # Request current notices
            self.request_notices()
            
        except Exception as e:
            print(f"Failed to establish persistent connection: {e}")
            self.connected = False
            self.update_connection_status()
    
    def listen_for_server_updates(self):
        """Listen for updates from the server"""
        while self.should_listen and self.server_socket:
            try:
                data = self.server_socket.recv(1024).decode()
                if not data:
                    break
                
                self.process_server_message(data)
                
            except socket.timeout:
                # Send ping to keep connection alive
                try:
                    ping_message = {'type': 'ping', 'timestamp': datetime.now().isoformat()}
                    self.server_socket.send(json.dumps(ping_message).encode())
                except:
                    break
            except Exception as e:
                print(f"Error listening for server updates: {e}")
                break
        
        # Connection lost
        self.connected = False
        self.root.after(0, self.update_connection_status)
    
    def process_server_message(self, data):
        """Process messages from the server"""
        try:
            # Clean the data string before parsing
            data_str = data.decode('utf-8') if isinstance(data, bytes) else str(data)
            data_str = data_str.strip()
            
            if not data_str:
                return
                
            message = json.loads(data_str)
            message_type = message.get('type')
            
            if message_type == 'notices_update':
                # Update notices display
                notices = message.get('notices', [])
                self.root.after(0, lambda: self.update_notices_display(notices))
            elif message_type == 'employee_update':
                # Update employee list
                employees = message.get('employees', [])
                print(f"Received employee update with {len(employees)} employees")
                self.root.after(0, lambda: self.update_employees_from_server(employees))
            elif message_type == 'pong':
                # Server responded to ping
                pass
                
        except json.JSONDecodeError as e:
            print(f"JSON decode error: {e}")
            print(f"Data received: {data[:200]}...")  # Show first 200 chars for debugging
        except Exception as e:
            print(f"Error processing server message: {e}")
    
    def update_notices_display(self, notices):
        """Update the notices display with new data"""
        self.notice_text.config(state=tk.NORMAL)
        self.notice_text.delete(1.0, tk.END)
        
        if notices:
            for notice in notices:
                self.notice_text.insert(tk.END, f"• {notice}\n\n")
        else:
            self.notice_text.insert(tk.END, "No notices at this time.")
        
        self.notice_text.config(state=tk.DISABLED)
    
    def update_employees_from_server(self, employees):
        """Update employee list from server"""
        print(f"Updating employees from server: {len(employees)} employees received")
        self.employees = employees
        self.save_employees()
        self.update_employee_display()
        print(f"Employee display updated with {len(self.employees)} employees")
    
    def request_notices(self):
        """Request current notices from the server"""
        try:
            if self.server_socket and self.connected:
                request = {'type': 'request_notices'}
                self.server_socket.send(json.dumps(request).encode())
        except Exception as e:
            print(f"Error requesting notices: {e}")
    
    def disconnect_from_server(self):
        """Disconnect from the server"""
        self.should_listen = False
        if self.server_socket:
            try:
                self.server_socket.close()
            except:
                pass
            self.server_socket = None
        
        self.connected = False
        self.update_connection_status()
    
    def test_connection(self):
        """Test connection to server"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(5)  # 5 second timeout
                s.connect((self.server_host, self.server_port))
                return True
        except Exception as e:
            print(f"Connection test failed: {e}")
            return False
        
    def load_employees(self):
        """Load employee data from JSON file"""
        try:
            if os.path.exists('employees.json'):
                with open('employees.json', 'r') as f:
                    return json.load(f)
            else:
                return []
        except:
            return []
    
    def load_notices(self):
        """Load notices from JSON file"""
        try:
            if os.path.exists('notices.json'):
                with open('notices.json', 'r') as f:
                    notices = json.load(f)
                    # Update display with loaded notices
                    self.root.after(100, lambda: self.update_notices_display(notices))
                    return notices
            else:
                return []
        except:
            return []
    
    def setup_ui(self):
        """Setup the user interface with modern macOS design"""
        # Configure the root window for macOS
        self.root.configure(bg='#ffffff')
        
        # Main container with proper spacing
        main_frame = tk.Frame(self.root, bg='#ffffff')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)
        
        # Modern header with subtle shadow effect
        header_frame = tk.Frame(main_frame, bg='#ffffff', height=80)
        header_frame.pack(fill=tk.X, padx=0, pady=0)
        header_frame.pack_propagate(False)
        
        # Title with SF Pro Display styling
        title_label = tk.Label(header_frame, text="Employee Clock In/Out", 
                              font=('SF Pro Display', 28, 'normal'), 
                              bg='#ffffff', fg='#1d1d1f')
        title_label.pack(expand=True)
        
        # Connection status bar with modern design
        self.connection_frame = tk.Frame(main_frame, bg='#f5f5f7', height=50)
        self.connection_frame.pack(fill=tk.X, padx=0, pady=0)
        self.connection_frame.pack_propagate(False)
        
        self.connection_label = tk.Label(self.connection_frame, 
                                        text="🔴 Not Connected", 
                                        font=('SF Pro Text', 14), 
                                        bg='#f5f5f7', fg='#ff3b30')
        self.connection_label.pack(expand=True)
        
        # Content area with proper layout
        content_frame = tk.Frame(main_frame, bg='#ffffff')
        content_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=20)
        
        # Create paned window for resizable sidebar
        paned_window = tk.PanedWindow(content_frame, orient=tk.HORIZONTAL, sashwidth=8, sashrelief=tk.RAISED)
        paned_window.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Left sidebar with modern card design
        left_frame = tk.Frame(paned_window, bg='#ffffff', width=400)
        left_frame.pack_propagate(False)
        paned_window.add(left_frame, minsize=300, width=400)
        
        # Time and date card with modern styling and beveled corners
        time_card = tk.Frame(left_frame, bg='#f5f5f7', relief=tk.RAISED, bd=2)
        time_card.pack(fill=tk.X, pady=(0, 20))
        
        self.time_label = tk.Label(time_card, text="", font=('SF Pro Display', 36, 'normal'), 
                                  bg='#f5f5f7', fg='#1d1d1f')
        self.time_label.pack(pady=(20, 5))
        
        self.date_label = tk.Label(time_card, text="", font=('SF Pro Text', 16), 
                                  bg='#f5f5f7', fg='#86868b')
        self.date_label.pack(pady=(0, 5))
        
        self.day_label = tk.Label(time_card, text="", font=('SF Pro Text', 16), 
                                 bg='#f5f5f7', fg='#86868b')
        self.day_label.pack(pady=(0, 20))
        
        # Weather card with beveled corners
        weather_card = tk.Frame(left_frame, bg='#f5f5f7', relief=tk.RAISED, bd=2)
        weather_card.pack(fill=tk.X, pady=(0, 20))
        
        weather_title = tk.Label(weather_card, text="Weather", font=('SF Pro Display', 18, 'normal'), 
                                bg='#f5f5f7', fg='#1d1d1f')
        weather_title.pack(pady=(20, 10))
        
        self.weather_label = tk.Label(weather_card, text="22°C Sunny", 
                                     font=('SF Pro Text', 16), bg='#f5f5f7', fg='#86868b')
        self.weather_label.pack(pady=(0, 20))
        
        # Notice board card with beveled corners
        notice_card = tk.Frame(left_frame, bg='#f5f5f7', relief=tk.RAISED, bd=2)
        notice_card.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        notice_title = tk.Label(notice_card, text="Notice Board", font=('SF Pro Display', 18, 'normal'), 
                               bg='#f5f5f7', fg='#1d1d1f')
        notice_title.pack(pady=(20, 15))
        
        # Modern text widget styling
        self.notice_text = tk.Text(notice_card, height=8, width=30, 
                                  font=('SF Pro Display', 18, 'bold'), bg='#ffffff', 
                                  relief=tk.FLAT, bd=0, state=tk.DISABLED,
                                  padx=15, pady=15)
        self.notice_text.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        
        # Camera controls card with modern design and beveled corners
        camera_card = tk.Frame(left_frame, bg='#f5f5f7', relief=tk.RAISED, bd=2)
        camera_card.pack(fill=tk.X, pady=(0, 20))
        
        camera_title = tk.Label(camera_card, text="Camera", font=('SF Pro Display', 18, 'normal'), 
                               bg='#f5f5f7', fg='#1d1d1f')
        camera_title.pack(pady=(20, 15))
        
        # Camera frame with rounded corners effect
        self.camera_frame = tk.Frame(camera_card, bg='#000000', width=360, height=270)
        self.camera_frame.pack(pady=(0, 15))
        self.camera_frame.pack_propagate(False)
        
        # Camera placeholder with modern styling
        self.camera_label = tk.Label(self.camera_frame, text="Camera\nNot Active", 
                                    font=('SF Pro Text', 14), bg='#000000', fg='#86868b')
        self.camera_label.pack(expand=True)
        
        # Modern button styling with beveled corners
        self.camera_btn = tk.Button(camera_card, text="Start Camera", 
                                   command=self.toggle_camera, 
                                   font=('SF Pro Text', 14, 'normal'),
                                   bg='#007aff', fg='black', relief=tk.RAISED, bd=2,
                                   padx=20, pady=8, cursor='hand2')
        self.camera_btn.pack(pady=(0, 8))
        
        self.capture_btn = tk.Button(camera_card, text="Take Photo", 
                                    command=self.capture_photo, 
                                    font=('SF Pro Text', 14, 'normal'),
                                    bg='#ff9500', fg='black', relief=tk.RAISED, bd=2,
                                   padx=20, pady=8, state=tk.DISABLED, cursor='hand2')
        self.capture_btn.pack(pady=(0, 15))
        
        # Test camera button for debugging
        test_camera_btn = tk.Button(camera_card, text="Test Camera", 
                                   command=self.test_camera_manually, 
                                   font=('SF Pro Text', 12, 'normal'),
                                   bg='#34c759', fg='black', relief=tk.RAISED, bd=2,
                                   padx=15, pady=6, cursor='hand2')
        test_camera_btn.pack(pady=(0, 8))
        
        # Clock button with modern styling and beveled corners
        self.clock_btn = tk.Button(camera_card, text="Select Employee First", 
                                  command=self.clock_action, 
                                  font=('SF Pro Text', 14, 'normal'),
                                  bg='#8e8e93', fg='black', relief=tk.RAISED, bd=2,
                                  padx=20, pady=8, state=tk.DISABLED, cursor='hand2')
        self.clock_btn.pack(pady=(0, 15))
        
        # Status display with modern typography
        self.status_label = tk.Label(camera_card, text="Ready", 
                                    font=('SF Pro Text', 12), bg='#f5f5f7', fg='#86868b')
        self.status_label.pack(pady=(0, 20))
        
        # Right section with modern grid layout
        right_frame = tk.Frame(paned_window, bg='#ffffff')
        paned_window.add(right_frame, minsize=400)
        
        # Employee section title with modern styling
        emp_title = tk.Label(right_frame, text="Employees", font=('SF Pro Display', 24, 'normal'), 
                            bg='#ffffff', fg='#1d1d1f')
        emp_title.pack(pady=(0, 25))
        
        # Employee grid container
        self.emp_frame = tk.Frame(right_frame, bg='#ffffff')
        self.emp_frame.pack(fill=tk.BOTH, expand=True)
        
        self.update_employee_display()
        
        # Modern reconnect button with beveled corners
        reconnect_btn = tk.Button(right_frame, text="Reconnect to Server", 
                                 command=self.show_connection_dialog, 
                                 font=('SF Pro Text', 14, 'normal'),
                                 bg='#f5f5f7', fg='black', relief=tk.RAISED, bd=2,
                                 padx=20, pady=10, cursor='hand2')
        reconnect_btn.pack(pady=20)
    
    def update_connection_status(self):
        """Update the connection status display"""
        if self.connected:
            self.connection_frame.configure(bg='#e8f5e8')
            self.connection_label.configure(text=f"🟢 Connected to {self.server_host}:{self.server_port}", 
                                          bg='#e8f5e8', fg='#2e7d32')
        else:
            self.connection_frame.configure(bg='#ffebee')
            self.connection_label.configure(text=f"🔴 Disconnected from {self.server_host}:{self.server_port}", 
                                          bg='#ffebee', fg='#c62828')
    
    def update_time(self):
        """Update time and date display"""
        now = datetime.now()
        
        # Time
        time_str = now.strftime("%I:%M:%S %p")
        self.time_label.config(text=time_str)
        
        # Date
        date_str = now.strftime("%d/%m/%y")
        self.date_label.config(text=date_str)

        # Day of the week
        day_str = now.strftime("%A")
        self.day_label.config(text=day_str)
        
        # Schedule next update
        self.root.after(1000, self.update_time)
    
    def update_employee_list(self):
        """Update the employee listbox"""
        self.emp_listbox.delete(0, tk.END)
        for emp in self.employees:
            status_icon = "🟢" if emp['status'] == 'In' else "🔴"
            self.emp_listbox.insert(tk.END, f"{status_icon} {emp['calling_name']} ({emp['status']})")
    
    def update_employee_display(self):
        """Update the employee grid display with modern macOS design"""
        # Clear existing widgets
        for widget in self.emp_frame.winfo_children():
            widget.destroy()
        
        # Create employee cards with modern macOS design
        row = 0
        col = 0
        max_cols = 5  # 5 cards per row as requested
        
        for emp in self.employees:
            # Create modern card container
            card_container = tk.Frame(self.emp_frame, bg='#ffffff')
            card_container.grid(row=row, column=col, padx=8, pady=8, sticky='nsew')
            
            # Store employee ID in the container for easier access
            card_container.employee_id = emp['id']
            
            # Modern card with beveled corners - adjusted for 5 per row
            card_frame = tk.Frame(card_container, bg='#ffffff', relief=tk.RAISED, bd=2,
                                 width=120, height=160)  # Adjusted dimensions for 5 per row
            card_frame.pack(expand=True)
            card_frame.pack_propagate(False)
            
            # Add subtle border and background for modern look
            card_frame.configure(bg='#f5f5f7')
            
            # Store employee ID in the frame for selection (backup)
            card_frame.employee_id = emp['id']
            
            # Make the entire card clickable
            card_frame.bind('<Button-1>', self.on_employee_select)
            card_container.bind('<Button-1>', self.on_employee_select)
            
            # Add hover effects to show cards are clickable
            card_frame.bind('<Enter>', lambda e, cf=card_frame: self.on_card_hover_enter(cf))
            card_frame.bind('<Leave>', lambda e, cf=card_frame: self.on_card_hover_leave(cf))
            card_container.bind('<Enter>', lambda e, cf=card_frame: self.on_card_hover_enter(cf))
            card_container.bind('<Leave>', lambda e, cf=card_frame: self.on_card_hover_leave(cf))
            
            # Employee photo with modern styling - try to load actual photo
            photo_label = tk.Label(card_frame, text="👤", font=('SF Pro Display', 32), 
                                  bg='#f5f5f7', fg='#007aff')
            photo_label.place(relx=0.5, rely=0.25, anchor='center')
            photo_label.bind('<Button-1>', self.on_employee_select)
            
            # Try to load actual employee photo
            try:
                # Check if employee has a photo field
                if emp.get('photo') and emp['photo'] != "default_avatar.png" and os.path.exists(emp['photo']):
                    photo_path = emp['photo']
                else:
                    # Try to find photos by employee ID pattern
                    photo_path = f"photos/employee_{emp['id']}_*.jpg"
                    photo_files = glob.glob(photo_path)
                    if photo_files:
                        # Get the most recent photo
                        photo_path = max(photo_files, key=os.path.getctime)
                    else:
                        photo_path = None
                
                if photo_path and os.path.exists(photo_path):
                    from PIL import Image, ImageTk
                    img = Image.open(photo_path)
                    img = img.resize((60, 60), Image.Resampling.LANCZOS)  # Small size for card
                    photo = ImageTk.PhotoImage(img)
                    
                    photo_label.config(image=photo, text="")
                    photo_label.image = photo  # Keep a reference
            except Exception as e:
                # Keep the emoji if photo loading fails
                pass
            
            # Employee name with modern typography - bigger font
            name_label = tk.Label(card_frame, text=emp['calling_name'], 
                                 font=('SF Pro Text', 14, 'normal'), 
                                 bg='#f5f5f7', fg='#1d1d1f')
            name_label.place(relx=0.5, rely=0.55, anchor='center')
            name_label.bind('<Button-1>', self.on_employee_select)
            
            # Status with modern color scheme - bigger font
            status_color = '#34c759' if emp['status'] == 'In' else '#ff3b30'
            status_label = tk.Label(card_frame, text=emp['status'], 
                                   font=('SF Pro Text', 12, 'normal'), 
                                   bg='#f5f5f7', fg=status_color)
            status_label.place(relx=0.5, rely=0.8, anchor='center')
            status_label.bind('<Button-1>', self.on_employee_select)
            
            # Update grid position
            col += 1
            if col >= max_cols:
                col = 0
                row += 1
        
        # Configure grid weights for proper spacing
        for i in range(max_cols):
            self.emp_frame.grid_columnconfigure(i, weight=1)
        for i in range(row + 1):
            self.emp_frame.grid_rowconfigure(i, weight=1)
    
    def on_employee_select(self, event):
        """Handle employee selection from the grid"""
        # Get the widget that was clicked
        widget = event.widget
        
        # Find the employee ID - check the clicked widget and its parents
        employee_id = None
        current_widget = widget
        
        # Traverse up the widget hierarchy to find the card frame with employee_id
        while current_widget and not hasattr(current_widget, 'employee_id'):
            current_widget = current_widget.master
        
        if current_widget and hasattr(current_widget, 'employee_id'):
            employee_id = current_widget.employee_id
        
        if employee_id:
            # Find employee by ID
            for emp in self.employees:
                if emp['id'] == employee_id:
                    self.current_employee = emp
                    break
            
            if self.current_employee:
                # Update clock button
                action = "Clock Out" if self.current_employee['status'] == 'In' else "Clock In"
                self.clock_btn.config(text=action, state=tk.NORMAL, 
                                     bg='#f44336' if action == "Clock Out" else '#4CAF50')
                
                self.status_label.config(text=f"Selected: {self.current_employee['calling_name']}")
                
                # Highlight selected employee
                self.highlight_selected_employee(employee_id)
                
                # Automatically start camera if not already active
                if not self.camera_active:
                    self.start_camera()
                
                # Automatically start the clock in/out process
                self.auto_clock_process()
    
    def on_card_hover_enter(self, card_frame):
        """Handle mouse enter on employee card"""
        if not hasattr(card_frame, 'is_selected') or not card_frame.is_selected:
            card_frame.configure(bg='#e8f4fd')  # Light blue hover effect
    
    def on_card_hover_leave(self, card_frame):
        """Handle mouse leave on employee card"""
        if not hasattr(card_frame, 'is_selected') or not card_frame.is_selected:
            card_frame.configure(bg='#f5f5f7')  # Return to normal background
    
    def auto_clock_process(self):
        """Automatically handle the clock in/out process when employee is selected"""
        if not self.current_employee:
            return
        
        # Wait a moment for camera to start, then proceed
        self.root.after(1000, self.execute_clock_process)
    
    def execute_clock_process(self):
        """Execute the actual clock in/out process"""
        if not self.current_employee:
            return
        
        # Check if we're connected to server
        if not self.connected:
            messagebox.showerror("Error", "Not connected to server. Please connect first.")
            return
        
        # Determine action
        current_status = self.current_employee['status']
        action = 'out' if current_status == 'In' else 'in'
        
        # Take photo first
        if self.camera_active and self.camera:
            try:
                ret, frame = self.camera.read()
                if ret:
                    # Save photo with timestamp
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"employee_{self.current_employee['id']}_{timestamp}.jpg"
                    
                    # Create photos directory if it doesn't exist
                    if not os.path.exists('photos'):
                        os.makedirs('photos')
                    
                    filepath = os.path.join('photos', filename)
                    cv2.imwrite(filepath, frame)
                    
                    self.status_label.config(text=f"Photo captured: {filename}")
                else:
                    messagebox.showwarning("Warning", "Could not capture photo, proceeding with clock action")
            except Exception as e:
                messagebox.showwarning("Warning", f"Photo capture failed: {e}, proceeding with clock action")
        
        # Send data to server
        try:
            clock_data = {
                'employee_id': self.current_employee['id'],
                'action': action,
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            # Send to server
            self.send_to_server(clock_data)
            
            # Update local status
            self.current_employee['status'] = 'In' if action == 'in' else 'Out'
            self.current_employee['last_clock'] = clock_data['timestamp']
            
            # Save updated data
            self.save_employees()
            
            # Update display
            self.update_employee_display()
            
            # Show success message
            action_text = "in" if action == 'in' else "out"
            messagebox.showinfo("Success", f"{self.current_employee['calling_name']} clocked {action_text} successfully!")
            
            # Update clock button for next action
            next_action = "Clock Out" if self.current_employee['status'] == 'In' else "Clock In"
            self.clock_btn.config(text=next_action, 
                                 bg='#f44336' if next_action == "Clock Out" else '#4CAF50')
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to send clock data: {str(e)}")
    
    def highlight_selected_employee(self, selected_id):
        """Highlight the selected employee card"""
        for widget in self.emp_frame.winfo_children():
            if hasattr(widget, 'grid_info'):  # Check if it's a grid widget
                # Find the inner card frame within the outer bevel frame
                for child in widget.winfo_children():
                    if hasattr(child, 'employee_id'):
                        if child.employee_id == selected_id:
                            # Highlight the selected card
                            child.configure(bg='#e3f2fd')
                            child.is_selected = True
                            # Change outer frame color for bevel effect
                            widget.configure(bg='#90caf9')
                        else:
                            # Reset the inner card
                            child.configure(bg='#f5f5f7')
                            child.is_selected = False
                            # Reset outer frame color
                            widget.configure(bg='#e0e0e0')
    
    def toggle_camera(self):
        """Toggle camera on/off"""
        if not self.camera_active:
            self.start_camera()
        else:
            self.stop_camera()
    
    def test_camera_manually(self):
        """Manually test camera functionality for debugging"""
        try:
            print("=== Manual Camera Test ===")
            
            # Test if camera object exists
            if hasattr(self, 'camera'):
                print(f"Camera object exists: {self.camera}")
                if self.camera:
                    print(f"Camera is opened: {self.camera.isOpened()}")
                else:
                    print("Camera object is None")
            else:
                print("No camera object found")
            
            # Test camera_active flag
            print(f"Camera active flag: {self.camera_active}")
            
            # Test if we can create a new camera
            print("Testing new camera creation...")
            test_camera = cv2.VideoCapture(0)
            if test_camera.isOpened():
                print("✅ Test camera opened successfully")
                
                # Try to read a frame
                ret, frame = test_camera.read()
                if ret and frame is not None:
                    print(f"✅ Test camera can read frames: {frame.shape}")
                    
                    # Try to display the frame
                    try:
                        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                        pil_image = Image.fromarray(frame_rgb)
                        pil_image = pil_image.resize((360, 270), Image.Resampling.LANCZOS)
                        photo = ImageTk.PhotoImage(pil_image)
                        
                        # Update the camera label
                        self.camera_label.config(image=photo, text="")
                        self.camera_label.image = photo
                        
                        print("✅ Test frame displayed successfully")
                        messagebox.showinfo("Camera Test", "Camera is working! Test frame displayed.")
                        
                    except Exception as e:
                        print(f"❌ Error displaying test frame: {e}")
                        messagebox.showerror("Camera Test", f"Error displaying frame: {e}")
                else:
                    print("❌ Test camera cannot read frames")
                    messagebox.showerror("Camera Test", "Camera opened but cannot read frames")
                
                test_camera.release()
            else:
                print("❌ Test camera failed to open")
                messagebox.showerror("Camera Test", "Failed to open test camera")
                
        except Exception as e:
            print(f"❌ Camera test failed: {e}")
            messagebox.showerror("Camera Test", f"Test failed: {e}")
        
        print("=== End Camera Test ===")
    
    def start_camera(self):
        """Start the camera"""
        try:
            print("Starting camera...")
            
            # Try different camera devices for cross-platform compatibility
            camera_devices = [0, 1, -1]  # Common camera device numbers
            
            for device in camera_devices:
                try:
                    print(f"Trying camera device {device}...")
                    self.camera = cv2.VideoCapture(device)
                    if self.camera.isOpened():
                        print(f"Camera device {device} opened successfully!")
                        break
                    else:
                        print(f"Camera device {device} failed to open")
                except Exception as e:
                    print(f"Error with camera device {device}: {e}")
                    continue
            
            if self.camera and self.camera.isOpened():
                # Set camera properties for better performance
                self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                self.camera.set(cv2.CAP_PROP_FPS, 30)
                
                self.camera_active = True
                self.camera_btn.config(text="Stop Camera", bg='#f44336')
                self.capture_btn.config(state=tk.NORMAL)
                self.status_label.config(text="Camera active - Starting feed...")
                
                print("Camera started successfully, updating feed...")
                self.update_camera_feed()
            else:
                error_msg = "Could not open camera. Please check if webcam is connected."
                print(f"Camera error: {error_msg}")
                messagebox.showerror("Error", error_msg)
        except Exception as e:
            error_msg = f"Camera error: {str(e)}"
            print(f"Camera exception: {error_msg}")
            messagebox.showerror("Error", error_msg)
    
    def stop_camera(self):
        """Stop the camera"""
        if self.camera:
            self.camera.release()
        self.camera_active = False
        self.camera_btn.config(text="Start Camera", bg='#2196F3')
        self.capture_btn.config(state=tk.DISABLED)
        self.status_label.config(text="Camera stopped")
    
    def update_camera_feed(self):
        """Update camera feed display"""
        if not self.camera_active or not self.camera:
            print("Camera not active, stopping feed update")
            return
            
        try:
            ret, frame = self.camera.read()
            if ret and frame is not None:
                # Convert frame to PIL Image
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                pil_image = Image.fromarray(frame_rgb)
                
                # Resize to fit camera frame (360x270 to match the frame size)
                pil_image = pil_image.resize((360, 270), Image.Resampling.LANCZOS)
                
                # Convert to PhotoImage
                photo = ImageTk.PhotoImage(pil_image)
                
                # Update camera label
                self.camera_label.config(image=photo, text="")
                self.camera_label.image = photo  # Keep a reference
                
                # Update status to show camera is working
                self.status_label.config(text="Camera active - Live feed")
                
                # Schedule next update (30ms = ~33 FPS)
                self.root.after(30, self.update_camera_feed)
            else:
                print(f"Camera read failed: ret={ret}, frame={frame is not None}")
                # Try to continue updating even if frame read fails
                self.root.after(100, self.update_camera_feed)
                
        except Exception as e:
            print(f"Error updating camera feed: {e}")
            # Try to continue updating even if there's an error
            self.root.after(100, self.update_camera_feed)
    
    def capture_photo(self):
        """Capture a photo from the camera"""
        if not self.camera_active or not self.camera:
            messagebox.showerror("Error", "Camera not active")
            return
        
        ret, frame = self.camera.read()
        if ret:
            # Save photo with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"employee_{self.current_employee['id']}_{timestamp}.jpg"
            
            # Create photos directory if it doesn't exist
            if not os.path.exists('photos'):
                os.makedirs('photos')
            
            filepath = os.path.join('photos', filename)
            cv2.imwrite(filepath, frame)
            
            self.status_label.config(text=f"Photo saved: {filename}")
            messagebox.showinfo("Success", f"Photo captured and saved as {filename}")
        else:
            messagebox.showerror("Error", "Could not capture photo")
    
    def clock_action(self):
        """Perform clock in/out action"""
        if not self.current_employee:
            messagebox.showerror("Error", "Please select an employee first")
            return
        
        if not self.connected:
            messagebox.showerror("Error", "Not connected to server. Please connect first.")
            return
        
        # Determine action
        current_status = self.current_employee['status']
        action = 'out' if current_status == 'In' else 'in'
        
        # Take photo first and get filename
        photo_filename = "No photo"
        if self.camera_active and self.camera:
            try:
                ret, frame = self.camera.read()
                if ret:
                    # Save photo with timestamp
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"employee_{self.current_employee['id']}_{timestamp}.jpg"
                    
                    # Create photos directory if it doesn't exist
                    if not os.path.exists('photos'):
                        os.makedirs('photos')
                    
                    filepath = os.path.join('photos', filename)
                    cv2.imwrite(filepath, frame)
                    
                    photo_filename = filename
                    self.status_label.config(text=f"Photo captured: {filename}")
            except Exception as e:
                print(f"Photo capture failed: {e}")
        
        # Send data to server
        try:
            clock_data = {
                'employee_id': self.current_employee['id'],
                'action': action,
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'photo_filename': photo_filename
            }
            
            # Send to server
            self.send_to_server(clock_data)
            
            # Update local status
            self.current_employee['status'] = 'In' if action == 'in' else 'Out'
            self.current_employee['last_clock'] = clock_data['timestamp']
            
            # Save updated data
            self.save_employees()
            
            # Update display
            self.update_employee_display()
            
            # Show success message
            action_text = "in" if action == 'in' else "out"
            messagebox.showinfo("Success", f"{self.current_employee['calling_name']} clocked {action_text} successfully!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to send clock data: {str(e)}")
    
    def send_to_server(self, data):
        """Send data to the admin server using persistent connection"""
        try:
            if self.server_socket and self.connected:
                # Add message type for proper routing
                data['type'] = 'clock_data'
                self.server_socket.send(json.dumps(data).encode())
            else:
                # Fallback to temporary connection if persistent connection is down
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.settimeout(10)  # 10 second timeout
                    s.connect((self.server_host, self.server_port))
                    data['type'] = 'clock_data'
                    s.send(json.dumps(data).encode())
                    s.close()
        except Exception as e:
            self.connected = False
            self.update_connection_status()
            raise Exception(f"Server connection failed: {str(e)}")
    
    def save_employees(self):
        """Save updated employee data"""
        try:
            with open('employees.json', 'w') as f:
                json.dump(self.employees, f, indent=2)
        except Exception as e:
            print(f"Error saving employees: {e}")
    
    def on_closing(self):
        """Handle application closing"""
        if self.camera_active:
            self.stop_camera()
        
        # Disconnect from server
        self.disconnect_from_server()
        
        self.root.destroy()

def main():
    root = tk.Tk()
    app = ClockInOutClient(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()
