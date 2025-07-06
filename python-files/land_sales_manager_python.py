import json
import os
from datetime import datetime
from typing import Dict, List, Optional

class Property:
    def __init__(self, prop_id: int, address: str, size: str, purchase_price: float, 
                 purchase_date: str, listing_price: float, status: str = "For Sale", 
                 description: str = ""):
        self.id = prop_id
        self.address = address
        self.size = size
        self.purchase_price = purchase_price
        self.purchase_date = purchase_date
        self.listing_price = listing_price
        self.status = status
        self.description = description
    
    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'address': self.address,
            'size': self.size,
            'purchase_price': self.purchase_price,
            'purchase_date': self.purchase_date,
            'listing_price': self.listing_price,
            'status': self.status,
            'description': self.description
        }
    
    @classmethod
    def from_dict(cls, data: Dict):
        return cls(
            data['id'], data['address'], data['size'], data['purchase_price'],
            data['purchase_date'], data['listing_price'], data['status'], data['description']
        )
    
    def get_potential_profit(self) -> float:
        return self.listing_price - self.purchase_price
    
    def __str__(self) -> str:
        profit = self.get_potential_profit()
        return f"ID: {self.id} | {self.address} | {self.size} | Status: {self.status} | Profit: ${profit:,.2f}"

class Customer:
    def __init__(self, customer_id: int, name: str, email: str, phone: str, 
                 interested_property: str = "", status: str = "Active", notes: str = ""):
        self.id = customer_id
        self.name = name
        self.email = email
        self.phone = phone
        self.interested_property = interested_property
        self.status = status
        self.notes = notes
    
    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'interested_property': self.interested_property,
            'status': self.status,
            'notes': self.notes
        }
    
    @classmethod
    def from_dict(cls, data: Dict):
        return cls(
            data['id'], data['name'], data['email'], data['phone'],
            data['interested_property'], data['status'], data['notes']
        )
    
    def __str__(self) -> str:
        return f"ID: {self.id} | {self.name} | {self.phone} | {self.email} | Status: {self.status}"

