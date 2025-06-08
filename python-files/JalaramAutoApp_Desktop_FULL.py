import tkinter as tk
from tkinter import messagebox, filedialog
import pandas as pd
import datetime
import webbrowser
import os

# ---------- GLOBAL CONFIG ----------
EXCEL_PATH = "jalaram_policies.xlsx"
WHATSAPP_NUMBER = "6351063036"

# ---------- CORE FUNCTIONS ----------

def send_whatsapp_reminder(name, vehicle, date):
    msg_guj = f"શ્રીમાન/શ્રીમતી {name},\nઆપના વાહન નં. {vehicle} ની વીમા પૉલિસી {date} ના રોજ પૂર્ણ થઈ રહી છે.\n\nતમારા વાહન ના વીમા ને સમય પર રિન્યુ કરાવો જેથી કાયદેસર રક્ષણ મળતું રહે અને કોઈ પણ દંડમાંથી બચી શકાય.\n\nવિમો પણ સંબંધ છે – વ્યવસાય નહીં.\nજય જલારામ!"
    url = f"https://wa.me/{WHATSAPP_NUMBER}?text={msg_guj}"
    webbrowser.open(url)

def calculate_days_left(renew_date):
    today = datetime.date.today()
    rdate = datetime.datetime.strptime(renew_date, "%d-%m-%Y").date()
    return (rdate - today).days

def save_to_excel(data):
    df = pd.DataFrame([data])
    if os.path.exists(EXCEL_PATH):
        df.to_excel(EXCEL_PATH, index=False, header=False, mode='a')
    else:
        df.to_excel(EXCEL_PATH, index=False)

def open_pdf_placeholder():
    messagebox.showinfo("PDF Upload", "Auto PDF reading feature is under development.")

# ---------- GUI SETUP ----------
root = tk.Tk()
root.title("Jalaram Auto – Powered by Jay Thakker")
root.geometry("500x500")

# Labels & Inputs
tk.Label(root, text="Customer Name").pack()
entry_name = tk.Entry(root)
entry_name.pack()

tk.Label(root, text="Vehicle No").pack()
entry_vehicle = tk.Entry(root)
entry_vehicle.pack()

tk.Label(root, text="Renewal Date (dd-mm-yyyy)").pack()
entry_renew = tk.Entry(root)
entry_renew.pack()

tk.Label(root, text="OD Premium").pack()
entry_od = tk.Entry(root)
entry_od.pack()

tk.Label(root, text="TP Premium").pack()
entry_tp = tk.Entry(root)
entry_tp.pack()

tk.Label(root, text="Sub-Agent Name").pack()
entry_agent = tk.Entry(root)
entry_agent.pack()

tk.Label(root, text="Payment Type (Cash/Credit/Online)").pack()
entry_payment = tk.Entry(root)
entry_payment.pack()

def handle_submit():
    try:
        name = entry_name.get()
        vehicle = entry_vehicle.get()
        renew = entry_renew.get()
        od = float(entry_od.get())
        tp = float(entry_tp.get())
        agent = entry_agent.get()
        pay_type = entry_payment.get()
        net = od + tp

        days_left = calculate_days_left(renew)
        data = {
            "Customer": name, "Vehicle": vehicle, "Renewal Date": renew, "Days Left": days_left,
            "OD": od, "TP": tp, "Net": net, "Agent": agent, "Payment": pay_type
        }
        save_to_excel(data)

        color = "white"
        if days_left <= 30:
            color = "red"
        elif days_left <= 80:
            color = "yellow"
        elif days_left <= 180:
            color = "blue"

        root.configure(bg=color)
        messagebox.showinfo("Saved", f"Policy saved for {name}\nDays left: {days_left}")
    except Exception as e:
        messagebox.showerror("Error", f"Something went wrong: {str(e)}")

def handle_reminder():
    name = entry_name.get()
    vehicle = entry_vehicle.get()
    renew = entry_renew.get()
    send_whatsapp_reminder(name, vehicle, renew)

# Buttons
tk.Button(root, text="Save Policy", command=handle_submit).pack(pady=10)
tk.Button(root, text="Send WhatsApp Reminder", command=handle_reminder).pack(pady=10)
tk.Button(root, text="Upload Policy PDF", command=open_pdf_placeholder).pack(pady=10)
tk.Button(root, text="Exit", command=root.quit).pack(pady=20)

root.mainloop()
