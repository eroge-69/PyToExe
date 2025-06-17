import serial
import serial.tools.list_ports
import tkinter as tk
from tkinter import ttk, messagebox

color_commands = [
    "red", "blue", "yellow", "green", "white",
    "black", "magenta", "cyan", "pink", "gray", "teal"
]
fx_commands = [
    "strobe_fast", "strobe_slow", "strobe_random", "strobe_off"
]

def scan_serial_ports():
    ports = serial.tools.list_ports.comports()
    matching_ports = [p.device for p in ports if "AmosGlow ESP32 BLE Color Advertiser" in p.description]
    if not matching_ports:
        matching_ports = [p.device for p in ports]
    return matching_ports

class SerialControlApp:
    def __init__(self, root):
        self.root = root
        self.root.title("AmosGlow Serial Control")
        self.root.attributes('-fullscreen', True)  # Fullscreen mode

        self.serial_conn = None

        # Main frame
        main_frame = ttk.Frame(root, padding=20)
        main_frame.pack(expand=True, fill=tk.BOTH)

        # Serial Port Selector
        port_frame = ttk.Frame(main_frame)
        port_frame.pack(pady=10, fill=tk.X)

        ttk.Label(port_frame, text="Serial Port:", font=("Segoe UI", 14)).pack(side=tk.LEFT)
        self.port_var = tk.StringVar()
        self.port_combo = ttk.Combobox(port_frame, textvariable=self.port_var, font=("Segoe UI", 14), width=35)
        self.port_combo.pack(side=tk.LEFT, padx=10)

        refresh_btn = ttk.Button(port_frame, text="🔄 Refresh", command=self.refresh_ports)
        refresh_btn.pack(side=tk.LEFT, padx=5)

        connect_btn = ttk.Button(port_frame, text="✅ Connect", command=self.connect_serial)
        connect_btn.pack(side=tk.LEFT, padx=5)

        self.refresh_ports()

        # Color Buttons
        color_frame = ttk.LabelFrame(main_frame, text="Color Commands", padding=10)
        color_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        self.add_buttons(color_frame, color_commands)

        # FX Buttons
        fx_frame = ttk.LabelFrame(main_frame, text="FX Commands", padding=10)
        fx_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        self.add_buttons(fx_frame, fx_commands)

        # Log
        self.log = tk.Text(main_frame, height=6, state='disabled', bg="black", fg="lime", font=("Consolas", 12))
        self.log.pack(fill=tk.BOTH, padx=10, pady=10)

        # Signature at bottom
        sig_frame = ttk.Frame(root)
        sig_frame.pack(side=tk.BOTTOM, fill=tk.X)
        sig_label = tk.Label(sig_frame, text="ene zafer mad  !", font=("Segoe UI", 10, "bold"), fg="gray25")
        sig_label.pack(pady=5)

        # Bind ESC to exit fullscreen
        self.root.bind("<Escape>", lambda e: root.destroy())

    def refresh_ports(self):
        ports = scan_serial_ports()
        self.port_combo['values'] = ports
        if ports:
            self.port_var.set(ports[0])
        else:
            self.port_var.set("")

    def connect_serial(self):
        try:
            if self.serial_conn and self.serial_conn.is_open:
                self.serial_conn.close()
            self.serial_conn = serial.Serial(self.port_var.get(), 115200, timeout=1)
            self.log_message(f"Connected to {self.port_var.get()}")
        except Exception as e:
            messagebox.showerror("Connection Error", str(e))

    def send_command(self, cmd):
        if not self.serial_conn or not self.serial_conn.is_open:
            messagebox.showwarning("Not Connected", "Please connect to a serial port first.")
            return
        try:
            self.serial_conn.write((cmd + "\n").encode())
            self.log_message(f"Sent: {cmd}")
        except Exception as e:
            messagebox.showerror("Send Error", str(e))

    def add_buttons(self, frame, commands):
        for idx, cmd in enumerate(commands):
            btn = tk.Button(frame, text=cmd, width=18, height=3, font=("Segoe UI", 16, "bold"),
                            command=lambda c=cmd: self.send_command(c))
            btn.grid(row=idx // 4, column=idx % 4, padx=10, pady=10, sticky="nsew")

        # Make buttons expand equally
        for i in range((len(commands) + 3) // 4):
            frame.rowconfigure(i, weight=1)
        for j in range(4):
            frame.columnconfigure(j, weight=1)

    def log_message(self, msg):
        self.log.config(state='normal')
        self.log.insert(tk.END, msg + "\n")
        self.log.config(state='disabled')
        self.log.see(tk.END)

if __name__ == "__main__":
    root = tk.Tk()
    app = SerialControlApp(root)
    root.mainloop()
