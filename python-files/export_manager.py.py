Python 3.13.3 (tags/v3.13.3:6280bb5, Apr  8 2025, 14:47:33) [MSC v.1943 64 bit (AMD64)] on win32
Enter "help" below or click "Help" above for more information.
import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd

# DataFrames for storing data
buyers = pd.DataFrame(columns=['ID', 'Name', 'Address', 'Contact'])
suppliers = pd.DataFrame(columns=['ID', 'Name', 'Address', 'Contact'])
contracts = pd.DataFrame(columns=['Contract No', 'Buyer ID', 'Product', 'Amount'])
payments = pd.DataFrame(columns=['Payment ID', 'Supplier ID', 'Amount', 'Date'])
deliveries = pd.DataFrame(columns=['Delivery ID', 'Contract No', 'Date', 'Status'])

# Save data to Excel (for simplicity)
def save_to_excel():
    buyers.to_excel('buyers.xlsx', index=False)
    suppliers.to_excel('suppliers.xlsx', index=False)
    contracts.to_excel('contracts.xlsx', index=False)
    payments.to_excel('payments.xlsx', index=False)
    deliveries.to_excel('deliveries.xlsx', index=False)
    messagebox.showinfo("Save", "Data saved to Excel files.")

# Main App
class ExportManagerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Export Manager")
        self.geometry("600x400")

        tab_control = ttk.Notebook(self)
        
        self.buyer_tab = ttk.Frame(tab_control)
        self.supplier_tab = ttk.Frame(tab_control)
        self.contract_tab = ttk.Frame(tab_control)
        self.payment_tab = ttk.Frame(tab_control)
        self.delivery_tab = ttk.Frame(tab_control)
        
        tab_control.add(self.buyer_tab, text='Buyers')
        tab_control.add(self.supplier_tab, text='Suppliers')
        tab_control.add(self.contract_tab, text='Contracts')
        tab_control.add(self.payment_tab, text='Payments')
        tab_control.add(self.delivery_tab, text='Deliveries')
        
        tab_control.pack(expand=1, fill='both')
        
        self.setup_buyer_tab()
        self.setup_supplier_tab()
        self.setup_contract_tab()
        self.setup_payment_tab()
        self.setup_delivery_tab()
        
        save_button = tk.Button(self, text="Save All", command=save_to_excel)
        save_button.pack(side=tk.BOTTOM)

    def setup_buyer_tab(self):
        tk.Label(self.buyer_tab, text="Buyer Name:").pack()
        name = tk.Entry(self.buyer_tab)
        name.pack()
        tk.Label(self.buyer_tab, text="Address:").pack()
        address = tk.Entry(self.buyer_tab)
        address.pack()
        tk.Label(self.buyer_tab, text="Contact:").pack()
        contact = tk.Entry(self.buyer_tab)
        contact.pack()
        tk.Button(self.buyer_tab, text="Add Buyer", command=lambda: buyers.loc[len(buyers)] = [len(buyers)+1, name.get(), address.get(), contact.get()]).pack()

    def setup_supplier_tab(self):
        tk.Label(self.supplier_tab, text="Supplier Name:").pack()
        name = tk.Entry(self.supplier_tab)
        name.pack()
        tk.Label(self.supplier_tab, text="Address:").pack()
        address = tk.Entry(self.supplier_tab)
        address.pack()
        tk.Label(self.supplier_tab, text="Contact:").pack()
        contact = tk.Entry(self.supplier_tab)
        contact.pack()
        tk.Button(self.supplier_tab, text="Add Supplier", command=lambda: suppliers.loc[len(suppliers)] = [len(suppliers)+1, name.get(), address.get(), contact.get()]).pack()

    def setup_contract_tab(self):
        tk.Label(self.contract_tab, text="Contract No:").pack()
        cno = tk.Entry(self.contract_tab)
        cno.pack()
...         tk.Label(self.contract_tab, text="Buyer ID:").pack()
...         bid = tk.Entry(self.contract_tab)
...         bid.pack()
...         tk.Label(self.contract_tab, text="Product:").pack()
...         product = tk.Entry(self.contract_tab)
...         product.pack()
...         tk.Label(self.contract_tab, text="Amount:").pack()
...         amount = tk.Entry(self.contract_tab)
...         amount.pack()
...         tk.Button(self.contract_tab, text="Add Contract", command=lambda: contracts.loc[len(contracts)] = [cno.get(), bid.get(), product.get(), amount.get()]).pack()
... 
...     def setup_payment_tab(self):
...         tk.Label(self.payment_tab, text="Payment ID:").pack()
...         pid = tk.Entry(self.payment_tab)
...         pid.pack()
...         tk.Label(self.payment_tab, text="Supplier ID:").pack()
...         sid = tk.Entry(self.payment_tab)
...         sid.pack()
...         tk.Label(self.payment_tab, text="Amount:").pack()
...         amount = tk.Entry(self.payment_tab)
...         amount.pack()
...         tk.Label(self.payment_tab, text="Date:").pack()
...         date = tk.Entry(self.payment_tab)
...         date.pack()
...         tk.Button(self.payment_tab, text="Add Payment", command=lambda: payments.loc[len(payments)] = [pid.get(), sid.get(), amount.get(), date.get()]).pack()
... 
...     def setup_delivery_tab(self):
...         tk.Label(self.delivery_tab, text="Delivery ID:").pack()
...         did = tk.Entry(self.delivery_tab)
...         did.pack()
...         tk.Label(self.delivery_tab, text="Contract No:").pack()
...         cno = tk.Entry(self.delivery_tab)
...         cno.pack()
...         tk.Label(self.delivery_tab, text="Date:").pack()
...         date = tk.Entry(self.delivery_tab)
...         date.pack()
...         tk.Label(self.delivery_tab, text="Status:").pack()
        status = tk.Entry(self.delivery_tab)
        status.pack()
        tk.Button(self.delivery_tab, text="Add Delivery", command=lambda: deliveries.loc[len(deliveries)] = [did.get(), cno.get(), date.get(), status.get()]).pack()

if __name__ == "__main__":
    app = ExportManagerApp()
    app.mainloop()
