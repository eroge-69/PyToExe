import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
from datetime import datetime, timedelta
from bs4 import BeautifulSoup

# Predefined station list
stations = [
    "RUDRAPUR",
    "DELHI ANANDVIHAR and Back",
    "NAINITAL",
    "MUSSOORIE PICTURE PALACE and Back",
    "ROORKEE"
]

# Load HTML template
html_file_path = "Family Pass Print Slip.html"
with open(html_file_path, "r", encoding="utf-8") as f:
    soup = BeautifulSoup(f, "html.parser")

# GUI setup
root = tk.Tk()
root.title("Family Pass Editor")

# Entry: Pass No
tk.Label(root, text="New Pass No:").grid(row=0, column=0, sticky="w")
pass_no_var = tk.StringVar(value="FP0032683")
tk.Entry(root, textvariable=pass_no_var).grid(row=0, column=1, sticky="ew")

# Dropdown: From Station
tk.Label(root, text="From Station:").grid(row=1, column=0, sticky="w")
from_station_var = tk.StringVar()
from_dropdown = ttk.Combobox(root, textvariable=from_station_var, values=stations)
from_dropdown.grid(row=1, column=1, sticky="ew")
from_dropdown.set(stations[0])

# Dropdown: To Station
tk.Label(root, text="To Station:").grid(row=2, column=0, sticky="w")
to_station_var = tk.StringVar()
to_dropdown = ttk.Combobox(root, textvariable=to_station_var, values=stations)
to_dropdown.grid(row=2, column=1, sticky="ew")
to_dropdown.set(stations[1])

# Date Picker: Date of Issue / Valid From
tk.Label(root, text="Date of Issue / Pass Valid From:").grid(row=3, column=0, sticky="w")
date_var = tk.StringVar()
date_picker = DateEntry(root, textvariable=date_var, date_pattern='dd-mm-yyyy')
date_picker.grid(row=3, column=1, sticky="ew")

# Update function
def update_html():
    new_pass_no = pass_no_var.get().strip()
    from_station = from_station_var.get().strip()
    to_station = to_station_var.get().strip()
    base_date = datetime.strptime(date_var.get(), "%d-%m-%Y")
    date_of_issue = pass_valid_from = base_date.strftime("%d-%b-%Y").upper()
    pass_valid_to = (base_date + timedelta(days=30)).strftime("%d-%b-%Y").upper()

    # Update Office Copy
    soup.find(id="lblPassNoVal").string = new_pass_no
    soup.find(id="lblDateVal").string = date_of_issue
    soup.find(id="lblFrmStonVal").string = from_station
    soup.find(id="lblToStonVal").string = to_station
    soup.find(id="lblPassValidFrmVal").string = pass_valid_from
    soup.find(id="lblPassValidToVal").string = pass_valid_to

    # Update Employee Copy
    soup.find(id="lblPassNoValRJ").string = new_pass_no
    soup.find(id="lblDateValRJ").string = date_of_issue
    soup.find(id="lblFrmStonValRJ").string = from_station
    soup.find(id="lblToStonValRJ").string = to_station
    soup.find(id="lblPassValidFrmValRJ").string = pass_valid_from
    soup.find(id="lblPassValidToValRJ").string = pass_valid_to

    # Save updated HTML
    with open("Family Pass Print Slip - UPDATED.html", "w", encoding="utf-8") as f_out:
        f_out.write(str(soup))

    messagebox.showinfo("Success", "HTML file updated successfully!")

# Button
tk.Button(root, text="Update HTML", command=update_html).grid(row=4, column=0, columnspan=2, pady=15)

# Layout stretch
root.columnconfigure(1, weight=1)

root.mainloop()
