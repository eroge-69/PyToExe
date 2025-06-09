
import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import docx
import openpyxl
import subprocess

def search_files(directory, keyword):
    results = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            filepath = os.path.join(root, file)
            if file.endswith(".docx"):
                try:
                    doc = docx.Document(filepath)
                    for para in doc.paragraphs:
                        if keyword in para.text:
                            results.append(filepath)
                            break
                except:
                    pass
            elif file.endswith(".xlsx"):
                try:
                    wb = openpyxl.load_workbook(filepath)
                    for sheet in wb:
                        for row in sheet.iter_rows():
                            for cell in row:
                                if cell.value and keyword in str(cell.value):
                                    results.append(filepath)
                                    raise StopIteration
                except StopIteration:
                    pass
                except:
                    pass
    return results

def browse_folder():
    folder = filedialog.askdirectory()
    if folder:
        folder_var.set(folder)

def start_search():
    folder = folder_var.get()
    keyword = keyword_entry.get()
    result_list.delete(0, tk.END)
    if not os.path.isdir(folder):
        messagebox.showerror("خطأ", "المجلد غير صالح")
        return
    results = search_files(folder, keyword)
    if results:
        for res in results:
            result_list.insert(tk.END, res)
    else:
        messagebox.showinfo("نتيجة البحث", "لم يتم العثور على نتائج")

def open_selected_file(event):
    selection = result_list.curselection()
    if selection:
        filepath = result_list.get(selection[0])
        subprocess.Popen(['start', '', filepath], shell=True)

root = tk.Tk()
root.title("الدائرة الأولى")
root.geometry("600x400")

folder_var = tk.StringVar()

frame = ttk.Frame(root, padding="10")
frame.pack(fill=tk.BOTH, expand=True)

ttk.Label(frame, text="ادخل رقم أو اسم للبحث:").pack(anchor=tk.W)
keyword_entry = ttk.Entry(frame, width=50)
keyword_entry.pack(fill=tk.X)

ttk.Label(frame, text="اختر المجلد:").pack(anchor=tk.W, pady=(10,0))
folder_frame = ttk.Frame(frame)
folder_frame.pack(fill=tk.X)
ttk.Entry(folder_frame, textvariable=folder_var, width=40).pack(side=tk.LEFT, fill=tk.X, expand=True)
ttk.Button(folder_frame, text="تصفح", command=browse_folder).pack(side=tk.RIGHT)

ttk.Button(frame, text="بحث", command=start_search).pack(pady=10)

result_list = tk.Listbox(frame, height=10)
result_list.pack(fill=tk.BOTH, expand=True)
result_list.bind('<Double-1>', open_selected_file)

root.mainloop()
