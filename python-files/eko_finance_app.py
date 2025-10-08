import csv
from datetime import datetime

# --- Configuration for EKO Packaging ---
CSV_FILENAME = 'financial_log_cli.csv'
FIELD_NAMES = [
    "Date", "Description", "BOI", "UB", "Method / Category", "Total"
]

def save_to_csv(data):
    """Saves the entered data to the CSV file."""
    try:
        # Check if file exists to determine if header is needed
        try:
            with open(CSV_FILENAME, 'r') as f:
                has_header = csv.Sniffer().has_header(f.read(1024))
        except FileNotFoundError:
            has_header = False

        with open(CSV_FILENAME, mode='a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)

            # Write header only if the file is new or empty
            if not has_header:
                writer.writerow(FIELD_NAMES)

            writer.writerow(data)
        print(f"\n✅ SUCCESS: Entry saved to {CSV_FILENAME}")
        return True
    except Exception as e:
        print(f"\n❌ ERROR: Failed to save data: {e}")
        return False

def get_numeric_input(prompt):
    """Prompts user for a numeric value and validates the input."""
    while True:
        try:
            value = input(prompt).strip()
            # If nothing is entered, treat it as 0.00
            if not value:
                return 0.00
            # Otherwise, convert to float
            return float(value)
        except ValueError:
            print("❗ Invalid input. Please enter a number (e.g., 1000.50) or leave blank for 0.")

def run_app():
    """Runs the main command-line application loop."""
    print("==================================================")
    print("   EKO Packaging: Financial Data Entry (CLI) ")
    print("==================================================")

    while True:
        print("\n--- New Entry ---")

        # 1. Date (Pre-filled)
        default_date = datetime.now().strftime("%Y-%m-%d")
        date_input = input(f"1. Date [{default_date}]: ").strip()
        date = date_input if date_input else default_date

        # 2. Description
        description = input("2. Description (e.g., Paycheck, Raw Material Purchase): ").strip()
        if not description:
            print("❗ Description cannot be empty.")
            continue

        # 3. Allocation Amounts
        boi_amount = get_numeric_input("3. BOI Amount: ")
        ub_amount = get_numeric_input("4. UB Amount: ")

        # 4. Method / Category
        category = input("5. Method / Category (e.g., Direct Deposit, Cheque, UPI): ").strip()

        # 5. Calculation
        total = boi_amount + ub_amount

        # 6. Summary and Save
        print("\n--- Summary ---")
        print(f"Date: {date}")
        print(f"Description: {description}")
        print(f"BOI: {boi_amount:.2f} | UB: {ub_amount:.2f}")
        print(f"TOTAL: {total:.2f}")

        confirm = input("\nSave this entry? (y/n): ").strip().lower()

        if confirm == 'y':
            data_to_save = [
                date,
                description,
                f"{boi_amount:.2f}",
                f"{ub_amount:.2f}",
                category,
                f"{total:.2f}"
            ]
            save_to_csv(data_to_save)
        else:
            print("Entry cancelled.")

        # Ask if the user wants to continue
        next_entry = input("\nDo you want to enter another transaction? (y/n): ").strip().lower()
        if next_entry != 'y':
            print("\nApplication closed. Goodbye.")
            break

# Execute the main function
if __name__ == "__main__":
    run_app()