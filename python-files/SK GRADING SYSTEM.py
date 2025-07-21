import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
from tkinter.scrolledtext import ScrolledText
import json
import os
import re
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Image, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from PIL import Image as PILImage, ImageTk
import datetime
import pandas as pd  # 添加pandas库用于Excel处理
import numpy as np   # 添加numpy库用于数据处理

# 注册中文字体
try:
    pdfmetrics.registerFont(TTFont('SimSun', 'simsun.ttf'))
except:
    print("警告：未找到SimHei字体，中文字符可能无法正确显示在PDF中")

# 初始化数据结构
if os.path.exists('students.json'):
    with open('students.json', 'r', encoding='utf-8') as f:
        students_data = json.load(f)
else:
    students_data = {
        "classes": {
            "1 Ikhlas": [], "1 Rajin": [], "1 Jimat": [],
            "2 Ikhlas": [], "2 Rajin": [], "2 Jimat": [],
            "3 Ikhlas": [], "3 Rajin": [], "3 Jimat": [],
            "4 Ikhlas": [], "4 Rajin": [], "4 Jimat": [],
            "5 Ikhlas": [], "5 Rajin": [], "5 Jimat": [],
            "6 Ikhlas": [], "6 Rajin": [], "6 Jimat": []
        },
        "scores": {},
        "school_info": {
            "name": "丹绒马林重新华小",
            "english_name": "SJKC CHUNG SIN TANJONG MALIM",
            "logo": None,
            "year": datetime.datetime.now().year
        }
    }

# 科目定义
SEMESTER1_SUBJECTS = [
    "华文Bahasa Cina", "英文Bahasa Inggeris", "马来文Bahasa Melayu",
    "科学Sains", "数学Matematik", "道德/宗教课Moral/Pendidikan Islam", "历史Sejarah"
]

SEMESTER2_SUBJECTS = SEMESTER1_SUBJECTS + [
    "设计与工艺RBT", "体育体健PJPK", "美术PSV"
]

# 成绩等级转换
def score_to_grade(score):
    if score == "TH":  # 缺席
        return "TH"
    try:
        score = int(score)
    except:
        return ""
    
    if 82 <= score <= 100:
        return "A Cemerlang"
    elif 66 <= score <= 81:
        return "B Kepujian"
    elif 50 <= score <= 65:
        return "C Baik"
    elif 35 <= score <= 49:
        return "D Memuaskan"
    elif 20 <= score <= 34:
        return "E Mencapai tahap minimum"
    else:
        return "F belum mencapai tahap minimum"

