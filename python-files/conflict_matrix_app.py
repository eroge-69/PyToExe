#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
تطبيق مصفوفة التعارض - Conflict Matrix Desktop App
تحويل من كود R إلى تطبيق Python GUI
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
import numpy as np
from pathlib import Path
import sys
import os
from tkinter import scrolledtext
import threading
import time

class ConflictMatrixApp:
    def __init__(self, root):
        self.root = root
        self.root.title("تطبيق مصفوفة التعارض - Conflict Matrix App")
        self.root.geometry("1200x800")
        self.root.configure(bg='#f0f0f0')
        
        # متغيرات البيانات
        self.data = None
        self.conflict_matrix = None
        self.subjects = []
        self.conflict_details = []
        
        # إعداد الواجهة
        self.setup_ui()
        self.setup_styles()
        
    def setup_styles(self):
        """إعداد الأنماط المخصصة"""
        style = ttk.Style()
        
        # تخصيص الأنماط
        style.configure('Header.TLabel', 
                       font=('Arial', 16, 'bold'),
                       background='#2c3e50',
                       foreground='white',
                       padding=10)
        
        style.configure('Title.TLabel',
                       font=('Arial', 14, 'bold'),
                       background='#34495e',
                       foreground='white',
                       padding=5)
        
        style.configure('Custom.TButton',
                       font=('Arial', 10, 'bold'),
                       padding=10)
        
        style.configure('Stats.TLabel',
                       font=('Arial', 12, 'bold'),
                       foreground='#2c3e50')
    
    def setup_ui(self):
        """إعداد واجهة المستخدم"""
        
        # الإطار الرئيسي
        main_frame = tk.Frame(self.root, bg='#ecf0f1')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # العنوان الرئيسي
        title_label = ttk.Label(main_frame, 
                               text="📊 تطبيق مصفوفة التعارض - Conflict Matrix App",
                               style='Header.TLabel')
        title_label.pack(fill=tk.X, pady=(0, 10))
        
        # إطار التحكم
        control_frame = tk.Frame(main_frame, bg='#bdc3c7', relief=tk.RAISED, bd=2)
        control_frame.pack(fill=tk.X, pady=(0, 10), padx=5)
        
        # إطار اختيار الملف
        file_frame = tk.Frame(control_frame, bg='#bdc3c7')
        file_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(file_frame, text="📁 اختيار ملف Excel:",
                 font=('Arial', 11, 'bold')).pack(anchor='w')
        
        file_select_frame = tk.Frame(file_frame, bg='#bdc3c7')
        file_select_frame.pack(fill=tk.X, pady=5)
        
        self.file_path_var = tk.StringVar()
        self.file_entry = ttk.Entry(file_select_frame, textvariable=self.file_path_var,
                                   font=('Arial', 10), width=70)
        self.file_entry.pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(file_select_frame, text="استعراض...",
                  command=self.browse_file,
                  style='Custom.TButton').pack(side=tk.LEFT)
        
        # أزرار التحكم
        button_frame = tk.Frame(control_frame, bg='#bdc3c7')
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.process_btn = ttk.Button(button_frame, text="🔄 معالجة البيانات",
                                     command=self.process_data_threaded,
                                     style='Custom.TButton',
                                     state='disabled')
        self.process_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.export_btn = ttk.Button(button_frame, text="💾 تصدير النتيجة",
                                    command=self.export_results,
                                    style='Custom.TButton',
                                    state='disabled')
        self.export_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.clear_btn = ttk.Button(button_frame, text="🗑️ مسح البيانات",
                                   command=self.clear_data,
                                   style='Custom.TButton')
        self.clear_btn.pack(side=tk.LEFT)
        
        # شريط التقدم
        self.progress = ttk.Progressbar(control_frame, mode='indeterminate')
        self.progress.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        # إطار النتائج مع تبويبات
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # تبويب الإحصائيات
        self.stats_frame = tk.Frame(self.notebook, bg='#ecf0f1')
        self.notebook.add(self.stats_frame, text="📊 الإحصائيات")
        
        # تبويب المصفوفة
        self.matrix_frame = tk.Frame(self.notebook, bg='#ecf0f1')
        self.notebook.add(self.matrix_frame, text="🔍 مصفوفة التعارض")
        
        # تبويب التفاصيل
        self.details_frame = tk.Frame(self.notebook, bg='#ecf0f1')
        self.notebook.add(self.details_frame, text="📋 تفاصيل التعارضات")
        
        # إعداد محتوى التبويبات
        self.setup_stats_tab()
        self.setup_matrix_tab()
        self.setup_details_tab()
        
        # شريط الحالة
        self.status_var = tk.StringVar()
        self.status_var.set("مستعد - اختر ملف Excel لبدء المعالجة")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var,
                              relief=tk.SUNKEN, anchor=tk.W,
                              font=('Arial', 9))
        status_bar.pack(fill=tk.X, pady=(5, 0))
    
    def setup_stats_tab(self):
        """إعداد تبويب الإحصائيات"""
        # إطار الإحصائيات الرئيسية
        stats_main_frame = tk.Frame(self.stats_frame, bg='#ecf0f1')
        stats_main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # إحصائيات عامة
        general_stats_frame = tk.LabelFrame(stats_main_frame, text="إحصائيات عامة",
                                           font=('Arial', 12, 'bold'),
                                           bg='#ecf0f1', fg='#2c3e50')
        general_stats_frame.pack(fill=tk.X, pady=(0, 10))
        
        # إنشاء متغيرات الإحصائيات
        self.stats_vars = {
            'subjects_count': tk.StringVar(value="0"),
            'conflicts_count': tk.StringVar(value="0"),
            'conflict_percentage': tk.StringVar(value="0%"),
            'total_students': tk.StringVar(value="0")
        }
        
        # إنشاء عرض الإحصائيات
        stats_grid = tk.Frame(general_stats_frame, bg='#ecf0f1')
        stats_grid.pack(fill=tk.X, padx=10, pady=10)
        
        stat_labels = [
            ("عدد المواد:", 'subjects_count'),
            ("عدد التعارضات:", 'conflicts_count'),
            ("نسبة التعارضات:", 'conflict_percentage'),
            ("إجمالي التسجيلات:", 'total_students')
        ]
        
        for i, (label, var_key) in enumerate(stat_labels):
            row = i // 2
            col = (i % 2) * 2
            
            tk.Label(stats_grid, text=label, font=('Arial', 11, 'bold'),
                    bg='#ecf0f1', fg='#34495e').grid(row=row, column=col,
                                                    sticky='e', padx=5, pady=5)
            tk.Label(stats_grid, textvariable=self.stats_vars[var_key],
                    font=('Arial', 11), bg='#ecf0f1',
                    fg='#e74c3c').grid(row=row, column=col+1,
                                      sticky='w', padx=5, pady=5)
        
        # إحصائيات تفصيلية للمواد
        subjects_stats_frame = tk.LabelFrame(stats_main_frame, text="إحصائيات المواد",
                                            font=('Arial', 12, 'bold'),
                                            bg='#ecf0f1', fg='#2c3e50')
        subjects_stats_frame.pack(fill=tk.BOTH, expand=True)
        
        # جدول إحصائيات المواد
        self.subjects_tree = ttk.Treeview(subjects_stats_frame,
                                         columns=('subject', 'students_count', 'conflicts'),
                                         show='headings',
                                         height=8)
        
        self.subjects_tree.heading('subject', text='المادة')
        self.subjects_tree.heading('students_count', text='عدد الطلاب')
        self.subjects_tree.heading('conflicts', text='عدد التعارضات')
        
        self.subjects_tree.column('subject', width=200, anchor='center')
        self.subjects_tree.column('students_count', width=100, anchor='center')
        self.subjects_tree.column('conflicts', width=100, anchor='center')
        
        # شريط تمرير للجدول
        subjects_scrollbar = ttk.Scrollbar(subjects_stats_frame,
                                          orient=tk.VERTICAL,
                                          command=self.subjects_tree.yview)
        self.subjects_tree.configure(yscroll=subjects_scrollbar.set)
        
        self.subjects_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        subjects_scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=10)
    
    def setup_matrix_tab(self):
        """إعداد تبويب المصفوفة"""
        # إطار المصفوفة
        matrix_main_frame = tk.Frame(self.matrix_frame, bg='#ecf0f1')
        matrix_main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # عنوان المصفوفة
        ttk.Label(matrix_main_frame, text="مصفوفة التعارض بين المواد",
                 style='Title.TLabel').pack(pady=(0, 10))
        
        # إطار المصفوفة مع أشرطة التمرير
        matrix_container = tk.Frame(matrix_main_frame, bg='white', relief=tk.SUNKEN, bd=2)
        matrix_container.pack(fill=tk.BOTH, expand=True)
        
        # Canvas للمصفوفة
        self.matrix_canvas = tk.Canvas(matrix_container, bg='white')
        
        # أشرطة التمرير
        h_scrollbar = ttk.Scrollbar(matrix_container, orient=tk.HORIZONTAL,
                                   command=self.matrix_canvas.xview)
        v_scrollbar = ttk.Scrollbar(matrix_container, orient=tk.VERTICAL,
                                   command=self.matrix_canvas.yview)
        
        self.matrix_canvas.configure(xscrollcommand=h_scrollbar.set,
                                    yscrollcommand=v_scrollbar.set)
        
        # إطار داخلي للمصفوفة
        self.matrix_inner_frame = tk.Frame(self.matrix_canvas, bg='white')
        
        # ترتيب العناصر
        self.matrix_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # ربط الإطار الداخلي بالـ Canvas
        self.canvas_frame = self.matrix_canvas.create_window((0, 0),
                                                           window=self.matrix_inner_frame,
                                                           anchor='nw')
        
        # ربط تحديث منطقة التمرير
        self.matrix_inner_frame.bind('<Configure>',
                                    lambda e: self.matrix_canvas.configure(
                                        scrollregion=self.matrix_canvas.bbox('all')))
    
    def setup_details_tab(self):
        """إعداد تبويب التفاصيل"""
        # إطار التفاصيل
        details_main_frame = tk.Frame(self.details_frame, bg='#ecf0f1')
        details_main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # عنوان التفاصيل
        ttk.Label(details_main_frame, text="تفاصيل التعارضات",
                 style='Title.TLabel').pack(pady=(0, 10))
        
        # منطقة التفاصيل مع التمرير
        self.details_text = scrolledtext.ScrolledText(details_main_frame,
                                                     font=('Arial', 10),
                                                     bg='white',
                                                     wrap=tk.WORD,
                                                     state=tk.DISABLED)
        self.details_text.pack(fill=tk.BOTH, expand=True)
    
    def browse_file(self):
        """استعراض واختيار ملف Excel"""
        file_path = filedialog.askopenfilename(
            title="اختر ملف Excel",
            filetypes=[("Excel files", "*.xlsx *.xls"), ("All files", "*.*")]
        )
        
        if file_path:
            self.file_path_var.set(file_path)
            self.process_btn.config(state='normal')
            self.status_var.set(f"تم اختيار الملف: {Path(file_path).name}")
    
    def process_data_threaded(self):
        """معالجة البيانات في خيط منفصل"""
        # تعطيل الأزرار
        self.process_btn.config(state='disabled')
        self.export_btn.config(state='disabled')
        
        # بدء شريط التقدم
        self.progress.start()
        self.status_var.set("جاري معالجة البيانات...")
        
        # تشغيل المعالجة في خيط منفصل
        thread = threading.Thread(target=self.process_data)
        thread.daemon = True
        thread.start()
    
    def process_data(self):
        """معالجة البيانات الرئيسية"""
        try:
            file_path = self.file_path_var.get()
            if not file_path or not Path(file_path).exists():
                raise FileNotFoundError("الملف غير موجود")
            
            # قراءة ملف Excel
            self.root.after(0, lambda: self.status_var.set("جاري قراءة الملف..."))
            self.data = pd.read_excel(file_path)
            
            if self.data.empty:
                raise ValueError("الملف فارغ أو لا يحتوي على بيانات صالحة")
            
            # الحصول على أسماء المواد
            self.subjects = [col for col in self.data.columns if str(col) != 'nan']
            
            if len(self.subjects) < 2:
                raise ValueError("يجب أن يحتوي الملف على مادتين على الأقل")
            
            # إنشاء مصفوفة التعارض
            self.root.after(0, lambda: self.status_var.set("جاري إنشاء مصفوفة التعارض..."))
            self.create_conflict_matrix()
            
            # تحليل التفاصيل
            self.root.after(0, lambda: self.status_var.set("جاري تحليل التفاصيل..."))
            self.analyze_conflicts()
            
            # تحديث الواجهة
            self.root.after(0, self.update_ui)
            
        except Exception as e:
            self.root.after(0, lambda: self.show_error(f"خطأ في معالجة البيانات: {str(e)}"))
        finally:
            # إيقاف شريط التقدم
            self.root.after(0, self.progress.stop)
    
    def create_conflict_matrix(self):
        """إنشاء مصفوفة التعارض"""
        num_subjects = len(self.subjects)
        self.conflict_matrix = np.full((num_subjects, num_subjects), "لا", dtype=object)
        
        # ملء القطر الرئيسي
        for i in range(num_subjects):
            self.conflict_matrix[i][i] = "نعم"
        
        # حساب التعارضات
        for i in range(num_subjects):
            for j in range(i + 1, num_subjects):
                # الحصول على قوائم الطلاب
                students_i = set(self.data[self.subjects[i]].dropna().astype(str))
                students_j = set(self.data[self.subjects[j]].dropna().astype(str))
                
                # التحقق من وجود طلاب مشتركين
                common_students = students_i.intersection(students_j)
                
                if len(common_students) > 0:
                    self.conflict_matrix[i][j] = "نعم"
                    self.conflict_matrix[j][i] = "نعم"
    
    def analyze_conflicts(self):
        """تحليل التعارضات بالتفصيل"""
        self.conflict_details = []
        num_subjects = len(self.subjects)
        
        for i in range(num_subjects):
            for j in range(i + 1, num_subjects):
                students_i = set(self.data[self.subjects[i]].dropna().astype(str))
                students_j = set(self.data[self.subjects[j]].dropna().astype(str))
                common_students = students_i.intersection(students_j)
                
                if len(common_students) > 0:
                    detail = {
                        'subject1': self.subjects[i],
                        'subject2': self.subjects[j],
                        'common_count': len(common_students),
                        'common_students': list(common_students),
                        'total_students1': len(students_i),
                        'total_students2': len(students_j),
                        'percentage1': len(common_students) / len(students_i) * 100 if len(students_i) > 0 else 0,
                        'percentage2': len(common_students) / len(students_j) * 100 if len(students_j) > 0 else 0
                    }
                    self.conflict_details.append(detail)
    
    def update_ui(self):
        """تحديث واجهة المستخدم بالنتائج"""
        # تحديث الإحصائيات
        self.update_stats()
        
        # تحديث المصفوفة
        self.update_matrix()
        
        # تحديث التفاصيل
        self.update_details()
        
        # تفعيل زر التصدير
        self.export_btn.config(state='normal')
        self.process_btn.config(state='normal')
        
        self.status_var.set("تمت معالجة البيانات بنجاح! ✅")
    
    def update_stats(self):
        """تحديث الإحصائيات"""
        num_subjects = len(self.subjects)
        num_conflicts = len(self.conflict_details)
        max_conflicts = num_subjects * (num_subjects - 1) // 2
        conflict_percentage = (num_conflicts / max_conflicts * 100) if max_conflicts > 0 else 0
        
        total_students = 0
        for subject in self.subjects:
            total_students += len(self.data[subject].dropna())
        
        # تحديث متغيرات الإحصائيات
        self.stats_vars['subjects_count'].set(str(num_subjects))
        self.stats_vars['conflicts_count'].set(str(num_conflicts))
        self.stats_vars['conflict_percentage'].set(f"{conflict_percentage:.2f}%")
        self.stats_vars['total_students'].set(str(total_students))
        
        # تحديث جدول المواد
        # مسح البيانات السابقة
        for item in self.subjects_tree.get_children():
            self.subjects_tree.delete(item)
        
        # إضافة بيانات جديدة
        for i, subject in enumerate(self.subjects):
            student_count = len(self.data[subject].dropna())
            conflict_count = sum(1 for detail in self.conflict_details
                               if detail['subject1'] == subject or detail['subject2'] == subject)
            
            self.subjects_tree.insert('', 'end',
                                    values=(subject, student_count, conflict_count))
    
    def update_matrix(self):
        """تحديث عرض المصفوفة"""
        # مسح المحتوى السابق
        for widget in self.matrix_inner_frame.winfo_children():
            widget.destroy()
        
        if self.conflict_matrix is None:
            return
        
        num_subjects = len(self.subjects)
        
        # إنشاء الجدول
        # صف العناوين
        tk.Label(self.matrix_inner_frame, text="المادة", font=('Arial', 10, 'bold'),
                bg='#3498db', fg='white', relief=tk.RAISED, bd=1,
                width=15).grid(row=0, column=0, sticky='nsew')
        
        for j, subject in enumerate(self.subjects):
            tk.Label(self.matrix_inner_frame, text=subject, font=('Arial', 9, 'bold'),
                    bg='#3498db', fg='white', relief=tk.RAISED, bd=1,
                    width=12).grid(row=0, column=j+1, sticky='nsew')
        
        # صفوف البيانات
        for i in range(num_subjects):
            # عمود أسماء المواد
            tk.Label(self.matrix_inner_frame, text=self.subjects[i],
                    font=('Arial', 9, 'bold'), bg='#ecf0f1',
                    relief=tk.RAISED, bd=1, width=15).grid(row=i+1, column=0, sticky='nsew')
            
            # خلايا المصفوفة
            for j in range(num_subjects):
                value = self.conflict_matrix[i][j]
                
                # تحديد اللون
                if i == j:
                    bg_color = '#f39c12'  # قطر رئيسي
                elif value == "نعم":
                    bg_color = '#e74c3c'  # تعارض
                else:
                    bg_color = '#2ecc71'  # لا يوجد تعارض
                
                tk.Label(self.matrix_inner_frame, text=value,
                        font=('Arial', 9, 'bold'), bg=bg_color, fg='white',
                        relief=tk.RAISED, bd=1, width=12).grid(row=i+1, column=j+1, sticky='nsew')
        
        # تحديث منطقة التمرير
        self.matrix_inner_frame.update_idletasks()
        self.matrix_canvas.configure(scrollregion=self.matrix_canvas.bbox('all'))
    
    def update_details(self):
        """تحديث تفاصيل التعارضات"""
        self.details_text.config(state=tk.NORMAL)
        self.details_text.delete(1.0, tk.END)
        
        if not self.conflict_details:
            self.details_text.insert(tk.END, "لا توجد تعارضات في البيانات الحالية.")
        else:
            details_content = "=== تفاصيل التعارضات ===\n\n"
            
            for i, detail in enumerate(self.conflict_details, 1):
                details_content += f"التعارض رقم {i}:\n"
                details_content += f"المواد المتعارضة: {detail['subject1']} ↔ {detail['subject2']}\n"
                details_content += f"عدد الطلاب المشتركين: {detail['common_count']}\n"
                details_content += f"إجمالي طلاب {detail['subject1']}: {detail['total_students1']}\n"
                details_content += f"إجمالي طلاب {detail['subject2']}: {detail['total_students2']}\n"
                details_content += f"نسبة التداخل من {detail['subject1']}: {detail['percentage1']:.2f}%\n"
                details_content += f"نسبة التداخل من {detail['subject2']}: {detail['percentage2']:.2f}%\n"
                
                # عرض الطلاب المشتركين
                if len(detail['common_students']) <= 20:
                    details_content += f"الطلاب المشتركون: {', '.join(detail['common_students'])}\n"
                else:
                    first_students = ', '.join(detail['common_students'][:20])
                    details_content += f"أول 20 طالب مشترك: {first_students}...\n"
                
                details_content += "-" * 60 + "\n\n"
            
            self.details_text.insert(tk.END, details_content)
        
        self.details_text.config(state=tk.DISABLED)
    
    def export_results(self):
        """تصدير النتائج إلى ملف Excel"""
        try:
            file_path = filedialog.asksaveasfilename(
                title="حفظ النتيجة",
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")]
            )
            
            if not file_path:
                return
            
            # إنشاء DataFrame للمصفوفة
            matrix_df = pd.DataFrame(self.conflict_matrix,
                                   columns=self.subjects,
                                   index=self.subjects)
            
            # إنشاء DataFrame للتفاصيل
            if self.conflict_details:
                details_data = []
                for detail in self.conflict_details:
                    details_data.append({
                        'المادة الأولى': detail['subject1'],
                        'المادة الثانية': detail['subject2'],
                        'عدد الطلاب المشتركين': detail['common_count'],
                        'إجمالي طلاب المادة الأولى': detail['total_students1'],
                        'إجمالي طلاب المادة الثانية': detail['total_students2'],
                        'نسبة التداخل من الأولى': f"{detail['percentage1']:.2f}%",
                        'نسبة التداخل من الثانية': f"{detail['percentage2']:.2f}%"
                    })
                details_df = pd.DataFrame(details_data)
            else:
                details_df = pd.DataFrame({'رسالة': ['لا توجد تعارضات']})
            
            # كتابة الملف
            with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                matrix_df.to_excel(writer, sheet_name='مصفوفة التعارض')
                details_df.to_excel(writer, sheet_name='تفاصيل التعارضات', index=False)
            
            messagebox.showinfo("نجح التصدير", f"تم حفظ النتيجة في:\n{file_path}")
            self.status_var.set("تم تصدير النتائج بنجاح! 💾")
            
        except Exception as e:
            self.show_error(f"خطأ في التصدير: {