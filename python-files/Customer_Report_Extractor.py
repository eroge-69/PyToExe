
import pandas as pd
import re
import os
from tkinter import Tk, Label, Entry, Button, filedialog, messagebox, StringVar
from pathlib import Path
from tkinter import ttk

def extract_data_from_rpt(file_path):
    with open(file_path, 'r', errors='ignore') as f:
        lines = f.read().splitlines()

    clean_lines = [line for line in lines if not re.match(r'^[-=]+$', line.strip()) and not re.search(r'report|total|summary', line, re.IGNORECASE)]

    header_index = None
    for i, line in enumerate(clean_lines):
        if len(re.split(r'\s{2,}', line.strip())) >= 3:
            header_index = i
            break

    if header_index is None:
        return pd.DataFrame()

    header = re.split(r'\s{2,}', clean_lines[header_index].strip())
    data_lines = clean_lines[header_index + 1:]
    rows = []

    for line in data_lines:
        if not line.strip():
            continue
        cols = re.split(r'\s{2,}', line.strip())
        if len(cols) == len(header):
            rows.append(cols)

    df = pd.DataFrame(rows, columns=header)
    df.columns = [col.strip().lower() for col in df.columns]
    return df

def merge_duplicate_records(df, unique_keys):
    df = df.copy()
    df["remarks"] = ""

    merged_rows = []
    for _, group in df.groupby(unique_keys):
        if group.empty:
            continue

        representative = group.iloc[0].copy()
        remark_msgs = []

        for col in df.columns:
            if col in unique_keys or col == "remarks":
                continue

            unique_vals = group[col].dropna().unique()
            if len(unique_vals) > 1:
                remark_msgs.append(f"{col}: {', '.join(unique_vals)}")

        if remark_msgs:
            representative["remarks"] = "; ".join(remark_msgs)

        merged_rows.append(representative)

    return pd.DataFrame(merged_rows)

class ReportExtractorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("RPT File Search Tool")
        self.root.geometry("550x330")
        self.root.resizable(False, False)

        self.file_paths = []
        self.output_dir = StringVar()
        self.output_dir.set(str(Path.home() / "Desktop"))

        Label(root, text="Step 1: Select .rpt Files").pack(pady=5)
        Button(root, text="Select Files", command=self.select_files, width=25).pack()
        self.file_label = Label(root, text="No files selected")
        self.file_label.pack()

        Label(root, text="Step 2: Choose Output Folder").pack(pady=5)
        folder_frame = ttk.Frame(root)
        folder_frame.pack()
        self.output_entry = Entry(folder_frame, textvariable=self.output_dir, width=50)
        self.output_entry.pack(side="left", padx=5)
        Button(folder_frame, text="Browse", command=self.select_output_folder).pack(side="left")

        Label(root, text="Step 3: Enter Detail to Search (PAN / Aadhaar / Account / ID)").pack(pady=5)
        self.search_entry = Entry(root, width=50)
        self.search_entry.pack()

        Button(root, text="Process", command=self.process_files, width=20).pack(pady=15)

    def select_files(self):
        self.file_paths = filedialog.askopenfilenames(title="Select .rpt files", filetypes=[("Report Files", "*.rpt")])
        self.file_label.config(text=f"{len(self.file_paths)} file(s) selected" if self.file_paths else "No files selected")

    def select_output_folder(self):
        folder = filedialog.askdirectory(title="Select Output Folder")
        if folder:
            self.output_dir.set(folder)

    def process_files(self):
        if not self.file_paths:
            messagebox.showerror("Error", "Please select at least one .rpt file.")
            return
        if not self.output_dir.get():
            messagebox.showerror("Error", "Please select an output folder.")
            return

        search_value = self.search_entry.get().strip().lower()
        if not search_value:
            messagebox.showerror("Error", "Please enter a customer detail to search.")
            return

        dataframes = []
        for file in self.file_paths:
            df = extract_data_from_rpt(file)
            if not df.empty:
                df['__source_file__'] = Path(file).name
                dataframes.append(df)

        if not dataframes:
            messagebox.showinfo("Result", "No valid data found in the selected files.")
            return

        combined_df = pd.concat(dataframes, ignore_index=True, sort=False).fillna("")
        combined_df.columns = [col.strip().lower() for col in combined_df.columns]

        filtered_df = combined_df[
            combined_df.apply(lambda row: search_value in row.astype(str).str.lower().tolist(), axis=1)
        ]

        if filtered_df.empty:
            messagebox.showinfo("Result", "No matching records found.")
            return

        possible_keys = ['pan', 'aadhaar', 'aadhar', 'account', 'account no', 'account number', 'cust id', 'customer id']
        unique_keys = [col for col in filtered_df.columns if any(key in col for key in possible_keys)]

        if not unique_keys:
            unique_keys = filtered_df.columns[:1].tolist()

        merged_df = merge_duplicate_records(filtered_df, unique_keys)

        # Fill missing values in first row from lower rows
        for col in merged_df.columns:
            if pd.isna(merged_df.at[0, col]) or merged_df.at[0, col] == "":
                for row in range(1, len(merged_df)):
                    val = merged_df.at[row, col]
                    if pd.notna(val) and val != "":
                        merged_df.at[0, col] = val
                        break

        # Keep only the first row
        merged_df = merged_df.iloc[:1]

        output_path = os.path.join(self.output_dir.get(), "Customer_Details_Merged.xlsx")
        merged_df.to_excel(output_path, index=False)
        messagebox.showinfo("Success", f"Excel file saved:
{output_path}")

def main():
    root = Tk()
    app = ReportExtractorApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
