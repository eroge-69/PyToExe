# Check if tkinter is available before importing
try:
    import tkinter as tk
    from tkinter import ttk, messagebox, filedialog
except ImportError:
    print("tkinter is not installed. This application requires a GUI environment with tkinter support.")
    raise SystemExit(1)

import json
from datetime import datetime

# Optional: Use a calendar widget for date selection
try:
    from tkcalendar import DateEntry
except ImportError:
    DateEntry = tk.Entry  # Fallback to basic Entry if tkcalendar is not available

# Global data storage
user_data = {}
equipment_data = []
maintenance_data = []
spare_data = []
msr_data = []

# Save/Load functionality
def save_data():
    data = {
        "users": user_data,
        "equipment": equipment_data,
        "maintenance": maintenance_data,
        "spare": spare_data,
        "msr": msr_data
    }
    with open("cmms_data.json", "w") as f:
        json.dump(data, f)

def load_data():
    global user_data, equipment_data, maintenance_data, spare_data, msr_data
    try:
        with open("cmms_data.json", "r") as f:
            data = json.load(f)
            user_data = data.get("users", {})
            equipment_data = data.get("equipment", [])
            maintenance_data = data.get("maintenance", [])
            spare_data = data.get("spare", [])
            msr_data = data.get("msr", [])
    except FileNotFoundError:
        pass

# Login/Signup window
def open_main_app():
    root = tk.Tk()
    root.title("CMMS Software")
    root.geometry("1000x600")

    menu = tk.Menu(root)
    root.config(menu=menu)

    file_menu = tk.Menu(menu, tearoff=0)
    menu.add_cascade(label="File", menu=file_menu)
    file_menu.add_command(label="Save Data", command=save_data)
    file_menu.add_command(label="Load Data", command=load_data)

    notebook = ttk.Notebook(root)
    notebook.pack(fill='both', expand=True)

    equip_tab = ttk.Frame(notebook)
    maint_tab = ttk.Frame(notebook)
    spare_tab = ttk.Frame(notebook)
    msr_tab = ttk.Frame(notebook)

    notebook.add(equip_tab, text='Equipment')
    notebook.add(maint_tab, text='Maintenance')
    notebook.add(spare_tab, text='Spare Parts')
    notebook.add(msr_tab, text='MSR Requests')

    # Equipment Tab
    tk.Label(equip_tab, text="Code").grid(row=0, column=0)
    tk.Label(equip_tab, text="Name").grid(row=1, column=0)
    tk.Label(equip_tab, text="Location").grid(row=2, column=0)

    equip_code = tk.Entry(equip_tab)
    equip_name = tk.Entry(equip_tab)
    equip_loc = tk.Entry(equip_tab)

    equip_code.grid(row=0, column=1)
    equip_name.grid(row=1, column=1)
    equip_loc.grid(row=2, column=1)

    def add_equipment():
        equipment_data.append([equip_code.get(), equip_name.get(), equip_loc.get()])
        refresh_equipment()

    def refresh_equipment():
        equip_tree.delete(*equip_tree.get_children())
        for item in equipment_data:
            equip_tree.insert('', 'end', values=item)

    add_btn = tk.Button(equip_tab, text="Add", command=add_equipment)
    add_btn.grid(row=3, column=0, columnspan=2)

    equip_tree = ttk.Treeview(equip_tab, columns=("Code", "Name", "Location"), show='headings')
    for col in ("Code", "Name", "Location"):
        equip_tree.heading(col, text=col)
    equip_tree.grid(row=4, column=0, columnspan=2)

    # Maintenance Tab
    tk.Label(maint_tab, text="Equipment").grid(row=0, column=0)
    tk.Label(maint_tab, text="Task").grid(row=1, column=0)
    tk.Label(maint_tab, text="Date").grid(row=2, column=0)

    equip_combo = ttk.Combobox(maint_tab, values=[x[1] for x in equipment_data])
    maint_task = tk.Entry(maint_tab)
    maint_date = DateEntry(maint_tab)

    equip_combo.grid(row=0, column=1)
    maint_task.grid(row=1, column=1)
    maint_date.grid(row=2, column=1)

    def add_maintenance():
        maintenance_data.append([equip_combo.get(), maint_task.get(), maint_date.get()])
        refresh_maintenance()

    def refresh_maintenance():
        equip_combo['values'] = [x[1] for x in equipment_data]
        maint_tree.delete(*maint_tree.get_children())
        for item in maintenance_data:
            maint_tree.insert('', 'end', values=item)

    maint_btn = tk.Button(maint_tab, text="Add", command=add_maintenance)
    maint_btn.grid(row=3, column=0, columnspan=2)

    maint_tree = ttk.Treeview(maint_tab, columns=("Equipment", "Task", "Date"), show='headings')
    for col in ("Equipment", "Task", "Date"):
        maint_tree.heading(col, text=col)
    maint_tree.grid(row=4, column=0, columnspan=2)

    # Spare Tab
    tk.Label(spare_tab, text="Spare Code").grid(row=0, column=0)
    tk.Label(spare_tab, text="Description").grid(row=1, column=0)
    tk.Label(spare_tab, text="Quantity").grid(row=2, column=0)

    spare_code = tk.Entry(spare_tab)
    spare_desc = tk.Entry(spare_tab)
    spare_qty = tk.Entry(spare_tab)

    spare_code.grid(row=0, column=1)
    spare_desc.grid(row=1, column=1)
    spare_qty.grid(row=2, column=1)

    def add_spare():
        spare_data.append([spare_code.get(), spare_desc.get(), spare_qty.get()])
        refresh_spare()

    def refresh_spare():
        spare_tree.delete(*spare_tree.get_children())
        for item in spare_data:
            spare_tree.insert('', 'end', values=item)

    spare_btn = tk.Button(spare_tab, text="Add", command=add_spare)
    spare_btn.grid(row=3, column=0, columnspan=2)

    spare_tree = ttk.Treeview(spare_tab, columns=("Code", "Description", "Qty"), show='headings')
    for col in ("Code", "Description", "Qty"):
        spare_tree.heading(col, text=col)
    spare_tree.grid(row=4, column=0, columnspan=2)

    # MSR Tab
    tk.Label(msr_tab, text="Spare Part").grid(row=0, column=0)
    tk.Label(msr_tab, text="Quantity").grid(row=1, column=0)
    tk.Label(msr_tab, text="Date Required").grid(row=2, column=0)

    msr_part_combo = ttk.Combobox(msr_tab, values=[x[1] for x in spare_data])
    msr_qty_entry = tk.Entry(msr_tab)
    msr_date_entry = DateEntry(msr_tab)

    msr_part_combo.grid(row=0, column=1)
    msr_qty_entry.grid(row=1, column=1)
    msr_date_entry.grid(row=2, column=1)

    def add_msr():
        msr_data.append([msr_part_combo.get(), msr_qty_entry.get(), msr_date_entry.get()])
        refresh_msr()

    def refresh_msr():
        msr_part_combo['values'] = [x[1] for x in spare_data]
        msr_tree.delete(*msr_tree.get_children())
        for item in msr_data:
            msr_tree.insert('', 'end', values=item)

    msr_btn = tk.Button(msr_tab, text="Add", command=add_msr)
    msr_btn.grid(row=3, column=0, columnspan=2)

    msr_tree = ttk.Treeview(msr_tab, columns=("Spare", "Qty", "Date Required"), show='headings')
    for col in ("Spare", "Qty", "Date Required"):
        msr_tree.heading(col, text=col)
    msr_tree.grid(row=4, column=0, columnspan=2)

    def refresh_all():
        refresh_equipment()
        refresh_maintenance()
        refresh_spare()
        refresh_msr()

    load_data()
    refresh_all()
    root.mainloop()

