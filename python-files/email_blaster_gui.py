import os
import sys
import pandas as pd
import win32com.client as win32
from tkinter import ttk, filedialog, messagebox, StringVar, BooleanVar, IntVar, Canvas
import tkinter as tk
from tkinter.constants import *  # For BOTH, LEFT, RIGHT, etc.
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from typing import List, Dict, Optional, Tuple
from pathlib import Path

class EmailBlasterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Email Blaster — Developed by Ahmed Hossam")
        self.root.geometry("900x800")
        
        # Create main container with scrollbar
        self.main_frame = ttk.Frame(root)
        self.main_frame.pack(fill=BOTH, expand=True)
        
        # Create a canvas with scrollbar
        self.canvas = Canvas(self.main_frame, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self.main_frame, orient=VERTICAL, command=self.canvas.yview)
        
        # Pack scrollbar and canvas
        self.scrollbar.pack(side=RIGHT, fill=Y)
        self.canvas.pack(side=LEFT, fill=BOTH, expand=True)
        
        # Configure the canvas
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        # Create a frame inside the canvas
        self.scrollable_frame = ttk.Frame(self.canvas)
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor='nw', tags=('scrollable_frame',))
        
        # Bind mouse wheel for scrolling
        self.canvas.bind_all('<MouseWheel>', self._on_mousewheel)
        self.canvas.bind('<Configure>', self._on_canvas_configure)
        self.scrollable_frame.bind('<Configure>', self._on_frame_configure)
        
        # Make the window responsive
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)
        
        # Initialize variables
        self.file_path = StringVar()
        self.column_mapping = {
            'to': StringVar(),
            'cc': StringVar(),
            'subject': StringVar(),
            'body': StringVar()
        }
        self.attachment_mode = IntVar(value=1)  # 1: Fixed, 2: Per-row
        self.attachment_paths = [StringVar() for _ in range(5)]
        self.attachment_columns = [StringVar() for _ in range(5)]
        self.preview_emails = BooleanVar(value=True)
        self.send_immediately = BooleanVar(value=False)
        self.skip_empty_to = BooleanVar(value=True)
        self.df = None
        self.available_columns = []
        
        self.setup_ui()
    
    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
    def _on_canvas_configure(self, event):
        self.canvas.itemconfig('scrollable_frame', width=event.width)
        
    def _on_frame_configure(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox('all'))
    
    def setup_ui(self):
        # Main container with responsive grid
        main_frame = ttk.Frame(self.scrollable_frame, padding=10)
        main_frame.pack(fill=BOTH, expand=True)
        main_frame.grid_rowconfigure(0, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)
        
        # Header
        header = ttk.Label(
            main_frame, 
            text='Email Blaster - Developed by Ahmed Hossam - BIS Student', 
            font=('Helvetica', 16, 'bold')
        )
        header.pack(pady=(0, 10))
        
        # File Selection
        file_frame = ttk.LabelFrame(main_frame, text="1. Select Excel/CSV File", padding=10)
        file_frame.pack(fill=X, pady=5)
        
        ttk.Entry(file_frame, textvariable=self.file_path).pack(
            side=LEFT, fill=X, expand=True, padx=(0, 5)
        )
        ttk.Button(
            file_frame, 
            text="Browse...", 
            command=self.browse_file,
            bootstyle=SECONDARY
        ).pack(side=RIGHT)
        
        # Column Mapping
        self.setup_column_mapping(main_frame)
        
        # Attachments
        self.setup_attachments(main_frame)
        
        # Options
        self.setup_options(main_frame)
        
        # Buttons
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=X, pady=10)
        
        ttk.Button(
            btn_frame,
            text="Generate Emails",
            command=self.generate_emails,
            bootstyle=SUCCESS,
            width=15
        ).pack(side=LEFT, padx=5)
        
        ttk.Button(
            btn_frame,
            text="Quit",
            command=self.root.quit,
            bootstyle=DANGER,
            width=15
        ).pack(side=RIGHT, padx=5)
        
        # Status (outside scrollable area)
        self.status_var = StringVar(value="Ready")
        status_bar = ttk.Label(
            self.root, 
            textvariable=self.status_var,
            relief=SUNKEN,
            anchor=W,
            font=('Segoe UI', 9)
        )
        status_bar.pack(side=BOTTOM, fill=X, padx=2, pady=2)
        
        self.progress = ttk.Progressbar(
            main_frame, 
            mode='determinate',
            bootstyle=SUCCESS
        )
        self.progress.pack(side=BOTTOM, fill=X, pady=(0, 5))
    
    def setup_column_mapping(self, parent):
        frame = ttk.LabelFrame(parent, text="2. Map Columns", padding=10)
        frame.pack(fill=X, pady=5)
        self.column_frame = frame  # Store reference to column frame
        
        labels = ['To (required):', 'CC (optional):', 'Subject (required):', 'Body (required):']
        keys = ['to', 'cc', 'subject', 'body']
        
        for i, (label, key) in enumerate(zip(labels, keys)):
            row = ttk.Frame(frame)
            row.pack(fill=X, pady=2)
            
            ttk.Label(row, text=label, width=15, anchor=W).pack(side=LEFT)
            cb = ttk.Combobox(
                row, 
                textvariable=self.column_mapping[key],
                state='readonly',
                width=30
            )
            cb.pack(side=LEFT, padx=5)
            
            # Set initial values if available_columns is already populated
            if hasattr(self, 'available_columns'):
                cb['values'] = self.available_columns
    
    def setup_attachments(self, parent):
        # Configure styles
        style = ttk.Style()
        style.configure('Large.TLabel', font=('Segoe UI', 10, 'bold'), foreground='black')
        style.configure('Help.TLabel', font=('Segoe UI', 9), foreground='#333333')
        style.configure('Large.TRadiobutton', font=('Segoe UI', 10, 'bold'), foreground='black')
        style.configure('Large.TEntry', font=('Segoe UI', 10))
        style.configure('Large.TCombobox', font=('Segoe UI', 10))
        
        # Main container
        frame = ttk.LabelFrame(parent, text="3. Attachments", padding=10)
        frame.pack(fill=X, pady=5)
        
        # Section header
        ttk.Label(
            frame,
            text="Choose how to handle attachments:",
            style='Large.TLabel'
        ).pack(anchor='w', pady=(0, 10))
        
        # Fixed attachments option
        fixed_frame = ttk.Frame(frame)
        fixed_frame.pack(fill=X, pady=(5, 10))
        
        ttk.Radiobutton(
            fixed_frame,
            text="Fixed attachments for all rows",
            variable=self.attachment_mode,
            value=1,
            command=self.toggle_attachment_mode,
            style='Large.TRadiobutton'
        ).pack(anchor='nw')
        
        ttk.Label(
            fixed_frame,
            text="• Same files will be attached to every email\n• Use the file browser to select files"
                 "\n• Best for sending the same documents to all recipients",
            style='Help.TLabel',
            padding=(25, 0, 0, 5)
        ).pack(anchor='w', fill=X)
        
        # Divider
        ttk.Separator(frame, orient='horizontal').pack(fill=X, pady=5)
        
        # Per-row attachments option
        per_row_frame = ttk.Frame(frame)
        per_row_frame.pack(fill=X, pady=(10, 15))
        
        ttk.Radiobutton(
            per_row_frame,
            text="Per-row attachment columns",
            variable=self.attachment_mode,
            value=2,
            command=self.toggle_attachment_mode,
            style='Large.TRadiobutton'
        ).pack(anchor='nw')
        
        ttk.Label(
            per_row_frame,
            text="• Different attachments for each email"
                 "\n• Add columns in your Excel/CSV with file paths"
                 "\n• Example: 'C:/files/document.pdf' in the attachment column"
                 "\n• Best for personalized documents or certificates",
            style='Help.TLabel',
            padding=(25, 0, 0, 5)
        ).pack(anchor='w', fill=X)
        
        # Attachment files section
        ttk.Separator(frame, orient='horizontal').pack(fill=X, pady=5)
        
        ttk.Label(
            frame,
            text="Attachment Files:",
            style='Large.TLabel'
        ).pack(anchor='w', pady=(10, 5))
        
        # Container for attachment inputs
        self.attachment_frame = ttk.Frame(frame)
        self.attachment_frame.pack(fill=X, pady=(0, 5))
        
        # Create file input rows
        for i in range(5):
            row = ttk.Frame(self.attachment_frame)
            row.pack(fill=X, pady=2)
            
            # File number label
            file_label = ttk.Label(
                row, 
                text=f"File {i+1}:",
                width=8,
                style='Large.TLabel'
            )
            file_label.pack(side=LEFT, padx=(0, 5))
            
            if self.attachment_mode.get() == 1:
                entry = ttk.Entry(
                    row, 
                    textvariable=self.attachment_paths[i], 
                    width=40,
                    style='Large.TEntry'
                )
                entry.pack(side=LEFT, padx=5)
                
                ttk.Button(
                    row,
                    text="Browse...",
                    command=lambda i=i: self.browse_attachment(i),
                    bootstyle=SECONDARY,
                    width=10
                ).pack(side=LEFT)
            else:
                cb = ttk.Combobox(
                    row,
                    textvariable=self.attachment_columns[i],
                    state='readonly',
                    width=40,
                    style='Large.TCombobox'
                )
                cb.pack(side=LEFT, padx=5)
    
    def setup_options(self, parent):
        frame = ttk.LabelFrame(parent, text="4. Options", padding=10)
        frame.pack(fill=X, pady=5)
        
        ttk.Checkbutton(
            frame,
            text="Preview emails before sending (recommended)",
            variable=self.preview_emails,
            command=self.toggle_preview_mode
        ).pack(anchor=W, pady=2)
        
        ttk.Checkbutton(
            frame,
            text="Send immediately without preview",
            variable=self.send_immediately,
            command=self.toggle_send_mode
        ).pack(anchor=W, pady=2)
        
        ttk.Checkbutton(
            frame,
            text="Skip rows with empty 'To' field",
            variable=self.skip_empty_to
        ).pack(anchor=W, pady=2)
    
    def toggle_attachment_mode(self):
        # Clear existing widgets
        for widget in self.attachment_frame.winfo_children():
            widget.destroy()
        
        # Rebuild attachment UI based on selected mode
        # Create file input rows
        for i in range(5):
            row = ttk.Frame(self.attachment_frame)
            row.pack(fill=X, pady=2)
            
            # File number label
            file_label = ttk.Label(
                row, 
                text=f"File {i+1}:",
                width=8,
                style='Large.TLabel'
            )
            file_label.pack(side=LEFT, padx=(0, 5))
            
            if self.attachment_mode.get() == 1:  # Fixed mode
                entry = ttk.Entry(
                    row, 
                    textvariable=self.attachment_paths[i], 
                    width=40,
                    style='Large.TEntry'
                )
                entry.pack(side=LEFT, padx=5)
                
                ttk.Button(
                    row,
                    text="Browse...",
                    command=lambda i=i: self.browse_attachment(i),
                    bootstyle=SECONDARY,
                    width=10
                ).pack(side=LEFT)
            else:  # Per-row mode
                cb = ttk.Combobox(
                    row,
                    textvariable=self.attachment_columns[i],
                    state='readonly',
                    width=40,
                    style='Large.TCombobox'
                )
                cb.pack(side=LEFT, padx=5)
                
                # Update combobox values if we have a file loaded
                if hasattr(self, 'available_columns'):
                    cb['values'] = self.available_columns
    
    def toggle_preview_mode(self):
        if self.preview_emails.get():
            self.send_immediately.set(False)
    
    def toggle_send_mode(self):
        if self.send_immediately.get():
            self.preview_emails.set(False)
    
    def browse_file(self):
        file_types = [
            ('Excel/CSV Files', '*.xlsx *.xls *.csv'),
            ('All Files', '*.*')
        ]
        filename = filedialog.askopenfilename(
            title="Select Excel/CSV File",
            filetypes=file_types
        )
        
        if filename:
            self.file_path.set(filename)
            self.load_file_columns(filename)
    
    def browse_attachment(self, index):
        filename = filedialog.askopenfilename(title=f"Select Attachment {index+1}")
        if filename:
            self.attachment_paths[index].set(filename)
    
    def load_file_columns(self, file_path):
        try:
            if file_path.endswith(('.xlsx', '.xls')):
                self.df = pd.read_excel(file_path, nrows=0)  # Only read headers
            else:  # CSV
                self.df = pd.read_csv(file_path, nrows=0)
            
            self.available_columns = self.df.columns.tolist()
            
            # Clear existing values
            for var in self.column_mapping.values():
                var.set('')
            
            # Update column mapping comboboxes
            for widget in self.column_frame.winfo_children():
                if isinstance(widget, ttk.Frame):
                    for child in widget.winfo_children():
                        if isinstance(child, ttk.Combobox):
                            child['values'] = self.available_columns
                            child.set('')
            
            # Update attachment column comboboxes if in per-row mode
            if self.attachment_mode.get() == 2:
                for widget in self.attachment_frame.winfo_children():
                    if isinstance(widget, ttk.Frame):
                        for child in widget.winfo_children():
                            if isinstance(child, ttk.Combobox):
                                child['values'] = self.available_columns
                                child.set('')
            
            self.status_var.set(f"Loaded {len(self.available_columns)} columns from {os.path.basename(file_path)}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load file: {str(e)}\nMake sure the file is not open in another program.")
            self.status_var.set("Error loading file")
    
    def validate_inputs(self) -> bool:
        if not self.file_path.get() or not os.path.exists(self.file_path.get()):
            messagebox.showerror("Error", "Please select a valid Excel/CSV file")
            return False
        
        if not self.column_mapping['to'].get():
            messagebox.showerror("Error", "Please select a column for 'To' field")
            return False
        
        if not self.column_mapping['subject'].get():
            messagebox.showerror("Error", "Please select a column for 'Subject' field")
            return False
        
        if not self.column_mapping['body'].get():
            messagebox.showerror("Error", "Please select a column for 'Body' field")
            return False
        
        return True
    
    def generate_emails(self):
        if not self.validate_inputs():
            return
        
        try:
            # Load the data
            file_path = self.file_path.get()
            self.status_var.set("Loading data file...")
            self.root.update_idletasks()
            
            try:
                if file_path.endswith(('.xlsx', '.xls')):
                    self.df = pd.read_excel(file_path, dtype=str)
                else:  # CSV
                    self.df = pd.read_csv(file_path, dtype=str)
                
                # Replace NaN with empty string
                self.df = self.df.fillna('')
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load file: {str(e)}\nMake sure the file is not open in another program.")
                self.status_var.set("Error loading file")
                return
            
            total_emails = len(self.df)
            if total_emails == 0:
                messagebox.showinfo("Info", "No data found in the selected file")
                self.status_var.set("No data found in file")
                return
            
            # Initialize Email Client
            try:
                self.status_var.set("Initializing email client...")
                self.root.update_idletasks()
                
                # Try Outlook first
                try:
                    try:
                        outlook = win32.GetActiveObject('Outlook.Application')
                    except:
                        outlook = win32.Dispatch('Outlook.Application')
                    
                    # Test Outlook functionality
                    test_mail = outlook.CreateItem(0)
                    if not test_mail:
                        raise Exception("Outlook is running but cannot create email items")
                    test_mail = None
                    self.status_var.set("Connected to Outlook")
                    
                except Exception as e:
                    # If Outlook fails, try using Windows Mail
                    self.status_var.set("Outlook not available, trying Windows Mail...")
                    self.root.update_idletasks()
                    
                    # Initialize Windows Mail
                    try:
                        # Just set up for Windows Mail without sending a test email
                        outlook = None
                        self.status_var.set("Using Windows Mail")
                        
                    except Exception as mail_err:
                        raise Exception(f"Failed to initialize any email client. Please install Microsoft Outlook or set up Windows Mail.")
                
            except Exception as e:
                error_msg = (
                    f"Email Client Error: {str(e)}\n\n"
                    "This application requires either:\n"
                    "1. Microsoft Outlook (recommended):\n"
                    "   - Install Microsoft 365 or Outlook from Microsoft Store\n"
                    "   - Open Outlook and set up your email account\n"
                    "   - Make sure Outlook is running in the background\n\n"
                    "2. Windows Mail:\n"
                    "   - Set up Windows Mail with your email account\n"
                    "   - Set it as your default mail client"
                )
                messagebox.showerror("Email Client Error", error_msg)
                self.status_var.set("Email client initialization failed")
                return
            
            # Process each row
            success_count = 0
            self.progress['maximum'] = total_emails
            
            for idx, row in self.df.iterrows():
                try:
                    # Get column values
                    to_col = self.column_mapping['to'].get()
                    if not to_col or to_col not in row:
                        error_msg = f"Column '{to_col}' not found in the data. Please check your column mapping."
                        messagebox.showerror("Error", error_msg)
                        self.status_var.set("Column mapping error")
                        return
                        
                    to_email = str(row[to_col]).strip()
                    
                    # Skip if To is empty and skip_empty_to is checked
                    if not to_email and self.skip_empty_to.get():
                        continue
                    
                    # Validate required fields
                    subject = str(row.get(self.column_mapping['subject'].get(), '')).strip()
                    body = str(row.get(self.column_mapping['body'].get(), '')).strip()
                    
                    if not subject:
                        messagebox.showwarning("Warning", f"Empty subject in row {idx+1}. This email will be skipped.")
                        continue
                    
                    if not body:
                        messagebox.showwarning("Warning", f"Empty body in row {idx+1}. This email will be skipped.")
                        continue
                    
                    try:
                        if outlook is not None:
                            # Use Outlook
                            try:
                                mail = outlook.CreateItem(0)  # 0 = olMailItem
                                if not mail:
                                    raise Exception("Failed to create Outlook email item")
                                
                                # Set recipients
                                mail.To = to_email
                                
                                # Add CC if specified
                                if self.column_mapping['cc'].get() and self.column_mapping['cc'].get() in row:
                                    cc_email = str(row[self.column_mapping['cc'].get()]).strip()
                                    if cc_email:
                                        mail.CC = cc_email
                                
                                # Set subject and body
                                mail.Subject = subject
                                mail.Body = body
                                
                                # Add attachments
                                try:
                                    if self.attachment_mode.get() == 1:  # Fixed attachments
                                        for path_var in self.attachment_paths:
                                            path = path_var.get().strip()
                                            if path and os.path.exists(path):
                                                mail.Attachments.Add(path)
                                            elif path:  # Path specified but doesn't exist
                                                messagebox.showwarning("Warning", f"Attachment not found: {path}")
                                    else:  # Per-row attachments
                                        for col_var in self.attachment_columns:
                                            col_name = col_var.get()
                                            if col_name and col_name in row and row[col_name]:
                                                attachment_path = str(row[col_name]).strip()
                                                if os.path.exists(attachment_path):
                                                    mail.Attachments.Add(attachment_path)
                                except Exception as e:
                                    messagebox.showwarning("Warning", f"Error adding attachments: {str(e)}")
                                
                                # Display or send email
                                if self.send_immediately.get():
                                    try:
                                        mail.Send()
                                        self.status_var.set(f"Sent email {idx+1} of {total_emails}")
                                    except Exception as send_err:
                                        # If send fails, fall back to display
                                        messagebox.showwarning(
                                            "Send Failed", 
                                            f"Could not send email automatically: {str(send_err)}\n"
                                            "The email will be opened for manual sending."
                                        )
                                        mail.Display(False)
                                        self.status_var.set(f"Previewing email {idx+1} of {total_emails} (send failed)")
                                else:
                                    mail.Display(False)  # False = non-modal
                                    self.status_var.set(f"Previewing email {idx+1} of {total_emails}")
                                    
                            except Exception as e:
                                raise Exception(f"Outlook error: {str(e)}")
                            
                        else:
                            # Use Windows Mail (or default mail client)
                            try:
                                import win32com.client as win32
                                import pythoncom
                                
                                # Initialize COM in a new thread
                                pythoncom.CoInitialize()
                                
                                try:
                                    # Try to use Outlook automation
                                    outlook = win32.Dispatch('Outlook.Application')
                                    mail = outlook.CreateItem(0)  # olMailItem = 0
                                    
                                    # Set email properties
                                    mail.To = to_email
                                    
                                    # Add CC if specified
                                    if self.column_mapping['cc'].get() and self.column_mapping['cc'].get() in row:
                                        cc_email = str(row[self.column_mapping['cc'].get()]).strip()
                                        if cc_email:
                                            mail.CC = cc_email
                                    
                                    mail.Subject = subject
                                    mail.Body = body
                                    
                                    # Add attachments
                                    try:
                                        if self.attachment_mode.get() == 1:  # Fixed attachments
                                            for path_var in self.attachment_paths:
                                                path = path_var.get().strip()
                                                if path and os.path.exists(path):
                                                    mail.Attachments.Add(path)
                                                elif path:  # Path specified but doesn't exist
                                                    messagebox.showwarning("Warning", f"Attachment not found: {path}")
                                        else:  # Per-row attachments
                                            for col_var in self.attachment_columns:
                                                col_name = col_var.get()
                                                if col_name and col_name in row and row[col_name]:
                                                    attachment_path = str(row[col_name]).strip()
                                                    if os.path.exists(attachment_path):
                                                        mail.Attachments.Add(attachment_path)
                                    except Exception as e:
                                        messagebox.showwarning("Warning", f"Error adding attachments: {str(e)}")
                                    
                                    # Send or display the email
                                    if self.send_immediately.get():
                                        mail.Send()
                                        self.status_var.set(f"Sent email {idx+1} of {total_emails}")
                                    else:
                                        mail.Display(False)  # False = non-modal
                                        self.status_var.set(f"Previewing email {idx+1} of {total_emails}")
                                    
                                except Exception as e:
                                    # If Outlook automation fails, fall back to default mail client with warning about attachments
                                    import urllib.parse
                                    import webbrowser
                                    
                                    # Create mailto link (without attachments)
                                    mailto_parts = [
                                        f"to={urllib.parse.quote(to_email)}",
                                        f"subject={urllib.parse.quote(subject)}",
                                        f"body={urllib.parse.quote(body)}"
                                    ]
                                    
                                    # Add CC if specified
                                    if self.column_mapping['cc'].get() and self.column_mapping['cc'].get() in row:
                                        cc_email = str(row[self.column_mapping['cc'].get()]).strip()
                                        if cc_email:
                                            mailto_parts.append(f"cc={urllib.parse.quote(cc_email)}")
                                    
                                    # Open default mail client
                                    mailto_url = f"mailto:?{'&'.join(mailto_parts)}"
                                    webbrowser.open(mailto_url)
                                    
                                    # Show warning about attachments if any are specified
                                    if (self.attachment_mode.get() == 1 and any(p.get().strip() for p in self.attachment_paths)) or \
                                       (self.attachment_mode.get() == 2 and any(c.get() and c.get() in row and row[c.get()] for c in self.attachment_columns)):
                                        messagebox.showwarning(
                                            "Attachment Notice", 
                                            "Attachments cannot be automatically added with the default mail client.\n\n"
                                            "Please add the following attachments manually:\n" + 
                                            "\n".join(
                                                [f"- {p.get()}" for p in self.attachment_paths if p.get().strip()] if self.attachment_mode.get() == 1 else
                                                [f"- {row[c.get()]}" for c in self.attachment_columns if c.get() and c.get() in row and row[c.get()]]
                                            )
                                        )
                                    
                                    self.status_var.set(f"Opened email {idx+1} of {total_emails} in default mail client")
                                    
                            except Exception as e:
                                raise Exception(f"Failed to open default mail client: {str(e)}")
                            finally:
                                # Clean up COM
                                try:
                                    pythoncom.CoUninitialize()
                                except:
                                    pass
                        
                    except Exception as e:
                        raise Exception(f"Failed to create email: {str(e)}")
                    
                    success_count += 1
                    
                except Exception as e:
                    error_msg = f"Error processing row {idx+1}: {str(e)}"
                    messagebox.showerror("Error", error_msg)
                    self.status_var.set(error_msg)
                    
                    # Ask if user wants to continue after error
                    if not messagebox.askyesno("Continue?", "An error occurred. Do you want to continue with the next email?"):
                        break
                
                # Update progress
                self.progress['value'] = idx + 1
                self.root.update_idletasks()
            
            # Show completion message
            msg = f"Successfully processed {success_count} of {total_emails} emails"
            messagebox.showinfo("Complete", msg)
            self.status_var.set(msg)
            
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            error_msg = f"An unexpected error occurred: {str(e)}\n\n{error_details}"
            messagebox.showerror("Error", error_msg)
            self.status_var.set("Error occurred")
        finally:
            self.progress['value'] = 0

def main():
    root = ttk.Window(themename="minty")
    app = EmailBlasterApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
