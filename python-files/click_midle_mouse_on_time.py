from pynput.mouse import Button, Controller
import time

# Создаем объект контроллера мыши
mouse = Controller()

def click_and_hold(button=Button.middle, duration=1):
    """
    Нажатие и удерживание заданной кнопки мыши,
    с последующим отпуском спустя указанное количество секунд.
    
    :param button: Кнопка мыши (например, Button.left, Button.right, Button.middle)
    :param duration: Время удерживания кнопки в секундах
    """
    # Нажимаем среднюю кнопку мыши
    mouse.press(button)
    print(f'Нажата {button.name}')
    
    # Удерживаем кнопку указанное время
    time.sleep(duration)
    
    # Отпускаем кнопку
    mouse.release(button)
    print(f'{button.name} отпущена')

if __name__ == "__main__":
    try:
        while True:
            # Запрашиваем у пользователя длительность удержания
            input_duration = float(input("Введите время удержания средней кнопки (секунды): "))
            
            if input_duration <= 0:
                break
                
            # Выполняем клик и удержание
            click_and_hold(Button.middle, input_duration)
        
    except KeyboardInterrupt:
        pass