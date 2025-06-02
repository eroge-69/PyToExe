import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import pandas as pd
import os

class VehicleDataApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Vehicle Data Search")
        self.root.geometry("1000x600")

        # Upload Files Button
        self.upload_btn = tk.Button(root, text="Upload .xls Files", command=self.upload_files, bg="blue", fg="white")
        self.upload_btn.pack(pady=10)

        # Progress Bar Frame
        self.progress_frame = tk.Frame(root)
        self.progress_frame.pack(pady=10)
        self.progress = ttk.Progressbar(self.progress_frame, orient="horizontal", length=300, mode="determinate")
        self.progress.pack(side=tk.LEFT, padx=10)
        self.progress_label = tk.Label(self.progress_frame, text="", font=("Arial", 12))  # Display percentage
        self.progress_label.pack(side=tk.LEFT)

        self.progress_frame.pack_forget()  # Hide initially

        # Search Frame
        self.search_frame = tk.Frame(root)
        self.search_frame.pack(pady=10)

        # Search TextField
        self.search_entry = tk.Entry(self.search_frame, width=40)
        self.search_entry.pack(side=tk.LEFT, padx=5)

        # Date Filter Checkbox
        self.date_filter_var = tk.BooleanVar()
        self.date_filter_checkbox = tk.Checkbutton(self.search_frame, text="Date Filter", variable=self.date_filter_var, command=self.toggle_date_fields)
        self.date_filter_checkbox.pack(side=tk.LEFT, padx=5)

        # Start and End Date TextFields (Initially Hidden)
        self.start_date_entry = tk.Entry(root, width=15)
        self.end_date_entry = tk.Entry(root, width=15)

        self.start_date_entry.pack_forget()
        self.end_date_entry.pack_forget()

        # Filter Button (Initially Hidden)
        self.filter_btn = tk.Button(root, text="Filter Record", command=self.filter_data, bg="purple", fg="white")
        self.filter_btn.pack_forget()

        # Search Button
        self.search_btn = tk.Button(root, text="Search", command=self.search_data, bg="green", fg="white")
        self.search_btn.pack(pady=10)

        # Table Frame
        self.tree_frame = tk.Frame(root, bg="lightgrey")
        self.tree_frame.pack(pady=10, fill="both", expand=True)

        # Scrollbar
        self.tree_scroll = tk.Scrollbar(self.tree_frame)
        self.tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        # Table (Treeview)
        self.tree = ttk.Treeview(self.tree_frame, yscrollcommand=self.tree_scroll.set)
        self.tree_scroll.config(command=self.tree.yview)
        self.tree.pack(fill="both", expand=True)

        self.data_list = []

    def upload_files(self):
        file_paths = filedialog.askopenfilenames(filetypes=[("Excel Files", "*.xls")])  # Restrict to `.xls` only
        if not file_paths:
            return

        self.progress_frame.pack()  # Show progress bar
        self.progress["maximum"] = len(file_paths)
        self.progress["value"] = 0
        self.progress_label.config(text="Uploading 0%")

        for index, file_path in enumerate(file_paths):
            try:
                # Read `.xls` file using `xlrd`
                df = pd.read_excel(file_path, engine="xlrd")
                self.data_list.append(df)

            except Exception as e:
                import traceback
                messagebox.showerror("Error", f"Failed to load {file_path}:\n{str(e)}\n\n{traceback.format_exc()}")

            # Update progress
            self.progress["value"] = index + 1
            percentage = int((index + 1) / len(file_paths) * 100)
            self.progress_label.config(text=f"Uploading {percentage}%")
            self.root.update_idletasks()  # Prevent UI freeze

        self.progress_label.config(text="Data Uploaded 100%")
        messagebox.showinfo("Success", "Files Uploaded Successfully!")

    def toggle_date_fields(self):
        if self.date_filter_var.get():
            self.start_date_entry.pack(pady=5)
            self.start_date_entry.delete(0, tk.END)
            self.start_date_entry.insert(0, "YYYY-MM-DD")
            self.end_date_entry.pack(pady=5)
            self.end_date_entry.delete(0, tk.END)
            self.end_date_entry.insert(0, "YYYY-MM-DD")
            self.filter_btn.pack(pady=5)
        else:
            self.start_date_entry.pack_forget()
            self.end_date_entry.pack_forget()
            self.filter_btn.pack_forget()

    def search_data(self):
        if not self.data_list:
            messagebox.showwarning("Warning", "Please upload at least one Excel file first.")
            return

        search_term = self.search_entry.get().strip()
        if not search_term:
            messagebox.showwarning("Warning", "Please enter a search term.")
            return

        combined_data = pd.concat(self.data_list, ignore_index=True)
        matching_records = combined_data[combined_data['Plate Number'].astype(str).str.contains(search_term, case=False, na=False)].copy()

        if matching_records.empty:
            messagebox.showinfo("No Results", "No matching records found.")
        else:
            if 'Date(Year/Month/Day)' in matching_records.columns:
                matching_records['Date(Year/Month/Day)'] = pd.to_datetime(matching_records['Date(Year/Month/Day)'], errors='coerce')

            matching_records = matching_records.sort_values(by='Date(Year/Month/Day)', ascending=True)

            for item in self.tree.get_children():
                self.tree.delete(item)

            self.tree["columns"] = list(matching_records.columns)
            self.tree["show"] = "headings"

            for col in matching_records.columns:
                self.tree.heading(col, text=col)
                self.tree.column(col, anchor="center", width=120)

            for _, row in matching_records.iterrows():
                self.tree.insert("", "end", values=list(row))

            self.filtered_data = matching_records

    def filter_data(self):
        if not hasattr(self, 'filtered_data'):
            messagebox.showwarning("Warning", "Please search for records first.")
            return

        try:
            start_date = pd.to_datetime(self.start_date_entry.get().strip(), errors='coerce')
            end_date = pd.to_datetime(self.end_date_entry.get().strip(), errors='coerce')

            if pd.isna(start_date) or pd.isna(end_date):
                messagebox.showerror("Error", "Please enter valid dates in YYYY-MM-DD format.")
                return

            filtered_records = self.filtered_data[
                (self.filtered_data['Date(Year/Month/Day)'] >= start_date) &
                (self.filtered_data['Date(Year/Month/Day)'] <= end_date)
            ]

            if filtered_records.empty:
                messagebox.showinfo("No Results", "No records found within the selected date range.")
            else:
                for item in self.tree.get_children():
                    self.tree.delete(item)

                for _, row in filtered_records.iterrows():
                    self.tree.insert("", "end", values=list(row))

        except Exception as e:
            messagebox.showerror("Error", f"Failed to filter records: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = VehicleDataApp(root)
    root.mainloop()
