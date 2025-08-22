import speech_recognition as sr
import pyautogui
import time
import json
import argparse
import os

BUTTONS = ["маленький", "средний", "большой", "выход"]

def load_coords():
    if os.path.exists("button_coords.json"):
        with open("button_coords.json", "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_coords(coords):
    with open("button_coords.json", "w", encoding="utf-8") as f:
        json.dump(coords, f, ensure_ascii=False, indent=2)

def setup(labels):
    coords = {}
    print("Наводи мышь на каждую кнопку и жми Enter.")
    for label in labels:
        input(f"Наведи на '{label}' и нажми Enter...")
        x, y = pyautogui.position()
        coords[label] = (x, y)
        print(f"Сохранено: {label} → {x}, {y}")
    save_coords(coords)
    print("Готово! Координаты сохранены.")

def main(labels, speed):
    recognizer = sr.Recognizer()
    mic = sr.Microphone()
    coords = load_coords()

    print("Слушаю команды... Говори:", ", ".join(labels))

    with mic as source:
        recognizer.adjust_for_ambient_noise(source, duration=0.5)
        while True:
            try:
                audio = recognizer.listen(source, phrase_time_limit=1)
                text = recognizer.recognize_google(audio, language="ru-RU").lower()
                print("Распознано:", text)

                for label in labels:
                    if label[:4] in text:
                        if label == "выход":
                            print("Выход...")
                            return
                        if label in coords:
                            x, y = coords[label]
                            pyautogui.moveTo(x, y, duration=speed)
                            pyautogui.click()
                            print(f"Клик по '{label}'")
                        else:
                            print(f"Нет координат для '{label}'")
            except sr.UnknownValueError:
                pass
            except Exception as e:
                print("Ошибка:", e)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--setup", action="store_true", help="Режим настройки координат")
    parser.add_argument("--labels", nargs="*", default=BUTTONS, help="Список слов-команд")
    parser.add_argument("--speed", type=float, default=0.2, help="Скорость наведения (сек)")
    args = parser.parse_args()

    if args.setup:
        setup(args.labels)
    else:
        main(args.labels, args.speed)
