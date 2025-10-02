import re
import sys

def convertir_vers_cle(texte):
    lignes = texte.strip().splitlines()
    resultat = []

    # Chaque ligne typographique est transformée en format MycoClé : x,y $ texte $ $
    for ligne in lignes:
        ligne = ligne.strip()
        if not ligne:
            continue

        # Cherche motif "1. Texte ..." ou "12. Texte ..."
        match = re.match(r'^(\d+)\.?\s*(.*)$', ligne)
        if match:
            numero = match.group(1)
            texte = match.group(2).strip()
            # Détermine le renvoi (si "..." suivi d'un nombre)
            renvoi = None
            if "..." in texte:
                parts = texte.split("...")
                texte = parts[0].strip()
                renvoi = parts[1].strip()

            if renvoi:
                resultat.append(f"{numero},{renvoi} $ {texte} $ $")
            else:
                resultat.append(f"{numero} $ {texte} $ $")
        else:
            # ligne qui ne correspond pas au schéma attendu
            resultat.append(f"# Ligne ignorée : {ligne}")

    return "\n".join(resultat)


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python convert_cle.py input.txt output.cle")
        sys.exit(1)

    with open(sys.argv[1], "r", encoding="utf-8") as f:
        contenu = f.read()

    resultat = convertir_vers_cle(contenu)

    with open(sys.argv[2], "w", encoding="utf-8") as f:
        f.write(resultat)

    print(f"Conversion terminée. Résultat écrit dans {sys.argv[2]}")
