import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import datetime
import uuid
import json
import os
import csv

DATA_FILE = "jobs.json"
PRIMARY_COLOR = "#0A2647"
SECONDARY_COLOR = "#144272"
TEXT_COLOR = "white"
BG_COLOR = "#EAF2F8"



class Job:
    def __init__(self, title, submitted_by, location, date_submitted, issue_description, job_id=None):
        self.job_id = job_id if job_id else str(uuid.uuid4())[:8]
        self.title = title
        self.submitted_by = submitted_by
        self.location = location
        self.date_submitted = date_submitted
        self.issue_description = issue_description

    def to_dict(self):
        return {
            "Job ID": self.job_id,
            "Title": self.title,
            "Submitted By": self.submitted_by,
            "Location": self.location,
            "Date Submitted": self.date_submitted.strftime("%Y-%m-%d"),
            "Issue Description": self.issue_description
        }

    @staticmethod
    def from_dict(data):
        return Job(
            title=data["Title"],
            submitted_by=data["Submitted By"],
            location=data["Location"],
            date_submitted=datetime.datetime.strptime(data["Date Submitted"], "%Y-%m-%d").date(),
            issue_description=data["Issue Description"],
            job_id=data["Job ID"]
        )

class JobDatabase:
    def __init__(self):
        self.jobs = []
        self.load_jobs()

    def add_job(self, job):
        self.jobs.append(job)
        self.save_jobs()

    def delete_job(self, job_id):
        self.jobs = [job for job in self.jobs if job.job_id != job_id]
        self.save_jobs()

    def update_job(self, updated_job):
        for i, job in enumerate(self.jobs):
            if job.job_id == updated_job.job_id:
                self.jobs[i] = updated_job
                break
        self.save_jobs()

    def load_jobs(self):
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'r') as f:
                data = json.load(f)
                self.jobs = [Job.from_dict(item) for item in data]

    def save_jobs(self):
        with open(DATA_FILE, 'w') as f:
            json.dump([job.to_dict() for job in self.jobs], f, indent=4)

class JobFormPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.current_job = None
        self.entries = {}

        fields = ["Title", "Submitted By", "Location", "Date"]
        for field in fields:
            row = tk.Frame(self)
            row.pack(fill="x", padx=20, pady=5)
            tk.Label(row, text=field, width=15).pack(side="left")
            entry = tk.Entry(row)
            entry.pack(side="left", fill="x", expand=True)
            self.entries[field] = entry

        row_desc = tk.Frame(self)
        row_desc.pack(fill="both", padx=20, pady=5, expand=True)
        tk.Label(row_desc, text="Description", width=15).pack(anchor="w")
        self.entries["Issue Description"] = tk.Text(row_desc, height=10)
        self.entries["Issue Description"].pack(fill="both", expand=True)

        btn_frame = tk.Frame(self)
        btn_frame.pack(fill="x", pady=10)
        tk.Button(btn_frame, text="Save", command=self.save_job).pack(side="left", padx=10)
        tk.Button(btn_frame, text="Back", command=lambda: controller.show_frame("HomePage")).pack(side="right", padx=10)

    def load_job(self, job):
        self.current_job = job
        self.clear_form()
        if job:
            self.entries["Title"].insert(0, job.title)
            self.entries["Submitted By"].insert(0, job.submitted_by)
            self.entries["Location"].insert(0, job.location)
            self.entries["Date"].insert(0, job.date_submitted.strftime("%Y-%m-%d"))
            self.entries["Issue Description"].insert("1.0", job.issue_description)

    def save_job(self):
        try:
            date = datetime.datetime.strptime(self.entries["Date"].get(), "%Y-%m-%d").date()
        except ValueError:
            tk.messagebox.showerror("Invalid Date", "Date must be in YYYY-MM-DD format.")
            return

        if self.current_job:
            self.current_job.title = self.entries["Title"].get()
            self.current_job.submitted_by = self.entries["Submitted By"].get()
            self.current_job.location = self.entries["Location"].get()
            self.current_job.date_submitted = date
            self.current_job.issue_description = self.entries["Issue Description"].get("1.0", "end").strip()
            self.controller.db.update_job(self.current_job)
        else:
            new_job = Job(
                title=self.entries["Title"].get(),
                submitted_by=self.entries["Submitted By"].get(),
                location=self.entries["Location"].get(),
                date_submitted=date,
                issue_description=self.entries["Issue Description"].get("1.0", "end").strip()
            )
            self.controller.db.add_job(new_job)

        self.controller.show_frame("HomePage")

    def clear_form(self):
        for entry in self.entries.values():
            if isinstance(entry, tk.Entry):
                entry.delete(0, "end")
            elif isinstance(entry, tk.Text):
                entry.delete("1.0", "end")

class JobDetailPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG_COLOR)
        self.controller = controller
        self.labels = {}
        fields = ["Title", "Submitted By", "Location", "Date Submitted", "Issue Description"]

        header = tk.Label(self, text="Job Details", font=("Helvetica", 20, "bold"), fg=TEXT_COLOR, bg=PRIMARY_COLOR)
        header.pack(fill="x", pady=10)

        for field in fields:
            frame = tk.Frame(self, bg=BG_COLOR)
            frame.pack(fill="x", padx=20, pady=5)
            label = tk.Label(frame, text=f"{field}:", width=15, anchor="w", font=("Helvetica", 12, "bold"), bg=BG_COLOR)
            label.pack(side="left")
            value = tk.Label(frame, text="", anchor="w", wraplength=800, justify="left", bg=BG_COLOR, font=("Helvetica", 12))
            value.pack(side="left", fill="x", expand=True)
            self.labels[field] = value

        btn = tk.Button(self, text="Back", bg=SECONDARY_COLOR, fg=TEXT_COLOR, font=("Helvetica", 10), command=lambda: controller.show_frame("HomePage"))
        btn.pack(pady=20)

    def load_job(self, job):
        self.labels["Title"].config(text=job.title)
        self.labels["Submitted By"].config(text=job.submitted_by)
        self.labels["Location"].config(text=job.location)
        self.labels["Date Submitted"].config(text=job.date_submitted.strftime("%Y-%m-%d"))
        self.labels["Issue Description"].config(text=job.issue_description)

