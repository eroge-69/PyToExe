import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
import os
from PIL import Image, ImageTk
import threading
import time

class ExcelConverterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Excel Dönüştürücü")
        self.root.geometry("1198x1184")  # Özel boyut
        self.root.configure(bg='white')
        
        # Modern styling
        self.colors = {
            'primary': '#2196F3',
            'secondary': '#FFC107', 
            'success': '#4CAF50',
            'danger': '#F44336',
            'dark': '#212121',
            'light': '#FAFAFA',
            'accent': '#FF6B35'
        }
        
        self.input_file = None
        self.output_file = None
        self.animation_frames = []
        self.current_frame = 0
        self.animation_job = None
        self.is_animating = False
        
        self.setup_ui()
        self.load_images()
        
    def setup_ui(self):
        # Main container with white background
        main_frame = tk.Frame(self.root, bg='white')
        main_frame.pack(expand=True, fill='both', padx=30, pady=30)
        
        # Title
        title_label = tk.Label(
            main_frame,
            font=('Segoe UI', 24, 'bold'),
            bg='white',
            fg=self.colors['dark']
        )
        title_label.pack(pady=(0, 30))
        
        # Image container without border
        self.image_label = tk.Label(main_frame, bg='white')
        self.image_label.pack(pady=20)
        
        # Buttons container
        buttons_frame = tk.Frame(main_frame, bg='white')
        buttons_frame.pack(pady=20)
        
        # ÇOK BÜYÜK Modern browse button
        self.browse_btn = tk.Button(
            buttons_frame,
            text="📁 Excel Dosyası Seç",
            command=self.browse_file,
            font=('Segoe UI', 18, 'bold'),  # Çok daha büyük font
            bg='#4285F4',  # Google Blue
            fg='white',
            relief='flat',
            bd=0,
            padx=50,  # Çok daha büyük padding
            pady=25,  # Çok daha büyük padding
            cursor='hand2',
            width=20,  # Sabit genişlik
            height=2   # Sabit yükseklik
        )
        self.browse_btn.pack(side='left', padx=20, pady=10)
        
        # ÇOK BÜYÜK Output location button
        self.output_btn = tk.Button(
            buttons_frame,
            text="💾 Kayıt Konumu Seç",
            command=self.choose_output_location,
            font=('Segoe UI', 18, 'bold'),  # Çok daha büyük font
            bg='#FF9800',  # Material Orange
            fg='white',
            relief='flat',
            bd=0,
            padx=50,  # Çok daha büyük padding
            pady=25,  # Çok daha büyük padding
            cursor='hand2',
            width=20,  # Sabit genişlik
            height=2,  # Sabit yükseklik
            state='disabled'
        )
        self.output_btn.pack(side='left', padx=20, pady=10)
        
        # Gelişmiş hover efektleri
        def browse_enter(e):
            self.browse_btn.configure(bg='#3367D6')
            
        def browse_leave(e):
            self.browse_btn.configure(bg='#4285F4')
            
        def output_enter(e):
            if self.output_btn['state'] == 'normal':
                self.output_btn.configure(bg='#F57C00')
                
        def output_leave(e):
            if self.output_btn['state'] == 'normal':
                self.output_btn.configure(bg='#FF9800')
                
        self.browse_btn.bind('<Enter>', browse_enter)
        self.browse_btn.bind('<Leave>', browse_leave)
        self.output_btn.bind('<Enter>', output_enter)
        self.output_btn.bind('<Leave>', output_leave)
        
        # File info frame
        info_frame = tk.Frame(main_frame, bg='white')
        info_frame.pack(pady=15)
        
        # Input file label
        self.file_label = tk.Label(
            info_frame,
            text="📄 Giriş: Dosya seçilmedi",
            font=('Segoe UI', 11),
            bg='white',
            fg=self.colors['dark']
        )
        self.file_label.pack(pady=2)
        
        # Output file label
        self.output_label = tk.Label(
            info_frame,
            text="💾 Çıkış: Konum seçilmedi",
            font=('Segoe UI', 11),
            bg='white',
            fg=self.colors['dark']
        )
        self.output_label.pack(pady=2)
        
        # Şerefe button (animation only) - without border
        self.serefe_btn = tk.Label(
            main_frame,
            cursor='hand2',
            bg='white'
        )
        self.serefe_btn.pack(pady=40)
        self.serefe_btn.bind('<Button-1>', lambda e: self.convert_excel())
        self.serefe_btn.bind('<Enter>', self.start_animation)
        self.serefe_btn.bind('<Leave>', self.stop_animation)
        
        # Progress container - Always visible but hidden initially
        self.progress_container = tk.Frame(main_frame, bg='white')
        
        # Progress bar (modern style) - Çok daha büyük ve belirgin
        style = ttk.Style()
        style.configure("BigModern.Horizontal.TProgressbar", 
                       background='#4285F4',
                       troughcolor='#E0E0E0',
                       borderwidth=2,
                       lightcolor='#4285F4',
                       darkcolor='#4285F4',
                       thickness=30)  # Çok daha kalın
        
        self.progress = ttk.Progressbar(
            self.progress_container,
            mode='indeterminate',
            length=700,  # Çok daha uzun
            style="BigModern.Horizontal.TProgressbar"
        )
        
        # Status label - Daha büyük
        self.status_label = tk.Label(
            self.progress_container,
            text="",
            font=('Segoe UI', 16, 'bold'),  # Daha büyük font
            bg='white',
            fg='#4285F4'
        )
        
    def load_images(self):
        try:
            # Before image (maintain aspect ratio) - Bigger for larger GUI
            before_img = Image.open('before.jpeg')
            # Calculate size maintaining aspect ratio
            max_width, max_height = 700, 450
            before_img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
            self.before_photo = ImageTk.PhotoImage(before_img)
            
            # After image (maintain aspect ratio) - Bigger for larger GUI
            after_img = Image.open('after.jpeg')
            after_img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
            self.after_photo = ImageTk.PhotoImage(after_img)
            
            # Animation frames for button - Much bigger
            try:
                gif = Image.open('animation.gif')
                for frame in range(gif.n_frames):
                    gif.seek(frame)
                    # Much larger animation for button
                    frame_img = gif.copy().resize((200, 200), Image.Resampling.LANCZOS)
                    self.animation_frames.append(ImageTk.PhotoImage(frame_img))
                    
                # Static first frame for initial display
                if self.animation_frames:
                    self.serefe_btn.configure(image=self.animation_frames[0])
                    
            except Exception as e:
                print(f"Animation yüklenemedi: {e}")
                # Fallback text button
                self.serefe_btn.configure(
                    text="🍻 Şerefe!",
                    font=('Segoe UI', 16, 'bold'),
                    fg=self.colors['accent'],
                    width=15,
                    height=3
                )
            
            # Set initial image
            self.image_label.configure(image=self.before_photo)
            
        except Exception as e:
            print(f"Resim yükleme hatası: {e}")
            # Fallback placeholder
            self.image_label.configure(
                text="📊 Görsel Yüklenemedi",
                font=('Segoe UI', 16),
                fg=self.colors['dark'],
                width=40,
                height=15
            )
            
    def browse_file(self):
        file_path = filedialog.askopenfilename(
            title="Excel Dosyası Seç",
            filetypes=[("Excel files", "*.xlsx *.xls")]
        )
        
        if file_path:
            self.input_file = file_path
            filename = os.path.basename(file_path)
            self.file_label.configure(text=f"📄 Giriş: {filename}")
            # Enable output button with proper styling
            self.output_btn.configure(
                state='normal',
                bg='#FF9800',
                cursor='hand2'
            )
            self.check_ready_state()
            
    def choose_output_location(self):
        file_path = filedialog.asksaveasfilename(
            title="Çıkış Dosyası Kayıt Konumu",
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx")]
        )
        
        if file_path:
            self.output_file = file_path
            filename = os.path.basename(file_path)
            self.output_label.configure(text=f"💾 Çıkış: {filename}")
            self.check_ready_state()
            
    def check_ready_state(self):
        # Enable animation button when both files are selected
        if self.input_file and self.output_file:
            if hasattr(self, 'animation_frames') and self.animation_frames:
                self.serefe_btn.configure(state='normal')
            else:
                self.serefe_btn.configure(state='normal')
            
    def start_animation(self, event=None):
        if self.animation_frames and not self.is_animating:
            self.is_animating = True
            self.animate()
            
    def stop_animation(self, event=None):
        self.is_animating = False
        if self.animation_job:
            self.root.after_cancel(self.animation_job)
            
    def animate(self):
        if self.is_animating and self.animation_frames:
            frame = self.animation_frames[self.current_frame]
            self.serefe_btn.configure(image=frame)
            self.current_frame = (self.current_frame + 1) % len(self.animation_frames)
            self.animation_job = self.root.after(50, self.animate)  # Çok daha hızlı animasyon!
        elif self.animation_frames:
            # Return to first frame when not animating
            self.serefe_btn.configure(image=self.animation_frames[0])
            
    def convert_excel(self):
        if not self.input_file:
            messagebox.showerror("Hata", "Lütfen bir Excel dosyası seçin!")
            return
            
        if not self.output_file:
            messagebox.showerror("Hata", "Lütfen çıkış dosyası konumu seçin!")
            return
            
        # Start conversion in thread
        thread = threading.Thread(target=self.process_conversion)
        thread.daemon = True
        thread.start()
        
    def process_conversion(self):
        try:
            # Show progress
            self.root.after(0, self.show_progress)
            
            # Read input Excel
            df = pd.read_excel(self.input_file)
            
            # Process data
            output_data = self.process_data(df)
            
            # Create output Excel
            self.create_output_excel(output_data, self.output_file)
            
            # Hide progress and show success
            self.root.after(0, self.hide_progress)
            self.root.after(0, lambda: self.show_success(self.output_file))
            
        except Exception as e:
            self.root.after(0, self.hide_progress)
            self.root.after(0, lambda: messagebox.showerror("Hata", f"Dönüştürme hatası: {str(e)}"))
            
    def show_progress(self):
        # Show progress container
        self.progress_container.pack(pady=30, fill='x')
        
        # Show status label first
        self.status_label.configure(text="🔄 Dönüştürülüyor... Lütfen bekleyin!")
        self.status_label.pack(pady=(0, 15))
        
        # Show and start progress bar
        self.progress.pack(pady=10, fill='x', padx=50)
        self.progress.start(10)  # Daha hızlı animasyon
        
        # Disable buttons during processing with visual feedback
        self.browse_btn.configure(state='disabled', bg='#CCCCCC', cursor='')
        self.output_btn.configure(state='disabled', bg='#CCCCCC', cursor='')
        self.serefe_btn.configure(cursor='')
        
        # Force GUI update
        self.root.update()
        
    def hide_progress(self):
        # Stop and hide progress bar
        self.progress.stop()
        self.progress.pack_forget()
        self.status_label.pack_forget()
        self.progress_container.pack_forget()
        
        # Re-enable buttons with original colors
        self.browse_btn.configure(state='normal', bg='#4285F4', cursor='hand2')
        if self.input_file:
            self.output_btn.configure(state='normal', bg='#FF9800', cursor='hand2')
        self.serefe_btn.configure(cursor='hand2')
        
        # Force GUI update
        self.root.update()
        
    def show_success(self, output_file):
        self.image_label.configure(image=self.after_photo)
        messagebox.showinfo(
            "✅ Başarılı!", 
            f"Dönüştürme tamamlandı!\n\n📁 Çıktı dosyası:\n{output_file}"
        )
        
    def process_data(self, df):
        processed_data = []
        
        for _, row in df.iterrows():
            # Extract data from row
            name_data = self.extract_name(row)
            extension_data = self.extract_extension(row)
            email_data = self.extract_email(row)
            
            if name_data and extension_data:
                # Handle multiple extensions (xxxx-yyyy format)
                extensions = self.parse_extensions(extension_data)
                
                for ext in extensions:
                    # Clean extension (remove spaces, keep only digits)
                    ext_clean = ''.join(filter(str.isdigit, ext))
                    if len(ext_clean) >= 4:
                        processed_row = {
                            'first_name': name_data['first'],
                            'last_name': name_data['last'],
                            'extension': ext_clean,
                            'email': email_data,
                            'password': f"{ext_clean}EG{ext_clean}"
                        }
                        processed_data.append(processed_row)
                    
        return processed_data
        
    def extract_name(self, row):
        # Look for names in columns 1 and 6 (main name columns)
        name_columns = [1, 6]  # Based on Excel structure analysis
        
        for col_idx in name_columns:
            if col_idx < len(row):
                full_name = str(row.iloc[col_idx]).strip()
                if full_name and full_name != 'nan' and len(full_name) > 3:
                    # Skip header rows and department names
                    if any(skip_word in full_name.upper() for skip_word in 
                           ['UNVAN', 'ADI SOYADI', 'YÖNETİM', 'İDARİ', 'PORTFÖY', 'SATINALMA']):
                        continue
                    
                    # Clean and format name
                    full_name = full_name.replace('  ', ' ').strip()
                    parts = full_name.split()
                    if len(parts) >= 2:
                        first_name = parts[0].capitalize()
                        last_name = ' '.join(parts[1:]).capitalize()
                        return {'first': first_name, 'last': last_name}
        return None
        
    def extract_extension(self, row):
        # Look for extensions in columns 0 and 5 (main extension columns)
        ext_columns = [0, 5]
        
        for col_idx in ext_columns:
            if col_idx < len(row):
                value = str(row.iloc[col_idx]).strip()
                if value and value != 'nan':
                    # Check if it's a 4-digit extension or extension range
                    if value.replace('-', '').replace(' ', '').isdigit():
                        digits_only = ''.join(filter(str.isdigit, value))
                        if len(digits_only) >= 4:
                            return value
                    # Handle ranges like "3339-3309" or "3450 - 3453"
                    elif '-' in value and any(char.isdigit() for char in value):
                        digits_only = ''.join(filter(str.isdigit, value))
                        if len(digits_only) >= 4:
                            return value
        return None
        
    def extract_email(self, row):
        # Look for email in columns 4 and 8 (main email columns)
        email_columns = [4, 8]
        
        for col_idx in email_columns:
            if col_idx < len(row):
                email_value = str(row.iloc[col_idx]).strip()
                if email_value and email_value != 'nan' and '@' in email_value:
                    # Clean and format email
                    email_clean = email_value.lower().replace(' ', '')
                    if '.' in email_clean and len(email_clean) > 5:
                        return email_clean
        return ""
        
    def parse_extensions(self, ext_str):
        # Handle xxxx-yyyy format
        if '-' in ext_str:
            parts = ext_str.split('-')
            return [part.strip() for part in parts if part.strip()]
        else:
            return [ext_str.strip()]
            
    def create_output_excel(self, data, output_file):
        # Create DataFrame with template structure
        output_df = pd.DataFrame({
            'Extension': [item['extension'] for item in data],
            'First Name': [item['first_name'] for item in data],
            'Last Name': [item['last_name'] for item in data],
            'Technology': ['SIP/IAX2'] * len(data),
            'Enable Voicemail': ['yes'] * len(data),
            'CallerID Number': [item['extension'] for item in data],
            'SIP/IAX Password': [item['password'] for item in data],
            'Voicemail Password': [item['password'] for item in data],
            'Permission': ['National'] * len(data),
            'AuthID': [''] * len(data),
            'User Password': [''] * len(data),
            'Email Address': [item['email'] for item in data],
            'Enable Contact': [''] * len(data)
        })
        
        # Save to Excel
        output_df.to_excel(output_file, index=False)

def main():
    """Ana uygulama başlatıcı"""
    print("🚀 Excel Dönüştürücü başlatılıyor...")
    
    # Gerekli dosyaları kontrol et
    import os
    required_files = ['before.jpeg', 'after.jpeg', 'animation.gif']
    missing_files = [f for f in required_files if not os.path.exists(f)]
    
    if missing_files:
        print(f"⚠️  Eksik dosyalar: {', '.join(missing_files)}")
        print("Lütfen bu dosyaları aynı klasöre koyun.")
        input("Devam etmek için Enter'a basın...")
    
    try:
        root = tk.Tk()
        app = ExcelConverterApp(root)
        print("✅ Uygulama başlatıldı!")
        root.mainloop()
        
    except ImportError as e:
        print(f"❌ Import hatası: {e}")
        print("Gerekli kütüphaneleri yükleyin: pip3 install pandas openpyxl Pillow")
    except Exception as e:
        print(f"❌ Uygulama hatası: {e}")

if __name__ == "__main__":
    main()