import tkinter as tk
from tkinter import messagebox

# Sample inventory data
inventory = {
    "TUK001": {"description": "Three Wheeler Brake Pad", "unit_price": 500, "quantity": 50},
    "TUK002": {"description": "Three Wheeler Clutch Cable", "unit_price": 700, "quantity": 30},
    "TUK003": {"description": "Three Wheeler Headlight Bulb", "unit_price": 250, "quantity": 100},
    "TUK004": {"description": "Three Wheeler Engine Oil", "unit_price": 1200, "quantity": 20},
    "TUK005": {"description": "Three Wheeler Air Filter", "unit_price": 600, "quantity": 15},
}

bill = []

def search_parts(event=None):
    query = entry_search.get().strip().lower()
    listbox_suggestions.delete(0, tk.END)
    if not query:
        listbox_suggestions.place_forget()
        return

    matches = []
    for code, info in inventory.items():
        if query in code.lower() or query in info['description'].lower():
            matches.append(f"{code} - {info['description']}")

    if matches:
        for item in matches:
            listbox_suggestions.insert(tk.END, item)
        listbox_suggestions.place(x=entry_search.winfo_x(),
                                  y=entry_search.winfo_y() + entry_search.winfo_height())
        listbox_suggestions.selection_set(0)
        listbox_suggestions.activate(0)
    else:
        listbox_suggestions.place_forget()

def fill_from_selection(event=None):
    if listbox_suggestions.curselection():
        index = listbox_suggestions.curselection()[0]
        selected = listbox_suggestions.get(index)
        entry_search.delete(0, tk.END)
        entry_search.insert(0, selected)
        listbox_suggestions.place_forget()
        entry_qty.focus_set()

def on_down_key(event):
    if listbox_suggestions.size() > 0:
        listbox_suggestions.focus_set()
        listbox_suggestions.selection_set(0)
        listbox_suggestions.activate(0)

def on_listbox_down(event):
    try:
        index = listbox_suggestions.curselection()[0]
        listbox_suggestions.selection_clear(index)
        index += 1
        if index >= listbox_suggestions.size():
            index = 0
        listbox_suggestions.selection_set(index)
        listbox_suggestions.activate(index)
    except IndexError:
        listbox_suggestions.selection_set(0)

def on_listbox_up(event):
    try:
        index = listbox_suggestions.curselection()[0]
        listbox_suggestions.selection_clear(index)
        index -= 1
        if index < 0:
            index = listbox_suggestions.size() - 1
        listbox_suggestions.selection_set(index)
        listbox_suggestions.activate(index)
    except IndexError:
        listbox_suggestions.selection_set(0)

def add_to_bill():
    search_text = entry_search.get().strip()
    if " - " in search_text:
        code = search_text.split(" - ")[0]
    else:
        code = search_text

    if not code:
        messagebox.showerror("Error", "Please select or enter a valid part code.")
        return

    if code not in inventory:
        messagebox.showerror("Error", "Part code not found in inventory.")
        return

    qty_str = entry_qty.get().strip()
    if not qty_str:
        messagebox.showerror("Error", "Please enter quantity.")
        return
    try:
        qty = int(qty_str)
        if qty <= 0:
            raise ValueError
    except ValueError:
        messagebox.showerror("Error", "Quantity must be a positive integer.")
        return

    already_in_bill = next((item for item in bill if item['code'] == code), None)
    already_qty = already_in_bill['quantity'] if already_in_bill else 0

    if qty + already_qty > inventory[code]["quantity"]:
        messagebox.showerror("Error", f"Insufficient stock. Available: {inventory[code]['quantity'] - already_qty}")
        return

    if already_in_bill:
        already_in_bill['quantity'] += qty
    else:
        bill.append({
            "code": code,
            "description": inventory[code]["description"],
            "quantity": qty,
            "unit_price": inventory[code]["unit_price"]
        })

    update_bill_display()
    entry_search.delete(0, tk.END)
    entry_qty.delete(0, tk.END)
    entry_search.focus_set()

def update_bill_display():
    text_bill.config(state='normal')
    text_bill.delete(1.0, tk.END)
    text_bill.insert(tk.END, f"{'Code':10} {'Description':40} {'Qty':>5} {'Unit Price':>12} {'Total':>12}\n")
    text_bill.insert(tk.END, "-" * 95 + "\n")
    total_amount = 0
    for item in bill:
        line_total = item['quantity'] * item['unit_price']
        total_amount += line_total
        text_bill.insert(tk.END, f"{item['code']:10} {item['description'][:40]:40} {item['quantity']:>5} "
                                 f"{item['unit_price']:12.2f} {line_total:12.2f}\n")
    text_bill.insert(tk.END, "-" * 95 + "\n")
    text_bill.insert(tk.END, f"{'Total Amount:':>77} {total_amount:12.2f}\n")
    text_bill.config(state='disabled')

