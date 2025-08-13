import tkinter as tk
from tkinter import messagebox
import time
import random
import webbrowser

class JokeVirus:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("💀 КРИТИЧЕСКИЙ ВИРУС 💀")
        self.root.geometry("550x450")
        self.root.resizable(False, False)
        self.root.configure(bg="black")

        # Настройки вируса
        self.secret_code = "12345"  # Правильный код
        self.video_url = "https://yandex.ru/video/preview/4949585347665448597"  # Ваше видео

        # Шрифты
        self.title_font = ("Arial", 20, "bold")
        self.text_font = ("Arial", 12)
        self.button_font = ("Arial", 12, "bold")

        self.create_widgets()

    def create_widgets(self):
        # Заголовок
        tk.Label(
            self.root,
            text="💀 ВАШ КОМПЬЮТЕР ЗАРАЖЕН! 💀",
            font=self.title_font,
            fg="red",
            bg="black"
        ).pack(pady=20)

        # Сообщение о вирусе
        tk.Label(
            self.root,
            text="Вирус: TROJAN.PYTHON.ALARM\nВсе файлы будут удалены через 30 секунд!",
            font=self.text_font,
            fg="white",
            bg="black"
        ).pack()

        # Таймер
        self.timer_label = tk.Label(
            self.root,
            text="Осталось времени: 30 секунд",
            font=self.text_font,
            fg="yellow",
            bg="black"
        )
        self.timer_label.pack(pady=10)

        # Прогресс "заражения"
        self.progress = tk.Label(
            self.root,
            text="Удаление файлов: 0%",
            font=self.text_font,
            fg="white",
            bg="black"
        )
        self.progress.pack()

        # Поле для ввода кода
        tk.Label(
            self.root,
            text="Введите код деактивации:",
            font=self.text_font,
            fg="lime",
            bg="black"
        ).pack(pady=10)

        self.code_entry = tk.Entry(self.root, font=self.text_font, show="*")
        self.code_entry.pack()

        # Кнопка
        tk.Button(
            self.root,
            text="ОСТАНОВИТЬ ВИРУС",
            command=self.check_code,
            font=self.button_font,
            bg="red",
            fg="white",
            activebackground="darkred"
        ).pack(pady=20)

        # Запускаем обратный отсчет
        self.countdown(30)

    def countdown(self, seconds_left):
        if seconds_left >= 0:
            # Обновляем таймер
            self.timer_label.config(text=f"Осталось времени: {seconds_left} секунд")
            
            # Обновляем прогресс "удаления"
            progress = 100 - (seconds_left * 100 // 30)
            self.progress.config(text=f"Удаление файлов: {progress}%")
            
            # Случайные эффекты
            if seconds_left % 5 == 0:
                self.root.configure(bg=random.choice(["black", "maroon"]))
            
            # Продолжаем отсчет
            self.root.after(1000, self.countdown, seconds_left - 1)
        else:
            # Если время вышло
            self.time_expired()

    def time_expired(self):
        self.progress.config(text="Удаление завершено! 💀", fg="red")
        messagebox.showerror(
            "ПОЗДНО!",
            "Все ваши файлы удалены!\n\nШутка! Введите код 12345 чтобы увидеть сюрприз"
        )

    def check_code(self):
        if self.code_entry.get() == self.secret_code:
            messagebox.showinfo(
                "УСПЕХ!",
                "Вирус деактивирован! Это была шутка 😊\n"
                "Сейчас откроется видео-сюрприз..."
            )
            self.root.destroy()
            webbrowser.open(self.video_url)  # Открываем ваше видео
        else:
            messagebox.showerror(
                "ОШИБКА!",
                f"Неверный код! Попробуйте еще раз.\nПодсказка: {self.secret_code}"
            )

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    virus = JokeVirus()
    virus.run()
