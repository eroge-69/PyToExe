import tkinter as tk
from tkinter import messagebox
import threading
import time
import sqlite3
from scapy.all import ARP, Ether, srp
import socket

# --- Глобальные переменные настроек ---
SCAN_INTERVAL = 60  # секунд (по умолчанию)
TARGET_SUBNET = "192.168.1.0/24"  # по умолчанию

WHITELIST_DB = "whitelist.db"

# --- Работа с базой данных ---
def init_db():
    conn = sqlite3.connect(WHITELIST_DB)
    conn.execute("CREATE TABLE IF NOT EXISTS whitelist (mac TEXT PRIMARY KEY, name TEXT)")
    conn.commit()
    conn.close()

def get_whitelist():
    conn = sqlite3.connect(WHITELIST_DB)
    cursor = conn.cursor()
    cursor.execute("SELECT mac FROM whitelist")
    result = [row[0].upper() for row in cursor.fetchall()]
    conn.close()
    return result

def add_to_whitelist(mac, name=""):
    conn = sqlite3.connect(WHITELIST_DB)
    conn.execute("INSERT OR IGNORE INTO whitelist(mac, name) VALUES(?, ?)", (mac.upper(), name))
    conn.commit()
    conn.close()

# --- Сканирование сети ---
def scan_network(subnet):
    devices = []
    arp = ARP(pdst=subnet)
    ether = Ether(dst="ff:ff:ff:ff:ff:ff")
    packet = ether/arp

    try:
        result = srp(packet, timeout=2, verbose=False)[0]
    except PermissionError:
        messagebox.showerror("Ошибка", "Программу нужно запускать от администратора.")
        return []

    for sent, received in result:
        devices.append({
            "ip": received.psrc,
            "mac": received.hwsrc.upper()
        })

    return devices

# --- Интерфейс ---
class NetworkMonitorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Сетевой монитор")
        self.running = True

        self.text = tk.Text(root, width=70, height=20)
        self.text.pack(pady=10)

        btn_frame = tk.Frame(root)
        btn_frame.pack(pady=5)

        tk.Button(btn_frame, text="Добавить MAC в белый список", command=self.add_mac_gui).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Сканировать сейчас", command=self.manual_scan).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Настройки", command=self.open_settings).pack(side=tk.LEFT, padx=5)

        self.log("Запуск мониторинга сети...")
        threading.Thread(target=self.auto_scan_loop, daemon=True).start()

    def log(self, msg):
        timestamp = time.strftime('%H:%M:%S')
        self.text.insert(tk.END, f"[{timestamp}] {msg}\n")
        self.text.see(tk.END)

    def alert_unknown(self, device):
        msg = f"‼ Обнаружено неизвестное устройство: IP={device['ip']} MAC={device['mac']}"
        self.log(msg)
        messagebox.showwarning("Найдено неизвестное устройство", msg)

    def scan_and_compare(self):
        whitelist = get_whitelist()
        active_devices = scan_network(TARGET_SUBNET)

        if not active_devices:
            self.log("Устройства не найдены (возможно, ошибка или сеть пуста)")
            return

        self.log("Обнаружены устройства:")
        for dev in active_devices:
            mac = dev["mac"]
            ip = dev["ip"]
            self.log(f" - {ip} ({mac})")
            if mac not in whitelist:
                self.alert_unknown(dev)

    def auto_scan_loop(self):
        while self.running:
            self.scan_and_compare()
            time.sleep(SCAN_INTERVAL)

    def manual_scan(self):
        self.scan_and_compare()

    def add_mac_gui(self):
        win = tk.Toplevel(self.root)
        win.title("Добавить MAC")
        tk.Label(win, text="MAC:").grid(row=0, column=0, padx=5, pady=5)
        mac_entry = tk.Entry(win, width=20)
        mac_entry.grid(row=0, column=1)

        tk.Label(win, text="Имя устройства (необязательно):").grid(row=1, column=0, padx=5, pady=5)
        name_entry = tk.Entry(win, width=20)
        name_entry.grid(row=1, column=1)

        def save():
            mac = mac_entry.get().strip().upper()
            name = name_entry.get().strip()
            if mac:
                add_to_whitelist(mac, name)
                self.log(f"Добавлено в белый список: {mac} ({name})")
                win.destroy()
            else:
                messagebox.showerror("Ошибка", "Введите MAC-адрес")

        tk.Button(win, text="Сохранить", command=save).grid(row=2, column=0, columnspan=2, pady=10)

    def open_settings(self):
        win = tk.Toplevel(self.root)
        win.title("Настройки")

        tk.Label(win, text="Интервал сканирования (сек):").grid(row=0, column=0, padx=5, pady=5)
        interval_entry = tk.Entry(win, width=10)
        interval_entry.insert(0, str(SCAN_INTERVAL))
        interval_entry.grid(row=0, column=1)

        tk.Label(win, text="Целевая подсеть:").grid(row=1, column=0, padx=5, pady=5)
        subnet_entry = tk.Entry(win, width=20)
        subnet_entry.insert(0, TARGET_SUBNET)
        subnet_entry.grid(row=1, column=1)

        def save_settings():
            global SCAN_INTERVAL, TARGET_SUBNET
            try:
                interval = int(interval_entry.get())
                subnet = subnet_entry.get().strip()
                if interval < 10:
                    raise ValueError
                SCAN_INTERVAL = interval
                TARGET_SUBNET = subnet
                self.log(f"Настройки обновлены: интервал={interval} сек, подсеть={subnet}")
                win.destroy()
            except ValueError:
                messagebox.showerror("Ошибка", "Введите корректный интервал (целое число ≥ 10)")

        tk.Button(win, text="Сохранить", command=save_settings).grid(row=2, column=0, columnspan=2, pady=10)

# --- Запуск приложения ---
if __name__ == "__main__":
    init_db()
    root = tk.Tk()
    app = NetworkMonitorApp(root)
    root.mainloop()