# Login/Signup Logic
def show_login_window():
    login_root = tk.Tk()
    login_root.title("Login / Signup")

    tk.Label(login_root, text="Username").grid(row=0, column=0)
    tk.Label(login_root, text="Password").grid(row=1, column=0)
    tk.Label(login_root, text="Department").grid(row=2, column=0)

    username_entry = tk.Entry(login_root)
    password_entry = tk.Entry(login_root, show="*")
    dept_entry = tk.Entry(login_root)

    username_entry.grid(row=0, column=1)
    password_entry.grid(row=1, column=1)
    dept_entry.grid(row=2, column=1)

    def signup():
        uname = username_entry.get()
        pwd = password_entry.get()
        dept = dept_entry.get()
        if uname in user_data:
            messagebox.showerror("Error", "User already exists")
        else:
            user_data[uname] = {"password": pwd, "department": dept}
            messagebox.showinfo("Success", "User registered successfully")
            save_data()

    def login():
        uname = username_entry.get()
        pwd = password_entry.get()
        if user_data.get(uname, {}).get("password") == pwd:
            messagebox.showinfo("Welcome", f"Login successful! Welcome {uname}")
            login_root.destroy()
            open_main_app()
        else:
            messagebox.showerror("Error", "Invalid credentials")

    tk.Button(login_root, text="Login", command=login).grid(row=3, column=0)
    tk.Button(login_root, text="Signup", command=signup).grid(row=3, column=1)

    login_root.mainloop()

show_login_window()
