import pandas as pd
import os
from datetime import datetime
import hashlib
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import configparser
import logging
import re # For regular expressions in autosearch

# --- Configuration Loading ---
config = configparser.ConfigParser()
config_file = 'config.ini'

# Define default configuration settings
default_config = {
    'PATHS': {
        'INVENTORY_FILE': 'inventory.csv',
        'SALES_LOG_FILE': 'sales_log.csv',
        'USERS_FILE': 'users.csv',
        'FILE_HASH_FILE': 'file_hashes.txt',
        'ACTIVITY_LOG_FILE': 'activity_log.csv'
    },
    'DEFAULT_ADMIN': {
        'USERNAME': 'admin',
        'PASSWORD': '$LUTERwing1992' # REMEMBER TO CHANGE THIS IN PRODUCTION!
    },
    'ALERTS': {
        'LOW_STOCK_THRESHOLD': '5' # Default threshold for low stock alert
    }
}

# Check if config file exists
if not os.path.exists(config_file):
    print(f"INFO: '{config_file}' not found. Creating a default configuration file.")
    # Populate the config object with default values
    for section, options in default_config.items():
        if section not in config:
            config[section] = {}
        for key, value in options.items():
            config[section][key] = value

    # Write the default configuration to the file
    with open(config_file, 'w') as f:
        config.write(f)
    print(f"INFO: Default '{config_file}' created. Please review its settings and change the default admin password.")
    messagebox.showinfo("Initial Setup", f"No users file found. A default admin user has been created:\nUsername: {default_config['DEFAULT_ADMIN']['USERNAME']}\nPassword: {default_config['DEFAULT_ADMIN']['PASSWORD']}\nPLEASE CHANGE THIS AFTER FIRST LOGIN!")
else:
    # If config file exists, read it
    config.read(config_file)
    print(f"INFO: '{config_file}' found. Reading existing configuration.")

    # Check for missing sections/keys and add defaults if necessary
    config_updated = False
    for section, options in default_config.items():
        if section not in config:
            config[section] = {}
            logging.warning(f"Section '{section}' missing in '{config_file}'. Adding default.")
            config_updated = True
        for key, value in options.items():
            if key not in config[section]:
                config[section][key] = value
                logging.warning(f"Key '{key}' missing in section '{section}' of '{config_file}'. Adding default value: '{value}'.")
                config_updated = True
    
    # If configuration was updated with missing sections/keys, save it back
    if config_updated:
        with open(config_file, 'w') as f:
            config.write(f)
        print(f"INFO: '{config_file}' updated with missing default settings.")
        messagebox.showinfo("Config Update", f"Your '{config_file}' has been updated with new default settings (e.g., for alerts).")


# --- File Paths from Config ---
INVENTORY_FILE = config['PATHS']['INVENTORY_FILE']
SALES_LOG_FILE = config['PATHS']['SALES_LOG_FILE']
USERS_FILE = config['PATHS']['USERS_FILE']
FILE_HASH_FILE = config['PATHS']['FILE_HASH_FILE']
ACTIVITY_LOG_FILE = config['PATHS']['ACTIVITY_LOG_FILE']

DEFAULT_ADMIN_USERNAME = config['DEFAULT_ADMIN']['USERNAME']
DEFAULT_ADMIN_PASSWORD = config['DEFAULT_ADMIN']['PASSWORD']
LOW_STOCK_THRESHOLD = int(config['ALERTS']['LOW_STOCK_THRESHOLD']) # This line should now work consistently


# --- Logging Setup ---
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[
                        logging.FileHandler("pos_application.log"),
                        logging.StreamHandler()
                    ])

# --- Security and Integrity Functions ---

def calculate_file_hash(filepath):
    """Calculates the SHA256 hash of a given file."""
    hasher = hashlib.sha256()
    try:
        with open(filepath, 'rb') as f:
            while True:
                chunk = f.read(4096)
                if not chunk:
                    break
                hasher.update(chunk)
        return hasher.hexdigest()
    except FileNotFoundError:
        logging.warning(f"File '{filepath}' not found for hash calculation.")
        return None
    except Exception as e:
        logging.error(f"Error calculating hash for '{filepath}': {e}")
        return None

def save_file_hash(filepath, file_hash):
    """Saves the hash of a file to a dedicated hash file."""
    try:
        lines_to_keep = []
        if os.path.exists(FILE_HASH_FILE):
            with open(FILE_HASH_FILE, 'r') as f:
                for line in f:
                    parts = line.strip().split(',')
                    if len(parts) == 3 and parts[0] != filepath:
                        lines_to_keep.append(line)

        with open(FILE_HASH_FILE, 'w') as f:
            f.writelines(lines_to_keep)
            f.write(f"{filepath},{file_hash},{datetime.now().isoformat()}\n")
        logging.info(f"Hash saved for {filepath}")
    except Exception as e:
        logging.error(f"Could not save hash for {filepath}: {e}")
        messagebox.showerror("Security Error", f"ERROR: Could not save integrity hash for {filepath}. Data integrity might be compromised.")

def check_file_integrity(filepath):
    """Checks the integrity of a file against its last saved hash."""
    if not os.path.exists(filepath):
        logging.info(f"File '{filepath}' does not exist for integrity check. Assuming new or will be created.")
        return True # If file doesn't exist, it's 'OK' for initial creation

    current_hash = calculate_file_hash(filepath)
    if current_hash is None:
        logging.warning(f"Failed to calculate current hash for '{filepath}'. Cannot verify integrity.")
        return False

    if not os.path.exists(FILE_HASH_FILE):
        save_file_hash(filepath, current_hash)
        logging.info(f"No hash file found for '{filepath}', saved current hash.")
        return True

    try:
        with open(FILE_HASH_FILE, 'r') as f:
            lines = f.readlines()
            relevant_hashes = [line.strip().split(',') for line in lines if len(line.strip().split(',')) == 3 and line.strip().split(',')[0] == filepath]

            if relevant_hashes:
                saved_hash = relevant_hashes[-1][1]
                if saved_hash == current_hash:
                    logging.info(f"Integrity check OK for '{filepath}'.")
                    return True
                else:
                    msg = (f"CRITICAL: Integrity check FAILED for '{filepath}'. File may have been tampered with!\n"
                           f"Saved hash: {saved_hash}\nCurrent hash: {current_hash}\n"
                           "Please investigate immediately.")
                    logging.critical(msg)
                    messagebox.showerror("Integrity Warning", msg)
                    return False
            else:
                save_file_hash(filepath, current_hash)
                logging.info(f"No previous hash found for '{filepath}', saved current hash.")
                return True
    except Exception as e:
        logging.error(f"Error during integrity check for '{filepath}': {e}")
        messagebox.showerror("Integrity Error", f"ERROR: Could not perform integrity check for '{filepath}': {e}")
        return False

# --- Activity Logging ---
def log_activity(username, action, details=""):
    """Logs user activities to a CSV file."""
    try:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_entry = f'"{timestamp}","{username}","{action}","{details}"\n'
        
        # Check if file exists and is empty to write header
        if not os.path.exists(ACTIVITY_LOG_FILE) or os.stat(ACTIVITY_LOG_FILE).st_size == 0:
            with open(ACTIVITY_LOG_FILE, 'w') as f:
                f.write("Timestamp,Username,Action,Details\n")
        
        with open(ACTIVITY_LOG_FILE, 'a') as f:
            f.write(log_entry)
        logging.info(f"Activity Logged: User '{username}' - {action} - {details}")
    except Exception as e:
        logging.error(f"Failed to log activity: {e}")


# --- User Authentication Functions ---

def hash_password(password):
    """Hashes a password using SHA256."""
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

def verify_password(plain_password, hashed_password):
    """Verifies a plain password against a hashed one."""
    return hash_password(plain_password) == hashed_password

def load_users():
    """Loads user data from CSV or creates a new DataFrame if file doesn't exist."""
    integrity_ok = check_file_integrity(USERS_FILE)
    if not integrity_ok and os.path.exists(USERS_FILE):
        logging.warning(f"User file '{USERS_FILE}' integrity compromised. Proceeding with caution.")
        messagebox.showwarning("User Data Integrity", f"User file '{USERS_FILE}' integrity compromised. Proceeding with caution.")

    required_cols = ['Username', 'Hashed_Password', 'Role']
    if os.path.exists(USERS_FILE):
        try:
            df = pd.read_csv(USERS_FILE)
            for col in required_cols:
                if col not in df.columns:
                    logging.warning(f"Missing column '{col}' in {USERS_FILE}. Attempting to add with default values.")
                    df[col] = ''
            return df
        except pd.errors.EmptyDataError:
            logging.warning(f"{USERS_FILE} is empty. Creating new DataFrame.")
            return pd.DataFrame(columns=required_cols)
        except Exception as e:
            logging.error(f"Could not load {USERS_FILE}. Creating new DataFrame. Error: {e}")
            messagebox.showerror("User Load Error", f"Could not load {USERS_FILE}. Creating new DataFrame. Error: {e}")
            return pd.DataFrame(columns=required_cols)
    else:
        logging.info(f"{USERS_FILE} not found. Creating new user file and default admin.")
        df = pd.DataFrame(columns=required_cols)
        df = pd.concat([df, pd.DataFrame([{
            'Username': DEFAULT_ADMIN_USERNAME,
            'Hashed_Password': hash_password(DEFAULT_ADMIN_PASSWORD),
            'Role': 'Admin'
        }])], ignore_index=True)
        messagebox.showinfo("Initial Setup", f"No users file found. A default admin user has been created:\nUsername: {DEFAULT_ADMIN_USERNAME}\nPassword: {DEFAULT_ADMIN_PASSWORD}\nPLEASE CHANGE THIS AFTER FIRST LOGIN!")
        return df

def save_users(df, user_performing_action="SYSTEM"):
    """Saves the user DataFrame to CSV and updates its hash."""
    try:
        df.to_csv(USERS_FILE, index=False)
        current_hash = calculate_file_hash(USERS_FILE)
        if current_hash:
            save_file_hash(USERS_FILE, current_hash)
        log_activity(user_performing_action, "User Data Saved", f"User data saved to {USERS_FILE}")
        return True, f"Users saved to {USERS_FILE}"
    except Exception as e:
        logging.error(f"Error saving users: {e}")
        return False, f"Error saving users: {e}"

def add_user_backend(df_users, username, password, role, user_performing_action="SYSTEM"):
    """Adds a new user to the user DataFrame (backend logic)."""
    if not username or not password:
        return df_users, False, "Username and password cannot be empty."
    if username in df_users['Username'].values:
        return df_users, False, "Username already exists."

    hashed_password = hash_password(password)
    new_user = pd.DataFrame([{
        'Username': username,
        'Hashed_Password': hashed_password,
        'Role': role
    }])
    df_users = pd.concat([df_users, new_user], ignore_index=True)
    log_activity(user_performing_action, "User Added", f"User '{username}' with role '{role}' added.")
    return df_users, True, f"User '{username}' registered successfully with role '{role}'."

