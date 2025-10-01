import keyboard
import time
import threading
from collections import defaultdict

class RapidFire:
    def __init__(self):
        self.active = False
        self.rapid_keys = {'q', 'e', 'r', 'f'}
        self.pressed_keys = defaultdict(bool)
        self.num_presses = 5
        self.bind_key = 'f8'
        
        self.show_welcome()
        self.setup_settings()
        self.setup_hotkeys()
        
    def show_welcome(self):
        print("=" * 50)
        print("      ПРОГРАММА ДЛЯ УДУШЕНИЯ НА МИНГЛЕ")
        print("=" * 50)
        print("Эта программа эмулирует умножение нажатия клавиш")
        print("Настройте параметры ниже:")
        print("=" * 50)
    
    def setup_settings(self):
        # Настройка количества нажатий
        while True:
            try:
                presses = input("Введите количество нажатий (1-10): ")
                self.num_presses = int(presses)
                if 1 <= self.num_presses <= 10:
                    break
                else:
                    print("Ошибка: введите число от 1 до 10")
            except ValueError:
                print("Ошибка: введите корректное число")
        
        # Настройка клавиши бинда
        print("\nВыберите клавишу для активации/деактивации:")
        print("Доступные варианты: f1-f12, home, end, insert, delete, page up, page down")
        print("Или введите любую другую клавишу")
        
        while True:
            bind_key = input("Введите клавишу бинда: ").strip().lower()
            if bind_key:
                self.bind_key = bind_key
                break
            else:
                print("Ошибка: введите корректную клавишу")
        
        print("\n" + "=" * 50)
        print("НАСТРОЙКИ ЗАВЕРШЕНЫ!")
        print(f"Количество нажатий: {self.num_presses}")
        print(f"Клавиша активации: {self.bind_key.upper()}")
        print(f"Целевые клавиши: Q, E, R, F")
        print("=" * 50)
        print("\nУправление:")
        print(f"- Нажмите {self.bind_key.upper()} для активации/деактивации")
        print("- Нажмите F12 для выхода")
        print("- Когда режим активен, Q/E/R/F нажимаются многократно")
        print("=" * 50)
    
    def setup_hotkeys(self):
        # Бинд для включения/выключения
        try:
            keyboard.add_hotkey(self.bind_key, self.toggle_mode)
        except Exception as e:
            print(f"Ошибка при настройке клавиши {self.bind_key}: {e}")
            print("Используется клавиша F8 по умолчанию")
            self.bind_key = 'f8'
            keyboard.add_hotkey(self.bind_key, self.toggle_mode)
        
        # Хоткей для выхода (F12)
        keyboard.add_hotkey('f12', self.exit_program)
        
        # Регистрируем обработчики для целевых клавиш
        for key in self.rapid_keys:
            keyboard.on_press_key(key, self.handle_key_press, suppress=True)
    
    def toggle_mode(self):
        self.active = not self.active
        status = "АКТИВИРОВАН" if self.active else "ДЕАКТИВИРОВАН"
        print(f"\n[{status}]")
        print(f"→ Клавиши будут нажиматься {self.num_presses} раз")
    
    def rapid_fire(self, key):
        # Эмулируем нужное количество нажатий
        for i in range(self.num_presses):
            keyboard.press(key)
            keyboard.release(key)
            if i < self.num_presses - 1:  # Не ждем после последнего нажатия
                time.sleep(0)  # интервал между нажатиями
    
    def handle_key_press(self, event):
        if event.name in self.rapid_keys and self.active:
            # Подавляем оригинальное нажатие и запускаем rapid fire
            thread = threading.Thread(target=self.rapid_fire, args=(event.name,))
            thread.daemon = True
            thread.start()
            return False  # подавляем оригинальное нажатие
        return True
    
    def exit_program(self):
        print("\n" + "=" * 50)
        print("Выход из программы...")
        print("Программа создана bluehare")
        print("=" * 50)
        keyboard.unhook_all()
        exit()

def main():
    try:
        print("Запуск программы...")
        rapid_fire = RapidFire()
        print("\nПрограмма успешно запущена и готова к работе!")
        keyboard.wait()  # бесконечный цикл
    except KeyboardInterrupt:
        print("\nПрограмма завершена пользователем")
    except Exception as e:
        print(f"Произошла ошибка: {e}")
        print("Перезапустите программу")
    finally:
        keyboard.unhook_all()

if __name__ == "__main__":
    main()