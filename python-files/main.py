import pygetwindow as gw
import pyautogui

def move_windows_to_corner():
    # Получаем все активные окна
    all_windows = gw.getAllWindows()
    
    # Координаты левого верхнего угла экрана
    x = 0
    y = 0
    
    # Перебираем все окна
    for window in all_windows:
        # Проверяем, содержит ли название окна слово "hand"
        if 'hand' in window.title.lower():
            try:
                # Перемещаем окно в левый верхний угол
                window.moveTo(x, y)
                print(f"Окно '{window.title}' перемещено в левый верхний угол")
                
                # Сдвигаем координаты для следующего окна
                x += window.width + 10  # добавляем отступ между окнами
                
                # Если достигли правого края экрана, переходим на следующую строку
                if x + window.width > pyautogui.size().width:
                    x = 0
                    y += window.height + 10  # добавляем отступ между строками
            except Exception as e:
                print(f"Ошибка при работе с окном '{window.title}': {str(e)}")

if __name__ == "__main__":
    move_windows_to_corner()
               

