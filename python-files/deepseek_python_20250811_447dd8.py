import sqlite3
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox
import os

class DowntimeTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("Machine Downtime Tracker")
        self.root.geometry("600x400")
        
        # Initialize database
        self.db_file = "downtime.db"
        self.init_db()
        
        # Create GUI elements
        self.create_widgets()
        
        # Load existing records
        self.load_records()

    def init_db(self):
        if not os.path.exists(self.db_file):
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS downtime_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    machine_name TEXT NOT NULL,
                    start_time TEXT NOT NULL,
                    end_time TEXT,
                    reason TEXT,
                    resolved BOOLEAN DEFAULT 0
                )
            ''')
            conn.commit()
            conn.close()

    def create_widgets(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Input frame
        input_frame = ttk.LabelFrame(main_frame, text="Record Downtime", padding="10")
        input_frame.pack(fill=tk.X, pady=5)
        
        # Machine name
        ttk.Label(input_frame, text="Machine Name:").grid(row=0, column=0, sticky=tk.W)
        self.machine_name = ttk.Entry(input_frame, width=30)
        self.machine_name.grid(row=0, column=1, padx=5, pady=5)
        
        # Reason
        ttk.Label(input_frame, text="Reason:").grid(row=1, column=0, sticky=tk.W)
        self.reason = ttk.Entry(input_frame, width=30)
        self.reason.grid(row=1, column=1, padx=5, pady=5)
        
        # Buttons
        button_frame = ttk.Frame(input_frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=10)
        
        ttk.Button(button_frame, text="Start Downtime", command=self.start_downtime).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="End Downtime", command=self.end_downtime).pack(side=tk.LEFT, padx=5)
        
        # Records frame
        records_frame = ttk.LabelFrame(main_frame, text="Downtime Records", padding="10")
        records_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Treeview
        self.tree = ttk.Treeview(records_frame, columns=("ID", "Machine", "Start", "End", "Reason", "Status"), show="headings")
        
        self.tree.heading("ID", text="ID")
        self.tree.heading("Machine", text="Machine")
        self.tree.heading("Start", text="Start Time")
        self.tree.heading("End", text="End Time")
        self.tree.heading("Reason", text="Reason")
        self.tree.heading("Status", text="Status")
        
        self.tree.column("ID", width=40)
        self.tree.column("Machine", width=80)
        self.tree.column("Start", width=120)
        self.tree.column("End", width=120)
        self.tree.column("Reason", width=150)
        self.tree.column("Status", width=80)
        
        self.tree.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(records_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Right-click menu
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="Mark as Resolved", command=self.mark_resolved)
        self.context_menu.add_command(label="Delete Record", command=self.delete_record)
        
        self.tree.bind("<Button-3>", self.show_context_menu)

    def show_context_menu(self, event):
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)

    def mark_resolved(self):
        selected_item = self.tree.selection()
        if selected_item:
            record_id = self.tree.item(selected_item)['values'][0]
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            cursor.execute("UPDATE downtime_records SET resolved=1 WHERE id=?", (record_id,))
            conn.commit()
            conn.close()
            self.load_records()

    def delete_record(self):
        selected_item = self.tree.selection()
        if selected_item:
            if messagebox.askyesno("Confirm", "Delete this record?"):
                record_id = self.tree.item(selected_item)['values'][0]
                conn = sqlite3.connect(self.db_file)
                cursor = conn.cursor()
                cursor.execute("DELETE FROM downtime_records WHERE id=?", (record_id,))
                conn.commit()
                conn.close()
                self.load_records()

    def start_downtime(self):
        machine = self.machine_name.get()
        reason_text = self.reason.get()
        
        if not machine:
            messagebox.showerror("Error", "Please enter a machine name")
            return
            
        start_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO downtime_records (machine_name, start_time, reason) VALUES (?, ?, ?)",
            (machine, start_time, reason_text)
        )
        conn.commit()
        conn.close()
        
        self.machine_name.delete(0, tk.END)
        self.reason.delete(0, tk.END)
        self.load_records()
        messagebox.showinfo("Success", f"Downtime started for {machine} at {start_time}")

    def end_downtime(self):
        machine = self.machine_name.get()
        if not machine:
            messagebox.showerror("Error", "Please enter a machine name")
            return
            
        end_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        # Find the most recent unresolved downtime for this machine
        cursor.execute(
            "SELECT id FROM downtime_records WHERE machine_name=? AND resolved=0 ORDER BY start_time DESC LIMIT 1",
            (machine,)
        )
        result = cursor.fetchone()
        
        if result:
            record_id = result[0]
            cursor.execute(
                "UPDATE downtime_records SET end_time=?, resolved=1 WHERE id=?",
                (end_time, record_id)
            )
            conn.commit()
            conn.close()
            self.load_records()
            messagebox.showinfo("Success", f"Downtime ended for {machine} at {end_time}")
        else:
            conn.close()
            messagebox.showerror("Error", f"No active downtime found for {machine}")

    def load_records(self):
        # Clear existing records
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        # Load from database
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute("SELECT id, machine_name, start_time, end_time, reason, resolved FROM downtime_records ORDER BY start_time DESC")
        
        for row in cursor.fetchall():
            status = "Resolved" if row[5] else "Ongoing"
            end_time = row[3] if row[3] else "N/A"
            self.tree.insert("", tk.END, values=(row[0], row[1], row[2], end_time, row[4], status))
        
        conn.close()

def main():
    root = tk.Tk()
    app = DowntimeTracker(root)
    root.mainloop()

if __name__ == "__main__":
    main()