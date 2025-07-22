# -*- coding: utf-8 -*-

# =============================================================================
# برنامج Magharaby Attendance Test
# الإصدار: 1.9
# المطور: Gemini
# الوصف: إعادة تفعيل الأصوات المخصصة مع مسار ديناميكي والاحتفاظ بـ winsound كخيار احتياطي.
# 
# المكتبات المطلوبة:
# pip install playsound==1.2.2 numpy opencv-python pyzbar pandas openpyxl reportlab arabic_reshaper python-bidi Pillow
# =============================================================================

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import cv2
from pyzbar import pyzbar
import pandas as pd
import threading
from PIL import Image, ImageTk
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib import colors
import arabic_reshaper
from bidi.algorithm import get_display
import os
import sys
import time
import numpy as np
import winsound 
from playsound import playsound # <-- إعادة استخدام المكتبة للأصوات المخصصة

# --- إعدادات أساسية ---
APP_TITLE = "Magharaby Attendance Test"
WINDOW_SIZE = "1000x720"

# --- تعريف الألوان والخطوط للواجهة ---
COLOR_BG = "#2E2E2E"
COLOR_FRAME = "#3A3A3A"
COLOR_TEXT = "#EAEAEA"
COLOR_SUCCESS = "#4CAF50"
COLOR_ERROR = "#F44336"
COLOR_DUPLICATE = "#FFC107"
COLOR_ACCENT = "#2196F3"
FONT_MAIN = ("Tahoma", 12)
FONT_HEADER = ("Tahoma", 16, "bold")
FONT_COUNTER = ("Tahoma", 24, "bold")
FONT_STATUS = ("Courier", 18, "bold")

