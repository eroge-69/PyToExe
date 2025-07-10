
import xml.etree.ElementTree as ET
from collections import defaultdict
import tkinter as tk
from tkinter import filedialog, messagebox
import zipfile
import os
import re
import pandas as pd

KML_NS = {'kml': 'http://www.opengis.net/kml/2.2'}

def extract_kml_from_kmz(kmz_path, extract_to="./kmz_temp"):
    with zipfile.ZipFile(kmz_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)
    return os.path.join(extract_to, 'doc.kml')

def count_mufty_subfolders(file_path):
    tree = ET.parse(file_path)
    root = tree.getroot()
    document = root.find('kml:Document', KML_NS)
    mufty_folder = None
    for folder in document.findall('.//kml:Folder', KML_NS):
        name = folder.find('kml:name', KML_NS)
        if name is not None and name.text.strip() == 'Муфты':
            mufty_folder = folder
            break
    counts = {"Абонентская": 0, "Распределительная": 0}
    if mufty_folder:
        for subfolder in mufty_folder.findall('kml:Folder', KML_NS):
            sub_name = subfolder.find('kml:name', KML_NS)
            if sub_name is None:
                continue
            sub_name_text = sub_name.text.strip()
            placemarks = subfolder.findall('.//kml:Placemark', KML_NS)
            counts[sub_name_text] = len(placemarks)
    return counts

def extract_vok_data_with_style_id(document):
    for folder in document.findall('.//kml:Folder', KML_NS):
        name = folder.find('kml:name', KML_NS)
        if name is not None and name.text.strip() == 'ВОК':
            return extract_all_placemarks_with_id(folder)
    return []

def extract_all_placemarks_with_id(vok_folder):
    placemarks = []
    for subfolder in vok_folder.findall('kml:Folder', KML_NS):
        sub_name = subfolder.find('kml:name', KML_NS)
        if sub_name is None:
            continue
        if sub_name.text.strip() not in ['Магистральный', 'Распределительный']:
            continue
        for placemark in subfolder.findall('kml:Placemark', KML_NS):
            name_elem = placemark.find('kml:name', KML_NS)
            style_elem = placemark.find('kml:styleUrl', KML_NS)
            name = name_elem.text.strip() if name_elem is not None else None
            style_ref = style_elem.text.strip().lstrip('#') if style_elem is not None else None
            placemarks.append({'name': name, 'style_id': style_ref})
    return placemarks

def get_resolved_style_colors(document):
    style_map_refs = {}
    style_colors = {}
    for stylemap in document.findall('.//kml:StyleMap', KML_NS):
        map_id = stylemap.attrib.get('id')
        for pair in stylemap.findall('kml:Pair', KML_NS):
            key = pair.find('kml:key', KML_NS)
            style_ref = pair.find('kml:styleUrl', KML_NS)
            if key is not None and key.text == 'normal' and style_ref is not None:
                ref_id = style_ref.text.strip().lstrip('#')
                style_map_refs[map_id] = ref_id
    for style in document.findall('.//kml:Style', KML_NS):
        style_id = style.attrib.get('id')
        color_elem = style.find('.//kml:LineStyle/kml:color', KML_NS)
        color = color_elem.text.strip() if color_elem is not None else None
        if style_id and color:
            style_colors[style_id] = color
    resolved_styles = {}
    resolved_styles.update(style_colors)
    for sid, mapped_id in style_map_refs.items():
        if mapped_id in style_colors:
            resolved_styles[sid] = style_colors[mapped_id]
    return resolved_styles

def process_vok_color_totals(file_path):
    tree = ET.parse(file_path)
    root = tree.getroot()
    document = root.find('kml:Document', KML_NS)
    resolved_colors = get_resolved_style_colors(document)
    placemarks = extract_vok_data_with_style_id(document)
    color_totals = defaultdict(int)
    for pm in placemarks:
        name = pm['name']
        style_id = pm['style_id']
        color = resolved_colors.get(style_id)
        if not color:
            continue
        match = re.search(r'^\d+$', name or "")
        if match:
            number = int(match.group())
            color_totals[color] += number
    return dict(color_totals)

def process_zazhimy_kml(file_path):
    result = {}
    tree = ET.parse(file_path)
    root = tree.getroot()
    document = root.find('kml:Document', KML_NS)
    zazhimy_folder = None
    for folder in document.findall('.//kml:Folder', KML_NS):
        name_elem = folder.find('kml:name', KML_NS)
        if name_elem is not None and name_elem.text.strip() == 'Зажимы':
            zazhimy_folder = folder
            break
    if zazhimy_folder is None:
        return {}
    for subfolder in zazhimy_folder.findall('kml:Folder', KML_NS):
        sub_name_elem = subfolder.find('kml:name', KML_NS)
        subfolder_name = sub_name_elem.text.strip() if sub_name_elem is not None else "Без имени"
        a_total, b_total = 0, 0
        for placemark in subfolder.findall('kml:Placemark', KML_NS):
            name_elem = placemark.find('kml:name', KML_NS)
            name = name_elem.text.strip() if name_elem is not None else None
            if name:
                match = re.search(r'(\d+)\s*/\s*(\d+)', name)
                if match:
                    a = int(match.group(1))
                    b = int(match.group(2))
                    a_total += a
                    b_total += b
        result[subfolder_name] = f"{a_total}/{b_total}"
    return result

def main():
    root = tk.Tk()
    root.withdraw()
    kmz_path = filedialog.askopenfilename(title="Выберите .KMZ файл", filetypes=[("KMZ files", "*.kmz")])
    if not kmz_path:
        messagebox.showinfo("Отмена", "Файл не выбран.")
        return

    kml_path = extract_kml_from_kmz(kmz_path)
    mufty = count_mufty_subfolders(kml_path)
    vok = process_vok_color_totals(kml_path)
    zazhimy = process_zazhimy_kml(kml_path)

    df = pd.DataFrame({
        "Муфты - Абонентская": [mufty["Абонентская"]],
        "Муфты - Распределительная": [mufty["Распределительная"]],
        "Зажимы (всего подпапок)": [len(zazhimy)],
        "ВОК - Цветов найдено": [len(vok)],
        "ВОК - Суммарные волокна": [sum(vok.values())]
    })

    excel_path = os.path.splitext(kmz_path)[0] + "_анализ.xlsx"
    df.to_excel(excel_path, index=False)

    messagebox.showinfo("Готово", f"Анализ завершён. Excel-файл:
{excel_path}")

if __name__ == "__main__":
    main()
