import tkinter as tk
from tkinter import messagebox, filedialog
from tkinter import font as tkfont
from datetime import date
import os, sys, traceback, webbrowser

LOG_PATH = os.path.join(os.path.dirname(__file__) or os.getcwd(), "yt_premium_calc.log")

def log_exception(exc: BaseException):
    try:
        with open(LOG_PATH, "a", encoding="utf-8") as f:
            f.write("===== ERROR =====\n")
            traceback.print_exc(file=f)
            f.write("\n")
    except Exception:
        pass

try:
    import pyperclip
    _HAS_PYPERCLIP = True
except Exception:
    _HAS_PYPERCLIP = False

APP_TITLE = "YouTube Premium Discount Calculator"
DATE_HINT = "dd.mm.yy หรือ dd.mm.yyyy (รองรับ พ.ศ./ค.ศ.)"

# ------------------ Date Parsing (supports Thai BE and CE) ------------------ #
def parse_thai_friendly_date(s: str):
    from datetime import date as _date
    s = s.strip().replace("/", ".").replace("-", ".")
    try:
        d, m, y = s.split(".")
        d, m = int(d), int(m)
        if len(y) == 2:
            yy = int(y)
            year_be = 2500 + yy
            year_ce = year_be - 543
        else:
            year = int(y)
            year_ce = year - 543 if year >= 2200 else year
        return _date(year_ce, m, d)
    except Exception:
        raise ValueError("รูปแบบวันที่ไม่ถูกต้อง กรุณากรอกเป็น " + DATE_HINT)

# ------------------ Core Calculation ------------------ #
DAILY_DISCOUNT = 2
MONTH_PRICE = 129
YEAR_PRICE = 1249

def calc_days_left(today, expiry):
    delta = (expiry - today).days
    return max(delta, 0)

def format_baht(n: int) -> str:
    return f"{n:,}".replace(",", ",")

# Build final report text in Thai layout
def build_report(today_str: str, expiry_str: str, days_left: int) -> str:
    total_discount = DAILY_DISCOUNT * days_left

    # Monthly
    m_applied = min(MONTH_PRICE, total_discount)
    m_leftover = max(0, total_discount - MONTH_PRICE)
    m_to_pay = MONTH_PRICE - m_applied

    # Yearly
    y_applied = min(YEAR_PRICE, total_discount)
    y_leftover = max(0, total_discount - YEAR_PRICE)
    y_to_pay = YEAR_PRICE - y_applied

    lines = []
    lines.append(f"📅 วันนี้: {today_str}")
    lines.append(f"📆 วันหมดอายุ: {expiry_str}")
    lines.append(f"🧮 วันใช้งานคงเหลือ {days_left} วัน\n")

    lines.append("🔹สรุปราคาแพ็กเกจ Youtube Premium (ส่วนตัว) แบบบุคคล\n")

    # Monthly block
    lines.append("⭐รายเดือน")
    lines.append(f"ราคาปกติ: {format_baht(MONTH_PRICE)} บาท")
    lines.append(f"ส่วนลด: {DAILY_DISCOUNT} × {days_left} = {format_baht(total_discount)} บาท")
    lines.append(f"➡️ จ่าย {format_baht(m_to_pay)} บาท ✅")
    if m_leftover > 0:
        lines.append(f"(มีส่วนลดคงเหลือ {format_baht(m_leftover)} บาท ใช้ต่ออายุครั้งถัดไป)")
    lines.append("")

    # Yearly block
    lines.append("⭐รายปี")
    lines.append(f"ราคาปกติ: {format_baht(YEAR_PRICE)} บาท")
    lines.append(f"ส่วนลด: {DAILY_DISCOUNT} × {days_left} = {format_baht(total_discount)} บาท")
    lines.append(f"➡️ จ่าย {format_baht(y_to_pay)} บาท ✅")

    return "\n".join(lines)

