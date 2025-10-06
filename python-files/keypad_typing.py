import keyboard
import time

# Define multi-tap mappings
multi_tap = {
    '1': ['.', ',', '?', '!', '1'],
    '2': ['a', 'b', 'c'],
    '3': ['d', 'e', 'f'],
    '4': ['g', 'h', 'i'],
    '5': ['j', 'k', 'l'],
    '6': ['m', 'n', 'o'],
    '7': ['p', 'q', 'r', 's'],
    '8': ['t', 'u', 'v'],
    '9': ['w', 'x', 'y', 'z'],
    '0': [' ']
}

# Variables to track timing and tap cycles
last_key = None
last_time = 0
tap_index = 0
hold_threshold = 0.8  # seconds

def on_key(event):
    global last_key, last_time, tap_index

    if event.event_type == 'down' and event.name in multi_tap:
        key = event.name
        press_time = time.time()
        press_start = press_time

        # Wait until key is released to measure hold time
        keyboard.wait(event.name + ' up')
        hold_time = time.time() - press_start

        # Long press → print number
        if hold_time > hold_threshold:
            keyboard.write(key)
            last_key = None
            return

        # Check if same key pressed quickly again
        if last_key == key and (press_time - last_time) < 1.0:
            tap_index = (tap_index + 1) % len(multi_tap[key])
        else:
            tap_index = 0

        # Output letter
        keyboard.write(multi_tap[key][tap_index])

        # Update last press data
        last_key = key
        last_time = press_time

print("📱 Old keypad typing mode active. Press Ctrl+C to stop.")
keyboard.hook(on_key)
keyboard.wait()
