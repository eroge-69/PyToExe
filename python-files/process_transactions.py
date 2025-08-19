import os
import sys
import pandas as pd
from tkinter import Tk, filedialog
import xml.etree.ElementTree as ET

def parse_xml_file(xml_file):
    """
    Parses the specific XML structure described in the prompt and returns a DataFrame.
    Each <devicePayments> entry is treated as a transaction row (positive).
    Each <fees> entry is treated as a transaction row (negative, using total_sum_with_vat).
    """
    tree = ET.parse(xml_file)
    root = tree.getroot()

    # Get general info from <row> attributes
    row_attrs = root.attrib
    company_name = row_attrs.get("company_name", "")
    report_start = row_attrs.get("reimbursement_start_date", "")
    # Use only date part
    date_str = report_start.split("T")[0] if report_start else ""

    transactions = []

    # Device Payments (positive amounts, 2 decimals)
    for dp in root.findall("devicePayments"):
        amount = dp.attrib.get('total_sum', '')
        try:
            amount = f"{float(amount):.2f}"
        except Exception:
            amount = amount
        trans = {
            "Person": company_name,
            "Date": date_str,
            "Amount": amount,
            "Payee": dp.attrib.get("billing_provider", ""),
            "Description": f"{dp.attrib.get('payment_method_descr', '')} ({dp.attrib.get('recognition_descr', '')})",
            "Reference": "",
            "Check Number": dp.attrib.get("entity_id", "")
        }
        transactions.append(trans)

    # Fees (negative amounts, use total_sum_with_vat, 2 decimals)
    for fee in root.findall("fees"):
        amount = fee.attrib.get('total_sum_with_vat', '')
        try:
            amount = f"-{float(amount):.2f}"
        except Exception:
            amount = f"-{amount}"
        trans = {
            "Person": company_name,
            "Date": date_str,
            "Amount": amount,
            "Payee": "",
            "Description": fee.attrib.get('fee_type_descr', ''),
            "Reference": "",
            "Check Number": ""
        }
        transactions.append(trans)

    return pd.DataFrame(transactions)

def main():
    # Hide the root window of Tkinter
    root = Tk()
    root.withdraw()
    input_file = filedialog.askopenfilename(
        title="Select Transaction Report file (CSV, Excel, or XML)",
        filetypes=[
            ("CSV/Excel/XML files", "*.csv;*.xls;*.xlsx;*.xml"),
            ("CSV files", "*.csv"),
            ("Excel files", "*.xls;*.xlsx"),
            ("XML files", "*.xml"),
            ("All files", "*.*")
        ]
    )
    if not input_file or not os.path.isfile(input_file):
        print("File not found or no file selected.")
        return

    ext = os.path.splitext(input_file)[1].lower()
    if ext in ['.xls', '.xlsx']:
        df = pd.read_excel(input_file, skiprows=1, dtype={'FIN.TRANSACTION AMOUNT': str})
    elif ext == '.csv':
        df = pd.read_csv(input_file, skiprows=1, low_memory=False, dtype={'FIN.TRANSACTION AMOUNT': str})
    elif ext == '.xml':
        df = parse_xml_file(input_file)
    else:
        print("Unsupported file type.")
        return

    # If XML, skip the rest of the processing and just output the file
    if ext == '.xml':
        input_dir = os.path.dirname(input_file)
        output_dir = os.path.join(input_dir, "individual_transactions")
        os.makedirs(output_dir, exist_ok=True)
        for person, group in df.groupby('Person'):
            out_df = group[['Date', 'Amount', 'Payee', 'Description', 'Reference', 'Check Number']].copy()
            filename = os.path.join(output_dir, f"{person.replace(' ', '_')}_transactions.csv")
            out_df.to_csv(filename, index=False)
            print(f"Created: {filename}")
        return

    # Combine last and first name for a unique person identifier
    df['Person'] = df['ACC.LAST NAME'].str.title().str.strip() + " " + df['ACC.FIRST NAME'].str.title().str.strip()

    # Prepare output columns
    df['Date'] = df['FIN.TRANSACTION DATE']
    # Parse Date as datetime for correct sorting
    df['Date_dt'] = pd.to_datetime(df['Date'], dayfirst=False, errors='coerce')

    def clean_amount_with_string_formatting(val):
        """
        Formats a value as a string with two decimal places, always negative unless a credit is detected.
        """
        if pd.isna(val) or not str(val).strip():
            return ''
        s = str(val).strip()

        # Handle negative sign if present
        is_negative = s.startswith('-')
        if is_negative:
            s = s[1:]

        # Remove all leading zeros
        s = s.lstrip('0')
        if not s or s == '.':
            s = '0'
        if s.startswith('.'):
            s = '0' + s

        # Convert to float and format with two decimals
        try:
            num = float(s)
            formatted = f"{num:.2f}"
        except ValueError:
            return ''

        # If original value was negative, output as +, else as -
        if is_negative:
            result = f"+{formatted}"
        else:
            result = f"-{formatted}"
        return result

    df['Amount'] = df['FIN.TRANSACTION AMOUNT'].apply(clean_amount_with_string_formatting)

    # Fill any remaining NaN values in other columns with empty strings
    df['Payee'] = df['MCH.MERCHANT NAME'].fillna('')
    df['Description'] = df['FIN.EXPENSE DESCRIPTION'].fillna('') + df['FIN.ADJUSTMENT DESCRIPTION'].fillna('')
    df['Reference'] = df['FIN.TRANSACTION REFERENCE NUMBER']
    df['Check Number'] = df['ACC.ACCOUNT NUMBER']

    # Create output folder in the same directory as the input file
    input_dir = os.path.dirname(input_file)
    output_dir = os.path.join(input_dir, "individual_transactions")
    os.makedirs(output_dir, exist_ok=True)

    for person, group in df.groupby('Person'):
        # Sort by parsed date ascending
        group = group.sort_values('Date_dt').reset_index(drop=True)
        out_df = group[['Date', 'Amount', 'Payee', 'Description', 'Reference', 'Check Number']].copy()
        filename = os.path.join(output_dir, f"{person.replace(' ', '_')}_transactions.csv")
        out_df.to_csv(filename, index=False)
        print(f"Created: {filename}")

if __name__ == "__main__":
    main()