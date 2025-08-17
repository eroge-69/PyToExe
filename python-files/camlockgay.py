# ──────────────────────────── IMPORTS ────────────────────────────
import numpy

import sys

import os

import time

import threading

import random

import string

from math import sqrt, pi

from ctypes import windll, byref, Structure, wintypes

import ctypes

import msvcrt 



# Essential imports only

try:

    from numpy import array, float32, linalg, cross, dot, reshape

    import dearpygui.dearpygui as dpg

    from requests import get

    from pymem import Pymem

    from pymem.process import list_processes

    from pymem.exception import ProcessError

    from psutil import pid_exists

    import json

    DEPS_OK = True

except ImportError as e:

    print(f"Missing dependency: {e}")

    input("Press Enter to exit...")

    sys.exit(1)



# ──────────────────────────── GLOBAL VARIABLES ────────────────────────────

pi180 = pi/180

Handle = None

PID = -1

baseAddr = None

pm = Pymem()



aimbot_enabled = False

aimbot_keybind = 2  

aimbot_mode = "Hold"  

aimbot_toggled = False  

waiting_for_keybind = False

injected = False  

aimbot_smoothness_enabled = False

aimbot_smoothness_value = 0.1

aimbot_ignoreteam = False

aimbot_ignoredead = False

aimbot_hitpart = "Head" 

aimbot_prediction_enabled = False
aimbot_prediction_amount = 0.1 # not used
aimbot_prediction_multiplier = 1.0  # not used
aimbot_prediction_x = 0.1  
aimbot_prediction_y = 0.1  




esp_enabled = False

esp_ignoreteam = False

esp_ignoredead = False

aimbot_shake_enabled = False
aimbot_shake_strength = 0.005

# Triggerbot variables
triggerbot_enabled = False
triggerbot_keybind = 1  
triggerbot_mode = "Hold" 
triggerbot_toggled = False
triggerbot_delay = 0
triggerbot_prediction_x = 0.1
triggerbot_prediction_y = 0.1
triggerbot_fov = 50.0



# Walkspeed variables

walkspeed_gui_enabled = False

walkspeed_gui_value = 16

walkspeed_gui_thread = None

walkspeed_gui_active = False



# Game addresses

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



VK_CODES = {

    'Left Mouse': 1, 'Right Mouse': 2, 'Middle Mouse': 4,

    'F1': 112, 'F2': 113, 'F3': 114, 'F4': 115, 'F5': 116, 'F6': 117,

    'A': 65, 'B': 66, 'C': 67, 'D': 68, 'E': 69, 'F': 70,

    'Shift': 16, 'Ctrl': 17, 'Alt': 18, 'Space': 32

}



class RECT(Structure):

    _fields_ = [('left', wintypes.LONG), ('top', wintypes.LONG), ('right', wintypes.LONG), ('bottom', wintypes.LONG)]



class POINT(Structure):

    _fields_ = [('x', wintypes.LONG), ('y', wintypes.LONG)]



# Windows file dialog structures

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



# ──────────────────────────── CORE FUNCTIONS ────────────────────────────

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



def yield_for_program(program_name, printInfo=True):

    global PID, Handle, baseAddr, pm

    for proc in simple_get_processes():

        if proc["Name"] == program_name:

            pm.open_process_from_id(proc["ProcessId"])

            PID = proc["ProcessId"]

            Handle = windll.kernel32.OpenProcess(0x1038, False, PID)


            for module in pm.list_modules():

                if module.name == "RobloxPlayerBeta.exe":

                    baseAddr = module.lpBaseOfDll

                    break

    return False



def is_process_dead():

    return not pid_exists(PID)



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



def find_window_by_title(title):

    return windll.user32.FindWindowW(None, title)



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



def title_changer():

    while True:

        try:

            dpg.configure_item("Primary Window", label="brutalsigma")

            dpg.set_viewport_title("brutalsigma")

        except:

            pass  

        time.sleep(1)



# ──────────────────────────── INITIALIZATION ────────────────────────────


def background_process_monitor():

    global baseAddr

    while True:

        if is_process_dead():

            while not yield_for_program("RobloxPlayerBeta.exe"):

                time.sleep(0.5)

            baseAddr = get_base_addr()

        time.sleep(0.1)



threading.Thread(target=background_process_monitor, daemon=True).start()



def init():

    global dataModel, wsAddr, camAddr, camCFrameRotAddr, plrsAddr, lpAddr, matrixAddr, camPosAddr, injected

    

    try:

        fakeDatamodel = pm.read_longlong(baseAddr + int(offsets['FakeDataModelPointer'], 16))

        print(f'Fake datamodel: {fakeDatamodel:x}')



        dataModel = pm.read_longlong(fakeDatamodel + int(offsets['FakeDataModelToDataModel'], 16))

        print(f'Real datamodel: {dataModel:x}')



        wsAddr = pm.read_longlong(dataModel + int(offsets['Workspace'], 16))

        print(f'Workspace: {wsAddr:x}')



        camAddr = pm.read_longlong(wsAddr + int(offsets['Camera'], 16))

        camCFrameRotAddr = camAddr + int(offsets['CameraRotation'], 16)

        camPosAddr = camAddr + int(offsets['CameraPos'], 16)



        visualEngine = pm.read_longlong(baseAddr + int(offsets['VisualEnginePointer'], 16))

        matrixAddr = visualEngine + int(offsets['viewmatrix'], 16)

        print(f'Matrix: {matrixAddr:x}')



        plrsAddr = FindFirstChildOfClass(dataModel, 'Players')

        print(f'Players: {plrsAddr:x}')



        lpAddr = pm.read_longlong(plrsAddr + int(offsets['LocalPlayer'], 16))

        print(f'Local player: {lpAddr:x}')

        

    except ProcessError:

        print('You forget to open Roblox!')

        return



    print('Injected successfully\n-------------------------------')

    injected = True

    

    def delayed_show():

        time.sleep(1)

        show_main_features()



    threading.Thread(target=delayed_show, daemon=True).start()



