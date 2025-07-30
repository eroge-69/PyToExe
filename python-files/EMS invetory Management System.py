import json
import os
from datetime import datetime, timedelta
import uuid # For generating unique IDs

# --- Data Models ---

class Item:
    """Represents an inventory item."""
    def __init__(self, name, quantity, item_type, location, expiration_date=None, ambulance_id=None, item_id=None, created_at=None):
        self.id = item_id if item_id else str(uuid.uuid4())
        self.name = name
        self.quantity = quantity
        self.type = item_type # 'station', 'ambulance', 'medication'
        self.location = location # e.g., "Main Storage", "Ambulance 1", "Medication Cabinet"
        self.expiration_date = expiration_date # YYYY-MM-DD format (string)
        self.ambulance_id = ambulance_id # ID of the ambulance if type is 'ambulance'
        self.created_at = created_at if created_at else datetime.now().isoformat()

    def to_dict(self):
        """Converts the Item object to a dictionary for JSON serialization."""
        return {
            "id": self.id,
            "name": self.name,
            "quantity": self.quantity,
            "type": self.type,
            "location": self.location,
            "expiration_date": self.expiration_date,
            "ambulance_id": self.ambulance_id,
            "created_at": self.created_at
        }

    @staticmethod
    def from_dict(data):
        """Creates an Item object from a dictionary."""
        return Item(
            item_id=data["id"],
            name=data["name"],
            quantity=data["quantity"],
            item_type=data["type"],
            location=data["location"],
            expiration_date=data.get("expiration_date"),
            ambulance_id=data.get("ambulance_id"),
            created_at=data.get("created_at")
        )

class Ambulance:
    """Represents an ambulance unit."""
    def __init__(self, name, amb_id=None, created_at=None):
        self.id = amb_id if amb_id else str(uuid.uuid4())
        self.name = name
        self.created_at = created_at if created_at else datetime.now().isoformat()

    def to_dict(self):
        """Converts the Ambulance object to a dictionary for JSON serialization."""
        return {
            "id": self.id,
            "name": self.name,
            "created_at": self.created_at
        }

    @staticmethod
    def from_dict(data):
        """Creates an Ambulance object from a dictionary."""
        return Ambulance(
            amb_id=data["id"],
            name=data["name"],
            created_at=data.get("created_at")
        )

# --- Data Persistence ---

class DataPersistence:
    """Handles saving and loading data to/from a JSON file."""
    def __init__(self, filename="ems_inventory_data.json"):
        self.filename = filename

    def load_data(self):
        """Loads inventory items, ambulances, and settings from the JSON file."""
        if not os.path.exists(self.filename):
            return [], [], {"expiration_threshold_days": 30, "low_stock_threshold": 5}
        try:
            with open(self.filename, 'r') as f:
                data = json.load(f)
                items = [Item.from_dict(item_data) for item_data in data.get("items", [])]
                ambulances = [Ambulance.from_dict(amb_data) for amb_data in data.get("ambulances", [])]
                settings = data.get("settings", {"expiration_threshold_days": 30, "low_stock_threshold": 5})
                return items, ambulances, settings
        except json.JSONDecodeError as e:
            print(f"Error reading data file: {e}. Starting with empty data.")
            return [], [], {"expiration_threshold_days": 30, "low_stock_threshold": 5}
        except Exception as e:
            print(f"An unexpected error occurred while loading data: {e}. Starting with empty data.")
            return [], [], {"expiration_threshold_days": 30, "low_stock_threshold": 5}

    def save_data(self, items, ambulances, settings):
        """Saves inventory items, ambulances, and settings to the JSON file."""
        data = {
            "items": [item.to_dict() for item in items],
            "ambulances": [amb.to_dict() for amb in ambulances],
            "settings": settings
        }
        try:
            with open(self.filename, 'w') as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            print(f"Error saving data: {e}")

# --- Inventory Manager Logic ---

