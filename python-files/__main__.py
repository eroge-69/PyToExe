import tkinter as tk
from tkinter import messagebox
import json
import os

SAVE_FOLDER = "New folder"
if not os.path.exists(SAVE_FOLDER):
    os.makedirs(SAVE_FOLDER)

SAVE_FILE = os.path.join(SAVE_FOLDER, "savefile.json")


class PC_Timer:
    def __init__(self, parent, name, saved_time=0):
        self.name = name
        self.time_left = saved_time
        self.running = False

        # إنشاء الإطار لكل عداد
        self.frame = tk.Frame(parent, relief=tk.GROOVE, borderwidth=1, padx=10, pady=5)
        self.frame.pack(fill=tk.X, padx=5, pady=3)

        # اسم الجهاز
        self.label_name = tk.Label(
            self.frame, text=self.name, font=("Arial", 12, "bold"), width=9, anchor="w"
        )
        self.label_name.grid(row=0, column=0, rowspan=2, sticky="w")

        # عناوين الحقول (ساعات - دقائق - ثواني)
        tk.Label(self.frame, text="ساعات", font=("Arial", 9)).grid(row=0, column=1)
        tk.Label(self.frame, text="دقائق", font=("Arial", 9)).grid(row=0, column=2)
        tk.Label(self.frame, text="ثواني", font=("Arial", 9)).grid(row=0, column=3)

        # مدخلات الساعات والدقائق والثواني
        self.hours_entry = tk.Entry(self.frame, width=3, font=("Arial", 10), justify="center")
        self.hours_entry.grid(row=1, column=1, padx=5)
        self.minutes_entry = tk.Entry(self.frame, width=3, font=("Arial", 10), justify="center")
        self.minutes_entry.grid(row=1, column=2, padx=5)
        self.seconds_entry = tk.Entry(self.frame, width=3, font=("Arial", 10), justify="center")
        self.seconds_entry.grid(row=1, column=3, padx=5)

        # القيم الافتراضية للمدخلات
        self.hours_entry.insert(0, "0")
        self.minutes_entry.insert(0, "0")
        self.seconds_entry.insert(0, "0")

        # عرض الوقت بشكل كبير
        self.label_time = tk.Label(
            self.frame, text="00:00:00", font=("Arial", 16, "bold"), width=10
        )
        self.label_time.grid(row=0, column=4, rowspan=2, padx=20)

        # أزرار التحكم (ابدأ، إيقاف، إعادة)
        self.start_btn = tk.Button(
            self.frame, text="ابدأ", font=("Arial", 11), width=7, command=self.start_timer
        )
        self.start_btn.grid(row=1, column=5, padx=5)

        self.stop_btn = tk.Button(
            self.frame, text="إيقاف", font=("Arial", 11), width=7, command=self.stop_timer
        )
        self.stop_btn.grid(row=1, column=6, padx=5)

        self.reset_btn = tk.Button(
            self.frame, text="إعادة", font=("Arial", 11), width=7, command=self.reset_timer
        )
        self.reset_btn.grid(row=1, column=7, padx=5)

        # تحميل الوقت المحفوظ إذا كان موجودًا
        if self.time_left > 0:
            self.update_display()
            h = self.time_left // 3600
            m = (self.time_left % 3600) // 60
            s = self.time_left % 60
            self.hours_entry.delete(0, tk.END)
            self.hours_entry.insert(0, str(h))
            self.minutes_entry.delete(0, tk.END)
            self.minutes_entry.insert(0, str(m))
            self.seconds_entry.delete(0, tk.END)
            self.seconds_entry.insert(0, str(s))

    def update_display(self):
        h = self.time_left // 3600
        m = (self.time_left % 3600) // 60
        s = self.time_left % 60
        self.label_time.config(text=f"{h:02}:{m:02}:{s:02}")

    def start_timer(self):
        if not self.running:
            try:
                hours = int(self.hours_entry.get())
                minutes = int(self.minutes_entry.get())
                seconds = int(self.seconds_entry.get())

                # تحقق من صحة الوقت المدخل
                if not (0 <= minutes < 60) or not (0 <= seconds < 60):
                    messagebox.showerror("خطأ", "يجب أن تكون الدقائق والثواني بين 0 و59")
                    return

                total_seconds = hours * 3600 + minutes * 60 + seconds
                if total_seconds <= 0:
                    messagebox.showerror("خطأ", "أدخل وقتًا أكبر من صفر")
                    return

                self.time_left = total_seconds
                self.running = True
                self.update_timer()
            except ValueError:
                messagebox.showerror("خطأ", "أدخل أرقامًا صحيحة")

    def stop_timer(self):
        self.running = False

    def reset_timer(self):
        self.running = False
        self.time_left = 0
        self.label_time.config(text="00:00:00")
        self.hours_entry.delete(0, tk.END)
        self.hours_entry.insert(0, "0")
        self.minutes_entry.delete(0, tk.END)
        self.minutes_entry.insert(0, "0")
        self.seconds_entry.delete(0, tk.END)
        self.seconds_entry.insert(0, "0")

    def update_timer(self):
        if self.running and self.time_left > 0:
            self.time_left -= 1
            self.update_display()
            self.frame.after(1000, self.update_timer)
        elif self.time_left == 0 and self.running:
            self.running = False
            self.label_time.config(text="انتهى!")
            messagebox.showinfo("انتهى الوقت", f"انتهى العداد لـ {self.name}!\nيمكنك الآن فتح اللعبة.")


def save_data(timers):
    data = {pc.name: pc.time_left for pc in timers}
    try:
        with open(SAVE_FILE, "w") as f:
            json.dump(data, f)
    except Exception as e:
        print(f"خطأ في الحفظ: {e}")


def load_data():
    if os.path.exists(SAVE_FILE):
        try:
            with open(SAVE_FILE, "r") as f:
                return json.load(f)
        except Exception as e:
            print(f"خطأ في تحميل البيانات: {e}")
    return {}


def on_closing():
    save_data(timers)
    root.destroy()


def auto_save():
    save_data(timers)
    root.after(10000, auto_save)  # حفظ تلقائي كل 10 ثواني


def on_ctrl_s(event=None):
    save_data(timers)
    messagebox.showinfo("حفظ", "تم الحفظ بنجاح!")


root = tk.Tk()
root.title("PC Timers")
root.geometry("750x600")
root.resizable(False, False)

timers = []
saved_times = load_data()
for i in range(1, 10):
    time_left = saved_times.get(f"PC {i}", 0)
    timer = PC_Timer(root, f"PC {i}", saved_time=time_left)
    timers.append(timer)

root.protocol("WM_DELETE_WINDOW", on_closing)
auto_save()

root.bind("<Control-s>", on_ctrl_s)
root.bind("<Control-S>", on_ctrl_s)

root.mainloop()
