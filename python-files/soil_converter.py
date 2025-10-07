#!/usr/bin/env python3
"""
soil_converter.py

Конвертирует файл типа "2.xml" (структуры словарей SoilBox) в формат, похожий на файл "1.xml".
Usage:
    python soil_converter.py input_2.xml output_1.xml

Если аргументы не переданы, берёт /mnt/data/2.xml и пишет /mnt/data/converted_from_2_to_1.xml
"""

import sys
import xml.etree.ElementTree as ET
from xml.dom import minidom
import re
import os

def pretty_xml(element):
    s = ET.tostring(element, encoding='utf-8')
    parsed = minidom.parseString(s)
    return parsed.toprettyxml(indent="  ", encoding='utf-8')

def extract_cells(root):
    # Найдём все <data> элементы, у которых есть дочерний <CELL>
    datas = []
    for data in root.findall('.//data'):
        cell = data.find('CELL')
        if cell is not None:
            entry = {}
            id_el = data.find('ID')
            entry['ID'] = id_el.text.strip() if id_el is not None and id_el.text else None
            entry['CELL'] = cell.text.strip() if cell.text else ''
            disp = data.find('DISPL_TEXT')
            entry['DISPL_TEXT'] = disp.text.strip() if disp is not None and disp.text else ''
            datas.append(entry)
    return datas

def cell_prefix(cell):
    # Возвращаем буквенную префиксную часть CELL, например GR38 -> GR
    m = re.match(r'([A-Za-zА-Яа-я]+)', cell)
    return m.group(1) if m else ''

def build_output_tree(entries):
    Stg = ET.Element('Stg')
    Body = ET.SubElement(Stg, 'Body')
    GroundTable = ET.SubElement(Body, 'GroundTable')
    Grounds = ET.SubElement(GroundTable, 'Grounds', {'aType': '0'})
    for e in entries:
        gid = e.get('ID') or ''
        Ground = ET.SubElement(Grounds, 'Ground', {'Id': gid})
        SDHolder = ET.SubElement(Ground, 'SDHolder', {'aType': '0'})
        # Handle 1: cell code (e.g. GR38)
        ET.SubElement(SDHolder, 'Item', {'Handle': '1', 'DataType': '0', 'Value': e.get('CELL','')})
        # Handle 163: prefix of cell (like GR, VK) or 'AUTO' if empty
        pref = cell_prefix(e.get('CELL','')) or 'AUTO'
        ET.SubElement(SDHolder, 'Item', {'Handle': '163', 'DataType': '0', 'Value': pref})
        # Handle 21 and 22: description text — берем часть после " - " если есть, иначе весь DISPL_TEXT
        disp = e.get('DISPL_TEXT','')
        if ' - ' in disp:
            # возможен формат "GR38 - Суглинок"
            text = disp.split(' - ', 1)[1].strip()
        else:
            # попробуем убрать префикс "GR38" в начале если он есть
            text = re.sub(r'^\s*' + re.escape(e.get('CELL','')) + r'\s*[-:]*\s*', '', disp).strip()
            if not text:
                text = disp.strip()
        ET.SubElement(SDHolder, 'Item', {'Handle': '21', 'DataType': '0', 'Value': text})
        ET.SubElement(SDHolder, 'Item', {'Handle': '22', 'DataType': '0', 'Value': text})
    return Stg

def main():
    in_path = '/mnt/data/2.xml'
    out_path = '/mnt/data/converted_from_2_to_1.xml'
    argv = sys.argv[1:]
    if len(argv) >= 1:
        in_path = argv[0]
    if len(argv) >= 2:
        out_path = argv[1]

    if not os.path.exists(in_path):
        print("Input file not found:", in_path)
        sys.exit(2)

    # Попытка парсинга
    tree = ET.parse(in_path)
    root = tree.getroot()
    entries = extract_cells(root)
    if not entries:
        print("Не найдено записей <data> с <CELL> в файле", in_path)
        sys.exit(3)

    out_root = build_output_tree(entries)
    xml_bytes = pretty_xml(out_root)
    with open(out_path, 'wb') as f:
        f.write(xml_bytes)
    print("Converted", len(entries), "entries.")
    print("Output written to", out_path)

if __name__ == '__main__':
    main()
