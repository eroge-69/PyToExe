import tkinter as tk
from tkinter import ttk, messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from ping3 import ping
import json
import time
from datetime import datetime, timedelta
import threading

class PingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Ping Monitor")
        self.root.configure(bg="#2b2b2b")
        self.running = False
        self.times = []
        self.pings = []
        self.total_packets = 0
        self.lost_packets = 0
        self.start_datetime = None
        self.host = "www.google.com"
        self.start_time = None
        self.pause_offset = 0

        self.setup_style()
        self.setup_ui()
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def setup_style(self):
        style = ttk.Style(self.root)
        style.theme_use("clam")
        style.configure(".", background="#2b2b2b", foreground="#ffffff", fieldbackground="#3c3f41")
        style.configure("TButton", background="#3c3f41", foreground="#ffffff")
        style.configure("TLabel", background="#2b2b2b", foreground="#ffffff")
        style.configure("TEntry", fieldbackground="#3c3f41", foreground="#ffffff")

    def setup_ui(self):
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Rechter Bereich: Buttons + Status + Statistik
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=10, pady=10)

        ttk.Label(control_frame, text="Ziel-Host:").pack(pady=5)
        self.host_entry = ttk.Entry(control_frame, width=25)
        self.host_entry.insert(0, self.host)
        self.host_entry.pack(pady=5)

        self.start_button = ttk.Button(control_frame, text="Start", command=self.start_ping)
        self.start_button.pack(pady=5, fill=tk.X)

        self.stop_button = ttk.Button(control_frame, text="Stop", command=self.stop_ping)
        self.stop_button.pack(pady=5, fill=tk.X)

        self.save_button = ttk.Button(control_frame, text="Save as JSON", command=self.save_json)
        self.save_button.pack(pady=5, fill=tk.X)

        self.status_label = ttk.Label(control_frame, text="Status: Bereit", wraplength=200)
        self.status_label.pack(pady=10)

        # Statistik direkt unter Status
        self.stats_frame = ttk.Frame(control_frame)
        self.stats_frame.pack(pady=10, anchor="w")

        self.start_time_label = ttk.Label(self.stats_frame, text="Startzeit: –")
        self.start_time_label.pack(anchor="w")

        self.elapsed_label = ttk.Label(self.stats_frame, text="Laufzeit: –")
        self.elapsed_label.pack(anchor="w")

        self.avg_label = ttk.Label(self.stats_frame, text="⏱ Durchschnitt: –")
        self.avg_label.pack(anchor="w")

        self.min_label = ttk.Label(self.stats_frame, text="📉 Minimum: –")
        self.min_label.pack(anchor="w")

        self.max_label = ttk.Label(self.stats_frame, text="📈 Maximum: –")
        self.max_label.pack(anchor="w")

        self.loss_label = ttk.Label(self.stats_frame, text="❌ Paketverlust: –")
        self.loss_label.pack(anchor="w")

        # Linker Bereich: Plot
        display_frame = ttk.Frame(main_frame)
        display_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        fig, self.ax = plt.subplots(facecolor="#2b2b2b")
        self.line, = self.ax.plot([], [], label="Ping (ms)", color="#00ffcc")
        self.ax.set_xlabel("Zeit (s)")
        self.ax.set_ylabel("Antwortzeit (ms)")
        self.ax.set_title("Live Ping", color="#ffffff")
        self.ax.legend()
        self.ax.grid(True)
        self.ax.set_facecolor("#3c3f41")
        self.ax.tick_params(colors="#ffffff")
        self.ax.xaxis.label.set_color("#ffffff")
        self.ax.yaxis.label.set_color("#ffffff")

        self.canvas = FigureCanvasTkAgg(fig, master=display_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def start_ping(self):
        if not self.running:
            self.running = True
            if self.start_datetime is None:
                self.start_datetime = datetime.now()
                self.start_time = time.time()
                self.host = self.host_entry.get().strip() or "www.google.com"
                self.status_label.config(text=f"Status: Ping zu {self.host} gestartet")
            else:
                self.pause_offset += time.time() - self.pause_start
                self.status_label.config(text=f"Status: Fortgesetzt")

            threading.Thread(target=self.ping_loop, daemon=True).start()

    def stop_ping(self):
        if self.running:
            self.running = False
            self.pause_start = time.time()
            self.status_label.config(text="Status: Pausiert")

    def ping_loop(self):
        while self.running:
            response = ping(self.host, unit="ms", timeout=2)
            current_time = time.time() - self.start_time - self.pause_offset
            self.total_packets += 1

            if response is None:
                self.lost_packets += 1
                self.pings.append(0)
            else:
                self.pings.append(response)

            self.times.append(current_time)

            if len(self.times) > 3:  # Vermeide Flackern beim Start
                self.line.set_xdata(self.times)
                self.line.set_ydata(self.pings)
                self.ax.relim()
                self.ax.autoscale_view()
                self.canvas.draw_idle()

            self.root.after(0, self.update_ui_stats, current_time)
            time.sleep(1)

    def update_ui_stats(self, current_time):
        valid_pings = [p for p in self.pings if p > 0]
        elapsed = timedelta(seconds=int(current_time))

        self.start_time_label.config(text=f"Startzeit: {self.start_datetime.strftime('%Y-%m-%d %H:%M:%S')}")
        self.elapsed_label.config(text=f"Laufzeit: {str(elapsed)}")

        if valid_pings:
            avg = sum(valid_pings) / len(valid_pings)
            min_ping = min(valid_pings)
            max_ping = max(valid_pings)
            loss = (self.lost_packets / self.total_packets) * 100

            self.avg_label.config(text=f"⏱ Durchschnitt: {avg:.1f} ms")
            self.min_label.config(text=f"📉 Minimum: {min_ping:.1f} ms")
            self.max_label.config(text=f"📈 Maximum: {max_ping:.1f} ms")
            self.loss_label.config(text=f"❌ Paketverlust: {self.lost_packets} ({loss:.1f}%)")

    def save_json(self):
        if not self.times:
            messagebox.showwarning("Keine Daten", "Es wurden keine Ping-Daten gesammelt.")
            return

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"ping_log_{timestamp}.json"

        data = {
            "host": self.host,
            "start_time": self.start_datetime.strftime("%Y-%m-%d %H:%M:%S"),
            "end_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "total_packets": self.total_packets,
            "lost_packets": self.lost_packets,
            "packet_loss_percent": round((self.lost_packets / self.total_packets) * 100, 2),
            "pings": [
                {
                    "timestamp": (self.start_datetime + timedelta(seconds=t)).strftime("%Y-%m-%d %H:%M:%S"),
                    "ping_ms": p
                }
                for t, p in zip(self.times, self.pings)
            ]
        }

        with open(filename, "w") as f:
            json.dump(data, f, indent=4)

        messagebox.showinfo("Gespeichert", f"✅ JSON gespeichert als {filename}")

    def on_close(self):
        self.running = False
        self.root.quit()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = PingApp(root)
    root.mainloop()
