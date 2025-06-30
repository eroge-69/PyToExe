import PySimpleGUI as sg
import pyautogui
import time
import cv2
import numpy as np
import threading
import json
import os
from PIL import Image, ImageTk
import io

class FishingBot:
    CONFIG_FILE = 'fishing_bot_config.json'
    
    def __init__(self):
        self.default_config = {
            'keys': {
                'cast': 'f',
                'hook': 'space',
                'left': 'a',
                'right': 'd',
                'interact': 'e',
                'emergency_stop': 'f12'
            },
            'regions': {
                'bite': [810, 500, 300, 100],
                'fight': [900, 400, 120, 120]
            },
            'delays': {
                'after_cast': 2.0,
                'bite_check': 0.3,
                'after_hook': 1.0,
                'fight_delay': 0.2,
                'catch_delay': 3.5
            },
            'colors': {
                'lower_green': [40, 50, 50],
                'upper_green': [80, 255, 255]
            }
        }
        
        self.load_config()
        self.running = False
        self.fish_count = 0
        self.status = "Остановлен"

    def load_config(self):
        if os.path.exists(self.CONFIG_FILE):
            with open(self.CONFIG_FILE, 'r') as f:
                self.config = json.load(f)
        else:
            self.config = self.default_config
            self.save_config()

    def save_config(self):
        with open(self.CONFIG_FILE, 'w') as f:
            json.dump(self.config, f, indent=4)

    def start(self):
        self.running = True
        self.status = "Работает"
        threading.Thread(target=self.fishing_process, daemon=True).start()

    def stop(self):
        self.running = False
        self.status = "Остановлен"

    def fishing_process(self):
        while self.running:
            try:
                # 1. Cast fishing rod
                self.press_key(self.config['keys']['cast'])
                time.sleep(self.config['delays']['after_cast'])
                
                # 2. Wait for bite
                if not self.wait_for_bite():
                    continue
                
                # 3. Hook the fish
                self.press_key(self.config['keys']['hook'])
                time.sleep(self.config['delays']['after_hook'])
                
                # 4. Fight with fish
                self.fight_with_fish()
                
                # 5. Get catch
                self.get_catch()
                self.fish_count += 1
                
            except Exception as e:
                print(f"Error: {e}")
                self.stop()

    # ... (остальные методы класса остаются без изменений)

