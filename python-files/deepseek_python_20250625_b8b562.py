import tkinter as tk
from tkinter import ttk, filedialog
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
import os

class ReceiptApp:
    def __init__(self, root):
        self.root = root
        root.title("ثلاجة السيلي - فاتورة")
        root.geometry("500x450")
        root.configure(bg="#f0f0f0")
        
        # Header
        header = tk.Label(root, text="ثلاجة السيلي", font=("Arial", 18, "bold"), bg="#f0f0f0")
        header.pack(pady=(15, 10))
        
        # Create table frame
        table_frame = tk.Frame(root, bg="#f0f0f0")
        table_frame.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)
        
        # Create table
        self.entries = []
        for i in range(4):
            row_frame = tk.Frame(table_frame, bg="#f0f0f0")
            row_frame.pack(fill=tk.X, pady=2)
            
            date_label = tk.Label(row_frame, text="2025/6/", width=10, anchor="e", 
                                 font=("Arial", 12), bg="#f0f0f0")
            date_label.pack(side=tk.LEFT, padx=(0, 10))
            
            entry = tk.Entry(row_frame, font=("Arial", 12), width=20)
            entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
            self.entries.append(entry)
        
        # Separator
        separator = ttk.Separator(table_frame, orient="horizontal")
        separator.pack(fill=tk.X, pady=10)
        
        # Total and payment date
        total_frame = tk.Frame(table_frame, bg="#f0f0f0")
        total_frame.pack(fill=tk.X, pady=2)
        
        tk.Label(total_frame, text="المجموع:", width=10, anchor="e", 
                font=("Arial", 12), bg="#f0f0f0").pack(side=tk.LEFT, padx=(0, 10))
        self.total_entry = tk.Entry(total_frame, font=("Arial", 12), width=20)
        self.total_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        payment_frame = tk.Frame(table_frame, bg="#f0f0f0")
        payment_frame.pack(fill=tk.X, pady=2)
        
        tk.Label(payment_frame, text="تم الدفع بتاريخ:", width=10, anchor="e", 
                font=("Arial", 12), bg="#f0f0f0").pack(side=tk.LEFT, padx=(0, 10))
        self.date_entry = tk.Entry(payment_frame, font=("Arial", 12), width=20)
        self.date_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Buttons
        btn_frame = tk.Frame(root, bg="#f0f0f0")
        btn_frame.pack(pady=20)
        
        print_btn = tk.Button(btn_frame, text="طباعة الفاتورة", font=("Arial", 12), 
                            command=self.generate_pdf, bg="#4CAF50", fg="white")
        print_btn.pack(side=tk.LEFT, padx=10)
        
        clear_btn = tk.Button(btn_frame, text="مسح النموذج", font=("Arial", 12), 
                            command=self.clear_form, bg="#f44336", fg="white")
        clear_btn.pack(side=tk.LEFT, padx=10)
    
    def clear_form(self):
        for entry in self.entries:
            entry.delete(0, tk.END)
        self.total_entry.delete(0, tk.END)
        self.date_entry.delete(0, tk.END)
    
    def generate_pdf(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")],
            title="حفظ الفاتورة كـ PDF"
        )
        
        if not file_path:
            return
        
        c = canvas.Canvas(file_path, pagesize=A4)
        width, height = A4
        
        # Header
        c.setFont("Helvetica-Bold", 18)
        c.drawCentredString(width/2, height-50, "ثلاجة السيلي")
        
        # Table
        c.setFont("Helvetica", 12)
        y_position = height - 100
        
        # Draw table rows
        for i in range(4):
            date_text = "2025/6/" + (self.entries[i].get() or "")
            c.drawString(100, y_position, date_text)
            y_position -= 30
        
        # Separator
        c.line(100, y_position-10, width-100, y_position-10)
        y_position -= 30
        
        # Total
        c.drawString(100, y_position, "المجموع: " + (self.total_entry.get() or ""))
        y_position -= 30
        
        # Payment date
        c.drawString(100, y_position, "تم الدفع بتاريخ: " + (self.date_entry.get() or ""))
        
        c.save()
        os.startfile(file_path)

if __name__ == "__main__":
    root = tk.Tk()
    app = ReceiptApp(root)
    root.mainloop()