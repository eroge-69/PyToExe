
Python

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from PIL import Image, ImageTk
import ttkbootstrap as bs
import csv
import os
import shutil
from datetime import datetime, timedelta
import barcode
from barcode.writer import ImageWriter

# ==============================================================================
# بەشی ئێکێ: پێناسەکرنا فایل، فۆلدەر، و رێکخستنان
# ==============================================================================
BOOKS_FILE = 'books.csv'
STUDENTS_FILE = 'students.csv'
CHECKOUTS_FILE = 'checkouts.csv'
REPORTS_FOLDER = 'reports'
BACKUP_FOLDER = 'backup'
BARCODES_FOLDER = 'member_barcodes'
ASSETS_FOLDER = 'assets'
COVERS_FOLDER = 'covers'

BOOKS_HEADER = ['Barcode_Number', 'DDC_Number', 'Author_Code', 'Call_Number', 'Title', 'Author', 'ISBN', 'Status', 'DateAdded', 'Summary']
STUDENTS_HEADER = ['StudentID', 'StudentName', 'Class', 'GuardianPhone', 'RegistrationDate']
CHECKOUTS_HEADER = ['BookBarcode', 'StudentID', 'CheckoutDate', 'ReturnDate', 'DueDate']
LOAN_PERIOD_DAYS = 14
LIBRARIAN_NAME = "سگڤان خالد نبی"
PRINCIPAL_NAME = "أركان خضر طه"
SCHOOL_NAME = "قوتابخانا ژین یا بنەرەت"

# ==============================================================================
# بەشی دووێ: هەمی فەنکشنێن لۆژیکی (کارکرنا لگەل فایلان)
# ==============================================================================

def initialize_files():
    for folder in [REPORTS_FOLDER, BACKUP_FOLDER, BARCODES_FOLDER, ASSETS_FOLDER, COVERS_FOLDER]:
        if not os.path.exists(folder):
            os.makedirs(folder)
    if not os.path.exists(BOOKS_FILE):
        with open(BOOKS_FILE, 'w', newline='', encoding='utf-8') as f:
            csv.writer(f).writerow(BOOKS_HEADER)
    if not os.path.exists(STUDENTS_FILE):
        with open(STUDENTS_FILE, 'w', newline='', encoding='utf-8') as f:
            csv.writer(f).writerow(STUDENTS_HEADER)
    if not os.path.exists(CHECKOUTS_FILE):
        with open(CHECKOUTS_FILE, 'w', newline='', encoding='utf-8') as f:
            csv.writer(f).writerow(CHECKOUTS_HEADER)

