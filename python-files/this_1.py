import pyautogui
import time

fishingTime = int(input("Enter in seconds how long should scan last: "))
end_time = time.time() + fishingTime
print(f"Программа будет работать {fishingTime} секунд")

# Переменная для отслеживания состояния
fishing_in_progress = False

while time.time() < end_time:
    try:
        # Ищем изображение на экране
        Location = pyautogui.locateOnScreen('point.png', confidence=0.4, grayscale=True)

        if Location is not None:
            # Если изображение найдено - начинаем быстро кликать
            print("Объект найден! Начинаем вываживание...")
            fishing_in_progress = True

            # Быстро кликаем пока изображение не исчезнет
            while Location is not None:
                point = pyautogui.center(Location)
                clickX, clickY = point
                pyautogui.click(clickX, clickY)
                print("Кликнули по метке")

                # Короткая пауза между кликами
                time.sleep(0.1)

                # Проверяем, не исчезла ли метка
                try:
                    Location = pyautogui.locateOnScreen('point.png', confidence=0.4, grayscale=True)
                except pyautogui.ImageNotFoundException:
                    Location = None
                    print("Метка исчезла - рыба поймана!")

            fishing_in_progress = False
            # Короткая пауза после поимки рыбы
            time.sleep(1)

        else:
            # Если изображения нет и удочка не заброшена - забрасываем
            if not fishing_in_progress:
                print("Забрасываем удочку...")
                pyautogui.click()
                fishing_in_progress = True
                # Ждем пока поплавок утонет и появится метка
                time.sleep(3)
            else:
                # Если удочка заброшена, но метки еще нет - ждем
                print("Ждем поклевки...")
                time.sleep(0.5)

    except pyautogui.ImageNotFoundException:
        # Если изображение не найдено, но удочка не заброшена - забрасываем
        if not fishing_in_progress:
            print("Изображение не найдено. Забрасываем удочку...")
            pyautogui.click()
            fishing_in_progress = True
            time.sleep(3)
        else:
            print("Ждем поклевки...")
            time.sleep(0.5)
    except Exception as e:
        print(f"Произошла ошибка: {e}")
        time.sleep(1)

print("Программа завершила работу")