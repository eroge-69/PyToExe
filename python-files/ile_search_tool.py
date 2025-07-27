import os
import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
from tkinter.scrolledtext import ScrolledText

def search_files_and_folders(search_terms, save_path):
    search_root = "C:\\"
    results = []

    for root, dirs, files in os.walk(search_root):
        for name in files:
            if any(term.lower() in name.lower() for term in search_terms):
                path = os.path.join(root, name)
                try:
                    size = os.path.getsize(path)
                except:
                    size = 0
                results.append({
                    "الاسم": name,
                    "المسار": path,
                    "النوع": "ملف",
                    "الحجم (بايت)": size
                })

        for name in dirs:
            if any(term.lower() in name.lower() for term in search_terms):
                path = os.path.join(root, name)
                results.append({
                    "الاسم": name,
                    "المسار": path,
                    "النوع": "مجلد",
                    "الحجم (بايت)": "-"
                })

    df = pd.DataFrame(results)
    output_file = os.path.join(save_path, "نتائج_البحث.xlsx")
    df.to_excel(output_file, index=False)
    return output_file

def run_gui():
    def browse_save_location():
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            save_path_var.set(folder_selected)

    def start_search():
        terms = search_input.get("1.0", tk.END).strip().splitlines()
        save_path = save_path_var.get()
        if not terms or not save_path:
            messagebox.showerror("خطأ", "يرجى إدخال كلمات البحث وتحديد مكان الحفظ.")
            return
        output = search_files_and_folders(terms, save_path)
        messagebox.showinfo("تم", f"تم حفظ النتائج في:\n{output}")

    window = tk.Tk()
    window.title("البحث عن الملفات والمجلدات")

    tk.Label(window, text="أدخل كلمات البحث (كل سطر كلمة):").pack(pady=5)
    search_input = ScrolledText(window, width=50, height=10)
    search_input.pack(pady=5)

    save_path_var = tk.StringVar()
    tk.Button(window, text="اختيار مكان الحفظ", command=browse_save_location).pack(pady=5)
    tk.Entry(window, textvariable=save_path_var, width=60).pack(pady=5)

    tk.Button(window, text="بدء البحث", command=start_search, bg="green", fg="white").pack(pady=10)

    window.mainloop()

run_gui()
