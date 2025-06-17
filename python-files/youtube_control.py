
import keyboard
import pyautogui
import time
import win32gui
import win32con

def find_youtube_window():
    def enum_handler(hwnd, result):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if "YouTube" in title:
                result.append(hwnd)
    windows = []
    win32gui.EnumWindows(enum_handler, windows)
    return windows[0] if windows else None

def toggle_play_pause():
    hwnd = find_youtube_window()
    if not hwnd:
        print("YouTube uygulaması bulunamadı.")
        return
    # Şu anki aktif pencereyi al
    foreground = win32gui.GetForegroundWindow()

    # YouTube uygulamasına geç
    win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
    win32gui.SetForegroundWindow(hwnd)
    time.sleep(0.4)

    # 'k' tuşunu gönder
    pyautogui.press('k')
    time.sleep(0.2)

    # Eski pencereye geri dön
    win32gui.SetForegroundWindow(foreground)

print("Hazır: Ctrl + Alt + Z ile YouTube oynatma/duraklat.")
keyboard.add_hotkey('ctrl+alt+z', toggle_play_pause)

keyboard.wait()
