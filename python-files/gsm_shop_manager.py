#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GSM Shop Management - Tkinter App
Features:
- Sales (Vente) & Recharges logging to CSV
- Invoice payments logging to CSV
- Stock management (add/update products)
- Dashboard with period filter (Day/Week/Month)
- Bar chart (sales by product) + Pie chart (by type)
- Export summary to PDF
"""
import tkinter as tk
from tkinter import ttk, messagebox
import csv
from datetime import datetime, timedelta
from fpdf import FPDF
import os
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# CSV Files
VENTES_FILE = "ventes.csv"
STOCK_FILE = "stock.csv"
FACTURES_FILE = "factures.csv"

# Ensure CSV files exist with headers
def init_files():
    if not os.path.exists(VENTES_FILE):
        with open(VENTES_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Date", "Type", "Produit", "Prix", "Quantité"])
    if not os.path.exists(STOCK_FILE):
        with open(STOCK_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Produit", "Quantité"])
    if not os.path.exists(FACTURES_FILE):
        with open(FACTURES_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Date", "Facture", "Montant"])

init_files()

# Helpers
def lire_stock():
    stock = {}
    with open(STOCK_FILE, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                stock[row["Produit"]] = int(row["Quantité"])
            except Exception:
                # skip malformed lines
                continue
    return stock

def sauvegarder_stock(stock):
    with open(STOCK_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Produit", "Quantité"])
        for produit, qte in stock.items():
            writer.writerow([produit, qte])

def ajouter_vente(produit, prix, quantite):
    if not produit or not prix or not quantite:
        messagebox.showerror("Erreur", "Tous les champs sont obligatoires")
        return
    try:
        prix = float(prix)
        quantite = int(quantite)
    except ValueError:
        messagebox.showerror("Erreur", "Prix et quantité doivent être numériques")
        return

    date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Update stock
    stock = lire_stock()
    if produit in stock:
        if stock[produit] < quantite:
            messagebox.showerror("Erreur", f"Stock insuffisant pour {produit}")
            return
        stock[produit] -= quantite
        sauvegarder_stock(stock)
    else:
        messagebox.showerror("Erreur", "Produit introuvable dans le stock")
        return

    with open(VENTES_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([date, "Vente", produit, prix, quantite])

    messagebox.showinfo("Succès", f"{quantite} {produit} ajouté à la vente")
    update_dashboard()

def ajouter_facture(facture, montant):
    if not montant:
        messagebox.showerror("Erreur", "Montant obligatoire")
        return
    try:
        montant = float(montant)
    except ValueError:
        messagebox.showerror("Erreur", "Montant doit être numérique")
        return

    date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(FACTURES_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([date, facture, montant])
    messagebox.showinfo("Succès", f"Facture {facture} ajoutée")
    update_dashboard()

def ajouter_recharge(type_recharge, montant):
    if not montant:
        messagebox.showerror("Erreur", "Montant obligatoire")
        return
    try:
        montant = float(montant)
    except ValueError:
        messagebox.showerror("Erreur", "Montant doit être numérique")
        return

    date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(VENTES_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([date, "Recharge", type_recharge, montant, 1])
    messagebox.showinfo("Succès", f"Recharge {type_recharge} ajoutée")
    update_dashboard()

# GUI
root = tk.Tk()
root.title("GSM Shop Management")
root.geometry("1350x820")

# Layout Frames
menu_frame = tk.Frame(root, width=220, bg="#2c3e50")
menu_frame.pack(side="left", fill="y")
content_frame = tk.Frame(root, bg="#ecf0f1")
content_frame.pack(side="right", fill="both", expand=True)

# Dashboard
dashboard_frame = tk.Frame(content_frame, bg="#ecf0f1")
dashboard_frame.pack(fill="both", expand=True, padx=10, pady=10)

label_title = tk.Label(dashboard_frame, text="Tableau de bord", font=("Arial", 20, "bold"), bg="#ecf0f1")
label_title.pack(pady=(0,10))

# Period selector
periode_var = tk.StringVar(value="Jour")
periode_row = tk.Frame(dashboard_frame, bg="#ecf0f1")
periode_row.pack(pady=5)
tk.Label(periode_row, text="Période :", bg="#ecf0f1").pack(side="left", padx=(0,8))
periode_menu = ttk.Combobox(periode_row, textvariable=periode_var, state="readonly", width=12)
periode_menu["values"] = ["Jour", "Semaine", "Mois"]
periode_menu.pack(side="left")

# Summary labels
vente_text = tk.StringVar()
label_vente = tk.Label(dashboard_frame, textvariable=vente_text, bg="#ecf0f1", font=("Arial", 12), justify="left", anchor="w")
label_vente.pack(fill="x", pady=5)

stock_text = tk.StringVar()
label_stock = tk.Label(dashboard_frame, textvariable=stock_text, bg="#ecf0f1", font=("Arial", 12), justify="left", anchor="w")
label_stock.pack(fill="x", pady=5)

resume_text = tk.StringVar()
label_resume = tk.Label(dashboard_frame, textvariable=resume_text, bg="#ecf0f1", font=("Arial", 12), justify="left", anchor="w")
label_resume.pack(fill="x", pady=5)

# Graph area
graph_frame = tk.Frame(dashboard_frame, bg="#ecf0f1")
graph_frame.pack(fill="both", expand=True, pady=10)

# Windows
def open_new_sale():
    sale_win = tk.Toplevel(root)
    sale_win.title("Nouvelle Vente")
    sale_win.geometry("350x180")
    tk.Label(sale_win, text="Produit:").grid(row=0, column=0, sticky="e", padx=5, pady=5)

    # Combobox with stock
    stock = lire_stock()
    produit_var = tk.StringVar()
    produit_menu = ttk.Combobox(sale_win, textvariable=produit_var, state="readonly", width=22)
    produit_menu["values"] = list(stock.keys())
    produit_menu.grid(row=0, column=1, padx=5, pady=5)

    tk.Label(sale_win, text="Prix:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
    prix_entry = tk.Entry(sale_win, width=25)
    prix_entry.grid(row=1, column=1, padx=5, pady=5)

    tk.Label(sale_win, text="Quantité:").grid(row=2, column=0, sticky="e", padx=5, pady=5)
    quantite_entry = tk.Entry(sale_win, width=25)
    quantite_entry.grid(row=2, column=1, padx=5, pady=5)

    tk.Button(sale_win, text="Ajouter",
              command=lambda: [ajouter_vente(produit_var.get(), prix_entry.get(), quantite_entry.get()), sale_win.destroy()]
              ).grid(row=3, column=0, columnspan=2, pady=10)

def open_new_invoice():
    fact_win = tk.Toplevel(root)
    fact_win.title("Paiement Facture")
    fact_win.geometry("350x160")
    tk.Label(fact_win, text="Facture:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
    tk.Label(fact_win, text="Montant:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
    facture_var = tk.StringVar(value="TopNet")
    facture_menu = ttk.Combobox(fact_win, textvariable=facture_var, state="readonly", width=22)
    facture_menu["values"] = ["TopNet", "Telecom", "NETY", "BEE"]
    facture_menu.grid(row=0, column=1, padx=5, pady=5)
    montant_entry = tk.Entry(fact_win, width=25)
    montant_entry.grid(row=1, column=1, padx=5, pady=5)
    tk.Button(fact_win, text="Ajouter",
              command=lambda: [ajouter_facture(facture_var.get(), montant_entry.get()), fact_win.destroy()]
              ).grid(row=2, column=0, columnspan=2, pady=10)

def open_new_recharge():
    rec_win = tk.Toplevel(root)
    rec_win.title("Nouvelle Recharge")
    rec_win.geometry("350x160")
    tk.Label(rec_win, text="Type de recharge:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
    tk.Label(rec_win, text="Montant:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
    recharge_var = tk.StringVar(value="Ooredoo")
    recharge_menu = ttk.Combobox(rec_win, textvariable=recharge_var, state="readonly", width=22)
    recharge_menu["values"] = ["Ooredoo", "Telecom", "Orange", "Internet Telecom"]
    recharge_menu.grid(row=0, column=1, padx=5, pady=5)
    montant_entry = tk.Entry(rec_win, width=25)
    montant_entry.grid(row=1, column=1, padx=5, pady=5)
    tk.Button(rec_win, text="Ajouter",
              command=lambda: [ajouter_recharge(recharge_var.get(), montant_entry.get()), rec_win.destroy()]
              ).grid(row=2, column=0, columnspan=2, pady=10)

def open_stock_manager():
    stock_win = tk.Toplevel(root)
    stock_win.title("Gestion du Stock")
    stock_win.geometry("450x480")

    # Table current stock
    tree = ttk.Treeview(stock_win, columns=("Produit", "Quantité"), show="headings", height=12)
    tree.heading("Produit", text="Produit")
    tree.heading("Quantité", text="Quantité")
    tree.column("Produit", width=260)
    tree.column("Quantité", width=100, anchor="center")
    tree.pack(fill="both", expand=True, pady=(10,5), padx=10)

    def refresh_tree():
        for i in tree.get_children():
            tree.delete(i)
        for produit, qte in lire_stock().items():
            tree.insert("", "end", values=(produit, qte))

    refresh_tree()

    form = tk.Frame(stock_win)
    form.pack(fill="x", padx=10, pady=5)
    tk.Label(form, text="Produit:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
    produit_entry = tk.Entry(form, width=28)
    produit_entry.grid(row=0, column=1, padx=5, pady=5)

    tk.Label(form, text="Quantité (+/-):").grid(row=1, column=0, sticky="e", padx=5, pady=5)
    quantite_entry = tk.Entry(form, width=28)
    quantite_entry.grid(row=1, column=1, padx=5, pady=5)

    def ajouter_modifier_stock():
        produit = produit_entry.get().strip()
        qtext = quantite_entry.get().strip()
        if not produit or not qtext:
            messagebox.showerror("Erreur", "Nom du produit et quantité requis")
            return
        try:
            qte = int(qtext)
        except ValueError:
            messagebox.showerror("Erreur", "La quantité doit être un entier (utilisez un nombre négatif pour retirer)")
            return
        stock = lire_stock()
        stock[produit] = stock.get(produit, 0) + qte
        if stock[produit] < 0:
            stock[produit] = 0
        sauvegarder_stock(stock)
        messagebox.showinfo("Succès", f"Stock de '{produit}' mis à {stock[produit]}")
        refresh_tree()
        update_dashboard()

    tk.Button(stock_win, text="Ajouter / Modifier", command=ajouter_modifier_stock).pack(pady=8)

# Dashboard calculation + charts
def update_dashboard(*args):
    periode = periode_var.get()
    total_ventes = 0.0
    nb_articles = 0
    ventes_detail = []
    ventes_par_produit = {}
    ventes_par_type = {}

    today = datetime.now().date()

    def include_row(row_date):
        if periode == "Jour":
            return row_date == today
        elif periode == "Semaine":
            return row_date >= today - timedelta(days=7)
        elif periode == "Mois":
            return row_date.year == today.year and row_date.month == today.month
        return False

    # Read sales
    if os.path.exists(VENTES_FILE):
        with open(VENTES_FILE, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    row_date = datetime.strptime(row["Date"], "%Y-%m-%d %H:%M:%S").date()
                except Exception:
                    continue
                if include_row(row_date):
                    try:
                        qte = int(row["Quantité"])
                        prix = float(row["Prix"])
                    except Exception:
                        continue
                    montant = prix * qte
                    nb_articles += qte
                    total_ventes += montant
                    ventes_detail.append(f"{row['Type']} - {row['Produit']} : {prix} x{qte} = {montant:.2f}")
                    ventes_par_produit[row["Produit"]] = ventes_par_produit.get(row["Produit"], 0.0) + montant
                    ventes_par_type[row["Type"]] = ventes_par_type.get(row["Type"], 0.0) + montant

    vente_text.set(f"Ventes ({periode}) : {nb_articles} articles, Total: {total_ventes:.2f} DT\n" + ("\n".join(ventes_detail) if ventes_detail else "Aucune vente pour cette période."))

    # Stock snapshot
    stock = lire_stock()
    if stock:
        stock_lines = "\n".join([f"{p}: {q}" for p, q in stock.items()])
    else:
        stock_lines = "Aucun produit en stock."
    stock_text.set("Stock actuel:\n" + stock_lines)

    # Invoices total (all-time)
    factures_total = 0.0
    if os.path.exists(FACTURES_FILE):
        with open(FACTURES_FILE, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    factures_total += float(row["Montant"])
                except Exception:
                    continue
    resume_text.set(f"Total Factures payées (tout temps): {factures_total:.2f} DT")

    # Clear previous charts
    for widget in graph_frame.winfo_children():
        widget.destroy()

    if ventes_par_produit:
        # Build figure with 2 subplots: bar (products) + pie (types)
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4))

        produits = list(ventes_par_produit.keys())
        montants = list(ventes_par_produit.values())
        x = list(range(len(produits)))
        ax1.bar(x, montants)
        ax1.set_title("Ventes par produit")
        ax1.set_ylabel("Montant (DT)")
        ax1.set_xticks(x)
        ax1.set_xticklabels(produits, rotation=45, ha="right")

        types = list(ventes_par_type.keys())
        valeurs = list(ventes_par_type.values())
        if sum(valeurs) > 0:
            ax2.pie(valeurs, labels=types, autopct="%1.1f%%", startangle=90)
            ax2.set_title("Répartition par type")

        canvas = FigureCanvasTkAgg(fig, master=graph_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
    else:
        tk.Label(graph_frame, text="Aucune donnée à afficher pour la période sélectionnée.", bg="#ecf0f1").pack(pady=10)

# Bind period change
periode_menu.bind("<<ComboboxSelected>>", update_dashboard)

# Initial dashboard
update_dashboard()

# Menu buttons
menus = [
    ("Tableau de bord", lambda: update_dashboard()),
    ("Nouvelle vente", open_new_sale),
    ("Paiement", open_new_invoice),
    ("Recharge", open_new_recharge),
    ("Stock", open_stock_manager),
]

for name, cmd in menus:
    btn = tk.Button(menu_frame, text=name, width=22, command=cmd, bg="#34495e", fg="white", relief="flat")
    btn.pack(pady=6, padx=10)

# Export PDF
def export_pdf():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(0, 10, "Résumé", ln=True)
    pdf.multi_cell(0, 10, vente_text.get())
    pdf.multi_cell(0, 10, stock_text.get())
    pdf.multi_cell(0, 10, resume_text.get())
    pdf_file = f"rapport_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    try:
        pdf.output(pdf_file)
        messagebox.showinfo("PDF", f"Exporté avec succès: {pdf_file}")
    except Exception as e:
        messagebox.showerror("Erreur", f"Échec d'export PDF: {e}")

tk.Button(dashboard_frame, text="Exporter PDF", command=export_pdf, bg="#27ae60", fg="white").pack(pady=10)

# Run
if __name__ == "__main__":
    root.mainloop()
