# save this as server.py
from flask import Flask, request, jsonify
import threading
import pyautogui
import time

app = Flask(name)

# Змінна для зберігання стану підключення
connected = False

# Функція для прийому команд від керуючого
def receive_commands():
    global connected
    while True:
        if connected:
            command = input("Enter command: ")
            if command == "exit":
                connected = False
                break
            elif command.startswith("type "):
                text = command[5:]
                pyautogui.typewrite(text)
            elif command == "screenshot":
                screenshot = pyautogui.screenshot()
                screenshot.save("screenshot.png")
                print("Screenshot saved as screenshot.png")
            elif command == "alert":
                pyautogui.alert("You are controlled!")
            else:
                print("Unknown command")
        time.sleep(1)

# Маршрут для підключення керуючого
@app.route('/connect', methods=['POST'])
def connect():
    global connected
    connected = True
    threading.Thread(target=receive_commands).start()
    return jsonify({"message": "Connected"})

# Маршрут для відправки команд
@app.route('/command', methods=['POST'])
def command():
    data = request.json
    command = data.get('command')
    if command:
        if command == "screenshot":
            screenshot = pyautogui.screenshot()
            screenshot.save("screenshot.png")
            return jsonify({"message": "Screenshot taken"})
        elif command == "alert":
            pyautogui.alert("You are controlled!")
            return jsonify({"message": "Alert shown"})
        elif command.startswith("type "):
            text = command[5:]
            pyautogui.typewrite(text)
            return jsonify({"message": "Text typed"})
        else:
            return jsonify({"message": "Unknown command"}), 400
    return jsonify({"message": "No command provided"}), 400

if name == 'main':
    app.run(port=5000)