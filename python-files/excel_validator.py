import streamlit as st
import pandas as pd
import re
from io import BytesIO
import os

st.title("📊 Excel Validation Tool (with Ruleset)")

# Upload files
main_file = st.file_uploader("📂 Upload Main Excel File", type=["xlsx"])
ruleset_file = st.file_uploader("📑 Upload Ruleset Excel File", type=["xlsx"])

if main_file and ruleset_file:
    st.success("✅ Both files uploaded successfully!")
    run_validation = st.button("▶️ Run Validation")

    if run_validation:
        # Load files
        df_dict = pd.read_excel(main_file, sheet_name=None)
        ruleset = pd.read_excel(ruleset_file)

        # Load states/countries list if present
        blocked_terms = []
        if os.path.exists("states_countries.txt"):
            with open("states_countries.txt", "r", encoding="utf-8") as f:
                blocked_terms = [line.strip().lower() for line in f if line.strip()]

        errors = []

        # Iterate over each rule
        for idx, row in ruleset.iterrows():
            campaign = str(row['Campaign Name']).strip()
            attribute = str(row['Attribute Name']).strip()
            sheet = str(row['Sheet Name']).strip()
            header = str(row['Header Name']).strip()
            check_type = str(row['Check Type']).strip().lower()
            value = str(row['Value']).strip() if not pd.isna(row['Value']) else None

            if sheet not in df_dict:
                errors.append({
                    "FDRID": "N/A",
                    "Campaign": campaign,
                    "Attribute": attribute,
                    "Sheet": sheet,
                    "Header": header,
                    "Row": "N/A",
                    "Cell Value": "N/A",
                    "Error": f"Sheet '{sheet}' not found"
                })
                continue

            df = df_dict[sheet]

            if header not in df.columns:
                errors.append({
                    "FDRID": "N/A",
                    "Campaign": campaign,
                    "Attribute": attribute,
                    "Sheet": sheet,
                    "Header": header,
                    "Row": "N/A",
                    "Cell Value": "N/A",
                    "Error": f"Header '{header}' not found in sheet '{sheet}'"
                })
                continue

            # Apply validation per cell
            for i, cell_value in enumerate(df[header], start=2):  # +2 for Excel row indexing
                if pd.isna(cell_value):
                    continue
                cell_value_str = str(cell_value)
                error_message = None

                # ========== Check types ==========
                if check_type == "contains":
                    if value not in cell_value_str:
                        error_message = f"Does not contain '{value}'"

                elif check_type == "not_contains":
                    if value in cell_value_str:
                        error_message = f"Contains forbidden text '{value}'"

                elif check_type == "regex":
                    if re.search(value, cell_value_str):
                        if value == r"\b(198\d|199\d|20(0\d|1\d|2[0-5]))\b":
                            error_message = "The year is not allowed"
                        elif value == r"\b\d{3}\.\d{3}\.\d{4}\b":
                            error_message = "The phone number is written with dots"
                        else:
                            error_message = "The cell contains text that doesn’t follow the required format"

                elif check_type == "not_all_caps":
                    if cell_value_str.isupper():
                        error_message = f"Value is all uppercase: '{cell_value_str}'"

                elif check_type == "phone_dot_separator":
                    if re.search(r"\b\d{3}\.\d{3}\.\d{4}\b", cell_value_str):
                        error_message = "The phone number is written with dots"

                elif check_type == "no_list":
                    # Full match only (ignore case)
                    if cell_value_str.strip().lower() in blocked_terms:
                        error_message = f"Cell matches blocked term '{cell_value_str.strip()}'"
                # =================================

                if error_message:
                    fdrid_value = df.at[i - 2, "FDRID"] if "FDRID" in df.columns else "N/A"
                    errors.append({
                        "FDRID": fdrid_value,
                        "Campaign": campaign,
                        "Attribute": attribute,
                        "Sheet": sheet,
                        "Header": header,
                        "Row": i,
                        "Cell Value": cell_value_str,
                        "Error": error_message
                    })

        # Show results
        if errors:
            error_df = pd.DataFrame(errors)
            cols = ["FDRID"] + [c for c in error_df.columns if c != "FDRID"]
            error_df = error_df[cols]

            st.error(f"❌ Found {len(error_df)} validation errors!")

            # Save to Excel
            output = BytesIO()
            with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
                error_df.to_excel(writer, index=False, sheet_name="Validation Errors")
            output.seek(0)

            suggested_name = main_file.name.replace(".xlsx", "_Error_Report.xlsx")
            with open(suggested_name, "wb") as f:
                f.write(output.getvalue())

            st.success(f"📂 Error report saved as {suggested_name} in the current folder")
            st.dataframe(error_df)

        else:
            st.success("✅ No validation errors found!")
