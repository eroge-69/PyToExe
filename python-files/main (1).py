import pandas as pd
import os
from datetime import datetime

# --- Constants for filenames ---
CHART_OF_ACCOUNTS_FILE = 'chart_of_accounts.csv'
GENERAL_LEDGER_FILE = 'general_ledger.csv'

def initialize_files():
    """Creates the necessary CSV files if they don't already exist."""
    if not os.path.exists(CHART_OF_ACCOUNTS_FILE):
        df_accounts = pd.DataFrame(columns=['AccountName', 'AccountType', 'Balance'])
        df_accounts.to_csv(CHART_OF_ACCOUNTS_FILE, index=False)
        print(f"Created '{CHART_OF_ACCOUNTS_FILE}'.")

    if not os.path.exists(GENERAL_LEDGER_FILE):
        df_ledger = pd.DataFrame(columns=['Date', 'Account', 'Description', 'Debit', 'Credit'])
        df_ledger.to_csv(GENERAL_LEDGER_FILE, index=False)
        print(f"Created '{GENERAL_LEDGER_FILE}'.")

def add_account():
    """Adds a new account to the chart of accounts."""
    df_accounts = pd.read_csv(CHART_OF_ACCOUNTS_FILE)

    print("\n--- Add a New Account ---")
    name = input("Enter new account name (e.g., 'Office Supplies'): ").strip()
    
    # Check if account already exists
    if name.lower() in df_accounts['AccountName'].str.lower().values:
        print(f"Error: Account '{name}' already exists.")
        return

    acc_type = input("Enter account type (Asset, Liability, Equity, Revenue, Expense): ").strip().capitalize()
    
    # Simple validation for account type
    valid_types = ['Asset', 'Liability', 'Equity', 'Revenue', 'Expense']
    if acc_type not in valid_types:
        print(f"Error: Invalid account type. Must be one of {valid_types}.")
        return

    new_account = pd.DataFrame({
        'AccountName': [name],
        'AccountType': [acc_type],
        'Balance': [0.0]
    })

    df_accounts = pd.concat([df_accounts, new_account], ignore_index=True)
    df_accounts.to_csv(CHART_OF_ACCOUNTS_FILE, index=False)
    print(f"Success! Account '{name}' added.")

def record_journal_entry():
    """Records a double-entry transaction to the general ledger."""
    print("\n--- Record a New Journal Entry ---")
    df_accounts = pd.read_csv(CHART_OF_ACCOUNTS_FILE)
    df_ledger = pd.read_csv(GENERAL_LEDGER_FILE)

    # Display accounts for user reference
    print("Available Accounts:")
    print(df_accounts[['AccountName', 'AccountType']].to_string(index=False))
    print("-" * 30)

    # Get transaction details
    trans_date = datetime.now().strftime('%Y-%m-%d')
    description = input("Enter transaction description: ").strip()
    
    try:
        amount = float(input("Enter transaction amount: "))
        if amount <= 0:
            print("Error: Amount must be positive.")
            return
    except ValueError:
        print("Error: Invalid amount entered.")
        return

    debit_account = input("Enter account to DEBIT: ").strip()
    credit_account = input("Enter account to CREDIT: ").strip()

    # Validate accounts
    all_accounts = df_accounts['AccountName'].tolist()
    if debit_account not in all_accounts or credit_account not in all_accounts:
        print("Error: One or both accounts do not exist. Please add them first.")
        return

    # Create entries
    debit_entry = {'Date': trans_date, 'Account': debit_account, 'Description': description, 'Debit': amount, 'Credit': 0.0}
    credit_entry = {'Date': trans_date, 'Account': credit_account, 'Description': description, 'Debit': 0.0, 'Credit': amount}
    
    # Append to ledger DataFrame and save
    new_entries = pd.DataFrame([debit_entry, credit_entry])
    df_ledger = pd.concat([df_ledger, new_entries], ignore_index=True)
    df_ledger.to_csv(GENERAL_LEDGER_FILE, index=False)

    print("Success! Journal entry recorded.")

def view_general_ledger():
    """Displays all entries in the general ledger."""
    print("\n" + "="*40)
    print("         GENERAL LEDGER")
    print("="*40)
    try:
        df_ledger = pd.read_csv(GENERAL_LEDGER_FILE)
        if df_ledger.empty:
            print("The General Ledger is empty.")
        else:
            print(df_ledger.to_string(index=False))
    except FileNotFoundError:
        print("General Ledger file not found. No transactions recorded yet.")
    print("="*40 + "\n")

def generate_trial_balance():
    """Calculates and displays the trial balance."""
    print("\n" + "="*40)
    print("            TRIAL BALANCE")
    print(f"             As of {datetime.now().strftime('%Y-%m-%d')}")
    print("="*40)
    
    try:
        df_ledger = pd.read_csv(GENERAL_LEDGER_FILE)
        if df_ledger.empty:
            print("No transactions to report.")
            print("="*40 + "\n")
            return

        # Calculate total debits and credits for each account
        account_totals = df_ledger.groupby('Account').agg(
            TotalDebit=('Debit', 'sum'),
            TotalCredit=('Credit', 'sum')
        ).reset_index()

        # Calculate the final balance and determine if it's a debit or credit balance
        account_totals['DebitBalance'] = 0.0
        account_totals['CreditBalance'] = 0.0

        for i, row in account_totals.iterrows():
            balance = row['TotalDebit'] - row['TotalCredit']
            if balance > 0:
                account_totals.loc[i, 'DebitBalance'] = balance
            else:
                account_totals.loc[i, 'CreditBalance'] = -balance

        # Display the report
        report = account_totals[['Account', 'DebitBalance', 'CreditBalance']]
        print(report.to_string(index=False))
        print("-" * 40)

        # Sum the columns and display totals
        total_debits = report['DebitBalance'].sum()
        total_credits = report['CreditBalance'].sum()
        print(f"{'Total:':<20} {total_debits:>10.2f} {total_credits:>10.2f}")
        print("="*40)

        if abs(total_debits - total_credits) < 0.001: # Use a small tolerance for float comparison
            print("✅ Debits equal Credits. The books are balanced.")
        else:
            print("❌ WARNING: Debits DO NOT equal Credits. The books are out of balance.")
        print("="*40 + "\n")

    except FileNotFoundError:
        print("General Ledger file not found. No transactions recorded yet.")
        print("="*40 + "\n")

def display_menu():
    """Displays the main menu to the user."""
    print("\n--- Simple Accounting Software ---")
    print("1. Add a new account")
    print("2. Record a journal entry")
    print("3. View General Ledger")
    print("4. Generate Trial Balance")
    print("5. Exit")
    return input("Please choose an option (1-5): ")

def main():
    """Main function to run the application loop."""
    initialize_files()
    while True:
        choice = display_menu()
        if choice == '1':
            add_account()
        elif choice == '2':
            record_journal_entry()
        elif choice == '3':
            view_general_ledger()
        elif choice == '4':
            generate_trial_balance()
        elif choice == '5':
            print("Exiting program. Goodbye!")
            break
        else:
            print("Invalid option. Please try again.")

if __name__ == "__main__":
    main()