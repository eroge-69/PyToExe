import tkinter as tk

def main():
    # Создаем главное окно
    window = tk.Tk()
    window.title("Вывод текста")
    window.geometry("400x300")  # Размер окна

    # Создаем поле для текста
    text_widget = tk.Text(window, wrap='word')
    text_widget.pack(expand=True, fill='both', padx=10, pady=10)

    # Вставляем текст
    sample_text = "Это пример текста, который отображается в отдельном окне."
    text_widget.insert('1.0', sample_text)

    # Запускаем цикл обработки событий
    window.mainloop()

if __name__ == "__main__":
    main()