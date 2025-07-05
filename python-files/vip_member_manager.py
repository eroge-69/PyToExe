import pandas as pd
import os
import shutil

# Constants
FILE_NAME = "VIP Members.xlsm"
BACKUP_NAME = "VIP Members_backup.xlsm"
SHEET_NAME = "Worksheet"

# Get the directory where the script or EXE is running
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FILE_PATH = os.path.join(BASE_DIR, FILE_NAME)
BACKUP_PATH = os.path.join(BASE_DIR, BACKUP_NAME)

# Load and clean data
def load_data():
    df = pd.read_excel(FILE_PATH, sheet_name=SHEET_NAME, skiprows=4)
    df.dropna(how='all', inplace=True)
    df.fillna('', inplace=True)
    return df

def save_data(df):
    # Backup original file
    try:
        shutil.copy2(FILE_PATH, BACKUP_PATH)
        print(f"Backup saved to '{BACKUP_NAME}'")
    except Exception as e:
        print(f"Backup failed: {e}")

    with pd.ExcelWriter(FILE_PATH, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
        df.to_excel(writer, sheet_name=SHEET_NAME, index=False)
    print("Data saved successfully.")

def view_members(df):
    print("\n--- VIP Card Members ---")
    print(df[['CARD NUMBER', 'MEMBERS NAME', 'Card Type']].to_string(index=False))

def search_member(df):
    keyword = input("Enter name or card number to search: ").strip().lower()
    result = df[df.apply(lambda row: keyword in str(row['MEMBERS NAME']).lower() or \
                                      keyword in str(row['CARD NUMBER']).lower(), axis=1)]
    if not result.empty:
        print("\n--- Search Results ---")
        print(result.to_string(index=False))
    else:
        print("No matching member found.")

def add_member(df):
    print("\n--- Add New Member ---")
    new_data = {
        'CARD NUMBER': input("Card Number: ").strip(),
        'MEMBERS NAME': input("Name: ").strip(),
        'ADDRESS': input("Address: ").strip(),
        'CONTACT NUMBER': input("Contact Number: ").strip(),
        'DATE OF MEMBER': input("Date of Membership: ").strip(),
        'BIRTHDAY': input("Birthday: ").strip(),
        'Card Type': input("Card Type: ").strip(),
        'SUB-MEMBER': input("Sub Member 1: ").strip(),
        'Sub Member2': input("Sub Member 2: ").strip(),
        'Sub Member3': input("Sub Member 3: ").strip(),
        'Sub Member4': input("Sub Member 4: ").strip(),
    }
    df.loc[len(df)] = new_data
    print("Member added successfully.")
    return df

def main():
    df = load_data()

    while True:
        print("\n==== VIP Card Member Manager ====")
        print("1. View All Members")
        print("2. Search Member")
        print("3. Add Member")
        print("4. Save and Exit")

        choice = input("Enter your choice: ").strip()

        if choice == '1':
            view_members(df)
        elif choice == '2':
            search_member(df)
        elif choice == '3':
            df = add_member(df)
        elif choice == '4':
            save_data(df)
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
