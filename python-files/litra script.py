import subprocess
import win32gui
import win32api
import threading
import os
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
systray = None  # will hold the tray object


def run_program(path):
    try:
        subprocess.Popen(path, shell=True)
    except Exception as e:
        print(f"Failed to run {path}: {e}")


def wnd_proc(hwnd, msg, wparam, lparam):
    global camera_active, systray

    if msg == WM_DEVICECHANGE:
        if wparam == DBT_DEVICEARRIVAL:  # camera powered on
            if not camera_active:
                print("📷 Camera ON")
                run_program(PROGRAM_ON)
                camera_active = True
                if systray:
                    systray.update(icon=ICON_ON, hover_text="Camera ON")
        elif wparam == DBT_DEVICEREMOVECOMPLETE:  # camera powered off
            if camera_active:
                print("📷 Camera OFF")
                run_program(PROGRAM_OFF)
                camera_active = False
                if systray:
                    systray.update(icon=ICON_OFF, hover_text="Camera OFF")

    return win32gui.DefWindowProc(hwnd, msg, wparam, lparam)


def start_message_loop():
    hInstance = win32api.GetModuleHandle(None)
    className = "CameraWatcher"

    wndClass = win32gui.WNDCLASS()
    wndClass.lpfnWndProc = wnd_proc
    wndClass.hInstance = hInstance
    wndClass.lpszClassName = className
    atom = win32gui.RegisterClass(wndClass)

    hwnd = win32gui.CreateWindow(
        atom,
        className,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        hInstance,
        None,
    )

    win32gui.PumpMessages()


def on_quit_callback(systray_obj):
    print("Exiting Camera Watcher...")
    os._exit(0)  # hard exit


def main():
    global systray

    # Start the hidden window listener in another thread
    threading.Thread(target=start_message_loop, daemon=True).start()

    # Tray icon starts with OFF state
    systray = SysTrayIcon(ICON_OFF, "Camera OFF", (), on_quit=on_quit_callback)
    systray.start()


if __name__ == "__main__":
    main()
