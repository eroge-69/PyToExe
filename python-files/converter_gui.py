import tkinter as tk
from tkinter import filedialog, messagebox
import xml.etree.ElementTree as ET
import os

def loc_to_xml(src_file, dst_file):
    try:
        with open(src_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        root = ET.Element("Localization")

        for line in lines:
            if line.strip() == "":
                continue
            if "=" in line:
                key, value = line.strip().split("=", 1)
                text_elem = ET.SubElement(root, "text", id=key)
                text_elem.text = value

        tree = ET.ElementTree(root)
        tree.write(dst_file, encoding="utf-8", xml_declaration=True)
        messagebox.showinfo("Başarılı", f"{dst_file} oluşturuldu!")
    except Exception as e:
        messagebox.showerror("Hata", str(e))

def xml_to_loc(src_file, dst_file):
    try:
        tree = ET.parse(src_file)
        root = tree.getroot()

        with open(dst_file, 'w', encoding='utf-8') as f:
            for text_elem in root.findall("text"):
                key = text_elem.get("id")
                value = text_elem.text if text_elem.text else ""
                f.write(f"{key}={value}\n")
        messagebox.showinfo("Başarılı", f"{dst_file} oluşturuldu!")
    except Exception as e:
        messagebox.showerror("Hata", str(e))

def browse_src():
    file = filedialog.askopenfilename(filetypes=[("LOC ve XML Dosyaları", "*.loc *.xml")])
    entry_src.delete(0, tk.END)
    entry_src.insert(0, file)

def browse_dst():
    file = filedialog.asksaveasfilename(defaultextension=".xml", filetypes=[("LOC ve XML Dosyaları", "*.loc *.xml")])
    entry_dst.delete(0, tk.END)
    entry_dst.insert(0, file)

def convert():
    src_file = entry_src.get()
    dst_file = entry_dst.get()

    if not os.path.isfile(src_file):
        messagebox.showerror("Hata", "Kaynak dosya geçersiz!")
        return
    if not dst_file:
        messagebox.showerror("Hata", "Hedef dosya seçin!")
        return

    ext = os.path.splitext(src_file)[1].lower()
    if ext == ".loc":
        loc_to_xml(src_file, dst_file)
    elif ext == ".xml":
        xml_to_loc(src_file, dst_file)
    else:
        messagebox.showerror("Hata", "Desteklenmeyen dosya formatı! (.loc veya .xml olmalı)")

# GUI
root = tk.Tk()
root.title("Hitman 2 LOC ↔ XML Dönüştürücü")
root.geometry("500x200")

tk.Label(root, text="Kaynak Dosya:").pack(pady=5)
entry_src = tk.Entry(root, width=60)
entry_src.pack(pady=5)
tk.Button(root, text="Gözat", command=browse_src).pack(pady=5)

tk.Label(root, text="Hedef Dosya:").pack(pady=5)
entry_dst = tk.Entry(root, width=60)
entry_dst.pack(pady=5)
tk.Button(root, text="Gözat", command=browse_dst).pack(pady=5)

tk.Button(root, text="Dönüştür", command=convert, bg="green", fg="white").pack(pady=20)

root.mainloop()