class LandSalesManager:
    def __init__(self, data_file: str = "land_sales_data.json"):
        self.data_file = data_file
        self.properties: List[Property] = []
        self.customers: List[Customer] = []
        self.next_property_id = 1
        self.next_customer_id = 1
        self.load_data()
    
    def load_data(self):
        """Load data from JSON file"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as f:
                    data = json.load(f)
                
                # Load properties
                for prop_data in data.get('properties', []):
                    prop = Property.from_dict(prop_data)
                    self.properties.append(prop)
                    if prop.id >= self.next_property_id:
                        self.next_property_id = prop.id + 1
                
                # Load customers
                for cust_data in data.get('customers', []):
                    customer = Customer.from_dict(cust_data)
                    self.customers.append(customer)
                    if customer.id >= self.next_customer_id:
                        self.next_customer_id = customer.id + 1
                
                print(f"Loaded {len(self.properties)} properties and {len(self.customers)} customers.")
            except Exception as e:
                print(f"Error loading data: {e}")
                self.initialize_sample_data()
        else:
            self.initialize_sample_data()
    
    def save_data(self):
        """Save data to JSON file"""
        try:
            data = {
                'properties': [prop.to_dict() for prop in self.properties],
                'customers': [cust.to_dict() for cust in self.customers]
            }
            with open(self.data_file, 'w') as f:
                json.dump(data, f, indent=2)
            print("Data saved successfully.")
        except Exception as e:
            print(f"Error saving data: {e}")
    
    def initialize_sample_data(self):
        """Initialize with sample data"""
        sample_properties = [
            Property(1, "123 Oak Valley Drive", "2.5 acres", 45000, "2023-03-15", 65000, "For Sale", "Beautiful wooded lot with creek access"),
            Property(2, "456 Pine Ridge Road", "1.8 acres", 32000, "2023-07-22", 48000, "Under Contract", "Level building site with mountain views")
        ]
        
        sample_customers = [
            Customer(1, "John Smith", "john.smith@email.com", "(555) 123-4567", "123 Oak Valley Drive", "Active", "Looking for recreational property, cash buyer"),
            Customer(2, "Sarah Johnson", "sarah.johnson@email.com", "(555) 987-6543", "456 Pine Ridge Road", "Under Contract", "Building custom home, needs financing approval")
        ]
        
        self.properties = sample_properties
        self.customers = sample_customers
        self.next_property_id = 3
        self.next_customer_id = 3
        self.save_data()
        print("Initialized with sample data.")
    
    def add_property(self):
        """Add a new property"""
        print("\n=== Add New Property ===")
        address = input("Address: ").strip()
        size = input("Size (e.g., 2.5 acres): ").strip()
        
        while True:
            try:
                purchase_price = float(input("Purchase Price: $"))
                break
            except ValueError:
                print("Please enter a valid number for purchase price.")
        
        while True:
            try:
                listing_price = float(input("Listing Price: $"))
                break
            except ValueError:
                print("Please enter a valid number for listing price.")
        
        while True:
            purchase_date = input("Purchase Date (YYYY-MM-DD): ").strip()
            try:
                datetime.strptime(purchase_date, "%Y-%m-%d")
                break
            except ValueError:
                print("Please enter date in YYYY-MM-DD format.")
        
        print("Status options: For Sale, Under Contract, Sold")
        status = input("Status (default: For Sale): ").strip() or "For Sale"
        description = input("Description: ").strip()
        
        property_obj = Property(
            self.next_property_id, address, size, purchase_price,
            purchase_date, listing_price, status, description
        )
        
        self.properties.append(property_obj)
        self.next_property_id += 1
        self.save_data()
        print(f"Property added successfully! ID: {property_obj.id}")
    
    def add_customer(self):
        """Add a new customer"""
        print("\n=== Add New Customer ===")
        name = input("Name: ").strip()
        email = input("Email: ").strip()
        phone = input("Phone: ").strip()
        
        if self.properties:
            print("\nAvailable Properties:")
            for prop in self.properties:
                print(f"  {prop.id}: {prop.address}")
            
            while True:
                prop_choice = input("Interested Property ID (or press Enter to skip): ").strip()
                if not prop_choice:
                    interested_property = ""
                    break
                try:
                    prop_id = int(prop_choice)
                    prop = next((p for p in self.properties if p.id == prop_id), None)
                    if prop:
                        interested_property = prop.address
                        break
                    else:
                        print("Property ID not found.")
                except ValueError:
                    print("Please enter a valid property ID.")
        else:
            interested_property = ""
        
        print("Status options: Active, Under Contract, Inactive")
        status = input("Status (default: Active): ").strip() or "Active"
        notes = input("Notes: ").strip()
        
        customer = Customer(
            self.next_customer_id, name, email, phone,
            interested_property, status, notes
        )
        
        self.customers.append(customer)
        self.next_customer_id += 1
        self.save_data()
        print(f"Customer added successfully! ID: {customer.id}")
    
    def view_properties(self):
        """View all properties"""
        if not self.properties:
            print("No properties found.")
            return
        
        print("\n=== Properties ===")
        print(f"{'ID':<3} {'Address':<25} {'Size':<12} {'Purchase':<10} {'Listing':<10} {'Profit':<10} {'Status':<15}")
        print("-" * 95)
        
        total_investment = 0
        total_potential = 0
        
        for prop in self.properties:
            profit = prop.get_potential_profit()
            total_investment += prop.purchase_price
            total_potential += profit
            
            print(f"{prop.id:<3} {prop.address[:24]:<25} {prop.size:<12} "
                  f"${prop.purchase_price:>8,.0f} ${prop.listing_price:>8,.0f} "
                  f"${profit:>8,.0f} {prop.status:<15}")
        
        print("-" * 95)
        print(f"Total Investment: ${total_investment:,.2f}")
        print(f"Total Potential Profit: ${total_potential:,.2f}")
    
    def view_customers(self):
        """View all customers"""
        if not self.customers:
            print("No customers found.")
            return
        
        print("\n=== Customers ===")
        print(f"{'ID':<3} {'Name':<20} {'Phone':<15} {'Email':<25} {'Status':<12} {'Property':<25}")
        print("-" * 100)
        
        for customer in self.customers:
            print(f"{customer.id:<3} {customer.name[:19]:<20} {customer.phone:<15} "
                  f"{customer.email[:24]:<25} {customer.status:<12} {customer.interested_property[:24]:<25}")
    
    def search_properties(self):
        """Search properties by address or description"""
        search_term = input("Enter search term (address or description): ").strip().lower()
        
        if not search_term:
            print("Search term cannot be empty.")
            return
        
        found_properties = []
        for prop in self.properties:
            if (search_term in prop.address.lower() or 
                search_term in prop.description.lower()):
                found_properties.append(prop)
        
        if found_properties:
            print(f"\n=== Found {len(found_properties)} Properties ===")
            for prop in found_properties:
                print(f"ID: {prop.id}")
                print(f"Address: {prop.address}")
                print(f"Size: {prop.size}")
                print(f"Purchase Price: ${prop.purchase_price:,.2f}")
                print(f"Listing Price: ${prop.listing_price:,.2f}")
                print(f"Potential Profit: ${prop.get_potential_profit():,.2f}")
                print(f"Status: {prop.status}")
                print(f"Description: {prop.description}")
                print("-" * 50)
        else:
            print("No properties found matching the search term.")
    
    def search_customers(self):
        """Search customers by name or email"""
        search_term = input("Enter search term (name or email): ").strip().lower()
        
        if not search_term:
            print("Search term cannot be empty.")
            return
        
        found_customers = []
        for customer in self.customers:
            if (search_term in customer.name.lower() or 
                search_term in customer.email.lower()):
                found_customers.append(customer)
        
        if found_customers:
            print(f"\n=== Found {len(found_customers)} Customers ===")
            for customer in found_customers:
                print(f"ID: {customer.id}")
                print(f"Name: {customer.name}")
                print(f"Email: {customer.email}")
                print(f"Phone: {customer.phone}")
                print(f"Interested Property: {customer.interested_property}")
                print(f"Status: {customer.status}")
                print(f"Notes: {customer.notes}")
                print("-" * 50)
        else:
            print("No customers found matching the search term.")
    
    def update_property_status(self):
        """Update property status"""
        if not self.properties:
            print("No properties available to update.")
            return
        
        self.view_properties()
        
        while True:
            try:
                prop_id = int(input("\nEnter Property ID to update: "))
                prop = next((p for p in self.properties if p.id == prop_id), None)
                if prop:
                    break
                else:
                    print("Property ID not found.")
            except ValueError:
                print("Please enter a valid property ID.")
        
        print(f"\nCurrent status: {prop.status}")
        print("Status options: For Sale, Under Contract, Sold")
        new_status = input("New status: ").strip()
        
        if new_status:
            prop.status = new_status
            self.save_data()
            print(f"Property status updated to: {new_status}")
        else:
            print("Status update cancelled.")
    
    def generate_report(self):
        """Generate a summary report"""
        print("\n=== Land Sales Report ===")
        print(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("-" * 50)
        
        # Property statistics
        total_properties = len(self.properties)
        for_sale = len([p for p in self.properties if p.status == "For Sale"])
        under_contract = len([p for p in self.properties if p.status == "Under Contract"])
        sold = len([p for p in self.properties if p.status == "Sold"])
        
        total_investment = sum(p.purchase_price for p in self.properties)
        total_potential_profit = sum(p.get_potential_profit() for p in self.properties)
        
        print(f"Total Properties: {total_properties}")
        print(f"  - For Sale: {for_sale}")
        print(f"  - Under Contract: {under_contract}")
        print(f"  - Sold: {sold}")
        print(f"Total Investment: ${total_investment:,.2f}")
        print(f"Total Potential Profit: ${total_potential_profit:,.2f}")
        
        # Customer statistics
        total_customers = len(self.customers)
        active_customers = len([c for c in self.customers if c.status == "Active"])
        contract_customers = len([c for c in self.customers if c.status == "Under Contract"])
        
        print(f"\nTotal Customers: {total_customers}")
        print(f"  - Active: {active_customers}")
        print(f"  - Under Contract: {contract_customers}")
        
        # Most profitable properties
        if self.properties:
            most_profitable = max(self.properties, key=lambda p: p.get_potential_profit())
            print(f"\nMost Profitable Property:")
            print(f"  {most_profitable.address} - ${most_profitable.get_potential_profit():,.2f}")
    
    def run(self):
        """Main application loop"""
        print("Welcome to Land Sales Management System")
        print("=" * 50)
        
        while True:
            print("\n=== Main Menu ===")
            print("1. Add Property")
            print("2. Add Customer")
            print("3. View Properties")
            print("4. View Customers")
            print("5. Search Properties")
            print("6. Search Customers")
            print("7. Update Property Status")
            print("8. Generate Report")
            print("9. Save & Exit")
            
            choice = input("\nEnter your choice (1-9): ").strip()
            
            if choice == "1":
                self.add_property()
            elif choice == "2":
                self.add_customer()
            elif choice == "3":
                self.view_properties()
            elif choice == "4":
                self.view_customers()
            elif choice == "5":
                self.search_properties()
            elif choice == "6":
                self.search_customers()
            elif choice == "7":
                self.update_property_status()
            elif choice == "8":
                self.generate_report()
            elif choice == "9":
                self.save_data()
                print("Thank you for using Land Sales Management System!")
                break
            else:
                print("Invalid choice. Please try again.")

if __name__ == "__main__":
    manager = LandSalesManager()
    manager.run()