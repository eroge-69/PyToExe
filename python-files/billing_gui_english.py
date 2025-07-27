import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import datetime
import os
import threading
import queue
import tempfile
import playsound
import pandas as pd
import pywhatkit
from fpdf import FPDF
import speech_recognition as sr
from gtts import gTTS

# --- Simple Login System ---
class LoginSystem:
    """
    A simple, predefined password-based login system.
    Manages the login window and launches the main application upon success.
    """
    # Set the predefined password here
    PREDEFINED_PASSWORD = "admin123" 

    def __init__(self, root_window):
        """Initializes the login window."""
        self.root = root_window
        self.root.title("Login")
        self.root.geometry("350x200")
        self.root.resizable(False, False)
        self.root.configure(bg="#f0f2f5")

        # --- Tkinter Variables ---
        self.password_var = tk.StringVar()

        self._create_widgets()

    def _create_widgets(self):
        """Creates and places the widgets for the login screen."""
        style = ttk.Style(self.root)
        style.theme_use("clam")
        style.configure("TFrame", background="#f0f2f5")
        style.configure("TLabel", background="#f0f2f5", font=("Segoe UI", 11))
        style.configure("TButton", font=("Segoe UI", 10, "bold"), padding=6)
        style.configure("Accent.TButton", background="#007bff", foreground="white")
        style.map("Accent.TButton", background=[('active', '#0056b3')])

        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(expand=True, fill="both")

        ttk.Label(main_frame, text="Enter Password:").grid(row=0, column=0, sticky="w", pady=(0, 5))
        password_entry = ttk.Entry(main_frame, textvariable=self.password_var, show="*", font=("Segoe UI", 11))
        password_entry.grid(row=1, column=0, sticky="ew", pady=(0, 20))
        password_entry.focus()
        
        # Binding for logging in with the "Enter" key
        password_entry.bind("<Return>", lambda event: self.login())

        login_btn = ttk.Button(main_frame, text="Login", command=self.login, style="Accent.TButton")
        login_btn.grid(row=2, column=0, sticky="ew")
        
        main_frame.columnconfigure(0, weight=1)

    def login(self):
        """Checks if the entered password matches the predefined one."""
        password = self.password_var.get()
        
        if password == self.PREDEFINED_PASSWORD:
            self._launch_main_app()
        else:
            messagebox.showerror("Access Denied", "Incorrect password.")

    def _launch_main_app(self):
        """Destroys the login window and starts the main billing application."""
        self.root.destroy()
        main_app()