# 主应用类
class StudentGradeProcessor(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("学生成绩处理器")
        self.geometry("1000x700")
        self.configure(bg="#f0f0f0")
        
        # 创建菜单栏
        self.create_menu()
        
        # 创建标签页
        self.tab_control = ttk.Notebook(self)
        
        # 创建四个页面
        self.page1 = StudentInfoPage(self.tab_control, self)
        self.page2 = ScoreEntryPage(self.tab_control, self)
        self.page3 = RankingPage(self.tab_control, self)
        self.page4 = ReportCardPage(self.tab_control, self)
        
        # 添加标签页
        self.tab_control.add(self.page1, text="学生资料")
        self.tab_control.add(self.page2, text="成绩录入")
        self.tab_control.add(self.page3, text="排名系统")
        self.tab_control.add(self.page4, text="成绩单生成")
        
        self.tab_control.pack(expand=1, fill="both")
        
        # 保存数据定时器
        self.save_data_timer()
    
    def create_menu(self):
        menubar = tk.Menu(self)
        
        # 文件菜单
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="保存数据", command=self.save_data)
        file_menu.add_command(label="从Excel导入学生", command=self.import_students_from_excel)  # 新增导入功能
        file_menu.add_command(label="退出", command=self.quit)
        menubar.add_cascade(label="文件", menu=file_menu)
        
        # 设置菜单
        settings_menu = tk.Menu(menubar, tearoff=0)
        settings_menu.add_command(label="更改年份", command=self.change_year)
        settings_menu.add_command(label="更改学校信息", command=self.change_school_info)
        settings_menu.add_command(label="设置校徽", command=self.set_school_logo)
        menubar.add_cascade(label="设置", menu=settings_menu)
        
        self.config(menu=menubar)
    
    def change_year(self):
        year = simpledialog.askinteger("更改年份", "请输入新学年年份:", 
                                      parent=self, 
                                      minvalue=2000, 
                                      maxvalue=2100)
        if year:
            students_data["school_info"]["year"] = year
            self.save_data()
            messagebox.showinfo("成功", f"年份已更新为 {year}")
    
    def change_school_info(self):
        dialog = tk.Toplevel(self)
        dialog.title("更改学校信息")
        dialog.geometry("400x200")
        dialog.transient(self)
        dialog.grab_set()
        
        tk.Label(dialog, text="学校名称(中文):").grid(row=0, column=0, padx=10, pady=5, sticky="e")
        chinese_name = tk.Entry(dialog, width=30)
        chinese_name.insert(0, students_data["school_info"]["name"])
        chinese_name.grid(row=0, column=1, padx=10, pady=5)
        
        tk.Label(dialog, text="学校名称(英文):").grid(row=1, column=0, padx=10, pady=5, sticky="e")
        english_name = tk.Entry(dialog, width=30)
        english_name.insert(0, students_data["school_info"]["english_name"])
        english_name.grid(row=1, column=1, padx=10, pady=5)
        
        def save_changes():
            students_data["school_info"]["name"] = chinese_name.get()
            students_data["school_info"]["english_name"] = english_name.get()
            self.save_data()
            messagebox.showinfo("成功", "学校信息已更新")
            dialog.destroy()
        
        tk.Button(dialog, text="保存", command=save_changes).grid(row=2, column=1, pady=10)
    
    def set_school_logo(self):
        file_path = filedialog.askopenfilename(title="选择校徽图片",
                                              filetypes=[("Image files", "*.png;*.jpg;*.jpeg")])
        if file_path:
            students_data["school_info"]["logo"] = file_path
            self.save_data()
            messagebox.showinfo("成功", "校徽已设置")
    
    def save_data(self):
        with open('students.json', 'w', encoding='utf-8') as f:
            json.dump(students_data, f, ensure_ascii=False, indent=2)
    
    def save_data_timer(self):
        self.save_data()
        self.after(30000, self.save_data_timer)  # 每30秒自动保存一次
    
    # 新增Excel导入方法
    def import_students_from_excel(self):
        file_path = filedialog.askopenfilename(
            title="选择学生名单Excel文件",
            filetypes=[("Excel文件", "*.xlsx"), ("所有文件", "*.*")]
        )
        
        if not file_path:
            return
        
        try:
            # 读取Excel文件
            df = pd.read_excel(file_path)
            
            # 检查必要的列是否存在
            required_columns = ['学生姓名', '班级', '班主任']
            if not all(col in df.columns for col in required_columns):
                missing = [col for col in required_columns if col not in df.columns]
                messagebox.showerror("错误", f"Excel文件中缺少必要的列: {', '.join(missing)}")
                return
            
            # 创建导入进度窗口
            progress_window = tk.Toplevel(self)
            progress_window.title("导入进度")
            progress_window.geometry("400x150")
            progress_window.transient(self)
            progress_window.grab_set()
            
            tk.Label(progress_window, text="正在导入学生数据...").pack(pady=10)
            
            progress_var = tk.DoubleVar()
            progress_bar = ttk.Progressbar(progress_window, variable=progress_var, maximum=100)
            progress_bar.pack(fill="x", padx=20, pady=5)
            
            status_label = tk.Label(progress_window, text="")
            status_label.pack(pady=5)
            
            progress_window.update()
            
            # 处理导入
            total_students = len(df)
            imported_count = 0
            skipped_count = 0
            new_classes = []
            
            for index, row in df.iterrows():
                # 更新进度
                progress = (index + 1) / total_students * 100
                progress_var.set(progress)
                status_label.config(text=f"处理中: {index+1}/{total_students}")
                progress_window.update()
                
                # 获取学生数据
                name = str(row['学生姓名']).strip()
                class_name = str(row['班级']).strip()
                teacher = str(row['班主任']).strip()
                
                # 检查数据有效性
                if not name or not class_name or not teacher:
                    skipped_count += 1
                    continue
                
                # 检查班级是否存在，不存在则创建
                if class_name not in students_data["classes"]:
                    students_data["classes"][class_name] = []
                    new_classes.append(class_name)
                
                # 检查是否已存在相同学生
                exists = any(s["name"] == name and s["class"] == class_name 
                            for s in students_data["classes"][class_name])
                
                if exists:
                    skipped_count += 1
                else:
                    # 添加新学生
                    new_student = {
                        "name": name,
                        "class": class_name,
                        "teacher": teacher
                    }
                    students_data["classes"][class_name].append(new_student)
                    imported_count += 1
            
            # 保存数据
            self.save_data()
            progress_window.destroy()
            
            # 显示导入结果
            result_message = f"导入完成!\n\n成功导入: {imported_count} 名学生\n跳过重复/无效: {skipped_count} 名"
            if new_classes:
                result_message += f"\n\n创建了新班级: {', '.join(new_classes)}"
            
            messagebox.showinfo("导入结果", result_message)
            
            # 刷新学生资料页面
            self.page1.load_students()
            
        except Exception as e:
            messagebox.showerror("导入错误", f"导入过程中发生错误:\n{str(e)}")


