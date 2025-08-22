import os
import zipfile
import tarfile
import csv
from datetime import datetime
import tkinter as tk
from tkinter import filedialog, messagebox

# --- FUNCTIONS ---

def extract_and_process(input_file, output_folder, delimiter=","):
    # Make sure output folder exists
    os.makedirs(output_folder, exist_ok=True)

    # --- STEP 1: EXTRACT ARCHIVE ---
    try:
        if zipfile.is_zipfile(input_file):
            with zipfile.ZipFile(input_file, 'r') as zip_ref:
                zip_ref.extractall(output_folder)
            print(f"Extracted ZIP: {os.path.basename(input_file)}")

        elif tarfile.is_tarfile(input_file):
            with tarfile.open(input_file, 'r:*') as tar_ref:
                tar_ref.extractall(output_folder)
            print(f"Extracted TAR: {os.path.basename(input_file)}")

        else:
            messagebox.showwarning("Invalid File", "Selected file is not ZIP or TAR.")
            return

    except Exception as e:
        messagebox.showerror("Error", f"Error extracting {os.path.basename(input_file)}:\n{e}")
        return

    # --- STEP 2: EXTRACT SECOND COLUMN FROM DAT FILES ---
    second_column_values = []

    for root, dirs, files in os.walk(output_folder):
        for file_name in files:
            if file_name.lower().endswith(".dat"):
                dat_path = os.path.join(root, file_name)
                try:
                    with open(dat_path, 'r', encoding='utf-8') as f:
                        reader = csv.reader(f, delimiter=delimiter)
                        for row in reader:
                            if len(row) >= 2:  # check if there is a second column
                                second_column_values.append(row[1].strip())
                    print(f"Processed second column from: {file_name}")
                except Exception as e:
                    print(f"Error reading {file_name}: {e}")

    # --- STEP 3: SAVE WITH ASCENDING NUMBERS, DATE & TIME ---
    if second_column_values:
        today = datetime.now().strftime("%Y%m%d")   # e.g., 20250822
        time_now = datetime.now().strftime("%H%M%S")  # e.g., 073015

        # Find latest number used today
        existing_files = [f for f in os.listdir(output_folder) if f.startswith(today)]
        numbers = []
        for f in existing_files:
            parts = f.split("_")
            if len(parts) > 1 and parts[1].isdigit():
                numbers.append(int(parts[1]))
        next_num = max(numbers, default=0) + 1

        # Filename format: YYYYMMDD_###_HHMMSS.txt
        output_text_file = os.path.join(
            output_folder,
            f"{today}_{str(next_num).zfill(3)}_{time_now}.txt"
        )

        with open(output_text_file, 'w', encoding='utf-8') as f:
            for value in second_column_values:
                f.write(value + "\n")

        messagebox.showinfo("Success", f"Saved extracted data to:\n{output_text_file}")
    else:
        messagebox.showwarning("No Data", "No DAT files found or no second column to extract.")


# --- GUI APP ---

def run_app():
    input_file = filedialog.askopenfilename(
        title="Select ZIP/TAR File",
        filetypes=[("Compressed files", "*.zip *.tar *.tar.gz *.tgz"), ("All files", "*.*")]
    )
    if not input_file:
        return

    # Hardcode output folder to C:\1
    output_folder = r"C:\1"

    extract_and_process(input_file, output_folder)


# Build tkinter window
root = tk.Tk()
root.title("DAT File Extractor")
root.geometry("400x200")

label = tk.Label(root, text="DAT File Extractor", font=("Arial", 16))
label.pack(pady=20)

run_button = tk.Button(root, text="Select File & Run", command=run_app, font=("Arial", 12))
run_button.pack(pady=10)

exit_button = tk.Button(root, text="Exit", command=root.quit, font=("Arial", 12))
exit_button.pack(pady=5)

root.mainloop()
