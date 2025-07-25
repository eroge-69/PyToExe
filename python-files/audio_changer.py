import tkinter as tk
from tkinter import messagebox
import speech_recognition as sr
from googletrans import Translator
from gtts import gTTS
import os
from playsound import playsound
import tempfile

# Initialize translator
translator = Translator()

# Function to recognize Chinese speech and translate to Hindi
def translate_chinese_to_hindi():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        status_label.config(text="Listening... Speak in Chinese")
        root.update()
        try:
            audio = recognizer.listen(source, timeout=5)
            status_label.config(text="Recognizing...")
            root.update()
            chinese_text = recognizer.recognize_google(audio, language='zh-CN')
            input_text.delete(1.0, tk.END)
            input_text.insert(tk.END, chinese_text)

            # Translate to Hindi
            translated = translator.translate(chinese_text, src='zh-CN', dest='hi')
            output_text.delete(1.0, tk.END)
            output_text.insert(tk.END, translated.text)

            # Convert to speech
            tts = gTTS(translated.text, lang='hi')
            with tempfile.NamedTemporaryFile(delete=True, suffix=".mp3") as fp:
                tts.save(fp.name)
                playsound(fp.name)

            status_label.config(text="Done")
        except sr.WaitTimeoutError:
            status_label.config(text="No speech detected. Try again.")
        except sr.UnknownValueError:
            status_label.config(text="Could not understand the audio.")
        except Exception as e:
            status_label.config(text=f"Error: {str(e)}")

# GUI setup
root = tk.Tk()
root.title("Chinese to Hindi Voice Translator")
root.geometry("500x400")

title_label = tk.Label(root, text="🎤 Chinese to Hindi Voice Translator", font=("Arial", 16))
title_label.pack(pady=10)

input_label = tk.Label(root, text="Recognized Chinese Text:")
input_label.pack()
input_text = tk.Text(root, height=4, width=50)
input_text.pack()

output_label = tk.Label(root, text="Translated Hindi Text:")
output_label.pack()
output_text = tk.Text(root, height=4, width=50)
output_text.pack()

translate_button = tk.Button(root, text="Start Voice Translation", command=translate_chinese_to_hindi, bg="blue", fg="white")
translate_button.pack(pady=10)

status_label = tk.Label(root, text="", fg="green")
status_label.pack(pady=5)

root.mainloop()
