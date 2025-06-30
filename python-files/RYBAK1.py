import PySimpleGUI as sg
import pyautogui
import time
import cv2
import numpy as np
import threading
from PIL import Image, ImageTk
import io

class FishingBot:
    def __init__(self):
        # Настройки для зелёного индикатора
        self.region = (810, 500, 300, 100)  # Область поиска (x,y,width,height)
        self.lower_color = (0, 200, 0)      # Минимальный зелёный (R,G,B)
        self.upper_color = (100, 255, 100)  # Максимальный зелёный
        self.cast_key = 'f'                 # Клавиша заброса
        self.hook_key = 'space'             # Клавиша подсечки
        self.running = False
        self.delay_after_cast = 2           # Задержка после заброса
        self.bite_check_interval = 0.5      # Проверка поклёвки каждые 0.5 сек
        self.hook_delay = 3                 # Задержка после подсечки

    def start(self):
        self.running = True
        threading.Thread(target=self.fishing_loop, daemon=True).start()

    def stop(self):
        self.running = False

    def fishing_loop(self):
        while self.running:
            try:
                # Заброс удочки
                pyautogui.press(self.cast_key)
                time.sleep(self.delay_after_cast)
                
                # Ожидание поклёвки
                bite_timeout = 10  # Макс время ожидания поклёвки
                start_time = time.time()
                
                while self.running and (time.time() - start_time) < bite_timeout:
                    if self.check_for_bite():
                        pyautogui.press(self.hook_key)
                        time.sleep(self.hook_delay)
                        break
                    time.sleep(self.bite_check_interval)
                
            except Exception as e:
                print(f"Ошибка: {e}")
                self.stop()

    def check_for_bite(self):
        screenshot = pyautogui.screenshot(region=self.region)
        img = np.array(screenshot)
        hsv = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)
        
        # Более точное определение зелёного в HSV-пространстве
        lower_green = np.array([40, 50, 50])
        upper_green = np.array([80, 255, 255])
        mask = cv2.inRange(hsv, lower_green, upper_green)
        
        return cv2.countNonZero(mask) > 50  # Порог срабатывания

def create_gui():
    bot = FishingBot()
    sg.theme('DarkGreen4')
    
    layout = [
        [sg.Text('Fishing Bot (Зелёный индикатор)', font=('Helvetica', 16))],
        [sg.HorizontalSeparator()],
        
        [sg.Frame('Настройки цвета', [
            [sg.Text('Диапазон зелёного (RGB):')],
            [sg.Text('От:'), sg.Input('0', size=3, key='-R1-'), 
             sg.Input('200', size=3, key='-G1-'), 
             sg.Input('0', size=3, key='-B1-')],
            [sg.Text('До:'), sg.Input('100', size=3, key='-R2-'),
             sg.Input('255', size=3, key='-G2-'),
             sg.Input('100', size=3, key='-B2-')],
        ])],
        
        [sg.Frame('Тайминги (сек)', [
            [sg.Text('После заброса:'), sg.Input('2', size=5, key='-DELAY_CAST-')],
            [sg.Text('Проверка поклёвки:'), sg.Input('0.5', size=5, key='-CHECK_INT-')],
            [sg.Text('После подсечки:'), sg.Input('3', size=5, key='-DELAY_HOOK-')],
        ])],
        
        [sg.Frame('Область поиска', [
            [sg.Text('X:'), sg.Input('810', size=5, key='-X-'),
             sg.Text('Y:'), sg.Input('500', size=5, key='-Y-')],
            [sg.Text('Ширина:'), sg.Input('300', size=5, key='-W-'),
             sg.Text('Высота:'), sg.Input('100', size=5, key='-H-')],
            [sg.Button('Обновить настройки', key='-UPDATE-')]
        ])],
        
        [sg.Frame('Управление', [
            [sg.Button('Старт', key='-START-', button_color=('white', 'green')),
             sg.Button('Стоп', key='-STOP-', button_color=('white', 'red'))],
            [sg.Text('Статус:'), sg.Text('Остановлен', key='-STATUS-')]
        ])],
        
        [sg.Image(key='-PREVIEW-')],
        [sg.Button('Тест области', key='-TEST-'), sg.Button('Выход', key='-EXIT-')]
    ]
    
    window = sg.Window('Зелёный рыбак v2.0', layout, finalize=True)
    
    def update_preview():
        try:
            screenshot = pyautogui.screenshot(region=(
                int(values['-X-']), int(values['-Y-']),
                int(values['-W-']), int(values['-H-'])
            ))
            bio = io.BytesIO()
            screenshot.save(bio, format='PNG')
            window['-PREVIEW-'].update(data=bio.getvalue())
        except:
            pass
    
    while True:
        event, values = window.read(timeout=100)
        
        if event in (sg.WIN_CLOSED, '-EXIT-'):
            bot.stop()
            break
            
        elif event == '-UPDATE-':
            try:
                bot.region = (
                    int(values['-X-']), int(values['-Y-']),
                    int(values['-W-']), int(values['-H-'])
                )
                bot.lower_color = (
                    int(values['-R1-']), int(values['-G1-']), int(values['-B1-'])
                )
                bot.upper_color = (
                    int(values['-R2-']), int(values['-G2-']), int(values['-B2-'])
                )
                bot.delay_after_cast = float(values['-DELAY_CAST-'])
                bot.bite_check_interval = float(values['-CHECK_INT-'])
                bot.hook_delay = float(values['-DELAY_HOOK-'])
                sg.popup_ok('Настройки обновлены!')
            except Exception as e:
                sg.popup_error(f'Ошибка: {e}')
                
        elif event == '-TEST-':
            update_preview()
            
        elif event == '-START-':
            bot.start()
            window['-STATUS-'].update('Работает')
            update_preview()
            
        elif event == '-STOP-':
            bot.stop()
            window['-STATUS-'].update('Остановлен')
    
    window.close()

if __name__ == "__main__":
    create_gui()