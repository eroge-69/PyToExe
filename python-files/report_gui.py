import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import mysql.connector
import pandas as pd
from datetime import datetime
import json
import os
from tkinter import simpledialog

PROFILE_FILE = "profiles.json"
DEFAULT_PROFILES = {
    "Server1": {
        "host": "10.10.10.64",
        "user": "root",
        "password": "nano1545",
        "database": "kalypso_v24"
    },
    "Server2": {
        "host": "127.0.0.1",
        "user": "user2",
        "password": "pass2",
        "database": "db2"
    },
    "Server3": {
        "host": "192.168.1.100",
        "user": "user3",
        "password": "pass3",
        "database": "db3"
    }
}

def load_profiles():
    if not os.path.exists(PROFILE_FILE):
        with open(PROFILE_FILE, "w", encoding="utf-8") as f:
            json.dump(DEFAULT_PROFILES, f, indent=2)
        return DEFAULT_PROFILES
    with open(PROFILE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_profiles(profiles):
    with open(PROFILE_FILE, "w", encoding="utf-8") as f:
        json.dump(profiles, f, indent=2)

# Συνάρτηση για σύνδεση στη βάση και ανάκτηση δεδομένων

def get_sales_data(host, user, password, database, date_from=None, date_to=None):
    try:
        conn = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )
        cursor = conn.cursor()
        # Προσπάθεια για αγγλικά, αν αποτύχει δοκιμή για ελληνικά
        try:
            cursor.execute("SET lc_messages = 'en_US'")
        except Exception:
            try:
                cursor.execute("SET lc_messages = 'el_GR'")
            except Exception:
                pass  # Αν δεν υπάρχει ούτε ελληνικά, συνέχισε χωρίς αλλαγή
        query = "SELECT perig, axia, fpa, created_at FROM trans_ap"
        params = []
        if date_from and date_to:
            query += " WHERE created_at BETWEEN %s AND %s"
            params = [date_from, date_to]
        elif date_from:
            query += " WHERE created_at >= %s"
            params = [date_from]
        elif date_to:
            query += " WHERE created_at <= %s"
            params = [date_to]
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        return rows
    except Exception as e:
        messagebox.showerror("Σφάλμα Σύνδεσης", str(e))
        return []

