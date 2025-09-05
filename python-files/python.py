import xml.etree.ElementTree as ET
from pathlib import Path

# --- Escolher ficheiro ---
ficheiro = input("👉 Arraste o ficheiro XML aqui e pressione Enter: ").strip().strip('"')

# Se o utilizador só escreveu o nome
ficheiro = Path(ficheiro)

if not ficheiro.exists():
    print(f"❌ Ficheiro não encontrado: {ficheiro}")
    exit(1)

# --- Escolher campo a procurar ---
campo = input("🔍 Qual campo deseja procurar? (CustomerID / CustomerTaxID): ").strip()

if campo not in ["CustomerID", "CustomerTaxID"]:
    print("❌ Campo inválido! Apenas CustomerID ou CustomerTaxID.")
    exit(1)

# --- Ler ficheiro ---
tree = ET.parse(ficheiro)
root = tree.getroot()

encontrado = False

for elem in root.iter(campo):
    valor = elem.text.strip() if elem.text else ""

    print(f"{campo}: {valor}")

    if len(valor) > 30:
        print(f"⚠️ Encontrado {campo} com mais de 30 caracteres!")
        print(f"➡️ Valor a corrigir: {valor}")
        encontrado = True

if not encontrado:
    print(f"✅ Nenhum {campo} com mais de 30 caracteres encontrado.")
