import pandas as pd

# Charger le fichier Excel
FICHIER = "C:\\Users\\MariemBY\\Downloads\\Etat d'avancement des travaux de migration.xlsx"  # Remplace par ton vrai fichier
df = pd.read_excel(
    FICHIER,
    converters={0: lambda x: str(x).replace('\u00A0', ' ').strip()}  # 0 = 1ère colonne (A)
)

# Saisie du code et nettoyage des espaces
code_saisi = input("Entrez le code (colonne A) : ").replace('\u00A0', ' ').strip()

# 1) Tentative de correspondance exacte en texte
colA_txt = df.iloc[:, 0].astype(str).str.replace('\u00A0', ' ', regex=False).str.strip()
mask = colA_txt == code_saisi

# 2) Si rien trouvé, tentative en numérique (utile si Excel a transformé 00123 -> 123.0)
if not mask.any():
    try:
        # convertir l'entrée en nombre (gère virgule ou point)
        code_num = float(code_saisi.replace(',', '.'))
        colA_num = pd.to_numeric(colA_txt.str.replace(',', '.', regex=False), errors='coerce')
        mask = colA_num == code_num
    except ValueError:
        pass  # l'entrée n'est pas numérique, on ignore

if mask.any():
    # Colonnes D à K = indices 3 à 10 inclus
    colonnes_a_afficher = [df.columns[1]] + list(df.columns[3:11])
    resultat = df.loc[mask, colonnes_a_afficher]
    print(resultat.to_string(index=False))
else:
    print("❌ Code introuvable.")
    print("\nAstuce : vérifie les espaces/accents invisibles, les zéros en tête, et le format du code.")
    # Optionnel : afficher quelques codes lus pour diagnostic
    print("\nExemples de codes lus (10 premiers) :")
    print(colA_txt.head(10).tolist())
