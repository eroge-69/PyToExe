
# -*- coding: utf-8 -*-
import sqlite3
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, font
import sys
import os

class DentalClinicApp:
    def __init__(self, root):
        self.root = root
        self.setup_encoding()
        self.root.title("Ստոմատոլոգիական կլինիկա - Dental Clinic")
        self.root.geometry("{0}x{1}+0+0".format(root.winfo_screenwidth(), root.winfo_screenheight()))
        self.root.attributes('-fullscreen', True)
        self.root.configure(bg='#f5f7fa')
        
        # Цветовая схема
        self.colors = {
            'primary': '#4a8dbc',
            'secondary': '#6c757d',
            'success': '#28a745',
            'danger': '#dc3545',
            'warning': '#ffc107',
            'info': '#17a2b8',
            'light': '#f8f9fa',
            'dark': '#343a40',
            'background': '#f5f7fa',
            'card': '#ffffff',
            'text': '#212529'
        }
        
        # Ensure database directory exists
        if not os.path.exists('data'):
            os.makedirs('data')
        
        # Հիվանդությունների ցանկ
        self.diseases_list = [
            "Արյան գերճնշում",
            "Արյան թերճնշում",
            "Սրտի վիրահատություն",
            "Ցավ կրծքավանդակի շրջանում",
            "Վահանաձև գեղձի հիվանդություն",
            "Վարակիչ հիվանդություններ",
            "Մաշկային հիվանդություններ",
            "Նյարդային և հոգեկան խանգարումներ",
            "Ստամոքս-աղիքային համակարգի հիվանդություններ",
            "Արյան հիվանդություններ",
            "Ալերգիաներ"
        ]
        
        # Տվյալների բազայի կապ
        self.db_path = 'data/dental_clinic.db'
        self.conn = sqlite3.connect(self.db_path)
        self.conn.execute('PRAGMA encoding="UTF-8"')
        self.create_tables()
        
        # Գրաֆիկական ինտերֆեյս
        self.setup_ui()
        self.current_patient_id = None
        self.patient_card_frame = None

    def setup_encoding(self):
        if sys.platform == 'win32':
            import ctypes
            try:
                ctypes.windll.kernel32.SetConsoleOutputCP(65001)
                ctypes.windll.kernel32.SetConsoleCP(65001)
            except:
                pass
        
        self.default_font = font.nametofont("TkDefaultFont")
        self.default_font.configure(family="Arial", size=10)
        
        self.text_font = font.nametofont("TkTextFont")
        self.text_font.configure(family="Arial", size=10)
        
        self.fixed_font = font.nametofont("TkFixedFont")
        self.fixed_font.configure(family="Arial", size=10)

        # Configure Armenian phonetic keyboard layout
        self.root.bind('<Key>', self.handle_key_press)

    def handle_key_press(self, event):
        # Armenian phonetic keyboard mapping
        mapping = {
            'a': 'ա', 'b': 'բ', 'g': 'գ', 'd': 'դ', 'e': 'ե', 'z': 'զ',
            'e`': 'է', 'y': 'ը', 't`': 'թ', 'zh': 'ժ', 'i': 'ի', 'l': 'լ',
            'x': 'խ', 'c': 'ծ', 'k': 'կ', 'h': 'հ', 'j': 'ջ', 'm': 'մ',
            'sh': 'շ', 'n': 'ն', 'o': 'ո', 'ch': 'չ', 'p': 'պ', 's': 'ս',
            'v': 'վ', 't': 'տ', 'r': 'ր', 'ts`': 'ց', 'u': 'ու', 'p`': 'փ',
            'k`': 'ք', 'ev': 'և', 'o`': 'օ', 'f': 'ֆ'
        }
        
        # Check if we need to convert the character
        if event.char.lower() in mapping:
            # Insert the Armenian character instead
            self.root.focus_get().insert(tk.INSERT, mapping[event.char.lower()])
            return "break"

    def create_tables(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS patients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                full_name TEXT NOT NULL,
                birth_date TEXT,
                phone TEXT,
                notes TEXT,
                registration_date TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS patient_diseases (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id INTEGER,
                disease_name TEXT,
                FOREIGN KEY (patient_id) REFERENCES patients (id)
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS procedures (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id INTEGER,
                procedure_date TEXT,
                procedure_type TEXT,
                tooth_number TEXT,
                price REAL,
                is_paid INTEGER DEFAULT 0,
                comments TEXT,
                FOREIGN KEY (patient_id) REFERENCES patients (id)
            )
        ''')
        self.conn.commit()

    def setup_ui(self):
        # Main container
        self.main_frame = tk.Frame(self.root, bg=self.colors['background'])
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Վերնագիր
        header_frame = tk.Frame(self.main_frame, bg=self.colors['primary'], height=90)
        header_frame.pack(fill=tk.X)
        
        # Add author signature (small and subtle)
        author_label = tk.Label(header_frame, 
                              text="Dr. Grigoryan", 
                              font=('Arial', 8, 'italic'), 
                              bg=self.colors['primary'], 
                              fg='white')
        author_label.pack(side=tk.RIGHT, padx=10, pady=5)
        
        logo_label = tk.Label(header_frame, 
                            text="🦷 Ստոմատոլոգիական կլինիկա", 
                            font=('Arial', 18, 'bold'), 
                            bg=self.colors['primary'], 
                            fg='white',
                            pady=15)
        logo_label.pack(side=tk.LEFT, padx=20)
        
        # Exit fullscreen button
        exit_fullscreen_btn = tk.Button(header_frame, 
                                      text="⎚ Exit Fullscreen", 
                                      command=self.toggle_fullscreen,
                                      bg=self.colors['danger'],
                                      fg='white',
                                      font=('Arial', 10, 'bold'),
                                      relief=tk.FLAT,
                                      bd=0,
                                      padx=10,
                                      pady=5)
        exit_fullscreen_btn.pack(side=tk.RIGHT, padx=20)
        
        # Գործիքագոտի
        toolbar = tk.Frame(self.main_frame, bg=self.colors['light'], height=50)
        toolbar.pack(fill=tk.X, padx=10, pady=5)

        buttons = [
            ("➕ Ավելացնել հիվանդ", self.add_patient, self.colors['success']),
            ("🔄 Թարմացնել", self.update_patients_table, self.colors['info']),
            ("🔍 Փնտրել", self.search_patient, self.colors['warning']),
            ("📊 Վիճակագրություն", self.show_stats, self.colors['secondary']),
            ("← Հետ", self.show_patients_list, self.colors['dark']),
            ("❌ Ջնջել հիվանդ", self.delete_patient, self.colors['danger'])
        ]

        for text, cmd, color in buttons:
            btn = tk.Button(toolbar, 
                          text=text, 
                          command=cmd,
                          bg=color,
                          fg='white',
                          font=('Arial', 10, 'bold'),
                          relief=tk.FLAT,
                          padx=12,
                          pady=5,
                          bd=0,
                          activebackground=color,
                          activeforeground='white')
            btn.pack(side=tk.LEFT, padx=5)

        # Patients list frame
        self.patients_list_frame = tk.Frame(self.main_frame, bg=self.colors['background'])
        self.patients_list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        # Style for Treeview
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview",
                      background=self.colors['card'],
                      foreground=self.colors['text'],
                      rowheight=25,
                      fieldbackground=self.colors['card'],
                      borderwidth=0)
        style.map('Treeview', background=[('selected', self.colors['primary'])])
        style.configure("Treeview.Heading",
                      background=self.colors['primary'],
                      foreground='white',
                      relief='flat',
                      font=('Arial', 10, 'bold'))
        style.map("Treeview.Heading",
                 background=[('active', self.colors['primary'])])

        # Հիվանդների աղյուսակ
        self.patients_tree = ttk.Treeview(self.patients_list_frame, 
                                       columns=("ID", "Անուն", "Հեռախոս", "Ծննդյան ամսաթիվ"), 
                                       show="headings",
                                       selectmode='browse')
        
        columns = [
            ("ID", 50),
            ("Անուն", 300),
            ("Հեռախոս", 150),
            ("Ծննդյան ամսաթիվ", 150)
        ]

        for col, width in columns:
            self.patients_tree.heading(col, text=col)
            self.patients_tree.column(col, width=width, anchor='center')

        scrollbar = ttk.Scrollbar(self.patients_list_frame, orient="vertical", command=self.patients_tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.patients_tree.configure(yscrollcommand=scrollbar.set)

        self.patients_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.patients_tree.bind("<Double-1>", self.open_patient_card)

        # Կարգավիճակի տող
        self.status_bar = tk.Label(self.main_frame, 
                                 text="Պատրաստ է", 
                                 bd=1, 
                                 relief=tk.SUNKEN, 
                                 anchor=tk.W,
                                 bg=self.colors['light'],
                                 fg=self.colors['dark'],
                                 font=('Arial', 9))
        self.status_bar.pack(fill=tk.X, padx=10, pady=(0, 10))

        self.update_patients_table()

    def toggle_fullscreen(self):
        self.root.attributes('-fullscreen', not self.root.attributes('-fullscreen'))

    def show_patients_list(self):
        if self.patient_card_frame:
            self.patient_card_frame.pack_forget()
        self.patients_list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        self.update_patients_table()

    def delete_patient(self):
        """Удаление выбранного пациента"""
        selected_item = self.patients_tree.selection()
        if not selected_item:
            messagebox.showwarning("Զգուշացում", "Ընտրեք հիվանդին")
            return
            
        patient_id = self.patients_tree.item(selected_item[0], "values")[0]
        patient_name = self.patients_tree.item(selected_item[0], "values")[1]
        
        confirm = messagebox.askyesno("Հաստատում", 
                                    f"Դուք վստահ եք, որ ցանկանում եք ջնջել {patient_name} հիվանդին?\nԲոլոր տվյալները կկորչեն!")
        if not confirm:
            return
            
        try:
            cursor = self.conn.cursor()
            # Удаляем связанные процедуры
            cursor.execute("DELETE FROM procedures WHERE patient_id=?", (patient_id,))
            # Удаляем связанные заболевания
            cursor.execute("DELETE FROM patient_diseases WHERE patient_id=?", (patient_id,))
            # Удаляем самого пациента
            cursor.execute("DELETE FROM patients WHERE id=?", (patient_id,))
            self.conn.commit()
            
            messagebox.showinfo("Հաջողություն", "Հիվանդը հաջողությամբ ջնջված է")
            self.status_bar.config(text=f"Հիվանդ {patient_name} ջնջված է")
            self.update_patients_table()
        except Exception as e:
            messagebox.showerror("Սխալ", f"Ջնջելիս սխալ է տեղի ունեցել:\n{str(e)}")
            self.status_bar.config(text=f"Սխալ: {str(e)}")

    def add_patient(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Նոր հիվանդի գրանցում")
        dialog.geometry("700x700")
        dialog.resizable(False, False)
        dialog.configure(bg=self.colors['background'])

        # Վերնագիր
        header = tk.Label(dialog, 
                        text="Հիվանդի տվյալներ", 
                        font=('Arial', 14, 'bold'), 
                        bg=self.colors['primary'], 
                        fg='white',
                        padx=10,
                        pady=10)
        header.pack(fill=tk.X)

        form_frame = tk.Frame(dialog, bg=self.colors['background'], padx=20, pady=20)
        form_frame.pack(fill=tk.BOTH, expand=True)

        # Style for entry fields
        entry_style = {
            'font': ('Arial', 10),
            'relief': tk.GROOVE,
            'bd': 1,
            'bg': self.colors['card'],
            'highlightbackground': self.colors['secondary'],
            'highlightthickness': 1
        }

        # Հիմնական տվյալներ
        tk.Label(form_frame, 
               text="1. Անուն ազգանուն*:", 
               bg=self.colors['background'],
               font=('Arial', 10, 'bold')).grid(row=0, column=0, padx=10, pady=5, sticky="e")
        name_entry = tk.Entry(form_frame, 
                            width=40,
                            **entry_style)
        name_entry.grid(row=0, column=1, padx=10, pady=5, sticky="w")

        tk.Label(form_frame, 
               text="2. Ծննդյան ամսաթիվ (ՏՏՏՏ-ԱԱ-ՕՕ):", 
               bg=self.colors['background'],
               font=('Arial', 10, 'bold')).grid(row=1, column=0, padx=10, pady=5, sticky="e")
        birth_entry = tk.Entry(form_frame, 
                             width=40,
                             **entry_style)
        birth_entry.grid(row=1, column=1, padx=10, pady=5, sticky="w")

        tk.Label(form_frame, 
               text="3. Հեռախոսահամար:", 
               bg=self.colors['background'],
               font=('Arial', 10, 'bold')).grid(row=2, column=0, padx=10, pady=5, sticky="e")
        phone_entry = tk.Entry(form_frame, 
                             width=40,
                             **entry_style)
        phone_entry.grid(row=2, column=1, padx=10, pady=5, sticky="w")

        tk.Label(form_frame, 
               text="4. Այլ նշումներ:", 
               bg=self.colors['background'],
               font=('Arial', 10, 'bold')).grid(row=3, column=0, padx=10, pady=5, sticky="e")
        notes_entry = tk.Entry(form_frame, 
                             width=40,
                             **entry_style)
        notes_entry.grid(row=3, column=1, padx=10, pady=5, sticky="w")

        # Հիվանդությունների շրջանակ
        diseases_frame = tk.LabelFrame(form_frame, 
                                     text="5. Ընդհանուր հիվանդություններ", 
                                     font=('Arial', 10, 'bold'),
                                     bg=self.colors['background'],
                                     padx=10, 
                                     pady=10)
        diseases_frame.grid(row=4, columnspan=2, sticky="we", padx=10, pady=10)

        disease_vars = []
        for i, disease in enumerate(self.diseases_list):
            var = tk.IntVar()
            disease_vars.append(var)
            cb = tk.Checkbutton(diseases_frame, 
                              text=f"• {disease}", 
                              variable=var,
                              bg=self.colors['background'],
                              font=('Arial', 10),
                              anchor='w',
                              activebackground=self.colors['background'],
                              activeforeground=self.colors['text'])
            cb.pack(fill=tk.X, padx=5, pady=2)

        # Կոճակներ
        btn_frame = tk.Frame(form_frame, bg=self.colors['background'])
        btn_frame.grid(row=5, columnspan=2, pady=20)

        def save_patient():
            if not name_entry.get():
                messagebox.showwarning("Զգուշացում", "Մուտքագրեք հիվանդի անուն ազգանունը")
                return

            try:
                cursor = self.conn.cursor()
                cursor.execute(
                    "INSERT INTO patients (full_name, birth_date, phone, notes) VALUES (?, ?, ?, ?)",
                    (name_entry.get(), 
                     birth_entry.get(), 
                     phone_entry.get(), 
                     notes_entry.get())
                )
                patient_id = cursor.lastrowid
                
                # Պահպանել հիվանդությունները
                for i, var in enumerate(disease_vars):
                    if var.get() == 1:
                        cursor.execute(
                            "INSERT INTO patient_diseases (patient_id, disease_name) VALUES (?, ?)",
                            (patient_id, self.diseases_list[i])
                        )
                
                self.conn.commit()
                self.update_patients_table()
                dialog.destroy()
                messagebox.showinfo("Հաջողություն", "Հիվանդը հաջողությամբ գրանցված է")
                self.status_bar.config(text="Հիվանդը հաջողությամբ գրանցված է")
            except Exception as e:
                messagebox.showerror("Սխալ", f"Տվյալների պահպանման սխալ:\n{str(e)}")
                self.status_bar.config(text=f"Սխալ: {str(e)}")

        tk.Button(btn_frame, 
                 text="Պահպանել", 
                 command=save_patient,
                 bg=self.colors['success'],
                 fg='white',
                 font=('Arial', 10, 'bold'),
                 padx=15,
                 pady=5,
                 relief=tk.FLAT,
                 bd=0).pack(side=tk.LEFT, padx=10)

        tk.Button(btn_frame, 
                 text="Չեղարկել", 
                 command=dialog.destroy,
                 bg=self.colors['danger'],
                 fg='white',
                 font=('Arial', 10, 'bold'),
                 padx=15,
                 pady=5,
                 relief=tk.FLAT,
                 bd=0).pack(side=tk.LEFT, padx=10)

    def update_patients_table(self):
        for item in self.patients_tree.get_children():
            self.patients_tree.delete(item)
            
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, full_name, phone, birth_date FROM patients ORDER BY full_name")
        
        for row in cursor.fetchall():
            self.patients_tree.insert("", "end", values=row)

    def open_patient_card(self, event=None):
        if event:
            selected_item = self.patients_tree.selection()
            if not selected_item:
                return
            self.current_patient_id = self.patients_tree.item(selected_item[0], "values")[0]
        else:
            if not self.current_patient_id:
                return
        
        # Hide patients list
        self.patients_list_frame.pack_forget()
        
        # Create patient card frame if not exists
        if not self.patient_card_frame:
            self.patient_card_frame = tk.Frame(self.main_frame, bg=self.colors['background'])
        
        # Clear previous content
        for widget in self.patient_card_frame.winfo_children():
            widget.destroy()
        
        self.patient_card_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Վերնագիր
        header_frame = tk.Frame(self.patient_card_frame, bg=self.colors['primary'], height=60)
        header_frame.pack(fill=tk.X)
        
        tk.Button(header_frame, 
                text="✏️ Խմբագրել տվյալները", 
                command=lambda: self.edit_patient(self.current_patient_id),
                bg=self.colors['info'],
                fg='white',
                font=('Arial', 10, 'bold'),
                relief=tk.FLAT,
                bd=0,
                padx=10,
                pady=5).pack(side=tk.LEFT, padx=10, pady=10)

        tk.Button(header_frame, 
                text="➕ Ավելացնել աշխատանք", 
                command=lambda: self.add_procedure(self.current_patient_id),
                bg=self.colors['success'],
                fg='white',
                font=('Arial', 10, 'bold'),
                relief=tk.FLAT,
                bd=0,
                padx=10,
                pady=5).pack(side=tk.LEFT, padx=10, pady=10)

        # Հիմնական բովանդակություն
        main_frame = tk.Frame(self.patient_card_frame, bg=self.colors['background'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Տեղեկություն հիվանդի մասին
        info_frame = tk.LabelFrame(main_frame, 
                                 text="Հիվանդի տվյալներ", 
                                 font=('Arial', 12, 'bold'),
                                 bg=self.colors['card'],
                                 padx=15, 
                                 pady=15)
        info_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 20))

        # Ստանալ հիվանդի տվյալները
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM patients WHERE id=?", (self.current_patient_id,))
        patient_data = cursor.fetchone()

        # Հիմնական տվյալներ
        labels = [
            ("1. Անուն ազգանուն:", 0),
            ("2. Ծննդյան ամսաթիվ:", 1),
            ("3. Հեռախոսահամար:", 2), 
            ("4. Այլ նշումներ:", 3),
            ("5. Գրանցման ամսաթիվ:", 4)
        ]

        for text, row in labels:
            tk.Label(info_frame, 
                   text=text, 
                   font=('Arial', 10, 'bold'),
                   bg=self.colors['card']).grid(row=row, column=0, sticky="e", padx=5, pady=5)
            tk.Label(info_frame, 
                   text=patient_data[row+1], 
                   font=('Arial', 10),
                   bg=self.colors['card'],
                   wraplength=300,
                   justify=tk.LEFT).grid(row=row, column=1, sticky="w", padx=5, pady=5)

        # Հիվանդությունների շրջանակ
        diseases_frame = tk.LabelFrame(info_frame, 
                                     text="6. Ընդհանուր հիվանդություններ", 
                                     font=('Arial', 10, 'bold'),
                                     bg=self.colors['card'],
                                     padx=10, 
                                     pady=10)
        diseases_frame.grid(row=5, columnspan=2, sticky="we", pady=10)

        # Ստանալ հիվանդի հիվանդությունները
        cursor.execute("SELECT disease_name FROM patient_diseases WHERE patient_id=?", (self.current_patient_id,))
        patient_diseases = [row[0] for row in cursor.fetchall()]

        # Ցուցադրել հիվանդությունները
        if patient_diseases:
            for disease in patient_diseases:
                tk.Label(diseases_frame, 
                       text=f"• {disease}", 
                       font=('Arial', 10),
                       bg=self.colors['card'],
                       anchor='w').pack(fill=tk.X, padx=5, pady=2)
        else:
            tk.Label(diseases_frame, 
                   text="Հիվանդություններ չեն գրանցված", 
                   font=('Arial', 10),
                   bg=self.colors['card'],
                   fg='gray').pack(pady=5)

        # Կատարված աշխատանքներ
        procedures_frame = tk.LabelFrame(main_frame, 
                                       text="Կատարված աշխատանքներ", 
                                       font=('Arial', 12, 'bold'),
                                       bg=self.colors['card'],
                                       padx=15, 
                                       pady=15)
        procedures_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Աշխատանքների աղյուսակ (без столбца ID)
        self.procedures_tree = ttk.Treeview(procedures_frame, 
                                     columns=("Ամսաթիվ", "Ծառայություն", "Ատամ", "Արժեք", "Վճարված", "Մեկնաբանություն"), 
                                     show="headings",
                                     selectmode='browse')
        
        columns = [
            ("Ամսաթիվ", 120),
            ("Ծառայություն", 200),
            ("Ատամ", 100),
            ("Արժեք", 100),
            ("Վճարված", 100),
            ("Մեկնաբանություն", 300)
        ]

        for col, width in columns:
            self.procedures_tree.heading(col, text=col)
            self.procedures_tree.column(col, width=width, anchor='center')

        scrollbar = ttk.Scrollbar(procedures_frame, orient="vertical", command=self.procedures_tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.procedures_tree.configure(yscrollcommand=scrollbar.set)

        self.procedures_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Կոճակներ
        btn_frame = tk.Frame(procedures_frame, bg=self.colors['card'])
        btn_frame.pack(fill=tk.X, pady=10)

        def update_procedures_table():
            for item in self.procedures_tree.get_children():
                self.procedures_tree.delete(item)
                
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT procedure_date, procedure_type, tooth_number, price, 
                       CASE WHEN is_paid = 1 THEN 'Այո' ELSE 'Ոչ' END, comments 
                FROM procedures 
                WHERE patient_id=?
                ORDER BY procedure_date DESC
            """, (self.current_patient_id,))
            
            for row in cursor.fetchall():
                self.procedures_tree.insert("", "end", values=row)

        def toggle_payment_status():
            selected = self.procedures_tree.selection()
            if not selected:
                messagebox.showwarning("Զգուշացում", "Ընտրեք գրանցում")
                return
                
            # Получаем дату процедуры как уникальный идентификатор
            procedure_date = self.procedures_tree.item(selected[0], "values")[0]
            cursor = self.conn.cursor()
            cursor.execute("SELECT id, is_paid FROM procedures WHERE patient_id=? AND procedure_date=?", 
                         (self.current_patient_id, procedure_date))
            procedure_id, current_status = cursor.fetchone()
            
            new_status = 0 if current_status == 1 else 1
            cursor.execute("UPDATE procedures SET is_paid=? WHERE id=?", 
                         (new_status, procedure_id))
            self.conn.commit()
            update_procedures_table()

        def delete_procedure():
            selected = self.procedures_tree.selection()
            if not selected:
                messagebox.showwarning("Զգուշացում", "Ընտրեք գրանցում")
                return
                
            if not messagebox.askyesno("Հաստատում", "Ջնջե՞լ ընտրված գրանցումը"):
                return
                
            # Получаем дату процедуры как уникальный идентификатор
            procedure_date = self.procedures_tree.item(selected[0], "values")[0]
            cursor = self.conn.cursor()
            cursor.execute("SELECT id FROM procedures WHERE patient_id=? AND procedure_date=?", 
                         (self.current_patient_id, procedure_date))
            procedure_id = cursor.fetchone()[0]
            cursor.execute("DELETE FROM procedures WHERE id=?", (procedure_id,))
            self.conn.commit()
            update_procedures_table()

        def edit_procedure():
            selected = self.procedures_tree.selection()
            if not selected:
                messagebox.showwarning("Զգուշացում", "Ընտրեք գրանցում")
                return
                
            # Получаем дату процедуры как уникальный идентификатор
            procedure_date = self.procedures_tree.item(selected[0], "values")[0]
            cursor = self.conn.cursor()
            cursor.execute("SELECT id FROM procedures WHERE patient_id=? AND procedure_date=?", 
                         (self.current_patient_id, procedure_date))
            procedure_id = cursor.fetchone()[0]
            self.edit_procedure_details(procedure_id)

        buttons = [
            ("🔄 Թարմացնել", update_procedures_table, self.colors['info']),
            ("✏️ Փոխել վճարումը", toggle_payment_status, self.colors['warning']),
            ("✏️ Խմբագրել", edit_procedure, self.colors['secondary']),
            ("❌ Ջնջել", delete_procedure, self.colors['danger'])
        ]

        for text, cmd, color in buttons:
            btn = tk.Button(btn_frame, 
                          text=text, 
                          command=cmd,
                          bg=color,
                          fg='white',
                          font=('Arial', 10, 'bold'),
                          padx=10,
                          pady=5,
                          relief=tk.FLAT,
                          bd=0)
            btn.pack(side=tk.LEFT, padx=5)

        update_procedures_table()

    def edit_patient(self, patient_id):
        # Ստանալ հիվանդի տվյալները
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM patients WHERE id=?", (patient_id,))
        patient_data = cursor.fetchone()
        
        cursor.execute("SELECT disease_name FROM patient_diseases WHERE patient_id=?", (patient_id,))
        patient_diseases = [row[0] for row in cursor.fetchall()]

        dialog = tk.Toplevel(self.root)
        dialog.title("Խմբագրել հիվանդի տվյալները")
        dialog.geometry("700x700")
        dialog.resizable(False, False)
        dialog.configure(bg=self.colors['background'])

        # Վերնագիր
        header = tk.Label(dialog, 
                        text="Խմբագրել տվյալները", 
                        font=('Arial', 14, 'bold'), 
                        bg=self.colors['primary'], 
                        fg='white',
                        padx=10,
                        pady=10)
        header.pack(fill=tk.X)

        form_frame = tk.Frame(dialog, bg=self.colors['background'], padx=20, pady=20)
        form_frame.pack(fill=tk.BOTH, expand=True)

        # Style for entry fields
        entry_style = {
            'font': ('Arial', 10),
            'relief': tk.GROOVE,
            'bd': 1,
            'bg': self.colors['card'],
            'highlightbackground': self.colors['secondary'],
            'highlightthickness': 1
        }

        # Հիմնական տվյալներ
        tk.Label(form_frame, 
               text="1. Անուն ազգանուն*:", 
               bg=self.colors['background'],
               font=('Arial', 10, 'bold')).grid(row=0, column=0, padx=10, pady=5, sticky="e")
        name_entry = tk.Entry(form_frame, 
                            width=40,
                            **entry_style)
        name_entry.grid(row=0, column=1, padx=10, pady=5, sticky="w")
        name_entry.insert(0, patient_data[1])

        tk.Label(form_frame, 
               text="2. Ծննդյան ամսաթիվ (ՏՏՏՏ-ԱԱ-ՕՕ):", 
               bg=self.colors['background'],
               font=('Arial', 10, 'bold')).grid(row=1, column=0, padx=10, pady=5, sticky="e")
        birth_entry = tk.Entry(form_frame, 
                             width=40,
                             **entry_style)
        birth_entry.grid(row=1, column=1, padx=10, pady=5, sticky="w")
        birth_entry.insert(0, patient_data[2])

        tk.Label(form_frame, 
               text="3. Հեռախոսահամար:", 
               bg=self.colors['background'],
               font=('Arial', 10, 'bold')).grid(row=2, column=0, padx=10, pady=5, sticky="e")
        phone_entry = tk.Entry(form_frame, 
                             width=40,
                             **entry_style)
        phone_entry.grid(row=2, column=1, padx=10, pady=5, sticky="w")
        phone_entry.insert(0, patient_data[3])

        tk.Label(form_frame, 
               text="4. Այլ նշումներ:", 
               bg=self.colors['background'],
               font=('Arial', 10, 'bold')).grid(row=3, column=0, padx=10, pady=5, sticky="e")
        notes_entry = tk.Entry(form_frame, 
                             width=40,
                             **entry_style)
        notes_entry.grid(row=3, column=1, padx=10, pady=5, sticky="w")
        notes_entry.insert(0, patient_data[4])

        # Հիվանդությունների շրջանակ
        diseases_frame = tk.LabelFrame(form_frame, 
                                     text="5. Ընդհանուր հիվանդություններ", 
                                     font=('Arial', 10, 'bold'),
                                     bg=self.colors['background'],
                                     padx=10, 
                                     pady=10)
        diseases_frame.grid(row=4, columnspan=2, sticky="we", padx=10, pady=10)

        disease_vars = []
        for i, disease in enumerate(self.diseases_list):
            var = tk.IntVar()
            if disease in patient_diseases:
                var.set(1)
            disease_vars.append(var)
            cb = tk.Checkbutton(diseases_frame, 
                              text=f"• {disease}", 
                              variable=var,
                              bg=self.colors['background'],
                              font=('Arial', 10),
                              anchor='w',
                              activebackground=self.colors['background'],
                              activeforeground=self.colors['text'])
            cb.pack(fill=tk.X, padx=5, pady=2)

        # Կոճակներ
        btn_frame = tk.Frame(form_frame, bg=self.colors['background'])
        btn_frame.grid(row=5, columnspan=2, pady=20)

        def save_changes():
            try:
                cursor = self.conn.cursor()
                # Թարմացնել հիմնական տվյալները
                cursor.execute(
                    """UPDATE patients SET 
                    full_name = ?,
                    birth_date = ?,
                    phone = ?,
                    notes = ?
                    WHERE id = ?""",
                    (name_entry.get(), 
                     birth_entry.get(),
                     phone_entry.get(),
                     notes_entry.get(),
                     patient_id)
                )
                
                # Թարմացնել հիվանդությունները
                cursor.execute("DELETE FROM patient_diseases WHERE patient_id=?", (patient_id,))
                
                for i, var in enumerate(disease_vars):
                    if var.get() == 1:
                        cursor.execute(
                            "INSERT INTO patient_diseases (patient_id, disease_name) VALUES (?, ?)",
                            (patient_id, self.diseases_list[i])
                        )
                
                self.conn.commit()
                dialog.destroy()
                messagebox.showinfo("Հաջողություն", "Հիվանդի տվյալները թարմացված են")
                self.status_bar.config(text="Հիվանդի տվյալները թարմացված են")
                
                # Թարմացնել հիվանդի ցուցակը
                self.update_patients_table()
                
                # Թարմացնել հիվանդի քարտը
                self.open_patient_card()
                
            except Exception as e:
                messagebox.showerror("Սխալ", f"Տվյալների թարմացման սխալ:\n{str(e)}")
                self.status_bar.config(text=f"Սխալ: {str(e)}")

        tk.Button(btn_frame, 
                 text="Պահպանել", 
                 command=save_changes,
                 bg=self.colors['success'],
                 fg='white',
                 font=('Arial', 10, 'bold'),
                 padx=15,
                 pady=5,
                 relief=tk.FLAT,
                 bd=0).pack(side=tk.LEFT, padx=10)

        tk.Button(btn_frame, 
                 text="Չեղարկել", 
                 command=dialog.destroy,
                 bg=self.colors['danger'],
                 fg='white',
                 font=('Arial', 10, 'bold'),
                 padx=15,
                 pady=5,
                 relief=tk.FLAT,
                 bd=0).pack(side=tk.LEFT, padx=10)

    def add_procedure(self, patient_id):
        dialog = tk.Toplevel(self.root)
        dialog.title("Ավելացնել նոր աշխատանք")
        dialog.geometry("600x500")
        dialog.resizable(False, False)
        dialog.configure(bg=self.colors['background'])

        # Վերնագիր
        header = tk.Label(dialog, 
                        text="Աշխատանքի տվյալներ", 
                        font=('Arial', 14, 'bold'), 
                        bg=self.colors['primary'], 
                        fg='white',
                        padx=10,
                        pady=10)
        header.pack(fill=tk.X)

        form_frame = tk.Frame(dialog, bg=self.colors['background'], padx=20, pady=20)
        form_frame.pack(fill=tk.BOTH, expand=True)

        # Style for entry fields
        entry_style = {
            'font': ('Arial', 10),
            'relief': tk.GROOVE,
            'bd': 1,
            'bg': self.colors['card'],
            'highlightbackground': self.colors['secondary'],
            'highlightthickness': 1
        }

        # Աշխատանքի տեսակ
        tk.Label(form_frame, 
               text="1. Աշխատանքի տեսակ*:", 
               bg=self.colors['background'],
               font=('Arial', 10, 'bold')).grid(row=0, column=0, padx=10, pady=5, sticky="e")
        procedure_entry = tk.Entry(form_frame, 
                                 width=40,
                                 **entry_style)
        procedure_entry.grid(row=0, column=1, padx=10, pady=5, sticky="w")

        # Ամսաթիվ
        tk.Label(form_frame, 
               text="2. Ամսաթիվ (ՏՏՏՏ-ԱԱ-ՕՕ)*:", 
               bg=self.colors['background'],
               font=('Arial', 10, 'bold')).grid(row=1, column=0, padx=10, pady=5, sticky="e")
        date_entry = tk.Entry(form_frame, 
                            width=40,
                            **entry_style)
        date_entry.grid(row=1, column=1, padx=10, pady=5, sticky="w")
        date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))

        # Ատամի համար
        tk.Label(form_frame, 
               text="3. Ատամի համար:", 
               bg=self.colors['background'],
               font=('Arial', 10, 'bold')).grid(row=2, column=0, padx=10, pady=5, sticky="e")
        tooth_entry = tk.Entry(form_frame, 
                             width=40,
                             **entry_style)
        tooth_entry.grid(row=2, column=1, padx=10, pady=5, sticky="w")

        # Գին
        tk.Label(form_frame, 
               text="4. Գին (դրամ)*:", 
               bg=self.colors['background'],
               font=('Arial', 10, 'bold')).grid(row=3, column=0, padx=10, pady=5, sticky="e")
        price_entry = tk.Entry(form_frame, 
                             width=40,
                             **entry_style)
        price_entry.grid(row=3, column=1, padx=10, pady=5, sticky="w")

        # Վճարման կարգավիճակ
        paid_var = tk.IntVar()
        paid_check = tk.Checkbutton(form_frame, 
                                  text="5. Վճարված է", 
                                  variable=paid_var,
                                  bg=self.colors['background'],
                                  font=('Arial', 10))
        paid_check.grid(row=4, column=1, padx=10, pady=5, sticky="w")

        # Մեկնաբանություն
        tk.Label(form_frame, 
               text="6. Մեկնաբանություն:", 
               bg=self.colors['background'],
               font=('Arial', 10, 'bold')).grid(row=5, column=0, padx=10, pady=5, sticky="ne")
        comments_text = tk.Text(form_frame, 
                              width=40, 
                              height=5, 
                              font=('Arial', 10),
                              relief=tk.GROOVE,
                              bd=2)
        comments_text.grid(row=5, column=1, padx=10, pady=5, sticky="w")

        # Կոճակներ
        btn_frame = tk.Frame(form_frame, bg=self.colors['background'])
        btn_frame.grid(row=6, columnspan=2, pady=20)

        def save_procedure():
            if not procedure_entry.get():
                messagebox.showwarning("Զգուշացում", "Մուտքագրեք աշխատանքի տեսակը")
                return
            if not date_entry.get():
                messagebox.showwarning("Զգուշացում", "Մուտքագրեք ամսաթիվը")
                return
            if not price_entry.get():
                messagebox.showwarning("Զգուշացում", "Մուտքագրեք գինը")
                return

            try:
                price = float(price_entry.get())
                cursor = self.conn.cursor()
                cursor.execute(
                    """INSERT INTO procedures 
                    (patient_id, procedure_date, procedure_type, tooth_number, price, is_paid, comments) 
                    VALUES (?, ?, ?, ?, ?, ?, ?)""",
                    (patient_id, 
                     date_entry.get(),
                     procedure_entry.get(),
                     tooth_entry.get(),
                     price,
                     paid_var.get(),
                     comments_text.get("1.0", tk.END).strip())
                )
                self.conn.commit()
                dialog.destroy()
                messagebox.showinfo("Հաջողություն", "Աշխատանքը հաջողությամբ գրանցված է")
                self.status_bar.config(text="Աշխատանքը հաջողությամբ գրանցված է")
                
                # Թարմացնել աշխատանքների ցուցակը
                self.open_patient_card()
            except ValueError:
                messagebox.showerror("Սխալ", "Գինը պետք է լինի թիվ")
            except Exception as e:
                messagebox.showerror("Սխալ", f"Տվյալների պահպանման սխալ:\n{str(e)}")
                self.status_bar.config(text=f"Սխալ: {str(e)}")

        tk.Button(btn_frame, 
                 text="Պահպանել", 
                 command=save_procedure,
                 bg=self.colors['success'],
                 fg='white',
                 font=('Arial', 10, 'bold'),
                 padx=15,
                 pady=5,
                 relief=tk.FLAT,
                 bd=0).pack(side=tk.LEFT, padx=10)

        tk.Button(btn_frame, 
                 text="Չեղարկել", 
                 command=dialog.destroy,
                 bg=self.colors['danger'],
                 fg='white',
                 font=('Arial', 10, 'bold'),
                 padx=15,
                 pady=5,
                 relief=tk.FLAT,
                 bd=0).pack(side=tk.LEFT, padx=10)

    def edit_procedure_details(self, procedure_id):
        # Ստանալ աշխատանքի տվյալները
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM procedures WHERE id=?", (procedure_id,))
        procedure_data = cursor.fetchone()

        dialog = tk.Toplevel(self.root)
        dialog.title("Խմբագրել աշխատանք")
        dialog.geometry("600x500")
        dialog.resizable(False, False)
        dialog.configure(bg=self.colors['background'])

        # Վերնագիր
        header = tk.Label(dialog, 
                        text="Խմբագրել աշխատանք", 
                        font=('Arial', 14, 'bold'), 
                        bg=self.colors['primary'], 
                        fg='white',
                        padx=10,
                        pady=10)
        header.pack(fill=tk.X)

        form_frame = tk.Frame(dialog, bg=self.colors['background'], padx=20, pady=20)
        form_frame.pack(fill=tk.BOTH, expand=True)

        # Style for entry fields
        entry_style = {
            'font': ('Arial', 10),
            'relief': tk.GROOVE,
            'bd': 1,
            'bg': self.colors['card'],
            'highlightbackground': self.colors['secondary'],
            'highlightthickness': 1
        }

        # Աշխատանքի տեսակ
        tk.Label(form_frame, 
               text="1. Աշխատանքի տեսակ*:", 
               bg=self.colors['background'],
               font=('Arial', 10, 'bold')).grid(row=0, column=0, padx=10, pady=5, sticky="e")
        procedure_entry = tk.Entry(form_frame, 
                                 width=40,
                                 **entry_style)
        procedure_entry.grid(row=0, column=1, padx=10, pady=5, sticky="w")
        procedure_entry.insert(0, procedure_data[3])

        # Ամսաթիվ
        tk.Label(form_frame, 
               text="2. Ամսաթիվ (ՏՏՏՏ-ԱԱ-ՕՕ)*:", 
               bg=self.colors['background'],
               font=('Arial', 10, 'bold')).grid(row=1, column=0, padx=10, pady=5, sticky="e")
        date_entry = tk.Entry(form_frame, 
                            width=40,
                            **entry_style)
        date_entry.grid(row=1, column=1, padx=10, pady=5, sticky="w")
        date_entry.insert(0, procedure_data[2])

        # Ատամի համար
        tk.Label(form_frame, 
               text="3. Ատամի համար:", 
               bg=self.colors['background'],
               font=('Arial', 10, 'bold')).grid(row=2, column=0, padx=10, pady=5, sticky="e")
        tooth_entry = tk.Entry(form_frame, 
                             width=40,
                             **entry_style)
        tooth_entry.grid(row=2, column=1, padx=10, pady=5, sticky="w")
        tooth_entry.insert(0, procedure_data[4])

        # Գին
        tk.Label(form_frame, 
               text="4. Գին (դրամ)*:", 
               bg=self.colors['background'],
               font=('Arial', 10, 'bold')).grid(row=3, column=0, padx=10, pady=5, sticky="e")
        price_entry = tk.Entry(form_frame, 
                             width=40,
                             **entry_style)
        price_entry.grid(row=3, column=1, padx=10, pady=5, sticky="w")
        price_entry.insert(0, procedure_data[5])

        # Վճարման կարգավիճակ
        paid_var = tk.IntVar(value=procedure_data[6])
        paid_check = tk.Checkbutton(form_frame, 
                                  text="5. Վճարված է", 
                                  variable=paid_var,
                                  bg=self.colors['background'],
                                  font=('Arial', 10))
        paid_check.grid(row=4, column=1, padx=10, pady=5, sticky="w")

        # Մեկնաբանություն
        tk.Label(form_frame, 
               text="6. Մեկնաբանություն:", 
               bg=self.colors['background'],
               font=('Arial', 10, 'bold')).grid(row=5, column=0, padx=10, pady=5, sticky="ne")
        comments_text = tk.Text(form_frame, 
                              width=40, 
                              height=5, 
                              font=('Arial', 10),
                              relief=tk.GROOVE,
                              bd=2)
        comments_text.grid(row=5, column=1, padx=10, pady=5, sticky="w")
        comments_text.insert("1.0", procedure_data[7])

        # Կոճակներ
        btn_frame = tk.Frame(form_frame, bg=self.colors['background'])
        btn_frame.grid(row=6, columnspan=2, pady=20)

        def save_changes():
            if not procedure_entry.get():
                messagebox.showwarning("Զգուշացում", "Մուտքագրեք աշխատանքի տեսակը")
                return
            if not date_entry.get():
                messagebox.showwarning("Զգուշացում", "Մուտքագրեք ամսաթիվը")
                return
            if not price_entry.get():
                messagebox.showwarning("Զգուշացում", "Մուտքագրեք գինը")
                return

            try:
                price = float(price_entry.get())
                cursor = self.conn.cursor()
                cursor.execute(
                    """UPDATE procedures SET 
                    procedure_date = ?,
                    procedure_type = ?,
                    tooth_number = ?,
                    price = ?,
                    is_paid = ?,
                    comments = ?
                    WHERE id = ?""",
                    (date_entry.get(),
                     procedure_entry.get(),
                     tooth_entry.get(),
                     price,
                     paid_var.get(),
                     comments_text.get("1.0", tk.END).strip(),
                     procedure_id)
                )
                self.conn.commit()
                dialog.destroy()
                messagebox.showinfo("Հաջողություն", "Աշխատանքը հաջողությամբ թարմացված է")
                self.status_bar.config(text="Աշխատանքը հաջողությամբ թարմացված է")
                
                # Թարմացնել աշխատանքների ցուցակը
                self.open_patient_card()
            except ValueError:
                messagebox.showerror("Սխալ", "Գինը պետք է լինի թիվ")
            except Exception as e:
                messagebox.showerror("Սխալ", f"Տվյալների թարմացման սխալ:\n{str(e)}")
                self.status_bar.config(text=f"Սխալ: {str(e)}")

        tk.Button(btn_frame, 
                 text="Պահպանել", 
                 command=save_changes,
                 bg=self.colors['success'],
                 fg='white',
                 font=('Arial', 10, 'bold'),
                 padx=15,
                 pady=5,
                 relief=tk.FLAT,
                 bd=0).pack(side=tk.LEFT, padx=10)

        tk.Button(btn_frame, 
                 text="Չեղարկել", 
                 command=dialog.destroy,
                 bg=self.colors['danger'],
                 fg='white',
                 font=('Arial', 10, 'bold'),
                 padx=15,
                 pady=5,
                 relief=tk.FLAT,
                 bd=0).pack(side=tk.LEFT, padx=10)

    def search_patient(self):
        search_term = simpledialog.askstring("Փնտրել հիվանդ", "Մուտքագրեք հիվանդի անունը կամ հեռախոսահամարը:")
        if not search_term:
            return
            
        for item in self.patients_tree.get_children():
            self.patients_tree.delete(item)
            
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT id, full_name, phone, birth_date 
            FROM patients 
            WHERE full_name LIKE ? OR phone LIKE ?
            ORDER BY full_name
        """, (f"%{search_term}%", f"%{search_term}%"))
        
        for row in cursor.fetchall():
            self.patients_tree.insert("", "end", values=row)

    def show_stats(self):
        cursor = self.conn.cursor()
        
        # Հաշվարկել հիվանդների ընդհանուր քանակը
        cursor.execute("SELECT COUNT(*) FROM patients")
        total_patients = cursor.fetchone()[0]
        
        # Հաշվարկել ընդհանուր եկամուտը
        cursor.execute("SELECT SUM(price) FROM procedures WHERE is_paid=1")
        total_income = cursor.fetchone()[0] or 0
        
        # Հաշվարկել չվճարված գումարը
        cursor.execute("SELECT SUM(price) FROM procedures WHERE is_paid=0")
        unpaid_amount = cursor.fetchone()[0] or 0
        
        # Ստեղծել վիճակագրության պատուհան
        stats_window = tk.Toplevel(self.root)
        stats_window.title("Վիճակագրություն")
        stats_window.geometry("500x300")
        stats_window.resizable(False, False)
        stats_window.configure(bg=self.colors['background'])

        # Վերնագիր
        header = tk.Label(stats_window, 
                        text="Կլինիկայի վիճակագրություն", 
                        font=('Arial', 14, 'bold'), 
                        bg=self.colors['primary'], 
                        fg='white',
                        padx=10,
                        pady=10)
        header.pack(fill=tk.X)

        # Վիճակագրության տվյալներ
        stats_frame = tk.Frame(stats_window, bg=self.colors['background'], padx=20, pady=20)
        stats_frame.pack(fill=tk.BOTH, expand=True)

        stats = [
            (f"1. Հիվանդների ընդհանուր քանակ՝ {total_patients}", 0),
            (f"2. Ընդհանուր եկամուտ՝ {total_income:.2f} դրամ", 1),
            (f"3. Չվճարված գումար՝ {unpaid_amount:.2f} դրամ", 2)
        ]

        for text, row in stats:
            tk.Label(stats_frame, 
                   text=text, 
                   font=('Arial', 12),
                   bg=self.colors['background'],
                   anchor='w').grid(row=row, column=0, sticky="w", padx=10, pady=10)

    def __del__(self):
        if hasattr(self, 'conn'):
            self.conn.close()

if __name__ == "__main__":
    root = tk.Tk()
    app = DentalClinicApp(root)
    root.mainloop()
