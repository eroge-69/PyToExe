import pandas as pd
import sys
import os
from datetime import datetime
from collections import defaultdict

def convert_excel_to_272(excel_file_path):
    """
    Reads an Excel file and converts it to the [272] Customer Order tab-delimited format.
    """
    if not os.path.exists(excel_file_path):
        print(f"Error: The file '{excel_file_path}' was not found.")
        input("Press Enter to exit...")
        sys.exit(1)

    try:
        df = pd.read_excel(excel_file_path)
    except Exception as e:
        print(f"Error reading the Excel file: {e}")
        input("Press Enter to exit...")
        sys.exit(1)

    # Dictionary to hold the data grouped by order number
    orders = defaultdict(list)
    
    # Loop through each row to group detail lines under a single header
    for index, row in df.iterrows():
        try:
            order_key = str(row['Order #']).strip()
            if not order_key:
                continue
            
            # Use Order # and Store number as a unique key for the order
            unique_order_key = f"{order_key}-{str(row['Store number']).strip()}"
            orders[unique_order_key].append(row)
        except KeyError as e:
            print(f"Error: Missing a required column in the Excel file. Please ensure the file contains a column named '{e}'.")
            input("Press Enter to exit...")
            sys.exit(1)

    # Prepare the output content string
    output_content = []
    
    for key, items in orders.items():
        header_row = items[0]
        
        # Extract and format header information
        full_store_name = str(header_row['Store Name']).strip()
        customer_code = full_store_name[:6]
        store_code = str(header_row['Store number']).strip()
        ref_number = str(header_row['Order #']).strip()
        delivery_date_raw = str(header_row['Delivery']).strip()

        # Convert NZ/AU date format (DD-Mon-YY) to US format (MM/DD/YYYY)
        try:
            delivery_date_obj = datetime.strptime(delivery_date_raw, '%d-%b-%y')
            formatted_date = delivery_date_obj.strftime('%m/%d/%Y')
        except ValueError:
            print(f"Error: The date '{delivery_date_raw}' is in an unexpected format. Please ensure all dates are in DD-Mon-YY format.")
            input("Press Enter to exit...")
            sys.exit(1)
        
        # Construct the header line
        header_line = f"H\t{store_code}\t{customer_code}\t{ref_number}\t\t{formatted_date}\tN"
        output_content.append(header_line)
        
        # Process all detail items for this order
        for item_row in items:
            item_code = str(item_row['Item code']).strip()
            order_quantity = str(item_row['Qty']).strip()
            
            # Construct the detail line
            detail_line = f"D\t{item_code}\t{order_quantity}"
            output_content.append(detail_line)

    # Write the output to a new .txt file
    output_filename = os.path.splitext(os.path.basename(excel_file_path))[0] + ".txt"
    try:
        with open(output_filename, 'w') as f:
            for line in output_content:
                f.write(line + '\n')
        print(f"Conversion complete. The output file is '{output_filename}'")
    except Exception as e:
        print(f"Error writing the output file: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: Drag and drop your Excel file onto this program.")
        input("Press Enter to exit...")
    else:
        file_to_convert = sys.argv[1]
        convert_excel_to_272(file_to_convert)
        input("Press Enter to exit...")