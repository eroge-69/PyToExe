import fitz
import os
import re
import shutil
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import subprocess
import sys

class PDFRenamerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PDF Renamer")
        self.root.geometry("700x500")
        
        # متغیرهای مسیرها
        self.input_folder = tk.StringVar()
        self.output_folder = tk.StringVar()
        
        # تنظیم مستطیل برش (مقادیر پیش‌فرض)
        self.clip_rect = fitz.Rect(150, 90, 250, 100)
        
        self.setup_ui()
    
    def setup_ui(self):
        # فریم برای فولدرها
        folder_frame = ttk.LabelFrame(self.root, text="Folder Settings", padding="10")
        folder_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # فولدر ورودی
        ttk.Label(folder_frame, text="Input Folder:").grid(row=0, column=0, sticky=tk.W, pady=2)
        input_entry = ttk.Entry(folder_frame, textvariable=self.input_folder, width=60)
        input_entry.grid(row=0, column=1, padx=5, pady=2)
        ttk.Button(folder_frame, text="Browse...", command=self.browse_input_folder).grid(row=0, column=2, pady=2)
        
        # فولدر خروجی
        ttk.Label(folder_frame, text="Output Folder:").grid(row=1, column=0, sticky=tk.W, pady=2)
        output_entry = ttk.Entry(folder_frame, textvariable=self.output_folder, width=60)
        output_entry.grid(row=1, column=1, padx=5, pady=2)
        ttk.Button(folder_frame, text="Browse...", command=self.browse_output_folder).grid(row=1, column=2, pady=2)
        
        # تنظیمات مستطیل برش
        rect_frame = ttk.LabelFrame(self.root, text="Text Extraction Area", padding="10")
        rect_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(rect_frame, text="Coordinates (x0, y0, x1, y1):").grid(row=0, column=0, sticky=tk.W)
        self.rect_entry = ttk.Entry(rect_frame, width=30)
        self.rect_entry.grid(row=0, column=1, padx=5, sticky=tk.W)
        self.rect_entry.insert(0, "150,90,250,100")
        
        # فریم برای کنترل‌ها
        control_frame = ttk.Frame(self.root, padding="10")
        control_frame.pack(fill=tk.X)
        
        # دکمه شروع پردازش
        self.process_btn = ttk.Button(control_frame, text="Start Processing", command=self.process_pdfs)
        self.process_btn.pack(side=tk.LEFT, padx=5)
        
        # دکمه باز کردن پوشه (غیرفعال در ابتدا)
        self.open_folder_btn = ttk.Button(control_frame, text="Open Output Folder", 
                                 command=self.open_output_folder, state=tk.DISABLED)
        self.open_folder_btn.pack(side=tk.LEFT, padx=5)
        
        # پیشرفت بار
        progress_frame = ttk.Frame(self.root, padding="10")
        progress_frame.pack(fill=tk.X, padx=10, pady=5)
        
        progress_label = ttk.Label(progress_frame, text="Progress:")
        progress_label.pack(anchor=tk.W)
        
        self.progress_bar = ttk.Progressbar(progress_frame, orient=tk.HORIZONTAL, mode='determinate')
        self.progress_bar.pack(fill=tk.X, pady=5)
        
        # ناحیه گزارش
        log_frame = ttk.LabelFrame(self.root, text="Processing Log", padding="10")
        log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # جعبه متن برای گزارش‌ها
        self.log_text = tk.Text(log_frame, wrap=tk.WORD)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # افزودن اسکرول بار
        scrollbar = ttk.Scrollbar(log_frame, command=self.log_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.config(yscrollcommand=scrollbar.set)
        
        # وضعیت پایین پنجره
        self.status_var = tk.StringVar(value="Ready to start processing")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def browse_input_folder(self):
        folder = filedialog.askdirectory(title="Select Input Folder")
        if folder:
            self.input_folder.set(os.path.normpath(folder))
    
    def browse_output_folder(self):
        folder = filedialog.askdirectory(title="Select Output Folder")
        if folder:
            self.output_folder.set(os.path.normpath(folder))
    
    def process_pdfs(self):
        # غیرفعال کردن دکمه حین پردازش
        self.process_btn.config(state=tk.DISABLED)
        self.open_folder_btn.config(state=tk.DISABLED)
        self.status_var.set("Processing...")
        self.root.update()
        
        # دریافت مسیرهای فعلی
        input_folder = self.input_folder.get()
        output_folder = self.output_folder.get()
        
        # اعتبارسنجی مسیرها
        if not input_folder or not output_folder:
            messagebox.showerror("Error", "Please select both input and output folders")
            self.process_btn.config(state=tk.NORMAL)
            self.status_var.set("Ready to start processing")
            return
        
        # دریافت مستطیل برش
        try:
            coords = [int(x.strip()) for x in self.rect_entry.get().split(',')]
            if len(coords) != 4:
                raise ValueError
            self.clip_rect = fitz.Rect(coords[0], coords[1], coords[2], coords[3])
        except:
            messagebox.showerror("Error", "Invalid coordinates format. Use: x0,y0,x1,y1")
            self.process_btn.config(state=tk.NORMAL)
            self.status_var.set("Ready to start processing")
            return
        
        # ایجاد پوشه خروجی اگر وجود نداشته باشد
        output_folder = os.path.normpath(output_folder)
        os.makedirs(output_folder, exist_ok=True)
        self.output_folder.set(output_folder)  # ذخیره مسیر نرمال‌سازی شده

        try:
            # لیست فایل‌های PDF
            pdf_files = [f for f in os.listdir(input_folder) if f.lower().endswith('.pdf')]
            
            if not pdf_files:
                messagebox.showinfo("Information", "No PDF files found in input folder")
                self.process_btn.config(state=tk.NORMAL)
                self.status_var.set("Ready to start processing")
                return
            
            # شمارنده‌ها
            success_count = 0
            error_count = 0
            duplicate_count = 0
            
            # پیشرفت بار
            self.progress_bar['maximum'] = len(pdf_files)
            self.progress_bar['value'] = 0
            
            # پاک کردن لاگ قبلی
            self.log_text.delete(1.0, tk.END)
            self.log_text.insert(tk.END, f"Starting processing for {len(pdf_files)} files...\n")
            self.log_text.insert(tk.END, f"Input folder: {input_folder}\n")
            self.log_text.insert(tk.END, f"Output folder: {output_folder}\n")
            self.log_text.insert(tk.END, f"Extraction area: {self.clip_rect}\n\n")
            self.root.update()
            
            for filename in pdf_files:
                file_path = os.path.join(input_folder, filename)
                
                try:
                    doc = fitz.open(file_path)
                    page = doc[0]
                    text = page.get_text("text", clip=self.clip_rect)
                    doc.close()
                    
                    clean_text = re.sub(r'\s+', '', text)
                    
                    if len(clean_text) < 13:
                        self.log_text.insert(tk.END, f"Error in {filename}: Extracted text too short ({clean_text})\n")
                        error_count += 1
                        continue
                    
                    # ساخت نام جدید
                    extname = clean_text[11] + clean_text[12] + clean_text[7:10] + "-" + clean_text[0:2]
                    base_name = extname + ".pdf"
                    output_path = os.path.join(output_folder, base_name)
                    
                    # مدیریت فایل‌های تکراری
                    counter = 1
                    while os.path.exists(output_path):
                        base, ext = os.path.splitext(base_name)
                        output_path = os.path.join(output_folder, f"{base}_{counter}{ext}")
                        counter += 1
                    
                    # انتقال فایل به مسیر جدید با نام جدید
                    shutil.copy2(file_path, output_path)
                    
                    # گزارش نتیجه
                    if counter > 1:
                        new_filename = os.path.basename(output_path)
                        self.log_text.insert(tk.END, f"Renamed (duplicate): {filename} -> {new_filename}\n")
                        duplicate_count += 1
                    else:
                        self.log_text.insert(tk.END, f"Renamed: {filename} -> {base_name}\n")
                    
                    success_count += 1
                
                except Exception as e:
                    self.log_text.insert(tk.END, f"Error processing {filename}: {str(e)}\n")
                    error_count += 1
                
                # به‌روزرسانی پیشرفت بار
                self.progress_bar['value'] += 1
                self.root.update_idletasks()
            
            # نمایش گزارش نهایی
            self.log_text.insert(tk.END, "\n" + "=" * 50 + "\n")
            self.log_text.insert(tk.END, f"Processing Summary:\n")
            self.log_text.insert(tk.END, f"Total PDFs processed: {len(pdf_files)}\n")
            self.log_text.insert(tk.END, f"Successfully renamed: {success_count}\n")
            self.log_text.insert(tk.END, f"  - Unique files: {success_count - duplicate_count}\n")
            self.log_text.insert(tk.END, f"  - Duplicate handled: {duplicate_count}\n")
            self.log_text.insert(tk.END, f"Errors encountered: {error_count}\n")
            self.log_text.insert(tk.END, f"Output folder: {output_folder}\n")
            self.log_text.insert(tk.END, "=" * 50 + "\n")
            
            # فعال کردن دکمه باز کردن پوشه
            self.open_folder_btn.config(state=tk.NORMAL)
            self.status_var.set("Processing completed successfully")
        
        except Exception as e:
            messagebox.showerror("Processing Error", f"An error occurred during processing: {str(e)}")
            self.status_var.set("Processing failed")
        
        # فعال کردن دکمه پردازش
        self.process_btn.config(state=tk.NORMAL)
    
    def open_output_folder(self):
        output_folder = self.output_folder.get()
        if not output_folder:
            messagebox.showwarning("Warning", "Output folder not selected")
            return
            
        # تبدیل به مسیر مطلق و نرمال‌سازی
        abs_path = os.path.abspath(output_folder)
        
        if not os.path.exists(abs_path):
            messagebox.showwarning("Warning", f"Folder does not exist:\n{abs_path}")
            return

        try:
            # باز کردن پوشه خروجی در File Explorer
            if sys.platform == "win32":
                os.startfile(abs_path)
            elif sys.platform == "darwin":
                subprocess.Popen(["open", abs_path])
            else:  # لینوکس و سایر سیستم‌ها
                subprocess.Popen(["xdg-open", abs_path])
        except Exception as e:
            messagebox.showerror("Error", f"Could not open folder: {e}")

# ایجاد و اجرای برنامه
if __name__ == "__main__":
    root = tk.Tk()
    app = PDFRenamerApp(root)
    root.mainloop()