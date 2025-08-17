import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import sqlite3
from datetime import datetime, timedelta
import time

DB_NAME = "hotel.db"

# ===== تهيئة قاعدة البيانات =====
def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    # جدول المستخدمين
    c.execute("""CREATE TABLE IF NOT EXISTS users (
                    username TEXT PRIMARY KEY,
                    password TEXT,
                    role TEXT
                 )""")
    c.execute("INSERT OR IGNORE INTO users VALUES ('admin','admin123','admin')")
    c.execute("INSERT OR IGNORE INTO users VALUES ('clerk','clerk123','clerk')")
    
    # جدول الموظفين
    c.execute("""CREATE TABLE IF NOT EXISTS employees (
                    emp_id TEXT PRIMARY KEY,
                    name TEXT,
                    section TEXT,
                    phone TEXT
                 )""")
    
    # جدول الغرف
    c.execute("""CREATE TABLE IF NOT EXISTS rooms (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    block INTEGER,
                    room_number INTEGER,
                    status TEXT DEFAULT 'empty',
                    owner_emp_id TEXT,
                    visitor_emp_id TEXT,
                    check_in_date TEXT,
                    check_out_date TEXT,
                    last_update TEXT,
                    UNIQUE(block, room_number)
                 )""")
    
    # جدول سجل التعديلات على الغرف
    c.execute("""CREATE TABLE IF NOT EXISTS room_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    room_id INTEGER,
                    status TEXT,
                    emp_id TEXT,
                    change_date TEXT,
                    FOREIGN KEY(room_id) REFERENCES rooms(id)
                 )""")
    
    # إضافة البلوكات والغرف الافتراضية
    try:
        for blk in range(1, 9):
            for room in range(1, 13):
                c.execute("INSERT OR IGNORE INTO rooms (block, room_number) VALUES (?,?)", (blk, room))
        for room in range(1, 61):
            c.execute("INSERT OR IGNORE INTO rooms (block, room_number) VALUES (9, ?)", (room,))
        conn.commit()
    except sqlite3.IntegrityError:
        messagebox.showerror("خطأ", "يوجد غرف مكررة في قاعدة البيانات")
    finally:
        conn.close()

# ===== تسجيل الدخول =====
def login():
    username = entry_user.get()
    password = entry_pass.get()
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT role FROM users WHERE username=? AND password=?", (username, password))
    result = c.fetchone()
    conn.close()
    if result:
        root.destroy()
        open_main_window(result[0])
    else:
        messagebox.showerror("خطأ", "بيانات الدخول غير صحيحة")

