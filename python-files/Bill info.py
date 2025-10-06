import tkinter as tk
from tkinter import messagebox

def generate_and_copy():
    username = entry_username.get()
    payment_date = entry_payment_date.get()
    last_number = entry_last_number.get()
    ref_id = entry_ref_id.get()
    id_status = status_var.get()

    if not (username and payment_date and last_number and ref_id and id_status):
        messagebox.showwarning("Warning", "সবগুলো ফিল্ড পূরণ করুন!")
        return

    # বিলিং কপি টেক্সট তৈরি
    bill_text = f"""User Name: {username}
Payment Date: {payment_date}
Last Number: {last_number}
Ref ID: {ref_id}
ID Status: {id_status}"""

    # ক্লিপবোর্ডে কপি
    root.clipboard_clear()
    root.clipboard_append(bill_text)
    root.update()

    messagebox.showinfo("Success", "Billing Copy ক্লিপবোর্ডে কপি হয়েছে!")

# Tkinter UI
root = tk.Tk()
root.title("Billing Form")

tk.Label(root, text="User Name:").grid(row=0, column=0, padx=10, pady=5, sticky="e")
entry_username = tk.Entry(root, width=30)
entry_username.grid(row=0, column=1, pady=5)

tk.Label(root, text="Payment Date:").grid(row=1, column=0, padx=10, pady=5, sticky="e")
entry_payment_date = tk.Entry(root, width=30)
entry_payment_date.grid(row=1, column=1, pady=5)

tk.Label(root, text="Last Number:").grid(row=2, column=0, padx=10, pady=5, sticky="e")
entry_last_number = tk.Entry(root, width=30)
entry_last_number.grid(row=2, column=1, pady=5)

tk.Label(root, text="Ref ID:").grid(row=3, column=0, padx=10, pady=5, sticky="e")
entry_ref_id = tk.Entry(root, width=30)
entry_ref_id.grid(row=3, column=1, pady=5)

tk.Label(root, text="ID Status:").grid(row=4, column=0, padx=10, pady=5, sticky="e")
status_var = tk.StringVar(value="Enable")
status_menu = tk.OptionMenu(root, status_var, "Enable", "Disable")
status_menu.config(width=28)
status_menu.grid(row=4, column=1, pady=5)

generate_btn = tk.Button(root, text="Generate & Copy", command=generate_and_copy, bg="lightblue")
generate_btn.grid(row=5, column=0, columnspan=2, pady=15)

root.mainloop()
