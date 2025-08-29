import xml.etree.ElementTree as ET
import tkinter as tk
import locale
import csv
import os
from tkinter import filedialog, messagebox

# Set locale to system default (to ensure correct sorting method for rows)
locale.setlocale(locale.LC_ALL, '')

# Create a dialog to choose export option
root = tk.Tk()
root.withdraw()

# Ask user if they want to export full entity info
export_full_entity_info = messagebox.askyesno(
    title="エクスポートオプション",
    message="各列の完全なエンティティ情報をエクスポートしますか？\n（「はい」で完全な情報を、「いいえ」で最初の列のみ）"
)

# Create a file dialog to choose the XML file
xml_path = filedialog.askopenfilename(
    title="EDMまたはXMLファイルを選択",
    filetypes=[("EDM/XMLファイル", "*.xml *.EDM"), ("すべてのファイル", "*.*")]
)

if not xml_path:
    print("ファイルが選択されていません。終了します。")
    exit()

# Choose where to save CSV
csv_path = filedialog.asksaveasfilename(
    title="CSVファイルとして保存",
    defaultextension=".csv",
    filetypes=[("CSVファイル", "*.csv"), ("すべてのファイル", "*.*")]
)

if not csv_path:
    print("出力ファイルが選択されていません。終了します。")
    exit()

# Parse XML
tree = ET.parse(xml_path)
root = tree.getroot()

# Build DBMAPPING dictionary: {id: (name, database)}
dbmapping_dict = {}
for mapping in root.findall('./DBMAPPING'):
    id_ = mapping.attrib.get('ID')
    name = mapping.attrib.get('NAME')
    database = mapping.attrib.get('DATABASE')
    if id_:
        dbmapping_dict[id_] = (name, database)

with open(csv_path, mode='w', newline='', encoding='utf-8') as file:
    # Read XML
    rows = []
    for entity in root.findall('ENTITY'):
        table_name = entity.attrib.get('P-NAME')
        entity_name = entity.attrib.get('L-NAME')
        dbmapping_id = entity.attrib.get('DBMAPPINGID')
        database_name, schema_name = dbmapping_dict.get(dbmapping_id, ("", ""))
        for attr in entity.findall('ATTR'):
            pk = attr.attrib.get('PK')
            column_name = attr.attrib.get('P-NAME')
            attribute_name = attr.attrib.get('L-NAME')
            data_type = attr.attrib.get('DATATYPE')
            length = attr.attrib.get('LENGTH')
            is_required = attr.attrib.get('NULL')
            default_value = attr.attrib.get('DEF').upper()
            description = attr.attrib.get('COMMENT')
            collate = attr.attrib.get('COLLATE')
            rows.append([table_name, entity_name, database_name, schema_name, pk, column_name, attribute_name, data_type, length, is_required, default_value, description, collate])

    # Sort by table name (index 0)
    rows.sort(key=lambda x: locale.strxfrm(x[0] or ""))
    
    # Write to CSV
    writer = csv.writer(file)
    writer.writerow([
        "テーブル名",
        "エンティティ名",
        "データベース名",
        "スキーマ名",
        "PK",
        "列名",
        "属性名",
        "データ型",
        "長さ",
        "必須",
        "デフォルト値",
        "説明",
        "照合"
    ])
    
    prev_entity = None
    for row in rows:
        current_entity = (row[0], row[1], row[2], row[3])
        if current_entity == prev_entity and not export_full_entity_info:
            writer.writerow(["", "", "", "", row[4], row[5], row[6], row[7], row[8], row[9], row[10], row[11], row[12]])
        else:
            writer.writerow(row)
            prev_entity = current_entity

print(f"完了！CSVが保存されました：{os.path.abspath(csv_path)}")