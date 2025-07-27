import os
import datetime
import hashlib
import tkinter.messagebox
from tkinter import filedialog
import json
import tkinter as tk  # Import tkinter for Entry widget

# Monkey-patch ReportLab to use hashlib.md5 without 'usedforsecurity'
import reportlab
import reportlab.lib.utils as rl_utils
import reportlab.pdfbase.pdfdoc as pdfdoc
from reportlab.lib.utils import ImageReader


# Define a safe md5 wrapper that ignores 'usedforsecurity'
def safe_md5(data=b"", **kwargs):
    """A wrapper for hashlib.md5 that ignores extra keyword arguments."""
    return hashlib.md5(data)


# Override md5 functions in ReportLab with our safe wrapper
rl_utils.openssl_md5 = safe_md5
rl_utils.md5 = safe_md5
pdfdoc.md5 = safe_md5

from num2words import num2words
import customtkinter as ctk
from tkinter import ttk
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas


class InvoiceGeneratorApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Invoice Generator")
        self.geometry("900x750")  # Increased height to accommodate new fields

        # --- Settings file path for persistence ---
        self.settings_file = "invoice_app_settings.json"
        self.company_details_file_path = None
        self.logo_file_path = None
        self.last_invoice_serial = 0  # This will be loaded from company details file

        # StringVars to hold company details loaded from file (no direct input widgets)
        self.company_name_var = ctk.StringVar(value="Your Company Name")
        self.company_address_var = ctk.StringVar(value="123 Main Street, City, Country")
        self.company_gstn_var = ctk.StringVar(value="22AAAAA0000A1Z5")
        self.company_phone_var = ctk.StringVar(value="")  # Initialize as empty string

        # === Tabview for Company and Client Details ===
        self.tabview = ctk.CTkTabview(self, width=800, height=200)  # Set a fixed height for the tabview
        self.tabview.pack(padx=10, pady=10, fill="x")

        # --- Reordered Tabs: Client Details first, then My Company Details ---
        self.client_tab = self.tabview.add("Client Details")
        self.my_company_tab = self.tabview.add("My Company Details")

        # === Client Details Tab ===
        ctk.CTkLabel(self.client_tab, text="Client Name:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.client_name_var = ctk.StringVar()
        ctk.CTkEntry(self.client_tab, textvariable=self.client_name_var).grid(row=0, column=1, padx=5, pady=5,
                                                                              sticky="ew")
        ctk.CTkLabel(self.client_tab, text="Client Address:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.client_address_var = ctk.StringVar()
        ctk.CTkEntry(self.client_tab, textvariable=self.client_address_var).grid(row=1, column=1, padx=5, pady=5,
                                                                                 sticky="ew")
        ctk.CTkLabel(self.client_tab, text="Client GSTN No:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.client_gstn_var = ctk.StringVar()
        ctk.CTkEntry(self.client_tab, textvariable=self.client_gstn_var).grid(row=2, column=1, padx=5, pady=5,
                                                                              sticky="ew")
        self.client_tab.grid_columnconfigure(1, weight=1)  # Make the entry fields expand

        # === My Company Details Tab (only button to load files) ===
        ctk.CTkLabel(self.my_company_tab, text="Company details loaded from file.").grid(row=0, column=0, columnspan=2,
                                                                                         pady=10)
        ctk.CTkButton(self.my_company_tab, text="Load Company Settings & Logo",
                      command=self.load_company_settings_and_logo).grid(row=1, column=0, columnspan=2, pady=10)
        self.my_company_tab.grid_columnconfigure(0, weight=1)
        self.my_company_tab.grid_columnconfigure(1, weight=1)

        # === Items frame ===
        items_frame = ctk.CTkFrame(self, corner_radius=10)
        items_frame.pack(padx=10, pady=10, fill="both", expand=True)

        # Use a custom style for the Treeview to better integrate with CTk
        style = ttk.Style()
        style.theme_use("default")

        current_appearance_mode = ctk.get_appearance_mode()

        fg_color_tuple = ctk.ThemeManager.theme["CTkFrame"]["fg_color"]
        text_color_tuple = ctk.ThemeManager.theme["CTkLabel"]["text_color"]
        border_color_tuple = ctk.ThemeManager.theme["CTkFrame"]["border_color"]
        button_fg_color_tuple = ctk.ThemeManager.theme["CTkButton"]["fg_color"]
        button_text_color_tuple = ctk.ThemeManager.theme["CTkButton"]["text_color"]

        if current_appearance_mode == "Light":
            bg_color = fg_color_tuple[0]
            fg_color = text_color_tuple[0]
            field_bg_color = fg_color_tuple[0]
            border_color = border_color_tuple[0]
            selected_bg_color = button_fg_color_tuple[0]
            heading_bg_color = button_fg_color_tuple[0]
            heading_fg_color = button_text_color_tuple[0]
        else:
            bg_color = fg_color_tuple[1]
            fg_color = text_color_tuple[1]
            field_bg_color = fg_color_tuple[1]
            border_color = border_color_tuple[1]
            selected_bg_color = button_fg_color_tuple[1]
            heading_bg_color = button_fg_color_tuple[1]
            heading_fg_color = button_text_color_tuple[1]

        style.configure("Treeview",
                        background=bg_color,
                        foreground=fg_color,
                        fieldbackground=field_bg_color,
                        bordercolor=border_color,
                        borderwidth=1,
                        relief="solid")
        style.map("Treeview", background=[('selected', selected_bg_color)])
        style.configure("Treeview.Heading",
                        background=heading_bg_color,
                        foreground=heading_fg_color,
                        font=('Helvetica', 10, 'bold'))

        self.tree = ttk.Treeview(items_frame, columns=("sl", "item", "qty", "rate", "total"), show="headings",
                                 style="Treeview")
        self.tree.column("sl", width=50, anchor="center")
        self.tree.column("item", width=250, anchor="w")
        self.tree.column("qty", width=80, anchor="center")
        self.tree.column("rate", width=100, anchor="e")
        self.tree.column("total", width=120, anchor="e")

        for col in ("sl", "item", "qty", "rate", "total"):
            self.tree.heading(col, text=col.title())
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar = ttk.Scrollbar(items_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        # Bind event for editing
        self.tree.bind("<Button-1>", self.on_tree_click)
        self.tree.bind("<Double-1>", self.on_tree_double_click)  # Double click to edit

        # Entry row for new item
        entry_frame = ctk.CTkFrame(self, corner_radius=10)
        entry_frame.pack(padx=10, pady=5, fill="x")
        self.sl_var = ctk.StringVar()
        self.item_var = ctk.StringVar()
        self.qty_var = ctk.StringVar()
        self.rate_var = ctk.StringVar()

        for i in range(9):
            entry_frame.grid_columnconfigure(i, weight=1)

        ctk.CTkLabel(entry_frame, text="SL No").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        ctk.CTkEntry(entry_frame, textvariable=self.sl_var, width=80).grid(row=0, column=1, padx=5, pady=5, sticky="w")

        ctk.CTkLabel(entry_frame, text="Item Name").grid(row=0, column=2, padx=5, pady=5, sticky="e")
        ctk.CTkEntry(entry_frame, textvariable=self.item_var, width=150).grid(row=0, column=3, padx=5, pady=5,
                                                                              sticky="w")

        ctk.CTkLabel(entry_frame, text="Qty").grid(row=0, column=4, padx=5, pady=5, sticky="e")
        ctk.CTkEntry(entry_frame, textvariable=self.qty_var, width=80).grid(row=0, column=5, padx=5, pady=5, sticky="w")

        ctk.CTkLabel(entry_frame, text="Rate").grid(row=0, column=6, padx=5, pady=5, sticky="e")
        ctk.CTkEntry(entry_frame, textvariable=self.rate_var, width=80).grid(row=0, column=7, padx=5, pady=5,
                                                                             sticky="w")

        ctk.CTkButton(entry_frame, text="Add Item", command=self.add_item).grid(row=0, column=8, padx=5, sticky="e")

        # Action buttons
        action_frame = ctk.CTkFrame(self, corner_radius=10)
        action_frame.pack(padx=10, pady=10)
        ctk.CTkButton(action_frame, text="Generate PDF", command=self.generate_pdf).grid(row=0, column=0, padx=10)
        ctk.CTkButton(action_frame, text="Print Invoice", command=self.print_invoice).grid(row=0, column=1, padx=10)
        # New: Delete Item Button
        ctk.CTkButton(action_frame, text="Delete Selected Item", command=self.delete_selected_item).grid(row=0,
                                                                                                         column=2,
                                                                                                         padx=10)

        self.load_settings()

    def load_settings(self):
        """Loads company details file path, logo file path, and last invoice serial from settings.json."""
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, 'r') as f:
                    settings = json.load(f)
                    self.company_details_file_path = settings.get("company_details_file")
                    self.logo_file_path = settings.get("logo_file")

                if self.company_details_file_path and os.path.exists(self.company_details_file_path):
                    self.load_company_details_from_file()
                else:
                    self.company_details_file_path = None
                    tkinter.messagebox.showwarning("Company Details",
                                                   "Company details file not found. Please load it via 'Load Company Settings & Logo' button.")

                if self.logo_file_path and os.path.exists(self.logo_file_path):
                    pass
                else:
                    self.logo_file_path = None
                    tkinter.messagebox.showwarning("Company Logo",
                                                   "Company logo file not found. Please load it via 'Load Company Settings & Logo' button.")

            except json.JSONDecodeError:
                tkinter.messagebox.showerror("Settings Error", "Could not read settings file. It might be corrupted.")
            except Exception as e:
                tkinter.messagebox.showerror("Settings Error", f"An error occurred loading settings: {e}")
        else:
            tkinter.messagebox.showinfo("First Run",
                                        "No settings file found. Please use 'Load Company Settings & Logo' to set up your company details and logo.")

    def save_settings(self):
        """Saves company details file path and logo file path to settings.json."""
        settings = {
            "company_details_file": self.company_details_file_path,
            "logo_file": self.logo_file_path,
        }
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(settings, f, indent=4)
        except Exception as e:
            tkinter.messagebox.showerror("Settings Error", f"Could not save settings: {e}")

    def load_company_settings_and_logo(self):
        """Opens file dialogs to select company details text file and logo image."""
        file_path = filedialog.askopenfilename(
            title="Select Company Details Text File",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if file_path:
            self.company_details_file_path = file_path
            self.load_company_details_from_file()
        else:
            self.company_details_file_path = None
            tkinter.messagebox.showinfo("Selection Cancelled", "Company details file selection cancelled.")

        logo_path = filedialog.askopenfilename(
            title="Select Company Logo Image",
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.gif"), ("All files", "*.*")]
        )
        if logo_path:
            self.logo_file_path = logo_path
            tkinter.messagebox.showinfo("Logo Selected", f"Logo file selected: {os.path.basename(logo_path)}")
        else:
            self.logo_file_path = None
            tkinter.messagebox.showinfo("Selection Cancelled", "Logo file selection cancelled.")

        self.save_settings()

    def load_company_details_from_file(self):
        """Loads company name, address, GSTN, phone, and last invoice serial from the selected text file."""
        if not self.company_details_file_path or not os.path.exists(self.company_details_file_path):
            tkinter.messagebox.showwarning("File Not Found", "Company details file not found.")
            return

        try:
            with open(self.company_details_file_path, 'r') as f:
                lines = f.readlines()
                company_data = {}
                for line in lines:
                    if ":" in line:
                        key, value = line.split(":", 1)
                        company_data[key.strip()] = value.strip()

                self.company_name_var.set(company_data.get("Company Name", "N/A"))
                self.company_address_var.set(company_data.get("Company Address", "N/A"))
                self.company_gstn_var.set(company_data.get("Company GSTN", "N/A"))
                self.company_phone_var.set(company_data.get("Company Phone", "").strip())

                try:
                    self.last_invoice_serial = int(company_data.get("Last Invoice Serial", 0))
                except ValueError:
                    self.last_invoice_serial = 0
                    tkinter.messagebox.showwarning("Serial Number Error",
                                                   "Last Invoice Serial in file is invalid. Resetting to 0.")

            tkinter.messagebox.showinfo("Company Details Loaded",
                                        "Company details and last invoice serial loaded successfully.")
        except Exception as e:
            tkinter.messagebox.showerror("File Read Error", f"Error reading company details file: {e}")

    def update_company_details_file_with_serial(self, new_serial):
        """Updates the 'Last Invoice Serial' in the company details text file."""
        if not self.company_details_file_path or not os.path.exists(self.company_details_file_path):
            tkinter.messagebox.showerror("File Error",
                                         "Company details file path not set or file does not exist. Cannot update serial.")
            return

        try:
            with open(self.company_details_file_path, 'r') as f:
                lines = f.readlines()

            found_serial_line = False
            updated_lines = []
            for line in lines:
                if line.strip().startswith("Last Invoice Serial:"):
                    updated_lines.append(f"Last Invoice Serial: {new_serial}\n")
                    found_serial_line = True
                else:
                    updated_lines.append(line)

            if not found_serial_line:
                updated_lines.append(f"Last Invoice Serial: {new_serial}\n")

            with open(self.company_details_file_path, 'w') as f:
                f.writelines(updated_lines)

        except Exception as e:
            tkinter.messagebox.showerror("File Write Error",
                                         f"Error updating last invoice serial in company details file: {e}")

    def add_item(self):
        try:
            sl = self.sl_var.get()
            item = self.item_var.get()
            qty = int(self.qty_var.get())  # Changed to int
            rate = float(self.rate_var.get())
            total = qty * rate
            self.tree.insert('', 'end', values=(sl, item, qty, rate, f"{total:.2f}"))
            self.sl_var.set("")
            self.item_var.set("")
            self.qty_var.set("")
            self.rate_var.set("")
        except ValueError:
            tkinter.messagebox.showerror("Invalid input",
                                         "Please enter numeric values for Qty and Rate (Qty must be whole number).")
        except Exception as e:
            tkinter.messagebox.showerror("Error", f"An unexpected error occurred: {e}")

    def on_tree_click(self, event):
        """Handles single click on Treeview to identify cell."""
        pass

    def on_tree_double_click(self, event):
        """Handles double click on Treeview to initiate editing."""
        region = self.tree.identify_region(event.x, event.y)
        if region == "cell":
            column_id = self.tree.identify_column(event.x)
            row_id = self.tree.identify_row(event.y)
            self.edit_cell(row_id, column_id)

    def edit_cell(self, row_id, column_id):
        """Creates an entry widget for editing a Treeview cell."""
        # Only allow editing for 'sl', 'item', 'qty', 'rate'
        if column_id not in ("#1", "#2", "#3", "#4"):  # SL, Item, Qty, Rate
            return

        column_name = self.tree.heading(column_id)["text"].lower()
        if column_name == "sl":
            col_index = 0
        elif column_name == "item":
            col_index = 1
        elif column_name == "qty":
            col_index = 2
        elif column_name == "rate":
            col_index = 3
        else:
            return

        current_value = self.tree.item(row_id, 'values')[col_index]

        bbox = self.tree.bbox(row_id, column_id)
        if not bbox:
            return

        x, y, width, height = bbox

        edit_entry = tk.Entry(self.tree, width=width)
        edit_entry.insert(0, current_value)
        edit_entry.place(x=x, y=y, width=width, height=height)
        edit_entry.focus_set()
        edit_entry.select_range(0, tk.END)

        edit_entry.bind("<Return>", lambda e: self.on_edit_finish(edit_entry, row_id, column_id, col_index))
        edit_entry.bind("<FocusOut>", lambda e: self.on_edit_finish(edit_entry, row_id, column_id, col_index))

    def on_edit_finish(self, entry_widget, row_id, column_id, col_index):
        """Processes the edited value and updates the Treeview."""
        new_value = entry_widget.get()
        entry_widget.destroy()

        current_values = list(self.tree.item(row_id, 'values'))

        column_name = self.tree.heading(column_id)["text"].lower()

        if column_name == "qty":
            try:
                new_numeric_value = int(new_value)  # Changed to int
                current_values[col_index] = str(new_numeric_value)  # Store as string without decimals

                qty = int(current_values[2])  # Use int for qty
                rate = float(current_values[3])
                current_values[4] = f"{(qty * rate):.2f}"

                self.tree.item(row_id, values=current_values)
            except ValueError:
                tkinter.messagebox.showerror("Invalid Input", f"Please enter a valid whole number for Quantity.")
                self.tree.item(row_id, values=current_values)
        elif column_name == "rate":
            try:
                new_numeric_value = float(new_value)
                current_values[col_index] = f"{new_numeric_value:.2f}"

                qty = int(current_values[2])  # Use int for qty
                rate = float(current_values[3])
                current_values[4] = f"{(qty * rate):.2f}"

                self.tree.item(row_id, values=current_values)
            except ValueError:
                tkinter.messagebox.showerror("Invalid Input", f"Please enter a valid number for Rate.")
                self.tree.item(row_id, values=current_values)
        else:  # For 'sl' and 'item'
            current_values[col_index] = new_value
            self.tree.item(row_id, values=current_values)

    def delete_selected_item(self):
        """Deletes the selected item(s) from the Treeview and re-indexes SL numbers."""
        selected_items = self.tree.selection()
        if not selected_items:
            tkinter.messagebox.showwarning("No Selection", "Please select an item to delete.")
            return

        if tkinter.messagebox.askyesno("Confirm Delete", "Are you sure you want to delete the selected item(s)?"):
            for item in selected_items:
                self.tree.delete(item)

            # Re-index SL numbers after deletion
            all_items = self.tree.get_children()
            for i, item_id in enumerate(all_items):
                current_values = list(self.tree.item(item_id, 'values'))
                current_values[0] = str(i + 1)  # Update SL No.
                self.tree.item(item_id, values=current_values)

            tkinter.messagebox.showinfo("Deleted", "Selected item(s) deleted successfully and SL numbers re-indexed.")

    def generate_pdf(self):
        client_name = self.client_name_var.get().strip()
        if not client_name:
            tkinter.messagebox.showwarning("Missing Client Name",
                                           "Please enter the client's name before generating the PDF.")
            return

        if self.company_name_var.get() == "Your Company Name" and \
                self.company_address_var.get() == "123 Main Street, City, Country" and \
                self.company_gstn_var.get() == "22AAAAA0000A1Z5":
            tkinter.messagebox.showwarning("Company Details Missing",
                                           "Please load your company details and logo using the 'Load Company Settings & Logo' button before generating the PDF.")
            return

        company_name = self.company_name_var.get()
        company_address = self.company_address_var.get()
        company_gstn = self.company_gstn_var.get()
        company_phone = self.company_phone_var.get()

        default_filename = f"Invoice_{client_name.replace(' ', '_')}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"

        filename = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            initialfile=default_filename,
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )

        if not filename:
            return

        c = canvas.Canvas(filename, pagesize=A4)
        width, height = A4
        margin = 40

        # --- Invoice Details (Date, Invoice No.) - Top Right ---
        invoice_date = datetime.date.today().strftime("%d-%m-%Y")
        self.last_invoice_serial += 1
        current_year = datetime.date.today().strftime("%Y")
        formatted_serial = f"{self.last_invoice_serial:04d}"
        invoice_no = f"ELE{current_year}{formatted_serial}"

        c.setFont("Helvetica-Bold", 10)
        c.drawString(width - margin - c.stringWidth(f"Date: {invoice_date}", "Helvetica-Bold", 10),
                     height - margin - 15, f"Date: {invoice_date}")
        c.drawString(width - margin - c.stringWidth(f"Invoice No: {invoice_no}", "Helvetica-Bold", 10),
                     height - margin - 30, f"Invoice No: {invoice_no}")

        # --- Company Logo (Top-Left) ---
        logo_width = 70
        logo_height = 70
        logo_x = margin
        logo_y_top = height - margin
        logo_y_bottom = logo_y_top - logo_height

        if self.logo_file_path and os.path.exists(self.logo_file_path):
            try:
                c.drawImage(self.logo_file_path, logo_x, logo_y_bottom, width=logo_width, height=logo_height,
                            preserveAspectRatio=True, mask='auto')
                # Start drawing company details below the logo with some padding
                current_y = logo_y_bottom - 15  # 15 units padding below logo
            except Exception as e:
                tkinter.messagebox.showwarning("Logo Error", f"Could not draw logo: {e}. Proceeding without logo.")
                current_y = height - margin  # Fallback if no logo or error
        else:
            current_y = height - margin  # Start from top margin if no logo

        # --- Company Header (Left-aligned, below logo) ---
        company_text_x = margin  # Align with left margin

        c.setFont("Helvetica-Bold", 16)
        c.drawString(company_text_x, current_y, company_name)
        current_y -= 15  # Line spacing for next line (address)
        c.setFont("Helvetica", 10)
        c.drawString(company_text_x, current_y, company_address)
        current_y -= 12  # Line spacing for next line (GSTN)
        c.drawString(company_text_x, current_y, f"GSTN: {company_gstn}")

        if company_phone.strip():
            current_y -= 12  # Line spacing for next line (phone)
            c.drawString(company_text_x, current_y, f"Phone: {company_phone}")

        # --- Gap between Company Details and Client Details ---
        # Increased this value to provide more blank space as requested.
        gap_after_company_details = 30  # Increased from 15 to 30 for more visible gap
        client_details_start_y = current_y - gap_after_company_details

        # --- Client Details (left-aligned) ---
        current_y = client_details_start_y  # Set current_y to start client details
        c.setFont("Helvetica-Bold", 12)
        c.drawString(margin, current_y, "Bill To:")
        c.setFont("Helvetica", 10)
        current_y -= 15
        c.drawString(margin, current_y, self.client_name_var.get())
        current_y -= 12
        c.drawString(margin, current_y, self.client_address_var.get())
        current_y -= 12

        client_gstn_value = self.client_gstn_var.get().strip().upper()
        if client_gstn_value:
            c.drawString(margin, current_y, f"GSTN: {client_gstn_value}")
            current_y -= 12

        # --- Items Table Header ---
        current_y -= 30
        c.setFont("Helvetica-Bold", 10)

        col_widths = [40, 240, 60, 80, 100]
        cols = ["SL", "Item Name", "Qty", "Rate", "Total"]

        col_start_x = []
        current_col_x_calc = margin
        for width_val in col_widths:
            col_start_x.append(current_col_x_calc)
            current_col_x_calc += width_val

        table_right_edge = col_start_x[-1] + col_widths[-1]
        table_width = table_right_edge - margin

        header_height = 20
        c.setFillColorRGB(0.9, 0.9, 0.9)
        c.rect(margin, current_y - 5, table_width, header_height, fill=1)
        c.setFillColorRGB(0, 0, 0)

        text_y_offset = 7

        for i, col in enumerate(cols):
            c.drawCentredString(col_start_x[i] + col_widths[i] / 2, current_y + text_y_offset, col)

        current_y -= 15
        c.line(margin, current_y + 5, table_right_edge, current_y + 5)

        table_content_start_y = current_y + 5

        c.setFont("Helvetica", 10)

        # Table Rows
        subtotal = 0
        item_row_height = 20
        min_y_for_items = margin + 100

        current_y_for_rows = current_y

        for iid in self.tree.get_children():
            sl, item, qty_str, rate_str, total_str = self.tree.item(iid)['values']

            try:
                qty = int(qty_str)  # Ensure qty is int for calculation
                rate = float(rate_str)
                total = float(total_str)
            except ValueError:
                tkinter.messagebox.showerror("Data Error",
                                             f"Invalid numeric data found for item: {item}. Please check quantity, rate, or total.")
                continue

            subtotal += total

            if current_y_for_rows - item_row_height < min_y_for_items:
                c.showPage()
                current_y_for_rows = height - margin
                c.setFont("Helvetica-Bold", 10)
                c.setFillColorRGB(0.9, 0.9, 0.9)
                c.rect(margin, current_y_for_rows - 5, table_width, header_height, fill=1)
                c.setFillColorRGB(0, 0, 0)
                for i_col, col_name in enumerate(cols):
                    c.drawCentredString(col_start_x[i_col] + col_widths[i_col] / 2, current_y_for_rows + text_y_offset,
                                        col_name)
                current_y_for_rows -= 15
                c.line(margin, current_y_for_rows + 5, table_right_edge, current_y_for_rows + 5)
                table_content_start_y = current_y_for_rows + 5
                c.setFont("Helvetica", 10)

            current_y_for_rows -= item_row_height

            c.drawCentredString(col_start_x[0] + col_widths[0] / 2, current_y_for_rows + text_y_offset, str(sl))
            c.drawCentredString(col_start_x[1] + col_widths[1] / 2, current_y_for_rows + text_y_offset, str(item))
            c.drawCentredString(col_start_x[2] + col_widths[2] / 2, current_y_for_rows + text_y_offset,
                                f"{qty}")  # Display Qty as integer
            c.drawCentredString(col_start_x[3] + col_widths[3] / 2, current_y_for_rows + text_y_offset, f"{rate:.2f}")
            c.drawCentredString(col_start_x[4] + col_widths[4] / 2, current_y_for_rows + text_y_offset, f"{total:.2f}")

        final_table_bottom_y = current_y_for_rows
        c.line(margin, final_table_bottom_y, table_right_edge, final_table_bottom_y)

        for i in range(len(col_start_x)):
            x_pos = col_start_x[i]
            c.line(x_pos, table_content_start_y, x_pos, final_table_bottom_y)
        c.line(table_right_edge, table_content_start_y, table_right_edge, final_table_bottom_y)

        # Totals Section (always at the bottom of the last page)
        required_space_for_totals = 100
        if final_table_bottom_y < margin + required_space_for_totals:
            c.showPage()
            current_y = height - margin
        else:
            current_y = final_table_bottom_y

        footer_y_start = margin + 80

        c.setFont("Helvetica-Bold", 12)
        c.drawRightString(width - margin, footer_y_start + 45, "TOTALS")

        c.setFont("Helvetica", 10)

        gst_rate = 0.18
        if client_gstn_value:
            gst_amount = subtotal * gst_rate
        else:
            gst_amount = 0.0

        grand_total = subtotal + gst_amount

        c.drawRightString(width - margin, footer_y_start + 30, f"Sum of Totals: {subtotal:.2f}")

        if client_gstn_value:
            c.drawRightString(width - margin, footer_y_start + 15, f"GST ({gst_rate * 100:.0f}%): {gst_amount:.2f}")
            c.setFont("Helvetica-Bold", 12)
            c.drawRightString(width - margin, footer_y_start, f"Grand Total: {grand_total:.2f}")
        else:
            c.setFont("Helvetica-Bold", 12)
            c.drawRightString(width - margin, footer_y_start + 15, f"Grand Total: {grand_total:.2f}")

        # --- Amount in Words (Now in Bold) ---
        integer_part_of_total = int(grand_total)
        words = num2words(integer_part_of_total, lang='en_IN').strip()
        words = words[0].upper() + words[1:] if words else ""
        words = f"{words} only/-"

        c.setFont("Helvetica-Bold", 10)  # Set font to bold
        c.drawString(margin, margin + 50, f"Amount in Words: {words}")
        c.setFont("Helvetica", 10)  # Reset font to normal for subsequent text

        # Signature Line
        signature_line_length = 150
        c.line(width - margin - signature_line_length, margin + 30, width - margin, margin + 30)
        c.setFont("Helvetica", 10)
        c.drawCentredString(width - margin - (signature_line_length / 2), margin + 15, "Authorized Signatory")

        c.save()
        self.update_company_details_file_with_serial(self.last_invoice_serial)
        tkinter.messagebox.showinfo("Saved", f"Invoice saved as {filename}")
        self.last_pdf = os.path.abspath(filename)

    def print_invoice(self):
        if hasattr(self, 'last_pdf') and os.path.exists(self.last_pdf):
            try:
                if os.name == 'nt':
                    os.startfile(self.last_pdf, "print")
                elif os.uname().sysname == 'Darwin':
                    os.system(f"lp '{self.last_pdf}'")
                else:
                    os.system(f"lpr '{self.last_pdf}'")
                tkinter.messagebox.showinfo("Print", "Invoice sent to printer.")
            except Exception as e:
                tkinter.messagebox.showerror("Error",
                                             f"Failed to print: {e}\nEnsure a PDF viewer and printer are configured.")
        else:
            tkinter.messagebox.showerror("Error", "No PDF found. Generate the invoice first.")


if __name__ == '__main__':
    app = InvoiceGeneratorApp()
    app.mainloop()
