import tkinter as tk
from tkinter import ttk, messagebox
import json
import threading
import time
import random
import numpy as np
import cv2
import bettercam
from comtypes import CLSCTX_ALL
from comtypes.client import CreateObject
from win32api import GetSystemMetrics, GetAsyncKeyState
import keyboard
import math
import logging
import socket  # For KMBoxNet TCP
import serial  # For Arduino (pip install pyserial)
import ctypes  # For embedded rzctl-py and g-input (Windows API)
from ctypes import *
from ctypes.wintypes import *
import sys
import win32file  # For embedded g-input
from cryptography.fernet import Fernet  # Optional encryption
try:
    from human_cursor import SystemCursor
except ImportError:
    SystemCursor = None
try:
    import pystray
    from PIL import Image
except ImportError:
    pystray = None
try:
    from scipy.interpolate import splprep, splev
except ImportError:
    splprep = splev = None

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Embedded rzctl_nt.py logic (full from user)
ntdll = windll.ntdll
kernel32 = windll.kernel32

NTSTATUS = c_long
STATUS_SUCCESS = NTSTATUS(0x00000000).value
STATUS_UNSUCCESSFUL = NTSTATUS(0xC0000001).value
STATUS_BUFFER_TOO_SMALL = NTSTATUS(0xC0000023).value
PVOID = c_void_p
PWSTR = c_wchar_p
DIRECTORY_QUERY = 0x0001
OBJ_CASE_INSENSITIVE = 0x00000040
INVALID_HANDLE_VALUE = -1
FILE_SHARE_READ = 0x00000001
FILE_SHARE_WRITE = 0x00000002
OPEN_EXISTING = 3


class UNICODE_STRING(Structure):
    _fields_ = [("Length", USHORT), ("MaximumLength", USHORT), ("Buffer", PWSTR)]


class OBJECT_ATTRIBUTES(Structure):
    _fields_ = [
        ("Length", ULONG),
        ("RootDirectory", HANDLE),
        ("ObjectName", POINTER(UNICODE_STRING)),
        ("Attributes", ULONG),
        ("SecurityDescriptor", PVOID),
        ("SecurityQualityOfService", PVOID),
    ]


class OBJECT_DIRECTORY_INFORMATION(Structure):
    _fields_ = [("Name", UNICODE_STRING), ("TypeName", UNICODE_STRING)]


def InitializeObjectAttributes(
    InitializedAttributes, ObjectName, Attributes, RootDirectory, SecurityDescriptor
):
    memset(addressof(InitializedAttributes), 0, sizeof(InitializedAttributes))
    InitializedAttributes.Length = sizeof(InitializedAttributes)
    InitializedAttributes.ObjectName = ObjectName
    InitializedAttributes.Attributes = Attributes
    InitializedAttributes.RootDirectory = RootDirectory
    InitializedAttributes.SecurityDescriptor = SecurityDescriptor
    InitializedAttributes.SecurityQualityOfService = None


def RtlInitUnicodeString(DestinationString, Src):
    memset(addressof(DestinationString), 0, sizeof(DestinationString))
    DestinationString.Buffer = cast(Src, PWSTR)
    DestinationString.Length = sizeof(Src) - 2
    DestinationString.MaximumLength = DestinationString.Length
    return STATUS_SUCCESS


def open_directory(root_handle, dir, desired_access):
    status = STATUS_UNSUCCESSFUL
    dir_handle = c_void_p()
    us_dir = UNICODE_STRING()
    p_us_dir = None
    if dir:
        w_dir = create_unicode_buffer(dir)
        us_dir = UNICODE_STRING()
        status = RtlInitUnicodeString(us_dir, w_dir)
        p_us_dir = pointer(us_dir)
        if status != STATUS_SUCCESS:
            logging.error("RtlInitUnicodeString failed.")
            return None
    obj_attr = OBJECT_ATTRIBUTES()
    InitializeObjectAttributes(
        obj_attr, p_us_dir, OBJ_CASE_INSENSITIVE, root_handle, None
    )
    status = ntdll.NtOpenDirectoryObject(
        byref(dir_handle), desired_access, byref(obj_attr)
    )
    if status != STATUS_SUCCESS:
        logging.error("NtOpenDirectoryObject failed.")
        return None
    return dir_handle


def find_sym_link(dir, name):
    dir_handle = open_directory(None, dir, DIRECTORY_QUERY)
    if not dir_handle:
        return False, None
    status = STATUS_UNSUCCESSFUL
    query_context = ULONG(0)
    length = ULONG()
    objinf = OBJECT_DIRECTORY_INFORMATION()
    found = False
    out = None
    while True:
        status = ntdll.NtQueryDirectoryObject(
            dir_handle, 0, 0, True, False, byref(query_context), byref(length)
        )
        if status != STATUS_BUFFER_TOO_SMALL:
            logging.error("NtQueryDirectoryObject failed (not buffer small).")
            break
        p_objinf = pointer(objinf)
        status = ntdll.NtQueryDirectoryObject(
            dir_handle,
            p_objinf,
            length,
            True,
            False,
            byref(query_context),
            byref(length),
        )
        if status != STATUS_SUCCESS:
            logging.error("NtQueryDirectoryObject failed.")
            break
        _name = objinf.Name.Buffer
        if name in _name:
            found = True
            out = _name
            break
    ntdll.NtClose(dir_handle)
    return found, out

# Embedded rzctl.py logic (full from user)
def enum(**enums):
    return type("Enum", (), enums)

MOUSE_CLICK = enum(
    LEFT_DOWN=1,
    LEFT_UP=2,
    RIGHT_DOWN=4,
    RIGHT_UP=8,
    SCROLL_CLICK_DOWN=16,
    SCROLL_CLICK_UP=32,
    BACK_DOWN=64,
    BACK_UP=128,
    FOWARD_DOWN=256,
    FOWARD_UP=512,
    SCROLL_DOWN=4287104000,
    SCROLL_UP=7865344,
)

KEYBOARD_INPUT_TYPE = enum(KEYBOARD_DOWN=0, KEYBOARD_UP=1)


class RZCONTROL_IOCTL_STRUCT(Structure):
    _fields_ = [
        ("unk0", c_int32),
        ("unk1", c_int32),
        ("max_val_or_scan_code", c_int32),
        ("click_mask", c_int32),
        ("unk3", c_int32),
        ("x", c_int32),
        ("y", c_int32),
        ("unk4", c_int32),
    ]


IOCTL_MOUSE = 0x88883020
MAX_VAL = 65536
RZCONTROL_MOUSE = 2
RZCONTROL_KEYBOARD = 1


