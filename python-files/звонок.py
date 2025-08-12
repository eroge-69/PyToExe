import tkinter as tk
from tkinter import messagebox

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Внимание! Windows заблокирован")
        self.root.attributes("-fullscreen", True)
        self.root.config(bg="black")

        self.total_time = 300
        self.time_left = self.total_time

        self.label_info = tk.Label(root, text="Ваш Windows заблокирован!\nЧерез 5 минут все данные будут удалены.",
                                   font=("Arial", 24), fg="red", bg="black")
        self.label_info.pack(pady=50)

        self.canvas = tk.Canvas(root, height=30, bg="white")
        self.canvas.pack(pady=20, fill='x', padx=100)
        self.progress = self.canvas.create_rectangle(0, 0, 0, 30, fill="red")

        self.entry = tk.Entry(root, show="*", font=("Arial", 20))
        self.entry.pack(pady=20)
        self.entry.focus()

        self.button = tk.Button(root, text="Ввести пароль", font=("Arial", 20), command=self.check_password)
        self.button.pack()

        self.sys_label = tk.Label(root, text="Система: Windows 10 Pro\nПользователь: USER\nДиск C: занято 75%",
                                  font=("Arial", 14), fg="white", bg="black")
        self.sys_label.pack(side="bottom", pady=30)

        # Запускаем таймер с задержкой, чтобы canvas успел отрисоваться
        self.root.after(100, self.update_timer)

    def update_timer(self):
        if self.time_left <= 0:
            messagebox.showinfo("Время вышло", "Данные удалены (но на самом деле нет).")
            self.root.destroy()
            return

        width = self.canvas.winfo_width()
        progress_width = width * (self.time_left / self.total_time)
        self.canvas.coords(self.progress, 0, 0, progress_width, 30)

        mins, secs = divmod(self.time_left, 60)
        self.root.title(f"Windows заблокирован - осталось {mins:02}:{secs:02}")

        self.time_left -= 1
        self.root.after(1000, self.update_timer)

    def check_password(self):
        pwd = self.entry.get()
        if pwd == "7777":
            messagebox.showinfo("Пароль верный", "Доступ разблокирован!")
            self.root.destroy()
        else:
            self.time_left -= 30
            if self.time_left < 0:
                self.time_left = 0
            messagebox.showwarning("Ошибка", "Неверный пароль! -30 секунд.")
            self.entry.delete(0, tk.END)

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
