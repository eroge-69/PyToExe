import pyautogui
from PIL import ImageGrab
from screeninfo import get_monitors
import time
import threading
import tkinter as tk
import ctypes
import win32con
import win32gui

def make_window_clickthrough(hwnd):
    ex_style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
    ex_style |= win32con.WS_EX_LAYERED | win32con.WS_EX_TRANSPARENT
    win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, ex_style)


target_color = (252, 107, 60)
tolerance = 10
prev_position = None
start_time = None

root = tk.Tk()
root.attributes('-topmost', True)
root.attributes('-transparentcolor', 'white')
root.overrideredirect(True)
root.update_idletasks()
root.update()
hwnd = ctypes.windll.user32.GetParent(root.winfo_id())
make_window_clickthrough(hwnd)


monitor = get_monitors()[0]
screen_w = monitor.width
screen_h = monitor.height
screen_x = monitor.x
screen_y = monitor.y

canvas = tk.Canvas(root, width=screen_w, height=screen_h, bg='white', highlightthickness=0)
canvas.pack()
root.geometry(f'{screen_w}x{screen_h}+{screen_x}+{screen_y}')

def color_match(c1, c2, tolerance):
    return all(abs(a - b) <= tolerance for a, b in zip(c1, c2))

def draw_overlay(prev_pos, new_pos, elapsed_time):
    canvas.delete('all')
    if prev_pos:
        canvas.create_line(prev_pos[0] - screen_x, prev_pos[1] - screen_y,
                           new_pos[0] - screen_x, new_pos[1] - screen_y,
                           fill='blue', width=3)
    radius = 80
    center_x = new_pos[0] - screen_x
    center_y = new_pos[1] - screen_y
    canvas.create_oval(center_x - radius, center_y - radius, center_x + radius, center_y + radius,
                       outline='red', width=2)
    time_text = f'{elapsed_time:.2f} 성공'
    canvas.create_text(center_x, center_y - radius - 10, text=time_text, fill='black',
                       font=('Arial', 12, 'bold'))

def start_tracking():
    global prev_position, start_time
    start_time = time.time()
    while True:
        img = ImageGrab.grab(bbox=(screen_x, screen_y, screen_x + screen_w, screen_y + screen_h))
        pixels = img.load()

        matched_pixels = []
        for y in range(0, screen_h, 4):  # 5 -> 3으로 조금 더 촘촘히 검사
            for x in range(0, screen_w, 4):
                pixel_color = pixels[x, y][:3]
                if color_match(pixel_color, target_color, tolerance):
                    matched_pixels.append((x + screen_x, y + screen_y))

        if matched_pixels:
            xs = [p[0] for p in matched_pixels]
            ys = [p[1] for p in matched_pixels]

            min_x, max_x = min(xs), max(xs)
            min_y, max_y = min(ys), max(ys)

            center_x = (min_x + max_x) // 2
            center_y = (min_y + max_y) // 2

            new_position = (center_x, center_y)
            elapsed = time.time() - start_time
            draw_overlay(prev_position, new_position, elapsed)
            pyautogui.moveTo(new_position[0], new_position[1])
            pyautogui.click()
            prev_position = new_position
            start_time = time.time()

        time.sleep(0)


threading.Thread(target=start_tracking, daemon=True).start()
root.mainloop()
