
import os
import zipfile
import PySimpleGUI as sg
from PyPDF2 import PdfReader, PdfWriter

def split_purchase_orders(input_pdf, output_zip, mapping):
    reader = PdfReader(input_pdf)
    with zipfile.ZipFile(output_zip, 'w') as zipf:
        for page_num, (order_no, pjt_nos, supplier) in mapping.items():
            writer = PdfWriter()
            writer.add_page(reader.pages[page_num])
            pjt_formatted = ", ".join(pjt_nos)
            filename = f"{order_no} 발주서({pjt_formatted}) - {supplier}.pdf"
            temp_path = os.path.join(os.path.dirname(output_zip), filename)
            with open(temp_path, "wb") as f:
                writer.write(f)
            zipf.write(temp_path, arcname=filename)
            os.remove(temp_path)

# 기본 GUI
sg.theme('LightBlue2')

layout = [
    [sg.Text('PDF 파일 선택:'), sg.Input(key='-PDF-'), sg.FileBrowse(file_types=(("PDF Files", "*.pdf"),))],
    [sg.Text('출력 ZIP 경로:'), sg.Input(key='-ZIP-'), sg.FileSaveAs(file_types=(("ZIP Files", "*.zip"),), default_extension="zip")],
    [sg.Button('실행'), sg.Button('종료')]
]

window = sg.Window('발주서 자동 분리기', layout)

while True:
    event, values = window.read()
    if event in (sg.WINDOW_CLOSED, '종료'):
        break
    if event == '실행':
        input_pdf = values['-PDF-']
        output_zip = values['-ZIP-']
        if not input_pdf or not output_zip:
            sg.popup_error("PDF 파일과 출력 경로를 모두 입력하세요.")
            continue
        try:
            sample_mapping = {
                0: ("YO-25-070777", ["250", "460"], "저스텍"),
                1: ("YO-25-070778", ["461"], "성원정밀"),
                2: ("YO-25-070779", ["921"], "마스트"),
                3: ("YO-25-070780", ["921"], "한두산업"),
                4: ("YO-25-070781", ["921"], "삼영시스템"),
                5: ("YO-25-070782", ["921"], "티엠에스"),
                6: ("YO-25-070783", ["921"], "와이엔에스테크닉스"),
                7: ("YO-25-070784", ["921"], "거성엔아이"),
                8: ("YO-25-070785", ["921"], "NWT밀텍"),
                9: ("YO-25-070786", ["921"], "바이스코리아"),
            }
            split_purchase_orders(input_pdf, output_zip, sample_mapping)
            sg.popup("완료", f"ZIP 파일이 생성되었습니다:\n{output_zip}")
        except Exception as e:
            sg.popup_error("오류 발생", str(e))

window.close()
