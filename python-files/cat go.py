import tkinter as tk
from tkinter import messagebox, simpledialog

def main():
    root = tk.Tk()
    root.withdraw()  # Скрыть главное окно

    # Сообщение об ошибке открытия файла
    messagebox.showerror("system", "Не удаётся открыть cat go.py")

    # Запрос подтверждения
    response = messagebox.askquestion("ebcvhcvbvcvvcvcvcv", "Вы правда хотите начать?")
    if response == 'no':
        messagebox.showinfo("Отмена", "Операция отменена пользователем.")
        return

    # Приветственное сообщение
    messagebox.showinfo("Приветствие", "Здравствуйте! Давайте познакомимся.")

    # Запрос имени и фамилии
    first_name = simpledialog.askstring("Ввод имени", "Введите ваше имя:")
    last_name = simpledialog.askstring("Ввод фамилии", "Введите вашу фамилию:")

    # Проверка, ввёл ли пользователь данные
    if not first_name:
        first_name = "Гость"

    if not last_name:
        full_name = first_name
    else:
        full_name = f"{first_name} {last_name}"

    # Вывод итогового сообщения
    messagebox.showinfo("Рада знакомству", f"Приятно познакомиться, {full_name}!")

    # Ещё одно сообщение
    messagebox.showinfo("Ваша математичка", "Всё равно не открою cat go.py")

if __name__ == "__main__":
    main()
