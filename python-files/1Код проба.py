import json
import os

class Jurnal:
    def __init__(self, filename="jurnal.json"):
        self.filename = filename
        self.students = {}  # {student_id: {"name": "Имя", "grades": {subject_id: grade}}}
        self.subjects = {}  # {subject_id: "Название предмета"}
        self.load_data()

    def load_data(self):
        """Загружает данные из JSON файла."""
        if os.path.exists(self.filename):
            try:
                with open(self.filename, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.students = data.get("students", {})
                    self.subjects = data.get("subjects", {})
            except (FileNotFoundError, json.JSONDecodeError):
                print("Ошибка при загрузке данных. Начинаем с чистого листа.")

    def save_data(self):
        """Сохраняет данные в JSON файл."""
        data = {"students": self.students, "subjects": self.subjects}
        try:
            with open(self.filename, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
        except IOError:
            print("Ошибка при сохранении данных.")

    def add_student(self, student_id, name):
        """Добавляет нового ученика."""
        if student_id not in self.students:
            self.students[student_id] = {"name": name, "grades": {}}
            self.save_data()
            print(f"Ученик {name} добавлен с ID {student_id}.")
        else:
            print(f"Ученик с ID {student_id} уже существует.")

    def add_subject(self, subject_id, subject_name):
        """Добавляет новый предмет."""
        if subject_id not in self.subjects:
            self.subjects[subject_id] = subject_name
            self.save_data()
            print(f"Предмет {subject_name} добавлен с ID {subject_id}.")
        else:
            print(f"Предмет с ID {subject_id} уже существует.")

    def add_grade(self, student_id, subject_id, grade):
        """Добавляет оценку ученику по предмету."""
        if student_id in self.students and subject_id in self.subjects:
            try:
                grade = int(grade)
                if 1 <= grade <= 5: # Проверка на допустимый диапазон оценок (1-5)
                    self.students[student_id]["grades"][subject_id] = grade
                    self.save_data()
                    print(f"Оценка {grade} добавлена ученику {self.students[student_id]['name']} по предмету {self.subjects[subject_id]}.")
                else:
                    print("Оценка должна быть в диапазоне от 1 до 5.")

            except ValueError:
                print("Оценка должна быть целым числом.")
        else:
            print("Неверный ID ученика или предмета.")

    def get_grades(self, student_id):
        """Возвращает оценки ученика."""
        if student_id in self.students:
            return self.students[student_id]["grades"]
        else:
            print("Неверный ID ученика.")
            return None

    def get_average_grade(self, student_id):
        """Вычисляет средний балл ученика."""
        if student_id in self.students:
            grades = self.students[student_id]["grades"]
            if grades:
                total = sum(grades.values())
                average = total / len(grades)
                return average
            else:
                print("У ученика нет оценок.")
                return None
        else:
            print("Неверный ID ученика.")
            return None

    def print_journal(self):
        """Выводит содержимое журнала на экран."""
        print("-" * 30)
        print("Электронный журнал")
        print("-" * 30)
        if not self.students:
            print("Журнал пуст.")
            return

        for student_id, student_data in self.students.items():
            print(f"ID: {student_id}, Имя: {student_data['name']}")
            grades = student_data['grades']
            if grades:
                for subject_id, grade in grades.items():
                    print(f"  - {self.subjects[subject_id]}: {grade}")
            else:
                print("  - Нет оценок")
        print("-" * 30)

    def run(self):
        """Запускает интерактивный режим журнала."""
        while True:
            print("\nМеню:")
            print("1. Добавить ученика")
            print("2. Добавить предмет")
            print("3. Добавить оценку")
            print("4. Показать оценки ученика")
            print("5. Показать средний балл ученика")
            print("6. Вывести журнал")
            print("7. Выйти")

            choice = input("Выберите действие: ")

            if choice == "1":
                student_id = input("Введите ID ученика: ")
                name = input("Введите имя ученика: ")
                self.add_student(student_id, name)
            elif choice == "2":
                subject_id = input("Введите ID предмета: ")
                subject_name = input("Введите название предмета: ")
                self.add_subject(subject_id, subject_name)
            elif choice == "3":
                student_id = input("Введите ID ученика: ")
                subject_id = input("Введите ID предмета: ")
                grade = input("Введите оценку: ")
                self.add_grade(student_id, subject_id, grade)
            elif choice == "4":
                student_id = input("Введите ID ученика: ")
                grades = self.get_grades(student_id)
                if grades:
                    print(f"Оценки ученика {self.students[student_id]['name']}: {grades}")
            elif choice == "5":
                student_id = input("Введите ID ученика: ")
                average = self.get_average_grade(student_id)
                if average:
                    print(f"Средний балл ученика {self.students[student_id]['name']}: {average}")
            elif choice == "6":
                self.print_journal()
            elif choice == "7":
                print("Выход из программы.")
                break
            else:
                print("Неверный выбор. Попробуйте еще раз.")


# Пример использования
if __name__ == "__main__":
    journal = Jurnal()
    journal.run()
