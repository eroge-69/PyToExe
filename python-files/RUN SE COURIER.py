import pandas as pd
from tqdm import tqdm
import glob
import os
from datetime import datetime

# Find all matching files
files = glob.glob("SE_COURIER_*.xlsx")

if not files:
    input("❌ No files found matching SE_COURIER_*.xlsx\nPress Enter to exit...")
    raise SystemExit

print("📥 Reading Excel files...")
dataframes = []

# Helper to extract date from file name (e.g. AUG25 -> 2025-08-01)
def extract_date(file):
    name = os.path.splitext(os.path.basename(file))[0]  # e.g. SE_COURIER_AUG25
    month_year = name.replace("SE_COURIER_", "")        # e.g. AUG25
    return datetime.strptime(month_year, "%b%y")

# Sort files by extracted date
files = sorted(files, key=extract_date)

# Read all files with progress bar
for file in tqdm(files, desc="Loading files"):
    df = pd.read_excel(file)
    dataframes.append(df)

print("🔄 Combining data...")
combined_df = pd.concat(dataframes, ignore_index=True)

print("📊 Creating pivot table...")
pivot_table = pd.pivot_table(
    combined_df,
    values='Amount',
    index='MasterAWB',
    columns='G/L Account No.',
    aggfunc='sum',
    fill_value=0
)

# Get last (latest) file and build output name
latest_file = files[-1]
latest_name = os.path.splitext(os.path.basename(latest_file))[0]  # e.g. SE_COURIER_AUG25
output_file = f"{latest_name}_PIVOT.xlsx"

print("💾 Saving to Excel...")
pivot_table.to_excel(output_file)

print("\n✅ Done!")
print(f"📂 File created: {output_file}")
print("\n📋 Files included in this run:")
for f in files:
    print("   -", os.path.basename(f))

# Pause so window doesn't close immediately (for .exe use)
input("\nPress Enter to exit...")
