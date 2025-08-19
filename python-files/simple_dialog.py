import tkinter as tk

def on_yes():
    root.quit()  # Закрывает окно при клике на "Да"

def on_no():
    root.quit()  # Закрывает окно при клике на "Нет"

root = tk.Tk()
root.title("Окно")  # Заголовок окна (можно скорректировать при необходимости)

label = tk.Label(root, text="Текст", padx=20, pady=20)
label.pack()

yes_button = tk.Button(root, text="Да", command=on_yes)
yes_button.pack(side=tk.LEFT, padx=10)

no_button = tk.Button(root, text="Нет", command=on_no)
no_button.pack(side=tk.RIGHT, padx=10)

root.mainloop()