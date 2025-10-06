import os
import sys
import glob
import win32clipboard
import io
from PIL import Image, ImageGrab
from PyPDF2 import PdfReader, PdfWriter
import tempfile
import shutil
from datetime import datetime
import win32print
import time
import math
import threading
from pynput import keyboard
import ctypes

def read_config():
    """Чтение пути директории и имени принтера из config.txt"""
    try:
        with open('config.txt', 'r', encoding='utf-8') as f:
            lines = f.readlines()
            directory = lines[0].strip()
            printer_name = lines[1].strip() if len(lines) > 1 else None
        return directory, printer_name
    except FileNotFoundError:
        print("Файл config.txt не найден!")
        return None, None
    except Exception as e:
        print(f"Ошибка чтения config.txt: {e}")
        return None, None

def dib_to_image(dib_data):
    """Конвертирует DIB данные в изображение PIL"""
    try:
        # Создаем временный файл BMP
        with tempfile.NamedTemporaryFile(delete=False, suffix='.bmp') as temp_file:
            # Добавляем заголовок BMP к DIB данным
            width = int.from_bytes(dib_data[4:8], 'little')
            height = int.from_bytes(dib_data[8:12], 'little')
            bit_count = int.from_bytes(dib_data[14:16], 'little')
            
            # Создаем BMP заголовок
            file_size = len(dib_data) + 14
            bmp_header = b'BM' + file_size.to_bytes(4, 'little') + b'\x00\x00\x00\x00' + b'\x36\x00\x00\x00'
            
            temp_file.write(bmp_header)
            temp_file.write(dib_data)
            temp_path = temp_file.name
        
        # Открываем как изображение PIL
        image = Image.open(temp_path)
        os.unlink(temp_path)  # Удаляем временный файл
        return image
        
    except Exception as e:
        print(f"Ошибка конвертации DIB: {e}")
        return None

