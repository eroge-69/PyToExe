import pandas as pd

# Load the Excel file into a pandas DataFrame
# Replace 'your_excel_file.xlsx' with the actual path to your Excel file
# Replace 'Sheet1' with the name of the sheet you want to split
df = pd.read_excel('your_excel_file.xlsx', sheet_name='Sheet1')

# Specify the column based on which you want to split the sheet
# Replace 'sales_rep' with the actual name of the column
split_column = 'sales_rep'

# Get the unique values from the specified column
unique_values = df[split_column].unique()

# Create a new Excel writer object
# Replace 'output_excel_file.xlsx' with the desired name for the new Excel file
output_file = 'output_excel_file.xlsx'

with pd.ExcelWriter(output_file, engine='xlsxwriter') as writer:
    # Iterate through each unique value and create a new sheet
    for value in unique_values:
        # Filter the DataFrame for the current unique value
        df_filtered = df[df[split_column] == value]

        # Clean sheet name (Excel does not allow certain characters)
        sheet_name = str(value).replace('/', '_').replace('\\', '_') \
                              .replace('*', '_').replace('?', '_') \
                              .replace('[', '_').replace(']', '_') \
                              .replace(':', '_')

        # Limit sheet name length to 31 characters (Excel's max)
        sheet_name = sheet_name[:31]

        # Write the filtered DataFrame to a new sheet
        df_filtered.to_excel(writer, sheet_name=sheet_name, index=False)

print("Excel sheet split into multiple tabs successfully!")
