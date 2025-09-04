import tkinter as tk
from tkinter import messagebox, ttk
import openpyxl
from openpyxl.styles import Font
import os

# ----------- Login Window -----------
def show_login_window():
    login_win = tk.Tk()
    login_win.title("Login")
    login_win.geometry('340x440')
    login_win.configure(bg='#333333')

    def login():
        username = "shiv"
        password = "12345"
        if username_entry.get() == username and password_entry.get() == password:
            messagebox.showinfo(title="Login Success", message="You successfully logged in.")
            login_win.destroy()
            show_main_app()
        else:
            messagebox.showerror(title="Error", message="Invalid login.")

    frame = tk.Frame(login_win, bg='#333333')
    login_label = tk.Label(frame, text="Login", bg='#333333', fg="#FF3399", font=("Arial", 30))
    username_label = tk.Label(frame, text="Username", bg='#333333', fg="#FFFFFF", font=("Arial", 16))
    username_entry = tk.Entry(frame, font=("Arial", 16))
    password_entry = tk.Entry(frame, show="*", font=("Arial", 16))
    password_label = tk.Label(frame, text="Password", bg='#333333', fg="#FFFFFF", font=("Arial", 16))
    login_button = tk.Button(frame, text="Login", bg="#FF3399", fg="#FFFFFF", font=("Arial", 16), command=login)

    login_label.grid(row=0, column=0, columnspan=2, sticky="news", pady=40)
    username_label.grid(row=1, column=0)
    username_entry.grid(row=1, column=1, pady=20)
    password_label.grid(row=2, column=0)
    password_entry.grid(row=2, column=1, pady=20)
    login_button.grid(row=3, column=0, columnspan=2, pady=30)
    frame.pack()

    login_win.mainloop()

