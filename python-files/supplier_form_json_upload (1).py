import tkinter as tk
from tkinter import messagebox
import json
import requests

# SAS URL provided for uploading the JSON file
sas_url = "https://sustainedscorecard1.blob.core.windows.net/pip-48suppliers/ABB.json?sp=racw&st=2025-06-10T21:58:09Z&se=2025-12-31T06:58:09Z&spr=https&sv=2024-11-04&sr=c&sig=JuMydQr2EmDhy7cDLJdFqQqh8NtEFJpzI%2FJgUoIMIUE%3D"

def submit_data():
    # Collect data from the form
    supplier_name = entry_name.get()
    email = entry_email.get()
    product = entry_product.get()
    quantity = entry_quantity.get()

    if not supplier_name or not email or not product or not quantity:
        messagebox.showerror("Error", "All fields are required.")
        return

    try:
        quantity = int(quantity)
    except ValueError:
        messagebox.showerror("Error", "Quantity must be a number.")
        return

    # Create a dictionary of the data
    data = {
        "SupplierName": supplier_name,
        "Email": email,
        "Product": product,
        "Quantity": quantity
    }

    # Convert to JSON
    json_data = json.dumps(data)

    # Upload to Azure Blob Storage using PUT request
    headers = {
        "x-ms-blob-type": "BlockBlob",
        "Content-Type": "application/json"
    }

    try:
        response = requests.put(sas_url, headers=headers, data=json_data)
        if response.status_code == 201:
            messagebox.showinfo("Success", "Data uploaded successfully.")
        else:
            messagebox.showerror("Upload Failed", f"Status Code: {response.status_code}\n{response.text}")
    except Exception as e:
        messagebox.showerror("Error", str(e))

# Create the GUI
root = tk.Tk()
root.title("Supplier Data Form")

tk.Label(root, text="Supplier Name:").grid(row=0, column=0, sticky="e")
entry_name = tk.Entry(root, width=40)
entry_name.grid(row=0, column=1)

tk.Label(root, text="Email:").grid(row=1, column=0, sticky="e")
entry_email = tk.Entry(root, width=40)
entry_email.grid(row=1, column=1)

tk.Label(root, text="Product:").grid(row=2, column=0, sticky="e")
entry_product = tk.Entry(root, width=40)
entry_product.grid(row=2, column=1)

tk.Label(root, text="Quantity:").grid(row=3, column=0, sticky="e")
entry_quantity = tk.Entry(root, width=40)
entry_quantity.grid(row=3, column=1)

submit_button = tk.Button(root, text="Submit", command=submit_data)
submit_button.grid(row=4, column=0, columnspan=2, pady=10)

root.mainloop()
