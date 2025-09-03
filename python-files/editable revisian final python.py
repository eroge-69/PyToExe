#LATEST FIX CODE (CHECKPOINT: 1 sept)-> edit assignment cases
import os
import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
import numpy as np
import datetime
import pytz
from itertools import cycle
from openpyxl import load_workbook
from openpyxl.worksheet.table import Table, TableStyleInfo
import xlsxwriter
import re
 
# The timezone-aware current time is needed for accurate time elapsed calculations
CURRENT_TIME = datetime.datetime.now(pytz.timezone('Asia/Jakarta')).replace(tzinfo=None)
 
# Priority logic for HC (Hard Complaints)
def assign_priority_1(row):
    """
    Calculates priority for complaints based on elapsed time and status.
    This logic is applied to "carry over" complaints.
    """
    time_elapsed = (CURRENT_TIME - row['Created At']).total_seconds() / 3600
    status = row['Status'].lower()
    if status == "open":
        if time_elapsed < 1:
            return 1
    elif status == "in progress":
        if 16 <= time_elapsed < 18:
            return 5
        elif 22 <= time_elapsed < 24:
            return 6
    return None
 
# Priority Logic for Pusrol
def assign_priority_2(row):
    """
    Calculates priority for complaints based on elapsed time.
    This logic is applied to "not carry over" complaints.
    """
    time_elapsed = (CURRENT_TIME - row['Created At']).total_seconds() / 3600
    if 2 <= time_elapsed <= 4:
        return 2
    elif time_elapsed < 1:
        return 3
    return None
   
# Priority logic for Non-HC (ordinary cases)
def assign_priority_3(row):
    """
    Calculates priority for complaints based on elapsed time and status.
    This logic is applied to "non-carry over" complaints.
    """
    time_elapsed = (CURRENT_TIME - row['Created At']).total_seconds() / 3600
    status = row['Status'].lower()
    if "open" in status and time_elapsed < 3:
        return 9
    if "in progress" in status:
        if 22 <= time_elapsed < 24:
            return 7
        elif 83 <= time_elapsed < 85:
            return 8
    if "reopened" in status and time_elapsed < 3:
        return 10
    return None
 
# Regex pattern for agent labels
AGENT_LABEL_RE = re.compile(r"^(xo|cr)\.[a-z0-9_]+$", re.IGNORECASE)
 
def extract_xo_labels(label_str: str):
    """
    Extract only labels matching xo.* or cr.* from the full comma-separated list.
    Returns a list of valid agent labels, in the same order as they appear.
    """
    if pd.isna(label_str):
        return []
    labels_list = [lbl.strip().lower() for lbl in str(label_str).split(",") if lbl.strip()]
    xo_labels = [lbl for lbl in labels_list if re.match(r'^(xo|cr)\.[a-z0-9_]+$', lbl, re.IGNORECASE)]
    return xo_labels

def is_agent_hadir(agent_df: pd.DataFrame, label: str) -> bool:
    """
    Checks if an agent with a specific label is 'HADIR' (present).
    """
    if not label:
        return False
    # Check if the label is an agent's name and that agent's status is 'HADIR'
    return not agent_df[
        (agent_df["New Label"].str.lower() == label.lower()) &
        (agent_df["Status"].str.upper() == "HADIR")
    ].empty
 
def load_clean_csv(path):
    """Loads and cleans a CSV file."""
    df = pd.read_csv(path, encoding='utf-8-sig', sep=',')
    df.columns = df.columns.str.strip().str.replace('\ufeff', '', regex=True)
    df = df.dropna(how='all')
    return df
 
def load_clean_excel(path):
    """Loads and cleans an Excel file."""
    df = pd.read_excel(path)
    df.columns = df.columns.str.strip().str.replace('\ufeff', '', regex=True)
    df = df.dropna(how='all')
    return df
 
