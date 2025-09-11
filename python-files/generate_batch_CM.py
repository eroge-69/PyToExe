import pandas as pd
import xml.etree.ElementTree as ET
from xml.dom import minidom
from datetime import datetime
import uuid
import sys

# === Configuratie ===
input_file = "payments.xlsx"
sheet_name = 0
output_dir = "."
amount_limit = 10000.00
master_list_file = "iban_debtor_list.xlsx"

# === IBAN validatie ===
def is_valid_iban(iban: str) -> bool:
    iban = iban.replace(" ", "").upper()
    if len(iban) < 15 or len(iban) > 34:
        return False
    if not iban[:2].isalpha() or not iban[2:4].isdigit():
        return False
    rearranged = iban[4:] + iban[:4]
    numeric_iban = ""
    for ch in rearranged:
        if ch.isdigit():
            numeric_iban += ch
        elif ch.isalpha():
            numeric_iban += str(ord(ch) - 55)
        else:
            return False
    return int(numeric_iban) % 97 == 1

# === Masterlijst inlezen ===
try:
    master_df = pd.read_excel(master_list_file)
except Exception as e:
    sys.exit(f"❌ Fout bij inlezen masterlijst: {e}")

# Filter alleen actieve combinaties
master_df = master_df[master_df["Status"].str.lower() == "actief"]

# === Batch inlezen ===
try:
    df = pd.read_excel(input_file, sheet_name=sheet_name)
except Exception as e:
    sys.exit(f"❌ Fout bij inlezen batch Excel: {e}")

required_columns = ["IBAN_own", "DebtorName", "IBAN_client", "Name_client", "Description", "Amount", "ExecutionDate"]
for col in required_columns:
    if col not in df.columns:
        sys.exit(f"❌ Vereiste kolom ontbreekt in Excel: {col}")

# === Hard validatie per regel ===
for idx, row in df.iterrows():
    rownum = idx + 2
    for col in ["IBAN_own", "DebtorName", "IBAN_client", "Name_client", "Description", "Amount"]:
        if pd.isna(row[col]) or str(row[col]).strip() == "":
            sys.exit(f"❌ Fout in regel {rownum}: kolom '{col}' is leeg.")

    # Controle IBAN_own en DebtorName tegen masterlijst
    match = master_df[
        (master_df["IBAN_own"].str.replace(" ", "") == str(row["IBAN_own"]).replace(" ", "")) &
        (master_df["DebtorName"].str.strip() == str(row["DebtorName"]).strip())
    ]
    if match.empty:
        sys.exit(f"❌ Fout in regel {rownum}: combinatie IBAN_own '{row['IBAN_own']}' en DebtorName '{row['DebtorName']}' niet toegestaan volgens masterlijst.")

    # IBAN_validatie
    if not is_valid_iban(str(row["IBAN_own"])):
        sys.exit(f"❌ Fout in regel {rownum}: IBAN_own '{row['IBAN_own']}' ongeldig.")
    if not is_valid_iban(str(row["IBAN_client"])): 
        sys.exit(f"❌ Fout in regel {rownum}: IBAN_client '{row['IBAN_client']}' ongeldig.")

    # Bedrag
    try:
        amount = float(row["Amount"])
    except ValueError:
        sys.exit(f"❌ Fout in regel {rownum}: bedrag '{row['Amount']}' is geen getal.")
    if amount <= 0:
        sys.exit(f"❌ Fout in regel {rownum}: bedrag '{amount}' moet groter zijn dan 0.")
    if amount > amount_limit:
        sys.exit(f"❌ Fout in regel {rownum}: bedrag '{amount}' overschrijdt limiet € {amount_limit:,.2f}.")

    # Lengtecheck omschrijving (Ustrd)
    if len(str(row["Description"])) > 140:
        sys.exit(f"❌ Fout in regel {rownum}: omschrijving langer dan 140 tekens.")

# === Uniformiteit IBAN_own en DebtorName ===
if df["IBAN_own"].nunique() != 1:
    sys.exit(f"❌ Alle regels moeten dezelfde IBAN_own hebben, gevonden: {df['IBAN_own'].unique()}")
if df["DebtorName"].nunique() != 1:
    sys.exit(f"❌ Alle regels moeten dezelfde DebtorName hebben, gevonden: {df['DebtorName'].unique()}")

iban_own = str(df["IBAN_own"].iloc[0]).replace(" ", "")
debtor_name = str(df["DebtorName"].iloc[0]).strip()

# Zoek bijbehorende BIC in masterlijst
bic_match = master_df[
    (master_df["IBAN_own"].str.replace(" ", "") == iban_own) &
    (master_df["DebtorName"].str.strip() == debtor_name)
]
if bic_match.empty:
    sys.exit(f"❌ Geen BIC gevonden voor IBAN_own '{iban_own}' en DebtorName '{debtor_name}'.")
bic_code = bic_match.iloc[0]["BIC"]

# === ExecutionDate validatie ===
exec_dates = df["ExecutionDate"].dropna().unique()
if len(exec_dates) > 1:
    sys.exit(f"❌ Alle regels moeten dezelfde ExecutionDate hebben, gevonden: {exec_dates}")

