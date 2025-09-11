import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import math
import subprocess
import re
import threading

# Цветовая палитра - оттенки серого и белого
POINT_COLORS = ['#FFFFFF', '#C0C0C0', '#A0A0A0', '#808080', '#606060', '#404040']

class Radar(tk.Canvas):
    def __init__(self, master, info_frame, **kwargs):
        super().__init__(master, **kwargs)
        self.info_frame = info_frame
        self.networks = []

        self.bind('<Configure>', self.on_resize)
        self.angle = 0
        self.beam = None
        self.after(70, self.animate)  # увеличили паузу для замедления
        self.start_scan_thread()

    def on_resize(self, event):
        self.width = event.width
        self.height = event.height
        self.center = (self.width // 2, self.height // 2)
        self.radius = min(self.width, self.height) * 0.4
        self.redraw()

    def redraw(self):
        self.delete("all")
        self.create_oval(
            self.center[0] - self.radius, self.center[1] - self.radius,
            self.center[0] + self.radius, self.center[1] + self.radius,
            outline='#DDDDDD', width=2, tags="circle"
        )
        self.beam = self.create_line(
            self.center[0], self.center[1],
            self.center[0], self.center[1],
            fill='#FFFFFF', width=3, dash=(4, 2), tags="beam"
        )
        self.draw_networks()

    def start_scan_thread(self):
        threading.Thread(target=self.update_networks, daemon=True).start()

    def update_networks(self):
        while True:
            networks = scan_wifi_windows()
            if networks:
                self.networks = networks
                self.after(0, self.redraw)
                self.after(0, self.update_network_info)
            threading.Event().wait(8)

    def animate(self):
        if not hasattr(self, 'center'):
            self.angle = (self.angle + 5) % 360  # более плавное движение
            self.after(70, self.animate)  # увеличено время таймера
            return

        x = self.center[0] + self.radius * math.cos(math.radians(self.angle))
        y = self.center[1] + self.radius * math.sin(math.radians(self.angle))
        self.coords(self.beam, self.center[0], self.center[1], x, y)
        self.angle = (self.angle + 5) % 360
        self.after(70, self.animate)

    def draw_networks(self):
        self.delete("point")
        self.delete("label")
        if not self.networks or not hasattr(self, 'center'):
            return
        signals = [net['signal_level'] for net in self.networks if net['signal_level'] is not None]
        if not signals:
            return
        min_signal = min(signals)
        max_signal = max(signals)
        range_signal = max_signal - min_signal if max_signal != min_signal else 1
        count = len(self.networks)

        for i, net in enumerate(self.networks):
            signal_level = net['signal_level'] if net['signal_level'] is not None else min_signal
            normalized = (signal_level - min_signal) / range_signal
            dist = self.radius * (1 - normalized)

            angle_deg = i * (360 / count)
            nx = self.center[0] + dist * math.cos(math.radians(angle_deg))
            ny = self.center[1] + dist * math.sin(math.radians(angle_deg))
            color = POINT_COLORS[i % len(POINT_COLORS)]
            self.create_oval(nx - 6, ny - 6, nx + 6, ny + 6, fill=color, outline='', tags="point")
            font_size = max(9, int(self.radius * 0.07))
            self.create_text(nx, ny - 14, text=net['ssid'], fill='#E0E0E0',
                             font=("Segoe UI", font_size), tags="label", anchor='s')

    def update_network_info(self):
        for widget in self.info_frame.winfo_children():
            widget.destroy()

        max_networks = 15
        for i, net in enumerate(self.networks[:max_networks]):
            info_text = (
                f"SSID: {net.get('ssid', 'N/A')}\n"
                f"BSSID: {net.get('bssid', 'N/A')}\n"
                f"MAC: {net.get('mac', 'N/A')}\n"
                f"Clients: {net.get('clients', 'N/A')}\n"
                f"Signal: {net.get('signal_level', 'N/A')} dBm"
            )
            lbl = tk.Label(self.info_frame, text=info_text, fg='#FFFFFF', bg='#121212',
                           justify='left', anchor='w', font=("Segoe UI", 10))
            lbl.pack(fill='x', padx=8, pady=4)


def scan_wifi_windows():
    try:
        # cp866 - кодировка консоли Windows по-умолчанию в русской Windows
        scan_output = subprocess.check_output(
            ['netsh', 'wlan', 'show', 'networks', 'mode=bssid'],
            stderr=subprocess.STDOUT, text=True, encoding='cp866'
        )
    except Exception as e:
        print("Error scanning Wi-Fi:", e)
        return []

    networks = []
    blocks = scan_output.split("\n\n")
    for block in blocks:
        ssid_match = re.search(r'SSID\s+\d+\s+:\s(.+)', block)
        if not ssid_match:
            continue
        ssid = ssid_match.group(1).strip()
        bssid_matches = re.findall(r'BSSID\s+\d+\s+:\s([0-9a-fA-F:-]+)', block)
        signal_matches = re.findall(r'Signal\s+:\s(\d+)%', block)

        for bssid, signal_str in zip(bssid_matches, signal_matches):
            signal_percent = int(signal_str)
            # Приблизительный перевод % сигнала в dBm:
            signal_level = (signal_percent / 2) - 100
            networks.append({
                'ssid': ssid,
                'signal_level': signal_level,
                'bssid': bssid,
                'mac': bssid,
                'clients': 'N/A'
            })

    return networks


def main():
    root = tk.Tk()
    root.title("N R")
    root.configure(bg='#121212')

    style = ttk.Style()
    style.theme_use('clam')

    style.configure('TButton',
                    font=('Segoe UI', 11, 'bold'),
                    background='#1E1E1E',
                    foreground='#FFFFFF',
                    borderwidth=0,
                    padding=6)
    style.map('TButton',
              foreground=[('active', '#CCCCCC')],
              background=[('active', '#333333')])

    toolbar = ttk.Frame(root, padding=6)
    toolbar.pack(side='top', fill='x')

    btn_refresh = ttk.Button(toolbar, text="Relog")
    btn_refresh.pack(side='left', padx=10)
    btn_show_info = ttk.Button(toolbar, text="WiFi Log")
    btn_show_info.pack(side='left', padx=10)
    btn_about = ttk.Button(toolbar, text="Info")
    btn_about.pack(side='left', padx=10)

    main_frame = ttk.Frame(root)
    main_frame.pack(fill='both', expand=True, padx=12, pady=12)

    style.configure('TFrame', background='#121212')
    style.configure('TLabel', background='#121212', foreground='#FFFFFF')

    info_frame = tk.Frame(main_frame, bg='#121212', width=270)
    info_frame.pack(side='right', fill='y')
    info_frame.pack_propagate(False)

    radar = Radar(main_frame, info_frame=info_frame, bg='#000000', width=600, height=600)
    radar.pack(side='left', fill='both', expand=True)

    def toggle_info():
        if info_frame.winfo_ismapped():
            info_frame.pack_forget()
            btn_show_info.config(text="Show Info Wifi")
        else:
            info_frame.pack(side='right', fill='y')
            btn_show_info.config(text="Close Info Wifi")

    def refresh_scan():
        networks = scan_wifi_windows()
        if networks:
            radar.networks = networks
            radar.redraw()
            radar.update_network_info()

    btn_show_info.config(command=toggle_info)
    btn_refresh.config(command=lambda: threading.Thread(target=refresh_scan, daemon=True).start())
    btn_about.config(command=lambda: messagebox.showinfo("About Program", "NetworkRadar\nVersion 1.0\nDev : inf"))

    root.minsize(350, 200)
    root.mainloop()


if __name__ == '__main__':
    main()