# ===== إدارة البلوكات والغرف =====
def manage_blocks():
    win = tk.Toplevel()
    win.title("إدارة البلوكات والغرف - إعداد المهندس عبدالرحيم اللافي")
    win.geometry("400x350")
    
    def add_block():
        block_num = simpledialog.askinteger("بلوك جديد", "أدخل رقم البلوك:")
        if not block_num:
            return
        num_rooms = simpledialog.askinteger("عدد الغرف", "كم عدد الغرف في هذا البلوك؟")
        if not num_rooms:
            return
        
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        try:
            for r in range(1, num_rooms + 1):
                c.execute("INSERT INTO rooms (block, room_number) VALUES (?,?)", (block_num, r))
            conn.commit()
            load_rooms()
            messagebox.showinfo("تم", f"تم إضافة البلوك {block_num} بعدد {num_rooms} غرفة")
        except sqlite3.IntegrityError:
            messagebox.showerror("خطأ", "البلوك أو الغرف موجودة بالفعل")
        finally:
            conn.close()
    
    def add_rooms():
        block_num = simpledialog.askinteger("إضافة غرف", "أدخل رقم البلوك:")
        if not block_num:
            return
        num_rooms = simpledialog.askinteger("إضافة غرف", "كم عدد الغرف المراد إضافتها؟")
        if not num_rooms:
            return
        
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        try:
            c.execute("SELECT MAX(room_number) FROM rooms WHERE block=?", (block_num,))
            last = c.fetchone()[0] or 0
            for r in range(last + 1, last + num_rooms + 1):
                c.execute("INSERT INTO rooms (block, room_number) VALUES (?,?)", (block_num, r))
            conn.commit()
            load_rooms()
            messagebox.showinfo("تم", f"تم إضافة {num_rooms} غرفة إلى البلوك {block_num}")
        except sqlite3.IntegrityError:
            messagebox.showerror("خطأ", "بعض الغرف موجودة بالفعل")
        finally:
            conn.close()
    
    def delete_room():
        block_num = simpledialog.askinteger("حذف غرفة", "أدخل رقم البلوك:")
        if not block_num:
            return
        room_num = simpledialog.askinteger("حذف غرفة", "أدخل رقم الغرفة:")
        if not room_num:
            return
        
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        try:
            c.execute("SELECT id,status FROM rooms WHERE block=? AND room_number=?", (block_num, room_num))
            row = c.fetchone()
            if not row:
                messagebox.showerror("خطأ", "الغرفة غير موجودة")
                return
            if row[1] != "empty":
                messagebox.showerror("خطأ", "لا يمكن حذف غرفة مشغولة")
                return
            c.execute("DELETE FROM rooms WHERE id=?", (row[0],))
            conn.commit()
            load_rooms()
            messagebox.showinfo("تم", f"تم حذف الغرفة {room_num} من البلوك {block_num}")
        finally:
            conn.close()
    
    def delete_block():
        block_num = simpledialog.askinteger("حذف بلوك", "أدخل رقم البلوك:")
        if not block_num:
            return
        
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        try:
            c.execute("SELECT COUNT(*) FROM rooms WHERE block=? AND status!='empty'", (block_num,))
            if c.fetchone()[0] > 0:
                messagebox.showerror("خطأ", "لا يمكن حذف بلوك به غرف مشغولة")
                return
            
            c.execute("DELETE FROM rooms WHERE block=?", (block_num,))
            conn.commit()
            load_rooms()
            messagebox.showinfo("تم", f"تم حذف البلوك {block_num} بالكامل")
        finally:
            conn.close()
    
    tk.Button(win, text="إضافة بلوك", command=add_block, bg='blue', fg='white').pack(pady=5)
    tk.Button(win, text="إضافة غرف", command=add_rooms, bg='green', fg='white').pack(pady=5)
    tk.Button(win, text="حذف غرفة", command=delete_room, bg='red', fg='white').pack(pady=5)
    tk.Button(win, text="حذف بلوك", command=delete_block, bg='purple', fg='white').pack(pady=5)

# ===== عرض الغرف مع التمرير =====
buttons = {}
blinking_buttons = {}
def load_rooms():
    for widget in frame_rooms.winfo_children():
        widget.destroy()
    
    # إنشاء إطار التمرير
    container = ttk.Frame(frame_rooms)
    canvas = tk.Canvas(container)
    scroll_y = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
    scroll_x = ttk.Scrollbar(container, orient="horizontal", command=canvas.xview)
    
    scrollable_frame = ttk.Frame(canvas)
    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(
            scrollregion=canvas.bbox("all"))
    )
    
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)
    
    container.pack(fill="both", expand=True)
    canvas.pack(side="left", fill="both", expand=True)
    scroll_y.pack(side="right", fill="y")
    scroll_x.pack(side="bottom", fill="x")
    
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT * FROM rooms ORDER BY block, room_number")
    all_rooms = c.fetchall()
    conn.close()
    
    today = datetime.now().date()
    
    for blk_num in range(1, 10):
        block_frame = tk.LabelFrame(scrollable_frame, text=f"بلوك {blk_num}", font=('Arial',12,'bold'))
        block_frame.pack(fill='x', padx=10, pady=5, anchor='nw')
        
        # شرح ألوان الحالات (للمدير فقط)
        if current_role == "admin":
            color_frame = tk.Frame(block_frame)
            color_frame.pack(anchor='e', padx=5)
            tk.Label(color_frame, text="  ", bg="red").pack(side='left', padx=2)
            tk.Label(color_frame, text="مملوكة").pack(side='left', padx=5)
            tk.Label(color_frame, text="  ", bg="lightgray").pack(side='left', padx=2)
            tk.Label(color_frame, text="فارغة").pack(side='left', padx=5)
        
        row_frame = tk.Frame(block_frame)
        row_frame.pack(anchor='w')
        room_count = 0
        
        for room in all_rooms:
            room_id, blk, room_num, status, owner, visitor, checkin, checkout, last_update = room
            if blk != blk_num:
                continue
            
            # تحديد اللون حسب الصلاحية
            if current_role == "admin":
                color = "lightgray" if status == "empty" else "red"
            else:
                color = "lightgray"
                if status == "owner_present":
                    color = "red"
                elif status == "visitor_present" or status == "visitor_present_without_owner":
                    color = "yellow"
                elif status == "owner_away":
                    if checkout:
                        try:
                            out_date = datetime.strptime(checkout, "%Y-%m-%d").date()
                            if out_date - timedelta(days=1) == today:  # سيعود غداً
                                color = "orange"
                                blinking_buttons[room_id] = True
                            elif out_date > today:
                                color = "green"
                        except:
                            pass
                if last_update:
                    try:
                        last = datetime.strptime(last_update, "%Y-%m-%d").date()
                        if (today - last).days >= 16:
                            color = "blue"
                    except:
                        pass
            
            if room_count % 20 == 0 and room_count != 0:
                row_frame = tk.Frame(block_frame)
                row_frame.pack(anchor='w')
            
            btn = tk.Button(row_frame, text=f"{room_num}", width=5, height=2, bg=color,
                            command=lambda rid=room_id: room_window(rid, current_role))
            btn.pack(side='left', padx=2, pady=2)
            buttons[room_id] = btn
            room_count += 1
    
    # بدء وميض الأزرار البرتقالية
    blink_question_mark()

