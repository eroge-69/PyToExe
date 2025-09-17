import pyautogui
import pyperclip
import keyboard
import webbrowser

def send_clipboard():
    text = pyperclip.paste().replace("\n","")
    pyautogui.typewrite(text, interval=0)

keyboard.add_hotkey('F5', send_clipboard)

if input("Heslo: ") != "nigga":
    quit()

print("Dej F5 pro paste")
keyboard.wait()
