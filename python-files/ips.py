import pandas as pd
import tkinter as tk
from tkinter import messagebox, ttk
import webbrowser

EXCEL_FILE = "C:/Users/roshan.paudel/Desktop/IPSSSSSSSS.xlsx"
IP_COLUMN = "IP"
NAME_COLUMN = "Name"

# Load data from Excel
df = pd.read_excel(EXCEL_FILE)
df = df[[NAME_COLUMN, IP_COLUMN]].dropna()
df[NAME_COLUMN] = df[NAME_COLUMN].astype(str)
df[IP_COLUMN] = df[IP_COLUMN].astype(str)
router_dict = dict(zip(df[NAME_COLUMN], df[IP_COLUMN]))

def connect_to_router(ip):
    firefox_path = "C:/Program Files/Mozilla Firefox/firefox.exe"
    try:
        webbrowser.get(firefox_path + " %s").open(f"http://{ip}")
    except webbrowser.Error:
        webbrowser.open(f"http://{ip}")

def on_search(event=None):
    search_term = search_var.get().strip().lower()
    listbox.delete(0, tk.END)
    if len(search_term) >= 1:
        matches = [name for name in router_dict if search_term in name.lower()]
        for match in matches:
            listbox.insert(tk.END, match)



def on_connect():
    selected = listbox.curselection()
    if not selected:
        messagebox.showwarning("Select Router", "Please select a router from the list.")
        return
    selected_name = listbox.get(selected[0])
    ip = router_dict[selected_name]
    connect_to_router(ip)
    
# === GUI SETUP ===
root = tk.Tk()
root.title("MikroTik Router Quick Access")
root.geometry("500x400")
root.resizable(False, False)

style = ttk.Style()
style.theme_use("clam")

main_frame = ttk.Frame(root, padding=10)
main_frame.pack(fill="both", expand=True)

ttk.Label(main_frame, text="🔍 Search Router:", font=("Segoe UI", 11)).pack(anchor="w")

search_var = tk.StringVar()
search_entry = ttk.Entry(main_frame, textvariable=search_var, font=("Segoe UI", 11))
search_entry.pack(fill="x", pady=(0, 10))
search_entry.bind("<KeyRelease>", on_search)

list_frame = ttk.Frame(main_frame)
list_frame.pack(fill="both", expand=True)

listbox = tk.Listbox(list_frame, font=("Segoe UI", 10), activestyle="dotbox")
scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=listbox.yview)
listbox.config(yscrollcommand=scrollbar.set)

listbox.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")

connect_button = ttk.Button(main_frame, text="🌐 Connect", command=on_connect)
connect_button.pack(pady=10)

root.mainloop()