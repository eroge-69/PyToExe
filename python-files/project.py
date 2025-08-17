import tkinter as tk

# Create main window
root = tk.Tk()
root.title("Osama Shaikh Project - 422241 - Universal Converter")
root.configure(bg="lightblue")
root.geometry("750x500")

# -------------------- Conversion Function --------------------
def convert():
    try:
        value = float(entry_value.get())
        choice = unit_choice.get()

        # Clear previous results
        t1.delete("1.0", tk.END)
        t2.delete("1.0", tk.END)
        t3.delete("1.0", tk.END)

        if choice == "Weight (KG)":
            gram = value * 1000
            pound = value * 2.20462
            ounce = value * 35.274

            t1.insert(tk.END, f"{gram:.2f} g")
            t2.insert(tk.END, f"{pound:.2f} lb")
            t3.insert(tk.END, f"{ounce:.2f} oz")

            l1.config(text="Gram")
            l2.config(text="Pound")
            l3.config(text="Ounce")

        elif choice == "Temperature (°C)":
            f = (value * 9/5) + 32
            k = value + 273.15

            t1.insert(tk.END, f"{f:.2f} °F")
            t2.insert(tk.END, f"{k:.2f} K")
            t3.insert(tk.END, "-")  # only 2 outputs here

            l1.config(text="Fahrenheit")
            l2.config(text="Kelvin")
            l3.config(text="---")

        elif choice == "Pressure (atm)":
            pa = value * 101325
            mmhg = value * 760

            t1.insert(tk.END, f"{pa:.2f} Pa")
            t2.insert(tk.END, f"{mmhg:.2f} mmHg")
            t3.insert(tk.END, "-")  # only 2 outputs here

            l1.config(text="Pascal")
            l2.config(text="mmHg")
            l3.config(text="---")

    except ValueError:
        for box in [t1, t2, t3]:
            box.delete("1.0", tk.END)
            box.insert(tk.END, "Invalid input")

# -------------------- Input Section --------------------
label1 = tk.Label(root, text="Enter Value:", bg="lightblue", font=("Arial", 12))
label1.grid(row=0, column=0, padx=10, pady=10)

entry_value = tk.StringVar()
entry = tk.Entry(root, textvariable=entry_value, width=20)
entry.grid(row=0, column=1, padx=10, pady=10)

# Dropdown for unit type
unit_choice = tk.StringVar(value="Weight (KG)")
options = ["Weight (KG)", "Temperature (°C)", "Pressure (atm)"]
dropdown = tk.OptionMenu(root, unit_choice, *options)
dropdown.config(bg="yellow", font=("Arial", 10, "bold"))
dropdown.grid(row=0, column=2, padx=10, pady=10)

# Convert button
button = tk.Button(root, text="Convert", command=convert, bg="orange", font=("Arial", 10, "bold"))
button.grid(row=0, column=3, padx=10, pady=10)

# -------------------- Results Section --------------------
l1 = tk.Label(root, text="Result 1", bg="lightblue", font=("Arial", 12))
l2 = tk.Label(root, text="Result 2", bg="lightblue", font=("Arial", 12))
l3 = tk.Label(root, text="Result 3", bg="lightblue", font=("Arial", 12))
l1.grid(row=1, column=0)
l2.grid(row=1, column=1)
l3.grid(row=1, column=2)

t1 = tk.Text(root, height=5, width=25, bg="lightyellow")
t2 = tk.Text(root, height=5, width=25, bg="lightgreen")
t3 = tk.Text(root, height=5, width=25, bg="lightpink")
t1.grid(row=2, column=0, padx=5, pady=5)
t2.grid(row=2, column=1, padx=5, pady=5)
t3.grid(row=2, column=2, padx=5, pady=5)

# Start GUI loop
root.mainloop()
