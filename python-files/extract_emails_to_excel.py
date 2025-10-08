import re
import os
import fitz  # PyMuPDF for PDF reading
import pandas as pd
from datetime import datetime

def extract_messages_from_pdf(pdf_path):
    """Extracts structured email data from an OurFamilyWizard-style PDF."""
    with fitz.open(pdf_path) as doc:
        text = ""
        for page in doc:
            text += page.get_text("text")

    # Split messages by the 'Sent:' marker
    parts = re.split(r"\nSent: ", text)
    messages = []

    for part in parts[1:]:  # skip anything before first 'Sent:'
        try:
            # Extract headers
            sent_match = re.match(r"(\d{2}/\d{2}/\d{4}) at ([0-9:]+ [APM]+)", part)
            from_match = re.search(r"From:\s*(.+)", part)
            to_match = re.search(r"To:\s*(.+)", part)
            subject_match = re.search(r"Subject:\s*(.+)", part)

            if not sent_match:
                continue

            date, time = sent_match.groups()
            sender = from_match.group(1).strip() if from_match else ""
            recipient = to_match.group(1).strip() if to_match else ""
            subject = subject_match.group(1).strip() if subject_match else ""

            # Body starts after Subject
            body_start = part.find("Subject:")
            if body_start != -1:
                body = part[body_start:].split("\n", 1)[1] if "\n" in part[body_start:] else ""
            else:
                body = ""
            # Flatten multi-line text into a single paragraph
            body = re.sub(r"\s+", " ", body).strip()

            messages.append({
                "Date": date,
                "Time": time,
                "Sender": sender,
                "Recipient": recipient,
                "Subject": subject,
                "Message Body": body
            })
        except Exception:
            continue

    return messages


def main():
    folder = os.getcwd()
    all_messages = []

    for file in os.listdir(folder):
        if file.lower().endswith(".pdf"):
            print(f"Processing {file} ...")
            all_messages.extend(extract_messages_from_pdf(os.path.join(folder, file)))

    # Sort messages chronologically
    for msg in all_messages:
        try:
            msg["DateTime"] = datetime.strptime(f"{msg['Date']} {msg['Time']}", "%m/%d/%Y %I:%M %p")
        except Exception:
            msg["DateTime"] = None

    df = pd.DataFrame(all_messages)
    df = df.sort_values(by="DateTime", ascending=True).drop(columns=["DateTime"])

    output_path = os.path.join(folder, "combined_email_report.xlsx")
    df.to_excel(output_path, index=False)
    print(f"\n✅ Done! Saved as: {output_path}")

if __name__ == "__main__":
    main()
