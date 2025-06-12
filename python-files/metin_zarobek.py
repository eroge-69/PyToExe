def oblicz_zarobek(ilosc_itemow, wartosc_itemu):
    return ilosc_itemow * wartosc_itemu

ilosc_itemow = int(input("Podaj ilość itemów: "))
wartosc_itemu = int(input("Podaj wartość jednego itemu (w yang): "))

zarobek = oblicz_zarobek(ilosc_itemow, wartosc_itemu)
print(f"Twój zarobek to: {zarobek} yang")
input("Naciśnij Enter, aby zakończyć...")
