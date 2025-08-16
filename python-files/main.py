# main.py
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import pandas as pd
import os
import openpyxl
from openpyxl.styles import Font, PatternFill
from datetime import datetime
import tempfile
import os
from reportlab.lib.pagesizes import landscape, A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle, SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

import db
import gst_report
from advanced_reports import AdvancedReports
from reports_page import ReportsPage

db.init_db()

# ---------- Helpers ----------
def refresh_tree(rows):
    for r in tree.get_children():
        tree.delete(r)
    for gstin, name, email, mobile, assigned_to, type_val, constitution in rows:
        tree.insert("", "end", values=(gstin, name, email, mobile, assigned_to, type_val, constitution))

# ---------- Pagination State ----------
PAGE_SIZE = 50
current_page = 0
current_search = ""
current_total = 0

def goto_prev_page():
    if current_page > 0:
        if current_search:
            do_search(page=current_page-1)
        else:
            load_all_taxpayers(page=current_page-1)

def goto_next_page():
    total_pages = (current_total + PAGE_SIZE - 1) // PAGE_SIZE
    if current_page+1 < total_pages:
        if current_search:
            do_search(page=current_page+1)
        else:
            load_all_taxpayers(page=current_page+1)

def update_pagination_label():
    global pagination_label, taxpayer_count_label
    if pagination_label:
        total_pages = (current_total + PAGE_SIZE - 1) // PAGE_SIZE
        pagination_label.config(text=f"Page {current_page+1} of {max(total_pages,1)}")
    
    if taxpayer_count_label:
        start_count = current_page * PAGE_SIZE + 1
        end_count = min((current_page + 1) * PAGE_SIZE, current_total)
        if current_total == 0:
            taxpayer_count_label.config(text="No taxpayers found")
        else:
            taxpayer_count_label.config(text=f"Showing {start_count}-{end_count} of {current_total} taxpayers")

def load_all_taxpayers(page=0):
    global current_page, current_search, current_total
    current_page = page
    current_search = ""
    with db.get_conn() as conn:
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM taxpayers")
        current_total = cur.fetchone()[0]
    rows = db.list_taxpayers(limit=PAGE_SIZE, offset=PAGE_SIZE*current_page)
    refresh_tree(rows)
    update_pagination_label()

def do_search(*args, page=0):
    global current_page, current_search, current_total
    q = search_var.get().strip()
    if not q:
        load_all_taxpayers(0)
        return
    current_page = page
    current_search = q
    with db.get_conn() as conn:
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM taxpayers WHERE gstin LIKE ? OR name LIKE ?", (f"%{q}%", f"%{q}%"))
        current_total = cur.fetchone()[0]
    rows = db.search_taxpayers(q, limit=PAGE_SIZE, offset=PAGE_SIZE*current_page)
    refresh_tree(rows)
    update_pagination_label()

def get_selected_gstins():
    sels = tree.selection()
    gstins = []
    for item in sels:
        vals = tree.item(item, "values")
        if vals:
            gstins.append(vals[0])
    return gstins

def select_all_toggle():
    if select_all_var.get():
        # Select all
        items = tree.get_children()
        tree.selection_set(items)
    else:
        tree.selection_remove(tree.selection())

# ---------- Actions ----------
def upload_taxpayers_excel():
    path = filedialog.askopenfilename(title="Select Taxpayers Excel", filetypes=[("Excel files","*.xlsx *.xls")])
    if not path:
        return
    try:
        df = pd.read_excel(path)
        # Store the original order of GSTINs from the uploaded file
        uploaded_gstins = df['GSTIN'].tolist()
        
        db.upsert_taxpayers_from_df(df)
        
        # Load taxpayers in the same sequence as uploaded
        rows = db.list_taxpayers_by_gstin_order(uploaded_gstins)
        refresh_tree(rows)
        load_all_taxpayers(0)
        
        messagebox.showinfo("Success", "Taxpayers uploaded/updated successfully.")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to upload taxpayers:\n{e}")

def upload_returns_excel():
    gstins = get_selected_gstins()
    if len(gstins) != 1:
        messagebox.showwarning("Select one taxpayer", "Please select exactly one taxpayer for uploading returns.")
        return
    gstin = gstins[0]

    # Create a dialog for financial year selection
    fy_dialog = tk.Toplevel(root)
    fy_dialog.title("Select Financial Year")
    fy_dialog.geometry("300x150")  # Normal sized dialog
    fy_dialog.transient(root)
    fy_dialog.grab_set()
    
    # Center the dialog on screen
    def center_fy_dialog():
        fy_dialog.update_idletasks()
        screen_width = fy_dialog.winfo_screenwidth()
        screen_height = fy_dialog.winfo_screenheight()
        window_width = 300
        window_height = 150
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        fy_dialog.geometry(f"{window_width}x{window_height}+{x}+{y}")
    
    fy_dialog.after(100, center_fy_dialog)
    
    tk.Label(fy_dialog, text="Select Financial Year for Upload:", font=("Segoe UI", 10, "bold")).pack(pady=10)
    
    fy_var = tk.StringVar()
    fy_options = ['2024-25', '2025-26', '2026-27', '2027-28']
    fy_combo = ttk.Combobox(fy_dialog, textvariable=fy_var, values=fy_options, state="readonly", width=15)
    fy_combo.pack(pady=10)
    fy_combo.set(fy_options[0])  # Default to first option
    
    def proceed_with_upload():
        selected_fy = fy_var.get()
        if not selected_fy:
            messagebox.showwarning("Select FY", "Please select a financial year.")
            return
        
        fy_dialog.destroy()
        
        path = filedialog.askopenfilename(title="Select GST Returns Excel", filetypes=[("Excel files","*.xlsx *.xls")])
        if not path:
            return
        
        try:
            # Read the raw Excel file (no headers) and let the database function handle the processing
            raw = pd.read_excel(path, header=None)
            db.insert_or_replace_returns_from_df_with_fy(gstin, selected_fy, raw)
            messagebox.showinfo("Success", f"Returns uploaded for {gstin} for FY {selected_fy}.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to upload returns:\n{e}")
    
    def cancel_upload():
        fy_dialog.destroy()
    
    button_frame = tk.Frame(fy_dialog)
    button_frame.pack(pady=20)
    
    tk.Button(button_frame, text="Proceed", command=proceed_with_upload, bg="#4CAF50", fg="white", padx=20).pack(side="left", padx=5)
    tk.Button(button_frame, text="Cancel", command=cancel_upload, bg="#f44336", fg="white", padx=20).pack(side="left", padx=5)

def generate_gstr1_non_filers():
    """Generate GSTR-1 Non Filers report by matching GSTINs from uploaded Excel with taxpayer list"""
    # Ask user to browse Excel file
    path = filedialog.askopenfilename(
        title="Select Non-Filers Excel File", 
        filetypes=[("Excel files","*.xlsx *.xls")],
        initialfile="GST-Prime M3.3 MIS On Non-Filers.xlsx"
    )
    if not path:
        return
    
    try:
        # Read the non-filers Excel file (headers are in row 2)
        non_filers_df = pd.read_excel(path, header=2)
        
        # Clean up column names and data
        non_filers_df.columns = ['SNo', 'Unnamed1', 'GSTIN', 'Trade Name', 'Office', 'Jurisdiction']
        
        # Remove rows where GSTIN is NaN or empty
        non_filers_df = non_filers_df.dropna(subset=['GSTIN'])
        non_filers_df = non_filers_df[non_filers_df['GSTIN'].astype(str).str.strip() != '']
        
        # Get list of non-filer GSTINs
        non_filer_gstins = non_filers_df['GSTIN'].astype(str).str.strip().tolist()
        
        # Get all taxpayers from database with full details including address
        all_taxpayers = db.list_taxpayers_with_address()
        
        # Create result DataFrame - ONLY for non-filers
        result_data = []
        for taxpayer in all_taxpayers:
            gstin, name, address, email, mobile, assigned_to, type_val, constitution = taxpayer
            
            # Only include taxpayers who are in the non-filers list
            if gstin in non_filer_gstins:
                result_data.append({
                    'GSTIN': gstin,
                    'Taxpayer Name': name,
                    'Email': email or '',
                    'Mobile': mobile or '',
                    'Address': address or '',
                    'GSTR-1 Status': 'Not Filed'
                })
        
        # Create result DataFrame - only non-filers
        result_df = pd.DataFrame(result_data)
        
        # Save to Excel
        save_path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel Workbook", "*.xlsx")],
            title="Save GSTR-1 Non Filers Report",
            initialfile=f"GSTR-1/3B_Non_Filers_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        )
        
        if not save_path:
            return
        
        # Export to Excel with formatting
        with pd.ExcelWriter(save_path, engine='openpyxl') as writer:
            result_df.to_excel(writer, sheet_name='GSTR-1 Status Report', index=False)
            
            # Get the workbook and worksheet
            workbook = writer.book
            worksheet = writer.sheets['GSTR-1 Status Report']
            
            # Auto-adjust column widths
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = min(max_length + 2, 50)
                worksheet.column_dimensions[column_letter].width = adjusted_width
            
            # Format headers
            for col_num in range(1, len(result_df.columns) + 1):
                cell = worksheet.cell(row=1, column=col_num)
                cell.font = Font(bold=True)
                cell.fill = PatternFill(start_color="E3F2FD", end_color="E3F2FD", fill_type="solid")
            
            # Format all rows as non-filers (since we only show non-filers now)
            for row_num in range(2, len(result_df) + 2):  # +2 because Excel is 1-indexed and we have header
                # Highlight the entire row to indicate non-filer status
                    for col_num in range(1, len(result_df.columns) + 1):
                        cell = worksheet.cell(row=row_num, column=col_num)
                        cell.fill = PatternFill(start_color="FFCDD2", end_color="FFCDD2", fill_type="solid")
        
        # Show success message with summary - only non-filers
        non_filers_count = len(result_df)
        
        messagebox.showinfo(
            "Success", 
            f"GSTR-1 Non Filers Report generated successfully!\n\n"
            f"Non Filers Found: {non_filers_count}\n\n"
            f"File saved to:\n{save_path}\n\n"
            f"Note: Only taxpayers with 'Not Filed' status are included in this report."
        )
        
        # Open the file
        try:
            os.startfile(save_path)
        except Exception:
            pass
            
    except Exception as e:
        messagebox.showerror("Error", f"Failed to generate GSTR-1 Non Filers report:\n{e}")

