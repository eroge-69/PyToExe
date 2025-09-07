import pyautogui
import keyboard
import time
time.sleep(3)
check_interval = 10
def smart_click(location):
    x, y = location
    pyautogui.moveTo(x - 5, y, duration=0.1)
    pyautogui.moveTo(x, y, duration=0.1)
    pyautogui.click()
while True:
    # ��������� ������ "����� � ����"
    try:
        exit_location = pyautogui.locateCenterOnScreen("exit_to_menu.png", confidence=0.7)
        if exit_location:
            smart_click(exit_location)
            time.sleep(600)
    except pyautogui.ImageNotFoundException:
        pass  # ������ ��� �� ���������, ����������

    # ��������� ������ "������ ����"
    try:
        start_location = pyautogui.locateCenterOnScreen("start_button.png", confidence=0.7)
        if start_location:
            pyautogui.click(start_location)
            time.sleep(2)
            pyautogui.click(start_location)
            pyautogui.click(start_location)
            time.sleep(30)
            keyboard.press('w')
            time.sleep(0.4)
            keyboard.release('w')

            keyboard.press('shift')
            time.sleep(1)
            keyboard.release('shift')


                

    except pyautogui.ImageNotFoundException:
        pass  # ������ ��� �� ���������, ���

    time.sleep(check_interval)
