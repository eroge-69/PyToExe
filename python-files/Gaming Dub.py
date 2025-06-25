# main.py
# Flexible fallback when tkinter is not available

import threading
import sys

try:
    import speech_recognition as sr
except ImportError:
    print("[ERROR] speech_recognition is missing. Install via pip install SpeechRecognition")
    sr = None

try:
    from googletrans import Translator
except ImportError:
    print("[ERROR] googletrans is missing. Install via pip install googletrans==4.0.0-rc1")
    Translator = None

try:
    import tkinter as tk
    TK_AVAILABLE = True
except ImportError:
    print("[WARNING] tkinter not available. Subtitles will print to console instead.")
    TK_AVAILABLE = False

# === SubtitlesWindow ===
class SubtitlesWindow:
    def __init__(self):
        if TK_AVAILABLE:
            self.root = tk.Tk()
            self.root.title("Gamingdub - Tamil Subtitles")
            self.root.geometry("600x100+20+600")
            self.root.configure(bg='black')
            self.root.attributes('-topmost', True)

            self.label = tk.Label(self.root, text="", font=("Arial", 18), fg="white", bg="black", wraplength=580, justify="left")
            self.label.pack(padx=10, pady=20)
        else:
            self.root = None

    def update_text(self, text):
        if TK_AVAILABLE:
            self.label.config(text=text)
            self.root.update_idletasks()
        else:
            print("Tamil Subtitle:", text)

    def run(self):
        if TK_AVAILABLE:
            self.root.mainloop()
        else:
            print("[INFO] Running in headless mode. Press Ctrl+C to stop.")
            try:
                while True:
                    pass
            except KeyboardInterrupt:
                print("[INFO] Stopped.")

# === Translator ===
def translate_text(text):
    if Translator is None:
        return "[Translator not available] " + text
    try:
        translator = Translator()
        translated = translator.translate(text, src='en', dest='ta')
        return translated.text
    except Exception as e:
        return f"Translation error: {e}"

# === Audio Handler ===
def listen_in_background(callback):
    if sr is None:
        print("[ERROR] Speech recognition unavailable. Exiting...")
        return

    recognizer = sr.Recognizer()
    mic = sr.Microphone()

    def listen():
        with mic as source:
            recognizer.adjust_for_ambient_noise(source)
            while True:
                try:
                    print("Listening...")
                    audio = recognizer.listen(source, timeout=5)
                    text = recognizer.recognize_google(audio)
                    print("Heard:", text)
                    callback(text)
                except sr.UnknownValueError:
                    callback("[Unrecognized speech]")
                except Exception as e:
                    callback(f"[Error: {str(e)}]")

    threading.Thread(target=listen, daemon=True).start()


# === Main Program ===
subtitles = SubtitlesWindow()

def process_audio_callback(english_text):
    tamil_text = translate_text(english_text)
    subtitles.update_text(tamil_text)

def main():
    listen_in_background(process_audio_callback)
    subtitles.run()

if __name__ == "__main__":
    main()
