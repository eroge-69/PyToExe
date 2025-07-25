
import tkinter as tk
from tkinter import messagebox

VALID_USERNAME = "PAWAN"
VALID_PASSWORD = "01460"

def show_login():
    login_win = tk.Tk()
    login_win.title("Login Required")
    login_win.geometry("300x180")
    login_win.resizable(False, False)

    tk.Label(login_win, text="Username:", font=("Arial", 10)).pack(pady=(20, 5))
    username_entry = tk.Entry(login_win, width=25, justify="center")
    username_entry.pack()

    tk.Label(login_win, text="Password:", font=("Arial", 10)).pack(pady=(10, 5))
    password_entry = tk.Entry(login_win, show="*", width=25, justify="center")
    password_entry.pack()

    def attempt_login(event=None):
        username = username_entry.get().strip()
        password = password_entry.get().strip()
        if username == VALID_USERNAME and password == VALID_PASSWORD:
            login_win.destroy()
            start_main_app()
        else:
            messagebox.showerror(
                "Access Denied",
                "Invalid username or password.\n\nPlease contact Mr. Pawan Saini at 8875557099."
            )

    def focus_next(event):
        password_entry.focus_set()
        return "break"

    def focus_prev(event):
        username_entry.focus_set()
        return "break"

    username_entry.bind("<Down>", focus_next)
    username_entry.bind("<Return>", attempt_login)
    password_entry.bind("<Up>", focus_prev)
    password_entry.bind("<Return>", attempt_login)

    tk.Button(login_win, text="Login", command=attempt_login).pack(pady=15)
    username_entry.focus_set()
    login_win.mainloop()


