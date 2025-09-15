import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import sqlite3
from datetime import datetime

class ContractEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("برنامج تحرير العقود")
        self.root.geometry("1000x700")
        
        self.create_widgets()
        self.create_database()
        
    def create_database(self):
        conn = sqlite3.connect('contracts.db')
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS contracts
                     (id INTEGER PRIMARY KEY, title TEXT, content TEXT, 
                     created_date TEXT, modified_date TEXT)''')
        conn.commit()
        conn.close()
        
    def create_widgets(self):
        # إنشاء القوائم
        menubar = tk.Menu(self.root)
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="عقد جديد", command=self.new_contract)
        file_menu.add_command(label="فتح", command=self.open_contract)
        file_menu.add_command(label="حفظ", command=self.save_contract)
        file_menu.add_separator()
        file_menu.add_command(label="خروج", command=self.root.quit)
        menubar.add_cascade(label="ملف", menu=file_menu)
        
        # شريط الأدوات
        toolbar = tk.Frame(self.root, bd=1, relief=tk.RAISED)
        toolbar.pack(side=tk.TOP, fill=tk.X)
        
        # أزرار شريط الأدوات
        new_btn = tk.Button(toolbar, text="جديد", command=self.new_contract)
        new_btn.pack(side=tk.LEFT, padx=2, pady=2)
        
        save_btn = tk.Button(toolbar, text="حفظ", command=self.save_contract)
        save_btn.pack(side=tk.LEFT, padx=2, pady=2)
        
        # منطقة تحرير النص
        self.text_area = tk.Text(self.root, wrap=tk.WORD, font=("Arial", 12))
        self.text_area.pack(fill=tk.BOTH, expand=1, padx=5, pady=5)
        
        self.root.config(menu=menubar)
        
    def new_contract(self):
        self.text_area.delete(1.0, tk.END)
        self.current_file = None
        
    def save_contract(self):
        content = self.text_area.get(1.0, tk.END)
        title = simpledialog.askstring("العنوان", "أدخل عنوان العقد:")
        
        if title:
            conn = sqlite3.connect('contracts.db')
            c = conn.cursor()
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            c.execute("INSERT INTO contracts (title, content, created_date, modified_date) VALUES (?, ?, ?, ?)",
                     (title, content, now, now))
            conn.commit()
            conn.close()
            messagebox.showinfo("تم الحفظ", "تم حفظ العقد بنجاح")
        
    def open_contract(self):
        # سيتم تنفيذ وظيفة فتح العقود المحفوظة
        pass

if __name__ == "__main__":
    root = tk.Tk()
    app = ContractEditor(root)
    root.mainloop()