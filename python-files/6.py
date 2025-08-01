import cv2
import pytesseract
import re
from PIL import Image, ImageTk
import os
import platform
import shutil
import numpy as np
import tkinter as tk
from tkinter import filedialog, scrolledtext

# 📌 خواندن تصویر با پشتیبانی از مسیر فارسی
def imread_unicode(path):
    try:
        data = np.fromfile(path, dtype=np.uint8)
        img = cv2.imdecode(data, cv2.IMREAD_COLOR)
        return img
    except Exception as e:
        log_message(f"⚠️ خطا در خواندن تصویر: {e}")
        return None

# 🔍 پیدا کردن خودکار مسیر tesseract
def auto_set_tesseract_path():
    try:
        system_os = platform.system()
        if system_os == "Windows":
            default_path = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
            if os.path.exists(default_path):
                pytesseract.pytesseract.tesseract_cmd = default_path
                return True
            tesseract_in_path = shutil.which("tesseract")
            if tesseract_in_path:
                pytesseract.pytesseract.tesseract_cmd = tesseract_in_path
                return True
            log_message("❌ Tesseract پیدا نشد. لطفا آن را نصب کنید:\n📥 https://github.com/UB-Mannheim/tesseract/wiki")
            return False
        else:
            if shutil.which("tesseract"):
                return True
            else:
                log_message("❌ لطفاً Tesseract را نصب کنید. (Linux/Mac)")
                return False
    except Exception as e:
        log_message(f"⚠️ خطا در شناسایی مسیر Tesseract: {e}")
        return False

# 📌 تابع استخراج اعداد از تصویر
def extract_numbers(image_path):
    try:
        if not auto_set_tesseract_path():
            return []

        if not os.path.exists(image_path):
            log_message(f"❌ فایل '{image_path}' پیدا نشد.")
            return []

        img = imread_unicode(image_path)
        if img is None:
            log_message("❌ خطا در خواندن تصویر. ممکن است فرمت پشتیبانی نشود.")
            return []

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)
        thresh = cv2.bitwise_not(thresh)

        custom_config = r'--oem 3 --psm 6 outputbase digits'
        extracted_text = pytesseract.image_to_string(thresh, config=custom_config)

        log_message(f"📜 متن خام استخراج‌شده:\n{repr(extracted_text.strip())}")

        numbers = re.findall(r'\d+', extracted_text)
        if numbers:
            log_message(f"🔢 لیست اعداد پیدا شده: {numbers}")
            return [int(num) for num in numbers]
        else:
            log_message("❌ عددی پیدا نشد.")
            return []
    except pytesseract.TesseractError as te:
        log_message(f"⚠️ خطا در اجرای OCR: {te}")
        return []
    except Exception as e:
        log_message(f"⚠️ خطای ناشناخته: {e}")
        return []

# 📌 انتخاب فایل و نمایش تصویر
def select_file():
    file_path = filedialog.askopenfilename(
        title="انتخاب تصویر",
        filetypes=[("تصاویر", "*.png;*.jpg;*.jpeg;*.bmp;*.tiff"), ("همه فایل‌ها", "*.*")]
    )
    if file_path:
        entry_path.delete(0, tk.END)
        entry_path.insert(0, file_path)
        clear_output()  # پاک کردن خروجی قبلی
        show_image(file_path)
        extract_numbers(file_path)

# 📌 نمایش تصویر
def show_image(path):
    try:
        img_pil = Image.open(path)
        img_pil.thumbnail((300, 300))
        img_tk = ImageTk.PhotoImage(img_pil)
        label_image.config(image=img_tk)
        label_image.image = img_tk
    except Exception as e:
        log_message(f"⚠️ خطا در نمایش تصویر: {e}")

# 📌 نوشتن در خروجی
def log_message(message):
    text_output.insert(tk.END, message + "\n")
    text_output.see(tk.END)

# 📌 پاک کردن خروجی
def clear_output():
    text_output.delete("1.0", tk.END)

# 📌 خروج
def exit_app():
    root.destroy()

# ===============================
# رابط گرافیکی
# ===============================
root = tk.Tk()
root.title("تشخیص اعداد با OCR")
root.geometry("700x600")

instructions = (
    "📌 راهنمای استفاده:"
    "\n1- ابتدا Tesseract OCR را روی ویندوز، مک یا لینوکس نصب کنید:"
    "\n- ویندوز: https: // github.com / UB-Mannheim / tesseract / wiki"
    "\n- لینوکس: sudo apt install tesseract-ocr -y"
    "\n- مک: brew install tesseract"
    "\n2- این برنامه با رابط گرافیکی Tkinter برای سیستم‌های دسکتاپ ساخته شده است و در محیط‌های وب مانند Google Colab قابل اجرا نیست."
    "\n3- اگر می‌خواهید در Google Colab OCR انجام دهید، باید از کدهای بدون رابط گرافیکی استفاده کنید."
    "\n4- این برنامه فقط اعداد را از تصویر استخراج می‌کند."
)
label_instructions = tk.Label(root, text=instructions, justify="left", fg="blue")
label_instructions.pack(pady=5)

frame_input = tk.Frame(root)
frame_input.pack(pady=5)

entry_path = tk.Entry(frame_input, width=50)
entry_path.pack(side=tk.LEFT, padx=5)

btn_browse = tk.Button(frame_input, text="انتخاب فایل", command=select_file)
btn_browse.pack(side=tk.LEFT, padx=5)

btn_exit = tk.Button(frame_input, text="خروج", command=exit_app, fg="red")
btn_exit.pack(side=tk.LEFT, padx=5)

label_image = tk.Label(root)
label_image.pack(pady=5)

text_output = scrolledtext.ScrolledText(root, width=80, height=15)
text_output.pack(padx=10, pady=10)

root.mainloop()