# 学生资料页面
class StudentInfoPage(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.create_widgets()
    
    def create_widgets(self):
        # 班级选择
        class_frame = ttk.LabelFrame(self, text="班级选择")
        class_frame.pack(pady=10, padx=10, fill="x")
        
        self.class_var = tk.StringVar()
        classes = list(students_data["classes"].keys())
        class_combo = ttk.Combobox(class_frame, textvariable=self.class_var, values=classes, width=20)
        class_combo.current(0)
        class_combo.pack(side="left", padx=5, pady=5)
        
        # 添加学生按钮
        add_btn = ttk.Button(class_frame, text="添加学生", command=self.add_student)
        add_btn.pack(side="left", padx=5, pady=5)
        
        # 删除学生按钮
        del_btn = ttk.Button(class_frame, text="删除选中学生", command=self.delete_student)
        del_btn.pack(side="left", padx=5, pady=5)
        
        # 学生列表
        list_frame = ttk.LabelFrame(self, text="学生列表")
        list_frame.pack(pady=10, padx=10, fill="both", expand=True)
        
        columns = ("name", "class", "teacher")
        self.tree = ttk.Treeview(list_frame, columns=columns, show="headings", selectmode="extended")
        
        # 设置列标题
        self.tree.heading("name", text="学生姓名")
        self.tree.heading("class", text="班级")
        self.tree.heading("teacher", text="班主任")
        
        # 设置列宽
        self.tree.column("name", width=200)
        self.tree.column("class", width=150)
        self.tree.column("teacher", width=200)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # 绑定班级选择事件
        self.class_var.trace("w", self.load_students)
        self.load_students()
    
    def load_students(self, *args):
        selected_class = self.class_var.get()
        self.tree.delete(*self.tree.get_children())
        
        if selected_class:
            for student in students_data["classes"][selected_class]:
                self.tree.insert("", "end", values=(
                    student["name"],
                    student["class"],
                    student["teacher"]
                ))
    
    def add_student(self):
        dialog = tk.Toplevel(self)
        dialog.title("添加学生")
        dialog.geometry("400x200")
        dialog.transient(self)
        dialog.grab_set()
        
        tk.Label(dialog, text="学生姓名(英文):").grid(row=0, column=0, padx=10, pady=5, sticky="e")
        name_entry = tk.Entry(dialog, width=30)
        name_entry.grid(row=0, column=1, padx=10, pady=5)
        
        tk.Label(dialog, text="班级:").grid(row=1, column=0, padx=10, pady=5, sticky="e")
        class_var = tk.StringVar(value=self.class_var.get())
        class_combo = ttk.Combobox(dialog, textvariable=class_var, 
                                  values=list(students_data["classes"].keys()), width=20)
        class_combo.grid(row=1, column=1, padx=10, pady=5)
        
        tk.Label(dialog, text="班主任:").grid(row=2, column=0, padx=10, pady=5, sticky="e")
        teacher_entry = tk.Entry(dialog, width=30)
        teacher_entry.grid(row=2, column=1, padx=10, pady=5)
        
        def save_student():
            name = name_entry.get().strip()
            class_name = class_var.get().strip()
            teacher = teacher_entry.get().strip()
            
            if not name or not class_name or not teacher:
                messagebox.showerror("错误", "所有字段必须填写")
                return
            
            new_student = {
                "name": name,
                "class": class_name,
                "teacher": teacher
            }
            
            students_data["classes"][class_name].append(new_student)
            self.app.save_data()
            self.load_students()
            dialog.destroy()
            messagebox.showinfo("成功", "学生已添加")
        
        tk.Button(dialog, text="保存", command=save_student).grid(row=3, column=1, pady=10)
    
    def delete_student(self):
        selected_class = self.class_var.get()
        selected_items = self.tree.selection()
        
        if not selected_class or not selected_items:
            messagebox.showwarning("警告", "请选择要删除的学生")
            return
        
        for item in selected_items:
            student_name = self.tree.item(item, "values")[0]
            # 从班级中删除学生
            students_data["classes"][selected_class] = [
                s for s in students_data["classes"][selected_class] if s["name"] != student_name
            ]
        
        self.app.save_data()
        self.load_students()
        messagebox.showinfo("成功", f"已删除 {len(selected_items)} 名学生")


# 成绩录入页面
class ScoreEntryPage(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.current_class = ""
        self.current_semester = 1
        self.student_scores = {}
        self.th_vars = {}  # 存储每个科目的TH状态
        self.create_widgets()
    
    def create_widgets(self):
        # 学期选择
        semester_frame = ttk.LabelFrame(self, text="学期选择")
        semester_frame.pack(pady=10, padx=10, fill="x")
        
        self.semester_var = tk.IntVar(value=1)
        tk.Radiobutton(semester_frame, text="上半年", variable=self.semester_var, value=1, 
                      command=self.semester_changed).pack(side="left", padx=10)
        tk.Radiobutton(semester_frame, text="下半年", variable=self.semester_var, value=2, 
                      command=self.semester_changed).pack(side="left", padx=10)
        
        # 班级选择
        class_frame = ttk.LabelFrame(self, text="班级选择")
        class_frame.pack(pady=10, padx=10, fill="x")
        
        self.class_var = tk.StringVar()
        classes = list(students_data["classes"].keys())
        class_combo = ttk.Combobox(class_frame, textvariable=self.class_var, values=classes, width=20)
        class_combo.current(0)
        class_combo.pack(side="left", padx=5, pady=5)
        
        # 加载学生按钮
        load_btn = ttk.Button(class_frame, text="加载学生", command=self.load_students)
        load_btn.pack(side="left", padx=5, pady=5)
        
        # 保存成绩按钮
        save_btn = ttk.Button(class_frame, text="保存成绩", command=self.save_scores)
        save_btn.pack(side="left", padx=5, pady=5)
        
        # 成绩录入区域
        entry_frame = ttk.Frame(self)
        entry_frame.pack(pady=10, padx=10, fill="both", expand=True)
        
        # 左侧学生列表
        student_list_frame = ttk.Frame(entry_frame)
        student_list_frame.pack(side="left", fill="y", padx=(0, 10))
        
        tk.Label(student_list_frame, text="学生列表 (A-Z顺序)").pack()
        
        self.student_listbox = tk.Listbox(student_list_frame, width=25, height=20)
        self.student_listbox.pack(fill="y", expand=True)
        self.student_listbox.bind("<<ListboxSelect>>", self.student_selected)
        
        # 右侧成绩录入
        score_entry_frame = ttk.LabelFrame(entry_frame, text="成绩录入")
        score_entry_frame.pack(side="right", fill="both", expand=True)
        
        self.score_entries = {}
        self.grade_labels = {}
        self.th_checkboxes = {}
        
        # 创建科目标签和输入框
        subjects = SEMESTER1_SUBJECTS if self.semester_var.get() == 1 else SEMESTER2_SUBJECTS
        
        for i, subject in enumerate(subjects):
            frame = ttk.Frame(score_entry_frame)
            frame.grid(row=i, column=0, sticky="ew", padx=5, pady=2)
            
            # 科目名称
            tk.Label(frame, text=subject, width=30, anchor="w").pack(side="left")
            
            # TH复选框 (缺席标记)
            th_var = tk.BooleanVar(value=False)
            th_check = ttk.Checkbutton(frame, text="TH", variable=th_var, 
                                      command=lambda s=subject: self.th_check_changed(s))
            th_check.pack(side="left", padx=(0, 5))
            self.th_vars[subject] = th_var
            
            # 分数输入框
            entry = ttk.Entry(frame, width=10)
            entry.pack(side="left", padx=5)
            entry.bind("<KeyRelease>", self.score_changed)
            self.score_entries[subject] = entry
            
            # 等级显示
            grade_label = tk.Label(frame, text="", width=20)
            grade_label.pack(side="left")
            self.grade_labels[subject] = grade_label
    
    def th_check_changed(self, subject):
        """处理TH复选框状态变化"""
        th_checked = self.th_vars[subject].get()
        entry = self.score_entries[subject]
        
        if th_checked:
            # 如果选中TH，清空分数并禁用输入框
            entry.delete(0, tk.END)
            entry.insert(0, "TH")
            entry.config(state="disabled")
            # 更新等级显示
            self.grade_labels[subject].config(text="TH", fg="red")
        else:
            # 如果取消TH，启用输入框
            entry.config(state="normal")
            entry.delete(0, tk.END)
            self.grade_labels[subject].config(text="", fg="black")
    
    def semester_changed(self):
        self.load_students()
    
    def load_students(self):
        self.current_class = self.class_var.get()
        self.current_semester = self.semester_var.get()
        
        if not self.current_class:
            return
        
        # 清空学生列表
        self.student_listbox.delete(0, tk.END)
        
        # 获取班级学生并按名字排序
        students = students_data["classes"][self.current_class]
        sorted_students = sorted(students, key=lambda s: s["name"])
        
        # 添加到列表框
        for student in sorted_students:
            self.student_listbox.insert(tk.END, student["name"])
        
        # 初始化成绩数据
        self.student_scores = {}
        
        # 尝试加载已有成绩
        class_scores = students_data["scores"].get(self.current_class, {})
        semester_scores = class_scores.get(f"semester{self.current_semester}", {})
        
        for student in students:
            student_name = student["name"]
            if student_name in semester_scores:
                self.student_scores[student_name] = semester_scores[student_name]
            else:
                # 初始化空成绩
                subjects = SEMESTER1_SUBJECTS if self.current_semester == 1 else SEMESTER2_SUBJECTS
                self.student_scores[student_name] = {subj: "" for subj in subjects}
        
        # 选择第一个学生
        if sorted_students:
            self.student_listbox.selection_set(0)
            self.student_listbox.see(0)
            self.student_selected(None)
    
    def student_selected(self, event):
        selected = self.student_listbox.curselection()
        if not selected:
            return
        
        student_name = self.student_listbox.get(selected[0])
        
        # 清空输入框和TH状态
        for subject in self.score_entries:
            self.score_entries[subject].delete(0, tk.END)
            self.score_entries[subject].config(state="normal")
            self.th_vars[subject].set(False)
            self.grade_labels[subject].config(text="")
        
        # 加载学生成绩
        if student_name in self.student_scores:
            scores = self.student_scores[student_name]
            for subject, score in scores.items():
                if subject in self.score_entries:
                    # 设置分数
                    self.score_entries[subject].delete(0, tk.END)
                    self.score_entries[subject].insert(0, str(score))
                    
                    # 设置TH状态
                    if str(score).upper() == "TH":
                        self.th_vars[subject].set(True)
                        self.score_entries[subject].config(state="disabled")
                    
                    # 更新等级显示
                    self.update_grade_label(subject, str(score))
    
    def score_changed(self, event):
        for subject, entry in self.score_entries.items():
            # 如果TH已选中，跳过更新
            if self.th_vars[subject].get():
                continue
                
            score = entry.get().strip()
            self.update_grade_label(subject, score)
    
    def update_grade_label(self, subject, score):
        if score == "":
            self.grade_labels[subject].config(text="")
        elif score.upper() == "TH":
            self.grade_labels[subject].config(text="TH", fg="red")
        else:
            try:
                score_val = int(score)
                grade = score_to_grade(score_val)
                self.grade_labels[subject].config(text=grade)
            except ValueError:
                self.grade_labels[subject].config(text="无效输入", fg="red")
    
    def save_scores(self):
        selected = self.student_listbox.curselection()
        if not selected:
            messagebox.showwarning("警告", "请选择一名学生")
            return
        
        student_name = self.student_listbox.get(selected[0])
        
        # 获取当前学生成绩
        scores = {}
        for subject, entry in self.score_entries.items():
            # 如果TH已选中，使用"TH"
            if self.th_vars[subject].get():
                scores[subject] = "TH"
            else:
                score_val = entry.get().strip()
                # 处理无效分数
                if score_val == "":
                    scores[subject] = ""
                elif score_val.upper() == "TH":
                    scores[subject] = "TH"
                else:
                    try:
                        score_val = int(score_val)
                        scores[subject] = score_val
                    except ValueError:
                        messagebox.showerror("错误", f"科目 {subject} 的分数无效")
                        return
        
        # 更新成绩数据
        self.student_scores[student_name] = scores
        
        # 保存到全局数据结构
        if self.current_class not in students_data["scores"]:
            students_data["scores"][self.current_class] = {}
        
        semester_key = f"semester{self.current_semester}"
        if semester_key not in students_data["scores"][self.current_class]:
            students_data["scores"][self.current_class][semester_key] = {}
        
        students_data["scores"][self.current_class][semester_key][student_name] = scores
        
        self.app.save_data()
        messagebox.showinfo("成功", f"{student_name} 的成绩已保存")


# 排名页面
class RankingPage(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.create_widgets()
    
    def create_widgets(self):
        # 班级选择
        class_frame = ttk.LabelFrame(self, text="班级选择")
        class_frame.pack(pady=10, padx=10, fill="x")
        
        self.class_var = tk.StringVar()
        classes = list(students_data["classes"].keys())
        class_combo = ttk.Combobox(class_frame, textvariable=self.class_var, values=classes, width=20)
        class_combo.current(0)
        class_combo.pack(side="left", padx=5, pady=5)
        
        # 生成排名按钮
        gen_btn = ttk.Button(class_frame, text="生成排名", command=self.generate_ranking)
        gen_btn.pack(side="left", padx=5, pady=5)
        
        # 打印按钮
        print_btn = ttk.Button(class_frame, text="打印PDF", command=self.print_ranking)
        print_btn.pack(side="left", padx=5, pady=5)
        
        # 排名显示区域
        result_frame = ttk.LabelFrame(self, text="排名结果")
        result_frame.pack(pady=10, padx=10, fill="both", expand=True)
        
        self.result_text = ScrolledText(result_frame, wrap=tk.WORD, height=20)
        self.result_text.pack(fill="both", expand=True, padx=5, pady=5)
        self.result_text.config(state="disabled")
    
    def calculate_average(self, student_name, class_name, semester):
        # 获取学生成绩
        semester_key = f"semester{semester}"
        scores = students_data["scores"].get(class_name, {}).get(semester_key, {}).get(student_name, {})
        
        # 计算平均分
        total = 0
        count = 0
        
        for subject, score in scores.items():
            if str(score).upper() == "TH":  # 缺席，不计入平均分
                continue
            
            try:
                score_val = int(score)
                total += score_val
                count += 1
            except (ValueError, TypeError):
                pass
        
        if count == 0:
            return 0
        return total / count
    
    def generate_ranking(self):
        class_name = self.class_var.get()
        if not class_name:
            messagebox.showwarning("警告", "请选择一个班级")
            return
        
        # 获取班级学生
        students = students_data["classes"][class_name]
        if not students:
            messagebox.showinfo("提示", "该班级没有学生")
            return
        
        # 计算每个学生的平均分
        student_averages = []
        for student in students:
            name = student["name"]
            # 计算两个学期的平均分
            avg1 = self.calculate_average(name, class_name, 1)
            avg2 = self.calculate_average(name, class_name, 2)
            total_avg = (avg1 + avg2) / 2 if avg1 > 0 and avg2 > 0 else max(avg1, avg2)
            student_averages.append((name, total_avg))
        
        # 按平均分排序
        student_averages.sort(key=lambda x: x[1], reverse=True)
        
        # 显示结果
        self.result_text.config(state="normal")
        self.result_text.delete(1.0, tk.END)
        
        self.result_text.insert(tk.END, f"{class_name} 学生排名:\n\n")
        self.result_text.insert(tk.END, "排名  学生姓名        平均分\n")
        self.result_text.insert(tk.END, "-" * 30 + "\n")
        
        for rank, (name, avg) in enumerate(student_averages, 1):
            self.result_text.insert(tk.END, f"{rank:<6}{name:<15}{avg:.2f}\n")
        
        self.result_text.config(state="disabled")
        self.current_ranking = student_averages
        self.current_class = class_name
    
    def print_ranking(self):
        if not hasattr(self, "current_ranking"):
            messagebox.showwarning("警告", "请先生成排名")
            return
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")],
            title="保存排名PDF"
        )
        
        if not file_path:
            return
        
        doc = SimpleDocTemplate(file_path, pagesize=A4)
        elements = []
        
        # 学校信息
        school_info = students_data["school_info"]
        year = school_info["year"]
        school_name = school_info["name"]
        english_name = school_info["english_name"]
        
        # 标题
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            "Title",
            parent=styles["Heading1"],
            fontName="SimHei",
            fontSize=16,
            alignment=1
        )
        
        title = Paragraph(f"{school_name}<br/>{english_name}", title_style)
        elements.append(title)
        elements.append(Spacer(1, 12))
        
        # 子标题
        subtitle = Paragraph(f"{year}学年学生成绩排名<br/>{self.current_class}", 
                           ParagraphStyle(
                               name="Subtitle",
                               parent=styles["Heading2"],
                               fontSize=14,
                               alignment=1
                           ))
        elements.append(subtitle)
        elements.append(Spacer(1, 24))
        
        # 创建排名表格
        data = [["排名", "学生姓名", "总平均分"]]
        
        for rank, (name, avg) in enumerate(self.current_ranking, 1):
            data.append([str(rank), name, f"{avg:.2f}"])
        
        table = Table(data)
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("FONTNAME", (0, 0), (-1, 0), "SimHei"),
            ("FONTSIZE", (0, 0), (-1, 0), 12),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
            ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
            ("GRID", (0, 0), (-1, -1), 1, colors.black),
        ]))
        
        elements.append(table)
        
        # 添加页脚
        elements.append(Spacer(1, 36))
        date_str = datetime.datetime.now().strftime("%Y-%m-%d")
        footer = Paragraph(f"生成日期: {date_str}", 
                          ParagraphStyle(
                              name="Footer",
                              parent=styles["Normal"],
                              fontSize=10
                          ))
        elements.append(footer)
        
        # 生成PDF
        doc.build(elements)
        messagebox.showinfo("成功", f"排名PDF已保存至: {file_path}")