# ------------------ UI ------------------ #
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)

        # ✅ เปิดให้ย่อ-ขยายได้ + ตั้งขนาดเริ่ม + กันย่อเล็กเกิน
        self.resizable(True, True)
        self.geometry("800x600")
        self.minsize(640, 520)

        # ✅ ฟอนต์กลางสำหรับทั้งแอป (ใช้ Tk default ที่พกพาได้)
        default = tkfont.nametofont("TkDefaultFont")
        self.base_font_default_size = default.cget("size") or 12
        self.base_font = tkfont.Font(**default.configure())
        self.base_font.configure(size=self.base_font_default_size)
        # ผูกเป็นฟอนต์ระบบเริ่มต้นเพื่อให้ทุก widget ใช้
        self.option_add("*Font", self.base_font)

        # เมนูช่วยเหลือ + ซูม
        menubar = tk.Menu(self)
        viewmenu = tk.Menu(menubar, tearoff=0)
        viewmenu.add_command(label="ขยายตัวหนังสือ (A+)", command=lambda: self.change_font_size(+2))
        viewmenu.add_command(label="ย่อตัวหนังสือ (A-)", command=lambda: self.change_font_size(-2))
        viewmenu.add_command(label="รีเซ็ตขนาดตัวหนังสือ (Ctrl+0)", command=self.reset_font_size)
        menubar.add_cascade(label="มุมมอง", menu=viewmenu)

        helpmenu = tk.Menu(menubar, tearoff=0)
        helpmenu.add_command(label="เปิดไฟล์บันทึกข้อผิดพลาด", command=self.open_log)
        menubar.add_cascade(label="ช่วยเหลือ", menu=helpmenu)
        self.config(menu=menubar)

        # ใช้ grid layout ทั้งหน้าต่าง
        self.grid_columnconfigure(0, weight=1, uniform="cols")
        self.grid_columnconfigure(1, weight=1, uniform="cols")
        # แถวข้อความผลลัพธ์จะขยายแนวตั้ง
        self.grid_rowconfigure(4, weight=1)

        # --- Today input ---
        tk.Label(self, text="วันนี้ (เว้นว่าง = วันนี้อัตโนมัติ)").grid(row=0, column=0, sticky="w", padx=16, pady=(12,0))
        self.ent_today = tk.Entry(self)
        self.ent_today.grid(row=1, column=0, sticky="we", padx=16)
        tk.Label(self, text=DATE_HINT, fg="#666").grid(row=2, column=0, sticky="w", padx=16)

        # --- Expiry input ---
        tk.Label(self, text="วันหมดอายุ (จำเป็น)").grid(row=0, column=1, sticky="w", padx=16, pady=(12,0))
        self.ent_expiry = tk.Entry(self)
        self.ent_expiry.grid(row=1, column=1, sticky="we", padx=16)
                # --- Copy/Paste/Select-All bindings for date entries ---
        for ent in (self.ent_today, self.ent_expiry):
            ent.bind("<Control-a>", lambda e: (e.widget.select_range(0, "end"), "break")[-1])
            ent.bind("<Control-c>", lambda e: (e.widget.event_generate("<<Copy>>"), "break")[-1])
            ent.bind("<Control-x>", lambda e: (e.widget.event_generate("<<Cut>>"), "break")[-1])
            ent.bind("<Control-v>", lambda e: (e.widget.event_generate("<<Paste>>"), "break")[-1])

        tk.Label(self, text=DATE_HINT, fg="#666").grid(row=2, column=1, sticky="w", padx=16)

        # --- Buttons / Toolbar ---
        toolbar = tk.Frame(self)
        toolbar.grid(row=3, column=0, columnspan=2, sticky="we", padx=16, pady=8)
        for i in range(7):
            toolbar.grid_columnconfigure(i, weight=1)

        tk.Button(toolbar, text="คำนวณ (Enter)", command=self.calculate).grid(row=0, column=0, sticky="we", padx=4)
        tk.Button(toolbar, text="คัดลอกผลลัพธ์", command=self.copy_output).grid(row=0, column=1, sticky="we", padx=4)
        tk.Button(toolbar, text="บันทึกเป็นไฟล์ .txt", command=self.save_output).grid(row=0, column=2, sticky="we", padx=4)
        tk.Button(toolbar, text="ล้างค่า", command=self.clear_all).grid(row=0, column=3, sticky="we", padx=4)

        # 🔎 Font Zoom controls
        tk.Button(toolbar, text="A-", command=lambda: self.change_font_size(-2)).grid(row=0, column=4, sticky="we", padx=4)
        tk.Button(toolbar, text="A+", command=lambda: self.change_font_size(+2)).grid(row=0, column=5, sticky="we", padx=4)
        tk.Button(toolbar, text="รีเซ็ตฟอนต์", command=self.reset_font_size).grid(row=0, column=6, sticky="we", padx=4)

        # --- Output (ขยายเต็มพื้นที่ที่เหลือ) ---
        self.txt = tk.Text(self, wrap="word")
        self.txt.grid(row=4, column=0, columnspan=2, sticky="nsew", padx=16, pady=(0,16))

        # Keyboard shortcuts
        self.bind('<Return>', lambda e: self.calculate())
        # Zoom shortcuts: Ctrl + '+', Ctrl + '-', Ctrl + '0'
        self.bind("<Control-plus>", lambda e: self.change_font_size(+2))
        self.bind("<Control-minus>", lambda e: self.change_font_size(-2))
        self.bind("<Control-equal>", lambda e: self.change_font_size(+2))  # '=' without Shift often used for '+'
        self.bind("<Control-0>", lambda e: self.reset_font_size())
        # Mouse wheel zoom (Windows). Wrap in try/except to avoid platform issues.
        try:
            self.bind("<Control-MouseWheel>", self._on_ctrl_wheel)
        except Exception:
            pass

        # Pre-fill today (Thai style dd.mm.yy in BE)
        today = date.today()
        be_year_2d = (today.year + 543) % 100
        self.ent_today.insert(0, f"{today.day:02d}.{today.month:02d}.{be_year_2d:02d}")

    # ------------------ Helpers ------------------ #
    def open_log(self):
        try:
            if os.path.exists(LOG_PATH):
                webbrowser.open(f"file://{LOG_PATH}")
            else:
                messagebox.showinfo("Log", "ยังไม่มีไฟล์บันทึกข้อผิดพลาด")
        except Exception:
            pass

    # ------------------ Font Zoom ------------------ #
    def change_font_size(self, delta: int):
        try:
            new_size = max(8, int(self.base_font['size']) + int(delta))
        except Exception:
            new_size = max(8, self.base_font_default_size + int(delta))
        self.base_font.configure(size=new_size)

    def reset_font_size(self):
        self.base_font.configure(size=self.base_font_default_size)

    def _on_ctrl_wheel(self, event):
        step = +2 if getattr(event, "delta", 0) > 0 else -2
        self.change_font_size(step)

    
    # ------------------ Clipboard Helpers ------------------ #
    def copy_selection(self, widget):
        try:
            sel = widget.selection_get()
            self.clipboard_clear()
            self.clipboard_append(sel)
        except Exception:
            pass

    def cut_selection(self, widget):
        try:
            sel = widget.selection_get()
            self.clipboard_clear()
            self.clipboard_append(sel)
            widget.delete("sel.first", "sel.last")
        except Exception:
            pass

    def paste_clipboard(self, widget):
        try:
            data = self.clipboard_get()
            widget.insert("insert", data)
        except Exception:
            pass

