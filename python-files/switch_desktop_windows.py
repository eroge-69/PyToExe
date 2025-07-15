import pyautogui
from pynput import mouse

def switch_to_desktop(next_desktop):
    """Simulate keypress to switch desktops in Windows."""
    pyautogui.hotkey('ctrl', 'win', 'right' if next_desktop else 'left')

def on_click(x, y, button, pressed):
    """Handle mouse click events."""
    if button == mouse.Button.x1 and pressed:  # Mouse4 is typically x1
        # Toggle between Desktop 1 and Desktop 2
        global current_desktop
        current_desktop = 1 if current_desktop == 0 else 0
        switch_to_desktop(current_desktop == 1)

# Initialize current desktop (start on Desktop 1)
current_desktop = 0

# Set up the mouse listener
with mouse.Listener(on_click=on_click) as listener:
    listener.join()