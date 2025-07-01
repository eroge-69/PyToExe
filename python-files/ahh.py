import tkinter as tk
import random

class CrazyWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("eblan laucher")
        self.root.geometry("300x200")
        self.root.configure(bg='white')

        # Создаем кнопку
        self.button = tk.Button(self.root, text="Скачать", command=self.start_madness)
        self.button.pack(expand=True)

        # Переменные для анимации
        self.moving = False
        self.color_change = False

    def start_madness(self):
        # Запускаем анимацию
        if not self.moving:
            self.moving = True
            self.color_change = True
            self.animate()

    def animate(self):
        if not self.moving:
            return

        # Меняем цвет фона на случайный
        r = lambda: random.randint(0,255)
        color = f'#{r():02x}{r():02x}{r():02x}'
        self.root.configure(bg=color)

        # Перемещаем окно по экрану с бешеной скоростью
        x = random.randint(0, self.root.winfo_screenwidth() - self.root.winfo_width())
        y = random.randint(0, self.root.winfo_screenheight() - self.root.winfo_height())
        try:
            self.root.geometry(f"+{x}+{y}")
        except:
            pass

        # Запускаем следующую итерацию очень быстро
        self.root.after(10, self.animate)  # 10 мс между обновлениями

# Создаем главное окно и запускаем программу
if __name__ == "__main__":
    root = tk.Tk()
    app = CrazyWindow(root)
    root.mainloop()