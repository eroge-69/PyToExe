import cv2
import numpy as np
import pyautogui
import keyboard
import time

# Конфигурация
MAGNIFICATION = 4  # Кратность увеличения
REGION_SIZE = 300   # Размер области захвата (пиксели)
WINDOW_SIZE = REGION_SIZE * MAGNIFICATION  # Размер окна лупы
HOTKEY = "1"  # Горячая клавиша
EXIT_KEY = "esc"    # Клавиша выхода

def main():
    print(f"Программа лупы запущена. Используйте:\n"
          f"• {HOTKEY.upper()} - показать/скрыть лупу\n"
          f"• {EXIT_KEY.upper()} - выход из программы")
    
    active = False
    window_name = "Screen Magnifier"
    
    while True:
        if keyboard.is_pressed(EXIT_KEY):
            if active:
                cv2.destroyWindow(window_name)
            print("Выход из программы")
            break
        
        if keyboard.is_pressed(HOTKEY.split()[-1]):  # Проверка последней клавиши комбинации
            if all(keyboard.is_pressed(k) for k in HOTKEY.split() if k != '+'):  # Проверка полной комбинации
                active = not active
                time.sleep(0.3)  # Защита от двойного срабатывания
                
                if active:
                    # Создаем окно
                    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
                    cv2.resizeWindow(window_name, WINDOW_SIZE, WINDOW_SIZE)
                    print("Лупа активирована")
                else:
                    cv2.destroyWindow(window_name)
                    print("Лупа скрыта")
        
        if active:
            # Получаем размеры экрана
            screen_w, screen_h = pyautogui.size()
            
            # Рассчитываем область захвата (центр экрана)
            x_center, y_center = screen_w // 2, screen_h // 2
            x1 = max(0, x_center - REGION_SIZE // 2)
            y1 = max(0, y_center - REGION_SIZE // 2)
            x2 = min(screen_w, x_center + REGION_SIZE // 2)
            y2 = min(screen_h, y_center + REGION_SIZE // 2)
            
            # Захватываем область экрана
            screenshot = pyautogui.screenshot(region=(x1, y1, x2 - x1, y2 - y1))
            frame = np.array(screenshot)
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            
            # Увеличиваем изображение
            magnified = cv2.resize(
                frame, 
                (WINDOW_SIZE, WINDOW_SIZE), 
                interpolation=cv2.INTER_LINEAR
            )
            
            # Отображаем результат
            cv2.imshow(window_name, magnified)
            cv2.waitKey(1)
        
        time.sleep(0.01)

if __name__ == "__main__":
    main()