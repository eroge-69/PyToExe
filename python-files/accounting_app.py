
import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import csv
import os
from datetime import datetime

DB_FILE = os.path.join(os.path.dirname(__file__), "accounting.db")

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute(\"\"\"CREATE TABLE IF NOT EXISTS journal
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  date TEXT,
                  debit TEXT,
                  credit TEXT,
                  amount REAL,
                  description TEXT)\"\"\")
    conn.commit()
    conn.close()

class AccountingApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("برنامج القيود اليومية - Accounting (Standalone)")
        self.geometry("900x600")
        self.create_widgets()
        init_db()
        self.load_entries()

    def create_widgets(self):
        frm = ttk.Frame(self, padding=10)
        frm.pack(fill=tk.BOTH, expand=True)

        # Entry form
        form = ttk.LabelFrame(frm, text="إدخال قيد جديد", padding=10)
        form.pack(fill=tk.X)

        ttk.Label(form, text="التاريخ (YYYY-MM-DD)").grid(row=0, column=0, sticky=tk.W, padx=5, pady=4)
        self.e_date = ttk.Entry(form); self.e_date.grid(row=0, column=1, sticky=tk.W, padx=5, pady=4)
        self.e_date.insert(0, datetime.now().strftime("%Y-%m-%d"))

        ttk.Label(form, text="الحساب المدين").grid(row=0, column=2, sticky=tk.W, padx=5, pady=4)
        self.e_debit = ttk.Entry(form); self.e_debit.grid(row=0, column=3, sticky=tk.W, padx=5, pady=4)

        ttk.Label(form, text="الحساب الدائن").grid(row=1, column=0, sticky=tk.W, padx=5, pady=4)
        self.e_credit = ttk.Entry(form); self.e_credit.grid(row=1, column=1, sticky=tk.W, padx=5, pady=4)

        ttk.Label(form, text="المبلغ").grid(row=1, column=2, sticky=tk.W, padx=5, pady=4)
        self.e_amount = ttk.Entry(form); self.e_amount.grid(row=1, column=3, sticky=tk.W, padx=5, pady=4)

        ttk.Label(form, text="البيان").grid(row=2, column=0, sticky=tk.W, padx=5, pady=4)
        self.e_desc = ttk.Entry(form, width=60); self.e_desc.grid(row=2, column=1, columnspan=3, sticky=tk.W, padx=5, pady=4)

        btn_frame = ttk.Frame(form)
        btn_frame.grid(row=3, column=0, columnspan=4, pady=8)
        ttk.Button(btn_frame, text="حفظ القيد", command=self.save_entry).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="تفريغ الحقول", command=self.clear_form).pack(side=tk.LEFT, padx=5)

        # Search & actions
        actions = ttk.Frame(frm, padding=(0,10))
        actions.pack(fill=tk.X)
        ttk.Label(actions, text="بحث:").pack(side=tk.LEFT, padx=5)
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *a: self.load_entries())
        ttk.Entry(actions, textvariable=self.search_var, width=30).pack(side=tk.LEFT, padx=5)
        ttk.Button(actions, text="تصدير CSV", command=self.export_csv).pack(side=tk.RIGHT, padx=5)
        ttk.Button(actions, text="طباعة ميزان المراجعة", command=self.show_trial_balance).pack(side=tk.RIGHT, padx=5)

        # Treeview for journal entries
        cols = ("id","date","debit","credit","amount","description")
        self.tree = ttk.Treeview(frm, columns=cols, show="headings", selectmode="browse")
        self.tree.heading("id", text="ID")
        self.tree.column("id", width=50, anchor=tk.CENTER)
        self.tree.heading("date", text="التاريخ")
        self.tree.column("date", width=100)
        self.tree.heading("debit", text="مدين")
        self.tree.column("debit", width=150)
        self.tree.heading("credit", text="دائن")
        self.tree.column("credit", width=150)
        self.tree.heading("amount", text="المبلغ")
        self.tree.column("amount", width=100, anchor=tk.E)
        self.tree.heading("description", text="البيان")
        self.tree.column("description", width=300)

        self.tree.pack(fill=tk.BOTH, expand=True)
        self.tree.bind("<Double-1>", self.on_edit)

        # Right-click menu
        self.menu = tk.Menu(self, tearoff=0)
        self.menu.add_command(label="حذف القيد", command=self.delete_selected)
        self.menu.add_command(label="تعديل القيد", command=self.edit_selected)
        self.tree.bind("<Button-3>", self.show_menu)

    def show_menu(self, event):
        try:
            self.tree.selection_set(self.tree.identify_row(event.y))
            self.menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.menu.grab_release()

    def save_entry(self):
        date = self.e_date.get().strip()
        debit = self.e_debit.get().strip()
        credit = self.e_credit.get().strip()
        amount = self.e_amount.get().strip()
        desc = self.e_desc.get().strip()

        if not (date and debit and credit and amount):
            messagebox.showerror("خطأ", "التاريخ، الحساب المدين، الحساب الدائن، والمبلغ مطلوبة")
            return
        try:
            amount_val = float(amount)
        except ValueError:
            messagebox.showerror("خطأ", "المبلغ يجب أن يكون رقمًا")
            return

        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("INSERT INTO journal (date, debit, credit, amount, description) VALUES (?,?,?,?,?)",
                  (date, debit, credit, amount_val, desc))
        conn.commit()
        conn.close()
        messagebox.showinfo("تم", "تم حفظ القيد بنجاح")
        self.clear_form()
        self.load_entries()

    def clear_form(self):
        self.e_debit.delete(0, tk.END)
        self.e_credit.delete(0, tk.END)
        self.e_amount.delete(0, tk.END)
        self.e_desc.delete(0, tk.END)

    def load_entries(self):
        for r in self.tree.get_children():
            self.tree.delete(r)
        q = self.search_var.get().strip()
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        if q:
            like = f"%{q}%"
            c.execute("SELECT id,date,debit,credit,amount,description FROM journal WHERE date LIKE ? OR debit LIKE ? OR credit LIKE ? OR description LIKE ? ORDER BY date, id",
                      (like, like, like, like))
        else:
            c.execute("SELECT id,date,debit,credit,amount,description FROM journal ORDER BY date, id")
        rows = c.fetchall()
        conn.close()
        for row in rows:
            self.tree.insert("", tk.END, values=row)

    def on_edit(self, event):
        item = self.tree.selection()
        if not item:
            return
        self.edit_selected()

    def edit_selected(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("تنبيه", "اختر قيدًا للتعديل")
            return
        item = self.tree.item(sel[0])["values"]
        EditDialog(self, item, self.load_entries)

    def delete_selected(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("تنبيه", "اختر قيدًا للحذف")
            return
        item = self.tree.item(sel[0])["values"]
        ans = messagebox.askyesno("تأكيد الحذف", f"هل تريد حذف القيد رقم {item[0]}؟")
        if not ans:
            return
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("DELETE FROM journal WHERE id=?", (item[0],))
        conn.commit()
        conn.close()
        self.load_entries()

    def export_csv(self):
        path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files","*.csv")], title="حفظ كـ CSV")
        if not path:
            return
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("SELECT id,date,debit,credit,amount,description FROM journal ORDER BY date, id")
        rows = c.fetchall()
        conn.close()
        with open(path, "w", newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["ID","Date","Debit","Credit","Amount","Description"])
            for r in rows:
                writer.writerow(r)
        messagebox.showinfo("تم", f"تم التصدير إلى {path}")

    def show_trial_balance(self):
        # Simple trial balance: sum debits and credits by account name (assuming debit/credit fields contain account names)
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("SELECT debit, credit, amount FROM journal")
        rows = c.fetchall()
        conn.close()
        tb = {}
        for debit, credit, amount in rows:
            tb[debit] = tb.get(debit, 0) + amount
            tb[credit] = tb.get(credit, 0) - amount
        # show in a new window
        win = tk.Toplevel(self)
        win.title("ميزان المراجعة")
        cols = ("account","balance")
        tree = ttk.Treeview(win, columns=cols, show="headings")
        tree.heading("account", text="الحساب")
        tree.heading("balance", text="الرصيد")
        tree.column("balance", anchor=tk.E, width=150)
        tree.pack(fill=tk.BOTH, expand=True)
        total_dr = 0
        total_cr = 0
        for acc, bal in sorted(tb.items()):
            tree.insert("", tk.END, values=(acc, "{:.2f}".format(bal)))
            if bal > 0:
                total_dr += bal
            else:
                total_cr += -bal
        ttk.Label(win, text=f"إجمالي مدين: {total_dr:.2f}    إجمالي دائن: {total_cr:.2f}").pack(pady=6)

class EditDialog(tk.Toplevel):
    def __init__(self, parent, item_values, refresh_callback):
        super().__init__(parent)
        self.title("تعديل قيد")
        self.item_values = item_values
        self.refresh_callback = refresh_callback
        self.create_widgets()
        self.load_values()

    def create_widgets(self):
        self.geometry("600x220")
        frm = ttk.Frame(self, padding=10)
        frm.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frm, text="التاريخ (YYYY-MM-DD)").grid(row=0, column=0, sticky=tk.W, padx=5, pady=4)
        self.e_date = ttk.Entry(frm); self.e_date.grid(row=0, column=1, sticky=tk.W, padx=5, pady=4)

        ttk.Label(frm, text="الحساب المدين").grid(row=1, column=0, sticky=tk.W, padx=5, pady=4)
        self.e_debit = ttk.Entry(frm); self.e_debit.grid(row=1, column=1, sticky=tk.W, padx=5, pady=4)

        ttk.Label(frm, text="الحساب الدائن").grid(row=2, column=0, sticky=tk.W, padx=5, pady=4)
        self.e_credit = ttk.Entry(frm); self.e_credit.grid(row=2, column=1, sticky=tk.W, padx=5, pady=4)

        ttk.Label(frm, text="المبلغ").grid(row=3, column=0, sticky=tk.W, padx=5, pady=4)
        self.e_amount = ttk.Entry(frm); self.e_amount.grid(row=3, column=1, sticky=tk.W, padx=5, pady=4)

        ttk.Label(frm, text="البيان").grid(row=4, column=0, sticky=tk.W, padx=5, pady=4)
        self.e_desc = ttk.Entry(frm, width=50); self.e_desc.grid(row=4, column=1, sticky=tk.W, padx=5, pady=4)

        btns = ttk.Frame(frm)
        btns.grid(row=5, column=0, columnspan=2, pady=8)
        ttk.Button(btns, text="حفظ التعديلات", command=self.save).pack(side=tk.LEFT, padx=5)
        ttk.Button(btns, text="إلغاء", command=self.destroy).pack(side=tk.LEFT, padx=5)

    def load_values(self):
        _, date, debit, credit, amount, desc = self.item_values
        self.e_date.insert(0, date)
        self.e_debit.insert(0, debit)
        self.e_credit.insert(0, credit)
        self.e_amount.insert(0, str(amount))
        self.e_desc.insert(0, desc)

    def save(self):
        try:
            id_ = int(self.item_values[0])
        except:
            messagebox.showerror("خطأ", "قيمة ID غير صحيحة")
            return
        date = self.e_date.get().strip()
        debit = self.e_debit.get().strip()
        credit = self.e_credit.get().strip()
        amount = self.e_amount.get().strip()
        desc = self.e_desc.get().strip()
        if not (date and debit and credit and amount):
            messagebox.showerror("خطأ", "التاريخ، الحساب المدين، الحساب الدائن، والمبلغ مطلوبة")
            return
        try:
            amount_val = float(amount)
        except ValueError:
            messagebox.showerror("خطأ", "المبلغ يجب أن يكون رقمًا")
            return
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("UPDATE journal SET date=?, debit=?, credit=?, amount=?, description=? WHERE id=?",
                  (date, debit, credit, amount_val, desc, id_))
        conn.commit()
        conn.close()
        messagebox.showinfo("تم", "تم تحديث القيد")
        self.refresh_callback()
        self.destroy()

if __name__ == "__main__":
    init_db()
    app = AccountingApp()
    app.mainloop()
