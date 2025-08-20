import os
import csv

# Folder & file setup
DATA_FOLDER = "data"
DATA_FILE = os.path.join(DATA_FOLDER, "works.csv")

# Ensure folder exists
os.makedirs(DATA_FOLDER, exist_ok=True)

# Field names (A - J)
FIELDS = [
    "Customer Name",     # A
    "Phone Number",      # B
    "Customer ID",       # C
    "Total",             # D
    "Paid (Advance)",    # E
    "Balance",           # F
    "Frame Size",        # G
    "Required Date",     # H
    "Our Cost",          # I
    "Date Today"         # J
]

# Ensure file exists with headers
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(FIELDS)


def new_work():
    print("\n--- Enter New Work ---")
    row = []
    for field in FIELDS:
        value = input(f"{field}: ")
        row.append(value)

    with open(DATA_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(row)

    print("✅ Work saved successfully!\n")


def check_recent_work():
    print("\n--- Check Recent Work ---")
    cust_id = input("Enter Customer ID: ")

    with open(DATA_FILE, "r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        found = False
        for row in reader:
            if row["Customer ID"] == cust_id:
                print("\n--- Work Details ---")
                for key in FIELDS:
                    print(f"{key}: {row[key]}")
                found = True
                break

        if not found:
            print("❌ No record found for that Customer ID.\n")


def profit_certain_job():
    print("\n--- Profit of a Certain Job ---")
    cust_id = input("Enter Customer ID: ")

    with open(DATA_FILE, "r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        found = False
        for row in reader:
            if row["Customer ID"] == cust_id:
                total = float(row["Total"])
                cost = float(row["Our Cost"])
                profit = total - cost
                print(f"\nProfit for Customer ID {cust_id}: {profit}")
                found = True
                break

        if not found:
            print("❌ No record found for that Customer ID.\n")


def profit_month():
    print("\n--- Profit of the Month ---")
    month = input("Enter month (MM): ")

    total_sum = 0.0
    cost_sum = 0.0
    count = 0

    with open(DATA_FILE, "r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            date_today = row["Date Today"]  # YYYY/MM/DD
            if len(date_today) >= 7 and date_today[5:7] == month:
                total_sum += float(row["Total"])
                cost_sum += float(row["Our Cost"])
                count += 1

    if count > 0:
        profit = total_sum - cost_sum
        print(f"\n✅ Total Jobs in {month}: {count}")
        print(f"Total: {total_sum}")
        print(f"Cost: {cost_sum}")
        print(f"Profit: {profit}\n")
    else:
        print("❌ No records found for that month.\n")


def main():
    while True:
        print("===== MENU =====")
        print("1) New Work")
        print("2) Check the Recent Work")
        print("3) Check the Profit of a Certain Job")
        print("4) Check the Profit of the Month")
        print("5) Exit")

        choice = input("Choose an option (1-5): ")

        if choice == "1":
            new_work()
        elif choice == "2":
            check_recent_work()
        elif choice == "3":
            profit_certain_job()
        elif choice == "4":
            profit_month()
        elif choice == "5":
            print("Goodbye!")
            break
        else:
            print("❌ Invalid choice, try again.\n")


if __name__ == "__main__":
    main()
