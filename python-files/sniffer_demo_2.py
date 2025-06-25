import pyinstaller
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
from tkinter import ttk
import serial
import serial.tools.list_ports
import subprocess
import threading
import struct
import datetime
import win32pipe
import win32file
import re
import os
import queue

def list_serial_ports():
    """List available serial ports"""
    return [port.device for port in serial.tools.list_ports.comports()]

class SnifferGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Sniffer Dongle Configuration")
        self.root.geometry("900x600")

        # Wireshark Path Selection
        self.wireshark_path_label = tk.Label(root, text="Wireshark Path:")
        self.wireshark_path_label.grid(row=0, column=0, sticky="w", padx=10, pady=5)
        self.wireshark_path_entry = tk.Entry(root, width=50)
        self.wireshark_path_entry.grid(row=0, column=1, columnspan=2, sticky="w", padx=(10,0), pady=5)
        self.browse_button = tk.Button(root, text="Browse", command=self.browse_wireshark, width=10)
        self.browse_button.grid(row=0, column=3, sticky="w", padx=(5,10), pady=5)

        # Button to start Wireshark
        self.start_wireshark_button = tk.Button(root, text="Start", command=self.start_wireshark, width=20)
        self.start_wireshark_button.grid(row=1, column=0, columnspan=4, pady=10)

        # Container frame for port configurations
        container = tk.Frame(root)
        container.grid(row=2, column=0, columnspan=4, pady=10, padx=10)

        self.ports = []
        for i in range(5):
            frame = tk.Frame(container, borderwidth=2, relief="groove", padx=10, pady=10)
            frame.grid(row=0, column=i, padx=10, pady=10)

            sp_label = tk.Label(frame, text=f"Serial Port {i+1}", font=("Helvetica", 10, "bold"))
            sp_label.grid(row=0, column=0, padx=2, pady=(0,5))
            sp_var = tk.StringVar()
            sp_menu = tk.OptionMenu(frame, sp_var, *list_serial_ports())
            sp_menu.config(width=12)
            sp_menu.grid(row=1, column=0, padx=2, pady=5)

            # Channel Entry
            ch_label = tk.Label(frame, text="Channel", font=("Helvetica", 10, "bold"))
            ch_label.grid(row=2, column=0, padx=2, pady=(10,5))
            ch_entry = tk.Entry(frame, width=10)
            ch_entry.grid(row=3, column=0, padx=2, pady=5)

            # PHY Mode Entry
            phy_label = tk.Label(frame, text="PHY Mode", font=("Helvetica", 10, "bold"))
            phy_label.grid(row=4, column=0, padx=2, pady=(10,5))
            phy_entry = tk.Entry(frame, width=10)
            phy_entry.grid(row=5, column=0, padx=2, pady=5)

            # Separate buttons for configuring channel and PHY mode
            configure_channel_button = tk.Button(frame, text="Configure Channel", command=lambda sp_var=sp_var, ch_entry=ch_entry, index=i: self.configure_channel(sp_var, ch_entry, index), width=15)
            configure_channel_button.grid(row=6, column=0, padx=2, pady=5)

            configure_phy_button = tk.Button(frame, text="Configure PHY Mode", command=lambda sp_var=sp_var, phy_entry=phy_entry, index=i: self.configure_phy_mode(sp_var, phy_entry, index), width=15)
            configure_phy_button.grid(row=7, column=0, padx=2, pady=10)

            self.ports.append((sp_var, ch_entry, phy_entry, configure_channel_button, configure_phy_button))

        self.hard_coded_baud = 115200

        # Create tabbed logs using ttk.Notebook
        self.notebook = ttk.Notebook(root)
        self.notebook.grid(row=3, column=0, columnspan=4, padx=10, pady=10)

        self.log_tabs = {}  
        for i in range(5):
            log_frame = ttk.Frame(self.notebook)
            log_text = scrolledtext.ScrolledText(log_frame, width=120, height=10, font=("Courier", 10), wrap=tk.WORD)
            log_text.grid(row=0, column=0, padx=10, pady=10)
            self.notebook.add(log_frame, text=f"Port {i+1}")
            self.log_tabs[i] = log_text

        self.serial_ports = [None] * 5
        self.channel_queues = [queue.Queue() for _ in range(5)]
        self.shared_queue = queue.Queue()  # This is the shared queue across all threads
        self.wireshark_started = False

        # Start writer thread
        self.writer_thread = threading.Thread(target=self.writer_thread_func, daemon=True)
        self.writer_thread.start()

    def browse_wireshark(self):
        path = filedialog.askopenfilename(title="Select Wireshark Executable")
        if path:
            self.wireshark_path_entry.delete(0, tk.END)
            self.wireshark_path_entry.insert(0, path)

    def start_wireshark(self):
        wireshark_path = self.wireshark_path_entry.get()
        if not wireshark_path:
            messagebox.showerror("Error", "Please select the Wireshark executable.")
            return

        # Start Wireshark
        subprocess.Popen([wireshark_path, "-k", "-i", "\\\\.\\pipe\\sniffer_pipe"], creationflags=subprocess.CREATE_NO_WINDOW)
        self.open_named_pipe()
        self.write_pcap_global_header()
        self.wireshark_started = True
        messagebox.showinfo("Success", "Wireshark started. Packet capture in progress.")

    def open_named_pipe(self):
        self.pipe_handle = win32pipe.CreateNamedPipe(
            r"\\.\pipe\sniffer_pipe",
            win32pipe.PIPE_ACCESS_OUTBOUND,
            win32pipe.PIPE_TYPE_BYTE | win32pipe.PIPE_WAIT,
            1, 65536, 65536, 0, None
        )
        win32pipe.ConnectNamedPipe(self.pipe_handle, None)

    def configure_channel(self, sp_var, ch_entry, index):
        port = sp_var.get().strip()
        channel = ch_entry.get().strip()

        if not port:
            messagebox.showerror("Error", f"Please select Serial Port {index+1}.")
            return

        # Open Serial Port if not already open
        if self.serial_ports[index] is None:
            ser = serial.Serial(port, baudrate=115200, timeout=1)
            self.serial_ports[index] = ser
            threading.Thread(target=self.sniffer_thread, args=(ser, index)).start()

        # Send Channel configuration
        ser = self.serial_ports[index]
        ser.write(f"SETCHANNEL {channel}\n".encode())
        messagebox.showinfo("Success", "Channel Set.")

    def configure_phy_mode(self, sp_var, phy_entry, index):
        port = sp_var.get().strip()
        phy_mode = phy_entry.get().strip()

        if not port:
            messagebox.showerror("Error", f"Please select Serial Port {index+1}.")
            return

        # Open Serial Port if not already open
        if self.serial_ports[index] is None:
            ser = serial.Serial(port, baudrate=115200, timeout=1)
            self.serial_ports[index] = ser
            threading.Thread(target=self.sniffer_thread, args=(ser, index)).start()

        # Send PHY Mode configuration
        ser = self.serial_ports[index]
        ser.write(f"SETCONFIGINDEX {phy_mode}\n".encode())
        messagebox.showinfo("Success", "PHY Mode Set.")

    def sniffer_thread(self, ser, index):
        while True:
            data = ser.read_until(b'\r\n')
            if data and self.wireshark_started:
               if not re.search(b'(?i)(SETCHANNEL|SETCONFIGINDEX|^> |^>$)', data):
                    # Put data in the shared queue
                    self.shared_queue.put((data[3:-3], index))
                    self.process_and_log_data(data, index)

    def write_pcap_global_header(self):
        global_header = struct.pack("<IHHiIII", 0xa1b2c3d4, 2, 4, 0, 0, 65535, 195)
        win32file.WriteFile(self.pipe_handle, global_header)

    def write_pcap_packet(self, data):
        timestamp = int(datetime.datetime.now().timestamp())
        microseconds = datetime.datetime.now().microsecond
        packet_header = struct.pack("<IIII", timestamp, microseconds, len(data), len(data))
        win32file.WriteFile(self.pipe_handle, packet_header + data)

    def writer_thread_func(self):
        while True:
            # Get data from the shared queue and write to PCAP
            data, index = self.shared_queue.get()
            if data:
                self.write_pcap_packet(data)

    def process_and_log_data(self, data, index):
        hex_dump = " ".join(f"{byte:02x}" for byte in data)
        byte_list = hex_dump.split()
        hex_dump = hex_dump[5:-5]
        if len(byte_list) < 3:
            return

        try:
            first = int(byte_list[1], 16)
            second = int(byte_list[2], 16)
            combined_value = (first << 8) | second

            mode = (combined_value >> 15) & 0x01
            fcs = (combined_value >> 12) & 0x01
            data_whitening = (combined_value >> 11) & 0x01

            log_message = (
                f"Received Data: {hex_dump[3:]}\n"
                f"Mode: {mode}\n"
                f"FCS: {fcs}\n"
                f"Data Whitening: {data_whitening}\n"
                "---------------------------------------------\n"
            )

            self.log_tabs[index].insert(tk.END, log_message)
            self.log_tabs[index].see(tk.END)
        except Exception as e:
            self.log_tabs[index].insert(tk.END, f"Error processing data: {str(e)}\n")
            self.log_tabs[index].see(tk.END)

if __name__ == "__main__":
    root = tk.Tk()
    app = SnifferGUI(root)
    root.mainloop()