def update_user_backend(df_users, username_to_update, new_role=None, new_password=None, user_performing_action="SYSTEM"):
    """Updates an existing user's role or password."""
    if username_to_update not in df_users['Username'].values:
        return df_users, False, f"User '{username_to_update}' not found."

    idx = df_users[df_users['Username'] == username_to_update].index[0]
    details_changed = []

    if new_role and new_role != df_users.loc[idx, 'Role']:
        df_users.loc[idx, 'Role'] = new_role
        details_changed.append(f"role changed to '{new_role}'")

    if new_password:
        df_users.loc[idx, 'Hashed_Password'] = hash_password(new_password)
        details_changed.append("password changed")

    if not details_changed:
        return df_users, False, "No changes specified for user."

    log_activity(user_performing_action, "User Updated", f"User '{username_to_update}' {', '.join(details_changed)}.")
    return df_users, True, f"User '{username_to_update}' updated successfully: {', '.join(details_changed)}."

def delete_user_backend(df_users, username_to_delete, user_performing_action="SYSTEM"):
    """Deletes a user from the user DataFrame."""
    if username_to_delete not in df_users['Username'].values:
        return df_users, False, f"User '{username_to_delete}' not found."
    if username_to_delete == DEFAULT_ADMIN_USERNAME:
        return df_users, False, "Default admin user cannot be deleted."

    df_users = df_users[df_users['Username'] != username_to_delete].reset_index(drop=True)
    log_activity(user_performing_action, "User Deleted", f"User '{username_to_delete}' deleted.")
    return df_users, True, f"User '{username_to_delete}' deleted successfully."


def authenticate_user_backend(df_users, username, password):
    """Authenticates a user (backend logic)."""
    user_row = df_users[df_users['Username'] == username]
    if user_row.empty:
        log_activity(username, "Login Failed", "Invalid username.")
        return None, False, "Invalid username or password."

    hashed_password_in_db = user_row['Hashed_Password'].iloc[0]
    if verify_password(password, hashed_password_in_db):
        log_activity(username, "Login Success")
        return user_row.iloc[0], True, f"Welcome, {username}!"
    else:
        log_activity(username, "Login Failed", "Incorrect password.")
        return None, False, "Invalid username or password."


# --- POS System Backend Functions (Modified for GUI interaction) ---

def load_inventory():
    """Loads inventory from CSV or creates a new DataFrame if file doesn't exist."""
    integrity_ok = check_file_integrity(INVENTORY_FILE)
    if not integrity_ok and os.path.exists(INVENTORY_FILE):
        logging.warning(f"Inventory file '{INVENTORY_FILE}' integrity compromised. Proceeding with caution.")
        messagebox.showwarning("Inventory Data Integrity", f"Inventory file '{INVENTORY_FILE}' integrity compromised. Proceeding with caution.")

    required_cols = ['SKU', 'Name', 'Quantity', 'Price', 'Reorder_Level', 'Location', 'Last_Updated']
    if os.path.exists(INVENTORY_FILE):
        try:
            df = pd.read_csv(INVENTORY_FILE)
            for col in required_cols:
                if col not in df.columns:
                    logging.warning(f"Missing column '{col}' in {INVENTORY_FILE}. Attempting to add with default values.")
                    if col == 'Quantity' or col == 'Reorder_Level':
                        df[col] = 0
                    elif col == 'Price':
                        df[col] = 0.0
                    else:
                        df[col] = ''
            df['Quantity'] = pd.to_numeric(df['Quantity'], errors='coerce').fillna(0).astype(int)
            df['Price'] = pd.to_numeric(df['Price'], errors='coerce').fillna(0.0)
            df['Reorder_Level'] = pd.to_numeric(df['Reorder_Level'], errors='coerce').fillna(0).astype(int)
            return df
        except pd.errors.EmptyDataError:
            logging.warning(f"{INVENTORY_FILE} is empty. Creating new DataFrame.")
            return pd.DataFrame(columns=required_cols)
        except Exception as e:
            logging.error(f"Could not load {INVENTORY_FILE}. Creating new DataFrame. Error: {e}")
            messagebox.showerror("Load Error", f"Could not load {INVENTORY_FILE}. Creating new DataFrame. Error: {e}")
            return pd.DataFrame(columns=required_cols)
    else:
        logging.info(f"{INVENTORY_FILE} not found. Creating new inventory file.")
        return pd.DataFrame(columns=required_cols)

def save_inventory(df, user_performing_action="SYSTEM"):
    """Saves the current inventory DataFrame to CSV and updates its hash."""
    try:
        df.to_csv(INVENTORY_FILE, index=False)
        current_hash = calculate_file_hash(INVENTORY_FILE)
        if current_hash:
            save_file_hash(INVENTORY_FILE, current_hash)
        log_activity(user_performing_action, "Inventory Saved", f"Inventory data saved to {INVENTORY_FILE}")
        return True, f"Inventory saved to {INVENTORY_FILE}"
    except Exception as e:
        logging.error(f"Error saving inventory: {e}")
        return False, f"Error saving inventory: {e}"

def load_sales_log():
    """Loads sales log from CSV or creates a new DataFrame if file doesn't exist."""
    integrity_ok = check_file_integrity(SALES_LOG_FILE)
    if not integrity_ok and os.path.exists(SALES_LOG_FILE):
        logging.warning(f"Sales log file '{SALES_LOG_FILE}' integrity compromised. Proceeding with caution.")
        messagebox.showwarning("Sales Log Integrity", f"Sales log file '{SALES_LOG_FILE}' integrity compromised. Proceeding with caution.")

    # Added 'TransactionDate', 'Amount', 'CustomerID'
    required_cols = ['Sale_ID', 'SKU', 'Item_Name', 'Quantity_Sold', 'Price_at_Sale', 'Amount', 'TransactionDate', 'CustomerID', 'Cashier']
    if os.path.exists(SALES_LOG_FILE):
        try:
            df_sales = pd.read_csv(SALES_LOG_FILE)
            for col in required_cols:
                if col not in df_sales.columns:
                    logging.warning(f"Missing column '{col}' in {SALES_LOG_FILE}. Attempting to add with default values.")
                    if col in ['Quantity_Sold', 'Sale_ID']:
                        df_sales[col] = 0
                    elif col in ['Price_at_Sale', 'Amount']:
                        df_sales[col] = 0.0
                    else:
                        df_sales[col] = '' # For 'TransactionDate', 'CustomerID', 'Cashier'
            df_sales['Quantity_Sold'] = pd.to_numeric(df_sales['Quantity_Sold'], errors='coerce').fillna(0).astype(int)
            df_sales['Price_at_Sale'] = pd.to_numeric(df_sales['Price_at_Sale'], errors='coerce').fillna(0.0)
            df_sales['Amount'] = pd.to_numeric(df_sales['Amount'], errors='coerce').fillna(0.0)
            return df_sales
        except pd.errors.EmptyDataError:
            logging.warning(f"{SALES_LOG_FILE} is empty. Creating new DataFrame.")
            return pd.DataFrame(columns=required_cols)
        except Exception as e:
            logging.error(f"Could not load {SALES_LOG_FILE}. Creating new DataFrame. Error: {e}")
            messagebox.showerror("Load Error", f"Could not load {SALES_LOG_FILE}. Creating new DataFrame. Error: {e}")
            return pd.DataFrame(columns=required_cols)
    else:
        logging.info(f"{SALES_LOG_FILE} not found. Creating new sales log file.")
        return pd.DataFrame(columns=required_cols)

def save_sales_log(df_sales, user_performing_action="SYSTEM"):
    """Saves the sales log DataFrame to CSV and updates its hash."""
    try:
        df_sales.to_csv(SALES_LOG_FILE, index=False)
        current_hash = calculate_file_hash(SALES_LOG_FILE)
        if current_hash:
            save_file_hash(SALES_LOG_FILE, current_hash)
        log_activity(user_performing_action, "Sales Log Saved", f"Sales log data saved to {SALES_LOG_FILE}")
        return True, f"Sales log saved to {SALES_LOG_FILE}"
    except Exception as e:
        logging.error(f"Error saving sales log: {e}")
        return False, f"Error saving sales log: {e}"

def add_item_backend(df, sku, name, quantity, price, reorder_level, location, user_performing_action="SYSTEM"):
    """Adds a new item to the inventory (backend logic)."""
    if not sku:
        return df, False, "SKU cannot be empty."
    if sku in df['SKU'].values:
        return df, False, "Error: SKU already exists. Use 'Update Item Quantity' or 'Update Item Details' to modify existing items."
    if not name:
        return df, False, "Item Name cannot be empty."
    if quantity < 0:
        return df, False, "Quantity cannot be negative."
    if price < 0:
        return df, False, "Price cannot be negative."
    if reorder_level < 0:
        return df, False, "Reorder Level cannot be negative."

    last_updated = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    new_item = pd.DataFrame([{
        'SKU': sku,
        'Name': name,
        'Quantity': quantity,
        'Price': price,
        'Reorder_Level': reorder_level,
        'Location': location,
        'Last_Updated': last_updated
    }])

    df = pd.concat([df, new_item], ignore_index=True)
    log_activity(user_performing_action, "Item Added", f"SKU: {sku}, Name: {name}, Qty: {quantity}")
    return df, True, f"Item '{name}' (SKU: {sku}) added successfully."

