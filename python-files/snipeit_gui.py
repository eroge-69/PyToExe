import tkinter as tk
from tkinter import ttk, messagebox
import requests

API_TOKEN = "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJhdWQiOiIxIiwianRpIjoiMThjZGQ1MDcxOTA4NDY3MjIwNzY5MDc4NTdhNGUyZWMzZmZlZTU3NjE1ZGE0NTdkNDcxNjE5ZDliMjk0NTExOWFkNzc1OGI1ODdjNWNjZGQiLCJpYXQiOjE3NTIwNjYyMjQuNDM5NDIyLCJuYmYiOjE3NTIwNjYyMjQuNDM5NDI3LCJleHAiOjIyMjU0NTE4MjQuNDM1MTc3LCJzdWIiOiIxIiwic2NvcGVzIjpbXX0.QP5JVctmYM5nm0g_H3JxAuNhk2YckrPdyxtwJjDkI8Rj9MrDzma2912J9sccSpfN8UakAulYANk2vYZ0HA4N78HmbDxUsrdy1lQjVTQgZVj8jNqpsSHL7UT0gSSOqBOy-fKscmCmBynKHpNyGEUx3tUJrfZsFyQFS8aTKjbnwC7s2GCezbc1WB8PgBrviVwiKMHe_-9B_1p_ETpA9MXy7-rDjhhOhYKS7kkX7jShKOdn0U_nUynuoAFv5xJPnM4saSyoau1lMfJI2WydjFg87W6ZrIv_9zhyQq7p32dly3K1LD5xB74ZSpbtKbEMiOjdBNMMt7zbuYoHKirezNbXUcx7dsYNG_aS2fo--OSWXjHmOiik61ZtTtGF_qfesAzZ852_KjtQ2RA2lAYpO9BDu36LOwo4MRztyo_RCbcpp-_5cf4NRyneyyO5wAJHS3IuU2XbmdariA901jOhJu_TEbwrh0eq72nvpvsmqHX5EzFhYTZNfqK-lH_4BPBzcMdFNHOQtOo0DUojcpQyKWgu21StITSlSxbmMlCZXBRMGoafwFDZL91nVWY2l0Lm7QBZ88tNykF02p4hBuiSZvJ0JxC4hXoQ5xcup-fKWyppHMp9ilcQJJcfnxfAurKvYZg1gybAwjoSy8Mp38SeB0evokitqAzAEkHeNgwtB-LNmlQ"
API_URL = "http://102.221.237.202:8088/api/v1"

HEADERS = {
    "Authorization": f"Bearer {API_TOKEN}",
    "Accept": "application/json",
    "Content-Type": "application/json"
}

cart = []

def search_consumables(term):
    res = requests.get(f"{API_URL}/consumables", headers=HEADERS)
    if res.status_code == 200:
        data = res.json().get("rows", [])
        return [c for c in data if term.lower() in c['name'].lower()]
    return []

def get_users():
    res = requests.get(f"{API_URL}/users", headers=HEADERS)
    if res.status_code == 200:
        return res.json().get("rows", [])
    return []

def add_to_cart():
    try:
        item = consumable_box.get()
        cid = item.split(" - ")[0]
        quantity = int(quantity_entry.get())
        user = user_box.get()
        uid = user.split(" - ")[0]
        cart.append({"id": cid, "qty": quantity, "user": uid, "name": item.split(" - ")[1]})
        update_cart_display()
    except:
        messagebox.showerror("Error", "Please select valid values")

def update_cart_display():
    cart_list.delete(0, tk.END)
    for i, item in enumerate(cart):
        cart_list.insert(tk.END, f"{item['qty']} x {item['name']} → User ID {item['user']}")

def checkout():
    for item in cart:
        for _ in range(item['qty']):
            url = f"{API_URL}/consumables/{item['id']}/checkout"
            payload = {"assigned_to": item['user']}
            res = requests.post(url, json=payload, headers=HEADERS)
            if res.status_code != 200:
                messagebox.showwarning("Warning", f"Failed to checkout {item['name']}")
    messagebox.showinfo("Success", "Checkout complete!")
    cart.clear()
    update_cart_display()

def search_and_update():
    term = search_entry.get()
    matches = search_consumables(term)
    consumable_box["values"] = [f"{c['id']} - {c['name']} ({c['remaining']})" for c in matches]
    if matches:
        consumable_box.set(consumable_box["values"][0])

def load_users():
    users = get_users()
    user_box["values"] = [f"{u['id']} - {u['name']}" for u in users]
    if users:
        user_box.set(user_box["values"][0])

# GUI setup
root = tk.Tk()
root.title("Snipe-IT Mass Checkout")
root.geometry("550x450")

tk.Label(root, text="🔍 Search Consumable:").pack()
search_entry = tk.Entry(root)
search_entry.pack()

tk.Button(root, text="Search", command=search_and_update).pack(pady=5)

consumable_box = ttk.Combobox(root, width=50)
consumable_box.pack(pady=5)

tk.Label(root, text="Quantity:").pack()
quantity_entry = tk.Entry(root)
quantity_entry.pack()

tk.Label(root, text="Select Engineer:").pack()
user_box = ttk.Combobox(root, width=50)
user_box.pack()
tk.Button(root, text="🔁 Load Users", command=load_users).pack()

tk.Button(root, text="➕ Add to Cart", command=add_to_cart).pack(pady=5)

tk.Label(root, text="🛒 Cart:").pack()
cart_list = tk.Listbox(root, width=60, height=6)
cart_list.pack()

tk.Button(root, text="✅ Checkout All", command=checkout).pack(pady=10)

root.mainloop()
