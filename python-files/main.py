import queue
import sounddevice as sd
from vosk import Model, KaldiRecognizer
import json
from gpt4all import GPT4All
import pyttsx3
import os
import tkinter as tk
from PIL import Image, ImageTk, ImageSequence
from tkinter import scrolledtext
import threading

# === CONFIGURATION ===
VOSK_MODEL_PATH = "."  # folder name

# === Voice recognition using Vosk ===
q = queue.Queue()
running = False
stop_event = threading.Event() 

def callback(indata, frames, time, status):
    global running
    if status:
        print("Status:", status)
    q.put(bytes(indata))

def recognize_speech():
    global running
    if not os.path.exists(VOSK_MODEL_PATH):
        print("❌ Vosk model not found!")
        return ""

    model = Model(VOSK_MODEL_PATH)
    recognizer = KaldiRecognizer(model, 16000)

    print("🎤 Speak now... (Ctrl+C to stop)")
    with sd.RawInputStream(samplerate=16000, blocksize=8000, dtype='int16',
                           channels=1, callback=callback):
        while True:
            data = q.get()
            if recognizer.AcceptWaveform(data):
                result = json.loads(recognizer.Result())
                return result.get("text", "")

# === GPT4All ===
def chat_with_gpt4all(prompt):
    global running
    if not os.path.exists("Llama-3.2-1B-Instruct-Q4_0.gguf"):
        print("❌ GPT4All model not found!")
        text_1.delete("1.0", "end")
        text_1.insert(tk.END,"Please select the model")
        return "please select the model."

    model = GPT4All("Llama-3.2-1B-Instruct-Q4_0.gguf",allow_download=False)
    with model.chat_session():
        response = model.generate(prompt, temp=0.7,max_tokens=100)
        return response

# === Text to speech ===
def speak(text):
    global running
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

# === Main Loop ===
def main():
    global running
    while not stop_event.is_set():
        question=recognize_speech()
        if "jarvis" in question:
            speak("hi how can i assists you")
            text_1.delete("1.0", "end")
            text_1.insert(tk.END,'hi how can i assists you')
            try:
                while True:
                      question=recognize_speech()
                      if "stop" in question:
                          speak("At your service")
                          text_1.delete("1.0", "end")
                          text_1.insert(tk.END,'At your service')
                          break
                      elif question.strip():
                         print(f"\n🗣 You said: {question}")
                         answer = chat_with_gpt4all(question)
                         text_1.delete("1.0", "end")
                         text_1.insert(tk.END,{answer})
                         print(f"\n🤖 GPT4All: {answer}")
                         speak(answer)
                      else:
                        pass
            except:
                pass
def start_loop():
    t = threading.Thread(target=main, daemon=True)
    t.start()

# Close the UI and stop the loop
def on_closing():
    stop_event.set()     # Set the flag to exit the loop
    root.destroy()

root = tk.Tk()
root.title("Jarvis")
root.geometry("800x600")
root.resizable(False,False)


# Load animated GIF
gif = Image.open(r"animation.gif")  # replace with your gif file
frames = [
    ImageTk.PhotoImage(
        frame.copy().resize((1000, 480), Image.LANCZOS)
    )
    for frame in ImageSequence.Iterator(gif)
]

# Set up label to show GIF
bg_label = tk.Label(root)
bg_label.place(relwidth=1, relheight=0.8)

# Animation loop
def update_frame(ind):
    frame = frames[ind]
    bg_label.configure(image=frame)
    ind = (ind + 1) % len(frames)
    root.after(100, update_frame, ind)

update_frame(0)


text_1=scrolledtext.ScrolledText(root,bg="#0F1010",fg="#B4B6D9",font=('Arial','12','bold'),height=7,width=86)
text_1.place(x=3,y=455)

root.protocol("WM_DELETE_WINDOW",on_closing)
start_loop()              
root.mainloop()