def get_image_from_clipboard():
    """Получение изображения из буфера обмена"""
    try:
        # Сначала проверяем, есть ли файлы в буфере обмена
        try:
            win32clipboard.OpenClipboard()
            if win32clipboard.IsClipboardFormatAvailable(win32clipboard.CF_HDROP):
                print("Обнаружены файлы в буфере обмена")
                files = win32clipboard.GetClipboardData(win32clipboard.CF_HDROP)
                if files and len(files) > 0:
                    # Берем первый файл и проверяем, является ли он изображением
                    first_file = files[0]
                    if first_file.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif', '.tiff')):
                        print(f"Загружаем изображение из файла: {first_file}")
                        image = Image.open(first_file)
                        win32clipboard.CloseClipboard()
                        return image
            win32clipboard.CloseClipboard()
        except:
            try:
                win32clipboard.CloseClipboard()
            except:
                pass

        # Способ 1: Прямой захват через ImageGrab
        print("Попытка получить изображение через ImageGrab...")
        image = ImageGrab.grabclipboard()
        if image is not None:
            if hasattr(image, 'size'):  # Проверяем, что это действительно изображение
                print(f"Изображение получено через ImageGrab: {image.size}")
                return image
            else:
                print("ImageGrab вернул не изображение")

        # Способ 2: Через win32clipboard для формата DIB
        print("Попытка получить изображение через win32clipboard...")
        win32clipboard.OpenClipboard()
        try:
            # Проверяем различные форматы изображений
            formats = []
            format_num = 0
            while True:
                try:
                    format_num = win32clipboard.EnumClipboardFormats(format_num)
                    if format_num == 0:
                        break
                    formats.append(format_num)
                except:
                    break
            
            print(f"Доступные форматы в буфере: {formats}")

            # CF_DIB (8) - Device Independent Bitmap
            if win32clipboard.IsClipboardFormatAvailable(win32clipboard.CF_DIB):
                print("Обнаружен формат CF_DIB")
                data = win32clipboard.GetClipboardData(win32clipboard.CF_DIB)
                if data:
                    image = dib_to_image(data)
                    if image:
                        return image

            # CF_BITMAP (2) - Bitmap handle
            elif win32clipboard.IsClipboardFormatAvailable(win32clipboard.CF_BITMAP):
                print("Обнаружен формат CF_BITMAP")
                try:
                    from PIL import ImageWin
                    bitmap_handle = win32clipboard.GetClipboardData(win32clipboard.CF_BITMAP)
                    if bitmap_handle:
                        bitmap = ImageWin.Dib(bitmap_handle)
                        image = Image.frombytes("RGB", (bitmap.width, bitmap.height), bitmap.get_bitmap_bytes(), "raw", "BGRX")
                        return image
                except Exception as e:
                    print(f"Ошибка обработки CF_BITMAP: {e}")

            # Проверяем наличие PNG (формат 13)
            png_format = win32clipboard.RegisterClipboardFormat("PNG")
            if win32clipboard.IsClipboardFormatAvailable(png_format):
                print("Обнаружен формат PNG")
                try:
                    data = win32clipboard.GetClipboardData(png_format)
                    if data:
                        image = Image.open(io.BytesIO(data))
                        return image
                except Exception as e:
                    print(f"Ошибка обработки PNG: {e}")

            # Проверяем наличие JPEG
            jpeg_format = win32clipboard.RegisterClipboardFormat("JFIF")
            if win32clipboard.IsClipboardFormatAvailable(jpeg_format):
                print("Обнаружен формат JPEG")
                try:
                    data = win32clipboard.GetClipboardData(jpeg_format)
                    if data:
                        image = Image.open(io.BytesIO(data))
                        return image
                except Exception as e:
                    print(f"Ошибка обработки JPEG: {e}")

            # Дополнительные форматы изображений
            for format_id in [win32clipboard.CF_TIFF, win32clipboard.CF_METAFILEPICT]:
                if win32clipboard.IsClipboardFormatAvailable(format_id):
                    print(f"Обнаружен формат {format_id}")
                    try:
                        data = win32clipboard.GetClipboardData(format_id)
                        if data:
                            # Пытаемся открыть как изображение
                            image = Image.open(io.BytesIO(data))
                            return image
                    except Exception as e:
                        print(f"Ошибка обработки формата {format_id}: {e}")
                    
        finally:
            win32clipboard.CloseClipboard()
            
        print("Не удалось получить изображение ни одним из способов")
        return None
        
    except Exception as e:
        print(f"Общая ошибка получения изображения из буфера: {str(e)}")
        return None
    
def get_newest_pdf(directory):
    """Поиск самого нового PDF файла в директории"""
    pdf_files = glob.glob(os.path.join(directory, "*.pdf"))
    if not pdf_files:
        return None
    
    newest_pdf = max(pdf_files, key=os.path.getctime)
    return newest_pdf

def calculate_target_area():
    """Расчет целевой области на основе данных из примера"""
    target_area = {
        'x0': 121.94,
        'y0': 480.25,  
        'x1': 469.40,
        'y1': 740.84,
        'width': 347.46,
        'height': 260.60,
        'center_x': (121.94 + 469.40) / 2,
        'center_y': (480.25 + 740.84) / 2
    }
    return target_area

def resize_image_to_fit_area(image, target_area):
    """Изменение размера изображения чтобы вписать в целевую область с сохранением пропорций"""
    original_width, original_height = image.size
    target_width = target_area['width']
    target_height = target_area['height']
    
    width_ratio = target_width / original_width
    height_ratio = target_height / original_height
    
    scale_ratio = min(width_ratio, height_ratio)
    
    new_width = int(original_width * scale_ratio)
    new_height = int(original_height * scale_ratio)
    
    resized_image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
    
    return resized_image

