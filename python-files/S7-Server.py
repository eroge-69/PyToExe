import tkinter as tk
from tkinter import filedialog, messagebox
import snap7
from snap7.util import get_int, set_int
import pandas as pd

class PLCExcelSyncApp:
    def __init__(self, master):
        self.master = master
        master.title("🌐 PLC ↔ Excel Auto Sync Tool")
        master.geometry("520x400")
        master.configure(bg="#e3f2fd")

        self.plc = None
        self.filename = None
        self.running = False

        self.style_label("PLC IP Address:").pack(pady=(10, 0))
        self.ip_entry = self.style_entry("192.168.0.1")
        self.ip_entry.pack()

        self.connect_button = self.style_button("🔌 Connect PLC", self.connect_plc)
        self.connect_button.pack(pady=5)

        self.status_label = tk.Label(master, text="Status: Disconnected", fg="red", bg="#e3f2fd", font=("Arial", 10, "bold"))
        self.status_label.pack()

        self.style_label("Excel File:").pack(pady=(10, 0))
        file_frame = tk.Frame(master, bg="#e3f2fd")
        file_frame.pack()
        self.file_entry = self.style_entry()
        self.file_entry.pack(in_=file_frame, side=tk.LEFT, padx=5)
        self.browse_button = self.style_button("📂 Browse", self.browse_file, small=True)
        self.browse_button.pack(in_=file_frame, side=tk.LEFT)

        self.last_value_label = tk.Label(master, text="📊 Current Value: -", bg="#e3f2fd", fg="#333", font=("Arial", 11, "bold"))
        self.last_value_label.pack(pady=15)

        self.start_button = self.style_button("▶️ Start Auto Sync", self.start_auto_sync)
        self.start_button.pack(pady=5)
        self.stop_button = self.style_button("⏹ Stop Auto Sync", self.stop_auto_sync)
        self.stop_button.pack(pady=5)
        self.stop_button.config(state=tk.DISABLED)

    def style_label(self, text):
        return tk.Label(self.master, text=text, bg="#e3f2fd", fg="#0d47a1", font=("Arial", 11, "bold"))

    def style_entry(self, default=""):
        entry = tk.Entry(self.master, font=("Arial", 10), width=40)
        if default:
            entry.insert(0, default)
        return entry

    def style_button(self, text, command, small=False):
        return tk.Button(self.master, text=text, command=command,
                         bg="#64b5f6", fg="white", font=("Arial", 10 if small else 11, "bold"),
                         padx=10, pady=5)

    def browse_file(self):
        filename = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx *.xls")])
        if filename:
            self.file_entry.delete(0, tk.END)
            self.file_entry.insert(0, filename)
            self.filename = filename

    def connect_plc(self):
        ip = self.ip_entry.get()
        try:
            self.plc = snap7.client.Client()
            self.plc.connect(ip, 0, 1)
            if self.plc.get_connected():
                self.status_label.config(text=f"Connected to {ip}", fg="green")
                self.start_button.config(state=tk.NORMAL)
            else:
                self.status_label.config(text="Connection Failed", fg="red")
        except Exception as e:
            messagebox.showerror("Connection Error", str(e))
            self.status_label.config(text="Disconnected", fg="red")

    def auto_sync(self):
        if not self.running or not self.plc or not self.plc.get_connected() or not self.filename:
            return

        try:
            # PLC Value Read
            data = self.plc.db_read(1, 0, 2)
            plc_value = get_int(data, 0)

            # Excel Value Read
            df = pd.read_excel(self.filename)
            excel_value = int(df.iloc[-1, 0])

            # Compare and Sync
            if excel_value != plc_value:
                # Write Excel value to PLC
                set_int(data, 0, excel_value)
                self.plc.db_write(1, 0, data)
                self.last_value_label.config(text=f"Excel → PLC: {excel_value}")
            elif plc_value != df.iloc[-1, 0]:
                # Write PLC value to Excel
                df.iloc[-1, 0] = plc_value
                df.to_excel(self.filename, index=False)
                self.last_value_label.config(text=f"PLC → Excel: {plc_value}")
            else:
                self.last_value_label.config(text=f"No Change: {plc_value}")

        except Exception as e:
            self.last_value_label.config(text=f"Error: {e}", fg="red")

        self.master.after(1000, self.auto_sync)

    def start_auto_sync(self):
        if not self.filename:
            messagebox.showwarning("Excel File", "Please select an Excel file.")
            return
        self.running = True
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.auto_sync()

    def stop_auto_sync(self):
        self.running = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)

if __name__ == "__main__":
    root = tk.Tk()
    app = PLCExcelSyncApp(root)
    root.mainloop()
