import sys
import json
import struct
import time
import threading
import tkinter as tk
from tkinter import ttk
import ctypes
import numpy as np

from pymem import Pymem
from pymem.process import list_processes

from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QPainter, QColor, QPen

# ------ some define and offset -----------

print("[+] Loading offsets.json")
with open("offsets.json", "r") as f:
    _raw = json.load(f)

OFFS = {}
for k, v in _raw.items():
    try:
        # Try converting value to hex integer
        OFFS[k] = int(v, 16)
    except ValueError:
        # Skip non-hex values (like version info)
        print(f"[!] Skipping non-hex offset: {k} = {v}")
        continue

print(f"[+] Loaded {len(OFFS)} valid offsets")


def DRP(pm, addr):
    try:
        b = pm.read_bytes(addr, 8)
        return int.from_bytes(b, "little")
    except:
        return 0


def GetChildren(pm, inst, off):
    out = []
    try:
        start = DRP(pm, inst + off)
        end   = DRP(pm, start + 8)
        cur   = DRP(pm, start)
        while cur and cur < end:
            out.append(pm.read_longlong(cur))
            cur += 0x10
    except:
        pass
    return out


def read_string_safe(pm, addr, length=32):
    try:
        raw = pm.read_bytes(addr, length).split(b'\x00', 1)[0]
        return raw.decode('utf-8', 'ignore')
    except:
        return ""


def get_class_name(pm, inst):
    try:
        cd    = pm.read_longlong(inst + OFFS["ClassDescriptor"])
        ptr   = pm.read_longlong(cd   + OFFS["ClassDescriptorToClassName"])
        return read_string_safe(pm, ptr)
    except:
        return "<err>"


def get_name(pm, inst):
    try:
        ptr = pm.read_longlong(inst + OFFS["Name"])
        return read_string_safe(pm, ptr)
    except:
        return "<err>"


def get_world_pos(pm, inst):
    try:
        ph = DRP(pm, inst + OFFS["Primitive"])
        # Read all 3 floats at once
        pos_data = pm.read_bytes(ph + OFFS["Position"], 12)
        return struct.unpack('<3f', pos_data)
    except:
        return (0, 0, 0)


def FindPlayersService(pm, realDM):
    for inst in GetChildren(pm, realDM, OFFS["Children"]):
        if get_class_name(pm, inst) == "Players":
            return inst
    return 0


def world_to_screen(position, view_matrix, screen_width, screen_height):
    """
    Convert 3D coordinates to 2D coordinates
    using the view matrix
    """
    x, y, z = position
    world_pos = np.array([x, y, z, 1.0])
    
    clip_pos = view_matrix @ world_pos
    
    # if point is behind camera
    if clip_pos[3] < 0.1:
        return None
    
    # divis
    ndc_x = clip_pos[0] / clip_pos[3]
    ndc_y = clip_pos[1] / clip_pos[3]
    
    # Check if point is within view frustum
    if not (-1 <= ndc_x <= 1 and -1 <= ndc_y <= 1):
        return None
    
    # convert to screen coordinates
    screen_x = (ndc_x + 1) * 0.5 * screen_width
    screen_y = (1 - ndc_y) * 0.5 * screen_height
    
    return (int(screen_x), int(screen_y))


# some work thread