def export_returns_to_excel(df_view, taxpayer_name="", gstin="", financial_year=""):
    """Export the current returns data to Excel with only UI columns"""
    if df_view.empty:
        messagebox.showwarning("No Data", "No data to export.")
        return
    
    # Create filename with taxpayer details
    filename = f"Return Data_{taxpayer_name}_{gstin}"
    if financial_year:
        filename += f"_{financial_year}"
    filename += ".xlsx"
    
    save_path = filedialog.asksaveasfilename(
        defaultextension=".xlsx",
        filetypes=[("Excel Workbook", "*.xlsx")],
        title="Export Returns Data",
        initialfile=filename
    )
    
    if not save_path:
        return
    
    try:
        # Create export DataFrame with only the columns shown in UI
        export_df = df_view.copy()
        
        # Select only the columns that are displayed in the UI
        ui_columns = {
            'return_period': 'Return Period',
            'date_of_filing': 'Date Of Filing',
            'total_turnover': 'Total Turnover',
            'taxable_value': 'Taxable Value',
            'gst_total': 'GST Total',
            'gst_itc': 'GST ITC',
            'sgst_cash_paid': 'SGST Cash Paid',
            'sgst_receivable_after_settlement': 'SGST Receivable After Settlement',
            'net_sgst': 'Net SGST',
            'total_gst_paid': 'Total GST Paid'
        }
        
        # Filter DataFrame to only include UI columns
        available_columns = [col for col in ui_columns.keys() if col in export_df.columns]
        export_df = export_df[available_columns].copy()
        
        # Rename columns to UI display names
        export_df = export_df.rename(columns=ui_columns)
        
        # Add totals row
        numeric_cols = ['Total Turnover', 'Taxable Value', 'GST Total', 'GST ITC', 
                       'SGST Cash Paid', 'SGST Receivable After Settlement', 'Net SGST', 'Total GST Paid']
        
        totals_row = {}
        for col in export_df.columns:
            if col in numeric_cols:
                # Convert to numeric for calculation
                values = pd.to_numeric(export_df[col], errors='coerce')
                total = values.sum()
                totals_row[col] = total if not pd.isna(total) else 0
            else:
                totals_row[col] = ""
        
        totals_row['Return Period'] = "TOTAL"
        totals_row['Date Of Filing'] = f"{len(export_df)} periods"
        
        # Create totals DataFrame and concatenate
        totals_df = pd.DataFrame([totals_row])
        export_df = pd.concat([export_df, totals_df], ignore_index=True)
        
        # Export to Excel
        with pd.ExcelWriter(save_path, engine='openpyxl') as writer:
            export_df.to_excel(writer, sheet_name='GST Returns', index=False)
            
            # Get the workbook and worksheet
            workbook = writer.book
            worksheet = writer.sheets['GST Returns']
            
            # Auto-adjust column widths
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = min(max_length + 2, 50)
                worksheet.column_dimensions[column_letter].width = adjusted_width
            
            # Format the totals row (last row)
            last_row = len(export_df) + 1  # +1 because Excel is 1-indexed
            for col_num in range(1, len(export_df.columns) + 1):
                cell = worksheet.cell(row=last_row, column=col_num)
                cell.font = Font(bold=True)
                cell.fill = PatternFill(start_color="E3F2FD", end_color="E3F2FD", fill_type="solid")
        
        messagebox.showinfo("Success", f"Data exported successfully to:\n{save_path}")
        
        # Open the file
        try:
            os.startfile(save_path)
        except Exception:
            pass
            
    except Exception as e:
        messagebox.showerror("Error", f"Failed to export data:\n{e}")

def view_details():
    """View detailed returns for selected taxpayer"""
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("No Selection", "Please select a taxpayer first.")
        return
    
    gstin = tree.item(selected[0])['values'][0]  # GSTIN is in column 0
    taxpayer_name = tree.item(selected[0])['values'][1]  # Name is in column 1
    
    # Get all returns data for this taxpayer
    returns_data = db.get_returns_df(gstin)
    
    if returns_data.empty:
        messagebox.showinfo("No Data", f"No returns data found for {taxpayer_name}")
        return
    
    # Show all records by default (no FY selection dialog)
    show_details_window(gstin, taxpayer_name, returns_data)

def show_details_window(gstin, taxpayer_name, returns_data):
    """Show the details window with all records"""
    top = tk.Toplevel(root)
    top.title(f"GST Returns Details - {taxpayer_name}")
    top.state('zoomed')  # Full screen
    
    # Create main frame
    main_frame = tk.Frame(top)
    main_frame.pack(fill="both", expand=True, padx=20, pady=20)
    
    # Header
    header_frame = tk.Frame(main_frame)
    header_frame.pack(fill="x", pady=(0, 20))
    
    tk.Label(header_frame, text=f"GST Returns Details", font=("Segoe UI", 16, "bold")).pack()
    tk.Label(header_frame, text=f"Taxpayer: {taxpayer_name}", font=("Segoe UI", 12)).pack()
    tk.Label(header_frame, text=f"GSTIN: {gstin}", font=("Segoe UI", 12)).pack()
    
    # Add filters frame
    filters_frame = tk.Frame(header_frame)
    filters_frame.pack(pady=10)
    
    # Financial Year filter
    tk.Label(filters_frame, text="Financial Year:", font=("Segoe UI", 10, "bold")).pack(side="left", padx=(0, 5))
    fy_var = tk.StringVar(value="All")
    fy_combo = ttk.Combobox(filters_frame, textvariable=fy_var, values=["All"] + sorted(returns_data['financial_year'].unique().tolist()), 
                            state="readonly", width=10)
    fy_combo.pack(side="left", padx=(0, 15))
    
    # Month filter
    tk.Label(filters_frame, text="Month:", font=("Segoe UI", 10, "bold")).pack(side="left", padx=(0, 5))
    month_var = tk.StringVar(value="All")
    month_combo = ttk.Combobox(filters_frame, textvariable=month_var, values=["All"] + sorted(returns_data['return_period'].unique().tolist()), 
                               state="readonly", width=10)
    month_combo.pack(side="left", padx=(0, 15))
    
    # Filter button
    def apply_filters():
        # Get selected filters
        selected_fy = fy_var.get()
        selected_month = month_var.get()
        
        # Filter the data
        filtered_data = returns_data.copy()
        
        if selected_fy != "All":
            filtered_data = filtered_data[filtered_data['financial_year'] == selected_fy]
        
        if selected_month != "All":
            filtered_data = filtered_data[filtered_data['return_period'] == selected_month]
        
        # Clear existing data
        for item in tree.get_children():
            tree.delete(item)
        
        # Insert filtered data
        for _, row in filtered_data.iterrows():
            tree.insert("", "end", values=(
                row['return_period'],
                row['date_of_filing'],
                f"{row['total_turnover']:,.2f}" if pd.notna(row['total_turnover']) else "",
                f"{row['taxable_value']:,.2f}" if pd.notna(row['taxable_value']) else "",
                f"{row['gst_total']:,.2f}" if pd.notna(row['gst_total']) else "",
                f"{row['gst_itc']:,.2f}" if pd.notna(row['gst_itc']) else "",
                f"{row['sgst_cash_paid']:,.2f}" if pd.notna(row['sgst_cash_paid']) else "",
                f"{row['sgst_receivable_after_settlement']:,.2f}" if pd.notna(row['sgst_receivable_after_settlement']) else "",
                f"{row['net_sgst']:,.2f}" if pd.notna(row['net_sgst']) else "",
                f"{row['total_gst_paid']:,.2f}" if pd.notna(row['total_gst_paid']) else "",
                row['financial_year']
            ))
        
        # Update record count
        record_count_label.config(text=f"Showing {len(filtered_data)} of {len(returns_data)} records")
    
    filter_btn = tk.Button(filters_frame, text="Apply Filters", command=apply_filters, 
                           bg="#2196F3", fg="white", font=("Segoe UI", 10, "bold"))
    filter_btn.pack(side="left", padx=(0, 15))
    
    # Clear filters button
    def clear_filters():
        fy_var.set("All")
        month_var.set("All")
        apply_filters()
    
    clear_btn = tk.Button(filters_frame, text="Clear Filters", command=clear_filters, 
                          bg="#FF9800", fg="white", font=("Segoe UI", 10, "bold"))
    clear_btn.pack(side="left")
    
    # Record count label
    record_count_label = tk.Label(header_frame, text=f"Showing {len(returns_data)} records", 
                                 font=("Segoe UI", 10), fg="gray")
    record_count_label.pack(pady=(5, 0))
    
    # Add Delete button
    def delete_all_returns():
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete ALL return data for {taxpayer_name}?\n\nThis action cannot be undone."):
            db.delete_all_returns_for_taxpayer(gstin)
            messagebox.showinfo("Success", f"All return data for {taxpayer_name} has been deleted.")
            top.destroy()
    
    delete_btn = tk.Button(header_frame, text="Delete All Returns", command=delete_all_returns, 
                          bg="#f44336", fg="white", font=("Segoe UI", 10, "bold"))
    delete_btn.pack(pady=10)
    
    # Add Delete Single button
    def delete_single_fy_returns():
        # Get the currently selected FY from the main interface
        selected_fy = fy_var.get()
        
        # Check if a specific FY is selected
        if selected_fy == "All":
            messagebox.showwarning("Select FY", "Please select a specific Financial Year from the dropdown above before deleting.")
            return
        
        # Check if the selected FY has data
        fy_data = returns_data[returns_data['financial_year'] == selected_fy]
        if len(fy_data) == 0:
            messagebox.showinfo("No Data", f"No return data found for Financial Year {selected_fy}.")
            return
        
        # Show confirmation dialog
        confirm_message = f"""Are you sure you want to delete ALL return data for:

Taxpayer: {taxpayer_name}
GSTIN: {gstin}
Financial Year: {selected_fy}

⚠️ This action will permanently delete {len(fy_data)} records and cannot be undone."""
        
        if messagebox.askyesno("Confirm Delete", confirm_message):
            # Delete the returns for selected FY
            deleted_count = db.delete_returns_for_taxpayer_and_fy(gstin, selected_fy)
            messagebox.showinfo("Success", f"Successfully deleted {deleted_count} return records for {taxpayer_name} (FY: {selected_fy})")
            top.destroy()
    
    delete_single_btn = tk.Button(header_frame, text="Delete Single FY Returns", command=delete_single_fy_returns, 
                                 bg="#FF9800", fg="white", font=("Segoe UI", 10, "bold"))
    delete_single_btn.pack(pady=5)
    
    # Create Treeview for returns data
    tree_frame = tk.Frame(main_frame)
    tree_frame.pack(fill="both", expand=True)
    
    # Create Treeview with scrollbars
    tree = ttk.Treeview(tree_frame, columns=("Return Period", "Date of Filing", "Total Turnover", 
                                            "Taxable Value", "GST Total", "GST ITC", "SGST Cash Paid",
                                            "SGST Receivable", "Net SGST", "Total GST Paid", "Financial Year"), 
                        show="headings", height=20)
    
    # Configure columns
    tree.heading("Return Period", text="Return Period")
    tree.heading("Date of Filing", text="Date of Filing")
    tree.heading("Total Turnover", text="Total Turnover")
    tree.heading("Taxable Value", text="Taxable Value")
    tree.heading("GST Total", text="GST Total")
    tree.heading("GST ITC", text="GST ITC")
    tree.heading("SGST Cash Paid", text="SGST Cash Paid")
    tree.heading("SGST Receivable", text="SGST Receivable")
    tree.heading("Net SGST", text="Net SGST")
    tree.heading("Total GST Paid", text="Total GST Paid")
    tree.heading("Financial Year", text="Financial Year")
    
    # Set column widths
    tree.column("Return Period", width=120)
    tree.column("Date of Filing", width=120)
    tree.column("Total Turnover", width=120)
    tree.column("Taxable Value", width=120)
    tree.column("GST Total", width=100)
    tree.column("GST ITC", width=100)
    tree.column("SGST Cash Paid", width=120)
    tree.column("SGST Receivable", width=140)
    tree.column("Net SGST", width=100)
    tree.column("Total GST Paid", width=120)
    tree.column("Financial Year", width=100)
    
    # Add scrollbars
    vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
    hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=tree.xview)
    tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
    
    # Pack tree and scrollbars
    tree.pack(side="left", fill="both", expand=True)
    vsb.pack(side="right", fill="y")
    hsb.pack(side="bottom", fill="x")
    
    # Insert data
    for _, row in returns_data.iterrows():
        tree.insert("", "end", values=(
            row['return_period'],
            row['date_of_filing'],
            f"{row['total_turnover']:,.2f}" if pd.notna(row['total_turnover']) else "",
            f"{row['taxable_value']:,.2f}" if pd.notna(row['taxable_value']) else "",
            f"{row['gst_total']:,.2f}" if pd.notna(row['gst_total']) else "",
            f"{row['gst_itc']:,.2f}" if pd.notna(row['gst_itc']) else "",
            f"{row['sgst_cash_paid']:,.2f}" if pd.notna(row['sgst_cash_paid']) else "",
            f"{row['sgst_receivable_after_settlement']:,.2f}" if pd.notna(row['sgst_receivable_after_settlement']) else "",
            f"{row['net_sgst']:,.2f}" if pd.notna(row['net_sgst']) else "",
            f"{row['total_gst_paid']:,.2f}" if pd.notna(row['total_gst_paid']) else "",
            row['financial_year']
        ))
    
    # Close button
    close_btn = tk.Button(main_frame, text="Close", command=top.destroy, 
                         bg="#2196F3", fg="white", font=("Segoe UI", 12, "bold"), padx=30)
    close_btn.pack(pady=20)

