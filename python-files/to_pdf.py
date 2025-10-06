from openpyxl import Workbook, load_workbook
from pypdf import PdfReader

wb = ""
path = "dateien/Veranstaltungen 2024-Vorlage.xlsx"
pdf_path = "dateien/AntragVeranstalzungen.pdf"



def loading_workbook():
    global wb
    global path
    wb = load_workbook(path)
    sheet = wb.active
    return sheet
    
def load_pdf()-> list:
    global pdf_path
    reader = PdfReader(pdf_path)
    fields = reader.get_fields()
    return fields

sheet = loading_workbook()
pdf = load_pdf()


def make_dict()->dict:
    temp_dict = {}
    fields = load_pdf()
    field = list(fields.keys())
    for x in range(len(field)):
        temp_dict[field[x]] = fields[field[x]]["/V"]
    return (temp_dict)

#make a dictionary form the form answers
answer_dict = make_dict()


row = 5
cell = "A" + str(row)
while (cell != ""):
    cell = "A" + str(row)
    if sheet[cell].value == None:break
    row += 1


col_len = 1
head_list = []
head_letter = []
for letter in range(65,91):
    col = chr(letter) + "5"
    if sheet[col].value == None:break
    head_list.append(sheet[col].value)
    head_letter.append(chr(letter))

for item in head_list:
    if item in answer_dict: 
        cell = head_letter[head_list.index(item)] + "6"
        sheet[cell] = answer_dict[item]

print("put data in")
wb.save(path)
