import os
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from pdf2image import convert_from_path

class MyHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory:
            return

        if event.src_path.lower().endswith('.pdf'):
            pdf_path = event.src_path
            png_folder = "C:\\etiket2"
            output_folder = "C:\\etiket2"
            convert_pdf_to_png(pdf_path, png_folder)
            #delete_pdf(png_folder)

    def on_modified(self, event):
        if event.is_directory:
            return

        if event.src_path.lower().endswith('.pdf'):
            self.process_pdf(event.src_path)

    def process_pdf(self, pdf_path):
        png_folder = "C:\\etiket2"
        output_folder = "C:\\Users\\administrator.ONKA\\Desktop\\New folder2"
        convert_pdf_to_png(pdf_path, output_folder)
        #delete_pdf("C:\\etiket2")

def convert_pdf_to_png(pdf_path, output_folder,image_size=(800, 320)):
    try:
        # PDF'yi PNG'ye dönüştür
        images = convert_from_path(pdf_path, size=image_size , poppler_path=r"C:\Program Files\poppler-23.11.0\Library\bin")

        # PNG olarak kaydet
        for i, image in enumerate(images):
            pdf_name = os.path.splitext(os.path.basename(pdf_path))[0]
            file_name = f"{pdf_name}.png"
            png_path = os.path.join(output_folder, file_name)
            with open(png_path, 'wb') as png_file:
                image.save(png_path, "PNG")
            print(f"{pdf_path} dosyası {png_path} olarak kaydedildi.")
    except Exception as e:
        print(f"Hata: {e}")

def delete_pdf(folder_path):
    try:
        time.sleep(2)
        klasor_yolu = folder_path  # Silmek istediğiniz klasörün yolu

        # Klasörün içindeki dosyaları listele
        dosyalar = os.listdir(klasor_yolu)

        # Her bir dosyayı sil
        for dosya in dosyalar:
            dosya_yolu = os.path.join(klasor_yolu, dosya)
            if os.path.isfile(dosya_yolu):
                os.remove(dosya_yolu)
    except Exception as e:
        print(f"Hata oluştu: {e}")

def process_existing_pdfs(folder_to_watch):
    existing_pdfs = [f for f in os.listdir(folder_to_watch) if f.lower().endswith('.pdf')]
    for pdf in existing_pdfs:
        pdf_path = os.path.join(folder_to_watch, pdf)
        event_handler.process_pdf(pdf_path)

if __name__ == "__main__":
    folder_to_watch = "C:\\etiket2"
    
    event_handler = MyHandler()
    observer = Observer()
    process_existing_pdfs(folder_to_watch)
    observer.schedule(event_handler, folder_to_watch, recursive=False)
    print(f"Klasör izleme başladı: {folder_to_watch}")
    
    try:
        observer.start()
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    
    observer.join()