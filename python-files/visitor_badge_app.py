import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import requests
import datetime

# Label file name (must be in the same directory)
LABEL_FILE = "Visitor Badge.dymo"

# DYMO Web Service URL
DYMO_URL = "https://localhost:41951/DYMO/DLS/Printing/PrintLabel"

def print_label(name, valid_from, valid_to, host, supervised):
    try:
        with open(LABEL_FILE, 'r', encoding='utf-8') as f:
            label_xml = f.read()

        label_data = {
            "LabelXml": label_xml,
            "LabelSetXml": f"""
                <LabelSet>
                    <Label>
                        <Name>{name}</Name>
                        <ValidFrom>{valid_from}</ValidFrom>
                        <ValidTo>{valid_to}</ValidTo>
                        <Host>{host}</Host>
                        <Supervised>{supervised}</Supervised>
                    </Label>
                </LabelSet>
            """,
            "PrinterName": ""  # Let DYMO auto-select the printer
        }

        response = requests.post(DYMO_URL, json=label_data, verify=False)

        if response.status_code == 200:
            messagebox.showinfo("Success", "Label sent to printer.")
        else:
            messagebox.showerror("Error", f"Print failed: {response.status_code}\n{response.text}")

    except Exception as e:
        messagebox.showerror("Error", str(e))


# GUI Setup
app = tk.Tk()
app.title("Visitor Badge Printer")
app.geometry("400x400")

tk.Label(app, text="Visitor Name").pack()
name_entry = tk.Entry(app)
name_entry.pack()

tk.Label(app, text="Valid From (YYYY-MM-DD)").pack()
valid_from_entry = tk.Entry(app)
valid_from_entry.insert(0, datetime.date.today().isoformat())
valid_from_entry.pack()

tk.Label(app, text="Valid To (YYYY-MM-DD)").pack()
valid_to_entry = tk.Entry(app)
valid_to_entry.insert(0, (datetime.date.today() + datetime.timedelta(days=1)).isoformat())
valid_to_entry.pack()

tk.Label(app, text="Host").pack()
host_entry = tk.Entry(app)
host_entry.pack()

supervised_var = tk.BooleanVar()
tk.Checkbutton(app, text="Supervised Visitor", variable=supervised_var).pack(pady=10)

def on_print():
    print_label(
        name=name_entry.get(),
        valid_from=valid_from_entry.get(),
        valid_to=valid_to_entry.get(),
        host=host_entry.get(),
        supervised="Yes" if supervised_var.get() else "No"
    )

tk.Button(app, text="Print Badge", command=on_print, bg="green", fg="white").pack(pady=20)

app.mainloop()
