import tkinter as tk

def calculate_lot_size():
    try:
        risk = float(risk_entry.get())
        pips = float(pips_entry.get())
        if pips == 0:
            result_label.config(text="Pips cannot be 0")
            return
        lot_size = risk / (pips * 10)  # GBPUSD standard pip value $10 per lot
        result_label.config(text=f"Lot Size: {lot_size:.2f}")
    except:
        result_label.config(text="Invalid input")

# Window setup
root = tk.Tk()
root.title("GBP/USD Lot Size Calculator")
root.geometry("350x250")
root.configure(bg="#f5f5f5")  # Light mode background

# Risk Amount input
tk.Label(root, text="Risk Amount ($):", bg="#f5f5f5", font=("Arial", 12, "bold")).pack(pady=5)
risk_entry = tk.Entry(root, font=("Arial", 12), justify="center", bg="white", fg="black")
risk_entry.pack(pady=5)
risk_entry.insert(0, "30")  # Default value

# Pips input
tk.Label(root, text="Pips:", bg="#f5f5f5", font=("Arial", 12, "bold")).pack(pady=5)
pips_entry = tk.Entry(root, font=("Arial", 12), justify="center", bg="white", fg="black")
pips_entry.pack(pady=5)
pips_entry.insert(0, "1.0")  # Default value

# Calculate button
tk.Button(root, text="Calculate Lot Size", command=calculate_lot_size,
          bg="#4da6ff", fg="white", font=("Arial", 12, "bold"),
          width=20, height=2, relief="raised").pack(pady=10)

# Result display
result_label = tk.Label(root, text="Lot Size: ", bg="#f5f5f5", font=("Arial", 14, "bold"))
result_label.pack(pady=10)

root.mainloop()
