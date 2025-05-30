
import tkinter as tk
from tkinter import messagebox
import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# === Google Sheets Setup ===
SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/spreadsheets",
         "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]

CREDS_JSON = "visitorcheckinapp-461023-c498725b59c1.json"
SHEET_NAME = "Visitor Log"

def connect_sheet():
    creds = ServiceAccountCredentials.from_json_keyfile_name(CREDS_JSON, SCOPE)
    client = gspread.authorize(creds)
    sheet = client.open(SHEET_NAME).sheet1
    return sheet

def generate_unique_id():
    timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    return f"SE-25{timestamp}"

root = tk.Tk()
root.title("Smile Europe Wholesale - Visitor Log")
root.geometry("400x300")

def clear_fields():
    entry_name.delete(0, tk.END)
    entry_business.delete(0, tk.END)
    entry_phone.delete(0, tk.END)
    entry_unique_id.delete(0, tk.END)

def register_customer():
    name = entry_name.get().strip()
    business = entry_business.get().strip()
    phone = entry_phone.get().strip()
    if not name or not business or not phone:
        messagebox.showerror("Missing Info", "Please fill all fields.")
        return

    unique_id = generate_unique_id()
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    sheet = connect_sheet()
    sheet.append_row([timestamp, name, business, phone, unique_id])

    messagebox.showinfo("Registered", f"Customer registered.\nUnique ID: {unique_id}")
    clear_fields()

def checkin_customer():
    unique_id = entry_unique_id.get().strip()
    if not unique_id:
        messagebox.showerror("Missing Info", "Please enter Unique ID.")
        return

    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    sheet = connect_sheet()
    sheet.append_row([timestamp, "", "", "", unique_id])

    messagebox.showinfo("Check-In", "Returning customer check-in recorded.")
    clear_fields()

tk.Label(root, text="Name").pack()
entry_name = tk.Entry(root, width=40)
entry_name.pack()

tk.Label(root, text="Business Name").pack()
entry_business = tk.Entry(root, width=40)
entry_business.pack()

tk.Label(root, text="Phone Number").pack()
entry_phone = tk.Entry(root, width=40)
entry_phone.pack()

tk.Button(root, text="Register New Customer", command=register_customer, bg="green", fg="white").pack(pady=5)

tk.Label(root, text="OR Check-In with Unique ID").pack(pady=10)
entry_unique_id = tk.Entry(root, width=40)
entry_unique_id.pack()

tk.Button(root, text="Check-In", command=checkin_customer, bg="blue", fg="white").pack(pady=5)

root.mainloop()
