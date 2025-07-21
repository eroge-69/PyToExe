Python 3.13.5 (tags/v3.13.5:6cb20a2, Jun 11 2025, 16:15:46) [MSC v.1943 64 bit (AMD64)] on win32
Enter "help" below or click "Help" above for more information.
>>> import tkinter as tk
... from tkinter import ttk, messagebox, filedialog
... import csv
... 
... # Sample list of cars
... car_list = ["Mahindra Thar 4x4", "Mahindra Scorpio s11 Classic", "Mahindra Scorpio N", "Maruti sizuki Swift", "Hyundai Verna SX"]
... 
... # Main application window
... root = tk.Tk()
... root.title("JB CARS RENTAL")
... root.geometry("900x900")
... 
... # Create a frame to hold all widgets
... frame = ttk.Frame(root, padding="10")
... frame.grid(row=0, column=0, sticky="nsew")
... 
... # Title Label
... title_label = ttk.Label(frame, text="JB CARS RENTAL RECORD SOFTWARE", font=("Arial", 18, "bold"))
... title_label.grid(row=0, column=0, columnspan=2, pady=10)
... 
... # Define all labels and entry widgets
... fields = [
...     ("Car Name", ttk.Combobox(frame, values=car_list, state="readonly")),
...     ("Pickup Date", tk.Entry(frame)),
...     ("Drop Date", tk.Entry(frame)),
...     ("Customer Name", tk.Entry(frame)),
...     ("Customer Age", tk.Entry(frame)),
...     ("Customer Mobile Number", tk.Entry(frame)),
...     ("Customer ID Type", tk.Entry(frame)),
...     ("Customer ID Number", tk.Entry(frame)),
...     ("Customer Address", tk.Entry(frame)),
...     ("Car Pickup Time", tk.Entry(frame)),
...     ("Car Drop Time", tk.Entry(frame)),
...     ("Extra Rent Time", tk.Entry(frame)),
...     ("Rent Payment", tk.Entry(frame)),
...     ("Extra Rent Payment", tk.Entry(frame)),
...     ("Final Rent Payment", tk.Entry(frame, state="readonly")),
...     ("Customer Security Deposit Amount / Bike", tk.Entry(frame)),
...     ("Car Rented By", tk.Entry(frame))
... ]
... 
... entries = {}
... 
... # Display fields in the GUI
... for idx, (label_text, widget) in enumerate(fields):
...     label = ttk.Label(frame, text=label_text)
    label.grid(row=idx+1, column=0, sticky="e", padx=5, pady=2)
    widget.grid(row=idx+1, column=1, sticky="w", padx=5, pady=2)
    entries[label_text] = widget

# Calculate final rent payment
def calculate_final_rent():
    try:
        rent = float(entries["Rent Payment"].get())
        extra = float(entries["Extra Rent Payment"].get())
        total = rent + extra
        entries["Final Rent Payment"].config(state="normal")
        entries["Final Rent Payment"].delete(0, tk.END)
        entries["Final Rent Payment"].insert(0, str(total))
        entries["Final Rent Payment"].config(state="readonly")
    except ValueError:
        messagebox.showerror("Input Error", "Please enter valid numbers for Rent Payment and Extra Rent Payment")

# Save data function
def save_data():
    calculate_final_rent()
    data = {key: widget.get() for key, widget in entries.items()}
    filename = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
    if filename:
        try:
            with open(filename, mode='a', newline='') as file:
                writer = csv.writer(file)
                if file.tell() == 0:
                    writer.writerow(data.keys())
                writer.writerow(data.values())
            messagebox.showinfo("Data Saved", "Customer Rental Record saved successfully.")
        except Exception as e:
            messagebox.showerror("Save Error", f"An error occurred: {e}")

# View saved records function
def view_records():
    filename = filedialog.askopenfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
    if filename:
        try:
            with open(filename, mode='r') as file:
                content = file.read()
            view_window = tk.Toplevel(root)
            view_window.title("Saved Records")
            text_area = tk.Text(view_window, wrap="none")
            text_area.insert(tk.END, content)
            text_area.pack(fill=tk.BOTH, expand=True)
        except Exception as e:
            messagebox.showerror("View Error", f"An error occurred: {e}")

# Buttons
calc_button = ttk.Button(frame, text="Calculate Final Rent", command=calculate_final_rent)
calc_button.grid(row=len(fields)+1, column=0, pady=5)

save_button = ttk.Button(frame, text="Save Record", command=save_data)
save_button.grid(row=len(fields)+1, column=1, pady=5)

view_button = ttk.Button(frame, text="View Saved Records", command=view_records)
view_button.grid(row=len(fields)+2, column=0, columnspan=2, pady=5)

# Run the application
