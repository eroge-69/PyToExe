import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import random

HOSPITAL = "Astitva Balrugnalay"
DOCTOR = "Dr. Prashant Jadhav"

# Function to calculate bill
def generate_bill():
    baby_name = entry_baby.get().strip()
    baby_age = entry_age.get().strip()
    father_name = entry_father.get().strip()
    phone = entry_phone.get().strip()
    room_type = room_var.get()
    try:
        service = float(entry_service.get() or 0)
        medicine = float(entry_medicine.get() or 0)
    except:
        messagebox.showerror("Error", "Enter valid numbers for charges!")
        return

    # Room charges
    room_charge = 0
    if room_type == "General Ward":
        room_charge = 1500
    elif room_type == "Private Room":
        room_charge = 3000
    elif room_type == "ICU":
        room_charge = 5000

    if not baby_name or not father_name:
        messagebox.showwarning("Missing Info", "Please enter baby's name and father's name")
        return

    subtotal = service + medicine + room_charge
    discount = 1000
    total = max(0, subtotal - discount)

    # Generate invoice number & date
    invoice_no = "INV" + str(random.randint(1000, 9999))
    date_time = datetime.now().strftime("%d-%m-%Y %H:%M:%S")

    # Create invoice text
    invoice_text = f"""
    ***************************************
               {HOSPITAL}
             {DOCTOR}
    ***************************************
    Invoice No: {invoice_no}
    Date: {date_time}

    Baby Name     : {baby_name}
    Baby Age      : {baby_age}
    Father's Name : {father_name}
    Contact No.   : {phone}

    Room Type     : {room_type}
    Room Charge   : ₹{room_charge}

    ---------------------------------------
    Service Charges : ₹{service:.2f}
    Medicine Charges: ₹{medicine:.2f}
    Subtotal        : ₹{subtotal:.2f}
    Discount        : -₹{discount}
    ---------------------------------------
    TOTAL BILL      : ₹{total:.2f}
    ***************************************
          THANK YOU - GET WELL SOON
    ***************************************
    """

    # Show invoice in new window
    invoice_window = tk.Toplevel(root)
    invoice_window.title("Invoice")
    invoice_window.configure(bg="#ffe4ec")
    text = tk.Text(invoice_window, wrap="word", font=("Courier", 12), bg="#fff0f5", fg="black")
    text.insert("1.0", invoice_text)
    text.config(state="disabled")
    text.pack(expand=True, fill="both", padx=10, pady=10)

# --- GUI Setup ---
root = tk.Tk()
root.title(f"{HOSPITAL} - Billing System")
root.geometry("700x600")
root.configure(bg="#ffe4ec")

# Header
tk.Label(root, text=HOSPITAL, font=("Arial", 20, "bold"), bg="#ff69b4", fg="white").pack(fill="x", pady=5)
tk.Label(root, text=DOCTOR, font=("Arial", 14), bg="#ffe4ec").pack(pady=5)

# Patient Info
frame1 = tk.LabelFrame(root, text="Patient Information", bg="#ffe4ec", font=("Arial", 12, "bold"))
frame1.pack(fill="x", padx=20, pady=10)

tk.Label(frame1, text="Baby's Name:", bg="#ffe4ec").grid(row=0, column=0, sticky="w", padx=10, pady=5)
entry_baby = tk.Entry(frame1, width=30)
entry_baby.grid(row=0, column=1, pady=5)

tk.Label(frame1, text="Baby's Age:", bg="#ffe4ec").grid(row=1, column=0, sticky="w", padx=10, pady=5)
entry_age = tk.Entry(frame1, width=10)
entry_age.grid(row=1, column=1, pady=5)

tk.Label(frame1, text="Father's Name:", bg="#ffe4ec").grid(row=2, column=0, sticky="w", padx=10, pady=5)
entry_father = tk.Entry(frame1, width=30)
entry_father.grid(row=2, column=1, pady=5)

tk.Label(frame1, text="Contact Number:", bg="#ffe4ec").grid(row=3, column=0, sticky="w", padx=10, pady=5)
entry_phone = tk.Entry(frame1, width=20)
entry_phone.grid(row=3, column=1, pady=5)

# Billing Info
frame2 = tk.LabelFrame(root, text="Billing Information", bg="#ffe4ec", font=("Arial", 12, "bold"))
frame2.pack(fill="x", padx=20, pady=10)

tk.Label(frame2, text="Room Type:", bg="#ffe4ec").grid(row=0, column=0, sticky="w", padx=10, pady=5)
room_var = tk.StringVar(value="General Ward")
room_menu = ttk.Combobox(frame2, textvariable=room_var, values=["General Ward", "Private Room", "ICU"], state="readonly")
room_menu.grid(row=0, column=1, pady=5)

tk.Label(frame2, text="Service Charges (₹):", bg="#ffe4ec").grid(row=1, column=0, sticky="w", padx=10, pady=5)
entry_service = tk.Entry(frame2, width=15)
entry_service.grid(row=1, column=1, pady=5)

tk.Label(frame2, text="Medicine Charges (₹):", bg="#ffe4ec").grid(row=2, column=0, sticky="w", padx=10, pady=5)
entry_medicine = tk.Entry(frame2, width=15)
entry_medicine.grid(row=2, column=1, pady=5)

# Generate Bill Button
tk.Button(root, text="Generate Bill", command=generate_bill,
          bg="#ff69b4", fg="white", font=("Arial", 14, "bold")).pack(pady=20)

root.mainloop()
