import base64
import os
import tkinter as tk
from tkinter import filedialog, messagebox
def decode_base64_to_pdf():
    base64_string = input_text.get("1.0", tk.END).strip()  # Get Base64 string from the text box
    if not base64_string:
        messagebox.showerror("Error", "Please enter a Base64 string.")
        return
    # Ask the user where to save the PDF file
    file_path = filedialog.asksaveasfilename(
        defaultextension=".pdf",
        filetypes=[("PDF files", "*.pdf")],
        title="Save PDF File"
    )
    if not file_path:  # If the user cancels the save dialog
        return
    try:
        # Decode the Base64 string
        pdf_bytes = base64.b64decode(base64_string)
        # Save the decoded bytes as a PDF file
        with open(file_path, "wb") as pdf_file:
            pdf_file.write(pdf_bytes)
        # Show success message
        messagebox.showinfo("Success", f"PDF file has been successfully created at:\n{file_path}")
    except Exception as e:
        # Show error message if decoding fails
        messagebox.showerror("Error", f"An error occurred:\n{e}")
# Create the main window
root = tk.Tk()
root.title("Base64 to PDF Decoder")
# Create a text box for Base64 input
input_label = tk.Label(root, text="Enter Base64 String:")
input_label.pack(pady=5)
input_text = tk.Text(root, height=10, width=50)
input_text.pack(pady=5)
# Create a button to decode and save the PDF
decode_button = tk.Button(root, text="Decode and Save PDF", command=decode_base64_to_pdf)
decode_button.pack(pady=10)
# Run the application
root.mainloop()