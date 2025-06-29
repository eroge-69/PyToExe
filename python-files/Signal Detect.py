import subprocess
import re
import platform
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from threading import Thread
import csv
import sys
import ctypes
import os

class WiFiScannerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Wi-Fi Network Scanner")
        self.root.geometry("900x650")
        self.root.resizable(True, True)
        
        # شناسایی سیستم عامل و وضعیت دسترسی
        self.os_name = platform.system()
        self.is_admin = self.check_admin()
        
        # تنظیم تم و ایجاد رابط کاربری
        self.setup_theme()
        self.create_widgets()
        
        # نمایش هشدار در صورت نیاز به دسترسی ادمین
        if self.os_name == "Windows" and not self.is_admin:
            self.show_admin_warning()

    def setup_theme(self):
        """تنظیم تم تاریک برای برنامه"""
        self.root.tk_setPalette(
            background='#2e2e2e',
            foreground='white',
            activeBackground='#3e3e3e',
            activeForeground='white'
        )
        
        self.style = ttk.Style()
        self.style.configure('TButton', font=('Arial', 10), padding=6)
        self.style.configure('TLabel', font=('Arial', 10))
        self.style.configure('Header.TLabel', font=('Arial', 14, 'bold'))
        self.style.configure('Treeview', 
                           background='#3e3e3e',
                           fieldbackground='#3e3e3e',
                           foreground='white')
        self.style.configure('Treeview.Heading', 
                           background='#2e2e2e',
                           foreground='white')
        self.style.map('Treeview',
                      background=[('selected', '#1a73e8')])

    def create_widgets(self):
        """ایجاد و چیدمان ویجت‌های رابط کاربری"""
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # بخش عنوان
        title_frame = ttk.Frame(main_frame)
        title_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(
            title_frame, 
            text="Wi-Fi Network Scanner", 
            style='Header.TLabel'
        ).pack(side=tk.LEFT)
        
        # نمایش وضعیت دسترسی ادمین
        if self.os_name == "Windows":
            admin_status = " (Administrator)" if self.is_admin else " (Limited Access)"
            status_color = "green" if self.is_admin else "orange"
            ttk.Label(
                title_frame,
                text=admin_status,
                foreground=status_color
            ).pack(side=tk.LEFT, padx=10)
        
        # بخش دکمه‌های کنترل
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=10)
        
        self.scan_button = ttk.Button(
            control_frame,
            text="Scan Networks",
            command=self.start_scan_thread
        )
        self.scan_button.pack(side=tk.LEFT, padx=5)
        
        self.export_button = ttk.Button(
            control_frame,
            text="Export to CSV",
            command=self.export_to_csv,
            state=tk.DISABLED
        )
        self.export_button.pack(side=tk.RIGHT, padx=5)
        
        # نوار پیشرفت
        self.progress = ttk.Progressbar(
            main_frame,
            orient=tk.HORIZONTAL,
            length=400,
            mode='indeterminate'
        )
        
        # جدول نتایج
        tree_frame = ttk.Frame(main_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        # تعریف ستون‌های جدول
        columns = [
            ('SSID', 'Network Name', 180, tk.W),
            ('BSSID', 'MAC Address', 150, tk.W),
            ('Signal', 'Signal Strength', 120, tk.CENTER),
            ('Band', 'Frequency Band', 100, tk.CENTER),
            ('Channel', 'Channel', 70, tk.CENTER),
            ('Security', 'Security Type', 120, tk.W)
        ]
        
        self.tree = ttk.Treeview(
            tree_frame,
            columns=[col[0] for col in columns],
            show='headings',
            height=20
        )
        
        # تنظیم ستون‌ها
        for col in columns:
            self.tree.heading(col[0], text=col[1])
            self.tree.column(col[0], width=col[2], anchor=col[3])
        
        # نوار اسکرول
        scrollbar = ttk.Scrollbar(
            tree_frame,
            orient=tk.VERTICAL,
            command=self.tree.yview
        )
        self.tree.configure(yscroll=scrollbar.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # نوار وضعیت
        status_frame = ttk.Frame(main_frame)
        status_frame.pack(fill=tk.X, pady=10)
        
        self.status_label = ttk.Label(
            status_frame,
            text=f"System: {self.os_name} | Ready"
        )
        self.status_label.pack(side=tk.LEFT)

    def show_admin_warning(self):
        """نمایش هشدار درباره نیاز به دسترسی ادمین"""
        messagebox.showwarning(
            "Limited Access",
            "For complete Wi-Fi scanning capabilities, administrator privileges are required.\n\n"
            "You can still scan networks, but some information may not be available.\n"
            "To get full access, please restart the program as administrator.",
            parent=self.root
        )

    def check_admin(self):
        """بررسی وضعیت دسترسی ادمین"""
        try:
            if self.os_name == "Windows":
                return ctypes.windll.shell32.IsUserAnAdmin() != 0
            return os.getuid() == 0  # برای سیستم‌های Unix-like
        except:
            return False

    def start_scan_thread(self):
        """شروع عملیات اسکن در یک رشته جداگانه"""
        self.toggle_ui_state(False)
        self.progress.pack(pady=10)
        self.progress.start()
        self.status_label.config(text=f"System: {self.os_name} | Scanning...")
        
        # پاکسازی نتایج قبلی
        self.tree.delete(*self.tree.get_children())
        
        # ایجاد و شروع رشته اسکن
        scan_thread = Thread(target=self.perform_scan)
        scan_thread.start()
        
        # بررسی وضعیت اسکن
        self.monitor_scan_thread(scan_thread)
    
    def monitor_scan_thread(self, thread):
        """مانیتورینگ وضعیت رشته اسکن"""
        if thread.is_alive():
            self.root.after(100, self.monitor_scan_thread, thread)
        else:
            self.progress.stop()
            self.progress.pack_forget()
            self.toggle_ui_state(True)
            self.status_label.config(text=f"System: {self.os_name} | Ready")

    def perform_scan(self):
        """انجام عملیات اسکن شبکه‌های وای‌فای"""
        try:
            if self.os_name == "Windows":
                networks = self.scan_windows()
            elif self.os_name == "Linux":
                networks = self.scan_linux()
            elif self.os_name == "Darwin":
                networks = self.scan_mac()
            else:
                messagebox.showerror("Error", "Unsupported operating system", parent=self.root)
                return
            
            self.display_results(networks)
                
        except Exception as e:
            messagebox.showerror("Error", f"Scan failed: {str(e)}", parent=self.root)

    def display_results(self, networks):
        """نمایش نتایج اسکن در جدول"""
        for network in networks:
            self.tree.insert('', tk.END, values=(
                network.get('SSID', 'Hidden'),
                network.get('BSSID', 'N/A'),
                network.get('Signal', 'N/A'),
                network.get('Band', 'N/A'),
                network.get('Channel', 'N/A'),
                network.get('Security', 'N/A')
            ))
        
        # فعال کردن دکمه export در صورت وجود نتایج
        if self.tree.get_children():
            self.export_button.config(state=tk.NORMAL)

    def scan_windows(self):
        """اسکن شبکه‌های وای‌فای در ویندوز"""
        try:
            # ابتدا روش پیشرفته را امتحان می‌کنیم
            result = subprocess.run(
                ["netsh", "wlan", "show", "networks", "mode=Bssid"],
                capture_output=True,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            if result.returncode == 0:
                return self.parse_windows_advanced(result.stdout)
            
            # اگر روش پیشرفته جواب نداد، از روش ساده استفاده می‌کنیم
            return self.scan_windows_basic()
        
        except Exception as e:
            messagebox.showerror("Error", f"Windows scan failed: {str(e)}", parent=self.root)
            return []

    def parse_windows_advanced(self, output):
        """تجزیه و تحلیل نتایج اسکن پیشرفته ویندوز"""
        networks = []
        current = {}
        
        for line in output.split('\n'):
            line = line.strip()
            
            if line.startswith("SSID"):
                if current:
                    networks.append(current)
                current = {'SSID': line.split(':')[-1].strip()}
            
            elif "Signal" in line:
                current['Signal'] = line.split(':')[-1].strip()
            
            elif "Radio type" in line:
                radio = line.split(':')[-1].strip()
                current['Band'] = '5 GHz' if '802.11a' in radio or '802.11ac' in radio else '2.4 GHz'
            
            elif "BSSID" in line:
                current['BSSID'] = line.split(':')[-1].strip()
            
            elif "Channel" in line:
                current['Channel'] = line.split(':')[-1].strip()
            
            elif "Authentication" in line:
                current['Security'] = line.split(':')[-1].strip()
        
        if current:
            networks.append(current)
        
        return networks

    def scan_windows_basic(self):
        """اسکن پایه شبکه‌های وای‌فای در ویندوز"""
        try:
            result = subprocess.run(
                ["netsh", "wlan", "show", "networks"],
                capture_output=True,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            networks = []
            current = {}
            
            for line in result.stdout.split('\n'):
                line = line.strip()
                
                if "SSID" in line and "BSSID" not in line:
                    if current:
                        networks.append(current)
                    current = {
                        'SSID': line.split(':')[-1].strip(),
                        'Signal': 'N/A',
                        'Band': 'N/A',
                        'BSSID': 'N/A',
                        'Channel': 'N/A',
                        'Security': 'N/A'
                    }
                
                elif "Authentication" in line:
                    current['Security'] = line.split(':')[-1].strip()
            
            if current:
                networks.append(current)
            
            return networks
        
        except Exception as e:
            messagebox.showerror("Error", f"Basic scan failed: {str(e)}", parent=self.root)
            return []

    def scan_linux(self):
        """اسکن شبکه‌های وای‌فای در لینوکس"""
        try:
            result = subprocess.run(
                ["iwlist", "scan"],
                capture_output=True,
                text=True
            )
            
            networks = []
            current = {}
            
            for line in result.stdout.split('\n'):
                line = line.strip()
                
                if "ESSID:" in line:
                    if current:
                        networks.append(current)
                    current = {
                        'SSID': line.split('"')[1],
                        'Signal': 'N/A',
                        'Band': 'N/A',
                        'BSSID': 'N/A',
                        'Channel': 'N/A',
                        'Security': 'N/A'
                    }
                
                elif "Signal level=" in line:
                    signal = line.split("Signal level=")[1].split(" ")[0]
                    current['Signal'] = f"{signal} dBm"
                
                elif "Frequency:" in line:
                    freq = line.split("Frequency:")[1].split(" ")[1]
                    current['Band'] = '5 GHz' if freq.startswith("5") else '2.4 GHz'
                
                elif "Address:" in line:
                    current['BSSID'] = line.split("Address: ")[1]
                
                elif "Channel:" in line:
                    current['Channel'] = line.split("Channel:")[1].strip()
                
                elif "IE: IEEE 802.11i/WPA2" in line:
                    current['Security'] = 'WPA2'
                elif "Encryption key:on" in line:
                    if 'Security' not in current:
                        current['Security'] = 'WEP'
            
            if current:
                networks.append(current)
            
            return networks
        
        except FileNotFoundError:
            messagebox.showerror("Error", "iwlist command not found. Please install wireless-tools.", parent=self.root)
            return []
        except Exception as e:
            messagebox.showerror("Error", f"Linux scan failed: {str(e)}", parent=self.root)
            return []

    def scan_mac(self):
        """اسکن شبکه‌های وای‌فای در مک"""
        try:
            result = subprocess.run(
                ["/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport", "-s"],
                capture_output=True,
                text=True
            )
            
            networks = []
            pattern = re.compile(r'^(.*?)\s+([a-fA-F0-9:]{17})\s+(-\d+)\s+([^\s]+)\s+([^\s]+)\s+([^\s]+)\s+([^\s]+)\s+([^\s]+)')
            
            for line in result.stdout.split('\n')[1:]:
                match = pattern.match(line)
                if match:
                    ssid = match.group(1).strip()
                    bssid = match.group(2).strip()
                    signal = match.group(3).strip() + " dBm"
                    channel = match.group(4).strip()
                    security = match.group(7).strip()
                    
                    band = "5 GHz" if channel.endswith(")") and "5" in channel else "2.4 GHz"
                    
                    networks.append({
                        'SSID': ssid,
                        'BSSID': bssid,
                        'Signal': signal,
                        'Band': band,
                        'Channel': channel.split('(')[0],
                        'Security': security
                    })
            
            return networks
        
        except FileNotFoundError:
            messagebox.showerror("Error", "airport command not found", parent=self.root)
            return []
        except Exception as e:
            messagebox.showerror("Error", f"Mac scan failed: {str(e)}", parent=self.root)
            return []

    def export_to_csv(self):
        """ذخیره نتایج در فایل CSV"""
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV Files", "*.csv")],
                title="Save Scan Results"
            )
            
            if not filename:
                return
            
            with open(filename, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                
                # نوشتن هدرها
                headers = [self.tree.heading(col)['text'] for col in self.tree['columns']]
                writer.writerow(headers)
                
                # نوشتن داده‌ها
                for item in self.tree.get_children():
                    writer.writerow(self.tree.item(item)['values'])
            
            messagebox.showinfo("Success", f"Results exported to:\n{filename}", parent=self.root)
        
        except Exception as e:
            messagebox.showerror("Error", f"Export failed: {str(e)}", parent=self.root)

    def toggle_ui_state(self, enabled):
        """فعال یا غیرفعال کردن عناصر رابط کاربری"""
        state = tk.NORMAL if enabled else tk.DISABLED
        self.scan_button.config(state=state)
        self.export_button.config(state=state if self.tree.get_children() else tk.DISABLED)

if __name__ == "__main__":
    root = tk.Tk()
    app = WiFiScannerApp(root)
    root.mainloop()