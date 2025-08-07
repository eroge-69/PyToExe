import tkinter as tk
from tkinter import filedialog
import re
import os

def remove_text_in_parentheses(input_file):
    with open(input_file, 'r') as f:
        lines = f.readlines()

    new_lines = []
    for line in lines:
        new_lines.append(re.sub(r'\(.*?\)', '', line).strip() + '\n')

    return new_lines

def export_file(new_lines, input_file):
    filename, file_extension = os.path.splitext(input_file)
    output_file = f"{filename}_distribution{file_extension}"
    with open(output_file, 'w') as f:
        f.writelines(new_lines)

    os.startfile(output_file)

def select_file():
    input_file = filedialog.askopenfilename(title="Select the original file", filetypes=[("Text files", "*.txt")])
    if input_file:
        new_lines = remove_text_in_parentheses(input_file)
        export_file(new_lines, input_file)

root = tk.Tk()
root.title("Text File Processor")

select_button = tk.Button(root, text="Select the original file", command=select_file)
select_button.pack(padx=10, pady=10)

root.mainloop()
