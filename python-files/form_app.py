import tkinter as tk
from tkinter import messagebox, filedialog
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import os

class FormApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Форма для заполнения")
        self.root.geometry("500x650")
        
        # Переменные для хранения данных
        self.data = {
            "full_name": tk.StringVar(),
            "birth_date": tk.StringVar(),
            "email": tk.StringVar(),
            "phone": tk.StringVar(),
            "gender": tk.StringVar(value="М"),
            "education": tk.StringVar(value="Среднее"),
            "interests": [],
            "experience": tk.StringVar()
        }
        
        # Создание формы
        self.create_form()
        
    def create_form(self):
        # Основной фрейм с прокруткой
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Заголовок
        tk.Label(main_frame, text="Анкета", font=("Arial", 16, "bold")).grid(row=0, column=0, columnspan=2, pady=10)
        
        # Поля формы
        fields = [
            ("ФИО:", "full_name", 1),
            ("Дата рождения (ДД.ММ.ГГГГ):", "birth_date", 2),
            ("Email:", "email", 3),
            ("Телефон:", "phone", 4),
            ("Пол:", "gender", 5),
            ("Образование:", "education", 6),
            ("Интересы:", "interests", 7),
            ("Опыт работы:", "experience", 9)
        ]
        
        row_counter = 1
        for label_text, field_name, row in fields:
            if field_name == "gender":
                tk.Label(main_frame, text=label_text).grid(row=row, column=0, sticky="w", pady=5)
                tk.Radiobutton(main_frame, text="Мужской", variable=self.data["gender"], value="М").grid(row=row, column=1, sticky="w")
                tk.Radiobutton(main_frame, text="Женский", variable=self.data["gender"], value="Ж").grid(row=row+1, column=1, sticky="w")
                row_counter += 1
            elif field_name == "education":
                tk.Label(main_frame, text=label_text).grid(row=row, column=0, sticky="w", pady=5)
                education_options = ["Среднее", "Среднее специальное", "Неоконченное высшее", "Высшее", "Ученая степень"]
                tk.OptionMenu(main_frame, self.data["education"], *education_options).grid(row=row, column=1, sticky="ew")
            elif field_name == "interests":
                tk.Label(main_frame, text=label_text).grid(row=row, column=0, sticky="w", pady=5)
                interests_frame = tk.Frame(main_frame)
                interests_frame.grid(row=row, column=1, sticky="w")
                
                interests = ["Программирование", "Дизайн", "Маркетинг", "Аналитика", "Управление"]
                self.interest_vars = []
                for i, interest in enumerate(interests):
                    var = tk.IntVar()
                    cb = tk.Checkbutton(interests_frame, text=interest, variable=var)
                    cb.pack(anchor="w")
                    self.interest_vars.append((interest, var))
            elif field_name == "experience":
                tk.Label(main_frame, text=label_text).grid(row=row, column=0, sticky="nw", pady=5)
                self.experience_text = tk.Text(main_frame, width=30, height=4, wrap=tk.WORD)
                self.experience_text.grid(row=row, column=1, sticky="ew")
            else:
                tk.Label(main_frame, text=label_text).grid(row=row, column=0, sticky="w", pady=5)
                tk.Entry(main_frame, textvariable=self.data[field_name], width=30).grid(row=row, column=1, sticky="ew")
            
            row_counter = row + 1
        
        # Кнопки
        buttons_frame = tk.Frame(main_frame)
        buttons_frame.grid(row=row_counter+1, column=0, columnspan=2, pady=20)
        
        tk.Button(buttons_frame, text="Отправить", command=self.submit_form).pack(side=tk.LEFT, padx=5)
        tk.Button(buttons_frame, text="Экспорт в PDF", command=self.export_to_pdf).pack(side=tk.LEFT, padx=5)
        tk.Button(buttons_frame, text="Очистить", command=self.clear_form).pack(side=tk.LEFT, padx=5)
    
    def validate_form(self):
        # Проверка ФИО
        if not self.data["full_name"].get().strip():
            messagebox.showerror("Ошибка", "Поле 'ФИО' обязательно для заполнения")
            return False
        
        # Проверка даты рождения
        try:
            birth_date = datetime.strptime(self.data["birth_date"].get(), "%d.%m.%Y")
            if birth_date > datetime.now():
                messagebox.showerror("Ошибка", "Дата рождения не может быть в будущем")
                return False
        except ValueError:
            messagebox.showerror("Ошибка", "Некорректный формат даты. Используйте ДД.ММ.ГГГГ")
            return False
        
        # Проверка email
        email = self.data["email"].get()
        if email and "@" not in email:
            messagebox.showerror("Ошибка", "Некорректный email адрес")
            return False
        
        # Проверка телефона
        phone = self.data["phone"].get()
        if phone and not phone.replace("+", "").replace(" ", "").isdigit():
            messagebox.showerror("Ошибка", "Некорректный номер телефона")
            return False
        
        return True
    
    def collect_form_data(self):
        # Собираем данные формы в словарь
        form_data = {
            "full_name": self.data["full_name"].get(),
            "birth_date": self.data["birth_date"].get(),
            "email": self.data["email"].get(),
            "phone": self.data["phone"].get(),
            "gender": "Мужской" if self.data["gender"].get() == "М" else "Женский",
            "education": self.data["education"].get(),
            "interests": [interest for interest, var in self.interest_vars if var.get() == 1],
            "experience": self.experience_text.get("1.0", tk.END).strip()
        }
        return form_data
    
    def submit_form(self):
        if not self.validate_form():
            return
        
        form_data = self.collect_form_data()
        
        # Сохранение в текстовый файл
        try:
            with open("form_data.txt", "a", encoding="utf-8") as f:
                f.write(self.format_form_data(form_data) + "\n" + "="*50 + "\n")
            messagebox.showinfo("Успех", "Данные успешно сохранены в текстовый файл!")
            self.clear_form()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить данные: {str(e)}")
    
    def export_to_pdf(self):
        if not self.validate_form():
            return
        
        form_data = self.collect_form_data()
        
        # Диалог выбора места сохранения
        file_path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF файлы", "*.pdf")],
            title="Сохранить как PDF"
        )
        
        if not file_path:
            return  # Пользователь отменил сохранение
        
        try:
            # Создаем PDF документ
            c = canvas.Canvas(file_path, pagesize=letter)
            width, height = letter
            
            # Заголовок
            c.setFont("Helvetica-Bold", 16)
            c.drawString(100, height - 100, "Анкета")
            c.line(100, height - 105, 300, height - 105)
            
            # Данные формы
            c.setFont("Helvetica", 12)
            y_position = height - 140
            
            # Форматируем данные для PDF
            pdf_data = [
                ("ФИО:", form_data["full_name"]),
                ("Дата рождения:", form_data["birth_date"]),
                ("Email:", form_data["email"]),
                ("Телефон:", form_data["phone"]),
                ("Пол:", form_data["gender"]),
                ("Образование:", form_data["education"]),
                ("Интересы:", ", ".join(form_data["interests"]) if form_data["interests"] else "Нет"),
                ("Опыт работы:", "")
            ]
            
            # Добавляем данные в PDF
            for label, value in pdf_data:
                c.drawString(100, y_position, f"{label} {value}")
                y_position -= 25
            
            # Опыт работы (может быть многострочным)
            experience_lines = form_data["experience"].split('\n')
            c.drawString(100, y_position, "Опыт работы:")
            y_position -= 20
            
            c.setFont("Helvetica", 10)
            for line in experience_lines:
                if y_position < 100:  # Если осталось мало места, создаем новую страницу
                    c.showPage()
                    y_position = height - 50
                    c.setFont("Helvetica", 10)
                c.drawString(120, y_position, line)
                y_position -= 15
            
            # Подпись и дата
            c.setFont("Helvetica", 10)
            c.drawString(100, 80, f"Дата заполнения: {datetime.now().strftime('%d.%m.%Y %H:%M')}")
            
            c.save()
            messagebox.showinfo("Успех", f"Данные успешно экспортированы в PDF:\n{file_path}")
            
            # Открываем PDF после сохранения (если система поддерживает)
            if os.name == 'nt':  # Для Windows
                os.startfile(file_path)
            elif os.name == 'posix':  # Для MacOS и Linux
                os.system(f'open "{file_path}"' if sys.platform == 'darwin' else f'xdg-open "{file_path}"')
                
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось создать PDF: {str(e)}")
    
    def format_form_data(self, form_data):
        result = "Данные формы:\n\n"
        result += f"ФИО: {form_data['full_name']}\n"
        result += f"Дата рождения: {form_data['birth_date']}\n"
        result += f"Email: {form_data['email']}\n"
        result += f"Телефон: {form_data['phone']}\n"
        result += f"Пол: {form_data['gender']}\n"
        result += f"Образование: {form_data['education']}\n"
        result += f"Интересы: {', '.join(form_data['interests']) if form_data['interests'] else 'Нет'}\n"
        result += f"Опыт работы:\n{form_data['experience']}\n"
        return result
    
    def clear_form(self):
        for field in self.data:
            if isinstance(self.data[field], tk.StringVar):
                self.data[field].set("")
        
        for _, var in self.interest_vars:
            var.set(0)
        
        self.experience_text.delete("1.0", tk.END)
        self.data["gender"].set("М")
        self.data["education"].set("Среднее")

if __name__ == "__main__":
    root = tk.Tk()
    app = FormApp(root)
    root.mainloop()