# GUI
class SalesReportApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Αναφορά Πωλήσεων Προϊόντων")
        self.create_widgets()
        self.sales_data = []

    def create_widgets(self):
        # Load profiles
        self.profiles = load_profiles()
        self.profile_names = list(self.profiles.keys())
        # Profile selection
        frame_profile = ttk.Frame(self.root)
        frame_profile.pack(fill="x", padx=10, pady=5)
        ttk.Label(frame_profile, text="Select Profile:").pack(side="left", padx=5)
        self.profile_var = tk.StringVar()
        self.combo_profile = ttk.Combobox(frame_profile, textvariable=self.profile_var, values=self.profile_names, state="readonly")
        self.combo_profile.pack(side="left", padx=5)
        self.combo_profile.bind("<<ComboboxSelected>>", self.on_profile_select)
        # Add/Delete/Rename Profile buttons
        self.btn_add_profile = ttk.Button(frame_profile, text="Add Profile", command=self.add_profile)
        self.btn_add_profile.pack(side="left", padx=2)
        self.btn_delete_profile = ttk.Button(frame_profile, text="Delete Profile", command=self.delete_profile)
        self.btn_delete_profile.pack(side="left", padx=2)
        self.btn_rename_profile = ttk.Button(frame_profile, text="Rename Profile", command=self.rename_profile)
        self.btn_rename_profile.pack(side="left", padx=2)

        # Connection frame
        frame_conn = ttk.LabelFrame(self.root, text="Database Connection")
        frame_conn.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(frame_conn, text="Host:").grid(row=0, column=0, padx=5, pady=2)
        self.entry_host = ttk.Entry(frame_conn)
        self.entry_host.grid(row=0, column=1, padx=5, pady=2)
        self.entry_host.insert(0, "10.10.10.64")

        ttk.Label(frame_conn, text="User:").grid(row=0, column=2, padx=5, pady=2)
        self.entry_user = ttk.Entry(frame_conn)
        self.entry_user.grid(row=0, column=3, padx=5, pady=2)
        self.entry_user.insert(0, "root")

        ttk.Label(frame_conn, text="Password:").grid(row=0, column=4, padx=5, pady=2)
        self.entry_password = ttk.Entry(frame_conn, show="*")
        self.entry_password.grid(row=0, column=5, padx=5, pady=2)
        self.entry_password.insert(0, "nano1545")

        ttk.Label(frame_conn, text="Database:").grid(row=0, column=6, padx=5, pady=2)
        self.entry_database = ttk.Entry(frame_conn)
        self.entry_database.grid(row=0, column=7, padx=5, pady=2)
        self.entry_database.insert(0, "kalypso_v24")

        # Date filter frame
        frame_filter = ttk.LabelFrame(self.root, text="Date Filters (optional)")
        frame_filter.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(frame_filter, text="From (YYYY-MM-DD):").grid(row=0, column=0, padx=5, pady=2)
        self.entry_date_from = ttk.Entry(frame_filter)
        self.entry_date_from.grid(row=0, column=1, padx=5, pady=2)
        
        ttk.Label(frame_filter, text="To (YYYY-MM-DD):").grid(row=0, column=2, padx=5, pady=2)
        self.entry_date_to = ttk.Entry(frame_filter)
        self.entry_date_to.grid(row=0, column=3, padx=5, pady=2)

        # Buttons
        frame_btn = ttk.Frame(self.root)
        frame_btn.pack(fill="x", padx=10, pady=5)
        
        self.btn_fetch = ttk.Button(frame_btn, text="Show Sales", command=self.fetch_sales)
        self.btn_fetch.pack(side="left", padx=5)
        
        self.btn_export = ttk.Button(frame_btn, text="Export to Excel", command=self.export_excel, state="disabled")
        self.btn_export.pack(side="left", padx=5)

        self.btn_save = ttk.Button(frame_btn, text="Save Connection", command=self.save_connection)
        self.btn_save.pack(side="left", padx=5)

        self.btn_clear = ttk.Button(frame_btn, text="Clear", command=self.clear_fields)
        self.btn_clear.pack(side="left", padx=5)

        # Search/filter frame
        frame_search = ttk.LabelFrame(self.root, text="Search/Filters")
        frame_search.pack(fill="x", padx=10, pady=5)
        ttk.Label(frame_search, text="Product search:").grid(row=0, column=0, padx=5, pady=2)
        self.entry_search = ttk.Entry(frame_search)
        self.entry_search.grid(row=0, column=1, padx=5, pady=2)
        ttk.Label(frame_search, text="Price equals:").grid(row=0, column=2, padx=5, pady=2)
        self.entry_price = ttk.Entry(frame_search)
        self.entry_price.grid(row=0, column=3, padx=5, pady=2)

        # Total label (above table)
        self.label_total = ttk.Label(self.root, text="Total: 0.00", font=("Arial", 12, "bold"))
        self.label_total.pack(padx=10, pady=2)

        # Table with scrollbar
        frame_table = ttk.Frame(self.root)
        frame_table.pack(fill="both", expand=True, padx=10, pady=5)
        self.tree = ttk.Treeview(frame_table, columns=("perig", "axia", "fpa", "created_at"), show="headings")
        self.tree.heading("perig", text="Product")
        self.tree.heading("axia", text="Price")
        self.tree.heading("fpa", text="VAT")
        self.tree.heading("created_at", text="Sale Date")
        self.tree.column("axia", anchor="center")
        self.tree.column("fpa", anchor="center")
        vsb = ttk.Scrollbar(frame_table, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        self.tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")

        # Set default profile if exists
        if self.profile_names:
            self.combo_profile.current(0)
            self.on_profile_select()

    def on_profile_select(self, event=None):
        name = self.profile_var.get()
        if name and name in self.profiles:
            prof = self.profiles[name]
            self.entry_host.delete(0, tk.END)
            self.entry_host.insert(0, prof.get("host", ""))
            self.entry_user.delete(0, tk.END)
            self.entry_user.insert(0, prof.get("user", ""))
            self.entry_password.delete(0, tk.END)
            self.entry_password.insert(0, prof.get("password", ""))
            self.entry_database.delete(0, tk.END)
            self.entry_database.insert(0, prof.get("database", ""))

    def save_connection(self):
        # Save connection details to file
        try:
            with open("connection.txt", "w", encoding="utf-8") as f:
                f.write(f"host={self.entry_host.get()}\n")
                f.write(f"user={self.entry_user.get()}\n")
                f.write(f"password={self.entry_password.get()}\n")
                f.write(f"database={self.entry_database.get()}\n")
            # Ενημέρωση του τρέχοντος προφίλ αν υπάρχει
            name = self.profile_var.get()
            if name and name in self.profiles:
                self.profiles[name] = {
                    "host": self.entry_host.get(),
                    "user": self.entry_user.get(),
                    "password": self.entry_password.get(),
                    "database": self.entry_database.get()
                }
                save_profiles(self.profiles)
            messagebox.showinfo("Success", "Connection details saved!")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def clear_fields(self):
        # Clear all fields
        self.entry_host.delete(0, tk.END)
        self.entry_user.delete(0, tk.END)
        self.entry_password.delete(0, tk.END)
        self.entry_database.delete(0, tk.END)
        self.entry_date_from.delete(0, tk.END)
        self.entry_date_to.delete(0, tk.END)
        self.entry_search.delete(0, tk.END)
        self.entry_price.delete(0, tk.END)
        self.label_total.config(text="Total: 0.00")
        for i in self.tree.get_children():
            self.tree.delete(i)
        self.btn_export.config(state="disabled")

    def fetch_sales(self):
        host = self.entry_host.get()
        user = self.entry_user.get()
        password = self.entry_password.get()
        database = self.entry_database.get()
        date_from = self.entry_date_from.get().strip() or None
        date_to = self.entry_date_to.get().strip() or None
        # Date validation
        for d in [date_from, date_to]:
            if d:
                try:
                    from datetime import datetime
                    datetime.strptime(d, "%Y-%m-%d")
                except ValueError:
                    messagebox.showerror("Date Error", f"Invalid date format: {d}")
                    return
        self.sales_data = get_sales_data(host, user, password, database, date_from, date_to)
        self.update_table_view()

    def update_table_view(self):
        # Apply filters and search
        search = self.entry_search.get().strip().lower()
        price = self.entry_price.get().strip()
        filtered = []
        total = 0
        for row in self.sales_data:
            # row: (perig, axia, fpa, created_at)
            if search and search not in str(row[0]).lower():
                continue
            if price:
                try:
                    if float(row[1]) != float(price):
                        continue
                except:
                    continue
            filtered.append(row)
            try:
                total += float(row[1])
            except:
                pass
        # Clear table
        for i in self.tree.get_children():
            self.tree.delete(i)
        for row in filtered:
            self.tree.insert("", "end", values=tuple(row))
        self.label_total.config(text=f"Total: {total:.2f}")
        if filtered:
            self.btn_export.config(state="normal")
        else:
            self.btn_export.config(state="disabled")

    def export_excel(self):
        # Εξαγωγή μόνο των φιλτραρισμένων δεδομένων και προσθήκη συνόλου
        # Apply filters as στο update_table_view
        search = self.entry_search.get().strip().lower()
        price = self.entry_price.get().strip()
        filtered = []
        total = 0
        for row in self.sales_data:
            if search and search not in str(row[0]).lower():
                continue
            if price:
                try:
                    if float(row[1]) != float(price):
                        continue
                except:
                    continue
            filtered.append(row)
            try:
                total += float(row[1])
            except:
                pass
        if not filtered:
            messagebox.showwarning("Warning", "No data to export!")
            return
        file_path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel Files", "*.xlsx")])
        if not file_path:
            return
        import pandas as pd
        df = pd.DataFrame(filtered, columns=["Product", "Price", "VAT", "Sale Date"])
        # Προσθήκη γραμμής συνόλου
        total_row = ["TOTAL", total, "", ""]
        df.loc[len(df)] = total_row
        try:
            df.to_excel(file_path, index=False)
            messagebox.showinfo("Success", f"File saved: {file_path}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def add_profile(self):
        # Άνοιγμα διαλόγου για όνομα νέου προφίλ
        name = simpledialog.askstring("Add Profile", "Enter new profile name:")
        if not name:
            return
        if name in self.profiles:
            messagebox.showerror("Error", "Profile already exists!")
            return
        # Παίρνει τα τρέχοντα στοιχεία σύνδεσης
        prof = {
            "host": self.entry_host.get(),
            "user": self.entry_user.get(),
            "password": self.entry_password.get(),
            "database": self.entry_database.get()
        }
        self.profiles[name] = prof
        save_profiles(self.profiles)
        self.profile_names = list(self.profiles.keys())
        self.combo_profile["values"] = self.profile_names
        self.profile_var.set(name)
        self.on_profile_select()
        messagebox.showinfo("Success", f"Profile '{name}' added.")

    def delete_profile(self):
        name = self.profile_var.get()
        if not name:
            return
        if name not in self.profiles:
            return
        if messagebox.askyesno("Delete Profile", f"Are you sure you want to delete profile '{name}'?"):
            del self.profiles[name]
            save_profiles(self.profiles)
            self.profile_names = list(self.profiles.keys())
            self.combo_profile["values"] = self.profile_names
            if self.profile_names:
                self.profile_var.set(self.profile_names[0])
                self.on_profile_select()
            else:
                self.profile_var.set("")
            messagebox.showinfo("Success", f"Profile '{name}' deleted.")

    def rename_profile(self):
        old_name = self.profile_var.get()
        if not old_name or old_name not in self.profiles:
            return
        new_name = simpledialog.askstring("Rename Profile", "Enter new profile name:", initialvalue=old_name)
        if not new_name or new_name == old_name:
            return
        if new_name in self.profiles:
            messagebox.showerror("Error", "Profile with this name already exists!")
            return
        self.profiles[new_name] = self.profiles.pop(old_name)
        save_profiles(self.profiles)
        self.profile_names = list(self.profiles.keys())
        self.combo_profile["values"] = self.profile_names
        self.profile_var.set(new_name)
        self.on_profile_select()
        messagebox.showinfo("Success", f"Profile renamed to '{new_name}'.")

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Product Sales Report")
    app = SalesReportApp(root)
    root.mainloop() 