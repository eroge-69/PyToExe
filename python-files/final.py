import tkinter as tk
from tkinter import messagebox, colorchooser
import random
import time
import csv
import os

# ------------------ بخش آزمون ------------------
class QuizApp:
    def __init__(self, root):
        self.root = root
        self.root.title("سیستم آزمون")
        self.root.geometry("600x400")

        self.questions = []
        self.answers = []
        self.user_answers = {}
        self.current = 0
        self.start_time = None
        self.duration = 30 * 60  # 30 دقیقه ثابت
        self.remaining = 0

        # صفحه شروع
        self.start_frame = tk.Frame(root)
        self.start_frame.pack(fill="both", expand=True)

        tk.Label(self.start_frame, text="زمان آزمون: 30 دقیقه").pack(pady=10)
        tk.Label(self.start_frame, text="تعداد سوالات ازمون : 10").pack(pady=10)
        tk.Label(self.start_frame, text="نمره اين آزمون از 100 ميباشد.باآرزوي موفقيت براي شما دوست عزيز").pack(pady=10)
        tk.Button(self.start_frame, text="شروع آزمون", command=self.start_quiz).pack(pady=10)
        

    def load_questions(self):
        # استفاده از os.getcwd برای دریافت مسیر فایل
        file_path = os.path.join(os.getcwd(), "extended_farsi_questions_utf8.csv")
        
        # چاپ مسیر فایل برای بررسی
        print(f"فایل سوالات در مسیر: {file_path}")
        
        # بررسی اینکه آیا فایل واقعا وجود دارد؟
        if not os.path.isfile(file_path):
            messagebox.showerror("خطا", f"فایل سوالات پیدا نشد. مسیر: {file_path}")
            self.root.quit()
            return
        
        try:
            with open(file_path, mode="r", encoding="utf-8-sig") as file:
                reader = csv.reader(file)
                next(reader)  # خط اول رو که عنوان ستون‌هاست رد می‌کنیم
                for row in reader:
                    if len(row) < 6:  # اگر تعداد ستون‌ها کمتر از 6 بود، از آن سوال صرفنظر کن
                        continue
                    q, a, b, c, d, ans = row
                    options = [("A", a), ("B", b), ("C", c), ("D", d)]
                    random.shuffle(options)  # جابجایی گزینه‌ها
                    self.questions.append((q, options))
                    self.answers.append(ans)

            if not self.questions:
                messagebox.showerror("خطا", "هیچ سوالی برای بارگذاری وجود ندارد.")
                self.root.quit()
                return

            # ترتیب سوالات هم تصادفی
            zipped = list(zip(self.questions, self.answers))
            random.shuffle(zipped)
            self.questions, self.answers = zip(*zipped)

        except FileNotFoundError:
            messagebox.showerror("خطا", f"فایل سوالات پیدا نشد. مسیر: {file_path}")
            self.root.quit()

    def start_quiz(self):
        self.load_questions()
        self.start_time = time.time()
        self.remaining = self.duration

        self.start_frame.destroy()
        self.quiz_frame = tk.Frame(self.root)
        self.quiz_frame.pack(fill="both", expand=True)
        self.show_question()
        self.update_timer()

    def show_question(self):
        if self.current >= len(self.questions):  # جلوگیری از ارور با بررسی طول لیست سوالات
            self.finish()
            return

        for widget in self.quiz_frame.winfo_children():
            widget.destroy()

        q_text, options = self.questions[self.current]
        tk.Label(self.quiz_frame, text=f"سوال {self.current+1}: {q_text}", wraplength=500).pack(pady=10)

        self.var = tk.StringVar()  # ایجاد یک متغیر StringVar برای کنترل انتخاب‌ها
        self.var.set(None)  # تنظیم مقدار اولیه None تا هیچ گزینه‌ای پیش‌فرض انتخاب نشود

        for letter, text in options:
            tk.Radiobutton(self.quiz_frame, text=text, variable=self.var, value=text).pack(anchor="w")

        btn_frame = tk.Frame(self.quiz_frame)
        btn_frame.pack(pady=20)

        if self.current > 0:
            tk.Button(btn_frame, text="قبلی", command=self.prev_question).pack(side="left", padx=5)
        if self.current < len(self.questions) - 1:
            tk.Button(btn_frame, text="بعدی", command=self.next_question).pack(side="left", padx=5)
        else:
            tk.Button(btn_frame, text="پایان آزمون", command=self.finish).pack(side="left", padx=5)

    def next_question(self):
        if self.current < len(self.questions) - 1:  # جلوگیری از دسترسی خارج از محدوده
            self.user_answers[self.current] = self.var.get()
            self.current += 1
            self.show_question()

    def prev_question(self):
        if self.current > 0:  # جلوگیری از رفتن به سوال منفی
            self.user_answers[self.current] = self.var.get()
            self.current -= 1
            self.show_question()

    def update_timer(self):
        elapsed = int(time.time() - self.start_time)
        self.remaining = self.duration - elapsed
        if self.remaining <= 0:
            self.finish()
            return
        mins, secs = divmod(self.remaining, 60)
        self.root.title(f"زمان باقی مانده: {mins:02d}:{secs:02d}")
        self.root.after(1000, self.update_timer)

    def finish(self):
        # اگر هنوز در حال پاسخ دادن به سوالی هستیم، پاسخ را ذخیره می‌کنیم
        if self.current < len(self.questions):
            self.user_answers[self.current] = self.var.get()

        score = 0
        review = ""

        for i, ((q, options), ans) in enumerate(zip(self.questions, self.answers)):
            user = self.user_answers.get(i, "")
            
            # Create a dict of options and map the answer correctly
            options_dict = dict(options)
            
            # Find the correct answer in options
            correct_option = ans
            correct_text = options_dict.get(correct_option, "پاسخ نادرست")
            
            user_text = options_dict.get(user, "بی‌پاسخ")
            
            # Increment score if the user selects the correct answer
            if user == correct_option:
                score += 10
            review += f"سوال {i+1}: {q}\nپاسخ صحیح: {correct_text}\nپاسخ شما: {user_text}\n\n"

        messagebox.showinfo("نتیجه", f"نمره شما: {score} از 100")
        self.show_review(review)

    def show_review(self, text):
        self.quiz_frame.destroy()
        frame = tk.Frame(self.root)
        frame.pack(fill="both", expand=True)
        txt = tk.Text(frame, wrap="word")
        txt.insert("1.0", text)
        txt.pack(expand=True, fill="both")