def checkout():
    if not bill:
        messagebox.showinfo("Info", "No items in bill to checkout.")
        return

    total_amount = 0
    for item in bill:
        inventory[item["code"]]["quantity"] -= item["quantity"]
        total_amount += item["quantity"] * item["unit_price"]

    bill_window = tk.Toplevel(window)
    bill_window.title("Final Bill")
    text_final = tk.Text(bill_window, width=100, height=20, font=("Courier New", 10))
    text_final.pack(padx=10, pady=10)

    text_final.insert(tk.END, f"{'Code':10} {'Description':40} {'Qty':>5} {'Unit Price':>12} {'Total':>12}\n")
    text_final.insert(tk.END, "-" * 95 + "\n")

    for item in bill:
        line_total = item['quantity'] * item['unit_price']
        text_final.insert(tk.END, f"{item['code']:10} {item['description'][:40]:40} {item['quantity']:>5} "
                                  f"{item['unit_price']:12.2f} {line_total:12.2f}\n")

    text_final.insert(tk.END, "-" * 95 + "\n")
    text_final.insert(tk.END, f"{'Grand Total:':>77} {total_amount:12.2f}\n")
    text_final.config(state='disabled')

    bill.clear()
    update_bill_display()
    messagebox.showinfo("Success", "Checkout complete. Inventory updated.")

