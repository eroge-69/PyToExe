# -*- coding: utf-8 -*-
"""
Claim Auditor Standalone EXE (Categorized Report + Word Check + Excel Support)
"""

import multiprocessing
multiprocessing.freeze_support()

import pandas as pd
import os, difflib, subprocess, re
from datetime import datetime
from tkinter import Tk, filedialog, messagebox

# Save path
DESKTOP_PATH = os.path.join(os.path.expanduser("~"), "Desktop")
EXCEL_REPORT = os.path.join(DESKTOP_PATH, "Claim_Audit_Report.xlsx")

# Keywords and patterns
AMBIGUOUS_KEYWORDS = [
    # Vague/Generic
    "meeting", "event", "discussion", "briefing", "visit", "call", "catch-up", "check-in",
    "activity", "support", "session", "presentation", "talk", "forum", "prep", "roundtable",
    "gathering", "engagement", "interaction", "sharing", "interview", "orientation", "consultation",
    
    # Celebrations, Meals
    "dinner", "lunch", "tea", "snack", "supper", "refreshments", "celebration", "birthday",
    "farewell", "appreciation", "anniversary", "retreat", "party", "treat", "outing", "get-together",
    
    # Institutions
    "ntu", "nus", "university", "school", "campus", "hall", "department", "office", "faculty",
    "committee", "admin", "club", "society", "lab", "division", "center", "unit",
    
    # Internal processes
    "submission", "report", "document", "paperwork", "application", "approval", "printing",
    "copying", "scanning", "reimbursement", "invoice", "statement", "claims", "renewal", "subscription",
    
    # Placeholders
    "misc", "others", "etc", "general", "na", "n/a", "various", "to be advised", "tbd",
    "adhoc", "undefined", "ongoing", "follow-up", "unclear", "internal", "personal", "test",
    
    # Time-related
    "monthly", "weekly", "annual", "yearly", "q1", "q2", "q3", "q4", "quarterly",
    "semester", "term", "holiday", "leave", "vacation", "day off", "offsite",
    
    # Projects/Codes
    "project", "task", "initiative", "work", "phase", "program", "code", "batch", "pilot",
    "review", "check", "testing", "trial", "case", "plan", "setup"
]

MONTHS_PATTERN = re.compile(
    r'\b('
    r'(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec|'
    r'january|february|march|april|may|june|july|august|september|october|november|december)'
    r'[\s\-]?\d{2,4}'
    r'|\d{2,4}[\s\-]?'
    r'(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec|'
    r'january|february|march|april|may|june|july|august|september|october|november|december)'
    r')\b',
    re.IGNORECASE
)

DATE_PATTERN = re.compile(
    r'\b('
    r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}'            # 12/09/2023
    r'|\d{4}[/-]?\d{2}[/-]?\d{2}'               # 20231209
    r'|\d{2}[/-]?\d{2}[/-]?\d{4}'               # 12092023
    r'|\d{8}'                                   # 12092023
    r'|\d{1,2}\s*(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)'  # 12 Feb
    r'|\d{1,2}\s*(january|february|march|april|may|june|july|august|september|october|november|december)'
    r')\b',
    re.IGNORECASE
)

class Claim:
    def __init__(self, row):
        self.raw = row
        self.claim_id = str(row.get('Report Key', '')).strip()
        self.emp_id = str(row.get('Employee ID', '')).strip()
        self.employee = str(row.get('Employee', '')).strip()
        self.report_name = str(row.get('Report Name', '')).strip()
        self.cost_object = str(row.get('Cost Object Code', '')).strip()
        self.description = str(row.get('Purpose', '')).strip()
        try:
            self.date = datetime.strptime(str(row.get('Transaction Date', '')).strip(), '%Y-%m-%d')
        except:
            self.date = None
        try:
            self.amount = float(str(row.get('Approved Amount', '')).replace(',', '').strip())
        except:
            self.amount = None

