# This script remaps mouse buttons to keyboard shortcuts for Windows virtual desktops.
# It is designed to be lightweight and run in the background.
#
# The Windows operating system uses a specific shortcut to switch desktops, which
# requires the Ctrl and Windows keys to be pressed together with an arrow key.
# This script simulates that exact key combination.
#
# Prerequisites:
# 1. Install Python from python.org
# 2. Install the pynput library: pip install pynput

from pynput.mouse import Listener as MouseListener
from pynput.keyboard import Controller, Key

def on_click(x, y, button, pressed):
    """
    This function is called every time a mouse button is clicked.
    It checks if the specific button is pressed and performs the remapping.
    """
    
    # We create a single instance of the keyboard controller.
    keyboard_controller = Controller()

    # 'Button.x1' and 'Button.x2' are typically the side buttons on a gaming mouse.
    
    # Check if the desired button is pressed down
    if button == button.x1 and pressed:
        print("Side button 1 pressed. Simulating previous desktop shortcut...")
        # To switch to the previous desktop, we must send Ctrl + Windows + Left Arrow.
        # 'Key.cmd' represents the Windows key in pynput.
        with keyboard_controller.pressed(Key.ctrl, Key.cmd):
            keyboard_controller.press(Key.left)
            keyboard_controller.release(Key.left)
        
    elif button == button.x2 and pressed:
        print("Side button 2 pressed. Simulating next desktop shortcut...")
        # To switch to the next desktop, we must send Ctrl + Windows + Right Arrow.
        with keyboard_controller.pressed(Key.ctrl, Key.cmd):
            keyboard_controller.press(Key.right)
            keyboard_controller.release(Key.right)
            
    # To stop the listener, close the console window.

def start_remapper():
    """Starts the mouse listener."""
    print("Starting mouse remapper. To stop, close the console window.")
    with MouseListener(on_click=on_click) as listener:
        # This line keeps the script running until the listener is stopped.
        listener.join()

if __name__ == "__main__":
    start_remapper()
