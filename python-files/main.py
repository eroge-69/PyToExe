from tkinter import Tk, Label, Button, Entry, Radiobutton, StringVar
import datetime

class FacultyTeacherJournal:
    def __init__(self, master):
        self.master = master
        master.title("Преподавательский журнал факультета")
        master.config(bg='#add8e6')
        self.setup_ui()

        self.student_data = {
            "Класс 1": ["Иванов И.И.", "Петров П.П.", "Сидоров С.С."],
            "Класс 2": ["Алексеев А.А.", "Борисов Б.Б.", "Викторов В.В."],
            "Класс 3": ["Глебов Г.Г.", "Денисов Д.Д.", "Ефимов Е.Е."]
        }
        self.grade_entries = {}

    def setup_ui(self):
        self.welcome_label = Label(self.master, text="Добро пожаловать в ваш журнал!", bg='#add8e6', font=("Helvetica", 14))
        self.welcome_label.pack(pady=20)

        self.group_select_button = Button(self.master, text="Выбор класса", command=self.choose_class)
        self.group_select_button.pack(pady=10)

    def choose_class(self):
        self.welcome_label.pack_forget()
        self.group_select_button.pack_forget()

        self.class_label = Label(self.master, text="Выберите класс:", bg='#add8e6', font=("Helvetica", 12))
        self.class_label.pack(pady=10)

        self.class_var = StringVar()
        for class_name in self.student_data.keys():
            rb = Radiobutton(self.master, text=class_name, variable=self.class_var, value=class_name, command=self.display_students, bg='#add8e6')
            rb.pack(pady=5)

    def display_students(self):
        selected_class = self.class_var.get()
        if selected_class:
            self.input_grades(selected_class)

    def input_grades(self, selected_class):
        self.class_label.pack_forget()
        for widget in self.master.pack_slaves():
            widget.pack_forget()

        for student in self.student_data[selected_class]:
            student_label = Label(self.master, text=f"Оценка {student}:", bg='#add8e6', font=("Helvetica", 12))
            student_label.pack(pady=10)
            grade_entry = Entry(self.master)
            grade_entry.pack(pady=10)
            self.grade_entries[student] = grade_entry

        grades_save_button = Button(self.master, text="Записать оценки", command=self.record_grades)
        grades_save_button.pack(pady=20)

    def record_grades(self):
        recorded_data = {student: entry.get() for student, entry in self.grade_entries.items()}
        file_name = "grades_" + datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + ".txt"
        with open(file_name, "w") as file:
            for student, grade in recorded_data.items():
                file.write(f"{student}: {grade}\n")
                print(f"{student}: {grade}")
        for entry in self.grade_entries.values():
            entry.delete(0, 'end')

main_window = Tk()
journal_app = FacultyTeacherJournal(main_window)
main_window.mainloop()
