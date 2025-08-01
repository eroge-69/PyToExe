import csv
import os

# File to store passwords (could be a JSON or a simple text file for storing entries)
filename = 'passwords.csv'

# Fieldnames for the CSV file
fieldnames = ['name', 'url', 'username', 'password', 'note']

# Initialize an empty list to store password entries
passwords_data = []

# Function to load existing passwords from the CSV file
def load_passwords():
    if os.path.exists(filename):
        with open(filename, mode='r', newline='') as file:
            reader = csv.DictReader(file)
            for row in reader:
                passwords_data.append(row)

# Function to save passwords to the CSV file
def save_passwords():
    with open(filename, mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(passwords_data)

# Function to get password entry from the user
def get_password_entry():
    name = input("Enter the name (e.g., Gmail, Facebook, etc.): ")
    url = input("Enter the URL (e.g., https://gmail.com): ")
    username = input("Enter the username/email: ")
    password = input("Enter the password: ")
    note = input("Enter a note (optional): ")
    return {
        "name": name,
        "url": url,
        "username": username,
        "password": password,
        "note": note
    }

# Function to display the list of saved passwords
def display_passwords():
    if not passwords_data:
        print("No passwords found.")
    else:
        print(f"{'Name':<20}{'URL':<30}{'Username':<30}{'Note':<40}")
        print("="*120)
        for entry in passwords_data:
            print(f"{entry['name']:<20}{entry['url']:<30}{entry['username']:<30}{entry['note']:<40}")

# Main menu
def main_menu():
    while True:
        print("\n--- Password Manager ---")
        print("1. Add a new password entry")
        print("2. View saved passwords")
        print("3. Export passwords to CSV")
        print("4. Exit")
        choice = input("Enter your choice: ")

        if choice == "1":
            print("\n--- Add New Password ---")
            password_entry = get_password_entry()
            passwords_data.append(password_entry)
            save_passwords()  # Save to file after adding
            print("Password entry added successfully!")

        elif choice == "2":
            print("\n--- Saved Passwords ---")
            display_passwords()

        elif choice == "3":
            print("\n--- Exporting Passwords ---")
            save_passwords()
            print(f"Passwords exported to {filename}.")

        elif choice == "4":
            print("Exiting the password manager.")
            break

        else:
            print("Invalid choice. Please select a valid option.")

# Load existing passwords from CSV (if file exists) before showing the menu
load_passwords()
main_menu()
