import tkinter as tk

# 1. Создаем главное окно
root = tk.Tk()
root.title("Конвертер")
root.geometry("500x300")

# 2. Создаем все виджеты
entr = tk.Entry(root)
entr.pack()

lbl = tk.Label(root, text="Результат: ")
lbl.pack()

btn = tk.Button(root, text="Конвертировать")
btn.pack()

# 3. Определяем функцию, которая использует entr
def convert_currency():
    # Твоя логика конвертации здесь
    try:
        dollars = float(entr.get())
        manats = dollars * 1.70
        lbl.config(text=f"{manats} манатов")
    except ValueError:
        lbl.config(text="Ошибка!")

# 4. Привязываем функцию к кнопке
btn.config(command=convert_currency)

# 5. Запускаем главный цикл
root.mainloop()