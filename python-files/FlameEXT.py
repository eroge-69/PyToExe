import sys
import os
import time
import threading
import random
from math import sqrt, pi, sin, cos
from ctypes import windll, byref, Structure, wintypes
import ctypes
import msvcrt
import requests
try:
    from numpy import array, float32, linalg, cross, dot, reshape, empty, einsum
    from requests import get
    from pymem import Pymem
    from pymem.process import list_processes
    from pymem.exception import ProcessError
    from psutil import pid_exists
    from struct import unpack_from
    import json
    import dearpygui.dearpygui as dpg
    DEPS_OK = True
except ImportError as e:
    print(f"Missing dependency: {e}")
    input("Press Enter to exit...")
    sys.exit(1)

pi180 = pi/180
Handle = None
PID = -1
baseAddr = None
pm = Pymem()
aimbot_enabled = False
aimbot_keybind = 0
aimbot_mode = "Hold"
aimbot_toggled = False
waiting_for_keybind = False
injected = False
aimbot_smoothness_enabled = False
aimbot_smoothness_x = 5.5
aimbot_smoothness_y = 5.5
aimbot_ignoreteam = False
aimbot_ignoredead = False
aimbot_hitpart = "Head"
aimbot_prediction_enabled = False
aimbot_prediction_x = 0.01  # Valor inicial ajustado
aimbot_prediction_y = 0.01  # Valor inicial ajustado
aimbot_shake_enabled = False
aimbot_shake_strength = 0.005
aimbot_fov = 2000.0
aimbot_type = "Mouse"  # "Mouse", "Camera" o "Silent Aim"
smoothing_buffer = []
triggerbot_enabled = False
triggerbot_keybind = 1
triggerbot_mode = "Hold"
triggerbot_toggled = False
triggerbot_delay = 0
triggerbot_prediction_x = 0.0
triggerbot_prediction_y = 0.0
triggerbot_fov = 50.0
triggerbot_detection_mode = "Default"
triggerbot_wallcheck_enabled = False
walkspeed_gui_enabled = False
walkspeed_gui_value = 16.0
walkspeed_gui_thread = None
walkspeed_gui_active = False
rotation_360_enabled = False
rotation_360_keybind = 0
rotation_360_in_progress = False
rotation_360_speed = 1.0
rotation_360_mode = "Hold"  # Hold or Toggle
rotation_360_toggled = False
rotation_360_active = False
rotation_360_direction_mode = "Mode 1 (Default)"  # Mode 1 or Mode 2
rotation_360_alternate_direction = False  # Para Mode 2
fly_enabled = False
fly_keybind = 81  # Q key
fly_mode = "Hold"
fly_toggled = False
fly_speed = 60.0
fly_method = 1  # 0 = Position, 1 = Velocity
fly_thread = None
fly_active = False
esp_enabled = False
esp_team_check = False
esp_death_check = False
esp_tracers_enabled = False
esp_box_enabled = False
esp_thread = None
dataModel = 0
wsAddr = 0
camAddr = 0
camCFrameRotAddr = 0
plrsAddr = 0
lpAddr = 0
matrixAddr = 0
camPosAddr = 0
target = 0
nameOffset = 0
childrenOffset = 0
offsets = {}

VK_CODES = {
    'LButton': 1,
    'RButton': 2,
    'MM': 4,
    'XButton1': 5,
    'XButton2': 6,
    '0': 48, '1': 49, '2': 50, '3': 51, '4': 52,
    '5': 53, '6': 54, '7': 55, '8': 56, '9': 57,
    'A': 65, 'B': 66, 'C': 67, 'D': 68, 'E': 69, 'F': 70,
    'G': 71, 'H': 72, 'I': 73, 'J': 74, 'K': 75, 'L': 76,
    'M': 77, 'N': 78, 'O': 79, 'P': 80, 'Q': 81, 'R': 82,
    'S': 83, 'T': 84, 'U': 85, 'V': 86, 'W': 87, 'X': 88,
    'Y': 89, 'Z': 90,
    'F1': 112, 'F2': 113, 'F3': 114, 'F4': 115, 'F5': 116,
    'F6': 117, 'F7': 118, 'F8': 119, 'F9': 120, 'F10': 121,
    'F11': 122, 'F12': 123, 'F13': 124, 'F14': 125, 'F15': 126,
    'F16': 127, 'F17': 128, 'F18': 129, 'F19': 130, 'F20': 131,
    'F21': 132, 'F22': 133, 'F23': 134, 'F24': 135,
    'Shift': 16, 'Ctrl': 17, 'Alt': 18,
    'Tab': 9, 'CapsLock': 20, 'Esc': 27,
    'Space': 32, 'Enter': 13, 'Backspace': 8,
    'LShift': 160, 'RShift': 161, 'LCtrl': 162, 'RCtrl': 163,
    'LAlt': 164, 'RAlt': 165,
    'Left': 37, 'Up': 38, 'Right': 39, 'Down': 40,
    'Insert': 45, 'Delete': 46, 'Home': 36,
    'End': 35, 'PageUp': 33, 'PageDown': 34,
    'Num0': 96, 'Num1': 97, 'Num2': 98, 'Num3': 99, 'Num4': 100,
    'Num5': 101, 'Num6': 102, 'Num7': 103, 'Num8': 104, 'Num9': 105,
    'NumMultiply': 106, 'NumAdd': 107, 'NumSubtract': 109,
    'NumDecimal': 110, 'NumDivide': 111,
    'Semicolon': 186,
    'Equal': 187,
    'Comma': 188,
    'Minus': 189,
    'Period': 190,
    'Slash': 191,
    'Backtick': 192,
    'LBracket': 219,
    'Backslash': 220,
    'RBracket': 221,
    'Quote': 222
}

class RECT(Structure):
    _fields_ = [('left', wintypes.LONG), ('top', wintypes.LONG), ('right', wintypes.LONG), ('bottom', wintypes.LONG)]

class POINT(Structure):
    _fields_ = [('x', wintypes.LONG), ('y', wintypes.LONG)]

class OPENFILENAME(Structure):
    _fields_ = [
        ('lStructSize', wintypes.DWORD),
        ('hwndOwner', wintypes.HWND),
        ('hInstance', wintypes.HINSTANCE),
        ('lpstrFilter', wintypes.LPCWSTR),
        ('lpstrCustomFilter', wintypes.LPWSTR),
        ('nMaxCustFilter', wintypes.DWORD),
        ('nFilterIndex', wintypes.DWORD),
        ('lpstrFile', wintypes.LPWSTR),
        ('nMaxFile', wintypes.DWORD),
        ('lpstrFileTitle', wintypes.LPWSTR),
        ('nMaxFileTitle', wintypes.DWORD),
        ('lpstrInitialDir', wintypes.LPCWSTR),
        ('lpstrTitle', wintypes.LPCWSTR),
        ('Flags', wintypes.DWORD),
        ('nFileOffset', wintypes.WORD),
        ('nFileExtension', wintypes.WORD),
        ('lpstrDefExt', wintypes.LPCWSTR),
        ('lCustData', wintypes.LPARAM),
        ('lpfnHook', wintypes.LPVOID),
        ('lpTemplateName', wintypes.LPCWSTR),
        ('pvReserved', wintypes.LPVOID),
        ('dwReserved', wintypes.DWORD),
        ('FlagsEx', wintypes.DWORD)
    ]



def get_key_name(vk_code):
    for name, code in VK_CODES.items():
        if code == vk_code:
            return name
    return f"Key {vk_code}"

def DRP(address):
    if isinstance(address, str):
        address = int(address, 16)
    return int.from_bytes(pm.read_bytes(address, 8), "little")

def simple_get_processes():
    return [{"Name": i.szExeFile.decode(), "ProcessId": i.th32ProcessID} for i in list_processes()]

def cleanup_resources():
    global Handle, pm
    try:
        if Handle:
            windll.kernel32.CloseHandle(Handle)
            Handle = None
        # Cerrar el proceso de pymem si está abierto
        if hasattr(pm, 'process_handle') and pm.process_handle:
            pm.close_process()
    except:
        pass

def yield_for_program(program_name, printInfo=True):
    global PID, Handle, baseAddr, pm
    
    # Limpiar recursos anteriores antes de abrir nuevos
    cleanup_resources()
    
    for proc in simple_get_processes():
        if proc["Name"] == program_name:
            try:
                pm.open_process_from_id(proc["ProcessId"])
                PID = proc["ProcessId"]
                Handle = windll.kernel32.OpenProcess(0x1038, False, PID)
                for module in pm.list_modules():
                    if module.name == "RobloxPlayerBeta.exe":
                        baseAddr = module.lpBaseOfDll
                        return True
            except Exception as e:
                cleanup_resources()
                continue
    return False

def is_process_dead():
    global PID
    try:
        return PID == -1 or not pid_exists(PID)
    except:
        return True

def get_base_addr():
    return baseAddr

def setOffsets(nameOffset2, childrenOffset2):
    global nameOffset, childrenOffset
    nameOffset = nameOffset2
    childrenOffset = childrenOffset2

def ReadRobloxString(expected_address):
    string_count = pm.read_int(expected_address + 0x10)
    if string_count > 15:
        ptr = DRP(expected_address)
        return pm.read_string(ptr, string_count)
    return pm.read_string(expected_address, string_count)

def GetClassName(instance):
    ptr = pm.read_longlong(instance + 0x18)
    ptr = pm.read_longlong(ptr + 0x8)
    fl = pm.read_longlong(ptr + 0x18)
    if fl == 0x1F:
        ptr = pm.read_longlong(ptr)
    return ReadRobloxString(ptr)

def GetName(instance):
    return ReadRobloxString(DRP(instance + nameOffset))

def GetChildren(instance):
    if not instance:
        return []
    children = []
    start = DRP(instance + childrenOffset)
    if start == 0:
        return []
    end = DRP(start + 8)
    current = DRP(start)
    for _ in range(1000):
        if current == end:
            break
        children.append(pm.read_longlong(current))
        current += 0x10
    return children

def FindFirstChild(instance, child_name):
    if not instance:
        return 0
    start = DRP(instance + childrenOffset)
    if start == 0:
        return 0
    end = DRP(start + 8)
    current = DRP(start)
    for _ in range(1000):
        if current == end:
            break
        child = pm.read_longlong(current)
        try:
            if GetName(child) == child_name:
                return child
        except:
            pass
        current += 0x10
    return 0

def FindFirstChildOfClass(instance, class_name):
    if not instance:
        return 0
    start = DRP(instance + childrenOffset)
    if start == 0:
        return 0
    end = DRP(start + 8)
    current = DRP(start)
    for _ in range(1000):
        if current == end:
            break
        child = pm.read_longlong(current)
        try:
            if GetClassName(child) == class_name:
                return child
        except:
            pass
        current += 0x10
    return 0

# Cache para la ventana de Roblox
_cached_window = None
_last_window_check = 0

def find_window_by_title(title):
    global _cached_window, _last_window_check
    current_time = time.time()
    
    # Solo verificar la ventana cada 0.5 segundos para reducir lag
    if current_time - _last_window_check > 0.5 or _cached_window is None:
        _cached_window = windll.user32.FindWindowW(None, title)
        _last_window_check = current_time
    
    return _cached_window

def get_client_rect_on_screen(hwnd):
    rect = RECT()
    if windll.user32.GetClientRect(hwnd, byref(rect)) == 0:
        return 0, 0, 0, 0
    top_left = POINT(rect.left, rect.top)
    bottom_right = POINT(rect.right, rect.bottom)
    windll.user32.ClientToScreen(hwnd, byref(top_left))
    windll.user32.ClientToScreen(hwnd, byref(bottom_right))
    return top_left.x, top_left.y, bottom_right.x, bottom_right.y

def normalize(vec):
    norm = linalg.norm(vec)
    return vec / norm if norm != 0 else vec

def cframe_look_at(from_pos, to_pos):
    from_pos = array(from_pos, dtype=float32)
    to_pos = array(to_pos, dtype=float32)
    look_vector = normalize(to_pos - from_pos)
    up_vector = array([0, 1, 0], dtype=float32)
    if abs(look_vector[1]) > 0.999:
        up_vector = array([0, 0, -1], dtype=float32)
    right_vector = normalize(cross(up_vector, look_vector))
    recalculated_up = cross(look_vector, right_vector)
    return look_vector, recalculated_up, right_vector

def world_to_screen_with_matrix(world_pos, matrix, screen_width, screen_height):
    vec = array([*world_pos, 1.0], dtype=float32)
    clip = dot(matrix, vec)
    if clip[3] == 0: return None
    ndc = clip[:3] / clip[3]
    if ndc[2] < 0 or ndc[2] > 1: return None
    x = (ndc[0] + 1) * 0.5 * screen_width
    y = (1 - ndc[1]) * 0.5 * screen_height
    return round(x), round(y)

# Función wallcheck eliminada - ya no se usa

def viewport_resize_callback():
    try:
        viewport_width = dpg.get_viewport_width()
        viewport_height = dpg.get_viewport_height()
        dpg.configure_item("Primary Window", width=viewport_width, height=viewport_height)
    except:
        pass

def title_changer():
    while True:
        try:
            dpg.configure_item("Primary Window", label="Flame-external")
            dpg.set_viewport_title("Flame-external")
            # Llamar al callback de redimensionamiento
            viewport_resize_callback()
        except:
            pass
        time.sleep(0.1)

