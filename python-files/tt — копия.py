import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import csv


class StudentFilterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Student Filter App")
        self.root.geometry("500x300")


        self.students = []
        self.selected_students = []
        self.headers = []


        self.create_widgets()

    def create_widgets(self):

        style = ttk.Style()
        style.configure("TButton", padding=6, font=('Arial', 10))


        frame = ttk.Frame(self.root, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)


        btn_db = ttk.Button(
            frame,
            text="Загрузить базу данных (CSV)",
            command=self.load_database
        )
        btn_db.pack(fill=tk.X, pady=5)


        btn_list = ttk.Button(
            frame,
            text="Загрузить список студентов (TXT)",
            command=self.load_student_list
        )
        btn_list.pack(fill=tk.X, pady=5)


        btn_report = ttk.Button(
            frame,
            text="Создать отчет (CSV)",
            command=self.create_report,
            state=tk.DISABLED
        )
        btn_report.pack(fill=tk.X, pady=5)
        self.btn_report = btn_report


        self.status = tk.StringVar()
        self.status.set("Ожидание загрузки данных")
        status_bar = ttk.Label(
            self.root,
            textvariable=self.status,
            relief=tk.SUNKEN,
            anchor=tk.W
        )
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def load_database(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("CSV files", "*.csv")]
        )
        if not file_path:
            return

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                self.headers = next(reader)  # Читаем заголовки
                self.students = list(reader)

            self.status.set(f"Загружено студентов: {len(self.students)}")
            self.check_data_loaded()

        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка загрузки CSV:\n{str(e)}")

    def load_student_list(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Text files", "*.txt")]
        )
        if not file_path:
            return

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                self.selected_students = [
                    line.strip() for line in f if line.strip()
                ]

            self.status.set(f"Загружено имен для фильтра: {len(self.selected_students)}")
            self.check_data_loaded()

        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка загрузки TXT:\n{str(e)}")

    def check_data_loaded(self):
        if self.students and self.selected_students:
            self.btn_report.config(state=tk.NORMAL)
            self.status.set("Данные загружены. Готов к созданию отчета")

    def create_report(self):
        if not self.students or not self.selected_students:
            return

        save_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")]
        )
        if not save_path:
            return

        try:

            selected_set = {name.lower() for name in self.selected_students}


            filtered_students = []
            for student in self.students:

                full_name = student[0].strip().lower()
                if full_name in selected_set:
                    filtered_students.append(student)

            
            with open(save_path, 'w', encoding='utf-8', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(self.headers)
                writer.writerows(filtered_students)

            self.status.set(f"Сохранено студентов: {len(filtered_students)}")
            messagebox.showinfo(
                "Успех",
                f"Отчет создан успешно!\nСохранено записей: {len(filtered_students)}"
            )

        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка создания отчета:\n{str(e)}")


if __name__ == "__main__":
    root = tk.Tk()
    app = StudentFilterApp(root)
    root.mainloop()