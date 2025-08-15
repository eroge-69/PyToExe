## CHANGES MADE
# - Added More Currencies: Expanded the list of default values for the Comboboxes.
# - Numeric Input Validation: Added validation to ensure the units entry is a valid number. If not, an error message is displayed.
# - Styling and Layout Adjustments:
#    Adjusted window size for better layout.
#    Added padding around widgets for better spacing.
#    Set default values for the Comboboxes.
#    Styled the output label with background color and sunken relief.
#    Added padding to elements for better user experience.

import requests
from tkinter import *
from tkinter import ttk
from tkinter import messagebox

def convert():
    try:
        base = base_currency.get()
        units = float(units_currency_var.get())
        other = other_currency.get()
        
        # Make a request to get the exchange rate data
        x = requests.get('https://api.exchangerate-api.com/v4/latest/' + base)
        response = x.json()
        
        # Calculate the conversion
        conversion = round(units * response['rates'][other], 2)
        
        # Set the output variable to display the conversion result
        output_var.set(f'{units} {base} = {conversion} {other}')
    except ValueError:
        messagebox.showerror("Input Error", "Please enter a valid number for units.")
    except KeyError:
        messagebox.showerror("Conversion Error", "Invalid currency code.")
    except requests.exceptions.RequestException as e:
        messagebox.showerror("Request Error", f"Failed to fetch exchange rates: {e}")

# Create the main window
window = Tk()
window.title('Currency Converter')
window.geometry('400x200')

# Title Label
title = Label(
    master=window, 
    text="Currency Converter", 
    font="Calibri 24 bold"
)
title.pack(pady=10)

# Input fields frame
input_frame = Frame(master=window)

# Units entry
units_currency_var = StringVar()
units_currency = Entry(
    master=input_frame, 
    width=10, 
    textvariable=units_currency_var
)
units_currency.pack(side='left', padx=5)

# Base currency Combobox
currencies = ["GBP", "HKD", "NGN", "USD", "PHP", "CAD", "GHS", "EUR", "JPY", "AUD", "CHF", "CNY", "INR"]
base_currency = ttk.Combobox(
    master=input_frame, 
    width=5,
    values=currencies, 
    state="readonly",
)
base_currency.current(0)
base_currency.pack(side='left', padx=5)

# "to" label
to_text = Label(
    master=input_frame, 
    text="to"
)
to_text.pack(side='left', padx=5)

# Other currency Combobox
other_currency = ttk.Combobox(
    master=input_frame, 
    width=5,
    values=currencies, 
    state="readonly",
)
other_currency.current(1)
other_currency.pack(side='left', padx=5)

# Pack the input frame
input_frame.pack(pady=10)

# Output label
output_var = StringVar()
output = Label(
    master=window, 
    text="Output", 
    font="Calibri 18", 
    textvariable=output_var,
    bg='white',
    width=30,
    relief='sunken'
)
output.pack(pady=10)

# Convert button
convert_btn = Button(
    master=window, 
    text="Convert", 
    fg="blue", 
    command=convert,
    width=20
)
convert_btn.pack(pady=10)

# Run the application
window.mainloop()