import tkinter as tk
from tkinter import ttk
import serial
import serial.tools.list_ports
import math
import threading
import time
import queue
import base64
import requests
import configparser
import os

try:
    from tkintermapview import TkinterMapView
    HAS_MAP = True
except ImportError:
    HAS_MAP = False

CENTER_OFFSET = 2048
SIGNAL_SCALE = 1.2
QUALITY_SCALE = 0.3
NOIP_UPDATE_INTERVAL = 10 * 60 * 1000

MODE_OPTIONS = [
    ("00", "SSB Medium"), ("01", "SSB Slow"), ("02", "CW Ultra Fast"),
    ("03", "CW Very Fast"), ("04", "CW Fast"), ("05", "Special S2"),
    ("06", "Special S1"), ("07", "CW Medium"), ("08", "CW Slow"),
    ("09", "AM Medium"), ("10", "AM Slow"), ("11", "FM Medium"),
    ("12", "FM Slow"), ("13", "Special S3"), ("14", "Special S4")
]
BINT_OPTIONS = [
    ("00", "35 ms"), ("01", "50 ms"), ("02", "80 ms"), ("03", "100 ms"),
    ("04", "160 ms"), ("05", "200 ms"), ("06", "275 ms"), ("07", "400 ms")
]
IFBW_OPTIONS = [
    ("00", "6 kHz"), ("01", "15 kHz"), ("02", "30 kHz"), ("03", "200 kHz")
]
BAND_OPTIONS = [(f"{i:02}", f"Band {i:02}") for i in range(1, 16)]

CMD_DELAYS = {
    'MODE=': 300,
    'IFBW=': 300,
    'BAND=': 300,
    'BINT=': 100,
    'MUTE=': 100,
    'THLD=': 100,
    'START': 200,
    'STOP': 100,
    'STATUS': 200
}

class DFP2000BGUIGraph(tk.Canvas):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.config(bg='grey')
        self.center = (150, 150)
        self.radius = 100
        self._draw_static_elements()

    def _draw_static_elements(self):
        x, y = self.center
        self.create_oval(x-self.radius, y-self.radius, x+self.radius, y+self.radius,
                         fill='blue', outline='black')
        for angle in range(0, 360, 30):
            rad = math.radians(angle)
            lx = x + math.sin(rad) * (self.radius + 10)
            ly = y - math.cos(rad) * (self.radius + 10)
            self.create_text(lx, ly, text=str(angle), font=("Arial", 8))
        self.line = self.create_line(x, y, x, y, fill='yellow', width=2)
        self.signal_bar = self.create_rectangle(10, 280, 10, 295, fill='green')
        self.quality_bar = self.create_rectangle(10, 310, 10 + 1, 325, fill='orange')
        self.bearing_label = self.create_text(
            x, y+self.radius+20,
            text="Bearing: ---°", fill='white', font=("Arial", 10)
        )
        self.signal_text = self.create_text(
            130, 285, text="", fill='white', font=("Arial", 8), anchor='w'
        )
        self.quality_text = self.create_text(
            130, 315, text="", fill='white', font=("Arial", 8), anchor='w'
        )
        self.avg_text = self.create_text(
            150, 370, text="Avg: ---", fill='white', font=("Arial", 9)
        )

    def update_bearing(self, angle, signal, quality):
        x, y = self.center
        angle_rad = math.radians(angle)
        x2 = x + math.sin(angle_rad) * self.radius
        y2 = y - math.cos(angle_rad) * self.radius
        self.coords(self.line, x, y, x2, y2)
        self.itemconfig(self.bearing_label, text=f"Bearing: {int(angle)%360:03d}°")
        self.coords(self.signal_bar, 10, 280, 10 + max(int(signal), 1), 295)
        self.coords(self.quality_bar, 10, 310, 10 + max(int(quality), 1), 325)
        self.itemconfig(self.signal_text, text=str(int(signal)))
        self.itemconfig(self.quality_text, text=str(int(quality)))

    def update_avg(self, count):
        self.itemconfig(self.avg_text, text=f"Avg: {count}")

