import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox
import os

def filter_csv(input_file, output_file):
    try:
        # Read the CSV file
        df = pd.read_csv(input_file)
        
        # Columns to remove
        columns_to_remove = ['Review Count', 'Rating', 'Catagory', 'Address', 
                           'Email Id', 'latitude', 'longitude', 'State', 'Location']
        
        # Drop specified columns if they exist
        df = df.drop(columns=[col for col in columns_to_remove if col in df.columns])
        
        # Remove rows where Website column has data (not empty)
        if 'Website' in df.columns:
            df = df[df['Website'].isna() | (df['Website'] == '')]
        
        # Save the filtered data to the output CSV
        df.to_csv(output_file, index=False)
        messagebox.showinfo("Success", f"Filtered data saved to {output_file}")
        
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {str(e)}")

def main():
    # Create Tkinter root
    root = tk.Tk()
    root.title("CSV Filter Tool")
    root.geometry("400x200")
    
    def select_input():
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if file_path:
            input_label.config(text=file_path)
    
    def select_output():
        file_path = filedialog.asksaveasfilename(defaultextension=".csv", 
                                              filetypes=[("CSV files", "*.csv")])
        if file_path:
            output_label.config(text=file_path)
    
    def process_files():
        input_file = input_label.cget("text")
        output_file = output_label.cget("text")
        
        if not input_file or input_file == "No file selected":
            messagebox.showwarning("Warning", "Please select an input file!")
            return
        if not output_file or output_file == "No file selected":
            messagebox.showwarning("Warning", "Please select an output file!")
            return
        
        filter_csv(input_file, output_file)
    
    # GUI elements
    tk.Label(root, text="Select Input CSV File:").pack(pady=10)
    input_label = tk.Label(root, text="No file selected")
    input_label.pack()
    tk.Button(root, text="Browse", command=select_input).pack(pady=5)
    
    tk.Label(root, text="Select Output CSV File:").pack(pady=10)
    output_label = tk.Label(root, text="No file selected")
    output_label.pack()
    tk.Button(root, text="Browse", command=select_output).pack(pady=5)
    
    tk.Button(root, text="Process", command=process_files).pack(pady=20)
    
    root.mainloop()

if __name__ == "__main__":
    main()