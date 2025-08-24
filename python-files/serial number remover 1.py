import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import re

def remove_duplicate_rows():
    # Ask user to select input file
    input_file_path = filedialog.askopenfilename(
        title="Select Input File",
        filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
    )
    
    if not input_file_path:
        return
    
    try:
        # Read the file
        with open(input_file_path, 'r', encoding='utf-8', errors='ignore') as file:
            lines = file.readlines()
        
        if not lines:
            messagebox.showerror("Error", "The file is empty!")
            return
        
        # Process each line to find 8-digit serial numbers
        seen_serial_numbers = set()
        unique_rows = []
        duplicates_removed = 0
        total_serial_numbers_found = 0
        
        for line in lines:
            line = line.strip()
            if not line:
                unique_rows.append(line)
                continue
            
            # Find all 8-digit numbers in this line
            eight_digit_numbers = re.findall(r'\b\d{8}\b', line)
            
            if not eight_digit_numbers:
                # No 8-digit numbers found, keep the line
                unique_rows.append(line)
                continue
            
            # Use the first 8-digit number as the serial number for this row
            serial_number = eight_digit_numbers[0]
            total_serial_numbers_found += 1
            
            if serial_number not in seen_serial_numbers:
                # First time seeing this serial number - keep the row
                seen_serial_numbers.add(serial_number)
                unique_rows.append(line)
            else:
                # Duplicate serial number - skip this row
                duplicates_removed += 1
        
        # Ask user to select output file location
        output_file_path = filedialog.asksaveasfilename(
            title="Save Output File As",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if not output_file_path:
            return
        
        # Write to output file
        with open(output_file_path, 'w', encoding='utf-8') as file:
            for row in unique_rows:
                file.write(row + '\n')
        
        # Show results
        result_text.delete(1.0, tk.END)
        result_text.insert(tk.END, f"Total 8-digit serial numbers found: {total_serial_numbers_found}\n")
        result_text.insert(tk.END, f"Original rows: {len(lines)}\n")
        result_text.insert(tk.END, f"Unique rows: {len(unique_rows)}\n")
        result_text.insert(tk.END, f"Duplicate rows removed: {duplicates_removed}\n\n")
        result_text.insert(tk.END, f"Output saved to: {output_file_path}\n\n")
        
        # Show some sample serial numbers
        result_text.insert(tk.END, "First 10 unique serial numbers found:\n")
        for i, serial in enumerate(list(seen_serial_numbers)[:10]):
            result_text.insert(tk.END, f"{i+1}. {serial}\n")
        
        messagebox.showinfo("Success", f"Duplicate rows removed successfully!\n\n"
                                      f"8-digit serial numbers found: {total_serial_numbers_found}\n"
                                      f"Original rows: {len(lines)}\n"
                                      f"Unique rows: {len(unique_rows)}\n"
                                      f"Duplicates removed: {duplicates_removed}")

    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {str(e)}")

# Create the main window
root = tk.Tk()
root.title("8-Digit Serial Number Duplicate Remover")
root.geometry("700x500")

# Create and place widgets
frame = tk.Frame(root)
frame.pack(pady=10)

select_button = tk.Button(frame, text="Select File and Remove Duplicate Rows", 
                         command=remove_duplicate_rows, bg="lightgreen", font=("Arial", 12))
select_button.pack(pady=10)

result_text = scrolledtext.ScrolledText(root, width=80, height=20)
result_text.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

instructions = tk.Label(root, text="This program will find EXACT 8-DIGIT NUMBERS as serial numbers\n"
                                  "and remove entire rows where these numbers are duplicates.\n"
                                  "Example: '11873134' will be detected as a serial number.\n"
                                  "It keeps the first occurrence of each serial number and removes subsequent duplicates.",
                      justify=tk.CENTER)
instructions.pack(pady=5)

root.mainloop()