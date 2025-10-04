import re
import os
import fitz  # PyMuPDF
import camelot
import pandas as pd
from datetime import datetime
import json
from tkinter import Tk, filedialog, messagebox


# ----------------------------
# Helper function to format dates
# ----------------------------
def format_date(date_str):
    """Convert dd/mm/yyyy or dd-mm-yyyy → yyyy-mm-ddT00:00:00."""
    try:
        dt = datetime.strptime(date_str.strip(), "%d/%m/%Y")
        return dt.strftime("%Y-%m-%dT00:00:00")
    except Exception:
        try:
            dt = datetime.strptime(date_str.strip(), "%d-%m-%Y")
            return dt.strftime("%Y-%m-%dT00:00:00")
        except Exception:
            return date_str.strip()


# ----------------------------
# Remove special characters from item description
# ----------------------------
def remove_special_characters(text: str) -> str:
    return re.sub(r'[^A-Za-z0-9 ]+', '', text)


# ----------------------------
# Clean invoice number
# ----------------------------
def clean_invoice_number(invoice_no: str) -> str:
    return invoice_no.replace("/", "-")


# ----------------------------
# Convert amount to INR
# ----------------------------
def convert_to_inr(amount, rate=86.20):
    try:
        return round(float(amount) * rate, 2)
    except:
        return 0.0


# ----------------------------
# Extract text from PDF
# ----------------------------
def extract_text_from_pdf(pdf_path):
    try:
        doc = fitz.open(pdf_path)
        text = ''
        for page in doc:
            text += page.get_text()
        doc.close()
        return text
    except Exception as e:
        print(f"Error extracting text from {pdf_path}: {e}")
        return ""


# ----------------------------
# Extract tables from PDF using Camelot
# ----------------------------
def extract_tables_from_pdf(pdf_path):
    try:
        tables = camelot.read_pdf(pdf_path, flavor='lattice', pages='all')
        return [table.df for table in tables]
    except Exception as e:
        print(f"Lattice mode failed: {e}. Trying stream mode...")
        try:
            tables = camelot.read_pdf(pdf_path, flavor='stream', pages='all', strip_text='\n')
            return [table.df for table in tables]
        except Exception as e:
            print(f"Stream mode failed: {e}")
            return []


# ----------------------------
# Extract invoice details from text
# ----------------------------
def extract_invoice_details(text: str):
    info = {}

    # Invoice number
    number_match = re.search(
        r"(?:Invoice\s*No\.?|Inv\.?\s*No\.?|Bill\s*No\.?)\s*[:\-]?\s*([A-Z]{0,3}[0-9]+(?:[/\-]\d+)+)",
        text,
        re.IGNORECASE
    )
    if number_match:
        invoice_no = number_match.group(1).strip()
    else:
        pattern = re.findall(r"\b[A-Z]{1,3}/\d+(?:/\d+)*(?:-\d+)?\b", text)
        invoice_no = pattern[-1] if pattern else ""
    info["InvoiceNo"] = clean_invoice_number(invoice_no)

    # LUT Date
    lut_match = re.search(r"LUT NO\.: .* Dt\. (\d{2}/\d{2}/\d{4})", text)
    info["LUT_Date"] = format_date(lut_match.group(1)) if lut_match else ""

    # Invoice Date (last date in text)
    all_dates = re.findall(r"\b\d{2}/\d{2}/\d{4}\b", text)
    info["Invoice_Date"] = format_date(all_dates[-1]) if all_dates else ""

    # Total amount (last numeric amount with decimals, remove commas)
    amount_matches = re.findall(r'[\d,]+\.\d{2}', text)
    total_amount = float(amount_matches[-1].replace(",", "")) if amount_matches else 0.0
    info["Total"] = total_amount

    return info


