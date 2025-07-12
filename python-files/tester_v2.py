import tkinter as tk
from tkinter import ttk, messagebox
import serial
import serial.tools.list_ports
from threading import Thread
import queue
import binascii

class SerialConfigurator:
    def __init__(self, root):
        self.root = root
        self.root.title("Serial Configuration Tool")
        
        # Serial connection variables
        self.serial_connection = None
        self.is_connected = False
        self.data_queue = queue.Queue()
        
        # Configuration variables
        self.config_values = {
            "code": tk.IntVar(value=1),
            "baudrate": tk.IntVar(value=9600),
            "slaveID": tk.IntVar(value=19),
            "dataBit": tk.IntVar(value=0),
            "stopBit": tk.IntVar(value=0),
            "parityBits": tk.IntVar(value=0),
            "channel1_max": tk.IntVar(value=5),
            "channel2_max": tk.IntVar(value=150),
            "channel3_max": tk.IntVar(value=50),
            "channel4_max": tk.IntVar(value=10),
            "channel1_min": tk.IntVar(value=0),
            "channel2_min": tk.IntVar(value=0),
            "channel3_min": tk.IntVar(value=0),
            "channel4_min": tk.IntVar(value=0)
        }
        
        # Create GUI elements
        self.create_widgets()
        
        # Start the periodic check for new data
        self.root.after(100, self.process_incoming_data)
        
        # Populate COM ports initially
        self.update_com_ports()
    
    def create_widgets(self):
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Left panel - Configuration
        config_frame = ttk.LabelFrame(main_frame, text="Configuration Settings", padding=10)
        config_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Right panel - Serial Monitor
        monitor_frame = ttk.LabelFrame(main_frame, text="Serial Monitor", padding=10)
        monitor_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Configuration settings
        self.create_config_controls(config_frame)
        
        # Serial monitor controls
        self.create_serial_controls(monitor_frame)
    
    def create_config_controls(self, parent):
        # Connection settings
        conn_frame = ttk.LabelFrame(parent, text="Connection Settings", padding=5)
        conn_frame.pack(fill=tk.X, pady=5)
        
        # COM Port selection
        ttk.Label(conn_frame, text="COM Port:").grid(row=0, column=0, sticky="w")
        self.com_port_var = tk.StringVar()
        self.com_port_dropdown = ttk.Combobox(conn_frame, textvariable=self.com_port_var)
        self.com_port_dropdown.grid(row=0, column=1, padx=5, pady=2, sticky="ew")
        
        # Refresh COM ports button
        refresh_button = ttk.Button(conn_frame, text="↻", width=3, command=self.update_com_ports)
        refresh_button.grid(row=0, column=2, padx=5, pady=2)
        
        # Baud rate selection
        ttk.Label(conn_frame, text="Baud Rate:").grid(row=1, column=0, sticky="w")
        self.baud_rate_var = tk.StringVar(value="9600")
        baud_rates = ["300", "600", "1200", "2400", "4800", "9600", "14400", 
                      "19200", "28800", "38400", "57600", "115200"]
        self.baud_rate_dropdown = ttk.Combobox(conn_frame, textvariable=self.baud_rate_var, values=baud_rates)
        self.baud_rate_dropdown.grid(row=1, column=1, padx=5, pady=2, sticky="ew")
        
        # Connect/Disconnect button
        self.connect_button = ttk.Button(conn_frame, text="Connect", command=self.toggle_connection)
        self.connect_button.grid(row=2, column=0, columnspan=3, pady=5, sticky="ew")
        
        # Register settings
        reg_frame = ttk.LabelFrame(parent, text="Register Settings", padding=5)
        reg_frame.pack(fill=tk.BOTH, pady=5, expand=True)
        
        # Code (Register 0)
        ttk.Label(reg_frame, text="Code:").grid(row=0, column=0, sticky="w")
        ttk.Entry(reg_frame, textvariable=self.config_values["code"], width=10).grid(row=0, column=1, padx=5, pady=2)
        
        # Baudrate (Register 4)
        ttk.Label(reg_frame, text="Baudrate:").grid(row=1, column=0, sticky="w")
        ttk.Entry(reg_frame, textvariable=self.config_values["baudrate"], width=10).grid(row=1, column=1, padx=5, pady=2)
        
        # SlaveID (Register 6)
        ttk.Label(reg_frame, text="Slave ID:").grid(row=2, column=0, sticky="w")
        ttk.Entry(reg_frame, textvariable=self.config_values["slaveID"], width=10).grid(row=2, column=1, padx=5, pady=2)
        
        # DataBit (Register 7)
        ttk.Label(reg_frame, text="Data Bit:").grid(row=3, column=0, sticky="w")
        ttk.Entry(reg_frame, textvariable=self.config_values["dataBit"], width=10).grid(row=3, column=1, padx=5, pady=2)
        
        # StopBit (Register 8)
        ttk.Label(reg_frame, text="Stop Bit:").grid(row=4, column=0, sticky="w")
        ttk.Entry(reg_frame, textvariable=self.config_values["stopBit"], width=10).grid(row=4, column=1, padx=5, pady=2)
        
        # ParityBits (Register 9)
        ttk.Label(reg_frame, text="Parity Bits:").grid(row=5, column=0, sticky="w")
        ttk.Entry(reg_frame, textvariable=self.config_values["parityBits"], width=10).grid(row=5, column=1, padx=5, pady=2)
        
        # Channel settings frame
        channel_frame = ttk.LabelFrame(parent, text="Channel Settings", padding=5)
        channel_frame.pack(fill=tk.BOTH, pady=5, expand=True)
        
        # Channel max values
        ttk.Label(channel_frame, text="Channel 1 Max:").grid(row=0, column=0, sticky="w")
        ttk.Entry(channel_frame, textvariable=self.config_values["channel1_max"], width=10).grid(row=0, column=1, padx=5, pady=2)
        
        ttk.Label(channel_frame, text="Channel 2 Max:").grid(row=1, column=0, sticky="w")
        ttk.Entry(channel_frame, textvariable=self.config_values["channel2_max"], width=10).grid(row=1, column=1, padx=5, pady=2)
        
        ttk.Label(channel_frame, text="Channel 3 Max:").grid(row=2, column=0, sticky="w")
        ttk.Entry(channel_frame, textvariable=self.config_values["channel3_max"], width=10).grid(row=2, column=1, padx=5, pady=2)
        
        ttk.Label(channel_frame, text="Channel 4 Max:").grid(row=3, column=0, sticky="w")
        ttk.Entry(channel_frame, textvariable=self.config_values["channel4_max"], width=10).grid(row=3, column=1, padx=5, pady=2)
        
        # Channel min values
        ttk.Label(channel_frame, text="Channel 1 Min:").grid(row=0, column=2, sticky="w", padx=(10,0))
        ttk.Entry(channel_frame, textvariable=self.config_values["channel1_min"], width=10).grid(row=0, column=3, padx=5, pady=2)
        
        ttk.Label(channel_frame, text="Channel 2 Min:").grid(row=1, column=2, sticky="w", padx=(10,0))
        ttk.Entry(channel_frame, textvariable=self.config_values["channel2_min"], width=10).grid(row=1, column=3, padx=5, pady=2)
        
        ttk.Label(channel_frame, text="Channel 3 Min:").grid(row=2, column=2, sticky="w", padx=(10,0))
        ttk.Entry(channel_frame, textvariable=self.config_values["channel3_min"], width=10).grid(row=2, column=3, padx=5, pady=2)
        
        ttk.Label(channel_frame, text="Channel 4 Min:").grid(row=3, column=2, sticky="w", padx=(10,0))
        ttk.Entry(channel_frame, textvariable=self.config_values["channel4_min"], width=10).grid(row=3, column=3, padx=5, pady=2)
        
        # Generate and send button
        gen_button = ttk.Button(parent, text="Generate & Send Config", command=self.generate_and_send_config)
        gen_button.pack(pady=10)
    
    def create_serial_controls(self, parent):
        # ADC Control Frame
        adc_frame = ttk.LabelFrame(parent, text="ADC Control", padding=5)
        adc_frame.pack(fill=tk.X, pady=5)
        
        # Start ADC button
        start_adc_btn = ttk.Button(adc_frame, text="Start ADC", command=self.start_adc)
        start_adc_btn.pack(side=tk.LEFT, padx=5, pady=2, expand=True, fill=tk.X)
        
        # Stop ADC button
        stop_adc_btn = ttk.Button(adc_frame, text="Stop ADC", command=self.stop_adc)
        stop_adc_btn.pack(side=tk.LEFT, padx=5, pady=2, expand=True, fill=tk.X)
        
        # Serial monitor text box
        self.serial_text = tk.Text(parent, wrap=tk.WORD, height=20, width=50)
        self.serial_text.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=self.serial_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.serial_text.config(yscrollcommand=scrollbar.set)
        
        # Control buttons frame
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill=tk.X, pady=5)
        
        # Clear button
        clear_button = ttk.Button(button_frame, text="Clear", command=self.clear_monitor)
        clear_button.pack(side=tk.LEFT, padx=5)
        
        # Send custom hex frame
        custom_frame = ttk.Frame(parent)
        custom_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(custom_frame, text="Custom Hex:").pack(side=tk.LEFT)
        self.custom_hex_var = tk.StringVar()
        custom_entry = ttk.Entry(custom_frame, textvariable=self.custom_hex_var)
        custom_entry.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
        custom_entry.bind('<Return>', lambda event: self.send_custom_hex())
        
        send_button = ttk.Button(custom_frame, text="Send", command=self.send_custom_hex)
        send_button.pack(side=tk.LEFT)
    
    def start_adc(self):
        """Send command to start ADC (0x02)"""
        if not self.is_connected:
            messagebox.showerror("Error", "Not connected to any serial port!")
            return
        
        try:
            self.serial_connection.write(b'\x02')
            self.serial_text.insert(tk.END, "Sent: 0x02 (Start ADC)\n")
            self.serial_text.see(tk.END)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to send start command: {str(e)}")
    
    def stop_adc(self):
        """Send command to stop ADC (0x03)"""
        if not self.is_connected:
            messagebox.showerror("Error", "Not connected to any serial port!")
            return
        
        try:
            self.serial_connection.write(b'\x03')
            self.serial_text.insert(tk.END, "Sent: 0x03 (Stop ADC)\n")
            self.serial_text.see(tk.END)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to send stop command: {str(e)}")
    
    def update_com_ports(self):
        """Update the list of available COM ports"""
        ports = [port.device for port in serial.tools.list_ports.comports()]
        self.com_port_dropdown['values'] = ports
        if ports:
            self.com_port_var.set(ports[0])
    
    def toggle_connection(self):
        """Connect or disconnect from the serial port"""
        if not self.is_connected:
            self.connect_serial()
        else:
            self.disconnect_serial()
    
    def connect_serial(self):
        """Establish serial connection"""
        com_port = self.com_port_var.get()
        baud_rate = self.baud_rate_var.get()
        
        if not com_port:
            self.serial_text.insert(tk.END, "No COM port selected!\n")
            return
        
        try:
            self.serial_connection = serial.Serial(com_port, int(baud_rate), timeout=1)
            self.is_connected = True
            self.connect_button.config(text="Disconnect")
            self.serial_text.insert(tk.END, f"Connected to {com_port} at {baud_rate} baud\n")
            
            # Start a thread to read from the serial port
            self.read_thread = Thread(target=self.read_from_serial, daemon=True)
            self.read_thread.start()
            
        except Exception as e:
            self.serial_text.insert(tk.END, f"Error connecting to {com_port}: {str(e)}\n")
    
    def disconnect_serial(self):
        """Close the serial connection"""
        if self.serial_connection and self.serial_connection.is_open:
            self.serial_connection.close()
        self.is_connected = False
        self.connect_button.config(text="Connect")
        self.serial_text.insert(tk.END, "Disconnected from serial port\n")
    
    def read_from_serial(self):
        """Read data from serial port in a separate thread"""
        while self.is_connected and self.serial_connection and self.serial_connection.is_open:
            try:
                if self.serial_connection.in_waiting:
                    line = self.serial_connection.readline().decode('utf-8', errors='replace').strip()
                    if line:
                        self.data_queue.put(line)
            except:
                break
    
    def process_incoming_data(self):
        """Process incoming data from the queue in the main thread"""
        while not self.data_queue.empty():
            data = self.data_queue.get()
            self.serial_text.insert(tk.END, data + "\n")
            self.serial_text.see(tk.END)
        
        # Schedule this method to run again
        self.root.after(100, self.process_incoming_data)
    
    def generate_and_send_config(self):
        """Generate hex configuration from settings and send it"""
        if not self.is_connected:
            messagebox.showerror("Error", "Not connected to any serial port!")
            return
        
        try:
            # Create the configuration bytes according to your table
            config_bytes = bytearray()
            
            # Register 0 - Code
            config_bytes.extend(self.int_to_bytes(self.config_values["code"].get(), 1))
            
            # Registers 1-3 - Empty
            config_bytes.extend(b'\x00\x00')
            
            # Register 4 - Baudrate (example: 9600 -> 0x002580)
            config_bytes.extend(self.int_to_bytes(self.config_values["baudrate"].get(), 3))

            # Register 6 - SlaveID
            config_bytes.extend(self.int_to_bytes(self.config_values["slaveID"].get(), 1))
            
            # Registers 7-9 - DataBit, StopBit, ParityBits
            config_bytes.extend(self.int_to_bytes(self.config_values["dataBit"].get(), 1))
            config_bytes.extend(self.int_to_bytes(self.config_values["stopBit"].get(), 1))
            config_bytes.extend(self.int_to_bytes(self.config_values["parityBits"].get(), 1))
            
            # Register 12 - Channel 2 Max
            config_bytes.extend(self.int_to_bytes(self.config_values["channel2_max"].get(), 3))
            # Register 15 - Channel 3 Max
            config_bytes.extend(self.int_to_bytes(self.config_values["channel3_max"].get(), 3))
            # Register 18 - Channel 4 Max
            config_bytes.extend(self.int_to_bytes(self.config_values["channel4_max"].get(), 3))
            
            # Register 21 - Channel 1 Max
            config_bytes.extend(self.int_to_bytes(self.config_values["channel1_max"].get(), 3))
            
            # Registers 22-25 - Channel Min values
            config_bytes.extend(self.int_to_bytes(self.config_values["channel1_min"].get(), 1))
            config_bytes.extend(self.int_to_bytes(self.config_values["channel2_min"].get(), 1))
            config_bytes.extend(self.int_to_bytes(self.config_values["channel3_min"].get(), 1))
            config_bytes.extend(self.int_to_bytes(self.config_values["channel4_min"].get(), 1))
            
            # Send the configuration
            self.serial_connection.write(config_bytes)
            
            # Display the sent data
            hex_str = ' '.join(f'{b:02X}' for b in config_bytes)
            self.serial_text.insert(tk.END, f"Sent configuration: {hex_str}\n")
            self.serial_text.see(tk.END)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to send configuration: {str(e)}")
    
    def int_to_bytes(self, value, length):
        """Convert integer to bytes with specified length"""
        return value.to_bytes(length, byteorder='big')
    
    def send_custom_hex(self):
        """Send custom hex data entered by user"""
        if not self.is_connected:
            messagebox.showerror("Error", "Not connected to any serial port!")
            return
        
        hex_str = self.custom_hex_var.get()
        if not hex_str:
            messagebox.showerror("Error", "Please enter hex data to send!")
            return
        
        try:
            # Remove any whitespace or common hex separators
            clean_hex = hex_str.replace(" ", "").replace("0x", "").replace(",", "").replace(":", "")
            if len(clean_hex) % 2 != 0:
                messagebox.showerror("Error", "Hex data must have even number of characters!")
                return
            
            binary_data = binascii.unhexlify(clean_hex)
            self.serial_connection.write(binary_data)
            self.serial_text.insert(tk.END, f"Sent custom HEX: {hex_str}\n")
            self.serial_text.see(tk.END)
            self.custom_hex_var.set("")  # Clear the entry field
        except binascii.Error:
            messagebox.showerror("Error", "Invalid hex data!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to send data: {str(e)}")
    
    def clear_monitor(self):
        """Clear the serial monitor text box"""
        self.serial_text.delete(1.0, tk.END)
    
    def on_closing(self):
        """Clean up when closing the window"""
        if self.is_connected:
            self.disconnect_serial()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = SerialConfigurator(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()