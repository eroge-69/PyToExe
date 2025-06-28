import tkinter as tk
from tkinter import messagebox
import threading
import pyautogui
import keyboard
import time

# Variável de controle
listening = False

def double_click():
    pyautogui.click()
    time.sleep(0.05)
    pyautogui.click()

def listen_f1():
    global listening
    while listening:
        if keyboard.is_pressed("f1"):
            double_click()
            while keyboard.is_pressed("f1"):
                time.sleep(0.1)
        time.sleep(0.01)

def toggle_listening():
    global listening
    if not listening:
        listening = True
        toggle_button.config(text="Desativar F1")
        threading.Thread(target=listen_f1, daemon=True).start()
    else:
        listening = False
        toggle_button.config(text="Ativar F1")

def close_app():
    global listening
    listening = False
    root.destroy()

# GUI
root = tk.Tk()
root.title("Double Click com F1")
root.geometry("250x120")
root.resizable(False, False)

label = tk.Label(root, text="Atalho: F1 → Double Click", font=("Arial", 10))
label.pack(pady=10)

toggle_button = tk.Button(root, text="Ativar F1", width=20, command=toggle_listening)
toggle_button.pack(pady=5)

exit_button = tk.Button(root, text="Sair", width=20, command=close_app)
exit_button.pack(pady=5)

root.protocol("WM_DELETE_WINDOW", close_app)
root.mainloop()
