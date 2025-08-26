
import re
from datetime import datetime, timedelta
import tkinter as tk
from tkinter import ttk, messagebox

APP_TITLE = "حاسبة الثلث الأخير من الليل"
APP_WIDTH = 540
APP_HEIGHT = 480

TIME_RE = re.compile(r"^(?:[01]\d|2[0-3]):[0-5]\d$")

def parse_time(s: str) -> datetime:
    try:
        if not TIME_RE.match(s):
            raise ValueError("صيغة الوقت يجب أن تكون HH:MM بنظام 24 ساعة.")
        return datetime.strptime(s, "%H:%M")
    except Exception as e:
        raise ValueError(str(e))

def compute_last_third(maghrib_s: str, fajr_s: str):
    maghrib = parse_time(maghrib_s)
    fajr = parse_time(fajr_s)
    if fajr <= maghrib:
        fajr += timedelta(days=1)
    night_duration = fajr - maghrib
    third = night_duration / 3
    start_last = fajr - third
    start_second = fajr - (third * 2)
    start_first = maghrib
    return {
        "maghrib": maghrib,
        "fajr": fajr,
        "night_duration": night_duration,
        "third": third,
        "first_start": start_first,
        "second_start": start_second,
        "last_start": start_last,
    }

def fmt_time(dt: datetime) -> str:
    return dt.strftime("%H:%M")

