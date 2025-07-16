import tkinter as tk
from tkinter import filedialog
import os

def search_keyword_in_file(file_path, keyword, output_path):
    found = 0
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as infile, open(output_path, 'w', encoding='utf-8') as outfile:
        for line in infile:
            if keyword.lower() in line.lower():
                outfile.write(line)
                found += 1
    return found

def select_file_and_search():
    file_path = filedialog.askopenfilename(title="Select a .txt file", filetypes=[("Text files", "*.txt")])
    if not file_path:
        print("No file selected.")
        return

    keyword = input("Enter keyword to search for (e.g., glovo.com): ").strip()
    if not keyword:
        print("No keyword entered.")
        return

    output_path = os.path.splitext(file_path)[0] + f"__matches_{keyword}.txt"

    print(f"Searching for keyword '{keyword}' in:\n{file_path}")
    matches = search_keyword_in_file(file_path, keyword, output_path)
    print(f"✅ Done. Found {matches} matching lines.")
    print(f"Results saved to: {output_path}")

if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()  # Hide the main tkinter window
    select_file_and_search()