def add_new_part_window():
    def add_part():
        code = entry_code.get().strip().upper()
        desc = entry_desc.get().strip()
        price_str = entry_price.get().strip()
        qty_str = entry_qty_add.get().strip()

        if not code or not desc or not price_str or not qty_str:
            messagebox.showerror("Error", "All fields are required.")
            return

        if code in inventory:
            messagebox.showerror("Error", "Part code already exists.")
            return

        try:
            price = float(price_str)
            if price < 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Unit price must be a positive number.")
            return

        try:
            qty = int(qty_str)
            if qty < 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Quantity must be a positive integer.")
            return

        inventory[code] = {"description": desc, "unit_price": price, "quantity": qty}
        messagebox.showinfo("Success", f"Part {code} added to inventory.")
        add_part_win.destroy()

    add_part_win = tk.Toplevel(window)
    add_part_win.title("Add New Part")

    tk.Label(add_part_win, text="Part Code:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
    entry_code = tk.Entry(add_part_win)
    entry_code.grid(row=0, column=1, padx=5, pady=5)

    tk.Label(add_part_win, text="Description:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
    entry_desc = tk.Entry(add_part_win)
    entry_desc.grid(row=1, column=1, padx=5, pady=5)

    tk.Label(add_part_win, text="Unit Price:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
    entry_price = tk.Entry(add_part_win)
    entry_price.grid(row=2, column=1, padx=5, pady=5)

    tk.Label(add_part_win, text="Quantity:").grid(row=3, column=0, sticky="w", padx=5, pady=5)
    entry_qty_add = tk.Entry(add_part_win)
    entry_qty_add.grid(row=3, column=1, padx=5, pady=5)

    btn_add = tk.Button(add_part_win, text="Add Part", command=add_part)
    btn_add.grid(row=4, column=0, columnspan=2, pady=10)

def view_inventory():
    def update_inventory_display(filter_text=""):
        text_inv.config(state='normal')
        text_inv.delete(1.0, tk.END)
        text_inv.insert(tk.END, f"{'Code':10} {'Description':30} {'Qty':>5} {'Unit Price':>10}\n")
        text_inv.insert(tk.END, "-" * 60 + "\n")
        for code, info in inventory.items():
            if filter_text.lower() in code.lower() or filter_text.lower() in info['description'].lower():
                text_inv.insert(tk.END, f"{code:10} {info['description'][:30]:30} {info['quantity']:>5} {info['unit_price']:>10.2f}\n")
        text_inv.config(state='disabled')

    def on_inventory_search(event):
        query = entry_inv_search.get().strip()
        update_inventory_display(query)

    def on_select(event):
        try:
            line_index = text_inv.index(tk.CURRENT).split('.')[0]
            line = text_inv.get(f"{line_index}.0", f"{line_index}.end").strip()
            if line.startswith("Code") or line.startswith("-") or not line:
                return
            code = line.split()[0]
            # Load details into edit fields
            entry_code_edit.config(state='normal')
            entry_code_edit.delete(0, tk.END)
            entry_code_edit.insert(0, code)
            entry_code_edit.config(state='disabled')  # Prevent editing code

            entry_desc_edit.delete(0, tk.END)
            entry_desc_edit.insert(0, inventory[code]['description'])

            entry_qty_edit.delete(0, tk.END)
            entry_qty_edit.insert(0, str(inventory[code]['quantity']))

            entry_price_edit.delete(0, tk.END)
            entry_price_edit.insert(0, str(inventory[code]['unit_price']))
        except Exception:
            pass

    def save_changes():
        code = entry_code_edit.get()
        if not code:
            messagebox.showerror("Error", "No part selected.")
            return
        desc = entry_desc_edit.get().strip()
        qty_str = entry_qty_edit.get().strip()
        price_str = entry_price_edit.get().strip()

        if not desc or not qty_str or not price_str:
            messagebox.showerror("Error", "All fields are required.")
            return

        try:
            qty = int(qty_str)
            if qty < 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Quantity must be a positive integer.")
            return

        try:
            price = float(price_str)
            if price < 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Unit price must be a positive number.")
            return

        inventory[code] = {"description": desc, "quantity": qty, "unit_price": price}
        messagebox.showinfo("Success", f"Part {code} updated.")
        update_inventory_display(entry_inv_search.get())

    def delete_part():
        code = entry_code_edit.get()
        if not code:
            messagebox.showerror("Error", "No part selected.")
            return

        confirm = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete part {code}?")
        if confirm:
            inventory.pop(code, None)
            messagebox.showinfo("Deleted", f"Part {code} deleted from inventory.")
            entry_code_edit.config(state='normal')
            entry_code_edit.delete(0, tk.END)
            entry_code_edit.config(state='disabled')
            entry_desc_edit.delete(0, tk.END)
            entry_qty_edit.delete(0, tk.END)
            entry_price_edit.delete(0, tk.END)
            update_inventory_display(entry_inv_search.get())

    inv_win = tk.Toplevel(window)
    inv_win.title("Inventory")

    tk.Label(inv_win, text="Search Inventory:").grid(row=0, column=0, sticky='w', padx=5, pady=5)
    entry_inv_search = tk.Entry(inv_win, width=50)
    entry_inv_search.grid(row=1, column=0, columnspan=3, sticky='we', padx=5)
    entry_inv_search.bind("<KeyRelease>", on_inventory_search)

    text_inv = tk.Text(inv_win, width=70, height=20, font=("Courier New", 10))
    text_inv.grid(row=2, column=0, columnspan=3, padx=5, pady=5)
    text_inv.bind("<ButtonRelease-1>", on_select)

    # Edit fields
    tk.Label(inv_win, text="Part Code:").grid(row=3, column=0, sticky='w', padx=5, pady=2)
    entry_code_edit = tk.Entry(inv_win, state='disabled')
    entry_code_edit.grid(row=3, column=1, sticky='w', padx=5, pady=2)

    tk.Label(inv_win, text="Description:").grid(row=4, column=0, sticky='w', padx=5, pady=2)
    entry_desc_edit = tk.Entry(inv_win, width=50)
    entry_desc_edit.grid(row=4, column=1, columnspan=2, sticky='we', padx=5, pady=2)

    tk.Label(inv_win, text="Quantity:").grid(row=5, column=0, sticky='w', padx=5, pady=2)
    entry_qty_edit = tk.Entry(inv_win)
    entry_qty_edit.grid(row=5, column=1, sticky='w', padx=5, pady=2)

    tk.Label(inv_win, text="Unit Price:").grid(row=6, column=0, sticky='w', padx=5, pady=2)
    entry_price_edit = tk.Entry(inv_win)
    entry_price_edit.grid(row=6, column=1, sticky='w', padx=5, pady=2)

    btn_save = tk.Button(inv_win, text="Save Changes", command=save_changes)
    btn_save.grid(row=7, column=1, sticky='w', padx=5, pady=10)

    btn_delete = tk.Button(inv_win, text="Delete Part", command=delete_part)
    btn_delete.grid(row=7, column=2, sticky='e', padx=5, pady=10)

    update_inventory_display()

# GUI setup
window = tk.Tk()
window.title("POS Billing System")

# Search Area
tk.Label(window, text="Search Part (code or description):").grid(row=0, column=0, sticky="w")
entry_search = tk.Entry(window, width=50)
entry_search.grid(row=1, column=0, padx=5)
entry_search.bind("<KeyRelease>", search_parts)
entry_search.bind("<Down>", on_down_key)

listbox_suggestions = tk.Listbox(window, width=50, height=5)
listbox_suggestions.bind("<Double-Button-1>", fill_from_selection)
listbox_suggestions.bind("<Return>", fill_from_selection)
listbox_suggestions.bind("<Down>", on_listbox_down)
listbox_suggestions.bind("<Up>", on_listbox_up)
listbox_suggestions.place_forget()

# Quantity Input
tk.Label(window, text="Quantity:").grid(row=2, column=0, sticky="w", padx=5)
entry_qty = tk.Entry(window, width=10)
entry_qty.grid(row=3, column=0, sticky="w", padx=5)
entry_qty.bind("<Return>", lambda event: add_to_bill())

# Buttons
frame_buttons = tk.Frame(window)
frame_buttons.grid(row=4, column=0, pady=5, sticky="we", padx=5)

btn_add = tk.Button(frame_buttons, text="Add to Bill", command=add_to_bill)
btn_add.pack(side="left")

btn_checkout = tk.Button(frame_buttons, text="Checkout", command=checkout)
btn_checkout.pack(side="left", padx=10)

btn_inventory = tk.Button(frame_buttons, text="View Inventory", command=view_inventory)
btn_inventory.pack(side="right")

btn_new_part = tk.Button(frame_buttons, text="Add New Part", command=add_new_part_window)
btn_new_part.pack(side="right", padx=10)

# Bill Display
text_bill = tk.Text(window, width=100, height=15, state='disabled', font=("Courier New", 10))
text_bill.grid(row=5, column=0, padx=5, pady=5)

window.mainloop()
