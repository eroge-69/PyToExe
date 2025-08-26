import os
import subprocess
import threading
import ctypes
import win32con
import win32gui
import win32api
from infi.systray import SysTrayIcon

# Programs to run
PROGRAM_ON = r".\litra.exe on"
PROGRAM_OFF = r".\litra.exe off"

# Windows constants
WM_DEVICECHANGE = 0x0219
DBT_DEVICEARRIVAL = 0x8000
DBT_DEVICEREMOVECOMPLETE = 0x8004

# Icons
ICON_OFF = "bulb_off.ico"
ICON_ON = "bulb_on.ico"

# Globals
camera_active = False
systray = None


def run_program(command):
    """Run a command string like '.\\litra.exe on'."""
    try:
        subprocess.Popen(command, shell=True)
    except Exception as e:
        print(f"Failed to run {command}: {e}")


def wnd_proc(hwnd, msg, wparam, lparam):
    global camera_active, systray

    if msg == WM_DEVICECHANGE:
        if wparam == DBT_DEVICEARRIVAL:  # Camera ON
            if not camera_active:
                print("📷 Camera ON")
                run_program(PROGRAM_ON)
                camera_active = True
                if systray:
                    systray.icon = ICON_ON
                    systray.hover_text = "Camera ON"
                    systray.update()
        elif wparam == DBT_DEVICEREMOVECOMPLETE:  # Camera OFF
            if camera_active:
                print("📷 Camera OFF")
                run_program(PROGRAM_OFF)
                camera_active = False
                if systray:
                    systray.icon = ICON_OFF
                    systray.hover_text = "Camera OFF"
                    systray.update()

    return win32gui.DefWindowProc(hwnd, msg, wparam, lparam)


def start_message_loop():
    hInstance = win32api.GetModuleHandle(None)
    className = "CameraWatcher"

    wndClass = win32gui.WNDCLASS()
    wndClass.lpfnWndProc = wnd_proc
    wndClass.hInstance = hInstance
    wndClass.lpszClassName = className
    atom = win32gui.RegisterClass(wndC