def add_image_to_pdf(pdf_path, image, target_area):
    """Добавление изображения в PDF файл с центрированием относительно целевой области"""
    try:
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.utils import ImageReader
        
        temp_image_pdf = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
        temp_image_path = temp_image_pdf.name
        temp_image_pdf.close()
        
        c = canvas.Canvas(temp_image_path, pagesize=A4)
        img_reader = ImageReader(image)
        
        img_width = image.width
        img_height = image.height
        
        page_height = A4[1]
        center_x = target_area['center_x']
        center_y_from_bottom = target_area['center_y']
        center_y = page_height - center_y_from_bottom
        
        x = center_x - (img_width / 2)
        y = center_y - (img_height / 2)
        
        c.drawImage(img_reader, x, y, width=img_width, height=img_height)
        c.save()
        
        original_pdf = PdfReader(pdf_path)
        image_pdf = PdfReader(temp_image_path)
        
        writer = PdfWriter()
        
        original_page = original_pdf.pages[0]
        image_page = image_pdf.pages[0]
        original_page.merge_page(image_page)
        
        writer.add_page(original_page)
        
        for i in range(1, len(original_pdf.pages)):
            writer.add_page(original_pdf.pages[i])
        
        with open(pdf_path, 'wb') as output_file:
            writer.write(output_file)
        
        os.unlink(temp_image_path)
        return True
        
    except Exception as e:
        print(f"Ошибка добавления изображения в PDF: {e}")
        if 'temp_image_path' in locals() and os.path.exists(temp_image_path):
            os.unlink(temp_image_path)
        return False

