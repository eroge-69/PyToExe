import time
import keyboard
import pyautogui

# Настройки
space_interval = 5  # Интервал между нажатиями пробела (в секундах)
mouse_delay = 1     # Задержка после пробела перед кликом мыши (в секундах)

def main():
    print("Кликер запущен. Для остановки нажмите 'Q'")
    
    while True:
        # Проверка остановки по клавише Q
        if keyboard.is_pressed('q'):
            print("Остановка кликера...")
            break
        
        # Нажатие пробела
        keyboard.press_and_release('space')
        print("Нажат пробел")
        time.sleep(mouse_delay)
        
        # Клик левой кнопкой мыши
        pyautogui.click()
        print("Клик мыши")
        time.sleep(space_interval - mouse_delay)

if __name__ == "__main__":
    main()
