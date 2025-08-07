
#!/usr/bin/env python3
"""
ANARES ANALYTICS LLP
Compliance Calendar Management System
Version 1.0
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
from datetime import datetime, date, timedelta
import json
import os
import threading
import time
from tkinter import font
import webbrowser

class ComplianceCalendar:
    def __init__(self, root):
        self.root = root
        self.root.title("ANARES ANALYTICS LLP - Compliance Calendar")
        self.root.geometry("1200x800")
        self.root.configure(bg="#f0f0f0")

        # Initialize database
        self.init_database()

        # Create main interface
        self.create_widgets()

        # Load existing data
        self.refresh_compliance_list()

        # Start notification checker
        self.start_notification_service()

    def init_database(self):
        """Initialize SQLite database for compliance tracking"""
        self.db_path = "compliance_calendar.db"
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()

        # Create compliance table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS compliance_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                due_date DATE NOT NULL,
                category TEXT,
                priority TEXT,
                status TEXT DEFAULT 'Pending',
                assigned_to TEXT,
                created_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                completed_date DATETIME,
                notes TEXT
            )
        """)

        # Create notifications table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS notifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                compliance_id INTEGER,
                notification_date DATETIME,
                message TEXT,
                is_sent BOOLEAN DEFAULT FALSE,
                FOREIGN KEY (compliance_id) REFERENCES compliance_items (id)
            )
        """)

        self.conn.commit()

    def create_widgets(self):
        """Create main GUI widgets"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)

        # Title
        title_label = ttk.Label(main_frame, text="Compliance Calendar Management", 
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))

        # Left panel - Add/Edit compliance items
        left_frame = ttk.LabelFrame(main_frame, text="Add New Compliance Item", padding="10")
        left_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))

        # Input fields
        ttk.Label(left_frame, text="Title:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.title_var = tk.StringVar()
        self.title_entry = ttk.Entry(left_frame, textvariable=self.title_var, width=30)
        self.title_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=2)

        ttk.Label(left_frame, text="Description:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.desc_text = tk.Text(left_frame, height=3, width=30)
        self.desc_text.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=2)

        ttk.Label(left_frame, text="Due Date:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.due_date_var = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        self.due_date_entry = ttk.Entry(left_frame, textvariable=self.due_date_var, width=30)
        self.due_date_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=2)

        ttk.Label(left_frame, text="Category:").grid(row=3, column=0, sticky=tk.W, pady=2)
        self.category_var = tk.StringVar()
        self.category_combo = ttk.Combobox(left_frame, textvariable=self.category_var, width=27)
        self.category_combo['values'] = ('Legal', 'Financial', 'Environmental', 'Safety', 'HR', 'IT Security', 'Other')
        self.category_combo.grid(row=3, column=1, sticky=(tk.W, tk.E), pady=2)

        ttk.Label(left_frame, text="Priority:").grid(row=4, column=0, sticky=tk.W, pady=2)
        self.priority_var = tk.StringVar(value="Medium")
        self.priority_combo = ttk.Combobox(left_frame, textvariable=self.priority_var, width=27)
        self.priority_combo['values'] = ('Low', 'Medium', 'High', 'Critical')
        self.priority_combo.grid(row=4, column=1, sticky=(tk.W, tk.E), pady=2)

        ttk.Label(left_frame, text="Assigned To:").grid(row=5, column=0, sticky=tk.W, pady=2)
        self.assigned_var = tk.StringVar()
        self.assigned_entry = ttk.Entry(left_frame, textvariable=self.assigned_var, width=30)
        self.assigned_entry.grid(row=5, column=1, sticky=(tk.W, tk.E), pady=2)

        # Buttons
        button_frame = ttk.Frame(left_frame)
        button_frame.grid(row=6, column=0, columnspan=2, pady=10)

        self.add_button = ttk.Button(button_frame, text="Add Item", command=self.add_compliance_item)
        self.add_button.pack(side=tk.LEFT, padx=5)

        self.update_button = ttk.Button(button_frame, text="Update", command=self.update_compliance_item, state='disabled')
        self.update_button.pack(side=tk.LEFT, padx=5)

        self.clear_button = ttk.Button(button_frame, text="Clear", command=self.clear_form)
        self.clear_button.pack(side=tk.LEFT, padx=5)

        # Right panel - Compliance list and management
        right_frame = ttk.LabelFrame(main_frame, text="Compliance Items", padding="10")
        right_frame.grid(row=1, column=1, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        right_frame.columnconfigure(0, weight=1)
        right_frame.rowconfigure(1, weight=1)

        # Filter frame
        filter_frame = ttk.Frame(right_frame)
        filter_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))

        ttk.Label(filter_frame, text="Filter by Status:").pack(side=tk.LEFT, padx=5)
        self.filter_var = tk.StringVar(value="All")
        self.filter_combo = ttk.Combobox(filter_frame, textvariable=self.filter_var, width=15)
        self.filter_combo['values'] = ('All', 'Pending', 'In Progress', 'Completed', 'Overdue')
        self.filter_combo.pack(side=tk.LEFT, padx=5)
        self.filter_combo.bind('<<ComboboxSelected>>', self.filter_compliance_list)

        # Treeview for compliance items
        self.tree = ttk.Treeview(right_frame, columns=('Title', 'Due Date', 'Category', 'Priority', 'Status', 'Assigned'), show='headings')

        # Define headings
        self.tree.heading('Title', text='Title')
        self.tree.heading('Due Date', text='Due Date')
        self.tree.heading('Category', text='Category')
        self.tree.heading('Priority', text='Priority')
        self.tree.heading('Status', text='Status')
        self.tree.heading('Assigned', text='Assigned To')

        # Define column widths
        self.tree.column('Title', width=200)
        self.tree.column('Due Date', width=100)
        self.tree.column('Category', width=100)
        self.tree.column('Priority', width=80)
        self.tree.column('Status', width=100)
        self.tree.column('Assigned', width=120)

        # Scrollbar for treeview
        scrollbar = ttk.Scrollbar(right_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=1, column=1, sticky=(tk.N, tk.S))

        # Bind double-click event
        self.tree.bind('<Double-1>', self.on_item_select)

        # Action buttons
        action_frame = ttk.Frame(right_frame)
        action_frame.grid(row=2, column=0, pady=10)

        ttk.Button(action_frame, text="Edit", command=self.edit_compliance_item).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="Complete", command=self.mark_complete).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="Delete", command=self.delete_compliance_item).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="Export", command=self.export_data).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="Import", command=self.import_data).pack(side=tk.LEFT, padx=5)

        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))

        # Configure left frame grid weights
        left_frame.columnconfigure(1, weight=1)

    def add_compliance_item(self):
        """Add new compliance item to database"""
        title = self.title_var.get().strip()
        description = self.desc_text.get("1.0", tk.END).strip()
        due_date = self.due_date_var.get().strip()
        category = self.category_var.get().strip()
        priority = self.priority_var.get().strip()
        assigned_to = self.assigned_var.get().strip()

        if not title or not due_date:
            messagebox.showerror("Error", "Title and Due Date are required!")
            return

        try:
            # Validate date format
            datetime.strptime(due_date, "%Y-%m-%d")

            self.cursor.execute("""
                INSERT INTO compliance_items (title, description, due_date, category, priority, assigned_to)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (title, description, due_date, category, priority, assigned_to))

            self.conn.commit()
            self.refresh_compliance_list()
            self.clear_form()
            self.status_var.set(f"Added: {title}")

        except ValueError:
            messagebox.showerror("Error", "Invalid date format! Use YYYY-MM-DD")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add item: {str(e)}")

    def update_compliance_item(self):
        """Update selected compliance item"""
        if not hasattr(self, 'selected_id'):
            messagebox.showerror("Error", "No item selected!")
            return

        title = self.title_var.get().strip()
        description = self.desc_text.get("1.0", tk.END).strip()
        due_date = self.due_date_var.get().strip()
        category = self.category_var.get().strip()
        priority = self.priority_var.get().strip()
        assigned_to = self.assigned_var.get().strip()

        if not title or not due_date:
            messagebox.showerror("Error", "Title and Due Date are required!")
            return

        try:
            # Validate date format
            datetime.strptime(due_date, "%Y-%m-%d")

            self.cursor.execute("""
                UPDATE compliance_items 
                SET title=?, description=?, due_date=?, category=?, priority=?, assigned_to=?
                WHERE id=?
            """, (title, description, due_date, category, priority, assigned_to, self.selected_id))

            self.conn.commit()
            self.refresh_compliance_list()
            self.clear_form()
            self.status_var.set(f"Updated: {title}")

        except ValueError:
            messagebox.showerror("Error", "Invalid date format! Use YYYY-MM-DD")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update item: {str(e)}")

    def clear_form(self):
        """Clear all form fields"""
        self.title_var.set("")
        self.desc_text.delete("1.0", tk.END)
        self.due_date_var.set(datetime.now().strftime("%Y-%m-%d"))
        self.category_var.set("")
        self.priority_var.set("Medium")
        self.assigned_var.set("")

        self.add_button.config(state='normal')
        self.update_button.config(state='disabled')
        if hasattr(self, 'selected_id'):
            delattr(self, 'selected_id')

    def on_item_select(self, event):
        """Handle item selection in treeview"""
        self.edit_compliance_item()

    def edit_compliance_item(self):
        """Edit selected compliance item"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select an item to edit!")
            return

        item = self.tree.item(selection[0])
        item_id = item['tags'][0] if item['tags'] else None

        if not item_id:
            return

        # Fetch full item details from database
        self.cursor.execute("SELECT * FROM compliance_items WHERE id=?", (item_id,))
        row = self.cursor.fetchone()

        if row:
            self.selected_id = row[0]
            self.title_var.set(row[1])
            self.desc_text.delete("1.0", tk.END)
            self.desc_text.insert("1.0", row[2] or "")
            self.due_date_var.set(row[3])
            self.category_var.set(row[4] or "")
            self.priority_var.set(row[5] or "Medium")
            self.assigned_var.set(row[7] or "")

            self.add_button.config(state='disabled')
            self.update_button.config(state='normal')

    def mark_complete(self):
        """Mark selected item as complete"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select an item to mark as complete!")
            return

        item = self.tree.item(selection[0])
        item_id = item['tags'][0] if item['tags'] else None

        if item_id:
            self.cursor.execute("""
                UPDATE compliance_items 
                SET status='Completed', completed_date=CURRENT_TIMESTAMP 
                WHERE id=?
            """, (item_id,))
            self.conn.commit()
            self.refresh_compliance_list()
            self.status_var.set("Item marked as completed")

    def delete_compliance_item(self):
        """Delete selected compliance item"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select an item to delete!")
            return

        if messagebox.askyesno("Confirm", "Are you sure you want to delete this item?"):
            item = self.tree.item(selection[0])
            item_id = item['tags'][0] if item['tags'] else None

            if item_id:
                self.cursor.execute("DELETE FROM compliance_items WHERE id=?", (item_id,))
                self.conn.commit()
                self.refresh_compliance_list()
                self.status_var.set("Item deleted")

    def refresh_compliance_list(self):
        """Refresh the compliance items list"""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Get filter value
        filter_status = self.filter_var.get()

        # Build query based on filter
        if filter_status == "All":
            query = "SELECT * FROM compliance_items ORDER BY due_date ASC"
            params = ()
        elif filter_status == "Overdue":
            query = "SELECT * FROM compliance_items WHERE due_date < date('now') AND status != 'Completed' ORDER BY due_date ASC"
            params = ()
        else:
            query = "SELECT * FROM compliance_items WHERE status=? ORDER BY due_date ASC"
            params = (filter_status,)

        self.cursor.execute(query, params)
        rows = self.cursor.fetchall()

        # Add items to treeview
        for row in rows:
            item_id, title, description, due_date, category, priority, status, assigned_to = row[:8]

            # Check if overdue
            if status != 'Completed' and datetime.strptime(due_date, "%Y-%m-%d").date() < date.today():
                status = "Overdue"

            # Color coding based on priority and status
            tags = [str(item_id)]
            if status == "Overdue":
                tags.append("overdue")
            elif priority == "Critical":
                tags.append("critical")
            elif priority == "High":
                tags.append("high")

            self.tree.insert('', tk.END, values=(title, due_date, category or '', priority or '', status, assigned_to or ''), tags=tags)

        # Configure tag colors
        self.tree.tag_configure("overdue", background="#ffcccc")
        self.tree.tag_configure("critical", background="#ff9999")
        self.tree.tag_configure("high", background="#ffddaa")

        # Update status
        total_items = len(rows)
        overdue_count = len([r for r in rows if r[6] != 'Completed' and datetime.strptime(r[3], "%Y-%m-%d").date() < date.today()])
        self.status_var.set(f"Total items: {total_items} | Overdue: {overdue_count}")

    def filter_compliance_list(self, event=None):
        """Filter compliance list based on status"""
        self.refresh_compliance_list()

    def export_data(self):
        """Export compliance data to JSON file"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )

        if filename:
            try:
                self.cursor.execute("SELECT * FROM compliance_items")
                rows = self.cursor.fetchall()

                data = []
                for row in rows:
                    data.append({
                        'id': row[0],
                        'title': row[1],
                        'description': row[2],
                        'due_date': row[3],
                        'category': row[4],
                        'priority': row[5],
                        'status': row[6],
                        'assigned_to': row[7],
                        'created_date': row[8],
                        'completed_date': row[9],
                        'notes': row[10]
                    })

                with open(filename, 'w') as f:
                    json.dump(data, f, indent=2, default=str)

                messagebox.showinfo("Success", f"Data exported to {filename}")

            except Exception as e:
                messagebox.showerror("Error", f"Failed to export data: {str(e)}")

    def import_data(self):
        """Import compliance data from JSON file"""
        filename = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )

        if filename:
            try:
                with open(filename, 'r') as f:
                    data = json.load(f)

                imported_count = 0
                for item in data:
                    # Check if item already exists
                    self.cursor.execute("SELECT id FROM compliance_items WHERE title=? AND due_date=?", 
                                      (item['title'], item['due_date']))
                    if not self.cursor.fetchone():
                        self.cursor.execute("""
                            INSERT INTO compliance_items (title, description, due_date, category, priority, assigned_to, status)
                            VALUES (?, ?, ?, ?, ?, ?, ?)
                        """, (item['title'], item.get('description', ''), item['due_date'], 
                             item.get('category', ''), item.get('priority', 'Medium'), 
                             item.get('assigned_to', ''), item.get('status', 'Pending')))
                        imported_count += 1

                self.conn.commit()
                self.refresh_compliance_list()
                messagebox.showinfo("Success", f"Imported {imported_count} items")

            except Exception as e:
                messagebox.showerror("Error", f"Failed to import data: {str(e)}")

    def start_notification_service(self):
        """Start background notification service"""
        def check_notifications():
            while True:
                try:
                    # Check for items due within 7 days
                    self.cursor.execute("""
                        SELECT title, due_date, assigned_to FROM compliance_items 
                        WHERE due_date BETWEEN date('now') AND date('now', '+7 days') 
                        AND status != 'Completed'
                    """)
                    upcoming = self.cursor.fetchall()

                    # Check for overdue items
                    self.cursor.execute("""
                        SELECT title, due_date, assigned_to FROM compliance_items 
                        WHERE due_date < date('now') AND status != 'Completed'
                    """)
                    overdue = self.cursor.fetchall()

                    if upcoming or overdue:
                        notification_text = ""
                        if overdue:
                            notification_text += f"OVERDUE ITEMS: {len(overdue)}\n"
                        if upcoming:
                            notification_text += f"DUE WITHIN 7 DAYS: {len(upcoming)}"

                        # Update status bar with notification
                        self.root.after(0, lambda: self.status_var.set(f"⚠️ {notification_text}"))

                except Exception as e:
                    print(f"Notification service error: {e}")

                time.sleep(3600)  # Check every hour

        notification_thread = threading.Thread(target=check_notifications, daemon=True)
        notification_thread.start()

    def __del__(self):
        """Cleanup database connection"""
        if hasattr(self, 'conn'):
            self.conn.close()

def main():
    """Main function to run the application"""
    root = tk.Tk()

    # Set application icon (if available)
    try:
        # You can add an icon file here
        # root.iconbitmap('app_icon.ico')
        pass
    except:
        pass

    app = ComplianceCalendar(root)

    # Handle window close event
    def on_closing():
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_closing)

    # Center window on screen
    root.update_idletasks()
    x = (root.winfo_screenwidth() // 2) - (1200 // 2)
    y = (root.winfo_screenheight() // 2) - (800 // 2)
    root.geometry(f"1200x800+{x}+{y}")

    root.mainloop()

if __name__ == "__main__":
    main()
