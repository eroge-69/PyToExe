import tkinter as tk
from tkinter import simpledialog, messagebox

# Data structure to store items
item_database = []

# Helper function to search items by keyword or name
def search_items(query):
    query = query.lower()
    matches = []
    for item in item_database:
        if query in item['name'].lower() or any(query in kw.lower() for kw in item['keywords']):
            matches.append(item)
    return matches

# Function to clear the current frame
def clear_frame():
    for widget in main_frame.winfo_children():
        widget.destroy()

# Add item workflow
def add_item():
    clear_frame()
    
    # Prompt for item name
    item_name = simpledialog.askstring("Add Item", "Enter item name:", parent=root)
    if not item_name:
        main_menu()
        return

    # Prompt for keywords
    keyword_str = simpledialog.askstring("Add Item", "Enter keywords (comma separated):", parent=root)
    keywords = [kw.strip() for kw in keyword_str.split(',')] if keyword_str else []

    # Prompt for cost
    try:
        cost = float(simpledialog.askstring("Add Item", "Enter item cost:", parent=root))
    except (ValueError, TypeError):
        messagebox.showerror("Invalid Input", "Cost must be a number.")
        main_menu()
        return

    # Prompt for estimated value
    try:
        estimated_value = float(simpledialog.askstring("Add Item", "Enter estimated value:", parent=root))
    except (ValueError, TypeError):
        messagebox.showerror("Invalid Input", "Estimated value must be a number.")
        main_menu()
        return

    # Store the item
    item = {
        'name': item_name,
        'keywords': keywords,
        'cost': cost,
        'estimated_value': estimated_value
    }
    item_database.append(item)

    # Show summary
    summary = (
        f"Item Added:\n"
        f"1. Name: {item_name}\n"
        f"2. Keywords: {', '.join(keywords)}\n"
        f"3. Cost: ${cost:.2f}\n"
        f"4. Estimated Value: ${estimated_value:.2f}"
    )
    messagebox.showinfo("Item Summary", summary)
    main_menu()

# Lookup item workflow
def lookup_item():
    clear_frame()
    query = simpledialog.askstring("Look Up Item", "Enter item name or keyword:", parent=root)
    if not query:
        main_menu()
        return

    matches = search_items(query)

    if matches:
        result_text = "Items Found:\n\n"
        for idx, item in enumerate(matches, 1):
            result_text += (
                f"{idx}. Name: {item['name']}\n"
                f"   Keywords: {', '.join(item['keywords'])}\n"
                f"   Cost: ${item['cost']:.2f}\n"
                f"   Estimated Value: ${item['estimated_value']:.2f}\n\n"
            )
    else:
        result_text = "No items found."

    messagebox.showinfo("Search Results", result_text)

    again = messagebox.askyesno("Search Again?", "Would you like to look up another item?")
    if again:
        lookup_item()
    else:
        main_menu()

# Main menu
def main_menu():
    clear_frame()

    title = tk.Label(main_frame, text="Inventory Manager", font=("Helvetica", 20), bg="#333", fg="#eee")
    title.pack(pady=20)

    btn1 = tk.Button(main_frame, text="1. Add an Item", font=("Helvetica", 14),
                     width=30, command=add_item, bg="#555", fg="#fff")
    btn1.pack(pady=10)

    btn2 = tk.Button(main_frame, text="2. Look Up an Item", font=("Helvetica", 14),
                     width=30, command=lookup_item, bg="#555", fg="#fff")
    btn2.pack(pady=10)

    btn3 = tk.Button(main_frame, text="3. Exit", font=("Helvetica", 14),
                     width=30, command=root.quit, bg="#555", fg="#fff")
    btn3.pack(pady=10)

# GUI setup
root = tk.Tk()
root.title("Item Inventory System")
root.geometry("500x400")
root.configure(bg="#222")

main_frame = tk.Frame(root, bg="#222")
main_frame.pack(expand=True, fill="both")

main_menu()
root.mainloop()
