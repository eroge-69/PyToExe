from pathlib import Path
import fitz
import os
import re
from tkinter import filedialog
import tkinter as tk


def select_folder():
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    folder_path = filedialog.askdirectory()
    return folder_path
def extract_text_from_pdf(pdf_document):
    text = ""
    try:
        doc = pdf_document
        for page_num in range(doc.page_count):
            page = doc[page_num]
            text += page.get_text()
    except Exception as e:
        print("Error extracting text from PDF:", str(e))
    return text

def find_pdfs_in_folders(root_path, target_folders):
    pdf_files = []
    for folder_name in os.listdir(root_path):
        folder_path = os.path.join(root_path, folder_name)
        if os.path.isdir(folder_path) and folder_name in target_folders:
            for root, dirs, files in os.walk(folder_path):
                for file in files:
                    if file.endswith(".pdf"):
                        pdf_files.append(os.path.join(root, file))
    return pdf_files

def count_root_folders(path,target_folders):
    # Get the list of items (files and directories) in the given path
    items = os.listdir(path)

    # Filter out only directories
    folders = [item for item in items if os.path.isdir(os.path.join(path, item))]
    # print(folders)
    # Count the number of root folders

    report_file_path = f"{path}/Report.txt"

    if os.path.exists(report_file_path):
        os.remove(report_file_path)


    for i in range(len(folders)):
        pdf_folder = os.path.join(path, folders[i])
        pdf_paths = find_pdfs_in_folders(pdf_folder,target_folders)

        for pdf in pdf_paths:
            parent_folder = os.path.dirname(pdf)
            if os.path.basename(parent_folder) == "McAfee":
                pdf_document2 = fitz.open(pdf)
                text2 = extract_text_from_pdf(pdf_document2)
                total_pattern = r"Total\s+(\d+)"
                total_numbers = re.findall(total_pattern, text2)

            elif(os.path.basename(parent_folder) == "Apex"):
                pdf_document2 = fitz.open(pdf)
                text1 = extract_text_from_pdf(pdf_document2)
                word_to_count = "Client"
                lowercase_text1 = text1.lower()
                word_count = lowercase_text1.count(word_to_count.lower())


        with open(report_file_path, 'a') as file:

            file.write(folders[i] + '\n')
            file.write("Agent Versions Summary: " + total_numbers[0] + '\n')
            file.write("ENS - 7 Days OLD Report Windows: " + total_numbers[1] + '\n')
            file.write("Apex Outdated Count:" + str(word_count) + '\n')
            file.write('\n')



# Example usage
path_to_check = select_folder()

# path_to_check = "C:/Users/SL907/Downloads/New folder (1)/New folder/January"

target_folders = ["Apex", "McAfee"]
count_root_folders(path_to_check,target_folders)




# Example usage
# root_path = "/path/to/your/directory"

# pdf_files = find_pdfs_in_folders(root_path, target_folders)
#
# if pdf_files:
#     print("PDF files found in target folders:")
#     for pdf_file in pdf_files:
#         print(pdf_file)
# else:
#     print("No PDF files found in target folders.")

# Example usage:
# given_path = "C:/Users/SL907/Downloads/New folder (1)/New folder/January"

