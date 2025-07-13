import time
import threading
import tkinter as tk
from tkinter import ttk, messagebox

class DucatiELM327:
    def __init__(self, port, baudrate=38400, timeout=1):
        self.ser = serial.Serial(port, baudrate=baudrate, timeout=timeout)
        time.sleep(2)  # wait for ELM327 to initialize
        self.initialize_elm327()

    def initialize_elm327(self):
        self.send_command("ATZ")   # Reset ELM327
        time.sleep(1)
        self.send_command("ATE0")  # Echo off
        self.send_command("ATL0")  # Linefeeds off
        self.send_command("ATST 10") # Set timeout
        self.send_command("ATSP 0")  # Automatic protocol
        time.sleep(0.1)

    def send_command(self, cmd):
        self.ser.write((cmd + "\r").encode())
        return self.read_response()

    def read_response(self):
        lines = []
        while True:
            line = self.ser.readline().decode(errors='ignore').strip()
            if line == '' or line == '>' or line is None:
                break
            lines.append(line)
        return lines

    def read_mileage(self):
        response = self.send_command("22F180")
        if response and response[0].startswith("62 F1 80"):
            bytes_str = response[0].split()[3:]
            try:
                mileage = int(''.join(bytes_str), 16)
                return mileage
            except ValueError:
                return None
        return None

    def read_bbs_mileage(self):
        response = self.send_command("22F181")
        if response and response[0].startswith("62 F1 81"):
            bytes_str = response[0].split()[3:]
            try:
                mileage = int(''.join(bytes_str), 16)
                return mileage
            except ValueError:
                return None
        return None

    def close(self):
        self.ser.close()


class MileageSyncApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Ducati Mileage Sync Checker")
        self.geometry("400x250")
        self.resizable(False, False)

        self.elm = None

        self.create_widgets()

    def create_widgets(self):
        # COM port entry
        ttk.Label(self, text="ELM327 COM Port:").pack(pady=(20, 5))
        self.port_var = tk.StringVar(value="COM3")
        self.port_entry = ttk.Entry(self, textvariable=self.port_var, width=15)
        self.port_entry.pack()

        # Connect button
        self.connect_btn = ttk.Button(self, text="Check Mileage Sync", command=self.on_check)
        self.connect_btn.pack(pady=15)

        # Results
        self.result_frame = ttk.Frame(self)
        self.result_frame.pack(pady=10)

        ttk.Label(self.result_frame, text="Dash Mileage:").grid(row=0, column=0, sticky="e", padx=5)
        self.dash_mileage_var = tk.StringVar(value="N/A")
        ttk.Label(self.result_frame, textvariable=self.dash_mileage_var).grid(row=0, column=1, sticky="w", padx=5)

        ttk.Label(self.result_frame, text="BBS Mileage:").grid(row=1, column=0, sticky="e", padx=5)
        self.bbs_mileage_var = tk.StringVar(value="N/A")
        ttk.Label(self.result_frame, textvariable=self.bbs_mileage_var).grid(row=1, column=1, sticky="w", padx=5)

        ttk.Label(self.result_frame, text="Sync Status:").grid(row=2, column=0, sticky="e", padx=5)
        self.sync_status_var = tk.StringVar(value="Unknown")
        ttk.Label(self.result_frame, textvariable=self.sync_status_var).grid(row=2, column=1, sticky="w", padx=5)

    def on_check(self):
        port = self.port_var.get()
        if not port:
            messagebox.showerror("Error", "Please enter a COM port.")
            return
        # Disable button to prevent multiple clicks
        self.connect_btn.config(state="disabled")
        self.sync_status_var.set("Checking...")
        self.dash_mileage_var.set("N/A")
        self.bbs_mileage_var.set("N/A")

        # Run in separate thread to avoid freezing GUI
        threading.Thread(target=self.check_sync, args=(port,), daemon=True).start()

    def check_sync(self, port):
        try:
            self.elm = DucatiELM327(port)
            dash_mileage = self.elm.read_mileage()
            bbs_mileage = self.elm.read_bbs_mileage()

            # Update UI in main thread
            self.after(0, self.update_results, dash_mileage, bbs_mileage)

        except serial.SerialException as e:
            self.after(0, self.show_error, f"Serial error: {e}")
        except Exception as ex:
            self.after(0, self.show_error, f"Error: {ex}")
        finally:
            if self.elm:
                self.elm.close()
            self.after(0, lambda: self.connect_btn.config(state="normal"))

    def update_results(self, dash_mileage, bbs_mileage):
        self.dash_mileage_var.set(f"{dash_mileage} km" if dash_mileage is not None else "Read Failed")
        self.bbs_mileage_var.set(f"{bbs_mileage} km" if bbs_mileage is not None else "Read Failed")

        if dash_mileage is None or bbs_mileage is None:
            self.sync_status_var.set("Could not read all mileages.")
        elif dash_mileage == bbs_mileage:
            self.sync_status_var.set("Mileage is in sync.")
        else:
            self.sync_status_var.set("Mileage mismatch detected!")

    def show_error(self, message):
        messagebox.showerror("Error", message)
        self.sync_status_var.set("Error")


if __name__ == "__main__":
    app = MileageSyncApp()
    app.mainloop()