class App:
    def __init__(self, master):
        self.master = master
        self.setup_window()
        self.initialize_variables()
        self.create_styles()
        self.create_widgets()
        self.master.protocol("WM_DELETE_WINDOW", self.on_closing)

    def setup_window(self):
        """إعداد النافذة الرئيسية للتطبيق."""
        self.master.title(APP_TITLE)
        self.master.geometry(WINDOW_SIZE)
        self.master.configure(bg=COLOR_BG)

    def initialize_variables(self):
        """تهيئة جميع متغيرات الحالة والعدادات."""
        self.all_ids = set()
        self.scanned_ids = set()
        self.scanned_log = []
        self.video_thread = None
        self.stop_video_loop = False
        self.camera_source = 0

        # العدادات
        self.total_scanned_count = tk.IntVar(value=0)
        self.correct_count = tk.IntVar(value=0)
        self.duplicate_count = tk.IntVar(value=0)
        self.error_count = tk.IntVar(value=0)
        self.fr_count = tk.IntVar(value=0)
        self.gr_count = tk.IntVar(value=0)
        self.pa_count = tk.IntVar(value=0)
        
        self.last_scan_text = tk.StringVar(value="---")
        self.last_scan_status_icon = tk.StringVar(value="⚪")
        self.last_scan_status_color = tk.StringVar(value=COLOR_TEXT)

    def create_styles(self):
        """إنشاء وتخصيص أنماط عناصر الواجهة."""
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TButton', background=COLOR_ACCENT, foreground='white', font=FONT_MAIN, borderwidth=0)
        style.map('TButton', background=[('active', '#1976D2')])
        style.configure('TFrame', background=COLOR_FRAME)
        style.configure('TLabelframe', background=COLOR_FRAME, bordercolor=COLOR_ACCENT)
        style.configure('TLabelframe.Label', background=COLOR_FRAME, foreground=COLOR_TEXT, font=FONT_MAIN)
        style.configure('Header.TLabel', background=COLOR_FRAME, foreground=COLOR_TEXT, font=FONT_HEADER)
        style.configure('Counter.TLabel', background=COLOR_FRAME, foreground=COLOR_TEXT, font=FONT_COUNTER)
        style.configure('Status.TLabel', background=COLOR_FRAME, font=FONT_STATUS)
        style.configure('Accent.TLabel', background=COLOR_FRAME, foreground=COLOR_ACCENT, font=FONT_MAIN)

    def create_widgets(self):
        """إنشاء ووضع جميع عناصر الواجهة."""
        main_frame = tk.Frame(self.master, bg=COLOR_BG)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        left_panel = ttk.Frame(main_frame, style='TFrame')
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))

        control_frame = ttk.LabelFrame(left_panel, text="لوحة التحكم", style='TLabelframe')
        control_frame.pack(fill=tk.X, pady=10)
        
        self.load_button = ttk.Button(control_frame, text="📂 تحميل ملف IDs", command=self.load_file)
        self.load_button.pack(fill=tk.X, padx=10, pady=10)
        
        self.save_button = ttk.Button(control_frame, text="💾 حفظ التقرير", command=self.save_report, state=tk.DISABLED)
        self.save_button.pack(fill=tk.X, padx=10, pady=10)

        stats_frame = ttk.LabelFrame(left_panel, text="الإحصائيات", style='TLabelframe')
        stats_frame.pack(fill=tk.BOTH, expand=True)
        
        self.create_counter_display(stats_frame, "الإجمالي", self.total_scanned_count, COLOR_TEXT)
        ttk.Separator(stats_frame, orient='horizontal').pack(fill='x', pady=5, padx=20)
        
        self.create_counter_display(stats_frame, "الصحيحة", self.correct_count, COLOR_SUCCESS)
        self.create_counter_display(stats_frame, "المكررة", self.duplicate_count, COLOR_DUPLICATE)
        self.create_counter_display(stats_frame, "الخاطئة", self.error_count, COLOR_ERROR)
        
        ttk.Separator(stats_frame, orient='horizontal').pack(fill='x', pady=10, padx=20)
        
        self.create_counter_display(stats_frame, "FR-Type", self.fr_count, COLOR_ACCENT)
        self.create_counter_display(stats_frame, "GR-Type", self.gr_count, COLOR_ACCENT)
        self.create_counter_display(stats_frame, "PA-Type", self.pa_count, COLOR_ACCENT)

        right_panel = ttk.Frame(main_frame, style='TFrame')
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        self.camera_label = tk.Label(right_panel, bg='black')
        self.camera_label.pack(fill=tk.BOTH, expand=True)

        last_scan_frame = ttk.Frame(right_panel, style='TFrame', height=80)
        last_scan_frame.pack(fill=tk.X, pady=5)
        last_scan_frame.pack_propagate(False)

        status_label = ttk.Label(last_scan_frame, textvariable=self.last_scan_status_icon, style='Status.TLabel')
        status_label.pack(side=tk.RIGHT, padx=20)
        status_label.bind("<Map>", lambda e: status_label.config(foreground=self.last_scan_status_color.get()))

        scan_text_label = ttk.Label(last_scan_frame, textvariable=self.last_scan_text, style='Status.TLabel', anchor='center')
        scan_text_label.pack(side=tk.LEFT, padx=20, fill=tk.X, expand=True)
        
    def create_counter_display(self, parent, text, variable, color):
        frame = ttk.Frame(parent, style='TFrame')
        frame.pack(fill=tk.X, padx=10, pady=5)
        label = ttk.Label(frame, text=text, style='Accent.TLabel', anchor='w')
        label.pack(side=tk.LEFT)
        counter = ttk.Label(frame, textvariable=variable, style='Counter.TLabel', anchor='e')
        counter.pack(side=tk.RIGHT)
        counter.configure(foreground=color)

    def load_file(self):
        file_path = filedialog.askopenfilename(
            title="اختر ملف IDs",
            filetypes=(("Excel files", "*.xlsx *.xls"), ("CSV files", "*.csv"), ("Text files", "*.txt"))
        )
        if not file_path: return
        try:
            if file_path.endswith(('.xlsx', '.xls')):
                df = pd.read_excel(file_path, header=None)
            elif file_path.endswith('.csv'):
                df = pd.read_csv(file_path, header=None)
            else:
                with open(file_path, 'r', encoding='utf-8') as f:
                    self.all_ids = {line.strip() for line in f if line.strip()}
                    self.reset_and_start()
                    return
            self.all_ids = set(df.iloc[:, 0].astype(str))
            self.reset_and_start()
        except Exception as e:
            messagebox.showerror("خطأ في الملف", f"فشل تحميل الملف:\n{e}")

    def reset_and_start(self):
        self.reset_state()
        self.save_button.config(state=tk.NORMAL)
        messagebox.showinfo("نجاح", f"تم تحميل {len(self.all_ids)} كود بنجاح.")
        self.start_camera_thread()

    def reset_state(self):
        self.scanned_ids.clear()
        self.scanned_log.clear()
        self.total_scanned_count.set(0)
        self.correct_count.set(0)
        self.duplicate_count.set(0)
        self.error_count.set(0)
        self.fr_count.set(0)
        self.gr_count.set(0)
        self.pa_count.set(0)
        self.last_scan_text.set("---")
        self.last_scan_status_icon.set("⚪")
        self.last_scan_status_color.set(COLOR_TEXT)

    def start_camera_thread(self):
        if self.video_thread and self.video_thread.is_alive(): return
        self.stop_video_loop = False
        self.video_thread = threading.Thread(target=self.video_loop, daemon=True)
        self.video_thread.start()

    def video_loop(self):
        cap = cv2.VideoCapture(self.camera_source)
        last_scan_time = 0
        scan_cooldown = 1
        while not self.stop_video_loop:
            ret, frame = cap.read()
            if not ret:
                time.sleep(0.1)
                continue
            
            current_time = time.time()
            if current_time - last_scan_time > scan_cooldown:
                decoded_objects = pyzbar.decode(frame)
                if decoded_objects:
                    for obj in decoded_objects:
                        qr_data = obj.data.decode('utf-8')
                        self.process_scan(qr_data)
                        last_scan_time = time.time()
                        points = obj.polygon
                        pts = np.array(points, np.int32)
                        pts = pts.reshape((-1, 1, 2))
                        cv2.polylines(frame, [pts], True, (0, 255, 0), 3)
                        break

            img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img_pil = Image.fromarray(img)
            img_tk = ImageTk.PhotoImage(image=img_pil)
            self.master.after(0, self.update_camera_label, img_tk)
            time.sleep(0.015)
        cap.release()

    def update_camera_label(self, img_tk):
        try:
            if not self.stop_video_loop:
                self.camera_label.config(image=img_tk)
                self.camera_label.image = img_tk 
        except tk.TclError: pass

    def process_scan(self, data):
        if data in self.scanned_ids:
            status = "duplicate"
            self.duplicate_count.set(self.duplicate_count.get() + 1)
        elif data in self.all_ids:
            status = "correct"
            self.correct_count.set(self.correct_count.get() + 1)
            self.total_scanned_count.set(self.total_scanned_count.get() + 1)
            self.scanned_ids.add(data)
            if data.upper().startswith("FR"): self.fr_count.set(self.fr_count.get() + 1)
            elif data.upper().startswith("GR"): self.gr_count.set(self.gr_count.get() + 1)
            elif data.upper().startswith("PA"): self.pa_count.set(self.pa_count.get() + 1)
        else:
            status = "error"
            self.error_count.set(self.error_count.get() + 1)
            self.total_scanned_count.set(self.total_scanned_count.get() + 1)

        self.scanned_log.append((data, status, datetime.now()))
        self.play_sound_thread(status)
        self.master.after(0, self.update_gui_for_scan, data, status)

    def update_gui_for_scan(self, data, status):
        self.last_scan_text.set(data)
        if status == "correct":
            self.last_scan_status_icon.set("✅")
            self.last_scan_status_color.set(COLOR_SUCCESS)
        elif status == "duplicate":
            self.last_scan_status_icon.set("🔁")
            self.last_scan_status_color.set(COLOR_DUPLICATE)
        else:
            self.last_scan_status_icon.set("❌")
            self.last_scan_status_color.set(COLOR_ERROR)
        try:
            status_widget = self.master.winfo_children()[-1].winfo_children()[-1].winfo_children()[0]
            status_widget.config(foreground=self.last_scan_status_color.get())
        except (tk.TclError, IndexError): pass

    def play_sound_thread(self, sound_type):
        threading.Thread(target=self.play_sound, args=(sound_type,), daemon=True).start()

    def get_base_path(self):
        """الحصول على المسار الأساسي للبرنامج سواء كان ملف .py أو .exe"""
        if getattr(sys, 'frozen', False):
            return os.path.dirname(sys.executable)
        else:
            return os.path.dirname(os.path.abspath(__file__))

    def play_sound(self, sound_type):
        """تشغيل ملف صوتي مخصص مع مسار ديناميكي والرجوع إلى صوت النظام عند الفشل."""
        base_path = self.get_base_path()
        sound_folder = os.path.join(base_path, "sound")
        correct_sound_path = os.path.join(sound_folder, "correct.wav")
        error_sound_path = os.path.join(sound_folder, "error.wav")

        sound_played = False
        try:
            if sound_type == "correct" and os.path.exists(correct_sound_path):
                playsound(correct_sound_path)
                sound_played = True
            elif sound_type == "error" and os.path.exists(error_sound_path):
                playsound(error_sound_path)
                sound_played = True
        except Exception as e:
            print(f"فشل تشغيل الصوت المخصص: {e}")

        if not sound_played:
            try:
                if sound_type == "correct":
                    winsound.Beep(1200, 200)
                elif sound_type == "error":
                    winsound.Beep(440, 500)
                elif sound_type == "duplicate":
                    winsound.Beep(800, 150)
                    time.sleep(0.05)
                    winsound.Beep(800, 150)
            except Exception as e:
                print(f"فشل تشغيل الصوت باستخدام winsound: {e}")

    def save_report(self):
        file_path = filedialog.asksaveasfilename(
            title="حفظ التقرير",
            defaultextension=".pdf",
            filetypes=(("PDF files", "*.pdf"), ("Text files", "*.txt"))
        )
        if not file_path: return
        try:
            if file_path.endswith(".pdf"):
                self.generate_pdf_report_v2(file_path)
            else:
                self.generate_txt_report(file_path)
            messagebox.showinfo("نجاح", f"تم حفظ التقرير بنجاح في:\n{file_path}")
        except Exception as e:
            messagebox.showerror("خطأ في الحفظ", f"فشل حفظ التقرير:\n{e}")

    def generate_report_string(self):
        lines = [
            f"تقرير الحضور - {APP_TITLE}",
            f"تاريخ ووقت التقرير: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "="*40, "\n--- ملخص الإحصائيات ---\n",
            f"إجمالي الأكواد الممسوحة (صحيح + خطأ): {self.total_scanned_count.get()}",
            f"إجمالي الأكواد الصحيحة: {self.correct_count.get()}",
            f"  - نوع FR: {self.fr_count.get()}",
            f"  - نوع GR: {self.gr_count.get()}",
            f"  - نوع PA: {self.pa_count.get()}",
            f"إجمالي الأكواد المكررة: {self.duplicate_count.get()}",
            f"إجمالي الأكواد الخاطئة: {self.error_count.get()}",
            "\n--- سجل المسح التفصيلي ---\n"
        ]
        for data, status, ts in self.scanned_log:
            lines.append(f"[{ts.strftime('%H:%M:%S')}] - {data} - ({status.upper()})")
        return "\n".join(lines)

    def generate_txt_report(self, path):
        with open(path, 'w', encoding='utf-8') as f:
            f.write(self.generate_report_string())

    def generate_pdf_report_v2(self, path):
        """إنشاء تقرير PDF بتصميم احترافي."""
        try:
            pdfmetrics.registerFont(TTFont('Tahoma', 'tahoma.ttf'))
            pdfmetrics.registerFont(TTFont('Tahoma-Bold', 'tahomabd.ttf'))
        except Exception:
            messagebox.showwarning("تحذير الخط", "لم يتم العثور على خطوط Tahoma. قد لا تظهر العربية بشكل صحيح.")
            return

        c = canvas.Canvas(path, pagesize=A4)
        width, height = A4

        # --- دوال مساعدة للرسم ---
        def draw_rtl_text(x, y, text, font='Tahoma', size=10, color=colors.black):
            c.setFillColor(color)
            c.setFont(font, size)
            c.drawRightString(x, y, get_display(arabic_reshaper.reshape(text)))

        def draw_header_footer(canvas_obj, page_num):
            canvas_obj.saveState()
            # Header
            canvas_obj.setFillColor(colors.HexColor(COLOR_FRAME))
            canvas_obj.rect(0, height - 1.5*cm, width, 1.5*cm, fill=1, stroke=0)
            draw_rtl_text(width - 0.7*cm, height - 1*cm, "تقرير الحضور", 'Tahoma-Bold', 20, color=colors.white)
            c.setFillColor(colors.white)
            c.setFont('Helvetica', 9)
            c.drawString(0.7*cm, height - 1*cm, APP_TITLE)
            # Footer
            draw_rtl_text(width - 0.7*cm, 0.7*cm, f"صفحة {page_num}", color=colors.black)
            c.setFont('Helvetica', 9)
            c.drawString(0.7*cm, 0.7*cm, datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            canvas_obj.restoreState()

        # --- رسم المحتوى ---
        page_number = 1
        draw_header_footer(c, page_number)
        y_pos = height - 2.5*cm

        # --- قسم الملخص ---
        draw_rtl_text(width - 1*cm, y_pos, "ملخص الإحصائيات", 'Tahoma-Bold', 16, color=colors.black)
        y_pos -= 1*cm
        
        summary_data = {
            "إجمالي الممسوح (صحيح+خطأ)": self.total_scanned_count.get(),
            "الأكواد الصحيحة": self.correct_count.get(),
            "الأكواد المكررة": self.duplicate_count.get(),
            "الأكواد الخاطئة": self.error_count.get(),
            "نوع FR": self.fr_count.get(),
            "نوع GR": self.gr_count.get(),
            "نوع PA": self.pa_count.get()
        }
        
        box_x = 1.5*cm
        box_width = (width - 3*cm) / 2.2
        for i, (key, value) in enumerate(summary_data.items()):
            c.setFillColor(colors.HexColor(COLOR_FRAME))
            c.roundRect(box_x, y_pos - 0.2*cm, box_width, 1*cm, 4, fill=1, stroke=0)
            draw_rtl_text(box_x + box_width - 0.5*cm, y_pos, key, 'Tahoma-Bold', 12, color=colors.white)
            c.setFont('Helvetica-Bold', 18)
            c.setFillColor(colors.white)
            c.drawString(box_x + 0.5*cm, y_pos, str(value))
            if (i + 1) % 2 == 0:
                y_pos -= 1.5*cm
                box_x = 1.5*cm
            else:
                box_x += box_width + 0.5*cm
        
        y_pos -= 1.5*cm
        
        # --- قسم التفاصيل ---
        draw_rtl_text(width - 1*cm, y_pos, "سجل المسح التفصيلي", 'Tahoma-Bold', 16, color=colors.black)
        y_pos -= 1*cm

        # Table Header
        header_y = y_pos
        c.setFillColor(colors.HexColor(COLOR_ACCENT))
        c.rect(1.5*cm, header_y - 0.2*cm, width - 3*cm, 1*cm, fill=1, stroke=0)
        draw_rtl_text(width - 2*cm, header_y, "الحالة", 'Tahoma-Bold', 12, color=colors.white)
        draw_rtl_text(width - 7*cm, header_y, "الكود", 'Tahoma-Bold', 12, color=colors.white)
        draw_rtl_text(width - 16*cm, header_y, "الوقت", 'Tahoma-Bold', 12, color=colors.white)
        y_pos -= 1.2*cm

        for i, (data, status, ts) in enumerate(self.scanned_log):
            if y_pos < 3*cm:
                c.showPage()
                page_number += 1
                draw_header_footer(c, page_number)
                y_pos = height - 2.5*cm
                header_y = y_pos
                c.setFillColor(colors.HexColor(COLOR_ACCENT))
                c.rect(1.5*cm, header_y - 0.2*cm, width - 3*cm, 1*cm, fill=1, stroke=0)
                draw_rtl_text(width - 2*cm, header_y, "الحالة", 'Tahoma-Bold', 12, color=colors.white)
                draw_rtl_text(width - 7*cm, header_y, "الكود", 'Tahoma-Bold', 12, color=colors.white)
                draw_rtl_text(width - 16*cm, header_y, "الوقت", 'Tahoma-Bold', 12, color=colors.white)
                y_pos -= 1.2*cm

            row_color = colors.HexColor("#F0F0F0") if i % 2 == 0 else colors.white
            c.setFillColor(row_color)
            c.rect(1.5*cm, y_pos - 0.2*cm, width - 3*cm, 0.8*cm, fill=1, stroke=0)

            status_map = {"correct": "صحيح ✅", "duplicate": "مكرر 🔁", "error": "خطأ ❌"}
            draw_rtl_text(width - 2*cm, y_pos, status_map.get(status, status), 'Tahoma', 11, color=colors.black)
            c.setFont('Courier', 11)
            c.setFillColor(colors.black)
            c.drawString(4.5*cm, y_pos, data)
            c.setFont('Helvetica', 11)
            c.drawString(14*cm, y_pos, ts.strftime('%H:%M:%S'))
            y_pos -= 0.8*cm

        c.save()

    def on_closing(self):
        if messagebox.askokcancel("إنهاء", "هل تريد بالتأكيد إغلاق البرنامج؟"):
            self.stop_video_loop = True
            if self.video_thread: self.video_thread.join(timeout=1)
            self.master.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
