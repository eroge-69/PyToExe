import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
import os
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from datetime import datetime

# ---------------------------
# File paths
# ---------------------------
CRM_FILE = "Asset_Management_CRM_GUI.xlsx"

# ---------------------------
# Initialize sheets if not exist
# ---------------------------
def init_crm_file():
    if not os.path.exists(CRM_FILE):
        clients_df = pd.DataFrame(columns=["Client ID", "Full Name", "Type", "PAN/Tax ID", "Contact", "Email", "Risk Profile", "Advisor Assigned"])
        portfolio_df = pd.DataFrame(columns=["Portfolio ID", "Client ID", "Investment Date", "Total AUM", "Equity%", "Debt%", "Gold%", "Alternatives%"])
        transactions_df = pd.DataFrame(columns=["Transaction ID", "Client ID", "Date", "Type", "Product Type", "Units", "Amount", "Status"])
        with pd.ExcelWriter(CRM_FILE, engine="openpyxl") as writer:
            clients_df.to_excel(writer, sheet_name="Clients", index=False)
            portfolio_df.to_excel(writer, sheet_name="Portfolio", index=False)
            transactions_df.to_excel(writer, sheet_name="Transactions", index=False)

init_crm_file()

# ---------------------------
# Load and Save data
# ---------------------------
def load_data():
    clients = pd.read_excel(CRM_FILE, sheet_name="Clients")
    portfolio = pd.read_excel(CRM_FILE, sheet_name="Portfolio")
    transactions = pd.read_excel(CRM_FILE, sheet_name="Transactions")
    return clients, portfolio, transactions

def save_data(clients, portfolio, transactions):
    with pd.ExcelWriter(CRM_FILE, engine="openpyxl", mode='w') as writer:
        clients.to_excel(writer, sheet_name="Clients", index=False)
        portfolio.to_excel(writer, sheet_name="Portfolio", index=False)
        transactions.to_excel(writer, sheet_name="Transactions", index=False)

# ---------------------------
# GUI Setup
# ---------------------------
root = tk.Tk()
root.title("Asset Management CRM")
root.geometry("1000x700")

# Style configuration
style = ttk.Style()
style.theme_use('clam')
style.configure('TNotebook.Tab', font=('Arial', 10, 'bold'))
style.configure('Treeview', font=('Arial', 9))
style.configure('Treeview.Heading', font=('Arial', 10, 'bold'))

tab_control = ttk.Notebook(root)
tab_clients = ttk.Frame(tab_control)
tab_portfolio = ttk.Frame(tab_control)
tab_transactions = ttk.Frame(tab_control)
tab_dashboard = ttk.Frame(tab_control)

tab_control.add(tab_clients, text="Clients")
tab_control.add(tab_portfolio, text="Portfolio")
tab_control.add(tab_transactions, text="Transactions")
tab_control.add(tab_dashboard, text="Dashboard")
tab_control.pack(expand=1, fill="both")

# ---------------------------
# Clients Tab
# ---------------------------
client_main_frame = tk.Frame(tab_clients)
client_main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

# Client form frame
client_form_frame = tk.LabelFrame(client_main_frame, text="Add/Edit Client", padx=10, pady=10)
client_form_frame.pack(side=tk.TOP, fill=tk.X, pady=(0, 10))

client_id_entry = tk.Entry(client_form_frame, width=30)
client_name_entry = tk.Entry(client_form_frame, width=30)
client_type_var = tk.StringVar(value="Individual")
client_pan_entry = tk.Entry(client_form_frame, width=30)
client_contact_entry = tk.Entry(client_form_frame, width=30)
client_email_entry = tk.Entry(client_form_frame, width=30)
client_risk_var = tk.StringVar(value="Moderate")
client_advisor_entry = tk.Entry(client_form_frame, width=30)

# Layout
fields = [("Client ID", client_id_entry), ("Full Name", client_name_entry), 
          ("Type", client_type_var), ("PAN/Tax ID", client_pan_entry),
          ("Contact", client_contact_entry), ("Email", client_email_entry),
          ("Risk Profile", client_risk_var), ("Advisor Assigned", client_advisor_entry)]

for i, (label_text, widget) in enumerate(fields):
    tk.Label(client_form_frame, text=label_text, width=15, anchor='w').grid(row=i, column=0, sticky='w', pady=2)
    if isinstance(widget, tk.StringVar):
        if label_text == "Type":
            ttk.Combobox(client_form_frame, textvariable=widget, values=["Individual", "Corporate", "NRI"], width=27).grid(row=i, column=1, pady=2)
        else:
            ttk.Combobox(client_form_frame, textvariable=widget, values=["Conservative", "Moderate", "Aggressive"], width=27).grid(row=i, column=1, pady=2)
    else:
        widget.grid(row=i, column=1, pady=2)

