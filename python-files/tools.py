import cv2
import pyautogui
import keyboard
import threading
import time
from tkinter import Tk, Button, filedialog

# List រក្សារូបភាព gun
gun_images = [Capture.JPG]

# Function add phone gun
def add_gun():
    file_path = filedialog.askopenfilename(title="Select Gun Image", filetypes=[("Image files", "*.png;*.jpg;*.jpeg")])
    if file_path:
        gun_images.append(cv2.imread(file_path))
        print(f"Added gun image: {file_path}")

# Function detect gun on screen
def detect_gun():
    screenshot = pyautogui.screenshot()
    screen = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
    for gun in gun_images:
        res = cv2.matchTemplate(screen, gun, cv2.TM_CCOEFF_NORMED)
        loc = cv2.minMaxLoc(res)
        if loc[1] > 0.8:  # threshold 0.8
            return True
    return False

# Function for auto-click Q twice when left mouse clicked
def auto_click_q():
    while True:
        if keyboard.is_pressed('u'):  # enable tool
            print("Tools Enabled")
            tool_enabled = True
            while tool_enabled:
                if keyboard.is_pressed('i'):  # disable tool
                    print("Tools Disabled")
                    break
                if pyautogui.mouseDown(button='left') and detect_gun():
                    pyautogui.press('q')
                    time.sleep(0.1)
                    pyautogui.press('q')
                time.sleep(0.05)
        time.sleep(0.1)

# Create UI
root = Tk()
root.title("Gun Tool")
Button(root, text="Add Phone Gun", command=add_gun).pack(pady=10)

# Start auto-click thread
threading.Thread(target=auto_click_q, daemon=True).start()

root.mainloop()