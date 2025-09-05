import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
from statistics import mean
import csv

# Subjects
subjects = [
    "Buddhism", "Sinhala", "Maths", "Science", "English", "Tamil",
    "Health", "Civic", "Geography", "History", "Aesthetic", "PTS"
]

students = []
student_marks = {}

# ------------------ Core Functions ------------------

def calculate_results(marks, student_name="Student"):
    total = sum(marks.values())
    average = mean(marks.values())
    grade_boundaries = {"A+": 90, "A": 75, "B": 65, "C": 55, "S": 35, "W": 0}
    grade = next(g for g, bound in grade_boundaries.items() if average >= bound)
    return {"name": student_name, "marks": marks, "total": total,
            "average": round(average, 2), "grade": grade}

def assign_ranks(students_results):
    sorted_students = sorted(students_results, key=lambda x: (-x['total'], -x['average']))
    current_rank = 1
    last_total = None
    last_average = None
    for i, student in enumerate(sorted_students, start=1):
        if student['total'] == last_total and student['average'] == last_average:
            student["rank"] = current_rank
        else:
            student["rank"] = i
            current_rank = i
            last_total = student['total']
            last_average = student['average']
    return sorted_students

def highest_in_each_subject(students_results):
    top_scorers = {}
    for subject in subjects:
        max_mark = max(s['marks'][subject] for s in students_results)
        top_students = [s['name'] for s in students_results if s['marks'][subject] == max_mark]
        top_scorers[subject] = {"students": top_students, "marks": max_mark}
    return top_scorers

def export_to_csv(students_results):
    file = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files","*.csv")])
    if not file:
        return
    headers = ["Rank", "Name"] + subjects + ["Total", "Average", "Grade"]
    with open(file, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        for s in students_results:
            row = [s['rank'], s['name']] + [s['marks'][sub] for sub in subjects] + [
                s['total'], s['average'], s['grade']
            ]
            writer.writerow(row)
    messagebox.showinfo("Exported", f"Results saved to {file}")

# ------------------ GUI Functions ------------------

def add_names():
    global students, student_marks
    try:
        num = int(simpledialog.askstring("Number of Students", "Enter number of students:"))
        if num <= 0:
            raise ValueError
    except (TypeError, ValueError):
        messagebox.showerror("Error", "Please enter a valid number.")
        return

    students = []
    student_marks = {}
    for i in range(num):
        name = simpledialog.askstring("Student Name", f"Enter name of student {i+1}:")
        if not name:
            name = f"Student{i+1}"
        students.append(name)
        student_marks[name] = {}
    update_student_list()
    messagebox.showinfo("Done", "All student names added.\nNow enter marks subject by subject.")

def enter_marks():
    if not students:
        messagebox.showerror("Error", "Please add student names first.")
        return

    for subject in subjects:
        for name in students:
            while True:
                mark = simpledialog.askstring("Enter Marks", f"{subject} - {name} (0–100):")
                if mark is None:
                    return  # cancel
                try:
                    mark = int(mark)
                    if 0 <= mark <= 100:
                        student_marks[name][subject] = mark
                        break
                    else:
                        messagebox.showerror("Error", "Marks must be between 0 and 100.")
                except ValueError:
                    messagebox.showerror("Error", "Enter a valid number.")

    calculate_and_show_results()

def calculate_and_show_results():
    students_results = []
    for name in students:
        students_results.append(calculate_results(student_marks[name], name))

    ranked_students = assign_ranks(students_results)

    for row in tree.get_children():
        tree.delete(row)
    for s in ranked_students:
        values = [s['rank'], s['name']] + [s['marks'][sub] for sub in subjects] + [
            s['total'], s['average'], s['grade']
        ]
        tree.insert("", tk.END, values=values)

def show_toppers():
    if not students:
        messagebox.showinfo("Info", "No data available.")
        return
    results = []
    students_results = [calculate_results(student_marks[name], name) for name in students]
    toppers = highest_in_each_subject(assign_ranks(students_results))
    for subject, data in toppers.items():
        results.append(f"{subject}: {', '.join(data['students'])} ({data['marks']})")
    messagebox.showinfo("Top Scorers", "\n".join(results))

def update_student_list():
    listbox_students.delete(0, tk.END)
    for s in students:
        listbox_students.insert(tk.END, s)

# ------------------ GUI Layout ------------------

root = tk.Tk()
root.title("Student Results Application")
root.geometry("1300x600")

frame_buttons = tk.Frame(root)
frame_buttons.pack(side=tk.TOP, fill=tk.X, pady=5)

tk.Button(frame_buttons, text="Add Student Names", command=add_names).pack(side=tk.LEFT, padx=5)
tk.Button(frame_buttons, text="Enter Marks", command=enter_marks).pack(side=tk.LEFT, padx=5)
tk.Button(frame_buttons, text="Show Toppers", command=show_toppers).pack(side=tk.LEFT, padx=5)
tk.Button(frame_buttons, text="Export CSV", command=lambda: export_to_csv(assign_ranks(
    [calculate_results(student_marks[name], name) for name in students]))).pack(side=tk.LEFT, padx=5)

frame_side = tk.Frame(root)
frame_side.pack(side=tk.LEFT, fill=tk.Y, padx=10)

tk.Label(frame_side, text="Students", font=("Arial", 12, "bold")).pack()
listbox_students = tk.Listbox(frame_side, height=25, width=25)
listbox_students.pack(pady=5)

columns = ["Rank", "Name"] + subjects + ["Total", "Average", "Grade"]
tree = ttk.Treeview(root, columns=columns, show="headings")
for col in columns:
    tree.heading(col, text=col)
    tree.column(col, width=80)
tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

root.mainloop()
