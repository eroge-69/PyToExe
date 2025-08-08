import sqlite3
import os
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
from datetime import date

DB_PATH = os.path.join(os.path.dirname(__file__), 'school_app.db')

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    # Students
    cur.execute('''CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        roll_no TEXT,
        name TEXT NOT NULL,
        class TEXT,
        section TEXT,
        dob TEXT,
        parent_name TEXT,
        parent_phone TEXT,
        address TEXT
    )''')
    # Staff
    cur.execute('''CREATE TABLE IF NOT EXISTS staff (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        emp_id TEXT UNIQUE,
        name TEXT NOT NULL,
        role TEXT,
        phone TEXT,
        email TEXT,
        join_date TEXT,
        qualifications TEXT
    )''')
    # Attendance (students)
    cur.execute('''CREATE TABLE IF NOT EXISTS attendance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER,
        date TEXT,
        status TEXT,
        remarks TEXT
    )''')
    # Staff attendance
    cur.execute('''CREATE TABLE IF NOT EXISTS staff_attendance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        staff_id INTEGER,
        date TEXT,
        status TEXT,
        remarks TEXT
    )''')
    # Fees
    cur.execute('''CREATE TABLE IF NOT EXISTS fees (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER,
        head TEXT,
        amount REAL,
        due_date TEXT,
        status TEXT
    )''')
    # Payments
    cur.execute('''CREATE TABLE IF NOT EXISTS payments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER,
        amount REAL,
        date TEXT,
        mode TEXT,
        receipt_no TEXT
    )''')
    # Subjects & exams & marks
    cur.execute('''CREATE TABLE IF NOT EXISTS subjects (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT
    )''')
    cur.execute('''CREATE TABLE IF NOT EXISTS exams (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        term TEXT,
        date TEXT
    )''')
    cur.execute('''CREATE TABLE IF NOT EXISTS marks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER,
        exam_id INTEGER,
        subject_id INTEGER,
        marks REAL
    )''')
    conn.commit()
    conn.close()

class SchoolApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('School Management (Offline)')
        self.geometry('1000x650')
        self.resizable(True, True)
        self.conn = sqlite3.connect(DB_PATH)
        self.create_ui()

    def create_ui(self):
        nb = ttk.Notebook(self)
        nb.pack(fill='both', expand=True)
        self.students_frame = StudentsFrame(nb, self.conn)
        self.staff_frame = StaffFrame(nb, self.conn)
        self.attendance_frame = AttendanceFrame(nb, self.conn)
        self.fees_frame = FeesFrame(nb, self.conn)
        self.results_frame = ResultsFrame(nb, self.conn)

        nb.add(self.students_frame, text='Students')
        nb.add(self.staff_frame, text='Staff')
        nb.add(self.attendance_frame, text='Attendance')
        nb.add(self.fees_frame, text='Fees')
        nb.add(self.results_frame, text='Results')

    def on_closing(self):
        self.conn.close()
        self.destroy()

