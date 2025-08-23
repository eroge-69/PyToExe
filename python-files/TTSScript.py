import pyttsx3
import tkinter as tk

def speak_text():
    text = entry.get()
    if text:
        engine = pyttsx3.init()
        voices = engine.getProperty('voices')
        for voice in voices:
            if "en_US" in voice.id and "male" in voice.name.lower():
                engine.setProperty('voice', voice.id)
                break
        engine.setProperty('rate', 150)
        engine.say(text)
        engine.runAndWait()

app = tk.Tk()
app.title("Text to Speech")

label = tk.Label(app, text="Enter text to speak:")
label.pack(pady=5)

entry = tk.Entry(app, width=50)
entry.pack(pady=5)

button = tk.Button(app, text="Speak", command=speak_text)
button.pack(pady=10)

app.mainloop()
