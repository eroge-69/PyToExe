import re
import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

class DIDDataExtractorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("JLR Snapshot Comparison Tool")
        self.root.geometry("1100x700")
        self.root.configure(bg="#D6D6D6")  # JLR background color

        self.dataframe_1 = None
        self.dataframe_2 = None
        self.comparison_df = None
        self.file_1_name = tk.StringVar()
        self.file_2_name = tk.StringVar()
        self.module_var = tk.StringVar()
        self.did_var = tk.StringVar()

        # File selection buttons and display boxes
        file_frame = tk.Frame(root, bg="#D6D6D6")
        file_frame.pack(pady=5)

        # Set a fixed width for both upload buttons
        button_width = 20

        self.upload_button_1 = tk.Button(file_frame, text="Upload First Snapshot", command=self.upload_file_1,
                                         font=("Helvetica", 12, "bold"), bg="#005A4B", fg="white", relief="flat", width=button_width)
        self.upload_button_1.grid(row=0, column=0, padx=5)

        self.file_label_1 = tk.Label(file_frame, textvariable=self.file_1_name, font=("Helvetica", 10),
                                     width=40, bg="white", relief="sunken", anchor="w")
        self.file_label_1.grid(row=0, column=1, padx=5)

        self.upload_button_2 = tk.Button(file_frame, text="Upload Second Snapshot", command=self.upload_file_2,
                                         font=("Helvetica", 12, "bold"), bg="#005A4B", fg="white", relief="flat", width=button_width)
        self.upload_button_2.grid(row=1, column=0, padx=5)

        self.file_label_2 = tk.Label(file_frame, textvariable=self.file_2_name, font=("Helvetica", 10),
                                     width=40, bg="white", relief="sunken", anchor="w")
        self.file_label_2.grid(row=1, column=1, padx=5)

        # Filter section
        filter_frame = tk.Frame(root, bg="#D6D6D6")
        filter_frame.pack(pady=5)

        tk.Label(filter_frame, text="Module:", font=("Helvetica", 10), bg="#D6D6D6").grid(row=0, column=0, padx=5)
        self.module_dropdown = ttk.Combobox(filter_frame, textvariable=self.module_var, state="readonly")
        self.module_dropdown.grid(row=0, column=1, padx=5)
        self.module_dropdown.bind("<<ComboboxSelected>>", self.update_did_dropdown)

        tk.Label(filter_frame, text="DID Code:", font=("Helvetica", 10), bg="#D6D6D6").grid(row=0, column=2, padx=5)
        self.did_dropdown = ttk.Combobox(filter_frame, textvariable=self.did_var, state="readonly")
        self.did_dropdown.grid(row=0, column=3, padx=5)

        self.filter_button = tk.Button(filter_frame, text="Filter", command=self.apply_filter,
                                       font=("Helvetica", 10, "bold"), bg="#005A4B", fg="white", relief="flat")
        self.filter_button.grid(row=0, column=4, padx=10)

        # Add "Remove Filters" button with red color
        self.remove_filters_button = tk.Button(filter_frame, text="Remove Filters", command=self.remove_filters,
                                               font=("Helvetica", 10, "bold"), bg="red", fg="white", relief="flat")
        self.remove_filters_button.grid(row=0, column=5, padx=10)

        # Export to Excel button
        self.export_button = tk.Button(filter_frame, text="Export to Excel", command=self.export_to_excel,
                                       font=("Helvetica", 10, "bold"), bg="#004B87", fg="white", relief="flat")
        self.export_button.grid(row=0, column=6, padx=10)
        # Table to display differences
        self.tree_frame = tk.Frame(root, bg="#D6D6D6")
        self.tree_frame.pack(expand=True, fill="both", padx=10, pady=10)

        # Updated column names
        columns = ("Node", "Module", "DID Code", "DID Name", "Part Number 1", "Part Number 2", "Status")
        self.tree = ttk.Treeview(self.tree_frame, columns=columns, show="headings")
        self.tree.pack(expand=True, fill="both")

        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor="center")

        # Style for highlighting differences
        self.tree.tag_configure("match", background="lightgreen")
        self.tree.tag_configure("mismatch", background="lightcoral")

    def is_valid_snapshot_file(self, file_path):
        """
        Check if the uploaded file is a valid Snapshot file.
        A valid file should contain at least one line matching the expected patterns.
        """
        expected_patterns = [
            r"- MODULE \(Info\)  : Node - \d+",
            r"- MODULE \(Info\)  : Name - \w+",
            r"- DID \(Read\)     : [A-F0-9]+ \| \w+ \| Ascii - .*"
        ]

        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as file:
                data = file.readlines()

            # Check if any line matches the expected patterns
            for line in data:
                if any(re.search(pattern, line) for pattern in expected_patterns):
                    return True
            return False
        except Exception as e:
            print(f"Error reading file: {e}")
            return False

    def upload_file_1(self):
        file_path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
        if file_path:
            if not self.is_valid_snapshot_file(file_path):
                messagebox.showerror("Invalid File", "Text file has an invalid format. Please upload a valid Snapshot.")
                return
            self.file_1_name.set(file_path.split("/")[-1])
            self.dataframe_1 = self.process_file(file_path)
            self.save_to_csv(self.dataframe_1, "File_1.csv")
            messagebox.showinfo("Success", "First file processed and saved as CSV!")

    def upload_file_2(self):
        file_path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
        if file_path:
            if not self.is_valid_snapshot_file(file_path):
                messagebox.showerror("Invalid File", "Text file has an invalid format. Please upload a valid Snapshot.")
                return
            self.file_2_name.set(file_path.split("/")[-1])
            self.dataframe_2 = self.process_file(file_path)
            self.save_to_csv(self.dataframe_2, "File_2.csv")
            messagebox.showinfo("Success", "Second file processed and saved as CSV!")
            self.compare_files()

    def is_valid_ascii_value(self, value):
        """
        Check if the ASCII value is valid.
        Valid values contain only alphanumeric characters, spaces, or common punctuation.
        Also, discard values containing "data not processed" or fewer than 5 characters.
        """
        if "data not processed" in value.lower():
            return False
        if len(value.strip()) < 5:  # Discard values with fewer than 5 characters
            return False
        # Allow alphanumeric, spaces, and common punctuation
        return bool(re.match(r'^[a-zA-Z0-9\s\.,;:!?\-_()\'"]+$', value))

    def process_file(self, file_path):
        nodes_data = {}
        current_node = None

        node_start_pattern = re.compile(r"- MODULE \(Info\)  : Node - (\d+)")
        node_name_pattern = re.compile(r"- MODULE \(Info\)  : Name - (\w+)")
        did_read_pattern = re.compile(r"- DID \(Read\)     : ([A-F0-9]+) \| (\w+) \| Ascii - (.*)")

        with open(file_path, "r", encoding="utf-8", errors="ignore") as file:
            data = file.readlines()

        for line in data:
            node_match = node_start_pattern.search(line)
            if node_match:
                current_node = node_match.group(1)
                nodes_data[current_node] = {"Module": None, "DID Data": []}

            module_match = node_name_pattern.search(line)
            if module_match and current_node:
                nodes_data[current_node]["Module"] = module_match.group(1)

            did_match = did_read_pattern.search(line)
            if did_match and current_node:
                did_code, did_name, did_value = did_match.groups()
                if did_value.strip() and self.is_valid_ascii_value(did_value):  # Filter invalid ASCII values
                    nodes_data[current_node]["DID Data"].append({"DID Code": did_code, "DID Name": did_name, "ASCII Value": did_value})

        df_list = []
        for node, info in nodes_data.items():
            module = info["Module"]
            for entry in info["DID Data"]:
                df_list.append([node, module, entry["DID Code"], entry["DID Name"], entry["ASCII Value"]])

        return pd.DataFrame(df_list, columns=["Node", "Module", "DID Code", "DID Name", "ASCII Value"])

    def save_to_csv(self, dataframe, filename):
        dataframe.to_csv(filename, index=False)

    def compare_files(self):
        if self.dataframe_1 is None or self.dataframe_2 is None:
            messagebox.showerror("Error", "Please upload two files before comparing!")
            return

        comparison = self.dataframe_1.merge(self.dataframe_2, on=["Node", "Module", "DID Code", "DID Name"], how="inner", suffixes=(" File 1", " File 2"))
        comparison["Status"] = comparison.apply(
            lambda row: "✅" if row["ASCII Value File 1"] == row["ASCII Value File 2"] else "❌", axis=1
        )

        # Sort the comparison dataframe:
        # 1. Sort by Status (mismatches first, matches second)
        # 2. Within each status group, sort by Node
        comparison = comparison.sort_values(by=["Status", "Node"], ascending=[False, True])

        # Rename columns for display
        comparison = comparison.rename(columns={
            "ASCII Value File 1": "Part Number 1",
            "ASCII Value File 2": "Part Number 2"
        })
        # Auto-export a default Excel file next to the script
        try:
            desired_cols = ["Node", "Module", "DID Code", "DID Name", "Part Number 1", "Part Number 2", "Status"]
            cols = [c for c in desired_cols if c in comparison.columns]
            comparison[cols].to_excel("Comparison_Results.xlsx", index=False)
        except Exception as e:
            # Non-fatal; continue
            pass


        self.comparison_df = comparison
        self.update_module_dropdown()
        self.load_data(comparison)

    def update_module_dropdown(self):
        if self.comparison_df is not None:
            modules = sorted(self.comparison_df["Module"].unique().tolist())
            self.module_dropdown["values"] = modules

    def update_did_dropdown(self, event):
        selected_module = self.module_var.get()
        if self.comparison_df is not None and selected_module:
            did_codes = sorted(self.comparison_df[self.comparison_df["Module"] == selected_module]["DID Code"].unique().tolist())
            self.did_dropdown["values"] = did_codes

    def apply_filter(self):
        filtered_df = self.comparison_df
        if self.module_var.get():
            filtered_df = filtered_df[filtered_df["Module"] == self.module_var.get()]
        if self.did_var.get():
            filtered_df = filtered_df[filtered_df["DID Code"] == self.did_var.get()]
        self.load_data(filtered_df)

    def remove_filters(self):
        # Reset dropdowns and load the original comparison data
        self.module_var.set("")
        self.did_var.set("")
        if self.comparison_df is not None:
            self.load_data(self.comparison_df)

    def load_data(self, df):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for _, row in df.iterrows():
            status = row["Status"]
            tag = "match" if status == "✅" else "mismatch"
            values = row.tolist()
            # Insert the row with the appropriate tag
            self.tree.insert("", "end", values=values, tags=(tag,))
            # Change the text color of Part Number 1 and Part Number 2 based on the status
            if status == "✅":
                self.tree.tag_configure(tag, foreground="green")
            elif status == "❌":
                self.tree.tag_configure(tag, foreground="red")


    def export_to_excel(self):
        """
        Export the current view to Excel. If filters are selected, export the filtered view;
        otherwise export the full comparison. Prompts the user for a save location.
        Also writes a default "Comparison_Results.xlsx" adjacent to the script as a quick export.
        """
        if self.comparison_df is None:
            messagebox.showerror("Error", "No comparison data to export yet. Please upload and compare files first.")
            return

        # Recreate the filtered view based on current selections
        df_to_export = self.comparison_df.copy()
        if self.module_var.get():
            df_to_export = df_to_export[df_to_export["Module"] == self.module_var.get()]
        if self.did_var.get():
            df_to_export = df_to_export[df_to_export["DID Code"] == self.did_var.get()]

        if df_to_export.empty:
            messagebox.showwarning("Nothing to export", "Your current filter results in no rows. Clear filters or choose another filter.")
            return

        # Ask user where to save
        file_path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel Files", "*.xlsx")],
            title="Save Comparison Results As"
        )
        if file_path:
            try:
                # Ensure column order matches what is shown in the table
                desired_cols = ["Node", "Module", "DID Code", "DID Name", "Part Number 1", "Part Number 2", "Status"]
                cols = [c for c in desired_cols if c in df_to_export.columns]
                df_to_export[cols].to_excel(file_path, index=False)
                messagebox.showinfo("Exported", f"Saved to:\n{file_path}")
            except Exception as e:
                messagebox.showerror("Export failed", f"Could not save Excel file:\n{e}")
        else:
            # User cancelled dialog; do nothing
            return

if __name__ == "__main__":
    root = tk.Tk()
    app = DIDDataExtractorApp(root)
    root.mainloop()

