import json
import os
from datetime import datetime

# Define the file name for storing inventory data
INVENTORY_FILE = 'chemical_inventory.json'

def load_inventory():
   """Loads inventory data from a JSON file."""
   if os.path.exists(INVENTORY_FILE):
       with open(INVENTORY_FILE, 'r') as f:
           return json.load(f)
   return []

def save_inventory(inventory):
   """Saves inventory data to a JSON file."""
   with open(INVENTORY_FILE, 'w') as f:
       json.dump(inventory, f, indent=4)

def add_chemical(inventory):
   """Adds a new chemical entry to the inventory."""
   print("\n--- Add a New Chemical ---")
   
   # Get user input for each entry
   chemical_name = input("Enter Chemical Name: ").strip()
   supplier_name = input("Enter Supplier Name: ").strip()
   supplier_lot_no = input("Enter Supplier Lot No.: ").strip()
   
   # Validate and get expiry date
   while True:
       try:
           expiry_date_str = input("Enter Expiry Date (YYYY-MM-DD): ").strip()
           datetime.strptime(expiry_date_str, "%Y-%m-%d")
           break
       except ValueError:
           print("Invalid date format. Please use YYYY-MM-DD.")
   
   # Validate and get volume
   while True:
       try:
           volume = float(input("Enter Volume (e.g., 100.5): "))
           break
       except ValueError:
           print("Invalid volume. Please enter a number.")
           
   # Validate and get number of stock
   while True:
       try:
           number_of_stock = int(input("Enter Number of Stock: "))
           break
       except ValueError:
           print("Invalid number of stock. Please enter an integer.")

   # Create the new chemical entry dictionary
   new_chemical = {
       "chemical_name": chemical_name,
       "supplier_name": supplier_name,
       "supplier_lot_no": supplier_lot_no,
       "expiry_date": expiry_date_str,
       "volume": volume,
       "number_of_stock": number_of_stock
   }
   
   # Add the new entry to the inventory and save
   inventory.append(new_chemical)
   save_inventory(inventory)
   print("✅ Chemical added successfully!")

def view_inventory(inventory):
   """Displays the entire chemical inventory."""
   print("\n--- Chemical Inventory ---")
   if not inventory:
       print("The inventory is empty.")
       return
   
   # Iterate through and print each chemical entry
   for i, chem in enumerate(inventory, 1):
       print(f"\nEntry #{i}")
       print(f"  Chemical Name: {chem['chemical_name']}")
       print(f"  Supplier Name: {chem['supplier_name']}")
       print(f"  Supplier Lot No.: {chem['supplier_lot_no']}")
       print(f"  Expiry Date: {chem['expiry_date']}")
       print(f"  Volume: {chem['volume']}")
       print(f"  Number of Stock: {chem['number_of_stock']}")

def main():
   """Main function to run the inventory application."""
   inventory = load_inventory()
   
   while True:
       print("\n--- Menu ---")
       print("1. Add a new chemical")
       print("2. View inventory")
       print("3. Exit")
       
       choice = input("Enter your choice (1-3): ")
       
       if choice == '1':
           add_chemical(inventory)
       elif choice == '2':
           view_inventory(inventory)
       elif choice == '3':
           print("Goodbye! 👋")
           break
       else:
           print("Invalid choice. Please try again.")

if __name__ == "__main__":
   main()