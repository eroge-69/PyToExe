products = {
    "P001": {"name": "Laptop", "category": "Electronics", "price": 999.99, "stock_quantity": 25, "min_stock_level": 5},
    "P002": {"name": "Office Chair", "category": "Furniture", "price": 149.99, "stock_quantity": 12, "min_stock_level": 3},
    "P003": {"name": "Notebook", "category": "Stationery", "price": 2.99, "stock_quantity": 2, "min_stock_level": 10},
}

transactions = {
    "T001": {"product_id": "P001", "type": "SALE", "quantity": 3, "total_amount": 3 * 999.99},
    "T002": {"product_id": "P002", "type": "RESTOCK", "quantity": 8, "total_amount": 0.0},
}

def add_product(products):
    last_id = max((int(pid[1:]) for pid in products), default=0)
    new_id = f"P{last_id + 1:03d}"

    name = input("Enter product name: ").strip()
    category = input("Enter product category: ").strip()
    if not name or not category:
        print("Error: name and category cannot be empty.")
        return False

    try:
        price = float(input("Enter price (0.01–9999.99): "))
        if not (0.01 <= price <= 9999.99):
            raise ValueError
        stock_quantity = int(input("Enter stock quantity (0 or more): "))
        if stock_quantity < 0:
            raise ValueError
        min_stock_level_input = input("Enter minimum stock level (leave empty for 5): ").strip()
        min_stock_level = int(min_stock_level_input) if min_stock_level_input else 5
        if not (0 <= min_stock_level <= 1000):
            raise ValueError
    except ValueError:
        print("Invalid value entered.")
        return False

    products[new_id] = {
        "name": name,
        "category": category,
        "price": price,
        "stock_quantity": stock_quantity,
        "min_stock_level": min_stock_level
    }
    print(f"Product {new_id} added successfully.")
    return True

def search_products(products):
    criteria = input("Search by 'name' or 'category': ").strip().lower()
    if criteria not in ("name", "category"):
        print("Invalid search criteria. Use 'name' or 'category'.")
        return False

    keyword = input(f"Enter keyword to search in {criteria}: ").strip().lower()
    found_any = False

    for pid, data in products.items():
        if keyword in data[criteria].lower():
            found_any = True
            print(f"\nProduct ID: {pid}")
            print(f"  Name: {data['name']}")
            print(f"  Category: {data['category']}")
            print(f"  Price: {data['price']}")
            print(f"  Stock: {data['stock_quantity']}  Min Stock Level: {data['min_stock_level']}")
            if data['stock_quantity'] < data['min_stock_level']:
                print("  ** Warning: Stock is very low! **")

    if not found_any:
        print("No products matched your search.")
        return False
    return True

def restock_product(products, transactions):
    print("\nAvailable products:")
    for pid, data in products.items():
        print(f"{pid}: {data['name']} (Current stock: {data['stock_quantity']})")

    pid = input("Enter a product ID to restock: ").strip()
    if pid not in products:
        print("Incorrect product ID.")
        return False

    try:
        qty = int(input("Enter quantity to restock (1–500): "))
        if not (1 <= qty <= 500):
            raise ValueError
    except ValueError:
        print("Invalid value.")
        return False

    products[pid]["stock_quantity"] += qty
    tid = f"T{len(transactions) + 1:03d}"
    transactions[tid] = {"product_id": pid, "type": "RESTOCK", "quantity": qty, "total_amount": 0.0}
    print(f"Restocked {qty} units of {products[pid]['name']}. New stock: {products[pid]['stock_quantity']}")
    return True

def process_sale(products, transactions):
    print("\nProducts available for sale:")
    for pid, data in products.items():
        print(f"{pid}: {data['name']} - Stock: {data['stock_quantity']} - Price: {data['price']}")

    pid = input("Enter a product ID to sell: ").strip()
    if pid not in products:
        print("Wrong product ID.")
        return False

    try:
        qty = int(input("Enter quantity to sell: "))
        if qty <= 0:
            raise ValueError
    except ValueError:
        print("Invalid quantity value.")
        return False

    if products[pid]["stock_quantity"] < qty:
        print("Not enough stock available.")
        return False

    products[pid]["stock_quantity"] -= qty
    total = qty * products[pid]["price"]
    tid = f"T{len(transactions) + 1:03d}"
    transactions[tid] = {"product_id": pid, "type": "SALE", "quantity": qty, "total_amount": total}
    print(f"Sold {qty} units of {products[pid]['name']}. Total amount: {total:.2f}")
    return True

def generate_reports(products, transactions):
    print("="*10,  "a) Low stock alert" ,"="*10 )
    for pid, data in products.items():
        if data["stock_quantity"] < data["min_stock_level"]:
            print(f"{data['name']} (ID: {pid}) — Stock: {data['stock_quantity']}, Min required: {data['min_stock_level']}")

    print("="*10,  "b) All products with stock levels ","="*10 )
    for pid, data in products.items():
        value = data["stock_quantity"] * data["price"]
        print(f"{data['name']} (ID: {pid}) — Stock: {data['stock_quantity']}, Total value: {value:.2f}")

    print("="*10,  "c) Recent transactions summary ","="*10 )
    for tid, t in transactions.items():
        print(f"{tid}: {t['type']} - {t['product_id']} - Qty: {t['quantity']} - Total: {t['total_amount']:.2f}")

    print("="*10,  "d) Total inventory value" ,"="*10 )
    total_val = sum(data["stock_quantity"] * data["price"] for data in products.values())
    print(f"Total inventory value: {total_val:.2f}")
    return True

def display_all_products(products):
    if not products:
        print("No products in inventory.")
        return False

    print(f"\n{'Product ID':<10}{'Name':<20}{'Category':<15}{'Price':<10}{'Stock':<10}{'Status'}")
    print("-" * 70)
    for pid, data in products.items():
        status = ("out of stock" if data["stock_quantity"] == 0 else
                  "low stock" if data["stock_quantity"] < data["min_stock_level"] else
                  "in stock")
        print(f"{pid:<10}{data['name']:<20}{data['category']:<15}{data['price']:<10.2f}{data['stock_quantity']:<10}{status}")
    return True

def display_menu():
    print("="*10, "INVENTORY MANAGEMENT SYSTEM ","="*10,
              "\n 1. Add New Product ",
               "\n 2. Search Products ",
                "\n 3. Restock Product",
                "\n 4. Process Sale",
                "\n 5. Generate Reports",
                "\n 6. Display All Products",
                "\n 7. Exit ")
    try:
        choice = int(input("Enter between 1 and 7: "))
        if 1 <= choice <= 7:
            return choice
    except ValueError:
        pass
    print("Invalid choice. Please enter a number between 1 and 7.")
    return None

def main():
    while True:
        choice = display_menu()
        if choice == 1:
            add_product(products)
        elif choice == 2:
            search_products(products)
        elif choice == 3:
            restock_product(products, transactions)
        elif choice == 4:
            process_sale(products, transactions)
        elif choice == 5:
            generate_reports(products, transactions)
        elif choice == 6:
            display_all_products(products)
        elif choice == 7:
            print("Exiting. Goodbye!")
            break

if __name__ == "__main__":
    main()