def create_gui():
    bot = FishingBot()
    sg.theme('DarkTeal9')
    
    # Key selection dropdown
    key_options = [chr(i) for i in range(97, 123)] + [
        'space', 'enter', 'shift', 'ctrl', 'alt', 
        'f1', 'f2', 'f3', 'f4', 'f5', 'f6', 
        'f7', 'f8', 'f9', 'f10', 'f11', 'f12'
    ]
    
    # Main layout
    layout = [
        [sg.Text('Fishing Bot Pro - Полный контроль', font=('Arial', 16, 'bold'))],
        [sg.HorizontalSeparator()],
        
        [sg.Frame('Управление', [
            [sg.Button('Старт', key='-START-', size=(10, 1), button_color=('white', 'green')),
             sg.Button('Стоп', key='-STOP-', size=(10, 1), button_color=('white', 'red')),
             sg.Button('Экстренный стоп', key='-ESTOP-', button_color=('white', 'orange'))],
            [sg.Text('Статус:'), sg.Text(bot.status, key='-STATUS-', size=(15, 1)),
             sg.Text('Поймано:'), sg.Text('0', key='-FISHCOUNT-', size=(10, 1))]
        ])],
        
        [sg.TabGroup([[
            sg.Tab('Клавиши', [
                [sg.Text('Заброс:'), sg.Combo(key_options, default_value=bot.config['keys']['cast'], key='-KEY_CAST-')],
                [sg.Text('Подсечка:'), sg.Combo(key_options, default_value=bot.config['keys']['hook'], key='-KEY_HOOK-')],
                [sg.Text('Влево:'), sg.Combo(key_options, default_value=bot.config['keys']['left'], key='-KEY_LEFT-')],
                [sg.Text('Вправо:'), sg.Combo(key_options, default_value=bot.config['keys']['right'], key='-KEY_RIGHT-')],
                [sg.Text('Взаимодействие:'), sg.Combo(key_options, default_value=bot.config['keys']['interact'], key='-KEY_INTERACT-')],
                [sg.Text('Экстренный стоп:'), sg.Combo(key_options, default_value=bot.config['keys']['emergency_stop'], key='-KEY_ESTOP-')]
            ]),
            
            sg.Tab('Области', [
                [sg.Text('Область поклёвки (X,Y,W,H):')],
                [sg.Input(bot.config['regions']['bite'][0], size=5, key='-BITE_X-'),
                 sg.Input(bot.config['regions']['bite'][1], size=5, key='-BITE_Y-'),
                 sg.Input(bot.config['regions']['bite'][2], size=5, key='-BITE_W-'),
                 sg.Input(bot.config['regions']['bite'][3], size=5, key='-BITE_H-'),
                 sg.Button('Тест', key='-TEST_BITE-')],
                
                [sg.Text('Область борьбы (X,Y,W,H):')],
                [sg.Input(bot.config['regions']['fight'][0], size=5, key='-FIGHT_X-'),
                 sg.Input(bot.config['regions']['fight'][1], size=5, key='-FIGHT_Y-'),
                 sg.Input(bot.config['regions']['fight'][2], size=5, key='-FIGHT_W-'),
                 sg.Input(bot.config['regions']['fight'][3], size=5, key='-FIGHT_H-'),
                 sg.Button('Тест', key='-TEST_FIGHT-')],
                
                [sg.Image(key='-PREVIEW-')]
            ]),
            
            sg.Tab('Тайминги', [
                [sg.Text('После заброса:'), sg.Input(bot.config['delays']['after_cast'], size=5, key='-DELAY_CAST-'), sg.Text('сек')],
                [sg.Text('Проверка поклёвки:'), sg.Input(bot.config['delays']['bite_check'], size=5, key='-DELAY_BITE-'), sg.Text('сек')],
                [sg.Text('После подсечки:'), sg.Input(bot.config['delays']['after_hook'], size=5, key='-DELAY_HOOK-'), sg.Text('сек')],
                [sg.Text('Задержка борьбы:'), sg.Input(bot.config['delays']['fight_delay'], size=5, key='-DELAY_FIGHT-'), sg.Text('сек')],
                [sg.Text('Получение улова:'), sg.Input(bot.config['delays']['catch_delay'], size=5, key='-DELAY_CATCH-'), sg.Text('сек')]
            ]),
            
            sg.Tab('Цвета', [
                [sg.Text('Нижний порог зелёного (H,S,V):')],
                [sg.Input(bot.config['colors']['lower_green'][0], size=5, key='-LOW_H-'),
                 sg.Input(bot.config['colors']['lower_green'][1], size=5, key='-LOW_S-'),
                 sg.Input(bot.config['colors']['lower_green'][2], size=5, key='-LOW_V-')],
                
                [sg.Text('Верхний порог зелёного (H,S,V):')],
                [sg.Input(bot.config['colors']['upper_green'][0], size=5, key='-HIGH_H-'),
                 sg.Input(bot.config['colors']['upper_green'][1], size=5, key='-HIGH_S-'),
                 sg.Input(bot.config['colors']['upper_green'][2], size=5, key='-HIGH_V-')],
                
                [sg.Button('Тест цвета', key='-TEST_COLOR-')]
            ])
        ]])],
        
        [sg.Button('Сохранить настройки', key='-SAVE-'), 
         sg.Button('Сброс настроек', key='-RESET-'),
         sg.Button('Выход', key='-EXIT-')]
    ]
    
    window = sg.Window('Fishing Bot Pro', layout, finalize=True)
    
    def update_status():
        window['-STATUS-'].update(bot.status)
        window['-FISHCOUNT-'].update(str(bot.fish_count))
    
    def save_settings():
        bot.config = {
            'keys': {
                'cast': values['-KEY_CAST-'],
                'hook': values['-KEY_HOOK-'],
                'left': values['-KEY_LEFT-'],
                'right': values['-KEY_RIGHT-'],
                'interact': values['-KEY_INTERACT-'],
                'emergency_stop': values['-KEY_ESTOP-']
            },
            'regions': {
                'bite': [
                    int(values['-BITE_X-']),
                    int(values['-BITE_Y-']),
                    int(values['-BITE_W-']),
                    int(values['-BITE_H-'])
                ],
                'fight': [
                    int(values['-FIGHT_X-']),
                    int(values['-FIGHT_Y-']),
                    int(values['-FIGHT_W-']),
                    int(values['-FIGHT_H-'])
                ]
            },
            'delays': {
                'after_cast': float(values['-DELAY_CAST-']),
                'bite_check': float(values['-DELAY_BITE-']),
                'after_hook': float(values['-DELAY_HOOK-']),
                'fight_delay': float(values['-DELAY_FIGHT-']),
                'catch_delay': float(values['-DELAY_CATCH-'])
            },
            'colors': {
                'lower_green': [
                    int(values['-LOW_H-']),
                    int(values['-LOW_S-']),
                    int(values['-LOW_V-'])
                ],
                'upper_green': [
                    int(values['-HIGH_H-']),
                    int(values['-HIGH_S-']),
                    int(values['-HIGH_V-'])
                ]
            }
        }
        bot.save_config()
        sg.popup('Настройки сохранены!', title='Успех')
    
    while True:
        event, values = window.read(timeout=100)
        
        if event in (sg.WIN_CLOSED, '-EXIT-'):
            bot.stop()
            break
            
        elif event == '-START-':
            save_settings()
            bot.start()
            
        elif event == '-STOP-':
            bot.stop()
            
        elif event == '-ESTOP-':
            bot.stop()
            pyautogui.press(bot.config['keys']['emergency_stop'])
            
        elif event == '-SAVE-':
            save_settings()
            
        elif event == '-RESET-':
            bot.config = bot.default_config
            bot.save_config()
            sg.popup('Настройки сброшены!', title='Успех')
            # Обновляем интерфейс
            window.close()
            return create_gui()
            
        elif event == '-TEST_BITE-':
            region = (
                int(values['-BITE_X-']), int(values['-BITE_Y-']),
                int(values['-BITE_W-']), int(values['-BITE_H-'])
            )
            try:
                screenshot = pyautogui.screenshot(region=region)
                bio = io.BytesIO()
                screenshot.save(bio, format='PNG')
                window['-PREVIEW-'].update(data=bio.getvalue())
            except Exception as e:
                sg.popup_error(f"Ошибка: {e}")
        
        elif event == '-TEST_FIGHT-':
            region = (
                int(values['-FIGHT_X-']), int(values['-FIGHT_Y-']),
                int(values['-FIGHT_W-']), int(values['-FIGHT_H-'])
            )
            try:
                screenshot = pyautogui.screenshot(region=region)
                bio = io.BytesIO()
                screenshot.save(bio, format='PNG')
                window['-PREVIEW-'].update(data=bio.getvalue())
            except Exception as e:
                sg.popup_error(f"Ошибка: {e}")
        
        elif event == '-TEST_COLOR-':
            try:
                lower = np.array([
                    int(values['-LOW_H-']),
                    int(values['-LOW_S-']),
                    int(values['-LOW_V-'])
                ])
                upper = np.array([
                    int(values['-HIGH_H-']),
                    int(values['-HIGH_S-']),
                    int(values['-HIGH_V-'])
                ])
                
                region = (
                    int(values['-BITE_X-']), int(values['-BITE_Y-']),
                    int(values['-BITE_W-']), int(values['-BITE_H-'])
                )
                
                screenshot = pyautogui.screenshot(region=region)
                img = np.array(screenshot)
                hsv = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)
                mask = cv2.inRange(hsv, lower, upper)
                res = cv2.bitwise_and(img, img, mask=mask)
                
                bio = io.BytesIO()
                Image.fromarray(res).save(bio, format='PNG')
                window['-PREVIEW-'].update(data=bio.getvalue())
                
                sg.popup(f"Найдено пикселей: {cv2.countNonZero(mask)}")
            except Exception as e:
                sg.popup_error(f"Ошибка: {e}")
        
        update_status()
    
    window.close()

if __name__ == "__main__":
    create_gui()