def keybind_listener():

    global waiting_for_keybind, aimbot_keybind, triggerbot_keybind, triggerbot_mode, triggerbot_toggled

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

                            # Check which button was waiting for keybind
                            try:
                                dpg.configure_item("keybind_button", label=f"Keybind: {get_key_name(aimbot_keybind)} ({aimbot_mode})")
                            except:
                                pass
                            try:
                                dpg.configure_item("triggerbot_keybind_button", label=f"Keybind: {get_key_name(triggerbot_keybind)} ({triggerbot_mode})")
                            except:
                                pass
                            break

                        try:
                            current_label = dpg.get_item_label("keybind_button")
                            if "..." in current_label:
                                aimbot_keybind = vk_code
                                dpg.configure_item("keybind_button", label=f"Keybind: {get_key_name(vk_code)} ({aimbot_mode})")
                        except:
                            pass
                        
                        try:
                            current_label = dpg.get_item_label("triggerbot_keybind_button")
                            if "..." in current_label:
                                triggerbot_keybind = vk_code
                                dpg.configure_item("triggerbot_keybind_button", label=f"Keybind: {get_key_name(vk_code)} ({triggerbot_mode})")
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
                if target > 0 and matrixAddr > 0:
                    from_pos = [pm.read_float(camPosAddr), pm.read_float(camPosAddr+4), pm.read_float(camPosAddr+8)]
                    to_pos = [pm.read_float(target), pm.read_float(target+4), pm.read_float(target+8)]

                    # Prediction logic (for direct aim)
                    if aimbot_prediction_enabled:
                        try:
                            velocity = [pm.read_float(target - int(offsets['Position'], 16) + int(offsets['Velocity'], 16)),
                                        pm.read_float(target - int(offsets['Position'], 16) + int(offsets['Velocity'], 16) + 4),
                                        pm.read_float(target - int(offsets['Position'], 16) + int(offsets['Velocity'], 16) + 8)]
                            to_pos[0] += velocity[0] * aimbot_prediction_x
                            to_pos[1] += velocity[1] * aimbot_prediction_y
                        except Exception:
                            pass

                    look, up, right = cframe_look_at(from_pos, to_pos)

                    if aimbot_smoothness_enabled:
                        # Get current camera rotation vectors
                        current_right = [pm.read_float(camCFrameRotAddr), pm.read_float(camCFrameRotAddr+12), pm.read_float(camCFrameRotAddr+24)]
                        current_up = [pm.read_float(camCFrameRotAddr+4), pm.read_float(camCFrameRotAddr+16), pm.read_float(camCFrameRotAddr+28)]
                        current_look = [pm.read_float(camCFrameRotAddr+8), pm.read_float(camCFrameRotAddr+20), pm.read_float(camCFrameRotAddr+32)]
                        
                        def lerp(a, b, t):
                            return a + (b - a) * t
                        
                        # Apply smoothing
                        smooth_right = [lerp(current_right[i], -right[i], aimbot_smoothness_value) for i in range(3)]
                        smooth_up = [lerp(current_up[i], up[i], aimbot_smoothness_value) for i in range(3)]
                        smooth_look = [lerp(current_look[i], -look[i], aimbot_smoothness_value) for i in range(3)]
                        
                        # Apply shake to smoothed values and write to camera
                        for i in range(3):
                            shake_r = random.uniform(-aimbot_shake_strength, aimbot_shake_strength) if aimbot_shake_enabled else 0
                            shake_u = random.uniform(-aimbot_shake_strength, aimbot_shake_strength) if aimbot_shake_enabled else 0
                            shake_l = random.uniform(-aimbot_shake_strength, aimbot_shake_strength) if aimbot_shake_enabled else 0
                            
                            pm.write_float(camCFrameRotAddr + i*12, float(smooth_right[i] + shake_r))
                            pm.write_float(camCFrameRotAddr + 4 + i*12, float(smooth_up[i] + shake_u))
                            pm.write_float(camCFrameRotAddr + 8 + i*12, float(smooth_look[i] + shake_l))
                    else:
                        # Direct aim with shake
                        for i in range(3):
                            shake_r = random.uniform(-aimbot_shake_strength, aimbot_shake_strength) if aimbot_shake_enabled else 0
                            shake_u = random.uniform(-aimbot_shake_strength, aimbot_shake_strength) if aimbot_shake_enabled else 0
                            shake_l = random.uniform(-aimbot_shake_strength, aimbot_shake_strength) if aimbot_shake_enabled else 0

                            pm.write_float(camCFrameRotAddr + i*12, float(-right[i] + shake_r))
                            pm.write_float(camCFrameRotAddr + 4 + i*12, float(up[i] + shake_u))
                            pm.write_float(camCFrameRotAddr + 8 + i*12, float(-look[i] + shake_l))

                else:
                    # Target acquisition logic
                    target = 0
                    hwnd_roblox = find_window_by_title("Roblox")
                    if hwnd_roblox and matrixAddr > 0:
                        left, top, right, bottom = get_client_rect_on_screen(hwnd_roblox)
                        matrix_flat = [pm.read_float(matrixAddr + i * 4) for i in range(16)]
                        view_proj_matrix = reshape(array(matrix_flat, dtype=float32), (4, 4))
                        lpTeam = pm.read_longlong(lpAddr + int(offsets['Team'], 16))
                        width = right - left
                        height = bottom - top
                        widthCenter = width/2
                        heightCenter = height/2
                        minDistance = float('inf')
                        
                        for v in GetChildren(plrsAddr):
                            if v != lpAddr:
                                if not aimbot_ignoreteam or pm.read_longlong(v + int(offsets['Team'], 16)) != lpTeam:
                                    char = pm.read_longlong(v + int(offsets['ModelInstance'], 16))
                                    # Use selected hit part
                                    hitpart = FindFirstChild(char, aimbot_hitpart)
                                    hum = FindFirstChildOfClass(char, 'Humanoid')
                                    if hitpart and hum:
                                        health = pm.read_float(hum + int(offsets['Health'], 16))
                                        if aimbot_ignoredead and health <= 0:
                                            continue
                                        primitive = pm.read_longlong(hitpart + int(offsets['Primitive'], 16))
                                        targetPos = primitive + int(offsets['Position'], 16)
                                        obj_pos = array([
                                            pm.read_float(targetPos),
                                            pm.read_float(targetPos + 4),
                                            pm.read_float(targetPos + 8)
                                        ], dtype=float32)
                                        if aimbot_prediction_enabled:
                                            try:
                                                velocity = [pm.read_float(primitive + int(offsets['Velocity'], 16)),
                                                            pm.read_float(primitive + int(offsets['Velocity'], 16) + 4),
                                                            pm.read_float(primitive + int(offsets['Velocity'], 16) + 8)]
                                                predicted_pos = obj_pos.copy()
                                                predicted_pos[0] += velocity[0] * aimbot_prediction_x
                                                predicted_pos[1] += velocity[1] * aimbot_prediction_y
                                            except Exception:
                                                predicted_pos = obj_pos
                                        else:
                                            predicted_pos = obj_pos
                                        screen_coords = world_to_screen_with_matrix(predicted_pos, view_proj_matrix, width, height)
                                        if screen_coords is not None:
                                            distance = sqrt((widthCenter - screen_coords[0])**2 + (heightCenter - screen_coords[1])**2)
                                            if distance < minDistance:
                                                minDistance = distance
                                                target = targetPos
            else:
                target = 0
        else:
            aimbot_toggled = False  
            time.sleep(0.1)



