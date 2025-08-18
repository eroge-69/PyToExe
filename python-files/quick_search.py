import keyboard
import pyperclip
import time
import pyautogui
import pygetwindow as gw

def search_in_chrome():
    # Copy selected text
    pyautogui.hotkey("ctrl", "c")
    time.sleep(0.2)
    text = pyperclip.paste().strip()

    if text:
        # Find Chrome window
        windows = gw.getWindowsWithTitle("Google Chrome")
        if windows:
            chrome = windows[0]
            chrome.activate()  # Bring Chrome to front
            time.sleep(0.3)

            # Focus address bar
            pyautogui.hotkey("ctrl", "l")
            time.sleep(0.1)

            # Type Google search and press Enter
            pyautogui.typewrite("https://www.google.com/search?q=" + text)
            pyautogui.press("enter")
        else:
            print("⚠️ Chrome not found. Please open Chrome first.")
    else:
        print("⚠️ No text selected!")

# Bind to PageDown key
keyboard.add_hotkey("pagedown", search_in_chrome)

print("✅ Running... Select text anywhere and press PageDown to search in Chrome tab.")
keyboard.wait("esc")  # Press ESC to exit
