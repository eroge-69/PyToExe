import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
import re

class SmartDBCConverter:
    def __init__(self):
        self.required_columns = ['Message ID', 'Message Name', 'Message Source', 'Name']
    
    def read_excel(self, file_path):
        """Excel'i oku"""
        try:
            df = pd.read_excel(file_path)
            df = df.dropna(how='all')
            df.columns = [str(col).strip() for col in df.columns]
            
            missing_cols = [col for col in self.required_columns if col not in df.columns]
            if missing_cols:
                raise Exception(f"Eksik sütunlar: {', '.join(missing_cols)}")
                
            return df
        except Exception as e:
            raise Exception(f"Excel okuma hatası: {str(e)}")
    
    def safe_int(self, value, default=0):
        """Güvenli integer dönüşümü"""
        if pd.isna(value):
            return default
        try:
            if isinstance(value, str):
                value = value.strip()
                if value.startswith(('0x', '0X')):
                    return int(value, 16)
                match = re.search(r'(\d+)', value)
                if match:
                    return int(match.group(1))
                return default
            return int(float(value))
        except:
            return default
    
    def safe_float(self, value, default=0.0):
        """Güvenli float dönüşümü"""
        if pd.isna(value):
            return default
        try:
            if isinstance(value, str):
                match = re.search(r'([-+]?\d*\.?\d+)', value)
                if match:
                    return float(match.group(1))
                return default
            return float(value)
        except:
            return default
    
    def clean_name(self, name):
        """İsimleri temizle"""
        if pd.isna(name):
            return "Unknown"
        name = str(name).strip()
        name = re.sub(r'[^\w]', '_', name)
        name = re.sub(r'_+', '_', name)
        name = name.strip('_')
        return name if name else "Unknown"
    
    def detect_byte_order_from_offsets(self, df):
        """Byte Offset ve Bit Offset değerlerine göre byte order tespit et"""
        
        motorola_count = 0
        intel_count = 0
        
        for idx, row in df.iterrows():
            if pd.isna(row.get('Byte Offset')) or pd.isna(row.get('Bit Offset')):
                continue
                
            byte_offset = self.safe_int(row.get('Byte Offset'))
            bit_offset = self.safe_int(row.get('Bit Offset'))
            length = self.safe_int(row.get('Length', 1))
            
            # Motorola (Big-endian) tespiti:
            if bit_offset == 0 and length > 8:
                motorola_count += 1
            
            # Intel (Little-endian) tespiti:
            if bit_offset > 0 and bit_offset < 7:
                intel_count += 1
        
        print(f"Motorola işaretleri: {motorola_count}, Intel işaretleri: {intel_count}")
        
        if intel_count > motorola_count:
            return '1'  # Intel/Little-endian
        else:
            return '0'  # Motorola/Big-endian (default)
    
    def calculate_start_bit(self, byte_offset, bit_offset, byte_order, length):
        """Byte order'a göre gerçek start bit hesapla"""
        byte_offset = self.safe_int(byte_offset, 0)
        bit_offset = self.safe_int(bit_offset, 0)
        length = self.safe_int(length, 1)
        
        if byte_order == '1':  # Intel/Little-endian
            start_bit = (byte_offset * 8) + bit_offset
        else:  # Motorola/Big-endian
            start_bit = (byte_offset * 8) + (7 - bit_offset)
            
            if length > 8:
                start_bit = (byte_offset * 8) + bit_offset
        
        return start_bit
    
    def create_dbc_structure(self, df):
        """DBC yapısı oluştur - Akıllı Byte Order tespiti"""
        nodes = set()
        messages = {}
        
        byte_order = self.detect_byte_order_from_offsets(df)
        print(f"Tespit edilen Byte Order: {'Intel/Little-endian (1)' if byte_order == '1' else 'Motorola/Big-endian (0)'}")
        
        for idx, row in df.iterrows():
            try:
                msg_id = self.safe_int(row['Message ID'])
                msg_name = self.clean_name(row['Message Name'])
                msg_source = self.clean_name(row.get('Message Source', 'Vector__XXX'))
                signal_name = self.clean_name(row['Name'])
                
                if not msg_id or not msg_name or not signal_name:
                    continue
                
                nodes.add(msg_source)
                nodes.add('Vector__XXX')
                
                if msg_id not in messages:
                    messages[msg_id] = {
                        'name': msg_name,
                        'dlc': 8,
                        'transmitter': msg_source,
                        'signals': []
                    }
                
                start_bit = self.calculate_start_bit(
                    row.get('Byte Offset', 0),
                    row.get('Bit Offset', 0), 
                    byte_order,
                    row.get('Length', 1)
                )
                
                length = self.safe_int(row.get('Length', 8))
                factor = self.safe_float(row.get('Scale', 1.0))
                offset = self.safe_float(row.get('Offset', 0.0))
                min_val = self.safe_float(row.get('Min Value', 0.0))
                max_val = self.safe_float(row.get('Max Value', 255.0))
                
                if start_bit < 0:
                    start_bit = 0
                if start_bit >= 64:
                    start_bit = start_bit % 64
                if length <= 0:
                    length = 1
                if length > 64:
                    length = 64
                if start_bit + length > 64:
                    start_bit = 64 - length
                    if start_bit < 0:
                        start_bit = 0
                        length = 64
                
                value_type = '+'
                var_type = str(row.get('Variable Type', '')).upper()
                if any(signed in var_type for signed in ['SIGNED', 'INT', 'SNG']):
                    value_type = '-'
                
                signal = {
                    'name': signal_name,
                    'start_bit': start_bit,
                    'length': length,
                    'byte_order': byte_order,
                    'value_type': value_type,
                    'factor': factor,
                    'offset': offset,
                    'min': min_val,
                    'max': max_val,
                    'unit': str(row.get('Unit', '')).strip() or '',
                    'comment': str(row.get('Description', '')).strip()
                }
                
                messages[msg_id]['signals'].append(signal)
                
            except Exception as e:
                print(f"Satır {idx+2} atlandı: {str(e)}")
                continue
        
        return list(nodes), messages, byte_order
    
    def generate_dbc(self, nodes, messages, byte_order):
        """DBC içeriği oluştur"""
        lines = []
        
        lines.append('VERSION ""')
        lines.append('')
        lines.append('')
        
        lines.append('NS_ :')
        lines.append('    NS_DESC_')
        lines.append('    CM_')
        lines.append('    BA_DEF_')
        lines.append('    BA_')
        lines.append('    VAL_')
        lines.append('    BA_DEF_DEF_')
        lines.append('    EV_DATA_')
        lines.append('    ENVVAR_DATA_')
        lines.append('    SGTYPE_')
        lines.append('    SGTYPE_VAL_')
        lines.append('    BA_DEF_SGTYPE_')
        lines.append('    BA_SGTYPE_')
        lines.append('    SIG_VALTYPE_')
        lines.append('    SIGTYPE_VALTYPE_')
        lines.append('    BO_TX_BU_')
        lines.append('    BA_DEF_REL_')
        lines.append('    BA_REL_')
        lines.append('    BA_DEF_DEF_REL_')
        lines.append('    BU_SG_REL_')
        lines.append('    BU_EV_REL_')
        lines.append('    BU_BO_REL_')
        lines.append('    SG_MUL_VAL_')
        lines.append('')
        
        lines.append('BS_:')
        lines.append('')
        
        lines.append('BU_: ' + ' '.join(sorted(nodes)))
        lines.append('')
        
        for msg_id in sorted(messages.keys()):
            msg = messages[msg_id]
            
            lines.append(f'BO_ {msg_id} {msg["name"]}: {msg["dlc"]} {msg["transmitter"]}')
            
            msg['signals'].sort(key=lambda x: x['start_bit'])
            
            for sig in msg['signals']:
                signal_format = f'{sig["start_bit"]}|{sig["length"]}@{sig["byte_order"]}{sig["value_type"]}'
                
                factor = sig["factor"]
                offset = sig["offset"]
                factor_offset = f'({factor:.1f},{offset:.1f})'
                
                min_val = sig["min"] 
                max_val = sig["max"]
                min_max = f'[{min_val:.1f}|{max_val:.1f}]'
                
                unit = f'"{sig["unit"]}"' if sig["unit"] else '""'
                
                lines.append(f' SG_ {sig["name"]} : {signal_format} {factor_offset} {min_max} {unit} Vector__XXX')
            
            lines.append('')
        
        return '\n'.join(lines)
    
    def convert(self, excel_path, dbc_path):
        """Ana dönüştürme fonksiyonu"""
        try:
            print("Excel okunuyor...")
            df = self.read_excel(excel_path)
            print(f"Excel satır sayısı: {len(df)}")
            
            print("Byte Order tespit ediliyor...")
            nodes, messages, byte_order = self.create_dbc_structure(df)
            print(f"Node'lar: {nodes}")
            print(f"Mesaj sayısı: {len(messages)}")
            print(f"Byte Order: {byte_order}")
            
            if not messages:
                return False, "Hiç mesaj bulunamadı!"
            
            print("DBC içeriği oluşturuluyor...")
            dbc_content = self.generate_dbc(nodes, messages, byte_order)
            
            print("Dosya yazılıyor...")
            with open(dbc_path, 'w', encoding='utf-8') as f:
                f.write(dbc_content)
            
            total_signals = sum(len(msg['signals']) for msg in messages.values())
            byte_order_name = "Intel/Little-endian" if byte_order == '1' else "Motorola/Big-endian"
            
            return True, f"Başarılı! Mesaj: {len(messages)}, Sinyal: {total_signals}, Byte Order: {byte_order_name}"
            
        except Exception as e:
            return False, f"Hata: {str(e)}"

class TurkishDBCConverterGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("EXCEL-DBC Dönüştürücü / Bozankaya Teknoloji")
        self.root.geometry("650x500")
        self.root.configure(bg='white')
        self.root.resizable(False, False)
        
        self.colors = {
            'primary': '#2c3e50',
            'secondary': '#3498db', 
            'accent': '#e74c3c',
            'success': '#27ae60',
            'warning': '#f39c12',
            'light': '#ecf0f1',
            'dark': '#34495e',
            'text': '#2c3e50',
            'background': 'white'
        }
        
        self.converter = SmartDBCConverter()
        self.setup_turkish_ui()
    
    def setup_turkish_ui(self):
        # Ana container - beyaz arkaplan
        main_container = tk.Frame(self.root, bg='white', padx=20, pady=20)
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # ÜST BÖLÜM - Sadece başlık
        header_frame = tk.Frame(main_container, bg='white')
        header_frame.pack(fill=tk.X, pady=(0, 15))
        
        tk.Label(header_frame, 
                text="EXCEL-DBC Dönüştürücü / Bozankaya Teknoloji",
                font=("Arial", 16, "bold"),
                fg=self.colors['primary'],
                bg='white').pack(anchor='w')
        
        tk.Label(header_frame,
                text="Excel CAN veritabanlarını Vector DBC dosyalarına dönüştürün",
                font=("Arial", 9),
                fg=self.colors['text'],
                bg='white').pack(anchor='w', pady=(2, 0))
        
        # ORTA BÖLÜM - 2 kolon
        middle_frame = tk.Frame(main_container, bg='white')
        middle_frame.pack(fill=tk.BOTH, expand=True)
        
        # SOL PANEL - Dosya işlemleri
        left_panel = self.create_left_panel(middle_frame)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # SAĞ PANEL - Özellikler
        right_panel = self.create_right_panel(middle_frame)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))
    
    def create_left_panel(self, parent):
        """Sol panel - Dosya işlemleri"""
        panel = tk.Frame(parent, bg='white')
        
        # Panel başlığı
        title_label = tk.Label(panel, 
                              text="Dosya Dönüşümü",
                              font=("Arial", 11, "bold"),
                              fg=self.colors['primary'],
                              bg='white')
        title_label.pack(anchor='w', pady=(0, 12))
        
        # Excel dosyası seçme
        excel_group = tk.Frame(panel, bg='white')
        excel_group.pack(fill=tk.X, pady=6)
        
        tk.Label(excel_group, 
                text="Excel Kaynak Dosyası:",
                font=("Arial", 9, "bold"),
                fg=self.colors['text'],
                bg='white').pack(anchor='w')
        
        excel_frame = tk.Frame(excel_group, bg='white')
        excel_frame.pack(fill=tk.X, pady=4)
        
        self.excel_path = tk.StringVar()
        excel_entry = tk.Entry(excel_frame, 
                              textvariable=self.excel_path,
                              font=("Arial", 9),
                              width=30,
                              state='readonly',
                              relief=tk.SOLID,
                              bd=1)
        excel_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        excel_btn = tk.Button(excel_frame,
                             text="Gözat",
                             font=("Arial", 9),
                             bg=self.colors['secondary'],
                             fg='white',
                             relief=tk.FLAT,
                             command=self.browse_excel)
        excel_btn.pack(side=tk.RIGHT)
        
        # DBC dosyası kaydetme
        dbc_group = tk.Frame(panel, bg='white')
        dbc_group.pack(fill=tk.X, pady=6)
        
        tk.Label(dbc_group, 
                text="DBC Çıktı Dosyası:",
                font=("Arial", 9, "bold"),
                fg=self.colors['text'],
                bg='white').pack(anchor='w')
        
        dbc_frame = tk.Frame(dbc_group, bg='white')
        dbc_frame.pack(fill=tk.X, pady=4)
        
        self.dbc_path = tk.StringVar()
        dbc_entry = tk.Entry(dbc_frame, 
                            textvariable=self.dbc_path,
                            font=("Arial", 9),
                            width=30,
                            state='readonly',
                            relief=tk.SOLID,
                            bd=1)
        dbc_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        dbc_btn = tk.Button(dbc_frame,
                           text="Farklı Kaydet",
                           font=("Arial", 9),
                           bg=self.colors['secondary'],
                           fg='white',
                           relief=tk.FLAT,
                           command=self.browse_dbc)
        dbc_btn.pack(side=tk.RIGHT)
        
        # Ayırıcı
        separator = tk.Frame(panel, height=1, bg='#e0e0e0')
        separator.pack(fill=tk.X, pady=12)
        
        # Dönüştürme butonu
        convert_btn = tk.Button(panel,
                               text="DBC'YE DÖNÜŞTÜR",
                               font=("Arial", 11, "bold"),
                               bg=self.colors['success'],
                               fg='white',
                               relief=tk.FLAT,
                               padx=25,
                               pady=10,
                               command=self.convert)
        convert_btn.pack(pady=8)
        
        # Durum bilgisi
        self.status_label = tk.Label(panel,
                                   text="Dönüştürmeye hazır...",
                                   font=("Arial", 9),
                                   fg=self.colors['text'],
                                   bg='white',
                                   wraplength=280,
                                   justify=tk.LEFT)
        self.status_label.pack(fill=tk.X, pady=8)
        
        return panel
    
    def create_right_panel(self, parent):
        """Sağ panel - Özellikler ve gereksinimler"""
        panel = tk.Frame(parent, bg='white')
        
        # Özellikler başlığı
        title_label = tk.Label(panel, 
                              text="Dönüştürücü Özellikleri",
                              font=("Arial", 11, "bold"),
                              fg=self.colors['primary'],
                              bg='white')
        title_label.pack(anchor='w', pady=(0, 8))
        
        # Özellikler listesi
        features = [
            "✓ Akıllı Byte Order Tespiti",
            "✓ Otomatik Bit Pozisyonu Doğrulama", 
            "✓ Vector CANdb++ Uyumluluğu",
            "✓ Motorola & Intel Desteği",
            "✓ Excel Format Otomatik Algılama",
            "✓ Hata Yönetimi & Doğrulama",
            "✓ Profesyonel DBC Çıktısı",
            "✓ Çoklu Node Ağ Desteği"
        ]
        
        for feature in features:
            tk.Label(panel,
                    text=feature,
                    font=("Arial", 8),
                    fg=self.colors['success'],
                    bg='white',
                    justify=tk.LEFT).pack(anchor='w', pady=1)
        
        # Ayırıcı
        separator = tk.Frame(panel, height=1, bg='#e0e0e0')
        separator.pack(fill=tk.X, pady=12)
        
        # Gereksinimler başlığı
        req_label = tk.Label(panel,
                           text="Gerekli Excel Sütunları:",
                           font=("Arial", 10, "bold"),
                           fg=self.colors['primary'],
                           bg='white')
        req_label.pack(anchor='w', pady=(0, 6))
        
        requirements = [
            "• Message ID",
            "• Message Name", 
            "• Message Source",
            "• Name (Sinyal)",
            "• Byte Offset",
            "• Bit Offset",
            "• Length"
        ]
        
        for req in requirements:
            tk.Label(panel,
                    text=req,
                    font=("Arial", 8),
                    fg=self.colors['text'],
                    bg='white',
                    justify=tk.LEFT).pack(anchor='w', pady=1)
        
        return panel
    
    def browse_excel(self):
        """Excel dosyası seç"""
        file_path = filedialog.askopenfilename(
            title="Excel Dosyası Seçin",
            filetypes=[("Excel files", "*.xlsx *.xls"), ("All files", "*.*")]
        )
        if file_path:
            self.excel_path.set(file_path)
            base_name = os.path.splitext(file_path)[0]
            self.dbc_path.set(base_name + ".dbc")
            self.status_label.config(text=f"Seçilen: {os.path.basename(file_path)}", fg=self.colors['success'])
    
    def browse_dbc(self):
        """DBC kayıt yeri seç"""
        file_path = filedialog.asksaveasfilename(
            title="DBC Dosyasını Kaydet",
            defaultextension=".dbc",
            filetypes=[("DBC files", "*.dbc"), ("All files", "*.*")]
        )
        if file_path:
            self.dbc_path.set(file_path)
            self.status_label.config(text=f"Çıktı: {os.path.basename(file_path)}", fg=self.colors['success'])
    
    def convert(self):
        """Dönüştürme işlemini başlat"""
        excel_path = self.excel_path.get()
        dbc_path = self.dbc_path.get()
        
        if not excel_path or not dbc_path:
            messagebox.showerror("Hata", "Lütfen hem giriş hem de çıkış dosyalarını seçin")
            return
        
        # Progress window
        progress = tk.Toplevel(self.root)
        progress.title("Dönüştürülüyor...")
        progress.geometry("300x100")
        progress.configure(bg='white')
        progress.transient(self.root)
        progress.grab_set()
        
        tk.Label(progress, 
                text="Excel DBC'ye dönüştürülüyor...",
                font=("Arial", 10),
                fg=self.colors['text'],
                bg='white').pack(pady=10)
        
        progress_bar = ttk.Progressbar(progress, mode='indeterminate', length=250)
        progress_bar.pack(pady=5)
        progress_bar.start()
        
        progress.update()
        
        # Conversion
        success, message = self.converter.convert(excel_path, dbc_path)
        
        progress.destroy()
        
        if success:
            self.status_label.config(text=message, fg=self.colors['success'])
            messagebox.showinfo("Başarılı", f"Dönüşüm başarıyla tamamlandı!\n\n{message}")
        else:
            self.status_label.config(text=message, fg=self.colors['accent'])
            messagebox.showerror("Hata", f"Dönüşüm başarısız!\n\n{message}")

def main():
    root = tk.Tk()
    app = TurkishDBCConverterGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
