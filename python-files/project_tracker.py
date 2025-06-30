import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import json
from datetime import datetime
import os

class ProjectRevisionApp:
    def __init__(self, master):
        self.master = master
        master.title("Project Revision Tracker")
        master.geometry("800x700") # Set initial window size

        # Define the path for the local data file
        self.data_file = "projects_data.json"
        self.projects = self.load_projects() # Load projects from file

        self.current_project_id = None # To track which project is being edited/revisied

        # --- Styles (basic ttk styling) ---
        style = ttk.Style()
        style.theme_use('clam') # Use 'clam' theme for a more modern look
        style.configure('TFrame', background='#f0f4f8')
        style.configure('TLabel', background='#f0f4f8', foreground='#333333', font=('Inter', 10))
        style.configure('TButton', font=('Inter', 10, 'bold'), padding=8, background='#4c51bf', foreground='white')
        style.map('TButton', background=[('active', '#5a62d3')])
        style.configure('TEntry', padding=5)
        style.configure('TText', padding=5)
        style.configure('TCombobox', padding=5)
        style.configure('Treeview.Heading', font=('Inter', 10, 'bold'))
        style.configure('Treeview', font=('Inter', 9))


        # --- Main Layout ---
        # Frame for Project Input
        self.input_frame = ttk.Frame(master, padding="15", relief="groove", borderwidth=2)
        self.input_frame.pack(fill=tk.X, padx=15, pady=15)

        ttk.Label(self.input_frame, text="Create New Project / Revision", font=('Inter', 14, 'bold'), foreground='#4c51bf').grid(row=0, column=0, columnspan=2, pady=(0, 10))

        # Project Name Input
        ttk.Label(self.input_frame, text="Project Name:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.project_name_entry = ttk.Entry(self.input_frame, width=40)
        self.project_name_entry.grid(row=1, column=1, sticky=tk.EW, pady=5)

        # Revision Date Input
        ttk.Label(self.input_frame, text="Revision Date (YYYY-MM-DD):").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.revision_date_entry = ttk.Entry(self.input_frame, width=40)
        self.revision_date_entry.insert(0, datetime.now().strftime("%Y-%m-%d")) # Default to today
        self.revision_date_entry.grid(row=2, column=1, sticky=tk.EW, pady=5)

        # Author Input
        ttk.Label(self.input_frame, text="Author:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.author_entry = ttk.Entry(self.input_frame, width=40)
        self.author_entry.grid(row=3, column=1, sticky=tk.EW, pady=5)

        # Release Notes Input
        ttk.Label(self.input_frame, text="Release Notes:").grid(row=4, column=0, sticky=tk.NW, pady=5)
        self.release_notes_text = tk.Text(self.input_frame, height=5, width=40, wrap=tk.WORD)
        self.release_notes_text.grid(row=4, column=1, sticky=tk.EW, pady=5)

        # Buttons for Project Input
        self.save_button = ttk.Button(self.input_frame, text="Create Project (First Revision)", command=self.save_project)
        self.save_button.grid(row=5, column=0, columnspan=2, pady=10, sticky=tk.EW)

        self.cancel_edit_button = ttk.Button(self.input_frame, text="Cancel Editing", command=self.cancel_editing)
        self.cancel_edit_button.grid(row=6, column=0, columnspan=2, pady=5, sticky=tk.EW)
        self.cancel_edit_button.grid_remove() # Hide initially

        self.input_frame.columnconfigure(1, weight=1) # Allow second column to expand

        # --- Project List Frame ---
        self.list_frame = ttk.Frame(master, padding="15", relief="groove", borderwidth=2)
        self.list_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

        ttk.Label(self.list_frame, text="Your Projects", font=('Inter', 14, 'bold'), foreground='#4c51bf').pack(pady=(0, 10))

        # Treeview to display projects
        self.tree = ttk.Treeview(self.list_frame, columns=("Name", "Latest Revision Date", "Author", "Last Updated"), show="headings")
        self.tree.heading("Name", text="Project Name")
        self.tree.heading("Latest Revision Date", text="Rev. Date")
        self.tree.heading("Author", text="Author")
        self.tree.heading("Last Updated", text="Last Updated")

        # Set column widths
        self.tree.column("Name", width=200, anchor=tk.W)
        self.tree.column("Latest Revision Date", width=120, anchor=tk.CENTER)
        self.tree.column("Author", width=150, anchor=tk.W)
        self.tree.column("Last Updated", width=150, anchor=tk.CENTER)

        self.tree.pack(fill=tk.BOTH, expand=True)

        self.tree.bind("<<TreeviewSelect>>", self.on_project_select)

        # Buttons for Project List actions
        self.action_buttons_frame = ttk.Frame(self.list_frame)
        self.action_buttons_frame.pack(fill=tk.X, pady=10)

        self.new_revision_button = ttk.Button(self.action_buttons_frame, text="Create New Revision", command=self.create_new_revision)
        self.new_revision_button.pack(side=tk.LEFT, padx=5, expand=True)

        self.export_csv_button = ttk.Button(self.action_buttons_frame, text="Export Project to CSV", command=self.export_to_csv)
        self.export_csv_button.pack(side=tk.LEFT, padx=5, expand=True)

        self.delete_button = ttk.Button(self.action_buttons_frame, text="Delete Project", command=self.delete_project)
        self.delete_button.pack(side=tk.LEFT, padx=5, expand=True)

        self.update_project_list() # Populate the treeview on start

    def load_projects(self):
        """Loads projects data from a JSON file."""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Convert string timestamps back to datetime objects for internal use
                    for project in data:
                        if 'createdAt' in project:
                            project['createdAt'] = datetime.fromisoformat(project['createdAt'])
                        if 'lastUpdated' in project:
                            project['lastUpdated'] = datetime.fromisoformat(project['lastUpdated'])
                        if 'revisions' in project:
                            for rev in project['revisions']:
                                if 'timestamp' in rev:
                                    rev['timestamp'] = datetime.fromisoformat(rev['timestamp'])
                    return data
            except json.JSONDecodeError:
                messagebox.showerror("Error", "Could not decode projects_data.json. File might be corrupted. Starting fresh.")
                return []
        return []

    def save_projects(self):
        """Saves projects data to a JSON file."""
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                # Convert datetime objects to ISO format strings for JSON serialization
                serializable_projects = []
                for project in self.projects:
                    p = project.copy()
                    if 'createdAt' in p and isinstance(p['createdAt'], datetime):
                        p['createdAt'] = p['createdAt'].isoformat()
                    if 'lastUpdated' in p and isinstance(p['lastUpdated'], datetime):
                        p['lastUpdated'] = p['lastUpdated'].isoformat()
                    if 'revisions' in p:
                        p['revisions'] = [
                            {**rev, 'timestamp': rev['timestamp'].isoformat()}
                            if isinstance(rev.get('timestamp'), datetime) else rev
                            for rev in p['revisions']
                        ]
                    serializable_projects.append(p)
                json.dump(serializable_projects, f, indent=4)
        except Exception as e:
            messagebox.showerror("Error", f"Could not save projects data: {e}")

    def update_project_list(self):
        """Clears and repopulates the Treeview with current project data."""
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Sort projects by lastUpdated in descending order
        sorted_projects = sorted(self.projects, key=lambda p: p['lastUpdated'], reverse=True)

        for project in sorted_projects:
            latest_revision_date = project.get('revisionDate', 'N/A')
            latest_author = project.get('author', 'N/A')
            last_updated_display = project['lastUpdated'].strftime("%Y-%m-%d %H:%M") if isinstance(project['lastUpdated'], datetime) else 'N/A'

            self.tree.insert("", tk.END, iid=project['id'],
                             values=(project['name'], latest_revision_date, latest_author, last_updated_display))

    def clear_form(self):
        """Clears the input form fields."""
        self.project_name_entry.delete(0, tk.END)
        self.project_name_entry.config(state=tk.NORMAL) # Enable project name for new project
        self.revision_date_entry.delete(0, tk.END)
        self.revision_date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.author_entry.delete(0, tk.END)
        self.release_notes_text.delete(1.0, tk.END)
        self.save_button.config(text="Create Project (First Revision)")
        self.cancel_edit_button.grid_remove()
        self.current_project_id = None

    def save_project(self):
        """Handles saving a new project or a new revision to an existing project."""
        name = self.project_name_entry.get().strip()
        revision_date = self.revision_date_entry.get().strip()
        author = self.author_entry.get().strip()
        release_notes = self.release_notes_text.get(1.0, tk.END).strip()

        if not name or not revision_date or not author or not release_notes:
            messagebox.showwarning("Input Error", "All fields (Project Name, Revision Date, Author, Release Notes) are required.")
            return

        # Basic date format validation
        try:
            datetime.strptime(revision_date, "%Y-%m-%d")
        except ValueError:
            messagebox.showwarning("Input Error", "Revision Date must be in YYYY-MM-DD format.")
            return

        new_revision = {
            "timestamp": datetime.now(), # When this revision entry was saved
            "revisionDate": revision_date,
            "releaseNotes": release_notes,
            "author": author,
            "name": name # Store project name with revision for history consistency
        }

        if self.current_project_id:
            # Update existing project (add new revision)
            project_found = False
            for project in self.projects:
                if project['id'] == self.current_project_id:
                    project['revisions'].append(new_revision)
                    project['releaseNotes'] = release_notes # Update latest details
                    project['revisionDate'] = revision_date
                    project['author'] = author
                    project['lastUpdated'] = datetime.now()
                    project_found = True
                    break
            if project_found:
                messagebox.showinfo("Success", f"New revision added to project '{name}'.")
            else:
                messagebox.showerror("Error", "Could not find project to update.")
        else:
            # Create new project
            new_project_id = str(len(self.projects) + 1) # Simple ID generation
            new_project = {
                "id": new_project_id,
                "name": name,
                "releaseNotes": release_notes,
                "revisionDate": revision_date,
                "author": author,
                "revisions": [new_revision],
                "createdAt": datetime.now(),
                "lastUpdated": datetime.now()
            }
            self.projects.append(new_project)
            messagebox.showinfo("Success", f"New project '{name}' created.")

        self.save_projects()
        self.update_project_list()
        self.clear_form()

    def create_new_revision(self):
        """Pre-fills the form to add a new revision to a selected project."""
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Selection Error", "Please select a project from the list to create a new revision.")
            return

        project_id = self.tree.item(selected_item[0], 'iid')
        project_to_edit = next((p for p in self.projects if p['id'] == project_id), None)

        if project_to_edit:
            self.clear_form() # Clear any previous input
            self.project_name_entry.insert(0, project_to_edit['name'])
            self.project_name_entry.config(state=tk.DISABLED) # Disable name editing
            self.revision_date_entry.insert(0, datetime.now().strftime("%Y-%m-%d")) # Default to today's date for new revision
            self.author_entry.insert(0, project_to_edit['author']) # Pre-fill with last author
            # release_notes_text remains empty for new notes
            self.save_button.config(text=f"Save New Revision for '{project_to_edit['name']}'")
            self.cancel_edit_button.grid() # Show cancel button
            self.current_project_id = project_id
        else:
            messagebox.showerror("Error", "Selected project not found.")

    def cancel_editing(self):
        """Cancels the current editing mode and clears the form."""
        self.clear_form()
        messagebox.showinfo("Cancelled", "Editing cancelled. Form cleared.")

    def delete_project(self):
        """Deletes the selected project."""
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Selection Error", "Please select a project from the list to delete.")
            return

        project_id = self.tree.item(selected_item[0], 'iid')
        project_name = self.tree.item(selected_item[0], 'values')[0]

        if messagebox.askyesno("Confirm Deletion", f"Are you sure you want to delete project '{project_name}' and all its revisions? This action cannot be undone."):
            self.projects = [p for p in self.projects if p['id'] != project_id]
            self.save_projects()
            self.update_project_list()
            self.clear_form()
            messagebox.showinfo("Success", f"Project '{project_name}' deleted.")

    def on_project_select(self, event):
        """Displays the revision history for the selected project (in a new window)."""
        selected_item = self.tree.selection()
        if not selected_item:
            return

        project_id = self.tree.item(selected_item[0], 'iid')
        project = next((p for p in self.projects if p['id'] == project_id), None)

        if project:
            self.show_revision_history(project)

    def show_revision_history(self, project):
        """Opens a new window to display the revision history of a project."""
        history_window = tk.Toplevel(self.master)
        history_window.title(f"Revisions for: {project['name']}")
        history_window.geometry("600x500")
        history_window.transient(self.master) # Make it appear on top of the main window
        history_window.grab_set() # Make it modal

        ttk.Label(history_window, text=f"Revision History for: {project['name']}", font=('Inter', 12, 'bold')).pack(pady=10)

        history_tree = ttk.Treeview(history_window, columns=("Saved On", "Rev. Date", "Author", "Release Notes"), show="headings")
        history_tree.heading("Saved On", text="Saved On")
        history_tree.heading("Rev. Date", text="Rev. Date")
        history_tree.heading("Author", text="Author")
        history_tree.heading("Release Notes", text="Release Notes")

        history_tree.column("Saved On", width=150, anchor=tk.CENTER)
        history_tree.column("Rev. Date", width=100, anchor=tk.CENTER)
        history_tree.column("Author", width=120, anchor=tk.W)
        history_tree.column("Release Notes", width=250, anchor=tk.W)

        # Sort revisions by timestamp (most recent first)
        sorted_revisions = sorted(project.get('revisions', []), key=lambda rev: rev['timestamp'], reverse=True)

        for rev in sorted_revisions:
            saved_on = rev['timestamp'].strftime("%Y-%m-%d %H:%M") if isinstance(rev['timestamp'], datetime) else 'N/A'
            history_tree.insert("", tk.END, values=(
                saved_on,
                rev.get('revisionDate', 'N/A'),
                rev.get('author', 'N/A'),
                rev.get('releaseNotes', 'N/A')
            ))
        history_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        close_button = ttk.Button(history_window, text="Close", command=history_window.destroy)
        close_button.pack(pady=10)

    def export_to_csv(self):
        """Exports the selected project's data and all revisions to a CSV file."""
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Selection Error", "Please select a project from the list to export.")
            return

        project_id = self.tree.item(selected_item[0], 'iid')
        project = next((p for p in self.projects if p['id'] == project_id), None)

        if not project:
            messagebox.showerror("Error", "Selected project not found for export.")
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            initialfile=f"{project['name']}_revisions.csv"
        )
        if not file_path:
            return # User cancelled

        try:
            with open(file_path, 'w', newline='', encoding='utf-8') as f:
                # CSV Header
                common_headers = ["Project ID", "Project Name", "Latest Release Notes", "Latest Revision Date", "Latest Author", "Created At", "Last Updated"]
                revision_headers = ["Revision Saved On", "Revision Date (User)", "Revision Release Notes", "Revision Author"]
                f.write(",".join(common_headers + revision_headers) + "\n")

                # Escape double quotes and handle commas in CSV
                def escape_csv(value):
                    if value is None:
                        return ""
                    value_str = str(value)
                    # Corrected line: Using chr(34) for double quotes to avoid f-string syntax issues
                    return f'"{value_str.replace(chr(34), chr(34) * 2)}"'

                # Project's latest data
                created_at = project['createdAt'].strftime("%Y-%m-%d %H:%M") if isinstance(project['createdAt'], datetime) else 'N/A'
                last_updated = project['lastUpdated'].strftime("%Y-%m-%d %H:%M") if isinstance(project['lastUpdated'], datetime) else 'N/A'

                project_data_row = [
                    escape_csv(project.get('id')),
                    escape_csv(project.get('name')),
                    escape_csv(project.get('releaseNotes')),
                    escape_csv(project.get('revisionDate')),
                    escape_csv(project.get('author')),
                    escape_csv(created_at),
                    escape_csv(last_updated)
                ]

                # Add revisions
                if project.get('revisions'):
                    for i, rev in enumerate(project['revisions']):
                        rev_saved_on = rev['timestamp'].strftime("%Y-%m-%d %H:%M") if isinstance(rev['timestamp'], datetime) else 'N/A'
                        revision_data_row = [
                            escape_csv(rev_saved_on),
                            escape_csv(rev.get('revisionDate')),
                            escape_csv(rev.get('releaseNotes')),
                            escape_csv(rev.get('author'))
                        ]
                        if i == 0:
                            # First revision, append to project data row
                            f.write(",".join(project_data_row + revision_data_row) + "\n")
                        else:
                            # Subsequent revisions, prepend with empty common fields
                            f.write(",".join([""] * len(common_headers) + revision_data_row) + "\n")
                else:
                    # No revisions, just write the project data row with empty revision fields
                    f.write(",".join(project_data_row + [""] * len(revision_headers)) + "\n")

            messagebox.showinfo("Export Successful", f"Project '{project['name']}' exported to:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export project: {e}")

# Main part of the script
if __name__ == "__main__":
    root = tk.Tk()
    app = ProjectRevisionApp(root)
    root.mainloop()
