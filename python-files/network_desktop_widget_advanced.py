import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import psutil
import threading
import time
import os
import sys
from PIL import Image, ImageTk
import io

class NetworkDesktopWidgetAdvanced:
    def __init__(self):
        # إعداد النافذة الرئيسية
        self.root = tk.Tk()
        self.root.title("Network Connections Widget")
        self.root.geometry("380x250")
        self.root.resizable(False, False)
        
        # جعل النافذة تظهر دائماً في المقدمة
        self.root.attributes('-topmost', True)
        
        # إعداد الألوان والخطوط
        self.root.configure(bg='#2b2b2b')
        
        # إزالة شريط العنوان
        self.root.overrideredirect(True)
        
        # متغيرات للتحكم في النافذة
        self.is_dragging = False
        self.drag_start_x = 0
        self.drag_start_y = 0
        self.is_minimized = False
        
        # إنشاء واجهة المستخدم
        self.create_widgets()
        
        # تحديث معلومات الشبكة
        self.update_network_info()
        
        # بدء التحديث التلقائي
        self.auto_update()
        
        # ربط أحداث النظام
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    def create_widgets(self):
        """إنشاء عناصر واجهة المستخدم"""
        # إطار العنوان
        title_frame = tk.Frame(self.root, bg='#3c3c3c', height=35)
        title_frame.pack(fill="x")
        title_frame.pack_propagate(False)
        
        # عنوان الكارت
        title_label = tk.Label(
            title_frame,
            text="🌐 Network Connections Widget",
            font=('Arial', 11, 'bold'),
            fg='#ffffff',
            bg='#3c3c3c',
            cursor="hand2"
        )
        title_label.pack(side="left", padx=10, pady=8)
        
        # أزرار التحكم
        control_frame = tk.Frame(title_frame, bg='#3c3c3c')
        control_frame.pack(side="right", padx=5)
        
        # زر تصغير
        minimize_btn = tk.Button(
            control_frame,
            text="−",
            command=self.minimize_widget,
            width=3,
            height=1,
            font=('Arial', 10, 'bold'),
            bg='#4CAF50',
            fg='white',
            relief='flat',
            bd=0
        )
        minimize_btn.pack(side="right", padx=2)
        
        # زر إغلاق
        close_btn = tk.Button(
            control_frame,
            text="×",
            command=self.close_widget,
            width=3,
            height=1,
            font=('Arial', 10, 'bold'),
            bg='#f44336',
            fg='white',
            relief='flat',
            bd=0
        )
        close_btn.pack(side="right", padx=2)
        
        # ربط أحداث السحب والنقر
        title_frame.bind("<Button-1>", self.start_drag)
        title_frame.bind("<B1-Motion>", self.drag)
        title_label.bind("<Button-1>", self.start_drag)
        title_label.bind("<B1-Motion>", self.drag)
        
        # المحتوى الرئيسي
        main_frame = tk.Frame(self.root, bg='#2b2b2b')
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # جعل الكارت بالكامل قابل للنقر
        self.root.bind("<Button-1>", self.on_widget_click)
        main_frame.bind("<Button-1>", self.on_widget_click)
        
        # إضافة تأثيرات التمرير
        self.root.bind("<Enter>", self.on_mouse_enter)
        self.root.bind("<Leave>", self.on_mouse_leave)
        
        # معلومات الشبكة
        self.network_info_frame = tk.Frame(main_frame, bg='#2b2b2b')
        self.network_info_frame.pack(fill="both", expand=True)
        
        # إنشاء عناصر معلومات الشبكة
        self.create_network_info_widgets()
        
        # ربط أحداث النقر لـ network_info_frame
        self.network_info_frame.bind("<Button-1>", self.on_widget_click)
        
        # أزرار التحكم
        buttons_frame = tk.Frame(main_frame, bg='#2b2b2b')
        buttons_frame.pack(fill="x", pady=5)
        
        # زر فتح Network Connections
        open_btn = tk.Button(
            buttons_frame,
            text="🔗 Open Network Connections",
            command=self.open_network_connections,
            width=20,
            height=2,
            font=('Arial', 9, 'bold'),
            bg='#2196F3',
            fg='white',
            relief='raised',
            bd=2
        )
        open_btn.pack(side="left", padx=5)
        
        # زر فتح Network Manager
        manager_btn = tk.Button(
            buttons_frame,
            text="⚙️ Network Manager",
            command=self.open_network_manager,
            width=15,
            height=2,
            font=('Arial', 9, 'bold'),
            bg='#FF9800',
            fg='white',
            relief='raised',
            bd=2
        )
        manager_btn.pack(side="left", padx=5)
        
        # زر تحديث
        refresh_btn = tk.Button(
            buttons_frame,
            text="🔄",
            command=self.update_network_info,
            width=3,
            height=2,
            font=('Arial', 10, 'bold'),
            bg='#4CAF50',
            fg='white',
            relief='raised',
            bd=2
        )
        refresh_btn.pack(side="right", padx=5)
        
        # نص توضيحي
        hint_frame = tk.Frame(main_frame, bg='#2b2b2b')
        hint_frame.pack(fill="x", pady=5)
        
        hint_label = tk.Label(
            hint_frame,
            text="💡 Click anywhere to open Network Connections",
            font=('Arial', 8, 'italic'),
            fg='#888888',
            bg='#2b2b2b',
            cursor="hand2"
        )
        hint_label.pack()
        hint_label.bind("<Button-1>", self.on_widget_click)
        
    def create_network_info_widgets(self):
        """إنشاء عناصر معلومات الشبكة"""
        # مسح العناصر السابقة
        for widget in self.network_info_frame.winfo_children():
            widget.destroy()
        
        # معلومات الاتصال النشط
        active_frame = tk.Frame(self.network_info_frame, bg='#3c3c3c', relief='raised', bd=1)
        active_frame.pack(fill="x", pady=2)
        
        active_label = tk.Label(
            active_frame,
            text="Active Connection:",
            font=('Arial', 9, 'bold'),
            fg='#4CAF50',
            bg='#3c3c3c'
        )
        active_label.pack(anchor="w", padx=5, pady=2)
        
        self.active_connection_label = tk.Label(
            active_frame,
            text="Loading...",
            font=('Arial', 8),
            fg='#ffffff',
            bg='#3c3c3c'
        )
        self.active_connection_label.pack(anchor="w", padx=5, pady=2)
        
        # معلومات IP
        ip_frame = tk.Frame(self.network_info_frame, bg='#3c3c3c', relief='raised', bd=1)
        ip_frame.pack(fill="x", pady=2)
        
        ip_label = tk.Label(
            ip_frame,
            text="IP Address:",
            font=('Arial', 9, 'bold'),
            fg='#2196F3',
            bg='#3c3c3c'
        )
        ip_label.pack(anchor="w", padx=5, pady=2)
        
        self.ip_address_label = tk.Label(
            ip_frame,
            text="Loading...",
            font=('Arial', 8),
            fg='#ffffff',
            bg='#3c3c3c'
        )
        self.ip_address_label.pack(anchor="w", padx=5, pady=2)
        
        # حالة الاتصال
        status_frame = tk.Frame(self.network_info_frame, bg='#3c3c3c', relief='raised', bd=1)
        status_frame.pack(fill="x", pady=2)
        
        status_label = tk.Label(
            status_frame,
            text="Status:",
            font=('Arial', 9, 'bold'),
            fg='#FF9800',
            bg='#3c3c3c'
        )
        status_label.pack(anchor="w", padx=5, pady=2)
        
        self.status_label = tk.Label(
            status_frame,
            text="Loading...",
            font=('Arial', 8),
            fg='#ffffff',
            bg='#3c3c3c'
        )
        self.status_label.pack(anchor="w", padx=5, pady=2)
        
        # معلومات إضافية
        info_frame = tk.Frame(self.network_info_frame, bg='#3c3c3c', relief='raised', bd=1)
        info_frame.pack(fill="x", pady=2)
        
        info_label = tk.Label(
            info_frame,
            text="Last Updated:",
            font=('Arial', 9, 'bold'),
            fg='#9C27B0',
            bg='#3c3c3c'
        )
        info_label.pack(anchor="w", padx=5, pady=2)
        
        self.last_updated_label = tk.Label(
            info_frame,
            text="Never",
            font=('Arial', 8),
            fg='#ffffff',
            bg='#3c3c3c'
        )
        self.last_updated_label.pack(anchor="w", padx=5, pady=2)
        
    def start_drag(self, event):
        """بدء سحب النافذة"""
        self.is_dragging = True
        self.drag_start_x = event.x_root - self.root.winfo_x()
        self.drag_start_y = event.y_root - self.root.winfo_y()
        
    def drag(self, event):
        """سحب النافذة"""
        if self.is_dragging:
            x = event.x_root - self.drag_start_x
            y = event.y_root - self.drag_start_y
            self.root.geometry(f"+{x}+{y}")
            
    def minimize_widget(self):
        """تصغير الكارت"""
        if self.is_minimized:
            self.root.deiconify()
            self.is_minimized = False
        else:
            # بدلاً من iconify، نخفي النافذة
            self.root.withdraw()
            self.is_minimized = True
            
    def close_widget(self):
        """إغلاق الكارت"""
        self.root.quit()
        
    def on_closing(self):
        """عند محاولة إغلاق النافذة"""
        self.close_widget()
    
    def on_widget_click(self, event):
        """عند النقر على الكارت"""
        # تجنب النقر على الأزرار
        widget = event.widget
        if widget.winfo_class() == 'Button':
            return
        
        # تأثير بصري عند النقر
        self.root.configure(bg='#404040')
        self.root.after(100, lambda: self.root.configure(bg='#2b2b2b'))
        
        # تأثير إضافي - تغيير لون الحدود
        self.root.configure(highlightbackground='#FF9800', highlightthickness=3)
        self.root.after(200, lambda: self.root.configure(highlightbackground='#2b2b2b', highlightthickness=0))
        
        # فتح Network Connections
        self.open_network_connections()
    
    def on_mouse_enter(self, event):
        """عند دخول الماوس للكارت"""
        # تغيير لون الحدود
        self.root.configure(highlightbackground='#4CAF50', highlightthickness=2)
    
    def on_mouse_leave(self, event):
        """عند خروج الماوس من الكارت"""
        # إزالة لون الحدود
        self.root.configure(highlightbackground='#2b2b2b', highlightthickness=0)
        
    def open_network_connections(self):
        """فتح Network Connections"""
        try:
            # فتح Network Connections باستخدام Control Panel
            subprocess.run([
                'rundll32.exe', 
                'shell32.dll,Control_RunDLL', 
                'ncpa.cpl'
            ], check=True)
        except Exception as e:
            # محاولة بديلة
            try:
                subprocess.run(['ncpa.cpl'], check=True)
            except:
                messagebox.showerror("خطأ", f"لا يمكن فتح Network Connections: {e}")
                
    def open_network_manager(self):
        """فتح Network Manager"""
        try:
            # فتح Network Manager
            if os.path.exists('network_manager_no_admin.py'):
                subprocess.Popen(['python', 'network_manager_no_admin.py'])
            elif os.path.exists('network_manager_tkinter.py'):
                subprocess.Popen(['python', 'network_manager_tkinter.py'])
            else:
                messagebox.showinfo("معلومات", "Network Manager غير موجود في المجلد الحالي")
        except Exception as e:
            messagebox.showerror("خطأ", f"لا يمكن فتح Network Manager: {e}")
                
    def get_network_info(self):
        """الحصول على معلومات الشبكة"""
        try:
            # الحصول على معلومات واجهات الشبكة
            interfaces = psutil.net_if_addrs()
            stats = psutil.net_if_stats()
            
            active_interfaces = []
            for interface_name, addresses in interfaces.items():
                if interface_name in stats and stats[interface_name].isup:
                    for addr in addresses:
                        if addr.family == 2:  # IPv4
                            active_interfaces.append({
                                'name': interface_name,
                                'ip': addr.address,
                                'status': 'Connected' if stats[interface_name].isup else 'Disconnected'
                            })
                            break
            
            return active_interfaces
        except Exception as e:
            print(f"خطأ في الحصول على معلومات الشبكة: {e}")
            return []
    
    def update_network_info(self):
        """تحديث معلومات الشبكة"""
        def update_thread():
            try:
                interfaces = self.get_network_info()
                current_time = time.strftime("%H:%M:%S")
                
                if interfaces:
                    # عرض أول واجهة نشطة
                    interface = interfaces[0]
                    self.root.after(0, lambda: self.active_connection_label.configure(
                        text=interface['name']
                    ))
                    self.root.after(0, lambda: self.ip_address_label.configure(
                        text=interface['ip']
                    ))
                    self.root.after(0, lambda: self.status_label.configure(
                        text=interface['status'],
                        fg='#4CAF50' if interface['status'] == 'Connected' else '#f44336'
                    ))
                else:
                    self.root.after(0, lambda: self.active_connection_label.configure(
                        text="No active connection"
                    ))
                    self.root.after(0, lambda: self.ip_address_label.configure(
                        text="N/A"
                    ))
                    self.root.after(0, lambda: self.status_label.configure(
                        text="Disconnected",
                        fg='#f44336'
                    ))
                
                # تحديث وقت آخر تحديث
                self.root.after(0, lambda: self.last_updated_label.configure(
                    text=current_time
                ))
            except Exception as e:
                print(f"خطأ في تحديث معلومات الشبكة: {e}")
        
        threading.Thread(target=update_thread, daemon=True).start()
    
    def auto_update(self):
        """التحديث التلقائي كل 5 ثوان"""
        self.update_network_info()
        self.root.after(5000, self.auto_update)
    
    def run(self):
        """تشغيل الكارت"""
        # وضع النافذة في الزاوية اليمنى العلوية
        self.root.geometry("+{}+{}".format(
            self.root.winfo_screenwidth() - 400,
            50
        ))
        
        self.root.mainloop()

def main():
    """الدالة الرئيسية"""
    print("🌐 Network Connections Desktop Widget - Advanced")
    print("=" * 50)
    print("✓ كارت سطح المكتب لـ Network Connections")
    print("✓ يظهر دائماً في المقدمة")
    print("✓ يمكن سحبه في أي مكان")
    print("✓ تحديث تلقائي للمعلومات")
    print("✓ فتح Network Manager مباشرة")
    print("✓ إمكانية التصغير")
    print()
    
    try:
        # إنشاء وتشغيل الكارت
        widget = NetworkDesktopWidgetAdvanced()
        widget.run()
    except Exception as e:
        print(f"❌ خطأ في تشغيل الكارت: {e}")
        input("اضغط Enter للخروج...")

if __name__ == "__main__":
    main()
