import tkinter as tk
from tkinter import filedialog, messagebox
import os

def process_line(line):
    if line.startswith("<NAME>"):
        prefix = "<NAME>"
        content = line[len(prefix):].rstrip("\n")
        truncated = content[:32]
        return prefix + truncated + "\n"
    return line

def process_file(input_path):
    output_path = os.path.splitext(input_path)[0] + "_fixed.qbo"
    try:
        with open(input_path, 'r', encoding='utf-8') as infile, \
             open(output_path, 'w', encoding='utf-8') as outfile:
            for line in infile:
                outfile.write(process_line(line))
        return output_path
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred:\n{e}")
        return None

def select_file():
    filepath = filedialog.askopenfilename(
        title="Select a QBO File",
        filetypes=[("QBO files", "*.qbo"), ("All files", "*.*")]
    )
    if filepath:
        result = process_file(filepath)
        if result:
            messagebox.showinfo("Success", f"Fixed file saved as:\n{result}")

def main():
    root = tk.Tk()
    root.withdraw()  # Hide the root window
    select_file()

if __name__ == "__main__":
    main()