class DFP2000BGUI:
    def __init__(self, root):
        self.root = root
        root.title("DFP-2000B Control GUI")
        root.protocol("WM_DELETE_WINDOW", self.on_close)

        self.serial = None
        self.running = False
        self.history = []
        self.last_signal = 0

        self.port = tk.StringVar()
        self.mode = tk.StringVar(value=MODE_OPTIONS[0][1])
        self.bint = tk.StringVar(value=BINT_OPTIONS[0][1])
        self.ifbw = tk.StringVar(value=IFBW_OPTIONS[0][1])
        self.band = tk.StringVar(value=BAND_OPTIONS[0][1])
        self.mute = tk.BooleanVar()
        self.thld = tk.BooleanVar()
        self.avg = tk.DoubleVar(value=0.5)
        self.avg_value = self.avg.get()
        self.avg.trace_add('write', lambda *a: setattr(self, 'avg_value', self.avg.get()))
        self.offset = tk.DoubleVar(value=0.0)
        self.status = tk.StringVar(value="DFP Status: ---")

        self.noip = tk.BooleanVar()
        self.noip_host = tk.StringVar()
        self.noip_user = tk.StringVar()
        self.noip_pass = tk.StringVar()
        self.noip_status = tk.StringVar(value="No-IP: Disconnected")

        self.map_lat = tk.DoubleVar(value=57.0)
        self.map_lon = tk.DoubleVar(value=12.0)

        self.last_bearing = 0

        self.ui_queue = queue.Queue()
        main = ttk.Frame(root)
        main.pack(fill=tk.BOTH, expand=True)
        left = ttk.Frame(main)
        left.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)
        self.canvas = DFP2000BGUIGraph(main, width=320, height=420)
        self.canvas.pack(side=tk.RIGHT, padx=10, pady=10)
        self.log = tk.Text(root, height=8, bg='black', fg='lime', font=("Courier", 9))
        self.log.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=5)

        ttk.Label(left, text='COM Port').grid(row=0,column=0,sticky='w')
        ttk.Combobox(left,textvariable=self.port,values=[p.device for p in serial.tools.list_ports.comports()],state='readonly',width=12).grid(row=0,column=1)
        ttk.Button(left,text='Connect',command=self.connect).grid(row=1,column=0,padx=5,pady=2)
        ttk.Button(left,text='Start',command=self.start).grid(row=1,column=1,pady=2)
        ttk.Button(left,text='Stop',command=self.stop).grid(row=2,column=0,padx=5,pady=2)
        ttk.Button(left,text='Send Settings',command=self.send_settings).grid(row=2,column=1,pady=2)
        ttk.Button(left,text='Get Status',command=self.get_status).grid(row=3,column=0,columnspan=2,pady=5)
        for i,(lbl,opts,var) in enumerate([
            ('Mode', MODE_OPTIONS, self.mode),
            ('Integration', BINT_OPTIONS, self.bint),
            ('IFBW', IFBW_OPTIONS, self.ifbw),
            ('Band', BAND_OPTIONS, self.band)
        ],start=4):
            ttk.Label(left,text=lbl).grid(row=i,column=0,sticky='w')
            ttk.Combobox(left,textvariable=var,values=[d for c,d in opts],state='readonly',width=14).grid(row=i,column=1,sticky='w')
        ttk.Checkbutton(left,text='Mute',variable=self.mute).grid(row=8,column=0,sticky='w')
        ttk.Checkbutton(left,text='Track & Hold',variable=self.thld).grid(row=8,column=1,sticky='w')
        ttk.Label(left,text='Avg (s)').grid(row=9,column=0,sticky='w')
        ttk.Spinbox(left,from_=0.1,to=5.0,increment=0.1,textvariable=self.avg,format='%.1f',width=6).grid(row=9,column=1,sticky='w')
        ttk.Label(left,text='Offset (°)').grid(row=10,column=0,sticky='w')
        ttk.Spinbox(left,from_=-180,to=180,increment=1,textvariable=self.offset,width=6).grid(row=10,column=1,sticky='w')
        ttk.Label(left, text='Lat').grid(row=11, column=0, sticky='w')
        ttk.Entry(left, textvariable=self.map_lat, width=10).grid(row=11, column=1, sticky='w')
        ttk.Label(left, text='Lon').grid(row=12, column=0, sticky='w')
        ttk.Entry(left, textvariable=self.map_lon, width=10).grid(row=12, column=1, sticky='w')
        ttk.Checkbutton(left,text='Use No-IP',variable=self.noip).grid(row=13,column=0,columnspan=2,sticky='w',pady=(10,0))
        ttk.Label(left,text='Host').grid(row=14,column=0,sticky='w')
        ttk.Entry(left,textvariable=self.noip_host,width=20).grid(row=14,column=1,sticky='w')
        ttk.Label(left,text='Username').grid(row=15,column=0,sticky='w')
        ttk.Entry(left,textvariable=self.noip_user,width=20).grid(row=15,column=1,sticky='w')
        ttk.Label(left,text='Password').grid(row=16,column=0,sticky='w')
        pw_entry=ttk.Entry(left,textvariable=self.noip_pass,width=20)
        pw_entry.config(show='*')
        pw_entry.grid(row=16,column=1,sticky='w')
        ttk.Button(left,text='Update No-IP',command=self.update_noip).grid(row=17,column=0,columnspan=2,pady=5)
        ttk.Label(left,textvariable=self.noip_status,wraplength=200).grid(row=18,column=0,columnspan=2,sticky='w')
        ttk.Button(left, text='Map', command=self.open_map_window).grid(row=19, column=0, columnspan=2, pady=8)
        ttk.Button(left, text='Save', command=self.save_settings).grid(row=20, column=0, columnspan=2, pady=6)
        ttk.Label(left, textvariable=self.status, wraplength=200).grid(row=21, column=0, columnspan=2, sticky='w')
        self.root.after(100, self.process_ui_queue)
        self.schedule_noip()
        self.load_settings()

    def log_debug(self,msg):
        self.root.after(0,lambda:(self.log.insert(tk.END,msg+"\n"),self.log.see(tk.END)))

    def save_settings(self):
        config = configparser.ConfigParser()
        config['Settings'] = {
            'com_port': self.port.get(),
            'mode': self.mode.get(),
            'bint': self.bint.get(),
            'ifbw': self.ifbw.get(),
            'band': self.band.get(),
            'mute': str(int(self.mute.get())),
            'thld': str(int(self.thld.get())),
            'avg': str(self.avg.get()),
            'offset': str(self.offset.get()),
            'noip': str(int(self.noip.get())),
            'noip_host': self.noip_host.get(),
            'noip_user': self.noip_user.get(),
            'noip_pass': self.noip_pass.get(),
            'map_lat': str(self.map_lat.get()),
            'map_lon': str(self.map_lon.get())
        }
        with open('settings.ini', 'w') as f:
            config.write(f)
        self.log_debug("[SAVED] Settings saved to settings.ini")

    def load_settings(self):
        if not os.path.exists('settings.ini'):
            return
        config = configparser.ConfigParser()
        config.read('settings.ini')
        s = config['Settings']
        try:
            self.port.set(s.get('com_port', self.port.get()))
            self.mode.set(s.get('mode', self.mode.get()))
            self.bint.set(s.get('bint', self.bint.get()))
            self.ifbw.set(s.get('ifbw', self.ifbw.get()))
            self.band.set(s.get('band', self.band.get()))
            self.mute.set(int(s.get('mute', int(self.mute.get()))))
            self.thld.set(int(s.get('thld', int(self.thld.get()))))
            self.avg.set(float(s.get('avg', self.avg.get())))
            self.offset.set(float(s.get('offset', self.offset.get())))
            self.noip.set(int(s.get('noip', int(self.noip.get()))))
            self.noip_host.set(s.get('noip_host', self.noip_host.get()))
            self.noip_user.set(s.get('noip_user', self.noip_user.get()))
            self.noip_pass.set(s.get('noip_pass', self.noip_pass.get()))
            self.map_lat.set(float(s.get('map_lat', self.map_lat.get())))
            self.map_lon.set(float(s.get('map_lon', self.map_lon.get())))
            self.log_debug("[LOADED] Settings loaded from settings.ini")
        except Exception as e:
            self.log_debug(f"[LOAD] Error loading settings: {e}")

    def connect(self):
        try:
            self.serial=serial.Serial(self.port.get(),19200,timeout=1)
            self.log_debug(f"[CONNECT] {self.port.get()}")
        except Exception as e:
            self.log_debug(f"[ERROR] {e}")

    def send_cmd(self,cmd):
        if not self.serial or not getattr(self.serial,'is_open',False):
            self.log_debug("[ERROR] Serial port is closed or not connected.")
            return False
        try:
            self.serial.reset_input_buffer()
            self.serial.write(f"{cmd}\r\n".encode())
            self.serial.flush()
            self.log_debug(f"[SEND] {cmd}")
            if cmd in ('START', 'STOP'):
                time.sleep(CMD_DELAYS[cmd] / 1000)
                return True
            delay = CMD_DELAYS.get(cmd.split('=')[0] + '=', 100) / 1000
            time.sleep(delay)
            buf, start = '', time.time()
            while time.time() - start < 3.0:
                if self.serial.in_waiting:
                    d = self.serial.read(self.serial.in_waiting).decode(errors='ignore')
                    buf += d
                    self.log_debug(f"[RECV] {d.strip()}")
                    if 'OK' in buf:
                        return True
            self.log_debug(f"[TIMEOUT] {cmd}")
            return False
        except Exception as e:
            self.log_debug(f"[ERROR] Serial exception during {cmd}: {e}")
            return False

    def send_settings(self):
        cmds=[f"MODE={c}" for c,d in MODE_OPTIONS if d==self.mode.get()]
        cmds+=[f"BINT={c}" for c,d in BINT_OPTIONS if d==self.bint.get()]
        cmds+=[f"IFBW={c}" for c,d in IFBW_OPTIONS if d==self.ifbw.get()]
        cmds+=[f"BAND={c}" for c,d in BAND_OPTIONS if d==self.band.get()]
        cmds+=[f"MUTE={'1' if self.mute.get() else '0'}",f"THLD={'1' if self.thld.get() else '0'}"]
        for c in cmds: self.send_cmd(c)
        if self.running: self.send_cmd('START')

    def start(self):
        if not self.serial or not getattr(self.serial,'is_open',False):
            self.log_debug("[ERROR] Serial not open for START")
            return
        if self.send_cmd('START'):
            self.running=True
            self.history.clear()
            threading.Thread(target=self.read_loop,daemon=True).start()
            self.log_debug("[START] Running")
        else:
            self.log_debug("[ERROR] START failed")

    def stop(self):
        self.running=False
        self.send_cmd('STOP')
        self.log_debug("[STOP] Stopped")

    def get_status(self):
        if not self.serial or not getattr(self.serial,'is_open',False):
            self.log_debug("[ERROR] Serial not open for STATUS")
            return
        self.serial.reset_input_buffer()
        self.serial.write(b"STATUS\r\n")
        self.serial.flush()
        buf, start = '', time.time()
        while time.time()-start<1.0:
            if self.serial.in_waiting:
                d=self.serial.read(self.serial.in_waiting).decode(errors='ignore')
                buf+=d
                self.log_debug(f"[RECV] {d.strip()}")
                if '\r\n'in buf: break
        line=buf.splitlines()[0] if buf else ''
        if not line or 'MODE='not in line:
            self.status.set("DFP Status: Timeout or invalid response")
            return
        self.status.set(f"DFP Status: {line}")
        settings={tok.split('=',1)[0]:tok.split('=',1)[1] for tok in line.split() if '='in tok}
        for c,l in MODE_OPTIONS:
            if settings.get('MODE')==c: self.mode.set(l)
        for c,l in BINT_OPTIONS:
            if settings.get('BINT')==c: self.bint.set(l)
        for c,l in IFBW_OPTIONS:
            if settings.get('IFBW')==c: self.ifbw.set(l)
        for c,l in BAND_OPTIONS:
            if settings.get('BAND')==c: self.band.set(l)
        self.mute.set(settings.get('MUTE')=='1')
        self.thld.set(settings.get('THLD')=='1')
        if self.running: self.send_cmd('START')

    # --- UPDATED averaging logic for block/integrate mode ---
    def read_loop(self):
        buffer = []
        last_update = time.time()
        while self.running and self.serial and self.serial.is_open:
            try:
                line = self.serial.readline().decode(errors='ignore').strip()
                if not (line.startswith('B') and len(line) >= 15):
                    continue
                try:
                    raw_x = int(line[1:5])
                    raw_y = int(line[5:9])
                    toggle = line[9]
                    mm = int(line[10:12])
                    compass = int(line[12:15])
                except Exception as e:
                    continue
                x2 = raw_x - CENTER_OFFSET
                y2 = raw_y - CENTER_OFFSET
                angle = (math.degrees(math.atan2(x2, y2)) + 360) % 360
                if toggle == 'S':
                    self.last_signal = mm * SIGNAL_SCALE
                sig = self.last_signal
                qual = math.hypot(x2, y2) * QUALITY_SCALE
                buffer.append((angle, sig, qual))
                now = time.time()
                interval = self.avg.get()
                if now - last_update >= interval:
                    if buffer:
                        angles = [a for a, s, q in buffer]
                        sigs = [s for a, s, q in buffer]
                        quals = [q for a, s, q in buffer]
                        ss = sum(math.sin(math.radians(a)) for a in angles)
                        cs = sum(math.cos(math.radians(a)) for a in angles)
                        avg_angle = (math.degrees(math.atan2(ss, cs)) + 360) % 360
                        avg_sig = sum(sigs) / len(sigs)
                        avg_qual = sum(quals) / len(quals)
                        cnt = len(buffer)
                        self.last_bearing = avg_angle
                        self.ui_queue.put((avg_angle, avg_sig, avg_qual, cnt))
                    buffer = []
                    last_update = now
            except Exception as ex:
                self.log_debug(f"[THREAD ERROR] {ex}")

    def process_ui_queue(self):
        try:
            while True:
                avg, sig, qual, cnt = self.ui_queue.get_nowait()
                angle = (avg + self.offset.get()) % 360
                self.canvas.update_bearing(angle, sig, qual)
                self.canvas.update_avg(cnt)
        except queue.Empty:
            pass
        self.root.after(100, self.process_ui_queue)

    def schedule_noip(self):
        self.root.after(NOIP_UPDATE_INTERVAL, lambda: (self.update_noip(), self.schedule_noip()))

    def update_noip(self):
        if not self.noip.get():
            self.noip_status.set("No-IP: Disabled")
            return
        auth = base64.b64encode(f"{self.noip_user.get()}:{self.noip_pass.get()}".encode()).decode()
        headers = {"Authorization": f"Basic {auth}", "User-Agent": "DFP2000BClient"}
        try:
            r = requests.get(f"https://dynupdate.no-ip.com/nic/update?hostname={self.noip_host.get()}",
                             headers=headers, timeout=5)
            status = r.text.strip()
            if "good" in status or "nochg" in status:
                self.noip_status.set(f"No-IP: Updated ({status})")
            else:
                self.noip_status.set(f"No-IP Error: {status}")
            self.log_debug(f"[No-IP] {status}")
        except Exception as e:
            self.noip_status.set(f"No-IP Connection Error: {e}")
            self.log_debug(f"[No-IP ERROR] {e}")

    def on_close(self):
        self.running = False
        if self.serial and getattr(self.serial, 'is_open', False):
            try:
                self.serial.close()
            except:
                pass
        self.root.after(200, self.root.destroy)

    def open_map_window(self):
        win = tk.Toplevel(self.root)
        win.title("Direction Map")
        lat = self.map_lat.get()
        lon = self.map_lon.get()

        if HAS_MAP:
            map_widget = TkinterMapView(win, width=600, height=400, corner_radius=0)
            map_widget.pack(fill="both", expand=True)
            map_widget.set_position(lat, lon)
            map_widget.set_zoom(6)
            ring_path = [None]
            bearing_line = [None]
            def redraw_shapes():
                angle = getattr(self, "last_bearing", 0)
                R_km = 0.1  # 100 meters ring radius
                ring_points = []
                for t in range(0, 360, 18):
                    t_rad = math.radians(t)
                    ring_lat = lat + (R_km * math.cos(t_rad)) / 111.32
                    ring_lon = lon + (R_km * math.sin(t_rad)) / (111.32 * math.cos(math.radians(lat)))
                    ring_points.append((ring_lat, ring_lon))
                ring_points.append(ring_points[0])
                if ring_path[0]:
                    map_widget.delete(ring_path[0])
                ring_path[0] = map_widget.set_path(ring_points, color="red", width=2)
                R1 = 0.1    # Start at 100 meters (edge of ring)
                R2 = 1600   # End at 1600 km (double previous)
                start_lat = lat + (R1 * math.cos(math.radians(angle))) / 111.32
                start_lon = lon + (R1 * math.sin(math.radians(angle))) / (111.32 * math.cos(math.radians(lat)))
                end_lat = lat + (R2 * math.cos(math.radians(angle))) / 111.32
                end_lon = lon + (R2 * math.sin(math.radians(angle))) / (111.32 * math.cos(math.radians(lat)))
                if bearing_line[0]:
                    map_widget.delete(bearing_line[0])
                bearing_line[0] = map_widget.set_path(
                    [(start_lat, start_lon), (end_lat, end_lon)],
                    color="red", width=2
                )
                win.after(1000, redraw_shapes)
            redraw_shapes()
        else:
            c = tk.Canvas(win, width=600, height=600, bg='white')
            c.pack()
            x0, y0 = 300, 300
            r = 3
            c.create_oval(x0 - r, y0 - r, x0 + r, y0 + r, outline="red", width=2)
            c.create_text(x0, y0 + 15, text="Station")
            def update_line():
                c.delete("line")
                angle = getattr(self, "last_bearing", 0)
                L = 400
                x1 = x0 + r * math.sin(math.radians(angle))
                y1 = y0 - r * math.cos(math.radians(angle))
                x2 = x0 + L * math.sin(math.radians(angle))
                y2 = y0 - L * math.cos(math.radians(angle))
                c.create_line(x1, y1, x2, y2, fill="red", width=1, arrow=tk.LAST, tag="line")
                c.create_text(60, 20, text=f"Bearing: {int(angle):03d}°", font=("Arial", 12))
                win.after(1000, update_line)
            update_line()

if __name__ == '__main__':
    try:
        root = tk.Tk()
        gui = DFP2000BGUI(root)
        root.mainloop()
    except KeyboardInterrupt:
        print("Exiting...")