class InventoryManager:
    """Manages all inventory operations."""
    def __init__(self):
        self.persistence = DataPersistence()
        self.items, self.ambulances, self.settings = self.persistence.load_data()

    def _save_all(self):
        """Internal method to save all current data."""
        self.persistence.save_data(self.items, self.ambulances, self.settings)

    # --- Item Management ---
    def add_item(self, name, quantity, item_type, location, expiration_date=None, ambulance_id=None):
        """Adds a new item to the inventory."""
        new_item = Item(name, quantity, item_type, location, expiration_date, ambulance_id)
        self.items.append(new_item)
        self._save_all()
        print(f"Item '{name}' added successfully.")

    def update_item(self, item_id, new_name=None, new_quantity=None, new_type=None, new_location=None, new_expiration_date=None, new_ambulance_id=None):
        """Updates an existing item's details."""
        for item in self.items:
            if item.id == item_id:
                if new_name is not None:
                    item.name = new_name
                if new_quantity is not None:
                    item.quantity = new_quantity
                if new_type is not None:
                    item.type = new_type
                if new_location is not None:
                    item.location = new_location
                if new_expiration_date is not None:
                    item.expiration_date = new_expiration_date
                if new_ambulance_id is not None:
                    item.ambulance_id = new_ambulance_id
                self._save_all()
                print(f"Item '{item.name}' updated successfully.")
                return True
        print("Item not found.")
        return False

    def delete_item(self, item_id):
        """Deletes an item from the inventory."""
        initial_len = len(self.items)
        self.items = [item for item in self.items if item.id != item_id]
        if len(self.items) < initial_len:
            self._save_all()
            print("Item deleted successfully.")
            return True
        print("Item not found.")
        return False

    def get_items_by_type(self, item_type, ambulance_id=None):
        """Retrieves items filtered by type and optionally by ambulance ID."""
        filtered = [item for item in self.items if item.type == item_type]
        if item_type == 'ambulance' and ambulance_id:
            filtered = [item for item in filtered if item.ambulance_id == ambulance_id]
        return filtered

    # --- Ambulance Management ---
    def add_ambulance(self, name):
        """Adds a new ambulance unit."""
        new_ambulance = Ambulance(name)
        self.ambulances.append(new_ambulance)
        self._save_all()
        print(f"Ambulance '{name}' added successfully.")
        return new_ambulance.id

    def delete_ambulance(self, amb_id):
        """Deletes an ambulance and its associated inventory items."""
        amb_found = False
        for amb in self.ambulances:
            if amb.id == amb_id:
                amb_found = True
                break

        if not amb_found:
            print("Ambulance not found.")
            return False

        # Confirm deletion, as it also deletes associated items
        confirm = input(f"Are you sure you want to delete ambulance '{amb.name}' and all its associated inventory items? (yes/no): ").lower()
        if confirm != 'yes':
            print("Ambulance deletion cancelled.")
            return False

        # Delete associated items first
        items_to_delete_ids = [item.id for item in self.items if item.ambulance_id == amb_id]
        for item_id in items_to_delete_ids:
            self.delete_item(item_id) # This will also save data after each item deletion, could optimize

        # Then delete the ambulance itself
        self.ambulances = [amb for amb in self.ambulances if amb.id != amb_id]
        self._save_all()
        print(f"Ambulance '{amb.name}' and its associated items deleted successfully.")
        return True

    def get_ambulance_by_id(self, amb_id):
        """Retrieves an ambulance by its ID."""
        for amb in self.ambulances:
            if amb.id == amb_id:
                return amb
        return None

    # --- Settings Management ---
    def update_settings(self, expiration_threshold_days=None, low_stock_threshold=None):
        """Updates system settings."""
        if expiration_threshold_days is not None:
            self.settings["expiration_threshold_days"] = expiration_threshold_days
        if low_stock_threshold is not None:
            self.settings["low_stock_threshold"] = low_stock_threshold
        self._save_all()
        print("Settings updated successfully.")

    # --- Alert Generation ---
    def get_alerts(self):
        """Generates a list of low stock and expiring item alerts."""
        alerts = []
        now = datetime.now()
        exp_threshold = self.settings.get("expiration_threshold_days", 30)
        low_stock_threshold = self.settings.get("low_stock_threshold", 5)

        for item in self.items:
            # Expiration Alert
            if item.expiration_date:
                try:
                    exp_date = datetime.strptime(item.expiration_date, "%Y-%m-%d")
                    time_diff = exp_date - now
                    diff_days = time_diff.days

                    if 0 <= diff_days <= exp_threshold:
                        alerts.append(f"EXPIRATION ALERT: '{item.name}' at {item.location} expires in {diff_days} days.")
                    elif diff_days < 0:
                        alerts.append(f"EXPIRED: '{item.name}' at {item.location} expired {abs(diff_days)} days ago.")
                except ValueError:
                    alerts.append(f"WARNING: '{item.name}' has an invalid expiration date format.")

            # Low Stock Alert
            if item.quantity <= low_stock_threshold:
                alerts.append(f"LOW STOCK ALERT: '{item.name}' at {item.location} has {item.quantity} on hand.")
        return alerts

    # --- Reporting ---
    def generate_report(self):
        """Generates a comprehensive inventory report."""
        report = ["--- EMS Inventory Report ---"]
        report.append(f"Generated On: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

        report.append("--- Current Alerts ---")
        alerts = self.get_alerts()
        if alerts:
            for alert in alerts:
                report.append(f"- {alert}")
        else:
            report.append("- No active alerts.")
        report.append("\n")

        report.append("--- Inventory Summary ---")
        report.append(f"Expiration Threshold: {self.settings['expiration_threshold_days']} days")
        report.append(f"Low Stock Threshold: {self.settings['low_stock_threshold']} units\n")

        # Group by type
        item_types = ['station', 'ambulance', 'medication']
        for item_type in item_types:
            report.append(f"--- {item_type.capitalize()} Inventory ---")
            if item_type == 'ambulance':
                if not self.ambulances:
                    report.append("  No ambulances registered.")
                else:
                    for amb in self.ambulances:
                        report.append(f"  Ambulance: {amb.name} (ID: {amb.id})")
                        amb_items = self.get_items_by_type('ambulance', amb.id)
                        if amb_items:
                            for item in amb_items:
                                exp_date_str = item.expiration_date if item.expiration_date else 'N/A'
                                report.append(f"    - {item.name} | Qty: {item.quantity} | Exp: {exp_date_str}")
                        else:
                            report.append("    No items in this ambulance.")
            else:
                items_of_type = self.get_items_by_type(item_type)
                if items_of_type:
                    for item in items_of_type:
                        exp_date_str = item.expiration_date if item.expiration_date else 'N/A'
                        report.append(f"- {item.name} | Qty: {item.quantity} | Exp: {exp_date_str} | Loc: {item.location}")
                else:
                    report.append(f"- No {item_type} items.")
            report.append("\n")

        return "\n".join(report)

# --- CLI Functions ---

def clear_screen():
    """Clears the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def get_valid_input(prompt, type_cast=str, validation_func=None, error_msg="Invalid input. Please try again."):
    """Helper to get validated user input."""
    while True:
        user_input = input(prompt).strip()
        try:
            value = type_cast(user_input)
            if validation_func and not validation_func(value):
                print(error_msg)
                continue
            return value
        except ValueError:
            print(error_msg)

def display_main_menu():
    """Displays the main menu options."""
    print("\n--- EMS Inventory Management System ---")
    print("1. Manage Inventory Items")
    print("2. Manage Ambulances")
    print("3. View Alerts")
    print("4. Settings")
    print("5. Generate Full Report")
    print("6. Exit")
    print("---------------------------------------")

def manage_inventory_items(manager):
    """Sub-menu for managing inventory items."""
    while True:
        clear_screen()
        print("\n--- Manage Inventory Items ---")
        print("1. Add New Item")
        print("2. View All Items")
        print("3. Update Item")
        print("4. Delete Item")
        print("5. Back to Main Menu")
        print("------------------------------")

        choice = get_valid_input("Enter your choice: ", int, lambda x: 1 <= x <= 5, "Please enter a number between 1 and 5.")

        if choice == 1:
            add_item_cli(manager)
        elif choice == 2:
            view_all_items_cli(manager)
            input("\nPress Enter to continue...")
        elif choice == 3:
            update_item_cli(manager)
        elif choice == 4:
            delete_item_cli(manager)
        elif choice == 5:
            break

def add_item_cli(manager):
    """CLI function to add a new item."""
    print("\n--- Add New Item ---")
    name = get_valid_input("Enter item name: ")
    quantity = get_valid_input("Enter quantity: ", int, lambda x: x >= 0, "Quantity must be a non-negative number.")
    
    item_type = get_valid_input("Enter item type (station, ambulance, medication): ", str, 
                                 lambda x: x in ['station', 'ambulance', 'medication'], 
                                 "Invalid type. Must be 'station', 'ambulance', or 'medication'.")
    
    expiration_date = None
    exp_choice = get_valid_input("Does this item have an expiration date? (yes/no): ").lower()
    if exp_choice == 'yes':
        expiration_date = get_valid_input("Enter expiration date (YYYY-MM-DD): ", str, 
                                          lambda x: bool(datetime.strptime(x, "%Y-%m-%d")), 
                                          "Invalid date format. Please use YYYY-MM-DD.")
    
    location = None
    ambulance_id = None
    if item_type == 'ambulance':
        if not manager.ambulances:
            print("No ambulances registered. Please add an ambulance first.")
            input("Press Enter to return to menu...")
            return
        
        print("\n--- Select Ambulance ---")
        for i, amb in enumerate(manager.ambulances):
            print(f"{i+1}. {amb.name} (ID: {amb.id})")
        
        amb_index = get_valid_input("Select an ambulance by number: ", int, 
                                    lambda x: 1 <= x <= len(manager.ambulances), 
                                    "Invalid ambulance selection.") - 1
        selected_ambulance = manager.ambulances[amb_index]
        ambulance_id = selected_ambulance.id
        location = selected_ambulance.name # Location is the ambulance name for ambulance items
    else:
        location = get_valid_input("Enter item location (e.g., 'Shelf A', 'Cabinet 3'): ")

    manager.add_item(name, quantity, item_type, location, expiration_date, ambulance_id)

def view_all_items_cli(manager):
    """CLI function to view all items."""
    print("\n--- All Inventory Items ---")
    if not manager.items:
        print("No items in inventory.")
        return

    # Print header
    print(f"{'ID':<38} | {'Name':<20} | {'Qty':<5} | {'Type':<12} | {'Expiration':<12} | {'Location':<25}")
    print("-" * 120)

    for item in manager.items:
        exp_date_str = item.expiration_date if item.expiration_date else 'N/A'
        print(f"{item.id:<38} | {item.name:<20} | {item.quantity:<5} | {item.type:<12} | {exp_date_str:<12} | {item.location:<25}")

def update_item_cli(manager):
    """CLI function to update an item."""
    print("\n--- Update Item ---")
    item_id = get_valid_input("Enter the ID of the item to update: ")
    
    item_to_update = next((item for item in manager.items if item.id == item_id), None)
    if not item_to_update:
        print("Item not found.")
        input("Press Enter to continue...")
        return

    print(f"Current details for '{item_to_update.name}':")
    print(f"  Quantity: {item_to_update.quantity}")
    print(f"  Type: {item_to_update.type}")
    print(f"  Location: {item_to_update.location}")
    print(f"  Expiration Date: {item_to_update.expiration_date if item_to_update.expiration_date else 'N/A'}")
    if item_to_update.type == 'ambulance' and item_to_update.ambulance_id:
        amb_name = manager.get_ambulance_by_id(item_to_update.ambulance_id).name if manager.get_ambulance_by_id(item_to_update.ambulance_id) else 'Unknown'
        print(f"  Assigned Ambulance: {amb_name}")

    new_name = input(f"Enter new name (current: {item_to_update.name}, leave blank to keep): ").strip() or None
    new_quantity_str = input(f"Enter new quantity (current: {item_to_update.quantity}, leave blank to keep): ").strip()
    new_quantity = int(new_quantity_str) if new_quantity_str.isdigit() and int(new_quantity_str) >= 0 else None
    
    new_type = input(f"Enter new type (current: {item_to_update.type}, station/ambulance/medication, leave blank to keep): ").strip()
    if new_type and new_type not in ['station', 'ambulance', 'medication']:
        print("Invalid type. Keeping current type.")
        new_type = None

    new_expiration_date = None
    exp_choice = input(f"Update expiration date? (yes/no, current: {item_to_update.expiration_date if item_to_update.expiration_date else 'N/A'}): ").lower()
    if exp_choice == 'yes':
        new_expiration_date = get_valid_input("Enter new expiration date (YYYY-MM-DD, leave blank to clear): ").strip() or None
        if new_expiration_date and not bool(datetime.strptime(new_expiration_date, "%Y-%m-%d")):
            print("Invalid date format. Keeping current expiration date.")
            new_expiration_date = item_to_update.expiration_date

    new_location = None
    new_ambulance_id = None
    if new_type == 'ambulance':
        if not manager.ambulances:
            print("No ambulances registered. Cannot assign to ambulance.")
            input("Press Enter to continue...")
            return
        
        print("\n--- Select New Ambulance for Item ---")
        for i, amb in enumerate(manager.ambulances):
            print(f"{i+1}. {amb.name} (ID: {amb.id})")
        
        amb_index_str = input("Select an ambulance by number (leave blank to keep current): ").strip()
        if amb_index_str.isdigit():
            amb_index = int(amb_index_str) - 1
            if 0 <= amb_index < len(manager.ambulances):
                selected_ambulance = manager.ambulances[amb_index]
                new_ambulance_id = selected_ambulance.id
                new_location = selected_ambulance.name
            else:
                print("Invalid ambulance selection. Keeping current assignment.")
        else:
            new_ambulance_id = item_to_update.ambulance_id
            new_location = item_to_update.location # Keep current location if no new ambulance selected
    else: # If not an ambulance item, or changing away from ambulance type
        new_location = input(f"Enter new location (current: {item_to_update.location}, leave blank to keep): ").strip() or None
        new_ambulance_id = None # Clear ambulance association if type changes

    manager.update_item(item_id, new_name, new_quantity, new_type, new_location, new_expiration_date, new_ambulance_id)
    input("Press Enter to continue...")

def delete_item_cli(manager):
    """CLI function to delete an item."""
    print("\n--- Delete Item ---")
    item_id = get_valid_input("Enter the ID of the item to delete: ")
    manager.delete_item(item_id)
    input("Press Enter to continue...")

def manage_ambulances(manager):
    """Sub-menu for managing ambulances."""
    while True:
        clear_screen()
        print("\n--- Manage Ambulances ---")
        print("1. Add New Ambulance")
        print("2. View All Ambulances")
        print("3. Delete Ambulance")
        print("4. View/Modify Ambulance Inventory")
        print("5. Back to Main Menu")
        print("-------------------------")

        choice = get_valid_input("Enter your choice: ", int, lambda x: 1 <= x <= 5, "Please enter a number between 1 and 5.")

        if choice == 1:
            add_ambulance_cli(manager)
        elif choice == 2:
            view_all_ambulances_cli(manager)
            input("\nPress Enter to continue...")
        elif choice == 3:
            delete_ambulance_cli(manager)
        elif choice == 4:
            view_modify_ambulance_inventory_cli(manager)
        elif choice == 5:
            break

def add_ambulance_cli(manager):
    """CLI function to add a new ambulance."""
    print("\n--- Add New Ambulance ---")
    name = get_valid_input("Enter ambulance name (e.g., 'Medic 1', 'Ambulance 2'): ")
    manager.add_ambulance(name)
    input("Press Enter to continue...")

def view_all_ambulances_cli(manager):
    """CLI function to view all ambulances."""
    print("\n--- All Ambulances ---")
    if not manager.ambulances:
        print("No ambulances registered.")
        return
    
    print(f"{'ID':<38} | {'Name':<20}")
    print("-" * 60)
    for amb in manager.ambulances:
        print(f"{amb.id:<38} | {amb.name:<20}")

def delete_ambulance_cli(manager):
    """CLI function to delete an ambulance."""
    print("\n--- Delete Ambulance ---")
    view_all_ambulances_cli(manager)
    if not manager.ambulances:
        input("Press Enter to continue...")
        return
    
    amb_id = get_valid_input("Enter the ID of the ambulance to delete: ")
    manager.delete_ambulance(amb_id)
    input("Press Enter to continue...")

def view_modify_ambulance_inventory_cli(manager):
    """CLI function to view/modify inventory for a selected ambulance."""
    if not manager.ambulances:
        print("\nNo ambulances registered to view inventory for.")
        input("Press Enter to continue...")
        return

    print("\n--- Select Ambulance to Manage Inventory ---")
    view_all_ambulances_cli(manager)
    
    selected_amb_id = get_valid_input("Enter the ID of the ambulance to manage: ")
    selected_ambulance = manager.get_ambulance_by_id(selected_amb_id)

    if not selected_ambulance:
        print("Ambulance not found.")
        input("Press Enter to continue...")
        return

    while True:
        clear_screen()
        print(f"\n--- Inventory for {selected_ambulance.name} ---")
        print("1. View Items in this Ambulance")
        print("2. Add Item to this Ambulance")
        print("3. Update Item in this Ambulance")
        print("4. Delete Item from this Ambulance")
        print("5. Back to Ambulance Management")
        print("---------------------------------------")

        choice = get_valid_input("Enter your choice: ", int, lambda x: 1 <= x <= 5, "Please enter a number between 1 and 5.")

        if choice == 1:
            view_ambulance_items_cli(manager, selected_ambulance.id)
            input("\nPress Enter to continue...")
        elif choice == 2:
            add_item_to_ambulance_cli(manager, selected_ambulance.id, selected_ambulance.name)
        elif choice == 3:
            update_item_in_ambulance_cli(manager, selected_ambulance.id)
        elif choice == 4:
            delete_item_from_ambulance_cli(manager, selected_ambulance.id)
        elif choice == 5:
            break

def view_ambulance_items_cli(manager, ambulance_id):
    """CLI function to view items for a specific ambulance."""
    items = manager.get_items_by_type('ambulance', ambulance_id)
    if not items:
        print("No items found for this ambulance.")
        return
    
    print(f"{'ID':<38} | {'Name':<20} | {'Qty':<5} | {'Expiration':<12}")
    print("-" * 80)
    for item in items:
        exp_date_str = item.expiration_date if item.expiration_date else 'N/A'
        print(f"{item.id:<38} | {item.name:<20} | {item.quantity:<5} | {exp_date_str:<12}")

def add_item_to_ambulance_cli(manager, ambulance_id, ambulance_name):
    """CLI function to add an item directly to a selected ambulance."""
    print(f"\n--- Add Item to {ambulance_name} ---")
    name = get_valid_input("Enter item name: ")
    quantity = get_valid_input("Enter quantity: ", int, lambda x: x >= 0, "Quantity must be a non-negative number.")
    
    expiration_date = None
    exp_choice = get_valid_input("Does this item have an expiration date? (yes/no): ").lower()
    if exp_choice == 'yes':
        expiration_date = get_valid_input("Enter expiration date (YYYY-MM-DD): ", str, 
                                          lambda x: bool(datetime.strptime(x, "%Y-%m-%d")), 
                                          "Invalid date format. Please use YYYY-MM-DD.")
    
    # Location is automatically the ambulance name
    manager.add_item(name, quantity, 'ambulance', ambulance_name, expiration_date, ambulance_id)

def update_item_in_ambulance_cli(manager, ambulance_id):
    """CLI function to update an item within a selected ambulance."""
    print("\n--- Update Item in Ambulance ---")
    view_ambulance_items_cli(manager, ambulance_id)
    items = manager.get_items_by_type('ambulance', ambulance_id)
    if not items:
        input("Press Enter to continue...")
        return

    item_id = get_valid_input("Enter the ID of the item to update in this ambulance: ")
    
    item_to_update = next((item for item in items if item.id == item_id), None)
    if not item_to_update:
        print("Item not found in this ambulance.")
        input("Press Enter to continue...")
        return

    print(f"Current details for '{item_to_update.name}':")
    print(f"  Quantity: {item_to_update.quantity}")
    print(f"  Expiration Date: {item_to_update.expiration_date if item_to_update.expiration_date else 'N/A'}")

    new_name = input(f"Enter new name (current: {item_to_update.name}, leave blank to keep): ").strip() or None
    new_quantity_str = input(f"Enter new quantity (current: {item_to_update.quantity}, leave blank to keep): ").strip()
    new_quantity = int(new_quantity_str) if new_quantity_str.isdigit() and int(new_quantity_str) >= 0 else None
    
    new_expiration_date = None
    exp_choice = input(f"Update expiration date? (yes/no, current: {item_to_update.expiration_date if item_to_update.expiration_date else 'N/A'}): ").lower()
    if exp_choice == 'yes':
        new_expiration_date = get_valid_input("Enter new expiration date (YYYY-MM-DD, leave blank to clear): ").strip() or None
        if new_expiration_date and not bool(datetime.strptime(new_expiration_date, "%Y-%m-%d")):
            print("Invalid date format. Keeping current expiration date.")
            new_expiration_date = item_to_update.expiration_date

    # Type and ambulance_id remain fixed for items within this sub-menu
    manager.update_item(item_id, new_name, new_quantity, item_type='ambulance', new_location=item_to_update.location, new_expiration_date=new_expiration_date, new_ambulance_id=ambulance_id)
    input("Press Enter to continue...")

def delete_item_from_ambulance_cli(manager, ambulance_id):
    """CLI function to delete an item from a selected ambulance."""
    print("\n--- Delete Item from Ambulance ---")
    view_ambulance_items_cli(manager, ambulance_id)
    items = manager.get_items_by_type('ambulance', ambulance_id)
    if not items:
        input("Press Enter to continue...")
        return

    item_id = get_valid_input("Enter the ID of the item to delete from this ambulance: ")
    
    item_to_delete = next((item for item in items if item.id == item_id), None)
    if not item_to_delete:
        print("Item not found in this ambulance.")
        input("Press Enter to continue...")
        return

    manager.delete_item(item_id)
    input("Press Enter to continue...")


def view_alerts_cli(manager):
    """CLI function to view system alerts."""
    print("\n--- System Alerts ---")
    alerts = manager.get_alerts()
    if alerts:
        for alert in alerts:
            print(f"- {alert}")
    else:
        print("No active alerts.")
    input("\nPress Enter to continue...")

def settings_cli(manager):
    """CLI function to adjust settings."""
    while True:
        clear_screen()
        print("\n--- Settings ---")
        print(f"Current Expiration Alert Threshold: {manager.settings.get('expiration_threshold_days')} days")
        print(f"Current Low Stock Threshold: {manager.settings.get('low_stock_threshold')} units")
        print("\n1. Adjust Expiration Alert Threshold")
        print("2. Adjust Low Stock Threshold")
        print("3. Back to Main Menu")
        print("--------------------")

        choice = get_valid_input("Enter your choice: ", int, lambda x: 1 <= x <= 3, "Please enter a number between 1 and 3.")

        if choice == 1:
            new_threshold = get_valid_input("Enter new expiration alert threshold (days): ", int, lambda x: x >= 0, "Threshold must be a non-negative number.")
            manager.update_settings(expiration_threshold_days=new_threshold)
            input("Press Enter to continue...")
        elif choice == 2:
            new_threshold = get_valid_input("Enter new low stock threshold (units): ", int, lambda x: x >= 0, "Threshold must be a non-negative number.")
            manager.update_settings(low_stock_threshold=new_threshold)
            input("Press Enter to continue...")
        elif choice == 3:
            break

def generate_report_cli(manager):
    """CLI function to generate and display a full report."""
    clear_screen()
    report = manager.generate_report()
    print(report)
    
    save_choice = input("\nDo you want to save this report to a text file? (yes/no): ").lower()
    if save_choice == 'yes':
        filename = get_valid_input("Enter filename (e.g., 'ems_report.txt'): ", str, lambda x: x.strip() != "", "Filename cannot be empty.")
        try:
            with open(filename, 'w') as f:
                f.write(report)
            print(f"Report saved to {filename}")
        except Exception as e:
            print(f"Error saving report: {e}")
    
    input("\nPress Enter to continue...")

# --- Main Application Loop ---

def main():
    manager = InventoryManager()
    while True:
        clear_screen()
        display_main_menu()
        choice = get_valid_input("Enter your choice: ", int, lambda x: 1 <= x <= 6, "Please enter a number between 1 and 6.")

        if choice == 1:
            manage_inventory_items(manager)
        elif choice == 2:
            manage_ambulances(manager)
        elif choice == 3:
            view_alerts_cli(manager)
        elif choice == 4:
            settings_cli(manager)
        elif choice == 5:
            generate_report_cli(manager)
        elif choice == 6:
            print("Exiting EMS Inventory Management System. Goodbye!")
            break

if __name__ == "__main__":
    main()
