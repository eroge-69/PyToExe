#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import cv2
import numpy as np
import os
from PIL import Image, ImageTk

class DesignAnalyzerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("أداة تحليل التصميم - Design Analyzer")
        self.root.geometry("800x600")
        self.root.configure(bg='#f0f0f0')
        
        # متغيرات
        self.current_image_path = None
        
        # إنشاء الواجهة
        self.create_widgets()
        
    def create_widgets(self):
        # العنوان الرئيسي
        title_label = tk.Label(
            self.root, 
            text="أداة تحليل التصميم", 
            font=("Arial", 20, "bold"),
            bg='#f0f0f0',
            fg='#333333'
        )
        title_label.pack(pady=20)
        
        # زر اختيار الصورة
        select_button = tk.Button(
            self.root,
            text="اختر صورة التصميم",
            font=("Arial", 12),
            bg='#4CAF50',
            fg='white',
            padx=20,
            pady=10,
            command=self.select_image
        )
        select_button.pack(pady=10)
        
        # عرض مسار الصورة المختارة
        self.path_label = tk.Label(
            self.root,
            text="لم يتم اختيار صورة بعد",
            font=("Arial", 10),
            bg='#f0f0f0',
            fg='#666666'
        )
        self.path_label.pack(pady=5)
        
        # زر التحليل
        self.analyze_button = tk.Button(
            self.root,
            text="تحليل التصميم",
            font=("Arial", 12),
            bg='#2196F3',
            fg='white',
            padx=20,
            pady=10,
            command=self.analyze_design,
            state='disabled'
        )
        self.analyze_button.pack(pady=10)
        
        # منطقة عرض النتائج
        results_label = tk.Label(
            self.root,
            text="نتائج التحليل:",
            font=("Arial", 14, "bold"),
            bg='#f0f0f0',
            fg='#333333'
        )
        results_label.pack(pady=(20, 5))
        
        # صندوق النص لعرض النتائج
        self.results_text = scrolledtext.ScrolledText(
            self.root,
            width=80,
            height=20,
            font=("Arial", 10),
            wrap=tk.WORD
        )
        self.results_text.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)
        
        # زر حفظ النتائج
        save_button = tk.Button(
            self.root,
            text="حفظ النتائج",
            font=("Arial", 10),
            bg='#FF9800',
            fg='white',
            padx=15,
            pady=5,
            command=self.save_results
        )
        save_button.pack(pady=10)
        
    def select_image(self):
        """اختيار صورة للتحليل"""
        file_path = filedialog.askopenfilename(
            title="اختر صورة التصميم",
            filetypes=[
                ("ملفات الصور", "*.png *.jpg *.jpeg *.bmp *.tiff *.gif"),
                ("جميع الملفات", "*.*")
            ]
        )
        
        if file_path:
            self.current_image_path = file_path
            # عرض اسم الملف فقط بدلاً من المسار الكامل
            filename = os.path.basename(file_path)
            self.path_label.config(text=f"الصورة المختارة: {filename}")
            self.analyze_button.config(state='normal')
            
    def analyze_design(self):
        """تحليل التصميم المختار"""
        if not self.current_image_path:
            messagebox.showerror("خطأ", "يرجى اختيار صورة أولاً")
            return
            
        try:
            # مسح النتائج السابقة
            self.results_text.delete(1.0, tk.END)
            
            # قراءة الصورة
            img = cv2.imread(self.current_image_path)
            if img is None:
                messagebox.showerror("خطأ", "لا يمكن قراءة الصورة المختارة")
                return
                
            # إجراء التحليل
            results = self.perform_analysis(img)
            
            # عرض النتائج
            self.results_text.insert(tk.END, results)
            
        except Exception as e:
            messagebox.showerror("خطأ", f"حدث خطأ أثناء التحليل: {str(e)}")
            
    def perform_analysis(self, img):
        """إجراء تحليل التصميم"""
        results = f"تحليل التصميم: {os.path.basename(self.current_image_path)}\n"
        results += "=" * 50 + "\n\n"
        
        # 1. تحليل الألوان
        results += "--- تحليل الألوان ---\n"
        results += self.analyze_colors(img) + "\n\n"
        
        # 2. تحليل التنسيق بين العناصر
        results += "--- تحليل التنسيق بين العناصر ---\n"
        results += self.analyze_coordination(img) + "\n\n"
        
        # 3. تحليل المحاذاة
        results += "--- تحليل المحاذاة ---\n"
        results += self.analyze_alignment(img) + "\n\n"
        
        return results
        
    def analyze_colors(self, img):
        """تحليل الألوان"""
        results = ""
        
        # تحويل الصورة إلى مساحة ألوان HSV
        hsv_img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        
        # متوسط درجة اللون (Hue)
        avg_hue = np.mean(hsv_img[:,:,0])
        results += f"متوسط درجة اللون (Hue): {avg_hue:.2f}\n"
        
        # متوسط التشبع (Saturation)
        avg_saturation = np.mean(hsv_img[:,:,1])
        results += f"متوسط التشبع (Saturation): {avg_saturation:.2f}\n"
        
        # متوسط القيمة (Value)
        avg_value = np.mean(hsv_img[:,:,2])
        results += f"متوسط القيمة (Value): {avg_value:.2f}\n"
        
        # تحليل التباين
        gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        contrast = np.std(gray_img)
        results += f"التباين (Contrast): {contrast:.2f}\n"
        
        # تحليل التناسق اللوني
        unique_colors = np.unique(img.reshape(-1, img.shape[2]), axis=0)
        results += f"عدد الألوان الفريدة (تقريبي): {len(unique_colors)}\n"
        
        if len(unique_colors) < 50:
            results += "ملاحظة: قد يشير عدد الألوان المنخفض إلى تناسق لوني جيد.\n"
        else:
            results += "ملاحظة: قد يشير عدد الألوان المرتفع إلى تعقيد لوني، قد يحتاج إلى مراجعة التناسق.\n"
            
        return results
        
    def analyze_coordination(self, img):
        """تحليل التنسيق بين العناصر"""
        results = ""
        
        edges = cv2.Canny(img, 100, 200)
        num_edges_pixels = np.sum(edges > 0)
        results += f"عدد بكسلات الحواف المكتشفة: {num_edges_pixels}\n"
        
        if num_edges_pixels > (img.shape[0] * img.shape[1] * 0.05):
            results += "ملاحظة: وجود حواف واضحة قد يشير إلى عناصر محددة.\n"
        else:
            results += "ملاحظة: قد تكون العناصر أقل تحديدًا أو التصميم أكثر سلاسة.\n"
            
        results += "يتطلب تحليل التنسيق المتقدم بين العناصر اكتشاف الكائنات وتقسيم الصور.\n"
        
        return results
        
    def analyze_alignment(self, img):
        """تحليل المحاذاة"""
        results = ""
        
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 50, 150, apertureSize=3)
        lines = cv2.HoughLinesP(edges, 1, np.pi/180, 100, minLineLength=100, maxLineGap=10)
        
        horizontal_lines = 0
        vertical_lines = 0
        
        if lines is not None:
            for line in lines:
                x1, y1, x2, y2 = line[0]
                if abs(x2 - x1) > abs(y2 - y1):  # خط أفقي
                    horizontal_lines += 1
                else:  # خط عمودي
                    vertical_lines += 1
                    
        results += f"عدد الخطوط الأفقية المكتشفة: {horizontal_lines}\n"
        results += f"عدد الخطوط العمودية المكتشفة: {vertical_lines}\n"
        
        if horizontal_lines > 0 and vertical_lines > 0:
            results += "ملاحظة: وجود خطوط أفقية وعمودية قد يشير إلى بنية محاذاة جيدة.\n"
        else:
            results += "ملاحظة: قد يكون التصميم أقل اعتمادًا على المحاذاة الشبكية الصارمة.\n"
            
        results += "يتطلب تحليل المحاذاة المتقدم اكتشاف الكائنات وتحديد محاذاتها النسبية.\n"
        
        return results
        
    def save_results(self):
        """حفظ النتائج في ملف نصي"""
        results_content = self.results_text.get(1.0, tk.END)
        
        if not results_content.strip():
            messagebox.showwarning("تحذير", "لا توجد نتائج لحفظها")
            return
            
        file_path = filedialog.asksaveasfilename(
            title="حفظ النتائج",
            defaultextension=".txt",
            filetypes=[("ملفات نصية", "*.txt"), ("جميع الملفات", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(results_content)
                messagebox.showinfo("نجح", "تم حفظ النتائج بنجاح")
            except Exception as e:
                messagebox.showerror("خطأ", f"فشل في حفظ الملف: {str(e)}")

def main():
    root = tk.Tk()
    app = DesignAnalyzerGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()