# ------------------ بخش Paint ------------------
class PaintApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Paint ساده")
        self.root.geometry("600x400")

        self.color = "black"
        self.old_x, self.old_y = None, None

        self.canvas = tk.Canvas(self.root, bg="white")
        self.canvas.pack(fill="both", expand=True)

        self.canvas.bind("<B1-Motion>", self.draw)
        self.canvas.bind("<ButtonRelease-1>", self.reset)

        btn_frame = tk.Frame(self.root)
        btn_frame.pack()

        tk.Button(btn_frame, text="انتخاب رنگ", command=self.choose_color).pack(side="left")
        tk.Button(btn_frame, text="پاک‌کن", command=self.use_eraser).pack(side="left")
        tk.Button(btn_frame, text="پاک کردن همه", command=self.clear_canvas).pack(side="left")

    def draw(self, event):
        if self.old_x and self.old_y:
            self.canvas.create_line(self.old_x, self.old_y, event.x, event.y, fill=self.color, width=3)
        self.old_x, self.old_y = event.x, event.y

    def reset(self, event):
        self.old_x, self.old_y = None, None

    def choose_color(self):
        c = colorchooser.askcolor()[1]
        if c:
            self.color = c

    def use_eraser(self):
        self.color = "white"

    def clear_canvas(self):
        self.canvas.delete("all")

# ------------------ منوی اصلی ------------------
def main_menu():
    root = tk.Tk()
    root.title("منوی اصلی")
    root.geometry("300x200")

    tk.Label(root, text="لطفا یکی را انتخاب کنید:").pack(pady=20)
    tk.Button(root, text="شروع آزمون", command=lambda: open_quiz(root)).pack(pady=10)
    tk.Button(root, text="باز کردن Paint", command=lambda: open_paint(root)).pack(pady=10)

    root.mainloop()

def open_quiz(old_root):
    old_root.destroy()
    root = tk.Tk()
    app = QuizApp(root)
    root.mainloop()

def open_paint(old_root):
    old_root.destroy()
    root = tk.Tk()
    app = PaintApp(root)
    root.mainloop()

if __name__ == "__main__":
    main_menu()