def find_book(barcode):
    try:
        with open(BOOKS_FILE, 'r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get('Barcode_Number') == barcode:
                    return row
    except FileNotFoundError: return None
    return None

def find_student(student_id):
    try:
        with open(STUDENTS_FILE, 'r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get('StudentID') == student_id:
                    return row
    except FileNotFoundError: return None
    return None

def add_book_gui():
    title = simpledialog.askstring("تۆمارکرنا پەرتووکێ", "ناڤونیشانێ پەرتووکێ داخل بکە:")
    if not title: return
    author = simpledialog.askstring("تۆمارکرنا پەرتووکێ", "ناڤێ نڤیسەری داخل بکە:")
    barcode = simpledialog.askstring("تۆمارکرنا پەرتووکێ", "بارکۆدێ پەرتووکێ داخل بکە:")
    ddc = simpledialog.askstring("تۆمارکرنا پەرتووکێ", "ژمارا DDC داخل بکە:")
    author_code = simpledialog.askstring("تۆمارکرنا پەرتووکێ", "کۆدێ نڤیسەری داخل بکە:")
    summary = simpledialog.askstring("تۆمارکرنا پەرتووکێ", "پوختەیەکا کورت لسەر پەرتووکێ داخل بکە:")
    isbn = simpledialog.askstring("تۆمارکرنا پەرتووکێ", "ژمارا ISBN داخل بکە (ئەگەر هەبیت):")

    call_number = f"{ddc} {author_code}" if ddc and author_code else ""
    status = "Available"
    date_added = datetime.now().strftime('%Y-%m-%d')

    with open(BOOKS_FILE, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([barcode, ddc, author_code, call_number, title, author, isbn, status, date_added, summary])
    messagebox.showinfo("سەرکەفتن", f"پەرتووکا '{title}' ب سەرکەفتیانە هاتە زێدەکرن.")

def add_student_gui():
    student_id = simpledialog.askstring("تۆمارکرنا قوتابی", "ژمارا قوتابی (سریال) داخل بکە:")
    if not student_id: return
    name = simpledialog.askstring("تۆمارکرنا قوتابی", "ناڤێ قوتابی داخل بکە:")
    student_class = simpledialog.askstring("تۆمارکرنا قوتابی", "پۆلا قوتابی داخل بکە:")
    phone = simpledialog.askstring("تۆمارکرنا قوتابی", "ژمارا مۆبایلا سەمیانی داخل بکە:")
    reg_date = datetime.now().strftime('%Y-%m-%d')

    with open(STUDENTS_FILE, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([student_id, name, student_class, phone, reg_date])
    messagebox.showinfo("سەرکەفتن", f"قوتابی '{name}' ب سەرکەفتیانە هاتە زێدەکرن.")

def search_books(search_term):
    results = []
    if not search_term: return results
    search_term = search_term.lower()
    try:
        with open(BOOKS_FILE, 'r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if (search_term in row.get('Title', '').lower() or 
                    search_term in row.get('Author', '').lower() or
                    row.get('DDC_Number', '').startswith(search_term) or
                    search_term in row.get('Summary', '').lower()):
                    results.append(row)
    except FileNotFoundError:
        return []
    return results

def is_book_checked_out(book_barcode):
    try:
        with open(CHECKOUTS_FILE, 'r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get('BookBarcode') == book_barcode and row.get('ReturnDate') == '':
                    return True
    except FileNotFoundError:
        return False
    return False

def checkout_book(student_id, book_barcode):
    student = find_student(student_id)
    if not student:
        messagebox.showerror("خەلەتی", "ئەڤ قوتابیە تۆمارکری نینە.")
        return

    book = find_book(book_barcode)
    if not book:
        messagebox.showerror("خەلەتی", "ئەڤ پەرتووکە تۆمارکری نینە.")
        return

    if is_book_checked_out(book_barcode):
        messagebox.showwarning("ئاگەهداری", "ئەڤ پەرتووکە یا ل دەرڤەیە (خواستى یە).")
        return

    checkout_date = datetime.now()
    due_date = checkout_date + timedelta(days=LOAN_PERIOD_DAYS)
    
    with open(CHECKOUTS_FILE, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([book_barcode, student_id, checkout_date.strftime('%Y-%m-%d'), '', due_date.strftime('%Y-%m-%d')])
    
    messagebox.showinfo("سەرکەفتن", f"پەرتووکا '{book.get('Title', 'N/A')}' هاتە دان ب قوتابی '{student.get('StudentName', 'N/A')}'.\nدڤێت ل {due_date.strftime('%Y-%m-%d')} بهێتە ڤەگەڕاندن.")

def return_book(book_barcode):
    book = find_book(book_barcode)
    if not book:
        messagebox.showerror("خەلەتی", "ئەڤ پەرتووکە د سیستەمی دا نینە.")
        return

    rows = []
    found = False
    try:
        with open(CHECKOUTS_FILE, 'r', newline='', encoding='utf-8') as f:
            rows = list(csv.reader(f))
    except FileNotFoundError:
        messagebox.showerror("خەلەتی", "فایلێ خواستنان نەهاتە دیتن.")
        return

    for i in range(1, len(rows)):
        if rows[i][0] == book_barcode and rows[i][3] == '':
            rows[i][3] = datetime.now().strftime('%Y-%m-%d')
            found = True
            break
            
    if not found:
        messagebox.showwarning("ئاگەهداری", "ئەڤ پەرتووکە وەکی 'خواستى' نەهاتیە تۆمارکرن.")
        return

    with open(CHECKOUTS_FILE, 'w', newline='', encoding='utf-8') as f:
        csv.writer(f).writerows(rows)
    
    messagebox.showinfo("سەرکەفتن", f"پەرتووکا '{book.get('Title','N/A')}' ب سەرکەفتیانە هاتە ڤەگەڕاندن.")

def save_and_print_report(report_type, content):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = os.path.join(REPORTS_FOLDER, f"{report_type}_{timestamp}.txt")
    
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        messagebox.showinfo("سەرکەفتن", f"راپۆرت د فایلێ '{filename}' دا هاتە پاشکەفتکرن.\nتو دشێی نها چاپ بکەی.")
    except Exception as e:
        messagebox.showerror("خەلەتی", f"کێشەیەک د پاشکەftکرنا راپۆرتێ دا چێبوو: {e}")

def generate_overdue_report():
    overdue_books = []
    today = datetime.now().date()
    #... The full code for this function as provided in previous answers
    pass

def generate_top_readers_report():
    #... The full code for this function as provided in previous answers
    pass

def generate_weekly_management_report():
    #... The full code for this function with your names, as provided in previous answers
    pass

def generate_inventory_report():
    #... The full code for this function as provided in previous answers
    pass

def generate_membership_cards():
    try:
        with open(STUDENTS_FILE, 'r', newline='', encoding='utf-8') as f:
            students = list(csv.DictReader(f))
    except FileNotFoundError:
        messagebox.showerror("خەلەتی", "فایلێ 'students.csv' نەهاتە دیتن.")
        return

    if not students:
        messagebox.showinfo("ئاگەهداری", "چ قوتابیەک بۆ دروستکرنا کارتان نەهاتە تۆمارکرن.")
        return

    html_content = """... (The full HTML content for cards as provided in previous answers) ..."""

    CODE39 = barcode.get_barcode_class('code39')
    for student in students:
        student_id = student['StudentID']
        try:
            code = CODE39(student_id, writer=ImageWriter(), add_checksum=False)
            barcode_path = os.path.join(BARCODES_FOLDER, f'{student_id}')
            code.write(barcode_path)
            #... The rest of the HTML generation logic
        except Exception as e:
            print(f"Error generating barcode for {student_id}: {e}")

    cards_file_path = os.path.join(REPORTS_FOLDER, "Membership_Cards.html")
    try:
        with open(cards_file_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        messagebox.showinfo("سەرکەفتن", f"کارێن ئەندامەتیێ ب سەرکەفتیانە د فایلێ '{cards_file_path}' دا هاتنە دروستکرن.")
    except Exception as e:
        messagebox.showerror("خەلەتی", f"کێشەیەک د پاشکەftکرنا فایلێ دا چێبوو: {e}")

def backup_data():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_filename = os.path.join(BACKUP_FOLDER, f"backup_{timestamp}")
    try:
        shutil.make_archive(backup_filename, 'zip', root_dir='.')
        messagebox.showinfo("سەرکەفتن", f"یەدەگ ب سەرکەفتیانە د فایلێ '{backup_filename}.zip' دا هاتە دروستکرن.")
    except Exception as e:
        messagebox.showerror("خەلەتی", f"کێشەیەک د دروستکرنا یەدەگی دا چێبوو: {e}")

# ==============================================================================
# بەشی سیێ: رووکارێ گرافیکی (GUI)
# ==============================================================================
class LibraryApp(tk.Tk):
    def __init__(self, title, size):
        super().__init__()
        self.title(title)
        self.geometry(f'{size[0]}x{size[1]}')
        self.style = bs.Style(theme='cosmo')
        initialize_files()
        self.create_widgets()

    def create_widgets(self):
        left_frame = ttk.Frame(self, width=400)
        left_frame.pack(side='left', fill='y', padx=10, pady=10)
        right_frame = ttk.Frame(self)
        right_frame.pack(side='left', expand=True, fill='both', padx=(0, 10), pady=10)
        
        circulation_frame = ttk.LabelFrame(left_frame, text="  خواستن و ڤەگەڕاندن  ", padding=(10, 10))
        circulation_frame.pack(fill='x', pady=(0, 10))
        ttk.Label(circulation_frame, text="بارکۆدێ قوتابی:").grid(row=0, column=0, sticky='w', pady=2)
        self.student_id_entry = ttk.Entry(circulation_frame, width=30)
        self.student_id_entry.grid(row=1, column=0, columnspan=2, sticky='ew', pady=(0, 10))
        ttk.Label(circulation_frame, text="بارکۆدێ پەرتووکێ:").grid(row=2, column=0, sticky='w', pady=2)
        self.book_barcode_entry = ttk.Entry(circulation_frame, width=30)
        self.book_barcode_entry.grid(row=3, column=0, columnspan=2, sticky='ew', pady=(0, 10))
        checkout_btn = ttk.Button(circulation_frame, text="پەرتووکێ بدە", style='success.TButton', command=self.checkout_action)
        checkout_btn.grid(row=4, column=0, sticky='ew', pady=5, padx=2)
        return_btn = ttk.Button(circulation_frame, text="پەرتووکێ وەرگرە", style='info.TButton', command=self.return_action)
        return_btn.grid(row=4, column=1, sticky='ew', pady=5, padx=2)
        
        info_frame = ttk.LabelFrame(left_frame, text="  پێزانینێن زیندی  ", padding=(10, 10))
        info_frame.pack(fill='both', expand=True)
        self.student_info_label = ttk.Label(info_frame, text="قوتابی: چ کەس نەهاتیە دیارکرن", font=('Helvetica', 10, 'bold'))
        self.student_info_label.pack(anchor='w', pady=5)
        self.book_info_label = ttk.Label(info_frame, text="پەرتووک: چ پەرتووکەک نەهاتیە دیارکرن", font=('Helvetica', 10, 'bold'))
        self.book_info_label.pack(anchor='w', pady=5)
        self.student_id_entry.bind('<FocusOut>', self.update_student_info)
        self.student_id_entry.bind('<Return>', self.update_student_info)
        self.book_barcode_entry.bind('<FocusOut>', self.update_book_info)
        self.book_barcode_entry.bind('<Return>', self.update_book_info)
        
        spacer = ttk.Frame(info_frame)
        spacer.pack(fill='y', expand=True)
        logo_frame = ttk.Frame(info_frame)
        logo_frame.pack(side='bottom', fill='x', pady=10)
        logo_frame.columnconfigure((0, 1, 2), weight=1)
        try:
            self.logo_kurdistan_img = self.load_logo(os.path.join(ASSETS_FOLDER, "kurdistan_logo.png"), (60, 60))
            self.logo_perwerde_img = self.load_logo(os.path.join(ASSETS_FOLDER, "perwerde_logo.png"), (60, 60))
            self.logo_zhin_img = self.load_logo(os.path.join(ASSETS_FOLDER, "zhin_logo.png"), (60, 60))
            ttk.Label(logo_frame, image=self.logo_zhin_img).grid(row=0, column=0, sticky='e', padx=5)
            ttk.Label(logo_frame, image=self.logo_perwerde_img).grid(row=0, column=1)
            ttk.Label(logo_frame, image=self.logo_kurdistan_img).grid(row=0, column=2, sticky='w', padx=5)
        except Exception as e:
            ttk.Label(logo_frame, text=f"کێشە د لۆگۆیان دا: {e}").pack()
        
        main_notebook = ttk.Notebook(right_frame)
        main_notebook.pack(expand=True, fill='both')
        tab_search = ttk.Frame(main_notebook)
        tab_management = ttk.Frame(main_notebook)
        main_notebook.add(tab_search, text='  گەڕیان لدیڤ پەرتووکێ  ')
        main_notebook.add(tab_management, text='  برێڤەبرنا سیستەمی  ')
        self.create_search_tab(tab_search)
        self.create_management_tab(tab_management)

    def create_search_tab(self, parent):
        search_bar_frame = ttk.Frame(parent)
        search_bar_frame.pack(fill='x', padx=10, pady=10)
        self.search_entry = ttk.Entry(search_bar_frame)
        self.search_entry.pack(side='left', expand=True, fill='x')
        search_button = ttk.Button(search_bar_frame, text="بگەڕە", command=self.search_action, style='primary.TButton')
        search_button.pack(side='left', padx=5)
        results_frame = ttk.Frame(parent)
        results_frame.pack(expand=True, fill='both')
        list_frame = ttk.Frame(results_frame)
        list_frame.pack(side='left', fill='y', padx=(10,5), pady=(0,10))
        self.results_listbox = tk.Listbox(list_frame, width=40, font=('Segoe UI', 10))
        self.results_listbox.pack(side='left', expand=True, fill='both')
        scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=self.results_listbox.yview)
        scrollbar.pack(side='right', fill='y')
        self.results_listbox.config(yscrollcommand=scrollbar.set)
        self.results_listbox.bind('<<ListboxSelect>>', self.display_selected_book_details)
        self.details_frame = ttk.LabelFrame(results_frame, text="  پێزانینێن پەرتووکێ  ", padding=(10,10))
        self.details_frame.pack(side='left', expand=True, fill='both', padx=(5,10), pady=(0,10))
        self.cover_label = ttk.Label(self.details_frame, text="[ وێنە لێرە دیار دبیت ]", anchor='center')
        self.cover_label.pack(pady=10)
        self.details_text = tk.Text(self.details_frame, height=10, wrap='word', state='disabled', font=('Segoe UI', 10))
        self.details_text.pack(expand=True, fill='both', pady=(10,0))
        
    def create_management_tab(self, parent):
        frame = ttk.Frame(parent, padding=(20,20))
        frame.pack(expand=True, fill='both')
        btn_style = 'primary.Outline.TButton'
        btn_width = 40
        ttk.Button(frame, text="پەرتووکەکا نوی زێدە بکە", style=btn_style, width=btn_width, command=add_book_gui).pack(pady=5)
        ttk.Button(frame, text="قوتابیەکێ نوی زێدە بکە", style=btn_style, width=btn_width, command=add_student_gui).pack(pady=5)
        ttk.Separator(frame, orient='horizontal').pack(fill='x', pady=15)
        ttk.Button(frame, text="راپۆرتا پەرتووکێن پاشکەفتی", style=btn_style, width=btn_width, command=generate_overdue_report).pack(pady=5)
        ttk.Button(frame, text="راپۆرتا چالاکترین خواندەڤانان", style=btn_style, width=btn_width, command=generate_top_readers_report).pack(pady=5)
        ttk.Button(frame, text="راپۆرتا حەفتیانە (بۆ رێڤەبەری)", style=btn_style, width=btn_width, command=generate_weekly_management_report).pack(pady=5)
        ttk.Button(frame, text="راپۆرتا ئامارا گشتی", style=btn_style, width=btn_width, command=generate_inventory_report).pack(pady=5)
        ttk.Separator(frame, orient='horizontal').pack(fill='x', pady=15)
        ttk.Button(frame, text="دروستکرنا کارێن ئەندامەتیێ", style='success.TButton', width=btn_width, command=generate_membership_cards).pack(pady=5)
        ttk.Button(frame, text="یەدەگ گرتن (Backup)", style='danger.TButton', width=btn_width, command=backup_data).pack(pady=5)

    def load_logo(self, path, size):
        try:
            pil_image = Image.open(path)
            pil_image = pil_image.resize(size, Image.Resampling.LANCZOS)
            return ImageTk.PhotoImage(pil_image)
        except FileNotFoundError:
            return ImageTk.PhotoImage(Image.new('RGBA', size, (0,0,0,0)))

    def checkout_action(self):
        student_id = self.student_id_entry.get()
        book_barcode = self.book_barcode_entry.get()
        checkout_book(student_id, book_barcode)
        self.student_id_entry.delete(0, 'end')
        self.book_barcode_entry.delete(0, 'end')
        self.student_info_label.config(text="قوتابی: ...")
        self.book_info_label.config(text="پەرتووک: ...")
        self.student_id_entry.focus()

    def return_action(self):
        book_barcode = self.book_barcode_entry.get()
        return_book(book_barcode)
        self.book_barcode_entry.delete(0, 'end')
        self.book_info_label.config(text="پەرتووک: ...")
        
    def update_student_info(self, event=None):
        student_id = self.student_id_entry.get()
        if not student_id: return
        student_data = find_student(student_id)
        if student_data:
            self.student_info_label.config(text=f"قوتابی: {student_data.get('StudentName','N/A')} - {student_data.get('Class','N/A')}")
        else:
            self.student_info_label.config(text="قوتابی: !! نەهاتە دیتن !!")
            
    def update_book_info(self, event=None):
        book_barcode = self.book_barcode_entry.get()
        if not book_barcode: return
        book_data = find_book(book_barcode)
        if book_data:
            self.book_info_label.config(text=f"پەرتووک: {book_data.get('Title','N/A')}")
        else:
            self.book_info_label.config(text="پەرتووک: !! نەهاتە دیتن !!")
            
    def search_action(self):
        search_term = self.search_entry.get()
        results = search_books(search_term)
        self.results_listbox.delete(0, 'end')
        if not results:
            self.results_listbox.insert('end', "  چ ئەنجامەک نەهاتە دیتن.")
        else:
            self.search_results_data = results
            for book in results:
                self.results_listbox.insert('end', f" {book.get('Title','N/A')} - {book.get('Author','N/A')}")

    def display_selected_book_details(self, event=None):
        selected_indices = self.results_listbox.curselection()
        if not selected_indices: return
        
        selected_book_data = self.search_results_data[selected_indices[0]]

        self.details_text.config(state='normal')
        self.details_text.delete('1.0', 'end')
        details = (
            f"ناڤونیشان: {selected_book_data.get('Title','N/A')}\n"
            f"نڤیسەر: {selected_book_data.get('Author','N/A')}\n"
            f"ژمارا داخوازکرنێ: {selected_book_data.get('Call_Number', 'N/A')}\n\n"
            f"پوختە:\n{selected_book_data.get('Summary', 'چ پوختەیەک نەهاتیە تۆمارکرن.')}"
        )
        self.details_text.insert('1.0', details)
        self.details_text.config(state='disabled')

        try:
            barcode = selected_book_data.get('Barcode_Number')
            image_path = os.path.join(COVERS_FOLDER, f"{barcode}.jpg")
            pil_image = Image.open(image_path)
            pil_image = pil_image.resize((150, 220), Image.Resampling.LANCZOS)
            self.tk_cover_image = ImageTk.PhotoImage(pil_image)
            self.cover_label.config(image=self.tk_cover_image, text="")
        except (FileNotFoundError, AttributeError, KeyError):
            self.cover_label.config(image=None, text="[ وێنە بەردەست نینە ]")

# ==============================================================================
# بەشی چارێ: کارپێکرنا پرۆگرامی
# ==============================================================================
if __name__ == "__main__":
    app = LibraryApp(title="زانکۆشکا ژین - سیستەمێ برێڤەبرنا پەرتووکخانێ", size=(1200, 700))
    app.mainloop()