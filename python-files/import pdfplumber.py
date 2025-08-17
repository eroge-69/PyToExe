import pdfplumber
import re
import math
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet
from openpyxl import Workbook
import uuid

# -----------------------------
# Step 1: Extract Housing Loan Rules
# -----------------------------
def extract_housing_rules(pdf_path):
    rules = {
        "FOIR": {},
        "LTV": {},
        "ROI": {"NonCRE": {}, "CRE": {}},  # Separate ROI tables
        "MaxTenureYears": 30
    }
    
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"

    # ---- FOIR ----
    foir_pattern = r"Upto Rs\.?(\d+(?:\.\d+)?)\s*Lakh.*?(\d+)%"
    foir_matches = re.findall(foir_pattern, text, re.IGNORECASE)
    for income, percent in foir_matches:
        income_val = float(income) * 100000
        rules["FOIR"][income_val] = int(percent)/100
    if "70%" in text:
        rules["FOIR"]["above"] = 0.70

    # ---- LTV ----
    ltv_pattern = r"Upto Rs\.?\s*(\d+)\s*lakhs?.*?(\d+)%"
    ltv_matches = re.findall(ltv_pattern, text, re.IGNORECASE)
    for loan, ltv in ltv_matches:
        loan_val = float(loan) * 100000
        rules["LTV"][loan_val] = int(ltv)/100
    if not rules["LTV"]:
        rules["LTV"] = {3000000:0.8, 7500000:0.8, "above":0.75}
    
    # ---- ROI ----
    roi_pattern = r"(Non[- ]?CRE|CRE).*?CIC.*?(\d+)\s*-\s*(\d+).*?(\d+\.\d+)%"
    roi_matches = re.findall(roi_pattern, text, re.IGNORECASE)
    for scheme, start, end, roi in roi_matches:
        scheme_type = "NonCRE" if "NON" in scheme.upper() else "CRE"
        rules["ROI"][scheme_type][(int(start), int(end))] = float(roi)/100

    roi_above_pattern = r"(Non[- ]?CRE|CRE).*?CIC.*?Above\s*(\d+).*?(\d+\.\d+)%"
    roi_above_matches = re.findall(roi_above_pattern, text, re.IGNORECASE)
    for scheme, score, roi in roi_above_matches:
        scheme_type = "NonCRE" if "NON" in scheme.upper() else "CRE"
        rules["ROI"][scheme_type][("above", int(score))] = float(roi)/100
    
    return rules, text[:2000]

# -----------------------------
# Step 2: EMI Helper
# -----------------------------
def reverse_emi(max_emi, annual_rate, tenure_years):
    r = annual_rate / 12
    n = tenure_years * 12
    loan = max_emi * ((1 + r)**n - 1) / (r * (1 + r)**n)
    return loan

# -----------------------------
# Step 3: Pick ROI
# -----------------------------
def get_applicable_roi(rules, cic_score, scheme_type="NonCRE", repo_rate=0.065,
                       is_woman=False, is_staff=False, is_defence=False):
    roi_slab = None
    scheme_rules = rules["ROI"].get(scheme_type, {})
    
    for band, roi in scheme_rules.items():
        if isinstance(band, tuple) and len(band) == 2:  # e.g. (700,749)
            if band[0] <= cic_score <= band[1]:
                roi_slab = roi
        elif isinstance(band, tuple) and band[0] == "above":
            if cic_score >= band[1]:
                roi_slab = roi
    if roi_slab is None:
        roi_slab = 0.02  # fallback spread
    
    # Final ROI = Repo + Spread
    roi_final = repo_rate + roi_slab
    
    # Concessions
    if is_woman:
        roi_final -= 0.0005   # 0.05%
    if is_staff:
        roi_final -= 0.005    # 0.50%
    if is_defence:
        roi_final -= 0.0025   # 0.25%
    
    return max(roi_final, 0.0)  # never negative

