# برنامه چک‌لیست با پشتیبانی از زمان تکی و بازه‌ای و آلارم
# این کد بدون نیاز به کتابخانه خارجی است و در PyCharm و بعد از تبدیل به exe قابل اجراست.
# نکته: برای پخش صدا از winsound استفاده می‌شود اگر در دسترس باشد، در غیر این‌صورت از bell() استفاده می‌شود.

import tkinter as tk
from tkinter import ttk, messagebox
import datetime

# تلاش برای وارد کردن winsound (ویندوز). اگر نباشد از bell استفاده می‌شود.
try:
    import winsound
    _HAS_WINSOUND = True
except Exception:
    _HAS_WINSOUND = False

TIME_FORMAT = "%H:%M"


def parse_time_string(time_string: str):
    """
    ورودی می‌تواند یکی از دو حالت باشد:
    - "HH:MM" (زمان تکی)
    - "HH:MM-HH:MM" (بازه)
    خروجی: (mode, start_str, end_str_or_None)
    mode -> "single" یا "range"
    اگر فرمت اشتباه باشد ValueError پرتاب می‌شود.
    """
    s = time_string.strip()
    if "-" in s:
        parts = s.split("-")
        if len(parts) != 2:
            raise ValueError("فرمت بازه اشتباه است.")
        a = parts[0].strip()
        b = parts[1].strip()
        datetime.datetime.strptime(a, TIME_FORMAT)
        datetime.datetime.strptime(b, TIME_FORMAT)
        return "range", a, b
    else:
        datetime.datetime.strptime(s, TIME_FORMAT)
        return "single", s, None


def current_time_hm():
    """ساعت فعلی به فرمت HH:MM"""
    return datetime.datetime.now().strftime(TIME_FORMAT)


class TodoApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("چک‌لیست ایلیا — بدون ارور")
        try:
            self.root.state("zoomed")
        except Exception:
            self.root.geometry("1000x700")
        self.root.configure(bg="#1E1E2E")

        self.tasks = []  # لیست کارها

        # --- رابط کاربری ---
        header = tk.Label(self.root, text="مدیریت کارهای روزانه", font=("B Nazanin", 26, "bold"),
                          bg="#1E1E2E", fg="#00FFCC")
        header.pack(pady=14)

        input_frame = tk.Frame(self.root, bg="#1E1E2E")
        input_frame.pack(padx=12, pady=8, fill="x")

        tk.Label(input_frame, text="عنوان کار:", bg="#1E1E2E", fg="white", font=("B Nazanin", 13)).grid(row=0, column=0, sticky="w", padx=6)
        self.title_entry = tk.Entry(input_frame, font=("B Nazanin", 13), width=40)
        self.title_entry.grid(row=0, column=1, padx=6, sticky="w")

        tk.Label(input_frame, text="زمان (مثلاً 12:30 یا 12:30-13:45):", bg="#1E1E2E", fg="white", font=("B Nazanin", 13)).grid(row=0, column=2, sticky="w", padx=6)
        self.time_entry = tk.Entry(input_frame, font=("B Nazanin", 13), width=25)
        self.time_entry.grid(row=0, column=3, padx=6, sticky="w")

        self.alarm_var = tk.BooleanVar(value=True)
        tk.Checkbutton(input_frame, text="یادآوری فعال باشد", variable=self.alarm_var,
                       bg="#1E1E2E", fg="white", font=("B Nazanin", 12), selectcolor="#333").grid(row=0, column=4, padx=8)

        # دکمه‌ها
        btn_frame = tk.Frame(self.root, bg="#1E1E2E")
        btn_frame.pack(pady=10, padx=10, fill="x")

        style = ttk.Style()
        style.configure("TButton", font=("B Nazanin", 12, "bold"), padding=6)

        ttk.Button(btn_frame, text="➕ افزودن کار", command=self.add_task).grid(row=0, column=0, padx=6)
        ttk.Button(btn_frame, text="✏️ ویرایش کار", command=self.open_edit_window).grid(row=0, column=1, padx=6)
        ttk.Button(btn_frame, text="❌ حذف کار", command=self.delete_task).grid(row=0, column=2, padx=6)
        ttk.Button(btn_frame, text="🧹 پاک کردن همه", command=self.clear_all).grid(row=0, column=3, padx=6)
        ttk.Button(btn_frame, text="🚪 خروج", command=self.root.quit).grid(row=0, column=4, padx=6)

        # لیست با اسکرول بار
        list_frame = tk.Frame(self.root, bg="#1E1E2E")
        list_frame.pack(padx=12, pady=10, fill="both", expand=True)

        self.listbox = tk.Listbox(list_frame, font=("Consolas", 13), bg="#282A36", fg="cyan",
                                  selectbackground="#00FFCC", activestyle="none")
        self.listbox.pack(side="left", fill="both", expand=True)

        scroll = ttk.Scrollbar(list_frame, orient="vertical", command=self.listbox.yview)
        scroll.pack(side="right", fill="y")
        self.listbox.config(yscrollcommand=scroll.set)

        # وضعیت ساعت فعلی
        self.status_label = tk.Label(self.root, text=f"ساعت فعلی: {current_time_hm()}",
                                     font=("B Nazanin", 11), bg="#1E1E2E", fg="white")
        self.status_label.pack(pady=6)

        self.check_interval_ms = 5000  # هر ۵ ثانیه بررسی می‌کند
        self.root.after(1000, self.check_alarms_main_thread)

    # --- نمایش قالب برای هر کار ---
    def task_display_text(self, task: dict) -> str:
        if task["mode"] == "single":
            return f"🕒 {task['start']} | {task['title']}" + (" 🔔" if task["alarm"] else "")
        else:
            return f"🕒 {task['start']} تا {task['end']} | {task['title']}" + (" 🔔" if task["alarm"] else "")

    # --- افزودن کار جدید ---
    def add_task(self):
        title = self.title_entry.get().strip()
        time_text = self.time_entry.get().strip()
        alarm_on = bool(self.alarm_var.get())

        if not title or not time_text:
            messagebox.showwarning("هشدار", "لطفاً عنوان و زمان را وارد کنید.")
            return

        try:
            mode, start_str, end_str = parse_time_string(time_text)
        except Exception as e:
            messagebox.showerror("فرمت زمان نادرست", f"زمان به شکل صحیح وارد نشده است.\nمثال‌های صحیح: 12:30 یا 12:30-13:45\n\nخطا: {e}")
            return

        task_obj = {
            "title": title,
            "mode": mode,
            "start": start_str,
            "end": end_str,
            "alarm": alarm_on,
            "alerted_start": False,
            "alerted_end": False
        }
        self.tasks.append(task_obj)
        self.listbox.insert(tk.END, self.task_display_text(task_obj))

        self.title_entry.delete(0, tk.END)
        self.time_entry.delete(0, tk.END)
        self.alarm_var.set(True)

    # --- باز کردن پنجره ویرایش ---
    def open_edit_window(self):
        try:
            idx = self.listbox.curselection()[0]
        except IndexError:
            messagebox.showwarning("هشدار", "ابتدا یک کار را از لیست انتخاب کنید.")
            return

        task = self.tasks[idx]
        edit_win = tk.Toplevel(self.root)
        edit_win.title("ویرایش کار")
        edit_win.configure(bg="#1E1E2E")
        edit_win.grab_set()

        tk.Label(edit_win, text="عنوان:", bg="#1E1E2E", fg="white", font=("B Nazanin", 12)).grid(row=0, column=0, padx=6, pady=6, sticky="w")
        title_e = tk.Entry(edit_win, font=("B Nazanin", 12), width=40)
        title_e.grid(row=0, column=1, padx=6, pady=6)
        title_e.insert(0, task["title"])

        tk.Label(edit_win, text="نوع زمان‌بندی:", bg="#1E1E2E", fg="white", font=("B Nazanin", 12)).grid(row=1, column=0, padx=6, pady=6, sticky="w")
        mode_var = tk.StringVar(value=task["mode"])
        tk.Radiobutton(edit_win, text="تک‌زمانی", variable=mode_var, value="single", bg="#1E1E2E", fg="white", selectcolor="#333", font=("B Nazanin", 11)).grid(row=1, column=1, sticky="w")
        tk.Radiobutton(edit_win, text="بازه", variable=mode_var, value="range", bg="#1E1E2E", fg="white", selectcolor="#333", font=("B Nazanin", 11)).grid(row=1, column=1, sticky="e")

        tk.Label(edit_win, text="شروع (HH:MM):", bg="#1E1E2E", fg="white", font=("B Nazanin", 12)).grid(row=2, column=0, padx=6, pady=6, sticky="w")
        start_e = tk.Entry(edit_win, font=("B Nazanin", 12), width=15)
        start_e.grid(row=2, column=1, padx=6, pady=6, sticky="w")
        start_e.insert(0, task["start"])

        tk.Label(edit_win, text="پایان (HH:MM):", bg="#1E1E2E", fg="white", font=("B Nazanin", 12)).grid(row=3, column=0, padx=6, pady=6, sticky="w")
        end_e = tk.Entry(edit_win, font=("B Nazanin", 12), width=15)
        end_e.grid(row=3, column=1, padx=6, pady=6, sticky="w")
        if task["end"]:
            end_e.insert(0, task["end"])

        alarm_var_local = tk.BooleanVar(value=task["alarm"])
        tk.Checkbutton(edit_win, text="یادآوری فعال باشد", variable=alarm_var_local, bg="#1E1E2E", fg="white", font=("B Nazanin", 11), selectcolor="#333").grid(row=4, column=1, padx=6, pady=6, sticky="w")

        def save_edit():
            new_title = title_e.get().strip()
            new_mode = mode_var.get()
            new_start = start_e.get().strip()
            new_end = end_e.get().strip()
            new_alarm = bool(alarm_var_local.get())

            if not new_title or not new_start:
                messagebox.showwarning("خطا", "عنوان و زمان شروع را وارد کنید.")
                return

            try:
                if new_mode == "single":
                    datetime.datetime.strptime(new_start, TIME_FORMAT)
                    new_end_val = None
                else:
                    if not new_end:
                        messagebox.showwarning("خطا", "در حالت بازه باید زمان پایان را وارد کنید.")
                        return
                    datetime.datetime.strptime(new_start, TIME_FORMAT)
                    datetime.datetime.strptime(new_end, TIME_FORMAT)
                    new_end_val = new_end
            except Exception as e:
                messagebox.showerror("فرمت اشتباه", f"فرمت زمان اشتباه است.\nمثال صحیح: 12:30 یا 12:30-13:45\n\nخطا: {e}")
                return

            task["title"] = new_title
            task["mode"] = new_mode
            task["start"] = new_start
            task["end"] = new_end_val
            task["alarm"] = new_alarm
            task["alerted_start"] = False
            task["alerted_end"] = False

            self.listbox.delete(idx)
            self.listbox.insert(idx, self.task_display_text(task))
            messagebox.showinfo("موفق", "تغییرات ذخیره شد.")
            edit_win.destroy()

        ttk.Button(edit_win, text="ذخیره تغییرات", command=save_edit).grid(row=5, column=1, padx=6, pady=10, sticky="e")

    # --- حذف یک کار ---
    def delete_task(self):
        try:
            idx = self.listbox.curselection()[0]
        except IndexError:
            messagebox.showwarning("هشدار", "ابتدا یک کار را انتخاب کنید.")
            return
        if messagebox.askyesno("حذف", "آیا مطمئن هستید این کار حذف شود؟"):
            self.listbox.delete(idx)
            del self.tasks[idx]

    # --- پاک کردن همه ---
    def clear_all(self):
        if messagebox.askyesno("تأیید", "آیا مطمئن هستید همه‌ی کارها حذف شوند؟"):
            self.listbox.delete(0, tk.END)
            self.tasks.clear()

    # --- چک کردن آلارم‌ها ---
    def check_alarms_main_thread(self):
        try:
            self.status_label.config(text=f"ساعت فعلی: {current_time_hm()}")
        except Exception:
            pass

        now_hm = current_time_hm()
        for task in self.tasks:
            try:
                if not task.get("alarm", False):
                    continue
                if task.get("mode") == "single":
                    if now_hm == task.get("start") and not task.get("alerted_start", False):
                        self.fire_alert(f"⏰ زمان انجام کار: {task.get('title')}")
                        task["alerted_start"] = True
                else:
                    if now_hm == task.get("start") and not task.get("alerted_start", False):
                        self.fire_alert(f"✅ شروع کار: {task.get('title')}")
                        task["alerted_start"] = True
                    if task.get("end") and now_hm == task.get("end") and not task.get("alerted_end", False):
                        self.fire_alert(f"🏁 پایان کار: {task.get('title')}")
                        task["alerted_end"] = True
            except Exception:
                continue

        try:
            self.root.after(self.check_interval_ms, self.check_alarms_main_thread)
        except Exception:
            pass

    # --- پخش صدا و نمایش پیام پاپ‌آپ ---
    def fire_alert(self, message_text: str):
        try:
            if _HAS_WINSOUND:
                winsound.Beep(1000, 300)
                winsound.Beep(1400, 300)
                winsound.Beep(1800, 300)
            else:
                self.root.bell()
                self.root.after(300, lambda: self.root.bell())
                self.root.after(600, lambda: self.root.bell())
        except Exception:
            try:
                self.root.bell()
            except Exception:
                pass

        try:
            messagebox.showinfo("یادآوری", message_text)
        except Exception:
            print("ALERT:", message_text)


# --- اجرای برنامه ---
if __name__ == "__main__":
    root = tk.Tk()
    app = TodoApp(root)
    root.mainloop()
