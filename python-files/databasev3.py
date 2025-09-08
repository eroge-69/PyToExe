import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import datetime
import os

APP_TITLE = "مدير المستخدمين"
DB_FILENAME = 'users.db'
WINDOW_SIZE = "1024x640"
MASTER_PASSWORD = "1234"  # يمكنك تغييره

def initialize_database():
    conn = sqlite3.connect(DB_FILENAME)
    c = conn.cursor()
    c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
    table_exists = c.fetchone()
    if not table_exists:
        c.execute('''CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            phone TEXT,
            parent_phone TEXT,
            address TEXT,
            dob TEXT)''')
    else:
        existing_columns = [col[1] for col in c.execute('PRAGMA table_info(users)').fetchall()]
        needed_columns = ['username','phone','parent_phone','address','dob']
        for col in needed_columns:
            if col not in existing_columns:
                c.execute(f'ALTER TABLE users ADD COLUMN {col} TEXT')
    conn.commit()
    conn.close()

class Database:
    def __init__(self, filename=DB_FILENAME):
        self.conn = sqlite3.connect(filename)

    def add_user(self, username, phone, parent_phone, address, dob):
        c = self.conn.cursor()
        c.execute('INSERT INTO users (username, phone, parent_phone, address, dob) VALUES (?, ?, ?, ?, ?)',
                  (username, phone, parent_phone, address, dob))
        self.conn.commit()

    def update_user(self, user_id, username, phone, parent_phone, address, dob):
        c = self.conn.cursor()
        c.execute('UPDATE users SET username=?, phone=?, parent_phone=?, address=?, dob=? WHERE id=?',
                  (username, phone, parent_phone, address, dob, user_id))
        self.conn.commit()

    def delete_user(self, user_id):
        c = self.conn.cursor()
        c.execute('DELETE FROM users WHERE id=?', (user_id,))
        self.conn.commit()

    def get_all(self):
        c = self.conn.cursor()
        c.execute('SELECT id, username, phone, parent_phone, address, dob FROM users ORDER BY id DESC')
        return c.fetchall()

    def search(self, term):
        c = self.conn.cursor()
        pattern = f"%{term}%"
        c.execute('''SELECT id, username, phone, parent_phone, address, dob FROM users
                     WHERE username LIKE ? OR phone LIKE ? OR parent_phone LIKE ? OR address LIKE ?
                     ORDER BY id DESC''', (pattern, pattern, pattern, pattern))
        return c.fetchall()

class PasswordDialog:
    def __init__(self):
        self.top = tk.Tk()
        self.top.title("أدخل كلمة المرور")
        self.top.geometry("300x150")
        self.top.configure(bg="#263238")
        tk.Label(self.top, text="أدخل كلمة المرور لفتح التطبيق", bg="#263238", fg="white").pack(pady=10)
        self.entry = tk.Entry(self.top, show="*", width=20)
        self.entry.pack(pady=5)
        tk.Button(self.top, text="تأكيد", bg="#06b6a4", fg="white", command=self.check_password).pack(pady=5)
        self.valid = False
        self.entry.focus_set()
        self.top.mainloop()

    def check_password(self):
        if self.entry.get() == MASTER_PASSWORD:
            self.valid = True
            self.top.destroy()
        else:
            messagebox.showerror("خطأ", "كلمة المرور غير صحيحة")

class UserManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title(APP_TITLE)
        self.root.geometry(WINDOW_SIZE)
        self.db = Database()
        self.selected_user_id = None

        self.bg = '#1f2a2e'
        self.frame_bg = '#263238'
        self.input_bg = '#2b3134'
        self.text_fg = '#d0d7d9'
        self.accent = '#06b6a4'
        self.danger = '#ef5350'

        self.root.configure(bg=self.bg)
        self._build_ui()
        self._populate_tree()

    def _build_ui(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Treeview", background=self.input_bg, foreground=self.text_fg, fieldbackground=self.input_bg, rowheight=25)
        style.map("Treeview", background=[('selected', self.accent)])

        left = tk.Frame(self.root, bg=self.frame_bg, bd=2, relief='groove', padx=12, pady=12)
        left.pack(side='left', padx=12, pady=12, fill='y')

        tk.Label(left, text='بيانات المستخدم', bg=self.frame_bg, fg=self.text_fg, font=('Arial', 14, 'bold')).pack(anchor='e')
        form = tk.Frame(left, bg=self.frame_bg)
        form.pack(pady=6)

        self.entries = {}
        self.entries['اسم المستخدم'] = self._create_input(form, 'اسم المستخدم:')
        self.entries['رقم الهاتف'] = self._create_input(form, 'رقم الهاتف:')
        self.entries['رقم الاب او الام'] = self._create_input(form, 'رقم الاب او الام:')
        self.entries['عنوان المنزل'] = self._create_input(form, 'عنوان المنزل:')

        row = tk.Frame(form, bg=self.frame_bg)
        row.pack(fill='x', pady=4)
        tk.Label(row, text='تاريخ الميلاد:', width=18, anchor='e', bg=self.frame_bg, fg=self.text_fg).pack(side='right')
        self.entries['تاريخ الميلاد (YYYY-MM-DD)'] = tk.Entry(row, bg=self.input_bg, fg=self.text_fg, insertbackground=self.text_fg)
        self.entries['تاريخ الميلاد (YYYY-MM-DD)'].pack(side='right', padx=6, fill='x', expand=True)
        tk.Button(row, text='📅 اليوم', bg=self.accent, fg='white', command=self._fill_today_date).pack(side='right', padx=4)

        btn_frame = tk.Frame(left, bg=self.frame_bg)
        btn_frame.pack(pady=8)
        tk.Button(btn_frame, text='تسجيل جديد', bg=self.accent, fg='white', width=12, command=self.on_new).grid(row=0, column=0, padx=6, pady=6)
        tk.Button(btn_frame, text='مسح الحقول', bg=self.accent, fg='white', width=12, command=self.clear_fields).grid(row=0, column=1, padx=6, pady=6)

        search_frame = tk.Frame(left, bg=self.frame_bg, pady=10)
        search_frame.pack(fill='x')
        self.search_var = tk.StringVar()
        tk.Entry(search_frame, textvariable=self.search_var, bg=self.input_bg, fg=self.text_fg, width=24).pack(side='right', padx=6, fill='x', expand=True)
        tk.Button(search_frame, text='بحث', bg=self.accent, fg='white', command=self.on_search).pack(side='right', padx=6)
        tk.Button(search_frame, text='مسح', bg=self.accent, fg='white', command=self.on_clear_search).pack(side='right', padx=6)

        tk.Button(self.root, text='خروج', bg=self.danger, fg='white', command=self.root.quit).pack(side='bottom', pady=8)

        right = tk.Frame(self.root, bg=self.frame_bg, bd=2, relief='groove', padx=12, pady=12)
        right.pack(side='left', padx=12, pady=12, fill='both', expand=True)
        tk.Label(right, text='قاعدة البيانات', bg=self.frame_bg, fg=self.text_fg, font=('Arial', 14, 'bold')).pack(anchor='w')

        cols = ('id', 'username', 'phone', 'parent_phone', 'address', 'dob')
        self.tree = ttk.Treeview(right, columns=cols, show='headings', height=15)
        headings = ['ID', 'الاسم', 'الهاتف', 'رقم الاب/الام', 'عنوان المنزل', 'تاريخ الميلاد']
        for c, h in zip(cols, headings):
            self.tree.heading(c, text=h)
            self.tree.column(c, anchor='center', width=150)
        self.tree.pack(fill='both', expand=True, pady=6)
        self.tree.bind('<<TreeviewSelect>>', self.on_tree_select)

        action_frame = tk.Frame(right, bg=self.frame_bg)
        action_frame.pack(pady=6)
        tk.Button(action_frame, text='حفظ البيانات', bg=self.accent, fg='white', width=12, command=self.on_save).grid(row=0, column=0, padx=6)
        tk.Button(action_frame, text='حذف', bg=self.accent, fg='white', width=10, command=self.on_delete).grid(row=0, column=1, padx=6)
        tk.Button(action_frame, text='تعديل', bg=self.accent, fg='white', width=10, command=self.on_edit).grid(row=0, column=2, padx=6)

    def _create_input(self, parent, label_text):
        row = tk.Frame(parent, bg=self.frame_bg)
        row.pack(fill='x', pady=4)
        tk.Label(row, text=label_text, width=18, anchor='e', bg=self.frame_bg, fg=self.text_fg).pack(side='right')
        ent = tk.Entry(row, bg=self.input_bg, fg=self.text_fg, insertbackground=self.text_fg)
        ent.pack(side='right', padx=6, fill='x', expand=True)
        return ent

    def _fill_today_date(self):
        today = datetime.date.today().strftime("%Y-%m-%d")
        self.entries['تاريخ الميلاد (YYYY-MM-DD)'].delete(0, tk.END)
        self.entries['تاريخ الميلاد (YYYY-MM-DD)'].insert(0, today)

    def clear_fields(self):
        for ent in self.entries.values():
            ent.delete(0, tk.END)
        self.selected_user_id = None

    def on_new(self):
        self.clear_fields()
        messagebox.showinfo('جاهز', 'الآن يمكنك إدخال بيانات مستخدم جديد ثم اضغط "حفظ البيانات"')

    def on_save(self):
        username = self.entries['اسم المستخدم'].get().strip()
        phone = self.entries['رقم الهاتف'].get().strip()
        parent_phone = self.entries['رقم الاب او الام'].get().strip()
        address = self.entries['عنوان المنزل'].get().strip()
        dob = self.entries['تاريخ الميلاد (YYYY-MM-DD)'].get().strip()

        if not username or not phone:
            messagebox.showwarning('مطلوب', 'الرجاء ملء الاسم ورقم الهاتف على الأقل')
            return

        if self.selected_user_id:
            self.db.update_user(self.selected_user_id, username, phone, parent_phone, address, dob)
            messagebox.showinfo('تم', 'تم تحديث بيانات المستخدم')
        else:
            self.db.add_user(username, phone, parent_phone, address, dob)
            messagebox.showinfo('تم', 'تم حفظ بيانات المستخدم')
        self._populate_tree()
        self.clear_fields()

    def on_delete(self):
        if not self.selected_user_id:
            messagebox.showwarning('مطلوب', 'اختر سجلاً للحذف')
            return
        if messagebox.askyesno('تأكيد', 'هل أنت متأكد أنك تريد حذف هذا السجل؟'):
            self.db.delete_user(self.selected_user_id)
            self._populate_tree()
            self.clear_fields()

    def on_edit(self):
        if not self.selected_user_id:
            messagebox.showwarning('مطلوب', 'اختر سجلاً للتعديل')
            return
        messagebox.showinfo('تعليمات', 'عدّل الحقول على اليسار ثم اضغط "حفظ البيانات"')

    def on_search(self):
        term = self.search_var.get().strip()
        if not term:
            messagebox.showinfo('بحث فارغ', 'ادخل نص للبحث')
            return
        self._populate_tree(self.db.search(term))

    def on_clear_search(self):
        self.search_var.set('')
        self._populate_tree()

    def _populate_tree(self, rows=None):
        for r in self.tree.get_children():
            self.tree.delete(r)
        if rows is None:
            rows = self.db.get_all()
        for row in rows:
            self.tree.insert('', tk.END, values=row)

    def on_tree_select(self, event):
        sel = self.tree.selection()
        if not sel:
            return
        vals = self.tree.item(sel[0], 'values')
        self.selected_user_id = int(vals[0])
        self.entries['اسم المستخدم'].delete(0, tk.END); self.entries['اسم المستخدم'].insert(0, vals[1])
        self.entries['رقم الهاتف'].delete(0, tk.END); self.entries['رقم الهاتف'].insert(0, vals[2])
        self.entries['رقم الاب او الام'].delete(0, tk.END); self.entries['رقم الاب او الام'].insert(0, vals[3])
        self.entries['عنوان المنزل'].delete(0, tk.END); self.entries['عنوان المنزل'].insert(0, vals[4])
        self.entries['تاريخ الميلاد (YYYY-MM-DD)'].delete(0, tk.END)
        self.entries['تاريخ الميلاد (YYYY-MM-DD)'].insert(0, vals[5])

def run():
    initialize_database()
    pd = PasswordDialog()
    if not pd.valid:
        return
    root = tk.Tk()
    app = UserManagerApp(root)
    root.mainloop()

if __name__ == "__main__":
    run()
