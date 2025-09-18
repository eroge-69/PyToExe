from fpdf import FPDF
from num2words import num2words
from datetime import datetime

# Informations de la société (fixes)
COMPANY_INFO = {
    "name": "Ste Amin De Métaux",
    "activity": "Collecte Déchets",
    "address": "Route Tunis km 10 SFAX",
    "tel": "23133750 / 25121695",
    "mf": "1568883E/A/M/000"
}

class DocumentPDF(FPDF):
    def header(self):
        self.set_font("Arial", "B", 16)
        self.cell(0, 10, COMPANY_INFO["name"], ln=1, align="C")
        self.set_font("Arial", "", 12)
        self.cell(0, 8, COMPANY_INFO["activity"], ln=1, align="C")
        self.cell(0, 8, COMPANY_INFO["address"], ln=1, align="C")
        self.cell(0, 8, f"Tél: {COMPANY_INFO['tel']}", ln=1, align="C")
        self.cell(0, 8, f"MF: {COMPANY_INFO['mf']}", ln=1, align="C")
        self.ln(5)

def generer_facture(
    num_facture,
    date_facture,
    client_nom,
    client_mf,
    client_adresse,
    description,
    montant_ht,
    taux_tva,
    montant_tambre=1.0,
    fichier="facture.pdf"
):
    pdf = DocumentPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "FACTURE", ln=1, align="C")
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 8, f"Facture N°: {num_facture}", ln=1)
    pdf.cell(0, 8, f"Date: {date_facture}", ln=1)
    pdf.cell(0, 8, f"Client: {client_nom}", ln=1)
    pdf.cell(0, 8, f"MF Client: {client_mf}", ln=1)
    pdf.cell(0, 8, f"Adresse Client: {client_adresse}", ln=1)
    pdf.ln(5)
    pdf.cell(0, 8, f"Désignation: {description}", ln=1)
    pdf.cell(0, 8, f"Montant HT: {montant_ht:.3f} DT", ln=1)
    montant_tva = montant_ht * taux_tva / 100
    pdf.cell(0, 8, f"TVA ({taux_tva}%): {montant_tva:.3f} DT", ln=1)
    pdf.cell(0, 8, f"Tambre: {montant_tambre:.3f} DT", ln=1)
    montant_total = montant_ht + montant_tva + montant_tambre
    pdf.cell(0, 8, f"Total TTC: {montant_total:.3f} DT", ln=1)
    pdf.ln(5)
    montant_lettres = num2words(montant_total, lang="fr") + " dinars"
    pdf.cell(0, 8, f"Arrêtée la présente facture à la somme de: {montant_lettres}", ln=1)
    pdf.ln(20)
    pdf.cell(0, 8, "Signature", ln=1, align="R")
    pdf.output(fichier)
    print(f"Facture générée : {fichier}")

def generer_bon_livraison(
    num_bl,
    date_bl,
    client_nom,
    client_mf,
    client_adresse,
    description,
    quantite,
    chauffeur_nom,
    matricule_voiture,
    fichier="bon_livraison.pdf"
):
    pdf = DocumentPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "BON DE LIVRAISON", ln=1, align="C")
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 8, f"Bon de livraison N°: {num_bl}", ln=1)
    pdf.cell(0, 8, f"Date: {date_bl}", ln=1)
    pdf.cell(0, 8, f"Client: {client_nom}", ln=1)
    pdf.cell(0, 8, f"MF Client: {client_mf}", ln=1)
    pdf.cell(0, 8, f"Adresse Client: {client_adresse}", ln=1)
    pdf.ln(5)
    pdf.cell(0, 8, f"Désignation: {description}", ln=1)
    pdf.cell(0, 8, f"Quantité: {quantite}", ln=1)
    pdf.ln(20)
    pdf.cell(0, 8, f"Nom du chauffeur: {chauffeur_nom}", ln=1)
    pdf.cell(0, 8, f"Matricule du voiture: {matricule_voiture}", ln=1)
    pdf.ln(15)
    pdf.cell(0, 8, "Signature", ln=1, align="R")
    pdf.output(fichier)
    print(f"Bon de livraison généré : {fichier}")

def generer_bon_sortie(
    num_bs,
    date_bs,
    client_nom,
    client_mf,
    client_adresse,
    description,
    quantite,
    chauffeur_nom,
    matricule_voiture,
    fichier="bon_sortie.pdf"
):
    pdf = DocumentPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "BON DE SORTIE", ln=1, align="C")
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 8, f"Bon de sortie N°: {num_bs}", ln=1)
    pdf.cell(0, 8, f"Date: {date_bs}", ln=1)
    pdf.cell(0, 8, f"Client: {client_nom}", ln=1)
    pdf.cell(0, 8, f"MF Client: {client_mf}", ln=1)
    pdf.cell(0, 8, f"Adresse Client: {client_adresse}", ln=1)
    pdf.ln(5)
    pdf.cell(0, 8, f"Désignation: {description}", ln=1)
    pdf.cell(0, 8, f"Quantité: {quantite}", ln=1)
    pdf.ln(20)
    pdf.cell(0, 8, f"Nom du chauffeur: {chauffeur_nom}", ln=1)
    pdf.cell(0, 8, f"Matricule du voiture: {matricule_voiture}", ln=1)
    pdf.ln(15)
    pdf.cell(0, 8, "Signature", ln=1, align="R")
    pdf.output(fichier)
    print(f"Bon de sortie généré : {fichier}")

# Exemple d’utilisation des trois fonctions
if __name__ == "__main__":
    # Facture
    generer_facture(
        num_facture="2025-001",
        date_facture="18/09/2025",
        client_nom="Société Client SARL",
        client_mf="1234567A/M/000",
        client_adresse="Avenue Habib Bourguiba, Tunis",
        description="Collecte de déchets industriels",
        montant_ht=1200.0,
        taux_tva=19,
        montant_tambre=1.000,
        fichier="facture.pdf"
    )
    # Bon de Livraison
    generer_bon_livraison(
        num_bl="BL-2025-001",
        date_bl="18/09/2025",
        client_nom="Société Client SARL",
        client_mf="1234567A/M/000",
        client_adresse="Avenue Habib Bourguiba, Tunis",
        description="Déchets industriels",
        quantite="5 tonnes",
        chauffeur_nom="Ali Ben Salem",
        matricule_voiture="123 TU 4567",
        fichier="bon_livraison.pdf"
    )
    # Bon de Sortie
    generer_bon_sortie(
        num_bs="BS-2025-001",
        date_bs="18/09/2025",
        client_nom="Société Client SARL",
        client_mf="1234567A/M/000",
        client_adresse="Avenue Habib Bourguiba, Tunis",
        description="Déchets industriels",
        quantite="5 tonnes",
        chauffeur_nom="Ali Ben Salem",
        matricule_voiture="123 TU 4567",
        fichier="bon_sortie.pdf"
    )