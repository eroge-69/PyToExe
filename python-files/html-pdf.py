
import pdfkit
import datetime
import os

# Sett sti til wkhtmltopdf (oppdater hvis installert et annet sted)
wkhtmltopdf_path = r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe"

# Konfigurer pdfkit
config = pdfkit.configuration(wkhtmltopdf=wkhtmltopdf_path)

# HTML-fil som skal konverteres
html_file = "input.html"  # Endre til din filsti

# Lag PDF-fil med tidsstempel
timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
pdf_file = f"output_{timestamp}.pdf"

# Konverter HTML til PDF
try:
    pdfkit.from_file(html_file, pdf_file, configuration=config)
    print(f"Konverterte '{html_file}' til '{pdf_file}'")
except Exception as e:
    print(f"Feil under konvertering: {e}")
