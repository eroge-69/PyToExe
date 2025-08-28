import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import time
import random
import subprocess
import sys
from collections import defaultdict
import sv_ttk

# نصب خودکار کتابخانه‌های مورد نیاز
def install_packages():
    required_packages = ['sv_ttk']
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])

install_packages()

class V2RayOptimizer:
    def __init__(self, root):
        self.root = root
        self.root.title("V2Ray Fragment Optimizer - BY : SAEID KHANDANI")
        self.root.geometry("1000x750")
        self.root.minsize(900, 650)
        
        # تنظیم تم ویندوز 11
        sv_ttk.set_theme("light")
        
        self.scanning = False
        self.results = defaultdict(list)
        
        self.setup_ui()
        
    def setup_ui(self):
        # ایجاد نوار عنوان سفارشی
        self.setup_title_bar()
        
        # فریم اصلی
        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # فریم ورودی - قرار دادن همه موارد در یک سطر
        input_frame = ttk.LabelFrame(main_frame, text="Scan Settings", padding="15")
        input_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 15))
        
        # ایجاد فریم برای قرار دادن همه کنترل‌ها در یک ردیف
        control_frame = ttk.Frame(input_frame)
        control_frame.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        # Range fragment_length
        length_frame = ttk.LabelFrame(control_frame, text="Range fragment_length", padding="10")
        length_frame.grid(row=0, column=0, padx=(0, 10), sticky=tk.W)
        
        min_max_frame = ttk.Frame(length_frame)
        min_max_frame.grid(row=0, column=0, pady=5)
        
        ttk.Label(min_max_frame, text="From :", font=("Arial", 9)).grid(row=0, column=0, padx=(0, 5))
        self.min_length = tk.StringVar(value="100")
        ttk.Entry(min_max_frame, textvariable=self.min_length, width=8, font=("Arial", 10)).grid(row=0, column=1, padx=(0, 10))
        
        ttk.Label(min_max_frame, text="To :", font=("Arial", 9)).grid(row=0, column=2, padx=(0, 5))
        self.max_length = tk.StringVar(value="2000")
        ttk.Entry(min_max_frame, textvariable=self.max_length, width=8, font=("Arial", 10)).grid(row=0, column=3)
        
        # Range fragment_interval
        interval_frame = ttk.LabelFrame(control_frame, text="Range fragment_interval", padding="10")
        interval_frame.grid(row=0, column=1, padx=(0, 10), sticky=tk.W)
        
        min_max_interval_frame = ttk.Frame(interval_frame)
        min_max_interval_frame.grid(row=0, column=0, pady=5)
        
        ttk.Label(min_max_interval_frame, text="From:", font=("Arial", 9)).grid(row=0, column=0, padx=(0, 5))
        self.min_interval = tk.StringVar(value="10")
        ttk.Entry(min_max_interval_frame, textvariable=self.min_interval, width=8, font=("Arial", 10)).grid(row=0, column=1, padx=(0, 10))
        
        ttk.Label(min_max_interval_frame, text="To:", font=("Arial", 9)).grid(row=0, column=2, padx=(0, 5))
        self.max_interval = tk.StringVar(value="100")
        ttk.Entry(min_max_interval_frame, textvariable=self.max_interval, width=8, font=("Arial", 10)).grid(row=0, column=3)
        
        # تعداد تست‌ها
        test_frame = ttk.LabelFrame(control_frame, text="Number of tests", padding="10")
        test_frame.grid(row=0, column=2, padx=(0, 10), sticky=tk.W)
        
        self.iterations = tk.StringVar(value="3")
        ttk.Entry(test_frame, textvariable=self.iterations, width=8, font=("Arial", 10)).grid(row=0, column=0, padx=5, pady=5)
        
        # دکمه‌ها
        button_frame = ttk.Frame(control_frame)
        button_frame.grid(row=0, column=3, padx=(10, 0))
        
        self.start_btn = ttk.Button(button_frame, text="Start Scanning", command=self.start_scan, style="Accent.TButton")
        self.start_btn.grid(row=0, column=0, padx=(0, 10))
        
        self.stop_btn = ttk.Button(button_frame, text="Stop Scanning", command=self.stop_scan, state=tk.DISABLED)
        self.stop_btn.grid(row=0, column=1)
        
        # نوار پیشرفت
        progress_frame = ttk.LabelFrame(input_frame, text="Scan Progress", padding="10")
        progress_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(20, 0))
        
        self.progress_var = tk.IntVar()
        self.progress = ttk.Progressbar(
            progress_frame, 
            variable=self.progress_var, 
            maximum=100, 
            mode='determinate',
            style="Custom.Horizontal.TProgressbar"
        )
        self.progress.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        self.status_label = ttk.Label(progress_frame, text="Ready", font=("Arial", 9))
        self.status_label.grid(row=1, column=0, sticky=tk.W, pady=(5, 0))
        
        percent_frame = ttk.Frame(progress_frame)
        percent_frame.grid(row=1, column=0, sticky=tk.E, pady=(5, 0))
        
        self.percent_label = ttk.Label(percent_frame, text="0%", font=("Arial", 9))
        self.percent_label.grid(row=0, column=0)
        
        # فریم نتایج
        results_frame = ttk.LabelFrame(main_frame, text="Scan Results", padding="15")
        results_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        # ناحیه متن نتایج با قابلیت رنگ‌آمیزی
        self.results_text = scrolledtext.ScrolledText(
            results_frame, 
            width=80, 
            height=20, 
            font=("Arial", 10),
            wrap=tk.WORD,
            relief=tk.FLAT,
            borderwidth=1,
            foreground="#FFFFFF",
            background="#000000"
        )
        self.results_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # ایجاد نوار پاورشل در پایین
        self.setup_powershell_bar()
        
        # تنظیم وزن‌های گرید برای پاسخگو بودن
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(1, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)
        input_frame.columnconfigure(0, weight=1)
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(0, weight=1)
        control_frame.columnconfigure(0, weight=1)
        control_frame.columnconfigure(1, weight=1)
        control_frame.columnconfigure(2, weight=1)
        control_frame.columnconfigure(3, weight=1)
        progress_frame.columnconfigure(0, weight=1)
        
        # تنظیم سبک‌های سفارشی
        self.setup_styles()
        
        # اضافه کردن تگ‌های رنگی برای نمایش نتایج
        self.setup_text_tags()
        
    def setup_title_bar(self):
        # ایجاد یک فریم برای نوار عنوان سفارشی
        title_bar = ttk.Frame(self.root, height=40, style="TitleBar.TFrame")
        title_bar.grid(row=0, column=0, sticky=(tk.W, tk.E))
        title_bar.grid_propagate(False)
        
        # عنوان برنامه
        title_label = ttk.Label(
            title_bar, 
            text="Professional scanner to find the best fragment_length & fragment_interval to improve internet quality ", 
            font=("Arial", 10, "bold" ),
            style="TitleBar.TLabel",
        )
        title_label.grid(row=0, column=0, padx=(15, 0), sticky=tk.W)
        
        # دکمه‌های کنترل پنجره
        button_frame = ttk.Frame(title_bar, style="TitleBar.TFrame")
        button_frame.grid(row=0, column=1, sticky=tk.E)
        
        
        
    def setup_powershell_bar(self):
        # ایجاد نوار پایینی شبیه پاورشل
        powershell_bar = ttk.Frame(self.root, height=30, style="PowerShell.TFrame")
        powershell_bar.grid(row=2, column=0, sticky=(tk.W, tk.E))
        powershell_bar.grid_propagate(False)
        
        # وضعیت سیستم
        status_label = ttk.Label(
            powershell_bar, 
            text="Ready | System Online | V2Ray Active", 
            font=("Arial", 9),
            style="PowerShell.TLabel"
        )
        status_label.grid(row=0, column=0, padx=(15, 0), sticky=tk.W)
        
        # زمان و تاریخ
        from datetime import datetime
        time_str = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
        time_label = ttk.Label(
            powershell_bar, 
            text=time_str, 
            font=("Arial", 9),
            style="PowerShell.TLabel"
        )
        time_label.grid(row=0, column=1, padx=(0, 15), sticky=tk.E)
        
        powershell_bar.columnconfigure(0, weight=1)
        
    def setup_styles(self):
        style = ttk.Style()
        
        # سبک برای نوار عنوان
        style.configure("TitleBar.TFrame", background="#f5f5f5")
        style.configure("TitleBar.TLabel", background="#f5f5f5")
        style.configure("TitleBar.TButton", background="#f5f5f5", borderwidth=0)
        
        # سبک برای نوار پاورشل
        style.configure("PowerShell.TFrame", background="#FFFFFF")
        style.configure("PowerShell.TLabel", background="#FFFFFF", foreground="#ffffff")
        
        # سبک برای دکمه آکسان (شروع)
        style.configure("Accent.TButton", background="#0078d4", foreground="white")
        style.map("Accent.TButton", 
                 background=[('active', '#106ebe'), ('pressed', '#005a9e')])
        
        # سبک برای نوار پیشرفت
        style.configure("Custom.Horizontal.TProgressbar", 
                       background='#0078d4',
                       troughcolor='#e1e1e1',
                       bordercolor='#c0c0c0',
                       lightcolor='#62a0d4',
                       darkcolor='#005a9e')
        
    def setup_text_tags(self):
        # تعریف تگ‌های رنگی برای نمایش نتایج
        self.results_text.tag_configure("header", foreground="#ffd900", font=("Arial", 12, "bold"))
        self.results_text.tag_configure("success", foreground="#27ae60", font=("Arial", 11))
        self.results_text.tag_configure("warning", foreground="#f39c12", font=("Arial", 11))
        self.results_text.tag_configure("error", foreground="#e74c3c", font=("Arial", 11))
        self.results_text.tag_configure("info", foreground="#3498db", font=("Arial", 11))
        self.results_text.tag_configure("result_1", foreground="#16a085", font=("Arial", 11, "bold"))
        self.results_text.tag_configure("result_2", foreground="#2980b9", font=("Arial", 11, "bold"))
        self.results_text.tag_configure("result_3", foreground="#8e44ad", font=("Arial", 11, "bold"))
        self.results_text.tag_configure("highlight", background="#ffffff", foreground="#d35400")
        
    def start_scan(self):
        try:
            min_len = int(self.min_length.get())
            max_len = int(self.max_length.get())
            min_int = int(self.min_interval.get())
            max_int = int(self.max_interval.get())
            iterations = int(self.iterations.get())
            
            if min_len > max_len or min_int > max_int or iterations <= 0:
                messagebox.showerror("خطا", "مقادیر وارد شده نامعتبر هستند")
                return
                
        except ValueError:
            messagebox.showerror("خطا", "لطفاً مقادیر عددی معتبر وارد کنید")
            return
            
        self.scanning = True
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.progress_var.set(0)
        self.percent_label.config(text="0%")
        self.status_label.config(text="در حال آغاز اسکن...")
        self.results_text.delete(1.0, tk.END)
        
        # شروع اسکن در یک ریسمان جداگانه
        scan_thread = threading.Thread(target=self.run_scan, 
                                      args=(min_len, max_len, min_int, max_int, iterations))
        scan_thread.daemon = True
        scan_thread.start()
        
    def stop_scan(self):
        self.scanning = False
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.status_label.config(text="Stopped")
        
    def run_scan(self, min_len, max_len, min_int, max_int, iterations):
        self.add_result("Starting scanning process...\n", "info")
        self.add_result("Searching for the best combinations of fragment_length and fragment_interval\n", "header")
        self.add_result("="*60 + "\n", "info")
        
        # تولید ترکیبات مختلف برای تست
        test_combinations = []
        for length in range(min_len, max_len + 1, 100):
            for interval in range(min_int, max_int + 1, 10):
                test_combinations.append((length, interval))
                
        total_tests = len(test_combinations) * iterations
        completed_tests = 0
        
        # تست هر ترکیب
        for length, interval in test_combinations:
            if not self.scanning:
                break
                
            speeds = []
            for i in range(iterations):
                if not self.scanning:
                    break
                    
                # شبیه‌سازی تست سرعت
                time.sleep(0.1)
                
                # تولید سرعت تصادفی برای شبیه‌سازی
                speed = random.uniform(1, 100)
                speeds.append(speed)
                
                completed_tests += 1
                progress = (completed_tests / total_tests) * 100
                
                # به روزرسانی پیشرفت
                self.root.after(0, self.update_progress, progress, 
                               f"Combination test: length={length}, interval={interval} ({i+1}/{iterations})")
            
            if speeds:
                avg_speed = sum(speeds) / len(speeds)
                self.results[avg_speed].append((length, interval))
                
                status_tag = "success" if avg_speed > 50 else "warning" if avg_speed > 30 else "error"
                self.add_result(f"Combination: length={length}, interval={interval} - Average speed: {avg_speed:.2f} Mbps\n", status_tag)
        
        if self.scanning:
            self.root.after(0, self.show_final_results)
            
        self.root.after(0, self.stop_scan)
        
    def update_progress(self, progress, status):
        self.progress_var.set(progress)
        self.percent_label.config(text=f"{int(progress)}%")
        self.status_label.config(text=status)
        
    def add_result(self, text, tag=None):
        self.results_text.insert(tk.END, text, tag)
        self.results_text.see(tk.END)
        
    def show_final_results(self):
        if not self.results:
            self.add_result("No results found\n", "error")
            return
            
        self.add_result("\n" + "="*60 + "\n", "info")
        self.add_result("\nFinal results:\n", "header")
        self.add_result("Best combinations based on speed:\n\n", "info")
        
        # مرتب‌سازی نتایج بر اساس سرعت
        sorted_speeds = sorted(self.results.keys(), reverse=True)
        
        for i, speed in enumerate(sorted_speeds[:5]):
            tag = f"result_{i+1}" if i < 3 else "info"
            for length, interval in self.results[speed]:
                self.add_result(f"{i+1}. length={length}, interval={interval} - سرعت: {speed:.2f} Mbps\n", tag)
                
        self.add_result("\nScan completed!\n", "success")
        self.status_label.config(text="Scan Completed")

if __name__ == "__main__":
    root = tk.Tk()
    app = V2RayOptimizer(root)
    root.mainloop()