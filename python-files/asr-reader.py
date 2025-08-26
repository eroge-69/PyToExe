import fitz  # PyMuPDF
import re

def extract_field(pattern, text, default="Not found"):
    match = re.search(pattern, text)
    return match.group(1).strip() if match else default

def generate_asr_summary(pdf_path, output_txt_path="asr_summary.txt"):
    doc = fitz.open(pdf_path)
    full_text = "".join(page.get_text() for page in doc)

    # General Info
    ccna = extract_field(r"CCNA\s+(\w+)", full_text)
    pon = extract_field(r"PON\s+(\w+)", full_text)
    version = extract_field(r"VER\s+(\w+)", full_text)
    req_type = extract_field(r"REQTYP\s+(\w+)", full_text)
    action = extract_field(r"ACT\s+(\w+)", full_text)
    quantity = extract_field(r"QTY\s+(\d+)", full_text)
    ban = extract_field(r"BAN\s+(\w+)", full_text)
    due_date = extract_field(r"DDD\s+([\d\-]+)", full_text)
    date_sent = extract_field(r"DTSENT\s+([\d\-]+-\d+PM)", full_text)

    # Billing Info
    billing_name = extract_field(r"BILLNM\s+(.+)", full_text)
    billing_contact = extract_field(r"BILLCON\s+(.+)", full_text)
    billing_phone = extract_field(r"TEL NO\s+(\d{3}-\d{3}-\d{4})", full_text)
    billing_email = extract_field(r"BILLCON_EMAIL\s+(\S+)", full_text)

    # Contact Info
    initiator = extract_field(r"INIT\s+(.+?)\nTEL NO\s+(\d{3}-\d{3}-\d{4})", full_text)
    initiator_email = extract_field(r"INIT EMAIL\s+(\S+)", full_text)
    location = extract_field(r"CITY\s+(.+?)\nSTATE\s+(.+?)\nZIP CODE\s+(\d+)", full_text)

    # Circuit Details
    nc_code = extract_field(r"NC\s+(\w+)", full_text)
    nci_code = extract_field(r"NCI\s+([\w\.]+)", full_text)
    sec_nci_code = extract_field(r"SECNCI\s+([\w\.]+)", full_text)

    nc_definition = "Switched Ethernet service configuration for EVPL (Ethernet Virtual Private Line)"
    nc_speed = "1 Gbps"
    nci_definition = "2-conductor LAN fiber interface with option A02. Used for 1 Gbps Ethernet over fiber"
    nci_speed = "1 Gbps"
    sec_nci_definition = "1 Gigabit Ethernet interface at the secondary location"
    sec_nci_speed = "1 Gbps"

    # Service Address
    customer_name = extract_field(r"EUNAME\s+(.+)", full_text)
    street_address = extract_field(r"STR\s+(\d+)", full_text)
    building = extract_field(r"BLDG\s+(.+)", full_text)
    floor = extract_field(r"FLR\s+(.+)", full_text)
    city = extract_field(r"CITY\s+(.+?)\nSTATE", full_text)
    state = extract_field(r"STATE\s+(.+?)\nZIP", full_text)
    zip_code = extract_field(r"ZIP\s+(\d+)", full_text)
    latitude = extract_field(r"LAT\s+([\d\.]+)", full_text)
    longitude = extract_field(r"LONG\s+([\d\.]+)", full_text)
    local_contact = extract_field(r"LCON\s+(.+)", full_text)
    local_phone = extract_field(r"ACTEL\s+(\d{3}-\d{3}-\d{4})", full_text)
    local_email = extract_field(r"LCON_EMAIL\s+(\S+)", full_text)
    alt_contact = extract_field(r"ALCON\s+(.+)", full_text)
    alt_phone = extract_field(r"ALCON_TEL\s+(\d{3}-\d{3}-\d{4})", full_text)
    alt_email = extract_field(r"ALCON_EMAIL\s+(\S+)", full_text)

    summary = f"""
GENERAL INFORMATION
-------------------
CCNA: {ccna}
PON: {pon}
Version: {version}
Request Type: {req_type}
Action: {action}
Quantity: {quantity}
BAN: {ban}
Requested Due Date: {due_date}
Date Sent: {date_sent}

BILLING INFORMATION
-------------------
Billing Name: {billing_name}
Billing Contact: {billing_contact}
Billing Phone: {billing_phone}
Billing Email: {billing_email}

CONTACT INFORMATION
-------------------
Initiator: {initiator}
Initiator Email: {initiator_email}
Location: {location}

CIRCUIT DETAILS
---------------
NC Code: {nc_code}
  Definition: {nc_definition}
  Speed: {nc_speed}
NCI Code: {nci_code}
  Definition: {nci_definition}
  Speed: {nci_speed}
Secondary NCI Code: {sec_nci_code}
  Definition: {sec_nci_definition}
  Speed: {sec_nci_speed}

SERVICE ADDRESS
---------------
Customer Name: {customer_name}
Street Address: {street_address} {building}, Floor {floor}
City/State/ZIP: {city}, {state} {zip_code}
Latitude/Longitude: {latitude} / {longitude}
Local Contact: {local_contact}
  Phone: {local_phone}
  Email: {local_email}
Alternate Contact: {alt_contact}
  Phone: {alt_phone}
  Email: {alt_email}
"""

    with open(output_txt_path, "w") as f:
        f.write(summary)
    print(f"ASR summary saved to {output_txt_path}")

# Example usage:
# generate_asr_summary("att asr example 5.pdf")