# ----------- Main App -----------
def show_main_app():
    # ---------- Helper Functions ----------
    def parse_potency(potency_str):
        potency_str = potency_str.upper().strip()
        number = ''.join(filter(str.isdigit, potency_str))
        scale = ''.join(filter(str.isalpha, potency_str))
        if not number or scale not in ['X', 'C']:
            raise ValueError("Invalid potency format. Use '6X' or '30C'.")
        return int(number), scale

    def get_dilution_factor(scale):
        return 10 if scale == 'X' else 100

    def calculate_initial_volume(final_volume, potency_str):
        dilutions, scale = parse_potency(potency_str)
        factor = get_dilution_factor(scale)
        total_dilution = factor ** dilutions
        starting_volume = final_volume / total_dilution
        return starting_volume, dilutions, factor, total_dilution

    def export_to_excel(steps, factor, starting_volume, final_volume, potency):
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Dilution Steps"
        headers = ["Step Number", f"Dilution (1:{factor})", "Volume After Step (ml)"]
        ws.append(headers)
        for cell in ws[1]: cell.font = Font(bold=True)
        for step_num, dilution_factor, volume in steps:
            ws.append([step_num, dilution_factor, volume])
        ws.append([])
        ws.append(["Final Volume (ml):", final_volume])
        ws.append(["Potency:", potency])
        ws.append(["Starting Volume Needed (ml):", starting_volume])
        filename = "dilution_steps.xlsx"
        wb.save(filename)
        return filename

    def clear_treeview():
        for row in tree.get_children(): tree.delete(row)

    def populate_treeview(steps):
        clear_treeview()
        for step_num, dilution_factor, volume in steps:
            tree.insert("", "end", values=(step_num, f"1:{dilution_factor}", f"{volume:.10f}"))

    class EditableTreeview(ttk.Treeview):
        def __init__(self, master=None, **kw):
            super().__init__(master, **kw)
            self._edit_entry = None
            self.bind("<Double-1>", self._on_double_click)

        def _on_double_click(self, event):
            region = self.identify("region", event.x, event.y)
            if region != "cell": return
            column = self.identify_column(event.x)
            row = self.identify_row(event.y)
            if not row or not column: return
            x, y, width, height = self.bbox(row, column)
            col_idx = int(column.replace("#", "")) - 1
            item = self.item(row)
            value = item['values'][col_idx]
            if self._edit_entry: self._edit_entry.destroy()
            self._edit_entry = tk.Entry(self)
            self._edit_entry.place(x=x, y=y, width=width, height=height)
            self._edit_entry.insert(0, value)
            self._edit_entry.focus_set()

            def save_edit(event=None):
                new_val = self._edit_entry.get()
                values = list(item['values'])
                values[col_idx] = new_val
                self.item(row, values=values)
                self._edit_entry.destroy()
                self._edit_entry = None

            self._edit_entry.bind("<Return>", save_edit)
            self._edit_entry.bind("<FocusOut>", save_edit)

    def calculate():
        try:
            final_volume = float(entry_volume.get())
            potency = entry_potency.get()

            selected_tincture = tracker_tree.selection()
            if not selected_tincture:
                messagebox.showwarning("No Tincture", "Select a tincture from the tracker.")
                return

            tincture_values = tracker_tree.item(selected_tincture[0], "values")
            tincture_name = tincture_values[0]
            remaining_volume = float(tincture_values[2])

            start_volume, steps, factor, total_dilution = calculate_initial_volume(final_volume, potency)
            if start_volume > remaining_volume:
                messagebox.showerror("Insufficient Volume",
                    f"Tincture '{tincture_name}' does not have enough volume.\n"
                    f"Required: {start_volume:.10f} ml\nAvailable: {remaining_volume:.10f} ml")
                return

            dilution_steps = []
            for step in range(steps, 0, -1):
                dilution_factor = factor ** step
                volume_after_step = final_volume / dilution_factor
                dilution_steps.append((steps - step + 1, dilution_factor, volume_after_step))

            result_label.config(text=(
                f"🧪 Final Volume: {final_volume} ml\n"
                f"🔢 Potency: {potency.upper()} ({steps} steps of 1:{factor})\n"
                f"📉 Total Dilution: 1:{total_dilution}\n"
                f"💧 Starting Volume Needed: {start_volume:.10f} ml\n"
                f"🏷️ Tincture Used: {tincture_name}"
            ))

            populate_treeview(dilution_steps)
            new_remaining = remaining_volume - start_volume
            updated_values = list(tincture_values)
            updated_values[2] = f"{new_remaining:.10f}"
            tracker_tree.item(selected_tincture[0], values=updated_values)

            filename = export_to_excel(dilution_steps, factor, start_volume, final_volume, potency.upper())
            try: os.startfile(filename)
            except: messagebox.showwarning("Open File", f"Couldn't open file automatically:\n{filename}")
            messagebox.showinfo("Success", f"Dilution steps exported to '{filename}'")

        except ValueError as e:
            messagebox.showerror("Input Error", str(e))
        except Exception as e:
            messagebox.showerror("Error", f"Unexpected error: {e}")

    # ---------- GUI ----------
    root = tk.Tk()
    root.title("Homeopathic Calculator & Tincture Tracker")
    root.geometry("780x540")
    root.configure(bg="#333333")

    label_font = ("Arial", 12)
    entry_font = ("Arial", 12)

    frame_inputs = tk.Frame(root, bg="#333333")
    frame_inputs.pack(pady=10)

    tk.Label(frame_inputs, text="Final Volume (ml):", font=label_font, bg="#333333", fg="white").grid(row=0, column=0, sticky="w", padx=5)
    entry_volume = tk.Entry(frame_inputs, font=entry_font, width=15)
    entry_volume.grid(row=0, column=1, padx=5)

    tk.Label(frame_inputs, text="Potency (e.g., 6X or 30C):", font=label_font, bg="#333333", fg="white").grid(row=1, column=0, sticky="w", padx=5)
    entry_potency = tk.Entry(frame_inputs, font=entry_font, width=15)
    entry_potency.grid(row=1, column=1, padx=5)

    tk.Button(frame_inputs, text="Calculate", font=label_font, command=calculate, bg="#FF3399", fg="white").grid(row=0, column=2, rowspan=2, padx=10)

    notebook = ttk.Notebook(root)
    notebook.pack(fill="both", expand=True, padx=10, pady=10)

    tab_results = tk.Frame(notebook)
    notebook.add(tab_results, text="Results")

    result_label = tk.Label(tab_results, text="", font=("Courier", 11), justify="left", anchor="nw", bg="white")
    result_label.pack(fill="both", expand=True, padx=10, pady=10)

    tab_log = tk.Frame(notebook)
    notebook.add(tab_log, text="Activity Log")

    columns = ("Step Number", "Dilution", "Volume (ml)")
    tree = ttk.Treeview(tab_log, columns=columns, show="headings", height=15)
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, anchor="center", width=180)
    tree.pack(fill="both", expand=True, padx=10, pady=10)

    tab_tracker = tk.Frame(notebook)
    notebook.add(tab_tracker, text="Tincture Tracker")

    tracker_columns = ("Tincture Name", "Start Volume (ml)", "Remaining Volume (ml)")
    tracker_tree = EditableTreeview(tab_tracker, columns=tracker_columns, show="headings", height=12)
    for col in tracker_columns:
        tracker_tree.heading(col, text=col)
        tracker_tree.column(col, anchor="center", width=200)
    tracker_tree.pack(side="top", fill="both", expand=True, padx=10, pady=(10, 0))

    btn_frame = tk.Frame(tab_tracker)
    btn_frame.pack(pady=5)

    def add_tincture():
        tracker_tree.insert("", "end", values=("New Tincture", "100.0", "100.0"))

    def delete_tincture():
        selected = tracker_tree.selection()
        if not selected:
            messagebox.showwarning("Delete Row", "Select a row to delete.")
            return
        for item in selected:
            tracker_tree.delete(item)

    tk.Button(btn_frame, text="Add Tincture", command=add_tincture).pack(side="left", padx=5)
    tk.Button(btn_frame, text="Delete Selected", command=delete_tincture).pack(side="left", padx=5)

    root.mainloop()

# ---------- Run App ----------
show_login_window()
