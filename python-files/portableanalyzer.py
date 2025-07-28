# -*- coding: utf-8 -*-
"""
Created on Mon Jul 28 01:49:09 2025

@author: gagek
"""

import csv
import datetime
import os
from tkinter import *
from tkinter import ttk, messagebox

zip_offer_map = {
    "32114": 0.65, "32117": 0.66, "32119": 0.67, "32720": 0.68, "32724": 0.68,
    "32174": 0.66, "32129": 0.65, "32127": 0.65, "32141": 0.64, "32132": 0.65,
    "32210": 0.75, "32218": 0.72, "32207": 0.70, "32244": 0.71,
    "32208": 0.70, "32209": 0.68, "32211": 0.69, "32216": 0.70,
    "32068": 0.70, "32065": 0.71, "32084": 0.73, "32092": 0.74, "32086": 0.72,
    "32164": 0.70, "32137": 0.68,
}

def estimate_wholesale(purchase_price, rehab_cost, arv, zip_code, desired_assignment_fee=10000):
    try:
        purchase_price = float(purchase_price)
        rehab_cost = float(rehab_cost)
        arv = float(arv)

        if arv < 30000 or purchase_price < 10000:
            raise ValueError("ARV or Purchase Price is unrealistically low.")
        if rehab_cost > arv:
            raise ValueError("Rehab exceeds ARV. Check numbers.")

        base_pct = zip_offer_map.get(zip_code, 0.68)

        if arv < 100000:
            base_pct += 0.02
        elif arv > 300000:
            base_pct -= 0.03

        rehab_ratio = rehab_cost / arv
        if rehab_ratio > 0.35:
            base_pct -= 0.02
        elif rehab_ratio < 0.10:
            base_pct += 0.01

        buyer_offer = arv * base_pct - rehab_cost
        assignment_fee = buyer_offer - purchase_price
        is_deal = assignment_fee >= desired_assignment_fee

        if rehab_ratio > 0.35:
            deal_type = "Heavy Rehab"
        elif rehab_ratio < 0.15:
            deal_type = "Rental / Light Flip"
        else:
            deal_type = "Standard Flip"

        return round(buyer_offer, 2), round(assignment_fee, 2), is_deal, round(base_pct * 100, 1), deal_type
    except Exception as e:
        raise e

def suggest_adjustments(purchase_price, rehab_cost, arv, zip_code, desired_assignment_fee):
    """
    Try to adjust Purchase Price, Rehab Cost, or Assignment Fee to make deal work,
    within realistic and safe boundaries.
    """
    suggestions = []
    purchase_price = float(purchase_price)
    rehab_cost = float(rehab_cost)
    arv = float(arv)
    desired_assignment_fee = float(desired_assignment_fee)

    # Try lowering purchase price by up to 10%
    for discount in [0.95, 0.90, 0.85]:
        new_pp = purchase_price * discount
        buyer_offer, assignment_fee, is_deal, pct, deal_type = estimate_wholesale(new_pp, rehab_cost, arv, zip_code, desired_assignment_fee)
        if is_deal:
            suggestions.append(f"Lower Purchase Price to ${new_pp:.0f} (discount {int((1-discount)*100)}%)")

    # Try lowering rehab cost by up to 20%
    for rehab_discount in [0.90, 0.85, 0.80]:
        new_rc = rehab_cost * rehab_discount
        buyer_offer, assignment_fee, is_deal, pct, deal_type = estimate_wholesale(purchase_price, new_rc, arv, zip_code, desired_assignment_fee)
        if is_deal:
            suggestions.append(f"Lower Rehab Cost to ${new_rc:.0f} (discount {int((1-rehab_discount)*100)}%)")

    # Try lowering desired assignment fee (profit) by increments of $1000 down to 0
    for fee_cut in range(int(desired_assignment_fee), -1, -1000):
        buyer_offer, assignment_fee, is_deal, pct, deal_type = estimate_wholesale(purchase_price, rehab_cost, arv, zip_code, fee_cut)
        if is_deal:
            suggestions.append(f"Accept lower Assignment Fee of ${fee_cut}")

    # Remove duplicates and limit to top 5 suggestions
    unique_suggestions = list(dict.fromkeys(suggestions))
    return unique_suggestions[:5]

def save_deal(data):
    filename = "wholesale_logs.csv"
    file_exists = os.path.isfile(filename)
    with open(filename, 'a', newline='') as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow([
                "Date", "Address", "ZIP", "Purchase Price", "Rehab Cost", "ARV",
                "Buyer Offer %", "Buyer Offer", "Assignment Fee", "Deal?", "Deal Type"
            ])
        writer.writerow(data)

def run_gui():
    root = Tk()
    root.title("🏠 Portable Real Estate Wholesale Analyzer")
    root.geometry("560x700")

    Label(root, text="Fill out the fields below:", font=("Segoe UI", 12)).pack(pady=5)

    fields = [
        ("Address", 50),
        ("ZIP Code", 20),
        ("Purchase Price", 20),
        ("Rehab Cost", 20),
        ("After Repair Value (ARV)", 20),
        ("Desired Assignment Fee", 20)
    ]

    entries = {}
    for label, width in fields:
        Label(root, text=label).pack()
        e = Entry(root, width=width)
        e.pack(pady=5)
        entries[label] = e

    entries["Desired Assignment Fee"].insert(0, "10000")

    result_label = Label(root, text="", font=("Segoe UI", 10), justify=LEFT)
    result_label.pack(pady=10)

    suggestions_label = Label(root, text="", font=("Segoe UI", 10), fg="blue", justify=LEFT)
    suggestions_label.pack(pady=10)

    def analyze():
        try:
            addr = entries["Address"].get()
            zipc = entries["ZIP Code"].get().strip()
            pp = entries["Purchase Price"].get()
            rc = entries["Rehab Cost"].get()
            arv = entries["After Repair Value (ARV)"].get()
            daf = entries["Desired Assignment Fee"].get()

            if not all([addr, zipc, pp, rc, arv, daf]):
                messagebox.showwarning("Missing Info", "Please fill out all fields.")
                return

            buyer_offer, assignment_fee, deal, pct, deal_type = estimate_wholesale(pp, rc, arv, zipc, float(daf))
            status = "✅ DEAL" if deal else "❌ NO DEAL"

            result_text = (
                f"ZIP Buyer Offer %: {pct}%\n"
                f"Buyer Offer: ${buyer_offer}\n"
                f"Assignment Fee: ${assignment_fee}\n"
                f"Type: {deal_type}\n"
                f"Status: {status}"
            )
            result_label.config(text=result_text)

            suggestions_label.config(text="")
            if not deal:
                suggestions = suggest_adjustments(pp, rc, arv, zipc, daf)
                if suggestions:
                    suggestions_text = "💡 Suggestions to make the deal work:\n" + "\n".join(f"- {s}" for s in suggestions)
                    suggestions_label.config(text=suggestions_text)
                else:
                    suggestions_label.config(text="No easy suggestions found to make this deal profitable.")

            save_data = [
                datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
                addr, zipc, pp, rc, arv, pct, buyer_offer, assignment_fee, status, deal_type
            ]
            save_deal(save_data)
            messagebox.showinfo("Saved", "Deal saved to wholesale_logs.csv")
        except Exception as e:
            messagebox.showerror("Error", f"Calculation failed:\n{e}")

    ttk.Button(root, text="📊 Analyze Wholesale Deal", command=analyze).pack(pady=15)
    root.mainloop()

if __name__ == "__main__":
    run_gui()
