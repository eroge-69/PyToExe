import os
import pandas as pd
import win32com.client as win32
from tkinter import Tk, filedialog

# --- Select invoices folder ---
def select_folder(title):
    root = Tk()
    root.withdraw()
    folder = filedialog.askdirectory(title=title)
    root.destroy()
    return folder

# --- Find PDFs for given companies ---
def find_pdfs_for_companies(base_folder, companies):
    pdf_files = []
    for company in companies:
        for subdir, _, files in os.walk(base_folder):
            for file in files:
                if company.lower() in file.lower() and file.lower().endswith(".pdf"):
                    full_path = os.path.join(subdir, file)
                    pdf_files.append(full_path)
    return pdf_files

# --- Create email draft in Outlook ---
def create_email_draft(to_emails, subject, body, attachments):
    outlook = win32.Dispatch("Outlook.Application")
    mail = outlook.CreateItem(0)
    mail.To = "; ".join(to_emails)
    mail.Subject = subject
    mail.Body = body
    for file_path in attachments:
        mail.Attachments.Add(file_path)
    mail.Save()

# --- Main script ---
def main():
    print("Select the folder containing the invoices (with Results subfolder)")
    base_folder = select_folder("Select the main invoices folder")
    base_folder_name = os.path.basename(base_folder)
    results_folder = os.path.join(base_folder, "Results")

    print("Select the Excel file (Final_Email_Format_List.xlsx)")
    email_list_path = filedialog.askopenfilename(title="Select Final_Email_Format_List.xlsx",
                                                 filetypes=[("Excel Files", "*.xlsx")])
    df = pd.read_excel(email_list_path)
    df['Companies'] = df['Company'].astype(str).str.split('\n')
    df['Emails'] = df['Email'].astype(str).str.split('\n')

    for index, row in df.iterrows():
        companies = [c.strip() for c in row['Companies'] if c.strip()]
        emails = [e.strip() for e in row['Emails'] if e.strip()]
        pdfs = find_pdfs_for_companies(results_folder, companies)

        if not pdfs:
            print(f"⚠️ No PDFs found for companies: {', '.join(companies)}")
            continue

        company_label = ", ".join(companies)
        subject = f"{company_label} - Invoices for {base_folder_name}"
        body = f"Hello,\n\nPlease find attached the invoices for {base_folder_name}.\n\nBest regards,"

        print(f"✅ Creating draft for: {company_label} to {', '.join(emails)} ({len(pdfs)} attachments)")
        create_email_draft(emails, subject, body, pdfs)

    print("🎉 All drafts created.")

if __name__ == "__main__":
    main()