# ----------------------------
# Extract items from text and tables
# ----------------------------
def extract_items(text, tables):
    items = []

    # Regex extraction from text
    item_pattern = r'(\d+)\n([^\n]+)\n(\d+|Pcs\.)\n([\d,]+\.\d{2})\n([\d,]+(?:\.\d+)?|\d+)\n([\d,]+\.\d{2})\n'
    matches = re.finditer(item_pattern, text)
    for match in matches:
        items.append({
            'number': match.group(1),
            'description': match.group(2),
            'pcs': match.group(3) if match.group(3) != 'Pcs.' else '1',
            'amount': match.group(4).replace(",", ""),
            'rate': match.group(5).replace(",", ""),
            'cts': match.group(6).replace(",", ""),
            'hsCode': "71049900",
            'igstAmount': "0"
        })

    # Fallback to tables if few items found
    if len(items) < 1:
        for table in tables:
            headers = [str(col).strip() for col in table.iloc[0]]
            if any(h in headers for h in ['Description of Goods', 'Quantity', 'Rate', 'Amount']):
                item_started = False
                prev_description = ''
                for index, row in table.iterrows():
                    row_values = [str(val).strip().replace('\n', ' ') if pd.notna(val) else '' for val in row]
                    if any(h in row_values for h in ['Description of Goods', 'Quantity', 'Rate', 'Amount']):
                        item_started = True
                        continue
                    if item_started and re.match(r'^\d+$', row_values[0]):
                        description = row_values[1] if len(row_values) > 1 else prev_description
                        pcs = row_values[2] if len(row_values) > 2 else '0'
                        rate = row_values[3].replace(",", "") if len(row_values) > 3 else '0'
                        amount = row_values[4].replace(",", "") if len(row_values) > 4 else '0'
                        items.append({
                            'number': row_values[0],
                            'description': remove_special_characters(description),
                            'pcs': pcs,
                            'rate': rate,
                            'amount': amount,
                            'hsCode': "71049900",
                            'igstAmount': "0"
                        })
                        prev_description = description

    items.sort(key=lambda x: int(x['number']))
    return items


# ----------------------------
# Process PDF file
# ----------------------------
def process_pdf(pdf_path):
    if not os.path.exists(pdf_path):
        print(f"File not found: {pdf_path}")
        return {}

    text = extract_text_from_pdf(pdf_path)
    tables = extract_tables_from_pdf(pdf_path)

    invoice_info = extract_invoice_details(text)
    invoice_items = extract_items(text, tables)
    invoice_info['items'] = invoice_items

    return invoice_info