class HomePage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG_COLOR)
        self.controller = controller
        self.sort_column = "Title"
        self.sort_reverse = False

        search_frame = tk.Frame(self, bg=BG_COLOR)
        search_frame.pack(fill="x")

        self.search_category = ttk.Combobox(search_frame, values=["All", "Title", "Submitted By", "Location", "Date"], state="readonly")
        self.search_category.set("All")
        self.search_category.pack(side="left", padx=5, pady=5)

        self.search_entry = tk.Entry(search_frame)
        self.search_entry.pack(side="left", fill="x", expand=True, padx=5, pady=5)
        tk.Button(search_frame, text="Search", bg=SECONDARY_COLOR, fg=TEXT_COLOR, command=self.quick_search).pack(side="left", padx=5)
        tk.Button(search_frame, text="Export to CSV", command=self.export_csv, bg=SECONDARY_COLOR, fg=TEXT_COLOR).pack(side="left", padx=5)

        self.tree = ttk.Treeview(self, columns=("ID", "Title", "Submitted By", "Location", "Date"), show='headings')
        for col in self.tree["columns"]:
            self.tree.heading(col, text=col, command=lambda _col=col: self.sort_by_column(_col))
            self.tree.column(col, anchor="center", width=150)
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)

        self.tree.configure(style="Treeview")

        btn_frame = tk.Frame(self, bg=BG_COLOR)
        btn_frame.pack(fill="x", pady=5)
        tk.Button(btn_frame, text="Add Job", command=lambda: controller.show_frame("JobFormPage"), bg=PRIMARY_COLOR, fg=TEXT_COLOR).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Edit Job", command=self.edit_job, bg=PRIMARY_COLOR, fg=TEXT_COLOR).pack(side="left", padx=5)
        tk.Button(btn_frame, text="View Job", command=self.view_job, bg=PRIMARY_COLOR, fg=TEXT_COLOR).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Delete Job", command=self.delete_job, bg=PRIMARY_COLOR, fg=TEXT_COLOR).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Refresh", command=self.refresh, bg=SECONDARY_COLOR, fg=TEXT_COLOR).pack(side="right", padx=5)

    def refresh(self):
        self.tree.delete(*self.tree.get_children())
        sorted_jobs = sorted(self.controller.db.jobs, key=lambda job: getattr(job, self.sort_column.lower().replace(" ", "_")), reverse=self.sort_reverse)
        for job in sorted_jobs:
            self.tree.insert('', 'end', values=(job.job_id, job.title, job.submitted_by, job.location, job.date_submitted.strftime("%Y-%m-%d")))

    def sort_by_column(self, col):
        self.sort_column = col
        self.sort_reverse = not self.sort_reverse
        self.refresh()

    def quick_search(self):
        query = self.search_entry.get().strip().lower()
        category = self.search_category.get()

        def match(job):
            if category == "All":
                return (query in job.title.lower() or
                        query in job.submitted_by.lower() or
                        query in job.location.lower() or
                        query in job.date_submitted.strftime("%Y-%m-%d").lower())
            elif category == "Title":
                return query in job.title.lower()
            elif category == "Submitted By":
                return query in job.submitted_by.lower()
            elif category == "Location":
                return query in job.location.lower()
            elif category == "Date":
                return query in job.date_submitted.strftime("%Y-%m-%d").lower()
            return False

        results = [job for job in self.controller.db.jobs if match(job)]

        self.tree.delete(*self.tree.get_children())
        for job in results:
            self.tree.insert('', 'end', values=(job.job_id, job.title, job.submitted_by, job.location, job.date_submitted.strftime("%Y-%m-%d")))

    def get_selected_job_id(self):
        selected = self.tree.focus()
        if not selected:
            return None
        return self.tree.item(selected)['values'][0]

    def edit_job(self):
        job_id = self.get_selected_job_id()
        if job_id:
            job = self.controller.get_job_by_id(job_id)
            self.controller.frames["JobFormPage"].load_job(job)
            self.controller.show_frame("JobFormPage")

    def view_job(self):
        job_id = self.get_selected_job_id()
        if job_id:
            job = self.controller.get_job_by_id(job_id)
            self.controller.frames["JobDetailPage"].load_job(job)
            self.controller.show_frame("JobDetailPage")

    def delete_job(self):
        job_id = self.get_selected_job_id()
        if job_id:
            confirm = messagebox.askyesno("Delete Job", "Are you sure you want to delete this job?")
            if confirm:
                self.controller.db.delete_job(job_id)
                self.refresh()

    def export_csv(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if not file_path:
            return
        with open(file_path, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Job ID", "Title", "Submitted By", "Location", "Date Submitted", "Issue Description"])
            for job in self.controller.db.jobs:
                writer.writerow([job.job_id, job.title, job.submitted_by, job.location, job.date_submitted.strftime("%Y-%m-%d"), job.issue_description])

class JobApp:
    def __init__(self, root):
        self.db = JobDatabase()
        self.root = root
        self.root.title("IT Technician Job Tracker")
        self.root.state('zoomed')

        self.container = tk.Frame(self.root, bg=BG_COLOR)
        self.container.pack(fill="both", expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for F in (HomePage, JobFormPage, JobDetailPage):
            frame = F(parent=self.container, controller=self)
            self.frames[F.__name__] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("HomePage")

    def show_frame(self, name):
        frame = self.frames[name]
        frame.tkraise()
        if hasattr(frame, "refresh"):
            frame.refresh()

    def get_job_by_id(self, job_id):
        return next((j for j in self.db.jobs if j.job_id == job_id), None)

if __name__ == '__main__':
    root = tk.Tk()

    style = ttk.Style(root)
    style.configure("Treeview",
                    font=("Helvetica", 10),
                    rowheight=25,
                    fieldbackground=BG_COLOR)
    style.configure("Treeview.Heading",
                    font=("Helvetica", 11, "bold"))
    style.map('Treeview', background=[('selected', SECONDARY_COLOR)], foreground=[('selected', TEXT_COLOR)])

    app = JobApp(root)
    root.mainloop()