def start_main_app():
    
    import tkinter as tk
    from tkinter import ttk
    
    NUM_ROWS = 15
    NEW_TAB_ROWS = 10
    
    # --- Functions ---
    def apply_formulas():
        total_c_sum = 0.0
        for i in range(NUM_ROWS):
            val_str = table_entries[i][0].get().strip()
            if not val_str:
                calculations[i][0] = 0
                calculations[i][1] = 0
                continue
            try:
                val = float(val_str)
                col_b = val / 2
                col_c = 1 / col_b if col_b != 0 else 0
                calculations[i][0] = col_b
                calculations[i][1] = col_c
                total_c_sum += col_c
            except ValueError:
                calculations[i][0] = 0
                calculations[i][1] = 0
    
        result = 1 / total_c_sum if total_c_sum != 0 else 0.0
        total_entry.config(state="normal")
        total_entry.delete(0, tk.END)
        total_entry.insert(0, f"{result:.4f}")
        total_entry.config(state="readonly")
        result_label.config(text="TOTAL PAIR/METER:")
    
    def on_a_column_change(var, row):
        apply_formulas()
    
    def handle_down_arrow(event, current_row):
        if current_row < NUM_ROWS - 1:
            table_entries[current_row + 1][0].focus_set()
        return "break"
    
    def handle_up_arrow(event, current_row):
        if current_row > 0:
            table_entries[current_row - 1][0].focus_set()
        return "break"
    
    def make_arrow_bindings(entry, row):
        entry.bind("<Down>", lambda event: handle_down_arrow(event, row))
        entry.bind("<Up>", lambda event: handle_up_arrow(event, row))
    
    def handle_down_arrow_tab2(event, current_row):
        if current_row < NEW_TAB_ROWS - 1:
            tab2_entries[current_row + 1].focus_set()
        return "break"
    
    def handle_up_arrow_tab2(event, current_row):
        if current_row > 0:
            tab2_entries[current_row - 1].focus_set()
        return "break"
    
    def make_arrow_bindings_tab2(entry, row):
        entry.bind("<Down>", lambda event: handle_down_arrow_tab2(event, row))
        entry.bind("<Up>", lambda event: handle_up_arrow_tab2(event, row))
    
    def apply_formula_tab2():
        total = 0.0
        for var in tab2_vars:
            val_str = var.get().strip()
            try:
                val = float(val_str)
                total += val
            except ValueError:
                continue
    
        result = (2 * total) / 1000
        tab2_result_entry.config(state="normal")
        tab2_result_entry.delete(0, tk.END)
        tab2_result_entry.insert(0, f"{result:.4f}")
        tab2_result_entry.config(state="readonly")
    
    def on_tab2_change(var):
        apply_formula_tab2()
    
    def reset_all():
        for row in table_entries:
            for cell in row:
                cell.delete(0, tk.END)
        for row in calculations:
            row[0] = 0
            row[1] = 0
        total_entry.config(state="normal")
        total_entry.delete(0, tk.END)
        total_entry.config(state="readonly")
        result_label.config(text="TOTAL PAIR/METER:")
        for var in tab2_vars:
            var.set("")
        tab2_result_entry.config(state="normal")
        tab2_result_entry.delete(0, tk.END)
        tab2_result_entry.config(state="readonly")
    
    def switch_tab(event, direction):
        current = notebook.index(notebook.select())
        total_tabs = notebook.index("end")
        if direction == "left" and current > 0:
            notebook.select(current - 1)
        elif direction == "right" and current < total_tabs - 1:
            notebook.select(current + 1)
    
    def focus_first_entry():
        notebook.select(0)
        table_entries[0][0].focus_set()
    
    def on_tab_changed(event):
        current_tab = notebook.index(notebook.select())
        if current_tab == 0:
            table_entries[0][0].focus_set()
        elif current_tab == 1:
            tab2_entries[0].focus_set()
    
    # --- GUI Setup ---
    root = tk.Tk()
    root.title("LICENCED WITH ATOM SHOEMASTER")
    root.geometry("500x580")
    root.resizable(False, False)
    
    notebook = ttk.Notebook(root)
    notebook.pack(expand=True, fill='both')
    notebook.bind("<<NotebookTabChanged>>", on_tab_changed)
    
    # --- Tab 1 ---
    tab1 = tk.Frame(notebook)
    notebook.add(tab1, text="Pair/Meter Calculator  ")
    
    tk.Label(tab1, text="Value", width=20, borderwidth=1, relief="solid", bg="#e6e6e6").pack()
    
    calculations = [[0, 0] for _ in range(NUM_ROWS)]
    table_entries = []
    a_vars = []
    
    table_frame = tk.Frame(tab1)
    table_frame.pack()
    
    for i in range(NUM_ROWS):
        a_var = tk.StringVar()
        a_var.trace_add("write", lambda name, index, mode, row=i: on_a_column_change(a_var, row))
        a_vars.append(a_var)
        entry = tk.Entry(table_frame, width=20, textvariable=a_var, justify="center")
        entry.grid(row=i, column=0, padx=1, pady=1)
        make_arrow_bindings(entry, i)
        table_entries.append([entry])
    
    bottom_frame = tk.Frame(tab1)
    bottom_frame.pack(pady=10)
    
    result_label = tk.Label(bottom_frame, text="TOTAL PAIR/METER:", font=("Arial", 12))
    result_label.pack()
    
    total_entry = tk.Entry(bottom_frame, width=20, justify="center", fg="blue", font=("Arial", 15, "bold"))
    total_entry.pack()
    total_entry.config(state="readonly")
    
    tk.Button(tab1, text="Reset", command=reset_all).pack(pady=5)
    
    # --- Tab 2 ---
    tab2 = tk.Frame(notebook)
    notebook.add(tab2, text="Meter/Pair Calculator")
    
    tk.Label(tab2, text="Enter 5 Values:", font=("Arial", 12)).pack(pady=5)
    
    tab2_vars = []
    tab2_entries = []
    tab2_frame = tk.Frame(tab2)
    tab2_frame.pack()
    
    for i in range(NEW_TAB_ROWS):
        var = tk.StringVar()
        var.trace_add("write", lambda name, index, mode, v=var: on_tab2_change(v))
        entry = tk.Entry(tab2_frame, width=20, textvariable=var, justify="center")
        entry.grid(row=i, column=0, pady=3)
        make_arrow_bindings_tab2(entry, i)
        tab2_vars.append(var)
        tab2_entries.append(entry)
    
    tab2_result_label = tk.Label(tab2, text="METER/PAIR:", font=("Arial", 12))
    tab2_result_label.pack(pady=(15, 2))
    
    tab2_result_entry = tk.Entry(tab2, width=20, justify="center", fg="green", font=("Arial", 15, "bold"))
    tab2_result_entry.pack()
    tab2_result_entry.config(state="readonly")
    
    # --- Global Key Bindings ---
    root.bind("<Escape>", lambda event: reset_all())
    root.bind("<Control-Right>", lambda event: switch_tab(event, "right"))
    root.bind("<Control-Left>", lambda event: switch_tab(event, "left"))
    
    root.after(100, focus_first_entry)
    
    root.mainloop()

show_login()