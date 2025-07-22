import speech_recognition as sr
import pyttsx3
import datetime
import random
import webbrowser
import os
import subprocess
import pyautogui
import time
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
import re
import threading
import pytesseract
import shutil
import cv2
import numpy as np
from PIL import ImageGrab
from dateutil import parser as dateutil
import pywhatkit

engine = pyttsx3.init()
scrolling = False

def speak(text):
    def _speak():
        engine.say(text)
        engine.runAndWait()
    threading.Thread(target=_speak).start()
    print(f"Jarvis: {text}")


def greet_user():
    hour = datetime.datetime.now().hour
    now = datetime.datetime.now().strftime("%I:%M %p")
    greetings = [
        "Hope you're doing fantastic!",
        "Welcome back, ready to assist you.",
        "Nice to see you again!",
        "Here to help you, anytime."
    ]
    if 0 <= hour < 12:
        greet = "Good Morning!"
    elif 12 <= hour < 18:
        greet = "Good Afternoon!"
    else:
        greet = "Good Evening!"
    speak(f"{greet} It's {now}. {random.choice(greetings)}")

def listen():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        try:
            r.adjust_for_ambient_noise(source, duration=0.1)  # Faster ambient adjustment
            print("Listening...")
            audio = r.listen(source, phrase_time_limit=20)  # Instant capture after user starts
            print("Recognizing...")

            
            command = r.recognize_google(audio).lower()
            
            if command.strip():
                print(f"User: {command}")
                return command
        except sr.WaitTimeoutError:
            return ""
        except sr.UnknownValueError:
            return ""
        except sr.RequestError:
            speak("Could not request results, check internet.")
            return ""
    return ""


def calculate_and_return_result(op, num1, num2):
    try:
        if op == "+":
            result = num1 + num2
        elif op == "-":
            result = num1 - num2
        elif op == "*":
            result = num1 * num2
        elif op == "/":
            result = "undefined" if num2 == 0 else round(num1 / num2, 2)
        else:
            result = "Invalid operation"
        speak(f"The result is {result}")
    except:
        speak("Sorry, I couldn't perform the calculation.")

def scroll_down_continuous():
    global scrolling
    scrolling = True
    speak("Starting to scroll continuously.")
    def scroll():
        while scrolling:
            pyautogui.scroll(-10)
            time.sleep(0.1)
    threading.Thread(target=scroll).start()






def auto_arrange_desktop_icons():

    
    pyautogui.moveTo(1355, 273, duration=0.9)
    
    pyautogui.click(button='right')
    
    pyautogui.press("v")

for _ in range(3):
    pyautogui.press('down')
    pyautogui.press("enter")

    pyautogui.moveTo(1355, 273, duration=0.9)
    pyautogui.click(button='right')
    pyautogui.press("v")


for _ in range(3):
    pyautogui.press('down')
    pyautogui.press("enter")


    
    print("Toggled auto arrange icons on desktop.")



    


def stop_scrolling():
    global scrolling
    scrolling = False
    speak("Stopped scrolling.")



def maximize_tab():
    speak("Maximizing window.")
    pyautogui.hotkey('win', 'up')

def minimize_tab():
    speak("Minimizing window.")
    pyautogui.hotkey('win', 'down')

def close_tab():
    speak("Closing the window.")
    pyautogui.hotkey('alt', 'f4')

def exitfullscreenyt():
    speak("Checking for YouTube full screen...")
    screenshot = ImageGrab.grab()
    img = np.array(screenshot)
    text = pytesseract.image_to_string(img)
    if "subscribe" not in text.lower():
        pyautogui.press("esc")
        speak("Exited full screen.")
    else:
        speak("Already out of full screen.")

def setplaybackspeed2ytinfullmode():
    speak("Setting playback speed to 2x.")
    pyautogui.press("k")
    pyautogui.press("shift+>")
    pyautogui.press("shift+>")

def setplaybackspeednormalytinfullmode():
    speak("Setting playback speed to normal.")
    pyautogui.press("shift+<")
    pyautogui.press("shift+<")

