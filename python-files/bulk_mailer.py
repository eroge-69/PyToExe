import os
import re
import win32com.client as win32
import pandas as pd
import chardet
from tkinter import Tk, filedialog, messagebox, simpledialog

def send_bulk_emails():
    try:
        # --- 1. CHOOSE EXCEL FILE ---
        root = Tk()
        root.withdraw()
        excel_file = filedialog.askopenfilename(
            title="Select Excel File",
            filetypes=[("Excel Files", "*.xlsx;*.xls")]
        )
        if not excel_file:
            messagebox.showwarning("Cancelled", "No Excel file selected.")
            return

        # --- 2. CHOOSE HTML TEMPLATE ---
        html_file = filedialog.askopenfilename(
            title="Select HTML Template (Exported from Word as .html)",
            filetypes=[("HTML Files", "*.html;*.htm")]
        )
        if not html_file:
            messagebox.showwarning("Cancelled", "No HTML file selected.")
            return

        # --- SAFETY CHECK: Reject .docx ---
        if html_file.lower().endswith(".docx"):
            messagebox.showerror(
                "Invalid File",
                "You selected a Word file (.docx).\n\n"
                "Please open your Word file and save it as:\n"
                "  File → Save As → Web Page, Filtered (*.htm; *.html)\n\n"
                "Then select that .html file here."
            )
            return

        # --- 3. ASK FOR SUBJECT LINE ---
        subject_line = simpledialog.askstring("Email Subject", "Enter subject for the emails:")
        if not subject_line:
            messagebox.showwarning("Cancelled", "No subject entered.")
            return

        # --- 4. ASK FOR ATTACHMENTS (OPTIONAL) ---
        attachments_common = filedialog.askopenfilenames(
            title="Select Attachments (Optional - Cancel if none)"
        )
        attachments_common = list(attachments_common) if attachments_common else []

        # --- 5. READ EXCEL DATA ---
        df = pd.read_excel(excel_file, sheet_name=0, header=0)  # Use header row for column names

        # --- 6. READ HTML BODY (auto-detect encoding) ---
        with open(html_file, "rb") as f:
            raw_data = f.read()
            detected = chardet.detect(raw_data)
            file_encoding = detected["encoding"]

        try:
            email_body_template = raw_data.decode(file_encoding, errors="ignore")
        except Exception:
            email_body_template = raw_data.decode("utf-8", errors="ignore")

        # Find folder with images (Word usually creates "Template_files")
        img_folder = os.path.splitext(html_file)[0] + "_files"

        # --- 7. CONNECT TO OUTLOOK ---
        outlook = win32.Dispatch("Outlook.Application")

        # --- 8. LOOP THROUGH ROWS ---
        for i, row in df.iterrows():
            if "Email" not in df.columns:
                messagebox.showerror("Error", "Excel must have a column named 'Email'.")
                return

            email_id = str(row["Email"]).strip() if not pd.isna(row["Email"]) else ""

            if not email_id or "@" not in email_id:
                print(f"Skipped row {i+1}: Invalid or missing email ({email_id})")
                continue

            # Create a personalized copy of email body
            personalized_body = email_body_template

            # Replace placeholders {{COLUMN}} with values
            for col in df.columns:
                value = str(row[col]).strip() if not pd.isna(row[col]) else ""
                placeholder = "{{" + col.upper() + "}}"
                personalized_body = personalized_body.replace(placeholder, value)

            print(f"Row {i+1}: Sending to {email_id}")

            try:
                mail = outlook.CreateItem(0)

                mail.To = email_id
                mail.Subject = subject_line
                mail.HTMLBody = personalized_body

                # Handle embedded images
                if os.path.exists(img_folder):
                    img_tags = re.findall(r'src="([^"]+)"', personalized_body)
                    for img_file in set(img_tags):
                        img_path = os.path.join(img_folder, os.path.basename(img_file))
                        if os.path.exists(img_path):
                            attach = mail.Attachments.Add(img_path)
                            cid = os.path.basename(img_file)
                            attach.PropertyAccessor.SetProperty(
                                "http://schemas.microsoft.com/mapi/proptag/0x3712001F",
                                cid
                            )
                            personalized_body = personalized_body.replace(img_file, f"cid:{cid}")

                # Add global attachments
                for att in attachments_common:
                    if os.path.exists(att):
                        mail.Attachments.Add(att)

                mail.Send()
                print(f"Sent successfully to {email_id}")
            except Exception as e:
                print(f"Failed to send to {email_id}: {str(e)}")

        messagebox.showinfo("Done", "Email sending process completed!")

    except Exception as e:
        messagebox.showerror("Error", f"An error occurred:\n{str(e)}")

if __name__ == "__main__":
    send_bulk_emails()
