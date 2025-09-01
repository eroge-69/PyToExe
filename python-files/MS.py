import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
import sqlite3
import datetime

# قاعدة البيانات
conn = sqlite3.connect("mohader.db")
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS mohader (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    jeha TEXT,
    number TEXT,
    name TEXT,
    stage INTEGER,
    status TEXT,
    start_date TEXT,
    end_date TEXT
)
""")
conn.commit()

# المراحل
stages = {
    1: "استلام المحضر",
    2: "عند رئيس الجامعة للتوقيع",
    3: "عاد موقعًا من رئيس الجامعة",
    4: "أحيل إلى قسم الرقابة والتدقيق",
    5: "عاد من قسم الرقابة والتدقيق",
    6: "تمت المصادقة عليه من قبل الرئيس",
    7: "أعيد إلى الجهة المعنية (منتهي)"
}

# الجهات
jehat = [
    "مكتب الخدمات العلمية والاستشارية الزراعية / كلية الزراعة",
    "مكتب اللغات الحية والترجمة / كلية الاداب",
    "المكتب الاستشاري الهندسي / كلية الهندسة",
    "المكتب الاستشاري في كلية طب الاسنان",
    "المكتب الاستشاري لنظم المعلومات والحاسبات الالكترونية / مركز الحاسبة الالكترونية",
    "مكتب الخدمات الاستشارية والمالية / كلية الادارة والاقتصاد",
    "المكتب الاستشاري الاحصائي / كلية علوم الحاسوب والرياضيات"
]

class MohaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("متابعة المحاضر")
        self.current_jeha = None
        self.start_screen()

    def start_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        tk.Label(self.root, text="اختر الجهة:", font=("Arial", 14)).pack(pady=10)

        self.jeha_var = tk.StringVar()
        jeha_combo = ttk.Combobox(self.root, textvariable=self.jeha_var, values=jehat, state="readonly", width=80)
        jeha_combo.pack(pady=5)
        jeha_combo.current(0)

        tk.Button(self.root, text="دخول", command=self.open_jeha).pack(pady=10)

    def open_jeha(self):
        self.current_jeha = self.jeha_var.get()
        self.show_mohader_list()

    def show_mohader_list(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        tk.Label(self.root, text=f"المحاضر - {self.current_jeha}", font=("Arial", 14)).pack(pady=10)

        self.tree = ttk.Treeview(self.root, columns=("number", "name", "stage", "status"), show="headings")
        self.tree.heading("number", text="رقم")
        self.tree.heading("name", text="الاسم")
        self.tree.heading("stage", text="المرحلة")
        self.tree.heading("status", text="الحالة")
        self.tree.pack(pady=10, fill="both", expand=True)

        self.load_mohader()

        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="إضافة محضر", command=self.add_mohader).grid(row=0, column=0, padx=5)
        tk.Button(btn_frame, text="فتح", command=self.open_mohader).grid(row=0, column=1, padx=5)
        tk.Button(btn_frame, text="رجوع", command=self.start_screen).grid(row=0, column=2, padx=5)

    def load_mohader(self):
        for i in self.tree.get_children():
            self.tree.delete(i)

        c.execute("SELECT id, number, name, stage, status FROM mohader WHERE jeha=?", (self.current_jeha,))
        for row in c.fetchall():
            self.tree.insert("", "end", values=(row[1], row[2], stages[row[3]], row[4]), iid=row[0])

    def add_mohader(self):
        number = simpledialog.askstring("إضافة", "أدخل رقم المحضر:")
        if not number: return
        name = simpledialog.askstring("إضافة", "أدخل اسم المحضر:")
        if not name: return

        start_date = datetime.date.today().isoformat()
        c.execute("INSERT INTO mohader (jeha, number, name, stage, status, start_date) VALUES (?, ?, ?, ?, ?, ?)",
                  (self.current_jeha, number, name, 1, "نشط", start_date))
        conn.commit()
        self.load_mohader()

    def open_mohader(self):
        selected = self.tree.focus()
        if not selected:
            messagebox.showwarning("تنبيه", "اختر محضر أولاً")
            return

        mohader_id = int(selected)
        c.execute("SELECT number, name, stage, status FROM mohader WHERE id=?", (mohader_id,))
        number, name, stage, status = c.fetchone()

        top = tk.Toplevel(self.root)
        top.title("تفاصيل المحضر")

        tk.Label(top, text=f"رقم: {number}", font=("Arial", 12)).pack(pady=5)
        tk.Label(top, text=f"الاسم: {name}", font=("Arial", 12)).pack(pady=5)
        self.stage_label = tk.Label(top, text=f"المرحلة الحالية: {stages[stage]}", font=("Arial", 12))
        self.stage_label.pack(pady=5)
        self.status_label = tk.Label(top, text=f"الحالة: {status}", font=("Arial", 12))
        self.status_label.pack(pady=5)

        def next_stage():
            nonlocal stage, status
            if stage < 7:
                stage += 1
                if stage == 7:
                    status = "منتهي"
                    end_date = datetime.date.today().isoformat()
                    c.execute("UPDATE mohader SET stage=?, status=?, end_date=? WHERE id=?",
                              (stage, status, end_date, mohader_id))
                else:
                    c.execute("UPDATE mohader SET stage=? WHERE id=?", (stage, mohader_id))
                conn.commit()
                self.stage_label.config(text=f"المرحلة الحالية: {stages[stage]}")
                self.status_label.config(text=f"الحالة: {status}")
                self.load_mohader()

        tk.Button(top, text="التالي", command=next_stage).pack(pady=10)

# تشغيل البرنامج
root = tk.Tk()
app = MohaderApp(root)
root.mainloop()
