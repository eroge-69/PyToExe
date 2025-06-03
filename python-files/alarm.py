import time
import pyautogui
import playsound
import keyboard

IDLE_TIME = 15  # წამები, რომლის შემდეგაც ჩაირთვება ხმა

def check_activity():
    last_x, last_y = pyautogui.position()
    last_time = time.time()

    while True:
        time.sleep(1)
        new_x, new_y = pyautogui.position()
        
        # თუ მაუსი ან კლავიატურა არ გამოიყენება
        if new_x == last_x and new_y == last_y and not keyboard.is_pressed():
            if time.time() - last_time >= IDLE_TIME:
                try:
                    playsound.playsound("alarm.mp3")  # ხმოვანი გაფრთხილება
                except:
                    print("‼️ **გაფრთხილება: გაიღვიძე!**")  # ტექსტური გაფრთხილება
                last_time = time.time()
        else:
            last_time = time.time()

        last_x, last_y = new_x, new_y

check_activity()
