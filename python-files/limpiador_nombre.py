import os
import re
import unicodedata
import argparse
import requests
from typing import List
from tkinter import filedialog, Tk, messagebox

# Configura tu API de LibreTranslate
LIBRETRANSLATE_API_URL = "https://libretranslate.com/translate"
LIBRETRANSLATE_DETECT_URL = "https://libretranslate.com/detect"

def normalize_text(text: str, remove_accents=True, remove_symbols=True, remove_emojis=True, remove_ascii=True, remove_commas=True) -> str:
    original = text
    if remove_accents:
        text = unicodedata.normalize('NFD', text)
        text = text.encode('ascii', 'ignore').decode('utf-8')
    if remove_emojis:
        emoji_pattern = re.compile("[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF]+", flags=re.UNICODE)
        text = emoji_pattern.sub('', text)
    if remove_symbols:
        text = re.sub(r'[\!\"\#\$%&\'()*+/<=>?@[\\\]^_`{|}~]', '', text)
    if remove_commas:
        text = text.replace(',', '').replace('.', '')
    if remove_ascii:
        text = re.sub(r'[\x00-\x1F\x7F-\x9F]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    print(f"Normalizado '{original}' -> '{text}'")
    return text

def translate_text(text: str, target_lang: str) -> str:
    try:
        response = requests.post(LIBRETRANSLATE_API_URL, json={
            "q": text,
            "source": "auto",
            "target": target_lang,
            "format": "text"
        })
        result = response.json()
        return result.get("translatedText", text)
    except Exception as e:
        print(f"Error en traducción: {e}")
        return text

def detect_language(text: str) -> str:
    try:
        response = requests.post(LIBRETRANSLATE_DETECT_URL, json={"q": text})
        result = response.json()
        return result[0].get("language", "unknown") if result else "unknown"
    except Exception as e:
        print(f"Error en detección: {e}")
        return "unknown"

def rename_file(path, new_name):
    dir_path = os.path.dirname(path)
    new_path = os.path.join(dir_path, new_name)
    if new_path != path:
        os.rename(path, new_path)
        print(f"Renombrado: {path} -> {new_path}")

def process_files(base_path: str, levels: int, options: dict, apply_to_files=True, apply_to_dirs=True):
    for root, dirs, files in os.walk(base_path):
        depth = root[len(base_path):].count(os.sep)
        if depth > levels:
            continue

        if apply_to_dirs:
            for d in dirs:
                new_name = normalize_text(d, **options)
                rename_file(os.path.join(root, d), new_name)

        if apply_to_files:
            for f in files:
                name, ext = os.path.splitext(f)
                new_name = normalize_text(name, **options) + ext
                rename_file(os.path.join(root, f), new_name)

def run_gui():
    root = Tk()
    root.withdraw()
    folder = filedialog.askdirectory(title="Selecciona una carpeta para procesar")
    if not folder:
        messagebox.showinfo("Cancelado", "No se seleccionó carpeta.")
        return

    levels = int(input("Niveles de subcarpetas a procesar: "))

    # Opciones de limpieza
    options = {
        "remove_accents": messagebox.askyesno("Quitar acentos", "Deseas quitar acentos?"),
        "remove_symbols": messagebox.askyesno("Quitar símbolos", "Deseas quitar símbolos?"),
        "remove_emojis": messagebox.askyesno("Quitar emojis", "Deseas quitar emojis?"),
        "remove_ascii": messagebox.askyesno("Quitar ASCII", "Deseas quitar caracteres ASCII de control?"),
        "remove_commas": messagebox.askyesno("Quitar comas/puntos", "Deseas quitar comas y puntos?"),
    }

    # Traducción / detección de idioma
    translate_option = messagebox.askyesno("Traducir", "Deseas traducir nombres?")
    if translate_option:
        lang = input("Idioma de destino (es, en, ja, ko): ")
        for dirpath, _, filenames in os.walk(folder):
            for filename in filenames:
                new_name = translate_text(filename, lang)
                rename_file(os.path.join(dirpath, filename), new_name)

    process_files(folder, levels, options)
    messagebox.showinfo("Completado", "Proceso de limpieza finalizado.")

if __name__ == '__main__':
    run_gui()
