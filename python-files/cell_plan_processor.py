import zipfile
import os
import re
import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox
from datetime import datetime

class CellPlanProcessor:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Cell Plan Processor")
        self.root.geometry("400x200")
        self.zip_file_path = None
        self.date = None
        self.output_dir = os.path.join(os.getcwd(), "output_files")
        os.makedirs(self.output_dir, exist_ok=True)

        self.setup_gui()

    def setup_gui(self):
        tk.Button(self.root, text="Select Zip File", command=self.select_zip_file).pack(pady=10)
        tk.Button(self.root, text="Process File", command=self.process_file, state="disabled").pack(pady=10)
        tk.Button(self.root, text="Download Processed File", command=lambda: self.download_file("processed"), state="disabled").pack(pady=10)
        tk.Button(self.root, text="Download Final File", command=lambda: self.download_file("final"), state="disabled").pack(pady=10)

        self.process_button = self.root.winfo_children()[1]
        self.download_processed_button = self.root.winfo_children()[2]
        self.download_final_button = self.root.winfo_children()[3]

    def select_zip_file(self):
        self.zip_file_path = filedialog.askopenfilename(filetypes=[("Zip files", "*.zip")])
        if self.zip_file_path:
            # Extract date from filename
            filename = os.path.basename(self.zip_file_path)
            date_match = re.search(r'(\d{1,2})_([A-Za-z]+)_(\d{4})', filename)
            if date_match:
                day, month, year = date_match.groups()
                try:
                    self.date = datetime.strptime(f"{day} {month} {year}", "%d %B %Y").strftime("%d_%B_%Y")
                    messagebox.showinfo("Success", f"Zip file selected. Date extracted: {self.date}")
                    self.process_button.config(state="normal")
                except ValueError:
                    messagebox.showerror("Error", "Invalid date format in filename.")
                    self.zip_file_path = None
            else:
                messagebox.showerror("Error", "Filename does not match expected format (e.g., Updated_CellRefFile_16_June_2025.zip).")
                self.zip_file_path = None

    def unzip_file(self):
        with zipfile.ZipFile(self.zip_file_path, 'r') as zip_ref:
            zip_ref.extractall(self.output_dir)
        print("File unzipped successfully.")

    def process_file(self):
        try:
            # Step 1: Unzip the file
            self.unzip_file()

            # Step 2: Read the extracted CSV
            input_file = os.path.join(self.output_dir, f"Updated_CellRefFile_{self.date}.csv")
            if not os.path.exists(input_file):
                raise FileNotFoundError(f"CSV file {input_file} not found after unzipping.")

            df = pd.read_csv(input_file)
            num_rows = df.shape[0]
            num_columns = df.shape[1]
            print(f"Number of input file rows: {num_rows}")
            print(f"Number of input file columns: {num_columns}")

            # Step 3: Process the DataFrame (from Part-2)
            df[['SAP ID', 'Sector ID']] = df['Cell Name'].str.split('_', n=1, expand=True)
            mapping_dict_1 = {1: 0, 2: 1, 3: 2, 7: 16, 8: 17, 9: 18}
            df['Sector ID'].fillna(-1, inplace=True)
            df['Sector ID'] = df['Sector ID'].astype(int)
            df['Cell_ID'] = df['Sector ID'].map(mapping_dict_1)
            df['Cell_ID'].fillna(-1, inplace=True)
            df['Cell_ID'] = df['Cell_ID'].astype(int)

            mapping_dict_2 = {0: 60, 1: 61, 2: 62, 16: 70, 17: 71, 18: 72, 48: 63, 49: 64, 50: 65}
            df['Cell Name in MYCOM'] = df['Cell_ID'].map(mapping_dict_2)
            df['Cell Name in MYCOM'].fillna(-1, inplace=True)
            df['Cell Name in MYCOM'] = df['Cell Name in MYCOM'].astype(int)
            df['CellName'] = df.apply(lambda row: f"{row['SAP ID']}_{row['Cell Name in MYCOM']}", axis=1)

            df.rename(columns={
                'Site Name': 'SiteID', 'Latitude': 'Latitude_Sector', 'Longitude': 'Longitude_Sector',
                'Beamwidth': 'HorizBeamwidth', 'eNodeb ID_Dec': 'gNodeBID', 'Azimuth ': 'Azimuth'
            }, inplace=True)

            df['mcc'] = df['ECGI_Hex'].str[:3]
            df['mnc'] = df['ECGI_Hex'].str[3:6]
            df['CoverageType'] = 'Macro'
            df['Technology'] = '5G'
            df['RF_Solution'] = 'MACRO'
            df['On_Air'] = 'On'

            earfcn_range_mapping = {634080: 10, 156750: 15, 632064: 10}
            df['expected_cell_range'] = df['DL EARFCN'].map(earfcn_range_mapping)

            output_columns = ['CellName', 'Cell_ID', 'Latitude_Sector', 'Longitude_Sector', 'CoverageType', 'SiteID', 'Azimuth',
                             'HorizBeamwidth', 'Technology', 'gNodeBID', 'RF_Solution', 'mcc', 'mnc', 'Circle', 'State', 'City',
                             'On_Air', 'dlChannelBandwidth', 'DL EARFCN', 'Spectrum Band', 'expected_cell_range']
            processed_df = df[output_columns]

            original_count = len(processed_df)
            processed_df = processed_df[processed_df['Cell_ID'] != -1]
            deleted_count = original_count - len(processed_df)
            print("***********************************")
            print("Number of rows deleted:", deleted_count)
            print("***********************************")
            print(f"Number of processed file rows: {processed_df.shape[0]}")
            print(f"Number of processed file columns: {processed_df.shape[1]}")

            processed_output_path = os.path.join(self.output_dir, f"processed_cell_plan_{self.date}.csv")
            processed_df.to_csv(processed_output_path, index=False)
            print(f"Processed data saved to '{processed_output_path}'")

            # Step 4: Further processing (from Part-2)
            df1 = pd.read_csv(processed_output_path)
            circle_filter = ['JK', 'MP', 'RJ', 'UW', 'HP']
            df2 = df1[df1['Circle'].isin(circle_filter)].copy()
            fixed_values = {'dlChannelBandwidth': 30, 'DL EARFCN': 632064, 'Spectrum Band': 'N3500', 'expected_cell_range': 10}
            df2 = df2.assign(**fixed_values)
            cell_id_mapping = {0: 48, 1: 49, 2: 50, 16: 48, 17: 49, 18: 50}
            df2['Cell_ID'] = df2['Cell_ID'].replace(cell_id_mapping)
            char_mapping = {"_60": "_63", "_61": "_64", "_62": "_65", "_70": "_63", "_71": "_64", "_72": "_65"}
            df2['CellName'] = df2['CellName'].apply(lambda x: reduce(lambda s, kv: s.replace(kv[0], kv[1]), char_mapping.items(), x))
            df2.drop_duplicates(subset='CellName', inplace=True)
            df1 = pd.concat([df1, df2], ignore_index=True)
            df1.drop_duplicates(subset='CellName', inplace=True)

            final_output_path = os.path.join(self.output_dir, f"Final_CellPlan_{self.date}.csv")
            df1.to_csv(final_output_path, index=False)
            print(f"Final data saved to '{final_output_path}'")

            messagebox.showinfo("Success", "File processed successfully!")
            self.download_processed_button.config(state="normal")
            self.download_final_button.config(state="normal")

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

    def download_file(self, file_type):
        if file_type == "processed":
            default_filename = f"processed_cell_plan_{self.date}.csv"
            file_path = os.path.join(self.output_dir, default_filename)
        else:
            default_filename = f"Final_CellPlan_{self.date}.csv"
            file_path = os.path.join(self.output_dir, default_filename)

        if os.path.exists(file_path):
            save_path = filedialog.asksaveasfilename(defaultextension=".csv", initialfile=default_filename, filetypes=[("CSV files", "*.csv")])
            if save_path:
                import shutil
                shutil.copy(file_path, save_path)
                messagebox.showinfo("Success", f"File saved to {save_path}")
        else:
            messagebox.showerror("Error", f"{file_type.capitalize()} file not found.")

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    from functools import reduce
    app = CellPlanProcessor()
    app.run()
