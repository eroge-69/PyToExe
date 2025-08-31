import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pandas as pd
import os
from datetime import datetime

class ChurchOfferingSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("Church Offering Management System")
        self.root.geometry("1000x700")
        
        # Data storage
        self.families_df = pd.DataFrame(columns=["FamilyID", "FamilyName", "HeadOfFamily", "ContactNumber"])
        self.members_df = pd.DataFrame(columns=["FamilyID", "MemberName", "Relationship"])
        self.offerings_df = pd.DataFrame(columns=["Date", "OfferingType", "FamilyID", "Amount"])
        self.offering_types = ["Thanks Giving", "Harvest Festival", "Christmas", "New Year", "Church Day", "Monthly"]
        
        # Create main notebook (tabs)
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Create frames for each tab
        self.family_frame = ttk.Frame(self.notebook)
        self.member_frame = ttk.Frame(self.notebook)
        self.offering_frame = ttk.Frame(self.notebook)
        self.report_frame = ttk.Frame(self.notebook)
        self.receipt_frame = ttk.Frame(self.notebook)
        
        self.notebook.add(self.family_frame, text="Family Management")
        self.notebook.add(self.member_frame, text="Member Management")
        self.notebook.add(self.offering_frame, text="Offering Entry")
        self.notebook.add(self.report_frame, text="Reports")
        self.notebook.add(self.receipt_frame, text="Receipt Generation")
        
        # Initialize each tab
        self.setup_family_tab()
        self.setup_member_tab()
        self.setup_offering_tab()
        self.setup_report_tab()
        self.setup_receipt_tab()
        
        # Load existing data if available
        self.load_data()
    
    def setup_family_tab(self):
        # Family management UI
        frame = ttk.LabelFrame(self.family_frame, text="Family Details")
        frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Input fields
        ttk.Label(frame, text="Family ID:").grid(row=0, column=0, padx=5, pady=5, sticky='e')
        self.family_id = ttk.Entry(frame)
        self.family_id.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(frame, text="Family Name:").grid(row=1, column=0, padx=5, pady=5, sticky='e')
        self.family_name = ttk.Entry(frame)
        self.family_name.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(frame, text="Head of Family:").grid(row=2, column=0, padx=5, pady=5, sticky='e')
        self.head_of_family = ttk.Entry(frame)
        self.head_of_family.grid(row=2, column=1, padx=5, pady=5)
        
        ttk.Label(frame, text="Contact Number:").grid(row=3, column=0, padx=5, pady=5, sticky='e')
        self.contact_number = ttk.Entry(frame)
        self.contact_number.grid(row=3, column=1, padx=5, pady=5)
        
        # Buttons
        btn_frame = ttk.Frame(frame)
        btn_frame.grid(row=4, column=0, columnspan=2, pady=10)
        
        ttk.Button(btn_frame, text="Add Family", command=self.add_family).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Load from Excel", command=self.load_families_from_excel).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Save to Excel", command=self.save_families_to_excel).pack(side=tk.LEFT, padx=5)
        
        # Family list
        list_frame = ttk.Frame(frame)
        list_frame.grid(row=5, column=0, columnspan=2, pady=10, sticky='nsew')
        
        columns = ("Family ID", "Family Name", "Head of Family", "Contact")
        self.family_tree = ttk.Treeview(list_frame, columns=columns, show="headings")
        
        for col in columns:
            self.family_tree.heading(col, text=col)
            self.family_tree.column(col, width=100)
        
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.family_tree.yview)
        self.family_tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.family_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Bind selection event
        self.family_tree.bind("<<TreeviewSelect>>", self.on_family_select)
    
    def setup_member_tab(self):
        # Member management UI
        frame = ttk.LabelFrame(self.member_frame, text="Member Details")
        frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Input fields
        ttk.Label(frame, text="Family ID:").grid(row=0, column=0, padx=5, pady=5, sticky='e')
        self.member_family_id = ttk.Combobox(frame, state="readonly")
        self.member_family_id.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(frame, text="Member Name:").grid(row=1, column=0, padx=5, pady=5, sticky='e')
        self.member_name = ttk.Entry(frame)
        self.member_name.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(frame, text="Relationship:").grid(row=2, column=0, padx=5, pady=5, sticky='e')
        self.relationship = ttk.Combobox(frame, values=["Head", "Spouse", "Son", "Daughter", "Other"])
        self.relationship.grid(row=2, column=1, padx=5, pady=5)
        
        # Buttons
        btn_frame = ttk.Frame(frame)
        btn_frame.grid(row=3, column=0, columnspan=2, pady=10)
        
        ttk.Button(btn_frame, text="Add Member", command=self.add_member).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Load from Excel", command=self.load_members_from_excel).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Save to Excel", command=self.save_members_to_excel).pack(side=tk.LEFT, padx=5)
        
        # Member list
        list_frame = ttk.Frame(frame)
        list_frame.grid(row=4, column=0, columnspan=2, pady=10, sticky='nsew')
        
        columns = ("Family ID", "Member Name", "Relationship")
        self.member_tree = ttk.Treeview(list_frame, columns=columns, show="headings")
        
        for col in columns:
            self.member_tree.heading(col, text=col)
            self.member_tree.column(col, width=100)
        
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.member_tree.yview)
        self.member_tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.member_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    
    def setup_offering_tab(self):
        # Offering entry UI
        frame = ttk.LabelFrame(self.offering_frame, text="Offering Entry")
        frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Input fields
        ttk.Label(frame, text="Offering Type:").grid(row=0, column=0, padx=5, pady=5, sticky='e')
        self.offering_type = ttk.Combobox(frame, values=self.offering_types, state="readonly")
        self.offering_type.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(frame, text="Date:").grid(row=1, column=0, padx=5, pady=5, sticky='e')
        self.offering_date = ttk.Entry(frame)
        self.offering_date.insert(0, datetime.today().strftime('%Y-%m-%d'))
        self.offering_date.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(frame, text="Family ID:").grid(row=2, column=0, padx=5, pady=5, sticky='e')
        self.offering_family_id = ttk.Combobox(frame, state="readonly")
        self.offering_family_id.grid(row=2, column=1, padx=5, pady=5)
        
        ttk.Label(frame, text="Amount:").grid(row=3, column=0, padx=5, pady=5, sticky='e')
        self.amount = ttk.Entry(frame)
        self.amount.grid(row=3, column=1, padx=5, pady=5)
        
        # Barcode section
        ttk.Label(frame, text="Barcode Scan:").grid(row=4, column=0, padx=5, pady=5, sticky='e')
        self.barcode_entry = ttk.Entry(frame)
        self.barcode_entry.grid(row=4, column=1, padx=5, pady=5)
        self.barcode_entry.bind('<Return>', self.process_barcode)
        
        # Buttons
        btn_frame = ttk.Frame(frame)
        btn_frame.grid(row=5, column=0, columnspan=2, pady=10)
        
        ttk.Button(btn_frame, text="Record Offering", command=self.record_offering).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Load Offerings", command=self.load_offerings_from_excel).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Save Offerings", command=self.save_offerings_to_excel).pack(side=tk.LEFT, padx=5)
        
        # Offering list
        list_frame = ttk.Frame(frame)
        list_frame.grid(row=6, column=0, columnspan=2, pady=10, sticky='nsew')
        
        columns = ("Date", "Offering Type", "Family ID", "Amount")
        self.offering_tree = ttk.Treeview(list_frame, columns=columns, show="headings")
        
        for col in columns:
            self.offering_tree.heading(col, text=col)
            self.offering_tree.column(col, width=100)
        
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.offering_tree.yview)
        self.offering_tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.offering_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    
    def setup_report_tab(self):
        # Report generation UI
        frame = ttk.LabelFrame(self.report_frame, text="Reports")
        frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Report options
        ttk.Label(frame, text="Report Type:").grid(row=0, column=0, padx=5, pady=5, sticky='e')
        self.report_type = ttk.Combobox(frame, values=["Offering Summary", "Family-wise Report", "Offering Type Summary"], state="readonly")
        self.report_type.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(frame, text="Start Date:").grid(row=1, column=0, padx=5, pady=5, sticky='e')
        self.start_date = ttk.Entry(frame)
        self.start_date.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(frame, text="End Date:").grid(row=2, column=0, padx=5, pady=5, sticky='e')
        self.end_date = ttk.Entry(frame)
        self.end_date.grid(row=2, column=1, padx=5, pady=5)
        
        # Buttons
        btn_frame = ttk.Frame(frame)
        btn_frame.grid(row=3, column=0, columnspan=2, pady=10)
        
        ttk.Button(btn_frame, text="Generate Report", command=self.generate_report).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Export to Excel", command=self.export_report).pack(side=tk.LEFT, padx=5)
        
        # Report display
        report_display_frame = ttk.Frame(frame)
        report_display_frame.grid(row=4, column=0, columnspan=2, pady=10, sticky='nsew')
        
        self.report_text = tk.Text(report_display_frame, height=20, width=80)
        scrollbar = ttk.Scrollbar(report_display_frame, orient=tk.VERTICAL, command=self.report_text.yview)
        self.report_text.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.report_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    
    def setup_receipt_tab(self):
        # Receipt generation UI
        frame = ttk.LabelFrame(self.receipt_frame, text="Receipt Generation")
        frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Input fields
        ttk.Label(frame, text="Family ID:").grid(row=0, column=0, padx=5, pady=5, sticky='e')
        self.receipt_family_id = ttk.Combobox(frame, state="readonly")
        self.receipt_family_id.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(frame, text="Start Date:").grid(row=1, column=0, padx=5, pady=5, sticky='e')
        self.receipt_start_date = ttk.Entry(frame)
        self.receipt_start_date.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(frame, text="End Date:").grid(row=2, column=0, padx=5, pady=5, sticky='e')
        self.receipt_end_date = ttk.Entry(frame)
        self.receipt_end_date.grid(row=2, column=1, padx=5, pady=5)
        
        # Buttons
        btn_frame = ttk.Frame(frame)
        btn_frame.grid(row=3, column=0, columnspan=2, pady=10)
        
        ttk.Button(btn_frame, text="Generate Receipt", command=self.generate_receipt).pack(side=tk.LEFT, padx=5)
        
        # Receipt display
        receipt_display_frame = ttk.Frame(frame)
        receipt_display_frame.grid(row=4, column=0, columnspan=2, pady=10, sticky='nsew')
        
        self.receipt_text = tk.Text(receipt_display_frame, height=20, width=80)
        scrollbar = ttk.Scrollbar(receipt_display_frame, orient=tk.VERTICAL, command=self.receipt_text.yview)
        self.receipt_text.configure(yscscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.receipt_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    
    def load_data(self):
        # Try to load existing data from Excel files
        try:
            if os.path.exists("families.xlsx"):
                self.families_df = pd.read_excel("families.xlsx")
                self.update_family_comboboxes()
                self.refresh_family_tree()
            
            if os.path.exists("members.xlsx"):
                self.members_df = pd.read_excel("members.xlsx")
                self.refresh_member_tree()
            
            if os.path.exists("offerings.xlsx"):
                self.offerings_df = pd.read_excel("offerings.xlsx")
                self.refresh_offering_tree()
                
        except Exception as e:
            # Initialize empty dataframes
            self.families_df = pd.DataFrame(columns=["FamilyID", "FamilyName", "HeadOfFamily", "ContactNumber"])
            self.members_df = pd.DataFrame(columns=["FamilyID", "MemberName", "Relationship"])
            self.offerings_df = pd.DataFrame(columns=["Date", "OfferingType", "FamilyID", "Amount"])
    
    def add_family(self):
        # Add a new family to the database
        family_id = self.family_id.get().strip()
        family_name = self.family_name.get().strip()
        head_of_family = self.head_of_family.get().strip()
        contact = self.contact_number.get().strip()
        
        if not family_id or not family_name:
            messagebox.showerror("Error", "Family ID and Name are required!")
            return
        
        # Check if family ID already exists
        if not self.families_df.empty and family_id in self.families_df["FamilyID"].values:
            messagebox.showerror("Error", "Family ID already exists!")
            return
        
        # Add to dataframe
        new_family = pd.DataFrame({
            "FamilyID": [family_id],
            "FamilyName": [family_name],
            "HeadOfFamily": [head_of_family],
            "ContactNumber": [contact]
        })
        
        self.families_df = pd.concat([self.families_df, new_family], ignore_index=True)
        self.update_family_comboboxes()
        self.refresh_family_tree()
        
        messagebox.showinfo("Success", "Family added successfully!")
        self.clear_family_fields()
    
    def add_member(self):
        # Add a new member to a family
        family_id = self.member_family_id.get().strip()
        member_name = self.member_name.get().strip()
        relationship = self.relationship.get().strip()
        
        if not family_id or not member_name:
            messagebox.showerror("Error", "Family ID and Member Name are required!")
            return
        
        # Add to dataframe
        new_member = pd.DataFrame({
            "FamilyID": [family_id],
            "MemberName": [member_name],
            "Relationship": [relationship]
        })
        
        self.members_df = pd.concat([self.members_df, new_member], ignore_index=True)
        self.refresh_member_tree()
        
        messagebox.showinfo("Success", "Member added successfully!")
        self.clear_member_fields()
    
    def record_offering(self):
        # Record a new offering
        offering_type = self.offering_type.get()
        date = self.offering_date.get().strip()
        family_id = self.offering_family_id.get().strip()
        amount = self.amount.get().strip()
        
        if not all([offering_type, date, family_id, amount]):
            messagebox.showerror("Error", "All fields are required!")
            return
        
        try:
            amount = float(amount)
        except ValueError:
            messagebox.showerror("Error", "Amount must be a number!")
            return
        
        # Add to dataframe
        new_offering = pd.DataFrame({
            "Date": [date],
            "OfferingType": [offering_type],
            "FamilyID": [family_id],
            "Amount": [amount]
        })
        
        self.offerings_df = pd.concat([self.offerings_df, new_offering], ignore_index=True)
        self.refresh_offering_tree()
        
        messagebox.showinfo("Success", "Offering recorded successfully!")
        self.clear_offering_fields()
    
    def process_barcode(self, event):
        # Process barcode scan
        barcode_data = self.barcode_entry.get().strip()
        self.offering_family_id.set(barcode_data)
        self.barcode_entry.delete(0, tk.END)
    
    def generate_report(self):
        # Generate report based on selected criteria
        report_type = self.report_type.get()
        start_date = self.start_date.get().strip()
        end_date = self.end_date.get().strip()
        
        if not report_type:
            messagebox.showerror("Error", "Please select a report type!")
            return
        
        # Filter by date if provided
        filtered_offerings = self.offerings_df.copy()
        if start_date:
            filtered_offerings = filtered_offerings[filtered_offerings["Date"] >= start_date]
        if end_date:
            filtered_offerings = filtered_offerings[filtered_offerings["Date"] <= end_date]
        
        if report_type == "Offering Summary":
            report = filtered_offerings.groupby("OfferingType")["Amount"].sum()
            report_text = "OFFERING SUMMARY REPORT\n\n"
            report_text += f"Period: {start_date or 'Start'} to {end_date or 'End'}\n\n"
            for offering_type, total in report.items():
                report_text += f"{offering_type}: ₹{total:,.2f}\n"
            report_text += f"\nGRAND TOTAL: ₹{report.sum():,.2f}"
            
        elif report_type == "Family-wise Report":
            report = filtered_offerings.groupby("FamilyID")["Amount"].sum()
            report_text = "FAMILY-WISE OFFERING REPORT\n\n"
            report_text += f"Period: {start_date or 'Start'} to {end_date or 'End'}\n\n"
            for family_id, total in report.items():
                report_text += f"{family_id}: ₹{total:,.2f}\n"
            report_text += f"\nGRAND TOTAL: ₹{report.sum():,.2f}"
            
        elif report_type == "Offering Type Summary":
            # Create a pivot table
            pivot_table = pd.pivot_table(filtered_offerings, 
                                       values='Amount', 
                                       index='OfferingType', 
                                       columns='FamilyID', 
                                       aggfunc='sum', 
                                       fill_value=0)
            report_text = "DETAILED OFFERING REPORT\n\n"
            report_text += f"Period: {start_date or 'Start'} to {end_date or 'End'}\n\n"
            report_text += pivot_table.to_string()
            report_text += f"\n\nGRAND TOTAL: ₹{filtered_offerings['Amount'].sum():,.2f}"
        
        self.report_text.delete(1.0, tk.END)
        self.report_text.insert(1.0, report_text)
    
    def generate_receipt(self):
        # Generate receipt for a family
        family_id = self.receipt_family_id.get().strip()
        start_date = self.receipt_start_date.get().strip()
        end_date = self.receipt_end_date.get().strip()
        
        if not family_id:
            messagebox.showerror("Error", "Please select a Family ID!")
            return
        
        # Filter offerings for this family
        family_offerings = self.offerings_df[self.offerings_df["FamilyID"] == family_id].copy()
        
        # Filter by date if provided
        if start_date:
            family_offerings = family_offerings[family_offerings["Date"] >= start_date]
        if end_date:
            family_offerings = family_offerings[family_offerings["Date"] <= end_date]
        
        if family_offerings.empty:
            messagebox.showinfo("Info", "No offerings found for this family in the selected period!")
            return
        
        # Get family details
        family_details = self.families_df[self.families_df["FamilyID"] == family_id].iloc[0]
        
        # Generate receipt text
        receipt_text = "CHURCH OFFERING RECEIPT\n\n"
        receipt_text += f"Family ID: {family_id}\n"
        receipt_text += f"Family Name: {family_details['FamilyName']}\n"
        receipt_text += f"Head of Family: {family_details['HeadOfFamily']}\n"
        receipt_text += f"Contact: {family_details['ContactNumber']}\n"
        receipt_text += f"Period: {start_date or 'Start'} to {end_date or 'End'}\n\n"
        receipt_text += "OFFERINGS:\n"
        receipt_text += "-" * 50 + "\n"
        
        for _, offering in family_offerings.iterrows():
            receipt_text += f"{offering['Date']} - {offering['OfferingType']}: ₹{offering['Amount']:,.2f}\n"
        
        receipt_text += "-" * 50 + "\n"
        total = family_offerings["Amount"].sum()
        receipt_text += f"TOTAL: ₹{total:,.2f}\n\n"
        receipt_text += "Thank you for your generous offerings!\n"
        receipt_text += f"Generated on: {datetime.today().strftime('%Y-%m-%d')}"
        
        self.receipt_text.delete(1.0, tk.END)
        self.receipt_text.insert(1.0, receipt_text)
    
    def export_report(self):
        # Export report to Excel
        file_path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                # Get the current report text
                report_text = self.report_text.get(1.0, tk.END)
                
                # For simplicity, we'll just save the offerings data
                self.offerings_df.to_excel(file_path, index=False)
                messagebox.showinfo("Success", f"Report exported to {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Could not export report: {str(e)}")
    
    def load_families_from_excel(self):
        file_path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")])
        if file_path:
            try:
                self.families_df = pd.read_excel(file_path)
                self.update_family_comboboxes()
                self.refresh_family_tree()
                messagebox.showinfo("Success", "Families loaded from Excel successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Could not load families: {str(e)}")
    
    def save_families_to_excel(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")]
        )
        if file_path:
            try:
                self.families_df.to_excel(file_path, index=False)
                messagebox.showinfo("Success", "Families saved to Excel successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Could not save families: {str(e)}")
    
    def load_members_from_excel(self):
        file_path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")])
        if file_path:
            try:
                self.members_df = pd.read_excel(file_path)
                self.refresh_member_tree()
                messagebox.showinfo("Success", "Members loaded from Excel successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Could not load members: {str(e)}")
    
    def save_members_to_excel(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")]
        )
        if file_path:
            try:
                self.members_df.to_excel(file_path, index=False)
                messagebox.showinfo("Success", "Members saved to Excel successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Could not save members: {str(e)}")
    
    def load_offerings_from_excel(self):
        file_path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")])
        if file_path:
            try:
                self.offerings_df = pd.read_excel(file_path)
                self.refresh_offering_tree()
                messagebox.showinfo("Success", "Offerings loaded from Excel successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Could not load offerings: {str(e)}")
    
    def save_offerings_to_excel(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")]
        )
        if file_path:
            try:
                self.offerings_df.to_excel(file_path, index=False)
                messagebox.showinfo("Success", "Offerings saved to Excel successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Could not save offerings: {str(e)}")
    
    def update_family_comboboxes(self):
        # Update all comboboxes with family IDs
        if not self.families_df.empty:
            family_ids = self.families_df["FamilyID"].tolist()
            self.member_family_id['values'] = family_ids
            self.offering_family_id['values'] = family_ids
            self.receipt_family_id['values'] = family_ids
    
    def refresh_family_tree(self):
        # Refresh the family treeview
        for item in self.family_tree.get_children():
            self.family_tree.delete(item)
        
        if not self.families_df.empty:
            for _, row in self.families_df.iterrows():
                self.family_tree.insert("", "end", values=(
                    row["FamilyID"], row["FamilyName"], row["HeadOfFamily"], row["ContactNumber"]
                ))
    
    def refresh_member_tree(self):
        # Refresh the member treeview
        for item in self.member_tree.get_children():
            self.member_tree.delete(item)
        
        if not self.members_df.empty:
            for _, row in self.members_df.iterrows():
                self.member_tree.insert("", "end", values=(
                    row["FamilyID"], row["MemberName"], row["Relationship"]
                ))
    
    def refresh_offering_tree(self):
        # Refresh the offering treeview
        for item in self.offering_tree.get_children():
            self.offering_tree.delete(item)
        
        if not self.offerings_df.empty:
            for _, row in self.offerings_df.iterrows():
                self.offering_tree.insert("", "end", values=(
                    row["Date"], row["OfferingType"], row["FamilyID"], row["Amount"]
                ))
    
    def on_family_select(self, event):
        # When a family is selected in the treeview, populate the fields
        selected_item = self.family_tree.selection()
        if selected_item:
            values = self.family_tree.item(selected_item, "values")
            self.family_id.delete(0, tk.END)
            self.family_id.insert(0, values[0])
            self.family_name.delete(0, tk.END)
            self.family_name.insert(0, values[1])
            self.head_of_family.delete(0, tk.END)
            self.head_of_family.insert(0, values[2])
            self.contact_number.delete(0, tk.END)
            self.contact_number.insert(0, values[3])
    
    def clear_family_fields(self):
        self.family_id.delete(0, tk.END)
        self.family_name.delete(0, tk.END)
        self.head_of_family.delete(0, tk.END)
        self.contact_number.delete(0, tk.END)
    
    def clear_member_fields(self):
        self.member_name.delete(0, tk.END)
        self.relationship.set('')
    
    def clear_offering_fields(self):
        self.offering_type.set('')
        self.offering_family_id.set('')
        self.amount.delete(0, tk.END)

# Run the application
if __name__ == "__main__":
    root = tk.Tk()
    app = ChurchOfferingSystem(root)
    root.mainloop()