import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3


class StudentApp(tk.Tk):

    def __init__(self, db_name="student_database.db"):
        super().__init__()
        self.title("Student Management System (SQLite)")
        self.geometry("800x500")

        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.setup_table()

        self.create_widgets()
        self.refresh_treeview()

    def setup_table(self):
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            Name TEXT NOT NULL,
            grade TEXT,
            attendence INTEGER
        )""")
        self.conn.commit()

    def create_widgets(self):
        form_frame = ttk.Frame(self, padding=15)
        form_frame.pack(fill="x")
        tree_frame = ttk.Frame(self, padding=(15, 0, 15, 15))
        tree_frame.pack(fill="both", expand=True)

        self.entries = {}
        form_fields = {"Name": "Name:", "Grade": "Grade:", "Attendance": "Attendance (%):"}
        for i, (field, text) in enumerate(form_fields.items()):
            ttk.Label(form_frame, text=text).grid(row=i, column=0, padx=5, pady=5, sticky="w")
            entry = ttk.Entry(form_frame, width=30)
            entry.grid(row=i, column=1, padx=5, pady=5)
            self.entries[field] = entry

        button_frame = ttk.Frame(form_frame)
        button_frame.grid(row=len(form_fields), column=0, columnspan=2, pady=10)
        buttons = {"Add": self.add, "Update": self.update, "Delete": self.delete, "Clear": self.clear_fields}
        for text, command in buttons.items():
            ttk.Button(button_frame, text=text, command=command).pack(side="left", padx=5)

        self.tree = ttk.Treeview(tree_frame, columns=("ID", "Name", "Grade", "Attendance"), show="headings")
        self.tree.heading("ID", text="ID");
        self.tree.column("ID", width=50, anchor="center")
        self.tree.heading("Name", text="Name")
        self.tree.heading("Grade", text="Grade", anchor="center")
        self.tree.heading("Attendance", text="Attendance (%)", anchor="center")
        self.tree.bind("<<TreeviewSelect>>", self.on_item_select)

        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def refresh_treeview(self):
        self.tree.delete(*self.tree.get_children())
        self.cursor.execute("SELECT * FROM students ORDER BY Name")
        for row in self.cursor.fetchall():
            self.tree.insert("", "end", values=row)

    def execute_and_refresh(self, query, params=(), message=""):
        try:
            self.cursor.execute(query, params)
            self.conn.commit()
            self.refresh_treeview()
            self.clear_fields()
            if message:
                messagebox.showinfo("Success", message)
        except Exception as e:
            messagebox.showerror("Database Error", f"An error occurred: {e}")

    def add(self):
        values = [entry.get() for entry in self.entries.values()]
        if not all(values): return messagebox.showerror("Error", "All fields are required.")
        self.execute_and_refresh(
            "INSERT INTO students (Name, grade, attendence) VALUES (?, ?, ?)",
            values, "Student added successfully."
        )

    def update(self):
        selected_id = self.get_selected_id()
        if not selected_id: return
        values = [entry.get() for entry in self.entries.values()]
        values.append(selected_id)  # Add ID for the WHERE clause
        self.execute_and_refresh(
            "UPDATE students SET Name=?, grade=?, attendence=? WHERE id=?",
            values, "Student updated successfully."
        )

    def delete(self):
        selected_id = self.get_selected_id()
        if selected_id and messagebox.askyesno("Confirm", "Delete this student?"):
            self.execute_and_refresh("DELETE FROM students WHERE id=?", (selected_id,), "Student deleted.")

    def on_item_select(self, event):
        selected_id = self.get_selected_id(show_error=False)
        if not selected_id: return
        data = self.tree.item(self.tree.selection()[0])['values']
        self.clear_fields(clear_selection=False)
        self.entries["Name"].insert(0, data[1])
        self.entries["Grade"].insert(0, data[2])
        self.entries["Attendance"].insert(0, data[3])

    def get_selected_id(self, show_error=True):
        selection = self.tree.selection()
        if not selection:
            if show_error: messagebox.showerror("Error", "Please select a student first.")
            return None
        return self.tree.item(selection[0])['values'][0]

    def clear_fields(self, clear_selection=True):
        for entry in self.entries.values(): entry.delete(0, "end")
        if clear_selection and self.tree.selection(): self.tree.selection_remove(self.tree.selection()[0])

    def __del__(self):
        self.conn.close()


if __name__ == "__main__":
    app = StudentApp()
    app.mainloop()