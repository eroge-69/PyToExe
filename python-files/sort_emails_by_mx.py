
import os
import re
import csv
import dns.resolver
import tkinter as tk
from tkinter import filedialog, messagebox
from collections import defaultdict

def extract_emails(text):
    email_pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
    return re.findall(email_pattern, text)

def get_mx_record(domain):
    try:
        answers = dns.resolver.resolve(domain, 'MX', lifetime=5)
        sorted_answers = sorted(answers, key=lambda x: x.preference)
        return str(sorted_answers[0].exchange).rstrip('.')
    except Exception:
        return "MX lookup failed"

def main():
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(
        title="Select your email list file (.txt or .csv)",
        filetypes=[("Text files", "*.txt"), ("CSV files", "*.csv")]
    )

    if not file_path:
        messagebox.showinfo("Cancelled", "No file selected.")
        return

    with open(file_path, "r", encoding="utf-8") as file:
        content = file.read()

    emails = extract_emails(content)
    domains = set(email.split("@")[1] for email in emails)
    domain_mx_map = {domain: get_mx_record(domain) for domain in domains}

    mx_email_map = defaultdict(list)
    for email in emails:
        domain = email.split("@")[1]
        mx_record = domain_mx_map.get(domain, "Unknown")
        mx_email_map[mx_record].append(email)

    output_path = os.path.join(os.path.dirname(file_path), "sorted_by_mx.csv")
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["MX Record", "Email"])
        for mx, email_list in mx_email_map.items():
            for email in email_list:
                writer.writerow([mx, email])

    messagebox.showinfo("Done", f"Sorted emails saved to:
{output_path}")

if __name__ == "__main__":
    main()
