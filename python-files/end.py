import tkinter as tk

def main():
    # Создаём главное окно приложения
    root = tk.Tk()
    root.title("Секретно")          # Заголовок окна
    root.geometry("300x150")           # Размеры окна (ширина x высота)

    # Добавляем надпись в центр окна
    label = tk.Label(
        root,
        text="154",
        font=("Helvetica", 24),      # Шрифт и размер
        fg="#333333"                 # Цвет текста
    )
    label.pack(expand=True)           # Центрируем виджет

    # Запускаем цикл обработки событий Tkinter
    root.mainloop()

if __name__ == "__main__":
    main()