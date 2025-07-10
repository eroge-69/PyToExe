import serial
import time
import re
import logging
from typing import Optional, List
import tkinter as tk
from tkinter import ttk, messagebox
from ttkbootstrap import Style
import serial.tools.list_ports
from threading import Thread
import pandas as pd
from datetime import datetime

# Configuration constants
BAUDRATE = 9600
TIMEOUT = 2
COMMAND_DELAY = 0.5
TRIGGER_DELAY = 2.0
MAX_RETRIES = 3
VALID_UNITS = {'K', 'C', 'F'}
CHANNEL_RANGE = range(1, 21)  # Channels 1 to 20
OPEN_VALUE = 9000000000.00  # Value to interpret as "OPEN"

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class FlukeGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Fluke 2625A Temperature Reader")
        Style('flatly')  # Using ttkbootstrap for modern look
        
        self.ser = None
        self.is_scanning = False
        self.is_continuous = False
        self.active_channels = []
        self.scan_data = []  # Store all scan results with timestamps
        
        # Main frame
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Status label (moved above table)
        self.status_var = tk.StringVar(value="Disconnected")
        ttk.Label(self.main_frame, textvariable=self.status_var, style='Info.TLabel').grid(row=0, column=0, columnspan=4, pady=5)
        
        # COM Port Selection
        ttk.Label(self.main_frame, text="COM Port:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.com_var = tk.StringVar()
        self.com_combo = ttk.Combobox(self.main_frame, textvariable=self.com_var, width=15)
        self.com_combo.grid(row=1, column=1, padx=5, pady=5)
        self.update_com_ports()
        
        # Number of Scans
        ttk.Label(self.main_frame, text="Number of Scans:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        self.scans_var = tk.StringVar(value="1")
        self.scans_entry = ttk.Entry(self.main_frame, textvariable=self.scans_var, width=10)
        self.scans_entry.grid(row=2, column=1, padx=5, pady=5)
        
        # Continuous Scan Interval (in minutes)
        ttk.Label(self.main_frame, text="Interval (minutes):").grid(row=2, column=2, padx=5, pady=5, sticky=tk.W)
        self.interval_var = tk.StringVar(value="1")
        self.interval_entry = ttk.Entry(self.main_frame, textvariable=self.interval_var, width=10)
        self.interval_entry.grid(row=2, column=3, padx=5, pady=5)
        
        # Continuous Run Time (in minutes)
        ttk.Label(self.main_frame, text="Run Time (minutes):").grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)
        self.runtime_var = tk.StringVar(value="")  # Empty by default, optional
        self.runtime_entry = ttk.Entry(self.main_frame, textvariable=self.runtime_var, width=10)
        self.runtime_entry.grid(row=3, column=1, padx=5, pady=5)
        
        # Buttons
        self.start_button = ttk.Button(self.main_frame, text="Start Scan", command=self.start_scan)
        self.start_button.grid(row=4, column=0, padx=5, pady=10)
        
        self.stop_button = ttk.Button(self.main_frame, text="Stop Scan", command=self.stop_scan, state='disabled')
        self.stop_button.grid(row=4, column=1, padx=5, pady=10)
        
        self.continuous_button = ttk.Checkbutton(
            self.main_frame, 
            text="Continuous Scan", 
            command=self.toggle_continuous, 
            style='primary.TCheckbutton'
        )
        self.continuous_button.grid(row=4, column=2, padx=5, pady=10)
        
        self.identify_button = ttk.Button(self.main_frame, text="Identify Equipment", command=self.identify_equipment)
        self.identify_button.grid(row=4, column=3, padx=5, pady=10)
        
        self.export_button = ttk.Button(self.main_frame, text="Export to Excel", command=self.export_to_excel, state='disabled')
        self.export_button.grid(row=4, column=4, padx=5, pady=10)
        
        # Table for results
        columns = ['Timestamp'] + [f'Channel {ch}' for ch in CHANNEL_RANGE] + ['Status']
        self.tree = ttk.Treeview(self.main_frame, columns=columns, show='headings')
        self.tree.heading('Timestamp', text='Timestamp')
        for ch in CHANNEL_RANGE:
            self.tree.heading(f'Channel {ch}', text=f'Channel {ch}')
        self.tree.heading('Status', text='Status')
        self.tree.column('Timestamp', width=150, anchor='center')
        for ch in CHANNEL_RANGE:
            self.tree.column(f'Channel {ch}', width=80, anchor='center')
        self.tree.column('Status', width=150, anchor='center')
        self.tree.grid(row=5, column=0, columnspan=4, padx=5, pady=5)
        
        # Scrollbar for table
        scrollbar = ttk.Scrollbar(self.main_frame, orient=tk.VERTICAL, command=self.tree.yview)
        scrollbar.grid(row=5, column=4, sticky='ns')
        self.tree.configure(yscrollcommand=scrollbar.set)

    def update_com_ports(self):
        ports = [port.device for port in serial.tools.list_ports.comports()]
        self.com_combo['values'] = ports
        if ports:
            self.com_var.set(ports[0])
        else:
            self.com_var.set("")
            self.status_var.set("No COM ports available")

    def connect_fluke_2625a(self, port: str) -> Optional[serial.Serial]:
        if not port:
            logger.error("No COM port selected")
            self.status_var.set("No COM port selected")
            return None
        try:
            available_ports = [p.device for p in serial.tools.list_ports.comports()]
            if port not in available_ports:
                logger.error(f"COM port {port} is not available")
                self.status_var.set(f"COM port {port} is not available")
                return None
            ser = serial.Serial(
                port=port,
                baudrate=BAUDRATE,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                timeout=TIMEOUT
            )
            logger.info(f"Connected to Fluke 2625A on {port}")
            self.status_var.set(f"Connected to {port}")
            return ser
        except serial.SerialException as e:
            logger.error(f"Failed to connect to {port}: {e}")
            self.status_var.set(f"Connection failed: {e}")
            messagebox.showerror("Error", f"Failed to connect to {port}: {e}\nEnsure the port is not in use and try again.")
            return None

    def send_command(self, ser: serial.Serial, command: str, delay: float = COMMAND_DELAY, retries: int = MAX_RETRIES) -> str:
        for attempt in range(retries):
            try:
                logger.debug(f"Sending command: {command}")
                ser.write(command.encode() + b'\r\n')
                time.sleep(delay)
                response = ser.read_all().decode().strip()
                cleaned_response = re.sub(r'=>\s*$', '', response).strip()
                logger.debug(f"Received response: '{cleaned_response}'")
                if cleaned_response == '?>':
                    logger.warning(f"Syntax error for command '{command}'")
                    return ''
                elif cleaned_response == '!>':
                    logger.warning(f"Execution error for command '{command}'")
                    return ''
                return cleaned_response
            except serial.SerialException as e:
                logger.error(f"Serial error on attempt {attempt + 1} for '{command}': {e}")
                if attempt < retries - 1:
                    time.sleep(0.2)
                continue
        logger.error(f"Failed to get valid response for '{command}' after {retries} attempts")
        return ''

    def parse_temperature_response(self, response: str, channel: int) -> tuple[Optional[float], str]:
        try:
            response = response.strip().replace('"', '')
            if not response:
                logger.error(f"Empty response for channel {channel}")
                return None, "N/A"
            if ',' in response:
                parts = response.split(',')
                if len(parts) < 2:
                    logger.error(f"Invalid response format for channel {channel}: '{response}'")
                    return None, "N/A"
                value_str, unit = parts[0].strip(), parts[1].strip().upper()
                if value_str.upper() in {'OPEN', 'OVERLOAD', 'ERROR', 'N/A', 'INVALID', 'NAN'}:
                    logger.error(f"Measurement error on channel {channel}: {value_str}")
                    return None, "N/A"
                if unit not in VALID_UNITS:
                    logger.error(f"Invalid unit '{unit}' for channel {channel}")
                    return None, "N/A"
                temp_value = float(value_str)
                if temp_value == OPEN_VALUE:
                    logger.info(f"Channel {channel} value {temp_value} interpreted as OPEN")
                    return None, "OPEN"
                return temp_value, f"{temp_value:.2f}"
            else:
                temp_value = float(response)
                if temp_value == OPEN_VALUE:
                    logger.info(f"Channel {channel} value {temp_value} interpreted as OPEN")
                    return None, "OPEN"
                return temp_value, f"{temp_value:.2f}"
        except ValueError:
            logger.error(f"Could not convert response '{response}' to float for channel {channel}")
            return None, "N/A"
        except Exception as e:
            logger.error(f"Error parsing response for channel {channel}: {e}")
            return None, "N/A"

    def check_device_status(self, ser: serial.Serial) -> List[int]:
        logger.info("Checking device status")
        active_channels = []
        for ch in CHANNEL_RANGE:
            func_status = self.send_command(ser, f'FUNC? {ch}')
            status = func_status if func_status and func_status.strip().upper() != 'OFF' else 'OFF'
            logger.info(f"Channel {ch}: Function: {status}")
            if status != 'OFF':
                active_channels.append(ch)
        logger.info(f"Active channels: {active_channels}")
        return active_channels

    def identify_equipment(self):
        port = self.com_var.get()
        if not port:
            messagebox.showerror("Error", "Please select a COM port")
            return
        ser = self.connect_fluke_2625a(port)
        if not ser:
            return
        try:
            idn = self.send_command(ser, '*IDN?')
            if idn:
                logger.info(f"Device ID: {idn}")
                self.status_var.set(f"Device ID: {idn}")
                messagebox.showinfo("Equipment Info", f"Device ID: {idn}\nCOM Port: {port}\nSettings: {BAUDRATE} baud, 8N1")
            else:
                logger.error("No response from device")
                self.status_var.set("No response from device")
                messagebox.showerror("Error", "No response from device")
        except Exception as e:
            logger.error(f"Error identifying equipment: {e}")
            self.status_var.set(f"Error identifying: {e}")
            messagebox.showerror("Error", f"Error identifying equipment: {e}")
        finally:
            if ser:
                try:
                    ser.close()
                    logger.info("Serial connection closed after identification")
                except Exception as e:
                    logger.error(f"Error closing serial connection: {e}")

    def read_temperature(self, ser: serial.Serial, channels: List[int], num_scans: int):
        self.is_scanning = True
        self.start_button.config(state='disabled')
        self.stop_button.config(state='normal')
        self.export_button.config(state='normal')
        
        start_time = time.time()
        scan_count = 0
        while self.is_scanning:
            if not self.is_continuous and scan_count >= num_scans:
                break
            try:
                runtime = float(self.runtime_var.get()) * 60 if self.runtime_var.get() else float('inf')
                if time.time() - start_time > runtime:
                    logger.info("Continuous run time expired")
                    self.status_var.set("Run time expired")
                    self.is_scanning = False
                    break
            except ValueError:
                if self.runtime_var.get():
                    logger.error("Invalid run time value")
                    self.status_var.set("Invalid run time value")
                    self.is_scanning = False
                    break
                
            temperatures = {ch: None for ch in channels}
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            row_data = {'Timestamp': timestamp}
            status = "Success"
            
            try:
                if not channels:
                    logger.warning("No channels provided for temperature reading")
                    self.status_var.set("No active channels")
                    return

                self.send_command(ser, 'SCAN 1', delay=COMMAND_DELAY)
                for channel in channels:
                    if not self.is_scanning:
                        break
                    if channel not in CHANNEL_RANGE:
                        logger.warning(f"Invalid channel {channel}. Skipping.")
                        row_data[f'Channel {channel}'] = "N/A"
                        status = "Invalid Channel"
                        continue
                    self.send_command(ser, f'MON 1,{channel}', delay=COMMAND_DELAY)
                    response = self.send_command(ser, 'MON_VAL?', delay=TRIGGER_DELAY)
                    logger.info(f"MON_VAL? response for channel {channel}: '{response}'")
                    temp_value, display_value = self.parse_temperature_response(response, channel)
                    if temp_value is not None:
                        logger.info(f"Channel {channel}: {temp_value:.2f}")
                        temperatures[channel] = temp_value
                        row_data[f'Channel {channel}'] = display_value
                    else:
                        logger.error(f"Failed to get valid measurement for channel {channel}")
                        row_data[f'Channel {channel}'] = display_value
                        status = "Failed"
                    self.root.update()
                self.send_command(ser, 'SCAN 0', delay=COMMAND_DELAY)
                
                row_data['Status'] = status
                self.scan_data.append(row_data)
                self.tree.insert('', 'end', values=[row_data.get(col, 'N/A') for col in self.tree['columns']])
                self.status_var.set(f"Completed scan {scan_count + 1}/{num_scans if not self.is_continuous else 'continuous'}")
                
                scan_count += 1
                if self.is_continuous and self.is_scanning:
                    try:
                        interval = float(self.interval_var.get()) * 60
                        if interval <= 0:
                            raise ValueError("Interval must be positive")
                        time.sleep(interval)
                    except ValueError:
                        logger.error("Invalid interval value")
                        self.status_var.set("Invalid interval value")
                        self.is_scanning = False
                        break
                
            except serial.SerialException as e:
                logger.error(f"Serial error reading temperatures: {e}")
                self.status_var.set(f"Serial error: {e}")
                self.close_serial()
                break
            except Exception as e:
                logger.error(f"Unexpected error reading temperatures: {e}")
                self.status_var.set(f"Error: {e}")
                self.close_serial()
                break

        self.is_scanning = False
        self.start_button.config(state='normal')
        self.stop_button.config(state='disabled')
        self.continuous_button.config(state='normal')
        self.export_button.config(state='normal')
        self.close_serial()
        self.status_var.set("Scan completed, port closed")

    def toggle_continuous(self):
        self.is_continuous = not self.is_continuous
        state = "Continuous" if self.is_continuous else "Single"
        self.status_var.set(f"Scan mode: {state}")
        logger.info(f"Continuous scan mode: {self.is_continuous}")

    def close_serial(self):
        if self.ser:
            try:
                self.send_command(self.ser, 'SCAN 0')
                self.ser.close()
                self.ser = None
                logger.info("Serial connection closed")
                self.status_var.set("Serial connection closed")
            except Exception as e:
                logger.error(f"Error closing serial connection: {e}")
                self.status_var.set(f"Error closing serial: {e}")

    def start_scan(self):
        if self.is_scanning:
            return
        
        try:
            num_scans = int(self.scans_var.get())
            if num_scans <= 0:
                messagebox.showerror("Error", "Number of scans must be positive")
                return
        except ValueError:
            messagebox.showerror("Error", "Invalid number of scans")
            return

        if self.is_continuous:
            try:
                interval = float(self.interval_var.get())
                if interval <= 0:
                    messagebox.showerror("Error", "Interval must be positive")
                    return
            except ValueError:
                messagebox.showerror("Error", "Invalid interval value")
                return
            if self.runtime_var.get():
                try:
                    runtime = float(self.runtime_var.get())
                    if runtime <= 0:
                        messagebox.showerror("Error", "Run time must be positive")
                        return
                except ValueError:
                    messagebox.showerror("Error", "Invalid run time value")
                    return

        port = self.com_var.get()
        if not port:
            messagebox.showerror("Error", "Please select a COM port")
            return

        self.ser = self.connect_fluke_2625a(port)
        if not self.ser:
            return

        try:
            idn = self.send_command(self.ser, '*IDN?')
            logger.info(f"Device ID: {idn}")
            self.status_var.set(f"Device ID: {idn}")

            if not self.active_channels:
                self.active_channels = self.check_device_status(self.ser)
            if not self.active_channels:
                logger.error("No active channels found")
                self.status_var.set("No active channels found")
                self.close_serial()
                return

            scan_thread = Thread(target=self.read_temperature, args=(self.ser, self.active_channels, num_scans))
            scan_thread.start()
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            self.status_var.set(f"Error: {e}")
            self.close_serial()

    def stop_scan(self):
        self.is_scanning = False
        self.is_continuous = False
        self.continuous_button.state(['!selected'])
        self.close_serial()
        self.status_var.set("Scan stopped, port closed")
        self.export_button.config(state='normal')

    def export_to_excel(self):
        if not self.scan_data:
            messagebox.showinfo("Info", "No data to export")
            return
        
        try:
            df = pd.DataFrame(self.scan_data)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"fluke_2625a_data_{timestamp}.xlsx"
            df.to_excel(filename, index=False)
            messagebox.showinfo("Success", f"Data exported to {filename}")
            logger.info(f"Data exported to {filename}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export data: {e}")
            logger.error(f"Failed to export data: {e}")

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    root = tk.Tk()
    app = FlukeGUI(root)
    app.run()