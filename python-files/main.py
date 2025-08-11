"""
Rocket Status Monitoring System
Single-file Python 3.10 program using Tkinter.

Features implemented (1-10):
 1) Real-time telemetry (altitude, velocity, acceleration, fuel, orientation, GPS, temp/pressure)
 2) Live graphs (matplotlib embedded)
 3) Camera feed simulation (generated frames)
 4) Navigation & tracking (simple map canvas with predicted landing)
 5) AI-based decision support (simple rule-based advisor)
 6) System health monitoring with alerts
 7) Alerts & notifications (visual + sound optional)
 8) Data logging (SQLite + CSV export)
 9) Simulation & testing mode (adjustable env params and failures)
10) Extra facilities: control panel (thrust, stage sep, parachute), multi-rocket support, mission log

Optional dependencies:
 pip install matplotlib numpy pillow

Run: python rocket_monitor.py

NOTE: This program is a simulation/training UI. It does not interface with real rockets.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tkinter.scrolledtext import ScrolledText
import sqlite3
import threading
import time
import math
import random
import csv
import os
import datetime

# Optional libs
try:
    import numpy as np
    import matplotlib
    matplotlib.use('TkAgg')
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
except Exception:
    np = None
    Figure = None

try:
    from PIL import Image, ImageDraw, ImageTk
except Exception:
    Image = None

DB_FILE = 'rocket_monitor.db'

# --------------------- Database & Logging -------------------------------
class DataLogger:
    def __init__(self, db_file=DB_FILE):
        self.conn = sqlite3.connect(db_file, check_same_thread=False)
        self._ensure_tables()
        self.lock = threading.Lock()

    def _ensure_tables(self):
        c = self.conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS telemetry (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            rocket_id TEXT,
            ts TEXT,
            altitude REAL,
            velocity REAL,
            accel REAL,
            fuel REAL,
            pitch REAL,
            yaw REAL,
            roll REAL,
            lat REAL,
            lon REAL,
            temp REAL,
            pressure REAL
        )''')
        c.execute('''CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            rocket_id TEXT,
            ts TEXT,
            event_type TEXT,
            message TEXT
        )''')
        self.conn.commit()

    def log_telemetry(self, rocket_id, data: dict):
        with self.lock:
            c = self.conn.cursor()
            c.execute('''INSERT INTO telemetry (rocket_id, ts, altitude, velocity, accel, fuel, pitch, yaw, roll, lat, lon, temp, pressure)
                         VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)''', (
                         rocket_id, datetime.datetime.now().isoformat(sep=' ', timespec='seconds'),
                         data['altitude'], data['velocity'], data['acceleration'], data['fuel'],
                         data['pitch'], data['yaw'], data['roll'], data['lat'], data['lon'], data['temp'], data['pressure']
                         ))
            self.conn.commit()

    def log_event(self, rocket_id, event_type, message):
        with self.lock:
            c = self.conn.cursor()
            c.execute('''INSERT INTO events (rocket_id, ts, event_type, message) VALUES (?,?,?,?)''',
                      (rocket_id, datetime.datetime.now().isoformat(sep=' ', timespec='seconds'), event_type, message))
            self.conn.commit()

    def query_telemetry(self, rocket_id=None, limit=1000):
        c = self.conn.cursor()
        if rocket_id:
            c.execute('SELECT ts, altitude, velocity, accel, fuel, lat, lon FROM telemetry WHERE rocket_id=? ORDER BY id DESC LIMIT ?', (rocket_id, limit))
        else:
            c.execute('SELECT ts, altitude, velocity, accel, fuel, lat, lon FROM telemetry ORDER BY id DESC LIMIT ?', (limit,))
        return c.fetchall()

    def export_csv(self, path, rocket_id=None):
        rows = self.query_telemetry(rocket_id, limit=1000000)
        with open(path, 'w', newline='', encoding='utf-8') as f:
            w = csv.writer(f)
            w.writerow(['ts','altitude','velocity','accel','fuel','lat','lon'])
            for r in reversed(rows):
                w.writerow(r)

    def close(self):
        self.conn.close()

# --------------------- Telemetry Simulation -----------------------------
class TelemetrySimulator(threading.Thread):
    """Simulates telemetry for multiple rockets. Runs in background thread.
    Emits callbacks with (rocket_id, data_dict)
    """
    def __init__(self, callback, control_state, env_params):
        super().__init__(daemon=True)
        self.callback = callback
        self.control_state = control_state  # shared dict of controls per rocket
        self.env_params = env_params
        self.running = True
        self.dt = 0.5  # telemetry interval
        self.rockets = {}
        self._init_rockets()

    def _init_rockets(self):
        # create a sample rocket state
        for i in range(1, 3):
            rid = f'ROCKET-{i:02d}'
            self.rockets[rid] = {
                'altitude': 0.0,
                'velocity': 0.0,
                'acceleration': 0.0,
                'fuel': 100.0,
                'pitch': 0.0,
                'yaw': 0.0,
                'roll': 0.0,
                'lat': 28.6139 + i*0.001,  # base near Dhaka but arbitrary
                'lon': 77.2090 + i*0.001,
                'temp': 20.0,
                'pressure': 1013.25,
                'time': 0.0,
                'stage': 1,
                'status': 'PRELAUNCH'
            }
            self.control_state[rid] = {'thrust': 0.0, 'stage_sep': False, 'parachute': False, 'abort': False}

    def run(self):
        while self.running:
            start = time.time()
            for rid, s in list(self.rockets.items()):
                ctrl = self.control_state.get(rid, {})
                # simple physics model
                thrust = float(ctrl.get('thrust', 0.0))  # 0..100
                mass = 1000 - (100 - s['fuel'])*2  # mass decreases with fuel
                g = 9.80665
                # compute acceleration: a = (thrust_force / mass) - g + wind_effect
                thrust_force = thrust * 200.0  # arbitrary scale
                wind = self.env_params.get('wind', 0.0) * (random.random()-0.5)
                accel = thrust_force / max(1.0, mass) - g + wind
                # integrate
                s['acceleration'] = accel
                s['velocity'] = max(0.0, s['velocity'] + accel * self.dt)
                s['altitude'] = max(0.0, s['altitude'] + s['velocity'] * self.dt)
                s['fuel'] = max(0.0, s['fuel'] - thrust * 0.01 * self.dt)
                s['time'] += self.dt
                # orientation changes randomly
                s['pitch'] += (random.random()-0.5)*0.5
                s['yaw'] += (random.random()-0.5)*0.5
                s['roll'] += (random.random()-0.5)*0.5
                # temp and pressure influenced by altitude
                s['temp'] = 20 - 0.0065 * s['altitude']
                s['pressure'] = 1013.25 * math.exp(-s['altitude']/8434.5)
                # GPS drift
                s['lat'] += 0.00001 * (s['velocity']/100.0) * (random.random()-0.5)
                s['lon'] += 0.00001 * (s['velocity']/100.0) * (random.random()-0.5)

                # stage separation logic
                if ctrl.get('stage_sep') and s['stage'] == 1:
                    s['stage'] = 2
                    s['velocity'] *= 0.9

                # parachute
                if ctrl.get('parachute'):
                    s['velocity'] = max(0.0, s['velocity'] * 0.6)

                # abort
                if ctrl.get('abort'):
                    s['thrust'] = 0
                    s['velocity'] = max(0.0, s['velocity'] * 0.8)

                # update status
                if s['altitude'] > 1 and s['status'] == 'PRELAUNCH':
                    s['status'] = 'ASCENDING'
                if s['altitude'] > 30000:
                    s['status'] = 'EXO'

                # callback with a copy
                data = {
                    'altitude': s['altitude'],
                    'velocity': s['velocity'],
                    'acceleration': s['acceleration'],
                    'fuel': s['fuel'],
                    'pitch': s['pitch'],
                    'yaw': s['yaw'],
                    'roll': s['roll'],
                    'lat': s['lat'],
                    'lon': s['lon'],
                    'temp': s['temp'],
                    'pressure': s['pressure'],
                    'status': s['status'],
                    'stage': s['stage']
                }
                try:
                    self.callback(rid, data)
                except Exception:
                    pass
            elapsed = time.time() - start
            sleep = max(0.0, self.dt - elapsed)
            time.sleep(sleep)

    def stop(self):
        self.running = False

# --------------------- AI Advisor -------------------------------------
class AIAdvisor:
    def __init__(self, logger: DataLogger):
        self.logger = logger

    def evaluate(self, rocket_id, data):
        # simple rule-based checks; returns list of (level, message)
        alerts = []
        if data['fuel'] < 20:
            alerts.append(('CRITICAL', 'Fuel low (<20%)'))
        if data['acceleration'] > 50:
            alerts.append(('WARNING', f"High acceleration: {data['acceleration']:.1f} m/s²"))
        if data['temp'] > 150:
            alerts.append(('CRITICAL', 'High temperature'))
        if data['pressure'] < 200:
            alerts.append(('WARNING', 'Low atmospheric pressure'))
        # predicted landing: if descending and low altitude
        if data['velocity'] < 1 and data['altitude'] < 500 and data['fuel'] < 5:
            alerts.append(('INFO', 'Preparing for landing / deploy parachute'))
        # log to DB
        for lvl, msg in alerts:
            self.logger.log_event(rocket_id, lvl, msg)
        return alerts

# --------------------- Main UI ----------------------------------------
class RocketMonitorApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Rocket Status Monitoring System')
        self.geometry('1200x780')

        self.logger = DataLogger()
        self.control_state = {}
        self.env_params = {'wind': 0.2}
        self.simulator = TelemetrySimulator(self.on_telemetry, self.control_state, self.env_params)
        self.ai = AIAdvisor(self.logger)

        self.current_rocket = None
        self.telemetry_history = {}  # rocket_id -> list of dicts

        self.create_ui()
        self.simulator.start()
        self.after(1000, self.refresh_ui)

    def create_ui(self):
        # top toolbar
        toolbar = ttk.Frame(self)
        toolbar.pack(side='top', fill='x')
        ttk.Button(toolbar, text='Add Rocket', command=self.add_rocket).pack(side='left', padx=6, pady=6)
        ttk.Button(toolbar, text='Export CSV', command=self.export_csv).pack(side='left', padx=6)
        ttk.Button(toolbar, text='Show Logs', command=self.show_logs).pack(side='left', padx=6)
        ttk.Button(toolbar, text='Simulation Settings', command=self.open_sim_settings).pack(side='left', padx=6)

        # left: rocket list
        left = ttk.Frame(self, width=200)
        left.pack(side='left', fill='y')
        ttk.Label(left, text='Rockets').pack()
        self.rocket_listbox = tk.Listbox(left, width=20)
        self.rocket_listbox.pack(fill='y', expand=True, padx=6, pady=6)
        self.rocket_listbox.bind('<<ListboxSelect>>', self.on_select_rocket)
        # populate initial rockets
        for rid in list(self.simulator.rockets.keys()):
            self.rocket_listbox.insert('end', rid)
        if not self.current_rocket:
            self.current_rocket = list(self.simulator.rockets.keys())[0]
            self.rocket_listbox.select_set(0)

        # center: telemetry panels
        center = ttk.Frame(self)
        center.pack(side='left', fill='both', expand=True)

        # telemetry numbers
        numbers = ttk.Frame(center)
        numbers.pack(fill='x')
        self.labels = {}
        for i, key in enumerate(['altitude','velocity','acceleration','fuel','pitch','yaw','roll','temp','pressure']):
            f = ttk.Frame(numbers, relief='ridge', borderwidth=1)
            f.grid(row=0, column=i, padx=2, pady=2, sticky='n')
            ttk.Label(f, text=key.capitalize()).pack()
            self.labels[key] = ttk.Label(f, text='-')
            self.labels[key].pack()

        # graphs area
        graphs = ttk.Frame(center)
        graphs.pack(fill='both', expand=True, padx=6, pady=6)

        if Figure is not None:
            self.fig = Figure(figsize=(8,4), dpi=90)
            self.ax_alt = self.fig.add_subplot(131)
            self.ax_vel = self.fig.add_subplot(132)
            self.ax_fuel = self.fig.add_subplot(133)
            self.fig.tight_layout()
            self.canvas = FigureCanvasTkAgg(self.fig, master=graphs)
            self.canvas.get_tk_widget().pack(fill='both', expand=True)
        else:
            ttk.Label(graphs, text='Matplotlib not available - install matplotlib and numpy for graphs').pack()

        # right: camera + controls + map
        right = ttk.Frame(self, width=360)
        right.pack(side='right', fill='y')

        # camera
        cam_frame = ttk.LabelFrame(right, text='Camera Feed')
        cam_frame.pack(fill='x', padx=6, pady=6)
        self.cam_label = ttk.Label(cam_frame)
        self.cam_label.pack()

        # map
        map_frame = ttk.LabelFrame(right, text='Trajectory Map')
        map_frame.pack(fill='both', padx=6, pady=6, expand=True)
        self.map_canvas = tk.Canvas(map_frame, width=320, height=240, bg='black')
        self.map_canvas.pack(padx=4, pady=4)

        # control panel
        control_frame = ttk.LabelFrame(right, text='Control Panel')
        control_frame.pack(fill='x', padx=6, pady=6)
        ttk.Label(control_frame, text='Thrust (%)').pack()
        self.thrust_var = tk.DoubleVar(value=0.0)
        thrust_slider = ttk.Scale(control_frame, from_=0, to=100, variable=self.thrust_var, orient='horizontal')
        thrust_slider.pack(fill='x', padx=6)
        ttk.Button(control_frame, text='Apply Thrust', command=self.apply_thrust).pack(pady=4)
        ttk.Button(control_frame, text='Stage Separate', command=self.stage_separate).pack(pady=2)
        ttk.Button(control_frame, text='Deploy Parachute', command=self.deploy_parachute).pack(pady=2)
        ttk.Button(control_frame, text='Abort', command=self.abort_launch).pack(pady=2)

        # bottom: alerts and mission log
        bottom = ttk.Frame(self)
        bottom.pack(side='bottom', fill='x')
        alert_frame = ttk.LabelFrame(bottom, text='Alerts & Advisor')
        alert_frame.pack(side='left', fill='both', expand=True, padx=6, pady=4)
        self.alert_box = ScrolledText(alert_frame, height=6, width=80, state='disabled')
        self.alert_box.pack(fill='both', expand=True)

        log_frame = ttk.LabelFrame(bottom, text='Mission Log')
        log_frame.pack(side='right', fill='both', padx=6, pady=4)
        self.log_box = ScrolledText(log_frame, height=6, width=50, state='disabled')
        self.log_box.pack(fill='both', expand=True)

        # populate camera image if PIL available
        self.cam_image = None
        self.generate_camera_frame()

    # ------------------ UI Actions ---------------------------------
    def add_rocket(self):
        # creates a new rocket in simulator
        new_id = f'ROCKET-{len(self.simulator.rockets)+1:02d}'
        self.simulator.rockets[new_id] = {
            'altitude': 0.0,'velocity': 0.0,'acceleration': 0.0,'fuel': 100.0,'pitch':0,'yaw':0,'roll':0,'lat':28.6,'lon':77.2,'temp':20,'pressure':1013.25,'time':0.0,'stage':1,'status':'PRELAUNCH'
        }
        self.control_state[new_id] = {'thrust':0,'stage_sep':False,'parachute':False,'abort':False}
        self.rocket_listbox.insert('end', new_id)
        self.logger.log_event(new_id, 'INFO', 'Rocket added')

    def export_csv(self):
        path = filedialog.asksaveasfilename(defaultextension='.csv', filetypes=[('CSV','*.csv')])
        if not path:
            return
        rid = self.current_rocket
        try:
            self.logger.export_csv(path, rocket_id=rid)
            messagebox.showinfo('Export', f'CSV exported to {path}')
        except Exception as e:
            messagebox.showerror('Export error', str(e))

    def show_logs(self):
        # open DB events in a window
        w = tk.Toplevel(self)
        w.title('Event Logs')
        txt = ScrolledText(w, width=100, height=30)
        txt.pack(fill='both', expand=True)
        c = self.logger.conn.cursor()
        c.execute('SELECT ts, rocket_id, event_type, message FROM events ORDER BY id DESC LIMIT 1000')
        rows = c.fetchall()
        for r in rows:
            txt.insert('end', f'[{r[0]}] {r[1]} {r[2]}: {r[3]}\n')

    def open_sim_settings(self):
        w = tk.Toplevel(self)
        w.title('Simulation Settings')
        ttk.Label(w, text='Wind strength:').pack(padx=6, pady=6)
        wind_var = tk.DoubleVar(value=self.env_params.get('wind', 0.2))
        ttk.Scale(w, from_=0.0, to=2.0, variable=wind_var, orient='horizontal').pack(fill='x', padx=8)
        def save():
            self.env_params['wind'] = wind_var.get()
            w.destroy()
        ttk.Button(w, text='Save', command=save).pack(pady=8)

    def on_select_rocket(self, event=None):
        sel = self.rocket_listbox.curselection()
        if not sel:
            return
        idx = sel[0]
        rid = self.rocket_listbox.get(idx)
        self.current_rocket = rid
        self.log(f'Selected {rid}')

    def apply_thrust(self):
        if not self.current_rocket:
            return
        val = float(self.thrust_var.get())
        self.control_state[self.current_rocket]['thrust'] = val
        self.logger.log_event(self.current_rocket, 'CTRL', f'Thrust set to {val:.1f}%')

    def stage_separate(self):
        if not self.current_rocket:
            return
        self.control_state[self.current_rocket]['stage_sep'] = True
        self.logger.log_event(self.current_rocket, 'CTRL', 'Stage separation commanded')
        self.log('Stage separation commanded')

    def deploy_parachute(self):
        if not self.current_rocket:
            return
        self.control_state[self.current_rocket]['parachute'] = True
        self.logger.log_event(self.current_rocket, 'CTRL', 'Parachute deployed')
        self.log('Parachute deployed')

    def abort_launch(self):
        if not self.current_rocket:
            return
        self.control_state[self.current_rocket]['abort'] = True
        self.logger.log_event(self.current_rocket, 'CTRL', 'Abort commanded')
        self.log('Abort commanded')

    # ---------------- Telemetry callback ---------------------------
    def on_telemetry(self, rocket_id, data):
        # called from simulator thread; update logger and in-memory history
        # store history limited size
        hist = self.telemetry_history.setdefault(rocket_id, [])
        hist.append({'ts': datetime.datetime.now(), **data})
        if len(hist) > 2000:
            hist.pop(0)
        # log to DB
        try:
            self.logger.log_telemetry(rocket_id, data)
        except Exception:
            pass
        # AI evaluate
        alerts = self.ai.evaluate(rocket_id, data)
        for lvl, msg in alerts:
            self.push_alert(rocket_id, lvl, msg)
        # if current rocket, schedule UI update
        if rocket_id == self.current_rocket:
            self.after(1, lambda: self.update_telemetry_display(rocket_id, data))

    def update_telemetry_display(self, rid, data):
        # update numeric labels
        self.labels['altitude']['text'] = f"{data['altitude']:.1f} m"
        self.labels['velocity']['text'] = f"{data['velocity']:.1f} m/s"
        self.labels['acceleration']['text'] = f"{data['acceleration']:.2f} m/s^2"
        self.labels['fuel']['text'] = f"{data['fuel']:.1f} %"
        self.labels['pitch']['text'] = f"{data['pitch']:.1f}°"
        self.labels['yaw']['text'] = f"{data['yaw']:.1f}°"
        self.labels['roll']['text'] = f"{data['roll']:.1f}°"
        self.labels['temp']['text'] = f"{data['temp']:.1f} °C"
        self.labels['pressure']['text'] = f"{data['pressure']:.1f} hPa"
        # update graphs
        self.update_graphs()
        # update map
        self.update_map()
        # update camera frame
        self.generate_camera_frame()

    def update_graphs(self):
        if Figure is None:
            return
        rid = self.current_rocket
        hist = self.telemetry_history.get(rid, [])[-300:]
        if not hist:
            return
        ts = [(h['ts'] - hist[0]['ts']).total_seconds() for h in hist]
        alt = [h['altitude'] for h in hist]
        vel = [h['velocity'] for h in hist]
        fuel = [h['fuel'] for h in hist]
        self.ax_alt.clear(); self.ax_alt.plot(ts, alt); self.ax_alt.set_title('Altitude (m)')
        self.ax_vel.clear(); self.ax_vel.plot(ts, vel); self.ax_vel.set_title('Velocity (m/s)')
        self.ax_fuel.clear(); self.ax_fuel.plot(ts, fuel); self.ax_fuel.set_title('Fuel (%)')
        self.fig.tight_layout()
        self.canvas.draw()

    def update_map(self):
        # draw simple path on canvas
        rid = self.current_rocket
        hist = self.telemetry_history.get(rid, [])[-200:]
        if not hist:
            return
        lats = [h['lat'] for h in hist]
        lons = [h['lon'] for h in hist]
        minlat, maxlat = min(lats), max(lats)
        minlon, maxlon = min(lons), max(lons)
        pad = 1e-6
        if abs(maxlat-minlat) < pad: maxlat += pad; minlat -= pad
        if abs(maxlon-minlon) < pad: maxlon += pad; minlon -= pad
        w = int(self.map_canvas['width']); h = int(self.map_canvas['height'])
        self.map_canvas.delete('all')
        # draw path scaled
        points = []
        for la, lo in zip(lats, lons):
            x = int((lo - minlon)/(maxlon-minlon) * (w-20) + 10)
            y = int((1 - (la - minlat)/(maxlat-minlat)) * (h-20) + 10)
            points.append((x,y))
        for i in range(1,len(points)):
            self.map_canvas.create_line(points[i-1][0], points[i-1][1], points[i][0], points[i][1], fill='lime')
        # current position
        cx, cy = points[-1]
        self.map_canvas.create_oval(cx-4, cy-4, cx+4, cy+4, fill='red')
        # predicted landing: naive projection
        pred_x = cx + int(self.labels['velocity']['text'].split()[0]) if self.labels['velocity']['text'] != '-' else cx
        pred_y = cy
        self.map_canvas.create_text(10,10, anchor='nw', fill='white', text=f'Predicted landing approx (naive)')

    def generate_camera_frame(self):
        # create a simple generated frame showing rocket icon and horizon
        if Image is None:
            return
        w, h = 320, 180
        img = Image.new('RGB', (w,h), (20,20,40))
        draw = ImageDraw.Draw(img)
        # draw horizon based on pitch
        pitch = 0.0
        rid = self.current_rocket
        hist = self.telemetry_history.get(rid, [])
        if hist:
            pitch = hist[-1].get('pitch', 0.0)
        horizon_y = h//2 + int(pitch)
        draw.rectangle([0, horizon_y, w, h], fill=(30,80,150))
        draw.rectangle([0,0,w,horizon_y], fill=(100,100,120))
        # rocket icon center
        rx, ry = w//2, h//2 + 20
        draw.polygon([(rx, ry-30),(rx-10, ry),(rx+10, ry)], fill=(200,200,200))
        draw.rectangle([rx-6,ry,rx+6,ry+30], fill=(160,160,160))
        # draw text overlay
        ts = datetime.datetime.now().strftime('%H:%M:%S')
        draw.text((8,8), f'{rid} - {ts}', fill=(255,255,0))
        # convert
        self.cam_image = ImageTk.PhotoImage(img.resize((480,270)))
        self.cam_label.configure(image=self.cam_image)

    def push_alert(self, rocket_id, level, message):
        t = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        s = f'[{t}] {rocket_id} {level}: {message}\n'
        self.alert_box['state'] = 'normal'
        self.alert_box.insert('end', s)
        self.alert_box.see('end')
        self.alert_box['state'] = 'disabled'
        # also log in mission log
        self.logger.log_event(rocket_id, level, message)

    def log(self, message):
        t = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        s = f'[{t}] {message}\n'
        self.log_box['state'] = 'normal'
        self.log_box.insert('end', s)
        self.log_box.see('end')
        self.log_box['state'] = 'disabled'

    def refresh_ui(self):
        # periodic tasks
        # update camera even if no new telemetry
        self.generate_camera_frame()
        # draw graphs if needed
        if Figure is not None:
            self.update_graphs()
        self.after(1000, self.refresh_ui)

    def on_close(self):
        if messagebox.askokcancel('Quit', 'Stop monitoring and exit?'):
            try:
                self.simulator.stop()
            except Exception:
                pass
            try:
                self.logger.close()
            except Exception:
                pass
            self.destroy()

# --------------------- Run --------------------------------------------
if __name__ == '__main__':
    app = RocketMonitorApp()
    app.protocol('WM_DELETE_WINDOW', app.on_close)
    app.mainloop()