if len(exec_dates) == 1:
    try:
        exec_date = pd.to_datetime(exec_dates[0]).date()
    except Exception:
        sys.exit(f"❌ Ongeldige ExecutionDate: {exec_dates[0]}")
    if exec_date < datetime.today().date():
        sys.exit(f"❌ ExecutionDate mag niet in het verleden liggen: {exec_date}")
else:
    exec_date = datetime.today().date()

# === Automatisch naar eerstvolgende werkdag als weekend ===
if exec_date.weekday() == 5:  # zaterdag
    exec_date = exec_date + pd.Timedelta(days=2)
elif exec_date.weekday() == 6:  # zondag
    exec_date = exec_date + pd.Timedelta(days=1)

# === XML bouwen ===
ns = {"": "urn:iso:std:iso:20022:tech:xsd:pain.001.001.09"}
ET.register_namespace("", ns[""])
root = ET.Element("Document", xmlns=ns[""])
cstmrCdtTrfInitn = ET.SubElement(root, "CstmrCdtTrfInitn")

# Group Header
grpHdr = ET.SubElement(cstmrCdtTrfInitn, "GrpHdr")
ET.SubElement(grpHdr, "MsgId").text = str(uuid.uuid4())[:35]  # max 35 tekens
ET.SubElement(grpHdr, "CreDtTm").text = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
ET.SubElement(grpHdr, "NbOfTxs").text = str(len(df))
ET.SubElement(grpHdr, "CtrlSum").text = "{:.2f}".format(df["Amount"].sum())
initgPty = ET.SubElement(grpHdr, "InitgPty")
ET.SubElement(initgPty, "Nm").text = debtor_name

# Payment Information
pmtInf = ET.SubElement(cstmrCdtTrfInitn, "PmtInf")
ET.SubElement(pmtInf, "PmtInfId").text = str(uuid.uuid4())[:35]  # max 35 tekens
ET.SubElement(pmtInf, "PmtMtd").text = "TRF"
ET.SubElement(pmtInf, "BtchBookg").text = "true"
ET.SubElement(pmtInf, "NbOfTxs").text = str(len(df))
ET.SubElement(pmtInf, "CtrlSum").text = "{:.2f}".format(df["Amount"].sum())

# Payment Type Information
pmtTpInf = ET.SubElement(pmtInf, "PmtTpInf")
ET.SubElement(pmtTpInf, "InstrPrty").text = "NORM"
svcLvl = ET.SubElement(pmtTpInf, "SvcLvl")
ET.SubElement(svcLvl, "Cd").text = "SEPA"

# Required Execution Date
reqdExctnDt_elem = ET.SubElement(pmtInf, "ReqdExctnDt")
ET.SubElement(reqdExctnDt_elem, "Dt").text = exec_date.strftime("%Y-%m-%d")

# Debtor
dbtr = ET.SubElement(pmtInf, "Dbtr")
ET.SubElement(dbtr, "Nm").text = debtor_name
dbtrAcct = ET.SubElement(pmtInf, "DbtrAcct")
id_elem = ET.SubElement(dbtrAcct, "Id")
ET.SubElement(id_elem, "IBAN").text = iban_own
dbtrAgt = ET.SubElement(pmtInf, "DbtrAgt")
finInstnId = ET.SubElement(dbtrAgt, "FinInstnId")
ET.SubElement(finInstnId, "BICFI").text = bic_code
ET.SubElement(pmtInf, "ChrgBr").text = "SLEV"

# Transactions
for idx, row in df.iterrows():
    cdtTrfTxInf = ET.SubElement(pmtInf, "CdtTrfTxInf")
    pmtId = ET.SubElement(cdtTrfTxInf, "PmtId")
    endToEndId = f"PAY-{idx+1}"
    if len(endToEndId) > 35:
        sys.exit(f"❌ Fout in regel {idx+2}: EndToEndId langer dan 35 tekens.")
    ET.SubElement(pmtId, "EndToEndId").text = endToEndId

    amt = ET.SubElement(cdtTrfTxInf, "Amt")
    ET.SubElement(amt, "InstdAmt", Ccy="EUR").text = "{:.2f}".format(float(row["Amount"]))

    cdtr = ET.SubElement(cdtTrfTxInf, "Cdtr")
    ET.SubElement(cdtr, "Nm").text = str(row["Name_client"])

    cdtrAcct = ET.SubElement(cdtTrfTxInf, "CdtrAcct")
    id_elem = ET.SubElement(cdtrAcct, "Id")
    ET.SubElement(id_elem, "IBAN").text = str(row["IBAN_client"])

    rmtInf = ET.SubElement(cdtTrfTxInf, "RmtInf")
    desc = str(row["Description"])
    if len(desc) > 140:
        sys.exit(f"❌ Fout in regel {idx+2}: omschrijving langer dan 140 tekens.")
    ET.SubElement(rmtInf, "Ustrd").text = desc

# === XML pretty-print en opslaan ===
xml_str = ET.tostring(root, encoding='UTF-8')
parsed = minidom.parseString(xml_str)
pretty_xml = parsed.toprettyxml(indent="  ", encoding='UTF-8')

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
output_file = f"{output_dir}/payments_{timestamp}.xml"
with open(output_file, "wb") as f:
    f.write(pretty_xml)

print(f"✅ Batchbestand aangemaakt: {output_file}")
