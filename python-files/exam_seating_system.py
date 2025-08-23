"""
نظام إدارة جلوس الامتحانات مع استيراد من Excel
============================================

المتطلبات (يجب تثبيتها أولاً):
pip install pandas openpyxl tkinter

أو استخدام:
pip install pandas openpyxl

ملاحظة: tkinter عادة ما يكون مثبت مع Python

الميزات:
- إدارة شاملة للطلبة والقاعات والأقسام والمواد
- استيراد بيانات الطلبة من ملف Excel
- تصدير البيانات إلى Excel
- إنشاء قوالب Excel جاهزة
- إنشاء خرائط جلوس تلقائية
- واجهة مستخدم متطورة باللغة العربية
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
import json
import os
from datetime import datetime
import pandas as pd
import openpyxl


class ExamSeatingSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("نظام إدارة جلوس الامتحانات")
        self.root.geometry("1200x800")
        self.root.configure(bg='#f0f0f0')

        # تهيئة البيانات
        self.data = {
            'students': [],
            'classrooms': [],
            'departments': [],
            'subjects': [],
            'seating_maps': {}
        }

        # تحميل البيانات المحفوظة
        self.load_data()

        # إنشاء الواجهة الرئيسية
        self.create_main_interface()

    def create_main_interface(self):
        # الإطار الرئيسي
        main_frame = tk.Frame(self.root, bg='#f0f0f0')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # العنوان الرئيسي
        title_label = tk.Label(main_frame, text="نظام إدارة جلوس الامتحانات",
                               font=('Arial', 24, 'bold'), bg='#f0f0f0', fg='#2c3e50')
        title_label.pack(pady=20)

        # إطار الأزرار الرئيسية
        buttons_frame = tk.Frame(main_frame, bg='#f0f0f0')
        buttons_frame.pack(pady=20)

        # أزرار التنقل الرئيسية
        buttons = [
            ("إدارة الطلبة", self.manage_students, '#3498db'),
            ("إدارة القاعات", self.manage_classrooms, '#e74c3c'),
            ("إدارة الأقسام", self.manage_departments, '#f39c12'),
            ("إدارة المواد", self.manage_subjects, '#27ae60'),
            ("خرائط الجلوس", self.manage_seating_maps, '#9b59b6'),
            ("حفظ البيانات", self.save_data, '#34495e')
        ]

        for i, (text, command, color) in enumerate(buttons):
            row = i // 3
            col = i % 3
            btn = tk.Button(buttons_frame, text=text, command=command,
                            font=('Arial', 14, 'bold'), bg=color, fg='white',
                            width=15, height=2, relief='raised', bd=3)
            btn.grid(row=row, column=col, padx=10, pady=10)

            # تأثير hover
            btn.bind('<Enter>', lambda e, b=btn, c=color: b.configure(bg=self.darken_color(c)))
            btn.bind('<Leave>', lambda e, b=btn, c=color: b.configure(bg=c))

    def darken_color(self, color):
        # تغميق اللون للتأثير
        colors = {
            '#3498db': '#2980b9',
            '#e74c3c': '#c0392b',
            '#f39c12': '#d68910',
            '#27ae60': '#229954',
            '#9b59b6': '#8e44ad',
            '#34495e': '#2c3e50'
        }
        return colors.get(color, color)

    def manage_students(self):
        self.open_students_window()

    def manage_classrooms(self):
        self.open_classrooms_window()

    def manage_departments(self):
        self.open_departments_window()

    def manage_subjects(self):
        self.open_subjects_window()

    def manage_seating_maps(self):
        self.open_seating_maps_window()

    def open_students_window(self):
        students_window = tk.Toplevel(self.root)
        students_window.title("إدارة الطلبة")
        students_window.geometry("1000x600")
        students_window.configure(bg='#ecf0f1')

        # الإطار الرئيسي
        main_frame = tk.Frame(students_window, bg='#ecf0f1')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # العنوان
        title = tk.Label(main_frame, text="إدارة الطلبة", font=('Arial', 18, 'bold'),
                         bg='#ecf0f1', fg='#2c3e50')
        title.pack(pady=10)

        # إطار الإدخال
        input_frame = tk.LabelFrame(main_frame, text="إضافة/تعديل طالب",
                                    font=('Arial', 12, 'bold'), bg='#ecf0f1', fg='#34495e')
        input_frame.pack(fill=tk.X, pady=10)

        # حقول الإدخال
        tk.Label(input_frame, text="الاسم:", bg='#ecf0f1').grid(row=0, column=0, padx=5, pady=5, sticky='e')
        name_entry = tk.Entry(input_frame, width=20, font=('Arial', 10))
        name_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(input_frame, text="الرقم الجامعي:", bg='#ecf0f1').grid(row=0, column=2, padx=5, pady=5, sticky='e')
        id_entry = tk.Entry(input_frame, width=15, font=('Arial', 10))
        id_entry.grid(row=0, column=3, padx=5, pady=5)

        tk.Label(input_frame, text="القسم:", bg='#ecf0f1').grid(row=1, column=0, padx=5, pady=5, sticky='e')
        dept_combo = ttk.Combobox(input_frame, width=17, state='readonly')
        dept_combo['values'] = [dept['name'] for dept in self.data['departments']]
        dept_combo.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(input_frame, text="المستوى:", bg='#ecf0f1').grid(row=1, column=2, padx=5, pady=5, sticky='e')
        level_combo = ttk.Combobox(input_frame, width=12, state='readonly')
        level_combo['values'] = ['الأول', 'الثاني', 'الثالث', 'الرابع', 'الخامس']
        level_combo.grid(row=1, column=3, padx=5, pady=5)

        # أزرار التحكم
        buttons_frame = tk.Frame(input_frame, bg='#ecf0f1')
        buttons_frame.grid(row=2, column=0, columnspan=4, pady=10)

        def add_student():
            name = name_entry.get().strip()
            student_id = id_entry.get().strip()
            dept = dept_combo.get()
            level = level_combo.get()

            if not all([name, student_id, dept, level]):
                messagebox.showerror("خطأ", "يرجى ملء جميع الحقول")
                return

            # التحقق من عدم تكرار الرقم الجامعي
            if any(s['id'] == student_id for s in self.data['students']):
                messagebox.showerror("خطأ", "الرقم الجامعي موجود بالفعل")
                return

            student = {
                'name': name,
                'id': student_id,
                'department': dept,
                'level': level,
                'created_at': datetime.now().isoformat()
            }

            self.data['students'].append(student)
            refresh_list()
            clear_fields()
            messagebox.showinfo("نجح", "تم إضافة الطالب بنجاح")

        def update_student():
            selection = students_tree.selection()
            if not selection:
                messagebox.showerror("خطأ", "يرجى اختيار طالب للتعديل")
                return

            item = students_tree.item(selection[0])
            old_id = item['values'][1]

            name = name_entry.get().strip()
            student_id = id_entry.get().strip()
            dept = dept_combo.get()
            level = level_combo.get()

            if not all([name, student_id, dept, level]):
                messagebox.showerror("خطأ", "يرجى ملء جميع الحقول")
                return

            # العثور على الطالب وتحديثه
            for student in self.data['students']:
                if student['id'] == old_id:
                    student['name'] = name
                    student['id'] = student_id
                    student['department'] = dept
                    student['level'] = level
                    break

            refresh_list()
            clear_fields()
            messagebox.showinfo("نجح", "تم تحديث بيانات الطالب بنجاح")

        def delete_student():
            selection = students_tree.selection()
            if not selection:
                messagebox.showerror("خطأ", "يرجى اختيار طالب للحذف")
                return

            if messagebox.askyesno("تأكيد", "هل تريد حذف الطالب المحدد؟"):
                item = students_tree.item(selection[0])
                student_id = item['values'][1]

                self.data['students'] = [s for s in self.data['students'] if s['id'] != student_id]
                refresh_list()
                clear_fields()
                messagebox.showinfo("نجح", "تم حذف الطالب بنجاح")

        def clear_fields():
            name_entry.delete(0, tk.END)
            id_entry.delete(0, tk.END)
            dept_combo.set('')
            level_combo.set('')

        def import_from_excel():
            """استيراد بيانات الطلبة من ملف Excel"""
            file_path = filedialog.askopenfilename(
                title="اختر ملف Excel",
                filetypes=[("Excel files", "*.xlsx *.xls"), ("All files", "*.*")]
            )

            if not file_path:
                return

            try:
                # قراءة ملف Excel
                df = pd.read_excel(file_path)

                # التحقق من وجود الأعمدة المطلوبة
                required_columns = ['الاسم', 'الرقم الجامعي', 'القسم', 'المستوى']
                missing_columns = []

                for col in required_columns:
                    if col not in df.columns:
                        # البحث عن أعمدة مشابهة
                        similar_cols = [c for c in df.columns if any(word in c for word in col.split())]
                        if similar_cols:
                            df = df.rename(columns={similar_cols[0]: col})
                        else:
                            missing_columns.append(col)

                if missing_columns:
                    # إظهار نافذة لربط الأعمدة
                    mapping_window = tk.Toplevel(students_window)
                    mapping_window.title("ربط أعمدة Excel")
                    mapping_window.geometry("600x400")
                    mapping_window.configure(bg='#ecf0f1')

                    tk.Label(mapping_window, text="يرجى ربط أعمدة Excel بالحقول المطلوبة:",
                             font=('Arial', 14, 'bold'), bg='#ecf0f1').pack(pady=10)

                    mappings = {}

                    for i, req_col in enumerate(required_columns):
                        frame = tk.Frame(mapping_window, bg='#ecf0f1')
                        frame.pack(fill=tk.X, padx=20, pady=5)

                        tk.Label(frame, text=f"{req_col}:", font=('Arial', 12),
                                 bg='#ecf0f1', width=15).pack(side=tk.LEFT)

                        combo = ttk.Combobox(frame, values=list(df.columns), width=25, state='readonly')
                        combo.pack(side=tk.LEFT, padx=10)
                        mappings[req_col] = combo

                        # محاولة تخمين العمود المناسب
                        for col in df.columns:
                            if any(word in col for word in req_col.split()):
                                combo.set(col)
                                break

                    def apply_mapping():
                        nonlocal df
                        try:
                            for req_col, combo in mappings.items():
                                excel_col = combo.get()
                                if excel_col and excel_col in df.columns:
                                    df = df.rename(columns={excel_col: req_col})
                            mapping_window.destroy()
                            process_excel_data()
                        except Exception as e:
                            messagebox.showerror("خطأ", f"خطأ في ربط الأعمدة: {str(e)}")

                    tk.Button(mapping_window, text="تطبيق", command=apply_mapping,
                              bg='#27ae60', fg='white', font=('Arial', 12, 'bold')).pack(pady=20)

                    return

                process_excel_data()

                def process_excel_data():
                    """معالجة بيانات Excel بعد التأكد من الأعمدة"""
                    imported_count = 0
                    skipped_count = 0
                    errors = []

                    for index, row in df.iterrows():
                        try:
                            # تنظيف البيانات
                            name = str(row['الاسم']).strip() if pd.notna(row['الاسم']) else ''
                            student_id = str(row['الرقم الجامعي']).strip() if pd.notna(row['الرقم الجامعي']) else ''
                            department = str(row['القسم']).strip() if pd.notna(row['القسم']) else ''
                            level = str(row['المستوى']).strip() if pd.notna(row['المستوى']) else ''

                            # تنظيف الرقم الجامعي من الأرقام العشرية
                            if '.' in student_id:
                                student_id = student_id.split('.')[0]

                            # التحقق من البيانات المطلوبة
                            if not all([name, student_id, department, level]):
                                skipped_count += 1
                                errors.append(f"الصف {index + 2}: بيانات ناقصة")
                                continue

                            # التحقق من عدم تكرار الرقم الجامعي
                            if any(s['id'] == student_id for s in self.data['students']):
                                skipped_count += 1
                                errors.append(f"الصف {index + 2}: الرقم الجامعي {student_id} موجود بالفعل")
                                continue

                            # التأكد من وجود القسم
                            dept_exists = any(d['name'] == department for d in self.data['departments'])
                            if not dept_exists:
                                # إضافة القسم تلقائياً
                                new_dept = {
                                    'name': department,
                                    'created_at': datetime.now().isoformat()
                                }
                                self.data['departments'].append(new_dept)

                            # إضافة الطالب
                            student = {
                                'name': name,
                                'id': student_id,
                                'department': department,
                                'level': level,
                                'created_at': datetime.now().isoformat(),
                                'imported': True
                            }

                            self.data['students'].append(student)
                            imported_count += 1

                        except Exception as e:
                            skipped_count += 1
                            errors.append(f"الصف {index + 2}: خطأ - {str(e)}")

                    # تحديث القائمة
                    refresh_list()

                    # إظهار نتائج الاستيراد
                    result_message = f"تم استيراد {imported_count} طالب بنجاح"
                    if skipped_count > 0:
                        result_message += f"\nتم تخطي {skipped_count} صف"

                    if errors and len(errors) <= 10:  # إظهار أول 10 أخطاء فقط
                        result_message += "\n\nالأخطاء:\n" + "\n".join(errors[:10])
                        if len(errors) > 10:
                            result_message += f"\n... و {len(errors) - 10} خطأ آخر"

                    messagebox.showinfo("نتائج الاستيراد", result_message)

            except Exception as e:
                messagebox.showerror("خطأ", f"فشل في قراءة ملف Excel: {str(e)}")

        def export_to_excel():
            """تصدير بيانات الطلبة إلى ملف Excel"""
            if not self.data['students']:
                messagebox.showwarning("تحذير", "لا توجد بيانات طلبة للتصدير")
                return

            file_path = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
                title="حفظ ملف Excel"
            )

            if not file_path:
                return

            try:
                # إنشاء DataFrame
                data_for_export = []
                for student in self.data['students']:
                    data_for_export.append({
                        'الاسم': student['name'],
                        'الرقم الجامعي': student['id'],
                        'القسم': student['department'],
                        'المستوى': student['level'],
                        'تاريخ الإضافة': student.get('created_at', '')
                    })

                df = pd.DataFrame(data_for_export)

                # حفظ الملف
                with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                    df.to_excel(writer, sheet_name='بيانات الطلبة', index=False)

                    # تنسيق الجدول
                    worksheet = writer.sheets['بيانات الطلبة']

                    # تعديل عرض الأعمدة
                    for column in worksheet.columns:
                        max_length = 0
                        column_letter = column[0].column_letter
                        for cell in column:
                            try:
                                if len(str(cell.value)) > max_length:
                                    max_length = len(str(cell.value))
                            except:
                                pass
                        adjusted_width = min(max_length + 2, 50)
                        worksheet.column_dimensions[column_letter].width = adjusted_width

                messagebox.showinfo("نجح", f"تم تصدير {len(self.data['students'])} طالب إلى ملف Excel بنجاح")

            except Exception as e:
                messagebox.showerror("خطأ", f"فشل في تصدير البيانات: {str(e)}")

        def create_excel_template():
            """إنشاء قالب Excel للاستيراد"""
            file_path = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx")],
                title="حفظ قالب Excel",
                initialvalue="قالب_بيانات_الطلبة.xlsx"
            )

            if not file_path:
                return

            try:
                # إنشاء بيانات تجريبية
                template_data = {
                    'الاسم': ['أحمد محمد علي', 'فاطمة أحمد', 'محمد سالم'],
                    'الرقم الجامعي': ['20210001', '20210002', '20210003'],
                    'القسم': ['علوم الحاسوب', 'الرياضيات', 'علوم الحاسوب'],
                    'المستوى': ['الثاني', 'الأول', 'الثالث']
                }

                df = pd.DataFrame(template_data)

                with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                    df.to_excel(writer, sheet_name='بيانات الطلبة', index=False)

                    worksheet = writer.sheets['بيانات الطلبة']

                    # تنسيق الرأس
                    from openpyxl.styles import Font, PatternFill
                    header_font = Font(bold=True, color="FFFFFF")
                    header_fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")

                    for cell in worksheet[1]:
                        cell.font = header_font
                        cell.fill = header_fill

                    # تعديل عرض الأعمدة
                    for column in worksheet.columns:
                        max_length = 0
                        column_letter = column[0].column_letter
                        for cell in column:
                            try:
                                if len(str(cell.value)) > max_length:
                                    max_length = len(str(cell.value))
                            except:
                                pass
                        adjusted_width = max_length + 2
                        worksheet.column_dimensions[column_letter].width = adjusted_width

                messagebox.showinfo("نجح", "تم إنشاء قالب Excel بنجاح!\nيمكنك تعديل البيانات ثم استيرادها.")

            except Exception as e:
                messagebox.showerror("خطأ", f"فشل في إنشاء القالب: {str(e)}")

        def on_select(event):
            selection = students_tree.selection()
            if selection:
                item = students_tree.item(selection[0])
                values = item['values']

                clear_fields()
                name_entry.insert(0, values[0])
                id_entry.insert(0, values[1])
                dept_combo.set(values[2])
                level_combo.set(values[3])

        tk.Button(buttons_frame, text="إضافة", command=add_student, bg='#27ae60', fg='white',
                  font=('Arial', 10, 'bold'), width=10).pack(side=tk.LEFT, padx=5)
        tk.Button(buttons_frame, text="تعديل", command=update_student, bg='#f39c12', fg='white',
                  font=('Arial', 10, 'bold'), width=10).pack(side=tk.LEFT, padx=5)
        tk.Button(buttons_frame, text="حذف", command=delete_student, bg='#e74c3c', fg='white',
                  font=('Arial', 10, 'bold'), width=10).pack(side=tk.LEFT, padx=5)
        tk.Button(buttons_frame, text="مسح", command=clear_fields, bg='#95a5a6', fg='white',
                  font=('Arial', 10, 'bold'), width=10).pack(side=tk.LEFT, padx=5)

        # أزرار Excel
        excel_frame = tk.Frame(input_frame, bg='#ecf0f1')
        excel_frame.grid(row=3, column=0, columnspan=4, pady=10)

        tk.Button(excel_frame, text="📥 استيراد من Excel", command=import_from_excel,
                  bg='#9b59b6', fg='white', font=('Arial', 10, 'bold'), width=15).pack(side=tk.LEFT, padx=5)
        tk.Button(excel_frame, text="📤 تصدير إلى Excel", command=export_to_excel,
                  bg='#16a085', fg='white', font=('Arial', 10, 'bold'), width=15).pack(side=tk.LEFT, padx=5)
        tk.Button(excel_frame, text="📋 إنشاء قالب Excel", command=create_excel_template,
                  bg='#d35400', fg='white', font=('Arial', 10, 'bold'), width=15).pack(side=tk.LEFT, padx=5)

        # إطار المساعدة لـ Excel
        help_frame = tk.LabelFrame(main_frame, text="إرشادات استيراد Excel",
                                   font=('Arial', 12, 'bold'), bg='#ecf0f1', fg='#34495e')
        help_frame.pack(fill=tk.X, pady=10)

        help_text = """📋 إرشادات تحضير ملف Excel:
