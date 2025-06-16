import customtkinter as ctk
from tkinter import messagebox
from tkcalendar import DateEntry
from hijri_converter import convert
import datetime
import subprocess

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")

app = ctk.CTk()
app.title("برنامج الوقت والتاريخ")
app.geometry("500x500")
app.resizable(False, False)

# تحكم بالنوافذ المفتوحة
time_window_open = False
date_window_open = False

# تحديث الساعة
def update_clock():
    now = datetime.datetime.now()
    time_label.configure(text=now.strftime("%I:%M:%S %p"))
    date_label.configure(text="ميلادي: " + now.strftime("%Y-%m-%d"))
    hijri = convert.Gregorian(now.year, now.month, now.day).to_hijri()
    hijri_label.configure(text=f"هجري: {hijri.day} {hijri.month_name()} {hijri.year} هـ")
    app.after(1000, update_clock)

# نافذة تعديل الوقت
def open_time_editor():
    global time_window_open
    if time_window_open:
        return  # لا تفتح مرتين
    time_window_open = True

    x = app.winfo_x() + 520
    y = app.winfo_y() + 50
    win = ctk.CTkToplevel(app)
    win.geometry(f"350x320+{x}+{y}")
    win.title("تعديل الوقت")
    win.resizable(False, False)

    def on_close():
        global time_window_open
        time_window_open = False
        win.destroy()

    win.protocol("WM_DELETE_WINDOW", on_close)

    ctk.CTkLabel(win, text="حدد الوقت الجديد:", font=("Segoe UI", 16, "bold")).pack(pady=20)

    time_frame = ctk.CTkFrame(win)
    time_frame.pack(pady=10)

    hours = ctk.CTkComboBox(time_frame, values=[f"{i:02}" for i in range(1, 13)], width=70)
    hours.set("12")
    hours.grid(row=0, column=0, padx=5)

    minutes = ctk.CTkComboBox(time_frame, values=[f"{i:02}" for i in range(60)], width=70)
    minutes.set("00")
    minutes.grid(row=0, column=1, padx=5)

    seconds = ctk.CTkComboBox(time_frame, values=[f"{i:02}" for i in range(60)], width=70)
    seconds.set("00")
    seconds.grid(row=0, column=2, padx=5)

    period = ctk.CTkComboBox(win, values=["AM", "PM"], width=100)
    period.set("AM")
    period.pack(pady=10)

    def apply_time():
        try:
            t = f"{hours.get()}:{minutes.get()}:{seconds.get()} {period.get()}"
            subprocess.run(f"time {t}", shell=True, check=True)
            messagebox.showinfo("نجاح", "تم تغيير الوقت")
            update_clock()
        except:
            messagebox.showerror("خطأ", "فشل التغيير. شغل البرنامج كمسؤول")

    def reset_time():
        try:
            subprocess.run("w32tm /resync", shell=True, check=True)
            messagebox.showinfo("نجاح", "تمت مزامنة الوقت")
            update_clock()
        except:
            messagebox.showerror("خطأ", "فشل المزامنة")

    btns = ctk.CTkFrame(win, fg_color="transparent")
    btns.pack(pady=20)

    ctk.CTkButton(btns, text="تطبيق", command=apply_time, width=120).grid(row=0, column=0, padx=10)
    ctk.CTkButton(btns, text="مزامنة تلقائية", command=reset_time, width=120).grid(row=0, column=1, padx=10)

    close_btn = ctk.CTkButton(win, command=on_close, text="✖", width=40, fg_color="#d9534f", hover_color="#c9302c")
    close_btn.pack(pady=5)

# نافذة تعديل التاريخ
def open_date_editor():
    global date_window_open
    if date_window_open:
        return  # لا تفتح مرتين
    date_window_open = True

    x = app.winfo_x() + 520
    y = app.winfo_y() + 50
    win = ctk.CTkToplevel(app)
    win.geometry(f"300x250+{x}+{y}")
    win.title("تعديل التاريخ")
    win.resizable(False, False)

    def on_close():
        global date_window_open
        date_window_open = False
        win.destroy()

    win.protocol("WM_DELETE_WINDOW", on_close)

    ctk.CTkLabel(win, text="حدد التاريخ الجديد:", font=("Segoe UI", 16, "bold")).pack(pady=20)

    date_picker = DateEntry(win, date_pattern='yyyy-mm-dd', locale='ar_SA')
    date_picker.pack(pady=10)

    def apply_date():
        try:
            d = date_picker.get_date().strftime("%m-%d-%y")
            subprocess.run(f'date {d}', shell=True, check=True)
            messagebox.showinfo("نجاح", "تم تغيير التاريخ")
            update_clock()
        except:
            messagebox.showerror("خطأ", "فشل التغيير. شغل البرنامج كمسؤول")

    def reset_date():
        try:
            subprocess.run("w32tm /resync", shell=True, check=True)
            messagebox.showinfo("نجاح", "تمت مزامنة التاريخ")
            update_clock()
        except:
            messagebox.showerror("خطأ", "فشل المزامنة")

    btns = ctk.CTkFrame(win, fg_color="transparent")
    btns.pack(pady=20)

    ctk.CTkButton(btns, text="تطبيق", command=apply_date, width=120).grid(row=0, column=0, padx=10)
    ctk.CTkButton(btns, text="مزامنة تلقائية", command=reset_date, width=120).grid(row=0, column=1, padx=10)

    close_btn = ctk.CTkButton(win, command=on_close, text="✖", width=40, fg_color="#d9534f", hover_color="#c9302c")
    close_btn.pack(pady=5)

# الواجهة الرئيسية
main_frame = ctk.CTkFrame(app)
main_frame.pack(expand=True)

ctk.CTkLabel(main_frame, text="الساعة الآن", font=("Segoe UI", 28, "bold")).pack(pady=20)

time_label = ctk.CTkLabel(main_frame, text="", font=("Segoe UI", 48, "bold"))
time_label.pack(pady=10)

date_label = ctk.CTkLabel(main_frame, text="", font=("Segoe UI", 22))
date_label.pack(pady=5)

hijri_label = ctk.CTkLabel(main_frame, text="", font=("Segoe UI", 22))
hijri_label.pack(pady=5)

buttons_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
buttons_frame.pack(pady=30)

ctk.CTkButton(buttons_frame, text="⏰ تعديل الوقت", command=open_time_editor, width=220, height=45, corner_radius=10).grid(row=0, column=0, padx=15)
ctk.CTkButton(buttons_frame, text="📅 تعديل التاريخ", command=open_date_editor, width=220, height=45, corner_radius=10).grid(row=0, column=1, padx=15)

update_clock()
app.mainloop()
