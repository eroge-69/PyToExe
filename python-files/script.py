import os
import pandas as pd
import matplotlib.pyplot as plt
from docx import Document
from docx.shared import Pt
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import letter
from fpdf import FPDF
import xlsxwriter

# -------------------------------
# CONFIG
# -------------------------------
DATA_FILE = "PlaylistData_2025-09-15.xlsx"
OUTPUT_DIR = "scout_outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# -------------------------------
# LOAD DATA
# -------------------------------
df = pd.read_excel(DATA_FILE, sheet_name="Sheet1")

# Normalize fields
df['is_pass'] = df['PLAY TYPE'].str.contains("Pass", case=False, na=False)
df['is_run'] = df['PLAY TYPE'].str.contains("Run", case=False, na=False)

# -------------------------------
# ANALYSIS
# -------------------------------
# By down tendencies
by_down = df.groupby("DN").agg(
    total=("PLAY #","count"),
    pass_plays=("is_pass","sum"),
    run_plays=("is_run","sum")
).reset_index()
by_down["pass_pct"] = (by_down["pass_plays"]/by_down["total"]).round(2)

# By personnel tendencies
by_personnel = df.groupby("PERSONNEL").agg(
    total=("PLAY #","count"),
    pass_plays=("is_pass","sum"),
    run_plays=("is_run","sum")
).reset_index()
by_personnel["pass_pct"] = (by_personnel["pass_plays"]/by_personnel["total"]).round(2)

# 3rd down success (simple: any play on DN=3 that results in "Complete" or GN/LS >= DIST)
third_down = df[df["DN"]==3].copy()
third_down["converted"] = (third_down["RESULT"].str.contains("Complete", na=False)) | (third_down["GN/LS"]>=third_down["DIST"])
third_summary = third_down.groupby(["PERSONNEL","OFF FORM"]).agg(
    total=("PLAY #","count"),
    conversions=("converted","sum")
).reset_index()
third_summary["conv_pct"] = (third_summary["conversions"]/third_summary["total"]).round(2)
top_third = third_summary.sort_values("conv_pct", ascending=False).head(5)

# -------------------------------
# EXCEL DASHBOARD
# -------------------------------
excel_path = os.path.join(OUTPUT_DIR,"Opponent_Dashboard.xlsx")
with pd.ExcelWriter(excel_path, engine="xlsxwriter") as writer:
    df.to_excel(writer, sheet_name="Raw_Plays", index=False)
    by_down.to_excel(writer, sheet_name="By_Down", index=False)
    by_personnel.to_excel(writer, sheet_name="By_Personnel", index=False)
    third_summary.to_excel(writer, sheet_name="3rdDown_Summary", index=False)

    # Charts
    workbook  = writer.book
    sheet = writer.sheets["By_Down"]
    chart = workbook.add_chart({"type":"column"})
    chart.add_series({
        "name":"Pass %",
        "categories":["By_Down",1,0,len(by_down),0],
        "values":["By_Down",1,4,len(by_down),4],
    })
    chart.set_title({"name":"Pass % by Down"})
    sheet.insert_chart("G2", chart)

# -------------------------------
# SCOUTING REPORT (PDF & DOCX)
# -------------------------------
report_text = f"""
Opponent Scouting Report

Key Tendencies:
- Pass % by Down: {by_down.to_dict(orient='records')}
- Pass % by Personnel: {by_personnel.to_dict(orient='records')}

Top 3rd Down Conversions:
{top_third.to_string(index=False)}

Practice Recommendations:
- Rep 3rd & Long vs Trips/11 personnel.
- Defend quick game from Empty formations.
- Prepare for Zone Read in 2nd and medium.
"""

# PDF
pdf_path = os.path.join(OUTPUT_DIR,"Full_Scouting_Report.pdf")
doc = SimpleDocTemplate(pdf_path, pagesize=letter)
styles = getSampleStyleSheet()
story = [Paragraph(line, styles["Normal"]) for line in report_text.split("\n")]
doc.build(story)

# DOCX
docx_path = os.path.join(OUTPUT_DIR,"Full_Scouting_Report.docx")
docx = Document()
for line in report_text.split("\n"):
    p = docx.add_paragraph(line)
    p.style.font.size = Pt(11)
docx.save(docx_path)

# -------------------------------
# CHEAT SHEET (PDF)
# -------------------------------
cheat_path = os.path.join(OUTPUT_DIR,"Coach_Cheat_Sheet.pdf")
pdf = FPDF()
pdf.add_page()
pdf.set_font("Arial","B",16)
pdf.cell(0,10,"Coach Cheat Sheet", ln=True)
pdf.set_font("Arial","",12)
pdf.multi_cell(0,10,f"""
Scout Calls to Watch:
- Empty quick game
- Trips stick/option

Must-Stop Plays:
- {top_third.iloc[0]['OFF FORM']} with {top_third.iloc[0]['PERSONNEL']} personnel (3rd down)

Practice Reps:
- 3rd & Long pressure check
- Zone read fits
- Quick slant leverage
""")
pdf.output(cheat_path)

# -------------------------------
# PRACTICE SCRIPT (PDF)
# -------------------------------
practice_path = os.path.join(OUTPUT_DIR,"Practice_Script.pdf")
pdf = FPDF()
pdf.add_page()
pdf.set_font("Arial","B",16)
pdf.cell(0,10,"Opponent-Specific Practice Script", ln=True)
pdf.set_font("Arial","",12)

drills = [
    "Indy: Quick Slant coverage vs Empty",
    "Group: Trips Stick check",
    "Team: 3rd & Long (11 personnel/Trips)",
    "Indy: Zone Read fits",
    "Team: 2nd & Medium run-pass keys",
    "Group: Empty pressure check",
    "Team: Red Zone coverage vs Quads",
    "Indy: Pass Pro recognition",
    "Group: Motion adjust vs Jet",
    "Team: 4th down tempo defense",
    "Team: Screen pursuit drill",
    "Indy: DB leverage on slant",
    "Group: LB scrape exchange vs Zone Read",
    "Team: 2-minute defense",
    "Team: Backed-up defense"
]

for i, drill in enumerate(drills,1):
    pdf.cell(0,10,f"{i}. {drill}", ln=True)

pdf.output(practice_path)

print("All outputs saved to:", OUTPUT_DIR)
