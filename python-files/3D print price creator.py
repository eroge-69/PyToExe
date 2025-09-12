# 3D Print Price Calculator with Profit
# Works in Python 3.x - Copy this entire script into VS Code or Notepad and save as "3D_print_pricing.py"

def calculate_price():
    print("=== 3D Print Price Calculator ===\n")

    # --- Input Costs ---
    filament_cost_per_kg = float(input("Filament cost per kg (€): ") or 20)
    weight_g = float(input("Print weight (grams): ") or 100)
    print_time_h = float(input("Print time (hours): ") or 2)
    electricity_cost_kwh = float(input("Electricity cost per kWh (€): ") or 0.20)
    printer_power_w = float(input("Average printer power draw (W): ") or 120)
    labor_rate = float(input("Your labor rate per hour (€): ") or 10)
    handling_time_h = float(input("Handling/finishing time (hours): ") or 0.25)
    platform_fee_percent = float(input("Platform fee % (Etsy ~6.5): ") or 6.5)

    # --- Calculate Base Costs ---
    filament_used_kg = weight_g / 1000
    filament_cost = filament_used_kg * filament_cost_per_kg
    energy_cost = (printer_power_w / 1000) * print_time_h * electricity_cost_kwh
    labor_cost = labor_rate * handling_time_h
    subtotal = filament_cost + energy_cost + labor_cost
    platform_fee = subtotal * (platform_fee_percent / 100)

    print(f"\nBase Material Cost: €{filament_cost:.2f}")
    print(f"Energy Cost: €{energy_cost:.2f}")
    print(f"Labor Cost: €{labor_cost:.2f}")
    print(f"Platform Fee: €{platform_fee:.2f}")

    # --- Profit Calculation ---
    print("\nHow do you want to specify profit?\n 1) Markup on COST (e.g. 30% markup over your costs)\n 2) Desired profit as % of FINAL PRICE (advanced)")
    profit_mode = input("Choose (1/2): ").strip() or "1"

    if profit_mode == "1":
        markup_percent = float(input("Markup on cost (%): ") or 30)
        profit = subtotal * (markup_percent / 100)
        final_price = subtotal + platform_fee + profit
    else:
        desired_profit_percent = float(input("Desired profit as % of FINAL price: ") or 20)
        final_price = (subtotal + platform_fee) / (1 - desired_profit_percent / 100)
        profit = final_price - (subtotal + platform_fee)

    print("\n=== PRICE CALCULATION SUMMARY ===")
    print(f"Subtotal (Cost before profit): €{subtotal:.2f}")
    print(f"Profit: €{profit:.2f}")
    print(f"Suggested Selling Price: €{final_price:.2f}")

if __name__ == "__main__":
    calculate_price()
