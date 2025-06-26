import json
import os
import xlwt


json_dir = os.path.dirname(os.path.abspath(__file__))
json_name = r'data.json'
json_full_path = os.path.join(json_dir, json_name)
data = None
xls_data = []
no_email_users = []

with open(json_full_path, 'r', encoding='utf-8-sig') as file:
    data = json.load(file)

print("Пользователи без email, если таковые есть выведены ниже:")

for el in data['enrollees']:
    already_exists = False

    for xls_el in xls_data:
        if xls_el["last_name"] == el["surname"] and xls_el["first_name"] == el["name"] and \
                xls_el["mid_name"] == el["patronymic"] and xls_el["email"] == el["email"]:
            already_exists = True
            break

    if already_exists:
        continue

    new_xls_el = {
        "last_name": el["surname"],
        "first_name": el["name"],
        "mid_name": el["patronymic"],
        "email": el["email"],
        "status": "Абитуриент",
        "dept": "ПРИЁМНАЯ КАМПАНИЯ",
        "group": f"{el['PKname']}"
    }

    if not new_xls_el["email"].strip():
        already_exists = False

        for no_email_el in no_email_users:
            if no_email_el["last_name"] == el["surname"] and no_email_el["first_name"] == el["name"] and \
                    no_email_el["mid_name"] == el["patronymic"] and no_email_el["email"] == el["email"]:
                already_exists = True
                break

        if already_exists:
            continue

        print(f"""{el["surname"]} {el["name"]} {el["patronymic"]}""")
        no_email_users.append(new_xls_el)
        continue

    xls_data.append(new_xls_el)

workbook = xlwt.Workbook(encoding='utf-8')
worksheet = workbook.add_sheet('Сотрудники')

headers = ["last_name", "first_name", "mid_name", "email", "status", "dept", "group"]
for col, header in enumerate(headers):
    worksheet.write(0, col, header)

for row, employee in enumerate(xls_data, start=1):
    for col, field in enumerate(headers):
        worksheet.write(row, col, employee[field])

workbook.save('data.xls')
