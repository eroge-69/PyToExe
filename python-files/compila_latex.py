import zipfile
import os
import subprocess

# Nome dello zip
zip_name = "Fisica_1.zip"
extract_path = "Fisica_1"
output_dir = "output_pdf"

# Estrai lo zip
with zipfile.ZipFile(zip_name, 'r') as zip_ref:
    zip_ref.extractall(extract_path)

# Crea cartella output
os.makedirs(output_dir, exist_ok=True)

# Cerca file .tex
tex_files = []
for root, dirs, files in os.walk(extract_path):
    for f in files:
        if f.endswith(".tex"):
            tex_files.append(os.path.join(root, f))

# Compila ogni file .tex
for tex_path in tex_files:
    tex_dir = os.path.dirname(tex_path)
    tex_file = os.path.basename(tex_path)
    print(f"Compilo: {tex_file} ...")
    
    try:
        subprocess.run(
            ["pdflatex", "-interaction=nonstopmode", "-output-directory", output_dir, tex_path],
            check=True
        )
        print(f"✅ Creato PDF: {os.path.splitext(tex_file)[0]}.pdf")
    except subprocess.CalledProcessError:
        print(f"❌ Errore durante la compilazione di {tex_file}")

print("\n--- Operazione completata ---")
print(f"I PDF si trovano nella cartella: {output_dir}")
