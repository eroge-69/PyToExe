import pandas as pd
from datetime import datetime

data = {
    "Step No.": [1, 2, 3, 4, 5, 6, 7, 8],
    "Activity": [
        "Material Procurement & Planning",
        "Site Preparation & Safety",
        "Dismantling",
        "Panel Modifications",
        "Component Installation",
        "Wiring & Termination",
        "Testing & Verification",
        "Handover"
    ],
    "Details": [
        "• Finalize material list (CTs, PTs, MFM, lamps, wiring, fuses)\n• Raise PO, track delivery",
        "• Joint site walkthrough\n• Implement LOTO, safety boards, PPE",
        "• Remove old CTs/VDI\n• Clear outdated wiring",
        "• Cut MFM/RYB lamp holes\n• Modify busbar for new CT/PT",
        "• Mount CTs/PTs\n• Install MFM and lamps",
        "• Terminate CT/PT to MFM\n• Wire lamps with fuses, label cables",
        "• Continuity/IR tests\n• Verify MFM readings, lamp indicators",
        "• Customer inspection\n• Submit test reports, as-built drawings"
    ],
    "Responsible Team": [
        "Procurement Team", "Site Engineers", "Electrical Team", 
        "Technical Team", "Installation Team", "Electricians", 
        "QA/QC Team", "Project Manager"
    ],
    "Target Date": [datetime.today().strftime("%d/%m/%Y")] * 8,
    "Status": ["Pending"] + ["Not Started"] * 7
}

df = pd.DataFrame(data)
with pd.ExcelWriter("Professional_Site_Execution_Plan.xlsx") as writer:
    df.to_excel(writer, index=False, sheet_name="Execution Plan")
    workbook = writer.book
    worksheet = writer.sheets["Execution Plan"]
    
    # Format headers
    header_format = workbook.add_format({
        "bold": True, "bg_color": "#4472C4", "font_color": "white", 
        "border": 1, "align": "center"
    })
    for col_num, value in enumerate(df.columns):
        worksheet.write(0, col_num, value, header_format)
    
    # Auto-adjust columns
    worksheet.set_column(0, 0, 10)  # Step No.
    worksheet.set_column(1, 1, 28)  # Activity
    worksheet.set_column(2, 2, 50)  # Details (wrap text)
    worksheet.set_column(3, 4, 18)  # Team & Date
    worksheet.set_column(5, 5, 12)  # Status

print("Professional Excel file created!")