def delete_taxpayers():
    """Delete selected taxpayers and their related returns data"""
    gstins = get_selected_gstins()
    if not gstins:
        messagebox.showwarning("No selection", "Please select at least one taxpayer to delete.")
        return
    
    # Create confirmation message
    if len(gstins) == 1:
        message = "Are you sure you want to delete this taxpayer?\n\nThis will permanently delete:\n• The taxpayer record\n• All related GST returns data\n\nThis action cannot be undone!"
        title = "Confirm Deletion"
    else:
        message = f"Are you sure you want to delete {len(gstins)} taxpayers?\n\nThis will permanently delete:\n• All selected taxpayer records\n• All related GST returns data\n\nThis action cannot be undone!"
        title = "Confirm Bulk Deletion"
    
    # Show confirmation dialog
    result = messagebox.askyesno(title, message, icon='warning')
    if not result:
        return
    
    try:
        # Delete taxpayers and their returns
        deleted_count = db.delete_taxpayers_and_returns(gstins)
        
        # Show success message
        if len(gstins) == 1:
            messagebox.showinfo("Success", f"Taxpayer deleted successfully!\n\nDeleted: {deleted_count} taxpayer and all related returns data.")
        else:
            messagebox.showinfo("Success", f"Taxpayers deleted successfully!\n\nDeleted: {deleted_count} taxpayers and all related returns data.")
        
        # Refresh the taxpayer list
        load_all_taxpayers(0)
        
    except Exception as e:
        messagebox.showerror("Error", f"Failed to delete taxpayers:\n{e}")

def generate_report():
    """Generate Excel report for selected taxpayers"""
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("No Selection", "Please select at least one taxpayer first.")
        return
    
    gstins = [tree.item(item)['values'][0] for item in selected]  # GSTIN is in column 0
    
    # Check if multiple FYs exist for selected taxpayers
    all_fys = set()
    for gstin in gstins:
        returns_data = db.get_returns_df(gstin)
        if not returns_data.empty and 'financial_year' in returns_data.columns:
            # Filter out None, NaN, and empty string values
            valid_fys = [fy for fy in returns_data['financial_year'].dropna().unique() if fy and str(fy).strip()]
            all_fys.update(valid_fys)
    
    if len(all_fys) > 1:
        # Multiple FYs exist, show selection dialog
        show_fy_selection_dialog(gstins, all_fys, "generate")
    else:
        # Single FY or no FY data, proceed with default
        if all_fys:
            selected_fy = list(all_fys)[0]
            generate_report_for_fy(gstins, [selected_fy])
        else:
            generate_report_for_fy(gstins, [])

def show_fy_selection_dialog(gstins, available_fys, action_type):
    """Show dialog for selecting multiple financial years"""
    dialog = tk.Toplevel(root)
    dialog.title("Select Financial Years")
    dialog.geometry("400x300")
    dialog.transient(root)
    dialog.grab_set()
    
    # Center the dialog
    dialog.update_idletasks()
    x = (dialog.winfo_screenwidth() // 2) - (400 // 2)
    y = (dialog.winfo_screenheight() // 2) - (300 // 2)
    dialog.geometry(f"400x300+{x}+{y}")
    
    main_frame = tk.Frame(dialog)
    main_frame.pack(fill="both", expand=True, padx=20, pady=20)
    
    tk.Label(main_frame, text="Select Financial Years:", font=("Segoe UI", 12, "bold")).pack(pady=(0, 10))
    
    # Create checkboxes for each FY
    fy_vars = {}
    for fy in sorted(available_fys):
        var = tk.BooleanVar(value=True)  # Default to selected
        fy_vars[fy] = var
        tk.Checkbutton(main_frame, text=fy, variable=var, font=("Segoe UI", 10)).pack(anchor="w")
    
    # Buttons
    button_frame = tk.Frame(main_frame)
    button_frame.pack(fill="x", pady=(20, 0))
    
    def proceed():
        selected_fys = [fy for fy, var in fy_vars.items() if var.get()]
        if not selected_fys:
            messagebox.showwarning("No Selection", "Please select at least one financial year.")
            return
        
        dialog.destroy()
        
        if action_type == "generate":
            generate_report_for_fy(gstins, selected_fys)
        elif action_type == "view":
            proceed_with_summary(gstins, selected_fys)
    
    def cancel():
        dialog.destroy()
    
    tk.Button(button_frame, text="Proceed", command=proceed, bg="#4CAF50", fg="white", 
              font=("Segoe UI", 10, "bold")).pack(side="left", padx=(0, 10))
    tk.Button(button_frame, text="Cancel", command=cancel, bg="#f44336", fg="white", 
              font=("Segoe UI", 10, "bold")).pack(side="left")

def generate_report_for_fy(gstins, selected_fys):
    """Generate report for specific financial years"""
    # Ensure selected_fys is always a list
    if selected_fys is None:
        selected_fys = []
    elif isinstance(selected_fys, str):
        selected_fys = [selected_fys]
    elif not isinstance(selected_fys, (list, tuple)):
        selected_fys = [str(selected_fys)]
    
    if len(gstins) == 1:
        # Single taxpayer
        gstin = gstins[0]
        taxpayer_name = tree.item(tree.selection()[0])['values'][1]
        
        if len(selected_fys) == 1:
            filename = f"{taxpayer_name}_{gstin}_{selected_fys[0]}.xlsx"
        else:
            filename = f"{taxpayer_name}_{gstin}_MultiFY.xlsx"
        
        filepath = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx")],
            initialfile=filename
        )
        
        if filepath:
            try:
                gst_report.export_single_taxpayer_3sheets(gstin, filepath, selected_fys)
                messagebox.showinfo("Success", f"Report generated successfully!\nSaved as: {filepath}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to generate report: {str(e)}")
    else:
        # Multiple taxpayers
        if len(selected_fys) == 1:
            filename = f"Return Summary_{selected_fys[0]}.xlsx"
        else:
            filename = "Return Summary_MultiFY.xlsx"
        
        filepath = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx")],
            initialfile=filename
        )
        
        if filepath:
            try:
                gst_report.export_multi_taxpayer_combined_sheets(gstins, filepath, selected_fys)
                messagebox.showinfo("Success", f"Report generated successfully!\nSaved as: {filepath}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to generate report: {str(e)}")