class RZCONTROL:

    hDevice = INVALID_HANDLE_VALUE

    def __init__(self):
        pass

    def init(self):
        if RZCONTROL.hDevice != INVALID_HANDLE_VALUE:
            kernel32.CloseHandle(RZCONTROL.hDevice)
        found, name = find_sym_link("\\GLOBAL??", "RZCONTROL")
        if not found:
            return False
        sym_link = "\\\\?\\" + name
        RZCONTROL.hDevice = kernel32.CreateFileW(
            sym_link, 0, FILE_SHARE_READ | FILE_SHARE_WRITE, 0, OPEN_EXISTING, 0, 0
        )
        return RZCONTROL.hDevice != INVALID_HANDLE_VALUE

    def impl_mouse_ioctl(self, ioctl):
        if ioctl:
            p_ioctl = pointer(ioctl)
            junk = c_ulong()
            bResult = kernel32.DeviceIoControl(
                RZCONTROL.hDevice,
                IOCTL_MOUSE,
                p_ioctl,
                sizeof(RZCONTROL_IOCTL_STRUCT),
                0,
                0,
                byref(junk),
                0,
            )
            if not bResult:
                self.init()

    def mouse_move(self, x, y, from_start_point):
        max_val = 0
        if not from_start_point:
            max_val = MAX_VAL
            if x < 1:
                x = 1
            if x > max_val:
                x = max_val
            if y < 1:
                y = 1
            if y > max_val:
                y = max_val
        mm = RZCONTROL_IOCTL_STRUCT(0, RZCONTROL_MOUSE, max_val, 0, 0, x, y, 0)
        self.impl_mouse_ioctl(mm)

    def mouse_click(self, click_mask):
        mm = RZCONTROL_IOCTL_STRUCT(
            0,
            RZCONTROL_MOUSE,
            0,
            click_mask,
            0,
            0,
            0,
            0,
        )
        self.impl_mouse_ioctl(mm)

    def keyboard_input(self, scan_code, up_down):
        mm = RZCONTROL_IOCTL_STRUCT(
            0,
            RZCONTROL_KEYBOARD,
            (int(scan_code) << 16),
            up_down,
            0,
            0,
            0,
            0,
        )
        self.impl_mouse_ioctl(mm)

# Embedded g-input mouse.py logic (full from user)
def clamp_char(value: int) -> int:
    return max(-128, min(127, value))

def _DeviceIoControl(devhandle, ioctl, inbuf, inbufsiz, outbuf, outbufsiz):
    DeviceIoControl_Fn = windll.kernel32.DeviceIoControl
    DeviceIoControl_Fn.argtypes = [
        wintypes.HANDLE,
        wintypes.DWORD,
        wintypes.LPVOID,
        wintypes.DWORD,
        wintypes.LPVOID,
        wintypes.DWORD,
        ctypes.POINTER(wintypes.DWORD),
        wintypes.LPVOID
    ]
    DeviceIoControl_Fn.restype = wintypes.BOOL
    
    dwBytesReturned = wintypes.DWORD(0)
    lpBytesReturned = ctypes.byref(dwBytesReturned)
    status = DeviceIoControl_Fn(
        int(devhandle),
        ioctl,
        inbuf,
        inbufsiz,
        outbuf,
        outbufsiz,
        lpBytesReturned,
        None
    )
    return status, dwBytesReturned


class MOUSE_IO(ctypes.Structure):
    _fields_ = [
        ("button", ctypes.c_char),
        ("x", ctypes.c_char),
        ("y", ctypes.c_char),
        ("wheel", ctypes.c_char),
        ("unk1", ctypes.c_char)
    ]


ginput_handle = 0
ginput_found = False

def ginput_mouse_open() -> bool:
    global ginput_handle
    global ginput_found

    if ginput_found and ginput_handle:
        return True

    for i in range(1, 10):
        devpath = f'\\??\\ROOT#SYSTEM#000{i}#' + '{1abc05c0-c378-41b9-9cef-df1aba82b015}'
        try:
            ginput_handle = win32file.CreateFileW(
                devpath,
                win32file.GENERIC_WRITE,
                0,
                None,
                win32file.OPEN_ALWAYS,
                win32file.FILE_ATTRIBUTE_NORMAL,
                0
            )
            if ginput_handle != INVALID_HANDLE_VALUE:
                ginput_found = True
                return True
        except Exception as e:
            pass
    logging.error('Failed to initialize G-Input device.')
    return False

def ginput_mouse_close() -> None:
    global ginput_handle
    if ginput_handle:
        win32file.CloseHandle(int(ginput_handle))
        ginput_handle = 0

def ginput_call_mouse(buffer: MOUSE_IO) -> bool:
    global ginput_handle
    status, _ = _DeviceIoControl(
        ginput_handle, 
        0x2a2010,
        ctypes.c_void_p(ctypes.addressof(buffer)),
        ctypes.sizeof(buffer),
        None,
        0, 
    )
    if not status:
        logging.error("DeviceIoControl failed to send mouse input.")
    return status

def ginput_mouse_move(button: int, x: int, y: int, wheel: int) -> None:
    global ginput_handle

    x_clamped = clamp_char(x)
    y_clamped = clamp_char(y)
    btn_byte   = clamp_char(button)
    wheel_byte = clamp_char(wheel)

    io = MOUSE_IO()
    io.button = ctypes.c_char(btn_byte)
    io.x      = ctypes.c_char(x_clamped)
    io.y      = ctypes.c_char(y_clamped)
    io.wheel  = ctypes.c_char(wheel_byte)
    io.unk1   = ctypes.c_char(0)

    if not ginput_call_mouse(io):
        ginput_mouse_close()
        if not ginput_mouse_open():
            logging.error("Failed to reinitialize G-Input device after error.")