def update_item_quantity_backend(df, sku, change, user_performing_action="SYSTEM"):
    """Updates the quantity of an existing item (backend logic)."""
    if not sku:
        return df, False, "SKU cannot be empty."
    if sku not in df['SKU'].values:
        return df, False, f"Error: SKU '{sku}' not found."

    idx = df[df['SKU'] == sku].index[0]
    current_quantity = df.loc[idx, 'Quantity']
    new_quantity = current_quantity + change
    if new_quantity < 0:
        return df, False, f"Warning: Cannot reduce quantity below zero. Current: {current_quantity}, Attempted change: {change}"

    df.loc[idx, 'Quantity'] = new_quantity
    df.loc[idx, 'Last_Updated'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_activity(user_performing_action, "Item Quantity Updated", f"SKU: {sku}, Name: {df.loc[idx, 'Name']}, Change: {change}, New Qty: {new_quantity}")
    return df, True, f"Quantity for '{df.loc[idx, 'Name']}' updated to {new_quantity}."

def update_item_details_backend(df, sku, new_name, new_price, new_reorder_level, new_location, user_performing_action="SYSTEM"):
    """Updates non-quantity details of an existing item (backend logic)."""
    if not sku:
        return df, False, "SKU cannot be empty."
    if sku not in df['SKU'].values:
        return df, False, f"Error: SKU '{sku}' not found."

    idx = df[df['SKU'] == sku].index[0]
    original_name = df.loc[idx, 'Name']
    original_price = df.loc[idx, 'Price']
    original_reorder = df.loc[idx, 'Reorder_Level']
    original_location = df.loc[idx, 'Location']
    changes_made = []

    if new_name is not None and new_name != "" and new_name != original_name:
        df.loc[idx, 'Name'] = new_name
        changes_made.append(f"Name from '{original_name}' to '{new_name}'")
    if new_price is not None and new_price >= 0 and new_price != original_price:
        df.loc[idx, 'Price'] = new_price
        changes_made.append(f"Price from {original_price:.2f} to {new_price:.2f}")
    if new_reorder_level is not None and new_reorder_level >= 0 and new_reorder_level != original_reorder:
        df.loc[idx, 'Reorder_Level'] = new_reorder_level
        changes_made.append(f"Reorder Level from {original_reorder} to {new_reorder_level}")
    if new_location is not None and new_location != "" and new_location != original_location:
        df.loc[idx, 'Location'] = new_location
        changes_made.append(f"Location from '{original_location}' to '{new_location}'")

    if not changes_made:
        return df, False, "No changes detected or invalid values provided."

    df.loc[idx, 'Last_Updated'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_activity(user_performing_action, "Item Details Updated", f"SKU: {sku}, Details: {'; '.join(changes_made)}")
    return df, True, f"Details for '{df.loc[idx, 'Name']}' (SKU: {sku}) updated successfully. ({'; '.join(changes_made)})"


def delete_item_backend(df, sku, user_performing_action="SYSTEM"):
    """Deletes an item from the inventory (backend logic)."""
    if not sku:
        return df, False, "SKU cannot be empty."
    if sku not in df['SKU'].values:
        return df, False, f"Error: SKU '{sku}' not found."

    item_name = df[df['SKU'] == sku]['Name'].iloc[0]
    df = df[df['SKU'] != sku].reset_index(drop=True)
    log_activity(user_performing_action, "Item Deleted", f"SKU: {sku}, Name: {item_name}")
    return df, True, f"Item '{item_name}' (SKU: {sku}) deleted successfully."

# Modified record_sale_backend to include customer_id and transaction_date
def record_sale_backend(df_inventory, df_sales_log, sale_items_list, cashier_username, low_stock_threshold, customer_id, transaction_date):
    """Records a complete sale from a list of items, updates inventory, and logs the transaction (backend logic).
    sale_items_list is a list of dictionaries, e.g., [{'sku': 'A101', 'name': 'Milk', 'qty': 2, 'price': 50.0}, ...]
    Includes customer_id and transaction_date.
    """
    if not sale_items_list:
        return df_inventory, df_sales_log, False, "No items in the sale to record.", 0.0, []

    successful_items = []
    failed_items_messages = []
    inventory_df_copy = df_inventory.copy()
    low_stock_alerts = [] # To store messages for low stock items

    for item in sale_items_list:
        sku = item['sku']
        quantity_sold = item['qty']
        item_name = item['name']
        item_price = item['price']

        idx = inventory_df_copy[inventory_df_copy['SKU'] == sku].index
        if idx.empty:
            failed_items_messages.append(f"Item '{item_name}' (SKU: {sku}) not found in inventory. Sale aborted for this item.")
            continue
        idx = idx[0]

        current_quantity = inventory_df_copy.loc[idx, 'Quantity']
        reorder_level = inventory_df_copy.loc[idx, 'Reorder_Level']

        if quantity_sold <= 0:
            failed_items_messages.append(f"Quantity sold for '{item_name}' (SKU: {sku}) must be positive. Sale aborted for this item.")
            continue
        if quantity_sold > current_quantity:
            failed_items_messages.append(f"Not enough stock for '{item_name}' (SKU: {sku}). Available: {current_quantity}, Attempted to sell: {quantity_sold}. Sale aborted for this item.")
            continue
        if current_quantity == 0:
            failed_items_messages.append(f"'{item_name}' (SKU: {sku}) is OUT OF STOCK! Cannot complete sale for this item.")
            continue

        inventory_df_copy.loc[idx, 'Quantity'] -= quantity_sold
        inventory_df_copy.loc[idx, 'Last_Updated'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        successful_items.append(item)

        # Check for low stock after sale
        new_quantity = inventory_df_copy.loc[idx, 'Quantity']
        if new_quantity <= reorder_level or new_quantity <= low_stock_threshold:
            alert_msg = f"EMERGENCY ALERT: '{item_name}' (SKU: {sku}) stock is now {new_quantity}. Reorder Level: {reorder_level}. Please reorder immediately!"
            low_stock_alerts.append(alert_msg)


    if not successful_items:
        return df_inventory, df_sales_log, False, "All items failed to be processed for sale:\n" + "\n".join(failed_items_messages), 0.0, low_stock_alerts

    last_sale_id = df_sales_log['Sale_ID'].max() if not df_sales_log.empty else 0
    sale_id = last_sale_id + 1
    
    # Use the provided transaction_date, or default to now if not provided
    transaction_date_str = transaction_date.strftime('%Y-%m-%d %H:%M:%S') if isinstance(transaction_date, datetime) else datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    new_sale_records = []
    total_transaction_amount = 0.0

    for item in successful_items:
        total_item_amount = item['qty'] * item['price']
        total_transaction_amount += total_item_amount
        new_sale_records.append({
            'Sale_ID': sale_id,
            'SKU': item['sku'],
            'Item_Name': item['name'],
            'Quantity_Sold': item['qty'],
            'Price_at_Sale': item['price'],
            'Amount': total_item_amount,  # Corresponds to Amount for this line item
            'TransactionDate': transaction_date_str, # Use the provided/default date
            'CustomerID': customer_id, # Use the provided CustomerID
            'Cashier': cashier_username
        })

    df_sales_log = pd.concat([df_sales_log, pd.DataFrame(new_sale_records)], ignore_index=True)

    df_inventory = inventory_df_copy.copy() # Update the main inventory DataFrame

    success_message = (f"Sale ID {sale_id} for Customer '{customer_id}' recorded successfully "
                       f"on {transaction_date_str} with total ₱{total_transaction_amount:,.2f}.")
    if failed_items_messages:
        success_message += "\n\nNOTE: Some items could not be processed:\n" + "\n".join(failed_items_messages)

    log_activity(cashier_username, "Sale Finalized", f"Sale ID: {sale_id}, Customer: {customer_id}, Date: {transaction_date_str}, Total: {total_transaction_amount:.2f}, Items: {len(successful_items)}")
    return df_inventory, df_sales_log, True, success_message, total_transaction_amount, low_stock_alerts

def get_low_stock_items(df):
    """Returns DataFrame of low stock items."""
    df_check = df.copy()
    df_check['Quantity'] = pd.to_numeric(df_check['Quantity'], errors='coerce').fillna(0)
    df_check['Reorder_Level'] = pd.to_numeric(df_check['Reorder_Level'], errors='coerce').fillna(0)
    # Check if quantity is <= reorder level OR quantity is <= a general low stock threshold
    return df_check[(df_check['Quantity'] <= df_check['Reorder_Level']) | (df_check['Quantity'] <= LOW_STOCK_THRESHOLD)]

def get_inventory_value(df):
    """Calculates and returns the total monetary value of all items in stock."""
    if df.empty:
        return 0.0, "Inventory is empty, total value is ₱0.00."

    df_numeric = df.copy()
    df_numeric['Quantity'] = pd.to_numeric(df_numeric['Quantity'], errors='coerce')
    df_numeric['Price'] = pd.to_numeric(df_numeric['Price'], errors='coerce')
    df_numeric = df_numeric.dropna(subset=['Quantity', 'Price'])

    if df_numeric.empty:
        return 0.0, "No valid quantity or price data to calculate inventory value."

    total_value = (df_numeric['Quantity'] * df_numeric['Price']).sum()
    return total_value, f"Total value of all items in stock: ₱{total_value:,.2f}"

# --- Hardware Integration Placeholder ---
def open_cash_drawer():
    """
    Placeholder function to simulate opening a POS cash drawer.
    """
    messagebox.showinfo("Cash Drawer", "Simulating Cash Drawer Open. (Real hardware command would go here!)")


# --- Main POS Application Class ---
class POSApp:
    def __init__(self, root, on_logout_callback, user_data):
        self.root = root
        self.root.title("Mariah Store POS")
        self.root.geometry("1200x750")
        self.on_logout_callback = on_logout_callback
        self.current_user = user_data # Store logged-in user's data (e.g., {'Username': 'admin', 'Role': 'Admin'})
        logging.info(f"POS App started for user: {self.current_user['Username']} ({self.current_user['Role']})")


        self.inventory_df = load_inventory()
        self.sales_df = load_sales_log()
        self.users_df = load_users() # Keep a reference to users_df for user management

        # Tkinter variables for input fields
        self.sku_var = tk.StringVar()
        self.name_var = tk.StringVar()
        self.quantity_var = tk.IntVar(value=0)
        self.price_var = tk.DoubleVar(value=0.0)
        self.reorder_level_var = tk.IntVar(value=0)
        self.location_var = tk.StringVar()

        self.sale_item_identifier_var = tk.StringVar()
        self.sale_quantity_var = tk.IntVar(value=1)
        self.total_due_var = tk.DoubleVar(value=0.0)
        self.customer_id_var = tk.StringVar() # For new CustomerID
        self.transaction_date_var = tk.StringVar(value=datetime.now().strftime('%Y-%m-%d')) # For new TransactionDate

        self.inventory_search_var = tk.StringVar()

        self.current_sale_items = []

        self.setup_gui()
        self.update_all_treeviews()
        self.update_dashboard()

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def setup_gui(self):
        # Apply a theme
        style = ttk.Style()
        style.theme_use('clam') # or 'alt', 'default', 'classic', 'vista', 'xpnative'
        style.configure('TFrame', background='#e0e0e0')
        style.configure('TLabelFrame', background='#e0e0e0')
        style.configure('TLabel', background='#e0e0e0', font=('Arial', 10))
        style.configure('TButton', font=('Arial', 10, 'bold'), padding=6)
        style.map('TButton', background=[('active', '#cccccc')])
        style.configure('Accent.TButton', background='#4CAF50', foreground='white')
        style.map('Accent.TButton', background=[('active', '#4CAF50')])
        style.configure('Treeview.Heading', font=('Arial', 10, 'bold'))
        style.configure('Treeview', font=('Arial', 9))
        
        # Style for Autocomplete Listbox
        style.configure('AutoComplete.TFrame', background='white', borderwidth=1, relief='solid')


        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(expand=True, fill="both", padx=10, pady=10)

        self.inventory_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.inventory_tab, text="Inventory Management")
        self.create_inventory_tab(self.inventory_tab)

        self.sales_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.sales_tab, text="Record Sales")
        self.create_sales_tab(self.sales_tab)

        self.reports_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.reports_tab, text="Reports & Monitoring")
        self.create_reports_tab(self.reports_tab)

        # Admin Features: User Management and Activity Log
        if self.current_user['Role'] == 'Admin':
            self.user_management_tab = ttk.Frame(self.notebook)
            self.notebook.add(self.user_management_tab, text="User Management")
            self.create_user_management_tab(self.user_management_tab)

            self.activity_log_tab = ttk.Frame(self.notebook)
            self.notebook.add(self.activity_log_tab, text="Activity Log")
            self.create_activity_log_tab(self.activity_log_tab)
        
        # User Change Password
        self.user_settings_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.user_settings_tab, text="My Account")
        self.create_user_settings_tab(self.user_settings_tab)


        logout_frame = ttk.Frame(self.root)
        logout_frame.pack(pady=5, fill="x")
        ttk.Button(logout_frame, text="Logout", command=self.logout).pack(side="right", padx=10)
        ttk.Label(logout_frame, text=f"Logged in as: {self.current_user['Username']} ({self.current_user['Role']})").pack(side="left", padx=10)

    def create_inventory_tab(self, parent_frame):
        # Input Frame
        input_frame = ttk.LabelFrame(parent_frame, text="Item Details")
        input_frame.pack(padx=10, pady=10, fill="x")

        labels = ["SKU:", "Name:", "Quantity:", "Price:", "Reorder Level:", "Location:"]
        vars = [self.sku_var, self.name_var, self.quantity_var, self.price_var, self.reorder_level_var, self.location_var]
        entries = []
        for i, (label_text, var) in enumerate(zip(labels, vars)):
            ttk.Label(input_frame, text=label_text).grid(row=i, column=0, padx=5, pady=2, sticky="w")
            if label_text in ["Quantity:", "Reorder Level:"]:
                entry = ttk.Entry(input_frame, textvariable=var, width=30, validate="key", validatecommand=(self.root.register(self.validate_integer_input), '%P'))
            elif label_text == "Price:":
                 entry = ttk.Entry(input_frame, textvariable=var, width=30, validate="key", validatecommand=(self.root.register(self.validate_float_input), '%P'))
            else:
                entry = ttk.Entry(input_frame, textvariable=var, width=30)
            entry.grid(row=i, column=1, padx=5, pady=2, sticky="ew")
            entries.append(entry)
        
        # Make entries change color on invalid input
        self.bind_validation_feedback(entries[2], self.quantity_var, self.validate_integer_input) # Quantity
        self.bind_validation_feedback(entries[3], self.price_var, self.validate_float_input) # Price
        self.bind_validation_feedback(entries[4], self.reorder_level_var, self.validate_integer_input) # Reorder Level


        # Buttons Frame
        button_frame = ttk.Frame(parent_frame)
        button_frame.pack(padx=10, pady=5, fill="x")

        # RBAC: Only Admin can Add, Update Details, Delete
        is_admin = (self.current_user['Role'] == 'Admin')

        ttk.Button(button_frame, text="Add Item", command=self.add_item_gui, state=tk.NORMAL if is_admin else tk.DISABLED).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Update Quantity", command=self.update_quantity_gui).pack(side="left", padx=5) # Cashiers can update quantity
        ttk.Button(button_frame, text="Update Details", command=self.update_details_gui, state=tk.NORMAL if is_admin else tk.DISABLED).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Delete Item", command=self.delete_item_gui, state=tk.NORMAL if is_admin else tk.DISABLED).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Clear Fields", command=self.clear_item_fields).pack(side="left", padx=5)

        # Inventory Search Frame (New)
        search_frame = ttk.LabelFrame(parent_frame, text="Search Inventory")
        search_frame.pack(padx=10, pady=10, fill="x")

        ttk.Label(search_frame, text="Search by SKU or Name:").grid(row=0, column=0, padx=5, pady=2, sticky="w")
        ttk.Entry(search_frame, textvariable=self.inventory_search_var, width=40).grid(row=0, column=1, padx=5, pady=2, sticky="ew")
        ttk.Button(search_frame, text="Search", command=self.search_inventory_gui).grid(row=0, column=2, padx=5, pady=2)
        ttk.Button(search_frame, text="Show All", command=lambda: self.update_treeview(self.inventory_tree, self.inventory_df)).grid(row=0, column=3, padx=5, pady=2)

        # Inventory Display Frame
        display_frame = ttk.LabelFrame(parent_frame, text="Current Inventory")
        display_frame.pack(padx=10, pady=10, expand=True, fill="both")

        self.inventory_tree = ttk.Treeview(display_frame, columns=['SKU', 'Name', 'Quantity', 'Price', 'Reorder_Level', 'Location', 'Last_Updated'], show='headings')
        self.inventory_tree.pack(side="left", fill="both", expand=True)

        for col in ['SKU', 'Name', 'Quantity', 'Price', 'Reorder_Level', 'Location', 'Last_Updated']:
            self.inventory_tree.heading(col, text=col, anchor="w")
            self.inventory_tree.column(col, width=100)

        self.inventory_tree.column('SKU', width=80)
        self.inventory_tree.column('Name', width=150)
        self.inventory_tree.column('Quantity', width=70, anchor="center")
        self.inventory_tree.column('Price', width=70, anchor="e")
        self.inventory_tree.column('Reorder_Level', width=80, anchor="center")
        self.inventory_tree.column('Location', width=100)
        self.inventory_tree.column('Last_Updated', width=150)

        yscroll = ttk.Scrollbar(display_frame, orient="vertical", command=self.inventory_tree.yview)
        yscroll.pack(side="right", fill="y")
        self.inventory_tree.configure(yscrollcommand=yscroll.set)

        self.inventory_tree.bind("<<TreeviewSelect>>", self.load_selected_item_into_fields)

    def create_sales_tab(self, parent_frame):
        sales_pane = ttk.PanedWindow(parent_frame, orient=tk.VERTICAL)
        sales_pane.pack(expand=True, fill="both", padx=10, pady=10)

        current_sale_frame = ttk.LabelFrame(sales_pane, text="Current Transaction")
        current_sale_frame.pack_propagate(False) # Prevent frame from shrinking to contents
        sales_pane.add(current_sale_frame, weight=2)

        # Customer and Date input
        customer_date_frame = ttk.Frame(current_sale_frame)
        customer_date_frame.pack(padx=5, pady=5, fill="x")

        ttk.Label(customer_date_frame, text="Customer ID:").pack(side="left", padx=5)
        ttk.Entry(customer_date_frame, textvariable=self.customer_id_var, width=15).pack(side="left", padx=5)
        self.customer_id_var.set("WALK_IN") # Default customer ID

        ttk.Label(customer_date_frame, text="Date (YYYY-MM-DD):").pack(side="left", padx=5)
        ttk.Entry(customer_date_frame, textvariable=self.transaction_date_var, width=15).pack(side="left", padx=5)
        self.transaction_date_var.set(datetime.now().strftime('%Y-%m-%d')) # Default to current date

        input_row_frame = ttk.Frame(current_sale_frame)
        input_row_frame.pack(padx=5, pady=5, fill="x")

        ttk.Label(input_row_frame, text="SKU / Item Name:").pack(side="left", padx=5)
        self.sale_item_entry = ttk.Entry(input_row_frame, textvariable=self.sale_item_identifier_var, width=30)
        self.sale_item_entry.pack(side="left", padx=5, expand=True, fill="x")
        self.sale_item_entry.bind("<Return>", self.process_barcode_or_enter)
        self.sale_item_entry.bind("<KeyRelease>", self.autocomplete_items) # AUTOSEARCH ADDED HERE
        self.sale_item_entry.focus_set()

        # Autocomplete Listbox Frame
        self.autocomplete_frame = ttk.Frame(current_sale_frame, style='AutoComplete.TFrame')
        # Initially hidden, position it dynamically below the entry
        self.autocomplete_listbox = tk.Listbox(self.autocomplete_frame, height=5, exportselection=False,
                                                font=('Arial', 9))
        self.autocomplete_listbox.pack(side="left", fill="both", expand=True)
        self.autocomplete_listbox.bind("<<ListboxSelect>>", self.select_autocomplete_item)
        self.autocomplete_listbox.bind("<Return>", lambda e: self.process_barcode_or_enter())
        self.autocomplete_listbox.bind("<Escape>", lambda e: self.hide_autocomplete())
        # Make the parent frame absorb clicks outside to hide listbox
        current_sale_frame.bind("<Button-1>", lambda e: self.hide_autocomplete())

        ttk.Label(input_row_frame, text="Qty:").pack(side="left", padx=5)
        ttk.Entry(input_row_frame, textvariable=self.sale_quantity_var, width=5, validate="key", validatecommand=(self.root.register(self.validate_positive_integer_input), '%P')).pack(side="left", padx=5)

        ttk.Button(input_row_frame, text="Add to Cart (Manual)", command=self.add_item_to_cart_gui).pack(side="left", padx=10)


        cart_display_frame = ttk.Frame(current_sale_frame)
        cart_display_frame.pack(padx=5, pady=5, expand=True, fill="both")

        self.shopping_cart_tree = ttk.Treeview(cart_display_frame, columns=['SKU', 'Name', 'Qty', 'Price', 'Subtotal'], show='headings')
        self.shopping_cart_tree.pack(side="left", fill="both", expand=True)

        for col in ['SKU', 'Name', 'Qty', 'Price', 'Subtotal']:
            self.shopping_cart_tree.heading(col, text=col, anchor="w")
            self.shopping_cart_tree.column(col, width=100)
        self.shopping_cart_tree.column('SKU', width=80)
        self.shopping_cart_tree.column('Name', width=150)
        self.shopping_cart_tree.column('Qty', width=50, anchor="center")
        self.shopping_cart_tree.column('Price', width=70, anchor="e")
        self.shopping_cart_tree.column('Subtotal', width=80, anchor="e")

        yscroll_cart = ttk.Scrollbar(cart_display_frame, orient="vertical", command=self.shopping_cart_tree.yview)
        yscroll_cart.pack(side="right", fill="y")
        self.shopping_cart_tree.configure(yscrollcommand=yscroll_cart.set)

        cart_actions_frame = ttk.Frame(current_sale_frame)
        cart_actions_frame.pack(padx=5, pady=10, fill="x")

        ttk.Button(cart_actions_frame, text="Remove Selected Item", command=self.remove_item_from_cart_gui).pack(side="left", padx=5)
        ttk.Button(cart_actions_frame, text="Clear Cart", command=self.clear_cart).pack(side="left", padx=5)
        ttk.Button(cart_actions_frame, text="Finalize Sale", command=self.finalize_sale_gui, style="Accent.TButton").pack(side="right", padx=5) # Ensure this button is correctly packed
        self.total_due_label = ttk.Label(cart_actions_frame, text="Total: ₱0.00", font=("Arial", 16, "bold"), textvariable=self.total_due_var)
        self.total_due_label.pack(side="right", padx=20)


        sales_display_frame = ttk.LabelFrame(sales_pane, text="Sales History")
        sales_pane.add(sales_display_frame, weight=1)

        # Updated sales_tree columns to reflect new sales log structure
        self.sales_tree = ttk.Treeview(sales_display_frame, columns=['Sale_ID', 'SKU', 'Item_Name', 'Quantity_Sold', 'Price_at_Sale', 'Amount', 'TransactionDate', 'CustomerID', 'Cashier'], show='headings')
        self.sales_tree.pack(side="left", fill="both", expand=True)

        # Updated column headings for sales_tree
        for col in ['Sale_ID', 'SKU', 'Item_Name', 'Quantity_Sold', 'Price_at_Sale', 'Amount', 'TransactionDate', 'CustomerID', 'Cashier']:
            self.sales_tree.heading(col, text=col, anchor="w")
            self.sales_tree.column(col, width=100)

        self.sales_tree.column('Sale_ID', width=60, anchor="center")
        self.sales_tree.column('SKU', width=80)
        self.sales_tree.column('Item_Name', width=150)
        self.sales_tree.column('Quantity_Sold', width=70, anchor="center")
        self.sales_tree.column('Price_at_Sale', width=90, anchor="e")
        self.sales_tree.column('Amount', width=90, anchor="e") # Amount column for each item's total
        self.sales_tree.column('TransactionDate', width=120)
        self.sales_tree.column('CustomerID', width=100)
        self.sales_tree.column('Cashier', width=100)


        yscroll_sales = ttk.Scrollbar(sales_display_frame, orient="vertical", command=self.sales_tree.yview)
        yscroll_sales.pack(side="right", fill="y")
        self.sales_tree.configure(yscrollcommand=yscroll_sales.set)

    def create_reports_tab(self, parent_frame):
        dashboard_frame = ttk.LabelFrame(parent_frame, text="System Dashboard")
        dashboard_frame.pack(padx=10, pady=10, fill="x")

        self.total_inventory_value_label = ttk.Label(dashboard_frame, text="Total Inventory Value: ₱0.00", font=("Arial", 12))
        self.total_inventory_value_label.pack(pady=5, anchor="w")

        self.total_items_label = ttk.Label(dashboard_frame, text="Total Items in Inventory: 0", font=("Arial", 12))
        self.total_items_label.pack(pady=5, anchor="w")

        self.total_sales_records_label = ttk.Label(dashboard_frame, text="Total Sales Records: 0", font=("Arial", 12))
        self.total_sales_records_label.pack(pady=5, anchor="w")

        ttk.Button(dashboard_frame, text="Refresh Dashboard", command=self.update_dashboard).pack(pady=5)

        low_stock_frame = ttk.LabelFrame(parent_frame, text="Low Stock Items (Needs Reorder)")
        low_stock_frame.pack(padx=10, pady=10, expand=True, fill="both")

        self.low_stock_tree = ttk.Treeview(low_stock_frame, columns=['SKU', 'Name', 'Quantity', 'Reorder_Level', 'Location'], show='headings')
        self.low_stock_tree.pack(side="left", fill="both", expand=True)

        for col in ['SKU', 'Name', 'Quantity', 'Reorder_Level', 'Location']:
            self.low_stock_tree.heading(col, text=col, anchor="w")
            self.low_stock_tree.column(col, width=100)

        self.low_stock_tree.column('SKU', width=80)
        self.low_stock_tree.column('Name', width=150)
        self.low_stock_tree.column('Quantity', width=70, anchor="center")
        self.low_stock_tree.column('Reorder_Level', width=80, anchor="center")
        self.low_stock_tree.column('Location', width=100)

        yscroll_low_stock = ttk.Scrollbar(low_stock_frame, orient="vertical", command=self.low_stock_tree.yview)
        yscroll_low_stock.pack(side="right", fill="y")
        self.low_stock_tree.configure(yscrollcommand=yscroll_low_stock.set)

        ttk.Button(low_stock_frame, text="Refresh Low Stock", command=self.update_low_stock_treeview).pack(pady=5)

    def create_user_management_tab(self, parent_frame):
        # Admin-only user management
        if self.current_user['Role'] != 'Admin':
            ttk.Label(parent_frame, text="Access Denied: Only Admins can manage users.").pack(pady=20)
            return

        input_frame = ttk.LabelFrame(parent_frame, text="Manage Users")
        input_frame.pack(padx=10, pady=10, fill="x")

        self.user_username_var = tk.StringVar()
        self.user_password_var = tk.StringVar()
        self.user_role_var = tk.StringVar(value='Cashier')

        ttk.Label(input_frame, text="Username:").grid(row=0, column=0, padx=5, pady=2, sticky="w")
        ttk.Entry(input_frame, textvariable=self.user_username_var, width=30).grid(row=0, column=1, padx=5, pady=2, sticky="ew")

        ttk.Label(input_frame, text="Password (for new/reset):").grid(row=1, column=0, padx=5, pady=2, sticky="w")
        ttk.Entry(input_frame, textvariable=self.user_password_var, show="*", width=30).grid(row=1, column=1, padx=5, pady=2, sticky="ew")

        ttk.Label(input_frame, text="Role:").grid(row=2, column=0, padx=5, pady=2, sticky="w")
        role_options = ['Cashier', 'Admin']
        ttk.Combobox(input_frame, textvariable=self.user_role_var, values=role_options, state="readonly", width=28).grid(row=2, column=1, padx=5, pady=2, sticky="ew")

        button_frame = ttk.Frame(parent_frame)
        button_frame.pack(padx=10, pady=5, fill="x")

        ttk.Button(button_frame, text="Add New User", command=self.add_user_gui).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Update User Role/Password", command=self.update_user_gui).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Delete User", command=self.delete_user_gui).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Clear User Fields", command=self.clear_user_fields).pack(side="left", padx=5)


        display_frame = ttk.LabelFrame(parent_frame, text="Current Users")
        display_frame.pack(padx=10, pady=10, expand=True, fill="both")

        self.users_tree = ttk.Treeview(display_frame, columns=['Username', 'Role'], show='headings')
        self.users_tree.pack(side="left", fill="both", expand=True)

        for col in ['Username', 'Role']:
            self.users_tree.heading(col, text=col, anchor="w")
            self.users_tree.column(col, width=150)

        yscroll_users = ttk.Scrollbar(display_frame, orient="vertical", command=self.users_tree.yview)
        yscroll_users.pack(side="right", fill="y")
        self.users_tree.configure(yscrollcommand=yscroll_users.set)

        self.users_tree.bind("<<TreeviewSelect>>", self.load_selected_user_into_fields)
        self.update_users_treeview() # Initial load

    def create_activity_log_tab(self, parent_frame):
        if self.current_user['Role'] != 'Admin':
            ttk.Label(parent_frame, text="Access Denied: Only Admins can view activity log.").pack(pady=20)
            return

        log_frame = ttk.LabelFrame(parent_frame, text="System Activity Log")
        log_frame.pack(padx=10, pady=10, expand=True, fill="both")

        self.activity_log_text = scrolledtext.ScrolledText(log_frame, wrap=tk.WORD, state=tk.DISABLED, font=('Consolas', 9))
        self.activity_log_text.pack(expand=True, fill="both")

        self.load_activity_log() # Load log content

        ttk.Button(log_frame, text="Refresh Log", command=self.load_activity_log).pack(pady=5)


    def create_user_settings_tab(self, parent_frame):
        settings_frame = ttk.LabelFrame(parent_frame, text=f"Change Password for {self.current_user['Username']}")
        settings_frame.pack(padx=20, pady=20, fill="x")

        self.current_password_var = tk.StringVar()
        self.new_password_var = tk.StringVar()
        self.confirm_new_password_var = tk.StringVar()

        ttk.Label(settings_frame, text="Current Password:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        ttk.Entry(settings_frame, textvariable=self.current_password_var, show="*", width=30).grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        ttk.Label(settings_frame, text="New Password:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        ttk.Entry(settings_frame, textvariable=self.new_password_var, show="*", width=30).grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        ttk.Label(settings_frame, text="Confirm New Password:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        ttk.Entry(settings_frame, textvariable=self.confirm_new_password_var, show="*", width=30).grid(row=2, column=1, padx=5, pady=5, sticky="ew")

        ttk.Button(settings_frame, text="Change Password", command=self.change_user_password).grid(row=3, column=0, columnspan=2, pady=10)


    # --- Input Validation and Data Loading ---
    def validate_integer_input(self, P):
        if P == "" or P.isdigit() or (P.startswith('-') and P[1:].isdigit() and len(P) > 1):
            return True
        return False
    
    def validate_positive_integer_input(self, P):
        if P == "" or (P.isdigit() and int(P) >= 0):
            return True
        return False

    def validate_float_input(self, P):
        if P == "":
            return True
        try:
            val = float(P)
            if val < 0: # Do not allow negative prices
                return False
            return True
        except ValueError:
            return False

    def bind_validation_feedback(self, entry_widget, var_to_track, validation_func):
        # A simple visual feedback mechanism for entries
        def check_and_style(*args):
            current_value = var_to_track.get()
            if not validation_func(str(current_value)):
                entry_widget.config(background="salmon") # Light red for invalid
            else:
                entry_widget.config(background="white") # Back to default
        var_to_track.trace_add("write", check_and_style)


    def clear_item_fields(self):
        self.sku_var.set("")
        self.name_var.set("")
        self.quantity_var.set(0)
        self.price_var.set(0.0)
        self.reorder_level_var.set(0)
        self.location_var.set("")
        # Reset background colors
        for child in self.inventory_tab.winfo_children():
            if isinstance(child, ttk.LabelFrame):
                for entry in child.winfo_children():
                    if isinstance(entry, ttk.Entry):
                        entry.config(background="white")


    def clear_user_fields(self):
        self.user_username_var.set("")
        self.user_password_var.set("")
        self.user_role_var.set("Cashier")

    def load_selected_item_into_fields(self, event):
        selected_item = self.inventory_tree.focus()
        if selected_item:
            values = self.inventory_tree.item(selected_item, 'values')
            self.sku_var.set(values[0])
            self.name_var.set(values[1])
            self.quantity_var.set(values[2])
            self.price_var.set(values[3])
            self.reorder_level_var.set(values[4])
            self.location_var.set(values[5])

    def load_selected_user_into_fields(self, event):
        selected_item = self.users_tree.focus()
        if selected_item:
            values = self.users_tree.item(selected_item, 'values')
            self.user_username_var.set(values[0])
            self.user_role_var.set(values[1])
            self.user_password_var.set("") # Never load password into field


    def update_treeview(self, tree, df):
        for item in tree.get_children():
            tree.delete(item)
        for index, row in df.iterrows():
            tree.insert('', 'end', values=list(row))

    def update_all_treeviews(self):
        self.update_treeview(self.inventory_tree, self.inventory_df)
        self.update_treeview(self.sales_tree, self.sales_df)
        self.update_low_stock_treeview()
        self.update_cart_display()
        if self.current_user['Role'] == 'Admin':
            self.update_users_treeview()
            self.load_activity_log()

    def update_low_stock_treeview(self):
        low_stock_df = get_low_stock_items(self.inventory_df)
        self.update_treeview(self.low_stock_tree, low_stock_df)

    def update_users_treeview(self):
        self.update_treeview(self.users_tree, self.users_df[['Username', 'Role']])

    def load_activity_log(self):
        if os.path.exists(ACTIVITY_LOG_FILE):
            try:
                with open(ACTIVITY_LOG_FILE, 'r') as f:
                    log_content = f.read()
                self.activity_log_text.config(state=tk.NORMAL)
                self.activity_log_text.delete('1.0', tk.END)
                self.activity_log_text.insert(tk.END, log_content)
                self.activity_log_text.see(tk.END) # Scroll to bottom
                self.activity_log_text.config(state=tk.DISABLED)
            except Exception as e:
                logging.error(f"Failed to load activity log: {e}")
                self.activity_log_text.config(state=tk.NORMAL)
                self.activity_log_text.delete('1.0', tk.END)
                self.activity_log_text.insert(tk.END, f"Error loading activity log: {e}")
                self.activity_log_text.config(state=tk.DISABLED)
        else:
            self.activity_log_text.config(state=tk.NORMAL)
            self.activity_log_text.delete('1.0', tk.END)
            self.activity_log_text.insert(tk.END, "Activity log file not found.")
            self.activity_log_text.config(state=tk.DISABLED)


    def update_dashboard(self):
        total_value, msg_value = get_inventory_value(self.inventory_df)
        self.total_inventory_value_label.config(text=msg_value)
        self.total_items_label.config(text=f"Total Items in Inventory: {len(self.inventory_df)}")
        self.total_sales_records_label.config(text=f"Total Sales Records: {len(self.sales_df)}")

    # --- Item Identification and Search Logic ---
    def resolve_item_identifier(self, identifier_text):
        """
        Attempts to resolve an identifier (SKU or Name) to a unique SKU.
        Returns the SKU, item_name, item_price if found uniquely, otherwise None and an error message.
        """
        if not identifier_text:
            return None, None, None, "Item identifier cannot be empty."

        matched_by_sku = self.inventory_df[self.inventory_df['SKU'].astype(str).str.lower() == identifier_text.lower()]
        if not matched_by_sku.empty:
            if len(matched_by_sku) == 1:
                item_row = matched_by_sku.iloc[0]
                return item_row['SKU'], item_row['Name'], item_row['Price'], None
            else:
                return None, None, None, f"Multiple items found with SKU-like identifier '{identifier_text}'. Please use a more specific identifier."

        matched_by_name = self.inventory_df[self.inventory_df['Name'].astype(str).str.lower() == identifier_text.lower()]
        if not matched_by_name.empty:
            if len(matched_by_name) == 1:
                item_row = matched_by_name.iloc[0]
                return item_row['SKU'], item_row['Name'], item_row['Price'], None
            else:
                return None, None, None, f"Multiple items found with the name '{identifier_text}'. Please use SKU to specify."

        return None, None, None, f"Item '{identifier_text}' not found by SKU or Name."

    def search_inventory_gui(self):
        search_term = self.inventory_search_var.get().strip()
        if not search_term:
            self.update_treeview(self.inventory_tree, self.inventory_df)
            return

        filtered_df = self.inventory_df[
            self.inventory_df['SKU'].astype(str).str.contains(search_term, case=False, na=False) |
            self.inventory_df['Name'].astype(str).str.contains(search_term, case=False, na=False)
        ]
        self.update_treeview(self.inventory_tree, filtered_df)
    
    # --- Autocomplete for Sales Tab ---
    def autocomplete_items(self, event=None):
        search_term = self.sale_item_identifier_var.get().strip()
        if not search_term:
            self.hide_autocomplete()
            return

        # Get the position of the entry widget
        x = self.sale_item_entry.winfo_rootx() - self.root.winfo_rootx()
        y = self.sale_item_entry.winfo_rooty() - self.root.winfo_rooty() + self.sale_item_entry.winfo_height()

        # Position the autocomplete frame
        self.autocomplete_frame.place(x=x, y=y, width=self.sale_item_entry.winfo_width())

        self.autocomplete_listbox.delete(0, tk.END)
        
        # Filter items
        filtered_items = self.inventory_df[
            self.inventory_df['SKU'].astype(str).str.contains(search_term, case=False, na=False) |
            self.inventory_df['Name'].astype(str).str.contains(search_term, case=False, na=False)
        ]

        if not filtered_items.empty:
            for index, row in filtered_items.iterrows():
                display_text = f"{row['Name']} (SKU: {row['SKU']}) [Qty: {row['Quantity']}]"
                self.autocomplete_listbox.insert(tk.END, display_text)
            self.autocomplete_listbox.lift() # Bring to front
            self.autocomplete_frame.lift()
        else:
            self.hide_autocomplete()

    def select_autocomplete_item(self, event=None):
        try:
            selected_index = self.autocomplete_listbox.curselection()[0]
            selected_text = self.autocomplete_listbox.get(selected_index)
            
            # Extract SKU from the selected text using regex
            match = re.search(r'SKU: (\w+)', selected_text)
            if match:
                sku = match.group(1)
                self.sale_item_identifier_var.set(sku)
                self.hide_autocomplete()
                self.sale_item_entry.focus_set() # Return focus to entry after selection
                self.process_barcode_or_enter() # Automatically add to cart after selection
            else:
                messagebox.showwarning("Selection Error", "Could not extract SKU from selected item.")
                self.hide_autocomplete()
        except IndexError:
            pass # No item selected
        except Exception as e:
            logging.error(f"Error selecting autocomplete item: {e}")
            messagebox.showerror("Error", f"An error occurred during item selection: {e}")
            self.hide_autocomplete()

    def hide_autocomplete(self):
        self.autocomplete_listbox.delete(0, tk.END)
        self.autocomplete_frame.place_forget() # Hide the frame


    # --- GUI Action Functions (Calling Backend) ---
    def add_item_gui(self):
        if self.current_user['Role'] != 'Admin':
            messagebox.showerror("Permission Denied", "Only Admins can add new items.")
            return
        try:
            sku = self.sku_var.get().strip().upper()
            name = self.name_var.get().strip()
            quantity = self.quantity_var.get()
            price = self.price_var.get()
            reorder_level = self.reorder_level_var.get()
            location = self.location_var.get().strip()

            if not self.validate_integer_input(str(quantity)) or quantity < 0:
                messagebox.showerror("Input Error", "Quantity must be a non-negative whole number.")
                return
            if not self.validate_float_input(str(price)) or price < 0:
                messagebox.showerror("Input Error", "Price must be a non-negative number.")
                return
            if not self.validate_integer_input(str(reorder_level)) or reorder_level < 0:
                messagebox.showerror("Input Error", "Reorder Level must be a non-negative whole number.")
                return

            self.inventory_df, success, message = add_item_backend(
                self.inventory_df, sku, name, quantity, price, reorder_level, location, self.current_user['Username']
            )
            if success:
                messagebox.showinfo("Success", message)
                self.update_all_treeviews()
                self.clear_item_fields()
                self.save_data()
            else:
                messagebox.showerror("Error", message)
        except Exception as e:
            logging.error(f"Error in add_item_gui: {e}")
            messagebox.showerror("Input Error", f"Invalid input. Please check all fields. Error: {e}")

    def update_quantity_gui(self):
        try:
            sku = self.sku_var.get().strip().upper()
            change = self.quantity_var.get()

            if not self.validate_integer_input(str(change)):
                messagebox.showerror("Input Error", "Quantity change must be an integer.")
                return

            self.inventory_df, success, message = update_item_quantity_backend(
                self.inventory_df, sku, change, self.current_user['Username']
            )
            if success:
                messagebox.showinfo("Success", message)
                self.update_all_treeviews()
                self.clear_item_fields()
                self.save_data()
            else:
                messagebox.showerror("Error", message)
        except Exception as e:
            logging.error(f"Error in update_quantity_gui: {e}")
            messagebox.showerror("Input Error", f"Invalid input for quantity change. Error: {e}")

    def update_details_gui(self):
        if self.current_user['Role'] != 'Admin':
            messagebox.showerror("Permission Denied", "Only Admins can update item details (excluding quantity).")
            return
        try:
            sku = self.sku_var.get().strip().upper()
            new_name = self.name_var.get().strip()

            price_val = self.price_var.get()
            new_price = float(price_val) if self.validate_float_input(str(price_val)) else None
            if new_price is not None and new_price < 0:
                messagebox.showerror("Input Error", "Price cannot be negative.")
                return

            reorder_val = self.reorder_level_var.get()
            new_reorder_level = int(reorder_val) if self.validate_integer_input(str(reorder_val)) else None
            if new_reorder_level is not None and new_reorder_level < 0:
                messagebox.showerror("Input Error", "Reorder Level cannot be negative.")
                return

            new_location = self.location_var.get().strip()

            self.inventory_df, success, message = update_item_details_backend(
                self.inventory_df, sku,
                new_name if new_name else None,
                new_price,
                new_reorder_level,
                new_location if new_location else None,
                self.current_user['Username']
            )
            if success:
                messagebox.showinfo("Success", message)
                self.update_all_treeviews()
                self.clear_item_fields()
                self.save_data()
            else:
                messagebox.showerror("Error", message)
        except ValueError as ve:
            logging.error(f"ValueError in update_details_gui: {ve}")
            messagebox.showerror("Input Error", f"Invalid number format for price or reorder level: {ve}")
        except Exception as e:
            logging.error(f"Error in update_details_gui: {e}")
            messagebox.showerror("Error", f"An unexpected error occurred: {e}")


    def delete_item_gui(self):
        if self.current_user['Role'] != 'Admin':
            messagebox.showerror("Permission Denied", "Only Admins can delete items.")
            return
        sku = self.sku_var.get().strip().upper()
        if not sku:
            messagebox.showerror("Error", "Pakisulat ang SKU para mg matuloy sa pag bura.")
            return

        confirm = messagebox.askyesno("Confirm Deletion", f"Sigurado ka ba na gusto mong burahin ang item kasama ang SKU: {sku}?")
        if confirm:
            self.inventory_df, success, message = delete_item_backend(self.inventory_df, sku, self.current_user['Username'])
            if success:
                messagebox.showinfo("Success", message)
                self.update_all_treeviews()
                self.clear_item_fields()
                self.save_data()
            else:
                messagebox.showerror("Error", message)

    def process_barcode_or_enter(self, event=None):
        identifier = self.sale_item_identifier_var.get().strip()
        self.hide_autocomplete() # Hide autocomplete listbox on processing

        try:
            quantity_to_add = self.sale_quantity_var.get()
            if quantity_to_add <= 0:
                messagebox.showwarning("Invalid Quantity", "Quantity must be a positive number.")
                self.sale_quantity_var.set(1) # Reset to 1
                self.sale_item_entry.focus_set()
                return
        except tk.TclError:
            messagebox.showwarning("Invalid Quantity", "Please enter a valid number for quantity.")
            self.sale_quantity_var.set(1)
            self.sale_item_entry.focus_set()
            return


        if not identifier:
            self.sale_item_identifier_var.set("")
            self.sale_item_entry.focus_set()
            return

        resolved_sku, item_name, item_price, error_message = self.resolve_item_identifier(identifier)

        if error_message:
            messagebox.showerror("Item Lookup Error", error_message)
            self.sale_item_identifier_var.set("")
            self.sale_item_entry.focus_set()
            return

        inventory_item = self.inventory_df[self.inventory_df['SKU'] == resolved_sku]
        if inventory_item.empty:
            messagebox.showerror("Stock Error", f"Item {resolved_sku} walang nakita sa inventory (critical error).")
            self.sale_item_identifier_var.set("")
            self.sale_item_entry.focus_set()
            return

        current_stock = inventory_item['Quantity'].iloc[0]

        found_in_cart = False
        for item in self.current_sale_items:
            if item['sku'] == resolved_sku:
                new_total_qty_in_cart = item['qty'] + quantity_to_add
                if new_total_qty_in_cart > current_stock:
                    messagebox.showwarning("Stock Warning", f"Adding {quantity_to_add} of '{item_name}' (SKU: {resolved_sku}) would exceed available stock of {current_stock}. Current in cart: {item['qty']}. Max can add: {current_stock - item['qty']}.")
                    self.sale_item_identifier_var.set("")
                    self.sale_item_entry.focus_set()
                    return
                item['qty'] = new_total_qty_in_cart
                item['subtotal'] = new_total_qty_in_cart * item_price
                found_in_cart = True
                break

        if not found_in_cart:
            if quantity_to_add > current_stock:
                messagebox.showwarning("Stock Warning", f"Cannot add {quantity_to_add} of '{item_name}' (SKU: {resolved_sku}). Only {current_stock} available.")
                self.sale_item_identifier_var.set("")
                self.sale_item_entry.focus_set()
                return
            if current_stock == 0:
                messagebox.showwarning("Out of Stock", f"'{item_name}' (SKU: {resolved_sku}) is out of stock.")
                self.sale_item_identifier_var.set("")
                self.sale_item_entry.focus_set()
                return

            self.current_sale_items.append({
                'sku': resolved_sku,
                'name': item_name,
                'qty': quantity_to_add,
                'price': item_price,
                'subtotal': quantity_to_add * item_price
            })

        self.update_cart_display()
        self.sale_item_identifier_var.set("")
        self.sale_quantity_var.set(1)
        self.sale_item_entry.focus_set()

    def add_item_to_cart_gui(self):
        self.process_barcode_or_enter()

    def update_cart_display(self):
        for item in self.shopping_cart_tree.get_children():
            self.shopping_cart_tree.delete(item)

        total_due = 0.0
        for item_data in self.current_sale_items:
            self.shopping_cart_tree.insert('', 'end', values=(
                item_data['sku'],
                item_data['name'],
                item_data['qty'],
                f"₱{item_data['price']:,.2f}",
                f"₱{item_data['subtotal']:,.2f}"
            ))
            total_due += item_data['subtotal']
        self.total_due_var.set(f"₱{total_due:,.2f}")

    def remove_item_from_cart_gui(self):
        selected_items = self.shopping_cart_tree.selection()
        if not selected_items:
            messagebox.showwarning("No Selection", "Pumili ka ng item sa cart para burahin.")
            return

        for selected_item in selected_items:
            item_values = self.shopping_cart_tree.item(selected_item, 'values')
            sku_to_remove = item_values[0]
            qty_in_cart_display = int(item_values[2]) 

            # Create a new list excluding the item to be removed
            new_cart_items = []
            removed_one = False
            for item_in_cart in self.current_sale_items:
                # If it's the item we want to remove AND we haven't removed it yet (for duplicates)
                if item_in_cart['sku'] == sku_to_remove and item_in_cart['qty'] == qty_in_cart_display and not removed_one:
                    removed_one = True
                    # If you only want to reduce quantity by 1 for multi-qty items in cart:
                    # if item_in_cart['qty'] > 1:
                    #     item_in_cart['qty'] -= 1
                    #     item_in_cart['subtotal'] = item_in_cart['qty'] * item_in_cart['price']
                    #     new_cart_items.append(item_in_cart)
                    # else:
                    #     continue # Skip adding this item to the new list if quantity becomes 0

                    # Current behavior: Remove the exact entry from the cart
                    continue
                new_cart_items.append(item_in_cart)
            
            if removed_one:
                messagebox.showinfo("Cart Update", f"Removed '{item_values[1]}' from cart.")
                self.current_sale_items = new_cart_items
            else:
                messagebox.showwarning("Error", "Could not remove selected item. Item not found in cart list (logic error).")


        self.update_cart_display()
        self.sale_item_entry.focus_set()

    def clear_cart(self):
        if self.current_sale_items:
            if not messagebox.askyesno("Clear Cart", "Gusto mo bang burahin lahat ng transaction?"):
                return

        self.current_sale_items = []
        self.update_cart_display()
        messagebox.showinfo("Cart Cleared", "Ang Transaction ay nabura na.")
        self.sale_item_entry.focus_set()

    # CORRECTED: finalize_sale_gui
    def finalize_sale_gui(self):
        if not self.current_sale_items:
            messagebox.showwarning("Finalize Sale", "walang item sa cart para mag proceed sa pagbayad.")
            return # Corrected indentation for this return

        customer_id = self.customer_id_var.get().strip()
        transaction_date_str = self.transaction_date_var.get().strip()

        if not customer_id:
            messagebox.showerror("Input Error", "Customer ID cannot be empty.")
            return
        
        try:
            transaction_date = datetime.strptime(transaction_date_str, '%Y-%m-%d')
        except ValueError:
            messagebox.showerror("Input Error", "Invalid date format. Please use YYYY-MM-DD.")
            return

        total_amount = sum(item['qty'] * item['price'] for item in self.current_sale_items) # Corrected sum logic

        self.prompt_for_payment(total_amount, customer_id, transaction_date)

    # CORRECTED: prompt_for_payment
    def prompt_for_payment(self, total_amount, customer_id, transaction_date):
        payment_window = tk.Toplevel(self.root)
        payment_window.title("Process Payment")
        payment_window.geometry("350x330") # Slightly increased height for better spacing
        payment_window.transient(self.root)
        payment_window.grab_set()

        tendered_amount_var = tk.DoubleVar(value=0.0)
        change_due_var = tk.DoubleVar(value=0.0)

        # Set initial tendered amount to be the total due for convenience
        tendered_amount_var.set(total_amount)

        def calculate_change(event=None):
            try:
                tendered = tendered_amount_var.get()
                change = tendered - total_amount
                change_due_var.set(f"{change:,.2f}") # Format as string here
                if change >= 0:
                    process_button.config(state=tk.NORMAL)
                else:
                    process_button.config(state=tk.DISABLED)
            except tk.TclError:
                change_due_var.set("0.00")
                process_button.config(state=tk.DISABLED)

        def process_payment():
            tendered = tendered_amount_var.get()
            if tendered < total_amount:
                messagebox.showerror("Payment Error", "Ang bayad ay kulang sa babayaran.")
                return

            # --- This is the critical block that finalizes the sale ---
            self.inventory_df, self.sales_df, success, message, recorded_total, low_stock_alerts = record_sale_backend(
                self.inventory_df, self.sales_df, self.current_sale_items, self.current_user['Username'], LOW_STOCK_THRESHOLD, customer_id, transaction_date
            )

            if success:
                messagebox.showinfo("Payment Success!", f"Payment Received: ₱{tendered:,.2f}\nChange Due: ₱{(tendered - total_amount):,.2f}\n\nSale Recorded Successfully!")
                open_cash_drawer() # Simulate opening the cash drawer
                self.update_all_treeviews() # Refresh all data displays
                self.save_data() # Save the updated inventory and sales logs
                self.show_receipt_window(self.current_sale_items, total_amount, tendered, (tendered - total_amount), customer_id, transaction_date)
                self.clear_cart() # Clear the shopping cart
                payment_window.destroy() # Close the payment window

                # --- Emergency Stock Alert (after successful sale) ---
                if low_stock_alerts:
                    alert_message = "\n\n".join(low_stock_alerts)
                    messagebox.showwarning("EMERGENCY LOW STOCK ALERT!", alert_message)
                    logging.warning(f"Low Stock Alert: {alert_message}") # Log the alert

            else:
                messagebox.showerror("Sale Error", f"Failed to finalize sale: {message}")
            # --- End of critical block ---

        ttk.Label(payment_window, text="Total Due:").pack(pady=5)
        ttk.Label(payment_window, text=f"₱{total_amount:,.2f}", font=("Arial", 16, "bold")).pack(pady=5) # Increased font size

        ttk.Label(payment_window, text="Amount Tendered:").pack(pady=5)
        tendered_entry = ttk.Entry(payment_window, textvariable=tendered_amount_var, width=20, font=("Arial", 14), # Increased font size
                               validate="key", validatecommand=(self.root.register(self.validate_float_input), '%P'))
        tendered_entry.pack(pady=5)
        tendered_entry.bind("<KeyRelease>", calculate_change)
        tendered_entry.focus_set()

        ttk.Label(payment_window, text="Change Due:").pack(pady=5)
        ttk.Label(payment_window, textvariable=change_due_var, font=("Arial", 16, "bold"), foreground="blue").pack(pady=5) # Increased font size

        process_button = ttk.Button(payment_window, text="Process Payment", command=process_payment, state=tk.DISABLED)
        process_button.pack(pady=10)

        calculate_change() # Initial calculation to enable/disable button
        tendered_entry.select_range(0, tk.END) # Select all text in tendered entry for easy overwrite

        payment_window.protocol("WM_DELETE_WINDOW", lambda: payment_window.destroy())

    # CORRECTED: show_receipt_window to include customer_id and transaction_date
    def show_receipt_window(self, sale_items, total_amount, tendered_amount, change_due, customer_id, transaction_date):
        receipt_window = tk.Toplevel(self.root)
        receipt_window.title("Official Receipt")
        receipt_window.geometry("400x600") # Adjust size as needed
        receipt_window.transient(self.root)
        receipt_window.grab_set()

        # Receipt Header
        ttk.Label(receipt_window, text="--- Official Receipt ---", font=("Courier New", 14, "bold")).pack(pady=5)
        ttk.Label(receipt_window, text="Maria Store", font=("Courier New", 12)).pack()
        ttk.Label(receipt_window, text=f"Date: {transaction_date.strftime('%Y-%m-%d %H:%M:%S')}", font=("Courier New", 10)).pack()
        ttk.Label(receipt_window, text=f"Customer ID: {customer_id}", font=("Courier New", 10)).pack()
        ttk.Label(receipt_window, text="------------------------", font=("Courier New", 14, "bold")).pack(pady=5)

        # Receipt details (scrollable)
        receipt_frame = ttk.Frame(receipt_window)
        receipt_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        receipt_text = scrolledtext.ScrolledText(receipt_frame, wrap=tk.WORD, width=40, height=15, font=("Courier New", 10))
        receipt_text.pack(fill=tk.BOTH, expand=True)

        # Populate receipt content
        receipt_text.insert(tk.END, "Item             Qty   Price     Total\n")
        receipt_text.insert(tk.END, "--------------------------------------\n")

        # --- THIS IS THE CRITICAL SECTION FOR INDENTATION ---
        for item_data in sale_items: # Corrected iteration for list of dicts
            item_name = item_data['name'] # Access 'name' key directly
            qty = item_data['qty']        # Access 'qty' key directly
            price = item_data['price']    # Access 'price' key directly
            line_total = qty * price
            receipt_text.insert(tk.END, f"{item_name:<16} {qty:<5} {price:<9.2f} {line_total:<8.2f}\n")
        # --- END OF CRITICAL SECTION ---

        receipt_text.insert(tk.END, "--------------------------------------\n")
        receipt_text.insert(tk.END, f"Total: {total_amount:>.2f}\n")
        receipt_text.insert(tk.END, f"Cash:  {tendered_amount:>.2f}\n")
        receipt_text.insert(tk.END, f"Change: {change_due:>.2f}\n")
        receipt_text.insert(tk.END, "--------------------------------------\n")
        receipt_text.insert(tk.END, "\nThank you for your purchase!\n")
        receipt_text.insert(tk.END, "------------------------\n")

        receipt_text.config(state=tk.DISABLED) # Make text read-only

        ttk.Button(receipt_window, text="Close", command=receipt_window.destroy).pack(pady=10)
        receipt_window.protocol("WM_DELETE_WINDOW", receipt_window.destroy)


    # --- User Management Backend (Admin Only) ---
    def add_user_gui(self):
        username = self.user_username_var.get().strip()
        password = self.user_password_var.get()
        role = self.user_role_var.get()

        if not username or not password:
            messagebox.showerror("Input Error", "Username and password cannot be empty.")
            return
        if len(password) < 6:
            messagebox.showerror("Input Error", "Password must be at least 6 characters long.")
            return

        self.users_df, success, message = add_user_backend(self.users_df, username, password, role, self.current_user['Username'])
        if success:
            save_users(self.users_df, self.current_user['Username'])
            messagebox.showinfo("Success", message)
            self.update_users_treeview()
            self.clear_user_fields()
        else:
            messagebox.showerror("Error", message)

    def update_user_gui(self):
        username_to_update = self.user_username_var.get().strip()
        new_password = self.user_password_var.get() # Can be empty if only role is changed
        new_role = self.user_role_var.get()

        if not username_to_update:
            messagebox.showerror("Input Error", "Please select or enter a username to update.")
            return
        if new_password and len(new_password) < 6:
            messagebox.showerror("Input Error", "New password must be at least 6 characters long.")
            return
        if new_password == "" and new_role == self.users_df[self.users_df['Username'] == username_to_update]['Role'].iloc[0]:
            messagebox.showwarning("No Changes", "No new password or role specified for update.")
            return


        if username_to_update == DEFAULT_ADMIN_USERNAME and new_role != 'Admin':
             messagebox.showwarning("Admin Role", f"Cannot change role of default admin '{DEFAULT_ADMIN_USERNAME}' from Admin.")
             new_role = 'Admin' # Force it back

        confirm = messagebox.askyesno("Confirm Update", f"Are you sure you want to update user '{username_to_update}'?")
        if confirm:
            self.users_df, success, message = update_user_backend(self.users_df, username_to_update, new_role, new_password if new_password else None, self.current_user['Username'])
            if success:
                save_users(self.users_df, self.current_user['Username'])
                messagebox.showinfo("Success", message)
                self.update_users_treeview()
                self.clear_user_fields()
            else:
                messagebox.showerror("Error", message)

    def delete_user_gui(self):
        username_to_delete = self.user_username_var.get().strip()
        if not username_to_delete:
            messagebox.showerror("Input Error", "Please select or enter a username to delete.")
            return

        if username_to_delete == self.current_user['Username']:
            messagebox.showerror("Error", "You cannot delete your own account while logged in.")
            return

        confirm = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete user '{username_to_delete}'? This cannot be undone.")
        if confirm:
            self.users_df, success, message = delete_user_backend(self.users_df, username_to_delete, self.current_user['Username'])
            if success:
                save_users(self.users_df, self.current_user['Username'])
                messagebox.showinfo("Success", message)
                self.update_users_treeview()
                self.clear_user_fields()
            else:
                messagebox.showerror("Error", message)

    def change_user_password(self):
        current_password = self.current_password_var.get()
        new_password = self.new_password_var.get()
        confirm_new_password = self.confirm_new_password_var.get()

        # Get the actual user data from the loaded DataFrame
        user_row = self.users_df[self.users_df['Username'] == self.current_user['Username']]
        if user_row.empty:
            messagebox.showerror("Error", "User data not found. Please re-login.")
            self.logout()
            return

        # Verify current password
        if not verify_password(current_password, user_row['Hashed_Password'].iloc[0]):
            messagebox.showerror("Password Change Failed", "Incorrect current password.")
            return

        if new_password != confirm_new_password:
            messagebox.showerror("Password Change Failed", "New passwords do not match.")
            return
        if len(new_password) < 6:
            messagebox.showerror("Password Change Failed", "New password must be at least 6 characters long.")
            return
        if new_password == current_password:
            messagebox.showwarning("Password Change", "New password is the same as the current password.")
            return

        # Update the password using the backend function
        self.users_df, success, message = update_user_backend(self.users_df, self.current_user['Username'], new_password=new_password, user_performing_action=self.current_user['Username'])
        if success:
            save_users(self.users_df, self.current_user['Username'])
            messagebox.showinfo("Password Change Success", "Your password has been changed successfully. Please remember your new password.")
            self.current_password_var.set("")
            self.new_password_var.set("")
            self.confirm_new_password_var.set("")
        else:
            messagebox.showerror("Password Change Failed", f"Failed to change password: {message}")


    def save_data(self):
        inv_success, inv_msg = save_inventory(self.inventory_df, self.current_user['Username'])
        sales_success, sales_msg = save_sales_log(self.sales_df, self.current_user['Username'])
        users_success, users_msg = save_users(self.users_df, self.current_user['Username']) # Save users if changes were made

        if not inv_success:
            messagebox.showerror("Save Error", f"Ang Inventory ay hindi maipatuloy: {inv_msg}")
        if not sales_success:
            messagebox.showerror("Save Error", f"Ang Sales data ay hindi maipatuloy: {sales_msg}")
        if not users_success:
            messagebox.showerror("Save Error", f"Ang User data ay hindi maipatuloy: {users_msg}")


    def logout(self):
        if self.current_sale_items:
            if not messagebox.askyesno("Unfinished Sale", "May natitira pang transaction sa cart, gusto mo bang baliwalain at mag patuloy sa pag alis/pag logout?"):
                return

        if messagebox.askyesno("Logout", "Gusto mo ba na talagang mag logout?"):
            self.save_data()
            logging.info(f"User {self.current_user['Username']} logged out.")
            self.root.destroy()
            if self.on_logout_callback:
                self.on_logout_callback()

    def on_closing(self):
        if self.current_sale_items:
            if not messagebox.askyesno("Unfinished Sale", "May natitira pang naiwan na transaction sa cart, gusto mo bang baliwalain at mag patuloy sa pag-alis?"):
                return

        if messagebox.askokcancel("Exit", "Gusto mo bang i-save ang data at mag patuloy sa pag-alis?"):
            self.save_data()
            logging.info(f"User {self.current_user['Username']} exited application.")
            self.root.destroy()
        else:
            logging.info(f"User {self.current_user['Username']} exited without saving.")
            self.root.destroy()


# --- Authentication Application Class ---
class AuthApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Mag Login / Mag Register")
        self.root.geometry("400x300")
        self.root.resizable(False, False)

        # Apply a theme to AuthApp as well
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TFrame', background='#f0f0f0')
        style.configure('TLabelFrame', background='#f0f0f0')
        style.configure('TLabel', background='#f0f0f0', font=('Arial', 10))
        style.configure('TButton', font=('Arial', 10, 'bold'), padding=6)
        style.map('TButton', background=[('active', '#cccccc')])

        self.users_df = load_users() # Load users directly into AuthApp

        self.username_var = tk.StringVar()
        self.password_var = tk.StringVar()

        self.setup_gui()
        logging.info("Auth App started.")


    def setup_gui(self):
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(expand=True, fill="both")

        login_frame = ttk.LabelFrame(main_frame, text="Login")
        login_frame.pack(pady=10, padx=10, fill="x")

        ttk.Label(login_frame, text="Username:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        ttk.Entry(login_frame, textvariable=self.username_var, width=30).grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        ttk.Label(login_frame, text="Password:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        ttk.Entry(login_frame, textvariable=self.password_var, show="*", width=30).grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        ttk.Button(login_frame, text="Login", command=self.login).grid(row=2, column=0, columnspan=2, pady=10)

        ttk.Label(main_frame, text="New user?").pack(pady=5)
        ttk.Button(main_frame, text="Register", command=self.open_registration_window).pack(pady=5)

        self.root.bind("<Return>", lambda event: self.login()) # Bind Enter key to login


    def login(self):
        username = self.username_var.get().strip()
        password = self.password_var.get()

        user_data, success, message = authenticate_user_backend(self.users_df, username, password)

        if success:
            messagebox.showinfo("Login Success", message)
            self.root.withdraw()
            self.open_pos_app(user_data)
        else:
            messagebox.showerror("Login Failed", message)

    def open_registration_window(self):
        reg_window = tk.Toplevel(self.root)
        reg_window.title("Register New User")
        reg_window.geometry("350x250")
        reg_window.transient(self.root)
        reg_window.grab_set()
        reg_window.resizable(False, False)

        reg_username_var = tk.StringVar()
        reg_password_var = tk.StringVar()
        reg_confirm_password_var = tk.StringVar()
        reg_role_var = tk.StringVar(value='Cashier')

        reg_frame = ttk.Frame(reg_window, padding="20")
        reg_frame.pack(expand=True, fill="both")

        ttk.Label(reg_frame, text="Username:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        ttk.Entry(reg_frame, textvariable=reg_username_var, width=30).grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        ttk.Label(reg_frame, text="Password:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        ttk.Entry(reg_frame, textvariable=reg_password_var, show="*", width=30).grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        ttk.Label(reg_frame, text="Confirm Pass:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        ttk.Entry(reg_frame, textvariable=reg_confirm_password_var, show="*", width=30).grid(row=2, column=1, padx=5, pady=5, sticky="ew")

        ttk.Label(reg_frame, text="Role:").grid(row=3, column=0, padx=5, pady=5, sticky="w")
        role_options = ['Cashier', 'Admin']
        ttk.Combobox(reg_frame, textvariable=reg_role_var, values=role_options, state="readonly").grid(row=3, column=1, padx=5, pady=5, sticky="ew")

        def register():
            username = reg_username_var.get().strip()
            password = reg_password_var.get()
            confirm_password = reg_confirm_password_var.get()
            role = reg_role_var.get()

            if password != confirm_password:
                messagebox.showerror("Registration Failed", "Ang Password ay hindi nsg tugma.")
                return
            if len(password) < 6:
                messagebox.showerror("Registration Failed", "Kailangangan ang iyong password ay tataas/hihigit pa sa anim na lettra/numero.")
                return
            if not username:
                messagebox.showerror("Registration Failed", "Username cannot be empty.")
                return


            self.users_df, success, message = add_user_backend(self.users_df, username, password, role, "Registration Window")
            if success:
                save_users(self.users_df, "Registration Window")
                messagebox.showinfo("Registration Success", message)
                reg_window.destroy()
            else:
                messagebox.showerror("Registration Failed", message)

        ttk.Button(reg_frame, text="Register", command=register).grid(row=4, column=0, columnspan=2, pady=10)
        reg_window.bind("<Return>", lambda event: register()) # Bind Enter key to register

        reg_window.protocol("WM_DELETE_WINDOW", reg_window.destroy)

    def open_pos_app(self, user_data):
        pos_root = tk.Toplevel(self.root)
        POSApp(pos_root, self.show_auth_app_on_logout, user_data)
        pos_root.protocol("WM_DELETE_WINDOW", self.on_pos_app_closing)
        pos_root.focus_set()

    def show_auth_app_on_logout(self):
        self.root.deiconify()
        self.username_var.set("")
        self.password_var.set("")
        self.root.focus_set()
        self.users_df = load_users() # Reload users in case they were modified by admin in POSApp

    def on_pos_app_closing(self):
        # This will trigger the POSApp's on_closing method, which handles saving and destroying.
        # After that, it'll return control here.
        self.root.deiconify()
        self.username_var.set("")
        self.password_var.set("")
        self.root.focus_set()
        self.users_df = load_users() # Reload users in case they were modified by admin in POSApp


if __name__ == "__main__":
    main_root = tk.Tk()
    auth_app = AuthApp(main_root)
    main_root.mainloop()