• يجب أن يحتوي ملف Excel على الأعمدة التالية: الاسم، الرقم الجامعي، القسم، المستوى
• يمكن استخدام أسماء أعمدة مشابهة مثل: Name، Student ID، Department، Level
• تأكد من عدم وجود صفوف فارغة في منتصف البيانات
• يمكن إنشاء قالب جاهز باستخدام زر "إنشاء قالب Excel" """

        tk.Label(help_frame, text=help_text, bg='#ecf0f1', fg='#2c3e50',
                 font=('Arial', 9), justify=tk.LEFT).pack(padx=10, pady=5, anchor='w')

        # قائمة الطلبة
        list_frame = tk.LabelFrame(main_frame, text="قائمة الطلبة",
                                   font=('Arial', 12, 'bold'), bg='#ecf0f1', fg='#34495e')
        list_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        # إطار البحث والتصفية
        search_frame = tk.Frame(list_frame, bg='#ecf0f1')
        search_frame.pack(fill=tk.X, padx=10, pady=5)

        tk.Label(search_frame, text="البحث:", bg='#ecf0f1').pack(side=tk.LEFT, padx=5)
        search_entry = tk.Entry(search_frame, width=20, font=('Arial', 10))
        search_entry.pack(side=tk.LEFT, padx=5)

        tk.Label(search_frame, text="تصفية حسب القسم:", bg='#ecf0f1').pack(side=tk.LEFT, padx=5)
        filter_combo = ttk.Combobox(search_frame, width=15, state='readonly')
        filter_combo['values'] = ['الكل'] + [dept['name'] for dept in self.data['departments']]
        filter_combo.set('الكل')
        filter_combo.pack(side=tk.LEFT, padx=5)

        def search_students():
            refresh_list()

        tk.Button(search_frame, text="بحث", command=search_students, bg='#3498db', fg='white',
                  font=('Arial', 9, 'bold'), width=8).pack(side=tk.LEFT, padx=5)

        # ربط البحث بالكتابة
        search_entry.bind('<KeyRelease>', lambda e: refresh_list())
        filter_combo.bind('<<ComboboxSelected>>', lambda e: refresh_list())

        # شجرة البيانات
        columns = ('name', 'id', 'department', 'level')
        students_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=15)

        # تحديد عناوين الأعمدة
        students_tree.heading('name', text='الاسم')
        students_tree.heading('id', text='الرقم الجامعي')
        students_tree.heading('department', text='القسم')
        students_tree.heading('level', text='المستوى')

        # تحديد عرض الأعمدة
        students_tree.column('name', width=250)
        students_tree.column('id', width=150)
        students_tree.column('department', width=200)
        students_tree.column('level', width=100)

        students_tree.bind('<<TreeviewSelect>>', on_select)

        # شريط التمرير
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=students_tree.yview)
        students_tree.configure(yscrollcommand=scrollbar.set)

        students_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        def refresh_list():
            students_tree.delete(*students_tree.get_children())

            # الحصول على معايير البحث والتصفية
            search_term = search_entry.get().lower()
            dept_filter = filter_combo.get()

            for student in self.data['students']:
                # تطبيق البحث
                if search_term and search_term not in student['name'].lower() and search_term not in student[
                    'id'].lower():
                    continue

                # تطبيق تصفية القسم
                if dept_filter != 'الكل' and student['department'] != dept_filter:
                    continue

                # إضافة أيقونة للطلبة المستوردين
                name_display = student['name']
                if student.get('imported', False):
                    name_display += " 📥"

                students_tree.insert('', 'end', values=(
                    name_display, student['id'], student['department'], student['level']
                ))

        refresh_list()

    def open_classrooms_window(self):
        classrooms_window = tk.Toplevel(self.root)
        classrooms_window.title("إدارة القاعات الدراسية")
        classrooms_window.geometry("900x600")
        classrooms_window.configure(bg='#ecf0f1')

        main_frame = tk.Frame(classrooms_window, bg='#ecf0f1')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        title = tk.Label(main_frame, text="إدارة القاعات الدراسية", font=('Arial', 18, 'bold'),
                         bg='#ecf0f1', fg='#2c3e50')
        title.pack(pady=10)

        # إطار الإدخال
        input_frame = tk.LabelFrame(main_frame, text="إضافة/تعديل قاعة",
                                    font=('Arial', 12, 'bold'), bg='#ecf0f1', fg='#34495e')
        input_frame.pack(fill=tk.X, pady=10)

        tk.Label(input_frame, text="اسم القاعة:", bg='#ecf0f1').grid(row=0, column=0, padx=5, pady=5, sticky='e')
        name_entry = tk.Entry(input_frame, width=20, font=('Arial', 10))
        name_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(input_frame, text="السعة:", bg='#ecf0f1').grid(row=0, column=2, padx=5, pady=5, sticky='e')
        capacity_entry = tk.Entry(input_frame, width=10, font=('Arial', 10))
        capacity_entry.grid(row=0, column=3, padx=5, pady=5)

        tk.Label(input_frame, text="عدد الصفوف:", bg='#ecf0f1').grid(row=1, column=0, padx=5, pady=5, sticky='e')
        rows_entry = tk.Entry(input_frame, width=10, font=('Arial', 10))
        rows_entry.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(input_frame, text="عدد الأعمدة:", bg='#ecf0f1').grid(row=1, column=2, padx=5, pady=5, sticky='e')
        cols_entry = tk.Entry(input_frame, width=10, font=('Arial', 10))
        cols_entry.grid(row=1, column=3, padx=5, pady=5)

        def add_classroom():
            name = name_entry.get().strip()
            try:
                capacity = int(capacity_entry.get())
                rows = int(rows_entry.get())
                cols = int(cols_entry.get())
            except ValueError:
                messagebox.showerror("خطأ", "يرجى إدخال أرقام صحيحة")
                return

            if not name:
                messagebox.showerror("خطأ", "يرجى إدخال اسم القاعة")
                return

            if any(c['name'] == name for c in self.data['classrooms']):
                messagebox.showerror("خطأ", "اسم القاعة موجود بالفعل")
                return

            classroom = {
                'name': name,
                'capacity': capacity,
                'rows': rows,
                'cols': cols,
                'created_at': datetime.now().isoformat()
            }

            self.data['classrooms'].append(classroom)
            refresh_list()
            clear_fields()
            messagebox.showinfo("نجح", "تم إضافة القاعة بنجاح")

        def delete_classroom():
            selection = classrooms_tree.selection()
            if not selection:
                messagebox.showerror("خطأ", "يرجى اختيار قاعة للحذف")
                return

            if messagebox.askyesno("تأكيد", "هل تريد حذف القاعة المحددة؟"):
                item = classrooms_tree.item(selection[0])
                classroom_name = item['values'][0]

                self.data['classrooms'] = [c for c in self.data['classrooms'] if c['name'] != classroom_name]
                refresh_list()
                clear_fields()
                messagebox.showinfo("نجح", "تم حذف القاعة بنجاح")

        def clear_fields():
            name_entry.delete(0, tk.END)
            capacity_entry.delete(0, tk.END)
            rows_entry.delete(0, tk.END)
            cols_entry.delete(0, tk.END)

        buttons_frame = tk.Frame(input_frame, bg='#ecf0f1')
        buttons_frame.grid(row=2, column=0, columnspan=4, pady=10)

        tk.Button(buttons_frame, text="إضافة", command=add_classroom, bg='#27ae60', fg='white',
                  font=('Arial', 10, 'bold'), width=10).pack(side=tk.LEFT, padx=5)
        tk.Button(buttons_frame, text="حذف", command=delete_classroom, bg='#e74c3c', fg='white',
                  font=('Arial', 10, 'bold'), width=10).pack(side=tk.LEFT, padx=5)
        tk.Button(buttons_frame, text="مسح", command=clear_fields, bg='#95a5a6', fg='white',
                  font=('Arial', 10, 'bold'), width=10).pack(side=tk.LEFT, padx=5)

        # قائمة القاعات
        list_frame = tk.LabelFrame(main_frame, text="قائمة القاعات",
                                   font=('Arial', 12, 'bold'), bg='#ecf0f1', fg='#34495e')
        list_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        columns = ('name', 'capacity', 'rows', 'cols')
        classrooms_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=15)

        classrooms_tree.heading('name', text='اسم القاعة')
        classrooms_tree.heading('capacity', text='السعة')
        classrooms_tree.heading('rows', text='الصفوف')
        classrooms_tree.heading('cols', text='الأعمدة')

        classrooms_tree.column('name', width=200)
        classrooms_tree.column('capacity', width=100)
        classrooms_tree.column('rows', width=100)
        classrooms_tree.column('cols', width=100)

        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=classrooms_tree.yview)
        classrooms_tree.configure(yscrollcommand=scrollbar.set)

        classrooms_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        def refresh_list():
            classrooms_tree.delete(*classrooms_tree.get_children())
            for classroom in self.data['classrooms']:
                classrooms_tree.insert('', 'end', values=(
                    classroom['name'], classroom['capacity'], classroom['rows'], classroom['cols']
                ))

        refresh_list()

    def open_departments_window(self):
        dept_window = tk.Toplevel(self.root)
        dept_window.title("إدارة الأقسام")
        dept_window.geometry("700x500")
        dept_window.configure(bg='#ecf0f1')

        main_frame = tk.Frame(dept_window, bg='#ecf0f1')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        title = tk.Label(main_frame, text="إدارة الأقسام", font=('Arial', 18, 'bold'),
                         bg='#ecf0f1', fg='#2c3e50')
        title.pack(pady=10)

        input_frame = tk.LabelFrame(main_frame, text="إضافة قسم جديد",
                                    font=('Arial', 12, 'bold'), bg='#ecf0f1', fg='#34495e')
        input_frame.pack(fill=tk.X, pady=10)

        tk.Label(input_frame, text="اسم القسم:", bg='#ecf0f1').grid(row=0, column=0, padx=5, pady=5, sticky='e')
        name_entry = tk.Entry(input_frame, width=30, font=('Arial', 10))
        name_entry.grid(row=0, column=1, padx=5, pady=5)

        def add_department():
            name = name_entry.get().strip()
            if not name:
                messagebox.showerror("خطأ", "يرجى إدخال اسم القسم")
                return

            if any(d['name'] == name for d in self.data['departments']):
                messagebox.showerror("خطأ", "القسم موجود بالفعل")
                return

            department = {
                'name': name,
                'created_at': datetime.now().isoformat()
            }

            self.data['departments'].append(department)
            refresh_list()
            name_entry.delete(0, tk.END)
            messagebox.showinfo("نجح", "تم إضافة القسم بنجاح")

        def delete_department():
            selection = dept_tree.selection()
            if not selection:
                messagebox.showerror("خطأ", "يرجى اختيار قسم للحذف")
                return

            if messagebox.askyesno("تأكيد", "هل تريد حذف القسم المحدد؟"):
                item = dept_tree.item(selection[0])
                dept_name = item['values'][0]

                self.data['departments'] = [d for d in self.data['departments'] if d['name'] != dept_name]
                refresh_list()
                messagebox.showinfo("نجح", "تم حذف القسم بنجاح")

        buttons_frame = tk.Frame(input_frame, bg='#ecf0f1')
        buttons_frame.grid(row=1, column=0, columnspan=2, pady=10)

        tk.Button(buttons_frame, text="إضافة", command=add_department, bg='#27ae60', fg='white',
                  font=('Arial', 10, 'bold'), width=10).pack(side=tk.LEFT, padx=5)
        tk.Button(buttons_frame, text="حذف", command=delete_department, bg='#e74c3c', fg='white',
                  font=('Arial', 10, 'bold'), width=10).pack(side=tk.LEFT, padx=5)

        list_frame = tk.LabelFrame(main_frame, text="قائمة الأقسام",
                                   font=('Arial', 12, 'bold'), bg='#ecf0f1', fg='#34495e')
        list_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        columns = ('name',)
        dept_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=15)
        dept_tree.heading('name', text='اسم القسم')
        dept_tree.column('name', width=300)

        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=dept_tree.yview)
        dept_tree.configure(yscrollcommand=scrollbar.set)

        dept_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        def refresh_list():
            dept_tree.delete(*dept_tree.get_children())
            for dept in self.data['departments']:
                dept_tree.insert('', 'end', values=(dept['name'],))

        refresh_list()

    def open_subjects_window(self):
        subjects_window = tk.Toplevel(self.root)
        subjects_window.title("إدارة المواد")
        subjects_window.geometry("800x600")
        subjects_window.configure(bg='#ecf0f1')

        main_frame = tk.Frame(subjects_window, bg='#ecf0f1')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        title = tk.Label(main_frame, text="إدارة المواد الدراسية", font=('Arial', 18, 'bold'),
                         bg='#ecf0f1', fg='#2c3e50')
        title.pack(pady=10)

        input_frame = tk.LabelFrame(main_frame, text="إضافة مادة جديدة",
                                    font=('Arial', 12, 'bold'), bg='#ecf0f1', fg='#34495e')
        input_frame.pack(fill=tk.X, pady=10)

        tk.Label(input_frame, text="اسم المادة:", bg='#ecf0f1').grid(row=0, column=0, padx=5, pady=5, sticky='e')
        name_entry = tk.Entry(input_frame, width=25, font=('Arial', 10))
        name_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(input_frame, text="رمز المادة:", bg='#ecf0f1').grid(row=0, column=2, padx=5, pady=5, sticky='e')
        code_entry = tk.Entry(input_frame, width=15, font=('Arial', 10))
        code_entry.grid(row=0, column=3, padx=5, pady=5)

        tk.Label(input_frame, text="القسم:", bg='#ecf0f1').grid(row=1, column=0, padx=5, pady=5, sticky='e')
        dept_combo = ttk.Combobox(input_frame, width=22, state='readonly')
        dept_combo['values'] = [dept['name'] for dept in self.data['departments']]
        dept_combo.grid(row=1, column=1, padx=5, pady=5)

        def add_subject():
            name = name_entry.get().strip()
            code = code_entry.get().strip()
            dept = dept_combo.get()

            if not all([name, code, dept]):
                messagebox.showerror("خطأ", "يرجى ملء جميع الحقول")
                return

            if any(s['code'] == code for s in self.data['subjects']):
                messagebox.showerror("خطأ", "رمز المادة موجود بالفعل")
                return

            subject = {
                'name': name,
                'code': code,
                'department': dept,
                'created_at': datetime.now().isoformat()
            }

            self.data['subjects'].append(subject)
            refresh_list()
            clear_fields()
            messagebox.showinfo("نجح", "تم إضافة المادة بنجاح")

        def delete_subject():
            selection = subjects_tree.selection()
            if not selection:
                messagebox.showerror("خطأ", "يرجى اختيار مادة للحذف")
                return

            if messagebox.askyesno("تأكيد", "هل تريد حذف المادة المحددة؟"):
                item = subjects_tree.item(selection[0])
                subject_code = item['values'][1]

                self.data['subjects'] = [s for s in self.data['subjects'] if s['code'] != subject_code]
                refresh_list()
                clear_fields()
                messagebox.showinfo("نجح", "تم حذف المادة بنجاح")

        def clear_fields():
            name_entry.delete(0, tk.END)
            code_entry.delete(0, tk.END)
            dept_combo.set('')

        buttons_frame = tk.Frame(input_frame, bg='#ecf0f1')
        buttons_frame.grid(row=2, column=0, columnspan=4, pady=10)

        tk.Button(buttons_frame, text="إضافة", command=add_subject, bg='#27ae60', fg='white',
                  font=('Arial', 10, 'bold'), width=10).pack(side=tk.LEFT, padx=5)
        tk.Button(buttons_frame, text="حذف", command=delete_subject, bg='#e74c3c', fg='white',
                  font=('Arial', 10, 'bold'), width=10).pack(side=tk.LEFT, padx=5)
        tk.Button(buttons_frame, text="مسح", command=clear_fields, bg='#95a5a6', fg='white',
                  font=('Arial', 10, 'bold'), width=10).pack(side=tk.LEFT, padx=5)

        list_frame = tk.LabelFrame(main_frame, text="قائمة المواد",
                                   font=('Arial', 12, 'bold'), bg='#ecf0f1', fg='#34495e')
        list_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        columns = ('name', 'code', 'department')
        subjects_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=15)

        subjects_tree.heading('name', text='اسم المادة')
        subjects_tree.heading('code', text='رمز المادة')
        subjects_tree.heading('department', text='القسم')

        subjects_tree.column('name', width=250)
        subjects_tree.column('code', width=100)
        subjects_tree.column('department', width=200)

        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=subjects_tree.yview)
        subjects_tree.configure(yscrollcommand=scrollbar.set)

        subjects_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        def refresh_list():
            subjects_tree.delete(*subjects_tree.get_children())
            for subject in self.data['subjects']:
                subjects_tree.insert('', 'end', values=(
                    subject['name'], subject['code'], subject['department']
                ))

        refresh_list()

    def open_seating_maps_window(self):
        seating_window = tk.Toplevel(self.root)
        seating_window.title("إدارة خرائط الجلوس")
        seating_window.geometry("1400x800")
        seating_window.configure(bg='#ecf0f1')

        main_frame = tk.Frame(seating_window, bg='#ecf0f1')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        title = tk.Label(main_frame, text="إدارة خرائط الجلوس", font=('Arial', 18, 'bold'),
                         bg='#ecf0f1', fg='#2c3e50')
        title.pack(pady=10)

        # إطار التحكم
        control_frame = tk.LabelFrame(main_frame, text="إنشاء خريطة جلوس جديدة",
                                      font=('Arial', 12, 'bold'), bg='#ecf0f1', fg='#34495e')
        control_frame.pack(fill=tk.X, pady=10)

        # الصف الأول من التحكم
        row1_frame = tk.Frame(control_frame, bg='#ecf0f1')
        row1_frame.pack(fill=tk.X, pady=5)

        tk.Label(row1_frame, text="القاعة:", bg='#ecf0f1').pack(side=tk.LEFT, padx=5)
        classroom_combo = ttk.Combobox(row1_frame, width=20, state='readonly')
        classroom_combo['values'] = [c['name'] for c in self.data['classrooms']]
        classroom_combo.pack(side=tk.LEFT, padx=5)

        tk.Label(row1_frame, text="المادة:", bg='#ecf0f1').pack(side=tk.LEFT, padx=5)
        subject_combo = ttk.Combobox(row1_frame, width=20, state='readonly')
        subject_combo['values'] = [f"{s['name']} ({s['code']})" for s in self.data['subjects']]
        subject_combo.pack(side=tk.LEFT, padx=5)

        tk.Label(row1_frame, text="تاريخ الامتحان:", bg='#ecf0f1').pack(side=tk.LEFT, padx=5)
        date_entry = tk.Entry(row1_frame, width=15, font=('Arial', 10))
        date_entry.pack(side=tk.LEFT, padx=5)

        # الصف الثاني من التحكم
        row2_frame = tk.Frame(control_frame, bg='#ecf0f1')
        row2_frame.pack(fill=tk.X, pady=5)

        tk.Label(row2_frame, text="القسم:", bg='#ecf0f1').pack(side=tk.LEFT, padx=5)
        filter_dept_combo = ttk.Combobox(row2_frame, width=20, state='readonly')
        filter_dept_combo['values'] = ['الكل'] + [d['name'] for d in self.data['departments']]
        filter_dept_combo.set('الكل')
        filter_dept_combo.pack(side=tk.LEFT, padx=5)

        tk.Label(row2_frame, text="المستوى:", bg='#ecf0f1').pack(side=tk.LEFT, padx=5)
        filter_level_combo = ttk.Combobox(row2_frame, width=15, state='readonly')
        filter_level_combo['values'] = ['الكل', 'الأول', 'الثاني', 'الثالث', 'الرابع', 'الخامس']
        filter_level_combo.set('الكل')
        filter_level_combo.pack(side=tk.LEFT, padx=5)

        def create_seating_map():
            classroom_name = classroom_combo.get()
            subject_text = subject_combo.get()
            exam_date = date_entry.get().strip()
            dept_filter = filter_dept_combo.get()
            level_filter = filter_level_combo.get()

            if not all([classroom_name, subject_text, exam_date]):
                messagebox.showerror("خطأ", "يرجى ملء جميع الحقول المطلوبة")
                return

            # العثور على القاعة
            classroom = next((c for c in self.data['classrooms'] if c['name'] == classroom_name), None)
            if not classroom:
                messagebox.showerror("خطأ", "القاعة غير موجودة")
                return

            # تصفية الطلبة
            filtered_students = self.data['students'][:]
            if dept_filter != 'الكل':
                filtered_students = [s for s in filtered_students if s['department'] == dept_filter]
            if level_filter != 'الكل':
                filtered_students = [s for s in filtered_students if s['level'] == level_filter]

            if not filtered_students:
                messagebox.showerror("خطأ", "لا توجد طلبة مطابقة للمعايير المحددة")
                return

            # التحقق من سعة القاعة
            if len(filtered_students) > classroom['capacity']:
                if not messagebox.askyesno("تحذير",
                                           f"عدد الطلبة ({len(filtered_students)}) أكبر من سعة القاعة ({classroom['capacity']}). هل تريد المتابعة؟"):
                    return

            # إنشاء خريطة الجلوس
            map_id = f"{classroom_name}_{exam_date}_{datetime.now().strftime('%H%M%S')}"
            seating_map = {
                'id': map_id,
                'classroom': classroom_name,
                'subject': subject_text,
                'exam_date': exam_date,
                'students': filtered_students[:classroom['capacity']],  # أخذ العدد المناسب فقط
                'created_at': datetime.now().isoformat()
            }

            self.data['seating_maps'][map_id] = seating_map
            refresh_maps_list()
            display_seating_arrangement(seating_map, classroom)
            messagebox.showinfo("نجح", f"تم إنشاء خريطة الجلوس بنجاح\nعدد الطلبة: {len(seating_map['students'])}")

        def delete_seating_map():
            selection = maps_tree.selection()
            if not selection:
                messagebox.showerror("خطأ", "يرجى اختيار خريطة جلوس للحذف")
                return

            if messagebox.askyesno("تأكيد", "هل تريد حذف خريطة الجلوس المحددة؟"):
                item = maps_tree.item(selection[0])
                map_id = item['values'][0]

                if map_id in self.data['seating_maps']:
                    del self.data['seating_maps'][map_id]
                    refresh_maps_list()
                    # مسح منطقة العرض
                    for widget in display_frame.winfo_children():
                        widget.destroy()
                    messagebox.showinfo("نجح", "تم حذف خريطة الجلوس بنجاح")

        def view_seating_map():
            selection = maps_tree.selection()
            if not selection:
                messagebox.showerror("خطأ", "يرجى اختيار خريطة جلوس للعرض")
                return

            item = maps_tree.item(selection[0])
            map_id = item['values'][0]

            if map_id in self.data['seating_maps']:
                seating_map = self.data['seating_maps'][map_id]
                classroom = next((c for c in self.data['classrooms'] if c['name'] == seating_map['classroom']), None)
                if classroom:
                    display_seating_arrangement(seating_map, classroom)

        # أزرار التحكم
        buttons_frame = tk.Frame(control_frame, bg='#ecf0f1')
        buttons_frame.pack(pady=10)

        tk.Button(buttons_frame, text="إنشاء خريطة جلوس", command=create_seating_map,
                  bg='#27ae60', fg='white', font=('Arial', 10, 'bold'), width=15).pack(side=tk.LEFT, padx=5)
        tk.Button(buttons_frame, text="عرض", command=view_seating_map,
                  bg='#3498db', fg='white', font=('Arial', 10, 'bold'), width=10).pack(side=tk.LEFT, padx=5)
        tk.Button(buttons_frame, text="حذف", command=delete_seating_map,
                  bg='#e74c3c', fg='white', font=('Arial', 10, 'bold'), width=10).pack(side=tk.LEFT, padx=5)

        # إطار رئيسي للمحتوى
        content_frame = tk.Frame(main_frame, bg='#ecf0f1')
        content_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        # الجانب الأيسر - قائمة خرائط الجلوس
        left_frame = tk.LabelFrame(content_frame, text="خرائط الجلوس المحفوظة",
                                   font=('Arial', 12, 'bold'), bg='#ecf0f1', fg='#34495e')
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))

        columns = ('id', 'classroom', 'subject', 'date', 'students_count')
        maps_tree = ttk.Treeview(left_frame, columns=columns, show='headings', height=20)

        maps_tree.heading('id', text='المعرف')
        maps_tree.heading('classroom', text='القاعة')
        maps_tree.heading('subject', text='المادة')
        maps_tree.heading('date', text='التاريخ')
        maps_tree.heading('students_count', text='عدد الطلبة')

        maps_tree.column('id', width=150)
        maps_tree.column('classroom', width=120)
        maps_tree.column('subject', width=150)
        maps_tree.column('date', width=100)
        maps_tree.column('students_count', width=80)

        maps_scrollbar = ttk.Scrollbar(left_frame, orient=tk.VERTICAL, command=maps_tree.yview)
        maps_tree.configure(yscrollcommand=maps_scrollbar.set)

        maps_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        maps_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # الجانب الأيمن - عرض ترتيب الجلوس
        right_frame = tk.LabelFrame(content_frame, text="ترتيب الجلوس",
                                    font=('Arial', 12, 'bold'), bg='#ecf0f1', fg='#34495e')
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))

        # إطار قابل للتمرير للعرض
        canvas = tk.Canvas(right_frame, bg='white')
        scrollbar_v = ttk.Scrollbar(right_frame, orient="vertical", command=canvas.yview)
        scrollbar_h = ttk.Scrollbar(right_frame, orient="horizontal", command=canvas.xview)
        display_frame = tk.Frame(canvas, bg='white')

        display_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=display_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar_v.set, xscrollcommand=scrollbar_h.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar_v.pack(side="right", fill="y")
        scrollbar_h.pack(side="bottom", fill="x")

        def display_seating_arrangement(seating_map, classroom):
            # مسح العرض الحالي
            for widget in display_frame.winfo_children():
                widget.destroy()

            # عنوان الخريطة
            info_label = tk.Label(display_frame,
                                  text=f"القاعة: {seating_map['classroom']} | المادة: {seating_map['subject']} | التاريخ: {seating_map['exam_date']}",
                                  font=('Arial', 12, 'bold'), bg='white', fg='#2c3e50')
            info_label.pack(pady=10)

            # إطار الكراسي
            seats_frame = tk.Frame(display_frame, bg='white')
            seats_frame.pack(padx=20, pady=20)

            rows = classroom['rows']
            cols = classroom['cols']
            students = seating_map['students'][:]

            # خلط الطلبة عشوائياً
            import random
            random.shuffle(students)

            student_index = 0

            for row in range(rows):
                for col in range(cols):
                    if student_index < len(students):
                        student = students[student_index]
                        seat_text = f"{student['name']}\n{student['id']}"
                        bg_color = '#3498db'
                        student_index += 1
                    else:
                        seat_text = "فارغ"
                        bg_color = '#bdc3c7'

                    seat_btn = tk.Button(seats_frame, text=seat_text,
                                         font=('Arial', 8, 'bold'),
                                         bg=bg_color, fg='white',
                                         width=12, height=3,
                                         relief='raised', bd=2)
                    seat_btn.grid(row=row, column=col, padx=2, pady=2)

            # تحديث منطقة التمرير
            display_frame.update_idletasks()
            canvas.configure(scrollregion=canvas.bbox("all"))

        def refresh_maps_list():
            maps_tree.delete(*maps_tree.get_children())
            for map_id, seating_map in self.data['seating_maps'].items():
                maps_tree.insert('', 'end', values=(
                    map_id,
                    seating_map['classroom'],
                    seating_map['subject'][:20] + '...' if len(seating_map['subject']) > 20 else seating_map['subject'],
                    seating_map['exam_date'],
                    len(seating_map['students'])
                ))

        refresh_maps_list()

    def save_data(self):
        try:
            with open('exam_seating_data.json', 'w', encoding='utf-8') as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
            messagebox.showinfo("نجح", "تم حفظ البيانات بنجاح")
        except Exception as e:
            messagebox.showerror("خطأ", f"فشل في حفظ البيانات: {str(e)}")

    def load_data(self):
        try:
            if os.path.exists('exam_seating_data.json'):
                with open('exam_seating_data.json', 'r', encoding='utf-8') as f:
                    self.data = json.load(f)
                print("تم تحميل البيانات بنجاح")
        except Exception as e:
            print(f"فشل في تحميل البيانات: {str(e)}")
            # إنشاء بيانات افتراضية
            self.create_sample_data()

    def create_sample_data(self):
        """إنشاء بيانات تجريبية للاختبار"""
        # إضافة أقسام تجريبية
        sample_departments = [
            {'name': 'علوم الحاسوب', 'created_at': datetime.now().isoformat()},
            {'name': 'الرياضيات', 'created_at': datetime.now().isoformat()},
            {'name': 'الفيزياء', 'created_at': datetime.now().isoformat()},
            {'name': 'الكيمياء', 'created_at': datetime.now().isoformat()}
        ]

        # إضافة قاعات تجريبية
        sample_classrooms = [
            {'name': 'قاعة A101', 'capacity': 30, 'rows': 6, 'cols': 5, 'created_at': datetime.now().isoformat()},
            {'name': 'قاعة B202', 'capacity': 40, 'rows': 8, 'cols': 5, 'created_at': datetime.now().isoformat()},
            {'name': 'قاعة C303', 'capacity': 50, 'rows': 10, 'cols': 5, 'created_at': datetime.now().isoformat()}
        ]

        # إضافة مواد تجريبية
        sample_subjects = [
            {'name': 'البرمجة المتقدمة', 'code': 'CS301', 'department': 'علوم الحاسوب',
             'created_at': datetime.now().isoformat()},
            {'name': 'قواعد البيانات', 'code': 'CS302', 'department': 'علوم الحاسوب',
             'created_at': datetime.now().isoformat()},
            {'name': 'التحليل الرياضي', 'code': 'MATH201', 'department': 'الرياضيات',
             'created_at': datetime.now().isoformat()},
            {'name': 'الفيزياء العامة', 'code': 'PHY101', 'department': 'الفيزياء',
             'created_at': datetime.now().isoformat()}
        ]

        self.data['departments'] = sample_departments
        self.data['classrooms'] = sample_classrooms
        self.data['subjects'] = sample_subjects


def main():
    root = tk.Tk()
    app = ExamSeatingSystem(root)

    # التأكد من حفظ البيانات عند إغلاق البرنامج
    def on_closing():
        if messagebox.askyesno("تأكيد الخروج", "هل تريد حفظ البيانات قبل الخروج؟"):
            app.save_data()
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()


if __name__ == "__main__":
    main()