# Button frame
client_button_frame = tk.Frame(client_form_frame)
client_button_frame.grid(row=len(fields), column=0, columnspan=2, pady=10)

def add_client():
    clients, portfolio, transactions = load_data()
    cid = client_id_entry.get().strip()
    if not cid:
        messagebox.showerror("Error", "Client ID is required!")
        return
    if cid in clients["Client ID"].values:
        messagebox.showerror("Error", "Client ID already exists!")
        return
    
    new_client = {
        "Client ID": cid,
        "Full Name": client_name_entry.get().strip(),
        "Type": client_type_var.get(),
        "PAN/Tax ID": client_pan_entry.get().strip(),
        "Contact": client_contact_entry.get().strip(),
        "Email": client_email_entry.get().strip(),
        "Risk Profile": client_risk_var.get(),
        "Advisor Assigned": client_advisor_entry.get().strip()
    }
    clients = pd.concat([clients, pd.DataFrame([new_client])], ignore_index=True)
    save_data(clients, portfolio, transactions)
    messagebox.showinfo("Success", "Client added successfully!")
    refresh_clients_tree()
    refresh_dashboard()
    clear_client_form()

def clear_client_form():
    client_id_entry.delete(0, tk.END)
    client_name_entry.delete(0, tk.END)
    client_type_var.set("Individual")
    client_pan_entry.delete(0, tk.END)
    client_contact_entry.delete(0, tk.END)
    client_email_entry.delete(0, tk.END)
    client_risk_var.set("Moderate")
    client_advisor_entry.delete(0, tk.END)

tk.Button(client_button_frame, text="Add Client", command=add_client, width=12).pack(side=tk.LEFT, padx=5)
tk.Button(client_button_frame, text="Clear Form", command=clear_client_form, width=12).pack(side=tk.LEFT, padx=5)

# Clients list frame
client_list_frame = tk.LabelFrame(client_main_frame, text="Client List", padx=10, pady=10)
client_list_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

# Treeview for clients
clients_tree = ttk.Treeview(client_list_frame, columns=("Client ID", "Full Name", "Type", "PAN/Tax ID", "Contact", "Email", "Risk Profile", "Advisor Assigned"), show="headings")
for col in clients_tree["columns"]:
    clients_tree.heading(col, text=col)
    clients_tree.column(col, width=100)

clients_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

# Scrollbar for clients tree
client_scrollbar = ttk.Scrollbar(client_list_frame, orient=tk.VERTICAL, command=clients_tree.yview)
client_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
clients_tree.configure(yscrollcommand=client_scrollbar.set)

def refresh_clients_tree():
    clients_tree.delete(*clients_tree.get_children())
    clients, _, _ = load_data()
    for _, row in clients.iterrows():
        clients_tree.insert("", "end", values=tuple(row))

refresh_clients_tree()

# ---------------------------
# Portfolio Tab
# ---------------------------
portfolio_main_frame = tk.Frame(tab_portfolio)
portfolio_main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

# Portfolio form frame
portfolio_form_frame = tk.LabelFrame(portfolio_main_frame, text="Add Portfolio", padx=10, pady=10)
portfolio_form_frame.pack(side=tk.TOP, fill=tk.X, pady=(0, 10))

portfolio_id_entry = tk.Entry(portfolio_form_frame, width=30)
client_id_portfolio_entry = tk.Entry(portfolio_form_frame, width=30)
investment_date_entry = tk.Entry(portfolio_form_frame, width=30)
total_aum_entry = tk.Entry(portfolio_form_frame, width=30)
equity_entry = tk.Entry(portfolio_form_frame, width=30)
debt_entry = tk.Entry(portfolio_form_frame, width=30)
gold_entry = tk.Entry(portfolio_form_frame, width=30)
alternatives_entry = tk.Entry(portfolio_form_frame, width=30)

portfolio_fields = [
    ("Portfolio ID", portfolio_id_entry),
    ("Client ID", client_id_portfolio_entry),
    ("Investment Date (YYYY-MM-DD)", investment_date_entry),
    ("Total AUM", total_aum_entry),
    ("Equity %", equity_entry),
    ("Debt %", debt_entry),
    ("Gold %", gold_entry),
    ("Alternatives %", alternatives_entry)
]

