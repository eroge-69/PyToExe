import pandas as pd
from tkinter import Tk, filedialog

# Conversion functions
def convert_to_feet_inches(value):
    try:
        value = float(value)
        feet = int(value)
        inches = round((value - feet) * 12, 2)
        return f"{feet}' {inches}\""
    except:
        return "Invalid"

def convert_kg_to_lbm(value):
    try:
        return round(float(value) * 2.20462, 2)
    except:
        return "Invalid"

# Step 1: File selection
Tk().withdraw()
file_path = filedialog.askopenfilename(
    title="Select Excel File",
    filetypes=[("Excel files", "*.xlsx *.xls")]
)

if not file_path:
    print("No file selected. Exiting.")
    exit()

# Step 2: Sheet and column configuration
sheets_and_columns = {
    "Site_Structure_Project": [
        "address", "attSiteId", "modelDate", "captureType", "city", "county",
        "ericssonSiteName", "faCode", "flightTimestamp", "flightType", "imageryUrl",
        "iwmJobId", "locationName", "state", "structureType", "esdtUrl", "usid", "zip"
    ],
    "Sector": [
        "cellId", "useid"
    ],
    "antenna": [
        "_rfdsWOId", "integratedAntenna", "weight", "radiationCenter"
    ]
}

# Step 3: Loop through each sheet
for sheet, columns in sheets_and_columns.items():
    try:
        df = pd.read_excel(file_path, sheet_name=sheet)
        print(f"\n--- Checking sheet: {sheet} ---")

        for col in columns:
            if col not in df.columns:
                print(f"{col}: Column not found")
                continue

            # Antenna-specific logic
            if sheet == "antenna":
                if col == "weight":
                    converted = df[col].dropna().apply(convert_kg_to_lbm)
                    print(f"{col} (converted to lbm):")
                    print(converted.head())
                    continue

                elif col == "radiationCenter":
                    converted = df[col].dropna().apply(convert_to_feet_inches)
                    print(f"{col} (converted to feet & inches):")
                    print(converted.head())
                    continue

                elif col == "integratedAntenna":
                    # Custom logic for integratedAntenna
                    values = df[col].dropna().astype(str).str.strip().str.upper()
                    if (values == "N").all():
                        print(f"{col}: No (all values are 'N')")
                    elif (values == "N").any():
                        print(f"{col}: Mixed (some values are 'N')")
                    else:
                        print(f"{col}: Yes")
                    continue

            # Generic check
            if df[col].dropna().astype(str).str.strip().any():
                print(f"{col}: Yes")
            else:
                print(f"{col}: No")

    except Exception as e:
        print(f"Error reading sheet '{sheet}': {e}")
