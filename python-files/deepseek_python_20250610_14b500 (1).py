import tkinter as tk
from tkinter import messagebox
from datetime import datetime

class StudentApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Данные студента")
        
        # Переменные для хранения данных
        self.full_name = tk.StringVar()
        self.group_number = tk.StringVar()
        
        self.create_form1()
    
    def create_form1(self):
        """Создание первой формы"""
        self.clear_window()
        
        # Заголовок
        tk.Label(self.root, text="Данные студента", font=("Arial", 14)).pack(pady=10)
        
        # Поле ФИО
        tk.Label(self.root, text="ФИО:").pack()
        tk.Entry(self.root, textvariable=self.full_name, width=30).pack(pady=5)
        
        # Поле Номер группы
        tk.Label(self.root, text="Номер группы:").pack()
        tk.Entry(self.root, textvariable=self.group_number, width=30).pack(pady=5)
        
        # Кнопки
        tk.Button(self.root, text="Старт", command=self.show_form2).pack(pady=10, side=tk.LEFT, padx=20)
        tk.Button(self.root, text="Выход", command=self.root.quit).pack(pady=10, side=tk.RIGHT, padx=20)
    
    def create_form2(self):
        """Создание второй формы"""
        self.clear_window()
        
        # Заголовок с номером группы
        group_label = f"Группа: {self.group_number.get()}"
        tk.Label(self.root, text=group_label, font=("Arial", 14)).pack(pady=10)
        
        # Разделение ФИО на составные части
        full_name = self.full_name.get().split()
        last_name = full_name[0] if len(full_name) > 0 else ""
        first_name = full_name[1] if len(full_name) > 1 else ""
        middle_name = full_name[2] if len(full_name) > 2 else ""
        
        # Отображение ФИО
        tk.Label(self.root, text=f"Фамилия: {last_name}").pack()
        tk.Label(self.root, text=f"Имя: {first_name}").pack()
        tk.Label(self.root, text=f"Отчество: {middle_name}").pack(pady=10)
        
        # Текущая дата и время
        now = datetime.now()
        tk.Label(self.root, text=f"Сейчас: {now.strftime('%Y-%m-%d %H:%M:%S')}").pack(pady=10)
        
        # Кнопки
        tk.Button(self.root, text="Сообщение о создателе программы", 
                 command=self.show_creator).pack(pady=5, fill=tk.X, padx=20)
        tk.Button(self.root, text="Описание картинки 1", 
                 command=lambda: self.show_image_desc(1)).pack(pady=5, fill=tk.X, padx=20)
        tk.Button(self.root, text="Описание картинки 2", 
                 command=lambda: self.show_image_desc(2)).pack(pady=5, fill=tk.X, padx=20)
        tk.Button(self.root, text="Выход", command=self.root.quit).pack(pady=10, fill=tk.X, padx=20)
    
    def show_form2(self):
        """Проверка данных и переход ко второй форме"""
        if not self.full_name.get() or not self.group_number.get():
            messagebox.showerror("Ошибка", "Пожалуйста, заполните все поля")
            return
        self.create_form2()
    
    def show_creator(self):
        """Показать информацию о создателе"""
        messagebox.showinfo("Создатель", "Эта программа была создана студентом для учебного проекта.")
    
    def show_image_desc(self, image_num):
        """Показать описание картинки"""
        if image_num == 1:
            messagebox.showinfo("Описание картинки 1", "Это первая картинка с примером изображения.")
        else:
            messagebox.showinfo("Описание картинки 2", "Это вторая картинка с примером изображения.")
    
    def clear_window(self):
        """Очистка окна от всех виджетов"""
        for widget in self.root.winfo_children():
            widget.destroy()

# Создание и запуск приложения
if __name__ == "__main__":
    root = tk.Tk()
    app = StudentApp(root)
    root.mainloop()