threading.Thread(target=aimbotLoop, daemon=True).start()

def triggerbotLoop():
    global triggerbot_enabled, triggerbot_toggled
    key_pressed_last_frame = False
    last_shot_time = 0

    while True:
        if triggerbot_enabled and injected and lpAddr > 0 and plrsAddr > 0 and matrixAddr > 0:
            try:
                # Get current time for rate limiting
                current_time = time.time()
                
                hwnd_roblox = find_window_by_title("Roblox")
                if not hwnd_roblox:
                    time.sleep(0.05)
                    continue
                    
                left, top, right, bottom = get_client_rect_on_screen(hwnd_roblox)
                width = right - left
                height = bottom - top
                widthCenter = width/2
                heightCenter = height/2

                # Get matrix and camera position
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
                    lpTeam = pm.read_longlong(lpAddr + int(offsets['Team'], 16))
                    minDistance = float('inf')
                    target_found = False
                    targets_scanned = 0

                    for v in GetChildren(plrsAddr):
                        if v != lpAddr:
                            targets_scanned += 1
                            try:
                                # Check team if ignore team is enabled
                                if aimbot_ignoreteam:
                                    playerTeam = pm.read_longlong(v + int(offsets['Team'], 16))
                                    if playerTeam == lpTeam:
                                        continue

                                char = pm.read_longlong(v + int(offsets['ModelInstance'], 16))
                                if char:
                                    head = FindFirstChild(char, 'Head')
                                    if head:
                                        # Check if player is alive
                                        if aimbot_ignoredead:
                                            hum = FindFirstChildOfClass(char, 'Humanoid')
                                            if hum:
                                                health = pm.read_float(hum + int(offsets['Health'], 16))
                                                if health <= 0:
                                                    continue

                                        primitive = pm.read_longlong(head + int(offsets['Primitive'], 16))
                                        if primitive:
                                            targetPos = primitive + int(offsets['Position'], 16)
                                            obj_pos = array([
                                                pm.read_float(targetPos),
                                                pm.read_float(targetPos + 4),
                                                pm.read_float(targetPos + 8)
                                            ], dtype=float32)

                                            # Apply prediction if enabled
                                            if triggerbot_prediction_x > 0 or triggerbot_prediction_y > 0:
                                                try:
                                                    velocity = [pm.read_float(primitive + int(offsets['Velocity'], 16)),
                                                                pm.read_float(primitive + int(offsets['Velocity'], 16) + 4),
                                                                pm.read_float(primitive + int(offsets['Velocity'], 16) + 8)]
                                                    obj_pos[0] += velocity[0] * triggerbot_prediction_x
                                                    obj_pos[1] += velocity[1] * triggerbot_prediction_y
                                                except Exception:
                                                    pass

                                            screen_coords = world_to_screen_with_matrix(obj_pos, view_proj_matrix, width, height)
                                            if screen_coords is not None:
                                                distance = sqrt((widthCenter - screen_coords[0])**2 + (heightCenter - screen_coords[1])**2)
                                                if distance <= triggerbot_fov:
                                                    if distance < minDistance:
                                                        minDistance = distance
                                                        target_found = True
                            except Exception:
                                continue

                    # Shoot if target found and enough time has passed since last shot
                    if target_found and (current_time - last_shot_time) >= (triggerbot_delay / 1000.0):
                        windll.user32.mouse_event(0x0002, 0, 0, 0, 0)  # Mouse down
                        time.sleep(0.005)  # Very short delay
                        windll.user32.mouse_event(0x0004, 0, 0, 0, 0)  # Mouse up
                        last_shot_time = current_time
                        
                else:
                    if triggerbot_mode == "Hold":
                        triggerbot_toggled = False
                        
            except Exception as e:
                pass
        else:
            time.sleep(0.05)
        
        # Reduced sleep for better responsiveness
        time.sleep(0.005)

threading.Thread(target=triggerbotLoop, daemon=True).start()



# ──────────────────────────── GUI CALLBACKS ────────────────────────────

def aimbot_callback(sender, app_data):

    global aimbot_enabled, aimbot_toggled

    if not injected:

        return

    aimbot_enabled = app_data

    if not app_data:

        aimbot_toggled = False  



def esp_callback(sender, app_data):

    global esp_enabled

    if not injected:

        return

    esp_enabled = app_data

    print(f"ESP {'enabled' if app_data else 'disabled'}")



def esp_ignoreteam_callback(sender, app_data):

    global esp_ignoreteam

    esp_ignoreteam = app_data



def esp_ignoredead_callback(sender, app_data):

    global esp_ignoredead

    esp_ignoredead = app_data



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



def aimbot_smoothness_callback(sender, app_data):

    global aimbot_smoothness_enabled

    aimbot_smoothness_enabled = app_data

    if app_data:

        dpg.show_item("smoothness_slider")

    else:

        dpg.hide_item("smoothness_slider")



def smoothness_value_callback(sender, app_data):

    global aimbot_smoothness_value

    aimbot_smoothness_value = app_data



def keybind_callback():

    global waiting_for_keybind

    if not waiting_for_keybind:

        waiting_for_keybind = True

        dpg.configure_item("keybind_button", label="... (ESC to cancel)")

    # The right-click popup is handled by dpg.popup