def view_summary():
    """View summary for selected taxpayers"""
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("No Selection", "Please select at least one taxpayer first.")
        return
    
    gstins = [tree.item(item)['values'][0] for item in selected]  # GSTIN is in column 0
    
    # Check if multiple FYs exist for selected taxpayers
    all_fys = set()
    for gstin in gstins:
        returns_data = db.get_returns_df(gstin)
        if not returns_data.empty and 'financial_year' in returns_data.columns:
            # Filter out None, NaN, and empty string values
            valid_fys = [fy for fy in returns_data['financial_year'].dropna().unique() if fy and str(fy).strip()]
            all_fys.update(valid_fys)
    
    if len(all_fys) > 1:
        # Multiple FYs exist, show selection dialog
        show_fy_selection_dialog(gstins, all_fys, "view")
    else:
        # Single FY or no FY data, proceed with default
        if all_fys:
            selected_fy = list(all_fys)[0]
            proceed_with_summary(gstins, [selected_fy])
        else:
            proceed_with_summary(gstins, [])

def proceed_with_summary(gstins, selected_fys):
    """Proceed with summary display for specific financial years"""
    # Ensure selected_fys is always a list
    if selected_fys is None:
        selected_fys = []
    elif isinstance(selected_fys, str):
        selected_fys = [selected_fys]
    elif not isinstance(selected_fys, (list, tuple)):
        selected_fys = [str(selected_fys)]
    
    # Handle case where selected_fys is empty
    if not selected_fys:
        messagebox.showinfo("No Data", "No financial year data available for selected taxpayers.")
        return
    
    if len(gstins) == 1:
        # Single taxpayer
        gstin = gstins[0]
        taxpayer_name = tree.item(tree.selection()[0])['values'][1]
        
        if len(selected_fys) == 1:
            title = f"GST Returns Summary - {taxpayer_name} ({selected_fys[0]})"
        else:
            title = f"GST Returns Summary - {taxpayer_name} (Multiple FYs)"
        
        # Filter data by selected FYs
        returns_data = db.get_returns_df(gstin)
        if not returns_data.empty:
            # Ensure financial_year column exists and has valid data
            if 'financial_year' in returns_data.columns and not returns_data['financial_year'].isna().all():
                try:
                    # Debug: Print the types and values
                    print(f"Debug - selected_fys type: {type(selected_fys)}, value: {selected_fys}")
                    print(f"Debug - returns_data['financial_year'] type: {type(returns_data['financial_year'])}")
                    print(f"Debug - returns_data['financial_year'].head(): {returns_data['financial_year'].head()}")
                    
                    filtered_data = returns_data[returns_data['financial_year'].isin(selected_fys)]
                    if not filtered_data.empty:
                        show_summary_window(gstins, filtered_data, title)
                    else:
                        messagebox.showinfo("No Data", f"No returns data found for {taxpayer_name} in selected financial years")
                except Exception as e:
                    messagebox.showerror("Error", f"Error filtering data: {str(e)}\n\nDebug info:\nselected_fys: {selected_fys}\nType: {type(selected_fys)}")
            else:
                messagebox.showinfo("No Data", f"No valid financial year data found for {taxpayer_name}")
        else:
            messagebox.showinfo("No Data", f"No returns data found for {taxpayer_name}")
    else:
        # Multiple taxpayers
        if len(selected_fys) == 1:
            title = f"GST Returns Summary - Multiple Taxpayers ({selected_fys[0]})"
        else:
            title = "GST Returns Summary - Multiple Taxpayers (Multiple FYs)"
        
        # Collect and filter data for all selected taxpayers and FYs
        all_data = []
        for gstin in gstins:
            returns_data = db.get_returns_df(gstin)
            if not returns_data.empty:
                # Ensure financial_year column exists and has valid data
                if 'financial_year' in returns_data.columns and not returns_data['financial_year'].isna().all():
                    try:
                        filtered_data = returns_data[returns_data['financial_year'].isin(selected_fys)]
                        if not filtered_data.empty:
                            all_data.append(filtered_data)
                    except Exception as e:
                        messagebox.showerror("Error", f"Error filtering data for {gstin}: {str(e)}\n\nDebug info:\nselected_fys: {selected_fys}\nType: {type(selected_fys)}")
                        return
                else:
                    print(f"Debug - No valid financial_year data for {gstin}")
        
        if all_data:
            combined_data = pd.concat(all_data, ignore_index=True)
            show_summary_window(gstins, combined_data, title)
        else:
            messagebox.showinfo("No Data", "No returns data found for selected taxpayers and financial years")

def show_summary_window(gstins, returns_data, title):
    """Show summary window with returns data"""
    win = tk.Toplevel(root)
    win.title(title)
    win.state('zoomed')  # Full screen
    win.transient(root)
    win.grab_set()
    
    frame = tk.Frame(win)
    frame.pack(fill="both", expand=True, padx=10, pady=10)
    
    # Header
    tk.Label(frame, text=title, font=("Segoe UI", 16, "bold")).pack(pady=(0, 20))
    
    # Add export buttons at the top
    btn_frame = tk.Frame(frame, relief="raised", bd=2, bg="#f0f0f0")
    btn_frame.pack(pady=(0, 20), padx=20, fill="x")
    
    # Add a label above the buttons
    tk.Label(btn_frame, text="Export Options", font=("Segoe UI", 12, "bold"), 
             bg="#f0f0f0", fg="#333333").pack(pady=(10, 15))
    
    # Ensure the button frame has minimum height
    btn_frame.configure(height=80)
    
    # Download PDF button
    def download_pdf():
        if len(gstins) == 1:
            # Single taxpayer
            gstin = gstins[0]
            taxpayer_name = tree.item(tree.selection()[0])['values'][1]
            if len(returns_data['financial_year'].unique()) == 1:
                filename = f"{taxpayer_name}_{gstin}_{returns_data['financial_year'].iloc[0]}.pdf"
            else:
                filename = f"{taxpayer_name}_{gstin}_MultiFY.pdf"
        else:
            # Multiple taxpayers
            if len(returns_data['financial_year'].unique()) == 1:
                filename = f"Return Summary_{returns_data['financial_year'].iloc[0]}.pdf"
            else:
                filename = "Return Summary_MultiFY.pdf"
        
        filepath = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")],
            initialfile=filename
        )
        
        if filepath:
            try:
                # Get the financial years from the filtered returns data
                selected_fys = list(returns_data['financial_year'].unique())
                
                if len(gstins) == 1:
                    gst_report.export_single_taxpayer_pdf(gstins[0], filepath, selected_fys)
                else:
                    gst_report.export_multi_taxpayer_pdf(gstins, filepath, selected_fys)
                messagebox.showinfo("Success", f"PDF downloaded successfully!\nSaved as: {filepath}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to download PDF: {str(e)}")
    
    # Create a sub-frame for button centering with proper sizing and spacing
    button_center_frame = tk.Frame(btn_frame, bg="#f0f0f0")
    button_center_frame.pack(expand=True, pady=10)
    
    # Create buttons with better styling and visibility - only PDF and Close
    pdf_btn = tk.Button(button_center_frame, text="📄 Download PDF", command=download_pdf, 
                        bg="#4CAF50", fg="white", font=("Segoe UI", 11, "bold"), 
                        padx=25, pady=8, relief="raised", bd=2, cursor="hand2", width=18)
    pdf_btn.pack(side="left", padx=20, pady=5)
    
    # Close button
    close_btn = tk.Button(button_center_frame, text="❌ Close", command=win.destroy, 
                          bg="#f44336", fg="white", font=("Segoe UI", 11, "bold"), 
                          padx=25, pady=8, relief="raised", bd=2, cursor="hand2", width=18)
    close_btn.pack(side="left", padx=20, pady=5)
    
    # Show returns data in a treeview
    tk.Label(frame, text="GST Returns Data", font=("Segoe UI", 12, "bold")).pack(anchor="w")
    
    # Create Treeview with scrollbars
    tree_frame = tk.Frame(frame)
    tree_frame.pack(fill="both", expand=True)
    
    summary_tree = ttk.Treeview(tree_frame, columns=list(returns_data.columns), show="headings", height=20)
    
    # Configure columns
    for col in returns_data.columns:
        summary_tree.heading(col, text=col)
        if col in ['Total Turnover', 'Taxable Value', 'GST Total', 'GST ITC', 'SGST Cash Paid', 
                   'SGST Receivable', 'Net SGST', 'Total GST Paid']:
            summary_tree.column(col, width=120, anchor="e")  # Right align numbers
        else:
            summary_tree.column(col, width=120, anchor="w")  # Left align text
    
    # Insert data
    for _, row in returns_data.iterrows():
        values = []
        for col in returns_data.columns:
            if col in ['Total Turnover', 'Taxable Value', 'GST Total', 'GST ITC', 'SGST Cash Paid', 
                       'SGST Receivable', 'Net SGST', 'Total GST Paid']:
                # Format numbers with commas
                if pd.notna(row[col]):
                    values.append(f"{row[col]:,.2f}")
                else:
                    values.append("")
            else:
                values.append(str(row[col]) if pd.notna(row[col]) else "")
        summary_tree.insert("", "end", values=values)
    
    # Add scrollbars
    vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=summary_tree.yview)
    hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=summary_tree.xview)
    summary_tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
    
    # Pack tree and scrollbars
    summary_tree.pack(side="left", fill="both", expand=True)
    vsb.pack(side="right", fill="y")
    hsb.pack(side="bottom", fill="x")
    
