import pandas as pd

# 1. Anagrafica progetto
anagrafica_data = {
    "Campo": [
        "Titolo progetto", "Tipo progetto (Film / Serie / Doc)", "Anno produzione", "Genere",
        "Paese/i di produzione", "Durata", "Regista", "Produttore"
    ],
    "Valore": ["", "", "", "", "", "", "", ""]
}
df_anagrafica = pd.DataFrame(anagrafica_data)

# 2. Ricavi
ricavi_data = {
    "Categoria": [
        "Diritti TV", "Piattaforme digitali", "Distribuzione cinema", "Home Video",
        "Diritti internazionali", "Festival / Premi", "Merchandising", "Product Placement",
        "Diritti derivati", "Contributi pubblici", "Contributi europei", "Tax Credit",
        "Coproduzioni estere", "Crowdfunding", "Prevendite"
    ],
    "Dettaglio": [
        "RAI, Mediaset, Sky", "Netflix, Prime Video, Apple TV", "Incassi da sala Italia/Estero", 
        "DVD, Blu-ray, Digital download", "Sales internazionali", "Premi festival, proiezioni",
        "Magliette, poster", "Sponsor e marchi inclusi", "Remake, sequel, ecc.",
        "MIC, fondi regionali", "Creative Europe MEDIA", "Tax credit Italia/Estero",
        "Fondi di coproduzione stranieri", "Donazioni online", "Prevendite diritti prima della produzione"
    ],
    "Importo previsto (€)": ["" for _ in range(15)],
    "Importo incassato (€)": ["" for _ in range(15)],
    "Note": ["" for _ in range(15)]
}
df_ricavi = pd.DataFrame(ricavi_data)

# 3. Costi
costi_data = {
    "Categoria": [
        "Sviluppo", "Pre-produzione", "Produzione - cast/crew", "Produzione - logistica",
        "Produzione - materiali", "Post-produzione", "Distribuzione e promozione",
        "Festival e eventi", "Costi legali", "Costi amministrativi", "Assicurazioni", "Uffici e software"
    ],
    "Dettaglio": [
        "Sceneggiatura, diritti, consulenze", "Casting, location, planning",
        "Cast artistico, troupe tecnica", "Viaggi, alloggi, trasporti", "Costumi, scenografie, attrezzature",
        "Montaggio, VFX, color grading, audio", "Trailer, poster, ufficio stampa",
        "Fee festival, viaggi, hospitality", "Contratti, delivery, consulenze",
        "Contabilità, tasse, consulenze", "Set, trasporti, RC, altri", "Noleggi, licenze, CRM"
    ],
    "Importo previsto (€)": ["" for _ in range(12)],
    "Importo sostenuto (€)": ["" for _ in range(12)],
    "Note": ["" for _ in range(12)]
}
df_costi = pd.DataFrame(costi_data)

# 4. Dashboard
dashboard_data = {
    "Voce": [
        "Totale ricavi previsti", "Totale ricavi incassati", "Totale costi previsti",
        "Totale costi sostenuti", "Margine previsto", "Margine reale"
    ],
    "Valore (€)": [
        "=SOMMA(Ricavi!C2:C100)", "=SOMMA(Ricavi!D2:D100)",
        "=SOMMA(Costi!C2:C100)", "=SOMMA(Costi!D2:D100)",
        "=B1-B3", "=B2-B4"
    ]
}
df_dashboard = pd.DataFrame(dashboard_data)

# Esporta il file
with pd.ExcelWriter("Progetto_Audiovisivo_Completo.xlsx", engine="xlsxwriter") as writer:
    df_anagrafica.to_excel(writer, sheet_name="Anagrafica", index=False)
    df_ricavi.to_excel(writer, sheet_name="Ricavi", index=False)
    df_costi.to_excel(writer, sheet_name="Costi", index=False)
    df_dashboard.to_excel(writer, sheet_name="Dashboard", index=False)

print("✅ File Excel creato: Progetto_Audiovisivo_Completo.xlsx")