class DataThread(QThread):
    targetsReady = pyqtSignal(list)

    def __init__(self, pm, base, offs, fps=60, parent=None):
        super().__init__(parent)
        self.pm = pm
        self.base = base
        self.OFFS = offs
        self.interval = 1.0 / fps
        self._running = True
        self.last_count = 0

        # addresses
        self.fakeDM_off = offs["FakeDataModelPointer"]
        self.f2dm_off = offs["FakeDataModelToDataModel"]
        self.children_off = offs["Children"]
        self.viewptr_off = offs["VisualEnginePointer"]
        self.vm_off = offs["viewmatrix"]

        # addresses
        self.fakeDM = DRP(pm, base + self.fakeDM_off)
        self.realDM = DRP(pm, self.fakeDM + self.f2dm_off)
        self.playersS = FindPlayersService(pm, self.realDM)
        self.workspace = pm.read_longlong(self.realDM + offs["Workspace"])
        self.localP = pm.read_longlong(self.playersS + offs["LocalPlayer"])

    def stop(self):
        self._running = False

    def run(self):
        pm = self.pm
        OFFS = self.OFFS
        read_i = pm.read_int
        read_f = pm.read_float
        read_ll = pm.read_longlong
        read_bytes = pm.read_bytes

        # addresses
        playersS = self.playersS
        workspace = self.workspace
        localP = self.localP
        last_count = self.last_count

        while self._running:
            start = time.time()
            targets = []
            # THANKS AI, I LOVE U , CHAT GPT
            try:
                # 1) Read view-matrix in one go
                mat_addr = DRP(pm, self.base + self.viewptr_off) + self.vm_off
                raw = read_bytes(mat_addr, 64)
                matrix_data = struct.unpack("<16f", raw)
                
                # Create 4x4 view matrix in row-major order
                view_matrix = np.array([
                    [matrix_data[0], matrix_data[1], matrix_data[2], matrix_data[3]],
                    [matrix_data[4], matrix_data[5], matrix_data[6], matrix_data[7]],
                    [matrix_data[8], matrix_data[9], matrix_data[10], matrix_data[11]],
                    [matrix_data[12], matrix_data[13], matrix_data[14], matrix_data[15]]
                ])

                # 2) Get current children pointers
                kids = GetChildren(pm, playersS, self.children_off)
                if len(kids) != last_count:
                    last_count = len(kids)
                    playersS = FindPlayersService(pm, self.realDM)
                    workspace = read_ll(self.realDM + OFFS["Workspace"])
                    localP = read_ll(playersS + OFFS["LocalPlayer"])
                    kids = GetChildren(pm, playersS, self.children_off)

                w = self.parent().width()
                h = self.parent().height()

                # 3) Process all players
                for inst in kids:
                    if inst == localP:
                        continue

                    # Read player data
                    team = read_i(inst + OFFS["Team"])
                    char = read_ll(inst + OFFS["ModelInstance"])
                    
                    if not char:
                        # Fallback: match by name in workspace
                        name = get_name(pm, inst)
                        for wch in GetChildren(pm, workspace, self.children_off):
                            if get_name(pm, wch) == name:
                                char = wch
                                break
                    if not char:
                        continue

                    # Find character parts
                    parts = GetChildren(pm, char, self.children_off)
                    hum = head = root = None
                    
                    for c in parts:
                        cname = get_class_name(pm, c)
                        nm = get_name(pm, c)
                        
                        if cname == "Humanoid":
                            hum = c
                        elif nm == "Head":
                            head = c
                        elif nm == "HumanoidRootPart":
                            root = c
                        elif not root and nm in ("Torso", "UpperTorso", "LowerTorso"):
                            root = c
                            
                        # Early exit if we have all essentials
                        if hum and head and root:
                            break

                    if not (hum and head and root):
                        continue

                    # Read health
                    hp = read_f(hum + OFFS["Health"])
                    
                    # Get positions
                    head_pos = get_world_pos(pm, head)
                    root_pos = get_world_pos(pm, root)

                    # numpy caculate
                    scr_h = world_to_screen(head_pos, view_matrix, w, h)
                    scr_r = world_to_screen(root_pos, view_matrix, w, h)
                    
                    if not (scr_h and scr_r):
                        continue

                    x_top, y_top = scr_h
                    y_bot = scr_r[1]
                    box_h = max(1, y_bot - y_top)
                    box_w = box_h * 0.5  # Default
                    x_ctr = x_top

                    # Calculate box width bye shoulders (if available)
                    for c in parts:
                        nm = get_name(pm, c)
                        if nm in ("Left Arm", "LeftUpperArm"):
                            lpos = get_world_pos(pm, c)
                            sl = world_to_screen(lpos, view_matrix, w, h)
                        elif nm in ("Right Arm", "RightUpperArm"):
                            rpos = get_world_pos(pm, c)
                            sr = world_to_screen(rpos, view_matrix, w, h)
                    
                    if 'sl' in locals() and 'sr' in locals() and sl and sr:
                        box_w = abs(sr[0] - sl[0])
                        x_ctr = (sl[0] + sr[0]) / 2

                    targets.append((x_ctr, y_top, box_w, box_h, hp, team))

            except Exception as e:
                print(f"[!] DataThread error: {e}")

            # emit to gui
            if targets:
                self.targetsReady.emit(targets)

            # fps
            elapsed = time.time() - start
            to_sleep = max(0, self.interval - elapsed)
            time.sleep(to_sleep)