def show_reports_page():
    """Show the Reports Page with three different report types"""
    reports_win = tk.Toplevel(root)
    reports_win.title("📊 GST Reports Dashboard")
    reports_win.state('zoomed')  # Full screen
    reports_win.transient(root)
    reports_win.grab_set()
    
    # Configure window background
    reports_win.configure(bg="white")
    
    # Create main frame
    main_frame = tk.Frame(reports_win, bg="white")
    main_frame.pack(fill="both", expand=True, padx=20, pady=20)
    
    # FY Selection Frame
    fy_frame = tk.Frame(main_frame, bg="white")
    fy_frame.pack(pady=(0, 20), fill="x")
    
    # FY selection row
    fy_row = tk.Frame(fy_frame, bg="white")
    fy_row.pack(fill="x", pady=10)
    
    tk.Label(fy_row, text="Financial Year:", font=("Arial", 10)).pack(side="left", padx=(0, 10))
    
    # Get available FYs from database
    available_fys = set()
    with db.get_conn() as conn:
        cur = conn.cursor()
        cur.execute("SELECT DISTINCT financial_year FROM gst_returns WHERE financial_year IS NOT NULL")
        for row in cur.fetchall():
            if row[0]:
                available_fys.add(row[0])
    
    if not available_fys:
        available_fys = {'2024-25', '2025-26', '2026-27', '2027-28'}  # Default options
    
    fy_var = tk.StringVar()
    fy_combo = ttk.Combobox(fy_row, textvariable=fy_var, values=sorted(list(available_fys)), 
                             state="readonly", width=20, font=("Arial", 9))
    fy_combo.pack(side="left", padx=(0, 20))
    fy_combo.set(sorted(list(available_fys))[0] if available_fys else "2024-25")
    
    # Buttons Frame
    buttons_frame = tk.Frame(fy_frame, bg="white")
    buttons_frame.pack(fill="x", pady=10)
    
    def generate_all_reports():
        selected_fy = fy_var.get()
        if not selected_fy:
            messagebox.showwarning("Select FY", "Please select a financial year first.")
            return
        
        # Generate all three reports
        generate_turnover_report(selected_fy)
        generate_cash_only_report(selected_fy)
        generate_itc_only_report(selected_fy)
    
    def clear_reports():
        # Clear all treeviews
        for tree in [turnover_tree, cash_only_tree, itc_only_tree]:
            for item in tree.get_children():
                tree.delete(item)
    
    generate_btn = tk.Button(buttons_frame, text="Generate Reports", command=generate_all_reports,
                            bg="lightblue", fg="black", font=("Arial", 9), 
                            padx=15, pady=5)
    generate_btn.pack(side="left", padx=(0, 10))
    
    clear_btn = tk.Button(buttons_frame, text="Clear", command=clear_reports,
                          bg="lightcoral", fg="black", font=("Arial", 9), 
                          padx=15, pady=5)
    clear_btn.pack(side="left", padx=(0, 10))
    
    # Export buttons
    def export_turnover():
        if not turnover_tree.get_children():
            messagebox.showwarning("No Data", "Please generate the report first.")
            return
        export_report_to_excel(turnover_tree, f"Total_Turnover_Report_{fy_var.get()}")
    
    def export_cash_only():
        if not cash_only_tree.get_children():
            messagebox.showwarning("No Data", "Please generate the report first.")
            return
        export_report_to_excel(cash_only_tree, f"Cash_Only_Report_{fy_var.get()}")
    
    def export_itc_only():
        if not itc_only_tree.get_children():
            messagebox.showwarning("No Data", "Please generate the report first.")
            return
        export_report_to_excel(itc_only_tree, f"ITC_Only_Report_{fy_var.get()}")
    
    export_turnover_btn = tk.Button(buttons_frame, text="Export Turnover", command=export_turnover,
                                   bg="lightgreen", fg="black", font=("Arial", 9), 
                                   padx=10, pady=5)
    export_turnover_btn.pack(side="left", padx=(0, 5))
    
    export_cash_btn = tk.Button(buttons_frame, text="Export Cash", command=export_cash_only,
                               bg="lightyellow", fg="black", font=("Arial", 9), 
                               padx=10, pady=5)
    export_cash_btn.pack(side="left", padx=(0, 5))
    
    export_itc_btn = tk.Button(buttons_frame, text="Export ITC", command=export_itc_only,
                              bg="lightblue", fg="black", font=("Arial", 9), 
                              padx=10, pady=5)
    export_itc_btn.pack(side="left")
    
    # Create Notebook for tabs
    notebook = ttk.Notebook(main_frame)
    notebook.pack(fill="both", expand=True)
    
    # Basic treeview styling
    style = ttk.Style()
    style.configure("Treeview", 
                   background="white",
                   foreground="black",
                   rowheight=25,
                   font=("Arial", 9))
    
    style.configure("Treeview.Heading", 
                   background="lightgray",
                   foreground="black",
                   font=("Arial", 9, "bold"))
    
    # Tab 1: Total Turnover Report
    turnover_frame = tk.Frame(notebook, bg="white")
    notebook.add(turnover_frame, text="Total Turnover")
    
    # Tab header with icon
    turnover_header_frame = tk.Frame(turnover_frame, bg="#E3F2FD", height=60)
    turnover_header_frame.pack(fill="x", pady=(0, 20))
    
    tk.Label(turnover_header_frame, text="💰 Taxpayers List with Total Turnover", 
             font=("Segoe UI", 18, "bold"), bg="#E3F2FD", fg="#1565C0").pack(expand=True)
    
    # Table header label
    turnover_table_header = tk.Frame(turnover_frame, bg="#E3F2FD", height=40)
    turnover_table_header.pack(fill="x", pady=(0, 10))
    
    tk.Label(turnover_table_header, text="💰 Total Turnover Data Table", 
             font=("Segoe UI", 14, "bold"), bg="#E3F2FD", fg="#1565C0").pack(expand=True)
    
    # Turnover Treeview
    turnover_tree = ttk.Treeview(turnover_frame, columns=("GSTIN", "Taxpayer Name", "Total Turnover", "Total GST Paid", "Returns Count"), 
                                 show="headings", height=20)
    
    # Configure columns
    turnover_tree.heading("GSTIN", text="GSTIN")
    turnover_tree.heading("Taxpayer Name", text="Taxpayer Name")
    turnover_tree.heading("Total Turnover", text="Total Turnover")
    turnover_tree.heading("Total GST Paid", text="Total GST Paid")
    turnover_tree.heading("Returns Count", text="Returns Count")
    
    turnover_tree.column("GSTIN", width=200)
    turnover_tree.column("Taxpayer Name", width=250)
    turnover_tree.column("Total Turnover", width=150)
    turnover_tree.column("Total GST Paid", width=150)
    turnover_tree.column("Returns Count", width=100)
    
    # Add scrollbars
    turnover_vsb = ttk.Scrollbar(turnover_frame, orient="vertical", command=turnover_tree.yview)
    turnover_hsb = ttk.Scrollbar(turnover_frame, orient="horizontal", command=turnover_tree.xview)
    turnover_tree.configure(yscrollcommand=turnover_vsb.set, xscrollcommand=turnover_hsb.set)
    
    # Pack tree and scrollbars
    turnover_tree.pack(side="left", fill="both", expand=True)
    turnover_vsb.pack(side="right", fill="y")
    turnover_hsb.pack(side="bottom", fill="x")
    

    
    # Tab 2: Cash Only Report
    cash_only_frame = tk.Frame(notebook, bg="white")
    notebook.add(cash_only_frame, text="Cash Only")
    
    # Tab header with icon
    cash_header_frame = tk.Frame(cash_only_frame, bg="#FFF3E0", height=60)
    cash_header_frame.pack(fill="x", pady=(0, 20))
    
    tk.Label(cash_header_frame, text="💵 Taxpayers with Only SGST Cash Payment (No ITC)", 
             font=("Segoe UI", 18, "bold"), bg="#FFF3E0", fg="#E65100").pack(expand=True)
    
    # Table header label
    cash_table_header = tk.Frame(cash_only_frame, bg="#FFF3E0", height=40)
    cash_table_header.pack(fill="x", pady=(0, 10))
    
    tk.Label(cash_table_header, text="💵 Cash Payment Data Table", 
             font=("Segoe UI", 14, "bold"), bg="#FFF3E0", fg="#E65100").pack(expand=True)
    
    # Cash Only Treeview
    cash_only_tree = ttk.Treeview(cash_only_frame, columns=("GSTIN", "Taxpayer Name", "Total SGST Cash", "Total Turnover", "Returns Count"), 
                                  show="headings", height=20)
    
    # Configure columns
    cash_only_tree.heading("GSTIN", text="GSTIN")
    cash_only_tree.heading("Taxpayer Name", text="Taxpayer Name")
    cash_only_tree.heading("Total SGST Cash", text="Total SGST Cash")
    cash_only_tree.heading("Total Turnover", text="Total Turnover")
    cash_only_tree.heading("Returns Count", text="Returns Count")
    
    cash_only_tree.column("GSTIN", width=200)
    cash_only_tree.column("Taxpayer Name", width=250)
    cash_only_tree.column("Total SGST Cash", width=150)
    cash_only_tree.column("Total Turnover", width=150)
    cash_only_tree.column("Returns Count", width=100)
    
    # Add scrollbars
    cash_only_vsb = ttk.Scrollbar(cash_only_frame, orient="vertical", command=cash_only_tree.yview)
    cash_only_hsb = ttk.Scrollbar(cash_only_frame, orient="horizontal", command=cash_only_tree.xview)
    cash_only_tree.configure(yscrollcommand=cash_only_vsb.set, xscrollcommand=cash_only_hsb.set)
    
    # Pack tree and scrollbars
    cash_only_tree.pack(side="left", fill="both", expand=True)
    cash_only_vsb.pack(side="right", fill="y")
    cash_only_hsb.pack(side="bottom", fill="x")
    

    
    # Tab 3: ITC Only Report
    itc_only_frame = tk.Frame(notebook, bg="white")
    notebook.add(itc_only_frame, text="ITC Only")
    
    # Tab header with icon
    itc_header_frame = tk.Frame(itc_only_frame, bg="#E8F5E8", height=60)
    itc_header_frame.pack(fill="x", pady=(0, 20))
    
    tk.Label(itc_header_frame, text="🏦 Taxpayers with Only ITC Payment (No SGST Cash)", 
             font=("Segoe UI", 18, "bold"), bg="#E8F5E8", fg="#2E7D32").pack(expand=True)
    
    # Table header label
    itc_table_header = tk.Frame(itc_only_frame, bg="#E8F5E8", height=40)
    itc_table_header.pack(fill="x", pady=(0, 10))
    
    tk.Label(itc_table_header, text="🏦 ITC Payment Data Table", 
             font=("Segoe UI", 14, "bold"), bg="#E8F5E8", fg="#2E7D32").pack(expand=True)
    
    # ITC Only Treeview
    itc_only_tree = ttk.Treeview(itc_only_frame, columns=("GSTIN", "Taxpayer Name", "Total ITC", "Total Turnover", "Returns Count"), 
                                 show="headings", height=20)
    
    # Configure columns
    itc_only_tree.heading("GSTIN", text="GSTIN")
    itc_only_tree.heading("Taxpayer Name", text="Taxpayer Name")
    itc_only_tree.heading("Total ITC", text="Total ITC")
    itc_only_tree.heading("Total Turnover", text="Total Turnover")
    itc_only_tree.heading("Returns Count", text="Returns Count")
    
    itc_only_tree.column("GSTIN", width=200)
    itc_only_tree.column("Taxpayer Name", width=250)
    itc_only_tree.column("Total ITC", width=150)
    itc_only_tree.column("Total Turnover", width=150)
    itc_only_tree.column("Returns Count", width=100)
    
    # Add scrollbars
    itc_only_vsb = ttk.Scrollbar(itc_only_frame, orient="vertical", command=itc_only_tree.yview)
    itc_only_hsb = ttk.Scrollbar(itc_only_frame, orient="horizontal", command=itc_only_tree.xview)
    itc_only_tree.configure(yscrollcommand=itc_only_vsb.set, xscrollcommand=itc_only_hsb.set)
    
    # Pack tree and scrollbars
    itc_only_tree.pack(side="left", fill="both", expand=True)
    itc_only_vsb.pack(side="right", fill="y")
    itc_only_hsb.pack(side="bottom", fill="x")
    

    
    # Report Generation Functions
    def generate_turnover_report(fy):
        """Generate Total Turnover Report"""
        # Clear existing data
        for item in turnover_tree.get_children():
            turnover_tree.delete(item)
        
        try:
            with db.get_conn() as conn:
                cur = conn.cursor()
                cur.execute("""
                    SELECT 
                        t.gstin,
                        t.name,
                        SUM(r.total_turnover) as total_turnover,
                        SUM(r.total_gst_paid) as total_gst_paid,
                        COUNT(r.id) as records_count
                    FROM taxpayers t
                    LEFT JOIN gst_returns r ON t.gstin = r.taxpayer_gstin
                    WHERE r.financial_year = ?
                    GROUP BY t.gstin, t.name
                    ORDER BY total_turnover DESC
                """, (fy,))
                
                for row in cur.fetchall():
                    gstin, name, turnover, gst_paid, count = row
                    turnover_tree.insert("", "end", values=(
                        gstin,
                        name,
                        f"{turnover:,.2f}" if turnover else "0.00",
                        f"{gst_paid:,.2f}" if gst_paid else "0.00",
                        count
                    ))
                
                
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate turnover report: {str(e)}")
    
    def generate_cash_only_report(fy):
        """Generate Cash Only Report (No ITC)"""
        # Clear existing data
        for item in cash_only_tree.get_children():
            cash_only_tree.delete(item)
        
        try:
            with db.get_conn() as conn:
                cur = conn.cursor()
                cur.execute("""
                    SELECT 
                        t.gstin,
                        t.name,
                        SUM(r.sgst_cash_paid) as total_sgst_cash,
                        SUM(r.total_turnover) as total_turnover,
                        COUNT(r.id) as records_count
                    FROM taxpayers t
                    LEFT JOIN gst_returns r ON t.gstin = r.taxpayer_gstin
                    WHERE r.financial_year = ?
                    AND r.sgst_cash_paid > 0
                    AND (r.gst_itc = 0 OR r.gst_itc IS NULL)
                    GROUP BY t.gstin, t.name
                    ORDER BY total_sgst_cash DESC
                """, (fy,))
                
                for row in cur.fetchall():
                    gstin, name, sgst_cash, turnover, count = row
                    cash_only_tree.insert("", "end", values=(
                        gstin,
                        name,
                        f"{sgst_cash:,.2f}" if sgst_cash else "0.00",
                        f"{turnover:,.2f}" if turnover else "0.00",
                        count
                    ))
                
                
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate cash only report: {str(e)}")
    
    def generate_itc_only_report(fy):
        """Generate ITC Only Report (No Cash)"""
        # Clear existing data
        for item in itc_only_tree.get_children():
            itc_only_tree.delete(item)
        
        try:
            with db.get_conn() as conn:
                cur = conn.cursor()
                cur.execute("""
                    SELECT 
                        t.gstin,
                        t.name,
                        SUM(r.gst_itc) as total_itc,
                        SUM(r.total_turnover) as total_turnover,
                        COUNT(r.id) as records_count
                    FROM taxpayers t
                    LEFT JOIN gst_returns r ON t.gstin = r.taxpayer_gstin
                    WHERE r.financial_year = ?
                    AND r.gst_itc > 0
                    AND (r.sgst_cash_paid = 0 OR r.sgst_cash_paid IS NULL)
                    GROUP BY t.gstin, t.name
                    ORDER BY total_itc DESC
                """, (fy,))
                
                for row in cur.fetchall():
                    gstin, name, itc, turnover, count = row
                    itc_only_tree.insert("", "end", values=(
                        gstin,
                        name,
                        f"{itc:,.2f}" if itc else "0.00",
                        f"{turnover:,.2f}" if turnover else "0.00",
                        count
                    ))
                
                
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate ITC only report: {str(e)}")
    
    def export_report_to_excel(tree, filename):
        """Export treeview data to Excel"""
        if not tree.get_children():
            messagebox.showwarning("No Data", "No data to export.")
            return
        
        # Get save path
        save_path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx")],
            initialfile=f"{filename}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        )
        
        if not save_path:
            return
        
        try:
            # Get data from treeview
            data = []
            columns = []
            
            # Get column headers
            for col in tree["columns"]:
                columns.append(col)
            
            # Get data rows
            for item in tree.get_children():
                row = tree.item(item)["values"]
                data.append(row)
            
            # Create DataFrame
            df = pd.DataFrame(data, columns=columns)
            
            # Export to Excel
            with pd.ExcelWriter(save_path, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Report Data', index=False)
                
                # Get workbook and format
                workbook = writer.book
                worksheet = writer.sheets['Report Data']
                
                # Auto-adjust column widths
                for column in worksheet.columns:
                    max_length = 0
                    column_letter = column[0].column_letter
                    for cell in column:
                        try:
                            if len(str(cell.value)) > max_length:
                                max_length = len(str(cell.value))
                        except:
                            pass
                    adjusted_width = min(max_length + 2, 50)
                    worksheet.column_dimensions[column_letter].width = adjusted_width
                
                # Format headers
                for col_num in range(1, len(columns) + 1):
                    cell = worksheet.cell(row=1, column=col_num)
                    cell.font = Font(bold=True)
                    cell.fill = PatternFill(start_color="E3F2FD", end_color="E3F2FD", fill_type="solid")
            
            messagebox.showinfo("Success", f"Report exported successfully to:\n{save_path}")
            
            # Open the file
            try:
                os.startfile(save_path)
            except Exception:
                pass
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export report: {str(e)}")
    
        # Close button
    close_btn = tk.Button(main_frame, text="Close", command=reports_win.destroy,
                           bg="red", fg="white", font=("Arial", 10), 
                           padx=20, pady=5)
    close_btn.pack(pady=10)

def show_advanced_reports_page():
    """Show the Advanced Reports Page with comprehensive analytics"""
    # Create a new window for advanced reports
    advanced_reports_win = tk.Toplevel(root)
    advanced_reports_win.title("📊 GST Advanced Reports Dashboard")
    advanced_reports_win.state('zoomed')  # Full screen
    advanced_reports_win.transient(root)
    advanced_reports_win.grab_set()
    
    # Initialize the ReportsPage class
    reports_page = ReportsPage(advanced_reports_win)

# ---------- UI ----------
root = tk.Tk()
root.title("GST Taxpayer Manager")
root.state('zoomed')  # Maximized window (Windows)

# Center the window on screen
def center_window():
    # Update the window to get accurate dimensions
    root.update_idletasks()
    
    # Get screen dimensions
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    
    # Get window dimensions
    window_width = 1400
    window_height = 650
    
    # Calculate position to center the window
    x = (screen_width - window_width) // 2
    y = (screen_height - window_height) // 2
    
    # Set the window position
    root.geometry(f"{window_width}x{window_height}+{x}+{y}")

# Center the window after it's created
# root.after(100, center_window) # This line is removed as per the edit hint

# Create two rows for buttons with beautiful styling
topbar = tk.Frame(root, bg="#f8f9fa", relief="flat", bd=0)
topbar.pack(fill="x", padx=15, pady=12)

# Add a subtle border line below the topbar
border_line = tk.Frame(root, height=2, bg="#dee2e6")
border_line.pack(fill="x", padx=15)

# First row of buttons
topbar_row1 = tk.Frame(topbar, bg="#f8f9fa")
topbar_row1.pack(fill="x", pady=(0, 8))

# Beautiful button creation function
def create_beautiful_button(parent, text, command, button_type="primary", width=15):
    """Create a beautifully styled button"""
    colors = {
        "primary": {"bg": "#007bff", "fg": "white", "active_bg": "#0056b3", "active_fg": "white"},
        "success": {"bg": "#28a745", "fg": "white", "active_bg": "#1e7e34", "active_fg": "white"},
        "info": {"bg": "#17a2b8", "fg": "white", "active_bg": "#117a8b", "active_fg": "white"},
        "warning": {"bg": "#ffc107", "fg": "black", "active_bg": "#e0a800", "active_fg": "black"},
        "danger": {"bg": "#dc3545", "fg": "white", "active_bg": "#c82333", "active_fg": "white"},
        "secondary": {"bg": "#6c757d", "fg": "white", "active_bg": "#545b62", "active_fg": "white"}
    }
    
    # Create a frame for the button to add shadow effect
    btn_frame = tk.Frame(parent, bg="#f8f9fa")
    
    btn = tk.Button(
        btn_frame, 
        text=text, 
        command=command,
        bg=colors[button_type]["bg"],
        fg=colors[button_type]["fg"],
        activebackground=colors[button_type]["active_bg"],
        activeforeground=colors[button_type]["active_fg"],
        font=("Segoe UI", 10, "bold"),
        relief="flat",
        bd=0,
        padx=20,
        pady=8,
        width=width,
        cursor="hand2"
    )
    
    # Pack the button in its frame
    btn.pack()
    
    # Add hover effects with smooth transitions
    def on_enter(e):
        btn.config(bg=colors[button_type]["active_bg"])
        # Add subtle shadow effect
        btn_frame.config(bg="#e9ecef")
    
    def on_leave(e):
        btn.config(bg=colors[button_type]["bg"])
        # Remove shadow effect
        btn_frame.config(bg="#f8f9fa")
    
    btn.bind("<Enter>", on_enter)
    btn.bind("<Leave>", on_leave)
    
    # Add click effect
    def on_click(e):
        btn.config(relief="sunken")
        btn.after(100, lambda: btn.config(relief="flat"))
    
    btn.bind("<Button-1>", on_click)
    
    return btn_frame

# Create first row buttons with beautiful styling
upload_btn = create_beautiful_button(topbar_row1, "📁 Upload Taxpayers Excel", upload_taxpayers_excel, "primary", 20)
upload_btn.pack(side="left", padx=8)

returns_btn = create_beautiful_button(topbar_row1, "📊 Upload Returns", upload_returns_excel, "success", 18)
returns_btn.pack(side="left", padx=8)

details_btn = create_beautiful_button(topbar_row1, "👁️ View Details", view_details, "info", 15)
details_btn.pack(side="left", padx=8)

summary_btn = create_beautiful_button(topbar_row1, "📋 View Summary", lambda: view_summary(), "warning", 15)
summary_btn.pack(side="left", padx=8)

generate_btn = create_beautiful_button(topbar_row1, "⚡ Generate Summary", generate_report, "secondary", 18)
generate_btn.pack(side="left", padx=8)

# Second row of buttons
topbar_row2 = tk.Frame(topbar, bg="#f8f9fa")
topbar_row2.pack(fill="x", pady=(0, 8))

reports_btn = create_beautiful_button(topbar_row2, "📈 Reports", lambda: show_reports_page(), "info", 15)
reports_btn.pack(side="left", padx=8)

advanced_btn = create_beautiful_button(topbar_row2, "🚀 Advanced Reports", lambda: show_advanced_reports_page(), "primary", 18)
advanced_btn.pack(side="left", padx=8)

gstr_btn = create_beautiful_button(topbar_row2, "📋 Generate GSTR-1/3B Non Filers", generate_gstr1_non_filers, "warning", 25)
gstr_btn.pack(side="left", padx=8)

delete_btn = create_beautiful_button(topbar_row2, "🗑️ Delete Selected", delete_taxpayers, "danger", 18)
delete_btn.pack(side="left", padx=8)

# Add Edit Selected button to topbar with beautiful styling
edit_btn = create_beautiful_button(topbar_row2, "✏️ Edit Selected", lambda: edit_selected_taxpayer(), "success", 18)
edit_btn.pack(side="left", padx=8)


def on_tree_select(event=None):
    sels = tree.selection()
    if len(sels) == 1:
        edit_btn.winfo_children()[0].config(state="normal")  # Get the actual button from the frame
        # Enable the button visually
        edit_btn.winfo_children()[0].config(bg="#28a745", fg="white")
    else:
        edit_btn.winfo_children()[0].config(state="disabled")  # Get the actual button from the frame
        # Disable the button visually
        edit_btn.winfo_children()[0].config(bg="#6c757d", fg="white")

# Edit dialog logic
def edit_selected_taxpayer():
    sels = tree.selection()
    if len(sels) != 1:
        messagebox.showwarning("Select one taxpayer", "Please select exactly one taxpayer to edit.")
        return
    vals = tree.item(sels[0], "values")
    gstin = vals[0]
    tp = db.get_taxpayer_details(gstin)
    if not tp:
        messagebox.showerror("Error", "Taxpayer not found.")
        return
    # tp: (gstin, name, address, email, mobile, assigned_to, type, constitution, created_at)
    edit_win = tk.Toplevel(root)
    edit_win.title(f"Edit Taxpayer — {tp[1]} ({tp[0]})")
    win_width, win_height = 500, 440
    screen_width = edit_win.winfo_screenwidth()
    screen_height = edit_win.winfo_screenheight()
    x = (screen_width - win_width) // 2
    y = (screen_height - win_height) // 2
    edit_win.geometry(f"{win_width}x{win_height}+{x}+{y}")
    edit_win.transient(root)
    edit_win.grab_set()
    labels = ["GSTIN", "Name", "Address", "Email", "Mobile", "Assigned To", "Type", "Constitution"]
    vars = [tk.StringVar(value=str(x) if x is not None else "") for x in tp[:8]]
    field_widgets = []
    for i, (label, var) in enumerate(zip(labels, vars)):
        tk.Label(edit_win, text=label+":", anchor="e", font=("Segoe UI", 10, "bold")).grid(row=i, column=0, sticky="e", padx=(30,10), pady=8)
        if label == "Address":
            address_text = tk.Text(edit_win, width=38, height=3, wrap="word")
            address_text.insert("1.0", tp[2] if tp[2] else "")
            address_text.grid(row=i, column=1, sticky="w", padx=(0,30), pady=8)
            field_widgets.append(address_text)
        elif label == "Assigned To":
            assigned_to_combo = ttk.Combobox(edit_win, textvariable=var, values=["STATE", "CENTRE"], state="readonly", width=38)
            assigned_to_combo.grid(row=i, column=1, sticky="w", padx=(0,30), pady=8)
            field_widgets.append(assigned_to_combo)
        elif label == "Mobile":
            # Only allow digits in mobile entry
            def validate_mobile(P):
                return P.isdigit() or P == ""
            vcmd = (edit_win.register(validate_mobile), '%P')
            entry = tk.Entry(edit_win, textvariable=var, width=40, validate='key', validatecommand=vcmd)
            # Remove any .0 from initial value
            clean_mobile = str(tp[4]) if tp[4] else ""
            if clean_mobile.endswith('.0'):
                clean_mobile = clean_mobile[:-2]
            var.set(clean_mobile)
            entry.grid(row=i, column=1, sticky="w", padx=(0,30), pady=8)
            field_widgets.append(entry)
        else:
            entry = tk.Entry(edit_win, textvariable=var, width=40)
            entry.grid(row=i, column=1, sticky="w", padx=(0,30), pady=8)
            field_widgets.append(entry)
            if label == "GSTIN":
                entry.config(state="readonly")
    def save_edits():
        address_val = address_text.get("1.0", "end").strip()
        mobile_val = vars[4].get().strip()
        # Remove any .0 and non-digits
        mobile_val = ''.join(filter(str.isdigit, mobile_val))
        if len(mobile_val) != 10:
            messagebox.showerror("Invalid Mobile", "Mobile number must be exactly 10 digits.")
            return
        db.update_taxpayer(
            vars[0].get(), vars[1].get(), address_val, vars[3].get(), mobile_val,
            vars[5].get(), vars[6].get(), vars[7].get()
        )
        edit_win.destroy()
        load_all_taxpayers(current_page)
        messagebox.showinfo("Success", "Taxpayer details updated.")
    btn_frame = tk.Frame(edit_win)
    btn_frame.grid(row=len(labels), column=0, columnspan=2, pady=18)
    btn_frame.grid_columnconfigure(0, weight=1)
    btn_frame.grid_columnconfigure(1, weight=1)
    tk.Button(btn_frame, text="Save", command=save_edits, bg="#4CAF50", fg="white", padx=20, width=10).grid(row=0, column=0, padx=20)
    tk.Button(btn_frame, text="Cancel", command=edit_win.destroy, bg="#f44336", fg="white", padx=20, width=10).grid(row=0, column=1, padx=20)

search_frame = tk.Frame(root)
search_frame.pack(fill="x", padx=10, pady=(0,8))
tk.Label(search_frame, text="Search by Name/GSTIN:").pack(side="left")
search_var = tk.StringVar()
search_entry = tk.Entry(search_frame, textvariable=search_var, width=40)
search_entry.pack(side="left", padx=6)
search_var.trace_add("write", lambda *args: do_search(page=0))

select_all_var = tk.BooleanVar()
tk.Checkbutton(search_frame, text="Select All", variable=select_all_var, command=select_all_toggle).pack(side="left", padx=12)

# Add Clear button to clear search and show all taxpayers
def clear_search():
    search_var.set("")  # Clear the search box
    load_all_taxpayers(0)  # Load all taxpayers from page 0

tk.Button(search_frame, text="Clear", command=clear_search, bg="#FF9800", fg="white", padx=15).pack(side="left", padx=5)

# Create frame for tree and scrollbars
tree_frame = tk.Frame(root)
tree_frame.pack(fill="both", expand=True, padx=10, pady=10)

# Create tree with scrollbars
tree = ttk.Treeview(tree_frame, columns=("gstin","name","email","mobile","assigned_to","type","constitution"), show="headings", selectmode="extended")

# Configure column widths and headings
for col, width in (("gstin",220),("name",320),("email",260),("mobile",160),("assigned_to",150),("type",120),("constitution",150)):
    tree.heading(col, text=col.upper())
    tree.column(col, width=width, stretch=False)  # Set stretch to False for horizontal scrolling

# Add double-click functionality to copy column values to clipboard
def on_tree_double_click(event):
    """Handle double-click on tree items to copy column values to clipboard"""
    region = tree.identify_region(event.x, event.y)
    if region == "cell":
        # Get the clicked item and column
        item = tree.identify_row(event.y)
        column = tree.identify_column(event.x)
        
        if item and column:
            # Get the item values
            values = tree.item(item, "values")
            if values:
                # Convert column index to list index (column 1 = index 0, column 2 = index 1, etc.)
                col_index = int(column[1]) - 1
                if 0 <= col_index < len(values):
                    # Get the value to copy
                    value_to_copy = str(values[col_index])
                    
                    # Copy to clipboard
                    root.clipboard_clear()
                    root.clipboard_append(value_to_copy)
                    
                    # Show brief feedback
                    show_copy_feedback(value_to_copy)

def show_copy_feedback(copied_value):
    """Show a brief feedback that value was copied"""
    # Create a temporary label to show copy feedback
    feedback_label = tk.Label(root, text=f"Copied: {copied_value[:30]}{'...' if len(copied_value) > 30 else ''}", 
                             bg="#4CAF50", fg="white", font=("Segoe UI", 9))
    
    # Position the label at the bottom right of the tree
    tree_frame.update_idletasks()
    x = tree_frame.winfo_rootx() + tree_frame.winfo_width() - 200
    y = tree_frame.winfo_rooty() + tree_frame.winfo_height() - 30
    
    feedback_label.place(x=x, y=y)
    
    # Remove the label after 2 seconds
    root.after(2000, feedback_label.destroy)

# Bind double-click event to the tree
tree.bind("<Double-1>", on_tree_double_click)

# Create scrollbars
v_scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
h_scrollbar = ttk.Scrollbar(tree_frame, orient="horizontal", command=tree.xview)

# Configure tree to use scrollbars
tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)

