import keyboard
import pyautogui
import time
import threading

# Global flag to control the script
is_running = False
script_thread = None

def macro_loop():
    """Main macro function that presses spacebar and right clicks"""
    global is_running
    
    while is_running:
        # Press spacebar
        pyautogui.press('space')
        time.sleep(0.1)  # Small delay between actions
        
        # Right click at current mouse position
        pyautogui.rightClick()
        time.sleep(0.5)  # Delay before next loop iteration (adjust as needed)

def start_macro():
    """Start the macro in a separate thread"""
    global is_running, script_thread
    
    if not is_running:
        is_running = True
        script_thread = threading.Thread(target=macro_loop, daemon=True)
        script_thread.start()
        print("Macro started! Press '0' to pause.")

def stop_macro():
    """Stop the macro"""
    global is_running
    
    if is_running:
        is_running = False
        print("Macro paused! Press 'Del' to start again.")

def main():
    print("Auto Macro Script")
    print("-" * 40)
    print("Press 'Del' to START the macro")
    print("Press '0' to PAUSE the macro")
    print("Press 'Esc' to EXIT the program")
    print("-" * 40)
    
    # Register hotkeys
    keyboard.add_hotkey('delete', start_macro)
    keyboard.add_hotkey('0', stop_macro)
    
    # Keep the program running
    keyboard.wait('esc')
    
    # Cleanup
    global is_running
    is_running = False
    print("\nProgram terminated.")

if __name__ == "__main__":
    main()