import sys

def process_file(input_file, output_file):
    try:
        # Read the input file
        with open(input_file, 'r') as infile:
            data = infile.readlines()

        # Process the data (example: convert to uppercase)
        processed_data = [line.upper() for line in data]

        # Write to the output file
        with open(output_file, 'w') as outfile:
            outfile.writelines(processed_data)

        print(f"Processing complete! Output saved to {output_file}")
    except FileNotFoundError:
        print(f"Error: The file {input_file} was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: process_file.exe <input_file> <output_file>")
    else:
        input_file = sys.argv[1]
        output_file = sys.argv[2]
        process_file(input_file, output_file)
