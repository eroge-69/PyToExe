import pandas as pd
from lxml import etree

# Чтение Excel
df = pd.read_excel("АТК.xlsx", header=None)
rows = df[0].astype(str).tolist()

# Создание XML
root = etree.Element("unit_pack")
doc = etree.SubElement(root, "Document")
org = etree.SubElement(doc, "organisation")
id_info = etree.SubElement(org, "id_info")
etree.SubElement(id_info, "LP_info", LP_TIN="7724928886")

# Основной блок pack_content
pack_content = etree.SubElement(doc, "pack_content")

# Обработка строк
for row in rows:
    if row.startswith("(01)"):
        # Pack code - удаляем (01)
        pack_code = etree.SubElement(pack_content, "pack_code")
        pack_code.text = etree.CDATA(row[4:].strip())  # Удаляем первые 4 символа "(01)"
    elif row.startswith("(00)"):
        # Cis - удаляем (00)
        cis = etree.SubElement(pack_content, "cis")
        cis.text = etree.CDATA(row[4:].strip())  # Удаляем первые 4 символа "(00)"

# Сохранение в файл
with open("АТК.xml", "wb") as f:
    f.write(etree.tostring(
        root,
        encoding="UTF-8",
        pretty_print=True,
        xml_declaration=True,
        doctype='<?xml version="1.0" encoding="UTF-8"?>'
    ))

print("Готово! Файл АТК.xml создан.")