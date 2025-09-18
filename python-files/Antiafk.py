import time
import threading
import logging
from pynput.keyboard import Controller

# ---------------------
# Setup Console Logging Only
# ---------------------
logger = logging.getLogger("KeyAutomationConsoleLogger")
logger.setLevel(logging.DEBUG)

console_handler = logging.StreamHandler()
console_formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
console_handler.setFormatter(console_formatter)

logger.handlers.clear()  # Clear any default handlers
logger.addHandler(console_handler)

# ---------------------
# Keyboard Automation
# ---------------------
keyboard = Controller()

def press_key(key, duration=2):
    """Press and hold a key for a specified duration."""
    logger.debug(f"Pressing '{key}' for {duration} seconds.")
    keyboard.press(key)
    time.sleep(duration)
    keyboard.release(key)
    logger.debug(f"Released '{key}'.")

def wasd_cycle():
    """Wait 5 seconds, then run WASD cycle every 2 seconds per key, with 2 min delay between loops."""
    logger.info("Delaying WASD cycle start by 5 seconds...")
    time.sleep(5)

    while True:
        logger.info("Starting WASD cycle.")
        for key in ['w', 'a', 's', 'd']:
            press_key(key, 2)
        logger.info("WASD cycle complete. Waiting 2 minutes before next cycle.")
        time.sleep(120)

def key34_cycle():
    """Wait 10 minutes, then press 3 and 4 every 10 minutes with a 15s gap between."""
    logger.info("Delaying 3/4 cycle start by 10 minutes...")
    time.sleep(600)  # Initial 10-minute delay
    logger.info("Starting 3/4 key cycle loop.")
    while True:
        press_key('3', 0.1)
        logger.info("Pressed '3'. Waiting 15 seconds...")
        time.sleep(15)
        press_key('4', 0.1)
        logger.info("Pressed '4'. Waiting 9 minutes 45 seconds until next cycle...")
        time.sleep(585)

# ---------------------
# Run Threads
# ---------------------
if __name__ == "__main__":
    logger.info("Starting key automation script...")

    t1 = threading.Thread(target=wasd_cycle, daemon=True)
    t2 = threading.Thread(target=key34_cycle, daemon=True)

    t1.start()
    t2.start()

    logger.info("Both automation threads started. Script running...")

    # Keep the main thread alive
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.warning("Script terminated by user.")
