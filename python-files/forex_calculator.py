import tkinter as tk
from tkinter import ttk, messagebox

def calculate_position_size():
    """
    Calculates the Forex position size based on user inputs.
    Displays results in a message box and updates output labels.
    """
    try:
        # Get input values from the Entry widgets
        currency_pair = entry_currency_pair.get().strip().upper()
        account_currency = entry_account_currency.get().strip().upper()
        account_size = float(entry_account_size.get())
        risk_ratio_percent = float(entry_risk_ratio.get())
        stop_loss_pips = int(entry_stop_loss_pips.get())
        
        # Get Pip Value per Standard Lot (in Account Currency)
        # This value is crucial and depends on the specific currency pair and your broker.
        # For EUR/USD with a USD account, it's typically $10.
        # For USD/JPY with a JPY account, it's typically 1000 JPY.
        # For USD/CAD with a CAD account, it's typically 10 CAD.
        pip_value_per_std_lot_in_account_currency = float(entry_pip_value_std_lot.get())

        # Get the exchange rate to USD for displaying 'Money in USD'
        # If your account currency is USD, this should be 1.0
        # If your account currency is EUR and you want to see USD value, enter EUR/USD rate (e.g., 1.08)
        account_currency_to_usd_rate = float(entry_acc_curr_to_usd_rate.get())

        # --- Calculations ---

        # 1. Calculate the total risk amount in the account currency
        risk_amount_account_currency = account_size * (risk_ratio_percent / 100)

        # 2. Calculate the value of one pip for one standard lot (100,000 units) in account currency
        # This is directly provided by the user via 'pip_value_per_std_lot_in_account_currency'
        
        # 3. Calculate the value of one pip per single unit of the base currency
        # A standard lot is 100,000 units. So, Pip Value per unit = (Pip Value per Std Lot) / 100,000
        pip_value_per_unit = pip_value_per_std_lot_in_account_currency / 100000

        # 4. Calculate the required position size in units
        # Units = (Risk Amount / (Stop Loss in Pips * Pip Value per Unit))
        if stop_loss_pips == 0 or pip_value_per_unit == 0:
            messagebox.showerror("Input Error", "Stop-Loss (Pips) and Pip Value cannot be zero.")
            return

        units = risk_amount_account_currency / (stop_loss_pips * pip_value_per_unit)

        # 5. Calculate the position size in standard lots
        # 1 Standard Lot = 100,000 units
        sizing_standard_lots = units / 100000

        # 6. Calculate Risk Amount in USD
        risk_amount_usd = risk_amount_account_currency * account_currency_to_usd_rate

        # --- Display Results ---
        label_risk_amount_account_currency.config(text=f"{risk_amount_account_currency:,.2f} {account_currency}")
        label_risk_amount_usd.config(text=f"{risk_amount_usd:,.2f} USD")
        label_units.config(text=f"{units:,.2f} Units")
        label_sizing.config(text=f"{sizing_standard_lots:,.4f} Standard Lots")

    except ValueError:
        messagebox.showerror("Input Error", "Please enter valid numerical values for all fields.")
    except Exception as e:
        messagebox.showerror("Calculation Error", f"An unexpected error occurred: {e}")

# --- GUI Setup ---

# Create the main window
root = tk.Tk()
root.title("FOREX Position Size Calculator")
root.geometry("500x700") # Set initial window size
root.resizable(False, False) # Make window not resizable

# Apply a modern style
style = ttk.Style()
style.theme_use('clam') # 'clam', 'alt', 'default', 'classic'

style.configure('TFrame', background='#e0e0e0')
style.configure('TLabel', background='#e0e0e0', font=('Inter', 10))
style.configure('TEntry', font=('Inter', 10))
style.configure('TButton', font=('Inter', 10, 'bold'), padding=10)
style.map('TButton', background=[('active', '#c0c0c0')])

# Create a main frame for padding and background
main_frame = ttk.Frame(root, padding="20 20 20 20")
main_frame.pack(fill=tk.BOTH, expand=True)

# Create input frame
input_frame = ttk.LabelFrame(main_frame, text="Input Parameters", padding="15 15 15 15")
input_frame.pack(pady=10, fill=tk.X)

# Grid layout for inputs
input_frame.columnconfigure(0, weight=1)
input_frame.columnconfigure(1, weight=2)

row_idx = 0

