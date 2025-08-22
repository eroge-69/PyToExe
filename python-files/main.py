import tkinter as tk
import pyautogui
import json
import time
from pynput import mouse, keyboard
import threading

eventos = []
gravando = False
executando = False

# --- GRAVAÇÃO ---
def gravar():
    global gravando, eventos
    eventos = []
    gravando = True

    def on_click(x, y, button, pressed):
        if gravando and pressed:
            eventos.append({"x": x, "y": y, "button": str(button)})

    listener = mouse.Listener(on_click=on_click)
    listener.start()

def parar_gravacao():
    global gravando
    gravando = False
    with open("cliques.json", "w") as f:
        json.dump(eventos, f, indent=4)
    print("Gravação salva em cliques.json")

# --- REPRODUÇÃO ---
def reproduzir():
    global executando
    executando = True

    def loop():
        with open("cliques.json", "r") as f:
            acoes = json.load(f)

        while executando:
            for e in acoes:
                if not executando:
                    break
                pyautogui.click(e["x"], e["y"])
                time.sleep(0.5)

    threading.Thread(target=loop, daemon=True).start()

def parar_execucao():
    global executando
    executando = False

# --- TECLA DE EMERGÊNCIA (ESC) ---
def on_press(key):
    global executando
    if key == keyboard.Key.esc:
        executando = False
        print("Execução interrompida pelo usuário (ESC).")

listener = keyboard.Listener(on_press=on_press)
listener.start()

# --- INTERFACE ---
root = tk.Tk()
root.title("Macro Bot - Gravador de Cliques")
root.geometry("250x200")

tk.Label(root, text="Controle de Macro", font=("Arial", 12, "bold")).pack(pady=10)

tk.Button(root, text="🎥 Gravar", width=20, command=gravar).pack(pady=5)
tk.Button(root, text="⏹ Parar Gravação", width=20, command=parar_gravacao).pack(pady=5)
tk.Button(root, text="▶ Reproduzir", width=20, command=reproduzir).pack(pady=5)
tk.Button(root, text="⏹ Parar Execução", width=20, command=parar_execucao).pack(pady=5)

tk.Label(root, text="Dica: pressione ESC para parar o loop", fg="red").pack(pady=10)

root.mainloop()