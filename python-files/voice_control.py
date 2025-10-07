import vosk
import pyaudio
import json
import time
import keyboard
from pynput.mouse import Button, Controller as MouseController
import threading
import os
import sys

class VoiceCommandController:
    def __init__(self):
        self.mouse = MouseController()
        self.model = None
        self.recognition_active = True
        
        # Инициализация модели Vosk
        self.init_vosk_model()
        
    def init_vosk_model(self):
        """Инициализация модели распознавания речи"""
        try:
            if not os.path.exists("model"):
                print("Ошибка: Модель Vosk не найдена!")
                print("Скачайте русскую модель с: https://alphacephei.com/vosk/models")
                print("И распакуйте в папку 'model' в текущей директории")
                sys.exit(1)
                
            self.model = vosk.Model("model")
            print("Модель Vosk загружена успешно")
        except Exception as e:
            print(f"Ошибка загрузки модели: {e}")
            sys.exit(1)
    
    def audio_capture(self):
        """Захват аудио с микрофона"""
        p = pyaudio.PyAudio()
        
        # Настройки аудио
        FORMAT = pyaudio.paInt16
        CHANNELS = 1
        RATE = 16000
        CHUNK = 4096
        
        try:
            stream = p.open(format=FORMAT,
                           channels=CHANNELS,
                           rate=RATE,
                           input=True,
                           frames_per_buffer=CHUNK)
            
            print("Микрофон активирован. Слушаю команды...")
            print("Доступные команды:")
            print("  'вперёд' - нажать W на 1 секунду")
            print("  'назад' - нажать S на 1 секунду") 
            print("  'инвентарь' - нажать E один раз")
            print("  'закрыть' - нажать ESC один раз")
            print("  'удар' - клик левой кнопкой мыши")
            print("  'правый клик' - клик правой кнопкой мыши")
            
            rec = vosk.KaldiRecognizer(self.model, RATE)
            
            while self.recognition_active:
                data = stream.read(CHUNK, exception_on_overflow=False)
                
                if rec.AcceptWaveform(data):
                    result = json.loads(rec.Result())
                    text = result.get('text', '').lower().strip()
                    
                    if text:
                        print(f"Распознано: {text}")
                        self.process_command(text)
                        
        except Exception as e:
            print(f"Ошибка захвата аудио: {e}")
        finally:
            stream.stop_stream()
            stream.close()
            p.terminate()
    
    def process_command(self, text):
        """Обработка полностью распознанных команд"""
        # Расширенный список команд с большим количеством вариантов
        commands = {
            # Команды движения
            "вперёд": lambda: self.hold_key('w', 1.0),
            "вперед": lambda: self.hold_key('w', 1.0),
            "перёд": lambda: self.hold_key('w', 1.0),
            "назад": lambda: self.hold_key('s', 1.0),
            "наза": lambda: self.hold_key('s', 1.0),
            "назва": lambda: self.hold_key('s', 1.0),
            
            # Команда инвентаря
            "инвентарь": lambda: self.press_key('e'),
            "инвентар": lambda: self.press_key('e'),
            "инвента": lambda: self.press_key('e'),
            "инвенто": lambda: self.press_key('e'),
            "инвен": lambda: self.press_key('e'),
            "инве": lambda: self.press_key('e'),
            "инв": lambda: self.press_key('e'),
            
            # Команда закрытия
            "закрыть": lambda: self.press_key('esc'),
            "закрой": lambda: self.press_key('esc'),
            "закры": lambda: self.press_key('esc'),
            "закр": lambda: self.press_key('esc'),
            
            # Команды мыши
            "удар": lambda: self.mouse_click('left'),
            "ударить": lambda: self.mouse_click('left'),
            "бей": lambda: self.mouse_click('left'),
            "ударь": lambda: self.mouse_click('left'),
            "правый клик": lambda: self.mouse_click('right'),
            "правый": lambda: self.mouse_click('right'),
            "правая кнопка": lambda: self.mouse_click('right'),
            "правая": lambda: self.mouse_click('right'),
            "правую": lambda: self.mouse_click('right'),
        }
        
        for command, action in commands.items():
            if command in text:
                print(f"Выполняю команду: {command}")
                # Запускаем в отдельном потоке, чтобы не блокировать распознавание
                threading.Thread(target=action, daemon=True).start()
                break
    
    def hold_key(self, key, duration=1.0):
        """Удерживает клавишу на указанное время с помощью keyboard"""
        try:
            print(f"Нажимаю {key} на {duration} секунд")
            keyboard.press(key)
            time.sleep(duration)
            keyboard.release(key)
            print(f"Отпускаю {key}")
        except Exception as e:
            print(f"Ошибка удержания клавиши {key}: {e}")
    
    def press_key(self, key):
        """Однократное нажатие клавиши с помощью keyboard"""
        try:
            print(f"Нажимаю {key}")
            keyboard.press(key)
            keyboard.release(key)
            print(f"Отпускаю {key}")
        except Exception as e:
            print(f"Ошибка нажатия клавиши {key}: {e}")
    
    def mouse_click(self, button):
        """Клик мыши с помощью pynput"""
        try:
            if button == 'left':
                print("Левый клик мыши")
                self.mouse.click(Button.left)
            elif button == 'right':
                print("Правый клик мыши")
                self.mouse.click(Button.right)
        except Exception as e:
            print(f"Ошибка клика мыши: {e}")
    
    def start(self):
        """Запуск системы распознавания"""
        print("Запуск голосового управления...")
        print("Используется библиотека keyboard для клавиатуры и pynput для мыши")
        print("ВАЖНО: Для работы программы может потребоваться запуск от имени администратора!")
        
        # Запускаем захват аудио в отдельном потоке
        audio_thread = threading.Thread(target=self.audio_capture, daemon=True)
        audio_thread.start()
        
        try:
            # Основной цикл
            while True:
                time.sleep(0.1)
        except KeyboardInterrupt:
            print("\nОстановка программы...")
            self.recognition_active = False

def check_dependencies():
    """Проверка и установка зависимостей"""
    try:
        import vosk
        import pyaudio
        import keyboard
        import pynput
        print("Все зависимости установлены")
        return True
    except ImportError as e:
        print(f"Не установлены зависимости: {e}")
        print("\nУстановите зависимости командой:")
        print("pip install vosk pyaudio keyboard pynput")
        return False

if __name__ == "__main__":
    print("=== Голосовое управление для Minecraft (исправленные клики мыши) ===")
    
    if not check_dependencies():
        sys.exit(1)
    
    # Проверяем наличие модели
    if not os.path.exists("model"):
        print("\nМодель распознавания не найдена!")
        print("1. Скачайте русскую модель с: https://alphacephei.com/vosk/models")
        print("2. Выберите 'vosk-model-small-ru-0.22' или подобную")
        print("3. Распакуйте содержимое в папку 'model' в текущей директории")
        sys.exit(1)
    
    # Запускаем контроллер
    controller = VoiceCommandController()
    controller.start()
