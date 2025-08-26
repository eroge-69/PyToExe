import os
import time
import ctypes
import win32api
import win32gui
import win32con
import random
import subprocess
import sys

# Define some colors
COLORS = [
    (255, 0, 0),    # Red
    (0, 255, 0),    # Green
    (0, 0, 255),    # Blue
    (255, 255, 0),  # Yellow
    (255, 0, 255),  # Magenta
    (0, 255, 255)   # Cyan
]

# Create a random pattern of glowing dots
def create_random_pattern(hdc, width, height):
    for _ in range(100):  # Number of dots
        x = random.randint(0, width)
        y = random.randint(0, height)
        color = random.choice(COLORS)
        win32gui.SetPixel(hdc, x, y, win32api.RGB(*color))

# Function to display the message on a black screen
def display_message(hdc, width, height, message):
    font = win32gui.CreateFont(
        -24, 0, 0, 0, 400, 0, 0, 0, 0, 0, 0, 0, 0, "Arial"
    )
    old_font = win32gui.SelectObject(hdc, font)
    win32gui.SetBkMode(hdc, win32con.TRANSPARENT)
    win32gui.SetTextColor(hdc, win32api.RGB(255, 255, 255))

    win32gui.TextOut(hdc, width // 4, height // 2, message, len(message))
    win32gui.SelectObject(hdc, old_font)
    win32gui.DeleteObject(font)

# Function to reboot the computer
def reboot_computer():
    ctypes.windll.kernel32.SetConsoleCtrlHandler(None, 1)
    os.system("shutdown /r /t 1")

# Function to simulate a 16-bit BIOS-like interface
def simulate_bios_interface(hdc, width, height):
    font = win32gui.CreateFont(
        -18, 0, 0, 0, 400, 0, 0, 0, 0, 0, 0, 0, 0, "Courier New"
    )
    old_font = win32gui.SelectObject(hdc, font)
    win32gui.SetBkMode(hdc, win32con.TRANSPARENT)
    win32gui.SetTextColor(hdc, win32api.RGB(0, 255, 0))

    bios_message = (
        "BIOS v1.00\n"
        "Copyright (C) 2025 Our Trojan\n"
        "Press F1 to continue, F2 for setup\n"
        "F3 for boot menu, F4 for BIOS setup\n"
        "F5 for system information, F6 for exit\n"
        "F7 for memory test, F8 for hardware test\n"
        "F9 for network test, F10 for storage test\n"
        "F11 for graphics test, F12 for audio test\n"
    )

    win32gui.TextOut(hdc, 10, 10, bios_message, len(bios_message))
    win32gui.SelectObject(hdc, old_font)
    win32gui.DeleteObject(font)

# Function to display warnings
def display_warnings():
    warnings = [
        "This application is a virus. Are you sure you want to launch it? (yes/no)",
        "You are absolutely sure you want to launch this? Your system will never return to normal. This is not a joke. (yes/no)",
        "Launch only on a virtual machine at your own risk. If you are on a real computer, I advise you to stop. (yes/no)"
    ]

    for warning in warnings:
        print(warning)
        choice = input().strip().lower()
        if choice != 'yes':
            sys.exit(0)

# Function to launch the custom OS
def launch_custom_os():
    # Get the device context of the screen
    hdc = win32gui.GetDC(0)

    # Get the screen dimensions
    width = win32api.GetSystemMetrics(win32con.SM_CXSCREEN)
    height = win32api.GetSystemMetrics(win32con.SM_CYSCREEN)

    try:
        start_time = time.time()
        while time.time() - start_time < 300:  # 5 minutes
            # Clear the screen with black color
            win32gui.PatBlt(hdc, 0, 0, width, height, win32con.PATCOPY, win32api.RGB(0, 0, 0))

            # Create a new random pattern
            create_random_pattern(hdc, width, height)

            # Update the display
            win32gui.UpdateWindow(win32gui.GetDesktopWindow())

            # Wait for a short period before creating a new pattern
            time.sleep(0.1)
    finally:
        # Release the device context
        win32gui.ReleaseDC(0, hdc)

    # Display the message on a black screen
    hdc = win32gui.GetDC(0)
    win32gui.PatBlt(hdc, 0, 0, width, height, win32con.PATCOPY, win32api.RGB(0, 0, 0))
    display_message(hdc, width, height, "Your computer is shaken by our Trojan\nAnd your computer died Because of this,\nwe have good news for you, enjoy your new computer.\n[press any key to confirm]")
    win32gui.UpdateWindow(win32gui.GetDesktopWindow())

    # Wait for a key press
    input()

    # Simulate a 16-bit BIOS-like interface
    hdc = win32gui.GetDC(0)
    win32gui.PatBlt(hdc, 0, 0, width, height, win32con.PATCOPY, win32api.RGB(0, 0, 0))
    simulate_bios_interface(hdc, width, height)
    win32gui.UpdateWindow(win32gui.GetDesktopWindow())

    # Wait for a key press to confirm
    input()

    # Reboot the computer
    reboot_computer()

# Function to launch the text-based browser
def launch_text_browser():
    subprocess.run(["lynx", "http://www.example.com"])

# Main function to coordinate the virus launch
def main():
    display_warnings()
    launch_custom_os()
    launch_text_browser()

if __name__ == "__main__":
    main()
