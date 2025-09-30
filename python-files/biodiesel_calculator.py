LITER_TO_GALLON = 3.78541
GRAM_TO_OUNCE = 28.3495

def get_float_input(prompt, default=0.0):
    while True:
        try:
            value = input(prompt).strip()
            return float(value) if value else default
        except ValueError:
            print("Please enter a valid number.")

def calculate_biodiesel(oil_liters, methanol_pct, base_lye, titration):
    methanol_liters = oil_liters * (methanol_pct / 100)
    total_lye_grams = (base_lye + titration) * oil_liters
    oil_gallons = oil_liters / LITER_TO_GALLON
    methanol_gallons = methanol_liters / LITER_TO_GALLON
    lye_ounces = total_lye_grams / GRAM_TO_OUNCE
    
    return {
        'oil_liters': oil_liters,
        'methanol_liters': methanol_liters,
        'lye_grams': total_lye_grams,
        'oil_gallons': oil_gallons,
        'methanol_gallons': methanol_gallons,
        'lye_ounces': lye_ounces
    }

def main():
    print("\nBiodiesel Recipe Calculator")
    print("Inspired by Triangle Biofuels / B100 Supply\n")
    
    oil_liters = get_float_input("Enter oil amount (liters, default 100): ", 100)
    methanol_pct = get_float_input("Enter methanol percentage (%, default 20): ", 20)
    base_lye = get_float_input("Enter base lye amount (g/L, default 5 for NaOH, 7 for KOH): ", 5)
    titration = get_float_input("Enter titration value (g/L, default 0): ", 0)
    
    if oil_liters < 0 or methanol_pct < 0 or base_lye < 0 or titration < 0:
        print("Error: All inputs must be non-negative.")
        return
    
    results = calculate_biodiesel(oil_liters, methanol_pct, base_lye, titration)
    
    print("\n=== The Recipe ===")
    print("Metric:")
    print(f"  Oil:     {results['oil_liters']:.2f} Liters")
    print(f"  Methanol: {results['methanol_liters']:.2f} Liters")
    print(f"  Lye:     {results['lye_grams']:.2f} grams")
    print("\nUS:")
    print(f"  Oil:     {results['oil_gallons']:.2f} Gallons")
    print(f"  Methanol: {results['methanol_gallons']:.2f} Gallons")
    print(f"  Lye:     {results['lye_ounces']:.2f} ounces")
    print("\nRun again to calculate a new recipe.")

if __name__ == "__main__":
    main()