# --- Main Billing Application ---
class BillingApp:
    """
    A comprehensive Grocery Billing Software with a graphical user interface,
    data persistence, reporting features, and voice control.
    """
    def __init__(self, root_window):
        """
        Initializes the application, sets up the main window, loads data,
        and creates all the UI widgets.
        """
        self.root = root_window
        self.root.title("Grocery Billing Software")
        self.root.geometry("1200x800")
        self.root.minsize(1100, 750)
        self.root.configure(bg="#f0f2f5")

        # --- Data File Paths ---
        self.DATA_DIR = "data"
        os.makedirs(self.DATA_DIR, exist_ok=True)
        self.MASTER_FILE = os.path.join(self.DATA_DIR, "master_items.json")
        self.DUE_FILE = os.path.join(self.DATA_DIR, "due_customers.json")
        self.LEDGER_FILE = os.path.join(self.DATA_DIR, "customer_ledger.json")
        self.CASHBOOK_FILE = os.path.join(self.DATA_DIR, "cashbook.json")
        self.SALES_FILE = os.path.join(self.DATA_DIR, "sales_records.json")

        self.bill_items = []
        self.load_data()

        # --- Tkinter Variables ---
        self.customer_name_var = tk.StringVar()
        self.mobile_var = tk.StringVar()
        self.bill_date_var = tk.StringVar(value=datetime.date.today().strftime("%d-%m-%Y"))
        self.item_name_var = tk.StringVar()
        self.qty_var = tk.StringVar()
        self.unit_var = tk.StringVar(value="Pcs")
        self.rate_var = tk.StringVar()
        self.payment_mode_var = tk.StringVar(value="Cash")
        self.paid_amount_var = tk.StringVar()
        
        # --- Voice Control ---
        self.voice_queue = queue.Queue()
        self.root.after(100, self.process_voice_queue)

        self.configure_styles()
        self._create_widgets()
        
        # --- Bindings ---
        self.item_name_entry.bind("<FocusOut>", self.autofill_item_details)
        self.item_name_entry.bind("<Return>", lambda e: self.qty_entry.focus())
        self.tree.bind("<Delete>", self.delete_selected_item)
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def configure_styles(self):
        """Configures the visual styles for ttk widgets."""
        style = ttk.Style(self.root)
        style.theme_use("clam")
        style.configure("TFrame", background="#f0f2f5")
        style.configure("TLabel", background="#f0f2f5", font=("Segoe UI", 11))
        style.configure("TButton", font=("Segoe UI", 11, "bold"), padding=8, borderwidth=0)
        style.configure("Accent.TButton", font=("Segoe UI", 11, "bold"), background="#007bff", foreground="white")
        style.map("Accent.TButton", background=[('active', '#0056b3')])
        style.configure("Treeview.Heading", font=("Segoe UI", 12, "bold"))
        style.configure("Treeview", font=("Segoe UI", 11), rowheight=30, background="#ffffff")
        style.map("Treeview", background=[('selected', '#007bff')])

    def load_data(self):
        """Loads all data from JSON files into memory."""
        self.masterlist = self._load_json(self.MASTER_FILE, {})
        self.due_customers = self._load_json(self.DUE_FILE, {})
        self.customer_ledger = self._load_json(self.LEDGER_FILE, {})
        self.cashbook = self._load_json(self.CASHBOOK_FILE, [])
        self.sales = self._load_json(self.SALES_FILE, [])

    def _load_json(self, filepath, default_value):
        """Helper function to load a single JSON file."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return default_value

    def _save_json(self, filepath, data):
        """Helper function to save data to a JSON file."""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    def _create_widgets(self):
        """Creates and arranges all the GUI elements in the main window."""
        self._create_top_frame()
        self._create_item_frame()
        self._create_bill_treeview()
        self._create_payment_frame()
        self._create_button_frame()
        self._create_voice_control_frame()

    def _create_top_frame(self):
        """Frame for customer details."""
        top_frame = ttk.Frame(self.root, padding="10 10 10 0")
        top_frame.pack(pady=10, padx=20, fill="x")

        ttk.Label(top_frame, text="Customer Name:").grid(row=0, column=0, padx=(0, 5), sticky="w")
        ttk.Entry(top_frame, textvariable=self.customer_name_var, width=25, font=("Segoe UI", 10)).grid(row=0, column=1, padx=5, sticky="ew")

        ttk.Label(top_frame, text="Mobile:").grid(row=0, column=2, padx=(20, 5), sticky="w")
        mobile_entry = ttk.Entry(top_frame, textvariable=self.mobile_var, width=18, font=("Segoe UI", 10))
        mobile_entry.grid(row=0, column=3, padx=5, sticky="ew")

        ttk.Label(top_frame, text="Date:").grid(row=0, column=4, padx=(20, 5), sticky="w")
        ttk.Entry(top_frame, textvariable=self.bill_date_var, width=14, font=("Segoe UI", 10)).grid(row=0, column=5, padx=5, sticky="ew")

        ttk.Button(top_frame, text="🔍 Search", command=self.search_by_mobile).grid(row=0, column=6, padx=(15, 5))
        
        top_frame.columnconfigure(1, weight=1)
        top_frame.columnconfigure(3, weight=1)

    def _create_item_frame(self):
        """Frame for adding items to the bill."""
        item_frame = ttk.Frame(self.root, padding="10 10 10 0")
        item_frame.pack(pady=5, padx=20, fill="x")

        ttk.Label(item_frame, text="Item Name:").grid(row=0, column=0, padx=(0, 5), sticky="w")
        self.item_name_entry = ttk.Entry(item_frame, textvariable=self.item_name_var, width=30, font=("Segoe UI", 10))
        self.item_name_entry.grid(row=0, column=1, padx=5, sticky="ew")

        ttk.Label(item_frame, text="Quantity:").grid(row=0, column=2, padx=(15, 5), sticky="w")
        self.qty_entry = ttk.Entry(item_frame, textvariable=self.qty_var, width=10, font=("Segoe UI", 10))
        self.qty_entry.grid(row=0, column=3, padx=5)

        ttk.Label(item_frame, text="Unit:").grid(row=0, column=4, padx=(15, 5), sticky="w")
        unit_combo = ttk.Combobox(item_frame, textvariable=self.unit_var, values=["Kg", "Litre", "Pcs", "Packet", "Gm"], width=10, state="readonly", font=("Segoe UI", 10))
        unit_combo.grid(row=0, column=5, padx=5)

        ttk.Label(item_frame, text="Rate (₹):").grid(row=0, column=6, padx=(15, 5), sticky="w")
        ttk.Entry(item_frame, textvariable=self.rate_var, width=10, font=("Segoe UI", 10)).grid(row=0, column=7, padx=5)

        ttk.Button(item_frame, text="➕ Add Item", command=self.add_item, style="Accent.TButton").grid(row=0, column=8, padx=(15, 5))
        
        item_frame.columnconfigure(1, weight=2)

    def _create_bill_treeview(self):
        """Frame for displaying the current bill items in a treeview."""
        tree_frame = ttk.Frame(self.root)
        tree_frame.pack(pady=10, padx=20, fill="both", expand=True)

        self.tree = ttk.Treeview(tree_frame, columns=("Item", "Quantity", "Unit", "Rate", "Total"), show="headings")
        
        headings = {"Item": 200, "Quantity": 100, "Unit": 100, "Rate": 100, "Total": 100}
        for col, width in headings.items():
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor="center", width=width)
            
        self.tree.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        
        self.total_label = ttk.Label(self.root, text="Total: ₹0.00", font=("Segoe UI", 16, "bold"), background="#f0f2f5", foreground="#1d2129")
        self.total_label.pack(pady=(5, 10))

    def _create_payment_frame(self):
        """Frame for payment details."""
        payment_frame = ttk.Frame(self.root, padding=10)
        payment_frame.pack(pady=5, padx=20, fill="x")

        ttk.Label(payment_frame, text="Payment Mode:").pack(side="left", padx=(0, 10))
        ttk.Radiobutton(payment_frame, text="Cash", variable=self.payment_mode_var, value="Cash").pack(side="left", padx=5)
        ttk.Radiobutton(payment_frame, text="Credit", variable=self.payment_mode_var, value="Credit").pack(side="left", padx=5)

        ttk.Label(payment_frame, text="Paid Amount (₹):").pack(side="left", padx=(40, 10))
        ttk.Entry(payment_frame, textvariable=self.paid_amount_var, width=15, font=("Segoe UI", 10)).pack(side="left", padx=5)

    def _create_button_frame(self):
        """Frame for main action buttons."""
        btn_frame = ttk.Frame(self.root, padding="10 0")
        btn_frame.pack(pady=10)

        buttons = {
            "🧾 Generate Bill": self.generate_bill,
            "🔄 Reset": self.reset_bill,
            "📄 Export PDF": self.export_pdf,
            "📊 Export Excel": self.export_excel,
            "💬 Send WhatsApp": self.send_whatsapp,
        }
        for i, (text, cmd) in enumerate(buttons.items()):
            ttk.Button(btn_frame, text=text, command=cmd).grid(row=0, column=i, padx=8)

        reports_frame = ttk.Frame(self.root, padding="10 0")
        reports_frame.pack(pady=5)
        
        report_buttons = {
            "📈 Daily Sales": self.export_sales_report,
            "💰 Daily Cash": self.export_cash_report,
            "🔔 Due Reminders": self.send_due_reminders,
        }
        for i, (text, cmd) in enumerate(report_buttons.items()):
            ttk.Button(reports_frame, text=text, command=cmd).grid(row=0, column=i, padx=8)

    def _create_voice_control_frame(self):
        """Frame for the voice control button."""
        voice_frame = ttk.Frame(self.root, padding="10 0")
        voice_frame.pack(pady=10)
        self.voice_button = ttk.Button(voice_frame, text="🎤 Start Voice Command", style="Accent.TButton", command=self.start_voice_thread)
        self.voice_button.pack()

    def update_total(self):
        """Calculates and updates the total bill amount label."""
        total = sum(float(item[4]) for item in self.bill_items)
        self.total_label.config(text=f"Total: ₹{total:.2f}")

    def add_item(self):
        """Adds a new item to the bill."""
        name = self.item_name_var.get().strip().title()
        q_str = self.qty_var.get().strip()
        r_str = self.rate_var.get().strip()
        unit = self.unit_var.get()

        if not all([name, q_str, r_str]):
            messagebox.showerror("Error", "Please fill Item Name, Quantity, and Rate.")
            return
        try:
            qty_val = float(q_str)
            rate_val = float(r_str)
            total = qty_val * rate_val
        except ValueError:
            messagebox.showerror("Error", "Invalid input for Quantity or Rate. Please enter numbers.")
            return

        item_data = [name, f"{qty_val:.2f}", unit, f"{rate_val:.2f}", f"{total:.2f}"]
        self.bill_items.append(item_data)
        self.tree.insert("", "end", values=item_data)
        self.update_total()

        self.masterlist[name] = {"unit": unit, "rate": str(rate_val)}
        
        self.item_name_var.set("")
        self.qty_var.set("")
        self.rate_var.set("")
        self.unit_var.set("Pcs")
        self.item_name_entry.focus()

    def delete_selected_item(self, event=None):
        """Deletes the selected item from the bill."""
        selected_items = self.tree.selection()
        if not selected_items:
            messagebox.showinfo("Info", "Please select an item to delete.")
            return
        
        for selected_item in selected_items:
            item_values = self.tree.item(selected_item)['values']
            try:
                item_to_remove = next(item for item in self.bill_items if all(str(i) == str(j) for i, j in zip(item, item_values)))
                self.bill_items.remove(item_to_remove)
            except StopIteration:
                print(f"Warning: Could not find item {item_values} in backend list for deletion.")

            self.tree.delete(selected_item)
        
        self.update_total()
        self.speak("Item removed.")

    def reset_bill(self, confirm=True):
        """Clears the entire bill and customer information."""
        if confirm:
            if not messagebox.askyesno("Confirm", "Are you sure you want to reset the current bill?"):
                return
        
        self.bill_items.clear()
        if self.tree.winfo_exists():
            for i in self.tree.get_children():
                self.tree.delete(i)

        self.update_total()
        self.customer_name_var.set("")
        self.mobile_var.set("")
        self.paid_amount_var.set("")
        self.bill_date_var.set(datetime.date.today().strftime("%d-%m-%Y"))
        if confirm:
            self.speak("Bill reset.")

    def generate_bill(self):
        """Finalizes the bill, saves all records, and resets the interface."""
        name = self.customer_name_var.get().strip()
        mobile = self.mobile_var.get().strip()
        
        if not name or not mobile or not self.bill_items:
            messagebox.showerror("Error", "Customer info and at least one item are required to generate a bill.")
            return
        
        if not self._is_valid_mobile(mobile):
            messagebox.showerror("Error", "Invalid Mobile Number. It must be 10 digits.")
            return

        date = self.bill_date_var.get()
        mode = self.payment_mode_var.get()
        paid_str = self.paid_amount_var.get().strip()
        total = sum(float(item[4]) for item in self.bill_items)

        if not paid_str:
            if mode == "Cash":
                paid_amt = total
                self.paid_amount_var.set(f"{total:.2f}")
            else: # Credit
                paid_amt = 0.0
                self.paid_amount_var.set("0.00")
        else:
            try:
                paid_amt = float(paid_str)
            except ValueError:
                messagebox.showerror("Error", "Invalid Paid Amount. Please enter a number.")
                return

        due = total - paid_amt

        if due > 0:
            self.due_customers.setdefault(mobile, {"name": name, "due": 0})
            self.due_customers[mobile]["due"] += due
        
        bill_record = {
            "date": date, "customer": name, "mobile": mobile,
            "items": self.bill_items, "total": total, "paid": paid_amt,
            "due": due, "mode": mode
        }
        self.customer_ledger.setdefault(mobile, []).append(bill_record)
        self.sales.append(bill_record)
        if paid_amt > 0 and mode == "Cash":
            self.cashbook.append({
                "date": date, "desc": f"Bill: {name} ({mobile})",
                "in": paid_amt, "out": 0
            })

        self._save_all_data() 

        final_due = self.due_customers.get(mobile, {}).get("due", 0)
        msg = f"Thank you {name}! Your bill total is ₹{total:.2f}. Your total outstanding balance is ₹{final_due:.2f}."
        self.speak(msg)
        messagebox.showinfo("Bill Generated", msg)
        self.reset_bill(confirm=False)

    def _is_valid_mobile(self, mobile):
        """Checks if the mobile number is valid (10 digits)."""
        return mobile.isdigit() and len(mobile) == 10

    def autofill_item_details(self, event=None):
        """Autofills item rate and unit from masterlist when an item name is entered."""
        name = self.item_name_var.get().strip().title()
        if name in self.masterlist:
            item_details = self.masterlist[name]
            self.rate_var.set(item_details.get("rate", ""))
            self.unit_var.set(item_details.get("unit", "Pcs"))

    def search_by_mobile(self):
        """Searches for a customer's ledger by their mobile number."""
        mobile = self.mobile_var.get().strip()
        if not mobile:
            messagebox.showerror("Error", "Please enter a mobile number to search.")
            return
        
        if not self._is_valid_mobile(mobile):
            messagebox.showerror("Error", "Invalid Mobile Number. It must be 10 digits.")
            return

        ledger = self.customer_ledger.get(mobile)
        due_info = self.due_customers.get(mobile)

        if not ledger:
            messagebox.showinfo("Info", "No records found for this mobile number.")
            return

        ledger_win = tk.Toplevel(self.root)
        ledger_win.title(f"Ledger for {ledger[0]['customer']} ({mobile})")
        ledger_win.geometry("600x400")
        
        info_text = f"Customer: {ledger[0]['customer']}\n"
        if due_info:
            info_text += f"Total Due: ₹{due_info['due']:.2f}\n\n--- Last 5 Transactions ---\n"
        
        for entry in reversed(ledger[-5:]):
            info_text += f"Date: {entry['date']}, Total: ₹{entry['total']:.2f}, Paid: ₹{entry['paid']:.2f}, Due: ₹{entry['due']:.2f}\n"
        
        ttk.Label(ledger_win, text=info_text, font=("Courier", 10), padding=10).pack(expand=True, fill="both")

    def export_pdf(self):
        """Exports the current bill as a PDF file."""
        if not self.bill_items:
            messagebox.showerror("Error", "No items in the bill to export.")
            return
            
        filename = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF Files", "*.pdf")],
            initialfile=f"Bill_{self.customer_name_var.get().replace(' ', '_')}_{datetime.date.today()}.pdf"
        )
        if not filename: return

        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", 'B', 16)

        pdf.cell(0, 10, txt="Grocery Invoice", ln=True, align="C")
        
        pdf.set_font("Arial", '', 12)
        pdf.cell(0, 10, txt=f"Customer: {self.customer_name_var.get()}", ln=True)
        pdf.cell(0, 10, txt=f"Mobile: {self.mobile_var.get()}", ln=True)
        pdf.cell(0, 10, txt=f"Date: {self.bill_date_var.get()}", ln=True)
        pdf.ln(10)

        pdf.set_font("Arial", 'B', 10)
        pdf.cell(80, 10, "Item", 1, 0, 'C')
        pdf.cell(25, 10, "Quantity", 1, 0, 'C')
        pdf.cell(25, 10, "Unit", 1, 0, 'C')
        pdf.cell(30, 10, "Rate", 1, 0, 'C')
        pdf.cell(30, 10, "Total", 1, 1, 'C')

        pdf.set_font("Arial", '', 10)
        for item in self.bill_items:
            pdf.cell(80, 10, item[0], 1)
            pdf.cell(25, 10, item[1], 1, 0, 'R')
            pdf.cell(25, 10, item[2], 1, 0, 'C')
            pdf.cell(30, 10, f"{item[3]}", 1, 0, 'R')
            pdf.cell(30, 10, f"{item[4]}", 1, 1, 'R')
        
        total = sum(float(item[4]) for item in self.bill_items)
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(160, 10, "Grand Total", 1, 0, 'R')
        pdf.cell(30, 10, f"Rs {total:.2f}", 1, 1, 'R')

        try:
            pdf.output(filename)
            messagebox.showinfo("Success", f"PDF saved successfully to:\n{filename}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save PDF: {e}")

    def export_excel(self):
        """Exports the current bill to an Excel file."""
        if not self.bill_items:
            messagebox.showerror("Error", "No items to export.")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel Files", "*.xlsx")],
            initialfile=f"Bill_{self.customer_name_var.get().replace(' ', '_')}_{datetime.date.today()}.xlsx"
        )
        if not filename: return

        df = pd.DataFrame(self.bill_items, columns=["Item", "Quantity", "Unit", "Rate", "Total"])
        try:
            df.to_excel(filename, index=False)
            messagebox.showinfo("Success", f"Excel file saved successfully to:\n{filename}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save Excel file: {e}")

    def send_whatsapp(self):
        """Sends the bill summary via WhatsApp."""
        name = self.customer_name_var.get().strip()
        mobile = self.mobile_var.get().strip()
        if not all([name, mobile, self.bill_items]):
            messagebox.showerror("Error", "Complete bill information is required.")
            return
        
        if not self._is_valid_mobile(mobile):
            messagebox.showerror("Error", "Invalid Mobile Number. It must be 10 digits.")
            return

        total = sum(float(item[4]) for item in self.bill_items)
        due_info = self.due_customers.get(mobile, {})
        due = due_info.get("due", 0) if due_info else 0
        msg = f"Thank you {name}! Your bill total is: *Rs {total:.2f}*. Your total outstanding balance is: *Rs {due:.2f}*."

        try:
            threading.Thread(target=pywhatkit.sendwhatmsg_instantly, args=(f"+91{mobile}", msg), kwargs={"wait_time": 15, "tab_close": True}, daemon=True).start()
            messagebox.showinfo("Success", "Attempting to send WhatsApp message.\nPlease check your browser.")
        except Exception as e:
            messagebox.showerror("WhatsApp Error", f"Could not send message: {e}")

    def send_due_reminders(self):
        """Sends WhatsApp reminders to all customers with due amounts."""
        due_list = {mobile: info for mobile, info in self.due_customers.items() if info.get("due", 0) > 0}
        if not due_list:
            messagebox.showinfo("Info", "No customers with due amounts found.")
            return

        if not messagebox.askyesno("Confirm", f"This will attempt to send reminders to {len(due_list)} customers. Continue?"):
            return

        threading.Thread(target=self._send_reminders_thread, args=(due_list,), daemon=True).start()
        messagebox.showinfo("In Progress", "Sending due reminders in the background. This may take a while.")

    def _send_reminders_thread(self, due_list):
        """The actual threaded work of sending multiple reminders."""
        sent_count = 0
        for mobile, info in due_list.items():
            msg = f"Dear {info['name']}, this is a friendly reminder that you have a due amount of *Rs {info['due']:.2f}*. Kindly clear it at your earliest convenience. Thank you!"
            try:
                pywhatkit.sendwhatmsg_instantly(f"+91{mobile}", msg, wait_time=20, tab_close=True)
                sent_count += 1
            except Exception as e:
                print(f"Failed to send reminder to {mobile}: {e}")
        print(f"Finished sending reminders. {sent_count} successful.")

    def _export_report(self, data, filename_prefix):
        """Generic function to export report data to Excel."""
        if not data:
            messagebox.showinfo("Info", f"No data available for today's {filename_prefix} report.")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel Files", "*.xlsx")],
            initialfile=f"{filename_prefix}_Report_{datetime.date.today().strftime('%Y-%m-%d')}.xlsx"
        )
        if not filename: return

        df = pd.DataFrame(data)
        try:
            df.to_excel(filename, index=False)
            messagebox.showinfo("Success", f"{filename_prefix.title()} report saved successfully.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save report: {e}")

    def export_sales_report(self):
        """Exports a sales report for the current day."""
        today = datetime.date.today().strftime("%d-%m-%Y")
        daily_sales = [s for s in self.sales if s["date"] == today]
        report_data = [{
            "Customer": s["customer"], "Mobile": s["mobile"], "Total": s["total"],
            "Paid": s["paid"], "Due": s["due"], "Mode": s["mode"]
        } for s in daily_sales]
        self._export_report(report_data, "Sales")

    def export_cash_report(self):
        """Exports a cashbook report for the current day."""
        today = datetime.date.today().strftime("%d-%m-%Y")
        daily_cash = [c for c in self.cashbook if c["date"] == today]
        self._export_report(daily_cash, "Cash")

    def speak(self, text):
        """Converts text to speech and plays it in a non-blocking thread."""
        thread = threading.Thread(target=self._blocking_speak, args=(text,), daemon=True)
        thread.start()
        return thread

    def _blocking_speak(self, text):
        """
        The actual blocking part of the speech synthesis.
        """
        filepath = None
        try:
            tts = gTTS(text=text, lang="en-in")
            
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as fp:
                filepath = fp.name
            
            tts.save(filepath)
            
            playsound.playsound(filepath)

        except Exception as e:
            print(f"Error in TTS playback: {e}")
        finally:
            if filepath and os.path.exists(filepath):
                try:
                    os.remove(filepath)
                except OSError as e:
                    print(f"Error removing temp file {filepath}: {e}")

    def start_voice_thread(self):
        """
        Starts the voice recognition process.
        """
        self.voice_button.config(state="disabled")
        threading.Thread(target=self.run_voice_command_sequence, daemon=True).start()

    def run_voice_command_sequence(self):
        """
        Handles the complete voice command sequence: speak, then listen.
        """
        try:
            self.speak("Listening...")
            
            r = sr.Recognizer()
            with sr.Microphone() as source:
                r.pause_threshold = 1.0
                r.adjust_for_ambient_noise(source, duration=1)
                print("Listening...")
                try:
                    audio = r.listen(source, timeout=10, phrase_time_limit=6)
                    command = r.recognize_google(audio, language="en-IN").lower()
                    print(f"Recognized: {command}")
                    self.voice_queue.put(command)
                except sr.UnknownValueError:
                    self.speak("Sorry, I could not understand that.")
                except sr.WaitTimeoutError:
                    self.speak("No speech detected.")
                except Exception as e:
                    print(f"Voice recognition error: {e}")
                    self.speak("There was an error with voice recognition.")
        finally:
            self.root.after(0, lambda: self.voice_button.config(state="normal"))

    def process_voice_queue(self):
        """Processes commands from the voice queue in the main GUI thread."""
        try:
            command = self.voice_queue.get_nowait()
            self.handle_command(command)
        except queue.Empty:
            pass
        finally:
            if self.root.winfo_exists():
                self.root.after(100, self.process_voice_queue)

    def handle_command(self, command):
        """Executes actions based on the recognized voice command."""
        if "add item" in command:
            self.add_item()
        elif "generate bill" in command:
            self.generate_bill()
        elif "reset bill" in command or "clear all" in command:
            self.reset_bill()
        elif "export pdf" in command:
            self.export_pdf()
        elif "send whatsapp" in command:
            self.send_whatsapp()
        elif "delete item" in command or "remove item" in command:
            self.delete_selected_item()
        else:
            self.speak("Command not recognized.")

    def _save_all_data(self):
        """Saves all current data to their respective JSON files."""
        try:
            self._save_json(self.MASTER_FILE, self.masterlist)
            self._save_json(self.DUE_FILE, self.due_customers)
            self._save_json(self.LEDGER_FILE, self.customer_ledger)
            self._save_json(self.CASHBOOK_FILE, self.cashbook)
            self._save_json(self.SALES_FILE, self.sales)
        except Exception as e:
            print(f"Error saving data: {e}")
            messagebox.showerror("Save Error", f"Could not save data to files:\n{e}")

    def on_closing(self):
        """Handles saving data and properly closing the application."""
        self._save_all_data()
        self.root.destroy()

# --- Application Launchers ---

def main_app():
    """Initializes and runs the main billing application window."""
    root = tk.Tk()
    app = BillingApp(root)
    root.mainloop()

if __name__ == "__main__":
    # Start with the login system.
    # The login system will call main_app() upon successful login.
    login_root = tk.Tk()
    app = LoginSystem(login_root)
    login_root.mainloop()
