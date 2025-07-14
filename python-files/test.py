import math

def larghezza_massima_porta(diametro_pistone, percentuale_limite):
    return round(diametro_pistone * percentuale_limite / 100, 2)

def altezza_porta_scarico(corsa, uso):
    if uso == "racing":
        return round(corsa * 0.45, 2)  # scarico alto, più aggressivo
    else:
        return round(corsa * 0.38, 2)  # più affidabile, meno stress pistone

def angolo_apertura_scarico(altezza_porta, corsa, biella):
    r = biella / 2
    try:
        alfa = math.acos(1 - (2 * altezza_porta / corsa))  # semplificato
        return round(math.degrees(alfa), 1)
    except:
        return "Non calcolabile (quota eccessiva)"

def main():
    print("=== CALCOLO PORTA DI SCARICO AM6 ===")

    try:
        pistone = float(input("Diametro pistone (mm): "))
        corsa = float(input("Corsa (mm): "))
        biella = float(input("Lunghezza biella (mm): "))
        segmenti = int(input("Numero segmenti pistone (1 o 2): "))
        uso = input("Uso [racing/touring]: ").strip().lower()

        if segmenti == 1:
            percentuale = 72
        else:
            percentuale = 68

        larghezza = larghezza_massima_porta(pistone, percentuale)
        altezza = altezza_porta_scarico(corsa, uso)
        angolo = angolo_apertura_scarico(altezza, corsa, biella)

        print("\n--- RISULTATI ---")
        print(f"Larghezza massima porta scarico: {larghezza} mm")
        print(f"Altezza teorica massima scarico: {altezza} mm")
        print(f"Angolo apertura scarico: {angolo}°")
        
        if larghezza > pistone * 0.72:
            print("⚠️ Attenzione: rischio di scoprire i segmenti!")
        if uso == "racing" and altezza > corsa * 0.45:
            print("⚠️ Scarico troppo alto: rischio perdita coppia in basso.")
    
    except:
        print("Errore: controlla i dati inseriti.")

if __name__ == "__main__":
    main()