# ---------- qt layer ----------

class ESPOverlay(QWidget):
    def __init__(self, pm, base, fps=60, show_esp=True, show_hp=True):
        super().__init__()
        self.pm = pm
        self.base = base
        self.targets = []
        self.fps = fps
        self.show_esp = show_esp
        self.show_hp = show_hp

        # Configure window properties (without them = BROKEN)
        self.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint |
            Qt.Tool
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.showFullScreen()

        # Start data thread
        self.worker = DataThread(pm, base, OFFS, fps=fps, parent=self)
        self.worker.targetsReady.connect(self.onTargetsReady)
        self.worker.start()
        print(f"[+] DataThread started at ~{fps} Hz")

    def onTargetsReady(self, tlist):
        self.targets = tlist
        self.update()  # Request a repaint

    def paintEvent(self, ev):
        if not self.targets:
            return
            
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        
        # pens
        green_pen = QPen(QColor(0, 255, 0, 200), 2)
        red_pen = QPen(QColor(255, 0, 0, 200), 2)
        blue_pen = QPen(QColor(0, 150, 255, 200), 2)
        
        for x, y_top, w, h, hp, team in self.targets:
            # Choose color based on team and health :D
            if team == 0:  # bad team
                pen = red_pen if hp > 0 else blue_pen
            else:  # good team
                pen = green_pen
                
            # Draw bounding box if enabled
            if self.show_esp:
                p.setPen(pen)
                p.drawRect(int(x - w/2), int(y_top), int(w), int(h))
            
            # Draw health info if enabled
            if self.show_hp:
                # Health bar
                if hp > 0:
                    health_width = max(0, min(1, hp/100)) * w
                    health_color = QColor(0, 255, 0, 150) 
                    p.fillRect(int(x - w/2), int(y_top) - 5, int(health_width), 3, health_color)
                
                # Health text
                p.setPen(QColor(255, 255, 255, 220))
                p.drawText(int(x - w/2), int(y_top) - 10, f"{int(hp)} HP")
            
        p.end()

    def closeEvent(self, ev):
        self.worker.stop()
        self.worker.wait(2000) 
        ev.accept()


# -------- tk stuff ---------

