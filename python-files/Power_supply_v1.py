import sys
import time
import serial
import tkinter as tk
from tkinter import ttk, messagebox
import serial.tools.list_ports

#python -m auto_py_to_exe

class ka3305pInstrument:
    channels = [1, 2]

    def __init__(self, psu_com):
        try:
            self.psu_com = serial.Serial(
                port=psu_com,
                baudrate=9600,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                bytesize=serial.EIGHTBITS,
                timeout=1
            )
            self.psu_com.isOpen()
            self.isConnected = True
        except:
            print("COM port failure:", sys.exc_info())
            self.psu_com = None
            self.isConnected = False

    def close(self):
        if self.psu_com:
            self.psu_com.close()

    def serWriteAndRecieve(self, data, delay=0.05):
        self.psu_com.write(data.encode())
        time.sleep(delay)
        out = ''
        while self.psu_com.inWaiting() > 0:
            out += self.psu_com.read(1).decode("latin-1")
        return out if out else None

    def setVolt(self, channel, voltage):
        self.serWriteAndRecieve(f"VSET{channel}:{voltage:.2f}")

    def setAmp(self, channel, amp):
        self.serWriteAndRecieve(f"ISET{channel}:{amp:.3f}")

    def setOut(self, state):
        cmd = "OUT1" if state else "OUT0"
        self.serWriteAndRecieve(cmd)

    def getIdn(self):
        return self.serWriteAndRecieve("*IDN?", 0.3)

    def readVolt(self, channel):
        return self.serWriteAndRecieve(f"VOUT{channel}?")

    def readAmp(self, channel):
        return self.serWriteAndRecieve(f"IOUT{channel}?")


class PowerSupplyGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("KA3305P Power Supply Control")
        self.root.configure(bg="#2e2e2e")

        style = ttk.Style(self.root)
        style.theme_use("clam")
        style.configure("TFrame", background="#2e2e2e")
        style.configure("TLabel", background="#2e2e2e", foreground="white")
        style.configure("TButton", background="#3e3e3e", foreground="white")
        style.configure("TLabelframe", background="#2e2e2e", foreground="white")
        style.configure("TLabelframe.Label", background="#2e2e2e", foreground="white")

        self.psu = None
        self.voltage_vars = {}
        self.current_vars = {}
        self.voltage_read_vars = {}
        self.current_read_vars = {}

        self.create_widgets()

    def create_widgets(self):
        self.port_frame = ttk.Frame(self.root, padding=10)
        self.port_frame.grid(row=0, column=0, columnspan=2, sticky='ew')

        ttk.Label(self.port_frame, text="Select COM Port:").grid(row=0, column=0, sticky='w')
        self.port_var = tk.StringVar()
        self.port_combo = ttk.Combobox(self.port_frame, textvariable=self.port_var, values=self.get_ports(), width=10)
        self.port_combo.grid(row=0, column=1, padx=5)

        connect_btn = ttk.Button(self.port_frame, text="Connect", command=self.connect_psu)
        connect_btn.grid(row=0, column=2, padx=5)

        self.channel_frames = []
        for i in range(2):
            ch = i + 1
            ch_frame = ttk.LabelFrame(self.root, text=f"Channel {ch}", padding=10)
            ch_frame.grid(row=1, column=i, padx=10, pady=10)
            self.channel_frames.append(ch_frame)

            ttk.Label(ch_frame, text="Voltage (V):").grid(row=0, column=0, sticky='w')
            voltage = tk.DoubleVar(value=0.0)
            ttk.Entry(ch_frame, textvariable=voltage, width=10).grid(row=0, column=1)
            self.voltage_vars[ch] = voltage

            ttk.Label(ch_frame, text="Current (A):").grid(row=1, column=0, sticky='w')
            current = tk.DoubleVar(value=0.0)
            ttk.Entry(ch_frame, textvariable=current, width=10).grid(row=1, column=1)
            self.current_vars[ch] = current

            ttk.Label(ch_frame, text="Measured Voltage (V):").grid(row=2, column=0, sticky='w')
            voltage_read = tk.StringVar(value="--")
            ttk.Label(ch_frame, textvariable=voltage_read).grid(row=2, column=1, sticky='w')
            self.voltage_read_vars[ch] = voltage_read

            ttk.Label(ch_frame, text="Measured Current (A):").grid(row=3, column=0, sticky='w')
            current_read = tk.StringVar(value="--")
            ttk.Label(ch_frame, textvariable=current_read).grid(row=3, column=1, sticky='w')
            self.current_read_vars[ch] = current_read

            set_btn = ttk.Button(ch_frame, text="Set", command=lambda c=ch: self.set_values(c))
            set_btn.grid(row=4, column=0, columnspan=2, pady=5)

        self.out_btn = ttk.Button(self.root, text="Output ON", command=self.toggle_output)
        self.out_btn.grid(row=2, column=0, columnspan=2, pady=10)
        self.output_on = False

    def get_ports(self):
        return [port.device for port in serial.tools.list_ports.comports()]

    def connect_psu(self):
        port = self.port_var.get()
        if not port:
            messagebox.showerror("Error", "Please select a COM port.")
            return
        self.psu = ka3305pInstrument(port)
        if self.psu.isConnected:
            messagebox.showinfo("Connected", f"Connected to {port}")
            self.update_readings()
        else:
            messagebox.showerror("Connection Failed", f"Could not connect to {port}.")

    def set_values(self, channel):
        if not self.psu:
            messagebox.showwarning("Not Connected", "Power supply not connected.")
            return
        voltage = self.voltage_vars[channel].get()
        current = self.current_vars[channel].get()
        try:
            self.psu.setVolt(channel, voltage)
            self.psu.setAmp(channel, current)
            messagebox.showinfo("Success", f"Ch {channel} set to {voltage} V, {current} A")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def toggle_output(self):
        if not self.psu:
            messagebox.showwarning("Not Connected", "Power supply not connected.")
            return
        self.output_on = not self.output_on
        self.psu.setOut(self.output_on)
        self.out_btn.config(text="Output OFF" if self.output_on else "Output ON")

    def update_readings(self):
        if self.psu:
            for ch in [1, 2]:
                try:
                    v = self.psu.readVolt(ch)
                    a = self.psu.readAmp(ch)
                    self.voltage_read_vars[ch].set(v.strip() if v else "--")
                    self.current_read_vars[ch].set(a.strip() if a else "--")
                except:
                    self.voltage_read_vars[ch].set("--")
                    self.current_read_vars[ch].set("--")
        self.root.after(1000, self.update_readings)


if __name__ == "__main__":
    root = tk.Tk()
    app = PowerSupplyGUI(root)
    root.mainloop()
