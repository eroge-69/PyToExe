import pandas as pd

# The name of your CSV file
file_name = 'elements.csv'

# Read the CSV file into a pandas DataFrame
try:
    df = pd.read_csv(file_name)

    # Print the DataFrame to display it as a table
    print("Data from CSV file:")
    print(df.to_string())

except FileNotFoundError:
    print(f"Error: The file '{file_name}' was not found.")