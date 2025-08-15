"""
SlipUpApp - Simple point-of‑sale closing application for small restaurants.

This program implements a minimal point‑of‑sale closing sheet similar to the
provided Excel template.  Waiters can log in and record their daily revenue
(xhiro) and any deductions (zbritje) or additions (plus) before closing.
Each waiter entry is saved into a per‑month CSV file that an admin can
review later.  Administrators can also manage the list of waiters and the
available categories for deductions and additions.  Categories control the
drop‑down menus that appear in the waiter interface.

Data is stored locally in a few JSON files next to this script:

* ``users.json`` holds user credentials and roles.  An initial admin user
  with password ``1234`` is created on first run.
* ``categories.json`` stores two lists: ``deduction`` and ``addition``.
* ``slips/`` is a folder where monthly CSV files are written.  Each waiter
  gets a file named ``<year>-<month>_<waiter>.csv``.

The program requires only the Python standard library and Tkinter, so it
can be packaged into a standalone executable using a service such as
``pytoexe.vercel.app`` or by running PyInstaller on Windows yourself.  No
external dependencies are needed.
"""

import json
import os
import csv
import datetime
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog


DATA_DIR = os.path.dirname(os.path.abspath(__file__))
USERS_FILE = os.path.join(DATA_DIR, "users.json")
CATEGORIES_FILE = os.path.join(DATA_DIR, "categories.json")
SLIPS_DIR = os.path.join(DATA_DIR, "slips")


def ensure_data_files():
    """Ensure that the users and categories files exist.

    If they do not exist, create them with sensible defaults.  An
    administrator account with password ``1234`` is created on first run.
    """
    # Initialise users file
    if not os.path.isfile(USERS_FILE):
        default_users = {
            "admin": {"password": "1234", "role": "admin"}
        }
        with open(USERS_FILE, "w", encoding="utf-8") as f:
            json.dump(default_users, f, indent=2)

    # Initialise categories file
    if not os.path.isfile(CATEGORIES_FILE):
        default_categories = {
            "deduction": ["POS", "Fruta", "Gaz"],
            "addition": ["Borxh i kthyer"]
        }
        with open(CATEGORIES_FILE, "w", encoding="utf-8") as f:
            json.dump(default_categories, f, indent=2)

    # Ensure slips directory exists
    os.makedirs(SLIPS_DIR, exist_ok=True)


def load_users():
    """Load the users from disk."""
    with open(USERS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_users(users):
    """Persist user credentials to disk."""
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=2)


