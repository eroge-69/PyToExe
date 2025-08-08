import tkinter as tk
from tkinter import simpledialog, messagebox



class OptionsWindow:
    def __init__(self, master, manager):
        self.manager = manager
        self.window = tk.Toplevel(master)
        self.window.title("Student Manager Options")
        self.window.geometry("350x300")

        tk.Label(self.window, text="Choose an option:").pack(pady=10)
        tk.Button(self.window, text="Add Student", command=self.add_student).pack(fill='x', padx=20, pady=5)
        tk.Button(self.window, text="Show All Students Info", command=self.show_students_info).pack(fill='x', padx=20, pady=5)
        tk.Button(self.window, text="Show Best Student", command=self.show_best_student).pack(fill='x', padx=20, pady=5)
        tk.Button(self.window, text="Exit", command=self.window.destroy).pack(fill='x', padx=20, pady=20)

    def add_student(self):
        name = simpledialog.askstring("Input", "Enter student name:", parent=self.window)
        if not name:
            return
        age = simpledialog.askinteger("Input", "Enter student age:", parent=self.window)
        if age is None:
            return
        grades_str = simpledialog.askstring("Input", "Enter grades:", parent=self.window)
        if not grades_str:
            return
        try:
            grades = [int(g.strip()) for g in grades_str.split(',') if g.strip()]
        except ValueError:
            messagebox.showerror("Error", "Invalid grades input.")
            return
        student = Student(name, age, *grades)
        self.manager.add_student(student)
        messagebox.showinfo("Success", f"Added student {name}.")

    def show_students_info(self):
        students = [s for s in self.manager.students if isinstance(s, Student)]
        if not students:
            messagebox.showinfo("Info", "No students to show.")
            return
        info = "\n".join([f"Name: {s.name}, Age: {s.age}, Grades: {s.grades}" for s in students])
        messagebox.showinfo("All Students", info)

    def show_best_student(self):
        students = [s for s in self.manager.students if isinstance(s, Student) and s.grades]
        if not students:
            messagebox.showinfo("Info", "No students to evaluate.")
            return
        best = max(students, key=lambda s: sum(s.grades)/len(s.grades))
        avg = sum(best.grades)/len(best.grades)
        messagebox.showinfo("Best Student", f"Best student: {best.name}\nAverage: {avg}")
class Student:
    def __init__(self,name,age,*grades):
        self.name=name
        self.age=age
        self.grades=list(grades)
    def average(self):
        average=sum(self.grades)/len(self.grades)
        print(average)
    def status(self):
        average = sum(self.grades) / len(self.grades)
        if 18 <= average <= 20:
            print("Your status in your grades are great")
        elif 15 <= average < 18:
            print("Your status in Your grades are medium")
        elif 12 <= average < 15:
            print("Your status in Your grades are bad")
        elif 8 <= average < 12:
            print("Your status in Your grades are very bad Youve FAILED")
        else:
            print("No status for this average.")
class Manager(Student):
   
    def __init__(self, name, age, *grades, students=None):
        super().__init__(name, age, *grades)
        if students is None:
            self.students = []
        else:
            self.students = list(students)
    def Show_Students_Info(self):
        print(f"His name is{self.name}his age is{self.age} ")
    def add_student(self, student):
        self.students.append(student)
        print(f"The new Student is {self.students} ")
    def best_student(self):
        students = [s for s in self.students if isinstance(s, Student) and s.grades]
        if students:
            best = max(students, key=lambda s: sum(s.grades)/len(s.grades))
            print(f"Best student: {best.name} with average {sum(best.grades)/len(best.grades)}")
        else:
            print("No students to Calculate")
    def main():
        root = tk.Tk()
        root.withdraw()  
        manager = Manager("Manager", 0)
        OptionsWindow(root, manager)
        root.mainloop()

        if __name__ == "__main__":
            main()


        
        


        
        
        
        


        