# ------------------ Actions ------------------ #
    def calculate(self):
        try:
            from datetime import date as _date
            today_text = self.ent_today.get().strip()
            expiry_text = self.ent_expiry.get().strip()
            if not expiry_text:
                raise ValueError("กรุณากรอกวันหมดอายุ")

            if today_text:
                today_d = parse_thai_friendly_date(today_text)
                today_out = today_text
            else:
                today_d = _date.today()
                today_out = f"{today_d.day:02d}.{today_d.month:02d}.{(today_d.year + 543) % 100:02d}"

            expiry_d = parse_thai_friendly_date(expiry_text)
            expiry_out = expiry_text

            days_left = calc_days_left(today_d, expiry_d)
            report = build_report(today_out, expiry_out, days_left)

            self.txt.delete("1.0", tk.END)
            self.txt.insert("1.0", report)
        except Exception as e:
            log_exception(e)
            messagebox.showerror("Error", str(e))

    def copy_output(self):
        data = self.txt.get("1.0", tk.END).strip()
        if not data:
            messagebox.showwarning("Warning", "ยังไม่มีผลลัพธ์ให้คัดลอก")
            return
        try:
            if _HAS_PYPERCLIP:
                pyperclip.copy(data)
                messagebox.showinfo("Copied", "คัดลอกผลลัพธ์แล้ว")
            else:
                self.clipboard_clear()
                self.clipboard_append(data)
                messagebox.showinfo("Copied", "คัดลอกผลลัพธ์แล้ว (clipboard fallback)")
        except Exception as e:
            log_exception(e)
            try:
                self.clipboard_clear()
                self.clipboard_append(data)
                messagebox.showinfo("Copied", "คัดลอกผลลัพธ์แล้ว (clipboard fallback)")
            except Exception:
                pass

    def save_output(self):
        data = self.txt.get("1.0", tk.END).strip()
        if not data:
            messagebox.showwarning("Warning", "ยังไม่มีผลลัพธ์ให้บันทึก")
            return
        try:
            fp = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")],
                title="บันทึกผลลัพธ์เป็นไฟล์"
            )
            if fp:
                with open(fp, "w", encoding="utf-8") as f:
                    f.write(data)
                messagebox.showinfo("Saved", "บันทึกไฟล์เรียบร้อยแล้ว")
        except Exception as e:
            log_exception(e)
            messagebox.showerror("Error", str(e))

    def clear_all(self):
        self.ent_expiry.delete(0, tk.END)
        self.txt.delete("1.0", tk.END)


def main():
    try:
        app = App()
        app.mainloop()
    except Exception as e:
        # Log & show a friendly message so the window doesn't just close
        log_exception(e)
        try:
            messagebox.showerror("Fatal Error", f"โปรแกรมเกิดข้อผิดพลาดและต้องปิดตัวลง\\n\\n{e}\\n\\nLog: {LOG_PATH}")
        except Exception:
            pass

if __name__ == "__main__":
    # ทำ DPI awareness เฉพาะบน Windows และไม่ทำให้ล้มถ้าเรียกใช้ไม่ได้
    try:
        import ctypes, sys as _sys
        if _sys.platform.startswith("win"):
            try:
                ctypes.windll.shcore.SetProcessDpiAwareness(1)
            except Exception:
                pass
    except Exception:
        pass
    main()