# 成绩单生成页面
class ReportCardPage(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.create_widgets()
    
    def create_widgets(self):
        # 班级选择
        class_frame = ttk.LabelFrame(self, text="班级选择")
        class_frame.pack(pady=10, padx=10, fill="x")
        
        self.class_var = tk.StringVar()
        classes = list(students_data["classes"].keys())
        class_combo = ttk.Combobox(class_frame, textvariable=self.class_var, values=classes, width=20)
        class_combo.current(0)
        class_combo.pack(side="left", padx=5, pady=5)
        
        # 学期选择
        self.semester_var = tk.IntVar(value=1)
        tk.Radiobutton(class_frame, text="上半年", variable=self.semester_var, value=1).pack(side="left", padx=10)
        tk.Radiobutton(class_frame, text="下半年", variable=self.semester_var, value=2).pack(side="left", padx=10)
        
        # 显示分数
        self.show_score_var = tk.BooleanVar(value=True)
        tk.Checkbutton(class_frame, text="显示分数", variable=self.show_score_var).pack(side="left", padx=10)
        
        # 生成按钮
        gen_btn = ttk.Button(class_frame, text="生成成绩单", command=self.generate_report_cards)
        gen_btn.pack(side="left", padx=5, pady=5)
        
        # 状态信息
        self.status_var = tk.StringVar(value="准备就绪")
        status_label = tk.Label(self, textvariable=self.status_var)
        status_label.pack(pady=5)
    
    def generate_report_cards(self):
        class_name = self.class_var.get()
        semester = self.semester_var.get()
        show_score = self.show_score_var.get()
        
        if not class_name:
            messagebox.showwarning("警告", "请选择一个班级")
            return
        
        # 获取班级学生
        students = students_data["classes"][class_name]
        if not students:
            messagebox.showinfo("提示", "该班级没有学生")
            return
        
        # 选择保存位置
        folder_path = filedialog.askdirectory(title="选择保存成绩单的文件夹")
        if not folder_path:
            return
        
        self.status_var.set("正在生成成绩单...")
        self.update()
        
        # 为每个学生生成成绩单
        for student in students:
            student_name = student["name"]
            self.generate_report_card(student, class_name, semester, show_score, folder_path)
        
        self.status_var.set(f"成功生成 {len(students)} 份成绩单到: {folder_path}")
    
    def generate_report_card(self, student, class_name, semester, show_score, folder_path):
        # 学生信息
        student_name = student["name"]
        teacher = student["teacher"]
        
        # 学校信息
        school_info = students_data["school_info"]
        year = school_info["year"]
        school_name = school_info["name"]
        english_name = school_info["english_name"]
        logo_path = school_info["logo"]
        
        # 文件名
        file_name = f"{class_name}_{student_name}_S{semester}_{year}.pdf"
        file_path = os.path.join(folder_path, file_name)
        
        # 创建PDF文档
        doc = SimpleDocTemplate(file_path, pagesize=A4, leftMargin=20*mm, rightMargin=20*mm)
        elements = []
        
        # 样式
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            "Title",
            parent=styles["Heading1"],
            fontName="SimHei",
            fontSize=16,
            alignment=1
        )
        
        # 添加校徽
        if logo_path and os.path.exists(logo_path):
            try:
                logo = Image(logo_path, width=50, height=50)
                logo.hAlign = "CENTER"
                elements.append(logo)
                elements.append(Spacer(1, 5))
            except:
                pass
        
        # 学校名称
        title = Paragraph(f"{school_name}<br/>{english_name}", title_style)
        elements.append(title)
        elements.append(Spacer(1, 12))
        
        # 成绩单标题
        if semester == 1:
            report_title = f"{year}学年期中测试成绩"
            report_subtitle = f"KEPUTUSAN UJIAN PERTENGAHAN SESI AKADEMIK TAHUN {year}"
        else:
            report_title = f"{year}学年期末测试成绩"
            report_subtitle = f"KEPUTUSAN UJIAN AKHIR SESI AKADEMIK TAHUN {year}"
        
        elements.append(Paragraph(report_title, 
                                ParagraphStyle(
                                    name="ReportTitle",
                                    parent=styles["Heading2"],
                                    fontSize=14,
                                    alignment=1
                                )))
        elements.append(Paragraph(report_subtitle, 
                                ParagraphStyle(
                                    name="ReportSubtitle",
                                    parent=styles["Heading3"],
                                    fontSize=12,
                                    alignment=1
                                )))
        elements.append(Spacer(1, 24))
        
        # 学生信息
        student_info = [
            [f"学生姓名: {student_name}"],
            [f"Nama murid: {student_name}"],
            [f"班级Kelas: {class_name}"]
        ]
        
        student_table = Table(student_info, colWidths=[doc.width])
        student_table.setStyle(TableStyle([
            ("FONTNAME", (0, 0), (-1, -1), "SimHei"),
            ("FONTSIZE", (0, 0), (-1, -1), 12),
            ("ALIGN", (0, 0), (-1, -1), "LEFT"),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ]))
        elements.append(student_table)
        elements.append(Spacer(1, 12))
        
        # 成绩表格
        semester_key = f"semester{semester}"
        scores = students_data["scores"].get(class_name, {}).get(semester_key, {}).get(student_name, {})
        
        # 确定显示的科目
        grade = int(class_name.split()[0])  # 从班级名中提取年级
        if semester == 1:  # 上半年
            if grade <= 3:  # 低年级
                subjects = [subj for subj in SEMESTER1_SUBJECTS if "历史" not in subj]
            else:  # 高年级
                subjects = SEMESTER1_SUBJECTS
        else:  # 下半年
            if grade <= 3:  # 低年级
                subjects = [subj for subj in SEMESTER2_SUBJECTS 
                           if "历史" not in subj and "设计与工艺" not in subj]
            else:  # 高年级
                subjects = SEMESTER2_SUBJECTS
        
        # 创建表格数据
        table_data = [["科目", "分数", "等级"]]
        
        for subject in subjects:
            score = scores.get(subject, "")
            
            # 处理TH情况
            if str(score).upper() == "TH":
                grade_text = "TH"
                score_display = "TH"
            else:
                grade_text = score_to_grade(score) if score != "" else ""
                score_display = str(score)
            
            if show_score:
                table_data.append([subject, score_display, grade_text])
            else:
                table_data.append([subject, "", grade_text])
        
        # 创建表格
        table = Table(table_data, colWidths=[150, 60, 100])
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("FONTNAME", (0, 0), (-1, 0), "SimHei"),
            ("FONTSIZE", (0, 0), (-1, 0), 12),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
            ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
            ("GRID", (0, 0), (-1, -1), 1, colors.black),
            # 特殊处理TH行
            ("TEXTCOLOR", (1, 1), (1, -1), lambda r, c: colors.red if table_data[r][1] == "TH" else colors.black),
            ("TEXTCOLOR", (2, 1), (2, -1), lambda r, c: colors.red if table_data[r][2] == "TH" else colors.black),
        ]))
        
        elements.append(table)
        elements.append(Spacer(1, 24))
        
        # 签名区域
        sign_data = [
            [f"级任老师Guru Kelas: {teacher}", "", f"校长Guru besar: _______________"]
        ]
        sign_table = Table(sign_data, colWidths=[200, 100, 200])
        sign_table.setStyle(TableStyle([
            ("FONTNAME", (0, 0), (-1, 0), "SimHei"),
            ("FONTSIZE", (0, 0), (-1, 0), 12),
            ("ALIGN", (0, 0), (-1, 0), "CENTER"),
        ]))
        elements.append(sign_table)
        
        # 生成PDF
        doc.build(elements)


# 运行应用
if __name__ == "__main__":
    app = StudentGradeProcessor()
    app.mainloop()