def closeallwindows():
    speak("Closing all windows.")
    for _ in range(10):
        pyautogui.hotkey('alt', 'f4')
        time.sleep(0.5)

def closethiswindow():
    speak("Sure sir, closing this window")

def respond(command):
    if "time" in command:
        speak(datetime.datetime.now().strftime("%I:%M %p"))

    elif "date" in command:
        speak(datetime.date.today().strftime("%B %d, %Y"))

    


    elif "open youtube in command" in command:
        webbrowser.open("https://www.youtube.com")

    elif "open google" in command:
        webbrowser.open("https://www.google.com")

    elif "open notepad" in command:
        os.startfile("notepad.exe")

    elif "open whatsapp" in command:
        subprocess.run(["start", "whatsapp:"], shell=True)

    elif "search" in command and "on youtube" in command:
        query = command.replace("search", "").replace("on youtube", "").strip().replace(" ", "+")
        webbrowser.open(f"https://www.youtube.com/results?search_query={query}")
        speak(f"Searching YouTube for {query}")

    elif "search" in command and "google" in command:
        query = command.replace("search", "").replace("on google", "").strip().replace(" ", "+")
        webbrowser.open(f"https://www.google.com/search?q={query}")
        speak(f"Searching Google for {query}")

    elif "send a message" in command:
        speak("What message do you want to send?")
        msg = listen()
        speak("To whom?")
        recipient = listen()
        speak(f"Pretending to send '{msg}' to {recipient}' (actual sending not yet implemented).")

    elif "i want to send a message" in command:
        speak("What message do you want to send?")
        whatmsg = listen()
        speak("And to whom are you sending?")
        sendper = listen()

        pywhatkit.sendwhatmsg(f'{sendper}', f'{whatmsg}')
    elif "schedule" in command and "message" in command:
        speak("What message do you want to send?")
        msg = listen()
        speak("To whom? tell the number")
        recipient = listen()
        pywhatkit.sendwhatmsg(f'+91{recipient}', )


    elif "search for" and "in my computer" in command:

        query = command.replace("search for", "").replace

        pyautogui.press("win")
        pyautogui.typewrite("File Explorer")
        pyautogui.press("enter")
        pyautogui.moveTo(55,555, duration=0.01)
        pyautogui.click()
        pyautogui.moveTo(1212,156, duration=0.01)
        pyautogui.click()
        pyautogui.typewrite

    elif "subscribe this channel" in command:
        speak("Searching for Subscribe button...")
        button_location = pyautogui.locateOnScreen("subscribe_button.png", confidence=0.7)
    
        if button_location:
            speak("Found Subscribe button, clicking it now.")
            
            center = pyautogui.center(button_location)
            pyautogui.moveTo(center.x, center.y)
            pyautogui.click()
            time.sleep(1)
        
            speak("Subscribed.")
        else:
            pyautogui.press("esc")

            if button_location:
                speak("Found Subscribe button, clicking it now.")
            
                center = pyautogui.center(button_location)
                pyautogui.moveTo(center.x, center.y)
                pyautogui.click()
                time.sleep(1)
        
                speak("Subscribed.")

    elif "arrange all icons and files" in command:
        auto_arrange_desktop_icons()




    elif "close this window" in command:
        pyautogui.press("esc") #to avoid error as it could be maximzed window for yt

        button_location = pyautogui.locateOnScreen("closewind.PNG", confidence=0.5)
    
        if button_location:
            speak("closing...")
            
            center = pyautogui.center(button_location)
            pyautogui.moveTo(center.x, center.y)
            pyautogui.click()
            time.sleep(1)
        
            speak("closed the window.")
        
        else:
            speak("window not found, try again")

    
    












    elif "close window temporary" in command:

        minimize_tab()


    else:
        speak("I didn't understand that.")

# Initialize bot
greet_user()
def main_loop():
    while True:
        command = listen()
        if command:
            threading.Thread(target=respond, args=(command,)).start()

main_loop()



# Example usage:




