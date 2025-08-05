
import fitz  # PyMuPDF
from email.message import EmailMessage
import sys
import os

def extraire_infos_depuis_pdf(fichier_pdf):
    doc = fitz.open(fichier_pdf)
    texte = ""
    for page in doc:
        texte += page.get_text()
    return texte

def generer_mail(depuis_pdf):
    texte = extraire_infos_depuis_pdf(depuis_pdf)

    mail = EmailMessage()
    mail['Subject'] = "Demande de devis – 15 Meubles MARBLE V2 – Ref. 00114946"
    mail['To'] = "fournisseur@example.com"
    mail['From'] = "vous@example.com"

    corps = f"""Bonjour,

Je vous contacte pour obtenir un devis concernant une commande de 15 meubles MARBLE V2, modèle DAILY – Meuble France, avec les caractéristiques suivantes :

🔹 Dimensions :
- Hauteur extérieure : 3290 mm
- Hauteur intérieure : 2300 mm
- Largeur intérieure utile sur plinthe : 2146 mm
- Longueur intérieure utile sur plinthe : 4246 mm

🔹 Aménagements demandés :
- Bois chêne (caisse)
- 3 étagères
- 2 tiroirs
- Roulettes
- Châssis : caisse standard

🔹 Informations complémentaires :
- Référence devis : 00114946
- Projet client : PETIT MEUBLE CORP
- Quantité : 15 unités
- Demande initiée par : Olivier MAMOUD – Agence ORLY

Je vous joins le document client pour référence. Merci de me transmettre votre meilleur tarif et délai de livraison.

Bien cordialement,
[Votre prénom NOM]
[Votre entreprise]
[Coordonnées]
"""
    mail.set_content(corps)

    nom_fichier = os.path.splitext(os.path.basename(depuis_pdf))[0]
    chemin_eml = os.path.join(os.path.dirname(depuis_pdf), f"{nom_fichier}_devis.eml")
    with open(chemin_eml, "wb") as f:
        f.write(bytes(mail))
    print(f"✅ Fichier .eml généré : {chemin_eml}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Veuillez glisser un fichier PDF sur l'exécutable.")
        input("Appuyez sur Entrée pour quitter.")
        sys.exit(1)
    generer_mail(sys.argv[1])
