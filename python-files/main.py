import pyautogui
import webbrowser
import time
import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading
import shutil
from PIL import Image, ImageTk

DOWNLOAD_FOLDER = os.path.join(os.path.expanduser("~"), "Downloads")
stop_requested = False


def wait_for_pdf_download(before_files, timeout=30):
    for _ in range(timeout):
        if stop_requested:
            return None
        time.sleep(1)
        after = {f for f in os.listdir(DOWNLOAD_FOLDER) if f.endswith('.pdf')}
        new_pdfs = after - before_files
        if new_pdfs:
            return list(new_pdfs)[0]
    return None


def process_file(filepath, progress_var, log_box, progress_bar, start_btn, stop_btn):
    global stop_requested
    stop_requested = False

    start_btn.config(state=tk.DISABLED)
    stop_btn.config(state=tk.NORMAL)
    progress_bar.start()

    log_box_insert(log_box, f"🔍 شروع پردازش فایل: {filepath}\n")
    log_box.see(tk.END)

    try:
        with open(filepath, 'r', encoding='utf-8') as file:
            codes = [line.strip() for line in file if line.strip()]
    except Exception as e:
        messagebox.showerror("خطا در خواندن فایل", str(e))
        start_btn.config(state=tk.NORMAL)
        stop_btn.config(state=tk.DISABLED)
        progress_bar.stop()
        return

    webbrowser.open('https://bargheman.com/home')
    time.sleep(5)

    for i, code in enumerate(codes):
        if stop_requested:
            log_box_insert(log_box, "\n⛔ عملیات توسط کاربر متوقف شد.\n")
            break

        progress = int((i + 1) / len(codes) * 100)
        progress_var.set(progress)

        log_box_insert(log_box, f"▶️ در حال پردازش شناسه: {code}\n")

        if len(code) == 13 and code.isdigit():
            try:
                pyautogui.click(1394, 447)
                time.sleep(8)
                pyautogui.write(code)
                pyautogui.press('enter')
                time.sleep(8)

                pyautogui.click(661, 199)
                time.sleep(8)

                pyautogui.click(396, 435)
                time.sleep(8)

                pyautogui.click(1437, 122)

                before = {f for f in os.listdir(DOWNLOAD_FOLDER) if f.endswith('.pdf')}
                filename = wait_for_pdf_download(before, timeout=30)

                if filename:
                    old_path = os.path.join(DOWNLOAD_FOLDER, filename)
                    new_filename = f"{code}.pdf"
                    new_path = os.path.join(DOWNLOAD_FOLDER, new_filename)

                    try:
                        shutil.move(old_path, new_path)
                        log_box_insert(log_box, f"✅ ذخیره شد: {new_filename}\n")
                    except Exception as e:
                        log_box_insert(log_box, f"⚠️ خطا در تغییر نام فایل {filename}: {str(e)}\n")
                else:
                    log_box_insert(log_box, f"❌ دانلود نشد برای {code}\n")

            except Exception as e:
                log_box_insert(log_box, f"⚠️ خطا برای {code}: {str(e)}\n")
        else:
            log_box_insert(log_box, f"⚠️ شناسه نامعتبر: {code}\n")

        log_box.see(tk.END)

    if not stop_requested:
        log_box_insert(log_box, "\n✅ تمام عملیات انجام شد.\n")

    progress_bar.stop()
    progress_var.set(100)
    start_btn.config(state=tk.NORMAL)
    stop_btn.config(state=tk.DISABLED)

    if not stop_requested:
        messagebox.showinfo("پایان", "همه شناسه‌ها پردازش شدند.")


def log_box_insert(log_box, text):
    lines = text.split('\n')
    for line in lines:
        if not line.strip():
            log_box.insert(tk.END, '\n')
            continue
        if any('\u0600' <= c <= '\u06FF' for c in line):
            log_box.insert(tk.END, line + '\n', 'right')
        else:
            log_box.insert(tk.END, line + '\n', 'right')


def on_enter(e):
    e.widget['background'] = '#45a049'


def on_leave(e):
    e.widget['background'] = '#4CAF50'


def on_stop_enter(e):
    e.widget['background'] = '#e53935'


def on_stop_leave(e):
    e.widget['background'] = '#f44336'


def create_rounded_button(master, text, command):
    button = tk.Button(master, text=text, command=command, relief="flat", bg="#4CAF50", fg="white", font=("Vazir", 12))
    button.config(width=20, height=2)
    button.bind("<Enter>", on_enter)
    button.bind("<Leave>", on_leave)
    return button


def create_gui():
    root = tk.Tk()
    root.title("نرم افزار دریافت قبض خودکار - تامین انرژی پایدار آرارات")
    root.geometry("720x620")
    root.resizable(False, False)
    root.configure(bg="#f9f9f9")

    default_font = ("Vazir", 12)
    text_font = ("Vazir", 11)
    log_font = ("Courier New", 10)

    label1 = tk.Label(root, text="📥 انتخاب فایل لیست شناسه‌ها:", font=default_font, bg="#f9f9f9", anchor='e',
                      justify='right')
    label1.pack(pady=12, fill='x')

    selected_file_var = tk.StringVar()
    entry = tk.Entry(root, textvariable=selected_file_var, width=60, justify='right', font=text_font, bd=2,
                     relief="groove")
    entry.pack(pady=6)

    def browse_file():
        file_path = filedialog.askopenfilename(title="انتخاب فایل شناسه", filetypes=[("Text Files", "*.txt")])
        if file_path:
            selected_file_var.set(file_path)

    browse_btn = create_rounded_button(root, "انتخاب فایل", browse_file)
    browse_btn.pack(pady=8)

    progress_var = tk.IntVar()
    progress_bar = ttk.Progressbar(root, length=520, variable=progress_var, mode='determinate')
    progress_bar.pack(pady=12)

    log_box = tk.Text(root, height=18, width=88, font=log_font, bd=2, relief="sunken", wrap="word")
    log_box.pack(pady=12)
    log_box.tag_configure('right', justify='right', rmargin=15)

    def on_start():
        file_path = selected_file_var.get()
        if not file_path:
            messagebox.showwarning("هشدار", "لطفاً یک فایل را انتخاب کنید.")
            return
        threading.Thread(
            target=process_file,
            args=(file_path, progress_var, log_box, progress_bar, start_btn, stop_btn),
            daemon=True
        ).start()

    def on_stop():
        global stop_requested
        stop_requested = True
        log_box_insert(log_box, "\n🛑 دستور توقف صادر شد (توسط دکمه).\n")

    def on_key(event):
        global stop_requested
        key = event.keysym.lower()
        if key in ['s', 'س']:
            stop_requested = True
            log_box_insert(log_box, "\n🛑 دستور توقف صادر شد (توسط صفحه‌کلید).\n")
        elif key == 'escape':
            root.quit()

    global start_btn, stop_btn

    start_btn = create_rounded_button(root, "▶️ شروع عملیات", on_start)
    start_btn.pack(pady=6)

    stop_btn = create_rounded_button(root, "⛔ توقف عملیات", on_stop)
    stop_btn.pack(pady=6)
    stop_btn.config(state=tk.DISABLED)

    root.bind("<Key>", on_key)
    root.mainloop()


create_gui()
