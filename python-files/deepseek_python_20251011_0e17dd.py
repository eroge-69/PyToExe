import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import sqlite3
import json
from datetime import datetime, timedelta
import threading
import time
import os
import sys
import subprocess
from plyer import notification
import platform

class Database:
    def __init__(self):
        self.db_path = "wastenot.db"
        self.init_database()
        self.load_default_items()
        self.load_custom_items()
    
    def init_database(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                category TEXT,
                added_date TEXT NOT NULL,
                expiry_date TEXT NOT NULL,
                notified INTEGER DEFAULT 0,
                is_custom INTEGER DEFAULT 0,
                custom_expiry_days INTEGER
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS custom_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                category TEXT,
                default_expiry_days INTEGER NOT NULL,
                expiry_unit TEXT DEFAULT 'days'
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS scheduled_notifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                item_id INTEGER,
                notification_time TEXT NOT NULL,
                message TEXT NOT NULL,
                scheduled INTEGER DEFAULT 0,
                FOREIGN KEY (item_id) REFERENCES items (id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def load_default_items(self):
        self.default_items = {
            "milk": {"category": "dairy", "default_expiry": 7, "expiry_unit": "days"},
            "butter": {"category": "dairy", "default_expiry": 30, "expiry_unit": "days"},
            "tea": {"category": "beverage", "default_expiry": 180, "expiry_unit": "days"},
            "coffee": {"category": "beverage", "default_expiry": 365, "expiry_unit": "days"},
            "yogurt": {"category": "dairy", "default_expiry": 14, "expiry_unit": "days"},
            "egg": {"category": "dairy", "default_expiry": 28, "expiry_unit": "days"},
            "bread": {"category": "bakery", "default_expiry": 7, "expiry_unit": "days"},
            "cheese": {"category": "dairy", "default_expiry": 21, "expiry_unit": "days"},
            "chicken": {"category": "meat", "default_expiry": 3, "expiry_unit": "days"},
            "beef": {"category": "meat", "default_expiry": 5, "expiry_unit": "days"},
            "fish": {"category": "seafood", "default_expiry": 2, "expiry_unit": "days"},
            "apple": {"category": "fruit", "default_expiry": 21, "expiry_unit": "days"},
            "banana": {"category": "fruit", "default_expiry": 5, "expiry_unit": "days"},
            "carrot": {"category": "vegetable", "default_expiry": 14, "expiry_unit": "days"},
            "lettuce": {"category": "vegetable", "default_expiry": 7, "expiry_unit": "days"}
        }
    
    def load_custom_items(self):
        """Load custom items from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT name, category, default_expiry_days, expiry_unit FROM custom_items')
        custom_items = cursor.fetchall()
        
        self.custom_items = {}
        for name, category, expiry_days, expiry_unit in custom_items:
            self.custom_items[name.lower()] = {
                "category": category,
                "default_expiry": expiry_days,
                "expiry_unit": expiry_unit,
                "is_custom": True
            }
        
        conn.close()
    
    def add_custom_item(self, name, category, expiry_days, expiry_unit="days"):
        """Add a new custom item to the database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO custom_items (name, category, default_expiry_days, expiry_unit)
                VALUES (?, ?, ?, ?)
            ''', (name, category, expiry_days, expiry_unit))
            
            conn.commit()
            
            # Update in-memory custom items
            self.custom_items[name.lower()] = {
                "category": category,
                "default_expiry": expiry_days,
                "expiry_unit": expiry_unit,
                "is_custom": True
            }
            
            conn.close()
            return True
            
        except sqlite3.IntegrityError:
            conn.close()
            return False  # Item already exists
    
    def get_all_items_list(self):
        """Get combined list of default and custom items"""
        all_items = list(self.default_items.keys()) + list(self.custom_items.keys())
        return sorted(all_items)
    
    def get_item_info(self, item_name):
        """Get item information from either default or custom items"""
        item_name_lower = item_name.lower()
        
        if item_name_lower in self.default_items:
            return self.default_items[item_name_lower]
        elif item_name_lower in self.custom_items:
            return self.custom_items[item_name_lower]
        else:
            return None
    
    def add_item(self, name, expiry_option, custom_expiry_days=None):
        item_info = self.get_item_info(name)
        if not item_info:
            return False
        
        added_date = datetime.now()
        
        # Handle expiry date calculation
        if expiry_option == "today":
            expiry_date = added_date
        elif expiry_option == "tomorrow":
            expiry_date = added_date + timedelta(days=1)
        elif expiry_option == "3 days":
            expiry_date = added_date + timedelta(days=3)
        elif expiry_option == "5 days":
            expiry_date = added_date + timedelta(days=5)
        elif expiry_option == "1 week":
            expiry_date = added_date + timedelta(days=7)
        elif expiry_option == "2 weeks":
            expiry_date = added_date + timedelta(days=14)
        elif expiry_option == "3 weeks":
            expiry_date = added_date + timedelta(days=21)
        elif expiry_option == "1 month":
            expiry_date = added_date + timedelta(days=30)
        elif expiry_option == "custom" and custom_expiry_days:
            expiry_date = added_date + timedelta(days=custom_expiry_days)
        else:
            # Use default expiry from item info
            expiry_date = added_date + timedelta(days=item_info["default_expiry"])
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        is_custom = name.lower() in self.custom_items
        
        cursor.execute('''
            INSERT INTO items (name, category, added_date, expiry_date, is_custom, custom_expiry_days)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (name, item_info["category"], added_date.isoformat(), 
              expiry_date.date().isoformat(), is_custom, custom_expiry_days))
        
        item_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        # Schedule notifications for this new item
        self.schedule_notifications_for_item(item_id, name, expiry_date.date())
        
        return item_id
    
    def get_all_items(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM items ORDER BY expiry_date ASC')
        items = cursor.fetchall()
        conn.close()
        return items
    
    def delete_item(self, item_id):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM items WHERE id = ?', (item_id,))
        cursor.execute('DELETE FROM scheduled_notifications WHERE item_id = ?', (item_id,))
        
        conn.commit()
        conn.close()
        
        # Remove from system scheduler
        self.unschedule_item_notifications(item_id)
    
    def get_custom_items(self):
        """Get list of custom items for management"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM custom_items ORDER BY name')
        items = cursor.fetchall()
        conn.close()
        return items
    
    def delete_custom_item(self, item_name):
        """Delete a custom item definition"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM custom_items WHERE name = ?', (item_name,))
        
        conn.commit()
        conn.close()
        
        # Remove from in-memory cache
        if item_name.lower() in self.custom_items:
            del self.custom_items[item_name.lower()]
    
    def get_expiring_items(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        today = datetime.now().date().isoformat()
        cursor.execute('SELECT * FROM items WHERE expiry_date >= ? ORDER BY expiry_date ASC', (today,))
        items = cursor.fetchall()
        conn.close()
        return items
    
    def schedule_notifications_for_item(self, item_id, name, expiry_date):
        """Schedule all notifications for an item using system scheduler"""
        today = datetime.now().date()
        days_until_expiry = (expiry_date - today).days
        
        notifications = []
        
        if days_until_expiry == 0:
            notify_time = datetime.combine(expiry_date, datetime.min.time()) + timedelta(hours=9)
            notifications.append((notify_time, f"Your {name} expires today! Use it now."))
        
        elif days_until_expiry == 1:
            notify_time1 = datetime.combine(expiry_date - timedelta(days=1), datetime.min.time()) + timedelta(hours=9)
            notify_time2 = datetime.combine(expiry_date, datetime.min.time()) + timedelta(hours=9)
            notifications.append((notify_time1, f"Your {name} expires tomorrow!"))
            notifications.append((notify_time2, f"Your {name} expires today! Use it now."))
        
        elif days_until_expiry <= 3:
            notify_time1 = datetime.combine(expiry_date - timedelta(days=1), datetime.min.time()) + timedelta(hours=9)
            notify_time2 = datetime.combine(expiry_date, datetime.min.time()) + timedelta(hours=9)
            notifications.append((notify_time1, f"Your {name} expires in 1 day!"))
            notifications.append((notify_time2, f"Your {name} expires today! Use it now."))
        
        elif days_until_expiry <= 7:
            notify_time1 = datetime.combine(expiry_date - timedelta(days=2), datetime.min.time()) + timedelta(hours=9)
            notify_time2 = datetime.combine(expiry_date - timedelta(days=1), datetime.min.time()) + timedelta(hours=9)
            notifications.append((notify_time1, f"Your {name} will expire in 2 days."))
            notifications.append((notify_time2, f"Your {name} expires tomorrow!"))
        
        else:
            notify_time1 = datetime.combine(expiry_date - timedelta(days=7), datetime.min.time()) + timedelta(hours=9)
            notify_time2 = datetime.combine(expiry_date - timedelta(days=3), datetime.min.time()) + timedelta(hours=9)
            notify_time3 = datetime.combine(expiry_date - timedelta(days=1), datetime.min.time()) + timedelta(hours=9)
            notifications.append((notify_time1, f"Your {name} will expire in 1 week."))
            notifications.append((notify_time2, f"Your {name} will expire in 3 days."))
            notifications.append((notify_time3, f"Your {name} expires tomorrow!"))
        
        # Store in database and schedule with system
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for notify_time, message in notifications:
            if notify_time > datetime.now():
                cursor.execute('''
                    INSERT INTO scheduled_notifications (item_id, notification_time, message)
                    VALUES (?, ?, ?)
                ''', (item_id, notify_time.isoformat(), message))
                
                # Schedule with system
                self.schedule_system_notification(notify_time, message, f"wastenot_{item_id}_{int(notify_time.timestamp())}")
        
        conn.commit()
        conn.close()
    
    def schedule_system_notification(self, notify_time, message, job_id):
        """Schedule notification using system scheduler"""
        system = platform.system()
        script_path = os.path.abspath(__file__)
        
        # Create a separate notification script
        notification_script = self.create_notification_script()
        
        if system == "Windows":
            self.schedule_windows(notify_time, message, job_id, notification_script)
        elif system == "Darwin":  # macOS
            self.schedule_macos(notify_time, message, job_id, notification_script)
        else:  # Linux
            self.schedule_linux(notify_time, message, job_id, notification_script)
    
    def create_notification_script(self):
        """Create a standalone notification script"""
        script_content = '''
import os
import sys
from plyer import notification
import argparse

def show_notification(title, message):
    try:
        notification.notify(
            title=title,
            message=message,
            app_name="WasteNot",
            timeout=10
        )
    except Exception as e:
        print(f"Notification failed: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--title", required=True)
    parser.add_argument("--message", required=True)
    args = parser.parse_args()
    
    show_notification(args.title, args.message)
'''
        script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "wastenot_notify.py")
        with open(script_path, 'w') as f:
            f.write(script_content)
        return script_path
    
    def schedule_windows(self, notify_time, message, job_id, script_path):
        """Schedule on Windows using Task Scheduler"""
        from datetime import datetime
        import subprocess
        
        # Format: HH:MM AM/PM
        time_str = notify_time.strftime("%H:%M")
        date_str = notify_time.strftime("%m/%d/%Y")
        
        # PowerShell command to create scheduled task
        ps_command = f'''
$action = New-ScheduledTaskAction -Execute "python" -Argument "{script_path} --title \\"WasteNot Alert\\" --message \\"{message}\\""
$trigger = New-ScheduledTaskTrigger -Once -At "{date_str} {time_str}"
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries
Register-ScheduledTask -TaskName "{job_id}" -Action $action -Trigger $trigger -Settings $settings -Force
'''
        
        try:
            subprocess.run(["powershell", "-Command", ps_command], check=True, capture_output=True)
        except subprocess.CalledProcessError:
            # Fallback to simpler method
            pass
    
    def schedule_macos(self, notify_time, message, job_id, script_path):
        """Schedule on macOS using launchd"""
        import subprocess
        import time
        
        # Calculate seconds until notification
        now = datetime.now()
        delay_seconds = int((notify_time - now).total_seconds())
        
        if delay_seconds > 0:
            # Use 'at' command (might require enabling: sudo launchctl load -w /System/Library/LaunchDaemons/com.apple.atrun.plist)
            cmd = f'echo "python \\"{script_path}\\" --title \\"WasteNot Alert\\" --message \\"{message}\\"" | at {notify_time.strftime("%H:%M %m/%d/%Y")}'
            try:
                subprocess.run(cmd, shell=True, check=True)
            except subprocess.CalledProcessError:
                # Fallback method
                pass
    
    def schedule_linux(self, notify_time, message, job_id, script_path):
        """Schedule on Linux using cron or at"""
        import subprocess
        
        # Use 'at' command if available
        time_str = notify_time.strftime("%H:%M %Y-%m-%d")
        cmd = f'echo "python3 {script_path} --title \\"WasteNot Alert\\" --message \\"{message}\\"" | at {time_str}'
        
        try:
            subprocess.run(cmd, shell=True, check=True)
        except subprocess.CalledProcessError:
            # Try cron alternative
            pass
    
    def unschedule_item_notifications(self, item_id):
        """Remove all scheduled notifications for an item"""
        system = platform.system()
        
        if system == "Windows":
            self.unschedule_windows(item_id)
        elif system == "Darwin":
            self.unschedule_macos(item_id)
        else:
            self.unschedule_linux(item_id)
    
    def unschedule_windows(self, item_id):
        """Remove Windows scheduled tasks"""
        import subprocess
        ps_command = f'Get-ScheduledTask -TaskName "wastenot_{item_id}_*" | Unregister-ScheduledTask -Confirm:$false'
        try:
            subprocess.run(["powershell", "-Command", ps_command], check=True, capture_output=True)
        except subprocess.CalledProcessError:
            pass
    
    def unschedule_macos(self, item_id):
        """Remove macOS scheduled jobs"""
        import subprocess
        # This would need more sophisticated tracking of job IDs
        pass
    
    def unschedule_linux(self, item_id):
        """Remove Linux scheduled jobs"""
        import subprocess
        # This would need more sophisticated tracking of job IDs
        pass


class CustomItemDialog(simpledialog.Dialog):
    def __init__(self, parent, title, existing_items=None):
        self.existing_items = existing_items or []
        super().__init__(parent, title)
    
    def body(self, frame):
        tk.Label(frame, text="Item Name:").grid(row=0, column=0, sticky="w", pady=5)
        self.name_entry = tk.Entry(frame, width=30)
        self.name_entry.grid(row=0, column=1, padx=5, pady=5)
        
        tk.Label(frame, text="Category:").grid(row=1, column=0, sticky="w", pady=5)
        self.category_var = tk.StringVar()
        categories = ["dairy", "meat", "vegetable", "fruit", "beverage", "bakery", "seafood", "frozen", "canned", "other"]
        self.category_combo = ttk.Combobox(frame, textvariable=self.category_var, values=categories, state="readonly")
        self.category_combo.grid(row=1, column=1, padx=5, pady=5)
        self.category_combo.set("other")
        
        tk.Label(frame, text="Default Expiry Days:").grid(row=2, column=0, sticky="w", pady=5)
        self.expiry_entry = tk.Entry(frame, width=30)
        self.expiry_entry.grid(row=2, column=1, padx=5, pady=5)
        
        tk.Label(frame, text="Expiry Unit:").grid(row=3, column=0, sticky="w", pady=5)
        self.unit_var = tk.StringVar(value="days")
        ttk.Radiobutton(frame, text="Days", variable=self.unit_var, value="days").grid(row=3, column=1, sticky="w", padx=5)
        ttk.Radiobutton(frame, text="Weeks", variable=self.unit_var, value="weeks").grid(row=4, column=1, sticky="w", padx=5)
        ttk.Radiobutton(frame, text="Months", variable=self.unit_var, value="months").grid(row=5, column=1, sticky="w", padx=5)
        
        return self.name_entry  # initial focus
    
    def validate(self):
        name = self.name_entry.get().strip()
        expiry_days = self.expiry_entry.get().strip()
        category = self.category_var.get()
        
        if not name:
            messagebox.showerror("Error", "Please enter an item name")
            return False
        
        if name.lower() in [item.lower() for item in self.existing_items]:
            messagebox.showerror("Error", "This item already exists!")
            return False
        
        if not expiry_days or not expiry_days.isdigit():
            messagebox.showerror("Error", "Please enter a valid number of days")
            return False
        
        if int(expiry_days) <= 0:
            messagebox.showerror("Error", "Expiry days must be greater than 0")
            return False
        
        if not category:
            messagebox.showerror("Error", "Please select a category")
            return False
        
        # Convert to days based on unit
        days = int(expiry_days)
        if self.unit_var.get() == "weeks":
            days = days * 7
        elif self.unit_var.get() == "months":
            days = days * 30
        
        self.result = (name, category, days)
        return True
    
    def apply(self):
        self.result = self.result


class WasteNotApp:
    def __init__(self, root):
        self.root = root
        self.root.title("WasteNot - Smart Food Waste Reducer")
        self.root.geometry("900x700")
        self.root.configure(bg='#f0f8f0')
        
        self.db = Database()
        self.setup_ui()
        self.refresh_items_list()
        
        # Reschedule all notifications on startup (in case app was reinstalled/moved)
        self.reschedule_all_notifications()
    
    def reschedule_all_notifications(self):
        """Reschedule all notifications for existing items (useful after app updates)"""
        items = self.db.get_all_items()
        for item in items:
            item_id, name, category, added_date, expiry_date, notified, is_custom, custom_expiry = item
            expiry = datetime.fromisoformat(expiry_date).date()
            self.db.schedule_notifications_for_item(item_id, name, expiry)
    
    def setup_ui(self):
        header_frame = tk.Frame(self.root, bg='#2e8b57', height=80)
        header_frame.pack(fill=tk.X, padx=10, pady=10)
        header_frame.pack_propagate(False)
        
        title_label = tk.Label(header_frame, text="WasteNot", font=('Arial', 24, 'bold'), 
                              fg='white', bg='#2e8b57')
        title_label.pack(pady=20)
        
        subtitle_label = tk.Label(header_frame, text="Smart Food Waste Reducer - Background Notifications", 
                                 font=('Arial', 10), fg='white', bg='#2e8b57')
        subtitle_label.pack()
        
        main_frame = tk.Frame(self.root, bg='#f0f8f0')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Add Item Frame
        add_frame = tk.LabelFrame(main_frame, text="Add Food Item", font=('Arial', 12, 'bold'),
                                 bg='#f0f8f0', fg='#2e8b57', padx=10, pady=10)
        add_frame.pack(fill=tk.X, pady=(0, 10))
        
        item_label = tk.Label(add_frame, text="Select Item:", bg='#f0f8f0', font=('Arial', 10))
        item_label.grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        
        self.item_var = tk.StringVar()
        self.update_item_combobox()
        self.item_combo = ttk.Combobox(add_frame, textvariable=self.item_var, 
                                      state="readonly", width=20)
        self.item_combo.grid(row=0, column=1, padx=(0, 10))
        self.item_combo.set("Select item")
        
        # Add Custom Item Button
        add_custom_btn = tk.Button(add_frame, text="+ Add Custom Item", 
                                  command=self.add_custom_item,
                                  bg='#4a90e2', fg='white', font=('Arial', 9, 'bold'),
                                  padx=10, pady=2)
        add_custom_btn.grid(row=0, column=2, padx=(0, 20))
        
        expiry_label = tk.Label(add_frame, text="Expires:", bg='#f0f8f0', font=('Arial', 10))
        expiry_label.grid(row=0, column=3, sticky=tk.W, padx=(0, 10))
        
        self.expiry_var = tk.StringVar()
        expiry_options = ["today", "tomorrow", "3 days", "5 days", "1 week", "2 weeks", "3 weeks", "1 month", "custom"]
        self.expiry_combo = ttk.Combobox(add_frame, textvariable=self.expiry_var, 
                                        values=expiry_options, state="readonly", width=12)
        self.expiry_combo.grid(row=0, column=4, padx=(0, 20))
        self.expiry_combo.set("Select expiry")
        self.expiry_combo.bind('<<ComboboxSelected>>', self.on_expiry_selected)
        
        # Custom expiry entry (hidden by default)
        self.custom_expiry_label = tk.Label(add_frame, text="Days:", bg='#f0f8f0', font=('Arial', 10))
        self.custom_expiry_entry = tk.Entry(add_frame, width=8)
        
        add_btn = tk.Button(add_frame, text="Add Item", command=self.add_item,
                           bg='#2e8b57', fg='white', font=('Arial', 10, 'bold'),
                           padx=20, pady=5)
        add_btn.grid(row=0, column=5)
        
        # Manage Custom Items Button
        manage_custom_btn = tk.Button(add_frame, text="Manage Custom Items", 
                                     command=self.manage_custom_items,
                                     bg='#ff6b35', fg='white', font=('Arial', 9, 'bold'),
                                     padx=10, pady=2)
        manage_custom_btn.grid(row=0, column=6, padx=(10, 0))
        
        # Items List Frame
        list_frame = tk.LabelFrame(main_frame, text="Your Food Items", font=('Arial', 12, 'bold'),
                                  bg='#f0f8f0', fg='#2e8b57', padx=10, pady=10)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        columns = ('id', 'name', 'category', 'added', 'expiry', 'days_left', 'type')
        self.tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=15)
        
        self.tree.heading('id', text='ID')
        self.tree.heading('name', text='Item Name')
        self.tree.heading('category', text='Category')
        self.tree.heading('added', text='Added Date')
        self.tree.heading('expiry', text='Expiry Date')
        self.tree.heading('days_left', text='Days Left')
        self.tree.heading('type', text='Type')
        
        self.tree.column('id', width=40)
        self.tree.column('name', width=120)
        self.tree.column('category', width=100)
        self.tree.column('added', width=100)
        self.tree.column('expiry', width=100)
        self.tree.column('days_left', width=80)
        self.tree.column('type', width=80)
        
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.tree.bind('<Double-1>', self.delete_selected_item)
        
        # Info label about background notifications
        info_label = tk.Label(main_frame, 
                             text="✓ Notifications work even when app is closed! ✓ Add custom items not in the default list",
                             font=('Arial', 9, 'italic'), fg='green', bg='#f0f8f0')
        info_label.pack(pady=5)
        
        self.status_var = tk.StringVar()
        self.status_var.set("Ready - Notifications work in background!")
        status_bar = tk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, 
                             anchor=tk.W, bg='#e0e0e0')
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def update_item_combobox(self):
        """Update the combobox with both default and custom items"""
        all_items = self.db.get_all_items_list()
        self.item_combo['values'] = all_items
    
    def on_expiry_selected(self, event):
        """Show/hide custom expiry entry based on selection"""
        if self.expiry_var.get() == "custom":
            self.custom_expiry_label.grid(row=0, column=6, padx=(10, 5))
            self.custom_expiry_entry.grid(row=0, column=7, padx=(0, 10))
        else:
            self.custom_expiry_label.grid_remove()
            self.custom_expiry_entry.grid_remove()
    
    def add_custom_item(self):
        """Open dialog to add a new custom item"""
        existing_items = self.db.get_all_items_list()
        dialog = CustomItemDialog(self.root, "Add Custom Food Item", existing_items)
        
        if dialog.result:
            name, category, expiry_days = dialog.result
            success = self.db.add_custom_item(name, category, expiry_days)
            
            if success:
                self.update_item_combobox()
                self.status_var.set(f"Added custom item: {name} (expires in {expiry_days} days)")
                messagebox.showinfo("Success", f"Custom item '{name}' added successfully!")
            else:
                messagebox.showerror("Error", "Failed to add custom item. It might already exist.")
    
    def manage_custom_items(self):
        """Open window to manage custom items"""
        manage_window = tk.Toplevel(self.root)
        manage_window.title("Manage Custom Items")
        manage_window.geometry("600x400")
        manage_window.configure(bg='#f0f8f0')
        
        tk.Label(manage_window, text="Custom Food Items", font=('Arial', 16, 'bold'), 
                fg='#2e8b57', bg='#f0f8f0').pack(pady=10)
        
        # Create treeview for custom items
        columns = ('name', 'category', 'expiry_days')
        tree = ttk.Treeview(manage_window, columns=columns, show='headings', height=15)
        
        tree.heading('name', text='Item Name')
        tree.heading('category', text='Category')
        tree.heading('expiry_days', text='Expiry Days')
        
        tree.column('name', width=200)
        tree.column('category', width=150)
        tree.column('expiry_days', width=100)
        
        scrollbar = ttk.Scrollbar(manage_window, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Load custom items
        custom_items = self.db.get_custom_items()
        for item in custom_items:
            item_id, name, category, expiry_days, expiry_unit = item
            tree.insert('', tk.END, values=(name, category, f"{expiry_days} days"))
        
        # Delete button
        def delete_selected_custom():
            selected = tree.selection()
            if selected:
                item = tree.item(selected[0])
                item_name = item['values'][0]
                
                if messagebox.askyesno("Confirm Delete", 
                                      f"Delete custom item '{item_name}'?\nThis will not affect already added items."):
                    self.db.delete_custom_item(item_name)
                    tree.delete(selected[0])
                    self.update_item_combobox()
                    messagebox.showinfo("Success", f"Custom item '{item_name}' deleted!")
        
        delete_btn = tk.Button(manage_window, text="Delete Selected", 
                              command=delete_selected_custom,
                              bg='#ff6b35', fg='white', font=('Arial', 10, 'bold'),
                              padx=15, pady=5)
        delete_btn.pack(pady=10)
        
        # Add new item button
        add_btn = tk.Button(manage_window, text="Add New Custom Item", 
                           command=lambda: [manage_window.destroy(), self.add_custom_item()],
                           bg='#2e8b57', fg='white', font=('Arial', 10, 'bold'),
                           padx=15, pady=5)
        add_btn.pack(pady=5)
    
    def add_item(self):
        item_name = self.item_var.get()
        expiry_option = self.expiry_var.get()
        
        if item_name == "Select item" or expiry_option == "Select expiry":
            messagebox.showerror("Error", "Please select both an item and expiry option")
            return
        
        custom_expiry_days = None
        if expiry_option == "custom":
            custom_days = self.custom_expiry_entry.get().strip()
            if not custom_days or not custom_days.isdigit() or int(custom_days) <= 0:
                messagebox.showerror("Error", "Please enter a valid number of days for custom expiry")
                return
            custom_expiry_days = int(custom_days)
        
        success = self.db.add_item(item_name, expiry_option, custom_expiry_days)
        
        if success:
            item_type = "custom" if item_name.lower() in self.db.custom_items else "default"
            self.status_var.set(f"Added {item_name} ({item_type}) with expiry: {expiry_option} - Notifications scheduled!")
            self.refresh_items_list()
            self.item_combo.set("Select item")
            self.expiry_combo.set("Select expiry")
            self.custom_expiry_entry.delete(0, tk.END)
            self.custom_expiry_label.grid_remove()
            self.custom_expiry_entry.grid_remove()
        else:
            messagebox.showerror("Error", "Failed to add item. Please try again.")
    
    def refresh_items_list(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        items = self.db.get_all_items()
        today = datetime.now().date()
        
        for item in items:
            item_id, name, category, added_date, expiry_date, notified, is_custom, custom_expiry = item
            expiry = datetime.fromisoformat(expiry_date).date()
            days_left = (expiry - today).days
            
            tag = ""
            if days_left < 0:
                tag = "expired"
            elif days_left == 0:
                tag = "critical"
            elif days_left <= 3:
                tag = "urgent"
            elif days_left <= 7:
                tag = "warning"
            
            item_type = "Custom" if is_custom else "Default"
            
            self.tree.insert('', tk.END, values=(
                item_id, name, category, 
                datetime.fromisoformat(added_date).strftime('%Y-%m-%d'),
                expiry_date,
                days_left if days_left >= 0 else "Expired",
                item_type
            ), tags=(tag,))