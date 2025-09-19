import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import random
import requests
import threading
from datetime import datetime

class ProfessionalUAGenerator:
    def __init__(self, root):
        self.root = root
        self.root.title("🌟 Professional User Agent Generator Pro")
        self.root.geometry("1300x950")
        self.root.configure(bg='#2c3e50')
        self.root.resizable(True, True)
        
        # স্টাইল কনফিগারেশন
        self.setup_styles()
        
        # ডেটা সেটআপ
        self.setup_data()
        
        # UI তৈরি
        self.create_widgets()
        
    def setup_styles(self):
        """আধুনিক স্টাইল সেটআপ"""
        style = ttk.Style()
        
        # থিম সেটআপ
        style.theme_use('clam')
        
        # কাস্টম স্টাইল
        style.configure('Main.TFrame', background='#2c3e50')
        style.configure('Header.TLabel', background='#2c3e50', foreground='#ecf0f1', 
                       font=('Segoe UI', 20, 'bold'))
        style.configure('Section.TLabelframe', background='#34495e', foreground='#ecf0f1',
                       font=('Segoe UI', 12, 'bold'))
        style.configure('Section.TLabelframe.Label', background='#34495e', foreground='#ecf0f1')
        style.configure('Label.TLabel', background='#34495e', foreground='#ecf0f1',
                       font=('Segoe UI', 10))
        style.configure('Combo.TCombobox', fieldbackground='#ecf0f1', background='#ecf0f1')
        style.configure('Button.TButton', background='#3498db', foreground='white',
                       font=('Segoe UI', 10, 'bold'), borderwidth=1)
        style.map('Button.TButton', background=[('active', '#2980b9')])
        
        style.configure('Generate.TButton', background='#27ae60')
        style.map('Generate.TButton', background=[('active', '#229954')])
        
        style.configure('Copy.TButton', background='#f39c12')
        style.map('Copy.TButton', background=[('active', '#e67e22')])
        
        style.configure('Clear.TButton', background='#e74c3c')
        style.map('Clear.TButton', background=[('active', '#c0392b')])
        
        style.configure('Save.TButton', background='#9b59b6')
        style.map('Save.TButton', background=[('active', '#8e44ad')])
        
        style.configure('Test.TButton', background='#1abc9c')
        style.map('Test.TButton', background=[('active', '#16a085')])
        
        style.configure('Status.TLabel', background='#2c3e50', foreground='#bdc3c7',
                       font=('Segoe UI', 9))
        
    def setup_data(self):
        """সমস্ত ডেটা ইনিশিয়ালাইজ করুন"""
        # ডিভাইস টাইপ
        self.device_types = ["📱 iPhone", "🤖 Android", "📟 Samsung", "🔴 Redmi/Xiaomi", 
                           "🔷 Motorola", "💻 iPad", "🖥️ Windows PC", "🍎 Mac"]
        
        # iOS ভার্সন
        self.ios_versions = [
            "17.0", "17.0.1", "17.0.2", "17.0.3", "17.1", "17.1.1", "17.1.2",
            "17.2", "17.2.1", "17.3", "17.3.1", "17.4", "17.4.1", "17.5",
            "17.5.1", "17.6", "17.6.1", "17.7", "18.0", "18.0.1", "18.1",
            "18.1.1", "18.2", "18.2.1", "18.3", "18.3.1", "18.4", "18.5"
        ]
        
        # Android ভার্সন
        self.android_versions = [
            "10", "11", "12", "12L", "13", "14", "15",
            "10.0", "11.0", "12.0", "13.0", "14.0", "15.0",
            "10.1", "11.1", "12.1", "13.1"
        ]
        
        # iPhone মডেল
        self.iphone_models = [
            "iPhone 14 Pro", "iPhone 14 Pro Max", "iPhone 15", "iPhone 15 Plus",
            "iPhone 15 Pro", "iPhone 15 Pro Max", "iPhone 16", "iPhone 16 Plus",
            "iPhone 16 Pro", "iPhone 16 Pro Max"
        ]
        
        # Samsung মডেল
        self.samsung_models = [
            "Galaxy S23", "Galaxy S23+", "Galaxy S23 Ultra", "Galaxy Z Flip 5",
            "Galaxy Z Fold 5", "Galaxy A54", "Galaxy M54", "Galaxy Note 20"
        ]
        
        # Xiaomi/Redmi মডেল
        self.xiaomi_models = [
            "Redmi Note 12", "Redmi Note 12 Pro", "Xiaomi 13", "Xiaomi 13 Pro",
            "Poco X5", "Poco F5", "Redmi 12", "Xiaomi 14"
        ]
        
        # Motorola মডেল
        self.motorola_models = [
            "Moto G Power", "Moto G Stylus", "Moto Edge", "Moto Razr",
            "Moto One", "Moto Z4", "Moto X4", "Moto E7"
        ]
        
        # Android ডিভাইস মডেল (সাধারণ)
        self.android_models = self.samsung_models + self.xiaomi_models + self.motorola_models
        
        # ব্রাউজার টাইপ
        self.browser_types = [
            "🌐 Chrome", "🍎 Safari", "🦊 Firefox", "🧩 Edge", "🚢 Opera",
            "📱 Samsung Browser", "🔶 UC Browser", "🛡️ Brave", "⚛️ Chromium"
        ]
        
        # দেশ এবং ভাষা (আরও অনেক দেশ যোগ করা হয়েছে)
        self.countries = {
            "🇺🇸 USA": "en_US",
            "🇬🇧 UK": "en_GB",
            "🇮🇳 India": "en_IN",
            "🇩🇪 Germany": "de_DE",
            "🇫🇷 France": "fr_FR",
            "🇪🇸 Spain": "es_ES",
            "🇸🇪 Sweden": "sv_SE",
            "🇮🇹 Italy": "it_IT",
            "🇯🇵 Japan": "ja_JP",
            "🇨🇳 China": "zh_CN",
            "🇷🇺 Russia": "ru_RU",
            "🇧🇷 Brazil": "pt_BR",
            "🇸🇦 Saudi Arabia": "ar_SA",
            "🇧🇩 Bangladesh": "bn_BD",
            "🇹🇷 Turkey": "tr_TR",
            "🇳🇱 Netherlands": "nl_NL",
            "🇰🇷 South Korea": "ko_KR",
            "🇨🇦 Canada": "en_CA",
            "🇦🇺 Australia": "en_AU",
            "🇲🇽 Mexico": "es_MX",
            "🇦🇷 Argentina": "es_AR",
            "🇨🇴 Colombia": "es_CO",
            "🇵🇪 Peru": "es_PE",
            "🇨🇱 Chile": "es_CL",
            "🇻🇪 Venezuela": "es_VE",
            "🇵🇹 Portugal": "pt_PT",
            "🇬🇷 Greece": "el_GR",
            "🇵🇱 Poland": "pl_PL",
            "🇺🇦 Ukraine": "uk_UA",
            "🇷🇴 Romania": "ro_RO",
            "🇨🇿 Czech": "cs_CZ",
            "🇭🇺 Hungary": "hu_HU",
            "🇩🇰 Denmark": "da_DK",
            "🇳🇴 Norway": "no_NO",
            "🇫🇮 Finland": "fi_FI",
            "🇮🇩 Indonesia": "id_ID",
            "🇲🇾 Malaysia": "ms_MY",
            "🇹🇭 Thailand": "th_TH",
            "🇻🇳 Vietnam": "vi_VN",
            "🇵🇭 Philippines": "tl_PH",
            "🇪🇬 Egypt": "ar_EG",
            "🇿🇦 South Africa": "en_ZA",
            "🇳🇬 Nigeria": "en_NG",
            "🇰🇪 Kenya": "sw_KE",
            "🇮🇱 Israel": "he_IL",
            "🇮🇷 Iran": "fa_IR",
            "🇵🇰 Pakistan": "ur_PK"
        }
        
    def create_widgets(self):
        """আধুনিক UI উইজেট তৈরি করুন"""
        # মেইন ফ্রেম
        main_frame = ttk.Frame(self.root, style='Main.TFrame', padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # হেডার
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(header_frame, text="🚀 Professional User Agent Generator", 
                 style='Header.TLabel').pack(side=tk.LEFT)
        
        # সেটিংস ফ্রেম
        settings_frame = ttk.LabelFrame(main_frame, text="⚙️  Configuration Settings", 
                                       style='Section.TLabelframe')
        settings_frame.pack(fill=tk.X, pady=10)
        
        # প্রথম সারি - ডিভাইস এবং মডেল
        row1_frame = ttk.Frame(settings_frame)
        row1_frame.pack(fill=tk.X, pady=10, padx=15)
        
        ttk.Label(row1_frame, text="📱 Device Type:", style='Label.TLabel', width=15).grid(row=0, column=0, sticky=tk.W, padx=5)
        self.device_var = tk.StringVar(value="📱 iPhone")
        device_combo = ttk.Combobox(row1_frame, textvariable=self.device_var, 
                                   values=self.device_types, state="readonly", width=20, style='Combo.TCombobox')
        device_combo.grid(row=0, column=1, padx=5)
        device_combo.bind("<<ComboboxSelected>>", self.on_device_change)
        
        ttk.Label(row1_frame, text="🔧 Device Model:", style='Label.TLabel', width=15).grid(row=0, column=2, sticky=tk.W, padx=5)
        self.model_var = tk.StringVar(value="iPhone 15 Pro")
        self.model_combo = ttk.Combobox(row1_frame, textvariable=self.model_var, 
                                       values=self.iphone_models, state="readonly", width=20, style='Combo.TCombobox')
        self.model_combo.grid(row=0, column=3, padx=5)
        
        # দ্বিতীয় সারি - OS এবং ব্রাউজার
        row2_frame = ttk.Frame(settings_frame)
        row2_frame.pack(fill=tk.X, pady=10, padx=15)
        
        ttk.Label(row2_frame, text="💾 OS Version:", style='Label.TLabel', width=15).grid(row=0, column=0, sticky=tk.W, padx=5)
        self.os_var = tk.StringVar(value="17.0")
        self.os_combo = ttt.Combobox(row2_frame, textvariable=self.os_var, 
                                    values=self.ios_versions, state="readonly", width=20, style='Combo.TCombobox')
        self.os_combo.grid(row=0, column=1, padx=5)
        
        ttk.Label(row2_frame, text="🌐 Browser:", style='Label.TLabel', width=15).grid(row=0, column=2, sticky=tk.W, padx=5)
        self.browser_var = tk.StringVar(value="🍎 Safari")
        browser_combo = ttk.Combobox(row2_frame, textvariable=self.browser_var, 
                                    values=self.browser_types, state="readonly", width=20, style='Combo.TCombobox')
        browser_combo.grid(row=0, column=3, padx=5)
        
        # তৃতীয় সারি - দেশ এবং সংখ্যা
        row3_frame = ttk.Frame(settings_frame)
        row3_frame.pack(fill=tk.X, pady=10, padx=15)
        
        ttk.Label(row3_frame, text="🇺🇳 Country:", style='Label.TLabel', width=15).grid(row=0, column=0, sticky=tk.W, padx=5)
        self.country_var = tk.StringVar(value="🇺🇸 USA")
        country_combo = ttk.Combobox(row3_frame, textvariable=self.country_var, 
                                    values=list(self.countries.keys()), state="readonly", width=20, style='Combo.TCombobox')
        country_combo.grid(row=0, column=1, padx=5)
        
        ttk.Label(row3_frame, text="🔢 Number of UAs:", style='Label.TLabel', width=15).grid(row=0, column=2, sticky=tk.W, padx=5)
        self.quantity_var = tk.StringVar(value="10")
        quantity_spin = ttk.Spinbox(row3_frame, from_=1, to=1000, textvariable=self.quantity_var, width=18)
        quantity_spin.grid(row=0, column=3, padx=5)
        
        # বাটন ফ্রেম
        button_frame = ttk.Frame(settings_frame)
        button_frame.pack(fill=tk.X, pady=15, padx=15)
        
        ttk.Button(button_frame, text="🔄 Generate", command=self.generate_uas, style='Generate.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="📋 Copy All", command=self.copy_all, style='Copy.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="🧹 Clear", command=self.clear_text, style='Clear.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="💾 Save to File", command=self.save_to_file, style='Save.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="🧪 Test Selected", command=self.test_selected, style='Test.TButton').pack(side=tk.LEFT, padx=5)
        
        # আউটপুট ফ্রেম
        output_frame = ttk.LabelFrame(main_frame, text="📝 Generated User Agents", style='Section.TLabelframe')
        output_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # টেক্সট এরিয়া
        self.text_area = scrolledtext.ScrolledText(output_frame, width=120, height=25, wrap=tk.WORD, 
                                                  font=("Consolas", 10), bg='#ecf0f1', fg='#2c3e50')
        self.text_area.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # স্ট্যাটাস বার
        self.status_var = tk.StringVar(value="✅ Ready to generate user agents")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, style='Status.TLabel')
        status_bar.pack(fill=tk.X, pady=(5, 0))
        
    def on_device_change(self, event):
        """ডিভাইস টাইপ পরিবর্তন হলে মডেল এবং OS আপডেট করুন"""
        device_type = self.device_var.get()
        
        if "iPhone" in device_type:
            self.model_combo['values'] = self.iphone_models
            self.model_var.set("iPhone 15 Pro")
            self.os_combo['values'] = self.ios_versions
            self.os_var.set("17.0")
        elif "Android" in device_type or "Samsung" in device_type or "Redmi" in device_type or "Motorola" in device_type:
            self.model_combo['values'] = self.android_models
            self.model_var.set("Galaxy S23")
            self.os_combo['values'] = self.android_versions
            self.os_var.set("13")
        elif "iPad" in device_type:
            self.model_combo['values'] = ["iPad Pro", "iPad Air", "iPad Mini", "iPad 10th Gen"]
            self.model_var.set("iPad Pro")
            self.os_combo['values'] = self.ios_versions
            self.os_var.set("17.0")
        else:
            self.model_combo['values'] = ["Generic Device"]
            self.model_var.set("Generic Device")
            self.os_combo['values'] = ["10", "11", "12"]
            self.os_var.set("10")
    
    def generate_user_agent(self):
        """ইউজার এজেন্ট জেনারেট করুন"""
        device_type = self.device_var.get()
        device_model = self.model_var.get()
        os_version = self.os_var.get()
        browser_type = self.browser_var.get()
        country = self.country_var.get()
        language = self.countries[country]
        
        # ইমোজি সরিয়ে ফেলুন
        device_type_clean = device_type.split(' ')[-1]
        browser_type_clean = browser_type.split(' ')[-1]
        
        if "iPhone" in device_type:
            if "Safari" in browser_type:
                return (f"Mozilla/5.0 (iPhone; CPU iPhone OS {os_version.replace('.', '_')} like Mac OS X) "
                       f"AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 "
                       f"Mobile/15E148 Safari/604.1")
            else:
                return (f"Mozilla/5.0 (iPhone; CPU iPhone OS {os_version.replace('.', '_')} like Mac OS X) "
                       f"AppleWebKit/605.1.15 (KHTML, like Gecko) "
                       f"Mobile/15E148 {browser_type_clean}/120.0.0.0")
        
        elif "Android" in device_type or "Samsung" in device_type or "Redmi" in device_type or "Motorola" in device_type:
            if "Samsung" in device_type:
                return (f"Mozilla/5.0 (Linux; Android {os_version}; {device_model}) "
                       f"AppleWebKit/537.36 (KHTML, like Gecko) "
                       f"SamsungBrowser/20.0 Chrome/120.0.0.0 Mobile Safari/537.36")
            else:
                return (f"Mozilla/5.0 (Linux; Android {os_version}; {device_model}) "
                       f"AppleWebKit/537.36 (KHTML, like Gecko) "
                       f"Chrome/120.0.0.0 Mobile Safari/537.36")
        
        else:
            return (f"Mozilla/5.0 ({device_type_clean}; {device_model}; "
                   f"OS {os_version}) AppleWebKit/537.36 "
                   f"(KHTML, like Gecko) {browser_type_clean}/120.0.0.0 Safari/537.36")
    
    def generate_uas(self):
        """একাধিক ইউজার এজেন্ট জেনারেট করুন"""
        try:
            quantity = int(self.quantity_var.get())
            if quantity <= 0:
                messagebox.showerror("Error", "Please enter a valid number greater than 0")
                return
            
            self.status_var.set(f"⏳ Generating {quantity} user agents...")
            self.text_area.delete(1.0, tk.END)
            
            # থ্রেডে জেনারেট করুন
            thread = threading.Thread(target=self._generate_in_thread, args=(quantity,))
            thread.daemon = True
            thread.start()
            
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number")
    
    def _generate_in_thread(self, quantity):
        """ব্যাকগ্রাউন্ডে ইউজার এজেন্ট জেনারেট করুন"""
        uas = []
        for i in range(quantity):
            ua = self.generate_user_agent()
            uas.append(f"{i+1}. {ua}")
            
            if i % 10 == 0 or i == quantity - 1:
                self.root.after(0, self._update_text_area, uas[-min(10, len(uas)):])
                uas = []
        
        self.root.after(0, self._generation_complete, quantity)
    
    def _update_text_area(self, uas):
        """টেক্সট এরিয়া আপডেট করুন"""
        for ua in uas:
            self.text_area.insert(tk.END, ua + "\n\n")
        self.text_area.see(tk.END)
    
    def _generation_complete(self, quantity):
        """জেনারেশন সম্পূর্ণ হলে স্ট্যাটাস আপডেট করুন"""
        self.status_var.set(f"✅ Successfully generated {quantity} user agents")
    
    def copy_all(self):
        """সমস্ত ইউজার এজেন্ট কপি করুন"""
        self.text_area.clipboard_clear()
        self.text_area.clipboard_append(self.text_area.get(1.0, tk.END))
        self.status_var.set("📋 All user agents copied to clipboard")
    
    def clear_text(self):
        """টেক্সট এরিয়া ক্লিয়ার করুন"""
        self.text_area.delete(1.0, tk.END)
        self.status_var.set("🧹 Text area cleared")
    
    def save_to_file(self):
        """ফাইলে সেভ করুন"""
        content = self.text_area.get(1.0, tk.END)
        if not content.strip():
            messagebox.showwarning("Warning", "No user agents to save")
            return
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            title="Save user agents to file"
        )
        
        if file_path:
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)
                self.status_var.set(f"💾 User agents saved to {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Could not save file: {str(e)}")
    
    def test_selected(self):
        """নির্বাচিত ইউজার এজেন্ট টেস্ট করুন"""
        selected_text = self.text_area.get(tk.SEL_FIRST, tk.SEL_LAST)
        if not selected_text.strip():
            messagebox.showwarning("Warning", "Please select a user agent to test")
            return
        
        ua = selected_text.split('\n')[0].strip()
        if ua.startswith(tuple(str(i) for i in range(10))):
            ua = ' '.join(ua.split(' ')[1:])
        
        if not ua:
            messagebox.showwarning("Warning", "No valid user agent selected")
            return
        
        self.status_var.set(f"🧪 Testing user agent: {ua[:50]}...")
        
        thread = threading.Thread(target=self._test_in_thread, args=(ua,))
        thread.daemon = True
        thread.start()
    
    def _test_in_thread(self, ua):
        """ব্যাকগ্রাউন্ডে ইউজার এজেন্ট টেস্ট করুন"""
        try:
            headers = {"User-Agent": ua}
            response = requests.get("https://httpbin.org/user-agent", headers=headers, timeout=10)
            
            if response.status_code == 200:
                self.root.after(0, lambda: self.status_var.set("✅ Test successful - user agent is working"))
            else:
                self.root.after(0, lambda: self.status_var.set("❌ Test failed - user agent may not be valid"))
                
        except Exception as e:
            self.root.after(0, lambda: self.status_var.set(f"⚠️ Test error: {str(e)}"))

if __name__ == "__main__":
    root = tk.Tk()
    app = ProfessionalUAGenerator(root)
    root.mainloop()