def load_categories():
    """Load deduction and addition categories from disk."""
    with open(CATEGORIES_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_categories(categories):
    """Persist categories to disk."""
    with open(CATEGORIES_FILE, "w", encoding="utf-8") as f:
        json.dump(categories, f, indent=2)


class SlipForm(ttk.Frame):
    """
    Frame containing the waiter interface for entering the daily closure slip.

    It displays fields for date, revenue (xhiro), a table of deductions with
    drop‑down menus, a table of additions and computed totals.  When the
    waiter presses the "Print & Save" button the data is validated, written
    to a CSV file and a simple text receipt is displayed.
    """

    NUM_DEDUCTION_ROWS = 10
    NUM_ADDITION_ROWS = 5

    def __init__(self, master, app, waiter_name):
        super().__init__(master)
        self.app = app
        self.waiter_name = waiter_name
        self.categories = load_categories()
        # Build UI
        self.build_ui()
        # Trigger initial total calculation
        self.update_totals()

    def build_ui(self):
        # Title
        title = ttk.Label(self, text=f"Slip Up Duff Arena", font=("Arial", 16, "bold"))
        title.grid(row=0, column=0, columnspan=4, pady=(10, 5))

        # Waiter name and date
        ttk.Label(self, text=f"Emri: {self.waiter_name}", font=("Arial", 12)).grid(row=1, column=0, sticky="w", padx=10)

        today = datetime.date.today().strftime("%Y-%m-%d")
        self.date_var = tk.StringVar(value=today)
        ttk.Label(self, text="Dt.", font=("Arial", 12)).grid(row=1, column=1, sticky="e")
        self.date_entry = ttk.Entry(self, textvariable=self.date_var, width=12)
        self.date_entry.grid(row=1, column=2, sticky="w")

        # Revenue
        ttk.Label(self, text="Xhiro", font=("Arial", 12)).grid(row=2, column=0, sticky="w", padx=10, pady=(10,0))
        self.revenue_var = tk.StringVar()
        self.revenue_entry = ttk.Entry(self, textvariable=self.revenue_var)
        self.revenue_entry.grid(row=2, column=1, padx=10, pady=(10,0), sticky="w")
        self.revenue_var.trace_add('write', lambda *args: self.update_totals())

        # Deduction section header
        ttk.Label(self, text="Zbritje", font=("Arial", 12, "bold")).grid(row=3, column=0, pady=(15,5), sticky="w", padx=10)
        ttk.Label(self, text="Lloji", font=("Arial", 10, "bold")).grid(row=4, column=0, sticky="w", padx=10)
        ttk.Label(self, text="Shuma", font=("Arial", 10, "bold")).grid(row=4, column=1, sticky="w")

        # Deduction rows
        self.deduction_rows = []
        for i in range(self.NUM_DEDUCTION_ROWS):
            cat_var = tk.StringVar()
            amt_var = tk.StringVar()
            amt_var.trace_add('write', lambda *args: self.update_totals())
            cat_option = ttk.Combobox(self, textvariable=cat_var, values=self.categories.get("deduction", []), state="readonly")
            amt_entry = ttk.Entry(self, textvariable=amt_var)
            cat_option.grid(row=5 + i, column=0, padx=10, pady=2, sticky="ew")
            amt_entry.grid(row=5 + i, column=1, padx=10, pady=2, sticky="ew")
            self.deduction_rows.append((cat_var, amt_var))

        # Addition section header
        offset = 5 + self.NUM_DEDUCTION_ROWS
        ttk.Label(self, text="Plus", font=("Arial", 12, "bold")).grid(row=offset, column=0, pady=(15,5), sticky="w", padx=10)
        ttk.Label(self, text="Lloji", font=("Arial", 10, "bold")).grid(row=offset + 1, column=0, sticky="w", padx=10)
        ttk.Label(self, text="Shuma", font=("Arial", 10, "bold")).grid(row=offset + 1, column=1, sticky="w")
        self.addition_rows = []
        for i in range(self.NUM_ADDITION_ROWS):
            cat_var = tk.StringVar()
            amt_var = tk.StringVar()
            amt_var.trace_add('write', lambda *args: self.update_totals())
            cat_option = ttk.Combobox(self, textvariable=cat_var, values=self.categories.get("addition", []), state="readonly")
            amt_entry = ttk.Entry(self, textvariable=amt_var)
            cat_option.grid(row=offset + 2 + i, column=0, padx=10, pady=2, sticky="ew")
            amt_entry.grid(row=offset + 2 + i, column=1, padx=10, pady=2, sticky="ew")
            self.addition_rows.append((cat_var, amt_var))

        # Totals
        totals_start = offset + 2 + self.NUM_ADDITION_ROWS
        ttk.Label(self, text="Totali Zbritjeve:", font=("Arial", 10, "bold")).grid(row=totals_start, column=0, sticky="e", padx=10, pady=(15,2))
        self.total_ded_var = tk.StringVar(value="0.00")
        ttk.Label(self, textvariable=self.total_ded_var, font=("Arial", 10)).grid(row=totals_start, column=1, sticky="w")

        ttk.Label(self, text="Totali Plus:", font=("Arial", 10, "bold")).grid(row=totals_start + 1, column=0, sticky="e", padx=10)
        self.total_add_var = tk.StringVar(value="0.00")
        ttk.Label(self, textvariable=self.total_add_var, font=("Arial", 10)).grid(row=totals_start + 1, column=1, sticky="w")

        ttk.Label(self, text="Totali Net:", font=("Arial", 12, "bold")).grid(row=totals_start + 2, column=0, sticky="e", padx=10, pady=(5,10))
        self.total_net_var = tk.StringVar(value="0.00")
        ttk.Label(self, textvariable=self.total_net_var, font=("Arial", 12, "bold"), foreground="blue").grid(row=totals_start + 2, column=1, sticky="w", pady=(5,10))

        # Buttons
        button_row = totals_start + 3
        self.print_button = ttk.Button(self, text="Printo & Ruaj", command=self.print_and_save)
        self.print_button.grid(row=button_row, column=0, padx=10, pady=(10,10), sticky="e")
        self.logout_button = ttk.Button(self, text="Dil", command=self.app.logout)
        self.logout_button.grid(row=button_row, column=1, padx=10, pady=(10,10), sticky="w")

    def parse_amount(self, value):
        """Parse a numeric input and return a float.

        Empty strings or invalid inputs return 0.  This prevents exceptions
        during calculations.
        """
        value = value.strip().replace(',', '.') if isinstance(value, str) else value
        try:
            return float(value) if value else 0.0
        except (TypeError, ValueError):
            return 0.0

    def update_totals(self, *_):
        """Recompute totals whenever an amount is modified."""
        revenue = self.parse_amount(self.revenue_var.get())
        total_ded = 0.0
        for cat_var, amt_var in self.deduction_rows:
            total_ded += self.parse_amount(amt_var.get())
        total_add = 0.0
        for cat_var, amt_var in self.addition_rows:
            total_add += self.parse_amount(amt_var.get())
        net = revenue - total_ded + total_add
        self.total_ded_var.set(f"{total_ded:.2f}")
        self.total_add_var.set(f"{total_add:.2f}")
        self.total_net_var.set(f"{net:.2f}")

    def collect_entries(self):
        """Collect non‑empty deductions and additions into lists of tuples."""
        deductions = []
        for cat_var, amt_var in self.deduction_rows:
            cat = cat_var.get().strip()
            amt = self.parse_amount(amt_var.get())
            if cat and amt != 0.0:
                deductions.append((cat, amt))
        additions = []
        for cat_var, amt_var in self.addition_rows:
            cat = cat_var.get().strip()
            amt = self.parse_amount(amt_var.get())
            if cat and amt != 0.0:
                additions.append((cat, amt))
        return deductions, additions

    def print_and_save(self):
        """Validate the form, write the slip to disk and display a receipt preview."""
        # Validate revenue
        if not self.revenue_var.get().strip():
            messagebox.showwarning("Gabim", "Ju lutem shkruani Xhiron.")
            return
        revenue = self.parse_amount(self.revenue_var.get())
        # Collect entries
        deductions, additions = self.collect_entries()
        total_ded = sum(amt for _, amt in deductions)
        total_add = sum(amt for _, amt in additions)
        net = revenue - total_ded + total_add

        # Save slip to CSV
        date_str = self.date_var.get().strip()
        try:
            date_obj = datetime.datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Gabim", "Formati i dates duhet te jete YYYY-MM-DD.")
            return
        year_month = f"{date_obj.year:04d}-{date_obj.month:02d}"
        waiter_dir = os.path.join(SLIPS_DIR, self.waiter_name)
        os.makedirs(waiter_dir, exist_ok=True)
        csv_path = os.path.join(waiter_dir, f"{year_month}_{self.waiter_name}.csv")
        file_exists = os.path.isfile(csv_path)
        with open(csv_path, "a", newline="", encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)
            # Write header if file is new
            if not file_exists:
                writer.writerow([
                    "Date", "Revenue", "Total Deductions", "Total Additions", "Net", "Details"
                ])
            details = []
            for cat, amt in deductions:
                details.append(f"-{cat}:{amt:.2f}")
            for cat, amt in additions:
                details.append(f"+{cat}:{amt:.2f}")
            writer.writerow([
                date_str,
                f"{revenue:.2f}",
                f"{total_ded:.2f}",
                f"{total_add:.2f}",
                f"{net:.2f}",
                "; ".join(details)
            ])

        # Display a simple receipt preview
        receipt_lines = []
        receipt_lines.append("Slip Up Duff Arena")
        receipt_lines.append(f"Data: {date_str}")
        receipt_lines.append(f"Kamarieri: {self.waiter_name}")
        receipt_lines.append("---------------------------")
        receipt_lines.append(f"Xhiro: {revenue:.2f}")
        if deductions:
            receipt_lines.append("Zbritje:")
            for cat, amt in deductions:
                receipt_lines.append(f"  - {cat}: {amt:.2f}")
        if additions:
            receipt_lines.append("Plus:")
            for cat, amt in additions:
                receipt_lines.append(f"  + {cat}: {amt:.2f}")
        receipt_lines.append("---------------------------")
        receipt_lines.append(f"Tot. Zbritje: {total_ded:.2f}")
        receipt_lines.append(f"Tot. Plus: {total_add:.2f}")
        receipt_lines.append(f"Tot. Net: {net:.2f}")
        receipt_text = "\n".join(receipt_lines)
        messagebox.showinfo("Slip u ruajt", receipt_text)

        # Clear fields after saving
        self.revenue_var.set("")
        for cat_var, amt_var in self.deduction_rows:
            cat_var.set("")
            amt_var.set("")
        for cat_var, amt_var in self.addition_rows:
            cat_var.set("")
            amt_var.set("")
        self.update_totals()


class AdminPanel(ttk.Frame):
    """
    Frame for administrative tasks: managing users and categories and
    browsing saved slips.  Only accessible by the admin user.
    """

    def __init__(self, master, app):
        super().__init__(master)
        self.app = app
        self.categories = load_categories()
        self.users = load_users()
        self.build_ui()

    def build_ui(self):
        title = ttk.Label(self, text="Paneli i Adminit", font=("Arial", 16, "bold"))
        title.grid(row=0, column=0, columnspan=2, pady=(10,10))

        # Users management
        users_frame = ttk.LabelFrame(self, text="Menaxho kamarieret")
        users_frame.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")
        users_frame.columnconfigure(0, weight=1)
        self.user_listbox = tk.Listbox(users_frame, height=8)
        self.user_listbox.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        self.refresh_user_list()
        btn_frame = ttk.Frame(users_frame)
        btn_frame.grid(row=1, column=0, pady=(0,5))
        ttk.Button(btn_frame, text="Shto kamarier", command=self.add_waiter).grid(row=0, column=0, padx=5)
        ttk.Button(btn_frame, text="Fshi kamarier", command=self.delete_waiter).grid(row=0, column=1, padx=5)

        # Categories management
        cat_frame = ttk.LabelFrame(self, text="Menaxho kategorite")
        cat_frame.grid(row=1, column=1, padx=10, pady=5, sticky="nsew")
        cat_frame.columnconfigure(0, weight=1)
        self.cat_listbox = tk.Listbox(cat_frame, height=8)
        self.cat_listbox.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        self.refresh_cat_list()
        cat_btn_frame = ttk.Frame(cat_frame)
        cat_btn_frame.grid(row=1, column=0, pady=(0,5))
        ttk.Button(cat_btn_frame, text="Shto kategori", command=self.add_category).grid(row=0, column=0, padx=5)
        ttk.Button(cat_btn_frame, text="Fshi kategori", command=self.delete_category).grid(row=0, column=1, padx=5)

        # Slips browsing
        slips_frame = ttk.LabelFrame(self, text="Raportet mujore")
        slips_frame.grid(row=2, column=0, columnspan=2, padx=10, pady=5, sticky="nsew")
        slips_frame.columnconfigure(0, weight=1)
        self.slips_tree = ttk.Treeview(slips_frame, columns=("size",), show="headings")
        self.slips_tree.heading("size", text="Madhesia (B)" )
        self.slips_tree.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        ttk.Button(slips_frame, text="Fresko listën", command=self.refresh_slips_list).grid(row=1, column=0, pady=(0,5))
        self.refresh_slips_list()

        # Logout button
        ttk.Button(self, text="Dil", command=self.app.logout).grid(row=3, column=0, columnspan=2, pady=(10,10))

    def refresh_user_list(self):
        self.users = load_users()
        self.user_listbox.delete(0, tk.END)
        for user, info in self.users.items():
            if info.get("role") == "waiter":
                self.user_listbox.insert(tk.END, user)

    def refresh_cat_list(self):
        self.categories = load_categories()
        self.cat_listbox.delete(0, tk.END)
        # Show both deduction and addition categories with a prefix
        for cat in self.categories.get("deduction", []):
            self.cat_listbox.insert(tk.END, f"- {cat}")
        for cat in self.categories.get("addition", []):
            self.cat_listbox.insert(tk.END, f"+ {cat}")

    def refresh_slips_list(self):
        """Populate the treeview with monthly CSV files from slips directory."""
        # Clear existing
        for item in self.slips_tree.get_children():
            self.slips_tree.delete(item)
        # Iterate over waiter folders
        if not os.path.isdir(SLIPS_DIR):
            return
        for waiter_name in os.listdir(SLIPS_DIR):
            subdir = os.path.join(SLIPS_DIR, waiter_name)
            if os.path.isdir(subdir):
                for fname in os.listdir(subdir):
                    path = os.path.join(subdir, fname)
                    size = os.path.getsize(path)
                    self.slips_tree.insert("", tk.END, values=(fname, size))

    def add_waiter(self):
        """Prompt the admin for a new waiter name and password and add them."""
        username = simpledialog.askstring("Emri i kamarierit", "Shkruaj emrin e kamarierit:")
        if not username:
            return
        if username in self.users:
            messagebox.showerror("Gabim", "Ky kamarier ekziston tashme.")
            return
        password = simpledialog.askstring("Fjalekalimi", "Vendos fjalekalimin:", show='*')
        if not password:
            return
        self.users[username] = {"password": password, "role": "waiter"}
        save_users(self.users)
        self.refresh_user_list()

    def delete_waiter(self):
        """Delete the selected waiter from the list."""
        selection = self.user_listbox.curselection()
        if not selection:
            return
        idx = selection[0]
        waiter_name = self.user_listbox.get(idx)
        if messagebox.askyesno("Konfirmo", f"A deshironi te fshini kamarierin {waiter_name}?"):
            self.users.pop(waiter_name, None)
            save_users(self.users)
            self.refresh_user_list()

    def add_category(self):
        """Prompt for category type and name and add it."""
        cat_type = simpledialog.askstring("Lloji", "Shkruani llojin (deduction ose addition):")
        if not cat_type:
            return
        cat_type = cat_type.lower().strip()
        if cat_type not in ("deduction", "addition"):
            messagebox.showerror("Gabim", "Lloji i panjohur. Përdorni 'deduction' ose 'addition'.")
            return
        name = simpledialog.askstring("Emri i kategorisë", "Shkruani emrin e kategorisë:")
        if not name:
            return
        # Avoid duplicates
        if name in self.categories.get(cat_type, []):
            messagebox.showerror("Gabim", "Kategoria ekziston tashmë.")
            return
        self.categories.setdefault(cat_type, []).append(name)
        save_categories(self.categories)
        self.refresh_cat_list()

    def delete_category(self):
        """Delete the selected category from the list."""
        selection = self.cat_listbox.curselection()
        if not selection:
            return
        idx = selection[0]
        item = self.cat_listbox.get(idx)
        # Determine type based on prefix
        if item.startswith("- "):
            cat_type = "deduction"
            name = item[2:]
        else:
            cat_type = "addition"
            name = item[2:]
        if messagebox.askyesno("Konfirmo", f"A deshironi te fshini kategorinë {name}?"):
            try:
                self.categories[cat_type].remove(name)
            except ValueError:
                pass
            save_categories(self.categories)
            self.refresh_cat_list()


class LoginFrame(ttk.Frame):
    """
    Initial login frame offering a choice between admin and waiter access.

    Admin login requires only a password (username fixed to ``admin``).  Waiters
    select their username from a drop‑down list and enter their password.
    """

    def __init__(self, master, app):
        super().__init__(master)
        self.app = app
        self.users = load_users()
        self.build_ui()

    def build_ui(self):
        ttk.Label(self, text="Hyrja", font=("Arial", 16, "bold")).grid(row=0, column=0, columnspan=2, pady=(20,10))

        # Admin button
        admin_btn = ttk.Button(self, text="Admin", command=self.admin_login)
        admin_btn.grid(row=1, column=0, padx=10, pady=10)
        # Waiter button
        waiter_btn = ttk.Button(self, text="Kamarier", command=self.waiter_login)
        waiter_btn.grid(row=1, column=1, padx=10, pady=10)

    def admin_login(self):
        pwd = simpledialog.askstring("Admin", "Fjalekalimi:", show='*')
        if pwd is None:
            return
        users = load_users()
        if users.get("admin", {}).get("password") == pwd:
            self.app.show_admin_panel()
        else:
            messagebox.showerror("Gabim", "Fjalekalimi i gabuar")

    def waiter_login(self):
        users = load_users()
        # Build a list of waiter usernames
        waiter_names = [name for name, info in users.items() if info.get("role") == "waiter"]
        if not waiter_names:
            messagebox.showinfo("Info", "Nuk ka kamarierë të regjistruar.")
            return
        # Ask for username selection
        login_win = tk.Toplevel(self)
        login_win.title("Hyrja e kamarierit")
        ttk.Label(login_win, text="Zgjidh emrin:").grid(row=0, column=0, padx=10, pady=10)
        name_var = tk.StringVar(value=waiter_names[0])
        combo = ttk.Combobox(login_win, textvariable=name_var, values=waiter_names, state="readonly")
        combo.grid(row=0, column=1, padx=10, pady=10)
        ttk.Label(login_win, text="Fjalekalimi:").grid(row=1, column=0, padx=10, pady=10)
        pwd_var = tk.StringVar()
        pwd_entry = ttk.Entry(login_win, textvariable=pwd_var, show='*')
        pwd_entry.grid(row=1, column=1, padx=10, pady=10)
        def do_login():
            username = name_var.get()
            password = pwd_var.get()
            if users.get(username, {}).get("password") == password:
                login_win.destroy()
                self.app.show_waiter_form(username)
            else:
                messagebox.showerror("Gabim", "Fjalekalimi i gabuar")
        ttk.Button(login_win, text="Hyr", command=do_login).grid(row=2, column=0, columnspan=2, pady=(10,10))


class SlipUpApp(tk.Tk):
    """Main application class that manages switching between frames."""
    def __init__(self):
        super().__init__()
        self.title("Slip Up Duff Arena")
        # Ensure required files exist
        ensure_data_files()
        # Container for frames
        self.current_frame = None
        self.show_login()

    def clear_frame(self):
        if self.current_frame:
            self.current_frame.destroy()

    def show_login(self):
        self.clear_frame()
        self.current_frame = LoginFrame(self, self)
        self.current_frame.pack(fill="both", expand=True)

    def show_waiter_form(self, waiter_name):
        self.clear_frame()
        self.current_frame = SlipForm(self, self, waiter_name)
        self.current_frame.pack(fill="both", expand=True)

    def show_admin_panel(self):
        self.clear_frame()
        self.current_frame = AdminPanel(self, self)
        self.current_frame.pack(fill="both", expand=True)

    def logout(self):
        self.show_login()


def main():
    app = SlipUpApp()
    app.mainloop()


if __name__ == "__main__":
    main()