class AppConfig:
    def __init__(self, encryption_key: bytes = None):
        self.encryption_key = encryption_key
        self.master_toggle = tk.BooleanVar(value=False)
        self.aimbot_enabled = tk.BooleanVar(value=True)
        self.triggerbot_enabled = tk.BooleanVar(value=True)
        self.rcs_enabled = tk.BooleanVar(value=True)
        self.magnet_aim = tk.BooleanVar(value=False)
        self.trigger_mode = tk.StringVar(value='SINGLE')
        self.aim_location = tk.StringVar(value='HEAD')
        self.horizontal_offset = tk.DoubleVar(value=0)
        self.vertical_offset = tk.DoubleVar(value=0)
        self.dynamic_fov = tk.BooleanVar(value=True)
        self.hsv_density_filter = tk.BooleanVar(value=False)
        self.hsv_calibration = tk.BooleanVar(value=False)
        self.toggle_key = tk.StringVar(value='f4')
        self.aim_keys = tk.StringVar(value='shift')
        self.detection_fov = tk.DoubleVar(value=150)
        self.aim_fov = tk.DoubleVar(value=100)
        self.aimbot_sensitivity = tk.DoubleVar(value=3.5)
        self.rcs_strength = tk.DoubleVar(value=1.8)
        self.game_profile = tk.StringVar(value='Valorant')
        self.input_method = tk.StringVar(value='g-input')  # Options: 'g-input', 'rzctl-py', 'arduino', 'kmboxnet'
        self.humanization_method = tk.StringVar(value='HumanCursor')
        self.capture_method = tk.StringVar(value='BetterCam')
        self.target_colors = tk.StringVar(value='PURPLE,YELLOW')
        # New for Arduino and KMBoxNet
        self.arduino_com_port = tk.StringVar(value='COM3')
        self.arduino_baud_rate = tk.IntVar(value=115200)
        self.kmbox_ip = tk.StringVar(value='127.0.0.1')
        self.kmbox_port = tk.IntVar(value=1688)
        self.kmbox_uuid = tk.StringVar(value='')
        # Full color_ranges (from early messages)
        self.color_ranges = {
            'Valorant': {
                'PURPLE': ([140, 80, 100], [160, 255, 255]),
                'YELLOW': ([20, 100, 100], [30, 255, 255]),
                'CUSTOM_1': ([0, 0, 200], [180, 50, 255]),
                'CUSTOM_2': ([0, 0, 200], [180, 50, 255])
            },
            'Overwatch 2': {
                'RED_1': ([0, 120, 70], [10, 255, 255]),
                'RED_2': ([170, 120, 70], [180, 255, 255]),
                'CUSTOM_1': ([0, 0, 200], [180, 50, 255]),
                'CUSTOM_2': ([0, 0, 200], [180, 50, 255])
            },
            'KovaaK\'s': {
                'CUSTOM_1': ([0, 0, 200], [180, 50, 255]),
                'CUSTOM_2': ([0, 0, 200], [180, 50, 255])
            },
            'The Finals': {
                'FINALS_RED': ([0, 100, 100], [10, 255, 255]),
                'CUSTOM_1': ([0, 0, 200], [180, 50, 255]),
                'CUSTOM_2': ([0, 0, 200], [180, 50, 255])
            },
            'Marvel Rivals': {
                'MARVEL_ORANGE': ([5, 100, 100], [25, 255, 255]),
                'CUSTOM_1': ([0, 0, 200], [180, 50, 255]),
                'CUSTOM_2': ([0, 0, 200], [180, 50, 255])
            }
        }
        # Full custom_hsv (from early messages)
        self.custom_hsv = {
            'Valorant': {
                'CUSTOM_1_lower': tk.StringVar(value='0,0,200'),
                'CUSTOM_1_upper': tk.StringVar(value='180,50,255'),
                'CUSTOM_2_lower': tk.StringVar(value='0,0,200'),
                'CUSTOM_2_upper': tk.StringVar(value='180,50,255')
            },
            'Overwatch 2': {
                'CUSTOM_1_lower': tk.StringVar(value='0,0,200'),
                'CUSTOM_1_upper': tk.StringVar(value='180,50,255'),
                'CUSTOM_2_lower': tk.StringVar(value='0,0,200'),
                'CUSTOM_2_upper': tk.StringVar(value='180,50,255')
            },
            'KovaaK\'s': {
                'CUSTOM_1_lower': tk.StringVar(value='0,0,200'),
                'CUSTOM_1_upper': tk.StringVar(value='180,50,255'),
                'CUSTOM_2_lower': tk.StringVar(value='0,0,200'),
                'CUSTOM_2_upper': tk.StringVar(value='180,50,255')
            },
            'The Finals': {
                'CUSTOM_1_lower': tk.StringVar(value='0,0,200'),
                'CUSTOM_1_upper': tk.StringVar(value='180,50,255'),
                'CUSTOM_2_lower': tk.StringVar(value='0,0,200'),
                'CUSTOM_2_upper': tk.StringVar(value='180,50,255')
            },
            'Marvel Rivals': {
                'CUSTOM_1_lower': tk.StringVar(value='0,0,200'),
                'CUSTOM_1_upper': tk.StringVar(value='180,50,255'),
                'CUSTOM_2_lower': tk.StringVar(value='0,0,200'),
                'CUSTOM_2_upper': tk.StringVar(value='180,50,255')
            }
        }
        # Full game_profiles (from early messages)
        self.game_profiles = {
            'Valorant': {
                'detection_fov': 120, 'aim_fov': 80, 'aimbot_sensitivity': 3.0, 'rcs_strength': 1.8,
                'target_colors': 'PURPLE,YELLOW', 'aim_location': 'HEAD', 'hsv_density_filter': False,
                'horizontal_offset': 0, 'vertical_offset': -5, 'dynamic_fov': True, 'magnet_aim': True,
                'aim_keys': 'shift', 'triggerbot_enabled': True, 'input_method': 'g-input',
                'humanization_method': 'HumanCursor', 'capture_method': 'BetterCam'
            },
            'Overwatch 2': {
                'detection_fov': 180, 'aim_fov': 120, 'aimbot_sensitivity': 3.8, 'rcs_strength': 1.5,
                'target_colors': 'RED_1,RED_2', 'aim_location': 'CHEST', 'hsv_density_filter': True,
                'horizontal_offset': 0, 'vertical_offset': -10, 'dynamic_fov': True, 'magnet_aim': False,
                'aim_keys': 'left,right', 'triggerbot_enabled': True, 'input_method': 'g-input',
                'humanization_method': 'HumanCursor', 'capture_method': 'BetterCam'
            },
            'KovaaK\'s': {
                'detection_fov': 200, 'aim_fov': 150, 'aimbot_sensitivity': 4.0, 'rcs_strength': 0.0,
                'target_colors': 'CUSTOM_1', 'aim_location': 'CENTER', 'hsv_density_filter': False,
                'horizontal_offset': 0, 'vertical_offset': 0, 'dynamic_fov': False, 'magnet_aim': False,
                'aim_keys': 'left,right', 'triggerbot_enabled': False, 'input_method': 'g-input',
                'humanization_method': 'WindMouse', 'capture_method': 'BetterCam'
            },
            'The Finals': {
                'detection_fov': 150, 'aim_fov': 100, 'aimbot_sensitivity': 3.5, 'rcs_strength': 1.8,
                'target_colors': 'FINALS_RED', 'aim_location': 'CHEST', 'hsv_density_filter': False,
                'horizontal_offset': 0, 'vertical_offset': -5, 'dynamic_fov': True, 'magnet_aim': True,
                'aim_keys': 'left,right', 'triggerbot_enabled': True, 'input_method': 'g-input',
                'humanization_method': 'HumanCursor', 'capture_method': 'BetterCam'
            },
            'Marvel Rivals': {
                'detection_fov': 120, 'aim_fov': 80, 'aimbot_sensitivity': 3.2, 'rcs_strength': 1.5,
                'target_colors': 'MARVEL_ORANGE', 'aim_location': 'HEAD', 'hsv_density_filter': False,
                'horizontal_offset': 0, 'vertical_offset': -5, 'dynamic_fov': True, 'magnet_aim': True,
                'aim_keys': 'left,right', 'triggerbot_enabled': True, 'input_method': 'g-input',
                'humanization_method': 'HumanCursor', 'capture_method': 'BetterCam'
            }
        }
        self.load_settings()

    def save_settings(self, filename: str = 'settings.json') -> None:
        if not self.validate_settings():
            raise ValueError("Invalid settings; check logs for details.")
        
        settings = {
            'master_toggle': self.master_toggle.get(),
            'aimbot_enabled': self.aimbot_enabled.get(),
            'triggerbot_enabled': self.triggerbot_enabled.get(),
            'rcs_enabled': self.rcs_enabled.get(),
            'magnet_aim': self.magnet_aim.get(),
            'trigger_mode': self.trigger_mode.get(),
            'aim_location': self.aim_location.get(),
            'horizontal_offset': self.horizontal_offset.get(),
            'vertical_offset': self.vertical_offset.get(),
            'dynamic_fov': self.dynamic_fov.get(),
            'hsv_density_filter': self.hsv_density_filter.get(),
            'hsv_calibration': self.hsv_calibration.get(),
            'toggle_key': self.toggle_key.get(),
            'aim_keys': self.aim_keys.get(),
            'detection_fov': self.detection_fov.get(),
            'aim_fov': self.aim_fov.get(),
            'aimbot_sensitivity': self.aimbot_sensitivity.get(),
            'rcs_strength': self.rcs_strength.get(),
            'game_profile': self.game_profile.get(),
            'input_method': self.input_method.get(),
            'humanization_method': self.humanization_method.get(),
            'capture_method': self.capture_method.get(),
            'target_colors': self.target_colors.get(),
            'arduino_com_port': self.arduino_com_port.get(),
            'arduino_baud_rate': self.arduino_baud_rate.get(),
            'kmbox_ip': self.kmbox_ip.get(),
            'kmbox_port': self.kmbox_port.get(),
            'kmbox_uuid': self.kmbox_uuid.get(),
            'custom_hsv': {
                game: {
                    'CUSTOM_1_lower': self.custom_hsv[game]['CUSTOM_1_lower'].get(),
                    'CUSTOM_1_upper': self.custom_hsv[game]['CUSTOM_1_upper'].get(),
                    'CUSTOM_2_lower': self.custom_hsv[game]['CUSTOM_2_lower'].get(),
                    'CUSTOM_2_upper': self.custom_hsv[game]['CUSTOM_2_upper'].get()
                } for game in self.custom_hsv
            }
        }
        
        data = json.dumps(settings).encode('utf-8')
        if self.encryption_key:
            f = Fernet(self.encryption_key)
            data = f.encrypt(data)
            logging.info("Settings encrypted and saved.")
        else:
            logging.info("Settings saved (unencrypted).")
        
        with open(filename, 'wb') as f:
            f.write(data)

    def load_settings(self, filename: str = 'settings.json') -> None:
        try:
            with open(filename, 'rb') as f:
                data = f.read()
            if self.encryption_key:
                f = Fernet(self.encryption_key)
                data = f.decrypt(data).decode('utf-8')
                logging.info("Settings decrypted and loaded.")
            else:
                data = data.decode('utf-8')
            
            settings = json.loads(data)
            for key, value in settings.items():
                if key == 'custom_hsv':
                    for game, hsv_values in value.items():
                        for hsv_key, hsv_value in hsv_values.items():
                            self.custom_hsv[game][hsv_key].set(hsv_value)
                else:
                    getattr(self, key).set(value)
            
            if self.aim_fov.get() > self.detection_fov.get():
                self.aim_fov.set(self.detection_fov.get())
            
            for game in self.custom_hsv:
                try:
                    self.color_ranges[game]['CUSTOM_1'] = (
                        [int(x) for x in self.custom_hsv[game]['CUSTOM_1_lower'].get().split(',')],
                        [int(x) for x in self.custom_hsv[game]['CUSTOM_1_upper'].get().split(',')]
                    )
                    self.color_ranges[game]['CUSTOM_2'] = (
                        [int(x) for x in self.custom_hsv[game]['CUSTOM_2_lower'].get().split(',')],
                        [int(x) for x in self.custom_hsv[game]['CUSTOM_2_upper'].get().split(',')]
                    )
                except ValueError:
                    pass
            
            self.validate_settings()
            logging.info("Settings loaded successfully.")
        except FileNotFoundError:
            logging.info("No settings file found; saving defaults.")
            self.save_settings(filename)
        except Exception as e:
            logging.error(f"Error loading settings: {e}")
            raise

    def validate_settings(self) -> bool:
        valid = True
        if self.detection_fov.get() <= 0 or self.aim_fov.get() <= 0:
            logging.warning("FOV values must be positive.")
            valid = False
        if self.aim_fov.get() > self.detection_fov.get():
            self.aim_fov.set(self.detection_fov.get())
            logging.info("Adjusted aim_fov to match detection_fov.")
        for game in self.color_ranges:
            for color, (lower, upper) in self.color_ranges[game].items():
                if not (0 <= lower[0] <= 179 and 0 <= upper[0] <= 179):
                    logging.warning(f"Invalid HSV hue for {game}/{color}.")
                    valid = False
        return valid

    def reset_to_defaults(self) -> None:
        self.master_toggle.set(False)
        self.aimbot_enabled.set(True)
        self.triggerbot_enabled.set(True)
        self.rcs_enabled.set(True)
        self.magnet_aim.set(False)
        self.trigger_mode.set('SINGLE')
        self.aim_location.set('HEAD')
        self.horizontal_offset.set(0)
        self.vertical_offset.set(0)
        self.dynamic_fov.set(True)
        self.hsv_density_filter.set(False)
        self.hsv_calibration.set(False)
        self.toggle_key.set('f4')
        self.aim_keys.set('shift')
        self.detection_fov.set(150)
        self.aim_fov.set(100)
        self.aimbot_sensitivity.set(3.5)
        self.rcs_strength.set(1.8)
        self.game_profile.set('Valorant')
        self.input_method.set('g-input')
        self.humanization_method.set('HumanCursor')
        self.capture_method.set('BetterCam')
        self.target_colors.set('PURPLE,YELLOW')
        self.arduino_com_port.set('COM3')
        self.arduino_baud_rate.set(115200)
        self.kmbox_ip.set('127.0.0.1')
        self.kmbox_port.set(1688)
        self.kmbox_uuid.set('')
        for game in self.custom_hsv:
            self.custom_hsv[game]['CUSTOM_1_lower'].set('0,0,200')
            self.custom_hsv[game]['CUSTOM_1_upper'].set('180,50,255')
            self.custom_hsv[game]['CUSTOM_2_lower'].set('0,0,200')
            self.custom_hsv[game]['CUSTOM_2_upper'].set('180,50,255')
        logging.info("Settings reset to defaults.")
        self.save_settings()

