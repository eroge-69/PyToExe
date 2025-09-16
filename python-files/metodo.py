def dhondt(voti_liste, seggi_totali):
    quotients = []
    for lista, voti in voti_liste.items():
        for i in range(1, seggi_totali + 1):
            quotients.append((voti / i, lista))
    quotients.sort(reverse=True, key=lambda x: x[0])
    seggi = {lista: 0 for lista in voti_liste}
    for i in range(seggi_totali):
        _, lista = quotients[i]
        seggi[lista] += 1
    return seggi

if __name__ == "__main__":
    num_liste = int(input("Quante liste vuoi inserire? "))
    voti_liste = {}

    for _ in range(num_liste):
        nome = input("Nome della lista: ")
        voti = int(input(f"Voti per {nome}: "))
        voti_liste[nome] = voti

    seggi_totali = int(input("Numero totale di seggi disponibili: "))

    risultati = dhondt(voti_liste, seggi_totali)

    print("\nRisultati previsione seggi:")
    for lista, seggi in risultati.items():
        print(f"{lista}: {seggi} seggi")