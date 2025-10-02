import os
import shutil
import time
import threading
import psutil
from pynput import keyboard
import tkinter as tk
from tkinter import ttk, filedialog
import sys

class StableFlashCopyUI:
    def __init__(self):
        self.target_directory = ""
        self.running = True
        self.copied_drives = set()
        self.monitor_thread = None
        
        self.setup_ui()
        
    def setup_ui(self):
        """ایجاد رابط کاربری پایدار"""
        self.root = tk.Tk()
        self.root.title("USB Monitor")
        self.root.geometry("400x180")
        self.root.resizable(False, False)
        self.root.protocol("WM_DELETE_WINDOW", self.safe_exit)
        
        # مرکز کردن پنجره
        self.center_window()
        
        # ایجاد المان‌های UI
        self.create_widgets()
        
    def center_window(self):
        """مرکز کردن پنجره"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def create_widgets(self):
        """ایجاد ویجت‌ها"""
        # عنوان
        title_label = ttk.Label(self.root, text="USB Auto Backup", 
                               font=('Arial', 14, 'bold'))
        title_label.pack(pady=10)
        
        # وضعیت انتخاب پوشه
        self.path_var = tk.StringVar(value="No folder selected")
        path_label = ttk.Label(self.root, textvariable=self.path_var, 
                              foreground='red')
        path_label.pack(pady=5)
        
        # فریم دکمه‌ها
        btn_frame = ttk.Frame(self.root)
        btn_frame.pack(pady=15)
        
        # دکمه انتخاب پوشه
        ttk.Button(btn_frame, text="Select Folder",
                  command=self.select_folder).pack(side=tk.LEFT, padx=5)
        
        # دکمه شروع
        self.start_btn = ttk.Button(btn_frame, text="Start Monitoring",
                                   command=self.start_monitoring)
        self.start_btn.pack(side=tk.LEFT, padx=5)
        
        # دکمه خروج
        ttk.Button(btn_frame, text="Exit",
                  command=self.safe_exit).pack(side=tk.LEFT, padx=5)
        
        # برچسب وضعیت
        self.status_var = tk.StringVar(value="Ready")
        status_label = ttk.Label(self.root, textvariable=self.status_var,
                                foreground='blue')
        status_label.pack(pady=5)
        
        # اطلاعات پایین
        info_label = ttk.Label(self.root, 
                              text="Press Ctrl+Alt+2 to exit hidden mode",
                              font=('Arial', 8),
                              foreground='gray')
        info_label.pack(side=tk.BOTTOM, pady=5)
    
    def select_folder(self):
        """انتخاب پوشه مقصد"""
        directory = filedialog.askdirectory(title="Select Backup Folder")
        if directory:
            self.target_directory = directory
            self.path_var.set(f"Selected: {os.path.basename(directory)}")
    
    def start_monitoring(self):
        """شروع مانیتورینگ"""
        if not self.target_directory:
            # استفاده از پوشه پیش‌فرض
            self.target_directory = os.path.join(
                os.path.expanduser("~"), 
                "Documents", 
                "USB_Backups"
            )
            os.makedirs(self.target_directory, exist_ok=True)
            self.path_var.set(f"Using: USB_Backups")
        
        # غیرفعال کردن دکمه شروع
        self.start_btn.config(state='disabled')
        self.status_var.set("Starting monitor...")
        
        # آپدیت UI
        self.root.update()
        
        # نمایش تأیید
        self.show_confirmation()
        
        # شروع مانیتورینگ در thread جداگانه
        self.start_background_services()
        
        # بستن UI بعد از 2 ثانیه
        self.root.after(2000, self.hide_ui)
    
    def show_confirmation(self):
        """نمایش پیام تأیید"""
        confirm = tk.Toplevel(self.root)
        confirm.title("Success")
        confirm.geometry("250x100")
        confirm.resizable(False, False)
        confirm.attributes('-topmost', True)
        
        # مرکز کردن
        confirm.update_idletasks()
        width = confirm.winfo_width()
        height = confirm.winfo_height()
        x = (confirm.winfo_screenwidth() // 2) - (width // 2)
        y = (confirm.winfo_screenheight() // 2) - (height // 2)
        confirm.geometry(f'{width}x{height}+{x}+{y}')
        
        tk.Label(confirm, text="✓ Monitoring Started!", 
                font=('Arial', 11), fg='green').pack(expand=True)
        
        # بستن خودکار
        confirm.after(1500, confirm.destroy)
    
    def hide_ui(self):
        """مخفی کردن UI به طور ایمن"""
        self.status_var.set("Monitoring in background...")
        self.root.update()
        time.sleep(0.5)
        
        # مخفی کردن پنجره اصلی
        self.root.withdraw()
    
    def start_background_services(self):
        """شروع سرویس‌های پس‌زمینه"""
        # شروع مانیتورینگ USB
        self.monitor_thread = threading.Thread(
            target=self.usb_monitor_worker, 
            daemon=True
        )
        self.monitor_thread.start()
        
        # شروع keyboard listener
        self.kb_listener_thread = threading.Thread(
            target=self.keyboard_listener_worker,
            daemon=True
        )
        self.kb_listener_thread.start()
    
    def usb_monitor_worker(self):
        """کارگر مانیتورینگ USB"""
        previous_drives = set(self.get_usb_drives())
        
        while self.running:
            try:
                current_drives = set(self.get_usb_drives())
                new_drives = current_drives - previous_drives
                
                for drive in new_drives:
                    if drive not in self.copied_drives:
                        self.copy_usb_content(drive)
                        self.copied_drives.add(drive)
                
                previous_drives = current_drives
                time.sleep(3)  # چک هر 3 ثانیه
                
            except Exception as e:
                time.sleep(5)
    
    def keyboard_listener_worker(self):
        """کارگر keyboard listener"""
        def on_press(key):
            try:
                # کلید ترکیبی برای خروج: Ctrl+Alt+2
                if (hasattr(key, 'vk') and key.vk == 50 and  # کلید 2
                    self.kb_controller.pressed(keyboard.Key.ctrl_l) and 
                    self.kb_controller.pressed(keyboard.Key.alt_l)):
                    
                    self.safe_exit()
                    return False
                    
            except AttributeError:
                pass
        
        self.kb_controller = keyboard.Controller()
        with keyboard.Listener(on_press=on_press) as listener:
            listener.join()
    
    def get_usb_drives(self):
        """شناسایی درایوهای USB"""
        usb_drives = []
        try:
            partitions = psutil.disk_partitions()
            for partition in partitions:
                if ('removable' in partition.opts or 
                    (hasattr(partition, 'device') and 
                     len(partition.device) == 3 and 
                     partition.device[1] == ':')):
                    try:
                        if os.path.exists(partition.mountpoint):
                            usb_drives.append(partition.mountpoint)
                    except:
                        pass
        except Exception as e:
            pass
        
        return usb_drives
    
    def copy_usb_content(self, source_path):
        """کپی محتوای USB"""
        try:
            drive_name = os.path.basename(source_path.rstrip('\\/'))
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            dest_path = os.path.join(
                self.target_directory, 
                f"USB_{drive_name}_{timestamp}"
            )
            
            # جلوگیری از دوباره کاری
            if os.path.exists(dest_path):
                return False
            
            if os.path.exists(source_path):
                shutil.copytree(source_path, dest_path)
                self.log_activity(f"Copied: {source_path}")
                return True
                
        except Exception as e:
            self.log_activity(f"Error: {str(e)}")
        
        return False
    
    def log_activity(self, message):
        """ثبت فعالیت‌ها"""
        try:
            log_path = os.path.join(self.target_directory, "backup_log.txt")
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            with open(log_path, "a", encoding="utf-8") as f:
                f.write(f"[{timestamp}] {message}\n")
        except:
            pass
    
    def safe_exit(self):
        """خروج ایمن از برنامه"""
        self.running = False
        self.status_var.set("Exiting...")
        
        # آپدیت UI نهایی
        if self.root:
            try:
                self.root.update()
                time.sleep(0.5)
                self.root.quit()
                self.root.destroy()
            except:
                pass
        
        # خروج از برنامه
        os._exit(0)
    
    def run(self):
        """اجرای برنامه"""
        try:
            self.root.mainloop()
        except Exception as e:
            self.safe_exit()

if __name__ == "__main__":
    app = StableFlashCopyUI()
    app.run()