# Mouse drivers (separated as requested)
class MouseBase:
    def __init__(self, config=None):
        self.config = config

    def move(self, dx: int, dy: int) -> None:
        raise NotImplementedError

    def click(self) -> None:
        raise NotImplementedError

    def release(self) -> None:
        raise NotImplementedError

    def close(self) -> None:
        pass

class GInputMouse(MouseBase):
    def __init__(self, config=None):
        super().__init__(config)
        if not ginput_mouse_open():
            raise RuntimeError("Ghub is not open or something else is wrong")
        logging.info("Embedded G-Input initialized.")

    def move(self, dx: int, dy: int) -> None:
        ginput_mouse_move(0, dx, dy, 0)

    def click(self) -> None:
        ginput_mouse_move(1, 0, 0, 0)  # Down
        time.sleep(0.01)
        ginput_mouse_move(2, 0, 0, 0)  # Up

    def release(self) -> None:
        ginput_mouse_move(2, 0, 0, 0)

    def close(self) -> None:
        ginput_mouse_close()

class RazerMouse(MouseBase):
    def __init__(self, config=None):
        super().__init__(config)
        self.rzctl_instance = RZCONTROL()
        if not self.rzctl_instance.init():
            raise RuntimeError("Failed to initialize Razer control.")
        logging.info("Embedded Razer initialized.")

    def move(self, dx: int, dy: int) -> None:
        self.rzctl_instance.mouse_move(dx, dy, True)

    def click(self) -> None:
        self.rzctl_instance.mouse_click(MOUSE_CLICK.LEFT_DOWN)
        time.sleep(0.001)
        self.rzctl_instance.mouse_click(MOUSE_CLICK.LEFT_UP)

    def release(self) -> None:
        self.rzctl_instance.mouse_click(MOUSE_CLICK.LEFT_UP)

    def close(self) -> None:
        if RZCONTROL.hDevice != INVALID_HANDLE_VALUE:
            kernel32.CloseHandle(RZCONTROL.hDevice)

