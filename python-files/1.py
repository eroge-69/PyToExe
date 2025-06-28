import PySimpleGUI as sg
import speech_recognition as sr
import openai
from gtts import gTTS
from playsound import playsound
import tempfile
import os

# 1) Настройка ключа API
openai.api_key = "ВАШ_OPENAI_API_KEY"

# 2) GUI layout
layout = [
    [sg.Button("Новый чат", key="-NEW-")],
    [sg.Multiline(size=(60,10), key="-HISTORY-", disabled=True)],
    [sg.Input(key="-IN-"), sg.Button("Отправить", key="-SEND-"), sg.Button("Голос", key="-VOICE-")]
]
window = sg.Window("Voice-Chat GPT", layout)

# 3) Speech-to-Text
recognizer = sr.Recognizer()
mic = sr.Microphone()

def listen():
    with mic as source:
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)
    try:
        return recognizer.recognize_google(audio, language="ru-RU")
    except sr.UnknownValueError:
        return ""

# 4) Вызов нейронки
def ask_gpt(prompt, history):
    # собираем историю + новый запрос
    msgs = [{"role":r,"content":c} for r,c in history]
    msgs.append({"role":"user","content": prompt})
    resp = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=msgs
    )
    return resp.choices[0].message.content

# 5) Text-to-Speech
def speak(text):
    tts = gTTS(text=text, lang="ru")
    tf = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    tts.save(tf.name)
    playsound(tf.name)
    os.unlink(tf.name)

# 6) Главный цикл
chat_history = []  # list of tuples: (role, text)
while True:
    event, values = window.read()
    if event in (sg.WIN_CLOSED,):
        break
    if event == "-NEW-":
        chat_history.clear()
        window["-HISTORY-"].update("")
    if event == "-VOICE-":
        user_text = listen()
        window["-IN-"].update(user_text)
    if event == "-SEND-":
        user_text = values["-IN-"].strip()
        if not user_text: continue
        chat_history.append(("user", user_text))
        window["-HISTORY-"].print("Вы: " + user_text)
        ans = ask_gpt(user_text, chat_history)
        chat_history.append(("assistant", ans))
        window["-HISTORY-"].print("GPT: " + ans)
        speak(ans)
        window["-IN-"].update("")
window.close()
