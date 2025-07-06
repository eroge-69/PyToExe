import speech_recognition as sr
from gtts import gTTS
import os
from playsound import playsound
import webbrowser
import subprocess
print("""

Доступные команды
Привет - приветствие помощника

Открой браузер - запуск веб-браузера

Открой блокнот - запуск блокнота

Выключи компьютер - выключение компьютера

Стоп или Хватит - завершение работы помощника

""")
# Функция для распознавания речи
def recognize_speech():

    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Слушаю...")
        audio = recognizer.listen(source)
        
        try:
            text = recognizer.recognize_google(audio, language='ru-RU')
            print(f"Вы сказали: {text}")
            return text
        except sr.UnknownValueError:
            print("Не удалось распознать речь")
            return None
        except sr.RequestError:
            print("Ошибка при подключении к сервису распознавания")
            return None

# Функция для синтеза речи
def speak(text):
    tts = gTTS(text=text, lang='ru')
    filename = "response.mp3"
    tts.save(filename)
    playsound(filename)
    os.remove(filename)

# Основные команды
def process_command(command):
    if "привет" in command.lower():
        speak("Здравствуйте! Чем могу помочь?")
    elif "открой браузер" in command.lower():
        speak("Открываю браузер")
        webbrowser.open("https://yandex.ru")
    elif "открой блокнот" in command.lower():
        speak("Открываю блокнот")
        subprocess.Popen(['notepad.exe'])
    elif "выключи компьютер" in command.lower():
        speak("Выключаю компьютер")
        os.system("shutdown /s /t 1")
    elif "стоп" in command.lower() or "хватит" in command.lower():
        speak("До свидания!")
        return False
    else:
        speak("Не поняла команду. Повторите, пожалуйста.")
    return True

# Основной цикл
def main():
    speak("Здравствуйте! Я ваш голосовой помощник.")
    while True:
        command = recognize_speech()
        if command:
            if not process_command(command):
                break

if __name__ == "__main__":
    main()