class ComplaintDistributionApp(tk.Tk):
    """
    The main application class for the complaint distribution tool.
    This GUI handles file loading, data processing, and exporting.
    """
    def __init__(self):
        super().__init__()
        self.title("XO Bucket Distributor — Clean & Runnable")
        self.geometry("800x400")
 
        self.df = None
       
        # UI variable to hold file paths
        self.hc_bucket_path = tk.StringVar()
        self.nonhc_bucket_path = tk.StringVar()
        self.pusrol_bucket_path = tk.StringVar()
        self.agent_path = tk.StringVar()
        self.cust_vocal = tk.StringVar()
       
        # New UI variables for export paths
        self.export_path1 = tk.StringVar()
        self.export_path2 = tk.StringVar()
        self.export_path3 = tk.StringVar()
       
        self.create_widgets()
 
    def create_widgets(self):
        """Creates the GUI widgets and layout as per the provided image."""
        main_frame = tk.Frame(self, padx=10, pady=10)
        main_frame.pack(fill="both", expand=True)
 
        # Helper function to create a file selection row
        def create_file_row(parent, label_text, var, filetypes):
            row = tk.Frame(parent)
            row.pack(fill="x", pady=2)
            tk.Label(row, text=label_text, width=25, anchor="w").pack(side="left")
            entry = tk.Entry(row, textvariable=var)
            entry.pack(side="left", fill="x", expand=True, padx=5)
            tk.Button(row, text="Browse", command=lambda: var.set(filedialog.askopenfilename(filetypes=filetypes))).pack(side="right")
       
        # File path rows
        create_file_row(main_frame, "HC Bucket to distribute:", self.hc_bucket_path, [("CSV Files", "*.csv")])
        create_file_row(main_frame, "Non-HC Bucket to distribute:", self.nonhc_bucket_path, [("CSV Files", "*.csv")])
        create_file_row(main_frame, "Pusrol Bucket to distribute:", self.pusrol_bucket_path, [("CSV Files", "*.csv")])
        create_file_row(main_frame, "Data Agent:", self.agent_path, [("Excel Files", "*.xlsx")])
        create_file_row(main_frame, "Customer Vocal:", self.cust_vocal, [("CSV Files", "*.csv")])
 
        # Export path rows
        create_file_row(main_frame, "First CSV Export Path:", self.export_path1, [("CSV Files", "*.csv")])
        create_file_row(main_frame, "Second CSV Export Path:", self.export_path2, [("CSV Files", "*.csv")])
        create_file_row(main_frame, "Third CSV Export Path:", self.export_path3, [("Excel Files", "*.xlsx")])
       
        # Export Button
        export_button = tk.Button(main_frame, text="Export Link", command=self.export_all)
        export_button.pack(pady=20)
   
    def export_all(self):
        """
        Performs all data processing and exports the three dataframes
        to the specified file paths. This function now includes the
        Excel table creation for the third file.
        """
        # Validate all file paths are provided
        required_paths = [self.hc_bucket_path, self.nonhc_bucket_path,
                          self.pusrol_bucket_path, self.agent_path, self.cust_vocal,
                          self.export_path1, self.export_path2, self.export_path3]
        if not all(path.get() for path in required_paths):
            messagebox.showwarning("Warning", "Please provide all input and export file paths.")
            return
 
        try:
            # --- Data Loading and Preparation ---
            jakarta = pytz.timezone('Asia/Jakarta')
            dt_now_jakarta = datetime.datetime.now(jakarta)
            today_column_name = f'Jam {dt_now_jakarta.strftime("%H").lstrip("0")}'
 
            df_hc_new = load_clean_csv(self.hc_bucket_path.get())
            df_nonhc_new = load_clean_csv(self.nonhc_bucket_path.get())
            df_pusrol_new = load_clean_csv(self.pusrol_bucket_path.get())
            df_agent_new = load_clean_excel(self.agent_path.get())
            df_cust_vocal = load_clean_csv(self.cust_vocal.get())
 
            # Remove rows where 'Labels' contains '02'
            #for df_item in [df_hc_new, df_nonhc_new, df_pusrol_new]:
                #if 'Labels' in df_item.columns:
                    #df_item = df_item[~df_item['Labels'].astype(str).str.contains('02', na=False)]
                    
            df_hc_new = df_hc_new[~df_hc_new['Labels'].astype(str).str.contains(r'02|exp|xor', case=False, na=False)]
            df_nonhc_new = df_nonhc_new[~df_nonhc_new['Labels'].astype(str).str.contains(r'02|exp|xor', case=False, na=False)]
            df_pusrol_new = df_pusrol_new[~df_pusrol_new['Labels'].astype(str).str.contains(r'02|exp|xor', case=False, na=False)]

 #take out label lain

            # Combine new buckets and tag
            df_hc_new['bucket_type'] = 'HC'
            df_nonhc_new['bucket_type'] = 'NonHC'
            df_pusrol_new['bucket_type'] = 'Pusrol'
            df_ready_new = pd.concat([df_hc_new, df_nonhc_new, df_pusrol_new], ignore_index=True)
 
            # Assign Priority
            df_ready_new['Created At'] = pd.to_datetime(df_ready_new['Created At'], errors='coerce').dt.tz_localize(None)
            df_ready_new['Status'] = df_ready_new['Status'].astype(str)
            df_ready_new['Priority'] = df_ready_new.apply(
                lambda row: assign_priority_1(row) if row['bucket_type'] == 'HC' else
                            (assign_priority_2(row) if row['bucket_type'] == 'Pusrol' else assign_priority_3(row)),
                axis=1
            )
            df_ready_new['Priority'] = df_ready_new['Priority'].fillna(99).astype(int)
            df_ready_new['logon_id'] = df_ready_new['Customer Id']
            df_ready_new = df_ready_new[df_ready_new['Case Subcategory'] != 'Retur - Pengisian RMA Manual'].copy().reset_index(drop=True)
            df_ready_new['vocal_or_not'] = np.where(df_ready_new['logon_id'].isin(df_cust_vocal['user_name']), 'Vocal', 'Not Vocal')
           
            # Main Processing Logic (Consolidated) 
           
            # Prepare Agent data
            df_agent_new = df_agent_new.copy()
            df_agent_new = df_agent_new[df_agent_new['Status'].str.lower() == 'hadir'].reset_index(drop=True)
            # Keep only needed columns
            df_agent_new = df_agent_new[['Nama Lengkap', 'Online', 'Akun', 'New Label', 'Email Agent',
                             'XO Label', 'Status', 'Define', today_column_name]].copy()
           # Split out hadir vs. non-hadir for clarity
            df_agents_active = df_agent_new[df_agent_new[today_column_name] == 1].reset_index(drop=True)   # can receive NEW buckets
            df_agents_inactive = df_agent_new[df_agent_new[today_column_name] == 0].reset_index(drop=True) # keep old carry-over buckets only

            # CR vs non-CR
            df_agent_cr = df_agent_new[df_agent_new['XO Label'] == 'CR'].reset_index(drop=True)
            df_agent = df_agent_new[df_agent_new['XO Label'] != 'CR'].reset_index(drop=True)
            # Flagging complaints for distribution
            df_vocal_cust = df_ready_new[
                (df_ready_new['vocal_or_not'] == 'Vocal') |
                (df_ready_new['Case Subcategory'] == 'Retur Project')
            ].copy().reset_index(drop=True)

             
            exclude_xo_subcat = df_ready_new['Case Subcategory'].isin([
                '3PL - Keterlambatan pengiriman oleh Logistic Partner', '3PL - Sanggah produk telah diterima', '3PL - Pengiriman Terhambat karena Customer', '3PL - Kendala pengiriman', '3PL - Keterlambatan Pengiriman Sameday', 'Sameday - Kendala Pengiriman',
                '3PL - Keterlambatan pengiriman dengan status D', '3PL- Pengiriman Terhambat karena Customer dengan Status D', '3PL - Gagal Trade-in (tidak sesuai TnC)', 'Sameday - Pengiriman Terhambat karena Customer',
                'Pick Up - Kendala tracking order', 'Sameday - Pengiriman Terhambat Karena Customer Dengan Status D', 'Fulfillment - Keterlambatan pengiriman karena fulfillment by Merchant Partner',
                '3PL - Request update status order (penambahan poin Blibli reward)', 'Fulfillment - Keterlambatan pengiriman karena fulfillment by Warehouse', 'Big Product - Sanggah produk telah diterima (Warehouse)',
                'Big Product - Keterlambatan pengiriman barang warehouse', '3PL - Biaya COD tidak ditagihkan/tidak sesuai', '3PL - Pengiriman Terhambat karena Customer with Status D', 'BES - Kendala pengiriman',
                'BES - Keterlambatan pengiriman', 'BES - Keterlambatan pengiriman with status D', 'BES - Pengiriman Terhambat karena Customer', 'BES - Pengiriman Terhambat karena Customer with Status D',
                'BES - Sanggah produk telah diterima', 'BES - Request waktu pengiriman Tukar Tambah', '(OPS-CS) Followup Customer', 'Merchant Join - Request registrasi via Seller Care'
            ])
            df_ready = df_ready_new[~exclude_xo_subcat & (df_ready_new['vocal_or_not'] != 'Vocal') & (df_ready_new['Case Subcategory'] != 'Retur Project')].copy().reset_index(drop=True)
            df_ready['xo_labels'] = df_ready['Labels'].apply(extract_xo_labels)

            def pick_label_from_list(xo_labels):
            # Scan in order until a hadir agent is found
                for lbl in xo_labels:
                    if is_agent_hadir(df_agent_new, lbl):
                        return lbl
                return None
            
            df_ready['New Label'] = df_ready['xo_labels'].apply(pick_label_from_list)
            df_ready['is_carry_over'] = df_ready['New Label'].notna()
            df_to_distribute = df_ready[~df_ready['is_carry_over']].copy()
            df_carry_over   = df_ready[df_ready['is_carry_over']].copy()

            # --- NEW LOGIC: Assign agent and email for carry-over cases ---
            if not df_carry_over.empty:
    # Use the label already chosen earlier for carry-over (do NOT overwrite)
                df_carry_over['New Label'] = (
                    df_carry_over['New Label']  # assumed set earlier from first->last->middle HADIR logic
                    .astype(str).str.strip().str.lower()
                )
                df_carry_over['xo_agent'] = df_carry_over['New Label'].str.split('.').str[1]

                # Look up email from ALL HADIR agents (df_agent_new), not just active-now
                df_agent_lookup = df_agent_new[['New Label', 'Email Agent']].copy()
                df_agent_lookup['New Label'] = df_agent_lookup['New Label'].str.strip().str.lower()

                df_carry_over = df_carry_over.merge(df_agent_lookup, on='New Label', how='left')
 
            # The logic to perform the distribution now only runs on the 'df_to_distribute' dataframe
            def perform_distribution(df_cases, df_agents, df_carry_over, prefix, export_path):
                if df_cases.empty or df_agents.empty:
                    return pd.DataFrame(), pd.DataFrame(), pd.DataFrame() # Return empty dataframes

                df_agents = df_agents.copy()
                df_agents.loc[:, 'label_inti'] = df_agents['New Label'].str.extract(f'{prefix}\\.(.*)')
               
                # Calculate the number of cases currently on each agent's desk from the 'carry over' bucket
                # This replaces the need for the 'df_pending' input file
                    # --- 1. Everyone (except ABSEN) keeps their carry-over ---
                df_agents.loc[:, 'on_agent'] = df_agents['label_inti'].apply(
                    lambda x: df_carry_over['Key'][
                        df_carry_over['New Label'].str.contains(re.escape(f"{prefix}.{x}"), na=False, case=False)
                    ].nunique()
                )

               # --- 2. New buckets only go to "hadir" agents (today_column_name = 1) ---
                eligible_for_new = df_agents[(df_agents[today_column_name] == 1) & (df_agents['Status'].str.lower() == 'hadir')].copy()

                data_available = df_agents[['label_inti', 'on_agent']].copy()
                data_available.loc[:, 'total_after_distribution'] = data_available['on_agent']
 
                total_bucket_ready = df_cases.Key.nunique()
               
                def distribute_buckets(data, total_buckets):
                    data.loc[:, 'new_bucket'] = 0
                    if not eligible_for_new.empty and total_buckets > 0:
                        # distribute only among hadir agents
                        per_agent = total_buckets // len(eligible_for_new)
                        remainder = total_buckets % len(eligible_for_new)

                        data.loc[data['label_inti'].isin(eligible_for_new['label_inti']),
                                'new_bucket'] = per_agent
                        if remainder > 0:
                            extra_agents = (eligible_for_new['label_inti'].sort_values(kind='stable').head(remainder).tolist())
                            data.loc[data['label_inti'].isin(extra_agents), 'new_bucket'] += 1

                    return data
                   
                    # Distribute new buckets one by one to the agent with the lowest total
                    for _ in range(total_buckets):
                        min_total_index = data['total_after_distribution'].idxmin()
                        data.loc[min_total_index, 'new_bucket'] += 1
                        data.loc[min_total_index, 'total_after_distribution'] += 1
                    return data
               
                distributed_data = distribute_buckets(data_available, total_bucket_ready)

                # ✅ Use quota from distributed_data
                labels_pool = []
                for _, r in distributed_data.iterrows():
                    labels_pool.extend([r['label_inti']] * int(r['new_bucket']))

                # Make sure pool length matches case count
                if len(labels_pool) > len(df_cases):
                    labels_pool = labels_pool[:len(df_cases)]
                elif len(labels_pool) < len(df_cases):
                    # backfill deterministically
                    add_order = sorted(eligible_for_new['label_inti'].tolist())
                    i = 0
                    while len(labels_pool) < len(df_cases):
                        labels_pool.append(add_order[i % len(add_order)])
                        i += 1

                # Apply assignment (optional: sort cases by priority/created date first)
                df_cases = df_cases.sort_values(['Priority','Created At'], ascending=[True,True]).copy()
                df_cases['xo_agent'] = labels_pool
                df_cases['New Label'] = f'{prefix}.' + df_cases['xo_agent'].astype(str).str.lower()

 
                # Merge with agent emails
                df_agent_lookup = df_agent_new[['New Label', 'Email Agent']].copy()
                df_agent_lookup['New Label'] = df_agent_lookup['New Label'].str.strip().str.lower()
                df_cases = df_cases.merge(
                    df_agent_lookup,
                    on='New Label',
                    how='left'
                )
               
                df_cases.loc[:, 'Key'] = df_cases['Key'].astype('str')
               
                # Create the export link dataframe
                grouped_keys = df_cases.groupby(['New Label'])['Key'].apply(lambda x: ','.join(x)).reset_index()
                grouped = grouped_keys.merge(df_agents[['New Label', 'Akun']], on='New Label', how='left')
               
                base_url = 'https://crmcenter.gdn-app.com/cm/bulk-update?query=%22ID%22%20%3D%20('
                grouped.loc[:, 'url'] = grouped['Key'].apply(lambda x: base_url + f"%22{'%22,%22'.join(x.split(','))}%22)")
                grouped.rename(columns={'New Label': 'Label', 'Akun': 'agent'}, inplace=True)
                grouped['XO'] = grouped['Label']
                group_last = grouped[['Label', 'agent', 'XO', 'url']].copy()   

                # Export the three dataframes
                filepath = self.export_path1.get()
                filepath2 = self.export_path2.get()
                group_last.to_csv(f"{filepath}", index=False)
                distributed_data.to_csv(f"{filepath2}", index=False)
               
                return group_last, distributed_data, df_cases
 
            # --- Main Distribution Logic ---
            # Distribute vocal/retur cases to CR agents
            if not df_vocal_cust.empty and not df_agent_cr.empty:
                _, _, df_distributed_vocal = perform_distribution(df_vocal_cust, df_agent_cr, df_carry_over, 'cr', 'Vocal_CR')
            else:
                df_distributed_vocal = pd.DataFrame()
 
            # Distribute non-vocal/non-retur cases to XO agents
            if not df_to_distribute.empty and not df_agent.empty:
                _, _, df_distributed_general = perform_distribution(df_to_distribute, df_agent, df_carry_over, 'xo', 'XO_General')
            else:
                df_distributed_general = pd.DataFrame()
 
            # Combine all dataframes for final export
            final_df = df_carry_over.copy()
            # Append the newly distributed cases
            if not df_distributed_vocal.empty:
                final_df = pd.concat([final_df, df_distributed_vocal], ignore_index=True)
            if not df_distributed_general.empty:
                final_df = pd.concat([final_df, df_distributed_general], ignore_index=True)

            final_df['CM Link'] = final_df['Key'].apply(lambda x: f"https://crmcenter.gdn-app.com/cm/ticket?id={x}")
            # Export the final combined dataframe to the third specified path
            # Now 'New Label' is the carry-over label for carry-over cases and the assigned label for distributed cases
            # The 'xo_label_distributed' from the distributed cases is now 'New Label' due to the rename.
            #final_df['xo_label_distribute'] = 'xo.' + final_df['xo_agent'].astype(str)
            final_df.loc[:, 'Key'] = final_df['Key'].astype('str')
            final_df.to_csv(self.export_path3.get(), index=False)
            final_df['bucket_type_sort'] = final_df['bucket_type'].apply(lambda x: 0 if x == 'HC' else 1)
            #final_df = final_df.sort_values(by=['New Label', 'Priority', 'bucket_type_sort', 'Created At'], ascending=[True, True, True, True]).reset_index(drop=True)
            #final_df['local_priority'] = final_df.groupby('New Label').cumcount() + 1

            # Export to Excel with table format
            with pd.ExcelWriter(self.export_path3.get().replace('.csv', '.xlsx'), engine='xlsxwriter') as writer:
                final_df.to_excel(writer, sheet_name='Sheet1', index=False)

            book = load_workbook(self.export_path3.get().replace('.csv','.xlsx'))
            sheet = book.active
            tab = Table(displayName='Table1', ref=sheet.dimensions)
            style = TableStyleInfo(name='TableStyleMedium9', showFirstColumn=False, showLastColumn=False,
                                   showRowStripes=True, showColumnStripes=True)
            tab.tableStyleInfo = style
            sheet.add_table(tab)
            book.save(self.export_path3.get().replace('.csv','.xlsx'))
               
            messagebox.showinfo("Success", "Data processing and export completed successfully.")
 
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")
 
if __name__ == "__main__":
    app = ComplaintDistributionApp()
    app.mainloop()