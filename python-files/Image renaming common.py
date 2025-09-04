import os
import re
import tkinter as tk
from tkinter import filedialog, messagebox

def rename_file(file_path):
    """Rename a single file by removing version numbers while overwriting existing files."""
    # Define the regex pattern to match version numbers (e.g., .1.1, .233.444, .1.1(2))
    pattern = re.compile(r'\.(\d+(\.\d+)*)(\(\d+\))?\.jpg$', re.IGNORECASE)

    directory, filename = os.path.split(file_path)
    print(f"Processing file: {filename}")  # Debugging line

    match = pattern.search(filename)
    if match:
        # Generate new filename by removing the version number
        new_filename = filename[:match.start()] + '.jpg'
        new_file_path = os.path.join(directory, new_filename)
        print(f"New filename: {new_filename}")  # Debugging line

        if os.path.exists(new_file_path):
            os.remove(new_file_path)

        os.rename(file_path, new_file_path)
        return f'Renamed: {filename} -> {new_filename}'

    print("No match found.")  # Debugging line
    return None

def select_files():
    """Open a file dialog to select files and rename them."""
    try:
        # Open a file dialog to select multiple files
        file_paths = filedialog.askopenfilenames(
            title="Select Files",
            filetypes=[("JPEG files", "*.jpg")],
            initialdir=r"C:\Users\vjayabal\Desktop\Pro"  # Use raw string
        )

        if not file_paths:
            messagebox.showwarning("No Files Selected", r"C:\Users\vjayabal\Desktop\Pro")
            return

        # Process each selected file
        results = []
        for file_path in file_paths:
            result = rename_file(file_path)
            if result:
                results.append(result)

        if results:
            messagebox.showinfo("Success", "\n".join(results))
        else:
            messagebox.showwarning("No Match", "No matching version numbers found in the filenames.")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")

def main():
    # Create the main window
    root = tk.Tk()
    root.title("Image File Renamer")
    root.geometry("300x150")

    # Add a button to select files
    button = tk.Button(root, text="Select Files", command=select_files)
    button.pack(expand=True)

    # Start the GUI event loop
    root.mainloop()

if __name__ == "__main__":
    main()
