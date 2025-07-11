
import os
import glob
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
import xml.etree.ElementTree as ET
import pandas as pd

def parse_xml_files(folder_path):
    all_data = []

    xml_files = glob.glob(os.path.join(folder_path, "*.xml"))

    for xml_file in xml_files:
        try:
            tree = ET.parse(xml_file)
            root = tree.getroot()

            data = {
                "DosyaAdı": os.path.basename(xml_file),
                "KeyToolId": root.findtext("KeyToolId"),
                "ToolDescription": root.findtext("ToolDescription"),
                "KeyMachine": root.findtext("KeyMachine"),
                "AdapterDesc": root.findtext("AdapterDesc"),
                "ToolTypeDesc": root.findtext("ToolTypeDesc"),
                "ToolImage": root.findtext("ToolImage"),
                "PostProcParameterStage": root.findtext("PostProcParameterStage"),
                "isAngleHeadTool": root.findtext("isAngleHeadTool"),
                "RotationAngle": root.findtext("RotationAngle"),
                "ToolAngle": root.findtext("ToolAngle"),
                "midDeviation": root.findtext("midDeviation"),
                "ahHeight": root.findtext("ahHeight"),
                "ahWidth": root.findtext("ahWidth"),
                "shankdiameter": root.findtext("shankdiameter")
            }

            stage = root.find("STAGE")
            if stage is not None:
                for elem in stage:
                    if elem.tag != "DOCUMENT" and elem.tag != "AdditionalFields":
                        data[elem.tag] = elem.text

            document = stage.find("DOCUMENT") if stage is not None else None
            if document is not None:
                data["DocName"] = document.findtext("DocName")
                data["DocPath"] = document.findtext("DocPath")

            all_data.append(data)
        except Exception as e:
            print(f"Hata: {xml_file} - {e}")

    return pd.DataFrame(all_data)

def select_folder():
    folder_selected = filedialog.askdirectory()
    if folder_selected:
        entry_var.set(folder_selected)

def run_conversion():
    folder = entry_var.get()
    if not folder:
        messagebox.showerror("Hata", "Lütfen bir klasör seçin.")
        return

    output_name = simpledialog.askstring("Dosya Adı", "Excel dosyasının adını girin (uzantı olmadan):")
    if not output_name:
        messagebox.showerror("Hata", "Dosya adı boş olamaz.")
        return

    try:
        df = parse_xml_files(folder)
        output_path = os.path.join(folder, f"{output_name}.xlsx")
        df.to_excel(output_path, index=False)
        messagebox.showinfo("Başarılı", f"Excel dosyası kaydedildi:\n{output_path}")
    except Exception as e:
        messagebox.showerror("Hata", str(e))

# Arayüz
root = tk.Tk()
root.title("HAIMER XML")
root.geometry("500x200")
root.resizable(False, False)

entry_var = tk.StringVar()

label = tk.Label(root, text="XML dosyalarının bulunduğu klasörü seçin:")
label.pack(pady=10)

entry = tk.Entry(root, textvariable=entry_var, width=60)
entry.pack()

browse_btn = tk.Button(root, text="Klasör Seç", command=select_folder)
browse_btn.pack(pady=5)

convert_btn = tk.Button(root, text="Dönüştür ve Excel'e Kaydet", command=run_conversion)
convert_btn.pack(pady=10)

root.mainloop()
