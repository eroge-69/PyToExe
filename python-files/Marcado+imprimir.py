import os
import sys
import subprocess
from tkinter import Tk, filedialog
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from io import BytesIO
import traceback

def crear_marca_agua(texto, ancho, alto):
    packet = BytesIO()
    c = canvas.Canvas(packet, pagesize=(ancho, alto))
    c.setFont("Helvetica-Bold", 36)
    c.setFillColorRGB(0.7, 0.7, 0.7)
    c.drawCentredString(ancho / 2, alto / 2, texto)
    c.save()
    packet.seek(0)
    return PdfReader(packet)

def obtener_tamano_pdf(ruta_pdf):
    pdf = PdfReader(ruta_pdf)
    page = pdf.pages[0]
    width = float(page.mediabox.width)
    height = float(page.mediabox.height)
    width_mm = width * 25.4 / 72
    height_mm = height * 25.4 / 72
    return width_mm, height_mm

def identificar_formato(width_mm, height_mm):
    formatos = {
        "A0": (841, 1189),
        "A1": (594, 841),
        "A2": (420, 594),
        "A3": (297, 420),
        "A4": (210, 297),
    }
    for formato, (ancho, alto) in formatos.items():
        if (abs(width_mm - ancho) < 5 and abs(height_mm - alto) < 5) or \
           (abs(width_mm - alto) < 5 and abs(height_mm - ancho) < 5):
            return formato
    return "Tamaño desconocido"

def imprimir_pdf_con_sumatra(ruta_pdf, impresora):
    sumatra_path = r"C:\Users\mer\AppData\Local\SumatraPDF\SumatraPDF.exe"
    comando = f'"{sumatra_path}" -print-to "{impresora}" -print-settings "noscale" "{ruta_pdf}"'
    print(f"🖨️ Imprimiendo con Sumatra: {comando}")
    subprocess.run(comando, shell=True)

def imprimir_pdf_con_acrobat(ruta_pdf, impresora):
    acrobat_path = r"C:\Program Files\Adobe\Acrobat DC\Acrobat\Acrobat.exe"
    if not os.path.exists(acrobat_path):
        print("⚠️ Adobe Acrobat no encontrado.")
        return
    comando = f'"{acrobat_path}" /t "{ruta_pdf}" "{impresora}"'
    print(f"🖨️ Imprimiendo con Acrobat: {comando}")
    subprocess.run(comando, shell=True)

try:
    root = Tk()
    root.withdraw()

    carpeta_entrada = filedialog.askdirectory(title="Selecciona la carpeta con los planos PDF")
    if not carpeta_entrada:
        print("❌ No se seleccionó ninguna carpeta.")
        sys.exit()

    numero_proyecto = input("Introduce el número de proyecto: ")
    carpeta_marcados = os.path.join(carpeta_entrada, "Marcados")
    os.makedirs(carpeta_marcados, exist_ok=True)

    pdfs = [f for f in os.listdir(carpeta_entrada) if f.lower().endswith('.pdf')]
    if not pdfs:
        print("⚠️ No se encontraron archivos PDF.")
        sys.exit()

    writer_a1_a2 = PdfWriter()
    impresora_a3 = "A3_Impresora"

    print("\n🔧 Procesando archivos...")

    for nombre_pdf in pdfs:
        ruta_original = os.path.join(carpeta_entrada, nombre_pdf)
        reader = PdfReader(ruta_original)
        writer = PdfWriter()

        for pagina in reader.pages:
            ancho = float(pagina.mediabox.width)
            alto = float(pagina.mediabox.height)
            marca = crear_marca_agua(numero_proyecto, ancho, alto)
            pagina.merge_page(marca.pages[0])
            writer.add_page(pagina)

        ruta_marcado = os.path.join(carpeta_marcados, nombre_pdf)
        with open(ruta_marcado, "wb") as salida:
            writer.write(salida)
        print(f"✅ Marca de agua aplicada: {nombre_pdf}")

        # Ahora analizamos el tamaño del PDF ya marcado
        ancho_mm, alto_mm = obtener_tamano_pdf(ruta_marcado)
        formato = identificar_formato(ancho_mm, alto_mm)
        print(f"📐 {nombre_pdf} → {formato}")

        if formato in ["A1", "A2"]:
            # Añadir al combinado
            marcado_pdf = PdfReader(ruta_marcado)
            for page in marcado_pdf.pages:
                writer_a1_a2.add_page(page)
        elif formato in ["A3", "A4"]:
            imprimir_pdf_con_sumatra(ruta_marcado, impresora_a3)
            print(f"🖨️ Impreso individualmente: {nombre_pdf}")
        else:
            print("❓ Formato desconocido o A0: no se imprime.")

    # Imprimir combinado de A1 y A2
    if writer_a1_a2.pages:
        combinado_path = os.path.join(carpeta_marcados, "A1_A2_combinados.pdf")
        with open(combinado_path, "wb") as combinado:
            writer_a1_a2.write(combinado)
        print(f"\n📎 Combinado A1/A2 creado: {combinado_path}")

        imprimir_pdf_con_acrobat(combinado_path, impresora_a3)
        print("🖨️ Impreso combinado A1/A2 con Acrobat.")

        os.remove(combinado_path)
        print("🗑️ Archivo combinado eliminado.")

    # Limpiar archivos marcados
    for archivo in os.listdir(carpeta_marcados):
        try:
            os.remove(os.path.join(carpeta_marcados, archivo))
        except Exception as e:
            print(f"⚠️ No se pudo eliminar {archivo}: {e}")
    os.rmdir(carpeta_marcados)

    print("\n✅ Proceso completado.")
    input("\nPulsa ENTER para salir...")

except Exception:
    print("❌ Error inesperado:")
    traceback.print_exc()
    input("\nPulsa ENTER para salir...")

