import pandas as pd
from datetime import date

class AccountingSoftware:
    def __init__(self):
        # Initialize an empty DataFrame for the General Ledger
        self.general_ledger = pd.DataFrame(columns=[
            'Date', 'Account', 'Debit', 'Credit', 'Description'
        ])
        # Initialize an empty DataFrame for the Chart of Accounts
        self.chart_of_accounts = pd.DataFrame(columns=['AccountName', 'AccountType'])

    def add_account(self, account_name, account_type):
        """Adds a new account to the chart of accounts."""
        if account_name not in self.chart_of_accounts['AccountName'].values:
            new_account = pd.DataFrame([[account_name, account_type]], columns=['AccountName', 'AccountType'])
            self.chart_of_accounts = pd.concat([self.chart_of_accounts, new_account], ignore_index=True)
            print(f"Account '{account_name}' added successfully.")
        else:
            print(f"Account '{account_name}' already exists.")

    def record_transaction(self, transaction_date, description, debit_account, credit_account, amount):
        """
        Records a new transaction in the general ledger.
        In a real-world double-entry system, a single transaction would involve at least one debit and one credit.
        """
        # Validate that the accounts exist
        if debit_account not in self.chart_of_accounts['AccountName'].values or \
           credit_account not in self.chart_of_accounts['AccountName'].values:
            print("Error: One or both accounts do not exist in the Chart of Accounts.")
            return

        # Create the debit and credit entries for the transaction
        debit_entry = {
            'Date': transaction_date,
            'Account': debit_account,
            'Debit': amount,
            'Credit': 0,
            'Description': description
        }
        credit_entry = {
            'Date': transaction_date,
            'Account': credit_account,
            'Debit': 0,
            'Credit': amount,
            'Description': description
        }

        # Add the new entries to the general ledger
        self.general_ledger = pd.concat([self.general_ledger, pd.DataFrame([debit_entry, credit_entry])], ignore_index=True)
        print("Transaction recorded successfully.")

    def display_general_ledger(self):
        """Displays the current state of the general ledger."""
        print("\n--- General Ledger ---")
        print(self.general_ledger.to_string())

# Example Usage:
if __name__ == '__main__':
    app = AccountingSoftware()

    # Add some initial accounts
    app.add_account('Cash', 'Asset')
    app.add_account('Sales Revenue', 'Revenue')
    app.add_account('Office Supplies', 'Asset')
    app.add_account('Accounts Payable', 'Liability')


    # Record a sample transaction
    app.record_transaction(date.today(), 'Initial cash investment', 'Cash', 'Sales Revenue', 1000.00)
    app.record_transaction(date.today(), 'Purchase of office supplies on credit', 'Office Supplies', 'Accounts Payable', 150.00)

    # Display the general ledger
    app.display_general_ledger()