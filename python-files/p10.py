


import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import sqlite3
import os
from datetime import datetime

class IranianPlateSearchApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Iranian Vehicle Plate Search")
        self.root.geometry("900x700")
        self.root.configure(bg="#f0f8ff")
        
        # Create database
        self.create_database()
        
        # Create UI
        self.create_widgets()
        
    def create_database(self):
        self.conn = sqlite3.connect('iranian_plates.db')
        self.cursor = self.conn.cursor()
        
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS plates (
            id INTEGER PRIMARY KEY,
            two_digit1 TEXT,
            letter TEXT,
            three_digit TEXT,
            two_digit2 TEXT,
            full_plate TEXT UNIQUE
        )
        ''')
        
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS search_history (
            id INTEGER PRIMARY KEY,
            search_query TEXT,
            search_date TEXT
        )
        ''')
        
        self.conn.commit()
        
    def create_widgets(self):
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Create tabs
        self.create_search_tab()
        self.create_file_tab()
        self.create_history_tab()
        
    def create_search_tab(self):
        search_tab = tk.Frame(self.notebook, bg="#f0f8ff")
        self.notebook.add(search_tab, text="Search")
        
        # Title frame
        title_frame = tk.Frame(search_tab, bg="#1e3a8a", height=60)
        title_frame.pack(fill='x', padx=5, pady=5)
        title_frame.pack_propagate(False)
        
        tk.Label(
            title_frame, 
            text="Iranian Vehicle Plate Search",
            font=("Arial", 16, "bold"),
            bg="#1e3a8a", 
            fg="white"
        ).pack(expand=True)
        
        # Input frame
        input_frame = tk.Frame(search_tab, bg="#e0f2fe", relief="ridge", bd=2)
        input_frame.pack(fill='x', padx=10, pady=10)
        
        # Plate input fields
        fields_frame = tk.Frame(input_frame, bg="#e0f2fe")
        fields_frame.pack(pady=15)
        
        # Two digits 1
        tk.Label(fields_frame, text="First Two Digits:", bg="#e0f2fe", font=("Arial", 12)).grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.two_digit1 = tk.Entry(fields_frame, width=5, font=("Arial", 14))
        self.two_digit1.grid(row=0, column=1, padx=5, pady=5)
        
        # Letter
        tk.Label(fields_frame, text="Persian Letter:", bg="#e0f2fe", font=("Arial", 12)).grid(row=0, column=2, padx=5, pady=5, sticky='w')
        self.letter = tk.Entry(fields_frame, width=5, font=("Arial", 14))
        self.letter.grid(row=0, column=3, padx=5, pady=5)
        
        # Three digits
        tk.Label(fields_frame, text="Three Digits:", bg="#e0f2fe", font=("Arial", 12)).grid(row=0, column=4, padx=5, pady=5, sticky='w')
        self.three_digit = tk.Entry(fields_frame, width=5, font=("Arial", 14))
        self.three_digit.grid(row=0, column=5, padx=5, pady=5)
        
        # Two digits 2
        tk.Label(fields_frame, text="Second Two Digits:", bg="#e0f2fe", font=("Arial", 12)).grid(row=0, column=6, padx=5, pady=5, sticky='w')
        self.two_digit2 = tk.Entry(fields_frame, width=5, font=("Arial", 14))
        self.two_digit2.grid(row=0, column=7, padx=5, pady=5)
        
        # Search button
        search_button = tk.Button(
            input_frame, 
            text="Search Plate",
            bg="#059669", 
            fg="white",
            font=("Arial", 12, "bold"),
            command=self.search_plate,
            padx=20,
            pady=10
        )
        search_button.pack(pady=10)
        
        # Results frame
        results_frame = tk.Frame(search_tab, bg="#f0f8ff")
        results_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Results title
        tk.Label(
            results_frame, 
            text="Search Results",
            font=("Arial", 14, "bold"),
            bg="#f0f8ff",
            fg="#1e3a8a"
        ).pack(anchor='w', padx=5, pady=5)
        
        # Results listbox
        self.results_listbox = tk.Listbox(
            results_frame,
            font=("Arial", 12),
            bg="white",
            selectbackground="#3b82f6",
            height=15
        )
        self.results_listbox.pack(fill='both', expand=True, padx=5, pady=5)
        
    def create_file_tab(self):
        file_tab = tk.Frame(self.notebook, bg="#f0f8ff")
        self.notebook.add(file_tab, text="File Management")
        
        # Title frame
        title_frame = tk.Frame(file_tab, bg="#059669", height=60)
        title_frame.pack(fill='x', padx=5, pady=5)
        title_frame.pack_propagate(False)
        
        tk.Label(
            title_frame, 
            text="Data Import Management",
            font=("Arial", 16, "bold"),
            bg="#059669", 
            fg="white"
        ).pack(expand=True)
        
        # File selection frame
        file_frame = tk.Frame(file_tab, bg="#dcfce7", relief="ridge", bd=2)
        file_frame.pack(fill='x', padx=10, pady=10)
        
        # File path
        tk.Label(file_frame, text="File Path:", bg="#dcfce7", font=("Arial", 12)).grid(row=0, column=0, padx=5, pady=10, sticky='w')
        self.file_path = tk.Entry(file_frame, width=50, font=("Arial", 12))
        self.file_path.grid(row=0, column=1, padx=5, pady=10)
        
        # Browse button
        browse_button = tk.Button(
            file_frame, 
            text="Browse",
            bg="#3b82f6", 
            fg="white",
            font=("Arial", 12),
            command=self.browse_file,
            padx=15
        )
        browse_button.grid(row=0, column=2, padx=5, pady=10)
        
        # Import button
        import_button = tk.Button(
            file_frame, 
            text="Import Data",
            bg="#059669", 
            fg="white",
            font=("Arial", 12, "bold"),
            command=self.import_data,
            padx=20,
            pady=10
        )
        import_button.grid(row=1, column=1, padx=5, pady=10)
        
        # Instructions
        instructions = tk.Label(
            file_frame,
            text="File should contain one plate per line in format: [Two Digits] [Letter] [Three Digits] [Two Digits]",
            bg="#dcfce7",
            font=("Arial", 10),
            fg="#166534"
        )
        instructions.grid(row=2, column=0, columnspan=3, padx=5, pady=5)
        
    def create_history_tab(self):
        history_tab = tk.Frame(self.notebook, bg="#f0f8ff")
        self.notebook.add(history_tab, text="Search History")
        
        # Title frame
        title_frame = tk.Frame(history_tab, bg="#3b82f6", height=60)
        title_frame.pack(fill='x', padx=5, pady=5)
        title_frame.pack_propagate(False)
        
        tk.Label(
            title_frame, 
            text="Search History",
            font=("Arial", 16, "bold"),
            bg="#3b82f6", 
            fg="white"
        ).pack(expand=True)
        
        # History frame
        history_frame = tk.Frame(history_tab, bg="#dbeafe", relief="ridge", bd=2)
        history_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # History listbox
        self.history_listbox = tk.Listbox(
            history_frame,
            font=("Arial", 12),
            bg="white",
            selectbackground="#3b82f6",
            height=20
        )
        self.history_listbox.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Clear history button
        clear_button = tk.Button(
            history_frame, 
            text="Clear History",
            bg="#dc2626", 
            fg="white",
            font=("Arial", 12, "bold"),
            command=self.clear_history,
            padx=20,
            pady=10
        )
        clear_button.pack(pady=10)
        
        # Load history
        self.load_history()
        
    def browse_file(self):
        filename = filedialog.askopenfilename(
            title="Select Data File",
            filetypes=[("Text files", "*.txt"), ("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if filename:
            self.file_path.delete(0, tk.END)
            self.file_path.insert(0, filename)
            
    def import_data(self):
        file_path = self.file_path.get()
        if not file_path or not os.path.exists(file_path):
            messagebox.showerror("Error", "File not found")
            return
            
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                lines = file.readlines()
                
            imported_count = 0
            for line in lines:
                parts = line.strip().split()
                if len(parts) == 4:
                    two_digit1, letter, three_digit, two_digit2 = parts
                    full_plate = f"{two_digit1} {letter} {three_digit} {two_digit2}"
                    
                    try:
                        self.cursor.execute(
                            "INSERT OR IGNORE INTO plates (two_digit1, letter, three_digit, two_digit2, full_plate) VALUES (?, ?, ?, ?, ?)",
                            (two_digit1, letter, three_digit, two_digit2, full_plate)
                        )
                        if self.cursor.rowcount > 0:
                            imported_count += 1
                    except sqlite3.Error as e:
                        print(f"Database error: {e}")
                        
            self.conn.commit()
            messagebox.showinfo("Success", f"Successfully imported {imported_count} plates")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to import data: {str(e)}")
            
    def search_plate(self):
        two_digit1 = self.two_digit1.get()
        letter = self.letter.get()
        three_digit = self.three_digit.get()
        two_digit2 = self.two_digit2.get()
        
        if not (two_digit1 and letter and three_digit and two_digit2):
            messagebox.showerror("Error", "Please fill all fields")
            return
            
        search_query = f"{two_digit1} {letter} {three_digit} {two_digit2}"
        
        try:
            self.cursor.execute(
                "SELECT full_plate FROM plates WHERE two_digit1=? AND letter=? AND three_digit=? AND two_digit2=?",
                (two_digit1, letter, three_digit, two_digit2)
            )
            results = self.cursor.fetchall()
            
            self.cursor.execute(
                "INSERT INTO search_history (search_query, search_date) VALUES (?, ?)",
                (search_query, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            )
            self.conn.commit()
            
            self.load_history()
            
            self.results_listbox.delete(0, tk.END)
            if results:
                for result in results:
                    self.results_listbox.insert(tk.END, result[0])
            else:
                self.results_listbox.insert(tk.END, "No matching plates found")
                
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", str(e))
            
    def load_history(self):
        self.history_listbox.delete(0, tk.END)
        try:
            self.cursor.execute("SELECT search_query, search_date FROM search_history ORDER BY search_date DESC")
            for row in self.cursor.fetchall():
                self.history_listbox.insert(tk.END, f"{row[0]} - {row[1]}")
        except sqlite3.Error as e:
            print(f"History load error: {e}")
            
    def clear_history(self):
        if messagebox.askyesno("Confirm", "Are you sure you want to clear search history?"):
            try:
                self.cursor.execute("DELETE FROM search_history")
                self.conn.commit()
                self.load_history()
                messagebox.showinfo("Success", "Search history cleared")
            except sqlite3.Error as e:
                messagebox.showerror("Error", str(e))

if __name__ == "__main__":
    root = tk.Tk()
    app = IranianPlateSearchApp(root)
    root.mainloop()
