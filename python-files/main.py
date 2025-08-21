Wohnmobil = float(input("Anzahl Wohnmobile: "))
Erwachsene = float(input("Anzahl Erwachsene: "))
Kinder_ueber15 = float(input("Anzahl Kinder über 15: "))
Kinder_unter15 = float(input("Anzahl Kinder unter 15: "))

Gesamtpreis = (Wohnmobil * 18.50) + (Erwachsene * 3.0) + (Kinder_ueber15 * 3.0)
print("Insgesamt sind:", Gesamtpreis, " EUR zu kassieren")

