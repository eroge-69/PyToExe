import speech_recognition as sr
import pyttsx3
import datetime
import subprocess
import webbrowser
import os
import time
import threading
from pycaw.pycaw import AudioUtilities
from comtypes import CLSCTX_ALL
from ctypes import cast, POINTER
from comtypes.client import CreateObject
import pyautogui
import psutil

engine = pyttsx3.init()
recognizer = sr.Recognizer()

# Настройка голоса
voices = engine.getProperty('voices')
if len(voices) > 0:
    engine.setProperty('voice', voices[0].id)  
else:
    engine.setProperty('voice', 'default')  
engine.setProperty('rate', 180)  

opera_path = r"C:\Users\marik\AppData\Local\Programs\Opera GX\opera.exe"
webbrowser.register('opera', None, webbrowser.BackgroundBrowser(opera_path))


def speak(text):
    """Озвучивает текст и делает паузу для стабильности"""
    print(f"Джарвис: {text}")
    engine.say(text)
    engine.runAndWait()
    time.sleep(0.3)

def listen(timeout=5, phrase_time_limit=5):
    """Слушает и распознаёт одну фразу"""
    with sr.Microphone() as source:
        print("🎙️ Готов к записи...")
        recognizer.adjust_for_ambient_noise(source, duration=0.5)
        try:
            audio = recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
            text = recognizer.recognize_google(audio, language="ru-RU")
            print(f"Вы сказали: {text}")
            return text.lower()
        except sr.WaitTimeoutError:
            print("Таймаут: ничего не сказано.")
            return ""
        except sr.UnknownValueError:
            print("Не удалось распознать речь.")
            return ""
        except sr.RequestError as e:
            print(f"Ошибка сервиса распознавания: {e}")
            speak("Ошибка распознавания. Проверьте интернет.")
            return ""
        except Exception as e:
            print(f"Ошибка прослушивания: {e}")
            return ""

def set_volume(level):
    """Устанавливает громкость (0.0 — 1.0)"""
    try:
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = cast(interface, POINTER(IAudioEndpointVolume))
        volume.SetMasterVolumeLevelScalar(level, None)
        speak(f"Громкость установлена на {int(level * 100)}%.")
    except Exception as e:
        print("Ошибка управления громкостью:", e)
        speak("Не удалось изменить громкость.")

def toggle_mute():
    """Включает/выключает звук"""
    try:
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = cast(interface, POINTER(IAudioEndpointVolume))
        is_muted = volume.GetMute()
        if is_muted:
            volume.SetMute(0, None)
            speak("Звук включён.")
        else:
            volume.SetMute(1, None)
            speak("Звук выключен.")
    except Exception as e:
        print("Ошибка при отключении звука:", e)
        speak("Не удалось переключить звук.")

def open_url(url):
    """Открывает URL в Opera GX в фоновом потоке"""
    try:
        thread = threading.Thread(target=webbrowser.get('opera').open, args=(url,), daemon=True)
        thread.start()
    except Exception as e:
        print("Ошибка открытия браузера:", e)
        try:
            os.startfile(opera_path)
            time.sleep(1)
            os.system(f'start "" "{url}"')
        except:
            speak("Не удалось открыть браузер.")

def open_steam():
    """Открывает Steam, если путь существует"""
    steam_path = r"D:\steam\steam.exe"
    if os.path.exists(steam_path):
        speak("Запускаю Steam...")
        os.startfile(steam_path)
    else:
        speak("Steam не найден по указанному пути. Проверьте путь.")
        print("Путь не найден:", steam_path)

def close_application_by_name(process_name):
    """Закрывает приложение по имени процесса (например, steam.exe)"""
    try:
        found = False
        for proc in psutil.process_iter(['pid', 'name']):
            if process_name.lower() in proc.info['name'].lower():
                os.system(f'taskkill /f /im "{proc.info["name"]}"')
                speak(f"Приложение {proc.info['name']} закрыто.")
                found = True
        if not found:
            speak(f"Приложение {process_name} не запущено.")
    except Exception as e:
        print("Ошибка при закрытии приложения:", e)
        speak("Не удалось закрыть приложение.")

