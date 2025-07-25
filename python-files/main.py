import streamdeck
from pynput.keyboard import Controller, Key
import time

# Initialize keyboard controller
keyboard = Controller()

# --- User Configuration ---
# You'll need to find your Stream Deck device.
# If you have multiple Stream Decks, you might need to iterate through them.
# For simplicity, we'll assume the first found device.
DEVICE_INDEX = 0

# The index of the button you want to use as a trigger (0-indexed)
TRIGGER_BUTTON_INDEX = 0  # Example: Top-left button

# The keys to press after the trigger is activated
KEYS_TO_PRESS = ['x', '1', '2', '3', '4', '5', '6']

# --- Helper Functions ---

def press_keys_sequence(keys):
    """
    Presses a sequence of keys with a small delay between each.
    """
    print(f"Pressing keys: {keys}")
    for key in keys:
        if len(key) == 1: # Regular character
            keyboard.press(key)
            keyboard.release(key)
        else: # Special key (e.g., Key.enter) - not directly used in this example but good practice
            keyboard.press(getattr(Key, key))
            keyboard.release(getattr(Key, key))
        time.sleep(0.1)  # Small delay between key presses

# --- Main Application Logic ---

def run_streamdeck_application():
    decks = streamdeck.DeviceManager().enumerate()

    if not decks:
        print("No Stream Deck devices found.")
        return

    deck = decks[DEVICE_INDEX]
    print(f"Found Stream Deck: {deck.id()} (Product: {deck.product_name()})")

    deck.open()
    deck.reset()

    print(f"Listening for presses on button {TRIGGER_BUTTON_INDEX}...")

    @deck.set_key_callback(TRIGGER_BUTTON_INDEX)
    def key_callback(deck, key, state):
        """
        Callback function for when a Stream Deck button is pressed or released.
        """
        if state:  # Button is pressed
            print(f"Button {key} pressed. Triggering key sequence...")
            press_keys_sequence(KEYS_TO_PRESS)
        else:  # Button is released
            print(f"Button {key} released.")

    # Keep the application running to listen for events
    try:
        # A simple loop to keep the script alive. The callback handles events.
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Application stopped by user.")
    finally:
        deck.close()
        print("Stream Deck closed.")

if __name__ == "__main__":
    run_streamdeck_application()