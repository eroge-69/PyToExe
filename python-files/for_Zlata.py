import tkinter as tk
import random

# Список комплиментов в стиле системных ошибок
compliments = [
    "СИСТЕМНАЯ ОШИБКА: Ты слишком красивая для этого мира",
    "FATAL: Ты сделала мой сердечный ритм нестабильным",
    "ОШИБКА: Слишком много счастья. Причина: ты",
    "WARNING: Обнаружена непреодолимая симпатия",
    "CRITICAL: Ты — лучшее, что случилось за 10 лет",
    "ERROR: Не могу перестать думать о тебе",
    "СБОЙ: Ты снова улыбнулась — и я потерял концентрацию",
    "ОШИБКА: Ты пахнешь домом. Восстановление невозможно",
    "FATAL: Ты идеальна. Система отказывается это признавать",
    "WARNING: Уровень обаяния превышен — аварийное завершение"
]

# Настройки
TOTAL_WINDOWS = 10          # Количество окон
BATCH_DELAY = 150           # Задержка между окнами (мс)
WIDTH = 300
HEIGHT = 90
SCREEN_PADDING = 50

# Главное окно (скрыто)
root = tk.Tk()
root.withdraw()

# Счётчик закрытых окон
closed_count = 0


def create_one_window():
    """Создаёт одно окно-ошибку"""
    x = random.randint(SCREEN_PADDING, root.winfo_screenwidth() - WIDTH - SCREEN_PADDING)
    y = random.randint(SCREEN_PADDING, root.winfo_screenheight() - HEIGHT - SCREEN_PADDING)

    win = tk.Toplevel()
    win.geometry(f"{WIDTH}x{HEIGHT}+{x}+{y}")
    win.title(random.choice(["Ошибка", "Сбой", "Предупреждение", "Информация"]))
    win.resizable(False, False)
    win.configure(bg="SystemButtonFace")

    label = tk.Label(
        win,
        text=random.choice(compliments),
        font=("Segoe UI", 9),
        bg="SystemButtonFace",
        fg="black",
        wraplength=260,
        justify="left"
    )
    label.pack(pady=10, padx=10)

    button = tk.Button(
        win,
        text="ОК",
        font=("Segoe UI", 9),
        width=8,
        command=lambda: close_window(win)
    )
    button.pack(pady=5)

    win.transient()
    win.focus_force()
    win.grab_set()


def close_window(window):
    """Вызывается при закрытии одного окна"""
    global closed_count
    window.destroy()
    closed_count += 1

    # Если закрыты ВСЕ окна — показываем финальное
    if closed_count == TOTAL_WINDOWS:
        root.after(600, show_final_message)


def show_final_message():
    """Финальное окно с водопадом сердечек и плавным закрытием"""
    w, h = 500, 400
    x = (root.winfo_screenwidth() // 2) - (w // 2)
    y = (root.winfo_screenheight() // 2) - (h // 2)

    final = tk.Toplevel()
    final.title("Ты особенная ❤️")
    final.geometry(f"{w}x{h}+{x}+{y}")
    final.configure(bg="#ffebf3")
    final.resizable(False, False)
    final.focus_force()
    final.wm_attributes("-alpha", 1.0)  # Начальная непрозрачность

    # Текст
    label = tk.Label(
        final,
        text="Ты закрыла все ошибки...\n\nНо знай:\nя думаю о тебе\nкаждую секунду.\n\nЯ люблю тебя.",
        font=("Arial", 14, "bold"),
        bg="#ffebf3",
        fg="#d6306c",
        justify="center"
    )
    label.pack(pady=20)

    # Кнопка
    button = tk.Button(
        final,
        text="Я тоже тебя люблю ❤️",
        font=("Arial", 14, "bold"),
        bg="#ff6b9d",
        fg="white",
        activebackground="#ff4080",
        activeforeground="white",
        relief="flat",
        bd=0,
        padx=20,
        pady=12,
        width=20,
        height=2,
        cursor="hand2"
    )
    button.pack(pady=20)

    # Холст для сердечек
    canvas = tk.Canvas(final, width=w, height=h, bg="#ffebf3", highlightthickness=0)
    hearts = []           # Активные сердечки
    created = [0]         # Счётчик созданных (список для доступа в замыкании)
    max_hearts = 60       # Сколько всего создать

    def create_heart():
        """Создаёт одно сердечко сверху"""
        if created[0] < max_hearts:
            x_pos = random.randint(10, w - 10)
            size = random.randint(16, 28)
            color = random.choice(["#ff0000", "#ff3366", "#cc0066", "#ff6b9d", "#ff1493"])
            heart_id = canvas.create_text(
                x_pos, -20,
                text="❤",
                font=("Arial", size),
                fill=color,
                anchor="center"
            )
            hearts.append(heart_id)
            animate_heart(heart_id)
            created[0] += 1
            if created[0] < max_hearts:
                root.after(80, create_heart)
            else:
                root.after(1000, check_to_close)  # Проверяем, когда можно закрыть

    def animate_heart(heart_id):
        """Анимация падения сердечка"""
        try:
            canvas.move(heart_id, random.uniform(-0.5, 0.5), 4)  # Дрейф
            coords = canvas.coords(heart_id)
            if coords and coords[1] < h + 20:
                root.after(50, lambda: animate_heart(heart_id))
            else:
                canvas.delete(heart_id)
                if heart_id in hearts:
                    hearts.remove(heart_id)
        except (tk.TclError, IndexError):
            pass  # Окно закрыто

    def check_to_close():
        """Проверяет, все ли сердечки исчезли, и плавно закрывает окно"""
        if len(hearts) == 0:
            # Плавное затухание
            def fade_out(alpha):
                if alpha > 0.1:
                    final.wm_attributes("-alpha", alpha)
                    root.after(50, fade_out, alpha - 0.1)
                else:
                    final.destroy()  # Убираем окно
                    root.quit()      # Завершаем программу

            root.after(300, fade_out, 1.0)  # Запускаем через 0.3 сек
        else:
            root.after(200, check_to_close)  # Проверяем снова

    def start_rain():
        """Запускает водопад сердечек"""
        label.pack_forget()
        button.pack_forget()
        canvas.place(x=0, y=0, relwidth=1, relheight=1)
        created[0] = 0  # Сброс счётчика
        create_heart()  # Начинаем создавать сердечки

    button.config(command=start_rain)
    final.grab_set()


def start_spam():
    """Запускает цепочку из 10 окон"""
    def create_next(i):
        if i < TOTAL_WINDOWS:
            create_one_window()
            root.after(BATCH_DELAY, lambda: create_next(i + 1))

    create_next(0)


# Запуск через 0.5 секунды
root.after(500, start_spam)

# Главный цикл
root.mainloop()
