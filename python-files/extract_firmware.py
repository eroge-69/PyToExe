import csv
import binascii
import tkinter as tk
from tkinter import filedialog, messagebox
import os

def extract_binary():
    # Open file dialog to select CSV
    file_path = filedialog.askopenfilename(
        title="Select CAN Log CSV",
        filetypes=[("CSV files", "*.csv")]
    )
    if not file_path:
        messagebox.showwarning("Warning", "No file selected!")
        return

    try:
        # Initialize list to store binary data
        binary_data = []
        
        # Read CSV
        with open(file_path, 'r') as csv_file:
            reader = csv.DictReader(csv_file)
            for row in reader:
                if row['ID'] == '00000322' and row['D1'] == '01' and row['D2'] == '36':
                    # Extract payload (D4 to D8)
                    payload = [row[f'D{i}'] for i in range(4, 9) if row[f'D{i}']]
                    binary_data.append(payload)

        # Convert hex strings to binary
        binary_output = b''
        for payload in binary_data:
            for hex_byte in payload:
                try:
                    binary_output += binascii.unhexlify(hex_byte)
                except binascii.Error:
                    messagebox.showerror("Error", f"Invalid hex data in row: {payload}")
                    return

        # Save to .bin file in the same directory as the input CSV
        output_path = os.path.join(os.path.dirname(file_path), 'ecm_firmware.bin')
        with open(output_path, 'wb') as f:
            f.write(binary_output)

        messagebox.showinfo("Success", f"Extracted {len(binary_output)} bytes to {output_path}")

    except Exception as e:
        messagebox.showerror("Error", f"Failed to process CSV: {str(e)}")

# Create GUI
root = tk.Tk()
root.title("CAN Log Binary Extractor")
root.geometry("400x200")

# Add label and button
label = tk.Label(root, text="Select a CAN log CSV to extract ECM firmware binary", wraplength=350)
label.pack(pady=20)

extract_button = tk.Button(root, text="Select CSV and Extract", command=extract_binary)
extract_button.pack(pady=10)

# Start GUI
root.mainloop()