class ESPController:
    def __init__(self):
        self.overlay_app = None
        self.overlay_window = None
        self.esp_active = False
        self.pm = None
        self.base = None
        self.qt_thread = None
        
        # tk window
        self.root = tk.Tk()
        self.root.title("ESP")
        self.root.geometry("350x320")
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        
        # style conf
        style = ttk.Style()
        style.configure("TButton", padding=6, font=("Segoe UI", 10))
        style.configure("TLabel", font=("Segoe UI", 9))
        style.configure("Title.TLabel", font=("Segoe UI", 12, "bold"))
        
        # title
        title = ttk.Label(self.root, text="esp tool | by tux_koh", style="Title.TLabel")
        title.pack(pady=10)
        
        # status display
        status_frame = ttk.Frame(self.root)
        status_frame.pack(fill="x", padx=20, pady=5)
        
        ttk.Label(status_frame, text="Status:").pack(side="left")
        self.status_var = tk.StringVar(value="Inactive")
        status_label = ttk.Label(status_frame, textvariable=self.status_var, foreground="red")
        status_label.pack(side="left", padx=5)
        
        # button
        self.toggle_btn = ttk.Button(
            self.root, 
            text="start ESP", 
            command=self.toggle_esp,
            width=20
        )
        self.toggle_btn.pack(pady=10)
        
        # Display options
        display_frame = ttk.LabelFrame(self.root, text="Display Options")
        display_frame.pack(fill="x", padx=20, pady=5)
        
        # ESP box toggle
        self.esp_var = tk.BooleanVar(value=True)
        esp_check = ttk.Checkbutton(
            display_frame,
            text="Show ESP Box",
            variable=self.esp_var
        )
        esp_check.grid(row=0, column=0, sticky="w", padx=5, pady=2)
        
        # HP info toggle
        self.hp_var = tk.BooleanVar(value=True)
        hp_check = ttk.Checkbutton(
            display_frame,
            text="Show Health Info",
            variable=self.hp_var
        )
        hp_check.grid(row=0, column=1, sticky="w", padx=5, pady=2)
        
        # Process info
        info_frame = ttk.LabelFrame(self.root, text="Process Information")
        info_frame.pack(fill="x", padx=20, pady=10)
        
        self.pid_var = tk.StringVar(value="Not detected")
        self.base_var = tk.StringVar(value="Not detected")
        
        ttk.Label(info_frame, text="Roblox PID:").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        ttk.Label(info_frame, textvariable=self.pid_var).grid(row=0, column=1, sticky="w", padx=5, pady=2)
        
        ttk.Label(info_frame, text="Module Base:").grid(row=1, column=0, sticky="w", padx=5, pady=2)
        ttk.Label(info_frame, textvariable=self.base_var).grid(row=1, column=1, sticky="w", padx=5, pady=2)
        
        # Performance settings
        perf_frame = ttk.LabelFrame(self.root, text="Performance Settings")
        perf_frame.pack(fill="x", padx=20, pady=10)
        
        ttk.Label(perf_frame, text="Target FPS:").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        self.fps_var = tk.StringVar(value="60")
        fps_spin = ttk.Spinbox(
            perf_frame, 
            from_=30, 
            to=120, 
            textvariable=self.fps_var,
            width=5
        )
        fps_spin.grid(row=0, column=1, sticky="w", padx=5, pady=2)
        
        # Start GUI
        self.root.mainloop()
    
    def toggle_esp(self):
        if not self.esp_active:
            self.activate_esp()
        else:
            self.deactivate_esp()
    
    def activate_esp(self):
        # Find Roblox process
        pid = find_roblox_pid()
        if not pid:
            self.status_var.set("Roblox not found!")
            return
            
        self.pid_var.set(str(pid))
        
        try:
            # Initialize Pymem
            self.pm = Pymem()
            self.pm.open_process_from_id(pid)
            
            # Get base address
            self.base = next((m.lpBaseOfDll for m in self.pm.list_modules()
                        if m.name.lower().endswith("robloxplayerbeta.exe")), None)
            if not self.base:
                self.status_var.set("Module not found!")
                return
                
            self.base_var.set(hex(self.base))
            
            # Get FPS value
            try:
                fps = int(self.fps_var.get())
                fps = max(30, min(120, fps))  # 120+ = device explode
            except:
                fps = 60
            
            # Start esp
            self.esp_active = True
            self.toggle_btn.config(text="Deactivate ESP")
            self.status_var.set("Active")
            
            self.qt_thread = threading.Thread(
                target=self.run_qt_app,
                args=(fps,),
                daemon=True
            )
            self.qt_thread.start()
            
        except Exception as e:
            self.status_var.set(f"Error: {str(e)}")
            self.esp_active = False
    
    def run_qt_app(self, fps):
        """Run PyQt application in a separate thread"""
        # create QT in the thread
        app = QApplication(sys.argv)
        
        # overlay
        self.overlay_window = ESPOverlay(
            self.pm, 
            self.base, 
            fps=fps,
            show_esp=self.esp_var.get(),
            show_hp=self.hp_var.get()
        )
        
        # referance
        self.overlay_app = app
        
        # Run event loop
        app.exec_()
    
    def deactivate_esp(self):
        """Deactivate ESP functionality"""
        if self.esp_active:
            self.esp_active = False
            self.toggle_btn.config(text="Activate ESP")
            self.status_var.set("Deactivating...")
            
            if self.overlay_app:
                # quit qt
                self.overlay_app.quit()
                
            if self.qt_thread:
                # wait thread done
                self.qt_thread.join(timeout=1.0)
                
            if self.pm:
                try:
                    self.pm.close_process()
                except:
                    pass
                self.pm = None
                
            self.overlay_window = None
            self.overlay_app = None
            self.status_var.set("Inactive")
    
    def on_close(self):
        #destroy
        self.deactivate_esp()
        self.root.destroy()

def find_roblox_pid():
    for p in list_processes():
        name = p.szExeFile.decode(errors="ignore")
        if name.lower().startswith("robloxplayerbeta"):
            print(f"[+] Found Roblox PID={p.th32ProcessID}")
            return p.th32ProcessID
    print("[-] Roblox process not found")
    return None
# PLS WORKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKK

if __name__ == "__main__":
    controller = ESPController()