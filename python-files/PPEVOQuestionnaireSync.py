import os
import re
import tkinter as tk
from tkinter import filedialog, messagebox

ALLOWED_LANGS = {"de", "de-CH", "it", "fr", "en"}

def extract_all_translations_from_gel(input_folder):
    all_translations = {}

    for lang in ALLOWED_LANGS:
        folder = os.path.join(input_folder, lang)
        if not os.path.isdir(folder):
            print(f"Warning: Folder '{lang}' not found.")
            continue

        print(f"\nReading translations from: {lang}")
        main_file, long_keys_file = get_translation_files(folder, lang)

        if not main_file:
            continue

        main_content = read_file(main_file)
        variable_map = extract_variable_definitions(read_file(long_keys_file)) if long_keys_file else {}
        all_translations[lang] = parse_translation_dict(main_content, variable_map)

    return all_translations

def get_translation_files(folder, lang):
    main_ts = long_keys_ts = None
    for file in os.listdir(folder):
        if file.endswith('.ts') and file.startswith(lang):
            main_ts = os.path.join(folder, file)
        elif file.startswith('quest-long_keys_'):
            long_keys_ts = os.path.join(folder, file)
    return main_ts, long_keys_ts

def read_file(path):
    with open(path, encoding='utf-8') as f:
        return f.read()

def extract_variable_definitions(content):
    return dict(re.findall(r'export const (\w+)\s*=\s*`([^`]*)`;', content))

def parse_translation_dict(content, var_map):
    translations = {k: v for k, v in re.findall(r'"(.*?)"\s*:\s*"(.*?)"', content)}
    for key_ref, value_ref in re.findall(r'\[(\w+)\]\s*:\s*(\w+)', content):
        key = var_map.get(key_ref, f"[{key_ref}]")
        value = var_map.get(value_ref, value_ref)
        translations[key] = value
    return translations

def add_english_reference(translations):
    if "de" in translations:
        translations["en"] = {k: k for k in translations["de"]}

def write_translation_combinations(translations, output_folder):
    os.makedirs(output_folder, exist_ok=True)
    for to_lang in ALLOWED_LANGS:
        path = os.path.join(output_folder, f'ppevo-questionnaire_{to_lang}.{to_lang}')
        with open(path, 'w', encoding='utf-8') as f:
            for from_lang in ALLOWED_LANGS:
                f.write(f"{from_lang} --> {to_lang}\n")
                from_trans = translations.get(from_lang, {})
                to_trans = translations.get(to_lang, {})
                for key, source_text in from_trans.items():
                    target_text = to_trans.get(key)
                    if not target_text:
                        continue
                    clean_source = normalize_newlines(source_text)
                    clean_target = normalize_newlines(target_text)
                    f.write(f'"{clean_source}"§"{clean_target}",\n')
                f.write("\n")

def normalize_newlines(text):
    return text.replace("\r\n", "\n").replace("\r", "\n").replace("\n", "\\n")

def run_process(input_path, output_path):
    try:
        translations = extract_all_translations_from_gel(input_path)
        add_english_reference(translations)
        write_translation_combinations(translations, output_path)
        messagebox.showinfo("Success", "Translation combinations written successfully!")
    except Exception as e:
        messagebox.showerror("Error", f"Something went wrong: {e}")

def browse_input():
    path = filedialog.askdirectory()
    if path:
        input_entry.delete(0, tk.END)
        input_entry.insert(0, path)

def browse_output():
    path = filedialog.askdirectory()
    if path:
        output_entry.delete(0, tk.END)
        output_entry.insert(0, path)

def on_run():
    input_path = input_entry.get()
    output_path = output_entry.get()
    if not input_path or not output_path:
        messagebox.showwarning("Missing info", "Please set both input and output folders.")
        return
    run_process(input_path, output_path)

# GUI
root = tk.Tk()
root.title("Translation Combination Tool")

tk.Label(root, text="Input Folder:").grid(row=0, column=0, padx=10, pady=5, sticky="e")
input_entry = tk.Entry(root, width=60)
input_entry.grid(row=0, column=1, padx=5, pady=5)
tk.Button(root, text="Browse", command=browse_input).grid(row=0, column=2, padx=5, pady=5)

tk.Label(root, text="Output Folder:").grid(row=1, column=0, padx=10, pady=5, sticky="e")
output_entry = tk.Entry(root, width=60)
output_entry.grid(row=1, column=1, padx=5, pady=5)
tk.Button(root, text="Browse", command=browse_output).grid(row=1, column=2, padx=5, pady=5)

tk.Button(root, text="Run", command=on_run, width=20).grid(row=2, column=1, pady=20)

root.mainloop()
