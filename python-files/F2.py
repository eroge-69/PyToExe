import os
import tkinter as tk
from tkinter import font as tkfont, messagebox
from PIL import Image, ImageTk, ImageDraw
import sys
import webbrowser

class ModernAutorun:
    def __init__(self, root):
        self.root = root
        self.setup_window()
        self.create_folders()
        self.load_assets()
        self.create_ui()
        self.setup_autorun()

    def setup_window(self):
        self.root.title("Cyrus Engineering Group- @2025 Autorun")
        self.root.geometry("650x750")
        self.root.configure(bg='#001F3F')  # پس‌زمینه آبی نفتی تیره
        self.root.resizable(False, False)
        
        try:
            self.root.iconbitmap('logo.ico')
        except:
            pass

    def create_folders(self):
        self.project_folders = {
            'DWG': 'DWG_FORMAT',
            'PDF': 'PDF_FORMAT',
            'XLSX': 'XLSX_FORMAT',
            'CALPDF': 'CALPDF_FORMAT'
        }
        
        for folder in self.project_folders.values():
            if not os.path.exists(folder):
                os.makedirs(folder)

    def load_assets(self):
        self.logo_img = self.load_image_with_fallback(
            'logo.png', 
            size=(180, 180),
            fallback_color=(0, 96, 100)  # آبی نفتی
        )
        self.save_icon_for_autorun()

    def load_image_with_fallback(self, path, size, fallback_color):
        try:
            img = Image.open(path).convert("RGBA")
            img = img.resize(size, Image.Resampling.LANCZOS)
            return ImageTk.PhotoImage(img)
        except Exception as e:
            print(f"Error loading image: {e}")
            return self.create_fallback_image(size, fallback_color)

    def create_fallback_image(self, size, color):
        img = Image.new('RGBA', size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        draw.ellipse([(10, 10), (size[0]-10, size[1]-10)], fill=color + (200,))
        return ImageTk.PhotoImage(img)

    def save_icon_for_autorun(self):
        try:
            if hasattr(self, 'logo_img'):
                img = Image.new('RGBA', (32, 32), (0, 0, 0, 0))
                img.save('logo.ico', format='ICO')
        except Exception as e:
            print(f"Error saving icon: {e}")

    def create_ui(self):
        main_frame = tk.Frame(self.root, bg='#001F3F')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=25, pady=25)
        
        # عنوان با جلوه نورانی
        title_frame = tk.Frame(main_frame, bg='#001F3F')
        title_frame.pack(pady=(0, 20))
        
        title_font = tkfont.Font(family='Helvetica', size=24, weight='bold')
        tk.Label(
            title_frame,
            text="CYRUS ENGINEERING GROUP",
            font=title_font,
            fg='#00E5FF',  # آبی فسفری
            bg='#001F3F'
        ).pack(side=tk.LEFT)
        
        tk.Label(
            title_frame,
            text="2025",
            font=title_font,
            fg='#E31937',  # قرمز شرکتی
            bg='#001F3F'
        ).pack(side=tk.LEFT, padx=5)

        # نمایش لوگو
        logo_frame = tk.Frame(main_frame, bg='#001F3F')
        logo_frame.pack(pady=(0, 20))
        
        if hasattr(self, 'logo_img'):
            logo_label = tk.Label(logo_frame, image=self.logo_img, bg='#001F3F')
            logo_label.pack()

        # اطلاعات پروژه
        info_frame = tk.Frame(main_frame, bg='#003366')  # آبی نفتی روشن‌تر
        info_frame.pack(fill=tk.X, pady=(0, 25), padx=10)
        
        project_data = {
            "Project Name": "Zarin Sazan Commercial Building",
            "Project Type": "Commercial Building",
            "Employer Name": "Zarin Sazan Anarak",
            "Project Number": "140202-23-B",
            "Project Size": "30,000 sqm"
        }
        
        for i, (field, value) in enumerate(project_data.items()):
            row_frame = tk.Frame(info_frame, bg='#003366')
            row_frame.pack(fill=tk.X, pady=2)
            
            tk.Label(
                row_frame,
                text=f"{field}:",
                font=('Arial', 10),
                fg='#00CED1',  # آبی نفتی روشن
                bg='#003366',
                width=15,
                anchor='w'
            ).pack(side=tk.LEFT)
            
            tk.Label(
                row_frame,
                text=value,
                font=('Arial', 10, 'bold'),
                fg='white',
                bg='#003366',
                anchor='w'
            ).pack(side=tk.LEFT)

        # دکمه‌های اقدام
        button_frame = tk.Frame(main_frame, bg='#001F3F')
        button_frame.pack(fill=tk.X)
        
        buttons = [
            ("DWG FORMAT", self.open_dwg_folder, '#E31937'),  # قرمز
            ("PDF FORMAT", self.open_pdf_folder, '#00607A'),  # آبی نفتی
            ("XLSX FORMAT", self.open_xlsx_folder, '#E31937'),
            ("CAL PDF", self.open_calpdf_folder, '#00607A')
        ]
        
        for text, command, color in buttons:
            btn = tk.Button(
                button_frame,
                text=text,
                command=command,
                font=('Arial', 12, 'bold'),
                bg=color,
                fg='white',
                activebackground='#FFD700',  # طلایی هنگام کلیک
                activeforeground='black',
                bd=0,
                padx=20,
                pady=10,
                width=15,
                relief=tk.GROOVE
            )
            btn.pack(pady=8, fill=tk.X)
            btn.bind("<Enter>", lambda e, b=btn: b.config(bg='#FFD700', fg='black'))
            btn.bind("<Leave>", lambda e, b=btn, c=color: b.config(bg=c, fg='white'))

    def open_dwg_folder(self):
        self.open_folder('DWG')

    def open_pdf_folder(self):
        self.open_folder('PDF')

    def open_xlsx_folder(self):
        self.open_folder('XLSX')

    def open_calpdf_folder(self):
        self.open_folder('CALPDF')

    def open_folder(self, folder_type):
        folder_path = os.path.abspath(self.project_folders[folder_type])
        
        if os.path.exists(folder_path):
            try:
                if sys.platform == 'win32':
                    os.startfile(folder_path)
                elif sys.platform == 'darwin':
                    webbrowser.open(folder_path)
                else:
                    os.system(f'xdg-open "{folder_path}"')
            except Exception as e:
                messagebox.showerror(
                    "Error",
                    f"Cannot open {folder_type} folder:\n{str(e)}"
                )
        else:
            messagebox.showerror(
                "Error",
                f"{folder_type} folder not found:\n{folder_path}"
            )

    def setup_autorun(self):
        autorun_content = """[autorun]
open=autorun.exe
icon=logo.ico
label=Cyrus Engineering Group
action=Open Project Files
"""
        
        try:
            with open('autorun.inf', 'w', encoding='utf-8') as f:
                f.write(autorun_content)
        except Exception as e:
            print(f"Error creating autorun.inf: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = ModernAutorun(root)
    root.mainloop()