class ClaimAuditor:
    def __init__(self, file_path):
        self.file_path = file_path
        self.claims = []
        self.flags = []

    def run_checks(self):
        if self.file_path.lower().endswith(".xlsx"):
            df = pd.read_excel(self.file_path)
        else:
            df = pd.read_csv(self.file_path)

        for i, row in enumerate(df.itertuples(index=False, name=None)):
            row_dict = dict(zip(df.columns, row))
            claim = Claim(row_dict)
            self.claims.append(claim)

            report_key = claim.claim_id or f"Row {i+1}"
            emp_id = claim.emp_id
            employee = claim.employee

            for key, value in row_dict.items():
                if pd.isna(value) or str(value).strip() == "":
                    self.flags.append((report_key, emp_id, employee, f"Missing value in column: '{key}'"))

            if claim.amount and claim.amount > 1000:
                self.flags.append((report_key, emp_id, employee, f"Large claim: ${claim.amount:.2f}"))

            if not claim.description.strip():
                self.flags.append((report_key, emp_id, employee, "Missing Purpose field"))

            # Name similarity
            if claim.report_name and claim.employee:
                if len(claim.report_name) > 5 and len(claim.employee) > 5:
                    ratio = difflib.SequenceMatcher(None, claim.report_name.lower(), claim.employee.lower()).ratio()
                    if ratio > 0.85:
                        self.flags.append((report_key, emp_id, employee,
                                           f"Report name similar to employee name (Score: {ratio:.2f})",
                                           claim.report_name, claim.description))

            # Word Check (purpose/report name)
            for field, content in [("Report Name", claim.report_name), ("Purpose", claim.description)]:
                text = content.lower()
                if any(kw in text for kw in AMBIGUOUS_KEYWORDS) or MONTHS_PATTERN.search(text) or DATE_PATTERN.search(text):
                    self.flags.append((report_key, emp_id, employee,
                                       f"Ambiguous {field} wording", claim.report_name, claim.description))

        self.generate_excel_report()

    def generate_excel_report(self):
        categorized = {
            "Large Claims": [],
            "Missing Purpose": [],
            "Missing Fields": [],
            "Name Similarity": [],
            "Ambiguous Wording": [],
            "Others": []
        }

        for flag in self.flags:
            if len(flag) == 6:
                claim_id, emp_id, employee, msg, report_name, purpose = flag
                if "Ambiguous" in msg:
                    categorized["Ambiguous Wording"].append((claim_id, emp_id, employee, msg, report_name, purpose))
                else:
                    categorized["Name Similarity"].append((claim_id, emp_id, employee, msg, report_name, purpose))
            else:
                claim_id, emp_id, employee, msg = flag
                if "Large claim" in msg:
                    categorized["Large Claims"].append((claim_id, emp_id, employee, msg))
                elif "Missing Purpose" in msg:
                    categorized["Missing Purpose"].append((claim_id, emp_id, employee, msg))
                elif "Missing value" in msg:
                    categorized["Missing Fields"].append((claim_id, emp_id, employee, msg))
                else:
                    categorized["Others"].append((claim_id, emp_id, employee, msg))

        with pd.ExcelWriter(EXCEL_REPORT, engine='openpyxl') as writer:
            for category, entries in categorized.items():
                if not entries:
                    continue
                if category in ["Name Similarity", "Ambiguous Wording"]:
                    df = pd.DataFrame(entries, columns=["Report Key", "Employee ID", "Employee", "Issue", "Report Name", "Purpose"])
                else:
                    df = pd.DataFrame(entries, columns=["Report Key", "Employee ID", "Employee", "Issue"])
                df.to_excel(writer, sheet_name=category[:31], index=False)

            # Summary Sheet
            summary_df = pd.DataFrame([
                {"Category": cat, "Flag Count": len(lst)}
                for cat, lst in categorized.items() if lst
            ])
            summary_df.to_excel(writer, sheet_name="Summary", index=False)

        try:
            os.startfile(EXCEL_REPORT)
        except AttributeError:
            try:
                subprocess.call(['open', EXCEL_REPORT])
            except:
                subprocess.call(['xdg-open', EXCEL_REPORT])

if __name__ == "__main__":
    root = Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(
        title="Please select the Spreadsheet to be analysed",
        filetypes=[("CSV or Excel files", "*.csv *.xlsx"), ("CSV files", "*.csv"), ("Excel files", "*.xlsx")]
    )

    if not file_path:
        messagebox.showinfo("Cancelled", "No file selected.")
        exit()

    try:
        auditor = ClaimAuditor(file_path)
        auditor.run_checks()
        messagebox.showinfo("Done", f"Audit complete!\nReport saved as:\n{EXCEL_REPORT}")
    except Exception as e:
        messagebox.showerror("Error", str(e))
