import tkinter as tk
from tkinter import messagebox
import base64, hmac, hashlib

# المفتاح السري (احتفظ به سريًا)
SECRET_KEY = b"MY_SUPER_SECRET_KEY"

def generate_key():
    product_code = entry_product.get()
    activation_code = entry_activation.get()
    try:
        valid_days = int(entry_days.get())
    except:
        messagebox.showerror("خطأ", "عدد الأيام غير صحيح")
        return
    
    if not product_code or not activation_code:
        messagebox.showerror("خطأ", "يرجى إدخال جميع الحقول")
        return
    
    # إنشاء مفتاح يعتمد على المدخلات
    raw_data = f"{product_code}:{activation_code}:{valid_days}".encode()
    signature = hmac.new(SECRET_KEY, raw_data, hashlib.sha256).digest()
    license_key = base64.urlsafe_b64encode(raw_data + b":" + signature).decode()
    
    text_result.delete("1.0", tk.END)
    text_result.insert(tk.END, license_key)

# إنشاء الواجهة
root = tk.Tk()
root.title("Key Gen")
root.geometry("500x400")

tk.Label(root, text="Product Purchase Code:").pack(anchor="w", padx=10, pady=5)
entry_product = tk.Entry(root, width=50)
entry_product.pack(padx=10)

tk.Label(root, text="Activation Code:").pack(anchor="w", padx=10, pady=5)
entry_activation = tk.Entry(root, width=50)
entry_activation.pack(padx=10)

tk.Label(root, text="Valid For (days):").pack(anchor="w", padx=10, pady=5)
entry_days = tk.Entry(root, width=10)
entry_days.pack(padx=10)
entry_days.insert(0, "365")

tk.Button(root, text="Generate Key", command=generate_key).pack(pady=10)

text_result = tk.Text(root, height=10, width=60)
text_result.pack(padx=10, pady=5)

root.mainloop()