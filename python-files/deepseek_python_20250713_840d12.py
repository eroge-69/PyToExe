import PyPDF2
from collections import Counter
import tkinter as tk
from tkinter import filedialog, messagebox

def count_words():
    pdf_path = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
    if not pdf_path:
        return
    
    target_words = entry.get().split(',')
    target_words = [word.strip().lower() for word in target_words]
    
    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = ""
            for page in reader.pages:
                text += page.extract_text() or ""
            
            words = text.lower().split()
            word_counts = Counter(words)
            
            result = "\n".join([f"{word}: {word_counts.get(word, 0)}" for word in target_words])
            messagebox.showinfo("نتایج", result)
    except Exception as e:
        messagebox.showerror("خطا", f"خطا در پردازش فایل:\n{str(e)}")

app = tk.Tk()
app.title("شمارش کلمات در PDF")

tk.Label(app, text="کلمات مورد نظر (با کاما جدا کنید):").pack()
entry = tk.Entry(app, width=50)
entry.pack()

tk.Button(app, text="انتخاب فایل PDF و شمارش", command=count_words).pack()

app.mainloop()