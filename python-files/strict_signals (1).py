import pyautogui
import pytesseract
import time
from PIL import ImageGrab

# Set the path to tesseract (modify it if your path is different)
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Region to scan for trading signals (x1, y1, x2, y2)
SIGNAL_REGION = (910, 360, 1040, 410)  # Update coordinates for your screen

# Coordinates for HIGHER and LOWER buttons (change these to match your screen)
HIGHER_BUTTON = (1100, 400)
LOWER_BUTTON = (1100, 470)

def capture_signal_text():
    # Capture a portion of the screen
    image = ImageGrab.grab(bbox=SIGNAL_REGION)
    # Use OCR to extract text
    text = pytesseract.image_to_string(image).strip().upper()
    return text

def click_button(signal):
    if "HIGHER" in signal:
        print("Signal detected: HIGHER — clicking HIGHER button.")
        pyautogui.click(HIGHER_BUTTON)
    elif "LOWER" in signal:
        print("Signal detected: LOWER — clicking LOWER button.")
        pyautogui.click(LOWER_BUTTON)
    else:
        print(f"No valid signal detected: '{signal}'")

def main():
    print("Starting auto trading bot. Press Ctrl+C to stop.")
    try:
        while True:
            signal_text = capture_signal_text()
            print("Detected signal:", signal_text)
            click_button(signal_text)
            time.sleep(3)  # Wait before checking again
    except KeyboardInterrupt:
        print("Bot stopped by user.")

if __name__ == "__main__":
    main()

