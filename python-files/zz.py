import json
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

try:
    from tkcalendar import DateEntry
except ImportError:
    DateEntry = tk.Entry

# Global data
user_data = {}
equipment_data = []
maintenance_data = []
spare_data = []
msr_data = []
pm_data = []
history_data = []

# Save & Load
def save_data():
    data = {
        "users": user_data,
        "equipment": equipment_data,
        "maintenance": maintenance_data,
        "spare": spare_data,
        "msr": msr_data,
        "pm": pm_data,
        "history": history_data
    }
    with open("cmms_data.json", "w") as f:
        json.dump(data, f)

def load_data():
    global user_data, equipment_data, maintenance_data, spare_data, msr_data, pm_data, history_data
    try:
        with open("cmms_data.json", "r") as f:
            data = json.load(f)
            user_data = data.get("users", {})
            equipment_data = data.get("equipment", [])
            maintenance_data = data.get("maintenance", [])
            spare_data = data.get("spare", [])
            msr_data = data.get("msr", [])
            pm_data = data.get("pm", [])
            history_data = data.get("history", [])
    except FileNotFoundError:
        pass

# Main app window
def main_window():
    root = tk.Tk()
    root.title("CMMS Software")
    root.geometry("1100x650")

    notebook = ttk.Notebook(root)
    notebook.pack(expand=1, fill='both')

    equip_tab = ttk.Frame(notebook)
    maint_tab = ttk.Frame(notebook)
    spare_tab = ttk.Frame(notebook)
    msr_tab = ttk.Frame(notebook)
    pm_tab = ttk.Frame(notebook)
    history_tab = ttk.Frame(notebook)

    notebook.add(equip_tab, text='Equipment')
    notebook.add(maint_tab, text='Maintenance')
    notebook.add(spare_tab, text='Spare Parts')
    notebook.add(msr_tab, text='MSR Requests')
    notebook.add(pm_tab, text='PM Schedule')
    notebook.add(history_tab, text='History Card')

    # Equipment Tab
    tk.Label(equip_tab, text="Tag").grid(row=0, column=0)
    tk.Label(equip_tab, text="Name").grid(row=1, column=0)
    tk.Label(equip_tab, text="Rating").grid(row=2, column=0)
    tk.Label(equip_tab, text="Status").grid(row=3, column=0)

    tag_entry = tk.Entry(equip_tab)
    name_entry = tk.Entry(equip_tab)
    rating_entry = tk.Entry(equip_tab)
    status_entry = tk.Entry(equip_tab)

    tag_entry.grid(row=0, column=1)
    name_entry.grid(row=1, column=1)
    rating_entry.grid(row=2, column=1)
    status_entry.grid(row=3, column=1)

    def add_equipment():
        equipment_data.append([tag_entry.get(), name_entry.get(), rating_entry.get(), status_entry.get()])
        refresh_equipment()

    def edit_equipment():
        selected = equip_tree.selection()
        if selected:
            index = equip_tree.index(selected)
            equipment_data[index] = [tag_entry.get(), name_entry.get(), rating_entry.get(), status_entry.get()]
            refresh_equipment()

    def delete_equipment():
        selected = equip_tree.selection()
        if selected:
            index = equip_tree.index(selected)
            del equipment_data[index]
            refresh_equipment()

    def refresh_equipment():
        equip_tree.delete(*equip_tree.get_children())
        for eq in equipment_data:
            equip_tree.insert('', 'end', values=eq)
        equip_combo['values'] = [x[0] for x in equipment_data]
        hist_equip_combo['values'] = [x[0] for x in equipment_data]

    tk.Button(equip_tab, text="Add", command=add_equipment).grid(row=4, column=0)
    tk.Button(equip_tab, text="Edit", command=edit_equipment).grid(row=4, column=1)
    tk.Button(equip_tab, text="Delete", command=delete_equipment).grid(row=4, column=2)

    equip_tree = ttk.Treeview(equip_tab, columns=("Tag", "Name", "Rating", "Status"), show='headings')
    for col in ("Tag", "Name", "Rating", "Status"):
        equip_tree.heading(col, text=col)
    equip_tree.grid(row=5, column=0, columnspan=3)

    # Maintenance Tab
    tk.Label(maint_tab, text="Equipment Tag").grid(row=0, column=0)
    tk.Label(maint_tab, text="Date").grid(row=1, column=0)
    tk.Label(maint_tab, text="Description").grid(row=2, column=0)

    equip_combo = ttk.Combobox(maint_tab)
    date_entry = DateEntry(maint_tab)
    desc_entry = tk.Entry(maint_tab)

    equip_combo.grid(row=0, column=1)
    date_entry.grid(row=1, column=1)
    desc_entry.grid(row=2, column=1)

    def add_maintenance():
        maintenance_data.append([equip_combo.get(), date_entry.get(), desc_entry.get()])
        refresh_maintenance()

    def edit_maintenance():
        selected = maintenance_tree.selection()
        if selected:
            index = maintenance_tree.index(selected)
            maintenance_data[index] = [equip_combo.get(), date_entry.get(), desc_entry.get()]
            refresh_maintenance()

    def delete_maintenance():
        selected = maintenance_tree.selection()
        if selected:
            index = maintenance_tree.index(selected)
            del maintenance_data[index]
            refresh_maintenance()

    def refresh_maintenance():
        maintenance_tree.delete(*maintenance_tree.get_children())
        for m in maintenance_data:
            maintenance_tree.insert('', 'end', values=m)

    tk.Button(maint_tab, text="Add", command=add_maintenance).grid(row=3, column=0)
    tk.Button(maint_tab, text="Edit", command=edit_maintenance).grid(row=3, column=1)
    tk.Button(maint_tab, text="Delete", command=delete_maintenance).grid(row=3, column=2)

    maintenance_tree = ttk.Treeview(maint_tab, columns=("Equipment", "Date", "Description"), show='headings')
    for col in ("Equipment", "Date", "Description"):
        maintenance_tree.heading(col, text=col)
    maintenance_tree.grid(row=4, column=0, columnspan=3)

    # History Tab
    tk.Label(history_tab, text="Equipment Tag").grid(row=0, column=0)
    tk.Label(history_tab, text="Work Description").grid(row=1, column=0)
    tk.Label(history_tab, text="Date").grid(row=2, column=0)
    tk.Label(history_tab, text="Chief Electrician").grid(row=3, column=0)

    hist_equip_combo = ttk.Combobox(history_tab)
    hist_desc = tk.Entry(history_tab)
    hist_date = DateEntry(history_tab)
    hist_tech = tk.Entry(history_tab)

    hist_equip_combo.grid(row=0, column=1)
    hist_desc.grid(row=1, column=1)
    hist_date.grid(row=2, column=1)
    hist_tech.grid(row=3, column=1)

    def add_history():
        history_data.append([hist_equip_combo.get(), hist_desc.get(), hist_date.get(), hist_tech.get()])
        refresh_history()

    def edit_history():
        selected = hist_tree.selection()
        if selected:
            index = hist_tree.index(selected)
            history_data[index] = [hist_equip_combo.get(), hist_desc.get(), hist_date.get(), hist_tech.get()]
            refresh_history()

    def delete_history():
        selected = hist_tree.selection()
        if selected:
            index = hist_tree.index(selected)
            del history_data[index]
            refresh_history()

    def refresh_history():
        hist_tree.delete(*hist_tree.get_children())
        for h in history_data:
            hist_tree.insert('', 'end', values=h)
        hist_equip_combo['values'] = [x[0] for x in equipment_data]

    tk.Button(history_tab, text="Add", command=add_history).grid(row=4, column=0)
    tk.Button(history_tab, text="Edit", command=edit_history).grid(row=4, column=1)
    tk.Button(history_tab, text="Delete", command=delete_history).grid(row=4, column=2)

    hist_tree = ttk.Treeview(history_tab, columns=("Equipment", "Description", "Date", "Chief Electrician"), show='headings')
    for col in ("Equipment", "Description", "Date", "Chief Electrician"):
        hist_tree.heading(col, text=col)
    hist_tree.grid(row=5, column=0, columnspan=3)

    # Placeholder for Spare, MSR, PM tabs
    tk.Label(spare_tab, text="(Spare tab to be implemented)").pack()
    tk.Label(msr_tab, text="(MSR tab to be implemented)").pack()
    tk.Label(pm_tab, text="(PM tab to be implemented)").pack()

    def refresh_all():
        refresh_equipment()
        refresh_maintenance()
        refresh_history()

    def on_close():
        save_data()
        root.destroy()

    load_data()
    refresh_all()
    root.protocol("WM_DELETE_WINDOW", on_close)
    root.mainloop()

# Login system
def login_screen():
    login = tk.Tk()
    login.title("Login")
    login.geometry("300x180")

    tk.Label(login, text="Department").pack()
    dept_entry = tk.Entry(login)
    dept_entry.pack()

    tk.Label(login, text="Password").pack()
    pass_entry = tk.Entry(login, show="*")
    pass_entry.pack()

    def try_login():
        dept = dept_entry.get()
        pw = pass_entry.get()
        if user_data.get(dept) == pw:
            login.destroy()
            main_window()
        else:
            messagebox.showerror("Login Failed", "Invalid department or password")

    def signup():
        dept = dept_entry.get()
        pw = pass_entry.get()
        if dept in user_data:
            messagebox.showerror("Signup Failed", "Department already exists")
        else:
            user_data[dept] = pw
            save_data()
            messagebox.showinfo("Signup Success", "Account created")

    tk.Button(login, text="Login", command=try_login).pack(pady=5)
    tk.Button(login, text="Signup", command=signup).pack()

    load_data()
    login.mainloop()

# Start the app
login_screen()
