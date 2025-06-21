import pandas as pd
import os
from docx2pdf import convert
from PyPDF2 import PdfMerger

def combine_docx_to_pdf(excel_file_path, docx_column_name='Docx_Path', output_pdf_path):
    """
    Combines multiple DOCX files into a single PDF based on file paths
    listed in an Excel spreadsheet.

    Args:
        excel_file_path (str): The path to the Excel spreadsheet.
        output_pdf_path (str): The desired path for the combined PDF output file.
        docx_column_name (str): The name of the column in the Excel
                                spreadsheet containing the DOCX file paths.
                                Defaults to 'Docx_Path'.
    """

    try:
        # Read the Excel file into a pandas DataFrame.
        df = pd.read_excel(excel_file_path)

        # Get the list of DOCX file paths from the specified column.
        docx_files = df[docx_column_name].tolist()

        # Create a list to store paths of temporary PDF files.
        temp_pdf_files = []

        # Convert each DOCX file to a temporary PDF.
        for docx_file in docx_files:
            if not os.path.exists(docx_file):
                print(f"Warning: DOCX file not found at '{docx_file}'. Skipping.")
                continue

            temp_pdf_path = docx_file.replace('.docx', '.pdf')  # Create temp PDF path
            try:
                convert(docx_file, temp_pdf_path)  # Convert DOCX to PDF
                temp_pdf_files.append(temp_pdf_path)
            except Exception as e:
                print(f"Error converting '{docx_file}' to PDF: {e}")

        # Merge the temporary PDF files.
        pdf_merger = PdfMerger()
        for temp_pdf in temp_pdf_files:
            try:
                pdf_merger.append(temp_pdf)  # Append PDF to merger
            except Exception as e:
                print(f"Error merging '{temp_pdf}': {e}")

        # Write the combined PDF to the specified output path.
        with open(output_pdf_path, 'wb') as output_file:
            pdf_merger.write(output_file)

        # Close the PDF merger object.
        pdf_merger.close()

        # Clean up temporary PDF files.
        for temp_pdf in temp_pdf_files:
            try:
                os.remove(temp_pdf)  # Remove temporary PDF
            except Exception as e:
                print(f"Error removing temporary PDF '{temp_pdf}': {e}")

        print(f"Successfully combined DOCX files into '{output_pdf_path}'")

    except FileNotFoundError:
        print(f"Error: Excel file not found at '{excel_file_path}'")
    except KeyError:
        print(f"Error: Column '{docx_column_name}' not found in the Excel file.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == '__main__':
    # Example usage:
    excel_file = 'your_spreadsheet.xlsx'  # Replace with your Excel file name
    output_pdf = 'combined_document.pdf' # Replace with your desired output PDF name
    docx_column = 'Docx_File_Path'        # Replace with the name of the column in your Excel that contains the DOCX file paths

    combine_docx_to_pdf(excel_file, output_pdf, docx_column)