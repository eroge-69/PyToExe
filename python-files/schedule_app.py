import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
import json
import os
from datetime import datetime, timedelta

EMPLOYEE_COUNT = 4

DAYS = [
    "Δευτέρα",    # Monday
    "Τρίτη",      # Tuesday
    "Τετάρτη",    # Wednesday
    "Πέμπτη",     # Thursday
    "Παρασκευή",  # Friday
    "Σάββατο",    # Saturday
    "Κυριακή"     # Sunday
]
EVENING_CLOSED_DAYS = {"Δευτέρα", "Τετάρτη", "Σάββατο"}

REST_PATTERNS = [
    {"Δευτέρα": ["AM", "PM"]},  # Rest on Monday
    {"Τετάρτη": ["AM", "PM"]},  # Rest on Wednesday
    {"Πέμπτη": ["PM"], "Παρασκευή": ["PM"]},  # Rest on Thu/Fri evening
    {"Σάββατο": ["AM", "PM"]},  # Rest on Saturday
]
SCHEDULE_FILE = "schedule_data.json"

def get_week_index(start_date, current_date):
    delta = (current_date - start_date).days // 7
    return delta % 4

class ScheduleApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Employee Work Schedule Tracker")
        self.start_date = datetime(2025, 6, 16)
        self.current_date = datetime.today()
        self.week_offset = 0

        self.employee_names = [f"Employee {i+1}" for i in range(EMPLOYEE_COUNT)]
        self.create_widgets()
        self.load_data()

    def create_widgets(self):
        top_frame = tk.Frame(self.root)
        top_frame.pack(pady=10)

        self.prev_btn = tk.Button(top_frame, text="<< Προηγούμενη Εβδομάδα", command=self.prev_week)
        self.prev_btn.pack(side=tk.LEFT, padx=5)
        self.next_btn = tk.Button(top_frame, text="Επόμενη Εβδομάδα >>", command=self.next_week)
        self.next_btn.pack(side=tk.LEFT, padx=5)
        self.current_btn = tk.Button(top_frame, text="Τρέχουσα Εβδομάδα", command=self.go_to_current_week)
        self.current_btn.pack(side=tk.LEFT, padx=5)
        self.edit_names_btn = tk.Button(top_frame, text="Αλλαγή Ονομάτων", command=self.edit_names)
        self.edit_names_btn.pack(side=tk.LEFT, padx=5)
        self.save_btn = tk.Button(top_frame, text="Αποθήκευση", command=self.save_data)
        self.save_btn.pack(side=tk.LEFT, padx=5)
        self.load_btn = tk.Button(top_frame, text="Φόρτωση", command=self.load_data)
        self.load_btn.pack(side=tk.LEFT, padx=5)

        self.week_label = tk.Label(self.root, text="", font=("Arial", 14))
        self.week_label.pack(pady=5)

        self.columns = ["Εργαζόμενος"] + DAYS

        self.tree = ttk.Treeview(self.root, columns=self.columns, show="headings", height=EMPLOYEE_COUNT)
        for col in self.columns:
            self.tree.heading(col, text=col)
            if col == "Εργαζόμενος":
                self.tree.column(col, width=140, anchor="center")
            else:
                self.tree.column(col, width=170, anchor="center")
        self.tree.pack(padx=10, pady=10)

        self.tree.bind("<Double-1>", self.edit_cell)

        style = ttk.Style()
        style.configure("Treeview", background="#222831", fieldbackground="#222831", foreground="#eeeeee")
        style.configure("Treeview.Heading", font=("Arial", 10, "bold"), background="#393e46", foreground="#eeeeee")

    def get_current_week_index(self):
        week_start = self.start_date + timedelta(weeks=self.week_offset)
        return get_week_index(self.start_date, week_start)

    def get_week_dates(self):
        week_start = self.start_date + timedelta(weeks=self.week_offset)
        return [week_start + timedelta(days=i) for i in range(7)]

    def update_schedule(self):
        week_start = self.start_date + timedelta(weeks=self.week_offset)
        week_index = self.get_current_week_index()
        week_dates = self.get_week_dates()
        self.week_label.config(
            text=f"Εβδομάδα που ξεκινά {week_dates[0].strftime('%Y-%m-%d')} (Κύκλος {week_index+1}/4)"
        )

        # Update column headers to include the date
        for idx, day in enumerate(DAYS):
            date_str = f"{day} {week_dates[idx].day}"
            self.tree.heading(day, text=date_str)

        for row in self.tree.get_children():
            self.tree.delete(row)

        for i, name in enumerate(self.employee_names):
            rest_pattern_index = (week_index + i) % 4
            rest_days = REST_PATTERNS[rest_pattern_index]
            row = [name]
            for day in DAYS:
                # Πρωινό
                if day == "Κυριακή":
                    am_line = "Κλειστά"
                elif "AM" in rest_days.get(day, []):
                    am_line = "Ρεπό"
                else:
                    am_line = "8:30–14:30"
                # Απόγευμα
                if day == "Κυριακή" or day in EVENING_CLOSED_DAYS:
                    pm_line = "Κλειστά"
                elif "PM" in rest_days.get(day, []):
                    pm_line = "Ρεπό"
                else:
                    pm_line = "18:00–21:00"
                cell_value = f"{am_line} | {pm_line}"
                row.append(cell_value)
            self.tree.insert("", "end", iid=i, values=row, text=name)

    def prev_week(self):
        self.week_offset -= 1
        self.update_schedule()

    def next_week(self):
        self.week_offset += 1
        self.update_schedule()

    def go_to_current_week(self):
        today = datetime.today()
        self.week_offset = (today - self.start_date).days // 7
        self.update_schedule()

    def edit_names(self):
        for i in range(EMPLOYEE_COUNT):
            new_name = simpledialog.askstring("Αλλαγή Ονόματος", f"Όνομα για Εργαζόμενο {i+1}:", initialvalue=self.employee_names[i])
            if new_name:
                self.employee_names[i] = new_name
        self.save_data()
        self.update_schedule()

    def edit_cell(self, event):
        item = self.tree.identify_row(event.y)
        column = self.tree.identify_column(event.x)
        if not item or not column:
            return
        col_index = int(column.replace("#", "")) - 1
        emp_index = int(item)
        if col_index == 0:
            new_name = simpledialog.askstring("Αλλαγή Ονόματος", f"Όνομα για Εργαζόμενο {emp_index+1}:", initialvalue=self.employee_names[emp_index])
            if new_name:
                self.employee_names[emp_index] = new_name
                self.save_data()
                self.update_schedule()
            return
        current_value = self.tree.set(item, self.columns[col_index])
        new_value = simpledialog.askstring("Αλλαγή Κελιού", f"Τιμή για {self.employee_names[emp_index]}, {self.columns[col_index]}:", initialvalue=current_value)
        if new_value:
            self.tree.set(item, self.columns[col_index], new_value)
            self.save_data()

    def save_data(self):
        data = {
            "employee_names": self.employee_names,
            "week_offset": self.week_offset,
        }
        with open(SCHEDULE_FILE, "w") as f:
            json.dump(data, f)
        messagebox.showinfo("Αποθήκευση", "Το πρόγραμμα αποθηκεύτηκε με επιτυχία.")

    def load_data(self):
        if os.path.exists(SCHEDULE_FILE):
            with open(SCHEDULE_FILE, "r") as f:
                data = json.load(f)
                self.employee_names = data.get("employee_names", self.employee_names)
                self.week_offset = data.get("week_offset", 0)
        self.update_schedule()

if __name__ == "__main__":
    root = tk.Tk()
    app = ScheduleApp(root)
    root.mainloop()
