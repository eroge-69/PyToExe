import tkinter as tk
from tkinter import messagebox, simpledialog
import json, os, random, string
from datetime import datetime, timedelta

DATA_FILE = "rental_data.json"
OWNER_PASSWORD = "isalaadmin123"
RENTAL_PERIOD_DAYS = 3

# Load / Save data
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {"inventory": [], "rentals": [], "history": {}}

def save_data():
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

# Generate random code
def generate_code(length=5):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

data = load_data()

# Tkinter App
root = tk.Tk()
root.title("Filming Equipment Rental System")
root.geometry("600x400")

def login():
    role = role_var.get()
    name = username_entry.get().strip()
    if role == "Owner":
        if name == OWNER_PASSWORD:
            owner_dashboard()
        else:
            messagebox.showerror("Error", "Wrong password!")
    elif role == "Renter":
        if name == "":
            messagebox.showerror("Error", "Enter production house name")
        else:
            renter_dashboard(name)

def clear_window():
    for widget in root.winfo_children():
        widget.destroy()

def owner_dashboard():
    clear_window()
    tk.Label(root, text="Owner Dashboard", font=("Arial", 16)).pack()

    def add_item():
        item = simpledialog.askstring("Add Item", "Enter item name:")
        if item:
            data["inventory"].append(item)
            save_data()
            refresh_lists()

    def remove_item():
        selected = inv_list.curselection()
        if selected:
            item = inv_list.get(selected[0])
            data["inventory"].remove(item)
            save_data()
            refresh_lists()

    def refresh_lists():
        inv_list.delete(0, tk.END)
        rent_list.delete(0, tk.END)
        for item in data["inventory"]:
            inv_list.insert(tk.END, item)
        for r in data["rentals"]:
            rent_list.insert(tk.END, f"{r['item']} | {r['code']} | {r['renter']} | Due: {r['due']}")

    def view_history():
        crew = simpledialog.askstring("History", "Enter crew name:")
        if crew in data["history"]:
            records = "\n".join([f"{h['item']} | {h['code']} | Rented: {h['rented']} | Returned: {h.get('returned', 'Not yet')}" for h in data["history"][crew]])
            messagebox.showinfo("Rental History", records)
        else:
            messagebox.showinfo("Rental History", "No records for this crew.")

    tk.Button(root, text="Add Item", command=add_item).pack()
    tk.Button(root, text="Remove Item", command=remove_item).pack()
    tk.Button(root, text="View Crew History", command=view_history).pack()

    tk.Label(root, text="Available Inventory:").pack()
    inv_list = tk.Listbox(root)
    inv_list.pack(fill=tk.BOTH, expand=True)

    tk.Label(root, text="Current Rentals:").pack()
    rent_list = tk.Listbox(root)
    rent_list.pack(fill=tk.BOTH, expand=True)

    tk.Button(root, text="Logout", command=start_screen).pack(pady=5)
    refresh_lists()

def renter_dashboard(renter_name):
    clear_window()
    tk.Label(root, text=f"Renter: {renter_name}", font=("Arial", 16)).pack()

    def refresh_available():
        available_list.delete(0, tk.END)
        rented_items = [r['item'] for r in data["rentals"]]
        for item in data["inventory"]:
            if item not in rented_items:
                available_list.insert(tk.END, item)

    def rent_item():
        selected = available_list.curselection()
        if not selected:
            messagebox.showerror("Error", "Select an item")
            return
        # Check overdue
        for r in data["rentals"]:
            if r["renter"] == renter_name and datetime.strptime(r["due"], "%Y-%m-%d") < datetime.now():
                messagebox.showerror("Error", "You have overdue items!")
                return
        item = available_list.get(selected[0])
        code = generate_code()
        rent_date = datetime.now().strftime("%Y-%m-%d")
        due_date = (datetime.now() + timedelta(days=RENTAL_PERIOD_DAYS)).strftime("%Y-%m-%d")
        
        data["rentals"].append({"item": item, "code": code, "renter": renter_name,
                                "rented": rent_date, "due": due_date})
        if renter_name not in data["history"]:
            data["history"][renter_name] = []
        data["history"][renter_name].append({"item": item, "code": code, "rented": rent_date})
        save_data()
        messagebox.showinfo("Rented", f"Code: {code}\nDue Date: {due_date}")
        refresh_available()

    def return_item():
        code = simpledialog.askstring("Return Item", "Enter rental code:")
        if code:
            for r in data["rentals"]:
                if r["code"] == code and r["renter"] == renter_name:
                    data["rentals"].remove(r)
                    # Update history with return date
                    for h in data["history"][renter_name]:
                        if h["code"] == code and "returned" not in h:
                            h["returned"] = datetime.now().strftime("%Y-%m-%d")
                    save_data()
                    messagebox.showinfo("Returned", f"{r['item']} returned successfully")
                    refresh_available()
                    return
            messagebox.showerror("Error", "Invalid code or not rented by you")

    tk.Label(root, text="Available Items:").pack()
    available_list = tk.Listbox(root)
    available_list.pack(fill=tk.BOTH, expand=True)

    tk.Button(root, text="Rent Selected", command=rent_item).pack()
    tk.Button(root, text="Return Item", command=return_item).pack()
    tk.Button(root, text="Logout", command=start_screen).pack(pady=5)
    refresh_available()

def start_screen():
    clear_window()
    tk.Label(root, text="Login", font=("Arial", 16)).pack()
    tk.Label(root, text="Select Role:").pack()
    global role_var, username_entry
    role_var = tk.StringVar(value="Owner")
    tk.Radiobutton(root, text="Owner", variable=role_var, value="Owner").pack()
    tk.Radiobutton(root, text="Renter", variable=role_var, value="Renter").pack()
    tk.Label(root, text="Password (Owner) or Name (Renter):").pack()
    username_entry = tk.Entry(root)
    username_entry.pack()
    tk.Button(root, text="Login", command=login).pack()

start_screen()
root.mainloop()
