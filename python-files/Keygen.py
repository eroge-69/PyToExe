import hashlib
import tkinter as tk
from tkinter import ttk

def generate_activation_code(product_code: str) -> str:
    # Step 1: Hash the product code (deterministic, secure)
    hashed = hashlib.sha256(product_code.encode()).hexdigest().upper()

    # Step 2: Break into activation key blocks
    block1 = "CHN" + hashed[0:2]      # CHN + 2 characters
    block2 = hashed[2:7]
    block3 = hashed[7:12]
    block4 = hashed[12:17]
    block5 = hashed[17:22]

    # Step 3: Last block = digits from hash (5 digits)
    digits = "".join(c for c in hashed if c.isdigit())[:5]
    if len(digits) < 5:
        digits = digits.ljust(5, "0")

    # Step 4: Join blocks into final activation key
    activation_key = "-".join([block1, block2, block3, block4, block5, digits])
    return activation_key

def on_generate():
    product_id = entry.get().strip()
    if product_id:
        key = generate_activation_code(product_id)
        result_var.set(key)
    else:
        result_var.set("Enter a Product ID")

# --- GUI Setup ---
root = tk.Tk()
root.title("Product Keygen")
root.geometry("500x200")

ttk.Label(root, text="Enter Product ID:").pack(pady=5)
entry = ttk.Entry(root, width=50)
entry.pack(pady=5)

ttk.Button(root, text="Generate Activation Key", command=on_generate).pack(pady=5)

result_var = tk.StringVar()
ttk.Label(root, textvariable=result_var, font=("Courier", 12), foreground="blue").pack(pady=10)

root.mainloop()
