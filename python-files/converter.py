from pathlib import Path
import pandas as pd
from docxtpl import DocxTemplate
base_dir = Path(__file__).parent 
word_template_path = base_dir / "New Microsoft Word Document.docx"
excel_path = base_dir / "New Microsoft Excel Worksheet.xlsx"
output_dir = base_dir / "New folder"
df = pd.read_excel(excel_path, sheet_name="list")
df["التاريخ"] = pd.to_datetime(df["التاريخ"]).dt.date
for record in df.to_dict(orient="records"):
    doc = DocxTemplate(word_template_path)
    doc.render(record)
    output_path = output_dir / f"{record['الاسم']}.docx"
    doc.save (output_path)
