# === Karen 2.0 Desktop Assistant ===
# ✅ Voice-controlled offline assistant with basic system commands, search, and optional Excel

import os
import pyttsx3
import speech_recognition as sr
import subprocess
import webbrowser
import openpyxl
from gtts import gTTS
import playsound
import tempfile

# === Init ===
recognizer = sr.Recognizer()
engine = pyttsx3.init()
voices = engine.getProperty("voices")
for voice in voices:
    if "female" in voice.name.lower():
        engine.setProperty("voice", voice.id)
        break
engine.setProperty("rate", 175)

excel_file = None
workbook = None
sheet = None

def speak(text, lang="en"):
    print(f"Karen 🗣️: {text}")
    try:
        if lang == "hi":
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
                tts_path = fp.name
            tts = gTTS(text=text, lang="hi")
            tts.save(tts_path)
            playsound.playsound(tts_path)
            os.remove(tts_path)
        else:
            engine.say(text)
            engine.runAndWait()
    except Exception as e:
        print("Voice error:", e)

def listen():
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source)
        speak("Listening...")
        audio = recognizer.listen(source)
    try:
        command = recognizer.recognize_google(audio)
        print("You said:", command)
        return command.lower()
    except:
        speak("Sorry, I didn't catch that.")
        return None

def open_excel(file_name):
    global excel_file, workbook, sheet
    try:
        if not file_name.endswith(".xlsx"):
            file_name += ".xlsx"
        excel_file = os.path.join(os.getcwd(), file_name)
        if not os.path.exists(excel_file):
            workbook = openpyxl.Workbook()
            workbook.save(excel_file)
        workbook = openpyxl.load_workbook(excel_file)
        sheet = workbook.active
        speak(f"Excel file {file_name} is open.")
    except Exception as e:
        speak(f"Failed to open Excel file: {e}")

def read_cell(cell):
    if not sheet:
        speak("Please open an Excel file first.")
        return
    try:
        value = sheet[cell].value
        if value is None:
            speak(f"Cell {cell} is empty.")
        else:
            speak(f"Value in {cell} is {value}")
    except:
        speak("Invalid cell reference.")

def write_cell(cell, value):
    if not sheet:
        speak("Please open an Excel file first.")
        return
    try:
        sheet[cell] = value
        speak(f"Wrote {value} in {cell}")
    except:
        speak("Failed to write to the cell.")

def save_excel():
    if workbook and excel_file:
        workbook.save(excel_file)
        speak("Excel file saved.")
    else:
        speak("No Excel file is open.")

def handle_system_command(cmd):
    if "open chrome" in cmd:
        path = "C:\Program Files\Google\Chrome\Application\chrome.exe"
        speak("Opening Chrome")
        subprocess.Popen([path])
    elif "shutdown" in cmd:
        speak("Shutting down the system.")
        os.system("shutdown /s /t 1")
    elif "open folder" in cmd:
        speak("Which folder?")
        folder = listen()
        if folder:
            folder_path = os.path.join(os.path.expanduser("~"), folder)
            if os.path.exists(folder_path):
                os.startfile(folder_path)
                speak(f"Opened folder {folder}")
            else:
                speak("Folder not found.")
    elif "search for" in cmd or "google" in cmd:
        query = cmd.replace("search for", "").replace("google", "").strip()
        if query:
            speak(f"Searching Google for {query}")
            webbrowser.open(f"https://www.google.com/search?q={query}")
    elif "youtube" in cmd:
        query = cmd.replace("youtube", "").strip()
        if query:
            speak(f"Searching YouTube for {query}")
            webbrowser.open(f"https://www.youtube.com/results?search_query={query}")
    elif "joke" in cmd:
        speak("Why did the computer go to therapy? Because it had too many bytes of emotional baggage.")

def handle_excel_command(cmd):
    if "open excel" in cmd:
        speak("Which file?")
        fname = listen()
        if fname:
            open_excel(fname)
    elif "read cell" in cmd:
        speak("Which cell?")
        cell = listen()
        if cell:
            read_cell(cell.upper())
    elif "write" in cmd and "in" in cmd:
        parts = cmd.split("in")
        if len(parts) == 2:
            value = parts[0].replace("write", "").strip()
            cell = parts[1].strip().upper()
            write_cell(cell, value)
    elif "save file" in cmd or "save excel" in cmd:
        save_excel()

def main():
    speak("Hello Zarrar. I am Karen, your desktop assistant.")
    while True:
        speak("Say a command.")
        cmd = listen()
        if not cmd:
            continue
        if "exit" in cmd or "quit" in cmd:
            speak("Goodbye. See you soon.")
            break
        elif "excel" in cmd or "cell" in cmd or "write" in cmd:
            handle_excel_command(cmd)
        else:
            handle_system_command(cmd)

if __name__ == "__main__":
    main()
