def analizza_codice_brutale(codice):
    # Rimuove RS iniziale e EOT finale, se presenti
    codice = codice.strip()
    if codice.startswith("[RS]"):
        codice = codice[len("[RS]"):]
    if codice.endswith("[EOT]"):
        codice = codice[:-len("[EOT]")]

    # Divide il contenuto in sezioni tramite [GS]
    sezioni = codice.split("[GS]")

    # Analisi personalizzata
    info = {}
    for sezione in sezioni:
        if sezione.startswith("P6"):
            info["Numero prodotto"] = sezione[1:]  # Rimuove la 'P'
        elif sezione.startswith("V9"):
            info["Versione firmware"] = sezione
        elif sezione.startswith("2P"):
            info["HW Version"] = sezione[2:]
        elif sezione.startswith("16S"):
            info["SW Version"] = sezione[3:]
        elif sezione.startswith("1S"):
            info["Parameter Version"] = sezione[2:]
        elif sezione.startswith("S6"):
            info["Seriale completo"] = sezione[1:]  # Rimuove la 'S'
        else:
            pass  # Ignora la sezione "06" o altro se non ti serve

    print("\n🔍 Informazioni estratte:")
    for k, v in info.items():
        print(f"- {k}: {v}")

# Esempio di utilizzo
codice_input = "[RS]06[GS]P61950820[GS]V9117327[GS]2P2.2[GS]16S1.3[GS]1S1.0[GS]S61950820563940252751728210[RS][EOT]"
analizza_codice_brutale(codice_input)