# -----------------------------
# Step 4: Loan Eligibility
# -----------------------------
def housing_loan_eligibility(rules, monthly_income, existing_emi, property_value,
                             tenure_years, cic_score, scheme_type="NonCRE",
                             is_woman=False, is_staff=False, is_defence=False,
                             repo_rate=0.065):
    annual_income = monthly_income * 12
    
    # FOIR check
    foir = 0.5
    for slab, perc in rules["FOIR"].items():
        if slab != "above" and annual_income <= slab:
            foir = perc
            break
        foir = rules["FOIR"].get("above", foir)
    
    # EMI capacity
    max_emi_allowed = (annual_income * foir / 12) - existing_emi
    
    # ROI
    roi = get_applicable_roi(rules, cic_score, scheme_type, repo_rate,
                             is_woman, is_staff, is_defence)
    
    # Loan eligibility from EMI
    eligible_loan = reverse_emi(max_emi_allowed, roi, min(tenure_years, rules["MaxTenureYears"]))
    
    # LTV check
    ltv_limit = 0.8
    for slab, perc in rules["LTV"].items():
        if slab != "above" and eligible_loan <= slab:
            ltv_limit = perc
            break
        ltv_limit = rules["LTV"].get("above", ltv_limit)
    
    ltv_cap = property_value * ltv_limit
    final_eligibility = min(eligible_loan, ltv_cap)
    
    return {
        "AnnualIncome": annual_income,
        "MonthlyIncome": monthly_income,
        "ExistingEMI": existing_emi,
        "FOIR_Applied": f"{int(foir*100)}%",
        "MaxEMIAllowed": round(max_emi_allowed, 2),
        "ROI_Applied": round(roi*100, 2),
        "SchemeType": scheme_type,
        "WomanBorrower": is_woman,
        "StaffConcession": is_staff,
        "DefenceConcession": is_defence,
        "EligibleLoanBeforeLTV": round(eligible_loan, 2),
        "LTVCap": round(ltv_cap, 2),
        "FinalEligibleLoan": round(final_eligibility, 2),
        "TenureYears": min(tenure_years, rules["MaxTenureYears"])
    }

# -----------------------------
# Step 5: Export Report to PDF (Enhanced)
# -----------------------------
def export_to_pdf(result, borrower_info=None, filename="eligibility_report.pdf"):
    doc = SimpleDocTemplate(filename, pagesize=A4)
    elements = []
    styles = getSampleStyleSheet()

    # Unique Ref No + Date
    ref_no = f"PNB/KPG/{datetime.now().year}/{str(uuid.uuid4())[:6].upper()}"
    date_str = datetime.now().strftime("%d-%m-%Y")

    elements.append(Paragraph("🏦 Punjab National Bank", styles["Title"]))
    elements.append(Paragraph(f"Reference No: {ref_no}", styles["Normal"]))
    elements.append(Paragraph(f"Date: {date_str}", styles["Normal"]))
    elements.append(Spacer(1, 20))

    elements.append(Paragraph("Housing Loan Eligibility Report", styles["Title"]))
    elements.append(Spacer(1, 20))

    # Borrower Info
    if borrower_info:
        elements.append(Paragraph("<b>Borrower Details:</b>", styles["Heading2"]))
        borrower_data = [["Field", "Value"]]
        for k, v in borrower_info.items():
            borrower_data.append([k, str(v)])
        
        b_table = Table(borrower_data, colWidths=[200, 250])
        b_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#7D0039")),  # PNB maroon
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("ALIGN", (0, 0), (-1, -1), "LEFT"),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("BACKGROUND", (0, 1), (-1, -1), colors.whitesmoke),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ]))
        elements.append(b_table)
        elements.append(Spacer(1, 20))

    # Eligibility Results
    elements.append(Paragraph("<b>Eligibility Results:</b>", styles["Heading2"]))
    data = [["Field", "Value"]]
    for k, v in result.items():
        data.append([k, str(v)])

    table = Table(data, colWidths=[200, 250])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#FFB81C")),  # PNB yellow
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("BACKGROUND", (0, 1), (-1, -1), colors.whitesmoke),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    elements.append(table)
    elements.append(Spacer(1, 20))

    # Footer note
    elements.append(Paragraph(
        "Note: This is a system-generated eligibility report based on current PNB credit policy. "
        "Final sanction is subject to verification of documents and discretion of the bank.",
        styles["Normal"]
    ))

    doc.build(elements)
    print(f"✅ PDF report saved as {filename}")

# -----------------------------
# Step 6: Export Report to Excel
# -----------------------------
def export_to_excel(result, filename="eligibility_report.xlsx"):
    wb = Workbook()
    ws = wb.active
    ws.title = "Eligibility Report"

    ws.append(["Field", "Value"])
    for k, v in result.items():
        ws.append([k, v])

    for cell in ws["1:1"]:
        cell.font = cell.font.copy(bold=True)
    
    wb.save(filename)
    print(f"✅ Excel report saved as {filename}")

# -----------------------------
# Step 7: Example Run
# -----------------------------
if __name__ == "__main__":
    pdf_path = "CREDIT RETAIL PNB.pdf"
    rules, preview = extract_housing_rules(pdf_path)
    
    borrower_info = {
        "Name": "Mr. Neel Subba",
        "Age": "32",
        "Occupation": "Salaried - Defence",
        "Loan Purpose": "Purchase of Residential House",
        "Branch": "PNB Kalimpong"
    }

    customer_data = {
        "monthly_income": 80000,
        "existing_emi": 10000,
        "property_value": 5000000,
        "tenure_years": 25,
        "cic_score": 745,
        "scheme_type": "NonCRE",
        "is_woman": False,
        "is_staff": False,
        "is_defence": True,
        "repo_rate": 0.065
    }
    
    result = housing_loan_eligibility(rules, **customer_data)
    
    export_to_pdf(result, borrower_info, "housing_eligibility_report.pdf")
    export_to_excel(result, "housing_eligibility_report.xlsx")
