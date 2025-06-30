Python 3.13.5 (tags/v3.13.5:6cb20a2, Jun 11 2025, 16:15:46) [MSC v.1943 64 bit (AMD64)] on win32
Enter "help" below or click "Help" above for more information.
import tkinter as tk
from tkinter import ttk, messagebox
from tc import Student

class AcademicRecordApp:
    def __init__(self, root):
        self.root = root
        self.root.title("نظام السجل الأكاديمي للطالب")
        self.root.geometry("900x700")
        self.root.resizable(False, False)
        
        # إنشاء طالب جديد
        self.student = None
        
        # إنشاء واجهة المستخدم
        self.create_widgets()
        
    def create_widgets(self):
        # إطار معلومات الطالب
        student_frame = ttk.LabelFrame(self.root, text="معلومات الطالب")
        student_frame.pack(pady=10, padx=10, fill="x")
        
        ttk.Label(student_frame, text="اسم الطالب:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.name_entry = ttk.Entry(student_frame, width=30)
        self.name_entry.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(student_frame, text="رقم الهوية:").grid(row=0, column=2, padx=5, pady=5, sticky="e")
        self.id_entry = ttk.Entry(student_frame, width=20)
        self.id_entry.grid(row=0, column=3, padx=5, pady=5)
        
        ttk.Button(student_frame, text="إنشاء سجل جديد", command=self.create_student).grid(row=0, column=4, padx=10)
        
        # إطار إضافة مواد
        add_course_frame = ttk.LabelFrame(self.root, text="إضافة مادة دراسية")
        add_course_frame.pack(pady=10, padx=10, fill="x")
        
        ttk.Label(add_course_frame, text="السنة الدراسية:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.year_combo = ttk.Combobox(add_course_frame, values=[1, 2, 3, 4], width=5)
        self.year_combo.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        
        ttk.Label(add_course_frame, text="الترم الدراسي:").grid(row=0, column=2, padx=5, pady=5, sticky="e")
        self.term_combo = ttk.Combobox(add_course_frame, values=[1, 2, 3], width=5)
        self.term_combo.grid(row=0, column=3, padx=5, pady=5, sticky="w")
        
        ttk.Label(add_course_frame, text="اسم المادة:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.course_entry = ttk.Entry(add_course_frame, width=30)
        self.course_entry.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        
        ttk.Label(add_course_frame, text="الدرجة:").grid(row=1, column=2, padx=5, pady=5, sticky="e")
        self.grade_combo = ttk.Combobox(add_course_frame, 
                                      values=["A+", "A", "A-", "B+", "B", "B-", "C+", "C", "C-", "D+", "D", "F"])
        self.grade_combo.grid(row=1, column=3, padx=5, pady=5, sticky="w")
        
        ttk.Label(add_course_frame, text="الساعات المعتمدة:").grid(row=1, column=4, padx=5, pady=5, sticky="e")
        self.credit_spin = ttk.Spinbox(add_course_frame, from_=1, to=10, width=5)
        self.credit_spin.grid(row=1, column=5, padx=5, pady=5, sticky="w")
        
        ttk.Button(add_course_frame, text="إضافة المادة", command=self.add_course).grid(row=1, column=6, padx=10)
        
        # إطار عرض السجل الأكاديمي
        record_frame = ttk.LabelFrame(self.root, text="السجل الأكاديمي")
        record_frame.pack(pady=10, padx=10, fill="both", expand=True)
        
        self.tree = ttk.Treeview(record_frame, columns=("Year", "Term", "Course", "Grade", "Credits"), show="headings")
        self.tree.heading("Year", text="السنة")
        self.tree.heading("Term", text="الترم")
        self.tree.heading("Course", text="المادة")
        self.tree.heading("Grade", text="الدرجة")
        self.tree.heading("Credits", text="الساعات")
        
        self.tree.column("Year", width=50, anchor="center")
        self.tree.column("Term", width=50, anchor="center")
        self.tree.column("Course", width=300)
        self.tree.column("Grade", width=70, anchor="center")
        self.tree.column("Credits", width=70, anchor="center")
        
        scrollbar = ttk.Scrollbar(record_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # إطار المعلومات الإحصائية
        stats_frame = ttk.LabelFrame(self.root, text="المعلومات الإحصائية")
        stats_frame.pack(pady=10, padx=10, fill="x")
        
        ttk.Button(stats_frame, text="حساب معدل الترم", command=self.calculate_term_gpa).grid(row=0, column=0, padx=5)
        ttk.Button(stats_frame, text="حساب معدل السنة", command=self.calculate_year_gpa).grid(row=0, column=1, padx=5)
        ttk.Button(stats_frame, text="حساب المعدل التراكمي", command=self.calculate_cumulative_gpa).grid(row=0, column=2, padx=5)
        
        self.stats_label = ttk.Label(stats_frame, text="", font=('TkDefaultFont', 10, 'bold'))
        self.stats_label.grid(row=1, column=0, columnspan=3, pady=10)
        
    def create_student(self):
        name = self.name_entry.get()
        student_id = self.id_entry.get()
        
        if name and student_id:
            self.student = Student(name, student_id)
            messagebox.showinfo("نجاح", "تم إنشاء سجل الطالب بنجاح")
            self.update_record()
        else:
            messagebox.showerror("خطأ", "الرجاء إدخال اسم الطالب ورقم الهوية")
    
    def add_course(self):
        if not self.student:
            messagebox.showerror("خطأ", "الرجاء إنشاء سجل الطالب أولاً")
            return
            
        try:
            year = int(self.year_combo.get())
            term = int(self.term_combo.get())
            course = self.course_entry.get()
            grade = self.grade_combo.get()
            credits = int(self.credit_spin.get())
            
            if not all([year, term, course, grade]):
                messagebox.showerror("خطأ", "الرجاء ملء جميع الحقول")
                return
                
            self.student.add_course(year, term, course, grade, credits)
            messagebox.showinfo("نجاح", "تمت إضافة المادة بنجاح")
            self.update_record()
            
            # مسح حقول الإدخال
            self.course_entry.delete(0, tk.END)
            self.grade_combo.set('')
            
        except ValueError:
            messagebox.showerror("خطأ", "الرجاء إدخال قيم صحيحة")
    
    def update_record(self):
        # مسح البيانات القديمة
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        # إضافة البيانات الجديدة
        if self.student:
            for year, year_data in self.student.years.items():
                for term, term_data in year_data["terms"].items():
                    for course, info in term_data.items():
                        self.tree.insert("", "end", values=(year, term, course, info["grade"], info["credit_hours"]))
    
    def calculate_term_gpa(self):
        if not self.student:
            messagebox.showerror("خطأ", "الرجاء إنشاء سجل الطالب أولاً")
            return
            
        year = self.year_combo.get()
        term = self.term_combo.get()
        
...         if year and term:
...             try:
...                 gpa = self.student.calculate_term_gpa(int(year), int(term))
...                 self.stats_label.config(text=f"معدل الترم {term} من السنة {year}: {gpa:.2f}")
...             except ValueError:
...                 messagebox.showerror("خطأ", "الرجاء اختيار سنة وترم صحيحين")
...         else:
...             messagebox.showerror("خطأ", "الرجاء اختيار سنة وترم أولاً")
...     
...     def calculate_year_gpa(self):
...         if not self.student:
...             messagebox.showerror("خطأ", "الرجاء إنشاء سجل الطالب أولاً")
...             return
...             
...         year = self.year_combo.get()
...         
...         if year:
...             try:
...                 gpa = self.student.calculate_year_gpa(int(year))
...                 self.stats_label.config(text=f"معدل السنة {year}: {gpa:.2f}")
...             except ValueError:
...                 messagebox.showerror("خطأ", "الرجاء اختيار سنة صحيحة")
...         else:
...             messagebox.showerror("خطأ", "الرجاء اختيار سنة أولاً")
...     
...     def calculate_cumulative_gpa(self):
...         if not self.student:
...             messagebox.showerror("خطأ", "الرجاء إنشاء سجل الطالب أولاً")
...             return
...             
...         gpa = self.student.calculate_cumulative_gpa()
...         credits = self.student.total_credits
...         self.stats_label.config(text=f"المعدل التراكمي: {gpa:.2f} | مجموع الساعات: {credits}")
... 
... if __name__ == "__main__":
...     root = tk.Tk()
...     app = AcademicRecordApp(root)