# Currency Pair
ttk.Label(input_frame, text="Currency Pair (e.g., EUR/USD):").grid(row=row_idx, column=0, sticky="w", pady=5)
entry_currency_pair = ttk.Entry(input_frame)
entry_currency_pair.insert(0, "EUR/USD") # Default value
entry_currency_pair.grid(row=row_idx, column=1, sticky="ew", pady=5)
row_idx += 1

# Account Currency
ttk.Label(input_frame, text="Account Currency (e.g., USD):").grid(row=row_idx, column=0, sticky="w", pady=5)
entry_account_currency = ttk.Entry(input_frame)
entry_account_currency.insert(0, "USD") # Default value
entry_account_currency.grid(row=row_idx, column=1, sticky="ew", pady=5)
row_idx += 1

# Account Size
ttk.Label(input_frame, text="Account Size:").grid(row=row_idx, column=0, sticky="w", pady=5)
entry_account_size = ttk.Entry(input_frame)
entry_account_size.insert(0, "10000") # Default value
entry_account_size.grid(row=row_idx, column=1, sticky="ew", pady=5)
row_idx += 1

# Risk Ratio in Percentage
ttk.Label(input_frame, text="Risk Ratio (%):").grid(row=row_idx, column=0, sticky="w", pady=5)
entry_risk_ratio = ttk.Entry(input_frame)
entry_risk_ratio.insert(0, "1") # Default value
entry_risk_ratio.grid(row=row_idx, column=1, sticky="ew", pady=5)
row_idx += 1

# Stop-Loss in Pips
ttk.Label(input_frame, text="Stop-Loss (Pips):").grid(row=row_idx, column=0, sticky="w", pady=5)
entry_stop_loss_pips = ttk.Entry(input_frame)
entry_stop_loss_pips.insert(0, "50") # Default value
entry_stop_loss_pips.grid(row=row_idx, column=1, sticky="ew", pady=5)
row_idx += 1

# Pip Value per Standard Lot (in Account Currency)
ttk.Label(input_frame, text="Pip Value per Standard Lot (in Account Currency):").grid(row=row_idx, column=0, sticky="w", pady=5)
entry_pip_value_std_lot = ttk.Entry(input_frame)
entry_pip_value_std_lot.insert(0, "10") # Default value (for EUR/USD with USD account)
entry_pip_value_std_lot.grid(row=row_idx, column=1, sticky="ew", pady=5)
row_idx += 1

# Account Currency to USD Exchange Rate
ttk.Label(input_frame, text="Account Currency to USD Rate:").grid(row=row_idx, column=0, sticky="w", pady=5)
entry_acc_curr_to_usd_rate = ttk.Entry(input_frame)
entry_acc_curr_to_usd_rate.insert(0, "1.0") # Default value (if account is USD)
entry_acc_curr_to_usd_rate.grid(row=row_idx, column=1, sticky="ew", pady=5)
row_idx += 1

# Calculate Button
calculate_button = ttk.Button(main_frame, text="Calculate Position Size", command=calculate_position_size)
calculate_button.pack(pady=20)

# Create results frame
results_frame = ttk.LabelFrame(main_frame, text="Calculation Results", padding="15 15 15 15")
results_frame.pack(pady=10, fill=tk.X)

# Grid layout for results
results_frame.columnconfigure(0, weight=1)
results_frame.columnconfigure(1, weight=2)

# Risk Amount (in Account Currency)
ttk.Label(results_frame, text="Risk Amount (Account Currency):").grid(row=0, column=0, sticky="w", pady=5)
label_risk_amount_account_currency = ttk.Label(results_frame, text="")
label_risk_amount_account_currency.grid(row=0, column=1, sticky="w", pady=5)

# Risk Amount (in USD)
ttk.Label(results_frame, text="Risk Amount (USD):").grid(row=1, column=0, sticky="w", pady=5)
label_risk_amount_usd = ttk.Label(results_frame, text="")
label_risk_amount_usd.grid(row=1, column=1, sticky="w", pady=5)

# Units
ttk.Label(results_frame, text="Units:").grid(row=2, column=0, sticky="w", pady=5)
label_units = ttk.Label(results_frame, text="")
label_units.grid(row=2, column=1, sticky="w", pady=5)

# Sizing (Standard Lots)
ttk.Label(results_frame, text="Sizing (Standard Lots):").grid(row=3, column=0, sticky="w", pady=5)
label_sizing = ttk.Label(results_frame, text="")
label_sizing.grid(row=3, column=1, sticky="w", pady=5)

# Start the Tkinter event loop
root.mainloop()