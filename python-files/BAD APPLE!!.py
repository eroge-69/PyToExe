import os
import time
import ctypes
import threading
import subprocess
import random
import cv2
from ctypes import wintypes
from tkinter import Tk, Text, BOTH

# Windows API
user32 = ctypes.WinDLL('user32', use_last_error=True)
GetDC = user32.GetDC
GetDC.restype = wintypes.HDC
GetDC.argtypes = [wintypes.HWND]
DrawIcon = user32.DrawIcon
DrawIcon.restype = wintypes.BOOL
DrawIcon.argtypes = [wintypes.HDC, ctypes.c_int, ctypes.c_int, wintypes.HICON]
GetCursorPos = user32.GetCursorPos
GetCursorPos.restype = wintypes.BOOL
GetCursorPos.argtypes = [ctypes.POINTER(wintypes.POINT)]
LoadIconW = user32.LoadIconW
LoadIconW.restype = wintypes.HICON
LoadIconW.argtypes = [wintypes.HWND, ctypes.c_int]

IDI_ERROR = 32513
IDI_WARNING = 32515
IconError = LoadIconW(None, IDI_ERROR)
IconWarning = LoadIconW(None, IDI_WARNING)

class POINT(ctypes.Structure):
    _fields_ = [('x', ctypes.c_long), ('y', ctypes.c_long)]

def kill_explorer():
    os.system("taskkill /f /im explorer.exe")

def start_explorer():
    subprocess.Popen("explorer.exe")

ASCII_CHARS = "@%#*+=-:. "

def frame_to_ascii(frame, width=120):
    height = int((frame.shape[0] / frame.shape[1]) * width * 0.55)
    resized = cv2.resize(frame, (width, height))
    gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
    ascii_frame = "\n".join(
        "".join(ASCII_CHARS[pixel // 32] for pixel in row) for row in gray
    )
    return ascii_frame

def play_audio():
    subprocess.run([
        "ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet", "bad-apple-audio.mp3"
    ])

def draw_error_icons(stop_event):
    hdc = GetDC(0)
    pt = POINT()
    sw = ctypes.windll.user32.GetSystemMetrics(0)
    sh = ctypes.windll.user32.GetSystemMetrics(1)
    while not stop_event.is_set():
        x = random.randint(0, sw-32)
        y = random.randint(0, sh-32)
        DrawIcon(hdc, x, y, IconWarning)
        if GetCursorPos(ctypes.byref(pt)):
            DrawIcon(hdc, pt.x, pt.y, IconError)
        time.sleep(0.01)

def fullscreen_lock_and_play(stop_event):
    root = Tk()
    root.title("?")
    root.attributes("-fullscreen", True)
    root.attributes("-topmost", True)
    root.config(cursor="none", bg="black")

    def on_key(event):
        if event.char.lower() == 'k':
            stop_event.set()
            root.destroy()
            return "break"
        return "break"  # Diğer tüm tuşları engelle

    root.bind_all("<Key>", on_key)

    def disable_event():
        pass
    root.protocol("WM_DELETE_WINDOW", disable_event)

    text = Text(root, bg="black", fg="white", font=("Consolas", 8))
    text.pack(fill=BOTH, expand=True)

    def update_ascii(ascii_frame):
        if stop_event.is_set():
            root.destroy()
            return
        text.delete(1.0, "end")
        text.insert("end", ascii_frame)
        root.after(1, lambda: None)

    def play_video():
        cap = cv2.VideoCapture("BadApple.mp4")
        target_fps = 45
        frame_duration = 1 / target_fps

        audio_thread = threading.Thread(target=play_audio)
        audio_thread.start()

        while not stop_event.is_set():
            start_time = time.time()
            ret, frame = cap.read()
            if not ret:
                break
            ascii_art = frame_to_ascii(frame)
            root.after(0, update_ascii, ascii_art)

            elapsed = time.time() - start_time
            time.sleep(max(0, frame_duration - elapsed))

        cap.release()
        audio_thread.join()
        stop_event.set()

    video_thread = threading.Thread(target=play_video)
    video_thread.start()

    root.mainloop()

def main():
    print("?x2")
    kill_explorer()
    time.sleep(2)

    stop_event = threading.Event()

    draw_thread = threading.Thread(target=draw_error_icons, args=(stop_event,))
    draw_thread.start()

    fullscreen_lock_and_play(stop_event)

    stop_event.set()
    draw_thread.join()

    print("??")
    start_explorer()

    print("???")
    os._exit(0)

if __name__ == "__main__":
    main()  virüşmü explorer kapatma hariç