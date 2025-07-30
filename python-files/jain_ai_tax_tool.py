import tkinter as tk
from tkinter import ttk, messagebox
import datetime
import os
from fpdf import FPDF

# === Utility Function for Tax Calculation ===
def calculate_tax_old(gross_income, deductions):
    taxable_income = max(0, gross_income - deductions)
    tax = 0
    if taxable_income <= 250000:
        tax = 0
    elif taxable_income <= 500000:
        tax = (taxable_income - 250000) * 0.05
    elif taxable_income <= 1000000:
        tax = (250000 * 0.05) + (taxable_income - 500000) * 0.2
    else:
        tax = (250000 * 0.05) + (500000 * 0.2) + (taxable_income - 1000000) * 0.3

    rebate = 12500 if taxable_income <= 500000 else 0
    final_tax = max(0, tax - rebate)
    return taxable_income, tax, rebate, final_tax

def calculate_tax_new(gross_income):
    taxable_income = gross_income
    tax = 0
    slabs = [(300000, 0), (600000, 0.05), (900000, 0.1), (1200000, 0.15), (1500000, 0.2), (float('inf'), 0.3)]
    prev_limit = 0
    for limit, rate in slabs:
        if taxable_income > limit:
            tax += (limit - prev_limit) * rate
            prev_limit = limit
        else:
            tax += (taxable_income - prev_limit) * rate
            break
    rebate = 12500 if taxable_income <= 700000 else 0
    final_tax = max(0, tax - rebate)
    return taxable_income, tax, rebate, final_tax

# === PDF Export Function ===
def export_pdf(data):
    if not os.path.exists("reports"):
        os.makedirs("reports")

    filename = f"reports/{data['name'].replace(' ', '_')}_{data['date']}_{data['regime'].replace(' ', '')}.pdf"
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.cell(200, 10, txt="Jain AI Tax Tool - Tax Acknowledgement", ln=True, align='C')
    pdf.ln(10)
    for key, value in data.items():
        if key != "regime_note":
            pdf.cell(200, 8, txt=f"{key.capitalize()}: {value}", ln=True)
    pdf.ln(5)
    pdf.multi_cell(200, 8, txt="Regime Acknowledgement:")
    pdf.multi_cell(200, 8, txt=data["regime_note"])

    pdf.output(filename)
    messagebox.showinfo("Success", f"PDF exported to: {filename}")

# === GUI Start ===
root = tk.Tk()
root.title("Jain AI Tax Tool")
root.geometry("600x600")

fields = {}
labels = ["Name", "PAN", "Financial Year", "Gross Income", "Deductions (Old Regime Only)",
          "Bank Name", "Account No.", "IFSC Code", "Date (YYYY-MM-DD)"]

tk.Label(root, text="Tax Computation Form", font=('Arial', 16)).pack(pady=10)
form = tk.Frame(root)
form.pack()

for idx, label in enumerate(labels):
    tk.Label(form, text=label).grid(row=idx, column=0, sticky='w', padx=10, pady=5)
    entry = tk.Entry(form, width=40)
    entry.grid(row=idx, column=1, pady=5)
    fields[label] = entry

# Regime selection
tk.Label(form, text="Select Regime").grid(row=len(labels), column=0, padx=10, pady=5, sticky='w')
regime_var = tk.StringVar()
regime_box = ttk.Combobox(form, textvariable=regime_var, values=["Old Regime", "New Regime"])
regime_box.grid(row=len(labels), column=1, pady=5)
regime_box.set("Old Regime")

# === Compute Button Function ===
def compute_and_export():
    try:
        name = fields["Name"].get()
        pan = fields["PAN"].get()
        year = fields["Financial Year"].get()
        income = float(fields["Gross Income"].get())
        deductions = float(fields["Deductions (Old Regime Only)"].get() or 0)
        bank = fields["Bank Name"].get()
        acc = fields["Account No."].get()
        ifsc = fields["IFSC Code"].get()
        date = fields["Date (YYYY-MM-DD)"].get()
        regime = regime_var.get()

        if regime == "Old Regime":
            taxable, tax, rebate, final_tax = calculate_tax_old(income, deductions)
            regime_note = "This tax computation is done under Old Regime, where all deductions (80C, 80D etc.) are considered."
        else:
            taxable, tax, rebate, final_tax = calculate_tax_new(income)
            regime_note = "This tax computation is done under New Regime, where most deductions (80C, 80D etc.) are NOT considered."

        data = {
            "name": name,
            "pan": pan,
            "financial year": year,
            "date": date,
            "regime": regime,
            "gross income": f"₹ {income:,.2f}",
            "deductions": f"₹ {deductions:,.2f}" if regime == "Old Regime" else "N/A",
            "taxable income": f"₹ {taxable:,.2f}",
            "calculated tax": f"₹ {tax:,.2f}",
            "rebate": f"₹ {rebate:,.2f}",
            "final tax": f"₹ {final_tax:,.2f}",
            "bank name": bank,
            "account number": acc,
            "ifsc code": ifsc,
            "regime_note": regime_note
        }

        export_pdf(data)

    except Exception as e:
        messagebox.showerror("Error", f"Something went wrong:\n{e}")

# Button
submit_btn = tk.Button(root, text="Compute & Export PDF", bg="green", fg="white", command=compute_and_export)
submit_btn.pack(pady=20)

root.mainloop()
