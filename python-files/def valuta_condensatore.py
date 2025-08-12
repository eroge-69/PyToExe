def valuta_condensatore(cs_mis, cs_nom, esr_mis, esr_nom, delta_perc, d_val):
    risultati = {}

    # Capacità Cs
    if cs_nom * 0.8 <= cs_mis <= cs_nom * 1.2:
        risultati['Capacità (Cs)'] = 'OK'
    else:
        risultati['Capacità (Cs)'] = 'KO'

    # ESR Rs
    if esr_mis <= 2 * esr_nom:
        risultati['ESR (Rs)'] = 'OK'
    else:
        risultati['ESR (Rs)'] = 'KO'

    # Delta %
    if abs(delta_perc) <= 20:
        risultati['Δ% (Delta Capacità)'] = 'OK'
    else:
        risultati['Δ% (Delta Capacità)'] = 'KO'

    # Fattore dissipazione D
    if d_val < 0.10:
        risultati['D (Fattore dissipazione)'] = 'OK'
    else:
        risultati['D (Fattore dissipazione)'] = 'KO'

    return risultati


def main():
    print("Valutazione Condensatori - Inserisci i valori richiesti")

    cs_nom = float(input("Capacità nominale (uF): "))
    cs_mis = float(input("Capacità misurata (uF): "))
    esr_nom = float(input("ESR nominale (Ohm): "))
    esr_mis = float(input("ESR misurata (Ohm): "))
    delta_perc = float(input("Delta % capacità: "))
    d_val = float(input("Fattore dissipazione (D): "))

    risultati = valuta_condensatore(cs_mis, cs_nom, esr_mis, esr_nom, delta_perc, d_val)

    print("\n--- Risultati valutazione ---")
    for param, esito in risultati.items():
        print(f"{param}: {esito}")

    if all(esito == 'OK' for esito in risultati.values()):
        print("\nCondensatore in BUONE condizioni ✅")
    else:
        print("\nCondensatore DA SOSTITUIRE ❌")


if __name__ == "__main__":
    main()
