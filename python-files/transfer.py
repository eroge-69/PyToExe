import os
import pandas as pd
from pypdf import PdfReader, PdfWriter
from pypdf.generic import NameObject
from datetime import date
from tkinter import Tk, Label, Button, filedialog, StringVar, Entry

# --- GUI Setup ---
root = Tk()
root.title("Select Files & Folder for PDF Processing")
root.geometry("600x400")

pdf_var = StringVar(value="❌ No PDF template selected")
excel_var = StringVar(value="❌ No Excel file selected")
folder_var = StringVar(value="❌ No output folder selected")
finance_date_var = StringVar()
exec_date_var = StringVar()

def choose_pdf():
    path = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
    if path:
        pdf_var.set(path)

def choose_excel():
    path = filedialog.askopenfilename(filetypes=[("Excel Files", "*.xlsx;*.xls")])
    if path:
        excel_var.set(path)

def choose_folder():
    path = filedialog.askdirectory()
    if path:
        folder_var.set(path)

def continue_process():
    if pdf_var.get().startswith("❌") or excel_var.get().startswith("❌") or folder_var.get().startswith("❌"):
        Label(root, text="⚠ Please select all three paths!", fg="red").pack()
        return
    if not finance_date_var.get() or not exec_date_var.get():
        Label(root, text="⚠ Please enter both dates!", fg="red").pack()
        return
    root.destroy()  # Closes the GUI

# --- Buttons and Labels ---
Label(root, text="Step 1: Choose PDF Template").pack()
Label(root, textvariable=pdf_var).pack()
Button(root, text="Choose PDF", command=choose_pdf).pack(pady=5)

Label(root, text="Step 2: Choose Excel File").pack()
Label(root, textvariable=excel_var).pack()
Button(root, text="Choose Excel", command=choose_excel).pack(pady=5)

Label(root, text="Step 3: Choose Output Folder").pack()
Label(root, textvariable=folder_var).pack()
Button(root, text="Choose Folder", command=choose_folder).pack(pady=5)

# --- Step 4: Date inputs ---
Label(root, text="Step 4: Finance Committee Action Date (MM/DD/YYYY)").pack()
finance_entry = Entry(root, textvariable=finance_date_var, width=12)
finance_entry.pack(pady=2)

Label(root, text="Step 5: Executive Council Action Date (MM/DD/YYYY)").pack()
exec_entry = Entry(root, textvariable=exec_date_var, width=12)
exec_entry.pack(pady=2)

# ✅ Continue button
Button(root, text="Continue", command=continue_process, bg="green", fg="white").pack(pady=10)

root.mainloop()  # Waits until the GUI is closed

# --- After GUI closes ---
template_pdf = pdf_var.get()
location = excel_var.get()
output_folder = folder_var.get()
finance_date = finance_date_var.get()
exec_date = exec_date_var.get()

print("PDF:", template_pdf)
print("Excel:", location)
print("Output Folder:", output_folder)
print("Finance Committee Date:", finance_date)
print("Executive Council Date:", exec_date)

# --- Read Excel ---
data = pd.read_excel(location)
entries = len(data)

# --- Function to extract REQID info ---
def REQIDT(REQ):
    withdrawals, deposits = [], []
    from_, to_, desc, date1, Name_ = {}, {}, "", "", ""
    totalw_ = 0
    totald_ = 0
    for i in range(entries):
        if data.at[i, "REQID"] == REQ:
            type_ = data.at[i, "Withdrawal?"]
            desc = data.at[i, "Description"]
            date1 = data.at[i, "Date Made"].strftime("%m/%d/%y") if pd.notna(data.at[i, "Date Made"]) else ""
            Name_ = data.at[i, "Activity Name"]
            Account_ = data.at[i, "Account Name"]
            if type_:
                withdrawals.append([str(data.at[i, "Account"]), str(data.at[i, "Activity"]), str(data.at[i, "Amount"])] )
                if Account_ in from_:
                    from_[Account_].append(data.at[i, "ActName"])
                else:
                    from_[Account_] = [data.at[i, "ActName"]]
                totalw_ += data.at[i, "Amount"]
            else:
                deposits.append([str(data.at[i, "Account"]), str(data.at[i, "Activity"]), str(data.at[i, "Amount"])] )
                if Account_ in to_:
                    to_[Account_].append(data.at[i, "ActName"])
                else:
                    to_[Account_] = [data.at[i, "ActName"]]
                totald_ += data.at[i, "Amount"]
    return withdrawals, from_, to_, deposits, desc, date1, Name_, totalw_, totald_

