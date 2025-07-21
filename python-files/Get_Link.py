import tkinter as tk
from tkinter import messagebox
import webbrowser

def check_code():
    entered_code = code_entry.get()
    correct_code = "GhooseFun"
    if entered_code == correct_code:
        messagebox.showinfo("Успех!", "Доступ предоставлен! Открываем ссылку...")
        webbrowser.open("https://clck.ru/3NBGzc")
        root.destroy()
    else:
        messagebox.showerror("Ошибка", "Неверный код! Попробуйте снова.")

# Создаем главное окно
root = tk.Tk()
root.title("Grok's Cosmic Code Gate")
root.geometry("400x300")
root.configure(bg="#0a0a23")

# Стили в космическом стиле
label_style = {"font": ("Orbitron", 14), "fg": "#00ffcc", "bg": "#0a0a23"}
entry_style = {"font": ("Orbitron", 12), "fg": "#00ffcc", "bg": "#1b1b38", "insertbackground": "#00ffcc"}
button_style = {"font": ("Orbitron", 12), "fg": "#0a0a23", "bg": "#00ffcc", "activebackground": "#00cc99"}

# Заголовок
welcome_label = tk.Label(
    root,
    text="Добро пожаловать в Cosmic Gate!\nВведите код из чата FunPay",
    justify="center",
    **label_style
)
welcome_label.pack(pady=30)

# Поле для ввода кода
code_entry = tk.Entry(root, width=20, **entry_style)
code_entry.pack(pady=10)

# Кнопка проверки
check_button = tk.Button(root, text="Проверить код", command=check_code, **button_style)
check_button.pack(pady=20)

# Космический фон с эффектом
canvas = tk.Canvas(root, width=400, height=300, bg="#0a0a23", highlightthickness=0)
canvas.place(x=0, y=0)
for i in range(50):
    x, y = i * 8, i * 6
    canvas.create_oval(x, y, x + 2, y + 2, fill="#00ffcc")

root.mainloop()