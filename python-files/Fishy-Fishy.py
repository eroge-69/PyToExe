import os
import docx
import tkinter as tk
from tkinter import filedialog

def read_docx(file_path):
    doc = docx.Document(file_path)
    text = []
    for paragraph in doc.paragraphs:
        text.append(paragraph.text)
    return '\n'.join(text)

def main():
    root = tk.Tk()
    root.withdraw()
    folder_path = filedialog.askdirectory(title="Select Folder Containing .docx Files")

    keywords = ["fisher 3", "fisher 4", "fisher iii", "fisher iv"]
    flagged_files = []

    for filename in os.listdir(folder_path):
        if filename.endswith('.docx'):
            file_path = os.path.join(folder_path, filename)
            content = read_docx(file_path)
            if any(keyword.lower() in content.lower() for keyword in keywords):
                flagged_files.append(filename)

    with open('flagged_files.txt', 'w') as f:
        for file in flagged_files:
            f.write(f"{file}\n")

    print("Created by OptiCode Solutions")

if __name__ == "__main__":
    main()
