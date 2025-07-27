import tkinter as tk
from tkinter import ttk, scrolledtext
from PIL import Image, ImageTk
import serial
import serial.tools.list_ports
from threading import Thread
import time

class SerialApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Serial GUI")
        self.root.attributes('-fullscreen', True)

        self.serial_port = None
        self.running = False

        # Watermark background
        bg_canvas = tk.Canvas(root, highlightthickness=0)
        bg_canvas.pack(fill=tk.BOTH, expand=True)

        try:
            logo_img = Image.open("C:/logo.png").resize((150, 150), resample=Image.LANCZOS)
            self.logo_tk = ImageTk.PhotoImage(logo_img)
            bg_canvas.create_image(
                root.winfo_screenwidth() - 170,
                root.winfo_screenheight() - 170,
                image=self.logo_tk,
                anchor=tk.NW
            )
        except Exception as e:
            print(f"⚠️ Error loading logo: {e}")

        content_frame = tk.Frame(bg_canvas)
        bg_canvas.create_window(0, 0, anchor="nw", window=content_frame,
                                width=root.winfo_screenwidth())

        # Top bar
        top_frame = tk.Frame(content_frame)
        top_frame.pack(pady=10)

        self.combobox = ttk.Combobox(top_frame,
                                     values=self.list_ports(),
                                     width=15)
        self.combobox.pack(side=tk.LEFT, padx=10)

        self.connect_btn = ttk.Button(top_frame,
                                      text="Connect",
                                      command=self.connect_serial)
        self.connect_btn.pack(side=tk.LEFT, padx=5)

        self.disconnect_btn = ttk.Button(top_frame,
                                         text="Disconnect",
                                         command=self.disconnect_serial)
        self.disconnect_btn.pack(side=tk.LEFT, padx=5)

        self.refresh_btn = ttk.Button(top_frame,
                                      text="Refresh",
                                      command=self.refresh_ports)
        self.refresh_btn.pack(side=tk.LEFT)

        # Payload buttons panel
        button_frame = tk.Frame(content_frame)
        button_frame.pack(pady=10)

        labels = [f"Credit {i*10}" for i in range(1, 51)]     # Credit 10 → Credit 500
        payloads = [f"{i*10:04d}" for i in range(1, 51)]       # 0010 → 0500

        for idx, (label, val) in enumerate(zip(labels, payloads)):
            ttk.Button(button_frame,
                       text=label,
                       command=lambda v=val: self.send_value(v)).grid(row=idx//10, column=idx%10, padx=5, pady=5)

        # 🆕 Manual Credit Sender
        manual_frame = tk.Frame(content_frame)
        manual_frame.pack(pady=10)

        self.manual_entry = ttk.Entry(manual_frame, width=20)
        self.manual_entry.pack(side=tk.LEFT, padx=5)

        ttk.Button(manual_frame, text="Send Manual Credit", command=self.send_manual_credit).pack(side=tk.LEFT)

        # Terminal output
        terminal_frame = tk.Frame(content_frame, bg="#1a1a1a")
        terminal_frame.pack(pady=20)

        self.terminal = scrolledtext.ScrolledText(
            terminal_frame,
            width=80,
            height=20,
            font=("Consolas", 12),
            bg="#101010",
            fg="#00FF00",
            insertbackground="#00FF00",
            wrap=tk.WORD
        )
        self.terminal.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        Thread(target=self.read_from_serial, daemon=True).start()

        self.root.protocol("WM_DELETE_WINDOW", self.close)
        self.root.bind("<Escape>", lambda e: self.close())  # Optional: quick exit

    def list_ports(self):
        return [port.device for port in serial.tools.list_ports.comports()]

    def refresh_ports(self):
        ports = self.list_ports()
        self.combobox['values'] = ports
        self.terminal.insert(tk.END, f"Ports refreshed: {', '.join(ports)}\n")
        self.terminal.see(tk.END)

    def connect_serial(self):
        try:
            port = self.combobox.get()
            self.serial_port = serial.Serial(port, baudrate=9600, timeout=0.1)
            self.running = True
            self.terminal.insert(tk.END, f"Connected to {port}\n")
        except Exception as e:
            self.terminal.insert(tk.END, f"Connection error: {e}\n")

    def disconnect_serial(self):
        if self.serial_port and self.serial_port.is_open:
            self.serial_port.close()
            self.terminal.insert(tk.END, "Disconnected from serial port.\n")
        else:
            self.terminal.insert(tk.END, "Serial already disconnected.\n")
        self.terminal.see(tk.END)

    def send_value(self, value):
        if self.serial_port and self.serial_port.is_open:
            self.serial_port.write((value + "\r\n").encode())
            self.terminal.insert(tk.END, value + "\n")
            self.terminal.see(tk.END)
        else:
            self.terminal.insert(tk.END, "Serial not connected.\n")

    def send_manual_credit(self):
        value = self.manual_entry.get().strip()
        if value.isdigit() and 0 <= int(value) <= 9999:
            self.send_value(f"{int(value):04d}")
        else:
            self.terminal.insert(tk.END, "Invalid manual credit. Enter a number from 0 to 9999.\n")
            self.terminal.see(tk.END)

    def read_from_serial(self):
        while True:
            if self.running and self.serial_port and self.serial_port.is_open:
                try:
                    line = self.serial_port.readline().decode('utf-8', errors='ignore').strip()
                    if line:
                        self.terminal.insert(tk.END, line + "\n")
                        self.terminal.see(tk.END)
                except serial.SerialException:
                    break
            time.sleep(0.05)

    def close(self):
        self.running = False
        if self.serial_port and self.serial_port.is_open:
            self.serial_port.close()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = SerialApp(root)
    root.mainloop()