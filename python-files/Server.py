# Programma Semplice per Ordini in Python

MENU = {
    "Margherita": 6.50,
    "Diavola": 8.00,
    "Quattro Formaggi": 9.50,
    "Capricciosa": 8.50,
    "Focaccia": 3.00,
    "Acqua": 2.00,
    "Coca Cola": 3.50
}

def mostra_menu():
    """Stampa il menu con i prezzi."""
    print("\n--- MENU PIZZERIA ---")
    for nome, prezzo in MENU.items():
        print(f"{nome:20} €{prezzo:.2f}")
    print("---------------------\n")

def prendi_ordine():
    """Gestisce il processo di acquisizione dell'ordine."""
    ordine = {}
    
    while True:
        mostra_menu()
        
        scelta = input("Inserisci il nome della pietanza (o 'FINE' per terminare l'ordine): ").strip().title()
        
        if scelta == 'Fine':
            break
            
        if scelta in MENU:
            while True:
                try:
                    quantita = int(input(f"Quante {scelta} vuoi? "))
                    if quantita > 0:
                        break
                    else:
                        print("La quantità deve essere un numero positivo.")
                except ValueError:
                    print("Input non valido. Inserisci un numero.")
            
            # Aggiorna l'ordine
            if scelta in ordine:
                ordine[scelta] += quantita
            else:
                ordine[scelta] = quantita
            
            print(f"{quantita} x {scelta} aggiunti all'ordine.")
        else:
            print("Pietanza non trovata nel menu. Riprova.")

    return ordine

def stampa_scontrino(ordine):
    """Calcola e stampa il riepilogo dell'ordine."""
    if not ordine:
        print("\nOrdine vuoto. Nessun scontrino da stampare.")
        return

    totale_generale = 0
    print("\n========= SCONTRINO =========")
    
    for nome, quantita in ordine.items():
        prezzo_unitario = MENU[nome]
        costo_linea = prezzo_unitario * quantita
        totale_generale += costo_linea
        
        # Stampa l'articolo in formato scontrino
        print(f"{quantita} x {nome:20} €{prezzo_unitario:.2f} (Tot. €{costo_linea:.2f})")
        
    print("-----------------------------")
    print(f"TOTALE DA PAGARE:            €{totale_generale:.2f}")
    print("=============================")
    print("Grazie e buon appetito!")


# --- Esecuzione del Programma ---
if __name__ == "__main__":
    print("Sistema di gestione ordini Pizzeria V1.0")
    
    ordine_corrente = prendi_ordine()
    stampa_scontrino(ordine_corrente)
