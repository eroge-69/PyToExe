# استيراد المكتبات الضرورية
from tkinter import *
from tkinter import ttk, messagebox
import pymysql

#--------------الفئة الرئيسية للبرنامج لإدارة الطلاب---------------------
class Student:
    def __init__(self, root):
        self.root = root
        self.root.title('برنامج إدارة مدارس')
        self.root.configure(background="silver")
        self.root.resizable(False, False)

        # أبعاد النافذة المطلوبة
        window_width = 1350
        window_height = 690

        # الحصول على أبعاد الشاشة
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        # حساب إحداثيات المركز
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2

        # تعيين حجم وموقع النافذة
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")

        # متغيرات الحالة لحقول الإدخال
        self.id_var = StringVar()
        self.name_var = StringVar()
        self.phone_var = StringVar() # متغير الهاتف
        self.email_var = StringVar() # متغير الايميل
        self.moahl_var = StringVar() # مؤهل الطالب (يقابل certi في قاعدة البيانات)
        self.gender_var = StringVar()
        self.address_var = StringVar()
        self.dell_var = StringVar()  # لحقل الحذف (الرقم التسلسلي)
        self.se_var = StringVar()    # لمتغير البحث (غير مستخدم حالياً)

        # عنوان رئيسي
        title = Label(self.root, text='(نظام تسجيل الطلاب)', bg='#c1d4d4', font=('monospace', 14), fg='white')
        title.pack(fill=X)

        # لوحة أدوات الإدخال
        manage_frame = Frame(self.root, bg='white')
        manage_frame.place(x=1137, y=30, width=210, height=380)

        # حقول الإدخال مع التسميات
        Label(manage_frame, text='الرقم التسلسلى', bg='white').pack()
        id_entry = Entry(manage_frame, textvariable=self.id_var, bd=2, justify='center')
        id_entry.pack()

        Label(manage_frame, text='اسم الطالب', bg='white').pack()
        name_entry = Entry(manage_frame, textvariable=self.name_var, bd=2, justify='center')
        name_entry.pack()

        # **تصحيح ربط المتغيرات مع حقول الإدخال (تم تبديلها)**
        Label(manage_frame, text='هاتف الطالب', bg='white').pack()
        # هاتف الطالب يجب أن يربط بـ self.phone_var
        phone_entry = Entry(manage_frame, textvariable=self.phone_var, bd=2, justify='center')
        phone_entry.pack()

        Label(manage_frame, text='ايميل الطالب', bg='white').pack()
        # ايميل الطالب يجب أن يربط بـ self.email_var
        email_entry = Entry(manage_frame, textvariable=self.email_var, bd=2, justify='center')
        email_entry.pack()
        # -------------------------------------------------------------

        Label(manage_frame, text='مؤهل الطالب', bg='white').pack()
        moahl_entry = Entry(manage_frame, textvariable=self.moahl_var, bd=2, justify='center')
        moahl_entry.pack()

        # اختيار نوع الجنس
        Label(manage_frame, text='اختر جنس الطالب', bg='white').pack()
        comb0 = ttk.Combobox(manage_frame, textvariable=self.gender_var, values=('ذكر', 'انثى'), state='readonly')
        comb0.pack()

        # عنوان الطالب
        Label(manage_frame, text='عنوان الطالب', bg='white').pack()
        address_entry = Entry(manage_frame, textvariable=self.address_var, bd=2, justify='center')
        address_entry.pack()

        # حقل الحذف
        Label(manage_frame, text='حذف الطالب', bg='white').pack()
        delete_entry = Entry(manage_frame, textvariable=self.dell_var, bd=2, justify='center')
        delete_entry.pack()

        # لوحة الأزرار
        btn_frame = Frame(self.root, bg='white')
        btn_frame.place(x=1137, y=414, width=210, height=273)

        Label(btn_frame, text='لوحة التنفيذ', font=('Deco', 14), fg='black', bg='white').pack(fill=X)

        # أزرار العمليات
        Button(btn_frame, text='اضافة', fg='black', bg='#85929E', command=self.add_student).place(x=33, y=35, width=150, height=30)
        Button(btn_frame, text='افراغ', fg='black', bg='#85929E', command=self.clear_fields).place(x=33, y=70, width=150, height=30)
        Button(btn_frame, text='حذف', fg='black', bg='#85929E', command=self.delete_student).place(x=33, y=105, width=150, height=30)
        # **تغيير اسم الدالة المستدعاة لزر التعديل**
        Button(btn_frame, text='تعديل', fg='black', bg='#85929E', command=self.update_student_data).place(x=33, y=140, width=150, height=30)
        Button(btn_frame, text='من نحن', fg='black', bg='#85929E', command=self.about).place(x=33, y=175, width=150, height=30)
        Button(btn_frame, text='اغلاق البرنامج', fg='black', bg='#85929E', command=self.root.destroy).place(x=33, y=210, width=150, height=30)

        # لوحة البحث
        search_frame = Frame(self.root, bg='white')
        search_frame.place(x=1, y=30, width=1135, height=50)

        Label(search_frame, text='اختر طريقة البحث', bg='white').place(x=1035, y=15)

        self.search_method = ttk.Combobox(search_frame, values=('id', 'name', 'phone', 'email'), state='readonly')
        self.search_method.place(x=835, y=15)

        self.search_var = StringVar()
        search_entry = Entry(search_frame, textvariable=self.search_var, bd=2, justify='center')
        search_entry.place(x=380, y=15, width=300)

        Button(search_frame, text='بحث', fg='black', bg='#85929E', command=self.search_student).place(x=100, y=12, width=130, height=25)

        # لوحة عرض النتائج
        details_frame = Frame(self.root, bg='white')
        details_frame.place(x=1, y=82, width=1135, height=605)

        # إعداد السكولر للعرض الأفقي والعمودي
        scroll_x = Scrollbar(details_frame, orient=HORIZONTAL)
        scroll_y = Scrollbar(details_frame, orient=VERTICAL)

        # جدول عرض البيانات
        # تأكد من أن أسماء الأعمدة هنا تطابق تماماً أسماء الأعمدة في قاعدة البيانات (في استعلام SELECT)
        self.student_table = ttk.Treeview(details_frame, columns=('id','name','phone','email','certi','gender','address'),
                                          xscrollcommand=scroll_x.set, yscrollcommand=scroll_y.set)
        scroll_x.config(command=self.student_table.xview)
        scroll_y.config(command=self.student_table.yview)

        scroll_x.pack(side=BOTTOM, fill=X)
        scroll_y.pack(side=RIGHT, fill=Y)
        self.student_table.pack(fill=BOTH, expand=1)

        # إعداد رؤوس الأعمدة
        self.student_table['show'] = 'headings'
        self.student_table.heading('id', text='Id')
        self.student_table.heading('name', text='Name')
        self.student_table.heading('phone', text='Phone')
        self.student_table.heading('email', text='Email')
        self.student_table.heading('certi', text='Study') # 'certi' في DB يقابل 'Study' في الواجهة
        self.student_table.heading('gender', text='Type')
        self.student_table.heading('address', text='Address')

        # تعيين عرض الأعمدة
        self.student_table.column('id', width=100)
        self.student_table.column('name', width=150)
        self.student_table.column('phone', width=150)
        self.student_table.column('email', width=100)
        self.student_table.column('certi', width=100)
        self.student_table.column('gender', width=80)
        self.student_table.column('address', width=150)

        # ربط حدث الضغط على الجدول لاختيار سجل وتعبئة البيانات
        self.student_table.bind("<ButtonRelease-1>", self.update_student)

        # تحميل البيانات عند بدء البرنامج
        self.show_data()

    # الاتصال بقاعدة البيانات
    def connect_db(self):
        return pymysql.connect(host='localhost', user='root', password='', database='student')

    # عرض البيانات في الجدول
    def show_data(self):
        # حذف البيانات القديمة
        for row in self.student_table.get_children():
            self.student_table.delete(row)
        try:
            con = self.connect_db()
            cur = con.cursor()
            # **التعديل الهام هنا: تحديد ترتيب الأعمدة ليتوافق مع Treeview وقاعدة البيانات**
            cur.execute("SELECT id, name, phone, email, certi, gender, address FROM student")
            rows = cur.fetchall()
            for row in rows:
                self.student_table.insert('', END, values=row)
            con.close()
        except Exception as e:
            print("Error fetching data:", e)

    # اضافة سجل جديد
    def add_student(self):
        try:
            con = self.connect_db()
            cur = con.cursor()
            # **تأكد من ترتيب القيم هنا ليتوافق مع ترتيب الأعمدة في قاعدة البيانات**
            cur.execute(
                "INSERT INTO student (id, name, phone, email, certi, gender, address) VALUES (%s,%s,%s,%s,%s,%s,%s)",
                (
                    self.id_var.get(),
                    self.name_var.get(),
                    self.phone_var.get(),  # الهاتف
                    self.email_var.get(),  # الايميل
                    self.moahl_var.get(),  # المؤهل (يقابل certi)
                    self.gender_var.get(),
                    self.address_var.get()
                )
            )
            con.commit()
            con.close()
            self.show_data()
            self.clear_fields()
        except Exception as e:
            print("Error adding student:", e)
            messagebox.showerror("خطأ في الإضافة", f"حدث خطأ أثناء إضافة الطالب: {e}")

    # حذف سجل
    def delete_student(self):
        try:
            con = self.connect_db()
            cur = con.cursor()
            cur.execute("DELETE FROM student WHERE id=%s", (self.dell_var.get(),))
            con.commit()
            con.close()
            self.show_data()
            self.clear_fields()
        except Exception as e:
            print("Error deleting student:", e)
            messagebox.showerror("خطأ في الحذف", f"حدث خطأ أثناء حذف الطالب: {e}")

    # تحميل سجل عند اختيار صف من الجدول
    def update_student(self, ev):
        try:
            cursor_row = self.student_table.focus()
            contents = self.student_table.item(cursor_row)
            row = contents['values']
            if row:  # تحقق من وجود بيانات
                self.id_var.set(row[0])
                self.name_var.set(row[1])
                self.phone_var.set(row[2])  # القيمة الثالثة (Index 2) هي الهاتف
                self.email_var.set(row[3])  # القيمة الرابعة (Index 3) هي الإيميل
                self.moahl_var.set(row[4])  # القيمة الخامسة (Index 4) هي المؤهل (certi)
                self.gender_var.set(row[5])
                self.address_var.set(row[6])
        except Exception as e:
            print("Error loading student data:", e)
            messagebox.showerror("خطأ في التحميل", f"حدث خطأ أثناء تحميل بيانات الطالب: {e}")

    # **تغيير اسم الدالة من 'update' إلى 'update_student_data' لتجنب التعارض**
    def update_student_data(self):
        try:
            con = self.connect_db()
            cur = con.cursor()
            # **تأكد من ترتيب القيم هنا ليتوافق مع ترتيب الأعمدة في قاعدة البيانات**
            cur.execute(
                "UPDATE student SET name=%s, phone=%s, email=%s, certi=%s, gender=%s, address=%s WHERE id=%s",
                (
                    self.name_var.get(),
                    self.phone_var.get(),  # الهاتف
                    self.email_var.get(),  # الايميل
                    self.moahl_var.get(),  # المؤهل (يقابل certi)
                    self.gender_var.get(),
                    self.address_var.get(),
                    self.id_var.get()      # الـ ID هو الشرط الأخير للتحديث
                )
            )
            con.commit()
            con.close()
            self.show_data()
            self.clear_fields()
            messagebox.showinfo("تحديث", "تم تحديث بيانات الطالب بنجاح!")
        except Exception as e:
            print("Error updating student:", e)
            messagebox.showerror("خطأ في التحديث", f"حدث خطأ أثناء تحديث الطالب: {e}")

    # البحث عن سجل
    def search_student(self):
        method = self.search_method.get()
        value = self.search_var.get()
        if not method or not value:
            messagebox.showwarning("بحث", "الرجاء اختيار طريقة البحث وإدخال قيمة.")
            return

        query = f"SELECT id, name, phone, email, certi, gender, address FROM student WHERE {method} LIKE %s"
        try:
            con = self.connect_db()
            cur = con.cursor()
            cur.execute(query, ('%' + value + '%',))
            rows = cur.fetchall()
            self.student_table.delete(*self.student_table.get_children())
            if not rows:
                messagebox.showinfo("بحث", "لا توجد نتائج مطابقة.")
            for row in rows:
                self.student_table.insert('', END, values=row)
            con.close()
        except Exception as e:
            print("Error searching:", e)
            messagebox.showerror("خطأ في البحث", f"حدث خطأ أثناء البحث: {e}")

    # تفريغ الحقول
    def clear_fields(self):
        self.id_var.set('')
        self.name_var.set('')
        self.phone_var.set('')
        self.email_var.set('')
        self.moahl_var.set('')
        self.gender_var.set('')
        self.address_var.set('')
        self.dell_var.set('')
        self.search_var.set('') # تفريغ حقل البحث أيضاً
        # self.search_method.set('') # يمكن تفريغ اختيار طريقة البحث أيضاً إذا أردت

    # معلومات عن البرنامج
    def about(self):
        messagebox.showinfo("من نحن", "Developer by ZAKARIA AZIZ' 'Whatsapp +201285835712.")
    
# بدء البرنامج
if __name__ == "__main__":
    root = Tk()
    app = Student(root)
    root.mainloop()