def inject_callback():

    init()



def get_camera_addr_gui():

    try:

        a = pm.read_longlong(baseAddr + int(offsets["VisualEnginePointer"], 16))

        b = pm.read_longlong(a + int(offsets["VisualEngineToDataModel1"], 16))

        c = pm.read_longlong(b + int(offsets["VisualEngineToDataModel2"], 16))

        d = pm.read_longlong(c + int(offsets["Workspace"], 16))

        return pm.read_longlong(d + int(offsets["Camera"], 16))

    except:

        return None



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

    walkspeed_gui_value = value



def show_main_features():

    dpg.hide_item("injector_text")

    dpg.hide_item("inject_button")

    dpg.show_item("aimbot_group")

    dpg.show_item("aimbot_smoothness_checkbox")

    dpg.show_item("aimbot_ignoreteam_checkbox")

    dpg.show_item("aimbot_ignoredead_checkbox")

    dpg.show_item("esp_checkbox")

    dpg.show_item("esp_ignoreteam_checkbox")

    dpg.show_item("esp_ignoredead_checkbox")

    dpg.show_item("walkspeed_gui_checkbox")

    dpg.show_item("aimbot_hitpart_combo")

    dpg.show_item("aimbot_prediction_checkbox")
    dpg.show_item("aimbot_shake_checkbox")
    if aimbot_shake_enabled:
        dpg.show_item("aimbot_shake_slider")

    if aimbot_prediction_enabled:

        dpg.show_item("prediction_x_slider")

        dpg.show_item("prediction_y_slider")

    # Show triggerbot elements
    dpg.show_item("triggerbot_checkbox")
    dpg.show_item("triggerbot_keybind_button")
    dpg.show_item("triggerbot_delay_slider")
    dpg.show_item("triggerbot_prediction_x_slider")
    dpg.show_item("triggerbot_prediction_y_slider")
    dpg.show_item("triggerbot_fov_slider")



def aimbot_hitpart_callback(sender, app_data):

    global aimbot_hitpart

    aimbot_hitpart = app_data



def aimbot_prediction_checkbox(sender, app_data):

    global aimbot_prediction_enabled

    aimbot_prediction_enabled = app_data

    dpg.configure_item("prediction_x_slider", show=app_data)

    dpg.configure_item("prediction_y_slider", show=app_data)



def prediction_amount_callback(sender, app_data):

    global aimbot_prediction_amount

    aimbot_prediction_amount = app_data



def prediction_multiplier_callback(sender, app_data):

    global aimbot_prediction_multiplier

    aimbot_prediction_multiplier = app_data



def prediction_x_callback(sender, app_data):
    global aimbot_prediction_x
    aimbot_prediction_x = app_data

def prediction_y_callback(sender, app_data):
    global aimbot_prediction_y
    aimbot_prediction_y = app_data



def aimbot_shake_callback(sender, app_data):
    global aimbot_shake_enabled
    aimbot_shake_enabled = app_data
    dpg.configure_item("aimbot_shake_slider", show=app_data)

def aimbot_shake_strength_callback(sender, app_data):
    global aimbot_shake_strength
    aimbot_shake_strength = app_data

# Triggerbot callbacks
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

def triggerbot_keybind_callback():
    global waiting_for_keybind
    if not waiting_for_keybind:
        waiting_for_keybind = True
        dpg.configure_item("triggerbot_keybind_button", label="... (ESC to cancel)")

def triggerbot_delay_callback(sender, app_data):
    global triggerbot_delay
    triggerbot_delay = app_data

def triggerbot_prediction_x_callback(sender, app_data):
    global triggerbot_prediction_x
    triggerbot_prediction_x = app_data

def triggerbot_prediction_y_callback(sender, app_data):
    global triggerbot_prediction_y
    triggerbot_prediction_y = app_data

def triggerbot_fov_callback(sender, app_data):
    global triggerbot_fov
    triggerbot_fov = app_data

# ──────────────────────────── CONFIG FUNCTIONS ────────────────────────────

