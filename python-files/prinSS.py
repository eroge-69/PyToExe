def faktorial():
    print('Helllo Benutzer!\nDas ist ein Programm dass die mathematische Funktion "Faktorial" widerspiegelt.')
    erg = 1
    try:
        x = int(input("Bitte gebe eine Natürliche Zahl an:"))

        if x > 100:
            print("Geht nicht mehr als 100!")
            x = 100
        for y in range(1, x+1):
            erg = erg * y
        print(f"Das Ergebnis von {x}! lautet: {erg}")
    except ValueError:
        print("\nBitte nur Zahlen\n")
        faktorial()
    input("Danke!")
    
faktorial()

