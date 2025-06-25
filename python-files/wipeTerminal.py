import tkinter as tk
from tkinter import ttk, messagebox
import serial
import time
from serial.tools import list_ports

class MotorControlGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Motor Control Interface")
        self.root.geometry("450x580")
        self.root.configure(bg='#f0f0f0')
        self.root.resizable(False, False)
        
        # Variables
        self.serial_conn = None
        self.is_connected = False
        self.last_direction = None
        
        # Create widgets
        self.create_widgets()
        self.refresh_com_ports()
        
    def create_widgets(self):
        """Create formal GUI layout"""
        
        # Main container
        main_frame = tk.Frame(self.root, bg='#f0f0f0')
        main_frame.pack(fill='both', expand=True, padx=20, pady=15)
        
        # Title Section
        title_frame = tk.Frame(main_frame, bg='#f0f0f0')
        title_frame.pack(fill='x', pady=(0, 20))
        
        title = tk.Label(title_frame, text="Motor Control Interface", 
                        bg='#f0f0f0', fg='#000000', font=('Arial', 16, 'bold'))
        title.pack()
        
        subtitle = tk.Label(title_frame, text="Serial Communication Controller", 
                           bg='#f0f0f0', fg='#666666', font=('Arial', 10))
        subtitle.pack(pady=(5, 0))
        
        # Connection Section
        conn_section = tk.LabelFrame(main_frame, text="Connection Settings", 
                                   bg='white', fg='#000000', font=('Arial', 11, 'bold'),
                                   relief='groove', bd=2, padx=15, pady=10)
        conn_section.pack(fill='x', pady=(0, 15))
        
        # COM Port Row
        port_frame = tk.Frame(conn_section, bg='white')
        port_frame.pack(fill='x', pady=5)
        
        tk.Label(port_frame, text="COM Port:", bg='white', fg='#000000', 
                font=('Arial', 10), width=12, anchor='w').pack(side='left')
        
        self.port_var = tk.StringVar()
        self.port_combo = ttk.Combobox(port_frame, textvariable=self.port_var, 
                                      width=10, font=('Arial', 10), state='readonly')
        self.port_combo.pack(side='left', padx=(10, 10))
        
        refresh_btn = tk.Button(port_frame, text="Refresh", command=self.refresh_com_ports,
                               bg='#e0e0e0', fg='#000000', font=('Arial', 9),
                               relief='raised', bd=1, width=10, height=1)
        refresh_btn.pack(side='left')
        
        # Baud Rate Row
        baud_frame = tk.Frame(conn_section, bg='white')
        baud_frame.pack(fill='x', pady=5)
        
        tk.Label(baud_frame, text="Baud Rate:", bg='white', fg='#000000', 
                font=('Arial', 10), width=12, anchor='w').pack(side='left')
        
        self.baud_var = tk.StringVar(value="9600")
        baud_entry = tk.Entry(baud_frame, textvariable=self.baud_var, width=10,
                             bg='white', fg='#000000', font=('Arial', 10),
                             relief='sunken', bd=1)
        baud_entry.pack(side='left', padx=(10, 0))
        
        # Connect Button Row
        connect_frame = tk.Frame(conn_section, bg='white')
        connect_frame.pack(fill='x', pady=(10, 0))
        
        self.connect_btn = tk.Button(connect_frame, text="CONNECT", command=self.toggle_connection,
                                   bg='#007acc', fg='white', font=('Arial', 11, 'bold'),
                                   relief='raised', bd=2, width=18, height=2)
        self.connect_btn.pack()
        
        # Status Section
        status_section = tk.LabelFrame(main_frame, text="Connection Status", 
                                     bg='white', fg='#000000', font=('Arial', 11, 'bold'),
                                     relief='groove', bd=2, padx=15, pady=10)
        status_section.pack(fill='x', pady=(0, 15))
        
        self.status_label = tk.Label(status_section, text="Status: Disconnected", 
                                   bg='white', fg='#cc0000', font=('Arial', 10, 'bold'))
        self.status_label.pack(pady=5)
        
        self.last_cmd_label = tk.Label(status_section, text="Last Command: None", 
                                     bg='white', fg='#666666', font=('Arial', 9))
        self.last_cmd_label.pack()
        
        # Control Section
        control_section = tk.LabelFrame(main_frame, text="Motor Controls", 
                                      bg='white', fg='#000000', font=('Arial', 11, 'bold'),
                                      relief='groove', bd=2, padx=15, pady=10)
        control_section.pack(fill='x', pady=(0, 15))
        
        # Control Buttons Container
        btn_container = tk.Frame(control_section, bg='white')
        btn_container.pack(pady=5)
        
        # Row 1: Forward, Backward
        row1 = tk.Frame(btn_container, bg='white')
        row1.pack(pady=5)
        
        self.forward_btn = tk.Button(row1, text="FORWARD", command=lambda: self.send_command('F'),
                                   bg='#28a745', fg='white', font=('Arial', 10, 'bold'),
                                   relief='raised', bd=2, width=12, height=2)
        self.forward_btn.pack(side='left', padx=10)
        
        self.backward_btn = tk.Button(row1, text="BACKWARD", command=lambda: self.send_command('B'),
                                    bg='#17a2b8', fg='white', font=('Arial', 10, 'bold'),
                                    relief='raised', bd=2, width=12, height=2)
        self.backward_btn.pack(side='left', padx=10)
        
        # Row 2: Stop, Oscillate
        row2 = tk.Frame(btn_container, bg='white')
        row2.pack(pady=5)
        
        self.stop_btn = tk.Button(row2, text="STOP", command=lambda: self.send_command('S'),
                                bg='#dc3545', fg='white', font=('Arial', 10, 'bold'),
                                relief='raised', bd=2, width=12, height=2)
        self.stop_btn.pack(side='left', padx=10)
        
        self.oscillate_btn = tk.Button(row2, text="OSCILLATE", command=lambda: self.send_command('O'),
                                     bg='#fd7e14', fg='white', font=('Arial', 10, 'bold'),
                                     relief='raised', bd=2, width=12, height=2)
        self.oscillate_btn.pack(side='left', padx=10)
        
        # Row 3: Toggle
        row3 = tk.Frame(btn_container, bg='white')
        row3.pack(pady=5)
        
        self.toggle_btn = tk.Button(row3, text="TOGGLE DIRECTION", command=self.toggle_direction,
                                  bg='#6f42c1', fg='white', font=('Arial', 10, 'bold'),
                                  relief='raised', bd=2, width=26, height=2)
        self.toggle_btn.pack()
        
        # Disable buttons initially
        self.set_buttons_state('disabled')
        
        # Information Section
        info_section = tk.LabelFrame(main_frame, text="Command Reference", 
                                   bg='white', fg='#000000', font=('Arial', 11, 'bold'),
                                   relief='groove', bd=2, padx=15, pady=10)
        info_section.pack(fill='x')
        
        info_frame = tk.Frame(info_section, bg='white')
        info_frame.pack()
        
        commands = [
            "F - Forward (Clockwise)",
            "B - Backward (Anticlockwise)",
            "S - Stop Motor",
            "O - Oscillate Mode",
            "Toggle - Alternates F/B"
        ]
        
        for cmd in commands:
            tk.Label(info_frame, text="• " + cmd, bg='white', fg='#666666', 
                    font=('Arial', 9), anchor='w').pack(fill='x', pady=1)
    
    def refresh_com_ports(self):
        """Get available COM ports"""
        ports = [port.device for port in list_ports.comports()]
        self.port_combo['values'] = ports
        if ports:
            self.port_combo.set(ports[0])
    
    def toggle_connection(self):
        """Connect or disconnect"""
        if not self.is_connected:
            self.connect_serial()
        else:
            self.disconnect_serial()
    
    def connect_serial(self):
        """Connect to serial port"""
        try:
            port = self.port_var.get()
            baud = int(self.baud_var.get())
            
            if not port:
                messagebox.showerror("Connection Error", "Please select a COM port")
                return
            
            self.serial_conn = serial.Serial(port, baud, timeout=1)
            time.sleep(2)
            
            self.is_connected = True
            self.connect_btn.config(text="DISCONNECT", bg='#dc3545')
            self.status_label.config(text=f"Status: Connected to {port}", fg='#28a745')
            self.set_buttons_state('normal')
            
            messagebox.showinfo("Connection Success", f"Connected to {port} successfully")
            
        except Exception as e:
            messagebox.showerror("Connection Error", f"Failed to connect:\n{str(e)}")
    
    def disconnect_serial(self):
        """Disconnect from serial port"""
        if self.serial_conn:
            self.serial_conn.close()
            self.serial_conn = None
        
        self.is_connected = False
        self.connect_btn.config(text="CONNECT", bg='#007acc')
        self.status_label.config(text="Status: Disconnected", fg='#cc0000')
        self.set_buttons_state('disabled')
        self.last_cmd_label.config(text="Last Command: None")
        self.last_direction = None
    
    def set_buttons_state(self, state):
        """Enable/disable control buttons"""
        buttons = [self.forward_btn, self.backward_btn, self.stop_btn, 
                  self.oscillate_btn, self.toggle_btn]
        for btn in buttons:
            btn.config(state=state)
    
    def send_command(self, command):
        """Send command to Arduino"""
        if not self.is_connected:
            messagebox.showwarning("Connection Warning", "Device is not connected")
            return
        
        try:
            self.serial_conn.write(command.encode())
            
            cmd_names = {'F': 'Forward', 'B': 'Backward', 'S': 'Stop', 'O': 'Oscillate'}
            self.last_cmd_label.config(text=f"Last Command: {cmd_names.get(command, command)}")
            
            if command in ['F', 'B']:
                self.last_direction = command
                
        except Exception as e:
            messagebox.showerror("Communication Error", f"Failed to send command:\n{str(e)}")
            self.disconnect_serial()
    
    def toggle_direction(self):
        """Toggle between Forward and Backward"""
        if self.last_direction == 'F':
            self.send_command('B')
        else:
            self.send_command('F')
    
    def on_closing(self):
        """Handle window closing"""
        if self.is_connected:
            self.disconnect_serial()
        self.root.destroy()

def main():
    root = tk.Tk()
    app = MotorControlGUI(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()