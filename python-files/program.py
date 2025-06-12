import tkinter as tk
from tkinter import ttk

def predict_price(neighborhood, style, bedrooms, bathrooms):
    # Coefficients from your model
    const = -383300
    coef_bathrooms = 99960
    coef_bedrooms = 173200
    coef_lodge = 168500
    coef_victorian = 70560
    coef_B = 522900
    coef_C = -7168.63

    # Dummy variables
    is_B = 1 if neighborhood == 'B' else 0
    is_C = 1 if neighborhood == 'C' else 0
    is_lodge = 1 if style == 'lodge' else 0
    is_victorian = 1 if style == 'victorian' else 0

    # Predict price
    price = (const +
             coef_bathrooms * bathrooms +
             coef_bedrooms * bedrooms +
             coef_lodge * is_lodge +
             coef_victorian * is_victorian +
             coef_B * is_B +
             coef_C * is_C)

    return round(price, 2)

# GUI Setup
root = tk.Tk()
root.title("House Price Predictor")

# Dropdowns and Entry Fields
ttk.Label(root, text="Neighborhood:").grid(column=0, row=0, padx=10, pady=5, sticky='w')
neighborhood_var = tk.StringVar()
neighborhood_dropdown = ttk.Combobox(root, textvariable=neighborhood_var, values=['A', 'B', 'C'])
neighborhood_dropdown.grid(column=1, row=0)
neighborhood_dropdown.current(0)

ttk.Label(root, text="Style:").grid(column=0, row=1, padx=10, pady=5, sticky='w')
style_var = tk.StringVar()
style_dropdown = ttk.Combobox(root, textvariable=style_var, values=['ranch', 'lodge', 'victorian'])
style_dropdown.grid(column=1, row=1)
style_dropdown.current(0)

ttk.Label(root, text="Bedrooms:").grid(column=0, row=2, padx=10, pady=5, sticky='w')
bedrooms_entry = ttk.Entry(root)
bedrooms_entry.grid(column=1, row=2)

ttk.Label(root, text="Bathrooms:").grid(column=0, row=3, padx=10, pady=5, sticky='w')
bathrooms_entry = ttk.Entry(root)
bathrooms_entry.grid(column=1, row=3)

# Output Label
result_label = ttk.Label(root, text="Predicted Price: $0.00", font=('Helvetica', 14))
result_label.grid(column=0, row=5, columnspan=2, pady=10)

# Calculate Button
def calculate():
    try:
        neighborhood = neighborhood_var.get()
        style = style_var.get()
        bedrooms = int(bedrooms_entry.get())
        bathrooms = int(bathrooms_entry.get())
        price = predict_price(neighborhood, style, bedrooms, bathrooms)
        result_label.config(text=f"Predicted Price: ${price:,.2f}")
    except ValueError:
        result_label.config(text="Please enter valid numbers.")

ttk.Button(root, text="Calculate", command=calculate).grid(column=0, row=4, columnspan=2, pady=10)

root.mainloop()
