# working_fishing_bot.py
import pyautogui
import cv2
import numpy as np
import time
import keyboard
import random
import sys
from PIL import ImageGrab
from pynput.mouse import Controller

class FishingBot:
    def __init__(self):
        self.running = False
        self.debug_mode = False
        self.cast_delay = 5.0
        self.last_cast_time = 0
        self.fish_status = "waiting"  # waiting, casting, fishing, reeling
        self.mouse = Controller()
        
        # Настраиваемые параметры (подстройте под ваш сервер)
        self.config = {
            'cast_key': 'e',
            'reel_key': 'space',
            'fps': 10,
            'bite_threshold': 0.75,
            'reaction_delay': (0.2, 0.5),
            'fishing_spot_color': {
                'lower': np.array([70, 200, 200]),
                'upper': np.array([80, 230, 255])
            },
            'bite_color': {
                'lower': np.array([0, 150, 50]),
                'upper': np.array([10, 255, 150])
            }
        }
        
        self.setup_hotkeys()
        print("Бот для рыбалки инициализирован. Нажмите F6 для старта/остановки")

    def setup_hotkeys(self):
        keyboard.add_hotkey('f6', self.toggle_bot)
        keyboard.add_hotkey('f7', self.toggle_debug)
        keyboard.add_hotkey('f8', self.exit_bot)

    def toggle_bot(self):
        self.running = not self.running
        status = "ВКЛЮЧЕН" if self.running else "ВЫКЛЮЧЕН"
        print(f"Бот {status}. Статус: {self.fish_status}")

    def toggle_debug(self):
        self.debug_mode = not self.debug_mode
        print(f"Режим отладки: {'ВКЛЮЧЕН' if self.debug_mode else 'ВЫКЛЮЧЕН'}")

    def exit_bot(self):
        print("Завершение работы бота...")
        sys.exit(0)

    def get_screenshot(self, region=None):
        try:
            if region:
                screenshot = ImageGrab.grab(bbox=region)
            else:
                screenshot = ImageGrab.grab()
            return cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
        except Exception as e:
            print(f"Ошибка при получении скриншота: {e}")
            return None

    def find_fishing_spot(self):
        screenshot = self.get_screenshot()
        if screenshot is None:
            return None
            
        mask = cv2.inRange(screenshot, 
                          self.config['fishing_spot_color']['lower'],
                          self.config['fishing_spot_color']['upper'])
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if contours:
            largest = max(contours, key=cv2.contourArea)
            x, y, w, h = cv2.boundingRect(largest)
            return (x + w//2, y + h//2)
        return None

    def detect_bite(self):
        screen_width, screen_height = pyautogui.size()
        region = (screen_width//2 - 150, screen_height//2 - 150, 300, 300)
        screenshot = self.get_screenshot(region)
        
        if screenshot is None:
            return False
            
        mask = cv2.inRange(screenshot,
                          self.config['bite_color']['lower'],
                          self.config['bite_color']['upper'])
        
        if self.debug_mode:
            debug_img = cv2.resize(mask, (400, 400))
            cv2.imshow('Bite Detection', debug_img)
            cv2.waitKey(1)
            
        return np.sum(mask) / (mask.size) > self.config['bite_threshold']

    def cast_line(self):
        spot = self.find_fishing_spot()
        if spot:
            # Плавное перемещение к точке
            start_pos = self.mouse.position
            steps = 20
            for i in range(steps):
                t = i / steps
                x = start_pos[0] + (spot[0] - start_pos[0]) * t
                y = start_pos[1] + (spot[1] - start_pos[1]) * t
                self.mouse.position = (x, y)
                time.sleep(0.02)
            
            # Имитация человеческого клика
            self.mouse.press(mouse.Button.left)
            time.sleep(random.uniform(0.1, 0.3))
            self.mouse.release(mouse.Button.left)
            
            # Заброс удочки
            keyboard.press(self.config['cast_key'])
            time.sleep(random.uniform(0.2, 0.4))
            keyboard.release(self.config['cast_key'])
            
            self.fish_status = "fishing"
            self.last_cast_time = time.time()
            print("Удочка заброшена")
            return True
        return False

    def reel_in(self):
        delay = random.uniform(*self.config['reaction_delay'])
        time.sleep(delay)
        
        keyboard.press(self.config['reel_key'])
        time.sleep(random.uniform(0.3, 0.7))
        keyboard.release(self.config['reel_key'])
        
        self.fish_status = "waiting"
        print("Рыба поймана!")
        time.sleep(3)  # Пауза между попытками

    def run(self):
        frame_time = 1 / self.config['fps']
        
        while True:
            start_time = time.time()
            
            if not self.running:
                time.sleep(0.1)
                continue
                
            try:
                if self.fish_status == "waiting" and time.time() - self.last_cast_time > self.cast_delay:
                    if self.cast_line():
                        self.cast_delay = random.uniform(4.0, 8.0)
                
                elif self.fish_status == "fishing" and self.detect_bite():
                    self.fish_status = "reeling"
                    self.reel_in()
                    
                time.sleep(max(0, frame_time - (time.time() - start_time)))
                
            except Exception as e:
                print(f"Ошибка: {str(e)}")
                time.sleep(1)
                continue

if __name__ == "__main__":
    try:
        bot = FishingBot()
        bot.run()
    except KeyboardInterrupt:
        print("Бот остановлен пользователем")
    except Exception as e:
        print(f"Критическая ошибка: {str(e)}")
