import pdfplumber
import os
import openpyxl

# Folder where your PDFs are stored
folder = r"C:\Users\msalaheldin\Desktop\Mohamed Salah\Library\smart excel\collect data from diff word files to excel\pdf file"  # <-- change this path

# Prepare Excel file
wb = openpyxl.Workbook()
ws = wb.active
ws.append(["File Name", "Interface Title", "Cluster", "Discipline", "Coordinates", "Originator", "Interface Partner", "Issue Date"])

for filename in os.listdir(folder):
    if filename.lower().endswith(".pdf"):
        path = os.path.join(folder, filename)
        with pdfplumber.open(path) as pdf:
            text = ""
            # Only read first 5 pages
            for i in range(min(5, len(pdf.pages))):
                page_text = pdf.pages[i].extract_text()
                if page_text:
                    text += page_text + "\n"

        def get_between(txt, start, end):
            try:
                s = txt.index(start) + len(start)
                e = txt.index(end, s)
                return txt[s:e].strip()
            except ValueError:
                return ""

        ws.append([
            filename,
            get_between(text, "Interface Title:", "Region"),
            get_between(text, "Cluster:", "Partner Cluster:"),
            get_between(text, "Discipline:", "Current Project Stage:"),
            get_between(text, "Identify Stage:", "Interface Leader:"),
            get_between(text, "Originator/Leader:", "Interface Partner:"),
            get_between(text, "Interface Partner:", "Issue Date:"),
get_between(text, "Issue Date:", "Revision:")
        ])

# Save output Excel
wb.save(r"C:\Users\msalaheldin\Desktop\Mohamed Salah\Library\smart excel\collect data from diff word files to excel\Extracted_PDF_Data.xlsx")
print("✅ Extraction complete. Saved as Extracted_PDF_Data.xlsx")