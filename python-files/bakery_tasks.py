from bakery_utils import Bake_assoc, assoc_builder, writeList, getDates
import pandas as pd
import tkinter as tk
from tkinter import filedialog


root = tk.Tk()
root.withdraw()

print("Select Schedule")
input_file = filedialog.askopenfilename(title="Select Schedule", filetypes=[("Excel files", "*.xlsx *.xls")])

if not  input_file:
    print("No file selected")

dates = getDates(input_file)
we_date = dates[-1]

print("Select output location")
output_file = filedialog.asksaveasfilename(title="Save List", 
                                           defaultextension=".xlsx",
                                           initialfile=f"Task List WE {we_date}.xlsx", 
                                           filetypes=[("Excel files", "*.xlsx")])

if not output_file:
    print("No location")

schedule = pd.ExcelFile(input_file)
df_full_preview = schedule.parse("Report", header=None)

start_row = 7
name_col = 0
day_columns = [6, 8, 10, 11, 12, 14, 16]
days = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]

df_schedule_raw = df_full_preview.iloc[start_row::2, [name_col] + day_columns]
df_schedule_raw.columns = ["Name"] + days
df_schedule_raw.reset_index(drop=True, inplace=True)

assocs_and_days = {}

for _, row in df_schedule_raw.iterrows():
    name = row["Name"]
    scheduled_days = [day for day in df_schedule_raw.columns[1:] if pd.notna(row[day])]
    assocs_and_days[name] = scheduled_days

bakery_associates = assoc_builder(assocs_and_days)

print("Generating List")

writeList(bakery_associates, output_file, dates)

print("Done")