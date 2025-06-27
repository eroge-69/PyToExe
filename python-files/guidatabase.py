import Tkinter as tk
import tkMessageBox
import json
import os

json_file = "value_database.json"

def load_values():
    if not os.path.exists(json_file):
        return []
    with open(json_file, 'r') as f:
        data = json.load(f)
    return data.get("values", [])

def save_values(values):
    with open(json_file, 'w') as f:
        json.dump({"values": values}, f)

def add_value():
    val = entry.get()
    if val and val not in values:
        values.append(val)
        listbox.insert(tk.END, val)
        save_values(values)
    entry.delete(0, tk.END)

def delete_value():
    try:
        sel = listbox.curselection()[0]
        val = listbox.get(sel)
        values.remove(val)
        listbox.delete(sel)
        save_values(values)
    except:
        pass

root = tk.Tk()
root.title("Value Database Editor")

values = load_values()

entry = tk.Entry(root)
entry.pack()

btn_add = tk.Button(root, text="Add", command=add_value)
btn_add.pack()

btn_delete = tk.Button(root, text="Delete", command=delete_value)
btn_delete.pack()

listbox = tk.Listbox(root)
for val in values:
    listbox.insert(tk.END, val)
listbox.pack()

root.mainloop()
