import os
import ctypes
import sys

def shutdown_windows():
    try:
        # Method 1: Using os.system (simple)
        # os.system("shutdown /s /t 0")
        
        # Method 2: Using ctypes for more control
        if ctypes.windll.shell32.IsUserAnAdmin():
            # If running as admin, use ExitWindowsEx for immediate shutdown
            ctypes.windll.user32.ExitWindowsEx(0x00000008, 0x00000000)
        else:
            # If not admin, use standard shutdown command
            os.system("shutdown /s /t 0")
        
        return True
    except Exception as e:
        print(f"Error occurred: {e}")
        return False

if __name__ == "__main__":
    print("Attempting to shutdown Windows immediately...")
    if shutdown_windows():
        print("Shutdown command sent successfully!")
    else:
        print("Failed to send shutdown command.")
    
    # Small delay to see the message before shutdown (might not always work)
    import time
    time.sleep(2)