# --- Students Frame ---
class StudentsFrame(ttk.Frame):
    def __init__(self, parent, conn):
        super().__init__(parent)
        self.conn = conn
        self.setup_ui()
        self.load_students()

    def setup_ui(self):
        top = ttk.Frame(self)
        top.pack(fill='x', padx=8, pady=8)
        ttk.Button(top, text='Add Student', command=self.add_student).pack(side='left')
        ttk.Button(top, text='Import CSV', command=self.import_csv).pack(side='left', padx=6)
        ttk.Button(top, text='Export CSV', command=self.export_csv).pack(side='left')
        self.search_var = tk.StringVar()
        tk.Entry(top, textvariable=self.search_var).pack(side='right')
        ttk.Label(top, text='Search:').pack(side='right')

        # Tree
        cols = ('id','roll_no','name','class','section','parent_name','parent_phone')
        self.tree = ttk.Treeview(self, columns=cols, show='headings')
        for c in cols:
            self.tree.heading(c, text=c.title())
            self.tree.column(c, width=120)
        self.tree.pack(fill='both', expand=True, padx=8, pady=8)
        self.tree.bind('<Double-1>', self.on_edit)

        bottom = ttk.Frame(self)
        bottom.pack(fill='x', padx=8, pady=8)
        ttk.Button(bottom, text='Delete Selected', command=self.delete_selected).pack(side='left')

    def run_query(self, sql, params=()):
        cur = self.conn.cursor()
        cur.execute(sql, params)
        return cur

    def load_students(self):
        q = "SELECT id, roll_no, name, class, section, parent_name, parent_phone FROM students ORDER BY name"
        cur = self.run_query(q)
        rows = cur.fetchall()
        for i in self.tree.get_children():
            self.tree.delete(i)
        for r in rows:
            self.tree.insert('', 'end', values=r)

    def add_student(self):
        dlg = StudentDialog(self, title='Add Student')
        self.wait_window(dlg)
        if dlg.result:
            data = dlg.result
            self.run_query('INSERT INTO students (roll_no,name,class,section,dob,parent_name,parent_phone,address) VALUES (?,?,?,?,?,?,?,?)', data)
            self.conn.commit()
            self.load_students()

    def on_edit(self, event):
        item = self.tree.selection()[0]
        vals = self.tree.item(item,'values')
        sid = vals[0]
        cur = self.run_query('SELECT roll_no,name,class,section,dob,parent_name,parent_phone,address FROM students WHERE id=?',(sid,))
        r = cur.fetchone()
        dlg = StudentDialog(self, title='Edit Student', initial=r)
        self.wait_window(dlg)
        if dlg.result:
            data = dlg.result
            self.run_query('UPDATE students SET roll_no=?,name=?,class=?,section=?,dob=?,parent_name=?,parent_phone=?,address=? WHERE id=?', data+(sid,))
            self.conn.commit()
            self.load_students()

    def delete_selected(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo('Info','Select a student first')
            return
        if messagebox.askyesno('Confirm','Delete selected student(s)?'):
            for item in sel:
                sid = self.tree.item(item,'values')[0]
                self.run_query('DELETE FROM students WHERE id=?',(sid,))
            self.conn.commit()
            self.load_students()

    def import_csv(self):
        path = filedialog.askopenfilename(filetypes=[('CSV files','*.csv')])
        if not path:
            return
        import csv
        with open(path, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                self.run_query('INSERT INTO students (roll_no,name,class,section,dob,parent_name,parent_phone,address) VALUES (?,?,?,?,?,?,?,?)',(
                    row.get('rollNo') or row.get('roll_no'),
                    row.get('name'),
                    row.get('class'),
                    row.get('section'),
                    row.get('dob'),
                    row.get('parentName') or row.get('parent_name'),
                    row.get('parentPhone') or row.get('parent_phone'),
                    row.get('address')
                ))
        self.conn.commit()
        self.load_students()
        messagebox.showinfo('Import','Imported students from CSV')

    def export_csv(self):
        path = filedialog.asksaveasfilename(defaultextension='.csv', filetypes=[('CSV files','*.csv')])
        if not path:
            return
        import csv
        cur = self.run_query("SELECT roll_no,name,class,section,dob,parent_name,parent_phone,address FROM students")
        rows = cur.fetchall()
        with open(path,'w',newline='',encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['roll_no','name','class','section','dob','parent_name','parent_phone','address'])
            for r in rows:
                writer.writerow(r)
        messagebox.showinfo('Export','Students exported to CSV')

class StudentDialog(tk.Toplevel):
    def __init__(self, parent, title='Student', initial=None):
        super().__init__(parent)
        self.title(title)
        self.result = None
        self.build(initial)

    def build(self, initial):
        fields = ['Roll No','Name','Class','Section','DOB (YYYY-MM-DD)','Parent Name','Parent Phone','Address']
        self.vars = []
        for i,f in enumerate(fields):
            ttk.Label(self, text=f).grid(row=i, column=0, sticky='w', padx=6, pady=4)
            v = tk.StringVar(value=(initial[i] if initial else ''))
            ttk.Entry(self, textvariable=v, width=40).grid(row=i, column=1, padx=6, pady=4)
            self.vars.append(v)
        btn = ttk.Button(self, text='Save', command=self.on_save)
        btn.grid(row=len(fields), column=0, columnspan=2, pady=10)

    def on_save(self):
        vals = tuple(v.get().strip() for v in self.vars)
        if not vals[1]:
            messagebox.showerror('Error','Name is required')
            return
        self.result = vals
        self.destroy()

# --- Staff Frame ---
class StaffFrame(ttk.Frame):
    def __init__(self, parent, conn):
        super().__init__(parent)
        self.conn = conn
        self.setup_ui()
        self.load_staff()

    def setup_ui(self):
        top = ttk.Frame(self)
        top.pack(fill='x', padx=8, pady=8)
        ttk.Button(top, text='Add Staff', command=self.add_staff).pack(side='left')
        ttk.Button(top, text='Import CSV', command=self.import_csv).pack(side='left', padx=6)
        ttk.Button(top, text='Export CSV', command=self.export_csv).pack(side='left')
        self.tree = ttk.Treeview(self, columns=('id','emp_id','name','role','phone'), show='headings')
        for c in ('id','emp_id','name','role','phone'):
            self.tree.heading(c, text=c.title())
            self.tree.column(c, width=140)
        self.tree.pack(fill='both', expand=True, padx=8, pady=8)
        self.tree.bind('<Double-1>', self.on_edit)
        bottom = ttk.Frame(self)
        bottom.pack(fill='x', padx=8, pady=8)
        ttk.Button(bottom, text='Delete Selected', command=self.delete_selected).pack(side='left')

    def run_query(self, sql, params=()):
        cur = self.conn.cursor()
        cur.execute(sql, params)
        return cur

    def load_staff(self):
        cur = self.run_query("SELECT id,emp_id,name,role,phone FROM staff ORDER BY name")
        rows = cur.fetchall()
        for i in self.tree.get_children():
            self.tree.delete(i)
        for r in rows:
            self.tree.insert('', 'end', values=r)

    def add_staff(self):
        dlg = StaffDialog(self, title='Add Staff')
        self.wait_window(dlg)
        if dlg.result:
            self.run_query('INSERT INTO staff (emp_id,name,role,phone,email,join_date,qualifications) VALUES (?,?,?,?,?,?,?)', dlg.result)
            self.conn.commit()
            self.load_staff()

    def on_edit(self, event):
        item = self.tree.selection()[0]
        sid = self.tree.item(item,'values')[0]
        cur = self.run_query('SELECT emp_id,name,role,phone,email,join_date,qualifications FROM staff WHERE id=?',(sid,))
        r = cur.fetchone()
        dlg = StaffDialog(self, title='Edit Staff', initial=r)
        self.wait_window(dlg)
        if dlg.result:
            self.run_query('UPDATE staff SET emp_id=?,name=?,role=?,phone=?,email=?,join_date=?,qualifications=? WHERE id=?', dlg.result+(sid,))
            self.conn.commit()
            self.load_staff()

    def delete_selected(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo('Info','Select a staff first')
            return
        if messagebox.askyesno('Confirm','Delete selected staff?'):
            for item in sel:
                sid = self.tree.item(item,'values')[0]
                self.run_query('DELETE FROM staff WHERE id=?',(sid,))
            self.conn.commit()
            self.load_staff()

    def import_csv(self):
        path = filedialog.askopenfilename(filetypes=[('CSV files','*.csv')])
        if not path: return
        import csv
        with open(path, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                self.run_query('INSERT INTO staff (emp_id,name,role,phone,email,join_date,qualifications) VALUES (?,?,?,?,?,?,?)',(
                    row.get('empId') or row.get('emp_id'),
                    row.get('name'),
                    row.get('role'),
                    row.get('phone'),
                    row.get('email'),
                    row.get('joinDate') or row.get('join_date'),
                    row.get('qualifications')
                ))
        self.conn.commit()
        self.load_staff()
        messagebox.showinfo('Import','Imported staff from CSV')

    def export_csv(self):
        path = filedialog.asksaveasfilename(defaultextension='.csv', filetypes=[('CSV files','*.csv')])
        if not path: return
        import csv
        cur = self.run_query("SELECT emp_id,name,role,phone,email,join_date,qualifications FROM staff")
        rows = cur.fetchall()
        with open(path,'w',newline='',encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['emp_id','name','role','phone','email','join_date','qualifications'])
            for r in rows:
                writer.writerow(r)
        messagebox.showinfo('Export','Staff exported to CSV')

class StaffDialog(tk.Toplevel):
    def __init__(self, parent, title='Staff', initial=None):
        super().__init__(parent)
        self.title(title)
        self.result = None
        self.build(initial)

    def build(self, initial):
        fields = ['Emp ID','Name','Role','Phone','Email','Join Date (YYYY-MM-DD)','Qualifications']
        self.vars = []
        for i,f in enumerate(fields):
            ttk.Label(self, text=f).grid(row=i, column=0, sticky='w', padx=6, pady=4)
            v = tk.StringVar(value=(initial[i] if initial else ''))
            ttk.Entry(self, textvariable=v, width=40).grid(row=i, column=1, padx=6, pady=4)
            self.vars.append(v)
        ttk.Button(self, text='Save', command=self.on_save).grid(row=len(fields), column=0, columnspan=2, pady=10)

    def on_save(self):
        vals = tuple(v.get().strip() for v in self.vars)
        if not vals[1]:
            messagebox.showerror('Error','Name is required')
            return
        self.result = vals
        self.destroy()

# --- Attendance Frame ---
class AttendanceFrame(ttk.Frame):
    def __init__(self, parent, conn):
        super().__init__(parent)
        self.conn = conn
        self.setup_ui()

    def setup_ui(self):
        top = ttk.Frame(self)
        top.pack(fill='x', padx=8, pady=8)
        ttk.Label(top, text='Date:').pack(side='left')
        self.date_var = tk.StringVar(value=date.today().isoformat())
        ttk.Entry(top, textvariable=self.date_var, width=12).pack(side='left')
        ttk.Button(top, text='Load Students', command=self.load_students).pack(side='left', padx=6)
        ttk.Button(top, text='Load Staff', command=self.load_staff).pack(side='left', padx=6)
        self.table = ttk.Treeview(self, columns=('id','name','status'), show='headings')
        for c in ('id','name','status'):
            self.table.heading(c, text=c.title())
            self.table.column(c, width=200)
        self.table.pack(fill='both', expand=True, padx=8, pady=8)
        bottom = ttk.Frame(self)
        bottom.pack(fill='x', padx=8, pady=8)
        ttk.Button(bottom, text='Mark Present', command=lambda: self.mark('Present')).pack(side='left')
        ttk.Button(bottom, text='Mark Absent', command=lambda: self.mark('Absent')).pack(side='left')
        ttk.Button(bottom, text='Mark Leave', command=lambda: self.mark('Leave')).pack(side='left')

    def run_query(self, sql, params=()):
        cur = self.conn.cursor()
        cur.execute(sql, params)
        return cur

    def load_students(self):
        cur = self.run_query('SELECT id,name FROM students ORDER BY name')
        rows = cur.fetchall()
        for i in self.table.get_children(): self.table.delete(i)
        for r in rows:
            self.table.insert('', 'end', values=(r[0], r[1], ''))
        self.context = 'student'

    def load_staff(self):
        cur = self.run_query('SELECT id,name FROM staff ORDER BY name')
        rows = cur.fetchall()
        for i in self.table.get_children(): self.table.delete(i)
        for r in rows:
            self.table.insert('', 'end', values=(r[0], r[1], ''))
        self.context = 'staff'

    def mark(self, status):
        sel = self.table.selection()
        if not sel:
            messagebox.showinfo('Info','Select row(s) to mark')
            return
        for item in sel:
            row = self.table.item(item,'values')
            id_ = row[0]
            d = self.date_var.get()
            if self.context == 'student':
                self.run_query('INSERT INTO attendance (student_id,date,status) VALUES (?,?,?)',(id_,d,status))
            else:
                self.run_query('INSERT INTO staff_attendance (staff_id,date,status) VALUES (?,?,?)',(id_,d,status))
        self.conn.commit()
        messagebox.showinfo('Saved','Attendance saved')

# --- Fees Frame ---
class FeesFrame(ttk.Frame):
    def __init__(self, parent, conn):
        super().__init__(parent)
        self.conn = conn
        self.setup_ui()

    def setup_ui(self):
        top = ttk.Frame(self)
        top.pack(fill='x', padx=8, pady=8)
        ttk.Label(top, text='Student ID:').pack(side='left')
        self.sid_var = tk.StringVar()
        ttk.Entry(top, textvariable=self.sid_var, width=8).pack(side='left')
        ttk.Button(top, text='Load Fees', command=self.load_fees).pack(side='left', padx=6)
        ttk.Button(top, text='Add Fee', command=self.add_fee).pack(side='left')
        ttk.Button(top, text='Record Payment', command=self.record_payment).pack(side='left', padx=6)

        self.tree = ttk.Treeview(self, columns=('id','head','amount','due_date','status'), show='headings')
        for c in ('id','head','amount','due_date','status'): 
            self.tree.heading(c, text=c.title()); self.tree.column(c, width=140)
        self.tree.pack(fill='both', expand=True, padx=8, pady=8)

    def run_query(self, sql, params=()):
        cur = self.conn.cursor()
        cur.execute(sql, params)
        return cur

    def load_fees(self):
        sid = self.sid_var.get().strip()
        if not sid:
            messagebox.showinfo('Info','Enter student ID')
            return
        cur = self.run_query('SELECT id,head,amount,due_date,status FROM fees WHERE student_id=?',(sid,))
        rows = cur.fetchall()
        for i in self.tree.get_children(): self.tree.delete(i)
        for r in rows: self.tree.insert('', 'end', values=r)

    def add_fee(self):
        sid = self.sid_var.get().strip()
        if not sid:
            messagebox.showinfo('Info','Enter student ID')
            return
        head = simpledialog.askstring('Fee Head','Enter fee head (e.g., Tuition)')
        amt = simpledialog.askfloat('Amount','Enter amount')
        due = simpledialog.askstring('Due Date','YYYY-MM-DD')
        if head and amt is not None:
            self.run_query('INSERT INTO fees (student_id,head,amount,due_date,status) VALUES (?,?,?,?,?)',(sid,head,amt,due,'Due'))
            self.conn.commit()
            self.load_fees()

    def record_payment(self):
        sid = self.sid_var.get().strip()
        if not sid:
            messagebox.showinfo('Info','Enter student ID')
            return
        amt = simpledialog.askfloat('Amount','Enter payment amount')
        if amt is None: return
        self.run_query('INSERT INTO payments (student_id,amount,date,mode,receipt_no) VALUES (?,?,?,?,?)',(sid,amt,date.today().isoformat(),'Cash',''))
        self.conn.commit()
        messagebox.showinfo('Saved','Payment recorded')

# --- Results Frame ---
class ResultsFrame(ttk.Frame):
    def __init__(self, parent, conn):
        super().__init__(parent)
        self.conn = conn
        self.setup_ui()
        self.load_students()

    def setup_ui(self):
        top = ttk.Frame(self)
        top.pack(fill='x', padx=8, pady=8)
        ttk.Button(top, text='Add Subject', command=self.add_subject).pack(side='left')
        ttk.Button(top, text='Add Exam', command=self.add_exam).pack(side='left', padx=6)
        ttk.Button(top, text='Enter Mark', command=self.enter_mark).pack(side='left')
        ttk.Button(top, text='Generate Report (txt)', command=self.generate_report).pack(side='left', padx=6)

        mid = ttk.Frame(self)
        mid.pack(fill='x', padx=8, pady=8)
        ttk.Label(mid, text='Student ID:').pack(side='left')
        self.sid_var = tk.StringVar()
        ttk.Entry(mid, textvariable=self.sid_var, width=8).pack(side='left')
        ttk.Button(mid, text='Load Marks', command=self.load_marks).pack(side='left', padx=6)

        self.tree = ttk.Treeview(self, columns=('subject','marks'), show='headings')
        self.tree.heading('subject', text='Subject'); self.tree.heading('marks', text='Marks')
        self.tree.pack(fill='both', expand=True, padx=8, pady=8)

    def run_query(self, sql, params=()):
        cur = self.conn.cursor()
        cur.execute(sql, params)
        return cur

    def add_subject(self):
        name = simpledialog.askstring('Subject','Subject name')
        if not name: return
        self.run_query('INSERT INTO subjects (name) VALUES (?)',(name,))
        self.conn.commit()
        messagebox.showinfo('Saved','Subject added')

    def add_exam(self):
        name = simpledialog.askstring('Exam','Exam name')
        term = simpledialog.askstring('Term','Term name')
        d = simpledialog.askstring('Date','YYYY-MM-DD')
        if not name: return
        self.run_query('INSERT INTO exams (name,term,date) VALUES (?,?,?)',(name,term,d))
        self.conn.commit()
        messagebox.showinfo('Saved','Exam added')

    def enter_mark(self):
        sid = self.sid_var.get().strip()
        if not sid:
            messagebox.showinfo('Info','Enter student ID')
            return
        # choose exam and subject
        cur = self.run_query('SELECT id,name FROM exams')
        exams = cur.fetchall()
        if not exams:
            messagebox.showinfo('Info','Add an exam first')
            return
        exam = simpledialog.askinteger('Exam ID','Enter exam id from list:\n' + '\n'.join(f'{e[0]}: {e[1]}' for e in exams))
        cur = self.run_query('SELECT id,name FROM subjects')
        subs = cur.fetchall()
        if not subs:
            messagebox.showinfo('Info','Add a subject first')
            return
        sub = simpledialog.askinteger('Subject ID','Enter subject id from list:\n' + '\n'.join(f'{s[0]}: {s[1]}' for s in subs))
        marks = simpledialog.askfloat('Marks','Enter marks obtained')
        if exam and sub is not None and marks is not None:
            self.run_query('INSERT INTO marks (student_id,exam_id,subject_id,marks) VALUES (?,?,?,?)',(sid,exam,sub,marks))
            self.conn.commit()
            messagebox.showinfo('Saved','Mark recorded')

    def load_students(self):
        cur = self.run_query('SELECT id,name FROM students ORDER BY name')
        self.students = cur.fetchall()

    def load_marks(self):
        sid = self.sid_var.get().strip()
        if not sid:
            messagebox.showinfo('Info','Enter student ID')
            return
        cur = self.run_query('SELECT m.marks, s.name FROM marks m LEFT JOIN subjects s ON m.subject_id = s.id WHERE m.student_id=?',(sid,))
        rows = cur.fetchall()
        for i in self.tree.get_children(): self.tree.delete(i)
        for r in rows: self.tree.insert('', 'end', values=(r[1], r[0]))

    def generate_report(self):
        sid = self.sid_var.get().strip()
        if not sid:
            messagebox.showinfo('Info','Enter student ID')
            return
        cur = self.run_query('SELECT name,class,section FROM students WHERE id=?',(sid,))
        st = cur.fetchone()
        if not st:
            messagebox.showinfo('Error','Student not found')
            return
        cur = self.run_query('SELECT s.name, m.marks FROM marks m LEFT JOIN subjects s ON m.subject_id=s.id WHERE m.student_id=?',(sid,))
        rows = cur.fetchall()
        out = 'Report Card\n'
        out += f'Name: {st[0]}\nClass/Section: {st[1]}\n\nMarks:\n'
        for r in rows:
            out += f'{r[0]}: {r[1]}\n'
        path = filedialog.asksaveasfilename(defaultextension='.txt', filetypes=[('Text','*.txt')])
        if not path: return
        with open(path,'w',encoding='utf-8') as f:
            f.write(out)
        messagebox.showinfo('Saved','Report exported as text file')

if __name__ == '__main__':
    init_db()
    app = SchoolApp()
    app.protocol('WM_DELETE_WINDOW', app.on_closing)
    app.mainloop()
