import csv
import json
import os
import sqlite3
import tkinter as tk
import webbrowser
from datetime import datetime
from tkinter import filedialog, messagebox, scrolledtext, ttk
from typing import Dict, List, Optional

from data_manager import DataManager
from database import SecurityEventDB
from gui import SecurityEventEncyclopedia

# data_manager.py


class DataManager:
    def __init__(self, db):
        self.db = db
        self.data_file = "custom_events.json"
        self.builtin_event_ids = {
            "4624",
            "4625",
            "4672",
            "4688",
            "1",
            "3",
            "12",
            "11",
            "25000",
        }

    def load_initial_data(self):
        """Load both built-in and custom events only if DB empty"""
        if self.db.get_event_count() == 0:
            self._load_builtin_events()
            self._load_custom_events()
        else:
            print("Database already populated, skipping initial load.")

    def _load_builtin_events(self):
        """Load the initial built-in events"""
        builtin_events = [
            # Windows Security Events
            {
                "event_id": "4624",
                "event_title": "An account was successfully logged on",
                "description": "An account was successfully logged on. This event occurs when a user successfully authenticates to a system.",
                "severity": "Low",
                "category": "Logon/Logoff",
                "platform": "Windows",
                "response_guidance": "Verify this is expected user activity. Check for unusual patterns in logon times or locations.",
                "reference_links": [
                    "https://docs.microsoft.com/en-us/windows/security/threat-protection/auditing/event-4624"
                ],
            },
            {
                "event_id": "4625",
                "event_title": "Account failed to log on",
                "description": "An account failed to log on. This can indicate brute force attacks or password spraying.",
                "severity": "Medium",
                "category": "Logon/Logoff",
                "platform": "Windows",
                "response_guidance": "Investigate source IP, check for brute force patterns, review account lockout policies.",
                "reference_links": [
                    "https://docs.microsoft.com/en-us/windows/security/threat-protection/auditing/event-4625"
                ],
            },
            {
                "event_id": "4672",
                "event_title": "Special privileges assigned to new logon",
                "description": "Special privileges were assigned to the new logon. This indicates a user with administrative privileges logged on.",
                "severity": "High",
                "category": "Privilege Use",
                "platform": "Windows",
                "response_guidance": "Verify the privilege assignment is authorized. Monitor for unusual administrative activity.",
                "reference_links": [
                    "https://docs.microsoft.com/en-us/windows/security/threat-protection/auditing/event-4672"
                ],
            },
            {
                "event_id": "4688",
                "event_title": "A new process has been created",
                "description": "A new process was created. This event provides information about the created process.",
                "severity": "Informational",
                "category": "Process Creation",
                "platform": "Windows",
                "response_guidance": "Review the process name and parent process for suspicious activity.",
                "reference_links": [
                    "https://docs.microsoft.com/en-us/windows/security/threat-protection/auditing/event-4688"
                ],
            },
            # Sysmon Events
            {
                "event_id": "1",
                "event_title": "Process creation",
                "description": "Logs when a process is created. Provides full command line and parent process information.",
                "severity": "Informational",
                "category": "Process Creation",
                "platform": "Sysmon",
                "response_guidance": "Review process lineage and command line arguments for suspicious activity.",
                "reference_links": [
                    "https://docs.microsoft.com/en-us/sysinternals/downloads/sysmon#event-id-1-process-creation"
                ],
            },
            {
                "event_id": "3",
                "event_title": "Network connection detected",
                "description": "Logs when a process makes a network connection. Includes source and destination information.",
                "severity": "Informational",
                "category": "Network Activity",
                "platform": "Sysmon",
                "response_guidance": "Review destination IPs and ports for suspicious connections.",
                "reference_links": [
                    "https://docs.microsoft.com/en-us/sysinternals/downloads/sysmon#event-id-3-network-connection"
                ],
            },
            # SharePoint Events
            {
                "event_id": "11",
                "event_title": "Site collection audit policy changed",
                "description": "The audit policy for a SharePoint site collection was modified. Changes to audit settings can affect what user actions are logged and monitored.",
                "severity": "Informational",
                "category": "Audit Policy Change",
                "platform": "SharePoint",
                "response_guidance": "Review the user or administrator who made this change to ensure it was authorized. Confirm that the updated audit policy still meets your compliance and monitoring requirements.",
                "reference_links": [
                    "https://www.ultimatewindowssecurity.com/securitylog/encyclopedia/event.aspx?eventid=11"
                ],
            },
            # SQL Server Events
            {
                "event_id": "12",
                "event_title": "Audit Policy Changed",
                "description": "The audit policy for a SharePoint site collection was modified. This change can affect what activities are logged for compliance and security monitoring.",
                "severity": "Informational",
                "category": "Audit Policy Change",
                "platform": "SharePoint",
                "response_guidance": "Review who made the change and ensure it aligns with your organization’s compliance and security requirements. If unauthorized, revert the changes and investigate the user’s activities.",
                "reference_links": [
                    "https://www.ultimatewindowssecurity.com/securitylog/encyclopedia/event.aspx?eventid=12"
                ],
            },
            # Exchange Events
            {
                "event_id": "25000",
                "event_title": "Undocumented Exchange mailbox operation",
                "description": "Undocumented Exchange mailbox operation. Specific behavior is not documented; treat as potentially sensitive.",
                "severity": "Medium",
                "category": "Mailbox/Directory Configuration",
                "platform": "Exchange",
                "response_guidance": "Investigate actor, scope, and context; correlate with related events to understand intent.",
                "reference_links": [
                    "https://www.ultimatewindowssecurity.com/securitylog/encyclopedia/event.aspx?eventid=25000"
                ],
            },
        ]

        for event in builtin_events:
            self.db.add_event(event)

        print(f"Loaded {len(builtin_events)} built-in events")

    def _load_custom_events(self):
        """Load custom events from JSON file if it exists"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, "r", encoding="utf-8") as f:
                    custom_events = json.load(f)

                loaded_count = 0
                for event in custom_events:
                    if self.db.add_event(event):
                        loaded_count += 1

                print(f"Loaded {loaded_count} custom events from {self.data_file}")

            except Exception as e:
                print(f"Error loading custom events: {e}")
        else:
            print("No custom events file found. Starting with built-in events only.")

    def add_custom_event(self, event_data):
        """Add a custom event through the GUI and track it for saving"""
        success = self.db.add_event(event_data)
        if success:
            print(
                f"Custom event added: {event_data['event_id']} ({event_data['platform']})"
            )
            # Immediately save to ensure persistence
            self.save_custom_events()
        return success

    def is_custom_event(self, event_id):
        """Check if an event is custom (not built-in)"""
        return event_id not in self.builtin_event_ids

    def get_custom_events(self):
        """Get all custom events from database"""
        all_events = self.db.search_events()
        custom_events = []

        for event in all_events:
            if self.is_custom_event(event["event_id"]):
                custom_events.append(
                    {
                        "event_id": event["event_id"],
                        "event_title": event["event_title"],
                        "description": event.get("description", ""),
                        "severity": event.get("severity", "Unknown"),
                        "category": event.get("category", ""),
                        "platform": event.get("platform", ""),
                        "response_guidance": event.get("response_guidance", ""),
                        "reference_links": event.get("reference_links", []),
                    }
                )

        return custom_events

    def save_custom_events(self):
        """Save all custom events to JSON file"""
        try:
            custom_events = self.get_custom_events()

            with open(self.data_file, "w", encoding="utf-8") as f:
                json.dump(custom_events, f, indent=2, ensure_ascii=False)

            print(f"Saved {len(custom_events)} custom events to {self.data_file}")
            return True

        except Exception as e:
            print(f"Error saving custom events: {e}")
            return False


# main.py


class SecurityEventApp:
    def __init__(self):
        self.db = None
        self.data_manager = None
        self.gui = None

    def run(self):
        try:
            # Initialize database
            print("Initializing Security Event Encyclopedia...")
            self.db = SecurityEventDB()

            # Initialize data manager
            self.data_manager = DataManager(self.db)

            # Load initial data (built-in + custom)
            self.data_manager.load_initial_data()

            # Get event counts
            total_count = self.db.get_event_count()
            custom_count = self.db.get_custom_events_count()

            print(
                f"Database ready with {total_count} total events ({custom_count} custom)"
            )

            # Create and run GUI - pass both db and data_manager
            root = tk.Tk()
            self.gui = SecurityEventEncyclopedia(root, self.db, self.data_manager)

            # Save custom events when application closes
            def on_closing():
                self.data_manager.save_custom_events()
                root.destroy()

            root.protocol("WM_DELETE_WINDOW", on_closing)
            root.mainloop()

        except Exception as e:
            print(f"Error starting application: {e}")
            import traceback

            traceback.print_exc()
            input("Press Enter to exit...")


def main():
    app = SecurityEventApp()
    app.run()


if __name__ == "__main__":
    main()

# database.py


class SecurityEventDB:
    def __init__(self, db_path="security_events.db"):
        self.db_path = db_path
        self.init_database()

    def init_database(self):
        """Initialize database with required tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # REMOVE these lines:
        # cursor.execute('DROP TABLE IF EXISTS user_notes')
        # cursor.execute('DROP TABLE IF EXISTS security_events')

        # Use CREATE TABLE IF NOT EXISTS instead
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS security_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_id TEXT NOT NULL,
                event_title TEXT NOT NULL,
                description TEXT,
                severity TEXT,
                category TEXT,
                platform TEXT NOT NULL,
                response_guidance TEXT,
                reference_links TEXT,
                custom_notes TEXT,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                modified_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(event_id, platform)
            )
        """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS user_notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_id TEXT NOT NULL,
                platform TEXT NOT NULL,
                note_text TEXT,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (event_id, platform) REFERENCES security_events (event_id, platform)
            )
        """
        )

        # Keep indexes but also make them conditional:
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_event_id ON security_events(event_id)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_category ON security_events(category)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_platform ON security_events(platform)"
        )
        cursor.execute(
            "CREATE UNIQUE INDEX IF NOT EXISTS idx_event_platform ON security_events(event_id, platform)"
        )

        conn.commit()
        conn.close()
        print("Database initialized successfully")

    def add_event(self, event_data: Dict) -> bool:
        """Add a new security event to the database, preventing duplicates"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute(
                """
                INSERT OR IGNORE INTO security_events 
                (event_id, event_title, description, severity, category, platform, response_guidance, reference_links)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    event_data["event_id"],
                    event_data["event_title"],
                    event_data.get("description", ""),
                    event_data.get("severity", "Unknown"),
                    event_data.get("category", ""),
                    event_data.get("platform", ""),
                    event_data.get("response_guidance", ""),
                    json.dumps(event_data.get("reference_links", [])),
                ),
            )

            conn.commit()
            success = cursor.rowcount > 0

            if success:
                print(
                    f"Added event: {event_data['event_id']} ({event_data['platform']})"
                )
            else:
                print(
                    f"Event already exists: {event_data['event_id']} ({event_data['platform']})"
                )

            return success

        except sqlite3.Error as e:
            print(f"Database error adding event {event_data['event_id']}: {e}")
            return False
        finally:
            conn.close()

    def search_events(
        self, query: str = "", category: str = "", platform: str = ""
    ) -> List[Dict]:
        """Search events with filters"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        sql = "SELECT * FROM security_events WHERE 1=1"
        params = []

        if query:
            sql += " AND (event_id LIKE ? OR event_title LIKE ? OR description LIKE ?)"
            params.extend([f"%{query}%", f"%{query}%", f"%{query}%"])

        if category and category != "All":
            sql += " AND category = ?"
            params.append(category)

        if platform and platform != "All":
            sql += " AND platform = ?"
            params.append(platform)

        sql += " ORDER BY platform, event_id"

        cursor.execute(sql, params)
        results = [dict(row) for row in cursor.fetchall()]

        # Parse JSON fields
        for result in results:
            if result.get("reference_links"):
                try:
                    result["reference_links"] = json.loads(result["reference_links"])
                except json.JSONDecodeError:
                    result["reference_links"] = []

        conn.close()
        return results

    def get_event_by_id(self, event_id: str, platform: str = None) -> Optional[Dict]:
        """Get specific event by ID and platform"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        if platform:
            cursor.execute(
                "SELECT * FROM security_events WHERE event_id = ? AND platform = ?",
                (event_id, platform),
            )
        else:
            cursor.execute(
                "SELECT * FROM security_events WHERE event_id = ?", (event_id,)
            )

        if result := cursor.fetchone():
            event_data = dict(result)
            if event_data.get("reference_links"):
                try:
                    event_data["reference_links"] = json.loads(
                        event_data["reference_links"]
                    )
                except json.JSONDecodeError:
                    event_data["reference_links"] = []
            conn.close()
            return event_data

        conn.close()
        return None

    def add_user_note(self, event_id: str, platform: str, note_text: str):
        """Add user note to an event"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            # Add to user_notes table
            cursor.execute(
                """
                INSERT INTO user_notes (event_id, platform, note_text)
                VALUES (?, ?, ?)
            """,
                (event_id, platform, note_text),
            )

            # Update custom notes in main table
            cursor.execute(
                """
                UPDATE security_events 
                SET custom_notes = COALESCE(custom_notes || '\n', '') || ?, 
                    modified_date = CURRENT_TIMESTAMP
                WHERE event_id = ? AND platform = ?
            """,
                (
                    f"[{datetime.now().strftime('%Y-%m-%d %H:%M')}] {note_text}",
                    event_id,
                    platform,
                ),
            )

            conn.commit()
            print(f"Note added to event {event_id} ({platform})")
        except sqlite3.Error as e:
            print(f"Database error when adding note: {e}")
        finally:
            conn.close()

    def get_event_count(self) -> int:
        """Get total number of events in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM security_events")
        count = cursor.fetchone()[0]

        conn.close()
        return count

    def _get_connection(self):
        """Get a database connection (for internal use)"""
        return sqlite3.connect(self.db_path)

    def get_custom_events_count(self):
        """Get count of events added after initial load"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Count events that are not in the initial sample data
        cursor.execute(
            """
            SELECT COUNT(*) FROM security_events 
            WHERE event_id NOT IN ('4624', '4625', '4672', '4688', '1', '3', 'AUTH-1000', 'AUTH-2000', 'SP-1001')
        """
        )
        count = cursor.fetchone()[0]

        conn.close()
        return count

    def export_events_to_json(self, filename=None):
        """Export all events to JSON file for portability"""
        if not filename:
            filename = f"security_events_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        events = self.search_events()  # Get all events
        export_data = []

        for event in events:
            # Create a clean export format
            export_event = {
                "event_id": event["event_id"],
                "event_title": event["event_title"],
                "description": event.get("description", ""),
                "severity": event.get("severity", "Unknown"),
                "category": event.get("category", ""),
                "platform": event.get("platform", ""),
                "response_guidance": event.get("response_guidance", ""),
                "reference_links": event.get("reference_links", []),
            }
            export_data.append(export_event)

        with open(filename, "w", encoding="utf-8") as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)

        return filename

    def import_events_from_json(self, filename):
        """Import events from JSON file"""
        try:
            with open(filename, "r", encoding="utf-8") as f:
                events_data = json.load(f)

            imported_count = 0
            for event_data in events_data:
                try:
                    if self.add_event(event_data):
                        imported_count += 1
                except Exception as e:
                    print(
                        f"Error importing event {event_data.get('event_id', 'Unknown')}: {e}"
                    )

            return imported_count

        except Exception as e:
            print(f"Error importing from {filename}: {e}")
            return 0


# gui.py


class AddEventDialog:
    def __init__(self, parent, db, data_manager, on_event_added=None, event_data=None):
        self.parent = parent
        self.db = db
        self.data_manager = data_manager
        self.on_event_added = on_event_added
        self.event_data = event_data  # For edit mode
        self.is_edit_mode = event_data is not None

        self.dialog = tk.Toplevel(parent)
        if self.is_edit_mode:
            self.dialog.title(
                f"Edit Event: {event_data['event_id']} ({event_data['platform']})"
            )
        else:
            self.dialog.title("Add New Security Event")
        self.dialog.geometry("600x700")
        self.dialog.transient(parent)
        self.dialog.grab_set()

        self.setup_ui()
        if self.is_edit_mode:
            self.populate_form()

    def setup_ui(self):
        """Setup the add/edit event form"""
        main_frame = ttk.Frame(self.dialog, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Form fields
        ttk.Label(main_frame, text="Event ID:*", font=("Arial", 9, "bold")).grid(
            row=0, column=0, sticky=tk.W, pady=2
        )
        self.event_id_var = tk.StringVar()
        self.event_id_entry = ttk.Entry(
            main_frame, textvariable=self.event_id_var, width=50
        )
        self.event_id_entry.grid(
            row=0, column=1, sticky=(tk.W, tk.E), pady=2, padx=(5, 0)
        )
        if self.is_edit_mode:
            self.event_id_entry.config(
                state="readonly"
            )  # Can't change event ID in edit mode

        ttk.Label(main_frame, text="Event Title:*", font=("Arial", 9, "bold")).grid(
            row=1, column=0, sticky=tk.W, pady=2
        )
        self.title_var = tk.StringVar()
        self.title_entry = ttk.Entry(main_frame, textvariable=self.title_var, width=50)
        self.title_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=2, padx=(5, 0))

        ttk.Label(main_frame, text="Platform:*", font=("Arial", 9, "bold")).grid(
            row=2, column=0, sticky=tk.W, pady=2
        )
        self.platform_var = tk.StringVar()
        self.platform_combo = ttk.Combobox(
            main_frame,
            textvariable=self.platform_var,
            values=[
                "Windows",
                "Linux",
                "Sysmon",
                "SharePoint",
                "SQL Server",
                "Exchange",
                "Azure",
                "Other",
            ],
        )
        self.platform_combo.grid(row=2, column=1, sticky=tk.W, pady=2, padx=(5, 0))
        if self.is_edit_mode:
            self.platform_combo.config(
                state="readonly"
            )  # Can't change platform in edit mode

        ttk.Label(main_frame, text="Category:*", font=("Arial", 9, "bold")).grid(
            row=3, column=0, sticky=tk.W, pady=2
        )
        self.category_var = tk.StringVar()
        self.category_combo = ttk.Combobox(
            main_frame,
            textvariable=self.category_var,
            values=[
                "Logon/Logoff",
                "Privilege Use",
                "Process Creation",
                "Authentication",
                "File Access",
                "Account Management",
                "System",
                "Network Activity",
                "Registry",
                "DNS",
                "Firewall",
                "Application",
                "General Security" "Authentication/Logins",
                "Permissions & Authorization",
                "Object Changes",
                "Database Configuration",
                "Security & Encryption",
                "Detailed Tracking",
                "DS Access",
                "System Events",
                "Policy Change",
                "Object Access",
                "Privilege Use",
                "Account Management",
                "Logon/Logoff",
                "Account Logon",
                "Other",
            ],
        )
        self.category_combo.grid(row=3, column=1, sticky=tk.W, pady=2, padx=(5, 0))

        ttk.Label(main_frame, text="Severity:*", font=("Arial", 9, "bold")).grid(
            row=4, column=0, sticky=tk.W, pady=2
        )
        self.severity_var = tk.StringVar()
        self.severity_combo = ttk.Combobox(
            main_frame,
            textvariable=self.severity_var,
            values=["Informational", "Low", "Medium", "High", "Critical"],
        )
        self.severity_combo.grid(row=4, column=1, sticky=tk.W, pady=2, padx=(5, 0))

        ttk.Label(main_frame, text="Description:*", font=("Arial", 9, "bold")).grid(
            row=5, column=0, sticky=tk.NW, pady=2
        )
        self.desc_text = scrolledtext.ScrolledText(
            main_frame, width=50, height=4, wrap=tk.WORD
        )
        self.desc_text.grid(row=5, column=1, sticky=(tk.W, tk.E), pady=2, padx=(5, 0))

        ttk.Label(
            main_frame, text="Response Guidance:*", font=("Arial", 9, "bold")
        ).grid(row=6, column=0, sticky=tk.NW, pady=2)
        self.response_text = scrolledtext.ScrolledText(
            main_frame, width=50, height=4, wrap=tk.WORD
        )
        self.response_text.grid(
            row=6, column=1, sticky=(tk.W, tk.E), pady=2, padx=(5, 0)
        )

        ttk.Label(
            main_frame, text="Reference Links (one per line):", font=("Arial", 9)
        ).grid(row=7, column=0, sticky=tk.NW, pady=2)
        self.links_text = scrolledtext.ScrolledText(
            main_frame, width=50, height=3, wrap=tk.WORD
        )
        self.links_text.grid(row=7, column=1, sticky=(tk.W, tk.E), pady=2, padx=(5, 0))

        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=8, column=0, columnspan=2, pady=20)

        if self.is_edit_mode:
            ttk.Button(
                button_frame, text="Update Event", command=self.update_event
            ).pack(side=tk.LEFT, padx=(0, 10))
        else:
            ttk.Button(button_frame, text="Add Event", command=self.add_event).pack(
                side=tk.LEFT, padx=(0, 10)
            )
        ttk.Button(button_frame, text="Cancel", command=self.dialog.destroy).pack(
            side=tk.LEFT
        )

        # Configure grid weights
        main_frame.columnconfigure(1, weight=1)

    def populate_form(self):
        """Populate form with existing event data for editing"""
        if not self.event_data:
            return

        self.event_id_var.set(self.event_data["event_id"])
        self.title_var.set(self.event_data["event_title"])
        self.platform_var.set(self.event_data["platform"])
        self.category_var.set(self.event_data["category"])
        self.severity_var.set(self.event_data["severity"])

        self.desc_text.delete(1.0, tk.END)
        self.desc_text.insert(1.0, self.event_data.get("description", ""))

        self.response_text.delete(1.0, tk.END)
        self.response_text.insert(1.0, self.event_data.get("response_guidance", ""))

        self.links_text.delete(1.0, tk.END)
        if links := self.event_data.get("reference_links", []):
            self.links_text.insert(1.0, "\n".join(links))

    def add_event(self):
        """Add the new event to database using DataManager"""
        event_data = self._validate_and_get_event_data()
        if not event_data:
            return

        try:
            # Add to database USING DATA MANAGER
            success = self.data_manager.add_custom_event(event_data)
            if success:
                messagebox.showinfo(
                    "Success", f"Event {event_data['event_id']} added successfully!"
                )

                # Callback to refresh main UI
                if self.on_event_added:
                    self.on_event_added()

                self.dialog.destroy()
            else:
                messagebox.showerror(
                    "Error", f"Event {event_data['event_id']} already exists!"
                )

        except Exception as e:
            messagebox.showerror("Error", f"Failed to add event: {str(e)}")

    def update_event(self):
        """Update existing event"""
        event_data = self._validate_and_get_event_data()
        if not event_data:
            return

        try:
            # For update, we need to delete the old event and add the updated one
            # First delete the old event
            self._delete_event(self.event_data["event_id"], self.event_data["platform"])

            # Then add the updated event
            success = self.data_manager.add_custom_event(event_data)
            if success:
                messagebox.showinfo(
                    "Success", f"Event {event_data['event_id']} updated successfully!"
                )

                # Callback to refresh main UI
                if self.on_event_added:
                    self.on_event_added()

                self.dialog.destroy()
            else:
                messagebox.showerror(
                    "Error", f"Failed to update event {event_data['event_id']}!"
                )

        except Exception as e:
            messagebox.showerror("Error", f"Failed to update event: {str(e)}")

    def _delete_event(self, event_id, platform):
        """Delete an event from database"""
        conn = self.db._get_connection()
        cursor = conn.cursor()

        try:
            # Delete from user_notes first (foreign key constraint)
            cursor.execute(
                "DELETE FROM user_notes WHERE event_id = ? AND platform = ?",
                (event_id, platform),
            )
            # Delete from security_events
            cursor.execute(
                "DELETE FROM security_events WHERE event_id = ? AND platform = ?",
                (event_id, platform),
            )
            conn.commit()
            return True
        except Exception as e:
            print(f"Error deleting event: {e}")
            return False
        finally:
            conn.close()

    def _validate_and_get_event_data(self):
        """Validate form and return event data dict"""
        # Validate required fields
        if not self.event_id_var.get().strip():
            messagebox.showerror("Error", "Event ID is required!")
            return None

        if not self.title_var.get().strip():
            messagebox.showerror("Error", "Event Title is required!")
            return None

        if not self.platform_var.get().strip():
            messagebox.showerror("Error", "Platform is required!")
            return None

        if not self.category_var.get().strip():
            messagebox.showerror("Error", "Category is required!")
            return None

        if not self.severity_var.get().strip():
            messagebox.showerror("Error", "Severity is required!")
            return None

        description = self.desc_text.get(1.0, tk.END).strip()
        if not description:
            messagebox.showerror("Error", "Description is required!")
            return None

        response_guidance = self.response_text.get(1.0, tk.END).strip()
        if not response_guidance:
            messagebox.showerror("Error", "Response Guidance is required!")
            return None

        # Process reference links
        links_text = self.links_text.get(1.0, tk.END).strip()
        reference_links = [
            link.strip() for link in links_text.split("\n") if link.strip()
        ]

        # Create event data
        event_data = {
            "event_id": self.event_id_var.get().strip(),
            "event_title": self.title_var.get().strip(),
            "platform": self.platform_var.get().strip(),
            "category": self.category_var.get().strip(),
            "severity": self.severity_var.get().strip(),
            "description": description,
            "response_guidance": response_guidance,
            "reference_links": reference_links,
        }

        return event_data


class SecurityEventEncyclopedia:
    def __init__(self, root, db=None, data_manager=None):
        self.root = root
        self.root.title("Security Event Encyclopedia")
        self.root.geometry("1200x800")

        # Use provided database and data_manager instances
        if db is None:
            self.db = SecurityEventDB()
        else:
            self.db = db

        if data_manager is None:
            self.data_manager = DataManager(self.db)
        else:
            self.data_manager = data_manager

        self.current_event_id = None
        self.current_platform = None
        self.current_event_data = None

        self.setup_ui()
        self.load_categories()
        self.on_search()  # Load initial data

    def setup_ui(self):
        menubar = tk.Menu(self.root)

        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Exit", command=self.root.quit)
        menubar.add_cascade(label="File", menu=file_menu)

        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="About", command=self.show_about)
        menubar.add_cascade(label="Help", menu=help_menu)

        self.root.config(menu=menubar)

        """Setup the main user interface"""
        # Create main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)

        # Search frame
        search_frame = ttk.Frame(main_frame)
        search_frame.grid(
            row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10)
        )

        ttk.Label(search_frame, text="Search:").grid(row=0, column=0, padx=(0, 5))
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(
            search_frame, textvariable=self.search_var, width=40
        )
        self.search_entry.grid(row=0, column=1, padx=(0, 10))
        self.search_entry.bind("", self.on_search)

        ttk.Label(search_frame, text="Platform:").grid(row=0, column=2, padx=(10, 5))
        self.platform_var = tk.StringVar()
        self.platform_combo = ttk.Combobox(
            search_frame,
            textvariable=self.platform_var,
            values=[
                "All",
                "Windows",
                "Linux",
                "Sysmon",
                "SharePoint",
                "SQL Server",
                "Exchange",
                "Azure",
                "Other",
            ],
        )
        self.platform_combo.set("All")
        self.platform_combo.grid(row=0, column=3, padx=(0, 10))
        self.platform_combo.bind("<>", self.on_search)

        ttk.Label(search_frame, text="Category:").grid(row=0, column=4, padx=(10, 5))
        self.category_var = tk.StringVar()
        self.category_combo = ttk.Combobox(search_frame, textvariable=self.category_var)
        self.category_combo.set("All")
        self.category_combo.grid(row=0, column=5, padx=(0, 10))
        self.category_combo.bind("<>", self.on_search)

        ttk.Button(search_frame, text="Clear", command=self.clear_search).grid(
            row=0, column=6, padx=(10, 0)
        )

        # Results frame
        results_frame = ttk.Frame(main_frame)
        results_frame.grid(
            row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10)
        )
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(0, weight=1)

        # Results treeview
        columns = ("Event ID", "Title", "Platform", "Category", "Severity")
        self.results_tree = ttk.Treeview(
            results_frame, columns=columns, show="headings", height=15
        )

        # Define headings
        for col in columns:
            self.results_tree.heading(col, text=col)
            self.results_tree.column(col, width=120)

        self.results_tree.column("Title", width=300)
        self.results_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Scrollbar for treeview
        tree_scroll = ttk.Scrollbar(
            results_frame, orient=tk.VERTICAL, command=self.results_tree.yview
        )
        tree_scroll.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.results_tree.configure(yscrollcommand=tree_scroll.set)

        # Bind selection event
        self.results_tree.bind("<>", self.on_event_select)

        # Details frame
        details_frame = ttk.LabelFrame(main_frame, text="Event Details", padding="10")
        details_frame.grid(
            row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10)
        )
        details_frame.columnconfigure(1, weight=1)

        # Event details widgets
        ttk.Label(details_frame, text="Event ID:").grid(
            row=0, column=0, sticky=tk.W, pady=2
        )
        self.event_id_var = tk.StringVar()
        ttk.Label(details_frame, textvariable=self.event_id_var).grid(
            row=0, column=1, sticky=tk.W, pady=2
        )

        ttk.Label(details_frame, text="Platform:").grid(
            row=1, column=0, sticky=tk.W, pady=2
        )
        self.platform_detail_var = tk.StringVar()
        ttk.Label(details_frame, textvariable=self.platform_detail_var).grid(
            row=1, column=1, sticky=tk.W, pady=2
        )

        ttk.Label(details_frame, text="Title:").grid(
            row=2, column=0, sticky=tk.W, pady=2
        )
        self.title_var = tk.StringVar()
        ttk.Label(details_frame, textvariable=self.title_var, wraplength=800).grid(
            row=2, column=1, sticky=tk.W, pady=2
        )

        ttk.Label(details_frame, text="Severity:").grid(
            row=3, column=0, sticky=tk.W, pady=2
        )
        self.severity_var = tk.StringVar()
        ttk.Label(details_frame, textvariable=self.severity_var).grid(
            row=3, column=1, sticky=tk.W, pady=2
        )

        ttk.Label(details_frame, text="Category:").grid(
            row=4, column=0, sticky=tk.W, pady=2
        )
        self.category_detail_var = tk.StringVar()
        ttk.Label(details_frame, textvariable=self.category_detail_var).grid(
            row=4, column=1, sticky=tk.W, pady=2
        )

        ttk.Label(details_frame, text="Description:").grid(
            row=5, column=0, sticky=tk.NW, pady=2
        )
        self.desc_text = scrolledtext.ScrolledText(
            details_frame, width=80, height=4, wrap=tk.WORD
        )
        self.desc_text.grid(row=5, column=1, sticky=(tk.W, tk.E), pady=2)
        self.desc_text.config(state=tk.DISABLED)

        ttk.Label(details_frame, text="Response Guidance:").grid(
            row=6, column=0, sticky=tk.NW, pady=2
        )
        self.response_text = scrolledtext.ScrolledText(
            details_frame, width=80, height=3, wrap=tk.WORD
        )
        self.response_text.grid(row=6, column=1, sticky=(tk.W, tk.E), pady=2)
        self.response_text.config(state=tk.DISABLED)

        # Reference links
        ttk.Label(details_frame, text="Reference Links:").grid(
            row=7, column=0, sticky=tk.NW, pady=2
        )
        self.links_frame = ttk.Frame(details_frame)
        self.links_frame.grid(row=7, column=1, sticky=(tk.W, tk.E), pady=2)

        # Notes frame
        notes_frame = ttk.LabelFrame(main_frame, text="Custom Notes", padding="10")
        notes_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        notes_frame.columnconfigure(0, weight=1)
        notes_frame.rowconfigure(0, weight=1)

        self.notes_text = scrolledtext.ScrolledText(
            notes_frame, width=80, height=3, wrap=tk.WORD
        )
        self.notes_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        notes_buttons = ttk.Frame(notes_frame)
        notes_buttons.grid(row=1, column=0, sticky=tk.E, pady=(5, 0))

        ttk.Button(notes_buttons, text="Add Note", command=self.add_note).pack(
            side=tk.RIGHT, padx=(5, 0)
        )
        ttk.Button(notes_buttons, text="Clear Note", command=self.clear_note).pack(
            side=tk.RIGHT, padx=(5, 0)
        )

        # Action buttons frame (for selected event actions)
        action_frame = ttk.LabelFrame(main_frame, text="Event Actions", padding="10")
        action_frame.grid(
            row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10)
        )

        ttk.Button(
            action_frame, text="Edit Selected Event", command=self.edit_selected_event
        ).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(
            action_frame,
            text="Delete Selected Event",
            command=self.delete_selected_event,
        ).pack(side=tk.LEFT, padx=(0, 10))

        # Main action buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=5, column=0, columnspan=2, sticky=tk.E, pady=(10, 0))

        ttk.Button(button_frame, text="Import Events", command=self.import_events).pack(
            side=tk.RIGHT, padx=(5, 0)
        )
        ttk.Button(button_frame, text="Export Events", command=self.export_events).pack(
            side=tk.RIGHT, padx=(5, 0)
        )
        ttk.Button(button_frame, text="Add New Event", command=self.add_new_event).pack(
            side=tk.RIGHT, padx=(5, 0)
        )
        ttk.Button(button_frame, text="Refresh", command=self.on_search).pack(
            side=tk.RIGHT, padx=(5, 0)
        )

    def show_about(self):
        """Show about dialog"""
        messagebox.showinfo(
            "About", "Security Event Encyclopedia\n\nDeveloped by Rushab"
        )

    def load_categories(self):
        """Load available categories"""
        categories = [
            "All",
            "Logon/Logoff",
            "Privilege Use",
            "Process Creation",
            "Authentication",
            "File Access",
            "Account Management",
            "System",
            "Network Activity",
            "Registry",
            "DNS",
            "Firewall",
            "General Security",
            "Application",
            "Authentication/Logins",
            "Permissions & Authorization",
            "Object Changes",
            "Database Configuration",
            "Security & Encryption",
            "Detailed Tracking",
            "DS Access",
            "System Events",
            "Policy Change",
            "Object Access",
            "Privilege Use",
            "Account Management",
            "Logon/Logoff",
            "Account Logon",
            "Other",
        ]
        self.category_combo["values"] = categories

    def on_search(self, event=None):
        """Handle search operations"""
        query = self.search_var.get()
        platform = self.platform_var.get() if self.platform_var.get() != "All" else ""
        category = self.category_var.get() if self.category_var.get() != "All" else ""

        try:
            results = self.db.search_events(query, category, platform)
            self.display_results(results)
        except Exception as e:
            messagebox.showerror("Search Error", f"Error during search: {str(e)}")

    def clear_search(self):
        """Clear search filters"""
        self.search_var.set("")
        self.platform_var.set("All")
        self.category_var.set("All")
        self.on_search()

    def display_results(self, results):
        """Display search results in treeview"""
        # Clear existing results
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)

        # Add new results
        for event in results:
            self.results_tree.insert(
                "",
                tk.END,
                values=(
                    event["event_id"],
                    event["event_title"],
                    event["platform"],
                    event["category"],
                    event["severity"],
                ),
                tags=(event["event_id"], event["platform"]),
            )

    def on_event_select(self, event):
        """Handle event selection from results"""
        selection = self.results_tree.selection()
        if not selection:
            return

        try:
            item = selection[0]
            tags = self.results_tree.item(item, "tags")
            event_id = tags[0] if tags else ""
            platform = tags[1] if len(tags) > 1 else ""

            if event_id and platform:
                event_data = self.db.get_event_by_id(event_id, platform)
                if event_data:
                    self.display_event_details(event_data)
                    self.current_event_data = event_data  # Store for edit/delete
        except Exception as e:
            messagebox.showerror("Error", f"Error loading event details: {str(e)}")

    def display_event_details(self, event_data):
        """Display detailed event information"""
        try:
            self.current_event_id = event_data["event_id"]
            self.current_platform = event_data["platform"]

            self.event_id_var.set(event_data["event_id"])
            self.platform_detail_var.set(event_data["platform"])
            self.title_var.set(event_data["event_title"])
            self.severity_var.set(event_data["severity"])
            self.category_detail_var.set(event_data["category"])

            # Clear and set text widgets
            self.desc_text.config(state=tk.NORMAL)
            self.desc_text.delete(1.0, tk.END)
            self.desc_text.insert(
                1.0, event_data.get("description", "No description available")
            )
            self.desc_text.config(state=tk.DISABLED)

            self.response_text.config(state=tk.NORMAL)
            self.response_text.delete(1.0, tk.END)
            self.response_text.insert(
                1.0,
                event_data.get("response_guidance", "No response guidance available"),
            )
            self.response_text.config(state=tk.DISABLED)

            # Clear existing links
            for widget in self.links_frame.winfo_children():
                widget.destroy()

            # Add reference links
            links = event_data.get("reference_links", [])
            if isinstance(links, list) and links:
                for i, link in enumerate(links):
                    if link:  # Only create button if link is not empty
                        btn = ttk.Button(
                            self.links_frame,
                            text=f"Reference {i+1}",
                            command=lambda l=link: webbrowser.open(l),
                        )
                        btn.grid(row=0, column=i, padx=(0, 5))
            else:
                ttk.Label(self.links_frame, text="No reference links available").grid(
                    row=0, column=0
                )

            # Load custom notes
            self.notes_text.delete(1.0, tk.END)
            custom_notes = event_data.get("custom_notes", "")
            if custom_notes:
                self.notes_text.insert(1.0, custom_notes)

        except Exception as e:
            messagebox.showerror("Error", f"Error displaying event details: {str(e)}")

    def add_note(self):
        """Add custom note to selected event"""
        if not self.current_event_id or not self.current_platform:
            messagebox.showwarning("Warning", "Please select an event first.")
            return

        note_text = self.notes_text.get(1.0, tk.END).strip()
        if not note_text:
            messagebox.showwarning("Warning", "Note cannot be empty.")
            return

        try:
            self.db.add_user_note(
                self.current_event_id, self.current_platform, note_text
            )
            messagebox.showinfo("Success", "Note added successfully.")

            # Refresh the display
            event_data = self.db.get_event_by_id(
                self.current_event_id, self.current_platform
            )
            if event_data:
                self.display_event_details(event_data)

        except Exception as e:
            messagebox.showerror("Error", f"Error adding note: {str(e)}")

    def clear_note(self):
        """Clear the notes text area"""
        self.notes_text.delete(1.0, tk.END)

    def edit_selected_event(self):
        """Open edit dialog for selected event"""
        if not self.current_event_data:
            messagebox.showwarning("Warning", "Please select an event to edit.")
            return

        # Check if it's a built-in event (read-only)
        if not self.data_manager.is_custom_event(self.current_event_data["event_id"]):
            messagebox.showwarning(
                "Warning",
                "Built-in events cannot be edited. Please add a custom event instead.",
            )
            return

        AddEventDialog(
            self.root,
            self.db,
            self.data_manager,
            self.on_search,
            self.current_event_data,
        )

    def delete_selected_event(self):
        """Delete the selected event"""
        if not self.current_event_data:
            messagebox.showwarning("Warning", "Please select an event to delete.")
            return

        # Check if it's a built-in event (protected)
        if not self.data_manager.is_custom_event(self.current_event_data["event_id"]):
            messagebox.showwarning("Warning", "Built-in events cannot be deleted.")
            return

        event_id = self.current_event_data["event_id"]
        platform = self.current_event_data["platform"]

        # Confirm deletion
        result = messagebox.askyesno(
            "Confirm Delete",
            f"Are you sure you want to delete event {event_id} ({platform})?\n\nThis action cannot be undone.",
        )

        if result:
            try:
                # Delete from database
                success = self._delete_event(event_id, platform)
                if success:
                    messagebox.showinfo(
                        "Success", f"Event {event_id} deleted successfully!"
                    )
                    # Refresh data manager to update custom events
                    self.data_manager.save_custom_events()
                    # Refresh the display
                    self.on_search()
                    # Clear current selection
                    self.current_event_data = None
                    self.current_event_id = None
                    self.current_platform = None
                else:
                    messagebox.showerror("Error", f"Failed to delete event {event_id}!")

            except Exception as e:
                messagebox.showerror("Error", f"Error deleting event: {str(e)}")

    def _delete_event(self, event_id, platform):
        """Delete an event from database"""
        conn = self.db._get_connection()
        cursor = conn.cursor()

        try:
            # Delete from user_notes first (foreign key constraint)
            cursor.execute(
                "DELETE FROM user_notes WHERE event_id = ? AND platform = ?",
                (event_id, platform),
            )
            # Delete from security_events
            cursor.execute(
                "DELETE FROM security_events WHERE event_id = ? AND platform = ?",
                (event_id, platform),
            )
            conn.commit()
            return True
        except Exception as e:
            print(f"Error deleting event: {e}")
            return False
        finally:
            conn.close()

    def export_events(self):
        """Export all events to JSON file"""
        try:
            filename = filedialog.asksaveasfilename(
                title="Export Events",
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            )

            if filename:
                exported_file = self.db.export_events_to_json(filename)
                custom_count = self.db.get_custom_events_count()
                total_count = self.db.get_event_count()

                messagebox.showinfo(
                    "Export Successful",
                    f"Exported {total_count} events to:\n{exported_file}\n\n"
                    f"Custom events included: {custom_count}",
                )

        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export events: {str(e)}")

    def import_events(self):
        """Import events from JSON file"""
        try:
            filename = filedialog.askopenfilename(
                title="Import Events",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            )

            if filename:
                # Confirm import
                result = messagebox.askyesno(
                    "Confirm Import",
                    "This will add new events to your database. Duplicate events (same Event ID and Platform) will be ignored.\n\nContinue?",
                )

                if result:
                    imported_count = self.db.import_events_from_json(filename)

                    messagebox.showinfo(
                        "Import Successful",
                        f"Successfully imported {imported_count} new events!",
                    )

                    # Refresh the display
                    self.on_search()

        except Exception as e:
            messagebox.showerror("Import Error", f"Failed to import events: {str(e)}")

    def add_new_event(self):
        """Open dialog to add new event"""
        AddEventDialog(self.root, self.db, self.data_manager, self.on_search)


# export_manager.py


class ExportManager:
    @staticmethod
    def export_to_json(events, filename=None):
        """Export events to JSON format"""
        if not filename:
            filename = f"security_events_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        with open(filename, "w") as f:
            json.dump(events, f, indent=2)

        return filename

    @staticmethod
    def export_to_csv(events, filename=None):
        """Export events to CSV format"""
        if not filename:
            filename = (
                f"security_events_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            )

        if events:
            fieldnames = [
                "event_id",
                "event_title",
                "platform",
                "category",
                "severity",
                "description",
            ]

            with open(filename, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()

                for event in events:
                    # Create a simplified version for CSV
                    simplified = {field: event.get(field, "") for field in fieldnames}
                    writer.writerow(simplified)

        return filename
