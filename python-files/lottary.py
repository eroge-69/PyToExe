import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import random
import json
from datetime import datetime
import os

try:
    import xlsxwriter
except ImportError:
    xlsxwriter = None

# Create lottery folder on desktop if not exists
DESKTOP_PATH = os.path.join(os.path.expanduser('~'), 'Desktop')
LOTTERY_FOLDER = os.path.join(DESKTOP_PATH, 'قرعه کشی')
os.makedirs(LOTTERY_FOLDER, exist_ok=True)

SAVE_FILE = os.path.join(LOTTERY_FOLDER, 'lottery_data.json')
EXCEL_FILE = os.path.join(LOTTERY_FOLDER, 'نتایج.xlsx')

class DataManager:
    @staticmethod
    def load_data():
        try:
            with open(SAVE_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # Ensure all required keys exist
                if 'all_participants' not in data:
                    data['all_participants'] = []
                if 'all_prizes' not in data:
                    data['all_prizes'] = []
                if 'active_participants' not in data:
                    data['active_participants'] = []
                if 'active_prizes' not in data:
                    data['active_prizes'] = []
                if 'history' not in data:
                    data['history'] = []
                return data
        except (FileNotFoundError, json.JSONDecodeError):
            return {
                'all_participants': [],
                'all_prizes': [],
                'active_participants': [],
                'active_prizes': [],
                'history': []
            }

    @staticmethod
    def save_data(data):
        with open(SAVE_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

class LotteryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("سیستم پیشرفته قرعه‌کشی")
        self.root.geometry("1000x700")
        
        self.data_manager = DataManager()
        self.data = self.data_manager.load_data()
        
        self.create_widgets()
        self.load_data()
        
    def create_widgets(self):
        # Main Notebook
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Database Tab
        self.db_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.db_frame, text="پایگاه داده")
        
        # Lottery Tab
        self.lottery_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.lottery_frame, text="قرعه‌کشی")
        
        # Create Database Tab
        self.create_database_tab()
        
        # Create Lottery Tab
        self.create_lottery_tab()
        
    def create_database_tab(self):
        # Participants Section
        ttk.Label(self.db_frame, text="لیست اصلی افراد:").grid(row=0, column=0, padx=5, pady=5)
        
        self.all_participants_list = tk.Listbox(self.db_frame, height=15, width=30, selectmode=tk.MULTIPLE)
        self.all_participants_list.grid(row=1, column=0, padx=5, pady=5, sticky='nsew')
        
        # Participants Controls
        ttk.Button(self.db_frame, text="حذف انتخاب شده‌ها", 
                  command=lambda: self.remove_items(self.all_participants_list, 'all_participants')).grid(row=2, column=0)
        
        # Prizes Section
        ttk.Label(self.db_frame, text="لیست اصلی جوایز:").grid(row=0, column=1, padx=5, pady=5)
        
        self.all_prizes_list = tk.Listbox(self.db_frame, height=15, width=30, selectmode=tk.MULTIPLE)
        self.all_prizes_list.grid(row=1, column=1, padx=5, pady=5, sticky='nsew')
        
        # Prizes Controls
        ttk.Button(self.db_frame, text="حذف انتخاب شده‌ها", 
                  command=lambda: self.remove_items(self.all_prizes_list, 'all_prizes')).grid(row=2, column=1)
        
        # Add Items Section
        add_frame = ttk.Frame(self.db_frame)
        add_frame.grid(row=3, column=0, columnspan=2, pady=10)
        
        ttk.Label(add_frame, text="نام فرد:").grid(row=0, column=0)
        self.new_participant = ttk.Entry(add_frame, width=25)
        self.new_participant.grid(row=0, column=1)
        self.new_participant.bind('<Return>', lambda e: self.add_participant())
        
        ttk.Button(add_frame, text="+ افزودن فرد", command=self.add_participant).grid(row=0, column=2, padx=5)
        
        ttk.Label(add_frame, text="جایزه جدید:").grid(row=1, column=0)
        self.new_prize = ttk.Entry(add_frame, width=25)
        self.new_prize.grid(row=1, column=1)
        self.new_prize.bind('<Return>', lambda e: self.add_prize())
        
        ttk.Button(add_frame, text="+ افزودن جایزه", command=self.add_prize).grid(row=1, column=2, padx=5)
        
    def create_lottery_tab(self):
        # Active Participants Section
        ttk.Label(self.lottery_frame, text="شرکت کنندگان فعال:").grid(row=0, column=0, padx=5, pady=5)
        
        self.active_participants_list = tk.Listbox(self.lottery_frame, height=15, width=30, selectmode=tk.MULTIPLE)
        self.active_participants_list.grid(row=1, column=0, padx=5, pady=5, sticky='nsew')
        
        # Transfer Buttons
        btn_frame = ttk.Frame(self.lottery_frame)
        btn_frame.grid(row=1, column=1, padx=10)
        
        ttk.Button(btn_frame, text="<< اضافه به قرعه‌کشی", 
                  command=self.add_to_active_participants).pack(pady=5)
        ttk.Button(btn_frame, text="حذف از قرعه‌کشی >>", 
                  command=self.remove_from_active_participants).pack(pady=5)
        
        # Active Prizes Section
        ttk.Label(self.lottery_frame, text="جوایز فعال:").grid(row=0, column=2, padx=5, pady=5)
        
        self.active_prizes_list = tk.Listbox(self.lottery_frame, height=15, width=30, selectmode=tk.MULTIPLE)
        self.active_prizes_list.grid(row=1, column=2, padx=5, pady=5, sticky='nsew')
        
        # Prize Transfer Buttons
        prize_btn_frame = ttk.Frame(self.lottery_frame)
        prize_btn_frame.grid(row=1, column=3, padx=10)
        
        ttk.Button(prize_btn_frame, text="<< اضافه جوایز", 
                  command=self.add_to_active_prizes).pack(pady=5)
        ttk.Button(prize_btn_frame, text="حذف جوایز >>", 
                  command=self.remove_from_active_prizes).pack(pady=5)
        
        # Lottery Controls
        control_frame = ttk.Frame(self.lottery_frame)
        control_frame.grid(row=2, column=0, columnspan=4, pady=10)
        
        ttk.Button(control_frame, text="شروع قرعه‌کشی", command=self.run_lottery).pack(side='left', padx=5)
        ttk.Button(control_frame, text="بازنشانی قرعه‌کشی", command=self.reset_lottery).pack(side='left', padx=5)
        ttk.Button(control_frame, text="نمایش تاریخچه", command=self.show_history).pack(side='left', padx=5)
        ttk.Button(control_frame, text="خروجی اکسل", command=self.export_to_excel).pack(side='left', padx=5)
        
        # History Section
        ttk.Label(self.lottery_frame, text="تاریخچه:").grid(row=3, column=0, columnspan=4, pady=5)
        
        self.history_text = tk.Text(self.lottery_frame, height=8, state='disabled')
        self.history_text.grid(row=4, column=0, columnspan=4, sticky='nsew', padx=5, pady=5)
        
        # Configure grid weights
        self.lottery_frame.grid_rowconfigure(1, weight=1)
        self.lottery_frame.grid_columnconfigure(0, weight=1)
        self.lottery_frame.grid_columnconfigure(2, weight=1)
        
    def load_data(self):
        # Load all participants
        self.all_participants_list.delete(0, tk.END)
        for participant in self.data['all_participants']:
            self.all_participants_list.insert(tk.END, participant)
        
        # Load all prizes
        self.all_prizes_list.delete(0, tk.END)
        for prize in self.data['all_prizes']:
            self.all_prizes_list.insert(tk.END, prize)
        
        # Load active participants
        self.active_participants_list.delete(0, tk.END)
        for participant in self.data['active_participants']:
            self.active_participants_list.insert(tk.END, participant)
        
        # Load active prizes
        self.active_prizes_list.delete(0, tk.END)
        for prize in self.data['active_prizes']:
            self.active_prizes_list.insert(tk.END, prize)
        
        # Load history
        self.history_text.config(state='normal')
        self.history_text.delete(1.0, tk.END)
        for entry in reversed(self.data['history'][-10:]):
            self.history_text.insert(tk.END, entry + '\n')
        self.history_text.config(state='disabled')
    
    def add_participant(self):
        name = self.new_participant.get().strip()
        if name and name not in self.data['all_participants']:
            self.data['all_participants'].append(name)
            self.all_participants_list.insert(tk.END, name)
            self.new_participant.delete(0, tk.END)
            self.data_manager.save_data(self.data)
    
    def add_prize(self):
        prize = self.new_prize.get().strip()
        if prize and prize not in self.data['all_prizes']:
            self.data['all_prizes'].append(prize)
            self.all_prizes_list.insert(tk.END, prize)
            self.new_prize.delete(0, tk.END)
            self.data_manager.save_data(self.data)
    
    def remove_items(self, listbox, data_key):
        selected = listbox.curselection()
        if not selected:
            return
            
        for index in reversed(selected):
            item = listbox.get(index)
            self.data[data_key].remove(item)
            listbox.delete(index)
        
        self.data_manager.save_data(self.data)
        self.load_data()
    
    def add_to_active_participants(self):
        selected = self.all_participants_list.curselection()
        if not selected:
            return
            
        for index in selected:
            participant = self.all_participants_list.get(index)
            if participant not in self.data['active_participants']:
                self.data['active_participants'].append(participant)
        
        self.data_manager.save_data(self.data)
        self.load_data()
    
    def remove_from_active_participants(self):
        selected = self.active_participants_list.curselection()
        if not selected:
            return
            
        for index in reversed(selected):
            participant = self.active_participants_list.get(index)
            self.data['active_participants'].remove(participant)
        
        self.data_manager.save_data(self.data)
        self.load_data()
    
    def add_to_active_prizes(self):
        selected = self.all_prizes_list.curselection()
        if not selected:
            return
            
        for index in selected:
            prize = self.all_prizes_list.get(index)
            if prize not in self.data['active_prizes']:
                self.data['active_prizes'].append(prize)
        
        self.data_manager.save_data(self.data)
        self.load_data()
    
    def remove_from_active_prizes(self):
        selected = self.active_prizes_list.curselection()
        if not selected:
            return
            
        for index in reversed(selected):
            prize = self.active_prizes_list.get(index)
            self.data['active_prizes'].remove(prize)
        
        self.data_manager.save_data(self.data)
        self.load_data()
    
    def run_lottery(self):
        if not self.data['active_participants']:
            messagebox.showwarning("هشدار", "هیچ شرکت کننده فعالی وجود ندارد!")
            return
            
        if not self.data['active_prizes']:
            messagebox.showwarning("هشدار", "هیچ جایزه فعالی وجود ندارد!")
            return
            
        winner = random.choice(self.data['active_participants'])
        prize = random.choice(self.data['active_prizes'])
        
        # Remove prize and winner
        self.data['active_prizes'].remove(prize)
        self.data['active_participants'].remove(winner)
        
        # Add to history
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        entry = f"{timestamp}: {winner} برنده {prize} شد"
        self.data['history'].append(entry)
        
        self.data_manager.save_data(self.data)
        self.load_data()
        
        # Show winner in simple messagebox
        messagebox.showinfo("نتیجه قرعه‌کشی", f"{winner} برنده {prize} شد!")
        
        # Export to Excel
        self.export_to_excel(silent=True)
    
    def reset_lottery(self):
        self.data['active_participants'] = []
        self.data['active_prizes'] = []
        self.data_manager.save_data(self.data)
        self.load_data()
        messagebox.showinfo("اطلاعیه", "قرعه‌کشی بازنشانی شد.")
    
    def show_history(self):
        win = tk.Toplevel(self.root)
        win.title("تاریخچه کامل")
        win.geometry("600x400")
        
        text = tk.Text(win, state='normal')
        text.pack(fill='both', expand=True, padx=10, pady=10)
        
        for entry in reversed(self.data['history']):
            text.insert(tk.END, entry + '\n')
        
        text.config(state='disabled')
    
    def export_to_excel(self, silent=False):
        if not self.data['history']:
            if not silent:
                messagebox.showerror("خطا", "تاریخچه‌ای برای ذخیره وجود ندارد!")
            return
            
        if xlsxwriter is None:
            if not silent:
                messagebox.showerror("خطا", "کتابخانه xlsxwriter نصب نشده است!")
            return
            
        try:
            # Check if file exists
            file_exists = os.path.exists(EXCEL_FILE)
            
            workbook = xlsxwriter.Workbook(EXCEL_FILE)
            worksheet = workbook.add_worksheet()
            
            # Write headers if new file
            if not file_exists:
                worksheet.write(0, 0, "تاریخ")
                worksheet.write(0, 1, "برنده")
                worksheet.write(0, 2, "جایزه")
                start_row = 1
            else:
                # Find last row in existing file
                start_row = len(self.data['history'])
            
            # Write data
            for row, entry in enumerate(self.data['history'], start_row):
                parts = entry.split(": ")
                if len(parts) == 2:
                    date, rest = parts
                    winner_prize = rest.split(" برنده ")
                    if len(winner_prize) == 2:
                        worksheet.write(row, 0, date)
                        worksheet.write(row, 1, winner_prize[0])
                        worksheet.write(row, 2, winner_prize[1].replace(" شد", ""))  # Remove "شد" from prize
            
            workbook.close()
            if not silent:
                messagebox.showinfo("موفقیت", f"نتایج در فایل {EXCEL_FILE} ذخیره شد!")
        except Exception as e:
            if not silent:
                messagebox.showerror("خطا", f"خطا در ذخیره فایل: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = LotteryApp(root)
    root.mainloop()