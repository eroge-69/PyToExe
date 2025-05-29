# cook your dish here
import tkinter as tk
from tkinter import messagebox, scrolledtext, filedialog
import pandas as pd
from azure.devops.connection import Connection
from azure.devops.exceptions import AzureDevOpsServiceError
from msrest.authentication import BasicAuthentication
import os
from cryptography.fernet import Fernet

TOKEN_FILE = os.path.join(os.getcwd(), ".token.enc")
KEY_FILE = os.path.join(os.getcwd(), "key.key")

class AzureDevOpsApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Azure DevOps Task Assigner")

        self.api_token = None
        self.encryption_key = self.load_or_generate_key()
        self.excel_files = {}  # Dictionary to store SR ID and corresponding Excel file paths

        self.build_ui()
        self.load_token()

    def build_ui(self):
        tk.Label(self.root, text="Personal Access Token:").grid(row=0, column=0, sticky='w')
        self.token_entry = tk.Entry(self.root, width=60, show="*")
        self.token_entry.grid(row=0, column=1, padx=5, pady=5)

        # Frame for SR entries
        self.sr_frame = tk.Frame(self.root)
        self.sr_frame.grid(row=1, column=0, columnspan=2, sticky='ew', padx=5, pady=5)
        
        # Scrollable frame for multiple SR entries
        self.sr_canvas = tk.Canvas(self.sr_frame)
        self.scrollbar = tk.Scrollbar(self.sr_frame, orient="vertical", command=self.sr_canvas.yview)
        self.scrollable_frame = tk.Frame(self.sr_canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.sr_canvas.configure(
                scrollregion=self.sr_canvas.bbox("all")
            )
        )
        
        self.sr_canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.sr_canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.sr_canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        
        # Add initial SR entry
        self.sr_entries = []
        self.add_sr_entry()

        # Button to add more SR entries
        self.add_sr_button = tk.Button(self.root, text="Add Another SR", command=self.add_sr_entry)
        self.add_sr_button.grid(row=2, column=0, columnspan=2, pady=5)

        self.token_output = tk.Label(self.root, text="", fg="green")
        self.token_output.grid(row=3, column=1, sticky='w', padx=5)

        button_frame = tk.Frame(self.root)
        button_frame.grid(row=4, column=1, sticky='w', padx=5)

        tk.Button(button_frame, text="Save Token", command=self.save_token).grid(row=0, column=0, padx=5)
        tk.Button(button_frame, text="Delete Token", command=self.delete_token).grid(row=0, column=1, padx=5)
        tk.Button(button_frame, text="Run Assignment", command=self.on_run).grid(row=0, column=2, padx=5)

        self.log_output = scrolledtext.ScrolledText(self.root, width=100, height=25)
        self.log_output.grid(row=5, column=0, columnspan=2, padx=10, pady=10)

    def add_sr_entry(self):
        entry_frame = tk.Frame(self.scrollable_frame)
        entry_frame.pack(fill='x', pady=2)
        
        tk.Label(entry_frame, text="SR ID:").pack(side='left', padx=(0, 5))
        
        srid_entry = tk.Entry(entry_frame, width=15)
        srid_entry.pack(side='left', padx=(0, 10))
        
        tk.Label(entry_frame, text="Excel File:").pack(side='left', padx=(0, 5))
        
        excel_path_entry = tk.Entry(entry_frame, width=40)
        excel_path_entry.pack(side='left', padx=(0, 5))
        
        browse_button = tk.Button(entry_frame, text="Browse", 
                                command=lambda: self.browse_excel_file(excel_path_entry))
        browse_button.pack(side='left')
        
        remove_button = tk.Button(entry_frame, text="Remove", 
                                command=lambda: self.remove_sr_entry(entry_frame))
        remove_button.pack(side='left', padx=(5, 0))
        
        self.sr_entries.append((srid_entry, excel_path_entry))

    def browse_excel_file(self, entry_widget):
        filename = filedialog.askopenfilename(
            title="Select Excel File",
            filetypes=(("Excel files", "*.xlsx *.xls"), ("All files", "*.*"))
        )
        if filename:
            entry_widget.delete(0, tk.END)
            entry_widget.insert(0, filename)

    def remove_sr_entry(self, frame):
        # Find and remove the entry from our list
        for i, (srid_entry, excel_entry) in enumerate(self.sr_entries):
            if srid_entry.master == frame:
                self.sr_entries.pop(i)
                break
        frame.destroy()

    def on_run(self):
        token = self.token_entry.get() or self.api_token
        
        if not token:
            messagebox.showerror("Input Error", "Please provide a Token.")
            return
            
        if not self.sr_entries:
            messagebox.showerror("Input Error", "Please add at least one SR entry.")
            return

        # Validate all entries
        valid_entries = []
        for srid_entry, excel_entry in self.sr_entries:
            sr_id = srid_entry.get().strip()
            excel_path = excel_entry.get().strip()
            
            if not sr_id:
                messagebox.showerror("Input Error", "All SR IDs must be provided.")
                return
                
            if not excel_path:
                messagebox.showerror("Input Error", f"Excel file for SR {sr_id} must be provided.")
                return
                
            if not os.path.exists(excel_path):
                messagebox.showerror("Input Error", f"Excel file for SR {sr_id} does not exist: {excel_path}")
                return
                
            valid_entries.append((sr_id, excel_path))

        self.log_output.delete('1.0', tk.END)
        
        # Process each SR
        for sr_id, excel_path in valid_entries:
            self.log_output.insert(tk.END, f"\n=== Processing SR {sr_id} ===\n")
            self.run_assignment(token, sr_id, excel_path)

    def run_assignment(self, token, sr_id, excel_path):
        organization_url = "https://dev.azure.com/GlobalCollaborationService"
        project_name = "Global Collaboration Service Project"
        credentials = BasicAuthentication('', token)

        try:
            connection = Connection(base_url=organization_url, creds=credentials)
            work_item_client = connection.clients.get_work_item_tracking_client()
            sr_item = work_item_client.get_work_item(int(sr_id), project=project_name, expand='relations')

            assigned_ppl = self.read_excel_tab(excel_path, sr_id)

            tasksList = [rel.url.split("/")[-1] for rel in sr_item.relations if rel.rel == "System.LinkTypes.Hierarchy-Forward"]

            for task_id in sorted(tasksList):
                try:
                    task = work_item_client.get_work_item(task_id, fields=['System.Title', 'System.State'])
                    title = task.fields['System.Title']
                    state = task.fields['System.State']

                    for mapping in assigned_ppl:
                        lang_scope = mapping['task']
                        email = mapping['assignee']
                        expected_title = f"[TEST EXECUTION]: {lang_scope}: SR#{sr_id}"

                        if expected_title in title:
                            self.log_output.insert(tk.END, f"Assigning task '{title}' (ID {task_id}) to {email}\n")
                            update_payload = [{"op": "add", "path": "/fields/System.AssignedTo", "value": email}]
                            if state == 'New':
                                update_payload.append({"op": "replace", "path": "/fields/System.State", "value": 'Active'})
                            work_item_client.update_work_item(update_payload, task_id)
                            break
                except AzureDevOpsServiceError as e:
                    self.log_output.insert(tk.END, f"❌ Failed to assign task ID {task_id}: {e.message}, task {lang_scope} with email {email}\n")
                except Exception as e:
                    self.log_output.insert(tk.END, f"⚠️ Unexpected error on task ID {task_id}: {e}\n")

            self.log_output.insert(tk.END, f"✅ Assignment complete for SR {sr_id}.\n")

        except Exception as e:
            self.log_output.insert(tk.END, f"Connection or API error for SR {sr_id}: {e}\n")

    def read_excel_tab(self, filename, tab_start_number):
        try:
            xl = pd.ExcelFile(filename)
            sheet_name = next((s for s in xl.sheet_names if str(s).startswith(str(tab_start_number))), None)
            if not sheet_name:
                self.log_output.insert(tk.END, f"No sheet starts with '{tab_start_number}' in {filename}\n")
                return []

            df = xl.parse(sheet_name, header=None)
            return [{'task': str(row[0]).strip(), 'assignee': str(row[4]).replace('\xa0', '').strip()}
                    for idx, row in df.iterrows() if idx > 0 and pd.notna(row[0]) and pd.notna(row[4])]
        except Exception as e:
            self.log_output.insert(tk.END, f"Error reading Excel {filename}: {e}\n")
            return []

    def save_token(self):
        token = self.token_entry.get()
        if token:
            self.api_token = token
            self.token_output.config(text="Token saved securely.")
            self.save_token_to_file(token)
        else:
            messagebox.showwarning("Warning", "Token cannot be empty!")

    def delete_token(self):
        self.api_token = None
        self.token_entry.delete(0, tk.END)
        self.token_output.config(text="Token deleted.")
        self.delete_token_file()

    def save_token_to_file(self, token):
        try:
            fernet = Fernet(self.encryption_key)
            encrypted_token = fernet.encrypt(token.encode())
            with open(TOKEN_FILE, "wb") as f:
                f.write(encrypted_token)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save token: {e}")

    def load_token(self):
        if os.path.exists(TOKEN_FILE):
            try:
                with open(TOKEN_FILE, "rb") as f:
                    encrypted_token = f.read()
                    fernet = Fernet(self.encryption_key)
                    self.api_token = fernet.decrypt(encrypted_token).decode()
                    self.token_entry.insert(0, self.api_token)
                    self.token_output.config(text="Token loaded.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load token: {e}")

    def delete_token_file(self):
        if os.path.exists(TOKEN_FILE):
            try:
                os.remove(TOKEN_FILE)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete token file: {e}")

    def load_or_generate_key(self):
        if os.path.exists(KEY_FILE):
            try:
                with open(KEY_FILE, "rb") as f:
                    return f.read()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load encryption key: {e}")
        key = Fernet.generate_key()
        try:
            with open(KEY_FILE, "wb") as f:
                f.write(key)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save encryption key: {e}")
        return key

if __name__ == "__main__":
    root = tk.Tk()
    app = AzureDevOpsApp(root)
    root.mainloop()