import pyautogui
import time
import keyboard 
import random

paused = False
print("press ' to pause")

while True:
    if keyboard.is_pressed("'"):
        paused = not paused
        state = "paused" if paused else "resumed"
        print(f"program {state}")
        time.sleep(0.5)

    if paused:
        time.sleep(0.1)
        continue

    if pyautogui.pixel(961, 525) == (255, 25, 25):
        print("mob detected, clicking in 1 sec")
        time.sleep(1)
        pyautogui.click()

        seconds1to10 = random.randint(1, 10)
        print(f"waiting {seconds1to10} seconds")
        elapsed = 0

        while elapsed < seconds1to10:
            if keyboard.is_pressed("'"):
                paused = not paused
                state = "paused" if paused else "resumed"
                print(f"program {state}")
                time.sleep(0.5)

            if paused:
                time.sleep(0.1)
                continue

            time.sleep(0.1)
            elapsed += 0.1

            if int(elapsed) != int(elapsed - 0.1):
                print(int(elapsed))

    else:
        print("no mob detected")
        time.sleep(0.5)

# sequence of random movmements:
# commented cause it looks like a bot

"""    if random.random() < 0.25:
        hold_time = random.uniform(0.1, 1.75)  # float seconds between 1 and 2
        print(f"holding 'A' for {hold_time:.2f} seconds")
        keyboard.press('a')
        time.sleep(hold_time)
        keyboard.release('a')

        print(f"holding 'D' for {hold_time:.2f} seconds")
        keyboard.press('d')
        time.sleep(hold_time)
        keyboard.release('d')

    elif random.random() > 0.25:
        hold_time = random.uniform(0.1, 1.75)  # float seconds between 1 and 2
        print(f"holding 'D' for {hold_time:.2f} seconds")
        keyboard.press('d')
        time.sleep(hold_time)
        keyboard.release('d')

        print(f"holding 'a' for {hold_time:.2f} seconds")
        keyboard.press('a')
        time.sleep(hold_time)
        keyboard.release('a')

    elif random.random() > 0.25:
        hold_time = random.uniform(0.1, 0.5)  # float seconds between 1 and 2
        print(f"holding 'a' and 'w'for {hold_time:.2f} seconds")
        keyboard.press('a')
        keyboard.press('w')
        time.sleep(hold_time)
        keyboard.release('a')
        keyboard.release('w')

        print(f"holding 's' and 'd'for {hold_time:.2f} seconds")
        keyboard.press('s')
        keyboard.press('d')
        time.sleep(hold_time)
        keyboard.release('s')
        keyboard.release('d')

    else:
        hold_time = random.uniform(0.1, 0.5)  # float seconds between 1 and 2
        print(f"holding 'w' for {hold_time:.2f} seconds")
        keyboard.press('w')
        time.sleep(hold_time)
        keyboard.release('w')

        print(f"holding 'a' for {hold_time:.2f} seconds")
        keyboard.press('s')
        time.sleep(hold_time)
        keyboard.release('s')"""
    
