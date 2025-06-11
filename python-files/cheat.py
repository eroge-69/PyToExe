import keyboard
import pyautogui
import time
import os
import random
import threading
dict_path = r"C:\Users\Nadia\Desktop\Sorry Bub\words.txt"

if not os.path.exists(dict_path):
    print(f"Dictionary not found at: {dict_path}")
    exit()

with open(dict_path, "r", encoding="utf-8") as f:
    words = [line.strip() for line in f if line.strip().isalpha()]

words.sort(key=len, reverse=True)

typed = ""
locked = False
triggered = False
fragment_timer = None
TIMER_DELAY = 0.5
emergency_buffer = []
ready_for_new_input = True

def find_exact_fragment_word(fragment):
    fragment = fragment.lower()
    for word in words:
        if fragment in word.lower():
            return word
    return None

def slow_type(text):
    for char in text:
        pyautogui.typewrite(char)
        time.sleep(random.uniform(0.05, 0.1))

def reset_all():
    global typed, triggered, fragment_timer
    typed = ""
    triggered = False
    if fragment_timer:
        fragment_timer.cancel()
        fragment_timer = None

def trigger_match():
    global locked, triggered, ready_for_new_input, fragment_timer

    if triggered or locked:
        return

    # Immediately block other triggers
    triggered = True

    if fragment_timer:
        fragment_timer.cancel()
        fragment_timer = None

    word = find_exact_fragment_word(typed)
    if word:
        locked = True
        time.sleep(0.05)
        for _ in typed:
            pyautogui.press('backspace')
            time.sleep(random.uniform(0.05, 0.1))
        slow_type(word)
        pyautogui.press('enter')
        time.sleep(0.2)
        ready_for_new_input = False
        locked = False

    reset_all()

def start_timer():
    global fragment_timer
    if fragment_timer:
        fragment_timer.cancel()
    fragment_timer = threading.Timer(TIMER_DELAY, trigger_match)
    fragment_timer.start()

def on_key(e):
    global typed, locked, triggered, emergency_buffer, ready_for_new_input

    if e.event_type != 'down':
        return

    emergency_buffer.append(e.name)
    if len(emergency_buffer) > 5:
        emergency_buffer.pop(0)
    if emergency_buffer[-3:] == ['8', '8', '8']:
        print("Emergency stop activated. Exiting.")
        exit()

    if not ready_for_new_input:
        ready_for_new_input = True
        typed = ""
        return

    if locked or triggered:
        return

    if e.name == 'backspace':
        typed = typed[:-1]
    elif e.name == 'enter':
        reset_all()
    elif len(e.name) == 1 and e.name.isalpha():
        typed += e.name
        if len(typed) == 2:
            start_timer()
        elif len(typed) == 3:
            if fragment_timer:
                fragment_timer.cancel()
                fragment_timer = None
            trigger_match()
    else:
        reset_all()

print("📱 Listening. Type 3 letters or 2 + pause to trigger word replacement.")
print("Press '8' three times to EMERGENCY STOP.")
keyboard.hook(on_key)
keyboard.wait()
