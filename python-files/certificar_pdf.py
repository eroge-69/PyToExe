import PyPDF2
from reportlab.pdfgen import canvas
from reportlab.lib.colors import red

def add_folio_and_legend(input_pdf_path, output_pdf_path, password):
    # Crear un nuevo PDF temporal para las páginas con folios
    temp_pdf_path = "temp_foliado.pdf"
    c = canvas.Canvas(temp_pdf_path)

    # Abrir el PDF original
    pdf_in = open(input_pdf_path, 'rb')
    pdf_reader = PyPDF2.PdfReader(pdf_in)
    num_pages = len(pdf_reader.pages)

    # Crear un escritor de PDF
    pdf_writer = PyPDF2.PdfWriter()

    # Procesar cada página y añadir folio
    for page_num in range(num_pages):
        page = pdf_reader.pages[page_num]
        packet = c.beginDocument()
        c.setFillColor(red)
        c.drawString(500, 800, f"{page_num + 1:03d}")  # Folio en formato 001, 002, etc.
        c.showPage()
        c.save()

        # Combinar la página original con el folio
        folio_pdf = PyPDF2.PdfReader(open(temp_pdf_path, "rb"))
        folio_page = folio_pdf.pages[0]
        page.merge_page(folio_page)
        pdf_writer.add_page(page)

    # Solicitar la leyenda al usuario
    print("Por favor, ingresa la leyenda final (puedes editarla). Deja en blanco y presiona Enter para usar el valor predeterminado.")
    default_legend = "Documento certificado por el Secretario del Ayuntamiento el 11 de julio de 2025 a las 14:00 CST."
    legend_text = input(f"Legend (default: {default_legend}): ").strip()
    if not legend_text:
        legend_text = default_legend

    # Añadir página con la leyenda al final
    c = canvas.Canvas(temp_pdf_path)
    c.drawString(100, 750, legend_text)
    c.showPage()
    c.save()
    legend_pdf = PyPDF2.PdfReader(open(temp_pdf_path, "rb"))
    pdf_writer.add_page(legend_pdf.pages[0])

    # Proteger el PDF solo contra modificaciones
    pdf_writer.encrypt(user_pwd='', owner_pwd=password, use_128bit=True, permissions=PyPDF2.Permissions(access_permission_flag=0x0004))  # Solo permite lectura

    # Guardar el PDF final
    with open(output_pdf_path, 'wb') as pdf_out:
        pdf_writer.write(pdf_out)

    # Limpiar archivo temporal
    import os
    os.remove(temp_pdf_path)

    pdf_in.close()
    print(f"PDF guardado como {output_pdf_path} con éxito.")

# Ejemplo de uso
input_pdf_path = "documento_original.pdf"  # Cambia esto por la ruta de tu PDF
output_pdf_path = "documento_certificado.pdf"  # Nombre del PDF resultante
password = "secreto123"  # Contraseña para proteger modificaciones

add_folio_and_legend(input_pdf_path, output_pdf_path, password)