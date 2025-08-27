import pyautogui
import time

pyautogui.FAILSAFE = True

def main(interval_seconds=10):
    try:
        while True:
            x, y = pyautogui.position()
            pyautogui.moveRel(8, 0, duration=0.08)
            pyautogui.moveTo(x, y, duration=0.06)
            time.sleep(interval_seconds)
    except pyautogui.FailSafeException:
        print("Зупинено: курсор у верхньому лівому куті (failsafe).")
    except KeyboardInterrupt:
        print("Зупинено: Ctrl+C.")

if __name__ == "__main__":
    main(30)
