import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import os  # Добавляем импорт для модуля 'os'
import time

class HoronCheatCS2(tk.Tk):
    def __init__(self):
        super().__init__(screenName="HoronCheat CS2")
        self.title("HoronCheat CS2")
        self.resizable(False, False)  # Запрещаем изменение размерности окна
        self.overrideredirect(True)  # Убирает рамку окна и кнопку закрытия
        self.geometry("400x500+200+100")  # Ограничиваем разрешение окна и устанавливаем его координаты на экране
        self.configure(bg="#1c1c1d")  # Изменён цвет фона на темный синий

        # Create main frame
        self.main_frame = tk.Frame(self, bg="#1c1c1d")
        self.main_frame.pack()

        # Список названий читов
        cheat_names = [
            "AIM",
            "X-Ray",
            "RadarHack",
            "Better AIM",
            "TeamHack"
        ]

        self.switches = []
        for i in range(len(cheat_names)):
            label = tk.Label(self.main_frame, text=cheat_names[i], fg="#1c1c1d", bg="#1c1c1d", font=("Courier New", 14))
            switch = tk.IntVar()
            checkbox = tk.Checkbutton(self.main_frame, text=label.cget("text"), variable=switch, onvalue=1, offvalue=0,
                                      font=("Courier New", 12), bg='#1c1c1d', fg='yellow',
                                      command=lambda i=i: self.change_color(i))
            self.switches.append((label, switch))
            label.pack(pady=5)
            checkbox.pack(pady=5)

        # Create inject button with custom file name and add a hover effect
        self.inject_button = tk.Button(self.main_frame, text="Inject", fg="red", bg="black", command=self.open_file,
                                       font=("Courier New", 14))
        self.inject_button.pack(pady=30)
        self.inject_button.bind("<Enter>", lambda e: self.inject_button.config(bg='red'))
        self.inject_button.bind("<Leave>", lambda e: self.inject_button.config(bg='black'))

        # Add hover effect to close button
        self.close_button = tk.Button(self, text="X", font=("Courier New", 14), bg="#1c1c1d", fg="red",
                                      command=lambda: self.destroy())
        self.inject_button.pack(pady=(0, 30))
        self.close_button.place(x=350, y=20)
        self.close_button.bind("<Enter>", lambda e: self.close_button.config(bg='red'))
        self.close_button.bind("<Leave>", lambda e: self.close_button.config(bg="#1c1c1d"))

        # Add a progress bar for the injection process
        self.progress = tk.IntVar()
        self.progress_bar = ttk.Progressbar(self, orient="horizontal", length=200, mode='indeterminate', maximum=100)
        self.progress_bar.pack(fill=tk.X, pady=(30, 10))

    def open_file(self):
        # Получаем путь к директории, где находится текущий скрипт
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # Путь к папке bin
        bin_dir = os.path.join(current_dir, "bin")

        # Имя файла без расширения
        target_file_name = "activation__ini__injectify"
        found_file_path = None

        # Перебираем файлы в директории bin
        for file in os.listdir(bin_dir):
            # Проверяем, начинается ли имя файла с нужного имени
            if file.startswith(target_file_name):
                found_file_path = os.path.join(bin_dir, file)
                break  # Выходим из цикла, если нашли файл

        if found_file_path and os.path.exists(found_file_path):
            self.inject_start()
            os.system(f"start {found_file_path}")
        else:
            print("Файл не найден")

    def change_color(self, index):
        label, switch = self.switches[index]
        visible = switch.get() == 1
        if visible:
            label["fg"] = "red"
        else:
            label["fg"] = "#1c1c1d"

    def inject_start(self):
        if self.progress_bar["mode"] == 'indeterminate':
            self.progress_bar.start()
            time.sleep(1)  # Задержка для визуализации начала процесса внедрения
        else:
            self.progress_bar.configure(value=0, mode='determinate')
            for i in range(100):
                self.progress_bar['value'] = i
                time.sleep(0.05)  # Задержка для визуализации процесса внедрения
                self.update()  # Обновление окна GUI
            self.progress_bar.configure(mode='indeterminate')

if __name__ == "__main__":
    app = HoronCheatCS2()
    app.mainloop()