def execute_command(command):
    """Выполняет команду"""
    if not command.strip():
        speak("Я ничего не услышал.")
        return

    try:
        if "привет" in command:
            speak("Привет, сэр. Готов к работе.")

        elif "время" in command:
            now = datetime.datetime.now().strftime("%H:%M")
            speak(f"Сейчас {now}")

        elif "дата" in command:
            today = datetime.datetime.now().strftime("%d %B %Y")
            speak(f"Сегодня {today}")

        elif "открой браузер" in command:
            speak("Открываю Opera GX")
            open_url("https://google.com")

        elif "открой youtube" in command:
            speak("Открываю YouTube")
            open_url("https://youtube.com")

        elif "поиск" in command:
            query = command.replace("поиск", "").strip()
            if query:
                speak(f"Ищу {query}")
                url = f"https://www.google.com/search?q={query}"
                open_url(url)
            else:
                speak("Что искать?")

        elif "открой блокнот" in command:
            speak("Открываю Блокнот")
            try:
                subprocess.Popen([r"C:\Windows\System32\notepad.exe"])
            except Exception as e:
                speak("Не удалось открыть Блокнот")
                print("Ошибка:", e)

        elif "открой калькулятор" in command:
            speak("Открываю Калькулятор")
            try:
                subprocess.Popen("start calc", shell=True)
            except Exception as e:
                speak("Не удалось открыть Калькулятор")
                print("Ошибка:", e)

        elif "громкость вверх" in command or "увеличь громкость" in command:
            set_volume(0.8)

        elif "громкость вниз" in command or "уменьши громкость" in command:
            set_volume(0.3)

        elif "выключи звук" in command or "отключи звук" in command or "звук выключи" in command:
            toggle_mute()

        elif "включи звук" in command or "звук включи" in command:
            set_volume(0.5)
            speak("Звук включён.")

        elif "закрой окно" in command:
            speak("Закрываю текущее окно")
            pyautogui.hotkey('alt', 'f4')

        elif "открой steam" in command or "запусти стим" in command:
            open_steam()

        elif "закрой steam" in command or "выключи стим" in command:
            close_application_by_name("steam.exe")

        elif "закрой браузер" in command:
            close_application_by_name("opera.exe")

        elif "выключи компьютер" in command:
            speak("Выключаю компьютер через 10 секунд")
            os.system("shutdown /s /t 10")

        elif "отмени выключение" in command:
            speak("Отменяю выключение")
            os.system("shutdown /a")

        elif any(word in command for word in ["пока", "хватит", "выход", "стоп", "спать"]):
            speak("Выхожу из режима. До новых команд.")
            return "exit_mode"

        else:
            speak("Неизвестная команда.")

    except Exception as e:
        speak("Ошибка при выполнении команды.")
        print("Ошибка в execute_command:", e)

    return "continue"

if __name__ == "__main__":
    print("🎧 Доступные микрофоны:")
    for i, name in enumerate(sr.Microphone.list_microphone_names()):
        print(f"  {i}: {name}")
    print("\n" + "="*50)
    speak("Джарвис активирован. Скажите 'Джарвис', чтобы вызвать.")
    print("Говорите 'Джарвис' для активации...")

    while True:
        try:
            print("\n[Ожидание активации...]")
            command = listen(timeout=10, phrase_time_limit=3)

            if command and "джарвис" in command:
                speak("Режим активации. Готов к командам.")
                print("[Режим команд: жду команды...]")

                while True:
                    command = listen(timeout=5, phrase_time_limit=5)

                    if not command:
                        speak("Нет команды. Выхожу из режима.")
                        break

                    result = execute_command(command)
                    if result == "exit_mode":
                        break

                    time.sleep(0.5)

        except KeyboardInterrupt:
            speak("Система отключена.")
            break

        except Exception as e:
            print("❗ Критическая ошибка:", e)
            speak("Перезапускаю систему...")
            time.sleep(2)
            continue
