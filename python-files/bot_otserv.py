
import pyautogui
import time
import threading
import json
from tkinter import Tk, Button

waypoints = []

def save_position(x, y):
    waypoints.append((x, y))

def record_route():
    print("Clique nos pontos do caminho. Pressione Ctrl+C no terminal para finalizar.")
    try:
        while True:
            x, y = pyautogui.position()
            if pyautogui.mouseDown():
                save_position(x, y)
                print(f"Ponto salvo: {x}, {y}")
                time.sleep(0.5)
    except KeyboardInterrupt:
        with open("rota.json", "w") as f:
            json.dump(waypoints, f)
        print("Rota salva.")

def walk_route():
    try:
        with open("rota.json", "r") as f:
            loaded_waypoints = json.load(f)
    except:
        print("Erro ao carregar rota.")
        return

    while True:
        for x, y in loaded_waypoints:
            pyautogui.click(x, y)
            time.sleep(2)
            pyautogui.press('f1')
            screenshot = pyautogui.screenshot(region=(100, 50, 150, 20))
            avg_color = screenshot.getpixel((10, 10))
            if avg_color[0] < 100:
                pyautogui.press('f2')

def start_bot():
    threading.Thread(target=walk_route).start()

def gui():
    root = Tk()
    root.title("Bot OTServ")

    Button(root, text="Gravar Rota", command=record_route).pack(pady=10)
    Button(root, text="Iniciar Bot", command=start_bot).pack(pady=10)

    root.mainloop()

if __name__ == "__main__":
    gui()
