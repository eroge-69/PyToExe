import fitz  # PyMuPDF
import json

def find_pdf_files():
    """Encuentra todos los archivos PDF en el directorio actual"""
    import glob
    # Buscar todos los archivos .pdf en el directorio actual
    pdf_files = glob.glob('*.pdf')
    return pdf_files

def merge_pdfs(pdf_files, output_filename='merged_document.pdf'):
    """Combina múltiples archivos PDF en uno solo"""
    # Crear un nuevo documento PDF
    merged_doc = fitz.open()
    
    for pdf_file in pdf_files:
        print(f"Procesando: {pdf_file}")
        try:
            # Abrir cada PDF
            doc = fitz.open(pdf_file)
            # Insertar todas las páginas del PDF actual al documento combinado
            merged_doc.insert_pdf(doc)
            # Cerrar el documento actual
            doc.close()
        except Exception as e:
            print(f"Error procesando {pdf_file}: {str(e)}")
            continue
    
    # Guardar el documento combinado
    if merged_doc.page_count > 0:
        merged_doc.save(output_filename)
        merged_doc.close()
        return True
    else:
        print("No se encontraron páginas para combinar")
        merged_doc.close()
        return False

def main():
    print("Iniciando proceso de combinación de PDFs...")
    
    # Buscar archivos PDF
    pdf_files = find_pdf_files()
    
    if not pdf_files:
        print("No se encontraron archivos PDF en el directorio actual")
        return
    
    print(f"Archivos PDF encontrados: {len(pdf_files)}")
    for i, pdf_file in enumerate(pdf_files, 1):
        print(f"{i}. {pdf_file}")
    
    # Combinar PDFs
    success = merge_pdfs(pdf_files)
    
    if success:
        print("PDFs combinados exitosamente en 'merged_document.pdf'")
    else:
        print("Error al combinar los PDFs")

# Ejecutar el script principal
main()