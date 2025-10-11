import tkinter as tk

# Sakht panjare asli
root = tk.Tk()
root.title("Barname List")
root.geometry("300x250")  # andaze safhe
root.configure(bg="pink")  # pas zamine surati

# List item ha
items = ["Item 1", "Item 2", "Item 3", "Item 4", "Item 5"]

# Sakht Listbox
listbox = tk.Listbox(root, bg="white", fg="black", font=("Arial", 12))
for item in items:
    listbox.insert(tk.END, item)
listbox.pack(pady=30, padx=20, fill=tk.BOTH, expand=True)

# Ejra
root.mainloop()
