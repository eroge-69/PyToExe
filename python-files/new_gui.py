import tkinter as tk
from tkinter import scrolledtext, messagebox, ttk
import serial
import serial.tools.list_ports
import threading
import time

def calculate_crc(data: bytes) -> int:
    crc = 0xFFFF
    for b in data:
        crc ^= b
        for _ in range(8):
            if (crc & 0x0001):
                crc = (crc >> 1) ^ 0xA001
            else:
                crc >>= 1
    crc = ((crc & 0xFF00) >> 8) | ((crc & 0x00FF) << 8)
    return crc

class USBCRCGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("1.5kW CRC Checker")

        self.pass_count = 0
        self.fail_count = 0
        self.error_count = 0
        self.running = False
        self.loop_mode = False
        self.ser = None
        self.serial_thread = None
        self.loop_thread = None

        # --- Serial Port Selection ---
        tk.Label(root, text="Select Serial Port:").pack()
        self.port_combo = ttk.Combobox(root, values=self.get_serial_ports(), state='readonly')
        self.port_combo.pack()
        if self.port_combo['values']:
            self.port_combo.current(0)  # Select first available port by default

        # --- Baud Rate Selection ---
        tk.Label(root, text="Select Baud Rate:").pack()
        self.baud_combo = ttk.Combobox(root, values=[9600, 19200, 38400, 57600, 115200], state='readonly')
        self.baud_combo.pack()
        self.baud_combo.current(0)  # default to 9600

        # Text area
        self.text_area = scrolledtext.ScrolledText(root, width=70, height=20)
        self.text_area.pack(pady=10)

        # Labels for counts
        self.pass_label = tk.Label(root, text="Pass: 0", fg="green")
        self.pass_label.pack()
        self.fail_label = tk.Label(root, text="Fail: 0", fg="red")
        self.fail_label.pack()
        self.error_label = tk.Label(root, text="No Response Errors: 0", fg="orange")
        self.error_label.pack()

        # Data entry
        tk.Label(root, text="Enter Data to Send (hex):").pack()
        self.data_entry = tk.Entry(root, width=40)
        self.data_entry.pack()

        # Loop interval entry (milliseconds)
        tk.Label(root, text="Loop Interval (milliseconds):").pack()
        self.interval_entry = tk.Entry(root, width=10)
        self.interval_entry.pack()
        self.interval_entry.insert(0, "1000")

        # Buttons
        self.start_button = tk.Button(root, text="Start", command=self.start_reading)
        self.start_button.pack(pady=5)

        self.stop_button = tk.Button(root, text="Stop", command=self.stop_reading, state=tk.DISABLED)
        self.stop_button.pack()

        self.send_button = tk.Button(root, text="Send Data Once", command=self.send_data_once, state=tk.DISABLED)
        self.send_button.pack(pady=5)

        self.loop_var = tk.IntVar()
        self.loop_check = tk.Checkbutton(root, text="Loop Send", variable=self.loop_var, command=self.toggle_loop, state=tk.DISABLED)
        self.loop_check.pack()

    def get_serial_ports(self):
        ports = serial.tools.list_ports.comports()
        return [port.device for port in ports]

    def start_reading(self):
        port = self.port_combo.get()
        try:
            baud = int(self.baud_combo.get())
        except ValueError:
            messagebox.showerror("Invalid Baud Rate", "Please select a valid baud rate.")
            return

        if not port:
            messagebox.showerror("No Port Selected", "Please select a serial port.")
            return

        try:
            self.ser = serial.Serial(port, baud, timeout=1)
        except serial.SerialException as e:
            messagebox.showerror("Serial Error", f"Could not open serial port:\n{e}")
            return

        self.running = True
        self.pass_count = 0
        self.fail_count = 0
        self.error_count = 0
        self.update_labels()

        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.send_button.config(state=tk.NORMAL)
        self.loop_check.config(state=tk.NORMAL)

        self.text_area.insert(tk.END, f"Connected to {port} at {baud} baud\n")
        self.text_area.see(tk.END)

        self.serial_thread = threading.Thread(target=self.read_from_usb, daemon=True)
        self.serial_thread.start()

    def stop_reading(self):
        self.running = False
        self.loop_mode = False

        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.send_button.config(state=tk.DISABLED)
        self.loop_check.config(state=tk.DISABLED)
        self.loop_var.set(0)

        if self.ser and self.ser.is_open:
            self.ser.close()

        self.text_area.insert(tk.END, "Stopped reading.\n")
        self.text_area.see(tk.END)

    def read_from_usb(self):
        while self.running and self.ser and self.ser.is_open:
            try:
                response = self.ser.read(6)
                if not response:
                    continue
                if len(response) < 3:
                    continue

                data_bytes = response[:-2]
                crc_bytes = response[-2:]

                received_crc = int.from_bytes(crc_bytes, byteorder='big')
                calculated_crc = calculate_crc(data_bytes)

                data_str = data_bytes.hex().upper()
                crc_str = f"{received_crc:04X}"

                if calculated_crc == received_crc:
                    self.pass_count += 1
                    status = "PASS"
                else:
                    self.fail_count += 1
                    status = "FAIL"

                self.update_labels()
                self.text_area.insert(tk.END, f"[{status}] Data: {data_str}, CRC: {crc_str}\n")
                self.text_area.see(tk.END)

            except Exception as e:
                self.text_area.insert(tk.END, f"Error: {e}\n")
                self.text_area.see(tk.END)

    def send_data_once(self):
        if not (self.ser and self.ser.is_open):
            self.text_area.insert(tk.END, "Serial port not open.\n")
            self.text_area.see(tk.END)
            return

        hex_data = self.data_entry.get().strip()
        if len(hex_data) == 0:
            self.text_area.insert(tk.END, "Enter data to send.\n")
            self.text_area.see(tk.END)
            return

        try:
            data_bytes = bytes.fromhex(hex_data)
        except ValueError:
            self.text_area.insert(tk.END, "Invalid hex data entered.\n")
            self.text_area.see(tk.END)
            return

        crc = calculate_crc(data_bytes)
        crc_bytes = crc.to_bytes(2, byteorder='big')
        packet = data_bytes + crc_bytes

        try:
            self.ser.write(packet)
            self.text_area.insert(tk.END, f"Sent: {packet.hex().upper()}\n")
            self.text_area.see(tk.END)
        except Exception as e:
            self.text_area.insert(tk.END, f"Error sending data: {e}\n")
            self.text_area.see(tk.END)

        start_time = time.time()
        response = b''
        while time.time() - start_time < 1:
            if self.ser.in_waiting > 0:
                response += self.ser.read(self.ser.in_waiting)
                if len(response) >= 3:
                    break
            time.sleep(0.01)

        if len(response) < 3:
            self.error_count += 1
            self.update_labels()
            self.text_area.insert(tk.END, "No response or incomplete response received.\n")
            self.text_area.see(tk.END)
            return

        data_bytes = response[:-2]
        crc_bytes = response[-2:]
        received_crc = int.from_bytes(crc_bytes, byteorder='big')
        calculated_crc = calculate_crc(data_bytes)

        data_str = data_bytes.hex().upper()
        crc_str = f"{received_crc:04X}"

        if calculated_crc == received_crc:
            self.pass_count += 1
            status = "PASS"
        else:
            self.fail_count += 1
            status = "FAIL"

        self.update_labels()
        self.text_area.insert(tk.END, f"Response [{status}]: Data: {data_str}, CRC: {crc_str}\n")
        self.text_area.see(tk.END)

    def toggle_loop(self):
        if self.loop_var.get() == 1:
            self.loop_mode = True
            self.loop_thread = threading.Thread(target=self.loop_send_data, daemon=True)
            self.loop_thread.start()
            self.text_area.insert(tk.END, "Loop send mode started.\n")
        else:
            self.loop_mode = False
            self.text_area.insert(tk.END, "Loop send mode stopped.\n")
        self.text_area.see(tk.END)

    def loop_send_data(self):
        while self.loop_mode and self.running and self.ser and self.ser.is_open:
            self.send_data_once()
            try:
                interval_ms = float(self.interval_entry.get())
                if interval_ms < 10:
                    interval_ms = 10  # minimum 10 ms
            except ValueError:
                interval_ms = 1000
            time.sleep(interval_ms / 1000.0)

    def update_labels(self):
        self.pass_label.config(text=f"Pass: {self.pass_count}")
        self.fail_label.config(text=f"Fail: {self.fail_count}")
        self.error_label.config(text=f"No Response Errors: {self.error_count}")

if __name__ == "__main__":
    root = tk.Tk()
    app = USBCRCGUI(root)
    root.mainloop()