# ----------------------------
# Convert extracted data to JSON format with INR amounts
# ----------------------------
def pdf_to_json(pdf_path):
    invoice_info = process_pdf(pdf_path)

    # Convert total amount to INR
    total_inr = convert_to_inr(invoice_info.get("Total", 0))

    generalDetails = {
        "sezUnitCode": "BOM6Z026",
        "sezUnitName": "KIARA JEWELLERY PRIVATE LIMITED",
        "sezIecCode": "0305038508",
        "sezUnitAddress": "SEEPZ SEZ",
        "sezCity": "MUMBAI",
        "sezState": "Maharashtra",
        "sezPinCode": "400096",
        "sezGstin": "27AACCK4789M1ZT",
        "dtaUnitGstin": "27AACCG1529K1ZL",
        "dtaUnitPan": "",
        "dtaUnitName": "HARI DARSHAN EXPORTS PVT LTD",
        "dtaUnitAddressLine1": "FC/4070, F TOWER, 4TH FLOOR,BANDRA (E),",
        "dtaUnitCity": "MUMBAI",
        "dtaUnitState": "Maharashtra",
        "dtaUnitPinCode": "400051",
        "dtaIecCode": "",
        "typeOfDtaUnit": "F",
        "igstDeclaration": "LUT",
        "lutNumber": "AD270325180645V",
        "lutDate": invoice_info.get("LUT_Date", ""),
        "areDetailsToBeFilled": "N",
        "areNumber": "",
        "areDate": None,
        "range": None,
        "division": None,
        "address": None,
        "commissionerate": None,
        "dutyAmountAsPerAre": None,
        "availingFacilityOfCenvatCreditUnderCenvatCreditRules": None,
        "availingFacilityUnderNotification41": None,
        "availingFacilityUnderNotification43": None,
        "generalRemarks": ""
    }

    invoiceDetails = [
        {
            "invoiceNumber": invoice_info.get("InvoiceNo", ""),
            "invoiceValue": round(total_inr),
            "invoiceValueInr": round(total_inr),
            "invoiceDate": invoice_info.get("Invoice_Date", ""),
            "natureOfTransaction": "Sale",
            "natureOfSupply": "Supply under LUT",
            "invoiceCurrency": "INR",
            "exchangeRate": "86.20",
            "igstAmount": str(convert_to_inr(0)),
            "cessAmount": "0.00",
            "dutyAmountasPer": None,
            "invoiceFileIrn": "",
            "invoiceFileName": "",
            "incoterm": "",
            "freight": "",
            "insurance": "",
            "discount": "",
            "commission": "",
            "otherDeduction": "",
            "fobValue":""
        }
    ]

    main_description = ""
    if invoice_info.get("items"):
        main_description = remove_special_characters(invoice_info["items"][0].get("description", ""))

    # ✅ Changed quantity from pcs → cts (Carats)
    quantity_sum = sum(float(item.get("cts", "0")) for item in invoice_info.get("items", []))

    # ✅ Extended unit price to 9 decimal places
    unit_price_inr = round(total_inr / quantity_sum, 9) if quantity_sum else 0
    hs_code_match = re.search(r"HSN\s*CODE\s*[:\-]?\s*(\d{6,10})", extract_text_from_pdf(pdf_path), re.IGNORECASE)
    hs_code = hs_code_match.group(1) if hs_code_match else "N/A"

    itemDetails = [
        {
            "invoiceNumber": invoice_info.get("InvoiceNo", ""),
            "invoiceDate": invoice_info.get("Invoice_Date", ""),
            "itemDescription": main_description,
            "quantity": str(quantity_sum),  # Quantity in Carats
            "unitPrice": f"{unit_price_inr:.9f}",  # 9 decimal precision
            "productValue": round(total_inr),
            "unitOfMeasurement": "CTM",  # Changed from INR → CTM
            "presentMarketValue": 0,
            "itemAccessories": "",
             "hsCode": hs_code,  # Dynamically extracted
            "rebateClaimed": None,
            "itemType": "Raw Material",
            "taxableValue": round(total_inr),
            "igstNotificationNumber": "001-2017",
            "igstNotificationSerialNumber": "VI3",
            "isGstExempt": "N",
            "igstRate": 0.25,
            "igstAmount": str(convert_to_inr(0)),
            "cessNotificationNumber": "",
            "cessNotificationSerialNumber": "",
            "cessRate": 0.0,
            "cessAmount": "0.00"
        }
    ]

    final_json = {
        "generalDetailsRequest": generalDetails,
        "invoiceDetailsRequest": invoiceDetails,
        "itemDetailsRequest": itemDetails
    }

    return final_json


# ----------------------------
# Main with File Dialogs
# ----------------------------
if __name__ == "__main__":
    root = Tk()
    root.withdraw()  # Hide the main Tkinter window

    # Ask user to select PDF file
    pdf_file = filedialog.askopenfilename(
        title="Select PDF Invoice File",
        filetypes=[("PDF files", "*.pdf")]
    )

    if not pdf_file:
        messagebox.showerror("Error", "No PDF file selected.")
        exit()

    # Process PDF and convert to JSON
    output_json = pdf_to_json(pdf_file)

    # Ask user where to save the JSON file
    save_path = filedialog.asksaveasfilename(
        title="Save JSON Output",
        defaultextension=".json",
        filetypes=[("JSON files", "*.json")]
    )

    if save_path:
        with open(save_path, "w") as f:
            json.dump(output_json, f, indent=2)
        messagebox.showinfo("Success", f"JSON saved successfully at:\n{save_path}")
    else:
        messagebox.showwarning("Cancelled", "JSON save cancelled.")
