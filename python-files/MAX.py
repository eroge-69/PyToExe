import tkinter as tk
import random
import threading

def show_virus_windows():
    root = tk.Tk()
    root.withdraw()  # Скрываем главное окно

    # Получаем размер экрана
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    windows = []

    def create_window():
        win = tk.Toplevel()
        win.title("ВИРУС: СИСТЕМА ЗАРАЖЕНА MAX")
        win.geometry("500x180")
        win.configure(bg="black")

        # Случайное положение окна
        x = random.randint(0, screen_width - 500)
        y = random.randint(0, screen_height - 200)
        win.geometry(f"500x180+{x}+{y}")

        # Текст ошибки
        text = (
            "ВАШ КОМПЬЮТЕР БЫЛ ЗАРАЖЁН\n"
            "С ПОМОЩЬЮ МЕССЕНДЖЕРА MAX\n\n"
            "ВСЕ ВАШИ ДАННЫЕ БЫЛИ УДАЛЕНЫ\n"
            "И ОТПРАВЛЕНЫ В ФСБ"
        )

        label = tk.Label(
            win,
            text=text,
            font=("Consolas", 14, "bold"),
            fg="red",
            bg="black",
            justify="center"
        )
        label.pack(expand=True)

        # Кнопка "ОК" — просто закрывает окно
        button = tk.Button(
            win,
            text="ОК",
            command=win.destroy,
            bg="red",
            fg="white",
            font=("Arial", 12, "bold"),
            width=10
        )
        button.pack(pady=10)

        # Поверх всех окон
        win.attributes("-topmost", True)
        win.protocol("WM_DELETE_WINDOW", win.destroy)

        windows.append(win)

    # Создаём 50 окон
    for _ in range(100):
        create_window()
        root.update()  # Обновляем интерфейс, чтобы окна появлялись мгновенно
        # Небольшая задержка, чтобы не перегружать систему
        root.after(10)

    root.mainloop()

# Запускаем в отдельном потоке
if __name__ == "__main__":
    threading.Thread(target=show_virus_windows, daemon=True).start()
    input("Шутка запущена. Закройте все окна, чтобы завершить...")