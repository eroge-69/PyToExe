import pyautogui
import time
import keyboard
import pyperclip  # для работы с русским текстом

class AutoSpammer:
    def init(self):  # исправлено: init -> init
        self.words = []
        self.delay = 1.0  # задержка 1 секунда между словами
        self.running = False
        
    def load_text(self, text):
        """Загружает и анализирует текст"""
        self.words = text.split()
        print(f"Загружено {len(self.words)} слов")
        print("Слова:", self.words)
        
    def start_spamming(self):
        """Начинает автоматическую отправку слов"""
        if not self.words:
            print("Сначала загрузите текст!")
            return
            
        self.running = True
        print(f"Начинаю отправку слов с задержкой {self.delay} сек...")
        print("Нажмите E для остановки")
        
        for word in self.words:
            if not self.running:
                break
                
            # Используем буфер обмена для русских символов
            pyperclip.copy(word)  # копируем слово в буфер
            pyautogui.hotkey('ctrl', 'v')  # вставляем
            pyautogui.press('enter')  # отправляем
            
            print(f"Отправлено: '{word}'")
            time.sleep(self.delay)
            
        self.running = False
        print("Все слова отправлены!")
        
    def stop_spamming(self):
        """Останавливает отправку"""
        self.running = False
        print("Остановлено!")
        
    def run(self):
        """Основная программа"""
        print("=== АВТОМАТИЧЕСКИЙ СПАМЕР ===")
        print("Загрузите текст -> нажмите Q -> слова отправляются автоматически")
        print("Задержка между словами: 1 секунда")
        
        text = input("Введите текст: ")
        self.load_text(text)
        
        # Настройка задержки
        delay_input = input("Задержка между словами (сек) [1]: ")
        if delay_input:
            self.delay = float(delay_input)
        
        print("Готово! Перейдите в нужное окно (чат, мессенджер)")
        print("Нажмите Q для старта, E для остановки, ESC для выхода")
        
        while True:
            if keyboard.is_pressed('q'):
                time.sleep(0.5)
                self.start_spamming()
                
            if keyboard.is_pressed('e'):
                self.stop_spamming()
                
            if keyboard.is_pressed('esc'):
                print("Выход...")
                break
                
            time.sleep(0.1)

# Установите: pip install pyautogui keyboard pyperclip
if __name__ == "__main__":
    spammer = AutoSpammer()
    spammer.run()