import tkinter as tk
from tkinter import messagebox

def hdx_worth_index(price, years_of_use, resale_value, brand_new,
                    need_score, fit_score, quality_score, spending_tolerance):
    """
    Calculates the HDX Worth Index. This is a helper function for the GUI.
    """
    # Step 0: Convert price to “price per year”
    if brand_new:
        adjusted_years = 0.8 * years_of_use
    else:
        adjusted_years = years_of_use

    effective_price = price - resale_value
    price_per_year = effective_price / adjusted_years

    # Step 1: Score value
    value_score = need_score + fit_score + quality_score

    # Red-flag overrides (auto "No")
    overrides = []
    if value_score <= 4 and price_per_year > 1000:
        overrides.append("Red-flag: Value score is low and price per year is high. You may not need this item.")
    if quality_score == 0 and need_score == 4:
        overrides.append("Red-flag: Quality is 0 on a mission-critical item. Don't risk it.")
    
    if overrides:
        return {
            'overrides_triggered': overrides,
            'hdx_index': "N/A (Override)",
            'bep_break_even_price': "N/A",
            'stoplight_rule_pass': False,
        }

    # Step 2: Compute the index
    if value_score == 0:
        hdx_index = float('inf')
    else:
        hdx_index = price_per_year / value_score

    # Step 3: Stoplight rule
    k_values = {'frugal': 150, 'balanced': 250, 'premium': 400}
    if isinstance(spending_tolerance, str):
        k = k_values.get(spending_tolerance.lower(), 250)
    elif isinstance(spending_tolerance, (int, float)):
        k = spending_tolerance
    else:
        k = k_values['balanced']

    bep = k * value_score * years_of_use
    stoplight_rule_pass = effective_price <= bep

    return {
        'price_per_year': f"₹{price_per_year:.2f}",
        'value_score': value_score,
        'hdx_index': f"{hdx_index:.2f}",
        'bep_break_even_price': f"₹{bep:.2f}",
        'stoplight_rule_pass': stoplight_rule_pass,
        'overrides_triggered': overrides
    }

def calculate_hdx():
    """Function to get user input from the GUI and display results."""
    try:
        price = float(entry_price.get())
        years = float(entry_years.get())
        resale = float(entry_resale.get())
        brand_new = var_brand_new.get()
        
        need = int(entry_need.get())
        fit = int(entry_fit.get())
        quality = int(entry_quality.get())
        
        tolerance_map = {0: 'frugal', 1: 'balanced', 2: 'premium'}
        tolerance_index = var_tolerance.get()
        tolerance = tolerance_map.get(tolerance_index)
        
        result = hdx_worth_index(price, years, resale, brand_new,
                                 need, fit, quality, tolerance)
        
        # Display results in the output box
        output_text.delete(1.0, tk.END) # Clear previous text
        
        if result.get('overrides_triggered'):
            output_text.insert(tk.END, "WARNING: RED-FLAG OVERRIDES\n\n")
            for override in result['overrides_triggered']:
                output_text.insert(tk.END, f"- {override}\n")
            output_text.insert(tk.END, "\nRecommendation: **DO NOT BUY**")
        else:
            output_text.insert(tk.END, f"Price per Year: {result['price_per_year']}\n")
            output_text.insert(tk.END, f"Value Score (V): {result['value_score']}\n")
            output_text.insert(tk.END, f"**HDX Index**: {result['hdx_index']}\n")
            output_text.insert(tk.END, f"Break-Even Price (BEP): {result['bep_break_even_price']}\n")
            
            if result['stoplight_rule_pass']:
                output_text.insert(tk.END, "\nStoplight Rule: **BUY OK**")
            else:
                output_text.insert(tk.END, "\nStoplight Rule: **SKIP** (Price > BEP)")

    except ValueError:
        messagebox.showerror("Invalid Input", "Please enter valid numbers for all fields.")

# --- Set up the main GUI window ---
root = tk.Tk()
root.title("HDX Worth Index Calculator")
root.geometry("400x550")
root.configure(bg="#f0f0f0")

# Create a main frame for padding
main_frame = tk.Frame(root, padx=20, pady=20, bg="#f0f0f0")
main_frame.pack(fill=tk.BOTH, expand=True)

# Input Section
input_frame = tk.LabelFrame(main_frame, text="Item Details", padx=15, pady=10, bg="white")
input_frame.pack(fill="x", pady=10)

labels = ["Price (₹):", "Years of Use (Y):", "Resale Value (R):"]
entries = {}
for i, label_text in enumerate(labels):
    row_frame = tk.Frame(input_frame, bg="white")
    row_frame.pack(fill="x", pady=2)
    label = tk.Label(row_frame, text=label_text, bg="white", width=15, anchor="w")
    label.pack(side="left")
    entry = tk.Entry(row_frame)
    entry.pack(side="right", expand=True, fill="x")
    entries[label_text] = entry

entry_price = entries["Price (₹):"]
entry_years = entries["Years of Use (Y):"]
entry_resale = entries["Resale Value (R):"]

var_brand_new = tk.BooleanVar(value=True)
check_brand_new = tk.Checkbutton(input_frame, text="Apply 20% safety haircut (New item)", bg="white", variable=var_brand_new)
check_brand_new.pack(anchor="w", pady=(5, 0))

# Scores Section
scores_frame = tk.LabelFrame(main_frame, text="Value Scores (V)", padx=15, pady=10, bg="white")
scores_frame.pack(fill="x", pady=10)

score_labels = ["Need (0-4):", "Fit (0-3):", "Quality (0-3):"]
score_entries = {}
for i, label_text in enumerate(score_labels):
    row_frame = tk.Frame(scores_frame, bg="white")
    row_frame.pack(fill="x", pady=2)
    label = tk.Label(row_frame, text=label_text, bg="white", width=15, anchor="w")
    label.pack(side="left")
    entry = tk.Entry(row_frame)
    entry.pack(side="right", expand=True, fill="x")
    score_entries[label_text] = entry

entry_need = score_entries["Need (0-4):"]
entry_fit = score_entries["Fit (0-3):"]
entry_quality = score_entries["Quality (0-3):"]

# Spending Tolerance Section
tolerance_frame = tk.LabelFrame(main_frame, text="Spending Tolerance (k)", padx=15, pady=10, bg="white")
tolerance_frame.pack(fill="x", pady=10)

var_tolerance = tk.IntVar(value=1)
radio_frugal = tk.Radiobutton(tolerance_frame, text="Frugal (₹150)", variable=var_tolerance, value=0, bg="white")
radio_balanced = tk.Radiobutton(tolerance_frame, text="Balanced (₹250)", variable=var_tolerance, value=1, bg="white")
radio_premium = tk.Radiobutton(tolerance_frame, text="Premium (₹400)", variable=var_tolerance, value=2, bg="white")
radio_frugal.pack(anchor="w")
radio_balanced.pack(anchor="w")
radio_premium.pack(anchor="w")

# Calculate Button
calculate_button = tk.Button(main_frame, text="Calculate HDX Index", command=calculate_hdx, bg="#4CAF50", fg="white", font=("Helvetica", 12, "bold"))
calculate_button.pack(pady=10, fill="x")

# Output Section
output_frame = tk.LabelFrame(main_frame, text="Results", padx=15, pady=10, bg="white")
output_frame.pack(fill="x", pady=10)

output_text = tk.Text(output_frame, height=8, width=40, state="normal", font=("Courier", 10))
output_text.pack(fill="both", expand=True)

# Start the GUI
root.mainloop()9