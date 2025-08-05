import pickle
#import os

# ----- Account Class -----
class Account:
    def __init__(self, acc_no, name, acc_type, balance):
        self.acc_no = acc_no
        self.name = name
        self.acc_type = acc_type
        self.balance = balance

    def display_account(self):
        print(f"Acc No: {self.acc_no}, Name: {self.name}, Type: {self.acc_type}, Balance: ₹{self.balance}")

    def deposit(self, amount):
        self.balance += amount

    def withdraw(self, amount):
        if self.balance >= amount:
            self.balance -= amount
        else:
            print("Insufficient balance!")

    def modify_account(self, name, acc_type):
        self.name = name
        self.acc_type = acc_type

# ----- File Handling Functions -----

def write_account(account):
    with open("bank.dat", "ab") as f:
        pickle.dump(account, f)

def display_all():
    try:
        with open("bank.dat", "rb") as f:
            print("\nAll Bank Accounts:\n")
            while True:
                acc = pickle.load(f)
                acc.display_account()
    except (EOFError, FileNotFoundError):
        pass

def find_account(acc_no):
    found = False
    try:
        with open("bank.dat", "rb") as f:
            while True:
                acc = pickle.load(f)
                if acc.acc_no == acc_no:
                    acc.display_account()
                    found = True
                    break
    except (EOFError, FileNotFoundError):
        pass
    if not found:
        print("Account not found.")

def modify_account_file(acc_no, new_name, new_type):
    updated = False
    accounts = []
    try:
        with open("bank.dat", "rb") as f:
            while True:
                acc = pickle.load(f)
                if acc.acc_no == acc_no:
                    acc.modify_account(new_name, new_type)
                    updated = True
                accounts.append(acc)
    except EOFError:
        pass
    except FileNotFoundError:
        print("No data file found.")
        return

    with open("bank.dat", "wb") as f:
        for acc in accounts:
            pickle.dump(acc, f)
    if updated:
        print("Account updated successfully.")
    else:
        print("Account not found.")

def delete_account(acc_no):
    accounts = []
    deleted = False
    try:
        with open("bank.dat", "rb") as f:
            while True:
                acc = pickle.load(f)
                if acc.acc_no != acc_no:
                    accounts.append(acc)
                else:
                    deleted = True
    except EOFError:
        pass
    except FileNotFoundError:
        print("No data file found.")
        return

    with open("bank.dat", "wb") as f:
        for acc in accounts:
            pickle.dump(acc, f)
    if deleted:
        print("Account deleted.")
    else:
        print("Account not found.")

def deposit_withdraw(acc_no, option, amount):
    updated = False
    accounts = []
    try:
        with open("bank.dat", "rb") as f:
            while True:
                acc = pickle.load(f)
                if acc.acc_no == acc_no:
                    if option == 'deposit':
                        acc.deposit(amount)
                    elif option == 'withdraw':
                        acc.withdraw(amount)
                    updated = True
                accounts.append(acc)
    except EOFError:
        pass
    except FileNotFoundError:
        print("No data file found.")
        return

    with open("bank.dat", "wb") as f:
        for acc in accounts:
            pickle.dump(acc, f)
    if updated:
        print(f"{option.capitalize()} successful.")
    else:
        print("Account not found.")

# ----- Main Menu -----

def main():
    while True:
        print("\n--- Bank Management System ---")
        print("1. Create New Account")
        print("2. Display All Accounts")
        print("3. Search Account")
        print("4. Modify Account")
        print("5. Delete Account")
        print("6. Deposit Money")
        print("7. Withdraw Money")
        print("8. Exit")

        choice = input("Enter your choice (1-8): ")

        if choice == '1':
            acc_no = int(input("Enter Account Number: "))
            name = input("Enter Name: ")
            acc_type = input("Enter Account Type (S/C): ").upper()
            balance = float(input("Enter Initial Deposit: ₹"))
            acc = Account(acc_no, name, acc_type, balance)
            write_account(acc)
            print("Account Created Successfully.")

        elif choice == '2':
            display_all()

        elif choice == '3':
            acc_no = int(input("Enter Account Number to Search: "))
            find_account(acc_no)

        elif choice == '4':
            acc_no = int(input("Enter Account Number to Modify: "))
            name = input("Enter New Name: ")
            acc_type = input("Enter New Type (S/C): ").upper()
            modify_account_file(acc_no, name, acc_type)

        elif choice == '5':
            acc_no = int(input("Enter Account Number to Delete: "))
            delete_account(acc_no)

        elif choice == '6':
            acc_no = int(input("Enter Account Number: "))
            amount = float(input("Enter Amount to Deposit: ₹"))
            deposit_withdraw(acc_no, 'deposit', amount)

        elif choice == '7':
            acc_no = int(input("Enter Account Number: "))
            amount = float(input("Enter Amount to Withdraw: ₹"))
            deposit_withdraw(acc_no, 'withdraw', amount)

        elif choice == '8':
            print("Exiting program...")
            break

        else:
            print("Invalid choice. Try again.")

# Run the Program
#if __name__ == "_main_":
main()