# Pack scrollbars and tree
v_scrollbar.pack(side="right", fill="y")
h_scrollbar.pack(side="bottom", fill="x")
tree.pack(side="left", fill="both", expand=True)
tree.bind("<<TreeviewSelect>>", on_tree_select)

# nicer look
style = ttk.Style(root)
try:
    style.theme_use("clam")
except tk.TclError:
    pass
style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))
style.configure("Treeview", rowheight=24, font=("Segoe UI", 10))

# Add bottom button frame for template generation
bottom_frame = tk.Frame(root)
bottom_frame.pack(fill="x", padx=10, pady=(0, 10))

def generate_sample_template():
    """Generate a sample taxpayers template based on Taxpayers_Details.xlsx"""
    try:
        # Read the template file
        template_path = "Taxpayers_Details.xlsx"
        if not os.path.exists(template_path):
            messagebox.showerror("Error", f"Template file '{template_path}' not found.")
            return
        
        template_df = pd.read_excel(template_path)
        
        # Create a new template with sample data
        sample_data = {
            'GSTIN': [
                '29ABCDE1234F1Z5',
                '07PQRSX5678L1Z2',
                '32SAMPLE1234F1Z5',
                '12EXAMPLE5678L1Z2',
                '06DEMO1234F1Z5'
            ],
            'Name': [
                'ABC Traders',
                'XYZ Enterprises',
                'Sample Company Ltd',
                'Example Business',
                'Demo Corporation'
            ],
            'Address': [
                '123 Main Street, City, State - 123456',
                '456 Business Park, Town, State - 654321',
                '789 Industrial Area, District, State - 789123',
                '321 Commercial Complex, City, State - 321789',
                '654 Corporate Tower, Metro, State - 456123'
            ],
            'Email': [
                'abc@example.com',
                'xyz@example.com',
                'sample@example.com',
                'example@example.com',
                'demo@example.com'
            ],
            'Mobile': [
                '9876543210',
                '8765432109',
                '7654321098',
                '6543210987',
                '5432109876'
            ],
            'Assigned To': [
                'Agent 1',
                'Agent 2',
                'Agent 3',
                'Agent 4',
                'Agent 5'
            ],
            'Type': [
                'Regular',
                'Regular',
                'Regular',
                'Regular',
                'Regular'
            ],
            'Constitution of Business': [
                'Proprietorship',
                'Partnership',
                'Company',
                'LLP',
                'Company'
            ],
            'Created At': [
                datetime.now().strftime('%Y-%m-%d'),
                datetime.now().strftime('%Y-%m-%d'),
                datetime.now().strftime('%Y-%m-%d'),
                datetime.now().strftime('%Y-%m-%d'),
                datetime.now().strftime('%Y-%m-%d')
            ]
        }
        
        # Create sample DataFrame
        sample_df = pd.DataFrame(sample_data)
        
        # Save to Excel with formatting
        save_path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel Workbook", "*.xlsx")],
            title="Save Sample Taxpayers Template",
            initialfile=f"Sample_Taxpayers_Template_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        )
        
        if not save_path:
            return
        
        # Export to Excel with formatting
        with pd.ExcelWriter(save_path, engine='openpyxl') as writer:
            sample_df.to_excel(writer, sheet_name='Taxpayers Template', index=False)
            
            # Get the workbook and worksheet
            workbook = writer.book
            worksheet = writer.sheets['Taxpayers Template']
            
            # Auto-adjust column widths
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = min(max_length + 2, 50)
                worksheet.column_dimensions[column_letter].width = adjusted_width
            
            # Format headers
            for col_num in range(1, len(sample_df.columns) + 1):
                cell = worksheet.cell(row=1, column=col_num)
                cell.font = Font(bold=True)
                cell.fill = PatternFill(start_color="E3F2FD", end_color="E3F2FD", fill_type="solid")
            
            # Add instructions sheet
            instructions_data = {
                'Column': [
                    'GSTIN',
                    'Name',
                    'Address',
                    'Email',
                    'Mobile',
                    'Assigned To',
                    'Type',
                    'Constitution of Business'
                ],
                'Description': [
                    '15-digit GST Identification Number (required)',
                    'Business/Trade Name (required)',
                    'Complete business address',
                    'Business email address',
                    'Contact mobile number',
                    'Name of assigned agent/employee',
                    'Business type (Regular, Composition, etc.)',
                    'Business constitution (Proprietorship, Partnership, Company, LLP, etc.)'
                ],
                'Example': [
                    '29ABCDE1234F1Z5',
                    'ABC Traders',
                    '123 Main Street, City, State - 123456',
                    'abc@example.com',
                    '9876543210',
                    'Agent 1',
                    'Regular',
                    'Proprietorship'
                ]
            }
            
            instructions_df = pd.DataFrame(instructions_data)
            instructions_df.to_excel(writer, sheet_name='Instructions', index=False)
            
            # Format instructions sheet
            instructions_worksheet = writer.sheets['Instructions']
            
            # Auto-adjust column widths for instructions
            for column in instructions_worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = min(max_length + 2, 50)
                instructions_worksheet.column_dimensions[column_letter].width = adjusted_width
            
            # Format instructions headers
            for col_num in range(1, len(instructions_df.columns) + 1):
                cell = instructions_worksheet.cell(row=1, column=col_num)
                cell.font = Font(bold=True)
                cell.fill = PatternFill(start_color="E3F2FD", end_color="E3F2FD", fill_type="solid")
        
        messagebox.showinfo(
            "Success", 
            f"Sample Taxpayers Template generated successfully!\n\n"
            f"File saved to:\n{save_path}\n\n"
            f"The template contains:\n"
            f"• Sample data for 5 taxpayers\n"
            f"• Instructions sheet with column descriptions\n"
            f"• Proper formatting and column widths"
        )
        
        # Open the file
        try:
            os.startfile(save_path)
        except Exception:
            pass
            
    except Exception as e:
        messagebox.showerror("Error", f"Failed to generate sample template:\n{e}")

