import os

# Prompt for company name
company_name = input("Enter the Company Name: ").strip()

# Folder containing CSV files
folder_path = r"C:\Users\SmijithSathian\Downloads\Churn"  # <-- Update if needed

# Mapping of old file base names to new suffixes
rename_map = {
    "Export Postings": "OffboardingPostingsExport",
    "Export Opportunities": "OffboardingCandidatesExport",
    "Export Interview Calibration": "OffboardingInterviewCalibrationExport",
    "Export Interview Data": "OffboardingInterviewEventsExport"
}

print("\nChecking files in folder...")

# Rename files if they exist
for old_base, new_suffix in rename_map.items():
    old_file = os.path.join(folder_path, f"{old_base}.csv")
    new_file = os.path.join(folder_path, f"{company_name}_{new_suffix}.csv")

    if os.path.exists(old_file):
        try:
            os.rename(old_file, new_file)
            print(f"✅ Renamed: '{old_base}.csv' → '{company_name}_{new_suffix}.csv'")
        except Exception as e:
            print(f"❌ Error renaming '{old_base}.csv': {e}")
    else:
        print(f"⚠️  File not found: '{old_base}.csv'")

# List all remaining CSVs in the folder
print("\nRemaining CSV files in folder:")
for f in os.listdir(folder_path):
    if f.endswith(".csv"):
        print(" -", f)

# Wait before exit
input("\nPress Enter to exit...")