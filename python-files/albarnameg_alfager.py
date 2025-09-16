import tkinter as tk
from tkinter import messagebox
import pyperclip
from num2words import num2words

replace_on_type = False  # فلَاج علشان نمسح الرقم القديم عند الكتابة بعد Enter

# دالة تنسيق الرقم بفواصل
def format_number(event=None):
    global replace_on_type
    value = entry.get().replace(",", "").strip()
    
    # لو الفلاج مفعّل → نمسح القديم ونبدأ كتابة جديد
    if replace_on_type and event and event.char.isdigit():
        entry.delete(0, tk.END)
        replace_on_type = False
        entry.insert(0, event.char)
        return "break"  # يمنع تكرار الكتابة

    if value.isdigit():
        formatted = "{:,}".format(int(value))
        entry.delete(0, tk.END)
        entry.insert(0, formatted)

# دالة إرجاع الرقم بدون فواصل
def get_number():
    return entry.get().replace(",", "").strip()

# دالة التفقيط
def tafqeet(event=None):  
    global replace_on_type
    try:
        number = int(get_number())
        words = num2words(number, lang='ar')
        result_text.delete("1.0", tk.END)   # مسح النتيجة القديمة
        result_text.insert(tk.END, words)  # كتابة الجديدة
        replace_on_type = True  # فعل الفلاج بعد التفقيط
    except ValueError:
        messagebox.showerror("خطأ", "من فضلك أدخل رقم صحيح")

# دالة إعادة التعيين
def reset():
    global replace_on_type
    entry.delete(0, tk.END)
    result_text.delete("1.0", tk.END)
    replace_on_type = False

# دالة مسح الرقم من خانة الإدخال
def clear_entry():
    global replace_on_type
    entry.delete(0, tk.END)
    replace_on_type = False

# دالة لصق الرقم من الحافظة
def paste_entry():
    global replace_on_type
    try:
        pasted = pyperclip.paste()
        pasted = pasted.replace(",", "").strip()
        if pasted.isdigit():
            entry.delete(0, tk.END)
            entry.insert(0, pasted)
            format_number()
            replace_on_type = False
        else:
            messagebox.showwarning("تحذير", "المحتوى المنسوخ ليس رقمًا")
    except Exception:
        messagebox.showerror("خطأ", "لم يتم العثور على محتوى في الحافظة")

# دالة النسخ
def copy_text():
    text = result_text.get("1.0", tk.END).strip()
    if text:
        pyperclip.copy(text)
        messagebox.showinfo("تم النسخ", "تم نسخ النتيجة للحافظة")
    else:
        messagebox.showwarning("تحذير", "لا يوجد نص لنسخه")

# دالة التثبيت فوق الكل
def toggle_on_top():
    global always_on_top
    always_on_top = not always_on_top
    root.attributes("-topmost", always_on_top)
    if always_on_top:
        btn_top.config(text="📌 إلغاء التثبيت")
    else:
        btn_top.config(text="📌 تثبيت فوق الكل")

# إعداد النافذة
root = tk.Tk()
root.title("برنامج التفقيط بالعربي")
root.geometry("750x470")
root.configure(bg="#f0f0f0")

always_on_top = False

# فريم الإدخال + أزرار صغيرة
frame_entry = tk.Frame(root, bg="#f0f0f0")
frame_entry.pack(pady=15)

label = tk.Label(frame_entry, text="أدخل الرقم:", font=("Arial", 18, "bold"), bg="#f0f0f0")
label.pack(side="left", padx=5)

entry = tk.Entry(frame_entry, font=("Arial", 18), justify="center", width=20)
entry.pack(side="left", padx=5)

# حدث لتنسيق الرقم أثناء الكتابة
entry.bind("<KeyRelease>", format_number)

btn_clear_entry = tk.Button(frame_entry, text="❌", command=clear_entry,
                            font=("Arial", 12, "bold"), bg="#e0e0e0", fg="red", width=3, height=1)
btn_clear_entry.pack(side="left", padx=3)

btn_paste_entry = tk.Button(frame_entry, text="📥", command=paste_entry,
                            font=("Arial", 12, "bold"), bg="#e0e0e0", fg="green", width=3, height=1)
btn_paste_entry.pack(side="left", padx=3)

# زرار التفقيط
btn_tafqeet = tk.Button(root, text="✍️ تفقيط الرقم", command=tafqeet,
                        font=("Arial", 18, "bold"), bg="#4CAF50", fg="white", width=20, height=2)
btn_tafqeet.pack(pady=10)

# صندوق النتيجة
result_text = tk.Text(root, font=("Arial", 16), wrap="word",
                      bg="white", fg="black", relief="solid", width=70, height=6)
result_text.pack(pady=10)

# الأزرار (إعادة تعيين ونسخ)
frame = tk.Frame(root, bg="#f0f0f0")
frame.pack(pady=10)

btn_reset = tk.Button(frame, text="🔄 إعادة التعيين", command=reset,
                      font=("Arial", 16, "bold"), bg="#f44336", fg="white", width=18, height=2)
btn_reset.grid(row=0, column=0, padx=15)

btn_copy = tk.Button(frame, text="✅ نسخ النتيجة", command=copy_text,
                     font=("Arial", 16, "bold"), bg="#2196F3", fg="white", width=18, height=2)
btn_copy.grid(row=0, column=1, padx=15)

# زرار التثبيت فوق الكل
btn_top = tk.Button(root, text="📌 تثبيت فوق الكل", command=toggle_on_top,
                    font=("Arial", 14, "bold"), bg="#FFC107", fg="black", width=20, height=2)
btn_top.pack(pady=15)

# ربط زرار Enter بالتفقيط
root.bind("<Return>", tafqeet)

root.mainloop()