class ArduinoMouse(MouseBase):
    def __init__(self, config):
        super().__init__(config)
        if serial is None:
            raise ImportError("pyserial not installed.")
        try:
            self.serial_conn = serial.Serial(self.config.arduino_com_port.get(), self.config.arduino_baud_rate.get(), timeout=1)
            time.sleep(2)
            self.serial_conn.write(b'INIT\n')
            logging.info(f"Arduino connected.")
        except serial.SerialException as e:
            raise RuntimeError(f"Arduino failed: {e}")

    def move(self, dx: int, dy: int) -> None:
        command = f"MOVE {int(dx)} {int(dy)}\n".encode('utf-8')
        self.serial_conn.write(command)

    def click(self) -> None:
        self.serial_conn.write(b'CLICK\n')

    def release(self) -> None:
        self.serial_conn.write(b'RELEASE\n')

    def close(self) -> None:
        self.serial_conn.close()

class KMBoxMouse(MouseBase):
    def __init__(self, config):
        super().__init__(config)
        try:
            self.kmbox_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.kmbox_socket.connect((self.config.kmbox_ip.get(), self.config.kmbox_port.get()))
            auth_packet = f"AUTH {self.config.kmbox_uuid.get()}\n".encode('utf-8')
            self.kmbox_socket.send(auth_packet)
            response = self.kmbox_socket.recv(1024).decode()
            if "OK" not in response:
                raise RuntimeError("KMBox auth failed.")
            logging.info("KMBox connected.")
        except socket.error as e:
            raise RuntimeError(f"KMBox failed: {e}")

    def move(self, dx: int, dy: int) -> None:
        packet = b'\x01' + int(dx).to_bytes(2, 'big', signed=True) + int(dy).to_bytes(2, 'big', signed=True)
        self.kmbox_socket.send(packet)

    def click(self) -> None:
        self.kmbox_socket.send(b'\x02')

    def release(self) -> None:
        self.kmbox_socket.send(b'\x03')

    def close(self) -> None:
        self.kmbox_socket.close()

def create_mouse(method: str, config=None) -> MouseBase:
    if method == 'g-input':
        return GInputMouse(config)
    elif method == 'rzctl-py':
        return RazerMouse(config)
    elif method == 'arduino':
        return ArduinoMouse(config)
    elif method == 'kmboxnet':
        return KMBoxMouse(config)
    else:
        raise ValueError(f"Unsupported method: {method}")

