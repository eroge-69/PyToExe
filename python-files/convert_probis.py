import sys
import os

def convert_to_probis_format_from_file(filename, output_file="pdb_probis_ready.txt"):
    """
    Lit un fichier contenant des codes PDB et les convertit au format ProBiS Web (pdb.chain).
    - Supprime les doublons
    - Trie par code PDB puis par chaîne
    - Accepte les formats '2i8b:A' et '2i8bA'
    - Sauvegarde automatiquement le résultat dans un fichier texte
    """
    with open(filename, "r") as f:
        content = f.read()

    raw_items = content.replace(",", " ").split()
    formatted = set()

    for item in raw_items:
        item = item.strip()
        if not item:
            continue
        if ":" in item:
            pdb, chain = item.split(":")
        else:
            pdb, chain = item[:4], item[4:]
        pdb = pdb.lower()
        chain = chain.upper()
        formatted.add(f"{pdb}.{chain}")
    
    sorted_list = sorted(formatted, key=lambda x: (x[:4], x[5:]))
    result = ", ".join(sorted_list)

    with open(output_file, "w") as f_out:
        f_out.write(result)

    print(f"\n✅ Format ProBiS prêt à coller ! Résultat sauvegardé dans '{output_file}'\n")
    print(result)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("❌ Glissez-déposez un fichier sur ce script ou donnez le chemin en argument.")
        input("\nAppuyez sur Entrée pour quitter...")
        sys.exit(1)
    
    input_file = sys.argv[1]
    
    if not os.path.isfile(input_file):
        print(f"❌ Fichier introuvable : {input_file}")
        input("\nAppuyez sur Entrée pour quitter...")
        sys.exit(1)
    
    convert_to_probis_format_from_file(input_file)
    input("\nAppuyez sur Entrée pour quitter...")
