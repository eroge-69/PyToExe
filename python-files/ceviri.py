import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import re
import os

class TextEditorPackager:
    def __init__(self, root):
        self.root = root
        self.root.title("Metin Düzenleyici ve Paketleyici")
        self.root.geometry("800x600")
        
        # Tema ayarları
        self.root.configure(bg='#2c3e50')
        
        # Ana frame
        main_frame = tk.Frame(root, bg='#2c3e50')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Başlık
        title_label = tk.Label(main_frame, text="🎄 Metin Düzenleyici ve Paketleyici 🎃", 
                              font=('Arial', 16, 'bold'), bg='#2c3e50', fg='#ecf0f1')
        title_label.pack(pady=10)
        
        # Butonlar frame
        buttons_frame = tk.Frame(main_frame, bg='#2c3e50')
        buttons_frame.pack(fill=tk.X, pady=10)
        
        # İlk satır butonlar
        first_row = tk.Frame(buttons_frame, bg='#2c3e50')
        first_row.pack(fill=tk.X, pady=2)
        
        # Dosya seç butonu
        self.select_file_btn = tk.Button(first_row, text="📁 Metin Dosyası Seç", 
                                        command=self.select_file,
                                        bg='#3498db', fg='white', font=('Arial', 10, 'bold'),
                                        relief=tk.FLAT, padx=20, pady=5)
        self.select_file_btn.pack(side=tk.LEFT, padx=5)
        
        # Çıkart butonu
        self.extract_btn = tk.Button(first_row, text="📤 Metni Çıkart", 
                                    command=self.extract_text,
                                    bg='#27ae60', fg='white', font=('Arial', 10, 'bold'),
                                    relief=tk.FLAT, padx=20, pady=5, state=tk.DISABLED)
        self.extract_btn.pack(side=tk.LEFT, padx=5)
        
        # Paketle butonu
        self.package_btn = tk.Button(first_row, text="📦 Metni Paketle", 
                                    command=self.package_text,
                                    bg='#e74c3c', fg='white', font=('Arial', 10, 'bold'),
                                    relief=tk.FLAT, padx=20, pady=5, state=tk.DISABLED)
        self.package_btn.pack(side=tk.LEFT, padx=5)
        
        # Kaydet butonu
        self.save_btn = tk.Button(first_row, text="💾 Kaydet", 
                                 command=self.save_file,
                                 bg='#f39c12', fg='white', font=('Arial', 10, 'bold'),
                                 relief=tk.FLAT, padx=20, pady=5, state=tk.DISABLED)
        self.save_btn.pack(side=tk.LEFT, padx=5)
        
        # İkinci satır - Özel işaretler
        second_row = tk.Frame(buttons_frame, bg='#2c3e50')
        second_row.pack(fill=tk.X, pady=2)
        
        # Özel işaret ayarları label
        settings_label = tk.Label(second_row, text="🎯 Özel İşaretler:", 
                                 bg='#2c3e50', fg='#ecf0f1', font=('Arial', 10, 'bold'))
        settings_label.pack(side=tk.LEFT, padx=5)
        
        # Başlangıç işareti
        start_label = tk.Label(second_row, text="Başlangıç:", 
                              bg='#2c3e50', fg='#ecf0f1', font=('Arial', 9))
        start_label.pack(side=tk.LEFT, padx=(10, 2))
        
        self.start_marker = tk.Entry(second_row, width=8, font=('Arial', 10),
                                    bg='#ecf0f1', fg='#2c3e50', relief=tk.FLAT)
        self.start_marker.pack(side=tk.LEFT, padx=2)
        self.start_marker.insert(0, "🎄")
        
        # Bitiş işareti
        end_label = tk.Label(second_row, text="Bitiş:", 
                            bg='#2c3e50', fg='#ecf0f1', font=('Arial', 9))
        end_label.pack(side=tk.LEFT, padx=(10, 2))
        
        self.end_marker = tk.Entry(second_row, width=8, font=('Arial', 10),
                                  bg='#ecf0f1', fg='#2c3e50', relief=tk.FLAT)
        self.end_marker.pack(side=tk.LEFT, padx=2)
        self.end_marker.insert(0, "🎃")
        
        # Önayarlı işaretler butonu
        presets_btn = tk.Button(second_row, text="⚙️ Önayarlar", 
                               command=self.show_presets,
                               bg='#9b59b6', fg='white', font=('Arial', 9, 'bold'),
                               relief=tk.FLAT, padx=15, pady=3)
        presets_btn.pack(side=tk.LEFT, padx=(10, 5))
        
        # Test butonu
        test_btn = tk.Button(second_row, text="🔍 Test Et", 
                            command=self.test_markers,
                            bg='#1abc9c', fg='white', font=('Arial', 9, 'bold'),
                            relief=tk.FLAT, padx=15, pady=3)
        test_btn.pack(side=tk.LEFT, padx=5)
        
        # Dosya yolu etiketi
        self.file_path_label = tk.Label(main_frame, text="Dosya seçilmedi", 
                                       bg='#34495e', fg='#ecf0f1', font=('Arial', 9),
                                       relief=tk.SUNKEN, anchor=tk.W, padx=10, pady=5)
        self.file_path_label.pack(fill=tk.X, pady=5)
        
        # Metin editörü
        editor_frame = tk.Frame(main_frame, bg='#2c3e50')
        editor_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Metin alanı etiketi
        text_label = tk.Label(editor_frame, text="📝 Metin Editörü:", 
                             bg='#2c3e50', fg='#ecf0f1', font=('Arial', 12, 'bold'))
        text_label.pack(anchor=tk.W, pady=(0, 5))
        
        # Text editor container
        text_container = tk.Frame(editor_frame, bg='#2c3e50')
        text_container.pack(fill=tk.BOTH, expand=True)
        
        # Satır numaraları frame
        line_frame = tk.Frame(text_container, bg='#34495e', width=50)
        line_frame.pack(side=tk.LEFT, fill=tk.Y)
        line_frame.pack_propagate(False)
        
        # Satır numaraları text widget
        self.line_numbers = tk.Text(line_frame, 
                                   width=4, 
                                   bg='#34495e', fg='#bdc3c7',
                                   font=('Courier New', 11),
                                   relief=tk.FLAT,
                                   state=tk.DISABLED,
                                   wrap=tk.NONE,
                                   cursor="arrow")
        self.line_numbers.pack(fill=tk.BOTH, expand=True, padx=(5, 0))
        
        # Ana metin alanı
        self.text_area = tk.Text(text_container, 
                                wrap=tk.WORD, 
                                bg='#ecf0f1', fg='#2c3e50',
                                font=('Courier New', 11),
                                relief=tk.FLAT,
                                borderwidth=2,
                                undo=True)
        
        # Scrollbar
        scrollbar = tk.Scrollbar(text_container, orient=tk.VERTICAL, command=self.on_scrollbar)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.text_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.text_area.config(yscrollcommand=scrollbar.set)
        
        # Text area event bindings
        self.text_area.bind('<KeyRelease>', self.on_text_change)
        self.text_area.bind('<ButtonRelease-1>', self.on_text_change)
        self.text_area.bind('<MouseWheel>', self.on_mousewheel)
        self.text_area.bind('<<Selection>>', self.on_selection_change)
        self.text_area.bind('<Button-1>', self.on_click)
        self.text_area.bind('<B1-Motion>', self.on_drag)
        self.text_area.bind('<KeyPress>', self.on_key_press)
        self.text_area.bind('<Control-a>', self.on_select_all)
        
        # Durum çubuğu frame
        status_frame = tk.Frame(main_frame, bg='#2c3e50')
        status_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        # Ana durum çubuğu
        self.status_bar = tk.Label(status_frame, text="Hazır", 
                                  bg='#34495e', fg='#ecf0f1', 
                                  relief=tk.SUNKEN, anchor=tk.W, padx=10, pady=2)
        self.status_bar.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Seçim bilgisi
        self.selection_info = tk.Label(status_frame, text="", 
                                      bg='#34495e', fg='#ecf0f1', 
                                      relief=tk.SUNKEN, anchor=tk.E, padx=10, pady=2,
                                      width=25)
        self.selection_info.pack(side=tk.RIGHT)
        
        # Satır/sütun bilgisi
        self.cursor_info = tk.Label(status_frame, text="Satır: 1, Sütun: 1", 
                                   bg='#34495e', fg='#ecf0f1', 
                                   relief=tk.SUNKEN, anchor=tk.E, padx=10, pady=2,
                                   width=20)
        self.cursor_info.pack(side=tk.RIGHT)
        
        # Değişkenler
        self.current_file = None
        self.original_content = ""
        self.xml_structure = ""  # XML yapısını saklamak için
        self.current_start_marker = "🎄"
        self.current_end_marker = "🎃"
        
        # İlk satır numaralarını göster
        self.update_line_numbers()
        
    def select_file(self):
        """Metin dosyası seçme fonksiyonu"""
        file_path = filedialog.askopenfilename(
            title="Metin Dosyası Seç",
            filetypes=[("Metin Dosyaları", "*.txt"), ("Tüm Dosyalar", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()
                
                self.current_file = file_path
                self.original_content = content
                self.text_area.delete(1.0, tk.END)
                self.text_area.insert(1.0, content)
                
                # UI güncellemeleri
                self.file_path_label.config(text=f"📁 {os.path.basename(file_path)}")
                self.extract_btn.config(state=tk.NORMAL)
                self.save_btn.config(state=tk.NORMAL)
                self.status_bar.config(text=f"Dosya yüklendi: {os.path.basename(file_path)}")
                
                # Satır numaralarını güncelle
                self.update_line_numbers()
                self.on_text_change(None)
                
            except Exception as e:
                messagebox.showerror("Hata", f"Dosya okuma hatası: {str(e)}")
                
    def extract_text(self):
        """Simgeler arasındaki metni çıkarma fonksiyonu"""
        if not self.current_file:
            messagebox.showwarning("Uyarı", "Önce bir dosya seçin!")
            return
        
        # Özel işaretleri al
        start_marker = self.start_marker.get().strip()
        end_marker = self.end_marker.get().strip()
        
        if not start_marker or not end_marker:
            messagebox.showwarning("Uyarı", "Başlangıç ve bitiş işaretlerini girin!")
            return
            
        content = self.text_area.get(1.0, tk.END).strip()
        
        # Özel işaretler arasındaki metni bulma (regex escape)
        start_escaped = re.escape(start_marker)
        end_escaped = re.escape(end_marker)
        pattern = f'{start_escaped}(.*?){end_escaped}'
        matches = re.findall(pattern, content, re.DOTALL)
        
        if matches:
            # Tüm eşleşmeleri birleştir (sadece işaretler arasındaki metinler)
            extracted_texts = []
            for match in matches:
                clean_text = match.strip()
                extracted_texts.append(clean_text)
            
            extracted_content = '\n'.join(extracted_texts)
            
            # Orijinal yapıyı sakla (XML etiketleri ve yapısı)
            self.xml_structure = content
            self.current_start_marker = start_marker
            self.current_end_marker = end_marker
            
            # Metin alanını temizle ve sadece çıkarılan metinleri göster
            self.text_area.delete(1.0, tk.END)
            self.text_area.insert(1.0, extracted_content)
            
            # Satır numaralarını güncelle
            self.update_line_numbers()
            self.on_text_change(None)
            
            self.package_btn.config(state=tk.NORMAL)
            self.status_bar.config(text=f"✅ {len(matches)} adet metin çıkarıldı ({start_marker}...{end_marker})")
            
            messagebox.showinfo("Başarılı", f"{len(matches)} adet metin çıkarıldı!\n"
                                          f"İşaretler: {start_marker}...{end_marker}\n"
                                          f"Sadece işaretler arasındaki metinler gösteriliyor.")
        else:
            messagebox.showinfo("Bilgi", f"{start_marker} ve {end_marker} işaretleri arasında metin bulunamadı!")
            self.status_bar.config(text=f"❌ Çıkarılacak metin bulunamadı ({start_marker}...{end_marker})")
    
    def package_text(self):
        """Metni simgeler arasına paketleme fonksiyonu"""
        edited_text = self.text_area.get(1.0, tk.END).strip()

        if not edited_text:
            messagebox.showwarning("Uyarı", "Paketlenecek metin yok!")
            return

        if not hasattr(self, 'xml_structure') or not self.xml_structure:
            messagebox.showwarning("Uyarı", "Önce metni çıkarın!")
            return

        if not hasattr(self, 'current_start_marker') or not hasattr(self, 'current_end_marker'):
            messagebox.showwarning("Uyarı", "İşaretler tanımlanmamış!")
            return

        # DÜZELTME: BURADA BOŞ SATIRLAR DAHİL OLSUN, SADECE strip() YAP!
        edited_lines = [line.strip() for line in edited_text.split('\n')]

        # Orijinal XML yapısındaki işaretler arasındaki metinleri değiştir
        content = self.xml_structure
        start_escaped = re.escape(self.current_start_marker)
        end_escaped = re.escape(self.current_end_marker)
        pattern = f'{start_escaped}(.*?){end_escaped}'

        # Eski metinleri bul
        old_matches = [m.strip() for m in re.findall(pattern, content, re.DOTALL)]

        if len(edited_lines) != len(old_matches):
            # Farklı olan ilk satırı bul
            min_len = min(len(edited_lines), len(old_matches))
            first_diff = None
            for i in range(min_len):
                if edited_lines[i] != old_matches[i]:
                    first_diff = i
                    break
            if first_diff is not None:
                msg = (
                    f"Çıkarılan metin sayısı ({len(old_matches)}) ile düzenlenen metin sayısı ({len(edited_lines)}) eşleşmiyor!\n"
                    f"İlk farklı satır/blok: {first_diff+1}\n\n"
                    f"Orijinal:   {old_matches[first_diff]}\n"
                    f"Düzenlenen: {edited_lines[first_diff]}\n\n"
                    f"Devam etmek istiyor musunuz?"
                )
            else:
                msg = (
                    f"Çıkarılan metin sayısı ({len(old_matches)}) ile düzenlenen metin sayısı ({len(edited_lines)}) eşleşmiyor!\n"
                    f"İlk eksik/fazla blok: {min_len+1}\n\n"
                    f"Devam etmek istiyor musunuz?"
                )
            response = messagebox.askyesno("Uyarı", msg)
            if not response:
                return

        # Her eşleşmeyi sırayla yeni metinlerle değiştir
        lines_iter = iter(edited_lines)
        def replace_match(match):
            try:
                new_text = next(lines_iter)
                return f"{self.current_start_marker}{new_text}{self.current_end_marker}"
            except StopIteration:
                return match.group(0)  # Fazla blok olursa eski haliyle bırak

        # Değiştirme işlemi
        new_content = re.sub(pattern, replace_match, content, flags=re.DOTALL)

        # Paketlenmiş içeriği göster
        self.text_area.delete(1.0, tk.END)
        self.text_area.insert(1.0, new_content)

        # Satır numaralarını güncelle
        self.update_line_numbers()
        self.on_text_change(None)

        self.status_bar.config(text=f"✅ Metinler yapı korunarak paketlendi ({self.current_start_marker}...{self.current_end_marker})")
        messagebox.showinfo("Başarılı", f"Metinler yapı korunarak başarıyla paketlendi!\n"
                                       f"İşaretler: {self.current_start_marker}...{self.current_end_marker}")
    
    def save_file(self):
        """Dosyayı kaydetme fonksiyonu"""
        if not self.current_file:
            messagebox.showwarning("Uyarı", "Önce bir dosya seçin!")
            return
        
        content = self.text_area.get(1.0, tk.END).strip()
        
        try:
            with open(self.current_file, 'w', encoding='utf-8') as file:
                file.write(content)
            
            self.status_bar.config(text="✅ Dosya kaydedildi")
            messagebox.showinfo("Başarılı", "Dosya başarıyla kaydedildi!")
            
        except Exception as e:
            messagebox.showerror("Hata", f"Dosya kaydetme hatası: {str(e)}")
    
    def update_line_numbers(self):
        """Satır numaralarını güncelle"""
        self.line_numbers.config(state=tk.NORMAL)
        self.line_numbers.delete(1.0, tk.END)
        
        # Metin alanındaki satır sayısını al
        content = self.text_area.get(1.0, tk.END)
        lines = content.split('\n')
        line_count = len(lines) if lines[-1] else len(lines) - 1
        
        # Satır numaralarını oluştur
        line_numbers_text = '\n'.join(str(i) for i in range(1, line_count + 1))
        self.line_numbers.insert(1.0, line_numbers_text)
        self.line_numbers.config(state=tk.DISABLED)
    
    def on_text_change(self, event):
        """Metin değiştiğinde çağrılan fonksiyon"""
        self.update_line_numbers()
        self.update_cursor_info()
        # Seçim bilgisini de güncelle
        self.root.after(10, self.check_selection)
    
    def on_scrollbar(self, *args):
        """Scrollbar hareket ettiğinde hem text area hem de line numbers'ı kaydır"""
        self.text_area.yview(*args)
        self.line_numbers.yview(*args)
    
    def on_mousewheel(self, event):
        """Mouse wheel ile scrolling"""
        self.text_area.yview_scroll(int(-1 * (event.delta / 120)), "units")
        self.line_numbers.yview_scroll(int(-1 * (event.delta / 120)), "units")
        return "break"
    
    def update_cursor_info(self):
        """Cursor pozisyon bilgisini güncelle"""
        try:
            cursor_pos = self.text_area.index(tk.INSERT)
            line, col = cursor_pos.split('.')
            self.cursor_info.config(text=f"Satır: {line}, Sütun: {int(col)+1}")
        except:
            self.cursor_info.config(text="Satır: 1, Sütun: 1")
    
    def on_selection_change(self, event):
        """Metin seçimi değiştiğinde çağrılan fonksiyon"""
        self.root.after(10, self.check_selection)
    
    def on_click(self, event):
        """Mouse tıklaması"""
        self.root.after(10, self.check_selection)
    
    def on_drag(self, event):
        """Mouse sürükleme"""
        self.root.after(10, self.check_selection)
    
    def on_key_press(self, event):
        """Tuş basımı"""
        self.root.after(10, self.check_selection)
    
    def on_select_all(self, event):
        """Ctrl+A"""
        self.root.after(10, self.check_selection)
    
    def check_selection(self):
        """Seçim durumunu kontrol et"""
        try:
            # Seçili metni al
            selected = self.text_area.selection_get()
            char_count = len(selected)
            word_count = len(selected.split()) if selected.strip() else 0
            
            if char_count > 0:
                self.selection_info.config(text=f"🔤 {char_count} harf, 📝 {word_count} kelime")
            else:
                self.selection_info.config(text="")
        except tk.TclError:
            # Seçim yoksa
            self.selection_info.config(text="")
    
    def show_presets(self):
        """Önayarlı işaretleri gösteren pencere"""
        preset_window = tk.Toplevel(self.root)
        preset_window.title("🎯 Önayarlı İşaretler")
        preset_window.geometry("400x300")
        preset_window.configure(bg='#2c3e50')
        preset_window.resizable(False, False)
        
        # Ana frame
        main_frame = tk.Frame(preset_window, bg='#2c3e50')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Başlık
        title_label = tk.Label(main_frame, text="⚙️ Önayarlı İşaret Setleri", 
                              font=('Arial', 14, 'bold'), bg='#2c3e50', fg='#ecf0f1')
        title_label.pack(pady=(0, 20))
        
        # Önayarlar listesi
        presets = [
            ("🎄 Noel", "🎄", "🎃"),
            ("⭐ Yıldız", "⭐", "✨"),
            ("🔥 Ateş", "🔥", "💥"),
            ("💎 Değerli", "💎", "💍"),
            ("🎯 Hedef", "🎯", "🏆"),
            ("📌 İşaret", "📌", "📍"),
            ("🔰 Özel", "🔰", "⚡"),
            ("🎪 Eğlence", "🎪", "🎭"),
            ("[ ] Köşeli", "[", "]"),
            ("{ } Süslü", "{", "}"),
            ("< > Açılı", "<", ">"),
            ("| | Dikey", "|", "|"),
            ("\" \" Tırnak", "\"", "\""),
            ("' ' Apostrof", "'", "'")
        ]
        
        # Scrollable frame
        canvas = tk.Canvas(main_frame, bg='#34495e', highlightthickness=0, height=150)
        scrollbar = tk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='#34495e')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Preset butonları
        for i, (name, start, end) in enumerate(presets):
            btn = tk.Button(scrollable_frame, 
                           text=f"{name} ({start}...{end})", 
                           command=lambda s=start, e=end: self.apply_preset(s, e, preset_window),
                           bg='#3498db', fg='white', font=('Arial', 10),
                           relief=tk.FLAT, padx=15, pady=5,
                           width=25, anchor=tk.W)
            btn.pack(fill=tk.X, padx=5, pady=2)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y", pady=(0, 20))
        
        # Kapatma butonu
        close_btn = tk.Button(main_frame, text="❌ Kapat", 
                             command=preset_window.destroy,
                             bg='#e74c3c', fg='white', font=('Arial', 10, 'bold'),
                             relief=tk.FLAT, padx=20, pady=5)
        close_btn.pack(pady=10)
    
    def apply_preset(self, start_marker, end_marker, window):
        """Önayarı uygula"""
        self.start_marker.delete(0, tk.END)
        self.start_marker.insert(0, start_marker)
        self.end_marker.delete(0, tk.END)
        self.end_marker.insert(0, end_marker)
        
        self.status_bar.config(text=f"✅ Önayar uygulandı: {start_marker}...{end_marker}")
        window.destroy()
        messagebox.showinfo("Başarılı", f"Önayar uygulandı!\nYeni işaretler: {start_marker}...{end_marker}")
    
    def test_markers(self):
        """İşaretleri test et"""
        start_marker = self.start_marker.get().strip()
        end_marker = self.end_marker.get().strip()
        
        if not start_marker or not end_marker:
            messagebox.showwarning("Uyarı", "Başlangıç ve bitiş işaretlerini girin!")
            return
        
        content = self.text_area.get(1.0, tk.END).strip()
        
        if not content:
            messagebox.showinfo("Test Sonucu", f"Test edilecek metin yok!\n"
                                              f"İşaretler: {start_marker}...{end_marker}")
            return
        
        # Test et
        start_escaped = re.escape(start_marker)
        end_escaped = re.escape(end_marker)
        pattern = f'{start_escaped}(.*?){end_escaped}'
        matches = re.findall(pattern, content, re.DOTALL)
        
        if matches:
            preview = []
            for i, match in enumerate(matches[:3]):  # İlk 3 eşleşmeyi göster
                clean_match = match.strip()[:50]  # İlk 50 karakter
                if len(match.strip()) > 50:
                    clean_match += "..."
                preview.append(f"{i+1}. {clean_match}")
            
            preview_text = "\n".join(preview)
            if len(matches) > 3:
                preview_text += f"\n... ve {len(matches)-3} tane daha"
            
            messagebox.showinfo("Test Başarılı! ✅", 
                               f"İşaretler: {start_marker}...{end_marker}\n"
                               f"Bulunan eşleşme sayısı: {len(matches)}\n\n"
                               f"Önizleme:\n{preview_text}")
        else:
            messagebox.showinfo("Test Sonucu", 
                               f"İşaretler: {start_marker}...{end_marker}\n"
                               f"❌ Hiç eşleşme bulunamadı!")
        
        self.status_bar.config(text=f"🔍 Test tamamlandı: {len(matches) if matches else 0} eşleşme")

def main():
    root = tk.Tk()
    app = TextEditorPackager(root)
    root.mainloop()

if __name__ == "__main__":
    main()