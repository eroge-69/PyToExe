import pandas as pd
import sys
import os

def convert_excel_to_csv(input_excel_path, output_csv_path):
    try:
        # Read Excel, skip first 5 rows (headers are on row 6)
        df = pd.read_excel(input_excel_path, header=5)

        # SKU is in the 3rd column (index 2), shop data starts from column 5 (index 4)
        sku_column = df.columns[2]
        shop_columns = df.columns[4:]

        # Extract and reshape
        df_long = df[[sku_column] + list(shop_columns)].copy()
        df_unpivoted = df_long.melt(id_vars=[sku_column], var_name="shopcode", value_name="stock")

        # Rename and clean
        df_unpivoted.columns = ['sku#', 'shopcode', 'stock']
        df_unpivoted.dropna(subset=['sku#', 'shopcode', 'stock'], inplace=True)
        df_unpivoted['sku#'] = df_unpivoted['sku#'].astype(str).str.strip()
        df_unpivoted['shopcode'] = df_unpivoted['shopcode'].astype(str).str.strip()

        # Save to CSV
        df_unpivoted.to_csv(output_csv_path, index=False)
        print(f"✅ CSV created successfully at: {output_csv_path}")

    except Exception as e:
        print(f"❌ Error: {e}")

# Allow command-line usage: python convert_excel_to_csv.py input.xlsx output.csv
if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python convert_excel_to_csv.py <input_excel_path> <output_csv_path>")
    else:
        input_file = sys.argv[1]
        output_file = sys.argv[2]
        convert_excel_to_csv(input_file, output_file)