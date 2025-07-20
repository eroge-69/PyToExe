import threading
import time
import pyautogui
from PIL import ImageGrab
import dearpygui.dearpygui as dpg

# Settings
settings = {
    "HoldKey": "xbutton2",  # Mouse button
    "ToggleKey": "q",
    "FireMode": "Toggle",   # or "Hold"
    "ClickDelay": 15,       # ms
    "PixelSensitivity": 30, # color threshold
}

pixel_box = 2
pixel_color_range = [(0, 0, 0), (255, 255, 255)]  # black to white
toggle = False
running = True


def pixel_search_and_click():
    w, h = pyautogui.size()
    box = (w//2 - pixel_box, h//2 - pixel_box, w//2 + pixel_box, h//2 + pixel_box)
    screenshot = ImageGrab.grab(box)
    pixels = screenshot.load()

    for x in range(screenshot.width):
        for y in range(screenshot.height):
            r, g, b = pixels[x, y]
            if is_color_in_range((r, g, b)):
                if not pyautogui.mouseDown():
                    pyautogui.click()
                    time.sleep(settings["ClickDelay"] / 1000.0)
                return


def is_color_in_range(color):
    min_c, max_c = pixel_color_range
    return all(min_c[i] <= color[i] <= max_c[i] for i in range(3))


def triggerbot_loop():
    global toggle
    while running:
        if settings["FireMode"] == "Toggle" and toggle:
            pixel_search_and_click()
        elif settings["FireMode"] == "Hold" and pyautogui.mouseDown(button=settings["HoldKey"]):
            pixel_search_and_click()
        time.sleep(0.001)


def toggle_mode():
    global toggle
    toggle = not toggle
    dpg.set_value("status_text", f"Status: {'ON' if toggle else 'OFF'}")


def save_settings():
    settings["ClickDelay"] = dpg.get_value("click_delay")
    settings["PixelSensitivity"] = dpg.get_value("pixel_sensitivity")
    settings["FireMode"] = dpg.get_value("fire_mode")
    print("Settings saved:", settings)


def exit_script():
    global running
    running = False
    dpg.stop_dearpygui()


# Start triggerbot thread
threading.Thread(target=triggerbot_loop, daemon=True).start()


# DearPyGui GUI
dpg.create_context()
dpg.create_viewport(title='Triggerbot', width=400, height=300)
dpg.setup_dearpygui()

with dpg.window(label="Triggerbot", width=380, height=280):
    dpg.add_text("Triggerbot Configuration")
    dpg.add_text("Status: OFF", tag="status_text")
    dpg.add_button(label="Toggle Mode", callback=toggle_mode)
    dpg.add_combo(["Toggle", "Hold"], default_value=settings["FireMode"], label="Fire Mode", tag="fire_mode")
    dpg.add_input_int(label="Click Delay (ms)", default_value=settings["ClickDelay"], tag="click_delay")
    dpg.add_input_int(label="Pixel Sensitivity", default_value=settings["PixelSensitivity"], tag="pixel_sensitivity")
    dpg.add_button(label="Save Settings", callback=save_settings)
    dpg.add_button(label="Exit", callback=exit_script)

dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()

