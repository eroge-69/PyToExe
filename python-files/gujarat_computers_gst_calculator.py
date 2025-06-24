import tkinter as tk
from tkinter import ttk

def calculate_gst_discount():
    try:
        # Get inputs
        price_with_gst = float(entry_price.get())
        gst_rate = float(combo_gst_rate.get().replace('%', ''))
        discount_rate = float(entry_discount.get())

        # Calculate base price and GST amount
        base_price = price_with_gst / (1 + gst_rate / 100)
        gst_amount = price_with_gst - base_price

        # Apply discount on GST
        discounted_gst = gst_amount * (1 - discount_rate / 100)
        final_price = base_price + discounted_gst

        # Display results
        label_base_price.config(text=f"Base Price: ₹{base_price:.2f}")
        label_gst_amount.config(text=f"Original GST Amount ({gst_rate}%): ₹{gst_amount:.2f}")
        label_discounted_gst.config(text=f"Discounted GST Amount ({discount_rate}% off): ₹{discounted_gst:.2f}")
        label_final_price.config(text=f"Final Sale Price: ₹{final_price:.2f}")
    except ValueError:
        label_base_price.config(text="Please enter valid numeric values.")
        label_gst_amount.config(text="")
        label_discounted_gst.config(text="")
        label_final_price.config(text="")

# Create main window
root = tk.Tk()
root.title("Gujarat Computers - GST Calculator")

# Branding header
header = tk.Label(root, text="Gujarat Computers GST Calculator", font=("Arial", 16, "bold"), fg="blue")
header.grid(row=0, column=0, columnspan=2, pady=10)

# Price input
tk.Label(root, text="Product Price (GST Included):").grid(row=1, column=0, padx=10, pady=5, sticky='e')
entry_price = tk.Entry(root)
entry_price.grid(row=1, column=1, padx=10, pady=5)

# GST rate selection
tk.Label(root, text="GST Category (%):").grid(row=2, column=0, padx=10, pady=5, sticky='e')
combo_gst_rate = ttk.Combobox(root, values=[f"{i}%" for i in range(5, 29)], width=10)
combo_gst_rate.grid(row=2, column=1, padx=10, pady=5)
combo_gst_rate.set("18%")  # Default GST rate

# Discount input
tk.Label(root, text="GST Discount (%):").grid(row=3, column=0, padx=10, pady=5, sticky='e')
entry_discount = tk.Entry(root)
entry_discount.grid(row=3, column=1, padx=10, pady=5)
entry_discount.insert(0, "10")  # Default discount

# Calculate button
btn_calculate = tk.Button(root, text="Calculate", command=calculate_gst_discount)
btn_calculate.grid(row=4, column=0, columnspan=2, pady=10)

# Result labels
label_base_price = tk.Label(root, text="Base Price: ")
label_base_price.grid(row=5, column=0, columnspan=2, pady=2)

label_gst_amount = tk.Label(root, text="Original GST Amount: ")
label_gst_amount.grid(row=6, column=0, columnspan=2, pady=2)

label_discounted_gst = tk.Label(root, text="Discounted GST Amount: ")
label_discounted_gst.grid(row=7, column=0, columnspan=2, pady=2)

label_final_price = tk.Label(root, text="Final Sale Price: ")
label_final_price.grid(row=8, column=0, columnspan=2, pady=2)

# Run the application
root.mainloop()
