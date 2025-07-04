import os
import subprocess
from tqdm import tqdm

# Détecte le dossier où se trouve le script
DOSSIER_SCRIPT = os.path.dirname(os.path.abspath(__file__))
source = DOSSIER_SCRIPT
destination = os.path.join(DOSSIER_SCRIPT, "compressed")

# Nom de la commande Ghostscript sous Windows
GHOSTSCRIPT = "gswin64c"  # Change à un chemin absolu si nécessaire

def compresser_pdf(input_path, output_path):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    gs_command = [
        GHOSTSCRIPT,
        "-sDEVICE=pdfwrite",
        "-dCompatibilityLevel=1.4",
        "-dPDFSETTINGS=/screen",  # Compression maximale
        "-dNOPAUSE",
        "-dQUIET",
        "-dBATCH",
        f"-sOutputFile={output_path}",
        input_path
    ]

    try:
        subprocess.run(gs_command, check=True)
        return True
    except subprocess.CalledProcessError:
        return False

def trouver_tous_les_pdfs(dossier_source):
    pdfs = []
    for racine, _, fichiers in os.walk(dossier_source):
        for fichier in fichiers:
            if fichier.lower().endswith(".pdf"):
                chemin_source = os.path.join(racine, fichier)
                # Ignore les fichiers déjà dans le dossier destination
                if destination in chemin_source:
                    continue
                chemin_relatif = os.path.relpath(chemin_source, dossier_source)
                pdfs.append((chemin_source, chemin_relatif))
    return pdfs

def compresser_dossier_pdfs(dossier_source, dossier_destination):
    pdfs = trouver_tous_les_pdfs(dossier_source)

    print(f"📄 {len(pdfs)} fichiers PDF à compresser dans : {dossier_destination}\n")
    for chemin_source, chemin_relatif in tqdm(pdfs, desc="Compression", unit="fichier"):
        chemin_dest = os.path.join(dossier_destination, chemin_relatif)
        success = compresser_pdf(chemin_source, chemin_dest)
        if not success:
            tqdm.write(f"❌ Erreur : {chemin_source}")

if __name__ == "__main__":
    compresser_dossier_pdfs(source, destination)
