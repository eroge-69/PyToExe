import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import sqlite3
import threading
import time
from datetime import datetime, timedelta
import os
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

DB_FILE = "meditrack_new.db"

class MediTrackApp:
    def __init__(self, root):
        self.root = root
        self.root.title("MediTrack v2")
        self.root.geometry("750x600")
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        # --- Variables ---
        self.prescription_path = tk.StringVar()
        self.running = True  # Flag to control the background thread

        # --- Database Setup ---
        self.db_conn = sqlite3.connect(DB_FILE, check_same_thread=False)
        self.setup_database()

        # --- UI Setup ---
        self.create_widgets()
        self.populate_medicines_list()

        # --- Start background thread for notifications ---
        self.reminder_thread = threading.Thread(target=self.notification_checker, daemon=True)
        self.reminder_thread.start()

    def setup_database(self):
        """Initializes the database and creates tables if they don't exist."""
        cursor = self.db_conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS medicines (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                dosage TEXT,
                timings TEXT,
                prescription_path TEXT
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS history (
                id INTEGER PRIMARY KEY,
                medicine_id INTEGER,
                status TEXT, -- 'taken' or 'missed'
                timestamp TEXT,
                FOREIGN KEY(medicine_id) REFERENCES medicines(id) ON DELETE CASCADE
            )
        ''')
        self.db_conn.commit()

    def create_widgets(self):
        """Creates the entire GUI layout."""
        style = ttk.Style(self.root)
        style.configure("TNotebook.Tab", font=('Helvetica', 12, 'bold'))

        notebook = ttk.Notebook(self.root)
        notebook.pack(expand=True, fill='both', padx=10, pady=10)

        # Tab 1: Add Medicine
        add_frame = ttk.Frame(notebook, padding=20)
        notebook.add(add_frame, text='Add Medicine')
        self.create_add_tab(add_frame)

        # Tab 2: View Medicines
        view_frame = ttk.Frame(notebook, padding=20)
        notebook.add(view_frame, text='My Medicines')
        self.create_view_tab(view_frame)

        # Tab 3: Reports
        report_frame = ttk.Frame(notebook, padding=20)
        notebook.add(report_frame, text='Weekly Report')
        self.create_report_tab(report_frame)

    def create_add_tab(self, parent):
        """Widgets for the 'Add Medicine' tab."""
        ttk.Label(parent, text="Medicine Name:", font=('Helvetica', 11)).grid(row=0, column=0, sticky="w", pady=5)
        self.med_name_entry = ttk.Entry(parent, width=40)
        self.med_name_entry.grid(row=0, column=1, pady=5)

        ttk.Label(parent, text="Dosage (e.g., 1 tablet):", font=('Helvetica', 11)).grid(row=1, column=0, sticky="w", pady=5)
        self.dosage_entry = ttk.Entry(parent, width=40)
        self.dosage_entry.grid(row=1, column=1, pady=5)

        ttk.Label(parent, text="Timings (HH:MM, HH:MM):", font=('Helvetica', 11)).grid(row=2, column=0, sticky="w", pady=5)
        self.timings_entry = ttk.Entry(parent, width=40)
        self.timings_entry.grid(row=2, column=1, pady=5)

        ttk.Button(parent, text="Upload Prescription", command=self.upload_prescription).grid(row=3, column=0, sticky="w", pady=10)
        self.prescription_label = ttk.Label(parent, text="No file selected.", foreground="gray")
        self.prescription_label.grid(row=3, column=1, sticky="w", padx=5)

        ttk.Button(parent, text="Save Medicine", command=self.add_medicine).grid(row=4, column=0, columnspan=2, pady=20)

    def create_view_tab(self, parent):
        """Widgets for the 'View Medicines' tab."""
        tree_frame = ttk.Frame(parent)
        tree_frame.pack(expand=True, fill='both')

        columns = ('name', 'dosage', 'timings')
        self.tree = ttk.Treeview(tree_frame, columns=columns, show='headings')
        self.tree.heading('name', text='Medicine')
        self.tree.heading('dosage', text='Dosage')
        self.tree.heading('timings', text='Timings')
        
        # Add a scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side="left", expand=True, fill="both")
        scrollbar.pack(side="right", fill="y")
        
        ttk.Button(parent, text="Delete Selected Medicine", command=self.delete_medicine).pack(pady=15)

    def create_report_tab(self, parent):
        """Widgets for the 'Weekly Report' tab."""
        self.report_canvas = tk.Frame(parent) # Use a simple Frame
        self.report_canvas.pack(expand=True, fill='both', pady=10)
        ttk.Button(parent, text="Generate Report", command=self.generate_report).pack(pady=10)

    # --- Backend Functions ---

    def add_medicine(self):
        name = self.med_name_entry.get().strip()
        dosage = self.dosage_entry.get().strip()
        timings = self.timings_entry.get().strip()
        path = self.prescription_path.get()

        if not name or not dosage or not timings:
            messagebox.showerror("Error", "Please fill in the name, dosage, and timings.")
            return

        cursor = self.db_conn.cursor()
        cursor.execute("INSERT INTO medicines (name, dosage, timings, prescription_path) VALUES (?, ?, ?, ?)",
                       (name, dosage, timings, path))
        self.db_conn.commit()

        messagebox.showinfo("Success", f"'{name}' added successfully.")
        self.med_name_entry.delete(0, tk.END)
        self.dosage_entry.delete(0, tk.END)
        self.timings_entry.delete(0, tk.END)
        self.prescription_label.config(text="No file selected.")
        self.prescription_path.set("")
        self.populate_medicines_list()

    def populate_medicines_list(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        cursor = self.db_conn.cursor()
        for row in cursor.execute("SELECT id, name, dosage, timings FROM medicines ORDER BY name"):
            self.tree.insert("", "end", iid=row[0], values=(row[1], row[2], row[3]))

    def delete_medicine(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("No Selection", "Please select a medicine to delete.")
            return

        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this medicine?"):
            med_id = selected_item[0]
            cursor = self.db_conn.cursor()
            cursor.execute("DELETE FROM medicines WHERE id = ?", (med_id,))
            self.db_conn.commit()
            self.populate_medicines_list()

    def upload_prescription(self):
        filepath = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf"), ("Image files", "*.png;*.jpg;*.jpeg")])
        if filepath:
            self.prescription_path.set(filepath)
            self.prescription_label.config(text=os.path.basename(filepath))

    def generate_report(self):
        for widget in self.report_canvas.winfo_children():
            widget.destroy() # Clear previous report

        cursor = self.db_conn.cursor()
        week_ago = datetime.now() - timedelta(days=7)
        cursor.execute("SELECT status, COUNT(*) FROM history WHERE timestamp >= ? GROUP BY status", (week_ago,))
        
        report_data = dict(cursor.fetchall())
        taken = report_data.get('taken', 0)
        missed = report_data.get('missed', 0)

        # Chart
        fig = Figure(figsize=(6, 4), dpi=100)
        ax = fig.add_subplot(111)
        ax.bar(['Taken', 'Missed'], [taken, missed], color=['green', 'red'])
        ax.set_title("Weekly Adherence Report")
        ax.set_ylabel("Number of Doses")
        for i, v in enumerate([taken, missed]):
            ax.text(i, v + 0.1, str(v), ha='center', fontweight='bold')
        
        canvas = FigureCanvasTkAgg(fig, master=self.report_canvas)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    def notification_checker(self):
        """Background thread to check for reminder times."""
        notified_today = set()
        
        while self.running:
            now = datetime.now()
            current_day = now.date()
            current_time = now.strftime("%H:%M")

            # Reset the notified set at the start of a new day
            if datetime.fromisoformat(f"{current_day} 00:00:00") and f"day_reset_{current_day}" not in notified_today:
                notified_today = {f"day_reset_{current_day}"}

            cursor = self.db_conn.cursor()
            medicines = cursor.execute("SELECT id, name, dosage, timings FROM medicines").fetchall()
            
            for med_id, name, dosage, timings in medicines:
                for t in timings.replace(" ", "").split(','):
                    notification_id = f"{current_day}-{med_id}-{t}"
                    if t == current_time and notification_id not in notified_today:
                        self.show_reminder_popup(med_id, name, dosage)
                        notified_today.add(notification_id)
            
            time.sleep(20) # Check every 20 seconds

    def show_reminder_popup(self, med_id, name, dosage):
        """Creates the Toplevel popup window for a notification."""
        popup = tk.Toplevel(self.root)
        popup.title("Reminder!")
        popup.geometry("400x180")
        popup.attributes("-topmost", True)
        
        msg = f"Time to take your medicine:\n\n{name} - {dosage}"
        ttk.Label(popup, text=msg, font=('Helvetica', 14), justify='center').pack(pady=20)
        
        btn_frame = ttk.Frame(popup)
        btn_frame.pack(pady=10)

        def log_action(status):
            cursor = self.db_conn.cursor()
            cursor.execute("INSERT INTO history (medicine_id, status, timestamp) VALUES (?, ?, ?)",
                           (med_id, status, datetime.now()))
            self.db_conn.commit()
            popup.destroy()

        ttk.Button(btn_frame, text="Taken 👍", command=lambda: log_action('taken')).pack(side='left', padx=15, ipady=5)
        ttk.Button(btn_frame, text="Missed 👎", command=lambda: log_action('missed')).pack(side='left', padx=15, ipady=5)

    def on_closing(self):
        """Handle window closing."""
        if messagebox.askokcancel("Quit", "Do you want to exit MediTrack?"):
            self.running = False  # Signal the thread to stop
            self.db_conn.close()   # Close the database connection
            self.root.destroy()

if __name__ == "__main__":
    app_root = tk.Tk()
    app = MediTrackApp(app_root)
    app_root.mainloop()