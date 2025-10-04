import pyautogui
import pygetwindow as gw
import keyboard
import time
import threading
import tkinter as tk

# Target color in RGB (FF69B4 hot pink)
TARGET_COLOR = (255, 105, 180)
running = False  # toggle state
overlay_label = None

def get_minecraft_region():
    """Finds Minecraft window and returns (left, top, width, height)."""
    try:
        window = gw.getWindowsWithTitle("Minecraft")[0]
        if window.isMinimized:
            return None
        return (window.left, window.top, window.width, window.height)
    except IndexError:
        return None

def find_color_in_region(region, target_color):
    """Search for the target color inside a given region."""
    screenshot = pyautogui.screenshot(region=region)
    width, height = screenshot.size

    # sample every 3 pixels for speed
    for x in range(0, width, 3):
        for y in range(0, height, 3):
            if screenshot.getpixel((x, y)) == target_color:
                return region[0] + x, region[1] + y
    return None

def toggle():
    """Toggle the script on/off."""
    global running
    running = not running
    update_overlay("ON ✅" if running else "OFF ❌")

def update_overlay(text):
    """Update overlay label text."""
    global overlay_label
    if overlay_label:
        overlay_label.config(text=f"AutoClicker: {text}")

def overlay_window():
    """Creates an always-on-top overlay window."""
    root = tk.Tk()
    root.overrideredirect(True)  # remove borders
    root.attributes("-topmost", True)
    root.attributes("-alpha", 0.7)  # transparency

    global overlay_label
    overlay_label = tk.Label(root, text="AutoClicker: OFF ❌",
                             font=("Arial", 16, "bold"),
                             fg="red", bg="black")
    overlay_label.pack()

    # Position overlay in top-left corner
    root.geometry("+50+50")

    threading.Thread(target=root.mainloop, daemon=True).start()

def main():
    print("Press F8 to toggle scanning ON/OFF. Press ESC to quit.")
    overlay_window()
    keyboard.add_hotkey("F8", toggle)

    while True:
        if running:
            region = get_minecraft_region()
            if not region:
                time.sleep(1)
                continue

            pos = find_color_in_region(region, TARGET_COLOR)
            if pos:
                print(f"Found color at {pos}, right-clicking...")
                pyautogui.rightClick(pos)
                time.sleep(0.5)
        else:
            time.sleep(0.1)

        if keyboard.is_pressed("esc"):
            print("Exiting program.")
            break

if __name__ == "__main__":
    main()