class FlyThread(threading.Thread):
    def __init__(self, pm, base, offsets):
        super().__init__(daemon=True)
        self.pm = pm
        self.base = base
        self.offsets = offsets
        self.running = True
        self.datamodel = 0
        self.playersS = 0
        self.zero_bytes = array([0.0, 0.0, 0.0], dtype=float32).tobytes()

    def run(self):
        while self.running:
            global fly_enabled, fly_keybind, fly_mode, fly_toggled, fly_speed, fly_method, fly_active
            
            if not fly_enabled:
                time.sleep(0.1)
                continue
                
            # Check toggle key
            key_pressed = windll.user32.GetAsyncKeyState(fly_keybind) & 0x8000 != 0
            
            if fly_mode == "Toggle":
                if key_pressed and not fly_active:
                    fly_toggled = not fly_toggled
                    fly_active = True
                elif not key_pressed:
                    fly_active = False
                should_fly = fly_toggled
            else:
                should_fly = key_pressed
                
            if not should_fly:
                time.sleep(0.005)
                continue

            try:
                # Resolve DataModel pointer
                if not self.datamodel:
                    fake_ptr = self.base + int(self.offsets['FakeDataModelPointer'], 16)
                    fake_dm = self.pm.read_longlong(fake_ptr)
                    real_dm = fake_dm and self.pm.read_longlong(fake_dm + int(self.offsets['FakeDataModelToDataModel'], 16))
                    if real_dm:
                        self.datamodel = real_dm
                    else:
                        time.sleep(0.1)
                        continue

                # Resolve PlayersService
                if not self.playersS:
                    for c in self.get_children(self.datamodel):
                        if self.get_class_name(c) == "Players":
                            self.playersS = c
                            break
                    if not self.playersS:
                        time.sleep(0.1)
                        continue

                # Get local player → character → HRP → primitive → camera
                lp = self.pm.read_longlong(self.playersS + int(self.offsets['LocalPlayer'], 16))
                ch = lp and self.pm.read_longlong(lp + int(self.offsets['ModelInstance'], 16))
                hr = ch and self.find_first_child(ch, "HumanoidRootPart")
                pr = hr and self.pm.read_longlong(hr + int(self.offsets['Primitive'], 16))
                ws = self.pm.read_longlong(self.datamodel + int(self.offsets['Workspace'], 16))
                ca = ws and self.pm.read_longlong(ws + int(self.offsets['Camera'], 16))
                
                if not all((lp, ch, hr, pr, ws, ca)):
                    time.sleep(0.005)
                    continue

                # Read camera basis vectors
                cam_rot_addr = ca + int(self.offsets['CameraRotation'], 16)
                cam_matrix = []
                for i in range(9):
                    addr = cam_rot_addr + (i % 3) * 4 + (i // 3) * 12
                    cam_matrix.append(self.pm.read_float(addr))
                
                look = array([-cam_matrix[2], -cam_matrix[5], -cam_matrix[8]], dtype=float32)
                right = array([cam_matrix[0], cam_matrix[3], cam_matrix[6]], dtype=float32)

                # Movement keys → compute move vector
                mv = array([0.0, 0.0, 0.0], dtype=float32)
                if windll.user32.GetAsyncKeyState(87) & 0x8000:  # W
                    mv += look
                if windll.user32.GetAsyncKeyState(83) & 0x8000:  # S
                    mv -= look
                if windll.user32.GetAsyncKeyState(65) & 0x8000:  # A
                    mv -= right
                if windll.user32.GetAsyncKeyState(68) & 0x8000:  # D
                    mv += right
                if windll.user32.GetAsyncKeyState(32) & 0x8000:  # SPACE
                    mv[1] += 1.0
                
                norm = linalg.norm(mv)
                if norm > 0:
                    mv = mv / norm * fly_speed

                # Apply movement
                if fly_method == 0:  # Position method
                    pos_addr = pr + int(self.offsets['Position'], 16)
                    curr_pos = array([
                        self.pm.read_float(pos_addr),
                        self.pm.read_float(pos_addr + 4),
                        self.pm.read_float(pos_addr + 8)
                    ], dtype=float32)
                    new_pos = curr_pos + mv
                    self.pm.write_float(pos_addr, float(new_pos[0]))
                    self.pm.write_float(pos_addr + 4, float(new_pos[1]))
                    self.pm.write_float(pos_addr + 8, float(new_pos[2]))
                    
                    # Zero velocity
                    vel_addr = pr + int(self.offsets['Velocity'], 16)
                    self.pm.write_float(vel_addr, 0.0)
                    self.pm.write_float(vel_addr + 4, 0.0)
                    self.pm.write_float(vel_addr + 8, 0.0)
                else:  # Velocity method
                    vel_addr = pr + int(self.offsets['Velocity'], 16)
                    self.pm.write_float(vel_addr, float(mv[0]))
                    self.pm.write_float(vel_addr + 4, float(mv[1]))
                    self.pm.write_float(vel_addr + 8, float(mv[2]))
                
                # Disable collisions
                self.pm.write_bool(pr + int(self.offsets['CanCollide'], 16), False)

            except Exception:
                pass

            time.sleep(0.005)

    def stop(self):
        self.running = False

    def get_children(self, inst):
        children = []
        try:
            start = self.pm.read_longlong(inst + childrenOffset)
            if start == 0:
                return []
            end = self.pm.read_longlong(start + 8)
            current = self.pm.read_longlong(start)
            for _ in range(1000):
                if current == end:
                    break
                children.append(self.pm.read_longlong(current))
                current += 0x10
        except:
            pass
        return children

    def get_class_name(self, inst):
        try:
            ptr = self.pm.read_longlong(inst + 0x18)
            ptr = self.pm.read_longlong(ptr + 0x8)
            fl = self.pm.read_longlong(ptr + 0x18)
            if fl == 0x1F:
                ptr = self.pm.read_longlong(ptr)
            return ReadRobloxString(ptr)
        except:
            return ""

    def find_first_child(self, parent, target):
        for c in self.get_children(parent):
            try:
                if GetName(c) == target:
                    return c
            except:
                pass
        return 0

# Variables globales para ESP (como tracers.py)
esp_heads = []
esp_colors = []

def esp_head_finder():
    """Función optimizada que encuentra heads como tracers.py"""
    global esp_heads, esp_colors, esp_enabled, esp_tracers_enabled, esp_team_check, esp_death_check
    
    # Cache para mejorar rendimiento
    last_update = 0
    cached_players = []
    
    while True:
        current_time = time.time()
        
        if lpAddr == 0 or plrsAddr == 0 or matrixAddr == 0:
            time.sleep(0.5)
            continue

        if not esp_enabled or not esp_tracers_enabled:
            time.sleep(0.5)
            continue

        temp_colors = []
        temp_heads = []

        try:
            # Actualizar lista de jugadores cada 50ms para detectar más
            if current_time - last_update > 0.05:
                cached_players = GetChildren(plrsAddr)
                last_update = current_time
            
            lp_team = pm.read_longlong(lpAddr + int(offsets['Team'], 16))
            
            print(f"[DEBUG] Total players found: {len(cached_players)}")
            
            for v in cached_players:
                if v == lpAddr:
                    continue
                
                try:
                    # ELIMINAR TODAS LAS RESTRICCIONES DE EQUIPO
                    char = pm.read_longlong(v + int(offsets['ModelInstance'], 16))
                    if not char:
                        continue
                    
                    children_start = DRP(char + childrenOffset)
                    if children_start == 0:
                        continue
                    
                    head = 0
                    children_end = DRP(children_start + 8)
                    current_child_address = DRP(children_start)
                    
                    # Buscar SOLO Head - sin restricciones
                    for _ in range(500):  # Aumentado mucho más
                        try:
                            if current_child_address == children_end:
                                break
                            child = pm.read_longlong(current_child_address)
                            
                            name = GetName(child)
                            if name == 'Head':
                                head = child
                                break  # Encontrado, salir inmediatamente
                                
                            current_child_address += 0x10
                        except:
                            current_child_address += 0x10
                            continue
                    
                    # Si encontramos head, agregarlo SIN MÁS VERIFICACIONES
                    if head:
                        temp_colors.append('white')
                        temp_heads.append(head)
                        print(f"[DEBUG] Head found for player {len(temp_heads)}")
                        
                except Exception as e:
                    print(f"[DEBUG] Error processing player: {e}")
                    continue
                    
        except Exception:
            pass
        
        # Actualizar listas globales de forma atómica
        esp_heads = temp_heads
        esp_colors = temp_colors
        
        # Debug detallado
        print(f"ESP detectó {len(temp_heads)} jugadores de {len(cached_players)} totales")
        
        time.sleep(0.05)  # 50ms entre actualizaciones para tracking más rápido

class ESPThread(threading.Thread):
    def __init__(self, pm, base, offsets):
        super().__init__(daemon=True)
        self.pm = pm
        self.base = base
        self.offsets = offsets
        self.running = True
        self.plr_data = []
        self.prev_plr_data = []
        self.time = 0
        self.prev_geometry = (0, 0, 0, 0)
        self.start_line_x = 0
        self.start_line_y = 0
        self.hwnd_roblox = None
        self.hdc_screen = None

    def run(self):
        # Obtener DC de pantalla para dibujo persistente
        self.hdc_screen = windll.user32.GetDC(0)
        
        while self.running:
            global esp_enabled, esp_tracers_enabled, esp_box_enabled, esp_heads, esp_colors
            
            # Verificar si ESP está habilitado y al menos uno de los modos está activo
            if not esp_enabled or (not esp_tracers_enabled and not esp_box_enabled):
                self.clear_tracers()
                time.sleep(0.05)
                continue

            if lpAddr == 0 or plrsAddr == 0 or matrixAddr == 0:
                self.clear_tracers()
                time.sleep(0.05)
                continue

            try:
                current_time = time.time()
                
                # Actualizar geometría de ventana más frecuentemente
                if current_time - self.time > 0.1:
                    self.hwnd_roblox = find_window_by_title("Roblox")
                    if self.hwnd_roblox:
                        x, y, r, b = get_client_rect_on_screen(self.hwnd_roblox)
                        new_geom = (x, y, r - x, b - y)
                        if new_geom != self.prev_geometry and new_geom[2] > 0 and new_geom[3] > 0:
                            self.prev_geometry = new_geom
                            self.start_line_x = x + new_geom[2] / 2
                            self.start_line_y = y + new_geom[3] - new_geom[3] / 20
                    self.time = current_time

                # Solo procesar si hay heads disponibles
                if not esp_heads:
                    self.clear_tracers()
                    time.sleep(0.02)
                    continue

                # Procesar heads - asegurar capacidad suficiente
                max_players = max(len(esp_heads), 50)  # Mínimo 50 jugadores
                vecs_np = empty((max_players, 4), dtype=float32)
                count = 0
                self.plr_data.clear()

                # Leer matriz
                matrix_raw = self.pm.read_bytes(matrixAddr, 64)
                view_proj_matrix = array(unpack_from("<16f", matrix_raw, 0), dtype=float32).reshape(4, 4)

                # Procesar heads - más permisivo
                for head in esp_heads:
                    try:
                        # Verificar que sea una head válida
                        head_name = GetName(head)
                        if head_name == 'Head':
                            primitive = self.pm.read_longlong(head + int(self.offsets['Primitive'], 16))
                            pos_bytes = self.pm.read_bytes(primitive + int(self.offsets['Position'], 16), 12)
                            vecs_np[count, :3] = unpack_from("<fff", pos_bytes, 0)
                            vecs_np[count, 3] = 1.0
                            count += 1
                        else:
                            vecs_np[count, :3] = 0, 0, 0
                            vecs_np[count, 3] = 1.0
                            count += 1
                    except:
                        vecs_np[count, :3] = 0, 0, 0
                        vecs_np[count, 3] = 1.0
                        count += 1

                if count == 0:
                    self.clear_tracers()
                    time.sleep(0.02)
                    continue

                # Transformación matricial
                clip_coords = einsum('ij,nj->ni', view_proj_matrix, vecs_np[:count])

                # Procesar coordenadas de pantalla
                for idx, clip in enumerate(clip_coords):
                    if clip[3] != 0:
                        ndc = clip[:3] / clip[3]
                        if 0 <= ndc[2] <= 1:
                            x = int((ndc[0] + 1) * 0.5 * self.prev_geometry[2]) + self.prev_geometry[0]
                            y = int((1 - ndc[1]) * 0.5 * self.prev_geometry[3]) + self.prev_geometry[1]
                            
                            if (self.prev_geometry[0] <= x <= self.prev_geometry[0] + self.prev_geometry[2] and 
                                self.prev_geometry[1] <= y <= self.prev_geometry[1] + self.prev_geometry[3]):
                                try:
                                    color = esp_colors[idx] if idx < len(esp_colors) else 'white'
                                except IndexError:
                                    color = 'white'
                                self.plr_data.append((x, y, color))

                # Solo actualizar si hay cambios significativos
                if self.has_significant_changes():
                    self.clear_tracers()
                    self.draw_tracers()
                    self.prev_plr_data = self.plr_data.copy()
                else:
                    # Solo redibujar sin borrar para mantener estabilidad
                    self.draw_tracers_overlay()

            except Exception:
                pass

            time.sleep(0.002)  # ~500 FPS para tracking ultra-instantáneo

    def clear_tracers(self):
        """Borrar ESP anteriores - optimizado para velocidad máxima"""
        global esp_box_enabled, esp_tracers_enabled
        if not self.hdc_screen or not self.prev_plr_data:
            return
            
        # Borrado ultra-rápido
        pen = windll.gdi32.CreatePen(0, 2, 0x0000FF00)
        old_pen = windll.gdi32.SelectObject(self.hdc_screen, pen)
        windll.gdi32.SetROP2(self.hdc_screen, 7)  # R2_XORPEN
        
        # Borrar cajas si estaban habilitadas
        if esp_box_enabled:
            for x, y, color in self.prev_plr_data:
                # Tamaño de la caja (debe coincidir con draw_tracers)
                box_width = 40
                box_height = 60
                
                # Calcular esquinas de la caja
                left = int(x - box_width // 2)
                right = int(x + box_width // 2)
                top = int(y - box_height // 2)
                bottom = int(y + box_height // 2)
                
                # Borrar rectángulo (4 líneas)
                # Línea superior
                windll.gdi32.MoveToEx(self.hdc_screen, left, top, None)
                windll.gdi32.LineTo(self.hdc_screen, right, top)
                
                # Línea derecha
                windll.gdi32.MoveToEx(self.hdc_screen, right, top, None)
                windll.gdi32.LineTo(self.hdc_screen, right, bottom)
                
                # Línea inferior
                windll.gdi32.MoveToEx(self.hdc_screen, right, bottom, None)
                windll.gdi32.LineTo(self.hdc_screen, left, bottom)
                
                # Línea izquierda
                windll.gdi32.MoveToEx(self.hdc_screen, left, bottom, None)
                windll.gdi32.LineTo(self.hdc_screen, left, top)
        
        # Borrar líneas tracers si estaban habilitadas
        if esp_tracers_enabled:
            start_x = int(self.start_line_x)
            start_y = int(self.start_line_y)
            
            for x, y, color in self.prev_plr_data:
                windll.gdi32.MoveToEx(self.hdc_screen, start_x, start_y, None)
                windll.gdi32.LineTo(self.hdc_screen, int(x), int(y))
        
        # Limpiar recursos
        windll.gdi32.SelectObject(self.hdc_screen, old_pen)
        windll.gdi32.DeleteObject(pen)

    def draw_tracers(self):
        """Dibujar ESP - optimizado para velocidad máxima"""
        global esp_box_enabled, esp_tracers_enabled
        if not self.hdc_screen or not self.plr_data:
            return
            
        # Crear pen una sola vez y reutilizar
        pen = windll.gdi32.CreatePen(0, 2, 0x0000FF00)
        old_pen = windll.gdi32.SelectObject(self.hdc_screen, pen)
        windll.gdi32.SetROP2(self.hdc_screen, 7)  # R2_XORPEN
        
        # Dibujar cajas solo si están habilitadas
        if esp_box_enabled:
            for x, y, color in self.plr_data:
                # Tamaño de la caja (ajustable)
                box_width = 40
                box_height = 60
                
                # Calcular esquinas de la caja
                left = int(x - box_width // 2)
                right = int(x + box_width // 2)
                top = int(y - box_height // 2)
                bottom = int(y + box_height // 2)
                
                # Dibujar rectángulo (4 líneas)
                # Línea superior
                windll.gdi32.MoveToEx(self.hdc_screen, left, top, None)
                windll.gdi32.LineTo(self.hdc_screen, right, top)
                
                # Línea derecha
                windll.gdi32.MoveToEx(self.hdc_screen, right, top, None)
                windll.gdi32.LineTo(self.hdc_screen, right, bottom)
                
                # Línea inferior
                windll.gdi32.MoveToEx(self.hdc_screen, right, bottom, None)
                windll.gdi32.LineTo(self.hdc_screen, left, bottom)
                
                # Línea izquierda
                windll.gdi32.MoveToEx(self.hdc_screen, left, bottom, None)
                windll.gdi32.LineTo(self.hdc_screen, left, top)
        
        # Dibujar líneas tracers solo si están habilitadas
        if esp_tracers_enabled:
            start_x = int(self.start_line_x)
            start_y = int(self.start_line_y)
            
            for x, y, color in self.plr_data:
                windll.gdi32.MoveToEx(self.hdc_screen, start_x, start_y, None)
                windll.gdi32.LineTo(self.hdc_screen, int(x), int(y))
        
        # Limpiar recursos
        windll.gdi32.SelectObject(self.hdc_screen, old_pen)
        windll.gdi32.DeleteObject(pen)

    def has_significant_changes(self):
        """Detectar si hay cambios significativos en las posiciones"""
        if len(self.plr_data) != len(self.prev_plr_data):
            return True
        
        # Verificar si las posiciones han cambiado significativamente
        for i, (x, y, color) in enumerate(self.plr_data):
            if i < len(self.prev_plr_data):
                prev_x, prev_y, prev_color = self.prev_plr_data[i]
                if abs(x - prev_x) > 5 or abs(y - prev_y) > 5:  # Cambio de más de 5 píxeles
                    return True
        return False

    def draw_tracers_overlay(self):
        """Dibujar ESP overlay - ultra-rápido"""
        global esp_box_enabled, esp_tracers_enabled
        if not self.hdc_screen or not self.plr_data:
            return
            
        # Overlay ultra-rápido
        pen = windll.gdi32.CreatePen(0, 1, 0x0000FF00)
        old_pen = windll.gdi32.SelectObject(self.hdc_screen, pen)
        windll.gdi32.SetROP2(self.hdc_screen, 13)  # R2_COPYPEN
        
        # Dibujar cajas overlay solo si están habilitadas
        if esp_box_enabled:
            for x, y, color in self.plr_data:
                # Tamaño de la caja (debe coincidir con draw_tracers)
                box_width = 40
                box_height = 60
                
                # Calcular esquinas de la caja
                left = int(x - box_width // 2)
                right = int(x + box_width // 2)
                top = int(y - box_height // 2)
                bottom = int(y + box_height // 2)
                
                # Dibujar rectángulo (4 líneas)
                # Línea superior
                windll.gdi32.MoveToEx(self.hdc_screen, left, top, None)
                windll.gdi32.LineTo(self.hdc_screen, right, top)
                
                # Línea derecha
                windll.gdi32.MoveToEx(self.hdc_screen, right, top, None)
                windll.gdi32.LineTo(self.hdc_screen, right, bottom)
                
                # Línea inferior
                windll.gdi32.MoveToEx(self.hdc_screen, right, bottom, None)
                windll.gdi32.LineTo(self.hdc_screen, left, bottom)
                
                # Línea izquierda
                windll.gdi32.MoveToEx(self.hdc_screen, left, bottom, None)
                windll.gdi32.LineTo(self.hdc_screen, left, top)
        
        # Dibujar líneas tracers overlay solo si están habilitadas
        if esp_tracers_enabled:
            start_x = int(self.start_line_x)
            start_y = int(self.start_line_y)
            
            for x, y, color in self.plr_data:
                windll.gdi32.MoveToEx(self.hdc_screen, start_x, start_y, None)
                windll.gdi32.LineTo(self.hdc_screen, int(x), int(y))
        
        # Limpiar recursos
        windll.gdi32.SelectObject(self.hdc_screen, old_pen)
        windll.gdi32.DeleteObject(pen)

    def stop(self):
        self.running = False
        self.clear_tracers()
        if self.hdc_screen:
            windll.user32.ReleaseDC(0, self.hdc_screen)


def background_process_monitor():
    global baseAddr
    while True:
        try:
            if is_process_dead():
                # Limpiar recursos cuando el proceso muere
                cleanup_resources()
                while not yield_for_program("RobloxPlayerBeta.exe"):
                    time.sleep(0.5)
                baseAddr = get_base_addr()
        except Exception:
            # Si hay cualquier error, limpiar recursos
            cleanup_resources()
        time.sleep(0.1)

threading.Thread(target=background_process_monitor, daemon=True).start()

def init():
    global dataModel, wsAddr, camAddr, camCFrameRotAddr, plrsAddr, lpAddr, matrixAddr, camPosAddr, injected
    
    # Verificar que Roblox esté ejecutándose
    if is_process_dead():
        print("Roblox is not running! Please start Roblox first.")
        try:
            import tkinter as tk
            from tkinter import messagebox
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror("Process Not Found", "Roblox is not running!\n\nPlease start Roblox and try again.")
            root.destroy()
        except:
            pass
        return
    
    try:
        fakeDatamodel = pm.read_longlong(baseAddr + int(offsets['FakeDataModelPointer'], 16))
        dataModel = pm.read_longlong(fakeDatamodel + int(offsets['FakeDataModelToDataModel'], 16))
        
        wsAddr = pm.read_longlong(dataModel + int(offsets['Workspace'], 16))
        camAddr = pm.read_longlong(wsAddr + int(offsets['Camera'], 16))
        camCFrameRotAddr = camAddr + int(offsets['CameraRotation'], 16)
        camPosAddr = camAddr + int(offsets['CameraPos'], 16)
        visualEngine = pm.read_longlong(baseAddr + int(offsets['VisualEnginePointer'], 16))
        matrixAddr = visualEngine + int(offsets['viewmatrix'], 16)
        plrsAddr = FindFirstChildOfClass(dataModel, 'Players')
        lpAddr = pm.read_longlong(plrsAddr + int(offsets['LocalPlayer'], 16))
        
        injected = True
        dpg.delete_item("Injector Window")
        dpg.show_item("Primary Window")
        
    except Exception as e:
        
        # Show error in GUI
        try:
            import tkinter as tk
            from tkinter import messagebox
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror("Injection Failed", 
                               f"Failed to inject into Roblox.\n\n"
                               f"Error: {str(e)}\n\n"
                               f"Solutions:\n"
                               f"1. Make sure Roblox is running\n"
                               f"2. Restart Roblox and try again\n"
                               f"3. Check if offsets are updated")
            root.destroy()
        except:
            pass
        return

# ESP Callback Functions
def esp_visuals_callback(sender, app_data):
    global esp_enabled, esp_thread, offsets
    if not injected:
        return
    esp_enabled = app_data
    
    if esp_enabled and not esp_thread:
        esp_thread = ESPThread(pm, baseAddr, offsets)
        esp_thread.start()
    elif not esp_enabled and esp_thread:
        esp_thread.stop()
        esp_thread = None

def esp_team_check_callback(sender, app_data):
    global esp_team_check
    esp_team_check = app_data

def esp_death_check_callback(sender, app_data):
    global esp_death_check
    esp_death_check = app_data

def esp_tracers_callback(sender, app_data):
    global esp_tracers_enabled
    esp_tracers_enabled = app_data

def esp_box_callback(sender, app_data):
    global esp_box_enabled
    esp_box_enabled = app_data

# Fly Callback Functions
def fly_callback(sender, app_data):
    global fly_enabled, fly_thread, offsets
    if not injected:
        return
    fly_enabled = app_data
    
    if fly_enabled and not fly_thread:
        fly_thread = FlyThread(pm, baseAddr, offsets)
        fly_thread.start()
    elif not fly_enabled and fly_thread:
        fly_thread.stop()
        fly_thread = None

def fly_keybind_callback():
    global waiting_for_keybind
    if not waiting_for_keybind:
        waiting_for_keybind = True
        dpg.configure_item("fly_keybind_button", label="... (ESC to cancel)")

def fly_speed_callback(sender, app_data):
    global fly_speed
    fly_speed = float(app_data)

def fly_method_callback(sender, app_data):
    global fly_method
    fly_method = 0 if app_data == "Position" else 1

def set_fly_mode(mode):
    global fly_mode, fly_toggled
    fly_mode = mode
    fly_toggled = False
    dpg.configure_item("fly_keybind_button", label=f"{get_key_name(fly_keybind)} ({fly_mode})")
    dpg.hide_item("fly_mode_popup")

def keybind_listener():
    global waiting_for_keybind, aimbot_keybind, triggerbot_keybind, rotation_360_keybind, fly_keybind
    while True:
        if waiting_for_keybind:
            time.sleep(0.3)
            for vk_code in range(1, 256):
                windll.user32.GetAsyncKeyState(vk_code)
            key_found = False
            while waiting_for_keybind and not key_found:
                for vk_code in range(1, 256):
                    if windll.user32.GetAsyncKeyState(vk_code) & 0x8000:
                        if vk_code == 27:
                            waiting_for_keybind = False
                            try:
                                dpg.configure_item("keybind_button", label=f"{get_key_name(aimbot_keybind)}")
                            except:
                                pass
                            try:
                                dpg.configure_item("triggerbot_keybind_button", label=f"{get_key_name(triggerbot_keybind)}")
                            except:
                                pass
                            try:
                                dpg.configure_item("rotation_360_keybind_button", label=f"{get_key_name(rotation_360_keybind)}")
                            except:
                                pass
                            try:
                                dpg.configure_item("fly_keybind_button", label=f"{get_key_name(fly_keybind)}")
                            except:
                                pass
                            break
                        try:
                            if "..." in dpg.get_item_label("keybind_button"):
                                aimbot_keybind = vk_code
                                dpg.configure_item("keybind_button", label=f"{get_key_name(vk_code)}")
                        except:
                            pass
                        try:
                            if "..." in dpg.get_item_label("triggerbot_keybind_button"):
                                triggerbot_keybind = vk_code
                                dpg.configure_item("triggerbot_keybind_button", label=f"{get_key_name(vk_code)}")
                        except:
                            pass
                        try:
                            if "..." in dpg.get_item_label("rotation_360_keybind_button"):
                                rotation_360_keybind = vk_code
                                dpg.configure_item("rotation_360_keybind_button", label=f"{get_key_name(vk_code)}")
                        except:
                            pass
                        try:
                            if "..." in dpg.get_item_label("fly_keybind_button"):
                                fly_keybind = vk_code
                                dpg.configure_item("fly_keybind_button", label=f"{get_key_name(vk_code)}")
                        except:
                            pass
                        waiting_for_keybind = False
                        key_found = True
                        break
                time.sleep(0.01)
        else:
            time.sleep(0.1)

threading.Thread(target=keybind_listener, daemon=True).start()

def aimbotLoop():
    global target, aimbot_toggled
    key_pressed_last_frame = False
    
    while True:
        if aimbot_enabled:
            key_pressed_this_frame = windll.user32.GetAsyncKeyState(aimbot_keybind) & 0x8000 != 0
            
            if aimbot_mode == "Toggle":
                if key_pressed_this_frame and not key_pressed_last_frame:
                    aimbot_toggled = not aimbot_toggled
                key_pressed_last_frame = key_pressed_this_frame
                should_aim = aimbot_toggled
            else:
                should_aim = key_pressed_this_frame
                
            if should_aim:
                # Verificar que Roblox esté en foco antes de mover el mouse
                hwnd_roblox = find_window_by_title("Roblox")
                hwnd_foreground = windll.user32.GetForegroundWindow()
                
                if hwnd_roblox and hwnd_roblox == hwnd_foreground and target > 0 and matrixAddr > 0:
                    try:
                        from_pos = [pm.read_float(camPosAddr), pm.read_float(camPosAddr+4), pm.read_float(camPosAddr+8)]
                        to_pos = [pm.read_float(target), pm.read_float(target+4), pm.read_float(target+8)]
                        
                        # Predicción
                        if aimbot_prediction_enabled:
                            try:
                                vel_addr = target - int(offsets['Position'], 16) + int(offsets['Velocity'], 16)
                                velocity = [pm.read_float(vel_addr), pm.read_float(vel_addr+4), pm.read_float(vel_addr+8)]
                                to_pos[0] += velocity[0] * aimbot_prediction_x
                                to_pos[1] += velocity[1] * aimbot_prediction_y
                            except:
                                pass
                        
                        if aimbot_type == "Mouse":
                            # Método de mouse - Convertir posición 3D a coordenadas de pantalla
                            left, top, right, bottom = get_client_rect_on_screen(hwnd_roblox)
                            width = right - left
                            height = bottom - top
                            
                            matrix_flat = [pm.read_float(matrixAddr + i * 4) for i in range(16)]
                            view_proj_matrix = reshape(array(matrix_flat, dtype=float32), (4, 4))
                            
                            screen_coords = world_to_screen_with_matrix(to_pos, view_proj_matrix, width, height)
                            if screen_coords is not None:
                                # Calcular diferencia desde el centro de la pantalla
                                center_x = width / 2
                                center_y = height / 2
                                
                                diff_x = screen_coords[0] - center_x
                                diff_y = screen_coords[1] - center_y
                                
                                # Arreglar el problema de la "zona muerta"
                                if aimbot_smoothness_enabled:
                                    # Smoothness más suave para mouse
                                    smooth_factor_x = 1.0 / max(1.0, aimbot_smoothness_x)
                                    smooth_factor_y = 1.0 / max(1.0, aimbot_smoothness_y)
                                    
                                    # Aplicar smoothness manteniendo precisión decimal
                                    smooth_x = diff_x * smooth_factor_x
                                    smooth_y = diff_y * smooth_factor_y
                                    
                                    # Convertir a entero pero asegurar movimiento mínimo si hay diferencia
                                    if abs(smooth_x) >= 0.5:
                                        move_x = int(smooth_x + (0.5 if smooth_x > 0 else -0.5))
                                    else:
                                        move_x = 1 if smooth_x > 0.1 else (-1 if smooth_x < -0.1 else 0)
                                    
                                    if abs(smooth_y) >= 0.5:
                                        move_y = int(smooth_y + (0.5 if smooth_y > 0 else -0.5))
                                    else:
                                        move_y = 1 if smooth_y > 0.1 else (-1 if smooth_y < -0.1 else 0)
                                else:
                                    # Sin smoothness - movimiento directo pero con redondeo inteligente
                                    move_x = int(diff_x + (0.5 if diff_x > 0 else -0.5)) if abs(diff_x) >= 0.5 else (1 if diff_x > 0.1 else (-1 if diff_x < -0.1 else 0))
                                    move_y = int(diff_y + (0.5 if diff_y > 0 else -0.5)) if abs(diff_y) >= 0.5 else (1 if diff_y > 0.1 else (-1 if diff_y < -0.1 else 0))
                                
                                # Añadir shake si está habilitado
                                if aimbot_shake_enabled:
                                    shake_x = random.uniform(-aimbot_shake_strength * 50, aimbot_shake_strength * 50)
                                    shake_y = random.uniform(-aimbot_shake_strength * 50, aimbot_shake_strength * 50)
                                    move_x += int(shake_x)
                                    move_y += int(shake_y)
                                
                                # Mover el mouse incluso con movimientos pequeños
                                if move_x != 0 or move_y != 0:
                                    windll.user32.mouse_event(0x0001, move_x, move_y, 0, 0)  # MOUSEEVENTF_MOVE
                        
                        elif aimbot_type == "Silent Aim/flick (BETA)":
                            # Método Silent Aim - Solo actúa cuando disparas
                            # Detectar si se está presionando el botón de disparo
                            left_click_pressed = windll.user32.GetAsyncKeyState(0x01) & 0x8000 != 0  # VK_LBUTTON
                            
                            if left_click_pressed:
                                # Guardar rotación original de la cámara
                                original_rotation = []
                                for i in range(9):
                                    addr = camCFrameRotAddr + (i % 3) * 4 + (i // 3) * 12
                                    original_rotation.append(pm.read_float(addr))
                                
                                # Calcular rotación hacia el objetivo
                                look, up, right = cframe_look_at(from_pos, to_pos)
                                
                                # Aplicar rotación hacia el objetivo instantáneamente
                                target_rotation = [-right[0], up[0], -look[0], -right[1], up[1], -look[1], -right[2], up[2], -look[2]]
                                
                                # Añadir shake si está habilitado (muy sutil para silent aim)
                                if aimbot_shake_enabled:
                                    for i in range(9):
                                        shake = random.uniform(-aimbot_shake_strength * 0.1, aimbot_shake_strength * 0.1)
                                        target_rotation[i] += shake
                                
                                # Aplicar la rotación hacia el objetivo
                                for i, val in enumerate(target_rotation):
                                    addr = camCFrameRotAddr + (i % 3) * 4 + (i // 3) * 12
                                    pm.write_float(addr, float(val))
                                
                                # Esperar un frame para que el juego procese el disparo
                                time.sleep(0.001)
                                
                                # Restaurar rotación original inmediatamente
                                for i, val in enumerate(original_rotation):
                                    addr = camCFrameRotAddr + (i % 3) * 4 + (i // 3) * 12
                                    pm.write_float(addr, float(val))
                            
                            # Si no se está disparando, no hacer nada (mantener aim natural)
                        
                        else:
                            # Método de cámara - Manipulación directa (método original)
                            look, up, right = cframe_look_at(from_pos, to_pos)
                            
                            if aimbot_smoothness_enabled:
                                # Smoothness estándar como external normal
                                smooth_factor_x = 1.0 / max(1.0, aimbot_smoothness_x)
                                smooth_factor_y = 1.0 / max(1.0, aimbot_smoothness_y)
                                
                                # Leer rotación actual
                                current_rot = []
                                for i in range(9):
                                    addr = camCFrameRotAddr + (i % 3) * 4 + (i // 3) * 12
                                    current_rot.append(pm.read_float(addr))
                                
                                # Aplicar smoothness
                                target_rot = [-right[0], up[0], -look[0], -right[1], up[1], -look[1], -right[2], up[2], -look[2]]
                                
                                for i in range(9):
                                    smooth_factor = smooth_factor_x if i % 3 != 1 else smooth_factor_y
                                    new_val = current_rot[i] + (target_rot[i] - current_rot[i]) * smooth_factor
                                    
                                    if aimbot_shake_enabled:
                                        new_val += random.uniform(-aimbot_shake_strength, aimbot_shake_strength)
                                    
                                    addr = camCFrameRotAddr + (i % 3) * 4 + (i // 3) * 12
                                    pm.write_float(addr, float(new_val))
                            else:
                                # Sin smoothness - aplicar directamente
                                rotation_values = [-right[0], up[0], -look[0], -right[1], up[1], -look[1], -right[2], up[2], -look[2]]
                                for i, val in enumerate(rotation_values):
                                    if aimbot_shake_enabled:
                                        val += random.uniform(-aimbot_shake_strength, aimbot_shake_strength)
                                    
                                    addr = camCFrameRotAddr + (i % 3) * 4 + (i // 3) * 12
                                    pm.write_float(addr, float(val))
                                
                    except Exception:
                        target = 0
                elif hwnd_roblox and hwnd_roblox == hwnd_foreground:
                    # Búsqueda de objetivo optimizada (solo si Roblox está activo)
                    target = 0
                    try:
                        if hwnd_roblox and matrixAddr > 0:
                            left, top, right, bottom = get_client_rect_on_screen(hwnd_roblox)
                            width = right - left
                            height = bottom - top
                            
                            if width > 100 and height > 100:
                                widthCenter = width * 0.5
                                heightCenter = height * 0.5
                                
                                matrix_flat = [pm.read_float(matrixAddr + i * 4) for i in range(16)]
                                view_proj_matrix = reshape(array(matrix_flat, dtype=float32), (4, 4))
                                
                                lpTeam = pm.read_longlong(lpAddr + int(offsets['Team'], 16))
                                minDistance = float('inf')
                                
                                players = GetChildren(plrsAddr)
                                # Limitar a menos jugadores para reducir lag
                                for v in players[:min(len(players), 15)]:
                                    if v == lpAddr:
                                        continue
                                        
                                    try:
                                        if aimbot_ignoreteam:
                                            player_team = pm.read_longlong(v + int(offsets['Team'], 16))
                                            if player_team == lpTeam:
                                                continue
                                        
                                        char = pm.read_longlong(v + int(offsets['ModelInstance'], 16))
                                        if not char:
                                            continue
                                        
                                        if aimbot_ignoredead:
                                            hum = FindFirstChildOfClass(char, 'Humanoid')
                                            if hum:
                                                health = pm.read_float(hum + int(offsets['Health'], 16))
                                                if health <= 5:
                                                    continue
                                        
                                        # Buscar múltiples hitparts para mayor compatibilidad
                                        body_parts = [aimbot_hitpart, 'Head', 'Torso', 'UpperTorso', 'HumanoidRootPart']
                                        
                                        hitpart_found = False
                                        for part_name in body_parts:
                                            if hitpart_found:
                                                break
                                            hitpart = FindFirstChild(char, part_name)
                                            if hitpart:
                                                primitive = pm.read_longlong(hitpart + int(offsets['Primitive'], 16))
                                                if primitive:
                                                    targetPos = primitive + int(offsets['Position'], 16)
                                                    obj_pos = [pm.read_float(targetPos), pm.read_float(targetPos + 4), pm.read_float(targetPos + 8)]
                                                    
                                                    if aimbot_prediction_enabled:
                                                        try:
                                                            vel_addr = primitive + int(offsets['Velocity'], 16)
                                                            velocity = [pm.read_float(vel_addr), pm.read_float(vel_addr + 4), pm.read_float(vel_addr + 8)]
                                                            obj_pos[0] += velocity[0] * aimbot_prediction_x
                                                            obj_pos[1] += velocity[1] * aimbot_prediction_y
                                                        except:
                                                            pass
                                                    
                                                    screen_coords = world_to_screen_with_matrix(obj_pos, view_proj_matrix, width, height)
                                                    if screen_coords is not None:
                                                        distance = sqrt((widthCenter - screen_coords[0])**2 + (heightCenter - screen_coords[1])**2)
                                                        # Usar FOV del aimbot
                                                        if distance <= aimbot_fov and distance < minDistance:
                                                            minDistance = distance
                                                            target = targetPos
                                                            hitpart_found = True
                                    except:
                                        continue
                    except:
                        target = 0
                else:
                    # Roblox no está en foco, limpiar target
                    target = 0
            else:
                aimbot_toggled = False
                target = 0
        else:
            aimbot_toggled = False
            time.sleep(0.01)
            continue
        
        time.sleep(0.005)  # Timing optimizado para reducir lag

threading.Thread(target=aimbotLoop, daemon=True).start()

def rotation360Loop():
    global rotation_360_in_progress, rotation_360_toggled, rotation_360_active, rotation_360_alternate_direction
    key_pressed_last_frame = False
    while True:
        if rotation_360_enabled and injected and camCFrameRotAddr > 0:
            key_pressed_this_frame = windll.user32.GetAsyncKeyState(rotation_360_keybind) & 0x8000 != 0
            
            # Manejar modo Hold/Toggle
            if rotation_360_mode == "Toggle":
                if key_pressed_this_frame and not key_pressed_last_frame:
                    rotation_360_toggled = not rotation_360_toggled
                    rotation_360_active = True
                elif not key_pressed_this_frame:
                    rotation_360_active = False
                should_rotate = rotation_360_toggled
            else:  # Hold mode
                should_rotate = key_pressed_this_frame
            
            if should_rotate and not rotation_360_in_progress:
                rotation_360_in_progress = True
                
                # Determinar dirección según el modo
                if rotation_360_direction_mode == "Mode 2":
                    # Mode 2: Alternar dirección
                    clockwise = not rotation_360_alternate_direction
                    rotation_360_alternate_direction = not rotation_360_alternate_direction
                else:
                    # Mode 1: Siempre izquierda a derecha (clockwise)
                    clockwise = True
                
                # Leer la rotación actual de la cámara para obtener el yaw inicial
                try:
                    # Leer los vectores de rotación actuales
                    current_right = [pm.read_float(camCFrameRotAddr), pm.read_float(camCFrameRotAddr + 12), pm.read_float(camCFrameRotAddr + 24)]
                    current_look = [pm.read_float(camCFrameRotAddr + 8), pm.read_float(camCFrameRotAddr + 20), pm.read_float(camCFrameRotAddr + 32)]
                    
                    # Calcular el yaw actual desde el vector look
                    import math
                    initial_yaw = math.atan2(current_look[0], current_look[2])
                    
                    # Normalizar el yaw inicial
                    if initial_yaw < 0:
                        initial_yaw += 2 * pi
                        
                    rotation_progress = 0.0
                    target_rotation = 2 * pi  # 360 grados
                    
                    while rotation_progress < target_rotation and rotation_360_in_progress:
                        try:
                            rotation_progress += rotation_360_speed * pi180
                            if rotation_progress >= target_rotation:
                                rotation_progress = target_rotation
                                rotation_360_in_progress = False
                            
                            # Calcular el yaw actual basado en la dirección
                            if clockwise:
                                current_yaw = initial_yaw + rotation_progress
                            else:
                                current_yaw = initial_yaw - rotation_progress
                            
                            # Crear los vectores de rotación
                            right = [cos(current_yaw), 0, -sin(current_yaw)]
                            up = [0, 1, 0]
                            look = [sin(current_yaw), 0, cos(current_yaw)]
                            
                            # Aplicar la rotación
                            for i in range(3):
                                pm.write_float(camCFrameRotAddr + i*12, float(right[i]))
                                pm.write_float(camCFrameRotAddr + 4 + i*12, float(up[i]))
                                pm.write_float(camCFrameRotAddr + 8 + i*12, float(look[i]))
                            time.sleep(0.001)
                        except Exception:
                            rotation_360_in_progress = False
                            break
                except Exception:
                    rotation_360_in_progress = False
                    
            key_pressed_last_frame = key_pressed_this_frame
            if not rotation_360_in_progress:
                time.sleep(0.1)
        else:
            rotation_360_in_progress = False
            time.sleep(0.1)

threading.Thread(target=rotation360Loop, daemon=True).start()

def triggerbotLoop():
    global triggerbot_enabled, triggerbot_toggled
    key_pressed_last_frame = False
    last_valid_pos = [0.0, 0.0, 0.0]
    locked_target = None

    while True:
        if triggerbot_enabled and injected and lpAddr > 0 and plrsAddr > 0 and matrixAddr > 0:
            try:
                hwnd_roblox = find_window_by_title("Roblox")
                if not hwnd_roblox:
                    time.sleep(0.0005)
                    continue

                left, top, right, bottom = get_client_rect_on_screen(hwnd_roblox)
                width = right - left
                height = bottom - top
                widthCenter = width / 2
                heightCenter = height / 2
                matrix_flat = [pm.read_float(matrixAddr + i * 4) for i in range(16)]
                view_proj_matrix = reshape(array(matrix_flat, dtype=float32), (4, 4))
                key_pressed_this_frame = windll.user32.GetAsyncKeyState(triggerbot_keybind) & 0x8000 != 0

                if triggerbot_mode == "Toggle":
                    if key_pressed_this_frame and not key_pressed_last_frame:
                        triggerbot_toggled = not triggerbot_toggled
                    key_pressed_last_frame = key_pressed_this_frame
                    should_trigger = triggerbot_toggled
                else:
                    should_trigger = key_pressed_this_frame

                if should_trigger:
                    if locked_target is None:
                        # Find target based on detection mode
                        lpTeam = pm.read_longlong(lpAddr + int(offsets['Team'], 16))
                        
                        if triggerbot_detection_mode == "Hitpart (R15)":
                            # Modo Hitpart: Detectar cualquier hitpart visible sin FOV
                            for v in GetChildren(plrsAddr):
                                if v != lpAddr:
                                    try:
                                        if aimbot_ignoreteam:
                                            playerTeam = pm.read_longlong(v + int(offsets['Team'], 16))
                                            if playerTeam == lpTeam:
                                                continue
                                        char = pm.read_longlong(v + int(offsets['ModelInstance'], 16))
                                        if char:
                                            if aimbot_ignoredead:
                                                hum = FindFirstChildOfClass(char, 'Humanoid')
                                                if hum:
                                                    health = pm.read_float(hum + int(offsets['Health'], 16))
                                                    if health <= 5:
                                                        continue
                                            body_parts = ['Head', 'Torso', 'UpperTorso', 'LowerTorso', 'HumanoidRootPart',
                                                         'LeftArm', 'RightArm', 'LeftLeg', 'RightLeg',
                                                         'LeftHand', 'RightHand', 'LeftFoot', 'RightFoot',
                                                         'LeftUpperArm', 'RightUpperArm', 'LeftLowerArm', 'RightLowerArm',
                                                         'LeftUpperLeg', 'RightUpperLeg', 'LeftLowerLeg', 'RightLowerLeg']
                                            for part_name in body_parts:
                                                part = FindFirstChild(char, part_name)
                                                if part:
                                                    primitive = pm.read_longlong(part + int(offsets['Primitive'], 16))
                                                    if primitive:
                                                        targetPos = primitive + int(offsets['Position'], 16)
                                                        obj_pos = [
                                                            pm.read_float(targetPos),
                                                            pm.read_float(targetPos + 4),
                                                            pm.read_float(targetPos + 8)
                                                        ]
                                                        
                                                        # Aplicar predicción
                                                        try:
                                                            vel_addr = primitive + int(offsets['Velocity'], 16)
                                                            velocity = [pm.read_float(vel_addr), pm.read_float(vel_addr + 4), pm.read_float(vel_addr + 8)]
                                                            obj_pos[0] += velocity[0] * (triggerbot_prediction_x * 0.01)
                                                            obj_pos[1] += velocity[1] * (triggerbot_prediction_y * 0.01)
                                                        except:
                                                            pass
                                                        
                                                        obj_pos = array(obj_pos, dtype=float32)
                                                        screen_coords = world_to_screen_with_matrix(obj_pos, view_proj_matrix, width, height)
                                                        # Verificar que esté visible y cerca del cursor (precisión por defecto)
                                                        if screen_coords is not None:
                                                            # Usar precisión más grande para todas las partes
                                                            if part_name == "Head":
                                                                hitpart_precision = 45.0  # pixels más grandes para cabeza
                                                            elif part_name in ["Torso", "UpperTorso", "LowerTorso", "HumanoidRootPart"]:
                                                                hitpart_precision = 40.0  # pixels grandes para torso
                                                            elif part_name in ["LeftArm", "RightArm", "LeftLeg", "RightLeg"]:
                                                                hitpart_precision = 35.0  # pixels para brazos y piernas
                                                            else:
                                                                hitpart_precision = 30.0  # pixels de precisión por defecto para otras partes
                                                            distance = sqrt((widthCenter - screen_coords[0])**2 + (heightCenter - screen_coords[1])**2)
                                                            if distance <= hitpart_precision:
                                                                locked_target = (primitive, targetPos, part_name)
                                                                break
                                            if locked_target:
                                                break
                                    except:
                                        continue
                        
                        elif triggerbot_detection_mode == "Hitpart (R6)":
                            # Modo Hitpart (R6): Solo las 6 partes válidas de R6
                            for v in GetChildren(plrsAddr):
                                if v != lpAddr:
                                    try:
                                        if aimbot_ignoreteam:
                                            playerTeam = pm.read_longlong(v + int(offsets['Team'], 16))
                                            if playerTeam == lpTeam:
                                                continue
                                        char = pm.read_longlong(v + int(offsets['ModelInstance'], 16))
                                        if char:
                                            if aimbot_ignoredead:
                                                hum = FindFirstChildOfClass(char, 'Humanoid')
                                                if hum:
                                                    health = pm.read_float(hum + int(offsets['Health'], 16))
                                                    if health <= 5:
                                                        continue
                                            
                                            # Solo las partes que realmente existen en R6
                                            body_parts_r6 = ['Head', 'Torso', 'Left Arm', 'Right Arm', 'Left Leg', 'Right Leg']
                                            
                                            for part_name in body_parts_r6:
                                                part = FindFirstChild(char, part_name)
                                                if part:
                                                    primitive = pm.read_longlong(part + int(offsets['Primitive'], 16))
                                                    if primitive:
                                                        targetPos = primitive + int(offsets['Position'], 16)
                                                        obj_pos = [
                                                            pm.read_float(targetPos),
                                                            pm.read_float(targetPos + 4),
                                                            pm.read_float(targetPos + 8)
                                                        ]
                                                        
                                                        # Predicción de movimiento
                                                        try:
                                                            vel_addr = primitive + int(offsets['Velocity'], 16)
                                                            velocity = [
                                                                pm.read_float(vel_addr),
                                                                pm.read_float(vel_addr + 4),
                                                                pm.read_float(vel_addr + 8)
                                                            ]
                                                            obj_pos[0] += velocity[0] * (triggerbot_prediction_x * 0.01)
                                                            obj_pos[1] += velocity[1] * (triggerbot_prediction_y * 0.01)
                                                        except:
                                                            pass
                                                        
                                                        obj_pos = array(obj_pos, dtype=float32)
                                                        screen_coords = world_to_screen_with_matrix(obj_pos, view_proj_matrix, width, height)
                                                        if screen_coords is not None:
                                                            # Precisión ajustada por tamaño de parte
                                                            if part_name == "Head":
                                                                r6_precision = 35.0
                                                            elif part_name == "Torso":
                                                                r6_precision = 50.0
                                                            else:  # brazos y piernas
                                                                r6_precision = 40.0
                                                            
                                                            distance = sqrt((widthCenter - screen_coords[0])**2 + (heightCenter - screen_coords[1])**2)
                                                            if distance <= r6_precision:
                                                                locked_target = (primitive, targetPos, part_name)
                                                                break
                                            if locked_target:
                                                break
                                    except:
                                        continue

                        else:
                            # Modo Default: Usar FOV circular (comportamiento original)
                            minDistance = float('inf')
                            for v in GetChildren(plrsAddr):
                                if v != lpAddr:
                                    try:
                                        if aimbot_ignoreteam:
                                            playerTeam = pm.read_longlong(v + int(offsets['Team'], 16))
                                            if playerTeam == lpTeam:
                                                continue
                                        char = pm.read_longlong(v + int(offsets['ModelInstance'], 16))
                                        if char:
                                            if aimbot_ignoredead:
                                                hum = FindFirstChildOfClass(char, 'Humanoid')
                                                if hum:
                                                    health = pm.read_float(hum + int(offsets['Health'], 16))
                                                    if health <= 5:
                                                        continue
                                            body_parts = ['Head', 'Torso', 'UpperTorso', 'LowerTorso', 'HumanoidRootPart',
                                                         'LeftArm', 'RightArm', 'LeftLeg', 'RightLeg',
                                                         'LeftHand', 'RightHand', 'LeftFoot', 'RightFoot',
                                                         'LeftUpperArm', 'RightUpperArm', 'LeftLowerArm', 'RightLowerArm',
                                                         'LeftUpperLeg', 'RightUpperLeg', 'LeftLowerLeg', 'RightLowerLeg']
                                            for part_name in body_parts:
                                                part = FindFirstChild(char, part_name)
                                                if part:
                                                    primitive = pm.read_longlong(part + int(offsets['Primitive'], 16))
                                                    if primitive:
                                                        targetPos = primitive + int(offsets['Position'], 16)
                                                        obj_pos = [
                                                            pm.read_float(targetPos),
                                                            pm.read_float(targetPos + 4),
                                                            pm.read_float(targetPos + 8)
                                                        ]
                                                        
                                                        # Aplicar predicción usando el mismo método que el aimbot
                                                        try:
                                                            vel_addr = primitive + int(offsets['Velocity'], 16)
                                                            velocity = [pm.read_float(vel_addr), pm.read_float(vel_addr + 4), pm.read_float(vel_addr + 8)]
                                                            obj_pos[0] += velocity[0] * (triggerbot_prediction_x * 0.01)
                                                            obj_pos[1] += velocity[1] * (triggerbot_prediction_y * 0.01)
                                                        except:
                                                            pass
                                                        
                                                        obj_pos = array(obj_pos, dtype=float32)
                                                        
                                                        # Calcular distancia 3D para hitbox dinámica
                                                        cam_pos = [pm.read_float(camPosAddr), pm.read_float(camPosAddr+4), pm.read_float(camPosAddr+8)]
                                                        distance_3d = sqrt((cam_pos[0] - obj_pos[0])**2 + (cam_pos[1] - obj_pos[1])**2 + (cam_pos[2] - obj_pos[2])**2)
                                                        
                                                        # Hitbox dinámica: más grande para objetivos lejanos, más pequeña para cercanos
                                                        dynamic_fov = triggerbot_fov
                                                        if distance_3d > 100:  # Muy lejos
                                                            dynamic_fov = triggerbot_fov * 1.5
                                                        elif distance_3d > 50:  # Lejos
                                                            dynamic_fov = triggerbot_fov * 1.2
                                                        elif distance_3d < 20:  # Muy cerca
                                                            dynamic_fov = triggerbot_fov * 0.7
                                                        elif distance_3d < 35:  # Cerca
                                                            dynamic_fov = triggerbot_fov * 0.85
                                                        
                                                        screen_coords = world_to_screen_with_matrix(obj_pos, view_proj_matrix, width, height)
                                                        if screen_coords is not None:
                                                            screen_distance = sqrt((widthCenter - screen_coords[0])**2 + (heightCenter - screen_coords[1])**2)
                                                            if screen_distance <= dynamic_fov and screen_distance < minDistance:
                                                                minDistance = screen_distance
                                                                locked_target = (primitive, targetPos, part_name)
                                                                break
                                    except:
                                        continue
                    else:
                        # Fire based on detection mode
                        if len(locked_target) == 3:
                            primitive, targetPos, part_name = locked_target
                        else:
                            primitive, targetPos = locked_target
                            part_name = "Unknown"
                        
                        if triggerbot_detection_mode == "Hitpart":
                            # Modo Hitpart: Verificar precisión por defecto antes de disparar
                            obj_pos = [
                                pm.read_float(targetPos),
                                pm.read_float(targetPos + 4),
                                pm.read_float(targetPos + 8)
                            ]
                            
                            # Aplicar predicción
                            try:
                                vel_addr = primitive + int(offsets['Velocity'], 16)
                                velocity = [pm.read_float(vel_addr), pm.read_float(vel_addr + 4), pm.read_float(vel_addr + 8)]
                                obj_pos[0] += velocity[0] * (triggerbot_prediction_x * 0.01)
                                obj_pos[1] += velocity[1] * (triggerbot_prediction_y * 0.01)
                            except:
                                pass
                            
                            obj_pos = array(obj_pos, dtype=float32)
                            screen_coords = world_to_screen_with_matrix(obj_pos, view_proj_matrix, width, height)
                            if screen_coords is not None:
                                # Usar precisión más grande para todas las partes
                                if part_name == "Head":
                                    hitpart_precision = 45.0  # pixels más grandes para cabeza
                                elif part_name in ["Torso", "UpperTorso", "LowerTorso", "HumanoidRootPart"]:
                                    hitpart_precision = 40.0  # pixels grandes para torso
                                elif part_name in ["LeftArm", "RightArm", "LeftLeg", "RightLeg"]:
                                    hitpart_precision = 35.0  # pixels para brazos y piernas
                                else:
                                    hitpart_precision = 30.0  # pixels de precisión por defecto para otras partes
                                distance = sqrt((widthCenter - screen_coords[0])**2 + (heightCenter - screen_coords[1])**2)
                                if distance <= hitpart_precision:
                                    windll.user32.mouse_event(0x0002, 0, 0, 0, 0)
                                    time.sleep(triggerbot_delay / 1000.0)  # Convertir ms a segundos
                                    windll.user32.mouse_event(0x0004, 0, 0, 0, 0)
                                else:
                                    locked_target = None
                            else:
                                locked_target = None
                        else:
                            # Modo Default: Verificar FOV antes de disparar
                            obj_pos = [
                                pm.read_float(targetPos),
                                pm.read_float(targetPos + 4),
                                pm.read_float(targetPos + 8)
                            ]
                            
                            # Aplicar predicción usando el mismo método que el aimbot
                            try:
                                vel_addr = primitive + int(offsets['Velocity'], 16)
                                velocity = [pm.read_float(vel_addr), pm.read_float(vel_addr + 4), pm.read_float(vel_addr + 8)]
                                obj_pos[0] += velocity[0] * (triggerbot_prediction_x * 0.01)
                                obj_pos[1] += velocity[1] * (triggerbot_prediction_y * 0.01)
                            except:
                                pass
                            
                            obj_pos = array(obj_pos, dtype=float32)
                            
                            # Calcular distancia 3D para hitbox dinámica
                            cam_pos = [pm.read_float(camPosAddr), pm.read_float(camPosAddr+4), pm.read_float(camPosAddr+8)]
                            distance_3d = sqrt((cam_pos[0] - obj_pos[0])**2 + (cam_pos[1] - obj_pos[1])**2 + (cam_pos[2] - obj_pos[2])**2)
                            
                            # Hitbox dinámica: más grande para objetivos lejanos, más pequeña para cercanos
                            dynamic_fov = triggerbot_fov
                            if distance_3d > 100:  # Muy lejos
                                dynamic_fov = triggerbot_fov * 1.5
                            elif distance_3d > 50:  # Lejos
                                dynamic_fov = triggerbot_fov * 1.2
                            elif distance_3d < 20:  # Muy cerca
                                dynamic_fov = triggerbot_fov * 0.7
                            elif distance_3d < 35:  # Cerca
                                dynamic_fov = triggerbot_fov * 0.85
                            
                            screen_coords = world_to_screen_with_matrix(obj_pos, view_proj_matrix, width, height)
                            if screen_coords is not None:
                                screen_distance = sqrt((widthCenter - screen_coords[0])**2 + (heightCenter - screen_coords[1])**2)
                                if screen_distance <= dynamic_fov:
                                    windll.user32.mouse_event(0x0002, 0, 0, 0, 0)
                                    time.sleep(triggerbot_delay / 1000.0)  # Convertir ms a segundos
                                    windll.user32.mouse_event(0x0004, 0, 0, 0, 0)
                                else:
                                    locked_target = None
                            else:
                                locked_target = None
                else:
                    locked_target = None
            except:
                pass
        else:
            time.sleep(0.0005)  # 0.5ms cuando no está activo para ahorrar CPU
        time.sleep(0.0003)  # 0.3ms base para mantener responsividad

threading.Thread(target=triggerbotLoop, daemon=True).start()

def aimbot_callback(sender, app_data):
    global aimbot_enabled, aimbot_toggled
    if not injected:
        return
    aimbot_enabled = app_data
    if not app_data:
        aimbot_toggled = False

def aimbot_ignoreteam_callback(sender, app_data):
    global aimbot_ignoreteam
    aimbot_ignoreteam = app_data

def aimbot_ignoredead_callback(sender, app_data):
    global aimbot_ignoredead
    aimbot_ignoredead = app_data

def aimbot_mode_callback(sender, app_data):
    global aimbot_mode, aimbot_toggled
    aimbot_mode = app_data
    if aimbot_mode == "Hold":
        aimbot_toggled = False
    dpg.configure_item("keybind_button", label=f"{get_key_name(aimbot_keybind)} ({aimbot_mode})")

def aimbot_smoothness_callback(sender, app_data):
    global aimbot_smoothness_enabled
    aimbot_smoothness_enabled = app_data
    dpg.configure_item("smoothness_x_slider", show=app_data)
    dpg.configure_item("smoothness_y_slider", show=app_data)

def smoothness_x_callback(sender, app_data):
    global aimbot_smoothness_x
    aimbot_smoothness_x = float(app_data)

def smoothness_y_callback(sender, app_data):
    global aimbot_smoothness_y
    aimbot_smoothness_y = float(app_data)

def keybind_callback():
    global waiting_for_keybind
    if not waiting_for_keybind:
        waiting_for_keybind = True
        dpg.configure_item("keybind_button", label="... (ESC to cancel)")

def aimbot_hitpart_callback(sender, app_data):
    global aimbot_hitpart
    aimbot_hitpart = app_data



def aimbot_prediction_checkbox(sender, app_data):
    global aimbot_prediction_enabled
    aimbot_prediction_enabled = app_data
    dpg.configure_item("prediction_x_slider", show=app_data)
    dpg.configure_item("prediction_y_slider", show=app_data)

def prediction_x_callback(sender, app_data):
    global aimbot_prediction_x
    slider_value = float(app_data)
    # Mapear de 1-100 a 0.01-1.0 para un rango más amplio pero controlado
    aimbot_prediction_x = 0.01 + (slider_value - 1) * 0.01

def prediction_y_callback(sender, app_data):
    global aimbot_prediction_y
    slider_value = float(app_data)
    # Mapear de 1-100 a 0.01-1.0 para un rango más amplio pero controlado
    aimbot_prediction_y = 0.01 + (slider_value - 1) * 0.01

def aimbot_shake_callback(sender, app_data):
    global aimbot_shake_enabled
    aimbot_shake_enabled = app_data
    dpg.configure_item("aimbot_shake_slider", show=app_data)

def aimbot_shake_strength_callback(sender, app_data):
    global aimbot_shake_strength
    aimbot_shake_strength = float(app_data)

def aimbot_fov_callback(sender, app_data):
    global aimbot_fov
    aimbot_fov = float(app_data)

def aimbot_type_callback(sender, app_data):
    global aimbot_type
    aimbot_type = app_data

def triggerbot_callback(sender, app_data):
    global triggerbot_enabled, triggerbot_toggled
    if not injected:
        return
    triggerbot_enabled = app_data
    if not app_data:
        triggerbot_toggled = False

def triggerbot_mode_callback(sender, app_data):
    global triggerbot_mode, triggerbot_toggled
    triggerbot_mode = app_data
    if triggerbot_mode == "Hold":
        triggerbot_toggled = False
    dpg.configure_item("triggerbot_keybind_button", label=f"{get_key_name(triggerbot_keybind)} ({triggerbot_mode})")

def triggerbot_keybind_callback():
    global waiting_for_keybind
    if not waiting_for_keybind:
        waiting_for_keybind = True
        dpg.configure_item("triggerbot_keybind_button", label="... (ESC to cancel)")

def rotation_360_callback(sender, app_data):
    global rotation_360_enabled
    if not injected:
        return
    rotation_360_enabled = app_data

def rotation_360_keybind_callback():
    global waiting_for_keybind
    if not waiting_for_keybind:
        waiting_for_keybind = True
        dpg.configure_item("rotation_360_keybind_button", label="... (ESC to cancel)")

def rotation_360_speed_callback(sender, app_data):
    global rotation_360_speed
    rotation_360_speed = float(app_data)

def rotation_360_mode_callback(sender, app_data):
    global rotation_360_mode, rotation_360_toggled
    rotation_360_mode = app_data
    if rotation_360_mode == "Hold":
        rotation_360_toggled = False
    dpg.configure_item("rotation_360_keybind_button", label=f"{get_key_name(rotation_360_keybind)} ({rotation_360_mode})")

def rotation_360_direction_callback(sender, app_data):
    global rotation_360_direction_mode, rotation_360_alternate_direction
    rotation_360_direction_mode = app_data
    # Resetear el alternador cuando se cambia de modo
    rotation_360_alternate_direction = False

def fly_callback(sender, app_data):
    global fly_enabled, fly_thread, offsets
    if not injected:
        return
    fly_enabled = app_data
    
    if fly_enabled and not fly_thread:
        fly_thread = FlyThread(pm, baseAddr, offsets)
        fly_thread.start()
    elif not fly_enabled and fly_thread:
        fly_thread.stop()
        fly_thread = None

def fly_keybind_callback():
    global waiting_for_keybind
    if not waiting_for_keybind:
        waiting_for_keybind = True
        dpg.configure_item("fly_keybind_button", label="... (ESC to cancel)")

def fly_speed_callback(sender, app_data):
    global fly_speed
    fly_speed = float(app_data)

def fly_method_callback(sender, app_data):
    global fly_method
    fly_method = 0 if app_data == "Position" else 1

def set_fly_mode(mode):
    global fly_mode, fly_toggled
    fly_mode = mode
    fly_toggled = False
    dpg.configure_item("fly_keybind_button", label=f"{get_key_name(fly_keybind)} ({fly_mode})")
    dpg.hide_item("fly_mode_popup")

def esp_visuals_callback(sender, app_data):
    global esp_enabled, esp_thread, offsets
    if not injected:
        return
    esp_enabled = app_data
    
    if esp_enabled and not esp_thread:
        esp_thread = ESPThread(pm, baseAddr, offsets)
        esp_thread.start()
    elif not esp_enabled and esp_thread:
        esp_thread.stop()
        esp_thread = None

def esp_team_check_callback(sender, app_data):
    global esp_team_check
    esp_team_check = app_data

def esp_death_check_callback(sender, app_data):
    global esp_death_check
    esp_death_check = app_data

def esp_tracers_callback(sender, app_data):
    global esp_tracers_enabled
    esp_tracers_enabled = app_data

def set_aimbot_mode(mode):
    global aimbot_mode
    aimbot_mode = mode
    dpg.configure_item("keybind_button", label=f"{get_key_name(aimbot_keybind)} ({aimbot_mode})")
    dpg.hide_item("keybind_mode_popup")

def triggerbot_delay_callback(sender, app_data):
    global triggerbot_delay
    triggerbot_delay = max(1, int(app_data))  # Mínimo 1ms para evitar problemas

def triggerbot_prediction_x_callback(sender, app_data):
    global triggerbot_prediction_x
    triggerbot_prediction_x = float(app_data)

def triggerbot_prediction_y_callback(sender, app_data):
    global triggerbot_prediction_y
    triggerbot_prediction_y = float(app_data)

def triggerbot_fov_callback(sender, app_data):
    global triggerbot_fov
    triggerbot_fov = float(app_data)

def triggerbot_detection_mode_callback(sender, app_data):
    global triggerbot_detection_mode
    triggerbot_detection_mode = app_data

# Función triggerbot_wallcheck_callback eliminada - wallcheck removido
def triggerbot_wallcheck_callback(sender, app_data):
    # Dummy callback - wallcheck functionality was removed
    pass

def walkspeed_gui_loop():
    global walkspeed_gui_active
    while walkspeed_gui_active:
        try:
            if walkspeed_gui_enabled:
                cam_addr = get_camera_addr_gui()
                if cam_addr:
                    h = pm.read_longlong(cam_addr + int(offsets["CameraSubject"], 16))
                    pm.write_float(h + int(offsets["WalkSpeedCheck"], 16), float('inf'))
                    pm.write_float(h + int(offsets["WalkSpeed"], 16), float(walkspeed_gui_value))
            time.sleep(0.1)
        except:
            time.sleep(0.1)

def walkspeed_gui_toggle(sender, state):
    global walkspeed_gui_enabled, walkspeed_gui_active, walkspeed_gui_thread
    walkspeed_gui_enabled = state
    dpg.configure_item("walkspeed_gui_slider", show=state)
    if state and not walkspeed_gui_active:
        walkspeed_gui_active = True
        walkspeed_gui_thread = threading.Thread(target=walkspeed_gui_loop, daemon=True)
        walkspeed_gui_thread.start()
    if not state and walkspeed_gui_active:
        walkspeed_gui_active = False

def walkspeed_gui_change(sender, value):
    global walkspeed_gui_value
    walkspeed_gui_value = float(value)

def get_camera_addr_gui():
    try:
        a = pm.read_longlong(baseAddr + int(offsets["VisualEnginePointer"], 16))
        b = pm.read_longlong(a + int(offsets["VisualEngineToDataModel1"], 16))
        c = pm.read_longlong(b + int(offsets["VisualEngineToDataModel2"], 16))
        d = pm.read_longlong(c + int(offsets["Workspace"], 16))
        return pm.read_longlong(d + int(offsets["Camera"], 16))
    except Exception as e:
        print(f"Error in get_camera_addr_gui: {e}")
        return None

def get_configs_directory():
    # Obtener directorio del script o ejecutable
    if getattr(sys, 'frozen', False) or '__compiled__' in globals():
        # Ejecutable compilado (PyInstaller, Nuitka, etc.)
        script_dir = os.path.dirname(sys.executable)
    else:
        # Script Python normal
        script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Crear directorio configs junto al script/exe
    configs_dir = os.path.join(script_dir, "configs")
    if not os.path.exists(configs_dir):
        os.makedirs(configs_dir)
    return configs_dir

def get_config_files():
    configs_dir = get_configs_directory()
    return [f for f in os.listdir(configs_dir) if f.endswith('.json')]

def windows_save_file_dialog():
    try:
        configs_dir = get_configs_directory()
        filename_buffer = ctypes.create_unicode_buffer(260)
        initial_path = os.path.join(configs_dir, "config.json")
        filename_buffer.value = initial_path
        ofn = OPENFILENAME()
        ofn.lStructSize = ctypes.sizeof(OPENFILENAME)
        ofn.hwndOwner = None
        ofn.lpstrFilter = "JSON Files\0*.json\0All Files\0*.*\0"
        ofn.lpstrFile = ctypes.cast(filename_buffer, wintypes.LPWSTR)
        ofn.nMaxFile = 260
        ofn.lpstrFileTitle = None
        ofn.nMaxFileTitle = 0
        ofn.lpstrInitialDir = configs_dir
        ofn.lpstrTitle = "Save Config"
        ofn.lpstrDefExt = "json"
        ofn.Flags = 0x00000002 | 0x00000004
        if windll.comdlg32.GetSaveFileNameW(byref(ofn)):
            selected_path = filename_buffer.value
            if not selected_path.startswith(configs_dir):
                filename = os.path.basename(selected_path)
                selected_path = os.path.join(configs_dir, filename)
            return selected_path
        return None
    except Exception as e:
        print(f"Error in save dialog: {e}")
        return None

def windows_open_file_dialog():
    try:
        configs_dir = get_configs_directory()
        filename_buffer = ctypes.create_unicode_buffer(260)
        ofn = OPENFILENAME()
        ofn.lStructSize = ctypes.sizeof(OPENFILENAME)
        ofn.hwndOwner = None
        ofn.lpstrFilter = "JSON Files\0*.json\0All Files\0*.*\0"
        ofn.lpstrFile = ctypes.cast(filename_buffer, wintypes.LPWSTR)
        ofn.nMaxFile = 260
        ofn.lpstrInitialDir = configs_dir
        ofn.lpstrTitle = "Load Config"
        ofn.Flags = 0x00001000 | 0x00000004
        if windll.comdlg32.GetOpenFileNameW(byref(ofn)):
            return filename_buffer.value
        return None
    except Exception as e:
        print(f"Error in open dialog: {e}")
        return None

def save_config_callback():
    global aimbot_enabled, aimbot_keybind, aimbot_mode, aimbot_hitpart, aimbot_ignoreteam, aimbot_ignoredead
    global aimbot_prediction_enabled, aimbot_prediction_x, aimbot_prediction_y
    global aimbot_smoothness_enabled, aimbot_smoothness_x, aimbot_smoothness_y
    global aimbot_shake_enabled, aimbot_shake_strength, aimbot_fov, aimbot_type
    global triggerbot_enabled, triggerbot_keybind, triggerbot_mode, triggerbot_delay
    global triggerbot_prediction_x, triggerbot_prediction_y, triggerbot_fov, triggerbot_detection_mode, triggerbot_wallcheck_enabled
    global walkspeed_gui_enabled, walkspeed_gui_value
    global rotation_360_enabled, rotation_360_keybind, rotation_360_speed
    global fly_enabled, fly_keybind, fly_mode, fly_speed, fly_method
    global esp_enabled, esp_team_check, esp_death_check, esp_tracers_enabled
    try:
        file_path = windows_save_file_dialog()
        if file_path:
            config_data = {
                "aimbot": {
                    "enabled": aimbot_enabled,
                    "keybind": aimbot_keybind,
                    "mode": aimbot_mode,
                    "hitpart": aimbot_hitpart,
                    "ignoreteam": aimbot_ignoreteam,
                    "ignoredead": aimbot_ignoredead,
                    "fov": float(aimbot_fov),
                    "type": aimbot_type
                },
                "prediction": {
                    "enabled": aimbot_prediction_enabled,
                    "x": float(aimbot_prediction_x),
                    "y": float(aimbot_prediction_y)
                },
                "smoothness": {
                    "enabled": aimbot_smoothness_enabled,
                    "x": float(aimbot_smoothness_x),
                    "y": float(aimbot_smoothness_y)
                },
                "shake": {
                    "enabled": aimbot_shake_enabled,
                    "strength": float(aimbot_shake_strength)
                },
                "triggerbot": {
                    "enabled": triggerbot_enabled,
                    "keybind": triggerbot_keybind,
                    "mode": triggerbot_mode,
                    "delay": int(triggerbot_delay),
                    "prediction_x": float(triggerbot_prediction_x),
                    "prediction_y": float(triggerbot_prediction_y),
                    "fov": float(triggerbot_fov),
                    "detection_mode": triggerbot_detection_mode,
                    "wallcheck": triggerbot_wallcheck_enabled
                },
                "walkspeed": {
                    "enabled": walkspeed_gui_enabled,
                    "value": float(walkspeed_gui_value)
                },
                "rotation_360": {
                    "enabled": rotation_360_enabled,
                    "keybind": rotation_360_keybind,
                    "speed": float(rotation_360_speed),
                    "mode": rotation_360_mode,
                    "direction_mode": rotation_360_direction_mode
                },
                "fly": {
                    "enabled": fly_enabled,
                    "keybind": fly_keybind,
                    "mode": fly_mode,
                    "speed": float(fly_speed),
                    "method": fly_method
                },
                "esp": {
                    "enabled": esp_enabled,
                    "team_check": esp_team_check,
                    "death_check": esp_death_check,
                    "tracers": esp_tracers_enabled
                }
            }
            with open(file_path, 'w') as f:
                json.dump(config_data, f, indent=4, sort_keys=True)
            print(f"Config saved to: {file_path}")
            dpg.configure_item("config_listbox", items=get_config_files())
    except Exception as e:
        print(f"Error saving config: {e}")

def load_config_callback():
    global aimbot_enabled, aimbot_keybind, aimbot_mode, aimbot_hitpart, aimbot_ignoreteam, aimbot_ignoredead
    global aimbot_prediction_enabled, aimbot_prediction_x, aimbot_prediction_y
    global aimbot_smoothness_enabled, aimbot_smoothness_x, aimbot_smoothness_y
    global aimbot_shake_enabled, aimbot_shake_strength, aimbot_fov, aimbot_type
    global triggerbot_enabled, triggerbot_keybind, triggerbot_mode, triggerbot_delay
    global triggerbot_prediction_x, triggerbot_prediction_y, triggerbot_fov, triggerbot_detection_mode, triggerbot_wallcheck_enabled
    global walkspeed_gui_enabled, walkspeed_gui_value
    global rotation_360_enabled, rotation_360_keybind, rotation_360_speed
    global fly_enabled, fly_keybind, fly_mode, fly_speed, fly_method
    global esp_enabled, esp_team_check, esp_death_check, esp_tracers_enabled
    selected_config = dpg.get_value("config_listbox")
    if selected_config:
        file_path = os.path.join(get_configs_directory(), selected_config)
        try:
            with open(file_path, 'r') as f:
                config_data = json.load(f)
            if "aimbot" in config_data:
                aimbot_config = config_data["aimbot"]
                aimbot_enabled = aimbot_config.get("enabled", aimbot_enabled)
                aimbot_keybind = aimbot_config.get("keybind", aimbot_keybind)
                aimbot_mode = aimbot_config.get("mode", aimbot_mode)
                aimbot_hitpart = aimbot_config.get("hitpart", aimbot_hitpart)
                aimbot_ignoreteam = aimbot_config.get("ignoreteam", aimbot_ignoreteam)
                aimbot_ignoredead = aimbot_config.get("ignoredead", aimbot_ignoredead)
                aimbot_fov = float(aimbot_config.get("fov", aimbot_fov))
                aimbot_type = aimbot_config.get("type", aimbot_type)
                dpg.set_value("aimbot_checkbox", aimbot_enabled)
                dpg.configure_item("keybind_button", label=f"{get_key_name(aimbot_keybind)} ({aimbot_mode})")
                dpg.set_value("aimbot_hitpart_combo", aimbot_hitpart)
                dpg.set_value("aimbot_ignoreteam_checkbox", aimbot_ignoreteam)
                dpg.set_value("aimbot_ignoredead_checkbox", aimbot_ignoredead)
                dpg.set_value("aimbot_fov_slider", aimbot_fov)
                dpg.set_value("aimbot_type_combo", aimbot_type)
            if "prediction" in config_data:
                prediction_config = config_data["prediction"]
                aimbot_prediction_enabled = prediction_config.get("enabled", aimbot_prediction_enabled)
                aimbot_prediction_x = float(prediction_config.get("x", aimbot_prediction_x))
                aimbot_prediction_y = float(prediction_config.get("y", aimbot_prediction_y))
                dpg.set_value("aimbot_prediction_checkbox", aimbot_prediction_enabled)
                dpg.configure_item("prediction_x_slider", show=aimbot_prediction_enabled)
                dpg.configure_item("prediction_y_slider", show=aimbot_prediction_enabled)
                # Convertir de vuelta del rango 0.01-1.0 a 1-100
                slider_x = 1 + (aimbot_prediction_x - 0.01) / 0.01
                slider_y = 1 + (aimbot_prediction_y - 0.01) / 0.01
                dpg.set_value("prediction_x_slider", slider_x)
                dpg.set_value("prediction_y_slider", slider_y)
            if "smoothness" in config_data:
                smoothness_config = config_data["smoothness"]
                aimbot_smoothness_enabled = smoothness_config.get("enabled", aimbot_smoothness_enabled)
                aimbot_smoothness_x = float(smoothness_config.get("x", aimbot_smoothness_x))
                aimbot_smoothness_y = float(smoothness_config.get("y", aimbot_smoothness_y))
                dpg.set_value("aimbot_smoothness_checkbox", aimbot_smoothness_enabled)
                dpg.configure_item("smoothness_x_slider", show=aimbot_smoothness_enabled)
                dpg.configure_item("smoothness_y_slider", show=aimbot_smoothness_enabled)
                dpg.set_value("smoothness_x_slider", aimbot_smoothness_x)
                dpg.set_value("smoothness_y_slider", aimbot_smoothness_y)
            if "shake" in config_data:
                shake_config = config_data["shake"]
                aimbot_shake_enabled = shake_config.get("enabled", aimbot_shake_enabled)
                aimbot_shake_strength = float(shake_config.get("strength", aimbot_shake_strength))
                dpg.set_value("aimbot_shake_checkbox", aimbot_shake_enabled)
                dpg.configure_item("aimbot_shake_slider", show=aimbot_shake_enabled)
                dpg.set_value("aimbot_shake_slider", aimbot_shake_strength)
            if "triggerbot" in config_data:
                triggerbot_config = config_data["triggerbot"]
                triggerbot_enabled = triggerbot_config.get("enabled", triggerbot_enabled)
                triggerbot_keybind = triggerbot_config.get("keybind", triggerbot_keybind)
                triggerbot_mode = triggerbot_config.get("mode", triggerbot_mode)
                triggerbot_delay = int(triggerbot_config.get("delay", triggerbot_delay))
                triggerbot_prediction_x = float(triggerbot_config.get("prediction_x", triggerbot_prediction_x))
                triggerbot_prediction_y = float(triggerbot_config.get("prediction_y", triggerbot_prediction_y))
                triggerbot_fov = float(triggerbot_config.get("fov", triggerbot_fov))
                triggerbot_detection_mode = triggerbot_config.get("detection_mode", triggerbot_detection_mode)
                triggerbot_wallcheck_enabled = triggerbot_config.get("wallcheck", triggerbot_wallcheck_enabled)
                dpg.set_value("triggerbot_checkbox", triggerbot_enabled)
                dpg.configure_item("triggerbot_keybind_button", label=f"{get_key_name(triggerbot_keybind)} ({triggerbot_mode})")
                dpg.set_value("triggerbot_delay_slider", triggerbot_delay)
                dpg.set_value("triggerbot_prediction_x_slider", triggerbot_prediction_x)
                dpg.set_value("triggerbot_prediction_y_slider", triggerbot_prediction_y)
                dpg.set_value("triggerbot_fov_slider", triggerbot_fov)
                dpg.set_value("triggerbot_detection_mode_combo", triggerbot_detection_mode)
                dpg.set_value("triggerbot_wallcheck_checkbox", triggerbot_wallcheck_enabled)
            if "walkspeed" in config_data:
                walkspeed_config = config_data["walkspeed"]
                walkspeed_gui_enabled = walkspeed_config.get("enabled", walkspeed_gui_enabled)
                walkspeed_gui_value = float(walkspeed_config.get("value", walkspeed_gui_value))
                dpg.set_value("walkspeed_gui_checkbox", walkspeed_gui_enabled)
                dpg.configure_item("walkspeed_gui_slider", show=walkspeed_gui_enabled)
                dpg.set_value("walkspeed_gui_slider", walkspeed_gui_value)
            if "rotation_360" in config_data:
                rotation_config = config_data["rotation_360"]
                rotation_360_enabled = rotation_config.get("enabled", rotation_360_enabled)
                rotation_360_keybind = rotation_config.get("keybind", rotation_360_keybind)
                rotation_360_speed = float(rotation_config.get("speed", rotation_360_speed))
                rotation_360_mode = rotation_config.get("mode", rotation_360_mode)
                rotation_360_direction_mode = rotation_config.get("direction_mode", rotation_360_direction_mode)
                dpg.set_value("rotation_360_checkbox", rotation_360_enabled)
                dpg.configure_item("rotation_360_keybind_button", label=f"{get_key_name(rotation_360_keybind)} ({rotation_360_mode})")
                dpg.set_value("rotation_360_speed_slider", rotation_360_speed)
                dpg.set_value("rotation_360_mode_combo", rotation_360_mode)
                dpg.set_value("rotation_360_direction_combo", rotation_360_direction_mode)
            if "fly" in config_data:
                fly_config = config_data["fly"]
                fly_enabled = fly_config.get("enabled", fly_enabled)
                fly_keybind = fly_config.get("keybind", fly_keybind)
                fly_mode = fly_config.get("mode", fly_mode)
                fly_speed = float(fly_config.get("speed", fly_speed))
                fly_method = fly_config.get("method", fly_method)
                dpg.set_value("fly_checkbox", fly_enabled)
                dpg.configure_item("fly_keybind_button", label=f"{get_key_name(fly_keybind)} ({fly_mode})")
                dpg.set_value("fly_speed_slider", fly_speed)
                dpg.set_value("fly_method_combo", "Position" if fly_method == 0 else "Velocity")
            if "esp" in config_data:
                esp_config = config_data["esp"]
                esp_enabled = esp_config.get("enabled", esp_enabled)
                esp_team_check = esp_config.get("team_check", esp_team_check)
                esp_death_check = esp_config.get("death_check", esp_death_check)
                esp_tracers_enabled = esp_config.get("tracers", esp_tracers_enabled)
                esp_box_enabled = esp_config.get("box", esp_box_enabled)
                dpg.set_value("Visuals_checkbox", esp_enabled)
                dpg.set_value("Visuals_ignoreteam_checkbox", esp_team_check)
                dpg.set_value("Visuals_ignoredead_checkbox", esp_death_check)
                dpg.set_value("esp_tracers_checkbox", esp_tracers_enabled)
                dpg.set_value("esp_box_checkbox", esp_box_enabled)
            print(f"Config loaded from: {file_path}")
            dpg.configure_item("config_listbox", items=get_config_files())
        except Exception as e:
            print(f"Error loading config: {e}")

def delete_config_callback():
    selected_config = dpg.get_value("config_listbox")
    if selected_config:
        file_path = os.path.join(get_configs_directory(), selected_config)
        try:
            os.remove(file_path)
            print(f"Config deleted: {file_path}")
            dpg.configure_item("config_listbox", items=get_config_files())
            dpg.set_value("config_listbox", "")
        except Exception as e:
            print(f"Error deleting config: {e}")

def check_license():
    if os.name == 'nt':
        console_window = ctypes.windll.kernel32.GetConsoleWindow()
        if console_window:
            ctypes.windll.kernel32.SetConsoleScreenBufferSize(ctypes.windll.kernel32.GetStdHandle(-11), (80 << 16) | 25)
            GWL_STYLE = -16
            WS_THICKFRAME = 0x00040000
            WS_MAXIMIZEBOX = 0x00010000
            style = ctypes.windll.user32.GetWindowLongW(console_window, GWL_STYLE)
            style &= ~(WS_THICKFRAME | WS_MAXIMIZEBOX)
            ctypes.windll.user32.SetWindowLongW(console_window, GWL_STYLE, style)
            ctypes.windll.user32.SetWindowPos(console_window, 0, 0, 0, 700, 400, 0x0040)
    
    print("[Flame-external] License: ", end="", flush=True)
    while True:
        try:
            license_key = ""
            while True:
                char = msvcrt.getch().decode('utf-8')
                if char == '\r':
                    print()
                    break
                elif char == '\b':
                    if license_key:
                        license_key = license_key[:-1]
                        print('\b \b', end="", flush=True)
                elif char.isprintable():
                    license_key += char
                    print('*', end="", flush=True)
            if license_key == "Flame":
                os.system('cls' if os.name == 'nt' else 'clear')
                print("[warning] updater: checking if directory exists", end="", flush=True)
                time.sleep(3)
                try:
                    ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 6)
                except:
                    pass
                return True
            else:
                print("[ERROR] Invalid license key!")
                print("[logs] License key: ", end="", flush=True)
        except (EOFError, KeyboardInterrupt):
            print("\n[INFO] License verification cancelled")
            return False

if __name__ == "__main__":
    if not check_license():
        sys.exit(0)
    try:
        offsets = get('https://offsets.ntgetwritewatch.workers.dev/offsets.json').json()
        setOffsets(int(offsets['Name'], 16), int(offsets['Children'], 16))
    except Exception as e:
        print(f"Error loading offsets: {e}")
        sys.exit(1)
    threading.Thread(target=background_process_monitor, daemon=True).start()

    dpg.create_context()
    
    # Funciones de tema integradas - Estilo de 8.py
    def setup_modern_theme():
        """Tema blanco y negro con transparencia"""
        with dpg.theme() as global_theme:
            with dpg.theme_component(dpg.mvAll):
                # Fondo principal con transparencia
                dpg.add_theme_color(dpg.mvThemeCol_WindowBg, (0, 0, 0, 200))             # Fondo negro semi-transparente
                dpg.add_theme_color(dpg.mvThemeCol_ChildBg, (20, 20, 20, 180))           # Paneles gris muy oscuro semi-transparente
                dpg.add_theme_color(dpg.mvThemeCol_PopupBg, (10, 10, 10, 220))           # Popups negro semi-transparente
                
                # Texto en blanco y grises
                dpg.add_theme_color(dpg.mvThemeCol_Text, (255, 255, 255, 255))           # Texto blanco puro
                dpg.add_theme_color(dpg.mvThemeCol_TextDisabled, (120, 120, 120, 255))   # Texto deshabilitado gris
                
                # Botones en escala de grises
                dpg.add_theme_color(dpg.mvThemeCol_Button, (40, 40, 40, 200))            # Botones gris oscuro semi-transparente
                dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (80, 80, 80, 220))     # Hover gris medio
                dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, (120, 120, 120, 240))   # Activo gris claro
                
                # Inputs y frames
                dpg.add_theme_color(dpg.mvThemeCol_FrameBg, (30, 30, 30, 180))           # Fondo de inputs gris oscuro
                dpg.add_theme_color(dpg.mvThemeCol_FrameBgHovered, (60, 60, 60, 200))    # Hover inputs
                dpg.add_theme_color(dpg.mvThemeCol_FrameBgActive, (100, 100, 100, 220))  # Activo inputs
                
                # Headers
                dpg.add_theme_color(dpg.mvThemeCol_Header, (50, 50, 50, 180))            # Headers gris oscuro
                dpg.add_theme_color(dpg.mvThemeCol_HeaderHovered, (90, 90, 90, 200))     # Header hover
                dpg.add_theme_color(dpg.mvThemeCol_HeaderActive, (130, 130, 130, 220))   # Header activo
                
                # Elementos de control
                dpg.add_theme_color(dpg.mvThemeCol_CheckMark, (255, 255, 255, 255))      # Checkmarks blancos
                dpg.add_theme_color(dpg.mvThemeCol_SliderGrab, (200, 200, 200, 255))     # Sliders gris claro
                dpg.add_theme_color(dpg.mvThemeCol_SliderGrabActive, (255, 255, 255, 255)) # Slider activo blanco
                
                # Bordes y separadores
                dpg.add_theme_color(dpg.mvThemeCol_Border, (100, 100, 100, 150))         # Bordes gris semi-transparente
                dpg.add_theme_color(dpg.mvThemeCol_BorderShadow, (0, 0, 0, 0))           # Sin sombra
                dpg.add_theme_color(dpg.mvThemeCol_Separator, (80, 80, 80, 180))         # Separadores gris
                dpg.add_theme_color(dpg.mvThemeCol_SeparatorHovered, (120, 120, 120, 200))
                dpg.add_theme_color(dpg.mvThemeCol_SeparatorActive, (160, 160, 160, 220))
                
                # Scrollbars
                dpg.add_theme_color(dpg.mvThemeCol_ScrollbarBg, (20, 20, 20, 150))       # Fondo scrollbar
                dpg.add_theme_color(dpg.mvThemeCol_ScrollbarGrab, (80, 80, 80, 200))     # Grab scrollbar
                dpg.add_theme_color(dpg.mvThemeCol_ScrollbarGrabHovered, (120, 120, 120, 220))
                dpg.add_theme_color(dpg.mvThemeCol_ScrollbarGrabActive, (160, 160, 160, 240))
                
                # Tabs
                dpg.add_theme_color(dpg.mvThemeCol_Tab, (40, 40, 40, 180))
                dpg.add_theme_color(dpg.mvThemeCol_TabHovered, (80, 80, 80, 200))
                dpg.add_theme_color(dpg.mvThemeCol_TabActive, (120, 120, 120, 220))
                dpg.add_theme_color(dpg.mvThemeCol_TabUnfocused, (30, 30, 30, 160))
                dpg.add_theme_color(dpg.mvThemeCol_TabUnfocusedActive, (60, 60, 60, 180))
                
                # Título de ventana
                dpg.add_theme_color(dpg.mvThemeCol_TitleBg, (0, 0, 0, 200))              # Título negro semi-transparente
                dpg.add_theme_color(dpg.mvThemeCol_TitleBgActive, (20, 20, 20, 220))     # Título activo
                
                # Estilos con bordes más suaves
                dpg.add_theme_style(dpg.mvStyleVar_WindowRounding, 8)
                dpg.add_theme_style(dpg.mvStyleVar_ChildRounding, 6)
                dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 4)
                dpg.add_theme_style(dpg.mvStyleVar_PopupRounding, 6)
                dpg.add_theme_style(dpg.mvStyleVar_ScrollbarRounding, 4)
                dpg.add_theme_style(dpg.mvStyleVar_GrabRounding, 4)
                dpg.add_theme_style(dpg.mvStyleVar_TabRounding, 4)
                dpg.add_theme_style(dpg.mvStyleVar_WindowPadding, 12, 12)
                dpg.add_theme_style(dpg.mvStyleVar_FramePadding, 8, 4)
                dpg.add_theme_style(dpg.mvStyleVar_ItemSpacing, 8, 6)
                dpg.add_theme_style(dpg.mvStyleVar_ItemInnerSpacing, 6, 4)
                dpg.add_theme_style(dpg.mvStyleVar_IndentSpacing, 20)
                dpg.add_theme_style(dpg.mvStyleVar_ScrollbarSize, 14)
                dpg.add_theme_style(dpg.mvStyleVar_GrabMinSize, 12)
        return global_theme

    def setup_accent_button_theme():
        with dpg.theme() as accent_theme:
            with dpg.theme_component(dpg.mvButton):
                dpg.add_theme_color(dpg.mvThemeCol_Button, (80, 80, 80, 220))            # Gris medio semi-transparente
                dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (120, 120, 120, 240))  # Gris claro hover
                dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, (160, 160, 160, 255))   # Gris muy claro activo
                dpg.add_theme_color(dpg.mvThemeCol_Text, (255, 255, 255, 255))           # Texto blanco
        return accent_theme

    def setup_danger_button_theme():
        with dpg.theme() as danger_theme:
            with dpg.theme_component(dpg.mvButton):
                dpg.add_theme_color(dpg.mvThemeCol_Button, (60, 60, 60, 220))            # Gris oscuro
                dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (100, 100, 100, 240))  # Gris medio hover
                dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, (140, 140, 140, 255))   # Gris claro activo
                dpg.add_theme_color(dpg.mvThemeCol_Text, (255, 255, 255, 255))           # Texto blanco
        return danger_theme

    def setup_success_button_theme():
        with dpg.theme() as success_theme:
            with dpg.theme_component(dpg.mvButton):
                dpg.add_theme_color(dpg.mvThemeCol_Button, (100, 100, 100, 220))         # Gris claro
                dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (140, 140, 140, 240))  # Gris muy claro hover
                dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, (180, 180, 180, 255))   # Casi blanco activo
                dpg.add_theme_color(dpg.mvThemeCol_Text, (0, 0, 0, 255))                 # Texto negro para contraste
        return success_theme

    def setup_group_theme():
        with dpg.theme() as group_theme:
            with dpg.theme_component(dpg.mvChildWindow):
                dpg.add_theme_color(dpg.mvThemeCol_ChildBg, (15, 15, 15, 180))           # Fondo muy oscuro semi-transparente
                dpg.add_theme_color(dpg.mvThemeCol_Border, (80, 80, 80, 150))            # Bordes gris semi-transparente
                dpg.add_theme_style(dpg.mvStyleVar_ChildRounding, 4)
                dpg.add_theme_style(dpg.mvStyleVar_ChildBorderSize, 1)
                dpg.add_theme_style(dpg.mvStyleVar_WindowPadding, 12, 12)
        return group_theme
    
    # Aplicar temas
    global_theme = setup_modern_theme()
    accent_theme = setup_accent_button_theme()
    danger_theme = setup_danger_button_theme()
    success_theme = setup_success_button_theme()
    group_theme = setup_group_theme()

    # Ventana de inyección con tamaño normal
    with dpg.window(label="Flame External", tag="Injector Window", width=800, height=700, no_resize=True):
        dpg.add_spacer(height=80)
        
        # Header posicionado arriba y a la derecha
        with dpg.child_window(height=150, border=False):
            dpg.bind_item_theme(dpg.last_item(), group_theme)
            dpg.add_spacer(height=20)
            
            # Mover a la derecha usando grupo horizontal
            with dpg.group(horizontal=True):
                dpg.add_spacer(width=100)  # Espaciado a la izquierda para mover a la derecha
                dpg.add_text("Flame External", color=(130, 100, 200, 255))
            
            dpg.add_spacer(height=25)
            
            # Botón también movido a la derecha
            with dpg.group(horizontal=True):
                dpg.add_spacer(width=100)  # Mismo espaciado para alinear
                dpg.add_button(label="INJECT", callback=init, tag="inject_button", width=150, height=45)
                dpg.bind_item_theme(dpg.last_item(), accent_theme)

    # Ventana principal minimalista
    with dpg.window(label="Flame External", tag="Primary Window", width=800, height=700, show=False, no_resize=True, no_move=True, no_collapse=True, pos=[0, 0]):
        with dpg.tab_bar():
            # Tab Aimbot
            with dpg.tab(label="Aimbot"):
                dpg.add_spacer(height=8)
                
                # Configuración principal
                with dpg.child_window(height=150, width=760, border=True):
                    dpg.bind_item_theme(dpg.last_item(), group_theme)
                    dpg.add_text("Aimbot", color=(130, 100, 200, 255))
                    dpg.add_separator()
                    dpg.add_spacer(height=5)
                    
                    with dpg.group(horizontal=True):
                        dpg.add_checkbox(label="Enable", default_value=aimbot_enabled, callback=aimbot_callback, tag="aimbot_checkbox")
                        dpg.add_spacer(width=15)
                        dpg.add_button(label=f"{get_key_name(aimbot_keybind)} ({aimbot_mode})", tag="keybind_button", callback=keybind_callback, width=100)
                        dpg.bind_item_theme(dpg.last_item(), accent_theme)
                        dpg.add_spacer(width=15)
                        dpg.add_combo([
                            "Head", "Torso", "UpperTorso", "LowerTorso", "LeftArm", "RightArm"
                        ], label="Part", default_value="Head", tag="aimbot_hitpart_combo", width=120, callback=aimbot_hitpart_callback)
                        dpg.add_spacer(width=10)

                    dpg.add_spacer(height=8)
                    dpg.add_combo(label="Type", items=["Mouse", "Camera", "Silent Aim/flick (BETA)"], default_value=aimbot_type, callback=aimbot_type_callback, tag="aimbot_type_combo", width=200)
                    dpg.add_spacer(height=8)
                    dpg.add_slider_float(label="FOV", default_value=aimbot_fov, min_value=10.0, max_value=2000.0, format="%.1f", callback=aimbot_fov_callback, tag="aimbot_fov_slider", width=200)
                    dpg.add_spacer(height=8)
                
                dpg.add_spacer(height=8)
                
                # Prediction
                with dpg.child_window(height=100, width=760, border=True):
                    dpg.bind_item_theme(dpg.last_item(), group_theme)
                    dpg.add_text("Prediction", color=(130, 100, 200, 255))
                    dpg.add_separator()
                    dpg.add_spacer(height=5)
                    
                    dpg.add_checkbox(label="Enable", default_value=aimbot_prediction_enabled, callback=aimbot_prediction_checkbox, tag="aimbot_prediction_checkbox")
                    with dpg.group(horizontal=True):
                        dpg.add_slider_float(label="X", default_value=1.0, min_value=1.0, max_value=100.0, format="%.1f", callback=prediction_x_callback, tag="prediction_x_slider", show=aimbot_prediction_enabled, width=150)
                        dpg.add_slider_float(label="Y", default_value=1.0, min_value=1.0, max_value=100.0, format="%.1f", callback=prediction_y_callback, tag="prediction_y_slider", show=aimbot_prediction_enabled, width=150)
                
                dpg.add_spacer(height=8)
                
                # Smoothness
                with dpg.child_window(height=100, width=760, border=True):
                    dpg.bind_item_theme(dpg.last_item(), group_theme)
                    dpg.add_text("Smoothness", color=(130, 100, 200, 255))
                    dpg.add_separator()
                    dpg.add_spacer(height=5)
                    
                    dpg.add_checkbox(label="Enable", default_value=aimbot_smoothness_enabled, callback=aimbot_smoothness_callback, tag="aimbot_smoothness_checkbox")
                    with dpg.group(horizontal=True):
                        dpg.add_slider_float(label="X", default_value=5.5, min_value=1.0, max_value=100.0, format="%.1f", callback=smoothness_x_callback, tag="smoothness_x_slider", show=aimbot_smoothness_enabled, width=150)
                        dpg.add_slider_float(label="Y", default_value=5.5, min_value=1.0, max_value=100.0, format="%.1f", callback=smoothness_y_callback, tag="smoothness_y_slider", show=aimbot_smoothness_enabled, width=150)
                
                # Popup para modo
                with dpg.popup(parent="keybind_button", mousebutton=dpg.mvMouseButton_Right, tag="keybind_mode_popup"):
                    dpg.add_text("Mode", color=(130, 100, 200, 255))
                    dpg.add_separator()
                    dpg.add_button(label="Hold", callback=lambda s, a, u: set_aimbot_mode("Hold"), width=80)
                    dpg.add_button(label="Toggle", callback=lambda s, a, u: set_aimbot_mode("Toggle"), width=80)

            # Tab Visuals
            with dpg.tab(label="Visuals"):
                dpg.add_spacer(height=8)
                
                with dpg.child_window(height=150, width=760, border=True):
                    dpg.bind_item_theme(dpg.last_item(), group_theme)
                    dpg.add_text("Visuals", color=(130, 100, 200, 255))
                    dpg.add_separator()
                    dpg.add_spacer(height=5)
                    
                    dpg.add_checkbox(label="Enable Visuals", default_value=esp_enabled, callback=esp_visuals_callback, tag="Visuals_checkbox")
                    dpg.add_checkbox(label="Team Check", default_value=esp_team_check, callback=esp_team_check_callback, tag="Visuals_ignoreteam_checkbox")
                    dpg.add_checkbox(label="Death Check", default_value=esp_death_check, callback=esp_death_check_callback, tag="Visuals_ignoredead_checkbox")
                    dpg.add_checkbox(label="Tracers", default_value=esp_tracers_enabled, callback=esp_tracers_callback, tag="esp_tracers_checkbox")
                    dpg.add_checkbox(label="Box", default_value=esp_box_enabled, callback=esp_box_callback, tag="esp_box_checkbox")
                    
                    dpg.add_spacer(height=8)
                    dpg.add_checkbox(label="Shake", default_value=aimbot_shake_enabled, callback=aimbot_shake_callback, tag="aimbot_shake_checkbox")
                    dpg.add_slider_float(label="Strength", default_value=aimbot_shake_strength, min_value=0.000, max_value=0.05, format="%.3f", callback=aimbot_shake_strength_callback, tag="aimbot_shake_slider", show=aimbot_shake_enabled, width=200)

            # Tab Triggerbot
            with dpg.tab(label="Triggerbot"):
                dpg.add_spacer(height=8)
                
                with dpg.child_window(height=120, width=760, border=True):
                    dpg.bind_item_theme(dpg.last_item(), group_theme)
                    dpg.add_text("Triggerbot", color=(130, 100, 200, 255))
                    dpg.add_separator()
                    dpg.add_spacer(height=5)
                    
                    with dpg.group(horizontal=True):
                        dpg.add_checkbox(label="Enable", default_value=triggerbot_enabled, callback=triggerbot_callback, tag="triggerbot_checkbox")
                        dpg.add_spacer(width=15)
                        dpg.add_button(label=f"{get_key_name(triggerbot_keybind)} ({triggerbot_mode})", tag="triggerbot_keybind_button", callback=triggerbot_keybind_callback, width=100)
                        dpg.bind_item_theme(dpg.last_item(), accent_theme)
                    
                    dpg.add_spacer(height=8)
                    dpg.add_slider_int(label="Delay", default_value=triggerbot_delay, min_value=0, max_value=500, callback=triggerbot_delay_callback, tag="triggerbot_delay_slider", width=200)
                
                dpg.add_spacer(height=8)
                
                with dpg.child_window(height=120, width=760, border=True):
                    dpg.bind_item_theme(dpg.last_item(), group_theme)
                    dpg.add_text("Settings", color=(130, 100, 200, 255))
                    dpg.add_separator()
                    dpg.add_spacer(height=5)
                    
                    with dpg.group(horizontal=True):
                        dpg.add_slider_float(label="Pred X", default_value=0.0, min_value=0.0, max_value=100.0, format="%.1f", callback=triggerbot_prediction_x_callback, tag="triggerbot_prediction_x_slider", width=120)
                        dpg.add_slider_float(label="Pred Y", default_value=0.0, min_value=0.0, max_value=100.0, format="%.1f", callback=triggerbot_prediction_y_callback, tag="triggerbot_prediction_y_slider", width=120)
                    
                    dpg.add_combo(label="Mode", items=["Default (FOV)", "Hitpart (R15)", "Hitpart (R6)"], default_value=triggerbot_detection_mode, callback=triggerbot_detection_mode_callback, tag="triggerbot_detection_mode_combo", width=200)
                    
                    dpg.add_slider_float(label="FOV", default_value=triggerbot_fov, min_value=1.0, max_value=200.0, format="%.1f", callback=triggerbot_fov_callback, tag="triggerbot_fov_slider", width=200)
                    dpg.add_checkbox(label="Wall Check", default_value=triggerbot_wallcheck_enabled, callback=triggerbot_wallcheck_callback, tag="triggerbot_wallcheck_checkbox")
                
                # Popup para modo
                with dpg.popup(parent="triggerbot_keybind_button", mousebutton=dpg.mvMouseButton_Right, tag="triggerbot_mode_popup"):
                    dpg.add_text("Mode", color=(130, 100, 200, 255))
                    dpg.add_separator()
                    dpg.add_button(label="Hold", callback=lambda s, a, u: triggerbot_mode_callback(s, "Hold"), width=80)
                    dpg.add_button(label="Toggle", callback=lambda s, a, u: triggerbot_mode_callback(s, "Toggle"), width=80)
                

            # Tab Misc
            with dpg.tab(label="Misc"):
                dpg.add_spacer(height=8)
                
                # Walkspeed
                with dpg.child_window(height=100, width=760, border=True):
                    dpg.bind_item_theme(dpg.last_item(), group_theme)
                    dpg.add_text("Movement", color=(130, 100, 200, 255))
                    dpg.add_separator()
                    dpg.add_spacer(height=5)
                    
                    dpg.add_checkbox(label="Walkspeed", default_value=walkspeed_gui_enabled, callback=walkspeed_gui_toggle, tag="walkspeed_gui_checkbox")
                    dpg.add_slider_float(label="Value", default_value=walkspeed_gui_value, min_value=16.0, max_value=1000.0, format="%.1f", callback=walkspeed_gui_change, tag="walkspeed_gui_slider", show=walkspeed_gui_enabled, width=200)
                
                dpg.add_spacer(height=8)
                
                # Rotation
                with dpg.child_window(height=130, width=760, border=True):
                    dpg.bind_item_theme(dpg.last_item(), group_theme)
                    dpg.add_text("Rotation", color=(130, 100, 200, 255))
                    dpg.add_separator()
                    dpg.add_spacer(height=5)
                    
                    with dpg.group(horizontal=True):
                        dpg.add_checkbox(label="360 Rotation", default_value=rotation_360_enabled, callback=rotation_360_callback, tag="rotation_360_checkbox")
                        dpg.add_spacer(width=15)
                        dpg.add_button(label=f"{get_key_name(rotation_360_keybind)} ({rotation_360_mode})", tag="rotation_360_keybind_button", callback=rotation_360_keybind_callback, width=120)
                        dpg.bind_item_theme(dpg.last_item(), accent_theme)
                    
                    dpg.add_slider_float(label="Speed", default_value=rotation_360_speed, min_value=0.1, max_value=50.0, format="%.1f", callback=rotation_360_speed_callback, tag="rotation_360_speed_slider", width=200)
                    
                    with dpg.group(horizontal=True):
                        dpg.add_combo(["Hold", "Toggle"], default_value=rotation_360_mode, callback=rotation_360_mode_callback, tag="rotation_360_mode_combo", width=100)
                        dpg.add_spacer(width=20)
                        dpg.add_combo(["Mode 1 (Default)", "Mode 2"], default_value=rotation_360_direction_mode, callback=rotation_360_direction_callback, tag="rotation_360_direction_combo", width=150)
                
                dpg.add_spacer(height=8)
                
                # Fly
                with dpg.child_window(height=120, width=760, border=True):
                    dpg.bind_item_theme(dpg.last_item(), group_theme)
                    dpg.add_text("Fly", color=(130, 100, 200, 255))
                    dpg.add_separator()
                    dpg.add_spacer(height=5)
                    
                    with dpg.group(horizontal=True):
                        dpg.add_checkbox(label="Enable", default_value=fly_enabled, callback=fly_callback, tag="fly_checkbox")
                        dpg.add_spacer(width=15)
                        dpg.add_button(label=f"{get_key_name(fly_keybind)} ({fly_mode})", tag="fly_keybind_button", callback=fly_keybind_callback, width=100)
                        dpg.bind_item_theme(dpg.last_item(), accent_theme)
                    
                    dpg.add_spacer(height=8)
                    dpg.add_slider_float(label="Speed", default_value=fly_speed, min_value=10.0, max_value=200.0, format="%.1f", callback=fly_speed_callback, tag="fly_speed_slider", width=200)
                    dpg.add_combo(label="Method", items=["Position", "Velocity"], default_value="Velocity", callback=fly_method_callback, tag="fly_method_combo", width=120)
                
                # Popup para modo fly
                with dpg.popup(parent="fly_keybind_button", mousebutton=dpg.mvMouseButton_Right, tag="fly_mode_popup"):
                    dpg.add_text("Mode", color=(130, 100, 200, 255))
                    dpg.add_separator()
                    dpg.add_button(label="Hold", callback=lambda s, a, u: set_fly_mode("Hold"), width=80)
                    dpg.add_button(label="Toggle", callback=lambda s, a, u: set_fly_mode("Toggle"), width=80)
                
                dpg.add_spacer(height=8)
                
                # Checks
                with dpg.child_window(height=100, width=760, border=True):
                    dpg.bind_item_theme(dpg.last_item(), group_theme)
                    dpg.add_text("Aimbot Checks", color=(130, 100, 200, 255))
                    dpg.add_separator()
                    dpg.add_spacer(height=5)
                    
                    with dpg.group(horizontal=True):
                        dpg.add_checkbox(label="Team Check", default_value=aimbot_ignoreteam, callback=aimbot_ignoreteam_callback, tag="aimbot_ignoreteam_checkbox")
                        dpg.add_spacer(width=15)
                        dpg.add_checkbox(label="Death Check", default_value=aimbot_ignoredead, callback=aimbot_ignoredead_callback, tag="aimbot_ignoredead_checkbox")

            # Tab Config
            with dpg.tab(label="Config"):
                dpg.add_spacer(height=8)
                
                with dpg.child_window(height=350, width=760, border=True):
                    dpg.bind_item_theme(dpg.last_item(), group_theme)
                    dpg.add_text("Configuration", color=(130, 100, 200, 255))
                    dpg.add_separator()
                    dpg.add_spacer(height=10)
                    
                    # Botones más grandes y todos violeta
                    dpg.add_button(label="Save", callback=save_config_callback, width=350, height=35)
                    dpg.bind_item_theme(dpg.last_item(), accent_theme)
                    
                    dpg.add_spacer(height=8)
                    dpg.add_button(label="Load", callback=load_config_callback, width=350, height=35)
                    dpg.bind_item_theme(dpg.last_item(), accent_theme)
                    
                    dpg.add_spacer(height=8)
                    dpg.add_button(label="Delete", callback=delete_config_callback, width=350, height=35)
                    dpg.bind_item_theme(dpg.last_item(), accent_theme)
                    
                    dpg.add_spacer(height=15)
                    dpg.add_listbox(items=get_config_files(), tag="config_listbox", width=350, num_items=8)

    # Aplicar tema global
    dpg.bind_theme(global_theme)
    
    # Configurar viewport minimalista
    dpg.create_viewport(title="Flame External", width=820, height=620, resizable=True)
    dpg.setup_dearpygui()
    dpg.show_viewport()
    
    # Iniciar threads de título y monitoreo
    threading.Thread(target=title_changer, daemon=True).start()
    
    # Iniciar hilo de búsqueda de heads ESP
    threading.Thread(target=esp_head_finder, daemon=True).start()
    
    # Loop principal
    try:
        dpg.start_dearpygui()
    finally:
        # Cleanup al cerrar
        cleanup_resources()
        dpg.destroy_context()
    while dpg.is_dearpygui_running():
        dpg.render_dearpygui_frame()
    
    # Cleanup al cerrar
    cleanup_resources()
    dpg.destroy_context()