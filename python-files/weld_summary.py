import pandas as pd
import tkinter as tk
from tkinter import filedialog

def main():
    root = tk.Tk()
    root.withdraw()

    # Select multiple Excel files
    file_paths = filedialog.askopenfilenames(
        title="Select Excel files",
        filetypes=[("Excel Files", "*.xlsx *.xls")]
    )
    if not file_paths:
        print("No files selected.")
        return

    all_data = {}

    for file in file_paths:
        try:
            df = pd.read_excel(file)

            # Check required columns
            if "SIZE-INCH" not in df.columns or "WELD-CAT" not in df.columns:
                print(f"Skipping {file} (missing SIZE-INCH or WELD-CAT).")
                continue

            for _, row in df.iterrows():
                size = row["SIZE-INCH"]
                weld_cat = str(row["WELD-CAT"]).strip().upper()

                if pd.isna(size):
                    continue

                if size not in all_data:
                    all_data[size] = {"SHOP": 0, "FIELD": 0}

                if weld_cat == "SHOP":
                    all_data[size]["SHOP"] += 1
                elif weld_cat in ["FIELD", "FFW"]:
                    all_data[size]["FIELD"] += 1

        except Exception as e:
            print(f"Error in {file}: {e}")

    # Prepare summary
    summary = []
    for size, values in all_data.items():
        shop = values["SHOP"]
        field = values["FIELD"]
        total = shop + field
        summary.append([size, shop, field, total])

    result_df = pd.DataFrame(summary, columns=["LINE NO", "SHOP", "FIELD", "TOTAL"])

    # Ask save location
    save_path = filedialog.asksaveasfilename(
        defaultextension=".xlsx",
        filetypes=[("Excel files", "*.xlsx")],
        title="Save Summary Excel File"
    )
    if save_path:
        result_df.to_excel(save_path, index=False)
        print(f"Summary saved: {save_path}")
    else:
        print("Save cancelled.")

if __name__ == "__main__":
    main()
