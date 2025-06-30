import csv
import os

def copy_and_clean_csv(input_filepath, output_filepath):
    """
    Copies a CSV file to a new CSV file, removing quotation marks from all cell values.

    Args:
        input_filepath (str): The path to the input CSV file.
        output_filepath (str): The path where the new, cleaned CSV file will be saved.
    """
    try:
        # Ensure the input file exists
        if not os.path.exists(input_filepath):
            print(f"Error: Input file not found at '{input_filepath}'")
            return

        print(f"Reading from: {input_filepath}")
        print(f"Writing to: {output_filepath}")

        with open(input_filepath, 'r', newline='', encoding='utf-8') as infile, \
             open(output_filepath, 'w', newline='', encoding='utf-8') as outfile:

            reader = csv.reader(infile)
            writer = csv.writer(outfile)

            for row in reader:
                # Process each cell in the row to remove single and double quotation marks
                cleaned_row = [cell.replace('"', '').replace("'", '') for cell in row]
                writer.writerow(cleaned_row)

        print("CSV file copied and cleaned successfully!")

    except FileNotFoundError:
        print(f"Error: The file '{input_filepath}' was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    # Define input and output file paths
    # You can change these paths as needed
    input_csv_file = 'AutomatedMarshDatabase.csv'
    output_csv_file = 'AutomatedMarshDatabase_Cleaned.csv'

    # Call the function to perform the copy and clean operation
    copy_and_clean_csv(input_csv_file, output_csv_file)