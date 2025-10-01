import tkinter as tk
from tkinter import ttk, messagebox
from tkinter.font import Font
import random

class DaryaCenterConverter:
    def __init__(self, root):
        self.root = root
        self.root.title("Darya Center - Advanced Converter")
        self.root.geometry("800x680")
        self.root.configure(bg='#f0f0f0')
        
        # الكلمات الدينية والألوان
        self.religious_phrases = ["لا اله الا الله", "الله أكبر", "سبحان الله", "اللهم صل على محمد"]
        self.colors = ['#FF0000', '#00FF00', '#0000FF', '#FF00FF', '#00FFFF', '#FFA500']
        
        self.rates = {1: 15500, 2: 16000}
        self.rate_var = tk.IntVar(value=1)
        
        # متغيرات النص
        self.coins_var = tk.StringVar()
        self.dinar_var = tk.StringVar()
        self.total_amount_var = tk.StringVar()
        self.paid_amount_var = tk.StringVar()
        self.custom_rate_var = tk.StringVar()
        
        self.create_widgets()
        self.setup_bindings()
        self.setup_phrases_display()
    
    def setup_phrases_display(self):
        """إعداد عرض الكلمات العشوائية على الجانب الأيمن"""
        self.phrase_frame = tk.Frame(self.root, width=200, bg='#f0f0f0')
        self.phrase_frame.pack(side='right', fill='y', padx=10)
        
        self.current_phrase = None
        self.update_phrase()
    
    def update_phrase(self):
        """تحديث الكلمة كل 4 ثواني"""
        if hasattr(self, 'current_phrase') and self.current_phrase:
            self.current_phrase.destroy()
        
        phrase = random.choice(self.religious_phrases)
        color = random.choice(self.colors)
        font_size = random.randint(14, 18)
        
        self.current_phrase = tk.Label(
            self.phrase_frame,
            text=phrase,
            font=('Arial', font_size, 'bold'),
            fg=color,
            bg='#f0f0f0'
        )
        
        # وضع عشوائي في الإطار
        x_pos = random.randint(10, 150)
        y_pos = random.randint(10, 600)
        self.current_phrase.place(x=x_pos, y=y_pos)
        
        # جدولة التحديث بعد 4 ثواني
        self.root.after(4000, self.update_phrase)
    
    def setup_bindings(self):
        self.coins_var.trace('w', self.on_coins_change)
        self.dinar_var.trace('w', self.on_dinar_change)
        self.rate_var.trace('w', self.on_rate_change)
        self.paid_amount_var.trace('w', self.calculate_remaining)
    
    def on_coins_change(self, *args):
        if self.coins_var.get():
            self.calculate_coins_to_dinar()
        else:
            self.total_amount_var.set('')
            self.lbl_coins_result.config(text='')
    
    def on_dinar_change(self, *args):
        if self.dinar_var.get():
            self.total_amount_var.set(self.dinar_var.get())
            self.calculate_dinar_to_coins()
        else:
            self.total_amount_var.set('')
            self.lbl_dinar_result.config(text='')
    
    def on_rate_change(self, *args):
        if self.coins_var.get():
            self.calculate_coins_to_dinar()
        elif self.dinar_var.get():
            self.calculate_dinar_to_coins()
    
    def create_widgets(self):
        main_frame = ttk.Frame(self.root, padding=20)
        main_frame.pack(side='left', expand=True, fill='both')
        
        # العنوان
        title = ttk.Label(main_frame, 
                        text="محول عملات تيك توك المتقدم",
                        font=('Arial', 16, 'bold'),
                        foreground='#2c3e50')
        title.grid(row=0, column=0, columnspan=3, pady=10)
        
        # أقسام التحويل
        self.create_conversion_sections(main_frame)
        self.create_payment_section(main_frame)
        self.create_rate_settings(main_frame)
        
        # التحكم
        control_frame = ttk.Frame(main_frame)
        control_frame.grid(row=5, column=0, pady=10, sticky='we')
        
        clear_btn = ttk.Button(control_frame, 
                             text="مسح الكل",
                             command=self.clear_all)
        clear_btn.pack(side='right', padx=10)
        
        # التذييل
        footer_frame = ttk.Frame(main_frame)
        footer_frame.grid(row=6, column=0, pady=5, sticky='we')
        
        version = ttk.Label(footer_frame, 
                          text="الإصدار 3.1 - نظام التحويل الثنائي مع حساب المدفوعات",
                          foreground='gray')
        version.pack(side='right')
        
        # تأثير النار
        self.dev_label = tk.Label(footer_frame, 
                                text="Developed By: Ayub",
                                fg='#FF4500',
                                bg='#f0f0f0',
                                font=Font(family='Arial', size=10, weight='bold'))
        self.dev_label.pack(side='left', padx=10)
        
        # بدء التأثير
        self.animate_fire()
    
    def animate_fire(self):
        colors = ['#FF4500', '#FF6347', '#FF7F50', '#FF8C00', '#FFA500']
        current = getattr(self, '_fire_color', 0)
        self.dev_label.config(fg=colors[current])
        self._fire_color = (current + 1) % len(colors)
        self.root.after(300, self.animate_fire)
    
    def clear_all(self):
        self.coins_var.set('')
        self.dinar_var.set('')
        self.total_amount_var.set('')
        self.paid_amount_var.set('')
        self.custom_rate_var.set('')
        self.lbl_coins_result.config(text='')
        self.lbl_dinar_result.config(text='')
        self.lbl_remaining_result.config(text='')
        self.rate_var.set(1)
        self.entry_custom_rate.config(state='disabled')
    
    def create_conversion_sections(self, parent):
        coins_frame = ttk.LabelFrame(parent, text="تحويل العملات إلى دينار")
        coins_frame.grid(row=1, column=0, padx=10, pady=5, sticky='nsew')
        
        ttk.Label(coins_frame, text="عدد العملات:").grid(row=0, column=0, padx=5)
        ttk.Entry(coins_frame, width=20, textvariable=self.coins_var).grid(row=0, column=1, padx=5)
        
        ttk.Button(coins_frame, 
                 text="تحويل إلى دينار",
                 command=self.calculate_coins_to_dinar).grid(row=0, column=2, padx=5)
        
        self.lbl_coins_result = ttk.Label(coins_frame, text="", font=('Arial', 10))
        self.lbl_coins_result.grid(row=1, column=0, columnspan=3, pady=5)
        
        dinar_frame = ttk.LabelFrame(parent, text="تحويل الدينار إلى عملات")
        dinar_frame.grid(row=2, column=0, padx=10, pady=5, sticky='nsew')
        
        ttk.Label(dinar_frame, text="المبلغ بالدينار:").grid(row=0, column=0, padx=5)
        ttk.Entry(dinar_frame, width=20, textvariable=self.dinar_var).grid(row=0, column=1, padx=5)
        
        ttk.Button(dinar_frame, 
                 text="تحويل إلى عملات",
                 command=self.calculate_dinar_to_coins).grid(row=0, column=2, padx=5)
        
        self.lbl_dinar_result = ttk.Label(dinar_frame, text="", font=('Arial', 10))
        self.lbl_dinar_result.grid(row=1, column=0, columnspan=3, pady=5)
    
    def create_payment_section(self, parent):
        payment_frame = ttk.LabelFrame(parent, text="حساب المدفوعات والمتبقي")
        payment_frame.grid(row=4, column=0, padx=10, pady=10, sticky='nsew')
        
        ttk.Label(payment_frame, text="المبلغ الإجمالي (دينار):").grid(row=0, column=0, padx=5)
        ttk.Entry(payment_frame, width=20, textvariable=self.total_amount_var, state='readonly').grid(row=0, column=1, padx=5)
        
        ttk.Label(payment_frame, text="المبلغ المدفوع (دينار):").grid(row=1, column=0, padx=5)
        ttk.Entry(payment_frame, width=20, textvariable=self.paid_amount_var).grid(row=1, column=1, padx=5)
        
        self.lbl_remaining_result = ttk.Label(payment_frame, text="", font=('Arial', 10, 'bold'))
        self.lbl_remaining_result.grid(row=2, column=0, columnspan=2, pady=5)
    
    def create_rate_settings(self, parent):
        rate_frame = ttk.LabelFrame(parent, text="إعدادات سعر الصرف")
        rate_frame.grid(row=3, column=0, pady=10, sticky='we')
        
        ttk.Radiobutton(rate_frame, 
                      text="السعر الأساسي 1: 1000 عملة = 15,500 دينار",
                      variable=self.rate_var,
                      value=1).pack(anchor='w', padx=10)
        
        ttk.Radiobutton(rate_frame,
                      text="السعر الأساسي 2: 1000 عملة = 16,000 دينار",
                      variable=self.rate_var,
                      value=2).pack(anchor='w', padx=10)
        
        ttk.Radiobutton(rate_frame, 
                      text="سعر مخصص:",
                      variable=self.rate_var,
                      value=3).pack(anchor='w', padx=10, pady=5)
        
        self.entry_custom_rate = ttk.Entry(rate_frame, width=15, textvariable=self.custom_rate_var, state='disabled')
        self.entry_custom_rate.pack(side='left', padx=10)
        ttk.Label(rate_frame, text="دينار لكل 1000 عملة").pack(side='left')
        
        self.rate_var.trace('w', lambda *_: self.entry_custom_rate.config(
            state='normal' if self.rate_var.get() == 3 else 'disabled'))
    
    def get_current_rate(self):
        selected = self.rate_var.get()
        if selected == 3:
            try:
                rate = float(self.custom_rate_var.get().replace(',', ''))
                return rate if rate > 0 else 15500
            except:
                return 15500
        return self.rates.get(selected, 15500)
    
    def calculate_coins_to_dinar(self):
        try:
            coins = self.coins_var.get().strip().replace(',', '')
            if not coins:
                self.total_amount_var.set('')
                self.lbl_coins_result.config(text='')
                return
            
            coins = float(coins)
            rate = self.get_current_rate()
            result = (coins / 1000) * rate
            
            self.total_amount_var.set(f"{result:,.0f}")
            self.lbl_coins_result.config(
                text=f"المبلغ بالدينار: {result:,.0f} IQD",
                foreground='#27ae60'
            )
        except Exception as e:
            messagebox.showerror("خطأ", f"حدث خطأ في الحساب: {str(e)}")
            self.lbl_coins_result.config(
                text="حدث خطأ في الحساب",
                foreground='red'
            )
    
    def calculate_dinar_to_coins(self):
        try:
            dinar = self.dinar_var.get().strip().replace(',', '')
            if not dinar:
                self.lbl_dinar_result.config(text='')
                return
            
            dinar = float(dinar)
            rate = self.get_current_rate()
            result = (dinar / rate) * 1000
            
            self.lbl_dinar_result.config(
                text=f"عدد العملات: {result:,.0f} عملة",
                foreground='#2980b9'
            )
        except Exception as e:
            messagebox.showerror("خطأ", f"حدث خطأ في الحساب: {str(e)}")
            self.lbl_dinar_result.config(
                text="حدث خطأ في الحساب",
                foreground='red'
            )
    
    def calculate_remaining(self, *args):
        try:
            total = self.total_amount_var.get().strip().replace(',', '')
            paid = self.paid_amount_var.get().strip().replace(',', '')
            
            if not total:
                self.lbl_remaining_result.config(text='')
                return
            
            total = float(total)
            paid = float(paid) if paid else 0
            
            remaining = total - paid
            if remaining < 0:
                msg = f"المبلغ الزائد: {abs(remaining):,.0f} IQD"
                color = '#f39c12'
            elif remaining == 0:
                msg = "تم السداد بالكامل"
                color = '#2ecc71'
            else:
                msg = f"المبلغ المتبقي: {remaining:,.0f} IQD"
                color = '#e74c3c'
            
            self.lbl_remaining_result.config(text=msg, foreground=color)
        except Exception as e:
            messagebox.showerror("خطأ", f"حدث خطأ في الحساب: {str(e)}")
            self.lbl_remaining_result.config(
                text="حدث خطأ في الحساب",
                foreground='red'
            )

if __name__ == "__main__":
    root = tk.Tk()
    app = DaryaCenterConverter(root)
    root.mainloop()