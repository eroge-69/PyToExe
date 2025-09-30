import ctypes
import webbrowser
import time
# Display a pop-up alert
response = ctypes.windll.user32.MessageBoxW(0, "Brace for impact twin", "", 0x0050)
if response == 1:
    webbrowser.open("https://www.youtube.com/watch?v=dQw4w9WgXcQ")