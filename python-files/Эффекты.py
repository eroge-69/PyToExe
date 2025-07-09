import win32gui
import win32ui
import win32con
import win32api
import random
import time
import math
from ctypes import windll

# Константы
EFFECT_DURATION = 15  # секунд
WIDTH = win32api.GetSystemMetrics(0)
HEIGHT = win32api.GetSystemMetrics(1)

# Глобальные переменные
effects_active = False
start_time = 0

def draw_effects():
    # Получаем контекст всего экрана
    hdc = win32gui.GetDC(0)
    try:
        # Создаем совместимый контекст
        hdcMem = win32ui.CreateDCFromHandle(hdc)
        hbm = win32ui.CreateBitmap()
        hbm.CreateCompatibleBitmap(hdcMem, WIDTH, HEIGHT)
        hdcMem.SelectObject(hbm)
        
        # Рисуем эффекты
        for _ in range(50):
            x = random.randint(0, WIDTH)
            y = random.randint(0, HEIGHT)
            radius = random.randint(10, 100)
            color = win32api.RGB(
                random.randint(0, 255),
                random.randint(0, 255),
                random.randint(0, 255)
            )
            
            # Рисуем круг
            brush = win32ui.CreateBrush(win32con.BS_SOLID, color, 0)
            old_brush = hdcMem.SelectObject(brush)
            hdcMem.Ellipse((x-radius, y-radius, x+radius, y+radius))
            hdcMem.SelectObject(old_brush)
            brush.DeleteObject()
            
            # Рисуем линии
            for _ in range(5):
                x2 = random.randint(0, WIDTH)
                y2 = random.randint(0, HEIGHT)
                pen = win32ui.CreatePen(win32con.PS_SOLID, 2, color)
                old_pen = hdcMem.SelectObject(pen)
                hdcMem.MoveTo((x, y))
                hdcMem.LineTo((x2, y2))
                hdcMem.SelectObject(old_pen)
                pen.DeleteObject()
        
        # Копируем на экран
        windll.user32.BitBlt(hdc, 0, 0, WIDTH, HEIGHT, hdcMem.GetHandleAttrib(), 0, 0, win32con.SRCCOPY)
        
    finally:
        win32gui.ReleaseDC(0, hdc)
        hdcMem.DeleteDC()
        hbm.DeleteObject()

def clear_screen():
    # Просто обновляем весь экран
    hdc = win32gui.GetDC(0)
    try:
        windll.user32.InvalidateRect(0, None, True)
        windll.user32.UpdateWindow(0)
    finally:
        win32gui.ReleaseDC(0, hdc)

def main():
    global effects_active, start_time
    
    print("Управление:")
    print("1 - Включить эффекты")
    print("2 - Очистить экран")
    print("ESC - Выход")
    
    while True:
        if effects_active and time.time() - start_time > EFFECT_DURATION:
            effects_active = False
            clear_screen()
            print("Эффекты автоматически отключены")
        
        if win32api.GetAsyncKeyState(win32con.VK_ESCAPE) & 0x8000:
            break
            
        if win32api.GetAsyncKeyState(ord('1')) & 0x8000:
            effects_active = True
            start_time = time.time()
            print("Эффекты включены")
            time.sleep(0.3)  # Задержка для предотвращения многократного срабатывания
            
        if win32api.GetAsyncKeyState(ord('2')) & 0x8000:
            effects_active = False
            clear_screen()
            print("Эффекты отключены")
            time.sleep(0.3)
            
        if effects_active:
            draw_effects()
            time.sleep(0.05)

if __name__ == "__main__":
    main()