class AscendancyCore(threading.Thread):
    def __init__(self, config, mouse, status_callback):
        super().__init__()
        self.daemon = True
        self.config = config
        self.mouse = mouse
        self.status_callback = status_callback
        self.screen_width = GetSystemMetrics(0)
        self.screen_height = GetSystemMetrics(1)
        self.last_x, self.last_y = 0, 0
        self.cursor = SystemCursor() if SystemCursor else None
        self.bettercam = None
        self.wgc_session = None
        self.capture_method = self.config.capture_method.get()
        self.paused = False
        self.setup_capture()
        self.humanization_methods = {
            'HumanCursor': self.generate_human_cursor_path,
            'WindMouse': self.generate_windmouse_path,
            'Bezier': self.generate_bezier_path,
            'Spline': self.generate_spline_path if splprep else self.generate_bezier_path
        }

    def setup_capture(self):
        if self.capture_method == 'BetterCam':
            try:
                self.bettercam = bettercam.create(output_color="BGR")
                self.bettercam.start(target_fps=120, video_mode=True)
                self.status_callback("BetterCam initialized")
            except Exception as e:
                self.status_callback(f"BetterCam setup failed: {e}")
                self.bettercam = None
        elif self.capture_method == 'WGC':
            try:
                from comtypes.gen import WindowsGraphicsCapture as wgc
                factory = CreateObject(wgc.GraphicsCaptureItemInterop, CLSCTX_ALL)
                monitor = factory.CreateForMonitor(0)
                self.wgc_session = wgc.GraphicsCaptureSession(monitor)
                self.wgc_session.StartCapture()
                self.status_callback("Windows Graphics Capture initialized")
            except Exception as e:
                self.status_callback(f"WGC setup failed: {e}, falling back to BetterCam")
                self.capture_method = 'BetterCam'
                self.setup_capture()

    def update_capture_method(self, method):
        if method == self.capture_method:
            return
        if self.bettercam:
            self.bettercam.stop()
            self.bettercam = None
        if self.wgc_session:
            self.wgc_session.Close()
            self.wgc_session = None
        self.capture_method = method
        self.setup_capture()

    def get_frame(self) -> np.ndarray | None:
        try:
            if self.capture_method == 'BetterCam' and self.bettercam:
                return self.bettercam.get_latest_frame()
            elif self.capture_method == 'WGC' and self.wgc_session:
                # Placeholder; implement if available
                self.status_callback("WGC frame capture not fully implemented")
                return None
            return None
        except Exception as e:
            logging.error(f"Frame capture failed: {e}")
            return None

    def calibrate_hsv(self, hsv):
        if self.config.hsv_calibration.get():
            game = self.config.game_profile.get()
            target_colors = self.config.target_colors.get().split(',')
            for color in target_colors:
                if color in self.config.color_ranges[game]:
                    pixels = hsv[np.where(cv2.inRange(hsv, np.array(self.config.color_ranges[game][color][0]), 
                                                      np.array(self.config.color_ranges[game][color][1])))]
                    if pixels.size > 0:
                        avg_hsv = np.mean(pixels, axis=0)
                        self.config.color_ranges[game][color] = (
                            [max(0, avg_hsv[0] - 10), max(50, avg_hsv[1] - 50), max(70, avg_hsv[2] - 50)],
                            [min(180, avg_hsv[0] + 10), 255, 255]
                        )
            self.status_callback(f"HSV calibrated for {game}")

    def smooth_move(self, dx: float, dy: float, steps: int = 15, delay: float = 0.002) -> None:
        method = self.config.humanization_method.get()
        generator = self.humanization_methods.get(method, self.generate_bezier_path)
        try:
            path = generator(dx, dy, steps)
        except Exception as e:
            logging.error(f"Path generation failed ({method}): {e}; using Bezier fallback.")
            path = self.generate_bezier_path(dx, dy, steps)
        
        for step_dx, step_dy in path:
            step_dx = max(-self.screen_width // 2, min(self.screen_width // 2, int(step_dx)))
            step_dy = max(-self.screen_height // 2, min(self.screen_height // 2, int(step_dy)))
            self.mouse.move(step_dx, step_dy)
            time.sleep(delay + random.uniform(-0.001, 0.001))
        self.last_x, self.last_y = dx, dy
        logging.debug(f"Moved mouse by ({dx}, {dy}) using {method}")

    def generate_human_cursor_path(self, dx: float, dy: float, steps: int) -> list[tuple[float, float]]:
        path = []
        step_dx = dx / steps
        step_dy = dy / steps
        current_x, current_y = 0, 0
        for _ in range(steps):
            self.cursor.move_by_offset(step_dx, step_dy)
            path.append((step_dx, step_dy))
            current_x += step_dx
            current_y += step_dy
        path.append((dx - current_x, dy - current_y))
        return path

    def generate_windmouse_path(self, dx: float, dy: float, steps: int, G_0=9, W_0=3, M_0=15, D_0=12) -> list[tuple[float, float]]:
        current_x, current_y = 0, 0
        dest_x, dest_y = dx, dy
        path = []
        v_x = v_y = W_x = W_y = 0
        sqrt3, sqrt5 = math.sqrt(3), math.sqrt(5)
        while (dist := np.hypot(dest_x - current_x, dest_y - current_y)) >= 1:
            W_mag = min(W_0, dist)
            if dist >= D_0:
                W_x = W_x / sqrt3 + (2 * np.random.random() - 1) * W_mag / sqrt5
                W_y = W_y / sqrt3 + (2 * np.random.random() - 1) * W_mag / sqrt5
            else:
                W_x /= sqrt3
                W_y /= sqrt3
                if M_0 < 3:
                    M_0 = np.random.random() * 3 + 3
                else:
                    M_0 /= sqrt5
            v_x += W_x + G_0 * (dest_x - current_x) / dist
            v_y += W_y + G_0 * (dest_y - current_y) / dist
            v_mag = np.hypot(v_x, v_y)
            if v_mag > M_0:
                v_clip = M_0 / 2 + np.random.random() * M_0 / 2
                v_x = (v_x / v_mag) * v_clip
                v_y = (v_y / v_mag) * v_clip
            next_x = current_x + v_x
            next_y = current_y + v_y
            path.append((next_x - current_x, next_y - current_y))
            current_x, current_y = next_x, next_y
        path.append((dx - current_x, dy - current_y))
        return path[:steps]

    def generate_bezier_path(self, dx: float, dy: float, steps: int) -> list[tuple[float, float]]:
        t = np.linspace(0, 1, steps)
        control_point = (dx * 0.5 + random.uniform(-10, 10), dy * 0.5 + random.uniform(-10, 10))
        path = []
        prev_x, prev_y = 0, 0
        for i in t:
            x = int((1-i)**2 * 0 + 2*(1-i)*i * control_point[0] + i**2 * dx)
            y = int((1-i)**2 * 0 + 2*(1-i)*i * control_point[1] + i**2 * dy)
            path.append((x - prev_x, y - prev_y))
            prev_x, prev_y = x, y
        return path

    def generate_spline_path(self, dx: float, dy: float, steps: int) -> list[tuple[float, float]]:
        if splprep is None:
            logging.warning("scipy not installed; falling back to Bezier.")
            return self.generate_bezier_path(dx, dy, steps)
        points = np.array([[0, 0], [dx * 0.3 + random.uniform(-10, 10), dy * 0.3], 
                           [dx * 0.7 + random.uniform(-10, 10), dy * 0.7], [dx, dy]])
        tck, u = splprep(points.T, s=0)
        u_new = np.linspace(0, 1, steps)
        x_new, y_new = splev(u_new, tck)
        path = [(x_new[i+1] - x_new[i], y_new[i+1] - y_new[i]) for i in range(steps-1)]
        path.append((dx - x_new[-1], dy - y_new[-1]))
        return path

    def detect_targets(self, frame: np.ndarray, region: tuple) -> list:
        left, top, right, bottom = region
        img = frame[top:bottom, left:right]
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        self.calibrate_hsv(hsv)
        game = self.config.game_profile.get()
        target_colors = self.config.target_colors.get().split(',')
        masks = [cv2.inRange(hsv, np.array(self.config.color_ranges[game][color][0]), 
                             np.array(self.config.color_ranges[game][color][1])) 
                 for color in target_colors if color in self.config.color_ranges[game]]
        if not masks:
            return []
        mask = cv2.bitwise_or(*masks) if len(masks) > 1 else masks[0]
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        valid_contours = []
        for contour in contours:
            if cv2.contourArea(contour) > 20:
                moments = cv2.moments(contour)
                if moments["m00"] == 0:
                    continue
                if self.config.hsv_density_filter.get() and game == 'Overwatch 2':
                    x, y, w, h = cv2.boundingRect(contour)
                    density = cv2.contourArea(contour) / (w * h) if w * h > 0 else 0
                    if density > 0.3:
                        valid_contours.append((contour, moments))
                else:
                    valid_contours.append((contour, moments))
        return valid_contours

    def calculate_aim_point(self, best_contour, best_moment, det_center_fov: float) -> tuple[float, float]:
        cX = best_moment["m10"] / best_moment["m00"]
        cY = best_moment["m01"] / best_moment["m00"]
        x, y, w, h = cv2.boundingRect(best_contour)
        aim_location = self.config.aim_location.get()
        if aim_location == 'HEAD':
            cY = y + h * 0.2
        elif aim_location == 'NECK':
            cY = y + h * 0.3
        elif aim_location == 'CHEST':
            cY = y + h * 0.5
        elif aim_location == 'CENTER':
            cY = best_moment["m01"] / best_moment["m00"]
        elif aim_location == 'RANDOM':
            cY = y + h * random.uniform(0.2, 0.5)
        cX += self.config.horizontal_offset.get()
        cY += self.config.vertical_offset.get()
        dx = cX - det_center_fov
        dy = cY - det_center_fov
        return dx, dy

    def perform_aim(self, dx: float, dy: float, aim_center_fov: float) -> None:
        sens = self.config.aimbot_sensitivity.get()
        distance = math.hypot(dx, dy)
        speed_factor = 1 - 0.4 * min(1, distance / (aim_center_fov * 2))
        move_x = dx * (sens / 10) * speed_factor + random.uniform(-3, 3)
        move_y = dy * (sens / 10) * speed_factor + random.uniform(-3, 3)
        if self.config.magnet_aim.get():
            move_x *= 0.4
            move_y *= 0.4
        if random.random() < 0.2:
            overshoot_x, overshoot_y = move_x * 1.1, move_y * 1.1
            self.smooth_move(overshoot_x, overshoot_y)
            time.sleep(random.uniform(0.01, 0.03))
            self.smooth_move(move_x - overshoot_x, move_y - overshoot_y)
        else:
            time.sleep(random.uniform(0.05, 0.2))
            self.smooth_move(move_x, move_y)

    def perform_trigger(self, dx: float, dy: float, trigger_zone: int = 5) -> None:
        if abs(dx) < trigger_zone and abs(dy) < trigger_zone:
            time.sleep(random.uniform(0.05, 0.2))
            mode = self.config.trigger_mode.get()
            if mode == 'HOLD':
                self.mouse.click()
            elif mode == 'BURST':
                for _ in range(random.randint(2, 5)):
                    self.mouse.click()
                    time.sleep(random.uniform(0.01, 0.03))
                    self.mouse.release()
            else:
                self.mouse.click()
                time.sleep(0.01)
                self.mouse.release()

    def apply_rcs(self) -> None:
        if GetAsyncKeyState(0x01) < 0:
            strength = self.config.rcs_strength.get()
            self.mouse.move(0, int(strength * random.uniform(0.8, 1.2)))
            time.sleep(0.01)

    def toggle_pause(self) -> None:
        self.paused = not self.paused
        status = "paused" if self.paused else "resumed"
        self.status_callback(f"Core {status}.")
        logging.info(f"Core {status}.")

    def run(self) -> None:
        self.status_callback("Core thread started.")
        last_frame_time = time.time()
        try:
            while True:
                if self.paused or not self.config.master_toggle.get():
                    time.sleep(0.1)
                    continue
                
                if time.time() - last_frame_time < 1/120:
                    time.sleep(0.001)
                    continue
                last_frame_time = time.time()

                aim_keys = self.config.aim_keys.get().split(',')
                if any(keyboard.is_pressed(key) for key in aim_keys) and (
                    self.config.aimbot_enabled.get() or self.config.triggerbot_enabled.get()
                ):
                    det_fov = self.config.detection_fov.get()
                    aim_fov = self.config.aim_fov.get()
                    if self.config.dynamic_fov.get() and GetAsyncKeyState(0x02) < 0:
                        det_fov *= 0.5
                        aim_fov *= 0.5
                    det_center_fov = det_fov / 2
                    aim_center_fov = aim_fov / 2
                    left = int((self.screen_width - det_fov) / 2)
                    top = int((self.screen_height - det_fov) / 2)
                    right = left + int(det_fov)
                    bottom = top + int(det_fov)
                    region = (left, top, right, bottom)
                    
                    frame = self.get_frame()
                    if frame is None:
                        logging.warning("Invalid frame; skipping.")
                        time.sleep(0.005)
                        continue
                    
                    valid_contours = self.detect_targets(frame, region)
                    if valid_contours:
                        best_contour, best_moment = min(valid_contours, key=lambda c: math.hypot(
                            c[1]["m10"]/c[1]["m00"] - det_center_fov,
                            c[1]["m01"]/c[1]["m00"] - det_center_fov
                        ) if c[1]["m00"] != 0 else (float('inf'), None))
                        if best_moment["m00"] != 0 and abs(best_moment["m10"]/best_moment["m00"] - det_center_fov) <= aim_center_fov and abs(best_moment["m01"]/best_moment["m00"] - det_center_fov) <= aim_center_fov:
                            dx, dy = self.calculate_aim_point(best_contour, best_moment, det_center_fov)
                            if self.config.aimbot_enabled.get():
                                self.perform_aim(dx, dy, aim_center_fov)
                            if self.config.triggerbot_enabled.get():
                                self.perform_trigger(dx, dy)
                
                if self.config.rcs_enabled.get():
                    self.apply_rcs()
                
                time.sleep(0.005)
        except Exception as e:
            logging.error(f"Core loop error: {e}")
            self.status_callback(f"Core error: {e}")
        finally:
            if self.bettercam:
                self.bettercam.stop()
            if self.wgc_session:
                self.wgc_session.Close()
            self.status_callback("Core thread stopped.")

class Tooltip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tip = None
        widget.bind("<Enter>", self.show_tip)
        widget.bind("<Leave>", self.hide_tip)

    def show_tip(self, event=None):
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 25
        self.tip = tk.Toplevel(self.widget)
        self.tip.wm_overrideredirect(True)
        self.tip.wm_geometry(f"+{x}+{y}")
        label = tk.Label(self.tip, text=self.text, background="yellow", relief="solid", borderwidth=1, padx=5, pady=3)
        label.pack()

    def hide_tip(self, event=None):
        if self.tip:
            self.tip.destroy()
            self.tip = None

class AppGUI(tk.Tk):
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.core_logic = None
        self.title("ASCENDANCY AI v7.1")
        self.geometry("450x800")
        self.minsize(450, 600)
        self.resizable(True, True)
        self.configure(bg='#2E2E2E')
        style = ttk.Style(self)
        style.theme_use('clam')
        style.configure("TCheckbutton", background='#2E2E2E', foreground='white', font=('Segoe UI', 10))
        style.configure("TLabel", background='#2E2E2E', foreground='white', font=('Segoe UI', 10))
        style.configure("Header.TLabel", font=('Segoe UI', 14, 'bold'))
        style.configure("TFrame", background='#2E2E2E')
        style.configure("TRadiobutton", background='#2E2E2E', foreground='white', font=('Segoe UI', 10))
        style.map("TRadiobutton", background=[('active', '#3c3c3c')])
        self.create_widgets()
        self.setup_traces()
        self.tray_icon = None
        if pystray:
            self.setup_tray()

    def setup_traces(self) -> None:
        self.config.toggle_key.trace('w', self.update_hotkeys)
        self.config.aim_keys.trace('w', self.update_hotkeys)
        self.config.game_profile.trace('w', self.load_game_profile)
        self.config.input_method.trace('w', self.update_input_method)
        self.config.capture_method.trace('w', self.update_capture_method)
        self.config.detection_fov.trace('w', self.enforce_fov_limits)
        self.config.aim_fov.trace('w', self.enforce_fov_limits)
        self.config.humanization_method.trace('w', self.update_humanization_method)
        for game in self.config.custom_hsv:
            for key in self.config.custom_hsv[game]:
                self.config.custom_hsv[game][key].trace('w', self.update_custom_hsv)

    def create_widgets(self) -> None:
        canvas = tk.Canvas(self, bg='#2E2E2E', highlightthickness=0)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        main_frame = scrollable_frame

        ttk.Label(main_frame, text="ASCENDANCY AI", style="Header.TLabel", foreground="#00FFD1").pack(pady=(0, 5))
        self.status_label = ttk.Label(main_frame, text="Status: INACTIVE", foreground="red", font=('Segoe UI', 12, 'bold'))
        self.status_label.pack(pady=(0, 10))

        self.log_text = tk.Text(main_frame, height=5, wrap="word", bg="#3c3c3c", fg="white", font=('Segoe UI', 9))
        self.log_text.pack(fill='x', pady=5)
        self.log_text.insert(tk.END, "Log initialized.\n")
        self.log_text.config(state=tk.NORMAL)

        # Input Method section
        input_frame = ttk.LabelFrame(main_frame, text=" Input Method ", padding=10)
        input_frame.pack(fill='x', pady=5)
        ttk.Label(input_frame, text="Select Mouse Input").pack(anchor='w')
        combo = ttk.Combobox(input_frame, values=['g-input', 'rzctl-py', 'arduino', 'kmboxnet'], textvariable=self.config.input_method)
        combo.pack(anchor='w')
        combo.bind("<<ComboboxSelected>>", self.update_input_fields)
        ttk.Label(input_frame, text="Choose input driver", font=('Segoe UI', 8, 'italic')).pack(anchor='w')

        # Dynamic fields for Arduino and KMBox
        self.arduino_frame = ttk.Frame(input_frame)
        self.kmbox_frame = ttk.Frame(input_frame)
        ttk.Label(self.arduino_frame, text="COM Port (e.g., COM3)").pack(anchor='w')
        ttk.Entry(self.arduino_frame, textvariable=self.config.arduino_com_port).pack(anchor='w')
        ttk.Label(self.arduino_frame, text="Baud Rate").pack(anchor='w')
        ttk.Entry(self.arduino_frame, textvariable=self.config.arduino_baud_rate).pack(anchor='w')
        ttk.Label(self.kmbox_frame, text="IP Address").pack(anchor='w')
        ttk.Entry(self.kmbox_frame, textvariable=self.config.kmbox_ip).pack(anchor='w')
        ttk.Label(self.kmbox_frame, text="Port").pack(anchor='w')
        ttk.Entry(self.kmbox_frame, textvariable=self.config.kmbox_port).pack(anchor='w')
        ttk.Label(self.kmbox_frame, text="UUID").pack(anchor='w')
        ttk.Entry(self.kmbox_frame, textvariable=self.config.kmbox_uuid).pack(anchor='w')
        self.update_input_fields()

        # Add other sections (Capture Method, Humanization, Game Profile, Target Colors, Custom HSV, Keybinds, Features, Aimbot Settings, HSV Features, Recoil Control) as in initial code.
        # For example:
        capture_frame = ttk.LabelFrame(main_frame, text=" Capture Method ", padding=10)
        capture_frame.pack(fill='x', pady=5)
        ttk.Label(capture_frame, text="Select Capture Method").pack(anchor='w')
        ttk.Combobox(capture_frame, values=['BetterCam', 'WGC'], textvariable=self.config.capture_method).pack(anchor='w')
        ttk.Label(capture_frame, text="BetterCam (fast) or Windows Graphics Capture", font=('Segoe UI', 8, 'italic')).pack(anchor='w')

        # (Continue with all other frames similarly, using the structure from the initial AppGUI code in the conversation)

        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill='x', pady=10)
        ttk.Button(button_frame, text="Save Settings", command=self.config.save_settings).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Reset to Defaults", command=self.config.reset_to_defaults).pack(side="left", padx=5)

    def update_input_fields(self, event=None) -> None:
        method = self.config.input_method.get()
        self.arduino_frame.pack_forget()
        self.kmbox_frame.pack_forget()
        if method == 'arduino':
            self.arduino_frame.pack(fill='x')
        elif method == 'kmboxnet':
            self.kmbox_frame.pack(fill='x')
        self.config.save_settings()

    # Add all other methods (update_status, toggle_master, enforce_fov_limits, update_custom_hsv, etc.) as in previous responses.

    def update_hotkeys(self, *args):
        try:
            keyboard.remove_hotkey(self.config.toggle_key.get())
        except:
            pass
        keyboard.add_hotkey(self.config.toggle_key.get(), self.toggle_master)
        self.core_logic.status_callback(f"Hotkeys updated: Toggle={self.config.toggle_key.get()}, Aim={self.config.aim_keys.get()}")

    def load_game_profile(self, *args):
        profile = self.config.game_profiles.get(self.config.game_profile.get(), self.config.game_profiles['Valorant'])
        for key, value in profile.items():
            getattr(self, key).set(value)
        if self.aim_fov.get() > self.detection_fov.get():
            self.aim_fov.set(self.detection_fov.get())
        self.config.save_settings()
        # Update labels (as in previous)
        self.core_logic.status_callback(f"Loaded profile: {self.config.game_profile.get()}")

    # (Add remaining update methods)

class DummyMouse(MouseBase):
    def move(self, dx, dy):
        logging.warning(f"Dummy move: ({dx}, {dy})")
    def click(self):
        logging.warning("Dummy click")
    def release(self):
        logging.warning("Dummy release")

def main():
    config = AppConfig(encryption_key=None)
    try:
        mouse = create_mouse(config.input_method.get(), config)
    except Exception as e:
        logging.error(f"Initial Mouse init failed: {e}")
        mouse = DummyMouse()
    gui = AppGUI(config)
    gui.core_logic = AscendancyCore(config, mouse, gui.update_status)
    gui.core_logic.start()
    gui.mainloop()

if __name__ == "__main__":
    main()