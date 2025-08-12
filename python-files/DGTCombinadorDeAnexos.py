
import argparse
import os
import zipfile
import fitz
# from PyPDF2 import PdfMerger


def unzip_and_combine_pdfs(input_path):

    for root, dirs, files in os.walk(input_path):

        for file in files:

            if file.endswith(".zip"):

                zip_file_path = os.path.join(root, file)

                print("descomprimiendo", zip_file_path)

                extract_folder = os.path.splitext(zip_file_path)[0]

                # Descomprimir el archivo ZIP
                with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
                    zip_ref.extractall(extract_folder)

                pdf_files = [f for f in os.listdir(extract_folder) if f.endswith(".pdf")]

                # Ordenar los archivos PDF
                pdf_files.sort(key=lambda x: (
                    not x.startswith('Justificante CSV'),
                    not x.startswith('Justificante de Presentación'),
                    x
                ))

                # Combinar los archivos PDF
                """
                merger = PdfMerger()
                for pdf_file in pdf_files:
                    pdf_file_path = os.path.join(extract_folder, pdf_file)
                    merger.append(pdf_file_path)
                """
                merger = fitz.open()

                for pdf_file in pdf_files:
                    pdf_file_path = os.path.join(extract_folder, pdf_file)
                    pdf_document = fitz.open(pdf_file_path)
                    merger.insert_pdf(pdf_document)
                    pdf_document.close()

                # Guardar el archivo combinado en el directorio actual
                output_pdf_path = os.path.join(os.getcwd(), f"{os.path.basename(extract_folder)}.pdf")
                merger.save(output_pdf_path)
                merger.close()

                # Eliminar la carpeta después de combinar los archivos
                for file_to_delete in os.listdir(extract_folder):
                    file_path_to_delete = os.path.join(extract_folder, file_to_delete)
                    os.remove(file_path_to_delete)
                os.rmdir(extract_folder)

                # Eliminar el archivo ZIP después de procesarlo
                os.remove(zip_file_path)
                print(f"Archivo ZIP {zip_file_path} eliminado.")

if __name__ == "__main__":

    parser = argparse.ArgumentParser(prog='DGTCombinadorDeAnexos', description="Programa encargado de descomprimir zips de los anexos y combinar los pdfs que contienen dichos zip.", epilog='Actualizado por Melvin De Oleo :)')

    parser.add_argument("-p", "--path", default=".", help="Ruta donde están los anexos que se descomprimirán")

    args = parser.parse_args()

    input_path = args.path

    unzip_and_combine_pdfs(input_path)
