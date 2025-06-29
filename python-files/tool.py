import webbrowser
import time

timer = 0
while timer < 10:
    time.sleep(1)
    webbrowser.open("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
    timer = timer + 1
    
