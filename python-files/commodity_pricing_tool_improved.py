import pandas as pd
from tkinter import filedialog, Tk, Label, Entry, Button, messagebox, Frame
import os

def load_file():
    filepath = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx *.xls")])
    if not filepath:
        return
    df = pd.read_excel(filepath)
    excel_data["df"] = df
    excel_data["path"] = filepath
    lbl_file.config(text=f"📄 تم تحميل الملف: {os.path.basename(filepath)}")

def calculate():
    try:
        rate = float(entry_rate.get())
        expenses = float(entry_expenses.get())
        total_yuan = float(entry_total_yuan.get())

        total_dzd = round(total_yuan * rate + expenses, 2)
        factor = round(total_dzd / total_yuan, 2)

        df = excel_data["df"]
        df["السعر بالدينار"] = (df["price"] * factor).round(2)

        lbl_result.config(text=f"✅ السعر الكامل: {total_dzd:.2f} دج | ⚙️ المعامل: {factor:.2f}")

        entry_result_total.delete(0, 'end')
        entry_result_total.insert(0, f"{total_dzd:.2f}")

        entry_result_factor.delete(0, 'end')
        entry_result_factor.insert(0, f"{factor:.2f}")

        excel_data["df"] = df
    except Exception as e:
        messagebox.showerror("خطأ", str(e))

def save_file():
    df = excel_data.get("df")
    if df is None:
        return
    save_path = filedialog.asksaveasfilename(defaultextension=".xlsx")
    if save_path:
        df.to_excel(save_path, index=False)
        messagebox.showinfo("تم الحفظ", f"تم حفظ الملف في:\n{save_path}")

root = Tk()
root.title("📊 برنامج تقييم السلعة")
root.geometry("500x450")
root.resizable(False, False)
root.configure(bg="#f0f0f0")

font_label = ("Arial", 12)
font_entry = ("Arial", 12)
font_button = ("Arial", 12, "bold")

excel_data = {}

# إطار التحميل
frame_top = Frame(root, bg="#f0f0f0")
frame_top.pack(pady=10)

Button(frame_top, text="📂 تحميل ملف Excel", command=load_file, width=25,
       bg="#007acc", fg="white", font=font_button).pack()
lbl_file = Label(frame_top, text="لم يتم تحميل ملف", bg="#f0f0f0", fg="black", font=font_label)
lbl_file.pack()

# إدخال البيانات
frame_inputs = Frame(root, bg="#f0f0f0")
frame_inputs.pack(pady=10)

Label(frame_inputs, text="سعر الصرف:", bg="#f0f0f0", font=font_label).grid(row=0, column=0, sticky='e', padx=5, pady=5)
entry_rate = Entry(frame_inputs, font=font_entry)
entry_rate.grid(row=0, column=1, padx=5, pady=5)

Label(frame_inputs, text="المصاريف بالدينار:", bg="#f0f0f0", font=font_label).grid(row=1, column=0, sticky='e', padx=5, pady=5)
entry_expenses = Entry(frame_inputs, font=font_entry)
entry_expenses.grid(row=1, column=1, padx=5, pady=5)

Label(frame_inputs, text="قيمة السلعة الإجمالية باليوان:", bg="#f0f0f0", font=font_label).grid(row=2, column=0, sticky='e', padx=5, pady=5)
entry_total_yuan = Entry(frame_inputs, font=font_entry)
entry_total_yuan.grid(row=2, column=1, padx=5, pady=5)

Button(root, text="🔢 احسب السعر والمعامل", command=calculate,
       bg="#28a745", fg="white", font=font_button, width=30).pack(pady=10)

lbl_result = Label(root, text="", bg="#f0f0f0", fg="blue", font=("Arial", 12, "bold"))
lbl_result.pack()

# نتائج
frame_results = Frame(root, bg="#f0f0f0")
frame_results.pack(pady=10)

Label(frame_results, text="💰 السعر الكامل بالدينار:", bg="#f0f0f0", font=font_label).grid(row=0, column=0, sticky='e', padx=5, pady=5)
entry_result_total = Entry(frame_results, font=font_entry)
entry_result_total.grid(row=0, column=1, padx=5, pady=5)

Label(frame_results, text="⚙️ المعامل:", bg="#f0f0f0", font=font_label).grid(row=1, column=0, sticky='e', padx=5, pady=5)
entry_result_factor = Entry(frame_results, font=font_entry)
entry_result_factor.grid(row=1, column=1, padx=5, pady=5)

Button(root, text="💾 حفظ الملف الجديد", command=save_file,
       bg="#ffc107", font=font_button, width=30).pack(pady=10)

root.mainloop()
