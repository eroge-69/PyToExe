# -*- coding: utf-8 -*-
"""
Serial Data Sender GUI
----------------------
A simple graphical user interface to continuously send specific hexadecimal
data sequences over a selected serial port at a 96000 baud rate.

The application sends the following sequences in a continuous loop:
1. AB0001 to AB03E7
2. AD0001 to AD03E7
3. DC0001 to DC270F
4. AE0001 to AE270F

Requires the 'pyserial' library. Install it using:
pip install pyserial
"""
import tkinter as tk
from tkinter import ttk, messagebox
import serial
import serial.tools.list_ports
import threading
import time

class SerialSenderApp:
    """The main application class for the Serial Sender GUI."""
    def __init__(self, root_window):
        self.root = root_window
        self.root.title("Continuous Serial Sender")
        self.root.geometry("450x250")
        self.root.resizable(False, False)

        # --- Member Variables ---
        self.serial_connection = None
        self.is_sending = False
        self.sending_thread = None

        # --- Style Configuration ---
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TButton", padding=6, relief="flat", background="#007bff", foreground="white")
        style.map("TButton",
            foreground=[('pressed', 'white'), ('active', 'white')],
            background=[('pressed', '!disabled', '#0056b3'), ('active', '#0069d9')]
        )
        style.configure("TFrame", background="#f0f0f0")
        style.configure("TLabel", background="#f0f0f0")
        style.configure("TCombobox", fieldbackground="white")


        # --- GUI Setup ---
        self.main_frame = ttk.Frame(self.root, padding="15")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Port Selection
        port_frame = ttk.Frame(self.main_frame)
        port_frame.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(port_frame, text="COM Port:", font=("Helvetica", 10)).pack(side=tk.LEFT, padx=(0, 10))
        self.port_selector = ttk.Combobox(port_frame, state="readonly", width=20)
        self.port_selector.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.refresh_ports()

        refresh_button = ttk.Button(port_frame, text="Refresh", command=self.refresh_ports, width=10)
        refresh_button.pack(side=tk.LEFT, padx=(10, 0))

        # Status Display
        self.status_label_var = tk.StringVar(value="Status: Idle")
        status_label = ttk.Label(self.main_frame, textvariable=self.status_label_var, font=("Helvetica", 10, "italic"), anchor="center")
        status_label.pack(fill=tk.X, pady=10)

        # Control Buttons
        button_frame = ttk.Frame(self.main_frame)
        button_frame.pack(fill=tk.X, pady=10)
        button_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(1, weight=1)

        self.start_button = ttk.Button(button_frame, text="Start Sending", command=self.start_sending)
        self.start_button.grid(row=0, column=0, sticky="ew", padx=(0, 5))

        self.stop_button = ttk.Button(button_frame, text="Stop Sending", command=self.stop_sending, state=tk.DISABLED)
        self.stop_button.grid(row=0, column=1, sticky="ew", padx=(5, 0))

        # --- Window Close Handler ---
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def refresh_ports(self):
        """Finds and lists available serial ports in the combobox."""
        ports = [port.device for port in serial.tools.list_ports.comports()]
        self.port_selector['values'] = ports
        if ports:
            self.port_selector.set(ports[0])
        else:
            self.port_selector.set('')

    def start_sending(self):
        """Starts the data sending process in a separate thread."""
        selected_port = self.port_selector.get()
        if not selected_port:
            messagebox.showerror("Error", "No COM port selected. Please select a port and try again.")
            return

        try:
            # Configure and open the serial port
            self.serial_connection = serial.Serial(selected_port, 96000, timeout=1)
            self.status_label_var.set(f"Connected to {selected_port}. Starting...")
        except serial.SerialException as e:
            messagebox.showerror("Connection Error", f"Failed to open port {selected_port}.\nError: {e}")
            return

        self.is_sending = True
        # Use a daemon thread so it exits when the main program exits
        self.sending_thread = threading.Thread(target=self.send_loop, daemon=True)
        self.sending_thread.start()

        # Update GUI state
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.port_selector.config(state=tk.DISABLED)

    def stop_sending(self):
        """Stops the data sending process."""
        self.is_sending = False
        if self.serial_connection and self.serial_connection.is_open:
            self.serial_connection.close()
            
        self.status_label_var.set("Status: Stopped by user.")
        
        # Update GUI state
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.port_selector.config(state=tk.NORMAL)

    def send_loop(self):
        """The main loop that generates and sends data."""
        # Define the ranges for data generation
        # Hex values are inclusive
        ranges = [
            ("AB", 1, 0x03E7, 4),  # AB0001 to AB03E7 (1 to 999)
            ("AD", 1, 0x03E7, 4),  # AD0001 to AD03E7 (1 to 999)
            ("DC", 1, 0x270F, 4),  # DC0001 to DC270F (1 to 9999)
            ("AE", 1, 0x270F, 4),  # AE0001 to AE270F (1 to 9999)
        ]
        
        # This outer loop makes the sending process continuous
        while self.is_sending:
            for prefix, start, end, padding in ranges:
                for i in range(start, end + 1):
                    if not self.is_sending:
                        return # Exit if stop was requested
                    
                    # Format the number as a zero-padded hex string
                    hex_val = f'{i:0{padding}X}'
                    data_string = f'{prefix}{hex_val}\n' # Add newline as a terminator
                    
                    try:
                        self.serial_connection.write(data_string.encode('ascii'))
                        self.root.after(0, self.update_status, f"Sent: {data_string.strip()}")
                        # To send 2 times per second, we wait for 0.5 seconds between sends.
                        time.sleep(0.5)
                    except (serial.SerialException, TypeError, AttributeError) as e:
                        # Handle cases where the port is closed or disconnected
                        self.root.after(0, self.handle_send_error, str(e))
                        return # Stop the sending loop on error
                        
    def update_status(self, message):
        """Updates the status label from the sending thread safely."""
        self.status_label_var.set(message)

    def handle_send_error(self, error_message):
        """Handles serial errors that occur during sending."""
        if self.is_sending: # Only show error if we weren't trying to stop
            messagebox.showerror("Serial Error", f"An error occurred: {error_message}\nSending has been stopped.")
        self.stop_sending()


    def on_closing(self):
        """Handles the window close event."""
        if self.is_sending:
            self.stop_sending()
        self.root.destroy()


if __name__ == "__main__":
    app_root = tk.Tk()
    app = SerialSenderApp(app_root)
    app_root.mainloop()