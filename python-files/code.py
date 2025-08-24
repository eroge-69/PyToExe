import os
from pathlib import Path

# Directori de prova a xifrar (creat prèviament)
target_dir = Path("C:/TestData")

# Llista d'extensions a "xifrar" (canviar l'extensió)
target_exts = ['.txt', '.docx', '.jpg']

# "Xifrat" simulat: simplement canvia l'extensió dels arxius a .LOCKED
for file_path in target_dir.rglob('*'):
    if file_path.suffix in target_exts:
        new_name = file_path.with_suffix('.LOCKED')
        os.rename(file_path, new_name)
        print(f"[+] Arxiu 'xifrat': {file_path.name} -> {new_name.name}")

# Deixa un "rescatt" simulat
ransom_note = target_dir / "LEGGIMI.txt"
ransom_note.write_text("""[SIMULACIÓ] Els teus arxius han estat xifrats.
Aquest és un exercici acadèmic de ciberseguretat.
No es requereix cap pagament.""")
print("[+] Atac simulat completat. Fitxer de rescat creat.")