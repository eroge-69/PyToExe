import asyncio
import threading
import tkinter as tk
from tkinter import simpledialog, messagebox
from bleak import BleakScanner
import math

def rssi_to_distance(rssi, tx_power=-59):
    if rssi == "N/A" or rssi is None:
        return None
    try:
        ratio = (tx_power - rssi) / (10 * 2)
        distance = 10 ** ratio
        return round(distance, 2)
    except Exception:
        return None

class BLEScannerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("BLE Scanner")

        self.devices = {}
        self.custom_names = {}
        self.monitoring = None

        self.scan_interval = 1.0  # секунда по умолчанию

        self.listbox = tk.Listbox(root, width=80, height=20)
        self.listbox.pack(padx=10, pady=10)
        self.listbox.bind('<<ListboxSelect>>', self.on_select)

        control_frame = tk.Frame(root)
        control_frame.pack(padx=10, pady=5)

        tk.Label(control_frame, text="Интервал сканирования (сек):").grid(row=0, column=0, sticky="w")
        self.interval_entry = tk.Entry(control_frame, width=5)
        self.interval_entry.grid(row=0, column=1, sticky="w")
        self.interval_entry.insert(0, str(self.scan_interval))

        self.set_interval_btn = tk.Button(control_frame, text="Установить", command=self.set_interval)
        self.set_interval_btn.grid(row=0, column=2, padx=5)

        btn_frame = tk.Frame(root)
        btn_frame.pack(padx=10, pady=5)

        self.edit_name_btn = tk.Button(btn_frame, text="Редактировать имя", command=self.edit_name, state=tk.DISABLED)
        self.edit_name_btn.grid(row=0, column=0, padx=5)

        self.start_monitor_btn = tk.Button(btn_frame, text="Начать слежение", command=self.start_monitor, state=tk.DISABLED)
        self.start_monitor_btn.grid(row=0, column=1, padx=5)

        self.stop_monitor_btn = tk.Button(btn_frame, text="Остановить слежение", command=self.stop_monitor, state=tk.DISABLED)
        self.stop_monitor_btn.grid(row=0, column=2, padx=5)

        self.status_label = tk.Label(root, text="Выберите устройство для слежения")
        self.status_label.pack(padx=10, pady=5)

        self.loop = asyncio.new_event_loop()
        t = threading.Thread(target=self.run_loop, daemon=True)
        t.start()

        self.update_ui()

    def set_interval(self):
        val = self.interval_entry.get()
        try:
            new_interval = float(val)
            if new_interval <= 0:
                raise ValueError
            self.scan_interval = new_interval
            messagebox.showinfo("Интервал", f"Интервал сканирования установлен: {self.scan_interval} сек")
        except ValueError:
            messagebox.showerror("Ошибка", "Введите корректное положительное число для интервала.")

    def run_loop(self):
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(self.scan_loop())

    async def scan_loop(self):
        while True:
            try:
                devices = await BleakScanner.discover(timeout=self.scan_interval)
            except Exception as e:
                # Если вдруг ошибка с BLE, выводим и ждем повтор
                print(f"Ошибка сканирования: {e}")
                await asyncio.sleep(self.scan_interval)
                continue

            for dev in devices:
                rssi = getattr(dev, "rssi", None)
                if rssi is None and hasattr(dev, "details"):
                    adv = getattr(dev.details, "adv", None)
                    if adv is not None and hasattr(adv, "raw_signal_strength_in_dbm"):
                        rssi = adv.raw_signal_strength_in_dbm
                distance = rssi_to_distance(rssi)

                self.devices[dev.address] = {
                    "name": dev.name or "Unknown",
                    "rssi": rssi if rssi is not None else "N/A",
                    "distance": distance
                }

                if self.monitoring == dev.address:
                    status = f"Слежение за {self.get_display_name(dev.address)} | RSSI: {rssi} dBm | ~{distance} м"
                    self.root.after(0, lambda s=status: self.status_label.config(text=s))

    def update_ui(self):
        self.listbox.delete(0, tk.END)
        for addr, info in self.devices.items():
            name = self.get_display_name(addr)
            dist = f"{info['distance']} м" if info['distance'] is not None else "N/A"
            line = f"{addr} | {name} | RSSI: {info['rssi']} dBm | Расстояние: {dist}"
            self.listbox.insert(tk.END, line)

        self.root.after(1000, self.update_ui)

    def get_display_name(self, addr):
        return self.custom_names.get(addr, self.devices.get(addr, {}).get("name", "Unknown"))

    def on_select(self, event):
        sel = self.listbox.curselection()
        if sel:
            self.edit_name_btn.config(state=tk.NORMAL)
            self.start_monitor_btn.config(state=tk.NORMAL)
        else:
            self.edit_name_btn.config(state=tk.DISABLED)
            self.start_monitor_btn.config(state=tk.DISABLED)

    def edit_name(self):
        sel = self.listbox.curselection()
        if not sel:
            return
        line = self.listbox.get(sel[0])
        addr = line.split(" | ")[0]
        current_name = self.get_display_name(addr)

        new_name = simpledialog.askstring("Редактировать имя", "Введите новое имя устройства:", initialvalue=current_name)
        if new_name:
            self.custom_names[addr] = new_name
            self.update_ui()

    def start_monitor(self):
        sel = self.listbox.curselection()
        if not sel:
            return
        line = self.listbox.get(sel[0])
        addr = line.split(" | ")[0]
        self.monitoring = addr
        self.status_label.config(text=f"Слежение за {self.get_display_name(addr)}")
        self.start_monitor_btn.config(state=tk.DISABLED)
        self.stop_monitor_btn.config(state=tk.NORMAL)

    def stop_monitor(self):
        self.monitoring = None
        self.status_label.config(text="Слежение остановлено")
        self.start_monitor_btn.config(state=tk.DISABLED)
        self.stop_monitor_btn.config(state=tk.DISABLED)

if __name__ == "__main__":
    root = tk.Tk()
    app = BLEScannerApp(root)
    root.mainloop()
