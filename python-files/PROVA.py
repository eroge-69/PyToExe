def gioco_indovinello():
    print("FERMI TUTTI! Per scoprire un indizio importante, dovete risolvere questo indovinello.")
    print("\nIndovinello:")
    print("Corro veloce, la luce non rifletto, mangio pollo e sono bravo a basket, chi sono? (una sola parola)")
    
    risposta_corretta = "negro"
    
    tentativi = 3
    while tentativi > 0:
        risposta = input("\nRisposta: ").strip().lower()
        if risposta == risposta_corretta:
            print("\nCORRETTO! Guardate nella tasca posteriore dei miei pantaloni.")
            return
        else:
            tentativi -= 1
            print(f"Sbagliato! Ti rimangono {tentativi} tentativi.")
    
    print("\nHai esaurito i tentativi. Ritenta più tardi!")

gioco_indovinello()