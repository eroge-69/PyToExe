
import os
import re
import unicodedata
import argparse
import requests

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

def rename_file(path, new_name):
    dir_path = os.path.dirname(path)
    new_path = os.path.join(dir_path, new_name)
    if new_path != path:
        os.rename(path, new_path)
        print(f"Renombrado: {path} -> {new_path}")

def process_files(base_path: str, levels: int, options: dict, translate_lang=None):
    for root, dirs, files in os.walk(base_path):
        depth = root[len(base_path):].count(os.sep)
        if depth > levels:
            continue

        for d in list(dirs):
            new_name = normalize_text(d, **options)
            if translate_lang:
                new_name = translate_text(new_name, translate_lang)
            rename_file(os.path.join(root, d), new_name)

        for f in list(files):
            name, ext = os.path.splitext(f)
            new_name = normalize_text(name, **options)
            if translate_lang:
                new_name = translate_text(new_name, translate_lang)
            rename_file(os.path.join(root, f), new_name + ext)

def main():
    parser = argparse.ArgumentParser(description="Limpia y traduce nombres de archivos y carpetas.")
    parser.add_argument('--path', required=True, help='Ruta base de la carpeta')
    parser.add_argument('--levels', type=int, default=0, help='Niveles de subcarpetas a procesar')
    parser.add_argument('--remove-accents', action='store_true', help='Quitar acentos')
    parser.add_argument('--remove-symbols', action='store_true', help='Quitar símbolos')
    parser.add_argument('--remove-emojis', action='store_true', help='Quitar emojis')
    parser.add_argument('--remove-ascii', action='store_true', help='Quitar caracteres ASCII de control')
    parser.add_argument('--remove-commas', action='store_true', help='Quitar comas y puntos')
    parser.add_argument('--translate-to', choices=['es', 'en', 'ja', 'ko'], help='Idioma destino para traducción')

    args = parser.parse_args()
    options = {
        "remove_accents": args.remove_accents,
        "remove_symbols": args.remove_symbols,
        "remove_emojis": args.remove_emojis,
        "remove_ascii": args.remove_ascii,
        "remove_commas": args.remove_commas
    }

    process_files(args.path, args.levels, options, args.translate_to)

if __name__ == '__main__':
    main()
