import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import datetime

class Customer:
    def __init__(self, name, hourly_rate):
        self.name = name
        self.hourly_rate = hourly_rate
        self.actual_start_time = None
        self.total_cost = 0.0

    def start(self, time_str=None):
        if time_str:
            try:
                t = datetime.datetime.strptime(time_str, "%H:%M").time()
                today = datetime.date.today()
                self.actual_start_time = datetime.datetime.combine(today, t)
            except ValueError:
                messagebox.showwarning("فرمت اشتباه", "فرمت زمان باید HH:MM باشد\nاز زمان فعلی استفاده می‌شود.")
                self.actual_start_time = datetime.datetime.now()
        else:
            self.actual_start_time = datetime.datetime.now()

    def end(self, extra_cost=0.0):
        if not self.actual_start_time:
            return None, None
        end_time = datetime.datetime.now()
        hours = (end_time - self.actual_start_time).total_seconds() / 3600
        hours = max(hours, 0)
        total = round(hours * self.hourly_rate + extra_cost, 2)
        self.total_cost = total
        return hours, total

class GameClubApp:
    def __init__(self, root):
        self.root = root
        root.title("🎮 گیم کلاب والهالا")
        root.geometry("820x660")
        root.configure(bg="#1a1a1a")

        self.fnt_title   = ("Tahoma", 24, "bold")
        self.fnt_label   = ("Tahoma", 14)
        self.fnt_button  = ("Tahoma", 13, "bold")
        self.fnt_tree    = ("Tahoma", 12)

        self.customers = {}
        self._setup_styles()
        self._build_title()
        self._build_customer_list()
        self._build_session_controls()
        self._build_result_box()

    def _setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview",
                        background="#222",
                        foreground="white",
                        fieldbackground="#222",
                        rowheight=30,
                        font=self.fnt_tree)
        style.configure("Treeview.Heading",
                        background="#333",
                        foreground="cyan",
                        font=self.fnt_label)
        style.map("Treeview",
                  background=[("selected", "#006666")],
                  foreground=[("selected", "white")])
        style.configure("TButton",
                        background="#005f5f",
                        foreground="white",
                        font=self.fnt_button,
                        relief="flat",
                        padding=8)
        style.map("TButton", background=[("active", "#008f8f")])

    def _build_title(self):
        tk.Label(self.root, text="🏆 گیم کلاب والهالا 🏆", font=self.fnt_title,
                 fg="cyan", bg="#1a1a1a").pack(pady=10)

    def _build_customer_list(self):
        frm = tk.Frame(self.root, bg="#1a1a1a")
        frm.pack(padx=20, pady=10, fill="both", expand=False)

        top = tk.Frame(frm, bg="#1a1a1a")
        top.pack(fill="x", pady=5)

        tk.Label(top, text="نام مشتری:", font=self.fnt_label, fg="white", bg="#1a1a1a").pack(side="left", padx=5)
        self.add_name = tk.Entry(top, font=self.fnt_label, width=18)
        self.add_name.pack(side="left", padx=5)

        tk.Label(top, text="نرخ ساعتی:", font=self.fnt_label, fg="white", bg="#1a1a1a").pack(side="left", padx=5)
        self.add_rate = tk.Entry(top, font=self.fnt_label, width=10)
        self.add_rate.pack(side="left", padx=5)

        ttk.Button(top, text="➕ افزودن", command=self.add_customer).pack(side="left", padx=10)

        cols = ("name", "rate", "status", "start")
        self.tree = ttk.Treeview(frm, columns=cols, show="headings", height=8)
        for col, text, width in zip(cols,
                                    ("نام مشتری", "نرخ (تومان/ساعت)", "وضعیت", "زمان شروع"),
                                    (180, 160, 100, 140)):
            self.tree.heading(col, text=text)
            self.tree.column(col, width=width, anchor="center")
        self.tree.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(frm, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

    def add_customer(self):
        name = self.add_name.get().strip()
        rate_str = self.add_rate.get().strip()
        if not name or not rate_str:
            messagebox.showerror("خطا", "نام و نرخ ساعتی الزامی هستند.")
            return
        try:
            rate = float(rate_str)
        except ValueError:
            messagebox.showerror("خطا", "نرخ ساعتی باید عدد باشد.")
            return
        if name in self.customers:
            messagebox.showwarning("هشدار", "این مشتری قبلاً افزوده شده.")
            return

        self.customers[name] = Customer(name, rate)
        self.tree.insert("", "end", iid=name,
                         values=(name, f"{rate:,.0f}", "❌ غیرفعال", "--:--"))
        self.add_name.delete(0, tk.END)
        self.add_rate.delete(0, tk.END)

    def _build_session_controls(self):
        frm = tk.LabelFrame(self.root, text="کنترل جلسه",
                            font=self.fnt_label, fg="white", bg="#1a1a1a",
                            padx=10, pady=10)
        frm.pack(padx=20, pady=10, fill="x")

        tk.Label(frm, text="زمان شروع (HH:MM):", font=self.fnt_label,
                 fg="white", bg="#1a1a1a").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.start_time_entry = tk.Entry(frm, font=self.fnt_label, width=12)
        self.start_time_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Button(frm, text="▶ شروع", command=self.start_session).grid(row=0, column=2, padx=15)
        ttk.Button(frm, text="■ پایان", command=self.end_session).grid(row=0, column=3, padx=15)

    def start_session(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("هشدار", "ابتدا یک مشتری را انتخاب کنید.")
            return
        name = sel[0]
        cust = self.customers[name]
        tstr = self.start_time_entry.get().strip() or None
        cust.start(tstr)
        tm = cust.actual_start_time.strftime("%H:%M")
        self.tree.set(name, "status", "✅ فعال")
        self.tree.set(name, "start", tm)
        self.start_time_entry.delete(0, tk.END)

    def _build_result_box(self):
        self.result_label = tk.Label(self.root, text="", font=self.fnt_button,
                                     fg="#00ff00", bg="#1a1a1a", justify="center")
        self.result_label.pack(pady=20)

    def end_session(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("هشدار", "ابتدا یک مشتری را انتخاب کنید.")
            return
        name = sel[0]
        cust = self.customers[name]

        # دو بار پرسش هزینه کالا
        total_extra = 0.0
        for i in range(1, 3):
            val = simpledialog.askfloat(f"هزینه کالا {i}",
                                        f"مبلغ هزینه کالا {i} را وارد کنید:",
                                        minvalue=0.0) or 0.0
            total_extra += val

        hours, total = cust.end(total_extra)
        if hours is None:
            messagebox.showwarning("هشدار", "ابتدا جلسه را شروع کنید.")
            return

        self.result_label.config(
            text=(f"{cust.name}\n"
                  f"⌛ مدت: {hours:.2f} ساعت\n"
                  f"➕ جمع هزینه کالاها: {total_extra:,.0f} تومان\n"
                  f"💸 هزینه کل: {total:,.0f} تومان")
        )
        self.tree.set(name, "status", "❌ غیرفعال")
        self.tree.set(name, "start", "--:--")
        cust.actual_start_time = None

if __name__ == "__main__":
    root = tk.Tk()
    app = GameClubApp(root)
    root.mainloop()