# --- Process each REQID ---
unique_ids = data["REQID"].drop_duplicates().tolist()

for req_id in unique_ids:
    withdrawals, from_, to_, deposits, desc, date1, Name_, totalw_, totald_ = REQIDT(req_id)
    fromlines_ = "".join(f"({k}; {', '.join(v)}) " for k, v in from_.items())
    tolines_ = "".join(f"({k}; {', '.join(v)}) " for k, v in to_.items())

    reader = PdfReader(template_pdf)
    writer = PdfWriter()

    for page in reader.pages:
        writer.add_page(page)

    if "/AcroForm" in reader.trailer["/Root"]:
        writer._root_object[NameObject("/AcroForm")] = reader.trailer["/Root"]["/AcroForm"]

    fields = reader.get_fields()
    if fields:
        if "Finance Committee Action" in fields:
            writer.update_page_form_field_values(writer.pages[0], {"Finance Committee Action": finance_date})
        if "Executive Council Action" in fields:
            writer.update_page_form_field_values(writer.pages[0], {"Executive Council Action": exec_date})
        if "Date" in fields:
            writer.update_page_form_field_values(writer.pages[0], {"Date": f"{date.today().strftime('%m/%d/%Y')}"} )
        if "Document" in fields:
            writer.update_page_form_field_values(writer.pages[0], {"Document": req_id})
        if "From" in fields:
            writer.update_page_form_field_values(writer.pages[0], {"From": fromlines_})
        if "To" in fields:
            writer.update_page_form_field_values(writer.pages[0], {"To": tolines_})
        if "AmountTotal" in fields:
            writer.update_page_form_field_values(writer.pages[0], {"AmountTotal": f"${totalw_:,.2f}"})
        if "AmountTotal_2" in fields:
            writer.update_page_form_field_values(writer.pages[0], {"AmountTotal_2": f"${totald_:,.2f}"})
        if "Reason" in fields:
            writer.update_page_form_field_values(writer.pages[0], {"Reason": desc})

        for idx, withdrawrow in enumerate(withdrawals, start=1):
            amount = float(withdrawrow[2])
            writer.update_page_form_field_values(writer.pages[0], {f"ObjectRow{idx}": withdrawrow[0]})
            writer.update_page_form_field_values(writer.pages[0], {f"ActivityRow{idx}": withdrawrow[1]})
            writer.update_page_form_field_values(writer.pages[0], {f"AmountRow{idx}": f"${amount:,.2f}"})

        for idx, depositrow in enumerate(deposits, start=1):
            amount = float(depositrow[2])
            writer.update_page_form_field_values(writer.pages[0], {f"ObjectRow{idx}_2": depositrow[0]})
            writer.update_page_form_field_values(writer.pages[0], {f"ActivityRow{idx}_2": depositrow[1]})
            writer.update_page_form_field_values(writer.pages[0], {f"AmountRow{idx}_2": f"${amount:,.2f}"})

    safe_name = "".join(c for c in Name_ if c.isalnum() or c in (" ", "_", "-"))
    output_file = os.path.join(output_folder, f"{date.today().strftime('%m-%d-%Y')} {safe_name}.pdf")
    with open(output_file, "wb") as f:
        writer.write(f)
    print("PDF filled:", output_file)
