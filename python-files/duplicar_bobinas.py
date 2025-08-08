import re
import PyPDF2
import os
import tkinter as tk
from tkinter import filedialog
from tqdm import tqdm

# Ocultar ventana principal de Tkinter
root = tk.Tk()
root.withdraw()

print("=== DUPLICADOR DE CERTIFICADOS POR BOBINA ===")
print("Selecciona el archivo PDF que quieres procesar...\n")

# Pedir al usuario que seleccione el archivo
pdf_path = filedialog.askopenfilename(
    title="Selecciona el PDF",
    filetypes=[("Archivos PDF", "*.pdf")]
)

if not pdf_path:
    print("No se seleccionó ningún archivo. Saliendo...")
    input("\nPulsa Enter para salir...")
    exit()

# Patrón para detectar bobinas
patron_bobina = r"Bobina n\./Batch:\s*([^\n\r]+)"

# Leer PDF y extraer texto
try:
    with open(pdf_path, "rb") as file:
        reader = PyPDF2.PdfReader(file)
        texto = ""
        for pagina in reader.pages:
            texto += pagina.extract_text()
except Exception as e:
    print(f"ERROR al leer el PDF: {e}")
    input("\nPulsa Enter para salir...")
    exit()

# Buscar bobinas
bobinas_encontradas = re.findall(patron_bobina, texto)
bobinas_unicas = list(dict.fromkeys(bobinas_encontradas))

if not bobinas_unicas:
    print("No se han detectado bobinas. Revisa el patrón de búsqueda.")
    input("\nPulsa Enter para salir...")
    exit()

print(f"Se han detectado {len(bobinas_unicas)} bobinas.")

# Crear carpeta de salida
carpeta_salida = os.path.join(os.path.dirname(pdf_path), "Certificados_por_bobina")
os.makedirs(carpeta_salida, exist_ok=True)

# Crear PDFs individuales con barra de progreso
for bobina in tqdm(bobinas_unicas, desc="Generando certificados", unit="pdf"):
    writer = PyPDF2.PdfWriter()
    for pagina in reader.pages:
        writer.add_page(pagina)
    nombre_archivo = os.path.join(
        carpeta_salida, f"certificado_{bobina.strip().replace('/', '-')}.pdf"
    )
    with open(nombre_archivo, "wb") as output_file:
        writer.write(output_file)

print(f"\n✅ Proceso completado con éxito.\nArchivos guardados en:\n{carpeta_salida}")
input("\nPulsa Enter para salir...")
