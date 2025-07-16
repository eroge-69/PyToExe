import speech_recognition as sr
from googletrans import Translator, LANGUAGES
import tkinter as tk
from tkinter import ttk
import threading
import keyboard
import pyperclip
import pyaudio
import sounddevice as sd

translator = Translator()
recognizer = sr.Recognizer()

# 🎤 Get microphone list
def get_microphone_names():
    return sr.Microphone.list_microphone_names()

# 🔊 Get speaker output device list
def get_speaker_names():
    devices = sd.query_devices()
    speakers = [d['name'] for d in devices if d['max_output_channels'] > 0]
    return speakers

# GUI setup
root = tk.Tk()
root.title("🎮 Game Voice Translator Pro")
root.geometry("700x400")
root.attributes('-topmost', True)

output_box = tk.Text(root, height=12, width=80, wrap=tk.WORD)
output_box.pack(pady=5)

status_label = tk.Label(root, text="🔁 Ready (Hold SHIFT or V to translate)", fg="blue")
status_label.pack()

# Language selection
target_lang = tk.StringVar()
lang_list = sorted(LANGUAGES.items(), key=lambda x: x[1])
lang_names = [name.title() for code, name in lang_list]
lang_codes = [code for code, name in lang_list]

lang_combo = ttk.Combobox(root, values=["Auto (Speak Their Language)"] + lang_names, textvariable=target_lang, state="readonly")
lang_combo.set("English")
lang_combo.pack()

# 🎤 Microphone selector
mic_name = tk.StringVar()
mic_combo = ttk.Combobox(root, values=get_microphone_names(), textvariable=mic_name, state="readonly")
mic_combo.set(get_microphone_names()[0])
mic_combo.pack()
tk.Label(root, text="🎙 Select Microphone").pack()

# 🔊 Speaker selector (optional use)
speaker_name = tk.StringVar()
speaker_combo = ttk.Combobox(root, values=get_speaker_names(), textvariable=speaker_name, state="readonly")
speaker_combo.set(get_speaker_names()[0])
speaker_combo.pack()
tk.Label(root, text="🔊 Select Speaker (for future use)").pack()

clear_toggle = tk.BooleanVar(value=False)
tk.Checkbutton(root, text="Auto-clear old messages", variable=clear_toggle).pack()

copy_button = tk.Button(root, text="Copy Last Translation", state="disabled")
copy_button.pack(pady=2)

# Globals
listening = True
last_full_output = ""

def listen_and_translate():
    global listening, last_full_output
    mic_index = get_microphone_names().index(mic_name.get())
    with sr.Microphone(device_index=mic_index) as source:
        recognizer.adjust_for_ambient_noise(source)
        output_box.insert(tk.END, "[INFO] Hold SHIFT or V to activate translation...\n")
        output_box.see(tk.END)

        while listening:
            if keyboard.is_pressed('shift') or keyboard.is_pressed('v'):
                try:
                    status_label.config(text="🎤 Listening...", fg="green")
                    audio = recognizer.listen(source, timeout=2, phrase_time_limit=5)
                    spoken_text = recognizer.recognize_google(audio)

                    status_label.config(text="🌐 Translating...", fg="orange")
                    detected = translator.detect(spoken_text)
                    lang_code = detected.lang
                    lang_name = LANGUAGES.get(lang_code, "Unknown").title()

                    if target_lang.get() == "Auto (Speak Their Language)":
                        target_code = lang_code
                    else:
                        target_code = lang_codes[lang_names.index(target_lang.get())]

                    translated = translator.translate(spoken_text, src=lang_code, dest=target_code)
                    reply_lang_name = LANGUAGES.get(target_code, "Unknown").title()

                    result = (
                        f"👂 Heard: {spoken_text}\n"
                        f"🌍 Speaker Language: {lang_name} ({lang_code})\n"
                        f"💬 Reply With ({reply_lang_name}): {translated.text}\n\n"
                    )

                    last_full_output = result
                    if clear_toggle.get():
                        output_box.delete(1.0, tk.END)

                    output_box.insert(tk.END, result)
                    output_box.see(tk.END)
                    copy_button.config(state="normal")
                    status_label.config(text="✅ Translated - Hold key again to listen", fg="blue")

                except sr.UnknownValueError:
                    output_box.insert(tk.END, "[!] Couldn't understand speech.\n")
                    output_box.see(tk.END)
                    status_label.config(text="⚠️ Didn't catch that", fg="red")
                except Exception as e:
                    output_box.insert(tk.END, f"[ERROR] {str(e)}\n")
                    output_box.see(tk.END)
                    status_label.config(text="❌ Error", fg="red")

def start_translation():
    threading.Thread(target=listen_and_translate, daemon=True).start()

def stop_translation():
    global listening
    listening = False
    root.destroy()

def copy_translation():
    if last_full_output:
        pyperclip.copy(last_full_output)
        output_box.insert(tk.END, "[✔] Copied to clipboard.\n")
        output_box.see(tk.END)

copy_button.config(command=copy_translation)

tk.Button(root, text="Start Translator", command=start_translation).pack(pady=2)
tk.Button(root, text="Stop & Exit", command=stop_translation).pack(pady=2)

root.mainloop()
