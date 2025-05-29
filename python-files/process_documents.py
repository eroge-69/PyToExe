
import pandas as pd

def process_documents(input_file, output_file):
    # Read the input and unique series sheets
    df_input = pd.read_excel(input_file, sheet_name='Input', engine='openpyxl')
    df_unique_series = pd.read_excel(input_file, sheet_name='Unique Series', engine='openpyxl')

    # Prepare output DataFrame
    df_output = pd.DataFrame(columns=["Supplier GSTIN", "Document Type", "From", "To", "Total", "Cancelled", "Net"])

    # Sort input data
    df_input = df_input.sort_values(by=["Supplier GSTIN", "Document Type", "Document Number"])

    # Get list of series
    series_list = df_unique_series.iloc[:, 0].tolist()

    # Dictionary to hold series data
    dict_series = {}

    for series in series_list:
        previous_number = 0
        missing_count = 0

        for _, row in df_input.iterrows():
            supplier_gstin = row["Supplier GSTIN"]
            doc_type = row["Document Type"]
            doc_number = row["Document Number"]

            if str(doc_number).startswith(series):
                numeric_part = str(doc_number)[len(series):]

                if numeric_part.isdigit():
                    current_number = int(numeric_part)
                    key = f"{supplier_gstin}|{doc_type}|{series}"

                    if key in dict_series:
                        dict_series[key]["End"] = doc_number
                        dict_series[key]["Total"] += 1
                        if previous_number > 0 and current_number > previous_number + 1:
                            missing_count += (current_number - previous_number - 1)
                    else:
                        dict_series[key] = {
                            "Start": doc_number,
                            "End": doc_number,
                            "Total": 1,
                            "Cancelled": 0
                        }

                    previous_number = current_number

        if key in dict_series:
            dict_series[key]["Cancelled"] = missing_count
            dict_series[key]["Total"] += missing_count

    for key, value in dict_series.items():
        supplier_gstin, doc_type, _ = key.split("|")
        df_output = pd.concat([df_output, pd.DataFrame([{
            "Supplier GSTIN": supplier_gstin,
            "Document Type": doc_type,
            "From": value["Start"],
            "To": value["End"],
            "Total": value["Total"],
            "Cancelled": value["Cancelled"],
            "Net": value["Total"] - value["Cancelled"]
        }])], ignore_index=True)

    # Write to output Excel file
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        df_output.to_excel(writer, sheet_name='Output', index=False)

# Example usage:
# process_documents("sample_data.xlsx", "output_data.xlsx")
