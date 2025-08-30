import pandas as pd

# === Step 1: Load data from the template ===
file_name = "Courier_Pincode_Template.xlsx"

# India Post (base list)
post_df = pd.read_excel(file_name, sheet_name="IndiaPost")

# Couriers
couriers = ["Professional", "DTDC", "ShreeMaruti", "Tej", "Trackon"]
courier_dfs = {c: pd.read_excel(file_name, sheet_name=c) for c in couriers}

# === Step 2: Create master dataframe ===
master = post_df.copy()
for courier in couriers:
    master[courier] = master["Pincode"].isin(courier_dfs[courier]["Pincode"]).map({True: "Yes", False: "No"})

# === Step 3: Add Coverage Status column ===
def coverage_status(row):
    couriers_available = sum([row[courier] == "Yes" for courier in couriers])
    if couriers_available == 0:
        return "Only Post"
    elif couriers_available == 1:
        return "Single Courier"
    else:
        return "Multiple Couriers"

master["Coverage Status"] = master.apply(coverage_status, axis=1)

# === Step 4: Save output ===
output_file = "Master_Pincode_Coverage.xlsx"
master.to_excel(output_file, index=False)

print(f"b Master file created: {output_file}")
