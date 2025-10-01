import tkinter as tk
from tkinter import filedialog, messagebox
import pdfplumber
import pandas as pd
import re

correct_answers = {}
marks = {}
entries = {}
students_data = []  

all_choices = ["A", "B", "C", "D"]

def get_missing_choice(student_answer):
    """
    إرجاع الحرف الوحيد المفقود من إجابة الطالب.
    إذا كان هناك حرفان مفقودان أو أكثر أو لا يوجد مفقود وحيد -> ترجع None
    """
    answers = [x.strip().upper() for x in student_answer.split() if x.strip()]
    missing = [c for c in all_choices if c not in answers]
    if len(missing) == 1:
        return missing[0]
    else:
        return None  

# ------------------------
# تحميل ملف الإجابات الصحيحة
# ------------------------
def load_correct_file():
    global correct_answers, marks, entries
    file_path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
    if not file_path:
        return

    correct_answers = {}
    marks = {}
    entries = {}

    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            if ":" in line:
                q, ans = line.strip().split(":")
                correct_answers[q.strip()] = ans.strip().upper()
                marks[q.strip()] = 1  

    for widget in answers_frame.winfo_children():
        widget.destroy()

    row = 0
    for q, ans in correct_answers.items():
        tk.Label(answers_frame, text=f"{q}").grid(row=row, column=0, padx=5, pady=3, sticky="w")
        tk.Label(answers_frame, text=f"الإجابة الصحيحة: {ans}").grid(row=row, column=1, padx=5, pady=3, sticky="w")

        entry = tk.Entry(answers_frame, width=5)
        entry.insert(0, str(marks[q]))
        entry.grid(row=row, column=2, padx=5, pady=3)
        entries[q] = entry
        row += 1

    messagebox.showinfo("تم", "تم تحميل وعرض الإجابات الصحيحة")

def save_marks():
    global marks
    for q, entry in entries.items():
        try:
            marks[q] = int(entry.get())
        except:
            marks[q] = 1
            entry.delete(0, tk.END)
            entry.insert(0, "1")
    messagebox.showinfo("تم", "تم تحديث العلامات")

# ------------------------
# تحميل ملف الطلبة (PDF) + عرض النتائج
# ------------------------
def load_students_file():
    global students_data
    if not correct_answers:
        messagebox.showerror("خطأ", "يجب أولاً تحميل ملف الإجابات الصحيحة")
        return

    file_path = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
    if not file_path:
        return

    students_data = []
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if not text:
                continue
            lines = text.split("\n")

            file_num = ""
            answers = {}

            for line in lines:
                if re.match(r"^\d{5,}$", line.strip()):
                    file_num = line.strip()
                elif line.strip().startswith("Q"):
                    if ":" in line:
                        q, ans = line.split(":")
                        answers[q.strip()] = ans.strip().upper()

            if file_num:
                students_data.append({"رقم الملف": file_num, "الإجابات": answers})

    show_students_results()

    if students_data:
        messagebox.showinfo("تم", f"تم تحميل بيانات {len(students_data)} طالب")
    else:
        messagebox.showerror("خطأ", "لم يتم العثور على بيانات الطلبة")

def show_students_results():
    for widget in students_content.winfo_children():
        widget.destroy()

    row = 0
    for student in students_data:
        file_num = student["رقم الملف"]
        answers = student["الإجابات"]
        tk.Label(students_content, text=f"📌 الطالب: {file_num}", fg="blue", font=("Arial", 10, "bold")).grid(row=row, column=0, sticky="w", pady=5)
        row += 1

        total_score = 0
        for q, correct in correct_answers.items():
            student_ans = answers.get(q, "")
            missing = get_missing_choice(student_ans)
            score = 0
            if missing is not None and missing == correct:
                score = marks.get(q, 1)
                total_score += score
            display_missing = missing if missing is not None else "-"
            tk.Label(students_content, text=f"{q} = {score} (المفقود: {display_missing})").grid(row=row, column=1, sticky="w")
            row += 1

        tk.Label(students_content, text=f"إجمالي الدرجة: {total_score}", fg="green").grid(row=row, column=0, sticky="w", pady=3)
        row += 2

# ------------------------
# حفظ النتائج في ملف Excel
# ------------------------
def save_results_to_excel():
    if not students_data:
        messagebox.showerror("خطأ", "لم يتم تحميل بيانات الطلبة بعد")
        return

    save_path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel Files", "*.xlsx")])
    if not save_path:
        return

    all_records = []
    for student in students_data:
        record = {"رقم الملف": student["رقم الملف"]}
        answers = student["الإجابات"]
        total_score = 0
        for q, correct in correct_answers.items():
            student_ans = answers.get(q, "")
            missing = get_missing_choice(student_ans)
            score = 0
            if missing is not None and missing == correct:
                score = marks.get(q, 1)
                total_score += score
            record[q] = score
            record[f"{q}_المفقود"] = missing if missing is not None else ""
        record["إجمالي الدرجة"] = total_score
        all_records.append(record)

    df = pd.DataFrame(all_records)
    cols = ["رقم الملف"]
    for q in sorted(correct_answers.keys(), key=lambda x: int(re.sub(r'\D','',x))):
        cols.append(q)
        cols.append(f"{q}_المفقود")
    cols.append("إجمالي الدرجة")
    df = df[cols]
    df.to_excel(save_path, index=False)
    messagebox.showinfo("تم", f"تم حفظ النتائج في ملف Excel:\n{save_path}")

# ------------------------
# واجهة المستخدم مع Scrollbar
# ------------------------
root = tk.Tk()
root.title("برنامج التصحيح - عرض نتائج الطلاب")
root.geometry("750x600")

btn1 = tk.Button(root, text="تحميل ملف الإجابات الصحيحة (TXT)", command=load_correct_file, width=40)
btn1.pack(pady=10)

answers_frame = tk.Frame(root)
answers_frame.pack(pady=10, fill="both", expand=True)

btn2 = tk.Button(root, text="تحميل ملف إجابات الطلبة (PDF)", command=load_students_file, width=40)
btn2.pack(pady=10)

btn3 = tk.Button(root, text="تحديث العلامات", command=save_marks, width=40)
btn3.pack(pady=10)

btn4 = tk.Button(root, text="حفظ النتائج في Excel", command=save_results_to_excel, width=40, bg="lightgreen")
btn4.pack(pady=10)

students_canvas = tk.Canvas(root)
scrollbar = tk.Scrollbar(root, orient="vertical", command=students_canvas.yview)
students_canvas.configure(yscrollcommand=scrollbar.set)

scrollbar.pack(side="right", fill="y")
students_canvas.pack(side="left", fill="both", expand=True)

students_frame = tk.Frame(students_canvas)
students_canvas.create_window((0, 0), window=students_frame, anchor="nw")

students_content = tk.Frame(students_frame)
students_content.pack(fill="both", expand=True)

def on_frame_configure(event):
    students_canvas.configure(scrollregion=students_canvas.bbox("all"))

students_frame.bind("<Configure>", on_frame_configure)

root.mainloop()
