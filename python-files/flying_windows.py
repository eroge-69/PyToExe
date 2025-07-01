import tkinter as tk
from tkinter import messagebox
import random
import sys

# Настройки
WINDOW_WIDTH, WINDOW_HEIGHT = 200, 100
BG_COLORS = ["#FF0000", "#00FF00", "#0000FF", "#FFFF00", "#FF00FF", "#00FFFF"]
active_windows = []

def confirm_exit():
    """Показывает диалог подтверждения выхода"""
    if messagebox.askyesno(
        "Выход", 
        "Вы уверены, что хотите закрыть все окна?",
        icon='question'
    ):
        close_all_windows()

def close_all_windows():
    """Аварийное закрытие всех окон"""
    while active_windows:
        try:
            active_windows.pop().destroy()
        except:
            pass
    root.destroy()
    sys.exit()

def create_dvd_window(x=None, y=None):
    window = tk.Toplevel()
    window.title("I'm a Flying Window")
    window.overrideredirect(True)
    window.attributes("-topmost", True)
    active_windows.append(window)
    
    # Обработчики закрытия
    window.protocol("WM_DELETE_WINDOW", confirm_exit)
    window.bind("<Escape>", lambda e: confirm_exit())
    
    # Дизайн окна
    bg_color = random.choice(BG_COLORS)
    window.configure(bg=bg_color)
    
    label = tk.Label(
        window,
        text="Попался!",
        font=("Arial", 20, "bold"),
        bg=bg_color,
        fg="white" if sum(int(bg_color[i:i+2], 16) for i in (1, 3, 5)) < 384 else "black"
    )
    label.pack(expand=True, fill="both")
    
    # Позиция и движение
    x = x or random.randint(0, window.winfo_screenwidth() - WINDOW_WIDTH)
    y = y or random.randint(0, window.winfo_screenheight() - WINDOW_HEIGHT)
    dx, dy = random.choice([(3,3), (3,-3), (-3,3), (-3,-3)])
    
    def move():
        nonlocal x, y, dx, dy
        x += dx
        y += dy
        
        # Физика отскоков
        if x <= 0 or x >= window.winfo_screenwidth() - WINDOW_WIDTH:
            dx *= -1
            change_color()
        if y <= 0 or y >= window.winfo_screenheight() - WINDOW_HEIGHT:
            dy *= -1
            change_color()
        
        window.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}+{x}+{y}")
        window.after(20, move)
    
    def change_color():
        new_color = random.choice([c for c in BG_COLORS if c != window.cget("bg")])
        window.configure(bg=new_color)
        label.configure(
            bg=new_color,
            fg="white" if sum(int(new_color[i:i+2], 16) for i in (1, 3, 5)) < 384 else "black"
        )
    
    # Интерактивность
    label.bind("<Button-1>", lambda e: create_dvd_window(e.x_root, e.y_root))
    label.bind("<Double-Button-1>", lambda e: confirm_exit())
    
    window.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}+{x}+{y}")
    move()

# Основное окно
root = tk.Tk()
root.withdraw()
root.bind("<Escape>", lambda e: confirm_exit())

# Стартовая точка
create_dvd_window()

# Информация при запуске
messagebox.showinfo(
    "Управление",
    "ЛКМ - создать новое окно\nПКМ/DoubleClick - закрыть все\nEsc - выход",
    parent=root
)

root.mainloop()