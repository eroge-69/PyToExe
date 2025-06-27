
import tkinter as tk
from tkinter import messagebox
from reportlab.pdfgen import canvas
import os

def amount_in_words(n):
    return f"{n} only"

def print_cheque():
    payee = payee_entry.get()
    amount = amount_entry.get()
    date = date_entry.get()

    if not payee or not amount or not date:
        messagebox.showerror("Error", "All fields are mandatory.")
        return

    try:
        amount_float = float(amount)
    except ValueError:
        messagebox.showerror("Error", "Amount must be a number.")
        return

    c = canvas.Canvas("cheque.pdf", pagesize=(600, 200))
    c.drawString(50, 160, f"Date: {date}")
    c.drawString(50, 130, f"Payee: {payee}")
    c.drawString(50, 100, f"Amount (in words): {amount_in_words(amount)}")
    c.drawString(450, 130, f"Rs. {amount}")
    c.save()

    os.startfile("cheque.pdf", "print")
    messagebox.showinfo("Success", "Cheque sent to printer.")

root = tk.Tk()
root.title("HDFC Cheque Print Software")

tk.Label(root, text="Payee Name:").grid(row=0, column=0, sticky="w")
payee_entry = tk.Entry(root, width=40)
payee_entry.grid(row=0, column=1)

tk.Label(root, text="Amount (Rs.):").grid(row=1, column=0, sticky="w")
amount_entry = tk.Entry(root, width=20)
amount_entry.grid(row=1, column=1)

tk.Label(root, text="Date (DD/MM/YYYY):").grid(row=2, column=0, sticky="w")
date_entry = tk.Entry(root, width=20)
date_entry.grid(row=2, column=1)

tk.Button(root, text="Print Cheque", command=print_cheque).grid(row=3, column=1, pady=10)

root.mainloop()
