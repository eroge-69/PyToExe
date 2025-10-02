import keyboard
import time
import winsound
import threading

running = False
exit_program = False
start_delay = 0.2  # 200 ms

def play_beep(frequency, duration):
    winsound.Beep(frequency, duration)

def spam_keys():
    global running, exit_program
    keys = ["w", "a"] * 5  # W A W A W A W A W A
    while not exit_program:
        if running:
            for key in keys:
                if not running or exit_program:
                    break
                keyboard.press_and_release(key)
                time.sleep(0.05)  # 50 ms
        else:
            time.sleep(0.1)

def main():
    global running, exit_program
    threading.Thread(target=spam_keys, daemon=True).start()

    while not exit_program:
        if keyboard.is_pressed("f1"):
            running = not running
            if running:
                play_beep(1000, 200)  # high beep when ON
                time.sleep(start_delay)  # wait 200 ms before spamming starts
            else:
                play_beep(500, 200)   # low beep when OFF
            time.sleep(0.3)  # prevent multiple toggles from one press

        if keyboard.is_pressed("f2"):
            play_beep(800, 400)
            exit_program = True
            break

        time.sleep(0.05)

if __name__ == "__main__":
    main()
