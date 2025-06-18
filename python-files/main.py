import webbrowser
import pyautogui
import time
import pyttsx3

engine = pyttsx3.init()

# First TTS message
engine.say("Opening the file")
engine.runAndWait()

edge_path = "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe"
url1 = "https://hehehe21223ef.pythonanywhere.com/"
url2 = "https://www.youtube.com/watch?v=8Pc0AEbfnBM"

webbrowser.register('edge', None, webbrowser.BackgroundBrowser(edge_path))
webbrowser.get('edge').open_new(url1)

time.sleep(3)  # Wait a bit before starting countdown

# Wait 5 seconds before opening second tab with TTS warning
for i in range(5, 0, -1):
    print(f"Opening next tab in {i} seconds...")
    time.sleep(1)

# Second TTS message 5 seconds before opening second tab
engine.say("get ready to cry..")
engine.runAndWait()

time.sleep(2)  # Pause for 5 seconds after speaking

webbrowser.get('edge').open_new_tab(url2)

time.sleep(2)
pyautogui.hotkey('ctrl', 'w')  # Close the first tab