import tkinter as tk
from tkinter import messagebox
import sqlite3

# Database සම්බන්ධ කිරීම
conn = sqlite3.connect("officers.db")
cursor = conn.cursor()

# Table එකක් තනන්න
cursor.execute("""
CREATE TABLE IF NOT EXISTS officers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    position TEXT NOT NULL,
    nic TEXT NOT NULL,
    contact TEXT NOT NULL
)
""")
conn.commit()

# Data එක save කරන්න function එක
def save_data():
    name = entry_name.get()
    position = entry_position.get()
    nic = entry_nic.get()
    contact = entry_contact.get()

    if name and position and nic and contact:
        cursor.execute("INSERT INTO officers (name, position, nic, contact) VALUES (?, ?, ?, ?)",
                       (name, position, nic, contact))
        conn.commit()
        messagebox.showinfo("සාර්ථකයි", "තොරතුරු සුරක්ෂිතයි!")
        entry_name.delete(0, tk.END)
        entry_position.delete(0, tk.END)
        entry_nic.delete(0, tk.END)
        entry_contact.delete(0, tk.END)
    else:
        messagebox.showwarning("වරදකි", "සියලු ක්ෂේත්‍ර පුරවන්න!")

# GUI එක
window = tk.Tk()
window.title("නිලධාරී තොරතුරු රැස් කිරීම")

tk.Label(window, text="නම:").grid(row=0, column=0, padx=10, pady=5, sticky="e")
entry_name = tk.Entry(window, width=30)
entry_name.grid(row=0, column=1)

tk.Label(window, text="තනතුර:").grid(row=1, column=0, padx=10, pady=5, sticky="e")
entry_position = tk.Entry(window, width=30)
entry_position.grid(row=1, column=1)

tk.Label(window, text="ජා. හැ. අංකය:").grid(row=2, column=0, padx=10, pady=5, sticky="e")
entry_nic = tk.Entry(window, width=30)
entry_nic.grid(row=2, column=1)

tk.Label(window, text="දුරකථන අංකය:").grid(row=3, column=0, padx=10, pady=5, sticky="e")
entry_contact = tk.Entry(window, width=30)
entry_contact.grid(row=3, column=1)

tk.Button(window, text="සුරකින්න", command=save_data).grid(row=4, column=0, columnspan=2, pady=10)

window.mainloop()

# Close connection (මෘදුකාංගය වසන්නට කලින් call කරන්න)
# conn.close()
