import tkinter as tk
from tkinter import messagebox, ttk, simpledialog, colorchooser, font
import json
import os

DATA_FILE = "customers.json"
NAMES_FILE = "customer_names.json"
SETTINGS_FILE = "settings.json"


class DeliveryApp:
    def __init__(self, master):
        self.master = master
        master.title("Delivery Record Keeper")

        # Default theme values (may be overwritten by saved settings)
        self.bg_color = "#1e1e1e"
        self.text_color = "white"
        self.font_family = "Segoe UI"
        self.font_size = 10

        # Load settings if present
        self.load_settings()

        master.configure(bg=self.bg_color)

        # Records and products
        self.records = []
        self.current_products = {}
        self.known_customers = []  # from NAMES_FILE
        self.available_products = [
            "Rice Bag", "Sugar Bag", "Flour Bag",
            "Kg Flour", "Kg Sugar", "Kg Rice", "Gas Cylinder"
        ]
        self.kg_products = {"Kg Flour", "Kg Sugar", "Kg Rice"}
        self.prices = {
            "Rice Bag": 250,
            "Sugar Bag": 251,
            "Flour Bag": 200,
            "Kg Flour": 10,
            "Kg Sugar": 12,
            "Kg Rice": 12,
            "Gas Cylinder": 300
        }
        self.totals = {p: 0 for p in self.available_products}

        # Styles
        self.style = ttk.Style()
        # use default theme to allow styling
        try:
            self.style.theme_use("default")
        except Exception:
            pass
        self.configure_styles()

        # Build GUI
        self.build_form()
        self.make_resizable()

        # Load existing data
        self.load_customers()
        self.load_known_customers()

    # -------------------------
    # Styling & Theme functions
    # -------------------------
    def configure_styles(self):
        font_style = (self.font_family, self.font_size)
        # ttk styles
        self.style.configure("Dark.TLabel",
                             background=self.bg_color,
                             foreground=self.text_color,
                             font=font_style)
        self.style.configure("Dark.TEntry",
                             fieldbackground="#2b2b2b",
                             foreground=self.text_color,
                             insertcolor=self.text_color,
                             borderwidth=2,
                             font=font_style)
        self.style.configure("Dark.TButton",
                             background="#3a3a3a",
                             foreground=self.text_color,
                             font=font_style,
                             relief="flat")
        self.style.map("Dark.TButton",
                       background=[("active", "#505050"), ("pressed", "#606060")])
        self.style.configure("Dark.TCheckbutton",
                             background=self.bg_color,
                             foreground=self.text_color,
                             font=font_style)
        self.style.configure("Dark.TMenubutton",
                             background="#2b2b2b",
                             foreground=self.text_color,
                             font=font_style)

    def apply_theme(self):
        # reconfigure style and attempt to apply colors to non-ttk widgets safely
        self.master.configure(bg=self.bg_color)
        self.configure_styles()
        for widget in self.master.winfo_children():
            try:
                # if widget is a ttk widget and has 'style' option, reapply it
                if isinstance(widget, ttk.Widget):
                    # preserve existing style if set
                    style = widget.cget("style") if "style" in widget.keys() else ""
                    if style:
                        widget.configure(style=style)
                else:
                    # fallback for non-ttk widgets: try configuring bg/fg where supported
                    try:
                        widget.configure(bg=self.bg_color)
                    except Exception:
                        pass
                    try:
                        widget.configure(fg=self.text_color)
                    except Exception:
                        pass
            except Exception:
                # be silent for widgets that don't support queried options
                pass

    # -------------------------
    # GUI layout
    # -------------------------
    def build_form(self):
        ttk.Label(self.master, text="Customer Name:", style="Dark.TLabel").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.name_entry = ttk.Entry(self.master, style="Dark.TEntry")
        self.name_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=5)

        self.select_customer_btn = ttk.Button(self.master, text="Select Existing Customer",
                                              style="Dark.TButton", command=self.select_existing_customer)
        self.select_customer_btn.grid(row=0, column=2, sticky="ew", padx=5, pady=5)

        ttk.Label(self.master, text="Origin (/H or /M):", style="Dark.TLabel").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.origin_var = tk.StringVar(value="/H")
        self.origin_menu = ttk.OptionMenu(self.master, self.origin_var, "/H", "/H", "/M")
        self.origin_menu.configure(style="Dark.TMenubutton")
        self.origin_menu.grid(row=1, column=1, sticky="ew", padx=5, pady=5)

        ttk.Label(self.master, text="Product:", style="Dark.TLabel").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.product_var = tk.StringVar(value=self.available_products[0])
        self.product_menu = ttk.OptionMenu(self.master, self.product_var, self.available_products[0], *self.available_products)
        self.product_menu.configure(style="Dark.TMenubutton")
        self.product_menu.grid(row=2, column=1, sticky="ew", padx=5, pady=5)

        ttk.Label(self.master, text="Amount:", style="Dark.TLabel").grid(row=3, column=0, sticky="w", padx=5, pady=5)
        self.amount_entry = ttk.Entry(self.master, style="Dark.TEntry")
        self.amount_entry.insert(0, "1")
        self.amount_entry.grid(row=3, column=1, sticky="ew", padx=5, pady=5)

        self.add_button = ttk.Button(self.master, text="Add Product", style="Dark.TButton", command=self.add_product)
        self.add_button.grid(row=4, column=1, sticky="ew", padx=5, pady=5)

        self.products_display = tk.Text(self.master,
                                        height=6, width=40,
                                        bg="#2b2b2b", fg=self.text_color,
                                        insertbackground=self.text_color,
                                        selectbackground="#0366d6",
                                        selectforeground="white",
                                        bd=1, relief="solid")
        self.products_display.grid(row=5, column=0, columnspan=3, sticky="nsew", padx=5, pady=5)

        self.remove_product_button = ttk.Button(self.master, text="Remove Selected Product", style="Dark.TButton",
                                                command=self.remove_selected_product)
        self.remove_product_button.grid(row=6, column=1, sticky="ew", padx=5, pady=5)

        self.paid_var = tk.BooleanVar(value=True)
        self.paid_check = ttk.Checkbutton(self.master, text="Paid", variable=self.paid_var,
                                          style="Dark.TCheckbutton", command=self.update_paid_checkbox_text)
        self.paid_check.grid(row=7, column=0, sticky="w", padx=5, pady=5)

        ttk.Label(self.master, text="Note:", style="Dark.TLabel").grid(row=8, column=0, sticky="w", padx=5, pady=5)
        self.note_entry = ttk.Entry(self.master, style="Dark.TEntry")
        self.note_entry.grid(row=8, column=1, sticky="ew", padx=5, pady=5)

        self.save_button = ttk.Button(self.master, text="Save Customer", style="Dark.TButton", command=self.save_customer)
        self.save_button.grid(row=9, column=0, sticky="ew", padx=5, pady=10)

        self.finish_button = ttk.Button(self.master, text="Finish and Show Summary", style="Dark.TButton", command=self.finish)
        self.finish_button.grid(row=9, column=1, sticky="ew", padx=5, pady=10)

        self.remove_customer_button = ttk.Button(self.master, text="Remove Last Customer", style="Dark.TButton",
                                                 command=self.remove_last_customer)
        self.remove_customer_button.grid(row=10, column=0, columnspan=2, sticky="ew", padx=5, pady=5)

        self.settings_button = ttk.Button(self.master, text="Settings", style="Dark.TButton",
                                          command=self.open_settings)
        self.settings_button.grid(row=11, column=0, columnspan=3, sticky="ew", padx=5, pady=5)

        self.update_paid_checkbox_text()

    def make_resizable(self):
        for c in range(3):
            self.master.columnconfigure(c, weight=1)
        for r in range(0, 12):
            self.master.rowconfigure(r, weight=0)
        self.master.rowconfigure(5, weight=2)

    # -------------------------
    # Product handling
    # -------------------------
    def update_paid_checkbox_text(self):
        self.paid_check.config(text="Paid" if self.paid_var.get() else "Unpaid")

    def add_product(self):
        product = self.product_var.get()
        # allow amounts like "1", "2" — rounding for decimals requirement from earlier convo is omitted per latest request
        try:
            amount = int(float(self.amount_entry.get()))
            if amount <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid positive number for amount.")
            return
        self.current_products[product] = self.current_products.get(product, 0) + amount
        self.totals[product] += amount
        self.update_product_display()

    def remove_selected_product(self):
        if not self.current_products:
            messagebox.showwarning("No Products", "There are no products to remove.")
            return
        prod_list = list(self.current_products.keys())
        prod_str = "\n".join(prod_list)
        selected = simpledialog.askstring("Remove Product", f"Which product to remove?\nAvailable:\n{prod_str}")
        if not selected:
            return
        selected = selected.strip().lower()
        match = next((p for p in prod_list if p.lower() == selected), None)
        if not match:
            messagebox.showerror("Not Found", f"Product '{selected}' not in the current list.")
            return
        amt = simpledialog.askinteger("Amount to Remove",
                                      f"How many {match} to remove? (current: {self.current_products[match]})",
                                      minvalue=1, maxvalue=self.current_products[match])
        if not amt:
            return
        self.current_products[match] -= amt
        self.totals[match] -= amt
        if self.current_products[match] == 0:
            del self.current_products[match]
        self.update_product_display()

    def update_product_display(self):
        self.products_display.configure(state="normal")
        self.products_display.delete("1.0", tk.END)
        for p, a in sorted(self.current_products.items()):
            self.products_display.insert(tk.END, f"{p}: {a}\n")
        self.products_display.configure(state="disabled")

    # -------------------------
    # Save / Load customers & names
    # -------------------------
    def save_customer(self):
        name = self.name_entry.get().strip()
        if not name:
            messagebox.showwarning("Missing Name", "Please enter a name.")
            return
        if not self.current_products:
            messagebox.showwarning("No Products", "Please add at least one product before saving.")
            return
        only_kg_items = all(p in self.kg_products for p in self.current_products)
        if only_kg_items:
            total_kg = sum(self.current_products[p] for p in self.current_products if p in self.kg_products)
            if total_kg < 25:
                messagebox.showerror("Minimum Requirement", "Customers buying only KG items must order at least 25kg in total.")
                return

        record = {
            "name": name,
            "origin": self.origin_var.get(),
            "products": self.current_products.copy(),
            "paid": self.paid_var.get(),
            "note": self.note_entry.get().strip()
        }
        self.records.append(record)
        self.save_to_file()

        # Save customer name + origin separately if new
        if not any(c["name"].lower() == name.lower() and c["origin"] == self.origin_var.get() for c in self.known_customers):
            self.known_customers.append({"name": name, "origin": self.origin_var.get()})
            self.save_known_customers()

        # Reset form
        self.current_products.clear()
        self.update_product_display()
        self.name_entry.delete(0, tk.END)
        self.note_entry.delete(0, tk.END)
        self.amount_entry.delete(0, tk.END)
        self.amount_entry.insert(0, "1")
        self.paid_var.set(True)
        self.update_paid_checkbox_text()
        self.name_entry.focus_set()
        messagebox.showinfo("Saved", "Customer record saved.")

    def remove_last_customer(self):
        if not self.records:
            messagebox.showwarning("No Customers", "No customer records to remove.")
            return
        last = self.records[-1]
        confirm = messagebox.askyesno("Confirm Remove", f"Remove last saved customer: {last['name']}?")
        if confirm:
            for p, a in last['products'].items():
                if p in self.totals:
                    self.totals[p] -= a
            self.records.pop()
            self.save_to_file()
            messagebox.showinfo("Removed", f"Customer '{last['name']}' removed.")

    def save_to_file(self):
        try:
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(self.records, f, indent=2)
        except Exception as e:
            messagebox.showerror("Save Error", f"Failed to save customers: {e}")

    def load_customers(self):
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, "r", encoding="utf-8") as f:
                    self.records = json.load(f) or []
                    # rebuild totals
                    self.totals = {p: 0 for p in self.available_products}
                    for record in self.records:
                        for p, a in record.get('products', {}).items():
                            if p in self.totals:
                                self.totals[p] += a
            except Exception:
                self.records = []

    def save_known_customers(self):
        try:
            with open(NAMES_FILE, "w", encoding="utf-8") as f:
                json.dump(self.known_customers, f, indent=2)
        except Exception as e:
            messagebox.showerror("Save Error", f"Failed to save known customers: {e}")

    def load_known_customers(self):
        if os.path.exists(NAMES_FILE):
            try:
                with open(NAMES_FILE, "r", encoding="utf-8") as f:
                    self.known_customers = json.load(f) or []
            except Exception:
                self.known_customers = []

    # -------------------------
    # Summary building & overlay
    # -------------------------
    def finish(self):
        if not self.records:
            messagebox.showinfo("No Records", "No customer records to display.")
            return
        summary = self.build_summary()
        self.show_summary_window(summary)

    def build_summary(self):
        result = "Today's Delivery\n\n"

        for record in self.records:
            line = f"{record['name']} {record['origin']}"
            if not record["paid"]:
                total_due = sum(
                    (285 if p == "Gas Cylinder" and "triple bakers" in record["name"].lower() else self.prices.get(p, 0)) * a
                    for p, a in record["products"].items()
                )
                line += f" [Pending Payment] [{total_due} MVR]"
            if record["note"]:
                line += f" [Note: {record['note']}]"
            result += line + "\n"

            for p, a in record["products"].items():
                if p in self.kg_products:
                    # kg-style: e.g., "22kg Kg Flour" -> better to show "22kg Flour"
                    # we'll output e.g. "22kg Flour"
                    # so strip "Kg " prefix for nicer output
                    nice = p.replace("Kg ", "")
                    result += f"{a}kg {nice}\n"
                else:
                    result += f"{a} {p}\n"
            result += "\n"

        result += "Total\n"
        for p, a in self.totals.items():
            if a > 0:
                if p in self.kg_products:
                    nice = p.replace("Kg ", "")
                    result += f"{a}kg {nice}\n"
                else:
                    result += f"{a} {p}\n"
        return result

    def show_summary_window(self, summary_text):
        summary_win = tk.Toplevel(self.master)
        summary_win.title("Delivery Summary")
        summary_win.configure(bg=self.bg_color)
        summary_win.rowconfigure(0, weight=1)
        summary_win.columnconfigure(0, weight=1)

        # Text + scrollbar
        frame = ttk.Frame(summary_win)
        frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        frame.rowconfigure(0, weight=1)
        frame.columnconfigure(0, weight=1)

        text_box = tk.Text(frame,
                           wrap="word",
                           bg="#2b2b2b", fg=self.text_color,
                           insertbackground=self.text_color,
                           selectbackground="#0366d6", selectforeground="white",
                           bd=1, relief="solid")
        text_box.grid(row=0, column=0, sticky="nsew")
        text_box.insert(tk.END, summary_text)
        text_box.configure(state="disabled")

        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=text_box.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        text_box.configure(yscrollcommand=scrollbar.set)

        # Buttons (copy + clear)
        btn_frame = ttk.Frame(summary_win)
        btn_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=5)
        btn_frame.columnconfigure(0, weight=1)
        btn_frame.columnconfigure(1, weight=1)

        def copy_to_clipboard():
            self.master.clipboard_clear()
            self.master.clipboard_append(summary_text)
            self.master.update()
            messagebox.showinfo("Copied", "Summary copied to clipboard.")

        def clear_records():
            if messagebox.askyesno("Confirm Clear", "Clear all delivery records?"):
                self.records.clear()
                self.totals = {p: 0 for p in self.available_products}
                self.save_to_file()
                summary_win.destroy()
                messagebox.showinfo("Cleared", "All delivery records cleared.")

        copy_btn = ttk.Button(btn_frame, text="Copy to Clipboard", style="Dark.TButton", command=copy_to_clipboard)
        copy_btn.grid(row=0, column=0, sticky="ew", padx=5)

        clear_btn = ttk.Button(btn_frame, text="Clear Delivery List", style="Dark.TButton", command=clear_records)
        clear_btn.grid(row=0, column=1, sticky="ew", padx=5)

    # -------------------------
    # Select existing customer popup
    # -------------------------
    def select_existing_customer(self):
        if not self.known_customers:
            messagebox.showinfo("No Customers", "No saved customers available yet.")
            return

        popup = tk.Toplevel(self.master)
        popup.title("Select Customer")
        popup.configure(bg=self.bg_color)
        popup.geometry("400x200")
        popup.rowconfigure(2, weight=1)

        search_var = tk.StringVar()

        ttk.Label(popup, text="Search:", style="Dark.TLabel").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        search_entry = ttk.Entry(popup, textvariable=search_var, style="Dark.TEntry")
        search_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        popup.columnconfigure(1, weight=1)

        # Dropdown (OptionMenu) to show matches
        dropdown_var = tk.StringVar(value="")
        dropdown = ttk.OptionMenu(popup, dropdown_var, "")
        dropdown.configure(style="Dark.TMenubutton")
        dropdown.grid(row=1, column=0, columnspan=2, sticky="ew", padx=5, pady=5)

        def populate(matches=None):
            menu = dropdown["menu"]
            menu.delete(0, "end")
            matches = matches if matches is not None else self.known_customers
            for c in matches:
                label = f"{c['name']} {c['origin']}"
                menu.add_command(label=label, command=lambda cust=c: select_customer(cust))

        def update_dropdown(*_):
            q = search_var.get().strip().lower()
            matches = [c for c in self.known_customers if q in c["name"].lower()]
            populate(matches)

        def select_customer(cust):
            self.name_entry.delete(0, tk.END)
            self.name_entry.insert(0, cust["name"])
            self.origin_var.set(cust["origin"])
            popup.destroy()

        populate()
        search_var.trace_add("write", update_dropdown)

    # -------------------------
    # Settings (with persistence)
    # -------------------------
    def open_settings(self):
        settings_win = tk.Toplevel(self.master)
        settings_win.title("Settings")
        settings_win.configure(bg=self.bg_color)
        settings_win.geometry("420x220")

        def change_bg():
            color = colorchooser.askcolor(title="Choose Background Color", initialcolor=self.bg_color)[1]
            if color:
                self.bg_color = color
                self.apply_theme()
                self.save_settings()

        def change_text_color():
            color = colorchooser.askcolor(title="Choose Text Color", initialcolor=self.text_color)[1]
            if color:
                self.text_color = color
                self.apply_theme()
                self.save_settings()

        # Font selection via dropdown for safety (list top fonts)
        fonts_list = sorted(list(font.families()))
        top_fonts = fonts_list[:80]  # limit the list shown to avoid long menus

        ttk.Label(settings_win, text="Font Family:", style="Dark.TLabel").pack(padx=8, pady=(8, 2), anchor="w")
        font_var = tk.StringVar(value=self.font_family)
        font_dropdown = ttk.OptionMenu(settings_win, font_var, self.font_family, *top_fonts)
        font_dropdown.configure(style="Dark.TMenubutton")
        font_dropdown.pack(fill="x", padx=8, pady=2)

        ttk.Label(settings_win, text="Font Size:", style="Dark.TLabel").pack(padx=8, pady=(8, 2), anchor="w")
        size_var = tk.IntVar(value=self.font_size)
        size_spin = ttk.Spinbox(settings_win, from_=8, to=20, textvariable=size_var)
        size_spin.pack(fill="x", padx=8, pady=2)

        ttk.Button(settings_win, text="Change Background Color", style="Dark.TButton", command=change_bg).pack(padx=8, pady=6, fill="x")
        ttk.Button(settings_win, text="Change Text Color", style="Dark.TButton", command=change_text_color).pack(padx=8, pady=2, fill="x")

        def apply_and_save():
            self.font_family = font_var.get()
            self.font_size = int(size_var.get())
            self.apply_theme()
            self.save_settings()
            settings_win.destroy()

        ttk.Button(settings_win, text="Apply", style="Dark.TButton", command=apply_and_save).pack(padx=8, pady=8, fill="x")

    def save_settings(self):
        settings = {
            "bg_color": self.bg_color,
            "text_color": self.text_color,
            "font_family": self.font_family,
            "font_size": self.font_size
        }
        try:
            with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
                json.dump(settings, f, indent=2)
        except Exception as e:
            messagebox.showerror("Save Error", f"Failed to save settings: {e}")

    def load_settings(self):
        if os.path.exists(SETTINGS_FILE):
            try:
                with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                    s = json.load(f) or {}
                    self.bg_color = s.get("bg_color", self.bg_color)
                    self.text_color = s.get("text_color", self.text_color)
                    self.font_family = s.get("font_family", self.font_family)
                    self.font_size = s.get("font_size", self.font_size)
            except Exception:
                pass


if __name__ == "__main__":
    root = tk.Tk()
    app = DeliveryApp(root)
    root.mainloop()