def blink_question_mark():
    for room_id, btn in buttons.items():
        if room_id in blinking_buttons:
            current_text = btn.cget("text")
            if "?" in current_text:
                btn.config(text=current_text.replace("?", ""))
            else:
                btn.config(text=current_text + "?")
    
    # جدولة الوظيفة للتنفيذ بعد 500 مللي ثانية (0.5 ثانية)
    frame_rooms.after(500, blink_question_mark)

# ===== نافذة الغرفة للمدير =====
def admin_room_window(room_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT block, room_number, owner_emp_id FROM rooms WHERE id=?", (room_id,))
    room = c.fetchone()
    conn.close()
    block, room_number, owner_id = room
    
    win = tk.Toplevel()
    win.title(f"غرفة {room_number} - بلوك {block} - إعداد المهندس عبدالرحيم اللافي")
    win.geometry("350x400")
    
    tk.Label(win, text="بيانات المالك", font=('Arial', 14, 'bold')).pack(pady=10)
    
    owner_vars = {"ID": tk.StringVar(), "Name": tk.StringVar(), "Section": tk.StringVar(), "Phone": tk.StringVar()}
    
    if owner_id:
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("SELECT emp_id,name,section,phone FROM employees WHERE emp_id=?", (owner_id,))
        data = c.fetchone()
        conn.close()
        if data:
            owner_vars["ID"].set(data[0])
            owner_vars["Name"].set(data[1])
            owner_vars["Section"].set(data[2])
            owner_vars["Phone"].set(data[3])
    
    tk.Label(win, text="رقم الموظف:").pack()
    tk.Entry(win, textvariable=owner_vars["ID"]).pack()
    tk.Label(win, text="الاسم:").pack()
    tk.Entry(win, textvariable=owner_vars["Name"], state='readonly').pack()
    tk.Label(win, text="القسم:").pack()
    tk.Entry(win, textvariable=owner_vars["Section"], state='readonly').pack()
    tk.Label(win, text="الهاتف:").pack()
    tk.Entry(win, textvariable=owner_vars["Phone"], state='readonly').pack()
    
    def save_owner():
        emp_id = owner_vars["ID"].get()
        if not emp_id:
            messagebox.showerror("خطأ","يجب إدخال رقم الموظف")
            return
        
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        
        # التحقق من أن الموظف لا يملك غرفة أخرى
        c.execute("SELECT COUNT(*) FROM rooms WHERE owner_emp_id=? AND id!=?", (emp_id, room_id))
        if c.fetchone()[0] > 0:
            messagebox.showerror("خطأ","هذا الموظف يملك غرفة أخرى بالفعل")
            conn.close()
            return
        
        c.execute("SELECT name,section,phone FROM employees WHERE emp_id=?", (emp_id,))
        data = c.fetchone()
        if not data:
            messagebox.showerror("خطأ","الموظف غير مسجل")
            conn.close()
            return
        
        c.execute("UPDATE rooms SET owner_emp_id=?, status='owner_present', last_update=? WHERE id=?",
                  (emp_id, datetime.now().strftime("%Y-%m-%d"), room_id))
        
        # تسجيل التعديل في السجل
        c.execute("INSERT INTO room_history (room_id, status, emp_id, change_date) VALUES (?,?,?,?)",
                  (room_id, 'owner_present', emp_id, datetime.now().strftime("%Y-%m-%d")))
        
        conn.commit()
        conn.close()
        
        owner_vars["Name"].set(data[0])
        owner_vars["Section"].set(data[1])
        owner_vars["Phone"].set(data[2])
        load_rooms()
        messagebox.showinfo("تم","تم تعيين المالك بنجاح")
    
    tk.Button(win, text="حفظ", command=save_owner, bg='green', fg='white').pack(pady=10)

# ===== نافذة الغرفة للموظف =====
def clerk_room_window(room_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("""SELECT block, room_number, owner_emp_id, visitor_emp_id, status, check_out_date 
                 FROM rooms WHERE id=?""", (room_id,))
    room = c.fetchone()
    conn.close()
    block, room_number, owner_id, visitor_id, status, check_out = room
    
    win = tk.Toplevel()
    win.title(f"غرفة {room_number} - بلوك {block} - إعداد المهندس عبدالرحيم اللافي")
    win.geometry("400x650")
    
    # قسم بيانات المالك
    owner_frame = tk.LabelFrame(win, text="بيانات المالك", font=('Arial',14,'bold'))
    owner_frame.pack(fill='x', padx=10, pady=5)
    
    owner_vars = {"ID": tk.StringVar(), "Name": tk.StringVar(), "Section": tk.StringVar(), "Phone": tk.StringVar()}
    
    if owner_id:
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("SELECT emp_id,name,section,phone FROM employees WHERE emp_id=?", (owner_id,))
        data = c.fetchone()
        conn.close()
        if data:
            owner_vars["ID"].set(data[0])
            owner_vars["Name"].set(data[1])
            owner_vars["Section"].set(data[2])
            owner_vars["Phone"].set(data[3])
    
    tk.Label(owner_frame, text="رقم الموظف:").pack()
    tk.Entry(owner_frame, textvariable=owner_vars["ID"], state='readonly').pack()
    tk.Label(owner_frame, text="الاسم:").pack()
    tk.Entry(owner_frame, textvariable=owner_vars["Name"], state='readonly').pack()
    tk.Label(owner_frame, text="القسم:").pack()
    tk.Entry(owner_frame, textvariable=owner_vars["Section"], state='readonly').pack()
    tk.Label(owner_frame, text="الهاتف:").pack()
    tk.Entry(owner_frame, textvariable=owner_vars["Phone"], state='readonly').pack()
    
    # قسم بيانات الزائر
    visitor_frame = tk.LabelFrame(win, text="بيانات الزائر", font=('Arial',14,'bold'))
    visitor_frame.pack(fill='x', padx=10, pady=5)
    
    visitor_vars = {"ID": tk.StringVar(), "Name": tk.StringVar(), "Section": tk.StringVar(), "Phone": tk.StringVar()}
    
    if visitor_id:
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("SELECT emp_id,name,section,phone FROM employees WHERE emp_id=?", (visitor_id,))
        data = c.fetchone()
        conn.close()
        if data:
            visitor_vars["ID"].set(data[0])
            visitor_vars["Name"].set(data[1])
            visitor_vars["Section"].set(data[2])
            visitor_vars["Phone"].set(data[3])
    
    tk.Label(visitor_frame, text="رقم الزائر:").pack()
    tk.Entry(visitor_frame, textvariable=visitor_vars["ID"], state='readonly').pack()
    tk.Label(visitor_frame, text="الاسم:").pack()
    tk.Entry(visitor_frame, textvariable=visitor_vars["Name"], state='readonly').pack()
    tk.Label(visitor_frame, text="القسم:").pack()
    tk.Entry(visitor_frame, textvariable=visitor_vars["Section"], state='readonly').pack()
    tk.Label(visitor_frame, text="الهاتف:").pack()
    tk.Entry(visitor_frame, textvariable=visitor_vars["Phone"], state='readonly').pack()
    
    # قسم التحكم
    control_frame = tk.LabelFrame(win, text="التحكم", font=('Arial',14,'bold'))
    control_frame.pack(fill='x', padx=10, pady=5)
    
    def owner_present():
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("""UPDATE rooms SET status='owner_present', visitor_emp_id=NULL, 
                     check_in_date=NULL, check_out_date=NULL, last_update=? 
                     WHERE id=?""", (datetime.now().strftime("%Y-%m-%d"), room_id))
        
        # تسجيل التعديل في السجل
        c.execute("INSERT INTO room_history (room_id, status, emp_id, change_date) VALUES (?,?,?,?)",
                  (room_id, 'owner_present', owner_id, datetime.now().strftime("%Y-%m-%d")))
        
        conn.commit()
        conn.close()
        load_rooms()
        win.destroy()
        messagebox.showinfo("تم", "تم تحديث حالة الغرفة: المالك موجود")
    
    def owner_away():
        return_date = simpledialog.askstring("تاريخ العودة", "أدخل تاريخ عودة المالك (YYYY-MM-DD):")
        if not return_date:
            return
        
        try:
            datetime.strptime(return_date, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("خطأ", "صيغة التاريخ غير صحيحة. استخدم YYYY-MM-DD")
            return
        
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("""UPDATE rooms SET status='owner_away', check_out_date=?, last_update=? 
                     WHERE id=?""", (return_date, datetime.now().strftime("%Y-%m-%d"), room_id))
        
        # تسجيل التعديل في السجل
        c.execute("INSERT INTO room_history (room_id, status, emp_id, change_date) VALUES (?,?,?,?)",
                  (room_id, 'owner_away', owner_id, datetime.now().strftime("%Y-%m-%d")))
        
        conn.commit()
        conn.close()
        load_rooms()
        win.destroy()
        messagebox.showinfo("تم", "تم تسجيل مغادرة المالك وتاريخ العودة")
    
    def add_visitor():
        if status != 'owner_away' and status != 'empty':
            messagebox.showerror("خطأ", "لا يمكن إضافة زائر إلا بعد مغادرة المالك أو إذا كانت الغرفة فارغة")
            return
        
        emp_id = simpledialog.askstring("رقم الزائر", "أدخل رقم موظف الزائر:")
        if not emp_id:
            return
        
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        
        # التحقق من أن الزائر ليس في غرفة أخرى
        c.execute("SELECT COUNT(*) FROM rooms WHERE visitor_emp_id=?", (emp_id,))
        if c.fetchone()[0] > 0:
            messagebox.showerror("خطأ", "هذا الزائر موجود بالفعل في غرفة أخرى")
            conn.close()
            return
        
        c.execute("SELECT name,section,phone FROM employees WHERE emp_id=?", (emp_id,))
        data = c.fetchone()
        if not data:
            messagebox.showerror("خطأ", "الموظف غير موجود")
            conn.close()
            return
        
        new_status = 'visitor_present'
        if status == 'empty':
            new_status = 'visitor_present_without_owner'
        
        c.execute("""UPDATE rooms SET visitor_emp_id=?, status=?, 
                     check_in_date=?, last_update=? WHERE id=?""",
                  (emp_id, new_status, datetime.now().strftime("%Y-%m-%d"), 
                   datetime.now().strftime("%Y-%m-%d"), room_id))
        
        # تسجيل التعديل في السجل
        c.execute("INSERT INTO room_history (room_id, status, emp_id, change_date) VALUES (?,?,?,?)",
                  (room_id, new_status, emp_id, datetime.now().strftime("%Y-%m-%d")))
        
        conn.commit()
        conn.close()
        load_rooms()
        win.destroy()
        messagebox.showinfo("تم", "تم إضافة الزائر بنجاح")
    
    def force_visitor_out():
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        
        # تحديد الحالة الجديدة بناءً على وجود مالك
        c.execute("SELECT owner_emp_id FROM rooms WHERE id=?", (room_id,))
        owner_exists = c.fetchone()[0] is not None
        
        new_status = 'owner_away' if owner_exists else 'empty'
        
        c.execute("""UPDATE rooms SET visitor_emp_id=NULL, status=?, 
                     check_in_date=NULL, last_update=? WHERE id=?""",
                  (new_status, datetime.now().strftime("%Y-%m-%d"), room_id))
        
        # تسجيل التعديل في السجل
        c.execute("INSERT INTO room_history (room_id, status, emp_id, change_date) VALUES (?,?,?,?)",
                  (room_id, new_status, None, datetime.now().strftime("%Y-%m-%d")))
        
        conn.commit()
        conn.close()
        load_rooms()
        messagebox.showinfo("تم", "تم إخلاء الزائر من الغرفة")
        win.destroy()
    
    def extend_return_date():
        if status != 'owner_away':
            messagebox.showerror("خطأ", "هذا الخيار متاح فقط للغرف التي بها مالك مسافر")
            return
        
        new_date = simpledialog.askstring("تمديد الإقامة", "أدخل التاريخ الجديد للعودة (YYYY-MM-DD):")
        if not new_date:
            return
        
        try:
            datetime.strptime(new_date, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("خطأ", "صيغة التاريخ غير صحيحة. استخدم YYYY-MM-DD")
            return
        
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("UPDATE rooms SET check_out_date=?, last_update=? WHERE id=?", 
                  (new_date, datetime.now().strftime("%Y-%m-%d"), room_id))
        
        # تسجيل التعديل في السجل
        c.execute("INSERT INTO room_history (room_id, status, emp_id, change_date) VALUES (?,?,?,?)",
                  (room_id, 'owner_away_extended', owner_id, datetime.now().strftime("%Y-%m-%d")))
        
        conn.commit()
        conn.close()
        load_rooms()
        messagebox.showinfo("تم", f"تم تمديد موعد العودة إلى {new_date}")
        win.destroy()
    
    def show_room_history():
        history_win = tk.Toplevel(win)
        history_win.title(f"سجل الغرفة {room_number} - بلوك {block}")
        history_win.geometry("600x400")
        
        # إنشاء Treeview مع أشرطة التمرير
        container = ttk.Frame(history_win)
        container.pack(fill='both', expand=True)
        
        tree = ttk.Treeview(container, columns=("Status","EmpID","Date"), show='headings')
        tree.heading("Status", text="الحالة")
        tree.heading("EmpID", text="رقم الموظف")
        tree.heading("Date", text="تاريخ التعديل")
        
        scroll_y = ttk.Scrollbar(container, orient="vertical", command=tree.yview)
        scroll_x = ttk.Scrollbar(container, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)
        
        tree.pack(side='left', fill='both', expand=True)
        scroll_y.pack(side='right', fill='y')
        scroll_x.pack(side='bottom', fill='x')
        
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("""SELECT status, emp_id, change_date FROM room_history 
                     WHERE room_id=? ORDER BY change_date DESC LIMIT 4""", (room_id,))
        
        for row in c.fetchall():
            status, emp_id, change_date = row
            status_text = {
                'owner_present': 'مالك موجود',
                'owner_away': 'مالك مسافر',
                'owner_away_extended': 'تم تمديد الإقامة',
                'visitor_present': 'زائر موجود',
                'visitor_present_without_owner': 'زائر بدون مالك',
                'empty': 'غرفة فارغة'
            }.get(status, status)
            
            tree.insert('', 'end', values=(status_text, emp_id or '-', change_date))
        
        conn.close()
    
    # عرض الأزرار حسب الحالة
    if status == 'owner_present':
        tk.Button(control_frame, text="تسجيل خروج المالك", command=owner_away, 
                  bg='green', fg='white').pack(fill='x', pady=5)
    elif status == 'owner_away':
        tk.Button(control_frame, text="تسجيل عودة المالك", command=owner_present, 
                  bg='red', fg='white').pack(fill='x', pady=5)
        tk.Button(control_frame, text="إضافة زائر", command=add_visitor, 
                  bg='yellow', fg='black').pack(fill='x', pady=5)
        tk.Button(control_frame, text="تمديد موعد العودة", command=extend_return_date, 
                  bg='orange', fg='black').pack(fill='x', pady=5)
    elif status == 'visitor_present' or status == 'visitor_present_without_owner':
        tk.Button(control_frame, text="خروج الزائر بدون شرط", command=force_visitor_out, 
                  bg='orange', fg='black').pack(fill='x', pady=5)
    elif status == 'empty':
        tk.Button(control_frame, text="إضافة زائر", command=add_visitor, 
                  bg='yellow', fg='black').pack(fill='x', pady=5)
    
    # زر عرض سجل الغرفة
    tk.Button(control_frame, text="عرض سجل الغرفة", command=show_room_history, 
              bg='blue', fg='white').pack(fill='x', pady=5)

# ===== إدارة الموظفين =====
def manage_employees():
    win = tk.Toplevel()
    win.title("إدارة الموظفين - إعداد المهندس عبدالرحيم اللافي")
    win.geometry("600x400")
    
    # إنشاء Treeview مع أشرطة التمرير
    container = ttk.Frame(win)
    container.pack(fill='both', expand=True)
    
    tree = ttk.Treeview(container, columns=("ID","Name","Section","Phone"), show='headings')
    tree.heading("ID", text="رقم الموظف")
    tree.heading("Name", text="الاسم")
    tree.heading("Section", text="القسم")
    tree.heading("Phone", text="الهاتف")
    
    scroll_y = ttk.Scrollbar(container, orient="vertical", command=tree.yview)
    scroll_x = ttk.Scrollbar(container, orient="horizontal", command=tree.xview)
    tree.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)
    
    tree.pack(side='left', fill='both', expand=True)
    scroll_y.pack(side='right', fill='y')
    scroll_x.pack(side='bottom', fill='x')
    
    def load_emps():
        for i in tree.get_children():
            tree.delete(i)
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("SELECT * FROM employees")
        for row in c.fetchall():
            tree.insert('', 'end', values=row)
        conn.close()
    
    def add_emp():
        win_emp = tk.Toplevel()
        win_emp.title("إضافة موظف - إعداد المهندس عبدالرحيم اللافي")
        win_emp.geometry("300x250")
        
        tk.Label(win_emp, text="رقم الموظف:").pack()
        emp_id = tk.Entry(win_emp)
        emp_id.pack()
        
        tk.Label(win_emp, text="الاسم:").pack()
        name = tk.Entry(win_emp)
        name.pack()
        
        tk.Label(win_emp, text="القسم:").pack()
        section = tk.Entry(win_emp)
        section.pack()
        
        tk.Label(win_emp, text="الهاتف:").pack()
        phone = tk.Entry(win_emp)
        phone.pack()
        
        def save():
            if not emp_id.get() or not name.get():
                messagebox.showerror("خطأ", "يجب إدخال رقم الموظف والاسم")
                return
            
            conn = sqlite3.connect(DB_NAME)
            c = conn.cursor()
            try:
                c.execute("INSERT INTO employees VALUES (?,?,?,?)", 
                          (emp_id.get(), name.get(), section.get(), phone.get()))
                conn.commit()
                messagebox.showinfo("تم", "تم إضافة الموظف بنجاح")
                
                # مسح الحقول بعد الحفظ الناجح
                emp_id.delete(0, tk.END)
                name.delete(0, tk.END)
                section.delete(0, tk.END)
                phone.delete(0, tk.END)
                
                # تركيز المؤشر على حقل رقم الموظف
                emp_id.focus_set()
                
                # تحديث شجرة الموظفين في النافذة الرئيسية
                load_emps()
                
            except sqlite3.IntegrityError:
                messagebox.showerror("خطأ", "رقم الموظف موجود بالفعل")
            finally:
                conn.close()
        
        # إضافة زر إغلاق منفصل
        btn_frame = tk.Frame(win_emp)
        btn_frame.pack(pady=10)
        
        tk.Button(btn_frame, text="حفظ", command=save, bg='green', fg='white').pack(side='left', padx=5)
        tk.Button(btn_frame, text="إغلاق", command=win_emp.destroy, bg='red', fg='white').pack(side='left', padx=5)
    
    def delete_emp():
        selected = tree.selection()
        if not selected:
            return
        
        emp_id = tree.item(selected[0])['values'][0]
        if messagebox.askyesno("تأكيد", f"هل أنت متأكد من حذف الموظف {emp_id}؟"):
            conn = sqlite3.connect(DB_NAME)
            c = conn.cursor()
            
            # تحديث حالة الغرفة إذا كان الموظف مالكًا لأي غرفة
            c.execute("UPDATE rooms SET owner_emp_id=NULL, status='empty' WHERE owner_emp_id=?", (emp_id,))
            
            # حذف الموظف
            c.execute("DELETE FROM employees WHERE emp_id=?", (emp_id,))
            conn.commit()
            conn.close()
            load_emps()
            load_rooms()  # تحديث عرض الغرف
            messagebox.showinfo("تم", f"تم حذف الموظف {emp_id} وتحرير غرفته إن وجدت")
    
    def search_employee():
        emp_id = simpledialog.askstring("بحث عن موظف", "أدخل رقم الموظف:", parent=win)
        if not emp_id:
            return
        
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        
        # البحث في جدول الموظفين
        c.execute("SELECT * FROM employees WHERE emp_id=?", (emp_id,))
        emp_data = c.fetchone()
        
        if not emp_data:
            messagebox.showinfo("نتيجة البحث", "لم يتم العثور على الموظف", parent=win)
            conn.close()
            return
        
        # البحث عن الغرفة التي يشغلها الموظف
        c.execute("SELECT block, room_number FROM rooms WHERE owner_emp_id=? OR visitor_emp_id=?", (emp_id, emp_id))
        room_data = c.fetchone()
        conn.close()
        
        if room_data:
            messagebox.showinfo("نتيجة البحث", 
                              f"الموظف: {emp_data[1]}\nرقم الموظف: {emp_data[0]}\nالقسم: {emp_data[2]}\n"
                              f"يوجد في: بلوك {room_data[0]} - غرفة {room_data[1]}", parent=win)
        else:
            messagebox.showinfo("نتيجة البحث", 
                              f"الموظف: {emp_data[1]}\nرقم الموظف: {emp_data[0]}\nالقسم: {emp_data[2]}\n"
                              "لا يشغل أي غرفة حالياً", parent=win)
    
    btn_frame = tk.Frame(win)
    btn_frame.pack(pady=5)
    
    tk.Button(btn_frame, text="إضافة موظف", command=add_emp, bg='green', fg='white').pack(side='left', padx=5)
    tk.Button(btn_frame, text="حذف موظف", command=delete_emp, bg='red', fg='white').pack(side='left', padx=5)
    tk.Button(btn_frame, text="بحث عن موظف", command=search_employee, bg='blue', fg='white').pack(side='left', padx=5)
    
    load_emps()

# ===== فتح نافذة الغرفة حسب الصلاحية =====
def room_window(room_id, role):
    if role == "admin":
        admin_room_window(room_id)
    else:
        clerk_room_window(room_id)

# ===== النافذة الرئيسية =====
def open_main_window(role):
    global frame_rooms, current_role
    current_role = role
    
    main_win = tk.Tk()
    main_win.title("نظام إدارة الغرف - " + ("مدير" if role == "admin" else "موظف") + " - إعداد المهندس عبدالرحيم اللافي")
    main_win.geometry("1200x700")
    
    # إنشاء القائمة
    menu = tk.Menu(main_win)
    main_win.config(menu=menu)
    
    if role == "admin":
        admin_menu = tk.Menu(menu, tearoff=0)
        menu.add_cascade(label="الإدارة", menu=admin_menu)
        admin_menu.add_command(label="إدارة البلوكات والغرف", command=manage_blocks)
        admin_menu.add_command(label="إدارة الموظفين", command=manage_employees)
    
    # إضافة زر البحث للمدير والموظف
    search_menu = tk.Menu(menu, tearoff=0)
    menu.add_cascade(label="بحث", menu=search_menu)
    search_menu.add_command(label="بحث عن موظف", command=lambda: search_employee(main_win))
    
    frame_rooms = tk.Frame(main_win)
    frame_rooms.pack(fill='both', expand=True)
    
    load_rooms()
    
    main_win.mainloop()

# ===== دالة البحث عن موظف للنافذة الرئيسية =====
def search_employee(parent_window):
    emp_id = simpledialog.askstring("بحث عن موظف", "أدخل رقم الموظف:", parent=parent_window)
    if not emp_id:
        return
    
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    # البحث في جدول الموظفين
    c.execute("SELECT * FROM employees WHERE emp_id=?", (emp_id,))
    emp_data = c.fetchone()
    
    if not emp_data:
        messagebox.showinfo("نتيجة البحث", "لم يتم العثور على الموظف", parent=parent_window)
        conn.close()
        return
    
    # البحث عن الغرفة التي يشغلها الموظف
    c.execute("SELECT block, room_number FROM rooms WHERE owner_emp_id=? OR visitor_emp_id=?", (emp_id, emp_id))
    room_data = c.fetchone()
    conn.close()
    
    if room_data:
        messagebox.showinfo("نتيجة البحث", 
                          f"الموظف: {emp_data[1]}\nرقم الموظف: {emp_data[0]}\nالقسم: {emp_data[2]}\n"
                          f"يوجد في: بلوك {room_data[0]} - غرفة {room_data[1]}", parent=parent_window)
    else:
        messagebox.showinfo("نتيجة البحث", 
                          f"الموظف: {emp_data[1]}\nرقم الموظف: {emp_data[0]}\nالقسم: {emp_data[2]}\n"
                          "لا يشغل أي غرفة حالياً", parent=parent_window)

# ===== بدء البرنامج =====
root = tk.Tk()
root.title("تسجيل الدخول - إعداد المهندس عبدالرحيم اللافي")
root.geometry("300x150")

tk.Label(root, text="اسم المستخدم").pack()
entry_user = tk.Entry(root)
entry_user.pack()

tk.Label(root, text="كلمة المرور").pack()
entry_pass = tk.Entry(root, show='*')
entry_pass.pack()

tk.Button(root, text="دخول", command=login, bg='blue', fg='white').pack(pady=10)

init_db()
root.mainloop()