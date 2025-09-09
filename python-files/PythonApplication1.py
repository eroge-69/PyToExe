import sys
import os
import subprocess

def compress_pdf(input_path, output_path, quality="screen"):
    """
    Compress a PDF using Ghostscript.
    :param input_path: Path to the input PDF file.
    :param output_path: Path to save the compressed PDF.
    :param quality: Quality setting ('screen', 'ebook', 'printer', 'prepress').
    """
    gs_command = [
        r"C:\Program Files\gs\gs10.05.1\bin\gswin64c.exe",  # Update this path as needed
        "-sDEVICE=pdfwrite",
        f"-dPDFSETTINGS=/{quality}",
        "-dNOPAUSE",
        "-dBATCH",
        "-dQUIET",
        f"-sOutputFile={output_path}",
        input_path
    ]
    try:
        subprocess.run(gs_command, check=True)
        print(f"Compressed PDF saved as: {output_path}")
    except subprocess.CalledProcessError:
        print(f"Failed to compress: {input_path}")

if __name__ == "__main__":
    folder = input("Enter the folder path containing PDF files: ").strip().strip('"')
    print(f"Checking folder: {folder}")
    if not os.path.isdir(folder):
        print("The specified folder does not exist.")
        input("Press Enter to exit...")
        sys.exit(1)

    all_files = os.listdir(folder)
    print(f"Files found: {all_files}")
    pdf_files = [f for f in all_files if f.lower().endswith('.pdf')]
    print(f"PDF files found: {pdf_files}")
    if not pdf_files:
        print("No PDF files found in the specified folder.")
        input("Press Enter to exit...")
        sys.exit(1)

    output_folder = os.path.join(folder, "compressed")
    os.makedirs(output_folder, exist_ok=True)

    for pdf_file in pdf_files:
        input_path = os.path.join(folder, pdf_file)
        output_path = os.path.join(output_folder, pdf_file)
        print(f"Compressing: {pdf_file}")
        compress_pdf(input_path, output_path)

    print(f"All PDFs have been compressed and saved to: {output_folder}")
    input("Press Enter to exit...")
