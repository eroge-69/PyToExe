import pyautogui
import datetime

# Get the current time for the filename
timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
filename = f"screenshot_{timestamp}.png"

# Take a screenshot and save it to the file
screenshot = pyautogui.screenshot()
screenshot.save(filename)

print(f"✅ Screenshot saved as {filename}")