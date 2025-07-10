import os
import pandas as pd
import xlwings as xw
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading

class ExcelProcessorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Power BI Data Processor")
        self.root.geometry("500x680")
        self.root.resizable(False, False)

        # Variables
        self.excel_path = tk.StringVar()
        self.csv_folder = tk.StringVar()
        self.country_name = tk.StringVar()
        self.time_period = tk.StringVar()
        self.save_location = tk.StringVar()

        # --- Configuration Data ---
        self.default_start_cell = "C3"
        self.appending_groups = {
            "OBS": {
                "files": ["OBS.csv", "OBS_age.csv", "OBS_gender.csv", "OBS_income.csv", "OBS_location.csv"],
                "start_cell": "D3", "sheet": "OBS", "add_total_files": ["OBS.csv"]
            },
            "Occasion Size": {
                "files": ["BD7_Occasion.csv", "BD7_Occasion_age.csv", "BD7_Occasion_Gender.csv", "BD7_Occasion_Income.csv", "BD7_Occasion_Location.csv"],
                "start_cell": "C3", "sheet": "Occasion Size", "add_total_files": ["BD7_Occasion.csv"]
            }
        }
        self.sheet_mapping = {
            "Total_kpis.csv": {"sheet": "Total", "add_total": False},
            "Total_gender.csv": {"sheet": "Gender", "add_total": False},
            "Total_age.csv": {"sheet": "Age", "add_total": False},
            "total_location.csv": {"sheet": "Location", "add_total": False},
            "Total_income.csv": {"sheet": "Income", "add_total": False},
            "Pmds_total.csv": {"sheet": "Total PMDS", "add_total": False},
            "pmds_gender.csv": {"sheet": "Gender PMDS", "add_total": False},
            "pmds_location.csv": {"sheet": "Location PMDS", "add_total": False},
            "pmds_age.csv": {"sheet": "Age PMDS", "add_total": False},
            "pmds_income.csv": {"sheet": "Income PMDS", "add_total": False},
            "Imagery.csv": {"sheet": "Imagery", "add_total": True},
            "IMF.csv": {"sheet": "IMF", "add_total": True},
            "BIP.csv": {"sheet": "BIP", "add_total": True},
            "TBCA_media.csv": {"sheet": "TBCA_media_raw", "add_total": True, "start_cell": "C3"},
        }
        self.country_cell_mapping = {
            "Base size": ["A2"],
            "Overview": ["C1"],
            "Deep dive template": ["J1", "J10", "J41", "J73", "J105", "J137"],
            "PMDS - By Demog": ["A1"],
            "Brand Health - 1": ["B1"],
            "Brand Health - 2": ["A1"],
            "TBCA_mediamix": ["A1"],
            "PMDS - 1": ["B1"],
            "PMDS - 2": ["A1"],
            "OBS - 1": ["A6", "A25"],
            "OBS - 2": ["A1", "A2", "A17"],
            "Total Imagery": ["A6", "B6"],
            "Total BIP": ["A6", "B6"],
            "Total IMF": ["B6", "A6"],
            "PMDS - Overview":["B1","G1"]
        }

        self.setup_ui()

    def setup_ui(self):
        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)

        title_frame = ttk.Frame(main_frame)
        title_frame.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(title_frame, text="Control Panel", font=('Arial', 14, 'bold')).pack(side=tk.LEFT)
        ttk.Button(title_frame, text="📘 Instructions", command=self.show_instructions_window).pack(side=tk.RIGHT)

        inputs_frame = ttk.LabelFrame(main_frame, text="1. Select Files & Folders")
        inputs_frame.pack(fill=tk.X, pady=5)
        self.create_browse_row(inputs_frame, "Excel Template:", self.excel_path, self.browse_excel)
        self.create_browse_row(inputs_frame, "Country CSV Folder:", self.csv_folder, self.browse_csv_folder)
        self.create_browse_row(inputs_frame, "Save Location:", self.save_location, self.browse_save_location)

        params_frame = ttk.LabelFrame(main_frame, text="2. Set Parameters")
        params_frame.pack(fill=tk.X, pady=5)
        ttk.Label(params_frame, text="Country Name (e.g., UK, IT):").pack(anchor=tk.W, padx=5, pady=(5,0))
        ttk.Entry(params_frame, textvariable=self.country_name).pack(fill=tk.X, expand=True, padx=5, pady=5)

        ttk.Label(params_frame, text="Time Period (e.g., Q1'25):").pack(anchor=tk.W, padx=5, pady=(5,0))
        ttk.Entry(params_frame, textvariable=self.time_period).pack(fill=tk.X, expand=True, padx=5, pady=5)

        self.process_btn = ttk.Button(main_frame, text="🚀 Process Files", command=self.start_processing)
        self.process_btn.pack(fill=tk.X, pady=15)

        log_frame = ttk.LabelFrame(main_frame, text="Processing Log")
        log_frame.pack(fill=tk.BOTH, expand=True)
        log_text_frame = ttk.Frame(log_frame)
        log_text_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.log_text = tk.Text(log_text_frame, height=8, font=('Consolas', 9), wrap=tk.WORD)
        scrollbar = ttk.Scrollbar(log_text_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def create_browse_row(self, parent, label_text, var, cmd):
        row_frame = ttk.Frame(parent)
        row_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Label(row_frame, text=label_text).pack(anchor=tk.W)
        entry_frame = ttk.Frame(row_frame)
        entry_frame.pack(fill=tk.X)
        ttk.Entry(entry_frame, textvariable=var).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(entry_frame, text="Browse...", command=cmd).pack(side=tk.RIGHT, padx=(5,0))

    def show_instructions_window(self):
        win = tk.Toplevel(self.root)
        win.title("Instructions for Power BI Data Processing")
        win.geometry("600x480")
        win.resizable(False, False)
        win.transient(self.root)

        main_frame = ttk.Frame(win, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(main_frame, text="How to Use This Tool", font=("Arial", 16, "bold")).pack(anchor="w", pady=(0, 10))

        ttk.Label(main_frame, text="Part 1: Preparing Your Files", font=("Arial", 12, "bold")).pack(anchor="w", pady=(10, 5))
        instructions1 = (
            "The key to success is organizing your files correctly before using this tool.\n\n"
            "1. Create Country Folders: For each country (e.g., 'UK', 'France'), create its own separate folder.\n\n"
            "2. Export from Power BI: In your report, right-click on a visual and choose 'Export data'.\n\n"
            "3. Save CSVs Correctly: Save all exported CSV files for a single country into its dedicated folder.\n\n"
            "4. DO NOT RENAME FILES: The tool identifies files by their original names. Renaming them will cause the process to fail."
        )
        ttk.Label(main_frame, text=instructions1, wraplength=550, justify=tk.LEFT).pack(anchor="w", padx=10)

        ttk.Label(main_frame, text="Part 2: Using the Tool", font=("Arial", 12, "bold")).pack(anchor="w", pady=(15, 5))
        instructions2 = (
            "1. Select Template: Click 'Browse' to select your master Excel template (.xlsx).\n\n"
            "2. Select CSV Folder: Choose the specific country folder (e.g., 'UK') that you prepared.\n\n"
            "3. Enter Country Name: Type the name of the country you are processing.\n\n"
            "4. Enter Time Period: Specify the reporting period for the data (e.g., Q1'25).\n\n"
            "5. Choose Save Location: Select a folder where the final report will be saved.\n\n"
            "6. Begin Processing: Click 'Process Files' and monitor the log for progress."
        )
        ttk.Label(main_frame, text=instructions2, wraplength=550, justify=tk.LEFT).pack(anchor="w", padx=10)

        ttk.Button(main_frame, text="Close", command=win.destroy).pack(pady=20)

    def browse_excel(self):
        filename = filedialog.askopenfilename(title="Select.Excel Template File", filetypes=[("Excel files", "*.xlsx")])
        if filename:
            self.excel_path.set(filename)
            self.log(f"Selected.Excel: {os.path.basename(filename)}")

    def browse_csv_folder(self):
        folder = filedialog.askdirectory(title="Select Country-Specific CSV Folder")
        if folder:
            self.csv_folder.set(folder)
            self.log(f"Selected CSV Folder: {os.path.basename(folder)}")

    def browse_save_location(self):
        folder = filedialog.askdirectory(title="Select Output Save Location")
        if folder:
            self.save_location.set(folder)
            self.log(f"Save location set: {folder}")

    def log(self, message):
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()

    def start_processing(self):
        if not all([self.excel_path.get(), self.csv_folder.get(), self.country_name.get(), self.time_period.get(), self.save_location.get()]):
            messagebox.showerror("Input Missing", "Please complete all fields in the control panel.")
            return
        self.process_btn.config(state='disabled', text='Processing...')
        self.log_text.delete(1.0, tk.END)
        self.log("="*50 + "\nPROCESSING STARTED\n" + "="*50)
        threading.Thread(target=self.process_files, daemon=True).start()

    def process_files(self):
        try:
            app = xw.App(visible=False)
            wb = app.books.open(self.excel_path.get())
            try:
                self.log(f"Processing country: {self.country_name.get()}")
                for group_name, config in self.appending_groups.items():
                    self.preprocess_group_and_display(group_name, config, wb)
                self.process_base_size_files(wb)
                self.process_individual_csvs(wb)
                self.change_country(wb, self.country_name.get())
                filename = f"{self.country_name.get()} Brand Performance Tracker_{self.time_period.get()}.xlsx"
                output_file = os.path.join(self.save_location.get(), filename)
                wb.save(output_file)
                self.log("\n" + "="*50 + f"\nSUCCESS! File saved as: {filename}\n" + "="*50)
                messagebox.showinfo("Processing Complete", f"Success! The file has been saved as:\n{filename}")
            finally:
                wb.close()
                app.quit()
        except Exception as e:
            self.log("\n" + "="*50 + f"\nERROR: {e}\n" + "="*50)
            messagebox.showerror("Processing Error", f"An error occurred: {e}\nPlease check the log for details.")
        finally:
            self.process_btn.config(state='normal', text='🚀 Process Files')

    def insert_dataframe(self, sheet, df, start_cell):
        sheet.range(start_cell).expand("table").clear_contents()
        sheet.range(start_cell).options(index=False, header=False).value = df

    def preprocess_group_and_display(self, group_name, config, wb):
        self.log(f"Processing group: {group_name}")
        base_df = None
        for i, file in enumerate(config["files"]):
            path = os.path.join(self.csv_folder.get(), file)
            if not os.path.exists(path):
                self.log(f"  - File not found, skipping: {file}")
                continue
            df = pd.read_csv(path)
            df.insert(0, "Country", self.country_name.get())
            if i == 0 and file in config.get("add_total_files", []):
                df.insert(2, "Total", "Total")
                base_df = df.copy()
            else:
                df = df.rename(columns={df.columns[2]: "Total"}).reindex(columns=base_df.columns, fill_value="")
                base_df = pd.concat([base_df, df], ignore_index=True)
        if base_df is not None:
            self.insert_dataframe(wb.sheets[config["sheet"]], base_df.iloc[1:], config["start_cell"])
            self.log(f"  - Written combined data to '{config['sheet']}'")

    def process_individual_csvs(self, wb):
        self.log("Processing individual CSVs...")
        for csv_file, config in self.sheet_mapping.items():
            csv_path = os.path.join(self.csv_folder.get(), csv_file)
            if not os.path.exists(csv_path):
                self.log(f"  - File not found, skipping: {csv_file}")
                continue
            df = pd.read_csv(csv_path, skiprows=1)
            df.insert(0, "Country", self.country_name.get())
            if config.get("sheet") == "TBCA_media_raw":
                df.insert(2, "Total", "Total")
            elif config.get("add_total"):
                df.insert(2, "Total", "Total")
            start_cell = config.get("start_cell", self.default_start_cell)
            self.insert_dataframe(wb.sheets[config["sheet"]], df, start_cell)
            self.log(f"  - Written {csv_file} to '{config['sheet']}'")

    def process_base_size_files(self, wb):
        self.log("Processing base size files (OBS-style with Total at index 5)...")
        base_files = sorted([f for f in os.listdir(self.csv_folder.get()) if f.startswith("Baze_size_")])
        total_file = "Baze_size_total.csv"
        if total_file in base_files:
            base_files.remove(total_file)
            base_files.insert(0, total_file)
        base_df = None
        for file in base_files:
            path = os.path.join(self.csv_folder.get(), file)
            if not os.path.exists(path):
                continue
            df = pd.read_csv(path)
            df.insert(0, "Country", self.country_name.get())
            if file.lower() == total_file:
                df.insert(5, "Total", "Total")
                base_df = df.copy()
            else:
                if base_df is None:
                    continue
                df = df.rename(columns={df.columns[5]: "Total"}).reindex(columns=base_df.columns, fill_value="")
                base_df = pd.concat([base_df, df], ignore_index=True)
        if base_df is not None:
            self.insert_dataframe(wb.sheets["Base_size_raw"], base_df.iloc[1:], "C3")
            self.log("  - Combined base size files written to 'Base_size_raw'")

    def change_country(self, wb, country_name):
        self.log(f"Updating country name to '{country_name}'...")
        for sheet in wb.sheets:
            cells = self.country_cell_mapping.get(sheet.name)
            if cells:
                if isinstance(cells, str):
                    cells = [cells]
                for cell in cells:
                    try:
                        sheet.range(cell).value = country_name
                    except Exception as e:
                        self.log(f"  - Error updating {sheet.name} at {cell}: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = ExcelProcessorGUI(root)
    root.mainloop()
