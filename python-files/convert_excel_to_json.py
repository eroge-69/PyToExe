
import os
import pandas as pd
import json
import unicodedata
import re
import sys

# Função de normalização de texto
def normalize_text(text):
    if not isinstance(text, str):
        return text
    text = unicodedata.normalize('NFKD', text).encode('ASCII', 'ignore').decode('ASCII')  # Remove acentos
    text = re.sub(r'[^a-zA-Z0-9\s\-]', '', text)  # Remove caracteres especiais
    return text.upper()  # Converte para maiúsculo

# Função principal de processamento do arquivo
def process_uploaded_file(file_path):
    try:
        df = pd.read_excel(file_path, engine='openpyxl')
        levels = [f"Level {i}" for i in range(1, 11)]
        required_columns = levels + ["ID. Figura", "Description", "Fabricante/Fornecedor",
                                     "Referência comercial", "Código SAP", "Qtd", "Documentação",
                                     "Image URL1", "Image URL2", "Image URL3"]
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            print(f"Error: Missing required columns: {missing_columns}")
            return

        # Tratamento de strings e valores nulos
        df = df.astype(str).replace("nan", "").fillna("")

        def transform_url(url):
            if "https://drive.google.com/file/d/" in url and "/view?usp=drive_link" in url:
                file_id = url.split("/file/d/")[1].split("/view?usp=drive_link")[0]
                return f"https://drive.google.com/thumbnail?id={file_id}&sz=w800"
            return url

        def calculate_cadastro(subset):
            total = len(subset)
            non_blank = subset["Código SAP"].apply(lambda x: x != "").sum()
            percentage = (non_blank / total) * 100 if total > 0 else 0
            return f"{non_blank}/{total} ({percentage:.1f}%)"

        def build_hierarchy(df, levels, parent_level=0):
            if parent_level >= len(levels):
                return []
            hierarchy = []
            unique_items = df[levels[parent_level]].unique()
            for item in unique_items:
                if not item:
                    continue
                subset = df[df[levels[parent_level]] == item]
                id_figura = subset["ID. Figura"].iloc[0]
                id_figura = int(float(id_figura)) if id_figura.replace('.', '', 1).isdigit() else None
                node_name = f"{item} [{id_figura}]" if id_figura else item

                def to_int(value):
                    try:
                        return int(float(value.replace(',', '').strip()))
                    except ValueError:
                        return 0

                node = {
                    "name": normalize_text(node_name),
                    "originalname": normalize_text(item),
                    "idFigura": id_figura,
                    "description": normalize_text(subset["Description"].iloc[0]),
                    "fabricanteFornecedor": subset["Fabricante/Fornecedor"].iloc[0],
                    "referenciaComercial": subset["Referência comercial"].iloc[0],
                    "codigoSap": to_int(subset["Código SAP"].iloc[0]),
                    "qtd": to_int(subset["Qtd"].iloc[0]),
                    "documentation": subset["Documentação"].iloc[0],
                    "imageUrl1": transform_url(subset["Image URL1"].iloc[0]),
                    "imageUrl2": transform_url(subset["Image URL2"].iloc[0]),
                    "imageUrl3": transform_url(subset["Image URL3"].iloc[0]),
                    "cadastro": calculate_cadastro(subset),
                    "children": build_hierarchy(subset, levels, parent_level + 1)
                }
                hierarchy.append(node)
            return hierarchy

        hierarchy = build_hierarchy(df, levels)
        output_json_path = file_path.replace('.xlsx', '.json')
        with open(output_json_path, "w") as f:
            json.dump(hierarchy, f, indent=4)

        print(f"Hierarchy JSON saved at: {output_json_path}")

    except Exception as e:
        print(f"Error processing file: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python convert_excel_to_json.py <path_to_excel_file>")
    else:
        file_path = sys.argv[1]
        if not os.path.isfile(file_path):
            print(f"File not found: {file_path}")
        else:
            process_uploaded_file(file_path)
