import tkinter as tk

def calculate_angle():
    try:
        distance = float(distance_entry.get())
        wind = float(wind_entry.get())
        
        # Simple example formula (you can adjust this)
        # For now: angle = distance/10 + wind*2
        angle = distance / 10 + wind * 2
        
        result_label.config(text=f"Recommended Angle: {angle:.2f}")
    except ValueError:
        result_label.config(text="Please enter valid numbers.")

# GUI setup
root = tk.Tk()
root.title("DDTank Calculator")

tk.Label(root, text="Distance:").grid(row=0, column=0, padx=10, pady=5)
distance_entry = tk.Entry(root)
distance_entry.grid(row=0, column=1, padx=10, pady=5)

tk.Label(root, text="Wind:").grid(row=1, column=0, padx=10, pady=5)
wind_entry = tk.Entry(root)
wind_entry.grid(row=1, column=1, padx=10, pady=5)

calc_button = tk.Button(root, text="Calculate", command=calculate_angle)
calc_button.grid(row=2, column=0, columnspan=2, pady=10)

result_label = tk.Label(root, text="Recommended Angle: ")
result_label.grid(row=3, column=0, columnspan=2, pady=10)

root.mainloop()
