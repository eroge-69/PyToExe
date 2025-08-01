import json
from tkinter import *
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime

DATA_FILE = "tasks_data.json"

def load_data():
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except:
        return []

def save_data(tasks):
    with open(DATA_FILE, "w", encoding="utf-8") as file:
        json.dump(tasks, file, ensure_ascii=False, indent=2)

def run_app():
    tasks = load_data()

    def refresh_table():
        for i in tree.get_children():
            tree.delete(i)
        today = datetime.now().date()
        total = 0
        for task in tasks:
            task_date = datetime.strptime(task["date"], "%Y-%m-%d").date()
            if task_date == today:
                tree.insert("", "end", values=(task["name"], task["amount"], task["time"], task["date"], task["status"]))
                if task["status"] != "تم":
                    total += float(task["amount"])
        total_label.config(text=f"إجمالي المطلوب اليوم: {total} جنيه")

    def add_task():
        name = name_entry.get()
        amount = amount_entry.get()
        time = time_entry.get()
        date = date_entry.get()
        if not name or not amount or not time or not date:
            messagebox.showwarning("تحذير", "من فضلك املأ كل الخانات")
            return
        try:
            float(amount)
            datetime.strptime(date, "%Y-%m-%d")
        except:
            messagebox.showerror("خطأ", "صيغة التاريخ أو المبلغ غير صحيحة")
            return
        tasks.append({"name": name, "amount": amount, "time": time, "date": date, "status": "قيد التنفيذ"})
        save_data(tasks)
        refresh_table()
        name_entry.delete(0, END)
        amount_entry.delete(0, END)
        time_entry.delete(0, END)

    def mark_done():
        selected = tree.selection()
        for item in selected:
            values = tree.item(item, "values")
            for task in tasks:
                if (task["name"], task["amount"], task["time"], task["date"], task["status"]) == values:
                    task["status"] = "تم"
        save_data(tasks)
        refresh_table()

    def postpone_task():
        selected = tree.selection()
        if not selected:
            return
        new_day = simpledialog.askstring("تأجيل", "ادخل تاريخ التأجيل الجديد (yyyy-mm-dd):")
        try:
            datetime.strptime(new_day, "%Y-%m-%d")
        except:
            messagebox.showerror("خطأ", "صيغة التاريخ غير صحيحة")
            return
        for item in selected:
            values = tree.item(item, "values")
            for task in tasks:
                if (task["name"], task["amount"], task["time"], task["date"], task["status"]) == values:
                    task["date"] = new_day
        save_data(tasks)
        refresh_table()

    root = Tk()
    root.title("مذكرة المهمات اليومية")
    root.geometry("850x500")
    root.configure(bg="#f0f0f0")

    frame = Frame(root)
    frame.pack(pady=10)

    Label(frame, text="الاسم").grid(row=0, column=0)
    name_entry = Entry(frame)
    name_entry.grid(row=0, column=1)

    Label(frame, text="المبلغ").grid(row=0, column=2)
    amount_entry = Entry(frame)
    amount_entry.grid(row=0, column=3)

    Label(frame, text="الساعة").grid(row=0, column=4)
    time_entry = Entry(frame)
    time_entry.grid(row=0, column=5)

    Label(frame, text="التاريخ").grid(row=0, column=6)
    date_entry = Entry(frame)
    date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
    date_entry.grid(row=0, column=7)

    Button(root, text="إضافة", command=add_task).pack(pady=5)

    columns = ("الاسم", "المبلغ", "الساعة", "التاريخ", "الحالة")
    tree = ttk.Treeview(root, columns=columns, show="headings", height=10)
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, anchor="center")
    tree.pack()

    total_label = Label(root, text="", font=("Arial", 14), bg="#f0f0f0")
    total_label.pack(pady=10)

    Button(root, text="تمييز كمُنتهية", command=mark_done).pack(side=LEFT, padx=10, pady=5)
    Button(root, text="تأجيل", command=postpone_task).pack(side=LEFT, padx=10)

    refresh_table()
    root.mainloop()

if __name__ == "__main__":
    run_app()
