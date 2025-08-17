import tkinter as tk
from tkinter import ttk, messagebox
import serial
import serial.tools.list_ports
import threading

class SerialMonitor:
    def __init__(self, root):
        self.root = root
        self.root.title("Arduino Serial Monitor (Python) by aditya")
        self.root.geometry("900x600")

        self.ser = None
        self.running = False

        # --- UI Components ---
        tk.Label(root, text="COM Port:", font=("Arial", 12)).grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.port_var = tk.StringVar()
        self.port_cb = ttk.Combobox(root, textvariable=self.port_var, width=20, font=("Arial", 12))
        self.port_cb.grid(row=0, column=1, padx=5, pady=5)
        self.refresh_ports()

        tk.Label(root, text="Baud Rate:", font=("Arial", 12)).grid(row=0, column=2, padx=5, pady=5, sticky="w")
        self.baud_var = tk.StringVar(value="9600")
        self.baud_cb = ttk.Combobox(root, textvariable=self.baud_var, width=15, font=("Arial", 12),
                                    values=["300","1200","2400","4800","9600","14400","19200","38400","57600","115200"])
        self.baud_cb.grid(row=0, column=3, padx=5, pady=5)

        self.connect_btn = tk.Button(root, text="Connect", command=self.toggle_connection,
                                     width=15, font=("Arial", 12), bg="lightgray")
        self.connect_btn.grid(row=0, column=4, padx=10, pady=5)

        self.text_area = tk.Text(root, wrap="word", height=25, width=110,
                                 state="disabled", font=("Consolas", 12), bg="white", fg="black")
        self.text_area.grid(row=1, column=0, columnspan=5, padx=10, pady=10, sticky="nsew")

        scroll = tk.Scrollbar(root, command=self.text_area.yview)
        scroll.grid(row=1, column=5, sticky="ns")
        self.text_area.config(yscrollcommand=scroll.set)

        self.entry = tk.Entry(root, width=80, font=("Consolas", 12))
        self.entry.grid(row=2, column=0, columnspan=4, padx=5, pady=10, sticky="we")
        self.entry.bind("<Return>", self.send_data)  # ENTER sends command

        self.send_btn = tk.Button(root, text="Send", command=self.send_data,
                                  width=12, font=("Arial", 12), bg="lightgray")
        self.send_btn.grid(row=2, column=4, padx=5, pady=10)

        self.clear_btn = tk.Button(root, text="Clear Output", command=self.clear_output,
                                   width=15, font=("Arial", 12), bg="lightgray")
        self.clear_btn.grid(row=3, column=4, padx=5, pady=5)

        root.grid_rowconfigure(1, weight=1)
        root.grid_columnconfigure(0, weight=1)

    def refresh_ports(self):
        ports = [p.device for p in serial.tools.list_ports.comports()]
        self.port_cb["values"] = ports
        if ports:
            self.port_cb.current(0)

    def toggle_connection(self):
        if self.ser and self.ser.is_open:
            self.disconnect()
        else:
            self.connect()

    def connect(self):
        port = self.port_var.get()
        baud = self.baud_var.get()
        if not port:
            messagebox.showerror("Error", "Please select a COM port")
            return
        try:
            self.ser = serial.Serial(port, int(baud), timeout=1)
            self.running = True
            self.connect_btn.config(text="Disconnect", bg="tomato")
            threading.Thread(target=self.read_serial, daemon=True).start()
            self.write_text(f"✅ Connected to {port} at {baud} baud.\n")
        except Exception as e:
            messagebox.showerror("Connection Failed", str(e))

    def disconnect(self):
        if self.ser and self.ser.is_open:
            self.running = False
            self.ser.close()
            self.connect_btn.config(text="Connect", bg="lightgray")
            self.write_text("🔌 Disconnected.\n")

    def read_serial(self):
        while self.running and self.ser.is_open:
            try:
                line = self.ser.readline().decode(errors="ignore").strip()
                if line:
                    self.write_text(f"Arduino>> {line}\n")
            except Exception as e:
                self.write_text(f"⚠ Error: {e}\n")
                break

    def send_data(self, event=None):  # event=None makes it work for button + Enter
        if self.ser and self.ser.is_open:
            msg = self.entry.get()
            if msg:
                self.ser.write((msg + "\n").encode())
                self.write_text(f"You >> {msg}\n")
                self.entry.delete(0, tk.END)

    def clear_output(self):
        self.text_area.config(state="normal")
        self.text_area.delete(1.0, tk.END)
        self.text_area.config(state="disabled")

    def write_text(self, message):
        self.text_area.config(state="normal")
        self.text_area.insert("end", message)
        self.text_area.see("end")
        self.text_area.config(state="disabled")

if __name__ == "__main__":
    root = tk.Tk()
    app = SerialMonitor(root)
    root.mainloop()
