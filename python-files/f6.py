import tkinter as tk
from tkinter import messagebox, filedialog, Toplevel, Button
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from datetime import datetime
import csv

# ----------- CONFIG -----------
CREDENTIALS = {"admin": "password"}
BANK_CODE_MAP = {
    "810": "Union Bank of India",
    "1": "State Bank of India",
    "3": "Punjab National Bank",
    "4": "HDFC Bank",
    "5": "ICICI Bank",
    "6": "Axis Bank",
    "7": "Bank of Baroda",
    "8": "Canara Bank",
    "9": "IDBI Bank",
    "10": "Yes Bank"
}

uploaded_cheques = []

# ----------- CSV PROCESSING -----------
def process_csv_file(file_path):
    global uploaded_cheques
    uploaded_cheques = []
    try:
        with open(file_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                bank_code = row.get("Bank Name", "").strip()
                row["Bank Name"] = BANK_CODE_MAP.get(bank_code, "Unknown Bank")
                uploaded_cheques.append(row)
    except Exception as e:
        messagebox.showerror("❌ Error", f"Failed to read file:\n{str(e)}")

# ----------- REPORT: Union Summary -----------
def generate_union_bank_summary():
    union_cheques = [row for row in uploaded_cheques if row["Bank Name"] == "Union Bank of India"]
    grouped = {}
    for row in union_cheques:
        key = (row["Cheque No"], row["Cheque Date"])
        grouped.setdefault(key, {"amount": 0, "micr": row["Bank Branch Code"]})
        grouped[key]["amount"] += float(row["Cheque Amount"])

    file_path = filedialog.asksaveasfilename(
        initialfile=f"UBI_CHQ_{datetime.today().strftime('%d%b%Y')}.pdf",
        defaultextension=".pdf", filetypes=[("PDF Files", "*.pdf")]
    )
    if not file_path: return

    c = canvas.Canvas(file_path, pagesize=A4)
    width, height = A4
    c.setFont("Helvetica-Bold", 14)
    c.drawCentredString(width/2, height - 50, "BHARAT SANCHAR NIGAM LIMITED")
    c.setFont("Helvetica", 12)
    c.drawCentredString(width/2, height - 70, "CHEQUE MANAGEMENT SYSTEM")
    c.setFont("Helvetica", 10)
    c.drawString(50, height - 90, "BANK A/C NO – 509201010036**")
    c.drawRightString(width - 50, height - 90, f"DATE OF DEPOSIT: {datetime.today().strftime('%d-%b-%Y')}")

    y = height - 120
    c.setFont("Helvetica-Bold", 10)
    c.drawString(50, y, "SL NO")
    c.drawString(90, y, "BANK NAME")
    c.drawString(200, y, "CHEQUE NO")
    c.drawString(300, y, "CHEQUE DATE")
    c.drawRightString(460, y, "AMOUNT")
    c.drawString(470, y, "MICR CODE")
    y -= 20

    sl, total_amount = 1, 0
    for (chq_no, chq_date), data in grouped.items():
        if y < 100: c.showPage(); y = height - 100
        c.setFont("Helvetica", 10)
        c.drawString(50, y, str(sl))
        c.drawString(90, y, "Union Bank of India")
        c.drawString(200, y, chq_no)
        c.drawString(300, y, chq_date)
        c.drawRightString(460, y, f"{data['amount']:.2f}")
        c.drawString(470, y, data["micr"])
        total_amount += data["amount"]
        sl += 1
        y -= 20

    y -= 20
    c.setFont("Helvetica-Bold", 10)
    c.drawString(50, y, f"Total No. of Cheques: {sl - 1}")
    c.drawRightString(width - 50, y, f"Total Amount: ₹ {total_amount:.2f}")
    y -= 30
    c.setFont("Helvetica-Oblique", 8)
    c.drawCentredString(width/2, y, f"Developed by Shekhar | Generated on {datetime.now().strftime('%d-%b-%Y %H:%M:%S')}")
    c.save()
    messagebox.showinfo("✅ PDF Generated", f"Saved to:\n{file_path}")

# ----------- REPORT: Payslips (Cheque style) -----------
def generate_union_payslips():
    union_cheques = [row for row in uploaded_cheques if row["Bank Name"] == "Union Bank of India"]
    grouped = {}
    for row in union_cheques:
        key = (row["Cheque No"], row["Cheque Date"])
        grouped.setdefault(key, {"amount": 0, "micr": row["Bank Branch Code"]})
        grouped[key]["amount"] += float(row["Cheque Amount"])

    file_path = filedialog.asksaveasfilename(
        initialfile=f"UBI_PAYSLIP_{datetime.today().strftime('%d%b%Y')}.pdf",
        defaultextension=".pdf", filetypes=[("PDF Files", "*.pdf")]
    )
    if not file_path:
        return

    c = canvas.Canvas(file_path, pagesize=A4)
    width, height = A4

    for (chq_no, chq_date), data in grouped.items():
        for i, copy_type in enumerate(["BANK COPY", "BSNL COPY"]):
            y_offset = height - 60 - i * (height // 2)

            c.setFont("Helvetica-Bold", 12)
            c.drawCentredString(width/2, y_offset, "BHARAT SANCHAR NIGAM LIMITED")
            c.setFont("Helvetica", 11)
            c.drawCentredString(width/2, y_offset - 20, "UNION BANK CHEQUE PAYSLIP")

            c.setFont("Helvetica-Bold", 9)
            c.drawString(50, y_offset - 45, f"Copy: {copy_type}")

            c.setFont("Helvetica", 9)
            c.drawString(50, y_offset - 65, f"Cheque No: {chq_no}")
            c.drawString(300, y_offset - 65, f"Cheque Date: {chq_date}")
            c.drawString(50, y_offset - 85, "Bank: Union Bank of India")
            c.drawString(300, y_offset - 85, f"MICR Code: {data['micr']}")
            c.drawString(50, y_offset - 105, f"Amount: ₹ {data['amount']:.2f}")
            c.drawString(300, y_offset - 105, "Deposit A/C: 509201010036**")

            c.setFont("Helvetica-Oblique", 8)
            c.drawString(50, y_offset - 130, f"Signature: ______________________")
            c.drawString(300, y_offset - 130, f"Date: {datetime.today().strftime('%d-%b-%Y')}")

        c.setFont("Helvetica-Oblique", 7)
        c.drawCentredString(width/2, 30, f"Developed by Shekhar | Generated on {datetime.now().strftime('%d-%b-%Y %H:%M:%S')}")
        c.showPage()

    c.save()
    messagebox.showinfo("✅ Payslips PDF Generated", f"Saved to:\n{file_path}")

# ----------- REPORT: Other Bank Summary -----------
def generate_other_bank_summary():
    other_cheques = [row for row in uploaded_cheques if row["Bank Name"] != "Union Bank of India"]
    grouped = {}
    for row in other_cheques:
        key = (row["Cheque No"], row["Cheque Date"], row["Bank Name"])
        grouped.setdefault(key, {"amount": 0, "micr": row["Bank Branch Code"]})
        grouped[key]["amount"] += float(row["Cheque Amount"])

    file_path = filedialog.asksaveasfilename(
        initialfile=f"OTHERS_CHQ_{datetime.today().strftime('%d%b%Y')}.pdf",
        defaultextension=".pdf", filetypes=[("PDF Files", "*.pdf")]
    )
    if not file_path: return

    c = canvas.Canvas(file_path, pagesize=A4)
    width, height = A4
    c.setFont("Helvetica-Bold", 14)
    c.drawCentredString(width/2, height - 50, "BHARAT SANCHAR NIGAM LIMITED")
    c.setFont("Helvetica", 12)
    c.drawCentredString(width/2, height - 70, "CHEQUE MANAGEMENT SYSTEM")
    c.setFont("Helvetica", 10)
    c.drawString(50, height - 90, "BANK A/C NO – 509201010036**")
    c.drawRightString(width - 50, height - 90, f"DATE OF DEPOSIT: {datetime.today().strftime('%d-%b-%Y')}")

    y = height - 120
    c.setFont("Helvetica-Bold", 10)
    c.drawString(50, y, "SL NO")
    c.drawString(90, y, "BANK NAME")
    c.drawString(200, y, "CHEQUE NO")
    c.drawString(300, y, "CHEQUE DATE")
    c.drawRightString(460, y, "AMOUNT")
    c.drawString(470, y, "MICR CODE")
    y -= 20

    sl, total_amount = 1, 0
    for (chq_no, chq_date, bank), data in grouped.items():
        if y < 100: c.showPage(); y = height - 100
        c.setFont("Helvetica", 10)
        c.drawString(50, y, str(sl))
        c.drawString(90, y, bank)
        c.drawString(200, y, chq_no)
        c.drawString(300, y, chq_date)
        c.drawRightString(460, y, f"{data['amount']:.2f}")
        c.drawString(470, y, data["micr"])
        total_amount += data["amount"]
        sl += 1
        y -= 20

    y -= 20
    c.setFont("Helvetica-Bold", 10)
    c.drawString(50, y, f"Total No. of Cheques: {sl - 1}")
    c.drawRightString(width - 50, y, f"Total Amount: ₹ {total_amount:.2f}")
    y -= 30
    c.setFont("Helvetica-Oblique", 8)
    c.drawCentredString(width / 2, y, f"Developed by Shekhar | Generated on {datetime.now().strftime('%d-%b-%Y %H:%M:%S')}")
    c.save()
    messagebox.showinfo("✅ PDF Generated", f"Saved to:\n{file_path}")

# ----------- AFTER CSV UPLOAD WINDOW -----------
def show_cheque_options():
    win = Toplevel()
    win.title("🧾 Generate Cheque Reports")
    win.geometry("400x350")
    win.configure(bg="#fff8e1")

    tk.Label(win, text=f"⏰ {datetime.now().strftime('%d-%b-%Y %H:%M:%S')}", bg="#fff8e1", font=("Helvetica", 10, "italic")).pack(pady=5)
    Button(win, text="📄 Union Bank Summary PDF", command=generate_union_bank_summary, font=("Helvetica", 12, "bold"), bg="#4caf50", fg="white", width=30).pack(pady=10)
    Button(win, text="📑 Union Bank Payslips PDF", command=generate_union_payslips, font=("Helvetica", 12, "bold"), bg="#2196f3", fg="white", width=30).pack(pady=10)
    Button(win, text="📊 Other Banks Summary PDF", command=generate_other_bank_summary, font=("Helvetica", 12, "bold"), bg="#ff9800", fg="white", width=30).pack(pady=10)
    Button(win, text="❌ Close", command=win.destroy, font=("Helvetica", 11), bg="#d32f2f", fg="white", width=15).pack(pady=15)

# ----------- FILE UPLOAD TRIGGER -----------
def upload_csv():
    file_path = filedialog.askopenfilename(title="Select CSV File", filetypes=[("CSV Files", "*.csv")])
    if file_path:
        process_csv_file(file_path)
        messagebox.showinfo("✅ Success", "CSV uploaded successfully 😊")
        show_cheque_options()
    else:
        messagebox.showwarning("⚠️ Cancelled", "No file selected.")

# ----------- LOGIN + DASHBOARD -----------
def dashboard_window():
    dashboard = tk.Tk()
    dashboard.title("📊 BSNL Cheque Dashboard")
    dashboard.geometry("600x400")
    dashboard.configure(bg="#e3f2fd")

    tk.Label(dashboard, text=f"⏰ {datetime.now().strftime('%d-%b-%Y %H:%M:%S')}", bg="#e3f2fd", font=("Helvetica", 10, "italic")).pack(anchor="ne", padx=10, pady=5)
    tk.Label(dashboard, text="📋 Cheque Management Dashboard", font=("Helvetica", 18, "bold"), fg="#0d47a1", bg="#e3f2fd").pack(pady=40)
    tk.Button(dashboard, text="📁 Upload CSV File", command=upload_csv, font=("Helvetica", 13, "bold"), bg="#43a047", fg="white", width=25).pack(pady=15)
    tk.Button(dashboard, text="❌ Exit Application", command=dashboard.destroy, font=("Helvetica", 13, "bold"), bg="#e53935", fg="white", width=25).pack(pady=10)
    dashboard.mainloop()

def login():
    username = username_entry.get()
    password = password_entry.get()
    if username in CREDENTIALS and CREDENTIALS[username] == password:
        messagebox.showinfo("✅ Login Successful", "🎉 Welcome to the Cheque Management System!")
        root.destroy()
        dashboard_window()
    else:
        messagebox.showerror("🚫 Login Failed", "❌ Invalid credentials.")
        username_entry.delete(0, tk.END)
        password_entry.delete(0, tk.END)

root = tk.Tk()
root.title("📡 BSNL Cheque Management System")
root.geometry("500x400")
root.configure(bg="#f0f4ff")
tk.Label(root, text="📡 Bharat Sanchar Nigam Limited", font=("Helvetica", 20, "bold"), fg="#1a237e", bg="#f0f4ff").pack(pady=(30, 5))
tk.Label(root, text="🧾 Cheque Management System", font=("Helvetica", 14), fg="#37474f", bg="#f0f4ff").pack(pady=(0, 20))

tk.Label(root, text="👤 Username:", font=("Helvetica", 12), bg="#f0f4ff").pack(pady=(10, 5))
username_entry = tk.Entry(root, font=("Helvetica", 12), width=30)
username_entry.pack()
tk.Label(root, text="🔒 Password:", font=("Helvetica", 12), bg="#f0f4ff").pack(pady=(10, 5))
password_entry = tk.Entry(root, show="*", font=("Helvetica", 12), width=30)
password_entry.pack()

tk.Button(root, text="🔐 Login", command=login, font=("Helvetica", 12, "bold"), bg="#1e88e5", fg="white", width=20).pack(pady=20)
tk.Button(root, text="❌ Exit", command=root.destroy, font=("Helvetica", 10), bg="#b71c1c", fg="white", width=10).pack()
root.mainloop()
