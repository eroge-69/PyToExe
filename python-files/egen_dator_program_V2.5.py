import tkinter as tk
from tkinter import ttk, messagebox
from tkintermapview import TkinterMapView
import requests
import math
import json
import os

# Dynamiskt laddad serveradress
def get_server_addr():
    try:
        with open("client_settings.json") as f:
            settings = json.load(f)
            return settings.get("server_address", "http://localhost") + ":" + settings.get("server_port", "8081")
    except:
        return "http://localhost:8081"

SERVER_ADDR = get_server_addr()
DEFAULT_LINE_LENGTH_KM = 20.0

def fetch_settings():
    try:
        r = requests.get(SERVER_ADDR + "/api/settings", timeout=1)
        r.raise_for_status()
        return r.json()
    except Exception:
        return None

def post_settings(path, payload):
    try:
        r = requests.post(SERVER_ADDR + path, json=payload)
        r.raise_for_status()
        return True
    except Exception as e:
        messagebox.showerror("Fel", f"Fel vid POST till {path}:\n{e}")
        return False

def intersection_from_two_bearings(lat1, lon1, br1, lat2, lon2, br2):
    φ1, λ1, θ1 = map(math.radians, (lat1, lon1, br1))
    φ2, λ2, θ2 = map(math.radians, (lat2, lon2, br2))
    dφ, dλ = φ2 - φ1, λ2 - λ1
    dσ = 2 * math.asin(math.sqrt(math.sin(dφ / 2) ** 2 + math.cos(φ1) * math.cos(φ2) * math.sin(dλ / 2) ** 2))
    if dσ == 0: return None
    α1 = math.acos((math.sin(φ2) - math.sin(φ1) * math.cos(dσ)) / (math.sin(dσ) * math.cos(φ1)))
    α2 = math.acos((math.sin(φ1) - math.sin(φ2) * math.cos(dσ)) / (math.sin(dσ) * math.cos(φ2)))
    if math.sin(dλ) > 0: α1 = 2 * math.pi - α1
    if math.sin(dλ) < 0: α2 = 2 * math.pi - α2
    β1 = (θ1 - α1 + math.pi) % (2 * math.pi) - math.pi
    β2 = (α2 - θ2 + math.pi) % (2 * math.pi) - math.pi
    if math.sin(β1) * math.sin(β2) <= 0: return None
    α3 = math.acos(-math.cos(β1) * math.cos(β2) + math.sin(β1) * math.sin(β2) * math.cos(dσ))
    dσ13 = math.atan2(math.sin(dσ) * math.sin(β1) * math.sin(β2), math.cos(β2) + math.cos(β1) * math.cos(α3))
    φ3 = math.asin(math.sin(φ1) * math.cos(dσ13) + math.cos(φ1) * math.sin(dσ13) * math.cos(θ1))
    dλ13 = math.atan2(math.sin(θ1) * math.sin(dσ13) * math.cos(φ1), math.cos(dσ13) - math.sin(φ1) * math.sin(φ3))
    return math.degrees(φ3), math.degrees(λ1 + dλ13)

class PejlClientApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Pejl Klient med Karta")
        self.root.geometry("1200x800")

        main_frame = ttk.Frame(root)
        main_frame.pack(fill="both", expand=True)

        left_frame = ttk.Frame(main_frame)
        left_frame.pack(side="left", fill="both", expand=True)

        self.map_widget = TkinterMapView(left_frame, corner_radius=0)
        self.map_widget.pack(fill="both", expand=True)
        self.map_widget.set_zoom(7)

        right_frame = ttk.Frame(main_frame, padding=10)
        right_frame.pack(side="right", fill="y")

        self.status_label = ttk.Label(right_frame, text="Anslutning till servern: OK", foreground="green")
        self.status_label.pack(fill="x", pady=(0, 10))
        self.server_addr_label = ttk.Label(right_frame, text=f"Server: {SERVER_ADDR}", font=("Segoe UI", 8))
        self.server_addr_label.pack(fill="x", pady=(0, 10))

        ttk.Button(right_frame, text="Uppdatera karta", command=self.update_map).pack(pady=(20, 10), fill="x")
        ttk.Button(right_frame, text="Frekvensinställningar", command=self.show_freq_window).pack(fill="x")
        ttk.Button(right_frame, text="DF-stationer", command=self.show_df_window).pack(pady=(5, 0), fill="x")
        ttk.Button(right_frame, text="Serveradress", command=self.show_ddns_window).pack(pady=(5, 0), fill="x")

        ttk.Label(right_frame, text="DF-stationer:").pack(anchor="w")
        self.station_listbox = tk.Listbox(right_frame, height=10)
        self.station_listbox.pack(fill="x", pady=(0, 10))
        self.station_listbox.bind("<<ListboxSelect>>", self.on_station_select)

        self.settings = fetch_settings()
        if not self.settings:
            self.settings = {"df_stations": []}
            self.status_label.config(text="Anslutning till servern: MISSLYCKADES", foreground="red")

        self.markers = []
        self.paths = []

        self.update_map()
        self.update_station_list()
        self.live_update()

    def show_freq_window(self):
        dlg = tk.Toplevel(self.root)
        dlg.title("Frekvensinställningar")
        dlg.geometry("330x410")
        dlg.resizable(False, False)

        pcr = self.settings.get("pcr1000", {})
        entries = {}

        def make_dropdown(label, key, values, row, frame):
            ttk.Label(frame, text=label).grid(row=row, column=0, sticky="e", padx=5, pady=2)
            var = tk.StringVar(value=str(pcr.get(key, values[0])))
            cb = ttk.Combobox(frame, textvariable=var, values=values, state="readonly")
            cb.grid(row=row, column=1, sticky="w", padx=5, pady=2)
            entries[key] = var

        def make_slider(label, key, row, from_, to, frame):
            ttk.Label(frame, text=label).grid(row=row, column=0, sticky="e", padx=5, pady=2)
            var = tk.DoubleVar(value=float(pcr.get(key, 50)))
            scale = ttk.Scale(frame, variable=var, from_=from_, to=to, orient="horizontal")
            scale.grid(row=row, column=1, sticky="we", padx=5, pady=2)
            entries[key] = var

        def make_entry(label, key, row, frame):
            ttk.Label(frame, text=label).grid(row=row, column=0, sticky="e", padx=5, pady=2)
            var = tk.StringVar(value=str(pcr.get(key, "")))
            ent = ttk.Entry(frame, textvariable=var)
            ent.grid(row=row, column=1, sticky="w", padx=5, pady=2)
            entries[key] = var

        general_frame = ttk.LabelFrame(dlg, text="Allmänt")
        general_frame.pack(fill="x", padx=10, pady=5)
        make_entry("Frekvens (MHz):", "freq", 0, general_frame)
        make_dropdown("Mode:", "mode", ["AM", "FM", "USB", "LSB", "CW", "WFM", "NFM"], 1, general_frame)
        make_dropdown("Filter:", "filter", ["2.8 kHz", "6 kHz", "15 kHz", "50 kHz", "230 kHz"], 2, general_frame)
        make_dropdown("Step:", "step", ["0.1", "1", "2.5", "5", "9", "10", "12.5", "20", "25", "50", "100"], 3, general_frame)

        audio_frame = ttk.LabelFrame(dlg, text="Ljud")
        audio_frame.pack(fill="x", padx=10, pady=5)
        make_slider("Volym:", "volume", 0, 0, 100, audio_frame)
        make_slider("Squelch:", "squelch", 1, 0, 100, audio_frame)

        extra_frame = ttk.LabelFrame(dlg, text="Övrigt")
        extra_frame.pack(fill="x", padx=10, pady=5)
        make_entry("IF-shift:", "ifshift", 0, extra_frame)
        make_dropdown("CTCSS:", "ctcss", ["Av", "67.0", "69.3", "71.9", "74.4", "77.0", "79.7", "82.5", "85.4", "88.5", "91.5", "94.8", "97.4", "100.0", "103.5", "107.2", "110.9", "114.8", "118.8", "123.0", "127.3", "131.8", "136.5", "141.3", "146.2", "151.4", "156.7", "162.2", "167.9", "173.8", "179.9", "186.2", "192.8", "203.5", "210.7", "218.1", "225.7", "233.6", "241.8", "250.3"], 1, extra_frame)
        make_entry("BFO:", "bfo", 2, extra_frame)
        make_entry("BFO-offset:", "bfo_offset", 3, extra_frame)

        def save():
            for key, var in entries.items():
                value = var.get()
                try:
                    pcr[key] = float(value) if isinstance(var, tk.DoubleVar) else value
                except:
                    pcr[key] = value
            post_settings("/api/pcr1000", pcr)
            dlg.destroy()

        ttk.Button(dlg, text="Spara", command=save).pack(pady=10)

    def update_station_list(self):
        self.station_listbox.delete(0, tk.END)
        for station in self.settings.get("df_stations", []):
            name = station.get("name", f"DF {station.get('id', '?')}")
            self.station_listbox.insert(tk.END, name)

    def on_station_select(self, event):
        idx = self.station_listbox.curselection()
        if not idx:
            return
        station = self.settings.get("df_stations", [])[idx[0]]
        lat, lon = station.get("lat"), station.get("lon")
        if lat is not None and lon is not None:
            self.map_widget.set_position(lat, lon)

    def draw_circle(self, lat, lon, radius_km=0.01, segments=36, color="blue"):
        points = []
        for i in range(segments + 1):
            angle = math.radians(i * (360 / segments))
            dlat = math.cos(angle) * radius_km / 111.0
            dlon = math.sin(angle) * radius_km / (111.0 * math.cos(math.radians(lat)))
            points.append((lat + dlat, lon + dlon))
        self.paths.append(self.map_widget.set_path(points, color=color))

    def update_map(self):
        for m in self.markers:
            m.delete()
        for p in self.paths:
            p.delete()
        self.markers.clear()
        self.paths.clear()

        lines = []
        for station in self.settings.get("df_stations", []):
            lat, lon = station.get("lat"), station.get("lon")
            name = station.get("name", f"DF {station.get('id', '?')}")
            typ = station.get("type", "fixed")
            color = "blue" if typ == "fixed" else "green"
            self.draw_circle(lat, lon, radius_km=0.005, color=color)

            rpt = station.get("last_report")
            if rpt and "bearing" in rpt:
                br = float(rpt["bearing"])
                rad = math.radians(br)
                deg_len = DEFAULT_LINE_LENGTH_KM / 111.0
                lat2 = lat + math.cos(rad) * deg_len
                lon2 = lon + math.sin(rad) * deg_len
                p = self.map_widget.set_path([(lat, lon), (lat2, lon2)])
                self.paths.append(p)
                lines.append((lat, lon, br))

        if len(lines) >= 2:
            pt = intersection_from_two_bearings(*lines[0], *lines[1])
            if pt:
                self.draw_circle(pt[0], pt[1], radius_km=0.005, color="red")

    def live_update(self):
        new_settings = fetch_settings()
        if new_settings:
            self.settings = new_settings
            self.update_map()
            self.status_label.config(text="Anslutning till servern: OK", foreground="green")
        else:
            self.status_label.config(text="Anslutning till servern: MISSLYCKADES", foreground="red")
        self.root.after(1000, self.live_update)

    def show_df_window(self):
        dlg = tk.Toplevel(self.root)
        dlg.title("DF-stationer")
        dlg.geometry("250x190")
        for i, station in enumerate(self.settings.get("df_stations", [])):
            f = ttk.LabelFrame(dlg, text=station.get("name", f"DF {i}"))
            f.pack(fill="x", padx=5, pady=5)
            avg_var = tk.StringVar(value=station.get("average", "1.0"))
            ttk.Label(f, text="Average (s):").grid(row=0, column=0)
            ttk.Entry(f, textvariable=avg_var, width=5).grid(row=0, column=1)
            def save_station(i=i, var=avg_var):
                self.settings["df_stations"][i]["average"] = var.get()
                post_settings("/api/df_stations", self.settings["df_stations"])
                dlg.destroy()
            ttk.Button(f, text="Spara", command=save_station).grid(row=0, column=2, padx=5)

    def show_ddns_window(self):
        dlg = tk.Toplevel(self.root)
        dlg.title("Serveradress-inställning")
        dlg.geometry("300x130")
        settings = self.settings

        server_addr = tk.StringVar(value=settings.get("server_address", "http://localhost"))
        port = tk.StringVar(value=settings.get("server_port", "8081"))

        ttk.Label(dlg, text="Serveradress (inkl. http://):").pack()
        ttk.Entry(dlg, textvariable=server_addr).pack(fill="x", padx=10)

        ttk.Label(dlg, text="Port:").pack()
        ttk.Entry(dlg, textvariable=port).pack(fill="x", padx=10)

        def save():
            settings["server_address"] = server_addr.get().strip()
            settings["server_port"] = port.get().strip()
            with open("client_settings.json", "w") as f:
                json.dump(settings, f, indent=2)
            global SERVER_ADDR
            SERVER_ADDR = settings["server_address"] + ":" + settings["server_port"]
            self.settings = fetch_settings()
            self.update_map()
            self.status_label.config(text="Serveradress uppdaterad", foreground="green")

        ttk.Button(dlg, text="Spara", command=save).pack(pady=10)

if __name__ == "__main__":
    root = tk.Tk()
    app = PejlClientApp(root)
    root.mainloop()