def fmt_duration(td: timedelta) -> str:
    total_minutes = int(td.total_seconds() // 60)
    hours, minutes = divmod(total_minutes, 60)
    return f"{hours} ساعة و {minutes} دقيقة"

class App(ttk.Frame):
    def __init__(self, master):
        super().__init__(master, padding=16)
        self.master.title(APP_TITLE)
        self.master.minsize(APP_WIDTH, APP_HEIGHT)
        self.create_style()
        self.create_widgets()
        self.grid(sticky="nsew")
        self.master.grid_columnconfigure(0, weight=1)
        self.master.grid_rowconfigure(0, weight=1)

    def create_style(self):
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        style.configure("TFrame", background="#0f172a")
        style.configure("Header.TLabel", font=("Tajawal", 16, "bold"), foreground="#e2e8f0", background="#0f172a")
        style.configure("TLabel", font=("Tajawal", 11), foreground="#e2e8f0", background="#0f172a")
        style.configure("TEntry", font=("Tajawal", 12))
        style.configure("TButton", font=("Tajawal", 12, "bold"), padding=8)
        style.configure("Card.TFrame", background="#111827", relief="flat")
        style.configure("Help.TLabel", foreground="#94a3b8", background="#0f172a", font=("Tajawal", 10))

        # Buttons colors
        style.map("Primary.TButton",
                  background=[("!disabled", "#2563eb"), ("pressed", "#1e40af"), ("active", "#1d4ed8")],
                  foreground=[("!disabled", "#ffffff")])
        style.map("Ghost.TButton",
                  background=[("!disabled", "#1f2937"), ("pressed", "#111827"), ("active", "#111827")],
                  foreground=[("!disabled", "#e5e7eb")])

    def create_widgets(self):
        header = ttk.Label(self, text="حاسبة الثلث الأخير من الليل", style="Header.TLabel")
        header.grid(row=0, column=0, sticky="w")

        help_lbl = ttk.Label(self, text="أدخل وقتي المغرب والفجر بصيغة 24 ساعة (HH:MM).", style="Help.TLabel")
        help_lbl.grid(row=1, column=0, sticky="w", pady=(2, 12))

        card = ttk.Frame(self, style="Card.TFrame", padding=16)
        card.grid(row=2, column=0, sticky="nsew")
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)

        form = ttk.Frame(card, style="Card.TFrame")
        form.grid(row=0, column=0, sticky="ew", pady=(0, 8))
        form.grid_columnconfigure(1, weight=1)

        ttk.Label(form, text="وقت المغرب:", style="TLabel").grid(row=0, column=0, sticky="w", pady=4, padx=(0,8))
        self.maghrib_var = tk.StringVar(value="18:43")
        self.maghrib_entry = ttk.Entry(form, textvariable=self.maghrib_var, width=12, justify="center")
        self.maghrib_entry.grid(row=0, column=1, sticky="w")

        ttk.Label(form, text="وقت الفجر:", style="TLabel").grid(row=1, column=0, sticky="w", pady=4, padx=(0,8))
        self.fajr_var = tk.StringVar(value="04:00")
        self.fajr_entry = ttk.Entry(form, textvariable=self.fajr_var, width=12, justify="center")
        self.fajr_entry.grid(row=1, column=1, sticky="w")

        btns = ttk.Frame(card, style="Card.TFrame")
        btns.grid(row=1, column=0, sticky="ew", pady=(8, 12))
        for i in range(3):
            btns.grid_columnconfigure(i, weight=1)

        calc_btn = ttk.Button(btns, text="حساب", style="Primary.TButton", command=self.on_calculate)
        calc_btn.grid(row=0, column=0, padx=4, sticky="ew")

        copy_btn = ttk.Button(btns, text="نسخ النتائج", style="Ghost.TButton", command=self.copy_results)
        copy_btn.grid(row=0, column=1, padx=4, sticky="ew")

        reset_btn = ttk.Button(btns, text="إعادة تعيين", style="Ghost.TButton", command=self.reset_form)
        reset_btn.grid(row=0, column=2, padx=4, sticky="ew")

        self.result_frame = ttk.Frame(card, style="Card.TFrame")
        self.result_frame.grid(row=2, column=0, sticky="nsew")
        card.grid_rowconfigure(2, weight=1)

        self.result_text = tk.Text(self.result_frame, height=10, wrap="word", bd=0, highlightthickness=0, padx=8, pady=8)
        self.result_text.configure(bg="#0b1220", fg="#e5e7eb", insertbackground="#e5e7eb", font=("Tajawal", 12))
        self.result_text.grid(row=0, column=0, sticky="nsew")
        self.result_frame.grid_columnconfigure(0, weight=1)
        self.result_frame.grid_rowconfigure(0, weight=1)

        self.status_var = tk.StringVar(value="")
        status = ttk.Label(self, textvariable=self.status_var, style="Help.TLabel")
        status.grid(row=3, column=0, sticky="w", pady=(8, 0))

        # Keyboard shortcuts
        self.master.bind("<Return>", lambda e: self.on_calculate())
        self.master.bind("<Control-c>", lambda e: self.copy_results())
        self.master.bind("<Escape>", lambda e: self.reset_form())

        # First calculation
        self.on_calculate()

    def on_calculate(self):
        try:
            res = compute_last_third(self.maghrib_var.get().strip(), self.fajr_var.get().strip())
            lines = []
            lines.append("—"*40)
            lines.append(f"وقت المغرب: {fmt_time(res['maghrib'])}")
            lines.append(f"وقت الفجر : {fmt_time(res['fajr'])}")
            lines.append(f"مدة الليل: {fmt_duration(res['night_duration'])}")
            lines.append(f"طول الثلث الواحد: {fmt_duration(res['third'])}")
            lines.append("—"*40)
            lines.append(f"بداية الثلث الأول  : {fmt_time(res['first_start'])}")
            lines.append(f"بداية الثلث الثاني : {fmt_time(res['second_start'])}")
            lines.append(f"بداية الثلث الأخير : {fmt_time(res['last_start'])}")
            lines.append(f"نهاية الثلث الأخير : {fmt_time(res['fajr'])}")
            lines.append("—"*40)

            # هل نحن الآن داخل الثلث الأخير؟
            now = datetime.now()
            now_time = now
            # مواءمة اليوم الحالي مع الليلة المحسوبة
            m = res['maghrib']
            f = res['fajr']
            last_start = res['last_start']
            if not (m <= now_time <= f):
                # إذا الوقت الحالي خارج مدى الليلة، نبدّل التاريخ المرجعي لكي يظهر الحكم بشكل محايد
                now_time = last_start  # فقط لئلا يختل الشرط في حال عرض
            in_last_third = last_start <= now_time <= f

            lines.append(f"الآن في الثلث الأخير؟ {'نعم' if in_last_third else 'لا'}")
            text = "\n".join(lines)

            self.result_text.configure(state="normal")
            self.result_text.delete("1.0", "end")
            self.result_text.insert("1.0", text)
            self.result_text.configure(state="disabled")

            self.status_var.set("تم الحساب بنجاح ✅")
        except Exception as e:
            messagebox.showerror("خطأ في الإدخال", str(e))
            self.status_var.set("حدث خطأ ❌")

    def copy_results(self):
        text = self.result_text.get("1.0", "end").strip()
        if not text:
            return
        self.master.clipboard_clear()
        self.master.clipboard_append(text)
        self.status_var.set("تم نسخ النتائج إلى الحافظة 📋")

    def reset_form(self):
        self.maghrib_var.set("")
        self.fajr_var.set("")
        self.result_text.configure(state="normal")
        self.result_text.delete("1.0", "end")
        self.result_text.configure(state="disabled")
        self.status_var.set("تمت إعادة التعيين")
        
def main():
    root = tk.Tk()
    app = App(root)
    root.mainloop()

if __name__ == "__main__":
    main()
