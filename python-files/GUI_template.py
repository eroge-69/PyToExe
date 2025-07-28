import datetime
from pathlib import Path

import FreeSimpleGUI as sg
from docxtpl import DocxTemplate

document_path = Path('C:\Python') / "form.docx"
doc = DocxTemplate(document_path)

today = datetime.datetime.today()
today_in_one_week = today + datetime.timedelta(weeks=1)

layout = [
    [sg.Text("First name:"), sg.Input(key="FIRST_NAME", do_not_clear=False) ],
    [sg.Text("Last name:"), sg.Input(key="LAST_NAME", do_not_clear=False)],
    [sg.Text("Vendor name:"), sg.Input(key="VENDOR_NAME", do_not_clear=False)],
    [sg.Button("Create Sales Report"), sg.Exit()],
]

window = sg.Window("Sales Report Generator", layout, element_justification="right")

while True:
    event, values = window.read()
    if event == sg.WIN_CLOSED or event == "Exit":
        break
    if event == "Create Sales Report":
        values["TODAY"] = today.strftime("%Y-%m-%d")
        values["TODAY_IN_ONE_WEEK"] = today_in_one_week.strftime("%Y-%m-%d")

        doc.render(values)
        output_path = Path('C:\Python') / "Sales Report.docx"
        doc.save(output_path)
        sg.popup("File saved successfully!", f"File saved at {output_path}")

window.close()