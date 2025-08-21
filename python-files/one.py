import flet as ft
from xlutils.copy import copy
import xlrd
import os
import threading

def main(page: ft.Page):
    # Настройки страницы
    page.title = "Обработчик Excel файлов"
    page.window.width = 600
    page.window.height = 450
    page.window.resizable = False
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.theme_mode = ft.ThemeMode.LIGHT

    # Переменные
    file_path = ft.Ref[str]()
    file_path.current = ""

    # Элементы интерфейса
    selected_file_text = ft.Ref[ft.Text]()
    progress_bar = ft.Ref[ft.ProgressBar]()
    status_text = ft.Ref[ft.Text]()
    process_button = ft.Ref[ft.ElevatedButton]()

    def select_file(e: ft.FilePickerResultEvent):
        if e.files:
            file_path.current = e.files[0].path
            selected_file_text.current.value = f"Выбран файл: {os.path.basename(file_path.current)}"
            selected_file_text.current.color = ft.colors.GREEN
            process_button.current.disabled = False
        else:
            selected_file_text.current.value = "Файл не выбран"
            selected_file_text.current.color = ft.colors.RED
            process_button.current.disabled = True
        
        page.update()

    def process_excel():
        if not file_path.current:
            status_text.current.value = "Ошибка: Файл не выбран"
            status_text.current.color = ft.colors.RED
            page.update()
            return

        if not file_path.current.endswith('.xls'):
            status_text.current.value = "Ошибка: Файл должен быть в формате .xls"
            status_text.current.color = ft.colors.RED
            page.update()
            return

        try:
            # Обновляем интерфейс
            process_button.current.disabled = True
            progress_bar.current.value = 0
            status_text.current.value = "Обработка файла..."
            status_text.current.color = ft.colors.BLUE
            page.update()

            # Обрабатываем файл
            process_excel_file(file_path.current)

            # Успешное завершение
            progress_bar.current.value = 1
            status_text.current.value = "Готово! Файл успешно обработан"
            status_text.current.color = ft.colors.GREEN
            process_button.current.disabled = False

        except Exception as e:
            progress_bar.current.value = 0
            status_text.current.value = f"Ошибка: {str(e)}"
            status_text.current.color = ft.colors.RED
            process_button.current.disabled = False

        finally:
            page.update()

    def process_excel_file(file_path):
        # 1. Открываем исходный файл
        rb = xlrd.open_workbook(file_path, formatting_info=True)

        # 2. Создаем редактируемую копию
        wb = copy(rb)

        # 3. Получаем листы
        sheet_read = rb.sheet_by_index(0)
        sheet_write = wb.get_sheet(0)
        
        # 4. Получаем общее количество строк
        max_rows = sheet_read.nrows
        
        y = 1  # Начинаем со второй строки (первая обычно заголовок)
        
        # 5. Обрабатываем строки до "ИТОГО" или до конца файла
        while y < max_rows:
            # Проверяем, не достигли ли мы "ИТОГО" в столбце B (индекс 1)
            current_value = sheet_read.cell_value(y, 1)
            if current_value == "ИТОГО":
                break
            
            # 6. Обрабатываем текст из столбца J (индекс 9)
            text = str(sheet_read.cell_value(y, 9))
            result_text = ""
            
            # 7. Ищем "82000" и извлекаем следующие 5 цифр
            if "82000" in text:
                text = text.replace("82000", "&", 1)
                num = text.find("&")
                
                if num != -1 and num + 4 <= len(text):
                    extracted_text = text[num+1:num+4]
                    if extracted_text.isdigit():
                        result_text = "82000" + extracted_text
                    else:
                        result_text = ""
            
            # 8. Записываем результат в столбец C (индекс 2)
            sheet_write.write(y, 2, result_text)
            
            y += 1
        
        # 9. Сохраняем во временный файл
        temp_file = file_path.replace(".xls", "_temp.xls")
        wb.save(temp_file)

        # 10. Удаляем оригинал и переименовываем
        if os.path.exists(file_path):
            os.remove(file_path)
        
        os.rename(temp_file, file_path)

    def start_processing(e):
        # Запускаем обработку в отдельном потоке
        threading.Thread(target=process_excel, daemon=True).start()

    def exit_app(e):
        # Просто закрываем окно
        page.window.close()

    # Диалог выбора файла
    file_picker = ft.FilePicker(on_result=select_file)
    page.overlay.append(file_picker)

    # Создаем интерфейс
    page.add(
        ft.Column(
            [
                ft.Text(
                    "Обработчик Excel файлов",
                    size=24,
                    weight=ft.FontWeight.BOLD,
                    color=ft.colors.BLUE_800,
                    text_align=ft.TextAlign.CENTER
                ),
                
                ft.Divider(),
                
                ft.Text(
                    "Программа ищет '82000' в столбце J\nи извлекает следующие 3 цифры в столбец C",
                    size=14,
                    text_align=ft.TextAlign.CENTER,
                    color=ft.colors.GREY_600
                ),
                
                ft.ElevatedButton(
                    "Выбрать файл",
                    icon=ft.icons.FILE_OPEN,
                    on_click=lambda _: file_picker.pick_files(
                        allowed_extensions=["xls"],
                        file_type=ft.FilePickerFileType.CUSTOM
                    ),
                    width=200
                ),
                
                ft.Text(
                    ref=selected_file_text,
                    value="Файл не выбран",
                    color=ft.colors.RED,
                    size=12,
                    text_align=ft.TextAlign.CENTER
                ),
                
                ft.ElevatedButton(
                    ref=process_button,
                    text="Обработать файл",
                    icon=ft.icons.PLAY_ARROW,
                    on_click=start_processing,
                    disabled=True,
                    width=200,
                    color=ft.colors.WHITE,
                    bgcolor=ft.colors.BLUE
                ),
                
                ft.ProgressBar(
                    ref=progress_bar,
                    width=400,
                    value=0,
                    color=ft.colors.BLUE,
                    bgcolor=ft.colors.GREY_300
                ),
                
                ft.Text(
                    ref=status_text,
                    value="Готов к работе",
                    size=14,
                    weight=ft.FontWeight.BOLD,
                    text_align=ft.TextAlign.CENTER
                ),
                
                ft.ElevatedButton(
                    "Выход",
                    icon=ft.icons.EXIT_TO_APP,
                    on_click=exit_app,
                    width=200,
                    color=ft.colors.WHITE,
                    bgcolor=ft.colors.RED
                )
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=20
        )
    )

# Запуск приложения
if __name__ == "__main__":
    ft.app(target=main)