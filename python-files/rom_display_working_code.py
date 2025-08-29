import tkinter as tk
from tkinter import ttk, messagebox

FUEL_TYPES = ["Diesel", "Unleaded", "MGO", "KERO", "ADBLUE", "HVO"]

def calculate_closing_dips():
    summary_text.config(state="normal")
    summary_text.delete("1.0", tk.END)
    for i in range(6):
        tank = f"Tank {i+1}"
        fuel_type = fuel_type_vars[i].get()
        opening_dip = opening_dip_entries[i].get()
        delivery = delivery_entries[i].get()
        sales = sales_entries[i].get()

        if not fuel_type or not opening_dip or not delivery or not sales:
            summary_text.insert(tk.END, f"{tank}: Incomplete data. Skipped.\n\n")
            continue

        try:
            opening_dip = float(opening_dip)
            delivery = float(delivery)
            sales = float(sales)
            closing_dip = opening_dip + delivery - sales

            summary_text.insert(tk.END, f"{tank} ({fuel_type}):\n")
            summary_text.insert(tk.END, f"  Opening Dip: {opening_dip}\n")
            summary_text.insert(tk.END, f"  Delivery: {delivery}\n")
            summary_text.insert(tk.END, f"  Sales: {sales}\n")
            summary_text.insert(tk.END, f"  Closing Dip: {closing_dip}\n\n")
        except ValueError:
            summary_text.insert(tk.END, f"{tank}: Invalid numeric input. Skipped.\n\n")
    summary_text.config(state="disabled")

def clear_tank_fields(index):
    fuel_type_vars[index].set("")
    opening_dip_entries[index].delete(0, tk.END)
    delivery_entries[index].delete(0, tk.END)
    sales_entries[index].delete(0, tk.END)

def show_help():
    help_window = tk.Toplevel(root)
    help_window.title("Help - Dip Calculation")
    help_text = tk.Text(help_window, wrap="word", width=80, height=20)
    help_text.pack(padx=10, pady=10)
    help_message = (
        "🧪 How Dip Readings Work for ROM Reports\n\n"
        "Dip Reading is the measurement of fuel level in a tank, usually taken with a dipstick or automatic gauge. "
        "It's essential for calculating stock movement.\n\n"
        "📅 Scenario Example:\n"
        "- The tank gauge stopped reading on 28/08/2025\n"
        "- The store needs a ROM report for July (07)\n\n"
        "To calculate the ROM for July, you need:\n\n"
        "1. Opening Dip for July:\n"
        "   - This is the closing dip from June 30th, 2025\n"
        "   - If available, use the last recorded dip from June\n\n"
        "2. Deliveries in July:\n"
        "   - Total volume of fuel delivered to the tank during July\n\n"
        "3. Sales in July:\n"
        "   - Total volume of fuel dispensed from the tank during July\n\n"
        "4. Closing Dip for July:\n"
        "   - If the gauge stopped on 28/08/2025, use the last known dip before the failure\n"
        "   - If no dip is available for July 31st, estimate it using:\n"
        "     Closing Dip (July) = Opening Dip (July) + Deliveries (July) - Sales (July)\n\n"
        "This calculated closing dip becomes the opening dip for August, which helps maintain continuity in ROM tracking."
    )
    help_text.insert(tk.END, help_message)
    help_text.config(state="disabled")

root = tk.Tk()
root.title("ROM Reporting App")

main_frame = tk.Frame(root)
main_frame.pack(fill="both", expand=True)

canvas = tk.Canvas(main_frame)
scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
scrollable_frame = tk.Frame(canvas)

scrollable_frame.bind(
    "<Configure>",
    lambda e: canvas.configure(
        scrollregion=canvas.bbox("all")
    )
)

canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
canvas.configure(yscrollcommand=scrollbar.set)

canvas.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")

# Enable mouse wheel scrolling
def _on_mousewheel(event):
    canvas.yview_scroll(int(-1*(event.delta/120)), "units")

canvas.bind_all("<MouseWheel>", _on_mousewheel)  # Windows
canvas.bind_all("<Button-4>", lambda e: canvas.yview_scroll(-1, "units"))  # Linux scroll up
canvas.bind_all("<Button-5>", lambda e: canvas.yview_scroll(1, "units"))   # Linux scroll down

# Help button at the top
help_button = ttk.Button(scrollable_frame, text="Help", command=show_help)
help_button.pack(padx=10, pady=10)

fuel_type_vars = []
opening_dip_entries = []
delivery_entries = []
sales_entries = []

for i in range(6):
    frame = ttk.LabelFrame(scrollable_frame, text=f"Tank {i+1}")
    frame.pack(padx=10, pady=5, fill="x")

    ttk.Label(frame, text="Fuel Type:").grid(row=0, column=0, padx=5, pady=2)
    fuel_type_var = tk.StringVar()
    fuel_type_menu = ttk.Combobox(frame, textvariable=fuel_type_var, values=FUEL_TYPES, state="readonly")
    fuel_type_menu.grid(row=0, column=1, padx=5, pady=2)
    fuel_type_vars.append(fuel_type_var)

    ttk.Label(frame, text="Opening Dip:").grid(row=1, column=0, padx=5, pady=2)
    opening_dip_entry = ttk.Entry(frame)
    opening_dip_entry.grid(row=1, column=1, padx=5, pady=2)
    opening_dip_entries.append(opening_dip_entry)

    ttk.Label(frame, text="Delivery:").grid(row=2, column=0, padx=5, pady=2)
    delivery_entry = ttk.Entry(frame)
    delivery_entry.grid(row=2, column=1, padx=5, pady=2)
    delivery_entries.append(delivery_entry)

    ttk.Label(frame, text="Sales:").grid(row=3, column=0, padx=5, pady=2)
    sales_entry = ttk.Entry(frame)
    sales_entry.grid(row=3, column=1, padx=5, pady=2)
    sales_entries.append(sales_entry)

    clear_button = ttk.Button(frame, text="Clear", command=lambda idx=i: clear_tank_fields(idx))
    clear_button.grid(row=4, column=1, padx=5, pady=2, sticky="e")

calculate_button = ttk.Button(scrollable_frame, text="Calculate Closing Dips", command=calculate_closing_dips)
calculate_button.pack(padx=10, pady=10)

summary_frame = ttk.LabelFrame(scrollable_frame, text="ROM Summary")
summary_frame.pack(padx=10, pady=10, fill="both", expand=True)

summary_text = tk.Text(summary_frame, height=20, wrap="word")
summary_text.pack(side="left", fill="both", expand=True)

summary_scrollbar = ttk.Scrollbar(summary_frame, orient="vertical", command=summary_text.yview)
summary_scrollbar.pack(side="right", fill="y")
summary_text.config(yscrollcommand=summary_scrollbar.set, state="disabled")

root.mainloop()
