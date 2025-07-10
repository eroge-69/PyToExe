import os
import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
from bs4 import BeautifulSoup

def extract_failed_checkpoints(report_file):
    with open(report_file, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")
    table = soup.find_all("tr")
    failed = []
    for row in table:
        cells = row.find_all("td")
        if len(cells) == 4 and "Failed" in cells[2].text:
            failed.append(cells[0].text.strip())
    return failed

def determine_ubs_level(failed):
    LEVEL_1 = ["Document tagging", "Natural language", "Metadata and settings"]
    LEVEL_2 = LEVEL_1 + ["PDF syntax", "Alternative description", "Table tagging"]
    LEVEL_3 = LEVEL_2 + ["Fonts", "Structure tree", "Role mapping"]
    LEVEL_4 = LEVEL_3 + ["PDF/UA identifier"]

    for level, checks in zip([4,3,2,1], [LEVEL_4, LEVEL_3, LEVEL_2, LEVEL_1]):
        if all(check not in failed for check in checks):
            return f"Level {level}"
    return "Below Level 1"

def process_reports():
    folder = filedialog.askdirectory(title="Select Folder Containing PAC HTML Reports")
    if not folder:
        return

    rows = []
    for file in os.listdir(folder):
        if file.endswith(".html"):
            path = os.path.join(folder, file)
            failed = extract_failed_checkpoints(path)
            level = determine_ubs_level(failed)
            rows.append({
                "Filename": file,
                "Failed Checkpoints": ", ".join(failed),
                "UBS Level": level
            })

    if not rows:
        messagebox.showinfo("Done", "No valid PAC reports found.")
        return

    df = pd.DataFrame(rows)
    output_path = os.path.join(folder, "UBS_PAC_Report.xlsx")
    df.to_excel(output_path, index=False)
    messagebox.showinfo("Success", f"Report saved to: {output_path}")

# GUI Setup
root = tk.Tk()
root.title("UBS PAC Report Generator")
root.geometry("400x200")
root.resizable(False, False)

label = tk.Label(root, text="📁 UBS PAC Tool – Batch Report Generator", font=("Arial", 12, "bold"))
label.pack(pady=20)

btn = tk.Button(root, text="Select Report Folder & Generate Excel", font=("Arial", 10), command=process_reports)
btn.pack(pady=10)

root.mainloop()