def get_configs_directory():
    """Get the configs directory path relative to the script"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    configs_dir = os.path.join(script_dir, "configs")
    
    # Create configs directory if it doesn't exist
    if not os.path.exists(configs_dir):
        os.makedirs(configs_dir)
    
    return configs_dir

def windows_save_file_dialog():
    """Windows native save file dialog"""
    try:
        configs_dir = get_configs_directory()
        
        # Create buffer for filename and set initial directory
        filename_buffer = ctypes.create_unicode_buffer(260)
        # Pre-populate with configs directory path
        initial_path = os.path.join(configs_dir, "config.json")
        filename_buffer.value = initial_path
        
        # Setup OPENFILENAME structure
        ofn = OPENFILENAME()
        ofn.lStructSize = ctypes.sizeof(OPENFILENAME)
        ofn.hwndOwner = None
        ofn.lpstrFilter = "JSON Files\0*.json\0All Files\0*.*\0"
        ofn.lpstrFile = ctypes.cast(filename_buffer, wintypes.LPWSTR)
        ofn.nMaxFile = 260
        ofn.lpstrInitialDir = configs_dir
        ofn.lpstrTitle = "Save Config"
        ofn.lpstrDefExt = "json"
        ofn.Flags = 0x00000002 | 0x00000004  # OFN_OVERWRITEPROMPT | OFN_HIDEREADONLY
        
        # Call GetSaveFileName
        if windll.comdlg32.GetSaveFileNameW(byref(ofn)):
            selected_path = filename_buffer.value
            # Ensure the file is saved in configs directory
            if not selected_path.startswith(configs_dir):
                filename = os.path.basename(selected_path)
                selected_path = os.path.join(configs_dir, filename)
            return selected_path
        return None
    except Exception as e:
        print(f"Error in save dialog: {e}")
        return None

def windows_open_file_dialog():
    """Windows native open file dialog"""
    try:
        configs_dir = get_configs_directory()
        
        # Create buffer for filename
        filename_buffer = ctypes.create_unicode_buffer(260)
        
        # Setup OPENFILENAME structure
        ofn = OPENFILENAME()
        ofn.lStructSize = ctypes.sizeof(OPENFILENAME)
        ofn.hwndOwner = None
        ofn.lpstrFilter = "JSON Files\0*.json\0All Files\0*.*\0"
        ofn.lpstrFile = ctypes.cast(filename_buffer, wintypes.LPWSTR)
        ofn.nMaxFile = 260
        ofn.lpstrInitialDir = configs_dir
        ofn.lpstrTitle = "Load Config"
        ofn.Flags = 0x00001000 | 0x00000004  # OFN_FILEMUSTEXIST | OFN_HIDEREADONLY
        
        # Call GetOpenFileName
        if windll.comdlg32.GetOpenFileNameW(byref(ofn)):
            return filename_buffer.value
        return None
    except Exception as e:
        print(f"Error in open dialog: {e}")
        return None

def save_config_callback():
    """Save current configuration to a JSON file"""
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
                    "ignoredead": aimbot_ignoredead
                },
                "prediction": {
                    "enabled": aimbot_prediction_enabled,
                    "x": aimbot_prediction_x,
                    "y": aimbot_prediction_y
                },
                "smoothness": {
                    "enabled": aimbot_smoothness_enabled,
                    "value": aimbot_smoothness_value
                },
                "shake": {
                    "enabled": aimbot_shake_enabled,
                    "strength": aimbot_shake_strength
                },
                "triggerbot": {
                    "enabled": triggerbot_enabled,
                    "keybind": triggerbot_keybind,
                    "mode": triggerbot_mode,
                    "delay": triggerbot_delay,
                    "prediction_x": triggerbot_prediction_x,
                    "prediction_y": triggerbot_prediction_y,
                    "fov": triggerbot_fov
                },
                "esp": {
                    "enabled": esp_enabled,
                    "ignoreteam": esp_ignoreteam,
                    "ignoredead": esp_ignoredead
                },
                "walkspeed": {
                    "enabled": walkspeed_gui_enabled,
                    "value": walkspeed_gui_value
                }
            }
            
            with open(file_path, 'w') as f:
                json.dump(config_data, f, indent=4)
            
            print(f"Config saved to: {file_path}")
            
    except Exception as e:
        print(f"Error saving config: {e}")

def load_config_callback():
    """Load configuration from a JSON file"""
    try:
        file_path = windows_open_file_dialog()
        
        if file_path:
            with open(file_path, 'r') as f:
                config_data = json.load(f)
            
            # Load aimbot settings
            if "aimbot" in config_data:
                aimbot_config = config_data["aimbot"]
                global aimbot_enabled, aimbot_keybind, aimbot_mode, aimbot_hitpart
                global aimbot_ignoreteam, aimbot_ignoredead
                
                if "enabled" in aimbot_config:
                    aimbot_enabled = aimbot_config["enabled"]
                    dpg.set_value("aimbot_checkbox", aimbot_enabled)
                
                if "keybind" in aimbot_config:
                    aimbot_keybind = aimbot_config["keybind"]
                    dpg.configure_item("keybind_button", label=f"Keybind: {get_key_name(aimbot_keybind)} ({aimbot_mode})")
                
                if "mode" in aimbot_config:
                    aimbot_mode = aimbot_config["mode"]
                    dpg.configure_item("keybind_button", label=f"Keybind: {get_key_name(aimbot_keybind)} ({aimbot_mode})")
                
                if "hitpart" in aimbot_config:
                    aimbot_hitpart = aimbot_config["hitpart"]
                    dpg.set_value("aimbot_hitpart_combo", aimbot_hitpart)
                
                if "ignoreteam" in aimbot_config:
                    aimbot_ignoreteam = aimbot_config["ignoreteam"]
                    dpg.set_value("aimbot_ignoreteam_checkbox", aimbot_ignoreteam)
                
                if "ignoredead" in aimbot_config:
                    aimbot_ignoredead = aimbot_config["ignoredead"]
                    dpg.set_value("aimbot_ignoredead_checkbox", aimbot_ignoredead)
            
            # Load prediction settings
            if "prediction" in config_data:
                prediction_config = config_data["prediction"]
                global aimbot_prediction_enabled, aimbot_prediction_x, aimbot_prediction_y
                
                if "enabled" in prediction_config:
                    aimbot_prediction_enabled = prediction_config["enabled"]
                    dpg.set_value("aimbot_prediction_checkbox", aimbot_prediction_enabled)
                    dpg.configure_item("prediction_x_slider", show=aimbot_prediction_enabled)
                    dpg.configure_item("prediction_y_slider", show=aimbot_prediction_enabled)
                
                if "x" in prediction_config:
                    aimbot_prediction_x = prediction_config["x"]
                    dpg.set_value("prediction_x_slider", aimbot_prediction_x)
                
                if "y" in prediction_config:
                    aimbot_prediction_y = prediction_config["y"]
                    dpg.set_value("prediction_y_slider", aimbot_prediction_y)
            
            # Load smoothness settings
            if "smoothness" in config_data:
                smoothness_config = config_data["smoothness"]
                global aimbot_smoothness_enabled, aimbot_smoothness_value
                
                if "enabled" in smoothness_config:
                    aimbot_smoothness_enabled = smoothness_config["enabled"]
                    dpg.set_value("aimbot_smoothness_checkbox", aimbot_smoothness_enabled)
                    dpg.configure_item("smoothness_slider", show=aimbot_smoothness_enabled)
                
                if "value" in smoothness_config:
                    aimbot_smoothness_value = smoothness_config["value"]
                    dpg.set_value("smoothness_slider", aimbot_smoothness_value)
            
            # Load shake settings
            if "shake" in config_data:
                shake_config = config_data["shake"]
                global aimbot_shake_enabled, aimbot_shake_strength
                
                if "enabled" in shake_config:
                    aimbot_shake_enabled = shake_config["enabled"]
                    dpg.set_value("aimbot_shake_checkbox", aimbot_shake_enabled)
                    dpg.configure_item("aimbot_shake_slider", show=aimbot_shake_enabled)
                
                if "strength" in shake_config:
                    aimbot_shake_strength = shake_config["strength"]
                    dpg.set_value("aimbot_shake_slider", aimbot_shake_strength)
            
            # Load ESP settings
            if "esp" in config_data:
                esp_config = config_data["esp"]
                global esp_enabled, esp_ignoreteam, esp_ignoredead
                
                if "enabled" in esp_config:
                    esp_enabled = esp_config["enabled"]
                    dpg.set_value("esp_checkbox", esp_enabled)
                
                if "ignoreteam" in esp_config:
                    esp_ignoreteam = esp_config["ignoreteam"]
                    dpg.set_value("esp_ignoreteam_checkbox", esp_ignoreteam)
                
                if "ignoredead" in esp_config:
                    esp_ignoredead = esp_config["ignoredead"]
                    dpg.set_value("esp_ignoredead_checkbox", esp_ignoredead)
            
            # Load triggerbot settings
            if "triggerbot" in config_data:
                triggerbot_config = config_data["triggerbot"]
                global triggerbot_enabled, triggerbot_keybind, triggerbot_mode
                global triggerbot_delay, triggerbot_prediction_x, triggerbot_prediction_y, triggerbot_fov
                
                if "enabled" in triggerbot_config:
                    triggerbot_enabled = triggerbot_config["enabled"]
                    dpg.set_value("triggerbot_checkbox", triggerbot_enabled)
                
                if "keybind" in triggerbot_config:
                    triggerbot_keybind = triggerbot_config["keybind"]
                    dpg.configure_item("triggerbot_keybind_button", label=f"Keybind: {get_key_name(triggerbot_keybind)} ({triggerbot_mode})")
                
                if "mode" in triggerbot_config:
                    triggerbot_mode = triggerbot_config["mode"]
                    dpg.configure_item("triggerbot_keybind_button", label=f"Keybind: {get_key_name(triggerbot_keybind)} ({triggerbot_mode})")
                
                if "delay" in triggerbot_config:
                    triggerbot_delay = triggerbot_config["delay"]
                    dpg.set_value("triggerbot_delay_slider", triggerbot_delay)
                
                if "prediction_x" in triggerbot_config:
                    triggerbot_prediction_x = triggerbot_config["prediction_x"]
                    dpg.set_value("triggerbot_prediction_x_slider", triggerbot_prediction_x)
                
                if "prediction_y" in triggerbot_config:
                    triggerbot_prediction_y = triggerbot_config["prediction_y"]
                    dpg.set_value("triggerbot_prediction_y_slider", triggerbot_prediction_y)
                
                if "fov" in triggerbot_config:
                    triggerbot_fov = triggerbot_config["fov"]
                    dpg.set_value("triggerbot_fov_slider", triggerbot_fov)

            # Load walkspeed settings
            if "walkspeed" in config_data:
                walkspeed_config = config_data["walkspeed"]
                global walkspeed_gui_enabled, walkspeed_gui_value
                
                if "enabled" in walkspeed_config:
                    walkspeed_gui_enabled = walkspeed_config["enabled"]
                    dpg.set_value("walkspeed_gui_checkbox", walkspeed_gui_enabled)
                    dpg.configure_item("walkspeed_gui_slider", show=walkspeed_gui_enabled)
                
                if "value" in walkspeed_config:
                    walkspeed_gui_value = walkspeed_config["value"]
                    dpg.set_value("walkspeed_gui_slider", walkspeed_gui_value)
            
            print(f"Config loaded from: {file_path}")
            
    except Exception as e:
        print(f"Error loading config: {e}")
# ──────────────────────────── GUI CREATION ────────────────────────────
# ───────── Sakura License Menu ─────────
SAKURA = "\033[95m"   # Hồng Sakura
RESET = "\033[0m"

def main_menu():
    os.system('cls' if os.name == 'nt' else 'clear')
    print(SAKURA + "[+] Enter" + RESET)
    print(SAKURA + "[-] Exit" + RESET)
    choice = input(SAKURA + ">>> " + RESET).strip()
    if choice == "+":
        return True   # tiếp tục sang menu nhập key
    elif choice == "-":
        sys.exit(0)   # thoát luôn
    else:
        print(SAKURA + "[!] Invalid option" + RESET)
        time.sleep(1)
        return main_menu()   # lặp lại nếu nhập sai


def check_license():
    """Hiển thị menu nhập key"""
    os.system('cls' if os.name == 'nt' else 'clear')
    print(SAKURA + "[~] Please enter your license key" + RESET)
    print(SAKURA + ">>> " + RESET, end="", flush=True)

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
                    print(SAKURA + char + RESET, end="", flush=True)

            if license_key == "sigma":
                os.system('cls' if os.name == 'nt' else 'clear')
                print(SAKURA + "[warning] updater: checking if directory exists" + RESET, end="", flush=True)
                time.sleep(3)
                try:
                    ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 6)
                except Exception:
                    pass
                return True
            else:
                print(SAKURA + "[ERROR] Invalid license key!" + RESET)
                print(SAKURA + ">>> " + RESET, end="", flush=True)
        except (EOFError, KeyboardInterrupt):
            print(SAKURA + "\n[INFO] License verification cancelled" + RESET)
            return False
if __name__ == "__main__":
    if not check_license():
        sys.exit(0)
    
    try:
        offsets = get('https://offsets.ntgetwritewatch.workers.dev/offsets.json').json()
        setOffsets(int(offsets['Name'], 16), int(offsets['Children'], 16))
    except Exception as e:
        pass
    
    threading.Thread(target=background_process_monitor, daemon=True).start()
# ================== GUI ==================
dpg.create_context()

with dpg.window(label="brutal.sybau", tag="Primary Window", width=600, height=450,
                no_close=True, no_move=True, no_resize=True):

    with dpg.tab_bar():

        # AIMBOT TAB
        with dpg.tab(label="Aimbot"):
            dpg.add_checkbox(label="Enable Aimbot", default_value=aimbot_enabled,
                             callback=aimbot_callback, tag="aimbot_checkbox")
            dpg.add_button(label=f"Keybind: {get_key_name(aimbot_keybind)} ({aimbot_mode})",
                           tag="keybind_button", callback=keybind_callback)
            dpg.add_combo(["Head","Torso","UpperTorso","LowerTorso","HumanoidRootPart"],
                          default_value=aimbot_hitpart, callback=aimbot_hitpart_callback,
                          tag="aimbot_hitpart_combo", width=140)

            dpg.add_checkbox(label="Enable Prediction", default_value=aimbot_prediction_enabled,
                             callback=aimbot_prediction_checkbox, tag="aimbot_prediction_checkbox")
            dpg.add_slider_float(label="Prediction X", default_value=aimbot_prediction_x,
                                 min_value=0.0, max_value=10.0, format="%.2f",
                                 callback=prediction_x_callback, tag="prediction_x_slider", width=150)
            dpg.add_slider_float(label="Prediction Y", default_value=aimbot_prediction_y,
                                 min_value=0.0, max_value=10.0, format="%.2f",
                                 callback=prediction_y_callback, tag="prediction_y_slider", width=150)

            dpg.add_checkbox(label="Smoothness", default_value=aimbot_smoothness_enabled,
                             callback=aimbot_smoothness_callback, tag="aimbot_smoothness_checkbox")
            dpg.add_slider_float(label="Smooth Value", default_value=aimbot_smoothness_value,
                                 min_value=0.001, max_value=1.90, format="%.2f",
                                 callback=smoothness_value_callback, tag="smoothness_slider", width=200)

            dpg.add_checkbox(label="Ignore Team", default_value=aimbot_ignoreteam,
                             callback=aimbot_ignoreteam_callback, tag="aimbot_ignoreteam_checkbox")
            dpg.add_checkbox(label="Ignore Dead", default_value=aimbot_ignoredead,
                             callback=aimbot_ignoredead_callback, tag="aimbot_ignoredead_checkbox")
            dpg.add_checkbox(label="Shake", default_value=aimbot_shake_enabled,
                             callback=aimbot_shake_callback, tag="aimbot_shake_checkbox")
            dpg.add_slider_float(label="Shake Strength", default_value=aimbot_shake_strength,
                                 min_value=0.000, max_value=0.05, format="%.3f",
                                 callback=aimbot_shake_strength_callback, tag="aimbot_shake_slider", width=200)

        # TRIGGERBOT TAB
        with dpg.tab(label="Triggerbot"):
            dpg.add_checkbox(label="Enable Triggerbot", default_value=triggerbot_enabled,
                             callback=triggerbot_callback, tag="triggerbot_checkbox")
            dpg.add_button(label=f"Keybind: {get_key_name(triggerbot_keybind)} ({triggerbot_mode})",
                           tag="triggerbot_keybind_button", callback=triggerbot_keybind_callback)
            dpg.add_slider_int(label="Delay (ms)", default_value=triggerbot_delay,
                               min_value=0, max_value=20,
                               callback=triggerbot_delay_callback, tag="triggerbot_delay_slider", width=150)
            dpg.add_slider_float(label="Prediction X", default_value=triggerbot_prediction_x,
                                 min_value=0.0, max_value=10.0, format="%.2f",
                                 callback=triggerbot_prediction_x_callback, tag="triggerbot_prediction_x_slider", width=150)
            dpg.add_slider_float(label="Prediction Y", default_value=triggerbot_prediction_y,
                                 min_value=0.0, max_value=10.0, format="%.2f",
                                 callback=triggerbot_prediction_y_callback, tag="triggerbot_prediction_y_slider", width=150)
            dpg.add_slider_float(label="FOV", default_value=triggerbot_fov,
                                 min_value=1.0, max_value=200.0, format="%.1f",
                                 callback=triggerbot_fov_callback, tag="triggerbot_fov_slider", width=200)

        # VISUALS TAB
        with dpg.tab(label="Visuals"):
            dpg.add_checkbox(label="Enable ESP", default_value=esp_enabled,
                             callback=esp_callback, tag="esp_checkbox")
            dpg.add_checkbox(label="Ignore Team", default_value=esp_ignoreteam,
                             callback=esp_ignoreteam_callback, tag="esp_ignoreteam_checkbox")
            dpg.add_checkbox(label="Ignore Dead", default_value=esp_ignoredead,
                             callback=esp_ignoredead_callback, tag="esp_ignoredead_checkbox")

        # MISC TAB
        with dpg.tab(label="Misc"):
            dpg.add_checkbox(label="Enable Walkspeed", default_value=walkspeed_gui_enabled,
                             callback=walkspeed_gui_toggle, tag="walkspeed_gui_checkbox")
            dpg.add_slider_float(label="Walkspeed Value", tag="walkspeed_gui_slider",
                                 default_value=walkspeed_gui_value, min_value=16, max_value=500,
                                 callback=walkspeed_gui_change, width=250)

            dpg.add_button(label="Inject", tag="inject_button", callback=inject_callback, width=120)

        # CONFIG TAB
        with dpg.tab(label="Config"):
            with dpg.group(horizontal=True):
                dpg.add_button(label="Save Config", callback=save_config_callback, width=120)
                dpg.add_button(label="Load Config", callback=load_config_callback, width=120)


# ================== THEME ==================
with dpg.theme() as brutal_theme:
    with dpg.theme_component(dpg.mvAll):
        dpg.add_theme_color(dpg.mvThemeCol_WindowBg, (15, 15, 15), category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_ChildBg, (20, 20, 20), category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_Border, (60, 60, 60), category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_Text, (220, 220, 220), category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_Button, (90, 60, 180), category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (110, 80, 200), category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, (130, 100, 220), category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_Tab, (25, 25, 25), category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_TabHovered, (90, 60, 180), category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_TabActive, (120, 90, 200), category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_FrameBg, (30, 30, 30), category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_FrameBgHovered, (80, 50, 140), category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_FrameBgActive, (100, 70, 180), category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_SliderGrab, (150, 120, 240), category=dpg.mvThemeCat_Core)
        dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 2, category=dpg.mvThemeCat_Core)
        dpg.add_theme_style(dpg.mvStyleVar_TabRounding, 2, category=dpg.mvThemeCat_Core)
        dpg.add_theme_style(dpg.mvStyleVar_GrabRounding, 2, category=dpg.mvThemeCat_Core)
        dpg.add_theme_style(dpg.mvStyleVar_WindowPadding, 8, 8, category=dpg.mvThemeCat_Core)

dpg.bind_theme(brutal_theme)
dpg.create_viewport(title="yeno-external", width=600, height=450, decorated=False)
dpg.setup_dearpygui()
dpg.set_primary_window("Primary Window", True)

dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()



# ========== ESP Overlay Integration (PyQt5 + OpenGL) ==========

from PyQt5.QtWidgets import QApplication, QOpenGLWidget

from PyQt5.QtCore import Qt, QTimer

from PyQt5.QtGui import QColor

from OpenGL.GL import *

from numpy import array, float32, empty, einsum

from struct import unpack_from



esp_instance = None

esp_app = None

esp_enabled_flag = False

heads = []

colors = []



class ESPOverlay(QOpenGLWidget):

    def __init__(self):

        super().__init__()

        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)

        self.setAttribute(Qt.WA_TranslucentBackground)

        self.setAttribute(Qt.WA_NoSystemBackground)

        self.resize(1920, 1080)

        self.time = 0

        self.plr_data = []

        self.last_matrix = None

        self.prev_geometry = (0, 0, 0, 0)

        self.startLineX = 0

        self.startLineY = 0

        self.color = 'white'



        hwnd = self.winId().__int__()

        ex_style = windll.user32.GetWindowLongW(hwnd, -20)

        ex_style |= 0x80000 | 0x20

        windll.user32.SetWindowLongW(hwnd, -20, ex_style)



    def initializeGL(self):

        glClearColor(0.0, 0.0, 0.0, 0.0)

        glEnable(GL_BLEND)

        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        glLineWidth(3.0)

        glEnable(GL_LINE_SMOOTH)

        glHint(GL_LINE_SMOOTH_HINT, GL_NICEST)



    def resizeGL(self, w, h):

        glViewport(0, 0, w, h)

        glMatrixMode(GL_PROJECTION)

        glLoadIdentity()

        glOrtho(0, w, h, 0, -1, 1)

        glMatrixMode(GL_MODELVIEW)



    def paintGL(self):

        glClear(GL_COLOR_BUFFER_BIT)

        glLoadIdentity()

        for x, y, color in self.plr_data:

            r, g, b = QColor(color).redF(), QColor(color).greenF(), QColor(color).blueF()

            glColor3f(r, g, b)

            glBegin(GL_LINES)

            glVertex2f(self.startLineX, self.startLineY)

            glVertex2f(x, y)

            glEnd()



    def update_players(self):

        if not esp_enabled_flag or lpAddr == 0 or plrsAddr == 0 or matrixAddr == 0:

            return



        from time import time

        from numpy import array, float32, empty, einsum



        vecs_np = empty((50, 4), dtype=float32)

        count = 0

        self.plr_data.clear()



        if time() - self.time > 1:

            hwnd_roblox = find_window_by_title("Roblox")

            if hwnd_roblox:

                x, y, r, b = get_client_rect_on_screen(hwnd_roblox)

                new_geom = (x, y, r - x, b - y)

                if new_geom != self.prev_geometry:

                    self.setGeometry(*new_geom)

                    self.prev_geometry = new_geom

                    self.startLineX = self.width() / 2

                    self.startLineY = self.height() - self.height() / 20

            self.time = time()



        matrixRaw = pm.read_bytes(matrixAddr, 64)

        view_proj_matrix = array(unpack_from("<16f", matrixRaw, 0), dtype=float32).reshape(4, 4)



        for head in heads:

            try:

                className = GetClassName(head)

                if GetName(head) == 'Head' and className in ['Part', 'BasePart', 'MeshPart']:

                    vec = unpack_from("<fff", pm.read_bytes(DRP(head + offsets['Primitive']), 12), 0)

                    vecs_np[count, :3] = vec

                    vecs_np[count, 3] = 1.0

                    count += 1

            except:

                continue



        if count == 0:

            return



        clip_coords = einsum('ij,nj->ni', view_proj_matrix, vecs_np[:count])

        for idx, clip in enumerate(clip_coords):

            if clip[3] != 0:

                ndc = clip[:3] / clip[3]

                if 0 <= ndc[2] <= 1:

                    x = int((ndc[0] + 1) * 0.5 * self.width())

                    y = int((1 - ndc[1]) * 0.5 * self.height())

                    col = colors[idx] if idx < len(colors) else 'white'

                    self.plr_data.append((x, y, col))

        self.update()



def headAndHumFinder():

    global heads, colors

    from time import sleep

    while True:

        if not esp_enabled_flag or lpAddr == 0 or plrsAddr == 0 or matrixAddr == 0:

            sleep(1)

            continue



        tempColors = []

        tempHeads = []



        lpTeam = pm.read_longlong(lpAddr + int(offsets["Team"], 16))

        for v in GetChildren(plrsAddr):

            if v == lpAddr:

                continue

            team = pm.read_longlong(v + int(offsets["Team"], 16))

            if not esp_ignoreteam or (team != lpTeam and team > 0):

                char = pm.read_longlong(v + int(offsets["ModelInstance"], 16))

                if not char:

                    continue

                head = FindFirstChild(char, 'Head')

                hum = FindFirstChildOfClass(char, 'Humanoid')

                if head and hum:

                    if esp_ignoredead and pm.read_float(hum + int(offsets["Health"], 16)) <= 0:

                        continue

                    col = 'white'

                    if team > 0:

                        col = "#FFFFFF"

                    tempColors.append(col)

                    tempHeads.append(head)

        heads = tempHeads

        colors = tempColors

        sleep(0.1)



def start_esp_overlay():

    global esp_instance, esp_app, esp_enabled_flag

    from threading import Thread

    from time import sleep



    def qt_loop():

        global esp_instance, esp_app

        esp_app = QApplication([])

        esp_instance = ESPOverlay()

        esp_instance.show()

        timer = QTimer()

        timer.timeout.connect(esp_instance.update_players)

        timer.start(16)

        esp_app.exec_()



    esp_enabled_flag = True

    Thread(target=qt_loop, daemon=True).start()

    Thread(target=headAndHumFinder, daemon=True).start()



def esp_callback(sender, app_data):

    global esp_enabled_flag

    if not injected:

        return

    esp_enabled_flag = app_data

    if esp_enabled_flag:

        start_esp_overlay()



def set_aimbot_mode(mode):
    global aimbot_mode
    aimbot_mode = mode
    dpg.configure_item("keybind_button", label=f"Keybind: {get_key_name(aimbot_keybind)} ({aimbot_mode})")
    dpg.hide_item("keybind_mode_popup")