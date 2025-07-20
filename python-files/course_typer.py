
import tkinter as tk
from tkinter import messagebox
import pyautogui
import time
import threading

class CourseTyperApp:
    def __init__(self, root):
        self.root = root
        self.root.title("برنامج تسجيل المواد")
        self.entries = []

        # إنشاء 6 خانات لإدخال الرموز
        for i in range(6):
            entry = tk.Entry(root, width=10, justify='center', font=('Arial', 14))
            entry.grid(row=0, column=i, padx=5, pady=10)
            self.entries.append(entry)

        # زر التشغيل
        start_button = tk.Button(root, text="إدخال الرموز", command=self.start_typing_thread, font=('Arial', 12))
        start_button.grid(row=1, column=0, columnspan=6, pady=10)

        # تعليمات
        instructions = tk.Label(root, text="👆 أدخل الرموز، ثم ضع المؤشر في أول خانة في موقع التسجيل واضغط الزر", fg="gray")
        instructions.grid(row=2, column=0, columnspan=6)

    def start_typing_thread(self):
        # لتجنب تجمد الواجهة أثناء الإدخال
        thread = threading.Thread(target=self.type_codes)
        thread.start()

    def type_codes(self):
        time.sleep(2)  # انتظار ثانيتين قبل البدء للسماح بتغيير النافذة

        for entry in self.entries:
            code = entry.get()
            pyautogui.write(code)
            pyautogui.press('tab')

# تشغيل التطبيق
if __name__ == "__main__":
    root = tk.Tk()
    app = CourseTyperApp(root)
    root.mainloop()
