
import tkinter as tk
from tkinter import filedialog, messagebox
import datetime
import getpass
import csv
import os

def submit_issue():
    name = getpass.getuser()
    email = f"{name}@genpact.com"
    issue_type = issue_type_entry.get()
    description = description_text.get("1.0", tk.END).strip()
    screenshot_path = screenshot_entry.get()
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Save to CSV
    file = "it_issues_log.csv"
    file_exists = os.path.isfile(file)
    with open(file, mode='a', newline='') as csvfile:
        fieldnames = ['Timestamp', 'Name', 'Email', 'Issue Type', 'Description', 'Screenshot']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerow({
            'Timestamp': timestamp,
            'Name': name,
            'Email': email,
            'Issue Type': issue_type,
            'Description': description,
            'Screenshot': screenshot_path
        })

    messagebox.showinfo("Submitted", "Issue submitted successfully!")

def browse_screenshot():
    file_path = filedialog.askopenfilename()
    screenshot_entry.delete(0, tk.END)
    screenshot_entry.insert(0, file_path)

# GUI Setup
root = tk.Tk()
root.title("Nissan IT Issue Logger")

tk.Label(root, text="Issue Type").grid(row=0, column=0)
issue_type_entry = tk.Entry(root, width=40)
issue_type_entry.grid(row=0, column=1)

tk.Label(root, text="Description").grid(row=1, column=0)
description_text = tk.Text(root, width=40, height=5)
description_text.grid(row=1, column=1)

tk.Label(root, text="Screenshot").grid(row=2, column=0)
screenshot_entry = tk.Entry(root, width=30)
screenshot_entry.grid(row=2, column=1, sticky="w")
tk.Button(root, text="Browse", command=browse_screenshot).grid(row=2, column=2)

tk.Button(root, text="Submit", command=submit_issue).grid(row=3, column=1, pady=10)

root.mainloop()
