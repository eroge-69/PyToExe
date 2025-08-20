import os
import tkinter as tk
from tkinter import messagebox
from tkinterdnd2 import TkinterDnD, DND_FILES
import PyPDF2
import win32com.client

# -------- دوال قراءة الملفات -------- #

def count_pdf_pages(path):
    try:
        with open(path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            return len(reader.pages)
    except:
        return 0

def count_word_pages(path):
    try:
        word = win32com.client.Dispatch("Word.Application")
        doc = word.Documents.Open(path, ReadOnly=True)
        pages = doc.ComputeStatistics(2)
        doc.Close()
        word.Quit()
        return pages
    except:
        return 0

def count_ppt_slides(path):
    try:
        powerpoint = win32com.client.Dispatch("PowerPoint.Application")
        presentation = powerpoint.Presentations.Open(path, WithWindow=False)
        slides = presentation.Slides.Count
        presentation.Close()
        powerpoint.Quit()
        return slides
    except:
        return 0

# -------- حساب السعر -------- #

def calculate_price(doc_files, slide_files, mode):
    total_pages = 0
    total_slides = 0
    pdf_count = 0
    word_count = 0
    ppt_count = 0
    pdf_slide_count = 0

    # معالجة PDF/Word
    for f in doc_files:
        ext = os.path.splitext(f)[1].lower()
        if ext == ".pdf":
            pages = count_pdf_pages(f)
            pdf_count += 1
        elif ext in [".doc", ".docx"]:
            pages = count_word_pages(f)
            word_count += 1
        else:
            pages = 0

        # تعديل العدد ليصبح زوجي
        if pages % 2 != 0:
            pages += 1

        total_pages += pages

    # معالجة PPT أو PDF سلايدات
    for f in slide_files:
        ext = os.path.splitext(f)[1].lower()
        if ext in [".ppt", ".pptx"]:
            slides = count_ppt_slides(f)
            ppt_count += 1
        elif ext == ".pdf":
            slides = count_pdf_pages(f)
            pdf_slide_count += 1
        else:
            slides = 0

        # تعديل العدد ليصبح من مضاعفات 4
        if slides % 4 != 0:
            slides += (4 - (slides % 4))

        total_slides += slides

    # حساب السعر
    price = 0
    if mode == "bw":
        if total_pages > 0:
            price += ((total_pages + 9)//10) * 250
        if total_slides > 0:
            price += ((total_slides + 19)//20) * 250
    elif mode == "color":
        if total_pages > 0:
            price += ((total_pages + 5)//6) * 250
        if total_slides > 0:
            price += ((total_slides + 11)//12) * 250

    total_doc_files = pdf_count + word_count
    total_slide_files = ppt_count + pdf_slide_count

    return total_doc_files, total_pages, total_slide_files, total_slides, price

# -------- الواجهة الرسومية -------- #

class PrintCalculatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("حاسبة سعر الطباعة")
        self.doc_files = []
        self.slide_files = []

        tk.Label(root, text="اسحب ملفات PDF/Word إلى المربع الأول:").pack()
        self.doc_box = tk.Listbox(root, width=60, height=6, bg="#f0f0f0")
        self.doc_box.pack(pady=5)

        tk.Label(root, text="اسحب ملفات PPT أو PDF سلايدات إلى المربع الثاني:").pack()
        self.slide_box = tk.Listbox(root, width=60, height=6, bg="#e8f8ff")
        self.slide_box.pack(pady=5)

        # دعم السحب والإفلات
        self.doc_box.drop_target_register(DND_FILES)
        self.doc_box.dnd_bind('<<Drop>>', self.drop_docs)
        self.slide_box.drop_target_register(DND_FILES)
        self.slide_box.dnd_bind('<<Drop>>', self.drop_slides)

        self.mode_var = tk.StringVar(value="bw")
        self.bw_radio = tk.Radiobutton(root, text="أبيض وأسود", variable=self.mode_var, value="bw")
        self.color_radio = tk.Radiobutton(root, text="ملون", variable=self.mode_var, value="color")
        self.bw_radio.pack()
        self.color_radio.pack()

        self.calc_btn = tk.Button(root, text="احسب السعر", command=self.calculate)
        self.calc_btn.pack(pady=10)

        self.result_label = tk.Label(root, text="", justify="left")
        self.result_label.pack(pady=10)

        self.restart_btn = tk.Button(root, text="إعادة تشغيل", command=self.restart)
        self.restart_btn.pack(pady=5)

    def drop_docs(self, event):
        files = self.root.splitlist(event.data)
        for f in files:
            if f not in self.doc_files:
                self.doc_files.append(f)
                self.doc_box.insert(tk.END, f)

    def drop_slides(self, event):
        files = self.root.splitlist(event.data)
        for f in files:
            if f not in self.slide_files:
                self.slide_files.append(f)
                self.slide_box.insert(tk.END, f)

    def calculate(self):
        if not self.doc_files and not self.slide_files:
            messagebox.showwarning("تحذير", "الرجاء إضافة ملفات أولاً.")
            return
        mode = self.mode_var.get()
        total_docs, total_pages, total_slide_files, total_slides, price = calculate_price(self.doc_files, self.slide_files, mode)
        self.result_label.config(text=f"عدد ملفات PDF/Word: {total_docs}\n"
                                      f"إجمالي الصفحات: {total_pages}\n"
                                      f"عدد ملفات PPT/PDF Slides: {total_slide_files}\n"
                                      f"إجمالي السلايدات: {total_slides}\n"
                                      f"السعر الكلي: {price} دينار")

    def restart(self):
        self.doc_files = []
        self.slide_files = []
        self.doc_box.delete(0, tk.END)
        self.slide_box.delete(0, tk.END)
        self.result_label.config(text="")
        self.mode_var.set("bw")

# -------- تشغيل البرنامج -------- #

if __name__ == "__main__":
    root = TkinterDnD.Tk()
    app = PrintCalculatorApp(root)
    root.mainloop()
