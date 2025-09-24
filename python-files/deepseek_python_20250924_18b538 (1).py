import pyautogui
import time
import sys

def show_menu():
    print("\n=== Автокликер ===")
    print("1 - Нажать Enter")
    print("2 - Нажать Пробел") 
    print("3 - Написать текст")
    print("4 - Автоклик Пробелом")
    print("5 - Комбинация клавиш")
    print("0 - Выход")
    return input("Выберите действие: ")

def main():
    pyautogui.FAILSAFE = True
    
    while True:
        choice = show_menu()
        
        if choice == '1':
            pyautogui.press('enter')
            print("Нажат Enter")
            
        elif choice == '2':
            pyautogui.press('space')
            print("Нажат Пробел")
            
        elif choice == '3':
            text = input("Введите текст: ")
            print(f"Печатаю: {text}")
            time.sleep(3)  # Пауза чтобы переключиться в нужное окно
            pyautogui.write(text)
            
        elif choice == '4':
            interval = float(input("Интервал в секундах: "))
            duration = float(input("Длительность в секундах: "))
            
            print(f"Автоклик каждые {interval} сек в течение {duration} сек")
            time.sleep(3)
            
            end_time = time.time() + duration
            while time.time() < end_time:
                pyautogui.press('space')
                time.sleep(interval)
                
        elif choice == '5':
            print("Доступные комбинации:")
            print("1 - Ctrl+C (Копировать)")
            print("2 - Ctrl+V (Вставить)")
            print("3 - Alt+Tab (Переключение окон)")
            
            combo = input("Выберите комбинацию: ")
            if combo == '1':
                pyautogui.hotkey('ctrl', 'c')
            elif combo == '2':
                pyautogui.hotkey('ctrl', 'v')
            elif combo == '3':
                pyautogui.hotkey('alt', 'tab')
                
        elif choice == '0':
            print("Выход...")
            break
            
        time.sleep(1)

if __name__ == "__main__":
    main()