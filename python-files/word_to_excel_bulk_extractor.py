
import os
import re
import pandas as pd
from docx import Document
from datetime import datetime

def extract_value(keyword, text, pattern=None):
    if pattern:
        match = re.search(pattern, text)
        return match.group(1).strip() if match else ""
    for line in text.splitlines():
        if keyword in line:
            return line.split(":")[-1].strip()
    return ""

def process_word_files(folder_path):
    data = []
    for filename in os.listdir(folder_path):
        if filename.endswith(".docx"):
            filepath = os.path.join(folder_path, filename)
            try:
                doc = Document(filepath)
                full_text = "\n".join([p.text.strip() for p in doc.paragraphs if p.text.strip()])

                release_no = extract_value("رقم التصريح", full_text, r"رقم التصريح[:\s]*([\w\-]+)")
                description = extract_value("البنود", full_text)
                building_name = extract_value("إسم المبني", full_text)
                location = extract_value("المكان المحدد", full_text)
                date = extract_value("تاريخ التصريح", full_text, r"تاريخ التصريح[:\s]*([\d\-/]+)")
                status = "Approved"
                hyperlink = filename

                try:
                    formatted_date = datetime.strptime(date, "%d-%m-%Y").strftime("%Y-%m-%d")
                except:
                    formatted_date = date

                data.append({
                    "Release No.": release_no,
                    "Description": description,
                    "Building Name": building_name,
                    "location": location,
                    "Concrete type": "",
                    "Date": formatted_date,
                    "Status": status,
                    "Hyperlink": hyperlink
                })
            except Exception as e:
                print(f"Error processing {filename}: {e}")

    df = pd.DataFrame(data)
    output_file = os.path.join(folder_path, "Combined_Excel_Output.xlsx")
    df.to_excel(output_file, index=False)
    print(f"✅ Data extracted and saved to {output_file}")

# ضع هنا مسار الفولدر اللي فيه ملفات الورد
folder_path = "PUT_YOUR_FOLDER_PATH_HERE"
process_word_files(folder_path)
