import tkinter as tk
from tkinter import scrolledtext
from itertools import permutations

def generate_passwords():
    """Генерирует пароли и выводит их в текстовое поле."""
    must_include = entry_must.get().strip()
    optional_elements = entry_optional.get().strip().split()
    try:
        max_length = int(entry_max_len.get())
    except ValueError:
        output_area.delete(1.0, tk.END)
        output_area.insert(tk.END, "Ошибка! Введите число в поле 'Макс. длина'.")
        return
    
    passwords = set()
    # Генерируем все возможные комбинации
    for r in range(1, max_length + 1):
        for combo in permutations([must_include] + optional_elements, r):
            if combo.count(must_include) == 1:  # Проверяем, что обязательное слово ровно 1 раз
                password = "".join(combo)
                passwords.add(password)
    
    # Выводим результат
    output_area.delete(1.0, tk.END)
    if passwords:
        output_area.insert(tk.END, "\n".join(sorted(passwords)))
        output_area.insert(tk.END, f"\n\nВсего вариантов: {len(passwords)}")
    else:
        output_area.insert(tk.END, "Невозможно сгенерировать пароли с указанными параметрами.")

# Создаем главное окно
root = tk.Tk()
root.title("Генератор паролей")
root.geometry("600x500")

# Обязательное слово
tk.Label(root, text="Обязательное слово (1 раз):").pack(pady=5)
entry_must = tk.Entry(root, width=50)
entry_must.pack()

# Дополнительные слова
tk.Label(root, text="Дополнительные слова/символы (через пробел):").pack(pady=5)
entry_optional = tk.Entry(root, width=50)
entry_optional.pack()

# Максимальная длина
tk.Label(root, text="Максимальная длина пароля:").pack(pady=5)
entry_max_len = tk.Entry(root, width=10)
entry_max_len.pack()

# Кнопка генерации
btn_generate = tk.Button(root, text="Сгенерировать", command=generate_passwords)
btn_generate.pack(pady=10)

# Поле для вывода результатов
output_area = scrolledtext.ScrolledText(root, width=70, height=20, wrap=tk.WORD)
output_area.pack(padx=10, pady=5)

root.mainloop()
