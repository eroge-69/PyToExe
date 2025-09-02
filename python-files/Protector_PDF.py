from PyPDF2 import PdfFileWriter, PdfFileReader

pdfwriter = PdfFileWriter()
pdf = PdfFileReader(input("Ingrese el nombre del pdf sin la extensión: ") + ".pdf")
for page_nº in range(pdf.numPages):
    pdfwriter.addPage(pdf.getPage(page_nº))
password = input("Ingrese la contraseña: ")
new_name = input("Ingrese el nombre del nuevo archovo sin la extensión: " + ".pdf")
with open(new_name, "wb") as f:
    pdfwriter.write(f)
    f.close()