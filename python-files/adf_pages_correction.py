import argparse
import os
from PyPDF2 import PdfReader, PdfWriter

# ANSI escape codes for text colors
RED = "\033[91m"
RESET = "\033[0m"


def reorder_pdf_pages(input_path, output_path):
    # Read the input PDF
    pdf = PdfReader(input_path)

    # Create a PDF writer object
    output = PdfWriter()

    # Get the total number of pages
    total_pages = len(pdf.pages)

    # Calculate the number of odd and even pages
    odd_pages = (total_pages + 1) // 2

    # Reorder the pages
    for i in range(odd_pages):
        # Add odd page
        output.add_page(pdf.pages[i])

        # Add corresponding even page if it exists
        even_index = total_pages - 1 - i
        if even_index >= odd_pages:
            output.add_page(pdf.pages[even_index])

    # Write the reordered PDF to a file
    with open(output_path, 'wb') as output_file:
        output.write(output_file)

    return output_path


def confirm_overwrite(path):
    if os.path.exists(path):
        while True:
            response = input(
                f"{RED}The file '{path}' already exists. Do you want to overwrite it? (y/n): {RESET}").lower()
            if response in ['y', 'yes']:
                return True
            elif response in ['n', 'no']:
                return False
            else:
                print("Please answer with 'y' or 'n'.")
    return True


def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Reorder PDF pages from scanner output.")
    parser.add_argument("--input", required=True, help="Absolute path to the input PDF file")
    parser.add_argument("--output", required=True, help="Absolute path for the output PDF file")

    # Parse arguments
    args = parser.parse_args()

    try:
        # Check if output file exists and confirm overwrite
        if not confirm_overwrite(args.output):
            print("Operation cancelled.")
            return

        # Call the reorder function with provided arguments
        output_path = reorder_pdf_pages(args.input, args.output)
        print(f"Reordered PDF saved as {output_path}")
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    main()