# Add template generation button
template_button = tk.Button(
    bottom_frame, 
    text="Generate Sample Taxpayers Template", 
    command=generate_sample_template,
    bg="#FF9800", 
    fg="white", 
    padx=20,
    pady=5,
    font=("Segoe UI", 10, "bold")
)
template_button.pack(side="left", padx=5)

# Add help text
help_label = tk.Label(
    bottom_frame, 
    text="Click to generate a sample Excel template with the correct format for uploading taxpayers",
    fg="gray",
    font=("Segoe UI", 9)
)
help_label.pack(side="left", padx=10)

# Add credit text on the right side
credit_label = tk.Label(
    bottom_frame,
    text="Made with ❤️by Arshad Jackie",
    fg="#E91E63",  # Pink color for the heart
    font=("Segoe UI", 10, "bold")
)
credit_label.pack(side="right", padx=10)

# After tree and scrollbars are packed, add pagination controls:
pagination_frame = tk.Frame(root)
pagination_frame.pack(fill="x", padx=10, pady=(0, 10))
prev_btn = tk.Button(pagination_frame, text="Previous", command=goto_prev_page)
prev_btn.pack(side="left")
global pagination_label
pagination_label = tk.Label(pagination_frame, text="")
pagination_label.pack(side="left", padx=10)
next_btn = tk.Button(pagination_frame, text="Next", command=goto_next_page)
next_btn.pack(side="left")

# Add taxpayer count display
global taxpayer_count_label
taxpayer_count_label = tk.Label(pagination_frame, text="", fg="gray", font=("Segoe UI", 9))
taxpayer_count_label.pack(side="right", padx=10)

load_all_taxpayers(0)

root.mainloop()