def print_pdf(pdf_path, printer_name, copies=2):
    """Печать PDF файла через конвертацию в изображение на весь лист"""
    try:
        print(f"Печать {copies} копий на принтер: {printer_name}")
        
        import win32print
        import subprocess
        
        # Проверяем доступность принтера
        printers = [p[2] for p in win32print.EnumPrinters(win32print.PRINTER_ENUM_LOCAL | win32print.PRINTER_ENUM_CONNECTIONS)]
        print(f"Доступные принтеры: {printers}")
        
        if printer_name not in printers:
            print(f"Принтер '{printer_name}' не найден. Используем принтер по умолчанию.")
            printer_name = win32print.GetDefaultPrinter()
            print(f"Используется принтер: {printer_name}")

        # Конвертируем PDF в изображение и затем печатаем
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.utils import ImageReader
        
        # Создаем временное изображение из PDF
        temp_image = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
        temp_image_path = temp_image.name
        temp_image.close()
        
        try:
            # Открываем PDF и конвертируем первую страницу в изображение
            import fitz  # PyMuPDF
            doc = fitz.open(pdf_path)
            page = doc[0]
            
            # Конвертируем страницу в изображение с высоким DPI
            pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # 2x DPI для качества
            pix.save(temp_image_path)
            doc.close()
            
            print(f"PDF конвертирован в изображение: {pix.width}x{pix.height}")
            
            # Печать через PowerShell с растягиванием на весь лист
            powershell_script = f'''
            Add-Type -AssemblyName System.Drawing
            $printerName = "{printer_name}"
            $imagePath = "{temp_image_path}"
            $copies = {copies}
            
            try {{
                # Загружаем изображение
                $image = [System.Drawing.Image]::FromFile($imagePath)
                
                for ($copy = 1; $copy -le $copies; $copy++) {{
                    # Создаем объект для печати для каждой копии
                    $printDocument = New-Object System.Drawing.Printing.PrintDocument
                    $printDocument.PrinterSettings.PrinterName = $printerName
                    $printDocument.PrinterSettings.Copies = 1
                    
                    # Событие для печати страницы
                    $printDocument_PrintPage = {{
                        param([object]$sender, [System.Drawing.Printing.PrintPageEventArgs]$e)
                        
                        # Растягиваем изображение на ВЕСЬ лист (без полей)
                        $pageBounds = $e.PageBounds
                        
                        # Рисуем изображение на всей площади страницы
                        $e.Graphics.DrawImage($image, 0, 0, $pageBounds.Width, $pageBounds.Height)
                        $e.HasMorePages = $false
                    }}
                    
                    $printDocument.add_PrintPage($printDocument_PrintPage)
                    $printDocument.Print()
                    $printDocument.Dispose()
                    
                    Write-Output "Копия $copy отправлена на печать"
                    if ($copy -lt $copies) {{
                        Start-Sleep -Milliseconds 1000
                    }}
                }}
                
                $image.Dispose()
            }}
            catch {{
                Write-Error "Ошибка печати: $_"
            }}
            '''
            
            # Запускаем PowerShell скрипт
            result = subprocess.run([
                "powershell", "-ExecutionPolicy", "Bypass", "-Command", powershell_script
            ], capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                print("Печать отправлена успешно через PowerShell")
                print(f"Результат: {result.stdout}")
                return True
            else:
                print(f"Ошибка PowerShell: {result.stderr}")
                return False
                
        finally:
            # Удаляем временные файлы
            try:
                if os.path.exists(temp_image_path):
                    os.unlink(temp_image_path)
            except:
                pass
                
    except Exception as e:
        print(f"Ошибка печати: {e}")
        import traceback
        traceback.print_exc()
        return False

def close_pdf_applications():
    """Закрытие приложений PDF"""
    try:
        import subprocess
        subprocess.run(['taskkill', '/F', '/IM', 'AcroRd32.exe'], 
                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run(['taskkill', '/F', '/IM', 'Acrobat.exe'], 
                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print("PDF приложения закрыты")
    except Exception as e:
        print(f"Ошибка при закрытии приложений: {e}")

def show_error_message(message):
    """Показать сообщение об ошибке"""
    ctypes.windll.user32.MessageBoxW(0, message, "Ошибка", 0x00001000)

def show_success_message(message):
    """Показать сообщение об успехе"""
    ctypes.windll.user32.MessageBoxW(0, message, "Успех", 0x00001000)

def process_image_to_pdf():
    """Основной процесс обработки изображения и печати"""
    try:
        print("Запуск процесса...")
        
        directory, printer_name = read_config()
        if not directory:
            error_msg = "Ошибка: не удалось загрузить конфигурацию из config.txt"
            print(error_msg)
            show_error_message(error_msg)
            return
        
        if not printer_name:
            printer_name = win32print.GetDefaultPrinter()
            print(f"Используется принтер по умолчанию: {printer_name}")
        
        newest_pdf = get_newest_pdf(directory)
        if not newest_pdf:
            error_msg = "PDF файлы не найдены в указанной директории"
            print(error_msg)
            show_error_message(error_msg)
            return
        
        image = get_image_from_clipboard()
        if not image:
            error_msg = "Нет изображения в буфере обмена"
            print(error_msg)
            show_error_message(error_msg)
            return
        
        target_area = calculate_target_area()
        resized_image = resize_image_to_fit_area(image, target_area)
        
        if add_image_to_pdf(newest_pdf, resized_image, target_area):
            print("Изображение добавлено в PDF")
            
            if print_pdf(newest_pdf, printer_name, copies=2):
                success_msg = "Печать отправлена успешно"
                print(success_msg)
                show_success_message(success_msg)
            else:
                error_msg = "Ошибка отправки на печать"
                print(error_msg)
                show_error_message(error_msg)
                
            close_pdf_applications()
            
        else:
            error_msg = "Ошибка добавления изображения в PDF"
            print(error_msg)
            show_error_message(error_msg)
        
        print("Процесс завершен")
        
    except Exception as e:
        error_msg = f"Ошибка в процессе: {e}"
        print(error_msg)
        show_error_message(error_msg)

def on_activate():
    """Обработчик горячих клавиш"""
    print("Горячие клавиши нажаты, запуск процесса...")
    thread = threading.Thread(target=process_image_to_pdf)
    thread.daemon = True
    thread.start()

def main():
    """Основная функция с обработкой горячих клавиш"""
    print("Программа запущена. Ожидание комбинации Ctrl+1+2...")
    print("Для выхода нажмите Ctrl+C")
    
    # Создаем комбинацию горячих клавиш
    hotkey = keyboard.HotKey(
        keyboard.HotKey.parse('<ctrl>+1+2'),
        on_activate
    )
    
    def on_press(key):
        hotkey.press(listener.canonical(key))
    
    def on_release(key):
        hotkey.release(listener.canonical(key))
    
    # Запускаем слушатель клавиатуры
    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        try:
            listener.join()
        except KeyboardInterrupt:
            print("\nПрограмма завершена")

if __name__ == "__main__":
    main()