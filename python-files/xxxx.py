import tkinter as tk
from tkinter import ttk
import sqlite3

class TimetableApp:
    def __init__(self, root):
        self.root = root
        self.root.title("School Timetable")
        self.root.geometry("1000x600")
        self.root.configure(bg="#f0f4f8")  # Light gray background

        # Initialize SQLite database
        self.conn = sqlite3.connect("timetable.db")
        self.create_table()

        # Create main container frame
        self.container = ttk.Frame(root, padding="10", style="Container.TFrame")
        self.container.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Create timetable frame
        self.frame = ttk.Frame(self.container, padding="10", style="Timetable.TFrame")
        self.frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Days of the week
        self.days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        self.entries = {}

        # Configure styles
        self.style = ttk.Style()
        self.style.configure("Container.TFrame", background="#f0f4f8")
        self.style.configure("Timetable.TFrame", background="#ffffff")
        self.style.configure("Day.TLabel", background="#4a90e2", foreground="#ffffff", font=("Arial", 10, "bold"))
        self.style.configure("Bell.TLabel", background="#50c878", foreground="#ffffff", font=("Arial", 10, "bold"))
        self.style.configure("Button.TButton", font=("Arial", 10), padding=5)
        self.style.map("Button.TButton", background=[("active", "#45b7d1")], foreground=[("active", "#ffffff")])

        # First row: Bell numbers
        ttk.Label(self.frame, text="Day", style="Day.TLabel").grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        for bell in range(1, 9):
            ttk.Label(self.frame, text=f"Bell {bell}", style="Bell.TLabel").grid(row=0, column=bell, padx=5, pady=5, sticky="nsew")

        # First column: Days and timetable entries
        colors = ["#e6f3ff", "#f0fff0", "#fff0f5", "#f5f0ff", "#fff5e6", "#e6fff5", "#ffe6f0"]  # Pastel colors for rows
        for i, day in enumerate(self.days, start=1):
            ttk.Label(self.frame, text=day, style="Day.TLabel").grid(row=i, column=0, padx=5, pady=5, sticky="nsew")
            for bell in range(1, 9):
                entry = ttk.Entry(self.frame, width=15)
                entry.grid(row=i, column=bell, padx=5, pady=5, sticky="nsew")
                entry.insert(0, "")
                entry.configure(background=colors[i-1])  # Apply row color
                self.entries[(day, bell)] = entry

        # Notes label and Text widget (below timetable)
        self.notes_label = ttk.Label(self.container, text="Notes", style="Bell.TLabel")
        self.notes_label.grid(row=1, column=0, padx=10, pady=5, sticky="n")
        self.notes_text = tk.Text(self.container, width=80, height=10, font=("Arial", 10), bg="#f0f0f0", fg="#333333", bd=2, relief="groove")
        self.notes_text.grid(row=2, column=0, padx=10, pady=5, sticky="nsew")

        # Buttons for saving and loading
        button_frame = ttk.Frame(self.container, padding="10")
        button_frame.grid(row=3, column=0, sticky=(tk.W, tk.E))
        ttk.Button(button_frame, text="Save Timetable", command=self.save_timetable, style="Button.TButton").grid(row=0, column=0, padx=5, pady=5)
        ttk.Button(button_frame, text="Load Timetable", command=self.load_timetable, style="Button.TButton").grid(row=0, column=1, padx=5, pady=5)

        # Configure grid weights to make it responsive
        self.container.grid_columnconfigure(0, weight=1)
        self.container.grid_rowconfigure(0, weight=3)
        self.container.grid_rowconfigure(2, weight=1)
        for i in range(8):
            self.frame.grid_columnconfigure(i + 1, weight=1)
        for i in range(7):
            self.frame.grid_rowconfigure(i + 1, weight=1)

        # Load existing timetable on startup
        self.load_timetable()

    def create_table(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS timetable (
                day TEXT,
                bell INTEGER,
                subject TEXT,
                PRIMARY KEY (day, bell)
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY,
                content TEXT
            )
        ''')
        self.conn.commit()

    def save_timetable(self):
        cursor = self.conn.cursor()
        # Clear existing timetable data
        cursor.execute("DELETE FROM timetable")
        # Save timetable
        for day in self.days:
            for bell in range(1, 9):
                subject = self.entries[(day, bell)].get()
                cursor.execute('''
                    INSERT OR REPLACE INTO timetable (day, bell, subject)
                    VALUES (?, ?, ?)
                ''', (day, bell, subject))
        # Save notes
        cursor.execute("DELETE FROM notes")
        notes_content = self.notes_text.get("1.0", tk.END).strip()
        cursor.execute("INSERT INTO notes (id, content) VALUES (?, ?)", (1, notes_content))
        self.conn.commit()

    def load_timetable(self):
        cursor = self.conn.cursor()
        # Load timetable
        cursor.execute("SELECT day, bell, subject FROM timetable")
        rows = cursor.fetchall()
        for entry in self.entries.values():
            entry.delete(0, tk.END)
        for day, bell, subject in rows:
            if (day, bell) in self.entries and subject:
                self.entries[(day, bell)].insert(0, subject)
        # Load notes
        self.notes_text.delete("1.0", tk.END)
        cursor.execute("SELECT content FROM notes WHERE id = 1")
        result = cursor.fetchone()
        if result and result[0]:
            self.notes_text.insert("1.0", result[0])

    def __del__(self):
        self.conn.close()

def create_timetable():
    root = tk.Tk()
    app = TimetableApp(root)
    root.mainloop()

if __name__ == "__main__":
    create_timetable()