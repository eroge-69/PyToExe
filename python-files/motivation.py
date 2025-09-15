import tkinter as tk
from tkinter import messagebox
import webbrowser

# لینک‌ها
link_book = "https://s34.picofile.com/file/8486665450/%DA%A9%D8%AA%D8%A7%D8%A8_%D9%85%D9%88%D9%81%D9%82%DB%8C%D8%AA.docx.html"
link_music = "https://songsara.net/82599/"

# تابع برای بررسی ورودی
def check_word():
    user_input = entry.get().strip()
    if user_input == "کتاب":
        webbrowser.open(link_book)
    elif user_input == "اهنگ":
        webbrowser.open(link_music)
    else:
        messagebox.showwarning("خطا", "کلمه‌ی وارد شده معتبر نیست!\nفقط 'کتاب' یا 'اهنگ' پذیرفته می‌شود.")

# منوی اولیه
def start_menu():
    def continue_pressed():
        menu_frame.pack_forget()
        show_entry()

    menu_frame = tk.Frame(root, bg="#e0f7fa", padx=20, pady=20)
    menu_frame.pack(expand=True)

    # توضیحات کتاب
    tk.Label(menu_frame, text="کتاب رشد فردی", font=("Arial", 12, "bold"), bg="#e0f7fa").grid(row=0, column=0, sticky="w", padx=5, pady=5)
    tk.Label(menu_frame, text="برای دستیابی: در کادر کلمه‌ی 'کتاب' را وارد کنید", font=("Arial", 10), bg="#e0f7fa").grid(row=0, column=1, sticky="w", padx=5, pady=5)

    # توضیحات آهنگ
    tk.Label(menu_frame, text="تمرکز", font=("Arial", 12, "bold"), bg="#e0f7fa").grid(row=1, column=0, sticky="w", padx=5, pady=5)
    tk.Label(menu_frame, text="برای بهترین اهنگ ها: در کادر کلمه‌ی 'اهنگ' را وارد کنید", font=("Arial", 10), bg="#e0f7fa").grid(row=1, column=1, sticky="w", padx=5, pady=5)

    # دکمه ادامه دادن
    tk.Button(menu_frame, text="ادامه دادن", command=continue_pressed, bg="#00796b", fg="white", font=("Arial", 12, "bold")).grid(row=2, column=0, columnspan=2, pady=20)

# نمایش کادر ورودی
def show_entry():
    entry_frame = tk.Frame(root, bg="#fffde7", padx=20, pady=20)
    entry_frame.pack(expand=True)

    tk.Label(entry_frame, text="کلمه خود را وارد کنید:", font=("Arial", 12, "bold"), bg="#fffde7").pack(pady=10)
    global entry
    entry = tk.Entry(entry_frame, font=("Arial", 14), justify="center")
    entry.pack(pady=10)

    tk.Button(entry_frame, text="بررسی", command=check_word, bg="#f57f17", fg="white", font=("Arial", 12, "bold")).pack(pady=15)

# پنجره اصلی
root = tk.Tk()
root.title("دسترسی به کتاب و آهنگ")
root.geometry("700x300")
root.resizable(False, False)

start_menu()
root.mainloop()

