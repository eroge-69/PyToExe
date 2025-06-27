def add_expense(expenses, amount, category, description):
    """Adds a new expense to the list."""
    try:
        amount = float(amount)
        if amount <= 0:
            print("Amount must be positive.")
            return
        expense = {
            "amount": amount,
            "category": category.strip().capitalize(),
            "description": description.strip()
        }
        expenses.append(expense)
        print(f"Expense of ${amount:.2f} added to '{category}'.")
    except ValueError:
        print("Invalid amount. Please enter a number.")

def view_expenses(expenses):
    """Displays all recorded expenses."""
    if not expenses:
        print("No expenses recorded yet.")
        return

    print("\n--- Your Expenses ---")
    for i, expense in enumerate(expenses):
        print(f"{i+1}. Amount: ${expense['amount']:.2f}, Category: {expense['category']}, Description: {expense['description']}")
    print("---------------------\n")

def get_total_expenses(expenses):
    """Calculates and displays the total of all expenses."""
    total = sum(item['amount'] for item in expenses)
    print(f"Total expenses: ${total:.2f}")

def main():
    """Main function to run the expense tracker."""
    expenses = [] # This list will store all your expense dictionaries

    while True:
        print("\n--- Expense Tracker Menu ---")
        print("1. Add Expense")
        print("2. View Expenses")
        print("3. Get Total Expenses")
        print("4. Exit")
        print("----------------------------")

        choice = input("Enter your choice: ")

        if choice == '1':
            amount = input("Enter amount: ")
            category = input("Enter category (e.g., Food, Transport, Bills): ")
            description = input("Enter description (optional): ")
            add_expense(expenses, amount, category, description)
        elif choice == '2':
            view_expenses(expenses)
        elif choice == '3':
            get_total_expenses(expenses)
        elif choice == '4':
            print("Exiting Expense Tracker. Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()