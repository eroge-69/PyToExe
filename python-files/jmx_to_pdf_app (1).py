
import tkinter as tk
from tkinter import filedialog, messagebox
import xml.etree.ElementTree as ET
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import os

def parse_jmx(jmx_path):
    tree = ET.parse(jmx_path)
    root = tree.getroot()

    test_elements = []

    for elem in root.iter():
        if 'TestPlan' in elem.tag or 'ThreadGroup' in elem.tag or 'HTTPSamplerProxy' in elem.tag:
            name = elem.attrib.get('testname') or elem.attrib.get('guiclass') or elem.tag
            config = {child.tag.split('.')[-1]: child.text for child in elem}
            test_elements.append((name, config))

    return test_elements

def generate_pdf_report(data, output_path):
    c = canvas.Canvas(output_path, pagesize=A4)
    width, height = A4
    y = height - 40
    c.setFont("Helvetica-Bold", 14)
    c.drawString(40, y, "JMeter Test Report")
    c.setFont("Helvetica", 10)
    y -= 30

    for name, config in data:
        c.drawString(50, y, f"Element: {name}")
        y -= 15
        for k, v in config.items():
            text = f"  {k}: {v}" if v else f"  {k}: [empty]"
            c.drawString(60, y, text[:120])
            y -= 12
            if y < 100:
                c.showPage()
                y = height - 40
                c.setFont("Helvetica", 10)
        y -= 10

    c.save()

def select_file():
    filepath = filedialog.askopenfilename(filetypes=[("JMX files", "*.jmx")])
    if not filepath:
        return
    try:
        elements = parse_jmx(filepath)
        output_path = os.path.splitext(filepath)[0] + "_report.pdf"
        generate_pdf_report(elements, output_path)
        messagebox.showinfo("Gotowe!", f"Raport zapisany jako:\n{output_path}")
    except Exception as e:
        messagebox.showerror("Błąd", f"Nie udało się przetworzyć pliku:\n{str(e)}")

def main():
    root = tk.Tk()
    root.title("JMX ➜ PDF Konwerter")
    root.geometry("300x120")

    label = tk.Label(root, text="Wybierz plik .jmx do konwersji:")
    label.pack(pady=10)

    button = tk.Button(root, text="Wybierz plik", command=select_file)
    button.pack(pady=5)

    root.mainloop()

if __name__ == "__main__":
    main()
