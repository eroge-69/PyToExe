import keyboard
import pyautogui
import time

# Define text expansions
expansions = {
    "sg": "signin/google"
}

buffer = ""

def on_key(e):
    global buffer
    if e.event_type == "down":
        if e.name == "space":
            if buffer in expansions:
                # Erase the trigger word
                for _ in range(len(buffer)):
                    pyautogui.press('backspace')
                # Type replacement
                pyautogui.write(expansions[buffer])
            buffer = ""
        elif len(e.name) == 1:  # normal character
            buffer += e.name
        else:
            buffer = ""

keyboard.hook(on_key)
keyboard.wait()