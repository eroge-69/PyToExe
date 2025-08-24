import tkinter as tk
import random
import string

def generate_game_code(length=8):
    """Генерирует случайный код из букв и цифр."""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

def start_solo_mode():
    """Запускает режим 'Соло' с управлением точкой на холсте."""
    window = tk.Toplevel()
    window.title("Режим Соло")
    window.geometry("600x400")
    canvas = tk.Canvas(window, width=600, height=400, bg='white')
    canvas.pack()

    x, y = 300, 200
    radius = 10
    dot = canvas.create_oval(x - radius, y - radius, x + radius, y + radius, fill='black')

    def move(event):
        nonlocal x, y
        if event.keysym == 'Up':
            y -= 10
        elif event.keysym == 'Down':
            y += 10
        elif event.keysym == 'Left':
            x -= 10
        elif event.keysym == 'Right':
            x += 10
        x = max(radius, min(600 - radius, x))
        y = max(radius, min(400 - radius, y))
        canvas.coords(dot, x - radius, y - radius, x + radius, y + radius)

    window.bind('<KeyPress>', move)
    window.focus_set()

def create_game():
    """Создает игру и показывает уникальный код."""
    code = generate_game_code()
    win = tk.Toplevel()
    win.title("Создать игру")
    w