for i, (label_text, widget) in enumerate(portfolio_fields):
    tk.Label(portfolio_form_frame, text=label_text, width=25, anchor='w').grid(row=i//2, column=(i%2)*2, sticky='w', pady=2, padx=(0, 5))
    widget.grid(row=i//2, column=(i%2)*2+1, pady=2, padx=(0, 10))

def add_portfolio():
    clients, portfolio, transactions = load_data()
    pid = portfolio_id_entry.get().strip()
    cid = client_id_portfolio_entry.get().strip()
    
    if not pid or not cid:
        messagebox.showerror("Error", "Portfolio ID and Client ID are required!")
        return
        
    if pid in portfolio["Portfolio ID"].values:
        messagebox.showerror("Error", "Portfolio ID already exists!")
        return
        
    if cid not in clients["Client ID"].values:
        messagebox.showerror("Error", "Client ID does not exist!")
        return
        
    try:
        # Validate percentages
        equity = float(equity_entry.get() or 0)
        debt = float(debt_entry.get() or 0)
        gold = float(gold_entry.get() or 0)
        alternatives = float(alternatives_entry.get() or 0)
        
        if abs(equity + debt + gold + alternatives - 100) > 0.01:
            messagebox.showerror("Error", "Asset allocation percentages must sum to 100%!")
            return
            
        new_portfolio = {
            "Portfolio ID": pid,
            "Client ID": cid,
            "Investment Date": investment_date_entry.get().strip(),
            "Total AUM": float(total_aum_entry.get() or 0),
            "Equity%": equity,
            "Debt%": debt,
            "Gold%": gold,
            "Alternatives%": alternatives
        }
        
        portfolio = pd.concat([portfolio, pd.DataFrame([new_portfolio])], ignore_index=True)
        save_data(clients, portfolio, transactions)
        messagebox.showinfo("Success", "Portfolio added successfully!")
        refresh_portfolio_tree()
        refresh_dashboard()
        clear_portfolio_form()
        
    except ValueError:
        messagebox.showerror("Error", "Please enter valid numeric values!")

def clear_portfolio_form():
    portfolio_id_entry.delete(0, tk.END)
    client_id_portfolio_entry.delete(0, tk.END)
    investment_date_entry.delete(0, tk.END)
    total_aum_entry.delete(0, tk.END)
    equity_entry.delete(0, tk.END)
    debt_entry.delete(0, tk.END)
    gold_entry.delete(0, tk.END)
    alternatives_entry.delete(0, tk.END)

portfolio_button_frame = tk.Frame(portfolio_form_frame)
portfolio_button_frame.grid(row=4, column=0, columnspan=4, pady=10)

tk.Button(portfolio_button_frame, text="Add Portfolio", command=add_portfolio, width=15).pack(side=tk.LEFT, padx=5)
tk.Button(portfolio_button_frame, text="Clear Form", command=clear_portfolio_form, width=15).pack(side=tk.LEFT, padx=5)

# Portfolio list frame
portfolio_list_frame = tk.LabelFrame(portfolio_main_frame, text="Portfolio List", padx=10, pady=10)
portfolio_list_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

# Treeview for portfolio
portfolio_tree = ttk.Treeview(portfolio_list_frame, columns=("Portfolio ID", "Client ID", "Investment Date", "Total AUM", "Equity%", "Debt%", "Gold%", "Alternatives%"), show="headings")
for col in portfolio_tree["columns"]:
    portfolio_tree.heading(col, text=col)
    portfolio_tree.column(col, width=100)

portfolio_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

# Scrollbar for portfolio tree
portfolio_scrollbar = ttk.Scrollbar(portfolio_list_frame, orient=tk.VERTICAL, command=portfolio_tree.yview)
portfolio_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
portfolio_tree.configure(yscrollcommand=portfolio_scrollbar.set)

def refresh_portfolio_tree():
    portfolio_tree.delete(*portfolio_tree.get_children())
    _, portfolio, _ = load_data()
    for _, row in portfolio.iterrows():
        portfolio_tree.insert("", "end", values=tuple(row))

refresh_portfolio_tree()

# ---------------------------
# Transactions Tab
# ---------------------------
transactions_main_frame = tk.Frame(tab_transactions)
transactions_main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

# Transactions form frame
transaction_form_frame = tk.LabelFrame(transactions_main_frame, text="Add Transaction", padx=10, pady=10)
transaction_form_frame.pack(side=tk.TOP, fill=tk.X, pady=(0, 10))

transaction_id_entry = tk.Entry(transaction_form_frame, width=30)
client_id_transaction_entry = tk.Entry(transaction_form_frame, width=30)
transaction_date_entry = tk.Entry(transaction_form_frame, width=30)
transaction_type_var = tk.StringVar(value="Buy")
product_type_entry = tk.Entry(transaction_form_frame, width=30)
units_entry = tk.Entry(transaction_form_frame, width=30)
amount_entry = tk.Entry(transaction_form_frame, width=30)
transaction_status_var = tk.StringVar(value="Completed")

transaction_fields = [
    ("Transaction ID", transaction_id_entry),
    ("Client ID", client_id_transaction_entry),
    ("Date (YYYY-MM-DD)", transaction_date_entry),
    ("Type", transaction_type_var),
    ("Product Type", product_type_entry),
    ("Units", units_entry),
    ("Amount", amount_entry),
    ("Status", transaction_status_var)
]

for i, (label_text, widget) in enumerate(transaction_fields):
    tk.Label(transaction_form_frame, text=label_text, width=15, anchor='w').grid(row=i, column=0, sticky='w', pady=2)
    if isinstance(widget, tk.StringVar):
        if label_text == "Type":
            ttk.Combobox(transaction_form_frame, textvariable=widget, values=["Buy", "Sell", "Dividend", "Interest"], width=27).grid(row=i, column=1, pady=2)
        else:
            ttk.Combobox(transaction_form_frame, textvariable=widget, values=["Completed", "Pending", "Cancelled"], width=27).grid(row=i, column=1, pady=2)
    else:
        widget.grid(row=i, column=1, pady=2)

def add_transaction():
    clients, portfolio, transactions = load_data()
    tid = transaction_id_entry.get().strip()
    cid = client_id_transaction_entry.get().strip()
    
    if not tid or not cid:
        messagebox.showerror("Error", "Transaction ID and Client ID are required!")
        return
        
    if tid in transactions["Transaction ID"].values:
        messagebox.showerror("Error", "Transaction ID already exists!")
        return
        
    if cid not in clients["Client ID"].values:
        messagebox.showerror("Error", "Client ID does not exist!")
        return
        
    try:
        new_transaction = {
            "Transaction ID": tid,
            "Client ID": cid,
            "Date": transaction_date_entry.get().strip(),
            "Type": transaction_type_var.get(),
            "Product Type": product_type_entry.get().strip(),
            "Units": float(units_entry.get() or 0),
            "Amount": float(amount_entry.get() or 0),
            "Status": transaction_status_var.get()
        }
        
        transactions = pd.concat([transactions, pd.DataFrame([new_transaction])], ignore_index=True)
        save_data(clients, portfolio, transactions)
        messagebox.showinfo("Success", "Transaction added successfully!")
        refresh_transactions_tree()
        refresh_dashboard()
        clear_transaction_form()
        
    except ValueError:
        messagebox.showerror("Error", "Please enter valid numeric values for Units and Amount!")

def clear_transaction_form():
    transaction_id_entry.delete(0, tk.END)
    client_id_transaction_entry.delete(0, tk.END)
    transaction_date_entry.delete(0, tk.END)
    transaction_type_var.set("Buy")
    product_type_entry.delete(0, tk.END)
    units_entry.delete(0, tk.END)
    amount_entry.delete(0, tk.END)
    transaction_status_var.set("Completed")

transaction_button_frame = tk.Frame(transaction_form_frame)
transaction_button_frame.grid(row=8, column=0, columnspan=2, pady=10)

tk.Button(transaction_button_frame, text="Add Transaction", command=add_transaction, width=15).pack(side=tk.LEFT, padx=5)
tk.Button(transaction_button_frame, text="Clear Form", command=clear_transaction_form, width=15).pack(side=tk.LEFT, padx=5)

# Transactions list frame
transaction_list_frame = tk.LabelFrame(transactions_main_frame, text="Transaction List", padx=10, pady=10)
transaction_list_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

# Treeview for transactions
transactions_tree = ttk.Treeview(transaction_list_frame, columns=("Transaction ID", "Client ID", "Date", "Type", "Product Type", "Units", "Amount", "Status"), show="headings")
for col in transactions_tree["columns"]:
    transactions_tree.heading(col, text=col)
    transactions_tree.column(col, width=100)

transactions_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

# Scrollbar for transactions tree
transaction_scrollbar = ttk.Scrollbar(transaction_list_frame, orient=tk.VERTICAL, command=transactions_tree.yview)
transaction_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
transactions_tree.configure(yscrollcommand=transaction_scrollbar.set)

def refresh_transactions_tree():
    transactions_tree.delete(*transactions_tree.get_children())
    _, _, transactions = load_data()
    for _, row in transactions.iterrows():
        transactions_tree.insert("", "end", values=tuple(row))

refresh_transactions_tree()

# ---------------------------
# Dashboard Tab
# ---------------------------
dashboard_frame = tk.Frame(tab_dashboard, padx=20, pady=20)
dashboard_frame.pack(fill=tk.BOTH, expand=True)

# Stats frame
stats_frame = tk.LabelFrame(dashboard_frame, text="Key Metrics", padx=10, pady=10)
stats_frame.pack(side=tk.TOP, fill=tk.X)

total_clients_var = tk.StringVar(value="0")
total_aum_var = tk.StringVar(value="₹0.00")
avg_aum_var = tk.StringVar(value="₹0.00")
last_date_var = tk.StringVar(value="N/A")

tk.Label(stats_frame, text="Total Clients:", font=('Arial', 10, 'bold')).grid(row=0, column=0, sticky="w", pady=5)
tk.Label(stats_frame, textvariable=total_clients_var, font=('Arial', 10)).grid(row=0, column=1, sticky="w", pady=5)

tk.Label(stats_frame, text="Total AUM:", font=('Arial', 10, 'bold')).grid(row=0, column=2, sticky="w", pady=5, padx=(20, 0))
tk.Label(stats_frame, textvariable=total_aum_var, font=('Arial', 10)).grid(row=0, column=3, sticky="w", pady=5)

tk.Label(stats_frame, text="Average AUM per Client:", font=('Arial', 10, 'bold')).grid(row=1, column=0, sticky="w", pady=5)
tk.Label(stats_frame, textvariable=avg_aum_var, font=('Arial', 10)).grid(row=1, column=1, sticky="w", pady=5)

tk.Label(stats_frame, text="Last Investment Date:", font=('Arial', 10, 'bold')).grid(row=1, column=2, sticky="w", pady=5, padx=(20, 0))
tk.Label(stats_frame, textvariable=last_date_var, font=('Arial', 10)).grid(row=1, column=3, sticky="w", pady=5)

# Charts frame
charts_frame = tk.LabelFrame(dashboard_frame, text="Analytics", padx=10, pady=10)
charts_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, pady=(10, 0))

# Create figure for charts
fig, axes = plt.subplots(1, 2, figsize=(10, 4))
fig.subplots_adjust(wspace=0.4)
canvas = FigureCanvasTkAgg(fig, master=charts_frame)
canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

def refresh_dashboard():
    clients, portfolio, _ = load_data()
    
    # Update stats
    total_clients_var.set(str(len(clients)))
    total_aum = portfolio["Total AUM"].sum() if not portfolio.empty else 0
    total_aum_var.set(f"₹{total_aum:,.2f}")
    avg_aum = portfolio["Total AUM"].mean() if not portfolio.empty else 0
    avg_aum_var.set(f"₹{avg_aum:,.2f}")
    last_date = portfolio["Investment Date"].max() if not portfolio.empty else "N/A"
    last_date_var.set(str(last_date))
    
    # Update charts
    for ax in axes:
        ax.clear()
        
    if not portfolio.empty:
        # Asset allocation pie chart
        asset_totals = portfolio[["Equity%", "Debt%", "Gold%", "Alternatives%"]].sum()
        axes[0].pie(asset_totals, labels=asset_totals.index, autopct="%1.1f%%", startangle=90)
        axes[0].set_title("Overall Asset Allocation")
        
        # Client AUM bar chart (top 10 clients)
        client_aum = portfolio.groupby("Client ID")["Total AUM"].sum().nlargest(10)
        if not client_aum.empty:
            axes[1].bar(range(len(client_aum)), client_aum.values)
            axes[1].set_xticks(range(len(client_aum)))
            axes[1].set_xticklabels(client_aum.index, rotation=45, ha='right')
            axes[1].set_ylabel("AUM (₹)")
            axes[1].set_title("Top 10 Clients by AUM")
        else:
            axes[1].text(0.5, 0.5, "No portfolio data available", ha='center', va='center', transform=axes[1].transAxes)
    else:
        axes[0].text(0.5, 0.5, "No portfolio data available", ha='center', va='center